"""Linear elastic fracture mechanics: stress-intensity factor K = Y σ √(πa), finite-width corrections,
critical crack length / residual strength, Irwin plastic zone, crack-growth rates (Paris, Walker,
Forman) and the life integral.

Sources and verification status:

- Single-edge crack (SENT), Gross, Srawley & Brown, NASA TN D-2395 (1964):
  F = 1.122 − 0.231α + 10.550α² − 21.710α³ + 30.382α⁴, α = a/W ≤ 0.6, 0.5 % accuracy;
  Tada, Paris & Irwin (2000): F = √(2W/(πa)·tan(πa/2W))·[0.752 + 2.02α + 0.37(1 − sin(πa/2W))³]
  / cos(πa/2W), 0.5 % for any α -- both read from Aranda, García, Reinoso, Mantič & Paggi,
  arXiv:2009.06588, App. A.1 (Eqs. A.2, A.4).
- Centre crack, finite width: Feddersen (1966) secant correction √sec(πa/W) (a half length, W full width);
  Tada (1 − 0.025α² + 0.06α⁴)√sec(πα/2), α = 2a/W; Brown (1966) polynomial fit to Isida's solution
  K = σ√a[1.77 + 0.227α − 0.510α² + 2.7α³]. These three were NOT read from a primary source in this session
  (general knowledge); the tests check the W → ∞ limit and their mutual consistency.
- Crack at the edge of a hole (Bowie): NOT IMPLEMENTED, since no values could be read from a source.
- Irwin plastic zone: r_y = (1/2π)(K/σy)² (plane stress), (1/6π)(K/σy)² (plane strain);
  Dowling, Mechanical Behavior of Materials, Sec. 8.7 -- not read in this session (general knowledge).
- Paris & Erdogan, J. Basic Eng. 85 (1963): da/dN = C ΔK^m. Walker (1970): ΔK̄ = ΔK/(1−R)^(1−γ).
  Forman, Kearney & Engle, J. Basic Eng. 89 (1967): da/dN = C ΔK^m / [(1 − R)Kc − ΔK].

SI units: σ [Pa], a [m], K [Pa√m]. The Paris constant C must be consistent with the unit of K
(e.g. with C in m/cycle/(MPa√m)^m pass ΔK in MPa√m; the functions themselves are unit-agnostic).
"""
from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import integrate, optimize

from aerokit.references import cite

GeometryFactor = float | Callable[[float], float]


def _check_a(a: float) -> None:
    """Raise ``ValueError`` unless the crack length is positive."""
    if not (a > 0):
        raise ValueError("crack length a must be positive")


# ======================= K and geometry factors =======================
@cite("tada_paris_irwin_2000")
def sif(sigma: float, a: float, Y: float = 1.0) -> float:
    """Mode-I stress-intensity factor ``K = Y σ √(πa)``.

    Parameters
    ----------
    sigma : float
        Remote stress [Pa].
    a : float
        Crack length (half length for a centre crack) [m].
    Y : float
        Geometry factor [-].

    Returns
    -------
    float
        K [Pa√m].

    Raises
    ------
    ValueError
        If ``a ≤ 0``.
    """
    _check_a(a)
    return Y * sigma * math.sqrt(math.pi * a)


@cite("feddersen_1966")
def Y_center_secant(a: float, W: float) -> float:
    """Centre crack of length 2a in a plate of width W: ``Y = √sec(πa/W)`` (Feddersen).

    Parameters
    ----------
    a : float
        Half crack length [m].
    W : float
        Plate width [m]; ``2a < W``.

    Returns
    -------
    float
        Y [-].

    Raises
    ------
    ValueError
        If ``a ≤ 0`` or ``2a ≥ W``.
    """
    _check_a(a)
    if not (2 * a < W):
        raise ValueError("2a < W is required")
    return math.sqrt(1 / math.cos(math.pi * a / W))


@cite("tada_paris_irwin_2000", note="not read from the source in this session")
def Y_center_tada(a: float, W: float) -> float:
    """Tada centre-crack factor ``Y = (1 − 0.025α² + 0.06α⁴)√sec(πα/2)``, ``α = 2a/W``.

    Parameters
    ----------
    a : float
        Half crack length [m].
    W : float
        Plate width [m].

    Returns
    -------
    float
        Y [-].

    Raises
    ------
    ValueError
        If ``a ≤ 0`` or ``2a ≥ W``.
    """
    _check_a(a)
    alpha = 2 * a / W
    if not (alpha < 1):
        raise ValueError("2a < W is required")
    return (1 - 0.025 * alpha ** 2 + 0.06 * alpha ** 4) * math.sqrt(1 / math.cos(math.pi * alpha / 2))


