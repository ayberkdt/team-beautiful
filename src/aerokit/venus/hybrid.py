"""Alternative architecture (needs mentor approval — the brief says *rotorcraft*): VESPER-H, the same hexacopter
carrying a superpressure helium cell that floats most or all of its weight at the cruise altitude.

Why it matters: the pure rotorcraft cannot survive the ~3-Earth-day air-mass night (hover power ~2 kW against a
~1 kWh battery). A neutrally buoyant cell turns the rotors into an altitude/position *excursion* system and the night
into a 25 W "sleep" — mission length then set by helium leakage and acid ageing (weeks–months), not by energy.

Sizing (fixed-point on total floated mass, spherical envelope):
``V = m g / ((ρ_atm − ρ_He) g)``, envelope mass = areal density × sphere area. Areal density: VEGA heritage
12.5 kg for a 3.4–3.54 m sphere (TM-88516 via research note A_vega1985 [D-ag]) → ~0.32–0.34 kg/m² [K]; a modern
laminate is assumed at 0.20 kg/m² [Y]. Helium storage for in-air inflation: tank mass ≈ 8 × helium mass [Y]
(jettisoned after inflation; VEGA: 121 kg balloon system to float 21 kg [D-ag]).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from aerokit import planetary as P
from aerokit.venus import atmosphere as A

__all__ = ["HybridSizing", "size_hybrid", "VEGA_ENVELOPE_AREAL"]

VEGA_ENVELOPE_AREAL = 12.5 / (math.pi * 3.47 ** 2)      # kg/m², VEGA 12.5 kg envelope, ~3.4-3.54 m sphere [K]


@dataclass(frozen=True)
class HybridSizing:
    buoyant_fraction: float
    vehicle_kg: float
    envelope_kg: float
    helium_kg: float
    tank_kg: float
    volume_m3: float
    diameter_m: float
    floated_kg: float
    rotor_weight_share_N: float
    night_energy_Wh: float
    extra_battery_kg: float


def size_hybrid(vehicle_kg: float, buoyant_fraction: float = 1.0, h: float = 55e3, areal_kg_m2: float = 0.20,
                sleep_W: float = 25.0, night_h: float = 78.0, battery_Wh_per_kg: float = 155.0,
                tank_ratio: float = 8.0) -> HybridSizing:
    """Cell that floats ``buoyant_fraction`` of the total (vehicle + envelope + night battery) at altitude ``h``."""
    if not 0.0 < buoyant_fraction <= 1.2 or vehicle_kg <= 0:
        raise ValueError("buoyant fraction in (0, 1.2] and vehicle mass > 0")
    s = A.state(h)
    rho_he = s.p * P.M_HE / (P.R_UNIVERSAL * s.T)
    lift = s.rho - rho_he                                   # kg of mass floated per m³
    night_Wh = sleep_W * night_h
    extra_batt = night_Wh / battery_Wh_per_kg
    m_env = 0.0
    for _ in range(200):
        total = vehicle_kg + extra_batt + m_env
        V = buoyant_fraction * total / lift
        r = (3.0 * V / (4.0 * math.pi)) ** (1.0 / 3.0)
        new_env = areal_kg_m2 * 4.0 * math.pi * r * r
        if abs(new_env - m_env) < 1e-6:
            break
        m_env = new_env
    total = vehicle_kg + extra_batt + m_env
    he = rho_he * V
    return HybridSizing(buoyant_fraction, vehicle_kg, m_env, he, tank_ratio * he, V, 2 * r, total,
                        (1.0 - buoyant_fraction) * total * s.g, night_Wh, extra_batt)
