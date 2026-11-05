"""Weight and balance: mass, centre of gravity, %MAC and inertia from a component list; loading
(CG) envelope; Raymer general-aviation (GA) statistical group weights.

Coordinates: x aft, y towards the right wing, z up [m]; mass [kg]. The inertia tensor about the
centre of gravity is J = sum m (|r|^2 I - r r^T) + sum J_own; the products of inertia are also
returned with the POSITIVE convention (Ixy = sum m x y, Ixz = sum m x z, flight-dynamics custom).

Raymer GA equations - SOURCE STATUS (2026-10-25):

- Raymer's book "Aircraft Design: A Conceptual Approach" was NOT read. The equations were read from
  two independent re-implementations: AeroSandbox ``raymer_general_aviation_weights.py`` (cites
  5th ed. Sec. 15.3.3) and SUAVE ``Methods/Weights/Correlations/General_Aviation/*.py`` (cites
  4th ed. pp. 460-461). Coefficients on which both agree are used; where they differ, the function
  docstring says so. Equation numbers (15.46-15.59) are FROM MEMORY, not verified.
- The equations are evaluated in their own units (lb, ft^2, ft, psf, US gallon, inch); the
  interface is SI.
"""
from __future__ import annotations

import itertools
import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np

from aerokit.aero import sizing
from aerokit.references import cite

LB_KG = 0.45359237              # 1 lb mass [kg]
LB_N = 4.4482216152605
FT = 0.3048
PSF = LB_N / FT ** 2
GAL = 3.785411784e-3            # 1 US gallon [m³]
INC = 0.0254                    # 1 inch [m]
PSI = LB_N / INC ** 2

# A component is either a mapping {"name", "m", "x", "y", "z"[, "J_own"]} or a tuple (name, m, x, y, z).
Component = Mapping[str, Any] | Sequence[Any]

_RAYMER_GA = ("raymer_2012", "raymer_2006", "sharpe_2021", "lukaczyk_2015")
_RAYMER_NOTE = ("Raymer GA group weights read via AeroSandbox (5th ed. Sec. 15.3.3) and SUAVE "
                "(4th ed. pp. 460-461); book not consulted")


# --- mass properties ---
def _component(b: Component) -> tuple[str, float, np.ndarray, np.ndarray]:
    """Normalize one component to (name, mass, position (3,), own inertia tensor (3, 3))."""
    if isinstance(b, Mapping):
        m = b["m"]
        x, y, z = b.get("x", 0.0), b.get("y", 0.0), b.get("z", 0.0)
        J = np.array(b["J_own"], float) if "J_own" in b else np.zeros((3, 3))
        if J.shape == (3,):
            J = np.diag(J)
        name = b.get("name", "")
    else:
        name, m, x, y, z = b[:5]
        J = np.zeros((3, 3))
    if m < 0:
        raise ValueError(f"negative mass: {name}")
    return name, float(m), np.array([x, y, z], float), J


