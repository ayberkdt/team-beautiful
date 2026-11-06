# Material card — Scalmalloy (Al-Mg-Sc, L-PBF)

Route assumed: **AM L-PBF + age** · 3-D printable: **yes** · working temperature **300 °C**.

Tags: D = read from the primary source (values whose source starts with "pool" carry the tag recorded in `materials_pool.json`, built 2026-11-01…03 and not re-read on 2026-11-04), D-ag = read from the primary source by a research sub-agent on 2026-11-04 (URL in the source), S = secondary, Y = assumption or proxy.

| Property | 20 °C | 300 °C | Source | Tag |
|---|---|---|---|---|
| Density | 2670 kg/m³ |  | pool 'Scalmalloy L-PBF': 3D Systems 'Certified Scalmalloy (A)' datasheet PN 10123B 02-22, https://3dsystems.com/sites/default/files/2022-02/3d-systems-certified-scalmalloy(a)-datasheet-usen-2022-02-23-a-print.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md ('value from literature', adopted from APWORKS) | D |
| Young's modulus E | 69 GPa | 29 | pool 'Scalmalloy L-PBF': Colibrium Additive M2 Series 5 Al-Mg-Sc datasheet 2025-08-21 RevB (horizontal, after 325 C/4 h; 70 as-built), read by sub-agent 2026-11-01, as cited in prev_guess/01_Ansys/tradeoff/build_studies.py | S |
| Poisson's ratio | 0.33  |  | typical aluminium | Y |
| Tensile yield Fty (0.2 %) | 490 MPa | 60 | pool 'Scalmalloy L-PBF': 3D Systems 'Certified Scalmalloy (A)' datasheet PN 10123B 02-22, https://3dsystems.com/sites/default/files/2022-02/3d-systems-certified-scalmalloy(a)-datasheet-usen-2022-02-23-a-print.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md (30 um, XY and Z; 60 um XY 500) | D |
| Tensile ultimate Ftu | 520 MPa | 103 | pool 'Scalmalloy L-PBF': 3D Systems 'Certified Scalmalloy (A)' datasheet PN 10123B 02-22, https://3dsystems.com/sites/default/files/2022-02/3d-systems-certified-scalmalloy(a)-datasheet-usen-2022-02-23-a-print.pdf, via prev_guess/01_Ansys/research/Hafifletme derin araştırma 2/alloy_datasheets.md (30 um, XY and Z) | D |
| Max service temperature | 150 °C |  | pool notes: yield 319 MPa at 150 C (Colibrium sheet via build_studies.py) | S |
| Fatigue (endurance / 1e6-1e7) | NOT FOUND | | | |
| CTE | NOT FOUND | | | |
| Thermal conductivity | NOT FOUND | | | |
| Specific heat | NOT FOUND | | | |
| Embodied CO₂ (primary) | 128 kg CO₂e/kg |  | pool 'Scalmalloy L-PBF': estimate: Sc share from Mehta et al. 2022 Table 2 x Hengevoss et al. 2024 Table 1, + Al 12; prev_guess/01_Ansys/tradeoff/build_studies.py SCAL_CO2 | Y |
| Embodied energy (primary) | 210 MJ/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction: aluminium 200-220 MJ/kg (eco.FAMILIES) | D |
| Embodied CO₂ (recycled) | NOT FOUND | | | |
| Price (stock / powder) | NOT FOUND | | | |

Temperature factors E, Fty, Ftu at 300 °C: 0.420, 0.122, 0.198 — Colibrium M2 Series 5 Al-Mg-Sc CMDS Rev B (2025-08-21), elevated-temperature table, DA, horizontal: 300 C E 29 GPa, YS 60 MPa, UTS 103 MPa (RT E 69 GPa) [D-ag] [D-ag].

Notes:
- Kept in the comparison to show the 300 C screen: Al alloys lose most of their strength [S]

Ansys import: Engineering Data → File → Import Engineering Data → `materials_engineering_data.xml` (not tested on this laptop; the XML is checked by parsing it back).
