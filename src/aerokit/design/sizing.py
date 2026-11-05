"""Requirements-driven conceptual sizing (Raymer weight fractions + constraint diagram).

``size(requirements, assumptions)`` runs the chain of the 2023 rehearsal (docs/04 §1) as a function:
payload → mission fraction (Breguet cruise and loiter, Raymer segment fractions) → W/S from the stall
and landing limits (``wing_loading``) → P/W of every constraint → the governing constraint → W0 by
fixed-point iteration, with the empty weight corrected for the installed power
(``power_weight_coupling``) → an :class:`~aerokit.aero.aircraft.Aircraft`.

Guards (each found by an off-design run that passed silently before, docs/07 §1):

* only propeller classes of Raymer Table 3.1 are sized — the chain uses propeller Breguet equations and
  a :class:`~aerokit.aero.propulsion.Turboprop`; jet classes raise instead of returning a turboprop;
* a landing-distance requirement limits W/S (before, it was only checked afterwards);
* the engine mass follows the installed power, ΔWe/W0 = g (P/W − (P/W)_ref)/p_eng, with the class
  reference power loading of :data:`CLASS_POWER_REFERENCE` and the engine specific power p_eng; without
  it W0 did not grow when a requirement multiplied the power;
* warnings for a flight Mach number where propeller compressibility losses are not modelled, a power
  loading far above the class reference, and a manned regression used for an unmanned design.

``power_weight_coupling: "off"`` with the default ``wing_loading: "max"`` reproduces the docs/04
rehearsal exactly.
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from aerokit import units
from aerokit.aero import performance as perf
from aerokit.aero import sizing as rs
from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.atmosphere import isa
from aerokit.aero.propulsion import Turboprop, lapse_ratio
from aerokit.design.requirements import Assumptions, Requirements
from aerokit.references import cite

__all__ = ["SizingResult", "size", "constraint_curves", "power_drop", "wing_loading_limits", "PowerReference",
           "CLASS_POWER_REFERENCE", "PROPELLER_CLASSES", "MIXED_CLASSES", "UNMANNED_CLASSES",
           "PROPELLER_MACH_WARNING", "POWER_LOADING_WARNING_RATIO"]

#: Raymer Table 3.1 classes the propeller chain sizes. Classification by aerokit (judgement): the class
#: names say which engines the regression data come from; the book itself was not read.
PROPELLER_CLASSES = frozenset({"powered sailplane", "homebuilt metal/wood", "homebuilt composite",
                               "GA single engine", "GA twin engine", "agricultural", "twin turboprop",
                               "flying boat", "UAV tactical", "UAV small"})
#: Classes that mix propeller and jet aircraft: sized with a warning.
MIXED_CLASSES = frozenset({"military cargo/bomber", "UAV high altitude"})
#: Regressions fitted to unmanned aircraft.
UNMANNED_CLASSES = frozenset({"UAV tactical", "UAV high altitude", "UAV small"})

#: Flight Mach number above which the missing propeller-compressibility model is flagged. aerokit
#: judgement threshold, no source read; the mechanism (thrust loss and blade-drag rise as the tips
#: approach the speed of sound) is described in Anderson 2017, PDF p. 812.
PROPELLER_MACH_WARNING = 0.6
#: Installed P/W above this multiple of the class reference is flagged (aerokit judgement).
POWER_LOADING_WARNING_RATIO = 2.0


@dataclass(frozen=True)
class PowerReference:
    """Installed sea-level power per take-off weight [W/N] of a representative aircraft of a class."""

    power_loading: float
    source: str


CLASS_POWER_REFERENCE: dict[str, PowerReference] = {
    "twin turboprop": PowerReference(2 * 783e3 / (6804.0 * G0),
                                     "King Air 350i: 2 × 783 kW, MTOW 6 804 kg (Wikipedia, read 2026-10-25)"),
}


@dataclass(frozen=True)
class SizingResult:
    """Outcome of :func:`size` (SI; weights in N).

    ``ws_limits`` are the largest W/S each low-speed requirement allows, ``ws_basis`` says which one (or
    the minimum-power rule) set W/S, ``engine_we_add`` is the power-weight correction added to We/W0 and
    ``warnings`` the plausibility flags of the run.
    """

    W0: float
    S: float
    WS: float
    PW: float
    P_installed: float
    governing: str
    constraints: dict[str, float]
    mission_fraction: float
    Wf_W0: float
    We_W0: float
    LD_max: float
    CD0: float
    e: float
    payload_mass: float
    aircraft: Aircraft
    segments: dict[str, float] = field(default_factory=dict)
    ws_limits: dict[str, float] = field(default_factory=dict)
    ws_basis: str = ""
    engine_we_add: float = 0.0
    warnings: tuple[str, ...] = ()

    @property
    def mass(self) -> float:
        """Take-off mass [kg]."""
        return self.W0 / G0


def power_drop(asm: Assumptions) -> Callable[[float], float]:
    """Altitude lapse P(h)/P_SL chosen by the assumptions."""
    model, n = str(asm["power_lapse"]), float(asm["power_lapse_n"])
    return lambda h: lapse_ratio(h, model, n)


def _psfc_lb_hp_h(psfc_si: float) -> float:
    return units.to_unit(psfc_si, "lb/(hp*h)", "psfc")


def _aero(asm: Assumptions) -> tuple[float, float, float, float]:
    """(AR, e, L/Dmax, CD0): K_LD estimate, or the overrides set by a drag build-up."""
    AR = float(asm["aspect_ratio"])
    e = float(asm["e_override"]) or rs.oswald_raymer(AR)
    if float(asm["CD0_override"]) > 0:
        CD0 = float(asm["CD0_override"])
        return AR, e, 1.0 / (2.0 * math.sqrt(CD0 / (math.pi * e * AR))), CD0
    LDmax = float(asm["K_LD"]) * math.sqrt(AR / float(asm["wetted_area_ratio"]))
    CD0, _K = rs.cd0_ldmax(LDmax, AR, e)
    return AR, e, LDmax, CD0


def constraint_curves(req: Requirements, asm: Assumptions, WS: np.ndarray) -> dict[str, np.ndarray]:
    """P/W [W/N] of each constraint over a W/S grid [N/m²] (for the constraint-diagram figure)."""
    AR, e, LDmax, CD0 = _aero(asm)
    K = 1.0 / (math.pi * e * AR)
    eta, drop = float(asm["propeller_efficiency"]), power_drop(asm)
    clean = float(asm["CLmax_clean"])
    Vmax = req.require("max_speed")
    out: dict[str, np.ndarray] = {}
    if req.get("rate_of_climb"):
        out[f"Climb {req.require('rate_of_climb'):g} m/s (SL)"] = np.array(
            [rs.pw_en_good_climb(w, req.require("rate_of_climb"), 0.0, CD0, K, eta, clean, Vmax, drop)[0] for w in WS])
    if req.get("service_ceiling"):
        h = req.require("service_ceiling")
        out[f"Ceiling {h:.0f} m"] = np.array(
            [rs.pw_en_good_climb(w, rs.SERVICE_CEILING_VV, h, CD0, K, eta, clean, Vmax, drop)[0] for w in WS])
    hv = req.get("max_speed_altitude", 0.0) or 0.0
    out[f"Vmax {Vmax * 3.6:.0f} km/h ({hv:.0f} m)"] = np.array(
        [rs.pw_required(w, Vmax, 0.0, hv, CD0, K, eta, drop) for w in WS])
    if req.get("takeoff_ground_roll"):
        out[f"Take-off run {req.require('takeoff_ground_roll'):.0f} m"] = np.array(
            [rs.pw_takeoff(w, req.require("takeoff_ground_roll"), float(asm["CLmax_takeoff"]),
                           float(asm["takeoff_propeller_efficiency"]), float(asm["rolling_friction"])) for w in WS])
    return out


def _class_warnings(req: Requirements, kind: str) -> list[str]:
    """Refuse classes the propeller chain cannot size; warn on mixed and manned/unmanned mismatches."""
    if kind not in rs.EMPTY_WEIGHT:
        raise KeyError(f"unknown aircraft_type {kind!r}; choose one of {', '.join(rs.EMPTY_WEIGHT)}")
    if kind not in PROPELLER_CLASSES | MIXED_CLASSES:
        raise ValueError(f"aircraft_type {kind!r} is not a propeller class: the sizing chain uses propeller "
                         "Breguet equations and a turboprop engine, so it would return a turboprop "
                         "(no jet sizing path yet, docs/07 A4)")
    out = []
    if kind in MIXED_CLASSES:
        out.append(f"aircraft_type {kind!r} mixes propeller and jet aircraft; sized as a propeller aircraft")
    people = (req.get("crew", 0.0) or 0.0) + (req.get("passengers", 0.0) or 0.0)
    if people == 0 and kind not in UNMANNED_CLASSES:
        out.append(f"no crew or passengers, but the {kind!r} empty-weight regression is fitted to manned "
                   "aircraft; consider a 'UAV ...' class")
    if people > 0 and kind in UNMANNED_CLASSES:
        out.append(f"crew/passengers given, but {kind!r} is an unmanned-aircraft regression")
    return out


def wing_loading_limits(req: Requirements, asm: Assumptions) -> dict[str, float]:
    """Largest W/S [N/m²] each low-speed requirement allows: ``stall`` and, if given, ``landing``.

    The landing limit is the root of :func:`aerokit.aero.performance.landing_distance` (from 50 ft, at
    W0, sea level, the defaults of that function) = the required distance, i.e. the same model the
    compliance table uses, so the sized design meets it by construction. The distance depends on W/S
    only, not on W0.

    Raises
    ------
    ValueError
        The landing distance cannot be met at any W/S ≥ 20 N/m² (approach and flare alone are longer).
    """
    from scipy.optimize import brentq

    AR, e, _LD, CD0 = _aero(asm)
    clmax = float(asm["CLmax_landing"])
    out = {"stall": rs.ws_stall(req.require("stall_speed"), clmax)}
    need = req.get("landing_distance")
    if need:
        def miss(ws: float) -> float:
            probe = Aircraft("landing probe", 1e5, 1e5 / ws, AR, CD0, e, Turboprop(1.0), CLmax_landing=clmax)
            return float(perf.landing_distance(probe)["total"]) - need

        lo, hi = 20.0, max(out["stall"], 100.0)
        if miss(lo) >= 0:
            raise ValueError(f"landing distance {need:.0f} m cannot be met at any W/S ≥ {lo:g} N/m² "
                             "(approach and flare alone are longer)")
        while miss(hi) < 0 and hi < 1e5:
            hi *= 2.0
        out["landing"] = float(brentq(miss, lo, hi, xtol=1e-6)) if miss(hi) >= 0 else hi
    return out


def _governing(req: Requirements, asm: Assumptions, ws: float) -> tuple[dict[str, float], str]:
    cons = {k: float(v[0]) for k, v in constraint_curves(req, asm, np.array([ws])).items()}
    return cons, max(cons, key=lambda k: cons[k])


def _min_power_ws(req: Requirements, asm: Assumptions, ws_max: float) -> float:
    """W/S in [0.25, 1] × ``ws_max`` with the lowest governing P/W (grid, then bounded Brent)."""
    from scipy.optimize import minimize_scalar

    def pw(ws: float) -> float:
        cons, gov = _governing(req, asm, ws)
        return cons[gov]

    grid = np.linspace(0.25 * ws_max, ws_max, 61)
    values = [pw(float(w)) for w in grid]
    k = int(np.argmin(values))
    lo, hi = float(grid[max(k - 1, 0)]), float(grid[min(k + 1, len(grid) - 1)])
    best = minimize_scalar(pw, bounds=(lo, hi), method="bounded", options={"xatol": 1e-3})
    return float(best.x) if float(best.fun) <= values[k] else float(grid[k])


def _engine_mass_fraction(kind: str, PW: float, asm: Assumptions, warnings: list[str]) -> float:
    """ΔWe/W0 = g (P/W − (P/W)_ref) / p_eng (0 if the coupling is off or the class has no reference)."""
    mode = str(asm["power_weight_coupling"])
    if mode not in ("on", "off"):
        raise ValueError("power_weight_coupling must be 'on' or 'off'")
    if mode == "off":
        return 0.0
    ref = CLASS_POWER_REFERENCE.get(kind)
    if ref is None:
        warnings.append(f"power-weight coupling not applied: no reference power loading for {kind!r}")
        return 0.0
    p_eng = float(asm["engine_specific_power"])
    if not p_eng > 0:
        raise ValueError("engine_specific_power must be > 0")
    return G0 * (PW - ref.power_loading) / p_eng


@cite("raymer_2018", note="weight fractions (Ch. 3) and constraint analysis (Ch. 5); via VT AOE 4065 slides, "
                          "book not read in this session")
@cite("wikipedia_pt6_2026", note="engine specific power of the power-weight coupling (PT6A-60A)")
@cite("wikipedia_king_air_2026", note="twin-turboprop reference power loading")
def size(req: Requirements, asm: Assumptions) -> SizingResult:
    """Size the aircraft for ``req`` under ``asm`` (see module docstring).

    Raises
    ------
    KeyError
        A requirement needed by the chain is missing (range, loiter, stall_speed, max_speed), or the
        aircraft type is unknown.
    ValueError
        Non-propeller aircraft type; unknown ``wing_loading``/``power_weight_coupling``; unattainable
        landing distance; or no weight solution (fuel + empty-weight fractions ≥ 1, e.g. because the
        engines needed for the requirements are too heavy).
    """
    kind = str(asm["aircraft_type"])
    warnings = _class_warnings(req, kind)
    AR, e, LDmax, CD0 = _aero(asm)
    eta = float(asm["propeller_efficiency"])
    payload = req.payload_mass
    if payload <= 0:
        raise ValueError("payload is zero: give crew/passengers/cargo_mass in the requirements")
    W_fixed = payload * G0
    seg = {"warm-up/take-off": rs.SEGMENT["heating_takeoff"], "climb": rs.SEGMENT["climb"],
           "cruise": rs.cruise_propeller(req.require("range"), _psfc_lb_hp_h(asm["psfc_cruise"]), eta, LDmax),
           "loiter": rs.loiter_propeller(req.require("loiter"), float(asm["loiter_speed"]),
                                         _psfc_lb_hp_h(asm["psfc_loiter"]), eta, 0.866 * LDmax),
           "landing": rs.SEGMENT["landing"]}
    mission = math.prod(seg.values())

    limits = wing_loading_limits(req, asm)
    limiting = min(limits, key=lambda k: limits[k])
    WS_max = limits[limiting]
    rule = str(asm["wing_loading"])
    if rule == "max":
        WS, ws_basis = WS_max, f"{limiting} limit"
    elif rule == "min_power":
        WS = _min_power_ws(req, asm, WS_max)
        ws_basis = ("minimum governing P/W" if WS_max * (1 - 1e-6) > WS
                    else f"{limiting} limit (the minimum P/W lies beyond it)")
    else:
        raise ValueError("wing_loading must be 'max' or 'min_power'")
    cons, governing = _governing(req, asm, WS)
    PW = cons[governing]

    we_add = _engine_mass_fraction(kind, PW, asm, warnings)
    try:
        s = rs.takeoff_weight(W_fixed, rs.fuel_ratio(mission), kind, we_factor=float(asm["empty_weight_factor"]),
                              we_add=we_add)
    except ValueError as exc:
        raise ValueError(f"{exc}: fuel Wf/W0 = {rs.fuel_ratio(mission):.3f}, engine-mass correction "
                         f"{we_add:+.3f} to We/W0 for P/W = {PW:.1f} W/N ({governing} governs)") from exc
    W0 = float(s["W0"])
    S = W0 / WS
    hv = req.get("max_speed_altitude", 0.0) or 0.0
    mach = req.require("max_speed") / isa(hv)["a"]
    if mach > PROPELLER_MACH_WARNING:
        warnings.append(f"max_speed is Mach {mach:.2f} at {hv:.0f} m: propeller compressibility losses are not "
                        f"modelled (flagged above Mach {PROPELLER_MACH_WARNING:g})")
    ref = CLASS_POWER_REFERENCE.get(kind)
    if ref is not None and POWER_LOADING_WARNING_RATIO * ref.power_loading < PW:
        warnings.append(f"P/W = {PW:.1f} W/N is {PW / ref.power_loading:.1f} × the {kind} reference "
                        f"({ref.power_loading:.1f} W/N, {ref.source})")
    engine = Turboprop(PW * W0, eta=eta, eta_takeoff=float(asm["takeoff_propeller_efficiency"]),
                       psfc=float(asm["psfc_cruise"]), lapse=str(asm["power_lapse"]), n=float(asm["power_lapse_n"]))
    ac = Aircraft("sized design", W0, S, AR, CD0, e, engine, CLmax_clean=float(asm["CLmax_clean"]),
                  CLmax_takeoff=float(asm["CLmax_takeoff"]), CLmax_landing=float(asm["CLmax_landing"]),
                  W_fuel=float(s["Wf_W0"]) * W0, W_empty=float(s["We_W0"]) * W0, W_payload=W_fixed,
                  mu_roll=float(asm["rolling_friction"]))
    return SizingResult(W0=W0, S=S, WS=WS, PW=PW, P_installed=PW * W0, governing=governing, constraints=cons,
                        mission_fraction=mission, Wf_W0=float(s["Wf_W0"]), We_W0=float(s["We_W0"]), LD_max=LDmax,
                        CD0=CD0, e=e, payload_mass=payload, aircraft=ac, segments=seg, ws_limits=limits,
                        ws_basis=ws_basis, engine_we_add=we_add, warnings=tuple(warnings))
