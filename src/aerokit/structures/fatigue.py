"""Fatigue: S-N (Basquin, Shigley estimate), strain-life (Coffin-Manson), Marin factors, mean-stress
corrections, ASTM E1049-85 rainflow counting, Palmgren-Miner damage, equivalent constant amplitude;
stress concentration (Kt, notch sensitivity, Neuber's rule).

Sources (those read are also named in the tests):

- Shigley 10th ed. Ch. 6 (Hijazi lecture notes CH6 read): S'e = 0.5 Sut (Sut ≤ 1400 MPa), 700 MPa above;
  ka = a·Sut^b (Table 6-2), kb = 1.24 d^−0.107 (2.79-51 mm), 1.51 d^−0.157 (51-254 mm), axial kb = 1;
  kc = 1 / 0.85 / 0.59; kd polynomial (40-540 °C);
  σ'f = Sut + 345 MPa, b = −log(σ'f/Se)/log(2Ne), f = (σ'f/Sut)(2·10³)^b, a = (f Sut)²/Se;
  Kf = 1 + q(Kt − 1), Neuber: Kf = 1 + (Kt − 1)/(1 + √a/√r).
- Table 6-2 constants: ground 1.58/−0.085, machined 4.51/−0.265, hot-rolled 57.7/−0.718,
  as-forged 272/−0.995 (MPa). The machined and forged values were confirmed with worked examples that were
  read; ground and hot-rolled were NOT read from the source in this session.
- ke = 1 − 0.08 z_a (Shigley Sec. 6-9; 8 % standard-deviation assumption -- "σ̂ = 8 %" in the Hijazi notes;
  the relation itself was not read in this session, the table value 90 % → 0.897 was read in the Gantep tutorial).
- Mean stress: Goodman, Gerber, Soderberg (Shigley Sec. 6-12); Morrow (Dowling, Mechanical Behavior of
  Materials, Ch. 9-10); Smith, Watson & Topper, J. Materials 5 (1970);
  Walker, ASTM STP 462 (1970): σar = σmax^(1−γ) σa^γ.
- Rainflow: ASTM E1049-85 Sec. 5.4.4 (four-step stack algorithm, half cycles included).
- Kt: Inglis (1913) 1 + 2a/b; Heywood (1952) Ktn = 2 + (1 − d/W)³; Howland (1930) curve fit
  Ktg = 0.284 + 2/(1 − d/W) − 0.600(1 − d/W) + 1.32(1 − d/W)² -- both read from
  Deghboudj et al., U.P.B. Sci. Bull. D 78(4) 2016, Eqs. 7-10 and Table 1.
- Peterson q = 1/(1 + α/r) (Peterson's Stress Concentration Factors). Neuber's rule
  σ·ε = (Kt·S)²/E with Ramberg-Osgood ε = σ/E + (σ/K')^(1/n') (Neuber 1961; Dowling Ch. 14).

SI units (Pa). Shigley's curve fits in MPa are evaluated internally after converting to MPa.
"""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable, Iterable

import numpy as np
from numpy.typing import ArrayLike
from scipy import optimize, stats

from aerokit.references import cite

MPA = 1e6


# ======================= S-N (stress-life) =======================
@cite("budynas_nisbett_2015", note="Sec. 6-7 (Hijazi CH6 notes p. 5)")
def se_estimated(Sut: float) -> float:
    """Rotating-beam endurance limit estimate S'e for steel.

    Parameters
    ----------
    Sut : float
        Ultimate tensile strength [Pa].

    Returns
    -------
    float
        ``0.5 Sut`` for Sut ≤ 1400 MPa, otherwise 700 MPa [Pa].

    Raises
    ------
    ValueError
        If ``Sut ≤ 0``.
    """
    if not (Sut > 0):
        raise ValueError("Sut must be positive")
    return 0.5 * Sut if Sut <= 1400 * MPA else 700 * MPA


