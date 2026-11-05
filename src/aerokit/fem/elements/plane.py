"""Two-dimensional continuum elements: T3 (CST), Q4, QM6 and Q8.

Formulations (``format`` argument)
    ``"stress"``        plane stress, thickness ``t``; Voigt strain ``[εx, εy, γxy]``.
    ``"strain"``        plane strain, unit thickness (``t`` is ignored and set to 1); ``[εx, εy, γxy]``.
    ``"axisymmetric"``  axisymmetric solid with ``x = r``, ``y = z``; ``[εr, εz, εθ, γrz]``; the volume
                        integral is ``∫ 2π r dA``. The legacy spelling ``"axial"`` is accepted.

All elements are isoparametric (``x = Σ Nᵢ xᵢ``) with nodes numbered counter-clockwise; engineering
shear strains are used throughout. The stiffness is ``K = ∫ Bᵀ D B dV`` and the consistent mass
``M = ∫ ρ Nᵀ N dV`` [cook_2002]_.

QM6 adds the Taylor, Beresford & Wilson (1976) incompatible modes ``(1 − ξ², 1 − η²)`` with the
centroid Jacobian and the ``det J₀ / det J`` scaling so that the element passes the patch test; the
four internal DOFs are condensed statically (Cook et al. 2002, §6.7).

Units SI; tension positive.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.fem.quadrature import gauss2d, triangle
from aerokit.references import cite

__all__ = ["D_isotropic", "D_orthotropic", "shape_t3", "shape_q4", "shape_q8", "T3", "Q4", "QM6", "Q8",
           "FORMULATIONS"]

#: Accepted values of the ``format`` argument (``"axial"`` is a legacy alias of ``"axisymmetric"``).
FORMULATIONS = ("stress", "strain", "axisymmetric")

ShapeTriple = tuple[np.ndarray, np.ndarray, np.ndarray]
Rule = list[tuple[float, float, float]]


def normalize_formulation(format: str) -> str:
    """Return the canonical formulation name (``"axial"`` → ``"axisymmetric"``).

    Parameters
    ----------
    format : {"stress", "strain", "axisymmetric", "axial"}

    Returns
    -------
    str
        One of :data:`FORMULATIONS`.

    Raises
    ------
    ValueError
        Unknown formulation.
    """
    f = "axisymmetric" if format == "axial" else format
    if f not in FORMULATIONS:
        raise ValueError(f"format must be one of 'stress' | 'strain' | 'axisymmetric', got {format!r}")
    return f


# --- material matrices -------------------------------------------------------------------------
@cite("cook_2002", note="isotropic plane stress, plane strain and axisymmetric constitutive matrices")
def D_isotropic(E: float, nu: float, format: str) -> np.ndarray:
    """Isotropic elasticity matrix of a 2-D formulation.

    Parameters
    ----------
    E : float
        Young's modulus [Pa], ``E > 0``.
    nu : float
        Poisson's ratio, ``−1 < ν < 0.5``.
    format : {"stress", "strain", "axisymmetric"}
        Plane stress, plane strain or axisymmetric (``"axial"`` accepted as alias).

    Returns
    -------
    ndarray, shape (3, 3) or (4, 4)
        ``D`` in Voigt order ``[εx, εy, γxy]`` or ``[εr, εz, εθ, γrz]`` [Pa].

    Raises
    ------
    ValueError
        Invalid material constants or formulation.

    Notes
    -----
    Plane stress ``D = E/(1−ν²) [[1, ν, 0], [ν, 1, 0], [0, 0, (1−ν)/2]]``; plane strain and
    axisymmetric use ``c = E/((1+ν)(1−2ν))`` with ``1−ν`` on the normal diagonal and ``(1−2ν)/2``
    for shear.
    """
    if not (E > 0 and -1 < nu < 0.5):
        raise ValueError("material constants must satisfy E > 0 and −1 < ν < 0.5")
    f = normalize_formulation(format)
    if f == "stress":
        return E / (1 - nu ** 2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    c = E / ((1 + nu) * (1 - 2 * nu))
    if f == "strain":
        return c * np.array([[1 - nu, nu, 0], [nu, 1 - nu, 0], [0, 0, (1 - 2 * nu) / 2]])
    return c * np.array([[1 - nu, nu, nu, 0], [nu, 1 - nu, nu, 0],
                         [nu, nu, 1 - nu, 0], [0, 0, 0, (1 - 2 * nu) / 2]])


@cite("jones_1999", note="transformed reduced stiffness Q̄ of an orthotropic lamina")
def D_orthotropic(E1: float, E2: float, nu12: float, G12: float, angle_deg: float = 0.0) -> np.ndarray:
    """Plane-stress elasticity matrix of an orthotropic layer rotated by ``angle_deg``.

    Parameters
    ----------
    E1, E2 : float
        Moduli along and across the fibre [Pa].
    nu12 : float
        Major Poisson's ratio.
    G12 : float
        In-plane shear modulus [Pa].
    angle_deg : float
        Fibre angle measured from the global x axis [deg].

    Returns
    -------
    ndarray, shape (3, 3)
        ``Q̄`` in ``[εx, εy, γxy]`` (engineering shear) [Pa].
    """
    from aerokit.composites.lamina import Q_matrix, Qbar
    return np.asarray(Qbar(Q_matrix(E1, E2, nu12, G12), angle_deg), dtype=float)


def _von_mises(s: ArrayLike, format: str, nu: float = 0.0) -> float:
    """Von Mises stress of a 2-D stress vector (``σz = ν(σx + σy)`` in plane strain)."""
    v = np.asarray(s, dtype=float)
    if format in ("axial", "axisymmetric"):
        sr, sz, st, trz = v
        return math.sqrt(0.5 * ((sr - sz) ** 2 + (sz - st) ** 2 + (st - sr) ** 2) + 3 * trz ** 2)
    sx, sy, txy = v
    sz = nu * (sx + sy) if format == "strain" else 0.0
    return math.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * txy ** 2)


# --- shape functions: (N, dN/dξ, dN/dη) --------------------------------------------------------
def shape_q4(xi: float, eta: float) -> ShapeTriple:
    """Bilinear quadrilateral shape functions and natural derivatives.

    Parameters
    ----------
    xi, eta : float
        Natural coordinates in ``[-1, 1]``.

    Returns
    -------
    N, dN_dxi, dN_deta : ndarray, shape (4,)
        Nodes counter-clockwise from ``(−1, −1)``.
    """
    s = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], dtype=float)
    N = 0.25 * (1 + s[:, 0] * xi) * (1 + s[:, 1] * eta)
    dxi = 0.25 * s[:, 0] * (1 + s[:, 1] * eta)
    deta = 0.25 * s[:, 1] * (1 + s[:, 0] * xi)
    return N, dxi, deta


def shape_q8(xi: float, eta: float) -> ShapeTriple:
    """Eight-node serendipity shape functions.

    Node order: corners 0–3 counter-clockwise, mid-side nodes 4 (edge 0-1), 5 (1-2), 6 (2-3), 7 (3-0).

    Parameters
    ----------
    xi, eta : float
        Natural coordinates.

    Returns
    -------
    N, dN_dxi, dN_deta : ndarray, shape (8,)
    """
    s = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], dtype=float)
    N = np.zeros(8)
    dxi = np.zeros(8)
    deta = np.zeros(8)
    for i in range(4):
        a, b = s[i]
        N[i] = 0.25 * (1 + a * xi) * (1 + b * eta) * (a * xi + b * eta - 1)
        dxi[i] = 0.25 * a * (1 + b * eta) * (2 * a * xi + b * eta)
        deta[i] = 0.25 * b * (1 + a * xi) * (a * xi + 2 * b * eta)
    # edges η = ∓1 (nodes 4, 6) and ξ = ±1 (nodes 5, 7)
    for i, b in ((4, -1), (6, 1)):
        N[i] = 0.5 * (1 - xi ** 2) * (1 + b * eta)
        dxi[i] = -xi * (1 + b * eta)
        deta[i] = 0.5 * b * (1 - xi ** 2)
    for i, a in ((5, 1), (7, -1)):
        N[i] = 0.5 * (1 + a * xi) * (1 - eta ** 2)
        dxi[i] = 0.5 * a * (1 - eta ** 2)
        deta[i] = -eta * (1 + a * xi)
    return N, dxi, deta


def shape_t3(xi: float, eta: float) -> ShapeTriple:
    """Linear triangle (area coordinates ``L₁ = 1 − ξ − η``, ``L₂ = ξ``, ``L₃ = η``).

    Parameters
    ----------
    xi, eta : float
        Natural coordinates of the reference triangle.

    Returns
    -------
    N, dN_dxi, dN_deta : ndarray, shape (3,)
    """
    N = np.array([1 - xi - eta, xi, eta])
    return N, np.array([-1.0, 1.0, 0.0]), np.array([-1.0, 0.0, 1.0])


class _Continuum:
    """Common isoparametric 2-D continuum element (subclasses define ``n``, ``shape``, ``rule``)."""

    ndof = 2
    n: int = 0
    center: tuple[float, float] = (0.0, 0.0)
    NATURAL: list[tuple[float, float]] = []
    _ng: int | None = None

    def __init__(self, nodes: Sequence[int], D: ArrayLike, format: str = "stress", t: float = 1.0,
                 rho: float = 0.0, body_load: ArrayLike = (0.0, 0.0), omega: float = 0.0,
                 nu: float = 0.0) -> None:
        """Create the element.

        Parameters
        ----------
        nodes : sequence of int
            Node indices, counter-clockwise (``n`` of them).
        D : array_like, shape (3, 3) or (4, 4)
            Elasticity matrix [Pa] matching ``format`` (see :func:`D_isotropic`).
        format : {"stress", "strain", "axisymmetric"}
            2-D formulation (``"axial"`` accepted as alias of ``"axisymmetric"``).
        t : float
            Thickness [m] (plane stress only).
        rho : float
            Density [kg/m³].
        body_load : array_like, shape (2,)
            Body force per unit volume ``(bx, by)`` [N/m³] (e.g. ``(0, −ρ g)``).
        omega : float
            Spin rate [rad/s] for the centrifugal load ``ρ ω² r`` (about the z axis in plane
            problems, about the symmetry axis in axisymmetric ones).
        nu : float
            Poisson's ratio, only used for ``σz = ν(σx + σy)`` in the plane-strain von Mises stress.

        Raises
        ------
        ValueError
            Wrong node count, formulation or ``D`` shape.
        """
        if len(nodes) != self.n:
            raise ValueError(f"{type(self).__name__} needs {self.n} nodes")
        fmt = normalize_formulation(format)
        self.nodes = list(nodes)
        self.D = np.asarray(D, dtype=float)
        if self.D.shape != ((4, 4) if fmt == "axisymmetric" else (3, 3)):
            raise ValueError(f"D has shape {self.D.shape}, which does not match the {fmt!r} formulation")
        self.format = fmt
        self.t = t if fmt == "stress" else 1.0
        self.rho, self.omega, self.nu = rho, omega, nu
        self.body_load = np.asarray(body_load, dtype=float)

    # --- abstract interface ---
    @staticmethod
    def shape(xi: float, eta: float) -> ShapeTriple:
        """Shape functions ``(N, dN/dξ, dN/dη)`` (defined by each element)."""
        raise NotImplementedError

    def rule(self) -> Rule:
        """Stiffness quadrature rule ``[(ξ, η, w), ...]``."""
        raise NotImplementedError

    def rule_mass(self) -> Rule:
        """Mass/load quadrature rule ``[(ξ, η, w), ...]``."""
        raise NotImplementedError

    # --- geometry ---
    def _jacobian(self, Xe: np.ndarray, xi: float, eta: float) -> tuple[np.ndarray, np.ndarray, float]:
        """Return ``(N, [dN/dx; dN/dy], det J)`` at ``(ξ, η)``."""
        N, dxi, deta = self.shape(xi, eta)
        J = np.array([dxi @ Xe, deta @ Xe])          # [[dx/dξ, dy/dξ], [dx/dη, dy/dη]]
        detJ = float(np.linalg.det(J))
        if detJ <= 0:
            raise ValueError(f"{type(self).__name__}: Jacobian ≤ 0 (nodes must be counter-clockwise, "
                             "or the element is distorted)")
        dN = np.linalg.solve(J, np.vstack([dxi, deta]))  # [dN/dx; dN/dy]
        return N, dN, detJ

    def _B(self, N: np.ndarray, dN: np.ndarray, r: float | None) -> np.ndarray:
        """Strain-displacement matrix."""
        n = self.n
        if self.format == "axisymmetric":
            B = np.zeros((4, 2 * n))
            B[0, 0::2] = dN[0]
            B[1, 1::2] = dN[1]
            # on the axis (r → 0) εθ = u/r → ∂u/∂r (L'Hôpital; symmetry gives u_r(0) = 0)
            B[2, 0::2] = dN[0] if (r is None or r < 1e-12) else N / r
            B[3, 0::2] = dN[1]
            B[3, 1::2] = dN[0]
        else:
            B = np.zeros((3, 2 * n))
            B[0, 0::2] = dN[0]
            B[1, 1::2] = dN[1]
            B[2, 0::2] = dN[1]
            B[2, 1::2] = dN[0]
        return B

    def _volume_factor(self, N: np.ndarray, Xe: np.ndarray) -> tuple[float, float | None]:
        """Return ``(dV/dA, r)``: ``2π r`` (axisymmetric) or the thickness ``t``."""
        if self.format == "axisymmetric":
            r = float(N @ Xe[:, 0])
            if r <= 0:
                raise ValueError("axisymmetric elements need r > 0 at the Gauss points (element on the axis)")
            return 2 * math.pi * r, r
        return self.t, None

    def _Xe(self, X: np.ndarray) -> np.ndarray:
        return X[self.nodes, :2]

    # --- matrices ---
    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness matrix ``∫ Bᵀ D B dV`` (shape ``(2n, 2n)``, global axes).

        Parameters
        ----------
        X : ndarray, shape (n_node, 2)
            Model nodal coordinates [m].
        """
        Xe = self._Xe(X)
        K = np.zeros((2 * self.n, 2 * self.n))
        for xi, eta, w in self.rule():
            N, dN, detJ = self._jacobian(Xe, xi, eta)
            c, r = self._volume_factor(N, Xe)
            B = self._B(N, dN, r)
            K += B.T @ self.D @ B * detJ * w * c
        return K

    # --- vectorised (batched) stiffness for elements with equal type, formulation, t and D ---
    def batch_key(self) -> Any:
        """Key under which identical elements are integrated together by :meth:`k_batch`."""
        return (type(self), self.format, self.t, self.D.tobytes(), self._ng)

    @classmethod
    def k_batch(cls, X: np.ndarray, els: Sequence[_Continuum]) -> np.ndarray:
        """Stiffness matrices of many elements sharing :meth:`batch_key` (shape ``(ne, 2n, 2n)``)."""
        e0 = els[0]
        Xe = X[np.array([e.nodes for e in els])][:, :, :2]          # (ne, n, 2)
        ne, n = Xe.shape[:2]
        axisym = e0.format == "axisymmetric"
        nb = 4 if axisym else 3
        K = np.zeros((ne, 2 * n, 2 * n))
        rule = triangle(3) if (cls is T3 and axisym) else e0.rule()
        for xi, eta, w in rule:
            N, dxi, deta = e0.shape(xi, eta)
            J = np.stack([np.einsum("i,eij->ej", dxi, Xe), np.einsum("i,eij->ej", deta, Xe)], axis=1)
            detJ = J[:, 0, 0] * J[:, 1, 1] - J[:, 0, 1] * J[:, 1, 0]
            if np.any(detJ <= 0):
                raise ValueError(f"{cls.__name__}: Jacobian ≤ 0 (nodes must be counter-clockwise, "
                                 "or the element is distorted)")
            invJ = np.empty_like(J)
            invJ[:, 0, 0], invJ[:, 0, 1] = J[:, 1, 1] / detJ, -J[:, 0, 1] / detJ
            invJ[:, 1, 0], invJ[:, 1, 1] = -J[:, 1, 0] / detJ, J[:, 0, 0] / detJ
            dN = invJ @ np.vstack([dxi, deta])                          # (ne, 2, n)
            B = np.zeros((ne, nb, 2 * n))
            B[:, 0, 0::2] = dN[:, 0]
            B[:, 1, 1::2] = dN[:, 1]
            if axisym:
                r = Xe[:, :, 0] @ N
                if np.any(r <= 0):
                    raise ValueError("axisymmetric elements need r > 0 at the Gauss points (element on the axis)")
                B[:, 2, 0::2] = N[None, :] / r[:, None]
                B[:, 3, 0::2] = dN[:, 1]
                B[:, 3, 1::2] = dN[:, 0]
                c = 2 * math.pi * r
            else:
                B[:, 2, 0::2] = dN[:, 1]
                B[:, 2, 1::2] = dN[:, 0]
                c = np.full(ne, e0.t)
            K += np.matmul(B.transpose(0, 2, 1), np.matmul(e0.D, B)) * (detJ * w * c)[:, None, None]
        return K

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Consistent mass ``∫ ρ Nᵀ N dV`` or a lumped (diagonal) mass.

        Parameters
        ----------
        X : ndarray
            Nodal coordinates [m].
        lumped : bool
            Row-sum lumping for T3/Q4/QM6; HRZ diagonal scaling for Q8 (whose row sums are negative
            at the corners).
        """
        Xe = self._Xe(X)
        M = np.zeros((2 * self.n, 2 * self.n))
        for xi, eta, w in self.rule_mass():
            N, dN, detJ = self._jacobian(Xe, xi, eta)
            c, _ = self._volume_factor(N, Xe)
            Nm = np.zeros((2, 2 * self.n))
            Nm[0, 0::2] = N
            Nm[1, 1::2] = N
            M += self.rho * Nm.T @ Nm * detJ * w * c
        if lumped:
            if self.n == 8:
                return self._hrz(M)
            return np.diag(M.sum(axis=1))
        return M

    @cite("hinton_rock_zienkiewicz_1976")
    def _hrz(self, M: np.ndarray) -> np.ndarray:
        """Hinton-Rock-Zienkiewicz lumped mass: diagonal scaled to the total mass (per direction)."""
        d = np.diag(M).copy()
        Mt = np.zeros_like(M)
        for direction in (0, 1):
            idx = np.arange(direction, M.shape[0], 2)
            total = M[np.ix_(idx, idx)].sum()
            Mt[idx, idx] = d[idx] * total / d[idx].sum()
        return Mt

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Not available for 2-D continuum elements.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError("2-D continuum elements have no geometric stiffness")

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Equivalent nodal loads of :attr:`body_load` and of the centrifugal load ``ρ ω² r``.

        Parameters
        ----------
        X : ndarray
            Nodal coordinates [m].

        Returns
        -------
        ndarray, shape (2n,)
            ``∫ Nᵀ b dV`` [N].
        """
        if not np.any(self.body_load) and self.omega == 0:
            return np.zeros(2 * self.n)
        Xe = self._Xe(X)
        f = np.zeros(2 * self.n)
        for xi, eta, w in self.rule_mass():
            N, dN, detJ = self._jacobian(Xe, xi, eta)
            c, _ = self._volume_factor(N, Xe)
            b = self.body_load.copy()
            if self.omega:
                x = N @ Xe
                b = b + self.rho * self.omega ** 2 * (np.array([x[0], 0.0]) if self.format == "axisymmetric"
                                                      else x)
            f[0::2] += N * b[0] * detJ * w * c
            f[1::2] += N * b[1] * detJ * w * c
        return f

    def stress_at_point(self, X: np.ndarray, ue: np.ndarray, xi: float, eta: float
                        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Stress, strain and position at natural point ``(ξ, η)``.

        Parameters
        ----------
        X : ndarray
            Nodal coordinates [m].
        ue : ndarray, shape (2n,)
            Element displacement vector [m].
        xi, eta : float
            Natural coordinates.

        Returns
        -------
        sigma : ndarray
            ``D ε`` [Pa] (mechanical strain; see :func:`aerokit.fem.thermal.thermal_stresses` for
            temperature loads).
        eps : ndarray
            Strain (including the condensed incompatible modes of QM6).
        x : ndarray, shape (2,)
            Position [m].
        """
        Xe = self._Xe(X)
        N, dN, detJ = self._jacobian(Xe, xi, eta)
        r = max(float(N @ Xe[:, 0]), 0.0) if self.format == "axisymmetric" else None
        eps = self._B(N, dN, r) @ ue + self._extra_strain(X, ue, xi, eta)
        return self.D @ eps, eps, N @ Xe

    def _extra_strain(self, X: np.ndarray, ue: np.ndarray, xi: float, eta: float) -> np.ndarray | float:
        return 0.0

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Stresses at the stiffness Gauss points and at the centroid (with von Mises).

        Returns
        -------
        dict
            ``{"points": [{"x", "sigma", "eps"}, ...], "center": {"x", "sigma", "eps", "von_mises"}}``.
        """
        points = []
        for xi, eta, _ in self.rule():
            s, e, x = self.stress_at_point(X, ue, xi, eta)
            points.append({"x": x, "sigma": s, "eps": e})
        s0, e0, x0 = self.stress_at_point(X, ue, *self.center)
        return {"points": points, "center": {"x": x0, "sigma": s0, "eps": e0,
                                             "von_mises": _von_mises(s0, self.format, self.nu)}}


@cite("cook_2002", note="constant-strain triangle")
class T3(_Continuum):
    """Three-node constant-strain triangle (CST).

    One-point stiffness integration (exact), three-point mass/load rule; axisymmetric stiffness uses
    the three-point rule because ``εθ = u/r`` varies over the element. See :class:`_Continuum` for
    the constructor arguments.
    """

    n = 3
    center = (1 / 3, 1 / 3)
    NATURAL = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    @staticmethod
    def shape(xi: float, eta: float) -> ShapeTriple:
        """Linear triangle shape functions, see :func:`shape_t3`."""
        return shape_t3(xi, eta)

    def rule(self) -> Rule:
        """One-point centroid rule."""
        return triangle(1)

    def rule_mass(self) -> Rule:
        """Three-point rule (exact for ``N Nᵀ``)."""
        return triangle(3)

    def k(self, X: np.ndarray) -> np.ndarray:
        """Stiffness matrix (three-point rule in the axisymmetric case)."""
        if self.format == "axisymmetric":
            Xe = self._Xe(X)
            K = np.zeros((6, 6))
            for xi, eta, w in triangle(3):
                N, dN, detJ = self._jacobian(Xe, xi, eta)
                c, r = self._volume_factor(N, Xe)
                B = self._B(N, dN, r)
                K += B.T @ self.D @ B * detJ * w * c
            return K
        return super().k(X)


@cite("macneal_harder_1985", note="passes the MacNeal-Harder patch test (tests/fem/test_elements_plane.py)")
@cite("cook_2002", note="bilinear isoparametric quadrilateral")
class Q4(_Continuum):
    """Four-node bilinear quadrilateral.

    Parameters
    ----------
    *args, **kwargs
        As :class:`_Continuum` (``nodes, D, format, t, rho, body_load, omega, nu``).
    gauss : int
        Gauss points per direction for the stiffness (default 2 = full integration).
    """

    n = 4
    center = (0.0, 0.0)
    NATURAL = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]

    def __init__(self, *args: Any, gauss: int = 2, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._ng = gauss

    @staticmethod
    def shape(xi: float, eta: float) -> ShapeTriple:
        """Bilinear shape functions, see :func:`shape_q4`."""
        return shape_q4(xi, eta)

    def rule(self) -> Rule:
        """``gauss × gauss`` Gauss rule."""
        return gauss2d(self._ng or 2)

    def rule_mass(self) -> Rule:
        """2 × 2 Gauss rule."""
        return gauss2d(2)


@cite("nafems_1990", note="verified on the NAFEMS LE1 elliptic membrane (tests/fem/test_elements_plane.py)")
@cite("cook_2002", note="eight-node serendipity quadrilateral")
class Q8(_Continuum):
    """Eight-node serendipity quadrilateral (node order of :func:`shape_q8`).

    Parameters
    ----------
    *args, **kwargs
        As :class:`_Continuum`.
    gauss : int
        Gauss points per direction for the stiffness (3 = full; 2 = reduced, which leaves one
        spurious zero-energy mode per element).
    """

    n = 8
    center = (0.0, 0.0)
    NATURAL = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0),
               (0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]

    def __init__(self, *args: Any, gauss: int = 3, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._ng = gauss

    @staticmethod
    def shape(xi: float, eta: float) -> ShapeTriple:
        """Serendipity shape functions, see :func:`shape_q8`."""
        return shape_q8(xi, eta)

    def rule(self) -> Rule:
        """``gauss × gauss`` Gauss rule."""
        return gauss2d(self._ng or 3)

    def rule_mass(self) -> Rule:
        """3 × 3 Gauss rule."""
        return gauss2d(3)


@cite("taylor_beresford_wilson_1976", "cook_2002",
      note="incompatible modes 1−ξ², 1−η² with centroid Jacobian (Cook et al. 2002 §6.7)")
class QM6(Q4):
    """Q4 with incompatible bending modes (Taylor-Beresford-Wilson).

    Represents pure bending of a rectangle exactly and passes the patch test for arbitrary
    quadrilaterals. Plane stress / plane strain only.

    Notes
    -----
    The strain is ``ε = B u + G α`` with ``G`` built from ``∂P/∂x`` of ``P = (1 − ξ², 1 − η²)``
    using the centroid Jacobian ``J₀`` and scaled by ``det J₀ / det J``, so that ``∫ G dV = 0``.
    The internal DOFs ``α`` are condensed: ``K = K_uu − K_uα K_αα⁻¹ K_αu``.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["gauss"] = 2
        super().__init__(*args, **kwargs)
        if self.format == "axisymmetric":
            raise ValueError("QM6 is not defined for the axisymmetric formulation; use Q8")

    def batch_key(self) -> Any:
        """``None``: static condensation needs the element loop."""
        return None

    def _G(self, Xe: np.ndarray, xi: float, eta: float, detJ: float) -> np.ndarray:
        """Incompatible-mode strain matrix (centroid Jacobian, ``det J₀ / det J`` scaling)."""
        _, dxi0, deta0 = shape_q4(0.0, 0.0)
        J0 = np.array([dxi0 @ Xe, deta0 @ Xe])
        detJ0 = np.linalg.det(J0)
        dP = np.linalg.solve(J0, np.array([[-2 * xi, 0.0], [0.0, -2 * eta]]))  # [dP/dx; dP/dy]
        dP *= detJ0 / detJ
        G = np.zeros((3, 4))
        G[0, 0::2] = dP[0]
        G[1, 1::2] = dP[1]
        G[2, 0::2] = dP[1]
        G[2, 1::2] = dP[0]
        return G

    def _matrices(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return ``(K_uu, K_uα, K_αα)``."""
        Xe = self._Xe(X)
        Kuu = np.zeros((8, 8))
        Kua = np.zeros((8, 4))
        Kaa = np.zeros((4, 4))
        for xi, eta, w in self.rule():
            N, dN, detJ = self._jacobian(Xe, xi, eta)
            c, r = self._volume_factor(N, Xe)
            B = self._B(N, dN, r)
            G = self._G(Xe, xi, eta, detJ)
            Kuu += B.T @ self.D @ B * detJ * w * c
            Kua += B.T @ self.D @ G * detJ * w * c
            Kaa += G.T @ self.D @ G * detJ * w * c
        return Kuu, Kua, Kaa

    def k(self, X: np.ndarray) -> np.ndarray:
        """Condensed stiffness ``K_uu − K_uα K_αα⁻¹ K_αu`` (8 × 8)."""
        Kuu, Kua, Kaa = self._matrices(X)
        return Kuu - Kua @ np.linalg.solve(Kaa, Kua.T)

    def _extra_strain(self, X: np.ndarray, ue: np.ndarray, xi: float, eta: float) -> np.ndarray:
        _, Kua, Kaa = self._matrices(X)
        alpha = -np.linalg.solve(Kaa, Kua.T @ ue)
        Xe = self._Xe(X)
        _, _, detJ = self._jacobian(Xe, xi, eta)
        return self._G(Xe, xi, eta, detJ) @ alpha
