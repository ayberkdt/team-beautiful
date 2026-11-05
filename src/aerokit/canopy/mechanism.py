"""Extra NG shoot-bolt canopy latch (facts from AAIB-28120) and the trip-point tolerance analysis of a lock sensor.

Coordinate used throughout: the **aft handle centre distance** ``x`` in mm, as AAIB measured it — 70 mm when the canopy
is fully locked (and also when it is open with the handles released), 60 mm when the spring alone has moved the bolts
only into the "partially locked" condition. A bolt-engagement sensor somewhere else on the linkage is described by the
equivalent handle distance at which it switches; how bolt-tip travel maps to handle travel on the real linkage is not
published and must be measured on the aircraft (assumption [Y], listed in the doc as a mentor question).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from aerokit.references import cite

__all__ = ["LatchMechanism", "EXTRA_NG", "engagement_fraction", "trip_probabilities", "trip_window"]


@cite("aaib_2024_g_miil", note="pp. 8-10 (bolts, ramp, handle gaps), p. 20 (forces, no visible difference), p. 24")
@dataclass(frozen=True)
class LatchMechanism:
    """Published latch facts of one canopy type.

    Attributes
    ----------
    bolts : int
        Number of shoot bolts on the common linkage tube.
    gap_locked_mm, gap_partial_mm : float
        Handle centre distance when fully locked and when only spring-engaged (partially locked).
    ramp_length_mm, ramp_rise_mm : float
        Shoot-bolt end ramp; rollers climbing it compress the seal (3:1 mechanical advantage).
    force_open_locked_n, force_partial_to_locked_n, force_open_partial_n : float
        Measured handle forces on another aircraft of the type.
    force_drive_open_partial_n : float
        AAIB's estimate of the force needed to drive partially-locked bolts open (≥ 3 × 90 N).
    open_and_released_reads_locked : bool
        True when the handle position is the same with the canopy open and handles released as when locked: a
        handle-only sensor then cannot tell "open" from "locked" — a seated sensor is required.
    """

    name: str
    bolts: int
    bolt_side: str
    hinge_side: str
    gap_locked_mm: float
    gap_partial_mm: float
    ramp_length_mm: float
    ramp_rise_mm: float
    force_open_locked_n: float
    force_partial_to_locked_n: float
    force_open_partial_n: float
    force_drive_open_partial_n: float
    visible_difference_at_frame: bool
    open_and_released_reads_locked: bool

    @property
    def travel_mm(self) -> float:
        """Handle travel between partially and fully locked (10 mm on the Extra NG)."""
        return self.gap_locked_mm - self.gap_partial_mm

    @property
    def ramp_advantage(self) -> float:
        """Ramp length / rise (AAIB states 3 to 1)."""
        return self.ramp_length_mm / self.ramp_rise_mm


EXTRA_NG = LatchMechanism(
    name="Extra NG", bolts=3, bolt_side="left", hinge_side="right",
    gap_locked_mm=70.0, gap_partial_mm=60.0, ramp_length_mm=15.0, ramp_rise_mm=5.0,
    force_open_locked_n=136.0, force_partial_to_locked_n=60.0, force_open_partial_n=90.0,
    force_drive_open_partial_n=270.0, visible_difference_at_frame=False, open_and_released_reads_locked=True)
"""The G-MIIL type (AAIB-28120 pp. 8-10, 20, 24). Every number is [D]."""


def engagement_fraction(gap_mm: float, mech: LatchMechanism = EXTRA_NG) -> float:
    """0 at the partially-locked gap, 1 at full lock, linear in between (linearity is an assumption [Y])."""
    return min(1.0, max(0.0, (gap_mm - mech.gap_partial_mm) / mech.travel_mm))


def _phi(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def _pdf(z: float) -> float:
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def trip_probabilities(trip_mm: float, sigma_trip_mm: float, sigma_full_mm: float, hazard_below_mm: float,
                       mech: LatchMechanism = EXTRA_NG) -> tuple[float, float]:
    """(P(sensor reads LOCKED | partial lock), P(sensor reads NOT LOCKED | full lock)) for one engagement sensor.

    The sensor reads LOCKED when the handle-equivalent position ``x`` is at or beyond its actual trip point, which is
    the nominal ``trip_mm`` plus a normal rigging/wear error of s.d. ``sigma_trip_mm``. A fully locked latch sits at
    the locked gap with s.d. ``sigma_full_mm``. A hazardous partial lock is any ``x`` uniformly between the partially
    locked gap and ``hazard_below_mm`` (uniform: no data on where real partial locks sit; assumption [Y]).

    Closed forms: miss = (1/(b − a)) ∫ Φ((x − t)/σ) dx with ∫Φ(z)dz = zΦ(z) + φ(z); false = Φ((t − 70)/√(σt² + σf²)).
    """
    if sigma_trip_mm <= 0 or sigma_full_mm < 0:
        raise ValueError("sigma_trip_mm must be > 0 and sigma_full_mm >= 0")
    a, b = mech.gap_partial_mm, hazard_below_mm
    if not a < b <= mech.gap_locked_mm:
        raise ValueError("hazard_below_mm must lie in (partial gap, locked gap]")
    s = sigma_trip_mm
    za, zb = (a - trip_mm) / s, (b - trip_mm) / s
    miss = s * ((zb * _phi(zb) + _pdf(zb)) - (za * _phi(za) + _pdf(za))) / (b - a)
    false = _phi((trip_mm - mech.gap_locked_mm) / math.hypot(sigma_trip_mm, sigma_full_mm))
    return min(1.0, max(0.0, miss)), false


def trip_window(sigma_trip_mm: float, sigma_full_mm: float, hazard_below_mm: float, max_miss: float,
                max_false: float, mech: LatchMechanism = EXTRA_NG, step_mm: float = 0.01) -> tuple[float, float] | None:
    """Range of nominal trip points meeting both limits (None if the tolerances make it impossible)."""
    ok = []
    t = mech.gap_partial_mm
    while t <= mech.gap_locked_mm + 1e-9:
        m, f = trip_probabilities(t, sigma_trip_mm, sigma_full_mm, hazard_below_mm, mech)
        if m <= max_miss and f <= max_false:
            ok.append(t)
        t += step_mm
    return (round(ok[0], 3), round(ok[-1], 3)) if ok else None