@cite("budynas_nisbett_2015", note="Sec. 6-7 (Hijazi CH6 notes pp. 9-11)")
def shigley_sn(Sut: float, Se: float, Ne: float = 1e6, f: float | None = None) -> dict[str, float]:
    """Shigley S-N line ``Sf = a N^b`` between 10³ cycles and Ne.

    Parameters
    ----------
    Sut : float
        Ultimate tensile strength [Pa].
    Se : float
        Endurance limit [Pa], ``0 < Se < Sut``.
    Ne : float
        Cycles at the endurance limit [-].
    f : float, optional
        Fatigue strength fraction at 10³ cycles; if omitted it is computed with ``σ'f = Sut + 345 MPa``.

    Returns
    -------
    dict
        ``a`` [Pa], ``b`` [-], ``f`` [-], ``sigma_f`` (σ'f estimate) [Pa].

    Raises
    ------
    ValueError
        Unless ``0 < Se < Sut``.

    Notes
    -----
    ``a = (f Sut)²/Se``, ``b = −log10(f Sut/Se)/3``.
    """
    if not (Sut > 0 and Se > 0 and Se < Sut):
        raise ValueError("0 < Se < Sut is required")
    sigma_f = Sut + 345 * MPA
    if f is None:
        b_f = -math.log10(sigma_f / Se) / math.log10(2 * Ne)
        f = sigma_f / Sut * (2e3) ** b_f
    a = (f * Sut) ** 2 / Se
    b = -math.log10(f * Sut / Se) / 3
    return {"a": a, "b": b, "f": f, "sigma_f": sigma_f}


def sn_strength(a: float, b: float, N: float) -> float:
    """Fatigue strength ``Sf = a N^b`` of a power-law S-N curve.

    Parameters
    ----------
    a : float
        Coefficient [Pa].
    b : float
        Exponent [-] (negative).
    N : float
        Number of cycles [-].

    Returns
    -------
    float
        Strength [Pa].

    Raises
    ------
    ValueError
        If ``N ≤ 0``.
    """
    if not (N > 0):
        raise ValueError("N must be positive")
    return a * N ** b


def sn_life(a: float, b: float, sigma_a: float) -> float:
    """Life ``N = (σa/a)^(1/b)`` of a power-law S-N curve.

    Parameters
    ----------
    a, b : float
        S-N coefficient [Pa] and exponent [-].
    sigma_a : float
        Stress amplitude [Pa].

    Returns
    -------
    float
        Cycles to failure [-].

    Raises
    ------
    ValueError
        If ``sigma_a ≤ 0``.
    """
    if not (sigma_a > 0):
        raise ValueError("sigma_a must be positive")
    return (sigma_a / a) ** (1 / b)


@cite("basquin_1910")
def basquin_amplitude(sigma_f: float, b: float, N: float) -> float:
    """Basquin amplitude ``σa = σ'f (2N)^b`` (N cycles, 2N reversals).

    Parameters
    ----------
    sigma_f : float
        Fatigue strength coefficient σ'f [Pa].
    b : float
        Fatigue strength exponent [-].
    N : float
        Cycles [-].

    Returns
    -------
    float
        Stress amplitude [Pa].
    """
    return sigma_f * (2 * N) ** b


@cite("basquin_1910")
def basquin_life(sigma_a: float, sigma_f: float, b: float) -> float:
    """Inverse Basquin relation ``N = ½ (σa/σ'f)^(1/b)``.

    Parameters
    ----------
    sigma_a : float
        Stress amplitude [Pa].
    sigma_f, b : float
        Basquin coefficient [Pa] and exponent [-].

    Returns
    -------
    float
        Cycles to failure [-].

    Raises
    ------
    ValueError
        If ``sigma_a ≤ 0``.
    """
    if not (sigma_a > 0):
        raise ValueError("sigma_a must be positive")
    return 0.5 * (sigma_a / sigma_f) ** (1 / b)


# ======================= strain-life =======================
@cite("coffin_1954")
@cite("manson_1953")
@cite("morrow_1968", note="mean-stress correction")
def coffin_manson_amplitude(N: float, E: float, sigma_f: float, b: float, eps_f: float, c: float,
                            sigma_m: float = 0.0, correction: str = "no") -> float:
    """Strain amplitude ``εa(N) = (σ'f − σm)/E (2N)^b + ε'f (2N)^c``.

    Parameters
    ----------
    N : float
        Cycles [-].
    E : float
        Young's modulus [Pa].
    sigma_f, b : float
        Fatigue strength coefficient [Pa] and exponent [-].
    eps_f, c : float
        Fatigue ductility coefficient [-] and exponent [-].
    sigma_m : float
        Mean stress [Pa].
    correction : {"no", "morrow"}
        ``"no"`` ignores σm; ``"morrow"`` uses σ'f − σm in the elastic term.

    Returns
    -------
    float
        Strain amplitude [-].

    Raises
    ------
    ValueError
        If ``correction`` is unknown.
    """
    sm = sigma_m if correction == "morrow" else 0.0
    if correction not in ("no", "morrow"):
        raise ValueError("correction must be 'no' or 'morrow'")
    return (sigma_f - sm) / E * (2 * N) ** b + eps_f * (2 * N) ** c


