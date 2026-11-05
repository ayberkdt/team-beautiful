"""3-D linear static finite elements on a voxel model (cubic H8 bricks), SI units.

The bracket is described by a boolean voxel mask (``solid[i, j, k]``) with cube edge ``h`` [m] and the corner of
voxel (0, 0, 0) at ``origin`` [m]. Only solid voxels become elements, so holes and the space around the part carry
no degrees of freedom.

Elements
--------
``"H8"``
    Trilinear brick, 2×2×2 Gauss integration — the element of top3d (Liu & Tovar 2014) and of
    :func:`aerokit.optimization.topology.ke_h8`. Locks in bending when a member is one or two voxels thick.
``"H8IM"``
    The same brick with the nine Wilson incompatible modes ``1 − ξ², 1 − η², 1 − ζ²`` per displacement
    component, condensed statically (Taylor, Beresford & Wilson 1976; Cook et al. 2002 §6.7).
    Every element is the same cube, so the Jacobian is constant and the element passes the patch test without
    Taylor's correction. It removes most of the bending stiffening of H8; Ansys' SOLID185 offers the same
    family as its "enhanced strain" option.

Stresses: element-centroid stress (exact for both elements: the incompatible-mode derivatives vanish at the
centroid) and averaged nodal stress, extrapolated from the 2×2×2 Gauss points and averaged component-wise over the
elements sharing a node before the von Mises value is formed (the Ansys "averaged" nodal result convention).

Solver ("auto"): Intel MKL PARDISO (pypardiso, symmetric positive definite mode, threaded) when it can be loaded;
else sparse direct SuperLU up to ``direct_limit`` free DOFs and above that conjugate gradients preconditioned by
smoothed-aggregation algebraic multigrid (pyamg, rigid-body near-null space), else Jacobi-preconditioned CG.
Measured on this laptop (i7-9750H), 72 540 DOF, 3 right-hand sides: PARDISO 1.8 s, AMG-PCG 6.4 s (2 RHS),
SuperLU 31 s (2 RHS). pypardiso and the MKL / Intel OpenMP DLLs live in ``D:/tmp_ideathon/pylib`` (docs/22);
``AEROKIT_MKL_BIN`` overrides the DLL folder.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from aerokit.references import cite

__all__ = ["H8_CORNER", "ke_unit", "VoxelMesh", "solve", "StaticResult", "static", "von_mises",
           "D_iso"]

H8_CORNER = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                      [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], dtype=float)
"""Natural coordinates of the corner nodes (order of :class:`aerokit.fem.elements.solid.H8`)."""

_G = 1.0 / math.sqrt(3.0)
_GAUSS = np.array([[a, b, c] for a in (-_G, _G) for b in (-_G, _G) for c in (-_G, _G)])


def D_iso(nu: float) -> np.ndarray:
    """Isotropic 3-D elasticity matrix for E = 1, Voigt order [εx, εy, εz, γyz, γxz, γxy]."""
    if not -1 < nu < 0.5:
        raise ValueError("-1 < nu < 0.5 is required")
    c = 1.0 / ((1 + nu) * (1 - 2 * nu))
    D = np.zeros((6, 6))
    D[:3, :3] = c * nu
    np.fill_diagonal(D[:3, :3], c * (1 - nu))
    D[3:, 3:] = np.eye(3) / (2 * (1 + nu))
    return D


def _B_from_grad(dN: np.ndarray) -> np.ndarray:
    """Strain matrix (6, 3n) from shape-function gradients dN (3, n)."""
    n = dN.shape[1]
    B = np.zeros((6, 3 * n))
    B[0, 0::3] = dN[0]
    B[1, 1::3] = dN[1]
    B[2, 2::3] = dN[2]
    B[3, 1::3] = dN[2]
    B[3, 2::3] = dN[1]
    B[4, 0::3] = dN[2]
    B[4, 2::3] = dN[0]
    B[5, 0::3] = dN[1]
    B[5, 1::3] = dN[0]
    return B


def _B_unit(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(B_u (6, 24), B_α (6, 9)) of the unit cube at natural point ``p`` (∂/∂x = 2 ∂/∂ξ)."""
    s = H8_CORNER
    a = 1 + s * p
    dN = 0.125 * np.vstack([s[:, 0] * a[:, 1] * a[:, 2], s[:, 1] * a[:, 0] * a[:, 2],
                            s[:, 2] * a[:, 0] * a[:, 1]]) * 2.0
    dP = np.diag(-2.0 * p * 2.0)          # mode m = 1 − ξ_m²: ∂/∂ξ_m = −2 ξ_m, × 2 for the unit cube
    return _B_from_grad(dN), _B_from_grad(dP)


