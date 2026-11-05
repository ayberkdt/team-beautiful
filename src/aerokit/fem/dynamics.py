"""Linear structural dynamics: damping, direct time integration, modal superposition, harmonic response.

Equation of motion (reduced by the model's constraints, ``u = T q``)::

    M ü + C u̇ + K u = F(t)

* :func:`newmark` — implicit Newmark-β with the Hilber-Hughes-Taylor α variant. The effective
  stiffness is factorised **once** (constant step) and reused every step.
* :func:`central_difference` — explicit central differences with lumped mass and a stability
  check ``Δt < 2/ω_max``.
* :func:`modal_superposition` — mode-by-mode solution, either exact for a piecewise-linear load
  (matrix exponential of the SDOF state equation) or with Newmark on the modal SDOFs.
* :func:`harmonic` / :func:`harmonic_modal` — steady-state response ``(K − ω²M + iωC) U = F``.
* :func:`rayleigh_coefficients` / :func:`damping_matrix` — ``C = αM + βK + Σ c_dashpot``.

Constraints
    Only homogeneous constraints are supported (prescribed values and MPC right-hand sides must be
    zero): the dynamic solution then lives in the column space of ``T`` and no support motion
    terms are needed. A non-zero prescribed value raises :class:`ValueError`.

Loads
    ``load`` may be ``None`` (free vibration), an array ``(n_dof,)`` (constant in time),
    an array ``(n_dof, n_t)`` (one column per time point of ``t``) or a callable ``f(t) → (n_dof,)``
    evaluated at the time points.

Results
    :class:`~aerokit.fem.results.TransientResult` with ``u, v, a`` of shape ``(n_dof, n_t)`` and
    ``energy`` of shape ``(3, n_t)``: rows kinetic ``½ u̇ᵀMu̇``, strain ``½ uᵀKu`` and their sum.

Units SI; frequencies in Hz unless the name says ``omega`` [rad/s].
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

import numpy as np
import scipy.linalg as sla
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from aerokit.fem import solvers
from aerokit.fem.model import Model
from aerokit.fem.results import HarmonicResult, TransientResult
from aerokit.references import cite

__all__ = ["rayleigh_coefficients", "element_damping", "damping_matrix", "critical_time_step", "newmark",
           "central_difference", "modal_superposition", "harmonic", "harmonic_modal"]

LoadSpec = np.ndarray | Callable[[float], np.ndarray] | None
"""Load specification accepted by the time-domain solvers (see module docstring)."""


# ---------------------------------------------------------------------------------------------- damping
@cite("chopra_2012", note="Rayleigh damping, zeta(omega) = a0/(2 omega) + a1 omega/2")
def rayleigh_coefficients(zeta: float | Sequence[float], f1: float, f2: float) -> tuple[float, float]:
    """Rayleigh coefficients ``(α, β)`` of ``C = αM + βK`` giving damping ``zeta`` at ``f1`` and ``f2``.

    The modal damping ratio of a Rayleigh matrix is ``ζ(ω) = α/(2ω) + βω/2``. Imposing
    ``ζ(ω₁) = ζ₁`` and ``ζ(ω₂) = ζ₂`` gives the 2×2 system solved here; for ``ζ₁ = ζ₂ = ζ``
    it reduces to ``α = 2ζω₁ω₂/(ω₁ + ω₂)``, ``β = 2ζ/(ω₁ + ω₂)``.

    Parameters
    ----------
    zeta : float or (float, float)
        Target damping ratio(s) at ``f1`` and ``f2``.
    f1, f2 : float
        The two frequencies [Hz], positive and distinct.

    Returns
    -------
    alpha : float
        Mass-proportional coefficient [1/s].
    beta : float
        Stiffness-proportional coefficient [s].
    """
    z = np.broadcast_to(np.asarray(zeta, dtype=float), (2,))
    if not np.all(np.isfinite(z)) or np.any(z < 0):
        raise ValueError("damping ratios must be finite and non-negative")
    if not (np.isfinite(f1) and np.isfinite(f2)) or f1 <= 0 or f2 <= 0 or f1 == f2:
        raise ValueError("f1 and f2 must be positive, finite and distinct")
    w1, w2 = 2 * np.pi * f1, 2 * np.pi * f2
    A = np.array([[1 / (2 * w1), w1 / 2], [1 / (2 * w2), w2 / 2]])
    alpha, beta = np.linalg.solve(A, z)
    return float(alpha), float(beta)


@cite("cook_2002", note="assembly of element matrices into global matrices")
def element_damping(model: Model) -> sp.csr_matrix:
    """Assemble the damping matrices ``c(X)`` of all elements that provide one (e.g. dashpots)."""
    rows: list[np.ndarray] = []
    cols: list[np.ndarray] = []
    vals: list[np.ndarray] = []
    for e in model.elements:
        c = getattr(e, "c", None)
        if not callable(c):
            continue
        ce = np.asarray(c(model.X), dtype=float)
        idx = model.equivalent_dof(e)
        if ce.shape != (idx.size, idx.size):
            raise ValueError(f"{type(e).__name__}: damping matrix shape {ce.shape}, expected {idx.size}")
        rows.append(np.repeat(idx, idx.size))
        cols.append(np.tile(idx, idx.size))
        vals.append(ce.ravel())
    n = model.n_dof
    if not rows:
        return sp.csr_matrix((n, n))
    return sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                         shape=(n, n)).tocsr()


def _check_rayleigh(damping: tuple[float, float]) -> tuple[float, float]:
    if len(damping) != 2:
        raise ValueError("damping must be a Rayleigh pair (alpha, beta)")
    a, b = float(damping[0]), float(damping[1])
    if not (np.isfinite(a) and np.isfinite(b)) or a < 0 or b < 0:
        raise ValueError("Rayleigh coefficients must be finite and non-negative")
    return a, b


@cite("chopra_2012", note="classical (Rayleigh) damping matrix")
def damping_matrix(model: Model, alpha: float = 0.0, beta: float = 0.0, lumped: bool = False) -> sp.csr_matrix:
    """Global damping matrix ``C = αM + βK + C_elements``.

    Parameters
    ----------
    model : Model
    alpha, beta : float
        Rayleigh coefficients (see :func:`rayleigh_coefficients`).
    lumped : bool
        Use the lumped mass matrix for the ``αM`` term.
    """
    a, b = _check_rayleigh((alpha, beta))
    C = element_damping(model)
    if a:
        C = C + a * model.M(lumped=lumped)
    if b:
        C = C + b * model.K()
    return sp.csr_matrix(C)


# ---------------------------------------------------------------------------------------------- helpers
@dataclass(frozen=True)
class _System:
    """Reduced matrices ``Tᵀ A T`` and the transformation ``T`` (homogeneous constraints)."""

    T: sp.csr_matrix
    ind: np.ndarray
    K: sp.csr_matrix
    M: sp.csr_matrix
    C: sp.csr_matrix


def _transformation(model: Model) -> tuple[sp.csr_matrix, np.ndarray]:
    T, g, ind = model.reduction()
    if np.any(g != 0):
        bad = [model.dof_label(int(i)) for i in np.flatnonzero(g)[:4]]
        raise ValueError("dynamic analysis needs homogeneous constraints; non-zero prescribed value or MPC "
                         f"offset at {', '.join(bad)} (model support motion as an applied load instead)")
    if ind.size == 0:
        raise ValueError("no free DOFs")
    return sp.csr_matrix(T), ind


def _system(model: Model, damping: tuple[float, float], lumped: bool) -> _System:
    T, ind = _transformation(model)
    Tt = T.T.tocsr()
    K, M = model.K(), model.M(lumped=lumped)
    a, b = _check_rayleigh(damping)
    C = element_damping(model) + a * M + b * K

    def red(A: sp.spmatrix) -> sp.csr_matrix:
        return sp.csr_matrix(Tt @ sp.csr_matrix(A) @ T)

    return _System(T=T, ind=ind, K=red(K), M=red(M), C=red(C))


def _time_grid(t: np.ndarray | Sequence[float]) -> tuple[np.ndarray, float]:
    t = np.asarray(t, dtype=float).ravel()
    if t.size < 2 or not np.all(np.isfinite(t)):
        raise ValueError("t must contain at least two finite time points")
    steps = np.diff(t)
    dt = float(steps.mean())
    if dt <= 0 or np.max(np.abs(steps - dt)) > 1e-8 * dt:
        raise ValueError("t must be strictly increasing with a constant time step")
    return t, dt


def _full_load(model: Model, load: LoadSpec, t: np.ndarray) -> np.ndarray:
    """Load history ``(n_dof, n_t)``."""
    n, nt = model.n_dof, t.size
    if load is None:
        return np.zeros((n, nt))
    if callable(load):
        F = np.column_stack([np.asarray(load(float(tk)), dtype=float).ravel() for tk in t])
    else:
        F = np.asarray(load, dtype=float)
        if F.ndim == 1:
            F = np.repeat(F[:, None], nt, axis=1)
    if F.shape != (n, nt):
        raise ValueError(f"load must have shape ({n},) or ({n}, {nt}); got {F.shape}")
    if not np.all(np.isfinite(F)):
        raise ValueError("load must be finite")
    return F


def _initial(model: Model, T: sp.csr_matrix, ind: np.ndarray, x: np.ndarray | None, name: str) -> np.ndarray:
    """Reduced initial vector ``q`` with ``T q = x`` (checked)."""
    if x is None:
        return np.zeros(ind.size)
    x = np.asarray(x, dtype=float).ravel()
    if x.shape != (model.n_dof,) or not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must be a finite vector of length {model.n_dof}")
    q = x[ind].copy()
    if float(np.linalg.norm(T @ q - x)) > 1e-9 * max(float(np.linalg.norm(x)), 1e-300):
        raise ValueError(f"{name} violates the model constraints")
    return q


def _factor_mass(M: sp.csr_matrix) -> solvers.Factorization:
    try:
        return solvers.Factorization(M)
    except solvers.SingularMatrixError as exc:
        raise solvers.SingularMatrixError(
            "mass matrix is singular (massless DOFs, e.g. rotations with lumped mass); "
            "use the consistent mass, add rotary inertia (PointMass) or condense those DOFs") from exc


def _energy(M: sp.csr_matrix, K: sp.csr_matrix, q: np.ndarray, v: np.ndarray) -> np.ndarray:
    kin = 0.5 * np.einsum("ij,ij->j", v, M @ v)
    strain = 0.5 * np.einsum("ij,ij->j", q, K @ q)
    return np.vstack([kin, strain, kin + strain])


# ---------------------------------------------------------------------------------------------- Newmark / HHT
@cite("newmark_1959", "hilber_hughes_taylor_1977", "hughes_2000",
      note="Newmark-beta update formulas; HHT-alpha weighted equilibrium")
def _newmark_core(M: sp.spmatrix, C: sp.spmatrix, K: sp.spmatrix, F: np.ndarray, q0: np.ndarray,
                  v0: np.ndarray, dt: float, beta: float, gamma: float, alpha: float
                  ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate ``M a + C v + K q = F`` (reduced, sparse) with Newmark/HHT; returns ``q, v, a``.

    With ``Δq = q_{n+1} − q_n`` the Newmark relations are::

        a_{n+1} = Δq/(βΔt²) − v_n/(βΔt) − (1/(2β) − 1) a_n
        v_{n+1} = γΔq/(βΔt) + (1 − γ/β) v_n + Δt(1 − γ/(2β)) a_n

    and HHT enforces ``M a_{n+1} + (1+α)(C v_{n+1} + K q_{n+1}) − α(C v_n + K q_n)
    = (1+α) F_{n+1} − α F_n``. Substituting gives ``K_eff Δq = r_n`` with the constant
    ``K_eff = M/(βΔt²) + (1+α)γ C/(βΔt) + (1+α) K``, factorised once.
    """
    n, nt = q0.size, F.shape[1]
    q = np.empty((n, nt))
    v = np.empty((n, nt))
    a = np.empty((n, nt))
    q[:, 0], v[:, 0] = q0, v0
    a[:, 0] = _factor_mass(sp.csr_matrix(M)).solve(F[:, 0] - C @ v0 - K @ q0)
    Keff = sp.csr_matrix(M / (beta * dt * dt) + ((1 + alpha) * gamma / (beta * dt)) * C + (1 + alpha) * K)
    fac = solvers.Factorization(Keff)
    c1, c2 = 1 / (beta * dt), 1 / (2 * beta) - 1
    c3, c4 = 1 - gamma / beta, dt * (1 - gamma / (2 * beta))
    for k in range(nt - 1):
        qn, vn, an = q[:, k], v[:, k], a[:, k]
        Fa = (1 + alpha) * F[:, k + 1] - alpha * F[:, k]
        rhs = (Fa - K @ qn + M @ (c1 * vn + c2 * an)
               - C @ ((1 + alpha) * (c3 * vn + c4 * an) - alpha * vn))
        dq = fac.solve(rhs)
        a[:, k + 1] = dq / (beta * dt * dt) - c1 * vn - c2 * an
        v[:, k + 1] = gamma * c1 * dq + c3 * vn + c4 * an
        q[:, k + 1] = qn + dq
    return q, v, a


