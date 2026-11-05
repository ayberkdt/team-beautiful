# Copied from Sidera (sidera.communications.coverage.timeline (integrate_data_volume_bits only), commit 02029b76) into aerokit on 2026-10-25 at the author's request;
# only import paths were changed. Copyright (c) 2026 Ayberk Demirkanat, Sidera proprietary licence.
"""Data volume of a sampled bit-rate history: ``D = ∫ R_b(t) dt`` with three explicit sampling rules."""
from __future__ import annotations

import math
from collections.abc import Sequence
from itertools import pairwise
from typing import Literal

from aerokit.comms.rf import RfError

__all__ = ["DataVolumeMethod", "integrate_data_volume_bits"]

DataVolumeMethod = Literal["held_previous_sample", "trapezoidal", "held_lower"]


def integrate_data_volume_bits(
    epochs_s: Sequence[float],
    rates_bps: Sequence[float],
    method: DataVolumeMethod = "held_previous_sample",
) -> float:
    """``D = integral R_b(t) dt`` over a sampled rate history, in bits.

    The three methods differ only in what they assume between samples; see this
    module's docstring for which to pick. A single sample has no interval and
    returns 0.0, which is the honest answer rather than an extrapolation.
    """
    if method not in ("held_previous_sample", "trapezoidal", "held_lower"):
        raise RfError(
            f"unknown data-volume integration method {method!r}; expected one "
            "of 'held_previous_sample', 'trapezoidal', 'held_lower'"
        )
    times = [float(t) for t in epochs_s]
    rates = [float(r) for r in rates_bps]
    if len(times) != len(rates):
        raise RfError(
            f"the epoch and rate histories must be the same length, got "
            f"{len(times)} and {len(rates)}"
        )
    if any(not math.isfinite(value) for value in times + rates):
        raise RfError("every epoch and rate must be finite")
    if any(rate < 0.0 for rate in rates):
        raise RfError("a data rate cannot be negative")
    if len(times) < 2:
        return 0.0
    if any(b <= a for a, b in pairwise(times)):
        raise RfError("the epoch history must be strictly increasing")

    total = 0.0
    for (t0, t1), (r0, r1) in zip(pairwise(times), pairwise(rates), strict=True):
        span = t1 - t0
        if method == "held_previous_sample":
            total += r0 * span
        elif method == "trapezoidal":
            total += 0.5 * (r0 + r1) * span
        else:
            total += min(r0, r1) * span
    return total
