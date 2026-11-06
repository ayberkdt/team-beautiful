"""Case 5 — GNSS-independent approach guidance from a ground sensor (doc 18 / prev_guess, "guidance" reading).

    python 03_Advionics/cases/case_5_gnss_independent_approach/run.py [--quick] [--set radar_range_at_gate_m=2500]

Reuses ``aerokit.approach`` (NavSensor, monte_carlo_approach, simulate_approach with a dissimilar monitor,
protection_level, separation_threshold, fault_bound). The earlier card-driven version is
``prev_guess/03_Advionics/scripts/approach_day.py``.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit import approach as A  # noqa: E402

NM = 1852.0
FT = 0.3048


def make_sensors(p: dict) -> dict[str, A.NavSensor]:
    out = {}
    r = p["radar_range_at_gate_m"]
    for s in p["sensors"]:
        if "angle_deg" in s:
            ang = r * math.radians(s["angle_deg"])
            sig = (s.get("range_sigma_m", 7.0), ang, ang)
        else:
            sig = tuple(s["sigma"])
        out[s["name"]] = A.NavSensor(s["name"], bias=tuple(s.get("bias", (0, 0, 0))), sigma=sig, tau=s.get("tau", 30.0),
                                     ramp=tuple(s.get("ramp", (0, 0, 0))), ramp_start=s.get("ramp_start", math.inf))
    return out


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "gate accuracy per navigation source + spoofing monitor")
    p = c.p
    rwy = A.Runway(p["rwy_lat"], p["rwy_lon"], p["rwy_elev_m"], p["rwy_course_deg"])
    cfg = A.ApproachSimConfig(x0=p["start_range_nm"] * NM)
    sens = make_sensors(p)
    mc = A.monte_carlo_approach(rwy, sens, gate_height=p["gate_height_ft"] * FT, runs=int(p["runs"]), cfg=cfg,
                                seed=int(p["seed"]))
    val = p["vertical_alert_limit_m"]
    rows = [{"source": k, "v_p95": v["vertical_p95_abs"], "l_p95": v["lateral_p95_abs"],
             "within_val": "yes" if v["vertical_p95_abs"] <= val else "NO",
             "pl": A.protection_level(sens[k].sigma[2], p["integrity_risk"])} for k, v in mc.items()]
    mon, spf = sens[p["monitor_sensor"]], sens[p["spoof_sensor"]]
    thr_v = A.separation_threshold(spf.sigma[2], mon.sigma[2], p["p_false_alert"])
    thr = (1e9, A.separation_threshold(spf.sigma[1], mon.sigma[1], p["p_false_alert"]), thr_v)
    alone = A.simulate_approach(rwy, spf, cfg, np.random.default_rng(int(p["seed"])))
    watched = A.simulate_approach(rwy, spf, cfg, np.random.default_rng(int(p["seed"])), monitor=mon, threshold=thr)
    fb = A.fault_bound(thr_v, math.hypot(spf.sigma[2], mon.sigma[2]))
    alarm_h = watched.extra.get("alarm_height")
    key = [("95 % vertical error at the gate", "; ".join(f"{r['source']}: {r['v_p95']:.1f} m" for r in rows)),
           ("spoofed GNSS alone vs monitored",
            f"undetected error {alone.extra.get('undetected_error', float('nan')):.0f} m alone; with "
            f"{p['monitor_sensor']}: alarm at {alarm_h:.0f} m height, largest undetected "
            f"{watched.extra.get('undetected_error', float('nan')):.0f} m" if alarm_h is not None
            else "monitor did not alarm in this run"),
           ("monitor threshold / fault bound (vertical)", f"{thr_v:.1f} m / {fb:.1f} m vs VAL {val:g} m")]
    body = ["## Gate statistics per navigation source", "",
            md_table(rows, ["source", "v_p95", "l_p95", "within_val", "pl"],
                     {"v_p95": ".1f", "l_p95": ".1f", "pl": ".1f"}), "",
            f"v_p95 / l_p95: 95th percentile |deviation| at {p['gate_height_ft']:g} ft [m], {int(p['runs'])} runs; "
            f"pl: fault-free protection level K·σ_vertical at integrity risk {p['integrity_risk']:g} [m]. "
            "Radar angle errors are converted at the radar-to-gate range (R·δ).", "",
            "The ground sensor is the sponsor's world (PSR/SSR/IFF arrays, PAR); the monitor logic is the same "
            "rule as the cockpit panel: no valid source → needles removed, never centred (atc.guidance)."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("vp95", "95th-percentile vertical error at the 200 ft gate", "m", eksen="x")
        S.nicelik("source", "Navigation source", None, eksen="y")
        S.varlik("Gate error")
        fig, ax = S.figur(oran=0.55)
        ys = np.arange(len(rows))
        ax.scatter([r["v_p95"] for r in rows], ys, zorder=3, **S.stil("Gate error", tur="sacilim"))
        ax.set_yticks(ys, [r["source"] for r in rows])
        ax.set_xlim(0, max(max(r["v_p95"] for r in rows), val) * 1.15)
        S.eksen(ax, x="vp95", y="source")
        ax.axvline(val, color="#3b3b3b", linewidth=1.2, linestyle="--")
        ax.text(val, len(rows) - 0.5, f" alert limit {val:g} m", va="center", ha="left", color="#3b3b3b")
        figs.append(save_figure(S, fig, c.out, "C5_gate_deviation_by_source"))
    c.finish("Case 5 — GNSS-independent approach guidance", key, "\n".join(body), figs)
    return {"rows": rows, "alarm_height": alarm_h, "key": key}


if __name__ == "__main__":
    main()