@cite("newmark_1959", "hilber_hughes_taylor_1977", "hughes_2000",
      note="implicit Newmark-beta and HHT-alpha; optimal HHT parameters beta = (1-alpha)^2/4, gamma = (1-2 alpha)/2")
def newmark(model: Model, t: np.ndarray | Sequence[float], load: LoadSpec = None,
            u0: np.ndarray | None = None, v0: np.ndarray | None = None, beta: float | None = None,
            gamma: float | None = None, alpha: float = 0.0, damping: tuple[float, float] = (0.0, 0.0),
            lumped: bool = False) -> TransientResult:
    """Implicit direct integration with the Newmark-β / HHT-α method (constant time step).

    Parameters
    ----------
    model : Model
        Model with homogeneous constraints.
    t : array_like, shape (n_t,)
        Equally spaced time points [s]; ``t[0]`` is the initial time.
    load : None, ndarray or callable
        ``None``, ``(n_dof,)`` constant, ``(n_dof, n_t)`` history or ``f(t) → (n_dof,)``.
    u0, v0 : ndarray (n_dof,), optional
        Initial displacement and velocity (default zero); must satisfy the constraints.
    beta, gamma : float, optional
        Newmark parameters. Default (``None``): the HHT-optimal values ``β = (1 − α)²/4``,
        ``γ = (1 − 2α)/2``, i.e. the average-acceleration (trapezoidal) rule ``β = 1/4, γ = 1/2``
        for ``α = 0``. Unconditional stability needs ``2β ≥ γ ≥ 1/2``.
    alpha : float
        HHT parameter in ``[−1/3, 0]``; ``α < 0`` damps high frequencies (``0``: plain Newmark).
    damping : (float, float)
        Rayleigh coefficients ``(α_R, β_R)``; element dashpots are always included.
    lumped : bool
        Use the lumped mass matrix.

    Returns
    -------
    TransientResult
        ``t``, ``u``, ``v``, ``a`` (``(n_dof, n_t)``), ``energy`` (``(3, n_t)``: kinetic, strain,
        total) and ``method``.

    Notes
    -----
    The initial acceleration is consistent: ``M a₀ = F₀ − C v₀ − K u₀``. The effective stiffness
    ``K_eff`` is factorised once with :class:`aerokit.fem.solvers.Factorization` and reused at
    every step, so a step costs one forward/back substitution.
    """
    if not -1 / 3 - 1e-12 <= alpha <= 0:
        raise ValueError("HHT alpha must lie in [-1/3, 0]")
    beta = (1 - alpha) ** 2 / 4 if beta is None else float(beta)
    gamma = (1 - 2 * alpha) / 2 if gamma is None else float(gamma)
    if not beta > 0 or not gamma > 0:
        raise ValueError("Newmark beta and gamma must be positive")
    tt, dt = _time_grid(t)
    S = _system(model, damping, lumped)
    F = S.T.T @ _full_load(model, load, tt)
    q0 = _initial(model, S.T, S.ind, u0, "u0")
    qd0 = _initial(model, S.T, S.ind, v0, "v0")
    q, v, a = _newmark_core(S.M, S.C, S.K, F, q0, qd0, dt, beta, gamma, alpha)
    name = "newmark" if alpha == 0 else "hht-alpha"
    return TransientResult(t=tt, u=np.asarray(S.T @ q), v=np.asarray(S.T @ v), a=np.asarray(S.T @ a),
                           method=f"{name}(beta={beta:g}, gamma={gamma:g}, alpha={alpha:g})",
                           energy=_energy(S.M, S.K, q, v))


