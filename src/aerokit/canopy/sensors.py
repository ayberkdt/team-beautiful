"""Sensor channels with a self-checking output and fault injection.

A channel is a two-output (form-C / complementary) switch or a proximity sensor with complementary outputs: a healthy
channel always shows exactly one of its two outputs, so "both" (short) or "neither" (open wire, lost supply) is a
*detected* fault. A mechanically stuck actuator or a jammed target still gives a valid code — that is the *latent*
failure the architecture and the test interval must cover. Without self-checking (one plain contact) an open wire
looks like "not active" and a short like "active". The coding idea is generic engineering practice [Y]; failure
rates come from the cited sources in the study inputs, not from here.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

__all__ = ["Reading", "FAILURE_MODES", "Channel", "decode_complementary", "decode_single"]


class Reading(Enum):
    ACTIVE = "active"          # target present: canopy seated / bolt fully engaged
    INACTIVE = "inactive"
    FAULT = "fault"            # invalid code: open circuit, short, no supply


FAILURE_MODES = ("stuck_active", "stuck_inactive", "open_circuit", "short_circuit", "intermittent")
"""Injected channel failures. stuck_* = mechanical (valid code, latent); open/short = electrical; intermittent =
contact chatter (vibration), which reads INACTIVE on a fraction of samples when the truth is ACTIVE."""


def decode_complementary(out_a: bool, out_b: bool) -> Reading:
    """Complementary pair: (1, 0) active, (0, 1) inactive, anything else a fault."""
    if out_a and not out_b:
        return Reading.ACTIVE
    if out_b and not out_a:
        return Reading.INACTIVE
    return Reading.FAULT


def decode_single(out_a: bool) -> Reading:
    """One plain contact: an open wire and a released switch look the same."""
    return Reading.ACTIVE if out_a else Reading.INACTIVE


@dataclass
class Channel:
    """One sensing channel.

    ``failure`` is ``None`` (healthy) or one of :data:`FAILURE_MODES`; ``self_check`` selects complementary coding.
    """

    name: str
    failure: str | None = None
    self_check: bool = True
    chatter_fraction: float = 0.3

    def __post_init__(self) -> None:
        if self.failure is not None and self.failure not in FAILURE_MODES:
            raise ValueError(f"unknown failure mode {self.failure!r}; use one of {FAILURE_MODES}")

    def outputs(self, truth_active: bool, rng: np.random.Generator | None = None) -> tuple[bool, bool]:
        """The two raw outputs (the second is unused without self-check)."""
        f = self.failure
        active = truth_active
        if f == "stuck_active":
            active = True
        elif f == "stuck_inactive":
            active = False
        elif f == "intermittent" and truth_active:
            r = (rng or np.random.default_rng()).random()
            active = r >= self.chatter_fraction
        if f == "open_circuit":
            return False, False
        if f == "short_circuit":
            return True, True
        return active, not active

    def read(self, truth_active: bool, rng: np.random.Generator | None = None) -> Reading:
        a, b = self.outputs(truth_active, rng)
        return decode_complementary(a, b) if self.self_check else decode_single(a)
