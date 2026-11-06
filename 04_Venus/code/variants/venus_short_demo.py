#!/usr/bin/env python3
"""Short technology-demonstrator variant: no science payload, no dives, one short daylight mission.

Why: the LuGus spoiler deck (6 Nov 2026) asks for "a credible technology demonstrator" and says "keep the mission
short: no science goals, only controlled flight". The baseline carries 3 kg of science and flies 44 h with dives.

What it does (6 Nov power model of ``venus_budget_update``, rotor-rotor interaction included):
  1. Closes the mass for payload 3 / 1.5 / 0.5 / 0 kg, same 2.6 m rotors, 70 m/s tip speed, 0.10 m gap.
  2. Flies each design without dives, released at the morning threshold and later in the morning.
  3. Checks the 3 kg row against the budget result, so a change in this script cannot pass silently.

Mission thresholds below are proposals [Y], not requirements from the sponsor.
Writes only ``04_Venus/outputs/variants/short_demo/``. Nothing else in ``outputs/`` changes.

    python 04_Venus/code/variants/venus_short_demo.py
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "04_Venus" / "code" / "analysis")]

import venus_budget_update as B  # noqa: E402

from aerokit.venus import power as PW  # noqa: E402
from aerokit.venus import sizing as S  # noqa: E402

OUT = ROOT / "04_Venus" / "outputs" / "variants" / "short_demo"
PAYLOADS = ((3.0, 30.0, "baseline science"), (1.5, 15.0, "half payload"), (0.5, 5.0, "flight camera and recorder [Y]"),
            (0.0, 0.0, "no payload"))
DEMO_H = 6.0                 # proposed full-success length after release [Y]
MIN_HOLD_H = 1.0             # proposed minimum success: controlled hold at cruise [Y]
RELAY_PERIOD_H = 1.8         # doc 25 §6.1: one pass about every 1.8 h
LATE_RELEASE_DEG = -20.0     # later release: the array covers hover through the demonstration [K]
NO_DIVES = B.Profile(dive_times_h=(), label="short demo")


def demo(d: S.Design, tab: B.PowerTable, H0: float) -> dict:
    """Fly the demonstration block only."""
    fl = B.fly(d, tab, NO_DIVES, H0, stop_h=DEMO_H)
    z = d.req.altitude_m
    hover = tab.at(tab.hover_W, z) + d.P_sys_W
    loiter = tab.at(tab.level_W, z) + d.P_sys_W
    cruise = B.event(fl, "cruise altitude reached")
    t_c = cruise["t_h"] if cruise else None
    at = (fl.t / 3600.0 >= t_c) if t_c is not None else fl.t >= 0
    return {"release_hour_angle_deg": H0, "release_mu0": math.cos(math.radians(H0)), "cruise_reached_h": t_c,
            "min_soc": float(fl.soc.min()), "end_soc": float(fl.soc[-1]), "T_peak_C": float(fl.T_int.max()),
            "min_array_over_hover": float((fl.p_sun[at] / hover).min()),
            "min_array_over_loiter": float((fl.p_sun[at] / loiter).min()),
            "relay_passes": math.floor(DEMO_H / RELAY_PERIOD_H), "end": fl.end_reason or "planned stop"}


def row(kg: float, watts: float, note: str, models: dict, case: str = "nominal") -> dict:
    im = models[case]
    d = B.close_with_interaction(im, payload_kg=kg, payload_W=watts)
    tab = B.power_table(d, im, NO_DIVES)
    z = d.req.altitude_m
    arr = PW.SolarArray(d.solar_area_m2, d.req.solar_efficiency)
    hover = tab.at(tab.hover_W, z) + d.P_sys_W
    mu_l, mu_h = B.threshold_mu0(d, tab), S._mu0_for(hover, arr, z)
    H_early = B.release_angle(mu_l)
    fl, horizon = B.tuned_flight(d, tab, NO_DIVES, H_early)
    late = demo(d, tab, LATE_RELEASE_DEG)
    early = demo(d, tab, H_early)
    return {"payload_kg": kg, "payload_W": watts, "note": note, "case": case, "converged": d.converged, "gross_kg": d.gross_kg,
            "breakdown_kg": dict(d.breakdown), "battery_Wh": d.battery_Wh, "hover_W": hover,
            "loiter_W": tab.at(tab.level_W, z) + d.P_sys_W, "loiter_speed_m_s": tab.at(tab.v_best, z),
            "solar_overhead_W": arr.power(z, 1.0), "mu0_loiter": mu_l, "mu0_hover": mu_h,
            "reserve_h": d.battery_Wh / hover, "root_chord_m": d.rotor.root_chord,
            "longest_flight_h": fl.flight_h, "longest_sun_h": fl.sun_h, "sunset_horizon_h": horizon, "demo_early": early, "demo_late": late,
            "entry": B.entry_check(d.gross_kg), "_d": d, "_tab": tab}


def battery_only(r: dict) -> dict:
    """Hand check: could the deck go? Energy from release to the end of the minimum hold, against the deck mass."""
    d, tab, z = r["_d"], r["_tab"], r["_d"].req.altitude_m
    down = tab.at(tab.down_W, z) + d.P_sys_W
    t_down = r["demo_late"]["cruise_reached_h"]
    need = down * t_down + r["loiter_W"] * MIN_HOLD_H
    per_kg = d.req.battery.usable_Wh_per_kg()
    deck = d.breakdown["solar"]
    return {"energy_Wh": need, "descent_W": down, "battery_kg": need / per_kg, "deck_plus_baseline_battery_kg": deck + d.breakdown["battery"],
            "usable_Wh_per_kg": per_kg, "tag": "K on Y, no closure, contingency not applied"}


def public(r: dict) -> dict:
    return {k: v for k, v in r.items() if not k.startswith("_")}


def markdown(res: dict) -> str:
    rows = res["rows"]
    t = ["# Short demonstrator variant", "", f"Written by `{res['generated_by']}`. Status: variant, not confirmed by the team.",
         "Power model: 6 Nov budget, nominal interaction, current `guc_egrisi.json`. The simulator has **not** flown these designs.", "",
         "| Payload kg | Gross kg | Battery Wh | Hover W | Loiter W | Sun carries loiter, cos z | Sun carries hover, cos z | Longest flight h | Entry mass kg |",
         "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        t.append(f"| {r['payload_kg']:.1f} | {r['gross_kg']:.2f} | {r['battery_Wh']:.0f} | {r['hover_W']:.0f} | {r['loiter_W']:.0f} | "
                 f"{r['mu0_loiter']:.3f} | {r['mu0_hover']:.3f} | {r['longest_flight_h']:.1f} | {r['entry']['entry_mass_kg']:.0f} |")
    t += ["", f"## {DEMO_H:.0f} h demonstration, no dives", "",
          "| Payload kg | Release | cos z | Cruise reached h | Lowest SoC | Peak interior °C | Array / hover, lowest | Array / loiter, lowest |",
          "|---:|:---|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        for name, k in (("early", "demo_early"), ("late", "demo_late")):
            m = r[k]
            t.append(f"| {r['payload_kg']:.1f} | {name} | {m['release_mu0']:.2f} | {m['cruise_reached_h']:.2f} | {m['min_soc']:.2f} | {m['T_peak_C']:.1f} | "
                     f"{m['min_array_over_hover']:.2f} | {m['min_array_over_loiter']:.2f} |")
    c, bo, x = res["cases_no_payload"], res["battery_only"], res["crosscheck"]
    t += ["", "## Checks", "",
          f"- 3 kg row against the budget: {x['gross_3kg']:.2f} kg here, {x['budget_result_gross_kg']:.2f} kg in `budget_update/result.json`.",
          f"- With dives, 3 kg: {x['flight_with_dives_h']:.1f} h here, 43.5 h printed in `v0_7_44p6kg/CHANGES.md`, 43.8 h in `budget_update/result.json` (older curves).",
          f"- Mass growth: {x['growth_kg_per_kg']:.2f} kg of gross per kg of payload here; 2.4 to 2.5 in `sensitivity.json` (4 Nov, isolated rotors).",
          "- No payload, by interaction case: " + ", ".join(f"{k} {v['gross_kg']:.2f} kg, loiter {v['loiter_W']:.0f} W, late-release lowest SoC {v['min_soc']:.2f}" for k, v in c.items()) + ".",
          "", "## Could the solar deck go?", "",
          f"Release to the end of a {MIN_HOLD_H:.0f} h hold needs {bo['energy_Wh']:.0f} Wh at {bo['descent_W']:.0f} W descent. At {bo['usable_Wh_per_kg']:.0f} usable Wh/kg that is {bo['battery_kg']:.1f} kg of battery, "
          f"against {bo['deck_plus_baseline_battery_kg']:.1f} kg for deck plus battery now. [{bo['tag']}]", "",
          "## Not done", "",
          "- Pull-out battery current and canopy clearance were not rerun for these masses.",
          "- Mission thresholds (1 h hold, 6 h demonstration) are proposals, not sponsor numbers.",
          "- `design.json` and `sim_params.json` were not written for this variant.", ""]
    return "\n".join(t)


def compute() -> dict:
    raw = json.loads(B.CURVES.read_text(encoding="utf-8"))
    pts = B._points()
    base = S.close(2.6, 70.0)
    models = B.build_models(raw, base, pts)
    rows = [row(kg, w, note, models) for kg, w, note in PAYLOADS]
    ref, zero = rows[0], rows[-1]
    budget = json.loads((ROOT / "04_Venus/outputs/variants/budget_update/result.json").read_text(encoding="utf-8"))
    with_dives = B.fly_case(ref["_d"], models["nominal"], B.Profile())
    cases = {}
    for c in ("low", "nominal", "high"):
        r = row(0.0, 0.0, "no payload", models, c)
        cases[c] = {"gross_kg": r["gross_kg"], "loiter_W": r["loiter_W"], "hover_W": r["hover_W"], "mu0_hover": r["mu0_hover"], "min_soc": r["demo_late"]["min_soc"]}
    return {"generated_by": "python 04_Venus/code/variants/venus_short_demo.py", "curves_file": str(B.CURVES), "status": "variant, not confirmed",
            "source_of_change": "LuGus spoiler deck, 6 Nov 2026: no science goals, short mission",
            "assumptions_Y": {"demo_h": DEMO_H, "min_hold_h": MIN_HOLD_H, "late_release_deg": LATE_RELEASE_DEG},
            "rows": [public(r) for r in rows], "cases_no_payload": cases, "battery_only": battery_only(zero),
            "crosscheck": {"gross_3kg": ref["gross_kg"], "budget_result_gross_kg": budget["recommended_design"]["gross_kg"],
                           "flight_with_dives_h": with_dives["flight_h"], "growth_kg_per_kg": (ref["gross_kg"] - zero["gross_kg"]) / (ref["payload_kg"] - zero["payload_kg"])}}


def main() -> int:
    res = compute()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    (OUT / "result.md").write_text(markdown(res), encoding="utf-8")
    print(markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