@cite("coffin_1954")
@cite("manson_1953")
@cite("smith_watson_topper_1970", note="SWT parameter σmax·εa")
def coffin_manson_life(eps_a: float, E: float, sigma_f: float, b: float, eps_f: float, c: float,
                       sigma_m: float = 0.0, correction: str = "no") -> float:
    """Cycles to failure for a given strain amplitude (root finding in log N).

    Parameters
    ----------
    eps_a : float
        Strain amplitude [-].
    E, sigma_f, b, eps_f, c
        Strain-life constants, see :func:`coffin_manson_amplitude`.
    sigma_m : float
        Mean stress [Pa]; for ``correction="swt"`` it is interpreted as **σmax = σa + σm**.
    correction : {"no", "morrow", "swt"}
        Mean-stress treatment.

    Returns
    -------
    float
        Cycles N [-].

    Raises
    ------
    ValueError
        If ``eps_a ≤ 0``, or σmax ≤ 0 for SWT.

    Notes
    -----
    SWT: ``σmax εa = (σ'f²/E)(2N)^(2b) + σ'f ε'f (2N)^(b+c)``.
    """
    if not (eps_a > 0):
        raise ValueError("eps_a must be positive")
    if correction == "swt":
        target = sigma_m * eps_a
        if not (target > 0):
            raise ValueError("SWT requires σmax > 0")
        g = lambda L: math.log(sigma_f ** 2 / E * (2 * 10 ** L) ** (2 * b)
                               + sigma_f * eps_f * (2 * 10 ** L) ** (b + c)) - math.log(target)
    else:
        g = lambda L: math.log(coffin_manson_amplitude(10 ** L, E, sigma_f, b, eps_f, c,
                                                       sigma_m, correction)) - math.log(eps_a)
    return 10 ** optimize.brentq(g, -3, 20, xtol=1e-14, rtol=1e-14, maxiter=500)


@cite("dowling_2013", note="strain-life transition life")
def transition_life(E: float, sigma_f: float, b: float, eps_f: float, c: float) -> float:
    """Transition life 2Nt (reversals) at which the elastic and plastic strain amplitudes are equal.

    Parameters
    ----------
    E, sigma_f, b, eps_f, c
        Strain-life constants, see :func:`coffin_manson_amplitude`.

    Returns
    -------
    float
        ``2Nt = (ε'f E/σ'f)^(1/(b − c))`` [reversals].
    """
    return (eps_f * E / sigma_f) ** (1 / (b - c))


# ======================= Marin factors =======================
_SURFACE = {  # a [MPa^(−b)], b -- Shigley Table 6-2 (SI)
    "ground": (1.58, -0.085),        # not read from the source in this session
    "machined": (4.51, -0.265),      # read (Hijazi CH6, Gantep tutorial)
    "cold_drawn": (4.51, -0.265),
    "hot_rolled": (57.7, -0.718),    # not read from the source in this session
    "forged": (272.0, -0.995),       # read (Gantep tutorial)
}


@cite("budynas_nisbett_2015", note="Table 6-2")
def marin_ka(Sut: float, surface: str) -> float:
    """Surface factor ``ka = a Sut^b`` (Sut given in Pa, evaluated in MPa).

    Parameters
    ----------
    Sut : float
        Ultimate tensile strength [Pa].
    surface : {"ground", "machined", "cold_drawn", "hot_rolled", "forged"}
        Surface finish.

    Returns
    -------
    float
        ka [-].

    Raises
    ------
    ValueError
        If the surface is unknown or ``Sut ≤ 0``.
    """
    if surface not in _SURFACE:
        raise ValueError(f"surface must be one of: {', '.join(_SURFACE)}")
    if not (Sut > 0):
        raise ValueError("Sut must be positive")
    a, b = _SURFACE[surface]
    return a * (Sut / MPA) ** b


@cite("budynas_nisbett_2015", note="Sec. 6-9 (Hijazi CH6 notes p. 6)")
def marin_kb(d: float, loading: str = "bending") -> float:
    """Size factor kb.

    Parameters
    ----------
    d : float
        Diameter [m]; for a non-rotating section pass the equivalent diameter ``de = 0.37 d``.
    loading : str
        ``"axial"`` gives 1; anything else (bending, torsion) uses the size relation.

    Returns
    -------
    float
        ``1.24 d^−0.107`` (2.79 ≤ d ≤ 51 mm) or ``1.51 d^−0.157`` (51 < d ≤ 254 mm), d in mm [-].

    Raises
    ------
    ValueError
        If d is outside 2.79-254 mm (non-axial loading).
    """
    if loading == "axial":
        return 1.0
    dmm = d * 1e3
    if 2.79 <= dmm <= 51:
        return 1.24 * dmm ** -0.107
    if 51 < dmm <= 254:
        return 1.51 * dmm ** -0.157
    raise ValueError("the kb relation is valid for 2.79 ≤ d ≤ 254 mm")


