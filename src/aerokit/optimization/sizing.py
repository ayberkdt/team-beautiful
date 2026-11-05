"""Cross-section sizing optimization of trusses and plane frames.

The design variables are element cross-sectional areas ``x_g``. Linking groups: all elements of a
group share one area (``A_e = x_g(e)``). For frames and for Euler buckling the second moment of area
is tied to the area through a section family, ``I = c·A^p``, and the elastic section modulus through
``W = w·A^q`` (:class:`SectionFamily`).

Responses and their ANALYTIC sensitivities (all derivatives go through ``dK/dA_e``; for a truss
``dK/dA_e = k_e/A_e``):

========================  ===================================================================
mass, volume              direct: ``Σ ρ L``, ``Σ L``
compliance C = Σ Fᵀu      ``dC/dx = −uᵀ (dK/dx) u`` (self-adjoint)
stress, displacement,     ``r = qᵀu`` (+ explicit term):
Euler ratio               direct:  ``du/dx = −K⁻¹ (dK/dx) u``, ``dr/dx = qᵀ du/dx + ∂r/∂x``
                          adjoint: ``K λ = q``, ``dr/dx = −λᵀ (dK/dx) u + ∂r/∂x``
frequency (λ = ω²)        ``dλ = φᵀ (dK − λ dM) φ`` with ``φᵀ M φ = 1`` (invalid for repeated
                          eigenvalues)
system buckling factor    ``(K + λ G) φ = 0``: ``dλ = −φᵀ(dK + λ dG)φ / (φᵀ G φ)``,
                          ``G = Σ N_e ĝ_e``, ``N_e = A_e ν_eᵀ u_e`` (design dependence of the
                          pre-load included)
========================  ===================================================================

Source: Haftka & Gürdal, *Elements of Structural Optimization*, 3rd ed. (1992), Chapter 7
(direct/adjoint method, eigenvalue sensitivity) and Chapter 9 (fully stressed design, optimality
criteria). This source was NOT read in this repository; the formulas were derived here and are
verified against central finite differences in the tests.

Optimization methods:

* :func:`fully_stressed_design` -- stress-ratio iteration (FSD);
* :func:`optimality_criterion` -- minimum mass under a single compliance or displacement
  constraint (OC; linearization in reciprocal variables, λ found by bisection);
* :func:`slsqp` -- ``scipy.optimize.minimize(method="SLSQP")`` with analytic gradients and
  normalized constraints;
* :func:`kkt_audit` -- Lagrangian gradient and complementary slackness at an optimum.

Constraints are normalized and ``g ≤ 0`` means feasible (e.g. ``σ/σ_allow − 1``).
Units: the module is unit-agnostic; SI is recommended. The benchmark problems are in their
original units (kip, in, ksi, lb/in³ → weight in lb) because the literature values are given in
those units.
"""
from __future__ import annotations

import copy
import math
import warnings
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

import numpy as np
import scipy.linalg as sla
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from numpy.typing import ArrayLike
from scipy.optimize import minimize, nnls

from aerokit.fem import Model
from aerokit.fem.elements.line import Bar, Frame2D
from aerokit.references import cite

__all__ = [
    "SectionFamily", "filled_square", "filled_circle", "thin_tube_ratio", "thin_tube_fixed_t",
    "i_profile_fixed_height", "load_vector", "SizeProblem", "OptResult", "fully_stressed_design",
    "optimality_criterion", "slsqp", "kkt_audit", "LITERATURE", "three_bar_truss", "ten_bar_truss",
    "TWENTY_FIVE_JOINT", "TWENTY_FIVE_GROUPS", "twenty_five_bar_truss",
]


# ---------------------------------------------------------------- section families
class SectionFamily:
    """Power-law cross-section family ``I = c·A^p`` and (optionally) ``W = w·A^q``.

    Parameters
    ----------
    c, p : float
        Coefficient and exponent of the second moment of area, ``I = c·A^p`` [m⁴ for A in m²].
        Both must be positive.
    w, q : float, optional
        Coefficient and exponent of the elastic section modulus, ``W = w·A^q`` [m³]. Give both or
        neither; both must be positive. Required for fiber stresses ``N/A ± M/W`` in frames.
    name : str
        Label used in ``repr`` and error messages.

    Raises
    ------
    ValueError
        If ``c`` or ``p`` is not positive, or ``w``/``q`` are inconsistent or not positive.

    Examples
    --------
    >>> s = SectionFamily(1 / 12, 2, 1 / 6, 1.5, "solid square")
    >>> float(s.I(4.0))  # a = 2: a⁴/12
    1.3333333333333333
    """

    def __init__(self, c: float, p: float, w: float | None = None, q: float | None = None, name: str = ""):
        if not (c > 0 and p > 0):
            raise ValueError("section family: c > 0 and p > 0 required")
        if (w is None) != (q is None) or (w is not None and q is not None and not (w > 0 and q > 0)):
            raise ValueError("section family: w and q must be given together and be positive")
        self.c, self.p, self.w, self.q, self.name = float(c), float(p), w, q, name

    def I(self, A: ArrayLike) -> np.ndarray:  # noqa: E743
        """Second moment of area ``I = c·A^p``."""
        return self.c * np.asarray(A, dtype=float) ** self.p

    def dI(self, A: ArrayLike) -> np.ndarray:
        """Derivative ``dI/dA = c·p·A^(p−1)``."""
        return self.c * self.p * np.asarray(A, dtype=float) ** (self.p - 1)

    def W(self, A: ArrayLike) -> np.ndarray:
        """Elastic section modulus ``W = w·A^q``.

        Raises
        ------
        ValueError
            If the family has no section modulus (``w``, ``q``).
        """
        w, q = self._require_w()
        return w * np.asarray(A, dtype=float) ** q

    def I_W(self, A: ArrayLike) -> np.ndarray:
        """Ratio ``I/W = (c/w)·A^(p−q)``.

        Converts a bending moment to an extreme-fiber stress through ``M·(I/W)/I = M/W``.

        Raises
        ------
        ValueError
            If the family has no section modulus (``w``, ``q``).
        """
        w, q = self._require_w()
        return self.c / w * np.asarray(A, dtype=float) ** (self.p - q)

    def dI_W(self, A: ArrayLike) -> np.ndarray:
        """Derivative ``d(I/W)/dA = (c/w)(p − q)·A^(p−q−1)``.

        Raises
        ------
        ValueError
            If the family has no section modulus (``w``, ``q``).
        """
        w, q = self._require_w()
        return self.c / w * (self.p - q) * np.asarray(A, dtype=float) ** (self.p - q - 1)

    def _require_w(self) -> tuple[float, float]:
        """Return ``(w, q)`` or raise if the section modulus is not defined."""
        if self.w is None or self.q is None:
            raise ValueError(f"section family '{self.name}': section modulus (w, q) is not defined")
        return self.w, self.q

    def __repr__(self) -> str:
        return f"SectionFamily({self.name}: I = {self.c:.4g}·A^{self.p:g}" + \
            (f", W = {self.w:.4g}·A^{self.q:g})" if self.w is not None else ")")


def filled_square() -> SectionFamily:
    """Solid square section of side ``a``.

    Returns
    -------
    SectionFamily
        ``A = a²``, ``I = a⁴/12 = A²/12``, ``W = a³/6 = A^1.5/6``.
    """
    return SectionFamily(1 / 12, 2, 1 / 6, 1.5, "solid square")


def filled_circle() -> SectionFamily:
    """Solid circular section of diameter ``d``.

    Returns
    -------
    SectionFamily
        ``A = πd²/4``, ``I = πd⁴/64 = A²/(4π)``, ``W = πd³/32 = A^1.5/(4√π)``.
    """
    return SectionFamily(1 / (4 * math.pi), 2, 1 / (4 * math.sqrt(math.pi)), 1.5, "solid circle")


def thin_tube_ratio(R_t: float) -> SectionFamily:
    """Thin-walled circular tube with a fixed radius-to-thickness ratio ``k = R/t``.

    Parameters
    ----------
    R_t : float
        Mean radius over wall thickness, ``R/t`` [-]; must be positive.

    Returns
    -------
    SectionFamily
        ``A = 2πRt``, ``I = πR³t = k·A²/(4π)``, ``W = πR²t = ½√(k/2π)·A^1.5``.

    Raises
    ------
    ValueError
        If ``R_t ≤ 0``.
    """
    k = float(R_t)
    if k <= 0:
        raise ValueError("R/t must be positive")
    return SectionFamily(k / (4 * math.pi), 2, 0.5 * math.sqrt(k / (2 * math.pi)), 1.5, f"thin tube R/t={k:g}")


def thin_tube_fixed_t(t: float) -> SectionFamily:
    """Thin-walled circular tube with a fixed wall thickness ``t`` (radius varies with the area).

    Parameters
    ----------
    t : float
        Wall thickness [m]; must be positive.

    Returns
    -------
    SectionFamily
        ``I = A³/(8π²t²)``, ``W = A²/(4πt)``.

    Raises
    ------
    ValueError
        If ``t ≤ 0``.
    """
    if t <= 0:
        raise ValueError("wall thickness must be positive")
    return SectionFamily(1 / (8 * math.pi ** 2 * t ** 2), 3, 1 / (4 * math.pi * t), 2, f"thin tube t={t:g}")


def i_profile_fixed_height(h: float) -> SectionFamily:
    """Idealized I-section of fixed height ``h``, area lumped in two thin flanges (web neglected).

    Parameters
    ----------
    h : float
        Section height [m]; must be positive.

    Returns
    -------
    SectionFamily
        ``I = A·h²/4``, ``W = A·h/2``.

    Raises
    ------
    ValueError
        If ``h ≤ 0``.
    """
    if h <= 0:
        raise ValueError("height must be positive")
    return SectionFamily(h * h / 4, 1, h / 2, 1, f"I-section h={h:g}")


