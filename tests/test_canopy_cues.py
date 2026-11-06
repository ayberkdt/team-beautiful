"""aerokit.canopy.cues: feedback elements and barriers on top of the sensing Monte Carlo."""
import pytest

from aerokit.canopy import cues as cu
from aerokit.canopy import montecarlo as mc
from aerokit.verification import check, check_true

U = {"partial": 1e-3 * 0.5, "one_bolt": 1e-4 * 0.9, "unseated": 1e-4 * 0.05}
MISS = {"partial": 5e-4, "one_bolt": 1e-3, "unseated": 1e-5}
COND = {"normal": 0.7, "busy": 0.3}
LIGHT = cu.Cue("vis", "light", {"normal": 0.9, "busy": 0.6})
VOICE = cu.Cue("aur", "voice", {"normal": 0.9, "busy": 0.6})
PERFECT = cu.Cue("p", "perfect", {"normal": 1.0, "busy": 1.0})


def _mc_results():
    rates = mc.ChannelRates(1e-6, 1e-6, 1e-6, 1e-6)
    tol = mc.Tolerance()
    a = mc.ARCHITECTURES["A3"]
    return {h: mc.simulate(a, h, rates, tol, n=20_000, seed=5) for h in (None, *mc.HAZARDS)}


def test_perfect_cue_reproduces_the_sensing_model():
    res = _mc_results()
    exp = mc.Exposure({"partial": 1e-3, "one_bolt": 1e-4, "unseated": 1e-4},
                      {"partial": 0.5, "one_bolt": 0.9, "unseated": 0.05}, p_nuisance=2e-4)
    u = {h: exp.p_hazard[h] * exp.p_pilot_miss[h] for h in mc.HAZARDS}
    miss = {h: res[h].p_locked for h in mc.HAZARDS}
    p_none = 1 - sum(exp.p_hazard.values())
    fa = p_none * (res[None].p_alert + exp.p_nuisance)
    for comp in ("full", "matching"):
        ref = mc.takeoff_risk(res, exp, comp)
        new = cu.option_risk(miss, u, fa, [PERFECT], COND, compliance=comp)
        check(f"{comp}: cue layer with a perfect cue equals takeoff_risk", new["risk"], ref["risk"], rtol=1e-12)


def test_no_cue_no_barrier_gives_no_benefit_beyond_the_check():
    r = cu.option_risk(MISS, U, 1e-4, [], COND)
    check("no cue: risk equals the unalerted baseline", r["risk"], r["baseline"], rtol=1e-12)


def test_independent_bound_is_above_dependent_and_both_above_single():
    single = cu.p_detect([LIGHT], COND)
    ind = cu.p_detect([LIGHT, VOICE], COND, "independent")
    dep = cu.p_detect([LIGHT, VOICE], COND, "max")
    check("single light: 0.7*0.9 + 0.3*0.6", single, 0.81, rtol=1e-12)
    check("two cues independent: 0.7*0.99 + 0.3*0.84", ind, 0.945, rtol=1e-12)
    check_true("dependent bound equals the best single cue", abs(dep - single) < 1e-12)
    check_true("independent ≥ dependent", ind >= dep)


def test_gate_without_override_leaves_only_sensing_misses():
    gate = cu.Barrier("gate", "gate", p_override_distrust=0.0)
    r = cu.option_risk(MISS, U, 1e-3, [LIGHT], COND, barrier=gate, compliance="matching")
    check("unbeatable gate: risk = Σ u·miss", r["risk"], sum(U[h] * MISS[h] for h in U), rtol=1e-12)


def test_gate_helps_most_when_trust_is_low():
    gate = cu.Barrier("gate", "gate", p_override_distrust=0.5)
    no = cu.option_risk(MISS, U, 1e-2, [LIGHT, VOICE], COND, compliance="matching")
    yes = cu.option_risk(MISS, U, 1e-2, [LIGHT, VOICE], COND, barrier=gate, compliance="matching")
    check_true("low PPV (nuisance 1e-2): PPV < 0.1", no["ppv"] < 0.1)
    check_true("gate with 50 % override at least halves the matching risk", yes["risk"] < 0.55 * no["risk"])


