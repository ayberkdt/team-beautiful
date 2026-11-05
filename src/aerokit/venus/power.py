"""Power sources in the Venus cloud layer: bifacial solar array, Li-ion battery, and the air-mass day cycle.

**Solar array (front face).** Absolute level from Landis & Haag (2013, Table 1, read by the research agent): a
triple-junction array of 29 % AM0 efficiency at overhead sun delivers 112 / 181 / 256 / 404 / 559 W/m² at
40 / 45 / 50 / 55 / 60 km (their spectrum from Venera-11 transmission, cell at ambient temperature). Between nodes
the logarithm is interpolated; above 60 km the shape of the Pioneer Venus LSFR downward flux (COMBINED channel,
:func:`aerokit.venus.atmosphere.solar_down_relative`) scales the 60-km value up to 64 km [K].

Cross-check [K]: Landis–Haag 55→60 km ratio 0.72; LSFR downward-flux ratio 0.76 — independent data agree to 5 %.

**Rear face (bifacial).** The upward (cloud-reflected) flux is 0.84–0.89 of the downward flux at 50–62 km
(LSFR, :func:`aerokit.venus.atmosphere.solar_ratio_up_down`), so the rear collects ``ratio × bifaciality ×`` the
front. Bifaciality 0.85 is an assumption [Y].

**Sun elevation.** Inside an optically thick, conservatively scattering cloud the downward diffuse flux is close to
the Eddington two-stream transmission, ∝ ``μ₀ (μ₀ + 2/3)`` (μ₀ = cos of the solar zenith angle) — a textbook
approximation, *not verified against Venus data in this session* [Y]. Normalised to 1 at μ₀ = 1.
Consistency check with the probe [K]: the LSFR COMBINED downward flux at 55 km (302.6 W/m² in 0.41–1.78 µm at
μ₀ = 0.412) rescaled with this law to overhead sun is ~1.1×10³ W/m² in-band; Landis–Haag's overhead 55 km array
output (404 W/m² at 29 %) implies ~1.4×10³ W/m² total — the same order, the in-band share explains most of the gap.

**Acid protection.** A Parylene coat costs 5 % of power (JPL 2022 coupon test, research note) [D-ag].

**Air-mass day.** A platform drifting with the zonal wind ``u`` sees the Sun move at ``u + Ω_sun (R + h)`` where
``Ω_sun = 2π / 116.75 d`` (the ground's solar day; the super-rotation is in the same sense as the planet's
rotation). At 55 km and 65 m/s the air-mass day is ~6.5 Earth days: ~3.2 days of light, ~3.2 days of night.

**Battery.** Li-ion 18650-class energy cells: 243 Wh/kg cell (Panasonic NCR18650B datasheet), charge 0–45 °C,
discharge −20–60 °C (research note D_panasonic_ncr18650b, manufacturer data) [D-ag]; pack integration factor and
usable depth of discharge are assumptions [Y]. Ingenuity's Sony VTC4 pack: 163 Wh/kg, flights only at +10…+25 °C
[D-ag].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from aerokit import planetary as P
from aerokit.references import cite
from aerokit.venus import atmosphere as A

__all__ = ["LANDIS_HAAG_TABLE1", "array_output_overhead", "sun_factor", "SolarArray", "Battery",
           "air_mass_day_s", "mu0_history", "LI_ION_NCR18650B", "LI_ION_VTC4"]

# (altitude km, array output W/m² at overhead sun, 29 % AM0 triple junction) — Landis & Haag 2013 Table 1 [D-ag]
LANDIS_HAAG_TABLE1: tuple[tuple[float, float], ...] = ((40.0, 112.2), (45.0, 181.4), (50.0, 256.0), (55.0, 404.4),
                                                      (60.0, 559.2))
LANDIS_HAAG_EFFICIENCY = 0.29


@cite("landis_haag_2013_solar", "tomasko_1980_solar_flux",
      note="Table 1 nodes 40-60 km, log interpolation; LSFR downward-flux shape above 60 km")
def array_output_overhead(h: float, array_efficiency: float = LANDIS_HAAG_EFFICIENCY) -> float:
    """Front-face electrical output [W/m²] of a horizontal array at overhead sun, scaled linearly from the 29 %
    reference to ``array_efficiency`` (a first-order scaling; spectral mismatch ignored)."""
    km = h / 1e3
    if not 40.0 <= km <= 64.0:
        raise ValueError("solar model covers 40-64 km")
    xs = [a for a, _ in LANDIS_HAAG_TABLE1]
    ys = [math.log(b) for _, b in LANDIS_HAAG_TABLE1]
    if km <= 60.0:
        base = math.exp(float(np.interp(km, xs, ys)))
    else:
        base = LANDIS_HAAG_TABLE1[-1][1] * A.solar_down_relative(h) / A.solar_down_relative(60e3)
    return base * array_efficiency / LANDIS_HAAG_EFFICIENCY


def sun_factor(mu0: float) -> float:
    """In-cloud downward flux relative to overhead sun, Eddington-like ``μ₀ (μ₀ + 2/3) / (5/3)`` [Y]."""
    if mu0 <= 0:
        return 0.0
    mu0 = min(mu0, 1.0)
    return mu0 * (mu0 + 2.0 / 3.0) / (5.0 / 3.0)


@dataclass(frozen=True)
class SolarArray:
    area_m2: float
    efficiency: float = 0.29
    bifaciality: float = 0.85          # rear/front response [Y]
    coating_loss: float = 0.05         # Parylene acid coat (JPL coupon test) [D-ag]
    areal_mass_kg_m2: float = 0.9      # thin cells + FEP + CFRP frame [Y]
    rear_exposed: float = 1.0          # fraction of the rear not shadowed by the vehicle [Y]

    def power(self, h: float, mu0: float) -> float:
        """Electrical output [W] at altitude ``h`` and cos(solar zenith) ``mu0``."""
        front = array_output_overhead(h, self.efficiency) * sun_factor(mu0)
        rear = front * A.solar_ratio_up_down(h) * self.bifaciality * self.rear_exposed
        return (front + rear) * self.area_m2 * (1.0 - self.coating_loss)

    @property
    def mass(self) -> float:
        return self.area_m2 * self.areal_mass_kg_m2


@dataclass(frozen=True)
class Battery:
    """Li-ion pack. ``specific_energy`` at cell level [Wh/kg]; pack mass = cells / ``pack_factor``."""

    name: str
    cell_specific_energy: float
    pack_factor: float = 0.75          # cells / pack mass (structure, BMS, heaters) [Y]
    usable_dod: float = 0.85           # [Y]
    charge_C: tuple[float, float] = (0.0, 45.0)
    discharge_C: tuple[float, float] = (-20.0, 60.0)
    max_C_rate: float = 2.0

    def usable_Wh_per_kg(self) -> float:
        return self.cell_specific_energy * self.pack_factor * self.usable_dod

    def mass_for(self, usable_Wh: float) -> float:
        return usable_Wh / self.usable_Wh_per_kg()

    def can_charge(self, T_C: float) -> bool:
        return self.charge_C[0] <= T_C <= self.charge_C[1]

    def can_discharge(self, T_C: float) -> bool:
        return self.discharge_C[0] <= T_C <= self.discharge_C[1]


LI_ION_NCR18650B = Battery("Li-ion NCR18650B-class (energy cell)", 243.0)      # datasheet values [D-ag]
LI_ION_VTC4 = Battery("Li-ion VTC4 (Ingenuity power cell)", 163.0, charge_C=(-5.0, 25.0),
                      discharge_C=(10.0, 25.0), max_C_rate=10.0)                  # Ingenuity limits [D-ag]


@cite("wikipedia_venus_2026", note="solar day 116.75 d; drift speed is an input")
def air_mass_day_s(wind_west: float, h: float) -> float:
    """Length [s] of one day–night cycle for a platform drifting with ``wind_west`` [m/s] at the equator."""
    if wind_west < 0:
        raise ValueError("wind must be >= 0 (westward)")
    omega = 2.0 * math.pi / P.VENUS_SOLAR_DAY_S + wind_west / (P.VENUS_RADIUS + h)
    return 2.0 * math.pi / omega


def mu0_history(t: np.ndarray, wind_west: float, h: float, latitude_deg: float = 0.0,
                start_hour_angle_deg: float = -90.0) -> np.ndarray:
    """cos(solar zenith) along a drift (sub-solar declination ~0 for Venus' 177° obliquity [Y]); hour angle −90° =
    dawn terminator."""
    period = air_mass_day_s(wind_west, h)
    H = np.radians(start_hour_angle_deg) + 2.0 * np.pi * np.asarray(t) / period
    return np.cos(np.radians(latitude_deg)) * np.cos(H)
