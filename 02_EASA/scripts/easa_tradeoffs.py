"""EASA feedback-element trade-off: which combination of sensing, light, sound, vibration, take-off gate or engine
shut-down lowers the risk most, and what each one costs.

    python 02_EASA/scripts/easa_tradeoffs.py                # ~1 min (sensing Monte Carlo + 4 000 uncertainty draws)
    python 02_EASA/scripts/easa_tradeoffs.py --no-figures   # tables only

Scope (user, 5 Nov 2026): alert system only. The latch itself is not changed, so no powered lock or latch fix.

Reads ``02_EASA/inputs/inputs.json`` (sensing: hazard rates, pilot-check misses, channel rates, nuisance) and
``02_EASA/inputs/cues.json`` (cue detection, barriers, outcomes, passive marks, MCDA weights; source + tag per value).
Model: ``aerokit.canopy.montecarlo`` (sensing) + ``aerokit.canopy.cues`` (pilot response, barriers, outcomes).
Writes ``02_EASA/outputs/tradeoffs/``: ``tradeoffs.md`` (all tables), ``tradeoffs.json`` and figures T1–T2.
Tags: [D] read at source, [K] computed here, [Y] our judgement.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from day_common import console_text, protect_streams  # noqa: E402

from aerokit.canopy import cues as cu  # noqa: E402
from aerokit.canopy import montecarlo as mc  # noqa: E402

EASA = ROOT / "02_EASA"
OUT = EASA / "outputs" / "tradeoffs"
CUES_JSON = EASA / "inputs" / "cues.json"

ORG = mc.Architecture("ORG", "One microswitch at one pin, plain contact (organisers' example)", 0, (2,),
                      self_check=False)
ARCHS = {"A0": mc.ARCHITECTURES["A0"], "ORG": ORG, "A3": mc.ARCHITECTURES["A3"]}


@dataclass(frozen=True)
class Opt:
    key: str
    label: str
    arch: str
    cues: tuple[str, ...]
    barrier: str | None = None
    marks: bool = False
    trigger: str = "lever"      # alert onset: throttle-lever switch (0.35 s) or rpm/power + persistence (1.65 s)


MAIN = [
    Opt("O0", "No system (pilot check only)", "A0", ()),
    Opt("O1", "Passive bolt marks only", "A0", (), marks=True),
    Opt("O2", "Organisers' example: 1 microswitch + EFIS message + tone", "ORG", ("efis_message", "tone"),
        trigger="rpm"),
    Opt("O3", "LOCK-SENSE + lamp", "A3", ("light",)),
    Opt("O4", "LOCK-SENSE + lamp + voice + taxi chime", "A3", ("light", "voice", "taxi_chime")),
    Opt("O5", "O4 + lap-belt vibration tactor", "A3", ("light", "voice", "taxi_chime", "belt")),
    Opt("O6", "O5 + ground gate (separate release)", "A3", ("light", "voice", "taxi_chime", "belt"), "gate_release"),
    Opt("O7", "O5 + engine shut-down on the ground", "A3", ("light", "voice", "taxi_chime", "belt"), "esd_ground"),
    Opt("O8", "O5 + engine shut-down in flight", "A3", ("light", "voice", "taxi_chime", "belt"), "esd_air"),
    Opt("O9", "O5 + mechanical throttle pawl (cables from bolt plungers)", "A3",
        ("light", "voice", "taxi_chime", "belt"), "mech_pawl"),
    Opt("O10", "O5 + starter guard flap (released when bolts home)", "A3",
        ("light", "voice", "taxi_chime", "belt"), "start_guard"),
]
VARIANTS = [   # sub-options: one change against a main option
    Opt("O4t", "O4 with a generic tone instead of voice", "A3", ("light", "tone", "taxi_chime")),
    Opt("O4e", "O4 with an EFIS message instead of the dedicated lamp", "A3", ("efis_message", "voice", "taxi_chime")),
    Opt("O5m", "O5 + passive bolt marks", "A3", ("light", "voice", "taxi_chime", "belt"), marks=True),
    Opt("O6p", "O6 with a simple 50 N push-through", "A3", ("light", "voice", "taxi_chime", "belt"), "gate_push"),
    Opt("O6n", "O4 + ground gate, no tactor", "A3", ("light", "voice", "taxi_chime"), "gate_release"),
    Opt("O6m", "O6 + passive bolt marks", "A3", ("light", "voice", "taxi_chime", "belt"), "gate_release", marks=True),
    Opt("O5r", "O5 triggered by rpm + 0.5 s persistence instead of the throttle-lever switch", "A3",
        ("light", "voice", "taxi_chime", "belt"), trigger="rpm"),
    Opt("O4r", "O4 triggered by rpm + 0.5 s persistence instead of the throttle-lever switch", "A3",
        ("light", "voice", "taxi_chime"), trigger="rpm"),
    Opt("O4m", "O4 + passive bolt marks", "A3", ("light", "voice", "taxi_chime"), marks=True),
    Opt("O5k", "O4 + throttle-knob shaker (rejected: vibration source on a primary engine control)", "A3",
        ("light", "voice", "taxi_chime", "shaker")),
]

# Judgement scores for the criteria the model does not compute (0 = worst, 1 = best) [Y], with the reason.
RUBRIC = {
    "low_nuisance": ("What one false alert costs the pilot", {
        "O0": (1.0, "no alerts"), "O1": (1.0, "no alerts"),
        "O2": (0.7, "message + tone; plain switches flicker under flight loads (Van's notes, RV-14)"),
        "O3": (0.9, "a lamp only"), "O4": (0.75, "lamp + voice"), "O5": (0.65, "lamp + voice + vibration"),
        "O6": (0.45, "a stop at the holding point and a release action"),
        "O7": (0.25, "the engine stops; restart needed"), "O8": (0.0, "the engine stops in flight"),
        "O9": (0.45, "a stop at the holding point and a release action"), "O10": (0.4, "canopy must be locked to start, then may be reopened for taxi")}),
    "any_aircraft": ("Works on any canopy type, with or without EFIS, intercom or engine", {
        "O0": (1.0, "nothing to fit"), "O1": (0.8, "needs a view of each latch point"),
        "O2": (0.4, "needs an EFIS with a canopy discrete"),
        "O3": (0.9, "standalone lamp"), "O4": (0.8, "needs an audio input (most gliders have none)"),
        "O5": (0.8, "needs a lap belt only"),
        "O6": (0.45, "needs a throttle quadrant and air/ground sensing"),
        "O7": (0.35, "needs ignition access; not for gliders"), "O8": (0.3, "as O7"),
        "O9": (0.5, "needs a throttle and cable runs; no electrics needed"), "O10": (0.55, "needs a starter; not for pure gliders")}),
    "simple_retrofit": ("Parts, wiring and set-up work", {
        "O0": (1.0, "none"), "O1": (0.8, "paint bands; a window may be needed"),
        "O2": (0.9, "one switch, one wire, EFIS set-up"),
        "O3": (0.6, "4 sensors, harness, unit, lamp"), "O4": (0.55, "+ audio panel input"),
        "O5": (0.5, "+ belt tactor and a lead along the harness"), "O6": (0.3, "+ solenoid detent, IAS/GPS inputs"),
        "O7": (0.35, "+ ignition interface"), "O8": (0.35, "as O7"),
        "O9": (0.35, "cable runs from three lugs to the quadrant, rigged against 60 mm partial lock"), "O10": (0.45, "plunger cable to a flap at the starter")}),
    "device_worst_failure": ("Worst credible failure of the device itself", {
        "O0": (1.0, "no device"), "O1": (0.9, "a mis-painted band"),
        "O2": (0.3, "short to ground or a mis-set switch reads LOCKED (RV-14, fatal)"),
        "O3": (0.8, "self-checking; false green only for two double faults"), "O4": (0.8, "as O3"),
        "O5": (0.8, "as O3; a dead tactor is reported amber; nothing touches the engine controls"),
        "O6": (0.65, "detent jam in flight, mitigated by a mechanical breakout"),
        "O7": (0.3, "a logic fault cuts the engine in the air"), "O8": (0.1, "every false alert in flight cuts the engine"),
        "O9": (0.5, "cable slack misses a partial lock; no ground/air logic, blocks re-advance in the air"), "O10": (0.85, "fails only to prevent a start; must never cover the OFF direction")}),
}


def _load_cfg():
    spec = importlib.util.spec_from_file_location("canopy_day", EASA / "scripts" / "canopy_day.py")
    cd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cd)               # type: ignore[union-attr]
    return cd, cd.load(EASA / "inputs" / "inputs.json")


def mode(x):
    return x[1] if isinstance(x, list) else x


def tri(rng: np.random.Generator, x, n: int) -> np.ndarray:
    lo, md, hi = x
    if hi <= lo:
        return np.full(n, float(md))
    return rng.triangular(lo, md, hi, n)


def sensing(cfg: dict) -> dict:
    """Miss probability per hazard and false alerts per flight for each architecture [K]."""
    exp = cfg["_exp"]
    out = {}
    p_none = 1.0 - sum(exp.p_hazard.values())
    for k, a in ARCHS.items():
        res = {h: mc.simulate(a, h, cfg["_rates"], cfg["_tol"], n=cfg["n_samples"], seed=cfg["seed"])
               for h in (None, *mc.HAZARDS)}
        fa = p_none * (res[None].p_alert + exp.p_nuisance) if a.has_system else 0.0
        n = cfg["n_samples"]
        k_miss = {h: res[h].counts.get(mc.LOCKED, 0) for h in mc.HAZARDS}
        k_alert = res[None].counts.get(mc.CLOSED_UNLOCKED, 0) + res[None].counts.get(mc.OPEN, 0)
        out[k] = {"miss": {h: res[h].p_locked for h in mc.HAZARDS}, "fa": fa, "p_alert_none": res[None].p_alert,
                  "has_system": a.has_system, "fault_caution": p_none * res[None].p_fault,
                  "n": n, "seed": cfg["seed"], "k_miss": k_miss, "k_alert_none": k_alert,
                  "miss_upper95": {h: mc.wilson(k_miss[h], n)[1] for h in mc.HAZARDS},
                  "alert_none_upper95": mc.wilson(k_alert, n)[1]}
    return out


def build(params: dict, draw: dict | None = None):
    """Cue and barrier objects for one parameter set (``draw`` = sampled values, else the modes)."""
    pick = (lambda path, x: draw[path]) if draw else (lambda path, x: mode(x))
    conds = {k: v["weight"] for k, v in params["conditions"].items() if not k.startswith("_")}
    cues = {k: cu.Cue(k, c["label"], {cond: pick(f"cue.{k}.{cond}", p) for cond, p in c["p_detect"].items()})
            for k, c in params["cues"].items()}
    bars = {k: cu.Barrier(k, b["label"], pick(f"bar.{k}.od", b["p_override_distrust"]),
                          pick(f"bar.{k}.ot", b["p_override_trust"]), b["active_in_air"],
                          pick(f"bar.{k}.nh", b["p_new_hazard_engine_loss"]))
            for k, b in params["barriers"].items()}
    outc = {k: pick(f"out.{k}", v["value"]) for k, v in params["outcomes"].items()}
    marks = {h: pick(f"marks.{h}", v) for h, v in params["passive_marks"]["pilot_miss_factor"].items()}
    expo = {"p_nuisance": draw["exp.p_nuisance"], "p_partial": draw["exp.p_hazard_partial"],
            "miss_partial": draw["exp.miss_partial"], "miss_one_bolt": draw["exp.miss_one_bolt"]} if draw else None
    tm = params["timing"]
    med, p95 = pick("tim.med", tm["rt_median_s"]["value"]), pick("tim.p95", tm["rt_p95_s"]["value"])
    p95 = max(p95, med * 1.05)
    cases = [c for k, c in tm["cases"].items() if isinstance(c, dict)]
    timing = {trig: cu.p_in_time_lognormal([c["t_40kt_s"] - on for c in cases], [c["weight"] for c in cases], med, p95)
              for trig, on in tm["onset_s"].items() if trig in ("lever", "rpm")}
    return conds, cues, bars, outc, marks, expo, timing


def evaluate(opt: Opt, sens: dict, cfg: dict, conds, cues, bars, outc, marks, expo=None, timing=None) -> dict:
    """One option under one parameter set. ``expo`` (uncertainty draws only) overrides the nuisance rate and the
    partial-lock rate of ``inputs.json``; the sensing miss probabilities stay those of the central Monte Carlo."""
    exp = cfg["_exp"]
    p_haz = dict(exp.p_hazard)
    nuis = exp.p_nuisance
    p_miss = dict(exp.p_pilot_miss)
    if expo:
        p_haz["partial"], nuis = expo["p_partial"], expo["p_nuisance"]
        p_miss["partial"], p_miss["one_bolt"] = expo["miss_partial"], expo["miss_one_bolt"]
    u0 = {h: p_haz[h] * p_miss[h] for h in mc.HAZARDS}
    u = {h: u0[h] * (marks[h] if opt.marks else 1.0) for h in mc.HAZARDS}
    s = dict(sens[opt.arch])
    if expo and s["has_system"]:
        s["fa"] = (1.0 - sum(p_haz.values())) * (s["p_alert_none"] + nuis)
    cue_objs = [cues[c] for c in opt.cues]
    bar = bars[opt.barrier] if opt.barrier else None
    base = sum(u0.values())
    row = {"key": opt.key, "label": opt.label}
    for comp in ("full", "matching"):
        for dep in ("independent", "max"):
            r = cu.option_risk(s["miss"], u, s["fa"], cue_objs, conds, bar, comp, dep,
                               p_in_time=(timing or {}).get(opt.trigger, 1.0))
            f = cu.fatal_equivalent(r["risk"], r["risk_alerted"], s["fa"], bar, outc["p_open_given_unlocked_takeoff"],
                                    outc["f_open"], outc["f_engine_loss"], outc["f_shutdown_with_open_canopy"],
                                    outc["p_false_alert_airborne"])
            tag = f"{comp}_{'ind' if dep == 'independent' else 'max'}"
            row[f"rf_{tag}"] = base / r["risk"] if r["risk"] > 0 else float("inf")
            row[f"fatal_{tag}"] = f["total"]
            row[f"fatal_engine_{tag}"] = f["engine"]
            row[f"ppv_{tag}"] = r["ppv"]
            row[f"pdet_{tag}"] = r["p_detect"]
    row["fa_per_1000"] = 1000 * s["fa"] if opt.arch != "A0" else 0.0
    row["p_in_time"] = (timing or {}).get(opt.trigger, 1.0)
    row["base_fatal"] = base * outc["p_open_given_unlocked_takeoff"] * outc["f_open"]
    return row


def sample_draws(params: dict, n: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    cols: dict[str, np.ndarray] = {}
    for k, c in params["cues"].items():
        for cond, p in c["p_detect"].items():
            cols[f"cue.{k}.{cond}"] = tri(rng, p, n)
    for k, b in params["barriers"].items():
        cols[f"bar.{k}.od"] = tri(rng, b["p_override_distrust"], n)
        cols[f"bar.{k}.ot"] = tri(rng, b["p_override_trust"], n)
        cols[f"bar.{k}.nh"] = tri(rng, b["p_new_hazard_engine_loss"], n)
    for k, v in params["outcomes"].items():
        cols[f"out.{k}"] = tri(rng, v["value"], n)
    un = params["uncertainty"]
    cols["exp.miss_partial"] = tri(rng, un["p_pilot_miss_partial"]["value"], n)
    cols["exp.miss_one_bolt"] = tri(rng, un["p_pilot_miss_one_bolt"]["value"], n)
    cols["tim.med"] = tri(rng, params["timing"]["rt_median_s"]["value"], n)
    cols["tim.p95"] = tri(rng, params["timing"]["rt_p95_s"]["value"], n)
    for h, v in params["passive_marks"]["pilot_miss_factor"].items():
        cols[f"marks.{h}"] = tri(rng, v, n)
    un = params["uncertainty"]       # log-triangular: these span decades
    for key, name in (("p_nuisance", "exp.p_nuisance"), ("p_hazard_partial", "exp.p_hazard_partial")):
        lo, md, hi = (np.log10(x) for x in un[key]["value"])
        cols[name] = 10 ** rng.triangular(lo, md, hi, n)
    return [{k: float(a[i]) for k, a in cols.items()} for i in range(n)]


def uncertainty(opts: list[Opt], sens, cfg, params) -> dict:
    """Propagate the triangular ranges; independent cue bound under matching and full compliance [K]."""
    u = params["uncertainty"]
    draws = sample_draws(params, u["n_draws"], u["seed"])
    keys = [o.key for o in opts]
    rf_m = {k: [] for k in keys}
    rf_f = {k: [] for k in keys}
    fat = {k: [] for k in keys}
    for d in draws:
        objs = build(params, d)
        for o in opts:
            r = evaluate(o, sens, cfg, *objs)
            rf_m[o.key].append(r["rf_matching_ind"])
            rf_f[o.key].append(r["rf_full_ind"])
            fat[o.key].append(r["fatal_matching_ind"])
    out = {}
    fm = np.array([fat[k] for k in keys])
    best = np.bincount(fm.argmin(axis=0), minlength=len(keys)) / fm.shape[1]
    for i, k in enumerate(keys):
        q = lambda a: [float(np.percentile(a, p)) for p in (5, 50, 95)]   # noqa: E731
        out[k] = {"rf_matching": q(rf_m[k]), "rf_full": q(rf_f[k]), "fatal_matching": q(fat[k]),
                  "p_lowest_fatal": float(best[i])}
    return out


SWEEP_KEYS = ("O3", "O4", "O5", "O6", "O9", "O10")
SWEEP_C = (0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0)


def compliance_sweep(sens: dict, cfg: dict, params: dict) -> dict:
    """RF with compliance as an independent parameter (review 5 Nov), independent cues, central values [K]."""
    conds, cues, bars, outc, marks, _, timing = build(params)
    exp = cfg["_exp"]
    u = {h: exp.p_hazard[h] * exp.p_pilot_miss[h] for h in mc.HAZARDS}
    base = sum(u.values())
    opts = {o.key: o for o in MAIN}
    out = {}
    for k in SWEEP_KEYS:
        o = opts[k]
        s = sens[o.arch]
        out[k] = []
        for c in SWEEP_C:
            r = cu.option_risk(s["miss"], u, s["fa"], [cues[x] for x in o.cues], conds,
                               bars[o.barrier] if o.barrier else None, c, "independent",
                               p_in_time=timing.get(o.trigger, 1.0))
            out[k].append(base / r["risk"])
    return out


def rate_sensitivity(cfg: dict, params: dict) -> list[dict]:
    """How much the sensor failure-rate assumptions matter (review 5 Nov, problem 3) [K]: rerun the A3 sensing
    Monte Carlo with every rate scaled, with shorts added, and with no environment factor; report the misses and
    the resulting RF of O4 (alerts) and O6 (gate)."""
    import dataclasses
    r0 = cfg["_rates"]
    scen = [("as in inputs.json (NAMUR FMEDA × πE 18, shorts 0)", r0),
            ("no environment factor (rates ÷ 18)", dataclasses.replace(
                r0, stuck_active_per_h=r0.stuck_active_per_h / 18, stuck_inactive_per_h=r0.stuck_inactive_per_h / 18,
                open_per_h=r0.open_per_h / 18)),
            ("every rate × 10", dataclasses.replace(
                r0, stuck_active_per_h=r0.stuck_active_per_h * 10, stuck_inactive_per_h=r0.stuck_inactive_per_h * 10,
                open_per_h=r0.open_per_h * 10)),
            ("every rate × 100", dataclasses.replace(
                r0, stuck_active_per_h=r0.stuck_active_per_h * 100, stuck_inactive_per_h=r0.stuck_inactive_per_h * 100,
                open_per_h=r0.open_per_h * 100)),
            ("shorts added at the open-circuit rate × 10", dataclasses.replace(r0, short_per_h=r0.open_per_h * 10)),
            ("latent check every 1 000 h instead of 100 h", dataclasses.replace(r0, latent_interval_h=1000.0))]
    out = []
    opts = {o.key: o for o in MAIN}
    for label, rates in scen:
        c2 = {**cfg, "_rates": rates}
        sens = {"A3": sensing_one(c2, ARCHS["A3"])}
        objs = build(params)
        row = {"scenario": label, "miss_partial": sens["A3"]["miss"]["partial"],
               "miss_one_bolt": sens["A3"]["miss"]["one_bolt"], "fault_caution": sens["A3"]["fault_caution"]}
        for k in ("O4", "O5", "O6"):
            e = evaluate(opts[k], sens, c2, *objs)
            row[f"{k}_acts"], row[f"{k}_matches"] = e["rf_full_ind"], e["rf_matching_ind"]
        out.append(row)
    return out


def sensing_one(cfg: dict, a: mc.Architecture) -> dict:
    exp = cfg["_exp"]
    p_none = 1.0 - sum(exp.p_hazard.values())
    res = {h: mc.simulate(a, h, cfg["_rates"], cfg["_tol"], n=cfg["n_samples"], seed=cfg["seed"])
           for h in (None, *mc.HAZARDS)}
    return {"miss": {h: res[h].p_locked for h in mc.HAZARDS},
            "fa": p_none * (res[None].p_alert + exp.p_nuisance), "p_alert_none": res[None].p_alert,
            "has_system": True, "fault_caution": p_none * res[None].p_fault}


def sensing_options(cfg: dict, params: dict) -> list[dict]:
    """Extra NG sensing options (cues.json → sensing_options, from R9-physics §4.3) [K]: each option rerun in the
    sensing Monte Carlo with its own trip scatter, false-'locked' rate, short rate and nuisance rate, at the central σ
    and at the upper σ (handle-to-bolt ratio r = 0.5). Hazards an option is blind to get P(miss) = 1. Each option is
    then evaluated with the voice set (O4), the recommended alert-only set (O5) and, for reference, the rejected gate
    set (O6)."""
    import dataclasses
    so = params["sensing_options"]
    exp0, r0, tol0 = cfg["_exp"], cfg["_rates"], cfg["_tol"]
    objs = build(params)
    opts = {o.key: o for o in MAIN}
    out = []
    for k, o in so.items():
        if k.startswith("_"):
            continue
        row = {"key": k, "label": o["label"], "blind": o["blind"], "self_check": o["self_check"]}
        for tag, sig in (("c", o["sigma"][0]), ("u", o["sigma"][1])):
            rates = dataclasses.replace(r0, stuck_active_per_h=o["p_false"], latent_interval_h=2.0,
                                        short_per_h=o.get("short_per_flight", r0.short_per_h))
            tol = dataclasses.replace(tol0, sigma_trip_mm=sig, sigma_full_mm=sig)
            if o["per_bolt"]:
                a = mc.Architecture(k, o["label"], 1, (0, 1, 2), self_check=o["self_check"])
            else:
                a = mc.Architecture(k, o["label"], 0 if "unseated" in o["blind"] else 1, (0,), self_check=o["self_check"])
            exp = mc.Exposure(exp0.p_hazard, exp0.p_pilot_miss, o["p_nuisance"])
            c2 = {**cfg, "_rates": rates, "_tol": tol, "_exp": exp}
            s = sensing_one(c2, a)
            for h in o["blind"]:
                s["miss"][h] = 1.0
            row[f"miss_partial_{tag}"], row[f"miss_one_{tag}"] = s["miss"]["partial"], s["miss"]["one_bolt"]
            row[f"miss_unseated_{tag}"] = s["miss"]["unseated"]
            row[f"fa_{tag}"] = s["fa"]
            for ok in ("O4", "O5", "O6"):
                e = evaluate(dataclasses.replace(opts[ok], arch=k), {k: s}, c2, *objs)
                row[f"{ok}_acts_{tag}"], row[f"{ok}_match_{tag}"] = e["rf_full_ind"], e["rf_matching_ind"]
        out.append(row)
    return out


def mcda(rows: dict, params: dict) -> tuple[dict, dict]:
    """Scores (0–1) per criterion: three computed from the model, four from RUBRIC; then cu.mcda_rank."""
    keys = [o.key for o in MAIN]
    lg = lambda x: np.log10(max(x, 1.0))   # noqa: E731
    eff = {k: lg(rows[k]["rf_full_ind"]) for k in keys}
    dis = {k: 0.5 * (lg(rows[k]["rf_matching_ind"]) + lg(rows[k]["rf_matching_max"])) for k in keys}
    emax, dmax = max(eff.values()) or 1.0, max(dis.values()) or 1.0
    base_fatal = rows["O0"]["base_fatal"]
    scores = {}
    for k in keys:
        new = rows[k]["fatal_engine_matching_ind"] / base_fatal
        scores[k] = {"effectiveness": eff[k] / emax, "distrust_robustness": dis[k] / dmax,
                     "no_new_hazard": float(np.clip(1.0 - new, 0.0, 1.0))}
        for crit, (_, table) in RUBRIC.items():
            scores[k][crit] = table[k][0]
    m = params["mcda"]
    rank = cu.mcda_rank(scores, m["weights"], concentration=m["concentration"])
    return scores, rank


def fmt_rf(x: float) -> str:
    if x == float("inf"):
        return "∞"
    return f"{x:,.0f}×".replace(",", " ") if x >= 100 else (f"{x:.1f}×" if x >= 1.05 else "1.0×")


def fmt_e(x: float) -> str:
    return "0" if x == 0 else f"{x:.1e}"


def write_md(rows, var_rows, unc, scores, rank, sens, params, sweep=None, rates=None, sopts=None) -> str:
    L = ["# EASA feedback-element trade-off (generated by `02_EASA/scripts/easa_tradeoffs.py`; do not edit)", "",
         "Scope: alert system only; the latch is not changed. RF = reduction of the per-flight probability of taking "
         "off with the canopy not locked and nothing effective done, against no system. *Acts* = the pilot acts on "
         "every alert he notices; *matches* = he acts as often as alerts have been right (probability matching). "
         "Cue detection combined as independent (upper) or fully dependent (lower bound, the best single cue). "
         "Fatal = fatal outcomes per flight from canopy openings plus engine losses the device causes. "
         "Inputs: `02_EASA/inputs/inputs.json` and `cues.json` (source and tag per value). [K] unless marked.", "",
         "**Design decisions (user, 5 Nov 2026):** no mechanical restriction on the throttle lever (a jammed or "
         "wrongly engaged restriction is a serious risk in flight), and no vibration on the throttle knob (a vibration "
         "source on a primary engine control; CS 23.1141(c) 'tendency to creep due to ... vibration'; research/R10). "
         "The vibration cue moves to a lap-belt tactor. The recommended set is **O5** (dedicated lamp + voice "
         "\"CANOPY, CANOPY\" + taxi chime + lap-belt tactor, lever-switch trigger). The knob shaker (O5k), the "
         "take-off gate (O6, O6p/n/m), the cable throttle pawl (O9) and the starter guard (O10) stay as compared and "
         "rejected options; engine shut-down (O7, O8) was already rejected. O6 to O10 now build on the belt set.", ""]
    s3 = sens["A3"]
    L += [f"## 1. Sensing (Monte Carlo, {s3['n']} flights per cell, seed {s3['seed']})", "",
          "Each cell: observed count / flights → estimate, and the 95 % Wilson upper bound. **A zero count is not a zero "
          "probability**: it only bounds the probability (≈ 3/n). The false-alert column adds the separate nuisance "
          "rate of `inputs.json` (3e-4 per flight, [Y]); the sensor model alone produced the counts shown.", "",
          "| Architecture | Miss: partial lock | Miss: one bolt out | Miss: not seated | Sensor-model alerts with no hazard | False + nuisance per 1 000 flights |",
          "|---|---:|---:|---:|---:|---:|"]

    def cell(k, n, ub):
        return f"{k}/{n} → {k / n:.2g} (≤ {ub:.1g})"
    for k, a in ARCHS.items():
        s = sens[k]
        if not s["has_system"]:
            L.append(f"| {a.label} | 1 (no system) | 1 | 1 | — | 0 |")
            continue
        L.append(f"| {a.label} | " + " | ".join(cell(s['k_miss'][h], s['n'], s['miss_upper95'][h]) for h in mc.HAZARDS)
                 + f" | {cell(s['k_alert_none'], s['n'], s['alert_none_upper95'])} | {1000 * s['fa']:.2f} |")
    L += ["", "## 2. Main options (central values)", "",
          "| Option | RF acts | RF matches (ind. – dep.) | PPV | P(notice) ind. – dep. | P(act before 40 kt) | Fatal per 10⁶ flights (matches, ind.) | of which engine losses |",
          "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for o in MAIN:
        r = rows[o.key]
        L.append(f"| {o.key} {o.label} | {fmt_rf(r['rf_full_ind'])} | {fmt_rf(r['rf_matching_ind'])} – "
                 f"{fmt_rf(r['rf_matching_max'])} | {r['ppv_matching_ind']:.2f} | {r['pdet_full_ind']:.2f} – "
                 f"{r['pdet_full_max']:.2f} | {r['p_in_time']:.3f} | {1e6 * r['fatal_matching_ind']:.2f} | {1e6 * r['fatal_engine_matching_ind']:.2f} |")
    L += ["", "## 3. Sub-options (one change each)", "",
          "| Variant | RF acts | RF matches (ind.) | Fatal per 10⁶ flights (matches, ind.) | Compare with |",
          "|---|---:|---:|---:|---|"]
    for o in VARIANTS:
        r = var_rows[o.key]
        ref = {"O4t": "O4", "O4e": "O4", "O5m": "O5", "O6p": "O6", "O6n": "O6", "O6m": "O6", "O5r": "O5", "O4r": "O4", "O4m": "O4", "O5k": "O5"}[o.key]
        rr = rows[ref]
        L.append(f"| {o.key} {o.label} | {fmt_rf(r['rf_full_ind'])} | {fmt_rf(r['rf_matching_ind'])} | "
                 f"{1e6 * r['fatal_matching_ind']:.2f} | {ref}: {fmt_rf(rr['rf_full_ind'])}, "
                 f"{fmt_rf(rr['rf_matching_ind'])}, {1e6 * rr['fatal_matching_ind']:.2f} |")
    n = params["uncertainty"]["n_draws"]
    L += ["", f"## 4. Uncertainty ({n} draws over every triangular range; matches, independent cues)", "",
          "| Option | RF matches: 5 % – median – 95 % | Fatal per 10⁶ flights: 5 % – median – 95 % | Share of draws with the lowest fatal |",
          "|---|---|---|---:|"]
    for k, v in unc.items():
        a, b = v["rf_matching"], v["fatal_matching"]
        L.append(f"| {k} | {fmt_rf(a[0])} – {fmt_rf(a[1])} – {fmt_rf(a[2])} | {1e6 * b[0]:.2f} – {1e6 * b[1]:.2f} – "
                 f"{1e6 * b[2]:.2f} | {100 * v['p_lowest_fatal']:.1f} % |")
    w = params["mcda"]["weights"]
    crit = list(w)
    L += ["", "## 5. Multi-criteria comparison", "",
          "Computed criteria [K]: *effectiveness* = log RF (acts), *distrust robustness* = log RF (matches, mean of both "
          "bounds), each scaled to the best option; *no new hazard* = 1 − (engine-loss fatalities the device adds ÷ "
          "fatalities with no system). Judgement criteria [Y]: the table after this one gives the reason for every score. "
          "Weights resampled 20 000 times (Dirichlet, concentration %g)." % params["mcda"]["concentration"], "",
          "| Option | " + " | ".join(f"{c} ({w[c]:.2f})" for c in crit) + " | Weighted score | Ranked first in | Mean rank |",
          "|---|" + "---:|" * (len(crit) + 3)]
    for o in sorted(MAIN, key=lambda o: -rank[o.key]["score"]):
        s = scores[o.key]
        L.append(f"| {o.key} | " + " | ".join(f"{s[c]:.2f}" for c in crit) +
                 f" | **{rank[o.key]['score']:.3f}** | {100 * rank[o.key]['p_first']:.1f} % | {rank[o.key]['mean_rank']:.1f} |")
    L += ["", "**Reasons for the judgement scores [Y]:**", "", "| Option | " +
          " | ".join(RUBRIC[c][0] for c in RUBRIC) + " |", "|---|" + "---|" * len(RUBRIC)]
    for o in MAIN:
        L.append(f"| {o.key} | " + " | ".join(f"{RUBRIC[c][1][o.key][0]:.2f}: {RUBRIC[c][1][o.key][1]}" for c in RUBRIC) + " |")
    if sweep:
        L += ["", "## 6. Compliance as an independent parameter (review 5 Nov)", "",
              "RF when the pilot acts on a noticed alert with probability *c*, set directly instead of tied to the PPV "
              "(independent cues, central values, lever trigger). Probability matching corresponds to c = PPV ≈ 0.66 "
              "here; the ranking of the options is the same at every c.", "",
              "| Option | " + " | ".join(f"c = {c:g}" for c in SWEEP_C) + " |", "|---|" + "---:|" * len(SWEEP_C)]
        for k, vals in sweep.items():
            L.append(f"| {k} | " + " | ".join(fmt_rf(v) for v in vals) + " |")
    if rates:
        L += ["", "## 7. Do the sensor failure-rate assumptions matter? (review 5 Nov, problem 3)", "",
              "The rates in `inputs.json` transfer an industrial NAMUR sensor FMEDA with a MIL-HDBK-217F switch "
              "environment factor; they are not an Extra NG installation rate. This table reruns the A3 sensing Monte "
              "Carlo with the rates changed. Misses are set by rigging scatter and the common mis-rig, not by random "
              "sensor failure, so the RF barely moves until the rates are raised a hundredfold. Fault cautions of 0 "
              "mean none in 200 000 flights (below the Monte Carlo resolution of ≈ 1.5e-5), not zero.", "",
              "| Scenario | Miss: partial | Miss: one bolt | Fault cautions per flight | O4 acts / matches | O5 acts / matches | O6 (rejected) acts / matches |",
              "|---|---:|---:|---:|---|---|---|"]
        for r in rates:
            L.append(f"| {r['scenario']} | {r['miss_partial']:.2g} | {r['miss_one_bolt']:.2g} | "
                     f"{r['fault_caution']:.1e} | {fmt_rf(r['O4_acts'])} / {fmt_rf(r['O4_matches'])} | "
                     f"{fmt_rf(r['O5_acts'])} / {fmt_rf(r['O5_matches'])} | "
                     f"{fmt_rf(r['O6_acts'])} / {fmt_rf(r['O6_matches'])} |")
    if sopts:
        L += ["", "## 8. Sensing options for the Extra NG (R9-physics inputs)", "",
              "Each option rerun in the sensing Monte Carlo with its own trip scatter σ (handle-equivalent mm), "
              "false-'locked' rate, short rate and nuisance rate (`cues.json` → `sensing_options`, basis in "
              "`research/R9_not_locked_detection_physics.md` §4.3). Columns marked *r = 0.5* use the upper σ, i.e. "
              "if each mm of handle moves the bolt only 0.5 mm (the ratio is not published; measure it in step 2). "
              "RF with the voice set (O4: lamp + voice + chime), the recommended set (O5: O4 + lap-belt tactor) and, "
              "for reference, the rejected gate set (O6). 'Sees' = partial lock / one bolt out / not seated.", "",
              "| Option | Sees P / O / U | Miss partial (σ central → r = 0.5) | Miss one bolt | False + nuisance per 1 000 flights | O4 acts / distrust | O5 acts / distrust | O5 distrust at r = 0.5 | O6 (rejected) distrust |",
              "|---|---|---|---|---:|---|---|---|---|"]
        for r in sopts:
            sees = " / ".join("N" if h in r["blind"] else "Y" for h in ("partial", "one_bolt", "unseated"))
            L.append(f"| {r['key']} {r['label']} | {sees} | {r['miss_partial_c']:.2g} → {r['miss_partial_u']:.2g} | "
                     f"{r['miss_one_c']:.2g} | {1000 * r['fa_c']:.2f} | {fmt_rf(r['O4_acts_c'])} / {fmt_rf(r['O4_match_c'])} | "
                     f"{fmt_rf(r['O5_acts_c'])} / {fmt_rf(r['O5_match_c'])} | {fmt_rf(r['O5_match_u'])} | "
                     f"{fmt_rf(r['O6_match_c'])} |")
    L.append("")
    return "\n".join(L)


def figures(rows: dict, unc: dict, sweep: dict | None = None) -> list[str]:
    import datawiz as dw
    cd, _ = _load_cfg()
    OUT.mkdir(parents=True, exist_ok=True)
    S = dw.Seti(str(OUT / "tradeoffs.seti.json"), hedef="sunum-tam")
    # rrf is on x in the dot plots (T1) and on y in the sweep (T3): deliberate, both log, same name and unit
    S.nicelik("rrf", "Risk reduction factor", None, eksen="serbest", olcek="log")
    S.nicelik("fatal", "Fatal outcomes per million flights", None, eksen="x", olcek="log")
    S.varlik("Pilot always acts", renk="#07648e")
    S.varlik("Pilot matches reliability", renk="#5f5f5f")
    S.varlik("Engine loss caused by the device", renk="#d55e00")
    done = []
    keys = [o.key for o in MAIN if o.key != "O0"]
    labels = {o.key: f"{o.key} {o.label}" for o in MAIN}
    short = {"O1": "O1 bolt marks", "O2": "O2 organisers' switch", "O3": "O3 LOCK-SENSE + lamp",
             "O4": "O4 + voice", "O5": "O5 + belt tactor", "O6": "O6 + ground gate",
             "O7": "O7 + ground shut-down", "O8": "O8 + in-flight shut-down",
             "O9": "O9 + mechanical pawl", "O10": "O10 + starter guard"}
    # T1 — RF per option: acts vs matches (dumbbell, log x), with the matching 5–95 % range
    fig, ax = S.figur(oran=0.62)
    ys = np.arange(len(keys))[::-1]
    full = np.array([max(rows[k]["rf_full_ind"], 1.0) for k in keys])
    match = np.array([max(rows[k]["rf_matching_ind"], 1.0) for k in keys])
    lo = np.array([max(unc[k]["rf_matching"][0], 1.0) for k in keys])
    hi = np.array([max(unc[k]["rf_matching"][2], 1.0) for k in keys])
    ax.hlines(ys, match, full, colors="#bdbdbd", linewidth=2, zorder=1)
    ax.hlines(ys, lo, hi, colors="#5f5f5f", linewidth=6, alpha=0.25, zorder=1,
              label="Matches: 5–95 % range")
    for vals, lab in ((full, "Pilot always acts"), (match, "Pilot matches reliability")):
        st = S.stil(lab, isaretli=True)
        st["linestyle"] = "none"
        ax.plot(vals, ys, zorder=3, **st)
    ax.set_yticks(ys, [short[k] for k in keys])
    ax.set_xlim(0.8, 3e4)
    S.eksen(ax, x="rrf")
    cd.pow10(ax, "x")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(OUT / "T1_risk_reduction_by_option"), sessiz=True)
    done.append("T1_risk_reduction_by_option")
    # T2 — fatal outcomes per million flights (matches), canopy part vs engine-loss part
    fig, ax = S.figur(oran=0.62)
    allk = [o.key for o in MAIN]
    ys = np.arange(len(allk))[::-1]
    tot = np.array([1e6 * rows[k]["fatal_matching_ind"] for k in allk])
    eng = np.array([1e6 * rows[k]["fatal_engine_matching_ind"] for k in allk])
    st = S.stil("Pilot matches reliability", isaretli=True)
    st["linestyle"] = "none"
    ax.plot(tot, ys, zorder=3, **st)
    st2 = S.stil("Engine loss caused by the device", isaretli=True)
    st2["linestyle"] = "none"
    m = eng > 0
    ax.plot(eng[m], ys[m], zorder=4, **st2)
    lo = np.array([1e6 * unc[k]["fatal_matching"][0] for k in allk])
    hi = np.array([1e6 * unc[k]["fatal_matching"][2] for k in allk])
    ax.hlines(ys, lo, hi, colors="#5f5f5f", linewidth=6, alpha=0.25, zorder=1, label="5–95 % range")
    ax.set_xlim(0.1, 400)
    ax.set_yticks(ys, [("O0 no system" if k == "O0" else short[k]) for k in allk])
    S.eksen(ax, x="fatal")
    cd.pow10(ax, "x")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(OUT / "T2_fatal_outcomes_by_option"), sessiz=True)
    done.append("T2_fatal_outcomes_by_option")
    _ = labels
    if sweep:   # T3 — RF vs compliance, one line per option (log y)
        S.nicelik("compliance", "Probability the pilot acts on a noticed alert", None, eksen="x")
        names3 = {"O3": "O3 lamp", "O4": "O4 + voice", "O5": "O5 + belt tactor", "O6": "O6 + ground gate",
                  "O9": "O9 + mechanical pawl", "O10": "O10 + starter guard"}
        cols = {"O3": "#cc79a7", "O4": "#009e73", "O5": "#000000", "O6": "#0072b2", "O9": "#56b4e9", "O10": "#e69f00"}
        for k in names3:
            S.varlik(names3[k], renk=cols[k])
        fig, ax = S.figur(oran=0.62)
        for k in SWEEP_KEYS:
            ax.plot(SWEEP_C, sweep[k], **S.stil(names3[k], isaretli=True))
        ax.set_yscale("log")
        ax.set_xlim(0, 1.05)
        S.eksen(ax, x="compliance", y="rrf")
        cd.pow10(ax, "y")
        dw.etiket.cizgi_sonu(ax)
        S.kaydet(fig, str(OUT / "T3_compliance_sweep"), sessiz=True)
        done.append("T3_compliance_sweep")
    return done


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help", "/?") for a in argv):
        print(console_text(__doc__))
        return 0
    protect_streams()
    _, cfg = _load_cfg()
    params = json.loads(CUES_JSON.read_text(encoding="utf-8"))
    sens = sensing(cfg)
    objs = build(params)
    rows = {o.key: evaluate(o, sens, cfg, *objs) for o in MAIN}
    var_rows = {o.key: evaluate(o, sens, cfg, *objs) for o in VARIANTS}
    unc = uncertainty(MAIN, sens, cfg, params)
    scores, rank = mcda(rows, params)
    sweep = compliance_sweep(sens, cfg, params)
    rates = rate_sensitivity(cfg, params)
    sopts = sensing_options(cfg, params)
    OUT.mkdir(parents=True, exist_ok=True)
    md = write_md(rows, var_rows, unc, scores, rank, sens, params, sweep, rates, sopts)
    (OUT / "tradeoffs.md").write_text(md, encoding="utf-8")
    (OUT / "tradeoffs.json").write_text(json.dumps({"sensing": sens, "main": rows, "variants": var_rows,
                                                    "uncertainty": unc, "mcda_scores": scores, "mcda_rank": rank,
                                                    "compliance_sweep": {"c": SWEEP_C, **sweep}, "rate_sensitivity": rates,
                                                    "sensing_options": sopts},
                                                   indent=1, default=float), encoding="utf-8")
    print(f"wrote {(OUT / 'tradeoffs.md').relative_to(ROOT).as_posix()} and tradeoffs.json")
    for o in MAIN:
        r = rows[o.key]
        print(f"  {o.key:3s} RF acts {fmt_rf(r['rf_full_ind']):>9s}  matches {fmt_rf(r['rf_matching_ind']):>7s}"
              f"–{fmt_rf(r['rf_matching_max']):>6s}  fatal/1e6 {1e6 * r['fatal_matching_ind']:7.2f}  "
              f"MCDA {rank[o.key]['score']:.3f} first {100 * rank[o.key]['p_first']:5.1f} %")
    if "--no-figures" not in argv:
        names = figures(rows, unc, sweep)
        for nme in names:
            t = (OUT / f"{nme}.denetim.txt").read_text(encoding="utf-8")
            print(f"  figure {nme}: " + t.splitlines()[0])
    print("Result: trade-off tables written. Next step: read tradeoffs.md and look at the PNGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
