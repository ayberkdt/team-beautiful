"""Per-flight Monte Carlo of missed alerts and false alarms versus sensor architecture, and the pilot in the loop.

Each simulated flight draws (1) the true latch condition — conditioned on one hazard type so that rare events are
sampled efficiently — (2) each channel's rigging error and failure state, (3) the readings, and (4) fuses them with
the **same truth table** as :func:`aerokit.canopy.logic.canopy_state` (vectorised; a test checks the two agree on every
reading combination). The take-off risk is then combined from the conditional results and the exposure
(hazard base rates and the probability the pilot's own check misses the hazard), optionally with the pilot's
**compliance** depending on the alert's positive predictive value (the cry-wolf effect).

Hazard types
------------
``partial``   all three bolts short of full engagement together (they share one linkage tube): the G-MIIL partial lock.
``one_bolt``  one bolt not engaged, the others fine (e.g. loose rear fitting, the SP-HMM contributory factor).
``unseated``  canopy not down on the rim at all.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np

from aerokit.canopy.fta import standby_unavailability
from aerokit.canopy.mechanism import EXTRA_NG, LatchMechanism
from aerokit.references import cite

__all__ = ["HAZARDS", "Architecture", "ARCHITECTURES", "ChannelRates", "Tolerance", "ConditionalResult",
           "simulate", "fuse", "Exposure", "takeoff_risk", "wilson"]

HAZARDS = ("partial", "one_bolt", "unseated")
LOCKED, CLOSED_UNLOCKED, OPEN, UNKNOWN = 0, 1, 2, 3
ACTIVE, INACTIVE, FAULT = 1, 0, -1


@dataclass(frozen=True)
class Architecture:
    """``seated`` = number of seated channels; ``bolt_sensors`` = bolt index (0 front, 1 centre, 2 rear) of each
    engagement channel — a repeated index means redundant channels on the same bolt (all must read ACTIVE)."""

    key: str
    label: str
    seated: int
    bolt_sensors: tuple[int, ...]
    self_check: bool = True

    @property
    def has_system(self) -> bool:
        return self.seated + len(self.bolt_sensors) > 0


ARCHITECTURES: dict[str, Architecture] = {a.key: a for a in (
    Architecture("A0", "No system (pilot check only)", 0, ()),
    Architecture("A1", "Seated switch only, plain contact", 1, (), self_check=False),
    Architecture("A2", "Seated + rear bolt, self-checking", 1, (2,)),
    Architecture("A3", "Seated + all three bolts, self-checking", 1, (0, 1, 2)),
    Architecture("A4", "Dual seated + dual channel per bolt", 2, (0, 0, 1, 1, 2, 2)),
)}


@dataclass(frozen=True)
class ChannelRates:
    """Per-channel failure rates [1/h] and exposure times [h]. ``latent_interval_h`` is the interval between tests
    that would reveal a stuck-ACTIVE channel (a functional check, or the open-canopy plausibility check when the unit
    is powered while the canopy is opened)."""

    stuck_active_per_h: float
    stuck_inactive_per_h: float
    open_per_h: float
    short_per_h: float
    flight_h: float = 1.0
    latent_interval_h: float = 100.0

    def mode_probabilities(self) -> dict[str, float]:
        """Probability per flight that a channel is in each failure mode."""
        return {"stuck_active": standby_unavailability(self.stuck_active_per_h, self.latent_interval_h),
                "stuck_inactive": 1.0 - math.exp(-self.stuck_inactive_per_h * self.flight_h),
                "open": 1.0 - math.exp(-self.open_per_h * self.flight_h),
                "short": 1.0 - math.exp(-self.short_per_h * self.flight_h)}


@dataclass(frozen=True)
class Tolerance:
    """Trip point (handle-equivalent mm), rigging s.d., s.d. of the fully-locked position, hazard threshold, and a
    **systematic** rigging error: with probability ``p_misrig_common`` per flight every engagement channel trips
    ``misrig_shift_mm`` away from nominal (one wrong gauge / one disturbed bracket set-up; found at the next
    functional check). A negative shift makes the sensors read LOCKED too early (latent miss)."""

    trip_mm: float = 68.0
    sigma_trip_mm: float = 0.3
    sigma_full_mm: float = 0.3
    hazard_below_mm: float = 67.0
    p_misrig_common: float = 0.0
    misrig_shift_mm: float = -5.0


@dataclass(frozen=True)
class ConditionalResult:
    architecture: str
    hazard: str | None
    n: int
    counts: Mapping[int, int] = field(default_factory=dict)

    def p(self, state: int) -> float:
        return self.counts.get(state, 0) / self.n

    @property
    def p_locked(self) -> float:
        """Under a hazard: the missed-alert probability. Without a hazard: 1 − (false alarm + fault caution)."""
        return self.p(LOCKED)

    @property
    def p_alert(self) -> float:
        """Red/amber "unlocked/open" alert."""
        return self.p(CLOSED_UNLOCKED) + self.p(OPEN)

    @property
    def p_fault(self) -> float:
        return self.p(UNKNOWN)

    def interval(self, state: int) -> tuple[float, float]:
        return wilson(self.counts.get(state, 0), self.n)


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score 95 % interval for a binomial proportion (standard statistics; no source needed beyond any text)."""
    if n <= 0:
        raise ValueError("n must be positive")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def fuse(seated: np.ndarray, bolts: np.ndarray, has_system: bool = True) -> np.ndarray:
    """Vectorised :func:`aerokit.canopy.logic.canopy_state`. ``seated`` (N, s) and ``bolts`` (N, b) hold
    ACTIVE=1 / INACTIVE=0 / FAULT=-1. Returns LOCKED / CLOSED_UNLOCKED / OPEN / UNKNOWN codes."""
    n = seated.shape[0] if seated.ndim == 2 else bolts.shape[0]
    out = np.full(n, LOCKED, dtype=np.int8)
    if not has_system:
        return out
    s_n, b_n = seated.shape[1], bolts.shape[1]
    fault = np.zeros(n, bool)
    if s_n:
        fault |= np.any(seated == FAULT, axis=1)
    if b_n:
        fault |= np.any(bolts == FAULT, axis=1)
    s_any = np.any(seated == ACTIVE, axis=1) if s_n else np.zeros(n, bool)
    s_all = np.all(seated == ACTIVE, axis=1) if s_n else np.ones(n, bool)
    b_any = np.any(bolts == ACTIVE, axis=1) if b_n else np.zeros(n, bool)
    b_all = np.all(bolts == ACTIVE, axis=1) if b_n else np.ones(n, bool)
    disagree = s_any & ~s_all if s_n else np.zeros(n, bool)
    not_seated = ~s_all if s_n else np.zeros(n, bool)
    out = np.where(~b_all, CLOSED_UNLOCKED, out)
    out = np.where(not_seated, OPEN, out)
    out = np.where(not_seated & b_any, UNKNOWN, out)
    out = np.where(disagree | fault, UNKNOWN, out)
    return out.astype(np.int8)


