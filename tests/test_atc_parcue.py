"""Automated PAR cue: returns to the path, stays quiet on it, and bad data never produces guidance."""
import math

import numpy as np
import pytest

from aerokit.approach import Runway
from aerokit.atc.cue_intensity import VOICE_TEXT
from aerokit.atc.parcue import (END_STATES, AxisKalman, CueConfig, CueLogic, Fault, PilotModel, RadarPlot, ReplayConfig,
                                cue_changes, fly_replay, replay_track)
from aerokit.atc.parflight import AIRCRAFT, dryden_sigmas, wind_at
from aerokit.atc.parradar import NM, ParRadar, RadarConfig, error_limits_m

RWY = Runway(51.0, 4.0, 10.0, 250.0)
SEEDS = range(30)


def _plots(n, y=0.0, z=0.0, r0=9000.0, gs=67.0, t0=0.0):
    return [RadarPlot(t0 + i, r0 - gs * (t0 + i), y, z) for i in range(n)]


def _feed(logic, plots):
    fr = None
    for p in plots:
        fr = logic.step(p.t, p)
    return fr


# --- radar model -----------------------------------------------------------------------------------------------------
def test_annex10_limits():
    az, el, r = error_limits_m(10_000.0, 9_000.0, 100.0, 50.0)
    assert az == pytest.approx(0.006 * 10_000 + 10.0)
    assert el == pytest.approx(0.004 * 10_000 + 5.0)
    assert r == pytest.approx(30.0 + 270.0)                 # 30 m plus 3 %, not "or"
    assert error_limits_m(100.0, 0.0)[:2] == (9.0, 6.0)      # the floors


def test_radar_error_uses_the_antenna_distance():
    """Near touchdown the error is larger than a range-to-touchdown model gives, because the antenna is set back."""
    rng = np.random.default_rng(0)
    radar = ParRadar(RWY, RadarConfig(detection=1.0, multipath_deg=0.0), rng)
    errs = []
    for k in range(4000):
        p = radar.measure(float(k), 1852.0, 0.0, RWY.tch + 1852.0 * math.tan(math.radians(3.0)))
        errs.append(p.az_dev_m)
    sd = float(np.std(errs))
    r_ant = 1852.0 - RWY.gpip + 915.0
    assert sd == pytest.approx(0.5 * 0.006 * r_ant, rel=0.15)
    assert sd > 0.5 * max(0.006 * 1852.0, 9.0) * 1.2


def test_radar_loses_plots_at_the_stated_rate():
    radar = ParRadar(RWY, RadarConfig(detection=0.9), np.random.default_rng(1))
    miss = sum(radar.measure(float(k), 5000.0, 0.0, 280.0) is None for k in range(3000))
    assert 0.07 < miss / 3000 < 0.13


# --- flight model ----------------------------------------------------------------------------------------------------
def test_wind_grows_with_height_as_the_log_law():
    assert wind_at(20 * 0.3048, 10.0) == pytest.approx(10.0)
    assert wind_at(1000 * 0.3048, 10.0) == pytest.approx(18.0, abs=0.1)        # 1.8 x W20 in R5


def test_dryden_light_at_300_ft():
    s_u, s_w, _, l_w = dryden_sigmas(300 * 0.3048, 15.0)
    assert s_u == pytest.approx(1.09, abs=0.02)
    assert s_w == pytest.approx(0.77, abs=0.01) and l_w == pytest.approx(300 * 0.3048)


def test_turn_rate_is_limited():
    fr = fly_replay(RWY, rc=ReplayConfig(start_offset_m=250.0), seed=3)
    hdg = [f["hdg_rel_deg"] for f in fr if f["hdg_rel_deg"] is not None]
    assert max(abs(h) for h in hdg) <= CueConfig().cap_far_deg + CueConfig().max_trim_deg


# --- filter ----------------------------------------------------------------------------------------------------------
def test_kalman_tracks_a_constant_rate():
    k = AxisKalman(0.0, 0.0, 100.0, 0.1, 0.0)
    for t in range(1, 40):
        k.update(3.0 * t, 25.0, float(t))
    assert k.x[1] == pytest.approx(3.0, abs=0.2)


def test_gate_recovers_after_noise_rejections():
    lg = CueLogic(RWY)
    _feed(lg, _plots(8))
    r0 = 9000.0 - 67.0 * 8
    lg.step(8.0, RadarPlot(8.0, r0, 900.0, 0.0))
    fr = _feed(lg, _plots(8, t0=9.0))
    assert fr["state"] == "VALID"