def load_vector(model: Model, loads: Sequence[tuple[int, int, float]]) -> np.ndarray:
    """Assemble a full-DOF load vector for one load case.

    Parameters
    ----------
    model : aerokit.fem.Model
        Model defining the DOF numbering.
    loads : sequence of (node, local_dof, value)
        Nodal loads [N or N·m]; repeated entries are summed.

    Returns
    -------
    numpy.ndarray
        Load vector of length ``model.n_dof``.
    """
    F = np.zeros(model.n_dof)
    for node, local, value in loads:
        F[model.dof(node, local)] += value
    return F


# ---------------------------------------------------------------- element pre-computation
def _element_data(e: Any, X: np.ndarray, lumped: bool) -> dict[str, Any]:
    """Unit-property (A = 1 / I = 1) element matrices and stress row vectors, using the element's own code."""
    if isinstance(e, Bar):
        cb = copy.copy(e)
        cb.A = 1.0
        L, ev = cb._T(X)
        nd = cb.ndof
        kA = cb.k(X)
        kI = np.zeros_like(kA)
        nu = cb.E / L * np.concatenate([-ev, ev])        # N = A·νᵀu_e
        rM = np.zeros((2, 2 * nd))
        ub = np.zeros(2 * nd)
        ub[nd:] = ev * L / cb.E                           # end displacement giving N = 1
        gh = cb.kg(X, ub)
        return dict(kind="bar", L=L, E=cb.E, rho=cb.rho, kA=kA, kI=kI, mA=cb.m(X, lumped=lumped),
                    nu=nu, rM=rM, gh=gh)
    if isinstance(e, Frame2D):
        if e.q != 0:
            raise ValueError("Frame2D distributed load (q) is not supported in sizing; use equivalent nodal loads")
        cf = copy.copy(e)
        L, T = cf._T(X)
        cf.A, cf.I = 1.0, 0.0
        kA, kAy = cf.k(X), cf.k_local(L)
        mA = cf.m(X, lumped=lumped)
        cf.A, cf.I = 0.0, 1.0
        kI, kIy = cf.k(X), cf.k_local(L)
        nu = -(kAy @ T)[0]                               # same sign as the element stress output: N = −f[0]
        rM = np.vstack([-(kIy @ T)[2], (kIy @ T)[5]])   # M1 = −f[2], M2 = f[5] (per unit I)
        cf.A, cf.I = 1.0, 1.0
        gh = cf.kg(X, T.T @ np.array([0, 0, 0, L / cf.E, 0, 0]))
        return dict(kind="frame", L=L, E=cf.E, rho=cf.rho, kA=kA, kI=kI, mA=mA, nu=nu, rM=rM, gh=gh)
    raise ValueError(f"{type(e).__name__} is not supported in sizing (Bar or Frame2D)")


def _with_derivative(r: Any, derivative: bool) -> tuple[Any, Any]:
    """Split a ``(value, derivative)`` response; the derivative is ``None`` when not requested."""
    return r if derivative else (r, None)


# ---------------------------------------------------------------- problem
@cite("haftka_gurdal_1992", note="Ch. 7 (direct/adjoint sensitivities, eigenvalue derivatives); not read — "
      "formulas derived here and verified by central differences")