def mass_properties(components: Iterable[Component]) -> dict[str, Any]:
    """Total mass, centre of gravity and inertia tensor of a set of components.

    Parameters
    ----------
    components : iterable
        Each item is a mapping ``{"name", "m", "x", "y", "z"[, "J_own"]}`` or a tuple
        ``(name, m, x, y, z)``; m [kg], x, y, z [m]. ``J_own`` is the component's inertia about its
        own CG [kg m^2], aligned with the body axes, as a 3x3 tensor or the diagonal
        ``(Ixx, Iyy, Izz)``.

    Returns
    -------
    dict[str, Any]
        ``m`` total mass [kg], ``cg`` (3,) CG position [m], ``J`` (3, 3) inertia tensor about the CG
        [kg m^2], ``J_origin`` (3, 3) tensor about the origin, ``Ixx``, ``Iyy``, ``Izz`` moments
        of inertia and ``Ixy``, ``Ixz``, ``Iyz`` products of inertia (positive convention) [kg m^2].

    Raises
    ------
    ValueError
        If the list is empty, a mass is negative, or the total mass is not positive.

    Examples
    --------
    >>> r = mass_properties([("a", 2.0, 0, -1.0, 0), ("b", 6.0, 0, 3.0, 0)])
    >>> float(r["Ixx"])
    24.0
    """
    entries = [_component(b) for b in components]
    if not entries:
        raise ValueError("component list is empty")
    m = sum(k[1] for k in entries)
    if m <= 0:
        raise ValueError("total mass must be positive")
    cg = np.asarray(sum(k[1] * k[2] for k in entries)) / m

    def tensor(center: np.ndarray) -> np.ndarray:
        J = np.zeros((3, 3))
        for _, mi, r, J_own in entries:
            d = r - center
            J += mi * (d @ d * np.eye(3) - np.outer(d, d)) + J_own
        return J
    J = tensor(cg)
    return {"m": m, "cg": cg, "J": J, "J_origin": tensor(np.zeros(3)),
            "Ixx": J[0, 0], "Iyy": J[1, 1], "Izz": J[2, 2],
            "Ixy": -J[0, 1], "Ixz": -J[0, 2], "Iyz": -J[1, 2]}


def cg_percent_mac(x_cg: float, x_lemac: float, mac: float) -> float:
    """Centre-of-gravity position in percent of the mean aerodynamic chord.

    Parameters
    ----------
    x_cg : float
        CG position [m].
    x_lemac : float
        Position of the MAC leading edge [m].
    mac : float
        Mean aerodynamic chord [m], > 0.

    Returns
    -------
    float
        %MAC = 100 (x_cg - x_LEMAC) / MAC.

    Raises
    ------
    ValueError
        If ``mac <= 0``.

    Examples
    --------
    >>> round(cg_percent_mac(2.3, 2.0, 1.2), 9)
    25.0
    """
    if mac <= 0:
        raise ValueError("MAC must be positive")
    return 100.0 * (x_cg - x_lemac) / mac


def cg_envelope(basic: Iterable[Component], optional: Iterable[Component] = (), fuel: Component | None = None,
                fuel_step: int = 11, x_lemac: float | None = None, mac: float | None = None,
                max_optional: int = 14) -> dict[str, Any]:
    """Centre-of-gravity envelope (forward/aft limits) over all loading cases.

    Parameters
    ----------
    basic : iterable
        Components present in every case (empty aircraft, pilot, ...), see :func:`mass_properties`.
    optional : iterable, optional
        Two-state (present/absent) items (passengers, baggage); all 2^n combinations are tried.
    fuel : component, optional
        ``(name, m_full, x, y, z)``; swept from empty to full in ``fuel_step`` equal steps (fuel burn).
    fuel_step : int, optional
        Number of fuel levels.
    x_lemac, mac : float, optional
        MAC leading-edge position and MAC length [m]; if both are given, %MAC is added to each case.
    max_optional : int, optional
        Maximum number of optional items (guards against 2^n blow-up).

    Returns
    -------
    dict[str, Any]
        ``cases`` list of dicts (``name``, ``m`` [kg], ``x_cg`` [m], optional ``percent_mac``),
        ``front`` and ``rear`` limiting cases, ``x_front``, ``x_rear`` their CG positions [m],
        ``m_min``, ``m_max`` mass range [kg].

    Raises
    ------
    ValueError
        If there are more than ``max_optional`` optional items, or a mass is negative.
    """
    optional = list(optional)
    if len(optional) > max_optional:
        raise ValueError(f"{len(optional)} optional items -> 2^n cases; at most {max_optional} allowed")
    base = [_component(b) for b in basic]
    ops = [_component(b) for b in optional]
    fuel_item = _component(fuel) if fuel is not None else None
    fills = np.linspace(0.0, 1.0, fuel_step) if fuel_item is not None else [0.0]
    cases = []
    for selection in itertools.product((0, 1), repeat=len(ops)):
        for fill in fills:
            m = sum(k[1] for k in base) + sum(s * k[1] for s, k in zip(selection, ops, strict=True))
            mom = (sum(k[1] * k[2][0] for k in base)
                   + sum(s * k[1] * k[2][0] for s, k in zip(selection, ops, strict=True)))
            name = "+".join([k[0] for s, k in zip(selection, ops, strict=True) if s]) or "basic"
            if fuel_item is not None:
                m += fill * fuel_item[1]
                mom += fill * fuel_item[1] * fuel_item[2][0]
                name += f" | fuel {100 * fill:.0f} %"
            x = mom / m
            d = {"name": name, "m": m, "x_cg": x}
            if x_lemac is not None and mac is not None:
                d["percent_mac"] = cg_percent_mac(x, x_lemac, mac)
            cases.append(d)
    front = min(cases, key=lambda d: d["x_cg"])
    rear = max(cases, key=lambda d: d["x_cg"])
    return {"cases": cases, "front": front, "rear": rear,
            "x_front": front["x_cg"], "x_rear": rear["x_cg"],
            "m_min": min(d["m"] for d in cases), "m_max": max(d["m"] for d in cases)}


