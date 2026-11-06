# Material card — Inconel 718 (L-PBF, solution + double age)

Route assumed: **AM L-PBF + STA** · 3-D printable: **yes** · working temperature **300 °C**.

Tags: D = read from the primary source (values whose source starts with "pool" carry the tag recorded in `materials_pool.json`, built 2026-11-01…03 and not re-read on 2026-11-04), D-ag = read from the primary source by a research sub-agent on 2026-11-04 (URL in the source), S = secondary, Y = assumption or proxy.

| Property | 20 °C | 300 °C | Source | Tag |
|---|---|---|---|---|
| Density | 8150 kg/m³ |  | pool 'Inconel 718 L-PBF': EOS NickelAlloy IN718 MDS V1.0 CR696 2020-02, https://eos.info/05-datasheet-images/Assets_MDS_Metal/EOS_NickelAlloy_IN718/Material_DataSheet_EOS_NickelAlloy_IN718_en.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md and prev_guess/01_Ansys/research/Üç sapma alanı/C_isil_enerji.md ('min 8.15 g/cm3') | D |
| Young's modulus E | 200 GPa | 184 | pool 'Inconel 718 L-PBF': EOS gives none; wrought SMC-045 Table 4 value assumed (as in build_studies.py) | Y |
| Poisson's ratio | 0.29  |  | typical nickel superalloy | Y |
| Tensile yield Fty (0.2 %) | 1145 MPa | 1096 | pool 'Inconel 718 L-PBF': EOS NickelAlloy IN718 MDS V1.0 CR696 2020-02, https://eos.info/05-datasheet-images/Assets_MDS_Metal/EOS_NickelAlloy_IN718/Material_DataSheet_EOS_NickelAlloy_IN718_en.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md and prev_guess/01_Ansys/research/Üç sapma alanı/C_isil_enerji.md M290 40 um, heat treated, vertical (horizontal 1240) | D |
| Tensile ultimate Ftu | 1375 MPa | 1274 | pool 'Inconel 718 L-PBF': EOS NickelAlloy IN718 MDS V1.0 CR696 2020-02, https://eos.info/05-datasheet-images/Assets_MDS_Metal/EOS_NickelAlloy_IN718/Material_DataSheet_EOS_NickelAlloy_IN718_en.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md and prev_guess/01_Ansys/research/Üç sapma alanı/C_isil_enerji.md heat treated, vertical (horizontal 1505) | D |
| Max service temperature | 700 °C |  | pool 'Inconel 718 L-PBF': EOS NickelAlloy IN718 MDS V1.0 CR696 2020-02, https://eos.info/05-datasheet-images/Assets_MDS_Metal/EOS_NickelAlloy_IN718/Material_DataSheet_EOS_NickelAlloy_IN718_en.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md and prev_guess/01_Ansys/research/Üç sapma alanı/C_isil_enerji.md p1: 'good tensile, fatigue, creep and rupture strength at temperatures up to 700 C' | D |
| Fatigue (endurance / 1e6-1e7) | NOT FOUND | | | |
| CTE | NOT FOUND | | | |
| Thermal conductivity | NOT FOUND | | | |
| Specific heat | NOT FOUND | | | |
| Embodied CO₂ (primary) | 11.6 kg CO₂e/kg |  | pool 'Inconel 718 L-PBF': Ashby 2013 'Materials and the Environment' family values via 'Useful numbers for environmental studies' compilation (polybags.co.uk PDF), as coded in src/aerokit/materials/eco.py Ni family as low end; high 25 assumed for Nb/Mo and atomisation (prev_guess/01_Ansys/tradeoff/build_studies.py) | Y |
| Embodied energy (primary) | 232.5 MJ/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction: nickel superalloys 221-244 MJ/kg (eco.FAMILIES) | D |
| Embodied CO₂ (recycled) | 2.14 kg CO₂e/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction (eco.FAMILIES nickel) | D |
| Price (stock / powder) | NOT FOUND | | | |

Temperature factors E, Fty, Ftu at 300 °C: 0.920, 0.957, 0.927 — Special Metals INCONEL 718 bulletin (2007): Table 4 E 29.0 -> 26.7 Msi at 600 F; Table 19 (hot-rolled, annealed + aged) YS 163.0 -> 156.0 ksi, UTS 198.0 -> 183.5 ksi at 600 F (316 C, used for 300 C: slightly conservative) [D-ag]; wrought ratios applied to L-PBF [Y] [D-ag].

Ansys import: Engineering Data → File → Import Engineering Data → `materials_engineering_data.xml` (not tested on this laptop; the XML is checked by parsing it back).
