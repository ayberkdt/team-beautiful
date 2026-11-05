"""Time-stepped mission simulation of an :class:`~aerokit.aero.aircraft.Aircraft`.

A mission is a sequence of segments flown in order from a state (time, ground distance, altitude,
weight). Each segment is integrated with the explicit midpoint rule (second order) in its natural
variable — distance for cruise/search, time for loiter, altitude for climb/descent — with step
``dt`` seconds of flight; the last step of every segment is shortened to end exactly on target.

Physics (steady, quasi-steady point mass; optional constant :class:`Wind`):

* **taxi/take-off** — an allowance: ``taxi_time`` at ``taxi_throttle`` plus ``takeoff_time`` at full
  throttle at sea level, or a fuel fraction of the start weight. Ground distance is ignored.
* **climb** — full throttle at the best-climb speed (:func:`~aerokit.aero.performance.best_climb_speed`)
  or a given speed; ``ROC = (P_A − P_R)/W`` (:func:`~aerokit.aero.performance.rate_of_climb`);
  fuel flow of the engine at full power. Raises if ROC falls below ``min_rate_of_climb``.
* **cruise / search** — level flight over a distance at the best-range speed, the best-endurance
  speed (re-evaluated at the current weight every step) or a fixed speed; fuel flow
  :meth:`Aircraft.fuel_flow` at the current weight.
* **loiter** — level flight for a duration (reserve or time-limited search).
* **descent** — constant rate of descent at constant speed, thrust power ``P_R − W·RD`` but not
  below ``idle_throttle`` × available power.

A fixed speed must be ≥ 1.2 V_stall at the segment's start weight and sustainable (P_R ≤ P_A).
Running out of fuel raises :class:`FuelExhaustedError` naming the segment, time and distance.

**Wind.** A segment may carry a ``track`` — the ground-track bearing [rad] as a function of the
ground distance flown in that segment (``None`` from the function = holding, no fixed track). With a
:class:`Wind` the aircraft crabs to hold the track, and its ground speed is
``V_g = √(V² − w_⊥²) + w_∥`` (wind triangle; ``V`` the horizontal true airspeed, ``w_∥``/``w_⊥`` the
wind components along/across the track). Distances are ground distances, so a headwind raises the
fuel per kilometre. Segments without a track (reserve loiter, holding) fly in the air mass: the wind
averages out over a racetrack, ground speed = TAS. Speeds are still the *still-air* optima
(best range / endurance); the wind-optimal speed is not searched.

:func:`search_mission` builds the leg-2 mission: taxi, climb, cruise to the area along the
WGS-84 geodesic, search along a pattern, return, 30-min reserve loiter (or a fuel fraction),
descent; :func:`max_time_on_station` finds the search time that uses the fuel down to the reserve.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.performance import best_climb_speed, best_endurance_speed, best_range_speed, rate_of_climb
from aerokit.mission.geodesy import direct, inverse
from aerokit.mission.patterns import SearchPattern
from aerokit.output.tables import Table
from aerokit.references import cite

__all__ = ["FuelExhaustedError", "TaxiTakeoff", "Climb", "Cruise", "Loiter", "Descent", "Segment",
           "SegmentRecord", "MissionResult", "RESERVE_30MIN", "simulate", "search_mission", "max_time_on_station",
           "SpeedSpec", "Wind", "Track"]

FloatArray = NDArray[np.float64]
SpeedSpec = float | Literal["best_range", "best_endurance", "best_climb"]
#: ground-track bearing [rad, clockwise from north] as a function of the ground distance flown in the
#: segment [m]; ``None`` = no fixed track (holding)
Track = Callable[[float], float | None]


@dataclass(frozen=True)
class Wind:
    """Constant horizontal wind.

    Attributes
    ----------
    speed : float
        Wind speed [m/s] (≥ 0).
    from_direction : float
        Direction the wind blows **from** [rad, clockwise from north] (meteorological convention:
        a wind "from 270°" is a westerly and pushes the aircraft east).
    """

    speed: float
    from_direction: float = 0.0

    def __post_init__(self) -> None:
        if not (math.isfinite(self.speed) and self.speed >= 0 and math.isfinite(self.from_direction)):
            raise ValueError("wind speed must be finite and >= 0, direction finite")

    def components(self, track: float) -> tuple[float, float]:
        """(along-track tailwind, crosswind) [m/s] for a ground track ``track`` [rad]."""
        rel = self.from_direction + math.pi - track
        return self.speed * math.cos(rel), self.speed * math.sin(rel)

    def ground_speed(self, airspeed: float, track: float) -> float:
        """Ground speed [m/s] holding ``track`` at horizontal true airspeed ``airspeed`` (wind triangle).

        Raises
        ------
        ValueError
            The crosswind is not smaller than the airspeed, or the headwind stops ground progress.
        """
        along, cross = self.components(track)
        if abs(cross) >= airspeed:
            raise ValueError(f"crosswind {abs(cross):.1f} m/s is not below the airspeed {airspeed:.1f} m/s")
        gs = math.sqrt(airspeed * airspeed - cross * cross) + along
        if not gs > 0:
            raise ValueError(f"headwind {-along:.1f} m/s stops ground progress at {airspeed:.1f} m/s")
        return gs


class FuelExhaustedError(RuntimeError):
    """Fuel ran out before the end of the mission.

    Attributes
    ----------
    segment : str
        Name of the segment in which the fuel ran out.
    time : float
        Mission time at exhaustion [s].
    distance : float
        Ground distance flown in the mission at exhaustion [m].
    """

    def __init__(self, segment: str, time: float, distance: float) -> None:
        self.segment, self.time, self.distance = segment, time, distance
        super().__init__(f"fuel exhausted in segment {segment!r} at t = {time / 60.0:.1f} min, "
                         f"after {distance / 1e3:.1f} km — the mission cannot be flown with this fuel load")


@dataclass(frozen=True)
class TaxiTakeoff:
    """Taxi and take-off fuel allowance (assumed values, not from a source; change to suit)."""

    taxi_time: float = 600.0
    taxi_throttle: float = 0.10
    takeoff_time: float = 60.0
    fuel_fraction: float | None = None
    name: str = "taxi/take-off"
    kind: str = "ground"


@dataclass(frozen=True)
class Climb:
    """Climb to ``to_altitude`` [m] at full throttle; ``speed=None`` → best climb speed."""

    to_altitude: float
    speed: float | None = None
    name: str = "climb"
    kind: str = "climb"
    track: Track | None = None


@dataclass(frozen=True)
class Cruise:
    """Level flight over ``distance`` [m]; ``kind="search"`` counts as time on station."""

    distance: float
    speed: SpeedSpec = "best_range"
    name: str = "cruise"
    kind: str = "cruise"
    track: Track | None = None


@dataclass(frozen=True)
class Loiter:
    """Level flight for ``duration`` [s] (``kind`` "loiter", "reserve" or "search")."""

    duration: float
    speed: SpeedSpec = "best_endurance"
    name: str = "loiter"
    kind: str = "loiter"
    track: Track | None = None


@dataclass(frozen=True)
class Descent:
    """Descent to ``to_altitude`` [m] at ``rate`` [m/s] and constant ``speed`` [m/s or spec]."""

    to_altitude: float
    rate: float = 5.0
    speed: SpeedSpec = "best_range"
    idle_throttle: float = 0.05
    name: str = "descent"
    kind: str = "descent"
    track: Track | None = None


Segment = TaxiTakeoff | Climb | Cruise | Loiter | Descent

#: The challenge's 30-min loiter requirement, used as the default reserve.
RESERVE_30MIN = Loiter(1800.0, name="reserve loiter", kind="reserve")


@dataclass(frozen=True)
class SegmentRecord:
    """Result of one segment (SI: s, m, N, m/s)."""

    name: str
    kind: str
    t_start: float
    t_end: float
    distance: float
    fuel: float
    W_start: float
    W_end: float
    h_start: float
    h_end: float
    V_mean: float

    @property
    def duration(self) -> float:
        """Segment duration [s]."""
        return self.t_end - self.t_start


@dataclass(frozen=True)
class MissionResult:
    """Simulated mission.

    Attributes
    ----------
    records : tuple of SegmentRecord
    W_start, fuel, reserve_fuel : float
        Start weight, usable fuel and fuel to be kept unburned [N].
    end_point : tuple of float or None
        (lat, lon) where the search ended [deg] (:func:`search_mission` only).
    """

    records: tuple[SegmentRecord, ...]
    W_start: float
    fuel: float
    reserve_fuel: float = 0.0
    end_point: tuple[float, float] | None = None
    notes: tuple[str, ...] = field(default=())

    @property
    def total_time(self) -> float:
        """Block time [s]."""
        return self.records[-1].t_end if self.records else 0.0

    @property
    def time_on_station(self) -> float:
        """Time spent in segments of kind ``"search"`` [s]."""
        return sum(r.duration for r in self.records if r.kind == "search")

    @property
    def search_distance(self) -> float:
        """Distance flown in segments of kind ``"search"`` [m]."""
        return sum(r.distance for r in self.records if r.kind == "search")

    @property
    def fuel_used(self) -> float:
        """Fuel burned [N]."""
        return sum(r.fuel for r in self.records)

    @property
    def fuel_remaining(self) -> float:
        """Fuel on board at the end [N]."""
        return self.fuel - self.fuel_used

    @property
    def fuel_margin(self) -> float:
        """Fuel remaining beyond ``reserve_fuel`` [N] (negative: reserve infringed)."""
        return self.fuel_remaining - self.reserve_fuel

    @property
    def feasible(self) -> bool:
        """True if the reserve is intact at landing."""
        return self.fuel_margin >= 0.0

    def timeline(self) -> Table:
        """Timeline table (minutes, km, kg, m, km/h; one decimal place per column)."""
        rows = [[r.name, f"{r.t_start / 60:.1f}", f"{r.t_end / 60:.1f}", f"{r.distance / 1e3:.1f}",
                 f"{r.fuel / G0:.1f}", f"{r.W_end / G0:.1f}", f"{r.h_end:.1f}", f"{r.V_mean * 3.6:.1f}"]
                for r in self.records]
        return Table(["segment", "start (min)", "end (min)", "distance (km)", "fuel (kg)", "mass at end (kg)",
                      "altitude at end (m)", "mean ground speed (km/h)"], rows,
                     title=f"Mission timeline: {self.time_on_station / 3600:.2f} h on station, "
                           f"fuel margin {self.fuel_margin / G0:.1f} kg")


# ----------------------------------------------------------------------------- helpers
def _throttle_fuel_flow(ac: Aircraft, h: float, throttle: float) -> float:
    """Fuel flow [N/s] at a throttle setting (V-independent for both engine models)."""
    v_ref = 50.0
    return ac.engine.fuel_flow(v_ref, h, throttle * ac.engine.thrust_power(v_ref, h, False))


def _climb_fuel_flow(ac: Aircraft, V: float, h: float) -> float:
    return ac.engine.fuel_flow(V, h, ac.power_available(V, h))


def _speed(ac: Aircraft, spec: SpeedSpec, h: float, W: float) -> float:
    if isinstance(spec, str):
        if spec == "best_range":
            return best_range_speed(ac, h, W)
        if spec == "best_endurance":
            return best_endurance_speed(ac, h, W)
        if spec == "best_climb":
            return best_climb_speed(ac, h, W)
        raise ValueError(f"unknown speed {spec!r} (best_range, best_endurance, best_climb or m/s)")
    V = float(spec)
    if not (math.isfinite(V) and V > 0):
        raise ValueError(f"speed must be > 0 m/s, got {spec!r}")
    return V


class _Sim:
    def __init__(self, ac: Aircraft, W: float, fuel: float, dt: float, h: float, allow_negative: bool,
                 min_roc: float, wind: Wind | None = None) -> None:
        if not (dt > 0 and math.isfinite(dt)):
            raise ValueError("dt must be > 0")
        if not 0 <= fuel < W:
            raise ValueError("fuel must be >= 0 and below the start weight")
        self.ac, self.dt, self.allow_negative, self.min_roc = ac, dt, allow_negative, min_roc
        self.wind = wind
        self.t = self.x = 0.0
        self.h, self.W, self.W_zf = h, W, W - fuel
        self.records: list[SegmentRecord] = []

    # --- bookkeeping
    def _gs(self, track: Track | None, airspeed: float, s: float) -> float:
        """Ground speed at ground distance ``s`` into a segment (= airspeed without wind or track)."""
        if self.wind is None or track is None or self.wind.speed == 0.0:
            return airspeed
        bearing = track(s)
        return airspeed if bearing is None else self.wind.ground_speed(airspeed, bearing)

    def _step(self, name: str, W_new: float, dt: float, dx: float, dh: float) -> None:
        if not self.allow_negative and W_new < self.W_zf:
            drop = self.W - W_new
            frac = (self.W - self.W_zf) / drop if drop > 0.0 else 0.0
            raise FuelExhaustedError(name, self.t + frac * dt, self.x + frac * dx)
        self.W, self.t, self.x, self.h = W_new, self.t + dt, self.x + dx, self.h + dh

    def _record(self, seg: Segment, t0: float, x0: float, W0: float, h0: float) -> SegmentRecord:
        dur = self.t - t0
        rec = SegmentRecord(seg.name, seg.kind, t0, self.t, self.x - x0, W0 - self.W, W0, self.W, h0, self.h,
                            (self.x - x0) / dur if dur > 0 else 0.0)
        self.records.append(rec)
        return rec

    def _check_level(self, name: str, spec: SpeedSpec, V: float) -> None:
        ac = self.ac
        v_min = 1.2 * ac.stall_speed(self.h, self.W)
        if not isinstance(spec, str) and v_min - V > 1e-9:
            raise ValueError(f"{name}: speed {V:.1f} m/s is below 1.2 V_stall = "
                             f"{1.2 * ac.stall_speed(self.h, self.W):.1f} m/s")
        if ac.power_required(V, self.h, self.W) > ac.power_available(V, self.h):
            raise ValueError(f"{name}: level flight at {V:.1f} m/s and {self.h:.0f} m needs more power than available")

    # --- segments
    def run(self, seg: Segment) -> SegmentRecord:
        t0, x0, W0, h0 = self.t, self.x, self.W, self.h
        if isinstance(seg, TaxiTakeoff):
            self._taxi(seg)
        elif isinstance(seg, Climb):
            self._climb(seg)
        elif isinstance(seg, Cruise):
            self._cruise(seg)
        elif isinstance(seg, Loiter):
            self._loiter(seg)
        else:
            self._descent(seg)
        return self._record(seg, t0, x0, W0, h0)

    def _taxi(self, seg: TaxiTakeoff) -> None:
        if seg.fuel_fraction is not None:
            if not 0 <= seg.fuel_fraction < 1:
                raise ValueError("fuel_fraction must be in [0, 1)")
            fuel, dur = seg.fuel_fraction * self.W, seg.taxi_time + seg.takeoff_time
        else:
            if not (seg.taxi_time >= 0 and seg.takeoff_time >= 0 and 0 <= seg.taxi_throttle <= 1):
                raise ValueError("taxi/take-off times must be >= 0 and throttle in [0, 1]")
            fuel = (seg.taxi_time * _throttle_fuel_flow(self.ac, self.h, seg.taxi_throttle)
                    + seg.takeoff_time * _throttle_fuel_flow(self.ac, self.h, 1.0))
            dur = seg.taxi_time + seg.takeoff_time
        self._step(seg.name, self.W - fuel, dur, 0.0, 0.0)

    def _climb_rates(self, seg: Climb, h: float, W: float) -> tuple[float, float, float]:
        V = best_climb_speed(self.ac, h, W) if seg.speed is None else seg.speed
        roc = rate_of_climb(self.ac, V, h, W)
        if roc < self.min_roc:
            raise ValueError(f"{seg.name}: rate of climb {roc:.2f} m/s at {h:.0f} m is below "
                             f"{self.min_roc} m/s — {seg.to_altitude:.0f} m is above the reachable ceiling")
        return V, roc, _climb_fuel_flow(self.ac, V, h)

    def _climb(self, seg: Climb) -> None:
        if seg.to_altitude < self.h:
            raise ValueError(f"{seg.name}: target {seg.to_altitude} m is below the current altitude")
        s = 0.0
        while seg.to_altitude - self.h > 1e-6:
            V1, roc1, ff1 = self._climb_rates(seg, self.h, self.W)
            dh = min(roc1 * self.dt, seg.to_altitude - self.h)
            dt1 = dh / roc1
            Vm, rocm, ffm = self._climb_rates(seg, self.h + 0.5 * dh, self.W - 0.5 * ff1 * dt1)
            dtm = dh / rocm
            dx = self._gs(seg.track, math.sqrt(max(Vm * Vm - rocm * rocm, 0.0)), s) * dtm
            self._step(seg.name, self.W - ffm * dtm, dtm, dx, dh)
            s += dx
        self.h = seg.to_altitude

    def _cruise(self, seg: Cruise) -> None:
        if not seg.distance >= 0:
            raise ValueError(f"{seg.name}: distance must be >= 0")
        if seg.distance == 0:
            return
        V = _speed(self.ac, seg.speed, self.h, self.W)
        self._check_level(seg.name, seg.speed, V)
        s = 0.0
        while seg.distance - s > 1e-6:
            V1 = _speed(self.ac, seg.speed, self.h, self.W)
            G1 = self._gs(seg.track, V1, s)
            ds = min(G1 * self.dt, seg.distance - s)
            g1 = self.ac.fuel_flow(V1, self.h, self.W) / G1                  # dW/ds [N per ground m]
            Wm = self.W - 0.5 * g1 * ds
            Vm = _speed(self.ac, seg.speed, self.h, Wm)
            Gm = self._gs(seg.track, Vm, s + 0.5 * ds)
            gm = self.ac.fuel_flow(Vm, self.h, Wm) / Gm
            self._step(seg.name, self.W - gm * ds, ds / Gm, ds, 0.0)
            s += ds

    def _loiter(self, seg: Loiter) -> None:
        if not seg.duration >= 0:
            raise ValueError(f"{seg.name}: duration must be >= 0")
        if seg.duration == 0:
            return
        V = _speed(self.ac, seg.speed, self.h, self.W)
        self._check_level(seg.name, seg.speed, V)
        t = s = 0.0
        while seg.duration - t > 1e-9:
            dt = min(self.dt, seg.duration - t)
            V1 = _speed(self.ac, seg.speed, self.h, self.W)
            f1 = self.ac.fuel_flow(V1, self.h, self.W)
            Wm = self.W - 0.5 * f1 * dt
            Vm = _speed(self.ac, seg.speed, self.h, Wm)
            fm = self.ac.fuel_flow(Vm, self.h, Wm)
            ds = self._gs(seg.track, Vm, s + 0.5 * self._gs(seg.track, V1, s) * dt) * dt
            self._step(seg.name, self.W - fm * dt, dt, ds, 0.0)
            t += dt
            s += ds

    def _descent_flow(self, seg: Descent, V: float, h: float, W: float) -> float:
        ac = self.ac
        p = max(ac.power_required(V, h, W) - W * seg.rate, seg.idle_throttle * ac.power_available(V, h))
        return ac.engine.fuel_flow(V, h, p)

    def _descent(self, seg: Descent) -> None:
        if seg.to_altitude > self.h:
            raise ValueError(f"{seg.name}: target {seg.to_altitude} m is above the current altitude")
        if not (seg.rate > 0 and 0 <= seg.idle_throttle <= 1):
            raise ValueError(f"{seg.name}: rate must be > 0 and idle_throttle in [0, 1]")
        V = _speed(self.ac, seg.speed, self.h, self.W)
        if seg.rate >= V:
            raise ValueError(f"{seg.name}: speed must exceed the rate of descent")
        s = 0.0
        while self.h - seg.to_altitude > 1e-6:
            dh = min(seg.rate * self.dt, self.h - seg.to_altitude)
            dt = dh / seg.rate
            f1 = self._descent_flow(seg, V, self.h, self.W)
            fm = self._descent_flow(seg, V, self.h - 0.5 * dh, self.W - 0.5 * f1 * dt)
            dx = self._gs(seg.track, math.sqrt(V * V - seg.rate ** 2), s) * dt
            self._step(seg.name, self.W - fm * dt, dt, dx, -dh)
            s += dx
        self.h = seg.to_altitude


@cite("raymer_2018", note="mission segment build-up (Ch. 3, mission profile); steady point-mass performance")
@cite("anderson_1999", note="power-required/power-available climb and level-flight relations")
def simulate(ac: Aircraft, segments: Sequence[Segment], *, W_start: float | None = None, fuel: float | None = None,
             reserve_fuel: float = 0.0, h_start: float = 0.0, dt: float = 10.0, allow_negative_fuel: bool = False,
             min_rate_of_climb: float = 0.1, wind: Wind | None = None) -> MissionResult:
    """Fly ``segments`` in order and return the timeline.

    Parameters
    ----------
    ac : Aircraft
    segments : sequence of TaxiTakeoff, Climb, Cruise, Loiter, Descent
    W_start : float, optional
        Start weight [N] (default ``ac.W0``).
    fuel : float, optional
        Usable fuel on board [N] (default ``ac.W_fuel``).
    reserve_fuel : float
        Fuel that must remain unburned at the end [N] (for :attr:`MissionResult.fuel_margin`).
    h_start : float
        Initial altitude [m].
    dt : float
        Integration step [s of flight].
    allow_negative_fuel : bool
        Continue past fuel exhaustion (for root finding only; the result is then not physical).
    min_rate_of_climb : float
        Climb segments fail below this rate [m/s].
    wind : Wind, optional
        Constant wind, applied to segments that carry a ``track``.

    Raises
    ------
    FuelExhaustedError
        Fuel ran out before the last segment ended.
    ValueError
        Invalid segment, unattainable altitude, speed below 1.2 V_stall or not sustainable.
    """
    W = ac.W0 if W_start is None else W_start
    f = ac.W_fuel if fuel is None else fuel
    sim = _Sim(ac, W, f, dt, h_start, allow_negative_fuel, min_rate_of_climb, wind)
    for seg in segments:
        sim.run(seg)
    return MissionResult(tuple(sim.records), W, f, reserve_fuel)


# ----------------------------------------------------------------------------- search mission
def _route_geodesic(lats: FloatArray, lons: FloatArray) -> tuple[list[float], list[float]]:
    seg, az = [], []
    for i in range(len(lats) - 1):
        g = inverse(float(lats[i]), float(lons[i]), float(lats[i + 1]), float(lons[i + 1]))
        seg.append(g.distance)
        az.append(g.azimuth1)
    return seg, az


def _geodesic_track(lat: float, lon: float, azimuth: float, offset: float = 0.0) -> Track:
    """Forward azimuth [rad] along the geodesic from (lat, lon) with initial ``azimuth`` [deg]."""
    def track(s: float) -> float:
        return math.radians(direct(lat, lon, azimuth, max(offset + s, 0.0))[2]) if offset + s > 0 else \
            math.radians(azimuth)
    return track


def _route_track(seg: list[float], az: list[float]) -> Track:
    """Bearing [rad] of the pattern leg containing ground distance ``s`` (initial azimuth of each leg; the
    legs are short); ``None`` past the end of the route (holding at the last waypoint)."""
    def track(s: float) -> float | None:
        for L, a in zip(seg, az, strict=True):
            if s <= L:
                return math.radians(a)
            s -= L
        return None
    return track


def _point_on_route(lats: FloatArray, lons: FloatArray, seg: list[float], az: list[float],
                    s: float) -> tuple[float, float]:
    for i, (L, a) in enumerate(zip(seg, az, strict=True)):
        if s <= L:
            la, lo, _ = direct(float(lats[i]), float(lons[i]), a, max(s, 0.0))
            return la, lo
        s -= L
    return float(lats[-1]), float(lons[-1])


def search_mission(ac: Aircraft, base: tuple[float, float], pattern: SearchPattern, search_altitude: float, *,
                   cruise_altitude: float | None = None, search_speed: SpeedSpec = "best_endurance",
                   transit_speed: SpeedSpec = "best_range", station_time: float | None = None,
                   reserve: Loiter | float = RESERVE_30MIN,
                   taxi: TaxiTakeoff | None = None, descent_rate: float = 5.0, descent_speed: float | None = None,
                   W_start: float | None = None, fuel: float | None = None, dt: float = 10.0,
                   allow_negative_fuel: bool = False, wind: Wind | None = None) -> MissionResult:
    """Leg-2 mission: base → search area → search pattern → base, with reserve.

    Parameters
    ----------
    ac : Aircraft
    base : (lat, lon)
        Airfield [deg] (taken at sea level).
    pattern : SearchPattern
        Route with a :class:`~aerokit.mission.geodesy.LocalFrame`; flown from its first waypoint.
    search_altitude : float
        Search altitude [m] (above the ellipsoid = above ground for a sea-level area).
    cruise_altitude : float, optional
        Transit altitude [m] (default: the search altitude). A different value adds a climb or
        descent at area entry and exit whose horizontal distance is flown *in addition* to the
        geodesic legs (conservative).
    search_speed, transit_speed : float or str
        ``"best_endurance"``/``"best_range"`` or a fixed TAS [m/s] (≥ 1.2 V_stall).
    station_time : float, optional
        Search for this long [s] instead of flying the whole pattern; past the end of the route
        the aircraft holds at the last waypoint.
    reserve : Loiter or float
        Reserve flown before the final descent (default 30 min at best endurance, the challenge's
        loiter requirement), or a fraction of the usable fuel kept unburned.
    taxi : TaxiTakeoff, optional
        Allowance (default :class:`TaxiTakeoff`).
    descent_rate, descent_speed : float
        Final descent [m/s]; speed default: best-range TAS at the transit altitude and start weight.
    W_start, fuel, dt, allow_negative_fuel
        As in :func:`simulate`.
    wind : Wind, optional
        Constant wind on the outbound and return geodesics, the initial climb, the final descent and the
        search legs; the reserve loiter and the transit climbs/descents at the area fly in the air mass.

    Raises
    ------
    FuelExhaustedError
        Fuel ran out before landing.
    ValueError
        Area closer than the climb (or descent) distance, unattainable altitude, invalid speed.
    """
    W = ac.W0 if W_start is None else W_start
    f = ac.W_fuel if fuel is None else fuel
    h_c = search_altitude if cruise_altitude is None else cruise_altitude
    if isinstance(reserve, Loiter):
        reserve_fuel = 0.0
    else:
        if not 0 <= reserve < 1:
            raise ValueError("a reserve fraction must be in [0, 1)")
        reserve_fuel = reserve * f
    lats, lons = pattern.geodetic()
    seg, az = _route_geodesic(lats, lons)
    route_len = sum(seg)
    sim = _Sim(ac, W, f, dt, 0.0, allow_negative_fuel, 0.1, wind)
    sim.run(taxi or TaxiTakeoff())
    g_out = inverse(base[0], base[1], float(lats[0]), float(lons[0]))
    d_out = g_out.distance
    sim.run(Climb(h_c, name="climb", track=_geodesic_track(base[0], base[1], g_out.azimuth1)))
    if sim.x > d_out:
        raise ValueError(f"search area entry is {d_out / 1e3:.1f} km away, closer than the climb "
                         f"distance {sim.x / 1e3:.1f} km")
    sim.run(Cruise(d_out - sim.x, transit_speed, name="cruise out",
                   track=_geodesic_track(base[0], base[1], g_out.azimuth1, sim.x)))
    if search_altitude > h_c:
        sim.run(Climb(search_altitude, name="climb to search altitude"))
    elif search_altitude < h_c:
        sim.run(Descent(search_altitude, descent_rate, transit_speed, name="descent to search altitude"))
    search_track = _route_track(seg, az)
    if station_time is None:
        rec = sim.run(Cruise(route_len, search_speed, name="search", kind="search", track=search_track))
    else:
        rec = sim.run(Loiter(station_time, search_speed, name="search", kind="search", track=search_track))
    end = _point_on_route(lats, lons, seg, az, rec.distance)
    if h_c > search_altitude:
        sim.run(Climb(h_c, name="climb to transit altitude"))
    elif h_c < search_altitude:
        sim.run(Descent(h_c, descent_rate, transit_speed, name="descent to transit altitude"))
    V_d = best_range_speed(ac, h_c, W) if descent_speed is None else descent_speed
    if V_d <= descent_rate:
        raise ValueError("descent speed must exceed the rate of descent")
    g_back = inverse(end[0], end[1], base[0], base[1])
    d_back = g_back.distance
    back = _geodesic_track(end[0], end[1], g_back.azimuth1)
    v_h = math.sqrt(V_d * V_d - descent_rate ** 2)
    x_desc = (v_h if wind is None else wind.ground_speed(v_h, math.radians(g_back.azimuth2))) * h_c / descent_rate
    if x_desc > d_back:
        raise ValueError(f"return distance {d_back / 1e3:.1f} km is shorter than the descent distance "
                         f"{x_desc / 1e3:.1f} km")
    sim.run(Cruise(d_back - x_desc, transit_speed, name="cruise back", track=back))
    if isinstance(reserve, Loiter):
        sim.run(reserve)
    sim.run(Descent(0.0, descent_rate, V_d, name="descent and landing",
                    track=_geodesic_track(end[0], end[1], g_back.azimuth1, d_back - x_desc)))
    wind_note = ("no wind; ground speed = TAS" if wind is None or wind.speed == 0 else
                 f"wind {wind.speed:.1f} m/s from {math.degrees(wind.from_direction) % 360:.0f}°")
    notes = (f"{wind_note}; descent speed {V_d:.1f} m/s at {descent_rate:.1f} m/s",)
    return MissionResult(tuple(sim.records), W, f, reserve_fuel, end, notes)


def max_time_on_station(ac: Aircraft, base: tuple[float, float], pattern: SearchPattern, search_altitude: float,
                        *, cruise_altitude: float | None = None, search_speed: SpeedSpec = "best_endurance",
                        transit_speed: SpeedSpec = "best_range", reserve: Loiter | float = RESERVE_30MIN,
                        taxi: TaxiTakeoff | None = None, descent_rate: float = 5.0,
                        descent_speed: float | None = None, W_start: float | None = None,
                        fuel: float | None = None, dt: float = 10.0, tol: float = 1.0,
                        wind: Wind | None = None) -> tuple[float, MissionResult]:
    """Longest search time [s] that lands with the reserve intact, and that mission.

    The fuel margin decreases monotonically with the search time; the root of
    ``fuel_margin(T) = 0`` is bracketed and refined with Brent's method to ``tol`` seconds, then
    rounded down so the returned mission is feasible. Other arguments as in :func:`search_mission`.

    Raises
    ------
    ValueError
        The aircraft cannot reach the area and return with the reserve even without searching.
    """
    def run(T: float, negative: bool) -> MissionResult:
        return search_mission(ac, base, pattern, search_altitude, cruise_altitude=cruise_altitude,
                              search_speed=search_speed, transit_speed=transit_speed, station_time=T,
                              reserve=reserve, taxi=taxi, descent_rate=descent_rate, descent_speed=descent_speed,
                              W_start=W_start, fuel=fuel, dt=dt, allow_negative_fuel=negative, wind=wind)

    def margin(T: float) -> float:
        return run(T, True).fuel_margin

    m0 = margin(0.0)
    if m0 < 0.0:
        raise ValueError(f"the search area cannot be reached and left with the reserve: margin without "
                         f"searching is {m0 / G0:.1f} kg")
    W = ac.W0 if W_start is None else W_start
    ff = ac.fuel_flow(best_endurance_speed(ac, search_altitude, W), search_altitude, W)
    lo, hi = 0.0, max(m0 / ff, 60.0)
    for _ in range(60):
        if margin(hi) < 0.0:
            break
        lo, hi = hi, 1.5 * hi
    else:                                                              # pragma: no cover - defensive
        raise ValueError("could not bracket the time on station")
    T = float(brentq(margin, lo, hi, xtol=tol))
    while T > 0.0 and margin(T) < 0.0:
        T = max(T - tol, 0.0)
    return T, run(T, False)
