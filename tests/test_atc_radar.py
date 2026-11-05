"""PSR/SSR budgets and detection probability: formulas checked against exact computation and Monte Carlo."""
import math

import numpy as np
import pytest

from aerokit.atc import radar as r


def test_albersheim_matches_exact_nonfluctuating():
    for pd, pfa in ((0.9, 1e-6), (0.8, 1e-4), (0.5, 1e-8)):
        snr = 10 ** (r.albersheim_snr_db(pd, pfa) / 10)
        assert r.pd_nonfluctuating(snr, pfa) == pytest.approx(pd, abs=0.02)


def test_albersheim_reference_value():
    assert r.albersheim_snr_db(0.9, 1e-6) == pytest.approx(13.1, abs=0.1)


def test_swerling1_monte_carlo():
    rng = np.random.default_rng(0)
    snr, pfa = 10 ** (15 / 10), 1e-3
    n = 200_000
    thr = -math.log(pfa)                         # on power with unit mean noise power
    sig = rng.exponential(snr, n)                # Rayleigh amplitude -> exponential power
    amp = np.sqrt(sig)
    ph = rng.uniform(0, 2 * np.pi, n)
    i = amp * np.cos(ph) + rng.normal(0, math.sqrt(0.5), n)
    q = amp * np.sin(ph) + rng.normal(0, math.sqrt(0.5), n)
    assert np.mean(i ** 2 + q ** 2 > thr) == pytest.approx(r.pd_swerling1(snr, pfa), abs=0.005)


def test_fluctuation_loss():
    pfa = 1e-6
    snr = 10 ** (13.2 / 10)
    assert r.pd_swerling1(snr, pfa) < r.pd_nonfluctuating(snr, pfa) - 0.2


def test_psr_r4_and_range_for_pd():
    p1 = r.psr_received_power(1e6, 34, 2.8e9, 2.0, 10_000)
    p2 = r.psr_received_power(1e6, 34, 2.8e9, 2.0, 20_000)
    assert p1 / p2 == pytest.approx(16.0)
    snr_ref = r.psr_snr(25e3, 34, 2.8e9, 2.0, 50 * 1852, 1e6, 3, 6, n_coherent=16)
    rng_pd = r.psr_range_for_pd(0.9, 1e-6, snr_ref, 50 * 1852)
    snr_at = snr_ref * (50 * 1852 / rng_pd) ** 4
    assert r.pd_swerling1(snr_at, 1e-6) == pytest.approx(0.9, abs=1e-9)


def test_radar_horizon():
    # Wikipedia example: 1.6 km height -> ~164 km with 4/3 earth (their R_e 6.4e3 km; ours 6371 km)
    assert r.radar_horizon_m(1600.0) / 1e3 == pytest.approx(164, rel=0.01)


def test_ssr_one_way_r2():
    a, b = r.ssr_link(10 * 1852), r.ssr_link(20 * 1852)
    assert a.uplink_dbm - b.uplink_dbm == pytest.approx(20 * math.log10(2), abs=1e-9)
    assert a.downlink_dbm - b.downlink_dbm == pytest.approx(20 * math.log10(2), abs=1e-9)


def test_hits_and_m_of_n():
    assert r.hits_per_scan(250, 2.4, 4.8) == pytest.approx(8.0)
    assert r.pd_m_of_n(0.9, 8, 4) > 0.99
    assert r.fruit_free_probability(0) == 1.0
    assert r.fruit_free_probability(10000) == pytest.approx(math.exp(-0.406))
