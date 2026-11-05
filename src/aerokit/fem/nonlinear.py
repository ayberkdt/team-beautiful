"""Geometrically non-linear statics of truss structures (total Lagrangian).

Kinematics (one bar, reference length ``L₀``, reference axis vector ``d₀ = X_j − X_i``)
    Current axis vector ``d = d₀ + u_j − u_i``; Green-Lagrange strain
    ``E = (dᵀd − L₀²) / (2L₀²)``, uniform along a straight bar. With the St. Venant-Kirchhoff law
    ``S = E_mod · E`` and constant reference area ``A₀`` this is *exact* — no linearisation in the
    displacements [crisfield_1991]_.

Internal force and consistent tangent
    The strain energy ``U = ½ EA L₀ E²`` gives, with ``∂E/∂u_j = d/L₀² = −∂E/∂u_i``::

        f_j = −f_i = (EA E / L₀) d
        K_t = (EA/L₀³) [[ddᵀ, −ddᵀ], [−ddᵀ, ddᵀ]]        (material, incl. initial-displacement part)
            + (EA E/L₀) [[I, −I], [−I, I]]               (geometric / initial stress)

    The true (Cauchy) axial force is ``N = EA E ℓ/L₀`` with ``ℓ = |d|``.

Other elements
    :class:`~aerokit.fem.elements.discrete.Spring` (and the zero-stiffness
    :class:`~aerokit.fem.elements.discrete.PointMass`/:class:`~aerokit.fem.elements.discrete.Dashpot`)
    contribute their constant linear stiffness ``k u``. Any other element type raises
    :class:`ValueError`.

Solvers
    :func:`newton_raphson` (load control, full Newton) and :func:`arc_length` (Crisfield's cylindrical
    arc length [crisfield_1981]_) for paths with limit points, snap-through and snap-back. The load is
    ``λ F`` with the reference load ``F`` (default :attr:`Model.F`); constraints are applied through
    :meth:`Model.reduction` and must be homogeneous. Non-convergence raises
    :class:`ConvergenceError`, which carries the path up to the last converged step.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp

from aerokit.fem import solvers
from aerokit.fem.elements.discrete import Dashpot, PointMass, Spring
from aerokit.fem.elements.line import Bar
from aerokit.fem.model import Model
from aerokit.fem.results import NonlinearResult
from aerokit.references import cite

__all__ = ["ConvergenceError", "internal_force", "tangent_stiffness", "strain_energy", "axial_forces",
           "newton_raphson", "arc_length"]


class ConvergenceError(ValueError):
    """A non-linear step did not converge.

    Attributes
    ----------
    result : NonlinearResult
        Path up to and including the last converged step (``converged=False``).
    step : int
        Index of the step that failed (1-based; step 0 is the unloaded state).
    load_factor : float
        Load factor of the last converged state.
    """

    def __init__(self, message: str, result: NonlinearResult, step: int, load_factor: float) -> None:
        super().__init__(message)
        self.result = result
        self.step = step
        self.load_factor = load_factor


# ---------------------------------------------------------------------------------------------- kinematics
@dataclass(frozen=True)
class _Truss:
    n_dof: int
    nd: int
    idx: np.ndarray        # (nb, 2 nd) global DOFs of the bars
    d0: np.ndarray         # (nb, nd) reference axis vectors
    L0: np.ndarray         # (nb,)
    EA: np.ndarray         # (nb,)
    K_lin: sp.csr_matrix   # constant stiffness of the linear elements


def _truss(model: Model) -> _Truss:
    nd = model.ndof
    bars: list[Bar] = []
    lin: list[tuple[np.ndarray, np.ndarray]] = []
    for e in model.elements:
        if isinstance(e, Bar):
            bars.append(e)
        elif isinstance(e, Spring | PointMass | Dashpot):
            lin.append((model.equivalent_dof(e), np.asarray(e.k(model.X), dtype=float)))
        else:
            raise ValueError(f"{type(e).__name__} has no geometrically non-linear formulation "
                             "(supported: Bar, Spring, PointMass, Dashpot)")
    if bars and model.X.shape[1] != nd:
        raise ValueError("non-linear truss analysis needs ndof equal to the number of coordinates (2 or 3)")
    if bars:
        conn = np.array([b.nodes for b in bars], dtype=int)
        idx = np.concatenate([conn[:, :1] * nd + np.arange(nd), conn[:, 1:] * nd + np.arange(nd)], axis=1)
        d0 = model.X[conn[:, 1]] - model.X[conn[:, 0]]
        L0 = np.linalg.norm(d0, axis=1)
        if np.any(L0 <= 0):
            raise ValueError("zero-length bar")
        EA = np.array([float(b.E) * float(b.A) for b in bars])
    else:
        idx, d0, L0, EA = np.zeros((0, 2 * nd), dtype=int), np.zeros((0, nd)), np.zeros(0), np.zeros(0)
    n = model.n_dof
    if lin:
        rows = np.concatenate([np.repeat(i, i.size) for i, _ in lin])
        cols = np.concatenate([np.tile(i, i.size) for i, _ in lin])
        vals = np.concatenate([k.ravel() for _, k in lin])
        K_lin = sp.coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    else:
        K_lin = sp.csr_matrix((n, n))
    return _Truss(n, nd, idx, d0, L0, EA, K_lin)


def _state(tr: _Truss, u: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Current axis vectors ``d`` and Green-Lagrange strains ``E`` of all bars."""
    ue = u[tr.idx]
    d = tr.d0 + ue[:, tr.nd:] - ue[:, :tr.nd]
    E = (np.einsum("ij,ij->i", d, d) - tr.L0 ** 2) / (2 * tr.L0 ** 2)
    return d, E


