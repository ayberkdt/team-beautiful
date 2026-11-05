"""Canopy alert retrofit (aerokit.canopy): latch facts, sensors, warning logic, fault tree, Monte Carlo, ERCS."""
import itertools
import math

import numpy as np

from aerokit.canopy import (EXTRA_NG, AlertLevel, CanopyAlertUnit, CanopyState, Channel, FlightInputs, Phase,
                            Reading)
from aerokit.canopy import barriers, fmea, fta
from aerokit.canopy import montecarlo as mc
from aerokit.canopy.logic import LogicConfig, canopy_state
from aerokit.canopy.mechanism import engagement_fraction, trip_probabilities, trip_window
from aerokit.verification import check, check_true, expect_error

A, I, F = Reading.ACTIVE, Reading.INACTIVE, Reading.FAULT
BOLTS = ("bolt_front", "bolt_centre", "bolt_rear")


def locked():
    return {"seated": A, **{b: A for b in BOLTS}}


def partial():
    return {"seated": A, **{b: I for b in BOLTS}}


def opened():
    return {"seated": I, **{b: I for b in BOLTS}}


# --- mechanism -----------------------------------------------------------------------------------------------

def test_extra_ng_facts_from_aaib():
    m = EXTRA_NG
    check("three shoot bolts (AAIB p. 8)", m.bolts, 3)
    check("handle travel partial -> full 10 mm (p. 9)", m.travel_mm, 10.0)
    check("ramp 15 mm / 5 mm = 3:1 (p. 8)", m.ramp_advantage, 3.0)
    check("drive-open force 3 x 90 N (p. 24)", m.force_drive_open_partial_n, 3 * m.force_open_partial_n)
    check_true("no visible difference at the frame (p. 20)", not m.visible_difference_at_frame)
    check_true("open & released handle = locked handle (p. 9)", m.open_and_released_reads_locked)
    check("engagement at partial gap", engagement_fraction(60.0), 0.0)
    check("engagement half way", engagement_fraction(65.0), 0.5)
    check("engagement clipped above full", engagement_fraction(75.0), 1.0)


def test_trip_probabilities_closed_form_matches_sampling():
    rng = np.random.default_rng(3)
    t, st, sf, hb = 66.5, 0.6, 0.3, 68.0
    miss, false = trip_probabilities(t, st, sf, hb)
    n = 400_000
    x = rng.uniform(60.0, hb, n)
    trip = rng.normal(t, st, n)
    check("miss closed form vs MC", miss, np.mean(x >= trip), atol=3e-3)
    full = rng.normal(70.0, sf, n)
    trip2 = rng.normal(t, st, n)
    check("false-alarm closed form vs MC", false, np.mean(full < trip2), atol=1e-3)
    m_lo, f_lo = trip_probabilities(62.0, st, sf, hb)
    m_hi, f_hi = trip_probabilities(69.5, st, sf, hb)
    check_true("earlier trip point -> more misses, fewer false alarms", m_lo > m_hi and f_lo < f_hi)
    w = trip_window(0.3, 0.3, 67.0, max_miss=1e-3, max_false=1e-3)
    check_true("a trip window exists for 0.3 mm rigging", w is not None and 67.0 <= w[0] <= w[1] < 70.0, w)
    check_true("none for 0.5 mm rigging if 68 mm must count as hazardous",
               trip_window(0.5, 0.2, 68.0, 1e-3, 1e-3) is None)
    check_true("no window if rigging is sloppy", trip_window(3.0, 0.5, 68.0, 1e-3, 1e-3) is None)
    expect_error("hazard threshold outside travel", trip_probabilities, 66.0, 0.5, 0.3, 71.0, error=ValueError)
    expect_error("sigma must be positive", trip_probabilities, 66.0, 0.0, 0.3, 68.0, error=ValueError)


# --- sensors ---------------------------------------------------------------------------------------------------

