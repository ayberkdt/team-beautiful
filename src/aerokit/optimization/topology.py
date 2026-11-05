"""Topology optimization: SIMP compliance minimization under a volume constraint.

Basis: Andreassen, Clausen, Schevenels, Lazarov & Sigmund (2011), "Efficient topology optimization
in MATLAB using 88 lines of code", Struct Multidisc Optim 43:1-16 (top88). This module is a
line-by-line Python counterpart of top88 (KE, edofMat/iK/jK, H/Hs filter, OC bisection, stopping
criterion) and additionally contains the extensions of §5.1-5.4 (boundary conditions, multiple
load cases, passive elements, Heaviside projection).

Problem::

    min c(x) = Σ_loads Uᵀ K(x̄) U   subject to   Σ x̄_e = V*·n,   0 ≤ x ≤ 1

Modified SIMP: ``E_e = Emin + x̄_e^p (E0 − Emin)`` (Sigmund 2007).

Filters (``ft``):

0
    no filter (x̄ = x) — for testing and comparison
1
    sensitivity filter (top88 line 64) — dc is filtered, x̄ = x (the gradient is NOT consistent)
2
    density filter (top88 lines 66-67, 77) — x̄ = H x / Hs, exact chain rule
3
    Heaviside projection (top88 §5.4, Guest et al. 2004): x̃ = H x / Hs,
    x̄ = 1 − exp(−βx̃) + x̃ exp(−β); β = 1 → 512, doubled every 50 iterations or when the
    change drops to ≤ 0.01

Optimizers: ``"OC"`` (top88 lines 70-80) and ``"MMA"`` (Svanberg 1987, single constraint; the dual
of the subproblem is solved by bisection on λ, see :func:`mma_subproblem`).

Numbering (2-D, identical to top88, zero-based):

* node (column i, row j; j = 0 is the TOP edge) → n = i (nely + 1) + j; DOFs 2n (x), 2n + 1 (y)
* element (column i, row j) → e = i·nely + j; density array (nely, nelx), row 0 = top
  (MATLAB column-major flattening ``x(:)`` → ``order="F"``)
* physical coordinate y points up: :meth:`Grid2D.node` counts ``iy`` from the BOTTOM.

3-D (:class:`Grid3D`): node n = (ix (nely+1) + iy)(nelz+1) + iz, y up; element
e = (ix·nely + iy)·nelz + iz; density array (nelx, nely, nelz) in C order. The element node order
is that of :class:`aerokit.fem.elements.solid.H8`.

Unit-size (1×1 or 1×1×1) elements, thickness 1 and E0 = 1 by default; results are dimensionless.
This module produces no figures; every result is a NumPy array.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from functools import partial
from typing import Any, Literal

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from aerokit.references import cite


# =====================================================================================
# element stiffness matrices
# =====================================================================================
@cite("andreassen_2011", note="top88, lines 8-12")
def ke_q4(nu: float = 0.3) -> np.ndarray:
    """Stiffness matrix of the unit-square bilinear Q4 element in plane stress (8×8).

    Parameters
    ----------
    nu : float
        Poisson's ratio, −1 < ν < 0.5.

    Returns
    -------
    numpy.ndarray
        (8, 8) stiffness for E = 1 and thickness t = 1.

    Raises
    ------
    ValueError
        If ν is outside (−1, 0.5).

    Notes
    -----
    DOF order (top88 edofMat): lower-left, lower-right, upper-right, upper-left node, each (u, v).
    This is the counter-clockwise order (−1,−1), (1,−1), (1,1), (−1,1) of
    :class:`aerokit.fem.elements.plane.Q4`. ``KE = 1/(1 − ν²)/24 · ([A11 A12; A12ᵀ A11]
    + ν [B11 B12; B12ᵀ B11])``.

    Examples
    --------
    >>> round(float(ke_q4(0.3)[0, 0]), 6)
    0.494505
    """
    if not -1 < nu < 0.5:
        raise ValueError("−1 < ν < 0.5 is required")
    A11 = np.array([[12, 3, -6, -3], [3, 12, 3, 0], [-6, 3, 12, -3], [-3, 0, -3, 12]], float)
    A12 = np.array([[-6, -3, 0, 3], [-3, -6, -3, -6], [0, -3, -6, 3], [3, -6, 3, -6]], float)
    B11 = np.array([[-4, 3, -2, 9], [3, -4, -9, 4], [-2, -9, -4, -3], [9, 4, -3, -4]], float)
    B12 = np.array([[2, -3, 4, -9], [-3, 2, 9, -2], [4, 9, 2, 3], [-9, -2, 3, 2]], float)
    return 1 / (1 - nu ** 2) / 24 * (np.block([[A11, A12], [A12.T, A11]])
                                     + nu * np.block([[B11, B12], [B12.T, B11]]))


H8_CORNER = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                      [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], dtype=float)
"""Natural coordinates of the H8 corner nodes (same order as :class:`aerokit.fem.elements.solid.H8`)."""


def ke_h8(nu: float = 0.3) -> np.ndarray:
    """Stiffness matrix of the unit-cube trilinear brick (H8) element (24×24), 2×2×2 Gauss.

    Parameters
    ----------
    nu : float
        Poisson's ratio, −1 < ν < 0.5.

    Returns
    -------
    numpy.ndarray
        (24, 24) stiffness for E = 1.

    Raises
    ------
    ValueError
        If ν is outside (−1, 0.5).

    Notes
    -----
    Voigt order [εx, εy, εz, γyz, γxz, γxy]; node order :data:`H8_CORNER`. Liu & Tovar (2014, top3d)
    give KE in closed form; here it is integrated numerically (that paper was not read in this
    repository; the test compares against :class:`aerokit.fem.elements.solid.H8`). The Jacobian of
    the unit cube is I/2, so ∂/∂x = 2 ∂/∂ξ and det J = 1/8.
    """
    if not -1 < nu < 0.5:
        raise ValueError("−1 < ν < 0.5 is required")
    c = 1.0 / ((1 + nu) * (1 - 2 * nu))
    D = np.zeros((6, 6))
    D[:3, :3] = c * nu
    np.fill_diagonal(D[:3, :3], c * (1 - nu))
    D[3:, 3:] = np.eye(3) / (2 * (1 + nu))
    g = 1 / math.sqrt(3)
    K = np.zeros((24, 24))
    s = H8_CORNER
    for p in [(a, b, d) for a in (-g, g) for b in (-g, g) for d in (-g, g)]:
        a = 1 + s * np.asarray(p)
        dN = 0.125 * np.vstack([s[:, 0] * a[:, 1] * a[:, 2], s[:, 1] * a[:, 0] * a[:, 2],
                                s[:, 2] * a[:, 0] * a[:, 1]]) * 2.0     # J = I/2 → ∂/∂x = 2 ∂/∂ξ
        B = np.zeros((6, 24))
        B[0, 0::3] = dN[0]
        B[1, 1::3] = dN[1]
        B[2, 2::3] = dN[2]
        B[3, 1::3] = dN[2]
        B[3, 2::3] = dN[1]
        B[4, 0::3] = dN[2]
        B[4, 2::3] = dN[0]
        B[5, 0::3] = dN[1]
        B[5, 1::3] = dN[0]
        K += B.T @ D @ B * 0.125                                       # det J = 1/8, w = 1
    return K


# =====================================================================================
# structured grids
# =====================================================================================
class _Grid:
    """Shared grid machinery: edof (nel × nde), iK/jK (top88 lines 16-17), centres, filter."""

    ndim: int
    nel: int
    ndof: int
    shape: tuple[int, ...]
    _order: Literal["C", "F"]
    KE: np.ndarray
    edof: np.ndarray
    center: np.ndarray
    X: np.ndarray
    _dims: np.ndarray

    def _element_no(self, k: np.ndarray) -> np.ndarray:
        """Element number of integer element coordinates ``k`` (n, ndim)."""
        raise NotImplementedError

    def _prepare(self) -> None:
        """Build the COO assembly index vectors iK, jK and the flattened KE."""
        nde = self.edof.shape[1]
        self.iK = np.repeat(self.edof, nde, axis=1).ravel()
        self.jK = np.tile(self.edof, (1, nde)).ravel()
        self._KEr = self.KE.ravel()

    def to_array(self, v: np.ndarray) -> np.ndarray:
        """Reshape an element vector to the density array.

        Parameters
        ----------
        v : array_like
            (nel,) element values.

        Returns
        -------
        numpy.ndarray
            2-D: (nely, nelx), row 0 at the top; 3-D: (nelx, nely, nelz).
        """
        return np.asarray(v).reshape(self.shape, order=self._order)

    def vector(self, a: Any) -> np.ndarray:
        """Convert a scalar, a density array or an element vector to a (nel,) element vector.

        Parameters
        ----------
        a : float or array_like
            Scalar (uniform field), array of shape :attr:`shape` or vector of length ``nel``.

        Returns
        -------
        numpy.ndarray
            (nel,) float copy.

        Raises
        ------
        ValueError
            If the shape matches neither form.
        """
        a = np.asarray(a, dtype=float)
        if a.ndim == 0:
            return np.full(self.nel, float(a))
        if a.shape == self.shape:
            return a.reshape(-1, order=self._order).copy()
        if a.shape == (self.nel,):
            return a.copy()
        raise ValueError(f"density shape {a.shape}; expected {self.shape} or ({self.nel},)")

    @cite("andreassen_2011", note="top88, lines 25-44")
    def filter_matrix(self, rmin: float) -> tuple[sp.csr_matrix, np.ndarray]:
        """Linear (cone) filter matrix H and its row sums Hs.

        Parameters
        ----------
        rmin : float
            Filter radius in element sizes, > 0.

        Returns
        -------
        H : scipy.sparse.csr_matrix
            (nel, nel), ``H_ei = max(0, rmin − |e − i|)`` (distance between element centres).
        Hs : numpy.ndarray
            (nel,) row sums of H.

        Raises
        ------
        ValueError
            If ``rmin ≤ 0``.

        Notes
        -----
        Neighbourhood |Δ| ≤ ceil(rmin) − 1 in every index direction, as in top88.
        """
        if not rmin > 0:
            raise ValueError("rmin > 0 is required")
        r = math.ceil(rmin) - 1
        dim = self.center.shape[1]
        offsets = np.array(np.meshgrid(*[np.arange(-r, r + 1)] * dim, indexing="ij")).reshape(dim, -1).T
        e1 = np.arange(self.nel)
        rows, cols, weights = [], [], []
        for d in offsets:
            w = rmin - math.sqrt(float(d @ d))
            if w <= 0:
                continue
            k = self.center + d
            inside = np.all((k >= 0) & (k < self._dims), axis=1)
            rows.append(e1[inside])
            cols.append(self._element_no(k[inside]))
            weights.append(np.full(inside.sum(), w))
        H = sp.csr_matrix((np.concatenate(weights), (np.concatenate(rows), np.concatenate(cols))),
                          shape=(self.nel, self.nel))
        Hs = np.asarray(H.sum(axis=1)).ravel()
        return H, Hs

    def find_dof(self, condition: Callable[..., bool], direction: int) -> list[int]:
        """DOFs in ``direction`` (0 x, 1 y, 2 z) of the nodes where ``condition(x, y[, z])`` is true.

        Parameters
        ----------
        condition : callable
            Predicate of the physical node coordinates.
        direction : int
            0 (x), 1 (y) or 2 (z).

        Returns
        -------
        list of int
            Global DOF numbers.
        """
        return [self.ndim * n + direction for n, X in enumerate(self.X) if condition(*X)]


@cite("andreassen_2011", note="top88, lines 13-17")
class Grid2D(_Grid):
    """nelx × nely grid of unit-square Q4 elements, numbered as in top88.

    Parameters
    ----------
    nelx, nely : int
        Number of elements in x and y (positive integers).
    nu : float
        Poisson's ratio.

    Attributes
    ----------
    nel, ndof : int
        Number of elements and DOFs.
    shape : tuple
        Density-array shape (nely, nelx).
    KE : numpy.ndarray
        Unit element stiffness (:func:`ke_q4`).
    edof : numpy.ndarray
        (nel, 8) element DOF table (top88 edofMat, zero-based).
    center : numpy.ndarray
        (nel, 2) integer element indices (i, j), j counted from the top.
    X : numpy.ndarray
        (n_node, 2) physical node coordinates, y up.

    Raises
    ------
    ValueError
        If nelx or nely is not a positive integer.
    """

    ndim = 2

    def __init__(self, nelx: int, nely: int, nu: float = 0.3) -> None:
        if int(nelx) != nelx or int(nely) != nely or nelx < 1 or nely < 1:
            raise ValueError("nelx, nely must be positive integers")
        self.nelx, self.nely, self.nu = int(nelx), int(nely), nu
        self.nel = self.nelx * self.nely
        self.ndof = 2 * (self.nelx + 1) * (self.nely + 1)
        self.shape, self._order = (self.nely, self.nelx), "F"
        self.KE = ke_q4(nu)
        nodenrs = np.arange((nelx + 1) * (nely + 1)).reshape(nelx + 1, nely + 1).T   # [j, i]
        edofVec = (2 * nodenrs[:-1, :-1] + 2).reshape(-1, order="F")                 # lower-left node x DOF
        ny = self.nely
        self.edof = edofVec[:, None] + np.array([0, 1, 2 * ny + 2, 2 * ny + 3, 2 * ny, 2 * ny + 1, -2, -1])
        e = np.arange(self.nel)
        self.center = np.column_stack([e // ny, e % ny])                              # (i, j)
        self._dims = np.array([self.nelx, self.nely])
        n = np.arange((nelx + 1) * (nely + 1))
        self.X = np.column_stack([n // (ny + 1), ny - n % (ny + 1)]).astype(float)   # y up
        self._prepare()

    def _element_no(self, k: np.ndarray) -> np.ndarray:
        """Element number of (i, j) index pairs."""
        return k[:, 0] * self.nely + k[:, 1]

    def node(self, ix: int, iy: int) -> int:
        """Node number at physical position (x = ix, y = iy), with ``iy`` counted from the BOTTOM.

        Raises
        ------
        ValueError
            If the node lies outside the grid.
        """
        if not (0 <= ix <= self.nelx and 0 <= iy <= self.nely):
            raise ValueError("node outside the grid")
        return int(ix) * (self.nely + 1) + (self.nely - int(iy))

    def dof(self, ix: int, iy: int, direction: int) -> int:
        """Global DOF of node (ix, iy) in ``direction`` (0 x, 1 y)."""
        return 2 * self.node(ix, iy) + direction

    def element_center(self) -> np.ndarray:
        """(nel, 2) physical element-centre coordinates (x, y), y up."""
        return np.column_stack([self.center[:, 0] + 0.5, self.nely - self.center[:, 1] - 0.5])


class Grid3D(_Grid):
    """nelx × nely × nelz grid of unit-cube H8 elements.

    The layout resembles Liu & Tovar (2014, top3d) but the numbering differs (see module notes).

    Parameters
    ----------
    nelx, nely, nelz : int
        Number of elements in x, y, z (positive integers).
    nu : float
        Poisson's ratio.

    Raises
    ------
    ValueError
        If a dimension is not a positive integer.
    """

    ndim = 3

    def __init__(self, nelx: int, nely: int, nelz: int, nu: float = 0.3) -> None:
        for v in (nelx, nely, nelz):
            if int(v) != v or v < 1:
                raise ValueError("nelx, nely, nelz must be positive integers")
        self.nelx, self.nely, self.nelz, self.nu = int(nelx), int(nely), int(nelz), nu
        self.nel = self.nelx * self.nely * self.nelz
        self.ndof = 3 * (self.nelx + 1) * (self.nely + 1) * (self.nelz + 1)
        self.shape, self._order = (self.nelx, self.nely, self.nelz), "C"
        self.KE = ke_h8(nu)
        ix, iy, iz = np.meshgrid(np.arange(nelx), np.arange(nely), np.arange(nelz), indexing="ij")
        self.center = np.column_stack([ix.ravel(), iy.ravel(), iz.ravel()])
        self._dims = np.array([self.nelx, self.nely, self.nelz])
        corner = ((H8_CORNER + 1) / 2).astype(int)
        conn = np.column_stack([self._node_no(self.center + k) for k in corner])        # (nel, 8)
        self.edof = (3 * conn[:, :, None] + np.arange(3)).reshape(self.nel, 24)
        gx, gy, gz = np.meshgrid(np.arange(nelx + 1), np.arange(nely + 1), np.arange(nelz + 1), indexing="ij")
        self.X = np.column_stack([gx.ravel(), gy.ravel(), gz.ravel()]).astype(float)
        self._prepare()

    def _node_no(self, k: np.ndarray) -> np.ndarray:
        """Node number of integer node coordinates (ix, iy, iz)."""
        return (k[:, 0] * (self.nely + 1) + k[:, 1]) * (self.nelz + 1) + k[:, 2]

    def _element_no(self, k: np.ndarray) -> np.ndarray:
        """Element number of integer element coordinates (ix, iy, iz)."""
        return (k[:, 0] * self.nely + k[:, 1]) * self.nelz + k[:, 2]

    def node(self, ix: int, iy: int, iz: int) -> int:
        """Node number at (ix, iy, iz) (y up).

        Raises
        ------
        ValueError
            If the node lies outside the grid.
        """
        if not (0 <= ix <= self.nelx and 0 <= iy <= self.nely and 0 <= iz <= self.nelz):
            raise ValueError("node outside the grid")
        return int(self._node_no(np.array([[ix, iy, iz]]))[0])

    def dof(self, ix: int, iy: int, iz: int, direction: int) -> int:
        """Global DOF of node (ix, iy, iz) in ``direction`` (0 x, 1 y, 2 z)."""
        return 3 * self.node(ix, iy, iz) + direction

    def element_center(self) -> np.ndarray:
        """(nel, 3) element-centre coordinates."""
        return self.center + 0.5


# =====================================================================================
# problem: boundary conditions, loads, analysis
# =====================================================================================
@cite("andreassen_2011", note="top88 §5.2 (multiple loads), §5.3 (passive elements)")
class Problem:
    """Grid + loads + supports + passive elements + SIMP material.

    Parameters
    ----------
    grid : Grid2D or Grid3D
        Structured grid.
    F : array_like, dict or list of dict
        Loads: (ndof,) or (ndof, n_load) array (dense or sparse), a ``{dof: value}`` dict, or a
        list of such dicts (one per load case). The objective is Σ_loads c_i (top88 §5.2).
    fixed : sequence of int
        DOFs with zero displacement.
    passive : array_like, optional
        Element array/vector: 0 free, 1 void (x = 0), 2 solid (x = 1) (top88 §5.3 coding).
    penalty : float
        SIMP exponent p ≥ 1.
    E0, Emin : float
        Solid and void Young's moduli, E0 > 0, 0 ≤ Emin < E0.

    Attributes
    ----------
    F : numpy.ndarray
        (ndof, n_load) load matrix.
    fixed, free : numpy.ndarray
        Constrained and free DOFs.
    passive : numpy.ndarray
        (nel,) passive codes.

    Raises
    ------
    ValueError
        For invalid material data, missing supports, out-of-range DOFs or passive codes.
    """

    def __init__(self, grid: _Grid, F: Any, fixed: Sequence[int], passive: Any = None, penalty: float = 3.0,
                 E0: float = 1.0, Emin: float = 1e-9) -> None:
        self.grid = grid
        if not (E0 > 0 and 0 <= Emin < E0):
            raise ValueError("E0 > 0 and 0 ≤ Emin < E0 are required")
        if not penalty >= 1:
            raise ValueError("penalty exponent p ≥ 1 is required")
        self.penalty, self.E0, self.Emin = float(penalty), float(E0), float(Emin)
        self.F = self._load(F)
        fixed_arr = np.unique(np.asarray(fixed, dtype=int))
        if fixed_arr.size == 0:
            raise ValueError("no supports: rigid-body motion")
        if fixed_arr.min() < 0 or fixed_arr.max() >= grid.ndof:
            raise ValueError("fixed DOF number out of range")
        self.fixed = fixed_arr
        self.free = np.setdiff1d(np.arange(grid.ndof), fixed_arr)
        if passive is None:
            self.passive = np.zeros(grid.nel, dtype=int)
        else:
            self.passive = grid.vector(passive).astype(int)
            if not np.all(np.isin(self.passive, (0, 1, 2))):
                raise ValueError("passive values must be 0, 1 or 2")

    def _load(self, F: Any) -> np.ndarray:
        """Convert the load specification to an (ndof, n_load) matrix."""
        n = self.grid.ndof
        if isinstance(F, dict):
            F = [F]
        M: np.ndarray
        if isinstance(F, list | tuple) and F and isinstance(F[0], dict):
            M = np.zeros((n, len(F)))
            for k, d in enumerate(F):
                for dof, v in d.items():
                    if not 0 <= dof < n:
                        raise ValueError("load DOF number out of range")
                    M[dof, k] += v
            return M
        M = np.asarray(F.toarray() if sp.issparse(F) else F, dtype=float)
        if M.ndim == 1:
            M = M[:, None]
        if M.shape[0] != n:
            raise ValueError(f"F has {M.shape[0]} rows, expected ndof = {n}")
        return M

    def modulus(self, xphys: np.ndarray) -> np.ndarray:
        """Modified SIMP Young's modulus ``E = Emin + x̄^p (E0 − Emin)``."""
        return self.Emin + xphys ** self.penalty * (self.E0 - self.Emin)

    @cite("andreassen_2011", note="top88, lines 54-60")
    def analysis(self, xphys: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
        """Finite element analysis for a physical density field.

        Parameters
        ----------
        xphys : numpy.ndarray
            (nel,) physical densities x̄.

        Returns
        -------
        c : float
            Compliance Σ_loads Uᵀ K U.
        dc : numpy.ndarray
            (nel,) ∂c/∂x̄ = −p (E0 − Emin) x̄^(p−1) u_eᵀ KE u_e (summed over loads).
        U : numpy.ndarray
            (ndof, n_load) displacements.
        """
        grid = self.grid
        E = self.modulus(xphys)
        sK = (grid._KEr[None, :] * E[:, None]).ravel()
        K = sp.coo_matrix((sK, (grid.iK, grid.jK)), shape=(grid.ndof, grid.ndof)).tocsc()
        K = (K + K.T) / 2
        Kf = K[self.free][:, self.free].tocsc()
        U = np.zeros_like(self.F)
        U[self.free] = spla.splu(Kf).solve(self.F[self.free])
        Ue = U[grid.edof]                                           # (nel, nde, n_load)
        ce = np.einsum("eal,ab,ebl->e", Ue, grid.KE, Ue)
        c = float(np.sum(E * ce))
        dc = -self.penalty * (self.E0 - self.Emin) * xphys ** (self.penalty - 1) * ce
        return c, dc, U


# =====================================================================================
# density mapping (filter / projection) and chain rule
# =====================================================================================
@cite("bourdin_2001", "bruns_tortorelli_2001", "guest_prevost_2004", "andreassen_2011",
      note="density filter; Heaviside projection as in top88 §5.4")
class Density:
    """Mapping x (design) → x̄ (physical); passive elements are fixed to 0/1 in x̄.

    Parameters
    ----------
    grid : Grid2D or Grid3D
        Grid providing :meth:`_Grid.filter_matrix`.
    rmin : float
        Filter radius (element sizes).
    ft : int
        0 none, 1 sensitivity filter, 2 density filter, 3 Heaviside projection.
    passive : array_like, optional
        (nel,) passive codes (0 free, 1 void, 2 solid).

    Raises
    ------
    ValueError
        If ``ft`` is not 0-3 or ``rmin ≤ 0``.
    """

    def __init__(self, grid: _Grid, rmin: float, ft: int, passive: Any = None) -> None:
        if ft not in (0, 1, 2, 3):
            raise ValueError("ft: 0 (none), 1 (sensitivity), 2 (density), 3 (Heaviside)")
        self.ft = ft
        self.H, self.Hs = grid.filter_matrix(rmin)
        self.Ht = self.H.T.tocsr()
        self.passive = np.zeros(grid.nel, dtype=int) if passive is None else np.asarray(passive)

    def _apply_passive(self, x: np.ndarray) -> np.ndarray:
        """Set void elements to 0 and solid elements to 1 (in place)."""
        x[self.passive == 1] = 0.0
        x[self.passive == 2] = 1.0
        return x

    def intermediate(self, x: np.ndarray) -> np.ndarray:
        """Filtered density x̃ = H x / Hs (used by ft 2 and 3)."""
        return (self.H @ x) / self.Hs

    def physical(self, x: np.ndarray, beta: float = 1.0) -> np.ndarray:
        """Physical density x̄(x).

        Parameters
        ----------
        x : numpy.ndarray
            (nel,) design variables.
        beta : float
            Heaviside sharpness β (ft = 3 only).

        Returns
        -------
        numpy.ndarray
            (nel,) x̄: x (ft 0, 1), x̃ (ft 2) or 1 − exp(−βx̃) + x̃ exp(−β) (ft 3), passive elements
            overwritten.
        """
        if self.ft in (0, 1):
            xf = np.array(x, dtype=float)
        elif self.ft == 2:
            xf = self.intermediate(x)
        else:
            xt = self.intermediate(x)
            xf = 1 - np.exp(-beta * xt) + xt * math.exp(-beta)
        return self._apply_passive(xf)

    @cite("andreassen_2011", note="top88 Eqs. (21)-(23)")
    def chain_rule(self, x: np.ndarray, dphys: np.ndarray, beta: float = 1.0) -> np.ndarray:
        """Gradient with respect to the design: ∂f/∂x = (∂x̄/∂x)ᵀ ∂f/∂x̄.

        Parameters
        ----------
        x : numpy.ndarray
            (nel,) design variables.
        dphys : numpy.ndarray
            (nel,) ∂f/∂x̄.
        beta : float
            Heaviside sharpness β (ft = 3).

        Returns
        -------
        numpy.ndarray
            (nel,) ∂f/∂x. Exact for ft 0, 2, 3; for ft 1 the input is returned (x̄ = x).
            ∂x̄/∂x = 0 for passive elements.
        """
        d = np.array(dphys, dtype=float)
        d[self.passive > 0] = 0.0
        if self.ft in (0, 1):
            return d
        if self.ft == 3:
            xt = self.intermediate(x)
            d = d * (beta * np.exp(-beta * xt) + math.exp(-beta))     # top88 Eq. (23)
        return self.Ht @ (d / self.Hs)

    @cite("sigmund_1997", "andreassen_2011", note="top88, line 64")
    def sensitivity_filter(self, x: np.ndarray, dc: np.ndarray) -> np.ndarray:
        """Heuristic sensitivity filter ``dc ← H (x·dc) / Hs / max(1e-3, x)``."""
        return (self.H @ (x * dc)) / self.Hs / np.maximum(1e-3, x)


def compliance_and_gradient(problem: Problem, density: Density, x: np.ndarray,
                            beta: float = 1.0) -> tuple[float, np.ndarray]:
    """Compliance c(x) and its full gradient dc/dx.

    Parameters
    ----------
    problem : Problem
        Analysis problem.
    density : Density
        Design → physical mapping.
    x : numpy.ndarray
        (nel,) design variables.
    beta : float
        Heaviside sharpness β (ft = 3).

    Returns
    -------
    c : float
        Compliance.
    dc : numpy.ndarray
        (nel,) dc/dx (exact for ft 0, 2, 3). For ft = 1, ∂c/∂x̄ is returned (the sensitivity filter
        is not a gradient).
    """
    xphys = density.physical(x, beta)
    c, dcf, _ = problem.analysis(xphys)
    return c, density.chain_rule(x, dcf, beta)


# =====================================================================================
# optimizers
# =====================================================================================
@cite("andreassen_2011", note="top88, lines 70-80")
def update_oc(x: np.ndarray, dc: np.ndarray, dv: np.ndarray, volume: float, move: float,
              physical: Callable[[np.ndarray], np.ndarray], nel: int,
              passive: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    """Optimality-criteria update with bisection on the Lagrange multiplier λ.

    Parameters
    ----------
    x : numpy.ndarray
        (nel,) current design.
    dc, dv : numpy.ndarray
        (nel,) sensitivities of compliance and volume (dv > 0).
    volume : float
        Volume fraction V*.
    move : float
        Move limit on x.
    physical : callable
        Mapping x → x̄ used for the volume check.
    nel : int
        Number of elements.
    passive : numpy.ndarray, optional
        Passive codes; the design variables of passive elements are also held at 0/1 (an
        extension of this module; top88 §5.3 fixes only x̄ — the result is the same for ft = 1).

    Returns
    -------
    xnew : numpy.ndarray
        Updated design.
    xphys : numpy.ndarray
        Corresponding physical densities.
    lmid : float
        Final multiplier.

    Notes
    -----
    ``x_new = max(0, max(x − m, min(1, min(x + m, x·√(−dc/dv/λ)))))``; λ is bisected while
    (l2 − l1)/(l1 + l2) > 1e-3 (written without division). If the volume cannot be met within the
    move limit, l2 → 0 (MATLAB's 0/0 = NaN would end the loop); a floor
    λ ≥ 1e-250·max(−dc/dv) prevents overflow.
    """
    l1, l2 = 0.0, 1e9
    base = 1e-250 * max(float(np.max(-dc / dv)), 1e-300)
    while (l2 - l1) > 1e-3 * (l1 + l2) and l2 > base:
        lmid = 0.5 * (l2 + l1)
        Be = np.sqrt(np.maximum(-dc / dv / lmid, 0.0))     # top88: x.*sqrt(-dc./dv/lmid)
        xnew = np.maximum(0.0, np.maximum(x - move, np.minimum(1.0, np.minimum(x + move, x * Be))))
        if passive is not None:
            xnew[passive == 1] = 0.0
            xnew[passive == 2] = 1.0
        xphys = physical(xnew)
        if xphys.sum() > volume * nel:
            l1 = lmid
        else:
            l2 = lmid
    return xnew, xphys, lmid


@cite("svanberg_1987", note="§3; coefficients as in the mmapy port of Svanberg's 2007 MATLAB code")
def mma_asymptote(k: int, x: np.ndarray, xold1: np.ndarray, xold2: np.ndarray, low: np.ndarray | None,
                  upp: np.ndarray | None, xmin: np.ndarray, xmax: np.ndarray, asyinit: float = 0.5,
                  asydecr: float = 0.7, asyincr: float = 1.2, asymin: float = 0.01,
                  asymax: float = 10.0) -> tuple[np.ndarray, np.ndarray]:
    """Moving asymptotes of MMA.

    Parameters
    ----------
    k : int
        Iteration number (1-based).
    x, xold1, xold2 : numpy.ndarray
        Current design and the two previous designs.
    low, upp : numpy.ndarray or None
        Previous asymptotes (ignored for k ≤ 2).
    xmin, xmax : numpy.ndarray
        Variable bounds.
    asyinit, asydecr, asyincr, asymin, asymax : float
        Asymptote coefficients.

    Returns
    -------
    low, upp : numpy.ndarray
        New lower and upper asymptotes.

    Notes
    -----
    k ≤ 2: l = x − asyinit (xmax − xmin), u = x + asyinit (xmax − xmin).
    k > 2: γ = asyincr if (x − x₁)(x₁ − x₂) > 0, asydecr if < 0, 1 if = 0;
    l = x − γ (x₁ − l), u = x + γ (u − x₁), clipped to [asymin, asymax]·(xmax − xmin) from x.
    The coefficients were read from A. Deetman's Python port (GCMMA-MMA-Python, ``mmapy/mma.py``)
    of Svanberg's 2007 MATLAB code; Svanberg's 2007 notes could not be read.
    """
    dx = xmax - xmin
    if k <= 2:
        return x - asyinit * dx, x + asyinit * dx
    if low is None or upp is None:
        raise ValueError("mma_asymptote: previous asymptotes low/upp are required for k > 2")
    z = (x - xold1) * (xold1 - xold2)
    g = np.ones_like(x)
    g[z > 0] = asyincr
    g[z < 0] = asydecr
    low = x - g * (xold1 - low)
    upp = x + g * (upp - xold1)
    low = np.minimum(np.maximum(low, x - asymax * dx), x - asymin * dx)
    upp = np.maximum(np.minimum(upp, x + asymax * dx), x + asymin * dx)
    return low, upp


@cite("svanberg_1987", note="Eqs. 4-6 and §5 (dual approach); coefficients from the mmapy port")
def mma_subproblem(x: np.ndarray, xmin: np.ndarray, xmax: np.ndarray, low: np.ndarray, upp: np.ndarray,
                   df0: np.ndarray, g: float, dg: np.ndarray, move: float = 0.5, albefa: float = 0.1,
                   raa0: float = 1e-5, c: float = 1000.0, d: float = 1.0,
                   tol: float = 1e-14) -> tuple[np.ndarray, float, float]:
    """Solve the single-constraint MMA subproblem by bisection on its dual.

    Parameters
    ----------
    x : numpy.ndarray
        Current design xᵏ.
    xmin, xmax : numpy.ndarray
        Variable bounds.
    low, upp : numpy.ndarray
        Asymptotes (:func:`mma_asymptote`).
    df0 : numpy.ndarray
        Objective gradient at xᵏ.
    g : float
        Constraint value at xᵏ (g ≤ 0 feasible).
    dg : numpy.ndarray
        Constraint gradient at xᵏ.
    move : float
        Move limit as a fraction of (xmax − xmin).
    albefa, raa0, c, d : float
        MMA constants (defaults 0.1, 1e-5, 1000, 1).
    tol : float
        Relative bisection tolerance on λ.

    Returns
    -------
    x_new : numpy.ndarray
        Subproblem solution.
    lam : float
        Dual multiplier λ.
    y : float
        Artificial variable y = max(0, (λ − c)/d).

    Raises
    ------
    RuntimeError
        If no upper bracket for λ is found.

    Notes
    -----
    Approximations (constants omitted)::

        f̃₀(x) = Σ p₀ⱼ/(uⱼ − xⱼ) + q₀ⱼ/(xⱼ − lⱼ),   g̃(x) = Σ p₁ⱼ/(uⱼ − xⱼ) + q₁ⱼ/(xⱼ − lⱼ) − b
        p = (u − xᵏ)² [(∂f)⁺ + 0.001 |∂f| + raa0/(xmax − xmin)],  q = (xᵏ − l)² [(∂f)⁻ + …]
        αⱼ = max(xmin, l + albefa (x − l), x − move (xmax − xmin)),  βⱼ analogous

    Standard form (a₀ = 1, a = 0, z = 0): min f̃₀ + c y + ½ d y² s.t. g̃ − y ≤ 0, y ≥ 0.
    Dual: x(λ) is closed-form per j, xⱼ = (lⱼ√Pⱼ + uⱼ√Qⱼ)/(√Pⱼ + √Qⱼ) clipped to [αⱼ, βⱼ];
    y(λ) = max(0, (λ − c)/d). The dual derivative g̃(x(λ)) − y(λ) decreases in λ → bisection.
    The coefficients (0.001, raa0 = 1e-5, albefa = 0.1, c = 1000, d = 1) were read from Deetman's
    Python port (mmapy) of Svanberg's 2007 code, where the subproblem is solved by an interior-point
    method; with m = 1 a one-dimensional dual suffices.
    """
    dx = np.maximum(xmax - xmin, 1e-5)
    alpha = np.maximum(np.maximum(low + albefa * (x - low), x - move * (xmax - xmin)), xmin)
    beta = np.minimum(np.minimum(upp - albefa * (upp - x), x + move * (xmax - xmin)), xmax)
    ux, xl = upp - x, x - low

    def pq(df: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """MMA coefficients p, q of one function."""
        p, q = np.maximum(df, 0.0), np.maximum(-df, 0.0)
        e = 0.001 * (p + q) + raa0 / dx
        return (p + e) * ux ** 2, (q + e) * xl ** 2

    p0, q0 = pq(df0)
    p1, q1 = pq(dg)
    b = np.sum(p1 / ux + q1 / xl) - g

    def x_lam(lam: float) -> np.ndarray:
        """Primal minimizer x(λ) of the Lagrangian."""
        P, Q = p0 + lam * p1, q0 + lam * q1
        sP, sQ = np.sqrt(P), np.sqrt(Q)
        return np.clip((low * sP + upp * sQ) / (sP + sQ), alpha, beta)

    def derivative(lam: float) -> float:
        """Derivative of the dual function at λ."""
        xl_ = x_lam(lam)
        return np.sum(p1 / (upp - xl_) + q1 / (xl_ - low)) - b - max(0.0, (lam - c) / d)

    if derivative(0.0) <= 0:
        return x_lam(0.0), 0.0, 0.0
    lo, hi = 0.0, 1.0
    while derivative(hi) > 0:
        lo, hi = hi, 2 * hi
        if hi > 1e300:
            raise RuntimeError("MMA dual: no upper bound for λ found")
    for _ in range(2000):
        middle = 0.5 * (lo + hi)
        if derivative(middle) > 0:
            lo = middle
        else:
            hi = middle
        if hi - lo <= tol * max(1.0, hi):
            break
    lam = 0.5 * (lo + hi)
    return x_lam(lam), lam, max(0.0, (lam - c) / d)


# =====================================================================================
# main loop
# =====================================================================================
@cite("sigmund_2007", note="measure of non-discreteness M_nd")
def gray_measure(xphys: np.ndarray) -> float:
    """Measure of non-discreteness ``M_nd = Σ 4 x̄(1 − x̄) / n × 100 %``.

    Parameters
    ----------
    xphys : array_like
        Physical densities.

    Returns
    -------
    float
        M_nd in percent (0 for a 0/1 design, 100 for x̄ = 0.5 everywhere).

    Examples
    --------
    >>> gray_measure(np.array([0.25, 1.0]))
    37.5
    """
    x = np.asarray(xphys, dtype=float).ravel()
    return float(100.0 * np.sum(4 * x * (1 - x)) / x.size)


@cite("andreassen_2011", "sigmund_2007", "bendsoe_1989", note="top88 main loop, lines 45-88; §5.4 for ft = 3")
def topopt(problem: Problem, volume: float, rmin: float, ft: int = 1, optimizer: str = "OC", move: float = 0.2,
           tol: float = 0.01, max_iter: int = 1000, x0: Any = None, beta0: float = 1.0, beta_max: float = 512.0,
           beta_step: int = 50, mma_settings: dict[str, float] | None = None,
           verbose: bool = False) -> dict[str, Any]:
    """SIMP compliance minimization (top88 main loop).

    Parameters
    ----------
    problem : Problem
        Grid, loads, supports, passive elements and material.
    volume : float
        Volume fraction V* (bound on the mean of x̄), 0 < V* ≤ 1.
    rmin : float
        Filter radius (element sizes).
    ft : int
        Filter type 0-3 (see module notes).
    optimizer : {"OC", "MMA"}
        Update scheme.
    move : float
        Move limit, 0 < move ≤ 1. For MMA it is the subproblem move limit (multiplied by
        xmax − xmin = 1).
    tol : float
        Stopping tolerance on max|xᵏ⁺¹ − xᵏ| (top88: 0.01).
    max_iter : int
        Maximum number of iterations.
    x0 : array_like, optional
        Initial design (scalar, density array or element vector).
    beta0, beta_max : float
        Initial and maximum Heaviside β (ft = 3).
    beta_step : int
        Iterations per β level (ft = 3).
    mma_settings : dict, optional
        Overrides of the MMA constants ``move``, ``albefa``, ``raa0``, ``c``, ``d``, ``asyinit``,
        ``asydecr``, ``asyincr``.
    verbose : bool
        Print one top88-style line per iteration.

    Returns
    -------
    dict
        ``x``, ``xfiz``
            final design and physical density arrays (shape of :meth:`_Grid.to_array`);
        ``compliance``
            history; ``compliance[k]`` is the compliance of the design analysed at iteration k
            (top88 "Obj.");
        ``volume``
            mean x̄ of the same designs (``volume[k] = V(x̄ᵏ)``);
        ``volume_new``
            mean x̄ after each update (top88 "Vol.");
        ``change``
            max|Δx| history (top88 "ch."); ``beta``: β history (ft = 3);
        ``iteration``, ``converged``, ``gray`` (M_nd % of the final x̄), ``compliance_final``
            (compliance of the final x̄, analysed separately), ``U`` (its displacements),
            ``beta_final``, ``ft``, ``optimizer``.

    Raises
    ------
    ValueError
        For an invalid volume, optimizer, move limit, ``ft`` or ``rmin``.

    Notes
    -----
    With MMA the objective is c/c₀ (c₀ = compliance at the first iteration) and the constraint
    Σx̄/(V* n) − 1 ≤ 0. With ft = 1 MMA does not use a consistent gradient (filtered
    sensitivities) and is heuristic. For ft = 3, β is doubled every ``beta_step`` iterations or
    when the change falls to ``tol``, until ``beta_max``.

    Examples
    --------
    >>> r = topopt(mbb_half(12, 4), 0.5, 1.5, max_iter=3)
    >>> r["xfiz"].shape
    (4, 12)
    """
    grid = problem.grid
    if not 0 < volume <= 1:
        raise ValueError("0 < volume ≤ 1 is required")
    if optimizer not in ("OC", "MMA"):
        raise ValueError("optimizer: OC | MMA")
    if not 0 < move <= 1:
        raise ValueError("0 < move ≤ 1 is required")
    dens = Density(grid, rmin, ft, problem.passive)
    passive = problem.passive
    nel = grid.nel
    if x0 is None:
        # top88: x = volfrac. With passive elements the active ones are initialised so that
        # Σx̄ = V*·n (an extension of this module; identical to top88 without passive elements).
        n_active, n_filled = int(np.sum(passive == 0)), int(np.sum(passive == 2))
        x_start = (volume * nel - n_filled) / n_active if (n_active and (passive > 0).any()) else volume
        x = np.full(nel, float(min(max(x_start, 0.0), 1.0)))
    else:
        x = grid.vector(x0)
    x[passive == 1] = 0.0
    x[passive == 2] = 1.0
    beta = float(beta0)
    if ft == 3:
        xphys = dens._apply_passive(1 - np.exp(-beta * x) + x * math.exp(-beta))   # top88 §5.4: x̃ = x
    else:
        xphys = dens.physical(x, beta)
    history: dict[str, list[float]] = {"compliance": [], "volume": [], "volume_new": [], "change": [], "beta": []}
    active = np.flatnonzero(passive == 0)
    mma = dict(move=move, albefa=0.1, raa0=1e-5, c=1000.0, d=1.0, asyinit=0.5, asydecr=0.7, asyincr=1.2)
    mma.update(mma_settings or {})
    xold1 = xold2 = low = upp = None
    c0 = None
    loop = loopbeta = 0
    change = 1.0
    while change > tol and loop < max_iter:
        loop += 1
        loopbeta += 1
        c, dcf, _ = problem.analysis(xphys)
        history["compliance"].append(c)
        history["volume"].append(float(xphys.mean()))
        history["beta"].append(beta)
        if ft == 1:
            dc = dens.sensitivity_filter(x, dens.chain_rule(x, dcf, beta))
            dv = np.ones(nel)
            dv[passive > 0] = 0.0
        else:
            dc = dens.chain_rule(x, dcf, beta)
            dv = dens.chain_rule(x, np.ones(nel), beta)
        if optimizer == "OC":
            xnew, xphys, _ = update_oc(x, dc, np.where(dv > 0, dv, 1.0), volume, move,
                                       partial(dens.physical, beta=beta), nel, passive)
        else:
            if c0 is None:
                c0 = c
            xa = x[active]
            if xold1 is None or xold2 is None:
                xold1, xold2 = xa.copy(), xa.copy()
            lo_, hi_ = np.zeros_like(xa), np.ones_like(xa)
            low, upp = mma_asymptote(loop, xa, xold1, xold2, low, upp, lo_, hi_,
                                     mma["asyinit"], mma["asydecr"], mma["asyincr"])
            g = float(xphys.sum()) / (volume * nel) - 1.0
            xa_new, _, _ = mma_subproblem(xa, lo_, hi_, low, upp, dc[active] / c0, g,
                                          dv[active] / (volume * nel), mma["move"], mma["albefa"],
                                          mma["raa0"], mma["c"], mma["d"])
            xold2, xold1 = xold1, xa.copy()
            xnew = x.copy()
            xnew[active] = xa_new
            xphys = dens.physical(xnew, beta)
        change = float(np.max(np.abs(xnew - x)))
        x = xnew
        history["volume_new"].append(float(xphys.mean()))
        history["change"].append(change)
        if verbose:
            print(f" It.:{loop:5d} Obj.:{c:11.4f} Vol.:{xphys.mean():7.3f} ch.:{change:7.3f}")
        if ft == 3 and beta < beta_max and (loopbeta >= beta_step or change <= tol):
            beta *= 2
            loopbeta = 0
            change = 1.0
    c_final, _, U_final = problem.analysis(xphys)
    result: dict[str, Any] = {k: np.array(v) for k, v in history.items()}
    result.update(x=grid.to_array(x), xfiz=grid.to_array(xphys), iteration=loop, converged=change <= tol,
                  gray=gray_measure(xphys), compliance_final=c_final, U=U_final, beta_final=beta, ft=ft,
                  optimizer=optimizer)
    return result


@cite("andreassen_2011", note="top88 calling convention")
def top88(nelx: int, nely: int, volfrac: float, penal: float, rmin: float, ft: int, **kw: Any) -> dict[str, Any]:
    """``top88(nelx, nely, volfrac, penal, rmin, ft)`` — half MBB beam, same call as in the paper.

    Parameters
    ----------
    nelx, nely : int
        Grid size.
    volfrac : float
        Volume fraction V*.
    penal : float
        SIMP penalty p.
    rmin : float
        Filter radius.
    ft : int
        Filter type (1 sensitivity, 2 density, 3 Heaviside; 0 none).
    **kw
        Passed to :func:`topopt`.

    Returns
    -------
    dict
        See :func:`topopt`.
    """
    return topopt(mbb_half(nelx, nely, penalty=penal), volfrac, rmin, ft=ft, **kw)


# =====================================================================================
# ready-made problems
# =====================================================================================
@cite("andreassen_2011", note="top88, lines 19-23")
def mbb_half(nelx: int, nely: int, P: float = 1.0, nu: float = 0.3, **kw: Any) -> Problem:
    """Half MBB beam (symmetry model).

    Load −P (downwards) at the top-left corner; x DOFs of the left edge fixed (symmetry);
    y DOF of the bottom-right corner fixed (roller).

    Parameters
    ----------
    nelx, nely : int
        Grid size.
    P : float
        Load magnitude.
    nu : float
        Poisson's ratio.
    **kw
        Passed to :class:`Problem` (``passive``, ``penalty``, ``E0``, ``Emin``).

    Returns
    -------
    Problem
    """
    grid = Grid2D(nelx, nely, nu)
    fixed = [grid.dof(0, iy, 0) for iy in range(grid.nely + 1)] + [grid.dof(grid.nelx, 0, 1)]
    return Problem(grid, {grid.dof(0, grid.nely, 1): -P}, fixed, **kw)


def mbb_full(nelx: int, nely: int, P: float = 2.0, nu: float = 0.3, **kw: Any) -> Problem:
    """Full MBB beam: −P at the top-centre node, bottom-left corner (x, y) and bottom-right (y) supported.

    With P = 2 each half carries the P = 1 load of the half model, so c_full = 2 c_half for a
    mirror-symmetric design.

    Parameters
    ----------
    nelx, nely : int
        Grid size (``nelx`` even).
    P : float
        Load magnitude.
    nu : float
        Poisson's ratio.
    **kw
        Passed to :class:`Problem`.

    Returns
    -------
    Problem

    Raises
    ------
    ValueError
        If ``nelx`` is odd.
    """
    if nelx % 2:
        raise ValueError("the full MBB beam requires an even nelx")
    grid = Grid2D(nelx, nely, nu)
    fixed = [grid.dof(0, 0, 0), grid.dof(0, 0, 1), grid.dof(grid.nelx, 0, 1)]
    return Problem(grid, {grid.dof(grid.nelx // 2, grid.nely, 1): -P}, fixed, **kw)


@cite("andreassen_2011", note="top88 §5.1")
def cantilever(nelx: int, nely: int, P: float = 1.0, load: str = "lower", nu: float = 0.3, **kw: Any) -> Problem:
    """Cantilever beam: left edge clamped (all DOFs), −P on the right edge.

    Parameters
    ----------
    nelx, nely : int
        Grid size.
    P : float
        Load magnitude.
    load : {"lower", "middle"}
        "lower": bottom-right corner (top88 §5.1 load); "middle": mid-height of the right edge
        (``nely`` even).
    nu : float
        Poisson's ratio.
    **kw
        Passed to :class:`Problem`.

    Returns
    -------
    Problem

    Raises
    ------
    ValueError
        For an unknown ``load`` or an odd ``nely`` with ``load="middle"``.

    Notes
    -----
    top88 §5.1 uses ``fixeddofs = [1:2*nely+1]``, which leaves the y DOF of the bottom-left node
    free; here the whole left edge is clamped.
    """
    grid = Grid2D(nelx, nely, nu)
    if load == "lower":
        iy = 0
    elif load == "middle":
        if grid.nely % 2:
            raise ValueError("load='middle' requires an even nely")
        iy = grid.nely // 2
    else:
        raise ValueError("load: lower | middle")
    fixed = [grid.dof(0, j, k) for j in range(grid.nely + 1) for k in (0, 1)]
    return Problem(grid, {grid.dof(grid.nelx, iy, 1): -P}, fixed, **kw)


@cite("andreassen_2011", note="top88 §5.2")
def cantilever_two_load(nelx: int, nely: int, P: float = 1.0, nu: float = 0.3, **kw: Any) -> Problem:
    """Cantilever with two load cases: +P (y) at the top-right and −P (y) at the bottom-right corner.

    Parameters
    ----------
    nelx, nely : int
        Grid size.
    P : float
        Load magnitude.
    nu : float
        Poisson's ratio.
    **kw
        Passed to :class:`Problem`.

    Returns
    -------
    Problem
        Left edge clamped; two load columns.
    """
    grid = Grid2D(nelx, nely, nu)
    fixed = [grid.dof(0, j, k) for j in range(grid.nely + 1) for k in (0, 1)]
    return Problem(grid, [{grid.dof(grid.nelx, grid.nely, 1): P}, {grid.dof(grid.nelx, 0, 1): -P}], fixed, **kw)


@cite("andreassen_2011", note="multiple load cases and passive elements as in top88 §5.2-5.3; geometry defined here")
def pin_link(nelx: int, nely: int, bore_radius: float, ring: float,
             cases: Sequence[tuple[float, float]] = ((1.0, 0.0), (-1.0, 0.0), (0.0, -0.3)), P: float = 1.0,
             nu: float = 0.3, **kw: Any) -> Problem:
    """Two-pin link (lug-to-lug fitting): bores centred half a height in from each end on the mid-line.

    The bores are passive voids, a ``ring`` of solid (passive) material surrounds each, the nodes on the left bore
    edge are clamped (the fixed pin) and each load case ``(fx, fy)`` × ``P`` is a bearing load spread equally over
    the right-bore edge nodes on the side the load points to (a pin pushes on the half of the bore facing its
    motion). Several cases make one design carry tension, compression and side load (Σ compliance, top88 §5.2).

    Parameters
    ----------
    nelx, nely : int
        Grid size; ``nelx > 2 nely`` leaves room between the bores.
    bore_radius, ring : float
        Bore radius and protected ring width, in elements.
    cases : sequence of (fx, fy)
        Load direction and size per case, as fractions of ``P``.
    """
    if not 0 < bore_radius < nely / 2 - ring or ring < 1:
        raise ValueError("need 0 < bore_radius < nely/2 - ring and ring >= 1 element")
    if not nelx > 2 * nely:
        raise ValueError("need nelx > 2 nely so the bores do not overlap")
    if not cases:
        raise ValueError("at least one load case")
    grid = Grid2D(nelx, nely, nu)
    cy = nely / 2.0
    centres = (np.array([cy, cy]), np.array([nelx - cy, cy]))
    m = grid.element_center()
    passive = np.zeros(grid.nel, dtype=int)
    for c in centres:
        d = np.hypot(*(m - c).T)
        passive[(d >= bore_radius) & (d < bore_radius + ring)] = 2
        passive[d < bore_radius] = 1
    # bore-edge nodes: r - 0.5 <= d keeps every chosen node touching a ring element (its outermost neighbouring
    # element centre is at least 0.5 further out), so no loaded or fixed node floats among void elements
    edge = []
    for c in centres:
        d = np.hypot(*(grid.X - c).T)
        edge.append(np.flatnonzero((d >= bore_radius - 0.5) & (d <= bore_radius + 0.75)))
    if min(e.size for e in edge) < 4:
        raise ValueError("bore too small for the mesh: fewer than 4 edge nodes")
    fixed = [2 * n + k for n in edge[0] for k in (0, 1)]
    loads = []
    for fx, fy in cases:
        u = np.array([fx, fy], float)
        if not np.any(u):
            raise ValueError("a load case must not be zero")
        side = edge[1][(grid.X[edge[1]] - centres[1]) @ u > 0]
        f: dict[int, float] = {}
        for n in side:
            f[2 * int(n)] = f.get(2 * int(n), 0.0) + P * fx / side.size
            f[2 * int(n) + 1] = f.get(2 * int(n) + 1, 0.0) + P * fy / side.size
        loads.append(f)
    return Problem(grid, loads, fixed, passive=passive, **kw)


@cite("le_norato_2010", note="common L-bracket geometry; load position defined here, not taken from a source")
def l_bracket(n: int, P: float = 1.0, ratio: float = 0.4, nu: float = 0.3, **kw: Any) -> Problem:
    """L-bracket on an n × n domain.

    The upper-right region (x > ratio·n, y > ratio·n) is a passive void; the part x ≤ ratio·n of the
    top edge is clamped; −P acts at the tip of the arm (x = n, y = round(ratio·n)).

    Parameters
    ----------
    n : int
        Domain size in elements.
    P : float
        Load magnitude.
    ratio : float
        Arm width as a fraction of n.
    nu : float
        Poisson's ratio.
    **kw
        Passed to :class:`Problem` (``passive`` is set here).

    Returns
    -------
    Problem

    Notes
    -----
    A geometry common in the literature (e.g. Le et al. 2010, stress-based TO); the load position
    was not read from a source in this repository and is defined as above.
    """
    grid = Grid2D(n, n, nu)
    m = grid.element_center()
    a = ratio * n
    passive = np.where((m[:, 0] > a) & (m[:, 1] > a), 1, 0)
    arm = int(round(a))
    fixed = [grid.dof(ix, n, k) for ix in range(arm + 1) for k in (0, 1)]
    return Problem(grid, {grid.dof(n, arm, 1): -P}, fixed, passive=passive, **kw)


@cite("liu_tovar_2014", note="resembles the top3d default example; paper not read")
def cantilever_3d(nelx: int, nely: int, nelz: int, P: float = 1.0, nu: float = 0.3, **kw: Any) -> Problem:
    """3-D cantilever: face x = 0 clamped; total −P (y) along the edge x = nelx, y = 0.

    The load is split equally among the nodes of that edge.

    Parameters
    ----------
    nelx, nely, nelz : int
        Grid size.
    P : float
        Total load.
    nu : float
        Poisson's ratio.
    **kw
        Passed to :class:`Problem`.

    Returns
    -------
    Problem
    """
    grid = Grid3D(nelx, nely, nelz, nu)
    fixed = [grid.dof(0, j, k, d) for j in range(grid.nely + 1) for k in range(grid.nelz + 1) for d in range(3)]
    load = {grid.dof(grid.nelx, 0, k, 1): -P / (grid.nelz + 1) for k in range(grid.nelz + 1)}
    return Problem(grid, load, fixed, **kw)


# =====================================================================================
# post-processing
# =====================================================================================
def binarize(xphys: np.ndarray, threshold: float = 0.5, keep_volume: bool = False,
             problem: Problem | None = None) -> dict[str, Any]:
    """Threshold a density field into a black-and-white structure.

    Parameters
    ----------
    xphys : array_like
        Physical densities (any shape).
    threshold : float
        x̄ > threshold is solid.
    keep_volume : bool
        If True the threshold is chosen so that the solid fraction equals the mean of x̄ (rounded
        to the nearest whole number of elements): the k densest elements are solid.
    problem : Problem, optional
        If given, the compliance of the thresholded structure (solid 1, void Emin) is computed.

    Returns
    -------
    dict
        ``structure`` (bool array), ``threshold``, ``area`` (number of solid elements = area (2-D) /
        volume (3-D) of unit elements), ``ratio`` (solid fraction), ``compliance`` (or None).

    Examples
    --------
    >>> binarize(np.array([[0.1, 0.6, 0.9], [0.5, 0.7, 0.2]]))["area"]
    3.0
    """
    a = np.asarray(xphys, dtype=float)
    v = a.ravel()
    if keep_volume:
        k = int(round(v.mean() * v.size))
        order = np.argsort(-v, kind="stable")
        filled = np.zeros(v.size, dtype=bool)
        filled[order[:k]] = True
        threshold = float(v[order[k - 1]]) if k > 0 else 1.0
        structure = filled.reshape(a.shape)
    else:
        structure = a > threshold
    area = int(structure.sum())
    result: dict[str, Any] = {"structure": structure, "threshold": float(threshold), "area": float(area),
                              "ratio": area / v.size, "compliance": None}
    if problem is not None:
        xb = problem.grid.vector(structure.astype(float))
        xb[problem.passive == 1] = 0.0
        xb[problem.passive == 2] = 1.0
        result["compliance"] = problem.analysis(xb)[0]
    return result
