"""Navigation without GNSS in the Venus cloud layer — what can and cannot be measured (first-order numbers).

* **Altitude** from pressure: the probe-to-probe pressure spread at a given altitude maps into an altitude error
  through the local scale height (:func:`baro_altitude_error`). Relative altitude over minutes is far better.
* **Heading**: no magnetic field (VAPS 2018 via research note) [D-ag]; gyrocompassing needs the planet's rotation
  rate, which on Venus is 2.99e-7 rad/s — :func:`gyrocompass_ratio` compares it with a gyro bias [Y]: a
  navigation-grade gyro (0.01 °/h) gives a ratio of ~6, i.e. a heading error ≈ 1/6 rad ≈ 9° at the equator after
  long averaging (marginal); a tactical MEMS gyro (~1 °/h) gives 0.06 (impossible). Inside clouds a Sun fix better than 10° "may be impractical" (VAPS) [D-ag].
  Heading comes from the relay orbiter's radio direction / Doppler during passes and from the sun's diffuse
  brightness gradient (coarse) — assumption-level design choices.
* **Horizontal position**: the vehicle lives in the air-mass frame; its air-relative position comes from IMU +
  airspeed dead reckoning (Ingenuity drift 1–6 % of distance flown, note C_ingenuity_jpl [D-ag]). Its *ground*
  position integrates the unknown wind: error grows as σ_wind · t until an orbiter Doppler/range fix (VEGA balloons
  were tracked by Earth VLBI to ~15–24 km [D-ag]).
"""
from __future__ import annotations

import math

from aerokit import planetary as P
from aerokit.venus import atmosphere as A

__all__ = ["baro_altitude_error", "gyrocompass_ratio", "ground_position_error", "VENUS_ROTATION_RATE"]

VENUS_ROTATION_RATE = 2.0 * math.pi / P.VENUS_SIDEREAL_DAY_S      # rad/s


def baro_altitude_error(h: float) -> float:
    """Altitude error [m] if the reference profile is the probe mean and the true one is any probe (half-spread of
    pressure at ``h`` divided by ``dp/dh``)."""
    lo, hi = A.state(h, "min").p, A.state(h, "max").p
    mean = A.state(h).p
    dpdh = (A.state(h + 500.0).p - A.state(h - 500.0).p) / 1000.0
    return 0.5 * (hi - lo) / abs(dpdh) if mean > 0 else float("nan")


def gyrocompass_ratio(gyro_bias_deg_h: float = 0.01) -> float:
    """Planet rotation rate divided by the gyro bias (≫ 1 needed to find north; Earth gives ~1500 with 0.01 °/h)."""
    return VENUS_ROTATION_RATE / math.radians(gyro_bias_deg_h / 3600.0)


def ground_position_error(t_s: float, wind_sigma: float = 5.0, fix_sigma_m: float = 2e3) -> float:
    """1-σ ground-position error [m] a time ``t_s`` after the last orbiter fix: fix error ⊕ wind uncertainty × t."""
    return math.hypot(fix_sigma_m, wind_sigma * t_s)
