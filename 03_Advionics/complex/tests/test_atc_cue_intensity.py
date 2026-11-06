"""Cue intensity: silent on the path, quiet while closing, few calls, never above the sound ceiling."""
import pytest

from aerokit.atc.cue_intensity import VOICE_TEXT, CueIntensity, IntensityConfig, intensity_score, voice_level_dba

C = IntensityConfig()
R = 6000.0        # range [m]: 1 alert dot is about 37 m vertical, 131 m lateral
H = 900.0         # height [ft], below the gate


def run(ci, seq, t0=0.0, state="VALID", rng=R, h=H):
    """seq: (lat_m, vert_m) per second. Returns the frames."""
    return [ci.step(t0 + i, state, a, b, rng, h) for i, (a, b) in enumerate(seq)]


def test_silent_and_quiet_on_the_path():
    out = run(CueIntensity(), [(5.0, -3.0)] * 60)
    assert all(f["level"] == 0 and f["voice"] is None and f["visual"] == "none" for f in out)


def test_anchors_one_dot_and_one_point_three_dots():
    assert intensity_score(1.0, H, 0.0, C) == pytest.approx(1 / 3)
    assert C.l2 <= intensity_score(1.0, H, 0.0, C) < C.l3            # ALAR limit -> L2
    assert intensity_score(1.3, H, 0.0, C) >= C.l3                  # Mode 5 soft -> L3
    assert intensity_score(2.0, H, 0.0, C) == 1.0


def test_above_the_gate_weighs_less():
    assert intensity_score(1.0, 2000.0, 0.0, C) < intensity_score(1.0, 900.0, 0.0, C)


def test_below_path_weighs_more_than_above_path():
    ci = CueIntensity()
    assert ci.alert_dots(0.0, -30.0, R)[0] > ci.alert_dots(0.0, 30.0, R)[0]


def test_status_words_only():
    assert not any(w in v.upper() for v in VOICE_TEXT.values() for w in ("TURN", "DESCEND", "CLIMB", "ON PATH", "GOOD"))
    instructions = {k for k, v in VOICE_TEXT.items() if "execute" in v.lower() or "apply" in v.lower()}
    assert instructions == {"too_low", "too_high", "too_left", "too_right", "radar_lost", "radar_suspect", "no_glidepath",
                            "no_clearance", "link_lost"}


def test_missed_approach_is_conditional_with_the_reason_first():
    for k in ("too_low", "too_high", "too_left", "too_right", "radar_lost", "radar_suspect", "no_glidepath"):
        reason, condition = VOICE_TEXT[k].split(". ", 1)
        assert reason and condition == "If runway or approach lights not in sight, execute missed approach."
    assert "If" not in VOICE_TEXT["no_clearance"]       # 5-10-14d and 5-10-13: not conditional


def test_closing_deviation_stays_quieter_than_holding():
    hold = run(CueIntensity(), [(0.0, -38.0)] * 20)                  # about 1 dot, holding
    close = run(CueIntensity(), [(0.0, -46.0 + 1.0 * i) for i in range(20)])     # same place, closing
    assert sum(1 for f in hold if f["voice"]) >= 1
    assert sum(1 for f in close if f["voice"]) <= sum(1 for f in hold if f["voice"])
    assert any(f["trend"] == "correcting" for f in close)


def test_holding_deviation_is_said_once_not_nagged():
    out = run(CueIntensity(), [(0.0, -38.0)] * 120)
    assert sum(1 for f in out if f["voice"]) == 1


def test_repeat_needs_twenty_percent_growth():
    seq = [(0.0, -38.0)] * 15 + [(0.0, -40.0)] * 15 + [(0.0, -47.0)] * 15
    calls = [f for f in run(CueIntensity(), seq) if f["voice"]]
    assert len(calls) <= 2


def test_time_filter_ignores_a_one_frame_spike():
    out = run(CueIntensity(), [(0.0, 0.0)] * 5 + [(0.0, -60.0)] + [(0.0, 0.0)] * 5)
    assert all(f["level"] == 0 and f["voice"] is None for f in out)


def test_no_l2_voice_near_the_ground_but_l3_stays():
    assert not any(f["voice"] for f in run(CueIntensity(), [(0.0, -22.0)] * 20, rng=1500.0, h=250.0))
    assert any(f["voice"] == "well_below" for f in run(CueIntensity(), [(0.0, -30.0)] * 20, rng=1500.0, h=250.0))


def test_cue_quiet_silences_guidance_and_not_the_warning():
    ci = CueIntensity(quiet=True)
    assert not any(f["voice"] for f in run(ci, [(0.0, -60.0)] * 20))
    assert ci.step(30.0, "RADAR LOST", None, None, None, None, call="radar_lost")["voice"] == "radar_lost"


def test_data_fault_called_once_with_no_restored_call():
    ci = CueIntensity()
    out = run(ci, [(None, None)] * 8, state="DELAYED") + run(ci, [(0.0, 0.0)] * 8, t0=8.0)
    assert [f["voice"] for f in out if f["voice"]] == ["delayed"]


def lost(ci, n):
    return [ci.step(float(i), "RADAR LOST", None, None, None, None, call="radar_lost") for i in range(n)]


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


def test_sound_levels_are_capped():
    assert voice_level_dba(1, C) is None
    assert voice_level_dba(2, C) == pytest.approx(83.0)
    assert voice_level_dba(4, IntensityConfig(noise_dba=88.0)) == 90.0
    assert all(voice_level_dba(k, IntensityConfig(noise_dba=95.0)) <= 90.0 for k in (2, 3, 4))
