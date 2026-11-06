"""VESPER numbers for ``venus_final``: BEMT validation set and the whole ``compute()`` chain."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))   # venus_entry_validation

from day_common import progress  # noqa: E402

from aerokit.venus import atmosphere as A  # noqa: E402
from aerokit.venus import bemt as B  # noqa: E402
from aerokit.venus import control as CT  # noqa: E402
from aerokit.venus import design as DES  # noqa: E402
from aerokit.venus import entry as EN  # noqa: E402
from aerokit.venus import hybrid as HY  # noqa: E402
from aerokit.venus import link as LK  # noqa: E402
from aerokit.venus import navigation as NV  # noqa: E402
from aerokit.venus import performance as F  # noqa: E402
from aerokit.venus import power as PW  # noqa: E402
from aerokit.venus import risk as RK  # noqa: E402
from aerokit.venus import descent as DS  # noqa: E402
from aerokit.venus import thermal as TH  # noqa: E402


KH = {2: [(4, 0.00248, 0.000191), (6, 0.00442, 0.000316), (8, 0.0065, 0.000494), (10, 0.00847, 0.000691),
          (12, 0.0099, 0.000878)],
      3: [(4, 0.00298, 0.0003), (6, 0.00548, 0.000474), (8, 0.00833, 0.000735), (10, 0.01125, 0.001048),
          (12, 0.0137, 0.001357)],
      4: [(4, 0.00338, 0.00041), (6, 0.00645, 0.00062), (8, 0.00981, 0.00092), (10, 0.01382, 0.001395),
          (12, 0.01745, 0.00191)],
      5: [(4, 0.00362, 0.000396), (6, 0.00694, 0.00068), (8, 0.01103, 0.001086), (10, 0.01548, 0.001635),
          (12, 0.0200, 0.00228)]}
HARR_SINGLE = [(0.001054, 0.0000676), (0.001407, 0.0000796), (0.001865, 0.0001067), (0.002348, 0.0001373),
               (0.002825, 0.0001748), (0.0031, 0.0001944), (0.003468, 0.000236)]


def bemt_validation() -> dict:
    """Predicted vs measured torque coefficient: Knight & Hefner (predicted from the section polar) and Harrington
    rotor 1 single (cd0 from the measured zero-thrust torque)."""
    air = B.FlowState(1.225, 1.79e-5, 340.3)
    af = B.Airfoil(cl_alpha=5.6, cl_max=0.93, cd0=0.0113, d1=0.0, d2=0.7, re_ref=242000)
    meas, pred, src = [], [], []
    for b, rows in KH.items():
        rot = B.Rotor(0.762, b, 0.0508, 0.0508, 0.0, 0.0, 0.167, af)
        for th, ct, cq in rows:
            r = B.solve(B.with_collective(rot, th), 960 * 2 * math.pi / 60, air)
            meas.append(cq / 2)
            pred.append(r.CP)
            src.append("Knight & Hefner 1937")
    IN = 0.0254
    R = 150 * IN
    afh = B.Airfoil(cd0=0.0115, re_ref=1.3e6, cl_max=1.3)
    cts, cqs = [], []
    for th in np.arange(2.0, 15.0, 1.0):
        r = B.solve(B.Rotor(R, 2, (12.43 - 0.0534 * 22.5) * IN, (12.43 - 0.0534 * 150) * IN, th, 0.0, 0.15, afh),
                    500 * 0.3048 / R, air)
        cts.append(r.CT)
        cqs.append(r.CP)
    for ct, cq in HARR_SINGLE:
        meas.append(cq)
        pred.append(float(np.interp(ct, cts, cqs)))
        src.append("Harrington 1951 rotor 1")
    err = [p / m - 1 for p, m in zip(pred, meas)]
    return {"measured_CQ": meas, "predicted_CQ": pred, "source": src, "rms_error": float(np.sqrt(np.mean(np.square(err)))),
            "max_abs_error_hover_range": float(max(abs(e) for e, m in zip(err, meas) if m > 1.2e-4))}


def compute(BASE, OUT) -> dict:
    progress("closing the baseline and flying entry, descent and the 44 h mission")
    res = DES.baseline(BASE)
    d = res["design"]
    progress("power versus altitude (BEMT at each km)")
    alts = list(range(50, 65))
    rows = []
    for km in alts:
        s = A.state(km * 1e3)
        fl = B.FlowState(s.rho, s.mu, s.a)
        W = d.gross_kg * s.g
        hp = F.hover(d.system, W, fl)
        vb, pb = F.bucket(d.system, W, fl)
        arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
        rows.append({"km": km, "hover_W": hp.electric_W + d.P_sys_W, "loiter_W": pb / d.system.drive_efficiency + d.P_sys_W,
                     "solar_mu1_W": arr.power(km * 1e3, 1.0), "solar_mu07_W": arr.power(km * 1e3, 0.7),
                     "rpm": hp.rpm, "FM": hp.FM, "tip_mach": hp.per_rotor.tip_mach, "re75": hp.per_rotor.re75,
                     "interior_C": TH.vessel_steady(TH.Vessel(), km * 1e3, 80.0)[0]})
    progress("Pioneer Venus large-probe entry for comparison")
    pv = EN.EntryVehicle(316.0, 1.42, 316.0 / (190.0 * math.pi * 1.42 ** 2 / 4.0), nose_radius_m=0.363)
    pv_run = EN.fly_entry(pv, 11584.0, -31.829, h0=137.78e3, dt=0.005)
    progress("BEMT validation set")
    val = bemt_validation()
    link = LK.RelayLink()
    bits, T = LK.pass_data_volume(link, 55e3, 1000e3)
    hyb = HY.size_hybrid(d.gross_kg, 1.0)
    trade = json.loads((OUT / "trade_sizing.json").read_text(encoding="utf-8")) if (OUT / "trade_sizing.json").exists() else None
    sens = json.loads((OUT / "sensitivity.json").read_text(encoding="utf-8")) if (OUT / "sensitivity.json").exists() else None
    run = res["mission"]
    ent = res["entry"]
    s55 = A.state(55e3)
    progress("latitude study (mission hours at 0-45 deg)")
    from aerokit import venus_flight as VFL
    lat_rows = []
    for lat in (0.0, 15.0, 30.0, 40.0, 45.0):
        c_lat = math.cos(math.radians(lat))
        mu = d.sustain_mu0_loiter or 1.0
        H0 = -math.degrees(math.acos(min((mu + 0.03) / c_lat, 1.0))) if mu + 0.03 <= c_lat else 0.0
        rl = VFL.simulate_rotorcraft_day(d, start_hour_angle_deg=H0, latitude_deg=lat, dt=120.0)
        lat_rows.append({"latitude_deg": lat, "release_hour_angle_deg": H0, "flight_h": rl.flight_time_s / 3600,
                         "sustained_h": rl.solar_sustained_s / 3600,
                         "note": "air-mass day length taken as equatorial [Y]"})
    out = {
        "generated_by": "python 04_Venus/code/pipeline/venus_day.py --final",
        "atmosphere_55km": {"T_C": s55.T - 273.15, "p_bar": s55.p / 1e5, "rho": s55.rho, "a": s55.a, "mu": s55.mu,
                            "wind_band": A.zonal_wind_band(55e3), "rho_band": [A.state(55e3, "min").rho,
                                                                              A.state(55e3, "max").rho]},
        "vehicle": d.summary(),
        "power_vs_altitude": rows,
        "entry": {"m_entry": res["m_entry"], "beta": res["entry_vehicle"].beta, "VE": res["VE"],
                  "gamma_deg": BASE.gamma_deg, "peak_g": ent.peak_g, "peak_g_km": ent.peak_g_altitude / 1e3,
                  "peak_qconv_W_cm2": ent.peak_q / 1e4, "peak_qrad_W_cm2": float(np.nanmax(ent.q_rad)) / 1e4,
                  "heat_load_kJ_cm2": ent.heat_load / 1e7, "chute_km": res["h_chute"] / 1e3,
                  "chute_s": res["chute"].duration_s, "release_rate": res["chute"].V_end,
                  "pullout_loss_m": res["deploy"].altitude_loss_m, "drop_loss_m": res["deploy_drop"].altitude_loss_m,
                  "pv_peak_g": pv_run.peak_g, "mass_budget": res["entry_system"]},
        "mission": {"flight_h": run.flight_time_s / 3600, "sustained_h": run.solar_sustained_s / 3600,
                    "no_charge_h": run.no_charge_s / 3600, "drift_km": float(run.x[-1]) / 1e3,
                    "interior_max_C": float(run.T_interior_C.max()), "events": run.events},
        "link": {"orbit_km": 1000, "pass_min": T / 60, "Mbit_per_pass": bits / 1e6, "veva_margin_dB": LK.veva_check()},
        "navigation": {"baro_error_m_55km": NV.baro_altitude_error(55e3), "gyrocompass_ratio_0p01": NV.gyrocompass_ratio(0.01)},
        "hybrid": hyb.__dict__,
        "latitude_study": lat_rows,
        "bemt_validation": val,
        "risks": [dict(r, score=RK.score(r), score_after=RK.score(r, True)) for r in RK.RISKS],
    }
    progress("entry validation against 12 historical entries + DAVINCI")
    import venus_entry_validation as EV
    EV.main([])
    out["entry_validation"] = json.loads((ROOT / "04_Venus" / "outputs" /
                                          "entry_validation.json").read_text(encoding="utf-8"))
    progress("deployment Monte Carlo (measured wind profiles, gusts, density, motor failure)")
    mc = {proc: DS.deployment_monte_carlo(d.gross_kg, res["m_suspended"], BASE.chute_D, res["v_h_release"],
                                           n=300, procedure=proc) for proc in ("forward", "vertical")}
    out["deployment_mc"] = {proc: {"n": m.n, "loss_p50_m": float(np.percentile(m.altitude_loss_m, 50)),
                                   "loss_p99_m": float(np.percentile(m.altitude_loss_m, 99)),
                                   "loss_max_m": float(m.altitude_loss_m.max()),
                                   "vrs_fraction": float((m.vrs_time_s > 0).mean()),
                                   "vrs_p99_s": float(np.percentile(m.vrs_time_s, 99)),
                                   "release_airspeed_p50": float(np.median(m.release_airspeed_m_s)),
                                   "swing_max_deg": float(m.swing_deg.max()),
                                   "max_descent_p99": float(np.percentile(m.max_descent_m_s, 99)),
                                   "probes": sorted(set(m.probe))} for proc, m in mc.items()}
    progress("end of mission: unpowered terminal descent and surface survival")
    A_disk = d.system.disk_area
    term = {"windmilling": DS.terminal_descent(d.gross_kg, 1.2 * A_disk, float(run.z[-1]), float(run.T_interior_C[-1])),
            "rotors_failed": DS.terminal_descent(d.gross_kg, d.system.drag_area_m2, float(run.z[-1]),
                                                 float(run.T_interior_C[-1]))}
    placed = DS.terminal_descent(d.gross_kg, 1.2 * A_disk, 0.5, 25.0)
    out["end_of_mission"] = {k: {"start_km": float(run.z[-1]) / 1e3, "t_surface_h": v.t_surface_s / 3600,
                                 "impact_m_s": v.impact_speed,
                                 "t_electronics_125C_h": (v.t_electronics_125C_s or float("nan")) / 3600,
                                 "h_electronics_125C_km": (v.h_electronics_125C_m or float("nan")) / 1e3,
                                 "drag_area_m2": (1.2 * A_disk if k == "windmilling" else d.system.drag_area_m2)}
                             for k, v in term.items()}
    out["end_of_mission"]["placed_on_surface_at_25C_min_to_125C"] = (placed.t_electronics_125C_s or float("nan")) / 60
    progress("full air-mass day and station-keeping cost")
    arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
    period = PW.air_mass_day_s(A.zonal_wind(BASE.cruise_km * 1e3), BASE.cruise_km * 1e3)
    hrs = np.linspace(0.0, period / 3600.0, 400)
    Hh = -math.pi / 2 + 2 * math.pi * hrs * 3600.0 / period                  # 0 h = dawn terminator
    sol = [arr.power(BASE.cruise_km * 1e3, max(math.cos(x), 0.0)) if math.cos(x) > 0 else 0.0 for x in Hh]
    s55 = A.state(BASE.cruise_km * 1e3)
    fl55 = B.FlowState(s55.rho, s55.mu, s55.a)
    W55 = d.gross_kg * s55.g
    speeds = np.linspace(0.0, 30.0, 61)
    sk = [F.forward_power(d.system, W55, fl55, float(v)) / d.system.drive_efficiency + d.P_sys_W for v in speeds]
    vt = d.hover.per_rotor.tip_speed
    out["air_mass_day"] = {"period_h": period / 3600.0, "hours": hrs.tolist(), "solar_W": sol,
                           "loiter_W": d.P_bucket_elec_W, "hover_W": d.P_hover_elec_W,
                           "mission_start_h": (math.radians(res["release_hour_angle_deg"]) + math.pi / 2) * period
                           / (2 * math.pi) / 3600.0, "mission_h": run.flight_time_s / 3600.0}
    wl, wm, wh = A.zonal_wind_band(BASE.cruise_km * 1e3)
    out["station_keeping"] = {"speeds": speeds.tolist(), "electric_W": sk, "advance_ratio_at_30": 30.0 / vt,
                              "wind_band_m_s": [wl, wm, wh],
                              "parasite_only_kW_at_band": [0.5 * s55.rho * u ** 3 * d.system.drag_area_m2 / 1e3
                                                           for u in (wl, wm, wh)],
                              "advance_ratio_at_band": [u / vt for u in (wl, wm, wh)]}
    # margins: value vs limit (ratio > 1 = margin)
    gust = CT.gust_response(d.gross_kg, W55, CT.heave_derivative(d.system, W55, fl55), 0.1, kp=0.1, kd=1.0)
    from aerokit.venus import structure as STR
    arm = STR.size_arm(d.arm_m, d.req.thrust_margin * W55 / 6, 0.08)
    dive_peak = float(max(run.T_interior_C[(run.t > 5.5 * 3600) & (run.t < 8 * 3600)]))
    mg = [("Noon solar / loiter power", d.P_solar_overhead_W / d.P_bucket_elec_W, "power"),
          ("Thrust margin / gust peak", (d.req.thrust_margin - 1.0) / gust["dT_peak_over_W"], "control"),
          ("Arm stress allowable / actual", 300e6 / arm.root_stress_Pa, "structure"),
          ("Entry g qualification / peak", 100.0 / ent.peak_g, "entry"),
          ("Tested acid exposure / mission (FEP 168 h)", 168.0 / (run.flight_time_s / 3600.0), "materials"),
          ("Tip Mach cap / hover tip Mach", 0.7 / d.hover.per_rotor.tip_mach, "rotor"),
          ("Release altitude margin / p99 pull-out loss", 6000.0 / out["deployment_mc"]["forward"]["loss_p99_m"], "deployment"),
          ("Charge headroom: (45 °C − air) / (cruise interior − air)",
           (45.0 - (s55.T - 273.15)) / (TH.vessel_steady(TH.Vessel(), 55e3, 80.0)[0] - (s55.T - 273.15)), "thermal"),
          ("Dive headroom: (60 °C − cruise) / (dive peak − cruise)",
           (60.0 - TH.vessel_steady(TH.Vessel(), 55e3, 80.0)[0]) / (dive_peak - TH.vessel_steady(TH.Vessel(), 55e3, 80.0)[0]),
           "thermal"),
          ("Night energy stored / needed", d.battery_Wh / (d.P_bucket_elec_W * period / 2 / 3600.0), "energy")]
    out["margins"] = [{"item": a, "ratio": float(r), "area": c} for a, r, c in mg]
    return {"out": out, "res": res, "pv_run": pv_run, "trade": trade, "sens": sens, "mc": mc, "term": term}
