"""Eco audit of one bracket in the structure of Ansys Granta EduPack's Eco Audit tool.

Phases (energy MJ and CO₂-eq kg each): material, manufacture, transport, use, end of life (EoL potential shown
separately, as EduPack does). Inputs are the part mass, the material record (:mod:`aerokit.bracket.matdata`) and a
route; every factor is a field of :class:`EcoInputs` with its source and tag, so the team can overwrite it with the
value the installed EduPack shows.

Factors and their status (details in docs/22):

* material: primary embodied energy and CO₂ per kg (Ashby 2013 via the reproduction, see matdata), multiplied by the
  bought mass = part mass × buy-to-fly ratio [Y];
* manufacture, AM: L-PBF specific electricity 31 kWh/kg (Baumers et al. 2010, SLM250, 316L) [D-ag] plus gas
  atomisation of the powder 7-32 MJ/kg (Kellens et al. 2017 Table 2; 20 MJ/kg used) [D-ag]; machining: plate rolling
  3-5 MJ/kg and 0.15-0.25 kg CO₂/kg (Ashby p. 133, ``eco.SHAPING``) [D] plus machining energy per kg removed [Y];
  electricity to CO₂ with ``grid_kgCO2_per_kWh`` [Y, NOT VERIFIED];
* transport: EduPack form ``m · d · e`` with a 32 t truck 0.94 MJ/(t km) and 0.072 kg CO₂/MJ (EduPack 2021 R1 help,
  search-snippet level) [S];
* use (mobile, EduPack form): ``m · L · e_mode`` with long-haul aircraft 6.5 MJ/(t km) and 0.072 kg CO₂/MJ [S] and a
  life distance L [Y]; the marginal alternative (Kellens et al. 2017 Table 8: 12.5 t kerosene per 100 kg per year,
  short-haul) × 3.16 kg CO₂/kg fuel (ICAO) is reported beside it [D-ag];
* end of life: recycling potential ``−m · f_recovered · (CO₂_primary − CO₂_recycled)`` [Y method, D values].
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from aerokit.bracket.matdata import Material
from aerokit.design.sustainability import CO2_PER_KG_FUEL
from aerokit.references import cite

__all__ = ["EcoInputs", "PhaseResult", "Audit", "audit", "compare"]

KWH = 3.6  # MJ per kWh


@dataclass
class EcoInputs:
    """Every assumption of the audit; tags D/D-ag/S/Y as in the module notes."""

    route: str = "am"                          # "am" (L-PBF) or "machined"
    buy_to_fly: float | None = None            # None → 1.3 for AM (supports, allowance) and 8 for machining [Y]
    am_kwh_per_kg: float = 31.0                # Baumers 2010 SLM250 316L [D-ag]
    atomisation_mj_per_kg: float = 20.0        # Kellens 2017 Table 2 range 7-32 MJ/kg [D-ag]
    rolling_mj_per_kg: float = 4.0             # Ashby p.133 rolling 3-5 MJ/kg [D]
    rolling_co2_per_kg: float = 0.2            # Ashby p.133 rolling 0.15-0.25 kg/kg [D]
    machining_mj_per_kg_removed: float = 5.0   # [Y] NOT VERIFIED
    grid_kgCO2_per_kWh: float = 0.30           # [Y] NOT VERIFIED (European-mix order of magnitude)
    transport_km: float = 1000.0               # [Y]
    transport_mj_per_tkm: float = 0.94         # EduPack 32 t truck [S]
    co2_per_mj_fuel: float = 0.072             # EduPack per-MJ fuel factor [S]
    use_mj_per_tkm: float = 6.5                # EduPack long-haul aircraft [S]
    life_km: float = 6.0e7                     # 25 y × 3000 h/y × 800 km/h [Y]
    marginal_fuel_kg_per_kg_year: float = 125.0   # Kellens 2017 Table 8 short haul: 12.5 t/(100 kg·y) [D-ag]
    life_years: float = 25.0                   # Kellens 2017 service life [D-ag]
    recovered_fraction: float = 0.9            # [Y]
    recycled_content: float = 0.0              # virgin feedstock (EduPack "Virgin (0 %)")
    sources: dict[str, str] = field(default_factory=lambda: {
        "am_kwh_per_kg": "Baumers et al. 2010, SFF Symp., Table 5 (SLM250, 316L: 31 kWh/kg) [D-ag]",
        "atomisation_mj_per_kg": "Kellens et al. 2017, Procedia CIRP 61:582, Table 2 (7.02-31.7 MJ/kg) [D-ag]",
        "rolling": "Ashby 2013 p.133 via reproduction (aerokit.materials.eco.SHAPING) [D]",
        "transport/use factors": "Granta EduPack 2021 R1 help, Eco Audit tables, search-snippet level "
                                 "(prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/edupack_eco_audit_factors.md) [S]",
        "marginal fuel": "Kellens et al. 2017 Table 8 (12.5 t kerosene/(100 kg·y), short haul, 25 y) [D-ag]",
        "CO2 per kg fuel": "ICAO CEC 3.16 kg/kg (aerokit.design.sustainability) [D]",
        "grid / machining / buy-to-fly / life km / recovery": "team assumptions [Y]"})

    def btf(self) -> float:
        if self.buy_to_fly is not None:
            return self.buy_to_fly
        return 1.3 if self.route == "am" else 8.0


@dataclass
class PhaseResult:
    energy_MJ: float
    co2_kg: float


@dataclass
class Audit:
    """Eco audit of one part."""

    label: str
    material_name: str
    mass_kg: float
    bought_kg: float
    phases: dict[str, PhaseResult]
    eol_potential: PhaseResult
    use_marginal_co2_kg: float
    inputs: dict[str, Any]

    @property
    def total(self) -> PhaseResult:
        return PhaseResult(sum(p.energy_MJ for p in self.phases.values()), sum(p.co2_kg for p in self.phases.values()))

    def table(self) -> list[dict[str, Any]]:
        rows = [{"phase": k, "energy_MJ": v.energy_MJ, "co2_kg": v.co2_kg} for k, v in self.phases.items()]
        t = self.total
        rows.append({"phase": "total", "energy_MJ": t.energy_MJ, "co2_kg": t.co2_kg})
        rows.append({"phase": "EoL potential", "energy_MJ": self.eol_potential.energy_MJ,
                     "co2_kg": self.eol_potential.co2_kg})
        return rows

    def to_json(self) -> dict[str, Any]:
        return {"label": self.label, "material": self.material_name, "mass_kg": self.mass_kg,
                "bought_kg": self.bought_kg, "phases": {k: asdict(v) for k, v in self.phases.items()},
                "total": asdict(self.total), "eol_potential": asdict(self.eol_potential),
                "use_marginal_co2_kg": self.use_marginal_co2_kg, "inputs": self.inputs}


@cite("ashby_2013_env", "baumers_2010", "kellens_2017", "icao_cec_2015",
      note="EduPack-structured eco audit; factor tags in EcoInputs")
def audit(mass_kg: float, m: Material, inp: EcoInputs | None = None, label: str = "") -> Audit:
    """Eco audit of a part of ``mass_kg`` made of ``m`` by ``inp.route``."""
    inp = inp or EcoInputs()
    if not mass_kg > 0:
        raise ValueError("mass must be positive")
    btf = inp.btf()
    bought = mass_kg * btf
    rc = inp.recycled_content
    co2_mat = (1 - rc) * m.co2.value + rc * (m.co2_recycled.value if m.co2_recycled else m.co2.value)
    e_mat = (1 - rc) * m.energy.value + rc * (m.energy_recycled.value if m.energy_recycled else m.energy.value)
    material = PhaseResult(bought * e_mat, bought * co2_mat)
    if inp.route == "am":
        e_elec = bought * inp.am_kwh_per_kg * KWH
        e_atom = bought * inp.atomisation_mj_per_kg
        manufacture = PhaseResult(e_elec + e_atom, (e_elec + e_atom) / KWH * inp.grid_kgCO2_per_kWh)
    elif inp.route == "machined":
        e_roll = bought * inp.rolling_mj_per_kg
        e_mach = (bought - mass_kg) * inp.machining_mj_per_kg_removed
        manufacture = PhaseResult(e_roll + e_mach,
                                  bought * inp.rolling_co2_per_kg + e_mach / KWH * inp.grid_kgCO2_per_kWh)
    else:
        raise ValueError("route must be 'am' or 'machined'")
    e_tr = mass_kg / 1000 * inp.transport_km * inp.transport_mj_per_tkm
    transport = PhaseResult(e_tr, e_tr * inp.co2_per_mj_fuel)
    e_use = mass_kg / 1000 * inp.life_km * inp.use_mj_per_tkm
    use = PhaseResult(e_use, e_use * inp.co2_per_mj_fuel)
    marginal = mass_kg * inp.marginal_fuel_kg_per_kg_year * inp.life_years * CO2_PER_KG_FUEL
    rec_co2 = m.co2_recycled.value if m.co2_recycled else m.co2.value
    rec_e = m.energy_recycled.value if m.energy_recycled else m.energy.value
    eol = PhaseResult(-mass_kg * inp.recovered_fraction * (m.energy.value - rec_e),
                      -mass_kg * inp.recovered_fraction * (m.co2.value - rec_co2))
    phases = {"material": material, "manufacture": manufacture, "transport": transport, "use": use,
              "end_of_life": PhaseResult(0.0, 0.0)}
    d = asdict(inp)
    d["buy_to_fly_used"] = btf
    return Audit(label or m.name, m.name, mass_kg, bought, phases, eol, marginal, d)


def compare(base: Audit, new: Audit) -> dict[str, Any]:
    """Phase-by-phase change new − base and the break-even flights for the production CO₂ difference."""
    out: dict[str, Any] = {"phases": {}}
    for k in base.phases:
        out["phases"][k] = {"base_co2_kg": base.phases[k].co2_kg, "new_co2_kg": new.phases[k].co2_kg,
                            "delta_co2_kg": new.phases[k].co2_kg - base.phases[k].co2_kg}
    out["total_base_co2_kg"] = base.total.co2_kg
    out["total_new_co2_kg"] = new.total.co2_kg
    out["delta_total_co2_kg"] = new.total.co2_kg - base.total.co2_kg
    prod_base = base.phases["material"].co2_kg + base.phases["manufacture"].co2_kg
    prod_new = new.phases["material"].co2_kg + new.phases["manufacture"].co2_kg
    use_rate_base = base.phases["use"].co2_kg / base.inputs["life_km"]
    use_rate_new = new.phases["use"].co2_kg / new.inputs["life_km"]
    saving_per_km = use_rate_base - use_rate_new
    out["extra_production_co2_kg"] = prod_new - prod_base
    out["break_even_km"] = (prod_new - prod_base) / saving_per_km if saving_per_km > 0 and prod_new > prod_base \
        else (0.0 if prod_new <= prod_base else float("inf"))
    out["mass_saving_kg"] = base.mass_kg - new.mass_kg
    out["delta_use_marginal_co2_kg"] = new.use_marginal_co2_kg - base.use_marginal_co2_kg
    return out