@cite("taylor_beresford_wilson_1976", "cook_2002", "liu_tovar_2014",
      note="H8 (top3d) and H8 with incompatible modes, statically condensed")
def ke_unit(nu: float = 0.3, element: str = "H8") -> tuple[np.ndarray, np.ndarray | None]:
    """Stiffness (24, 24) of the unit cube for E = 1 and, for H8IM, the recovery matrix R (9, 24), α = R u.

    The physical cube of edge h and modulus E has stiffness ``E h K`` (B ∝ 1/h, volume ∝ h³).
    """
    if element not in ("H8", "H8IM"):
        raise ValueError("element must be 'H8' or 'H8IM'")
    D = D_iso(nu)
    Kuu = np.zeros((24, 24))
    Kua = np.zeros((24, 9))
    Kaa = np.zeros((9, 9))
    for p in _GAUSS:
        Bu, Ba = _B_unit(p)
        w = 0.125                                  # det J = 1/8, weight 1
        Kuu += Bu.T @ D @ Bu * w
        Kua += Bu.T @ D @ Ba * w
        Kaa += Ba.T @ D @ Ba * w
    if element == "H8":
        return Kuu, None
    R = -np.linalg.solve(Kaa, Kua.T)               # α = R u
    K = Kuu + Kua @ R
    return 0.5 * (K + K.T), R


def thermal_unit(nu: float = 0.3, element: str = "H8") -> tuple[np.ndarray, np.ndarray]:
    """Thermal load of the unit cube for E = 1 and α ΔT = 1: (f (24,), ε_modes (8 Gauss points, 6)).

    ``f = Σ_gp Bᵀ D ε₀ w`` with ε₀ = [1, 1, 1, 0, 0, 0]; for H8IM the incompatible modes are condensed
    (``f_u − K_uα K_αα⁻¹ f_α``) and ``ε_modes`` is the strain the modes add at each Gauss point when u = 0
    (``B_α K_αα⁻¹ f_α``). A cube of edge h, modulus E and strain α ΔT gets ``E α ΔT h² f``.
    """
    D = D_iso(nu)
    eps0 = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
    fu = np.zeros(24)
    fa = np.zeros(9)
    Kaa = np.zeros((9, 9))
    Kua = np.zeros((24, 9))
    Ba_g = []
    for gp in _GAUSS:
        Bu, Ba = _B_unit(gp)
        fu += Bu.T @ D @ eps0 * 0.125
        fa += Ba.T @ D @ eps0 * 0.125
        Kaa += Ba.T @ D @ Ba * 0.125
        Kua += Bu.T @ D @ Ba * 0.125
        Ba_g.append(Ba)
    if element == "H8":
        return fu, np.zeros((8, 6))
    a_th = np.linalg.solve(Kaa, fa)
    return fu - Kua @ a_th, np.array([Ba @ a_th for Ba in Ba_g])


def von_mises(s: np.ndarray) -> np.ndarray:
    """von Mises stress of Voigt stresses ``s[..., 6]`` = [σx, σy, σz, τyz, τxz, τxy]."""
    s = np.asarray(s, float)
    sx, sy, sz, tyz, txz, txy = (s[..., i] for i in range(6))
    return np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3.0 * (tyz ** 2 + txz ** 2 + txy ** 2))


