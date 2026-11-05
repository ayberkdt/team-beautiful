"""Write the study files of this folder from one base definition (rerun after changing an input).

    python studies/tradeoff/build_studies.py

Base: A320 bracket, strength-limited. Variants change only the index case or the life-cycle block.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AL_CO2 = {"value": 12.0, "low": 4.5, "high": 22.0, "unit": "kg CO2 / kg", "tag": "D",
          "group": "primary_al",
          "source": "Ashby 2013 aluminium family 12 (Useful Numbers PDF p. 1, read 2026-11-01); range 4.5-22 = IAI "
                    "'most footprints' (sub-agent fetch 2026-11-01); powder atomisation not added (ORNL: +2.4 % "
                    "energy for Ti powder)"}
SCAL_CO2 = {"value": 128.0, "low": 68.0, "high": 128.0, "unit": "kg CO2 / kg", "tag": "H",
            "source": "0.35 kg AlSc2% master alloy per kg (Sc 0.7 wt%, Mehta et al. 2022 Metals 12:57 Table 2, read "
                      "2026-11-01) x 172 kg CO2e/kg AlSc2% (Hengevoss et al. 2024 Cleaner Waste Systems 7:100129 "
                      "Table 1, novel bauxite-residue route, read 2026-11-01) + 0.65 kg Al x 12 = 68 (low); the same "
                      "paper puts the novel route at about half the state-of-the-art Sc2O3 GWP -> Sc share x2 = 128 "
                      "(value, current supply)"}

BASE = json.loads((HERE / "bracket_a320_strength.json").read_text(encoding="utf-8"))
BASE["materials"]["AlSi10Mg"] = {
    "E": 72e9, "Fty": 220e6, "rho": 2670,
    "properties_source": "EOS AlSi10Mg M290 datasheet 12.2017, stress-relieved 270 C/90 min: Rp0.2 220 (XY) / 225 (Z) "
                         "MPa, 2670 kg/m3 (sub-agent full PDF 2026-11-01); E = 72 +- 3 GPa XY as-built (AddUp "
                         "AlSi10Mg datasheet 2023, read 2026-11-01; 77 +- 4 after 210 C/2 h)",
    "co2_per_kg": AL_CO2}
BASE["materials"]["Scalmalloy"] = {
    "E": 69e9, "Fty": 490e6, "rho": 2670,
    "properties_source": "3D Systems Scalmalloy datasheet, stress-relieved 325 C/4 h: Rp0.2 490-500 MPa; density "
                         "2670 kg/m3 from the APWORKS sheet (sub-agent full PDF 2026-11-01); E = 69 GPa horizontal "
                         "after 325 C/4 h (Colibrium Additive M2 Series 5 Al-Mg-Sc datasheet 2025-08-21 RevB, ASTM "
                         "E8, read 2026-11-01; 70 GPa as-built); yield 319 MPa at 150 C and 60 MPa at 300 C (same "
                         "sheet)",
    "co2_per_kg": SCAL_CO2}
COST_SRC = "research_notes/Hafifletme derin araştırma 2/cost_data.md (sub-agent 2026-11-01; EUR at ECB 16 Sep 2026)"


def _f(value, low, high, tag, source, group=""):
    d = {"value": value, "low": low, "high": high, "unit": "EUR/kg", "tag": tag, "source": source}
    if group:
        d["group"] = group
    return d


AL_PLATE = _f(10, 7.5, 20, "Y", "aerospace Al plate: low 7.5 = Constellium A&T FY2024 revenue/volume (fetch); "
                                "value and high = assumed distributor premium; " + COST_SRC, "al_plate")
AL_MACHINING = _f(100, 40, 240, "S", "CNC Al route per kg finished at buy-to-fly ~10, template on Walker 2013 removal "
                                     "rates and snippet shop rates; " + COST_SRC, "cnc_al")
LPBF_AL_ROUTE = _f(500, 220, 1910, "A", "L-PBF route excluding powder: AMPOWER ~298 EUR/kg Al to Simpson 2021 "
                                        "EOS M290; " + COST_SRC, "lpbf_al")
COSTS = {
    "7075-T6": {"machined": {"price_per_kg": AL_PLATE, "route_cost_per_kg": AL_MACHINING},
                "machined_TO": {"price_per_kg": AL_PLATE, "route_cost_per_kg": AL_MACHINING}},
    "2024-T351": {"machined_TO": {"price_per_kg": AL_PLATE, "route_cost_per_kg": AL_MACHINING}},
    "Ti-6Al-4V": {
        "machined_TO": {"price_per_kg": _f(50, 29, 96, "A", "Ti-6Al-4V sheet 15-50 USD/lb, Dutta & Froes 2014 slide 3; "
                                                           + COST_SRC),
                        "route_cost_per_kg": _f(300, 120, 620, "S",
                                                "CNC Ti route per kg finished, template; " + COST_SRC)},
        "am_TO": {"price_per_kg": _f(110, 71, 180, "A", "Ti-6Al-4V EBM powder 45-106 um, Fraunhofer IAPT 2021 Fig. 13; "
                                                       + COST_SRC),
                  "route_cost_per_kg": _f(500, 250, 855, "A", "EBM/L-PBF Ti route excluding powder; " + COST_SRC)}},
    "AlSi10Mg": {"am_TO": {"price_per_kg": _f(80, 40, 126, "A", "AlSi10Mg powder: Depboylu et al. SFF 2024 p. 1 "
                                                               "(135-145 USD/kg standard, ~85 NExP-1); " + COST_SRC),
                           "route_cost_per_kg": LPBF_AL_ROUTE}},
    "Scalmalloy": {"am_TO": {"price_per_kg": _f(200, 120, 400, "Y", "Scalmalloy powder: no published price found, "
                                                                     "placeholder; " + COST_SRC),
                             "route_cost_per_kg": LPBF_AL_ROUTE}},
}
for _m, _c in COSTS.items():
    BASE["materials"][_m]["cost_by_route"] = _c

BASE["options"] = [
    {"material": "7075-T6", "route": "machined"},
    {"material": "7075-T6", "route": "machined_TO"},
    {"material": "2024-T351", "route": "machined_TO"},
    {"material": "Ti-6Al-4V", "route": "machined_TO"},
    {"material": "Ti-6Al-4V", "route": "am_TO"},
    {"material": "AlSi10Mg", "route": "am_TO"},
    {"material": "Scalmalloy", "route": "am_TO"},
]


def variant(name: str, case: str | None = None, lifecycle: dict | None = None) -> dict:
    d = copy.deepcopy(BASE)
    d["name"] = name
    if case:
        d["case"] = case
    if lifecycle:
        d["lifecycle"].update(lifecycle)
    return d


STUDIES = {
    "bracket_a320_strength": variant(BASE["name"]),
    "bracket_a320_stiffness": variant(
        "A320 cabin/system bracket, stiffness-limited (per kg of the conventional 7075-T6 machined part)",
        "beam_stiff"),
    "bracket_atr72_strength": variant(
        "ATR 72-600 bracket, strength-limited (per kg of the conventional 7075-T6 machined part)", lifecycle={
            "fuel_per_kg_per_flight": {
                "value": 0.028, "low": 0.022, "high": 0.033, "unit": "kg fuel / kg carried / flight", "tag": "A",
                "source": "ATR 72-600 factsheet 2020 p. 2 (MTOW 22,800 kg; 200/300 NM block fuel 638/879 kg) -> "
                          "marginal 0.04-0.06 kg/kg/1000 km (sub-agent arithmetic) x 555.6 km (300 NM sector)"},
            "flights": {"value": 50000, "low": 30000, "high": 70000, "unit": "flights over life", "tag": "Y",
                        "source": "assumption: regional turboprop, short sectors; no primary life figure read"}}),
    "bracket_satellite_strength": variant(
        "Satellite bracket, strength-limited, production only (per kg of the conventional 7075-T6 machined part)",
        lifecycle={
            "fuel_per_kg_per_flight": {"value": 0.0, "unit": "kg fuel / kg carried / flight", "tag": "Y",
                                       "source": "no use-phase fuel: launch emissions per kg not modelled; mass "
                                                 "enters through launch cost (exchange constant) instead"},
            "flights": {"value": 1, "unit": "-", "tag": "Y", "source": "single mission"}}),
}
# Satellite: production CO2 alone ranks the options; mass is valued through launch cost (Ashby 2000, Table 3, space
# vehicle 3000-10,000 per kg, read 2026-11-01; currency symbol garbled in the text layer, read as GBP) and CO2 through
# the EU ETS price (2025 average of the Dec-2025 EUA contract EUR 74.31/t, Montel via GMK Center, read 2026-11-01).
# Mixing GBP and EUR is accepted at this order-of-magnitude level and stated in the report.
SAT_PENALTY = dict(STUDIES["bracket_satellite_strength"], name=(
    "Satellite bracket, strength-limited, penalty Z = 3000 x mass + 0.0743 x CO2 (per kg of the conventional part)"),
    exchange={"mass_kg": 3000.0, "co2_total_kg": 0.0743},
    exchange_unit="currency (Ashby 2000 space-vehicle exchange constant, low end; EU ETS 2025 average)")
STUDIES["bracket_satellite_penalty"] = SAT_PENALTY
# A320 with cost: Z [EUR] = cost + alpha * mass + carbon price * CO2. alpha = 500 EUR/kg (Ashby 2000 civil aircraft
# 100-500 GBP/kg, upper end; bottom-up life value of a kg 120-2100 EUR/kg in cost_data.md), carbon EU ETS 2025.
A320_COST = dict(STUDIES["bracket_a320_strength"], name=(
    "A320 bracket, strength-limited, penalty Z = cost + 500 x mass + 0.0743 x CO2 (EUR, per kg conventional part)"),
    objectives=["mass_kg", "co2_total_kg", "cost"],
    exchange={"cost": 1.0, "mass_kg": 500.0, "co2_total_kg": 0.0743},
    exchange_unit="EUR (material + route cost, mass valued at 500 EUR/kg, CO2 at the EU ETS 2025 average)")
STUDIES["bracket_a320_cost"] = A320_COST

# ---------------------------------------------------------------------------------------------------------------
# Area B (docs/11): material substitution for a cabin panel, stiffness-limited, no topology optimisation.
# Numbers from research_notes/Üç sapma alanı/B_malzeme_dongusellik.md (sub-agent, read 2026-11-01/02; tags as there).
# ---------------------------------------------------------------------------------------------------------------
BNOTE = "research_notes/Üç sapma alanı/B_malzeme_dongusellik.md"


def _c(value, low, high, tag, source, unit="kg CO2 / kg", group=""):
    d = {"value": value, "low": low, "high": high, "unit": unit, "tag": tag, "source": source}
    if group:
        d["group"] = group
    return d


# carbon fibre: JCMA LCI 2022 19.85 (low) - Ashby/EduPack 33 via compilation (value) - Meng 2017 coal grid 68 (high);
# ecoinvent 81.6 left out as a 4x outlier (B notes §2). Epoxy 5.70 (ICE v2.0 p5). Fibre mass fractions [H] from the
# datasheet Vf and densities: IM7/8552 Vf 57.7 %, rho 1.57, resin 1.301 -> fibre 1.77 -> w_f 0.65; CF/PEEK 5HS Vf 50 %
# rho 1.53 -> w_f 0.58 (fibre 1.77 assumed). PEEK 7.5-13 is a weak web value (B notes §2, tag S).
CF = (33.0, 19.85, 68.0)
PANEL_CFRP_CO2 = _c(round(0.65 * CF[0] + 0.35 * 5.70, 1), round(0.65 * CF[1] + 0.35 * 5.70, 1),
                    round(0.65 * CF[2] + 0.35 * 5.70, 1), "H",
                    f"0.65 x carbon fibre (19.85-33-68) + 0.35 x epoxy 5.70; {BNOTE} §2", group="carbon_fibre")
PANEL_PEEK_CO2 = _c(round(0.58 * CF[0] + 0.42 * 10.0, 1), round(0.58 * CF[1] + 0.42 * 7.5, 1),
                    round(0.58 * CF[2] + 0.42 * 13.0, 1), "H",
                    f"0.58 x carbon fibre (19.85-33-68) + 0.42 x PEEK 7.5-13 (weak web value); {BNOTE} §2",
                    group="carbon_fibre")
AL_PANEL_CO2 = _c(12.79, 6.6, 15.1, "D", f"ICE v2.0 p1 primary Al 12.79 CO2e; EU-made 6.6 (European Aluminium EPR "
                                         f"2024 p5); global 15.1 (IAI factsheet 2022); {BNOTE} §2", group="primary_al")
# End-of-life potential per kg of part [H, own formula; Granta's is not public]: f_rec x (primary - recycled).
# f_rec 0.85-0.94: PAMELA up to 85 % recyclable, Tarmac Aerosave 92-94 % of mass recovered; recycled Al 1.81 (ICE).
AL_EOL = _c(round(0.92 * (12.79 - 1.81), 2), round(0.85 * (6.6 - 1.81), 2), round(0.94 * (15.1 - 1.81), 2), "H",
            f"f_rec x (primary - recycled 1.81 ICE); f_rec 0.85-0.94 (PAMELA, Airbus 2022); own formula; {BNOTE} §3",
            group="primary_al")
CF_EOL = _c(0.0, 0.0, 23.0, "S", "Granta Eco Design WP p12: continuous-fibre composites 'cannot be re-separated "
                                 "economically' (value 0); Meng 2018 net recycling benefit 19-27 kg CO2e per kg CFRP "
                                 f"(abstract) as the high end; {BNOTE} §3")
PANEL = {
    "name": "A320 cabin panel, stiffness-limited, monolithic plate (per 3 kg of the 2024-T3 reference panel)",
    "case": "panel_stiff",
    "reference_material": "2024-T3",
    "reference_mass": {"value": 3.0, "low": 2.0, "high": 5.0, "unit": "kg", "tag": "Y",
                       "source": "assumed panel mass; results scale with it"},
    "lifecycle": copy.deepcopy(BASE["lifecycle"]),
    "materials": {
        "2024-T3": {"E": 73.1e9, "Fty": 345e6, "rho": 2780, "co2_per_kg": AL_PANEL_CO2,
                    "eol_credit_per_kg": AL_EOL, "flags": ["fst_cabin"],
                    "properties_source": f"AA typical via aerospacemetals.com 2023 [S]; metal panels pass the "
                                         f"cabin fire tests (non-combustible) [Y]; {BNOTE} §1b"},
        "Al-Li 2050-T84": {"E": 76.5e9, "Fty": 476e6, "rho": 2700,
                           "co2_per_kg": dict(AL_PANEL_CO2, tag="Y", source="Al-Li footprint NOT FOUND; aluminium "
                                              "values used (ICE / EA / IAI)"),
                           "eol_credit_per_kg": dict(AL_EOL, tag="Y"), "flags": ["fst_cabin"],
                           "properties_source": f"Smiths HP distributor sheet 2025 (same E printed for 2198) [S]; "
                                                f"{BNOTE} §1b"},
        "CFRP QI IM7/8552": {"E": 57.8e9, "Fty": 722e6, "rho": 1570, "co2_per_kg": PANEL_CFRP_CO2,
                             "eol_credit_per_kg": CF_EOL,
                             "properties_source": f"NCAMP NCP-RP-2009-028 Rev B Tables 5-1/5-2, [25/50/25] RTD [D]; "
                                                  f"rho 1.57 Hexcel 8552 EU PDS p2 [D]; epoxy panels need FR or "
                                                  f"phenolic for OSU 65/65 [S]; {BNOTE} §1a, §4"},
        "Glass/phenolic 7781": {"E": 22.0e9, "Fty": 450e6, "rho": 1830,
                                "co2_per_kg": _c(8.10, 7.47, 8.26, "D", f"GFRP: ICE v2.0 p4 8.10 [D]; Ashby 2013 "
                                                                       f"7.47-8.26 via compilation [S]; {BNOTE} §2"),
                                "flags": ["fst_cabin"],
                                "properties_source": f"stiffness of 7781 glass on HexPly 913 epoxy as a proxy "
                                                     f"(phenolic 260 sheet gives fire data only) [D]; HexPly 260/7781 "
                                                     f"on Nomex OSU 44/44 [D]; {BNOTE} §1a, §4"},
        "Flax/epoxy": {"E": 11.7e9, "Fty": 120e6, "rho": 1300,
                       "co2_per_kg": _c(3.66, 3.4, 4.0, "H", f"0.51 x flax 1.70 + 0.49 x epoxy 5.70 (ICE v2.0 p4-5); "
                                                            f"{BNOTE} §2"),
                       "properties_source": f"QI estimated as 1/3 of the UD FlaxPreg values E1 35 GPa, 365 MPa [Y]; "
                                            f"rho 1.3 theoretical [D]; fails OSU peak heat release even with FR "
                                            f"(Thulo et al. 2025) [S]; {BNOTE} §1a, §4"},
        "CF/PEEK 5HS": {"E": 40.8e9, "Fty": 578e6, "rho": 1530, "co2_per_kg": PANEL_PEEK_CO2,
                        "eol_credit_per_kg": dict(CF_EOL, tag="Y", source="thermoplastic, remeltable; same range as "
                                                  "CFRP, no source for a higher value"),
                        "properties_source": f"Toray Cetex TC1200 PDS v4.0 p3 'plain tensile' (lay-up not printed, "
                                             f"QI likely) and p2 density [D]; {BNOTE} §1a"},
    },
    "routes": {
        "sheet_formed": {"buy_to_fly": {"value": 1.3, "low": 1.1, "high": 1.6, "unit": "-", "tag": "Y",
                                        "source": "assumed sheet trim and nesting loss"},
                         "process_MJ_per_kg": {"value": 4.0, "low": 3.0, "high": 5.0, "unit": "MJ/kg", "tag": "S",
                                               "source": "rolling 3-5 MJ/kg, Ashby 2013 p. 133 via the compilation"},
                         "mass_factor": {"value": 1.0, "unit": "-", "tag": "Y", "source": "no topology"}},
        "autoclave_layup": {"buy_to_fly": {"value": 1.3, "low": 1.1, "high": 1.5, "unit": "-", "tag": "Y",
                                           "source": "assumed prepreg cutting scrap"},
                            "process_MJ_per_kg": {"value": 200.0, "low": 100.0, "high": 300.0, "unit": "MJ/kg",
                                                  "tag": "S", "source": "autoclave moulding 100-300 MJ/kg, Ashby "
                                                                        "2013 p. 133 via the compilation"},
                            "mass_factor": {"value": 1.0, "unit": "-", "tag": "Y", "source": "no topology"}},
        "thermoplastic_press": {"buy_to_fly": {"value": 1.2, "low": 1.1, "high": 1.4, "unit": "-", "tag": "Y",
                                               "source": "assumed blank trim"},
                                "process_MJ_per_kg": {"value": 13.5, "low": 11.0, "high": 16.0, "unit": "MJ/kg",
                                                      "tag": "S", "source": "compression moulding 11-16 MJ/kg, Ashby "
                                                                            "2013 p. 133 via the compilation"},
                                "mass_factor": {"value": 1.0, "unit": "-", "tag": "Y", "source": "no topology"}},
    },
    "options": [{"material": "2024-T3", "route": "sheet_formed"},
                {"material": "Al-Li 2050-T84", "route": "sheet_formed"},
                {"material": "CFRP QI IM7/8552", "route": "autoclave_layup"},
                {"material": "Glass/phenolic 7781", "route": "autoclave_layup"},
                {"material": "Flax/epoxy", "route": "autoclave_layup"},
                {"material": "CF/PEEK 5HS", "route": "thermoplastic_press"}],
    "objectives": ["mass_kg", "co2_total_kg"],
}
STUDIES["panel_cabin_stiffness"] = PANEL
STUDIES["panel_cabin_fst"] = dict(copy.deepcopy(PANEL), name=(
    "A320 cabin panel, stiffness-limited, only materials that pass the cabin fire tests (OSU 65/65, 14 CFR 25.853)"),
    constraints={"require": ["fst_cabin"]})
STUDIES["panel_cabin_eol"] = dict(copy.deepcopy(PANEL), name=(
    "A320 cabin panel, stiffness-limited, ranked with the end-of-life potential counted (sensitivity only)"),
    objectives=["mass_kg", "co2_total_with_eol_kg"], exchange={"co2_total_with_eol_kg": 1.0},
    exchange_unit="kg CO2 including the end-of-life potential")

# ---------------------------------------------------------------------------------------------------------------
# Area C (docs/11): hot bracket. Separate study so that the A320 Monte Carlo draw order stays as it is.
# Numbers from research_notes/Üç sapma alanı/C_isil_enerji.md (sub-agent, read 2026-11-02; tags as there).
# ---------------------------------------------------------------------------------------------------------------
CNOTE = "research_notes/Üç sapma alanı/C_isil_enerji.md"
HOT = copy.deepcopy(BASE)
HOT["name"] = "Hot-zone bracket, strength-limited, A320 life cycle (per kg of the conventional 7075-T6 machined part)"
HOT["materials"]["2618-T61"] = {
    "E": 73.8e9, "Fty": 324e6, "rho": 2768, "co2_per_kg": AL_CO2,
    "properties_source": f"MMPDS-01 Table 3.2.13.0(c) p 3-211, hand forging < 2 in, S-basis L [D]; {CNOTE} §1a"}
HOT["materials"]["Inconel 718"] = {
    "E": 200e9, "Fty": 1145e6, "rho": 8150,
    "co2_per_kg": {"value": 11.6, "low": 11.6, "high": 25.0, "unit": "kg CO2 / kg", "tag": "Y",
                   "source": "nickel superalloy family 11.6 (Ashby 2013 p. 483 via the compilation, aerokit.materials."
                             "eco) as the low end; high end 25 assumed for the Nb/Mo content and powder atomisation"},
    "properties_source": f"EOS IN718 L-PBF, AMS 2774/5662 heat treatment, Rp0.2 1145 (V) MPa, rho >= 8150 [D]; E 200 "
                         f"GPa Special Metals SMC-045 Table 4 [D]; {CNOTE} §1b"}
HOT["options"] = BASE["options"] + [{"material": "2618-T61", "route": "machined_TO"},
                                    {"material": "Inconel 718", "route": "am_TO"}]
STUDIES["bracket_hot_strength"] = HOT

if __name__ == "__main__":
    for stem, d in STUDIES.items():
        (HERE / f"{stem}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {stem}.json ({len(d['options'])} options, case {d['case']})")
