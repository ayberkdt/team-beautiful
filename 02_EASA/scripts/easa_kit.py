"""EASA day kit: the modular pieces around LOCK-SENSE, regenerated from the same model and inputs as canopy_day.py.

    python 02_EASA/scripts/easa_kit.py                 # ~1-2 min (Monte Carlo for 1..5 latch points)
    python 02_EASA/scripts/easa_kit.py --no-figures    # tables and checks only

Reads ``02_EASA/inputs/inputs.json`` (rates, tolerances, exposure: tags as there) and ``02_EASA/outputs/day/result.json``
(written by ``canopy_day.py``). Writes into ``02_EASA/kit/``:

* ``04_traceability.md`` / ``.csv`` — requirement → hazard → design feature → verification step → basis;
* ``07_bom_budget.md`` — bill of materials with mass and power ranges, checked against requirement R-10;
* ``08_other_aircraft.md`` — the same model for latches with 1–5 latch points (the "any aircraft" answer) [K];
* ``11_concept_trade.md`` — architectures and options side by side (numbers from result.json) [K + Y];

and slide figures K1–K4 into ``02_EASA/outputs/kit/`` (datawiz-audited, set ``kit.seti.json``). It also prints the
spoken-word and report-word counts of ``02_talk_4min.md`` and ``03_report_draft.md`` against their budgets.
Tags: [D] read at source, [K] computed here, [Y] our assumption.
"""
from __future__ import annotations

import csv
import dataclasses
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from day_common import console_text, protect_streams  # noqa: E402

from aerokit.canopy import montecarlo as mc  # noqa: E402
from aerokit.canopy.mechanism import EXTRA_NG  # noqa: E402

EASA = ROOT / "02_EASA"
KIT = EASA / "kit"
FIG = EASA / "outputs" / "kit"
WORDS_PER_S = 2.3            # speaking rate used for the talk budget [Y]
REPORT_WORDS_MAX = 2100      # 5 pages A4 (176 x 227 mm text area) with four figures at ~1/3 page each [Y]


