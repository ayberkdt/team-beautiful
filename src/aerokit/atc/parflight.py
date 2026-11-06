"""Approach flight model for the PAR cue: real speeds, Dryden turbulence, wind that grows with height, a human pilot.

Sources are read in ``03_Advionics/research/R5_real_data_and_models.md`` and ``R2_par_deep_research.md``:

* Dryden low-altitude form (MIL-F-8785C through the MathWorks reference): sigma_w = 0.1 W20,
  sigma_u = sigma_v = sigma_w / (0.177 + 0.000823 h)^0.4, L_w = h, L_u = L_v = h / (0.177 + 0.000823 h)^1.2, h in ft.
* Wind shear: W(h) = W20 ln(h / z0) / ln(20 / z0), z0 = 0.15 ft in terminal phases. Light turbulence: W20 = 15 kt.
* Threshold speeds (Eurocontrol, indicative): A320 137 kt, C-130H 130 kt, F-16 150 kt.
* A PAR pilot turns at once to the exact heading given and holds it; half-standard rate 1.5 deg/s on final.
* The pilot corrects height from the information alone, by small changes: about 1 deg of pitch or less.
* Glide-slope loop crossover 0.25-0.45 rad/s with 0.6-1 s delay on a clean ILS needle (NASA CR-2019). PAR needle noise
  is larger, so the low end of the band is the default [Y].

The reaction time on a PAR call has no source (R2 section 8). 2 s is the EGPWS response peak (R4), used by analogy [Y].
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

__all__ = ["AIRCRAFT", "Aircraft", "Atmosphere", "PilotModel", "wind_at", "dryden_sigmas"]

KT = 0.514444
FT = 0.3048


@dataclass(frozen=True)
class Aircraft:
    name: str
    vat_kt: float
    response_s: float = 4.0           # [Y] heading and flight-path lag, R5 assumes 3-5 s, varied in the sweep


AIRCRAFT = {"C-130H": Aircraft("C-130H", 130.0), "A320": Aircraft("A320", 137.0), "F-16": Aircraft("F-16", 150.0)}


def wind_at(height_m: float, w20_ms: float, z0_ft: float = 0.15) -> float:
    """Log-law wind speed at a height, from the speed at 20 ft."""
    h_ft = max(height_m / FT, 2.0 * z0_ft)
    return w20_ms * math.log(h_ft / z0_ft) / math.log(20.0 / z0_ft)


def dryden_sigmas(height_m: float, w20_kt: float) -> tuple[float, float, float, float]:
    """(sigma_u, sigma_w [m/s], L_u, L_w [m]) in the low-altitude form, height limited to 10-1000 ft."""
    h = min(max(height_m / FT, 10.0), 1000.0)
    s_w = 0.1 * w20_kt * KT
    k = 0.177 + 0.000823 * h
    return s_w / k ** 0.4, s_w, (h / k ** 1.2) * FT, h * FT


@dataclass
class Atmosphere:
    """Steady wind by height plus Dryden gusts (first-order form, one state per axis)."""

    headwind_w20_ms: float = 0.0
    crosswind_w20_ms: float = 0.0     # + pushes the aircraft right
    turbulence_w20_kt: float = 15.0   # light; 30 moderate, 45 severe
    rng: np.random.Generator = field(default_factory=np.random.default_rng)

    def __post_init__(self) -> None:
        self.gu = self.gv = self.gw = 0.0

    def step(self, height_m: float, speed_ms: float, dt: float) -> tuple[float, float, float]:
        """(headwind, crosswind, updraught) in m/s at this step."""
        s_u, s_w, l_u, l_w = dryden_sigmas(height_m, self.turbulence_w20_kt)

        def nxt(g: float, s: float, length: float) -> float:
            a = min(speed_ms * dt / length, 1.0)
            return (1.0 - a) * g + math.sqrt(2.0 * a) * s * float(self.rng.standard_normal())

        self.gu, self.gv, self.gw = nxt(self.gu, s_u, l_u), nxt(self.gv, s_u, l_u), nxt(self.gw, s_w, l_w)
        return (wind_at(height_m, self.headwind_w20_ms) + self.gu, wind_at(height_m, self.crosswind_w20_ms) + self.gv,
                self.gw)


@dataclass(frozen=True)
class PilotModel:
    reaction_s: float = 2.0           # [Y] by analogy; no PAR source
    turn_rate_dps: float = 1.5        # half-standard rate on final
    follows_cue: bool = True          # False: keeps heading and descent, the no-cue baseline
    heading_error_deg: float = 0.0    # holds the target with this constant error
    vertical_wc: float = 0.25         # rad/s, low end of the sourced 0.25-0.45 glide-slope band
    max_pitch_change_deg: float = 1.0  # about 1 deg of pitch or less
    go_around_climb_ms: float = 5.0   # [Y]
