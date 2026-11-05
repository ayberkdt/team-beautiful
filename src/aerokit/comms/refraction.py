# Copied from Sidera (sidera.communications.channel.tropospheric_refraction, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""
Apparent elevation of a space station through the Earth's troposphere, ITU-R P.834-9 section 4.

A radio ray leaving a ground station bends toward the Earth, so the antenna
points (and the station's mask applies) at the apparent elevation ``theta``,
above the free-space elevation ``theta0`` of the geometry. P.834's reference
atmosphere is ``n(x) = 1 + a exp(-b x)`` (``a = 0.000315``, ``b = 0.1361`` per
km, eq. 8, from ITU-R P.453) on an Earth of radius 6370 km; the correction it
gives as a closed form is

- ``tau(h, theta) = 1 / [1.314 + 0.6437 theta + 0.02869 theta^2 + h (0.2305
  + 0.09428 theta + 0.01096 theta^2) + 0.008583 h^2]`` [deg] at the apparent
  elevation ``theta`` (eq. 9),
- ``theta = theta0 + tau_s(h, theta0)`` with ``tau_s(h, theta0) = 1 / [1.728
  + 0.5411 theta0 + 0.03723 theta0^2 + h (0.1815 + 0.06272 theta0 + 0.01380
  theta0^2) + h^2 (0.01727 + 0.008288 theta0)]`` [deg] (eqs. 13, 14),

for station heights ``0 <= h <= 3`` km, derived for ``theta <= 10`` deg and "a
reasonable approximation" to 90 deg. A space station is visible at all only
when ``theta_m - tau(h, theta_m) <= theta0`` with ``theta_m = -arccos(r / (r +
h) n(0) / n(h))`` (eqs. 10, 11); below that the free-space elevation is
returned (the station cannot see it, and ``tau_s`` diverges near -4.7 deg).
At 6 deg (the DSN models' lower limit) the correction is 0.16 deg at sea level.
Against the integral the closed forms approximate (eqs. 5-8, evaluated by
quadrature in the tests), eq. 9 is within 0.012 deg and eq. 14 within 0.014
deg for 0-3 km and 1-90 deg. Not modelled: the actual weather (P.834's
average atmosphere only) and the ionosphere.
"""

from __future__ import annotations

import math

from aerokit.comms.rf import RfError

__all__ = [
    "REFERENCE_ATMOSPHERE_A",
    "REFERENCE_ATMOSPHERE_B_PER_KM",
    "REFRACTION_EARTH_RADIUS_KM",
    "apparent_elevation_deg",
    "minimum_visible_elevation_deg",
    "refraction_correction_deg",
]

#: P.834-9 eq. 8: ``n(x) = 1 + a exp(-b x)``, ``x`` in km.
REFERENCE_ATMOSPHERE_A = 0.000315
REFERENCE_ATMOSPHERE_B_PER_KM = 0.1361
#: The Earth radius P.834-9 eqs. 6-7 and 10 use [km].
REFRACTION_EARTH_RADIUS_KM = 6370.0


def _height_km(height_km: float) -> float:
    h = float(height_km)
    if not (math.isfinite(h) and h <= 3.0):
        raise RfError(f"ITU-R P.834 refraction holds for station heights up to 3 km, got {height_km!r} km")
    return max(h, 0.0)  # the reference atmosphere starts at the surface; a site below the ellipsoid is at 0


def refraction_correction_deg(height_km: float, apparent_elevation_deg: float) -> float:
    """``tau(h, theta)`` [deg], the bending at the apparent elevation ``theta`` (P.834-9 eq. 9).

    Reference: Recommendation ITU-R P.834-9 (2017), Eqs. 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
    [SIDERA-STD-COM-011].
    """
    h, t = _height_km(height_km), float(apparent_elevation_deg)
    if not math.isfinite(t):
        raise RfError(f"the elevation must be finite, got {apparent_elevation_deg!r}")
    return 1.0 / (1.314 + 0.6437 * t + 0.02869 * t * t + h * (0.2305 + 0.09428 * t + 0.01096 * t * t)
                  + 0.008583 * h * h)


def minimum_visible_elevation_deg(height_km: float) -> float:
    """The lowest free-space elevation a station at ``h`` can see: ``theta_m - tau(h, theta_m)`` (eqs. 10, 11).

    Reference: Recommendation ITU-R P.834-9 (2017), Eqs. 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
    [SIDERA-STD-COM-011].
    """
    h = _height_km(height_km)
    n0 = 1.0 + REFERENCE_ATMOSPHERE_A
    nh = 1.0 + REFERENCE_ATMOSPHERE_A * math.exp(-REFERENCE_ATMOSPHERE_B_PER_KM * h)
    r = REFRACTION_EARTH_RADIUS_KM
    theta_m = -math.degrees(math.acos(min(1.0, r / (r + h) * n0 / nh)))
    return theta_m - refraction_correction_deg(h, theta_m)


def apparent_elevation_deg(height_km: float, free_space_elevation_deg: float) -> float:
    """The elevation the antenna points at, ``theta0 + tau_s(h, theta0)`` [deg] (P.834-9 eqs. 13, 14).

    Below `minimum_visible_elevation_deg` the free-space elevation comes back
    unchanged: the ray is intercepted by the Earth there.

    Reference: Recommendation ITU-R P.834-9 (2017), Eqs. 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
    [SIDERA-STD-COM-011].
    """
    h, t = _height_km(height_km), float(free_space_elevation_deg)
    if not math.isfinite(t):
        raise RfError(f"the elevation must be finite, got {free_space_elevation_deg!r}")
    if t < minimum_visible_elevation_deg(h):
        return t
    return t + 1.0 / (1.728 + 0.5411 * t + 0.03723 * t * t + h * (0.1815 + 0.06272 * t + 0.01380 * t * t)
                      + h * h * (0.01727 + 0.008288 * t))
