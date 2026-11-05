"""Flight loads: V-n diagram (maneuver + gust), design speeds, landing loads, wing root bending.

Regulatory sources (2011 CFR Title 14 Vol. 1 text, read from govinfo.gov on 2026-10-25):

- 14 CFR 23.333 (flight envelope), 23.335 (design airspeeds), 23.337 (limit maneuvering load
  factors), 23.341 (gust load factors; the formula image was read from the PDF:
  n = 1 + Kg Ude V a / (498 W/S)), 23.473 (ground load conditions: descent velocity
  4.4 (W/S)^(1/4) ft/s), 23.725(a) (free drop height).
- 14 CFR 25.337 (transport maneuvering load factor), 25.341(a) (discrete gust: Uds, Uref, Fg).

This is the old (pre-2017, prescriptive) Part 23 text; the current performance-based Part 23
carries these formulas through an "accepted means of compliance" (ASTM F3116). They are used
here as a reference.

Units: the interface is SI (N, m^2, m, m/s EAS). Internally the formulas are evaluated as in the
regulations, in lb, ft, knot and slug/ft^3.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from aerokit.aero import wing
from aerokit.aero.atmosphere import isa
from aerokit.references import cite

LB_N = 4.4482216152605          # 1 lbf [N]
FT = 0.3048                     # 1 ft [m]
KT = 1852.0 / 3600.0            # 1 knot [m/s]
PSF = LB_N / FT ** 2            # 1 lbf/ft² [Pa]
SLUG_FT3 = 515.378818           # 1 slug/ft³ [kg/m³]
G_FT = 32.174                   # g [ft/s²]

CATEGORIES = ("normal", "utility", "acrobatic", "commuter", "far25")


def _category(k: str) -> str:
    """Return ``k`` if it is a known category, else raise ValueError."""
    if k not in CATEGORIES:
        raise ValueError(f"category '{k}' is not defined; options: {', '.join(CATEGORIES)}")
    return k


# --- 23.337 / 25.337: maneuver load factors ---
@cite("cfr14_part23", "cfr14_part25", note="§23.337 and §25.337, 2011 edition text")
def n_maneuver(W: float, category: str = "normal") -> tuple[float, float]:
    """Limit maneuvering load factors.

    Parameters
    ----------
    W : float
        Design maximum takeoff weight [N], > 0.
    category : {"normal", "utility", "acrobatic", "commuter", "far25"}, optional
        Certification category.

    Returns
    -------
    n_pos : float
        Positive limit load factor [-].
    n_neg : float
        Negative limit load factor [-].

    Raises
    ------
    ValueError
        If the category is unknown or ``W <= 0``.

    Notes
    -----
    14 CFR 23.337 (2011): normal/commuter n >= 2.1 + 24 000/(W_lb + 10 000), need not exceed 3.8;
    utility 4.4; acrobatic 6.0. Negative: normal/utility/commuter -0.4 n, acrobatic -0.5 n.
    14 CFR 25.337 (2011): n >= 2.1 + 24 000/(W + 10 000), not less than 2.5, need not exceed 3.8;
    negative -1.0 (up to V_C; varies linearly to zero at V_D, applied in :func:`vn_diagram`).

    Examples
    --------
    >>> n_maneuver(3000 * LB_N, "utility")
    (4.4, -1.7600000000000002)
    """
    _category(category)
    if W <= 0:
        raise ValueError("weight must be positive")
    W_lb = W / LB_N
    formula = 2.1 + 24000.0 / (W_lb + 10000.0)
    if category in ("normal", "commuter"):
        n = min(formula, 3.8)
        return n, -0.4 * n
    if category == "utility":
        return 4.4, -0.4 * 4.4
    if category == "acrobatic":
        return 6.0, -0.5 * 6.0
    return min(max(formula, 2.5), 3.8), -1.0          # far25


# --- 23.335: design airspeeds ---
@cite("cfr14_part23", note="§23.335(a)(1)-(2)")
def vc_factor(WS_psf: float, category: str = "normal") -> float:
    """Coefficient k of the minimum design cruising speed V_C,min = k sqrt(W/S).

    Parameters
    ----------
    WS_psf : float
        Wing loading [lbf/ft^2].
    category : str, optional
        Certification category; ``"acrobatic"`` uses 36, all others 33.

    Returns
    -------
    float
        k [knot/sqrt(psf)]; for W/S > 20 psf it decreases linearly to 28.6 at W/S = 100 psf
        (constant beyond).
    """
    k0 = 36.0 if category == "acrobatic" else 33.0
    if WS_psf <= 20:
        return k0
    return k0 + (28.6 - k0) * (min(WS_psf, 100.0) - 20.0) / 80.0


@cite("cfr14_part23", note="§23.335(b)(2)-(3)")
def vd_factor(WS_psf: float, category: str = "normal") -> float:
    """Ratio k_D of the minimum design dive speed to V_C,min.

    Parameters
    ----------
    WS_psf : float
        Wing loading [lbf/ft^2].
    category : str, optional
        Certification category: normal/commuter 1.40, utility 1.50, acrobatic 1.55.

    Returns
    -------
    float
        k_D [-]; for W/S > 20 psf it decreases linearly to 1.35 at W/S = 100 psf (constant beyond).
    """
    k0 = {"utility": 1.50, "acrobatic": 1.55}.get(category, 1.40)
    if WS_psf <= 20:
        return k0
    return k0 + (1.35 - k0) * (min(WS_psf, 100.0) - 20.0) / 80.0


@cite("cfr14_part23", note="§23.335, 2011 edition text")
def design_speeds(W: float, S: float, CLmax: float, n_poz: float, category: str = "normal",
                  Vc: float | None = None, Vd: float | None = None, VH: float | None = None) -> dict[str, Any]:
    """Design airspeeds (EAS) per 14 CFR 23.335.

    Parameters
    ----------
    W : float
        Design weight [N].
    S : float
        Wing area [m^2].
    CLmax : float
        Maximum lift coefficient, flaps up [-].
    n_poz : float
        Positive limit maneuvering load factor [-].
    category : {"normal", "utility", "acrobatic", "commuter", "far25"}, optional
        Certification category.
    Vc, Vd : float, optional
        Chosen design cruising and dive speeds [m/s EAS]; default the regulatory minima.
        Required for ``"far25"``.
    VH : float, optional
        Maximum level-flight speed [m/s EAS]; V_C,min need not exceed 0.9 V_H.

    Returns
    -------
    dict[str, Any]
        ``VS``, ``VA``, ``VC``, ``VD`` design speeds [m/s EAS], ``VC_min``, ``VD_min`` regulatory
        minima [m/s EAS] (NaN for far25), ``WS`` wing loading [N/m^2], ``WS_psf`` [lbf/ft^2],
        ``suitable_VC``, ``suitable_VD`` True if the chosen speed is not below the minimum.

    Raises
    ------
    ValueError
        If an input is not positive, the category is unknown, Vc/Vd are missing for far25, or
        V_D <= V_C.

    Notes
    -----
    V_S = sqrt(2 W / (rho0 S CLmax)) (flaps up; CLmax used instead of CN_max - ASSUMPTION: normal
    force ~ lift). V_C,min = k sqrt(W/S) knot (W/S in psf). V_D >= max(1.25 V_C, k_D V_C,min).
    V_A >= V_S sqrt(n), need not exceed V_C. The 23.335 formulas are not defined for far25, so Vc
    and Vd must be given (25.335 is not implemented in this module).
    """
    _category(category)
    if min(W, S, CLmax, n_poz) <= 0:
        raise ValueError("W, S, CLmax and n_poz must be positive")
    rho0 = isa(0)["rho"]
    WS = W / S
    WS_psf = WS / PSF
    VS = math.sqrt(2 * WS / (rho0 * CLmax))
    if category == "far25":
        if Vc is None or Vd is None:
            raise ValueError("Vc and Vd are required for far25 (25.335 is not implemented in this module)")
        Vc_min = Vd_min = float("nan")
    else:
        Vc_min = vc_factor(WS_psf, category) * math.sqrt(WS_psf) * KT
        if VH is not None:
            Vc_min = min(Vc_min, 0.9 * VH)
        use_Vc = Vc if Vc is not None else Vc_min
        Vd_min = max(1.25 * use_Vc, vd_factor(WS_psf, category) * Vc_min)
    Vc = Vc if Vc is not None else Vc_min
    Vd = Vd if Vd is not None else Vd_min
    if Vd <= Vc:
        raise ValueError("V_D must be greater than V_C")
    VA = min(VS * math.sqrt(n_poz), Vc)
    return {"VS": VS, "VA": VA, "VC": Vc, "VD": Vd, "VC_min": Vc_min, "VD_min": Vd_min,
            "WS": WS, "WS_psf": WS_psf,
            "suitable_VC": not (Vc < Vc_min * (1 - 1e-12)),
            "suitable_VD": not (Vd < Vd_min * (1 - 1e-12))}


# --- 23.341 / 23.333(c): gust ---
@cite("cfr14_part23", note="§23.333(c)(1)")
def ude_far23(h: float, speed: str = "VC") -> float:
    """Derived gust velocity U_de per 14 CFR 23.333(c)(1).

    Parameters
    ----------
    h : float
        Altitude [m], 0-50 000 ft.
    speed : {"VC", "VD", "VB"}, optional
        Design speed the gust applies to (``"VB"`` for the commuter category).

    Returns
    -------
    float
        U_de [m/s EAS].

    Raises
    ------
    ValueError
        If ``speed`` is not one of the options or ``h`` is outside 0-50 000 ft.

    Notes
    -----
    V_C: 50 ft/s up to 20 000 ft, decreasing linearly to 25 ft/s at 50 000 ft;
    V_D: 25 -> 12.5 ft/s; V_B (commuter): 66 -> 38 ft/s.
    """
    value = {"VC": (50.0, 25.0), "VD": (25.0, 12.5), "VB": (66.0, 38.0)}
    if speed not in value:
        raise ValueError("speed must be 'VC', 'VD' or 'VB'")
    h_ft = h / FT
    if h_ft < 0 or h_ft > 50000:
        raise ValueError("23.333(c) is written for 0-50 000 ft")
    u0, u1 = value[speed]
    if h_ft <= 20000:
        u = u0
    else:
        u = u0 + (u1 - u0) * (h_ft - 20000) / 30000
    return u * FT


@cite("cfr14_part23", note="§23.341(c)")
def mass_ratio_mu(W: float, S: float, c_avg: float, CLa: float, h: float = 0.0) -> float:
    """Airplane mass ratio mu_g of the gust formula.

    Parameters
    ----------
    W : float
        Weight [N].
    S : float
        Wing area [m^2].
    c_avg : float
        Mean geometric chord [m].
    CLa : float
        Lift-curve slope [1/rad].
    h : float, optional
        Altitude [m] (density from ISA).

    Returns
    -------
    float
        mu_g = 2 (W/S) / (rho c_avg a g) [-] (dimensionless, identical in every unit system).
    """
    rho = isa(h)["rho"]
    return 2 * (W / S) / (rho * c_avg * CLa * 9.80665)


@cite("cfr14_part23", note="§23.341(c)")
def kg_reduction(mu_g: float) -> float:
    """Gust alleviation factor.

    Parameters
    ----------
    mu_g : float
        Airplane mass ratio [-], > 0.

    Returns
    -------
    float
        K_g = 0.88 mu_g / (5.3 + mu_g) [-].

    Raises
    ------
    ValueError
        If ``mu_g <= 0``.

    Examples
    --------
    >>> kg_reduction(5.3)
    0.44
    """
    if mu_g <= 0:
        raise ValueError("mu_g must be positive")
    return 0.88 * mu_g / (5.3 + mu_g)


@cite("cfr14_part23", note="§23.341(c)")
def wind_load_factor(V_eas: float, Ude: float, W: float, S: float, c_avg: float, CLa: float,
                     h: float = 0.0) -> dict[str, float]:
    """Gust load factor per 14 CFR 23.341(c).

    Parameters
    ----------
    V_eas : float
        Airspeed [m/s EAS].
    Ude : float
        Derived gust velocity [m/s EAS].
    W : float
        Weight [N].
    S : float
        Wing area [m^2].
    c_avg : float
        Mean geometric chord [m].
    CLa : float
        Wing (or airplane normal-force) lift-curve slope a [1/rad].
    h : float, optional
        Altitude [m] for the mass ratio.

    Returns
    -------
    dict[str, float]
        ``n_plus`` = 1 + dn and ``n_minus`` = 1 - dn [-], ``dn`` gust increment [-],
        ``mu_g`` mass ratio [-], ``Kg`` gust alleviation factor [-].

    Raises
    ------
    ValueError
        If W, S, c_avg or CLa is not positive.

    Notes
    -----
    n = 1 +/- K_g U_de V a / (498 (W/S)), with V in knots EAS, U_de in ft/s and W/S in psf.
    """
    if min(W, S, c_avg, CLa) <= 0:
        raise ValueError("W, S, c_avg and CLa must be positive")
    mu = mass_ratio_mu(W, S, c_avg, CLa, h)
    Kg = kg_reduction(mu)
    dn = Kg * (Ude / FT) * (V_eas / KT) * CLa / (498.0 * (W / S) / PSF)
    return {"n_plus": 1 + dn, "n_minus": 1 - dn, "dn": dn, "mu_g": mu, "Kg": Kg}


# --- V-n diagram ---
@cite("cfr14_part23", "cfr14_part25", note="§23.333, 23.335, 23.337, 23.341; §25.337")
def vn_diagram(W: float, S: float, c_avg: float, CLmax: float, CLa: float, h: float = 0.0,
               category: str = "normal", CLmax_neg: float | None = None, Vc: float | None = None,
               Vd: float | None = None, VH: float | None = None, n_poz: float | None = None,
               n_neg: float | None = None, n_point: int = 301) -> dict[str, Any]:
    """Combined maneuver and gust V-n envelope (14 CFR 23.333, 23.335, 23.337, 23.341).

    Parameters
    ----------
    W : float
        Design weight [N].
    S : float
        Wing area [m^2].
    c_avg : float
        Mean geometric chord [m].
    CLmax : float
        Positive maximum lift coefficient [-].
    CLa : float
        Lift-curve slope [1/rad].
    h : float, optional
        Altitude for the gust velocity and mass ratio [m].
    category : {"normal", "utility", "acrobatic", "commuter", "far25"}, optional
        Certification category.
    CLmax_neg : float, optional
        Negative maximum lift coefficient (sign ignored); default |CLmax_neg| = CLmax.
    Vc, Vd, VH : float, optional
        Design cruising / dive / maximum level speeds [m/s EAS], see :func:`design_speeds`.
    n_poz, n_neg : float, optional
        Limit load factors; default from :func:`n_maneuver`.
    n_point : int, optional
        Number of speed samples (the corner speeds are added).

    Returns
    -------
    dict[str, Any]
        ``speeds`` (dict from :func:`design_speeds`), ``n_poz``, ``n_neg``, ``category``,
        ``V`` speed samples [m/s EAS], ``n_maneuver_upper``/``n_maneuver_lower``,
        ``n_wind_upper``/``n_wind_lower`` (gust lines, None for far25),
        ``n_envelope_upper``/``n_envelope_lower`` (combined envelope) [-] arrays,
        ``n_max``, ``V_n_max``, ``n_min``, ``V_n_min`` envelope extremes,
        ``critical`` (``"gust"`` or ``"maneuver"``), ``wind_C``/``wind_D`` gust results at V_C and
        V_D (dicts from :func:`wind_load_factor`, None for far25), ``VB`` commuter gust speed
        [m/s] or None, ``points`` (list of dicts ``name``, ``V`` [m/s], ``V_kt`` [knot], ``n``,
        ``source``) and ``assumptions`` (list of str).

    Raises
    ------
    ValueError
        Propagated from :func:`n_maneuver` and :func:`design_speeds`.

    Notes
    -----
    Maneuver envelope: positive edge min(rho0 V^2 CLmax / (2 W/S), n_poz) for V <= V_D. Negative
    edge max(-rho0 V^2 |CLmax_neg| / (2 W/S), n_neg) up to V_C; between V_C and V_D linear to 0
    (normal/commuter/far25) or to -1 (utility/acrobatic) (23.333(b)(3), 25.337(c)).
    Gust lines: from (0, 1) to the 50 ft/s point at V_C, linear between V_C and V_D
    (23.333(c)(2)(ii)); for commuter also 66 ft/s at V_B. No gust lines for far25 (25.341(a)(1)
    requires a dynamic analysis).

    ASSUMPTIONS (also listed in the returned ``assumptions``):

    - Without CLmax_neg, |CLmax_neg| = CLmax (symmetric airfoil); the negative stall line uses it.
    - In the combined envelope the gust line is bounded by the positive/negative CLmax line
      (common practice; the regulation states "limited by CLmax" only for maneuvers).
    - V_B (commuter): the smaller of the intersection of the CN_max line with the 66 ft/s gust line
      and V_S1 sqrt(n_g), not exceeding V_C (23.335(d)).
    """
    _category(category)
    n_p, n_n = n_maneuver(W, category)
    n_poz = n_p if n_poz is None else n_poz
    n_neg = n_n if n_neg is None else n_neg
    assumptions = []
    if CLmax_neg is None:
        CLmax_neg = CLmax
        assumptions.append("|CLmax_neg| = CLmax assumed (symmetric airfoil)")
    CLmax_neg = abs(CLmax_neg)
    speeds = design_speeds(W, S, CLmax, n_poz, category, Vc, Vd, VH)
    VS, VA, VC, VD = speeds["VS"], speeds["VA"], speeds["VC"], speeds["VD"]
    rho0 = isa(0)["rho"]
    WS = W / S

    def stall_pos(V: Any) -> np.ndarray:
        return rho0 * np.asarray(V) ** 2 * CLmax / (2 * WS)

    def stall_neg(V: Any) -> np.ndarray:
        return -rho0 * np.asarray(V) ** 2 * CLmax_neg / (2 * WS)

    n_D_neg = -1.0 if category in ("utility", "acrobatic") else 0.0

    def man_upper(V: Any) -> np.ndarray:
        return np.minimum(stall_pos(V), n_poz)

    def man_lower(V: Any) -> np.ndarray:
        V = np.asarray(V, dtype=float)
        flat = np.where(V <= VC, n_neg, n_neg + (n_D_neg - n_neg) * (V - VC) / (VD - VC))
        return np.maximum(stall_neg(V), flat)

    gust = category != "far25"
    VB = None
    if gust:
        gC = wind_load_factor(VC, ude_far23(h, "VC"), W, S, c_avg, CLa, h)
        gD = wind_load_factor(VD, ude_far23(h, "VD"), W, S, c_avg, CLa, h)
        dnC, dnD = gC["dn"], gD["dn"]
        if category == "commuter":
            dnB_per_V = wind_load_factor(1.0, ude_far23(h, "VB"), W, S, c_avg, CLa, h)["dn"]  # per 1 m/s
            # intersection: rho0 V^2 CLmax / (2 W/S) = 1 + dnB_per_V V  -> positive root
            a_, b_, c_ = rho0 * CLmax / (2 * WS), -dnB_per_V, -1.0
            V_cross = (-b_ + math.sqrt(b_ ** 2 - 4 * a_ * c_)) / (2 * a_)
            VB = min(min(V_cross, VS * math.sqrt(gC["n_plus"])), VC)
            dnB = dnB_per_V * VB
            assumptions.append("V_B computed per 23.335(d) (V_S1 = V_S assumed)")

        def gust_dn(V: Any) -> np.ndarray:
            V = np.asarray(V, dtype=float)
            dn = np.where(V <= VC, dnC * V / VC, dnC + (dnD - dnC) * (V - VC) / (VD - VC))
            if VB is not None:
                dn = np.maximum(dn, np.where(V <= VB, dnB * V / VB,
                                             np.where(V <= VC, dnB + (dnC - dnB) * (V - VB) / (VC - VB), 0)))
            return dn
        assumptions.append("gust line bounded by the CLmax (stall) line in the combined envelope")

    V = np.linspace(0.0, VD, n_point)
    V = np.unique(np.concatenate([V, [VS, VA, VC, VD]]))
    m_upper, m_lower = man_upper(V), man_lower(V)
    g_upper: np.ndarray | None
    g_lower: np.ndarray | None
    if gust:
        g_upper, g_lower = 1 + gust_dn(V), 1 - gust_dn(V)
        e_upper = np.maximum(m_upper, np.minimum(g_upper, stall_pos(V)))
        e_lower = np.minimum(m_lower, np.maximum(g_lower, stall_neg(V)))
    else:
        g_upper = g_lower = None
        e_upper, e_lower = m_upper, m_lower

    def point(name: str, Vn: float, n: float, source: str) -> dict[str, Any]:
        return {"name": name, "V": float(Vn), "V_kt": float(Vn / KT), "n": float(n), "source": source}

    VS_neg = math.sqrt(2 * WS * abs(n_neg) / (rho0 * CLmax_neg))
    points = [
        point("S (1g stall)", VS, 1.0, "V_S"),
        point("A (maneuver corner)", VA, float(man_upper(VA)), "23.335(c)"),
        point("C+ (maneuver)", VC, n_poz, "23.333(b)(1)"),
        point("D+ (maneuver)", VD, n_poz, "23.333(b)(1)"),
        point("D− (maneuver)", VD, n_D_neg, "23.333(b)(3)"),
        point("C− (maneuver)", VC, n_neg, "23.333(b)(2)"),
        point("G (negative stall corner)", min(VS_neg, VC), float(man_lower(min(VS_neg, VC))), "negative CLmax"),
    ]
    if gust:
        points += [
            point("C+ gust", VC, 1 + dnC, "23.341, U_de(V_C)"),
            point("C− gust", VC, 1 - dnC, "23.341, U_de(V_C)"),
            point("D+ gust", VD, 1 + dnD, "23.341, U_de(V_D)"),
            point("D− gust", VD, 1 - dnD, "23.341, U_de(V_D)"),
        ]
        if VB is not None:
            points += [point("B+ gust", VB, 1 + dnB, "23.333(c)(1)(iii)"),
                       point("B− gust", VB, 1 - dnB, "23.333(c)(1)(iii)")]
    i_max, i_min = int(np.argmax(e_upper)), int(np.argmin(e_lower))
    return {
        "speeds": speeds, "n_poz": n_poz, "n_neg": n_neg, "category": category,
        "V": V, "n_maneuver_upper": m_upper, "n_maneuver_lower": m_lower,
        "n_wind_upper": g_upper, "n_wind_lower": g_lower, "n_envelope_upper": e_upper, "n_envelope_lower": e_lower,
        "n_max": float(e_upper[i_max]), "V_n_max": float(V[i_max]),
        "n_min": float(e_lower[i_min]), "V_n_min": float(V[i_min]),
        "critical": "gust" if gust and e_upper[i_max] > n_poz + 1e-12 else "maneuver",
        "wind_C": gC if gust else None, "wind_D": gD if gust else None,
        "VB": VB,
        "points": points, "assumptions": assumptions,
    }


@cite("cfr14_part23", note="§23.303 factor of safety 1.5")
def root_bending(W: float, b: float, c_root: float, c_tip: float, envelope: dict[str, Any], FS: float = 1.5,
                 distribution: str = "schrenk") -> dict[str, Any]:
    """Half-wing root shear and bending moment at the largest |n| of a V-n envelope.

    Parameters
    ----------
    W : float
        Design weight [N].
    b : float
        Span [m].
    c_root, c_tip : float
        Root and tip chords [m].
    envelope : dict
        Result of :func:`vn_diagram` (``n_max`` and ``n_min`` are used).
    FS : float, optional
        Factor of safety (14 CFR 23.303: 1.5).
    distribution : {"schrenk", "ellipse", "trapezoid"}, optional
        Spanwise lift distribution, see :func:`aerokit.aero.wing.span_loads`.

    Returns
    -------
    dict[str, Any]
        ``n`` design load factor [-], ``V_root``/``M_root`` limit root shear [N] and moment [N m],
        ``V_root_ultimate``/``M_root_ultimate`` ultimate values (x FS), ``distribution`` the full
        result of :func:`aerokit.aero.wing.span_loads`.

    Notes
    -----
    No bending relief from the wing weight (conservative).
    """
    n = max(envelope["n_max"], abs(envelope["n_min"]))
    y = wing.span_loads(W, n, b, c_root, c_tip, distribution=distribution)
    return {"n": n, "V_root": float(y["V"][0]), "M_root": float(y["M"][0]),
            "V_root_ultimate": FS * float(y["V"][0]), "M_root_ultimate": FS * float(y["M"][0]),
            "distribution": y}


# --- 25.341(a): discrete gust (design gust velocity only; loads need a dynamic analysis) ---
@cite("cfr14_part25", note="§25.341(a)(3)-(6)")
def discrete_wind_far25(H: float, h: float, Zmo: float, R1: float, R2: float, speed: str = "VC") -> dict[str, float]:
    """Design discrete-gust velocity per 14 CFR 25.341(a)(4)-(6).

    Parameters
    ----------
    H : float
        Gust gradient distance [m] (30-350 ft).
    h : float
        Altitude [m] (0-50 000 ft).
    Zmo : float
        Maximum operating altitude [m].
    R1 : float
        Maximum landing weight / maximum takeoff weight, in (0, 1].
    R2 : float
        Maximum zero-fuel weight / maximum takeoff weight, in (0, 1].
    speed : {"VC", "VD"}, optional
        Design speed; at V_D the reference gust velocity is halved.

    Returns
    -------
    dict[str, float]
        ``Uds`` design gust velocity [m/s EAS], ``Uref`` reference gust velocity [m/s EAS],
        ``Fg`` flight profile alleviation factor at ``h`` [-], ``Fg_sea`` its sea-level value,
        ``Fgz``, ``Fgm`` [-].

    Raises
    ------
    ValueError
        If H, h, R1, R2 or ``speed`` is out of range.

    Notes
    -----
    U_ds = U_ref F_g (H/350)^(1/6). U_ref (V_C): 56 ft/s at sea level -> 44 at 15 000 ft -> 26 at
    50 000 ft, linear; half of that at V_D. F_g = 0.5 (F_gz + F_gm), F_gz = 1 - Zmo/250 000 (ft),
    F_gm = sqrt(R2 tan(pi R1 / 4)); F_g increases linearly from its sea-level value to 1.0 at Zmo.
    The loads themselves require a dynamic analysis (25.341(a)(1)) and are not computed here.
    """
    H_ft, h_ft, Z_ft = H / FT, h / FT, Zmo / FT
    if not 30 - 1e-9 <= H_ft <= 350 + 1e-9:
        raise ValueError("25.341(a)(3): H must be within 30-350 ft")
    if not 0 <= h_ft <= 50000:
        raise ValueError("altitude must be within 0-50 000 ft")
    if not (0 < R1 <= 1 and 0 < R2 <= 1):
        raise ValueError("R1 and R2 must be in (0, 1]")
    if h_ft <= 15000:
        Uref = 56.0 + (44.0 - 56.0) * h_ft / 15000
    else:
        Uref = 44.0 + (26.0 - 44.0) * (h_ft - 15000) / 35000
    if speed == "VD":
        Uref *= 0.5
    elif speed != "VC":
        raise ValueError("speed must be 'VC' or 'VD'")
    Fgz = 1 - Z_ft / 250000
    Fgm = math.sqrt(R2 * math.tan(math.pi * R1 / 4))
    Fg0 = 0.5 * (Fgz + Fgm)
    Fg = Fg0 + (1.0 - Fg0) * min(h_ft / Z_ft, 1.0) if Z_ft > 0 else 1.0
    Uds = Uref * Fg * (H_ft / 350.0) ** (1 / 6)
    return {"Uds": Uds * FT, "Uref": Uref * FT, "Fg": Fg, "Fg_sea": Fg0, "Fgz": Fgz, "Fgm": Fgm}


# --- 23.473 / 23.725: landing ---
@cite("cfr14_part23", note="§23.473(d), (e), (g); §23.725(a)")
def landing_loads(W: float, S: float, stroke: float | None = None, efficiency: float = 0.7,
                  lift_ratio: float = 2 / 3) -> dict[str, float]:
    """Quick estimate of landing loads.

    Parameters
    ----------
    W : float
        Design landing weight [N].
    S : float
        Wing area [m^2].
    stroke : float, optional
        Shock-absorber stroke [m]; if given, an energy-based load factor is added.
    efficiency : float, optional
        Shock-absorber efficiency eta, 0 < eta <= 1 [-] (0.7 is an ASSUMPTION, typical of an oleo
        strut, not verified against a source; supply your own value).
    lift_ratio : float, optional
        Wing lift at touchdown as a fraction of W, 0 <= L <= 2/3 [-].

    Returns
    -------
    dict[str, float]
        ``V_sink`` design descent velocity [m/s], ``V_sink_ft_s`` [ft/s], ``drop_height`` free drop
        height [m], ``drop_height_in`` [in], ``n_inertia_min`` 2.67, ``n_ground_min`` 2.0,
        ``lift_ratio``; with ``stroke`` also ``N_ground_energy``, ``n_inertia_energy`` (energy
        estimate) and ``n_inertia_design``, ``N_ground_design`` (energy estimate but not below
        the regulatory minima) [-].

    Raises
    ------
    ValueError
        If W or S is not positive, ``lift_ratio`` is outside [0, 2/3], or ``stroke``/``efficiency``
        is out of range.

    Notes
    -----
    Regulation (14 CFR 23.473(d), (e), (g); 23.725(a)):

    - Design descent velocity V = 4.4 (W/S)^(1/4) ft/s (W/S in psf), 7 <= V <= 10 ft/s.
    - Wing lift up to 2/3 W may be assumed; ground reaction factor = inertia factor - L/W.
    - Inertia load factor >= 2.67 and ground reaction factor >= 2.0 (unless shown otherwise).
    - Free drop height h = 3.6 sqrt(W/S) in, 9.2 <= h <= 18.7 in.

    Energy estimate (DERIVATION, not regulation), stroke s and efficiency eta:
    (1/2)(W/g) V^2 + (1 - L) W s = eta N_ground W s  =>  N_ground = (V^2/(2 g s) + 1 - L)/eta,
    n_inertia = N_ground + L.
    """
    if W <= 0 or S <= 0:
        raise ValueError("W and S must be positive")
    if not 0 <= lift_ratio <= 2 / 3 + 1e-12:
        raise ValueError("23.473(e): lift ratio must be between 0 and 2/3")
    WS_psf = W / S / PSF
    V_ft = min(max(4.4 * WS_psf ** 0.25, 7.0), 10.0)
    h_in = min(max(3.6 * math.sqrt(WS_psf), 9.2), 18.7)
    result = {"V_sink": V_ft * FT, "V_sink_ft_s": V_ft, "drop_height": h_in * 0.0254,
              "drop_height_in": h_in, "n_inertia_min": 2.67, "n_ground_min": 2.0,
              "lift_ratio": lift_ratio}
    if stroke is not None:
        if stroke <= 0 or not 0 < efficiency <= 1:
            raise ValueError("stroke > 0 and 0 < efficiency <= 1 required")
        V = V_ft * FT
        N_ground = (V ** 2 / (2 * 9.80665 * stroke) + 1 - lift_ratio) / efficiency
        n_inertia = N_ground + lift_ratio
        result.update({"N_ground_energy": N_ground, "n_inertia_energy": n_inertia,
                       "n_inertia_design": max(n_inertia, 2.67), "N_ground_design": max(N_ground, 2.0)})
    return result
