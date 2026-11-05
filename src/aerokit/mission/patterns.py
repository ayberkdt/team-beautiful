"""IAMSAR search patterns generated in a local frame and mapped to latitude/longitude.

Patterns (names after the IAMSAR Manual Vol. II):

* **PS — parallel track**: tracks parallel to the long side ("length", pattern +y axis) of a
  ``width × length`` rectangle, ``n = ceil(width / S)`` tracks, the first one ``S/2`` inside the
  boundary, ``S`` apart. Tracks run the full length plus an optional ``end_extension`` at both
  ends (the sensor images the whole area; turns happen outside it).
  Total length ``n·(length + 2·end_extension) + (n − 1)·S``.
* **CS — creeping line**: the same ladder turned 90°: tracks parallel to the width, advancing along
  the length, ``n = ceil(length / S)``.
* **SS — expanding square**: from the datum, legs of ``S, S, 2S, 2S, 3S, …`` with 90° right turns.
* **VS — sector search**: three equilateral triangles of side ``r`` through the datum (120° right
  turns), nine legs, total length ``9 r``.
* **PS/CS over a polygon** (:func:`polygon_track`): the same ladder over any simple polygon. Track
  ``i`` images the strip ``|x − x_i| ≤ S/2``; it runs from the lowest to the highest ``y`` of the
  polygon *inside that strip* (strip clipping, Sutherland–Hodgman), so a slanted edge is imaged to
  its end and no track runs beyond the polygon. A non-convex polygon is flown straight across where a
  strip leaves and re-enters it (conservative: the notch is flown over).

Track spacing comes from the sensor footprint of a nadir imager: ``swath = 2 h tan(FOV/2)`` and
``S = swath·(1 − overlap)``. Lengths and angles may be given as strings with units through
:mod:`aerokit.units` (``"1500 m"``, ``"60 deg"``, ``"10 %"``); bare numbers are SI (metres,
**radians**). A field of view of π rad or more is rejected, so ``fov=60`` fails loudly instead of
being read as 60 rad.

Pattern frame: ``x`` to the right of the along-track axis, ``y`` along it. ``orientation`` is the
bearing of ``+y`` (clockwise from north); ``center`` shifts the pattern in the local ENU frame.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from numpy.typing import NDArray

from aerokit.mission.geodesy import LocalFrame
from aerokit.references import cite
from aerokit.units import parse

__all__ = ["SearchPattern", "sensor_swath", "track_spacing", "parallel_track", "creeping_line",
           "expanding_square", "expanding_square_legs", "sector_search", "route_length", "route_prefix",
           "point_along", "polygon_track", "polygon_centroid", "to_pattern_frame"]

FloatArray = NDArray[np.float64]
Quantity = float | int | str

_EPS = 1e-9


def _length(v: Quantity, name: str, positive: bool = True) -> float:
    x = parse(v, "length")
    if positive and not x > 0:
        raise ValueError(f"{name} must be > 0, got {v!r}")
    return x


def _angle(v: Quantity) -> float:
    return parse(v, "angle")


@dataclass(frozen=True)
class SearchPattern:
    """A search route in a local frame.

    Attributes
    ----------
    kind : str
        ``"PS"``, ``"CS"``, ``"SS"`` or ``"VS"``.
    xy : ndarray, shape (N, 2)
        Waypoints in the pattern frame [m].
    spacing : float
        Track spacing (VS: radius) [m].
    orientation : float
        Bearing of the pattern +y axis [rad, clockwise from north].
    center : tuple of float
        Pattern-frame origin in the local ENU frame (east, north) [m].
    area_xy : ndarray or None
        Search-area polygon in the pattern frame (PS/CS rectangle, SS square, VS disc), if defined.
    frame : LocalFrame or None
        Geodetic anchor of the local ENU frame (needed for :meth:`geodetic`).
    """

    kind: str
    xy: FloatArray
    spacing: float
    orientation: float = 0.0
    center: tuple[float, float] = (0.0, 0.0)
    area_xy: FloatArray | None = None
    frame: LocalFrame | None = None

    def _to_en(self, xy: FloatArray) -> FloatArray:
        c, s = math.cos(self.orientation), math.sin(self.orientation)
        x, y = xy[:, 0], xy[:, 1]
        return np.column_stack([self.center[0] + x * c + y * s, self.center[1] - x * s + y * c])

    def with_area(self, area_en: npt.ArrayLike) -> SearchPattern:
        """Same route with the search-area polygon replaced by ``area_en`` (local ENU) [m]."""
        return SearchPattern(self.kind, self.xy, self.spacing, self.orientation, self.center,
                             to_pattern_frame(area_en, self.orientation, self.center), self.frame)

    @property
    def en(self) -> FloatArray:
        """Waypoints in the local ENU frame (east, north) [m]."""
        return self._to_en(self.xy)

    @property
    def area_en(self) -> FloatArray | None:
        """Search-area polygon in the local ENU frame [m], if defined."""
        return None if self.area_xy is None else self._to_en(self.area_xy)

    @property
    def length(self) -> float:
        """Total route length [m]."""
        return route_length(self.xy)

    @property
    def n_legs(self) -> int:
        """Number of straight legs."""
        return int(len(self.xy) - 1)

    def geodetic(self, frame: LocalFrame | None = None) -> tuple[FloatArray, FloatArray]:
        """Waypoints as (lat, lon) [deg]; ``frame`` overrides :attr:`frame`."""
        fr = frame or self.frame
        if fr is None:
            raise ValueError("pattern has no LocalFrame; pass frame=LocalFrame(lat0, lon0)")
        en = self.en
        return fr.surface(en[:, 0], en[:, 1])

    def area_geodetic(self, frame: LocalFrame | None = None) -> tuple[FloatArray, FloatArray]:
        """Search-area polygon as (lat, lon) [deg]."""
        fr = frame or self.frame
        a = self.area_en
        if fr is None or a is None:
            raise ValueError("pattern needs both a LocalFrame and an area polygon")
        return fr.surface(a[:, 0], a[:, 1])

    def truncated(self, distance: float) -> SearchPattern:
        """The first ``distance`` metres of the route (same area, spacing and frame)."""
        return SearchPattern(self.kind, route_prefix(self.xy, distance), self.spacing, self.orientation,
                             self.center, self.area_xy, self.frame)


def route_length(xy: FloatArray) -> float:
    """Length of a polyline [m]."""
    p = np.asarray(xy, float)
    return float(np.sum(np.hypot(*np.diff(p, axis=0).T))) if len(p) > 1 else 0.0


def point_along(xy: FloatArray, distance: float) -> tuple[float, float]:
    """Point at arc length ``distance`` along a polyline (clamped to its ends)."""
    p = route_prefix(xy, distance)
    return float(p[-1, 0]), float(p[-1, 1])


def route_prefix(xy: FloatArray, distance: float) -> FloatArray:
    """The polyline truncated after arc length ``distance`` (whole route if longer)."""
    p = np.asarray(xy, float)
    if distance <= 0.0:
        return p[:1].copy()
    seg = np.hypot(*np.diff(p, axis=0).T)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    if distance >= cum[-1]:
        return p.copy()
    i = int(np.searchsorted(cum, distance, side="right") - 1)
    frac = (distance - cum[i]) / seg[i] if seg[i] > 0 else 0.0
    end = p[i] + frac * (p[i + 1] - p[i])
    return np.vstack([p[: i + 1], end[None, :]])


def sensor_swath(altitude: Quantity, fov: Quantity) -> float:
    """Ground swath of a nadir imager over flat ground, ``2 h tan(FOV/2)`` [m].

    Parameters
    ----------
    altitude : float or str
        Height above ground (``"1500 m"``, ``"5000 ft"``; bare number in m).
    fov : float or str
        Full cross-track field of view (``"60 deg"``; bare number in rad, < π).
    """
    h = _length(altitude, "altitude")
    a = _angle(fov)
    if not 0.0 < a < math.pi:
        raise ValueError(f"FOV must be in (0, 180) deg, got {fov!r} (bare numbers are radians: write '60 deg')")
    return 2.0 * h * math.tan(a / 2.0)


def track_spacing(altitude: Quantity, fov: Quantity, overlap: Quantity = 0.0) -> float:
    """Track spacing ``swath·(1 − overlap)`` [m]; ``overlap`` in (−1, 1) (``"10 %"`` accepted)."""
    ov = parse(overlap, "dimensionless")
    if not -1.0 < ov < 1.0:
        raise ValueError(f"overlap must be in (-1, 1), got {overlap!r}")
    return sensor_swath(altitude, fov) * (1.0 - ov)


def _ladder(across: float, along: float, spacing: float, extension: float) -> tuple[FloatArray, int]:
    """Boustrophedon tracks parallel to y over [−across/2, across/2] × [−along/2, along/2]."""
    n = max(1, math.ceil(across / spacing - _EPS))
    pts: list[tuple[float, float]] = []
    y0, y1 = -along / 2.0 - extension, along / 2.0 + extension
    for i in range(n):
        x = -across / 2.0 + (i + 0.5) * spacing
        ys = (y0, y1) if i % 2 == 0 else (y1, y0)
        pts += [(x, ys[0]), (x, ys[1])]
    return np.array(pts, float), n


def _rectangle(width: float, length: float) -> FloatArray:
    w, l = width / 2.0, length / 2.0
    return np.array([[-w, -l], [w, -l], [w, l], [-w, l]], float)


def to_pattern_frame(points_en: npt.ArrayLike, orientation: float, center: tuple[float, float]) -> FloatArray:
    """Local ENU points [m] → pattern frame (x right of the tracks, y along ``orientation``) [m]."""
    p = np.asarray(points_en, float)
    c, s = math.cos(orientation), math.sin(orientation)
    de, dn = p[:, 0] - center[0], p[:, 1] - center[1]
    return np.column_stack([c * de - s * dn, s * de + c * dn])


def _check_polygon(polygon: npt.ArrayLike) -> FloatArray:
    p = np.asarray(polygon, float)
    if p.ndim != 2 or p.shape[1] != 2 or len(p) < 3 or not np.isfinite(p).all():
        raise ValueError("polygon must be an (N >= 3, 2) array of finite coordinates")
    if np.allclose(p[0], p[-1]):
        p = p[:-1]
    x, y = p[:, 0], p[:, 1]
    twice_area = float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
    if len(p) < 3 or abs(twice_area) <= 1e-9 * (float(np.ptp(x)) * float(np.ptp(y)) + 1.0):
        raise ValueError("polygon has zero area")
    return p


def polygon_centroid(polygon: npt.ArrayLike) -> tuple[float, float]:
    """Area centroid of a simple polygon [m] (shoelace formula)."""
    p = _check_polygon(polygon)
    x, y = p[:, 0], p[:, 1]
    xn, yn = np.roll(x, -1), np.roll(y, -1)
    cross = x * yn - xn * y
    a = 0.5 * float(cross.sum())
    return float(((x + xn) * cross).sum() / (6.0 * a)), float(((y + yn) * cross).sum() / (6.0 * a))


def _clip_half(pts: list[tuple[float, float]], x: float, keep_greater: bool) -> list[tuple[float, float]]:
    """Sutherland–Hodgman step: keep the part of the polygon with x ≥ (or ≤) the line."""
    out: list[tuple[float, float]] = []
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        kp = p[0] >= x if keep_greater else p[0] <= x
        kq = q[0] >= x if keep_greater else q[0] <= x
        if kp:
            out.append(p)
        if kp != kq:
            out.append((x, p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])))
    return out


def _strip_y_range(poly: FloatArray, x0: float, x1: float) -> tuple[float, float] | None:
    """(min y, max y) of the polygon inside the strip x0 ≤ x ≤ x1, or None if they do not overlap."""
    pts = _clip_half([(float(a), float(b)) for a, b in poly], x0, True)
    if pts:
        pts = _clip_half(pts, x1, False)
    if not pts:
        return None
    ys = [p[1] for p in pts]
    return min(ys), max(ys)


@cite("iamsar_1998", note="parallel track (PS) and creeping line (CS) laid over an arbitrary search area")
def polygon_track(polygon_en: npt.ArrayLike, spacing: Quantity, *, orientation: Quantity = 0.0, kind: str = "PS",
                  end_extension: Quantity = 0.0, frame: LocalFrame | None = None) -> SearchPattern:
    """Parallel-track ladder over a simple polygon (see module docstring).

    Parameters
    ----------
    polygon_en : array_like, shape (N, 2)
        Search area in the local ENU frame (east, north) [m]; the pattern is centred on its centroid.
    spacing : float or str
        Track spacing S [m].
    orientation : float or str
        Bearing of the tracks (PS) or of the creep direction (CS, tracks perpendicular to it).
    kind : "PS" or "CS"
    end_extension : float or str
        Distance flown beyond the polygon at both ends of each track [m].
    frame : LocalFrame, optional

    Raises
    ------
    ValueError
        Invalid polygon, spacing or kind.
    """
    if kind not in ("PS", "CS"):
        raise ValueError("kind must be 'PS' or 'CS'")
    S = _length(spacing, "spacing")
    e = _length(end_extension, "end_extension", positive=False)
    poly = _check_polygon(polygon_en)
    theta = _angle(orientation) + (math.pi / 2.0 if kind == "CS" else 0.0)
    center = polygon_centroid(poly)
    pxy = to_pattern_frame(poly, theta, center)
    x_min, x_max = float(pxy[:, 0].min()), float(pxy[:, 0].max())
    n = max(1, math.ceil((x_max - x_min) / S - _EPS))
    pts: list[tuple[float, float]] = []
    for i in range(n):
        x = x_min + (i + 0.5) * S
        yr = _strip_y_range(pxy, x - S / 2.0, x + S / 2.0)
        if yr is None:
            continue
        y0, y1 = yr[0] - e, yr[1] + e
        if y1 < y0:
            y0 = y1 = 0.5 * (yr[0] + yr[1])
        ys = (y0, y1) if (len(pts) // 2) % 2 == 0 else (y1, y0)
        pts += [(x, ys[0]), (x, ys[1])]
    return SearchPattern(kind, np.array(pts, float), S, theta, center, pxy, frame)


@cite("iamsar_1998", note="parallel track search (PS)")
def parallel_track(width: Quantity, length: Quantity, spacing: Quantity, *, orientation: Quantity = 0.0,
                   center: tuple[float, float] = (0.0, 0.0), end_extension: Quantity = 0.0,
                   frame: LocalFrame | None = None) -> SearchPattern:
    """Parallel-track (PS) pattern over a ``width × length`` rectangle.

    Parameters
    ----------
    width : float or str
        Extent across the tracks [m]; the number of tracks is ``ceil(width / spacing)``.
    length : float or str
        Extent along the tracks [m].
    spacing : float or str
        Track spacing S [m].
    orientation : float or str
        Bearing of the track direction (bare number in rad).
    center : (east, north)
        Rectangle centre in the local frame [m].
    end_extension : float or str
        Distance flown beyond each end of the rectangle before turning [m] (may be negative).
    frame : LocalFrame, optional
        Geodetic anchor for :meth:`SearchPattern.geodetic`.
    """
    W, L, S = _length(width, "width"), _length(length, "length"), _length(spacing, "spacing")
    e = _length(end_extension, "end_extension", positive=False)
    if L + 2.0 * e <= 0.0:
        raise ValueError("end_extension too negative: tracks would have zero length")
    xy, _ = _ladder(W, L, S, e)
    return SearchPattern("PS", xy, S, _angle(orientation), center, _rectangle(W, L), frame)


@cite("iamsar_1998", note="creeping line search (CS)")
def creeping_line(width: Quantity, length: Quantity, spacing: Quantity, *, orientation: Quantity = 0.0,
                  center: tuple[float, float] = (0.0, 0.0), end_extension: Quantity = 0.0,
                  frame: LocalFrame | None = None) -> SearchPattern:
    """Creeping-line (CS) pattern: tracks parallel to the width, advancing along the length.

    ``orientation`` is the bearing of the creep (length) direction; ``ceil(length / spacing)`` tracks.
    """
    W, L, S = _length(width, "width"), _length(length, "length"), _length(spacing, "spacing")
    e = _length(end_extension, "end_extension", positive=False)
    if W + 2.0 * e <= 0.0:
        raise ValueError("end_extension too negative: tracks would have zero length")
    ladder, _ = _ladder(L, W, S, e)              # tracks along x' of a swapped ladder
    xy = np.column_stack([ladder[:, 1], ladder[:, 0]])
    return SearchPattern("CS", xy, S, _angle(orientation), center, _rectangle(W, L), frame)


def _square_route(spacing: float, n_legs: int) -> FloatArray:
    pts = [(0.0, 0.0)]
    dirs = ((0.0, 1.0), (1.0, 0.0), (0.0, -1.0), (-1.0, 0.0))     # right turns from +y
    x = y = 0.0
    for k in range(n_legs):
        mult = k // 2 + 1
        dx, dy = dirs[k % 4]
        x, y = x + dx * mult * spacing, y + dy * mult * spacing
        pts.append((x, y))
    return np.array(pts, float)


def expanding_square_legs(extent: Quantity, spacing: Quantity) -> int:
    """Smallest number of SS legs whose outermost tracks lie within S/2 of a centred square's sides."""
    E, S = _length(extent, "extent"), _length(spacing, "spacing")
    need = max(E / 2.0 - S / 2.0, 0.0)
    n = 1
    while True:
        r = _square_route(S, n)
        if r[:, 0].min() <= -need + _EPS and r[:, 0].max() >= need - _EPS and \
                r[:, 1].min() <= -need + _EPS and r[:, 1].max() >= need - _EPS:
            return n
        n += 1


