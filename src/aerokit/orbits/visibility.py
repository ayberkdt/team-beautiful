"""Satellite visibility from ground sites: look angles, satellites in view, access windows, common view.

Geometry: the site is a WGS-84 point (:func:`aerokit.mission.geodesy.geodetic_to_ecef`), the satellite's Earth-fixed
position comes from :meth:`MeanElements.position_ecef`, and the local east-north-up components give

    elevation = atan2(up, √(east² + north²)),   azimuth = atan2(east, north)   (clockwise from north).

A satellite is *visible* when its elevation is at least the site's mask (geometric line of sight above a cone; no
terrain, no refraction). *Common view* of two sites is the two-hop relay condition of a transparent (bent-pipe)
repeater such as the Cospas-Sarsat MEOSAR and GEOSAR payloads: one satellite above both masks at the same instant.
Access-window edges are refined by bisection to ``edge_tolerance_s``.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
from numpy.typing import NDArray

from aerokit.comms.constants import OMEGA_EARTH
from aerokit.comms.geometry import LinkGeometry, VisibilityStatus, geometry_from_states
from aerokit.mission.geodesy import LocalFrame, geodetic_to_ecef
from aerokit.orbits.constellations import MeanElements, gmst_rad

__all__ = ["GroundSite", "LookAngles", "look_angles", "count_in_view", "AccessWindow", "access_windows",
           "common_view", "site_state_eci", "link_geometry", "time_grid"]

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class GroundSite:
    """A point on (or above) the WGS-84 ellipsoid with an elevation mask."""

    name: str
    lat_deg: float
    lon_deg: float
    h_m: float = 0.0
    mask_deg: float = 5.0

    def __post_init__(self) -> None:
        if not (-90.0 <= self.lat_deg <= 90.0 and math.isfinite(self.lon_deg) and math.isfinite(self.h_m)):
            raise ValueError(f"{self.name}: invalid position")
        if not -90.0 <= self.mask_deg < 90.0:
            raise ValueError(f"{self.name}: elevation mask must be in [-90, 90) deg")

    @property
    def frame(self) -> LocalFrame:
        return LocalFrame(self.lat_deg, self.lon_deg, self.h_m)

    @property
    def ecef(self) -> FloatArray:
        x, y, z = geodetic_to_ecef(self.lat_deg, self.lon_deg, self.h_m)
        return np.array([float(x), float(y), float(z)])


@dataclass(frozen=True)
class LookAngles:
    """Azimuth, elevation [deg] and range [m] at each time."""

    azimuth_deg: FloatArray
    elevation_deg: FloatArray
    range_m: FloatArray


def time_grid(start: datetime, end: datetime, step_s: float) -> list[datetime]:
    """``start, start + step, …`` up to and including ``end`` (if it falls on the grid)."""
    if not (step_s > 0 and end >= start):
        raise ValueError("need step_s > 0 and end >= start")
    n = int(math.floor((end - start).total_seconds() / step_s + 1e-9))
    return [start + timedelta(seconds=k * step_s) for k in range(n + 1)]


def look_angles(sat: MeanElements, site: GroundSite, times: datetime | Sequence[datetime]) -> LookAngles:
    """Look angles of ``sat`` from ``site`` at each time."""
    r = sat.position_ecef(times)
    e, n, u = site.frame.enu_from_ecef(r[:, 0], r[:, 1], r[:, 2])
    horiz = np.hypot(e, n)
    return LookAngles(np.degrees(np.arctan2(e, n)) % 360.0, np.degrees(np.arctan2(u, horiz)),
                      np.sqrt(horiz ** 2 + u ** 2))


def count_in_view(sats: Sequence[MeanElements], site: GroundSite, times: Sequence[datetime]) -> NDArray[np.int64]:
    """Number of satellites at or above the site's mask at each time."""
    count = np.zeros(len(times), dtype=np.int64)
    for s in sats:
        count += look_angles(s, site, times).elevation_deg >= site.mask_deg
    return count


