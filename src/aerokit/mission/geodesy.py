"""WGS-84 geodesy for mission planning: geodesics, local frames and polygon areas.

* :func:`inverse` / :func:`direct` — geodesic problems on the WGS-84 ellipsoid by Vincenty's
  iterations (Vincenty 1975), implemented here. The inverse iteration is checked for convergence;
  it does not converge for nearly antipodal points. Then, if the optional ``geographiclib``
  package (Karney 2013) is installed, that solver is used and the result says so
  (``method == "karney"``); otherwise :class:`GeodesicConvergenceError` is raised. Lines whose
  longitude difference is exactly 0° or 180° are meridians and are solved in closed form (meridian
  arc by 32-point Gauss-Legendre quadrature), which covers the exactly antipodal case.
* :func:`great_circle_distance` — spherical haversine distance (quick estimates only).
* :class:`LocalFrame` — exact geodetic ↔ ECEF ↔ local east-north-up conversion. Search patterns
  are drawn in the tangent plane and mapped to the ellipsoid along the normal; a tangent-plane
  distance ``d`` from the origin then corresponds to a surface distance shorter by a relative
  ``≈ d²/(3R²)`` (2·10⁻⁵ at 50 km, about 1 m), which is the stated error of the local frame.
* :func:`polygon_area` — area on the ellipsoid via the authalic sphere and a Lambert azimuthal
  equal-area projection (Snyder 1987), both area-preserving, so the only error is that polygon
  edges are straight in the projection instead of geodesics; densify long edges with
  :func:`geodesic_path` first.

Angles in and out are degrees; lengths metres.
"""
from __future__ import annotations

import importlib
import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.references import cite

__all__ = ["WGS84_A", "WGS84_F", "WGS84_B", "WGS84_E2", "MEAN_RADIUS", "GeodesicConvergenceError", "Geodesic",
           "inverse", "direct", "meridian_arc", "great_circle_distance", "geodesic_path", "LocalFrame",
           "polygon_area", "authalic_radius", "geodetic_to_ecef", "ecef_to_geodetic"]

FloatArray = NDArray[np.float64]

WGS84_A = 6378137.0                         # semi-major axis [m]
WGS84_F = 1.0 / 298.257223563               # flattening
WGS84_B = WGS84_A * (1.0 - WGS84_F)         # semi-minor axis [m]
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)        # first eccentricity squared
MEAN_RADIUS = (2.0 * WGS84_A + WGS84_B) / 3.0   # mean radius R1 [m]

_GL_X, _GL_W = np.polynomial.legendre.leggauss(32)


class GeodesicConvergenceError(ArithmeticError):
    """Vincenty's inverse iteration did not converge (nearly antipodal points, no geographiclib)."""


@dataclass(frozen=True)
class Geodesic:
    """Solution of the inverse problem.

    Attributes
    ----------
    distance : float
        Geodesic length [m].
    azimuth1, azimuth2 : float
        Forward azimuth at the first point and at the second point [deg, clockwise from north].
    method : str
        ``"vincenty"``, ``"meridian"``, ``"coincident"`` or ``"karney"``.
    iterations : int
        Vincenty iterations used (0 for closed-form cases).
    """

    distance: float
    azimuth1: float
    azimuth2: float
    method: str
    iterations: int = 0


def _check_lat(lat: float, name: str) -> None:
    if not (math.isfinite(lat) and -90.0 <= lat <= 90.0):
        raise ValueError(f"{name} must be a finite latitude in [-90, 90] deg, got {lat!r}")


def _wrap180(x: float) -> float:
    y = math.fmod(x + 180.0, 360.0)
    if y < 0:
        y += 360.0
    return y - 180.0


