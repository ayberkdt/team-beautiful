"""ILS receiver in miniature: detected 90/150 Hz audio -> depth of modulation -> DDM -> needle, with a flag.

The localizer and glide-path carriers are amplitude-modulated by 90 Hz and 150 Hz tones; the receiver measures the
**difference in depth of modulation (DDM)**, which maps to an angle independent of range; on the centre line the
tones balance (Wikipedia "Instrument landing system", research note R_ils_wiki.md [D-ag]). This is the signal the
sponsor's SkyRF drones measure in flight inspection (S_intersoft_skyrf_brochure.md [D-ag]).

The safety point is the same as for voice: **a lost signal must never look like a good one.** A dead receiver with
balanced (zero) tones would put the needle in the centre -- "on course". So the needle is only driven when the carrier
and both tones are present with a plausible sum of modulation depths; otherwise the display shows the FLAG.

Conventions here (assumptions [Y], not read from Annex 10): DDM = m90 - m150; sum of depths nominal 0.40; full-scale
deflection at |DDM| = 0.155 (a commonly quoted value; the Wikipedia line giving 15.5 % is a hidden comment and was not
used as a source).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = ["ils_baseband", "tone_depth", "IlsReading", "read_ils"]


def ils_baseband(ddm: float, fs: int = 8000, duration_s: float = 0.5, sdm: float = 0.40, snr_db: float | None = 30.0,
                 carrier: float = 1.0, tones: tuple[bool, bool] = (True, True), seed: int = 0) -> np.ndarray:
    """Detected (envelope) audio of an ILS signal: carrier level + 90/150 Hz tones with depths giving ``ddm``.

    ``tones`` switches the 90 and 150 Hz components off to model a transmitter or receiver fault; ``carrier`` = 0 is
    no signal at all (only receiver noise remains).
    """
    rng = np.random.default_rng(seed)
    t = np.arange(int(fs * duration_s)) / fs
    m90, m150 = (sdm + ddm) / 2, (sdm - ddm) / 2
    x = carrier * (1.0 + (m90 * np.sin(2 * np.pi * 90 * t) if tones[0] else 0.0)
                   + (m150 * np.sin(2 * np.pi * 150 * t) if tones[1] else 0.0))
    if snr_db is not None:
        x = x + math.sqrt(0.5 * (0.2 ** 2) / 10 ** (snr_db / 10)) * rng.standard_normal(len(t))
    return np.asarray(x, float)


def tone_depth(x: np.ndarray, fs: int, f: float) -> float:
    """Amplitude of the ``f`` Hz component relative to the mean level (DC) -- a single-bin DFT (Goertzel-equivalent)."""
    t = np.arange(len(x)) / fs
    dc = float(np.mean(x))
    if abs(dc) < 1e-6:
        return 0.0
    c = 2.0 / len(x) * np.abs(np.sum((x - dc) * np.exp(-2j * np.pi * f * t)))
    return float(c / dc)


@dataclass(frozen=True)
class IlsReading:
    ddm: float | None
    sdm: float
    m90: float
    m150: float
    dots: float | None            # needle position, +-2 dots at full scale; None when flagged
    flag: bool
    reason: str


def read_ils(x: np.ndarray, fs: int, full_scale_ddm: float = 0.155, carrier_min: float = 0.2,
             sdm_range: tuple[float, float] = (0.3, 0.5), tone_min: float = 0.02) -> IlsReading:
    """Receiver logic: measure, validate, then (only then) drive the needle."""
    level = float(np.mean(x))
    m90, m150 = tone_depth(x, fs, 90.0), tone_depth(x, fs, 150.0)
    sdm = m90 + m150
    if level < carrier_min:
        return IlsReading(None, sdm, m90, m150, None, True, "no carrier")
    if m90 < tone_min or m150 < tone_min:
        return IlsReading(None, sdm, m90, m150, None, True, "90 or 150 Hz tone missing")
    if not sdm_range[0] <= sdm <= sdm_range[1]:
        return IlsReading(None, sdm, m90, m150, None, True, f"sum of modulation depths {sdm:.2f} out of range")
    ddm = m90 - m150
    dots = float(np.clip(ddm / full_scale_ddm, -1, 1) * 2.0)
    return IlsReading(ddm, sdm, m90, m150, dots, False, "valid")
