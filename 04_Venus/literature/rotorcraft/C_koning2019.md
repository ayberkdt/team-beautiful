# C_koning2019 — Improved Mars Helicopter Aerodynamic Rotor Model (incl. measured Ingenuity rotor CT-CP)

## Citation
Koning, Witold J. F.; Johnson, Wayne; Grip, Håvard F. (2019). *Improved Mars Helicopter Aerodynamic Rotor Model for Comprehensive Analyses.* AIAA Journal 57(9): 3969-3979. DOI: 10.2514/1.J058045.
PDF (author copy on the NASA Ames site): https://rotorcraft.arc.nasa.gov/Publications/files/koning_AIAA_2019.pdf

## What was read
Full text, 11 pages (pypdf). Table 1 and Table 2 (p. 3973). Figs 2, 3 and 4 (p. 3970) viewed. Figs 10 and 11 (p. 3974) read by eye at 330 dpi. Fig. 25 (p. 3976) measured points **extracted exactly from the PDF vector data** (marker centres), with axes calibrated from gridlines rasterized at 400 dpi.

Tag: [D-ag] read in this paper. [derived] my arithmetic.

## Rotor and conditions [D-ag]
- Rotor spacing 8-9 % of diameter. Up to 2800 RPM. In Mars hover V_tip ≈ **177 m/s** and M_tip ≈ **0.76** (p. 3970).
- Re_c ≈ 10³-10⁴. Fig. 2 shows Re_c peaking at ≈1.75×10⁴ near r/R ≈ 0.75-0.85 (p. 3970).
- JPL Space Simulator test: CO2 at ρ = 0.0175 kg/m³, T = 20 °C, **M_tip = 0.62 at 2600 RPM**, thrust **up to 13.25 N** (p. 3976).
- Table 1, MC2 vs JPL SS: ρ 0.017 vs 0.0185 kg/m³; T 223.2 vs 298.15 K; μ 1.130e-5 vs 1.504e-5 N s/m²; p 0.72 vs 1.04 kPa; a 233.13 vs 269.44 m/s. The paper notes a 13 % Mach decrease and 29 % Re decrease in the chamber relative to MC2 (p. 3973). (The density in Table 1 is 0.0185, while the text says 0.0175.)
- Table 2, Re/M ×10⁻⁴ at MC2: st1 1.074, st2 2.984, st3 4.176, st4 4.176, st5 3.451, st6 2.564, st7 1.825, st8 0.724 (r/R 0.091 … 0.991).
- Conclusion: FM is predicted **1.3-2.6 % higher on Mars (MC2) than measured in the chamber** over the design CT range (p. 3977).
- Design thrust coefficient range (hatched band in Figs 24 and 25): CT ≈ 0.015-0.020 [D-ag, read off the figure].

