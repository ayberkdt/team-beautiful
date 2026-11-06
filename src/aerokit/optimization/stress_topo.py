"""Stress-constrained topology optimisation: minimum mass subject to clustered P-norm von Mises constraints (2-D Q4).

Formulation (P1) of Holmberg, Torstenfelt & Klarbring (2013), read in the LiU post-print on 2026-11-03
(prev_guess/01_Ansys/research/Optimizasyon kaynakları/TO_kaynak_paketi.md §4a):

* stiffness ρ^q with q = 3, density filter with cone weights, initial ρ = 0.5;
* stress at the element centroid, relaxed as σ_a = η_S(ρ_e) σ̂_a with η_S = ρ^(1/2), σ̂ = E B u;
* cluster i: σ_i^PN = ((1/N_i) Σ_{a∈Ω_i} (σ_a^vM/σ̄)^p)^(1/p) ≤ 1 with p = 8;
* "stress level" clustering: points sorted by stress, consecutive blocks of n_e/n_c; re-clustering every iteration
  gave the best local stress control in their L-beam study (Table 1);
* elements under the load are not design variables and not stress-evaluation points.

Gradient: explicit term through η_S, implicit term by one adjoint solve per cluster with the stiffness matrix
already factorised for the state (Holmberg §7). The tests check it against finite differences.

The optimiser is MMA with m constraints; this module solves the MMA subproblem through its dual (concave, one
variable per constraint) with L-BFGS-B. Approximation coefficients and the artificial-variable penalty (c = 1000,
d = 1) are those of :func:`aerokit.optimization.topology.mma_subproblem` (Svanberg 1987 via the mmapy port); the
dual solver and the move limit 0.1 are this module's choices (Holmberg narrowed the MMA move limits but gives no
value).
"""
from __future__ import annotations

from typing import Any

import numpy as np
import scipy.optimize as so
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from aerokit.optimization import topology as tp
from aerokit.references import cite

__all__ = ["centroid_B", "plane_stress_D", "element_stress", "StressConstraint", "mma_multi", "topopt_stress",
           "holmberg_l_beam"]

_XI = np.array([-1.0, 1.0, 1.0, -1.0])        # element node order LL, LR, UR, UL (top88 edofMat, y up)
_ETA = np.array([-1.0, -1.0, 1.0, 1.0])


def centroid_B(h: float = 1.0) -> np.ndarray:
    """(3, 8) strain–displacement matrix of a square Q4 element of side ``h`` at its centroid."""
    dNdx, dNdy = _XI / (2.0 * h), _ETA / (2.0 * h)
    B = np.zeros((3, 8))
    B[0, 0::2], B[1, 1::2] = dNdx, dNdy
    B[2, 0::2], B[2, 1::2] = dNdy, dNdx
    return B


def plane_stress_D(E: float, nu: float) -> np.ndarray:
    return E / (1 - nu * nu) * np.array([[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, 0.5 * (1 - nu)]])


def _grid2d(problem: tp.Problem) -> tp.Grid2D:
    if not isinstance(problem.grid, tp.Grid2D):
        raise TypeError("stress-constrained TO is implemented for 2-D Q4 grids")
    return problem.grid


def element_stress(problem: tp.Problem, U: np.ndarray, h: float = 1.0) -> np.ndarray:
    """(nel, 3) solid-material centroid stress σ̂ = E0 D B u_e (first load case)."""
    u = np.asarray(U).reshape(problem.grid.ndof, -1)[:, 0]
    DB = plane_stress_D(problem.E0, _grid2d(problem).nu) @ centroid_B(h)
    return u[problem.grid.edof] @ DB.T


