"""Zero-lift drag by component build-up, Oswald factor and the resulting drag polar.

Replaces the rehearsal's guess ``L/Dmax = K_LD·√(AR/(Swet/Sref))`` (K_LD = 11, Swet/Sref = 5.5
assumed, docs/04) with a component build-up

    CD0 = (Σ_c Cf_c · FF_c · Q_c · Swet_c / Sref + Σ misc (D/q)/Sref) · (1 + leakage fraction)

and the parabolic polar CD = CD0 + CL²/(π e AR) (Anderson 2017, Eq. 6.24, PDF p. 538).

Sources and verification status
-------------------------------
Read from the primary source in this session (J. D. Anderson, *Fundamentals of Aerodynamics*,
6th ed., the user's PDF; PDF page = book page + 23):

* laminar flat plate Cf = 1.328/√Re and δ = 5.0x/√Re_x (Eqs. 4.86, 4.84, PDF pp. 404–405,
  Example 4.8);
* turbulent flat plate Cf = 0.074/Re^(1/5) and δ = 0.37x/Re_x^(1/5) (Eqs. 4.88, 4.87, PDF p. 406,
  Example 4.9; Eqs. 19.1–19.2, PDF pp. 1075–1076);
* transition location from a critical Reynolds number (Eq. 4.89, PDF pp. 407–408) and the mixed
  laminar/turbulent plate Cf = (x1/c)Cf_lam,1 + Cf_turb,c − (x1/c)Cf_turb,1 (Eq. 4.92,
  PDF pp. 408–410, Examples 4.10 and 4.11);
* compressibility: reference-temperature method, T*/Te = 1 + 0.032 Me² + 0.58 (Tw/Te − 1)
  (Eq. 18.53, PDF p. 1056), applied to turbulent flow by Eqs. 19.3–19.4 (PDF p. 1077), with
  Sutherland's law (Eq. 15.3, PDF p. 1058), the recovery factor definition (Eq. 16.49 / 18.56,
  PDF pp. 999, 1057), r = √Pr laminar (Eq. 18.47, PDF p. 1057) and r ≈ Pr^(1/3) turbulent
  (PDF p. 1079), T0/T = 1 + (γ−1)/2 M² (Eq. 8.40, PDF p. 602); Examples 18.2 and 19.2;
* drag polar and Oswald efficiency (Eq. 6.24, e typically 0.7–0.85) and Raymer's straight-wing
  expression e = 1.78(1 − 0.045 AR^0.68) − 0.64 as quoted by Anderson (Eq. 6.25, PDF p. 538).

**Not verified in this session** (Raymer, *Aircraft Design*, is not available locally; the forms
below are implemented as they are commonly quoted and are marked ``not read in this session`` in
their ``@cite`` note):

* turbulent Cf = 0.455/((log10 Re)^2.58 (1 + 0.144 M²)^0.65) (optional ``model="raymer"``);
* form factors: lifting surface [1 + 0.6/(x/c)_m · t/c + 100 (t/c)^4][1.34 M^0.18 (cos Λ_m)^0.28],
  fuselage 1 + 60/f³ + f/400, nacelle 1 + 0.35/f;
* interference factors Q (table :data:`INTERFERENCE`);
* aft-fuselage upsweep drag D/q = 3.83 u^2.5 A_max;
* wetted area of a lifting surface Swet ≈ Sexp (1.977 + 0.52 t/c) (optional ``method="raymer"``);
* swept-wing Oswald factor e = 4.61(1 − 0.045 AR^0.68)(cos Λ_LE)^0.15 − 3.1;
* the K_LD wetted-aspect-ratio estimate itself (the rehearsal's K_LD = 11 came from a CSV attributed
  to Raymer).

The default wetted areas are geometric derivations instead (airfoil perimeter of the NACA 4-digit
thickness distribution; cones + cylinder for bodies), and the default skin friction is Anderson's.
Leakage and protuberance drag is a user-given fraction (default 0, no source claimed).

All quantities SI; angles in radians.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, NamedTuple

import numpy as np

from aerokit.aero.aircraft import Aircraft
from aerokit.aero.atmosphere import GAMMA, isa
from aerokit.aero.geometry import planform
from aerokit.aero.propulsion import Turbofan, Turboprop
from aerokit.references import cite

__all__ = [
    "CfModel", "INTERFERENCE", "PR_AIR", "SUTHERLAND_S",
    "cf_laminar", "cf_turbulent", "cf_turbulent_raymer", "cf_mixed", "cf_flat_plate",
    "bl_thickness_laminar", "bl_thickness_turbulent", "transition_location",
    "adiabatic_wall_ratio", "reference_temperature_ratio", "reference_conditions",
    "airfoil_perimeter_ratio", "exposed_area", "wetted_area_lifting", "wetted_area_body",
    "form_factor_lifting", "form_factor_body", "form_factor_nacelle", "interference_factor",
    "upsweep_drag_area",
    "Component", "lifting_surface", "body", "nacelle",
    "ComponentDrag", "Buildup", "component_buildup",
    "OswaldEstimate", "oswald_e", "oswald_estimates",
    "DragPolar", "drag_polar_from_buildup", "aircraft_from_polar",
    "KLDComparison", "compare_with_kld",
]

CfModel = Literal["anderson", "raymer"]

PR_AIR = 0.71
"""Prandtl number of air at standard conditions (Anderson 2017, PDF p. 1057)."""

SUTHERLAND_S = 110.0
"""Sutherland constant [K] as used in Anderson 2017, Eq. 15.3 (PDF p. 1058)."""


def _positive(name: str, value: float) -> float:
    v = float(value)
    if not (math.isfinite(v) and v > 0):
        raise ValueError(f"{name} must be a positive finite number, got {value!r}")
    return v


# ============================================================================ skin friction
@cite("anderson_2017", note="Eq. 4.86 (= Eq. 18.22), PDF p. 404; Example 4.8, PDF p. 405")
def cf_laminar(Re: float) -> float:
    """Laminar flat-plate skin-friction coefficient of one surface, Cf = 1.328/√Re.

    Parameters
    ----------
    Re : float
        Reynolds number based on plate length [-].

    Returns
    -------
    float
        Cf based on the wetted area of one side [-].

    Examples
    --------
    >>> f"{cf_laminar(3.1e6):.3g}"
    '0.000754'
    """
    return 1.328 / math.sqrt(_positive("Re", Re))


@cite("anderson_2017", note="Eq. 4.88 (= Eq. 19.2), PDF pp. 406, 1076; Example 4.9, PDF p. 406")
def cf_turbulent(Re: float) -> float:
    """Turbulent (incompressible) flat-plate skin-friction coefficient, Cf = 0.074/Re^(1/5).

    Parameters
    ----------
    Re : float
        Reynolds number based on plate length [-].

    Returns
    -------
    float
        Cf of one surface [-].

    Notes
    -----
    Anderson stresses that this is "only approximate", one result among many turbulent analyses.

    Examples
    --------
    >>> f"{cf_turbulent(3.1e6):.3g}"
    '0.00372'
    """
    return float(0.074 / _positive("Re", Re) ** 0.2)


@cite("raymer_2018", note="turbulent flat-plate Cf with compressibility factor (Ch. 12); "
                          "not read in this session; formula as commonly quoted")
def cf_turbulent_raymer(Re: float, M: float = 0.0) -> float:
    """Turbulent flat-plate Cf = 0.455/((log10 Re)^2.58 (1 + 0.144 M²)^0.65) — UNVERIFIED form.

    Parameters
    ----------
    Re : float
        Reynolds number based on component length [-].
    M : float, optional
        Free-stream Mach number [-]; the factor (1 + 0.144 M²)^0.65 is the formula's own
        compressibility correction.

    Returns
    -------
    float
        Cf of one surface [-].
    """
    _positive("Re", Re)
    if not (math.isfinite(M) and M >= 0):
        raise ValueError("Mach number must be finite and >= 0")
    return float(0.455 / (math.log10(Re) ** 2.58 * (1.0 + 0.144 * M * M) ** 0.65))


@cite("anderson_2017", note="Eq. 4.84 (= Eq. 18.23), PDF p. 404")
def bl_thickness_laminar(x: float, Re_x: float) -> float:
    """Laminar boundary-layer thickness δ = 5.0 x/√Re_x [m]."""
    return 5.0 * _positive("x", x) / math.sqrt(_positive("Re_x", Re_x))


@cite("anderson_2017", note="Eq. 4.87 (= Eq. 19.1), PDF pp. 406, 1075")
def bl_thickness_turbulent(x: float, Re_x: float) -> float:
    """Turbulent boundary-layer thickness δ = 0.37 x/Re_x^(1/5) [m]."""
    return float(0.37 * _positive("x", x) / _positive("Re_x", Re_x) ** 0.2)


@cite("anderson_2017", note="Eq. 4.89, PDF pp. 407–408 (worked numbers on p. 408)")
def transition_location(Re_transition: float, V: float, rho: float, mu: float) -> float:
    """Distance from the leading edge where transition occurs, x_cr = μ Re_cr/(ρ V) [m].

    Parameters
    ----------
    Re_transition : float
        Critical (transition) Reynolds number [-]; it "must come from somewhere — experiment,
        free flight, or some semi-empirical theory" (Anderson).
    V, rho, mu : float
        Free-stream speed [m/s], density [kg/m³], dynamic viscosity [Pa·s].
    """
    return _positive("mu", mu) * _positive("Re_transition", Re_transition) / (
        _positive("rho", rho) * _positive("V", V))


def _mixed(Re: float, Re_transition: float | None, lam_scale: float, turb: Callable[[float], float]) -> float:
    """Eq. 4.92 with turbulent law ``turb(Re)``; ``lam_scale`` rescales Re for the laminar part."""
    if Re_transition is None:
        return turb(Re)
    _positive("Re_transition", Re_transition)
    x1 = Re_transition / Re                      # x1/c = Re_xcr/Re_c
    if x1 >= 1.0:
        return cf_laminar(Re * lam_scale)
    Re1 = x1 * Re
    return float(x1 * cf_laminar(Re1 * lam_scale) + turb(Re) - x1 * turb(Re1))


@cite("anderson_2017", note="Eq. 4.92, PDF p. 410; Examples 4.10–4.11, PDF pp. 408–411")
def cf_mixed(Re: float, Re_transition: float | None) -> float:
    """Incompressible flat-plate Cf with laminar flow up to the transition point.

    Cf = (x1/c) Cf_lam(Re_x1) + Cf_turb(Re_c) − (x1/c) Cf_turb(Re_x1), x1/c = Re_transition/Re_c,
    with Anderson's laminar (Eq. 4.86) and turbulent (Eq. 4.88) laws.

    Parameters
    ----------
    Re : float
        Reynolds number based on plate length [-].
    Re_transition : float or None
        Critical Reynolds number; ``None`` means turbulent from the leading edge. If it is not
        smaller than ``Re`` the plate is fully laminar.

    Returns
    -------
    float
        Cf of one surface [-].
    """
    return _mixed(_positive("Re", Re), Re_transition, 1.0, cf_turbulent)


# ------------------------------------------------------------------ compressibility (Anderson)
@cite("anderson_2017", note="recovery factor Eq. 16.49/18.56 (PDF pp. 999, 1057), T0/T Eq. 8.40 "
                            "(PDF p. 602), r = Pr^(1/3) turbulent (PDF p. 1079)")
def adiabatic_wall_ratio(M: float, recovery: float | None = None, gamma: float = GAMMA) -> float:
    """Adiabatic-wall to edge temperature ratio Taw/Te = 1 + r (T0/Te − 1).

    Parameters
    ----------
    M : float
        Edge (free-stream) Mach number [-].
    recovery : float, optional
        Recovery factor r; default Pr^(1/3) with Pr = 0.71 (turbulent value, Anderson PDF p. 1079;
        the laminar value is √Pr, Eq. 18.47).
    gamma : float, optional
        Ratio of specific heats.
    """
    if not (math.isfinite(M) and M >= 0):
        raise ValueError("Mach number must be finite and >= 0")
    r = PR_AIR ** (1.0 / 3.0) if recovery is None else _positive("recovery", recovery)
    return 1.0 + r * (gamma - 1.0) / 2.0 * M * M


@cite("anderson_2017", note="Eq. 18.53, PDF p. 1056; applied to turbulent flow in Sec. 19.2.1, PDF p. 1077")
def reference_temperature_ratio(M: float, Tw_Te: float) -> float:
    """Reference temperature T*/Te = 1 + 0.032 Me² + 0.58 (Tw/Te − 1).

    Examples
    --------
    >>> round(reference_temperature_ratio(2.94, 2.467), 4)   # Anderson Example 18.2
    2.1275
    """
    if not (math.isfinite(M) and M >= 0):
        raise ValueError("Mach number must be finite and >= 0")
    return 1.0 + 0.032 * M * M + 0.58 * (_positive("Tw_Te", Tw_Te) - 1.0)


@cite("anderson_2017", note="Eqs. 18.53, 15.3 (Sutherland, S = 110 K), 19.3–19.4; PDF pp. 1056–1058, 1077")
def reference_conditions(M: float, Te: float, Tw_Te: float | None = None) -> dict[str, float]:
    """Property ratios at the reference temperature, at the constant edge pressure.

    Parameters
    ----------
    M : float
        Edge Mach number [-].
    Te : float
        Edge static temperature [K] (needed by Sutherland's law).
    Tw_Te : float, optional
        Wall temperature ratio; default adiabatic wall (:func:`adiabatic_wall_ratio`).

    Returns
    -------
    dict[str, float]
        ``T_ratio`` = T*/Te, ``rho_ratio`` = ρ*/ρe = Te/T*, ``mu_ratio`` = μ*/μe (Sutherland),
        ``Re_ratio`` = Re*/Re = (ρ*/ρe)/(μ*/μe).

    Notes
    -----
    With Cf* = D_f/(½ ρ* ue² S) (Eq. 19.4) the coefficient on free-stream dynamic pressure is
    Cf = Cf*·ρ*/ρe; Cf* is evaluated from the incompressible law at Re* (Eqs. 18.57, 19.3).
    """
    _positive("Te", Te)
    tw = adiabatic_wall_ratio(M) if Tw_Te is None else Tw_Te
    tr = reference_temperature_ratio(M, tw)
    T_star = tr * Te
    mu_ratio = tr ** 1.5 * (Te + SUTHERLAND_S) / (T_star + SUTHERLAND_S)
    rho_ratio = 1.0 / tr
    return {"T_ratio": tr, "rho_ratio": rho_ratio, "mu_ratio": mu_ratio, "Re_ratio": rho_ratio / mu_ratio}


@cite("anderson_2017", note="Eqs. 4.86, 4.88, 4.92 with the reference-temperature method "
                            "Eqs. 18.53, 18.57, 19.3–19.4 (PDF pp. 404–410, 1056–1058, 1077)")
def cf_flat_plate(Re: float, Re_transition: float | None = None, M: float = 0.0, Te: float = 288.15,
                  Tw_Te: float | None = None, model: CfModel = "anderson",
                  compressibility: bool = True) -> float:
    """Flat-plate skin friction of one surface, referred to free-stream dynamic pressure.

    Parameters
    ----------
    Re : float
        Free-stream Reynolds number based on the component length [-].
    Re_transition : float or None, optional
        Critical Reynolds number (free-stream based); ``None`` = turbulent from the leading edge.
    M, Te : float, optional
        Free-stream Mach number and static temperature [K].
    Tw_Te : float, optional
        Wall temperature ratio (default adiabatic wall).
    model : {"anderson", "raymer"}
        ``"anderson"``: Anderson's laminar/turbulent laws, Eq. 4.92 mixing and — if
        ``compressibility`` — the reference-temperature method applied to both parts (Re → Re*,
        Cf = Cf*·ρ*/ρe). ``"raymer"``: Eq. 4.92 mixing of Anderson's laminar law with the
        UNVERIFIED Raymer turbulent law, whose own (1 + 0.144 M²)^0.65 factor is the only
        compressibility correction (the laminar part is left incompressible).
    compressibility : bool, optional
        Apply the compressibility correction of the chosen model.

    Returns
    -------
    float
        Cf [-].
    """
    _positive("Re", Re)
    if model == "raymer":
        mach = M if compressibility else 0.0
        return _mixed(Re, Re_transition, 1.0, lambda r: cf_turbulent_raymer(r, mach))
    if model != "anderson":
        raise ValueError(f"unknown skin-friction model {model!r}")
    if not compressibility or (M == 0.0 and Tw_Te is None):
        return cf_mixed(Re, Re_transition)
    rc = reference_conditions(M, Te, Tw_Te)
    k = rc["Re_ratio"]
    if Re_transition is None:
        cf_star = cf_turbulent(Re * k)
    else:
        # transition point fixed by the free-stream critical Re (x1/c = Re_cr/Re); every piece
        # of Eq. 4.92 is then evaluated at the reference Reynolds number of its own length
        x1 = _positive("Re_transition", Re_transition) / Re
        if x1 >= 1.0:
            cf_star = cf_laminar(Re * k)
        else:
            cf_star = x1 * cf_laminar(x1 * Re * k) + cf_turbulent(Re * k) - x1 * cf_turbulent(x1 * Re * k)
    return cf_star * rc["rho_ratio"]


# ============================================================================ wetted areas
@cite("abbott_vondoenhoff_1959", note="NACA 4-digit thickness distribution (closed trailing edge, "
                                      "same coefficients as aerokit.aero.geometry.naca4); perimeter by quadrature")
def airfoil_perimeter_ratio(t_c: float, n: int = 2001) -> float:
    """Perimeter/chord of a symmetric NACA 4-digit section of thickness ratio ``t_c``.

    For a wing of constant t/c the wetted area of an exposed panel is exactly
    ``Sexp · P/c`` (perimeter scales with the local chord; tip caps neglected). Cambered NACA
    sections with the same thickness distribution (e.g. 230xx) differ by a few tenths of a percent.

    Parameters
    ----------
    t_c : float
        Thickness ratio, 0 <= t_c < 0.4.
    n : int, optional
        Number of cosine-spaced points per surface.

    Examples
    --------
    >>> airfoil_perimeter_ratio(0.0)
    2.0
    """
    if not (math.isfinite(t_c) and 0 <= t_c < 0.4):
        raise ValueError("t/c must be in [0, 0.4)")
    if n < 3:
        raise ValueError("n must be >= 3")
    beta = np.linspace(0.0, math.pi, n)
    x = 0.5 * (1.0 - np.cos(beta))
    yt = 5.0 * t_c * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4)
    return float(2.0 * np.sum(np.hypot(np.diff(x), np.diff(yt))))


def exposed_area(S: float, AR: float, taper: float, body_width: float) -> dict[str, float]:
    """Exposed part of a straight-tapered wing outside a body of width ``body_width``.

    Parameters
    ----------
    S, AR, taper : float
        Reference (trapezoidal, centre-line) area [m²], aspect ratio, taper ratio.
    body_width : float
        Width of the fuselage at the wing [m] (0 for a tail mounted on top of a fin, etc.).

    Returns
    -------
    dict[str, float]
        ``S_exposed`` [m²], ``c_side`` chord at the body side [m], ``c_tip`` [m], ``MAC_exposed``
        mean aerodynamic chord of the exposed panel [m], ``b`` span [m].

    Notes
    -----
    Derivation: c(y) is linear in y, so the area inside the body is
    ``w (c_root + c(w/2))/2`` and the exposed panel is a trapezoid from c(w/2) to c_tip.
    """
    p = planform(_positive("S", S), _positive("AR", AR), _positive("taper", taper))
    w = float(body_width)
    if not (math.isfinite(w) and 0 <= w < p["b"]):
        raise ValueError("body width must be in [0, span)")
    c_side = p["c_root"] - (p["c_root"] - p["c_tip"]) * w / p["b"]
    s_exp = S - w * (p["c_root"] + c_side) / 2.0
    ct = p["c_tip"]
    mac = 2.0 / 3.0 * (c_side + ct - c_side * ct / (c_side + ct))
    return {"S_exposed": s_exp, "c_side": c_side, "c_tip": ct, "MAC_exposed": mac, "b": p["b"]}


@cite("raymer_2018", note="method='raymer' only: Swet = Sexp(1.977 + 0.52 t/c) (Ch. 7); "
                          "not read in this session; formula as commonly quoted")
def wetted_area_lifting(S_exposed: float, t_c: float, method: Literal["perimeter", "raymer"] = "perimeter") -> float:
    """Wetted area of a lifting surface [m²] (both sides).

    Parameters
    ----------
    S_exposed : float
        Exposed planform area [m²].
    t_c : float
        Mean thickness ratio [-].
    method : {"perimeter", "raymer"}
        ``"perimeter"`` (default, derivation): ``S_exposed · P/c`` from
        :func:`airfoil_perimeter_ratio`. ``"raymer"``: the UNVERIFIED commonly quoted fit.
    """
    _positive("S_exposed", S_exposed)
    if method == "perimeter":
        return S_exposed * airfoil_perimeter_ratio(t_c)
    if method == "raymer":
        if not 0 <= t_c < 0.4:
            raise ValueError("t/c must be in [0, 0.4)")
        return S_exposed * (1.977 + 0.52 * t_c) if t_c > 0.05 else 2.003 * S_exposed
    raise ValueError(f"unknown wetted-area method {method!r}")


def wetted_area_body(length: float, diameter: float, nose_length: float, tail_length: float) -> float:
    """Wetted area of a body of revolution: nose cone + cylinder + tail cone [m²].

    Parameters
    ----------
    length, diameter : float
        Overall length and maximum (equivalent circular) diameter [m].
    nose_length, tail_length : float
        Lengths of the conical nose and tail [m]; nose + tail <= length.

    Notes
    -----
    Derivation: cone lateral area π r √(r² + L²), cylinder π d L_cyl. A zero-length nose or tail
    is therefore a flat disc π r² (blunt end, counted as wetted). A cone is slimmer than a real
    (ogive/elliptic) nose, so this slightly underestimates the nose area.
    """
    L, d = _positive("length", length), _positive("diameter", diameter)
    if nose_length < 0 or tail_length < 0 or nose_length + tail_length > L:
        raise ValueError("need 0 <= nose_length, tail_length and nose + tail <= length")
    r = d / 2.0
    cyl = math.pi * d * (L - nose_length - tail_length)
    return cyl + math.pi * r * (math.hypot(r, nose_length) + math.hypot(r, tail_length))


# ============================================================================ form & interference factors
@cite("raymer_2018", note="wing/tail/strut form factor (Ch. 12); not read in this session; formula as commonly quoted")
def form_factor_lifting(t_c: float, x_c_max: float, M: float, sweep_max_t: float = 0.0) -> float:
    """Lifting-surface form factor FF = [1 + 0.6/(x/c)_m · t/c + 100 (t/c)^4][1.34 M^0.18 (cos Λ_m)^0.28].

    UNVERIFIED form. Note that the Mach factor tends to 0 as M → 0 (it is ≈ 1 near M = 0.2), so the
    formula is meant for M ≳ 0.2.

    Parameters
    ----------
    t_c : float
        Thickness ratio [-].
    x_c_max : float
        Chordwise position of maximum thickness [-] (≈ 0.30 for the NACA 4-digit/230xx thickness).
    M : float
        Free-stream Mach number [-], > 0.
    sweep_max_t : float, optional
        Sweep of the maximum-thickness line [rad].
    """
    _positive("x_c_max", x_c_max)
    _positive("M", M)
    if not 0 <= t_c < 0.4:
        raise ValueError("t/c must be in [0, 0.4)")
    return float((1.0 + 0.6 / x_c_max * t_c + 100.0 * t_c ** 4) * (1.34 * M ** 0.18 * math.cos(sweep_max_t) ** 0.28))


@cite("raymer_2018", note="fuselage/canopy form factor (Ch. 12); not read in this session; formula as commonly quoted")
def form_factor_body(fineness: float) -> float:
    """Fuselage form factor FF = 1 + 60/f³ + f/400, f = length/diameter. UNVERIFIED form."""
    f = _positive("fineness", fineness)
    return 1.0 + 60.0 / f ** 3 + f / 400.0


@cite("raymer_2018", note="nacelle/external-store form factor (Ch. 12); not read in this session; "
                          "formula as commonly quoted")
def form_factor_nacelle(fineness: float) -> float:
    """Nacelle form factor FF = 1 + 0.35/f, f = length/diameter. UNVERIFIED form."""
    return 1.0 + 0.35 / _positive("fineness", fineness)


INTERFERENCE: Mapping[str, tuple[float, float]] = MappingProxyType({
    "nacelle_on_fuselage_or_wing": (1.5, 1.5),
    "nacelle_within_one_diameter": (1.3, 1.3),
    "nacelle_beyond_one_diameter": (1.0, 1.0),
    "wingtip_store": (1.25, 1.25),
    "wing_high_mid_or_filleted_low": (1.0, 1.0),
    "wing_low_unfilleted": (1.1, 1.4),
    "fuselage": (1.0, 1.0),
    "tail_conventional": (1.04, 1.05),
    "tail_h": (1.08, 1.08),
    "tail_v": (1.03, 1.03),
})
"""Interference factor ranges (low, high), Raymer as commonly quoted — UNVERIFIED (not read)."""


@cite("raymer_2018", note="interference factors Q (Ch. 12); not read in this session; values as commonly quoted")
def interference_factor(kind: str, which: Literal["low", "high", "mid"] = "low") -> float:
    """Interference factor Q from :data:`INTERFERENCE` (UNVERIFIED values).

    Parameters
    ----------
    kind : str
        Key of :data:`INTERFERENCE`.
    which : {"low", "high", "mid"}
        End or midpoint of the quoted range.
    """
    if kind not in INTERFERENCE:
        raise ValueError(f"unknown interference kind {kind!r}; choose one of {', '.join(INTERFERENCE)}")
    lo, hi = INTERFERENCE[kind]
    return {"low": lo, "high": hi, "mid": 0.5 * (lo + hi)}[which]


@cite("raymer_2018", note="aft-fuselage upsweep drag (Ch. 12); not read in this session; formula as commonly quoted")
def upsweep_drag_area(upsweep: float, A_max: float) -> float:
    """Drag area of an upswept aft fuselage, D/q = 3.83 u^2.5 A_max [m²] (u in rad). UNVERIFIED form."""
    if not (math.isfinite(upsweep) and 0 <= upsweep < math.pi / 2):
        raise ValueError("upsweep must be in [0, pi/2) rad")
    return float(3.83 * upsweep ** 2.5 * _positive("A_max", A_max))


# ============================================================================ components
@dataclass(frozen=True)
class Component:
    """One wetted component of the build-up.

    Attributes
    ----------
    name : str
    kind : {"lifting", "body", "nacelle"}
        Selects the form-factor law.
    Swet : float
        Wetted area of ONE item [m²].
    length : float
        Reynolds-number length [m] (exposed MAC for lifting surfaces, body length otherwise).
    t_c, x_c_max, sweep_max_t : float
        Lifting surfaces: thickness ratio, max-thickness position, sweep of that line [rad].
    fineness : float
        Bodies/nacelles: length/diameter.
    Q : float
        Interference factor.
    Re_transition : float or None
        Critical Reynolds number (``None`` = turbulent from the leading edge).
    FF : float or None
        Form-factor override (skips the law).
    count : int
        Number of identical items (e.g. 2 nacelles).
    """

    name: str
    kind: Literal["lifting", "body", "nacelle"]
    Swet: float
    length: float
    t_c: float = 0.0
    x_c_max: float = 0.3
    sweep_max_t: float = 0.0
    fineness: float = 0.0
    Q: float = 1.0
    Re_transition: float | None = 5e5
    FF: float | None = None
    count: int = 1

    def __post_init__(self) -> None:
        if self.kind not in ("lifting", "body", "nacelle"):
            raise ValueError(f"unknown component kind {self.kind!r}")
        _positive("Swet", self.Swet)
        _positive("length", self.length)
        _positive("Q", self.Q)
        if self.count < 1:
            raise ValueError("count must be >= 1")
        if self.FF is None and self.kind != "lifting":
            _positive("fineness", self.fineness)
        if self.FF is not None:
            _positive("FF", self.FF)

    def form_factor(self, M: float) -> float:
        """Form factor at Mach ``M`` (override if given)."""
        if self.FF is not None:
            return self.FF
        if self.kind == "lifting":
            return form_factor_lifting(self.t_c, self.x_c_max, M, self.sweep_max_t)
        if self.kind == "body":
            return form_factor_body(self.fineness)
        return form_factor_nacelle(self.fineness)


def lifting_surface(name: str, S: float, AR: float, taper: float, t_c: float, *, body_width: float = 0.0,
                    x_c_max: float = 0.3, sweep_max_t: float = 0.0, Q: float = 1.0,
                    Re_transition: float | None = 5e5,
                    wetted: Literal["perimeter", "raymer"] = "perimeter") -> Component:
    """Wing or tail component from its trapezoidal planform.

    Parameters
    ----------
    name : str
    S, AR, taper : float
        Reference (centre-line trapezoid) area [m²], aspect ratio, taper ratio.
    t_c : float
        Mean thickness ratio.
    body_width : float, optional
        Width of the body covering the root [m].
    x_c_max, sweep_max_t, Q, Re_transition
        See :class:`Component`.
    wetted : {"perimeter", "raymer"}
        Wetted-area method of :func:`wetted_area_lifting`.
    """
    ex = exposed_area(S, AR, taper, body_width)
    return Component(name, "lifting", wetted_area_lifting(ex["S_exposed"], t_c, wetted), ex["MAC_exposed"],
                     t_c=t_c, x_c_max=x_c_max, sweep_max_t=sweep_max_t, Q=Q, Re_transition=Re_transition)


def body(name: str, length: float, diameter: float, nose_length: float, tail_length: float, *, Q: float = 1.0,
         Re_transition: float | None = 5e5) -> Component:
    """Fuselage component (body of revolution, :func:`wetted_area_body`)."""
    return Component(name, "body", wetted_area_body(length, diameter, nose_length, tail_length), length,
                     fineness=length / diameter, Q=Q, Re_transition=Re_transition)


def nacelle(name: str, length: float, diameter: float, nose_length: float, tail_length: float, *, count: int = 1,
            Q: float = 1.0, Re_transition: float | None = 5e5) -> Component:
    """Nacelle component(s) (body of revolution, nacelle form factor)."""
    return Component(name, "nacelle", wetted_area_body(length, diameter, nose_length, tail_length), length,
                     fineness=length / diameter, Q=Q, Re_transition=Re_transition, count=count)


# ============================================================================ build-up
@dataclass(frozen=True)
class ComponentDrag:
    """One row of the build-up table (``Swet`` and ``CD0`` include ``count``)."""

    name: str
    Re: float
    Cf: float
    FF: float
    Q: float
    Swet: float
    CD0: float
    share: float


@dataclass(frozen=True)
class Buildup:
    """Result of :func:`component_buildup`.

    Attributes
    ----------
    CD0 : float
        Total zero-lift drag coefficient.
    rows : tuple[ComponentDrag, ...]
        Component rows (``share`` = fraction of the total CD0).
    misc : tuple[tuple[str, float], ...]
        (name, ΔCD0) of the miscellaneous drag areas.
    CD0_leakage : float
        Leakage and protuberance increment.
    S_ref, Swet_total, V, h, M : float
        Reference area, total wetted area, flight condition.
    cf_model : str
    """

    CD0: float
    rows: tuple[ComponentDrag, ...]
    misc: tuple[tuple[str, float], ...]
    CD0_leakage: float
    S_ref: float
    Swet_total: float
    V: float
    h: float
    M: float
    cf_model: str

    @property
    def Swet_Sref(self) -> float:
        """Total wetted area over reference area."""
        return self.Swet_total / self.S_ref

    def as_rows(self) -> list[dict[str, float | str]]:
        """Component rows plus misc and leakage lines as plain dictionaries."""
        out: list[dict[str, float | str]] = [
            {"name": r.name, "Re": r.Re, "Cf": r.Cf, "FF": r.FF, "Q": r.Q, "Swet": r.Swet, "CD0": r.CD0,
             "share": r.share} for r in self.rows]
        out += [{"name": n, "CD0": c, "share": c / self.CD0} for n, c in self.misc]
        out.append({"name": "leakage & protuberance", "CD0": self.CD0_leakage, "share": self.CD0_leakage / self.CD0})
        return out


@cite("anderson_2017", note="CD,o as the sum of friction and pressure drag of all components (Sec. 6.7.2, "
                            "PDF pp. 537–538); skin friction per cf_flat_plate")
@cite("raymer_2018", note="component build-up CD0 = Σ Cf FF Q Swet/Sref + misc + L&P (Ch. 12); "
                          "not read in this session; method as commonly quoted")
def component_buildup(components: Sequence[Component], V: float, h: float, *, S_ref: float,
                      misc: Iterable[tuple[str, float]] = (), leakage_fraction: float = 0.0,
                      cf_model: CfModel = "anderson", compressibility: bool = True) -> Buildup:
    """Zero-lift drag coefficient by component build-up.

    Parameters
    ----------
    components : sequence of Component
    V : float
        True airspeed [m/s].
    h : float
        ISA altitude [m] (density, viscosity, temperature, speed of sound from
        :func:`aerokit.aero.atmosphere.isa`).
    S_ref : float
        Reference wing area [m²].
    misc : iterable of (name, D/q [m²])
        Miscellaneous drag areas (e.g. :func:`upsweep_drag_area`).
    leakage_fraction : float, optional
        Leakage & protuberance as a fraction of the other CD0 (user assumption; no default source).
    cf_model : {"anderson", "raymer"}
        Skin-friction law, see :func:`cf_flat_plate`.
    compressibility : bool, optional
        Apply the model's compressibility correction.

    Returns
    -------
    Buildup
    """
    if not components:
        raise ValueError("at least one component is needed")
    S_ref = _positive("S_ref", S_ref)
    V = _positive("V", V)
    if not (math.isfinite(leakage_fraction) and leakage_fraction >= 0):
        raise ValueError("leakage fraction must be >= 0")
    atm = isa(h)
    M = V / atm["a"]
    raw: list[tuple[Component, float, float, float, float]] = []
    for c in components:
        Re = V * c.length / atm["nu"]
        cf = cf_flat_plate(Re, c.Re_transition, M, atm["T"], None, cf_model, compressibility)
        ff = c.form_factor(M)
        cd = cf * ff * c.Q * c.Swet * c.count / S_ref
        raw.append((c, Re, cf, ff, cd))
    misc_rows = tuple((str(n), _positive(f"misc drag area {n!r}", a) / S_ref) for n, a in misc)
    subtotal = sum(r[4] for r in raw) + sum(m[1] for m in misc_rows)
    leak = leakage_fraction * subtotal
    total = subtotal + leak
    rows = tuple(ComponentDrag(c.name, Re, cf, ff, c.Q, c.Swet * c.count, cd, cd / total)
                 for c, Re, cf, ff, cd in raw)
    swet = sum(r.Swet for r in rows)
    return Buildup(total, rows, misc_rows, leak, S_ref, swet, V, h, M, cf_model)


# ============================================================================ Oswald factor and polar
class OswaldEstimate(NamedTuple):
    """An Oswald efficiency estimate with the provenance of its formula."""

    value: float
    method: str
    source: str
    verified: bool


@cite("anderson_2017", note="Eq. 6.25 (Raymer's straight-wing expression as quoted by Anderson), PDF p. 538")
@cite("raymer_2018", note="method='raymer_swept': e = 4.61(1-0.045AR^0.68)(cos ΛLE)^0.15 - 3.1 (Ch. 12); "
                          "not read in this session; formula as commonly quoted")
def oswald_e(AR: float, sweep_LE: float = 0.0, method: Literal["anderson", "raymer_swept"] = "anderson"
             ) -> OswaldEstimate:
    """Oswald efficiency factor of the complete aeroplane.

    Parameters
    ----------
    AR : float
        Aspect ratio [-]. Anderson notes Eq. 6.25 is for conventional AR, not sailplane AR (≈ 25+).
    sweep_LE : float, optional
        Leading-edge sweep [rad] (``raymer_swept`` only; commonly quoted as meant for ΛLE > 30°).
    method : {"anderson", "raymer_swept"}
        ``"anderson"``: e = 1.78 (1 − 0.045 AR^0.68) − 0.64, Anderson Eq. 6.25 (verified in this
        session). ``"raymer_swept"``: UNVERIFIED.

    Returns
    -------
    OswaldEstimate
    """
    _positive("AR", AR)
    if method == "anderson":
        return OswaldEstimate(1.78 * (1.0 - 0.045 * AR ** 0.68) - 0.64, method,
                              "Anderson 2017, Eq. 6.25, PDF p. 538 (Raymer straight-wing fit)", True)
    if method == "raymer_swept":
        e = 4.61 * (1.0 - 0.045 * AR ** 0.68) * math.cos(sweep_LE) ** 0.15 - 3.1
        return OswaldEstimate(e, method, "Raymer 2018 swept-wing fit, not read in this session", False)
    raise ValueError(f"unknown Oswald method {method!r}")


def oswald_estimates(AR: float, sweep_LE: float = 0.0) -> tuple[OswaldEstimate, ...]:
    """Every available Oswald estimate for (AR, ΛLE), verified ones first."""
    return (oswald_e(AR, sweep_LE, "anderson"), oswald_e(AR, sweep_LE, "raymer_swept"))


class DragPolar(NamedTuple):
    """Parabolic polar from a build-up; the first three fields are (CD0, e, L/Dmax)."""

    CD0: float
    e: float
    LD_max: float
    AR: float
    S_ref: float
    K: float
    CL_LDmax: float
    oswald: OswaldEstimate
    buildup: Buildup


@cite("anderson_2017", note="drag polar Eq. 6.24, PDF p. 538; (L/D)max = 1/(2√(CD0 K)) by derivation")
def drag_polar_from_buildup(buildup: Buildup, AR: float, *, sweep_LE: float = 0.0,
                            oswald_method: Literal["anderson", "raymer_swept"] = "anderson",
                            e: float | None = None) -> DragPolar:
    """Combine a build-up CD0 with an Oswald estimate into CD = CD0 + CL²/(π e AR).

    Parameters
    ----------
    buildup : Buildup
    AR : float
        Aspect ratio [-].
    sweep_LE, oswald_method
        Passed to :func:`oswald_e`.
    e : float, optional
        Use this Oswald factor instead of an estimate.

    Returns
    -------
    DragPolar
        ``(CD0, e, LD_max, ...)``; L/Dmax = ½ √(π e AR/CD0) at CL* = √(CD0 π e AR).
    """
    _positive("AR", AR)
    est = (oswald_e(AR, sweep_LE, oswald_method) if e is None
           else OswaldEstimate(_positive("e", e), "given", "user input", False))
    if not 0 < est.value <= 1:
        raise ValueError(f"Oswald factor {est.value:.3f} outside (0, 1]")
    K = 1.0 / (math.pi * est.value * AR)
    ld = 1.0 / (2.0 * math.sqrt(buildup.CD0 * K))
    return DragPolar(buildup.CD0, est.value, ld, AR, buildup.S_ref, K, math.sqrt(buildup.CD0 / K), est, buildup)


def aircraft_from_polar(polar: DragPolar, name: str, W0: float, engine: Turboprop | Turbofan,
                        **kwargs: Any) -> Aircraft:
    """:class:`~aerokit.aero.aircraft.Aircraft` with S, AR, CD0 and e taken from ``polar``.

    Other :class:`Aircraft` fields (CLmax, W_fuel, ...) are passed through ``kwargs``.
    """
    for k in ("S", "AR", "CD0", "e"):
        if k in kwargs:
            raise ValueError(f"{k} comes from the polar; do not pass it")
    return Aircraft(name=name, W0=W0, S=polar.S_ref, AR=polar.AR, CD0=polar.CD0, e=polar.e, engine=engine, **kwargs)


# ============================================================================ K_LD comparison
@dataclass(frozen=True)
class KLDComparison:
    """K_LD wetted-aspect-ratio estimate versus the build-up.

    Attributes
    ----------
    AR, Swet_Sref, KLD : float
        Inputs of the K_LD estimate.
    LD_kld : float
        K_LD √(AR/(Swet/Sref)).
    LD_buildup : float or None
        L/Dmax of the build-up polar.
    difference, rel_difference : float or None
        LD_buildup − LD_kld and that over LD_kld.
    KLD_implied : float or None
        K_LD that would reproduce the build-up, LD_buildup/√(AR/(Swet/Sref)).
    Swet_Sref_buildup : float or None
        Wetted-area ratio of the build-up geometry.
    LD_kld_buildup_wetted : float or None
        K_LD estimate re-evaluated with the build-up's Swet/Sref.
    """

    AR: float
    Swet_Sref: float
    KLD: float
    LD_kld: float
    LD_buildup: float | None = None
    difference: float | None = None
    rel_difference: float | None = None
    KLD_implied: float | None = None
    Swet_Sref_buildup: float | None = None
    LD_kld_buildup_wetted: float | None = None


@cite("raymer_2018", note="L/Dmax ≈ K_LD √(AR_wetted), AR_wetted = AR/(Swet/Sref) (Ch. 3); not read in this "
                          "session; the rehearsal's K_LD = 11 came from a CSV attributed to Raymer (docs/04)")
def compare_with_kld(AR: float, Swet_Sref: float, KLD: float = 11.0, polar: DragPolar | None = None
                     ) -> KLDComparison:
    """Report the K_LD estimate next to a build-up polar.

    Parameters
    ----------
    AR, Swet_Sref, KLD : float
        Aspect ratio, assumed wetted-area ratio and K_LD (rehearsal: 9, 5.5, 11 → 14.07).
    polar : DragPolar, optional
        Build-up polar to compare with.

    Returns
    -------
    KLDComparison
    """
    ld = _positive("KLD", KLD) * math.sqrt(_positive("AR", AR) / _positive("Swet_Sref", Swet_Sref))
    if polar is None:
        return KLDComparison(AR, Swet_Sref, KLD, ld)
    lb = polar.LD_max
    sw = polar.buildup.Swet_Sref
    return KLDComparison(AR, Swet_Sref, KLD, ld, lb, lb - ld, (lb - ld) / ld, lb / math.sqrt(AR / Swet_Sref),
                         sw, KLD * math.sqrt(AR / sw))
