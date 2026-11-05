"""IAMSAR pattern geometry (closed forms) and swath coverage (exact rectangle union vs raster)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from aerokit.mission import coverage as C
from aerokit.mission import patterns as P
from aerokit.mission.geodesy import LocalFrame
from aerokit.units import UnitError
from aerokit.verification import check


def test_swath_and_spacing_with_units():
    check("swath 1500 m, 60 deg", P.sensor_swath("1500 m", "60 deg"), 2 * 1500 * math.tan(math.radians(30)),
          rtol=1e-14, source="flat-ground nadir imager 2 h tan(FOV/2)")
    assert P.sensor_swath(1500.0, math.radians(60)) == pytest.approx(1732.0508075688772)
    assert P.sensor_swath("4921.26 ft", "60 deg") == pytest.approx(1732.05, rel=1e-5)
    assert P.track_spacing("1500 m", "60 deg", "10 %") == pytest.approx(0.9 * 1732.0508075688772)
    with pytest.raises(ValueError, match="radians"):
        P.sensor_swath(1500.0, 60)                      # 60 rad is not a field of view
    with pytest.raises(UnitError):
        P.sensor_swath("1500 m/s", "60 deg")
    with pytest.raises(ValueError):
        P.track_spacing(1500.0, 1.0, 1.0)


@pytest.mark.parametrize("W,L,S,e", [(8000, 20000, 2000, 0), (8000, 20000, 1999, 0), (8001, 20000, 2000, 300),
                                     (50e3, 50e3, 1558.85, 0), (1000, 5000, 3000, -100)])
def test_parallel_track_count_and_length(W, L, S, e):
    p = P.parallel_track(W, L, S, end_extension=e)
    n = math.ceil(W / S)
    assert len(p.xy) == 2 * n
    assert p.length == pytest.approx(n * (L + 2 * e) + (n - 1) * S, rel=1e-12)
    xs = np.unique(np.round(p.xy[:, 0], 6))
    assert xs[0] == pytest.approx(-W / 2 + S / 2) and np.allclose(np.diff(xs), S)


def test_creeping_line_count_and_length():
    p = P.creeping_line(8000, 20000, 2500)
    n = math.ceil(20000 / 2500)
    assert len(p.xy) == 2 * n and p.length == pytest.approx(n * 8000 + (n - 1) * 2500)
    assert np.allclose(p.xy[0], [-4000, -10000 + 1250]) and np.allclose(p.xy[1], [4000, -10000 + 1250])


def test_expanding_square_and_sector_closed_forms():
    for m in (1, 2, 5):
        s = P.expanding_square(100.0, n_legs=2 * m)
        assert s.length == pytest.approx(100.0 * m * (m + 1))
    sq = P.expanding_square(500.0, extent=5000.0)
    half = 5000 / 2 - 250
    assert sq.xy[:, 0].min() <= -half + 1e-9 and sq.xy[:, 1].max() >= half - 1e-9
    v = P.sector_search("2 km")
    seg = np.hypot(*np.diff(v.xy, axis=0).T)
    assert v.n_legs == 9 and np.allclose(seg, 2000.0) and v.length == pytest.approx(9 * 2000.0)
    assert np.allclose(v.xy[[0, 3, 6, 9]], 0.0, atol=1e-6)              # three passes over the datum
    with pytest.raises(ValueError):
        P.expanding_square(100.0)


def test_full_coverage_when_spacing_not_above_swath():
    w = 1000.0
    for ratio in (1.0, 0.9, 0.5):
        p = P.parallel_track(8000, 20000, ratio * w)
        assert C.pattern_coverage(p, w).fraction == pytest.approx(1.0, abs=1e-12)
        assert C.pattern_coverage(p, w, resolution=25.0).fraction == pytest.approx(1.0, abs=1e-12)
    c = P.creeping_line(8000, 20000, w)
    assert C.pattern_coverage(c, w).fraction == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("n", [2, 4, 7])
def test_spacing_twice_swath_expected_fraction(n):
    """Tracks sweep n·w·L; each of the n−1 end connectors adds w²/2 inside → ½ + (n−1)w/(4nL)."""
    w, L = 1000.0, 20000.0
    p = P.parallel_track(n * 2 * w, L, 2 * w)
    expected = 0.5 + (n - 1) * w / (4 * n * L)
    exact = C.pattern_coverage(p, w)
    check(f"PS coverage, S = 2 swath, n = {n}", exact.fraction, expected, rtol=1e-12,
          source="closed-form union of swept rectangles (derived in the test docstring)")
    raster = C.pattern_coverage(p, w, resolution=20.0)
    assert raster.fraction == pytest.approx(expected, rel=5e-3)


def test_raster_matches_exact_on_truncated_and_rotated_routes():
    w = 1200.0
    p = P.parallel_track(30e3, 20e3, 1500.0)
    for d in (0.0, 15e3, 0.37 * p.length, p.length):
        ex = C.pattern_coverage(p, w, distance=d)
        ra = C.pattern_coverage(p, w, distance=d, resolution=25.0)
        assert abs(ex.fraction - ra.fraction) < 3e-3
    rot = P.parallel_track(30e3, 20e3, 1500.0, orientation="30 deg", center=(5e3, -2e3))
    ra = C.coverage_raster(rot.area_en, rot.truncated(0.37 * rot.length).en, w, 25.0)
    assert abs(ra.fraction - C.pattern_coverage(p, w, distance=0.37 * p.length).fraction) < 3e-3


def test_exact_method_rejects_oblique_legs_and_pod_hook():
    with pytest.raises(ValueError):
        C.coverage_rectangles_exact((0, 10, 0, 10), [[0, 0], [5, 5]], 1.0)
    square = [[0, 0], [1000, 0], [1000, 1000], [0, 1000]]
    leg = [[500, -10], [500, 1010]]
    r1 = C.coverage_raster(square, leg, 200.0, 5.0, lateral_range=lambda d: np.ones_like(d))
    assert r1.pod == pytest.approx(r1.fraction) and r1.fraction == pytest.approx(0.2, abs=6e-3)
    r2 = C.coverage_raster(square, leg, 200.0, 5.0, lateral_range=lambda d: 0.5 * np.ones_like(d))
    assert r2.pod == pytest.approx(0.5 * r2.fraction)
    assert C.random_search_pod(1000.0, 50e3, 50e6) == pytest.approx(1 - math.exp(-1.0))


def test_pattern_maps_to_geodetic_and_back():
    fr = LocalFrame(39.0, 33.5)
    p = P.parallel_track("50 km", "50 km", "1.56 km", orientation="15 deg", frame=fr)
    lat, lon = p.geodetic()
    e, n, _ = fr.to_enu(lat, lon)
    # surface points sit below the tangent plane; horizontal offset < 3 m within 36 km of the origin
    assert np.max(np.hypot(e - p.en[:, 0], n - p.en[:, 1])) < 3.0
    with pytest.raises(ValueError):
        P.parallel_track(1000, 1000, 100).geodetic()