def test_channel_coding_and_fault_injection():
    check_true("healthy follows truth", Channel("c").read(True) is A and Channel("c").read(False) is I)
    check_true("open circuit detected with self-check", Channel("c", "open_circuit").read(True) is F)
    check_true("short detected with self-check", Channel("c", "short_circuit").read(False) is F)
    check_true("open circuit looks INACTIVE on a plain contact",
               Channel("c", "open_circuit", self_check=False).read(True) is I)
    check_true("short looks ACTIVE on a plain contact (dangerous)",
               Channel("c", "short_circuit", self_check=False).read(False) is A)
    check_true("stuck active is a valid code (latent)", Channel("c", "stuck_active").read(False) is A)
    rng = np.random.default_rng(0)
    reads = [Channel("c", "intermittent", chatter_fraction=0.3).read(True, rng) for _ in range(4000)]
    check("chatter fraction", sum(r is I for r in reads) / 4000, 0.3, atol=0.03)
    expect_error("unknown failure mode", Channel, "c", "melted", error=ValueError)


# --- fusion ----------------------------------------------------------------------------------------------------

def test_canopy_state_truth_table():
    s, b = ("seated",), BOLTS
    check_true("all active -> LOCKED", canopy_state(locked(), s, b)[0] is CanopyState.LOCKED)
    check_true("seated, bolts out -> CLOSED_UNLOCKED", canopy_state(partial(), s, b)[0] is CanopyState.CLOSED_UNLOCKED)
    check_true("one bolt out -> CLOSED_UNLOCKED",
               canopy_state({**locked(), "bolt_rear": I}, s, b)[0] is CanopyState.CLOSED_UNLOCKED)
    check_true("not seated -> OPEN", canopy_state(opened(), s, b)[0] is CanopyState.OPEN)
    st, why = canopy_state({**opened(), "bolt_centre": A}, s, b)
    check_true("bolt sensed while not seated -> UNKNOWN", st is CanopyState.UNKNOWN and "not seated" in why)
    check_true("fault -> UNKNOWN", canopy_state({**locked(), "bolt_front": F}, s, b)[0] is CanopyState.UNKNOWN)
    check_true("missing reading -> UNKNOWN", canopy_state({"seated": A}, s, b)[0] is CanopyState.UNKNOWN)
    check_true("seated-only architecture takes closed as locked (its flaw)",
               canopy_state({"seated": A}, s, ())[0] is CanopyState.LOCKED)
    two = ("s1", "s2")
    check_true("seated disagreement -> UNKNOWN",
               canopy_state({"s1": A, "s2": I, **{x: A for x in b}}, two, b)[0] is CanopyState.UNKNOWN)


def test_vectorised_fusion_equals_scalar_on_every_combination():
    code = {A: mc.ACTIVE, I: mc.INACTIVE, F: mc.FAULT}
    names = {mc.LOCKED: CanopyState.LOCKED, mc.CLOSED_UNLOCKED: CanopyState.CLOSED_UNLOCKED,
             mc.OPEN: CanopyState.OPEN, mc.UNKNOWN: CanopyState.UNKNOWN}
    for n_seat, n_bolt in ((1, 3), (2, 2), (1, 0), (0, 3)):
        seat_n = tuple(f"s{i}" for i in range(n_seat))
        bolt_n = tuple(f"b{i}" for i in range(n_bolt))
        combos = list(itertools.product((A, I, F), repeat=n_seat + n_bolt))
        sv = np.array([[code[r] for r in c[:n_seat]] for c in combos], np.int8).reshape(len(combos), n_seat)
        bv = np.array([[code[r] for r in c[n_seat:]] for c in combos], np.int8).reshape(len(combos), n_bolt)
        vec = mc.fuse(sv, bv)
        bad = 0
        for c, v in zip(combos, vec):
            st, _ = canopy_state(dict(zip(seat_n + bolt_n, c)), seat_n, bolt_n)
            bad += names[int(v)] is not st
        check(f"vector == scalar, {n_seat} seated + {n_bolt} bolt channels ({len(combos)} combos)", bad, 0)


# --- logic -----------------------------------------------------------------------------------------------------

def run(unit, script):
    """script: list of (t, inputs-kwargs, readings) → outputs."""
    return [unit.step(FlightInputs(t=t, **kw), r) for t, kw, r in script]


