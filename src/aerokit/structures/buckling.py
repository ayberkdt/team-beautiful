"""Buckling: columns (Euler, Johnson, secant, tangent modulus), plates (compression / shear / bending
coefficients, interaction, plasticity reduction), crippling, thin cylinders (SP-8007) and
lateral-torsional buckling.

Sources (pages read when the code was written):

- Gerard & Becker 1957, NACA TN 3781: Table 2 (η), Table 5 (interaction), Table 7 (long-plate k),
  Eqs. (18)-(20), (25), Fig. 2(b).
- Gerard 1957, NACA TN 3784: Eqs. (67), (69)-(72), (75) (crippling), β values on pp. 38-42.
- NASA SP-8007 (1968 rev.): Eqs. (4)-(6), (9), (10), (16), (19)-(21), (25)-(28), (30), (31).

The plate coefficients k(a/b) are the EXACT solution for a Lévy-type plate whose loaded edges are simply
supported (Timoshenko & Gere method; the characteristic determinant is solved numerically).

All functions use SI units (Pa, m, N) unless stated otherwise; buckling coefficients are dimensionless.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import brentq

from aerokit.references import cite
from aerokit.structures.beam import sp8007_reduction

# --- column end conditions: effective-length factor K (Le = K·L) -------------------------------
END_CONDITION_K = {
    "pinned-pinned": 1.0,
    "fixed-fixed": 0.5,
    "fixed-pinned": 0.6992,     # π/4.4934; 4.4934 is the first root of tan x = x
    "fixed-free": 2.0,
}


@cite("timoshenko_gere_1961", note="Euler column")
def euler_stress(E: float, slenderness: float) -> float:
    """Euler buckling stress ``σ_E = π² E / (Le/ρ)²``.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    slenderness : float
        Effective slenderness ratio ``Le/ρ`` [-].

    Returns
    -------
    float
        Critical stress [Pa].

    Raises
    ------
    ValueError
        If ``slenderness ≤ 0``.
    """
    if slenderness <= 0:
        raise ValueError("slenderness must be positive")
    return math.pi ** 2 * E / slenderness ** 2


@cite("timoshenko_gere_1961", note="Euler column; fixed-pinned K from tan(kL) = kL")
def euler_critical(E: float, I: float, L: float, condition: str | float = "pinned-pinned") -> float:
    """Euler critical load ``P_cr = π² E I / (K L)²``.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    I : float
        Second moment of area [m⁴].
    L : float
        Column length [m].
    condition : str or float
        A key of :data:`END_CONDITION_K` (``"pinned-pinned"``, ``"fixed-fixed"``, ``"fixed-pinned"``,
        ``"fixed-free"``) or a numerical effective-length factor K.

    Returns
    -------
    float
        Critical load [N].

    Raises
    ------
    KeyError
        If ``condition`` is an unknown string.
    ValueError
        If E, I, L or K is not positive.

    Examples
    --------
    >>> round(euler_critical(1.0, 1.0, 1.0, "fixed-free") * 4, 6)
    9.869604
    """
    K = END_CONDITION_K[condition] if isinstance(condition, str) else float(condition)
    if E <= 0 or I <= 0 or L <= 0 or K <= 0:
        raise ValueError("E, I, L and K must be positive")
    return math.pi ** 2 * E * I / (K * L) ** 2


@cite("bruhn_1973", note="Johnson-Euler column curve")
def johnson_transition_slenderness(sigma_c: float, E: float) -> float:
    """Slenderness at which the Johnson parabola is tangent to the Euler curve, ``(Le/ρ)_t = π √(2E/σ_c)``.

    Parameters
    ----------
    sigma_c : float
        Short-column strength [Pa].
    E : float
        Young's modulus [Pa].

    Returns
    -------
    float
        Transition slenderness ratio [-].
    """
    return math.pi * math.sqrt(2 * E / sigma_c)


@cite("bruhn_1973", note="Johnson-Euler column curve")
def johnson_stress(sigma_c: float, E: float, slenderness: float) -> float:
    """Johnson parabola ``σ = σ_c − σ_c²/(4π²E) · (Le/ρ)²``; Euler beyond the transition.

    Parameters
    ----------
    sigma_c : float
        Short-column strength [Pa] (compressive yield σ_cy or crippling stress σ_cc).
    E : float
        Young's modulus [Pa].
    slenderness : float
        Effective slenderness ``Le/ρ`` [-].

    Returns
    -------
    float
        Critical column stress [Pa].

    Raises
    ------
    ValueError
        If ``sigma_c`` or ``E`` is not positive, or ``slenderness < 0``.
    """
    if sigma_c <= 0 or E <= 0 or slenderness < 0:
        raise ValueError("σ_c and E must be positive and slenderness ≥ 0")
    if slenderness >= johnson_transition_slenderness(sigma_c, E):
        return euler_stress(E, slenderness)
    return sigma_c - sigma_c ** 2 / (4 * math.pi ** 2 * E) * slenderness ** 2


@cite("timoshenko_gere_1961", note="eccentrically loaded column (secant formula)")
def secant_max_stress(P: float, A: float, E: float, rho: float, e: float, c: float, Le: float) -> float:
    """Maximum stress in an eccentrically loaded column (secant formula).

    Parameters
    ----------
    P : float
        Axial compressive load [N].
    A : float
        Cross-section area [m²].
    E : float
        Young's modulus [Pa].
    rho : float
        Radius of gyration [m].
    e : float
        Load eccentricity [m].
    c : float
        Distance to the extreme compressive fibre [m].
    Le : float
        Effective length [m].

    Returns
    -------
    float
        Maximum compressive stress [Pa]; ``math.inf`` at or beyond the Euler load.

    Notes
    -----
    ``σ_max = (P/A) · [1 + (e c/ρ²) · sec((Le/2ρ) √(P/(E A)))]``.
    """
    arg = Le / (2 * rho) * math.sqrt(P / (E * A))
    if arg >= math.pi / 2:
        return math.inf
    return P / A * (1 + e * c / rho ** 2 / math.cos(arg))


@cite("timoshenko_gere_1961", note="eccentrically loaded column (secant formula)")
def secant_critical_load(sigma_yield: float, A: float, E: float, rho: float, e: float, c: float,
                         Le: float) -> float:
    """Axial load at which the secant-formula peak stress reaches yield (root with ``P < P_E``).

    Parameters
    ----------
    sigma_yield : float
        Yield stress [Pa].
    A, E, rho, e, c, Le : float
        As in :func:`secant_max_stress`.

    Returns
    -------
    float
        Load P [N] with ``σ_max(P) = σ_yield``, capped at ``min(P_E, σ_yield·A)``.

    Raises
    ------
    ValueError
        If any of ``sigma_yield, A, E, rho, Le`` is not positive or ``e < 0``.
    """
    if min(sigma_yield, A, E, rho, Le) <= 0 or e < 0:
        raise ValueError("invalid input")
    PE = math.pi ** 2 * E * A * rho ** 2 / Le ** 2
    upper = min(PE * (1 - 1e-15), sigma_yield * A)
    f = lambda P: secant_max_stress(P, A, E, rho, e, c, Le) - sigma_yield
    if f(upper) <= 0:
        return upper
    return brentq(f, 0.0, upper, xtol=1e-14 * upper, rtol=1e-14, maxiter=500)


# --- Ramberg-Osgood ----------------------------------------------------------------------------
@cite("ramberg_osgood_1943")
def ro_strain(sigma: float, E: float, F: float, n: float, offset: float = 0.002) -> float:
    """Ramberg-Osgood strain ``ε = σ/E + offset · (σ/F)^n`` (sign of σ preserved).

    Parameters
    ----------
    sigma : float
        Stress [Pa].
    E : float
        Young's modulus [Pa].
    F : float
        Offset yield stress, e.g. F_0.2 [Pa].
    n : float
        Ramberg-Osgood exponent [-].
    offset : float
        Plastic strain at ``σ = F`` [-].

    Returns
    -------
    float
        Total strain [-].
    """
    return sigma / E + offset * (abs(sigma) / F) ** n * math.copysign(1, sigma)


@cite("ramberg_osgood_1943")
def ro_tangent_modulus(sigma: float, E: float, F: float, n: float, offset: float = 0.002) -> float:
    """Ramberg-Osgood tangent modulus ``E_t = dσ/dε = 1 / (1/E + offset · n/F · (σ/F)^(n−1))``.

    Parameters
    ----------
    sigma, E, F, n, offset
        As in :func:`ro_strain`.

    Returns
    -------
    float
        Tangent modulus [Pa].
    """
    return 1 / (1 / E + offset * n / F * (abs(sigma) / F) ** (n - 1))


@cite("ramberg_osgood_1943")
def ro_secant_modulus(sigma: float, E: float, F: float, n: float, offset: float = 0.002) -> float:
    """Ramberg-Osgood secant modulus ``E_s = σ/ε`` (``E`` at σ = 0).

    Parameters
    ----------
    sigma, E, F, n, offset
        As in :func:`ro_strain`.

    Returns
    -------
    float
        Secant modulus [Pa].
    """
    return 1 / (1 / E + offset / abs(sigma) * (abs(sigma) / F) ** n) if sigma else E


@cite("ramberg_osgood_1943", note="secant yield stresses σ0.7, σ0.85")
def ro_n_secant(sigma_07: float, sigma_085: float) -> float:
    """Ramberg-Osgood exponent from the secant yield stresses, ``n = 1 + ln(17/7) / ln(σ0.7/σ0.85)``.

    Parameters
    ----------
    sigma_07, sigma_085 : float
        Stresses at which the secant modulus equals 0.7E and 0.85E [Pa].

    Returns
    -------
    float
        Exponent n [-].

    Raises
    ------
    ValueError
        Unless ``sigma_07 > sigma_085 > 0``.

    Notes
    -----
    Follows from the RO equation itself: ``E/E_s − 1 = 3/7`` at σ0.7 and ``3/17`` at σ0.85
    (Ramberg & Osgood 1943 definition).
    """
    if not sigma_07 > sigma_085 > 0:
        raise ValueError("σ0.7 > σ0.85 > 0 is required")
    return 1 + math.log(17 / 7) / math.log(sigma_07 / sigma_085)


@cite("timoshenko_gere_1961", note="inelastic buckling, tangent-modulus (Engesser) theory")
def tangent_modulus_column(E: float, F: float, n: float, slenderness: float, offset: float = 0.002) -> float:
    """Tangent-modulus (Engesser) column stress ``σ = π² E_t(σ) / (Le/ρ)²`` for a Ramberg-Osgood material.

    Parameters
    ----------
    E, F, n, offset
        Ramberg-Osgood parameters, see :func:`ro_strain`.
    slenderness : float
        Effective slenderness ``Le/ρ`` [-].

    Returns
    -------
    float
        Critical column stress [Pa] (never above the Euler stress).
    """
    sE = euler_stress(E, slenderness)
    f = lambda s: s - math.pi ** 2 * ro_tangent_modulus(s, E, F, n, offset) / slenderness ** 2
    return brentq(f, 1e-12 * sE, sE, xtol=1e-12 * sE, maxiter=500)


# ---------------------------------------------------------------------------
# Plate buckling
# ---------------------------------------------------------------------------
@cite("gerard_becker_1957", note="NACA TN 3781")
def plate_critical_stress(k: float, E: float, nu: float, t: float, b: float) -> float:
    """Plate critical stress ``σ_cr = k π² E / (12(1 − ν²)) · (t/b)²``.

    Parameters
    ----------
    k : float
        Compression, shear or bending buckling coefficient [-].
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    t : float
        Thickness [m].
    b : float
        Reference (loaded or short) edge width [m].

    Returns
    -------
    float
        Critical stress [Pa].
    """
    return k * math.pi ** 2 * E / (12 * (1 - nu ** 2)) * (t / b) ** 2


def _edge_rows(kind: str, d: list[NDArray[np.float64]], alpha: float, nu: float) -> list[NDArray[np.float64]]:
    """Boundary-condition rows of edge ``kind``; ``d[r]`` holds the r-th derivatives of the basis functions."""
    if kind == "SS":
        return [d[0], d[2]]
    if kind == "C":
        return [d[0], d[1]]
    if kind == "F":
        return [d[2] - nu * alpha ** 2 * d[0], d[3] - (2 - nu) * alpha ** 2 * d[1]]
    raise ValueError(f"edge type must be SS, C or F: {kind}")


def _plate_det(k: ArrayLike, alpha: float, edge1: str, edge2: str, nu: float) -> float | NDArray[np.float64]:
    """Characteristic determinant of a Lévy plate (b = 1, N/D = kπ²), columns scaled to stay positive.

    ``k`` may be a scalar or an array (vectorised scan). Basis: cosh(√μ y), sinh(√μ y)/√μ,
    cos(√λ y), sin(√λ y)/√λ (hyperbolic counterparts when λ < 0; 1, y when λ = 0).
    """
    k = np.atleast_1d(np.asarray(k, float))
    r = alpha * math.pi * np.sqrt(k)            # α·√(N/D)
    mu = alpha ** 2 + r                         # square of the hyperbolic root
    lam = r - alpha ** 2                        # square of the trigonometric root
    g = np.sqrt(mu)
    h = np.sqrt(np.abs(lam))
    hs = np.where(h > 0, h, 1.0)

    def basis(y: float) -> list[NDArray[np.float64]]:
        C = np.cosh(g * y)
        S = np.sinh(g * y) / g
        c = np.where(lam > 0, np.cos(h * y), np.cosh(h * y))
        s = np.where(lam > 0, np.sin(h * y), np.sinh(h * y)) / hs
        s = np.where(h > 0, s, y)
        # d[r] -> (N, 4): r-th derivative, columns [C, S, c, s]
        return [np.stack([C, S, c, s], -1),
                np.stack([mu * S, C, -lam * s, c], -1),
                np.stack([mu * C, mu * S, -lam * c, -lam * s], -1),
                np.stack([mu * mu * S, mu * C, lam * lam * s, -lam * c], -1)]

    rows: list[NDArray[np.float64]] = []
    for y, kind in ((0.0, edge1), (1.0, edge2)):
        rows.extend(_edge_rows(kind, basis(y), alpha, nu))
    M = np.stack(rows, axis=1)                  # (N, 4, 4)
    eh = np.exp(-np.where(lam < 0, h, 0.0))
    scale = np.stack([np.exp(-g), np.exp(-g), eh, eh], -1)[:, None, :]
    d = np.linalg.det(M * scale)
    return d if d.size > 1 else float(d[0])


def _first_root(alpha: float, k1: str, k2: str, nu: float, k_upper: float = 400.0) -> float:
    """Smallest k in (1e-3, k_upper) at which the Lévy determinant changes sign (``inf`` if none)."""
    ks = np.geomspace(1e-3, k_upper, 1200)
    v = np.asarray(_plate_det(ks, alpha, k1, k2, nu))
    sign_change = np.nonzero(np.sign(v[:-1]) * np.sign(v[1:]) <= 0)[0]
    if len(sign_change) == 0:
        return math.inf
    i = sign_change[0]
    f = lambda kk: _plate_det(kk, alpha, k1, k2, nu)
    if v[i] == 0:
        return float(ks[i])
    return brentq(f, ks[i], ks[i + 1], xtol=1e-13, rtol=1e-12)


@cite("timoshenko_gere_1961", note="Lévy-type exact solution, loaded edges simply supported")
@cite("gerard_becker_1957", note="TN 3781 Table 7 and Fig. 2(b) used as benchmarks")
def plate_compression_k(a_b: float, edge: str = "SS-SS", nu: float = 0.3, m_max: int | None = None) -> float:
    """Uniaxial-compression buckling coefficient k (``σ_cr = k π² E/(12(1 − ν²)) (t/b)²``).

    Parameters
    ----------
    a_b : float
        Plate length in the load direction divided by the loaded-edge width b [-].
    edge : str
        Unloaded edges as ``"<y=0>-<y=b>"`` with each of ``SS`` (simply supported), ``C`` (clamped) or
        ``F`` (free), e.g. ``"SS-SS"``, ``"C-C"``, ``"SS-C"``, ``"SS-F"``, ``"C-F"``. The loaded edges
        (x = 0, a) are always simply supported.
    nu : float
        Poisson's ratio [-] (matters only for free edges).
    m_max : int, optional
        Highest number of longitudinal half-waves tried (default ``int(2 a/b) + 3``).

    Returns
    -------
    float
        Minimum of k over the half-wave number m (exact Lévy solution) [-].

    Raises
    ------
    ValueError
        If ``a_b ≤ 0``, an edge type is unknown, or both unloaded edges are free.
    """
    if a_b <= 0:
        raise ValueError("a/b must be positive")
    k1, k2 = edge.upper().split("-")
    if "F" in (k1, k2) and k1 == k2:
        raise ValueError("a plate with both unloaded edges free (a column) is not supported")
    m_max = m_max or int(2 * a_b) + 3
    k_min = math.inf
    for m in range(1, m_max + 1):
        k_min = min(k_min, _first_root(m * math.pi / a_b, k1, k2, nu))
    return k_min


@cite("gerard_becker_1957", note="TN 3781 Eq. (20)")
def plate_compression_k_ss_closed(a_b: float) -> float:
    """Closed form for a plate simply supported on four edges, ``k = min_m (m b/a + a/(m b))²``.

    Parameters
    ----------
    a_b : float
        Aspect ratio a/b [-].

    Returns
    -------
    float
        Buckling coefficient k [-].

    Raises
    ------
    ValueError
        If ``a_b ≤ 0``.

    Examples
    --------
    >>> plate_compression_k_ss_closed(3.0)
    4.0
    """
    if a_b <= 0:
        raise ValueError("a/b must be positive")
    m0 = max(1, int(a_b))
    return min((m * 1 / a_b + a_b / m) ** 2 for m in (m0, m0 + 1, max(1, m0 - 1)))


@cite("gerard_becker_1957", note="TN 3781 Eqs. (18) and (19)")
def flange_k_gerard(a_b: float, nu: float = 0.3, edge: str = "SS") -> float:
    """Approximate k of a long flange (one unloaded edge free), TN 3781 energy solutions.

    Parameters
    ----------
    a_b : float
        Half-wave length over flange width, λ/b (here λ = a, m = 1) [-].
    nu : float
        Poisson's ratio [-].
    edge : {"SS", "C"}
        Restraint of the supported unloaded edge: simply supported (Eq. 18) or clamped (Eq. 19).

    Returns
    -------
    float
        Buckling coefficient k [-]; slightly above the exact solution (energy method).

    Raises
    ------
    ValueError
        If ``edge`` is not ``"SS"`` or ``"C"``.

    Notes
    -----
    (18): ``k = (6/π²)[(1 − ν) + (πb/λ)²/6]``; (19): ``k = 0.83 − 0.93ν + 1.34(λ/πb)² + 0.10(πb/λ)²``.
    """
    if edge == "SS":
        return 6 / math.pi ** 2 * ((1 - nu) + (math.pi / a_b) ** 2 / 6)
    if edge == "C":
        return 0.83 - 0.93 * nu + 1.34 * (a_b / math.pi) ** 2 + 0.10 * (math.pi / a_b) ** 2
    raise ValueError("edge must be SS or C")


@cite("timoshenko_gere_1961", note="SS shear-buckling approximation")
@cite("gerard_becker_1957", note="TN 3781 Table 7, infinitely long plates")
def plate_shear_k(a_b: float, edge: str = "SS") -> float:
    """Shear buckling coefficient k_s referred to the short side b.

    Parameters
    ----------
    a_b : float
        Aspect ratio (either a/b or b/a; it is converted to the short side) [-].
    edge : {"SS", "C"}
        All edges simply supported or all clamped.

    Returns
    -------
    float
        k_s [-] for ``τ_cr = k_s π² E/(12(1 − ν²)) (t/b)²`` with b the short side.

    Raises
    ------
    ValueError
        If ``a_b ≤ 0`` or ``edge`` is unknown.

    Notes
    -----
    SS: ``k_s = 5.35 + 4(b/a)²`` (Timoshenko & Gere approximation; 5.35 for an infinite plate,
    TN 3781 Table 7). C: ``k_s = 8.98 + 5.6(b/a)²`` (common curve fit; only the infinite-plate value
    8.98 was checked against TN 3781 Table 7 -- the 5.6 coefficient was not read from a primary source).
    """
    if a_b <= 0:
        raise ValueError("a/b must be positive")
    r = min(a_b, 1 / a_b)                    # b/a ≤ 1
    if edge == "SS":
        return 5.35 + 4.0 * r ** 2
    if edge == "C":
        return 8.98 + 5.6 * r ** 2
    raise ValueError("edge must be SS or C")


# TN 3781 Table 7, infinitely long plates
PLATE_BENDING_K = {"SS": 23.9, "C": 41.8}


@cite("gerard_becker_1957", note="TN 3781 Table 7")
def plate_bending_k(edge: str = "SS") -> float:
    """In-plane bending buckling coefficient k_b of a long plate.

    Parameters
    ----------
    edge : {"SS", "C"}
        Edge restraint.

    Returns
    -------
    float
        k_b [-] (23.9 simply supported, 41.8 clamped).
    """
    return PLATE_BENDING_K[edge]


def interaction_load_factor(ratios: Sequence[float], exponents: Sequence[float]) -> float:
    """Load factor λ satisfying ``Σ (λ R_i)^e_i = 1`` (all loads grow proportionally); ``MS = λ − 1``.

    Parameters
    ----------
    ratios : sequence of float
        Stress ratios R_i = applied / allowable [-] (signs ignored).
    exponents : sequence of float
        Interaction exponents e_i [-], same length as ``ratios``.

    Returns
    -------
    float
        Load factor λ [-].

    Raises
    ------
    ValueError
        If the lengths differ or all ratios are zero.

    Examples
    --------
    >>> round(interaction_load_factor([0.5], [1.0]), 12)
    2.0
    """
    R = [abs(r) for r in ratios]
    if len(R) != len(exponents) or not any(R):
        raise ValueError("ratios and exponents must have the same length and at least one ratio must be non-zero")
    f = lambda lam: sum((lam * r) ** e for r, e in zip(R, exponents, strict=True)) - 1
    upper = 1.0
    while f(upper) < 0:
        upper *= 2
    return brentq(f, 0.0, upper, xtol=1e-14, rtol=1e-14)


@cite("gerard_becker_1957", note="TN 3781 Table 5")
def ms_compression_shear(Rc: float, Rs: float) -> float:
    """Margin for ``R_c + R_s² = 1`` (long plate, elastic): ``MS = 2/(R_c + √(R_c² + 4R_s²)) − 1``.

    Parameters
    ----------
    Rc, Rs : float
        Compression and shear stress ratios [-].

    Returns
    -------
    float
        Margin of safety [-].
    """
    return 2 / (Rc + math.sqrt(Rc ** 2 + 4 * Rs ** 2)) - 1


@cite("gerard_becker_1957", note="TN 3781 Table 5, Eq. (58)")
def ms_bending_shear(Rb: float, Rs: float) -> float:
    """Margin for ``R_b² + R_s² = 1``: ``MS = 1/√(R_b² + R_s²) − 1``.

    Parameters
    ----------
    Rb, Rs : float
        Bending and shear stress ratios [-].

    Returns
    -------
    float
        Margin of safety [-].
    """
    return 1 / math.hypot(Rb, Rs) - 1


@cite("gerard_becker_1957", note="TN 3781 Table 5")
def ms_biaxial(Rx: float, Ry: float) -> float:
    """Margin for ``R_x + R_y = 1`` (plates buckling in square waves under biaxial compression).

    Parameters
    ----------
    Rx, Ry : float
        Stress ratios in x and y [-].

    Returns
    -------
    float
        Margin of safety [-].
    """
    return 1 / (Rx + Ry) - 1


@cite("gerard_becker_1957", note="TN 3781 Table 5")
def ms_plastic_compression_shear(Rc: float, Rs: float) -> float:
    """Margin for ``R_c² + R_s² = 1`` (inelastic compression + shear).

    Parameters
    ----------
    Rc, Rs : float
        Compression and shear stress ratios [-].

    Returns
    -------
    float
        Margin of safety [-].
    """
    return 1 / math.hypot(Rc, Rs) - 1


# --- plasticity reduction factor η (TN 3781 Table 2) -------------------------------------------
_ETA: dict[str, Callable[[float], float]] = {
    "flange_ss": lambda r: 1.0,
    "flange_c": lambda r: 0.330 + 0.335 * math.sqrt(1 + 3 * r),
    "plate_ss": lambda r: 0.500 + 0.250 * math.sqrt(1 + 3 * r),
    "plate_c": lambda r: 0.352 + 0.324 * math.sqrt(1 + 3 * r),
    "short_column": lambda r: 0.250 * (1 + 3 * r),
    "square_column": lambda r: 0.114 + 0.886 * r,
    "long_column": lambda r: r,
    "shear": lambda r: 0.83 + 0.17 * r,
}


@cite("gerard_becker_1957", note="TN 3781 Table 2, Eq. (25)")
def plasticity_eta(case: str, Es: float, Et: float, E: float, nu_e: float = 0.3, nu_p: float = 0.5) -> float:
    """Plasticity reduction factor ``η = (Es/E) (1 − ν_e²)/(1 − ν²) · f(Et/Es)``.

    Parameters
    ----------
    case : str
        One of ``flange_ss``, ``flange_c``, ``plate_ss``, ``plate_c``, ``short_column``,
        ``square_column``, ``long_column``, ``shear``.
    Es, Et : float
        Secant and tangent moduli at the current stress [Pa].
    E : float
        Young's modulus [Pa].
    nu_e, nu_p : float
        Elastic and fully plastic Poisson's ratios [-].

    Returns
    -------
    float
        η [-] (1 in the elastic range).

    Raises
    ------
    ValueError
        If ``case`` is unknown.

    Notes
    -----
    The inelastic Poisson's ratio is ``ν = ν_p − (Es/E)(ν_p − ν_e)`` (Eq. 25).
    """
    if case not in _ETA:
        raise ValueError(f"case must be one of: {', '.join(_ETA)}")
    nu = nu_p - Es / E * (nu_p - nu_e)
    return Es / E * (1 - nu_e ** 2) / (1 - nu ** 2) * _ETA[case](Et / Es)


@cite("gerard_becker_1957", note="TN 3781 Table 2")
def plate_plastic_critical(sigma_e: float, E: float, F: float, n: float, case: str = "plate_ss",
                           nu_e: float = 0.3, offset: float = 0.002) -> float:
    """Inelastic plate buckling stress: solves ``σ = η(σ) · σ_e`` for a Ramberg-Osgood material.

    Parameters
    ----------
    sigma_e : float
        Elastic critical stress [Pa].
    E, F, n, offset
        Ramberg-Osgood parameters, see :func:`ro_strain`.
    case : str
        Plasticity-factor case, see :func:`plasticity_eta`.
    nu_e : float
        Elastic Poisson's ratio [-].

    Returns
    -------
    float
        Inelastic critical stress [Pa] (``≤ sigma_e``).
    """
    def f(s: float) -> float:
        Es, Et = ro_secant_modulus(s, E, F, n, offset), ro_tangent_modulus(s, E, F, n, offset)
        return s - plasticity_eta(case, Es, Et, E, nu_e) * sigma_e
    return brentq(f, 1e-9 * sigma_e, sigma_e, xtol=1e-12 * sigma_e, maxiter=500)


# ---------------------------------------------------------------------------
# Crippling, Gerard method -- NACA TN 3784
# ---------------------------------------------------------------------------
CRIPPLING_BETA = {
    "single_corner": 0.565,   # extruded angles, Eq. (67), p. 38 ("first approximation")
    "two_corner": 4.00,       # 2024-T3 equal-flange Z and channel sections, Eq. (72), p. 40
    "multi_corner": 1.30,     # multi-corner sections, Eq. (75), p. 42
}


@cite("gerard_1957", note="TN 3784 Eqs. (67), (72), (75); β on pp. 38-42")
def crippling_gerard(kind: str, sigma_cy: float, E: float, t: float, A: float, count: int = 1,
                     beta: float | None = None, eta: float = 1.0) -> float:
    """Gerard crippling stress σ_f of a thin-walled section.

    Parameters
    ----------
    kind : {"single_corner", "two_corner", "multi_corner"}
        Section family (see Notes).
    sigma_cy : float
        Compressive yield stress [Pa].
    E : float
        Young's modulus [Pa].
    t : float
        Wall thickness [m].
    A : float
        Cross-section area [m²].
    count : int
        Number of flanges (``single_corner``) or corners (``multi_corner``); unused for ``two_corner``.
    beta : float, optional
        Overrides the default coefficient in :data:`CRIPPLING_BETA`.
    eta : float
        Plasticity reduction applied to E [-].

    Returns
    -------
    float
        Crippling stress [Pa], capped at ``sigma_cy``.

    Raises
    ------
    KeyError
        If ``kind`` is unknown and ``beta`` is not given.
    ValueError
        If an input is not positive or ``kind`` is unknown.

    Notes
    -----
    - single_corner: ``σ_f/σ_cy = β_f [(f t²/A)(ηE/σ_cy)^½]^0.85`` (f: number of flanges), Eq. (67)
    - two_corner:    ``σ_f/σ_cy = β [(t²/A)(ηE/σ_cy)^⅓]^0.75``, Eq. (72)
    - multi_corner:  ``σ_f/σ_cy = β_c [(c t²/A)(ηE/σ_cy)^½]^0.85`` (c: number of corners), Eq. (75)

    The result is capped at σ_cy; the cut-offs of TN 3784 Fig. 16 are NOT applied (conservative
    simplification).
    """
    if min(sigma_cy, E, t, A) <= 0:
        raise ValueError("σ_cy, E, t and A must be positive")
    b = CRIPPLING_BETA[kind] if beta is None else beta
    if kind == "single_corner":
        ratio = b * ((count * t ** 2 / A) * (eta * E / sigma_cy) ** 0.5) ** 0.85
    elif kind == "two_corner":
        ratio = b * ((t ** 2 / A) * (eta * E / sigma_cy) ** (1 / 3)) ** 0.75
    elif kind == "multi_corner":
        ratio = b * ((count * t ** 2 / A) * (eta * E / sigma_cy) ** 0.5) ** 0.85
    else:
        raise ValueError("kind must be single_corner, two_corner or multi_corner")
    return min(ratio, 1.0) * sigma_cy


# ---------------------------------------------------------------------------
# Thin cylinders (NASA SP-8007, 1968)
# ---------------------------------------------------------------------------
@cite("nasa_sp8007", note="list of symbols")
def cylinder_Z(L: float, r: float, t: float, nu: float = 0.3) -> float:
    """Batdorf curvature parameter ``Z = L²/(r t) · √(1 − ν²)``.

    Parameters
    ----------
    L, r, t : float
        Length, radius and wall thickness [m].
    nu : float
        Poisson's ratio [-].

    Returns
    -------
    float
        Z [-].
    """
    return L ** 2 / (r * t) * math.sqrt(1 - nu ** 2)


@cite("nasa_sp8007", note="Eqs. (4)-(6)")
def cylinder_axial(E: float, nu: float, r: float, t: float, gamma: float | None = None) -> float:
    """Axial-compression buckling stress ``σ_cr = γ E/√(3(1 − ν²)) · (t/r)``.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    r, t : float
        Radius and wall thickness [m].
    gamma : float, optional
        Knock-down factor; default from Eqs. (5)-(6) via :func:`~aerokit.structures.beam.sp8007_reduction`.

    Returns
    -------
    float
        Critical stress [Pa].
    """
    g = sp8007_reduction(r, t, "axial") if gamma is None else gamma
    return g * E / math.sqrt(3 * (1 - nu ** 2)) * t / r


@cite("nasa_sp8007", note="Eqs. (4), (9)-(10)")
def cylinder_bending(E: float, nu: float, r: float, t: float, gamma: float | None = None) -> float:
    """Peak compressive fibre stress at buckling in bending: Eq. (4) with ``γ = 1 − 0.731(1 − e^−φ)``.

    Parameters
    ----------
    E, nu, r, t
        As in :func:`cylinder_axial`.
    gamma : float, optional
        Knock-down factor; default from Eqs. (9)-(10).

    Returns
    -------
    float
        Critical extreme-fibre stress [Pa].
    """
    g = sp8007_reduction(r, t, "bending") if gamma is None else gamma
    return g * E / math.sqrt(3 * (1 - nu ** 2)) * t / r


@cite("nasa_sp8007", note="Sec. 4.2.3, Eqs. (16), (19)-(21)")
def cylinder_external_pressure(E: float, nu: float, r: float, t: float, L: float, root_gamma: float = 0.75,
                               gamma_long: float = 0.90) -> float:
    """Critical lateral external pressure of a simply supported cylinder.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    r, t, L : float
        Radius, wall thickness and length [m].
    root_gamma : float
        √γ for moderate-length cylinders (Eq. 20) [-].
    gamma_long : float
        γ for long cylinders, oval mode (Eq. 21) [-].

    Returns
    -------
    float
        Critical pressure [Pa].

    Notes
    -----
    Moderate length: ``p = 0.855 E √γ / ((1 − ν²)^¾ (r/t)^(5/2) (L/r))`` (Eqs. 16, 20).
    Long (oval): ``p = γ E/(4(1 − ν²)) (t/r)³`` (Eqs. 19, 21). The larger of the two is returned because
    the long-cylinder branches in Fig. 4 rise ABOVE the main line. Eq. (17) gives 0.926 for ν = 0.3, whereas
    Eq. (16) gives 0.855/0.91^0.75 = 0.918 (a 0.9 % inconsistency in the source).
    """
    p16 = 0.855 * E * root_gamma / ((1 - nu ** 2) ** 0.75 * (r / t) ** 2.5 * (L / r))
    p19 = gamma_long * E / (4 * (1 - nu ** 2)) * (t / r) ** 3
    return max(p16, p19)


@cite("nasa_sp8007", note="Sec. 4.2.4, Eqs. (25)-(28)")
def cylinder_torsion(E: float, nu: float, r: float, t: float, L: float, gamma34: float = 0.67) -> float:
    """Torsional buckling shear stress of a simply supported cylinder.

    Parameters
    ----------
    E : float
        Young's modulus [Pa].
    nu : float
        Poisson's ratio [-].
    r, t, L : float
        Radius, wall thickness and length [m].
    gamma34 : float
        γ^¾ (Eq. 28) [-].

    Returns
    -------
    float
        Critical shear stress [Pa].

    Raises
    ------
    ValueError
        If γZ < 50 (the curved part of Fig. 5 is not implemented).

    Notes
    -----
    ``50 < γZ < 78(r/t)²(1 − ν²)``: ``k_xy = 0.85(γZ)^¾``, ``τ = k_xy π² D/(L² t)`` (Eq. 25; Eq. 26 for ν = 0.3).
    ``γZ > 78(r/t)²(1 − ν²)`` (two waves): ``τ = γE/(3√2 (1 − ν²)^¾) · (t/r)^(3/2)`` (Eq. 27b).
    """
    g = gamma34 ** (4 / 3)
    Z = cylinder_Z(L, r, t, nu)
    gZ = g * Z
    if gZ > 78 * (r / t) ** 2 * (1 - nu ** 2):
        return g * E / (3 * math.sqrt(2) * (1 - nu ** 2) ** 0.75) * (t / r) ** 1.5
    if gZ < 50:
        raise ValueError(f"γZ = {gZ:.1f} < 50: outside the straight-line part of SP-8007 (Fig. 5 curve needed)")
    D_t = E * t ** 2 / (12 * (1 - nu ** 2))        # D/t
    return 0.85 * gZ ** 0.75 * math.pi ** 2 * D_t / L ** 2


@cite("nasa_sp8007", note="Eq. (30)")
def ms_cylinder_compression_bending(Rc: float, Rb: float) -> float:
    """Margin for the cylinder interaction ``R_c + R_b = 1``.

    Parameters
    ----------
    Rc, Rb : float
        Axial-compression and bending stress ratios [-].

    Returns
    -------
    float
        Margin of safety [-].
    """
    return 1 / (Rc + Rb) - 1


@cite("nasa_sp8007", note="Eq. (31)")
def ms_cylinder_compression_pressure(Rc: float, Rp: float) -> float:
    """Margin for the cylinder interaction ``R_c + R_p = 1``.

    Parameters
    ----------
    Rc, Rp : float
        Axial-compression and external-pressure ratios [-].

    Returns
    -------
    float
        Margin of safety [-].
    """
    return 1 / (Rc + Rp) - 1


# ---------------------------------------------------------------------------
# Lateral-torsional buckling
# ---------------------------------------------------------------------------
@cite("timoshenko_gere_1961", note="lateral buckling of beams; classical solution, not re-read in this session")
@cite("vlasov_1961")
def lateral_torsional_moment(E: float, G: float, Iy: float, J: float, Cw: float, L: float) -> float:
    """Elastic lateral-torsional buckling moment of a doubly symmetric beam under uniform moment.

    Parameters
    ----------
    E, G : float
        Young's and shear moduli [Pa].
    Iy : float
        Minor-axis second moment of area [m⁴].
    J : float
        St Venant torsion constant [m⁴].
    Cw : float
        Warping constant [m⁶].
    L : float
        Unbraced length [m].

    Returns
    -------
    float
        Critical moment [N·m].

    Raises
    ------
    ValueError
        If E, G, Iy, J or L is not positive or ``Cw < 0``.

    Notes
    -----
    Ends restrained against lateral displacement and twist, free to warp:
    ``M_cr = (π/L) √(E Iy G J (1 + π² E Cw/(G J L²)))``.
    """
    if min(E, G, Iy, J, L) <= 0 or Cw < 0:
        raise ValueError("invalid input")
    return math.pi / L * math.sqrt(E * Iy * G * J * (1 + math.pi ** 2 * E * Cw / (G * J * L ** 2)))
