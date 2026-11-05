# Copied from Sidera (sidera.common.two_body, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Closed-form two-body relations: Kepler's third law, the ellipse radii and
the osculating conic of a state (energy, eccentricity vector, periapsis).

The one home of these formulas; the engine, the analysis and reporting code,
the mission designers, the ST-LRPS evaluation and the desktop UI all call it
instead of re-deriving them. Pure Python and NumPy, no numba, so the UI and CLI
can import it cheaply. SI units: metres, seconds, m^3/s^2; altitudes in km where
the name says so.
"""

# =============================================================================
# 0.                                  IMPORTS
# =============================================================================

from __future__ import annotations

import math
from typing import overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

from aerokit.comms.constants import KM_TO_M, M_TO_KM

# =============================================================================
# 1.                           KEPLER'S THIRD LAW
# =============================================================================


@overload
def orbital_period_s(semi_major_axis_m: float, mu_m3_s2: float) -> float: ...
@overload
def orbital_period_s(semi_major_axis_m: NDArray[np.float64], mu_m3_s2: float) -> NDArray[np.float64]: ...
def orbital_period_s(semi_major_axis_m: ArrayLike, mu_m3_s2: float) -> float | NDArray[np.float64]:
    """Period ``2 pi sqrt(a^3 / mu)`` [s] of a bound orbit.

    A non-positive or non-finite ``a`` (an unbound or undefined orbit) has no
    period and gives ``nan``; ``mu`` must be finite and positive. A scalar
    ``a`` returns a ``float``, an array returns an array of the same shape.
    """
    mu = float(mu_m3_s2)
    if not math.isfinite(mu) or mu <= 0.0:
        raise ValueError(f"mu must be finite and > 0, got {mu!r}")
    a = np.asarray(semi_major_axis_m, dtype=np.float64)
    period = np.full(a.shape, np.nan)
    bound = np.isfinite(a) & (a > 0.0)
    period[bound] = 2.0 * np.pi * np.sqrt(a[bound] ** 3 / mu)
    return float(period) if period.ndim == 0 else period


# =============================================================================
# 2.                       ELLIPSE RADII AND ALTITUDES
# =============================================================================


def _ensure_positive_finite(value: float, name: str) -> float:
    """
    Ensures a value is a finite number and strictly greater than zero.
    Used for physical constants like radii and gravitational parameters.
    """
    val = float(value)
    if not math.isfinite(val) or val <= 0.0:
        raise ValueError(f"Parameter '{name}' must be finite and > 0. Got: {val}")
    return val


def _validate_elliptic_geometry(semi_major_axis: float, eccentricity: float) -> tuple[float, float]:
    """
    Validates that the provided (a, e) parameters describe a valid elliptic orbit.

    Requirements:
    1. 0 <= eccentricity < 1
    2. semi_major_axis > 0
    """
    a = float(semi_major_axis)
    e = float(eccentricity)

    if not (math.isfinite(a) and math.isfinite(e)):
        raise ValueError(f"Orbital parameters must be finite. Got a={a}, e={e}")

    if not (0.0 <= e < 1.0):
        raise ValueError(f"Eccentricity must be in range [0, 1) for elliptic orbits. Got: {e}")

    if a <= 0.0:
        raise ValueError(f"Semi-major axis must be positive for elliptic orbits. Got: {a}")

    return a, e


def calculate_periapsis_apoapsis_radii(
    semi_major_axis: float,
    eccentricity: float
) -> tuple[float, float]:
    """
    Calculates periapsis and apoapsis radii from semi-major axis and eccentricity.

    Formulas:
    $$ r_p = a(1 - e) $$
    $$ r_a = a(1 + e) $$

    Returns
    -------
    periapsis_radius, apoapsis_radius : float [m]
    """
    a, e = _validate_elliptic_geometry(semi_major_axis, eccentricity)

    periapsis_radius = a * (1.0 - e)
    apoapsis_radius = a * (1.0 + e)

    return periapsis_radius, apoapsis_radius


def calculate_ae_from_radii(
    periapsis_radius: float,
    apoapsis_radius: float
) -> tuple[float, float]:
    r"""
    Computes semi-major axis and eccentricity from periapsis and apoapsis radii.

    Formulas:
    $$ a = \frac{r_p + r_a}{2} $$
    $$ e = \frac{r_a - r_p}{r_a + r_p} $$
    """
    rp = _ensure_positive_finite(periapsis_radius, "periapsis_radius")
    ra = _ensure_positive_finite(apoapsis_radius, "apoapsis_radius")

    # Safety: ensure apoapsis is actually the larger radius
    if ra < rp:
        rp, ra = ra, rp

    semi_major_axis = 0.5 * (rp + ra)
    eccentricity = (ra - rp) / (ra + rp)  # Safe since rp, ra > 0

    return semi_major_axis, eccentricity


def calculate_ae_from_altitudes(
    reference_radius: float,
    periapsis_alt_km: float,
    apoapsis_alt_km: float
) -> tuple[float, float]:
    """
    Derives (a, e) from altitudes above a reference radius.

    Parameters
    ----------
    reference_radius : float [m]
    periapsis_alt_km : float [km]
    apoapsis_alt_km : float [km]
    """
    r_ref = _ensure_positive_finite(reference_radius, "reference_radius")

    # Convert altitudes to radii in meters
    periapsis_radius = r_ref + float(periapsis_alt_km) * KM_TO_M
    apoapsis_radius = r_ref + float(apoapsis_alt_km) * KM_TO_M

    return calculate_ae_from_radii(periapsis_radius, apoapsis_radius)


def calculate_altitudes_from_ae(
    reference_radius: float,
    semi_major_axis: float,
    eccentricity: float
) -> tuple[float, float]:
    """
    Calculates periapsis and apoapsis altitudes [km] from orbital elements.
    """
    r_ref = _ensure_positive_finite(reference_radius, "reference_radius")

    periapsis_radius, apoapsis_radius = calculate_periapsis_apoapsis_radii(
        semi_major_axis, eccentricity
    )

    # Convert radii back to altitudes in km
    periapsis_alt_km = (periapsis_radius - r_ref) * M_TO_KM
    apoapsis_alt_km = (apoapsis_radius - r_ref) * M_TO_KM

    return periapsis_alt_km, apoapsis_alt_km


# =============================================================================
# 3.                     OSCULATING CONIC OF A STATE
# =============================================================================
# ``r`` and ``v`` share one inertial frame and broadcast over leading axes; one
# state gives a ``float`` (or a ``(3,)`` vector). No input checks: each caller
# owns its domain rule (raise, return None, flag a violation) for a zero
# radius, a radial or an unbound trajectory.


def _scalar_or_array(value: NDArray[np.float64]) -> float | NDArray[np.float64]:
    return float(value) if value.ndim == 0 else value


def circular_speed_m_s(radius_m: float, mu_m3_s2: float) -> float:
    """Speed of a circular orbit of radius ``r``: ``sqrt(mu / r)`` [m/s]."""
    return math.sqrt(float(mu_m3_s2) / float(radius_m))


def escape_speed_m_s(radius_m: float, mu_m3_s2: float) -> float:
    """Local escape speed ``sqrt(2 mu / r)`` [m/s], ``sqrt(2)`` times circular."""
    return math.sqrt(2.0 * float(mu_m3_s2) / float(radius_m))


def specific_energy(r_m: ArrayLike, v_m_s: ArrayLike, mu_m3_s2: float) -> float | NDArray[np.float64]:
    """Specific orbital energy ``|v|^2 / 2 - mu / |r|`` [J/kg]."""
    r = np.asarray(r_m, dtype=np.float64)
    v = np.asarray(v_m_s, dtype=np.float64)
    radius = np.linalg.norm(r, axis=-1)
    return _scalar_or_array(0.5 * np.einsum("...i,...i->...", v, v) - float(mu_m3_s2) / radius)


def eccentricity_vector(r_m: ArrayLike, v_m_s: ArrayLike, mu_m3_s2: float) -> NDArray[np.float64]:
    """``(v x h) / mu - r / |r|``, pointing at periapsis with length ``e``."""
    r = np.asarray(r_m, dtype=np.float64)
    v = np.asarray(v_m_s, dtype=np.float64)
    h = np.cross(r, v)
    return np.cross(v, h) / float(mu_m3_s2) - r / np.linalg.norm(r, axis=-1, keepdims=True)


def periapsis_radius_m(r_m: ArrayLike, v_m_s: ArrayLike, mu_m3_s2: float) -> float | NDArray[np.float64]:
    """Periapsis radius ``p / (1 + e)`` with ``p = |h|^2 / mu`` [m].

    Valid for every conic -- ellipse, parabola and hyperbola -- and well
    conditioned near ``e = 0``, unlike ``a (1 - e)`` with ``a`` from vis-viva.
    """
    r = np.asarray(r_m, dtype=np.float64)
    v = np.asarray(v_m_s, dtype=np.float64)
    h = np.cross(r, v)
    semi_latus_rectum = np.einsum("...i,...i->...", h, h) / float(mu_m3_s2)
    e = np.linalg.norm(eccentricity_vector(r, v, mu_m3_s2), axis=-1)
    return _scalar_or_array(semi_latus_rectum / (1.0 + e))


__all__ = [
    "circular_speed_m_s",
    "eccentricity_vector",
    "escape_speed_m_s",
    "periapsis_radius_m",
    "specific_energy",
    "orbital_period_s",
    "calculate_periapsis_apoapsis_radii",
    "calculate_ae_from_radii",
    "calculate_ae_from_altitudes",
    "calculate_altitudes_from_ae",
]
