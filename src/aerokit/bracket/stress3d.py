"""3-D stress-constrained topology optimisation on voxels: minimum mass subject to clustered P-norm von Mises
constraints (Holmberg, Torstenfelt & Klarbring 2013, problem P1), optionally with a smoothed Heaviside projection and
β continuation so the result ends close to 0/1.

Formulation (as in the validated 2-D :mod:`aerokit.optimization.stress_topo`, now on H8 / H8IM voxels):

* design x → density filter (cone, radius ``rmin`` voxels) → x̃ → projection x̄ = H(x̃; β, η) (if ``projection``)
  → stiffness (Emin + x̄^p (1 − Emin)) · frac, p = 3;
* relaxed stress s_a = x̄_a^q σ_vm,a / σ̄, q = 1/2, σ at the element centroid (E-independent, E = 1 in the solve);
* per load case, the evaluation elements are sorted by s and split into ``n_clusters`` consecutive blocks ("stress
  level" clusters, re-clustered every iteration); constraint per cluster σ^PN = ((1/N) Σ s^P)^(1/P) ≤ 1, P = 8;
* objective: mean x̄ over the design elements (mass fraction); MMA (repository ``mma_multi``), one constraint per
  cluster and load case; adjoint: one extra solve with all constraint right-hand sides.

β continuation [Y, Guest/Sigmund practice]: β = ``beta0`` until iteration ``beta_start``, then doubled every
``beta_every`` iterations up to ``beta_max``; the MMA asymptotes are reset at every change.

Validation (``scripts/bracket_validate.py``, doc 22 §4c): Holmberg's L-beam extruded one voxel thick against the
published mass and compliance, and the grey level of a 3-D cantilever with and without projection.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import numpy as np

from aerokit.bracket.topo3d import _VM, _Solver, density_filter
from aerokit.bracket.voxfem import VoxelMesh, ke_unit
from aerokit.optimization.projection import project, project_dx
from aerokit.references import cite

__all__ = ["grey_measure", "clustered_pnorm", "optimize_stress", "optimize_stress_verified", "l_beam",
           "threshold_check"]


def grey_measure(x: np.ndarray) -> float:
    """M_nd = mean 4 x (1 − x) × 100 % (0 % black and white, 100 % all 0.5; Sigmund 2007 via Lazarov 2016)."""
    x = np.clip(np.asarray(x, float), 0.0, 1.0)
    return float(np.mean(4.0 * x * (1.0 - x)) * 100.0) if x.size else 0.0


def _stress(mesh: VoxelMesh, U: np.ndarray, S0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Centroid stress (ne, 6) per unit E and its von Mises value for one displacement vector."""
    sig = U[mesh.edof] @ S0.T / mesh.h
    vm = np.sqrt(np.maximum(np.einsum("ei,ij,ej->e", sig, _VM, sig), 1e-30))
    return sig, vm