def _f_int(tr: _Truss, u: np.ndarray) -> np.ndarray:
    d, E = _state(tr, u)
    fe = (tr.EA * E / tr.L0)[:, None] * d
    f = np.asarray(tr.K_lin @ u, dtype=float).copy()
    np.add.at(f, tr.idx[:, tr.nd:], fe)
    np.add.at(f, tr.idx[:, :tr.nd], -fe)
    return f


def _k_t(tr: _Truss, u: np.ndarray) -> sp.csr_matrix:
    d, E = _state(tr, u)
    nb, nd = d.shape
    if nb == 0:
        return tr.K_lin.copy()
    kd = (tr.EA / tr.L0 ** 3)[:, None, None] * d[:, :, None] * d[:, None, :] \
        + (tr.EA * E / tr.L0)[:, None, None] * np.eye(nd)[None]
    Ke = np.empty((nb, 2 * nd, 2 * nd))
    Ke[:, :nd, :nd] = kd
    Ke[:, nd:, nd:] = kd
    Ke[:, :nd, nd:] = -kd
    Ke[:, nd:, :nd] = -kd
    m = 2 * nd
    rows = np.repeat(tr.idx, m, axis=1).ravel()
    cols = np.tile(tr.idx, (1, m)).ravel()
    K = sp.coo_matrix((Ke.ravel(), (rows, cols)), shape=(tr.n_dof, tr.n_dof)).tocsr()
    return sp.csr_matrix(K + tr.K_lin)


def _vector(model: Model, u: np.ndarray, name: str = "u") -> np.ndarray:
    x = np.asarray(u, dtype=float).ravel()
    if x.shape != (model.n_dof,):
        raise ValueError(f"{name} must have length {model.n_dof}")
    return x


@cite("crisfield_1991", note="total-Lagrangian truss with Green-Lagrange strain")
def internal_force(model: Model, u: np.ndarray) -> np.ndarray:
    """Internal force vector ``f_int(u)`` (full DOF vector) of the non-linear truss model."""
    return _f_int(_truss(model), _vector(model, u))


