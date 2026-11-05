"""MITC4 Mindlin-Reissner plate element (Bathe & Dvorkin 1985, Int. J. Numer. Methods Eng. 21:367).

DOFs (``ndof = 3``): ``(w, βx, βy)``; through the thickness ``u = z·βx``, ``v = z·βy``. In the thin-plate
limit ``βx = −∂w/∂x`` and ``βy = −∂w/∂y``.

Bending
    ``κ = [βx,x, βy,y, βx,y + βy,x]``, ``M = D_b κ``,
    ``D_b = E h³/(12(1−ν²)) [[1, ν, 0], [ν, 1, 0], [0, 0, (1−ν)/2]]``.
Transverse shear
    ``γ = [w,x + βx, w,y + βy]``, ``Q = κs G h γ`` (``κs = 5/6``).
MITC4 assumed covariant shear
    ``γ_ξ`` is sampled at ``ξ = 0, η = ±1`` and ``γ_η`` at ``η = 0, ξ = ±1`` and interpolated
    linearly, which removes shear locking without spurious zero-energy modes.
Pre-stress
    In-plane membrane forces ``(Nx, Ny, Nxy)`` [N/m], tension positive, give the geometric
    stiffness used for buckling.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.fem.elements.plane import shape_q4
from aerokit.fem.quadrature import gauss2d
from aerokit.references import cite

__all__ = ["MITC4"]


@cite("timoshenko_woinowsky_1959", note="verified against the Navier series (tests/fem/test_elements_plate.py)")
@cite("bathe_dvorkin_1985", "bathe_2014", note="MITC4 assumed transverse shear strain interpolation")
class MITC4:
    """Four-node MITC4 Mindlin-Reissner plate element.

    Parameters
    ----------
    nodes : sequence of int
        Four node indices, counter-clockwise.
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio.
    h : float
        Plate thickness [m].
    rho : float
        Density [kg/m³] (mass uses ``ρh`` for ``w`` and ``ρh³/12`` for the rotations).
    q : float
        Uniform transverse pressure [Pa] (positive along +w).
    prestress : array_like, shape (3,)
        Membrane pre-stress resultants ``(Nx, Ny, Nxy)`` [N/m], tension positive, for :meth:`kg`.
    kappa : float
        Shear correction factor (default 5/6).

    Raises
    ------
    ValueError
        Wrong node count or invalid constants.
    """

    ndof = 3
    n = 4

    def __init__(self, nodes: Sequence[int], E: float, nu: float, h: float, rho: float = 0.0, q: float = 0.0,
                 prestress: ArrayLike = (0.0, 0.0, 0.0), kappa: float = 5 / 6) -> None:
        if len(nodes) != 4:
            raise ValueError("MITC4 needs 4 nodes")
        if not (E > 0 and h > 0 and -1 < nu < 0.5):
            raise ValueError("MITC4 needs E > 0, h > 0 and −1 < ν < 0.5")
        self.nodes = list(nodes)
        self.E, self.nu, self.h, self.rho, self.q = E, nu, h, rho, q
        self.N0 = np.asarray(prestress, dtype=float)
        G = E / (2 * (1 + nu))
        self.Db = E * h ** 3 / (12 * (1 - nu ** 2)) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
        self.Ds = kappa * G * h * np.eye(2)

    def _Xe(self, X: np.ndarray) -> np.ndarray:
        return X[self.nodes, :2]

    def _jacobian(self, Xe: np.ndarray, xi: float, eta: float
                  ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        N, dxi, deta = shape_q4(xi, eta)
        J = np.array([dxi @ Xe, deta @ Xe])
        detJ = float(np.linalg.det(J))
        if detJ <= 0:
            raise ValueError("MITC4: Jacobian ≤ 0 (nodes must be counter-clockwise)")
        dN = np.linalg.solve(J, np.vstack([dxi, deta]))
        return N, dN, J, detJ

    def _Bb(self, N: np.ndarray, dN: np.ndarray) -> np.ndarray:
        B = np.zeros((3, 12))
        B[0, 1::3] = dN[0]
        B[1, 2::3] = dN[1]
        B[2, 1::3] = dN[1]
        B[2, 2::3] = dN[0]
        return B

    def _covariant(self, Xe: np.ndarray, xi: float, eta: float, direction: int) -> np.ndarray:
        """Row of ``γ_ξ`` (direction 0) or ``γ_η`` (direction 1): ``∂w/∂ξᵢ + β·∂x/∂ξᵢ``."""
        N, dxi, deta = shape_q4(xi, eta)
        d = dxi if direction == 0 else deta
        tx, ty = d @ Xe
        r = np.zeros(12)
        r[0::3] = d
        r[1::3] = N * tx
        r[2::3] = N * ty
        return r

    def _Bs(self, Xe: np.ndarray, xi: float, eta: float, J: np.ndarray) -> np.ndarray:
        gA = self._covariant(Xe, 0.0, -1.0, 0)
        gC = self._covariant(Xe, 0.0, 1.0, 0)
        gB = self._covariant(Xe, 1.0, 0.0, 1)
        gD = self._covariant(Xe, -1.0, 0.0, 1)
        g_xi = 0.5 * (1 - eta) * gA + 0.5 * (1 + eta) * gC
        g_eta = 0.5 * (1 + xi) * gB + 0.5 * (1 - xi) * gD
        return np.linalg.solve(J, np.vstack([g_xi, g_eta]))   # [γxz; γyz]

    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness ``∫ (B_bᵀ D_b B_b + B_sᵀ D_s B_s) dA`` with 2 × 2 Gauss points (12 × 12)."""
        Xe = self._Xe(X)
        K = np.zeros((12, 12))
        for xi, eta, w in gauss2d(2):
            N, dN, J, detJ = self._jacobian(Xe, xi, eta)
            Bb = self._Bb(N, dN)
            Bs = self._Bs(Xe, xi, eta, J)
            K += (Bb.T @ self.Db @ Bb + Bs.T @ self.Ds @ Bs) * detJ * w
        return K

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Consistent mass (``ρh`` translational, ``ρh³/12`` rotary inertia) or its row-sum lumping."""
        Xe = self._Xe(X)
        M = np.zeros((12, 12))
        I0, I2 = self.rho * self.h, self.rho * self.h ** 3 / 12
        for xi, eta, w in gauss2d(2):
            N, _, _, detJ = self._jacobian(Xe, xi, eta)
            for j, I in ((0, I0), (1, I2), (2, I2)):
                Nj = np.zeros(12)
                Nj[j::3] = N
                M += I * np.outer(Nj, Nj) * detJ * w
        if lumped:
            return np.diag(M.sum(axis=1))
        return M

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Geometric stiffness ``∫ ∇Nᵀ [[Nx, Nxy], [Nxy, Ny]] ∇N dA`` on ``w`` from :attr:`N0`.

        The pre-stress is prescribed (``ue`` is ignored).
        """
        Nx, Ny, Nxy = self.N0
        S = np.array([[Nx, Nxy], [Nxy, Ny]])
        Xe = self._Xe(X)
        K = np.zeros((12, 12))
        for xi, eta, w in gauss2d(2):
            _, dN, _, detJ = self._jacobian(Xe, xi, eta)
            Gw = np.zeros((2, 12))
            Gw[:, 0::3] = dN
            K += Gw.T @ S @ Gw * detJ * w
        return K

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Equivalent nodal loads ``∫ N q dA`` of the pressure ``q`` [N]."""
        if self.q == 0:
            return np.zeros(12)
        Xe = self._Xe(X)
        f = np.zeros(12)
        for xi, eta, w in gauss2d(2):
            N, _, _, detJ = self._jacobian(Xe, xi, eta)
            f[0::3] += N * self.q * detJ * w
        return f

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Centroid resultants.

        Returns
        -------
        dict
            ``M`` moments [N·m/m], ``Q`` shear forces [N/m], ``kappa`` curvatures, ``gamma`` shear
            strains, ``sigma_surface = 6M/h²`` bending stress at ``z = ±h/2`` [Pa], ``x`` position.
        """
        Xe = self._Xe(X)
        N, dN, J, _ = self._jacobian(Xe, 0.0, 0.0)
        kappa = self._Bb(N, dN) @ ue
        gamma = self._Bs(Xe, 0.0, 0.0, J) @ ue
        M = self.Db @ kappa
        Q = self.Ds @ gamma
        sigma_surface = 6 * M / self.h ** 2
        return {"M": M, "Q": Q, "kappa": kappa, "gamma": gamma, "sigma_surface": sigma_surface,
                "x": N @ Xe}