# --- closed loop -----------------------------------------------------------------------------------------------------
def test_clean_runs_reach_minimums_near_the_path():
    ends = [fly_replay(RWY, seed=s)[-1] for s in SEEDS]
    gate = [e for e in ends if e["state"] == "MINIMUMS"]
    assert len(gate) >= 0.95 * len(ends)
    assert np.percentile([abs(e["y_m"]) for e in gate], 95) < 45
    assert np.percentile([abs(e["z_dev_m"]) for e in gate], 95) < 20


def test_without_the_cue_the_aircraft_does_not_get_there():
    assert all(fly_replay(RWY, rc=ReplayConfig(crosswind_ms=3.0), pilot=PilotModel(follows_cue=False), seed=s)[-1]["state"]
               != "MINIMUMS" for s in range(5))


def test_heading_target_points_back_to_the_path():
    fr = fly_replay(RWY, seed=1)
    assert next(f for f in fr if f["hdg_new"])["hdg_rel_deg"] < 0             # right of the centreline: heading left


def test_guidance_changes_as_the_aircraft_returns():
    fr = fly_replay(RWY, seed=1)
    valid = [f for f in fr if f["state"] == "VALID"]
    assert abs(valid[0]["y_m"]) > 100 and abs(valid[-1]["y_m"]) < 60
    assert valid[5]["lat_word"].startswith("SLIGHTLY") and "ON COURSE" in {f["lat_word"] for f in valid}
    assert abs(valid[-1]["hdg_rel_deg"]) < abs(min(f["hdg_rel_deg"] for f in valid))


def test_crosswind_is_handled_by_the_trim():
    ends = [fly_replay(RWY, rc=ReplayConfig(crosswind_ms=5.0), seed=s)[-1] for s in range(10)]
    assert sum(e["state"] == "MINIMUMS" for e in ends) >= 9


def test_other_aircraft_run():
    assert fly_replay(RWY, rc=ReplayConfig(aircraft=AIRCRAFT["F-16"]), seed=2)[-1]["state"] == "MINIMUMS"


def test_target_changes_are_rate_limited():
    ts = [f["t"] for f in fly_replay(RWY, seed=4) if f["hdg_new"]]
    assert all(b - a >= CueConfig().update_s for a, b in zip(ts, ts[1:]))
    assert cue_changes(fly_replay(RWY, seed=4)) > 0


def test_no_imperative_words_on_the_display():
    words = {f[k] for s in range(5) for f in fly_replay(RWY, seed=s) for k in ("lat_word", "vert_word")}
    assert not any(w.startswith(("TURN", "DESCEND", "CLIMB", "EASE")) for w in words)


def test_voice_is_scarce_and_never_on_the_path():
    runs = [fly_replay(RWY, seed=s) for s in SEEDS]
    assert np.median([sum(1 for f in r if f["voice"]) for r in runs]) <= 5
    for r in runs:
        for f in r:
            if f["voice"] and f["state"] == "VALID":
                assert not (f["lat_word"] == "ON COURSE" and f["vert_word"] == "ON GLIDE PATH" and f["voice"] != "coming_down")


def test_every_voice_key_has_text():
    keys = {f["voice"] for s in range(5) for f in fly_replay(RWY, seed=s) if f["voice"]}
    assert keys <= set(VOICE_TEXT)


def test_heartbeat_moves_while_silent():
    fr = fly_replay(RWY, seed=1)
    hb = [f["heartbeat"] for f in fr]
    assert hb[-1] > 0.8 * len(hb) and all(b >= a for a, b in zip(hb, hb[1:]))


# --- faults ----------------------------------------------------------------------------------------------------------
def test_delay_above_three_seconds_is_told_with_no_new_target():
    fr = fly_replay(RWY, faults=(Fault("delay", 60, 75, 4.0),), seed=5)
    d = [f for f in fr if f["state"] == "DELAYED"]
    assert d and all(f["age_s"] > CueConfig().track_lost_s for f in d)
    assert all(f["hdg_new"] == 0 and f["rod_new"] == 0 and f["hdg_rel_deg"] is None for f in d)
    assert all(f["lat_dots"] is not None for f in d)


def test_elevation_failure_leaves_azimuth_working():
    fr = fly_replay(RWY, faults=(Fault("el_invalid", 60, 63),), seed=6)
    bad = [f for f in fr if f["state"] == "INVALID"]
    assert bad and all(f["vert_dots"] is None and f["lat_dots"] is not None for f in bad)


def test_jump_is_rejected_not_flown():
    fr = fly_replay(RWY, faults=(Fault("jump", 60, 63, 400.0),), seed=7)
    assert any(f["state"] == "INVALID" for f in fr)
    assert max(abs(f["y_m"]) for f in fr if f["t"] > 55) < 100