class SizeProblem:
    """Cross-sectional area sizing problem on an :class:`aerokit.fem.Model`.

    Parameters
    ----------
    model : aerokit.fem.Model
        Model with 2D/3D :class:`Bar` or :class:`Frame2D` elements; prescribed DOFs must be zero.
    groups : list of list of int, optional
        Element index groups linked to one design variable each; every element must be in exactly
        one group. ``None``: one variable per element.
    lower, upper : float or array_like
        Variable bounds [m²], scalar or per group. ``lower`` must be positive and finite.
    load_cases : list of array_like, optional
        Full-DOF load vectors [N]; ``None`` uses ``[model.F + model.body_forces()]``.
    section : SectionFamily, optional
        Section family ``I = c·A^p`` (required for frames; for trusses only for Euler buckling).
    extra_mass : array_like or dict, optional
        Non-structural mass [kg]: full-DOF array or ``{(node, local_dof): mass}``.
    batch_mass : bool
        Use the lumped mass matrix (default: consistent).
    sensitivity : {"direct", "adjoint", "auto"}
        Linear-response sensitivity method; ``"auto"`` selects the one needing fewer solves.

    Attributes
    ----------
    n : int
        Number of design variables (groups).
    group_no : numpy.ndarray
        Group index of each element.
    P : numpy.ndarray
        Element-to-group incidence matrix ``(n_element, n)``.
    F : numpy.ndarray
        Load cases as columns ``(n_dof, n_disp)``.
    free : numpy.ndarray
        Free DOF indices.
    components : list of tuple
        Stress components ``(element, end k, fiber s)``; ``s = 0`` is the axial stress, ``s = ±1``
        the top/bottom fiber at frame end ``k``.
    constraint_names : list of str
        Names of the constraints of the last :meth:`constraints` call.

    Raises
    ------
    ValueError
        On unsupported elements, a missing section family for frames, prescribed non-zero
        displacements, inconsistent groups, invalid bounds, zero or wrongly sized load cases,
        or negative extra mass.

    Notes
    -----
    Element stiffness ``k_e = A_e k_A + I(A_e) k_I`` and mass ``m_e = A_e m_A`` are assembled from
    unit-property element matrices computed once. Constraint definitions are added with the
    ``*_limit`` methods, which return ``self`` and can be chained.
    """

    def __init__(self, model: Model, groups: Sequence[Sequence[int]] | None = None, lower: ArrayLike = 1e-6,
                 upper: ArrayLike = np.inf, load_cases: Sequence[ArrayLike] | None = None,
                 section: SectionFamily | None = None, extra_mass: ArrayLike | dict | None = None,
                 batch_mass: bool = False, sensitivity: str = "auto"):
        if not isinstance(model, Model):
            raise ValueError("model must be an aerokit.fem.Model")
        if not model.elements:
            raise ValueError("model has no elements")
        self.model = model
        n_el = len(model.elements)
        kinds = {type(e) for e in model.elements}
        if not kinds <= {Bar, Frame2D}:
            bad = ", ".join(sorted(t.__name__ for t in kinds - {Bar, Frame2D}))
            raise ValueError(f"unsupported element type: {bad} (Bar or Frame2D)")
        self.frame = Frame2D in kinds
        if self.frame and section is None:
            raise ValueError("frame sizing requires a section family (I = c·A^p)")
        if section is not None and not isinstance(section, SectionFamily):
            raise ValueError("section must be a SectionFamily")
        self.section = section
        free, _fixed, value = model._partition()
        if np.any(value != 0):
            raise ValueError("prescribed (non-zero) displacements are not supported in sizing")
        if free.size == 0:
            raise ValueError("no free DOFs")
        self.free = free
        if sensitivity not in ("direct", "adjoint", "auto"):
            raise ValueError("sensitivity: 'direct', 'adjoint' or 'auto'")
        self.sensitivity = sensitivity

        # groups
        if groups is None:
            groups = [[i] for i in range(n_el)]
        group_list = [list(map(int, g)) for g in groups]
        if any(len(g) == 0 for g in group_list):
            raise ValueError("empty group")
        all_ids = [i for g in group_list for i in g]
        if sorted(all_ids) != list(range(n_el)):
            missing = sorted(set(range(n_el)) - set(all_ids))
            repeat = sorted({i for i in all_ids if all_ids.count(i) > 1})
            out = sorted({i for i in all_ids if not 0 <= i < n_el})
            raise ValueError(f"groups must contain every element exactly once (missing {missing}, repeated {repeat}, "
                             f"invalid {out})")
        self.groups = group_list
        self.n = len(group_list)
        self.group_no = np.empty(n_el, dtype=int)
        for g, el in enumerate(group_list):
            self.group_no[el] = g
        self.P = np.zeros((n_el, self.n))
        self.P[np.arange(n_el), self.group_no] = 1.0

        # bounds
        self.lower = np.broadcast_to(np.asarray(lower, dtype=float), (self.n,)).copy()
        self.upper = np.broadcast_to(np.asarray(upper, dtype=float), (self.n,)).copy()
        if np.any(~np.isfinite(self.lower)) or np.any(self.lower <= 0):
            raise ValueError("lower bound must be positive and finite (K becomes singular if an area reaches zero)")
        if np.any(self.upper < self.lower):
            raise ValueError("upper bound smaller than lower bound")

        # load cases
        if load_cases is None:
            load_cases = [model.F + model.body_forces()]
        F = [np.asarray(f, dtype=float) for f in load_cases]
        if not F or any(f.shape != (model.n_dof,) for f in F):
            raise ValueError(f"each load case must be a full-DOF vector of length {model.n_dof}")
        if any(not np.any(f[free]) for f in F):
            raise ValueError("a load case has zero load")
        self.F = np.column_stack(F)
        self.n_disp = self.F.shape[1]

        # extra (non-structural) mass
        extra: np.ndarray = np.zeros(model.n_dof)
        if isinstance(extra_mass, dict):
            for (node, local), mass in extra_mass.items():
                extra[model.dof(node, local)] += mass
        elif extra_mass is not None:
            extra = np.asarray(extra_mass, dtype=float).copy()
            if extra.shape != (model.n_dof,):
                raise ValueError("extra_mass must have full-DOF length")
        if np.any(extra < 0):
            raise ValueError("extra mass cannot be negative")
        self.extra_mass = extra
        self.batch_mass = bool(batch_mass)

        # element data (geometry only)
        data = [_element_data(e, model.X, self.batch_mass) for e in model.elements]
        self.DOF = np.array([model.equivalent_dof(e) for e in model.elements])
        self.L = np.array([v["L"] for v in data])
        self.E = np.array([v["E"] for v in data], dtype=float)
        self.rho = np.array([v["rho"] for v in data], dtype=float)
        self.kind = [v["kind"] for v in data]
        self.kA = np.array([v["kA"] for v in data])
        self.kI = np.array([v["kI"] for v in data])
        self.mA = np.array([v["mA"] for v in data])
        self.nu = np.array([v["nu"] for v in data])
        self.rM = np.array([v["rM"] for v in data])
        self.gh = np.array([v["gh"] for v in data])
        nd = self.DOF.shape[1]
        self._rows = np.repeat(self.DOF, nd, axis=1).ravel()
        self._cols = np.tile(self.DOF, (1, nd)).ravel()

        # stress components: (element, end k, fiber s); s = 0 → axial
        self.components: list[tuple[int, int, int]] = []
        has_w = section is not None and section.w is not None
        for i, t in enumerate(self.kind):
            if t == "frame" and has_w:
                for k in (0, 1):
                    for s in (+1, -1):
                        self.components.append((i, k, s))
            else:
                self.components.append((i, 0, 0))
        self._constraint_definition: list[tuple] = []
        self._cache: dict[str, Any] | None = None
        self.constraint_names: list[str] = []

    # --- design ↔ elements
    @property
    def n_element(self) -> int:
        """Number of elements in the model."""
        return len(self.model.elements)

    def _x(self, x: ArrayLike) -> np.ndarray:
        """Validate a design vector (length n, positive, finite)."""
        x = np.asarray(x, dtype=float)
        if x.shape != (self.n,):
            raise ValueError(f"design vector must have {self.n} entries, got shape {x.shape}")
        if np.any(~np.isfinite(x)) or np.any(x <= 0):
            raise ValueError("design variables must be positive and finite")
        return x

    def areas(self, x: ArrayLike) -> np.ndarray:
        """Element areas ``A_e = x_g(e)`` [m²] for design ``x``.

        Raises
        ------
        ValueError
            If ``x`` has the wrong length or non-positive / non-finite entries.
        """
        return self._x(x)[self.group_no]

    def apply(self, x: ArrayLike) -> np.ndarray:
        """Write design ``x`` into the model elements (``A``, and ``I = I(A)`` for frames).

        Returns
        -------
        numpy.ndarray
            Element areas [m²].
        """
        A = self.areas(x)
        for e, a in zip(self.model.elements, A, strict=True):
            e.A = float(a)
            if isinstance(e, Frame2D) and self.section is not None:
                e.I = float(self.section.I(a))
        return A

    def initial(self) -> np.ndarray:
        """Default starting design: geometric mean of the bounds (``10·lower`` if ``upper`` is infinite)."""
        u = np.where(np.isfinite(self.upper), self.upper, 10 * self.lower)
        return np.sqrt(self.lower * np.maximum(u, self.lower))

    # --- assembly
    def _IdI(self, A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Element ``I(A)`` and ``dI/dA`` (zeros without a section family)."""
        if self.section is None:
            return np.zeros_like(A), np.zeros_like(A)
        return self.section.I(A), self.section.dI(A)

    def _dk(self, A: np.ndarray) -> np.ndarray:
        """Element stiffness derivatives ``dk_e/dA_e = k_A + I'(A_e) k_I``."""
        _, dI = self._IdI(A)
        return self.kA + dI[:, None, None] * self.kI

    def K(self, x: ArrayLike) -> sp.csr_matrix:
        """Global stiffness matrix (full DOF set, sparse CSR) for design ``x``."""
        A = self.areas(x)
        I, _ = self._IdI(A)
        ke = A[:, None, None] * self.kA + I[:, None, None] * self.kI
        n = self.model.n_dof
        return sp.coo_matrix((ke.ravel(), (self._rows, self._cols)), shape=(n, n)).tocsr()

    def M(self, x: ArrayLike) -> sp.csr_matrix:
        """Global mass matrix (structural + extra mass, sparse CSR) for design ``x``."""
        A = self.areas(x)
        me = A[:, None, None] * self.mA
        n = self.model.n_dof
        return (sp.coo_matrix((me.ravel(), (self._rows, self._cols)), shape=(n, n))
                + sp.diags(self.extra_mass)).tocsr()

    def _analysis(self, x: ArrayLike) -> dict[str, Any]:
        """Static solution, LU factor and pseudo-loads for design ``x`` (cached on the last design)."""
        x = self._x(x)
        if self._cache is not None and np.array_equal(self._cache["x"], x):
            return self._cache
        A = x[self.group_no]
        K = self.K(x)
        f = self.free
        Kff = K[f][:, f].tocsc()
        with warnings.catch_warnings():
            warnings.simplefilter("error", spla.MatrixRankWarning)
            try:
                lu = spla.splu(Kff)
            except (RuntimeError, spla.MatrixRankWarning) as error:
                raise ValueError(f"stiffness matrix is singular (mechanism or missing support): {error}") from error
        U = np.zeros_like(self.F)
        U[f] = lu.solve(self.F[f])
        residual = np.linalg.norm(Kff @ U[f] - self.F[f]) / np.linalg.norm(self.F[f])
        if not np.all(np.isfinite(U)) or residual > 1e-8:
            raise ValueError(f"static solution could not be verified (relative residual {residual:.1e}); "
                             "model singular or ill-conditioned")
        dk = self._dk(A)
        # pseudo-loads: P_lc[:, g] = (dK/dx_g) u
        pseudo = []
        for j in range(self.n_disp):
            ue = U[self.DOF, j]
            v = np.einsum("eij,ej->ei", dk, ue)
            Pj = np.zeros((self.model.n_dof, self.n))
            np.add.at(Pj, (self.DOF, np.broadcast_to(self.group_no[:, None], self.DOF.shape)), v)
            pseudo.append(Pj)
        self._cache = dict(x=x.copy(), A=A, K=K, Kff=Kff, lu=lu, U=U, dk=dk, pseudo=pseudo, du={})
        return self._cache

    def _solve(self, an: dict[str, Any], R: ArrayLike) -> np.ndarray:
        """Solve ``K Y = R`` on the free DOFs with the cached factorization."""
        R = np.atleast_2d(np.asarray(R, dtype=float).T).T
        Y = np.zeros_like(R)
        Y[self.free] = an["lu"].solve(np.ascontiguousarray(R[self.free]))
        return Y

    def _du(self, an: dict[str, Any], j: int) -> np.ndarray:
        """Displacement derivatives ``du_j/dx = −K⁻¹ (dK/dx) u_j`` (cached per load case)."""
        if j not in an["du"]:
            an["du"][j] = -self._solve(an, an["pseudo"][j])
        return an["du"][j]

    def _linear_derivative(self, an: dict[str, Any], j: int, Q: ArrayLike, explicit: Any = None,
                           method: str | None = None) -> np.ndarray:
        """Derivatives ``dr/dx`` of rows ``r = Qᵀu_j`` (+ explicit term), ``Q`` of shape (n_dof, r)."""
        Q = np.atleast_2d(np.asarray(Q, dtype=float).T).T
        r = Q.shape[1]
        method = method or self.sensitivity
        if method == "auto":
            method = "direct" if (j in an["du"] or self.n <= r) else "adjoint"
        if method == "direct":
            D = Q.T @ self._du(an, j)
        else:
            lam = self._solve(an, Q)
            D = -lam.T @ an["pseudo"][j]
        return D if explicit is None else D + explicit

    # --- responses
    def volume(self, x: ArrayLike, derivative: bool = False) -> float | tuple[float, np.ndarray]:
        """Material volume ``V = Σ L_e A_e`` [m³].

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        derivative : bool
            Also return ``dV/dx`` (length n).

        Returns
        -------
        float or (float, numpy.ndarray)
        """
        A = self.areas(x)
        h = float(self.L @ A)
        return (h, self.L @ self.P) if derivative else h

    def mass(self, x: ArrayLike, derivative: bool = False) -> float | tuple[float, np.ndarray]:
        """Structural mass ``m = Σ ρ_e L_e A_e`` [kg] (extra mass excluded).

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        derivative : bool
            Also return ``dm/dx`` (length n).

        Returns
        -------
        float or (float, numpy.ndarray)

        Raises
        ------
        ValueError
            If any element has ``rho ≤ 0`` (use :meth:`volume` instead).
        """
        if np.any(self.rho <= 0):
            raise ValueError("mass requires rho > 0 in every element (use 'volume' if only volume is needed)")
        A = self.areas(x)
        m = float((self.rho * self.L) @ A)
        return (m, (self.rho * self.L) @ self.P) if derivative else m

    def compliance(self, x: ArrayLike, derivative: bool = False) -> float | tuple[float, np.ndarray]:
        """Compliance ``C = Σ_lc Fᵀu`` summed over load cases [J].

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        derivative : bool
            Also return ``dC/dx = −Σ uᵀ (dK/dx) u`` (length n).

        Returns
        -------
        float or (float, numpy.ndarray)
        """
        an = self._analysis(x)
        C = float(np.sum(self.F * an["U"]))
        if not derivative:
            return C
        d = -sum(an["U"][:, j] @ an["pseudo"][j] for j in range(self.n_disp))
        return C, d

    def displacement(self, x: ArrayLike, dofs: ArrayLike, load_case: int = 0, derivative: bool = False,
                     method: str | None = None) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """Displacements at the given global DOFs for one load case [m or rad].

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        dofs : array_like of int
            Global DOF indices.
        load_case : int
            Load case index.
        derivative : bool
            Also return ``du/dx`` of shape (len(dofs), n).
        method : {"direct", "adjoint", "auto"}, optional
            Sensitivity method (default: the problem's setting).

        Returns
        -------
        numpy.ndarray or (numpy.ndarray, numpy.ndarray)
        """
        an = self._analysis(x)
        dofs = np.atleast_1d(np.asarray(dofs, dtype=int))
        u = an["U"][dofs, load_case]
        if not derivative:
            return u
        Q = np.zeros((self.model.n_dof, dofs.size))
        Q[dofs, np.arange(dofs.size)] = 1.0
        return u, self._linear_derivative(an, load_case, Q, method=method)

    def _stress_rows(self, A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Per component: row ``q`` with ``σ = qᵀu_e`` (local DOFs) and explicit ``dσ/dA_e`` row (times u_e)."""
        nb = len(self.components)
        nd = self.DOF.shape[1]
        Q = np.zeros((nb, nd))
        Qa = np.zeros((nb, nd))
        iw = diw = np.zeros_like(A)
        if self.section is not None and self.section.w is not None:
            iw, diw = self.section.I_W(A), self.section.dI_W(A)
        for b, (i, k, s) in enumerate(self.components):
            Q[b] = self.nu[i]
            if s:
                Q[b] += s * iw[i] * self.rM[i, k]
                Qa[b] = s * diw[i] * self.rM[i, k]
        return Q, Qa

    def stresses(self, x: ArrayLike, derivative: bool = False,
                 method: str | None = None) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """Stresses of all components [Pa], shape (n_disp, n_component).

        Truss: axial stress. Frame (with ``W`` defined): ends 1/2, top/bottom fiber ``N/A ± M/W``.

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        derivative : bool
            Also return ``dσ/dx`` of shape (n_disp, n_component, n).
        method : {"direct", "adjoint", "auto"}, optional
            Sensitivity method.

        Returns
        -------
        numpy.ndarray or (numpy.ndarray, numpy.ndarray)
        """
        an = self._analysis(x)
        A = an["A"]
        Q, Qa = self._stress_rows(A)
        el = np.array([b[0] for b in self.components])
        S = np.zeros((self.n_disp, len(el)))
        J = np.zeros((self.n_disp, len(el), self.n))
        for j in range(self.n_disp):
            ue = an["U"][self.DOF[el], j]
            S[j] = np.einsum("bi,bi->b", Q, ue)
            if derivative:
                Qg = np.zeros((self.model.n_dof, len(el)))
                np.add.at(Qg, (self.DOF[el], np.broadcast_to(np.arange(len(el))[:, None], self.DOF[el].shape)), Q)
                explicit = np.einsum("bi,bi->b", Qa, ue)[:, None] * self.P[el]
                J[j] = self._linear_derivative(an, j, Qg, explicit, method=method)
        return (S, J) if derivative else S

    def component_name(self, b: int) -> str:
        """Readable name of stress component ``b``, e.g. ``"e3"`` or ``"e3 end1 top"``."""
        i, k, s = self.components[b]
        return f"e{i + 1}" if s == 0 else f"e{i + 1} end{k + 1} {'top' if s > 0 else 'bottom'}"

    def _sigma_cr(self, A: np.ndarray, K: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Euler critical stress ``π²E·I/((K·L)²·A)`` and its derivative with respect to A."""
        if self.section is None:
            raise ValueError("Euler buckling requires a section family (I = c·A^p)")
        I, dI = self._IdI(A)
        LK2 = (K * self.L) ** 2
        s = math.pi ** 2 * self.E * I / (LK2 * A)
        ds = math.pi ** 2 * self.E * (dI * A - I) / (LK2 * A * A)
        return s, ds

    @cite("timoshenko_gere_1961", note="Euler column load π²EI/(KL)²")
    def euler_ratio(self, x: ArrayLike, K: ArrayLike = 1.0, derivative: bool = False,
                    method: str | None = None) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """Element Euler buckling ratio ``r_e = −σ_axial/σ_cr``, shape (n_disp, n_element).

        ``σ_cr = π²E·I/((K·L)²·A)``; ``r ≤ 1`` means no buckling (tension gives ``r < 0``).

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        K : float or array_like
            Effective length factor (scalar or per element).
        derivative : bool
            Also return ``dr/dx`` of shape (n_disp, n_element, n).
        method : {"direct", "adjoint", "auto"}, optional
            Sensitivity method.

        Returns
        -------
        numpy.ndarray or (numpy.ndarray, numpy.ndarray)

        Raises
        ------
        ValueError
            Without a section family.
        """
        an = self._analysis(x)
        A = an["A"]
        Kf = np.broadcast_to(np.asarray(K, dtype=float), A.shape)
        scr, dscr = self._sigma_cr(A, Kf)
        n_el = self.n_element
        R = np.zeros((self.n_disp, n_el))
        J = np.zeros((self.n_disp, n_el, self.n))
        for j in range(self.n_disp):
            ue = an["U"][self.DOF, j]
            sig = np.einsum("ei,ei->e", self.nu, ue)
            R[j] = -sig / scr
            if derivative:
                Qg = np.zeros((self.model.n_dof, n_el))
                np.add.at(Qg, (self.DOF, np.broadcast_to(np.arange(n_el)[:, None], self.DOF.shape)),
                          -self.nu / scr[:, None])
                explicit = (sig * dscr / scr ** 2)[:, None] * self.P
                J[j] = self._linear_derivative(an, j, Qg, explicit, method=method)
        return (R, J) if derivative else R

    @cite("haftka_gurdal_1992", note="Ch. 7 eigenvalue sensitivity (not read; derived here)")
    def frequencies(self, x: ArrayLike, n: int = 1, derivative: bool = False) -> dict[str, np.ndarray]:
        """Lowest natural frequencies of the structure.

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        n : int
            Number of modes.
        derivative : bool
            Also return eigenvalue sensitivities and mass-normalized mode shapes.

        Returns
        -------
        dict
            ``lambda_``: eigenvalues ``λ_k = ω_k²`` [rad²/s²] (ascending); ``omega`` [rad/s];
            ``f`` [Hz]; with ``derivative``: ``dlambda`` (n, n_variable) and ``modes``
            (full-DOF mode shapes, ``φᵀMφ = 1``).

        Raises
        ------
        ValueError
            If the generalized eigenproblem cannot be solved (mass matrix not positive definite).

        Warns
        -----
        RuntimeWarning
            For a repeated eigenvalue (sensitivity not defined).

        Notes
        -----
        ``dλ_k/dx = Σ_e φ_eᵀ (dk_e/dA − λ_k m_A) φ_e`` assembled per group.
        """
        A = self.areas(x)
        f = self.free
        Kff = self.K(x)[f][:, f].toarray()
        Mff = self.M(x)[f][:, f].toarray()
        n = int(min(n, f.size))
        m = min(n + 1, f.size)
        try:
            lam, V = sla.eigh(Kff, Mff, subset_by_index=[0, m - 1])
        except np.linalg.LinAlgError as error:
            raise ValueError(f"eigenproblem could not be solved (mass matrix not positive definite?): {error}") \
                from error
        if m > n and lam[n - 1] > 0 and (lam[n] - lam[n - 1]) / lam[n - 1] < 1e-6:
            warnings.warn("repeated eigenvalue: frequency sensitivity is not defined (not differentiable)",
                          RuntimeWarning, stacklevel=2)
        lam, V = lam[:n], V[:, :n]
        result = {"lambda_": lam, "omega": np.sqrt(np.maximum(lam, 0)),
                  "f": np.sqrt(np.maximum(lam, 0)) / (2 * math.pi)}
        if derivative:
            phi = np.zeros((self.model.n_dof, n))
            phi[f] = V
            dk = self._dk(A)
            D = np.zeros((n, self.n))
            for k in range(n):
                pe = phi[self.DOF, k]
                d_e = np.einsum("ei,eij,ej->e", pe, dk - lam[k] * self.mA, pe)
                D[k] = d_e @ self.P
            result["dlambda"] = D
            result["modes"] = phi
        return result

    @cite("haftka_gurdal_1992", note="Ch. 7 eigenvalue sensitivity (not read; derived here, pre-load "
          "dependence included)")
    def buckling_factor(self, x: ArrayLike, load_case: int = 0, derivative: bool = False,
                        method: str | None = None) -> float | tuple[float, np.ndarray]:
        """Linear system buckling load factor λ (smallest positive) of ``(K + λ G(u)) φ = 0``.

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        load_case : int
            Load case defining the pre-load.
        derivative : bool
            Also return ``dλ/dx`` (length n).
        method : {"direct", "adjoint", "auto"}, optional
            Sensitivity method for the pre-load term.

        Returns
        -------
        float or (float, numpy.ndarray)

        Raises
        ------
        ValueError
            If no positive buckling factor exists (the load case produces no compression).

        Warns
        -----
        RuntimeWarning
            For a repeated buckling eigenvalue.

        Notes
        -----
        ``G = Σ N_e ĝ_e`` with ``N_e = A_e ν_eᵀ u_e``. The eigenproblem is solved as
        ``−G φ = μ K φ``, ``λ = 1/μ_max``, and
        ``dλ/dx = −[φᵀ (dK/dx) φ + λ φᵀ (dG/dx) φ] / (φᵀ G φ)``, where ``dG/dx`` includes the
        design dependence of ``N_e`` through ``u`` (adjoint/direct linear sensitivity).
        """
        an = self._analysis(x)
        A, j = an["A"], load_case
        U = an["U"][:, j]
        ue = U[self.DOF]
        nuu = np.einsum("ei,ei->e", self.nu, ue)
        N = A * nuu
        n = self.model.n_dof
        G = sp.coo_matrix(((N[:, None, None] * self.gh).ravel(), (self._rows, self._cols)), shape=(n, n)).tocsr()
        f = self.free
        Kff = an["Kff"].toarray()
        Gff = G[f][:, f].toarray()
        mu, V = sla.eigh(-Gff, Kff)
        positive = mu > 1e-12 * max(np.abs(mu).max(), 1e-300)
        if not np.any(positive):
            raise ValueError("no positive buckling factor (load case produces no compression)")
        k = int(np.argmax(np.where(positive, mu, -np.inf)))
        lam = 1.0 / mu[k]
        ordered = np.sort(mu[positive])[::-1]
        if ordered.size > 1 and (ordered[0] - ordered[1]) / ordered[0] < 1e-6:
            warnings.warn("repeated buckling eigenvalue: sensitivity is not defined", RuntimeWarning, stacklevel=2)
        if not derivative:
            return lam
        phi = np.zeros(n)
        phi[f] = V[:, k]
        pe = phi[self.DOF]
        dk = an["dk"]
        t1 = np.einsum("ei,eij,ej->e", pe, dk, pe) @ self.P
        c = np.einsum("ei,eij,ej->e", pe, self.gh, pe)          # φᵀ ĝ_e φ
        explicit = (c * nuu) @ self.P                           # ∂N_e/∂A_e = νᵀu_e
        w = np.zeros(n)
        np.add.at(w, self.DOF, (c * A)[:, None] * self.nu)
        t2 = explicit + self._linear_derivative(an, j, w[:, None], method=method)[0]
        pGp = phi[f] @ Gff @ phi[f]
        return lam, -(t1 + lam * t2) / pGp

    # --- constraint definitions
    def stress_limit(self, tension: ArrayLike, compression: ArrayLike | None = None,
                     elements: ArrayLike | None = None) -> SizeProblem:
        """Add stress constraints ``σ ≤ σ_tension`` and ``−σ ≤ σ_compression``.

        Parameters
        ----------
        tension : float or array_like
            Allowable tensile stress [Pa], scalar or per entry of ``elements``.
        compression : float or array_like, optional
            Allowable compressive stress as a positive magnitude [Pa]; ``None``: same as tension.
        elements : array_like of int, optional
            Constrained elements (default: all).

        Returns
        -------
        SizeProblem
            ``self`` (chainable).

        Raises
        ------
        ValueError
            For an invalid element list or non-positive limits.
        """
        el = np.arange(self.n_element) if elements is None else np.asarray(elements, dtype=int)
        if el.size == 0 or el.min() < 0 or el.max() >= self.n_element:
            raise ValueError("invalid element list")
        st = np.broadcast_to(np.asarray(tension, dtype=float), el.shape).copy()
        sc = st.copy() if compression is None else np.broadcast_to(np.asarray(compression, dtype=float),
                                                                    el.shape).copy()
        if np.any(st <= 0) or np.any(sc <= 0):
            raise ValueError("stress limits must be positive (compression is given as a magnitude)")
        full_t = np.full(self.n_element, np.nan)
        full_c = np.full(self.n_element, np.nan)
        full_t[el], full_c[el] = st, sc
        self._constraint_definition.append(("stress", full_t, full_c))
        return self

    def displacement_limit(self, dofs: Sequence[int | tuple[int, int]], limit: ArrayLike,
                           load_cases: Sequence[int] | None = None) -> SizeProblem:
        """Add displacement constraints ``|u_k| ≤ limit``.

        Parameters
        ----------
        dofs : sequence
            Global DOF indices or ``(node, local_dof)`` pairs.
        limit : float or array_like
            Allowable displacement magnitude [m or rad], scalar or per DOF.
        load_cases : sequence of int, optional
            Load cases to constrain (default: all).

        Returns
        -------
        SizeProblem
            ``self`` (chainable).

        Raises
        ------
        ValueError
            For invalid or fixed DOFs, non-positive limits or invalid load cases.
        """
        idx_list = [self.model.dof(*s) if isinstance(s, tuple | list) else int(s) for s in dofs]
        idx = np.array(idx_list, dtype=int)
        if idx.size == 0 or idx.min() < 0 or idx.max() >= self.model.n_dof:
            raise ValueError("invalid DOF list")
        if np.isin(idx, self.free, invert=True).any():
            raise ValueError("a displacement limit on a fixed DOF is meaningless")
        d = np.broadcast_to(np.asarray(limit, dtype=float), idx.shape).copy()
        if np.any(d <= 0):
            raise ValueError("displacement limit must be positive")
        cases = list(range(self.n_disp)) if load_cases is None else list(load_cases)
        if any(not 0 <= j < self.n_disp for j in cases):
            raise ValueError("invalid load case")
        self._constraint_definition.append(("displacement", idx, d, cases))
        return self

    def euler_buckling_limit(self, K: float = 1.0, elements: ArrayLike | None = None) -> SizeProblem:
        """Add element Euler buckling constraints ``σ ≥ −π²E·I/((K·L)²·A)``, i.e. ``r = −σ/σ_cr ≤ 1``.

        Parameters
        ----------
        K : float
            Effective length factor.
        elements : array_like of int, optional
            Constrained elements (default: all).

        Returns
        -------
        SizeProblem
            ``self`` (chainable).

        Raises
        ------
        ValueError
            Without a section family, for an invalid element list or ``K ≤ 0``.
        """
        if self.section is None:
            raise ValueError("Euler buckling requires a section family (I = c·A^p)")
        el = np.arange(self.n_element) if elements is None else np.asarray(elements, dtype=int)
        if el.size == 0 or el.min() < 0 or el.max() >= self.n_element:
            raise ValueError("invalid element list")
        if np.any(np.asarray(K) <= 0):
            raise ValueError("effective length factor must be positive")
        self._constraint_definition.append(("euler", el, float(K)))
        return self

    def frequency_limit(self, f_min: float) -> SizeProblem:
        """Add the constraint first natural frequency ``f1 ≥ f_min`` [Hz].

        Returns
        -------
        SizeProblem
            ``self`` (chainable).

        Raises
        ------
        ValueError
            If ``f_min ≤ 0`` or the model has no mass (rho or extra_mass).
        """
        if f_min <= 0:
            raise ValueError("frequency limit must be positive")
        if not np.any(self.rho > 0) and not np.any(self.extra_mass > 0):
            raise ValueError("a frequency constraint requires mass (rho or extra_mass)")
        self._constraint_definition.append(("frequency", float(f_min)))
        return self

    def buckling_limit(self, lambda_min: float, load_case: int = 0) -> SizeProblem:
        """Add the constraint system linear buckling factor ``λ ≥ lambda_min``.

        Returns
        -------
        SizeProblem
            ``self`` (chainable).

        Raises
        ------
        ValueError
            If ``lambda_min ≤ 0`` or the load case is invalid.
        """
        if lambda_min <= 0 or not 0 <= load_case < self.n_disp:
            raise ValueError("lambda_min must be positive and the load case valid")
        self._constraint_definition.append(("buckling", float(lambda_min), int(load_case)))
        return self

    def compliance_limit(self, C_max: float) -> SizeProblem:
        """Add the constraint compliance ``C ≤ C_max`` [J].

        Returns
        -------
        SizeProblem
            ``self`` (chainable).

        Raises
        ------
        ValueError
            If ``C_max ≤ 0``.
        """
        if C_max <= 0:
            raise ValueError("compliance limit must be positive")
        self._constraint_definition.append(("compliance", float(C_max)))
        return self

    def constraints(self, x: ArrayLike, derivative: bool = False) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        """Evaluate all normalized constraints ``g`` (``g ≤ 0`` feasible).

        Also sets :attr:`constraint_names` (one name per row).

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        derivative : bool
            Also return the Jacobian of shape (m, n).

        Returns
        -------
        numpy.ndarray or (numpy.ndarray, numpy.ndarray)

        Notes
        -----
        Normalizations: stress ``σ/σ_t − 1``, ``−σ/σ_c − 1``; displacement ``±u/δ − 1``;
        Euler ``r − 1``; frequency ``1 − λ1/λ_min``; buckling ``1 − λ/λ_min``; compliance ``C/C_max − 1``.
        Names use ``LC<j>`` for the load case and ``n<node>.<local>`` for a DOF (1-based node).
        """
        g: list[float] = []
        J: list[Any] = []
        name: list[str] = []
        for t in self._constraint_definition:
            if t[0] == "stress":
                _, st, sc = t
                S, D = _with_derivative(self.stresses(x, derivative=derivative), derivative)
                el = np.array([b[0] for b in self.components])
                select = np.where(~np.isnan(st[el]))[0]
                for j in range(self.n_disp):
                    for b in select:
                        i = el[b]
                        g += [S[j, b] / st[i] - 1, -S[j, b] / sc[i] - 1]
                        name += [f"stress tension {self.component_name(b)} LC{j + 1}",
                                 f"stress compression {self.component_name(b)} LC{j + 1}"]
                        if derivative:
                            J += [D[j, b] / st[i], -D[j, b] / sc[i]]
            elif t[0] == "displacement":
                _, idx, d, cases = t
                for j in cases:
                    u, D = _with_derivative(self.displacement(x, idx, j, derivative=derivative), derivative)
                    for k in range(idx.size):
                        node, local = divmod(int(idx[k]), self.model.ndof)
                        g += [u[k] / d[k] - 1, -u[k] / d[k] - 1]
                        name += [f"displacement n{node + 1}.{local} (+) LC{j + 1}",
                                 f"displacement n{node + 1}.{local} (−) LC{j + 1}"]
                        if derivative:
                            J += [D[k] / d[k], -D[k] / d[k]]
            elif t[0] == "euler":
                _, el, K = t
                R, D = _with_derivative(self.euler_ratio(x, K, derivative=derivative), derivative)
                for j in range(self.n_disp):
                    for i in el:
                        g.append(R[j, i] - 1)
                        name.append(f"Euler e{i + 1} LC{j + 1}")
                        if derivative:
                            J.append(D[j, i])
            elif t[0] == "frequency":
                lmin = (2 * math.pi * t[1]) ** 2
                s = self.frequencies(x, 1, derivative=derivative)
                g.append(1 - s["lambda_"][0] / lmin)
                name.append("frequency f1")
                if derivative:
                    J.append(-s["dlambda"][0] / lmin)
            elif t[0] == "buckling":
                _, lmin, j = t
                lam, D = _with_derivative(self.buckling_factor(x, j, derivative=derivative), derivative)
                g.append(1 - lam / lmin)
                name.append(f"system buckling LC{j + 1}")
                if derivative:
                    J.append(-D / lmin)
            elif t[0] == "compliance":
                C, D = _with_derivative(self.compliance(x, derivative=derivative), derivative)
                g.append(C / t[1] - 1)
                name.append("compliance")
                if derivative:
                    J.append(D / t[1])
        self.constraint_names = name
        g_arr = np.array(g, dtype=float)
        if derivative:
            return g_arr, (np.array(J, dtype=float).reshape(len(g_arr), self.n))
        return g_arr

    def objective(self, x: ArrayLike, objective: str = "mass",
                  derivative: bool = False) -> float | tuple[float, np.ndarray]:
        """Evaluate an objective by name.

        Parameters
        ----------
        x : array_like
            Design vector [m²].
        objective : {"mass", "volume", "compliance"}
            Objective name.
        derivative : bool
            Also return the gradient.

        Returns
        -------
        float or (float, numpy.ndarray)

        Raises
        ------
        ValueError
            For an unknown objective.
        """
        if objective == "mass":
            return self.mass(x, derivative)
        if objective == "volume":
            return self.volume(x, derivative)
        if objective == "compliance":
            return self.compliance(x, derivative)
        raise ValueError(f"unknown objective '{objective}' (mass, volume, compliance)")

    def max_violation(self, x: ArrayLike) -> float:
        """Largest normalized constraint violation ``max(0, max g)`` (0 if feasible or unconstrained)."""
        g = cast(np.ndarray, self.constraints(x))
        return float(max(0.0, g.max())) if g.size else 0.0


# ---------------------------------------------------------------- result
@dataclass
class OptResult:
    """Result of a sizing optimization.

    Attributes
    ----------
    method : str
        Method label.
    x : numpy.ndarray
        Optimal design variables [m²].
    areas : numpy.ndarray
        Element areas [m²].
    objective_name : str
        ``"mass"``, ``"volume"`` or ``"compliance"``.
    objective : float
        Objective value at ``x``.
    mass : float or None
        Structural mass [kg] (``None`` if some element has ``rho ≤ 0``).
    max_violation : float
        Largest normalized constraint violation.
    active_constraints : list of str
        Names of constraints with ``g > −tol``.
    active_bounds : list of (int, str)
        Variables at a bound: ``(index, "lower" | "upper")``.
    history : dict
        Iteration history: ``objective``, ``mass``, ``violation``, ``x`` (and ``R`` for OC).
    iteration : int
        Number of iterations.
    successful : bool
        Convergence flag.
    message : str
        Termination message.
    extra : dict
        Method-specific data (e.g. OC constraint name, response ``R`` and ``limit``).
    """

    method: str
    x: np.ndarray
    areas: np.ndarray
    objective_name: str
    objective: float
    mass: float | None
    max_violation: float
    active_constraints: list
    active_bounds: list
    history: dict
    iteration: int
    successful: bool
    message: str
    extra: dict = field(default_factory=dict)

    def summary(self) -> str:
        """Multi-line plain-text summary (method, objective, violation, design, active set, verdict)."""
        active = ", ".join(self.active_constraints[:8]) + (" …" if len(self.active_constraints) > 8 else "")
        bounds = ", ".join(f"x{i + 1}={side}" for i, side in self.active_bounds[:10])
        rows = [
            f"Method: {self.method} · {self.iteration} iterations · "
            f"{'converged' if self.successful else 'NOT CONVERGED'} ({self.message})",
            f"Objective ({self.objective_name}): {self.objective:.6g}"
            + (f" · mass {self.mass:.6g}" if self.mass is not None else ""),
            f"Max. constraint violation (normalized): {self.max_violation:.2e}",
            "Design: " + ", ".join(f"x{i + 1}={v:.5g}" for i, v in enumerate(self.x)),
            f"Active constraints ({len(self.active_constraints)}): {active or 'none'}",
            f"Variables at bounds: {bounds or 'none'}",
        ]
        if self.max_violation > 1e-4:
            rows.append("Result: design INFEASIBLE; constraints are not satisfied.")
        else:
            rows.append("Result: design feasible." + (" The active constraints govern the sizing."
                                                       if self.active_constraints else ""))
        return "\n".join(rows)


def _actives(pr: SizeProblem, x: np.ndarray, tol: float) -> tuple[list[str], list[tuple[int, str]], float]:
    """Active constraint names, variables at bounds and the maximum violation at ``x``."""
    g = cast(np.ndarray, pr.constraints(x))
    active = [pr.constraint_names[i] for i in np.where(g > -tol)[0]]
    bounds = [(i, "lower") for i in range(pr.n) if x[i] <= pr.lower[i] * (1 + tol)] + \
             [(i, "upper") for i in range(pr.n) if np.isfinite(pr.upper[i]) and x[i] >= pr.upper[i] * (1 - tol)]
    return active, bounds, (float(max(0.0, g.max())) if g.size else 0.0)


def _mass_or_none(pr: SizeProblem, x: np.ndarray) -> float | None:
    """Structural mass, or ``None`` if some element has no density."""
    return pr.mass(x) if np.all(pr.rho > 0) else None  # type: ignore[return-value]


def _result(pr: SizeProblem, method: str, x: np.ndarray, objective: str, history: dict, it: int,
            successful: bool, message: str, tol_active: float = 1e-4, extra: dict | None = None) -> OptResult:
    """Build an :class:`OptResult` at design ``x``."""
    active, bounds, violation = _actives(pr, x, tol_active)
    return OptResult(method, x.copy(), pr.areas(x), objective, pr.objective(x, objective),  # type: ignore[arg-type]
                     _mass_or_none(pr, x), violation, active, bounds, history, it, successful, message, extra or {})


def _add_history(pr: SizeProblem, history: dict, x: np.ndarray, objective: str) -> None:
    """Append objective, mass, violation and design to ``history``."""
    history["objective"].append(pr.objective(x, objective))
    history["mass"].append(_mass_or_none(pr, x))
    history["violation"].append(pr.max_violation(x))
    history["x"].append(x.copy())


def _new_history() -> dict[str, list]:
    """Empty iteration history."""
    return {"objective": [], "mass": [], "violation": [], "x": []}


# ---------------------------------------------------------------- fully stressed design
@cite("haftka_gurdal_1992", note="Ch. 9 fully stressed design (not read; derived here)")
def fully_stressed_design(pr: SizeProblem, x0: ArrayLike | None = None, max_iter: int = 200, tol: float = 1e-9,
                          euler_K: float | None = None) -> OptResult:
    """Stress-ratio iteration (fully stressed design, FSD).

    Parameters
    ----------
    pr : SizeProblem
        Problem with at least one :meth:`SizeProblem.stress_limit` definition.
    x0 : array_like, optional
        Starting design [m²] (default :meth:`SizeProblem.initial`).
    max_iter : int
        Maximum number of resizing steps.
    tol : float
        Convergence tolerance on the maximum relative change of ``x``.
    euler_K : float, optional
        If given, the Euler ratio with this effective length factor is also enforced.

    Returns
    -------
    OptResult
        Objective is mass if every element has ``rho > 0``, otherwise volume.

    Raises
    ------
    ValueError
        If no stress limit is defined.

    Notes
    -----
    Update ``x_g ← x_g · max_{e∈g, lc}(σ/σ_allow)``, clipped to the bounds. With ``euler_K``:
    in a statically determinate truss ``σ ∝ 1/A`` and ``σ_cr ∝ A^(p−1)``, so ``r ∝ A^(−p)`` and the
    required factor is ``r^(1/p)``. For a determinate structure the fully stressed design
    ``A = |N|/σ_allow`` is reached in one step.
    """
    definition = [t for t in pr._constraint_definition if t[0] == "stress"]
    if not definition:
        raise ValueError("fully stressed design requires a stress_limit definition")
    st = np.full(pr.n_element, np.nan)
    sc = np.full(pr.n_element, np.nan)
    for _, a, b in definition:
        m = ~np.isnan(a)
        st[m], sc[m] = a[m], b[m]
    x = pr._x(pr.initial() if x0 is None else x0).copy()
    el = np.array([b[0] for b in pr.components])
    objective = "mass" if np.all(pr.rho > 0) else "volume"
    history = _new_history()
    _add_history(pr, history, x, objective)
    successful, message = False, "maximum number of iterations reached"
    it = 0
    for _ in range(max_iter):
        it += 1
        S = cast(np.ndarray, pr.stresses(x))
        ratio = np.where(S >= 0, S / st[el], -S / sc[el])            # (n_disp, n_component)
        ratio = np.where(np.isnan(ratio), 0.0, ratio).max(axis=0)
        e_ratio = np.zeros(pr.n_element)
        np.maximum.at(e_ratio, el, ratio)
        if euler_K is not None:
            r = cast(np.ndarray, pr.euler_ratio(x, euler_K)).max(axis=0)          # raises without a section family
            p = pr.section.p if pr.section is not None else 1.0
            e_ratio = np.maximum(e_ratio, np.maximum(r, 0) ** (1 / p))
        factor = np.zeros(pr.n)
        np.maximum.at(factor, pr.group_no, e_ratio)
        new = np.clip(x * factor, pr.lower, pr.upper)
        change = np.max(np.abs(new - x) / x)
        x = new
        _add_history(pr, history, x, objective)
        if change < tol:
            successful, message = True, f"relative change {change:.1e} < {tol:g}"
            break
    return _result(pr, "fully stressed design (FSD)", x, objective, history, it, successful, message)


# ---------------------------------------------------------------- optimality criterion
@cite("haftka_gurdal_1992", note="Ch. 9 optimality criteria (not read; derived here)")
def optimality_criterion(pr: SizeProblem, constraint: str | int | tuple[int, int] = "compliance",
                         limit: float | None = None, x0: ArrayLike | None = None, objective: str = "mass",
                         load_case: int = 0, eta: float = 0.5, move: float | None = 10.0, max_iter: int = 300,
                         tol: float = 1e-9) -> OptResult:
    """Minimum mass (or volume) under a single constraint ``R(x) ≤ limit`` by an optimality criterion.

    Parameters
    ----------
    pr : SizeProblem
        Sizing problem (its own constraint definitions are only used for reporting).
    constraint : "compliance", int or (node, local_dof)
        ``"compliance"`` [J] or a displacement magnitude ``|u_k|`` [m] at a free DOF.
    limit : float
        Positive constraint limit.
    x0 : array_like, optional
        Starting design [m²].
    objective : {"mass", "volume"}
        Objective.
    load_case : int
        Load case for a displacement constraint.
    eta : float
        Damping exponent in (0, 1].
    move : float or None
        Multiplicative move limit (> 1) per step; ``None`` disables it.
    max_iter : int
        Maximum number of iterations.
    tol : float
        Convergence tolerance on the maximum relative change of ``x``.

    Returns
    -------
    OptResult
        ``extra`` holds ``constraint`` (name), ``R`` (final response) and ``limit``; ``history``
        additionally holds ``R``. ``successful`` is set to False if the final ``R/limit − 1 > 1e-6``.

    Raises
    ------
    ValueError
        For a missing/non-positive limit, invalid ``eta`` or ``move``, a non-free constraint DOF, or
        if no variable reduces the response (all ``B_i ≤ 0``).

    Notes
    -----
    Stationarity ``∂W/∂x_i + λ ∂R/∂x_i = 0`` gives ``B_i = −(∂R/∂x_i)/(∂W/∂x_i) = 1/λ``. Update
    ``x_i ← x_i (λ B_i)^η``, with λ found by bisection (in ``log λ``) such that the response
    linearized in reciprocal variables equals the limit:
    ``R ≈ R0 + Σ ∂R/∂x_i · x_i (1 − x_i/x_i,new)``. In a determinate truss ``R = Σ c_i/x_i`` is exactly
    reciprocal-linear; with ``η = ½`` the closed form is obtained in one step. Variables with
    ``B_i ≤ 0`` (response does not decrease with area) go to the lower bound.
    """
    if limit is None or limit <= 0:
        raise ValueError("a positive constraint limit is required")
    if not 0 < eta <= 1:
        raise ValueError("eta must be in (0, 1]")
    if move is not None and move <= 1:
        raise ValueError("move limit (factor) must be greater than 1")
    response: Callable[[np.ndarray], tuple[float, np.ndarray]]
    if constraint == "compliance":
        def response(x: np.ndarray) -> tuple[float, np.ndarray]:
            return pr.compliance(x, derivative=True)  # type: ignore[return-value]
        name = "compliance"
    else:
        k = pr.model.dof(*constraint) if isinstance(constraint, tuple | list) else int(constraint)
        if k not in set(pr.free.tolist()):
            raise ValueError("the constraint DOF must be free")
        x_first = pr._x(pr.initial() if x0 is None else x0)
        sign = np.sign(pr.displacement(x_first, [k], load_case)[0]) or 1.0

        def response(x: np.ndarray) -> tuple[float, np.ndarray]:
            u, d = pr.displacement(x, [k], load_case, derivative=True)
            return sign * u[0], sign * d[0]
        name = f"|u| DOF {k}"
    x = pr._x(pr.initial() if x0 is None else x0).copy()
    history = _new_history()
    history["R"] = []
    successful, message, it = False, "maximum number of iterations reached", 0
    for _ in range(max_iter):
        it += 1
        R, dR = response(x)
        _, dW = pr.objective(x, objective, derivative=True)  # type: ignore[misc]
        _add_history(pr, history, x, objective)
        history["R"].append(R)
        B = -dR / dW
        if not np.any(B > 0):
            raise ValueError("no variable reduces the constraint response (B_i ≤ 0); OC is not applicable")
        lo = pr.lower.copy() if move is None else np.maximum(pr.lower, x / move)
        hi = pr.upper.copy() if move is None else np.minimum(pr.upper, x * move)
        Bp = np.maximum(B, 0)

        def x_new(log_lam: float, x: np.ndarray = x, Bp: np.ndarray = Bp, lo: np.ndarray = lo,
                  hi: np.ndarray = hi) -> np.ndarray:
            with np.errstate(divide="ignore", over="ignore"):
                t = x * np.exp(eta * (log_lam + np.log(np.where(Bp > 0, Bp, 1.0))))
            t = np.where(Bp > 0, t, lo)
            return np.clip(t, lo, hi)

        def R_approx(log_lam: float, R: float = R, dR: np.ndarray = dR, x: np.ndarray = x) -> float:
            xn = x_new(log_lam)
            return R + np.sum(dR * x * (1 - x / xn))

        a, b = -700.0, 700.0
        for _ in range(200):
            m = 0.5 * (a + b)
            if R_approx(m) > limit:
                a = m
            else:
                b = m
            if b - a < 1e-14:
                break
        xn = x_new(b)
        change = np.max(np.abs(xn - x) / x)
        x = xn
        if change < tol:
            successful, message = True, f"relative change {change:.1e} < {tol:g}"
            break
    R, _ = response(x)
    _add_history(pr, history, x, objective)
    history["R"].append(R)
    s = _result(pr, f"optimality criterion (OC, η={eta:g})", x, objective, history, it, successful, message,
                extra={"constraint": name, "R": R, "limit": limit})
    ratio = R / limit - 1
    if ratio > 1e-6:
        s.successful = False
        s.message += f"; OC constraint violated: R/limit − 1 = {ratio:.2e}"
    return s


# ---------------------------------------------------------------- SLSQP
@cite("nocedal_wright_2006", note="Ch. 18 sequential quadratic programming; implementation is scipy's SLSQP")
def slsqp(pr: SizeProblem, x0: ArrayLike | None = None, objective: str = "mass", max_iter: int = 500,
          ftol: float = 1e-12, tol_active: float = 1e-4) -> OptResult:
    """Solve the sizing problem with scipy SLSQP and analytic gradients.

    Parameters
    ----------
    pr : SizeProblem
        Problem with its constraint definitions (may be empty: bounds only).
    x0 : array_like, optional
        Starting design [m²] (default :meth:`SizeProblem.initial`).
    objective : {"mass", "volume", "compliance"}
        Objective.
    max_iter : int
        SLSQP ``maxiter``.
    ftol : float
        SLSQP ``ftol`` (on the scaled objective).
    tol_active : float
        Threshold ``g > −tol_active`` for reporting active constraints.

    Returns
    -------
    OptResult

    Raises
    ------
    ValueError
        If the initial objective value is zero.

    Notes
    -----
    The objective is divided by its starting value; constraints are already normalized and are
    passed as ``−g ≥ 0``. The final design is clipped to the bounds.
    """
    x0 = pr._x(pr.initial() if x0 is None else x0).copy()
    f0 = abs(pr.objective(x0, objective))  # type: ignore[arg-type]
    if f0 == 0:
        raise ValueError("initial objective value is zero")
    history = _new_history()
    _add_history(pr, history, x0, objective)

    def fun(x: np.ndarray) -> tuple[float, np.ndarray]:
        v, d = pr.objective(np.maximum(x, 1e-300), objective, derivative=True)  # type: ignore[misc]
        return v / f0, d / f0

    def cfun(x: np.ndarray) -> np.ndarray:
        return -cast(np.ndarray, pr.constraints(np.maximum(x, 1e-300)))

    def cjac(x: np.ndarray) -> np.ndarray:
        return -pr.constraints(np.maximum(x, 1e-300), derivative=True)[1]

    cons = []
    if pr._constraint_definition:
        cons = [{"type": "ineq", "fun": cfun, "jac": cjac}]
    bounds = [(a, None if not np.isfinite(b) else b) for a, b in zip(pr.lower, pr.upper, strict=True)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        r = minimize(fun, x0, jac=True, method="SLSQP", bounds=bounds, constraints=cons,
                     callback=lambda xk: _add_history(pr, history, np.maximum(xk, pr.lower), objective),
                     options={"maxiter": max_iter, "ftol": ftol})
    x = np.clip(r.x, pr.lower, pr.upper)
    if not np.array_equal(history["x"][-1], x):
        _add_history(pr, history, x, objective)
    return _result(pr, "SLSQP (analytic gradient)", x, objective, history, int(r.nit), bool(r.success), r.message,
                   tol_active=tol_active)


# ---------------------------------------------------------------- KKT
@cite("nocedal_wright_2006", note="Thm. 12.1 first-order (KKT) optimality conditions")
def kkt_audit(pr: SizeProblem, x: ArrayLike, objective: str = "mass", tol_active: float = 1e-6) -> dict[str, Any]:
    """Check the KKT conditions at a candidate optimum.

    Parameters
    ----------
    pr : SizeProblem
        Problem with its constraint definitions.
    x : array_like
        Candidate design [m²].
    objective : {"mass", "volume", "compliance"}
        Objective.
    tol_active : float
        Constraints with ``g > −tol_active`` and variables within ``tol_active`` (relative) of a
        bound are treated as active.

    Returns
    -------
    dict
        ``residual``: ``‖∇L‖/‖∇f‖`` with multipliers ``μ ≥ 0`` from non-negative least squares (NNLS);
        ``mu_min``: smallest multiplier from unconstrained least squares (must be ≥ 0 for KKT);
        ``complementarity``: ``max |μ_j g_j|`` divided by ``‖∇f‖``;
        ``active``: names of the active constraints and bounds (``"x<i> lower"``/``"x<i> upper"``);
        ``factors``: ``{name: μ}`` (NNLS multipliers).

    Notes
    -----
    On the active set: ``∇f + Σ μ_j ∇g_j − Σ μ_lower e_i + Σ μ_upper e_i = 0``.
    """
    x = pr._x(x)
    _, df = pr.objective(x, objective, derivative=True)  # type: ignore[misc]
    g, J = pr.constraints(x, derivative=True)
    names = list(pr.constraint_names)
    active = np.where(g > -tol_active)[0]
    columns, name = [], []
    for i in active:
        columns.append(J[i])
        name.append(names[i])
    for i in range(pr.n):
        e = np.zeros(pr.n)
        if x[i] <= pr.lower[i] * (1 + tol_active):
            e[i] = -1.0
            columns.append(e)
            name.append(f"x{i + 1} lower")
        elif np.isfinite(pr.upper[i]) and x[i] >= pr.upper[i] * (1 - tol_active):
            e[i] = 1.0
            columns.append(e)
            name.append(f"x{i + 1} upper")
    scale = float(np.linalg.norm(df))
    if not columns:
        return {"residual": scale / scale, "mu_min": 0.0, "complementarity": 0.0, "active": [], "factors": {}}
    Am = np.array(columns).T
    mu, _ = nnls(Am, -df)
    residual = np.linalg.norm(df + Am @ mu) / scale
    mu_ls = np.linalg.lstsq(Am, -df, rcond=None)[0]
    mu_full = np.zeros(g.size)
    mu_full[active] = mu[:active.size]
    complementarity = float(np.max(np.abs(mu_full * g))) if g.size else 0.0
    return {"residual": float(residual), "mu_min": float(mu_ls.min()),
            "complementarity": complementarity / max(scale, 1e-300),
            "active": name, "factors": dict(zip(name, mu, strict=True))}


# ---------------------------------------------------------------- benchmark problems
# Literature optima (original units). Keys: objective/weight, design x/A, other published values, source.
LITERATURE: dict[str, dict[str, Any]] = {
    "three_bar": {
        "objective": 263.89584337, "x": (0.78867531, 0.40824778),
        "source": "Stripinis & Paulavičius, DIRECTGO (arXiv:2107.02205) App. B.2: f* = 263.89584337, "
                  "x* = (0.78867531, 0.40824778), g1 active; problem definition citing Ray & Saini 2001",
    },
    "ten_bar_1": {
        "weight": 5060.85,
        "A": (30.5218, 0.1000, 23.1999, 15.2229, 0.1000, 0.5514, 7.4572, 21.0364, 21.5284, 0.1000),
        "other": {"Li et al.": 5060.92, "Farshi & Ziazi": 5061.4},
        "source": "arXiv:1306.1454 (H-SAGA, 10-bar case 1) Table 1, Sedaghati 2005 column",
    },
    "ten_bar_2": {
        "weight": 4676.92,
        "A": (23.53, 0.100, 25.29, 14.37, 0.100, 1.970, 12.39, 12.83, 20.33, 0.100),
        "other": {"Schmit & Miura": 4676.96, "John et al.": 4676.93},
        "source": "arXiv:1306.1454 Table 2 (10-bar case 2: P1 = 150, P2 = 50 kip), Rizzi 1976 column",
    },
    "twenty_five_bar": {
        "weight": 545.16,
        "A": (0.0100, 1.9870, 2.9935, 0.0100, 0.0100, 0.6840, 1.6769, 2.6621),
        "other": {"Schmit & Farshi": 545.22, "Schmit & Miura": 545.17},
        "source": "arXiv:1306.1454 Table 10 (25-bar space truss), Lamberti 2008 column",
    },
}


@cite("schmit_1960", "ray_saini_2001", "stripinis_paulavicius_2021",
      note="classical three-bar truss; optimum from DIRECTGO App. B.2")
def three_bar_truss(P: float = 2.0, sigma: float = 2.0, l: float = 100.0, E: float = 1.0) -> SizeProblem:
    """Classical three-bar truss (Nowacki/Schmit), volume minimization.

    Parameters
    ----------
    P : float
        Load magnitude [kN], applied at 45° as ``(P/√2, −P/√2)``.
    sigma : float
        Allowable stress (tension and compression) [kN/cm²].
    l : float
        Support spacing and height [cm].
    E : float
        Young's modulus (does not affect the stresses of this problem).

    Returns
    -------
    SizeProblem
        ``A1 = A3 = x1``, ``A2 = x2``, ``0.001 ≤ x ≤ 1``, two load cases (the second is the mirror
        image, which justifies the symmetric linking ``A1 = A3``), stress limit ``sigma``. The volume
        objective ``100·(2√2 x1 + x2)`` is ``pr.objective(x, "volume")`` for ``l = 100``.

    Notes
    -----
    Supports at ``(−l, 0)``, ``(0, 0)``, ``(l, 0)``, loaded node at ``(0, −l)``. The closed-form
    constraints g1, g2, g3 coincide exactly with the FE stresses (derivation in the tests).
    Units are consistent (kN, cm).
    """
    m = Model([[-l, 0.0], [0.0, 0.0], [l, 0.0], [0.0, -l]], 2)
    for i in range(3):
        m.add(Bar(i, 3, E, 1.0))
        m.fix(i, [0, 1])
    c = P / math.sqrt(2)
    F1 = load_vector(m, [(3, 0, c), (3, 1, -c)])
    F2 = load_vector(m, [(3, 0, -c), (3, 1, -c)])
    m.F[:] = F1                                     # first load case for Model.static()
    pr = SizeProblem(m, groups=[[0, 2], [1]], lower=1e-3, upper=1.0, load_cases=[F1, F2])
    pr.stress_limit(sigma)
    return pr


@cite("schmit_farshi_1974", "arxiv_1306_1454", "sedaghati_2005", "rizzi_1976", "schmit_miura_1976",
      note="geometry: arXiv:1306.1454 Fig. 1; optima: Tables 1-2 (Sedaghati 2005 and Rizzi 1976 columns)")
def ten_bar_truss(case: int = 1) -> SizeProblem:
    """Ten-bar planar truss (Schmit & Farshi 1974 version), weight minimization.

    Parameters
    ----------
    case : {1, 2}
        Load case 1: ``P1 = 100, P2 = 0`` kip; case 2: ``P1 = 150, P2 = 50`` kip.

    Returns
    -------
    SizeProblem
        One variable per bar, ``A ≥ 0.1 in²``, ``|σ| ≤ 25 ksi``, ``|u| ≤ 2 in`` at the four free
        nodes. Units: kip, in, ksi; ``E = 10⁴ ksi``, ``ρ = 0.1 lb/in³`` → weight in lb.

    Raises
    ------
    ValueError
        If ``case`` is not 1 or 2.

    Notes
    -----
    ``P1`` acts downward at nodes 2 and 4, ``P2`` upward at nodes 1 and 3 (1-based).
    """
    if case not in (1, 2):
        raise ValueError("case must be 1 or 2")
    X = [[720, 360], [720, 0], [360, 360], [360, 0], [0, 360], [0, 0]]
    joint = [(5, 3), (3, 1), (6, 4), (4, 2), (3, 4), (1, 2), (5, 4), (6, 3), (3, 2), (4, 1)]
    m = Model(X, 2)
    for i, j in joint:
        m.add(Bar(i - 1, j - 1, 1e4, 1.0, rho=0.1))
    m.fix(4, [0, 1])
    m.fix(5, [0, 1])
    P1, P2 = (100.0, 0.0) if case == 1 else (150.0, 50.0)
    F = load_vector(m, [(1, 1, -P1), (3, 1, -P1), (0, 1, P2), (2, 1, P2)])
    m.F[:] = F
    pr = SizeProblem(m, lower=0.1, load_cases=[F])
    pr.stress_limit(25.0)
    pr.displacement_limit([(d, y) for d in range(4) for y in (0, 1)], 2.0)
    return pr


# 25-bar connectivity (1-based node pairs) and the eight linking groups (0-based element indices).
TWENTY_FIVE_JOINT = [(1, 2), (1, 4), (2, 3), (1, 5), (2, 6), (2, 4), (2, 5), (1, 3), (1, 6), (3, 6),
                     (4, 5), (3, 4), (5, 6), (3, 10), (6, 7), (4, 9), (5, 8), (4, 7), (3, 8), (5, 10),
                     (6, 9), (6, 10), (3, 7), (4, 8), (5, 9)]
TWENTY_FIVE_GROUPS = [[0], [1, 2, 3, 4], [5, 6, 7, 8], [9, 10], [11, 12], [13, 14, 15, 16], [17, 18, 19, 20],
                      [21, 22, 23, 24]]


@cite("schmit_farshi_1974", "arxiv_1306_1454", "lamberti_2008",
      note="loads and group compression limits: arXiv:1306.1454 Tables 8-9; node coordinates: Memphis "
           "CIVL 7117 homework 5b, Table 1; connectivity not given as text in these sources")
def twenty_five_bar_truss() -> SizeProblem:
    """Twenty-five-bar space truss tower, weight minimization with eight linking groups.

    Returns
    -------
    SizeProblem
        Two load cases, tension limit 40 ksi, group-wise compression limits, ``|u| ≤ 0.35 in`` at
        the six free nodes, ``A ≥ 0.01 in²``. Units: kip, in, ksi; ``ρ = 0.1 lb/in³``;
        ``E = 10⁴ ksi``.

    Notes
    -----
    The connectivity table is not given as text in the sources; it was taken from the figure and
    common usage and is verified numerically by the weight of the literature areas.
    """
    X = [[-37.5, 0, 200], [37.5, 0, 200], [-37.5, 37.5, 100], [37.5, 37.5, 100], [37.5, -37.5, 100],
         [-37.5, -37.5, 100], [-100, 100, 0], [100, 100, 0], [100, -100, 0], [-100, -100, 0]]
    m = Model(X, 3)
    for i, j in TWENTY_FIVE_JOINT:
        m.add(Bar(i - 1, j - 1, 1e4, 1.0, 0.1, 3))      # rho = 0.1, 3-D (positional: FEM keyword in flux)
    for d in range(6, 10):
        m.fix(d, [0, 1, 2])
    F1 = load_vector(m, [(0, 0, 1.0), (0, 1, 10.0), (0, 2, -5.0), (1, 1, 10.0), (1, 2, -5.0),
                         (2, 0, 0.5), (5, 0, 0.5)])
    F2 = load_vector(m, [(0, 1, 20.0), (0, 2, -5.0), (1, 1, -20.0), (1, 2, -5.0)])
    pr = SizeProblem(m, groups=TWENTY_FIVE_GROUPS, lower=0.01, load_cases=[F1, F2])
    compression_g = [35.092, 11.590, 17.305, 35.092, 35.092, 6.759, 6.959, 11.082]
    pr.stress_limit(40.0, compression=np.array(compression_g)[pr.group_no])
    pr.displacement_limit([(d, y) for d in range(6) for y in (0, 1, 2)], 0.35)
    return pr
