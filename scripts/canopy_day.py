"""Competition-day command for the EASA canopy-alert retrofit: inputs JSON → analysis, report and slide figures.

    python scripts/canopy_day.py studies/final_2026/easa/inputs.json

Runs ``aerokit.canopy``: (1) Monte Carlo of missed alerts / false alarms for five sensor architectures on the Extra NG
shoot-bolt latch, (2) take-off risk with the pilot in the loop (full compliance vs probability matching), (3) the
trip-point tolerance window, (4) the fault tree of the recommended architecture vs Monte Carlo (common-cause check),
(5) ERCS barrier gain, (6) FMEA with per-flight probabilities, (7) two scripted logic traces (G-MIIL-type partial lock
before take-off; SP-HMM-type in-flight unlock), and (8) the occurrence dataset summary if
``research_notes/EASA kanopi/R2_occurrences.csv`` exists.
Writes ``<inputs folder>/out/result.json``, ``report.md`` and audited slide figures C1–C4 (+C5) (datawiz, sunum-tam).
Every input carries its source and tag in the JSON; the report repeats them.
"""
from __future__ import annotations

import csv
import json
from dataclasses import replace
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from day_common import audit_summary, console_text, progress, protect_streams, sig, wants_help  # noqa: E402

from aerokit.canopy import (AlertLevel, CanopyAlertUnit, FlightInputs, Reading, barriers, faults, fmea,  # noqa: E402
                            fta)
from aerokit.canopy import montecarlo as mc  # noqa: E402
from aerokit.canopy.mechanism import EXTRA_NG, trip_probabilities, trip_window  # noqa: E402

A, I = Reading.ACTIVE, Reading.INACTIVE
BOLTS = ("bolt_front", "bolt_centre", "bolt_rear")
LOCK = ("not_locked", "partially_latched")
OCC_CSV = ROOT / "research_notes" / "EASA kanopi" / "R2_occurrences.csv"


def v(node: dict) -> float:
    return node["value"]