@cite("crisfield_1991", note="consistent tangent: material + geometric stiffness")
def tangent_stiffness(model: Model, u: np.ndarray) -> sp.csr_matrix:
    """Consistent tangent stiffness ``K_t(u) = ∂f_int/∂u`` (full, CSR)."""
    return _k_t(_truss(model), _vector(model, u))


@cite("crisfield_1991", note="St. Venant-Kirchhoff bar energy U = EA L0 E^2 / 2")
def strain_energy(model: Model, u: np.ndarray) -> float:
    """Total strain energy ``Σ ½ EA L₀ E² + ½ uᵀ K_lin u``."""
    tr = _truss(model)
    x = _vector(model, u)
    _, E = _state(tr, x)
    return float(0.5 * np.sum(tr.EA * tr.L0 * E ** 2) + 0.5 * x @ (tr.K_lin @ x))


@cite("crisfield_1991", note="true axial force N = EA E l / L0")
def axial_forces(model: Model, u: np.ndarray) -> np.ndarray:
    """True (Cauchy) axial force ``EA E ℓ/L₀`` of every bar, tension positive, in element order."""
    tr = _truss(model)
    d, E = _state(tr, _vector(model, u))
    return np.asarray(tr.EA * E * np.linalg.norm(d, axis=1) / tr.L0)


# ---------------------------------------------------------------------------------------------- solvers
@dataclass
class _Problem:
    tr: _Truss
    T: sp.csr_matrix
    Tt: sp.csr_matrix
    ind: np.ndarray
    Fr: np.ndarray

    def residual(self, q: np.ndarray, lam: float) -> np.ndarray:
        return np.asarray(lam * self.Fr - self.Tt @ _f_int(self.tr, np.asarray(self.T @ q)))

    def factor(self, q: np.ndarray) -> solvers.Factorization:
        K = _k_t(self.tr, np.asarray(self.T @ q))
        return solvers.Factorization(sp.csr_matrix(self.Tt @ K @ self.T))


def _problem(model: Model, F: np.ndarray | None) -> _Problem:
    tr = _truss(model)
    T, g, ind = model.reduction()
    if np.any(g != 0):
        raise ValueError("non-linear analysis needs homogeneous constraints (zero prescribed values and MPC offsets)")
    if ind.size == 0:
        raise ValueError("no free DOFs")
    Fv = _vector(model, model.F if F is None else F, "F")
    T = sp.csr_matrix(T)
    Tt = T.T.tocsr()
    Fr = np.asarray(Tt @ Fv)
    if not np.all(np.isfinite(Fr)) or np.linalg.norm(Fr) == 0:
        raise ValueError("reference load is zero (or not finite) on the free DOFs")
    return _Problem(tr, T, Tt, ind, Fr)


def _result(P: _Problem, lams: list[float], qs: list[np.ndarray], its: list[int], converged: bool,
            method: str, history: list[dict[str, float]]) -> NonlinearResult:
    U = np.asarray(P.T @ np.column_stack(qs))
    return NonlinearResult(load_factor=np.array(lams), u=U, iterations=np.array(its, dtype=int),
                           converged=converged, method=method, history=history)


def _check_tols(tol: float, energy_tol: float, max_iter: int) -> None:
    if not (tol > 0 and energy_tol > 0 and max_iter >= 1):
        raise ValueError("tol and energy_tol must be positive, max_iter >= 1")


