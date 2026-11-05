"""Steady-state heat conduction and thermal-stress coupling.

Heat conduction
    Scalar elements with one DOF (temperature ``T`` [K or °C]) per node, used through the ordinary
    :class:`~aerokit.fem.model.Model` with ``ndof = 1``; :meth:`Model.static` then solves
    ``K T = Q``, prescribed temperatures are given with ``model.fix(node, 0, T)`` and the
    "reactions" are the nodal heat flows [W] needed to hold them.

    * :class:`HeatT3`, :class:`HeatQ4`, :class:`HeatQ8` — 2-D conduction in a plate of thickness ``t``;
    * :class:`HeatTet4`, :class:`HeatH8` — 3-D conduction;
    * :class:`ConvectionBoundary` — film condition ``q = h (T − T∞)`` on an edge (2-D) or face (3-D);
    * :class:`HeatFluxBoundary` — prescribed heat flux into the body on an edge or face.

    Galerkin weak form of ``∇·(k ∇T) + Q = 0`` [lewis_2004]_:

    ``K = ∫ Bᵀ k B dV + ∫_Γc h N Nᵀ dS``,  ``f = ∫ N Q dV + ∫_Γc h T∞ N dS + ∫_Γq q N dS``,

    with ``B = ∂N/∂x``. The conductivity may be isotropic (scalar), orthotropic (principal values
    along the global axes) or a full symmetric tensor [W/(m·K)].

Thermal stress
    A temperature change ``ΔT`` acts as an initial strain ``ε₀ = α ΔT`` [boley_weiner_1960]_.
    :func:`thermal_load` returns the equivalent nodal forces ``f = ∫ Bᵀ D ε₀ dV`` of a nodal ``ΔT``
    field for :class:`~aerokit.fem.elements.line.Bar`, the plane elements (T3, Q4, QM6, Q8 in plane
    stress, plane strain and axisymmetry) and the solids (T4, T10, H8); :func:`thermal_stresses`
    recovers ``σ = D (ε − ε₀)``. In plane strain the out-of-plane constraint ``εz = 0`` makes the
    effective in-plane initial strain ``(1 + ν) α ΔT`` and ``σz = ν(σx + σy) − E α ΔT``.

Units SI.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike

from aerokit.fem.elements.line import Bar
from aerokit.fem.elements.plane import QM6, T3, _Continuum, shape_q4, shape_q8, shape_t3
from aerokit.fem.elements.solid import _Solid, rule_hex, rule_tet, shape_h8, shape_t4
from aerokit.fem.quadrature import gauss1d, gauss2d, triangle
from aerokit.references import cite

__all__ = ["HeatT3", "HeatQ4", "HeatQ8", "HeatTet4", "HeatH8", "ConvectionBoundary", "HeatFluxBoundary",
           "conductivity_matrix", "thermal_strain", "element_thermal_load", "thermal_load",
           "element_thermal_stress", "thermal_stresses"]

Point = tuple[float, ...]
NaturalRule = list[tuple[Point, float]]


def conductivity_matrix(k: ArrayLike, dim: int) -> np.ndarray:
    """Conductivity tensor from a scalar, principal values or a full matrix.

    Parameters
    ----------
    k : float, sequence of ``dim`` floats, or array_like (dim, dim)
        Isotropic conductivity, orthotropic principal conductivities along the global axes, or
        the full symmetric tensor [W/(m·K)].
    dim : {2, 3}
        Spatial dimension.

    Returns
    -------
    ndarray, shape (dim, dim)

    Raises
    ------
    ValueError
        Wrong shape, non-symmetric or not positive definite.
    """
    a = np.asarray(k, dtype=float)
    if a.ndim == 0:
        K = float(a) * np.eye(dim)
    elif a.shape == (dim,):
        K = np.diag(a)
    elif a.shape == (dim, dim):
        K = a.copy()
    else:
        raise ValueError(f"conductivity must be a scalar, {dim} principal values or a {dim}×{dim} matrix")
    if not np.allclose(K, K.T) or np.any(np.linalg.eigvalsh(0.5 * (K + K.T)) <= 0):
        raise ValueError("conductivity tensor must be symmetric positive definite")
    return K


# ================================================================== conduction elements
class _HeatElement:
    """Common isoparametric conduction element (``ndof = 1``)."""

    ndof = 1
    n: int = 0
    dim: int = 2
    center: Point = (0.0, 0.0)

    def __init__(self, nodes: Sequence[int], k: ArrayLike, t: float = 1.0, heat_source: float = 0.0,
                 rho: float = 0.0, c: float = 0.0) -> None:
        """Create the element.

        Parameters
        ----------
        nodes : sequence of int
            Node indices (node order of the corresponding stress element).
        k : float, sequence or array_like
            Conductivity [W/(m·K)], see :func:`conductivity_matrix`.
        t : float
            Thickness [m] (2-D elements only).
        heat_source : float
            Internal heat generation ``Q`` [W/m³].
        rho, c : float
            Density [kg/m³] and specific heat [J/(kg·K)] for the heat-capacity matrix :meth:`m`.

        Raises
        ------
        ValueError
            Wrong node count, invalid conductivity or thickness.
        """
        if len(nodes) != self.n:
            raise ValueError(f"{type(self).__name__} needs {self.n} nodes")
        if self.dim == 2 and not t > 0:
            raise ValueError("thickness must be positive")
        self.nodes = list(nodes)
        self.kappa = conductivity_matrix(k, self.dim)
        self.t = float(t) if self.dim == 2 else 1.0
        self.heat_source = float(heat_source)
        self.rho, self.c = float(rho), float(c)

    # --- element definition (overridden) ---
    def _shape(self, p: Point) -> tuple[np.ndarray, np.ndarray]:
        """``(N, dN/dξ)`` with ``dN/dξ`` of shape ``(dim, n)``."""
        raise NotImplementedError

    def _rule(self) -> NaturalRule:
        raise NotImplementedError

    def _rule_mass(self) -> NaturalRule:
        return self._rule()

    # --- geometry ---
    def _Xe(self, X: np.ndarray) -> np.ndarray:
        if X.shape[1] < self.dim:
            raise ValueError(f"{type(self).__name__} needs {self.dim}-D nodal coordinates")
        return X[self.nodes, :self.dim]

    def _jacobian(self, Xe: np.ndarray, p: Point) -> tuple[np.ndarray, np.ndarray, float]:
        N, dNl = self._shape(p)
        J = dNl @ Xe
        detJ = float(np.linalg.det(J))
        if detJ <= 0:
            raise ValueError(f"{type(self).__name__}: Jacobian ≤ 0 (wrong node order or distorted element)")
        return N, np.linalg.solve(J, dNl), detJ

    # --- matrices ---
    def k(self, X: np.ndarray) -> np.ndarray:
        """Conductance matrix ``∫ Bᵀ k B dV`` [W/K], shape ``(n, n)``.

        Parameters
        ----------
        X : ndarray
            Model nodal coordinates [m].
        """
        Xe = self._Xe(X)
        K = np.zeros((self.n, self.n))
        for p, w in self._rule():
            _, B, detJ = self._jacobian(Xe, p)
            K += B.T @ self.kappa @ B * detJ * w * self.t
        return K

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Heat-capacity matrix ``∫ ρ c N Nᵀ dV`` [J/K] (``lumped``: row sum)."""
        Xe = self._Xe(X)
        C = np.zeros((self.n, self.n))
        for p, w in self._rule_mass():
            N, _, detJ = self._jacobian(Xe, p)
            C += self.rho * self.c * np.outer(N, N) * detJ * w * self.t
        return np.diag(C.sum(axis=1)) if lumped else C

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Not defined for conduction elements.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError("conduction elements have no geometric stiffness")

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Nodal heat input ``∫ N Q dV`` [W] of the internal heat generation."""
        if self.heat_source == 0.0:
            return np.zeros(self.n)
        Xe = self._Xe(X)
        f = np.zeros(self.n)
        for p, w in self._rule_mass():
            N, _, detJ = self._jacobian(Xe, p)
            f += N * self.heat_source * detJ * w * self.t
        return f

    def flux_at(self, X: np.ndarray, Te: np.ndarray, p: Sequence[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Heat flux, temperature gradient and position at natural point ``p``.

        Returns
        -------
        q : ndarray, shape (dim,)
            Fourier heat flux ``q = −k ∇T`` [W/m²].
        grad : ndarray, shape (dim,)
            ``∇T`` [K/m].
        x : ndarray, shape (dim,)
            Position [m].
        """
        Xe = self._Xe(X)
        N, B, _ = self._jacobian(Xe, tuple(float(v) for v in p))
        g = B @ np.asarray(Te, dtype=float)
        return -self.kappa @ g, g, N @ Xe

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Heat flux at the integration points and the centroid.

        Returns
        -------
        dict
            ``{"points": [{"x", "flux", "grad"}], "center": {"x", "flux", "grad", "T"}}``.
        """
        points = []
        for p, _ in self._rule():
            q, g, x = self.flux_at(X, ue, p)
            points.append({"x": x, "flux": q, "grad": g})
        q0, g0, x0 = self.flux_at(X, ue, self.center)
        N, _ = self._shape(self.center)
        return {"points": points, "center": {"x": x0, "flux": q0, "grad": g0, "T": float(N @ ue)}}


class _Heat2D(_HeatElement):
    """2-D conduction element; also usable with :meth:`Model.node_stresses` (nodal heat flux)."""

    dim = 2
    _shape2d: Callable[[float, float], tuple[np.ndarray, np.ndarray, np.ndarray]]

    def _shape(self, p: Point) -> tuple[np.ndarray, np.ndarray]:
        N, a, b = type(self)._shape2d(p[0], p[1])
        return N, np.vstack([a, b])

    def stress_at_point(self, X: np.ndarray, ue: np.ndarray, xi: float, eta: float
                        ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """``(q, ∇T, x)`` at ``(ξ, η)`` (same interface as the plane stress elements)."""
        return self.flux_at(X, ue, (xi, eta))


@cite("lewis_2004", "cook_2002", note="linear triangle conduction element")
class HeatT3(_Heat2D):
    """Three-node linear triangle for 2-D conduction (constant gradient), see :class:`_HeatElement`."""

    n = 3
    center = (1 / 3, 1 / 3)
    NATURAL = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    _shape2d = staticmethod(shape_t3)

    def _rule(self) -> NaturalRule:
        return [((xi, eta), w) for xi, eta, w in triangle(1)]

    def _rule_mass(self) -> NaturalRule:
        return [((xi, eta), w) for xi, eta, w in triangle(3)]


@cite("lewis_2004", "cook_2002", note="bilinear quadrilateral conduction element")
class HeatQ4(_Heat2D):
    """Four-node bilinear quadrilateral for 2-D conduction (2 × 2 Gauss), see :class:`_HeatElement`."""

    n = 4
    center = (0.0, 0.0)
    NATURAL = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)]
    _shape2d = staticmethod(shape_q4)

    def _rule(self) -> NaturalRule:
        return [((xi, eta), w) for xi, eta, w in gauss2d(2)]


@cite("lewis_2004", "cook_2002", note="eight-node serendipity conduction element")
class HeatQ8(_Heat2D):
    """Eight-node serendipity quadrilateral for 2-D conduction (3 × 3 Gauss), see :class:`_HeatElement`."""

    n = 8
    center = (0.0, 0.0)
    NATURAL = [(-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0),
               (0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]
    _shape2d = staticmethod(shape_q8)

    def _rule(self) -> NaturalRule:
        return [((xi, eta), w) for xi, eta, w in gauss2d(3)]


@cite("lewis_2004", "zienkiewicz_taylor_2013", note="linear tetrahedron conduction element")
class HeatTet4(_HeatElement):
    """Four-node linear tetrahedron for 3-D conduction, see :class:`_HeatElement` (``t`` ignored)."""

    n = 4
    dim = 3
    center = (0.25, 0.25, 0.25)

    def _shape(self, p: Point) -> tuple[np.ndarray, np.ndarray]:
        return shape_t4(p)

    def _rule(self) -> NaturalRule:
        return [(tuple(q), w) for q, w in rule_tet(1)]

    def _rule_mass(self) -> NaturalRule:
        return [(tuple(q), w) for q, w in rule_tet(4)]


@cite("lewis_2004", "zienkiewicz_taylor_2013", note="trilinear brick conduction element")
class HeatH8(_HeatElement):
    """Eight-node trilinear brick for 3-D conduction (2 × 2 × 2 Gauss), see :class:`_HeatElement`."""

    n = 8
    dim = 3
    center = (0.0, 0.0, 0.0)

    def _shape(self, p: Point) -> tuple[np.ndarray, np.ndarray]:
        return shape_h8(p)

    def _rule(self) -> NaturalRule:
        return [(tuple(q), w) for q, w in rule_hex(2)]


# ================================================================== boundary elements
def _boundary_rule(X: np.ndarray, nodes: Sequence[int], t: float) -> list[tuple[np.ndarray, float, np.ndarray]]:
    """Quadrature ``[(N, w·dS, x)]`` on an edge (2-D model) or face (3-D model)."""
    xe = X[list(nodes)]
    n = len(nodes)
    out = []
    if X.shape[1] == 2:
        s_g, w_g = gauss1d(3)
        for s, w in zip(s_g, w_g, strict=True):
            if n == 2:
                N = np.array([(1 - s) / 2, (1 + s) / 2])
                dN = np.array([-0.5, 0.5])
            elif n == 3:
                N = np.array([s * (s - 1) / 2, 1 - s * s, s * (s + 1) / 2])
                dN = np.array([s - 0.5, -2 * s, s + 0.5])
            else:
                raise ValueError("2-D boundary edges need 2 nodes (linear) or 3 nodes (start, mid, end)")
            out.append((N, float(w * math.hypot(*(dN @ xe)) * t), N @ xe))
        return out
    if n == 3:
        rule = [((1 / 6, 1 / 6), 1 / 6), ((2 / 3, 1 / 6), 1 / 6), ((1 / 6, 2 / 3), 1 / 6)]
        for (s, r), w in rule:
            N = np.array([1 - s - r, s, r])
            nrm = np.cross(np.array([-1, 1, 0.0]) @ xe, np.array([-1, 0, 1.0]) @ xe)
            out.append((N, float(w * np.linalg.norm(nrm)), N @ xe))
        return out
    if n == 4:
        g = 1 / math.sqrt(3)
        sg = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float)
        for s in (-g, g):
            for r in (-g, g):
                N = 0.25 * (1 + sg[:, 0] * s) * (1 + sg[:, 1] * r)
                dNs = 0.25 * sg[:, 0] * (1 + sg[:, 1] * r)
                dNr = 0.25 * sg[:, 1] * (1 + sg[:, 0] * s)
                out.append((N, float(np.linalg.norm(np.cross(dNs @ xe, dNr @ xe))), N @ xe))
        return out
    raise ValueError("3-D boundary faces need 3 (triangle) or 4 (quadrilateral) nodes")


@cite("incropera_2007", "lewis_2004", note="Newton cooling boundary h (T − T∞)")
class ConvectionBoundary:
    """Convective (film) boundary ``q_out = h (T − T∞)`` on an edge or face.

    Parameters
    ----------
    nodes : sequence of int
        Edge nodes (2-D model: 2, or 3 as ``(start, mid, end)``) or face nodes (3-D model: 3 or 4).
    h : float
        Film coefficient [W/(m²·K)].
    T_inf : float
        Ambient (fluid) temperature.
    t : float
        Thickness [m] for edges of 2-D models (ignored in 3-D).

    Notes
    -----
    Adds ``∫ h N Nᵀ dS`` to the conductance and ``∫ h T∞ N dS`` to the load (via
    :meth:`body_force`, which :meth:`Model.static` includes by default).
    """

    ndof = 1

    def __init__(self, nodes: Sequence[int], h: float, T_inf: float, t: float = 1.0) -> None:
        if not h >= 0:
            raise ValueError("film coefficient must be non-negative")
        self.nodes = list(nodes)
        self.h, self.T_inf, self.t = float(h), float(T_inf), float(t)

    def _t(self, X: np.ndarray) -> float:
        return self.t if X.shape[1] == 2 else 1.0

    def k(self, X: np.ndarray) -> np.ndarray:
        """Boundary conductance ``∫ h N Nᵀ dS`` [W/K]."""
        K = np.zeros((len(self.nodes), len(self.nodes)))
        for N, wds, _ in _boundary_rule(X, self.nodes, self._t(X)):
            K += self.h * np.outer(N, N) * wds
        return K

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Zero heat capacity."""
        return np.zeros((len(self.nodes), len(self.nodes)))

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Not defined.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError("boundary elements have no geometric stiffness")

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Ambient load ``∫ h T∞ N dS`` [W]."""
        f = np.zeros(len(self.nodes))
        for N, wds, _ in _boundary_rule(X, self.nodes, self._t(X)):
            f += self.h * self.T_inf * N * wds
        return f

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Return ``{"heat_loss": ∫ h (T − T∞) dS [W]}`` (positive leaving the body)."""
        Q = sum(self.h * (float(N @ ue) - self.T_inf) * wds for N, wds, _ in _boundary_rule(X, self.nodes, self._t(X)))
        return {"heat_loss": float(Q)}


