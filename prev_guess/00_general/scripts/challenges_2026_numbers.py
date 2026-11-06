"""Numbers for the 2026 challenge playbooks (Venus drones, approach guidance, accident investigation).

Every table in docs/17-20 that carries a computed number comes from this script. It writes

* ``prev_guess/00_general/challenges_2026/numbers.json`` — all values, with the inputs that produced them;
* ``prev_guess/00_general/challenges_2026/tables.md`` — the same values as Markdown tables (datawiz ``markdown_tablo``);
* ``prev_guess/00_general/challenges_2026/table_audit.txt`` — the ``tablo.denetle`` findings for every table.

Usage::

    python prev_guess/00_general/scripts/challenges_2026_numbers.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from datawiz import tablo  # noqa: E402

from aerokit import approach as A  # noqa: E402
from aerokit import investigation as I  # noqa: E402
from aerokit import planetary as P  # noqa: E402
from aerokit.aero.atmosphere import isa  # noqa: E402
from aerokit.design import electric as E  # noqa: E402

OUT = ROOT / "prev_guess" / "00_general" / "challenges_2026"
TABLES: list[tuple[str, str, pd.DataFrame, dict]] = []
DATA: dict[str, object] = {}


def table(key: str, title: str, df: pd.DataFrame, **kw: object) -> None:
    TABLES.append((key, title, df, kw))
    DATA[key] = df.to_dict(orient="records")


# ----------------------------------------------------------------------------- Venus
def venus() -> None:
    rows = []
    for km in (0, 20, 40, 45, 50, 52.5, 55, 57.5, 60, 65, 70):
        s = P.venus_atmosphere(km * 1e3)
        rows.append({"Altitude": km, "Temperature": s.T - 273.15, "Pressure": s.p / 1e5, "Density": s.rho,
                     "Gravity": s.g, "Density vs Earth SL": s.rho / 1.225})
    table("venus_atmosphere", "The 50–60 km band has Earth-like pressure and temperature; the surface is 53× denser "
          "than Earth sea level", pd.DataFrame(rows),
          birimler={"Altitude": "km", "Temperature": "°C", "Pressure": "bar", "Density": "kg/m³",
                    "Gravity": "m/s²", "Density vs Earth SL": "×"},
          ondaliklar={"Altitude": 1, "Temperature": 0, "Pressure": 3, "Density": 3, "Gravity": 2,
                      "Density vs Earth SL": 2})

    rows = []
    for name, M in (("Hydrogen", P.M_H2), ("Helium", P.M_HE), ("Earth air (N2/O2)", P.M_AIR_EARTH),
                    ("Nitrogen", P.M_N2)):
        for km in (50, 55, 60):
            lift = P.buoyant_lift_per_m3(km * 1e3, M)
            rows.append({"Gas": name, "Altitude": km, "Net lift": lift / P.venus_gravity(km * 1e3),
                         "Volume for 100 kg": P.balloon_volume(100.0, km * 1e3, M),
                         "Sphere diameter": (6 * P.balloon_volume(100.0, km * 1e3, M) / math.pi) ** (1 / 3)})
    table("venus_buoyancy", "Hydrogen and helium lift ~0.9 kg/m³ at 55 km; even Earth air floats", pd.DataFrame(rows),
          birimler={"Altitude": "km", "Net lift": "kg/m³", "Volume for 100 kg": "m³", "Sphere diameter": "m"},
          ondaliklar={"Altitude": 0, "Net lift": 2, "Volume for 100 kg": 0, "Sphere diameter": 1})

    rows = []
    cases = (("Earth sea level", 1.225, 9.80665), ("Venus 65 km", P.venus_atmosphere(65e3).rho,
                                                    P.venus_gravity(65e3)),
             ("Venus 55 km", P.venus_atmosphere(55e3).rho, P.venus_gravity(55e3)),
             ("Venus 40 km", P.venus_atmosphere(40e3).rho, P.venus_gravity(40e3)),
             ("Venus surface", P.venus_atmosphere(0).rho, P.VENUS_G0))
    for name, rho, g in cases:
        p = E.hover_power(5.0 * g, rho, 0.5, 0.7)
        rows.append({"Case": name, "Density": rho, "Gravity": g, "Hover power": p, "Specific power": p / 5.0})
    table("venus_hover", "Hovering 5 kg on rotors of 0.5 m² (FM 0.7) costs about the same at 55 km as on Earth "
          "and 8.5× less at the surface", pd.DataFrame(rows),
          birimler={"Density": "kg/m³", "Gravity": "m/s²", "Hover power": "W", "Specific power": "W/kg"},
          ondaliklar={"Density": 3, "Gravity": 2, "Hover power": 0, "Specific power": 0})

    rows = []
    s55 = P.venus_atmosphere(55e3)
    for e_whkg in (150, 250):
        for t_min in (10, 20, 30, 60):
            for payload in (0.5, 2.0):
                try:
                    sz = E.size_multirotor(payload, t_min * 60, 4, 0.6, specific_energy_J_kg=e_whkg * 3600,
                                           efficiency=0.7, figure_of_merit=0.65, empty_fraction=0.5,
                                           rho=s55.rho, g=s55.g)
                    m, pw = sz.mass, sz.hover_power
                except ValueError:
                    m, pw = float("nan"), float("nan")
                rows.append({"Pack energy": e_whkg, "Hover time": t_min, "Payload": payload, "Take-off mass": m,
                             "Hover power": pw})
    table("venus_multirotor", "At 55 km a battery quadrotor (4 × 0.6 m rotors) carries 2 kg for 20–30 min; a full hour "
          "works only with 0.5 kg at 250 Wh/kg (— = no solution)", pd.DataFrame(rows),
          birimler={"Pack energy": "Wh/kg", "Hover time": "min", "Payload": "kg", "Take-off mass": "kg",
                    "Hover power": "W"},
          ondaliklar={"Pack energy": 0, "Hover time": 0, "Payload": 1, "Take-off mass": 1, "Hover power": 0})

    rows = []
    for mass, span_area, cl in ((10.0, 2.0, 0.8), (50.0, 6.0, 0.8)):
        for km in (50, 55, 60, 65):
            s = P.venus_atmosphere(km * 1e3)
            v = P.level_flight_speed(mass, span_area, cl, s.rho, s.g)
            rows.append({"Mass": mass, "Wing area": span_area, "Altitude": km, "Speed": v,
                         "Power at L/D 15": P.level_flight_power(mass, v, 15.0, 0.6, s.g),
                         "Solar in on wing": P.VENUS_SOLAR_FLUX_TOP * span_area * 0.2})
    table("venus_aeroplane", "A 10 kg solar aeroplane at 55–65 km needs 0.1–0.2 kW; above the clouds 2 m² of 20 % "
          "cells give ~1 kW (before attenuation, cosine and night)", pd.DataFrame(rows),
          birimler={"Mass": "kg", "Wing area": "m²", "Altitude": "km", "Speed": "m/s", "Power at L/D 15": "W",
                    "Solar in on wing": "W"},
          ondaliklar={"Mass": 0, "Wing area": 0, "Altitude": 0, "Speed": 1, "Power at L/D 15": 0,
                      "Solar in on wing": 0})

    venus_environment_file()
    lo, hi = P.light_time_bounds()
    DATA["venus_scalars"] = {
        "circumnavigation_days_100ms_60km": P.circumnavigation_time(100.0, 60e3) / 86400,
        "circumnavigation_days_60ms_55km": P.circumnavigation_time(60.0, 55e3) / 86400,
        "light_time_min_minutes": lo / 60, "light_time_max_minutes": hi / 60,
        "altitude_1bar_km": P.altitude_for_pressure(1e5) / 1e3,
        "altitude_0C_km": P.altitude_for_temperature(273.15) / 1e3,
        "altitude_125C_km": P.altitude_for_temperature(398.15) / 1e3,
        "altitude_300C_km": P.altitude_for_temperature(573.15) / 1e3,
        "solar_day_days": P.VENUS_SOLAR_DAY_S / 86400,
    }


def venus_environment_file() -> None:
    """1 km environment table for a simulator (Unity / Liftoff Core), every field with its source."""
    gamma = 1.286          # Venus atmosphere, Young et al. 2026 Table 2 (via the research agent)
    r_spec = P.R_UNIVERSAL / P.M_VENUS
    rows = []
    for km in range(101):
        s = P.venus_atmosphere(km * 1e3)
        w = P.venus_zonal_wind(km * 1e3)
        light = P.venus_solar_fraction(km * 1e3) if km >= P.SOLAR_FRACTION_ANCHORS[0][0] else None
        rows.append({"altitude_km": km, "temperature_K": round(s.T, 2), "pressure_Pa": round(s.p, 3),
                     "density_kg_m3": round(s.rho, 5), "gravity_m_s2": round(s.g, 4),
                     "speed_of_sound_m_s": round(math.sqrt(gamma * r_spec * s.T), 1),
                     "zonal_wind_m_s": round(w, 1), "solar_fraction_down": None if light is None else round(light, 3)})
    env = {
        "description": "Venus reference environment for simulation, 0-100 km, equatorial, day side",
        "generated_by": "prev_guess/00_general/scripts/challenges_2026_numbers.py (aerokit.planetary)",
        "sources": {
            "temperature_K, pressure_Pa": "Wikipedia 'Atmosphere of Venus' table (VIRA values), read 2026-11-03; "
                                          "linear T and ln p between 5-10 km nodes",
            "density_kg_m3": "ideal gas, M = 43.45 g/mol (96.5 % CO2, 3.5 % N2); a few % high at the surface",
            "gravity_m_s2": "8.87 m/s2 at the surface (Wikipedia 'Venus'), inverse square with altitude",
            "speed_of_sound_m_s": "sqrt(gamma R T) with gamma = 1.286 from Young et al. 2026 Table 2 (read by the "
                                  "research agent, not by us); gamma of CO2 varies with T, so treat as approximate",
            "zonal_wind_m_s": "anchors 45 km 44.5, 53 km 65, 54 km 67, 60 km 100, 67 km 95 m/s (Landis 2001/2002, "
                              "VAPS 2018 via the research agent); surface 0.5 m/s (0.3-1); LINEAR INTERPOLATION "
                              "between anchors and constant above 67 km is OUR ASSUMPTION, not data",
            "solar_fraction_down": "20-50 % at the cloud base (~50 km, 0.35 used), ~95 % at 65 km (Landis 2002 via the "
                                   "research agent); linear between, 1.0 above 65 km assumed; null below 50 km = not "
                                   "sourced (surface sunlight figures are snippet-only)",
        },
        "constants": {"solar_flux_top_W_m2": P.VENUS_SOLAR_FLUX_TOP, "solar_day_earth_days": 116.75,
                      "light_time_one_way_min_s": P.light_time_bounds()[0],
                      "light_time_one_way_max_s": P.light_time_bounds()[1], "gamma": gamma,
                      "specific_gas_constant_J_kgK": r_spec},
        "not_modelled": ["turbulence and gusts (no source found)", "meridional wind", "latitude and day/night "
                         "variation", "sulfuric-acid droplet density"],
        "profile": rows,
    }
    (OUT / "venus_environment.json").write_text(json.dumps(env, indent=1), encoding="utf-8")
    DATA["venus_environment_file"] = str((OUT / "venus_environment.json").relative_to(ROOT))


# ----------------------------------------------------------------------------- approach
def approach() -> None:
    rows = []
    for ang in (3.0, 3.2, 4.5, 5.5):
        for gs_kt in (70, 90, 120, 140):
            vs = A.descent_rate(gs_kt * A.KT, ang) / A.FPM
            rows.append({"Path angle": ang, "Ground speed": gs_kt, "Descent rate": vs,
                         "Height per NM": 1852 * math.tan(math.radians(ang)) / A.FT,
                         "Above FSF 1000 fpm": "yes" if vs > 1000 else "no"})
    table("approach_descent", "A 5.5° approach breaks the FSF 1000 fpm line above ~103 kt ground speed; 3° only above "
          "~188 kt",
          pd.DataFrame(rows), birimler={"Path angle": "°", "Ground speed": "kt", "Descent rate": "fpm",
                                       "Height per NM": "ft"},
          ondaliklar={"Path angle": 1, "Ground speed": 0, "Descent rate": 0, "Height per NM": 0})

    rows = []
    for dT in (-10, -20, -30, -40):
        for ind_ft in (500, 1000, 2000, 3000):
            true = A.cold_temperature_true_height(ind_ft * A.FT, 0.0, dT) / A.FT
            rows.append({"ISA deviation": dT, "Indicated height": ind_ft, "True height": true,
                         "Aircraft low by": ind_ft - true})
    table("approach_cold", "At ISA−30 K a baro-VNAV aircraft indicating 1000 ft is ~104 ft low", pd.DataFrame(rows),
          birimler={"ISA deviation": "K", "Indicated height": "ft", "True height": "ft", "Aircraft low by": "ft"},
          ondaliklar={"ISA deviation": 0, "Indicated height": 0, "True height": 0, "Aircraft low by": 0})

    rows = []
    for nm in (10, 5, 2, 1, 0.6):
        for dd in (0.05, 0.1, 0.3):
            rows.append({"Range": nm, "Angle error": dd, "Position error": nm * 1852 * math.radians(dd)})
    table("approach_radar_angle", "A ground radar with 0.1° angle error is 3 m off at 1 NM but 32 m at 10 NM",
          pd.DataFrame(rows), birimler={"Range": "NM", "Angle error": "°", "Position error": "m"},
          ondaliklar={"Range": 1, "Angle error": 2, "Position error": 1})
    DATA["radar_range_resolution_m"] = {f"{b} MHz": 299_792_458.0 / (2 * b * 1e6) for b in (10, 50, 150, 500)}

    rwy = A.Runway(51.0, 3.0, 10.0, 262.0)
    cfg = A.ApproachSimConfig(x0=8000.0, y0=150.0, z0_above_path=60.0, wind_from_rel_deg=40.0, wind_speed=10.0,
                              gust_sigma=2.0)
    # radar error at the 200 ft gate (≈ 1.2 km from the radar sited near the threshold): R·δ per axis
    r_gate = 1200.0
    sensors = [
        A.NavSensor("Ideal (truth)"),
        A.NavSensor("SBAS LPV-like: σ 1.0/1.0/1.5 m", sigma=(1.0, 1.0, 1.5), tau=60.0),
        A.NavSensor("Baro-VNAV, ISA−30 K bias, σ 2 m", bias=(0.0, 0.0, 6.4), sigma=(3.0, 3.0, 2.0), tau=30.0),
        A.NavSensor("Ground radar 0.1° monopulse", sigma=(3.0, r_gate * math.radians(0.1), r_gate * math.radians(0.1)),
                    tau=2.0),
        A.NavSensor("Ground radar 0.3° (search-type)", sigma=(5.0, r_gate * math.radians(0.3),
                                                               r_gate * math.radians(0.3)), tau=2.0),
        A.NavSensor("Vision/INS, 2 % range-scaled", sigma=(10.0, 0.02 * r_gate, 0.02 * r_gate), tau=5.0),
    ]
    stats = A.monte_carlo_approach(rwy, sensors, gate_height=200 * A.FT, runs=200, cfg=cfg, seed=7)
    rows = [{"Navigation source": k, "Vertical mean": v["vertical_mean"],
             "Vertical P95 abs. dev.": v["vertical_p95_abs"], "Lateral P95 abs. dev.": v["lateral_p95_abs"]}
            for k, v in stats.items()]
    table("approach_montecarlo", "Deviation at the 200 ft gate (200 simulated runs each, 10 m/s wind at 40°, gusts "
          "σ 2 m/s): a 0.1° monopulse radar matches SBAS-like accuracy, ISA−30 K pulls baro-VNAV ~5 m low, a "
          "2 %-of-range vision fix is worst", pd.DataFrame(rows),
          birimler={"Vertical mean": "m", "Vertical P95 abs. dev.": "m", "Lateral P95 abs. dev.": "m"},
          ondaliklar={"Vertical mean": 1, "Vertical P95 abs. dev.": 1, "Lateral P95 abs. dev.": 1})
    DATA["approach_montecarlo_inputs"] = {
        "runway": "synthetic, 3° path, TCH 15.24 m, 2500 m", "x0_m": cfg.x0, "y0_m": cfg.y0,
        "z0_above_path_m": cfg.z0_above_path, "wind_ms": cfg.wind_speed, "wind_rel_deg": cfg.wind_from_rel_deg,
        "gust_sigma": cfg.gust_sigma, "runs": 200, "seed": 7,
        "baro_bias_note": "ISA−30 K at 200 ft above the station: indicated − true from the approach_cold model",
        "baro_bias_m": 200 * A.FT - A.cold_temperature_true_height(200 * A.FT, 0.0, -30.0)}

    rows = []
    for top_ft in (3000, 4000, 6000):
        for ang in (3.0, 3.2):
            rows.append({"Start height": top_ft, "Path angle": ang,
                         "Distance to threshold": A.distance_for_descent(top_ft * A.FT, ang) / 1852})
    table("approach_cda", "A continuous 3° descent from 6000 ft starts ~19 NM out", pd.DataFrame(rows),
          birimler={"Start height": "ft", "Path angle": "°", "Distance to threshold": "NM"},
          ondaliklar={"Start height": 0, "Path angle": 1, "Distance to threshold": 1})


# ----------------------------------------------------------------------------- investigation
def investigation() -> None:
    rows = []
    for h_ft, v_kt, label in ((35000, 480, "cruise FL350"), (10000, 250, "FL100")):
        for beta in (1, 10, 100, 1000, 5000):
            r = I.ballistic_trajectory(beta, h_ft * A.FT, v_kt * A.KT, wind_cross=20.0)
            rows.append({"Break-up": label, "Ballistic coefficient": beta, "Along track": r.impact_x / 1000,
                         "Wind drift": r.impact_y / 1000, "Fall time": r.time_of_fall / 60,
                         "Impact speed": r.impact_speed})
    table("debris", "Debris sorts itself by ballistic coefficient: from FL350 heavy parts land ~10 km ahead, light "
          "panels drift tens of km downwind", pd.DataFrame(rows),
          birimler={"Ballistic coefficient": "kg/m²", "Along track": "km", "Wind drift": "km", "Fall time": "min",
                    "Impact speed": "m/s"},
          ondaliklar={"Ballistic coefficient": 0, "Along track": 1, "Wind drift": 1, "Fall time": 1,
                      "Impact speed": 0})
    DATA["debris_inputs"] = {"wind_cross_ms": 20.0, "atmosphere": "ISA, wind constant with height"}

    rows = []
    for sigma in (50, 500, 2000):
        for p in (0.5, 0.95, 0.99):
            r = I.containment_radius(sigma, p)
            rows.append({"Position σ per axis": sigma, "Probability": p * 100, "Radius": r / 1000,
                         "Area": math.pi * (r / 1000) ** 2})
    table("search_radius", "Going from 95 % to 99 % containment adds ~25 % radius and ~55 % search area",
          pd.DataFrame(rows), birimler={"Position σ per axis": "m", "Probability": "%", "Radius": "km",
                                        "Area": "km²"},
          ondaliklar={"Position σ per axis": 0, "Probability": 0, "Radius": 2, "Area": 2})

    rows = []
    for h_ft, ld in ((35000, 17), (10000, 17), (5000, 9)):
        dist, drift = I.glide_reach(h_ft * A.FT, ld, 25.0, 130.0 if h_ft > 6000 else 60.0)
        rows.append({"Height": h_ft, "L/D": ld, "Still-air reach": dist / 1852, "Drift (25 m/s wind)": drift / 1852})
    table("glide", "From FL350 a transport glides ~100 NM: the search circle must be centred downwind",
          pd.DataFrame(rows), birimler={"Height": "ft", "Still-air reach": "NM", "Drift (25 m/s wind)": "NM"},
          ondaliklar={"Height": 0, "L/D": 0, "Still-air reach": 0, "Drift (25 m/s wind)": 0})
    DATA["glide_inputs"] = {"glide_tas_ms": {"high": 130.0, "low": 60.0}}
    DATA["isa_check_rho_sl"] = isa(0.0)["rho"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    venus()
    approach()
    investigation()
    md, audit = ["# Generated tables for docs 17–20\n", "Generated by `prev_guess/00_general/scripts/challenges_2026_numbers.py`; do not "
                 "edit by hand.\n"], []
    for key, title, df, kw in TABLES:
        shown = df.copy()
        for col, nd in dict(kw.get("ondaliklar", {})).items():      # audit what the reader sees
            shown[col] = shown[col].round(nd)
        findings = tablo.denetle(shown)
        audit.append(f"[{key}] " + ("; ".join(findings) if findings else "no findings"))
        md.append(f"\n## `{key}` — {title}\n")
        md.append(tablo.markdown_tablo(df, **kw))
    (OUT / "tables.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (OUT / "table_audit.txt").write_text("\n".join(audit) + "\n", encoding="utf-8")
    (OUT / "numbers.json").write_text(json.dumps(DATA, indent=1, default=float), encoding="utf-8")
    print(f"wrote {len(TABLES)} tables to {OUT}")


if __name__ == "__main__":
    main()
