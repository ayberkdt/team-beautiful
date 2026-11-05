"""Leg 2 of the Ansys task: search-mission plan for a sized aircraft (route, pattern, coverage, export).

A mission file (JSON, values with units) describes the base, the search area and the sensor::

    {"base": [39.0, 30.0], "area_bearing": "90 deg", "area_distance": "400 km",
     "area_width": "50 km", "area_length": "50 km", "pattern": "PS", "search_altitude": "1500 m",
     "fov": "60 deg", "overlap": "10 %"}

The area is either a rectangle (``area_width`` × ``area_length`` about ``area_center``, or about the
point ``area_bearing``/``area_distance`` from the base) or a polygon, ``"area_polygon": [[lat, lon],
...]`` (≥ 3 vertices; the pattern is centred on its area centroid). A constant wind is given as
``"wind_speed": "20 kt", "wind_from": "270 deg"`` (meteorological: the direction it blows from).
``min_search_altitude``/``max_search_altitude`` bound the altitudes the optimiser may choose (e.g. the
maximum from the required ground resolution).

``plan(aircraft, mission)`` flies base → area → search → base with the time-stepped simulator of
:mod:`aerokit.mission.simulate`, finds the longest time on station the fuel allows (30-min reserve),
computes the covered fraction, and returns the waypoints for STK/Google Earth and the Aviator sheet.
``optimize(aircraft, mission)`` first searches altitude × speed × overlap with
:func:`aerokit.mission.optimize.optimize_search` and returns the mission file of the best point.
"""
from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from aerokit import units
from aerokit.aero.aircraft import Aircraft
from aerokit.mission import export, patterns
from aerokit.mission.coverage import pattern_coverage
from aerokit.mission.geodesy import LocalFrame, direct, polygon_area
from aerokit.mission.optimize import OptimizationResult, optimize_search
from aerokit.mission.simulate import MissionResult, SpeedSpec, Wind, max_time_on_station, search_mission

__all__ = ["MISSION_SCHEMA", "MissionSpec", "MissionPlan", "load_mission", "plan", "optimize", "area_en",
           "build_pattern", "OPTIMIZE_ALTITUDE_FACTORS"]

MISSION_SCHEMA: dict[str, str] = {
    "area_bearing": "angle", "area_distance": "length", "area_width": "length", "area_length": "length",
    "search_altitude": "length", "cruise_altitude": "length", "fov": "angle", "overlap": "dimensionless",
    "orientation": "angle", "wind_speed": "speed", "wind_from": "angle", "min_search_altitude": "length",
    "max_search_altitude": "length",
}
_OTHER = {"base", "area_center", "area_polygon", "pattern", "name", "source", "notes"}
_RECTANGLE_KEYS = ("area_center", "area_bearing", "area_distance", "area_width", "area_length")

#: altitude grid of :func:`optimize` as multiples of the mission file's ``search_altitude``
OPTIMIZE_ALTITUDE_FACTORS = (0.5, 0.75, 1.0, 1.5, 2.0)


@dataclass(frozen=True)
class MissionSpec:
    """Parsed mission file (SI, angles in radians, positions in degrees).

    ``width``/``length`` are 0 when the area is ``area_polygon`` ((lat, lon) vertices); ``search_speed``
    is a fixed TAS [m/s] (``None``: best-endurance speed), set by :func:`optimize`.
    """

    base: tuple[float, float]
    area_center: tuple[float, float]
    width: float
    length: float
    pattern: str
    search_altitude: float
    cruise_altitude: float | None
    fov: float
    overlap: float
    orientation: float
    name: str = "mission"
    area_polygon: tuple[tuple[float, float], ...] | None = None
    wind: Wind | None = None
    search_speed: float | None = None
    min_search_altitude: float = 0.0
    max_search_altitude: float = math.inf


def _latlon(v: Any, key: str) -> tuple[float, float]:
    if not (isinstance(v, list | tuple) and len(v) == 2 and all(isinstance(x, int | float) for x in v)):
        raise units.UnitError(f"{key} must be [latitude, longitude] in degrees")
    lat, lon = float(v[0]), float(v[1])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise units.UnitError(f"{key} out of range: {v}")
    return lat, lon


def _polygon(raw: Any) -> tuple[tuple[tuple[float, float], ...], tuple[float, float]]:
    """Vertices and the area centroid (lat, lon) of ``area_polygon``."""
    if not isinstance(raw, list | tuple) or len(raw) < 3:
        raise units.UnitError("area_polygon must be a list of >= 3 [latitude, longitude] pairs")
    verts = tuple(_latlon(v, f"area_polygon[{i}]") for i, v in enumerate(raw))
    lat0 = sum(v[0] for v in verts) / len(verts)
    lon0 = sum(v[1] for v in verts) / len(verts)
    f0 = LocalFrame(lat0, lon0)
    e, n, _ = f0.to_enu([v[0] for v in verts], [v[1] for v in verts])
    try:
        ce, cn = patterns.polygon_centroid(np.column_stack([e, n]))
    except ValueError as exc:
        raise units.UnitError(f"area_polygon: {exc}") from exc
    la, lo = f0.surface(ce, cn)
    return verts, (float(la), float(lo))