def clustered_pnorm(mesh: VoxelMesh, xp: np.ndarray, U: np.ndarray, sigma_bar: float, evaluate: np.ndarray,
                    n_clusters: int = 10, P: float = 8.0, q: float = 0.5, element: str = "H8IM", nu: float = 0.3
                    ) -> dict[str, Any]:
    """Cluster P-norms of every load case (columns of ``U``, solved with E = 1) and their partial derivatives.

    Returns ``g`` (m,) the P-norm values, ``d_expl`` (m, ne) ∂σ^PN/∂x̄ at fixed u, ``rhs`` (ndof, m) ∂σ^PN/∂u for
    the adjoint, ``max_ratio`` (nc,) the largest relaxed stress ratio of each case and ``s`` (nc, ne).
    """
    from aerokit.bracket.voxfem import _stress_ops
    S0 = _stress_ops(nu, element).S0
    U = U[:, None] if U.ndim == 1 else U
    nc, ne = U.shape[1], mesh.ne
    ev = np.flatnonzero(evaluate)
    xq = np.maximum(xp, 1e-9) ** q
    g, d_expl, cols, mx, s_all, cmax = [], [], [], [], [], []
    for c in range(nc):
        sig, vm = _stress(mesh, U[:, c], S0)
        s = xq * vm / sigma_bar
        s_all.append(s)
        mx.append(float(s[ev].max()))
        order = ev[np.argsort(-s[ev])]
        for blk in np.array_split(order, max(1, min(n_clusters, len(order)))):
            sb = s[blk]
            pn = float(np.mean(sb ** P) ** (1.0 / P))
            w = np.zeros(ne)
            w[blk] = pn ** (1.0 - P) * sb ** (P - 1.0) / len(blk)                # ∂σ^PN/∂s_a
            g.append(pn)
            cmax.append(float(sb.max()))
            d_expl.append(w * q * np.maximum(xp, 1e-9) ** (q - 1.0) * vm / sigma_bar)
            a = w * xq / sigma_bar / vm                                          # ∂σ^PN/∂vm_a
            dsu = (a[:, None] * (sig @ _VM)) @ S0 / mesh.h                       # ∂/∂u_e (ne, 24)
            col = np.zeros(mesh.ndof)
            np.add.at(col, mesh.edof.ravel(), dsu.ravel())
            cols.append(col)
    return {"g": np.array(g), "d_expl": np.array(d_expl), "rhs": np.column_stack(cols), "max_ratio": np.array(mx),
            "s": np.array(s_all), "cluster_max": np.array(cmax)}


@cite("holmberg_2013", "svanberg_1987", "ferrari_sigmund_2020",
      note="P1 with stress-level clustered P-norms (p = 8, q = 1/2) on voxels; tanh projection with β continuation")