@cite("budynas_nisbett_2015", note="Sec. 6-9 (Hijazi CH6 notes p. 7)")
def marin_kc(loading: str) -> float:
    """Load factor kc: bending 1, axial 0.85, torsion 0.59.

    Parameters
    ----------
    loading : {"bending", "axial", "torsion"}
        Load type.

    Returns
    -------
    float
        kc [-].

    Raises
    ------
    ValueError
        If the load type is unknown.
    """
    table = {"bending": 1.0, "axial": 0.85, "torsion": 0.59}
    if loading not in table:
        raise ValueError("loading must be bending, axial or torsion")
    return table[loading]


@cite("budynas_nisbett_2015", note="Sec. 6-9 polynomial (Hijazi CH6 notes p. 7)")
def marin_kd(T_c: float) -> float:
    """Temperature factor kd (fourth-order polynomial, 40 ≤ T ≤ 540 °C).

    Parameters
    ----------
    T_c : float
        Temperature [°C].

    Returns
    -------
    float
        kd [-].

    Raises
    ------
    ValueError
        Outside 40-540 °C.
    """
    if not (40 <= T_c <= 540):
        raise ValueError("the kd polynomial is valid for 40-540 °C")
    T = T_c
    return (0.9877 + 0.6507e-3 * T - 0.3414e-5 * T ** 2 + 0.5621e-8 * T ** 3
            - 0.6246e-11 * T ** 4)


@cite("budynas_nisbett_2015", note="Sec. 6-9, 8 % standard deviation of the endurance limit")
def marin_ke(reliability: float) -> float:
    """Reliability factor ``ke = 1 − 0.08 z_a`` (z_a: standard normal variate).

    Parameters
    ----------
    reliability : float
        Reliability R, ``0.5 ≤ R < 1`` [-].

    Returns
    -------
    float
        ke [-].

    Raises
    ------
    ValueError
        Outside ``0.5 ≤ R < 1``.
    """
    if not (0.5 <= reliability < 1):
        raise ValueError("reliability must satisfy 0.5 ≤ R < 1")
    return 1 - 0.08 * stats.norm.ppf(reliability)


@cite("budynas_nisbett_2015", note="Marin equation, Sec. 6-9")
def marin_se(Se_prime: float, ka: float = 1.0, kb: float = 1.0, kc: float = 1.0, kd: float = 1.0,
             ke: float = 1.0, kf: float = 1.0) -> float:
    """Marin equation ``Se = ka kb kc kd ke kf S'e``.

    Parameters
    ----------
    Se_prime : float
        Rotating-beam endurance limit S'e [Pa].
    ka, kb, kc, kd, ke, kf : float
        Marin factors [-].

    Returns
    -------
    float
        Corrected endurance limit Se [Pa].
    """
    return ka * kb * kc * kd * ke * kf * Se_prime


# ======================= mean stress =======================
@cite("budynas_nisbett_2015", note="Goodman, Gerber, Soderberg, Sec. 6-12")
@cite("dowling_2013", note="Morrow")
@cite("smith_watson_topper_1970")
@cite("walker_1970")
def equivalent_fully_reversed(sigma_a: float, sigma_m: float, method: str, Sut: float | None = None,
                              Sy: float | None = None, sigma_f: float | None = None,
                              gamma: float | None = None) -> float:
    """Equivalent fully reversed (R = −1) amplitude σar of a cycle with mean stress.

    Parameters
    ----------
    sigma_a, sigma_m : float
        Stress amplitude (≥ 0) and mean stress [Pa].
    method : {"goodman", "gerber", "soderberg", "morrow", "swt", "walker"}
        Mean-stress correction.
    Sut, Sy, sigma_f : float, optional
        Ultimate strength (Goodman, Gerber), yield strength (Soderberg), fatigue strength coefficient
        (Morrow) [Pa].
    gamma : float, optional
        Walker exponent, ``0 < γ ≤ 1``.

    Returns
    -------
    float
        σar [Pa].

    Raises
    ------
    ValueError
        If σa < 0, the required strength is missing, the mean stress reaches the strength, σmax ≤ 0
        for SWT/Walker, or the method is unknown.

    Notes
    -----
    goodman ``σa/(1 − σm/Sut)``; gerber ``σa/(1 − (σm/Sut)²)``; soderberg ``σa/(1 − σm/Sy)``;
    morrow ``σa/(1 − σm/σ'f)``; swt ``√(σmax σa)``; walker ``σmax^(1−γ) σa^γ``.
    """
    sa, sm = float(sigma_a), float(sigma_m)
    if sa < 0:
        raise ValueError("sigma_a must not be negative")
    smax = sa + sm
    if method in ("goodman", "gerber", "soderberg", "morrow"):
        S = {"goodman": Sut, "gerber": Sut, "soderberg": Sy, "morrow": sigma_f}[method]
        if S is None or not (S > 0):
            raise ValueError(f"{method} requires the corresponding strength value")
        ratio = sm / S
        denominator = 1 - ratio ** 2 if method == "gerber" else 1 - ratio
        if method == "gerber" and sm < 0:
            denominator = 1.0   # Gerber is not normally used for compressive means; the mean is ignored
        if denominator <= 0:
            raise ValueError("the mean stress reaches or exceeds the strength")
        return sa / denominator
    if method in ("swt", "walker"):
        if smax <= 0:
            raise ValueError(f"{method}: damage is undefined for σmax ≤ 0 (infinite life assumed)")
        if method == "swt":
            return math.sqrt(smax * sa)
        if gamma is None or not (0 < gamma <= 1):
            raise ValueError("walker requires 0 < gamma ≤ 1")
        return smax ** (1 - gamma) * sa ** gamma
    raise ValueError("method must be goodman, gerber, soderberg, morrow, swt or walker")


