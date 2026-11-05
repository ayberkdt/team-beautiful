# Eco audit — baseline vs redesign candidates

Structure of the Granta EduPack Eco Audit (material, manufacture, transport, use, end of life). Factors, sources and tags: `aerokit.bracket.ecoaudit.EcoInputs` (each value tagged D / D-ag / S / Y). EoL potential is shown separately, as EduPack does.

Baseline: **Structural Steel (Ansys Engineering Data default)**, 1.996 kg, route machined (buy-to-fly 8).

| Phase | Baseline CO₂ (kg) | Baseline energy (MJ) |
|---|---|---|
| material | 28.75 | 423.2 |
| manufacture | 9.017 | 133.8 |
| transport | 0.1351 | 1.877 |
| use | 5.606e+04 | 7.786e+05 |
| end_of_life | 0 | 0 |
| **total** | **5.61e+04** | **7.791e+05** |
| EoL potential | n/a (no recycled-route value for this material in our data) | |

## Candidates (lightest passing design of each material, AM route where printable)

### Production (cradle to gate, kg CO₂e)

| Material | Mass (kg) | Material | Manufacture | Transport | Production total |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 0.789 | 11.36 | 3.562 | 0.0534 | 14.97 |
| 17-4PH H1025 (wrought data; L-PBF route) | 0.491 | 3.189 | 6.994 | 0.0332 | 10.22 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 0.443 | 26.78 | 6.316 | 0.03 | 33.13 |
| Inconel 718 (L-PBF, solution + double age) | 0.512 | 7.724 | 7.302 | 0.0347 | 15.06 |

### Whole life (kg CO₂e)

| Material | Use (EduPack form) | Life total | Δ vs baseline | Break-even km | Use, marginal factor |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 2.214e+04 | 2.216e+04 | -3.394e+04 | 0 | 7787 |
| 17-4PH H1025 (wrought data; L-PBF route) | 1.377e+04 | 1.378e+04 | -4.231e+04 | 0 | 4844 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 1.244e+04 | 1.247e+04 | -4.362e+04 | 0 | 4375 |
| Inconel 718 (L-PBF, solution + double age) | 1.438e+04 | 1.44e+04 | -4.17e+04 | 0 | 5058 |

Use phase (EduPack mobile form): mass × life distance × 6.5 MJ/(t km) × 0.072 kg CO₂/MJ (long-haul aircraft row, EduPack 2021 R1 help, snippet level [S]); life distance 6.0e7 km [Y]. Marginal alternative: 12.5 t kerosene per 100 kg per year (Kellens et al. 2017 Table 8, short haul) × 25 years × 3.16 kg CO₂/kg [D-ag]. On the day, re-type the same masses into EduPack and compare.
