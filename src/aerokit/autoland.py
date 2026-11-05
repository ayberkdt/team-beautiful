"""Automated approach and landing with multi-sensor fusion and fault detection and exclusion (FDE).

**Filter.** :class:`ApproachEKF` is an extended Kalman filter in the runway frame of :class:`aerokit.approach.Runway`
with seven states ``[x, y, z, vx, vy, vz, b]``: position, velocity and the bias ``b`` of the barometric height
(a cold or warm column shifts the baro reading, see :func:`aerokit.approach.cold_temperature_true_height`; the
filter learns it from the geometric sensors). The prediction integrates the IMU-measured acceleration; its noise
enters as process noise (white acceleration), the baro bias is a slow random walk.

**Measurements.**
* GNSS position ``(x, y, z) + noise`` — the source that can be jammed or spoofed (:attr:`FusionConfig.gnss_ramp`).
* Ground radar at a known site (runway frame): range, azimuth ``atan2(dy, dx)`` and elevation
  ``atan2(dz, √(dx² + dy²))``; non-linear, linearised with the analytic Jacobian (:func:`radar_measurement`).
* Baro height ``z + b``.
* Radio altimeter ``z`` (flat terrain at threshold height) below :attr:`FusionConfig.radalt_max_height`, noise a
  fraction of height with a floor.

**Integrity — two FDE modes.** ``"innovation"``: every update forms ``NIS = νᵀ S⁻¹ ν`` and a sensor whose NIS
exceeds ``χ²_dof(1 − α)`` for ``persist`` consecutive updates is excluded. Its known weakness shows in the tests:
a slowly drifting *precise* source (spoofed GNSS) drags the estimate with it, so the *honest* sensors look
inconsistent and get excluded instead. ``"separation"`` (default): a bank of sub-filters, each leaving one sensor
out, runs beside the main filter; for sensor i the separation ``d = x₀ − xᵢ`` is tested with ``dᵀ (Pᵢ − P₀)⁻¹ d``
against ``χ²₃(1 − α)`` (the solution-separation idea behind ARAIM/MHSS, Rippl & Perea 2018). Leaving out a
healthy sensor barely moves the solution, leaving out the faulty one moves it a lot; after ``persist`` exceedances
the main filter becomes that sub-filter and a new bank is built. A floor ``separation_floor²·I`` is added to
``Pᵢ − P₀`` (an assumption, 0.5 m by default): a sensor that adds almost no position information (the baro, whose
bias is a state) has ``Pᵢ ≈ P₀``, and without the floor linearisation noise alone would trip the test.
The vertical protection level from the filter is ``K σ_z`` with ``K = Q⁻¹(P/2)``
(:func:`aerokit.approach.protection_level`).

**Guidance and flare.** Above the flare the vertical law and the L1 lateral law of
:func:`aerokit.approach.simulate_approach` act on the *estimated* position. The flare commands
``ḣ_c = −(h + h₀) / τ`` (an exponential flare whose asymptote lies ``h₀`` below the ground, so with an instant
sink response the wheels touch at ``h₀ / τ``; the first-order sink lag ``tau_sink`` makes the real touchdown sink
larger — about twice the target with the defaults, as the simulation shows). It starts at the height where the
command equals the path sink, ``h_f = V_s τ − h₀`` — continuity, no jump. The touchdown point, sink and lateral
offset are recorded; :func:`monte_carlo_autoland` gives their spread.

Concept-level: point-mass vehicle, perfect attitude from the INS for the lateral law, flat terrain, no ground effect.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from aerokit import approach as A

__all__ = ["GroundRadar", "FusionConfig", "AutolandConfig", "radar_measurement", "ApproachEKF", "flare_height",
           "AutolandRun", "simulate_autoland", "monte_carlo_autoland"]

G0 = 9.80665


@dataclass(frozen=True)
class GroundRadar:
    """Ground radar site (runway frame, m) and its measurement noise (range m, angles in degrees)."""

    position: tuple[float, float, float] = (-300.0, 150.0, 2.0)
    sigma_range: float = 3.0
    sigma_az_deg: float = 0.1
    sigma_el_deg: float = 0.1


@dataclass(frozen=True)
class FusionConfig:
    """Sensors of the fused navigation solution (SI). ``None`` disables a sensor."""

    gnss_sigma: tuple[float, float, float] | None = (1.0, 1.0, 1.5)
    gnss_ramp: tuple[float, float, float] = (0.0, 0.0, 0.0)
    gnss_ramp_start: float = math.inf
    radar: GroundRadar | None = field(default_factory=GroundRadar)
    baro_sigma: float | None = 2.0
    baro_bias: float = 0.0                  # true bias of the baro height [m] (+ = reads high)
    radalt_max_height: float = 762.0        # 2500 ft
    radalt_sigma_frac: float = 0.02
    radalt_sigma_min: float = 0.5
    accel_sigma: float = 0.3                # IMU acceleration noise [m/s²], also the process noise
    bias_walk: float = 0.01                 # baro-bias random walk [m/√s]
    alpha: float = 1e-4                     # χ² false-alarm probability per update
    persist: int = 3                        # consecutive exceedances before exclusion
    fde: bool = True
    fde_mode: str = "separation"            # "separation" (sub-filter bank) or "innovation" (per-sensor χ² gate)
    separation_floor: float = 0.5           # σ [m] added to the separation covariance (assumption, see docstring)


@dataclass(frozen=True)
class AutolandConfig:
    """Approach, flare and touchdown parameters (SI)."""

    x0: float = 6000.0
    y0: float = 0.0
    z0_above_path: float = 0.0
    tas: float = 70.0
    wind_from_rel_deg: float = 0.0
    wind_speed: float = 0.0
    gust_sigma: float = 0.0
    gust_tau: float = 5.0
    tau_gamma: float = 3.0
    k_vertical: float = 2.0
    l1_distance: float = 600.0
    max_bank_deg: float = 25.0
    flare_tau: float = 3.0
    touchdown_sink: float = 0.6             # target sink at touchdown [m/s] → h₀ = sink × τ
    tau_sink: float = 1.0                   # sink-rate response time in the flare
    touchdown_box: tuple[float, float] = (150.0, 900.0)   # touchdown distance past the threshold [m]
    touchdown_lateral: float = 10.0         # |y| allowed at touchdown [m]
    dt: float = 0.1


def radar_measurement(p: np.ndarray, site: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Range, azimuth, elevation [m, rad, rad] of position ``p`` from ``site`` and the 3 × 3 Jacobian d(r,az,el)/dp."""
    d = np.asarray(p, float)[:3] - np.asarray(site, float)
    rh2 = d[0] ** 2 + d[1] ** 2
    rh = math.sqrt(rh2)
    r = math.sqrt(rh2 + d[2] ** 2)
    if rh < 1e-6:
        raise ValueError("target straight above the radar: azimuth undefined")
    h = np.array([r, math.atan2(d[1], d[0]), math.atan2(d[2], rh)])
    H = np.array([d / r,
                  [-d[1] / rh2, d[0] / rh2, 0.0],
                  [-d[0] * d[2] / (r * r * rh), -d[1] * d[2] / (r * r * rh), rh / (r * r)]])
    return h, H


