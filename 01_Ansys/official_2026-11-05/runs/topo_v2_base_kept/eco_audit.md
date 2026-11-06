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
| Structural Steel (Ansys Engineering Data default) | 67.914 | 978 | 306.7 | 4.6 | 1289 |
| 17-4PH H1025 (wrought data; L-PBF route) | 57.215 | 371.9 | 815.7 | 3.87 | 1191 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 32.324 | 1954 | 460.8 | 2.19 | 2417 |
| Inconel 718 (L-PBF, solution + double age) | 59.736 | 900.8 | 851.6 | 4.04 | 1757 |

### Whole life (kg CO₂e)

| Material | Use (EduPack form) | Life total | Δ vs baseline | Break-even km | Use, marginal factor |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 1.907e+06 | 1.908e+06 | -2.37e+06 | 0 | 6.706e+05 |
| 17-4PH H1025 (wrought data; L-PBF route) | 1.607e+06 | 1.608e+06 | -2.671e+06 | 0 | 5.65e+05 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 9.076e+05 | 9.101e+05 | -3.369e+06 | 0 | 3.192e+05 |
| Inconel 718 (L-PBF, solution + double age) | 1.677e+06 | 1.679e+06 | -2.6e+06 | 0 | 5.899e+05 |

Use phase (EduPack mobile form): mass × life distance × 6.5 MJ/(t km) × 0.072 kg CO₂/MJ (long-haul aircraft row, EduPack 2021 R1 help, snippet level [S]); life distance 6.0e7 km [Y]. Marginal alternative: 12.5 t kerosene per 100 kg per year (Kellens et al. 2017 Table 8, short haul) × 25 years × 3.16 kg CO₂/kg [D-ag]. On the day, re-type the same masses into EduPack and compare.