@cite("iamsar_1998", note="expanding square search (SS)")
def expanding_square(spacing: Quantity, *, n_legs: int | None = None, extent: Quantity | None = None,
                     orientation: Quantity = 0.0, center: tuple[float, float] = (0.0, 0.0),
                     frame: LocalFrame | None = None) -> SearchPattern:
    """Expanding-square (SS) pattern from the datum (``center``).

    Give either ``n_legs`` or ``extent`` (side of the centred square to cover; the area polygon is
    then that square). Leg ``k`` (0-based) has length ``(k//2 + 1)·S``; total for ``2m`` legs
    ``S·m(m+1)``.
    """
    S = _length(spacing, "spacing")
    if (n_legs is None) == (extent is None):
        raise ValueError("give exactly one of n_legs or extent")
    area = None
    if extent is not None:
        E = _length(extent, "extent")
        n_legs = expanding_square_legs(E, S)
        area = _rectangle(E, E)
    if n_legs is None or n_legs < 1:
        raise ValueError("n_legs must be >= 1")
    return SearchPattern("SS", _square_route(S, n_legs), S, _angle(orientation), center, area, frame)


@cite("iamsar_1998", note="sector search (VS): three triangles, 120 deg turns, legs of one radius")
def sector_search(radius: Quantity, *, orientation: Quantity = 0.0, center: tuple[float, float] = (0.0, 0.0),
                  frame: LocalFrame | None = None) -> SearchPattern:
    """Sector (VS) pattern: 9 legs of length ``radius`` through the datum, total ``9·radius``.

    The first leg leaves the datum along ``orientation``; the area polygon is the disc of radius
    ``radius`` (72-gon).
    """
    r = _length(radius, "radius")
    pts = [(0.0, 0.0)]
    x = y = 0.0
    heading = 0.0
    for tri in range(3):
        heading = math.radians(240.0 * tri)
        for _ in range(3):
            x, y = x + r * math.sin(heading), y + r * math.cos(heading)
            pts.append((x, y))
            heading += math.radians(120.0)
    xy = np.array(pts, float)
    xy[np.abs(xy) < 1e-9 * r] = 0.0
    t = np.linspace(0.0, 2.0 * math.pi, 72, endpoint=False)
    disc = np.column_stack([r * np.sin(t), r * np.cos(t)])
    return SearchPattern("VS", xy, r, _angle(orientation), center, disc, frame)
