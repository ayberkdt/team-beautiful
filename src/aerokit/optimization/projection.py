"""Threshold (tanh) projection, the robust eroded/dilated formulation and the filter-radius → member-size rule.

Equations used, all read in the primary source on 2026-11-03 (prev_guess/01_Ansys/research/Optimizasyon kaynakları/
TO_kaynak_paketi.md §2–§3):

* projection (Ferrari & Sigmund 2020 Eq. 1; Qian & Sigmund 2013 Eq. 25; Lazarov et al. 2016 Eq. 23)::

      x̂ = (tanh(βη) + tanh(β(x̃ − η))) / (tanh(βη) + tanh(β(1 − η)))

  and its derivative ∂x̂/∂x̃ (Ferrari & Sigmund Eq. 9);
* volume-preserving threshold η* with V(x̂(η*)) = V(x̃), found by Newton from the previous η (Ferrari & Sigmund
  Eq. 17, "generally η* ∈ [0.4, 0.52]");
* robust design: eroded / blueprint / dilated thresholds 1 − η, 0.5, η with η ∈ [0, 0.5]; β starts at 1 and doubles
  every 50 iterations up to 128; volume on the dilated design (Qian & Sigmund p. 8); objective max{J_e, J_d}
  (Lazarov et al. Eq. 37, the blueprint dropped);
* minimum member width of the blueprint for a hat (cone) filter of radius R (Qian & Sigmund Eq. 29–30):
  b/R = 2√(η_e − ½) for η_e ∈ [0.5, 0.75], 2 − 2√(1 − η_e) for η_e ∈ [0.75, 1]. η_e = 0.75 gives b = R.

The derivative of η* with respect to the filtered field (implicit function of the volume equality) is this module's
derivation; the tests check it, and every other gradient here, against finite differences.
"""
from __future__ import annotations

import math
from functools import partial
from typing import Any

import numpy as np

from aerokit.optimization import topology as tp
from aerokit.references import cite

__all__ = ["project", "project_dx", "project_deta", "volume_preserving_eta", "min_size_ratio", "eta_for_size",
           "radius_for_member", "Projected", "topopt_projected"]


@cite("ferrari_sigmund_2020", "qian_sigmund_2013", note="Eq. (1) / Eq. (25)")
def project(xt: np.ndarray, beta: float, eta: float) -> np.ndarray:
    """Smoothed Heaviside projection of the filtered density ``xt`` with sharpness β and threshold η."""
    a, b = math.tanh(beta * eta), math.tanh(beta * (1.0 - eta))
    return (a + np.tanh(beta * (np.asarray(xt, float) - eta))) / (a + b)


@cite("ferrari_sigmund_2020", note="Eq. (9)")
def project_dx(xt: np.ndarray, beta: float, eta: float) -> np.ndarray:
    """∂x̂/∂x̃ (element by element)."""
    a, b = math.tanh(beta * eta), math.tanh(beta * (1.0 - eta))
    return beta * (1.0 - np.tanh(beta * (np.asarray(xt, float) - eta)) ** 2) / (a + b)


def project_deta(xt: np.ndarray, beta: float, eta: float) -> np.ndarray:
    """∂x̂/∂η (quotient rule on :func:`project`)."""
    a, b = math.tanh(beta * eta), math.tanh(beta * (1.0 - eta))
    t = np.tanh(beta * (np.asarray(xt, float) - eta))
    da, db = beta * (1 - a * a), -beta * (1 - b * b)
    return (da - beta * (1 - t * t)) / (a + b) - (a + t) * (da + db) / (a + b) ** 2


@cite("ferrari_sigmund_2020", note="Eq. (17), Newton from the previous threshold")
def volume_preserving_eta(xt: np.ndarray, beta: float, eta0: float = 0.5, tol: float = 1e-6,
                          max_iter: int = 50) -> float:
    """Threshold η* with mean(project(x̃, β, η*)) = mean(x̃)."""
    xt = np.asarray(xt, float)
    target, eta = float(xt.mean()), float(eta0)
    for _ in range(max_iter):
        r = float(project(xt, beta, eta).mean()) - target
        if abs(r) < tol:
            return eta
        eta = min(max(eta - r / float(project_deta(xt, beta, eta).mean()), 1e-6), 1 - 1e-6)
    lo, hi = 1e-6, 1 - 1e-6                                     # Newton stalled: bisection (V(x̂) falls with η)
    for _ in range(200):
        eta = 0.5 * (lo + hi)
        if float(project(xt, beta, eta).mean()) > target:
            lo = eta
        else:
            hi = eta
        if hi - lo < tol:
            break
    return eta


