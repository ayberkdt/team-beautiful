"""Sensor coverage of a search area by the swath swept along a route.

Swath model: each straight leg sweeps a rectangle of width ``swath`` centred on the leg, with flat
ends (no sweep beyond the leg end points). At a turn the outer corner wedge is therefore left
uncovered and the inner corner counted once — a conservative model of a real banked turn, in
which the imager is usually not pointing at nadir anyway.

Two evaluations:

* :func:`coverage_raster` — any simple polygon; the polygon's bounding box is divided into square
  cells of side ``resolution`` and a cell counts as covered when its centre lies in a swept
  rectangle. Only cells cut by a boundary (polygon edge or swath edge) can be misclassified, so
  the error is bounded by (boundary length × resolution) / area and is usually much smaller since
  errors on opposite edges cancel; the tests compare it with the exact method. Optionally a *lateral-range*
  function ``p(d)`` (probability of detection at lateral distance ``d`` from the track) turns
  this into a mean probability of detection, combining legs as ``1 − Π(1 − p_i)``.
* :func:`coverage_rectangles_exact` — exact union area for axis-aligned legs over an axis-aligned
  rectangle (coordinate compression); used to verify the raster and by the optimiser.

:func:`random_search_pod` is the random-search formula ``1 − exp(−W·L/A)`` (Koopman 1980).
All coordinates are metres in a local plane (see :class:`aerokit.mission.geodesy.LocalFrame`).
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.mission.patterns import SearchPattern
from aerokit.references import cite

__all__ = ["CoverageResult", "coverage_raster", "coverage_rectangles_exact", "pattern_coverage",
           "points_in_polygon", "random_search_pod", "polygon_area_xy"]

FloatArray = NDArray[np.float64]
LateralRange = Callable[[FloatArray], FloatArray]


@dataclass(frozen=True)
class CoverageResult:
    """Coverage of a search area.

    Attributes
    ----------
    fraction : float
        Covered area / search area.
    covered_area, area : float
        [m²].
    method : str
        ``"raster"`` or ``"exact-rectangles"``.
    resolution : float
        Raster cell size [m] (0 for the exact method).
    pod : float or None
        Area-mean probability of detection (raster with a lateral-range function only).
    """

    fraction: float
    covered_area: float
    area: float
    method: str
    resolution: float = 0.0
    pod: float | None = None


def polygon_area_xy(polygon: ArrayLike) -> float:
    """Shoelace area of a planar polygon [m²]."""
    p = np.asarray(polygon, float)
    x, y = p[:, 0], p[:, 1]
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def points_in_polygon(px: FloatArray, py: FloatArray, polygon: ArrayLike) -> NDArray[np.bool_]:
    """Even-odd point-in-polygon test, vectorised over the points."""
    poly = np.asarray(polygon, float)
    inside = np.zeros(px.shape, dtype=bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if y1 == y2:
            continue
        crosses = (py >= min(y1, y2)) & (py < max(y1, y2))
        xc = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
        inside ^= crosses & (px < xc)
    return inside


def _check_route(route: ArrayLike, swath: float) -> FloatArray:
    r = np.asarray(route, float)
    if r.ndim != 2 or r.shape[1] != 2 or len(r) < 1:
        raise ValueError("route must be an (N, 2) array of waypoints")
    if not (math.isfinite(swath) and swath > 0):
        raise ValueError("swath must be > 0")
    return r


@cite("koopman_1980", note="cumulative detection 1 − Π(1 − p_i) over independent glimpses (legs)")
def coverage_raster(polygon: ArrayLike, route: ArrayLike, swath: float, resolution: float,
                    lateral_range: LateralRange | None = None) -> CoverageResult:
    """Covered fraction of ``polygon`` by the swath along ``route``, on a raster.

    Parameters
    ----------
    polygon : array_like, shape (M, 2)
        Search area [m].
    route : array_like, shape (N, 2)
        Waypoints [m].
    swath : float
        Swath width [m].
    resolution : float
        Raster cell size [m].
    lateral_range : callable, optional
        ``p(d)`` for lateral distances ``d`` ≥ 0 [m], values in [0, 1]; applied inside the swept
        rectangle of each leg. Without it, detection is definite inside the swath.
    """
    r = _check_route(route, swath)
    poly = np.asarray(polygon, float)
    if not (math.isfinite(resolution) and resolution > 0):
        raise ValueError("resolution must be > 0")
    x0, y0 = poly.min(axis=0)
    x1, y1 = poly.max(axis=0)
    nx, ny = max(1, math.ceil((x1 - x0) / resolution)), max(1, math.ceil((y1 - y0) / resolution))
    if nx * ny > 2e7:
        raise ValueError(f"raster of {nx}×{ny} cells is too large; increase the resolution")
    gx = x0 + (np.arange(nx) + 0.5) * (x1 - x0) / nx
    gy = y0 + (np.arange(ny) + 0.5) * (y1 - y0) / ny
    X, Y = np.meshgrid(gx, gy)
    mask = points_in_polygon(X.ravel(), Y.ravel(), poly)
    px, py = X.ravel()[mask], Y.ravel()[mask]
    cell = (x1 - x0) / nx * (y1 - y0) / ny
    area = polygon_area_xy(poly)
    covered = np.zeros(px.shape, dtype=bool)
    miss = np.ones(px.shape)
    half = swath / 2.0
    for a, b in zip(r[:-1], r[1:], strict=True):
        d = b - a
        L = float(np.hypot(*d))
        if L == 0.0:
            continue
        ux, uy = d / L
        rx, ry = px - a[0], py - a[1]
        t = rx * ux + ry * uy
        dist = np.abs(rx * uy - ry * ux)
        hit = (t >= 0.0) & (t <= L) & (dist <= half)
        covered |= hit
        if lateral_range is not None:
            p = np.clip(np.asarray(lateral_range(dist[hit]), float), 0.0, 1.0)
            miss[hit] *= 1.0 - p
    frac = float(covered.sum() * cell / area) if area > 0 else 0.0
    pod = float((1.0 - miss).sum() * cell / area) if lateral_range is not None and area > 0 else None
    return CoverageResult(min(frac, 1.0), min(frac, 1.0) * area, area, "raster", resolution, pod)


def coverage_rectangles_exact(rect: tuple[float, float, float, float], route: ArrayLike,
                              swath: float) -> CoverageResult:
    """Exact covered fraction of the rectangle ``(xmin, xmax, ymin, ymax)`` by axis-aligned legs.

    Raises
    ------
    ValueError
        A leg that is not parallel to x or y (relative tolerance 1e-9).
    """
    r = _check_route(route, swath)
    xmin, xmax, ymin, ymax = rect
    if not (xmax > xmin and ymax > ymin):
        raise ValueError("rectangle must have xmax > xmin and ymax > ymin")
    half = swath / 2.0
    boxes = []
    for a, b in zip(r[:-1], r[1:], strict=True):
        dx, dy = b - a
        L = math.hypot(dx, dy)
        if L == 0.0:
            continue
        if abs(dx) <= 1e-9 * L:
            boxes.append((a[0] - half, a[0] + half, min(a[1], b[1]), max(a[1], b[1])))
        elif abs(dy) <= 1e-9 * L:
            boxes.append((min(a[0], b[0]), max(a[0], b[0]), a[1] - half, a[1] + half))
        else:
            raise ValueError("exact coverage needs legs parallel to the rectangle sides")
    area = (xmax - xmin) * (ymax - ymin)
    if not boxes:
        return CoverageResult(0.0, 0.0, area, "exact-rectangles")
    B = np.clip(np.array(boxes), [xmin, xmin, ymin, ymin], [xmax, xmax, ymax, ymax])
    xs = np.unique(np.concatenate([B[:, 0], B[:, 1], [xmin, xmax]]))
    ys = np.unique(np.concatenate([B[:, 2], B[:, 3], [ymin, ymax]]))
    cx, cy = 0.5 * (xs[:-1] + xs[1:]), 0.5 * (ys[:-1] + ys[1:])
    inx = (cx[None, :] > B[:, 0:1]) & (cx[None, :] < B[:, 1:2])        # (boxes, nx)
    iny = (cy[None, :] > B[:, 2:3]) & (cy[None, :] < B[:, 3:4])        # (boxes, ny)
    cov = np.einsum("bi,bj->ij", inx.astype(np.int32), iny.astype(np.int32)) > 0
    covered = float(np.sum(cov * np.outer(np.diff(xs), np.diff(ys))))
    return CoverageResult(covered / area, covered, area, "exact-rectangles")


def _is_axis_rectangle(poly: FloatArray) -> bool:
    """True for a 4-vertex polygon whose vertices are the corners of its bounding box."""
    if len(poly) != 4:
        return False
    xs, ys = poly[:, 0], poly[:, 1]
    corners = {(float(a), float(b)) for a in (xs.min(), xs.max()) for b in (ys.min(), ys.max())}
    return {(float(a), float(b)) for a, b in poly} == corners


def pattern_coverage(pattern: SearchPattern, swath: float, *, distance: float | None = None,
                     polygon: ArrayLike | None = None, resolution: float | None = None,
                     lateral_range: LateralRange | None = None) -> CoverageResult:
    """Coverage of a pattern's area (or ``polygon``, pattern frame) by its route.

    ``distance`` truncates the route (e.g. to what the fuel allows). The exact rectangle method is
    used when the area is the pattern's own rectangle (PS/CS), no resolution or lateral-range
    function is requested; otherwise the raster (default resolution: swath/20).
    """
    route = pattern.xy if distance is None else pattern.truncated(distance).xy
    poly = pattern.area_xy if polygon is None else np.asarray(polygon, float)
    if poly is None:
        raise ValueError("pattern has no area polygon; pass polygon=")
    if (polygon is None and resolution is None and lateral_range is None and pattern.kind in ("PS", "CS")
            and _is_axis_rectangle(poly)):
        xs, ys = poly[:, 0], poly[:, 1]
        return coverage_rectangles_exact((float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())),
                                         route, swath)
    return coverage_raster(poly, route, swath, resolution or swath / 20.0, lateral_range)


@cite("koopman_1980", note="random-search formula POD = 1 − exp(−W L / A)")
def random_search_pod(sweep_width: float, track_length: float, area: float) -> float:
    """Probability of detection of a uniformly distributed target under random search."""
    if not (sweep_width >= 0 and track_length >= 0 and area > 0):
        raise ValueError("sweep_width, track_length must be >= 0 and area > 0")
    return 1.0 - math.exp(-sweep_width * track_length / area)
