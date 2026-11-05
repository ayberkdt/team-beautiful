"""Longitudinal static stability and tail sizing (conceptual design).

Sources (read 2026-10-25):

- Lift-curve slope, DATCOM (Helmbold) form:
  CL_alpha = 2 pi A / (2 + sqrt(4 + A^2 beta^2/kappa^2 (1 + tan^2 Lambda_c/2 / beta^2))),
  kappa = cl_alpha/(2 pi), beta^2 = 1 - M^2. Virginia Tech AOE 3104 (Lutze) Problem Sheet 5 answer
  key (2003), MATLAB "liftcurve" and its numerical tables; the sweep conversion
  tan Lambda_n = tan Lambda_m - (4/A)(n - m)(1 - lambda)/(1 + lambda) was checked against the
  24.997 deg value of the Problem Sheet 4 answer of the same course.
- Downwash gradient d(eps)/d(alpha) ~ 2 CL_alpha,w/(pi A) (elliptic loading), tail contribution,
  stick-fixed neutral point
  h_NP = (CL_alpha,w h_ac + eta (St/S) CL_alpha,t (1 - d eps/d alpha) h_t)/CL_alpha,T,
  CM_alpha = CL_alpha,T (h - h_NP): MIT 16.333 (J. How, Fall 2004) Lecture 2, pp. 2-6 ... 2-10.
- Tail volume coefficients: Raymer (1992) Table 6.4 values, taken from the "Raymer" column of
  Scholz/HAW Hamburg AERO_TN_TailSizing_13-04-15, Table 2.3 (horizontal) and Table 2.4
  (vertical), pp. 51-52. Definitions (same report, Eqs. 2.6-2.7): C_H = S_H l_H/(S_W c_MAC),
  C_V = S_V l_V/(S_W b_W).

Positions are in MAC units, measured from the leading edge of the wing MAC (h = x/c_bar).
"""
from __future__ import annotations

import math
from typing import Any

from scipy.optimize import brentq

from aerokit.references import cite

# Raymer 1992 Table 6.4 (via Scholz TN 2013 Table 2.3/2.4): (C_HT, C_VT).
# Keys use the aircraft-type vocabulary of aerokit.aero.sizing.EMPTY_WEIGHT.
TAIL_VOLUME = {
    "sailplane": (0.50, 0.020),
    "homebuilt": (0.50, 0.040),
    "GA single engine": (0.70, 0.040),
    "GA twin engine": (0.80, 0.070),
    "twin turboprop": (0.90, 0.080),       # "Regional Turboprop" row of the Scholz table
    "jet transport": (1.00, 0.090),
    "jet trainer": (0.70, 0.060),
    "jet fighter": (0.40, 0.070),
    "military transport": (1.00, 0.080),
    "agricultural": (0.50, 0.040),
    "flying boat": (0.70, 0.060),          # "Flying Boat"
}


@cite("raymer_1992", "scholz_2013", note="Raymer Table 6.4, via Scholz TN Tables 2.3/2.4 (pp. 51-52)")
def tail_volume(kind: str) -> tuple[float, float]:
    """Typical horizontal and vertical tail volume coefficients for an aircraft type.

    Parameters
    ----------
    kind : str
        Aircraft type, a key of :data:`TAIL_VOLUME` (e.g. ``"GA single engine"``).

    Returns
    -------
    C_HT : float
        Horizontal tail volume coefficient [-].
    C_VT : float
        Vertical tail volume coefficient [-].

    Raises
    ------
    KeyError
        If ``kind`` is unknown; the message lists the valid keys.

    Examples
    --------
    >>> tail_volume("GA single engine")
    (0.7, 0.04)
    """
    if kind not in TAIL_VOLUME:
        raise KeyError(f"unknown aircraft type '{kind}'; options: {', '.join(TAIL_VOLUME)}")
    return TAIL_VOLUME[kind]


# --- aerodynamics ---
@cite("lutze_2003", note="sweep conversion, checked against the Problem Sheet 4 answer (24.997 deg)")
def transform_sweep(Lambda_m: float, A: float, taper: float, m: float, n: float) -> float:
    """Convert the sweep angle of the chord fraction ``m`` line to that of the ``n`` line.

    Parameters
    ----------
    Lambda_m : float
        Sweep of the m-chord line [deg].
    A : float
        Aspect ratio [-].
    taper : float
        Taper ratio lambda [-].
    m, n : float
        Chord fractions (0 = leading edge, 0.25 = quarter chord, 0.5 = half chord, ...).

    Returns
    -------
    float
        Sweep of the n-chord line [deg].

    Raises
    ------
    ValueError
        If ``A <= 0``.

    Notes
    -----
    tan Lambda_n = tan Lambda_m - (4/A)(n - m)(1 - lambda)/(1 + lambda).
    """
    if A <= 0:
        raise ValueError("aspect ratio must be positive")
    t = math.tan(math.radians(Lambda_m)) - 4.0 / A * (n - m) * (1 - taper) / (1 + taper)
    return math.degrees(math.atan(t))


