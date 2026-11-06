# Card requirements vs the organisers' data — S275N, Al 2618-T6, Ti-8Al-1Mo-1V

Card: `Ideathon_Challenge_Ansys_2026.docx` (re-read from Files.zip). Values: the organisers' Material selection report p.7–13, copied by `conditions_matrix.py` from the verified record `organiser_table_full.json` (two extraction methods identical on 160 value rows; third engine found 447/450 cells, the 3 others checked on the page image). **All organiser values are at 23 °C** (report p.14 'Functional parameters: Temperature 23'); rows marked # are 'with temperature' attributes evaluated at that 23 °C, not at 300 °C.

## 0. Condition (heat treatment) of each record

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Condition | Normalized | T6 (Solution heat- treated and artificially aged) | Single annealed | p.7  |
| Materials Data for Simulation name | Structural steel, S275N | Aluminum alloy, wrought, 2618, T6 | Titanium alloy, Ti-8Al- 1Mo-1V, annealed | p.7  |
| EN name | BS EN 10025-3:2004 | EN AW-2618 (EN AW- Al Cu2Mg1,5Ni) | – | p.7  |
| UNS number | – | A92618 | R54810 | p.7  |

What the condition means for > 300 °C service: S275N normalized — no ageing treatment to lose. 2618 **T6 = solution treated and artificially aged**: strength comes from precipitates formed at the ageing temperature (≈ 195 °C for 2618A, BAM data set [S]); service above it over-ages the alloy (MIL-HDBK-5J: 2618-T61 keeps 60 % of Ftu after 1000 h at 204 °C [D-ag]). Ti-8-1-1 **single annealed = 1450 °F (788 °C) 8 h, furnace cool** (MIL-HDBK-5J p.5-27 [D]) — a stable mill condition far above 300 °C; MIL notes duplex anneal gives the higher fracture toughness [D].

## 1. 'Working temperature >300°C'

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Maximum service temperature (°C) | 471 - 501 | 250 - 300 | 407 - 455 | p.9  |
| **verdict** | ✔ top of range 501 °C > 300 | ✘ top of range 300 °C ≤ 300 | ✔ top of range 455 °C > 300 | |
| Oxidation at 500C | Acceptable | Unacceptable | Acceptable | p.11  |
| Melting point (°C) | 1410 - 1500 | 560 - 650 | 1530 - 1550 | p.9  |
| Young's modulus with temperature (GPa) # | – | 74 | 125 | p.8 (at 23 °C) |
| Yield strength with temperature (MPa) # | – | 370 | 845 | p.8 (at 23 °C) |
| Thermal expansion coefficient (µstrain/°C) | 11 - 13 | 21.5 - 22.6 | 8.73 - 9.18 | p.9  |
| Thermal conductivity (W/m.°C) | 48 - 53 | 148 - 154 | 6.1 - 6.61 | p.9  |
| Thermal shock resistance (°C) | 79.6 - 112 | 195 - 235 | 679 - 843 | p.9  |

Note: the organisers' Granta filter was '≥ 300' with 'pass when any part of record within selection' (report p.4) — that is why 2618 (250–300) passed their filter while failing the card's strict '> 300'.

## 2. 'Ability to be casted or 3D printed'

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Metal casting | Unsuitable | Unsuitable | Limited use | p.10  |
| Metal powder forming, climate change (CO2-eq) (kg/kg) | 5.28 - 6.79 | 3.89 - 5.17 | 6.24 - 7.26 | p.12 (process data exist for all three) |
| Metal casting, climate change (CO2-eq) (kg/kg) | – | – | 3.79 - 4.28 | p.12  |
| Machining speed (m/min) | 45.7 | 39.6 | 9.75 | p.11  |
| Weldability | Good | Poor | Good | p.11  |
| Weldability Notes _ | Preheating and post weld heat treatments may be required | Preheating is not required, post weld heat treatment is required | Preheating and post weld heat treatments are not required | p.11  |

All three passed the organisers' stage 2 (ProcessUniverse: Additive manufacturing OR Casting, report p.5). The report has no 'additive manufacturing suitability' row; 'Metal casting' is the only process rating given.

## 3. 'Minimum fracture toughness of 10MPa.m^1/2'

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Fracture toughness (MPa.m^0.5) | 26.4 - 38.1 | 31 - 34 | 65 - 75 | p.9  |
| **verdict** | ✔ low end 26.4 ≥ 10 | ✔ low end 31 ≥ 10 | ✔ low end 65 ≥ 10 | |
| Toughness (G) (kJ/m^2) | 3.41 - 6.73 | 13 - 15.7 | 34.2 - 45.2 | p.9  |
| Elongation (% strain) | 23 - 24 | 8 - 9 | 6 - 10 | p.8  |