def test_power_up_self_test_then_green():
    u = CanopyAlertUnit()
    out = run(u, [(0.0, {}, locked()), (1.0, {}, locked()), (3.5, {}, locked())])
    check_true("lamp test first 3 s", out[0].lamp_test and out[0].aural and out[0].green_locked)
    check_true("then parked, green, silent",
               out[2].phase is Phase.PARKED and out[2].green_locked and out[2].level is AlertLevel.NONE)
    check_true("recorder discrete false during lamp test", not out[0].recorder_locked and out[2].recorder_locked)


def test_partial_lock_caution_in_taxi_warning_at_takeoff_power():
    u = CanopyAlertUnit()
    run(u, [(0.0, {}, partial()), (4.0, {}, partial())])
    o = run(u, [(5.0, {"engine_running": True, "throttle": 0.2}, partial())])[0]
    check_true("taxi: amber CANOPY UNLOCKED with chime",
               o.phase is Phase.TAXI and o.level is AlertLevel.CAUTION and o.message == "CANOPY UNLOCKED" and o.aural)
    o2 = run(u, [(7.0, {"engine_running": True, "throttle": 0.2}, partial())])[0]
    check_true("chime is single (silent after 1 s)", not o2.aural and o2.level is AlertLevel.CAUTION)
    o3 = run(u, [(8.0, {"engine_running": True, "throttle": 1.0}, partial())])[0]
    check_true("take-off power: red flashing voice",
               o3.phase is Phase.TAKEOFF and o3.level is AlertLevel.WARNING and o3.flashing and o3.aural)
    o4 = run(u, [(9.0, {"engine_running": True, "throttle": 1.0, "ias_kt": 45.0}, partial())])[0]
    check_true("alert present before the roll keeps its voice above the inhibit speed", o4.aural)
    check_true("green never on while unlocked", not any(x.green_locked for x in (o, o2, o3, o4)))


def test_open_canopy_parked_dark_taxi_advisory():
    u = CanopyAlertUnit()
    run(u, [(0.0, {}, opened())])
    o = run(u, [(4.0, {}, opened())])[0]
    check_true("parked with canopy open: no alert", o.level is AlertLevel.NONE and not o.green_locked)
    o = run(u, [(5.0, {"engine_running": True}, opened())])[0]
    check_true("taxi with canopy open: advisory, silent", o.level is AlertLevel.ADVISORY and not o.aural)
    u2 = CanopyAlertUnit(config=LogicConfig(taxi_open_allowed=False))
    run(u2, [(0.0, {}, opened()), (4.0, {}, opened())])
    o = run(u2, [(5.0, {"engine_running": True}, opened())])[0]
    check_true("taxi-open not allowed: caution", o.level is AlertLevel.CAUTION)


def flight_to_cruise(u):
    run(u, [(0.0, {}, locked()), (4.0, {"engine_running": True, "throttle": 0.2}, locked()),
            (10.0, {"engine_running": True, "throttle": 1.0, "ias_kt": 20.0}, locked())])
    for k in range(20):
        u.step(FlightInputs(t=11.0 + k, engine_running=True, throttle=1.0, ias_kt=60.0 + 5 * k), locked())
    return run(u, [(40.0, {"engine_running": True, "throttle": 0.8, "ias_kt": 150.0}, locked())])[0]