@cite("lutze_2003", note="DATCOM (Helmbold) form, Problem Sheet 5 answer key and 'liftcurve' tables")
def CLa_datcom(A: float, Lambda_c2: float = 0.0, M: float = 0.0, cla: float = 2 * math.pi) -> float:
    """Finite-wing lift-curve slope, DATCOM/Helmbold form (subsonic, M < 1).

    Parameters
    ----------
    A : float
        Aspect ratio [-].
    Lambda_c2 : float, optional
        Half-chord sweep [deg].
    M : float, optional
        Mach number, 0 <= M < 1 [-].
    cla : float, optional
        Two-dimensional airfoil lift-curve slope [1/rad].

    Returns
    -------
    float
        CL_alpha [1/rad].

    Raises
    ------
    ValueError
        If ``A <= 0`` or ``cla <= 0``, or if ``M`` is outside [0, 1).

    Notes
    -----
    CL_alpha = 2 pi A / (2 + sqrt(A^2 beta^2/kappa^2 (1 + tan^2 Lambda_c/2 / beta^2) + 4)),
    beta^2 = 1 - M^2, kappa = cla/(2 pi).

    Examples
    --------
    >>> round(CLa_datcom(4, 45, 0.0), 4)
    3.1416
    """
    if A <= 0 or cla <= 0:
        raise ValueError("A and cla must be positive")
    if not 0 <= M < 1:
        raise ValueError("the relation is valid for subsonic flow only (0 <= M < 1)")
    b2 = 1 - M ** 2
    k = cla / (2 * math.pi)
    t2 = math.tan(math.radians(Lambda_c2)) ** 2
    return 2 * math.pi * A / (2 + math.sqrt(A ** 2 * b2 / k ** 2 * (1 + t2 / b2) + 4))


@cite("how_2004", note="Lecture 2, p. 2-6")
def downwash_gradient(CLa_w: float, A: float) -> float:
    """Downwash gradient at the tail for an elliptically loaded wing.

    Parameters
    ----------
    CLa_w : float
        Wing lift-curve slope [1/rad].
    A : float
        Wing aspect ratio [-].

    Returns
    -------
    float
        d(eps)/d(alpha) ~ 2 CL_alpha,w / (pi A) [-]. No tail-position effect: a rough estimate.

    Raises
    ------
    ValueError
        If ``A <= 0``.
    """
    if A <= 0:
        raise ValueError("aspect ratio must be positive")
    return 2 * CLa_w / (math.pi * A)


# --- tail volume ---
@cite("scholz_2013", note="Eq. 2.7")
def horizontal_volume_coefficient(S_h: float, l_h: float, S_w: float, c_mac: float) -> float:
    """Horizontal tail volume coefficient.

    Parameters
    ----------
    S_h : float
        Horizontal tail area [m^2].
    l_h : float
        Tail arm (wing to tail aerodynamic centre) [m].
    S_w : float
        Wing reference area [m^2].
    c_mac : float
        Wing mean aerodynamic chord [m].

    Returns
    -------
    float
        C_HT = S_h l_h / (S_w c_mac) [-].
    """
    return S_h * l_h / (S_w * c_mac)


@cite("scholz_2013", note="Eq. 2.6")
def vertical_volume_coefficient(S_v: float, l_v: float, S_w: float, b: float) -> float:
    """Vertical tail volume coefficient.

    Parameters
    ----------
    S_v : float
        Vertical tail area [m^2].
    l_v : float
        Tail arm [m].
    S_w : float
        Wing reference area [m^2].
    b : float
        Wing span [m].

    Returns
    -------
    float
        C_VT = S_v l_v / (S_w b) [-].
    """
    return S_v * l_v / (S_w * b)


@cite("scholz_2013", note="Eq. 2.7 solved for the tail area")
def horizontal_tail_area(C_HT: float, l_h: float, S_w: float, c_mac: float) -> float:
    """Horizontal tail area for a given volume coefficient.

    Parameters
    ----------
    C_HT : float
        Horizontal tail volume coefficient [-].
    l_h : float
        Tail arm [m], > 0.
    S_w : float
        Wing reference area [m^2].
    c_mac : float
        Wing mean aerodynamic chord [m].

    Returns
    -------
    float
        S_H = C_HT c_mac S_W / l_H [m^2].

    Raises
    ------
    ValueError
        If ``l_h <= 0``.
    """
    if l_h <= 0:
        raise ValueError("tail arm must be positive")
    return C_HT * c_mac * S_w / l_h


