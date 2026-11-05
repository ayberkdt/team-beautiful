# Copied from Sidera (sidera.core.kepler_j2, commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Mean-element orbits with first-order J2 secular drift: Kepler's equation and the secular rates.

The single definition of both, for every layer above ``core`` that needs an
analytic orbit: mission design (critical inclination, repeat ground tracks,
frozen orbits) and coverage (`sidera.communications.coverage.scenarios.KeplerianJ2Orbit`).

- `solve_kepler_elliptic`: ``M = E - e sin E`` by Newton's method from
  ``E0 = M + e sin M`` (Standish and Williams, JPL SSD "Keplerian Elements for
  Approximate Positions of the Major Planets"), to a tolerance in radians.
- `j2_secular_rates_rad_s`: the first-order secular rates of the node, the
  argument of periapsis and the mean anomaly under ``J2`` (unnormalized,
  ``J2 = -sqrt(5) C20``).

A mean-element orbit drops the short-period terms of order ``J2 (R/a)^2 a``
(about 6 km for a 400 km Mars orbit, under 1 km areostationary): right for
revisit and coverage statistics, not for a navigation-grade state.
"""

from __future__ import annotations

import math

__all__ = ["j2_secular_rates_rad_s", "solve_kepler_elliptic", "true_anomaly_from_eccentric"]

_MAX_ITERATIONS = 50


def solve_kepler_elliptic(mean_anomaly_rad: float, eccentricity: float, tolerance_rad: float = 1e-15) -> float:
    """Eccentric anomaly ``E`` [rad] with ``E - e sin E = M`` (``0 <= e < 1``), in the same turn as ``M``.

    Newton's method from ``E0 = M + e sin M``; for ``e > 0.8`` it starts at
    ``E0 = pi`` on the reduced anomaly, where the derivative ``1 - e cos E``
    cannot vanish.

    Reference: Standish & Williams (1992): Solution of Kepler's Equation [SIDERA-ALG-OE-002].
    """
    m, e = float(mean_anomaly_rad), float(eccentricity)
    if not (math.isfinite(m) and math.isfinite(e) and 0.0 <= e < 1.0):
        raise ValueError(f"need a finite mean anomaly and 0 <= e < 1, got M={mean_anomaly_rad!r}, e={eccentricity!r}")
    turns = math.floor((m + math.pi) / (2.0 * math.pi))
    reduced = m - 2.0 * math.pi * turns  # in [-pi, pi)
    big_e = math.pi if e > 0.8 else reduced + e * math.sin(reduced)
    if e > 0.8 and reduced < 0.0:
        big_e = -math.pi
    for _ in range(_MAX_ITERATIONS):
        step = (reduced - (big_e - e * math.sin(big_e))) / (1.0 - e * math.cos(big_e))
        big_e += step
        if abs(step) <= tolerance_rad:
            return big_e + 2.0 * math.pi * turns
    raise ValueError(f"Kepler's equation did not converge for M={m!r}, e={e!r}")


def true_anomaly_from_eccentric(eccentric_anomaly_rad: float, eccentricity: float) -> float:
    """``nu = 2 atan2(sqrt(1+e) sin(E/2), sqrt(1-e) cos(E/2))``, continuous with ``E``."""
    half = 0.5 * float(eccentric_anomaly_rad)
    e = float(eccentricity)
    return 2.0 * math.atan2(math.sqrt(1.0 + e) * math.sin(half), math.sqrt(1.0 - e) * math.cos(half))


def j2_secular_rates_rad_s(semi_major_axis_m: float, eccentricity: float, inclination_rad: float,
                           mu_m3_s2: float, j2: float, reference_radius_m: float) -> tuple[float, float, float]:
    """``(dOmega/dt, domega/dt, dM/dt)`` [rad/s] to first order in ``J2``.

    With ``n = sqrt(mu / a^3)``, ``p = a (1 - e^2)`` and ``k = n J2 (R/p)^2``:
    ``dOmega/dt = -3/2 k cos i``, ``domega/dt = 3/4 k (5 cos^2 i - 1)``,
    ``dM/dt = n + 3/4 k sqrt(1 - e^2) (3 cos^2 i - 1)``.

    Reference: none, a Sidera heuristic without a published source [SIDERA-HEUR-TRJ-017].
    """
    a, e, i = float(semi_major_axis_m), float(eccentricity), float(inclination_rad)
    mu, radius = float(mu_m3_s2), float(reference_radius_m)
    if not (math.isfinite(a) and a > 0.0 and math.isfinite(e) and 0.0 <= e < 1.0):
        raise ValueError("the semi-major axis must be positive and the eccentricity in [0, 1)")
    if not (math.isfinite(mu) and mu > 0.0 and math.isfinite(j2) and math.isfinite(radius) and radius > 0.0):
        raise ValueError("GM and the reference radius must be positive and J2 finite")
    n = math.sqrt(mu / a**3)
    k = n * float(j2) * (radius / (a * (1.0 - e * e))) ** 2
    c = math.cos(i)
    return -1.5 * k * c, 0.75 * k * (5.0 * c * c - 1.0), n + 0.75 * k * math.sqrt(1.0 - e * e) * (3.0 * c * c - 1.0)
