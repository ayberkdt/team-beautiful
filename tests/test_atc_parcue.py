"""Automated PAR cue: closed loop returns to the path, the cue stays quiet, and bad data never produces guidance."""
import math

import numpy as np
import pytest

from aerokit.approach import Runway
from aerokit.atc.parcue import (END_STATES, CueConfig, CueLogic, Fault, PilotModel, Plot, ReplayConfig, cue_changes,
                                fly_replay)

RWY = Runway(51.0, 4.0, 10.0, 250.0)
SEEDS = range(30)


def _plots(n, t0=0.0, y=0.0, z=0.0, r0=9000.0, gs=70.0):
    return [Plot(t0 + i, r0 - gs * (t0 + i), y, z) for i in range(n)]


def _state_after(logic, plots):
    fr = None
    for p in plots:
        fr = logic.step(p.t, p)
    return fr


def test_clean_runs_reach_minimums_near_the_path():
    ends = [fly_replay(RWY, seed=s)[-1] for s in SEEDS]
    gate = [e for e in ends if e["state"] == "MINIMUMS"]
    assert len(gate) >= 0.95 * len(ends)
    assert np.percentile([abs(e["y_m"]) for e in gate], 95) < 30
    assert np.percentile([abs(e["z_dev_m"]) for e in gate], 95) < 15


def test_a_limits_call_in_a_clean_run_is_a_real_deviation():
    """Seed 4: the aircraft really is about 17 m low at 1.5 km, so OUTSIDE LIMITS is the right call, not a false alarm."""
    fr = fly_replay(RWY, seed=4)
    first = next(f for f in fr if f["state"] == "OUTSIDE LIMITS")
    assert abs(first["z_dev_m"]) > 15 and first["x_m"] < 2000


def test_without_the_cue_the_aircraft_stays_off_the_path():
    fr = fly_replay(RWY, pilot=PilotModel(follows_cue=False), seed=1)
    assert fr[-1]["state"] == "OUTSIDE LIMITS"
    assert all(abs(f["y_m"]) > 100 for f in fr)


def test_first_cue_points_back_to_the_path():
    fr = fly_replay(RWY, seed=1)
    first = next(f for f in fr if f["hdg_new"])
    assert first["hdg_rel_deg"] < 0 and first["lat_word"] == "TURN LEFT"      # right of the centreline
    assert next(f for f in fr if f["sink_new"])["sink_fpm"] > 700            # above the path: more than nominal


def test_cue_changes_as_the_aircraft_returns():
    fr = fly_replay(RWY, seed=1)
    valid = [f for f in fr if f["state"] == "VALID"]
    assert abs(valid[0]["y_m"]) > 100 and abs(valid[-1]["y_m"]) < 40
    assert min(f["hdg_rel_deg"] for f in valid) <= -6
    assert abs(valid[-1]["hdg_rel_deg"]) <= 4                                # target has gone back near the course
    assert "ON COURSE" in {f["lat_word"] for f in valid}


def test_turn_word_never_points_away_from_the_path():
    for seed in SEEDS:
        for f in fly_replay(RWY, seed=seed):
            if f["hdg_new"] and f["lat_word"] == "TURN RIGHT":
                assert f["lat_dots"] < 0.15           # right of the path it must say EASE RIGHT (filter noise allowed)
            if f["hdg_new"] and f["lat_word"] == "TURN LEFT":
                assert f["lat_dots"] > -0.15


def test_ending_a_turn_is_said_as_ease_and_stays_silent():
    fr = fly_replay(RWY, seed=1)
    assert any(f["lat_word"] == "EASE RIGHT" for f in fr)
    assert not any(f["voice"] == "turn_right" and f["y_m"] > 30 for f in fr)


def test_wind_trim_learns_a_crosswind():
    fr = fly_replay(RWY, rc=ReplayConfig(crosswind_ms=5.0), seed=2)
    assert fr[-1]["state"] == "MINIMUMS"
    crab = math.degrees(math.asin(5.0 / 70.0))
    assert fr[-1]["trim_deg"] == pytest.approx(-crab, abs=2.0)
    assert abs(fr[-1]["y_m"]) < 40


def test_voice_is_for_important_changes_only():
    calls = [sum(1 for f in fly_replay(RWY, seed=s) if f["voice"]) for s in SEEDS]
    assert np.median(calls) <= 8


def test_voice_gap_between_routine_calls():
    routine = {"turn_left", "turn_right", "descend_more", "descend_less", "on_path"}
    ts = [f["t"] for f in fly_replay(RWY, seed=3) if f["voice"] in routine]
    assert all(b - a >= CueConfig().voice_gap_s for a, b in zip(ts, ts[1:]))


