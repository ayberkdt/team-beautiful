"""Search-mission optimisation: altitude × speed × track spacing for maximum coverage within fuel.

For each candidate (altitude ``h``, search speed ``V = k·V_E(h, W0)`` with ``V_E`` the best-endurance
speed, overlap ``o``) a parallel-track (PS) or creeping-line (CS) pattern with spacing
``S = 2 h tan(FOV/2)·(1 − o)`` is laid over the rectangle — or over a polygon (``polygon=``, then the
coverage is the raster of :func:`~aerokit.mission.coverage.pattern_coverage`) — and flown in an optional
constant wind; :func:`~aerokit.mission.simulate.max_time_on_station` gives the search time
the fuel allows (reserve kept), and the covered area is the exact swept-rectangle union of the
route flown in that time (the whole pattern if it fits; the fuel used is then that of the full
pattern). ``objective="pod"`` maximises the random-search probability of detection
``1 − exp(−W_sweep·L/A)`` with ``W_sweep = sweep_width_factor × swath`` instead.

Sensor constraints: ``altitudes`` must lie in ``[min_altitude, max_altitude]`` (e.g. a maximum
altitude from the required ground resolution, ``h_max = GSD / IFOV``). Infeasible candidates (cannot
climb, speed below 1.2 V_stall or unsustainable, area unreachable) are kept with a reason.

Search: full grid, then a local refinement around the best point (coordinate steps halved twice).
The Pareto front is coverage (maximise) versus fuel used (minimise) over all feasible candidates.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.performance import best_endurance_speed
from aerokit.mission.coverage import pattern_coverage, polygon_area_xy, random_search_pod
from aerokit.mission.geodesy import LocalFrame
from aerokit.mission.patterns import SearchPattern, creeping_line, parallel_track, polygon_track, sensor_swath
from aerokit.mission.simulate import (RESERVE_30MIN, FuelExhaustedError, Loiter, Wind, max_time_on_station,
                                      search_mission)
from aerokit.output.tables import Table
from aerokit.references import cite

__all__ = ["Candidate", "OptimizationResult", "evaluate_candidate", "optimize_search", "pareto_front"]


@dataclass(frozen=True)
class Candidate:
    """One evaluated design point (SI units).

    Attributes
    ----------
    altitude, speed_factor, overlap : float
        Decision variables (speed = speed_factor × best-endurance speed at W0).
    speed, swath, spacing : float
        Search TAS [m/s], swath [m], track spacing [m].
    coverage, covered_area, pod : float
        Covered fraction, area [m²], random-search POD.
    fuel_used, time_on_station, fuel_margin : float
        [N], [s], [N].
    complete : bool
        The whole pattern was flown.
    feasible : bool
    reason : str
        Why the point is infeasible ("" if feasible).
    """

    altitude: float
    speed_factor: float
    overlap: float
    speed: float = 0.0
    swath: float = 0.0
    spacing: float = 0.0
    coverage: float = 0.0
    covered_area: float = 0.0
    pod: float = 0.0
    fuel_used: float = 0.0
    time_on_station: float = 0.0
    fuel_margin: float = 0.0
    complete: bool = False
    feasible: bool = False
    reason: str = ""

    def score(self, objective: str) -> float:
        """Objective value (−inf when infeasible)."""
        if not self.feasible:
            return -math.inf
        return self.pod if objective == "pod" else self.covered_area

    def rank(self, objective: str) -> tuple[float, float]:
        """Sort key: objective fraction rounded to 1e-9 (the area is fixed), then less fuel."""
        if not self.feasible:
            return (-math.inf, 0.0)
        return (round(self.pod if objective == "pod" else self.coverage, 9), -self.fuel_used)


@dataclass(frozen=True)
class OptimizationResult:
    """Grid search + refinement result."""

    best: Candidate
    candidates: tuple[Candidate, ...]
    pareto: tuple[Candidate, ...]
    objective: str

    @staticmethod
    def _table(cands: Sequence[Candidate], title: str) -> Table:
        rows = [[f"{c.altitude:.0f}", f"{c.speed * 3.6:.1f}", f"{c.spacing:.0f}", f"{100 * c.coverage:.1f}",
                 f"{100 * c.pod:.1f}", f"{c.time_on_station / 3600:.2f}", f"{c.fuel_used / G0:.1f}",
                 "yes" if c.complete else "no", c.reason or "ok"] for c in cands]
        return Table(["altitude (m)", "search TAS (km/h)", "spacing (m)", "coverage (%)", "POD (%)",
                      "time on station (h)", "fuel used (kg)", "pattern complete", "status"], rows, title=title)

    def table(self) -> Table:
        """All candidates, best objective first."""
        order = sorted(self.candidates, key=lambda c: c.rank(self.objective), reverse=True)
        return self._table(order, f"Search optimisation: {len(self.candidates)} candidates, objective {self.objective}")

    def pareto_table(self) -> Table:
        """Pareto front, increasing fuel."""
        return self._table(self.pareto, "Pareto front: coverage versus fuel used")


def pareto_front(cands: Sequence[Candidate]) -> tuple[Candidate, ...]:
    """Feasible candidates not dominated in (coverage ↑, fuel used ↓), sorted by fuel."""
    feas = sorted((c for c in cands if c.feasible), key=lambda c: (c.fuel_used, -c.coverage))
    out: list[Candidate] = []
    best = -math.inf
    for c in feas:
        if c.coverage > best + 1e-9:
            out.append(c)
            best = c.coverage
    return tuple(out)


def _pattern(kind: str, width: float, length: float, spacing: float, orientation: float, frame: LocalFrame,
             polygon: ArrayLike | None) -> tuple[SearchPattern, float]:
    """(pattern, search-area size [m²]) for the optimiser: PS/CS over the rectangle or the polygon."""
    if kind not in ("PS", "CS"):
        raise ValueError("the search optimiser lays PS or CS patterns")
    if polygon is not None:
        poly = np.asarray(polygon, float)
        return polygon_track(poly, spacing, orientation=orientation, kind=kind, frame=frame), polygon_area_xy(poly)
    build = parallel_track if kind == "PS" else creeping_line
    return build(width, length, spacing, orientation=orientation, frame=frame), width * length


@cite("koopman_1980", note="random-search POD objective")
def evaluate_candidate(ac: Aircraft, base: tuple[float, float], area_center: tuple[float, float], width: float,
                       length: float, fov: float, altitude: float, speed_factor: float, overlap: float, *,
                       orientation: float = 0.0, reserve: Loiter | float = RESERVE_30MIN,
                       sweep_width_factor: float = 1.0, dt: float = 30.0, kind: str = "PS",
                       polygon: ArrayLike | None = None, wind: Wind | None = None) -> Candidate:
    """Evaluate one (altitude, speed factor, overlap) point; see the module docstring.

    ``fov`` in radians, ``orientation`` in radians (bearing of the tracks), lengths in metres.
    ``polygon`` (local ENU about ``area_center`` [m]) replaces the ``width × length`` rectangle.
    """
    c = Candidate(altitude, speed_factor, overlap)
    if not -1.0 < overlap < 1.0 or not speed_factor > 0 or not altitude > 0:
        return replace(c, reason="invalid variables")
    swath = sensor_swath(altitude, fov)
    S = swath * (1.0 - overlap)
    try:
        V = speed_factor * best_endurance_speed(ac, altitude, ac.W0)
    except ValueError as exc:
        return replace(c, reason=str(exc))
    c = replace(c, speed=V, swath=swath, spacing=S)
    if 1.2 * ac.stall_speed(altitude, ac.W0) - V > 1e-9:
        return replace(c, reason="speed below 1.2 V_stall")
    frame = LocalFrame(area_center[0], area_center[1])
    pat, area = _pattern(kind, width, length, S, orientation, frame, polygon)
    try:
        T, res = max_time_on_station(ac, base, pat, altitude, search_speed=V, reserve=reserve, dt=dt, wind=wind)
        complete = res.search_distance >= pat.length
        if complete:
            res = search_mission(ac, base, pat, altitude, search_speed=V, reserve=reserve, dt=dt, wind=wind)
    except (ValueError, FuelExhaustedError) as exc:
        return replace(c, reason=str(exc).split(" — ")[0][:80])
    # the flown route is the geodesic between the waypoints, a little shorter than the planar pattern
    dist = pat.length if complete else min(res.search_distance, pat.length)
    cov = pattern_coverage(pat, swath, distance=dist)
    pod = random_search_pod(sweep_width_factor * swath, dist, area)
    return replace(c, coverage=cov.fraction, covered_area=cov.covered_area, pod=pod, fuel_used=res.fuel_used,
                   time_on_station=res.time_on_station, fuel_margin=res.fuel_margin, complete=complete,
                   feasible=True)


def optimize_search(ac: Aircraft, base: tuple[float, float], area_center: tuple[float, float], width: float,
                    length: float, fov: float, *, altitudes: Sequence[float],
                    speed_factors: Sequence[float] = (1.0, 1.15, 1.3), overlaps: Sequence[float] = (0.0, 0.1, 0.2),
                    min_altitude: float = 0.0, max_altitude: float = math.inf,
                    objective: Literal["area", "pod"] = "area", refine: bool = True, orientation: float = 0.0,
                    reserve: Loiter | float = RESERVE_30MIN, sweep_width_factor: float = 1.0,
                    dt: float = 30.0, kind: str = "PS", polygon: ArrayLike | None = None,
                    wind: Wind | None = None) -> OptimizationResult:
    """Grid search plus local refinement of a PS/CS search over a rectangle or a polygon.

    Parameters
    ----------
    ac : Aircraft
    base, area_center : (lat, lon)
        [deg].
    width, length : float
        Area extents across and along the tracks [m].
    fov : float
        Imager full field of view [rad].
    altitudes, speed_factors, overlaps : sequences
        Grid values (speed factor relative to the best-endurance speed at W0).
    min_altitude, max_altitude : float
        Sensor altitude limits [m]; grid points outside are dropped.
    objective : "area" or "pod"
    refine : bool
        Coordinate refinement (two halvings) around the best grid point.
    kind : "PS" or "CS"
    polygon : array_like, optional
        Search area (local ENU about ``area_center`` [m]) instead of ``width × length``.
    wind : Wind, optional
        Constant wind (see :mod:`aerokit.mission.simulate`).

    Raises
    ------
    ValueError
        Empty grid or no feasible candidate.
    """
    if objective not in ("area", "pod"):
        raise ValueError("objective must be 'area' or 'pod'")
    hs = [h for h in altitudes if min_altitude <= h <= max_altitude]
    if not hs or not speed_factors or not overlaps:
        raise ValueError("empty grid (check the altitude limits)")
    cache: dict[tuple[float, float, float], Candidate] = {}

    def ev(h: float, k: float, o: float) -> Candidate:
        key = (round(h, 6), round(k, 9), round(o, 9))
        if key not in cache:
            cache[key] = evaluate_candidate(ac, base, area_center, width, length, fov, h, k, o,
                                            orientation=orientation, reserve=reserve,
                                            sweep_width_factor=sweep_width_factor, dt=dt, kind=kind,
                                            polygon=polygon, wind=wind)
        return cache[key]

    for h in hs:
        for k in speed_factors:
            for o in overlaps:
                ev(h, k, o)
    best = max(cache.values(), key=lambda c: c.rank(objective))
    if not best.feasible:
        raise ValueError("no feasible candidate: " + "; ".join(sorted({c.reason for c in cache.values()}))[:300])
    if refine:
        def step(vals: Sequence[float], default: float) -> float:
            v = sorted(set(vals))
            return min(b - a for a, b in zip(v[:-1], v[1:], strict=True)) / 2.0 if len(v) > 1 else default
        steps = [step(hs, 0.1 * best.altitude), step(speed_factors, 0.05), step(overlaps, 0.05)]
        for _ in range(2):
            for i in range(3):
                for sgn in (-1.0, 1.0):
                    x = [best.altitude, best.speed_factor, best.overlap]
                    x[i] += sgn * steps[i]
                    if not min_altitude <= x[0] <= max_altitude or x[0] <= 0:
                        continue
                    c = ev(x[0], x[1], x[2])
                    if c.rank(objective) > best.rank(objective):
                        best = c
            steps = [s / 2.0 for s in steps]
    cands = tuple(cache.values())
    return OptimizationResult(best, cands, pareto_front(cands), objective)