## clf5605 section data, OVERFLOW time-accurate with transition model, MC2 (Figs 10-11, read by eye, ±0.02 cl, ±0.005 cd) [D-ag]
| α [deg] | St5 cl (M0.40, Re 13,800) | St5 cd | St6 cl (M0.60, Re 15,400) | St6 cd | St8 cl (M0.80, Re 5,800) | St8 cd |
|---|---|---|---|---|---|---|
| −1 | 0.30 | 0.035 | 0.32 | 0.042 | −0.15 | 0.061 |
| 0 | 0.49 | 0.035 | 0.51 | 0.037 | 0.07 | 0.060 |
| 1 | 0.61 | 0.037 | 0.67 | 0.040 | 0.53 | 0.073 |
| 2 | 0.73 | 0.040 | 0.80 | 0.044 | 0.75 | 0.090 |
| 3 | 0.83 | 0.044 | 0.94 | 0.051 | 0.90 | 0.111 |
| 4 | 0.93 | 0.049 | 1.08 | 0.065 | 1.04 | 0.135 |
| 5 | 1.06 | 0.060 | 1.17 | 0.088 | 1.15 | 0.159 |
| 6 | 1.20 | 0.080 | 0.90 | 0.088 | 1.23 | 0.182 |
| 7 | 1.32 | 0.099 | 0.94 | 0.106 | 1.30 | 0.206 |
| 8 | 0.93 | 0.110 | 0.99 | 0.126 | 1.36 | 0.231 |
| 10 | 0.98 | 0.152 | 1.05 | 0.170 | 1.44 | 0.283 |
[derived]: clf5605 at Re ~1.4-1.5×10⁴, M 0.4-0.6 has cl ≈ 0.5 at α = 0 and dcl/dα ≈ 0.11-0.14 /deg (≈ 6.3-8 /rad, Mach-inflated) for α 0-4°. cd_min ≈ 0.035-0.037, (L/D)max ≈ 18-19 near α 2-4°, and stall/drop beyond ~5-7°. At M = 0.8 (Re 5,800) cd0 is ≈ 0.06 and L/D ≈ 8.
Background figures (McMasters & Henderson, reproduced as Figs 3-4): smooth airfoils lose performance sharply below Re ≈ 10⁵. A Schmitz flat plate gives (cl/cd)max ≈ 10 over Re 10⁴-10⁶ [D-ag, read off the log plot].

## Measured Ingenuity coaxial rotor hover data, JPL Space Simulator (Fig. 25 circles) [D-ag, vector-extracted]
Conditions: CO2, ρ = 0.0175 kg/m³, T = 20 °C, 2600 RPM, M_tip 0.62. CP = P/(ρA(ΩR)³), CT = T/(ρA(ΩR)²), A = rotor disk area (nomenclature, p. 3969). FM column = CT^1.5/(√2 CP) [derived]. It reaches 0.635 maximum, consistent with Fig. 24.
| CT | CP | FM [derived] |
|---|---|---|
| 0.00129 | 0.000993 | 0.03 |
| 0.00281 | 0.001115 | 0.09 |
| 0.00550 | 0.001164 | 0.25 |
| 0.00833 | 0.001407 | 0.38 |
| 0.01150 | 0.001776 | 0.49 |
| 0.01477 | 0.002253 | 0.56 |
| 0.01555 | 0.002321 | 0.59 |
| 0.01636 | 0.002507 | 0.59 |
| 0.01710 | 0.002561 | 0.62 |
| 0.01775 | 0.002710 | 0.62 |
| 0.01860 | 0.002897 | 0.62 |
| 0.01908 | 0.003030 | 0.62 |
| 0.01981 | 0.003169 | 0.62 |
| 0.02062 | 0.003347 | 0.63 |
| 0.02118 | 0.003433 | 0.64 |
| 0.02190 | 0.003725 | 0.62 |
| 0.02251 | 0.003913 | 0.61 |
| 0.02320 | 0.004110 | 0.61 |
| 0.02364 | 0.004237 | 0.61 |
| 0.02425 | 0.004408 | 0.61 |
Extraction accuracy ≈ ±0.00005 in CT and ±0.00002 in CP (marker centres are exact; the axis calibration is from raster gridlines).
[derived]: with the solidity from C_koning2018 (σ_coax ≈ 0.144 thrust-weighted), peak FM sits at CT/σ ≈ 0.14-0.15. Check: T = CT ρ A (ΩR)² = 0.0243 × 0.0175 × 1.150 × (164.7)² ≈ 13.3 N at 2600 rpm, which matches the paper's "up to 13.25 N". This confirms that **A is a single disk area (π·0.605²)**, CT is total coax thrust, and **CP is shaft power from motor power × 0.78** (2018 paper).

## Caveats
- The power is motor electrical power multiplied by an assumed constant 78 % drive efficiency (C_koning2018), not a measured shaft torque.
- At high CT the CAMRAD fully turbulent and transition models diverge (p. 3976).
- It is a coaxial rotor. For single-rotor BEMT validation, use Harrington's single-rotor data instead.
