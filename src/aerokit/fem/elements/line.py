"""One-dimensional elements: :class:`Bar` (truss), :class:`Frame2D` (Euler-Bernoulli) and :class:`Frame3D`.

Stiffness, consistent mass and geometric stiffness matrices follow Przemieniecki (1968) and
Cook, Malkus, Plesha & Witt (2002), Ch. 2, 11 and 18 [przemieniecki_1968]_ [cook_2002]_.

Sign convention: axial force ``N`` positive in tension; end forces are reported in element
(local) axes.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.references import cite

__all__ = ["Bar", "Frame2D", "Frame3D"]


def _length_direction(X: np.ndarray, i: int, j: int) -> tuple[float, np.ndarray]:
    """Length and unit direction vector of the element ``i → j``."""
    d = X[j] - X[i]
    L = float(np.linalg.norm(d))
    if L <= 0:
        raise ValueError("element has zero length")
    return L, d / L


@cite("przemieniecki_1968", "cook_2002", note="truss element; geometric stiffness Cook et al. Ch. 18")
class Bar:
    """Two-node axial bar (truss member).

    Parameters
    ----------
    i, j : int
        End node indices.
    E : float
        Young's modulus [Pa].
    A : float
        Cross-sectional area [m²].
    rho : float
        Density [kg/m³].
    dim : int
        Spatial dimension and DOFs per node: 2 (plane truss) or 3 (space truss).

    Notes
    -----
    ``k = EA/L [[eeᵀ, −eeᵀ], [−eeᵀ, eeᵀ]]`` with the unit axis ``e``; consistent mass
    ``ρAL/6 [[2I, I], [I, 2I]]``; lumped mass ``ρAL/2 I``.
    """

    def __init__(self, i: int, j: int, E: float, A: float, rho: float = 0.0, dim: int = 2) -> None:
        if dim not in (2, 3):
            raise ValueError("Bar dim must be 2 or 3")
        self.nodes = [i, j]
        self.E, self.A, self.rho = E, A, rho
        self.ndof = dim

    def _T(self, X: np.ndarray) -> tuple[float, np.ndarray]:
        L, e = _length_direction(X, *self.nodes)
        return L, e[:self.ndof]

    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness matrix in global axes, shape ``(2·dim, 2·dim)`` [N/m]."""
        L, e = self._T(X)
        ee = np.outer(e, e)
        return self.E * self.A / L * np.block([[ee, -ee], [-ee, ee]])

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Consistent (``ρAL/6 [[2I, I], [I, 2I]]``) or lumped (``ρAL/2 I``) mass [kg]."""
        L, _ = self._T(X)
        I = np.eye(self.ndof)
        mt = self.rho * self.A * L
        if lumped:
            return mt / 2 * np.eye(2 * self.ndof)
        return mt / 6 * np.block([[2 * I, I], [I, 2 * I]])

    def axial_force(self, X: np.ndarray, ue: np.ndarray) -> float:
        """Axial force ``N = EA/L · eᵀ(u_j − u_i)`` [N] (tension positive)."""
        L, e = self._T(X)
        elongation = e @ (ue[self.ndof:] - ue[:self.ndof])
        return float(self.E * self.A / L * elongation)

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Geometric stiffness ``N/L [[P, −P], [−P, P]]`` with ``P = I − eeᵀ`` (``N`` tension positive)."""
        L, e = self._T(X)
        N = self.axial_force(X, ue)
        P = np.eye(self.ndof) - np.outer(e, e)
        return N / L * np.block([[P, -P], [-P, P]])

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Return ``{"N": axial force [N], "sigma": N/A [Pa]}``."""
        N = self.axial_force(X, ue)
        return {"N": N, "sigma": N / self.A}


@cite("przemieniecki_1968", "cook_2002", note="plane frame: Euler-Bernoulli bending + axial; Ch. 18 K_G")
class Frame2D:
    """Plane frame element: axial + Euler-Bernoulli bending, DOFs ``(u, v, θz)`` per node.

    Parameters
    ----------
    i, j : int
        End node indices.
    E : float
        Young's modulus [Pa].
    A : float
        Cross-sectional area [m²].
    I : float
        Second moment of area about the bending axis [m⁴].
    rho : float
        Density [kg/m³].
    q : float
        Uniformly distributed load [N/m] in the element's local y direction (positive towards local
        +y); added to the model as equivalent nodal loads by :meth:`body_force`.

    Notes
    -----
    Cubic Hermite bending; consistent mass ``ρAL/420 [...]``; geometric stiffness
    ``N/(30L) [...]`` from the same cubic shape functions.
    """

    ndof = 3

    def __init__(self, i: int, j: int, E: float, A: float, I: float, rho: float = 0.0, q: float = 0.0) -> None:
        self.nodes = [i, j]
        self.E, self.A, self.I, self.rho, self.q = E, A, I, rho, q

    def _T(self, X: np.ndarray) -> tuple[float, np.ndarray]:
        L, e = _length_direction(X, *self.nodes)
        c, s = e[0], e[1]
        R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T = np.zeros((6, 6))
        T[:3, :3] = R
        T[3:, 3:] = R
        return L, T

    def k_local(self, L: float) -> np.ndarray:
        """Stiffness in local axes ``(u₁, v₁, θ₁, u₂, v₂, θ₂)`` for length ``L`` [m]."""
        E, A, I = self.E, self.A, self.I
        a, b = E * A / L, E * I / L ** 3
        return np.array([
            [a, 0, 0, -a, 0, 0],
            [0, 12 * b, 6 * L * b, 0, -12 * b, 6 * L * b],
            [0, 6 * L * b, 4 * L * L * b, 0, -6 * L * b, 2 * L * L * b],
            [-a, 0, 0, a, 0, 0],
            [0, -12 * b, -6 * L * b, 0, 12 * b, -6 * L * b],
            [0, 6 * L * b, 2 * L * L * b, 0, -6 * L * b, 4 * L * L * b]])

    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness in global axes ``Tᵀ k_local T`` (6 × 6)."""
        L, T = self._T(X)
        return T.T @ self.k_local(L) @ T

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Consistent mass (``ρAL/420`` cubic Hermite) or lumped translational mass [kg]."""
        L, T = self._T(X)
        mt = self.rho * self.A * L
        if lumped:
            return mt / 2 * np.diag([1, 1, 0, 1, 1, 0])
        c = mt / 420
        my = c * np.array([
            [140, 0, 0, 70, 0, 0],
            [0, 156, 22 * L, 0, 54, -13 * L],
            [0, 22 * L, 4 * L * L, 0, 13 * L, -3 * L * L],
            [70, 0, 0, 140, 0, 0],
            [0, 54, 13 * L, 0, 156, -22 * L],
            [0, -13 * L, -3 * L * L, 0, -22 * L, 4 * L * L]])
        return T.T @ my @ T

    def internal_forces(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Local end forces ``[N₁, V₁, M₁, N₂, V₂, M₂]`` acting on the element (distributed load included).

        Parameters
        ----------
        X : ndarray
            Nodal coordinates [m].
        ue : ndarray, shape (6,)
            Element displacements in global axes.

        Returns
        -------
        ndarray, shape (6,)
            ``k_local T uₑ − f_q`` [N, N·m].
        """
        L, T = self._T(X)
        return self.k_local(L) @ (T @ ue) - self._q_local(L)

    def _q_local(self, L: float) -> np.ndarray:
        q = self.q
        return np.array([0, q * L / 2, q * L * L / 12, 0, q * L / 2, -q * L * L / 12])

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Equivalent nodal loads of the distributed load ``q`` in global axes (fixed-end forces)."""
        L, T = self._T(X)
        return T.T @ self._q_local(L)

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Geometric stiffness from the cubic bending shape functions (axial force tension positive)."""
        L, T = self._T(X)
        N = -self.internal_forces(X, ue)[0]       # minus the axial end force at node 1 = tension
        g = N / (30 * L) * np.array([
            [0, 0, 0, 0, 0, 0],
            [0, 36, 3 * L, 0, -36, 3 * L],
            [0, 3 * L, 4 * L * L, 0, -3 * L, -L * L],
            [0, 0, 0, 0, 0, 0],
            [0, -36, -3 * L, 0, 36, -3 * L],
            [0, 3 * L, -L * L, 0, -3 * L, 4 * L * L]])
        return T.T @ g @ T

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Section forces: ``N`` (tension +), shear ``V1``/``V2``, moments ``M1``/``M2`` and ``end_forces``."""
        f = self.internal_forces(X, ue)
        return {"N": -f[0], "V1": f[1], "M1": -f[2], "V2": -f[4], "M2": f[5], "end_forces": f}


@cite("przemieniecki_1968", note="space frame element stiffness and consistent mass")
class Frame3D:
    """Space frame element, DOFs ``(u, v, w, θx, θy, θz)`` per node.

    Parameters
    ----------
    i, j : int
        End node indices.
    E, G : float
        Young's and shear moduli [Pa].
    A : float
        Area [m²].
    Iy, Iz : float
        Second moments of area about the local y and z axes [m⁴].
    J : float
        Torsion constant [m⁴].
    rho : float
        Density [kg/m³].
    ref : array_like, shape (3,)
        Reference vector defining the local x-y plane (should be close to local y).

    Notes
    -----
    Local axes: ``x = i → j``, ``z = x × ref``, ``y = z × x``. Uncoupled axial, torsion and the two
    Euler-Bernoulli bending blocks (``θy = −dw/dx`` sign convention in the x-z plane).
    """

    ndof = 6

    def __init__(self, i: int, j: int, E: float, G: float, A: float, Iy: float, Iz: float, J: float,
                 rho: float = 0.0, ref: ArrayLike = (0.0, 0.0, 1.0)) -> None:
        self.nodes = [i, j]
        self.E, self.G, self.A, self.Iy, self.Iz, self.J, self.rho = E, G, A, Iy, Iz, J, rho
        self.ref = np.asarray(ref, dtype=float)

    def _T(self, X: np.ndarray) -> tuple[float, np.ndarray]:
        L, ex = _length_direction(X, *self.nodes)
        ez = np.cross(ex, self.ref)
        if np.linalg.norm(ez) < 1e-8:
            raise ValueError("reference vector is parallel to the element axis")
        ez /= np.linalg.norm(ez)
        ey = np.cross(ez, ex)
        R = np.vstack([ex, ey, ez])
        T = np.zeros((12, 12))
        for b in range(4):
            T[3 * b:3 * b + 3, 3 * b:3 * b + 3] = R
        return L, T

    def k_local(self, L: float) -> np.ndarray:
        """Stiffness in local axes (12 × 12) for length ``L`` [m]."""
        E, G, A, Iy, Iz, J = self.E, self.G, self.A, self.Iy, self.Iz, self.J
        k = np.zeros((12, 12))
        a = E * A / L
        t = G * J / L
        k[np.ix_([0, 6], [0, 6])] = a * np.array([[1, -1], [-1, 1]])
        k[np.ix_([3, 9], [3, 9])] = t * np.array([[1, -1], [-1, 1]])
        # bending in the x-y plane (Iz): v, θz → DOFs 1, 5, 7, 11
        bz = E * Iz / L ** 3
        kz = bz * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                            [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
        k[np.ix_([1, 5, 7, 11], [1, 5, 7, 11])] = kz
        # bending in the x-z plane (Iy): w, θy → DOFs 2, 4, 8, 10 (sign change from θy = −dw/dx)
        by = E * Iy / L ** 3
        ky = by * np.array([[12, -6 * L, -12, -6 * L], [-6 * L, 4 * L * L, 6 * L, 2 * L * L],
                            [-12, 6 * L, 12, 6 * L], [-6 * L, 2 * L * L, 6 * L, 4 * L * L]])
        k[np.ix_([2, 4, 8, 10], [2, 4, 8, 10])] = ky
        return k

    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness in global axes (12 × 12)."""
        L, T = self._T(X)
        return T.T @ self.k_local(L) @ T

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Consistent mass (cubic Hermite bending, linear axial/torsion) or lumped mass [kg]."""
        L, T = self._T(X)
        mt = self.rho * self.A * L
        if lumped:
            Ip = (self.Iy + self.Iz) / self.A
            d = np.array([1, 1, 1, Ip, 0, 0] * 2) * mt / 2
            return np.diag(d)
        m = np.zeros((12, 12))
        m[np.ix_([0, 6], [0, 6])] = mt / 6 * np.array([[2, 1], [1, 2]])
        Ip = (self.Iy + self.Iz) / self.A
        m[np.ix_([3, 9], [3, 9])] = mt * Ip / 6 * np.array([[2, 1], [1, 2]])
        c = mt / 420
        mz = c * np.array([[156, 22 * L, 54, -13 * L], [22 * L, 4 * L * L, 13 * L, -3 * L * L],
                           [54, 13 * L, 156, -22 * L], [-13 * L, -3 * L * L, -22 * L, 4 * L * L]])
        m[np.ix_([1, 5, 7, 11], [1, 5, 7, 11])] = mz
        my = c * np.array([[156, -22 * L, 54, 13 * L], [-22 * L, 4 * L * L, -13 * L, -3 * L * L],
                           [54, -13 * L, 156, 22 * L], [13 * L, -3 * L * L, 22 * L, 4 * L * L]])
        m[np.ix_([2, 4, 8, 10], [2, 4, 8, 10])] = my
        return T.T @ m @ T

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Not available.

        Raises
        ------
        NotImplementedError
            Always; use :class:`Frame2D` for buckling.
        """
        raise NotImplementedError("Frame3D has no geometric stiffness; use Frame2D for buckling")

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Axial force ``N`` (tension +), torque ``T`` and local ``end_forces`` (12,)."""
        L, T = self._T(X)
        f = self.k_local(L) @ (T @ ue)
        return {"N": -f[0], "T": -f[3], "end_forces": f}

