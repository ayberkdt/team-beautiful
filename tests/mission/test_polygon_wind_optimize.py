"""Polygon search areas, constant wind and the search optimiser in ``sizing mission`` (docs/07 A5).

Each test pins one property that the A5 change introduced: the wind triangle, the polygon ladder (which
must reduce to the rectangle ladder for a rectangle), the mission-file keys, and the optimiser beating
the fixed 2023 rehearsal plan.
"""
from __future__ import annotations

import json
import math

import numpy as np
import pytest

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.propulsion import Turboprop
from aerokit.data import example_path
from aerokit.design import mission_plan as mpl
from aerokit.mission import patterns as P
from aerokit.mission.coverage import pattern_coverage, polygon_area_xy
from aerokit.mission.geodesy import LocalFrame
from aerokit.mission.simulate import Cruise, Loiter, Wind, search_mission, simulate
from aerokit.units import UnitError
from aerokit.verification import check, check_true, expect_error

MISSION = example_path("design", "ansys_2023_mission.json")


@pytest.fixture(scope="module")
def ac():
    return Aircraft("rehearsal", 5974 * G0, 27.5, 9, 0.0280, 0.783, Turboprop(1667e3), W_fuel=0.156 * 5974 * G0)


def mission(**changes):
    raw = json.loads(MISSION.read_text(encoding="utf-8"))
    raw.update(changes)
    return {k: v for k, v in raw.items() if v is not None}


# --- wind triangle ---------------------------------------------------------------------------------
def test_wind_triangle_components():
    east, north = math.radians(90), 0.0
    w = Wind(20.0, math.radians(90))           # from the east
    check("headwind flying east: V − w", w.ground_speed(80.0, east), 60.0, rtol=1e-12,
          source="wind triangle, along-track wind")
    check("tailwind flying west: V + w", w.ground_speed(80.0, math.radians(270)), 100.0, rtol=1e-12)
    check("crosswind flying north: √(V² − w²)", w.ground_speed(80.0, north), math.sqrt(80**2 - 20**2), rtol=1e-12)
    expect_error("crosswind ≥ airspeed rejected", Wind(90.0, math.radians(90)).ground_speed, 80.0, north,
                 error=ValueError)
    expect_error("headwind ≥ airspeed rejected", Wind(90.0, math.radians(90)).ground_speed, 80.0, east,
                 error=ValueError)
    expect_error("negative wind speed rejected", Wind, -1.0, 0.0, error=ValueError)


def test_fixed_speed_cruise_time_in_headwind(ac):
    V, w, D = 80.0, 15.0, 200e3
    r = simulate(ac, [Cruise(D, V, track=lambda s: 0.0)], h_start=3000.0, wind=Wind(w, 0.0))   # from north, fly north
    check("cruise time = D/(V − w)", r.records[0].duration, D / (V - w), rtol=1e-9)
    calm = simulate(ac, [Cruise(D, V, track=lambda s: 0.0)], h_start=3000.0)
    check_true("headwind burns more fuel over the same ground distance", r.fuel_used > calm.fuel_used * 1.2,
               f"{r.fuel_used / G0:.1f} vs {calm.fuel_used / G0:.1f} kg")


def test_segments_without_track_fly_in_the_air_mass(ac):
    calm = simulate(ac, [Loiter(1800.0, 70.0)], h_start=1500.0)
    windy = simulate(ac, [Loiter(1800.0, 70.0)], h_start=1500.0, wind=Wind(25.0, 1.0))
    check("holding: distance unchanged by the wind", windy.records[0].distance, calm.records[0].distance, rtol=1e-12)
    check("holding: fuel unchanged by the wind", windy.fuel_used, calm.fuel_used, rtol=1e-12)


def test_zero_wind_equals_no_wind(ac):
    frame = LocalFrame(39.0, 34.6)
    pat = P.parallel_track(20e3, 20e3, 1559.0, frame=frame)
    a = search_mission(ac, (39.0, 30.0), pat, 1500.0, dt=30.0)
    b = search_mission(ac, (39.0, 30.0), pat, 1500.0, dt=30.0, wind=Wind(0.0, 1.0))
    check("Wind(0) reproduces the calm mission fuel", b.fuel_used, a.fuel_used, rtol=1e-12)