def load_mission(path: str | Path | Mapping[str, Any]) -> MissionSpec:
    """Read and validate a mission file (unknown keys raise)."""
    raw = dict(path) if isinstance(path, Mapping) else json.loads(Path(path).read_text(encoding="utf-8"))
    unknown = set(raw) - set(MISSION_SCHEMA) - _OTHER
    if unknown:
        raise units.UnitError(f"unknown mission key(s): {', '.join(sorted(unknown))}")
    q = {k: units.parse(v, MISSION_SCHEMA[k]) for k, v in raw.items() if k in MISSION_SCHEMA}
    base = _latlon(raw.get("base"), "base")
    polygon = None
    if "area_polygon" in raw:
        clash = [k for k in _RECTANGLE_KEYS if k in raw]
        if clash:
            raise units.UnitError(f"give either area_polygon or the rectangle keys, not both ({', '.join(clash)})")
        polygon, center = _polygon(raw["area_polygon"])
        width = length = 0.0
    else:
        if "area_center" in raw:
            center = _latlon(raw["area_center"], "area_center")
        else:
            if "area_bearing" not in q or "area_distance" not in q:
                raise units.UnitError("give area_polygon, area_center, or area_bearing and area_distance")
            la, lo, _ = direct(base[0], base[1], float(np.degrees(q["area_bearing"])), q["area_distance"])
            center = (la, lo)
        for k in ("area_width", "area_length"):
            if k not in q:
                raise units.UnitError(f"mission needs {k} (or area_polygon)")
        width, length = q["area_width"], q["area_length"]
    kind = str(raw.get("pattern", "PS")).upper()
    if kind not in ("PS", "CS", "SS"):
        raise units.UnitError("pattern must be PS (parallel track), CS (creeping line) or SS (expanding square)")
    for k in ("search_altitude", "fov"):
        if k not in q:
            raise units.UnitError(f"mission needs {k}")
    wind = None
    if q.get("wind_speed", 0.0) > 0:
        if "wind_from" not in q:
            raise units.UnitError("wind_speed needs wind_from (direction the wind blows from)")
        wind = Wind(q["wind_speed"], q["wind_from"])
    h_min, h_max = q.get("min_search_altitude", 0.0), q.get("max_search_altitude", math.inf)
    if not h_min <= q["search_altitude"] <= h_max:
        raise units.UnitError("search_altitude must lie within min_search_altitude … max_search_altitude")
    return MissionSpec(base, center, width, length, kind, q["search_altitude"], q.get("cruise_altitude"), q["fov"],
                       q.get("overlap", 0.1), q.get("orientation", 0.0), str(raw.get("name", "mission")),
                       polygon, wind, None, h_min, h_max)


def area_en(spec: MissionSpec, frame: LocalFrame) -> npt.NDArray[np.float64] | None:
    """The polygon vertices in ``frame`` (local ENU) [m], or ``None`` for a rectangle."""
    if spec.area_polygon is None:
        return None
    e, n, _ = frame.to_enu([v[0] for v in spec.area_polygon], [v[1] for v in spec.area_polygon])
    return np.column_stack([e, n])


def build_pattern(spec: MissionSpec, spacing: float, frame: LocalFrame) -> patterns.SearchPattern:
    """The search pattern of ``spec`` with track spacing ``spacing`` [m]."""
    poly = area_en(spec, frame)
    if poly is not None:
        if spec.pattern in ("PS", "CS"):
            return patterns.polygon_track(poly, spacing, orientation=spec.orientation, kind=spec.pattern, frame=frame)
        extent = float(max(np.ptp(poly[:, 0]), np.ptp(poly[:, 1])))
        return patterns.expanding_square(spacing, extent=extent, orientation=spec.orientation,
                                         frame=frame).with_area(poly)
    if spec.pattern == "PS":
        return patterns.parallel_track(spec.width, spec.length, spacing, orientation=spec.orientation, frame=frame)
    if spec.pattern == "CS":
        return patterns.creeping_line(spec.width, spec.length, spacing, orientation=spec.orientation, frame=frame)
    return patterns.expanding_square(spacing, extent=max(spec.width, spec.length), orientation=spec.orientation,
                                     frame=frame)


@dataclass
class MissionPlan:
    """Result of :func:`plan`."""

    spec: MissionSpec
    pattern: patterns.SearchPattern
    swath: float
    spacing: float
    time_on_station: float
    coverage: float
    full_pattern_fits: bool
    result: MissionResult
    route_lat: npt.NDArray[np.float64]
    route_lon: npt.NDArray[np.float64]
    route_names: list[str]
    area_km2: float


