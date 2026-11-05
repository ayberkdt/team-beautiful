"""ERCS view of the retrofit: how much the "warning systems" barrier changes the risk score of the unlocked-canopy
scenario. Reuses :func:`aerokit.investigation.ercs_score` (read-only).
"""
from __future__ import annotations

from collections.abc import Mapping

from aerokit.investigation import ERCS_BARRIERS, ErcsResult, ercs_score

__all__ = ["SCENARIOS", "with_and_without"]

SCENARIOS: dict[str, dict] = {
    "takeoff_partial_lock": {
        "text": "Take-off with the canopy partially locked; canopy opens or departs in flight; loss of vision or control",
        "key_risk_area": "aircraft upset",
        "severity": "M",
        "severity_reason": "two-seat aeroplane; G-MIIL shows canopy loss can end in aircraft destruction (AAIB p. 1)",
        "barriers": {"design": "failed", "regulations and procedures": "failed", "situational awareness": "failed",
                     "late recovery": "remaining", "protections": "remaining"},
    },
    "inflight_unlock": {
        "text": "Canopy locked at take-off, a bolt backs out in flight (loose fitting / loss of stiffness, cf. SP-HMM)",
        "key_risk_area": "aircraft upset",
        "severity": "M",
        "severity_reason": "as above; SP-HMM canopy detached in flight (AAIB p. 23)",
        "barriers": {"design": "failed", "regulations and procedures": "remaining", "late recovery": "remaining",
                     "protections": "remaining"},
    },
}
"""Barrier states are our judgement [Y]; ``warning systems`` is set by :func:`with_and_without`."""


def with_and_without(scenario: Mapping) -> tuple[ErcsResult, ErcsResult]:
    """(score without a canopy alert, score with the alert counted as a remaining barrier)."""
    base = dict(scenario["barriers"])
    if "warning systems" in base:
        raise ValueError("leave 'warning systems' out; it is the barrier being compared")
    unknown = [b for b in base if b not in ERCS_BARRIERS]
    if unknown:
        raise KeyError(f"not an ERCS barrier: {unknown}")
    kra, sev = scenario["key_risk_area"], scenario["severity"]
    return (ercs_score(kra, sev, {**base, "warning systems": "n/a"}),
            ercs_score(kra, sev, {**base, "warning systems": "remaining"}))
