"""Sustainability metrics of a sized design (judging criterion of the 2026 Regulations §1.4).

* block fuel and CO₂ of the design mission, fuel and CO₂ per passenger-km and per km² searched;
* a sustainable-aviation-fuel (SAF) blend scenario with a life-cycle reduction factor;
* a hybrid-electric loiter variant: the loiter segment flown on battery energy, giving the battery
  mass that replaces the loiter fuel;
* light-weighting: fuel and CO₂ saved over a service life by removing mass from the aircraft, an eco audit by
  life phase (production, manufacture, transport, use, end of life) and the payback of a material that is
  lighter but carbon-heavier to produce.

The CO₂ index 3.16 kg CO₂ per kg of jet fuel is the ICAO Carbon Emissions Calculator constant (Methodology
v8, May 2015) and the CORSIA value for Jet-A (UK CORSIA Order 2021, art. 28(5); 3.10 for AvGas and Jet-B), both
read on 2026-10-25. It is tank-to-wake combustion CO₂ only. SAF life-cycle reductions and battery specific
energies remain **parameters** that the user must choose and justify.
"""
from __future__ import annotations

from dataclasses import dataclass

from aerokit.references import cite

__all__ = ["CO2_PER_KG_FUEL", "CO2_PER_KG_AVGAS", "EmissionsSummary", "emissions", "saf_scenario", "HybridLoiter",
           "hybrid_loiter", "fuel_per_kg_carried", "Lightweighting", "lightweighting", "EcoAudit", "eco_audit",
           "payback_missions"]

CO2_PER_KG_FUEL = 3.16        # kg CO2 / kg Jet-A (ICAO CEC methodology v8; CORSIA Order 2021 art. 28(5))
CO2_PER_KG_AVGAS = 3.10       # kg CO2 / kg AvGas or Jet-B (CORSIA Order 2021 art. 28(5))


@dataclass(frozen=True)
class EmissionsSummary:
    """Fuel and CO₂ of one mission."""

    fuel_kg: float
    co2_kg: float
    fuel_per_pax_km: float | None
    co2_per_pax_km: float | None
    fuel_per_km2: float | None


@cite("icao_cec_2015", "uk_corsia_order_2021", note="CO2 index 3.16 kg/kg (tank-to-wake)")
def emissions(fuel_kg: float, passengers: float = 0.0, distance_km: float = 0.0, area_km2: float = 0.0,
              co2_index: float = CO2_PER_KG_FUEL) -> EmissionsSummary:
    """CO₂ and intensity metrics of a mission burning ``fuel_kg``.

    Raises
    ------
    ValueError
        Negative inputs or a non-positive CO₂ index.
    """
    if min(fuel_kg, passengers, distance_km, area_km2) < 0 or not co2_index > 0:
        raise ValueError("inputs must be >= 0 and the CO2 index > 0")
    co2 = fuel_kg * co2_index
    pkm = passengers * distance_km
    return EmissionsSummary(fuel_kg, co2, fuel_kg / pkm if pkm else None, co2 / pkm if pkm else None,
                            fuel_kg / area_km2 if area_km2 else None)


def saf_scenario(co2_kg: float, blend: float, lifecycle_reduction: float) -> float:
    """Life-cycle CO₂ [kg] with a SAF ``blend`` (0–1) whose life-cycle reduction is ``lifecycle_reduction`` (0–1)."""
    if not (0 <= blend <= 1 and 0 <= lifecycle_reduction <= 1) or co2_kg < 0:
        raise ValueError("blend and lifecycle_reduction must be in [0, 1], CO2 >= 0")
    return co2_kg * (1.0 - blend * lifecycle_reduction)


@dataclass(frozen=True)
class HybridLoiter:
    """Battery replacing the loiter fuel."""

    loiter_energy_J: float
    battery_mass_kg: float
    fuel_saved_kg: float
    mass_penalty_kg: float
    co2_saved_kg: float


def hybrid_loiter(loiter_power_W: float, loiter_time_s: float, fuel_saved_kg: float,
                  specific_energy_Wh_kg: float, chain_efficiency: float = 0.9, usable_fraction: float = 0.8,
                  co2_index: float = CO2_PER_KG_FUEL) -> HybridLoiter:
    """Battery mass that delivers ``loiter_power_W`` (shaft) for ``loiter_time_s``.

    ``m_bat = P t / (η_chain · f_usable · e_spec)``; the mass penalty is battery mass minus the loiter
    fuel it replaces (positive = heavier aircraft).
    """
    if min(loiter_power_W, loiter_time_s, fuel_saved_kg) < 0 or not specific_energy_Wh_kg > 0:
        raise ValueError("power, time, fuel must be >= 0 and specific energy > 0")
    if not (0 < chain_efficiency <= 1 and 0 < usable_fraction <= 1):
        raise ValueError("efficiencies must be in (0, 1]")
    E = loiter_power_W * loiter_time_s
    m = E / (chain_efficiency * usable_fraction * specific_energy_Wh_kg * 3600.0)
    return HybridLoiter(E, m, fuel_saved_kg, m - fuel_saved_kg, fuel_saved_kg * co2_index)