def test_out_and_back_wind_costs_fuel_and_shifts_ground_speed(ac):
    calm = mpl.plan(ac, mpl.load_mission(mission()))
    windy = mpl.plan(ac, mpl.load_mission(mission(wind_speed="40 km/h", wind_from="90 deg")))
    gs = {r.name: r.V_mean * 3.6 for r in calm.result.records}
    gw = {r.name: r.V_mean * 3.6 for r in windy.result.records}
    check("cruise out (east, into the wind): ground speed −40 km/h", gw["cruise out"], gs["cruise out"] - 40.0,
          atol=1.0)
    check("cruise back (west, wind behind): ground speed +40 km/h", gw["cruise back"], gs["cruise back"] + 40.0,
          atol=1.0)
    check_true("a head/tail wind pair costs coverage (more time spent in the headwind)",
               windy.coverage < calm.coverage, f"{calm.coverage:.3f} → {windy.coverage:.3f}")


# --- polygon ladder --------------------------------------------------------------------------------
@pytest.mark.parametrize("orientation", [0.0, math.radians(30.0)])
def test_rectangle_polygon_reproduces_rectangle_ladder(orientation):
    W, L, S = 50e3, 30e3, 1559.0
    rect = P.parallel_track(W, L, S, orientation=orientation)
    poly_en = rect.area_en
    poly = P.polygon_track(poly_en, S, orientation=orientation)
    check_true("same number of legs", poly.n_legs == rect.n_legs, f"{poly.n_legs} vs {rect.n_legs}")
    check("same route length", poly.length, rect.length, rtol=1e-9)
    check("same waypoints (ENU)", float(np.abs(poly.en - rect.en).max()), 0.0, atol=1e-6)


def test_triangle_is_fully_covered_with_a_shorter_route():
    tri = np.array([[0.0, 0.0], [40e3, 0.0], [0.0, 30e3]])
    S, swath = 1559.0, 1732.0
    pat = P.polygon_track(tri, S)
    cov = pattern_coverage(pat, swath)
    check("triangle covered by its own ladder (raster)", cov.fraction, 1.0, atol=2e-3)
    box = P.parallel_track(40e3, 30e3, S)
    check_true("route shorter than the bounding-box ladder", pat.length < 0.75 * box.length,
               f"{pat.length / 1e3:.0f} vs {box.length / 1e3:.0f} km")
    check_true("no waypoint outside the triangle's bounding box", bool(
        (pat.en[:, 0] >= -S).all() and (pat.en[:, 0] <= 40e3 + S).all() and (pat.en[:, 1] >= -1e-6).all()
        and (pat.en[:, 1] <= 30e3 + 1e-6).all()))


def test_non_convex_polygon_is_covered():
    ell = np.array([[0, 0], [30e3, 0], [30e3, 10e3], [10e3, 10e3], [10e3, 30e3], [0, 30e3]], float)
    pat = P.polygon_track(ell, 1559.0, kind="CS")
    check("L-shaped area covered (notch flown over)", pattern_coverage(pat, 1732.0).fraction, 1.0, atol=2e-3)


def test_polygon_helpers_and_validation():
    c = P.polygon_centroid([[0, 0], [4, 0], [4, 2], [0, 2]])
    check("rectangle centroid x", c[0], 2.0, rtol=1e-12)
    check("rectangle centroid y", c[1], 1.0, rtol=1e-12)
    t = P.polygon_centroid([[0, 0], [3, 0], [0, 3]])
    check("triangle centroid = vertex mean", t[0], 1.0, rtol=1e-12)
    expect_error("two points rejected", P.polygon_track, [[0, 0], [1, 1]], 100.0, error=ValueError)
    expect_error("collinear points rejected", P.polygon_track, [[0, 0], [1, 1], [2, 2]], 100.0, error=ValueError)
    expect_error("SS kind rejected", P.polygon_track, [[0, 0], [1e3, 0], [0, 1e3]], 100.0, kind="SS",
                 error=ValueError)


# --- mission file ----------------------------------------------------------------------------------
POLY = [[39.10, 34.40], [39.30, 34.85], [38.95, 35.05], [38.75, 34.60]]


