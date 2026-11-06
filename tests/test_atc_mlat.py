"""MLAT: exact recovery without noise, covariance consistent with Monte Carlo, GDOP worse outside the station hull,
spoofed ADS-B position flagged."""
import numpy as np
import pytest

from aerokit.atc.mlat import adsb_consistency, gdop, solve_tdoa, tdoa_measure

ST = np.array([[0.0, 0.0], [20_000.0, 0.0], [0.0, 20_000.0], [20_000.0, 20_000.0], [10_000.0, -8_000.0]])


def test_noise_free_exact():
    p = np.array([7_300.0, 11_900.0])
    fix = solve_tdoa(tdoa_measure(p, ST), ST, p0=[10_000, 10_000])
    assert fix.converged and np.linalg.norm(fix.position - p) < 1e-3


def test_covariance_matches_monte_carlo():
    rng = np.random.default_rng(0)
    p = np.array([9_000.0, 8_000.0])
    sig = 10e-9                                                   # 10 ns per station ~ 3 m
    errs = np.array([solve_tdoa(tdoa_measure(p, ST, sig, rng), ST, [10_000, 10_000], sig).position - p
                     for _ in range(400)])
    fix = solve_tdoa(tdoa_measure(p, ST), ST, [10_000, 10_000], sig)
    assert np.sqrt(np.trace(np.cov(errs.T))) == pytest.approx(np.sqrt(np.trace(fix.covariance)), rel=0.15)


def test_gdop_grows_outside_the_network():
    inside, outside = gdop([10_000, 10_000], ST), gdop([60_000, 60_000], ST)
    assert outside > 3 * inside


def test_spoofed_adsb_flagged_true_report_not():
    rng = np.random.default_rng(1)
    p = np.array([12_000.0, 6_000.0])
    fix = solve_tdoa(tdoa_measure(p, ST, 10e-9, rng), ST, [10_000, 10_000], 10e-9)
    assert not adsb_consistency(p + np.array([8.0, -5.0]), fix)["flag"]          # honest ADS-B with ~10 m error
    spoof = adsb_consistency(p + np.array([0.0, 400.0]), fix)                   # ghost 400 m off: valid CRC, false position
    assert spoof["flag"] and spoof["status"].startswith("ADS-B POSITION INCONSISTENT")


def test_adsb_noise_and_horizontal_only_options():
    rng = np.random.default_rng(3)
    st3 = np.array([[0, 0, 20], [9000, 2000, 30], [-6000, 7000, 25], [-4000, -8000, 40], [7000, -6000, 15]], float)
    p = np.array([-9000.0, 1500.0, 600.0])
    honest = flagged_default = 0
    for _ in range(200):
        fix = solve_tdoa(tdoa_measure(p, st3, 2e-9, rng), st3, p + 50, 2e-9)
        rep = p + np.array([*rng.normal(0, 15, 2), 0.0])                          # honest ADS-B, 15 m noise
        honest += adsb_consistency(rep, fix, adsb_sigma_m=15.0, dims=2)["flag"]
        flagged_default += adsb_consistency(rep, fix)["flag"]
    assert honest <= 2 < flagged_default                  # ignoring ADS-B noise and the poor MLAT height flags honest
    fix = solve_tdoa(tdoa_measure(p, st3, 2e-9, rng), st3, p + 50, 2e-9)
    assert adsb_consistency(p + np.array([300.0, 0, 0]), fix, adsb_sigma_m=15.0, dims=2)["flag"]


def test_needs_enough_stations():
    with pytest.raises(ValueError):
        solve_tdoa(np.zeros(2), ST[:2], [0, 0])