def _vm(S: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Plane-stress von Mises and its gradient with respect to [σx, σy, τxy]."""
    sx, sy, t = S[:, 0], S[:, 1], S[:, 2]
    v = np.sqrt(np.maximum(sx * sx - sx * sy + sy * sy + 3 * t * t, 1e-300))
    dv = np.stack([(2 * sx - sy) / (2 * v), (2 * sy - sx) / (2 * v), 3 * t / v], axis=1)
    return v, dv


@cite("holmberg_2013", note="Eq. (3)-(6), stress-level clusters, adjoint of §7")
class StressConstraint:
    """Clustered P-norm stress measure and its gradient with respect to the physical densities.

    Parameters
    ----------
    problem : Problem
        Grid, load (first load case used), supports and SIMP stiffness.
    sigma_bar : float
        Stress limit, same unit as ``E0 · strain``.
    evaluate : array_like of bool
        (nel,) elements that are stress-evaluation points.
    n_clusters, p, q_s : int, float, float
        Number of clusters, P-norm exponent (8) and stress relaxation exponent (1/2).
    h : float
        Element side length (stress = E0 D B u / h for a unit-square stiffness matrix).
    """

    def __init__(self, problem: tp.Problem, sigma_bar: float, evaluate: Any, n_clusters: int = 10,
                 p: float = 8.0, q_s: float = 0.5, h: float = 1.0) -> None:
        self.pr, self.sbar, self.p, self.q_s, self.h = problem, float(sigma_bar), float(p), float(q_s), float(h)
        self.eval_idx = np.flatnonzero(np.asarray(evaluate, bool))
        self.nc = int(n_clusters)
        self.clusters: list[np.ndarray] = [self.eval_idx]
        self.DB = plane_stress_D(problem.E0, _grid2d(problem).nu) @ centroid_B(h)

    def solve(self, xphys: np.ndarray) -> tuple[Any, np.ndarray]:
        """Factorised free-DOF stiffness and the displacement field (first load case)."""
        g, pr = self.pr.grid, self.pr
        E = pr.modulus(xphys)
        K = sp.coo_matrix(((g._KEr[None, :] * E[:, None]).ravel(), (g.iK, g.jK)), shape=(g.ndof, g.ndof)).tocsc()
        K = (K + K.T) / 2
        lu = spla.splu(K[pr.free][:, pr.free].tocsc())
        U = np.zeros(g.ndof)
        U[pr.free] = lu.solve(pr.F[pr.free, 0])
        return lu, U

    def stresses(self, xphys: np.ndarray, U: np.ndarray) -> np.ndarray:
        """(nel,) relaxed von Mises η_S(ρ) σ̂^vM."""
        v, _ = _vm(U[self.pr.grid.edof] @ self.DB.T)
        return np.asarray(xphys) ** self.q_s * v

    def recluster(self, xphys: np.ndarray, U: np.ndarray) -> None:
        """Holmberg "stress level" clustering: sort descending, consecutive blocks."""
        s = self.stresses(xphys, U)[self.eval_idx]
        order = self.eval_idx[np.argsort(-s, kind="stable")]
        self.clusters = [c for c in np.array_split(order, self.nc) if c.size]

    def values(self, xphys: np.ndarray, U: np.ndarray) -> np.ndarray:
        s = self.stresses(xphys, U) / self.sbar
        return np.array([np.mean(s[c] ** self.p) ** (1.0 / self.p) for c in self.clusters])

    def gradient(self, xphys: np.ndarray, U: np.ndarray, lu: Any) -> tuple[np.ndarray, np.ndarray]:
        """Constraint values (m,) and ∂σ^PN_i/∂ρ (m, nel)."""
        pr, g = self.pr, self.pr.grid
        rho = np.asarray(xphys, float)
        ue = U[g.edof]
        v, dv = _vm(ue @ self.DB.T)
        vb = v / self.sbar
        s = rho ** self.q_s * vb
        m = len(self.clusters)
        vals = np.zeros(m)
        explicit = np.zeros((m, g.nel))
        rhs = np.zeros((g.ndof, m))
        for i, c in enumerate(self.clusters):
            A = float(np.mean(s[c] ** self.p))
            if A <= 1e-300:                                                    # an unstressed cluster: no gradient
                continue
            vals[i] = A ** (1.0 / self.p)
            k = A ** (1.0 / self.p - 1.0) / c.size                           # ∂PN/∂s_a = k s_a^(p−1)
            # explicit: k s^(p−1) q_s ρ^(q_s−1) v/σ̄ = k q_s ρ^(q_s p − 1) (v/σ̄)^p (finite at ρ = 0 for q_s p ≥ 1)
            explicit[i, c] = k * self.q_s * rho[c] ** (self.q_s * self.p - 1.0) * vb[c] ** self.p
            w = k * s[c] ** (self.p - 1.0) * rho[c] ** self.q_s / self.sbar   # ∂PN/∂v̂_a
            fe = (w[:, None] * dv[c]) @ self.DB                                # (|c|, 8) = ∂PN/∂u_e
            np.add.at(rhs[:, i], g.edof[c].ravel(), fe.ravel())
        lam = np.zeros((g.ndof, m))
        lam[pr.free] = lu.solve(rhs[pr.free])
        le = lam[g.edof]                                                       # (nel, 8, m)
        kel = np.einsum("eam,ab,eb->me", le, g.KE, ue)
        dK = pr.penalty * (pr.E0 - pr.Emin) * rho ** (pr.penalty - 1.0)
        return vals, explicit - kel * dK[None, :]


@cite("svanberg_1987", note="MMA approximations as in topology.mma_subproblem; dual solved with L-BFGS-B")
def mma_multi(x: np.ndarray, xmin: np.ndarray, xmax: np.ndarray, low: np.ndarray, upp: np.ndarray,
              df0: np.ndarray, g: np.ndarray, dg: np.ndarray, move: float = 0.1, albefa: float = 0.1,
              raa0: float = 1e-5, c: float = 1000.0, d: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """MMA subproblem with m constraints g_i ≤ 0 (rows of ``dg``); returns the new design and the multipliers."""
    dx = np.maximum(xmax - xmin, 1e-5)
    alpha = np.maximum(np.maximum(low + albefa * (x - low), x - move * (xmax - xmin)), xmin)
    beta = np.minimum(np.minimum(upp - albefa * (upp - x), x + move * (xmax - xmin)), xmax)
    ux, xl = upp - x, x - low

    def pq(df: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        p_, q_ = np.maximum(df, 0.0), np.maximum(-df, 0.0)
        e = 0.001 * (p_ + q_) + raa0 / dx
        return (p_ + e) * ux ** 2, (q_ + e) * xl ** 2

    p0, q0 = pq(df0)
    pi, qi = pq(np.atleast_2d(dg))
    b = np.sum(pi / ux + qi / xl, axis=1) - np.atleast_1d(g)

    def x_of(lam: np.ndarray) -> np.ndarray:
        P, Q = p0 + lam @ pi, q0 + lam @ qi
        sP, sQ = np.sqrt(P), np.sqrt(Q)
        return np.clip((low * sP + upp * sQ) / (sP + sQ), alpha, beta)

    def neg_dual(lam: np.ndarray) -> tuple[float, np.ndarray]:
        xx = x_of(lam)
        gi = np.sum(pi / (upp - xx) + qi / (xx - low), axis=1) - b
        y = np.maximum(0.0, (lam - c) / d)
        W = float(np.sum(p0 / (upp - xx) + q0 / (xx - low)) + lam @ (gi - y) + np.sum(c * y + 0.5 * d * y * y))
        return -W, -(gi - y)

    m = pi.shape[0]
    res = so.minimize(neg_dual, np.zeros(m), jac=True, method="L-BFGS-B", bounds=[(0.0, None)] * m,
                      options={"maxiter": 500, "ftol": 1e-15, "gtol": 1e-12})
    return x_of(res.x), res.x


@cite("holmberg_2013", note="problem (P1): minimum mass, clustered stress constraints")
def topopt_stress(problem: tp.Problem, sigma_bar: float, rmin: float = 1.5, evaluate: Any = None,
                  n_clusters: int = 10, p: float = 8.0, q_s: float = 0.5, h: float = 1.0, x0: float = 0.5,
                  move: float = 0.1, max_iter: int = 400, tol: float = 0.002, recluster_every: int = 1,
                  verbose: bool = False) -> dict[str, Any]:
    """Minimise the mass fraction of the free elements subject to σ_i^PN ≤ 1 for every cluster.

    ``evaluate`` defaults to the free (non-passive) elements. Returns the physical design ``xfiz``, the histories
    ``mass`` and ``max_constraint``, and for the final design: ``mass_fraction`` (mean ρ over free elements),
    ``max_stress_ratio`` (max relaxed σ^vM/σ̄ over evaluation points), ``share_over_limit`` (evaluation points with
    ρ > 0.5 and relaxed σ^vM > σ̄), ``compliance``, ``constraints`` and ``iteration``.
    """
    grid, nel = problem.grid, problem.grid.nel
    passive = problem.passive
    free = np.flatnonzero(passive == 0)
    if evaluate is None:
        evaluate = passive == 0
    dens = tp.Density(grid, rmin, 2, passive)
    sc = StressConstraint(problem, sigma_bar, evaluate, n_clusters, p, q_s, h)
    x = np.full(nel, float(x0))
    x[passive == 1], x[passive == 2] = 0.0, 1.0
    xa = x[free]
    xold1 = xold2 = xa.copy()
    low = upp = None
    lo_, hi_ = np.zeros_like(xa), np.ones_like(xa)
    mass_hist: list[float] = []
    gmax_hist: list[float] = []
    k = 0
    change = 1.0
    while k < max_iter:
        k += 1
        xphys = dens.physical(x)
        lu, U = sc.solve(xphys)
        if k == 1 or (recluster_every and (k - 1) % recluster_every == 0):
            sc.recluster(xphys, U)
        gv, dg_rho = sc.gradient(xphys, U, lu)
        f0 = float(xphys[free].mean())
        df0 = dens.chain_rule(x, np.where(passive == 0, 1.0 / free.size, 0.0))[free]
        dg = np.array([dens.chain_rule(x, row)[free] for row in dg_rho])
        mass_hist.append(f0)
        gmax_hist.append(float(gv.max()))
        if verbose and (k % 20 == 0 or k == 1):
            print(f"it {k:4d}  mass {f0:.4f}  max PN {gv.max():.4f}  change {change:.4f}", flush=True)
        low, upp = tp.mma_asymptote(k, xa, xold1, xold2, low, upp, lo_, hi_)
        xa_new, _ = mma_multi(xa, lo_, hi_, low, upp, df0, gv - 1.0, dg, move=move)
        xold2, xold1 = xold1, xa.copy()
        change = float(np.max(np.abs(xa_new - xa)))
        xa = xa_new
        x[free] = xa
        if change < tol and gv.max() <= 1.0 + 1e-3:
            break
    xphys = dens.physical(x)
    lu, U = sc.solve(xphys)
    sc.recluster(xphys, U)
    s = sc.stresses(xphys, U)[sc.eval_idx] / sc.sbar
    solid = xphys[sc.eval_idx] > 0.5
    return {"x": grid.to_array(x), "xfiz": grid.to_array(xphys), "mass": np.array(mass_hist),
            "max_constraint": np.array(gmax_hist), "mass_fraction": float(xphys[free].mean()),
            "max_stress_ratio": float(s.max()), "share_over_limit": float(np.mean(s[solid] > 1.0)) if solid.any()
            else 0.0, "compliance": float(problem.F[:, 0] @ U), "constraints": sc.values(xphys, U),
            "iteration": k, "U": U}


@cite("holmberg_2013", note="§9.1 and Fig. 3-4: L = 200 mm, 2L/5 arms, 1500 N, 3x2 load elements fixed solid")
def holmberg_l_beam(n: int = 100, L: float = 200.0, force: float = 1500.0, E: float = 71000.0,
                    nu: float = 0.33) -> tuple[tp.Problem, np.ndarray, float]:
    """Holmberg's L-beam on an n × n grid (n = 100 gives their 6400 elements in the L).

    Returns the problem (forces in N, E in MPa, unit thickness), the stress-evaluation mask (free elements) and the
    element size h in mm. The 3 × 2 elements under the load (top-right corner of the horizontal arm) are fixed solid.
    """
    base = tp.l_bracket(n, P=force, ratio=0.4, nu=nu, E0=E, Emin=E * 1e-9)
    grid = _grid2d(base)
    m = grid.element_center()
    arm = int(round(0.4 * n))
    passive = base.passive.copy()
    under = (m[:, 0] > n - 3) & (m[:, 1] < arm) & (m[:, 1] > arm - 2)
    passive[under] = 2
    pr = tp.Problem(grid, base.F, base.fixed, passive=passive, penalty=3.0, E0=E, Emin=E * 1e-9)
    return pr, passive == 0, L / n