def meridian_arc(lat: float) -> float:
    """Meridian distance from the equator to latitude ``lat`` [m] (signed), WGS-84.

    ``M(φ) = a(1−e²) ∫₀^φ (1 − e² sin²φ')^(−3/2) dφ'`` evaluated by 32-point Gauss-Legendre
    quadrature (the integrand is analytic and nearly constant, so the result is exact to rounding).
    """
    _check_lat(lat, "lat")
    phi = math.radians(lat)
    x = 0.5 * phi * (_GL_X + 1.0)
    integrand = (1.0 - WGS84_E2 * np.sin(x) ** 2) ** -1.5
    return float(WGS84_A * (1.0 - WGS84_E2) * 0.5 * phi * np.dot(_GL_W, integrand))


def _meridian_inverse(lat1: float, lat2: float, lon_diff: float) -> Geodesic:
    """Line along a meridian (Δλ = 0) or over a pole (Δλ = 180°)."""
    m1, m2 = meridian_arc(lat1), meridian_arc(lat2)
    if abs(lon_diff) < 90.0:                                   # same meridian
        az = 0.0 if lat2 >= lat1 else 180.0
        return Geodesic(abs(m2 - m1), az, az, "meridian")
    q = meridian_arc(90.0)
    north = (q - m1) + (q - m2)
    south = (q + m1) + (q + m2)
    if north <= south:
        return Geodesic(north, 0.0, 180.0, "meridian")
    return Geodesic(south, 180.0, 0.0, "meridian")


def _karney_inverse(lat1: float, lon1: float, lat2: float, lon2: float) -> Geodesic | None:
    try:
        mod: Any = importlib.import_module("geographiclib.geodesic")
    except ImportError:
        return None
    g = mod.Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)
    return Geodesic(float(g["s12"]), float(g["azi1"]), float(g["azi2"]), "karney")


@cite("vincenty_1975", note="inverse solution with the λ iteration; A, B series in u²")
@cite("karney_2013", note="fallback solver (geographiclib) for nearly antipodal lines, if installed")
def inverse(lat1: float, lon1: float, lat2: float, lon2: float, *, tol: float = 1e-12,
            max_iter: int = 200) -> Geodesic:
    """Distance and azimuths between two points on the WGS-84 ellipsoid.

    Parameters
    ----------
    lat1, lon1, lat2, lon2 : float
        Geodetic coordinates [deg].
    tol : float
        Convergence tolerance of the auxiliary longitude λ [rad].
    max_iter : int
        Iteration limit.

    Returns
    -------
    Geodesic

    Raises
    ------
    GeodesicConvergenceError
        Nearly antipodal points (the λ iteration diverges or stalls) and ``geographiclib`` is not
        installed.
    ValueError
        Latitude outside [-90, 90] or non-finite input.
    """
    _check_lat(lat1, "lat1")
    _check_lat(lat2, "lat2")
    if not (math.isfinite(lon1) and math.isfinite(lon2)):
        raise ValueError("longitudes must be finite")
    dlon = _wrap180(lon2 - lon1)
    if lat1 == lat2 and dlon == 0.0:
        return Geodesic(0.0, 0.0, 0.0, "coincident")
    if abs(lat1) == 90.0 or abs(lat2) == 90.0:                 # a pole: the line is a meridian
        return _meridian_inverse(lat1, lat2, 0.0)
    if dlon == 0.0 or abs(dlon) == 180.0:
        return _meridian_inverse(lat1, lat2, dlon)

    a, b, f = WGS84_A, WGS84_B, WGS84_F
    L = math.radians(dlon)
    p1, p2 = math.radians(lat1), math.radians(lat2)
    U1 = math.atan2((1.0 - f) * math.sin(p1), math.cos(p1))
    U2 = math.atan2((1.0 - f) * math.sin(p2), math.cos(p2))
    sU1, cU1, sU2, cU2 = math.sin(U1), math.cos(U1), math.sin(U2), math.cos(U2)
    lam = L
    converged = False
    it = 0
    sin_s = cos_s = sigma = cos2a = cos2sm = 0.0
    for it in range(1, max_iter + 1):
        sl, cl = math.sin(lam), math.cos(lam)
        sin_s = math.hypot(cU2 * sl, cU1 * sU2 - sU1 * cU2 * cl)
        if sin_s == 0.0:                                        # pragma: no cover - coincident handled above
            return Geodesic(0.0, 0.0, 0.0, "coincident", it)
        cos_s = sU1 * sU2 + cU1 * cU2 * cl
        sigma = math.atan2(sin_s, cos_s)
        sin_a = cU1 * cU2 * sl / sin_s
        cos2a = 1.0 - sin_a * sin_a
        cos2sm = cos_s - 2.0 * sU1 * sU2 / cos2a if cos2a != 0.0 else 0.0
        C = f / 16.0 * cos2a * (4.0 + f * (4.0 - 3.0 * cos2a))
        lam_prev = lam
        lam = L + (1.0 - C) * f * sin_a * (sigma + C * sin_s * (cos2sm + C * cos_s * (-1.0 + 2.0 * cos2sm ** 2)))
        if abs(lam) > math.pi:                                 # antipodal region: iteration leaves [-π, π]
            break
        if abs(lam - lam_prev) < tol:
            converged = True
            break
    if not converged:
        k = _karney_inverse(lat1, lon1, lat2, lon2)
        if k is not None:
            return k
        raise GeodesicConvergenceError(
            f"Vincenty inverse did not converge after {it} iterations for ({lat1}, {lon1}) -> ({lat2}, {lon2}) "
            "(nearly antipodal points); install geographiclib (Karney 2013) for these lines")
    u2 = cos2a * (a * a - b * b) / (b * b)
    A = 1.0 + u2 / 16384.0 * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)))
    B = u2 / 1024.0 * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)))
    ds = B * sin_s * (cos2sm + B / 4.0 * (cos_s * (-1.0 + 2.0 * cos2sm ** 2)
                                         - B / 6.0 * cos2sm * (-3.0 + 4.0 * sin_s ** 2) * (-3.0 + 4.0 * cos2sm ** 2)))
    s = b * A * (sigma - ds)
    sl, cl = math.sin(lam), math.cos(lam)
    az1 = math.degrees(math.atan2(cU2 * sl, cU1 * sU2 - sU1 * cU2 * cl))
    az2 = math.degrees(math.atan2(cU1 * sl, -sU1 * cU2 + cU1 * sU2 * cl))
    return Geodesic(s, az1 % 360.0, az2 % 360.0, "vincenty", it)