@cite("scholz_2013", note="Eq. 2.6 solved for the tail area")
def vertical_tail_area(C_VT: float, l_v: float, S_w: float, b: float) -> float:
    """Vertical tail area for a given volume coefficient.

    Parameters
    ----------
    C_VT : float
        Vertical tail volume coefficient [-].
    l_v : float
        Tail arm [m], > 0.
    S_w : float
        Wing reference area [m^2].
    b : float
        Wing span [m].

    Returns
    -------
    float
        S_V = C_VT b S_W / l_V [m^2].

    Raises
    ------
    ValueError
        If ``l_v <= 0``.
    """
    if l_v <= 0:
        raise ValueError("tail arm must be positive")
    return C_VT * b * S_w / l_v


# --- neutral point, static margin, trim ---
@cite("how_2004", note="Lecture 2, pp. 2-6 to 2-10")
def neutral_point(h_ac: float, CLa_w: float, CLa_t: float, St_S: float, h_t: float, deda: float,
                  eta: float = 1.0, dCma_fuselage: float = 0.0) -> dict[str, float]:
    """Stick-fixed neutral point of a wing-tail configuration.

    Parameters
    ----------
    h_ac : float
        Wing aerodynamic centre [MAC fraction from the MAC leading edge].
    CLa_w, CLa_t : float
        Wing and tail lift-curve slopes [1/rad]; ``CLa_w > 0``.
    St_S : float
        Tail-to-wing area ratio S_t/S [-], >= 0.
    h_t : float
        Tail aerodynamic centre [MAC fraction from the wing MAC leading edge].
    deda : float
        Downwash gradient d(eps)/d(alpha), 0 <= deda < 1 [-].
    eta : float, optional
        Tail dynamic-pressure ratio [-].
    dCma_fuselage : float, optional
        Fuselage/nacelle contribution Delta CM_alpha [1/rad] (positive = destabilizing); it moves
        h_NP forward by Delta CM_alpha / CL_alpha,T (from CM_alpha = CL_alpha,T (h - h_NP) + Delta CM_alpha).

    Returns
    -------
    dict[str, float]
        ``h_np`` neutral point [MAC fraction], ``CLa_T`` total lift-curve slope [1/rad],
        ``tail_term`` eta (St/S) CL_alpha,t (1 - d eps/d alpha) [1/rad].

    Raises
    ------
    ValueError
        If ``CLa_w <= 0``, ``St_S < 0`` or ``deda`` is outside [0, 1).

    Notes
    -----
    CL_alpha,T = CL_alpha,w + eta (St/S) CL_alpha,t (1 - d eps/d alpha),
    h_NP = (CL_alpha,w h_ac + eta (St/S) CL_alpha,t (1 - d eps/d alpha) h_t) / CL_alpha,T.
    """
    if CLa_w <= 0:
        raise ValueError("CLa_w must be positive")
    if St_S < 0 or not 0 <= deda < 1:
        raise ValueError("St/S >= 0 and 0 <= d(eps)/d(alpha) < 1 required")
    tail = eta * St_S * CLa_t * (1 - deda)
    CLaT = CLa_w + tail
    h_np = (CLa_w * h_ac + tail * h_t) / CLaT - dCma_fuselage / CLaT
    return {"h_np": h_np, "CLa_T": CLaT, "tail_term": tail}


@cite("how_2004", note="Lecture 2, pp. 2-8 to 2-9")
def static_margin(h_cg: float, h_np: float, CLa_T: float | None = None) -> dict[str, Any]:
    """Static margin and, optionally, the pitch-stiffness derivative.

    Parameters
    ----------
    h_cg : float
        Centre-of-gravity position [MAC fraction].
    h_np : float
        Neutral point [MAC fraction].
    CLa_T : float, optional
        Total lift-curve slope [1/rad]; if given, CM_alpha is returned too.

    Returns
    -------
    dict[str, Any]
        ``SM`` static margin h_NP - h_cg [MAC fraction], ``stable`` True if SM > 0,
        ``Cma`` (only if ``CLa_T`` is given) CM_alpha = -CL_alpha,T SM [1/rad].
    """
    sm = h_np - h_cg
    result: dict[str, Any] = {"SM": sm, "stable": sm > 0}
    if CLa_T is not None:
        result["Cma"] = -CLa_T * sm
    return result


