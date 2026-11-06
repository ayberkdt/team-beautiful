"""Feedback elements (cues) and barriers on top of the sensing Monte Carlo: which combination of light, sound,
vibration, take-off gate or engine shut-down gives the lowest risk, and at what cost.

The sensing model (:mod:`aerokit.canopy.montecarlo`) answers "does the system *know* the canopy is not locked?".
This module answers "does the pilot then *do* something?". For a true alert the take-off continues unlocked when

1. the sensors miss it (``miss_h`` from the Monte Carlo), or
2. the alert is raised but no cue is noticed, or a cue is noticed and the pilot does not believe it, **and** any
   barrier (gate, shut-down) is overridden or absent.

Per hazard ``h`` with unalerted-hazard probability ``u_h`` (hazard rate × pilot check miss)::

    risk = Σ_h u_h · [ miss_h + (1 − miss_h) · (1 − D·c) · g ]

* ``D`` — probability that at least one cue is noticed in time, averaged over operating conditions (normal,
  high workload, headset off). Cues are combined either as independent (``1 − Π(1 − d_i)``, optimistic) or fully
  dependent (``max d_i``, pessimistic); both bounds are reported.
* ``c`` — compliance once noticed: 1 ("pilot always acts"), the alert's positive predictive value
  ("probability matching", the cry-wolf model already used for the sensing study), or any fixed probability given as
  a number, so that compliance can be swept as an independent parameter.
* ``g`` — probability the barrier does not stop the take-off once the cues have failed: 1 without a barrier;
  ``(1 − c)·p_override_distrust + c·p_override_trust`` with a gate (a gate cannot go unnoticed: the lever stops).

Consequences (fatal-equivalent per flight) are computed separately, because an engine shut-down changes the
*outcome* of an event and turns every false alert raised in the air into an engine failure.

All numbers live in ``02_EASA/inputs/cues.json`` with a source and a tag per value; nothing is hard-coded here.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

__all__ = ["Cue", "Barrier", "Option", "p_detect", "option_risk", "p_in_time_lognormal", "fatal_equivalent", "mcda_rank"]


@dataclass(frozen=True)
class Cue:
    """One feedback element. ``p_detect[condition]`` = probability the pilot notices it in time (before committing
    to the take-off) when it is presented, under that operating condition."""

    key: str
    label: str
    p_detect: Mapping[str, float]

    def __post_init__(self) -> None:
        for k, v in self.p_detect.items():
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{self.key}: p_detect[{k}] = {v} outside [0, 1]")


@dataclass(frozen=True)
class Barrier:
    """Something that physically stops the take-off unless the pilot overrides it.

    ``p_override_distrust``: probability the pilot overrides (pushes through, restarts, disables) when he does not
    believe the alert; ``p_override_trust``: when he does believe it. ``active_in_air``: True only for an in-flight
    engine shut-down — then a false alert in the air causes an engine loss."""

    key: str
    label: str
    p_override_distrust: float
    p_override_trust: float = 0.0
    active_in_air: bool = False
    p_new_hazard_engine_loss: float = 0.0   # per flight: the device itself cuts the engine in the air (logic fault)


@dataclass(frozen=True)
class Option:
    """A design option = sensing architecture key (``A0``…``A4`` or a custom result key) + cues + optional barrier."""

    key: str
    label: str
    arch: str
    cues: tuple[str, ...]
    barrier: str | None = None
    attrs: Mapping[str, float] = field(default_factory=dict)


def p_detect(cues: Sequence[Cue], conditions: Mapping[str, float], dependence: str = "independent") -> float:
    """Probability that at least one cue is noticed, averaged over conditions (weights must sum to 1)."""
    if dependence not in ("independent", "max"):
        raise ValueError("dependence must be 'independent' or 'max'")
    tot = sum(conditions.values())
    if abs(tot - 1.0) > 1e-9:
        raise ValueError(f"condition weights sum to {tot}, not 1")
    if not cues:
        return 0.0
    out = 0.0
    for cond, w in conditions.items():
        ds = [c.p_detect[cond] for c in cues]
        if dependence == "independent":
            miss = 1.0
            for d in ds:
                miss *= 1.0 - d
            out += w * (1.0 - miss)
        else:
            out += w * max(ds)
    return out


def option_risk(miss: Mapping[str, float], u: Mapping[str, float], false_alert_per_flight: float,
                cues: Sequence[Cue], conditions: Mapping[str, float], barrier: Barrier | None = None,
                compliance: str | float = "full", dependence: str = "independent", floor: float = 0.0,
                p_in_time: float = 1.0) -> dict[str, float]:
    """Per-flight probability of taking off with the canopy not locked and nothing effective done.

    ``miss[h]``: sensing miss probability under hazard ``h``; ``u[h]``: hazard rate × pilot-check miss;
    ``false_alert_per_flight``: false + nuisance alerts per flight (no hazard present); ``p_in_time``: probability
    that a pilot who notices and believes the alert also acts before the reject window closes (see
    :func:`p_in_time_lognormal`). A barrier acts on lever advance and is not limited by it."""
    if not 0.0 <= p_in_time <= 1.0:
        raise ValueError("p_in_time outside [0, 1]")
    if isinstance(compliance, str) and compliance not in ("full", "matching"):
        raise ValueError("compliance must be 'full', 'matching' or a probability")
    if not isinstance(compliance, str) and not 0.0 <= float(compliance) <= 1.0:
        raise ValueError("compliance probability outside [0, 1]")
    true_alerts = sum(u[h] * (1.0 - miss[h]) for h in u)
    ppv = true_alerts / (true_alerts + false_alert_per_flight) if true_alerts + false_alert_per_flight > 0 else 1.0
    if isinstance(compliance, str):
        c = 1.0 if compliance == "full" else max(floor, ppv)
    else:
        c = float(compliance)          # independent parameter (review 5 Nov: do not tie compliance to PPV only)
    d = p_detect(cues, conditions, dependence) * p_in_time
    if barrier is None:
        g = 1.0
    else:
        g = (1.0 - c) * barrier.p_override_distrust + c * barrier.p_override_trust
    p_fail_given_alert = (1.0 - d * c) * g
    risk_alerted = sum(u[h] * (1.0 - miss[h]) * p_fail_given_alert for h in u)
    risk = sum(u[h] * miss[h] for h in u) + risk_alerted
    base = sum(u.values())
    return {"risk": risk, "risk_alerted": risk_alerted, "baseline": base,
            "reduction_factor": base / risk if risk > 0 else float("inf"),
            "ppv": ppv, "compliance": c, "p_detect": d, "barrier_pass": g, "p_fail_given_alert": p_fail_given_alert}


def p_in_time_lognormal(windows_s: Sequence[float], weights: Sequence[float], rt_median_s: float,
                        rt_p95_s: float) -> float:
    """Probability that a lognormal response time (given by its median and 95th percentile) is shorter than the
    available window, averaged over take-off cases (``windows_s`` with ``weights`` summing to 1). A window ≤ 0
    gives 0."""
    import math

    if rt_p95_s <= rt_median_s or rt_median_s <= 0:
        raise ValueError("need 0 < median < p95")
    if abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError("weights must sum to 1")
    sigma = math.log(rt_p95_s / rt_median_s) / 1.6448536269514722
    out = 0.0
    for w_s, wt in zip(windows_s, weights):
        if w_s > 0:
            z = (math.log(w_s) - math.log(rt_median_s)) / sigma
            out += wt * 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return out


def fatal_equivalent(risk: float, risk_alerted: float, false_alert_per_flight: float, barrier: Barrier | None,
                     p_open: float, f_open: float, f_engine_loss: float, f_shutdown_with_open_canopy: float,
                     p_false_alert_airborne: float) -> dict[str, float]:
    """Fatal outcomes per flight, split into canopy openings and engine losses caused by the device.

    ``risk`` = unlocked take-offs per flight (from :func:`option_risk`); ``risk_alerted`` = the part of it in which
    the system *did* raise the alert (the pilot missed, disbelieved or overrode it).

    * No in-flight barrier: each unlocked take-off opens with ``p_open`` and is fatal with ``f_open``.
    * In-flight shut-down (``barrier.active_in_air``): the alerted part becomes an engine cut **with** the canopy
      unlocked (fatal ``f_shutdown_with_open_canopy``), and every false alert that occurs airborne
      (``false_alert_per_flight × p_false_alert_airborne``) becomes an engine loss with the canopy closed (fatal
      ``f_engine_loss``).
    * Any barrier may also cut the engine in the air through its own fault (``p_new_hazard_engine_loss``)."""
    engine = 0.0
    if barrier is not None and barrier.active_in_air:
        canopy = (risk - risk_alerted) * p_open * f_open
        engine += risk_alerted * f_shutdown_with_open_canopy
        engine += false_alert_per_flight * p_false_alert_airborne * f_engine_loss
    else:
        canopy = risk * p_open * f_open
    if barrier is not None:
        engine += barrier.p_new_hazard_engine_loss * f_engine_loss
    return {"canopy": canopy, "engine": engine, "total": canopy + engine}


def mcda_rank(scores: Mapping[str, Mapping[str, float]], weights: Mapping[str, float], n: int = 20_000,
              concentration: float = 20.0, seed: int = 3) -> dict[str, dict[str, float]]:
    """Weighted-sum ranking and its stability under uncertain weights.

    ``scores[option][criterion]`` on a common 0–1 scale (1 best); ``weights[criterion]`` sum to 1. Weights are
    resampled from a Dirichlet distribution centred on the given weights (``concentration`` = how sure we are); the
    result gives each option's nominal score and the share of samples in which it ranks first."""
    import numpy as np

    opts = list(scores)
    crit = list(weights)
    w0 = np.array([weights[k] for k in crit], float)
    if abs(w0.sum() - 1.0) > 1e-9:
        raise ValueError("weights must sum to 1")
    s = np.array([[scores[o][k] for k in crit] for o in opts], float)
    nominal = s @ w0
    rng = np.random.default_rng(seed)
    w = rng.dirichlet(w0 * concentration, n)
    tot = s @ w.T                                   # options × samples
    first = np.bincount(tot.argmax(axis=0), minlength=len(opts)) / n
    ranks = (-tot).argsort(axis=0).argsort(axis=0) + 1
    return {o: {"score": float(nominal[i]), "p_first": float(first[i]), "mean_rank": float(ranks[i].mean())}
            for i, o in enumerate(opts)}