# --- Raymer GA statistical group weights (returned in kg) ---
def _lb(m_kg: float) -> float:
    """Convert a mass from kg to lb."""
    return m_kg / LB_KG


def _cosd(angle: float) -> float:
    """Cosine of an angle given in degrees."""
    return math.cos(math.radians(angle))


def _require_positive(**kw: float | None) -> None:
    """Raise ValueError naming the first argument that is None or not positive."""
    for k, v in kw.items():
        if v is None or v <= 0:
            raise ValueError(f"{k} must be positive")


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; wing")
def raymer_wing(S_w: float, W_fw: float, A: float, Lambda: float, q: float, taper: float, t_c: float, Nz: float,
                W_dg: float) -> float:
    """Raymer GA wing weight.

    Parameters
    ----------
    S_w : float
        Trapezoidal wing area [m^2].
    W_fw : float
        Fuel mass in the wing [kg], >= 0.
    A : float
        Aspect ratio [-].
    Lambda : float
        Quarter-chord sweep [deg].
    q : float
        Cruise dynamic pressure [Pa].
    taper : float
        Taper ratio [-].
    t_c : float
        Thickness-to-chord ratio [-].
    Nz : float
        Ultimate load factor (1.5 x limit) [-].
    W_dg : float
        Design gross mass [kg].

    Returns
    -------
    float
        Wing mass [kg].

    Raises
    ------
    ValueError
        If an input other than ``W_fw``/``Lambda`` is not positive, or ``W_fw < 0``.

    Notes
    -----
    W = 0.036 Sw^0.758 Wfw^0.0035 (A/cos^2 Lambda)^0.6 q^0.006 lambda^0.04 (100 t/c / cos Lambda)^-0.3
    (Nz Wdg)^0.49 [lb, ft^2, psf]. Without wing fuel (W_fw = 0) the Wfw^0.0035 term is taken as 1
    (as AeroSandbox does; the equation would give zero, which is not physical).
    """
    _require_positive(S_w=S_w, A=A, q=q, taper=taper, t_c=t_c, Nz=Nz, W_dg=W_dg)
    if W_fw < 0:
        raise ValueError("W_fw must not be negative")
    c = _cosd(Lambda)
    fw = _lb(W_fw) ** 0.0035 if W_fw > 0 else 1.0
    w = (0.036 * (S_w / FT ** 2) ** 0.758 * fw * (A / c ** 2) ** 0.6 * (q / PSF) ** 0.006 * taper ** 0.04
         * (100 * t_c / c) ** -0.3 * (Nz * _lb(W_dg)) ** 0.49)
    return w * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; horizontal tail")
