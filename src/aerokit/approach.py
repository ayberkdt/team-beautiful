"""Approach guidance geometry, stabilised-approach checks and a Monte-Carlo approach simulator.

**Runway frame.** :class:`Runway` puts the origin at the landing threshold (``LocalFrame`` from
``aerokit.mission.geodesy``, exact via ECEF, so the Earth's curvature is in the "up" coordinate). ``x`` is the
distance *before* the threshold along the extended centreline (positive on the approach side), ``y`` the
cross-track offset (positive right of the centreline looking towards the runway), ``z`` the height above the
threshold's tangent plane. The final approach path is a straight line in space through the glide-path intercept
point (GPIP) ``x = −TCH / tan γ`` (it crosses the threshold at the threshold crossing height TCH).

**Deviations.** Angular vertical deviation ``atan2(z, x − x_GPIP) − γ`` (like an ILS glide-path receiver), linear
vertical deviation ``z − (TCH + x tan γ)`` (like LPV/baro-VNAV close in), angular lateral deviation from a
localizer at ``x = −(L_rwy + setback)`` and linear cross-track ``y``. Conversion to display "dots" takes the
full-scale value as an explicit parameter; no ILS/LPV sensitivity is hard-coded here.

**Wind triangle and descent rate.** Crab angle ``asin(w_⊥ / V_TAS)``, ground speed
``V cos(crab) − w_∥``; the vertical speed on a path of angle ``γ`` is ``GS · tan γ``.

**Cold-temperature error of a barometric altimeter.** The altimeter converts pressure to height with the ISA
temperature. In a column ``ΔT`` warmer than ISA the hypsometric equation ``dz = (R T / g) dp / p`` stretches every
layer by ``T / T_ISA``; the true height above the station is ``∫ (T_ISA(z') + ΔT) / T_ISA(z') dz'`` over the
indicated height (derived here; constant ``ΔT`` with height assumed). Cold air ⇒ the aircraft is *lower* than
indicated, which matters for baro-VNAV approaches.

**Simulator.** :func:`simulate_approach` flies a point mass down the path with a first-order flight-path response,
an L1 lateral guidance law on the ground track (Park, Deyst & How 2004), a vertical law on the *sensed* linear
deviation with a ground-referenced path angle (as a VNAV path is flown), wind with a
Gauss–Markov gust, and a navigation-sensor model (bias + Gauss–Markov noise) given per axis. It is a concept-level
tool to compare sensor suites and gains by their deviation at a decision height, not an aircraft model. A sensor
can carry a slow error ramp from a given time (a spoofing drift), and an independent *monitor* sensor can be flown
alongside: when the primary and monitor positions separate by more than a threshold on any axis, the run raises an
alarm and guidance switches to the monitor (detect and exclude).

**Integrity.** A protection level bounds the position error at an integrity risk ``P``: ``PL = K σ`` with the
two-sided Gaussian factor ``K = Q⁻¹(P/2)`` (``P = 10⁻⁷`` gives the SBAS ``K_v = 5.33``, Rippl & Perea 2018).
A two-source solution-separation monitor uses the threshold ``T = Q⁻¹(P_FA/2) √(σ_a² + σ_b²)``; with a faulted
source the error that can go undetected is bounded by ``T + Q⁻¹(P_MD) σ`` (single fault, two sources — a
simplified form of the solution-separation protection level). Alert limits of the GNSS approach services are in
:data:`ALERT_LIMITS`.

**RF sensor physics.** One-way link budget (Friis) for a cooperative transponder reply, and monopulse angle noise
``σ_θ ≈ θ_3dB / (k_m √(2 SNR))``.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import ArrayLike

from aerokit.aero.atmosphere import isa
from aerokit.mission.geodesy import LocalFrame
from aerokit.references import cite

__all__ = ["FT", "KT", "FPM", "Runway", "PathDeviation", "glide_path_height", "deviation", "to_dots",
           "wind_triangle", "descent_rate", "distance_for_descent", "cold_temperature_true_height",
           "StabilityCriteria", "stability_violations", "NavSensor", "ApproachSimConfig", "ApproachRun",
           "simulate_approach", "monte_carlo_approach", "ALERT_LIMITS", "k_factor", "protection_level",
           "separation_threshold", "fault_bound", "friis_received_power", "thermal_noise_power",
           "monopulse_angle_sigma"]

FT = 0.3048
KT = 1852.0 / 3600.0
FPM = FT / 60.0
G0 = 9.80665


@dataclass(frozen=True)
class Runway:
    """Landing runway: threshold position, true course, length, glide path angle and TCH (SI, degrees)."""

    lat: float
    lon: float
    elevation: float
    course_deg: float
    length: float = 2500.0
    glide_path_deg: float = 3.0
    tch: float = 15.24                # 50 ft
    localizer_setback: float = 300.0  # beyond the stop end

    def __post_init__(self) -> None:
        if not 0 < self.glide_path_deg < 15:
            raise ValueError("glide path angle must be in (0, 15) deg")
        if self.length <= 0 or self.tch < 0:
            raise ValueError("runway length must be > 0 and TCH >= 0")

    @property
    def frame(self) -> LocalFrame:
        return LocalFrame(self.lat, self.lon, self.elevation)

    @property
    def gpip(self) -> float:
        """Along-track coordinate of the glide-path intercept point [m] (negative: beyond the threshold)."""
        return -self.tch / math.tan(math.radians(self.glide_path_deg))

    def to_runway(self, lat: ArrayLike, lon: ArrayLike, h: ArrayLike) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Geodetic (deg, deg, m above the ellipsoid as the threshold elevation) → runway (x, y, z) [m]."""
        e, n, u = self.frame.to_enu(lat, lon, h)
        c = math.radians(self.course_deg)
        along = e * math.sin(c) + n * math.cos(c)        # positive towards the runway direction
        right = e * math.cos(c) - n * math.sin(c)
        return -along, right, u

    def from_runway(self, x: ArrayLike, y: ArrayLike, z: ArrayLike) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Runway (x, y, z) → geodetic (lat, lon, h)."""
        c = math.radians(self.course_deg)
        along, right = -np.asarray(x, float), np.asarray(y, float)
        e = along * math.sin(c) + right * math.cos(c)
        n = along * math.cos(c) - right * math.sin(c)
        return self.frame.to_geodetic(e, n, z)


@dataclass(frozen=True)
class PathDeviation:
    """Deviations from the final approach path (positive = above / right)."""

    x: np.ndarray
    vertical_angle_deg: np.ndarray
    vertical_m: np.ndarray
    lateral_angle_deg: np.ndarray
    lateral_m: np.ndarray


def glide_path_height(rwy: Runway, x: ArrayLike) -> np.ndarray:
    """Height of the nominal path above the threshold plane at along-track ``x`` [m]: ``TCH + x tan γ``."""
    return rwy.tch + np.asarray(x, float) * math.tan(math.radians(rwy.glide_path_deg))


def deviation(rwy: Runway, x: ArrayLike, y: ArrayLike, z: ArrayLike) -> PathDeviation:
    """Angular and linear deviations of points given in runway coordinates."""
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    gam = math.radians(rwy.glide_path_deg)
    v_ang = np.degrees(np.arctan2(z, x - rwy.gpip) - gam)
    l_ang = np.degrees(np.arctan2(y, x + rwy.length + rwy.localizer_setback))
    return PathDeviation(x, v_ang, z - glide_path_height(rwy, x), l_ang, y)


def to_dots(deviation_value: ArrayLike, full_scale: float, dots_full_scale: float = 2.0) -> np.ndarray:
    """Scale a deviation to display dots, given the deviation at full scale (clipped at ±full scale)."""
    if full_scale <= 0 or dots_full_scale <= 0:
        raise ValueError("full scale and dots must be > 0")
    return np.clip(np.asarray(deviation_value, float) / full_scale, -1.0, 1.0) * dots_full_scale


def wind_triangle(tas: float, course_deg: float, wind_from_deg: float, wind_speed: float) -> tuple[float, float, float]:
    """Crab angle [deg, + = nose right of course], ground speed [m/s] and headwind component [m/s]."""
    if tas <= 0 or wind_speed < 0:
        raise ValueError("TAS must be > 0 and wind speed >= 0")
    rel = math.radians(wind_from_deg - course_deg)
    head = wind_speed * math.cos(rel)
    cross = wind_speed * math.sin(rel)                  # + from the right
    if abs(cross) >= tas:
        raise ValueError("crosswind exceeds the true airspeed")
    crab = math.asin(cross / tas)
    return math.degrees(crab), tas * math.cos(crab) - head, head


def descent_rate(ground_speed: float, path_deg: float) -> float:
    """Vertical speed [m/s] to stay on a path of angle ``path_deg`` at ``ground_speed``."""
    return ground_speed * math.tan(math.radians(path_deg))


def distance_for_descent(height_loss: float, path_deg: float) -> float:
    """Ground distance [m] to lose ``height_loss`` on a path of angle ``path_deg`` (e.g. CDA planning)."""
    if height_loss < 0 or not 0 < path_deg < 90:
        raise ValueError("height loss must be >= 0 and the angle in (0, 90) deg")
    return height_loss / math.tan(math.radians(path_deg))


@cite("hypsometric_equation", "iso_2533_1975", note="layer thickness scales with T/T_ISA at equal pressures")
def cold_temperature_true_height(indicated_height: float, station_elevation: float, isa_deviation_K: float,
                                 n: int = 400) -> float:
    """True height [m] above an altimeter-setting station for an indicated height above it, in a column
    ``isa_deviation_K`` off ISA (negative = cold; the aircraft is then below the indicated height)."""
    if indicated_height < 0 or station_elevation < 0 or n < 2:
        raise ValueError("heights must be >= 0 and n >= 2")
    zs = np.linspace(station_elevation, station_elevation + indicated_height, n)
    T_isa = np.array([isa(float(z))["T"] for z in zs])
    if np.any(T_isa + isa_deviation_K <= 0):
        raise ValueError("temperature deviation gives a non-physical temperature")
    return float(np.trapezoid((T_isa + isa_deviation_K) / T_isa, zs))


@dataclass(frozen=True)
class StabilityCriteria:
    """Stabilised-approach gate of FSF ALAR Briefing Note 7.1: stable by 1000 ft above airport elevation in IMC
    (500 ft in VMC); speed between VREF and VREF + 20 kt IAS; sink rate ≤ 1000 fpm; ILS within one dot of
    glideslope and localizer. Speeds here are *above VREF*. Airlines often use tighter SOP values."""

    gate_height: float = 1000 * FT
    speed_low: float = 0.0
    speed_high: float = 20 * KT
    max_sink_rate: float = 1000 * FPM
    max_vertical_dots: float = 1.0
    max_lateral_dots: float = 1.0


@cite("fsf_alar_bn71_2009", note="Recommended Elements of a Stabilized Approach, criteria 1-8")
def stability_violations(height: Sequence[float], speed_above_vref: Sequence[float], sink_rate: Sequence[float],
                         vertical_dots: Sequence[float], lateral_dots: Sequence[float],
                         criteria: StabilityCriteria | None = None) -> list[tuple[int, str]]:
    """Samples below the gate that break a criterion: list of (index, reason). Empty list = stabilised."""
    criteria = criteria or StabilityCriteria()
    arrays = [np.asarray(a, float) for a in (height, speed_above_vref, sink_rate, vertical_dots, lateral_dots)]
    if len({a.size for a in arrays}) != 1:
        raise ValueError("all series must have the same length")
    h, dv, vs, vd, ld = arrays
    out: list[tuple[int, str]] = []
    for i in np.flatnonzero(h <= criteria.gate_height):
        if not criteria.speed_low <= dv[i] <= criteria.speed_high:
            out.append((int(i), f"speed VREF{dv[i] / KT:+.1f} kt"))
        if vs[i] > criteria.max_sink_rate:
            out.append((int(i), f"sink rate {vs[i] / FPM:.0f} fpm"))
        if abs(vd[i]) > criteria.max_vertical_dots:
            out.append((int(i), f"vertical deviation {vd[i]:+.2f} dot"))
        if abs(ld[i]) > criteria.max_lateral_dots:
            out.append((int(i), f"lateral deviation {ld[i]:+.2f} dot"))
    return out


# ----------------------------------------------------------------------------- simulator
@dataclass(frozen=True)
class NavSensor:
    """Position-error model per axis (along, cross, vertical) [m]: constant bias + first-order Gauss–Markov
    noise with standard deviation ``sigma`` and correlation time ``tau`` [s], plus an error growing at ``ramp``
    [m/s] from time ``ramp_start`` [s] (a spoofing or drift fault; none by default). ``name`` is a label."""

    name: str
    bias: tuple[float, float, float] = (0.0, 0.0, 0.0)
    sigma: tuple[float, float, float] = (0.0, 0.0, 0.0)
    tau: float = 30.0
    ramp: tuple[float, float, float] = (0.0, 0.0, 0.0)
    ramp_start: float = math.inf

    def fault(self, t: float) -> np.ndarray:
        """Ramp error vector at time ``t``."""
        return np.array(self.ramp) * max(0.0, t - self.ramp_start)


@dataclass(frozen=True)
class ApproachSimConfig:
    """Initial state, aircraft response and guidance gains of :func:`simulate_approach` (SI)."""

    x0: float = 10 * 1852.0
    y0: float = 0.0
    z0_above_path: float = 0.0
    tas: float = 70.0
    wind_from_rel_deg: float = 0.0      # wind direction relative to the runway course
    wind_speed: float = 0.0
    gust_sigma: float = 0.0
    gust_tau: float = 5.0
    tau_gamma: float = 3.0              # flight-path response time constant
    tau_heading: float = 4.0
    k_vertical: float = 2.0             # γ_c − γ_ref = k · (sensed deviation) / (distance to go)
    l1_distance: float = 600.0
    max_bank_deg: float = 25.0
    dt: float = 0.1
    stop_height: float = 0.0


@dataclass
class ApproachRun:
    """Time histories (true state) of one simulated approach."""

    t: np.ndarray
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    vertical_dev: np.ndarray
    lateral_dev: np.ndarray
    sink_rate: np.ndarray
    extra: dict[str, float] = field(default_factory=dict)

    def at_height(self, height: float) -> tuple[float, float]:
        """(vertical, lateral) true deviation [m] when the aircraft first descends through ``height``."""
        idx = np.flatnonzero(self.z <= height)
        if idx.size == 0:
            raise ValueError("the run never reached that height")
        i = int(idx[0])
        return float(self.vertical_dev[i]), float(self.lateral_dev[i])


@cite("park_deyst_how_2004", note="lateral acceleration a = 2 V² sin(η) / L1; bank = atan(a/g)")
def simulate_approach(rwy: Runway, sensor: NavSensor, cfg: ApproachSimConfig | None = None,
                      rng: np.random.Generator | None = None, monitor: NavSensor | None = None,
                      threshold: tuple[float, float, float] | None = None) -> ApproachRun:
    """Fly one approach from ``cfg.x0`` down to ``cfg.stop_height`` using *sensed* position for guidance.

    Vertical law: commanded path angle ``γ_c = γ_ref + k · ẑ_dev / max(x̂ − x_GPIP, 200 m)`` (radians, path
    angle positive downwards, ``ẑ_dev`` the sensed linear deviation, positive above): with ``k = 2`` the aircraft
    aims to cancel its deviation over half the remaining distance, a law that stiffens towards the runway.
    Lateral law: L1 to the extended centreline on the ground track. Both are concept-level; tune the gains and
    response times for the vehicle studied.

    With ``monitor`` and ``threshold`` (per axis along, cross, vertical [m]) the run compares both sensed positions
    every step; the first exceedance sets ``extra["alarm_t"]``, ``extra["alarm_height"]`` and
    ``extra["undetected_error"]`` (largest primary cross/vertical error before the alarm) and guidance continues
    on the monitor. Without an alarm, ``extra["undetected_error"]`` is the largest primary error of the run.
    """
    cfg = cfg or ApproachSimConfig()
    rng = rng or np.random.default_rng()
    gam_ref = math.radians(rwy.glide_path_deg)
    x, y = cfg.x0, cfg.y0
    z = float(glide_path_height(rwy, x)) + cfg.z0_above_path
    rel = math.radians(cfg.wind_from_rel_deg)
    w_head, w_cross = cfg.wind_speed * math.cos(rel), cfg.wind_speed * math.sin(rel)
    gamma = gam_ref                           # ground path angle, positive downwards
    psi = math.asin(max(-0.99, min(0.99, w_cross / cfg.tas)))   # start crabbed into the wind (+ = right)
    gs_along, gs_cross = cfg.tas * math.cos(psi) - w_head, cfg.tas * math.sin(psi) - w_cross
    nav: np.ndarray = np.zeros(3)
    gust = 0.0
    a_nav = math.exp(-cfg.dt / sensor.tau)
    a_g = math.exp(-cfg.dt / cfg.gust_tau)
    sig = np.array(sensor.sigma)
    if (monitor is None) != (threshold is None):
        raise ValueError("give both monitor and threshold, or neither")
    nav_m: np.ndarray = np.zeros(3)
    a_mon = math.exp(-cfg.dt / monitor.tau) if monitor else 0.0
    sig_m = np.array(monitor.sigma) if monitor else np.zeros(3)
    thr = np.array(threshold) if threshold is not None else np.full(3, np.inf)
    alarm = False
    worst = 0.0
    extra: dict[str, float] = {}
    ts, xs, ys, zs, vs = [], [], [], [], []
    t = 0.0
    max_steps = int(10 * cfg.x0 / max(cfg.tas, 1.0) / cfg.dt) + 1000
    for _ in range(max_steps):
        if z <= cfg.stop_height or x <= rwy.gpip:
            break
        nav = a_nav * nav + math.sqrt(1 - a_nav ** 2) * sig * rng.standard_normal(3)
        gust = a_g * gust + math.sqrt(1 - a_g ** 2) * cfg.gust_sigma * rng.standard_normal()
        err = np.array(sensor.bias) + nav + sensor.fault(t)
        sensed = np.array([x, y, z]) + err
        if monitor is not None:
            nav_m = a_mon * nav_m + math.sqrt(1 - a_mon ** 2) * sig_m * rng.standard_normal(3)
            sensed_m = np.array([x, y, z]) + np.array(monitor.bias) + nav_m + monitor.fault(t)
            if not alarm and np.any(np.abs(sensed - sensed_m) > thr):
                alarm = True
                extra.update(alarm_t=t, alarm_height=z, undetected_error=worst)
            if alarm:
                sensed = sensed_m
        if not alarm:
            worst = max(worst, float(np.max(np.abs(err[1:]))))
        xh, yh, zh = sensed
        dz = zh - float(glide_path_height(rwy, xh))
        gamma_c = gam_ref + cfg.k_vertical * dz / max(xh - rwy.gpip, 200.0)
        gamma += (gamma_c - gamma) * cfg.dt / cfg.tau_gamma
        # L1 lateral guidance on the ground track towards a point L1 ahead on the centreline
        chi = math.atan2(gs_cross, gs_along)
        gs_h = math.hypot(gs_along, gs_cross)
        eta = math.atan2(-yh, cfg.l1_distance) - chi
        a_lat = 2 * gs_h ** 2 * math.sin(eta) / cfg.l1_distance
        bank = max(-math.radians(cfg.max_bank_deg), min(math.radians(cfg.max_bank_deg), math.atan(a_lat / G0)))
        psi += G0 * math.tan(bank) / cfg.tas * cfg.dt
        gs_along = cfg.tas * math.cos(psi) - (w_head + gust)
        gs_cross = cfg.tas * math.sin(psi) - w_cross
        x -= gs_along * cfg.dt
        y += gs_cross * cfg.dt
        sink = gs_along * math.tan(gamma)          # ground-referenced flight path angle (VNAV-like)
        z -= sink * cfg.dt
        t += cfg.dt
        ts.append(t)
        xs.append(x)
        ys.append(y)
        zs.append(z)
        vs.append(sink)
    X, Y, Z = np.array(xs), np.array(ys), np.array(zs)
    extra.setdefault("undetected_error", worst)
    return ApproachRun(np.array(ts), X, Y, Z, np.asarray(Z - glide_path_height(rwy, X)), Y, np.array(vs), extra)


def monte_carlo_approach(rwy: Runway, sensors: Mapping[str, NavSensor] | Sequence[NavSensor],
                         gate_height: float = 200 * FT, runs: int = 200,
                         cfg: ApproachSimConfig | None = None, seed: int = 1) -> dict[str, dict[str, float]]:
    """Deviation statistics at ``gate_height`` per sensor suite: mean and 95th-percentile |deviation| [m]."""
    items = sensors.items() if isinstance(sensors, Mapping) else ((s.name, s) for s in sensors)
    out: dict[str, dict[str, float]] = {}
    for name, s in items:
        rng = np.random.default_rng(seed)
        v, lat = [], []
        for _ in range(runs):
            dv, dl = simulate_approach(rwy, s, cfg, rng).at_height(gate_height)
            v.append(dv)
            lat.append(dl)
        V, L = np.array(v), np.array(lat)
        out[name] = {"vertical_mean": float(V.mean()), "vertical_p95_abs": float(np.percentile(np.abs(V), 95)),
                     "lateral_mean": float(L.mean()), "lateral_p95_abs": float(np.percentile(np.abs(L), 95)),
                     "runs": float(runs)}
    return out


# ----------------------------------------------------------------------------- integrity
ALERT_LIMITS: dict[str, tuple[float, float]] = {
    "LPV-200": (40.0, 35.0),
    "APV-I": (40.0, 50.0),
    "APV-II": (40.0, 20.0),
}
"""(horizontal, vertical) alert limits [m]. LPV-200 from the EGNOS availability definition (HPL < 40 m and
VPL < 35 m, read by the research agent); APV-I/II from a secondary transcription of ICAO Annex 10 (search summary
only — Annex 10 itself not read)."""


def k_factor(integrity_risk: float) -> float:
    """Two-sided Gaussian multiplier ``Q⁻¹(P/2)``: the bound exceeded with probability ``P``."""
    from scipy.stats import norm

    if not 0 < integrity_risk < 1:
        raise ValueError("integrity risk must be in (0, 1)")
    return float(norm.isf(integrity_risk / 2))


@cite("rippl_perea_2018", note="K_v,SBAS = Q^-1(0.5 P_HMI) = 5.33 for P_HMI = 1e-7")
def protection_level(sigma: float, integrity_risk: float = 1e-7) -> float:
    """Fault-free protection level ``K σ`` [m] for a Gaussian error of standard deviation ``sigma``."""
    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    return k_factor(integrity_risk) * sigma


def separation_threshold(sigma_a: float, sigma_b: float, p_false_alert: float = 1e-5) -> float:
    """Detection threshold [m] on the difference of two independent position estimates so that, fault-free, the
    monitor alarms with probability ``p_false_alert`` per independent sample."""
    if sigma_a < 0 or sigma_b < 0:
        raise ValueError("sigmas must be >= 0")
    return k_factor(p_false_alert) * math.hypot(sigma_a, sigma_b)


def fault_bound(threshold: float, sigma: float, p_missed_detection: float = 1e-3) -> float:
    """Largest error [m] of a faulted source that stays undetected with probability ``1 − P_MD``: ``T + K_MD σ``
    with the one-sided ``K_MD = Q⁻¹(P_MD)`` and ``σ`` the standard deviation of the separation statistic
    (simplified single-fault, two-source form)."""
    from scipy.stats import norm

    if threshold < 0 or sigma < 0 or not 0 < p_missed_detection < 1:
        raise ValueError("threshold, sigma >= 0 and P_MD in (0, 1)")
    return threshold + float(norm.isf(p_missed_detection)) * sigma


# ----------------------------------------------------------------------------- RF sensor physics
@cite("friis_1946", note="one-way free-space link: P_r = P_t G_t G_r (lambda / 4 pi R)^2")
def friis_received_power(p_tx_w: float, gain_tx_dbi: float, gain_rx_dbi: float, frequency_hz: float,
                         range_m: float, losses_db: float = 0.0) -> float:
    """Received power [W] of a one-way free-space link (a transponder reply to a ground sensor)."""
    if min(p_tx_w, frequency_hz, range_m) <= 0:
        raise ValueError("power, frequency and range must be > 0")
    lam = 299_792_458.0 / frequency_hz
    g = 10 ** ((gain_tx_dbi + gain_rx_dbi - losses_db) / 10)
    return p_tx_w * g * (lam / (4 * math.pi * range_m)) ** 2


def thermal_noise_power(bandwidth_hz: float, noise_figure_db: float, temperature_K: float = 290.0) -> float:
    """Receiver noise power ``k T B F`` [W]."""
    if bandwidth_hz <= 0 or temperature_K <= 0:
        raise ValueError("bandwidth and temperature must be > 0")
    return 1.380649e-23 * temperature_K * bandwidth_hz * 10 ** (noise_figure_db / 10)


@cite("monopulse_accuracy", note="sigma_theta ~ theta_3dB / (k_m sqrt(2 SNR)); k_m typically 1.5-1.8")
def monopulse_angle_sigma(beamwidth_deg: float, snr_linear: float, k_m: float = 1.6) -> float:
    """Thermal-noise angle standard deviation [deg] of a monopulse measurement (single pulse/dwell; average over
    ``n`` independent samples by dividing by ``√n``). Multipath near the ground is *not* included."""
    if beamwidth_deg <= 0 or snr_linear <= 0 or k_m <= 0:
        raise ValueError("beamwidth, SNR and k_m must be > 0")
    return beamwidth_deg / (k_m * math.sqrt(2 * snr_linear))
