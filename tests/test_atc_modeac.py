"""SSR Mode A/C pulse-train encode/decode, garble and phantom flags."""
import numpy as np

from aerokit.atc import modeac as ac


def test_interrogation_modes():
    assert ac.interrogation_mode(8.05) == "A"
    assert ac.interrogation_mode(21.0) == "C"
    assert ac.interrogation_mode(12.0) is None


def test_mode_a_round_trip_with_jitter():
    rng = np.random.default_rng(0)
    for sq in ("7600", "1234", "0356", "7777", "0000"):
        t = [x + rng.normal(0, 0.02) for x in ac.reply_for_squawk(sq, t0_us=100.0, spi=True)]
        frames = ac.decode_pulses(t)
        assert len(frames) == 1
        f = frames[0]
        assert ac.mode_a_code(f) == sq and f.spi and not f.garbled


def test_mode_c_round_trip():
    for alt in (-1000, 0, 2500, 3000, 12300, 36000):
        f = ac.decode_pulses(ac.reply_for_altitude(alt, 50.0))
        assert len(f) == 1 and ac.mode_c_altitude(f[0]) == alt


def test_same_pulses_mean_different_things():
    """The reply alone is ambiguous: identical pulses read as a squawk or an altitude depending on the mode."""
    f = ac.decode_pulses(ac.reply_for_altitude(3000))[0]
    assert ac.mode_a_code(f) != "3000"
    assert ac.mode_c_altitude(f) == 3000


def test_overlapping_replies_are_flagged_garbled():
    t = ac.reply_for_squawk("1200", 0.0) + ac.reply_for_squawk("7000", 8.0)
    frames = ac.decode_pulses(t)
    assert frames and all(fr.garbled for fr in frames)


def test_fruit_adds_garble_at_high_rate():
    clean = ac.reply_for_squawk("4321", 1000.0)
    low = ac.decode_pulses(ac.add_fruit(clean, 100, 2000, seed=1))
    high = ac.decode_pulses(ac.add_fruit(clean, 20000, 2000, seed=1))
    assert any(not f.garbled and ac.mode_a_code(f) == "4321" for f in low)
    target = [f for f in high if abs(f.t_f1_us - 1000.0) < 0.05]
    assert target and (target[0].garbled or target[0].phantom_risk or len(high) > 1)