def _canopy_day():
    spec = importlib.util.spec_from_file_location("canopy_day", EASA / "scripts" / "canopy_day.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------- 04 traceability
TRACE = [  # req, statement (short), hazards, design feature, verification (plan step), basis
    # steps (n) = the twelve steps of kit 03 §4 as revised on 5 Nov: 9 bench, 10 ground, 11 flight check, 12 train/maintain.
    # "Basis" = engineering basis; the official task sets certification aside, the cited documents are used as good practice.
    ("R-1", "LOCKED only if seated and every bolt beyond threshold", "H1 H2 H3", "S0 + one sensor per lug, hardware AND",
     "bench (9), state sequences (10)", "AD 2025-0156 reason; CS 23.1309 (practice)"),
    ("R-2", "P(LOCKED | partial) ≤ 1e-3; trip inside 67.5–68.7 mm", "H1", "trip point 68 mm handle-equivalent",
     "C2 [K]; rigging gauge (7, 10)", "AAIB pp. 9, 20 (60/70 mm)"),
    ("R-3", "Nuisance ≤ 1/10 of the unalerted-hazard rate", "cry wolf", "phase logic, taxi amber, persistence",
     "C3 [K]; ground run (10); flight check (11); log (12)", "AC 25.1322-1; R4 notes"),
    ("R-4", "No probable failure gives a false green", "H5", "self-checking outputs; SENS state",
     "FMEA; 13-case fault demo", "AC 23.1309-1E §11.b"),
    ("R-5", "Power or unit loss → green off, throttle free", "H5", "positive green, checklist 'green ON'; gate fail-free",
     "CB-pull test (10)", "AC 23.1309-1E §11.b"),
    ("R-6", "Red + voice ≤ 1 s at take-off power; 0.5 s persistence airborne", "H1 H2 H4", "phase logic, voice deferral",
     "logic tests (tests/test_canopy.py)", "AC 25.1322-1 inhibits (analogy)"),
    ("R-7", "Red warning, amber caution, green safe", "H5", "three-colour annunciator", "inspection",
     "CS 23.1322; CS-SC110a §3 (practice)"),
    ("R-8", "Voice audible, always paired with the light", "H1 H4", "audio-panel alert input + lamp",
     "ground run with headsets (10); flight check (11)", "AC 25.1322-1 App. 2"),
    ("R-9", "Nothing bridges canopy and fuselage", "H6", "fuselage-side sensors and harness",
     "jettison force test (10)", "CS 23.807(b)(5) (practice)"),
    ("R-10", "Mass ≤ 1.0 kg; continuous power ≤ 2 W at 14 V", "—", "inductive sensors < 60 g, < 10 mA",
     "weighing, current (10); BOM 07", "GAPS datasheet [D]"),
    ("R-11", "Power-up self-test; open-canopy plausibility", "H5", "lamp/voice test; bolt-without-seat → SENS",
     "logic tests; ground test (10)", "AC 23.1309-1E (latent faults)"),
    ("R-12", "Time-stamped event log incl. gate overrides; G1000 discrete", "H4 H7", "log in alert unit; EFIS data card",
     "download at the annual (12)", "AAIB p. 28 dispute; SR 2024-004/005"),
    ("R-13", "Throttle-knob vibration whenever the alert is red", "H1 H2 H4", "eccentric-mass shaker in the throttle knob",
     "flight check with gloves (11)", "task sheet (vibration); case-study slides 7–8"),
    ("R-14", "Ground-only take-off gate: throttle held at run-up while not locked, < 30 kt; breakout ≤ 50 N",
     "H1 H2 H3", "solenoid detent in the throttle quadrant, unpowered = free",
     "breakout and power-off test (10)", "task sheet (engine shut-down, rejected in flight); C3 [K]"),
]
TRACE_COLS = ["Req", "Statement", "Hazards", "Design feature", "Verification (step)", "Basis"]


# ---------------------------------------------------------------- 07 BOM
BOM = [  # item, qty, mass each low/high [g], power each low/high [W], tag, note
    ("Inductive proximity sensor, line-monitored (GAPS-class)", 4, 45, 60, 0.0, 0.14, "D+K",
     "< 60 g, 12–32 Vdc, < 10 mA [D]; 10 mA × 14 V = 0.14 W [K]"),
    ("Alert unit (logic, self-test, event log, audio driver)", 1, 100, 200, 0.3, 0.8, "Y", "no datasheet"),
    ("Annunciator (rear seat) + repeater (front)", 2, 25, 50, 0.05, 0.2, "Y", "one legend lit at a time"),
    ("Harness, 22 AWG, fuselage side, connectors", 1, 60, 150, 0.0, 0.0, "Y", "route length to be measured (step 2)"),
    ("Sensor brackets on existing lug fittings", 4, 10, 25, 0.0, 0.0, "Y", "no new holes if avoidable"),
    ("Circuit breaker 5 A + placard", 1, 15, 25, 0.0, 0.0, "Y", "AC 43.13-1B Table 11-3 [D-ag]"),
    ("Voice output into the audio panel (alert only)", 1, 0, 0, 0.0, 0.5, "Y", "only while an alert sounds"),
    ("Throttle-knob vibration motor + wiring (alert only)", 1, 5, 20, 0.0, 0.5, "Y", "phone-class eccentric-mass motor"),
    ("Take-off gate: solenoid detent + bracket (alert only)", 1, 80, 150, 0.0, 5.0, "Y",
     "energised only on the ground with the canopy not locked; unpowered = free"),
]
R10_MASS_G, R10_POWER_W = 1000.0, 2.0   # 5 Nov: raised from 0.6 kg to carry the shaker and the gate [Y]


def bom_rows() -> tuple[list[dict], dict]:
    rows, tot = [], {"m_lo": 0.0, "m_hi": 0.0, "p_lo": 0.0, "p_hi": 0.0, "p_hi_continuous": 0.0}
    for item, q, mlo, mhi, plo, phi, tag, note in BOM:
        r = {"Item": item, "Qty": q, "Mass (g)": f"{q * mlo:.0f}–{q * mhi:.0f}", "Power (W)": f"{q * plo:.2f}–{q * phi:.2f}",
             "Tag": tag, "Note": note}
        rows.append(r)
        tot["m_lo"] += q * mlo
        tot["m_hi"] += q * mhi
        tot["p_lo"] += q * plo
        tot["p_hi"] += q * phi
        if "alert only" not in item:
            tot["p_hi_continuous"] += q * phi
    return rows, tot


# ---------------------------------------------------------------- 08 other aircraft
def latch_study(cfg: dict, points=(1, 2, 3, 4, 5), n: int = 100_000) -> list[dict]:
    """Same channel rates, tolerances and exposure as the Extra NG study; only the number of latch points changes.
    'one_bolt' = one latch point not engaged. Travel 60→70 mm handle-equivalent kept [Y]."""
    out = []
    for k in points:
        mech = dataclasses.replace(EXTRA_NG, name=f"{k}-point latch", bolts=k)
        archs = {
            "seated": mc.Architecture("SO", "Seated sensor only", 1, ()),
            "one": mc.Architecture("S1", "Seated + one latch sensor", 1, (k - 1,)),
            "per_latch": mc.Architecture("SN", "One sensor per latch point", 1, tuple(range(k))),
        }
        row = {"points": k}
        for key, a in archs.items():
            rr = {h: mc.simulate(a, h, cfg["_rates"], cfg["_tol"], n=n, seed=11 + k, mech=mech) for h in (None, *mc.HAZARDS)}
            full = mc.takeoff_risk(rr, cfg["_exp"], "full")
            match = mc.takeoff_risk(rr, cfg["_exp"], "matching")
            row[key] = {"miss_partial": rr["partial"].p_locked, "miss_one": rr["one_bolt"].p_locked,
                        "rf_full": full["reduction_factor"], "rf_matching": match["reduction_factor"]}
        out.append(row)
    return out


# ---------------------------------------------------------------- 11 concept trade
OPTION_FACTS = {  # mass, power, route, cost class: doc 23 §3.3 (A3 mass/power D+Y, the rest Y)
    "A1": ("Seated switch only", "< 0.1 kg [Y]", "< 0.5 W [Y]", "standard/minor", "very low"),
    "A2": ("Seated + rear bolt", "≈ 0.3 kg [Y]", "< 1 W [Y]", "minor", "low"),
    "A3": ("LOCK-SENSE (chosen)", "0.5–0.6 kg [D+Y]", "< 2 W [D+Y]", "minor (EASA or DOA)", "low"),
    "A4": ("Dual everything", "≈ 0.9 kg [Y]", "< 3 W [Y]", "minor", "medium"),
    "PLUS": ("B · LOCK-SENSE Plus", "0.9–1.1 kg [Y]", "< 3 W [Y]", "minor + software assurance", "medium"),
    "POWER": ("C · Powered over-centre lock", "1.2–1.8 kg [Y]", "20–50 W for ~2 s [Y]", "major (TC holder / STC)", "high"),
}


def concept_rows(res: dict) -> list[dict]:
    rows = []
    for key, (label, mass, power, route, cost) in OPTION_FACTS.items():
        if key in res["architectures"]:
            a = res["architectures"][key]
            rf_f, rf_m = a["risk_full"]["reduction_factor"], a["risk_matching"]["reduction_factor"]
        else:
            o = res["options"][key]
            rf_f, rf_m = o["rf_full_vs_A0"], o["rf_matching_vs_A0"]
        rows.append({"key": key, "Option": label, "RF pilot acts": rf_f, "RF pilot matches": rf_m,
                     "Mass": mass, "Power": power, "Approval": route, "Cost": cost})
    return rows


# ---------------------------------------------------------------- word-count checks
def talk_check() -> list[str]:
    t = (KIT / "02_talk_4min.md").read_text(encoding="utf-8")
    sec = t.split("## Spoken text")[1].split("## Backup")[0]
    lines, total_w, total_b = [], 0, 0
    for p in sec.split("\n\n"):
        m = re.match(r"\*\*(.+?)\((\d+) s\)\.\*\*\s*(.*)", p, re.S)
        if not m:
            continue
        w, b = len(m.group(3).split()), int(m.group(2))
        total_w, total_b = total_w + w, total_b + b
        flag = "OK" if w / WORDS_PER_S <= b else "OVER"
        lines.append(f"  {m.group(1).strip():18s} {w:3d} words ≈ {w / WORDS_PER_S:5.1f} s of {b:3d} s  {flag}")
    lines.append(f"  total {total_w} words ≈ {total_w / WORDS_PER_S:.0f} s spoken; slide budget {total_b} s; hard cut 240 s")
    return lines


def report_check() -> str:
    t = (KIT / "03_report_draft.md").read_text(encoding="utf-8")
    body = t.split("## Title:")[1].split("## References")[0]
    body = re.sub(r"\*\(R\d[^)]*\)\*|\*Figure \d caption:\*", "", body)
    w = len(re.sub(r"[#*`|]", " ", body).split())
    return f"  report body ≈ {w} words (budget {REPORT_WORDS_MAX} for 5 pages with 4 figures) " + \
        ("OK" if w <= REPORT_WORDS_MAX else "OVER — cut before the docx")


# ---------------------------------------------------------------- tables to markdown
def md_table(rows: list[dict], cols: list[str]) -> tuple[str, list[str]]:
    import pandas as pd
    from datawiz import tablo
    df = pd.DataFrame(rows)[cols]
    return tablo.markdown_tablo(df), tablo.denetle(df)


def fmt_rf(x: float) -> str:
    return f"{x:,.0f}×".replace(",", " ") if x >= 100 else f"{x:.1f}×"


def write_tables(trace, bom, tot, latch, concept, res) -> dict:
    r3 = next(r for r in latch if r["points"] == 3)
    r3_one, r3_per = r3["one"]["rf_full"], r3["per_latch"]["rf_full"]
    res_a2 = res["architectures"]["A2"]["risk_full"]["reduction_factor"]
    res_a3 = res["architectures"]["A3"]["risk_full"]["reduction_factor"]
    res_a3_lb = res["architectures"]["A3"]["reduction_lower_bound_full"]
    KIT.mkdir(parents=True, exist_ok=True)
    audits = {}
    # 04
    rows = [dict(zip(TRACE_COLS, r)) for r in TRACE]
    md, audits["04"] = md_table(rows, TRACE_COLS)
    (KIT / "04_traceability.md").write_text(
        "# EASA kit · 04 — Requirements traceability (generated by `02_EASA/scripts/easa_kit.py`; do not edit)\n\n"
        "Every requirement of `02_EASA/docs/retrofit_plan.md` step 4 traced to the hazards of step 3, the design feature "
        "that meets it, the step that verifies it and its basis. H7 (structural failure, the AAIB G-MIIL cause) has no "
        "alert requirement: it is answered by the ICA bond inspection (kit `06`, task T5).\n\n" + md + "\n", encoding="utf-8")
    with (KIT / "04_traceability.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(TRACE_COLS)
        w.writerows(TRACE)
    # 07
    md, audits["07"] = md_table(bom, ["Item", "Qty", "Mass (g)", "Power (W)", "Tag", "Note"])
    mass_ok = "met" if tot["m_hi"] <= R10_MASS_G else ("met only at the low end" if tot["m_lo"] <= R10_MASS_G else "not met")
    pw_ok = "met" if tot["p_hi_continuous"] <= R10_POWER_W else "not met"
    (KIT / "07_bom_budget.md").write_text(
        "# EASA kit · 07 — Bill of materials, mass and power budget (generated by `easa_kit.py`)\n\n"
        "Ranges are low–high estimates per line (quantity included). Only the sensor limits are read from a datasheet "
        "(Honeywell GAPS, [D]); all other lines are [Y] and are replaced by weighing and current measurement in step 9.\n\n"
        + md + "\n\n"
        f"**Totals [K]:** mass {tot['m_lo']:.0f}–{tot['m_hi']:.0f} g; power {tot['p_lo']:.2f}–{tot['p_hi']:.2f} W "
        f"with every alert-only item running, {tot['p_hi_continuous']:.2f} W continuous.\n\n"
        f"**Against R-10 (≤ {R10_MASS_G:.0f} g, ≤ {R10_POWER_W:.0f} W):** mass {mass_ok}; continuous power {pw_ok}.\n"
        "The sensing part alone (sensors, unit, lamps, harness, brackets, breaker) is the 0.45–0.8 kg of the first "
        "kit version; the throttle shaker and the take-off gate (5 Nov, official task) add 85–170 g. The alert unit, the "
        "harness and the gate solenoid decide the total: weigh a harness mock-up and a candidate solenoid during the "
        "survey (step 2). Items marked *alert only* draw power only while an alert is active, so R-10 counts continuous "
        "power.\n", encoding="utf-8")
    # 08
    lines = ["| Latch points | Architecture | P(miss \\| partial) | P(miss \\| one point out) | RF, pilot acts | "
             "RF, pilot matches |", "|---:|---|---:|---:|---:|---:|"]
    names = {"seated": "Seated sensor only", "one": "Seated + one latch sensor", "per_latch": "One sensor per latch point"}
    for r in latch:
        for k, lab in names.items():
            x = r[k]
            lines.append(f"| {r['points']} | {lab} | {x['miss_partial']:.2g} | {x['miss_one']:.2g} | "
                         f"{fmt_rf(x['rf_full'])} | {fmt_rf(x['rf_matching'])} |")
    (KIT / "08_other_aircraft.md").write_text(
        "# EASA kit · 08 — Any aircraft: how many sensors does a latch with N points need? (generated by `easa_kit.py`)\n\n"
        "**Question it answers** (mentor Q2, \"pick your example aircraft (any)\"): does LOCK-SENSE transfer to a type "
        "with a different number of latch points (pins, shoot bolts, hooks)?\n\n"
        "**Model [K]:** the Extra NG study (`aerokit.canopy.montecarlo`) with the number of latch points changed and "
        "everything else kept: channel rates, rigging tolerances, 60→70 mm handle-equivalent travel, exposure and "
        "nuisance rate from `02_EASA/inputs/inputs.json` [D+Y]. \"One point out\" = one latch point not engaged, the "
        "others fine. 100 000 simulated flights per cell. Assumption [Y]: a common linkage (partial lock affects all "
        "points together) and the same per-flight hazard rates on every type.\n\n"
        + "\n".join(lines) + "\n\n"
        "**Reading [K]:** a seated (\"closed\") sensor never sees a partial lock or a missing point, on any type. One "
        "latch sensor sees the partial lock (all points move together) but misses a single point out with probability "
        "(N − 1)/N. Only one sensor per latch point keeps the miss rate at the rigging-error floor for every N. So the "
        "rule for any aircraft is: **one engagement sensor per latch point plus one seated sensor**; the parts count "
        "grows with N, the logic does not change. Under probability matching every architecture is limited to a few "
        "times by the nuisance rate, as on the Extra NG.\n\n"
        "**Cross-check [K]:** the 3-point rows must reproduce the Extra NG study (`02_EASA/outputs/day/result.json`: A2 "
        f"{fmt_rf(res_a2)}, A3 {fmt_rf(res_a3)} with 200 000 flights, 95 % lower bound {fmt_rf(res_a3_lb)}) within Monte Carlo "
        f"noise; here {fmt_rf(r3_one)} and {fmt_rf(r3_per)} with 100 000 flights per cell.\n\n"
        "**For a new type, measure first (step 2):** number of latch points, whether they share one linkage, handle or "
        "pin travel between partial and full engagement, free space for a sensor within its sensing range at each "
        "point, and whether an open-and-released canopy reads like a locked one at the handle.\n", encoding="utf-8")
    # 11
    lines = ["| Option | RF, pilot acts [K] | RF, pilot matches [K] | Mass | Power | Real-world approval (outside the task) | "
             "Cost class [Y] |",
             "|---|---:|---:|---|---|---|---|"]
    for r in concept:
        lines.append(f"| {r['Option']} | {fmt_rf(r['RF pilot acts'])} | {fmt_rf(r['RF pilot matches'])} | {r['Mass']} | "
                     f"{r['Power']} | {r['Approval']} | {r['Cost']} |")
    (KIT / "11_concept_trade.md").write_text(
        "# EASA kit · 11 — Concepts side by side (generated by `easa_kit.py` from `02_EASA/outputs/day/result.json`)\n\n"
        "RF = reduction of the per-flight probability of starting the take-off unlocked with no effective alert, "
        "relative to no system. *Pilot acts* = every true alert is acted on; *pilot matches* = the pilot acts as often "
        "as alerts have been right (probability matching, abstract-level evidence). Option effect factors are [Y] "
        "(`inputs.json` → `options`). D (two-stage restraint) changes severity, not probability, and is not in the table "
        "(doc 23 §3.3).\n\n" + "\n".join(lines) + "\n\n"
        "**Reading:** every alert-only option collapses to about 3× when pilots stop trusting it, however many sensors "
        "it has; the powered over-centre lock keeps about 6× because it removes hazards instead of warning about them. "
        "That is the ladder: A3 now, C next with the manufacturer (it changes the latch itself), B only once the nuisance "
        "budget R-3 is shown. The official task sets certification and cost aside, so the approval column is context, not "
        "a criterion. The throttle shaker and the ground-only take-off gate (kit `12`) are not in this table: they are "
        "not modelled yet. Figure K1.\n", encoding="utf-8")
    return audits


# ---------------------------------------------------------------- figures
def figures(latch: list[dict], concept: list[dict]) -> list[str]:
    import datawiz as dw
    import matplotlib.patches as mp
    cd = _canopy_day()
    FIG.mkdir(parents=True, exist_ok=True)
    S = dw.Seti(str(FIG / "kit.seti.json"), hedef="sunum-tam")
    S.nicelik("rrf", "Risk reduction factor", None, eksen="y", olcek="log")
    S.nicelik("option", "Design option", None, eksen="x")
    S.nicelik("points", "Latch points on the canopy", None, eksen="x")
    for name, col in (("Pilot always acts", "#07648e"), ("Pilot matches reliability", "#5f5f5f"),
                      ("Seated sensor only", "#d55e00"), ("Seated + one latch sensor", "#e69f00"),
                      ("One sensor per latch point", "#0072b2")):
        S.varlik(name, renk=col)
    done = []

    # K1 — concept ladder (vertical dumbbell, log y)
    fig, ax = S.figur(oran=0.55)
    xs = np.arange(len(concept))
    full = np.array([r["RF pilot acts"] for r in concept])
    match = np.array([r["RF pilot matches"] for r in concept])
    ax.vlines(xs, match, full, colors="#bdbdbd", linewidth=2, zorder=1)
    for vals, lab in ((full, "Pilot always acts"), (match, "Pilot matches reliability")):
        st = S.stil(lab, isaretli=True)
        st["linestyle"] = "none"
        ax.plot(xs, vals, zorder=3, **st)
    short = {"A1": "A1 seated\nswitch", "A2": "A2 seated\n+ rear bolt", "A3": "A3\nLOCK-SENSE", "A4": "A4 dual\neverything",
             "PLUS": "B LOCK-SENSE\nPlus", "POWER": "C powered\nlock"}
    ax.set_xticks(xs, [short[r["key"]] for r in concept])
    ax.set_xlim(-0.5, len(concept) - 0.5)
    ax.set_ylim(0.5, 1e5)
    S.eksen(ax, x="option", y="rrf")
    cd.pow10(ax, "y")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(FIG / "K1_concept_ladder"), sessiz=True)
    done.append("K1_concept_ladder")

    # K2 — any aircraft: RF (pilot acts) vs number of latch points
    fig, ax = S.figur(oran=0.55)
    pts = [r["points"] for r in latch]
    for key, lab in (("seated", "Seated sensor only"), ("one", "Seated + one latch sensor"),
                     ("per_latch", "One sensor per latch point")):
        ax.plot(pts, [max(r[key]["rf_full"], 1.0) for r in latch], **S.stil(lab, isaretli=True))
    ax.set_xticks(pts)
    ax.set_xlim(0.7, max(pts) + 0.3)
    ax.set_ylim(0.5, 1e4)
    S.eksen(ax, x="points", y="rrf")
    cd.pow10(ax, "y")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(FIG / "K2_any_aircraft_latch_points"), sessiz=True)
    done.append("K2_any_aircraft_latch_points")

    # K3 — retrofit process, twelve engineering steps with a test gate per block (5 Nov: certification set aside by
    # the official task, so no approval gates)
    fig, ax = S.figur(oran=0.56)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    phases = [("Define", ["1 Pick aircraft", "2 Survey", "3 Hazards + HF"], "Test: every\nhazard has a req."),
              ("Design", ["4 Requirements", "5 Sensors + cues", "6 Logic"], "Test: logic passes\nfault demo"),
              ("Build & test", ["7 Mount + rig", "8 Wire + EFIS", "9 Bench test", "10 Ground test"],
               "Test: every single\nfault caught"),
              ("Operate", ["11 Flight check", "12 Train + gauge"], "Loop: log +\nnuisance review")]
    w, gap = 0.215, 0.04
    for i, (ph, steps, gate) in enumerate(phases):
        x0 = 0.01 + i * (w + gap)
        ax.text(x0 + w / 2, 0.95, ph, ha="center", va="center", fontweight="bold")
        for j, s in enumerate(steps):
            y = 0.80 - j * 0.15
            ax.add_patch(mp.FancyBboxPatch((x0, y - 0.055), w, 0.11, boxstyle="round,pad=0.005,rounding_size=0.015",
                                           facecolor="#f2f2f2", edgecolor="#7f7f7f", linewidth=1))
            ax.text(x0 + w / 2, y, s, ha="center", va="center")
        ax.add_patch(mp.FancyBboxPatch((x0, 0.02), w, 0.17, boxstyle="round,pad=0.005,rounding_size=0.015",
                                       facecolor="#dbe9f5", edgecolor="#0072b2", linewidth=1.6))
        ax.text(x0 + w / 2, 0.105, gate, ha="center", va="center", color="#0b3c5d")
        if i < len(phases) - 1:
            ax.annotate("", xy=(x0 + w + gap - 0.004, 0.105), xytext=(x0 + w + 0.006, 0.105),
                        arrowprops={"arrowstyle": "-|>", "color": "#0072b2", "lw": 1.6})
    S.kaydet(fig, str(FIG / "K3_retrofit_process"), sessiz=True)
    done.append("K3_retrofit_process")

    # K4 — LOCK-SENSE architecture (diagram)
    fig, ax = S.figur(oran=0.56)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def box(x, y, w_, h, text, new=False, bold=False):
        ax.add_patch(mp.FancyBboxPatch((x, y), w_, h, boxstyle="round,pad=0.004,rounding_size=0.012",
                                       facecolor="#dbe9f5" if new else "#f2f2f2",
                                       edgecolor="#0072b2" if new else "#7f7f7f", linewidth=1.5 if new else 1))
        ax.text(x + w_ / 2, y + h / 2, text, ha="center", va="center", fontweight="bold" if bold else "normal")

    ax.text(0.105, 0.95, "Canopy (moving)", ha="center", va="center", fontweight="bold")
    ax.text(0.375, 0.95, "Fuselage rim", ha="center", va="center", fontweight="bold")
    ax.text(0.625, 0.95, "Alert unit", ha="center", va="center", fontweight="bold")
    ax.text(0.885, 0.95, "Cockpit", ha="center", va="center", fontweight="bold")
    rows_y = [0.74, 0.58, 0.42, 0.26]
    left = ["Steel target", "Bolt 1 tip", "Bolt 2 tip", "Bolt 3 tip"]
    mid = ["S0 seated", "S1 lug 1", "S2 lug 2", "S3 lug 3"]
    for y, a, b in zip(rows_y, left, mid):
        box(0.02, y, 0.17, 0.11, a)
        box(0.29, y, 0.17, 0.11, b, new=True)
        ax.annotate("", xy=(0.287, y + 0.055), xytext=(0.193, y + 0.055),
                    arrowprops={"arrowstyle": "-|>", "color": "#7f7f7f", "lw": 1, "linestyle": ":"})
        ax.annotate("", xy=(0.517, y + 0.055), xytext=(0.463, y + 0.055),
                    arrowprops={"arrowstyle": "-|>", "color": "#0072b2", "lw": 1.4})
    ax.plot([0.24, 0.24], [0.22, 0.89], color="#d55e00", lw=1.4, ls="--")
    ax.text(0.24, 0.12, "split line:\nnothing crosses", ha="center", va="center", color="#9c3f00")
    box(0.52, 0.26, 0.21, 0.59, "green only if\nS0 and S1–S3\n\nphase logic\nself-test\nevent log", new=True)
    box(0.52, 0.03, 0.21, 0.15, "throttle, IAS\n14 V bus")
    ax.annotate("", xy=(0.625, 0.257), xytext=(0.625, 0.183),
                arrowprops={"arrowstyle": "-|>", "color": "#7f7f7f", "lw": 1})
    # 5 Nov: four cues of the official task's list (visual, auditory, vibration, take-off gate) + G1000 record
    outs = [("3-colour lamp", 0.775), ("Chime / voice", 0.625), ("Throttle shaker", 0.475),
            ("Take-off gate", 0.325), ("G1000 + log", 0.175)]
    for text, y in outs:
        box(0.79, y, 0.20, 0.10, text, new=True)
        ax.annotate("", xy=(0.787, y + 0.05), xytext=(0.733, min(max(y + 0.05, 0.30), 0.82)),
                    arrowprops={"arrowstyle": "-|>", "color": "#0072b2", "lw": 1.4})
    S.kaydet(fig, str(FIG / "K4_lock_sense_architecture"), sessiz=True)
    done.append("K4_lock_sense_architecture")
    return done


