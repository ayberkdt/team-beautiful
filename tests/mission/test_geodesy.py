"""WGS-84 geodesy: Vincenty self-consistency, closed-form limits and independent integrals.

No published reference pairs are used (none was read in this session); instead every expected
value is computed independently: ECEF chords for short lines, a·Δλ on the equator, scipy
quadrature of the meridian and zone-area integrals, and direct/inverse round trips.
"""
from __future__ import annotations

import importlib.util
import math

import numpy as np
import pytest
from scipy.integrate import quad

from aerokit.mission import geodesy as G
from aerokit.verification import check

A, E2 = G.WGS84_A, G.WGS84_E2


def _ecef(lat, lon):
    p, l = math.radians(lat), math.radians(lon)
    N = A / math.sqrt(1 - E2 * math.sin(p) ** 2)
    return np.array([N * math.cos(p) * math.cos(l), N * math.cos(p) * math.sin(l), N * (1 - E2) * math.sin(p)])


def _pairs(n=200, seed=1):
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        la1, la2 = rng.uniform(-89, 89, 2)
        lo1, lo2 = rng.uniform(-180, 180, 2)
        # stay clear of the nearly antipodal region where Vincenty's inverse may not converge
        if G.great_circle_distance(la1, lo1, -la2, lo2 + 180.0) > 300e3:
            out.append((la1, lo1, la2, lo2))
    return out


def test_direct_inverse_round_trip_below_1mm():
    worst = 0.0
    for la1, lo1, la2, lo2 in _pairs():
        g = G.inverse(la1, lo1, la2, lo2)
        la, lo, az2 = G.direct(la1, lo1, g.azimuth1, g.distance)
        miss = G.inverse(la, lo, la2, lo2).distance
        worst = max(worst, miss)
        assert abs((az2 - g.azimuth2 + 180) % 360 - 180) < 1e-6
    print(f"\nworst direct(inverse) miss over 200 random lines: {worst * 1e3:.2e} mm")
    assert worst < 1e-3


def test_inverse_of_direct_recovers_distance_and_azimuth():
    rng = np.random.default_rng(7)
    for _ in range(100):
        la1, lo1, az = rng.uniform(-80, 80), rng.uniform(-180, 180), rng.uniform(0, 360)
        s = rng.uniform(1.0, 15_000e3)
        la2, lo2, _ = G.direct(la1, lo1, az, s)
        g = G.inverse(la1, lo1, la2, lo2)
        assert abs(g.distance - s) < 1e-4
        assert abs((g.azimuth1 - az + 180) % 360 - 180) < 1e-7


@pytest.mark.parametrize("lat", [0.0, 37.0, 60.0, -75.0])
@pytest.mark.parametrize("az", [0.0, 45.0, 90.0, 200.0])
def test_short_line_limit_equals_ecef_chord(lat, az):
    """For s = 1 km the arc exceeds the chord by ≈ s³/(24 R²) ≈ 1e-6 m; both solvers agree to 10 µm."""
    la2, lo2, _ = G.direct(lat, 10.0, az, 1000.0)
    chord = float(np.linalg.norm(_ecef(la2, lo2) - _ecef(lat, 10.0)))
    s = G.inverse(lat, 10.0, la2, lo2).distance
    assert abs(s - 1000.0) < 1e-5
    assert abs(chord - 1000.0) < 1e-5


def test_equator_line_is_a_times_dlon():
    for dlon in (1.0, 30.0, 90.0, 150.0):
        g = G.inverse(0.0, 0.0, 0.0, dlon)
        check(f"equatorial geodesic {dlon} deg", g.distance, A * math.radians(dlon), rtol=1e-12, atol=1e-6,
              source="closed form: geodesic along the equator = a·Δλ (Δλ < (1−f)π)")


def test_meridian_arc_against_quadrature_and_vincenty():
    def integrand(p):
        return A * (1 - E2) / (1 - E2 * math.sin(p) ** 2) ** 1.5
    for lat in (10.0, 45.0, 89.0, 90.0):
        ref = quad(integrand, 0.0, math.radians(lat), epsabs=1e-9, epsrel=1e-12)[0]
        assert abs(G.meridian_arc(lat) - ref) < 1e-5
    q = quad(integrand, 0.0, math.pi / 2, epsabs=1e-9, epsrel=1e-12)[0]
    # Vincenty along a meridian (Δλ = 0 is solved in closed form) and a near-meridian line
    assert abs(G.inverse(0.0, 5.0, 60.0, 5.0).distance - G.meridian_arc(60.0)) < 1e-6
    near = G.inverse(0.0, 5.0, 60.0, 5.0 + 1e-9).distance
    assert abs(near - G.meridian_arc(60.0)) < 1e-3
    print(f"\nWGS-84 meridian quadrant (quadrature): {q:.4f} m")


