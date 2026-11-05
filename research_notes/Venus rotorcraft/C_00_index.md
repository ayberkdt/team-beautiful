# C_00_index — Rotorcraft precedents and BEMT validation data (Venus rotorcraft, LuGus "Fly on Venus")

Compiled 2026-11-04. Tags: **[D-ag]** = read in the source itself (text, table, or my digitization of a figure in it); **[A]** = only from abstracts, snippets or secondary pages; **[derived]** = my arithmetic from [D-ag] values.
Local PDF copies: `D:\tmp_ideathon\venus\downloads\rotor\` (data, not committed).

## Files
| File | Source | What it gives | Read level |
|---|---|---|---|
| C_harrington1951.md | Harrington, NACA TN 2318 (1951) | **BEMT validation set 1**: coax + single hover C_T-C_Q for rotor 1 (R 3.81 m, 2+2 blades, tapered, untwisted, σ 0.027/0.054) and rotor 2 (c = 18 in, σ 0.076/0.152), digitized | full text + figures digitized [D-ag] |
| C_knight_hefner1937.md | Knight & Hefner, NACA TN 626 (1937) | **BEMT validation set 2 (tabulated, best for unit test)**: 2/3/4/5-blade, R 0.762 m, c 0.0508 m, NACA 0015, untwisted; C_T, C_Q vs θ; NACA 0015 polar at Re 242k. **Their C_T, C_Q are 2× standard** | tables read [D-ag] |
| C_koning2019.md | Koning, Johnson, Grip, AIAA J 2019 | **BEMT validation set 3 (low Re, coax)**: 20 measured Ingenuity C_T-C_P points (JPL chamber), vector-extracted; clf5605 cl/cd vs α at Re 5.8k-15k | full text [D-ag] |
| C_koning2018.md | Koning, Johnson, Allan, AHS 2018 | Ingenuity blade geometry table (r/R, c/R, t/c, twist) and airfoil thickness/camber | full text [D-ag] |
| C_balaram2018.md | Balaram et al., AIAA 2018-0023 | Ingenuity design: 1.8 kg, 1.21 m, 2800 rpm max, battery 6 cells/35.75 Wh, 360-510 W, thermal, sensors | full text [D-ag] |
| C_grip2018.md | Grip et al., AIAA 2018-1849 | Mars helicopter GNC: 40 % thrust margin, wind limits, loop crossovers and margins, 500 Hz | full text [D-ag] (2019 paper not obtained) |
| C_ingenuity_jpl.md | NASA/JPL pages and blog | Flight record: 72 flights, 128.8 min, 17.0 km, 24 m, 10 m/s; rpm raised 2537→2700; thrust margin 30 % → 8 % | official pages via fetch [D-ag], some [A] |
| C_johnson2020_msh.md | Johnson et al., NASA/TM-2020-220485 | Mars Science Helicopter: hexacopter 0.64 m R, 17.7-31.2 kg, σ, rpm, power, battery tech, airfoil L/D table, design rules | full text [D-ag] |
| C_delaune2022_mahd.md | Delaune et al., IEEE Aero 2022 | Mid-air helicopter delivery (jetpack): 600 m separation, 3 s free fall, 200 m hover, 12 s spin-up, 275 kg entry | full text [D-ag] |
| C_pensado2025_dragonfly_edl.md | Pensado et al., SciTech 2025 | Dragonfly EDL: rotors posed in airflow under main parachute, rotor despin, **release at 1000-800 m, < 2.9 m/s** | full text [D-ag] |
| C_lorenz2018_dragonfly.md | Lorenz et al., APL Tech Dig 2018 | Dragonfly concept: octocopter, Titan ρ 5.4, 420 kg → ~2 kW at 10 m/s, MMRTG 70 W | full text [D-ag] |
| C_langelaan2017_titan.md | Langelaan, Schmitz, Palacios, Lorenz, IEEE Aero 2017 | TREx 350 kg 8-rotor: 1.87 kW hover, FM 0.72, aeroshell rotor-packing formula, κ_ind 1.15 | full text [D-ag] |
| C_coleman1997.md | Coleman, NASA TP 3675 | Coax survey: Harrington Re_0.75 table, 7 % scale effect, 5 % theory error, Levin data | OCR text [D-ag] |
| C_syal2008_coaxial.md | Syal (Leishman group), UMD MS thesis 2008 | κ_int table (√2, 1.2808, 1.2810, 1.2657); Harrington validation (κ_int 1.28, d1 0.021, d2 0.65) | decoded text [D-ag] (JAHS paper not obtained) |
| C_koning2020_lowRe_airfoils.md | Koning, Romander, Johnson, SciTech 2020 + compilation | Low-Re airfoil behaviour; compiled cl_α, cd0 and L/D table across sources | text + figure by eye [D-ag] |
| C_young2026_venus_aerial.md | Young, Dominguez, Schatzman, VFS 2026 | NASA Ames Venus aerial explorer survey: no 50-60 km rotorcraft concept; technology challenges | full text [D-ag] |
| C_husseyin2016_cyclocopter.md | Husseyin, NASA Ames intern report | Venus stopped-rotor cyclocopter (RotCFD); its "60 km" atmosphere table looks wrong | partial [D-ag] |
| C_yatsenko_vorontsov_mai.md | Yatsenko & Vorontsov (MAI) 2021-2024 | Only explicit Venus multirotor concept found: 15 kg, up to 7 per Vega-type probe | **[A] only** |

## Key numbers (with tags)
**Ingenuity:** mass 1.8 kg [D-ag]; coax D 1.21 m [D-ag]; max 2800 rpm [D-ag]; flew ≤ 2537 rpm then 2700 rpm [D-ag]; tip M ≤ 0.6 design / 0.62 chamber at 2600 rpm / ~0.76-0.8 at 2800 rpm on Mars [D-ag]; σ = 0.148 (MSH TM) [D-ag], 0.144 thrust-weighted from the chord table [derived]; airfoil clf5605 (t/c 5 %, camber 4.9 %) [D-ag]; Re ≈ 10³-2×10⁴ [D-ag]; measured FM_max ≈ 0.63 at C_T ≈ 0.021 (JPL chamber) [D-ag/derived]; battery 6 × Sony VTC4, 273 g, 35.75 Wh EOL, ~10 Wh for flight [D-ag]; 360 W continuous / 510 W peak assumed, 480 W continuous tested [D-ag]; "≈350 W average" (NASA page) [D-ag]; battery kept > −15 °C, warmed to 5 °C before flight; nights −100 °C or lower [D-ag]; ≥ 40 % thrust margin design [D-ag]; flight record 72 flights, 128.8 min, 17.0 km, 24.0 m, 10 m/s [D-ag].
**MSH:** hexacopter, 6 × 4-blade rotors of R 0.64 m (D 1.28 m) [D-ag]; 17.7 kg baseline at 2.8 kW; 31.2 kg max-capability at 6.2 kW [D-ag]; C_T/σ 0.11-0.115, M_tip 0.7-0.8, battery pack 230 Wh/kg [D-ag]; cambered/double-edged plates give L/D ≈ 23.5 vs 18.3 for clf5605 [D-ag].
**Mid-air deployment:** MAHD separation 600 m AGL, 3 s free fall, hover at 200 m, 12 s rotor spin-up [D-ag]. Dragonfly: rotors posed and spun under the 16.7 m main parachute, release at 1000-800 m and < 2.9 m/s [D-ag].
**Dragonfly/Titan:** ρ 5.4 kg/m³, g 1.35 m/s² [D-ag]; 420 kg → "a little over 2 kW" at 10 m/s [D-ag]; TREx 350 kg: 1.87 kW hover, FM 0.72, tip M 0.18, Re 2×10⁶ [D-ag]; flight power per kg ~40× lower than Earth [D-ag]. Rotor D 1.35 m and lander mass ~875 kg remain **[A]/unverified**.
**Coaxial interference:** ideal κ_int = 1.2808 (lower rotor in the contracted upper wake, equal thrust) and 1.2657 (torque-balanced) [D-ag, Syal thesis]; Harrington rotor 1 BEMT total κ 1.34-1.38, giving κ_int ≈ 1.26 [D-ag]. Coax/single FM_max 0.635/0.615 (Harrington) [D-ag]. Ingenuity coax benefit "5-8 %" over a single rotor of the same blade number and area (CAMRAD) [D-ag]. **The "1.16" value in the brief was not found in any source read.**
**Harrington rotor 1:** R 3.81 m, b 2+2, c(r) ≈ 12.43 − 0.0534 r [in] (c_root/c_tip 2.92), untwisted, NACA 00xx t/c 30 → 15 %, spacing 9.5 % D, ΩR 500 ft/s, Re_0.75 1.3×10⁶; C_Q0 = 0.0000777 (coax), so c_d0 ≈ 0.0115 [D-ag + derived].
**Knight & Hefner:** 2-blade σ 0.0424, θ 8°: C_T(std) 0.00325, C_Q(std) 0.000247, FM 0.53; 4-blade σ 0.0849, θ 12°: 0.008725 / 0.000955, FM 0.60 [D-ag + derived conversion].

## Gaps / not obtained
- Leishman & Ananthan 2008 JAHS: not free. The Syal 2008 thesis (same group) was used instead.
- Grip et al. 2019 *Flight Control System…*: the JPL link returned HTML. Not read.
- MAI Venus multirotor papers: TLS certificate error and 403. Only press-level [A] numbers.
- Venus 50-60 km atmosphere: not in scope. Do **not** use Husseyin's Table 1 (ρ = 1.225 at "60 km" looks wrong). Note that the Venus rotor Re at 50-60 km is likely 10⁵-10⁶ [derived, rough], so Harrington/Knight-Hefner Re (2×10⁵-3×10⁶) is closer to Venus than Ingenuity's Re.