@cite("brown_srawley_1966", note="polynomial fit to Isida's solution; not read from the source in this session")
def Y_center_isida(a: float, W: float) -> float:
    """Brown's polynomial fit to Isida's centre-crack solution, ``Y = [1.77 + 0.227α − 0.510α² + 2.7α³]/√π``.

    Parameters
    ----------
    a : float
        Half crack length [m].
    W : float
        Plate width [m]; ``α = 2a/W ≤ 0.9``.

    Returns
    -------
    float
        Y [-].

    Raises
    ------
    ValueError
        If ``a ≤ 0`` or ``2a/W > 0.9``.
    """
    _check_a(a)
    alpha = 2 * a / W
    if not (alpha <= 0.9):
        raise ValueError("2a/W ≤ 0.9 is required")
    return (1.77 + 0.227 * alpha - 0.510 * alpha ** 2 + 2.7 * alpha ** 3) / math.sqrt(math.pi)


@cite("gross_srawley_1964", note="as given by Aranda et al., arXiv:2009.06588, Eq. A.2")
def Y_edge_gross(a: float, W: float) -> float:
    """Single-edge crack in tension, Gross-Srawley-Brown polynomial (a/W ≤ 0.6).

    Parameters
    ----------
    a : float
        Crack length [m].
    W : float
        Plate width [m].

    Returns
    -------
    float
        Y [-].

    Raises
    ------
    ValueError
        If ``a ≤ 0`` or ``a/W > 0.6``.

    Notes
    -----
    ``Y = 1.122 − 0.231α + 10.550α² − 21.710α³ + 30.382α⁴``, ``α = a/W``.
    """
    _check_a(a)
    alpha = a / W
    if not (alpha <= 0.6):
        raise ValueError("the polynomial is valid for a/W ≤ 0.6")
    return 1.122 - 0.231 * alpha + 10.550 * alpha ** 2 - 21.710 * alpha ** 3 + 30.382 * alpha ** 4


@cite("tada_paris_irwin_2000", note="as given by Aranda et al., arXiv:2009.06588, Eq. A.4")
def Y_edge_tada(a: float, W: float) -> float:
    """Single-edge crack in tension, Tada-Paris-Irwin (0.5 % for any a/W < 1).

    Parameters
    ----------
    a : float
        Crack length [m].
    W : float
        Plate width [m].

    Returns
    -------
    float
        Y [-].

    Raises
    ------
    ValueError
        If ``a ≤ 0`` or ``a ≥ W``.

    Notes
    -----
    ``Y = √(tan t / t) · [0.752 + 2.02α + 0.37(1 − sin t)³] / cos t``, ``t = πa/(2W)``.
    """
    _check_a(a)
    alpha = a / W
    if not (alpha < 1):
        raise ValueError("a < W is required")
    t = math.pi * a / (2 * W)
    return (math.sqrt(math.tan(t) / t) * (0.752 + 2.02 * alpha + 0.37 * (1 - math.sin(t)) ** 3)
            / math.cos(t))


# ======================= critical crack and residual strength =======================
def residual_strength(K_c: float, a: float, Y: GeometryFactor = 1.0) -> float:
    """Fracture stress at crack length a, ``σc = Kc/(Y √(πa))``.

    Parameters
    ----------
    K_c : float
        Fracture toughness [Pa√m].
    a : float
        Crack length [m].
    Y : float or callable
        Geometry factor, constant or ``Y(a)``.

    Returns
    -------
    float
        Residual strength [Pa].

    Raises
    ------
    ValueError
        If ``a ≤ 0``.
    """
    _check_a(a)
    y = Y(a) if callable(Y) else Y
    return K_c / (y * math.sqrt(math.pi * a))