def test_antipodal_limit_and_poles():
    q = G.meridian_arc(90.0)
    g = G.inverse(0.0, 0.0, 0.0, 180.0)                 # exactly antipodal on the equator: over a pole
    assert g.method == "meridian" and abs(g.distance - 2 * q) < 1e-6
    assert abs(G.inverse(30.0, 0.0, -30.0, 180.0).distance - 2 * q) < 1e-6
    assert abs(G.inverse(90.0, 0.0, -90.0, 0.0).distance - 2 * q) < 1e-6
    assert abs(G.inverse(90.0, 0.0, 45.0, 77.0).distance - (q - G.meridian_arc(45.0))) < 1e-6


def test_nearly_antipodal_fails_clearly_or_uses_karney():
    if importlib.util.find_spec("geographiclib") is not None:
        assert G.inverse(0.0, 0.0, 0.1, 179.9).method == "karney"
    else:
        with pytest.raises(G.GeodesicConvergenceError, match="geographiclib"):
            G.inverse(0.0, 0.0, 0.1, 179.9)


def test_haversine_within_half_percent_of_geodesic():
    for la1, lo1, la2, lo2 in _pairs(50, seed=3):
        g = G.inverse(la1, lo1, la2, lo2).distance
        assert abs(G.great_circle_distance(la1, lo1, la2, lo2) / g - 1) < 6e-3


def test_geodesic_path_points_lie_on_the_line():
    la, lo = G.geodesic_path(39.0, 30.0, 41.0, 36.0, 11)
    total = G.inverse(39.0, 30.0, 41.0, 36.0).distance
    for i in range(11):
        assert abs(G.inverse(39.0, 30.0, la[i], lo[i]).distance - total * i / 10) < 1e-3


def test_local_frame_round_trip_and_stated_distortion():
    fr = G.LocalFrame(39.3, 34.6, 120.0)
    e, n, u = np.array([0.0, 1234.5, -40e3, 50e3]), np.array([0.0, -987.6, 25e3, 50e3]), np.array([0.0, 10, -5, 0])
    lat, lon, h = fr.to_geodetic(e, n, u)
    e2, n2, u2 = fr.to_enu(lat, lon, h)
    assert np.max(np.abs(np.r_[e2 - e, n2 - n, u2 - u])) < 1e-6
    # surface mapping: geodesic distance from the origin vs tangent-plane distance (stated ≈ d²/(3R²))
    fr0 = G.LocalFrame(39.3, 34.6)
    for d in (10e3, 50e3):
        for bearing in (0.0, 45.0, 90.0):
            la, lo = fr0.surface(d * math.sin(math.radians(bearing)), d * math.cos(math.radians(bearing)))
            s = G.inverse(39.3, 34.6, float(la), float(lo)).distance
            rel = abs(s - d) / d
            assert rel < 1.5 * d ** 2 / (3 * G.MEAN_RADIUS ** 2) + 1e-9


def test_polygon_area_zone_quadrature_and_local_square():
    # quad bounded by parallels 30-32 deg and meridians 10-13 deg; every edge densified, because
    # edges are straight in the equal-area projection (undensified meridian edges: ~8e-5 error)
    lat1, lat2, lon1, lon2 = 30.0, 32.0, 10.0, 13.0
    n = 400
    lo, la_ = np.linspace(lon1, lon2, n), np.linspace(lat1, lat2, n)
    lat = np.r_[np.full(n, lat1), la_, np.full(n, lat2), la_[::-1]]
    lon = np.r_[lo, np.full(n, lon2), lo[::-1], np.full(n, lon1)]

    def dA(p):
        s = math.sin(p)
        M = A * (1 - E2) / (1 - E2 * s * s) ** 1.5
        N = A / math.sqrt(1 - E2 * s * s)
        return M * N * math.cos(p)
    ref = math.radians(lon2 - lon1) * quad(dA, math.radians(lat1), math.radians(lat2), epsrel=1e-13)[0]
    got = G.polygon_area(lat, lon)
    check("ellipsoidal zone area 30-32N x 3 deg", got, ref, rtol=2e-6,
          source="independent quadrature of M(φ)N(φ)cosφ dφ dλ")
    # 50 km square drawn in a local frame
    fr = G.LocalFrame(39.0, 33.5)
    la, lo2 = fr.surface([-25e3, 25e3, 25e3, -25e3], [-25e3, -25e3, 25e3, 25e3])
    assert abs(G.polygon_area(la, lo2) / 2.5e9 - 1) < 1e-4


def test_input_validation():
    with pytest.raises(ValueError):
        G.inverse(91.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        G.direct(0.0, 0.0, 0.0, -1.0)
    with pytest.raises(ValueError):
        G.polygon_area([0, 1], [0, 1])
    assert G.inverse(10.0, 20.0, 10.0, 20.0).distance == 0.0
