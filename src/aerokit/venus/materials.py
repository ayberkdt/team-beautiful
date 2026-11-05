"""Materials against concentrated sulfuric acid in the Venus clouds (75–98 wt % H₂SO₄ droplets, −20…+90 °C).

Every row carries the evidence the research agent read (notes ``D_*``) and its tag. Choice logic [Y]: anything that
meets the cloud is either a fluoropolymer (FEP / PTFE / PFA) or covered by one; metals stay inside the sealed vessel
or under a fluoropolymer skin; bare 316L is acceptable only for cold, concentrated exposure.
"""
from __future__ import annotations

__all__ = ["MATERIALS", "selection"]

MATERIALS: tuple[dict, ...] = (
    {"material": "FEP film / fabric", "use": "solar-cell cover, blade wrap, arm sleeve, vessel skin",
     "evidence": "168 h in concentrated H2SO4 at 120 °C: 95 % tensile, 98 % elongation, 0.0 % weight gain",
     "source": "D_fep_chemical_resistance (manufacturer)", "tag": "D-ag", "verdict": "excellent"},
    {"material": "FEP/Kapton laminate with Ag mirror", "use": "JPL aerobot envelope (hybrid option); vessel skin",
     "evidence": "survived 96.2 % H2SO4 at 100 °C under 63 N tension; α 0.08, ε 0.52",
     "source": "D_jpl_aerobot_materials", "tag": "D-ag", "verdict": "excellent"},
    {"material": "Parylene coating on solar cells", "use": "solar deck",
     "evidence": "96 h in 96 % H2SO4: no corrosion, no power loss; coating costs 5 % of power",
     "source": "D_jpl_solar_acid_2022", "tag": "D-ag", "verdict": "good (−5 % power)"},
    {"material": "FEP / PP films in 75-85 % H2SO4", "use": "windows, covers",
     "evidence": "30 days: transmittance change within 2 %; PVC fails", "source": "D_havoc_2016_acid",
     "tag": "D-ag", "verdict": "good"},
    {"material": "Commercially pure titanium (bare)", "use": "vessel shell, hinges (only under FEP/PFA)",
     "evidence": "conc. acid room temp 1.57 mm/y; 75 % RT 10.8 mm/y; 96 % vapour 38-66 °C nil",
     "source": "D_timet_titanium_h2so4 (manufacturer)", "tag": "D-ag", "verdict": "only coated"},
    {"material": "316L-type stainless (bare)", "use": "fasteners inside the vessel",
     "evidence": "90-98 %: < 0.1 mm/y at ≤ 30 °C; > 1 mm/y at 80 °C and in 60-85 % acid",
     "source": "D_alleima_steel_h2so4 (manufacturer)", "tag": "D-ag", "verdict": "cold & concentrated only"},
    {"material": "CFRP / epoxy", "use": "blades, arms (structural core)",
     "evidence": "no primary data for concentrated acid found (only 10-40 % studies)", "source": "gap in D_00_index",
     "tag": "A", "verdict": "must be wrapped (FEP) — open test item"},
    {"material": "NdFeB SH magnets / Sm2Co17", "use": "motor magnets (sealed can)",
     "evidence": "SH 150 °C, Sm2Co17 ~300 °C max working temperature; both corrode in acid -> PFA-sealed can",
     "source": "D_eclipse_magnets (manufacturer)", "tag": "D-ag", "verdict": "sealed"},
)


def selection() -> dict[str, str]:
    """Component → material choice used in the baseline [Y]."""
    return {"blades": "CFRP spar/shell, FEP film wrap, PFA leading-edge strip",
            "arms": "CFRP tube in FEP heat-shrink sleeve; Ti hinges PFA-coated",
            "vessel": "Ti-6Al-4V shell, silvered-FEP outer skin, dry N2 fill",
            "motors": "outrunner in PFA-sealed can, Sm2Co17 magnets, PTFE shaft seal",
            "solar deck": "triple-junction cells, Parylene + FEP cover, CFRP frame",
            "sensors": "sapphire windows, PTFE inlets, gold-plated contacts"}
