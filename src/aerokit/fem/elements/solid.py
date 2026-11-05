"""3-D solid elements: T4 (constant-strain tetrahedron), T10 (quadratic tetrahedron), H8 (trilinear brick).

DOFs (``ndof = 3``): ``(u, v, w)``. Voigt order ``[εx, εy, εz, γyz, γxz, γxy]`` (engineering shear).

Node order
    T10: corners 0–3, mid-edge nodes 4 (0-1), 5 (1-2), 6 (0-2), 7 (0-3), 8 (1-3), 9 (2-3).
    H8:  bottom face 0-1-2-3 (ζ = −1, counter-clockwise seen from +z), top face 4-5-6-7.

Formulation: isoparametric displacement elements, ``K = ∫ Bᵀ D B dV``, ``M = ∫ ρ Nᵀ N dV``
(Zienkiewicz, Taylor & Zhu 2013, Ch. 6; Cook et al. 2002, Ch. 7).
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.fem.quadrature import gauss1d
from aerokit.references import cite

__all__ = ["D_isotropic3d", "von_mises3d", "shape_t4", "shape_t10", "shape_h8", "H8_CORNER", "rule_tet",
           "rule_tet_duffy", "rule_hex", "T4", "T10", "H8"]

Rule3 = list[tuple[tuple[float, float, float], float]]


@cite("zienkiewicz_taylor_2013", note="isotropic 3-D elasticity matrix")
def D_isotropic3d(E: float, nu: float) -> np.ndarray:
    """Isotropic 3-D elasticity matrix.

    Parameters
    ----------
    E : float
        Young's modulus [Pa], ``E > 0``.
    nu : float
        Poisson's ratio, ``−1 < ν < 0.5``.

    Returns
    -------
    ndarray, shape (6, 6)
        ``D`` [Pa] in ``[εx, εy, εz, γyz, γxz, γxy]``: ``c = E/((1+ν)(1−2ν))``, normal block
        ``c[(1−ν) on the diagonal, ν off it]``, shear ``G = E/(2(1+ν))``.

    Raises
    ------
    ValueError
        Invalid constants.
    """
    if not (E > 0 and -1 < nu < 0.5):
        raise ValueError("material constants must satisfy E > 0 and −1 < ν < 0.5")
    c = E / ((1 + nu) * (1 - 2 * nu))
    D = np.zeros((6, 6))
    D[:3, :3] = c * nu
    np.fill_diagonal(D[:3, :3], c * (1 - nu))
    D[3:, 3:] = np.eye(3) * E / (2 * (1 + nu))
    return D


def von_mises3d(s: ArrayLike) -> float:
    """Von Mises stress of ``[σx, σy, σz, τyz, τxz, τxy]`` [Pa]."""
    sx, sy, sz, tyz, txz, txy = np.asarray(s, dtype=float)
    return math.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * (tyz ** 2 + txz ** 2 + txy ** 2))


# --- shape functions: (N, dN/dξ (3 × n)) --------------------------------------------------------
def shape_t4(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Linear tetrahedron: ``N = [1 − ξ − η − ζ, ξ, η, ζ]`` and ``dN/dξ`` (3 × 4)."""
    x, y, z = p
    N = np.array([1 - x - y - z, x, y, z])
    dN = np.array([[-1, 1, 0, 0], [-1, 0, 1, 0], [-1, 0, 0, 1]], dtype=float)
    return N, dN


