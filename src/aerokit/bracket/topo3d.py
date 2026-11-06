"""SIMP topology optimisation on the voxel design domain of a bracket (3-D, several load cases).

Problem (Bendsøe 1989; Andreassen et al. 2011 for the discretisation, Liu & Tovar 2014 for 3-D)::

    min  Σ_c w_c F_cᵀ U_c        K(x̄) U_c = F_c,   Σ_e x̄_e ≤ V* n_e,   0 ≤ x ≤ 1

* modified SIMP ``E_e = E_min + x̄_e^p (E0 − E_min)``;
* density filter with a linear cone of radius ``rmin`` voxels (Bourdin 2001; Bruns & Tortorelli 2001) built on the
  solid voxels only (voids and holes have no design variable);
* optional layer-by-layer AM overhang filter (Langelaar 2017, 3-D form: an element can be no denser than the
  smooth maximum of the five elements below it — centre and four face neighbours — so overhangs steeper than 45°
  from the build plate are suppressed);
* smoothed Heaviside projection ``tanh`` with threshold η and β continuation (Wang, Lazarov & Sigmund 2011 form as
  used by Ferrari & Sigmund 2020);
* optimality-criteria update with bisection on the volume multiplier (top88/top3d);
* non-design ("keep") elements are fixed solid in x̄: bolt and lug rings, as the "exclusion regions" of Ansys.

Ansys Mechanical 2025 R1 calls its default topology method "Mixable Density" (docs/16); its internals are not
public, so this module reproduces the standard density-based SIMP formulation that it belongs to, not the code.
"""
from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from aerokit.bracket.voxfem import ReducedUpper, VoxelMesh, _rigid_body_modes, ke_unit, pardiso_module
from aerokit.optimization.projection import project, project_dx
from aerokit.references import cite

__all__ = ["density_filter", "AMFilter3D", "TopoResult", "optimize", "optimize_stress", "to_grid", "mirror_groups"]


@cite("bourdin_2001", "bruns_tortorelli_2001", "andreassen_2011", note="cone filter on the solid voxels")
def density_filter(mesh: VoxelMesh, rmin: float) -> tuple[sp.csr_matrix, np.ndarray]:
    """Filter matrix H (ne, ne) with ``H_ei = max(0, rmin − dist)`` (in voxels) and its row sums."""
    if not rmin > 0:
        raise ValueError("rmin > 0 is required")
    r = math.ceil(rmin) - 1
    rows, cols, w = [], [], []
    shape = np.array(mesh.solid.shape)
    e1 = np.arange(mesh.ne)
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            for dz in range(-r, r + 1):
                wt = rmin - math.sqrt(dx * dx + dy * dy + dz * dz)
                if wt <= 0:
                    continue
                k = mesh.ijk + (dx, dy, dz)
                ok = np.all((k >= 0) & (k < shape), axis=1)
                j = np.full(mesh.ne, -1)
                j[ok] = mesh.element_of[tuple(k[ok].T)]
                ok &= j >= 0
                rows.append(e1[ok])
                cols.append(j[ok])
                w.append(np.full(ok.sum(), wt))
    H = sp.csr_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(mesh.ne, mesh.ne))
    return H, np.asarray(H.sum(axis=1)).ravel()


