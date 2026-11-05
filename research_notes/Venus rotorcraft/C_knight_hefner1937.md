# C_knight_hefner1937 — NACA TN 626 Static Thrust Analysis of the Lifting Airscrew (TABULATED hover data, 2/3/4/5 blades)

## Citation
Knight, Montgomery; Hefner, Ralph A. (1937). *Static Thrust Analysis of the Lifting Airscrew.* NACA Technical Note No. 626, Georgia School of Technology, December 1937. NTRS 19930081433.
PDF: https://ntrs.nasa.gov/api/citations/19930081433/downloads/19930081433.pdf

## What was read
- Text (pypdf OCR layer), pp. 1-17: theory, apparatus, test procedure, precision.
- **Definitions on pp. 9-10 and Tables I-VI (pp. 34-38) read directly from page images** rendered at 100-120 dpi. These tables are printed numbers, not digitized curves.

Tag: [D-ag] read in this report. [derived] mine.

## ⚠ Coefficient definitions (p. 9-10) [D-ag]
T = (ρ/2) π R² Ω² R² · C_T  and  Q = (ρ/2) π R² Ω² R³ · C_Q.
So **C_T(KH) = 2 · C_T(standard)** and **C_Q(KH) = 2 · C_Q(standard)**, where standard means T/(ρπR²(ΩR)²). σ = Bc/(πR) is standard: 2 × 2 in / (π × 30 in) = 0.0424, which matches Table I.
Check [derived]: 2-blade C_Q0(std) = 0.000054 gives c_d0 = 8 C_Q0/σ = 0.0102, close to the measured NACA 0015 cd_min = 0.0113 in Table V. This supports the factor of 2.

## Rotor geometry [D-ag] (p. 14)
- Diameter **5 ft** (R = 2.5 ft = 0.762 m). **2, 3, 4, 5 blades** (identical, interchangeable).
- **NACA 0015**, **constant 2-inch chord** (0.0508 m) from the tip in to r = 5 in (x = 0.167). Faired into a 3/4-in circle at r = 1.5 in. Hub diameter 3 in. Flapping hinges at r = 1 in. **No twist**, straight planform, semicircular tip.
- Blade angle θ is set relative to the **zero-thrust angle**, within ±0.05°.
- Speed ≈ **960 rpm** (p. 16), so ΩR ≈ 76.6 m/s [derived]. Tip Re ≈ 242,000: the profile was tested "at approximately the same Reynolds Number (242,000) as that of the rotor-blade tips" (p. 17).
- Precision (p. 17): thrust ±1 %, torque ±1 %, minimum torque ±2 %, rotation rate ± (value illegible in OCR, not checked on the image), blade angle ±0.05°.
- Tested in the Georgia Tech 9-ft wind tunnel (static), with the shaft horizontal.

## Tables I-IV, measured static thrust (as printed, KH coefficients) + standard conversion [D-ag; std/FM columns derived]
### 2 blades, σ = 0.0424 (Table I)
| θ° | C_T (KH) | C_Q (KH) | C_T std | C_Q std | FM [derived] |
|---|---|---|---|---|---|
| 0 | 0 | 0.000108 | 0 | 0.0000540 | 0 |
| 1 | 0.000280 | 0.000111 | 0.000140 | 0.0000555 | 0.02 |
| 2 | 0.000873 | 0.000125 | 0.000437 | 0.0000625 | 0.10 |
| 4 | 0.00248 | 0.000191 | 0.00124 | 0.0000955 | 0.32 |
| 6 | 0.00442 | 0.000316 | 0.00221 | 0.000158 | 0.47 |
| 8 | 0.00650 | 0.000494 | 0.00325 | 0.000247 | 0.53 |
| 10 | 0.00847 | 0.000691 | 0.00424 | 0.000346 | 0.56 |
| 12 | 0.00990 | 0.000878 | 0.00495 | 0.000439 | 0.56 |

### 3 blades, σ = 0.0636 (Table II)
| θ° | C_T (KH) | C_Q (KH) | FM [derived] |
|---|---|---|---|
| 0 | 0 | 0.000185 | 0 |
| 2 | 0.00102 | 0.000206 | 0.08 |
| 4 | 0.00298 | 0.000300 | 0.27 |
| 6 | 0.00548 | 0.000474 | 0.43 |
| 8 | 0.00833 | 0.000735 | 0.52 |
| 10 | 0.01125 | 0.001048 | 0.57 |
| 12 | 0.01370 | 0.001357 | 0.59 |

