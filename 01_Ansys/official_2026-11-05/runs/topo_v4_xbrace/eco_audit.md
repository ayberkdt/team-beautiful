# Eco audit — baseline vs redesign candidates

Structure of the Granta EduPack Eco Audit (material, manufacture, transport, use, end of life). Factors, sources and tags: `aerokit.bracket.ecoaudit.EcoInputs` (each value tagged D / D-ag / S / Y). EoL potential is shown separately, as EduPack does.

Baseline: **Structural Steel (Ansys Engineering Data default)**, 152.271 kg, route machined (buy-to-fly 8).

| Phase | Baseline CO₂ (kg) | Baseline energy (MJ) |
|---|---|---|
| material | 2193 | 3.228e+04 |
| manufacture | 687.8 | 1.02e+04 |
| transport | 10.31 | 143.1 |
| use | 4.276e+06 | 5.939e+07 |
| end_of_life | 0 | 0 |
| **total** | **4.279e+06** | **5.943e+07** |
| EoL potential | n/a (no recycled-route value for this material in our data) | |

## Candidates (lightest passing design of each material, AM route where printable)

### Production (cradle to gate, kg CO₂e)

| Material | Mass (kg) | Material | Manufacture | Transport | Production total |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 152.271 | 2193 | 687.8 | 10.3 | 2891 |
| 17-4PH H1025 (wrought data; L-PBF route) | 42.034 | 273.2 | 599.3 | 2.84 | 875.3 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 85.543 | 5171 | 1220 | 5.79 | 6396 |
| Inconel 718 (L-PBF, solution + double age) | 43.887 | 661.8 | 625.7 | 2.97 | 1290 |

### Whole life (kg CO₂e)

| Material | Use (EduPack form) | Life total | Δ vs baseline | Break-even km | Use, marginal factor |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 4.276e+06 | 4.279e+06 | +0 | 0 | 1.504e+06 |
| 17-4PH H1025 (wrought data; L-PBF route) | 1.18e+06 | 1.181e+06 | -3.097e+06 | 0 | 4.151e+05 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 2.402e+06 | 2.408e+06 | -1.87e+06 | 1.12e+05 | 8.447e+05 |
| Inconel 718 (L-PBF, solution + double age) | 1.232e+06 | 1.234e+06 | -3.045e+06 | 0 | 4.334e+05 |

Use phase (EduPack mobile form): mass × life distance × 6.5 MJ/(t km) × 0.072 kg CO₂/MJ (long-haul aircraft row, EduPack 2021 R1 help, snippet level [S]); life distance 6.0e7 km [Y]. Marginal alternative: 12.5 t kerosene per 100 kg per year (Kellens et al. 2017 Table 8, short haul) × 25 years × 3.16 kg CO₂/kg [D-ag]. On the day, re-type the same masses into EduPack and compare.