@cite("vincenty_1975", note="direct solution with the σ iteration")
def direct(lat1: float, lon1: float, azimuth1: float, distance: float, *, tol: float = 1e-12,
           max_iter: int = 200) -> tuple[float, float, float]:
    """Point reached from ``(lat1, lon1)`` along a geodesic of given initial azimuth and length.

    Parameters
    ----------
    lat1, lon1 : float
        Start point [deg].
    azimuth1 : float
        Initial azimuth [deg, clockwise from north].
    distance : float
        Geodesic length [m] (≥ 0).

    Returns
    -------
    (lat2, lon2, azimuth2) : tuple of float
        End point [deg] (longitude wrapped to [-180, 180)) and forward azimuth there [deg].

    Raises
    ------
    ValueError
        Invalid input, or the σ iteration did not converge.
    """
    _check_lat(lat1, "lat1")
    if not (math.isfinite(lon1) and math.isfinite(azimuth1) and math.isfinite(distance) and distance >= 0.0):
        raise ValueError("lon1, azimuth1 must be finite and distance finite and >= 0")
    if distance == 0.0:
        return lat1, _wrap180(lon1), azimuth1 % 360.0
    a, b, f = WGS84_A, WGS84_B, WGS84_F
    p1, a1 = math.radians(lat1), math.radians(azimuth1)
    U1 = math.atan2((1.0 - f) * math.sin(p1), math.cos(p1))
    sU1, cU1 = math.sin(U1), math.cos(U1)
    sa1, ca1 = math.sin(a1), math.cos(a1)
    sigma1 = math.atan2(sU1, cU1 * ca1)
    sin_a = cU1 * sa1
    cos2a = 1.0 - sin_a * sin_a
    u2 = cos2a * (a * a - b * b) / (b * b)
    A = 1.0 + u2 / 16384.0 * (4096.0 + u2 * (-768.0 + u2 * (320.0 - 175.0 * u2)))
    B = u2 / 1024.0 * (256.0 + u2 * (-128.0 + u2 * (74.0 - 47.0 * u2)))
    sigma = distance / (b * A)
    for _ in range(max_iter):
        cos2sm = math.cos(2.0 * sigma1 + sigma)
        sin_s, cos_s = math.sin(sigma), math.cos(sigma)
        ds = B * sin_s * (cos2sm + B / 4.0 * (cos_s * (-1.0 + 2.0 * cos2sm ** 2)
                                             - B / 6.0 * cos2sm * (-3.0 + 4.0 * sin_s ** 2)
                                             * (-3.0 + 4.0 * cos2sm ** 2)))
        new = distance / (b * A) + ds
        if abs(new - sigma) < tol:
            sigma = new
            break
        sigma = new
    else:
        raise ValueError("Vincenty direct iteration did not converge")
    cos2sm = math.cos(2.0 * sigma1 + sigma)
    sin_s, cos_s = math.sin(sigma), math.cos(sigma)
    tmp = sU1 * sin_s - cU1 * cos_s * ca1
    lat2 = math.atan2(sU1 * cos_s + cU1 * sin_s * ca1, (1.0 - f) * math.hypot(sin_a, tmp))
    lam = math.atan2(sin_s * sa1, cU1 * cos_s - sU1 * sin_s * ca1)
    C = f / 16.0 * cos2a * (4.0 + f * (4.0 - 3.0 * cos2a))
    L = lam - (1.0 - C) * f * sin_a * (sigma + C * sin_s * (cos2sm + C * cos_s * (-1.0 + 2.0 * cos2sm ** 2)))
    az2 = math.degrees(math.atan2(sin_a, -tmp)) % 360.0
    return math.degrees(lat2), _wrap180(lon1 + math.degrees(L)), az2