def raymer_horizontal_tail(S_ht: float, A_ht: float, Lambda_ht: float, q: float, taper_ht: float, t_c_ht: float,
                           Nz: float, W_dg: float) -> float:
    """Raymer GA horizontal-tail weight.

    Parameters
    ----------
    S_ht : float
        Horizontal tail area [m^2].
    A_ht : float
        Aspect ratio [-].
    Lambda_ht : float
        Quarter-chord sweep [deg].
    q : float
        Cruise dynamic pressure [Pa].
    taper_ht : float
        Taper ratio [-].
    t_c_ht : float
        Thickness-to-chord ratio [-].
    Nz : float
        Ultimate load factor [-].
    W_dg : float
        Design gross mass [kg].

    Returns
    -------
    float
        Horizontal tail mass [kg].

    Raises
    ------
    ValueError
        If an input other than ``Lambda_ht`` is not positive.

    Notes
    -----
    W = 0.016 (Nz Wdg)^0.414 q^0.168 Sht^0.896 (100 t/c / cos Lambda)^-0.12 (A/cos^2 Lambda)^0.043
    lambda^-0.02.
    """
    _require_positive(S_ht=S_ht, A_ht=A_ht, q=q, taper_ht=taper_ht, t_c_ht=t_c_ht, Nz=Nz, W_dg=W_dg)
    c = _cosd(Lambda_ht)
    w = (0.016 * (Nz * _lb(W_dg)) ** 0.414 * (q / PSF) ** 0.168 * (S_ht / FT ** 2) ** 0.896
         * (100 * t_c_ht / c) ** -0.12 * (A_ht / c ** 2) ** 0.043 * taper_ht ** -0.02)
    return w * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; vertical tail (Svt exponent: SUAVE 0.873, AeroSandbox 0.876)")
def raymer_vertical_tail(S_vt: float, A_vt: float, Lambda_vt: float, q: float, taper_vt: float, t_c_vt: float,
                         Nz: float, W_dg: float, Ht_Hv: float = 0.0) -> float:
    """Raymer GA vertical-tail weight.

    Parameters
    ----------
    S_vt : float
        Vertical tail area [m^2].
    A_vt : float
        Aspect ratio [-].
    Lambda_vt : float
        Quarter-chord sweep [deg].
    q : float
        Cruise dynamic pressure [Pa].
    taper_vt : float
        Taper ratio [-].
    t_c_vt : float
        Thickness-to-chord ratio [-].
    Nz : float
        Ultimate load factor [-].
    W_dg : float
        Design gross mass [kg].
    Ht_Hv : float, optional
        Height of the horizontal tail on the vertical tail: 0 conventional, 1 T-tail [-].

    Returns
    -------
    float
        Vertical tail mass [kg].

    Raises
    ------
    ValueError
        If an input other than ``Lambda_vt``/``Ht_Hv`` is not positive.

    Notes
    -----
    W = 0.073 (1 + 0.2 Ht/Hv) (Nz Wdg)^0.376 q^0.122 Svt^0.873 (100 t/c / cos Lambda)^-0.49
    (A/cos^2 Lambda)^0.357 lambda^0.039.

    SOURCE DISAGREEMENT: the Svt exponent is 0.873 in SUAVE and 0.876 in AeroSandbox. 0.873 is used
    (consistent with the Raymer text as remembered; not verified from the book). The difference is
    1.4 % for 100 ft^2.
    """
    _require_positive(S_vt=S_vt, A_vt=A_vt, q=q, taper_vt=taper_vt, t_c_vt=t_c_vt, Nz=Nz, W_dg=W_dg)
    c = _cosd(Lambda_vt)
    w = (0.073 * (1 + 0.2 * Ht_Hv) * (Nz * _lb(W_dg)) ** 0.376 * (q / PSF) ** 0.122 * (S_vt / FT ** 2) ** 0.873
         * (100 * t_c_vt / c) ** -0.49 * (A_vt / c ** 2) ** 0.357 * taper_vt ** 0.039)
    return w * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; fuselage (L/D: structural ratio per SUAVE, not verified)")