class AMFilter3D:
    """Langelaar (2017) layer-wise AM filter on the voxel grid, build direction ``axis`` (0, 1, 2) and ``sign``.

    The lowest layer of the grid (in the build direction) is the build plate and is printed as designed.
    Grid cells without an element count as void (0) when they support a layer above.
    """

    def __init__(self, mesh: VoxelMesh, axis: int = 2, sign: int = 1, P: float = 40.0, eps: float = 1e-4,
                 xi0: float = 0.5) -> None:
        self.mesh, self.axis, self.sign = mesh, axis, sign
        self.P, self.eps, self.xi0 = P, eps, xi0
        self._cache: list[tuple[np.ndarray, np.ndarray, np.ndarray]] = []

    def _grid(self, v: np.ndarray) -> np.ndarray:
        g = np.zeros(self.mesh.solid.shape)
        g[tuple(self.mesh.ijk.T)] = v
        g = np.moveaxis(g, self.axis, 0)
        return g[::-1] if self.sign < 0 else g          # layer 0 = build plate

    def _ungrid(self, g: np.ndarray) -> np.ndarray:
        g = g[::-1] if self.sign < 0 else g
        g = np.moveaxis(g, 0, self.axis)
        return g[tuple(self.mesh.ijk.T)]

    @staticmethod
    def _stencil_sum(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Sum over the 5-point support stencil (centre + 4 face neighbours) and the stencil size."""
        s = a.copy()
        n = np.ones_like(a)
        for ax in (0, 1):
            for sh in (1, -1):
                r = np.roll(a, sh, axis=ax)
                m = np.ones_like(a)
                idx: list[Any] = [slice(None)] * 2
                idx[ax] = 0 if sh == 1 else -1
                r[tuple(idx)] = 0.0
                m[tuple(idx)] = 0.0
                s += r
                n += m
        return s, n

    @cite("langelaar_2017", note="Eq. (3)-(8), 3-D five-element support region")
    def forward(self, x: np.ndarray) -> np.ndarray:
        a = self._grid(x)
        xi = np.empty_like(a)
        xi[0] = a[0]
        self._cache = []
        for k in range(1, a.shape[0]):
            s, n = self._stencil_sum(xi[k - 1] ** self.P)
            q = self.P + np.log(n) / math.log(self.xi0)
            Xi = np.power(np.maximum(s, 1e-300), 1.0 / q)
            d = a[k] - Xi
            root = np.sqrt(d * d + self.eps)
            xi[k] = 0.5 * (a[k] + Xi - root + math.sqrt(self.eps))
            self._cache.append((s, q, d / root))
        return self._ungrid(xi)

    def backward(self, x: np.ndarray, dxi: np.ndarray) -> np.ndarray:
        """Adjoint: ∂f/∂x from ∂f/∂ξ (after :meth:`forward` on the same x)."""
        a = self._grid(x)
        lam = self._grid(dxi)
        xi = self._grid(self.forward(x))
        dx = np.zeros_like(a)
        for k in range(a.shape[0] - 1, 0, -1):
            s, q, t = self._cache[k - 1]
            dx[k] = lam[k] * 0.5 * (1 - t)
            g = lam[k] * 0.5 * (1 + t) * (1.0 / q) * np.power(np.maximum(s, 1e-300), 1.0 / q - 1.0)
            # Xi = (Σ_stencil xi_below^P)^(1/q): ∂Xi/∂xi_j = g' P xi_j^(P-1), stencil is symmetric → same shifts
            gs, _ = self._stencil_sum(g)
            lam[k - 1] += gs * self.P * xi[k - 1] ** (self.P - 1)
        dx[0] = lam[0]
        return self._ungrid(dx)


def overhang_violations(mesh: VoxelMesh, xphys: np.ndarray, axis: int = 2, sign: int = 1,
                        threshold: float = 0.5) -> int:
    """Solid elements above the first layer with none of the five support cells below solid."""
    f = AMFilter3D(mesh, axis, sign)
    g = f._grid((xphys > threshold).astype(float)) > 0.5
    s, _ = AMFilter3D._stencil_sum(g[:-1].astype(float))
    return int((g[1:] & (s < 0.5)).sum())


class _Solver:
    """PCG with a smoothed-aggregation AMG preconditioner rebuilt every ``rebuild`` calls (an older hierarchy is
    still a valid SPD preconditioner); sparse direct below ``direct_limit`` free DOFs."""

    def __init__(self, mesh: VoxelMesh, fixed: np.ndarray, rebuild: int = 4, direct_limit: int = 30_000,
                 tol: float = 1e-8) -> None:
        self.free = np.setdiff1d(np.arange(mesh.ndof), fixed)
        self.mesh, self.rebuild, self.tol = mesh, rebuild, tol
        self.pardiso = pardiso_module() is not None
        self.reduced = ReducedUpper(mesh, fixed) if self.pardiso else None
        self.direct = len(self.free) <= direct_limit
        self.calls = 0
        self.M: Any = None
        self.cg_iters: list[int] = []
        try:
            import pyamg  # noqa: F401
            self.amg = True
        except ImportError:
            self.amg = False
        self.B = _rigid_body_modes(mesh.X)[self.free]

    def __call__(self, K: sp.csr_matrix | None, F: np.ndarray, U0: np.ndarray | None,
                 KE: np.ndarray | None = None, scale: np.ndarray | None = None) -> np.ndarray:
        if self.reduced is not None and KE is not None and scale is not None:
            return self.reduced.solve(KE, scale, F)
        if K is None:
            if KE is None or scale is None:
                raise ValueError("pass K or (KE, scale)")
            K = self.mesh.stiffness(KE, scale)
        Kf = K[self.free][:, self.free].tocsr()
        U = np.zeros_like(F)
        if self.direct:
            U[self.free] = spla.splu(Kf.tocsc(), permc_spec="MMD_AT_PLUS_A").solve(F[self.free])
            return U
        if self.M is None or self.calls % self.rebuild == 0:
            if self.amg:
                import pyamg
                ml = pyamg.smoothed_aggregation_solver(Kf, B=self.B, symmetry="hermitian", max_coarse=500)
                self.M = ml.aspreconditioner(cycle="V")
            else:
                d = Kf.diagonal()
                self.M = sp.diags(1.0 / d)
        self.calls += 1
        it = 0
        for c in range(F.shape[1]):
            n = [0]

            def cb(_: np.ndarray, n: list[int] = n) -> None:
                n[0] += 1
            x0 = U0[self.free, c] if U0 is not None else None
            u, flag = spla.cg(Kf, F[self.free, c], x0=x0, rtol=self.tol, atol=0.0, maxiter=3000, M=self.M,
                              callback=cb)
            if flag != 0:                                   # stale preconditioner: rebuild once and retry
                import pyamg
                ml = pyamg.smoothed_aggregation_solver(Kf, B=self.B, symmetry="hermitian", max_coarse=500)
                self.M = ml.aspreconditioner(cycle="V")
                u, flag = spla.cg(Kf, F[self.free, c], x0=x0, rtol=self.tol, atol=0.0, maxiter=5000, M=self.M,
                                  callback=cb)
                if flag != 0:
                    raise RuntimeError("PCG did not converge in the topology loop")
            U[self.free, c] = u
            it += n[0]
        self.cg_iters.append(it)
        return U


@dataclass
class TopoResult:
    """Outcome of :func:`optimize` (element vectors on the mesh's solid voxels)."""

    x: np.ndarray
    xphys: np.ndarray
    compliance: list[float]
    volume: list[float]
    change: list[float]
    beta: list[float]
    iterations: int
    converged: bool
    seconds: float
    compliance_cases: np.ndarray
    U: np.ndarray
    settings: dict[str, Any] = field(default_factory=dict)
    snapshots: list[tuple[int, np.ndarray]] = field(default_factory=list)   # (iteration, xphys float16)

    @property
    def volume_fraction(self) -> float:
        return float(self.xphys.mean())

    def gray(self) -> float:
        """Measure of non-discreteness M_nd [%] (Sigmund 2007)."""
        return float(100 * np.mean(4 * self.xphys * (1 - self.xphys)))


@cite("bendsoe_1989", "andreassen_2011", "liu_tovar_2014", "ferrari_sigmund_2020",
      note="SIMP + density filter + tanh projection + OC")
def optimize(mesh: VoxelMesh, F: np.ndarray, fixed: np.ndarray, volfrac: float, *, E0: float = 1.0, nu: float = 0.3,
             keep: np.ndarray | None = None, void: np.ndarray | None = None, rmin: float = 1.5,
             penal: float = 3.0, emin_ratio: float = 1e-6, projection: bool = True, eta: float = 0.5,
             beta0: float = 1.0, beta_max: float = 16.0, beta_every: int = 25, move: float = 0.2,
             max_iter: int = 100, tol: float = 0.01, am_axis: int | None = None, am_sign: int = 1,
             weights: np.ndarray | None = None, element: str = "H8", x0: np.ndarray | None = None,
             callback: Callable[[int, float, float], None] | None = None,
             solver_kw: dict[str, Any] | None = None, snapshot_every: int = 0,
             sym: np.ndarray | None = None) -> TopoResult:
    """Compliance minimisation with a volume bound ``volfrac`` (fraction of the solid voxels kept).

    ``sym`` (ne, G) int: symmetry groups (column 0 = the element itself, −1 = mirror cell not in the domain). The
    design variables of a group are tied (pattern grouping, as Altair OptiStruct / COMSOL mirror symmetry): the
    start design, the filtered sensitivities and every OC update are averaged over the group, so a symmetric
    problem cannot drift into a non-symmetric local optimum (5 Nov: the official layouts had one full and one
    nearly empty lug although loads and supports are mirror-symmetric).

    ``F`` (ndof, n_cases) [N]; ``E0`` [Pa] scales the compliance only (the layout does not depend on it).
    ``keep``/``void`` (ne,) bool force elements solid/void. ``am_axis`` switches the overhang filter on.
    ``snapshot_every`` > 0 keeps the physical density of every k-th iteration (and the last) in ``snapshots``.
    """
    t0 = time.perf_counter()
    if sym is not None:
        sym = np.asarray(sym, int)
        _sm = sym >= 0
        _sidx = np.where(_sm, sym, 0)
        _scnt = _sm.sum(1)

        def S(v: np.ndarray) -> np.ndarray:
            return (v[_sidx] * _sm).sum(1) / _scnt
    else:
        def S(v: np.ndarray) -> np.ndarray:
            return v
    if not 0 < volfrac <= 1:
        raise ValueError("0 < volfrac <= 1 is required")
    ne = mesh.ne
    keep = np.zeros(ne, bool) if keep is None else np.asarray(keep, bool)
    void = np.zeros(ne, bool) if void is None else np.asarray(void, bool) & ~keep
    free_e = ~keep & ~void
    if keep.mean() > volfrac:
        raise ValueError(f"non-design regions already fill {keep.mean():.3f} > volfrac {volfrac}")
    F = np.asarray(F, float)
    F = F[:, None] if F.ndim == 1 else F
    w = np.ones(F.shape[1]) if weights is None else np.asarray(weights, float)
    KE, _ = ke_unit(nu, element)
    frac = np.asarray(mesh.frac, float)
    Emin = emin_ratio * E0
    H, Hs = density_filter(mesh, rmin)
    Ht = H.T.tocsr()
    am = AMFilter3D(mesh, am_axis, am_sign) if am_axis is not None else None
    solver = _Solver(mesh, fixed, **(solver_kw or {}))

    def physical(x: np.ndarray, beta: float) -> np.ndarray:
        xt = (H @ x) / Hs
        if am is not None:
            xt = am.forward(xt)
        xp = project(xt, beta, eta) if projection else xt
        xp = np.where(keep, 1.0, np.where(void, 0.0, xp))
        return xp

    def chain(x: np.ndarray, d: np.ndarray, beta: float) -> np.ndarray:
        d = np.where(free_e, d, 0.0)
        xt = (H @ x) / Hs
        if am is not None:
            xa = am.forward(xt)
            if projection:
                d = d * project_dx(xa, beta, eta)
            d = am.backward(xt, d)
        elif projection:
            d = d * project_dx(xt, beta, eta)
        return Ht @ (d / Hs)

    if x0 is None:
        n_keep = keep.sum()
        start = (volfrac * ne - n_keep) / max(free_e.sum(), 1)
        x = np.where(keep, 1.0, np.where(void, 0.0, min(max(start, 0.0), 1.0)))
    else:
        x = np.asarray(x0, float).copy()
    x = np.where(keep, 1.0, np.where(void, 0.0, S(x)))
    beta = beta0 if projection else 1.0
    hist: dict[str, list[float]] = {"c": [], "v": [], "ch": [], "b": []}
    U = None
    loop = lb = 0
    change = 1.0
    cc = np.zeros(F.shape[1])
    snaps: list[tuple[int, np.ndarray]] = []
    while loop < max_iter:
        loop += 1
        lb += 1
        xp = physical(x, beta)
        Ee = (Emin + xp ** penal * (E0 - Emin)) * frac
        U = solver(None, F, U, KE, Ee * mesh.h)
        Ue = U[mesh.edof]                                                  # (ne, 24, nc)
        ce = np.einsum("eac,ab,ebc->ec", Ue, KE, Ue) * mesh.h               # per unit E
        cc = np.einsum("ec,e->c", ce, Ee)
        c = float(w @ cc)
        dc = -penal * (E0 - Emin) * frac * xp ** (penal - 1) * (ce @ w)
        dcx = S(chain(x, dc, beta))
        dvx = S(chain(x, np.ones(ne), beta))
        hist["c"].append(c)
        hist["v"].append(float(xp.mean()))
        hist["b"].append(beta)
        # OC with bisection on the volume of the physical field
        l1, l2 = 0.0, 1e9
        xl, xu = np.maximum(0.0, x - move), np.minimum(1.0, x + move)
        ratio = np.sqrt(np.maximum(-dcx, 0.0) / np.maximum(dvx, 1e-30))
        xnew = x
        for _ in range(80):
            lm = 0.5 * (l1 + l2)
            xnew = S(np.clip(x * ratio / math.sqrt(lm), xl, xu))
            xnew = np.where(keep, 1.0, np.where(void, 0.0, xnew))
            if physical(xnew, beta).sum() > volfrac * ne:
                l1 = lm
            else:
                l2 = lm
            if (l2 - l1) / (l1 + l2 + 1e-30) < 1e-4:
                break
        change = float(np.max(np.abs(xnew - x)))
        x = xnew
        hist["ch"].append(change)
        if snapshot_every and loop % snapshot_every == 0:
            snaps.append((loop, xp.astype(np.float16)))
        if callback:
            callback(loop, c, float(xp.mean()))
        if projection and beta < beta_max and (lb >= beta_every or change <= tol):
            beta = min(2 * beta, beta_max)
            lb = 0
            continue
        if change <= tol and (not projection or beta >= beta_max):
            break
    xp = physical(x, beta)
    return TopoResult(x, xp, hist["c"], hist["v"], hist["ch"], hist["b"], loop,
                      change <= tol, time.perf_counter() - t0, cc, U if U is not None else np.zeros_like(F),
                      {"volfrac": volfrac, "rmin": rmin, "penal": penal, "emin_ratio": emin_ratio,
                       "projection": projection, "eta": eta, "beta_max": beta_max, "move": move,
                       "am_axis": am_axis, "am_sign": am_sign, "element": element, "solver": "pardiso" if solver.pardiso
                       else ("direct" if solver.direct else ("amg-pcg" if solver.amg else "jacobi-pcg")),
                       "cg_iterations": solver.cg_iters, "symmetry_groups": None if sym is None else int(sym.shape[1])},
                      snaps + ([(loop, xp.astype(np.float16))] if snapshot_every and (not snaps or snaps[-1][0] != loop)
                               else []))


_VM = np.array([[1.0, -0.5, -0.5, 0, 0, 0], [-0.5, 1.0, -0.5, 0, 0, 0], [-0.5, -0.5, 1.0, 0, 0, 0],
                [0, 0, 0, 3.0, 0, 0], [0, 0, 0, 0, 3.0, 0], [0, 0, 0, 0, 0, 3.0]])
"""von Mises quadratic form: σ_vm² = σᵀ V σ (Voigt order of :mod:`voxfem`)."""


def stress_pnorm(mesh: VoxelMesh, xp: np.ndarray, F: np.ndarray, fixed: np.ndarray, sigma_bar: float,
                 evaluate: np.ndarray, *, penal: float = 3.0, q: float = 0.5, P: float = 8.0, emin_ratio: float = 1e-6,
                 nu: float = 0.3, element: str = "H8IM", solver: Any = None
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray, Any]:
    """P-norm of the relaxed stress ratio x̄^q σ_vm/σ̄ over ``evaluate`` for every load case, its gradient with
    respect to the physical densities (adjoint method) and the true maximum ratio.

    Returns ``(pn (nc,), dpn (nc, ne), max_ratio (nc,), U)``. Stress at the element centroid with E = 1 (stress does
    not depend on E for a homogeneous part).
    """
    from aerokit.bracket.voxfem import _stress_ops
    F = np.asarray(F, float)
    F = F[:, None] if F.ndim == 1 else F
    nc, ne = F.shape[1], mesh.ne
    KE, _ = ke_unit(nu, element)
    S0 = _stress_ops(nu, element).S0
    frac = np.asarray(mesh.frac, float)
    solver = solver or _Solver(mesh, fixed)
    Ee = (emin_ratio + xp ** penal * (1.0 - emin_ratio)) * frac
    U = solver(None, F, None, KE, Ee * mesh.h)
    pn = np.zeros(nc)
    mx = np.zeros(nc)
    d_expl = np.zeros((nc, ne))
    rhs = np.zeros((mesh.ndof, nc))
    xq = np.maximum(xp, 1e-9) ** q
    for c in range(nc):
        ue = U[mesh.edof, c]
        sig = ue @ S0.T / mesh.h
        vm = np.sqrt(np.maximum(np.einsum("ei,ij,ej->e", sig, _VM, sig), 1e-30))
        sr = xq * vm / sigma_bar
        se = sr[evaluate]
        pn[c] = float(np.sum(se ** P) ** (1.0 / P))
        mx[c] = float(se.max())
        dpn_ds = np.zeros(ne)
        dpn_ds[evaluate] = pn[c] ** (1 - P) * se ** (P - 1)
        d_expl[c] = dpn_ds * q * np.maximum(xp, 1e-9) ** (q - 1) * vm / sigma_bar
        w = dpn_ds * xq / sigma_bar / vm
        dsu = (w[:, None] * (sig @ _VM)) @ S0 / mesh.h
        np.add.at(rhs[:, c], mesh.edof.ravel(), dsu.ravel())
    lam = solver(None, rhs, None, KE, Ee * mesh.h)
    dK = penal * xp ** (penal - 1) * (1.0 - emin_ratio) * frac * mesh.h
    dpn = np.zeros((nc, ne))
    for c in range(nc):
        dpn[c] = d_expl[c] - dK * np.einsum("ea,ab,eb->e", lam[mesh.edof, c], KE, U[mesh.edof, c])
    return pn, dpn, mx, U


@cite("holmberg_2013", "le_norato_2010", "svanberg_1987",
      note="min volume s.t. P-norm of qp-relaxed von Mises per load case, adaptive normalisation, adjoint, MMA")
def optimize_stress(mesh: VoxelMesh, F: np.ndarray, fixed: np.ndarray, sigma_bar: float, *,
                    evaluate: np.ndarray | None = None, keep: np.ndarray | None = None, rmin: float = 2.0,
                    penal: float = 3.0, q: float = 0.5, P: float = 8.0, emin_ratio: float = 1e-6, nu: float = 0.3,
                    x0: np.ndarray | float = 0.5, move: float = 0.05, max_iter: int = 80, tol: float = 0.005,
                    element: str = "H8IM", callback: Callable[[int, float, float], None] | None = None,
                    solver_kw: dict[str, Any] | None = None) -> dict[str, Any]:
    """EXPERIMENTAL — minimum volume fraction subject to ``max_e x̄_e^q σ_vm,e ≤ σ̄`` per load case (``F`` in N).

    The maximum is approximated by a P-norm over the ``evaluate`` elements (default: not ``keep``) with the adaptive
    normalisation of Le et al. (rescaled every iteration to the true maximum; the scale is held constant in the
    sensitivities). Density filter, MMA (one constraint per load case). Gradients are checked against finite
    differences (``stress_pnorm``), but on 4 Nov 2026 a 100-iteration test cantilever ended 73 % grey (no
    projection or continuation yet): NOT used by the pipeline, which uses compliance layouts + a stress-aware volume
    search + T10 verification instead.
    """
    from aerokit.optimization.stress_topo import mma_multi
    from aerokit.optimization.topology import mma_asymptote

    t0 = time.perf_counter()
    ne = mesh.ne
    keep = np.zeros(ne, bool) if keep is None else np.asarray(keep, bool)
    ev = (~keep) if evaluate is None else np.asarray(evaluate, bool)
    free = ~keep
    H, Hs = density_filter(mesh, rmin)
    Ht = H.T.tocsr()
    solver = _Solver(mesh, fixed, **(solver_kw or {}))
    x = np.where(keep, 1.0, np.broadcast_to(np.asarray(x0, float), (ne,)))
    xa = x[free].copy()
    xold1 = xold2 = xa.copy()
    low = upp = None
    lo_, hi_ = np.full_like(xa, 1e-3), np.ones_like(xa)
    hist: dict[str, list[float]] = {"volume": [], "gmax": []}
    k = 0
    change = 1.0
    mx = np.zeros(1)
    U = None
    while k < max_iter:
        k += 1
        xp = np.where(keep, 1.0, (H @ x) / Hs)
        pn, dpn, mx, U = stress_pnorm(mesh, xp, F, fixed, sigma_bar, ev, penal=penal, q=q, P=P,
                                      emin_ratio=emin_ratio, nu=nu, element=element, solver=solver)
        cn = mx / pn                                              # adaptive normalisation (Le et al.)
        g = cn * pn - 1.0
        dgx = np.array([(Ht @ (np.where(keep, 0.0, cn[c] * dpn[c]) / Hs))[free] for c in range(len(pn))])
        f0 = float(xp.mean())
        df0 = (Ht @ (np.where(keep, 0.0, np.full(ne, 1.0 / ne)) / Hs))[free]
        hist["volume"].append(f0)
        hist["gmax"].append(float(mx.max()))
        if callback:
            callback(k, f0, float(mx.max()))
        low, upp = mma_asymptote(k, xa, xold1, xold2, low, upp, lo_, hi_, 0.5, 0.7, 1.2)
        xa_new, _ = mma_multi(xa, lo_, hi_, low, upp, df0 / max(f0, 1e-9), g, dgx, move=move)
        xold2, xold1 = xold1, xa.copy()
        change = float(np.max(np.abs(xa_new - xa)))
        xa = xa_new
        x[free] = xa
        if change < tol and mx.max() <= 1.0 + 1e-3:
            break
    xp = np.where(keep, 1.0, (H @ x) / Hs)
    return {"xphys": xp, "x": x, "volume_fraction": float(xp.mean()), "max_relaxed_stress_ratio": mx.tolist(),
            "volume_history": hist["volume"], "stress_history": hist["gmax"], "iterations": k,
            "converged": change < tol, "seconds": time.perf_counter() - t0, "U": U,
            "settings": {"sigma_bar": sigma_bar, "P": P, "q": q, "rmin": rmin, "penal": penal, "move": move}}


def mirror_groups(mesh: VoxelMesh, planes_mm: dict[str, float]) -> np.ndarray:
    """(ne, 2^k) element groups for mirror planes {axis: coordinate in mm}, e.g. {"x": 500.0, "y": 200.28}: the
    mirror cell of every element is the voxel nearest to its reflected centre (−1 if that voxel is not solid)."""
    ax = [("xyz".index(a), c * 1e-3) for a, c in planes_mm.items()]
    shape = np.array(mesh.solid.shape)
    o, h = np.asarray(mesh.origin, float), mesh.h
    cols = [np.arange(mesh.ne)]
    for k, c in ax:
        new = []
        for col in cols:
            ijk = mesh.ijk[np.maximum(col, 0)].copy()
            xc = o[k] + (ijk[:, k] + 0.5) * h
            ijk[:, k] = np.rint((2 * c - xc - o[k]) / h - 0.5).astype(int)
            ok = (col >= 0) & (ijk[:, k] >= 0) & (ijk[:, k] < shape[k])
            j = np.full(mesh.ne, -1)
            j[ok] = mesh.element_of[tuple(ijk[ok].T)]
            new.append(j)
        cols += new
    return np.stack(cols, axis=1)


def to_grid(mesh: VoxelMesh, v: np.ndarray, fill: float = 0.0) -> np.ndarray:
    """Element vector → (nx, ny, nz) array on the voxel grid (``fill`` outside the solid)."""
    g = np.full(mesh.solid.shape, fill, dtype=float)
    g[tuple(mesh.ijk.T)] = v
    return g
