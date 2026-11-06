"""Automated PAR cue: returns to the path, stays quiet on it, and bad data never produces guidance."""
import math

import numpy as np
import pytest

from aerokit.approach import Runway
from aerokit.atc.cue_intensity import VOICE_TEXT
from aerokit.atc.parcue import (END_STATES, MISSED_STATES, AxisKalman, CueConfig, CueLogic, Fault, PilotModel, RadarPlot,
                                ReplayConfig, cue_changes, dh_frame, fly_replay, replay_track)
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
    gate = [g for g in (dh_frame(fly_replay(RWY, seed=s)) for s in SEEDS) if g is not None]
    assert len(gate) >= 0.95 * len(SEEDS)
    assert np.percentile([abs(e["y_m"]) for e in gate], 95) < 45
    assert np.percentile([abs(e["z_dev_m"]) for e in gate], 95) < 20


def test_without_the_cue_the_aircraft_does_not_get_there():
    assert all(dh_frame(fly_replay(RWY, rc=ReplayConfig(crosswind_ms=3.0), pilot=PilotModel(follows_cue=False), seed=s))
               is None for s in range(5))


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
    assert sum(dh_frame(fly_replay(RWY, rc=ReplayConfig(crosswind_ms=5.0), seed=s)) is not None for s in range(10)) >= 9


def test_other_aircraft_run():
    assert sum(dh_frame(fly_replay(RWY, rc=ReplayConfig(aircraft=AIRCRAFT[a]), seed=2)) is not None
               for a in AIRCRAFT) >= 2


def test_target_changes_are_rate_limited():
    ts = [f["t"] for f in fly_replay(RWY, seed=4) if f["hdg_new"]]
    assert all(b - a >= CueConfig().update_s for a, b in zip(ts, ts[1:]))
    assert cue_changes(fly_replay(RWY, seed=4)) > 0


def test_no_imperative_words_on_the_display():
    words = {f[k] for s in range(5) for f in fly_replay(RWY, seed=s) for k in ("lat_word", "vert_word")}
    assert not any(w.startswith(("TURN", "DESCEND", "CLIMB", "EASE")) for w in words)
    assert {"ON COURSE", "ON GLIDEPATH"} <= words
    assert any("OF COURSE" in w and w.startswith(("SLIGHTLY", "WELL")) for w in words)


def test_voice_is_scarce_and_never_on_the_path():
    runs = [fly_replay(RWY, seed=s) for s in SEEDS]
    assert np.median([sum(1 for f in r if f["voice"]) for r in runs]) <= 5
    for r in runs:
        for f in r:
            if f["voice"] and f["state"] == "VALID":
                assert not (f["lat_word"] == "ON COURSE" and f["vert_word"] == "ON GLIDEPATH" and f["voice"] != "coming_down")


def test_every_voice_key_has_text():
    keys = {f["voice"] for s in range(5) for f in fly_replay(RWY, seed=s) if f["voice"]}
    assert keys <= set(VOICE_TEXT)


def test_heartbeat_moves_while_silent():
    fr = fly_replay(RWY, seed=1)
    hb = [f["heartbeat"] for f in fr]
    assert hb[-1] > 0.8 * len(hb) and all(b >= a for a, b in zip(hb, hb[1:]))


# --- faults ----------------------------------------------------------------------------------------------------------
def test_delay_above_three_seconds_is_told_with_no_new_target():
    fr = fly_replay(RWY, faults=(Fault("delay", 12, 22, 4.0),), seed=5)        # outside 4 NM a fault is not final
    d = [f for f in fr if f["state"] == "DELAYED"]
    assert d and all(f["age_s"] > CueConfig().track_lost_s for f in d)
    assert all(f["hdg_new"] == 0 and f["rod_new"] == 0 and f["hdg_rel_deg"] is None for f in d)
    assert all(f["lat_dots"] is not None for f in d)