def raymer_fuselage(S_f: float, Nz: float, W_dg: float, L_t: float, L_D: float, q: float, V_pr: float = 0.0,
                    dP: float = 0.0) -> float:
    """Raymer GA fuselage weight.

    Parameters
    ----------
    S_f : float
        Fuselage wetted area [m^2].
    Nz : float
        Ultimate load factor [-].
    W_dg : float
        Design gross mass [kg].
    L_t : float
        Distance from the wing quarter chord to the tail quarter chord [m].
    L_D : float
        Fuselage structural length-to-depth ratio [-] (SUAVE interpretation; AeroSandbox uses the
        aerodynamic L/D here - the two sources disagree; the structural ratio appears to match
        Raymer's variable definition, NOT VERIFIED).
    q : float
        Cruise dynamic pressure [Pa].
    V_pr : float, optional
        Pressurized volume [m^3].
    dP : float, optional
        Cabin pressure differential [Pa].

    Returns
    -------
    float
        Fuselage mass [kg].

    Raises
    ------
    ValueError
        If S_f, Nz, W_dg, L_t, L_D or q is not positive.

    Notes
    -----
    W = 0.052 Sf^1.086 (Nz Wdg)^0.177 Lt^-0.051 (L/D)^-0.072 q^0.241 + 11.9 (Vpr dP)^0.271
    [lb, ft^2, ft, psf, ft^3, psi]; the pressurization term is added only if V_pr > 0 and dP > 0.
    """
    _require_positive(S_f=S_f, Nz=Nz, W_dg=W_dg, L_t=L_t, L_D=L_D, q=q)
    w = (0.052 * (S_f / FT ** 2) ** 1.086 * (Nz * _lb(W_dg)) ** 0.177 * (L_t / FT) ** -0.051 * L_D ** -0.072
         * (q / PSF) ** 0.241)
    if V_pr > 0 and dP > 0:
        w += 11.9 * ((V_pr / FT ** 3) * (dP / PSI)) ** 0.271
    return w * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; main landing gear (length in inches, per SUAVE)")
def raymer_main_landing_gear(N_l: float, W_l: float, L_m: float) -> float:
    """Raymer GA main landing gear weight.

    Parameters
    ----------
    N_l : float
        Ultimate landing load factor (Raymer: 1.5 x N_gear) [-].
    W_l : float
        Landing mass [kg].
    L_m : float
        Extended main gear length [m].

    Returns
    -------
    float
        Main gear mass [kg].

    Raises
    ------
    ValueError
        If an input is not positive.

    Notes
    -----
    W = 0.095 (Nl Wl)^0.768 (Lm/12)^0.409, Lm in inches -> (Lm/12) in ft.
    AeroSandbox uses ft/12 here (looks like a unit error); SUAVE uses in/12, which is adopted.
    """
    _require_positive(N_l=N_l, W_l=W_l, L_m=L_m)
    return 0.095 * (N_l * _lb(W_l)) ** 0.768 * (L_m / INC / 12) ** 0.409 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; nose landing gear")
def raymer_nose_landing_gear(N_l: float, W_l: float, L_n: float) -> float:
    """Raymer GA nose landing gear weight.

    Parameters
    ----------
    N_l : float
        Ultimate landing load factor [-].
    W_l : float
        Landing mass [kg].
    L_n : float
        Extended nose gear length [m].

    Returns
    -------
    float
        Nose gear mass [kg].

    Raises
    ------
    ValueError
        If an input is not positive.

    Notes
    -----
    W = 0.125 (Nl Wl)^0.566 (Ln/12)^0.845, Ln in inches.
    """
    _require_positive(N_l=N_l, W_l=W_l, L_n=L_n)
    return 0.125 * (N_l * _lb(W_l)) ** 0.566 * (L_n / INC / 12) ** 0.845 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; installed engine")
