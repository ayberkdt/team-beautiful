"""Three rules: the cue goes quiet under an aircraft alert, a routine call yields to the radio, the display never waits."""
import pytest

from aerokit.approach import Runway
from aerokit.atc.parcue import Fault, ReplayConfig, fly_replay
from aerokit.atc.voice_arbiter import AIRCRAFT_ALERTS, VoiceArbiter

RWY = Runway(51.0, 4.0, 10.0, 250.0)


def test_priority_table_is_the_tso_order():
    order = sorted((v[0], k) for k, v in AIRCRAFT_ALERTS.items() if v[0] <= 23)
    assert [k for _, k in order[:4]] == ["REACTIVE WINDSHEAR", "SINK RATE PULL UP", "CLOSURE PULL UP", "TERRAIN"]
    assert AIRCRAFT_ALERTS["MINIMUMS"][0] < AIRCRAFT_ALERTS["GLIDESLOPE"][0] == 19


@pytest.mark.parametrize("alert", ["CLOSURE PULL UP", "TERRAIN", "REACTIVE WINDSHEAR", "TCAS RA", "GLIDESLOPE"])
def test_routine_call_is_dropped_under_an_aircraft_alert(alert):
    a = VoiceArbiter().step("well_below", 3, [alert])
    assert a["voice"] is None and a["dropped"] == "well_below"


@pytest.mark.parametrize("alert", ["CLOSURE PULL UP", "SINK RATE", "TCAS RA"])
def test_warning_waits_for_the_alert_to_end(alert):
    v = VoiceArbiter()
    assert v.step("radar_lost", 4, [alert])["held"]
    assert v.step(None, 0, [alert])["voice"] is None
    assert v.step(None, 0, [])["voice"] == "radar_lost"


def test_radio_drops_routine_but_not_a_warning():
    assert VoiceArbiter().step("slightly_left", 2, radio=True)["voice"] is None
    assert VoiceArbiter().step("radar_lost", 4, radio=True)["voice"] == "radar_lost"


def test_clear_channel_plays_at_once():
    assert VoiceArbiter().step("slightly_left", 2)["voice"] == "slightly_left"


def test_unknown_alert_is_refused():
    with pytest.raises(ValueError):
        VoiceArbiter().step(None, 0, ["NOT AN ALERT"])


def test_closed_loop_no_voice_under_an_aircraft_alert_display_stays():
    rc = ReplayConfig(aircraft_alerts=((68.0, 80.0, "CLOSURE PULL UP"),))
    fr = fly_replay(RWY, rc=rc, faults=(Fault("dropout", 70, 1e9),), seed=1)
    under = [f for f in fr if 68 <= f["t"] < 80]
    assert not any(f["voice"] for f in under)
    assert any(f["state"] == "RADAR LOST" and f["level"] == 4 for f in under)      # the display shows it at once
    assert any(f["voice_held"] for f in under)
