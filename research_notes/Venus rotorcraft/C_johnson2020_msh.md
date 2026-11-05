# C_johnson2020_msh — Mars Science Helicopter Conceptual Design (NASA/TM-2020-220485)

## Citation
Johnson, Wayne; Withrow-Maser, Shannah; Young, Larry; Malpica, Carlos; Koning, Witold J. F.; Kuang, Winnie; Fehler, Mireille; Tuano, Allysa; Chan, Athena; Datta, Anubhav; Chi, Cheng; Lumba, Ravi; Escobar, Daniel; Balaram, J.; Tzanetos, Theodore; Grip, Håvard F. (2020). *Mars Science Helicopter Conceptual Design.* NASA/TM-2020-220485, NASA Ames Research Center, March 2020. NTRS 20200002139.
PDF: https://ntrs.nasa.gov/api/citations/20200002139/downloads/1405_Johnson_Final_080420%5B1%5D.pdf
(The author list is as given by NTRS and the UWE repository search snippets. I did not check it against the PDF title page beyond the first author.)
Related: Withrow-Maser et al. / Malpica et al., *Mars Science Helicopter: Conceptual Design of the Next Generation of Mars Rotorcraft*, AIAA ASCEND 2020, DOI 10.2514/6.2020-4029 (not read).

## What was read
Full text extraction (53 pages, pypdf): abstract, the Mars atmosphere section and Table 1, computational methods, Tables 3, 5, 6, 7, 8, 9, 10, 11, the weight models and assumptions, and the conclusions. Figures were not viewed.

Tag: [D-ag] read in this report. [derived] my arithmetic.

## Key numbers [D-ag]
**Headline (abstract and conclusions):** a **31 kg hexacopter** that fits within a **2.5 m diameter aeroshell** could carry a **5 kg payload for 10 min of hover or 5 km range**. The initial design point was ~20 kg with 2-3 kg payload.

**Table 1 — Earth vs Mars:** ρ 1.225 vs 0.017 kg/m³; T 15 vs −50 °C; μ 1.75e-5 vs 1.13e-5; a 340.3 vs 233.1 m/s; tip speed at M = 0.7: 238 vs 163 m/s; Re (M = 0.5, c = 0.1 m) 1,297,000 vs 19,100. Mars density varies 0.010-0.020 kg/m³, and Mars rotor Re is 10,000-25,000.

**Table 3 — initial designs (NDARC):**
| | MSH coaxial | MSH hexacopter | MH (Ingenuity) |
|---|---|---|---|
| rotor radius [m] | 1.25 | 0.64 | 0.605 |
| gross weight [kg] | 18.03 | 17.66 | 1.80 |
| rotors × blades | 2 × 4 | 6 × 4 | 2 × 2 |
| disk area [m²] | 4.91 | 7.72 | 2.30 |
| disk loading [kg/m²] | 3.67 | 2.29 | 0.78 |
| Re (75 % R) | 24,752 | 15,784 | 11,412 |
| solidity | 0.310 | 0.193 | 0.148 |
| tip speed [m/s] | 163.17 | 163.17 | 163.17 |
| rotor speed [rpm] | 1247 | 2435 | 2575 |
| motor power [kW] | 3.17 | 3.32 | 0.36 |
| solar cell [m²] | 0.62 | 0.62 | 0.04 |
| battery [Ah] | 128 | 113 | 12 |
| payload [kg] | 2.02 | 2.02 | — |
Table 3 thus gives the MH (Ingenuity) solidity as **0.148**, consistent with my integration of Koning's table (C_koning2018: ≈0.144 thrust-weighted).

**Table 4 — hexacopter design mission:** takeoff 0.5 min; climb to 200 m; fly 1000 m at 30 m/s; hover 2 min at site (50 % of energy); sleep 1 sol (17 %).

**Design rules:** C_T/σ = 0.11 initial (10 % above MH), later 0.115. Control requirement: **40 % thrust margin from design blade loading to stall**. Tip Mach 0.7 → 0.8 in the update. Advancing-tip limit M_at < 0.95, with no drag divergence seen up to 0.95 for the thin optimized sections. Optimum twist −18° linear (hexacopter blade).

**Weight/technology models (calibrated to MH):** battery 278 Wh/kg cell, **230 Wh/kg pack**, 218.5 Wh/kg EOL, 420 Wh/L, 70 % usable (10-80 % DoD). Motor + electronics efficiency 80 %; servo power 15 % of rotor power; overall 68 %. Motor weight = 0.076·Q^n kg (the exponent n was garbled in the text extraction and is not read). Solar 540 Wh/m²/sol (21.9 W/m²) at 2.0 kg/m². Landing gear 0.067 W. Avionics 1.2 kg. Contingency 20 %. Sleep energy 15·W^(1/3) Wh/sol.

**Table 5 — flap frequency / control bandwidth:** MH flap frequency 2.02/rev = 86.7 Hz; MSH hex 1.546/rev = 62.7 Hz; coax 1.537/rev = 32.1 Hz. Conclusion: a large coaxial is hard to make controllable on Mars, so the **hexacopter** was preferred.

**Table 7 — airfoil (cl/cd) at design (Re 11,354-16,682, M 0.35-0.52, cl 0.65):** CLF5605 (MH) 18.34; circular arc 20.51; cambered plate 23.70; arbitrary continuous 21.51; **double-edged plate 23.43 (chosen for outboard)**; polygonal 22.57 (inboard). Optimized shapes are thin with a sharp leading edge, giving immediate LE separation.

**Table 8 — updated designs (hexacopter, updated tip speed case):** C_T/σ 0.115; M_tip 0.8; V_tip 186.5 m/s; 2782 rpm; R 0.64 m; GW 17.69 kg; σ 0.142; disk loading 2.29 kg/m²; total power **2.80 kW**; battery 172 Ah, 2.31 kg; range 2 km plus 4.5 min hover. Raising M_tip from 0.7 to 0.8 doubled range and hover time at the same gross weight.

**Table 10 — max-capability hexacopter (R 0.64 m, Jezero spring 0.015 kg/m³, −50 °C, 25 % contingency, σ ≤ 0.25):** GW **31.2 kg**, power **6.2 kW**. Payload 8 kg: 3.2 km or 1.5 min; 5 kg: 9.6 km or 4.7 min; 2 kg: 16 km or 7.8 min; 0 kg: 20.4 km or 9.9 min. (The abstract's "5 kg for 10 min or 5 km" phrasing differs from this table row.)

**Table 11 — Advanced MH (same R 0.605 m):** GW 4.6 kg, 1.3 kg payload, σ 0.248, 2943 rpm, 0.88 kW.

[derived]: Hexacopter hover power loading ≈ 2.80 kW / 17.69 kg ≈ 158 W/kg (Mars); 31.2 kg / 6.2 kW ≈ 199 W/kg installed.

## Design method [D-ag]
Spreadsheet sizing calibrated to MH → NDARC (P = P_i + P_o + P_p with κ and cd_mean calibrated to CAMRAD II) → CAMRAD II free wake for planform, twist and rotor-rotor interference. Blade planform from XROTOR/CROTOR minimum induced loss, refined with AeroVironment PROP (BEMT validated for low-Re propellers).

## Caveats
- All values are design-study outputs, not measurements.
- The report notes the MSH "updated" airfoil gains (Table 7) still awaited experimental verification near stall.
- The table formatting in my text extraction was flattened. I matched columns by order, and for Table 3 the column order is (coaxial, hex, MH) as in the header.
