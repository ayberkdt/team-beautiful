# C_koning2018 — Generation of Mars Helicopter Rotor Model for Comprehensive Analyses

## Citation
Koning, Witold J. F.; Johnson, Wayne; Allan, Brian G. (2018). *Generation of Mars Helicopter Rotor Model for Comprehensive Analyses.* AHS Specialists' Conference on Aeromechanics Design for Transformative Vertical Flight, San Francisco, 16-18 Jan 2018. NTRS 20180008645 (ARC-E-DAA-TN50660). Not subject to US copyright (US Government work).
PDF: https://rotorcraft.arc.nasa.gov/Publications/files/Koning_2018_TechMx.pdf

## What was read
Full text, 22 pages (pypdf extraction): abstract, Table 1 (Mars conditions), Table 2 (blade geometry), Table 3, Table B1 (airfoil thickness and camber), the conclusions, and the passages around Fig. 26 (FM vs blade loading). I did not digitize this paper's figures. The measured CT-CP points are taken from the 2019 journal version instead (see C_koning2019).

Tag: [D-ag] read in this paper. [derived] my arithmetic.

## Numbers [D-ag]
**Rotor** (p. 3): coaxial, 2 × 2-bladed, hingeless, counter-rotating. Rotor spacing "approximately 12% of the rotor radius" (the 2019 version says 8-9 % of diameter). Up to 2,800 RPM. Max airspeed 10 m/s horizontal, 3 m/s vertical (citing Grip). Mass ~1.8 kg, rotor diameter 1.21 m, flights up to 90 s (p. 2).

**Reynolds number**: chord-based Re ≈ 10³ to 10⁴ (abstract, p. 2). The flow is subcritical and boundary-layer transition is unlikely, so no transition model is needed (abstract, conclusions).

**Table 1 — Mars conditions** (p. 3):
| | Earth SLS | MC1 | MC2 | MC3 |
|---|---|---|---|---|
| ρ [kg/m³] | 1.225 | 0.015 | 0.017 | 0.020 |
| T [K] | 288.2 | 248.2 | 223.2 | 193.2 |
| R [J/kg K] | 287.1 | 188.9 | 188.9 | 188.9 |
| γ | 1.400 | 1.289 | 1.289 | 1.289 |
| μ [N s/m²] | 1.75e-5 | 1.13e-5 | 1.13e-5 | 1.13e-5 |
| p [Pa] | 101,300 | 703.1 | 716.6 | 729.7 |

**Table 2 — blade geometry, no sweep** (p. 3) — a complete BEMT input for the Ingenuity blade:
| Station | r/R | c/R | t/c | twist ε [deg] | airfoil |
|---|---|---|---|---|---|
| 1 | 0.0908 | 0.0506 | 0.973 | 16.32 | Station 1 (near-circular root) |
| 2 | 0.2000 | 0.1407 | 0.220 | 17.62 | Station 2 |
| 3 | 0.2950 | 0.1968 | 0.098 | 15.92 | Station 3 |
| 4 | 0.3903 | 0.1968 | 0.060 | 12.07 | Station 4 |
| 5 | 0.5271 | 0.1627 | 0.050 | 8.43 | clf5605 |
| 6 | 0.7621 | 0.1209 | 0.050 | 3.93 | clf5605 |
| 65 | 0.9241 | 0.0860 | 0.050 | 1.39 | clf5605 |
| 7 | 0.9912 | 0.0341 | 0.050 | 0.06 | clf5605 |

**Table B1 — airfoil thickness and camber** (p. 17), with t/c, f/c in % and positions in x/c:
| Airfoil | t/c | x_t/c | f/c | x_f/c |
|---|---|---|---|---|
| Station 1 | 96.201 | 0.466 | 0.000 | 0.000 |
| Station 2 | 21.985 | 0.346 | 5.298 | 0.594 |
| Station 3 | 9.800 | 0.255 | 5.083 | 0.591 |
| Station 4 | 5.899 | 0.201 | 4.944 | 0.597 |
| **clf5605** | **5.000** | 0.200 | **4.910** | 0.593 |
So clf5605 is a thin (5 %) section with ~4.9 % camber at ~59 % chord, close to a cambered plate.

**Airfoil deck** (Table 3, p. 4): α −15° to 20° in 1° steps. M 0.1-0.3 (station 1) up to 0.2-0.9 (station 7). Generated with C81Gen/ARC2D RANS. More than 4,500 cases. NACA 0012 experimental data stitched in outside the computed α range (p. 14).

**Performance validation** (p. 15-16): CAMRAD II free-wake FM vs blade loading for MC1-3, compared with JPL 25-ft Space Simulator data. The test was in CO2 at T = 288 K and 2,600 RPM. Measured shaft power was taken from motor power using a near-constant motor/drive efficiency of **78 %**. The paper calls the correlation "satisfactory".

[derived] from Table 2 (trapezoid over r/R 0.0908-0.9912): thrust-weighted c_e/R ≈ 0.113, giving σ ≈ 0.072 per 2-blade rotor and ≈ 0.144 for the coax (4 blades). The geometric (area) solidity is ≈ 0.079 per rotor. c(0.75R) ≈ 0.123R ≈ 0.074 m for R = 0.605 m. These are my integrations; the paper does not state a solidity in the text I read.

## Caveats
- The airfoil decks are CFD (RANS) results, not wind-tunnel data.
- The 2018 version was superseded by the 2019 AIAA J paper (C_koning2019), which uses time-accurate OVERFLOW with a transition model.