@cite("crisfield_1991", "bathe_2014", note="full Newton-Raphson under load control; force and energy norms")
def newton_raphson(model: Model, load_steps: int | Sequence[float] | np.ndarray = 10, tol: float = 1e-8,
                   max_iter: int = 25, energy_tol: float = 1e-12, F: np.ndarray | None = None,
                   divergence_check: bool = True) -> NonlinearResult:
    """Load-controlled full Newton-Raphson for the geometrically non-linear truss.

    Parameters
    ----------
    model : Model
        Bars (total Lagrangian), springs; homogeneous constraints.
    load_steps : int or array_like
        Number of equal increments up to ``λ = 1``, or the sequence of load factors.
    tol : float
        Force criterion ``‖R‖ ≤ tol · ‖F_r‖ · max|λ|`` (reduced residual ``R = λF_r − f_r``).
    max_iter : int
        Iterations per step.
    energy_tol : float
        Energy criterion ``|δqᵀR| ≤ energy_tol · |δq₁ᵀR₀|`` (relative to the first iteration of
        the step). Both criteria must hold.
    F : ndarray, optional
        Reference load (default :attr:`Model.F`).
    divergence_check : bool
        Declare a step diverging as soon as the residual norm grows after the first correction
        (``‖R_i‖ > ‖R_{i−1}‖`` for ``i ≥ 2``). Close to a solution full Newton converges
        monotonically (quadratically), so growth means the iterates have left the neighbourhood of
        the current equilibrium branch — typically because the load exceeds a limit point. With
        ``False`` such a step may instead converge to a remote branch (a static "jump" that load
        control cannot follow continuously).

    Returns
    -------
    NonlinearResult
        ``load_factor`` (``(n+1,)``, starting at 0), ``u`` (``(n_dof, n+1)``), ``iterations`` per
        step and ``history`` (per-step residual and energy norms).

    Raises
    ------
    ConvergenceError
        A step did not converge in ``max_iter`` iterations, became non-finite or met a singular
        tangent — under load control this happens beyond a limit point. ``exc.result`` holds the
        converged part of the path.
    """
    _check_tols(tol, energy_tol, max_iter)
    P = _problem(model, F)
    if np.ndim(load_steps) == 0:
        n = int(load_steps)  # type: ignore[arg-type]
        if n < 1:
            raise ValueError("load_steps must be >= 1")
        targets = np.linspace(0.0, 1.0, n + 1)[1:]
    else:
        targets = np.asarray(load_steps, dtype=float).ravel()
        if targets.size == 0 or not np.all(np.isfinite(targets)):
            raise ValueError("load factors must be finite")
    nF = float(np.linalg.norm(P.Fr))
    q: npt.NDArray[np.float64] = np.zeros(P.ind.size)
    lams, qs, its = [0.0], [q.copy()], [0]
    history: list[dict[str, float]] = []
    lam_scale = 0.0
    for s, lam in enumerate(targets, start=1):
        lam_scale = max(lam_scale, abs(float(lam)))
        ref = tol * nF * max(lam_scale, 1e-300)
        e0 = 0.0
        energy = 0.0
        ok, reason = False, "maximum iterations reached"
        trial: npt.NDArray[np.float64] = np.array(q, dtype=float)
        it = 0
        rn_prev = np.inf
        for it in range(max_iter + 1):
            R = P.residual(trial, float(lam))
            rn = float(np.linalg.norm(R))
            if not np.isfinite(rn):
                reason = "non-finite residual"
                break
            if divergence_check and it >= 2 and rn > rn_prev:
                reason = f"residual grew from {rn_prev:.3g} to {rn:.3g} at iteration {it} (diverging)"
                break
            rn_prev = rn
            if rn <= ref and (it == 0 or energy <= energy_tol * e0):
                ok = True
                break
            if it == max_iter:
                break
            try:
                dq = P.factor(trial).solve(R)
            except solvers.SingularMatrixError as exc:
                reason = f"singular tangent ({exc})"
                break
            energy = abs(float(dq @ R))
            if it == 0:
                e0 = max(energy, 1e-300)
            trial = trial + dq
        if not ok:
            part = _result(P, lams, qs, its, False, "newton-raphson", history)
            raise ConvergenceError(f"Newton-Raphson did not converge at step {s} (load factor {lam:g}): {reason}; "
                                   f"last converged load factor {lams[-1]:g}; beyond a limit point use arc_length",
                                   part, s, lams[-1])
        q = trial
        lams.append(float(lam))
        qs.append(q.copy())
        its.append(it)
        history.append({"load_factor": float(lam), "iterations": float(it), "residual": rn / (nF * lam_scale),
                        "energy": energy / e0 if e0 else 0.0})
    return _result(P, lams, qs, its, True, "newton-raphson", history)