@cite("budynas_nisbett_2015", note="Sec. 6-12, load line through the origin")
def safety_coefficient(sigma_a: float, sigma_m: float, Se: float, Sut: float | None = None,
                       Sy: float | None = None, method: str = "goodman") -> float:
    """Fatigue factor of safety along a load line through the origin.

    Parameters
    ----------
    sigma_a, sigma_m : float
        Stress amplitude and (tensile) mean stress, both ≥ 0 [Pa].
    Se : float
        Endurance limit [Pa].
    Sut, Sy : float, optional
        Ultimate (Goodman, Gerber) and yield (Soderberg) strength [Pa].
    method : {"goodman", "soderberg", "gerber"}
        Failure criterion.

    Returns
    -------
    float
        Factor of safety n [-].

    Raises
    ------
    ValueError
        If ``Se ≤ 0``, a stress is negative or the method is unknown.

    Notes
    -----
    goodman ``1/n = σa/Se + σm/Sut``; soderberg ``1/n = σa/Se + σm/Sy``;
    gerber ``n = ½(Sut/σm)²(σa/Se)[−1 + √(1 + (2σm Se/(Sut σa))²)]``, evaluated in the equivalent,
    cancellation-free form ``n = 2Se/(σa[1 + √(1 + x²)])``, ``x = 2σm Se/(Sut σa)``.
    The Goodman form was read in the Hijazi CH6 notes and the Gantep tutorial; the closed Gerber form was
    not read from a source in this session (tested through its σm → 0 limit Se/σa).
    """
    if not (Se > 0 and sigma_a >= 0 and sigma_m >= 0):
        raise ValueError("Se > 0, σa ≥ 0 and σm ≥ 0 are required (tensile mean only)")
    if method == "goodman":
        return 1 / (sigma_a / Se + sigma_m / Sut)  # type: ignore[operator]
    if method == "soderberg":
        return 1 / (sigma_a / Se + sigma_m / Sy)  # type: ignore[operator]
    if method == "gerber":
        if sigma_a == 0:
            return Sut / sigma_m  # type: ignore[operator]
        x = 2 * sigma_m * Se / (Sut * sigma_a)  # type: ignore[operator]
        return 2 * Se / (sigma_a * (1 + math.sqrt(1 + x * x)))
    raise ValueError("method must be goodman, soderberg or gerber")


@cite("budynas_nisbett_2015", note="Sec. 6-12")
def goodman_intersection(r: float, Se: float, Sut: float) -> dict[str, float]:
    """Intersection of a load line of slope ``r = σa/σm`` with the Goodman line.

    Parameters
    ----------
    r : float
        Load-line slope σa/σm [-].
    Se, Sut : float
        Endurance limit and ultimate strength (any consistent unit).

    Returns
    -------
    dict
        ``Sa = r Se Sut/(r Sut + Se)`` and ``Sm = Sa/r``.
    """
    Sa = r * Se * Sut / (r * Sut + Se)
    return {"Sa": Sa, "Sm": Sa / r}


