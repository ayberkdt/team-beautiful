"""LuGus final (4–5 Nov 2026): VESPER rotorcraft — numbers, audited figures and the design hand-off in one run.

    python scripts/venus_day.py --final          (or: python scripts/venus_final.py)
    python scripts/venus_day.py --final --payload-kg 5 --cruise-km 56     # mentor numbers -> out_variant_*/

Writes to ``studies/final_2026/venus/out/``: ``result.json``, ``result.md``, figures F1–F9 (PDF + PNG + datawiz
audit ``*.denetim.txt``, set ``vesper.seti.json`` + ``vesper.tutarlilik.txt``) and regenerates
``studies/final_2026/venus/design.json``. Reads ``trade_sizing.json`` / ``sensitivity.json`` when present (produced
by ``scripts/venus_trade.py`` and ``scripts/venus_sensitivity.py``, several minutes each).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from day_common import audit_summary, console_text, progress, protect_streams  # noqa: E402

from aerokit import planetary as P  # noqa: E402
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

OUT = ROOT / "studies" / "final_2026" / "venus" / "out"
BASE = DES.BASELINE                     # replaced by main() when the mentor gives other numbers

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


def compute() -> dict:
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
        "generated_by": "python scripts/venus_day.py --final",
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
    out["entry_validation"] = json.loads((ROOT / "studies" / "final_2026" / "venus" / "out" /
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


def figures(c: dict) -> None:
    import datawiz as dw

    out, res = c["out"], c["res"]
    d = res["design"]
    S = dw.Seti(str(OUT / "vesper.seti.json"), hedef="sunum-tam")
    S.nicelik("alt", "Altitude", "km", eksen="y")
    S.nicelik("temp", "Temperature", "°C", eksen="x")
    S.nicelik("rho", "Density", "kg/m³", eksen="x")
    S.nicelik("wind", "Westward wind", "m/s", eksen="x")
    S.nicelik("pw", "Electrical power", "kW", eksen="x")
    S.nicelik("t_s", "Time from entry interface", "s", eksen="x")
    S.nicelik("g", "Deceleration", "g", eksen="y")
    S.nicelik("q", "Stagnation heat flux", "W/cm²", eksen="y")
    S.nicelik("hours", "Mission time", "h", eksen="x")
    S.nicelik("alt2", "Altitude", "km", eksen="y")
    S.nicelik("pwy", "Power", "kW", eksen="y")
    S.nicelik("soc", "Battery charge", "Wh", eksen="y")
    S.nicelik("mass", "Mass", "kg", eksen="x")
    S.nicelik("D", "Rotor diameter", "m", eksen="x")
    S.nicelik("gross", "Gross mass", "kg", eksen="y")
    S.nicelik("mu", "Sun height needed, cos z", "", eksen="y")
    S.nicelik("cq_m", "Measured torque coefficient", "", eksen="x")
    S.nicelik("cq_p", "Predicted torque coefficient", "", eksen="y")
    S.nicelik("hrs", "Flight time", "h", eksen="x")
    S.nicelik("L", "Likelihood", "", eksen="x")
    S.nicelik("C", "Consequence", "", eksen="y")
    for n in ("VESPER", "Hover", "Loiter at bucket speed", "Sun overhead", "Knight & Hefner 1937",
              "Harrington 1951", "tip 55 m/s"):
        S.varlik(n)
    S.varlik("tip 115 m/s", renk=dw.renk.koyu_ton("#f0e442"), cizgi="--")
    S.varlik("Sun at cos z 0.7", renk=S.renk("Sun overhead"), cizgi="--", renk_paylas=True)
    S.varlik("tip 70 m/s (VESPER)", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("D 2.6 m, geared 5:1 (VESPER)", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("D 2.6 m, direct drive", renk=S.renk("tip 55 m/s"), cizgi=":", renk_paylas=True)
    S.varlik("D 2.3 m, geared 5:1", renk=S.renk("Harrington 1951"), cizgi="--", renk_paylas=True)
    S.varlik("Pioneer Venus probes", renk=S.renk("Harrington 1951"), renk_paylas=True)
    S.varlik("Venera and Vega", renk=S.renk("Knight & Hefner 1937"), renk_paylas=True)
    S.varlik("Pull-out in forward flight", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("Pull-out straight down", renk=S.renk("tip 55 m/s"), cizgi=":", renk_paylas=True)
    S.varlik("Rotors windmilling", renk=S.renk("VESPER"), cizgi="-", renk_paylas=True)
    S.varlik("Rotors failed", renk=S.renk("Hover"), cizgi="--", renk_paylas=True)
    S.varlik("Pioneer Venus", baglam=True)
    S.varlik("Probe envelope", baglam=True)

    # F1 altitude justification ---------------------------------------------------------------------------------
    km = np.arange(45, 64.01, 0.25)
    h = km * 1e3
    mean = [A.state(x) for x in h]
    lo = [A.state(x, "min") for x in h]
    hi = [A.state(x, "max") for x in h]
    wl, wm, wh = zip(*[A.zonal_wind_band(x) for x in h])
    fig, axs = S.figur(oran=0.55, ncols=3, sharey=True)
    band = dw.renk.alan_tonu(S.renk("VESPER"))
    for ax in axs:
        ax.axhspan(53, 58, color=dw.renk.alan_tonu("#7a7a7a", acik=0.75), lw=0, zorder=0)
    axs[0].fill_betweenx(km, [s.T - 273.15 for s in lo], [s.T - 273.15 for s in hi], color=band, lw=0)
    axs[0].plot([s.T - 273.15 for s in mean], km, **S.stil("VESPER"))
    axs[0].axvspan(0, 45, color=dw.renk.alan_tonu("#009E73", acik=0.8), lw=0, zorder=0)
    axs[1].fill_betweenx(km, [s.rho for s in lo], [s.rho for s in hi], color=band, lw=0)
    axs[1].plot([s.rho for s in mean], km, **S.stil("VESPER"))
    axs[2].fill_betweenx(km, wl, wh, color=band, lw=0)
    axs[2].plot(wm, km, **S.stil("VESPER"))
    for ax, q in zip(axs, ("temp", "rho", "wind")):
        S.eksen(ax, x=q, y="alt")
    for ax in axs[1:]:
        ax.set_ylabel("")
    axs[0].set_xticks([0, 50, 100])
    axs[0].text(22.5, 46.0, "Li-ion\ncharges\n0–45 °C", ha="center", va="bottom", fontsize=plt_size() * 0.8,
                color="#00694d")
    axs[1].text(2.6, 55.5, "operating\nband\n53–58 km", ha="right", va="center", fontsize=plt_size() * 0.8,
                color="#4d4d4d")
    S.kaydet(fig, str(OUT / "F1_altitude_justification"), sessiz=True)

    # F2 power vs altitude -------------------------------------------------------------------------------------
    rows = out["power_vs_altitude"]
    kms = [r["km"] for r in rows]
    fig, ax = S.figur(oran=0.55)
    for key, name in (("hover_W", "Hover"), ("loiter_W", "Loiter at bucket speed"),
                      ("solar_mu1_W", "Sun overhead"), ("solar_mu07_W", "Sun at cos z 0.7")):
        ax.plot([r[key] / 1e3 for r in rows], kms, **S.stil(name))
    S.eksen(ax, x="pw", y="alt")
    dw.lejant.yerlestir(ax)
    dw.notlar.referans(ax, y=55.0, metin="cruise 55 km")
    S.kaydet(fig, str(OUT / "F2_power_vs_altitude"), sessiz=True)

    # F3 entry --------------------------------------------------------------------------------------------------
    ent, pv = res["entry"], c["pv_run"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    t0 = float(ent.t[int(np.argmax(ent.decel_g))]) - 40.0
    tp = float(pv.t[int(np.argmax(pv.decel_g))]) - 40.0
    m1 = (ent.t >= t0) & (ent.t <= t0 + 80)
    m2 = (pv.t >= tp) & (pv.t <= tp + 80)
    axs[0].plot(ent.t[m1] - t0, ent.decel_g[m1], **S.stil("VESPER"))
    axs[0].plot(pv.t[m2] - tp, pv.decel_g[m2], **S.stil("Pioneer Venus"))
    axs[1].plot(ent.t[m1] - t0, (ent.q_conv[m1] + np.nan_to_num(ent.q_rad[m1])) / 1e4, **S.stil("VESPER"))
    axs[1].plot(pv.t[m2] - tp, (pv.q_conv[m2] + np.nan_to_num(pv.q_rad[m2])) / 1e4, **S.stil("Pioneer Venus"))
    S.eksen(axs[0], x="t_s", y="g")
    S.eksen(axs[1], x="t_s", y="q")
    for ax in axs:
        ax.set_xlabel("Time around peak deceleration (s)")
    gv, gp = float(ent.peak_g), float(pv.peak_g)
    axs[0].text(44.0, gp * 0.92, f"Pioneer Venus\nlarge probe\n{gp:.0f} g", ha="left", va="top",
                fontsize=plt_size() * 0.8, color=S.renk("Pioneer Venus"))
    axs[0].text(50.0, gv + 15.0, f"VESPER {gv:.0f} g", ha="left", va="bottom", fontsize=plt_size() * 0.8,
                color=S.renk("VESPER"))
    qv = float(np.nanmax(ent.q_conv + np.nan_to_num(ent.q_rad))) / 1e4
    axs[1].text(44.0, 4000.0, "Pioneer Venus", ha="left", va="top", fontsize=plt_size() * 0.8,
                color=S.renk("Pioneer Venus"))
    axs[1].text(50.0, qv + 250.0, f"VESPER {qv:.0f}", ha="left", va="bottom", fontsize=plt_size() * 0.8,
                color=S.renk("VESPER"))
    S.kaydet(fig, str(OUT / "F3_entry"), sessiz=True)

    # F4 mass budget ------------------------------------------------------------------------------------------
    bd = dict(d.breakdown)
    nice = {"blades+hubs": "blades + hubs", "arms+hinges": "arms + hinges", "contingency": "contingency 20 %"}
    small = [k for k, v in bd.items() if v < 0.9]
    other = sum(bd.pop(k) for k in small)
    items = {nice.get(k, k): v for k, v in bd.items()}
    items["other: " + ", ".join(small)] = other
    fig, ax = S.figur(oran=0.6)
    dw.ciz.cubuk(ax, list(items.keys()), list(items.values()), renk=S.renk("VESPER"), sirala=True, yatay=True,
                 deger_yaz=True, bicim="{:.1f}")
    S.eksen(ax, x="mass")
    ax.set_ylabel("Component")
    S.kaydet(fig, str(OUT / "F4_mass_budget"), sessiz=True)

    # F5 risk matrix --------------------------------------------------------------------------------------------
    fig, ax = S.figur(oran=0.75)
    for L in range(1, 6):
        for C in range(1, 6):
            band_c = {"red": "#d55e00", "amber": "#e69f00", "green": "#009e73"}[RK.colour_band(L * C)]
            ax.add_patch(__import__("matplotlib").patches.Rectangle((L - 0.5, C - 0.5), 1, 1,
                                                                      color=dw.renk.alan_tonu(band_c, acik=0.75), lw=0))
    offsets = {}
    for r in RK.RISKS:
        key = (r["L2"], r["C2"])
        k = offsets.get(key, 0)
        offsets[key] = k + 1
        x, y = r["L2"] - 0.32 + 0.32 * (k % 3), r["C2"] + 0.25 - 0.25 * (k // 3)
        ax.annotate("", xy=(x, y), xytext=(r["L"], r["C"]),
                    arrowprops=dict(arrowstyle="->", color="#7a7a7a", lw=0.8, shrinkA=6, shrinkB=6))
        ax.text(x, y, r["id"], ha="center", va="center", fontsize=plt_size() * 0.8, color="#000000")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    S.eksen(ax, x="L", y="C")
    ax.set_xlabel("Likelihood (1–5)")
    ax.set_ylabel("Consequence (1–5)")
    S.kaydet(fig, str(OUT / "F5_risk_matrix"), sessiz=True)

    # F6 mission ------------------------------------------------------------------------------------------------
    run = res["mission"]
    hrs = run.t / 3600.0
    fig, axs = S.figur(oran=1.25, nrows=3, sharex=True, gridspec_kw={"hspace": 0.3})
    axs[0].plot(hrs, run.z / 1e3, **S.stil("VESPER"))
    axs[1].plot(hrs, run.p_need / 1e3, **S.stil("Loiter at bucket speed"))
    axs[1].plot(hrs, run.p_solar / 1e3, **S.stil("Sun overhead"))
    axs[2].plot(hrs, run.energy_Wh, **S.stil("VESPER"))
    S.eksen(axs[0], x="hours", y="alt2")
    S.eksen(axs[1], x="hours", y="pwy")
    S.eksen(axs[2], x="hours", y="soc")
    axs[1].lines[1].set_label("Solar array")
    axs[1].lines[0].set_label("Demand")
    for ax in axs[:2]:
        ax.set_xlabel("")
    axs[0].set_ylim(45, 57)
    axs[0].set_yticks([47, 55])
    pmax = float(max(run.p_need.max(), run.p_solar.max())) / 1e3
    axs[1].set_ylim(0, math.ceil(pmax * 1.05))
    axs[1].set_yticks([0, 2 * math.ceil(pmax / 2.0 * 0.5)] if pmax > 2 else [0, 1])
    emax = float(run.energy_Wh.max())
    axs[2].set_ylim(0, emax * 1.1)
    axs[2].set_yticks([0, 1000 * round(emax / 1000.0)])
    dw.etiket.cizgi_sonu(axs[1])
    S.kaydet(fig, str(OUT / "F6_mission"), sessiz=True)

    # F7 trade --------------------------------------------------------------------------------------------------
    if c["trade"]:
        rows = [r for r in c["trade"]["rows"] if r["solar_option"] == "deck" and "error" not in r]
        fig, axs = S.figur(oran=0.55, ncols=2)
        for vt in (55.0, 70.0, 115.0):
            rr = sorted([r for r in rows if r["V_tip_m_s"] == vt], key=lambda r: r["D_m"])
            name = "tip 70 m/s (VESPER)" if vt == 70.0 else f"tip {vt:.0f} m/s"
            axs[0].plot([r["D_m"] for r in rr], [r["gross_kg"] for r in rr], **S.stil(name, isaretli=True))
            pts = [r for r in rr if r["sustain_mu0_loiter"] is not None]
            axs[1].plot([r["D_m"] for r in pts], [r["sustain_mu0_loiter"] for r in pts], **S.stil(name, isaretli=True))
        S.eksen(axs[0], x="D", y="gross")
        S.eksen(axs[1], x="D", y="mu")
        axs[1].set_ylabel("Sun height needed (cos z)")
        dw.lejant.yerlestir(axs[0])
        S.kaydet(fig, str(OUT / "F7_trade"), sessiz=True)

    # F8 BEMT validation ----------------------------------------------------------------------------------------
    val = out["bemt_validation"]
    fig, ax = S.figur(oran=0.75)
    m = np.array(val["measured_CQ"]) * 1e4
    p = np.array(val["predicted_CQ"]) * 1e4
    xs = np.geomspace(m.min() * 0.8, m.max() * 1.25, 20)
    ax.fill_between(xs, xs * 0.9, xs * 1.1, color=dw.renk.alan_tonu("#7a7a7a", acik=0.7), lw=0)
    ax.plot(xs, xs, color="#7a7a7a", lw=0.8)
    for srcname in ("Knight & Hefner 1937", "Harrington 1951"):
        sel = [i for i, s in enumerate(val["source"]) if s.startswith(srcname.split()[0])]
        st = S.stil(srcname, tur="sacilim")
        if srcname.startswith("Harrington"):
            st = dict(st, facecolors="none", edgecolors=st.get("color", st.get("c")), linewidths=1.5)
            st.pop("color", None)
            st.pop("c", None)
        ax.scatter(m[sel], p[sel], **st)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Measured torque coefficient (×10⁻⁴)")
    ax.set_ylabel("Predicted torque coefficient (×10⁻⁴)")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(OUT / "F8_bemt_validation"), sessiz=True)

    # F9 sensitivity --------------------------------------------------------------------------------------------
    if c["sens"]:
        rows = c["sens"]["rows"]
        base = next(r for r in rows if r["case"] == "baseline")["flight_h"]
        names = {"battery cell energy 180 / 280 Wh/kg": ("Battery cell energy", "180", "280 Wh/kg"),
                 "gearbox torque density 12 / 40 N·m/kg": ("Gearbox torque density", "12", "40 N·m/kg"),
                 "solar array efficiency 0.25 / 0.32": ("Solar array efficiency", "25 %", "32 %"),
                 "mass contingency 30 % / 10 %": ("Mass contingency", "30 %", "10 %"),
                 "atmosphere thin / dense (PV envelope)": ("Atmosphere (probe envelope)", "thin", "dense"),
                 "payload 5 kg / 1.5 kg": ("Payload", "5 kg", "1.5 kg"),
                 "cruise altitude 53 / 58 km": ("Cruise altitude", "53 km", "58 km"),
                 "battery reserve 1.0 / 0.25 h hover": ("Battery reserve (hover)", "1 h", "0.25 h"),
                 "blade areal mass 3.3 / 1.5 kg/m²": ("Blade areal mass", "3.3", "1.5 kg/m²"),
                 "motor specific torque 5 / 10 N·m/kg": ("Motor specific torque", "5", "10 N·m/kg")}
        dev = []
        for cs, (nm, la, lb) in names.items():
            a = next((r for r in rows if r.get("case") == cs and r.get("side") == "bad"), None)
            b = next((r for r in rows if r.get("case") == cs and r.get("side") == "good"), None)
            if a is None or b is None:
                continue
            da = (a["flight_h"] - base) if "flight_h" in a else -base
            db = (b["flight_h"] - base) if "flight_h" in b else -base
            dev.append((nm, la + (" (no closure)" if "error" in a else ""), da,
                        lb + (" (no closure)" if "error" in b else ""), db))
        dev.sort(key=lambda x: max(abs(x[2]), abs(x[4])))
        fig, ax = S.figur(oran=0.62)
        y = np.arange(len(dev))
        neg, pos = "#d55e00", "#0072b2"
        for i, (nm, la, da, lb, db) in enumerate(dev):
            for val, lab in ((da, la), (db, lb)):
                col = neg if val < 0 else pos
                if "no closure" in lab:            # no design exists: no bar, a word at the axis
                    ax.text(-0.8, i, lab, ha="right", va="center", fontsize=plt_size() * 0.8,
                            color=dw.renk.koyu_ton(neg))
                    continue
                ax.barh(i, val, height=0.6, color=dw.renk.alan_tonu(col), edgecolor=col, lw=0.8)
                ax.text(val + (-0.8 if val < 0 else 0.8), i, lab, ha="right" if val < 0 else "left", va="center",
                        fontsize=plt_size() * 0.8, color=dw.renk.koyu_ton(col))
        ax.axvline(0, color="#000000", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([x[0] for x in dev])
        lim = max(max(abs(v) for v, lab in ((x[2], x[1]), (x[4], x[3])) if "no closure" not in lab) for x in dev)
        ax.set_xlim(-lim * 1.45, lim * 1.45)
        ax.set_xlabel(f"Change in flight time from the {base:.0f} h baseline (h)")
        ax.set_ylabel("")
        S.kaydet(fig, str(OUT / "F9_sensitivity"), sessiz=True)

    # F10 robustness: flight hours of three rotor sizes under adverse assumptions -------------------------------
    if c["sens"] and c["sens"].get("robustness"):
        rob = c["sens"]["robustness"]
        cases = list(dict.fromkeys(r["case"] for r in rob))
        fig, ax = S.figur(oran=0.6)
        y = np.arange(len(cases))[::-1] + 1.0                       # rows at 1..n: no zero baseline through a row
        variants = ((2.6, 5.0, "D 2.6 m, geared 5:1 (VESPER)"), (2.6, 1.0, "D 2.6 m, direct drive"),
                    (2.3, 5.0, "D 2.3 m, geared 5:1"))
        for k, (Dr, gr, name) in enumerate(variants):
            yy = y + (1 - k) * 0.18                                   # small vertical dodge per variant
            xs = [next((r.get("flight_h", 0.0) for r in rob if r["D_m"] == Dr and r.get("gear_ratio") == gr
                        and r["case"] == cs), 0.0) for cs in cases]
            st = S.stil(name, tur="cizgi", isaretli=True)
            st["linestyle"] = "none"
            st.pop("ls", None)
            keep = [i for i, xv in enumerate(xs) if xv > 0.0]
            ax.plot([xs[i] for i in keep], [yy[i] for i in keep], **st)
        for i, cs in enumerate(cases):                                 # one label per row for designs that do not close
            bad = [("geared" if r.get("gear_ratio", 1.0) > 1 else "direct") + f" {r['D_m']:.1f} m"
                   for r in rob if r["case"] == cs and "error" in r]
            if bad:
                ax.text(0.8, y[i], "no closure: " + ", ".join(bad), ha="left", va="center",
                        fontsize=plt_size() * 0.8, color="#7a3b00")
        ax.set_yticks(y)
        ax.set_yticklabels(cases)
        S.eksen(ax, x="hrs")
        ax.set_ylabel("")
        xmax = max(r.get("flight_h", 0.0) for r in rob)
        ax.set_xlim(0, xmax * 1.15)
        ax.set_ylim(0.4, len(cases) + 1.9)                          # free band above the top row for the legend
        dw.lejant.yerlestir(ax)
        S.kaydet(fig, str(OUT / "F10_robustness"), sessiz=True)
    figures_extra(c, S, dw)


def figures_extra(c: dict, S, dw) -> None:
    """F11-F15: entry validation, deployment Monte Carlo, air-mass day + station keeping, terminal descent, margins."""
    out = c["out"]
    # F11 entry validation ---------------------------------------------------------------------------------------
    ev = out["entry_validation"]["rows"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    for grp, name in (("PV", "Pioneer Venus probes"), ("V", "Venera and Vega")):
        sel = [r for r in ev if r["case"].startswith("PV")] if grp == "PV" else [r for r in ev if not r["case"].startswith("PV")]
        axs[0].scatter([r["dutta_g"] for r in sel], [r["peak_g"] for r in sel], zorder=3, **S.stil(name, tur="sacilim"))
        axs[1].scatter([r["dutta_q_kW_cm2"] for r in sel], [r["peak_q_kW_cm2"] for r in sel], zorder=3,
                       **S.stil(name, tur="sacilim"))
    for ax, lo, hi in ((axs[0], 110.0, 560.0), (axs[1], 2.5, 36.0)):
        xs = np.geomspace(lo, hi, 20)
        ax.fill_between(xs, xs * 0.9, xs * 1.1, color=dw.renk.alan_tonu("#7a7a7a", acik=0.7), lw=0, zorder=0)
        ax.plot(xs, xs, color="#7a7a7a", lw=0.8, zorder=1)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_xscale("log")
        ax.set_yscale("log")
    axs[0].set_xlabel("Published peak deceleration (g)")
    axs[0].set_ylabel("Model peak deceleration (g)")
    axs[1].set_xlabel("Published peak heat flux (kW/cm²)")
    axs[1].set_ylabel("Model peak heat flux (kW/cm²)")
    dw.lejant.yerlestir(axs[0])
    S.kaydet(fig, str(OUT / "F11_entry_validation"), sessiz=True)

    # F12 deployment Monte Carlo ---------------------------------------------------------------------------------
    mc = c["mc"]
    fig, ax = S.figur(oran=0.55)
    for proc, name in (("forward", "Pull-out in forward flight"), ("vertical", "Pull-out straight down")):
        x = np.sort(mc[proc].altitude_loss_m)
        ax.step(x, np.arange(1, len(x) + 1) / len(x), where="post", **S.stil(name))
    ax.set_xlabel("Altitude lost after release (m)")
    ax.set_ylabel("Fraction of 300 runs")
    ax.set_ylim(0, 1.02)
    dw.etiket.cizgi_sonu(ax)
    S.kaydet(fig, str(OUT / "F12_deployment_monte_carlo"), sessiz=True)

    # F13 air-mass day and station keeping -----------------------------------------------------------------------
    day, sk = out["air_mass_day"], out["station_keeping"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    hrs = np.array(day["hours"])
    axs[0].axvspan(day["mission_start_h"], day["mission_start_h"] + day["mission_h"],
                   color=dw.renk.alan_tonu("#7a7a7a", acik=0.75), lw=0)
    axs[0].plot(hrs, np.array(day["solar_W"]) / 1e3, **S.stil("Sun overhead"))
    axs[0].axhline(day["loiter_W"] / 1e3, **S.stil("Loiter at bucket speed"))
    axs[0].axhline(day["hover_W"] / 1e3, **S.stil("Hover"))
    axs[0].set_xlabel("Hours from dawn, drifting at 55 km")
    axs[0].set_ylabel("Power over the day (kW)")
    axs[0].text(day["mission_start_h"] + day["mission_h"] / 2, 0.15, "VESPER flies", ha="center", va="bottom",
                fontsize=plt_size() * 0.8, color="#4d4d4d")
    axs[0].text(hrs[-1] * 0.78, 2.4, "night: 0 W", ha="center", va="center", fontsize=plt_size() * 0.8,
                color="#4d4d4d")
    sp = np.array(sk["speeds"])
    axs[1].plot(sp, np.array(sk["electric_W"]) / 1e3, **S.stil("VESPER"))
    band = sk["wind_band_m_s"]
    ub = np.linspace(band[0], band[2], 20)
    axs[1].plot(ub, [0.5 * A.state(55e3).rho * u ** 3 * c["res"]["design"].system.drag_area_m2 / 1e3 for u in ub],
                **S.stil("Pioneer Venus"))
    axs[1].set_yscale("log")
    axs[1].set_xlabel("Airspeed (m/s)")
    axs[1].set_ylabel("Power to hold that airspeed (kW)")
    axs[1].text(band[0] - 2.0, 0.5 * A.state(55e3).rho * band[2] ** 3 * c["res"]["design"].system.drag_area_m2 / 1e3,
                "airframe drag alone\nat wind speed", ha="right", va="top", fontsize=plt_size() * 0.8, color="#4d4d4d")
    S.kaydet(fig, str(OUT / "F13_day_and_station_keeping"), sessiz=True)

    # F14 terminal descent ---------------------------------------------------------------------------------------
    term = c["term"]
    fig, axs = S.figur(oran=0.55, ncols=2)
    for key, name in (("windmilling", "Rotors windmilling"), ("rotors_failed", "Rotors failed")):
        r = term[key]
        axs[0].plot(r.t / 3600.0, r.h / 1e3, **S.stil(name))
        axs[1].plot(r.t / 3600.0, r.T_interior_C, **S.stil(name))
    axs[1].axhline(125.0, color="#7a3b00", lw=0.8, ls="--")
    tmax = max(float(term[k].t[-1]) for k in term) / 3600.0
    axs[1].text(0.97 * tmax, 118.0, "electronics 125 °C", ha="right", va="top", fontsize=plt_size() * 0.8,
                color="#7a3b00")
    axs[0].set_xlabel("Hours after the sunset dive")
    axs[1].set_xlabel("Hours after the sunset dive")
    axs[0].set_ylabel("Altitude (km)")
    axs[1].set_ylabel("Battery-bay temperature (°C)")
    dw.etiket.cizgi_sonu(axs[0])
    S.kaydet(fig, str(OUT / "F14_end_of_mission"), sessiz=True)

    # F15 margins ------------------------------------------------------------------------------------------------
    mg = sorted(out["margins"], key=lambda m: m["ratio"])
    fig, ax = S.figur(oran=0.62)
    y = np.arange(len(mg)) + 1.0
    ax.scatter([m["ratio"] for m in mg], y, **S.stil("VESPER", tur="sacilim"))
    ax.axvline(1.0, color="#7a3b00", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlim(0.005, 400.0)
    ax.set_xticks([0.01, 0.1, 1.0, 10.0, 100.0])
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "100"])
    ax.minorticks_off()
    ax.set_yticks(y)
    ax.set_yticklabels([m["item"] for m in mg])
    ax.set_xlabel("Margin ratio (above 1 = margin, log scale)")
    ax.set_ylabel("")
    S.kaydet(fig, str(OUT / "F15_margins"), sessiz=True)


def simulator_parameters(c: dict) -> dict:
    """Flight-model parameters for a game/simulator engine (Liftoff Core / Unity): rigid body + 6 rotors.

    Inertia: point masses of the design components at their positions, arms as thin rods, each rotor+motor as a point
    mass at its hub [K from design.json masses, which are themselves K/Y]. Rotor thrust/torque curves: BEMT at the
    cruise altitude for the trimmed collective, 40-160 % of hover rpm [K]."""
    res = c["res"]
    d = res["design"]
    doc = DES.design_document(BASE)
    comps = {x["id"]: x for x in doc["vehicle"]["components"]}
    arm = d.arm_m
    az = [math.radians(a) for a in (30, 90, 150, 210, 270, 330)]
    z_rot = comps["rotors"]["position_m"][2]
    m_rotor = comps["rotors"]["mass_kg"] / 6.0
    I = np.zeros((3, 3))
    pts = []
    for cid, cm in comps.items():
        if cid in ("rotors", "arms") or cm.get("position_m") is None:
            continue
        pts.append((cm["mass_kg"], np.array(cm["position_m"], dtype=float)))
    for a in az:
        pts.append((m_rotor, np.array([arm * math.cos(a), arm * math.sin(a), z_rot])))
    m_arm = comps["arms"]["mass_kg"] / 6.0
    for a in az:                                   # thin rod from the body edge to the hub, 5 lumps
        for k in range(5):
            rr = 0.3 + (arm - 0.3) * (k + 0.5) / 5
            pts.append((m_arm / 5, np.array([rr * math.cos(a), rr * math.sin(a), z_rot])))
    unplaced = sum(x["mass_kg"] for x in comps.values() if x.get("position_m") is None)
    pts.append((unplaced, np.zeros(3)))           # wiring + contingency lumped at the centre [Y]
    m_tot = sum(m for m, _ in pts)
    cg = sum(m * r for m, r in pts) / m_tot
    for m, r in pts:
        q = r - cg
        I += m * (np.dot(q, q) * np.eye(3) - np.outer(q, q))
    s = A.state(BASE.cruise_km * 1e3)
    fl = B.FlowState(s.rho, s.mu, s.a)
    om_h = d.hover.per_rotor.omega
    curve = []
    for f in np.linspace(0.4, 1.6, 13):
        r = B.solve(d.rotor, om_h * f, fl)
        curve.append({"rpm": round(om_h * f * 30 / math.pi, 1), "thrust_N": round(r.thrust, 2),
                      "torque_Nm": round(r.torque * d.system.bemt_power_factor, 3),
                      "shaft_W": round(r.power * d.system.bemt_power_factor, 1)})
    I_rot = (d.breakdown["blades+hubs"] / 6 - 0.12) * d.rotor.radius ** 2 / 3.0   # blades as uniform rods [K]
    dep = res["deploy"]
    step = max(1, len(dep.t) // 200)
    return {
        "units": "SI; body frame x forward (between arms 1 and 6), y left, z up; rotor i at azimuth 30+60 i deg",
        "source": "python scripts/venus_day.py --final (aerokit.venus); tags K unless stated",
        "mass_kg": round(m_tot, 3), "cg_m": [round(x, 4) for x in cg],
        "inertia_kg_m2": [[round(x, 3) for x in row] for row in I],
        "rotors": [{"position_m": [round(arm * math.cos(a), 4), round(arm * math.sin(a), 4), round(z_rot, 3)],
                    "spin": sp, "radius_m": d.rotor.radius, "blades": d.rotor.blades,
                    "polar_inertia_kg_m2": round(I_rot, 4)} for a, sp in zip(az, ["ccw", "cw"] * 3)],
        "rotor_curve_at_cruise": curve,
        "hover": {"rpm": round(d.hover.rpm, 1), "thrust_per_rotor_N": round(d.hover.per_rotor.thrust, 2),
                  "shaft_W_total": round(d.hover.shaft_W, 0), "collective_deg": round(d.rotor.theta75_deg, 2)},
        "drag_area_m2": d.system.drag_area_m2,
        "max_airspeed_m_s": round(CT.max_airspeed(d.system, d.gross_kg * s.g, fl, d.hover.shaft_W * 1.6 ** 1.5), 2),
        "environment_cruise": {"altitude_m": BASE.cruise_km * 1e3, "density": round(s.rho, 4),
                               "temperature_K": round(s.T, 2), "gravity": round(s.g, 4),
                               "speed_of_sound": round(s.a, 1), "wind_west_m_s": round(A.zonal_wind(s.h), 1),
                               "vertical_gust_sigma_m_s": 0.7, "downdraft_episode_m_s": [2.0, 4.0]},
        "deployment_replay": [{"t_s": round(float(dep.t[i]), 3), "altitude_m": round(float(dep.h[i]), 2),
                               "descent_rate_m_s": round(float(dep.Vd[i]), 3)} for i in range(0, len(dep.t), step)],
        "mission_series": doc["operations"]["series_hourly"],
    }


def plt_size() -> float:
    import matplotlib.pyplot as plt

    return float(plt.rcParams.get("font.size", 18))


def markdown(out: dict) -> str:
    v, e, m = out["vehicle"], out["entry"], out["mission"]
    a = out["atmosphere_55km"]
    lines = ["# VESPER — computed numbers (python scripts/venus_day.py --final)", "",
             "| Quantity | Value | Tag |", "|---|---:|---|",
             f"| 55 km: T, p, ρ (Pioneer Venus mean) | {a['T_C']:.1f} °C, {a['p_bar']:.3f} bar, {a['rho']:.3f} kg/m³ | D/K |",
             f"| Gross mass | {v['gross_kg']:.1f} kg | K |",
             f"| Rotors | 6 × {v['D']:.1f} m, {v['rpm']:.0f} rpm, tip Mach {v['tip_mach']:.2f}, Re₀.₇₅ {v['re75']:.2g}, FM {v['FM']:.2f} | K |",
             f"| Hover / loiter electric power | {v['P_hover_elec_W']:.0f} W / {v['P_bucket_elec_W']:.0f} W at {v['V_bucket']:.1f} m/s | K |",
             f"| Solar overhead / sustains loiter above cos z | {v['P_solar_overhead_W']:.0f} W / {v['sustain_mu0_loiter']:.2f} | K |",
             f"| Battery | {v['battery_Wh']:.0f} Wh | K |",
             f"| Entry | {e['m_entry']:.0f} kg, β {e['beta']:.1f} kg/m², {e['VE'] / 1e3:.2f} km/s at {e['gamma_deg']}° | K |",
             f"| Peak deceleration / heating | {e['peak_g']:.0f} g; {e['peak_qconv_W_cm2']:.0f} + {e['peak_qrad_W_cm2']:.0f} W/cm²; {e['heat_load_kJ_cm2']:.1f} kJ/cm² (PV large probe {e['pv_peak_g']:.0f} g) | K |",
             f"| Parachute | opens {e['chute_km']:.1f} km, {e['chute_s']:.0f} s to release, {e['release_rate']:.1f} m/s at release | K |",
             f"| Release altitude loss | {e['pullout_loss_m']:.0f} m pre-spun vs {e['drop_loss_m']:.0f} m dropped unspun | K |",
             f"| Mission | {m['flight_h']:.1f} h flight, {m['sustained_h']:.1f} h on sunlight, {m['drift_km']:.0f} km drift | K |",
             f"| Relay (1000 km orbit, 5 W UHF) | {out['link']['pass_min']:.1f} min passes, {out['link']['Mbit_per_pass']:.0f} Mbit/pass | K |",
             f"| BEMT validation (torque, 27 points) | rms {100 * out['bemt_validation']['rms_error']:.1f} % | K vs D-ag |",
             f"| Hybrid alternative (neutral He cell) | {out['hybrid']['diameter_m']:.1f} m sphere, +{out['hybrid']['envelope_kg']:.0f} kg envelope | K |",
             "", "Events:", ""]
    lines += [f"- {t / 3600:.2f} h — {ev}" for t, ev in m["events"]]
    return "\n".join(lines) + "\n"


def _parse(argv: list[str]) -> tuple[dict, bool]:
    """``--payload-kg X``, ``--cruise-km X``, ``--rotor-d X`` (also ``--name=X``); ``--reuse``."""
    keys = {"payload-kg": "payload_kg", "cruise-km": "cruise_km", "rotor-d": "D"}
    over: dict = {}
    reuse = False
    i = 0
    while i < len(argv):
        a = argv[i].lower()
        if a in ("--reuse", "reuse"):
            reuse = True
        else:
            name, _, val = a.lstrip("-").partition("=")
            name = name.replace("_", "-")
            if name not in keys:
                raise SystemExit(f"unknown option {argv[i]!r}; use --payload-kg, --cruise-km, --rotor-d, --reuse")
            if not val:
                i += 1
                val = argv[i] if i < len(argv) else ""
            over[keys[name]] = float(val.replace(",", "."))
        i += 1
    return over, reuse


def main(argv: list[str] | None = None) -> int:
    global OUT, BASE
    protect_streams()
    over, reuse = _parse(list(argv or []))
    variant = bool(over)
    if variant:                           # mentor numbers: separate folder, never overwrite the hand-off files
        from dataclasses import replace as _rep

        BASE = _rep(DES.BASELINE, **over)
        tag = "_".join(f"{k}{v:g}" for k, v in sorted(over.items()))
        OUT = OUT.parent / f"out_variant_{tag}"
    OUT.mkdir(parents=True, exist_ok=True)
    import pickle

    cache = Path("D:/tmp_ideathon/venus/final_cache.pkl")
    if reuse and not variant and cache.exists():                # figure iteration only (not for delivery runs)
        c = pickle.loads(cache.read_bytes())
    else:
        c = compute()
        try:
            cache.write_bytes(pickle.dumps(c))
        except Exception:                                       # the cache is a convenience
            pass
    for k in ("trade", "sens"):                                 # always the latest sweep outputs (baseline folder)
        f = ROOT / "studies" / "final_2026" / "venus" / "out" / ("trade_sizing.json" if k == "trade" else "sensitivity.json")
        c[k] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    (OUT / "result.json").write_text(json.dumps(c["out"], indent=1, default=float, ensure_ascii=False), encoding="utf-8")
    (OUT / "result.md").write_text(markdown(c["out"]), encoding="utf-8")
    progress("drawing and auditing figures F1-F15")
    figures(c)
    progress("simulator parameters (vesper_for_simulator.json)")
    (OUT / "vesper_for_simulator.json").write_text(json.dumps(simulator_parameters(c), indent=1), encoding="utf-8")
    progress("regenerating design.json")
    import venus_design

    if variant:
        venus_design.main([], BASE, OUT.parent / f"design_variant_{OUT.name.removeprefix('out_variant_')}.json")
    else:
        venus_design.main([])
    n_err, line = audit_summary(OUT)
    print(console_text(markdown(c["out"])))
    print(console_text(line))
    v, m = c["out"]["vehicle"], c["out"]["mission"]
    verdict = "figures NOT deliverable (audit errors)" if n_err else "figures audited, deliverable"
    where = f"variant results in {OUT}" if variant else "design hand-off: studies/final_2026/venus/design.json"
    print(console_text(f"VESPER {v['gross_kg']:.1f} kg, {m['flight_h']:.0f} h flight; {verdict}. "
                       f"Next: read docs/25_lugus_venus_rotorcraft.md ({where})."))
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