def flare_height(sink_on_path: float, flare_tau: float, touchdown_sink: float) -> float:
    """Height [m] where ``ḣ_c = −(h + h₀)/τ`` equals the path sink, ``h₀ = touchdown_sink · τ``."""
    if min(sink_on_path, flare_tau) <= 0 or not 0 <= touchdown_sink < sink_on_path:
        raise ValueError("need sink_on_path > touchdown_sink >= 0 and flare_tau > 0")
    return (sink_on_path - touchdown_sink) * flare_tau


class ApproachEKF:
    """Seven-state EKF ``[x, y, z, vx, vy, vz, b_baro]`` with per-sensor χ² FDE (see the module docstring)."""

    def __init__(self, x0: np.ndarray, P0: np.ndarray, cfg: FusionConfig) -> None:
        from scipy.stats import chi2

        self.x = np.asarray(x0, float).copy()
        self.P = np.asarray(P0, float).copy()
        if self.x.shape != (7,) or self.P.shape != (7, 7):
            raise ValueError("state must have 7 elements and P must be 7 x 7")
        self.cfg = cfg
        self.threshold = {k: float(chi2.isf(cfg.alpha, k)) for k in (1, 3)}
        self.strikes: dict[str, int] = {}
        self.excluded: dict[str, float] = {}
        self.t = 0.0

    def predict(self, accel: np.ndarray, dt: float) -> None:
        """Propagate with the measured acceleration over ``dt``."""
        F = np.eye(7)
        F[0:3, 3:6] = dt * np.eye(3)
        self.x[0:3] += self.x[3:6] * dt + 0.5 * np.asarray(accel) * dt * dt
        self.x[3:6] += np.asarray(accel) * dt
        q = self.cfg.accel_sigma ** 2
        G = np.vstack([0.5 * dt * dt * np.eye(3), dt * np.eye(3), np.zeros((1, 3))])
        Q = q * G @ G.T
        Q[6, 6] = self.cfg.bias_walk ** 2 * dt
        self.P = F @ self.P @ F.T + Q
        self.t += dt

    def update(self, name: str, z: np.ndarray, h: np.ndarray, H: np.ndarray, R: np.ndarray,
               wrap: Sequence[int] = (), gate: bool = True) -> float:
        """Measurement update unless ``name`` is excluded; returns the NIS (``nan`` if skipped).

        ``wrap`` lists innovation components that are angles (wrapped to ±π); ``gate=False`` skips the χ² test
        (the solution-separation bank tests whole solutions instead)."""
        if name in self.excluded:
            return math.nan
        nu = np.asarray(z, float) - np.asarray(h, float)
        for i in wrap:
            nu[i] = (nu[i] + math.pi) % (2 * math.pi) - math.pi
        S = H @ self.P @ H.T + R
        Si = np.linalg.inv(S)
        nis = float(nu @ Si @ nu)
        if gate and self.cfg.fde and nis > self.threshold[len(nu)]:
            self.strikes[name] = self.strikes.get(name, 0) + 1
            if self.strikes[name] >= self.cfg.persist:
                self.excluded[name] = self.t
            return nis                          # a suspect measurement is never used
        self.strikes[name] = 0
        K = self.P @ H.T @ Si
        self.x = self.x + K @ nu
        I_KH = np.eye(7) - K @ H
        self.P = I_KH @ self.P @ I_KH.T + K @ R @ K.T          # Joseph form
        return nis