def load(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    r, t, e = cfg["rates"], cfg["tolerance"], cfg["exposure"]
    cfg["_rates"] = mc.ChannelRates(v(r["stuck_active_per_h"]), v(r["stuck_inactive_per_h"]), v(r["open_per_h"]),
                                    v(r["short_per_h"]), v(r["flight_h"]), v(r["latent_interval_h"]))
    cfg["_tol"] = mc.Tolerance(v(t["trip_mm"]), v(t["sigma_trip_mm"]), v(t["sigma_full_mm"]), v(t["hazard_below_mm"]),
                               v(t["p_misrig_common"]), v(t["misrig_shift_mm"]))
    cfg["_exp"] = mc.Exposure({h: v(e["p_hazard"][h]) for h in mc.HAZARDS},
                              {h: v(e["p_pilot_miss"][h]) for h in mc.HAZARDS}, v(e["p_nuisance"]))
    return cfg


def with_false_alarm(res: dict, fa: float, n: int = 10**7) -> dict:
    """Copy of the A3 results with the no-hazard false-alarm probability replaced (for the cry-wolf sweep)."""
    k = int(round(fa * n))
    return {**res, None: mc.ConditionalResult(res[None].architecture, None, n, {mc.LOCKED: n - k,
                                                                                 mc.CLOSED_UNLOCKED: k})}


def logic_traces() -> dict[str, list]:
    locked = {"seated": A, **{b: A for b in BOLTS}}
    partial = {"seated": A, **{b: I for b in BOLTS}}
    rear_out = {**locked, "bolt_rear": I}
    out = {}
    u = CanopyAlertUnit()
    rows = []
    script = [(0, {}, partial, "master ON after closing canopy (handle released, not pulled)"),
              (5, {}, partial, "pre-start checks"),
              (60, {"engine_running": True, "throttle": 0.2}, partial, "engine running, taxi"),
              (240, {"engine_running": True, "throttle": 0.5}, partial, "power checks at the holding point"),
              (300, {"engine_running": True, "throttle": 1.0}, partial, "take-off power applied"),
              (302, {"engine_running": True, "throttle": 0.0, "ias_kt": 15}, partial, "pilot rejects, throttle closed"),
              (330, {"engine_running": True, "throttle": 0.2}, locked, "handle pulled fully rearward"),
              (330.6, {"engine_running": True, "throttle": 0.2}, locked, "0.6 s later (persistence 0.5 s): green"),
              (360, {"engine_running": True, "throttle": 1.0}, locked, "take-off")]
    for t, kw, r, what in script:
        o = u.step(FlightInputs(t=float(t), **kw), r)
        rows.append({"t_s": t, "what": what, "phase": o.phase.value, "state": o.state.value,
                     "alert": o.level.name, "message": o.message, "voice": o.aural, "green": o.green_locked})
    out["partial_lock_before_takeoff"] = {"rows": rows, "events": u.events}
    u = CanopyAlertUnit()
    rows = []
    seq = [(0, {}, locked, "master ON, locked"), (5, {"engine_running": True, "throttle": 0.2}, locked, "taxi"),
           (100, {"engine_running": True, "throttle": 1.0, "ias_kt": 20}, locked, "take-off roll")]
    seq += [(101 + k, {"engine_running": True, "throttle": 1.0, "ias_kt": 60 + 5 * k}, locked, "climb")
            for k in range(6)]
    seq += [(900, {"engine_running": True, "throttle": 0.8, "ias_kt": 180}, locked, "cruise 180 KIAS"),
            (900.2, {"engine_running": True, "throttle": 0.8, "ias_kt": 180}, rear_out, "rear bolt backs out"),
            (900.4, {"engine_running": True, "throttle": 0.8, "ias_kt": 180}, rear_out, "persistence 0.2 s"),
            (900.8, {"engine_running": True, "throttle": 0.8, "ias_kt": 180}, rear_out, "persistence 0.6 s"),
            (903, {"engine_running": True, "throttle": 0.8, "ias_kt": 180, "ack": True}, rear_out,
             "pilot acknowledges, slows down, lands as soon as possible")]
    for t, kw, r, what in seq:
        o = u.step(FlightInputs(t=float(t), **kw), r)
        if what != "climb":
            rows.append({"t_s": t, "what": what, "phase": o.phase.value, "state": o.state.value,
                         "alert": o.level.name, "message": o.message, "voice": o.aural, "green": o.green_locked})
    out["inflight_unlock"] = {"rows": rows, "events": u.events}
    return out


_FAMILIES = (("Extra", r"\bextra\b"), ("Pitts", r"pitts"), ("Vans RV", r"\bvans?\b|\brv-?\d"), ("Europa", r"europa"),
             ("Zenith / Zenair CH", r"zenith|zenair|zodiac|\bch ?\d{3}"), ("Diamond DA", r"diamond|\bda ?[1-9]\d\b"),
             ("Schempp-Hirth", r"schempp|ventus|discus|nimbus|janus|duo discus"),   # before Cirrus (S-H Cirrus glider)
             ("Cirrus", r"cirrus|\bsr2\d"), ("Piper", r"piper|\bpa-?\d"), ("Cessna", r"cessna"),
             ("SportCruiser", r"sport ?cruiser|\bps-28"), ("Evektor", r"evektor|sportstar"),
             ("Dynamic WT9", r"wt9|dynamic"), ("Slingsby", r"slingsby"), ("Yak", r"\byak"), ("Sukhoi", r"sukhoi|\bsu-\d"),
             ("Cap / Mudry", r"\bcap ?\d|mudry"), ("Zlin", r"zlin"), ("Grob", r"grob"),
             ("Schleicher", r"schleicher|\bas[kwh] ?-?\d|\bask\b|\basw\b"), ("Grumman", r"grumman"), ("Schweizer", r"schweizer|sgs"),
             ("SZD", r"\bszd\b|bocian|foka|perkoz|junior"), ("Rutan-type canards", r"rutan|\bez\b|long-?ez|vari-?eze|berkut|defiant"),
             ("Lancair", r"lancair"), ("Robin", r"robin"), ("Glasair", r"glasair"))


def family(row: dict) -> str:
    """Canonical type family. The text searched is the "[family: X]" tag in the notes (R5) followed by the aircraft type,
    so agent tags such as "Grob G103" and "Grob G102" fall into one family "Grob"; an unmatched tag is kept as it is."""
    import re
    m = re.search(r"\[family:\s*([^\]]+)\]", row.get("notes", ""))
    tag = m.group(1).strip() if m else ""
    for text in (tag.lower(), row.get("aircraft_type", "").lower()):
        if not text:
            continue
        for name, pat in _FAMILIES:
            if re.search(pat, text):
                return name
    if tag:
        return tag
    return "Other glider" if row.get("category") == "glider" else "Other"


def load_occurrences() -> list[dict]:
    """R2 rows plus R5 additions, de-duplicated on (registration, date); each row keeps its own URL."""
    rows: list[dict] = []
    seen = set()
    for path in (OCC_CSV, OCC_CSV.with_name("R5_occurrences_add.csv")):
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                reg = r.get("registration", "").strip().upper()
                if not reg or reg.startswith("UNKNOWN") or reg == "N/A":      # unpublished registration: use the report
                    reg = "REPORT:" + r.get("report_id", "").strip().upper()  # (audit 2026-11-04 found two BFU events merged)
                key = (reg, r.get("date", "").strip())
                if key in seen:
                    continue
                seen.add(key)
                r["family"] = family(r)
                r["source_file"] = path.name
                rows.append(r)
    return rows


def occurrences() -> dict | None:
    rows = load_occurrences()
    if not rows:
        return None
    fam: dict[str, dict[str, int]] = {}
    for r in rows:
        d = fam.setdefault(r["family"], {"rows": 0, "lock": 0, "lock_climb": 0, "fatal": 0})
        d["rows"] += 1
        d["lock"] += r.get("cause_class") in LOCK
        d["lock_climb"] += r.get("cause_class") in LOCK and r.get("phase") == "initial_climb"
        d["fatal"] += r.get("outcome") == "fatal"
    phases = ("takeoff_roll", "initial_climb", "cruise", "aerobatics", "approach", "landing", "unknown")
    outcomes = ("no_injury", "minor", "serious", "fatal", "unknown")
    lock_rows = [r for r in rows if r.get("cause_class") in LOCK]
    phase_outcome = {ph: {oc: sum(r.get("phase") == ph and r.get("outcome") == oc for r in lock_rows) for oc in outcomes}
                     for ph in phases}
    return {"n": len(rows), "by_source": Counter(r["source_file"] for r in rows),
            "by_cause": Counter(r.get("cause_class", "unknown") for r in rows),
            "by_phase": Counter(r.get("phase", "unknown") for r in rows),
            "by_outcome": Counter(r.get("outcome", "unknown") for r in rows),
            "by_investigator": Counter(r.get("investigator", "unknown") for r in rows),
            "by_category": Counter(r.get("category", "unknown") for r in rows),
            "lock_related": len(lock_rows),
            "lock_related_fatal": sum(r.get("outcome") == "fatal" for r in lock_rows),
            "lock_related_by_phase": Counter(r.get("phase", "unknown") for r in lock_rows),
            "warning_fitted_yes": sum(r.get("warning_fitted") == "yes" for r in rows),
            "fatal": sum(r.get("outcome") == "fatal" for r in rows),
            "by_family": fam, "lock_phase_outcome": phase_outcome}


def occurrence_tables(oc: dict) -> tuple[str, str, list[str]]:
    """Two summary tables (datawiz tablo: sorted, right-aligned numbers) and the tablo.denetle findings."""
    from datawiz import tablo
    fam = oc["by_family"]
    top = sorted(fam, key=lambda k: -fam[k]["rows"])
    main = [k for k in top if fam[k]["rows"] >= 3 and k != "Other"]
    rest = [k for k in top if k not in main]
    names = main + ["All other types"]
    agg = [fam[k] for k in main] + [{c: sum(fam[k][c] for k in rest) for c in ("rows", "lock", "lock_climb", "fatal")}]
    t1 = {"Type family": names, "Occurrences": [a["rows"] for a in agg], "Lock-related": [a["lock"] for a in agg],
          "Lock-related in initial climb": [a["lock_climb"] for a in agg], "Fatal (any cause)": [a["fatal"] for a in agg]}
    po = oc["lock_phase_outcome"]
    ph = [p for p in po if sum(po[p].values())]
    t2 = {"Phase (lock-related only)": [p.replace("_", " ") for p in ph]}
    for o in ("no_injury", "minor", "serious", "fatal", "unknown"):
        t2[o.replace("_", " ")] = [po[p][o] for p in ph]
    findings = tablo.denetle(t1) + tablo.denetle(t2)
    return (tablo.markdown_tablo(t1, ondaliklar={k: 0 for k in t1 if k != "Type family"}),
            tablo.markdown_tablo(t2, ondaliklar={k: 0 for k in t2 if not k.startswith("Phase")}), findings)


def analyse(cfg: dict) -> tuple[dict, dict]:
    rates, tol, exp = cfg["_rates"], cfg["_tol"], cfg["_exp"]
    n, seed = cfg["n_samples"], cfg["seed"]
    progress(f"Monte Carlo: 5 architectures x 4 latch conditions x {n} flights")
    res = {a: {h: mc.simulate(mc.ARCHITECTURES[a], h, rates, tol, n=n, seed=seed + 17 * i + j)
               for j, h in enumerate((None,) + mc.HAZARDS)} for i, a in enumerate(mc.ARCHITECTURES)}
    arch = {}
    for a, rr in res.items():
        full = mc.takeoff_risk(rr, exp, "full")
        match = mc.takeoff_risk(rr, exp, "matching", floor=v(cfg["compliance_floor"]))
        arch[a] = {"label": mc.ARCHITECTURES[a].label, "channels": mc.ARCHITECTURES[a].seated
                   + len(mc.ARCHITECTURES[a].bolt_sensors),
                   "miss": {h: rr[h].p_locked for h in mc.HAZARDS},
                   "miss_ci": {h: rr[h].interval(mc.LOCKED) for h in mc.HAZARDS},
                   "miss_k": {h: rr[h].counts.get(mc.LOCKED, 0) for h in mc.HAZARDS},
                   "false_alarm": rr[None].p_alert, "false_alarm_ci": rr[None].interval(mc.CLOSED_UNLOCKED),
                   "fault_caution": rr[None].p_fault, "risk_full": full, "risk_matching": match,
                   "reduction_lower_bound_full": mc.takeoff_risk(upper_bound_results(rr), exp,
                                                                 "full")["reduction_factor"]}

    progress("trip-point window and cry-wolf sweep")
    trips = np.round(np.arange(64.0, 70.01, 0.05), 3)
    sweep = {}
    for s in (0.2, 0.3, 0.5):
        m_f = [trip_probabilities(float(t), s, tol.sigma_full_mm, tol.hazard_below_mm) for t in trips]
        sweep[s] = {"miss": [a for a, _ in m_f], "false": [b for _, b in m_f],
                    "window_1e3": trip_window(s, tol.sigma_full_mm, tol.hazard_below_mm, 1e-3, 1e-3)}
    fas = np.logspace(-6, -1, 41)
    exp0 = replace(exp, p_nuisance=0.0)          # x axis = ALL false + nuisance alerts per flight
    cry = {"fa": fas.tolist(),
           "full": [mc.takeoff_risk(with_false_alarm(res["A3"], f), exp0, "full")["reduction_factor"] for f in fas],
           "matching": [mc.takeoff_risk(with_false_alarm(res["A3"], f), exp0, "matching")["reduction_factor"]
                        for f in fas]}
    base_unalerted = sum(exp.p_hazard[h] * exp.p_pilot_miss[h] for h in mc.HAZARDS)

    progress("fault tree of A3 under a partial lock (independent vs Monte Carlo common cause)")
    q = rates.mode_probabilities()
    tol_miss, _ = trip_probabilities(tol.trip_mm, tol.sigma_trip_mm, tol.sigma_full_mm, tol.hazard_below_mm)
    tree = ("AND", "partial_lock", "pilot_check_misses",
            ("OR", "alert_ignored", "misrig_common",
             ("AND", *[("OR", f"tol_{b}", f"stuck_{b}") for b in ("front", "centre", "rear")])))
    ignored = 1.0 - arch["A3"]["risk_matching"]["compliance"]
    probs = {"partial_lock": exp.p_hazard["partial"], "pilot_check_misses": exp.p_pilot_miss["partial"],
             "alert_ignored": ignored, "misrig_common": tol.p_misrig_common,
             **{f"tol_{b}": tol_miss for b in ("front", "centre", "rear")},
             **{f"stuck_{b}": q["stuck_active"] for b in ("front", "centre", "rear")}}
    no_misrig = mc.simulate(mc.ARCHITECTURES["A3"], "partial", rates, replace(tol, p_misrig_common=0.0), n=n,
                            seed=seed + 4242)
    ft = {"tree": fta.tree_text(tree), "probs": probs, "top_exact": fta.evaluate(tree, probs),
          "top_rare_event": fta.cut_set_probability(tree, probs),
          "cut_sets": [sorted(s) for s in fta.minimal_cut_sets(tree)],
          "importance": fta.importance(tree, probs),
          "alert_ignored_from": "1 - compliance of A3 under probability matching (PPV), from the Monte Carlo",
          "sensor_part_independent": (tol_miss + q["stuck_active"]) ** 3,
          "sensor_part_mc_no_misrig": no_misrig.p_locked, "sensor_part_mc_no_misrig_ci": no_misrig.interval(mc.LOCKED),
          "sensor_part_mc": arch["A3"]["miss"]["partial"], "tol_miss_single": tol_miss}

    progress("sensitivity: A3 with other per-channel failure-rate sets")
    sens = {}
    for name, rs in cfg.get("rate_sets", {}).items():
        if name.startswith("_"):
            continue
        rates_s = mc.ChannelRates(v(rs["stuck_active_per_h"]), v(rs["stuck_inactive_per_h"]), v(rs["open_per_h"]),
                                  v(rs["short_per_h"]), rates.flight_h, rates.latent_interval_h)
        rr = {h: mc.simulate(mc.ARCHITECTURES["A3"], h, rates_s, tol, n=n, seed=seed + 999 + j)
              for j, h in enumerate((None,) + mc.HAZARDS)}
        sens[name] = {"miss": {h: rr[h].p_locked for h in mc.HAZARDS}, "false_alarm": rr[None].p_alert,
                      "fault_caution": rr[None].p_fault,
                      "rf_full": mc.takeoff_risk(rr, exp, "full")["reduction_factor"],
                      "rf_full_lb": mc.takeoff_risk(upper_bound_results(rr), exp, "full")["reduction_factor"],
                      "rf_matching": mc.takeoff_risk(rr, exp, "matching")["reduction_factor"],
                      "source": rs["stuck_active_per_h"]["source"]}
    grid = {"p_partial": [1e-4, 1e-3, 1e-2, 5e-2], "p_nuisance": [1e-5, 1e-4, 1e-3], "rf_matching": []}
    for pp in grid["p_partial"]:
        row = []
        for pn in grid["p_nuisance"]:
            e2 = mc.Exposure({**exp.p_hazard, "partial": pp}, exp.p_pilot_miss, pn)
            row.append(mc.takeoff_risk(res["A3"], e2, "matching")["reduction_factor"])
        grid["rf_matching"].append(row)
    progress("options at depth: LOCK-SENSE Plus and powered over-centre lock")
    opt_cfg = cfg.get("options", {})
    k_mis = v(opt_cfg["plus_misrig_factor"]) if "plus_misrig_factor" in opt_cfg else 0.1
    k_part = v(opt_cfg["powerlock_partial_factor"]) if "powerlock_partial_factor" in opt_cfg else 0.1
    tol_plus = replace(tol, p_misrig_common=tol.p_misrig_common * k_mis)
    rr_plus = {h: mc.simulate(mc.ARCHITECTURES["A4"], h, rates, tol_plus, n=n, seed=seed + 7000 + j)
               for j, h in enumerate((None,) + mc.HAZARDS)}
    exp_pl = mc.Exposure({**exp.p_hazard, "partial": exp.p_hazard["partial"] * k_part}, exp.p_pilot_miss, exp.p_nuisance)
    base_a0 = sum(exp.p_hazard[h] * exp.p_pilot_miss[h] for h in mc.HAZARDS)
    options = {}
    for key, label, rr, ex in (("A3", "LOCK-SENSE (A3, baseline)", res["A3"], exp),
                               ("PLUS", "LOCK-SENSE Plus: dual channel per bolt, one analog self-calibrating", rr_plus, exp),
                               ("POWER", "Powered over-centre lock + A3 sensing", res["A3"], exp_pl)):
        full = mc.takeoff_risk(rr, ex, "full")
        match = mc.takeoff_risk(rr, ex, "matching")
        options[key] = {"label": label, "risk_full": full["risk"], "risk_matching": match["risk"],
                        "rf_full_vs_A0": base_a0 / full["risk"] if full["risk"] > 0 else float("inf"),
                        "rf_matching_vs_A0": base_a0 / match["risk"] if match["risk"] > 0 else float("inf"),
                        "miss_partial": rr["partial"].p_locked, "false_alarm": rr[None].p_alert}
    options["_factors"] = {"plus_misrig_factor": k_mis, "powerlock_partial_factor": k_part}

    progress("complacency sensitivity: the pilot's own check degrades once the system is fitted")
    comp_cfg = cfg.get("complacency", {})
    pm_c = {h: v(comp_cfg["p_pilot_miss_with_system"][h]) for h in mc.HAZARDS} if comp_cfg else \
        {"partial": 0.9, "one_bolt": 0.99, "unseated": 0.2}
    complacency = {}
    for compl in ("full", "matching"):
        base = mc.takeoff_risk(res["A3"], exp, compl)
        e_c = mc.Exposure(exp.p_hazard, pm_c, exp.p_nuisance)
        rc = mc.takeoff_risk(res["A3"], e_c, compl)
        complacency[compl] = {"risk_no_complacency": base["risk"], "risk_complacent": rc["risk"],
                              "rf_vs_A0": base_a0 / rc["risk"] if rc["risk"] > 0 else float("inf")}
    complacency["p_pilot_miss_with_system"] = pm_c
    targets = {k: x for k, x in cfg.get("targets", {}).items() if not k.startswith("_")}
    residual = {a: {"risk_per_fh_full": r["risk_full"]["risk"] / rates.flight_h,
                    "risk_per_fh_matching": r["risk_matching"]["risk"] / rates.flight_h} for a, r in arch.items()}

    ercs = {}
    for key, sc in barriers.SCENARIOS.items():
        w0, w1 = barriers.with_and_without(sc)
        ercs[key] = {"text": sc["text"], "severity_reason": sc["severity_reason"], "states": sc["barriers"],
                     "without": {"code": w0.code, "colour": w0.colour, "sum": w0.barrier_sum, "value": w0.value},
                     "with": {"code": w1.code, "colour": w1.colour, "sum": w1.barrier_sum, "value": w1.value}}
    out = {"aircraft": cfg["aircraft"]["value"], "latch": EXTRA_NG.__dict__, "inputs": {
        k: cfg[k] for k in ("rates", "tolerance", "exposure", "compliance_floor")},
           "mode_probabilities": q, "architectures": arch, "trip_windows": {str(s): sweep[s]["window_1e3"]
                                                                              for s in sweep},
           "unalerted_hazard_per_flight_no_system": base_unalerted, "fault_tree": ft, "ercs": ercs,
           "sensitivity_rates": sens, "targets_per_fh": targets, "residual": residual, "exposure_grid": grid,
           "options": options, "complacency": complacency,
           "fmea_markdown": fmea.markdown_table(probs=q), "traces": logic_traces(), "occurrences": occurrences(),
           "fault_demo": faults.run_all()}
    return out, {"trips": trips, "sweep": sweep, "cry": cry}


def num(x: float) -> str:
    return "inf" if x == float("inf") else sig(x)


def upper_bound_results(rr: dict) -> dict:
    """Results with every missed-alert count raised to its 95 % Wilson upper bound (for a conservative factor)."""
    out = dict(rr)
    for h in mc.HAZARDS:
        r = rr[h]
        k = int(np.ceil(r.interval(mc.LOCKED)[1] * r.n))
        rest = {s: c for s, c in r.counts.items() if s != mc.LOCKED}
        scale = (r.n - k) / max(1, sum(rest.values()))
        out[h] = mc.ConditionalResult(r.architecture, h, r.n, {mc.LOCKED: k, **{s: int(c * scale) for s, c in
                                                                                   rest.items()}})
    return out


def _ann(v: dict) -> str:
    """One-cell text of what the pilot sees."""
    if v["phase"] == "off":
        return "dark (unit off)"
    parts = ["green LOCKED"] if v["green"] else []
    if v["level"] != "NONE":
        col = {"ADVISORY": "white", "CAUTION": "amber", "WARNING": "red"}[v["level"]]
        parts.append(f"{col} {v['message']}" + (" + voice" if v["voice"] else ""))
    return ", ".join(parts) or "dark"


_LAMP = {"green": ("#1f9d55", "#fff"), "white": ("#e9e9e4", "#1d1d1b"), "amber": ("#e0a000", "#1d1d1b"),
         "red": ("#d23b2e", "#fff"), "dark": ("#2c2d30", "#c9c9c4")}


def _chips(v: dict) -> str:
    import html
    if v["phase"] == "off":
        return '<span class="chip" style="background:#2c2d30;color:#c9c9c4">dark: unit off</span>'
    out = []
    if v["green"]:
        out.append('<span class="chip" style="background:#1f9d55;color:#fff">CANOPY LOCKED</span>')
    if v["level"] != "NONE":
        col = {"ADVISORY": "white", "CAUTION": "amber", "WARNING": "red"}[v["level"]]
        bg, fg = _LAMP[col]
        out.append(f'<span class="chip" style="background:{bg};color:{fg}">{html.escape(v["message"])}</span>'
                   + (' <span class="voice">+ voice</span>' if v["voice"] else ""))
    return " ".join(out) or '<span class="chip" style="background:#2c2d30;color:#c9c9c4">dark</span>'


def fault_demo_html(rows: list[dict]) -> str:
    """Static one-view page: what the pilot sees for each injected fault (generated from the real logic)."""
    import html
    body = []
    for r in rows:
        miss = r["verdict"] == "MISSED"
        body.append(f'<tr{" class=miss" if miss else ""}><td>{html.escape(r["title"])}</td>'
                    f'<td>{"locked" if r["locked"] else "<b>not locked</b>"}</td><td>{_chips(r["taxi"])}</td>'
                    f'<td>{_chips(r["takeoff"])}</td><td>{html.escape(r["verdict"])}</td>'
                    f'<td>{html.escape(r["found_by"])}</td></tr>')
    n_miss = sum(r["verdict"] == "MISSED" for r in rows)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Canopy Fault Injection</title>
<style>
  :root {{ --bg: #f6f5f1; --ink: #1d1d1b; --muted: #5a5a55; --line: #d6d4cc; --miss: #fbe3df;
          --s1: 8px; --s2: 16px; --s3: 32px; --r1: 4px; --f1: 13px; --f2: 15px; --f3: 20px; --f4: 26px; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #121314; --ink: #ecebe6; --muted: #a9a8a2; --line: #34353a; --miss: #3a1f1c; }} }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font: var(--f2)/1.45 system-ui, "Segoe UI", sans-serif; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: var(--s3) var(--s2); }}
  h1 {{ font-size: var(--f4); line-height: 1.2; margin: 0 0 var(--s1); }}
  .lede {{ color: var(--muted); margin: 0 0 var(--s3); max-width: 70ch; }}
  .wrap {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: var(--f1); }}
  th, td {{ text-align: left; vertical-align: top; padding: var(--s1); border-bottom: 1px solid var(--line); }}
  th {{ font-size: var(--f1); color: var(--muted); font-weight: 600; }}
  tr.miss td {{ background: var(--miss); }}
  .chip {{ display: inline-block; border-radius: var(--r1); padding: 2px 6px; margin: 1px 0;
          font: 700 var(--f1)/1.3 ui-monospace, Consolas, monospace; }}
  .voice {{ color: var(--muted); }}
  .note {{ margin-top: var(--s3); font-size: var(--f1); color: var(--muted); }}
</style></head>
<body><main>
<h1>What the pilot sees when a sensor fails</h1>
<p class="lede">{len(rows)} cases run through the real alert logic (power-up, taxi, take-off power). Green appears on a
canopy that is not locked in {n_miss} cases (shaded). Both need two failures at once, and the pilot's own handle check and
the maintenance gauge test remain.</p>
<div class="wrap"><table>
<thead><tr><th>Case</th><th>Canopy really</th><th>Taxi</th><th>Take-off power</th><th>Verdict</th><th>Found by</th></tr></thead>
<tbody>
{chr(10).join(body)}
</tbody></table></div>
<p class="note">Generated by <code>scripts/canopy_day.py</code> from <code>aerokit.canopy.faults</code>. Bolt positions:
70 mm handle-equivalent = full lock, 62 mm = partial lock, trip point 68 mm.</p>
</main></body></html>
"""


def _fmt_ci(ci) -> str:
    return f"{sig(ci[0])}–{sig(ci[1])}" if ci[1] > 0 else "0"


def markdown(o: dict) -> str:
    L = ["# Canopy alert retrofit — Extra NG — study output", "",
         "Generated by `python scripts/canopy_day.py studies/final_2026/easa/inputs.json`. Every value below is "
         "**[K]** (computed here) from the inputs listed at the end, whose tags ([D]/[D-ag]/[Y]) are in "
         "`inputs.json`.", "",
         "## 1. Architectures — Monte Carlo per flight", "",
         f"{o['inputs']['rates']['flight_h']['value']} h flights; latent stuck-active failures found every "
         f"{o['inputs']['rates']['latent_interval_h']['value']} h. Miss = the unit shows LOCKED although the "
         "latch is not. 95 % Wilson intervals.", "",
         "| Arch. | Sensors | Channels | P(miss \\| partial lock) | P(miss \\| one bolt out) | P(miss \\| unseated) "
         "| P(false alarm) per flight | P(SENS caution) per flight | Risk reduction: full (95 % lower bound) / matching |",
         "|---|---|---|---|---|---|---|---|---|"]
    for a, r in o["architectures"].items():
        m, ci = r["miss"], r["miss_ci"]
        L.append(f"| {a} | {r['label']} | {r['channels']} | {sig(m['partial'])} ({_fmt_ci(ci['partial'])}) | "
                 f"{sig(m['one_bolt'])} ({_fmt_ci(ci['one_bolt'])}) | {sig(m['unseated'])} | "
                 f"{sig(r['false_alarm'])} | {sig(r['fault_caution'])} | "
                 f"{num(r['risk_full']['reduction_factor'])} (≥ {num(r['reduction_lower_bound_full'])}) / "
                 f"{num(r['risk_matching']['reduction_factor'])} |")
    L += ["", f"Without a system the pilot leaves {sig(o['unalerted_hazard_per_flight_no_system'])} hazardous "
          "latch conditions per flight undetected (= Σ p_hazard × p_pilot_miss, all [Y]).", "",
          "### Residual risk per flight hour vs AC 23.1309-1E Class I ceilings", "",
          "Ceilings [D-ag, R4]: " + ", ".join(f"{k} < {x:g}" for k, x in o["targets_per_fh"].items())
          + ". Which class applies to 'take-off with the canopy not locked' is our judgement [Y] (hazardous to "
          "catastrophic for this type; AD 2025-0156 cites possible loss of control).", "",
          "| Arch. | Residual risk / FH (full compliance) | (probability matching) |", "|---|---|---|"]
    L += [f"| {a} | {sig(r['risk_per_fh_full']) if r['risk_per_fh_full'] > 0 else '0 (no miss sampled)'} | "
          f"{sig(r['risk_per_fh_matching'])} |" for a, r in o["residual"].items()]
    L += ["", "### Sensitivity of A3 to the per-channel failure rates", "",
          "| Rate set | P(miss \\| partial) | P(miss \\| one bolt) | P(false alarm) | P(SENS) | Reduction full (≥ 95 % LB) "
          "/ matching | Source |", "|---|---|---|---|---|---|---|"]
    L += [f"| {k} | {sig(s['miss']['partial'])} | {sig(s['miss']['one_bolt'])} | {sig(s['false_alarm'])} | "
          f"{sig(s['fault_caution'])} | {num(s['rf_full'])} (≥ {num(s['rf_full_lb'])}) / {num(s['rf_matching'])} | "
          f"{s['source']} |" for k, s in o["sensitivity_rates"].items()]
    g = o["exposure_grid"]
    L += ["", "### A3 benefit under probability matching vs the two assumed rates (risk reduction factor)", "",
          "| p(partial lock) per flight \\ p(nuisance) per flight | " + " | ".join(f"{x:g}" for x in g["p_nuisance"]) + " |",
          "|---|" + "---|" * len(g["p_nuisance"])]
    L += [f"| {pp:g} | " + " | ".join(num(x) for x in row) + " |" for pp, row in zip(g["p_partial"], g["rf_matching"])]
    L += ["", "Reading: the benefit depends on the ratio of nuisance alerts to real unalerted hazards, not on either alone; "
          "with full compliance the nuisance rate drops out of the formula (it only enters the PPV), see §1.", ""]
    op = o["options"]
    L += ["", "### Options at depth (same model, same inputs; factors are [Y], set in inputs.json `options`)", "",
          f"Factors: LOCK-SENSE Plus cuts the common mis-rig probability by x{op['_factors']['plus_misrig_factor']:g} "
          f"(the analog channel self-calibrates and disagrees with a mis-rigged switch); the powered lock cuts the "
          f"partial-lock rate by x{op['_factors']['powerlock_partial_factor']:g} (the actuator always drives to full lock; "
          "residual = actuator stops short, still seen by A3).", "",
          "| Option | Risk / flight (full) | Risk / flight (matching) | Reduction vs no system (full / matching) | "
          "P(miss \\| partial) | P(false alarm) |", "|---|---|---|---|---|---|"]
    L += [f"| {x['label']} | {sig(x['risk_full'])} | {sig(x['risk_matching'])} | {num(x['rf_full_vs_A0'])} / "
          f"{num(x['rf_matching_vs_A0'])} | {sig(x['miss_partial'])} | {sig(x['false_alarm'])} |"
          for k, x in op.items() if not k.startswith("_")]
    cp = o["complacency"]
    L += ["", "### Complacency sensitivity (A3; the pilot's own check degrades once the system is fitted)", "",
          "With the system fitted the pilot-check miss probabilities become " + ", ".join(
              f"{h} {x:g}" for h, x in cp["p_pilot_miss_with_system"].items()) + " [Y]; the no-system baseline keeps the "
          "original values.", "",
          "| Pilot response to alerts | Risk / flight, no complacency | Risk / flight, complacent | Reduction vs no system |",
          "|---|---|---|---|"]
    L += [f"| {k} | {sig(cp[k]['risk_no_complacency'])} | {sig(cp[k]['risk_complacent'])} | {num(cp[k]['rf_vs_A0'])} |"
          for k in ("full", "matching")]
    L += ["", "## 2. Trip-point window (both P(miss | partial) and P(false | full) ≤ 1e-3)", ""]
    for s, w in o["trip_windows"].items():
        L.append(f"- rigging s.d. {s} mm: " + (f"{w[0]}–{w[1]} mm handle-equivalent" if w else "**no window**"))
    ft = o["fault_tree"]
    L += ["", "## 3. Fault tree of A3, take-off with a partial lock and no effective alert", "", "```",
          ft["tree"].rstrip(), "```", "",
          f"- exact top (independent events): {sig(ft['top_exact'])} per flight; rare-event sum "
          f"{sig(ft['top_rare_event'])}",
          f"- sensor part (all three bolt sensors read LOCKED), independence assumed: (tol + stuck)^3 = "
          f"{sig(ft['sensor_part_independent'])}; Monte Carlo with the shared linkage tube, no mis-rigging: "
          f"{sig(ft['sensor_part_mc_no_misrig'])} (95 % CI {_fmt_ci(ft['sensor_part_mc_no_misrig_ci'])}) -> the "
          "shared bolt position is a common cause; independence is "
          + ("optimistic" if ft["sensor_part_mc_no_misrig"] > ft["sensor_part_independent"] else "not optimistic here")
          + f". With the systematic mis-rigging term the Monte Carlo gives {sig(ft['sensor_part_mc'])}.",
          f"- alert_ignored = {sig(ft['probs']['alert_ignored'])}: {ft['alert_ignored_from']}.",
          "- minimal cut sets: " + "; ".join("{" + ", ".join(s) + "}" for s in ft["cut_sets"]), "",
          "| Basic event | P | Fussell-Vesely | Birnbaum | RAW |", "|---|---|---|---|---|"]
    for e, im in ft["importance"].items():
        L.append(f"| {e} | {sig(ft['probs'][e])} | {sig(im['fussell_vesely'])} | {sig(im['birnbaum'])} | "
                 f"{sig(im['raw'])} |")
    L += ["", "## 4. ERCS (barrier model; states are [Y])", ""]
    for k, e in o["ercs"].items():
        L.append(f"- **{k}** — {e['text']}: without alert {e['without']['code']} ({e['without']['colour']}, "
                 f"barrier sum {e['without']['sum']}) → with alert {e['with']['code']} ({e['with']['colour']}, "
                 f"sum {e['with']['sum']}); numerical equivalent {e['without']['value']:g} → {e['with']['value']:g}.")
    L += ["", "## 5. FMEA (recommended installation A3)", "", o["fmea_markdown"],
          "## 6. Logic traces (scripted inputs through `CanopyAlertUnit`)", ""]
    for name, tr in o["traces"].items():
        L += [f"### {name}", "", "| t (s) | What happens | Phase | Canopy state | Alert | Message | Voice | Green |",
              "|---|---|---|---|---|---|---|---|"]
        L += [f"| {r['t_s']} | {r['what']} | {r['phase']} | {r['state']} | {r['alert']} | {r['message']} | "
              f"{'yes' if r['voice'] else '—'} | {'ON' if r['green'] else 'off'} |" for r in tr["rows"]]
        L += ["", "Event log: " + "; ".join(f"{t:g} s {e}" for t, e in tr["events"]), ""]
    L += ["## 6b. Fault-injection demo (real logic, `aerokit.canopy.faults`; HTML view `out/fault_demo.html`)", "",
          "| Case | Canopy really | Taxi | Take-off power | Verdict | Found by |", "|---|---|---|---|---|---|"]
    for r in o["fault_demo"]:
        L.append(f"| {r['title']} | {'locked' if r['locked'] else 'NOT locked'} | {_ann(r['taxi'])} | {_ann(r['takeoff'])} | "
                 f"**{r['verdict']}** | {r['found_by']} |")
    L.append("")
    oc = o["occurrences"]
    if oc:
        t1, t2, fnd = occurrence_tables(oc)
        L += ["## 7. Occurrence dataset (R2 + R5, subagent-built; every row has its own URL)", "",
              f"{oc['n']} rows after de-duplication on registration + date ("
              + ", ".join(f"{k} {c}" for k, c in oc["by_source"].items()) + "); lock-related (not locked + partially "
              f"latched) {oc['lock_related']}, of which {oc['lock_related_fatal']} fatal; by phase: "
              + ", ".join(f"{k} {c}" for k, c in oc["lock_related_by_phase"].most_common()) + ". "
              f"Rows with a warning fitted: {oc['warning_fitted_yes']}. **A sample of investigated events, not a rate.**", "",
              "### By type family (families with ≥ 3 rows; the rest pooled)", "", t1, "",
              "### Lock-related occurrences: phase × outcome", "", t2, "",
              "Table check (`datawiz.tablo.denetle`): " + ("; ".join(fnd) if fnd else "no findings") + ".", "",
              "All rows. By cause: " + ", ".join(f"{k} {c}" for k, c in oc["by_cause"].most_common()) + ".",
              "By investigator: " + ", ".join(f"{k} {c}" for k, c in oc["by_investigator"].most_common()) + ".", ""]
    L += ["## Inputs", "", "| Input | Value | Source | Tag |", "|---|---|---|---|"]
    for grp in ("rates", "tolerance"):
        for k, n in o["inputs"][grp].items():
            L.append(f"| {grp}.{k} | {n['value']} | {n['source']} | {n['tag']} |")
    for grp in ("p_hazard", "p_pilot_miss"):
        for k, n in o["inputs"]["exposure"][grp].items():
            L.append(f"| {grp}.{k} | {n['value']} | {n['source']} | {n['tag']} |")
    n = o["inputs"]["exposure"]["p_nuisance"]
    L.append(f"| p_nuisance | {n['value']} | {n['source']} | {n['tag']} |")
    return "\n".join(L) + "\n"


def figures(o: dict, c: dict, folder: Path) -> None:
    import datawiz as dw
    S = dw.Seti(str(folder / "canopy.seti.json"), hedef="sunum-tam")
    S.nicelik("pmiss", "Missed-alert probability", None, eksen="x", olcek="log")
    S.nicelik("arch", "Sensor architecture", None, eksen="y")
    S.nicelik("trip", "Lock-sensor trip point (handle gap)", "mm", eksen="x")
    S.nicelik("perr", "Probability per check", None, eksen="y", olcek="log")
    S.nicelik("pfa", "False-alarm probability per flight", None, eksen="x", olcek="log")
    S.nicelik("rrf", "Risk reduction factor", None, eksen="y", olcek="log")
    S.nicelik("barrier", "ERCS barrier", None, eksen="y")
    S.nicelik("weight", "Barrier weight", None, eksen="x")
    S.nicelik("count", "Investigated lock-related openings", None, eksen="x")
    S.nicelik("phase", "Flight phase", None, eksen="y")
    S.nicelik("family", "Type family", None, eksen="y")
    S.varlik("Held", renk="#009e73")           # green = held, vermilion = failed (reader's convention)
    S.varlik("Failed", renk="#d55e00")
    S.varlik("Added by the retrofit", renk="#0072b2")
    for name, col in (("Partial lock", "#000000"), ("One bolt out", "#7f3360"), ("Full lock", "#7f5708"),
                      ("Pilot always acts", "#07648e"), ("Pilot matches reliability", "#5f5f5f")):
        S.varlik(name, renk=col)
    _draw(S, o, c, folder)        # separate slides: no shared fixed margins (C1 has long category labels)


_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def pow10(ax, axis: str) -> None:
    """Log-axis ticks as 10⁻³ (superscript minus: no hyphen in tick labels) and 1 / 10 for 10⁰ / 10¹."""
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

    def f(val, _):
        if val <= 0:
            return ""
        e = int(round(np.log10(val)))
        if not np.isclose(val, 10.0 ** e):
            return ""
        return {0: "1", 1: "10"}.get(e, "10" + str(e).translate(_SUP))
    a = getattr(ax, f"{axis}axis")
    a.set_major_locator(LogLocator(base=10, numticks=12))
    a.set_major_formatter(FuncFormatter(f))
    a.set_minor_formatter(NullFormatter())


def _draw(S, o: dict, c: dict, folder: Path) -> None:
    import datawiz as dw
    # C1 — missed alerts by architecture
    keys = list(o["architectures"])
    fig, ax = S.figur(oran=0.55)
    yy = np.arange(len(keys))[::-1]
    floor = 1e-6
    for h, lab, off in (("partial", "Partial lock", 0.12), ("one_bolt", "One bolt out", -0.12)):
        vals, lo, hi = [], [], []
        for a in keys:
            r = o["architectures"][a]
            p, (l_, u_) = r["miss"][h], r["miss_ci"][h]
            vals.append(max(p, u_ if r["miss_k"][h] == 0 else p, floor))
            lo.append(max(l_, floor))
            hi.append(max(u_, floor))
        vals = np.array(vals)
        ax.errorbar(vals, yy + off, xerr=[np.maximum(vals - np.array(lo), 0), np.maximum(np.array(hi) - vals, 0)],
                    **S.stil(lab, tur="hata"))
    ax.set_yticks(yy, [f"{a}  {o['architectures'][a]['label']}" for a in keys])
    ax.set_xlim(floor, 2.0)
    S.eksen(ax, x="pmiss", y="arch")
    pow10(ax, "x")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(folder / "C1_missed_alert_by_architecture"), sessiz=True)

    # C2 — trip-point window
    fig, ax = S.figur(oran=0.55)
    s0 = 0.3
    sw = c["sweep"][s0]
    t = c["trips"]
    lm, = ax.plot(t, np.maximum(sw["miss"], 1e-9), **S.stil("Partial lock"))
    lf, = ax.plot(t, np.maximum(sw["false"], 1e-9), **S.stil("Full lock"))
    ax.set_ylim(1e-6, 1.5)
    w = sw["window_1e3"]
    if w:
        dw.notlar.bolge(ax, w[0], w[1])
        win_xy = ((w[0] + w[1]) / 2, 3e-5)
    ax.set_xlim(64.0, 70.0)
    S.eksen(ax, x="trip", y="perr")
    pow10(ax, "y")
    ax.set_ylim(1e-6, 1.5)
    dw.etiket.cizgi_sonu(ax, [lf], metinler=["false alarm"])
    ax.annotate("missed", (64.2, sw["miss"][4]), xytext=(0, -8), textcoords="offset points", va="top",
                color=S.renk("Partial lock"))
    dw.notlar.referans(ax, y=1e-3, metin="1 in 1000", konum="sol")
    if w:
        ax.text(64.3, 3e-5, f"shaded: trip window {w[0]:.1f}–{w[1]:.1f} mm\n(both errors below 1 in 1000)",
                ha="left", va="center", color=S.renk("Partial lock"))     # empty lower-left corner
    S.kaydet(fig, str(folder / "C2_trip_point_window"), sessiz=True)

    # C3 — cry wolf
    fig, ax = S.figur(oran=0.55)
    cr = c["cry"]
    l1, = ax.plot(cr["fa"], cr["full"], **S.stil("Pilot always acts"))
    l2, = ax.plot(cr["fa"], cr["matching"], **S.stil("Pilot matches reliability"))
    base = o["unalerted_hazard_per_flight_no_system"]
    ax.axvline(base, color="#5f5f5f", linestyle=(0, (2, 2)), linewidth=1.2, zorder=1)
    ht = ax.annotate("unalerted\nhazard rate", (base, 25.0), xytext=(6, 0), textcoords="offset points",
                     ha="left", va="center", color="#5f5f5f")
    dw.notlar._hale(ht, ax)
    nz = o["inputs"]["exposure"]["p_nuisance"]["value"]
    i_nz = int(np.argmin(np.abs(np.log10(cr["fa"]) - np.log10(nz))))
    dw.notlar.ok(ax, (cr["fa"][i_nz], cr["matching"][i_nz]), f"our nuisance estimate: {cr['matching'][i_nz]:.0f}x")
    S.eksen(ax, x="pfa", y="rrf")
    pow10(ax, "x")
    pow10(ax, "y")
    dw.etiket.cizgi_sonu(ax, [l1, l2], metinler=["always acts", "matches reliability"])
    S.kaydet(fig, str(folder / "C3_cry_wolf"), sessiz=True)

    # C4 — ERCS barriers with / without the retrofit
    from aerokit.investigation import ERCS_BARRIERS
    e = o["ercs"]["takeoff_partial_lock"]
    names = [b for b in ERCS_BARRIERS if b in e["states"] or b == "warning systems"]
    fig, ax = S.figur(oran=0.55)
    yy = np.arange(len(names))[::-1]
    groups = {"Held": [], "Failed": [], "Added by the retrofit": []}
    for i, b in enumerate(names):
        st = e["states"].get(b)
        key = "Added by the retrofit" if b == "warning systems" else "Held" if st in ("stopped", "remaining") \
            else "Failed"
        groups[key].append(i)
    for lab, sel in groups.items():
        if sel:
            w_ = [ERCS_BARRIERS[names[i]] for i in sel]
            ax.hlines(yy[sel], 0, w_, color=S.renk(lab), linewidth=3)
            ax.plot(w_, yy[sel], **S.stil(lab, tur="hata"))
    for i, b in enumerate(names):
        txt = "added by the retrofit" if b == "warning systems" else e["states"][b]
        ax.annotate(txt, (ERCS_BARRIERS[b], yy[i]), xytext=(4, 0), textcoords="offset points", va="center")
    ax.set_yticks(yy, names)
    ax.set_xlim(0, 7.5)
    S.eksen(ax, x="weight", y="barrier")
    S.kaydet(fig, str(folder / "C4_ercs_barriers"), sessiz=True)

    # C5 — investigated lock-related openings by flight phase (R2 dataset; a sample, not a rate)
    oc = o.get("occurrences")
    if not oc:
        return
    ph = oc["lock_related_by_phase"]
    order = sorted(ph, key=ph.get)
    fig, ax = S.figur(oran=0.55)
    yy = np.arange(len(order))
    cnt = [ph[k] for k in order]
    ax.hlines(yy, 0, cnt, color=S.renk("Partial lock"), linewidth=3)
    ax.plot(cnt, yy, **S.stil("Partial lock", tur="hata"))
    for i, k in enumerate(order):
        ax.annotate(str(ph[k]), (ph[k], yy[i]), xytext=(5, 0), textcoords="offset points", va="center")
    ax.set_yticks(yy, [k.replace("_", " ") for k in order])
    ax.set_xlim(0, max(cnt) * 1.2)
    S.eksen(ax, x="count", y="phase")
    S.kaydet(fig, str(folder / "C5_lock_related_by_phase"), sessiz=True)

    # C6 — lock-related openings by type family (same x quantity as C5)
    fam = oc["by_family"]
    shown = sorted([k for k in fam if fam[k]["lock"] >= 3 and k not in ("Other", "Other glider")],
                   key=lambda k: fam[k]["lock"])
    pooled = sum(fam[k]["lock"] for k in fam if k not in shown)
    names = (["all other types"] if pooled else []) + shown
    cnt = ([pooled] if pooled else []) + [fam[k]["lock"] for k in shown]
    fig, ax = S.figur(oran=0.9)
    yy = np.arange(len(names))
    ax.hlines(yy, 0, cnt, color=S.renk("Partial lock"), linewidth=3)
    ax.plot(cnt, yy, **S.stil("Partial lock", tur="hata"))
    for i, c in enumerate(cnt):
        ax.annotate(str(c), (c, yy[i]), xytext=(5, 0), textcoords="offset points", va="center")
    ax.set_yticks(yy, names)
    ax.set_xlim(0, max(cnt) * 1.2)
    S.eksen(ax, x="count", y="family")
    S.kaydet(fig, str(folder / "C6_lock_related_by_type"), sessiz=True)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if wants_help(argv):
        print(console_text(__doc__))
        return 0 if argv else 2
    protect_streams()
    path = Path(argv[0])
    cfg = load(path)
    out, curves = analyse(cfg)
    folder = path.parent / "out"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    (folder / "report.md").write_text(markdown(out), encoding="utf-8")
    (folder / "fault_demo.html").write_text(fault_demo_html(out["fault_demo"]), encoding="utf-8")
    if "--no-figures" not in argv:
        progress("drawing and auditing the slide figures")
        figures(out, curves, folder)
    errors, audit = audit_summary(folder)
    a3 = out["architectures"]["A3"]
    print(console_text(f"A3 (seated + 3 bolts): P(miss | partial) = {sig(a3['miss']['partial'])}, "
                       f"P(false alarm) = {sig(a3['false_alarm'])}/flight, risk reduction "
                       f"{num(a3['risk_full']['reduction_factor'])}x (full, >= {num(a3['reduction_lower_bound_full'])}x) / "
                       f"{num(a3['risk_matching']['reduction_factor'])}x (matching)"))
    print(console_text(audit))
    print(console_text(f"Wrote {folder / 'report.md'}"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