### 4 blades, σ = 0.0849 (Table III)
| θ° | C_T (KH) | C_Q (KH) | FM [derived] |
|---|---|---|---|
| 0 | 0 | 0.000268 | 0 |
| 1 | 0.000287 | 0.000274 | 0.01 |
| 2 | 0.001042 | 0.000300 | 0.06 |
| 3 | 0.00214 | 0.000338 | 0.15 |
| 4 | 0.00338 | 0.000410 | 0.24 |
| 5 | 0.00473 | 0.000499 | 0.33 |
| 6 | 0.00645 | 0.000620 | 0.42 |
| 7 | 0.00792 | 0.000743 | 0.47 |
| 8 | 0.00981 | 0.000920 | 0.53 |
| 9 | 0.01182 | 0.001162 | 0.55 |
| 10 | 0.01382 | 0.001395 | 0.58 |
| 11 | 0.01596 | 0.00171 | 0.59 |
| 12 | 0.01745 | 0.00191 | 0.60 |

### 5 blades, σ = 0.1061 (Table IV)
| θ° | C_T (KH) | C_Q (KH) | FM [derived] |
|---|---|---|---|
| 0 | 0 | 0.000238 | 0 |
| 2 | 0.001181 | 0.000270 | 0.08 |
| 4 | 0.00362 | 0.000396 | 0.28 |
| 6 | 0.00694 | 0.000680 | 0.43 |
| 8 | 0.01103 | 0.001086 | 0.53 |
| 10 | 0.01548 | 0.001635 | 0.59 |
| 12 | 0.0200 | 0.00228 | 0.62 |
(The tables also list C_Q′ = C_Q − C_Q0, T_σ = C_T/σ², Q_σ = C_Q/σ³, Q_σ′ and θ_σ = θ(rad)/σ, all consistent with the columns above. The odd ordering C_Q0(5 blades) = 0.000238 < C_Q0(4 blades) = 0.000268 is as printed.)

## NACA 0015 section data at Re = 242,000 (Tables V-VI, 6×72-in airfoil) [D-ag]
Position A (α∞ deg, C_L, C_D0): 12.65, 0.873, 0.0911 | 11.55, 0.906, 0.0504 | 10.60, 0.899, 0.0383 | 8.70, 0.830 (glyph unclear; OCR read .870), 0.0284 | 6.95, 0.711, 0.0222 | 5.30, 0.534, 0.0172 | 3.65, 0.351, 0.0131 | 1.95, 0.185, 0.0113 | 0.25, 0.026, 0.0113 | −1.45, −0.138, 0.0102 | −3.10, −0.302, 0.0136 | −4.75, −0.501, 0.0165 | (below from OCR, consistent with the ΔC_D column) −6.40, −0.693, 0.0205 | −8.10, −0.821, 0.0265 | −9.95, −0.915, 0.0350 | −10.90, −0.948, 0.0413 | −11.90, −0.939, 0.0710.
Position B: 12.00, 0.955, 0.0548 | 11.00, 0.944, 0.0387 | 10.05, 0.909, 0.0331 | 8.25, 0.819, 0.0262 | 6.55, 0.663, 0.0210 | 4.90, 0.475, 0.0160 | 3.20, 0.304, 0.0132 | 1.55, 0.143, 0.0117 | −0.20, −0.012, 0.0113 | −1.85, −0.174, 0.0121 | −3.55, −0.351, 0.0141 | −5.15, −0.561, 0.0177 | (OCR) −6.80, −0.734, 0.0226 | −8.60, −0.831, 0.0286 | −10.50, −0.903, 0.0397 | −11.45, −0.910, 0.0533 | −12.55, −0.870, 0.0968.
[derived]: lift slope ≈ 0.096-0.100 /deg (5.5-5.7 /rad); cd_min ≈ 0.0113; cl_max ≈ 0.91-0.96 at α ≈ 11-12°. The text (p. 17) says a profile-drag variation coefficient ε = 0.75 fits the section data, but **ε = 1.25 was needed to match the rotor torque**.

## Why this dataset matters
This is a fully tabulated, single-rotor, untwisted, constant-chord hover dataset with its own section polar at matching Re. It is cleaner for a BEMT unit test than the digitized Harrington plots. Recommended test: b = 2-5, R = 0.762 m, c = 0.0508 m, root cutout x = 0.167, θ = 0-12°, NACA 0015 polar above. Compare C_T(std) and C_Q(std) per θ.

## Caveats
- The 1937 balance and rotor are small (5 ft), with flapping hinges. Coning was not reported.
- Tip losses and the root fairing (r = 1.5-5 in) are not modelled in simple BEMT; the fairing is a minor contribution.