def test_elevation_failure_ends_guidance_at_once():
    """JO 7110.65 5-12-10: discontinue PAR instructions; no 5 s wait."""
    fr = fly_replay(RWY, faults=(Fault("el_invalid", 60, 1e9),), seed=6)
    first = next(f for f in fr if f["state"] == "ELEVATION FAILED")
    assert first["t"] <= 62 and first["voice"] == "no_glidepath" and first["missed_approach"]
    assert all(f["lat_dots"] is None and f["vert_dots"] is None for f in fr if f["t"] >= first["t"])


def test_one_bad_elevation_flag_is_not_a_failure():
    fr = fly_replay(RWY, faults=(Fault("el_invalid", 60, 61),), seed=6)
    assert not any(f["state"] == "ELEVATION FAILED" for f in fr)


def test_jump_is_rejected_not_flown():
    fr = fly_replay(RWY, faults=(Fault("jump", 60, 63, 400.0),), seed=7)
    assert any(f["state"] == "INVALID" for f in fr) and dh_frame(fr) is not None
    assert max(abs(f["y_m"]) for f in fr if f["t"] > 55) < 100


def test_persistent_bad_data_is_a_suspected_malfunction():
    fr = fly_replay(RWY, faults=(Fault("jump", 70, 300, 400.0),), seed=8)
    assert fr[-1]["state"] == "RADAR SUSPECT"
    assert any(f["voice"] == "radar_suspect" for f in fr)


def test_inside_4_nm_a_lost_target_is_final_after_3_s_and_latches():
    """RA 3291 paras 5, 7b; call from JO 7110.65 5-10-14c. Radar back later does not restart the approach."""
    fr = fly_replay(RWY, faults=(Fault("dropout", 70, 76),), seed=9)
    lost = next(f for f in fr if f["state"] == "RADAR LOST")
    assert lost["x_m"] < 4 * NM and 72 <= lost["t"] <= 75
    assert all(f["state"] == "RADAR LOST" and f["lat_dots"] is None for f in fr if f["t"] >= lost["t"])
    assert fr[-1]["height_m"] > lost["height_m"]
    assert lost["voice"] == "radar_lost" and "If runway or approach lights not in sight" in VOICE_TEXT["radar_lost"]


def test_outside_4_nm_a_short_loss_can_recover():
    fr = fly_replay(RWY, faults=(Fault("dropout", 12, 16),), seed=9)
    assert any(f["state"] == "DELAYED" for f in fr) and not any(f["state"] == "RADAR LOST" for f in fr)


def test_missed_approach_call_gives_the_side():
    assert fly_replay(RWY, rc=ReplayConfig(start_above_m=-110.0), seed=1)[-1]["state"] == "OUTSIDE LIMITS"
    assert any(f["voice"] == "too_low" for f in fly_replay(RWY, rc=ReplayConfig(start_above_m=-110.0), seed=1))
    assert any(f["voice"] == "too_right" for f in fly_replay(RWY, rc=ReplayConfig(start_offset_m=420.0), seed=1))


def test_after_dh_no_missed_approach_call_is_made():
    """5-10-14: conditions a, b, c do not apply after DH."""
    r = fly_replay(RWY, seed=1)
    t_dh = dh_frame(r)["t"]
    fr = fly_replay(RWY, faults=(Fault("dropout", t_dh + 2, 1e9),), seed=1)
    assert dh_frame(fr) is not None and not any(f["state"] in MISSED_STATES for f in fr)
    assert fr[-1]["state"] == "OVER THRESHOLD"


def test_position_stays_on_as_advisory_until_the_threshold():
    """5-12-7: guidance to the threshold, advisory only below DH; 5-12-8a3 ends it."""
    fr = fly_replay(RWY, seed=1)
    below = [f for f in fr if f["state"] == "ADVISORY"]
    assert below and all(f["note"] == "ADVISORY ONLY" and f["lat_dots"] is not None for f in below)
    assert all(f["hdg_rel_deg"] is None for f in below) and fr[-1]["state"] == "OVER THRESHOLD"
    assert [f["voice"] for f in fr if f["voice"]].count("at_dh") == 1


