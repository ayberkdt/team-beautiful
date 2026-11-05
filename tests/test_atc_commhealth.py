"""Comm-health state machine and the 'never invent a clearance' display invariant."""
import numpy as np

from aerokit.atc.channel import WordChannel, degrade_audio, degrade_words, measure_audio, tone_speech
from aerokit.atc.clearance import parse
from aerokit.atc.commhealth import (AdvisoryDisplay, AltLink, CommHealthMonitor, CommInputs, States,
                                    run_scenario)


def tick(t, **kw):
    base = dict(carrier=True, snr_db=25.0, asr_conf=0.9, heard_traffic=True)
    base.update(kw)
    return CommInputs(t, **base)


def test_normal_then_degraded_then_recovery():
    mon = CommHealthMonitor()
    assert mon.step(tick(0)) == States.NORMAL
    assert mon.step(tick(1, snr_db=6.0)) == States.DEGRADED
    assert mon.step(tick(2)) == States.DEGRADED      # hysteresis
    mon.step(tick(3))
    assert mon.step(tick(4)) == States.NORMAL


def test_silence_alone_is_not_loss():
    mon = CommHealthMonitor()
    for t in range(0, 120):
        st = mon.step(CommInputs(float(t), carrier=False))
    assert st == States.NORMAL


def test_rx_lost_needs_unanswered_calls():
    mon = CommHealthMonitor()
    mon.step(tick(0))
    states = []
    for t in range(1, 80):
        states.append(mon.step(CommInputs(float(t), carrier=False, we_transmitted=t in (35, 50))))
    assert states[-1] == States.RX_LOST


def test_tx_lost_when_atc_keeps_asking():
    mon = CommHealthMonitor()
    mon.step(tick(0))
    mon.step(tick(1, atc_to_us=True, atc_asks_if_read=True))
    assert mon.step(tick(2, atc_to_us=True, atc_asks_if_read=True)) == States.TX_LOST


def test_alternate_and_common_cause():
    alt_same_bus = AltLink("VHF2", True, bus="BUS1", antenna="ANT2")
    alt_indep = AltLink("CPDLC (VDL2)", True, bus="BUS2", antenna="ANT3", authorised_for="datalink (non-urgent)")
    mon = CommHealthMonitor()
    st = mon.step(CommInputs(0.0, carrier=False, primary_bus_ok=False, alt_links=(alt_same_bus,)))
    assert st == States.ALL_COMMS_LOST and any("shares failed bus" in r for r in mon.reasons)
    st = mon.step(CommInputs(1.0, carrier=False, primary_bus_ok=False, alt_links=(alt_same_bus, alt_indep)))
    assert st == States.ALTERNATE_AVAILABLE


def test_display_never_shows_unreceived_or_fresh_in_loss():
    rng = np.random.default_rng(42)
    for trial in range(30):
        ticks, msgs = [], {}
        mid = 0
        for t in range(200):
            carrier = rng.random() > 0.3
            ticks.append(CommInputs(float(t), carrier=carrier, snr_db=float(rng.uniform(0, 30)),
                                    asr_conf=float(rng.uniform(0.2, 1)), heard_traffic=carrier and rng.random() > .5,
                                    we_transmitted=rng.random() < 0.05,
                                    atc_asks_if_read=rng.random() < 0.02))
            if rng.random() < 0.1:
                mid += 1
                msgs[float(t)] = parse("beetle one two three heading two seven zero", own_callsign="BTL123",
                                       t_received=float(t), msg_id=mid)
        views = run_scenario(ticks, msgs)
        received_ids = {m.msg_id for t, m in msgs.items() if ticks[int(t)].carrier}
        for v, x in zip(views, ticks):
            for it in v["items"]:
                assert it["msg_id"] in received_ids
                assert it["t_received"] <= v["t"]
                if v["state"] in (States.RX_LOST, States.ALL_COMMS_LOST):
                    assert it["tag"].startswith("STALE")
            assert v["advisory_only"] is True