@cite("bazant_cedolin_1991", note="two-bar (von Mises) truss snap-through used to verify the path")
@cite("crisfield_1981", "riks_1979", "crisfield_1991",
      note="cylindrical arc-length constraint |dq|^2 + psi^2 dlam^2 |F|^2 = dl^2; root closest to previous increment")
def arc_length(model: Model, length: float, max_steps: int = 100, lambda_max: float | None = None,
               dof: int | None = None, u_limit: float | None = None, psi: float = 0.0, tol: float = 1e-8,
               energy_tol: float = 1e-12, max_iter: int = 20, desired_iter: int = 5, adaptive: bool = True,
               max_arc: float | None = None, max_cuts: int = 10, F: np.ndarray | None = None) -> NonlinearResult:
    """Path following with Crisfield's (cylindrical) arc-length method.

    Each step solves equilibrium ``R(q, λ) = λF_r − f_r(q) = 0`` together with the constraint
    ``ΔqᵀΔq + ψ² Δλ² F_rᵀF_r = Δl²`` on the step increment. Iteration ``i`` computes
    ``δq_R = K_t⁻¹R`` and ``δq_t = K_t⁻¹F_r`` (one factorisation, two right-hand sides) and
    ``δλ`` from the quadratic ``a δλ² + b δλ + c = 0`` obtained by inserting
    ``Δq + δq_R + δλ δq_t`` into the constraint. Of the two roots the one whose new increment makes
    the smaller angle with the current increment is taken (largest
    ``ΔqᵀΔq_new + ψ²ΔλΔλ_new F_rᵀF_r``) — Crisfield's rule, which keeps the path from doubling
    back. The predictor direction follows the previous increment (sign of
    ``Δq_{n−1}ᵀδq_t + ψ²Δλ_{n−1}F_rᵀF_r``), so limit points in load (snap-through) and in
    displacement (snap-back) are passed.

    Parameters
    ----------
    model : Model
        As for :func:`newton_raphson`.
    length : float
        Initial arc length ``Δl`` (displacement units when ``psi = 0``).
    max_steps : int
        Maximum number of converged steps.
    lambda_max : float, optional
        Stop once the load factor reaches this value.
    dof, u_limit : int, float, optional
        Stop once ``|u[dof]| ≥ u_limit`` (global DOF index).
    psi : float
        Load-term scaling (``0``: cylindrical arc length; ``> 0``: spherical form).
    tol, energy_tol, max_iter
        Convergence criteria as in :func:`newton_raphson` (force norm relative to
        ``‖F_r‖ · max|λ|`` over the path so far).
    desired_iter : int
        With ``adaptive``, ``Δl ← Δl · √(desired_iter / iterations)`` after each step.
    max_arc : float, optional
        Upper bound on ``Δl`` (default ``10 ×`` the initial value).
    max_cuts : int
        A failed step (no convergence, complex roots) is retried with half the arc length this
        many times before :class:`ConvergenceError` is raised.
    F : ndarray, optional
        Reference load (default :attr:`Model.F`).

    Returns
    -------
    NonlinearResult
        Path ``(load_factor, u)`` starting from the unloaded state; ``history`` holds the arc
        length, iterations, cuts and norms of every step.
    """
    _check_tols(tol, energy_tol, max_iter)
    if not (np.isfinite(length) and length > 0):
        raise ValueError("arc length must be positive")
    if psi < 0 or not np.isfinite(psi):
        raise ValueError("psi must be finite and non-negative")
    if dof is not None and u_limit is None:
        raise ValueError("give u_limit together with dof")
    P = _problem(model, F)
    FF = float(P.Fr @ P.Fr)
    nF = float(np.sqrt(FF))
    psi2 = psi * psi
    dl = float(length)
    dl_max = 10 * dl if max_arc is None else float(max_arc)
    dl_min = dl * 0.5 ** (max_cuts + 2)
    q = np.zeros(P.ind.size)
    lam = 0.0
    lams, qs, its = [0.0], [q.copy()], [0]
    history: list[dict[str, float]] = []
    dq_prev: np.ndarray | None = None
    dlam_prev = 0.0
    lam_scale = 0.0

    for step in range(1, max_steps + 1):
        cuts = 0
        while True:
            ok, reason, it, rn, energy, e0 = False, "maximum iterations reached", 0, np.inf, 0.0, 0.0
            try:
                dt = P.factor(q).solve(P.Fr)
            except solvers.SingularMatrixError as exc:
                dt, reason = None, f"singular tangent at the start of the step ({exc})"
            if dt is not None:
                sign = 1.0
                if dq_prev is not None:
                    sign = 1.0 if float(dq_prev @ dt) + psi2 * dlam_prev * FF >= 0 else -1.0
                dlam = sign * dl / np.sqrt(float(dt @ dt) + psi2 * FF)
                dq = dlam * dt
                if lam_scale == 0.0:
                    lam_scale = abs(dlam)
                for it in range(max_iter + 1):
                    lam_t = lam + dlam
                    R = P.residual(q + dq, lam_t)
                    rn = float(np.linalg.norm(R))
                    scale = max(lam_scale, abs(lam_t))
                    if not np.isfinite(rn):
                        reason = "non-finite residual"
                        break
                    if rn <= tol * nF * scale and (it == 0 or energy <= energy_tol * e0):
                        ok = True
                        break
                    if it == max_iter:
                        break
                    try:
                        sol = P.factor(q + dq).solve(np.column_stack([R, P.Fr]))
                    except solvers.SingularMatrixError as exc:
                        reason = f"singular tangent ({exc})"
                        break
                    dR, dT = sol[:, 0], sol[:, 1]
                    w = dq + dR
                    a = float(dT @ dT) + psi2 * FF
                    b = 2 * (float(dT @ w) + psi2 * dlam * FF)
                    c = float(w @ w) + psi2 * dlam * dlam * FF - dl * dl
                    disc = b * b - 4 * a * c
                    if disc < 0:
                        reason = "complex roots of the arc-length constraint"
                        break
                    sq = np.sqrt(disc)
                    roots = ((-b + sq) / (2 * a), (-b - sq) / (2 * a))
                    # Crisfield's rule: keep the root whose increment is closest in direction to the last one
                    dlam_i = max(roots, key=lambda root: float(dq @ (w + root * dT))
                                 + psi2 * dlam * (dlam + root) * FF)
                    corr = dR + dlam_i * dT
                    energy = abs(float(corr @ R))
                    if it == 0:
                        e0 = max(energy, 1e-300)
                    dq = dq + corr
                    dlam = dlam + dlam_i
            if ok:
                break
            cuts += 1
            if cuts > max_cuts or dl * 0.5 < dl_min:
                part = _result(P, lams, qs, its, False, "arc-length", history)
                raise ConvergenceError(f"arc-length step {step} failed after {cuts - 1} cuts (arc length {dl:g}): "
                                       f"{reason}; last converged load factor {lam:g}", part, step, lam)
            dl *= 0.5
        q = q + dq
        lam = lam + dlam
        lam_scale = max(lam_scale, abs(lam))
        dq_prev, dlam_prev = dq, dlam
        lams.append(lam)
        qs.append(q.copy())
        its.append(it)
        history.append({"load_factor": lam, "arc_length": dl, "iterations": float(it), "cuts": float(cuts),
                        "residual": rn / (nF * max(lam_scale, 1e-300)), "energy": energy / e0 if e0 else 0.0})
        if adaptive:
            dl = float(np.clip(dl * np.sqrt(desired_iter / max(it, 1)), dl_min, dl_max))
        if lambda_max is not None and lam >= lambda_max:
            break
        if dof is not None and u_limit is not None:
            u_full = np.asarray(P.T @ q)
            if abs(u_full[int(dof)]) >= u_limit:
                break
    return _result(P, lams, qs, its, True, "arc-length", history)
