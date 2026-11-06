# Material selection — aircraft bracket at 300 °C

`python 01_Ansys/scripts/bracket_material_report.py` [K]. Candidates and every value with its source and tag: `aerokit.bracket.matdata` and the cards in this folder. Relative mass = mass of the part in that material / mass in the best material for the same load and stiffness or strength target (Ashby index; `aerokit.materials.selection`). The geometry-specific answer (real layouts, real stresses) is in each `out/<case>/report.md`; this table is the screening step before it.

## Screen: maximum service temperature ≥ 300 °C

- Structural Steel (Ansys Engineering Data default): Tmax 400 °C [Y] → **passes**
- 17-4PH H1025 (wrought data; L-PBF route): Tmax 316 °C [S] → **passes**
- Ti-6Al-4V (L-PBF, stress relieved / HIP): Tmax 350 °C [D] → **passes**
- Inconel 718 (L-PBF, solution + double age): Tmax 700 °C [D] → **passes**
- Scalmalloy (Al-Mg-Sc, L-PBF): Tmax 150 °C [S] → **fails**

## Comparison at 300 °C (relative mass, 1 = lightest)

| Material | ρ (kg/m³) | E (GPa) | Fty (MPa) | Strong beam | Stiff beam | CO₂ (kg/kg) |
|---|---|---|---|---|---|---|
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 4410 | 96.8 | 590 | 1.00 | 1.00 | 46.5 |
| Inconel 718 (L-PBF, solution + double age) | 8150 | 184.0 | 1096 | 1.22 | 1.34 | 11.6 |
| 17-4PH H1025 (wrought data; L-PBF route) | 7806 | 173.0 | 816 | 1.43 | 1.32 | 5 |
| Structural Steel (Ansys Engineering Data default) | 7850 | 182.7 | 163 | 4.20 | 1.30 | 1.8 |
| Scalmalloy (Al-Mg-Sc, L-PBF) (fails screen) | 2670 | 29.0 | 60 | 2.78 | 1.11 | 128 |

## Effect of temperature on the strength-limited ranking

| Material | Rel. mass 20 °C | Rel. mass 300 °C | Fty factor | Factor source |
|---|---|---|---|---|
| Ti-6Al-4V (L-PBF, stress relieved / HIP) | 1.07 | 1.00 | 0.624 | MIL-HDBK-5J Fig. 5.4.1.1.1 (annealed wrought Ti-6Al-4V, 1/2 h) at 572 F for Fty/Ftu; E(300 C)/E(RT) = 0.88: TIMET 6-4 sheet Table 2 gives 107-122 GPa at 20 C and 95-111 at 230 C (ratio ~0.90 at 230 C, extrapolated ~0.88 at 300 C); laser-DED data (Ivanov 2021) give 0.97 [D-ag, range] [D/D-ag] |
| Inconel 718 (L-PBF, solution + double age) | 1.73 | 1.22 | 0.957 | Special Metals INCONEL 718 bulletin (2007): Table 4 E 29.0 -> 26.7 Msi at 600 F; Table 19 (hot-rolled, annealed + aged) YS 163.0 -> 156.0 ksi, UTS 198.0 -> 183.5 ksi at 600 F (316 C, used for 300 C: slightly conservative) [D-ag]; wrought ratios applied to L-PBF [Y] [D-ag] |
| 17-4PH H1025 (wrought data; L-PBF route) | 1.82 | 1.43 | 0.816 | MIL-HDBK-5J Fig. 2.6.9.2.1 (17-4PH bar H900-H1075; the unlabeled curve is Fty by elimination) and Fig. 2.6.9.1.4 (E of H900, proxy for H1025) at 572 F [D] |
| Structural Steel (Ansys Engineering Data default) | 4.60 | 4.20 | 0.651 | Fty: EN 10028-2 minimum Rp0.2 of P235GH (t <= 16 mm) 153 MPa at 300 C vs 235 MPa at RT, ratio 0.651 (Salzgitter reproduction, read by sub-agent 2026-11-04) [D-ag]; E and Ftu: MIL-HDBK-5J Fig. 2.3.1.1.4 / 2.3.1.1.1 AISI low-alloy steels at 572 F (proxy) [D curve, Y use] [D-ag/Y] |
| Scalmalloy (Al-Mg-Sc, L-PBF) | 1.00 | 2.78 | 0.122 | Colibrium M2 Series 5 Al-Mg-Sc CMDS Rev B (2025-08-21), elevated-temperature table, DA, horizontal: 300 C E 29 GPa, YS 60 MPa, UTS 103 MPa (RT E 69 GPa) [D-ag] [D-ag] |

## Recommendation (screening level)

**Ti-6Al-4V (L-PBF, stress relieved / HIP)** gives the lightest strength-limited bracket among the 3-D printable candidates that pass the 300 °C screen (relative mass 1.00). Three materials for the comparison table: the baseline Structural Steel, the lightest printable (above) and the next printable alternative — Inconel 718 (L-PBF, solution + double age), 17-4PH H1025 (wrought data; L-PBF route). Least embodied CO₂ per strength (beam, cradle to gate): 17-4PH H1025 (wrought data; L-PBF route) — the use phase (fuel) still dominates the life total, see the eco audits.

Price (stock or powder, EUR/kg): Structural Steel 0.77 [D-ag]; 17-4PH H1025 NOT FOUND; Ti-6Al-4V 70.6 [D-ag]; Inconel 718 NOT FOUND; Scalmalloy NOT FOUND. Sources in the cards; AM machine time and post-processing are not included.

Figure: `fig_relative_mass.png` — mass of a strength-limited bracket arm (index Fty^2/3/ρ) relative to the best passing material at 300 °C, at 20 °C and at 300 °C; '(fails)' = fails the 300 °C screen; audit 0 HATA

Files: `comparison.csv` (all columns), `materials_engineering_data.xml` (Ansys Engineering Data import), `card_*.md` (one card per material).