def test_display_degraded_marks_unconfirmed_and_ack():
    d = AdvisoryDisplay()
    d.receive(parse("beetle one two three heading two seven zero", own_callsign="BTL123", t_received=0.0, msg_id=1))
    assert d.view(1.0, States.DEGRADED)["items"][0]["tag"] == "UNCONFIRMED"
    d.acknowledge(1)
    v = d.view(1.0, States.DEGRADED)["items"][0]
    assert v["tag"] == "CONFIRMED" and v["pilot_confirmed"]
    assert d.view(500.0, States.NORMAL)["items"][0]["tag"].startswith("STALE")
    assert d.view(5.0, States.RX_LOST)["reminders"]


def test_audio_measurements():
    fs = 8000
    x = tone_speech(3.0, fs)
    clean = measure_audio(degrade_audio(x, fs, snr_db=30), fs)
    noisy = measure_audio(degrade_audio(x, fs, snr_db=3), fs)
    assert clean.snr_est_db is not None and noisy.snr_est_db is not None
    assert clean.snr_est_db > noisy.snr_est_db + 5
    clipped = measure_audio(degrade_audio(x, fs, snr_db=30, clip=0.1), fs)
    assert clipped.clip_fraction > clean.clip_fraction
    dead = measure_audio(degrade_audio(x, fs, snr_db=30, dropouts=[(1.0, 1.8)]), fs)
    assert dead.dropout_fraction > clean.dropout_fraction + 0.1
    squelched = degrade_audio(x, fs, carrier=False)
    assert np.sqrt(np.mean(squelched ** 2)) < 0.01


def test_word_channel_monotone_and_deterministic():
    ch = WordChannel()
    assert ch.error_rate(0) > ch.error_rate(10) > ch.error_rate(30)
    a = degrade_words("beetle one two three heading two seven zero", 5, seed=3)
    b = degrade_words("beetle one two three heading two seven zero", 5, seed=3)
    assert a == b


def test_stuck_microphone_is_tx_lost():
    mon = CommHealthMonitor()
    mon.step(tick(0))
    assert mon.step(tick(1, ptt_held_s=10)) == States.NORMAL
    assert mon.step(tick(2, ptt_held_s=45)) == States.TX_LOST
    assert any("stuck microphone" in r for r in mon.reasons)


def test_cpdlc_uplink_mapping():
    from aerokit.atc.datalink import Uplink, uplink_to_clearance
    c = uplink_to_clearance(Uplink(190, 250, "BTL123", 170.0, 9), "BTL123")
    assert c.source.startswith("CPDLC") and c.addressed_to_us and c.get("heading").value == 250
    bad = uplink_to_clearance(Uplink(117, ("approach", "118.020"), "BTL123", 1.0, 10), "BTL123")
    assert bad.get("frequency").status == "INVALID"
    other = uplink_to_clearance(Uplink(20, 120, "BTL132", 1.0, 11), "BTL123")
    assert other.addressed_to_us is False
    unk = uplink_to_clearance(Uplink(999, "x", "BTL123", 1.0, 12), "BTL123")
    assert unk.instructions[0].status == "INFO"



def test_partial_transmission_never_filled_in():
    d = AdvisoryDisplay()
    c = parse([("beetle", .9), ("one", .9), ("two", .9), ("three", .9), ("turn", .9), ("right", .9), ("heading", .9),
               ("one", .9), ("niner", .9), ("zero", .9), ("descend", .9), ("and", .9), ("maintain", .9),
               ("<gap>", 0.0), ("feet", .6)], own_callsign="BTL123", t_received=0.0, msg_id=7, partial=True)
    d.receive(c)
    v = d.view(2.0, States.NORMAL)
    items = {it["kind"]: it for it in v["items"]}
    assert items["altitude"]["tag"] == "NOT_RECEIVED" and items["altitude"]["text"] == "DESCEND NOT RECEIVED"
    assert items["heading"]["tag"] == "UNCONFIRMED" and items["heading"]["text"] == "TURN RIGHT HDG 190"
    assert v["partial"] is True
    assert not any(ch.isdigit() for ch in items["altitude"]["text"])