def plan(ac: Aircraft, spec: MissionSpec, dt: float = 10.0) -> MissionPlan:
    """Search the fuel allows, its coverage, and the flown route (see module docstring).

    If the whole pattern fits, the mission flies the pattern once and returns (the unused fuel is the
    margin); otherwise it searches for the longest time that keeps the reserve.
    """
    swath = patterns.sensor_swath(spec.search_altitude, spec.fov)
    spacing = patterns.track_spacing(spec.search_altitude, spec.fov, spec.overlap)
    frame = LocalFrame(*spec.area_center)
    pat = build_pattern(spec, spacing, frame)
    speed: SpeedSpec = spec.search_speed if spec.search_speed is not None else "best_endurance"
    T, res = max_time_on_station(ac, spec.base, pat, spec.search_altitude, cruise_altitude=spec.cruise_altitude,
                                 search_speed=speed, dt=dt, wind=spec.wind)
    complete = res.search_distance >= pat.length
    if complete:
        res = search_mission(ac, spec.base, pat, spec.search_altitude, cruise_altitude=spec.cruise_altitude,
                             search_speed=speed, dt=dt, wind=spec.wind)
        T = res.time_on_station
    # the flown route is the geodesic between the waypoints, a little shorter than the planar pattern
    flown = pat.length if complete else min(res.search_distance, pat.length)
    cov = pattern_coverage(pat, swath, distance=flown).fraction
    searched = pat.truncated(flown) if flown < pat.length else pat
    lat, lon = searched.geodetic()
    route_lat = np.r_[spec.base[0], lat, spec.base[0]]
    route_lon = np.r_[spec.base[1], lon, spec.base[1]]
    names = ["BASE"] + [f"S{i:03d}" for i in range(len(lat))] + ["BASE"]
    alat, alon = pat.area_geodetic()
    return MissionPlan(spec, pat, swath, spacing, T, cov, complete, res,
                       route_lat, route_lon, names, float(polygon_area(alat, alon)) / 1e6)


def optimize(ac: Aircraft, spec: MissionSpec, *, altitudes: Sequence[float] | None = None,
             speed_factors: Sequence[float] = (1.0, 1.15, 1.3), overlaps: Sequence[float] = (0.0, 0.1, 0.2),
             dt: float = 30.0) -> tuple[OptimizationResult, MissionSpec]:
    """Best (altitude, search speed, overlap) for the largest covered area, and the mission spec using it.

    The default altitude grid is :data:`OPTIMIZE_ALTITUDE_FACTORS` × ``search_altitude``, clipped to the
    sensor limits; speeds are multiples of the best-endurance speed at W0. Only PS and CS patterns are
    optimised.

    Raises
    ------
    ValueError
        SS pattern, empty grid or no feasible candidate.
    """
    if spec.pattern not in ("PS", "CS"):
        raise ValueError("the search optimiser lays PS or CS patterns; set pattern to PS or CS")
    hs = list(altitudes) if altitudes is not None else sorted({f * spec.search_altitude
                                                               for f in OPTIMIZE_ALTITUDE_FACTORS})
    frame = LocalFrame(*spec.area_center)
    res = optimize_search(ac, spec.base, spec.area_center, spec.width, spec.length, spec.fov, altitudes=hs,
                          speed_factors=speed_factors, overlaps=overlaps, min_altitude=spec.min_search_altitude,
                          max_altitude=spec.max_search_altitude, orientation=spec.orientation, dt=dt,
                          kind=spec.pattern, polygon=area_en(spec, frame), wind=spec.wind)
    b = res.best
    return res, replace(spec, search_altitude=b.altitude, overlap=b.overlap, search_speed=b.speed)


def map_figure(mp: MissionPlan, path: str, target: str = "web-640") -> Any:
    """Plan-view figure of the route and the pattern (see :func:`aerokit.output.figures.mission_map`)."""
    from aerokit.output import figures
    frame = mp.pattern.frame
    if frame is None or mp.pattern.area_en is None:
        raise ValueError("pattern has no frame or area polygon")
    e, n, _ = frame.to_enu(mp.spec.base[0], mp.spec.base[1])
    flown = min(mp.result.search_distance, mp.pattern.length)
    searched = mp.pattern.truncated(flown).en if flown < mp.pattern.length else mp.pattern.en
    return figures.mission_map((float(e), float(n)), mp.pattern.en, searched, mp.pattern.area_en, path,
                               mp.coverage, mp.time_on_station / 3600, target=target)


def write_outputs(ac: Aircraft, mp: MissionPlan, out_dir: str | Path) -> list[str]:
    """Waypoints (CSV/KML/GeoJSON) and the Aviator parameter sheet into ``out_dir``."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    alt = np.r_[0.0, np.full(mp.route_lat.size - 2, mp.spec.search_altitude), 0.0]
    files = export.write_waypoints(out / "waypoints", mp.route_lat, mp.route_lon, alt, mp.route_names)
    files += export.write_aviator_sheet(out / "aviator_sheet", export.aviator_sheet(ac))
    return [str(f) for f in files]