@dataclass
class VoxelMesh:
    """Finite element mesh of the solid voxels of ``solid`` (nx, ny, nz) with edge ``h`` [m] at ``origin`` [m].

    Attributes
    ----------
    ijk : (ne, 3) int
        Voxel index of each element.
    conn : (ne, 8) int
        Compact node numbers (corner order :data:`H8_CORNER`).
    X : (nn, 3) float
        Node coordinates [m].
    edof : (ne, 24) int
        Element DOFs (3 per node: x, y, z).
    """

    solid: np.ndarray
    h: float
    origin: np.ndarray = field(default_factory=lambda: np.zeros(3))
    frac: np.ndarray | None = None            # (ne,) solid fraction of each element (partial volume), default 1
    ijk: np.ndarray = field(init=False)
    conn: np.ndarray = field(init=False)
    X: np.ndarray = field(init=False)
    edof: np.ndarray = field(init=False)
    grid_node: np.ndarray = field(init=False)
    element_of: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.solid = np.asarray(self.solid, bool)
        if self.solid.ndim != 3 or not self.solid.any():
            raise ValueError("solid must be a non-empty 3-D boolean array")
        if not self.h > 0:
            raise ValueError("h > 0 is required")
        self.origin = np.asarray(self.origin, float).reshape(3)
        nx, ny, nz = self.solid.shape
        self.ijk = np.argwhere(self.solid)
        if self.frac is None:
            self.frac = np.ones(len(self.ijk))
        else:
            self.frac = np.asarray(self.frac, float).reshape(-1)
            if self.frac.shape != (len(self.ijk),):
                raise ValueError("frac must have one value per solid voxel (np.argwhere order)")
        self.element_of = np.full(self.solid.shape, -1, dtype=np.int64)
        self.element_of[tuple(self.ijk.T)] = np.arange(len(self.ijk))
        corner = ((H8_CORNER + 1) / 2).astype(int)
        gnode = lambda k: (k[..., 0] * (ny + 1) + k[..., 1]) * (nz + 1) + k[..., 2]   # noqa: E731
        g = np.stack([gnode(self.ijk + c) for c in corner], axis=1)                    # (ne, 8) grid nodes
        used, inv = np.unique(g, return_inverse=True)
        self.grid_node = used
        self.conn = inv.reshape(g.shape)
        iz = used % (nz + 1)
        iy = (used // (nz + 1)) % (ny + 1)
        ix = used // ((nz + 1) * (ny + 1))
        self.X = self.origin + self.h * np.column_stack([ix, iy, iz]).astype(float)
        self.edof = (3 * self.conn[:, :, None] + np.arange(3)).reshape(-1, 24)
        self._pattern: tuple[sp.csr_matrix, np.ndarray] | None = None

    # ------------------------------------------------------------------ sizes
    @property
    def ne(self) -> int:
        return len(self.ijk)

    @property
    def nn(self) -> int:
        return len(self.X)

    @property
    def ndof(self) -> int:
        return 3 * self.nn

    @property
    def centers(self) -> np.ndarray:
        """(ne, 3) element centres [m]."""
        return self.origin + self.h * (self.ijk + 0.5)

    @property
    def volume(self) -> float:
        """Solid volume [m³] (partial-volume: Σ frac h³)."""
        return float(np.asarray(self.frac).sum()) * self.h ** 3

    # ------------------------------------------------------------------ assembly
    def _sparsity(self) -> tuple[sp.csr_matrix, np.ndarray]:
        if self._pattern is None:
            r = np.repeat(self.edof, 24, axis=1).ravel()
            c = np.tile(self.edof, (1, 24)).ravel()
            key = r.astype(np.int64) * self.ndof + c
            ukey, inv = np.unique(key, return_inverse=True)
            rows, cols = ukey // self.ndof, ukey % self.ndof
            P = sp.csr_matrix((np.zeros(len(ukey)), (rows, cols)), shape=(self.ndof, self.ndof))
            # csr_matrix sorts by (row, col) exactly as np.unique sorted the keys
            self._pattern = (P, inv.astype(np.int64))
        return self._pattern

    def stiffness(self, KE: np.ndarray, scale: np.ndarray | float) -> sp.csr_matrix:
        """Global stiffness ``Σ scale_e KE`` (``scale_e = E_e h`` for physical units)."""
        P, inv = self._sparsity()
        s = np.broadcast_to(np.asarray(scale, float), (self.ne,))
        data = np.bincount(inv, weights=(s[:, None] * KE.ravel()[None, :]).ravel(), minlength=P.nnz)
        K = P.copy()
        K.data = data
        return K

    # ------------------------------------------------------------------ selections
    def nodes_where(self, predicate: Any) -> np.ndarray:
        """Node numbers where ``predicate(X)`` (X (nn, 3) in metres) is true."""
        return np.flatnonzero(np.asarray(predicate(self.X), bool))

    def surface_nodes(self) -> np.ndarray:
        """Nodes on the boundary of the voxel body (a node shared by fewer than 8 solid voxels)."""
        count = np.bincount(self.conn.ravel(), minlength=self.nn)
        return np.flatnonzero(count < 8)


_PARDISO: Any = None


def pardiso_module() -> Any:
    """The pypardiso module with the MKL DLLs made loadable, or ``None``."""
    global _PARDISO
    if _PARDISO is not None:
        return _PARDISO or None
    import os
    folder = os.environ.get("AEROKIT_MKL_BIN", "D:/tmp_ideathon/pylib/mkl_bin")
    try:
        if os.path.isdir(folder):
            os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
            os.add_dll_directory(folder)
            rt = [f for f in os.listdir(folder) if f.lower().startswith("mkl_rt")]
            if rt:
                os.environ.setdefault("PYPARDISO_MKL_RT", os.path.join(folder, rt[0]))
        import pypardiso
        A = sp.csr_matrix(np.array([[2.0, 0.0], [0.0, 4.0]]))
        pypardiso.PyPardisoSolver(mtype=2).solve(sp.triu(A, format="csr"), np.ones(2))
        _PARDISO = pypardiso
    except Exception:                    # noqa: BLE001 - optional accelerator
        _PARDISO = False
    return _PARDISO or None


def pardiso_solve(Kf: sp.csr_matrix, B: np.ndarray) -> np.ndarray:
    """Solve the SPD system with PARDISO (upper triangle, mtype 2)."""
    pp = pardiso_module()
    s = pp.PyPardisoSolver(mtype=2)
    try:
        X = s.solve(sp.triu(Kf, format="csr"), np.ascontiguousarray(B))
    finally:
        s.free_memory(everything=True)
    return X.reshape(B.shape)


class ReducedUpper:
    """Upper triangle of the stiffness on the free DOFs, assembled straight from element matrices with a cached
    pattern (no slicing of the full matrix per solve; half the entries). Used with PARDISO (mtype 2)."""

    def __init__(self, mesh: VoxelMesh, fixed: np.ndarray) -> None:
        nd = mesh.ndof
        gmap = np.full(nd, -1, dtype=np.int64)
        self.free = np.setdiff1d(np.arange(nd), np.unique(fixed))
        gmap[self.free] = np.arange(len(self.free))
        nf = len(self.free)
        r = gmap[np.repeat(mesh.edof, 24, axis=1).ravel()]
        c = gmap[np.tile(mesh.edof, (1, 24)).ravel()]
        keep = (r >= 0) & (c >= 0) & (r <= c)
        self.sel = np.flatnonzero(keep)
        key = r[keep] * nf + c[keep]
        ukey, inv = np.unique(key, return_inverse=True)
        self.inv = inv.astype(np.int64)
        self.P = sp.csr_matrix((np.zeros(len(ukey)), (ukey // nf, ukey % nf)), shape=(nf, nf))
        self.ne = mesh.ne

    def matrix(self, KE: np.ndarray, scale: np.ndarray | float) -> sp.csr_matrix:
        s = np.broadcast_to(np.asarray(scale, float), (self.ne,))
        w = (s[:, None] * KE.ravel()[None, :]).ravel()[self.sel]
        A = self.P.copy()
        A.data = np.bincount(self.inv, weights=w, minlength=self.P.nnz)
        return A

    def solve(self, KE: np.ndarray, scale: np.ndarray | float, F: np.ndarray) -> np.ndarray:
        """Displacements (ndof, n) for loads F (ndof, n) with PARDISO."""
        A = self.matrix(KE, scale)
        pp = pardiso_module()
        s = pp.PyPardisoSolver(mtype=2)
        try:
            X = s.solve(A, np.ascontiguousarray(F[self.free]))
        finally:
            s.free_memory(everything=True)
        U = np.zeros_like(F)
        U[self.free] = X.reshape(F[self.free].shape)
        return U


def _rigid_body_modes(X: np.ndarray) -> np.ndarray:
    """(3 nn, 6) translations and rotations about the centroid (AMG near-null space)."""
    c = X - X.mean(axis=0)
    n = len(X)
    B = np.zeros((3 * n, 6))
    for d in range(3):
        B[d::3, d] = 1.0
    B[0::3, 3], B[1::3, 3] = -c[:, 1], c[:, 0]
    B[1::3, 4], B[2::3, 4] = -c[:, 2], c[:, 1]
    B[0::3, 5], B[2::3, 5] = c[:, 2], -c[:, 0]
    return B


@dataclass
class SolveInfo:
    method: str
    seconds: float
    iterations: int = 0
    residual: float = 0.0


def solve(K: sp.csr_matrix, F: np.ndarray, fixed: np.ndarray, X: np.ndarray | None = None,
          method: str = "auto", direct_limit: int = 8_000, tol: float = 1e-9,
          x0: np.ndarray | None = None) -> tuple[np.ndarray, SolveInfo]:
    """Solve ``K U = F`` with ``U[fixed] = 0``; ``F`` (ndof,) or (ndof, n_cases).

    ``method``: "pardiso", "direct", "amg", "cg" or "auto" (PARDISO if available, else direct when the free DOFs
    ≤ ``direct_limit``, else AMG-PCG).
    """
    t0 = time.perf_counter()
    F = np.asarray(F, float)
    one = F.ndim == 1
    F2 = F[:, None] if one else F
    ndof = K.shape[0]
    fixed = np.unique(np.asarray(fixed, dtype=np.int64))
    if fixed.size == 0:
        raise ValueError("no supports: rigid-body motion")
    free = np.setdiff1d(np.arange(ndof), fixed)
    Kf = K[free][:, free].tocsr()
    U = np.zeros_like(F2)
    if method == "auto":
        method = "pardiso" if pardiso_module() else ("direct" if len(free) <= direct_limit else "amg")
    info = SolveInfo(method, 0.0)
    if method == "pardiso":
        U[free] = pardiso_solve(Kf, F2[free])
    elif method == "direct":
        lu = spla.splu(Kf.tocsc(), permc_spec="MMD_AT_PLUS_A")
        U[free] = lu.solve(F2[free])
    elif method in ("amg", "cg"):
        M = None
        ml = None
        if method == "amg":
            try:
                import pyamg
                Bn = _rigid_body_modes(X)[free] if X is not None else None
                ml = pyamg.smoothed_aggregation_solver(Kf, B=Bn, symmetry="hermitian", max_coarse=500)
                M = ml.aspreconditioner(cycle="V")
            except ImportError:
                info.method = "cg"
        if M is None:
            d = Kf.diagonal()
            M = sp.diags(1.0 / np.where(d > 0, d, 1.0))
        iters = 0
        for k in range(F2.shape[1]):
            b = F2[free, k]
            if not np.any(b):
                continue
            count = [0]

            def cb(_: np.ndarray, count: list[int] = count) -> None:
                count[0] += 1
            guess = x0[free] if (x0 is not None and x0.ndim == 1) else (
                x0[free, k] if x0 is not None else None)
            u, flag = spla.cg(Kf, b, x0=guess, rtol=tol, atol=0.0, maxiter=5000, M=M, callback=cb)
            if flag != 0:
                raise RuntimeError(f"CG did not converge (flag {flag}) for load case {k}")
            U[free, k] = u
            iters += count[0]
        info.iterations = iters
    else:
        raise ValueError("method: auto | pardiso | direct | amg | cg")
    r = K @ U - F2
    r[fixed] = 0.0
    info.residual = float(np.linalg.norm(r)) / max(float(np.linalg.norm(F2)), 1e-300)
    info.seconds = time.perf_counter() - t0
    return (U[:, 0] if one else U), info


# ---------------------------------------------------------------------------------------------- stresses
@dataclass
class _StressOps:
    """Unit-cube stress operators: centroid S0 (6, 24) and Gauss-point Sg (8, 6, 24) incl. modes."""

    S0: np.ndarray
    Sg: np.ndarray
    extrap: np.ndarray                    # (8 corners, 8 gauss) extrapolation matrix


def _stress_ops(nu: float, element: str) -> _StressOps:
    D = D_iso(nu)
    _, R = ke_unit(nu, element)
    Bu0, _ = _B_unit(np.zeros(3))
    S0 = D @ Bu0
    Sg = np.zeros((8, 6, 24))
    for g, p in enumerate(_GAUSS):
        Bu, Ba = _B_unit(p)
        B = Bu + (Ba @ R if R is not None else 0.0)
        Sg[g] = D @ B
    # trilinear interpolation of Gauss values, evaluated at the corners (natural coords ±√3 in Gauss space)
    E = np.zeros((8, 8))
    for i, c in enumerate(H8_CORNER):
        q = c * math.sqrt(3.0)
        for g, p in enumerate(_GAUSS):
            s = np.sign(p)
            E[i, g] = 0.125 * np.prod(1 + s * q)
    return _StressOps(S0, Sg, E)


@dataclass
class StaticResult:
    """Result of :func:`static` for one load case (SI units)."""

    U: np.ndarray                         # (ndof,) displacement [m]
    compliance: float                     # Fᵀ U [J]
    vm_element: np.ndarray                # (ne,) centroid von Mises [Pa]
    vm_node: np.ndarray                   # (nn,) averaged nodal von Mises [Pa]
    stress_node: np.ndarray               # (nn, 6) averaged nodal stress [Pa]
    reaction: np.ndarray                  # (3,) sum of reactions at the fixed DOFs [N]
    solve: SolveInfo
    max_disp: float = 0.0                 # max |u| [m]
    max_disp_node: int = -1

    def summary(self) -> dict[str, float]:
        return {"compliance_J": self.compliance, "max_disp_m": self.max_disp,
                "max_vm_node_Pa": float(self.vm_node.max()), "max_vm_element_Pa": float(self.vm_element.max())}


def static(mesh: VoxelMesh, E: float | np.ndarray, nu: float, F: np.ndarray, fixed: np.ndarray,
           element: str = "H8IM", method: str = "auto", thermal_strain: float | np.ndarray | None = None,
           **solve_kw: Any) -> list[StaticResult]:
    """Linear static analysis; ``E`` scalar or (ne,) [Pa]; ``F`` (ndof,) or (ndof, n_cases) [N].

    Partial-volume voxels (``mesh.frac`` < 1) contribute ``frac`` × their stiffness; their stress is the material
    stress E·ε of the computed strain (not scaled by ``frac``). ``thermal_strain`` (α ΔT, scalar or (ne,)) adds the
    equivalent thermal load to every case and the stress becomes D (ε − ε_th). Returns one :class:`StaticResult` per
    load case.
    """
    KE, _ = ke_unit(nu, element)
    Ee = np.broadcast_to(np.asarray(E, float), (mesh.ne,))
    K = mesh.stiffness(KE, Ee * np.asarray(mesh.frac) * mesh.h)          # partial voxels: stiffness × solid fraction
    F = np.asarray(F, float)
    F2 = (F[:, None] if F.ndim == 1 else F).copy()
    eth = None
    if thermal_strain is not None:
        eth = np.broadcast_to(np.asarray(thermal_strain, float), (mesh.ne,))
        f0, eps_modes = thermal_unit(nu, element)
        fe = (Ee * np.asarray(mesh.frac) * eth * mesh.h ** 2)[:, None] * f0[None, :]       # (ne, 24)
        fth = np.zeros(mesh.ndof)
        np.add.at(fth, mesh.edof.ravel(), fe.ravel())
        F2 += fth[:, None]
    U, info = solve(K, F2, fixed, mesh.X, method=method, **solve_kw)
    ops = _stress_ops(nu, element)
    out = []
    count = np.bincount(mesh.conn.ravel(), minlength=mesh.nn).astype(float)
    for k in range(F2.shape[1]):
        u = U[:, k]
        ue = u[mesh.edof]                                          # (ne, 24)
        s0 = (ue @ ops.S0.T) * (Ee / mesh.h)[:, None]             # (ne, 6)
        sg = np.einsum("gij,ej->egi", ops.Sg, ue) * (Ee / mesh.h)[:, None, None]   # (ne, 8, 6)
        if eth is not None:                                        # σ = D (ε − ε_th); modes add D B_α K_αα⁻¹ f_α
            Dm = D_iso(nu)
            e0 = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
            s0 -= (Ee * eth)[:, None] * (Dm @ e0)[None, :]
            corr = np.array([Dm @ (em - e0) for em in eps_modes])          # (8, 6)
            sg += (Ee * eth)[:, None, None] * corr[None, :, :]
        sc = np.einsum("cg,egi->eci", ops.extrap, sg)              # (ne, 8 corners, 6)
        sn = np.zeros((mesh.nn, 6))
        for i in range(6):
            sn[:, i] = np.bincount(mesh.conn.ravel(), weights=sc[:, :, i].ravel(), minlength=mesh.nn)
        sn /= count[:, None]
        r = K @ u - F2[:, k]
        react = np.zeros(3)
        fixed_u = np.unique(np.asarray(fixed))
        for d in range(3):
            sel = fixed_u[fixed_u % 3 == d]
            react[d] = r[sel].sum()
        disp = np.linalg.norm(u.reshape(-1, 3), axis=1)
        j = int(np.argmax(disp))
        out.append(StaticResult(u, float(F2[:, k] @ u), von_mises(s0), von_mises(sn), sn, react, info,
                                float(disp[j]), j))
    return out
