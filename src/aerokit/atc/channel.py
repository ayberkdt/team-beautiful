"""Synthetic VHF voice channel: audio degradation, receiver-side measurements and a word-level ASR error model.

Two levels, both deterministic for a given seed:

* **Audio** (:func:`degrade_audio`): add white noise at a set SNR, hard clipping, dropouts (fades / blocked
  transmissions) and squelch (carrier absent -> the receiver outputs silence). :func:`measure_audio` then estimates
  what an on-board monitor can actually know: speech activity, SNR, clipping and dropout fractions.
* **Words** (:func:`degrade_words`): a transcript is corrupted the way a recogniser fails -- confusable words are
  substituted, words deleted -- and every word gets a confidence. A tunable share of errors are *confidently
  wrong*, because real recognisers are not perfectly calibrated. The parameters are our assumptions [Y], chosen to
  exercise the safety logic; they are not fitted to published ATC recognition results.
"""
from __future__ import annotations

import math
import os
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from aerokit.atc.clearance import Word, tokenize

__all__ = ["vhf_voice_band", "read_wav", "write_wav", "degrade_audio", "AudioMeasure", "measure_audio", "CONFUSIONS", "WordChannel", "degrade_words",
           "tone_speech"]


def tone_speech(duration_s: float, fs: int = 8000, seed: int = 0, syllable_hz: float = 4.0) -> np.ndarray:
    """A speech-like test signal: harmonic tones with a ~4 Hz syllabic envelope (for tests without TTS)."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(duration_s * fs)) / fs
    f0 = 120 + 20 * np.sin(2 * np.pi * 0.7 * t)
    phase = 2 * np.pi * np.cumsum(f0) / fs
    sig = sum(np.sin(k * phase) / k for k in range(1, 8))
    env = np.clip(np.sin(2 * np.pi * syllable_hz * t + rng.uniform(0, 6.28)), 0, None) ** 0.5
    x = sig * env
    return 0.5 * x / np.max(np.abs(x))


def vhf_voice_band(x: np.ndarray, fs: int, lo_hz: float = 300.0, hi_hz: float = 3400.0) -> np.ndarray:
    """Band-limit audio to the telephone-like voice band of an AM air-band receiver (4th-order Butterworth).

    The 300-3400 Hz limits are our assumption [Y] for a demonstration, not a value read from Annex 10.
    """
    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, [lo_hz, min(hi_hz, 0.45 * fs)], btype="band", fs=fs, output="sos")
    return sosfiltfilt(sos, np.asarray(x, float))


def read_wav(path: str | os.PathLike) -> tuple[np.ndarray, int]:
    """Mono float audio in [-1, 1] and the sample rate."""
    from scipy.io import wavfile
    fs, y = wavfile.read(str(path))
    y = y.astype(float)
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y / 32768.0, int(fs)


def write_wav(path: str | os.PathLike, y: np.ndarray, fs: int) -> None:
    """16-bit PCM WAV (clipped to [-1, 1])."""
    from scipy.io import wavfile
    wavfile.write(str(path), fs, (np.clip(y, -1, 1) * 32767).astype(np.int16))


def degrade_audio(x: np.ndarray, fs: int, snr_db: float | None = 20.0, clip: float | None = None,
                  dropouts: Sequence[tuple[float, float]] = (), carrier: bool = True, seed: int = 0,
                  noise_floor: float = 1e-3) -> np.ndarray:
    """Return the audio a receiver would output.

    ``snr_db`` is relative to the mean power of the active (non-silent) part of ``x``. ``clip`` limits |y|.
    ``dropouts`` are (start, end) times [s] set to receiver noise only. With ``carrier=False`` the squelch stays
    closed and the output is near-silence -- there is no speech to recognise at all.
    """
    rng = np.random.default_rng(seed)
    if not carrier:
        return noise_floor * rng.standard_normal(len(x))
    y = np.asarray(x, float).copy()
    active = np.abs(y) > 0.02 * np.max(np.abs(y)) if np.any(y) else np.ones_like(y, bool)
    p_sig = float(np.mean(y[active] ** 2)) if np.any(active) else 0.0
    if snr_db is not None and p_sig > 0:
        y = y + math.sqrt(p_sig / 10 ** (snr_db / 10)) * rng.standard_normal(len(y))
    for t0, t1 in dropouts:
        a, b = max(0, int(t0 * fs)), min(len(y), int(t1 * fs))
        y[a:b] = noise_floor * rng.standard_normal(b - a)
    if clip is not None:
        y = np.clip(y, -clip, clip)
    return y


@dataclass(frozen=True)
class AudioMeasure:
    """What the on-board monitor can estimate from the received audio alone."""

    speech_fraction: float       # share of 20 ms frames classed as active
    snr_est_db: float | None     # active-frame power over quiet-frame power (None if no quiet frames)
    clip_fraction: float         # samples at the rail
    dropout_fraction: float      # active-region frames that are near-silent (inside the transmission)
    level_rms: float


def measure_audio(y: np.ndarray, fs: int, frame_s: float = 0.02) -> AudioMeasure:
    """Frame-energy speech-activity detector and SNR / clipping / dropout estimate (simple, explainable)."""
    n = max(1, int(frame_s * fs))
    m = len(y) // n
    if m == 0:
        return AudioMeasure(0.0, None, 0.0, 0.0, 0.0)
    fr = y[: m * n].reshape(m, n)
    e = np.mean(fr ** 2, axis=1) + 1e-20
    edb = 10 * np.log10(e)
    lo_db = np.percentile(edb, 10)
    hi_db = np.percentile(edb, 90)
    thr = lo_db + 0.5 * (hi_db - lo_db) if hi_db - lo_db > 6 else hi_db + 1
    act = edb > thr
    quiet = ~act
    snr = float(10 * np.log10(np.mean(e[act]) / np.mean(e[quiet]))) if act.any() and quiet.any() else None
    peak = np.max(np.abs(y)) if len(y) else 0.0
    clip_frac = float(np.mean(np.abs(y) >= 0.999 * peak)) if peak > 0 else 0.0
    # dropout = frames far below the channel's own noise level (carrier fade / squelch closed mid-transmission);
    # ordinary speech pauses still carry channel noise and are not counted
    if act.any() and quiet.any():
        first, last = np.argmax(act), len(act) - 1 - np.argmax(act[::-1])
        inside = edb[first:last + 1]
        noise_ref = float(np.median(edb[quiet]))
        dead = float(np.mean(inside < noise_ref - 6.0)) if len(inside) else 0.0
    else:
        dead = 0.0
    return AudioMeasure(float(np.mean(act)), snr, clip_frac, dead, float(np.sqrt(np.mean(y ** 2))))


#: confusable words (acoustic or homophone) used by the word-level error model
CONFUSIONS: dict[str, tuple[str, ...]] = {
    "zero": ("two", "oh"), "one": ("nine", "wun"), "two": ("to", "zero", "three"), "three": ("tree", "two"),
    "four": ("for", "five"), "five": ("nine", "four", "fife"), "six": ("seven",), "seven": ("six", "eleven"),
    "eight": ("ate", "eighty"), "nine": ("five", "one"), "niner": ("nine",), "to": ("two",), "for": ("four",),
    "left": ("right",), "right": ("left",), "climb": ("descend",), "descend": ("climb",),
    "thousand": ("hundred",), "hundred": ("thousand",), "heading": ("leading",),
}


@dataclass(frozen=True)
class WordChannel:
    """Word-level recogniser error model. Error rate falls logistically with SNR [Y]."""

    wer_floor: float = 0.03        # error rate at high SNR
    wer_ceiling: float = 0.6       # error rate at very low SNR
    snr_mid_db: float = 8.0        # SNR where the error rate is half-way
    snr_width_db: float = 3.0
    p_delete: float = 0.25         # share of errors that are deletions (the rest substitutions)
    p_confident_error: float = 0.15  # share of errors that still get a high confidence (miscalibration)
    conf_scale_floor: float = 0.02   # correct-word confidence = 1 - Exp(scale); scale at high SNR
    conf_scale_span: float = 0.3     # extra scale at low SNR

    def error_rate(self, snr_db: float) -> float:
        return self.wer_floor + (self.wer_ceiling - self.wer_floor) / (1 + math.exp((snr_db - self.snr_mid_db)
                                                                                     / self.snr_width_db))


def degrade_words(text: str | Sequence[Word], snr_db: float, channel: WordChannel = WordChannel(),
                  seed: int = 0) -> list[Word]:
    """Corrupt a transcript at ``snr_db`` and assign per-word confidences."""
    rng = np.random.default_rng(seed)
    p_err = channel.error_rate(snr_db)
    out: list[Word] = []
    for w in tokenize(text):
        if rng.random() < p_err:
            if rng.random() < channel.p_delete:
                continue
            alts = CONFUSIONS.get(w.text)
            sub = alts[int(rng.integers(len(alts)))] if alts else w.text
            if sub == w.text:          # nothing confusable: the word survives but with low confidence
                out.append(Word(w.text, float(rng.uniform(0.3, 0.7))))
                continue
            conf = float(rng.uniform(0.86, 0.97)) if rng.random() < channel.p_confident_error else \
                float(rng.uniform(0.15, 0.6))
            out.append(Word(sub, conf))
        else:
            # correct word: confidence 1 - Exp(scale), scale growing as SNR falls [Y]
            # (30 dB: P(conf < 0.85) ~ 1e-3; 10 dB: ~0.4; 0 dB: ~0.6)
            scale = channel.conf_scale_floor + channel.conf_scale_span / (1 + math.exp((snr_db - channel.snr_mid_db
                                                                                         - 2) / channel.snr_width_db))
            out.append(Word(w.text, float(max(0.05, 1.0 - rng.exponential(scale)))))
    return out