@dataclass
class AutolandRun:
    """Histories of one simulated autoland (true and estimated positions, NIS per sensor) and its outcome."""

    t: np.ndarray
    true: np.ndarray            # (n, 3)
    est: np.ndarray             # (n, 3)
    sigma_z: np.ndarray
    nis: dict[str, np.ndarray]
    excluded: dict[str, float]
    flare_height: float
    touchdown_x: float          # distance past the threshold [m] (positive = beyond); nan = no touchdown
    touchdown_y: float
    touchdown_sink: float
    baro_bias_est: float
    in_box: bool


def _measurements(p: np.ndarray, t: float, fusion: FusionConfig, rng: np.random.Generator) -> dict[str, tuple]:
    """One epoch of noisy measurements of the true position ``p``: name → (z, R)."""
    out: dict[str, tuple] = {}
    if fusion.gnss_sigma is not None:
        s = np.array(fusion.gnss_sigma)
        ramp = np.array(fusion.gnss_ramp) * max(0.0, t - fusion.gnss_ramp_start)
        out["gnss"] = (p + ramp + s * rng.standard_normal(3), np.diag(s ** 2))
    if fusion.radar is not None:
        rd = fusion.radar
        sig = np.array([rd.sigma_range, math.radians(rd.sigma_az_deg), math.radians(rd.sigma_el_deg)])
        out["radar"] = (radar_measurement(p, rd.position)[0] + sig * rng.standard_normal(3), np.diag(sig ** 2))
    if fusion.baro_sigma is not None:
        out["baro"] = (np.array([p[2] + fusion.baro_bias + fusion.baro_sigma * rng.standard_normal()]),
                       np.array([[fusion.baro_sigma ** 2]]))
    if p[2] <= fusion.radalt_max_height:
        sr = max(fusion.radalt_sigma_min, fusion.radalt_sigma_frac * max(p[2], 0.0))
        out["radalt"] = (np.array([p[2] + sr * rng.standard_normal()]), np.array([[sr * sr]]))
    return out


