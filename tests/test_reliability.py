"""Weibull life, censored MLE, system reliability and RUL (aerokit.reliability)."""
import math

import numpy as np
import pytest
from scipy import integrate, stats

from aerokit import reliability as R
from aerokit.verification import check, check_true, expect_error

NIST = "NIST/SEMATECH e-Handbook §8.1.6.2"


def test_weibull_formulas():
    w = R.Weibull(2.0, 1000.0)
    check("MTTF = α Γ(1 + 1/γ)", w.mttf, 1000 * math.gamma(1.5), rtol=1e-12, source=NIST)
    check("F(B10) = 0.10", float(w.cdf(w.b_life(0.10))), 0.10, rtol=1e-12)
    check("∫ f dt = 1", integrate.quad(lambda t: float(w.pdf(t)), 0, np.inf)[0], 1.0, rtol=1e-8)
    h = 1e-3
    check("f = −dR/dt", float(w.pdf(700.0)), float((w.reliability(700 - h) - w.reliability(700 + h)) / (2 * h)),
          rtol=1e-6)
    check("h = f / R", float(w.hazard(700.0)), float(w.pdf(700.0) / w.reliability(700.0)), rtol=1e-12)
    e = R.Weibull(1.0, 500.0)
    check("γ = 1 is exponential: R = exp(−t/α)", float(e.reliability(250.0)), math.exp(-0.5), rtol=1e-12, source=NIST)
    check("γ = 1: constant hazard 1/α", float(e.hazard(10.0)), float(e.hazard(900.0)), rtol=1e-12)
    check("γ = 1 is memoryless", e.conditional_reliability(400.0, 100.0), float(e.reliability(100.0)), rtol=1e-12)
    expect_error("non-positive shape", R.Weibull, 0.0, 1.0, error=ValueError)


def test_uncensored_fit_matches_scipy():
    t = 1000.0 * np.random.default_rng(3).weibull(1.7, 300)
    ours = R.fit_weibull(t)
    shape, _, scale = stats.weibull_min.fit(t, floc=0)
    check("MLE shape = scipy weibull_min.fit", ours.shape, shape, rtol=1e-4, source="scipy.stats (independent MLE)")
    check("MLE scale = scipy weibull_min.fit", ours.scale, scale, rtol=1e-4)


def test_censored_fit_recovers_the_population():
    t = 800.0 * np.random.default_rng(7).weibull(2.5, 4000)
    end = 900.0
    fit = R.fit_weibull(t[t <= end], np.full(int((t > end).sum()), end))
    check("censored MLE shape (n = 4000, ~1/3 censored)", fit.shape, 2.5, rtol=0.05)
    check("censored MLE scale", fit.scale, 800.0, rtol=0.03)
    naive = R.fit_weibull(t[t <= end])
    check_true("dropping the survivors underestimates the life", naive.scale < 0.95 * fit.scale,
               f"{naive.scale:.0f} vs {fit.scale:.0f}")
    expect_error("one failure is not enough", R.fit_weibull, [10.0], error=ValueError)


def test_system_reliability():
    r = [0.9, 0.95, 0.99]
    check("series = product", R.series_reliability(r), 0.9 * 0.95 * 0.99, rtol=1e-12)
    check("parallel = 1 − Π(1 − R)", R.parallel_reliability(r), 1 - 0.1 * 0.05 * 0.01, rtol=1e-12)
    check("1-out-of-3 = parallel of 3", R.k_out_of_n_reliability(1, 3, 0.9), R.parallel_reliability([0.9] * 3),
          rtol=1e-12)
    check("3-out-of-3 = series of 3", R.k_out_of_n_reliability(3, 3, 0.9), 0.9 ** 3, rtol=1e-12)
    check("2-out-of-3 = 3R² − 2R³", R.k_out_of_n_reliability(2, 3, 0.9), 3 * 0.81 - 2 * 0.729, rtol=1e-12)
    expect_error("R > 1 rejected", R.series_reliability, [1.2], error=ValueError)


def test_rul_noiseless_models_are_exact():
    t = np.arange(0.0, 20.0)
    r = R.estimate_rul(t, 0.1 + 0.02 * t, 1.0, "linear", n_boot=20)
    check("linear: crossing (1 − 0.1)/0.02 = 45", r.failure_time, 45.0, rtol=1e-9)
    check("RUL from the last sample (t = 19)", r.rul, 26.0, rtol=1e-9)
    y = 0.05 + 0.01 * np.exp(0.15 * t)
    re = R.estimate_rul(t, y, 1.0, "exponential", y0=0.05, n_boot=20)
    check("exponential: ln((1 − 0.05)/0.01)/0.15", re.failure_time, math.log(0.95 / 0.01) / 0.15, rtol=1e-9)


def test_rul_interval_covers_the_truth_on_synthetic_data():
    hits = 0
    histories = R.synthetic_degradation(20, model="linear", rate_mean=0.01, rate_cv=0.3, noise=0.01, threshold=1.0)
    for t, y in histories:
        k = len(t) // 2
        est = R.estimate_rul(t[:k], y[:k], 1.0, "linear", n_boot=300, confidence=0.9, seed=k)
        true = t[-1] - t[k - 1]
        hits += est.lower <= true <= est.upper
    # measured 2026-10-25: 51/60 = 85 % for a nominal 90 % (the residual bootstrap slightly under-covers)
    check_true("90 % bootstrap interval covers the true RUL in ≥ 14 of 20 units", hits >= 14, f"{hits}/20")
    for t, y in histories:
        check_true("each history ends at or past the threshold", y[-1] >= 1.0 - 0.05)


def test_rul_edge_cases():
    t = np.arange(5.0)
    flat = R.estimate_rul(t, np.full(5, 0.2) + 1e-9 * t[::-1], 1.0, n_boot=20)
    check_true("falling trend → infinite RUL", math.isinf(flat.rul), flat.rul)
    expect_error("threshold already reached", R.estimate_rul, t, np.linspace(0, 2, 5), 1.0, error=ValueError)
    expect_error("unordered times", R.estimate_rul, [0, 2, 1], [0.1, 0.2, 0.3], 1.0, error=ValueError)
    with pytest.raises(ValueError):
        R.estimate_rul(t, np.linspace(0.1, 0.5, 5), 1.0, "quadratic")