def shape_t10(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Quadratic tetrahedron: corners ``Lᵢ(2Lᵢ − 1)``, mid-edges ``4 Lᵢ Lⱼ`` (node order in the module docstring)."""
    x, y, z = p
    L = np.array([1 - x - y - z, x, y, z])
    dL = np.array([[-1, 1, 0, 0], [-1, 0, 1, 0], [-1, 0, 0, 1]], dtype=float)
    edge = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
    N = np.zeros(10)
    dN = np.zeros((3, 10))
    for i in range(4):
        N[i] = L[i] * (2 * L[i] - 1)
        dN[:, i] = (4 * L[i] - 1) * dL[:, i]
    for k, (i, j) in enumerate(edge):
        N[4 + k] = 4 * L[i] * L[j]
        dN[:, 4 + k] = 4 * (L[i] * dL[:, j] + L[j] * dL[:, i])
    return N, dN


#: Natural coordinates of the H8 corner nodes.
H8_CORNER = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                      [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], dtype=float)


def shape_h8(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Trilinear brick: ``N = ⅛ (1 + ξᵢξ)(1 + ηᵢη)(1 + ζᵢζ)`` and ``dN/dξ`` (3 × 8)."""
    s = H8_CORNER
    a = 1 + s * np.asarray(p)
    N = 0.125 * a[:, 0] * a[:, 1] * a[:, 2]
    dN = 0.125 * np.vstack([s[:, 0] * a[:, 1] * a[:, 2], s[:, 1] * a[:, 0] * a[:, 2], s[:, 2] * a[:, 0] * a[:, 1]])
    return N, dN


@cite("keast_1986", note="1-point (degree 1) and 4-point (degree 2) symmetric tetrahedron rules")
def rule_tet(n: int) -> Rule3:
    """Rules on the reference tetrahedron (volume 1/6).

    Parameters
    ----------
    n : {1, 4}
        Number of points: 1 (centroid, linear exact) or 4 (quadratic exact).

    Returns
    -------
    list of ((ξ, η, ζ), w)

    Raises
    ------
    ValueError
        Other ``n``; use :func:`rule_tet_duffy` for higher degree.
    """
    if n == 1:
        return [((0.25, 0.25, 0.25), 1 / 6)]
    if n == 4:
        a, b = 0.5854101966249685, 0.1381966011250105
        return [((b, b, b), 1 / 24), ((a, b, b), 1 / 24), ((b, a, b), 1 / 24), ((b, b, a), 1 / 24)]
    raise ValueError("tetrahedron rule needs n ∈ {1, 4}; use rule_tet_duffy for higher degree")


@cite("duffy_1982", note="collapsed-cube mapping of the tetrahedron")
def rule_tet_duffy(n: int) -> Rule3:
    """``n³``-point Gauss rule on the tetrahedron through the cube → tetrahedron (Duffy) map.

    Parameters
    ----------
    n : int
        Gauss points per cube direction.

    Returns
    -------
    list of ((ξ, η, ζ), w)
        Weights sum to 1/6.

    Notes
    -----
    ``x = u``, ``y = v(1 − u)``, ``z = w(1 − u)(1 − v)`` with Jacobian ``(1 − u)²(1 − v)``. For a
    polynomial of degree ``d`` the integrand in ``u`` has degree ``d + 2``, so ``n ≥ (d + 3)/2``
    suffices; ``n = 4`` integrates degree ≤ 5 exactly.
    """
    g, wg = gauss1d(n)
    t, wt = 0.5 * (g + 1), 0.5 * wg
    rule: Rule3 = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                u, v, w = float(t[i]), float(t[j]), float(t[k])
                rule.append(((u, v * (1 - u), w * (1 - u) * (1 - v)),
                             float(wt[i] * wt[j] * wt[k] * (1 - u) ** 2 * (1 - v))))
    return rule


def rule_hex(n: int) -> Rule3:
    """``n × n × n`` Gauss-Legendre rule on ``[-1, 1]³`` (weights sum to 8)."""
    x, w = gauss1d(n)
    return [((float(x[i]), float(x[j]), float(x[k])), float(w[i] * w[j] * w[k]))
            for i in range(n) for j in range(n) for k in range(n)]


class _Solid:
    """Common isoparametric solid element (subclasses define ``n``, ``shape``, ``rule``)."""

    ndof = 3
    n: int = 0
    center: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __init__(self, nodes: Sequence[int], D: ArrayLike, rho: float = 0.0,
                 body_load: ArrayLike = (0.0, 0.0, 0.0)) -> None:
        """Create the element.

        Parameters
        ----------
        nodes : sequence of int
            Node indices in the element's node order.
        D : array_like, shape (6, 6)
            Elasticity matrix [Pa] (e.g. :func:`D_isotropic3d`).
        rho : float
            Density [kg/m³].
        body_load : array_like, shape (3,)
            Body force per unit volume ``(bx, by, bz)`` [N/m³].

        Raises
        ------
        ValueError
            Wrong node count or ``D`` shape.
        """
        if len(nodes) != self.n:
            raise ValueError(f"{type(self).__name__} needs {self.n} nodes")
        self.nodes = list(nodes)
        self.D = np.asarray(D, dtype=float)
        if self.D.shape != (6, 6):
            raise ValueError("D must be 6×6")
        self.rho = rho
        self.body_load = np.asarray(body_load, dtype=float)

    @staticmethod
    def shape(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
        """Shape functions ``(N, dN/dξ)`` (defined by each element)."""
        raise NotImplementedError

    def rule(self) -> Rule3:
        """Stiffness quadrature rule."""
        raise NotImplementedError

    def rule_mass(self) -> Rule3:
        """Mass/load quadrature rule."""
        raise NotImplementedError

    def _jacobian(self, Xe: np.ndarray, p: Sequence[float]) -> tuple[np.ndarray, np.ndarray, float]:
        """Return ``(N, dN/dx (3 × n), det J)``."""
        N, dNl = self.shape(p)
        J = dNl @ Xe                                      # J[i, j] = ∂x_j/∂ξ_i
        detJ = float(np.linalg.det(J))
        if detJ <= 0:
            raise ValueError(f"{type(self).__name__}: Jacobian ≤ 0 (wrong node order or distorted element)")
        return N, np.linalg.solve(J, dNl), detJ

    @staticmethod
    def _B(dN: np.ndarray) -> np.ndarray:
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

    def _Xe(self, X: np.ndarray) -> np.ndarray:
        if X.shape[1] != 3:
            raise ValueError("3-D elements need 3-D nodal coordinates")
        return X[self.nodes]

    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness ``∫ Bᵀ D B dV`` (shape ``(3n, 3n)``)."""
        Xe = self._Xe(X)
        K = np.zeros((3 * self.n, 3 * self.n))
        for p, w in self.rule():
            _, dN, detJ = self._jacobian(Xe, p)
            B = self._B(dN)
            K += B.T @ self.D @ B * detJ * w
        return K

    def batch_key(self) -> Any:
        """Key under which identical elements are integrated together by :meth:`k_batch`."""
        return (type(self), self.D.tobytes())

    @classmethod
    def k_batch(cls, X: np.ndarray, els: Sequence[_Solid]) -> np.ndarray:
        """Stiffness matrices of many elements of one type and ``D`` (shape ``(ne, 3n, 3n)``)."""
        e0 = els[0]
        if X.shape[1] != 3:
            raise ValueError("3-D elements need 3-D nodal coordinates")
        Xe = X[np.array([e.nodes for e in els])]                    # (ne, n, 3)
        ne, n = Xe.shape[:2]
        K = np.zeros((ne, 3 * n, 3 * n))
        for p, w in e0.rule():
            _, dNl = e0.shape(p)                                        # (3, n)
            J = np.einsum("in,enj->eij", dNl, Xe)                       # (ne, 3, 3)
            detJ = np.linalg.det(J)
            if np.any(detJ <= 0):
                raise ValueError(f"{cls.__name__}: Jacobian ≤ 0 (wrong node order or distorted element)")
            dN = np.linalg.solve(J, np.broadcast_to(dNl, (ne, 3, n)))   # (ne, 3, n)
            B = np.zeros((ne, 6, 3 * n))
            B[:, 0, 0::3] = dN[:, 0]
            B[:, 1, 1::3] = dN[:, 1]
            B[:, 2, 2::3] = dN[:, 2]
            B[:, 3, 1::3] = dN[:, 2]
            B[:, 3, 2::3] = dN[:, 1]
            B[:, 4, 0::3] = dN[:, 2]
            B[:, 4, 2::3] = dN[:, 0]
            B[:, 5, 0::3] = dN[:, 1]
            B[:, 5, 1::3] = dN[:, 0]
            DB = np.matmul(e0.D, B)                                     # BLAS matmul instead of einsum
            K += np.matmul(B.transpose(0, 2, 1), DB) * (detJ * w)[:, None, None]
        return K

    @cite("hinton_rock_zienkiewicz_1976", note="HRZ lumping for T10")
    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Consistent mass, or lumped mass (row sum; HRZ diagonal scaling for T10).

        Parameters
        ----------
        X : ndarray
            Nodal coordinates [m].
        lumped : bool
            Return a diagonal mass. T10 row sums are negative at the corners, so HRZ is used.
        """
        Xe = self._Xe(X)
        M = np.zeros((3 * self.n, 3 * self.n))
        for p, w in self.rule_mass():
            N, _, detJ = self._jacobian(Xe, p)
            Nm = np.zeros((3, 3 * self.n))
            for j in range(3):
                Nm[j, j::3] = N
            M += self.rho * Nm.T @ Nm * detJ * w
        if lumped:
            if self.n == 10:
                Mt = np.zeros_like(M)
                for j in range(3):
                    idx = np.arange(j, M.shape[0], 3)
                    d = np.diag(M)[idx]
                    Mt[idx, idx] = d * M[np.ix_(idx, idx)].sum() / d.sum()
                return Mt
            return np.diag(M.sum(axis=1))
        return M

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Not available.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError("3-D solid elements have no geometric stiffness")

    def volume(self, X: np.ndarray) -> float:
        """Element volume ``∫ dV`` [m³]."""
        Xe = self._Xe(X)
        return float(sum(self._jacobian(Xe, p)[2] * w for p, w in self.rule()))

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Equivalent nodal loads ``∫ Nᵀ b dV`` of :attr:`body_load` [N] (shape ``(3n,)``)."""
        if not np.any(self.body_load):
            return np.zeros(3 * self.n)
        Xe = self._Xe(X)
        f = np.zeros(3 * self.n)
        for p, w in self.rule_mass():
            N, _, detJ = self._jacobian(Xe, p)
            for j in range(3):
                f[j::3] += N * self.body_load[j] * detJ * w
        return f

    def stress_at_point(self, X: np.ndarray, ue: np.ndarray, p: Sequence[float]
                        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return ``(σ = D ε [Pa], ε, x [m])`` at natural point ``p``."""
        Xe = self._Xe(X)
        N, dN, _ = self._jacobian(Xe, p)
        eps = self._B(dN) @ ue
        return self.D @ eps, eps, N @ Xe

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Stresses at the stiffness Gauss points and at the centroid (with von Mises)."""
        points = []
        for p, _ in self.rule():
            s, e, x = self.stress_at_point(X, ue, p)
            points.append({"x": x, "sigma": s, "eps": e})
        s0, e0, x0 = self.stress_at_point(X, ue, self.center)
        return {"points": points, "center": {"x": x0, "sigma": s0, "eps": e0, "von_mises": von_mises3d(s0)}}


@cite("zienkiewicz_taylor_2013", "cook_2002", note="constant-strain tetrahedron")
class T4(_Solid):
    """Four-node constant-strain tetrahedron (1-point stiffness, 4-point mass)."""

    n = 4
    center = (0.25, 0.25, 0.25)
    NATURAL = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]

    @staticmethod
    def shape(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
        """See :func:`shape_t4`."""
        return shape_t4(p)

    def rule(self) -> Rule3:
        """One-point rule."""
        return rule_tet(1)

    def rule_mass(self) -> Rule3:
        """Four-point rule."""
        return rule_tet(4)


@cite("zienkiewicz_taylor_2013", "cook_2002", note="ten-node quadratic tetrahedron")
class T10(_Solid):
    """Ten-node quadratic tetrahedron (4-point stiffness, 64-point Duffy mass rule)."""

    n = 10
    center = (0.25, 0.25, 0.25)
    NATURAL = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0.5, 0, 0), (0.5, 0.5, 0), (0, 0.5, 0),
               (0, 0, 0.5), (0.5, 0, 0.5), (0, 0.5, 0.5)]

    @staticmethod
    def shape(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
        """See :func:`shape_t10`."""
        return shape_t10(p)

    def rule(self) -> Rule3:
        """Four-point rule (exact for the quadratic ``Bᵀ D B``)."""
        return rule_tet(4)

    def rule_mass(self) -> Rule3:
        """Duffy rule with ``n = 4`` (``N Nᵀ`` has degree 4 → ``n ≥ (4 + 3)/2``)."""
        return rule_tet_duffy(4)


@cite("zienkiewicz_taylor_2013", "cook_2002", note="eight-node trilinear brick")
class H8(_Solid):
    """Eight-node trilinear brick with full 2 × 2 × 2 integration."""

    n = 8
    center = (0.0, 0.0, 0.0)
    NATURAL = [tuple(float(v) for v in r) for r in H8_CORNER]

    @staticmethod
    def shape(p: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
        """See :func:`shape_h8`."""
        return shape_h8(p)

    def rule(self) -> Rule3:
        """2 × 2 × 2 Gauss rule."""
        return rule_hex(2)

    def rule_mass(self) -> Rule3:
        """2 × 2 × 2 Gauss rule."""
        return rule_hex(2)