def optimize_stress(mesh: VoxelMesh, F: np.ndarray, fixed: np.ndarray, sigma_bar: float, *,
                    evaluate: np.ndarray | None = None, keep: np.ndarray | None = None, rmin: float = 1.5,
                    penal: float = 3.0, q: float = 0.5, P: float = 8.0, n_clusters: int = 10,
                    emin_ratio: float = 1e-9, nu: float = 0.3, x0: float | np.ndarray = 0.5, move: float = 0.1,
                    max_iter: int = 300, tol: float = 0.002, element: str = "H8IM", projection: bool = False,
                    eta: float = 0.5, beta0: float = 1.0, beta_max: float = 16.0, beta_start: int = 100,
                    beta_every: int = 40, adaptive: bool = False, adapt_damping: float = 0.5,
                    callback: Callable[[int, float, float, float], None] | None = None,
                    solver_kw: dict[str, Any] | None = None) -> dict[str, Any]:
    """Minimum mass fraction of the design elements s.t. every cluster P-norm of the relaxed von Mises ratio ≤ 1.

    ``F`` (ndof,) or (ndof, n_cases) in N; ``keep`` elements are solid and not design variables; ``evaluate``
    defaults to the design elements. Returns the physical density ``xphys``, ``mass_fraction``, the true
    ``max_stress_ratio`` per case (relaxed, design), ``grey_percent`` of the design elements, the histories, the
    compliance per unit E (``compliance_unitE``: divide by E) and the final β.
    """
    t0 = time.perf_counter()
    F = np.asarray(F, float)
    F = F[:, None] if F.ndim == 1 else F
    ne = mesh.ne
    keep = np.zeros(ne, bool) if keep is None else np.asarray(keep, bool)
    free = ~keep
    ev = free.copy() if evaluate is None else np.asarray(evaluate, bool)
    frac = np.asarray(mesh.frac, float)
    KE, _ = ke_unit(nu, element)
    H, Hs = density_filter(mesh, rmin)
    Ht = H.T.tocsr()
    solver = _Solver(mesh, fixed, **(solver_kw or {}))
    x = np.where(keep, 1.0, np.broadcast_to(np.asarray(x0, float), (ne,))).astype(float)
    xa = x[free].copy()
    xold1 = xold2 = xa.copy()
    low = upp = None
    lo_, hi_ = np.zeros_like(xa), np.ones_like(xa)
    beta = beta0 if projection else 1.0
    kk = 0                                                  # MMA iteration counter since the last β change
    hist: dict[str, list[float]] = {"mass": [], "max_pn": [], "beta": []}
    change, k = 1.0, 0
    U = np.zeros_like(F)

    ctx = _Ctx(mesh, F, KE, H, Hs, Ht, keep, free, ev, frac, solver, sigma_bar, penal, q, P, n_clusters,
               emin_ratio, element, nu, projection, eta)
    cp: dict[str, Any] = {}
    from aerokit.optimization.stress_topo import mma_multi
    x_safe: np.ndarray | None = None                        # last design with max P-norm ≤ 1.05 (trust region)
    shrink = 1.0
    cnorm: np.ndarray | None = None                         # adaptive normalisation factors (one per cluster)
    hist["fallbacks"] = []
    while k < max_iter:
        k += 1
        kk += 1
        f0, g, df0, dg, U, cp = _response(ctx, x, beta)
        if adaptive:                                        # Le et al. 2010: scale each cluster to its maximum
            ratio = cp["cluster_max"] / np.maximum(g, 1e-12)
            cnorm = ratio if cnorm is None else adapt_damping * ratio + (1 - adapt_damping) * cnorm
            g, dg = cnorm * g, cnorm[:, None] * dg
        if g.max() <= 1.05:
            x_safe = x.copy()
        elif g.max() > 2.0 and x_safe is not None:          # gross violation after a step: go back, smaller moves
            x, shrink = x_safe.copy(), shrink * 0.5
            xa = x[free].copy()
            xold1 = xold2 = xa.copy()
            low = upp = None
            kk = 1
            hist["fallbacks"].append(float(k))
            f0, g, df0, dg, U, cp = _response(ctx, x, beta)
            if adaptive and cnorm is not None:
                g, dg = cnorm * g, cnorm[:, None] * dg
        hist["mass"].append(f0)
        hist["max_pn"].append(float(g.max()))
        hist["beta"].append(beta)
        if callback:
            callback(k, f0, float(g.max()), beta)
        low, upp = _asymptotes(kk, xa, xold1, xold2, low, upp, lo_, hi_)
        mv = move * min(1.0, 2.0 / beta) * shrink           # high β: the tanh slope makes MMA's model local
        xa_new, _ = mma_multi(xa, lo_, hi_, low, upp, df0, g - 1.0, dg, move=mv)
        xold2, xold1 = xold1, xa.copy()
        change = float(np.max(np.abs(xa_new - xa)))
        xa = xa_new
        x[free] = xa
        if projection and beta < beta_max and k >= beta_start and (k - beta_start) % beta_every == 0:
            beta, kk, low, upp = min(2.0 * beta, beta_max), 0, None, None
            xold1 = xold2 = xa.copy()
            continue
        if change < tol and g.max() <= 1.0 + 1e-3 and (not projection or beta >= beta_max):
            break
    _, g, _, _, U, cp = _response(ctx, x, beta)
    if g.max() > 1.05 and x_safe is not None:               # never hand back a broken last iterate
        x = x_safe
        _, g, _, _, U, cp = _response(ctx, x, beta)
        hist["fallbacks"].append(float(k + 1))
    xp = cp["xp"]
    return {"xphys": xp, "x": x.copy(), "mass_fraction": float(xp[free].mean()),
            "max_stress_ratio": cp["max_ratio"].tolist(), "max_pnorm": float(cp["g"].max()),
            "grey_percent": grey_measure(xp[free]), "compliance_unitE": [float(F[:, c] @ U[:, c])
                                                                        for c in range(F.shape[1])],
            "beta": beta, "iterations": k, "converged": change < tol, "seconds": time.perf_counter() - t0,
            "history": hist, "U": U,
            "settings": {"sigma_bar": sigma_bar, "P": P, "q": q, "rmin": rmin, "penal": penal, "move": move,
                         "n_clusters": n_clusters, "projection": projection, "eta": eta, "beta_max": beta_max,
                         "adaptive": adaptive}}