def great_circle_distance(lat1: float, lon1: float, lat2: float, lon2: float,
                          radius: float = MEAN_RADIUS) -> float:
    """Spherical (haversine) distance [m]; differs from the WGS-84 geodesic by up to ≈ 0.5 %."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    h = math.sin(dp / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2.0) ** 2
    return 2.0 * radius * math.asin(min(1.0, math.sqrt(h)))


def geodesic_path(lat1: float, lon1: float, lat2: float, lon2: float, n: int) -> tuple[FloatArray, FloatArray]:
    """``n`` (≥ 2) equally spaced points along the geodesic, end points included [deg]."""
    if n < 2:
        raise ValueError("n must be >= 2")
    g = inverse(lat1, lon1, lat2, lon2)
    lats, lons = np.empty(n), np.empty(n)
    for i, frac in enumerate(np.linspace(0.0, 1.0, n)):
        la, lo, _ = direct(lat1, lon1, g.azimuth1, float(frac) * g.distance)
        lats[i], lons[i] = la, lo
    lats[-1], lons[-1] = lat2, _wrap180(lon2)
    return lats, lons


# ----------------------------------------------------------------------------- local frame
def _geodetic_to_ecef(lat: FloatArray, lon: FloatArray, h: FloatArray) -> tuple[FloatArray, FloatArray, FloatArray]:
    p, l = np.radians(lat), np.radians(lon)
    N = WGS84_A / np.sqrt(1.0 - WGS84_E2 * np.sin(p) ** 2)
    x = (N + h) * np.cos(p) * np.cos(l)
    y = (N + h) * np.cos(p) * np.sin(l)
    z = (N * (1.0 - WGS84_E2) + h) * np.sin(p)
    return x, y, z


def _ecef_to_geodetic(x: FloatArray, y: FloatArray, z: FloatArray) -> tuple[FloatArray, FloatArray, FloatArray]:
    lon = np.arctan2(y, x)
    p = np.hypot(x, y)
    lat = np.arctan2(z, p * (1.0 - WGS84_E2))
    h = np.zeros_like(lat)
    for _ in range(50):
        s = np.sin(lat)
        N = WGS84_A / np.sqrt(1.0 - WGS84_E2 * s * s)
        h = p * np.cos(lat) + (z + WGS84_E2 * N * s) * s - N
        new = np.arctan2(z, p * (1.0 - WGS84_E2 * N / (N + h)))
        done = bool(np.all(np.abs(new - lat) < 1e-14))
        lat = new
        if done:
            break
    return np.degrees(lat), np.degrees(lon), h


def geodetic_to_ecef(lat: ArrayLike, lon: ArrayLike, h: ArrayLike = 0.0) -> tuple[FloatArray, FloatArray, FloatArray]:
    """WGS-84 geodetic (lat, lon [deg], ellipsoidal height [m]) → Earth-centred Earth-fixed (x, y, z) [m]."""
    la, lo, hh = np.broadcast_arrays(np.asarray(lat, float), np.asarray(lon, float), np.asarray(h, float))
    return _geodetic_to_ecef(la, lo, hh)


def ecef_to_geodetic(x: ArrayLike, y: ArrayLike, z: ArrayLike) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Earth-centred Earth-fixed (x, y, z) [m] → WGS-84 (lat, lon [deg], ellipsoidal height [m]), iterative."""
    xx, yy, zz = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float))
    return _ecef_to_geodetic(xx, yy, zz)