## 4. Structural: 'Factor of Safety of 1.5', 'Max displacement below 1/400 of largest dimension'

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Young's modulus (GPa) | 200 - 221 | 72 - 76 | 121 - 127 | p.8  |
| Yield strength (elastic limit) (MPa) | 205 - 275 | 320 - 380 | 758 - 931 | p.8  |
| Tensile strength (MPa) | 350 - 510 | 400 - 440 | 827 - 1000 | p.8  |
| Compressive strength (MPa) | 205 - 275 | 320 - 380 | 750 - 829 | p.9  |
| Shear modulus (GPa) | 77.5 - 83.5 | 25 - 28 | 46 - 48.4 | p.9  |
| Poisson's ratio | 0.29 - 0.32 | 0.325 - 0.335 | 0.32 - 0.333 | p.9  |
| Specific stiffness (MN.m/kg) | 25.5 - 28.1 | 26.1 - 27.7 | 27.7 - 29.1 | p.8  |
| Specific strength (kN.m/kg) | 26.1 - 35 | 116 - 138 | 173 - 213 | p.8  |
| Fatigue strength at 10^7 cycles (MPa) | 194 - 233 | 118 - 130 | 529 - 579 | p.9  |

Allowable von Mises with FoS 1.5 on the LOW end of yield: S275N (reference) 137 MPa, Al 2618-T6 213 MPa, Ti-8Al-1Mo-1V SA 505 MPa (23 °C).

## 5. Objectives: weight, cost, CO₂ over the full life

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Density (kg/m^3) | 7800 - 7900 | 2720 - 2780 | 4350 - 4400 | p.8  |
| Price (USD/kg) | 1.02 - 1.56 | 3.12 - 3.48 | 23 - 26.3 | p.8  |
| Price per unit volume (USD/m^3) | 7960 - 12300 | 8490 - 9670 | 100000 - 116000 | p.8  |
| Mass per unit of stiffness | 528 - 556 | 314 - 325 | 388 - 398 | p.7  |
| Cost per unit of stiffness | 552 - 846 | 995 - 1120 | 9020 - 10300 | p.7  |
| Climate change (CO2-eq) (virgin grade production) (kg/kg) | 2.89 - 3.18 | 12 - 13.2 | 33.6 - 37.1 | p.11 (card: use virgin) |
| Metal powder forming, climate change (CO2-eq) (kg/kg) | 5.28 - 6.79 | 3.89 - 5.17 | 6.24 - 7.26 | p.12 (card: powder forming) |
| Climate change (CO2-eq), recycling (kg/kg) | 0.78 - 0.859 | 2.76 - 3.04 | 9.74 - 10.8 | p.13  |
| Recycle | Yes | Yes | Yes | p.13  |
| Functional recycle | Yes | No | No | p.13  |
| Recycle fraction in current supply (%) | 41 | 35 | 50 | p.13  |
| Embodied energy (virgin grade production) (MJ/kg) | 27.4 - 30.2 | 167 - 184 | 553 - 609 | p.11  |

## 6. Not in the card but relevant for an engine-cowling bracket

| Property (organisers' wording) | S275N (reference) | Al 2618-T6 | Ti-8Al-1Mo-1V SA | Source |
|---|---|---|---|---|
| Stress corrosion cracking | Slightly susceptible | Highly susceptible | Slightly susceptible | p.11  |
| Stress corrosion cracking Notes _ | Rated in chloride; Other susceptible environments: Hydrogen sulfide | Rated in chloride; Other susceptible environments: Halide, water | Rated in chloride; Other susceptible environments: Halide, organic liquids, dinitrogen tetroxide | p.11  |
| Water (salt) | Limited use | Acceptable | Excellent | p.11  |
| Galvanic potential (V) | -0.51 - -0.43 | -0.78 - -0.7 | -0.13 - -0.05 | p.10  |
| Galling resistance (adhesive wear) | Acceptable | Limited use | Limited use | p.11  |
| Flammability | Non-flammable | Non-flammable | Non-flammable | p.11  |
| Contains >5wt% critical elements? | No | Yes | Yes | p.10  |
| Sourcing and geopolitical risk level | Low | Very high | Medium | p.10  |
| Price volatility risk level | Medium | High | Low | p.10  |
| Conflict material risk level | None | Caution | None | p.10  |