@dataclass(frozen=True)
class AccessWindow:
    """One interval with the satellite above the mask."""

    satellite: str
    start: datetime
    end: datetime
    max_elevation_deg: float

    @property
    def duration_s(self) -> float:
        return (self.end - self.start).total_seconds()


def _elev(sat: MeanElements, site: GroundSite, t: datetime) -> float:
    return float(look_angles(sat, site, t).elevation_deg[0])


def _edge(sat: MeanElements, site: GroundSite, t_lo: datetime, t_hi: datetime, rising: bool, tol: float) -> datetime:
    """Bisection on elevation − mask between a below-mask and an above-mask sample."""
    lo, hi = (t_lo, t_hi) if rising else (t_hi, t_lo)        # lo: below the mask, hi: above
    while abs((hi - lo).total_seconds()) > tol:
        mid = lo + (hi - lo) / 2
        if _elev(sat, site, mid) >= site.mask_deg:
            hi = mid
        else:
            lo = mid
    return hi


def access_windows(sat: MeanElements, site: GroundSite, start: datetime, end: datetime, step_s: float = 60.0,
                   edge_tolerance_s: float = 0.5) -> list[AccessWindow]:
    """Intervals in [start, end] with ``sat`` above the site's mask (sampled at ``step_s``, edges bisected).

    A pass shorter than ``step_s`` between two samples can be missed; choose ``step_s`` well below the shortest pass.
    """
    ts = time_grid(start, end, step_s)
    el = look_angles(sat, site, ts).elevation_deg
    up = el >= site.mask_deg
    out: list[AccessWindow] = []
    k = 0
    while k < len(ts):
        if not up[k]:
            k += 1
            continue
        j = k
        while j + 1 < len(ts) and up[j + 1]:
            j += 1
        t0 = ts[0] if k == 0 else _edge(sat, site, ts[k - 1], ts[k], True, edge_tolerance_s)
        t1 = ts[-1] if j == len(ts) - 1 else _edge(sat, site, ts[j], ts[j + 1], False, edge_tolerance_s)
        out.append(AccessWindow(sat.name, t0, t1, float(el[k:j + 1].max())))
        k = j + 1
    return out


def common_view(sats: Sequence[MeanElements], site_a: GroundSite, site_b: GroundSite,
                times: Sequence[datetime]) -> tuple[NDArray[np.int64], float]:
    """Satellites above both sites' masks at each time, and the fraction of times with at least one (relay up)."""
    count = np.zeros(len(times), dtype=np.int64)
    for s in sats:
        a = look_angles(s, site_a, times).elevation_deg >= site_a.mask_deg
        b = look_angles(s, site_b, times).elevation_deg >= site_b.mask_deg
        count += a & b
    return count, float(np.mean(count > 0)) if len(times) else 0.0


def site_state_eci(site: GroundSite, t: datetime) -> FloatArray:
    """Inertial ``[r, v]`` of a ground site (Earth rotation ω_E about z) in the satellites' frame."""
    th = gmst_rad(t)
    c, s = math.cos(th), math.sin(th)
    x, y, z = site.ecef
    r = np.array([c * x - s * y, s * x + c * y, z])
    v = np.array([-OMEGA_EARTH * r[1], OMEGA_EARTH * r[0], 0.0])
    return np.concatenate([r, v])


def link_geometry(sat: MeanElements, site: GroundSite, t: datetime, *, uplink: bool) -> LinkGeometry:
    """`LinkGeometry` between ``site`` and ``sat`` at ``t`` (``uplink``: site transmits), with the site's elevation."""
    st, gs = sat.state_eci(t)[0], site_state_eci(site, t)
    la = look_angles(sat, site, t)
    el, az = math.radians(float(la.elevation_deg[0])), math.radians(float(la.azimuth_deg[0]))
    epoch = (t - datetime(2000, 1, 1, 12, tzinfo=t.tzinfo)).total_seconds()
    tx, rx = (gs, st) if uplink else (st, gs)
    vis: VisibilityStatus = "VISIBLE" if la.elevation_deg[0] >= site.mask_deg else "BELOW_ELEVATION_MASK"
    return geometry_from_states(epoch, tx, rx, elevation_rad=el, azimuth_rad=az, visibility=vis)