def test_persistent_bad_data_ends_in_lost():
    fr = fly_replay(RWY, faults=(Fault("jump", 60, 300, 400.0),), seed=8)
    assert fr[-1]["state"] == "LOST"


def test_radar_stop_lost_after_five_seconds_and_latches():
    fr = fly_replay(RWY, faults=(Fault("dropout", 60, 66),), seed=9)
    lost = next(f for f in fr if f["state"] == "LOST")
    assert 64 <= lost["t"] <= 67
    assert any(f["state"] == "DELAYED" and f["t"] < lost["t"] for f in fr)   # told at 3 s, before LOST
    assert all(f["state"] == "LOST" and f["lat_dots"] is None for f in fr if f["t"] >= lost["t"])
    assert fr[-1]["height_m"] > lost["height_m"]
    assert lost["voice"] == "lost" and "not visual" in VOICE_TEXT["lost"]


def test_no_guidance_is_extrapolated():
    for f in fly_replay(RWY, faults=(Fault("dropout", 60, 90),), seed=10):
        if f["state"] == "LOST":
            assert f["lat_dots"] is None and f["hdg_rel_deg"] is None and f["lat_word"] == ""


def test_old_plot_does_not_move_the_filter_back():
    lg = CueLogic(RWY)
    _feed(lg, _plots(6))
    y0 = float(lg.ky.x[0])
    lg.step(6.0, RadarPlot(2.0, 8866.0, 300.0, 300.0))
    assert float(lg.ky.x[0]) == y0


def test_non_finite_plot_is_rejected():
    lg = CueLogic(RWY)
    _feed(lg, _plots(6))
    lg.step(6.0, RadarPlot(6.0, 8598.0, float("nan"), 0.0))
    assert lg.step(7.0, RadarPlot(7.0, 8531.0, float("inf"), 0.0))["state"] == "INVALID"


def test_outside_limits_needs_to_stay_outside_and_latches():
    lg = CueLogic(RWY)
    a = _feed(lg, _plots(5, y=500.0))
    assert a["state"] == "VALID"
    b = _feed(lg, _plots(4, y=500.0, t0=5.0))
    assert b["state"] == "OUTSIDE LIMITS"
    assert lg.step(9.0, RadarPlot(9.0, 8397.0, 0.0, 0.0))["state"] == "OUTSIDE LIMITS"


def test_decision_height_comes_from_the_pilot():
    a = fly_replay(RWY, cfg=CueConfig(dh_ft=300.0), seed=1)
    b = fly_replay(RWY, cfg=CueConfig(dh_ft=200.0), seed=1)
    assert a[-1]["state"] == b[-1]["state"] == "MINIMUMS" and a[-1]["x_m"] > b[-1]["x_m"]


def test_clearance_gate_and_gear_prompt():
    fr = fly_replay(RWY, clearance=False, seed=1)
    assert any(f["note"] == "CHECK GEAR" for f in fr) and any(f["voice"] == "no_clearance" for f in fr)
    assert any(f["note"] == "CLEARANCE NOT CONFIRMED" for f in fr)
    assert not any(f["voice"] == "no_clearance" for f in fly_replay(RWY, seed=1))


def test_end_states_are_terminal():
    for s in range(6):
        states = [f["state"] for f in fly_replay(RWY, faults=(Fault("dropout", 50, 60),), seed=s)]
        first = next(i for i, x in enumerate(states) if x in END_STATES)
        assert len(set(states[first:])) == 1


def test_replay_is_repeatable():
    assert fly_replay(RWY, seed=11) == fly_replay(RWY, seed=11)


# --- recorded track --------------------------------------------------------------------------------------------------
def test_open_loop_track_on_the_path_is_silent():
    t = np.arange(0.0, 100.0)
    x = 8000.0 - 67.0 * t
    z = RWY.tch + x * math.tan(math.radians(3.0))
    fr = replay_track(RWY, t, x, np.zeros_like(t), z, noise=False)
    assert all(f["level"] == 0 and not f["voice"] for f in fr)


def test_fast_closure_is_called_on_a_steep_track_below_the_gate():
    """Above the path but sinking at twice the rate: position alone says nothing until the path is crossed."""
    t = np.arange(0.0, 45.0)
    x = 4000.0 - 75.0 * t
    gp = RWY.tch + x * math.tan(math.radians(3.0))
    z = gp + 45.0 - 3.6 * t
    fr = replay_track(RWY, t, x, np.zeros_like(t), z, cfg=CueConfig(latch_limits=False, dh_ft=1.0), noise=False)
    first = next(f for f in fr if f["closing_fast"])
    assert first["z_dev_m"] > -60 and any(f["voice"] == "coming_down" for f in fr)