@dataclass(frozen=True)
class LocalFrame:
    """Local east-north-up tangent frame at a geodetic origin (exact via ECEF).

    Attributes
    ----------
    lat0, lon0 : float
        Origin [deg].
    h0 : float
        Origin height above the ellipsoid [m].
    """

    lat0: float
    lon0: float
    h0: float = 0.0

    def __post_init__(self) -> None:
        _check_lat(self.lat0, "lat0")
        if abs(self.lat0) > 89.0:
            raise ValueError("local frames are not supported within 1 deg of a pole")
        if not (math.isfinite(self.lon0) and math.isfinite(self.h0)):
            raise ValueError("lon0 and h0 must be finite")

    def _rot(self) -> FloatArray:
        p, l = math.radians(self.lat0), math.radians(self.lon0)
        sp, cp, sl, cl = math.sin(p), math.cos(p), math.sin(l), math.cos(l)
        return np.array([[-sl, cl, 0.0], [-sp * cl, -sp * sl, cp], [cp * cl, cp * sl, sp]])

    def to_enu(self, lat: ArrayLike, lon: ArrayLike, h: ArrayLike = 0.0) -> tuple[FloatArray, FloatArray, FloatArray]:
        """Geodetic [deg, deg, m] → local (east, north, up) [m]."""
        la, lo, hh = np.broadcast_arrays(np.asarray(lat, float), np.asarray(lon, float), np.asarray(h, float))
        x, y, z = _geodetic_to_ecef(la, lo, hh)
        x0, y0, z0 = _geodetic_to_ecef(np.array(self.lat0), np.array(self.lon0), np.array(self.h0))
        d = np.stack([x - x0, y - y0, z - z0])
        enu = np.tensordot(self._rot(), d, axes=1)
        return enu[0], enu[1], enu[2]

    def enu_from_ecef(self, x: ArrayLike, y: ArrayLike, z: ArrayLike) -> tuple[FloatArray, FloatArray, FloatArray]:
        """Earth-fixed (x, y, z) [m] → local (east, north, up) [m] relative to the frame origin."""
        xx, yy, zz = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float))
        x0, y0, z0 = _geodetic_to_ecef(np.array(self.lat0), np.array(self.lon0), np.array(self.h0))
        enu = np.tensordot(self._rot(), np.stack([xx - x0, yy - y0, zz - z0]), axes=1)
        return enu[0], enu[1], enu[2]

    def to_geodetic(self, east: ArrayLike, north: ArrayLike,
                    up: ArrayLike = 0.0) -> tuple[FloatArray, FloatArray, FloatArray]:
        """Local (east, north, up) [m] → geodetic (lat, lon [deg], h [m])."""
        e, n, u = np.broadcast_arrays(np.asarray(east, float), np.asarray(north, float), np.asarray(up, float))
        d = np.tensordot(self._rot().T, np.stack([e, n, u]), axes=1)
        x0, y0, z0 = _geodetic_to_ecef(np.array(self.lat0), np.array(self.lon0), np.array(self.h0))
        lat, lon, h = _ecef_to_geodetic(d[0] + x0, d[1] + y0, d[2] + z0)
        return lat, (lon + 180.0) % 360.0 - 180.0, h

    def surface(self, east: ArrayLike, north: ArrayLike) -> tuple[FloatArray, FloatArray]:
        """Tangent-plane point mapped to the ellipsoid along the normal → (lat, lon) [deg]."""
        lat, lon, _ = self.to_geodetic(east, north, 0.0)
        return lat, lon