class _Ctx:
    """Fixed data of one optimisation (mesh, loads, filter, solver, settings)."""

    def __init__(self, *a: Any) -> None:
        (self.mesh, self.F, self.KE, self.H, self.Hs, self.Ht, self.keep, self.free, self.ev, self.frac, self.solver,
         self.sigma_bar, self.penal, self.q, self.P, self.n_clusters, self.emin, self.element, self.nu,
         self.projection, self.eta) = a


def _response(c: _Ctx, x: np.ndarray, beta: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
                                                            dict[str, Any]]:
    """Mass fraction, cluster P-norms and their gradients w.r.t. the free design variables at design ``x``."""
    m = c.mesh
    xt = (c.H @ x) / c.Hs
    if c.projection:
        xp = np.where(c.keep, 1.0, project(xt, beta, c.eta))
        dpdt = np.where(c.keep, 0.0, project_dx(xt, beta, c.eta))
    else:
        xp, dpdt = np.where(c.keep, 1.0, xt), np.where(c.keep, 0.0, 1.0)
    Ee = (c.emin + xp ** c.penal * (1.0 - c.emin)) * c.frac
    U = c.solver(None, c.F, None, c.KE, Ee * m.h)
    cp = clustered_pnorm(m, xp, U, c.sigma_bar, c.ev, c.n_clusters, c.P, c.q, c.element, c.nu)
    lam = c.solver(None, cp["rhs"], None, c.KE, Ee * m.h)
    dK = c.penal * xp ** (c.penal - 1.0) * (1.0 - c.emin) * c.frac * m.h
    nc = c.F.shape[1]
    per = len(cp["g"]) // nc
    dg = np.empty((len(cp["g"]), int(c.free.sum())))
    for i in range(len(cp["g"])):
        impl = dK * np.einsum("ea,ab,eb->e", lam[m.edof, i], c.KE, U[m.edof, i // per])
        dg[i] = (c.Ht @ ((cp["d_expl"][i] - impl) * dpdt / c.Hs))[c.free]
    nfree = int(c.free.sum())
    df0 = (c.Ht @ (np.where(c.free, 1.0 / nfree, 0.0) * dpdt / c.Hs))[c.free]
    cp["xp"] = xp
    return float(xp[c.free].mean()), cp["g"], df0, dg, U, cp


def _asymptotes(k: int, xa: np.ndarray, x1: np.ndarray, x2: np.ndarray, low: Any, upp: Any, lo_: np.ndarray,
                hi_: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    from aerokit.optimization.topology import mma_asymptote
    return mma_asymptote(k, xa, x1, x2, low, upp, lo_, hi_)


@cite("holmberg_2013", note="§9.1: L = 200 mm, arms 2L/5, 1500 N, 3x2 load elements fixed solid, σ̄ 350 MPa")
def l_beam(n: int = 100, L: float = 0.2, force: float = 1500.0, thickness: float = 1e-3
           ) -> tuple[VoxelMesh, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Holmberg's L-beam as a one-voxel-thick 3-D slab (h = L/n in all directions).

    The published beam is 1 mm thick; the slab is h thick, so the force is scaled by h / ``thickness`` to keep the
    plane stresses (compliance then scales by the same factor). Returns mesh, F, fixed DOFs, keep (3 × 2 elements
    under the load) and the evaluation mask (design elements), as :func:`optimize_stress` expects.
    """
    h = L / n
    a = int(round(0.4 * n))
    ii, jj = np.meshgrid(np.arange(n), np.arange(n), indexing="ij")
    solid = ~((ii + 0.5 > 0.4 * n) & (jj + 0.5 > 0.4 * n))
    mesh = VoxelMesh(solid[:, :, None], h)
    X = mesh.X
    top = np.flatnonzero(np.isclose(X[:, 1], n * h) & (X[:, 0] <= a * h + 1e-12))
    fixed = (3 * top[:, None] + np.arange(3)).ravel()
    tip = np.flatnonzero(np.isclose(X[:, 0], n * h) & np.isclose(X[:, 1], a * h))
    F = np.zeros(mesh.ndof)
    F[3 * tip + 1] = -force * (h / thickness) / len(tip)
    c = mesh.ijk
    keep = (c[:, 0] >= n - 3) & (c[:, 1] >= a - 2) & (c[:, 1] < a)
    return mesh, F, fixed, keep, ~keep


def threshold_check(mesh: VoxelMesh, xp: np.ndarray, F: np.ndarray, fixed: np.ndarray, sigma_bar: float,
                    evaluate: np.ndarray, level: float = 0.5, nu: float = 0.3, element: str = "H8IM",
                    emin_ratio: float = 1e-9) -> dict[str, Any]:
    """Re-analysis of the black-and-white design (x̄ > ``level`` solid, else void): true von Mises / σ̄ of the
    solid evaluation elements (no relaxation), the solid fraction and the compliance per unit E."""
    from aerokit.bracket.voxfem import _stress_ops
    F = np.asarray(F, float)
    F = F[:, None] if F.ndim == 1 else F
    solid = np.asarray(xp) > level
    KE, _ = ke_unit(nu, element)
    Ee = np.where(solid, 1.0, emin_ratio) * np.asarray(mesh.frac, float)
    U = _Solver(mesh, fixed)(None, F, None, KE, Ee * mesh.h)
    S0 = _stress_ops(nu, element).S0
    ev = np.asarray(evaluate, bool) & solid
    ratios = [float(_stress(mesh, U[:, c], S0)[1][ev].max() / sigma_bar) if ev.any() else 0.0
              for c in range(F.shape[1])]
    return {"max_true_ratio": ratios, "solid_fraction": float(solid.mean()),
            "compliance_unitE": [float(F[:, c] @ U[:, c]) for c in range(F.shape[1])]}


@cite("holmberg_2013", note="P-norm overshoot of the true maximum; verified by a black-and-white re-analysis")
def optimize_stress_verified(mesh: VoxelMesh, F: np.ndarray, fixed: np.ndarray, sigma_bar: float, *,
                             evaluate: np.ndarray | None = None, keep: np.ndarray | None = None, rounds: int = 3,
                             round_iters: int = 40, tol: float = 0.02, max_iter: int = 100,
                             **kw: Any) -> dict[str, Any]:
    """Projected stress-constrained optimisation followed by up to ``rounds`` verification rounds: the design is
    thresholded at 0.5 and re-analysed; if its true von Mises exceeds σ̄ by more than ``tol``, the working limit
    σ̄_eff is divided by the measured overshoot and the optimisation continues from the current design at the final
    β for ``round_iters`` iterations. Returns the last result plus ``rounds_log`` and ``verified``."""
    keep_ = np.zeros(mesh.ne, bool) if keep is None else np.asarray(keep, bool)
    ev = ~keep_ if evaluate is None else np.asarray(evaluate, bool)
    kw = {"projection": True, **kw}
    r = optimize_stress(mesh, F, fixed, sigma_bar, evaluate=ev, keep=keep_, max_iter=max_iter, **kw)
    log = []
    s_eff = sigma_bar
    for i in range(rounds + 1):
        chk = threshold_check(mesh, r["xphys"], F, fixed, sigma_bar, ev)
        ratio = max(chk["max_true_ratio"])
        log.append({"round": i, "sigma_eff_Pa": s_eff, "mass_fraction": r["mass_fraction"],
                    "grey_percent": r["grey_percent"], "threshold_true_ratio": ratio,
                    "solid_fraction": chk["solid_fraction"]})
        if ratio <= 1.0 + tol or i == rounds:
            break
        s_eff /= ratio
        bmax = kw.get("beta_max", 16.0)
        kw2 = {**kw, "beta0": bmax, "beta_start": 10**9, "x0": r["x"]}
        r = optimize_stress(mesh, F, fixed, s_eff, evaluate=ev, keep=keep_, max_iter=round_iters, **kw2)
    r["rounds_log"] = log
    r["verified"] = log[-1]["threshold_true_ratio"] <= 1.0 + tol
    r["sigma_eff_Pa"] = s_eff
    return r