# ======================= rainflow (ASTM E1049-85) =======================
def turn_points(series: Iterable[float]) -> list[float]:
    """Reduce a load history to its turning points (peaks and valleys).

    Parameters
    ----------
    series : iterable of float
        Load or stress history (at least two finite values).

    Returns
    -------
    list of float
        Reversal sequence; first and last points are kept, repeated values and points that do not change
        the slope direction are removed.

    Raises
    ------
    ValueError
        With fewer than two points or a non-finite value.
    """
    x = [float(v) for v in series]
    if len(x) < 2:
        raise ValueError("at least two points are required")
    if not all(math.isfinite(v) for v in x):
        raise ValueError("the series contains a non-finite value")
    plain = [x[0]]
    for v in x[1:]:
        if v != plain[-1]:
            plain.append(v)
    if len(plain) < 2:
        return plain
    tp = [plain[0]]
    for i in range(1, len(plain) - 1):
        if (plain[i] - plain[i - 1]) * (plain[i + 1] - plain[i]) < 0:
            tp.append(plain[i])
    tp.append(plain[-1])
    return tp


@cite("astm_e1049_1985", note="Sec. 5.4.4")
def rainflow(series: Iterable[float]) -> list[tuple[float, float, float]]:
    """ASTM E1049-85 rainflow cycle counting.

    Parameters
    ----------
    series : iterable of float
        Load history.

    Returns
    -------
    list of tuple
        ``(range, mean, count)`` with count 1.0 (full cycle) or 0.5 (half cycle).

    Notes
    -----
    X is the most recent range and Y the previous one. If X < Y read the next point; if X ≥ Y and Y contains
    the starting point S, count Y as a half cycle and discard its first point; otherwise count Y as a full
    cycle and discard both of its points. When the data are exhausted every remaining range is a half cycle.

    Examples
    --------
    >>> rainflow([0.0, 2.0, 0.0])
    [(2.0, 1.0, 0.5), (2.0, 1.0, 0.5)]
    """
    stack: list[float] = []
    result: list[tuple[float, float, float]] = []
    for p in turn_points(series):
        stack.append(p)
        while len(stack) >= 3:
            X = abs(stack[-1] - stack[-2])
            Y = abs(stack[-2] - stack[-3])
            if X < Y:
                break
            if len(stack) == 3:
                result.append((Y, 0.5 * (stack[0] + stack[1]), 0.5))
                stack.pop(0)
            else:
                result.append((Y, 0.5 * (stack[-2] + stack[-3]), 1.0))
                last = stack.pop()
                stack.pop()
                stack.pop()
                stack.append(last)
    for i in range(len(stack) - 1):
        result.append((abs(stack[i + 1] - stack[i]), 0.5 * (stack[i + 1] + stack[i]), 0.5))
    return result


def rainflow_summary(series: Iterable[float], decimals: int = 12) -> dict[float, float]:
    """Total rainflow count per range, ``{range: count}``.

    Parameters
    ----------
    series : iterable of float
        Load history.
    decimals : int
        Ranges are rounded to this many decimals before grouping.

    Returns
    -------
    dict
        Counts (cycles) keyed by range, sorted by range.
    """
    d: defaultdict[float, float] = defaultdict(float)
    for interval, _, n in rainflow(series):
        d[round(interval, decimals)] += n
    return dict(sorted(d.items()))


# ======================= Palmgren-Miner =======================
@cite("palmgren_1924")
@cite("miner_1945")
def miner_damage(counts: Iterable[tuple[float, float]], life_func: Callable[[float], float]) -> float:
    """Palmgren-Miner damage ``D = Σ nᵢ/Nᵢ``.

    Parameters
    ----------
    counts : iterable of (float, float)
        ``(amplitude_or_range, n)`` pairs; non-positive amplitudes and zero counts are skipped.
    life_func : callable
        ``life_func(amplitude) → N`` cycles to failure.

    Returns
    -------
    float
        Damage D [-].

    Raises
    ------
    ValueError
        If a cycle count is negative.
    """
    D = 0.0
    for s, n in counts:
        if n < 0:
            raise ValueError("cycle count must not be negative")
        if s <= 0 or n == 0:
            continue
        D += n / life_func(s)
    return D


@cite("palmgren_1924")
@cite("miner_1945")
def miner_life(counts: Iterable[tuple[float, float]], life_func: Callable[[float], float],
               D_critical: float = 1.0) -> float:
    """Number of repetitions of a load block until failure, ``D_critical / D_block``.

    Parameters
    ----------
    counts, life_func
        As in :func:`miner_damage`.
    D_critical : float
        Damage at failure [-].

    Returns
    -------
    float
        Block repetitions [-]; ``inf`` if the block causes no damage.
    """
    D = miner_damage(counts, life_func)
    return math.inf if D == 0 else D_critical / D