# ----------------------------------------------------------------------------- areas
def _q(phi: FloatArray) -> FloatArray:
    e = math.sqrt(WGS84_E2)
    s = np.sin(phi)
    out: FloatArray = (1.0 - WGS84_E2) * (s / (1.0 - WGS84_E2 * s * s)
                                          - np.log((1.0 - e * s) / (1.0 + e * s)) / (2.0 * e))
    return out


_QP = float(_q(np.array(math.pi / 2.0)))


def authalic_radius() -> float:
    """Radius of the sphere with the same surface area as the WGS-84 ellipsoid [m]."""
    return WGS84_A * math.sqrt(_QP / 2.0)


@cite("snyder_1987", note="authalic latitude β = asin(q/q_p), R_q = a√(q_p/2); Lambert azimuthal equal-area")
def polygon_area(lat: ArrayLike, lon: ArrayLike) -> float:
    """Area of a simple polygon on the WGS-84 ellipsoid [m²].

    Vertices are mapped to the authalic sphere and projected with the Lambert azimuthal equal-area
    projection centred on the polygon; the shoelace area of the projected polygon is returned.
    Both maps preserve area, so the result is exact for a polygon whose edges are straight in the
    projection; for geodesic edges longer than a few tens of km, densify them with
    :func:`geodesic_path`.

    Parameters
    ----------
    lat, lon : array_like
        Vertices [deg], open or closed ring, either orientation.

    Raises
    ------
    ValueError
        Fewer than three vertices, mismatched lengths or a polygon spanning a hemisphere or more.
    """
    la = np.asarray(lat, float).ravel()
    lo = np.asarray(lon, float).ravel()
    if la.shape != lo.shape or la.size < 3:
        raise ValueError("polygon needs >= 3 vertices with matching lat/lon arrays")
    if not (np.all(np.isfinite(la)) and np.all(np.isfinite(lo))) or np.any(np.abs(la) > 90.0):
        raise ValueError("invalid polygon coordinates")
    beta = np.arcsin(np.clip(_q(np.radians(la)) / _QP, -1.0, 1.0))
    lam = np.radians(lo)
    # projection centre: mean unit vector on the authalic sphere
    v = np.stack([np.cos(beta) * np.cos(lam), np.cos(beta) * np.sin(lam), np.sin(beta)])
    c = v.mean(axis=1)
    if np.linalg.norm(c) < 1e-6:
        raise ValueError("polygon too large for the equal-area projection")
    c = c / np.linalg.norm(c)
    b0, l0 = math.asin(float(c[2])), math.atan2(float(c[1]), float(c[0]))
    dl = lam - l0
    cosc = math.sin(b0) * np.sin(beta) + math.cos(b0) * np.cos(beta) * np.cos(dl)
    if np.any(cosc <= 0.0):
        raise ValueError("polygon spans a hemisphere or more")
    R = authalic_radius()
    k = np.sqrt(2.0 / (1.0 + cosc))
    x = R * k * np.cos(beta) * np.sin(dl)
    y = R * k * (math.cos(b0) * np.sin(beta) - math.sin(b0) * np.cos(beta) * np.cos(dl))
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))