def test_inflight_unlock_persistence_and_ack():
    u = CanopyAlertUnit()
    o = flight_to_cruise(u)
    check_true("airborne and locked", o.phase is Phase.AIRBORNE and o.green_locked)
    kw = {"engine_running": True, "throttle": 0.8, "ias_kt": 150.0}
    rear_out = {**locked(), "bolt_rear": I}
    out = run(u, [(41.0, kw, rear_out), (41.3, kw, locked()), (41.4, kw, locked())])
    check_true("0.3 s bounce filtered (no alert)", all(x.level is AlertLevel.NONE for x in out))
    out = run(u, [(50.0, kw, rear_out), (50.3, kw, rear_out), (50.6, kw, rear_out)])
    check_true("not yet after 0.3 s", out[1].level is AlertLevel.NONE)
    check_true("warning after 0.5 s persistence", out[2].level is AlertLevel.WARNING and out[2].aural)
    check_true("in-flight loss of lock logged", any("IN-FLIGHT LOSS OF LOCK" in e for _, e in u.events))
    o = run(u, [(51.0, {**kw, "ack": True}, rear_out)])[0]
    check_true("ack silences voice, light stays red steady",
               o.level is AlertLevel.WARNING and not o.aural and not o.flashing)
    o = run(u, [(52.0, kw, opened())])[0]
    check_true("worse/new state shows after persistence only", o.message == "CANOPY UNLOCKED")
    o = run(u, [(53.0, kw, opened())])[0]
    check_true("new alert (CANOPY OPEN) re-arms the voice",
               o.level is AlertLevel.WARNING and o.message == "CANOPY OPEN" and o.aural)


def test_new_alert_near_rotation_has_deferred_voice():
    u = CanopyAlertUnit()
    run(u, [(0.0, {}, locked()), (4.0, {"engine_running": True, "throttle": 0.2}, locked()),
            (10.0, {"engine_running": True, "throttle": 1.0, "ias_kt": 20.0}, locked()),
            (12.0, {"engine_running": True, "throttle": 1.0, "ias_kt": 45.0}, locked())])
    kw = {"engine_running": True, "throttle": 1.0, "ias_kt": 50.0}
    out = run(u, [(13.0, kw, partial()), (13.6, kw, partial())])
    check_true("new warning in the roll above 40 kt: red flashing, voice deferred",
               out[1].level is AlertLevel.WARNING and out[1].flashing and not out[1].aural)
    for k in range(5):
        u.step(FlightInputs(t=14.0 + k, engine_running=True, throttle=1.0, ias_kt=60.0 + 5 * k), partial())
    o = u.step(FlightInputs(t=35.0, engine_running=True, throttle=1.0, ias_kt=100.0), partial())
    check_true("voice resumes 10 s after lift-off", o.phase is Phase.AIRBORNE and o.aural)


def test_sensor_fault_never_green_and_rejected_takeoff():
    u = CanopyAlertUnit()
    run(u, [(0.0, {}, locked()), (4.0, {}, locked())])
    o = run(u, [(5.0, {"engine_running": True}, {**locked(), "bolt_centre": F}),
                (6.0, {"engine_running": True}, {**locked(), "bolt_centre": F})])[1]
    check_true("fault -> amber CANOPY SENS, green off",
               o.level is AlertLevel.CAUTION and o.message == "CANOPY SENS" and not o.green_locked and o.fault)
    u2 = CanopyAlertUnit()
    run(u2, [(0.0, {}, locked()), (4.0, {"engine_running": True}, locked()),
             (5.0, {"engine_running": True, "throttle": 1.0}, locked())])
    o = run(u2, [(8.0, {"engine_running": True, "throttle": 0.0, "ias_kt": 10.0}, locked())])[0]
    check_true("throttle closed at low speed = rejected take-off -> taxi", o.phase is Phase.TAXI)
    o = run(u2, [(9.0, {"powered": False}, locked())])[0]
    check_true("power loss: dark panel, no green", o.phase is Phase.OFF and not o.green_locked)
    check_true("power loss logged", any("power lost" in e for _, e in u2.events))


def test_power_restored_in_flight_goes_airborne():
    u = CanopyAlertUnit()
    run(u, [(0.0, {"engine_running": True, "ias_kt": 120.0}, locked())])
    o = run(u, [(4.0, {"engine_running": True, "ias_kt": 120.0}, locked())])[0]
    check_true("restart in flight -> AIRBORNE", o.phase is Phase.AIRBORNE)