def raymer_engine_installed(W_en: float, N_en: int = 1) -> float:
    """Raymer GA installed engine weight (including propeller and engine mounts).

    Parameters
    ----------
    W_en : float
        Dry mass of one engine [kg].
    N_en : int, optional
        Number of engines.

    Returns
    -------
    float
        Installed engine mass [kg], W = 2.575 Wen^0.922 Nen [lb].

    Raises
    ------
    ValueError
        If an input is not positive.
    """
    _require_positive(W_en=W_en, N_en=N_en)
    return 2.575 * _lb(W_en) ** 0.922 * N_en * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; fuel system")
def raymer_fuel_system(V_t: float, V_i: float, N_t: int, N_en: int = 1) -> float:
    """Raymer GA fuel system weight.

    Parameters
    ----------
    V_t : float
        Total fuel volume [m^3].
    V_i : float
        Integral-tank fuel volume [m^3], >= 0.
    N_t : int
        Number of fuel tanks.
    N_en : int, optional
        Number of engines.

    Returns
    -------
    float
        Fuel system mass [kg].

    Raises
    ------
    ValueError
        If V_t, N_t or N_en is not positive, or ``V_i < 0``.

    Notes
    -----
    W = 2.49 Vt^0.726 (1/(1 + Vi/Vt))^0.363 Nt^0.242 Nen^0.157, V in US gallons. SUAVE's
    (Vt/(Vt + Vi))^0.363 and AeroSandbox's (1 + Vi/Vt)^-0.363 are algebraically identical.
    """
    _require_positive(V_t=V_t, N_t=N_t, N_en=N_en)
    if V_i < 0:
        raise ValueError("V_i must not be negative")
    return (2.49 * (V_t / GAL) ** 0.726 * (1 / (1 + V_i / V_t)) ** 0.363 * N_t ** 0.242 * N_en ** 0.157 * LB_KG)


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; flight controls (AeroSandbox form)")
def raymer_flight_controls(L: float, b: float, Nz: float, W_dg: float) -> float:
    """Raymer GA flight-control system weight.

    Parameters
    ----------
    L : float
        Fuselage length [m].
    b : float
        Wing span [m].
    Nz : float
        Ultimate load factor [-].
    W_dg : float
        Design gross mass [kg].

    Returns
    -------
    float
        Flight-control mass [kg].

    Raises
    ------
    ValueError
        If an input is not positive.

    Notes
    -----
    W = 0.053 L^1.536 B_w^0.371 (Nz Wdg 1e-4)^0.80 [lb, ft]. The SUAVE code has a typo,
    Wdg^(1e-4); the AeroSandbox form (Nz Wdg 1e-4) is used.
    """
    _require_positive(L=L, b=b, Nz=Nz, W_dg=W_dg)
    return 0.053 * (L / FT) ** 1.536 * (b / FT) ** 0.371 * (Nz * _lb(W_dg) * 1e-4) ** 0.80 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; hydraulics (AeroSandbox form; SUAVE uses 0.001 Wdg)")
def raymer_hydraulic(K_h: float, W_f: float, M: float) -> float:
    """Raymer GA hydraulic system weight.

    Parameters
    ----------
    K_h : float
        Hydraulic system factor [-]: 0.05 low subsonic, brakes and gear only; 0.11 medium subsonic,
        with flaps; 0.12 high subsonic, hydraulic flight controls; 0.013 hydraulic brakes only
        (M = 0.1) (Raymer text as quoted in AeroSandbox).
    W_f : float
        Fuselage width [m].
    M : float
        Cruise Mach number [-].

    Returns
    -------
    float
        Hydraulic system mass [kg], W = K_h W_f^0.8 M^0.5 [lb, ft].

    Raises
    ------
    ValueError
        If an input is not positive.

    Notes
    -----
    SOURCE DISAGREEMENT: SUAVE takes the hydraulics as 0.001 Wdg (possibly another edition).
    """
    _require_positive(K_h=K_h, W_f=W_f, M=M)
    return K_h * (W_f / FT) ** 0.8 * M ** 0.5 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; installed avionics")