@cite("qian_sigmund_2013", note="Eq. (29), hat filter, same topology in all realisations")
def min_size_ratio(eta_e: float) -> float:
    """Blueprint minimum member width over filter radius, b/R, for the eroded threshold η_e ∈ [0.5, 1]."""
    if not 0.5 <= eta_e <= 1.0:
        raise ValueError("eroded threshold must lie in [0.5, 1]")
    return 2.0 * math.sqrt(eta_e - 0.5) if eta_e <= 0.75 else 2.0 - 2.0 * math.sqrt(1.0 - eta_e)


@cite("qian_sigmund_2013", note="Eq. (30)")
def eta_for_size(b_over_r: float) -> float:
    """Eroded threshold η_e that gives a blueprint minimum width b = (b/R)·R."""
    if b_over_r < 0:
        raise ValueError("b/R must be non-negative")
    if b_over_r <= 1.0:
        return 0.25 * b_over_r ** 2 + 0.5
    if b_over_r <= 2.0:
        return -0.25 * b_over_r ** 2 + b_over_r
    return 1.0


def radius_for_member(b_min: float, h: float, eta_e: float = 0.75) -> float:
    """Filter radius in element sizes that gives a blueprint minimum member width ``b_min`` (same unit as ``h``)."""
    return b_min / min_size_ratio(eta_e) / h


class Projected:
    """Design x → filtered x̃ = Hx/Hs → projected x̂ at threshold η (passive elements fixed), with exact chain rule.

    ``volume_preserving=True`` replaces η by η*(x̃) of :func:`volume_preserving_eta` and includes ∂η*/∂x̃ in the
    gradient.
    """

    def __init__(self, grid: tp._Grid, rmin: float, passive: Any = None) -> None:
        self.dens = tp.Density(grid, rmin, 2, passive)
        self.passive = self.dens.passive

    def filtered(self, x: np.ndarray) -> np.ndarray:
        return self.dens.intermediate(x)

    def physical(self, x: np.ndarray, beta: float, eta: float, volume_preserving: bool = False) -> np.ndarray:
        xt = self.filtered(x)
        if volume_preserving:
            eta = volume_preserving_eta(xt, beta, eta, tol=1e-12)
        return self.dens._apply_passive(project(xt, beta, eta))

    def chain(self, x: np.ndarray, d: np.ndarray, beta: float, eta: float,
              volume_preserving: bool = False) -> np.ndarray:
        """∂f/∂x from ∂f/∂x̂ (``eta`` is the threshold actually used, i.e. η* when ``volume_preserving``)."""
        d = np.array(d, float)
        d[self.passive > 0] = 0.0
        xt = self.filtered(x)
        dxt = d * project_dx(xt, beta, eta)
        if volume_preserving:
            # V(x̂(x̃, η*)) = V(x̃)  ⇒  ∂η*/∂x̃_e = (1 − ∂x̂_e/∂x̃_e) / Σ_k ∂x̂_k/∂η
            deta = project_deta(xt, beta, eta)
            dxt = dxt + float(np.sum(d * deta)) * (1.0 - project_dx(xt, beta, eta)) / float(np.sum(deta))
        return self.dens.Ht @ (dxt / self.dens.Hs)


@cite("qian_sigmund_2013", "lazarov_wang_sigmund_2016", "ferrari_sigmund_2020", "andreassen_2011",
      note="tanh projection with β continuation; robust max{J_e, J_d} with the volume on the dilated design")