def test_mission_file_polygon_and_wind_keys():
    spec = mpl.load_mission(mission(area_bearing=None, area_distance=None, area_width=None, area_length=None,
                                    area_polygon=POLY, wind_speed="20 kt", wind_from="270 deg"))
    check_true("polygon parsed", spec.area_polygon is not None and len(spec.area_polygon) == 4)
    check("wind speed 20 kt", spec.wind.speed, 20 * 1852 / 3600, rtol=1e-12)
    check("wind from 270°", spec.wind.from_direction, math.radians(270), rtol=1e-12)
    frame = LocalFrame(*spec.area_center)
    en = mpl.area_en(spec, frame)
    cx, cy = P.polygon_centroid(en)
    check("area centre is the polygon centroid (east)", cx, 0.0, atol=1.0)
    check("area centre is the polygon centroid (north)", cy, 0.0, atol=1.0)


@pytest.mark.parametrize("changes, why", [
    ({"area_polygon": POLY}, "polygon together with rectangle keys"),
    ({"area_polygon": POLY[:2], "area_bearing": None, "area_distance": None, "area_width": None,
      "area_length": None}, "polygon with 2 vertices"),
    ({"wind_speed": "10 m/s"}, "wind speed without direction"),
    ({"max_search_altitude": "1000 m"}, "search altitude above the sensor limit"),
])
def test_mission_file_rejects(changes, why):
    expect_error(f"rejected: {why}", mpl.load_mission, mission(**changes), error=UnitError)


def test_polygon_plan_area_matches_geodesic_area(ac):
    spec = mpl.load_mission(mission(area_bearing=None, area_distance=None, area_width=None, area_length=None,
                                    area_polygon=POLY))
    mp = mpl.plan(ac, spec, dt=30.0)
    en = mpl.area_en(spec, LocalFrame(*spec.area_center))
    check("plan area = planar polygon area (local frame)", mp.area_km2, polygon_area_xy(en) / 1e6, rtol=2e-3)
    check_true("polygon plan coverage in (0, 1]", 0 < mp.coverage <= 1, mp.coverage)


# --- optimiser -------------------------------------------------------------------------------------
def test_optimizer_beats_the_fixed_rehearsal_plan(ac):
    spec = mpl.load_mission(mission())
    fixed = mpl.plan(ac, spec, dt=30.0)
    opt, best = mpl.optimize(ac, spec, altitudes=[1500.0, 3000.0], speed_factors=(1.0, 1.15), overlaps=(0.1,))
    mp = mpl.plan(ac, best, dt=30.0)
    check_true("optimised plan covers more than the fixed 1500 m plan", mp.coverage > fixed.coverage,
               f"{fixed.coverage:.3f} → {mp.coverage:.3f}")
    check("plan of the best point reproduces the optimiser's coverage", mp.coverage, opt.best.coverage, atol=5e-3)
    if mp.full_pattern_fits:
        check_true("complete pattern: the unused fuel is a positive margin", mp.result.fuel_margin > 0)


def test_optimizer_respects_sensor_limit_and_pattern_kind(ac):
    spec = mpl.load_mission(mission(max_search_altitude="1600 m"))
    _, best = mpl.optimize(ac, spec, speed_factors=(1.0,), overlaps=(0.1,))
    check_true("best altitude within the sensor limit", best.search_altitude <= 1600.0, best.search_altitude)
    expect_error("SS pattern is not optimised", mpl.optimize, ac, mpl.load_mission(mission(pattern="SS")),
                 error=ValueError)


def test_complete_pattern_is_flown_once(ac):
    small = mpl.load_mission(mission(area_width="10 km", area_length="10 km"))
    mp = mpl.plan(ac, small, dt=30.0)
    check_true("10 × 10 km area fits", mp.full_pattern_fits)
    check("time on station = pattern length / search ground speed (one pass)", mp.time_on_station,
          mp.result.search_distance / next(r.V_mean for r in mp.result.records if r.kind == "search"), rtol=1e-9)
    check_true("fuel left over is margin, not burned holding", mp.result.fuel_margin > 0.05 * mp.result.fuel)