def test_target_changes_are_rate_limited():
    c = CueConfig()
    ts = [f["t"] for f in fly_replay(RWY, seed=4) if f["hdg_new"]]
    assert all(b - a >= c.update_s for a, b in zip(ts, ts[1:]))


def test_delayed_data_is_shown_with_no_new_target():
    fr = fly_replay(RWY, faults=(Fault("delay", 60, 75, 3.0),), seed=5)
    d = [f for f in fr if f["state"] == "DELAYED"]
    assert d and all(f["age_s"] > CueConfig().delayed_after_s for f in d)
    assert all(f["hdg_new"] == 0 and f["sink_new"] == 0 and f["hdg_rel_deg"] is None for f in d)
    assert all(f["lat_dots"] is not None for f in d)                         # the old needle stays, marked as old
    assert fr[-1]["state"] == "MINIMUMS"


def test_invalid_flag_removes_the_needles_and_recovers():
    fr = fly_replay(RWY, faults=(Fault("invalid", 60, 63),), seed=6)
    bad = [f for f in fr if f["state"] == "INVALID"]
    assert bad and all(f["lat_dots"] is None and f["vert_dots"] is None for f in bad)
    assert any(f["voice"] == "restored" for f in fr)
    assert fr[-1]["state"] == "MINIMUMS"


def test_jump_is_rejected_not_flown():
    fr = fly_replay(RWY, faults=(Fault("jump", 60, 63, 400.0),), seed=7)
    assert any(f["state"] == "INVALID" for f in fr)
    assert max(abs(f["y_m"]) for f in fr if f["t"] > 50) < 80                # the aircraft did not follow the jump


def test_persistent_bad_data_ends_in_lost_never_restored():
    fr = fly_replay(RWY, faults=(Fault("jump", 60, 200, 400.0),), seed=8)
    assert fr[-1]["state"] == "LOST"
    assert not any(f["voice"] == "restored" for f in fr)


def test_dropout_gives_lost_after_about_five_seconds_and_latches():
    fr = fly_replay(RWY, faults=(Fault("dropout", 60, 66),), seed=9)
    lost = next(f for f in fr if f["state"] == "LOST")
    assert 64 <= lost["t"] <= 67
    assert all(f["state"] == "LOST" for f in fr if f["t"] >= lost["t"])      # the radar came back; LOST stays
    assert all(f["lat_dots"] is None for f in fr if f["t"] >= lost["t"])
    assert fr[-1]["height_m"] > lost["height_m"]                             # go-around flown


def test_no_guidance_is_extrapolated():
    for f in fly_replay(RWY, faults=(Fault("dropout", 60, 80),), seed=10):
        if f["state"] in ("LOST", "INVALID"):
            assert f["lat_dots"] is None and f["hdg_rel_deg"] is None and f["lat_word"] == ""


def test_old_plot_does_not_move_the_filter_back():
    lg = CueLogic(RWY)
    _state_after(lg, _plots(6))
    before = lg.f.t
    lg.step(6.0, Plot(2.0, 8860.0, 300.0, 300.0))
    assert lg.f.t == before and lg.f.y == pytest.approx(0.0, abs=1e-9)


def test_non_finite_plot_is_rejected():
    lg = CueLogic(RWY)
    _state_after(lg, _plots(6))
    lg.step(6.0, Plot(6.0, 8580.0, float("nan"), 0.0))
    fr = lg.step(7.0, Plot(7.0, 8510.0, 0.0, float("inf")))
    assert fr["state"] == "INVALID"


def test_outside_limits_latches():
    lg = CueLogic(RWY)
    fr = _state_after(lg, _plots(6, y=900.0))
    assert fr["state"] == "OUTSIDE LIMITS"
    assert lg.step(7.0, Plot(7.0, 8510.0, 0.0, 0.0))["state"] == "OUTSIDE LIMITS"


def test_end_states_are_terminal_for_every_seed():
    for s in range(10):
        fr = fly_replay(RWY, faults=(Fault("dropout", 50, 60),), seed=s)
        states = [f["state"] for f in fr]
        first = next(i for i, x in enumerate(states) if x in END_STATES)
        assert len(set(states[first:])) == 1


def test_replay_is_repeatable():
    assert fly_replay(RWY, seed=11) == fly_replay(RWY, seed=11)
    assert cue_changes(fly_replay(RWY, seed=11)) > 0