# ---------------------------------------------------------------------------------------------- explicit
def _omega_max(S: _System) -> float:
    w2, _ = solvers.generalized_eigh(S.K, S.M, 1, which="LA")
    return float(np.sqrt(max(float(w2[0]), 0.0)))


@cite("bathe_2014", "hughes_2000", note="central difference stability limit dt <= 2/omega_max")
def critical_time_step(model: Model, lumped: bool = True) -> float:
    """Stability limit ``Δt_cr = 2/ω_max`` of :func:`central_difference`.

    ``ω_max²`` is the largest eigenvalue of ``K φ = ω² M φ`` (reduced). Classical viscous damping
    treated as in :func:`central_difference` (``C/(2Δt)`` on the left-hand side) does not lower the
    limit: for each mode
    ``ü + 2ζωu̇ + ω²u = 0`` the characteristic polynomial
    ``(1 + ζΩ)z² − (2 − Ω²)z + (1 − ζΩ)`` (``Ω = ωΔt``) satisfies the Jury conditions iff
    ``Ω ≤ 2`` for every ``ζ ≥ 0``.

    Raises
    ------
    ValueError
        If the mass matrix is not positive definite (massless DOFs).
    """
    S = _system(model, (0.0, 0.0), lumped)
    d = S.M.diagonal()
    if np.any(d <= 0):
        raise ValueError("explicit integration needs a positive mass on every free DOF "
                         "(add rotary inertia with PointMass or use newmark)")
    w = _omega_max(S)
    if w == 0:
        return float("inf")
    return 2.0 / w


