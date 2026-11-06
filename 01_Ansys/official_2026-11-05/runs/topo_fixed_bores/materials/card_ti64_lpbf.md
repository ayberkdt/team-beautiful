# Material card — Ti-6Al-4V (L-PBF, stress relieved / HIP)

Route assumed: **AM L-PBF + HIP** · 3-D printable: **yes** · working temperature **300 °C**.

Tags: D = read from the primary source (values whose source starts with "pool" carry the tag recorded in `materials_pool.json`, built 2026-11-01…03 and not re-read on 2026-11-04), D-ag = read from the primary source by a research sub-agent on 2026-11-04 (URL in the source), S = secondary, Y = assumption or proxy.

| Property | 20 °C | 300 °C | Source | Tag |
|---|---|---|---|---|
| Density | 4410 kg/m³ |  | pool 'Ti-6Al-4V L-PBF': EOS Titanium Ti64ELI MDS (M290 06.2022 / M400 07.22), https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Titanium_Ti64ELI/Material_DataSheet_EOS_Titanium_Ti64Eli_EOSM290_EOSM400_en.pdf, via research_notes/Hafifletme derin araştırma 2/alloy_datasheets.md and research_notes/Üç sapma alanı/C_isil_enerji.md ('Approx. 4.41 g/cm3', M290) | D |
| Young's modulus E | 110 GPa | 96.8 | pool 'Ti-6Al-4V L-PBF': EOS Titanium Ti64ELI MDS (M290 06.2022 / M400 07.22), https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Titanium_Ti64ELI/Material_DataSheet_EOS_Titanium_Ti64Eli_EOSM290_EOSM400_en.pdf, via research_notes/Hafifletme derin araştırma 2/alloy_datasheets.md and research_notes/Üç sapma alanı/C_isil_enerji.md (400 W sheet 07.2022: 110 +- 15 GPa, H and V), via research_notes/Üç sapma alanı/C_isil_enerji.md | D |
| Poisson's ratio | 0.31  |  | typical Ti-6Al-4V (MIL-HDBK-5J Table 5.4.1.0(b) not read here) | Y |
| Tensile yield Fty (0.2 %) | 945 MPa | 590.1 | pool 'Ti-6Al-4V L-PBF': EOS Titanium Ti64ELI MDS (M290 06.2022 / M400 07.22), https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Titanium_Ti64ELI/Material_DataSheet_EOS_Titanium_Ti64Eli_EOSM290_EOSM400_en.pdf, via research_notes/Hafifletme derin araştırma 2/alloy_datasheets.md and research_notes/Üç sapma alanı/C_isil_enerji.md M290, 800 C/2 h, horizontal (vertical 965) | D |
| Tensile ultimate Ftu | 1055 MPa | 751.6 | pool 'Ti-6Al-4V L-PBF': EOS Titanium Ti64ELI MDS (M290 06.2022 / M400 07.22), https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Titanium_Ti64ELI/Material_DataSheet_EOS_Titanium_Ti64Eli_EOSM290_EOSM400_en.pdf, via research_notes/Hafifletme derin araştırma 2/alloy_datasheets.md and research_notes/Üç sapma alanı/C_isil_enerji.md M290, 800 C/2 h, horizontal (vertical 1075) | D |
| Max service temperature | 350 °C |  | pool 'Ti-6Al-4V L-PBF': EOS Titanium Ti64ELI MDS (M290 06.2022 / M400 07.22), https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Titanium_Ti64ELI/Material_DataSheet_EOS_Titanium_Ti64Eli_EOSM290_EOSM400_en.pdf, via research_notes/Hafifletme derin araştırma 2/alloy_datasheets.md and research_notes/Üç sapma alanı/C_isil_enerji.md 07.2022 'Thermal properties of parts' (max long-term operating ~350 C), via research_notes/Üç sapma alanı/C_isil_enerji.md | D |
| Fatigue (endurance / 1e6-1e7) | 600 MPa |  | pool 'Ti-6Al-4V L-PBF': Greitemeier (milled + HIP 920 C/100 MPa) via Afroz et al. 2022 Int J Fract 235 Table 3, via research_notes/Üç sapma alanı/A_titresim_yorulma.md | S |
| CTE | NOT FOUND | | | |
| Thermal conductivity | NOT FOUND | | | |
| Specific heat | NOT FOUND | | | |
| Embodied CO₂ (primary) | 46.5 kg CO₂e/kg |  | pool 'Ti-6Al-4V L-PBF': Ashby 2013 'Materials and the Environment' family values via 'Useful numbers for environmental studies' compilation (polybags.co.uk PDF), as coded in src/aerokit/materials/eco.py (titanium alloy family, p.4) | S |
| Embodied energy (primary) | 685 MJ/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction: titanium alloys 650-720 MJ/kg (eco.FAMILIES) | D |
| Embodied CO₂ (recycled) | 5.2 kg CO₂e/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction (eco.FAMILIES titanium) | D |
| Price (stock / powder) | 70.6 EUR/kg |  | Santiago-Herrera et al. 2023, Sustainability, Table 3: gas-atomised Ti-6Al-4V powder production cost 70.6 EUR/kg (opened by sub-agent; table columns slightly garbled) | D-ag |

Temperature factors E, Fty, Ftu at 300 °C: 0.880, 0.624, 0.712 — MIL-HDBK-5J Fig. 5.4.1.1.1 (annealed wrought Ti-6Al-4V, 1/2 h) at 572 F for Fty/Ftu; E(300 C)/E(RT) = 0.88: TIMET 6-4 sheet Table 2 gives 107-122 GPa at 20 C and 95-111 at 230 C (ratio ~0.90 at 230 C, extrapolated ~0.88 at 300 C); laser-DED data (Ivanov 2021) give 0.97 [D-ag, range] [D/D-ag].

Notes:
- Wrought-annealed temperature factors applied to L-PBF room-temperature values [Y]
- Fty factor cross-checks at 300 C: TIMET Fig. 1 plot ~640/910 = 0.70, laser-DED (Ivanov 2021 Table 1) ~775/1000 = 0.78 by interpolation; MIL 0.63 kept (conservative) [D-ag]
- EOS Ti64 ELI sheet (2014): max long-term operating temperature approx. 350 C [D-ag]

Ansys import: Engineering Data → File → Import Engineering Data → `materials_engineering_data.xml` (not tested on this laptop; the XML is checked by parsing it back).