def critical_crack(K_c: float, sigma: float, Y: GeometryFactor = 1.0, a_max: float | None = None) -> float:
    """Critical crack length at which ``K(a) = Kc``.

    Parameters
    ----------
    K_c : float
        Fracture toughness [Pa√m].
    sigma : float
        Remote stress [Pa].
    Y : float or callable
        Geometry factor; constant gives the closed form ``a_c = (1/π)(Kc/(Yσ))²``, a callable ``Y(a)``
        is solved numerically up to ``a_max``.
    a_max : float, optional
        Validity limit of ``Y(a)`` [m]; required when Y is callable.

    Returns
    -------
    float
        Critical crack length [m].

    Raises
    ------
    ValueError
        If Kc or σ is not positive, ``a_max`` is missing for a callable Y, or no root exists in
        ``(0, a_max]``.
    """
    if not (K_c > 0 and sigma > 0):
        raise ValueError("Kc and σ must be positive")
    if not callable(Y):
        return (K_c / (Y * sigma)) ** 2 / math.pi
    if a_max is None:
        raise ValueError("a callable Y requires a_max (its validity limit)")
    f = lambda a: sif(sigma, a, Y(a)) - K_c
    lower = a_max * 1e-9
    if f(lower) > 0:
        raise ValueError("K > Kc even for the smallest crack")
    if f(a_max) < 0:
        raise ValueError("K < Kc up to a_max: no critical length within the validity range")
    return optimize.brentq(f, lower, a_max, xtol=1e-15, rtol=1e-13, maxiter=500)


# ======================= plastic zone =======================
@cite("dowling_2013", note="Irwin plastic zone; not read in this session")
def plastic_zone(K: float, sigma_y: float, case: str = "plane_stress") -> dict[str, float]:
    """Irwin first-order plastic-zone radius r_y and corrected zone diameter 2r_y.

    Parameters
    ----------
    K : float
        Stress-intensity factor [Pa√m].
    sigma_y : float
        Yield stress [Pa].
    case : {"plane_stress", "plane_strain"}
        Constraint.

    Returns
    -------
    dict
        ``r_y`` [m] and ``diameter = 2 r_y`` [m].

    Raises
    ------
    ValueError
        If ``sigma_y ≤ 0`` or the case is unknown.

    Notes
    -----
    Plane stress ``r_y = (1/2π)(K/σy)²``; plane strain ``r_y = (1/6π)(K/σy)²``.
    """
    if not (sigma_y > 0):
        raise ValueError("σy must be positive")
    if case == "plane_stress":
        ry = (K / sigma_y) ** 2 / (2 * math.pi)
    elif case == "plane_strain":
        ry = (K / sigma_y) ** 2 / (6 * math.pi)
    else:
        raise ValueError("case must be 'plane_stress' or 'plane_strain'")
    return {"r_y": ry, "diameter": 2 * ry}


@cite("dowling_2013", note="ASTM E399 size requirement; not read from the standard in this session")
def plane_strain_thickness(K_Ic: float, sigma_y: float) -> float:
    """ASTM E399 validity criterion: thickness B and crack length a ≥ 2.5 (KIc/σy)².

    Parameters
    ----------
    K_Ic : float
        Plane-strain fracture toughness [Pa√m].
    sigma_y : float
        Yield stress [Pa].

    Returns
    -------
    float
        Minimum B (and a) [m].
    """
    return 2.5 * (K_Ic / sigma_y) ** 2


# ======================= crack-growth rates =======================
@cite("paris_erdogan_1963")
def paris_rate(dK: float, C: float, m: float) -> float:
    """Paris law ``da/dN = C ΔK^m``.

    Parameters
    ----------
    dK : float
        Stress-intensity range ΔK (unit consistent with C).
    C, m : float
        Paris constants.

    Returns
    -------
    float
        Crack-growth rate [length/cycle].
    """
    return C * dK ** m


@cite("walker_1970")
def walker_rate(dK: float, R: float, C: float, m: float, gamma: float) -> float:
    """Walker law ``da/dN = C [ΔK/(1 − R)^(1−γ)]^m`` (γ = 1 recovers Paris).

    Parameters
    ----------
    dK : float
        ΔK (unit consistent with C).
    R : float
        Stress ratio, ``R < 1`` [-].
    C, m : float
        Paris constants at R = 0.
    gamma : float
        Walker exponent [-].

    Returns
    -------
    float
        Crack-growth rate [length/cycle].

    Raises
    ------
    ValueError
        If ``R ≥ 1``.
    """
    if not (R < 1):
        raise ValueError("R < 1 is required")
    return C * (dK / (1 - R) ** (1 - gamma)) ** m


@cite("forman_kearney_1967")
def forman_rate(dK: float, R: float, C: float, m: float, K_c: float) -> float:
    """Forman law ``da/dN = C ΔK^m / [(1 − R)Kc − ΔK]``.

    Parameters
    ----------
    dK : float
        ΔK (unit consistent with C and Kc).
    R : float
        Stress ratio [-].
    C, m : float
        Forman constants.
    K_c : float
        Fracture toughness (same unit as ΔK).

    Returns
    -------
    float
        Crack-growth rate [length/cycle]; ``inf`` once ΔK reaches (1 − R)Kc.
    """
    denominator = (1 - R) * K_c - dK
    if denominator <= 0:
        return math.inf
    return C * dK ** m / denominator


