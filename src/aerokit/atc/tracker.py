"""A small multi-sensor surveillance tracker: alpha-beta, constant-velocity Kalman, gating, M-of-N track management.

Plots from PSR (range/azimuth, no identity), SSR (range/azimuth + squawk/altitude) and ADS-B (position + identity)
are all turned into Cartesian measurements with their own covariance and fed, in time order, to the same track
(the idea behind multi-sensor trackers such as EUROCONTROL ARTAS; this code is a teaching-size version, not ARTAS).

Coordinates: local east/north [m] around the radar; time [s].
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

import numpy as np

__all__ = ["Plot", "polar_to_plot", "AlphaBeta", "CvKalman", "ImmCv", "Track", "Tracker", "GATE_CHI2_2DOF_99"]

#: chi-square 99 % point for 2 degrees of freedom (= -2 ln 0.01)
GATE_CHI2_2DOF_99 = -2.0 * math.log(0.01)


@dataclass(frozen=True)
class Plot:
    """One measurement: time, position, 2x2 covariance, sensor tag and optional identity."""

    t: float
    xy: tuple[float, float]
    cov: tuple[tuple[float, float], tuple[float, float]]
    sensor: str = "PSR"
    ident: str | None = None          # ICAO address or squawk if the sensor provides one
    altitude_ft: float | None = None


def polar_to_plot(t: float, range_m: float, azimuth_deg: float, sigma_r_m: float, sigma_az_deg: float,
                  sensor: str = "PSR", ident: str | None = None, altitude_ft: float | None = None) -> Plot:
    """Range/azimuth (azimuth clockwise from north) to an east/north plot with the linearised covariance.

    Cross-range error grows with range: sigma_cross = R sigma_az. At 60 NM a 0.05 deg azimuth error is ~97 m,
    larger than a typical 30-50 m range error -- the covariance ellipse is long across the beam.
    """
    az = math.radians(azimuth_deg)
    x, y = range_m * math.sin(az), range_m * math.cos(az)
    j = np.array([[math.sin(az), range_m * math.cos(az)], [math.cos(az), -range_m * math.sin(az)]])
    rp = np.diag([sigma_r_m ** 2, math.radians(sigma_az_deg) ** 2])
    cov = j @ rp @ j.T
    return Plot(t, (x, y), ((cov[0, 0], cov[0, 1]), (cov[1, 0], cov[1, 1])), sensor, ident, altitude_ft)


class AlphaBeta:
    """Classical fixed-gain alpha-beta tracker per axis (the radar-display tracker of old)."""

    def __init__(self, xy: Sequence[float], t: float, alpha: float = 0.5, beta: float = 0.2):
        if not (0 < alpha <= 1 and 0 < beta < 2):
            raise ValueError("0 < alpha <= 1, 0 < beta < 2")
        self.pos = np.asarray(xy, float).copy()
        self.vel: np.ndarray = np.zeros(2)
        self.t = t
        self.alpha, self.beta = alpha, beta

    def update(self, xy: Sequence[float], t: float) -> np.ndarray:
        dt = t - self.t
        if dt <= 0:
            raise ValueError("time must increase")
        pred = self.pos + self.vel * dt
        r = np.asarray(xy, float) - pred
        self.pos = pred + self.alpha * r
        self.vel = self.vel + self.beta / dt * r
        self.t = t
        return self.pos.copy()


class CvKalman:
    """Constant-velocity Kalman filter, state [x, y, vx, vy], white-acceleration process noise ``q`` [m^2/s^3]."""

    def __init__(self, plot: Plot, q: float = 1.0, v_sigma: float = 150.0):
        self.x = np.array([plot.xy[0], plot.xy[1], 0.0, 0.0])
        p = np.zeros((4, 4))
        p[:2, :2] = np.array(plot.cov)
        p[2, 2] = p[3, 3] = v_sigma ** 2
        self.P = p
        self.t = plot.t
        self.q = q

    def _fq(self, dt: float) -> tuple[np.ndarray, np.ndarray]:
        f = np.eye(4)
        f[0, 2] = f[1, 3] = dt
        q1 = np.array([[dt ** 3 / 3, dt ** 2 / 2], [dt ** 2 / 2, dt]]) * self.q
        q = np.zeros((4, 4))
        q[np.ix_([0, 2], [0, 2])] = q1
        q[np.ix_([1, 3], [1, 3])] = q1
        return f, q

    def predict(self, t: float) -> tuple[np.ndarray, np.ndarray]:
        """Predicted state and covariance at ``t`` (does not change the filter)."""
        dt = t - self.t
        if dt < 0:
            raise ValueError("cannot predict backwards")
        f, q = self._fq(dt)
        return f @ self.x, f @ self.P @ f.T + q

    _H = np.array([[1.0, 0, 0, 0], [0, 1.0, 0, 0]])

    def innovation(self, plot: Plot) -> tuple[np.ndarray, np.ndarray, float]:
        """Innovation, its covariance S and the squared Mahalanobis distance."""
        x, p = self.predict(plot.t)
        nu = np.asarray(plot.xy) - self._H @ x
        s = self._H @ p @ self._H.T + np.array(plot.cov)
        return nu, s, float(nu @ np.linalg.solve(s, nu))

    def update(self, plot: Plot) -> None:
        x, p = self.predict(plot.t)
        nu = np.asarray(plot.xy) - self._H @ x
        s = self._H @ p @ self._H.T + np.array(plot.cov)
        k = p @ self._H.T @ np.linalg.inv(s)
        self.x = x + k @ nu
        ikh = np.eye(4) - k @ self._H
        self.P = ikh @ p @ ikh.T + k @ np.array(plot.cov) @ k.T      # Joseph form
        self.t = plot.t

    @property
    def speed_mps(self) -> float:
        return float(math.hypot(self.x[2], self.x[3]))

    @property
    def track_deg(self) -> float:
        return float(math.degrees(math.atan2(self.x[2], self.x[3])) % 360)


class ImmCv:
    """Interacting Multiple Model filter over constant-velocity models with different process noise.

    Low ``q`` = quiet cruise (narrow gate, smooth velocity); high ``q`` = manoeuvre (wide bandwidth). Mixing,
    per-model update, mode-probability update and moment-matched combination follow the IMM cycle described by
    Blom, Yang and Bar-Shalom (read by the research agent, note R_blom_imm_atc.md). Same interface as
    :class:`CvKalman`, so :class:`Tracker` can use either.
    """

    def __init__(self, plot: Plot, qs: Sequence[float] = (0.5, 40.0), p_stay: float = 0.95, v_sigma: float = 150.0):
        self.models = [CvKalman(plot, q, v_sigma) for q in qs]
        m = len(qs)
        self.PI = np.full((m, m), (1 - p_stay) / max(m - 1, 1))
        np.fill_diagonal(self.PI, p_stay)
        self.mu = np.full(m, 1.0 / m)
        self.t = plot.t
        self._combine()

    def _combine(self) -> None:
        self.x = sum(mu * f.x for mu, f in zip(self.mu, self.models))
        self.P = sum(mu * (f.P + np.outer(f.x - self.x, f.x - self.x)) for mu, f in zip(self.mu, self.models))

    def predict(self, t: float) -> tuple[np.ndarray, np.ndarray]:
        preds = [f.predict(t) for f in self.models]
        x = sum(mu * p[0] for mu, p in zip(self.mu, preds))
        P = sum(mu * (p[1] + np.outer(p[0] - x, p[0] - x)) for mu, p in zip(self.mu, preds))
        return x, P

    def innovation(self, plot: Plot) -> tuple[np.ndarray, np.ndarray, float]:
        x, p = self.predict(plot.t)
        H = CvKalman._H
        nu = np.asarray(plot.xy) - H @ x
        s = H @ p @ H.T + np.array(plot.cov)
        return nu, s, float(nu @ np.linalg.solve(s, nu))

    def update(self, plot: Plot) -> None:
        cbar = self.PI.T @ self.mu                                   # predicted mode probabilities
        w = (self.PI * self.mu[:, None]) / np.maximum(cbar[None, :], 1e-300)   # w[i, j] = P(i | j)
        xs = [f.x.copy() for f in self.models]
        Ps = [f.P.copy() for f in self.models]
        for j, f in enumerate(self.models):                          # interaction / mixing
            x0 = sum(w[i, j] * xs[i] for i in range(len(xs)))
            P0 = sum(w[i, j] * (Ps[i] + np.outer(xs[i] - x0, xs[i] - x0)) for i in range(len(xs)))
            f.x, f.P = x0, P0
        lik = np.empty(len(self.models))
        for j, f in enumerate(self.models):
            nu, s, d2 = f.innovation(plot)
            lik[j] = math.exp(-0.5 * d2) / (2 * math.pi * math.sqrt(max(np.linalg.det(s), 1e-300)))
            f.update(plot)
        mu = lik * cbar
        self.mu = mu / mu.sum() if mu.sum() > 0 else cbar
        self.t = plot.t
        self._combine()

    @property
    def speed_mps(self) -> float:
        return float(math.hypot(self.x[2], self.x[3]))

    @property
    def track_deg(self) -> float:
        return float(math.degrees(math.atan2(self.x[2], self.x[3])) % 360)

    @property
    def manoeuvre_probability(self) -> float:
        return float(self.mu[-1])


@dataclass
class Track:
    """A track with its filter, identity and management counters."""

    tid: int
    kf: "CvKalman | ImmCv"
    ident: str | None = None
    altitude_ft: float | None = None
    hits: list[bool] = field(default_factory=list)
    status: str = "TENTATIVE"        # TENTATIVE -> CONFIRMED -> COASTING -> DROPPED
    sensors: set[str] = field(default_factory=set)
    history: list[tuple[float, float, float]] = field(default_factory=list)   # (t, x, y) for history dots

    def label(self) -> dict:
        return {"id": self.tid, "ident": self.ident, "alt_ft": self.altitude_ft, "status": self.status,
                "x": float(self.kf.x[0]), "y": float(self.kf.x[1]), "gs_kt": self.kf.speed_mps / 0.514444,
                "trk_deg": self.kf.track_deg, "sensors": sorted(self.sensors)}


class Tracker:
    """Scan-by-scan tracker with global nearest-neighbour association.

    Confirmation: ``m`` hits in the last ``n`` scans. Coasting: a confirmed track that misses is predicted, not
    deleted; it is dropped after ``max_misses`` consecutive misses. An identity (ICAO/squawk) on a plot only ever
    *associates* with the track carrying the same identity -- identity mismatch is never overruled by distance.
    """

    def __init__(self, q: float = 1.0, gate: float = GATE_CHI2_2DOF_99, m: int = 2, n: int = 3, max_misses: int = 3,
                 imm: bool = False, psr_min_speed_mps: float = 0.0, psr_m: int | None = None, psr_n: int | None = None):
        """``psr_min_speed_mps`` > 0: a track fed only by PSR plots confirms only if its estimated speed is at least
        this (stationary clutter residue cannot form a moving track; a hovering helicopter cannot either, which is
        the price). ``psr_m``/``psr_n``: stricter M-of-N for PSR-only tracks."""
        self.q, self.gate, self.m, self.n, self.max_misses, self.imm = q, gate, m, n, max_misses, imm
        self.psr_min_speed_mps, self.psr_m, self.psr_n = psr_min_speed_mps, psr_m or m, psr_n or n
        self.tracks: list[Track] = []
        self._next = 1

    def _new(self, plot: Plot) -> None:
        kf = ImmCv(plot) if self.imm else CvKalman(plot, self.q)
        tr = Track(self._next, kf, plot.ident, plot.altitude_ft, [True], "TENTATIVE",
                   {plot.sensor}, [(plot.t, plot.xy[0], plot.xy[1])])
        self._next += 1
        self.tracks.append(tr)

    def scan(self, plots: Iterable[Plot]) -> list[Track]:
        """Process one scan's plots; returns the live (not dropped) tracks."""
        plots = list(plots)
        live = [t for t in self.tracks if t.status != "DROPPED"]
        pairs: list[tuple[float, int, int]] = []
        for i, tr in enumerate(live):
            for j, pl in enumerate(plots):
                if tr.ident and pl.ident and tr.ident != pl.ident:
                    continue
                _, _, d2 = tr.kf.innovation(pl)
                if d2 <= self.gate:
                    pairs.append((d2, i, j))
        used_t: set[int] = set()
        used_p: set[int] = set()
        for d2, i, j in sorted(pairs):
            if i in used_t or j in used_p:
                continue
            used_t.add(i)
            used_p.add(j)
            tr, pl = live[i], plots[j]
            tr.kf.update(pl)
            tr.sensors.add(pl.sensor)
            tr.ident = tr.ident or pl.ident
            if pl.altitude_ft is not None:
                tr.altitude_ft = pl.altitude_ft
            tr.history.append((pl.t, float(tr.kf.x[0]), float(tr.kf.x[1])))
            tr.hits.append(True)
        for i, tr in enumerate(live):
            if i not in used_t:
                tr.hits.append(False)
        for tr in live:
            recent = tr.hits[-self.n:]
            misses = 0
            for h in reversed(tr.hits):
                if h:
                    break
                misses += 1
            if tr.status == "TENTATIVE":
                psr_only = tr.sensors == {"PSR"}
                m_need, n_win = (self.psr_m, self.psr_n) if psr_only else (self.m, self.n)
                recent = tr.hits[-n_win:]
                fast_enough = not psr_only or tr.kf.speed_mps >= self.psr_min_speed_mps
                if sum(recent) >= m_need and fast_enough:
                    tr.status = "CONFIRMED"
                elif len(tr.hits) >= n_win and (sum(recent) < m_need or not fast_enough):
                    tr.status = "DROPPED"
            elif misses == 0:
                tr.status = "CONFIRMED"
            elif misses >= self.max_misses:
                tr.status = "DROPPED"
            else:
                tr.status = "COASTING"
        for j, pl in enumerate(plots):
            if j not in used_p:
                self._new(pl)
        return [t for t in self.tracks if t.status != "DROPPED"]