@cite("lewis_2004", note="Neumann boundary load")
class HeatFluxBoundary:
    """Prescribed heat flux ``q`` [W/m²] entering the body through an edge or face.

    Parameters
    ----------
    nodes : sequence of int
        Edge or face nodes (as :class:`ConvectionBoundary`).
    q : float
        Heat flux into the body [W/m²] (negative: heat leaving).
    t : float
        Thickness [m] for edges of 2-D models.
    """

    ndof = 1

    def __init__(self, nodes: Sequence[int], q: float, t: float = 1.0) -> None:
        self.nodes = list(nodes)
        self.q, self.t = float(q), float(t)

    def k(self, X: np.ndarray) -> np.ndarray:
        """Zero conductance (pure load element)."""
        return np.zeros((len(self.nodes), len(self.nodes)))

    def m(self, X: np.ndarray, lumped: bool = False) -> np.ndarray:
        """Zero heat capacity."""
        return np.zeros((len(self.nodes), len(self.nodes)))

    def kg(self, X: np.ndarray, ue: np.ndarray) -> np.ndarray:
        """Not defined.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError("boundary elements have no geometric stiffness")

    def body_force(self, X: np.ndarray) -> np.ndarray:
        """Nodal heat input ``∫ q N dS`` [W]."""
        f = np.zeros(len(self.nodes))
        for N, wds, _ in _boundary_rule(X, self.nodes, self.t if X.shape[1] == 2 else 1.0):
            f += self.q * N * wds
        return f

    def stress(self, X: np.ndarray, ue: np.ndarray) -> dict[str, Any]:
        """Return ``{"heat_in": ∫ q dS [W]}``."""
        return {"heat_in": float(self.body_force(X).sum())}


# ================================================================== thermal stress
def _plane_strain_isotropic(D: np.ndarray) -> tuple[float, float] | None:
    """Lamé constants ``(λ, μ)`` of an isotropic plane-strain ``D``, else ``None``."""
    lam, mu = D[0, 1], D[2, 2]
    iso = (np.isclose(D[0, 0], D[1, 1], rtol=1e-9) and np.isclose(D[0, 1], D[1, 0], rtol=1e-9)
           and abs(D[0, 2]) + abs(D[1, 2]) <= 1e-12 * abs(D[0, 0])
           and np.isclose(D[0, 0], lam + 2 * mu, rtol=1e-9))
    return (float(lam), float(mu)) if iso else None


@cite("boley_weiner_1960", note="initial thermal strain; (1+ν) factor in plane strain")
def thermal_strain(element: Any, alpha: ArrayLike, nu: float | None = None) -> np.ndarray:
    """Initial strain per unit temperature change ``ε₀ / ΔT`` in the element's Voigt order.

    Parameters
    ----------
    element : Bar, plane element or solid element
    alpha : float or array_like
        Isotropic coefficient of thermal expansion [1/K], or the full Voigt vector of free thermal
        strain per kelvin (``[αx, αy, αxy]``, ``[αr, αz, αθ, 0]`` or 6 components; for plane strain it
        is then used as given, i.e. it must already contain the out-of-plane restraint).
    nu : float, optional
        Poisson's ratio for the plane-strain factor ``(1 + ν)``; default inferred from the element's
        isotropic ``D`` (``ν = λ / (2(λ + μ))``).

    Returns
    -------
    ndarray
        ``ε₀ / ΔT`` (1 component for a bar, 3/4 for plane, 6 for solids).

    Raises
    ------
    ValueError
        Wrong ``alpha`` length, or plane strain with an anisotropic ``D`` and no ``nu``.
    TypeError
        Unsupported element type.
    """
    a = np.asarray(alpha, dtype=float)
    if isinstance(element, Bar):
        if a.ndim:
            raise ValueError("a bar needs a scalar expansion coefficient")
        return np.array([float(a)])
    if isinstance(element, _Continuum):
        nv = 4 if element.format == "axisymmetric" else 3
        if a.ndim:
            if a.shape != (nv,):
                raise ValueError(f"alpha vector must have {nv} components for this formulation")
            return a.copy()
        if element.format == "stress":
            return float(a) * np.array([1.0, 1.0, 0.0])
        if element.format == "axisymmetric":
            return float(a) * np.array([1.0, 1.0, 1.0, 0.0])
        if nu is None:
            lm = _plane_strain_isotropic(element.D)
            if lm is None:
                raise ValueError("plane strain with anisotropic D: pass nu or a full alpha vector")
            nu = lm[0] / (2 * (lm[0] + lm[1]))
        return float(a) * (1 + nu) * np.array([1.0, 1.0, 0.0])
    if isinstance(element, _Solid):
        if a.ndim:
            if a.shape != (6,):
                raise ValueError("alpha vector must have 6 components for solid elements")
            return a.copy()
        return float(a) * np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
    raise TypeError(f"thermal strain is not implemented for {type(element).__name__}")


def _plane_points(e: _Continuum) -> list[tuple[float, float, float]]:
    """Integration rule for thermal loads of plane elements (QM6: its stiffness rule)."""
    if isinstance(e, QM6):
        return e.rule()
    if isinstance(e, T3):
        return triangle(3)
    return e.rule_mass()


def _plane_terms(e: _Continuum, X: np.ndarray, dTe: np.ndarray, eps0: np.ndarray
                 ) -> tuple[np.ndarray, np.ndarray | None]:
    """Return ``(∫ Bᵀ D ε₀ dV, ∫ Gᵀ D ε₀ dV or None)``."""
    Xe = e._Xe(X)
    f = np.zeros(2 * e.n)
    fa = np.zeros(4) if isinstance(e, QM6) else None
    for xi, eta, w in _plane_points(e):
        N, dN, detJ = e._jacobian(Xe, xi, eta)
        c, r = e._volume_factor(N, Xe)
        s0 = e.D @ eps0 * float(N @ dTe)
        f += e._B(N, dN, r).T @ s0 * detJ * w * c
        if fa is not None and isinstance(e, QM6):
            fa += e._G(Xe, xi, eta, detJ).T @ s0 * detJ * w * c
    return f, fa


def element_thermal_load(element: Any, X: np.ndarray, dT_e: ArrayLike, alpha: ArrayLike,
                         nu: float | None = None) -> np.ndarray:
    """Equivalent nodal forces of a nodal temperature change on one element.

    Parameters
    ----------
    element : Bar, T3, Q4, QM6, Q8, T4, T10 or H8
    X : ndarray
        Model nodal coordinates [m].
    dT_e : array_like, shape (n_element_nodes,)
        Temperature change ``ΔT`` at the element nodes [K], interpolated with the shape functions.
    alpha : float or array_like
        Expansion coefficient, see :func:`thermal_strain`.
    nu : float, optional
        Poisson's ratio override for plane strain.

    Returns
    -------
    ndarray
        ``f = ∫ Bᵀ D ε₀ ΔT dV`` [N] in the element DOF order (QM6: with the incompatible modes
        condensed, ``f_u − K_uα K_αα⁻¹ f_α``).
    """
    dTe = np.asarray(dT_e, dtype=float)
    eps0 = thermal_strain(element, alpha, nu)
    if isinstance(element, Bar):
        L, e = element._T(X)
        P = element.E * element.A * eps0[0] * float(dTe.mean())
        return np.concatenate([-P * e, P * e])
    if isinstance(element, _Continuum):
        f, fa = _plane_terms(element, X, dTe, eps0)
        if fa is not None and isinstance(element, QM6):
            _, Kua, Kaa = element._matrices(X)
            f = f - Kua @ np.linalg.solve(Kaa, fa)
        return f
    if isinstance(element, _Solid):
        Xe = element._Xe(X)
        f = np.zeros(3 * element.n)
        for p, w in element.rule_mass():
            N, dN, detJ = element._jacobian(Xe, p)
            f += element._B(dN).T @ (element.D @ eps0) * float(N @ dTe) * detJ * w
        return f
    raise TypeError(f"thermal load is not implemented for {type(element).__name__}")


def _supported(e: Any) -> bool:
    return isinstance(e, Bar | _Continuum | _Solid)


def thermal_load(model: Any, dT: ArrayLike, alpha: ArrayLike, nu: float | None = None,
                 skip_unsupported: bool = False) -> np.ndarray:
    """Global equivalent nodal load vector of a nodal temperature-change field.

    Parameters
    ----------
    model : Model
        Structural model (bars, plane or solid elements).
    dT : array_like, shape (n_node,)
        Temperature change from the stress-free state at every node [K] (e.g. the solution of a
        heat-conduction model on the same mesh minus the reference temperature).
    alpha : float or array_like
        Expansion coefficient [1/K], see :func:`thermal_strain`.
    nu : float, optional
        Poisson's ratio override for plane strain.
    skip_unsupported : bool
        Ignore element types without a thermal formulation instead of raising ``TypeError``.

    Returns
    -------
    ndarray, shape (n_dof,)
        Add it to ``model.F`` (or pass ``F=`` to :meth:`Model.static`).

    Examples
    --------
    >>> import numpy as np
    >>> from aerokit.fem import Model, Q4, D_isotropic
    >>> from aerokit.fem.thermal import thermal_load
    >>> m = Model([[0, 0], [1, 0], [1, 1], [0, 1]], ndof=2)
    >>> _ = m.add(Q4([0, 1, 2, 3], D_isotropic(70e9, 0.3, "stress")))
    >>> m.fix(0, [0, 1]); m.fix(3, 0)
    >>> u = m.static(F=thermal_load(m, np.full(4, 100.0), 23e-6)).u
    >>> round(u[2] / (23e-6 * 100), 12)                  # free expansion u = α ΔT x
    1.0
    """
    T = np.asarray(dT, dtype=float)
    if T.shape != (model.n_node,):
        raise ValueError(f"dT must have one value per node ({model.n_node}), got shape {T.shape}")
    F = np.zeros(model.n_dof)
    for e in model.elements:
        if not _supported(e):
            if skip_unsupported:
                continue
            raise TypeError(f"thermal load is not implemented for {type(e).__name__}")
        F[model.equivalent_dof(e)] += element_thermal_load(e, model.X, T[e.nodes], alpha, nu)
    return F


def _vm_plane(s: np.ndarray, sz: float) -> float:
    sx, sy, txy = s
    return math.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * txy ** 2)


def element_thermal_stress(element: Any, X: np.ndarray, ue: ArrayLike, dT_e: ArrayLike, alpha: ArrayLike,
                           nu: float | None = None) -> dict[str, Any]:
    """Stresses ``σ = D (ε − ε₀)`` of one element under a temperature change.

    Parameters
    ----------
    element : Bar, plane element or solid element
    X : ndarray
        Model nodal coordinates [m].
    ue : array_like
        Element displacement vector [m].
    dT_e : array_like
        Nodal temperature changes of the element [K].
    alpha, nu
        See :func:`thermal_strain`.

    Returns
    -------
    dict
        Bar: ``{"N", "sigma"}``. Continuum: ``{"points": [{"x", "sigma", "eps", "eps_thermal"}],
        "center": {..., "von_mises"}}``; plane strain adds ``sigma_z`` (isotropic ``D``), computed as
        ``λ(εx + εy) − (3λ + 2μ) α ΔT``.
    """
    u = np.asarray(ue, dtype=float)
    dTe = np.asarray(dT_e, dtype=float)
    eps0 = thermal_strain(element, alpha, nu)
    if isinstance(element, Bar):
        L, e = element._T(X)
        strain = float(e @ (u[element.ndof:] - u[:element.ndof])) / L
        sigma = element.E * (strain - eps0[0] * float(dTe.mean()))
        return {"N": sigma * element.A, "sigma": sigma}
    if isinstance(element, _Continuum):
        alpha_modes = None
        if isinstance(element, QM6):
            _, fa = _plane_terms(element, X, dTe, eps0)
            _, Kua, Kaa = element._matrices(X)
            if fa is None:                          # pragma: no cover - QM6 always returns f_α
                raise RuntimeError("QM6 incompatible-mode load missing")
            alpha_modes = np.linalg.solve(Kaa, fa - Kua.T @ u)
        Xe = element._Xe(X)
        lm = _plane_strain_isotropic(element.D) if element.format == "strain" else None
        a_scalar = float(np.asarray(alpha, dtype=float)) if np.ndim(alpha) == 0 else None

        def at(xi: float, eta: float) -> dict[str, Any]:
            N, dN, detJ = element._jacobian(Xe, xi, eta)
            r = max(float(N @ Xe[:, 0]), 0.0) if element.format == "axisymmetric" else None
            eps = element._B(N, dN, r) @ u
            if alpha_modes is not None and isinstance(element, QM6):
                eps = eps + element._G(Xe, xi, eta, detJ) @ alpha_modes
            dT = float(N @ dTe)
            eth = eps0 * dT
            s = element.D @ (eps - eth)
            out: dict[str, Any] = {"x": N @ Xe, "sigma": s, "eps": eps, "eps_thermal": eth}
            if element.format == "axisymmetric":
                sr, sz_, st, trz = s
                out["von_mises"] = math.sqrt(0.5 * ((sr - sz_) ** 2 + (sz_ - st) ** 2 + (st - sr) ** 2) + 3 * trz ** 2)
            elif element.format == "strain" and lm is not None and a_scalar is not None:
                lam, mu = lm
                sz = lam * (eps[0] + eps[1]) - (3 * lam + 2 * mu) * a_scalar * dT
                out["sigma_z"] = sz
                out["von_mises"] = _vm_plane(s, sz)
            else:
                out["von_mises"] = _vm_plane(s, 0.0) if element.format == "stress" else float("nan")
            return out
        points = [at(xi, eta) for xi, eta, _ in element.rule()]
        return {"points": points, "center": at(*element.center)}
    if isinstance(element, _Solid):
        from aerokit.fem.elements.solid import von_mises3d
        Xe = element._Xe(X)

        def at3(p: Sequence[float]) -> dict[str, Any]:
            N, dN, _ = element._jacobian(Xe, p)
            eps = element._B(dN) @ u
            eth = eps0 * float(N @ dTe)
            s = element.D @ (eps - eth)
            return {"x": N @ Xe, "sigma": s, "eps": eps, "eps_thermal": eth, "von_mises": von_mises3d(s)}
        return {"points": [at3(p) for p, _ in element.rule()], "center": at3(element.center)}
    raise TypeError(f"thermal stress is not implemented for {type(element).__name__}")


def thermal_stresses(model: Any, u: ArrayLike, dT: ArrayLike, alpha: ArrayLike, nu: float | None = None,
                     skip_unsupported: bool = False) -> list[dict[str, Any] | None]:
    """Element stresses with the thermal strain removed, ``σ = D (ε − α ΔT)``.

    Parameters
    ----------
    model : Model
    u : array_like, shape (n_dof,)
        Displacements from ``model.static`` with the :func:`thermal_load` applied.
    dT : array_like, shape (n_node,)
        Nodal temperature change [K].
    alpha, nu
        See :func:`thermal_strain`.
    skip_unsupported : bool
        Return ``None`` for unsupported elements instead of raising ``TypeError``.

    Returns
    -------
    list
        :func:`element_thermal_stress` of every element (model order).
    """
    U = np.asarray(u, dtype=float)
    T = np.asarray(dT, dtype=float)
    if T.shape != (model.n_node,):
        raise ValueError(f"dT must have one value per node ({model.n_node}), got shape {T.shape}")
    out: list[dict[str, Any] | None] = []
    for e in model.elements:
        if not _supported(e):
            if skip_unsupported:
                out.append(None)
                continue
            raise TypeError(f"thermal stress is not implemented for {type(e).__name__}")
        out.append(element_thermal_stress(e, model.X, U[model.equivalent_dof(e)], T[e.nodes], alpha, nu))
    return out