@cite("miner_1945")
@cite("basquin_1910", note="m = −1/b")
def equivalent_constant_amplitude(amplitudes: ArrayLike, counts: ArrayLike, m: float) -> float:
    """Equivalent constant amplitude ``S_eq = (Σ nᵢ Sᵢ^m / Σ nᵢ)^(1/m)``.

    Parameters
    ----------
    amplitudes : array_like
        Amplitudes Sᵢ [Pa].
    counts : array_like
        Cycle counts nᵢ [-], same shape.
    m : float
        Inverse S-N slope, ``m = −1/b`` (Basquin) [-].

    Returns
    -------
    float
        S_eq [Pa]; it gives the same Miner damage for the same total number of cycles.

    Raises
    ------
    ValueError
        If the shapes differ, ``Σn ≤ 0`` or ``m ≤ 0``.
    """
    g, n = np.asarray(amplitudes, float), np.asarray(counts, float)
    if g.shape != n.shape or n.sum() <= 0 or not (m > 0):
        raise ValueError("amplitude and count lengths must match, Σn > 0 and m > 0")
    return float((np.sum(n * g ** m) / np.sum(n)) ** (1 / m))


# ======================= stress concentration =======================
@cite("inglis_1913")
def kt_ellipse(a: float, b: float) -> float:
    """Elliptical hole in an infinite plate, ``Kt = 1 + 2a/b``.

    Parameters
    ----------
    a : float
        Semi-axis perpendicular to the load [m].
    b : float
        Semi-axis parallel to the load [m].

    Returns
    -------
    float
        Kt [-] (3 for a circular hole).

    Raises
    ------
    ValueError
        If a or b is not positive.
    """
    if not (a > 0 and b > 0):
        raise ValueError("a and b must be positive")
    return 1 + 2 * a / b


@cite("heywood_1952", note="as given by Deghboudj et al. 2016, Eqs. 7-10")
def kt_hole_heywood(d: float, W: float, base: str = "net") -> float:
    """Central hole in a finite-width plate (Heywood): ``Ktn = 2 + (1 − d/W)³``.

    Parameters
    ----------
    d : float
        Hole diameter [m].
    W : float
        Plate width [m].
    base : {"net", "gross"}
        Reference stress: net section, or gross section (``Ktg = Ktn/(1 − d/W)``); any value other than
        ``"net"`` is treated as gross.

    Returns
    -------
    float
        Kt [-].

    Raises
    ------
    ValueError
        Unless ``0 ≤ d < W``.
    """
    if not (0 <= d < W):
        raise ValueError("0 ≤ d < W is required")
    x = 1 - d / W
    ktn = 2 + x ** 3
    return ktn if base == "net" else ktn / x


@cite("howland_1930", note="curve fit as given by Deghboudj et al. 2016, Eqs. 7-10")
def kt_hole_howland(d: float, W: float, base: str = "net") -> float:
    """Curve fit to Howland's finite-width hole solution.

    Parameters
    ----------
    d : float
        Hole diameter [m].
    W : float
        Plate width [m].
    base : {"net", "gross"}
        Reference stress (any value other than ``"net"`` means gross).

    Returns
    -------
    float
        Kt [-].

    Raises
    ------
    ValueError
        Unless ``0 ≤ d < W``.

    Notes
    -----
    ``Ktg = 0.284 + 2/(1 − d/W) − 0.600(1 − d/W) + 1.32(1 − d/W)²``, ``Ktn = Ktg (1 − d/W)``.
    """
    if not (0 <= d < W):
        raise ValueError("0 ≤ d < W is required")
    x = 1 - d / W
    ktg = 0.284 + 2 / x - 0.600 * x + 1.32 * x ** 2
    return ktg * x if base == "net" else ktg


@cite("pilkey_2008")
def peterson_q(r: float, alpha: float) -> float:
    """Peterson notch sensitivity ``q = 1/(1 + α/r)``.

    Parameters
    ----------
    r : float
        Notch root radius [m].
    alpha : float
        Material characteristic length [m].

    Returns
    -------
    float
        q [-].

    Raises
    ------
    ValueError
        Unless ``r > 0`` and ``α ≥ 0``.
    """
    if not (r > 0 and alpha >= 0):
        raise ValueError("r > 0 and α ≥ 0 are required")
    return 1 / (1 + alpha / r)