def test_logic_driven_by_injected_channel_faults():
    """End-to-end: physical latch state → channels with injected faults → unit."""
    names = ("seated",) + BOLTS
    chans = {n: Channel(n) for n in names}
    chans["bolt_rear"].failure = "stuck_active"
    truth = {"seated": True, "bolt_front": False, "bolt_centre": False, "bolt_rear": False}     # partial lock
    u = CanopyAlertUnit()
    out = None
    for t in (0.0, 4.0, 5.0):
        out = u.step(FlightInputs(t=t, engine_running=t >= 5.0), {n: chans[n].read(truth[n]) for n in names})
    check_true("one stuck bolt sensor does not hide a partial lock", out.level is AlertLevel.CAUTION)
    truth_open = {n: False for n in names}
    u2 = CanopyAlertUnit()
    for t in (0.0, 4.0, 5.0):
        out = u2.step(FlightInputs(t=t), {n: chans[n].read(truth_open[n]) for n in names})
    check_true("stuck bolt sensor revealed when the canopy is open", out.state is CanopyState.UNKNOWN)


# --- fault tree ------------------------------------------------------------------------------------------------

def test_fault_tree_algebra_and_importance():
    tree = ("AND", "H", ("OR", "M", ("AND", "S1", "S2")))
    p = {"H": 1e-2, "M": 1e-3, "S1": 0.1, "S2": 0.2}
    exact = p["H"] * (1 - (1 - p["M"]) * (1 - p["S1"] * p["S2"]))
    check("exact gate algebra", fta.evaluate(tree, p), exact, rtol=1e-12)
    check("enumeration equals gate algebra", fta.exact_by_enumeration(tree, p), exact, rtol=1e-12)
    mcs = fta.minimal_cut_sets(tree)
    check_true("cut sets {H,M}, {H,S1,S2}", set(mcs) == {frozenset("HM"), frozenset({"H", "S1", "S2"})}, mcs)
    check_true("rare-event sum is conservative", fta.cut_set_probability(tree, p) >= exact)
    imp = fta.importance(tree, p)
    check("Birnbaum of H = P(top|H=1) - P(top|H=0)", imp["H"]["birnbaum"], exact / p["H"], rtol=1e-12)
    check("FV of H = 1 (in every cut set)", imp["H"]["fussell_vesely"], 1.0)
    rep = ("OR", ("AND", "A", "B"), ("AND", "A", "C"))
    expect_error("repeated event rejected by gate algebra", fta.evaluate, rep, {"A": .1, "B": .1, "C": .1},
                 error=ValueError)
    check("repeated event exact", fta.exact_by_enumeration(rep, {"A": .1, "B": .1, "C": .1}), 0.1 * 0.19,
          rtol=1e-12)
    check("absorption: {A} absorbs {A,B}", len(fta.minimal_cut_sets(("OR", "A", ("AND", "A", "B")))), 1)
    check("standby q = (lT/2)/(1+lT/2)", fta.standby_unavailability(1e-5, 100.0), 5e-4 / (1 + 5e-4), rtol=1e-12)
    expect_error("bad gate", fta.evaluate, ("XOR", "A", "B"), {"A": .1, "B": .1}, error=ValueError)


# --- Monte Carlo -----------------------------------------------------------------------------------------------

RATES = mc.ChannelRates(stuck_active_per_h=2e-5, stuck_inactive_per_h=2e-5, open_per_h=1e-5, short_per_h=1e-5,
                        flight_h=1.0, latent_interval_h=100.0)


def test_monte_carlo_architectures_rank_as_expected():
    tol = mc.Tolerance()
    res = {a: {h: mc.simulate(mc.ARCHITECTURES[a], h, RATES, tol, n=60_000, seed=7)
               for h in (None,) + mc.HAZARDS} for a in ("A0", "A1", "A3", "A4")}
    check("no system: every hazard missed", res["A0"]["partial"].p_locked, 1.0)
    check("seated-only misses every partial lock", res["A1"]["partial"].p_locked, 1.0, atol=1e-3)
    check_true("seated-only catches an unseated canopy", res["A1"]["unseated"].p_locked < 0.01)
    check_true("A3 catches partial locks", res["A3"]["partial"].p_locked < 0.01)
    check_true("A3 catches one-bolt hazards", res["A3"]["one_bolt"].p_locked < 0.02)
    check_true("A4 (dual) misses no more than A3",
               res["A4"]["one_bolt"].p_locked <= res["A3"]["one_bolt"].p_locked + 2e-3)
    check_true("A4 has more false alarms than A3 (more channels must all agree)",
               res["A4"][None].p_alert >= res["A3"][None].p_alert)
    lo, hi = res["A3"]["partial"].interval(mc.LOCKED)
    check_true("Wilson interval brackets the estimate", lo <= res["A3"]["partial"].p_locked <= hi)
    expect_error("unknown hazard", mc.simulate, mc.ARCHITECTURES["A3"], "bird", RATES, tol, error=ValueError)