def _read(truth: np.ndarray, probs: Mapping[str, float], self_check: bool, rng: np.random.Generator) -> np.ndarray:
    u = rng.random(truth.shape)
    r = np.where(truth, ACTIVE, INACTIVE).astype(np.int8)
    edges = np.cumsum([probs["stuck_active"], probs["stuck_inactive"], probs["open"], probs["short"]])
    sa, si = u < edges[0], (u >= edges[0]) & (u < edges[1])
    op, sh = (u >= edges[1]) & (u < edges[2]), (u >= edges[2]) & (u < edges[3])
    r[sa] = ACTIVE
    r[si] = INACTIVE
    r[op] = FAULT if self_check else INACTIVE
    r[sh] = FAULT if self_check else ACTIVE
    return r


def simulate(arch: Architecture, hazard: str | None, rates: ChannelRates, tol: Tolerance, n: int = 200_000,
             seed: int = 1, mech: LatchMechanism = EXTRA_NG) -> ConditionalResult:
    """Simulate ``n`` flights of ``arch`` with the latch in condition ``hazard`` (``None`` = correctly locked)."""
    if hazard is not None and hazard not in HAZARDS:
        raise ValueError(f"hazard must be None or one of {HAZARDS}")
    rng = np.random.default_rng(seed)
    nb = mech.bolts
    x = rng.normal(mech.gap_locked_mm, tol.sigma_full_mm, (n, nb))
    seated_truth = np.ones(n, bool)
    if hazard == "partial":
        x = rng.uniform(mech.gap_partial_mm, tol.hazard_below_mm, (n, 1)) + rng.normal(0, tol.sigma_full_mm, (n, nb))
    elif hazard == "one_bolt":
        j = rng.integers(0, nb, n)
        x[np.arange(n), j] = rng.uniform(mech.gap_partial_mm, tol.hazard_below_mm, n)
    elif hazard == "unseated":
        x[:] = -np.inf
        seated_truth[:] = False
    probs = rates.mode_probabilities()
    s = _read(np.repeat(seated_truth[:, None], arch.seated, axis=1), probs, arch.self_check, rng) \
        if arch.seated else np.zeros((n, 0), np.int8)
    if arch.bolt_sensors:
        idx = np.array(arch.bolt_sensors)
        trip = rng.normal(tol.trip_mm, tol.sigma_trip_mm, (n, idx.size))
        if tol.p_misrig_common > 0:
            trip[rng.random(n) < tol.p_misrig_common] += tol.misrig_shift_mm
        b = _read(x[:, idx] >= trip, probs, arch.self_check, rng)
    else:
        b = np.zeros((n, 0), np.int8)
    state = fuse(s, b, arch.has_system)
    vals, cnt = np.unique(state, return_counts=True)
    return ConditionalResult(arch.key, hazard, n, {int(v): int(c) for v, c in zip(vals, cnt)})