def _update_all(ekf: ApproachEKF, meas: dict[str, tuple], skip: set[str], fusion: FusionConfig,
                gate: bool) -> dict[str, float]:
    """Apply every measurement not in ``skip``; returns the NIS per sensor."""
    nis = {}
    for name, (z, R) in meas.items():
        if name in skip:
            continue
        H = np.zeros((len(z), 7))
        wrap: tuple[int, ...] = ()
        if name == "gnss":
            H[:, 0:3] = np.eye(3)
            h = ekf.x[0:3].copy()
        elif name == "radar":
            if fusion.radar is None:
                raise ValueError("a radar measurement arrived but no radar is configured")
            h, H[:, 0:3] = radar_measurement(ekf.x[0:3], fusion.radar.position)
            wrap = (1, 2)
        elif name == "baro":
            H[0, 2], H[0, 6] = 1.0, 1.0
            h = np.array([ekf.x[2] + ekf.x[6]])
        else:
            H[0, 2] = 1.0
            h = np.array([ekf.x[2]])
        nis[name] = ekf.update(name, z, h, H, R, wrap, gate=gate)
    return nis


def simulate_autoland(rwy: A.Runway, fusion: FusionConfig | None = None, cfg: AutolandConfig | None = None,
                      rng: np.random.Generator | None = None) -> AutolandRun:
    """Fly one fused-navigation approach to touchdown (see the module docstring)."""
    import copy

    from scipy.stats import chi2

    fusion = fusion or FusionConfig()
    cfg = cfg or AutolandConfig()
    rng = rng or np.random.default_rng()
    if fusion.fde_mode not in ("separation", "innovation"):
        raise ValueError("fde_mode must be 'separation' or 'innovation'")
    gam_ref = math.radians(rwy.glide_path_deg)
    rel = math.radians(cfg.wind_from_rel_deg)
    w_head, w_cross = cfg.wind_speed * math.cos(rel), cfg.wind_speed * math.sin(rel)
    x, y = cfg.x0, cfg.y0
    z = float(A.glide_path_height(rwy, x)) + cfg.z0_above_path
    psi = math.asin(max(-0.99, min(0.99, w_cross / cfg.tas)))
    gamma = gam_ref
    v = np.array([-(cfg.tas * math.cos(psi) - w_head), cfg.tas * math.sin(psi) - w_cross,
                  -(cfg.tas * math.cos(psi) - w_head) * math.tan(gamma)])
    sink_path = -v[2]
    h0 = cfg.touchdown_sink * cfg.flare_tau
    h_flare = flare_height(sink_path, cfg.flare_tau, cfg.touchdown_sink)
    main = ApproachEKF(np.array([x, y, z, *v, 0.0]), np.diag([25.0, 25.0, 25.0, 1.0, 1.0, 1.0, 100.0]), fusion)
    names = [n for n, on in (("gnss", fusion.gnss_sigma is not None), ("radar", fusion.radar is not None),
                             ("baro", fusion.baro_sigma is not None), ("radalt", True)) if on]
    separation = fusion.fde and fusion.fde_mode == "separation"
    excluded: dict[str, float] = {}
    subs = {n: copy.deepcopy(main) for n in names} if separation else {}
    strikes = dict.fromkeys(names, 0)
    ss_threshold = float(chi2.isf(fusion.alpha, 3))
    gust, sink = 0.0, sink_path
    a_g = math.exp(-cfg.dt / cfg.gust_tau)
    flaring = False
    T, TR, ES, SZ = [], [], [], []
    nis_hist: dict[str, list[float]] = {k: [] for k in ("gnss", "radar", "baro", "radalt")}
    t = 0.0
    for _ in range(int(20 * cfg.x0 / cfg.tas / cfg.dt) + 2000):
        p_true = np.array([x, y, z])
        v_old = v.copy()
        xh, yh, zh = main.x[0:3]
        if not flaring and zh <= h_flare:
            flaring = True
        gust = a_g * gust + math.sqrt(1 - a_g ** 2) * cfg.gust_sigma * rng.standard_normal()
        if flaring:
            sink_c = (zh + h0) / cfg.flare_tau
            sink += (sink_c - sink) * cfg.dt / cfg.tau_sink
        else:
            dz = zh - float(A.glide_path_height(rwy, xh))
            gamma_c = gam_ref + cfg.k_vertical * dz / max(xh - rwy.gpip, 200.0)
            gamma += (gamma_c - gamma) * cfg.dt / cfg.tau_gamma
        chi = math.atan2(v[1], -v[0])
        gs_h = math.hypot(v[0], v[1])
        eta = math.atan2(-yh, cfg.l1_distance) - chi
        a_lat = 2 * gs_h ** 2 * math.sin(eta) / cfg.l1_distance
        bank = max(-math.radians(cfg.max_bank_deg), min(math.radians(cfg.max_bank_deg), math.atan(a_lat / G0)))
        psi += G0 * math.tan(bank) / cfg.tas * cfg.dt
        gs_along = cfg.tas * math.cos(psi) - (w_head + gust)
        v = np.array([-gs_along, cfg.tas * math.sin(psi) - w_cross,
                      -sink if flaring else -gs_along * math.tan(gamma)])
        if not flaring:
            sink = -v[2]
        x, y, z = p_true + 0.5 * (v_old + v) * cfg.dt
        t += cfg.dt
        accel = (v - v_old) / cfg.dt + rng.normal(0.0, fusion.accel_sigma, 3)
        meas = _measurements(np.array([x, y, z]), t, fusion, rng)
        main.predict(accel, cfg.dt)
        rec = _update_all(main, meas, set(excluded), fusion, gate=fusion.fde and not separation)
        if not separation:
            excluded.update(main.excluded)
        for n, sub in subs.items():
            sub.predict(accel, cfg.dt)
            _update_all(sub, meas, set(excluded) | {n}, fusion, gate=False)
        # solution separation: excluding a healthy sensor barely moves the solution; excluding the faulty one does
        hit = None
        for n, sub in subs.items():
            d = main.x[0:3] - sub.x[0:3]
            Sd = sub.P[0:3, 0:3] - main.P[0:3, 0:3] + fusion.separation_floor ** 2 * np.eye(3)
            stat = float(d @ np.linalg.solve(Sd, d))
            strikes[n] = strikes[n] + 1 if stat > ss_threshold else 0
            if strikes[n] >= fusion.persist and (hit is None or stat > hit[1]):
                hit = (n, stat)
        if hit is not None:
            n = hit[0]
            excluded[n] = t
            main = subs[n]
            main.excluded = dict(excluded)
            subs = {m: copy.deepcopy(main) for m in names if m not in excluded}
            strikes = dict.fromkeys(names, 0)
        T.append(t)
        TR.append((x, y, z))
        ES.append(tuple(main.x[0:3]))
        SZ.append(math.sqrt(main.P[2, 2]))
        for k in nis_hist:
            nis_hist[k].append(rec.get(k, math.nan))
        if z <= 0.0:
            break
    landed = z <= 0.0                       # False: the aircraft never reached the ground (e.g. dragged high)
    td_x = -x if landed else math.nan
    lo, hi = cfg.touchdown_box
    return AutolandRun(np.array(T), np.array(TR), np.array(ES), np.array(SZ),
                       {k: np.array(vv) for k, vv in nis_hist.items()}, dict(excluded), h_flare, td_x, y, sink,
                       float(main.x[6]), bool(landed and lo <= td_x <= hi and abs(y) <= cfg.touchdown_lateral))