def test_monte_carlo_matches_fault_tree_for_single_bolt_sensor():
    """A2 under a one-bolt hazard: missed if the hazard is at an unsensed bolt, or the sensed bolt reads ACTIVE."""
    tol = mc.Tolerance(trip_mm=66.0, sigma_trip_mm=0.8, hazard_below_mm=68.0)
    r = mc.simulate(mc.ARCHITECTURES["A2"], "one_bolt", RATES, tol, n=300_000, seed=11)
    q = RATES.mode_probabilities()
    tol_miss, f_full = trip_probabilities(tol.trip_mm, tol.sigma_trip_mm, tol.sigma_full_mm, tol.hazard_below_mm)
    healthy = 1 - sum(q.values())
    seat_active = 1 - q["stuck_inactive"] - q["open"] - q["short"]
    active_other = q["stuck_active"] + healthy * (1 - f_full)        # hazard at an unsensed bolt
    active_sensed = q["stuck_active"] + healthy * tol_miss            # hazard at the sensed (rear) bolt
    expected = seat_active * (2 / 3 * active_other + 1 / 3 * active_sensed)
    lo, hi = r.interval(mc.LOCKED)
    check_true(f"MC miss {r.p_locked:.4f} within the analytic {expected:.4f} (95 % CI {lo:.4f}-{hi:.4f})",
               lo - 2e-3 <= expected <= hi + 2e-3)
    check_true("probabilities sum to one", math.isclose(sum(r.p(s) for s in range(4)), 1.0))


def test_takeoff_risk_and_cry_wolf():
    tol = mc.Tolerance()
    res = {h: mc.simulate(mc.ARCHITECTURES["A3"], h, RATES, tol, n=40_000, seed=5) for h in (None,) + mc.HAZARDS}
    exp = mc.Exposure({"partial": 1e-3, "one_bolt": 1e-4, "unseated": 1e-4},
                      {"partial": 0.5, "one_bolt": 0.9, "unseated": 0.05})
    full = mc.takeoff_risk(res, exp, "full")
    match = mc.takeoff_risk(res, exp, "matching")
    check_true("system reduces risk by > 10x with full compliance", full["reduction_factor"] > 10, full)
    check_true("probability matching lowers the benefit", match["risk"] >= full["risk"])
    check("baseline = sum p_h * p_miss_h", full["baseline"], 1e-3 * 0.5 + 1e-4 * 0.9 + 1e-4 * 0.05, rtol=1e-12)
    expect_error("bad compliance model", mc.takeoff_risk, res, exp, "sometimes", error=ValueError)


