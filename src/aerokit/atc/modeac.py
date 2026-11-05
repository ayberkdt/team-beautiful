"""SSR Mode A/C: interrogation modes and the 1090 MHz reply pulse train.

A Mode A/C reply is two framing pulses F1, F2 20.3 us apart with up to 12 code pulses on a 1.45 us grid between
them (order C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4) and an optional SPI pulse 4.35 us after F2. The reply does
**not** say whether it is an identity (Mode A) or an altitude (Mode C): the interrogator knows only from which
P1-P3 spacing it sent (8 us = Mode A, 21 us = Mode C). That is the deepest form of "translate signal": the same
pulses mean a squawk or an altitude depending on context held by the ground station.

The decoder works on a list of pulse leading-edge times (what a video extractor delivers). It finds F1/F2 brackets,
reads the code positions with a tolerance, and flags **garble** (a second reply's pulses overlapping) and
**phantom** brackets (a code pulse pair 20.3 us apart that is not a real F1/F2) instead of guessing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Sequence

from aerokit.atc.modes import altcode_to_ft, gillham_encode, idcode_to_squawk, squawk_to_idcode
from aerokit.references import cite

__all__ = ["INTERROGATION_P1_P3_US", "F1_F2_US", "PULSE_STEP_US", "SPI_AFTER_F2_US", "CODE_ORDER", "ReplyFrame",
           "interrogation_mode", "encode_reply", "decode_pulses", "mode_c_altitude", "mode_a_code",
           "add_fruit"]

#: P1-P3 spacing [us] for each interrogation mode (Wikipedia "Secondary surveillance radar", read 2026-11-04)
INTERROGATION_P1_P3_US = {"A": 8.0, "B": 17.0, "C": 21.0, "D": 25.0}
F1_F2_US = 20.3
PULSE_STEP_US = 1.45
SPI_AFTER_F2_US = 4.35
CODE_ORDER = ("C1", "A1", "C2", "A2", "C4", "A4", "X", "B1", "D1", "B2", "D2", "B4", "D4")


@cite("wikipedia_ssr_2026", note="P1-P3 spacing 8 us (A), 17 us (B), 21 us (C), 25 us (D)")
def interrogation_mode(p1_p3_us: float, tol_us: float = 0.2) -> str | None:
    """Interrogation mode letter from the measured P1-P3 spacing, ``None`` if it matches none."""
    for mode, spacing in INTERROGATION_P1_P3_US.items():
        if abs(p1_p3_us - spacing) <= tol_us:
            return mode
    return None


@dataclass(frozen=True)
class ReplyFrame:
    """One decoded reply bracket."""

    t_f1_us: float
    code13: int                    # bits in CODE_ORDER, MSB = C1
    spi: bool
    garbled: bool                  # a pulse of another reply overlaps the code window
    phantom_risk: bool             # the bracket could be two code pulses of other replies
    notes: tuple[str, ...] = field(default=())


@cite("ssr_reply_format_patents", note="F1-F2 20.3 us, 1.45 us grid, SPI 4.35 us after F2, order C1 A1 ... D4")
def encode_reply(code13: int, t0_us: float = 0.0, spi: bool = False) -> list[float]:
    """Leading-edge times [us] of an ideal reply carrying ``code13`` (13 bits in :data:`CODE_ORDER`)."""
    if not 0 <= code13 < 1 << 13:
        raise ValueError("code is 13 bits")
    t = [t0_us]
    for k in range(13):
        if (code13 >> (12 - k)) & 1:
            t.append(t0_us + PULSE_STEP_US * (k + 1))
    t.append(t0_us + F1_F2_US)
    if spi:
        t.append(t0_us + F1_F2_US + SPI_AFTER_F2_US)
    return t


def _near(times: Sequence[float], target: float, tol: float) -> bool:
    return any(abs(t - target) <= tol for t in times)


def decode_pulses(times_us: Sequence[float], tol_us: float = 0.1) -> list[ReplyFrame]:
    """Find every F1/F2 bracket in a pulse list and read its code.

    Garble: any pulse inside the bracket that is *off* the 1.45 us grid of this bracket, or a second bracket that
    overlaps in time. Phantom risk: the F1 or F2 pulse also sits on the grid of another bracket.
    """
    ts = sorted(times_us)
    brackets: list[float] = []
    for t in ts:
        if _near(ts, t + F1_F2_US, tol_us):
            brackets.append(t)
    # a bracket whose F1 and F2 are both explained by an earlier bracket (its code grid, F2 or SPI) is a phantom
    def explained(t: float, b: float) -> bool:
        return _on_grid(t, b, tol_us) or abs(t - (b + F1_F2_US)) <= tol_us or \
            abs(t - (b + F1_F2_US + SPI_AFTER_F2_US)) <= tol_us
    phantoms = {b2 for b2 in brackets for b1 in brackets
                if b1 < b2 and explained(b2, b1) and explained(b2 + F1_F2_US, b1)}
    real = [b for b in brackets if b not in phantoms]
    frames: list[ReplyFrame] = []
    for t1 in real:
        code = 0
        notes: list[str] = []
        for k in range(13):
            code = (code << 1) | int(_near(ts, t1 + PULSE_STEP_US * (k + 1), tol_us))
        inside = [t for t in ts if t1 + tol_us < t < t1 + F1_F2_US - tol_us]
        off_grid = [t for t in inside
                    if abs((t - t1) / PULSE_STEP_US - round((t - t1) / PULSE_STEP_US)) * PULSE_STEP_US > tol_us]
        overlap = [b for b in real if b != t1 and abs(b - t1) < F1_F2_US + PULSE_STEP_US]
        garbled = bool(off_grid) or bool(overlap)
        if off_grid:
            notes.append(f"{len(off_grid)} pulse(s) off this reply's grid")
        if overlap:
            notes.append("another bracket overlaps (synchronous garble)")
        phantom = any(b != t1 and (_on_grid(t1, b, tol_us) or _on_grid(t1 + F1_F2_US, b, tol_us)) for b in real)
        if phantom:
            notes.append("F1/F2 coincide with code positions of another bracket")
        own_ph = [b for b in phantoms if t1 < b < t1 + F1_F2_US + SPI_AFTER_F2_US + tol_us]
        if own_ph:
            notes.append(f"{len(own_ph)} phantom bracket(s) formed by this reply's own pulses suppressed")
        spi = _near(ts, t1 + F1_F2_US + SPI_AFTER_F2_US, tol_us)
        if code & (1 << 6):               # X position
            notes.append("X pulse present (not used by civil transponders)")
        frames.append(ReplyFrame(t1, code, spi, garbled, phantom, tuple(notes)))
    return frames


def _on_grid(t: float, bracket_f1: float, tol: float) -> bool:
    k = (t - bracket_f1) / PULSE_STEP_US
    return 1 <= round(k) <= 13 and abs(k - round(k)) * PULSE_STEP_US <= tol


def mode_a_code(frame: ReplyFrame) -> str:
    """Squawk (4 octal digits) if the reply answered a Mode A interrogation."""
    return idcode_to_squawk(frame.code13 & ~(1 << 6))


@cite("wikipedia_ssr_2026", note="Mode C: 11 pulses, D1 unused, 100 ft increments")
def mode_c_altitude(frame: ReplyFrame) -> int | None:
    """Pressure altitude [ft] if the reply answered a Mode C interrogation (D1 and X ignored)."""
    code = frame.code13 & ~(1 << 6) & ~(1 << 4)     # clear X (-> M position) and D1 (-> Q position)
    return altcode_to_ft(code)


def reply_for_altitude(alt_ft: int, t0_us: float = 0.0) -> list[float]:
    """Mode C reply pulse times for a 100 ft multiple (Gillham)."""
    return encode_reply(gillham_encode(alt_ft), t0_us)


def reply_for_squawk(squawk: str, t0_us: float = 0.0, spi: bool = False) -> list[float]:
    """Mode A reply pulse times for a squawk."""
    return encode_reply(squawk_to_idcode(squawk), t0_us, spi)


def add_fruit(times_us: Sequence[float], rate_per_s: float, window_us: float, seed: int = 0) -> list[float]:
    """Add random FRUIT pulses (Poisson, ``rate_per_s`` replies per second, each a random 0-12 code pulses).

    A deliberately simple model for demonstrations: FRUIT replies are full random replies at random times.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    n = rng.poisson(rate_per_s * window_us * 1e-6)
    out = list(times_us)
    for _ in range(int(n)):
        t0 = float(rng.uniform(-F1_F2_US, window_us))
        out.extend(encode_reply(int(rng.integers(0, 1 << 13)) & ~(1 << 6), t0))
    return sorted(out)


__all__ += ["reply_for_altitude", "reply_for_squawk"]
