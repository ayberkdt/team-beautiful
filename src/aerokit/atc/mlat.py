"""Multilateration (TDOA) and an ADS-B position-consistency check -- the independent cross-check against spoofed
ADS-B / replayed Mode S on final.

Every ground station time-stamps the same 1090 MHz reply; arrival-time differences against a reference station give
range differences d_i = |p - s_i| - |p - s_0| = c (t_i - t_0). The position is the least-squares solution of these
hyperbolic equations (Gauss-Newton from a start point). Accuracy follows from the geometry: with timing noise
sigma_t per station the position covariance is (c sigma_t)^2 (J^T Q^-1 J)^-1, Q the covariance of the differences
(1 on the diagonal + 1 everywhere from the shared reference); GDOP is its root trace / (c sigma_t). All of this is
derived here (no literature constant is used); the MLAT principle is summarised in research note R_mlat_wiki.md
[D-ag].

Spoof check: an ADS-B report states a position; MLAT measures where the transmitter really is. If they differ by
more than ``k`` times the MLAT standard deviation, the ADS-B position is flagged -- a valid CRC proves nothing about
the position (a spoofer computes correct parity, see ``modes.encode_position``).
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

__all__ = ["C", "tdoa_measure", "MlatFix", "solve_tdoa", "gdop", "adsb_consistency"]

C = 299_792_458.0


def tdoa_measure(p: Sequence[float], stations: np.ndarray, sigma_t: float = 0.0,
                 rng: np.random.Generator | None = None) -> np.ndarray:
    """Arrival times [s] (common unknown emission time removed) of a reply from ``p`` at each station, with Gaussian
    timing noise ``sigma_t`` per station."""
    pos = np.asarray(p, float)
    t = np.linalg.norm(stations - pos, axis=1) / C
    if sigma_t > 0:
        t = t + (rng or np.random.default_rng()).normal(0.0, sigma_t, len(t))
    return np.asarray(t, float)


@dataclass(frozen=True)
class MlatFix:
    position: np.ndarray
    covariance: np.ndarray
    iterations: int
    converged: bool
    residual_rms_m: float


def _jac(p: np.ndarray, stations: np.ndarray) -> np.ndarray:
    u = (p - stations) / np.linalg.norm(p - stations, axis=1)[:, None]
    return np.asarray(u[1:] - u[0], float)                   # d(|p-s_i| - |p-s_0|)/dp


def _q(n: int) -> np.ndarray:
    return np.eye(n - 1) + np.ones((n - 1, n - 1))           # covariance of t_i - t_0 in units of sigma_t^2


def solve_tdoa(times: np.ndarray, stations: np.ndarray, p0: Sequence[float], sigma_t: float = 1e-8,
               max_iter: int = 30, tol_m: float = 1e-4) -> MlatFix:
    """Weighted Gauss-Newton TDOA fix. ``stations`` is (n, d) with d = 2 or 3; n >= d + 1."""
    n, d = stations.shape
    if n < d + 1:
        raise ValueError(f"need at least {d + 1} stations for a {d}-D fix")
    dmeas = C * (np.asarray(times, float)[1:] - times[0])
    w = np.linalg.inv(_q(n))
    p = np.asarray(p0, float).copy()
    ok = False
    k = 0
    for k in range(1, max_iter + 1):
        r = np.linalg.norm(stations - p, axis=1)
        res = dmeas - (r[1:] - r[0])
        j = _jac(p, stations)
        step = np.linalg.solve(j.T @ w @ j, j.T @ w @ res)
        p = p + step
        if np.linalg.norm(step) < tol_m:
            ok = True
            break
    r = np.linalg.norm(stations - p, axis=1)
    res = dmeas - (r[1:] - r[0])
    j = _jac(p, stations)
    cov = (C * sigma_t) ** 2 * np.linalg.inv(j.T @ w @ j)
    return MlatFix(p, cov, k, ok, float(np.sqrt(np.mean(res ** 2))))


def gdop(p: Sequence[float], stations: np.ndarray) -> float:
    """Geometric dilution of precision of a TDOA fix at ``p``: sqrt(trace((J^T Q^-1 J)^-1))."""
    j = _jac(np.asarray(p, float), stations)
    return float(math.sqrt(np.trace(np.linalg.inv(j.T @ np.linalg.inv(_q(len(stations))) @ j))))


def adsb_consistency(adsb_position: Sequence[float], fix: MlatFix, k: float = 5.0, floor_m: float = 30.0) -> dict:
    """Compare a reported ADS-B position with the MLAT fix. Flag when the Mahalanobis distance exceeds ``k`` (and the
    distance exceeds ``floor_m``, so a tiny MLAT covariance cannot flag ordinary ADS-B error)."""
    dvec = np.asarray(adsb_position, float) - fix.position
    dist = float(np.linalg.norm(dvec))
    m2 = float(dvec @ np.linalg.solve(fix.covariance, dvec))
    flagged = math.sqrt(m2) > k and dist > floor_m
    return {"distance_m": dist, "mahalanobis": math.sqrt(m2), "flag": flagged,
            "status": "ADS-B POSITION INCONSISTENT WITH MLAT" if flagged else "consistent"}