def test_common_misrig_and_nuisance_terms():
    tol = mc.Tolerance(p_misrig_common=0.01, misrig_shift_mm=-10.0)   # trips at 58 mm: every partial lock reads LOCKED
    r = mc.simulate(mc.ARCHITECTURES["A4"], "partial", RATES, tol, n=100_000, seed=21)
    check("common mis-rigging defeats even dual channels (miss ≈ p_misrig)", r.p_locked, 0.01, atol=2e-3)
    late = mc.simulate(mc.ARCHITECTURES["A3"], None, RATES, mc.Tolerance(p_misrig_common=0.01, misrig_shift_mm=+5.0),
                       n=100_000, seed=22)
    check("late mis-rigging shows up as false alarms instead", late.p_alert, 0.01, atol=2e-3)
    res = {h: mc.simulate(mc.ARCHITECTURES["A3"], h, RATES, mc.Tolerance(), n=20_000, seed=23)
           for h in (None,) + mc.HAZARDS}
    e0 = mc.Exposure({"partial": 1e-3, "one_bolt": 0.0, "unseated": 0.0}, {"partial": 0.5, "one_bolt": 0, "unseated": 0})
    e1 = mc.Exposure(e0.p_hazard, e0.p_pilot_miss, p_nuisance=5e-4)
    check("PPV 0.5 when nuisance equals the unalerted hazard rate",
          mc.takeoff_risk(res, e1, "matching")["ppv"], 0.5, atol=0.02)
    check_true("nuisance does not change the full-compliance risk",
               math.isclose(mc.takeoff_risk(res, e0, "full")["risk"], mc.takeoff_risk(res, e1, "full")["risk"]))
    none = {h: mc.simulate(mc.ARCHITECTURES["A0"], h, RATES, mc.Tolerance(), n=1000, seed=1) for h in (None,) + mc.HAZARDS}
    check("no system has no nuisance alerts", mc.takeoff_risk(none, e1, "matching")["false_alarm_per_flight"], 0.0)


# --- ERCS and FMEA ---------------------------------------------------------------------------------------------

def test_ercs_warning_barrier_gain():
    for key, sc in barriers.SCENARIOS.items():
        without, with_ = barriers.with_and_without(sc)
        check(f"{key}: warning barrier adds weight 3", with_.barrier_sum - without.barrier_sum, 3)
        check_true(f"{key}: score improves or holds", with_.barrier_score >= without.barrier_score)
        check_true(f"{key}: numerical risk lower or equal", with_.value <= without.value)
    expect_error("warning barrier must be left out", barriers.with_and_without,
                 {**barriers.SCENARIOS["inflight_unlock"],
                  "barriers": {"warning systems": "remaining"}}, error=ValueError)


def test_fmea_table_renders():
    text = fmea.markdown_table(probs={"stuck_active": 1e-3})
    check_true("one row per failure mode", text.count("\n") == len(fmea.FMEA) + 2)
    check_true("probability filled where a rate exists", "1.0e-03" in text)
    check_true("emergency opening hazard listed", any("emergency opening" in r.effect for r in fmea.FMEA))


def test_sensor_fault_at_takeoff_power_is_red():
    u = CanopyAlertUnit()
    fault = {**locked(), "bolt_centre": F}
    run(u, [(0.0, {}, fault), (4.0, {}, fault), (10.0, {"engine_running": True, "throttle": 0.2}, fault)])
    o = run(u, [(20.0, {"engine_running": True, "throttle": 1.0}, fault)])[0]
    check_true("unconfirmed is not locked: red CANOPY SENS at take-off power",
               o.level is AlertLevel.WARNING and o.message == "CANOPY SENS" and not o.green_locked)


def test_fault_injection_demo_verdicts():
    from aerokit.canopy import faults
    res = {r["key"]: r for r in faults.run_all()}
    check_true("no-fault cases correct", res["ok_locked"]["verdict"] == "correct" and res["ok_partial"]["verdict"] == "correct")
    check_true("one stuck sensor does not hide a partial lock", res["stuck_one"]["verdict"] == "correct")
    check_true("wire break and short are shown as faults",
               res["wire_break"]["verdict"] == "fault shown" and res["short"]["verdict"] == "fault shown")
    check_true("open canopy + stuck bolt sensor -> red at take-off",
               res["open_stuck"]["takeoff"]["level"] == "WARNING" and not res["open_stuck"]["takeoff"]["green"])
    check_true("power loss is dark, never green", res["power_lost"]["verdict"] == "dark")
    check_true("stuck-inactive is a nuisance, not a miss", res["stuck_inactive"]["verdict"] == "nuisance")
    missed = sorted(k for k, r in res.items() if r["verdict"] == "MISSED")
    check_true("only the two latent combinations are missed", missed == ["misrig_all", "one_bolt_stuck"], missed)
    check_true("no case shows green on an unlocked canopy except the listed misses",
               all(not r["takeoff"]["green"] or r["locked"] or k in missed for k, r in res.items()))
