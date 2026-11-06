"""'Translate signal' traces and sweeps: stages are explicit, nothing is invented, wrong values are rare."""
import numpy as np

from aerokit.atc import modes as M
from aerokit.atc.translate import (adsb_trace, flip_bits, mode_a_trace, modes_ber_outcomes, modes_outcome, voice_sweep,
                                   voice_trace, wilson)

PH = "beetle one two three turn left heading two seven zero descend and maintain three thousand feet"


def test_voice_trace_clean_reaches_display():
    st = voice_trace(PH, 40.0, own_callsign="BTL123", seed=1)
    assert [s.name[0] for s in st] == ["1", "2", "3", "4"]
    assert "HDG 270" in st[-1].output and "3000" in st[-1].output


def test_voice_trace_other_callsign_not_shown():
    st = voice_trace(PH.replace("one two three", "one three two"), 40.0, own_callsign="BTL123", seed=1)
    assert st[-1].output.startswith("not shown") and not st[-1].ok


def test_voice_sweep_conservative_fewer_wrong_than_naive():
    r = voice_sweep([PH], [6, 24], 150, own_callsign="BTL123", seed=0)
    for i in range(2):
        assert r["conservative"][i]["wrong_per_1000"] <= r["naive"][i]["wrong_per_1000"]
    assert r["conservative"][0]["withheld_pct"] > r["conservative"][1]["withheld_pct"]     # low SNR: more SAY AGAIN
    assert r["wer_pct"][0] > r["wer_pct"][1]


def test_wilson_bounds():
    lo, hi = wilson(0, 100)
    assert lo == 0.0 and 0.0 < hi < 0.05
    assert wilson(5, 0) == (0.0, 1.0)


def test_flip_bits_and_outcomes():
    rng = np.random.default_rng(0)
    msg = M.encode_position("4B1A23", 51.2, 4.1, 7000, False)
    same, n = flip_bits(msg, 0.0, rng)
    assert same == msg and n == 0 and modes_outcome(msg, same) == "intact"
    one = f"{int(msg, 16) ^ (1 << 40):028X}"
    assert modes_outcome(msg, one) == "repaired"
    two = f"{int(msg, 16) ^ (1 << 40) ^ (1 << 70):028X}"
    assert modes_outcome(msg, two) in ("rejected", "wrong")


def test_ber_sweep_never_shows_wrong_in_small_run():
    rows = modes_ber_outcomes([1e-3, 1e-2], 300, seed=2)["rows"]
    for r in rows:
        assert abs(r["intact"] + r["repaired"] + r["rejected"] + r["wrong"] - 1.0) < 1e-9
        assert r["counts"]["wrong"] == 0
    assert rows[1]["rejected"] > rows[0]["rejected"]


def test_adsb_trace_clean_and_rejected():
    st = adsb_trace("BTL123", "4B1A23", 51.2, 4.1, 7000)
    assert st[-1].output.startswith("BTL123") and "FL070" in st[-1].output
    bad = adsb_trace("BTL123", "4B1A23", 51.2, 4.1, 7000, ber=0.2, seed=1)   # heavy errors -> rejected, no position
    assert any("rejected" in s.output or not s.ok for s in bad)


def test_mode_a_trace_reads_7600_and_mode_c_by_spacing():
    st = mode_a_trace("7600")
    assert st[-1].output == "squawk 7600"
    assert "Mode C" in mode_a_trace("7600", p1_p3_us=21.0)[0].output
