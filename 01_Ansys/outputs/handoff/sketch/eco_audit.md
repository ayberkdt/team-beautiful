# Eco audit — baseline vs redesign candidates

Structure of the Granta EduPack Eco Audit (material, manufacture, transport, use, end of life). Factors, sources and tags: `aerokit.bracket.ecoaudit.EcoInputs` (each value tagged D / D-ag / S / Y). EoL potential is shown separately, as EduPack does.

Baseline: **Structural Steel (Ansys Engineering Data default)**, 0.852 kg, route machined (buy-to-fly 8).

| Phase | Baseline CO₂ (kg) | Baseline energy (MJ) |
|---|---|---|
| material | 12.26 | 180.5 |
| manufacture | 3.846 | 57.05 |
| transport | 0.05763 | 0.8004 |
| use | 2.391e+04 | 3.321e+05 |
| end_of_life | 0 | 0 |
| **total** | **2.393e+04** | **3.323e+05** |
| EoL potential | n/a (no recycled-route value for this material in our data) | |

## Candidates (lightest passing design of each material, AM route where printable)

### Production (cradle to gate, kg CO₂e)

| Material | Mass (kg) | Material | Manufacture | Transport | Production total |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 0.852 | 12.26 | 3.846 | 0.0576 | 16.17 |
| 17-4PH H1025 (wrought data; L-PBF route) | 0.212 | 1.376 | 3.018 | 0.0143 | 4.408 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 0.120 | 7.229 | 1.705 | 0.00809 | 8.942 |
| Inconel 718 (L-PBF, solution + double age) | 0.221 | 3.333 | 3.151 | 0.015 | 6.499 |

### Whole life (kg CO₂e)

| Material | Use (EduPack form) | Life total | Δ vs baseline | Break-even km | Use, marginal factor |
|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) | 2.391e+04 | 2.393e+04 | +0 | 0 | 8409 |
| 17-4PH H1025 (wrought data; L-PBF route) | 5944 | 5949 | -1.798e+04 | 0 | 2090 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 3358 | 3367 | -2.056e+04 | 0 | 1181 |
| Inconel 718 (L-PBF, solution + double age) | 6206 | 6213 | -1.771e+04 | 0 | 2183 |

Use phase (EduPack mobile form): mass × life distance × 6.5 MJ/(t km) × 0.072 kg CO₂/MJ (long-haul aircraft row, EduPack 2021 R1 help, snippet level [S]); life distance 6.0e7 km [Y]. Marginal alternative: 12.5 t kerosene per 100 kg per year (Kellens et al. 2017 Table 8, short haul) × 25 years × 3.16 kg CO₂/kg [D-ag]. On the day, re-type the same masses into EduPack and compare.