def raymer_avionics(W_uav: float) -> float:
    """Raymer GA installed avionics weight.

    Parameters
    ----------
    W_uav : float
        Uninstalled avionics mass [kg].

    Returns
    -------
    float
        Installed avionics mass [kg], W = 2.117 W_uav^0.933 [lb].

    Raises
    ------
    ValueError
        If ``W_uav`` is not positive.
    """
    _require_positive(W_uav=W_uav)
    return 2.117 * _lb(W_uav) ** 0.933 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; electrical system")
def raymer_electrical(W_fuel_system: float, W_avionics: float) -> float:
    """Raymer GA electrical system weight.

    Parameters
    ----------
    W_fuel_system : float
        Fuel system mass [kg].
    W_avionics : float
        Installed avionics mass [kg].

    Returns
    -------
    float
        Electrical system mass [kg], W = 12.57 (W_fuel_system + W_avionics)^0.51 [lb].

    Raises
    ------
    ValueError
        If the sum of the inputs is not positive.
    """
    _require_positive(total=W_fuel_system + W_avionics)
    return 12.57 * _lb(W_fuel_system + W_avionics) ** 0.51 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; air conditioning and anti-icing")
def raymer_air_conditioning_icing(W_dg: float, N_p: float, W_avionics: float, M: float) -> float:
    """Raymer GA air-conditioning and anti-icing weight.

    Parameters
    ----------
    W_dg : float
        Design gross mass [kg].
    N_p : float
        Number of persons on board [-].
    W_avionics : float
        Installed avionics mass [kg].
    M : float
        Cruise Mach number [-].

    Returns
    -------
    float
        Mass [kg], W = 0.265 Wdg^0.52 Np^0.68 W_av^0.17 M^0.08 [lb].

    Raises
    ------
    ValueError
        If an input is not positive.
    """
    _require_positive(W_dg=W_dg, N_p=N_p, W_avionics=W_avionics, M=M)
    return 0.265 * _lb(W_dg) ** 0.52 * N_p ** 0.68 * _lb(W_avionics) ** 0.17 * M ** 0.08 * LB_KG


@cite(*_RAYMER_GA, note=_RAYMER_NOTE + "; furnishings")
def raymer_floor(W_dg: float) -> float:
    """Raymer GA furnishings ("floor") group weight.

    The Turkish original called this group "döşeme" (floor/furnishings); identifying it with
    Raymer's furnishings term is from memory and not verified against the book.

    Parameters
    ----------
    W_dg : float
        Design gross mass [kg].

    Returns
    -------
    float
        Mass [kg], W = 0.0582 Wdg - 65 [lb]; clipped to 0 if negative (small aircraft).

    Raises
    ------
    ValueError
        If ``W_dg`` is not positive.
    """
    _require_positive(W_dg=W_dg)
    return max(0.0582 * _lb(W_dg) - 65.0, 0.0) * LB_KG


