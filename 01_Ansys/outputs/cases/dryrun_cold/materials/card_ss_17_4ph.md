# Material card — 17-4PH H1025 (wrought data; L-PBF route)

Route assumed: **AM L-PBF + H1025 + HIP** · 3-D printable: **yes** · working temperature **300 °C**.

Tags: D = read from the primary source (values whose source starts with "pool" carry the tag recorded in `materials_pool.json`, built 2026-11-01…03 and not re-read on 2026-11-04), D-ag = read from the primary source by a research sub-agent on 2026-11-04 (URL in the source), S = secondary, Y = assumption or proxy.

| Property | 20 °C | 300 °C | Source | Tag |
|---|---|---|---|---|
| Density | 7806 kg/m³ |  | pool '17-4PH H1025': DOT/FAA/AR-MMPDS-01 (Jan 2003), https://everyspec.com/FAA/FAA-General/DOT-FAA-AR-MMPDS-01-JAN2003_24102/ via prev_guess/01_Ansys/research/Üç sapma alanı/C_isil_enerji.md Table 2.6.9.0(b) p.2-197 (H900 value; MIL-HDBK-5J leaves omega blank for H1025) | D |
| Young's modulus E | 196.5 GPa | 173 | pool '17-4PH H1025': MIL-HDBK-5J (31 Jan 2003), local copy references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf (https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf); project extraction src/aerokit/materials/data/ Table 2.6.9.0(e), PDF p.253 (28.5 Msi) | D |
| Poisson's ratio | 0.272  |  | assumed typical for martensitic stainless | Y |
| Tensile yield Fty (0.2 %) | 1000 MPa | 816.1 | pool '17-4PH H1025': MIL-HDBK-5J (31 Jan 2003), local copy references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf (https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf); project extraction src/aerokit/materials/data/ Table 2.6.9.0(e) col 5, AMS 5643 bar < 8.000 in, L (145 ksi) | D |
| Tensile ultimate Ftu | 1069 MPa | 902.3 | pool '17-4PH H1025': MIL-HDBK-5J (31 Jan 2003), local copy references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf (https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf); project extraction src/aerokit/materials/data/ Table 2.6.9.0(e) col 5, AMS 5643 bar, L (155 ksi) | D |
| Max service temperature | 316 °C |  | pool '17-4PH H1025': United Performance Metals 17-4 PH datasheet ('up to 600 F (316 C)'), https://www.upmet.com/sites/default/files/datasheets/17-4-ph.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md | S |
| Fatigue (endurance / 1e6-1e7) | NOT FOUND | | | |
| CTE | NOT FOUND | | | |
| Thermal conductivity | NOT FOUND | | | |
| Specific heat | NOT FOUND | | | |
| Embodied CO₂ (primary) | 5 kg CO₂e/kg |  | pool '17-4PH H1025': Ashby 2013 'Materials and the Environment' family values via 'Useful numbers for environmental studies' compilation (polybags.co.uk PDF), as coded in src/aerokit/materials/eco.py (stainless steel family, p.3); family value, not PH-grade specific | S |
| Embodied energy (primary) | 84.5 MJ/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction: stainless steel 81-88 MJ/kg (eco.FAMILIES) | D |
| Embodied CO₂ (recycled) | 0.73 kg CO₂e/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction (eco.FAMILIES stainless) | D |
| Price (stock / powder) | NOT FOUND | | | |

Temperature factors E, Fty, Ftu at 300 °C: 0.880, 0.816, 0.844 — MIL-HDBK-5J Fig. 2.6.9.2.1 (17-4PH bar H900-H1075; the unlabeled curve is Fty by elimination) and Fig. 2.6.9.1.4 (E of H900, proxy for H1025) at 572 F [D].

Notes:
- Wrought allowables used for the AM route; L-PBF 17-4PH needs HIP + H1025 to approach them [Y]
- Cleveland-Cliffs 17-4PH bulletin (2021): 'good mechanical properties at temperatures up to 600 F'; H1150 after 1000 h at 600 F tested at 600 F: YS 814 MPa, UTS 848 MPa [D-ag]
- E at 300 C ~175 GPa (AISI 630 sheet, snippet only) agrees with the MIL factor 0.88 [S]

Ansys import: Engineering Data → File → Import Engineering Data → `materials_engineering_data.xml` (not tested on this laptop; the XML is checked by parsing it back).
