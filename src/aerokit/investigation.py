"""Accident-investigation toolkit: flight-path reconstruction, energy state, debris ballistics, search areas,
flight-data exceedance events and the HFACS taxonomy.

* :func:`reconstruct_track` — from time-stamped positions (ADS-B, radar, GNSS log, FDR lat/lon/alt) to ground
  speed, track, vertical speed, longitudinal acceleration, turn rate, an estimated bank angle and load factor.
  Positions go to a local east-north-up frame (``aerokit.mission.geodesy.LocalFrame``) and are smoothed and
  differentiated with a Savitzky–Golay filter. Bank assumes a coordinated turn, ``tan φ = V ω / g``; the load
  factor is ``√((V ω / g)² + (1 + ḣ̇/g)²)`` with the vertical acceleration from the second derivative of height.
  Wind is not separated (the speeds are ground-referenced) unless a wind is supplied.
* :func:`energy_state` — specific energy height ``E_s = h + V²/(2g)`` and specific excess power ``P_s = dE_s/dt``.
  A falling ``E_s`` with full power, or ``V`` traded for ``h`` near the stall, is the usual story of a LOC-I.
* :func:`ballistic_trajectory`, :func:`debris_footprint`, :func:`locate_breakup` — point-mass fall of a fragment
  with ballistic coefficient ``β = m / (C_D A)`` [kg/m²] in the ISA with a horizontal wind,
  ``a = −g ẑ − (ρ |v_rel| / (2β)) v_rel``. Light fragments drift with the wind and land early on the track;
  dense ones carry on along the flight path. :func:`locate_breakup` inverts the footprint: given where
  fragments of known (estimated) β were found, it finds the break-up position by least squares.
* :func:`containment_radius` — radius holding probability ``P`` of a circular Gaussian position error,
  ``σ √(−2 ln(1 − P))`` (Rayleigh distribution), and :func:`glide_reach` for an engine-out search circle.
* :func:`exceedance_events` — FDM-style events: contiguous runs where a parameter crosses a limit for longer
  than a minimum duration, optionally only inside a height band.
* :data:`HFACS` — the four HFACS levels with their categories, for structuring the human-factors analysis.
* :func:`ercs_score` — EASA's European Risk Classification Scheme (Reg. (EU) 2020/2034): severity letter from
  the key risk area and potential loss of life, barrier score from the weights of the barriers that stopped or
  remained, colour band and numerical equivalent for aggregation.
* :func:`accelerate_stop_distance`, :func:`takeoff_acceleration_monitor` — take-off-roll arithmetic for wrong
  surface / erroneous take-off parameter cases: distance used by an accelerate-then-reject, and the first time a
  measured acceleration falls below a fraction of the expected one (the idea behind take-off monitoring systems).
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from aerokit.aero.atmosphere import isa
from aerokit.mission.geodesy import LocalFrame
from aerokit.references import cite

__all__ = ["G0", "TrackReconstruction", "reconstruct_track", "energy_state", "BallisticResult",
           "ballistic_trajectory", "debris_footprint", "locate_breakup", "containment_radius", "glide_reach",
           "mean_deceleration_g", "Event", "exceedance_events", "HFACS", "hfacs_table", "ERCS_SEVERITY",
           "ERCS_KEY_RISK_AREAS", "ERCS_BARRIERS", "ErcsResult", "ercs_score", "accelerate_stop_distance",
           "takeoff_acceleration_monitor"]

G0 = 9.80665


def _rho(h: float) -> float:
    return isa(min(max(h, 0.0), 20000.0))["rho"]


@dataclass(frozen=True)
class TrackReconstruction:
    """Smoothed kinematics of a reconstructed flight path (SI, angles in degrees, track from true north)."""

    t: np.ndarray
    east: np.ndarray
    north: np.ndarray
    height: np.ndarray
    ground_speed: np.ndarray
    track_deg: np.ndarray
    vertical_speed: np.ndarray
    accel_along: np.ndarray
    turn_rate_deg_s: np.ndarray
    bank_deg: np.ndarray
    load_factor: np.ndarray


@cite("savitzky_golay_1964", note="uniform resampling, then savgol_filter for smoothing and derivatives")
def reconstruct_track(t: ArrayLike, lat: ArrayLike, lon: ArrayLike, h: ArrayLike, *,
                      dt: float = 1.0, window_s: float = 9.0, polyorder: int = 3) -> TrackReconstruction:
    """Kinematics from time-stamped positions (irregular sampling allowed; it is resampled every ``dt``).

    ``window_s`` sets the smoothing window: longer = smoother but blunter manoeuvres. ADS-B position updates
    every ~0.5–1 s with ~10 m noise usually need 7–15 s.
    """
    from scipy.signal import savgol_filter

    ts = np.asarray(t, float)
    la, lo = np.asarray(lat, float), np.asarray(lon, float)
    if ts.size < 5 or np.any(np.diff(ts) <= 0):
        raise ValueError("need at least 5 samples with strictly increasing time")
    frame = LocalFrame(float(la[0]), float(lo[0]), 0.0)
    e, n, u = frame.to_enu(la, lo, h)
    tt = np.arange(ts[0], ts[-1] + 1e-9, dt)
    E, N, U = (np.interp(tt, ts, v) for v in (e, n, u))
    win = max(polyorder + 2, int(round(window_s / dt)) | 1)
    if win > tt.size:
        raise ValueError("record shorter than the smoothing window")

    def sg(v: np.ndarray, d: int = 0) -> np.ndarray:
        return savgol_filter(v, win, polyorder, deriv=d, delta=dt)

    Es, Ns, Us = sg(E), sg(N), sg(U)
    ve, vn, vu = sg(E, 1), sg(N, 1), sg(U, 1)
    ae, an, au = sg(E, 2), sg(N, 2), sg(U, 2)
    gs = np.hypot(ve, vn)
    safe = np.where(gs > 1e-6, gs, np.nan)
    track = np.degrees(np.arctan2(ve, vn)) % 360.0
    omega = (vn * ae - ve * an) / safe ** 2                     # rad/s, + = right (clockwise seen from above)
    a_along = (ve * ae + vn * an) / safe
    lateral = gs * omega / G0
    return TrackReconstruction(tt, Es, Ns, Us, gs, track, vu, a_along, np.degrees(omega),
                               np.degrees(np.arctan(lateral)), np.sqrt(lateral ** 2 + (1 + au / G0) ** 2))


def energy_state(t: ArrayLike, height: ArrayLike, speed: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    """Specific energy height ``h + V²/2g`` [m] and specific excess power ``dE_s/dt`` [m/s]."""
    ts, h, v = (np.asarray(a, float) for a in (t, height, speed))
    if not ts.size == h.size == v.size or ts.size < 2:
        raise ValueError("series must have equal length >= 2")
    es = h + v ** 2 / (2 * G0)
    return es, np.gradient(es, ts)


@dataclass(frozen=True)
class BallisticResult:
    """Trajectory of a falling fragment in the frame of the break-up point (x along the initial track)."""

    t: np.ndarray
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    impact_x: float
    impact_y: float
    time_of_fall: float
    impact_speed: float


def ballistic_trajectory(beta: float, h0: float, speed: float, flight_path_deg: float = 0.0,
                         wind_along: float = 0.0, wind_cross: float = 0.0, dt_max: float = 0.05,
                         max_time: float = 3600.0) -> BallisticResult:
    """Fall of a fragment of ballistic coefficient ``beta`` [kg/m²] from height ``h0`` [m] with initial
    ``speed`` along the track, climbing at ``flight_path_deg``; constant wind (to which it relaxes). RK4 with a step
    of at most ``dt_max`` and at most a fifth of the drag time constant ``2β / (ρ |v_rel|)``."""
    if beta <= 0 or h0 <= 0 or speed < 0 or dt_max <= 0:
        raise ValueError("beta, h0 and dt must be > 0 and speed >= 0")
    w = np.array([wind_along, wind_cross, 0.0])
    g = math.radians(flight_path_deg)
    s = np.array([0.0, 0.0, h0, speed * math.cos(g), 0.0, speed * math.sin(g)])

    def f(st: np.ndarray) -> np.ndarray:
        vrel = st[3:] - w
        k = _rho(st[2]) * np.linalg.norm(vrel) / (2 * beta)
        return np.concatenate([st[3:], -k * vrel - np.array([0.0, 0.0, G0])])

    T, X, Y, Z = [0.0], [s[0]], [s[1]], [s[2]]
    t = 0.0
    while s[2] > 0 and t < max_time:
        # the drag time constant 2β/(ρ|v_rel|) can be milliseconds for light fragments at speed: keep RK4 stable
        tau = 2 * beta / (_rho(s[2]) * max(float(np.linalg.norm(s[3:] - w)), 1e-9))
        dt = min(dt_max, 0.2 * tau)
        k1 = f(s)
        k2 = f(s + dt / 2 * k1)
        k3 = f(s + dt / 2 * k2)
        k4 = f(s + dt * k3)
        prev = s
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        if s[2] <= 0:                           # linear interpolation to the ground
            frac = prev[2] / (prev[2] - s[2])
            s = prev + frac * (s - prev)
            t = t - dt + frac * dt
        T.append(t)
        X.append(s[0])
        Y.append(s[1])
        Z.append(s[2])
    if s[2] > 0:
        raise ValueError("fragment did not reach the ground within max_time")
    return BallisticResult(np.array(T), np.array(X), np.array(Y), np.array(Z), float(s[0]), float(s[1]), t,
                           float(np.linalg.norm(s[3:])))


def debris_footprint(betas: ArrayLike, h0: float, speed: float, flight_path_deg: float = 0.0,
                     wind_along: float = 0.0, wind_cross: float = 0.0) -> np.ndarray:
    """Impact points ``[(β, x, y, t_fall, v_impact), …]`` for a set of ballistic coefficients."""
    rows = []
    for b in np.atleast_1d(np.asarray(betas, float)):
        r = ballistic_trajectory(float(b), h0, speed, flight_path_deg, wind_along, wind_cross)
        rows.append((b, r.impact_x, r.impact_y, r.time_of_fall, r.impact_speed))
    return np.array(rows)


def locate_breakup(found_east: ArrayLike, found_north: ArrayLike, betas: ArrayLike, h0: float,
                   speed: float, track_deg: float, wind_east: float = 0.0, wind_north: float = 0.0,
                   flight_path_deg: float = 0.0) -> tuple[float, float, float]:
    """Break-up position (east, north) [m] that best explains fragments found at the given local coordinates,
    each with an estimated β, for a known height, speed and track; returns (east, north, rms residual [m]).

    The footprint of a fragment is a translation of its impact offset, so the least-squares origin is the mean of
    (found − predicted offset): closed form, no iteration.
    """
    fe, fn, b = (np.asarray(a, float) for a in (found_east, found_north, betas))
    if not fe.size == fn.size == b.size or fe.size < 1:
        raise ValueError("need matching arrays with at least one fragment")
    c = math.radians(track_deg)
    ua = np.array([math.sin(c), math.cos(c)])            # along-track unit vector (east, north)
    uc = np.array([math.cos(c), -math.sin(c)])           # right of track
    w = np.array([wind_east, wind_north])
    fp = debris_footprint(b, h0, speed, flight_path_deg, float(w @ ua), float(w @ uc))
    off = np.outer(fp[:, 1], ua) + np.outer(fp[:, 2], uc)
    origins = np.column_stack([fe, fn]) - off
    o = origins.mean(axis=0)
    rms = float(np.sqrt(np.mean(np.sum((origins - o) ** 2, axis=1))))
    return float(o[0]), float(o[1]), rms


def containment_radius(sigma: float, probability: float) -> float:
    """Radius [m] containing ``probability`` of a circular Gaussian error with per-axis ``sigma`` (Rayleigh)."""
    if sigma < 0 or not 0 < probability < 1:
        raise ValueError("sigma must be >= 0 and probability in (0, 1)")
    return sigma * math.sqrt(-2.0 * math.log(1.0 - probability))


def glide_reach(height: float, LD: float, wind_speed: float = 0.0, airspeed: float | None = None) -> tuple[float,
                                                                                                          float]:
    """Engine-out still-air glide distance ``h · L/D`` [m] and the wind drift added over the glide time
    (needs the glide airspeed): the search circle is centred downwind by the drift."""
    if height < 0 or LD <= 0:
        raise ValueError("height must be >= 0 and L/D > 0")
    dist = height * LD
    drift = 0.0
    if airspeed:
        drift = wind_speed * dist / airspeed
    return dist, drift


def mean_deceleration_g(impact_speed: float, stopping_distance: float) -> float:
    """Mean deceleration [g] to stop from ``impact_speed`` over ``stopping_distance``: ``V²/(2 s g)``."""
    if impact_speed < 0 or stopping_distance <= 0:
        raise ValueError("speed must be >= 0 and distance > 0")
    return impact_speed ** 2 / (2 * stopping_distance * G0)


@dataclass(frozen=True)
class Event:
    """One exceedance: parameter name, start and end time, peak value."""

    name: str
    t_start: float
    t_end: float
    peak: float


def exceedance_events(t: ArrayLike, series: Mapping[str, ArrayLike],
                      rules: Sequence[tuple[str, str, Callable[[np.ndarray], np.ndarray], float]],
                      height: ArrayLike | None = None,
                      band: tuple[float, float] | None = None) -> list[Event]:
    """FDM events. ``rules`` = ``[(event name, series key, predicate on the array, minimum duration [s]), …]``;
    ``band`` (with ``height``) restricts the check to ``low ≤ h ≤ high``. Sorted by start time."""
    ts = np.asarray(t, float)
    mask_band: np.ndarray = np.ones(ts.size, dtype=np.bool_)
    if band is not None:
        if height is None:
            raise ValueError("a height band needs the height series")
        hh = np.asarray(height, float)
        mask_band = (hh >= band[0]) & (hh <= band[1])
    out: list[Event] = []
    for name, key, pred, min_dur in rules:
        v = np.asarray(series[key], float)
        if v.size != ts.size:
            raise ValueError(f"series {key!r} has the wrong length")
        m = pred(v) & mask_band
        edges = np.flatnonzero(np.diff(np.concatenate([[0], m.astype(int), [0]])))
        for s, e in zip(edges[::2], edges[1::2], strict=True):
            if ts[e - 1] - ts[s] >= min_dur:
                seg = v[s:e]
                out.append(Event(name, float(ts[s]), float(ts[e - 1]), float(seg[np.argmax(np.abs(seg))])))
    return sorted(out, key=lambda ev: ev.t_start)


HFACS: dict[str, tuple[str, ...]] = {
    "Unsafe acts": ("Skill-based errors", "Decision errors", "Perceptual errors", "Routine violations",
                    "Exceptional violations"),
    "Preconditions for unsafe acts": ("Adverse mental states", "Adverse physiological states",
                                      "Physical/mental limitations", "Crew resource management",
                                      "Personal readiness", "Physical environment", "Technological environment"),
    "Unsafe supervision": ("Inadequate supervision", "Planned inappropriate operations",
                           "Failed to correct a known problem", "Supervisory violations"),
    "Organisational influences": ("Resource management", "Organisational climate", "Organisational process"),
}
"""HFACS levels → categories (Shappell & Wiegmann 2000, names as commonly used; not re-read in this session)."""


@cite("shappell_wiegmann_2000", note="four levels, top-down from organisation to the act")
def hfacs_table(findings: Mapping[str, Sequence[str]]) -> list[tuple[str, str, str]]:
    """Validate a ``{category: [finding, …]}`` mapping against :data:`HFACS` and return rows
    ``(level, category, finding)`` ordered from unsafe acts up to organisational influences."""
    where = {c: lvl for lvl, cats in HFACS.items() for c in cats}
    unknown = [c for c in findings if c not in where]
    if unknown:
        raise KeyError(f"not an HFACS category: {', '.join(unknown)}")
    order = list(HFACS)
    rows = [(where[c], c, f) for c, fs in findings.items() for f in fs]
    return sorted(rows, key=lambda r: (order.index(r[0]), HFACS[r[0]].index(r[1])))


# --- EASA European Risk Classification Scheme ---------------------------------------------------------------

ERCS_SEVERITY: dict[str, str] = {
    "A": "no accident likelihood (no implication to safety)",
    "E": "minor or serious, not life-changing, injury or minor damage",
    "I": "single fatality, life-changing injury or substantial damage",
    "M": "2-19 fatalities or aircraft destruction",
    "S": "20-100 potential fatalities",
    "X": "more than 100 potential fatalities",
}
"""ERCS potential-loss classes (Reg. (EU) 2020/2034, as summarised from the EASA Easy Access Rules)."""

ERCS_KEY_RISK_AREAS: dict[str, bool] = {
    "airborne collision": False, "aircraft upset": False, "collision on runway": False, "excursion": True,
    "fire/smoke/pressurisation": False, "ground damage": True, "obstacle collision in flight": False,
    "terrain collision": False, "other injuries": True, "security": False,
}
"""The ten key risk areas → whether the area is "low energy" (the only ones where barrier 8 applies)."""

ERCS_BARRIERS: dict[str, int] = {
    "design": 5, "tactical planning": 2, "regulations and procedures": 3, "situational awareness": 2,
    "warning systems": 3, "late recovery": 1, "protections": 1, "low energy": 1,
}
"""The eight ERCS barriers and their weights (maximum sum 18)."""

_ERCS_RED = {"X0", "X1", "X2", "S0", "S1", "S2", "M0", "M1", "I0"}
_ERCS_YELLOW = {"X3", "X4", "S3", "S4", "M2", "M3", "I1", "I2", "E0", "E1"}
_ERCS_SCALE = {"X": 1.0, "S": 0.5, "M": 0.1, "I": 0.01, "E": 0.001, "A": 0.0}
_BARRIER_STATES = {"stopped", "remaining", "failed", "n/a"}


@dataclass(frozen=True)
class ErcsResult:
    """ERCS outcome: code such as ``"M2"``, the barrier weight sum, colour band and numerical equivalent."""

    code: str
    severity: str
    barrier_sum: int
    barrier_score: int
    colour: str
    value: float
    counted: tuple[str, ...]


@cite("easa_ercs_2020_2034", note="barrier score = ceil(sum of stopped/remaining weights / 2)")
def ercs_score(key_risk_area: str, severity: str, barriers: Mapping[str, str]) -> ErcsResult:
    """Score an occurrence with ERCS. ``barriers`` maps each of :data:`ERCS_BARRIERS` to ``"stopped"``,
    ``"remaining"``, ``"failed"`` or ``"n/a"`` (missing = ``"n/a"``); only stopped and remaining barriers count.

    The scheme scores the *risk of the occurrence*, not its outcome: a near-miss with one barrier left scores
    worse than a minor accident where many remained. Severity ``"A"`` has no colour and value 0.
    """
    if key_risk_area not in ERCS_KEY_RISK_AREAS:
        raise KeyError(f"not an ERCS key risk area: {key_risk_area!r}")
    if severity not in ERCS_SEVERITY:
        raise KeyError(f"severity must be one of {', '.join(ERCS_SEVERITY)}")
    bad = [b for b in barriers if b not in ERCS_BARRIERS]
    if bad:
        raise KeyError(f"not an ERCS barrier: {', '.join(bad)}")
    states = {b: barriers.get(b, "n/a").lower() for b in ERCS_BARRIERS}
    wrong = [f"{b}={s}" for b, s in states.items() if s not in _BARRIER_STATES]
    if wrong:
        raise ValueError(f"barrier state must be stopped/remaining/failed/n/a: {', '.join(wrong)}")
    if states["low energy"] != "n/a" and not ERCS_KEY_RISK_AREAS[key_risk_area]:
        raise ValueError("the low-energy barrier applies only to ground damage, excursion and other injuries")
    counted = tuple(b for b, s in states.items() if s in ("stopped", "remaining"))
    total = sum(ERCS_BARRIERS[b] for b in counted)
    score = math.ceil(total / 2)
    code = f"{severity}{score}"
    colour = "none" if severity == "A" else "RED" if code in _ERCS_RED else "YELLOW" if code in _ERCS_YELLOW \
        else "GREEN"
    return ErcsResult(code, severity, total, score, colour, 1.0e6 * 10.0 ** -score * _ERCS_SCALE[severity],
                      counted)


# --- take-off roll ----------------------------------------------------------------------------------------

def accelerate_stop_distance(v_reject: float, accel: float, decel: float, reaction_s: float = 2.0,
                             v_start: float = 0.0) -> tuple[float, float, float, float]:
    """Ground distances [m] for accelerating from ``v_start`` to ``v_reject`` at a mean ``accel``, running on
    for ``reaction_s`` at ``v_reject`` before the stop, then braking at a mean ``decel`` (both m/s², > 0):
    returns (accelerate, reaction, stop, total). Constant-acceleration arithmetic; for a report, use the
    recorded ground speed instead (integrate the FDR ground-speed trace)."""
    if v_reject <= v_start or v_start < 0 or accel <= 0 or decel <= 0 or reaction_s < 0:
        raise ValueError("need v_reject > v_start >= 0 and positive accelerations, reaction >= 0")
    a = (v_reject ** 2 - v_start ** 2) / (2 * accel)
    r = v_reject * reaction_s
    s = v_reject ** 2 / (2 * decel)
    return a, r, s, a + r + s


def takeoff_acceleration_monitor(t: ArrayLike, speed: ArrayLike, expected_accel: float, *, fraction: float = 0.85,
                                 window_s: float = 3.0, start_speed: float = 15.0) -> float | None:
    """First time [s] at which the acceleration measured over the last ``window_s`` falls below ``fraction`` of
    ``expected_accel`` (m/s²), checked only above ``start_speed`` (m/s) so the spool-up is ignored; ``None``
    if it never does. A wrong take-off mass or a de-rate typed for the wrong runway shows up here seconds
    after thrust is set — long before the rotate call."""
    ts, v = np.asarray(t, float), np.asarray(speed, float)
    if ts.size != v.size or ts.size < 3 or np.any(np.diff(ts) <= 0):
        raise ValueError("need matching, strictly increasing series of length >= 3")
    if expected_accel <= 0 or not 0 < fraction < 1 or window_s <= 0:
        raise ValueError("expected_accel > 0, fraction in (0, 1), window_s > 0")
    for i in range(ts.size):
        if v[i] < start_speed:
            continue
        j = int(np.searchsorted(ts, ts[i] - window_s))
        if ts[i] - ts[j] < 0.5 * window_s:
            continue
        a = (v[i] - v[j]) / (ts[i] - ts[j])
        if a < fraction * expected_accel:
            return float(ts[i])
    return None