@cite("bathe_2014", "hughes_2000", note="explicit central difference method")
def central_difference(model: Model, t: np.ndarray | Sequence[float], load: LoadSpec = None,
                       u0: np.ndarray | None = None, v0: np.ndarray | None = None,
                       damping: tuple[float, float] = (0.0, 0.0), lumped: bool = True) -> TransientResult:
    """Explicit central-difference integration with a stability check.

    Recurrence (reduced)::

        (M/Δt² + C/(2Δt)) u_{n+1} = F_n − (K − 2M/Δt²) u_n − (M/Δt² − C/(2Δt)) u_{n−1}

    started with ``u_{−1} = u₀ − Δt v₀ + Δt²/2 a₀``, ``M a₀ = F₀ − C v₀ − K u₀``; then
    ``v_n = (u_{n+1} − u_{n−1})/(2Δt)``, ``a_n = (u_{n+1} − 2u_n + u_{n−1})/Δt²``. With lumped
    mass and no damping (or mass-proportional damping) the left-hand matrix is diagonal and each step
    is a vector division; otherwise it is factorised once.

    Parameters
    ----------
    model, t, load, u0, v0, damping
        As for :func:`newmark`.
    lumped : bool
        Lumped (diagonal) mass, default ``True``.

    Raises
    ------
    ValueError
        If ``Δt ≥ Δt_cr = 2/ω_max`` (see :func:`critical_time_step`) or if a free DOF has no mass.
    """
    tt, dt = _time_grid(t)
    S = _system(model, damping, lumped)
    if np.any(S.M.diagonal() <= 0):
        raise ValueError("explicit integration needs a positive mass on every free DOF "
                         "(add rotary inertia with PointMass or use newmark)")
    w = _omega_max(S)
    if w > 0 and dt >= 2.0 / w:
        raise ValueError(f"central difference is unstable: dt = {dt:.4g} s >= dt_cr = 2/omega_max = "
                         f"{2.0 / w:.4g} s; reduce the time step")
    F = S.T.T @ _full_load(model, load, tt)
    q0 = _initial(model, S.T, S.ind, u0, "u0")
    qd0 = _initial(model, S.T, S.ind, v0, "v0")
    a0 = _factor_mass(S.M).solve(F[:, 0] - S.C @ qd0 - S.K @ q0)
    lhs = sp.csr_matrix(S.M / dt ** 2 + S.C / (2 * dt))
    off = lhs - sp.diags(lhs.diagonal())
    if off.count_nonzero() == 0:
        dlhs = lhs.diagonal()
        step: Callable[[np.ndarray], np.ndarray] = lambda r: r / dlhs
    else:
        step = solvers.Factorization(lhs).solve
    A1 = sp.csr_matrix(S.K - (2 / dt ** 2) * S.M)
    A0 = sp.csr_matrix(S.M / dt ** 2 - S.C / (2 * dt))
    n, nt = q0.size, tt.size
    q = np.empty((n, nt + 1))                     # q[:, k] = u_k, last column u_{n_t}
    q[:, 0] = q0
    prev = q0 - dt * qd0 + 0.5 * dt * dt * a0
    for k in range(nt):
        q[:, k + 1] = step(F[:, k] - A1 @ q[:, k] - A0 @ prev)
        prev = q[:, k]
    v = np.empty((n, nt))
    a = np.empty((n, nt))
    v[:, 0], a[:, 0] = qd0, a0
    v[:, 1:] = (q[:, 2:] - q[:, :-2]) / (2 * dt)
    a[:, 1:] = (q[:, 2:] - 2 * q[:, 1:-1] + q[:, :-2]) / dt ** 2
    qq = q[:, :nt]
    return TransientResult(t=tt, u=np.asarray(S.T @ qq), v=np.asarray(S.T @ v), a=np.asarray(S.T @ a),
                           method="central-difference", energy=_energy(S.M, S.K, qq, v))