def fuel_per_kg_carried(fuel_fraction: float) -> float:
    """Extra mission fuel [kg] per kg of extra mass carried for the whole mission (Breguet, fixed range).

    Breguet (jet or propeller) at constant L/D, SFC (and speed or propeller efficiency) gives
    ``W_i / W_f = e^k`` with ``k`` fixed by the range. Mass ``Δm`` carried to the end raises ``W_f`` by ``Δm`` and
    ``W_i`` by ``Δm e^k``, so the fuel grows by ``Δm (e^k − 1)``. With the mission fuel fraction
    ``f = W_fuel / W_i = 1 − e^{−k}``: ``Δm_fuel / Δm = f / (1 − f)``. The same factor is the fuel *saved* per kg
    removed. Derived here; the effect of the mass on L/D (induced drag) is neglected, so it is a lower bound.

    Raises
    ------
    ValueError
        ``fuel_fraction`` outside [0, 1).
    """
    if not 0 <= fuel_fraction < 1:
        raise ValueError("fuel_fraction must be in [0, 1)")
    return fuel_fraction / (1.0 - fuel_fraction)


@dataclass(frozen=True)
class Lightweighting:
    """Fuel and CO₂ effect of removing mass from the aircraft."""

    mass_saved_kg: float
    fuel_per_mission_kg: float
    lifetime_fuel_kg: float
    lifetime_co2_kg: float


@cite("icao_cec_2015", note="CO2 index 3.16 kg/kg (tank-to-wake)")
def lightweighting(mass_saved_kg: float, fuel_fraction: float, missions: float,
                   co2_index: float = CO2_PER_KG_FUEL) -> Lightweighting:
    """Fuel and CO₂ saved over ``missions`` flights by removing ``mass_saved_kg`` (see :func:`fuel_per_kg_carried`).

    ``fuel_fraction`` is the design mission's fuel / take-off mass (``aerokit sizing design`` prints it).
    A negative ``mass_saved_kg`` (a heavier part) gives the extra fuel as negative savings.
    """
    if missions < 0 or not co2_index > 0:
        raise ValueError("missions must be >= 0 and the CO2 index > 0")
    per = mass_saved_kg * fuel_per_kg_carried(fuel_fraction)
    return Lightweighting(mass_saved_kg, per, per * missions, per * missions * co2_index)


@dataclass(frozen=True)
class EcoAudit:
    """CO₂ [kg] of one part by life phase (Granta EduPack Eco Audit phases)."""

    material: float
    manufacture: float
    transport: float
    use: float
    end_of_life: float

    @property
    def total(self) -> float:
        return self.material + self.manufacture + self.transport + self.use + self.end_of_life

    @property
    def dominant(self) -> str:
        phases = {"material": self.material, "manufacture": self.manufacture, "transport": self.transport,
                  "use": self.use, "end_of_life": self.end_of_life}
        return max(phases, key=lambda k: abs(phases[k]))

    def shares(self) -> dict[str, float]:
        """Fraction of the total per phase (end of life is negative when recycling credits it)."""
        t = self.total
        if t == 0:
            raise ValueError("total CO2 is zero")
        return {"material": self.material / t, "manufacture": self.manufacture / t, "transport": self.transport / t,
                "use": self.use / t, "end_of_life": self.end_of_life / t}


def eco_audit(part_mass_kg: float, material_co2_per_kg: float, manufacture_co2_per_kg: float = 0.0,
              transport_co2_kg: float = 0.0, use_co2_kg: float = 0.0, end_of_life_co2_per_kg: float = 0.0,
              buy_to_fly: float = 1.0) -> EcoAudit:
    """Eco audit of a part by phase; every factor is a parameter to take from EduPack or another stated source.

    ``buy_to_fly`` (≥ 1) is raw material mass / finished part mass: machining from plate is large, additive
    manufacturing near 1. Material and manufacture CO₂ scale with the bought mass; end of life (negative for a
    recycling credit) with the part mass. ``use_co2_kg`` is e.g. ``lightweighting(...).lifetime_co2_kg`` of the
    part's own mass (``lightweighting(-m, …)`` gives the burden as a negative saving: pass its absolute value).
    """
    if not part_mass_kg > 0 or buy_to_fly < 1 or min(material_co2_per_kg, manufacture_co2_per_kg,
                                                      transport_co2_kg, use_co2_kg) < 0:
        raise ValueError("part mass > 0, buy_to_fly >= 1 and the production/transport/use terms >= 0")
    bought = part_mass_kg * buy_to_fly
    return EcoAudit(bought * material_co2_per_kg, bought * manufacture_co2_per_kg, transport_co2_kg, use_co2_kg,
                    part_mass_kg * end_of_life_co2_per_kg)


def payback_missions(extra_production_co2_kg: float, co2_saved_per_mission_kg: float) -> float:
    """Flights after which a lighter but carbon-heavier option breaks even (``inf`` if it never saves).

    ``extra_production_co2_kg`` ≤ 0 means the lighter option is also cleaner to make: payback is 0.
    """
    if extra_production_co2_kg <= 0:
        return 0.0
    if co2_saved_per_mission_kg <= 0:
        return float("inf")
    return extra_production_co2_kg / co2_saved_per_mission_kg