def monte_carlo_autoland(rwy: A.Runway, fusion: FusionConfig | None = None, cfg: AutolandConfig | None = None,
                         runs: int = 100, seed: int = 1) -> dict[str, float]:
    """Touchdown statistics over ``runs`` approaches: mean and σ of distance, |y| P95, sink mean and max, share
    inside the touchdown box, and the share of runs that excluded each sensor."""
    rng = np.random.default_rng(seed)
    out = [simulate_autoland(rwy, fusion, cfg, rng) for _ in range(runs)]
    landed = [r for r in out if np.isfinite(r.touchdown_x)]
    tx = np.array([r.touchdown_x for r in landed])
    ty = np.array([r.touchdown_y for r in landed])
    ts = np.array([r.touchdown_sink for r in landed])
    nan = math.nan
    res = {"runs": float(runs), "landed_share": len(landed) / runs,
           "touchdown_mean_m": float(tx.mean()) if tx.size else nan,
           "touchdown_sigma_m": float(tx.std(ddof=1)) if tx.size > 1 else nan,
           "lateral_p95_m": float(np.percentile(np.abs(ty), 95)) if ty.size else nan,
           "sink_mean_ms": float(ts.mean()) if ts.size else nan, "sink_max_ms": float(ts.max()) if ts.size else nan,
           "in_box_share": float(np.mean([r.in_box for r in out]))}
    for k in ("gnss", "radar", "baro", "radalt"):
        res[f"excluded_{k}_share"] = float(np.mean([k in r.excluded for r in out]))
    return res