@cite("how_2004", note="Lecture 2 terms; linear force and moment balance")
def trim(CL: float, Cm_ac: float, h_cg: float, h_ac: float, St_S: float, h_t: float, eta: float = 1.0,
         CLt_max: float | None = None, CLw_max: float | None = None) -> dict[str, Any]:
    """Trimmed sharing of lift between wing and tail.

    Parameters
    ----------
    CL : float
        Required total lift coefficient [-].
    Cm_ac : float
        Wing pitching-moment coefficient about its aerodynamic centre [-].
    h_cg, h_ac, h_t : float
        CG, wing aerodynamic centre and tail aerodynamic centre [MAC fractions].
    St_S : float
        Tail-to-wing area ratio [-], > 0.
    eta : float, optional
        Tail dynamic-pressure ratio [-].
    CLt_max : float, optional
        Tail lift-coefficient limit |CL_t| <= CLt_max.
    CLw_max : float, optional
        Wing lift-coefficient limit CL_w <= CLw_max.

    Returns
    -------
    dict[str, Any]
        ``CL_w`` wing and ``CL_t`` tail lift coefficients [-], ``V_H`` tail volume
        (St/S)(h_t - h_cg) [-], ``trim_possible`` False if a given limit is exceeded.

    Raises
    ------
    ValueError
        If the tail area or the tail arm is not positive (tail must be aft of the CG).

    Notes
    -----
    CL_w + eta (St/S) CL_t = CL;  Cm_ac + CL_w (h_cg - h_ac) - eta V_H CL_t = 0,
    V_H = (St/S)(h_t - h_cg).
    """
    VH = St_S * (h_t - h_cg)
    if St_S <= 0 or VH <= 0:
        raise ValueError("tail area and tail arm must be positive (tail aft of the centre of gravity)")
    # [1, eta St/S; (h - h_ac), -eta VH] [CLw, CLt] = [CL, -Cm_ac]
    a11, a12, a21, a22 = 1.0, eta * St_S, h_cg - h_ac, -eta * VH
    det = a11 * a22 - a12 * a21
    CLw = (CL * a22 - a12 * (-Cm_ac)) / det
    CLt = (a11 * (-Cm_ac) - a21 * CL) / det
    ok = True
    if CLt_max is not None and abs(CLt) > CLt_max:
        ok = False
    if CLw_max is not None and CLw > CLw_max:
        ok = False
    return {"CL_w": CLw, "CL_t": CLt, "V_H": VH, "trim_possible": ok}


def tail_size_sm(target_SM: float, h_cg: float, h_ac: float, CLa_w: float, CLa_t: float, h_t: float,
                 deda: float, eta: float = 1.0, dCma_fuselage: float = 0.0,
                 St_S_upper: float = 2.0) -> dict[str, Any]:
    """Tail-to-wing area ratio that gives a target static margin.

    Parameters
    ----------
    target_SM : float
        Required static margin [MAC fraction].
    h_cg, h_ac, h_t : float
        CG, wing aerodynamic centre and tail aerodynamic centre [MAC fractions].
    CLa_w, CLa_t : float
        Wing and tail lift-curve slopes [1/rad].
    deda : float
        Downwash gradient [-].
    eta : float, optional
        Tail dynamic-pressure ratio [-].
    dCma_fuselage : float, optional
        Fuselage contribution Delta CM_alpha [1/rad], see :func:`neutral_point`.
    St_S_upper : float, optional
        Upper end of the St/S search bracket [-].

    Returns
    -------
    dict[str, Any]
        ``St_S`` required area ratio [-], ``SM`` achieved static margin [MAC fraction];
        ``note`` (only if no tail is needed) explaining that the target is met without a tail.

    Raises
    ------
    ValueError
        If the target cannot be met within ``St_S_upper`` (tail arm too short or target too large).

    Notes
    -----
    The neutral point moves aft monotonically as the tail grows, so the root of
    h_NP(St/S) - h_cg - SM_target is bracketed and found with Brent's method.
    """
    def f(x: float) -> float:
        return neutral_point(h_ac, CLa_w, CLa_t, x, h_t, deda, eta, dCma_fuselage)["h_np"] - h_cg - target_SM
    if f(0.0) >= 0:
        return {"St_S": 0.0, "SM": f(0.0) + target_SM, "note": "target margin is met even without a tail"}
    if f(St_S_upper) < 0:
        raise ValueError("target margin cannot be reached within St_S_upper (tail arm too short or target too large)")
    x = brentq(f, 0.0, St_S_upper, xtol=1e-12)
    return {"St_S": x, "SM": f(x) + target_SM}
