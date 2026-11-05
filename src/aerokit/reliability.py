"""Reliability and predictive maintenance: Weibull life, censored fits, system reliability, remaining useful life.

* **Weibull** (NIST/SEMATECH e-Handbook §8.1.6.2), shape ``γ`` and characteristic life ``α``:
  ``R(t) = exp(−(t/α)^γ)``, ``h(t) = (γ/α)(t/α)^{γ−1}``, ``MTTF = α Γ(1 + 1/γ)``; the B-life ``B_p`` is the time
  by which a fraction ``p`` has failed, ``α (−ln(1 − p))^{1/γ}``. ``γ < 1`` infant mortality, ``γ = 1`` random
  (exponential), ``γ > 1`` wear-out.
* **Fit with right-censoring** (§8.4.1.2): the likelihood is ``Π f(t_i)`` over failures times ``Π R(t_j)`` over
  units still running at ``t_j``; maximised numerically in ``(ln α, ln γ)``.
* **Systems** of independent units: series ``Π R_i``, parallel ``1 − Π(1 − R_i)``, k-out-of-n identical units
  ``Σ_{j≥k} C(n,j) R^j (1−R)^{n−j}`` (probability algebra).
* **Remaining useful life** from a monitored health indicator: fit ``y = a + b t`` (linear) or ``ln(y − y0) =
  a + b t`` (exponential degradation) by least squares on the history and extrapolate to the failure threshold;
  the spread comes from a residual bootstrap (an empirical method chosen here, not from a source read).
* :func:`synthetic_degradation` generates run-to-failure histories for demonstrating a monitoring concept when
  no data are given (the 2023 GTD card allowed simulated flight data).
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import minimize
from scipy.special import gammaln

from aerokit.references import cite

__all__ = ["Weibull", "fit_weibull", "series_reliability", "parallel_reliability", "k_out_of_n_reliability",
           "RulEstimate", "estimate_rul", "synthetic_degradation"]

FloatArray = NDArray[np.float64]


@cite("nist_sematech_2012", note="§8.1.6.2 Weibull formulas")
@dataclass(frozen=True)
class Weibull:
    """Two-parameter Weibull life distribution (``shape`` γ, ``scale`` α = characteristic life)."""

    shape: float
    scale: float

    def __post_init__(self) -> None:
        if not (self.shape > 0 and self.scale > 0 and math.isfinite(self.shape) and math.isfinite(self.scale)):
            raise ValueError("Weibull shape and scale must be positive and finite")

    def reliability(self, t: ArrayLike) -> FloatArray:
        """``R(t) = exp(−(t/α)^γ)`` (1 for t ≤ 0)."""
        x = np.clip(np.asarray(t, float), 0.0, None) / self.scale
        return np.exp(-(x ** self.shape))

    def cdf(self, t: ArrayLike) -> FloatArray:
        """``F(t) = 1 − R(t)``."""
        return 1.0 - self.reliability(t)

    def pdf(self, t: ArrayLike) -> FloatArray:
        """``f(t) = (γ/t)(t/α)^γ exp(−(t/α)^γ)`` (0 for t ≤ 0)."""
        tt = np.asarray(t, float)
        x = np.clip(tt, 1e-300, None) / self.scale
        return np.where(tt > 0, self.shape / self.scale * x ** (self.shape - 1) * np.exp(-(x ** self.shape)), 0.0)

    def hazard(self, t: ArrayLike) -> FloatArray:
        """``h(t) = (γ/α)(t/α)^{γ−1}``."""
        x = np.clip(np.asarray(t, float), 1e-300, None) / self.scale
        return self.shape / self.scale * x ** (self.shape - 1)

    @property
    def mttf(self) -> float:
        """Mean life ``α Γ(1 + 1/γ)``."""
        return self.scale * math.exp(gammaln(1.0 + 1.0 / self.shape))

    def b_life(self, fraction_failed: float) -> float:
        """Time by which ``fraction_failed`` of the population has failed (B10: 0.10)."""
        if not 0 < fraction_failed < 1:
            raise ValueError("fraction_failed must be in (0, 1)")
        return float(self.scale * (-math.log1p(-fraction_failed)) ** (1.0 / self.shape))

    def conditional_reliability(self, age: float, mission: float) -> float:
        """Probability that a unit of ``age`` survives a further ``mission``: ``R(age + mission) / R(age)``."""
        if age < 0 or mission < 0:
            raise ValueError("age and mission must be >= 0")
        return float(self.reliability(age + mission) / self.reliability(age))


@cite("nist_sematech_2012", note="§8.4.1.2 likelihood with right-censored units")
def fit_weibull(failures: Sequence[float], censored: Sequence[float] = ()) -> Weibull:
    """Maximum-likelihood Weibull from failure times and right-censored (still running) times.

    Raises
    ------
    ValueError
        Fewer than two failures, non-positive times, or the optimiser fails.
    """
    tf, tc = np.asarray(failures, float), np.asarray(censored, float)
    if tf.size < 2:
        raise ValueError("need at least two failure times")
    if (tf <= 0).any() or (tc <= 0).any() or not (np.isfinite(tf).all() and np.isfinite(tc).all()):
        raise ValueError("times must be positive and finite")

    def nll(p: FloatArray) -> float:
        a, g = math.exp(p[0]), math.exp(p[1])
        zf, zc = tf / a, tc / a
        ll = np.sum(np.log(g / a) + (g - 1.0) * np.log(zf) - zf ** g) - np.sum(zc ** g)
        return float(-ll)

    x0 = np.array([math.log(float(np.mean(np.r_[tf, tc]))), 0.0])
    res = minimize(nll, x0, method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-12, "maxiter": 20000})
    if not res.success:
        raise ValueError(f"Weibull fit did not converge: {res.message}")
    return Weibull(shape=math.exp(res.x[1]), scale=math.exp(res.x[0]))


def _probabilities(r: Sequence[float]) -> FloatArray:
    a = np.asarray(r, float)
    if a.size == 0 or ((a < 0) | (a > 1)).any():
        raise ValueError("reliabilities must be a non-empty sequence in [0, 1]")
    return a


def series_reliability(r: Sequence[float]) -> float:
    """All units needed: ``Π R_i``."""
    return float(np.prod(_probabilities(r)))


def parallel_reliability(r: Sequence[float]) -> float:
    """Any one unit suffices: ``1 − Π (1 − R_i)``."""
    return float(1.0 - np.prod(1.0 - _probabilities(r)))


def k_out_of_n_reliability(k: int, n: int, r: float) -> float:
    """At least ``k`` of ``n`` identical independent units work (binomial sum)."""
    if not (0 <= k <= n and 0 <= r <= 1):
        raise ValueError("need 0 <= k <= n and 0 <= r <= 1")
    return float(sum(math.comb(n, j) * r ** j * (1 - r) ** (n - j) for j in range(k, n + 1)))


@dataclass(frozen=True)
class RulEstimate:
    """Remaining useful life from the last observation (same time unit as the history)."""

    model: str
    rul: float
    lower: float
    upper: float
    failure_time: float
    coefficients: tuple[float, float]


def _fit(t: FloatArray, y: FloatArray, model: str, y0: float) -> tuple[float, float]:
    if model == "linear":
        b, a = np.polyfit(t, y, 1)
        return float(a), float(b)
    if (y - y0 <= 0).any():
        raise ValueError("exponential model needs y > y0 for every sample")
    b, a = np.polyfit(t, np.log(y - y0), 1)
    return float(a), float(b)


def _crossing(a: float, b: float, threshold: float, model: str, y0: float) -> float:
    if b <= 0:
        return math.inf
    if model == "linear":
        return (threshold - a) / b
    if threshold <= y0:
        raise ValueError("threshold must exceed y0 for the exponential model")
    return (math.log(threshold - y0) - a) / b


def estimate_rul(times: ArrayLike, health: ArrayLike, threshold: float, model: str = "linear", *, y0: float = 0.0,
                 n_boot: int = 500, confidence: float = 0.9, seed: int = 0) -> RulEstimate:
    """RUL of a rising degradation indicator ``health`` reaching ``threshold`` (see module docstring).

    ``rul`` is from the last sample; ``lower``/``upper`` are the residual-bootstrap quantiles at ``confidence``.
    A non-rising fitted trend gives ``inf``.

    Raises
    ------
    ValueError
        Fewer than 3 samples, unknown model, unordered times, or the threshold already reached.
    """
    t, y = np.asarray(times, float), np.asarray(health, float)
    if t.size != y.size or t.size < 3:
        raise ValueError("need at least 3 samples of equal length")
    if (np.diff(t) <= 0).any():
        raise ValueError("times must be strictly increasing")
    if model not in ("linear", "exponential"):
        raise ValueError("model must be 'linear' or 'exponential'")
    if y[-1] >= threshold:
        raise ValueError("the threshold is already reached")
    if not (n_boot >= 10 and 0 < confidence < 1):
        raise ValueError("need n_boot >= 10 and 0 < confidence < 1")
    a, b = _fit(t, y, model, y0)
    t_fail = _crossing(a, b, threshold, model, y0)
    z = y if model == "linear" else np.log(y - y0)         # the quantity that is linear in t
    base = a + b * t
    resid = z - base
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(n_boot):
        bb, ab = np.polyfit(t, base + rng.choice(resid, size=resid.size, replace=True), 1)
        sims.append(_crossing(float(ab), float(bb), threshold, model, y0) - float(t[-1]))
    q = (1.0 - confidence) / 2.0
    srt = np.sort(np.asarray(sims))                        # order statistics: robust to infinite (flat) samples
    lo, hi = srt[int(math.floor(q * (srt.size - 1)))], srt[int(math.ceil((1.0 - q) * (srt.size - 1)))]
    return RulEstimate(model, max(t_fail - float(t[-1]), 0.0), max(float(lo), 0.0), float(hi), t_fail, (a, b))


def synthetic_degradation(n_units: int, *, initial: float = 0.0, rate_mean: float = 1.0, rate_cv: float = 0.2,
                          noise: float = 0.05, threshold: float = 1.0, model: str = "exponential",
                          dt: float = 1.0, seed: int = 0) -> list[tuple[FloatArray, FloatArray]]:
    """Run-to-failure histories ``(t, y)`` of ``n_units``: unit-to-unit rate scatter ``rate_cv``, Gaussian noise.

    ``exponential``: ``y = initial + 0.01·(exp(b t) − 1)`` (b drawn per unit); ``linear``: ``y = initial + b t``;
    each history stops at the first sample at or above ``threshold``.
    """
    if n_units < 1 or not (rate_mean > 0 and rate_cv >= 0 and noise >= 0 and dt > 0 and threshold > initial):
        raise ValueError("invalid synthetic-degradation parameters")
    if model not in ("linear", "exponential"):
        raise ValueError("model must be 'linear' or 'exponential'")
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_units):
        b = max(rng.normal(rate_mean, rate_cv * rate_mean), 0.05 * rate_mean)
        ts, ys, t = [], [], 0.0
        while True:
            clean = initial + (b * t if model == "linear" else 0.01 * math.expm1(b * t))
            y = clean + rng.normal(0.0, noise)
            ts.append(t)
            ys.append(y)
            if clean >= threshold or len(ts) > 100000:
                break
            t += dt
        out.append((np.asarray(ts), np.asarray(ys)))
    return out
