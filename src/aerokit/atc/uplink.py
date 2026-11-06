"""Ground-radar guidance sent to the aircraft as *data* (the "translate the radar signal to the display without a voice
in between" reading, research note R_mentor_roleplay_2026-11-04.md statement S4 [Y]).

A bit-exact message format with justified LSBs, CRC-24 integrity (the Mode S generator, ``modes.crc24``), and the
receiver rule "no message for ``timeout_s`` → GUIDANCE LOST, needles removed" (``guidance.GuidancePanel``).

What is *not* here: authentication (no cryptography; a spoofed uplink with a valid CRC is accepted — CRC is not
authentication), the transport (Mode S Comm-A, VDL Mode 2 or a dedicated link), and channel capacity under load.
Every field width and LSB below is our assumption [Y]; the case runner takes them from ``params.json``.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from aerokit.atc.modes import crc24

__all__ = ["Field", "DEFAULT_FORMAT", "pack", "unpack", "format_bits", "quantisation_errors",
           "p_no_long_gap", "nuisance_alarm_probability", "losses_for_alarm", "simulate_gaps"]


@dataclass(frozen=True)
class Field:
    name: str
    bits: int
    lsb: float = 1.0          # physical value of one count
    signed: bool = False

    @property
    def span(self) -> tuple[float, float]:
        if self.signed:
            return -(1 << (self.bits - 1)) * self.lsb, ((1 << (self.bits - 1)) - 1) * self.lsb
        return 0.0, ((1 << self.bits) - 1) * self.lsb


#: [Y] a 72-bit payload + 24-bit CRC = 96 bits
DEFAULT_FORMAT: tuple[Field, ...] = (
    Field("seq", 8),                              # message counter (wraps): detects lost/duplicated messages
    Field("t_meas_s", 16, 1 / 64),                # time of MEASUREMENT (not of transmission), mod 1024 s
    Field("range_m", 16, 1.0),                    # 0..65 km to touchdown
    Field("el_dev_m", 12, 0.1, signed=True),      # +-204.7 m above/below the glide path
    Field("az_dev_m", 12, 0.25, signed=True),     # +-511.75 m right/left of the centreline
    Field("valid", 1),                            # ground monitor says the measurement is usable
    Field("quality", 3),                          # integrity class 0-7 (meaning set by the ground system)
    Field("spare", 4),
)


def format_bits(fmt: Sequence[Field] = DEFAULT_FORMAT) -> int:
    """Payload bits + 24 CRC bits."""
    return sum(f.bits for f in fmt) + 24


def pack(values: dict[str, float], fmt: Sequence[Field] = DEFAULT_FORMAT) -> int:
    """Quantise and pack; raises ValueError for a value outside its field span (never clips silently)."""
    word = 0
    for f in fmt:
        v = float(values.get(f.name, 0.0))
        if f.name == "t_meas_s":
            v = v % (((1 << f.bits)) * f.lsb)
        q = int(round(v / f.lsb))
        lo, hi = (-(1 << (f.bits - 1)), (1 << (f.bits - 1)) - 1) if f.signed else (0, (1 << f.bits) - 1)
        if not lo <= q <= hi:
            raise ValueError(f"{f.name}={v} outside {f.span}")
        word = (word << f.bits) | (q & ((1 << f.bits) - 1))
    n = sum(f.bits for f in fmt)
    return (word << 24) | crc24(word << 24, n + 24)


def unpack(word: int, fmt: Sequence[Field] = DEFAULT_FORMAT) -> dict[str, float] | None:
    """Check the CRC and decode; ``None`` if the CRC fails (the message is discarded, nothing is displayed)."""
    n = sum(f.bits for f in fmt) + 24
    if crc24(word, n) != 0:
        return None
    payload = word >> 24
    out: dict[str, float] = {}
    for f in reversed(fmt):
        q = payload & ((1 << f.bits) - 1)
        payload >>= f.bits
        if f.signed and q >= 1 << (f.bits - 1):
            q -= 1 << f.bits
        out[f.name] = q * f.lsb
    return out


def quantisation_errors(fmt: Sequence[Field] = DEFAULT_FORMAT) -> dict[str, float]:
    """Worst-case rounding error per field (LSB / 2)."""
    return {f.name: f.lsb / 2 for f in fmt}


def losses_for_alarm(rate_hz: float, timeout_s: float) -> int:
    """Consecutive lost messages that make the gap between two received messages exceed ``timeout_s``
    (gap = (k + 1) / rate)."""
    return max(1, math.floor(timeout_s * rate_hz + 1e-9))      # smallest k with (k + 1) / rate > timeout


def p_no_long_gap(n: int, k: int, p_loss: float) -> float:
    """Probability that ``n`` independent messages (each lost with ``p_loss``) contain no run of >= ``k`` losses
    (exact dynamic programme over the current run length)."""
    if k <= 0:
        return 0.0
    state = np.zeros(k)
    state[0] = 1.0
    for _ in range(n):
        new = np.zeros(k)
        new[0] = state.sum() * (1 - p_loss)
        new[1:] = state[:-1] * p_loss
        state = new
    return float(state.sum())


def nuisance_alarm_probability(p_loss: float, rate_hz: float, timeout_s: float, duration_s: float) -> float:
    """P(at least one spurious 'GUIDANCE LOST' in one approach of ``duration_s``) for independent losses."""
    n = int(round(duration_s * rate_hz))
    return 1.0 - p_no_long_gap(n, losses_for_alarm(rate_hz, timeout_s), p_loss)


def simulate_gaps(p_loss: float, rate_hz: float, timeout_s: float, duration_s: float, runs: int,
                  seed: int = 0) -> float:
    """Monte Carlo check of :func:`nuisance_alarm_probability` (gap between received messages > timeout)."""
    rng = np.random.default_rng(seed)
    n = int(round(duration_s * rate_hz))
    hits = 0
    for _ in range(runs):
        rx = np.flatnonzero(rng.random(n) >= p_loss)
        times = np.concatenate(([-1.0 / rate_hz], rx / rate_hz, [n / rate_hz]))   # last known before start; end
        hits += bool(np.any(np.diff(times) > timeout_s + 1e-9))
    return hits / runs