@cite("budynas_nisbett_2015", note="Neuber notch sensitivity (Hijazi CH6 notes p. 9)")
def neuber_q(r: float, root_a: float) -> float:
    """Neuber notch sensitivity ``q = 1/(1 + √a/√r)``.

    Parameters
    ----------
    r : float
        Notch root radius [m].
    root_a : float
        Neuber constant √a [m^½].

    Returns
    -------
    float
        q [-].

    Raises
    ------
    ValueError
        Unless ``r > 0`` and ``√a ≥ 0``.
    """
    if not (r > 0 and root_a >= 0):
        raise ValueError("r > 0 and √a ≥ 0 are required")
    return 1 / (1 + root_a / math.sqrt(r))


@cite("budynas_nisbett_2015", note="fatigue stress-concentration factor (Hijazi CH6 notes p. 12)")
def kf(Kt: float, q: float) -> float:
    """Fatigue stress-concentration factor ``Kf = 1 + q(Kt − 1)``.

    Parameters
    ----------
    Kt : float
        Theoretical stress concentration factor (≥ 1) [-].
    q : float
        Notch sensitivity, ``0 ≤ q ≤ 1`` [-].

    Returns
    -------
    float
        Kf [-].

    Raises
    ------
    ValueError
        Unless ``Kt ≥ 1`` and ``0 ≤ q ≤ 1``.
    """
    if not (Kt >= 1 and 0 <= q <= 1):
        raise ValueError("Kt ≥ 1 and 0 ≤ q ≤ 1 are required")
    return 1 + q * (Kt - 1)


@cite("ramberg_osgood_1943")
def ramberg_osgood(sigma: float, E: float, K: float, n: float) -> float:
    """Ramberg-Osgood strain in the cyclic form ``ε = σ/E + (σ/K)^(1/n)`` (sign preserved).

    Parameters
    ----------
    sigma : float
        Stress [Pa].
    E : float
        Young's modulus [Pa].
    K : float
        Strength coefficient K' [Pa].
    n : float
        Strain-hardening exponent n' [-].

    Returns
    -------
    float
        Strain [-].
    """
    return sigma / E + math.copysign(abs(sigma / K) ** (1 / n), sigma)


@cite("neuber_1961")
@cite("dowling_2013", note="Ch. 14")
def neuber_rule(S: float, Kt: float, E: float, K: float, n: float) -> dict[str, float]:
    """Monotonic Neuber's rule ``σ ε = (Kt S)²/E`` with a Ramberg-Osgood material.

    Parameters
    ----------
    S : float
        Nominal stress [Pa] (sign preserved in the result).
    Kt : float
        Stress concentration factor (≥ 1) [-].
    E, K, n : float
        Ramberg-Osgood constants, see :func:`ramberg_osgood`.

    Returns
    -------
    dict
        Local ``sigma`` [Pa], ``eps`` [-] and the elastically computed ``sigma_elastic = Kt S`` [Pa].

    Raises
    ------
    ValueError
        Unless ``Kt ≥ 1`` and E, K, n are positive.
    """
    if not (Kt >= 1 and E > 0 and K > 0 and n > 0):
        raise ValueError("Kt ≥ 1 and E, K, n > 0 are required")
    se = Kt * abs(S)
    if se == 0:
        return {"sigma": 0.0, "eps": 0.0, "sigma_elastic": 0.0}
    target = se ** 2 / E
    f = lambda s: s * ramberg_osgood(s, E, K, n) - target
    s = optimize.brentq(f, 0.0, se, xtol=1e-14 * se, rtol=1e-14, maxiter=500)
    sign = math.copysign(1.0, S)
    return {"sigma": sign * s, "eps": sign * ramberg_osgood(s, E, K, n), "sigma_elastic": sign * se}


@cite("neuber_1961")
@cite("dowling_2013", note="Ch. 14, Masing hypothesis")
def neuber_range(dS: float, Kt: float, E: float, K_c: float, n_c: float) -> dict[str, float]:
    """Cyclic Neuber's rule (Masing): ``Δσ Δε = (Kt ΔS)²/E`` with ``Δε = Δσ/E + 2(Δσ/(2K'))^(1/n')``.

    Parameters
    ----------
    dS : float
        Nominal stress range [Pa] (> 0).
    Kt : float
        Stress concentration factor [-].
    E : float
        Young's modulus [Pa].
    K_c, n_c : float
        Cyclic strength coefficient K' [Pa] and exponent n' [-].

    Returns
    -------
    dict
        Local stress range ``d_sigma`` [Pa] and strain range ``d_eps`` [-].

    Raises
    ------
    ValueError
        If ``dS ≤ 0``.
    """
    if not (dS > 0):
        raise ValueError("ΔS must be positive")
    r = neuber_rule(dS / 2, Kt, E, K_c, n_c)
    return {"d_sigma": 2 * r["sigma"], "d_eps": 2 * r["eps"]}