@dataclass(frozen=True)
class Exposure:
    """Per-flight probability of each hazard *before* the pilot's own check, the probability the check misses it, and
    the per-flight probability of a **nuisance** alert from causes outside the channel model (intermittent connector,
    contamination, a sensor knocked out of adjustment towards "late")."""

    p_hazard: Mapping[str, float]
    p_pilot_miss: Mapping[str, float]
    p_nuisance: float = 0.0


@cite("bliss_gilson_deaton_1995", "wickens_dixon_2007",
      note="'matching': P(act | alert) = positive predictive value (probability matching, abstract-level evidence)")
def takeoff_risk(results: Mapping[str | None, ConditionalResult], exp: Exposure, compliance: str = "full",
                 floor: float = 0.0) -> dict[str, float]:
    """Probability per flight of starting the take-off with the canopy not locked and no effective alert.

    ``compliance``: ``"full"`` — the pilot always acts on a true alert; ``"matching"`` — the pilot acts with a
    probability equal to the alert's positive predictive value (probability matching), never below ``floor``.
    """
    if compliance not in ("full", "matching"):
        raise ValueError("compliance must be 'full' or 'matching'")
    u = {h: exp.p_hazard[h] * exp.p_pilot_miss[h] for h in HAZARDS}
    p_none = 1.0 - sum(exp.p_hazard.values())
    miss = {h: results[h].p_locked for h in HAZARDS}
    true_alerts = sum(u[h] * (1.0 - miss[h]) for h in HAZARDS)
    has_system = ARCHITECTURES[results[None].architecture].has_system         if results[None].architecture in ARCHITECTURES else True
    false_alerts = p_none * (results[None].p_alert + (exp.p_nuisance if has_system else 0.0))
    ppv = true_alerts / (true_alerts + false_alerts) if true_alerts + false_alerts > 0 else 1.0
    c = 1.0 if compliance == "full" else max(floor, ppv)
    risk = sum(u[h] * (miss[h] + (1.0 - miss[h]) * (1.0 - c)) for h in HAZARDS)
    base = sum(u.values())
    return {"risk": risk, "baseline": base, "reduction_factor": base / risk if risk > 0 else float("inf"),
            "ppv": ppv, "compliance": c, "false_alarm_per_flight": false_alerts,
            "fault_caution_per_flight": p_none * results[None].p_fault}
