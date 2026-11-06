# Eco audit — baseline vs redesign candidates

Structure of the Granta EduPack Eco Audit (material, manufacture, transport, use, end of life). Factors, sources and tags: `aerokit.bracket.ecoaudit.EcoInputs` (each value tagged D / D-ag / S / Y). EoL potential is shown separately, as EduPack does.

Baseline: **Structural Steel (Ansys Engineering Data default)**, 0.577 kg, route machined (buy-to-fly 8).

| Phase | Baseline CO₂ (kg) | Baseline energy (MJ) |
|---|---|---|
| material | 8.311 | 122.4 |
| manufacture | 2.607 | 38.67 |
| transport | 0.03906 | 0.5425 |
| use | 1.621e+04 | 2.251e+05 |
| end_of_life | 0 | 0 |
| **total** | **1.622e+04** | **2.252e+05** |
| EoL potential | n/a (no recycled-route value for this material in our data) | |

## Candidates (lightest passing design of each material, AM route where printable)

### Production (cradle to gate, kg CO₂e)

| Material | Mass (kg) | Material | Manufacture | Transport | Production total |
|---|---|---|---|---|---|
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 0.080 | 4.856 | 1.145 | 0.00544 | 6.006 |
| Inconel 718 (L-PBF, solution + double age) | 0.148 | 2.239 | 2.116 | 0.01 | 4.365 |
| 17-4PH H1025 (wrought data; L-PBF route) | 0.142 | 0.9242 | 2.027 | 0.00962 | 2.961 |
| Structural Steel (Ansys Engineering Data default) | 0.288 | 4.147 | 1.301 | 0.0195 | 5.467 |

### Whole life (kg CO₂e)

| Material | Use (EduPack form) | Life total | Δ vs baseline | Break-even km | Use, marginal factor |
|---|---|---|---|---|---|
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 2256 | 2262 | -1.396e+04 | 0 | 793.2 |
| Inconel 718 (L-PBF, solution + double age) | 4168 | 4173 | -1.204e+04 | 0 | 1466 |
| 17-4PH H1025 (wrought data; L-PBF route) | 3992 | 3995 | -1.222e+04 | 0 | 1404 |
| Structural Steel (Ansys Engineering Data default) | 8086 | 8092 | -8125 | 0 | 2844 |

Use phase (EduPack mobile form): mass × life distance × 6.5 MJ/(t km) × 0.072 kg CO₂/MJ (long-haul aircraft row, EduPack 2021 R1 help, snippet level [S]); life distance 6.0e7 km [Y]. Marginal alternative: 12.5 t kerosene per 100 kg per year (Kellens et al. 2017 Table 8, short haul) × 25 years × 3.16 kg CO₂/kg [D-ag]. On the day, re-type the same masses into EduPack and compare.