# ---------------------------------------------------------------------------------------------- modal
def _modal_basis(model: Model, n_modes: int | None, lumped: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(ω, Φ (n_dof, m), M)`` with mass-normalised modes."""
    if any(callable(getattr(e, "c", None)) for e in model.elements):
        raise ValueError("model has damper elements (non-classical damping): use newmark or harmonic")
    _transformation(model)                                    # homogeneous-constraint check
    n = model.n_dof if n_modes is None else int(n_modes)
    if n < 1:
        raise ValueError("n_modes must be positive")
    res = model.modal(n=n, lumped=lumped)
    return np.asarray(res.omega, dtype=float), np.asarray(res.modes, dtype=float), model.M(lumped=lumped)


def _modal_zeta(omega: np.ndarray, zeta: float | Sequence[float] | np.ndarray,
                rayleigh: tuple[float, float] | None) -> np.ndarray:
    z = np.broadcast_to(np.asarray(zeta, dtype=float), omega.shape).copy()
    if rayleigh is not None:
        a, b = _check_rayleigh(rayleigh)
        with np.errstate(divide="ignore"):
            z = z + np.where(omega > 0, a / (2 * np.where(omega > 0, omega, 1.0)), 0.0) + b * omega / 2
        if a > 0 and np.any(omega == 0):
            raise ValueError("mass-proportional damping is undefined for rigid-body modes in modal form")
    if not np.all(np.isfinite(z)) or np.any(z < 0):
        raise ValueError("modal damping ratios must be finite and non-negative")
    return z


@cite("chopra_2012", note="time stepping exact for piecewise-linear excitation")
def _sdof_exact(omega: np.ndarray, zeta: np.ndarray, P: np.ndarray, q0: np.ndarray, v0: np.ndarray,
                dt: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact recurrence for ``q̈ + 2ζωq̇ + ω²q = p(t)`` with ``p`` linear within each step.

    The augmented state ``z = [q, q̇, p, ṗ]`` obeys ``ż = A z`` with
    ``A = [[0, 1, 0, 0], [−ω², −2ζω, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]]`` inside a step, so
    ``z_{n+1} = exp(AΔt) z_n`` is exact (it covers ``ω = 0`` and ``ζ ≥ 1`` alike).
    """
    m, nt = P.shape
    q = np.empty((m, nt))
    v = np.empty((m, nt))
    q[:, 0], v[:, 0] = q0, v0
    E = np.empty((m, 2, 4))
    for i in range(m):
        A = np.zeros((4, 4))
        A[0, 1] = 1.0
        A[1, 0], A[1, 1], A[1, 2] = -omega[i] ** 2, -2 * zeta[i] * omega[i], 1.0
        A[2, 3] = 1.0
        E[i] = sla.expm(A * dt)[:2]
    for k in range(nt - 1):
        p0, r = P[:, k], (P[:, k + 1] - P[:, k]) / dt
        qk, vk = q[:, k], v[:, k]
        q[:, k + 1] = E[:, 0, 0] * qk + E[:, 0, 1] * vk + E[:, 0, 2] * p0 + E[:, 0, 3] * r
        v[:, k + 1] = E[:, 1, 0] * qk + E[:, 1, 1] * vk + E[:, 1, 2] * p0 + E[:, 1, 3] * r
    a = P - 2 * (zeta * omega)[:, None] * v - (omega ** 2)[:, None] * q
    return q, v, a


@cite("chopra_2012", "newmark_1959", note="classical modal superposition of decoupled SDOF equations")
def modal_superposition(model: Model, t: np.ndarray | Sequence[float], load: LoadSpec = None,
                        n_modes: int | None = None, zeta: float | Sequence[float] | np.ndarray = 0.0,
                        u0: np.ndarray | None = None, v0: np.ndarray | None = None,
                        rayleigh: tuple[float, float] | None = None, lumped: bool = False,
                        method: Literal["exact", "newmark"] = "exact", beta: float = 0.25,
                        gamma: float = 0.5) -> TransientResult:
    """Transient response by superposition of ``n_modes`` mass-normalised modes.

    Each modal coordinate obeys ``q̈ᵢ + 2ζᵢωᵢq̇ᵢ + ωᵢ²qᵢ = φᵢᵀF(t)`` with
    ``qᵢ(0) = φᵢᵀMu₀``, ``q̇ᵢ(0) = φᵢᵀMv₀``; ``u = Σ φᵢ qᵢ``.

    Parameters
    ----------
    model, t, load, u0, v0, lumped
        As for :func:`newmark`.
    n_modes : int, optional
        Number of modes (default: all).
    zeta : float or array_like (n_modes,)
        Viscous modal damping ratios.
    rayleigh : (float, float), optional
        Rayleigh coefficients; adds ``α/(2ωᵢ) + βωᵢ/2`` to ``zeta`` (the modal form of
        ``C = αM + βK``, so the result matches :func:`newmark` with ``damping=rayleigh``).
    method : {"exact", "newmark"}
        ``exact``: closed-form recurrence for a load varying linearly between time points (no
        time-step error for such loads). ``newmark``: Newmark (``beta``, ``gamma``) on the modal
        SDOFs — with all modes this reproduces :func:`newmark` with the same ``Δt`` to round-off.

    Raises
    ------
    ValueError
        Element dampers present (non-classical damping), or non-homogeneous constraints.
    """
    tt, dt = _time_grid(t)
    omega, Phi, M = _modal_basis(model, n_modes, lumped)
    z = _modal_zeta(omega, zeta, rayleigh)
    P = Phi.T @ _full_load(model, load, tt)
    uu0 = np.zeros(model.n_dof) if u0 is None else np.asarray(u0, dtype=float).ravel()
    vv0 = np.zeros(model.n_dof) if v0 is None else np.asarray(v0, dtype=float).ravel()
    if uu0.shape != (model.n_dof,) or vv0.shape != (model.n_dof,):
        raise ValueError(f"u0 and v0 must have length {model.n_dof}")
    q0, qd0 = Phi.T @ (M @ uu0), Phi.T @ (M @ vv0)
    if method == "exact":
        q, v, a = _sdof_exact(omega, z, P, q0, qd0, dt)
    elif method == "newmark":
        eye = sp.identity(omega.size, format="csr")
        q, v, a = _newmark_core(eye, sp.diags(2 * z * omega).tocsr(), sp.diags(omega ** 2).tocsr(), P, q0, qd0,
                                dt, float(beta), float(gamma), 0.0)
    else:
        raise ValueError("method must be 'exact' or 'newmark'")
    kin = 0.5 * np.sum(v * v, axis=0)
    strain = 0.5 * np.sum((omega ** 2)[:, None] * q * q, axis=0)
    return TransientResult(t=tt, u=Phi @ q, v=Phi @ v, a=Phi @ a,
                           method=f"modal-{method}({omega.size} modes)",
                           energy=np.vstack([kin, strain, kin + strain]))


# ---------------------------------------------------------------------------------------------- harmonic
def _frequencies(frequencies: float | Sequence[float] | np.ndarray) -> np.ndarray:
    f = np.atleast_1d(np.asarray(frequencies, dtype=float)).ravel()
    if f.size == 0 or not np.all(np.isfinite(f)) or np.any(f < 0):
        raise ValueError("frequencies must be finite and non-negative [Hz]")
    return f


def _amplitude(model: Model, F: np.ndarray | None) -> np.ndarray:
    A = np.asarray(model.F if F is None else F).ravel()
    if A.shape != (model.n_dof,) or not np.all(np.isfinite(A)):
        raise ValueError(f"load amplitude must be a finite vector of length {model.n_dof}")
    return A.astype(complex)


@cite("clough_penzien_1993", "chopra_2012", note="steady-state harmonic response; hysteretic damping K(1 + 2i zeta)")
def harmonic(model: Model, frequencies: float | Sequence[float] | np.ndarray, F: np.ndarray | None = None,
             damping: tuple[float, float] | float = (0.0, 0.0), lumped: bool = False) -> HarmonicResult:
    """Direct frequency response ``(K − ω²M + iωC) U = F`` with ``u(t) = Re(U e^{iωt})``.

    Parameters
    ----------
    model : Model
        Model with homogeneous constraints.
    frequencies : float or array_like
        Excitation frequencies [Hz].
    F : ndarray (n_dof,), optional
        Complex or real load amplitude (default :attr:`Model.F`).
    damping : (float, float) or float
        Rayleigh pair ``(α, β)`` for viscous ``C = αM + βK``; or a scalar ``ζ`` for structural
        (hysteretic) damping ``K → (1 + 2iζ) K``, which equals viscous modal damping ``ζ`` at
        every resonance. Element dashpots add ``iω C_e`` in both cases.
    lumped : bool
        Lumped mass matrix.

    Returns
    -------
    HarmonicResult
        ``f`` [Hz] and complex ``U`` of shape ``(n_dof, n_f)``.

    Raises
    ------
    aerokit.fem.solvers.SingularMatrixError
        At an undamped resonance (singular dynamic stiffness).
    """
    f = _frequencies(frequencies)
    amp = _amplitude(model, F)
    if np.ndim(damping) == 0:
        zeta = float(damping)                                   # type: ignore[arg-type]
        if not np.isfinite(zeta) or zeta < 0:
            raise ValueError("hysteretic damping ratio must be finite and non-negative")
        S = _system(model, (0.0, 0.0), lumped)
        Kc = (1 + 2j * zeta) * S.K
    else:
        S = _system(model, damping, lumped)                     # type: ignore[arg-type]
        Kc = S.K.astype(complex)
    Fr = S.T.T @ amp
    U = np.empty((model.n_dof, f.size), dtype=complex)
    for k, fk in enumerate(f):
        w = 2 * np.pi * fk
        A = sp.csc_matrix(Kc - (w * w) * S.M + (1j * w) * S.C)
        try:
            lu = spla.splu(A, permc_spec="MMD_AT_PLUS_A")
        except RuntimeError as exc:
            raise solvers.SingularMatrixError(f"dynamic stiffness singular at f = {fk:g} Hz "
                                              "(undamped resonance or unsupported model)") from exc
        x = lu.solve(Fr)
        if not np.all(np.isfinite(x)):
            raise solvers.SingularMatrixError(f"non-finite response at f = {fk:g} Hz")
        U[:, k] = S.T @ x
    return HarmonicResult(f=f, U=U, method="direct")


@cite("chopra_2012", "clough_penzien_1993", note="modal frequency response function")
def harmonic_modal(model: Model, frequencies: float | Sequence[float] | np.ndarray, F: np.ndarray | None = None,
                   n_modes: int | None = None, zeta: float | Sequence[float] | np.ndarray = 0.0,
                   rayleigh: tuple[float, float] | None = None, hysteretic: bool = False,
                   lumped: bool = False) -> HarmonicResult:
    """Frequency response by modal superposition.

    ``U = Σ φᵢ (φᵢᵀF) / (ωᵢ² − ω² + 2iζᵢωᵢω)`` (viscous), or with denominator
    ``ωᵢ²(1 + 2iζᵢ) − ω²`` when ``hysteretic`` (matches :func:`harmonic` with scalar ``damping``).

    Parameters
    ----------
    model, frequencies, F, lumped
        As for :func:`harmonic`.
    n_modes : int, optional
        Number of modes (default: all).
    zeta : float or array_like
        Modal damping ratios.
    rayleigh : (float, float), optional
        Rayleigh coefficients added in modal form (viscous only).
    hysteretic : bool
        Interpret ``zeta`` as structural damping.
    """
    f = _frequencies(frequencies)
    amp = _amplitude(model, F)
    omega, Phi, _ = _modal_basis(model, n_modes, lumped)
    z = _modal_zeta(omega, zeta, rayleigh if not hysteretic else None)
    if hysteretic and rayleigh is not None:
        raise ValueError("rayleigh damping is viscous; do not combine it with hysteretic=True")
    p = Phi.T @ amp
    w = 2 * np.pi * f
    if hysteretic:
        den = (omega ** 2 * (1 + 2j * z))[:, None] - (w ** 2)[None, :]
    else:
        den = (omega ** 2)[:, None] - (w ** 2)[None, :] + 2j * (z * omega)[:, None] * w[None, :]
    if np.any(den == 0):
        raise solvers.SingularMatrixError("excitation exactly at an undamped natural frequency")
    U = Phi @ (p[:, None] / den)
    return HarmonicResult(f=f, U=U, method=f"modal({omega.size} modes{', hysteretic' if hysteretic else ''})")
