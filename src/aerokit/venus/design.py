"""Baseline VESPER rotorcraft and the ``design.json`` hand-off document for the visual session.

VESPER (*Venus Solar-Electric Powered Exploration Rotorcraft*, our name [Y]) — a folding hexacopter delivered by a
low-ballistic-coefficient entry capsule and a parachute, flying in the middle cloud deck at 55 km in the air-mass
frame. Every number in the document is produced here from :mod:`aerokit.venus` (sizing loop, BEMT, entry, descent,
mission simulation) unless tagged ``Y``.

Frame for positions: origin at the body centre, x forward (between arms 1 and 6), y left, z up; hover configuration,
arms deployed. Units SI.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np
from functools import lru_cache

from aerokit.venus import atmosphere as A
from aerokit.venus import descent as DS
from aerokit.venus import entry as EN
from aerokit.venus import sizing as S

__all__ = ["DESIGN_VERSION", "BASELINE", "Baseline", "baseline", "design_document", "release_hour_angle"]

DESIGN_VERSION = "0.6"
DESIGN_STATUS = "draft"


@dataclass(frozen=True)
class Baseline:
    D: float = 2.6                  # rotor diameter [m]: trade (out/trade_sizing.json) + robustness — 2.3 m is 3.4 kg
    #                                 lighter but falls to 21-28 h of flight in adverse cases; 2.6 m keeps >= 37 h
    V_tip: float = 70.0             # hover tip speed [m/s]
    v_inf: float = 3500.0           # arrival hyperbolic excess speed [m/s] [Y] (Hohmann 2.7 km/s is the floor)
    entry_altitude: float = 200e3
    gamma_deg: float = -9.5         # entry flight-path angle (corridor −8 … −11°, skip-out at −7°)
    aeroshell_D: float = 3.7        # Landis: 9 m-span folded aircraft fit a 3.7 m aeroshell [D-ag]
    chute_D: float = 12.0           # main parachute [Y]
    release_km: float = 61.0
    cruise_km: float = 55.0
    body_d: float = 0.60
    body_h: float = 0.32
    start_hour_angle_deg: float | None = None   # None: release when cos z = sustain threshold + 0.03
    payload_kg: float = 3.0


BASELINE = Baseline()


@lru_cache(maxsize=4)
def baseline(b: Baseline = BASELINE) -> dict:
    """Close the design and run entry, descent, deployment and the mission for the baseline."""
    from aerokit import venus_flight as VF

    d = S.close(b.D, b.V_tip, replace(S.Requirements(), payload_kg=b.payload_kg, altitude_m=b.cruise_km * 1e3))
    es = DS.entry_system(d.gross_kg)
    m_entry = es["total_with_contingency"]
    veh = EN.EntryVehicle(m_entry, b.aeroshell_D, 1.05, nose_radius_m=0.25 * b.aeroshell_D)
    VE = EN.entry_speed(b.v_inf, b.entry_altitude)
    ent = EN.fly_entry(veh, VE, b.gamma_deg, h0=b.entry_altitude)
    heat_shield = (es["heatshield_structure"] + es["heatshield_tps"]) * 1.3
    m_susp = m_entry - heat_shield
    h_chute = float(ent.h[-1])
    chute = DS.parachute_descent(m_susp, b.chute_D, h_chute, b.release_km * 1e3, float(ent.V[-1]))
    s_rel = A.state(b.release_km * 1e3)
    v_h = math.sqrt(d.gross_kg * s_rel.g / d.system.count / (2 * s_rel.rho * d.rotor.disk_area))
    dep = DS.deploy(d.gross_kg, b.release_km * 1e3, chute.V_end, v_h, d.req.thrust_margin, "pre-spun")
    dep_drop = DS.deploy(d.gross_kg, b.release_km * 1e3, chute.V_end, v_h, d.req.thrust_margin, "drop-then-spin")
    H0 = b.start_hour_angle_deg if b.start_hour_angle_deg is not None else release_hour_angle(d)
    run = VF.simulate_rotorcraft_day(d, start_hour_angle_deg=H0, cruise_km=b.cruise_km,
                                     dives=((6 * 3600.0, 51.0, 300.0), (20 * 3600.0, 51.0, 300.0)), dt=60.0)
    return {"design": d, "entry_system": es, "m_entry": m_entry, "entry_vehicle": veh, "VE": VE, "entry": ent,
            "m_suspended": m_susp, "chute": chute, "h_chute": h_chute, "deploy": dep, "deploy_drop": dep_drop,
            "v_h_release": v_h, "mission": run, "release_hour_angle_deg": H0}


def release_hour_angle(d: S.Design, margin: float = 0.03) -> float:
    """Morning hour angle [deg] at which the sun is just high enough for solar-sustained loiter (+ margin):
    the entry is targeted so that the rotorcraft starts flying there [Y: CONOPS choice]."""
    mu = d.sustain_mu0_loiter
    if mu is None:
        return 0.0                       # never sustained: release at local noon for the longest battery flight
    return -math.degrees(math.acos(min(mu + margin, 1.0)))


LABELS = {"rotors": "Rotors & motors", "arms": "Folding arms", "body": "Sealed Ti vessel", "battery": "Li-ion battery",
          "solar": "Bifacial solar deck", "payload": "Science payload", "avionics": "Avionics & IMU",
          "antenna": "UHF relay antenna", "thermal": "Heat pipe & insulation", "coating": "Acid-proof FEP skin",
          "attach": "Bridle & release", "wiring": "Harness", "contingency": "Mass margin 20 %"}


def _event_kind(text: str) -> str:
    """Machine-readable event class for the visual: release / dive / climb / abort / sunset / end."""
    t = text.lower()
    for key, kind in (("release", "release"), ("aborted", "abort"), ("sunset", "sunset"), ("science dive", "dive"),
                      ("climb back", "climb"), ("empty", "end"), ("limit", "end")):
        if key in t:
            return kind
    return "other"


def solar_fraction_down(h: float) -> float | None:
    """Downward solar flux as a fraction of the top-of-atmosphere value: Landis & Haag array output / (0.29 × 2600)
    at 40-60 km (their 'effective efficiency' / 29 %), the probe radiometer shape to 64 km, aerokit.planetary
    (Landis 2002 anchors) above. None below 40 km."""
    from aerokit import planetary as P
    from aerokit.venus import power as PW

    if h < 40e3:
        return None
    if h <= 64e3:
        return PW.array_output_overhead(h) / (PW.LANDIS_HAAG_EFFICIENCY * P.VENUS_SOLAR_FLUX_TOP)
    return P.venus_solar_fraction(min(h, 100e3))


def _components(d: S.Design, b: Baseline, deck_rc: float) -> list[dict]:
    bd = d.breakdown
    z_rot = 0.30 - b.body_h / 2.0
    span = 2 * d.arm_m + d.D
    return [
        dict(id="rotors", name="6 folding 2-blade rotors + 5:1 geared motors + collective actuators",
             mass_kg=round(bd["blades+hubs"] + bd["motors"] + bd["ESCs"], 2), colour="#c9cdd3",
             material="CFRP blades with FEP film wrap; Sm2Co17-magnet motors + planetary gearbox in PFA-sealed cans",
             tag="K", position_m=[0.0, 0.0, z_rot], size_m=[span, span, 0.12],
             note="arm i at azimuth 30°+60°·i; adjacent rotors counter-rotate"),
        dict(id="arms", name="6 folding CFRP arms with Ti hinges", mass_kg=bd["arms+hinges"], colour="#2b2b2b",
             material="CFRP tube, FEP sleeve, Ti-6Al-4V hinge and latch", tag="K",
             position_m=[0.0, 0.0, z_rot], size_m=[2 * d.arm_m, 2 * d.arm_m, 0.06]),
        dict(id="body", name="Sealed Ti vessel: battery, avionics, payload electronics", mass_kg=bd["vessel"],
             colour="#e8e4da", material="Ti-6Al-4V shell, silvered-FEP skin (α 0.08, ε 0.52), dry N2 fill", tag="K",
             position_m=[0.0, 0.0, 0.0], size_m=[b.body_d, b.body_d, b.body_h]),
        dict(id="battery", name=f"Li-ion battery {d.battery_Wh:.0f} Wh (inside vessel)", mass_kg=bd["battery"],
             colour="#4f6d7a", material="18650 energy cells (243 Wh/kg cell), charge 0-45 °C", tag="K",
             position_m=[0.0, 0.0, -0.06], size_m=[0.42, 0.42, 0.12]),
        dict(id="solar", name=f"Bifacial solar deck {d.solar_area_m2:.2f} m² (6 folding petals)",
             mass_kg=bd["solar"], colour="#1f3a5f", material="triple-junction cells, Parylene + FEP cover, CFRP frame",
             tag="K", position_m=[0.0, 0.0, z_rot - 0.05], size_m=[2 * deck_rc, 2 * deck_rc, 0.012],
             note="hexagon, circumradius %.2f m, corners 5 cm inside every rotor-disk edge" % deck_rc),
        dict(id="payload", name="Science: nephelometer, aerosol mass spectrometer, T/p/wind/turbulence, camera",
             mass_kg=bd["payload"], colour="#d98e04", material="sapphire windows, PTFE inlets", tag="Y",
             position_m=[0.0, 0.0, -b.body_h / 2.0 - 0.09], size_m=[0.32, 0.32, 0.18]),
        dict(id="avionics", name="Flight computer, IMU, baro, sun sensor, radio", mass_kg=bd["avionics"],
             colour="#6b8e23", material="inside the vessel", tag="D-ag (MSH 1.2 kg)",
             position_m=[0.0, 0.0, 0.08], size_m=[0.26, 0.26, 0.08]),
        dict(id="antenna", name="UHF crossed dipole on mast (relay link)", mass_kg=bd["comms"], colour="#b0b7bf",
             material="Ti mast, PTFE radome", tag="Y", position_m=[0.0, 0.0, b.body_h / 2.0 + 0.30],
             size_m=[0.34, 0.34, 0.60]),
        dict(id="thermal", name="Aerogel blanket + variable-conductance heat pipe to shell fins",
             mass_kg=bd["thermal"], colour="#f2f2f2", material="silica aerogel, Al/NH3 VCHP, coated fins", tag="K",
             position_m=[0.0, 0.0, 0.0], size_m=[b.body_d + 0.04, b.body_d + 0.04, b.body_h]),
        dict(id="coating", name="Acid-protection skin on all exposed parts", mass_kg=bd["coating"],
             colour="#ffffff", material="FEP/PTFE film, PFA coat, Parylene on cells", tag="K",
             position_m=[0.0, 0.0, 0.0], size_m=None),
        dict(id="attach", name="Bridle ring, pyro release, deployment fittings", mass_kg=bd["attach"],
             colour="#a0522d", material="Ti fittings, Kevlar/PBO bridle", tag="Y",
             position_m=[0.0, 0.0, b.body_h / 2.0 + 0.03], size_m=[0.18, 0.18, 0.06]),
        dict(id="wiring", name="Harness and connectors", mass_kg=bd["wiring"], colour="#555555",
             material="PTFE-insulated wire", tag="K", position_m=None, size_m=None),
        dict(id="contingency", name="Mass contingency 20 % (MSH practice)", mass_kg=bd["contingency"],
             colour="#999999", material="—", tag="D-ag", position_m=None, size_m=None),
    ]


def design_document(b: Baseline = BASELINE) -> dict:
    res = baseline(b)
    d: S.Design = res["design"]
    hp = d.hover
    deck_rc = d.deck_circumradius_m
    st = A.state(b.cruise_km * 1e3)
    ent, chute, dep, run = res["entry"], res["chute"], res["deploy"], res["mission"]
    t_chute_end = float(ent.t[-1])
    # simple timeline on the parachute
    t_unfold = t_chute_end + 0.35 * chute.duration_s
    h_unfold = float(chute.h[int(0.35 * (len(chute.h) - 1))])
    t_spin = t_chute_end + 0.8 * chute.duration_s
    h_spin = float(chute.h[int(0.8 * (len(chute.h) - 1))])
    t_rel = t_chute_end + chute.duration_s
    t_cruise = t_rel + (b.release_km - b.cruise_km) * 1e3 / 3.0
    comps = _components(d, b, deck_rc)
    for c in comps:
        c["label"] = LABELS.get(c["id"], c["id"])
    profile = A.profile_table(30, 80)
    for row in profile:
        f = solar_fraction_down(row["altitude_km"] * 1e3)
        row["solar_fraction_down"] = None if f is None else round(f, 3)
    step = max(1, int(round(3600.0 / float(run.t[1] - run.t[0])))) if len(run.t) > 1 else 1
    series = [{"t_h": round(float(run.t[i]) / 3600.0, 2), "altitude_km": round(float(run.z[i]) / 1e3, 2),
               "battery_Wh": round(float(run.energy_Wh[i]), 1), "solar_W": round(float(run.p_solar[i]), 0),
               "demand_W": round(float(run.p_need[i]), 0), "cos_zenith": round(float(run.mu0[i]), 3),
               "interior_C": round(float(run.T_interior_C[i]), 1)} for i in range(0, len(run.t), step)]
    zones = [
        {"step": 1, "name": "Released from the carrier/orbiter ~5 days before arrival; spin-stabilised coast",
         "altitude_km": None, "time_s": None, "tag": "Y"},
        {"step": 2, "name": f"Entry interface, {res['VE'] / 1e3:.2f} km/s at {b.gamma_deg:.1f}°",
         "altitude_km": b.entry_altitude / 1e3, "speed_m_s": round(res["VE"], 0), "time_s": 0.0, "tag": "K"},
        {"step": 3, "name": f"Peak deceleration {ent.peak_g:.0f} g; peak heating "
                            f"{ent.peak_q / 1e4:.0f} W/cm² convective + {max(q for q in ent.q_rad if q == q) / 1e4:.0f} radiative",
         "altitude_km": round(ent.peak_g_altitude / 1e3, 1), "time_s": round(float(ent.t[int(ent.decel_g.argmax())]), 1),
         "tag": "K"},
        {"step": 4, "name": "Pilot chute (mortar), main parachute %.0f m opens near Mach 0.9" % b.chute_D,
         "altitude_km": round(res["h_chute"] / 1e3, 1), "speed_m_s": round(float(ent.V[-1]), 0),
         "time_s": round(t_chute_end, 0), "tag": "K",
         "load": "unreefed main at 200 m/s would give ~27 kN (~12 g); staged/reefed opening keeps it ≤ 5 g [Y]",
         "decision": "g-trigger + timer fire the pilot (DAVINCI practice)", "abort": "none possible: chute failure = loss"},
        {"step": 5, "name": "Heat-shield jettison", "altitude_km": round(res["h_chute"] / 1e3 - 1.0, 1),
         "time_s": round(t_chute_end + 10.0, 0), "tag": "K/Y",
         "decision": "separation confirmed (accelerometer step, range sensor)",
         "abort": "no separation: stay on the chute as a descent probe (payload sensors, ~1 h of data)"},
        {"step": 6, "name": "Rotorcraft lowered 10 m on bridle; arms, blades and solar petals unfold (springs)",
         "altitude_km": round(h_unfold / 1e3, 1), "time_s": round(t_unfold, 0), "tag": "K/Y",
         "attitude": "hangs vertical; pendulum period 6.7 s; swing < 0.3° in measured shear + gusts (Monte Carlo)",
         "decision": "12 latch sensors (6 arm hinges × 2)", "abort": "≥ 2 arms unlatched: descent-probe mode"},
        {"step": 7, "name": "Rotors spun up to hover rpm while hanging (Dragonfly practice)",
         "altitude_km": round(h_spin / 1e3, 1), "time_s": round(t_spin, 0), "tag": "K/Y",
         "load": "flat collective (no thrust on the bridle); spin-up ~2.3 s per rotor; alternating spins cancel torque",
         "decision": "rpm + current check on all 6 motors", "abort": "≤ 4 healthy motors: descent-probe mode"},
        {"step": 8, "name": f"Release at {chute.V_end:.0f} m/s descent; pull-out in {dep.t_arrest_s:.1f} s, "
                            f"{dep.altitude_loss_m:.0f} m lost (forward flight through vortex-ring band)",
         "altitude_km": b.release_km, "time_s": round(t_rel, 0), "tag": "K",
         "load": "collective to 1.6× weight: 0.6 g net upward", "attitude": "pitch forward to 2 v_h airspeed within 2 s",
         "decision": "release window 63-60 km, descent < 16 m/s, battery > 90 %",
         "abort": "window missed: stay on the chute to 58 km, then descent-probe mode; after release, loss > 300 m "
                  "-> full collective + forward flight"},
        {"step": 9, "name": "Descend at 3 m/s to the 55 km cruise level; begin air-mass-frame science loiter",
         "altitude_km": b.cruise_km, "time_s": round(t_cruise, 0), "tag": "K"},
        {"step": 10, "name": f"Solar-sustained flight ~{run.solar_sustained_s / 3600:.0f} h, science dives to 51 km",
         "altitude_km": b.cruise_km, "time_s": round(t_cruise + 3600.0, 0), "tag": "K"},
        {"step": 11, "name": "Sunset: final dive measuring through the lower cloud until battery empty/too hot",
         "altitude_km": round(float(run.z[-1]) / 1e3, 1), "time_s": round(t_cruise + run.flight_time_s, 0), "tag": "K"},
        {"step": 12, "name": "No landing: unpowered fall with windmilling rotors (~12 h to the surface, < 1 m/s); "
                             "electronics pass 125 °C near 34 km; the vehicle reaches the surface as debris",
         "altitude_km": 0.0, "time_s": None, "tag": "K"},
    ]
    doc = {
        "schema": "venus_rotorcraft_design/1",
        "version": DESIGN_VERSION,
        "status": DESIGN_STATUS,
        "name": "VESPER — Venus Solar-Electric Powered Exploration Rotorcraft",
        "note": "Generated by aerokit.venus (sizing loop + BEMT + entry/descent + mission simulation). Tags: D read "
                "from primary data in this session, D-ag read by a research agent, K computed, Y assumption. "
                "Geometry/masses are design-study values; ids and keys are stable.",
        "frame": "origin body centre; x forward (between arms 1 and 6), y left, z up; metres; hover, arms deployed",
        "atmosphere": {
            "source": "40-64 km: Pioneer Venus 4-probe mean of T, p, rho; wind = mean of the probes with a DLBI "
                      "sample within +-0.5 km (2-4 probes; 4-probe interpolation is 0-2.4 m/s lower) (PDS raw "
                      "tables, 04_Venus/scripts/venus_pds_extract.py),"
                      " bands = probe envelope (wind band widened ±10 m/s); outside: aerokit.planetary (VIRA-like "
                      "table via Wikipedia). Speed of sound from NIST CO2 Cp (aerokit.venus.gas).",
            "profile": profile,
            "solar_fraction_note": "solar_fraction_down: Landis & Haag 2013 Table 1 (via agent) 40-60 km, PV LSFR "
                                   "shape 60-64 km, Landis 2002 anchors above; overhead sun",
            "cloud_layers": [dict(c, tag="D-ag (Titov et al. 2018)") for c in A.CLOUD_LAYERS],
            "vertical_wind_54km": A.VERTICAL_WIND,
        },
        "operating_band": {"min_km": 53, "nominal_km": b.cruise_km, "max_km": 58, "tag": "K",
                           "rationale": f"55 km: {st.T - 273.15:.0f} °C, {st.p / 1e5:.2f} bar, ρ {st.rho:.3f} kg/m³ "
                                        "(PV mean); battery charge window 0-45 °C holds at 53-58 km; solar per unit "
                                        "hover power is flat 55-62 km; dives to 51 km thermally limited"},
        "vehicle": {
            "total_mass_kg": round(d.gross_kg, 2),
            "rotor": {"count": 6, "coaxial": False, "diameter_m": d.D, "blades": d.rotor.blades,
                      "rpm": round(hp.rpm, 0), "arm_radius_m": round(d.arm_m, 3), "hub_height_m": 0.30,
                      "folding": True, "duct": False, "root_chord_m": round(d.rotor.root_chord, 4),
                      "tip_chord_m": round(d.rotor.tip_chord, 4), "twist_deg": d.rotor.twist_deg,
                      "collective_75_deg": round(d.rotor.theta75_deg, 2), "tip_speed_m_s": d.V_tip,
                      "tip_mach_55km": round(hp.per_rotor.tip_mach, 3), "reynolds_75": round(hp.per_rotor.re75, -3),
                      "figure_of_merit": round(hp.FM, 3), "solidity": round(d.rotor.solidity, 4),
                      "disk_area_total_m2": round(d.system.disk_area, 3),
                      "disk_loading_N_m2": round(hp.weight_N / d.system.disk_area, 2),
                      "spin": ["ccw", "cw", "ccw", "cw", "ccw", "cw"],
                      "arm_azimuths_deg": [30, 90, 150, 210, 270, 330], "tag": "K"},
            "body": {"shape": "cylinder", "length_m": b.body_d, "width_m": b.body_d, "height_m": b.body_h,
                     "tag": "Y"},
            "envelope": None,
            "solar": {"area_m2": round(d.solar_area_m2, 3), "placement": "body_top", "bifacial": True,
                      "shape": "hexagon", "circumradius_m": round(deck_rc, 3), "tag": "K"},
            "span_m": round(2 * d.arm_m + d.D, 3),
            "stowed": {"diameter_m": round(b.body_d + 2 * 0.45, 2), "height_m": round(d.arm_m / 2 + b.body_h + 0.3, 2),
                       "arm_fold": "Z-fold: hinge at the body (down) and at mid-arm (back up); 2 folds per arm",
                       "blade_fold": "blades fold back along the outer arm segment (passive, centrifugal deploy)",
                       "solar_fold": "6 triangular petals hinged at the body rim fold up against the vessel",
                       "fits": "3.7 m 45° aeroshell (Landis: a 9 m-span airplane folded into a 3.7 m shell [D-ag])",
                       "note": "concept-level packaging estimate; the visual session's folded 3-D model measures "
                               "1.57 x 2.12 m (petals above the vessel, motor pods at the outer-arm tips) — still "
                               "inside the 3.7 m aeroshell", "tag": "Y"},
            "performance_55km": {"hover_electric_W": round(d.P_hover_elec_W, 0),
                                 "loiter_electric_W": round(d.P_bucket_elec_W, 0),
                                 "loiter_airspeed_m_s": round(d.V_bucket, 1),
                                 "solar_overhead_W": round(d.P_solar_overhead_W, 0),
                                 "solar_sustains_loiter_above_mu0": round(d.sustain_mu0_loiter or float("nan"), 3),
                                 "battery_Wh": round(d.battery_Wh, 0), "tag": "K"},
            "components": comps,
        },
        "entry": {
            "aeroshell_diameter_m": b.aeroshell_D, "aeroshell_shape": "45° sphere-cone, rigid (ADEPT deployable as option)",
            "entry_mass_kg": round(res["m_entry"], 1), "ballistic_coefficient_kg_m2": round(res["entry_vehicle"].beta, 1),
            "entry_speed_km_s": round(res["VE"] / 1e3, 3), "entry_altitude_km": b.entry_altitude / 1e3,
            "entry_flight_path_deg": b.gamma_deg, "peak_deceleration_g": round(ent.peak_g, 1),
            "peak_heat_flux_W_cm2": {"convective_sutton_graves": round(ent.peak_q / 1e4, 0),
                                     "radiative_tauber_2012": round(max(q for q in ent.q_rad if q == q) / 1e4, 0)},
            "heat_load_kJ_cm2": round(ent.heat_load / 1e7, 2),
            "parachute_deploy_km": round(res["h_chute"] / 1e3, 1),
            "heatshield_jettison_km": round(res["h_chute"] / 1e3 - 1.0, 1),
            "parachute_diameter_m": b.chute_D, "suspended_mass_kg": round(res["m_suspended"], 1),
            "time_on_parachute_s": round(chute.duration_s, 0),
            "rotor_spinup_km": round(h_spin / 1e3, 1), "spinup_time_s": 60.0,
            "release_km": b.release_km, "release_descent_rate_m_s": round(chute.V_end, 1),
            "pullout_altitude_loss_m": round(dep.altitude_loss_m, 0),
            "pullout_altitude_loss_if_dropped_unspun_m": round(res["deploy_drop"].altitude_loss_m, 0),
            "mass_budget_kg": {k: round(v, 1) for k, v in res["entry_system"].items()},
            "tag": "K (masses: Landis 2026 fractions [D-ag]; v_inf, chute size [Y])",
        },
        "deployment_sequence": zones,
        "operations": {"drift_speed_m_s": round(A.zonal_wind(b.cruise_km * 1e3), 1),
                       "circumnavigation_days": round(2 * math.pi * (6051.8e3 + b.cruise_km * 1e3)
                                                      / A.zonal_wind(b.cruise_km * 1e3) / 86400.0, 2),
                       "mission_days": round(run.flight_time_s / 86400.0, 2),
                       "solar_sustained_hours": round(run.solar_sustained_s / 3600.0, 1),
                       "drift_distance_km": round(float(run.x[-1]) / 1e3, 0),
                       "release_hour_angle_deg": round(res["release_hour_angle_deg"], 1),
                       "events": [{"t_h": round(t / 3600.0, 2), "event": e, "kind": _event_kind(e),
                                   "altitude_km": round(float(np.interp(t, run.t, run.z)) / 1e3, 2)}
                                  for t, e in run.events],
                       "series_hourly": series, "tag": "K"},
    }
    return doc
