"""Thermophysical properties of the Venus atmosphere gas (96.5 % CO₂ + 3.5 % N₂ by volume) for rotor aerodynamics.

* **Heat capacity** — NIST-JANAF Shomate fits (Chase 1998, via the NIST WebBook, read 2026-11-04 [D]) mixed by mole
  fraction (ideal gas). The CO₂ fit is valid from 298 K; below it the NIST fluid table (1 bar) is used for CO₂.
* **Speed of sound** — ideal gas ``a = √(γ R T / M)`` with the mixture γ. Pure CO₂ agrees with the NIST real-fluid
  value within 0.3 % at 0.5–1 bar (tested).
* **Viscosity, conductivity** — NIST fluid tables for CO₂ at 1 bar, 225–400 K (pressure effect < 0.1 % down to
  0.5 bar), interpolated linearly; outside the table a Sutherland-type power law fitted to its ends extrapolates.
  N₂ is neglected (≈3.5 % by volume; effect on μ estimated < 1 % [Y]).

All in SI. Reference: ``04_Venus/research/K_nist_co2_properties.md``.
"""
from __future__ import annotations

import math

import numpy as np

from aerokit.references import cite

__all__ = ["X_CO2", "X_N2", "M_MIX", "R_SPECIFIC", "cp_molar", "gamma", "speed_of_sound", "viscosity",
           "conductivity", "NIST_CO2_1BAR", "reynolds", "kinematic_viscosity"]

R_UNIVERSAL = 8.314462618
M_CO2 = 44.0095e-3
M_N2 = 28.0134e-3
X_CO2 = 0.965
X_N2 = 0.035
M_MIX = X_CO2 * M_CO2 + X_N2 * M_N2
R_SPECIFIC = R_UNIVERSAL / M_MIX

_SHOMATE_CO2 = (24.99735, 55.18696, -33.69137, 7.948387, -0.136638)      # 298-1200 K
_SHOMATE_CO2_HI = (58.16639, 2.720074, -0.492289, 0.038844, -6.447293)    # 1200-6000 K
_SHOMATE_N2 = (28.98641, 1.853978, -9.647459, 16.63537, 0.000117)         # 100-500 K
_SHOMATE_N2_MID = (19.50583, 19.88705, -8.598535, 1.369784, 0.527601)     # 500-2000 K

# T [K], Cp [J/mol K], a [m/s], mu [Pa s], k [W/m K] — CO2 at 0.1 MPa, NIST WebBook fluid tables (Lemmon et al.)
NIST_CO2_1BAR: tuple[tuple[float, float, float, float, float], ...] = (
    (225.0, 34.511, 235.93, 11.353e-6, 0.011302), (250.0, 35.428, 247.79, 12.581e-6, 0.013051),
    (275.0, 36.462, 258.89, 13.799e-6, 0.014881), (300.0, 37.520, 269.39, 15.003e-6, 0.016774),
    (325.0, 38.561, 279.42, 16.191e-6, 0.018714), (350.0, 39.566, 289.04, 17.359e-6, 0.020691),
    (375.0, 40.528, 298.31, 18.508e-6, 0.022695), (400.0, 41.446, 307.28, 19.635e-6, 0.024718),
)
_NT = np.array([r[0] for r in NIST_CO2_1BAR])
_NCP = np.array([r[1] for r in NIST_CO2_1BAR])
_NMU = np.array([r[3] for r in NIST_CO2_1BAR])
_NK = np.array([r[4] for r in NIST_CO2_1BAR])


def _shomate(c: tuple[float, ...], T: float) -> float:
    t = T / 1000.0
    return c[0] + c[1] * t + c[2] * t * t + c[3] * t ** 3 + c[4] / (t * t)


def _check_T(T: float) -> None:
    if not (math.isfinite(T) and 100.0 <= T <= 3000.0):
        raise ValueError(f"temperature {T} K outside 100-3000 K")


@cite("nist_webbook_co2_2026", note="Shomate Cp (Chase 1998); NIST 1-bar fluid table below 298 K")
def cp_molar(T: float) -> float:
    """Ideal-gas molar heat capacity of the Venus mixture [J/(mol K)]."""
    _check_T(T)
    if T < 298.0:
        cp_co2 = float(np.interp(T, _NT, _NCP))        # real fluid at 1 bar (≈ ideal within 0.5 %)
    elif T <= 1200.0:
        cp_co2 = _shomate(_SHOMATE_CO2, T)
    else:
        cp_co2 = _shomate(_SHOMATE_CO2_HI, T)
    cp_n2 = _shomate(_SHOMATE_N2 if T <= 500.0 else _SHOMATE_N2_MID, T)
    return X_CO2 * cp_co2 + X_N2 * cp_n2


def gamma(T: float) -> float:
    """Ratio of specific heats of the ideal-gas mixture."""
    cp = cp_molar(T)
    return cp / (cp - R_UNIVERSAL)


def speed_of_sound(T: float) -> float:
    """Speed of sound [m/s], ideal gas ``√(γ R T / M)``."""
    return math.sqrt(gamma(T) * R_SPECIFIC * T)


def _table_or_power(T: float, col: np.ndarray) -> float:
    _check_T(T)
    if _NT[0] <= T <= _NT[-1]:
        return float(np.interp(T, _NT, col))
    # power law through the two nearest table ends
    i, j = (0, 1) if T < _NT[0] else (-2, -1)
    n = math.log(col[j] / col[i]) / math.log(_NT[j] / _NT[i])
    k = j if T > _NT[-1] else i
    return float(col[k] * (T / _NT[k]) ** n)


@cite("nist_webbook_co2_2026", note="CO2 viscosity at 0.1 MPa, 225-400 K; power law outside")
def viscosity(T: float) -> float:
    """Dynamic viscosity [Pa s] (CO₂)."""
    return _table_or_power(T, _NMU)


@cite("nist_webbook_co2_2026", note="CO2 thermal conductivity at 0.1 MPa, 225-400 K; power law outside")
def conductivity(T: float) -> float:
    """Thermal conductivity [W/(m K)] (CO₂)."""
    return _table_or_power(T, _NK)


def kinematic_viscosity(T: float, rho: float) -> float:
    """ν = μ/ρ [m²/s]."""
    if rho <= 0:
        raise ValueError("density must be > 0")
    return viscosity(T) / rho


def reynolds(speed: float, length: float, T: float, rho: float) -> float:
    """Reynolds number ``ρ V L / μ``."""
    if speed < 0 or length <= 0:
        raise ValueError("speed >= 0 and length > 0")
    return rho * speed * length / viscosity(T)