def test_link_loss_is_lost_comm_not_a_missed_approach():
    """5-10-4: 5 s on PAR final, then the instruction given before final."""
    fr = fly_replay(RWY, faults=(Fault("link", 70, 1e9),), seed=2)
    f = next(q for q in fr if q["state"] == "LINK LOST")
    assert 75 <= f["t"] <= 77 and f["voice"] == "link_lost" and not f["missed_approach"]
    assert "lost communications" in VOICE_TEXT["link_lost"]


def test_pilot_proceeding_visually_ends_guidance():
    lg = CueLogic(RWY)
    _feed(lg, _plots(6))
    fr = lg.step(6.0, RadarPlot(6.0, 8598.0, 0.0, 0.0), pilot_visual=True)
    assert fr["state"] == "VISUAL" and fr["voice"] is None


def test_tower_break_is_unconditional():
    lg = CueLogic(RWY)
    _feed(lg, _plots(6))
    fr = lg.step(6.0, RadarPlot(6.0, 8598.0, 0.0, 0.0), tower_break="traffic on runway")
    assert fr["state"] == "NO CLEARANCE" and fr["voice"] == "no_clearance" and "If" not in VOICE_TEXT["no_clearance"]


def test_missed_approach_procedure_is_shown():
    fr = fly_replay(RWY, cfg=CueConfig(missed_approach="CLIMB 3000 RUNWAY HEADING"), faults=(Fault("dropout", 70, 1e9),), seed=1)
    assert any(f["note"] == "CLIMB 3000 RUNWAY HEADING" for f in fr)


def test_no_guidance_is_extrapolated():
    for f in fly_replay(RWY, faults=(Fault("dropout", 60, 90),), seed=10):
        if f["state"] in MISSED_STATES:
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
    assert lg.step(7.0, RadarPlot(7.0, 8531.0, float("inf"), 0.0))["state"] == "INVALID"     # 2 bad plots


def test_outside_limits_needs_to_stay_outside_and_latches():
    lg = CueLogic(RWY)
    a = _feed(lg, _plots(4, y=450.0))
    assert a["state"] == "VALID"
    b = _feed(lg, _plots(6, y=450.0, t0=4.0))
    assert b["state"] == "OUTSIDE LIMITS" and b["missed_approach"]
    assert lg.step(10.0, RadarPlot(10.0, 8330.0, 0.0, 0.0))["state"] == "OUTSIDE LIMITS"


def test_decision_height_comes_from_the_pilot():
    a = dh_frame(fly_replay(RWY, cfg=CueConfig(dh_ft=300.0), seed=1))
    b = dh_frame(fly_replay(RWY, cfg=CueConfig(dh_ft=200.0), seed=1))
    assert a["x_m"] > b["x_m"]


def test_clearance_gate_and_gear_prompt():
    fr = fly_replay(RWY, clearance=False, seed=1)
    stop = next(f for f in fr if f["state"] == "NO CLEARANCE")
    assert stop["x_m"] <= 2.2 * NM and stop["voice"] == "no_clearance" and stop["missed_approach"]
    ok = fly_replay(RWY, seed=1)
    assert any(f["note"] == "CHECK GEAR" for f in ok) and not any(f["state"] == "NO CLEARANCE" for f in ok)


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
    assert all(f["level"] == 0 for f in fr) and not any(f["voice"] and f["voice"] != "at_dh" for f in fr)


def test_fast_closure_is_called_on_a_steep_track_below_the_gate():
    """Above the path but sinking at twice the rate: position alone says nothing until the path is crossed."""
    t = np.arange(0.0, 45.0)
    x = 4000.0 - 75.0 * t
    gp = RWY.tch + x * math.tan(math.radians(3.0))
    z = gp + 45.0 - 3.6 * t
    fr = replay_track(RWY, t, x, np.zeros_like(t), z, cfg=CueConfig(latch_limits=False, dh_ft=1.0), noise=False)
    first = next(f for f in fr if f["closing_fast"])
    assert first["z_dev_m"] > -60 and any(f["voice"] == "coming_down" for f in fr)
