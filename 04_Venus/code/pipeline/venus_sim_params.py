"""Simulator-ready parameter file for LuGus (Liftoff Core / Unity): ``04_Venus/outputs/sim_params.json``.

    python 04_Venus/code/pipeline/venus_sim_params.py

Every scalar is ``{"value", "unit", "tag", "source"}`` (tags: D primary data read in this session, D-ag read by a
research agent, K computed by aerokit.venus, Y assumption). Tables (atmosphere, wind, solar, rotor curve) carry one
unit/tag/source block per column. Built from the same code as docs/25 (``aerokit.venus``), so it changes only when
the design does. A README sits next to it (``sim_params_README.md``).
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit import planetary as P  # noqa: E402
from aerokit.venus import atmosphere as A  # noqa: E402
from aerokit.venus import bemt as B  # noqa: E402
from aerokit.venus import control as CT  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402
from aerokit.venus import gas  # noqa: E402
from aerokit.venus import power as PW  # noqa: E402
from aerokit.venus import thermal as TH  # noqa: E402

OUT = ROOT / "04_Venus" / "outputs" / "sim_params.json"


def v(value, unit: str, tag: str, source: str) -> dict:
    if isinstance(value, float):
        value = round(value, 6)
    return {"value": value, "unit": unit, "tag": tag, "source": source}


def build() -> dict:
    res = DES.baseline()
    d = res["design"]
    doc = DES.design_document()
    h0 = DES.BASELINE.cruise_km * 1e3
    s0 = A.state(h0)
    fl0 = B.FlowState(s0.rho, s0.mu, s0.a)
    W0 = d.gross_kg * s0.g

    # atmosphere 40-64 km (probe data) every 0.5 km, outside: VIRA-like table 30-80 km
    alts = np.arange(30.0, 80.01, 0.5)
    cols = {k: [] for k in ("altitude_m", "temperature_K", "pressure_Pa", "density_kg_m3", "density_low", "density_high",
                            "speed_of_sound_m_s", "viscosity_Pa_s", "gravity_m_s2", "wind_west_mean_m_s",
                            "wind_west_low_m_s", "wind_west_high_m_s", "solar_array_overhead_W_m2", "up_down_ratio")}
    for km in alts:
        h = km * 1e3
        inside = A.Z_MIN <= h <= A.Z_MAX
        if inside:
            s, lo, hi = A.state(h), A.state(h, "min").rho, A.state(h, "max").rho
            T, p, rho, g = s.T, s.p, s.rho, s.g
            wl, wm, wh = A.zonal_wind_band(h)
            ud = A.solar_ratio_up_down(h)
        else:
            t = P.venus_atmosphere(h)
            T, p, rho, g, lo, hi = t.T, t.p, t.rho, t.g, None, None
            wm = P.venus_zonal_wind(h)
            wl = wh = None
            ud = None
        sol = PW.array_output_overhead(h, d.req.solar_efficiency) if 40.0 <= km <= 64.0 else None
        for k, x in (("altitude_m", h), ("temperature_K", T), ("pressure_Pa", p), ("density_kg_m3", rho),
                     ("density_low", lo), ("density_high", hi), ("speed_of_sound_m_s", gas.speed_of_sound(T)),
                     ("viscosity_Pa_s", gas.viscosity(T)), ("gravity_m_s2", g), ("wind_west_mean_m_s", wm),
                     ("wind_west_low_m_s", wl), ("wind_west_high_m_s", wh), ("solar_array_overhead_W_m2", sol),
                     ("up_down_ratio", ud)):
            cols[k].append(None if x is None else float(f"{float(x):.6g}"))
    col_meta = {
        "altitude_m": ("m", "K", "grid"),
        "temperature_K": ("K", "D/D(secondary)", "40-64 km: Pioneer Venus 4-probe mean (PDS raw tables); outside: VIRA-like table via Wikipedia"),
        "pressure_Pa": ("Pa", "D/D(secondary)", "as temperature"),
        "density_kg_m3": ("kg/m^3", "D/D(secondary)", "as temperature"),
        "density_low": ("kg/m^3", "D", "probe envelope minimum (40-64 km only)"),
        "density_high": ("kg/m^3", "D", "probe envelope maximum (40-64 km only)"),
        "speed_of_sound_m_s": ("m/s", "K from D", "ideal gas with NIST Cp of 96.5 % CO2 + 3.5 % N2"),
        "viscosity_Pa_s": ("Pa s", "D", "NIST WebBook CO2 at 0.1 MPa"),
        "gravity_m_s2": ("m/s^2", "K", "8.87 (R/(R+h))^2"),
        "wind_west_mean_m_s": ("m/s", "D/D-ag", "40-64 km: PV DLBI, mean of the probes with a sample within +-0.5 km (2-4 probes; 4-probe interpolation is 0-2.4 m/s lower, R_audit_2026-11-04); outside: Landis anchors, linear [Y]"),
        "wind_west_low_m_s": ("m/s", "D+Y", "probe minimum − 10 m/s"),
        "wind_west_high_m_s": ("m/s", "D+Y", "probe maximum + 10 m/s"),
        "solar_array_overhead_W_m2": ("W/m^2", "D-ag+K", "Landis & Haag 2013 Table 1 (29 % array), LSFR shape above 60 km"),
        "up_down_ratio": ("-", "D", "Pioneer Venus LSFR upward/downward flux (COMBINED channel)"),
    }
    atmosphere = {"columns": {k: {"unit": u, "tag": t, "source": src} for k, (u, t, src) in col_meta.items()},
                  "rows": cols,
                  "sun_angle_law": v("P(mu0) = P(1) * mu0 (mu0 + 2/3) / (5/3)", "-", "Y", "Eddington-type in-cloud law"),
                  "vertical_gust_sigma": v(0.7, "m/s", "D-ag", "VEGA balloons at 53-54 km (sd 0.65-0.75), A_vega1985 note"),
                  "vertical_gust_correlation": v(80.0, "s", "Y", "inside the measured 30-130 s periods"),
                  "horizontal_gust_sigma": v(1.0, "m/s", "Y", "VEGA fluctuations up to 1-2 m/s x 1.5 (D-ag)"),
                  "downdraft_episode": v({"speed": [-2.0, -3.3], "duration_h": 2.0, "altitude_loss_km": 2.9}, "m/s, h, km",
                                         "D-ag", "VEGA-2 event, A_vega1985 note"),
                  "meridional_wind_max": v(7.5, "m/s", "D-ag", "PV DLBI |v| <= ~7.5 m/s at 45-62 km, typically 1-5 (A_counselman1980 note)")}

    # vehicle
    sim = json.loads((ROOT / "04_Venus" / "outputs" / "vesper_for_simulator.json").read_text())
    rotor_curve = []
    om_h = d.hover.per_rotor.omega
    for f in np.linspace(0.3, 1.6, 27):
        r = B.solve(d.rotor, om_h * f, fl0)
        rotor_curve.append({"rpm": round(om_h * f * 30 / math.pi, 2), "thrust_N": round(r.thrust, 3),
                            "torque_Nm": round(r.torque * d.system.bemt_power_factor, 4),
                            "shaft_W": round(r.power * d.system.bemt_power_factor, 2)})
    Zw = CT.heave_derivative(d.system, W0, fl0)
    vehicle = {
        "mass": v(d.gross_kg, "kg", "K", "aerokit.venus.sizing.close"),
        "cg": v(sim["cg_m"], "m", "K", "component layout in design.json"),
        "inertia": v(sim["inertia_kg_m2"], "kg m^2", "K", "point masses + rods from design.json"),
        "drag_area": v(d.system.drag_area_m2, "m^2", "Y", "airframe C_D A"),
        "rotors": {"positions": v([r["position_m"] for r in sim["rotors"]], "m", "K", "arm radius x azimuth 30+60 i deg"),
                   "spin": v([r["spin"] for r in sim["rotors"]], "-", "Y", "alternating"),
                   "radius": v(d.rotor.radius, "m", "K", "trade + robustness study"),
                   "blades": v(d.rotor.blades, "-", "Y", "2-blade folding"),
                   "polar_inertia": v(sim["rotors"][0]["polar_inertia_kg_m2"], "kg m^2", "K", "blade rods"),
                   "collective_hover": v(d.rotor.theta75_deg, "deg", "K", "BEMT trim at 55 km"),
                   "curve_at_55km": {"rows": rotor_curve, "unit": "rpm, N, N m, W", "tag": "K",
                                     "source": "BEMT (validated vs Knight & Hefner / Harrington, torque rms 6.3 %)",
                                     "density_scaling": "thrust and torque scale with density at fixed rpm and pitch "
                                                        "(C_T, C_Q constant): multiply by rho(h)/rho(55 km)"},
                   "heave_derivative": v(Zw, "N/(m/s)", "K", "BEMT dT/dw at fixed rpm, pitch (whole vehicle)"),
                   "vortex_ring_band": v([0.5, 1.5], "x v_h descent", "Y", "helicopter practice; thrust -20 % inside, "
                                         "unless airspeed > v_h"),
                   "v_h_55km": v(d.hover.v_h, "m/s", "K", "momentum theory per rotor")},
        "drive": {"gear_ratio": v(5.0, "-", "Y", "sealed planetary (robustness study)"),
                  "motor_efficiency": v(d.system.motor_efficiency, "-", "Y", "motor x gearbox"),
                  "esc_efficiency": v(d.system.esc_efficiency, "-", "Y", ""),
                  "max_thrust_ratio": v(d.req.thrust_margin, "x weight", "D-ag+Y", "MSH >= 1.4 (40 % margin)"),
                  "rpm_response_20pct": v(CT.rpm_response_time(CT.blade_inertia(
                      (d.breakdown["blades+hubs"] / 6 - 0.12) / 2, d.rotor.radius, 2), om_h,
                      0.6 * d.hover.per_rotor.torque), "s", "K", "rotor inertia / spare torque"),
                  "collective_actuator_tau": v(0.1, "s", "Y", "per-rotor pitch actuator")},
        "power": {"battery_capacity": v(d.battery_Wh, "Wh", "K", "0.5 h hover reserve"),
                  "solar_area": v(d.solar_area_m2, "m^2", "K", "hexagon deck"),
                  "solar_efficiency": v(d.req.solar_efficiency, "-", "D-ag", "29 % AM0 array (Landis & Haag)"),
                  "bifaciality": v(0.85, "-", "Y", ""), "coating_loss": v(0.05, "-", "D-ag", "Parylene acid test"),
                  "system_load": v(d.P_sys_W, "W", "Y", "payload 30 W + avionics 25 W"),
                  "hover_electric_55km": v(d.P_hover_elec_W, "W", "K", "BEMT"),
                  "loiter_electric_55km": v(d.P_bucket_elec_W, "W", "K", "momentum + BEMT calibration"),
                  "loiter_airspeed": v(d.V_bucket, "m/s", "K", "minimum-power speed")},
        "thermal": {"vessel_heat_capacity": v(TH.Vessel().interior_heat_capacity_J_K, "J/K", "Y", ""),
                    "insulation_conductance": v(TH.Vessel().G_ins, "W/K", "Y", "10 mm aerogel"),
                    "heat_pipe_conductance_max": v(TH.Vessel().G_max_W_K, "W/K", "Y", "diode VCHP"),
                    "interior_at_55km": v(TH.vessel_steady(TH.Vessel(), h0, 80.0)[0], "degC", "K", "80 W inside")},
    }
    limits = [
        {"name": "battery charge window", **v([0.0, 45.0], "degC", "D-ag", "Panasonic NCR18650B datasheet")},
        {"name": "battery discharge window", **v([-20.0, 60.0], "degC", "D-ag", "Panasonic NCR18650B datasheet")},
        {"name": "electronics", **v([-40.0, 125.0], "degC", "D-ag", "AEC-Q100 grade 1")},
        {"name": "magnets (Sm2Co17)", **v(300.0, "degC", "D-ag", "manufacturer data")},
        {"name": "tip Mach cap", **v(0.7, "-", "D-ag/Y", "Ingenuity-like")},
        {"name": "advance ratio for the momentum model", **v(0.43, "-", "K", "model valid to ~30 m/s"),
         "note": "station keeping at the wind speed would need mu 0.7-1.2"},
        {"name": "max airspeed", **v(sim["max_airspeed_m_s"], "m/s", "K", "level-flight speed whose shaft power stays below 1.6^1.5 x hover shaft power")},
        {"name": "entry deceleration qualification", **v(100.0, "g", "Y", "peak 56 g, x1.8")},
        {"name": "acid exposure tested (FEP)", **v(168.0, "h", "D-ag", "manufacturer test, conc. H2SO4 at 120 degC")},
        {"name": "operating altitude band", **v([53.0, 58.0], "km", "K", "battery charge window + power")},
        {"name": "science dive floor", **v(51.0, "km", "K", "battery 57 degC peak at 51 km")},
    ]
    failure_modes = [
        {"name": "motor out", "trigger": "one motor fails (2 % per deployment in the Monte Carlo [Y])",
         "effect": "thrust margin 1.6 -> 1.6 x 5/6 = 1.33; yaw trim by the opposite pair",
         "recovery": "continue on 5 rotors", "tag": "Y/K"},
        {"name": "vortex ring state", "trigger": "descent 0.5-1.5 v_h with airspeed < v_h",
         "effect": "thrust -20 %, oscillation", "recovery": "pitch forward to 2 v_h airspeed", "tag": "Y"},
        {"name": "downdraft", "trigger": "-2..-3.3 m/s for ~2 h (VEGA-2)", "effect": "+1.4 kW to hold altitude",
         "recovery": "ride it within 51-58 km, climb back (0.4 kWh)", "tag": "D-ag/K"},
        {"name": "battery hot", "trigger": "interior > 50 degC during a dive", "effect": "charging stops above 45 degC",
         "recovery": "abort the dive and climb", "tag": "K"},
        {"name": "battery over discharge limit", "trigger": "interior > 60 degC", "effect": "end of controlled flight",
         "recovery": "none (end of mission)", "tag": "D-ag/K"},
        {"name": "sun too low", "trigger": "cos zenith < 0.595 at 55 km", "effect": "battery drains at ~1.3 kW",
         "recovery": "~0.8 h on battery, then sunset dive", "tag": "K"},
        {"name": "night", "trigger": "cos zenith <= 0", "effect": "0 W solar; 1.04 kWh vs ~103 kWh needed (loiter power x half the 154 h air-mass day)",
         "recovery": "none for a pure rotorcraft (helium hybrid only)", "tag": "K"},
        {"name": "deployment latch failure", "trigger": ">= 2 arms unlatched or <= 4 healthy motors",
         "effect": "no release", "recovery": "descent-probe mode on the parachute", "tag": "Y"},
        {"name": "acid degradation", "trigger": "exposure beyond tested 96-168 h", "effect": "cell/coating loss",
         "recovery": "mission ends at ~49 h anyway", "tag": "D-ag/Y"},
    ]
    return {"schema": "vesper_sim_params/1", "version": doc["version"],
            "generated_by": "python 04_Venus/code/pipeline/venus_sim_params.py",
            "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="minutes"),
            "units": "SI unless stated; temperatures K in tables, degC in limits",
            "frame": "body: x forward (between arms 1 and 6), y left, z up; world: x east, z up; wind blows westward "
                     "(negative x) at the tabulated speed",
            "atmosphere_and_wind": atmosphere, "vehicle": vehicle, "limits": limits, "failure_modes": failure_modes,
            "deployment_replay": {"rows": sim["deployment_replay"], "unit": "s, m, m/s (descent positive)", "tag": "K"},
            "mission_series": {"rows": sim["mission_series"], "unit": "h, km, Wh, W, -, degC", "tag": "K"}}


def main(argv: list[str]) -> int:
    doc = build()
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} kB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
