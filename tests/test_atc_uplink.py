"""Guidance uplink: bit-exact round trip within LSB/2, CRC rejects corruption, out-of-range values refused, exact
nuisance-alarm formula agrees with Monte Carlo."""
import numpy as np
import pytest

from aerokit.atc import uplink as U


def test_round_trip_within_half_lsb():
    vals = {"seq": 17, "t_meas_s": 123.4, "range_m": 4321.0, "el_dev_m": -12.34, "az_dev_m": 56.78, "valid": 1,
            "quality": 6}
    back = U.unpack(U.pack(vals))
    q = U.quantisation_errors()
    for k, v in vals.items():
        assert abs(back[k] - v) <= q[k] + 1e-9
    assert U.format_bits() == 96


def test_crc_rejects_every_single_and_double_bit_error():
    w = U.pack({"seq": 1, "range_m": 1000.0, "el_dev_m": 3.0})
    n = U.format_bits()
    assert all(U.unpack(w ^ (1 << k)) is None for k in range(n))
    rng = np.random.default_rng(0)
    for _ in range(500):
        a, b = rng.choice(n, 2, replace=False)
        assert U.unpack(w ^ (1 << int(a)) ^ (1 << int(b))) is None


def test_out_of_range_is_refused_not_clipped():
    with pytest.raises(ValueError):
        U.pack({"el_dev_m": 500.0})


def test_losses_for_alarm():
    assert U.losses_for_alarm(1.0, 5.0) == 5          # 5 lost at 1 Hz -> 6 s gap > 5 s
    assert U.losses_for_alarm(1.0, 4.5) == 4
    assert U.losses_for_alarm(2.0, 1.0) == 2


def test_exact_matches_monte_carlo_and_monotonic():
    for p in (0.1, 0.25):
        exact = U.nuisance_alarm_probability(p, 1.0, 3.0, 120.0)
        mc = U.simulate_gaps(p, 1.0, 3.0, 120.0, 4000, seed=1)
        assert abs(exact - mc) < 0.03
    a = [U.nuisance_alarm_probability(p, 1.0, 3.0, 180.0) for p in (0.01, 0.05, 0.2)]
    assert a == sorted(a)
    assert U.nuisance_alarm_probability(0.05, 1.0, 5.0, 180.0) < U.nuisance_alarm_probability(0.05, 1.0, 2.0, 180.0)
    assert U.p_no_long_gap(10, 3, 0.0) == 1.0 and U.p_no_long_gap(10, 3, 1.0) == 0.0