def test_in_flight_shutdown_turns_false_alerts_into_engine_losses():
    esd = cu.Barrier("esd", "shut-down", 0.0, active_in_air=True, p_new_hazard_engine_loss=1e-6)
    f = cu.fatal_equivalent(risk=1e-6, risk_alerted=4e-7, false_alert_per_flight=1e-3, barrier=esd, p_open=0.5,
                            f_open=0.12, f_engine_loss=0.2, f_shutdown_with_open_canopy=0.25,
                            p_false_alert_airborne=0.5)
    check("canopy term uses only the unalerted part", f["canopy"], 6e-7 * 0.5 * 0.12, rtol=1e-12)
    check("engine term = 4e-7*0.25 + 1e-3*0.5*0.2 + 1e-6*0.2", f["engine"], 1e-7 + 1e-4 + 2e-7, rtol=1e-12)
    check_true("false alerts in the air dominate", f["engine"] > 100 * f["canopy"])
    gate = cu.Barrier("gate", "gate", 0.5)
    g = cu.fatal_equivalent(1e-6, 4e-7, 1e-3, gate, 0.5, 0.12, 0.2, 0.25, 0.5)
    check("ground gate adds no engine term", g["engine"], 0.0, atol=0.0)


def test_risk_splits_into_missed_and_alerted_parts():
    r = cu.option_risk(MISS, U, 1e-4, [LIGHT], COND)
    missed = sum(U[h] * MISS[h] for h in U)
    check("risk = sensing misses + alerted-but-failed", r["risk"], missed + r["risk_alerted"], rtol=1e-12)


def test_mcda_rank_is_stable_for_a_dominant_option():
    scores = {"a": {"x": 1.0, "y": 1.0}, "b": {"x": 0.2, "y": 0.3}}
    r = cu.mcda_rank(scores, {"x": 0.6, "y": 0.4}, n=2000)
    check_true("dominant option ranks first in every weight sample", r["a"]["p_first"] == 1.0)


def test_input_validation():
    with pytest.raises(ValueError):
        cu.Cue("bad", "bad", {"normal": 1.2})
    with pytest.raises(ValueError):
        cu.p_detect([LIGHT], {"normal": 0.5, "busy": 0.4})


def test_response_time_window():
    med = cu.p_in_time_lognormal([1.5], [1.0], 1.5, 3.0)
    p95 = cu.p_in_time_lognormal([3.0], [1.0], 1.5, 3.0)
    check("window = median gives 0.5", med, 0.5, atol=1e-12)
    check("window = p95 gives 0.95", p95, 0.95, atol=1e-9)
    check("no window gives 0", cu.p_in_time_lognormal([0.0], [1.0], 1.5, 3.0), 0.0, atol=0.0)
    late = cu.option_risk(MISS, U, 1e-4, [LIGHT], COND, p_in_time=0.5)
    early = cu.option_risk(MISS, U, 1e-4, [LIGHT], COND, p_in_time=1.0)
    check_true("a shorter window raises the risk", late["risk"] > early["risk"])
    gate = cu.Barrier("gate", "gate", 0.0)
    g = cu.option_risk(MISS, U, 1e-4, [LIGHT], COND, barrier=gate, p_in_time=0.1)
    check("an unbeatable gate does not depend on the window", g["risk"], sum(U[h] * MISS[h] for h in U), rtol=1e-12)


def test_compliance_as_an_independent_parameter():
    r1 = cu.option_risk(MISS, U, 1e-3, [LIGHT], COND, compliance=1.0)
    rf = cu.option_risk(MISS, U, 1e-3, [LIGHT], COND, compliance="full")
    check("compliance=1.0 equals 'full'", r1["risk"], rf["risk"], rtol=1e-12)
    r0 = cu.option_risk(MISS, U, 1e-3, [LIGHT], COND, compliance=0.0)
    check("compliance=0 without barrier: no benefit beyond the check", r0["risk"], r0["baseline"], rtol=1e-12)
    with pytest.raises(ValueError):
        cu.option_risk(MISS, U, 1e-3, [LIGHT], COND, compliance=1.5)