# ======================= life integral =======================
@cite("paris_erdogan_1963")
def paris_life(C: float, m: float, d_sigma: float, a0: float, af: float, Y: float = 1.0) -> float:
    """Closed-form Paris life for a constant geometry factor.

    Parameters
    ----------
    C, m : float
        Paris constants (C consistent with the unit of ``d_sigma·√m``).
    d_sigma : float
        Stress range Δσ.
    a0, af : float
        Initial and final crack length [m], ``af > a0``.
    Y : float
        Constant geometry factor [-].

    Returns
    -------
    float
        Cycles N [-].

    Raises
    ------
    ValueError
        If ``a0 ≤ 0``, ``af ≤ a0``, or C or Δσ is not positive.

    Notes
    -----
    ``N = [af^(1−m/2) − a0^(1−m/2)] / [C (YΔσ√π)^m (1 − m/2)]``; for m = 2, ``N = ln(af/a0)/[C π (YΔσ)²]``.
    """
    _check_a(a0)
    if not (af > a0):
        raise ValueError("af > a0 is required")
    if not (C > 0 and d_sigma > 0):
        raise ValueError("C and Δσ must be positive")
    k = C * (Y * d_sigma * math.sqrt(math.pi)) ** m
    if math.isclose(m, 2.0):
        return math.log(af / a0) / k
    e = 1 - m / 2
    return (af ** e - a0 ** e) / (k * e)


def life_numeric(rate_func: Callable[[float], float], a0: float, af: float, n_sub: int = 1) -> float:
    """Crack-growth life ``N = ∫ da / (da/dN)(a)`` by adaptive Gauss-Kronrod quadrature (``quad``).

    Parameters
    ----------
    rate_func : callable
        ``rate_func(a) → da/dN`` [m/cycle].
    a0, af : float
        Initial and final crack length [m].
    n_sub : int
        Number of geometric sub-intervals (useful for a wide a0-af ratio).

    Returns
    -------
    float
        Cycles N [-].

    Raises
    ------
    ValueError
        If ``a0 ≤ 0`` or ``af ≤ a0``.
    """
    _check_a(a0)
    if not (af > a0):
        raise ValueError("af > a0 is required")
    bounds = np.geomspace(a0, af, n_sub + 1)
    N = 0.0
    for x0, x1 in zip(bounds[:-1], bounds[1:], strict=True):
        value, _ = integrate.quad(lambda a: 1.0 / rate_func(a), x0, x1, epsabs=0, epsrel=1e-12, limit=200)
        N += value
    return N


@cite("paris_erdogan_1963")
def paris_life_numeric(C: float, m: float, d_sigma: float, a0: float, af: float, Y: GeometryFactor = 1.0,
                       n_sub: int = 8) -> float:
    """Numerical Paris life for a variable geometry factor Y(a).

    Parameters
    ----------
    C, m, d_sigma, a0, af
        As in :func:`paris_life`.
    Y : float or callable
        Constant or ``Y(a)``.
    n_sub : int
        Geometric sub-intervals, see :func:`life_numeric`.

    Returns
    -------
    float
        Cycles N [-].
    """
    Yf: Callable[[float], float] = Y if callable(Y) else (lambda a: Y)
    return life_numeric(lambda a: paris_rate(Yf(a) * d_sigma * math.sqrt(math.pi * a), C, m),
                        a0, af, n_sub)


def crack_growth(rate_func: Callable[[float], float], a0: float, N_target: float,
                 a_max: float) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Integrate the ODE ``da/dN = f(a)`` up to ``N_target`` cycles (``solve_ivp``, RK45).

    Parameters
    ----------
    rate_func : callable
        ``rate_func(a) → da/dN`` [m/cycle].
    a0 : float
        Initial crack length [m].
    N_target : float
        Cycles to integrate [-].
    a_max : float
        Crack length at which integration stops (terminal event) [m].

    Returns
    -------
    tuple of ndarray
        ``(N, a)`` histories.
    """
    def event(N: float, a: NDArray[np.float64]) -> float:
        return float(a[0] - a_max)

    event_any: Any = event
    event_any.terminal = True
    c = integrate.solve_ivp(lambda N, a: [rate_func(a[0])], (0, N_target), [a0], events=event_any,
                            rtol=1e-10, atol=1e-14 * a_max, dense_output=False)
    return c.t, c.y[0]
