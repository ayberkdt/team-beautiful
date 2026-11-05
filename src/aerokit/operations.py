"""Airport and air-traffic operations: queues, runway capacity, peak-hour delay, per-passenger CO₂.

* **M/M/1, M/G/1, M/D/1** (Poisson arrivals ``λ``, one server, mean service ``1/μ``, ``ρ = λ/μ < 1``):
  Pollaczek–Khinchine ``W_q = (ρ + λ μ Var(S)) / (2 (μ − λ))``, ``L = λ W`` (Little), ``W = W_q + 1/μ``.
  ``Var(S) = 1/μ²`` gives M/M/1 (``W_q = ρ / (μ − λ)``), ``Var(S) = 0`` gives M/D/1 (half the M/M/1 wait).
  A runway is the usual server: ``1/μ`` is the mean separation (runway occupancy) time.
* **M/M/c** (``c`` servers: stands, check-in desks, security lanes): Erlang C probability of waiting
  ``C(c, λ/μ)`` and ``W = C / (cμ − λ) + 1/μ``.
* **Peak periods** where demand exceeds capacity are not steady queues; :func:`peak_queue` steps the deterministic
  cumulative balance ``q_{k+1} = max(0, q_k + a_k − c_k)`` per interval (a fluid queue) and sums the delay.
* **CO₂ per passenger** as in the ICAO Carbon Emissions Calculator (Methodology v8, 2015):
  ``3.16 × fuel × pax-to-freight factor / (economy-equivalent seats × load factor)``.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from aerokit.references import cite

__all__ = ["QueueMetrics", "mg1", "mm1", "md1", "mmc", "erlang_c", "runway_capacity_per_hour", "PeakQueue",
           "peak_queue", "co2_per_passenger_icao"]


@dataclass(frozen=True)
class QueueMetrics:
    """Steady-state means (time unit of the rates): utilisation, waits and numbers in queue/system."""

    rho: float
    Wq: float
    W: float
    Lq: float
    L: float
    p_wait: float | None = None


def _rates(lam: float, mu: float) -> None:
    if not (math.isfinite(lam) and math.isfinite(mu) and lam >= 0 and mu > 0):
        raise ValueError("need arrival rate >= 0 and service rate > 0")


@cite("wikipedia_queues_2026", note="Pollaczek–Khinchine mean formula and Little's law")
def mg1(lam: float, mu: float, service_variance: float) -> QueueMetrics:
    """M/G/1 means; raises ``ValueError`` if ``λ ≥ μ`` (no steady state)."""
    _rates(lam, mu)
    if service_variance < 0:
        raise ValueError("service-time variance must be >= 0")
    if lam >= mu:
        raise ValueError(f"unstable queue: utilisation λ/μ = {lam / mu:.3f} >= 1 (use peak_queue for overload)")
    rho = lam / mu
    Wq = (rho + lam * mu * service_variance) / (2.0 * (mu - lam))
    W = Wq + 1.0 / mu
    return QueueMetrics(rho, Wq, W, lam * Wq, lam * W)


def mm1(lam: float, mu: float) -> QueueMetrics:
    """M/M/1 (exponential service, ``Var(S) = 1/μ²``)."""
    return mg1(lam, mu, 1.0 / mu ** 2)


def md1(lam: float, mu: float) -> QueueMetrics:
    """M/D/1 (constant service, e.g. a fixed runway separation)."""
    return mg1(lam, mu, 0.0)


@cite("wikipedia_queues_2026", note="Erlang C formula")
def erlang_c(servers: int, offered_load: float) -> float:
    """Probability that an arrival waits, ``C(c, A)`` with ``A = λ/μ`` erlangs (requires ``A < c``)."""
    if servers < 1 or not (0 <= offered_load < servers):
        raise ValueError("need servers >= 1 and 0 <= offered load < servers")
    c, A = servers, offered_load
    top = A ** c / math.factorial(c) * c / (c - A)
    return top / (sum(A ** i / math.factorial(i) for i in range(c)) + top)


@cite("wikipedia_queues_2026", note="M/M/c mean response time W = C/(cμ − λ) + 1/μ")
def mmc(lam: float, mu: float, servers: int) -> QueueMetrics:
    """M/M/c means; raises ``ValueError`` if ``λ ≥ c μ``."""
    _rates(lam, mu)
    if servers < 1:
        raise ValueError("servers must be >= 1")
    if lam >= servers * mu:
        raise ValueError(f"unstable: λ/(cμ) = {lam / (servers * mu):.3f} >= 1")
    pw = erlang_c(servers, lam / mu)
    Wq = pw / (servers * mu - lam)
    W = Wq + 1.0 / mu
    return QueueMetrics(lam / (servers * mu), Wq, W, lam * Wq, lam * W, pw)


def runway_capacity_per_hour(separations_s: Sequence[float], fractions: Sequence[float] | None = None) -> float:
    """Movements per hour from the mean inter-movement separation (optionally weighted by pair fractions)."""
    s = np.asarray(separations_s, float)
    if s.size == 0 or (s <= 0).any():
        raise ValueError("separations must be positive")
    w = np.full(s.size, 1.0 / s.size) if fractions is None else np.asarray(fractions, float)
    if w.shape != s.shape or (w < 0).any() or not math.isclose(float(w.sum()), 1.0, rel_tol=1e-9):
        raise ValueError("fractions must be >= 0, one per separation, and sum to 1")
    return 3600.0 / float(np.dot(w, s))


@dataclass(frozen=True)
class PeakQueue:
    """Result of :func:`peak_queue` (counts per interval, delay in movement·hours if intervals are hours)."""

    queue: tuple[float, ...]
    served: tuple[float, ...]
    total_delay: float
    max_queue: float
    clears_after: int | None


def peak_queue(demand: Sequence[float], capacity: Sequence[float], interval: float = 1.0,
               initial_queue: float = 0.0) -> PeakQueue:
    """Deterministic fluid queue over intervals: ``q_{k+1} = max(0, q_k + a_k − c_k)``.

    ``total_delay`` integrates the queue with the trapezoid rule over each interval (``interval`` long);
    ``clears_after`` is the index of the interval at whose end the queue is empty for good (0 if there never is a
    queue, ``None`` if it is still non-empty at the end).
    """
    a, c = np.asarray(demand, float), np.asarray(capacity, float)
    if a.shape != c.shape or a.size == 0 or (a < 0).any() or (c < 0).any() or initial_queue < 0 or interval <= 0:
        raise ValueError("demand and capacity must be equal-length, non-negative; interval > 0")
    q, delay = float(initial_queue), 0.0
    queue: list[float] = []
    served: list[float] = []
    for k in range(a.size):
        nxt = max(0.0, q + float(a[k]) - float(c[k]))
        served.append(q + float(a[k]) - nxt)
        delay += 0.5 * (q + nxt) * interval
        q = nxt
        queue.append(q)
    positive = [k for k, x in enumerate(queue) if x > 0.0]
    clears = None if q > 0.0 else (positive[-1] + 1 if positive else 0)
    return PeakQueue(tuple(queue), tuple(served), delay, max(queue), clears)


@cite("icao_cec_2015", note="CO2 per pax = 3.16 x fuel x pax-to-freight factor / (y-seats x load factor)")
def co2_per_passenger_icao(total_fuel_kg: float, pax_to_freight_factor: float, economy_seats: float,
                           load_factor: float, co2_index: float = 3.16) -> float:
    """CO₂ [kg] attributed to one economy passenger of a flight burning ``total_fuel_kg`` (ICAO CEC v8)."""
    if not (total_fuel_kg >= 0 and 0 < pax_to_freight_factor <= 1 and economy_seats > 0 and 0 < load_factor <= 1
            and co2_index > 0):
        raise ValueError("invalid ICAO per-passenger inputs")
    return co2_index * total_fuel_kg * pax_to_freight_factor / (economy_seats * load_factor)
