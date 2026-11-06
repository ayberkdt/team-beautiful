"""Cue intensity: silent on the path, one table of levels, few calls, never above the sound ceiling."""
import pytest

from aerokit.atc.cue_intensity import VOICE_TEXT, CueIntensity, IntensityConfig, level_for, voice_level_dba

C = IntensityConfig()
R = 6000.0        # range [m]: 1 alert dot is about 37 m vertical, 131 m lateral
H = 900.0         # height [ft]


def run(ci, seq, t0=0.0, state="VALID", rng=R, h=H):
    return [ci.step(t0 + i, state, a, b, rng, h) for i, (a, b) in enumerate(seq)]


def lost(ci, n):
    return [ci.step(float(i), "RADAR LOST", None, None, None, None, call="radar_lost") for i in range(n)]


def test_the_table():
    assert level_for(0.9, C) == 0 and level_for(1.0, C) == 2 and level_for(1.3, C) == 3


def test_silent_and_quiet_on_the_path():
    out = run(CueIntensity(), [(5.0, -3.0)] * 60)
    assert all(f["level"] == 0 and f["voice"] is None and f["visual"] == "none" for f in out)


def test_status_words_only():
    assert not any(w in v.upper() for v in VOICE_TEXT.values() for w in ("TURN", "DESCEND", "CLIMB", "ON PATH", "GOOD"))


def test_missed_approach_is_conditional_with_the_reason_first():
    for k in ("too_low", "too_high", "too_left", "too_right", "radar_lost", "radar_suspect", "no_glidepath"):
        reason, condition = VOICE_TEXT[k].split(". ", 1)
        assert reason and condition == "If runway or approach lights not in sight, execute missed approach."


def test_holding_deviation_is_said_once_not_nagged():
    out = run(CueIntensity(), [(0.0, -40.0)] * 120)
    assert sum(1 for f in out if f["voice"]) == 1


def test_repeat_needs_twenty_percent_growth():
    calls = [f for f in run(CueIntensity(), [(0.0, -40.0)] * 15 + [(0.0, -42.0)] * 15) if f["voice"]]
    assert len(calls) == 1
    more = [f for f in run(CueIntensity(), [(0.0, -40.0)] * 15 + [(0.0, -49.0)] * 15) if f["voice"]]
    assert len(more) == 2


def test_time_filter_ignores_a_one_frame_spike():
    out = run(CueIntensity(), [(0.0, 0.0)] * 5 + [(0.0, -60.0)] + [(0.0, 0.0)] * 5)
    assert all(f["level"] == 0 and f["voice"] is None for f in out)


def test_what_the_radar_cannot_resolve_is_not_alerted():
    ci = CueIntensity()
    out = [ci.step(float(i), "VALID", 0.0, -45.0, R, H, resolve_m=(0.0, 20.0)) for i in range(10)]
    assert all(f["level"] == 0 for f in out)


def test_no_advise_voice_near_the_ground_but_caution_stays():
    assert not any(f["voice"] for f in run(CueIntensity(), [(0.0, -20.0)] * 20, rng=1500.0, h=250.0))
    assert any(f["voice"] == "well_below" for f in run(CueIntensity(), [(0.0, -30.0)] * 20, rng=1500.0, h=250.0))


def test_data_fault_called_once_with_no_restored_call():
    ci = CueIntensity()
    out = run(ci, [(None, None)] * 8, state="DELAYED") + run(ci, [(0.0, 0.0)] * 8, t0=8.0)
    assert [f["voice"] for f in out if f["voice"]] == ["delayed"]


def test_warning_repeats_twice_then_stops():
    out = lost(CueIntensity(), 30)
    assert [i for i, f in enumerate(out) if f["voice"]] == [0, 8]
    assert out[0]["tone_first"] and out[0]["level"] == 4


def test_blink_stops_after_ten_seconds():
    out = lost(CueIntensity(), 15)
    assert out[0]["blink"] and not out[12]["blink"]


def test_decision_height_called_once_then_silence():
    ci = CueIntensity()
    a = ci.step(0.0, "ADVISORY", 0.0, -80.0, 900.0, 150.0)
    b = ci.step(1.0, "ADVISORY", 0.0, -80.0, 900.0, 150.0)
    assert a["voice"] == "at_dh" and b["voice"] is None and b["level"] == 0


def test_sound_level_is_capped():
    assert voice_level_dba(0, C) is None
    assert voice_level_dba(2, C) == pytest.approx(88.0)
    assert voice_level_dba(4, IntensityConfig(noise_dba=95.0)) == 90.0
