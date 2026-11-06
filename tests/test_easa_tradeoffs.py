"""EASA feedback trade-off (02_EASA/scripts/easa_tradeoffs.py): the orderings the conclusions rest on."""
import importlib.util
import json
import pathlib
import sys

import pytest

from aerokit.verification import check, check_true

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def run():
    spec = importlib.util.spec_from_file_location("easa_tradeoffs", ROOT / "02_EASA" / "scripts" / "easa_tradeoffs.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m          # dataclasses look the module up by name
    spec.loader.exec_module(m)
    _, cfg = m._load_cfg()
    cfg = {**cfg, "n_samples": 40_000}
    params = json.loads(m.CUES_JSON.read_text(encoding="utf-8"))
    sens = m.sensing(cfg)
    objs = m.build(params)
    rows = {o.key: m.evaluate(o, sens, cfg, *objs) for o in m.MAIN + m.VARIANTS}
    return m, sens, rows, params


def test_inputs_carry_a_source_and_tag(run):
    _, _, _, params = run
    for group in ("cues", "barriers"):
        for k, v in params[group].items():
            check_true(f"{group}.{k} has source and tag", bool(v.get("source")) and bool(v.get("tag")))
    w = params["mcda"]["weights"]
    check("MCDA weights sum to 1", sum(w.values()), 1.0, atol=1e-12)


def test_organisers_switch_misses_two_thirds_of_single_bolt_faults(run):
    _, sens, _, _ = run
    check("one switch at one of three bolts: miss one-bolt-out ≈ 2/3", sens["ORG"]["miss"]["one_bolt"], 2 / 3, atol=0.02)
    check_true("LOCK-SENSE misses one bolt out < 1e-2", sens["A3"]["miss"]["one_bolt"] < 1e-2)


def test_each_cue_adds_when_the_pilot_acts(run):
    _, _, r, _ = run
    check_true("lamp + voice beats lamp", r["O4"]["rf_full_ind"] > r["O3"]["rf_full_ind"])
    check_true("adding the lap-belt tactor beats O4", r["O5"]["rf_full_ind"] > r["O4"]["rf_full_ind"])
    check_true("adding the gate beats O5", r["O6"]["rf_full_ind"] > r["O5"]["rf_full_ind"])


def test_alert_only_collapses_under_distrust_but_a_gate_does_not(run):
    _, _, r, _ = run
    check_true("O5 under matching < 5x", r["O5"]["rf_matching_ind"] < 5)
    check_true("gate keeps > 3x the O5 gain under matching", r["O6"]["rf_matching_ind"] > 3 * r["O5"]["rf_matching_ind"])
    check_true("separate release beats push-through", r["O6"]["rf_matching_ind"] > r["O6p"]["rf_matching_ind"])


def test_in_flight_shutdown_is_no_better_than_no_system(run):
    _, _, r, _ = run
    check_true("O8 fatal ≥ 0.9 × no system", r["O8"]["fatal_matching_ind"] >= 0.9 * r["O0"]["fatal_matching_ind"])
    check_true("O8 fatal is mostly engine losses", r["O8"]["fatal_engine_matching_ind"] > 0.9 * r["O8"]["fatal_matching_ind"])
    check_true("ground gate has no engine-loss term", r["O6"]["fatal_engine_matching_ind"] == 0.0)


def test_timing_and_mechanical_options(run):
    _, _, r, _ = run
    check_true("rpm trigger is worse than the lever trigger (pilot acts)", r["O5r"]["rf_full_ind"] < r["O5"]["rf_full_ind"])
    check_true("lever trigger: P(act before 40 kt) > 0.95", r["O5"]["p_in_time"] > 0.95)
    check_true("starter guard is weaker than the throttle gate under distrust",
               r["O10"]["rf_matching_ind"] < r["O6"]["rf_matching_ind"])
    check_true("mechanical pawl sits between O5 and the electric gate under distrust",
               r["O5"]["rf_matching_ind"] < r["O9"]["rf_matching_ind"] < r["O6"]["rf_matching_ind"])


def test_extra_ng_sensing_options(run):
    m, _, _, params = run
    _, cfg = m._load_cfg()
    cfg = {**cfg, "n_samples": 40_000}
    so = {r["key"]: r for r in m.sensing_options(cfg, params)}
    check_true("linkage-only options are blind to one bolt out (miss = 1)",
               so["S6"]["miss_one_c"] == 1.0 and so["S7"]["miss_one_c"] == 1.0)
    check_true("inductive per bolt beats the bare contact under distrust (lower nuisance)",
               so["S1"]["O6_match_c"] > so["S2"]["O6_match_c"])
    check_true("per-bolt inductive sees one bolt out (miss < 1e-2)", so["S1"]["miss_one_c"] < 1e-2)
    check_true("if r = 0.5 the per-bolt options lose most of their distrust gain",
               so["S1"]["O6_match_u"] < 0.2 * so["S1"]["O6_match_c"])
