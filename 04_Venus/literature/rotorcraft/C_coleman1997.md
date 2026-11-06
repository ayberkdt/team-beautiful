# C_coleman1997 — A Survey of Theoretical and Experimental Coaxial Rotor Aerodynamic Research

## Citation
Coleman, Colin P. (1997). *A Survey of Theoretical and Experimental Coaxial Rotor Aerodynamic Research.* NASA Technical Paper 3675, NASA Ames Research Center, March 1997. NTRS 19970015550.
PDF: https://ntrs.nasa.gov/api/citations/19970015550/downloads/19970015550.pdf

## What was read
pypdf text (OCR layer of the scan): nomenclature, the US research section (Taylor, Harrington, Dingeldein) with Table 1, the Russian "Helicopters" equivalent-solidity method, the Levin results, and the Nagashima optimum-sharing section with Fig. 32 labels. Figures were not digitized.

Tag: [D-ag] read in this report. [derived] mine.

## Numbers [D-ag]
**FOM definition (p. 10):** FOM = C_T^{3/2}/(√2 C_Q), with C_T = (T_upp + T_low)/(ρ(ΩR)² πR²) and C_Q = (Q_upp + Q_low)/(ρ(ΩR)² πR³). This is the same total-system normalization as Harrington.

**Table 1 — Harrington test conditions with Re_0.75** (useful because Harrington does not state Re):
| Rotor | Config | σ | V_tip [ft/s] | Re_0.75 |
|---|---|---|---|---|
| 1 | single lower / upper | 0.027 | 500 | 1.3×10⁶ |
| 1 | coaxial | 0.054 | 500 / 450 / 327 | 1.3 / 1.1 / 0.8 ×10⁶ |
| 2 | single lower | 0.076 | 392 / 262 | 2.8 / 1.9 ×10⁶ |
| 2 | coaxial | 0.152 | 392 / 327 | 2.8 / 2.3 ×10⁶ |
- Rotor 1: H/D = **0.093** (Harrington text: 2.33 ft = 9.5 % D), tapered in planform and thickness, max disc loading 3.3 lb/ft² (158 N/m²). Rotor 2: H/D = 0.080, max disc loading 2.5 lb/ft² (120 N/m²). Both 25 ft (7.62 m) diameter and **untwisted** (p. 10: "Two untwisted 25 ft (7.62 m) diameter rotors"). This confirms rotor 2 is untwisted too.
- Scale effect at 327 ft/s (Re_0.75 = 0.8×10⁶): **~7 % more power** for a given thrust.
- Rotor 2 coax: the equivalent-solidity theory predicted on average **~5 % more power** than measured, decreasing to zero at the highest C_T.
- Dingeldein (forward flight, rotor 1): coax needed up to **14 % more power** than a single rotor of equivalent solidity.
- Taylor 1950: 0.509 m coax, H/D 0.17, σ 0.08, Re_0.75 = 8.25×10⁴. Tip vortices of upper and lower rotors keep separate identities.
- "Helicopters" (Russian) method: C_Q = (C_Qpr) + 0.79 C_T^{3/2} J₀, where J₀ is an induced-power correction (Fig. 11 axis 1.01-1.12 vs twist and taper). Momentum with H/D = 0.1 gives C_Tlow/C_Tupp = 0.86. Levin's 2.034 m model (σ 0.0445, H/D 0.0985, −12° twist) measured 0.87.
- Levin: coax induced losses "21% lower than for a single rotor of the same diameter and doubled solidity" at H/D = 0.0985.
- Nagashima interference factors: k = 1 + (2H/D)/√(1 + 4H²/D²), k′ = 2 − k (Fig. 32). The optimal thrust-sharing ratio is roughly the contraction ratio of the upper wake at the lower rotor.

## Caveats
- The OCR text is imperfect, so equation forms (e.g. the 0.79 coefficient and J₀) should be checked against the scanned page before use.
- No "κ_int = 1.16" appears in this report. The theoretical κ_int values (1.28, √2) are in C_syal2008_coaxial.
