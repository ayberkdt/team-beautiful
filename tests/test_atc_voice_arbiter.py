"""The cue gives way: aircraft alerts first, one voice at a time, no repeat of what the aircraft just said."""
import pytest

from aerokit.approach import Runway
from aerokit.atc.parcue import Fault, ReplayConfig, fly_replay
from aerokit.atc.voice_arbiter import AIRCRAFT_ALERTS, ArbiterConfig, VoiceArbiter

RWY = Runway(51.0, 4.0, 10.0, 250.0)


def test_priority_table_is_the_tso_order():
    order = sorted((v[0], k) for k, v in AIRCRAFT_ALERTS.items() if v[0] <= 23)
    assert [k for _, k in order[:4]] == ["REACTIVE WINDSHEAR", "SINK RATE PULL UP", "CLOSURE PULL UP", "TERRAIN"]
    assert AIRCRAFT_ALERTS["MINIMUMS"][0] < AIRCRAFT_ALERTS["GLIDESLOPE"][0] == 19


@pytest.mark.parametrize("alert", ["CLOSURE PULL UP", "TERRAIN", "REACTIVE WINDSHEAR", "TCAS RA"])
def test_routine_call_is_dropped_behind_a_warning(alert):
    a = VoiceArbiter().step(0.0, "well_below", 3, [alert])
    assert a["voice"] is None and "behind" in a["dropped"]


@pytest.mark.parametrize("alert", ["CLOSURE PULL UP", "SINK RATE", "TCAS RA"])
def test_level_4_never_talks_over_an_aircraft_alert_but_waits(alert):
    v = VoiceArbiter()
    assert v.step(0.0, "radar_lost", 4, [alert])["held"]
    assert v.step(1.0, None, 0, [alert])["voice"] is None
    assert v.step(2.0, None, 0, [])["voice"] == "radar_lost"


def test_held_warning_goes_stale():
    v = VoiceArbiter(ArbiterConfig(hold_warning_s=5.0))
    v.step(0.0, "radar_lost", 4, ["TERRAIN"])
    assert v.step(6.0, None, 0, ["TERRAIN"])["dropped"] == "stale: radar_lost"
    assert v.step(7.0, None, 0, [])["voice"] is None


@pytest.mark.parametrize("alert,key", [("GLIDESLOPE", "well_below"), ("SINK RATE", "coming_down"), ("MINIMUMS", "at_dh")])
def test_same_meaning_is_not_repeated(alert, key):
    v = VoiceArbiter()
    v.step(0.0, None, 0, [alert])
    a = v.step(5.0, key, 3)
    assert a["voice"] is None and "same as aircraft" in a["dropped"]
    assert VoiceArbiter().step(5.0, key, 3)["voice"] == key


def test_radio_holds_routine_not_warning():
    v = VoiceArbiter()
    assert v.step(0.0, "slightly_left", 2, radio=True)["held"]
    assert v.step(1.0, None, 0, radio=False)["voice"] == "slightly_left"
    assert VoiceArbiter().step(0.0, "radar_lost", 4, radio=True)["voice"] == "radar_lost"


def test_routine_call_held_too_long_is_dropped():
    v = VoiceArbiter()
    v.step(0.0, "slightly_left", 2, radio=True)
    assert v.step(4.0, None, 0, radio=True)["dropped"] == "stale: slightly_left"


def test_higher_call_replaces_a_held_one():
    v = VoiceArbiter()
    v.step(0.0, "slightly_left", 2, radio=True)
    assert v.step(1.0, "radar_lost", 4, radio=True)["voice"] == "radar_lost"


def test_unknown_alert_is_refused():
    with pytest.raises(ValueError):
        VoiceArbiter().step(0.0, None, 0, ["NOT AN ALERT"])


def test_closed_loop_no_voice_under_an_aircraft_alert_display_stays():
    rc = ReplayConfig(aircraft_alerts=((68.0, 80.0, "CLOSURE PULL UP"),))
    fr = fly_replay(RWY, rc=rc, faults=(Fault("dropout", 70, 1e9),), seed=1)
    under = [f for f in fr if 68 <= f["t"] < 80]
    assert not any(f["voice"] for f in under)
    assert any(f["state"] == "RADAR LOST" and f["level"] == 4 for f in under)      # the display shows it at once
    assert any(f["voice_held"] for f in under)
