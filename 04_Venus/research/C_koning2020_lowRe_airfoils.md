# C_koning2020_lowRe_airfoils — Low-Re airfoil data for BEMT (clf5605, cambered and flat plates)

## Primary citation
Koning, Witold J. F.; Romander, Ethan A.; Johnson, Wayne (2020). *Optimization of Low Reynolds Number Airfoils for Martian Rotor Applications Using an Evolutionary Algorithm.* AIAA SciTech 2020 Forum, AIAA 2020-0084. DOI: 10.2514/6.2020-0084.
PDF: https://rotorcraft.arc.nasa.gov/Publications/files/koningAIAA2020.pdf
Cross-referenced (separate notes): C_koning2019 (clf5605 OVERFLOW polars), C_johnson2020_msh (Table 7 airfoil L/D), C_koning2018 (clf5605 geometry).

## What was read
pypdf text of 28 pages: abstract and Sec. II-B (sharp leading-edge performance). Page 7 Figs 8-9 were rendered at 110 dpi and read by eye. The optimization results tables were not read in detail.

Tag: [D-ag] read in the cited paper. [derived] mine.

## Numbers [D-ag]
- Conventional airfoils are "a suboptimal choice" around and below **Re_c = 50,000** (laminar separation without reattachment). Flat plates outperform conventional sections for **Re_c ≲ 80,000** (Hoerner, Laitone, Pelletier & Mueller).
- Circular-arc airfoils with ~5 % camber outperform both conventional airfoils and flat plates (several references).
- Freestream turbulence sensitivity of conventional sections: NACA 0015 cl_max +30 % at Re 250,000 (Hoffmann); NACA 0012 L/D −49 % at Re 20,700 (Laitone); NACA 0012 cl_max and L/D +52 % and +454 % at Re 5,300 (Wang et al.). Plates are comparatively insensitive (Okamoto, Laitone, Pelletier & Mueller).
- Substituting a cambered plate into the MH rotor gave **+7 % max rotor thrust and +5 % FM** over the design C_T range (Koning et al., cited as ref. 9).
- Optimized double-edged plate (cl ≈ 0.65 at M 0.3 and 0.5): L/D **+7-12 %** vs cambered plate and **+15-28 %** vs the MH outboard airfoil. Abstract: peak L/D gains of 17-41 % vs conventional at similar cl.
- **Fig. 8-9 (Hoerner data, constant α; read by eye, ±0.02):**
  - N60 (t/c 12.4 %, f/c 4.0 %): cl ≈ 0.54 and **cd ≈ 0.13-0.14** at Re 2-5×10⁴. Through the critical region (~7×10⁴-1.2×10⁵) it jumps to cl ≈ 1.05 and **cd ≈ 0.03** above ~1.5×10⁵.
  - Cambered plate (t/c 3 %, f/c 5.8 %): **cl ≈ 0.88-0.95 and cd ≈ 0.035-0.04** across Re 2×10⁴-10⁶, with no critical-Re jump.
  - The laminar flat-plate skin friction 2C_f line is ≈ 0.03 at 10⁴, falling to ≈ 0.01 at 10⁵ (log scale, rough reading).

## Compiled low-Re BEMT parameters (from the four notes; each value tagged to its source)
| Section | Re, M | cl_α | cd0 / cd_min | (L/D)max | Source |
|---|---|---|---|---|---|
| clf5605 (5 % t, 4.9 % camber) | 1.38×10⁴, M 0.4 | ≈ 0.11-0.12 /deg [derived from Fig. 10] | 0.035 | ≈ 19 [derived] | C_koning2019 [D-ag] |
| clf5605 | 1.54×10⁴, M 0.6 | ≈ 0.14 /deg (Mach-inflated) [derived] | 0.037 | ≈ 18 [derived] | C_koning2019 |
| clf5605 | 5.8×10³, M 0.8 | – | 0.060 | ≈ 8 [derived] | C_koning2019 |
| clf5605 (design cl 0.65) | 1.1-1.7×10⁴, M 0.35-0.52 | – | – | **18.34** | C_johnson2020_msh Table 7 |
| circular arc | same | – | – | 20.51 | MSH Table 7 |
| cambered plate | same | – | – | 23.70 | MSH Table 7 |
| double-edged plate | same | – | – | 23.43 | MSH Table 7 |
| cambered plate 3 %/5.8 % | 2×10⁴-10⁶ | – | ≈ 0.035-0.04 at fixed α | – | this paper, Fig. 9 (Hoerner) |
| Schmitz flat plate | 10⁴-10⁶ | – | – | ≈ 10 | C_koning2019 Fig. 3 |
| NACA 0012 quadratic drag (high Re, Harrington-type) | ~10⁶ | 5.73 /rad (Harrington's a, C_harrington1951) | cd0 not read (Harrington's δ0 is not printed in the text); Syal uses **d1 = 0.021, d2 = 0.65** in cd = cd0 + d1 α + d2 α² | – | C_syal2008_coaxial |

## Caveats
- The Venus 50-60 km rotor regime is probably **Re ~ 10⁵-10⁶**, not 10⁴. [derived, rough]: ρ ≈ 1 kg/m³, V ≈ 150 m/s, c ≈ 0.1 m, μ_CO2 ≈ 1.5×10⁻⁵ Pa s (μ value assumed, not read) give Re ≈ 10⁶. Low-Re data matters only for small rotors or low tip speeds. Check the team's atmosphere model.
- The clf5605 polars are 2D RANS (OVERFLOW) at Mars conditions, not wind-tunnel data.
- The Hoerner plate data are at a single, unstated α.