def audit_lines(names: list[str]) -> list[str]:
    out = []
    for n in names:
        t = (FIG / f"{n}.denetim.txt").read_text(encoding="utf-8")
        m = re.search(r"(\d+) HATA", t)
        out.append(f"  {n}: {m.group(0) if m else '? HATA'}")
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help", "/?") for a in argv):
        print(console_text(__doc__))
        return 0
    protect_streams()
    cd = _canopy_day()
    cfg = cd.load(EASA / "inputs" / "inputs.json")
    res = json.loads((EASA / "outputs" / "day" / "result.json").read_text(encoding="utf-8"))
    bom, tot = bom_rows()
    latch = latch_study(cfg)
    concept = concept_rows(res)
    audits = write_tables(TRACE, bom, tot, latch, concept, res)
    print("tables: 04_traceability.md/.csv, 07_bom_budget.md, 08_other_aircraft.md, 11_concept_trade.md")
    for k, a in audits.items():
        print(f"  table {k} audit: {len(a)} findings" + (": " + "; ".join(a) if a else ""))
    print("talk check (02_talk_4min.md):")
    print("\n".join(talk_check()))
    print("report check (03_report_draft.md):")
    print(report_check())
    if "--no-figures" not in argv:
        names = figures(latch, concept)
        print(f"figures in {FIG.relative_to(ROOT).as_posix()}:")
        print("\n".join(audit_lines(names)))
        set_report = FIG / "kit.tutarlilik.txt"
        if set_report.exists():
            print("  set: " + set_report.read_text(encoding="utf-8").splitlines()[0])
    print("Result: EASA kit pieces regenerated. Next step: open 02_EASA/kit/00_KIT_INDEX.md and look at the PNGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