@cite("raymer_2012", note="group weights compared with the Table 3.1 We/W0 regression")
def raymer_ga_empty_weight(g: Mapping[str, Any], kind: str = "GA single engine") -> dict[str, Any]:
    """Sum the Raymer GA group weights and compare with the statistical We/W0 regression.

    Parameters
    ----------
    g : mapping
        Required keys: ``W_dg`` design gross mass [kg], ``Nz`` ultimate load factor, ``q`` cruise
        dynamic pressure [Pa]; ``wing`` (S, A, Lambda, taper, t_c, W_fw), ``horizontal``
        (S, A, Lambda, taper, t_c), ``vertical`` (S, A, Lambda, taper, t_c[, Ht_Hv]), ``fuselage``
        (S_f, L_t, L_D[, V_pr, dP]), ``main_gear`` (N_l, W_l, L_m), ``nose_gear`` (N_l, W_l, L_n),
        ``engine`` (W_en, N_en), ``fuel`` (V_t, V_i, N_t), ``control`` (L, b).
        Optional: ``hydraulic`` (K_h, W_f, M), ``avionics`` (W_uav), ``air_conditioning`` (N_p, M;
        used only together with ``avionics``), ``floor`` (True to include furnishings).
        Units as in the individual ``raymer_*`` functions.
    kind : str, optional
        Aircraft type for the regression, a key of :data:`aerokit.aero.sizing.EMPTY_WEIGHT`.

    Returns
    -------
    dict[str, Any]
        ``groups`` dict of group masses [kg] (keys ``"wing"``, ``"horizontal tail"``,
        ``"vertical tail"``, ``"fuselage"``, ``"main landing gear"``, ``"nose landing gear"``,
        ``"installed engine"``, ``"fuel system"``, ``"flight controls"`` and, when requested,
        ``"hydraulics"``, ``"avionics"``, ``"electrical"``, ``"air conditioning/anti-icing"``,
        ``"furnishings"``), ``We`` total empty mass [kg], ``We_W0`` = We/W_dg [-],
        ``We_W0_regression`` Table 3.1 value [-], ``difference_percent`` 100 (We_W0 - reg)/reg.

    Raises
    ------
    KeyError
        If a required key is missing or ``kind`` is unknown.
    ValueError
        Propagated from the group-weight functions.
    """
    Wdg, Nz, q = g["W_dg"], g["Nz"], g["q"]
    wg, ht, vt, fus = g["wing"], g["horizontal"], g["vertical"], g["fuselage"]
    groups = {
        "wing": raymer_wing(wg["S"], wg["W_fw"], wg["A"], wg["Lambda"], q, wg["taper"], wg["t_c"], Nz, Wdg),
        "horizontal tail": raymer_horizontal_tail(ht["S"], ht["A"], ht["Lambda"], q, ht["taper"], ht["t_c"], Nz,
                                                  Wdg),
        "vertical tail": raymer_vertical_tail(vt["S"], vt["A"], vt["Lambda"], q, vt["taper"], vt["t_c"], Nz, Wdg,
                                              vt.get("Ht_Hv", 0.0)),
        "fuselage": raymer_fuselage(fus["S_f"], Nz, Wdg, fus["L_t"], fus["L_D"], q, fus.get("V_pr", 0.0),
                                    fus.get("dP", 0.0)),
        "main landing gear": raymer_main_landing_gear(**g["main_gear"]),
        "nose landing gear": raymer_nose_landing_gear(**g["nose_gear"]),
        "installed engine": raymer_engine_installed(**g["engine"]),
        "fuel system": raymer_fuel_system(**g["fuel"], N_en=g["engine"].get("N_en", 1)),
        "flight controls": raymer_flight_controls(g["control"]["L"], g["control"]["b"], Nz, Wdg),
    }
    if "hydraulic" in g:
        groups["hydraulics"] = raymer_hydraulic(**g["hydraulic"])
    if "avionics" in g:
        groups["avionics"] = raymer_avionics(**g["avionics"])
        groups["electrical"] = raymer_electrical(groups["fuel system"], groups["avionics"])
        if "air_conditioning" in g:
            ac = g["air_conditioning"]
            groups["air conditioning/anti-icing"] = raymer_air_conditioning_icing(Wdg, ac["N_p"],
                                                                                 groups["avionics"], ac["M"])
    if g.get("floor"):
        groups["furnishings"] = raymer_floor(Wdg)
    We = sum(groups.values())
    ratio = We / Wdg
    reg = sizing.empty_weight_ratio(Wdg * 9.80665, kind)
    return {"groups": groups, "We": We, "We_W0": ratio, "We_W0_regression": reg,
            "difference_percent": 100 * (ratio - reg) / reg}