def topopt_projected(problem: tp.Problem, volume: float, rmin: float, eta: float = 0.5,
                     robust: float | None = None, volume_preserving: bool = False, beta0: float = 1.0,
                     beta_max: float = 128.0, beta_step: int = 50, move: float = 0.1, tol: float = 0.01,
                     max_iter: int = 1000) -> dict[str, Any]:
    """Compliance minimisation with the tanh projection (OC update, top88 bisection).

    ``robust=η_d`` (e.g. 0.25) optimises max{J_e, J_d} over the eroded (threshold 1 − η_d) and dilated (η_d)
    designs with the volume constraint on the dilated design; the blueprint (threshold 0.5) is reported. β doubles
    every ``beta_step`` iterations or when the change drops to ``tol``, until ``beta_max``; the run stops when the
    change is below ``tol`` at ``beta_max``. The default OC move limit is 0.1: with top88's 0.2 the robust MBB
    120 x 40 (r_min 4) lost a member of the eroded design at the β 64 → 128 step and its compliance jumped from about
    320 to 32 000; with 0.1 the blueprint ended at 226.7 (run of 2026-11-03, docs/16 §6).

    Returns ``xfiz`` (blueprint array), ``compliance`` (history of the objective), ``compliance_final`` (blueprint),
    ``volume_blueprint``, ``gray`` (M_nd of the blueprint, %), ``iteration``, ``converged``, ``beta_final``, and
    for robust runs ``eroded``/``dilated`` arrays with their compliances.
    """
    grid, nel = problem.grid, problem.grid.nel
    if not 0 < volume <= 1:
        raise ValueError("0 < volume ≤ 1 is required")
    if robust is not None and not 0 < robust < 0.5:
        raise ValueError("robust threshold η_d must lie in (0, 0.5)")
    pj = Projected(grid, rmin, problem.passive)
    passive = problem.passive
    x = np.full(nel, float(volume))
    x[passive == 1], x[passive == 2] = 0.0, 1.0
    beta = float(beta0)
    eta_used = float(eta)
    thresholds = (1.0 - robust, robust) if robust is not None else (eta,)
    vol_eta = robust if robust is not None else eta
    hist: list[float] = []
    loop = loopbeta = 0
    change = 1.0
    while loop < max_iter:
        loop += 1
        loopbeta += 1
        worst, dc = -math.inf, np.zeros(nel)
        for th in thresholds:
            if volume_preserving and robust is None:
                xt = pj.filtered(x)
                eta_used = volume_preserving_eta(xt, beta, eta_used, tol=1e-12)
                th = eta_used
            xp = pj.dens._apply_passive(project(pj.filtered(x), beta, th))
            c, dcf, _ = problem.analysis(xp)
            if c > worst:
                worst, dc = c, pj.chain(x, dcf, beta, th, volume_preserving and robust is None)
        hist.append(worst)
        vp = volume_preserving and robust is None
        th_v = eta_used if vp else vol_eta
        dv = pj.chain(x, np.ones(nel), beta, th_v, vp)
        phys = partial(pj.physical, beta=beta, eta=th_v, volume_preserving=vp)
        xnew, _, _ = tp.update_oc(x, dc, np.where(dv > 1e-12, dv, 1e-12), volume, move, phys, nel, passive)
        change = float(np.max(np.abs(xnew - x)))
        x = xnew
        if beta < beta_max and (loopbeta >= beta_step or change <= tol):
            beta, loopbeta, change = min(2 * beta, beta_max), 0, 1.0
        elif beta >= beta_max and change <= tol:
            break
    blue_eta = eta_used if (volume_preserving and robust is None) else (0.5 if robust is not None else eta)
    xb = pj.physical(x, beta, blue_eta)
    cb, _, U = problem.analysis(xb)
    out: dict[str, Any] = {"x": grid.to_array(x), "xfiz": grid.to_array(xb), "compliance": np.array(hist),
                           "compliance_final": cb, "volume_blueprint": float(xb.mean()),
                           "gray": tp.gray_measure(xb), "iteration": loop, "converged": change <= tol,
                           "beta_final": beta, "eta_final": blue_eta, "U": U}
    if robust is not None:
        for name, th in (("eroded", 1.0 - robust), ("dilated", robust)):
            xr = pj.physical(x, beta, th)
            out[name] = grid.to_array(xr)
            out[f"compliance_{name}"] = problem.analysis(xr)[0]
            out[f"volume_{name}"] = float(xr.mean())
    return out
