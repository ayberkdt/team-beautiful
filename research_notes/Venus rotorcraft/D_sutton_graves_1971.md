# D_sutton_graves_1971 — Stagnation-point convective heating constant K (Earth, Mars, Venus)

## Citation
Sutton, K. & Graves, R. A., Jr. (1971). *A General Stagnation-Point Convective-Heating
Equation for Arbitrary Gas Mixtures.* NASA Technical Report TR R-376, NASA Langley
Research Center, November 1971. NTRS ID 19720003329.
URL: https://ntrs.nasa.gov/citations/19720003329
PDF: https://ntrs.nasa.gov/api/citations/19720003329/downloads/19720003329.pdf

## What I read (2026-11-04)
Downloaded the full 67-page NTRS PDF; extracted text with PyMuPDF and rendered page images
of PDF p.15 (report p.13, eqs. 32–35) and PDF p.41 (report p.39, Table II) to check the
OCR. Also read the summary, symbol list, eq. (41)–(44) region and Table I.
Local copy: `D:\tmp_ideathon\venus\downloads\eng\SG1971.pdf`.

## Equation as defined in the report
- Eq. (33), report p.13: **K = q̇_w · sqrt(R / p_s) / (h_s − h_w)** [D-ag]
  - q̇_w: convective heating rate, W/m² (symbol list) [D-ag]
  - R: "equivalent body radius", m [D-ag]
  - p_s: stagnation pressure, **atm** (1 atm = 101.325 kN/m²) [D-ag]
  - h_s − h_w: stagnation minus wall enthalpy (symbol list prints MJ/kg, but the K units
    kg/(s·m^{3/2}·atm^{1/2}) only close dimensionally with h in J/kg; I checked
    numerically — see below).
- Units of K in Table II header: **kg/(s·m^{3/2}·atm^{1/2})** [D-ag]
- Eq. (44) (report p.16): mixture summation **1/K² = Σ c_i / K_i²** (c_i = mass
  fraction), valid when wall Prandtl numbers of mixture and components are similar [D-ag].
  The report says N_Pr,w ≈ 0.69 for gases of planetary-entry interest [D-ag].
- Validity range of the correlation: enthalpies 2.3–116.2 MJ/kg, pressures 0.001–100 atm,
  wall temperatures 300 and 1111 K [D-ag, Summary p.1]. Radiative heating neglected
  [D-ag, symbol-list page note].
- Venus atmosphere described as primarily a binary CO2/N2 mixture [D-ag, Introduction].

## Table II (report p.39) — K values read from the rendered page image
| Gas (mass fractions)                 | K, kg/(s·m^1.5·atm^0.5) | avg / max error % |
|--------------------------------------|------|------|
| N2                                   | 0.1112 | 3.6 / 10.0 | [D-ag]
| CO2                                  | 0.1210 | 3.4 / 8.4 | [D-ag]
| Ar                                   | 0.1495 | 2.7 / 7.5 | [D-ag]
| 0.2320 O2–0.7680 N2 (air)            | 0.1113 | 3.3 / 9.8 | [D-ag]
| 0.8500 CO2–0.1500 N2                 | 0.1173 | 3.0 / 8.5 | [D-ag]
| 0.5000 CO2–0.5000 N2                 | 0.1131 | 2.7 / 7.4 | [D-ag]
| 0.1345 CO2–0.8655 N2                 | 0.1113 | 3.0 / 9.4 | [D-ag]
| 0.3626 CO2–0.3077 N2–0.3297 Ar       | 0.1218 | 2.7 / 9.1 | [D-ag]
| 0.1339 CO2–0.8525 N2–0.0136 Ar       | 0.1118 | 2.9 / 9.6 | [D-ag]

No row in Table II is exactly the modern Venus composition (96.5 % CO2 / 3.5 % N2 by
volume); the report predates Pioneer Venus.

## Conversion to the common SI form q = k · sqrt(ρ∞/R_n) · V∞³  (my derivation, not in the report)
Assumptions (hypersonic, cold wall): p_s ≈ ρ∞V∞² (Newtonian), h_s − h_w ≈ V∞²/2, p_s
converted from Pa to atm. Then
**k = K / (2·sqrt(101325)) = K / 636.63**, k in kg^0.5/m (i.e. W/m² when ρ in kg/m³,
R_n in m, V in m/s).

Numerical check of units (my calc): air, ρ = 1e-4 kg/m³, V = 7 km/s, R = 1 m →
TR form 0.1113·sqrt(0.04836 atm/1 m)·24.5e6 J/kg = 5.997e5 W/m²; SI form
1.748e-4·0.01·7000³ = 5.997e5 W/m². Consistent.

| Atmosphere | K used | k (SI, kg^0.5/m) | Tag |
|---|---|---|---|
| Earth air (Table II row) | 0.1113 | **1.748e-4** | [derived from D-ag] |
| Pure CO2 (Table II) | 0.1210 | 1.901e-4 | [derived from D-ag] |
| **Venus** 96.5 % CO2 / 3.5 % N2 by volume → mass fraction CO2 0.977, via eq.(44) from CO2 and N2 rows | 0.12075 | **1.897e-4** | [derived from D-ag; composition is an input I did not re-verify in this note] |
| Mars 95.3 CO2 / 2.7 N2 / 1.6 Ar vol. → eq.(44) | 0.1211 | 1.902e-4 | [derived from D-ag] |
| 0.85 CO2 / 0.15 N2 mass (Table II, closest tabulated) | 0.1173 | 1.843e-4 | [derived from D-ag] |

Widely circulated textbook constants (Earth 1.7415e-4, Mars 1.9027e-4, Venus 1.896e-4)
agree with these to <0.5 %, but I did **not** find them in a primary source this session
[A]. A web-search summary also cited 1.74e-4 and 1.83e-4 and 1.63e-4 (Chapman) for Earth
[A, arXiv 2107.13513 snippet only].

## Caveats
- Convective only. For Venus entry at ~11 km/s the shock-layer radiative heating is
  significant/dominant; add a separate radiative term (see D_tauber_sutton_1991.md and
  D_venus_entry_heating.md). An NTRS search snippet (Ames study) states radiation
  predominates for Venus, convection for Mars [A].
- Correlation accuracy is stated per gas: ~3 % average, up to ~8–10 % max for CO2/N2 rows
  [D-ag]. The ρV²/V²/2 conversion adds further approximation (p_s ≈ ρV²(1 − ε/2) in
  reality, so true p_s is a few % lower → k a few % lower).
- Laminar, equilibrium, cold-wall stagnation point; no ablation blowing.
- R in the report is "equivalent body radius" (the nose radius for a sphere-cone).
