# C_harrington1951 — NACA TN 2318, coaxial and single rotor static-thrust (hover) data

## Citation
Harrington, Robert D. (1951). *Full-Scale-Tunnel Investigation of the Static-Thrust Performance of a Coaxial Helicopter Rotor.* NACA Technical Note 2318, Langley Aeronautical Laboratory, March 1951.
NTRS ID 19930083001. PDF: https://ntrs.nasa.gov/api/citations/19930083001/downloads/19930083001.pdf (record: https://ntrs.nasa.gov/citations/19930083001)

## What was read
- Full text, 26-page scanned PDF downloaded from NTRS (local copy: `D:\tmp_ideathon\venus\downloads\rotor\harrington_tn2318.pdf`).
- Text pp. 1-8 (Summary, Symbols, Apparatus and Tests, Results and Discussion, Concluding Remarks), via pypdf text extraction.
- Figures 1(a), 1(b) (blade chord and t/c vs radius), Fig. 4 (rotor 1 CT vs CQ), Fig. 8 (rotor 2 CT vs CQ): rendered at 300 dpi and digitized by me (method below). Figs 5, 6, 7, 9, 10 viewed but not digitized.

Tag legend: **[D-ag]** = read in this source (text or figure). Values marked *digitized* come from my own reading of a scanned figure, not from a printed table. **[derived]** = my arithmetic from [D-ag] numbers.

## Definitions used in the report (p. 2-3) [D-ag]
- CT = T / (ρ π R² (ΩR)²);  CQ = Q / (ρ π R² (ΩR)² R). In hover CP = CQ.
- σ = b c_e / (π R), with c_e the "equivalent blade chord". **For the coaxial rotor σ counts both rotors (4 blades).**
- Figure of merit M = 0.707 CT^{3/2} / CQ. For the coaxial rotor this is the plain single-rotor formula with no coaxial correction applied.

## Rotor geometry
| Item | Rotor 1 | Rotor 2 | Source |
|---|---|---|---|
| Diameter | 25 ft (R = 12.5 ft = 3.81 m) | 25 ft (same, from 2.0 ft = 8 % D) | p. 3-4 [D-ag] |
| Blades | 2 per rotor (coax = 2+2) | 2 per rotor | p. 3 [D-ag] ("two, 25-foot-diameter, two-blade rotors"); rotor 2 described as similar design |
| Rotor spacing | 2.33 ft = 9.5 % D | 2.0 ft = 8 % D | p. 3, p. 4 [D-ag] |
| Solidity, single | 0.027 | 0.076 | p. 3, p. 4 [D-ag] |
| Solidity, coaxial | 0.054 | 0.152 | p. 3, p. 4 [D-ag] |
| Planform | linear taper, cr/ct = 2.92 | constant chord (cr/ct = 1) | Fig. 4 and Fig. 8 captions [D-ag] |
| Chord | c(r) ≈ 12.43 − 0.0534·r (in, r in inches); measured 12.16 in at r = 5 in, 10.52 at 35, 9.47 at 55, 5.73 at 125, 4.68 at 145; ~4.4 in at r ≈ 148-149 | 18.0 in constant | Fig. 1(a), 1(b), *digitized* [D-ag] |
| Twist | **untwisted** | not stated in text; Fig. 1(b) shows no twist curve | p. 4 [D-ag] |
| Airfoil | NACA four-digit symmetrical sections, thickness tapered | NACA four-digit symmetrical (rotor 2 "similar in design"), thickness tapered | p. 3-4 [D-ag] |
| t/c distribution | ~30.4 % at r = 25 in, 29.2 % at r = 44 in, step down to ~24.5 % at r = 48 in, ~21.7 % at r = 100, ~18 % at r = 125-130, ~15.8 % at r = 140, ~14.6 % at r = 145 | linear: 27.0 % at r = 25 in, 24.9 % at 45, 22.9 % at 65, 20.8 % at 85, 18.7 % at 105, 16.7 % at 125, 15.6 % at 135 (≈ 29.6 − 0.1035·r %) | Fig. 1, *digitized* [D-ag] |
| Root cutout | not stated. Fig. 1(a) solid curves start at r ≈ 20 in (0.13 R); Fig. 1(b) t/c is dashed (extrapolated) inboard of r ≈ 30 in (0.2 R) | | Fig. 1 [D-ag], interpretation mine |
| Hub | see-saw (teetering) flapping, rigid in-plane | rigid in flap and lag | p. 3-4 [D-ag] |
| Construction | wood (birch spar, mahogany ribs, spruce plywood skin) | all-metal | p. 4 [D-ag] |
| Design point | disk loading 2.5 lb/ft², tip speed 540 ft/s | – | p. 3 [D-ag] |
| Tip speed actually tested | max 500 ft/s (vibration); coax also 450 and 327 ft/s | coax 392 and 327 ft/s; single 392 and 262 ft/s | p. 5, Fig. 4, Fig. 8 [D-ag] |

Check [derived]: thrust-weighted equivalent chord of the digitized rotor-1 chord line, c_e = ∫c r² dr / ∫r² dr = 12.43 − 0.0534·0.75·150 ≈ 6.42 in, gives σ = 2·6.42/(π·150) ≈ 0.0273, which matches the stated 0.027. For rotor 2, σ = 2·18/(π·150) = 0.0764, which matches 0.076.
Approximate tip Reynolds/Mach [derived, ISA sea level assumed, not stated in report]: rotor 1 at ΩR = 500 ft/s = 152.4 m/s gives M_tip ≈ 0.45 and Re(0.75R) ≈ 1.3×10⁶.

## Key printed numbers (text) [D-ag]
- Rotor 1 coax CQ0 (profile torque coefficient at CT = 0, ΩR = 500 ft/s) = **0.0000777**. The single rotor's value is about half (p. 5, Concluding remark 1).
- Rotor 1 hover range tested at 500 ft/s: CT up to **0.00557** (coax) and **0.00346** (single) (p. 5).
- Max figure of merit: **0.635 coax, 0.615 single** (p. 6, Fig. 6).
- [derived] Effective zero-lift profile drag: C_Q0 = σ c_d0/8 gives c_d0 = 8 × 0.0000777 / 0.054 ≈ **0.0115** for rotor 1. The same value follows from the single rotor (half the C_Q0 with half the σ). Use this as the cd0 anchor for the rotor-1 BEMT (Re_0.75 ≈ 1.3×10⁶ per C_coleman1997).
- Scale (Re) effect: appreciable between 327 and 450 ft/s, small between 450 and 500 ft/s (p. 5).
- Differential collective (yaw control) at its maximum available settings (+3°30′, −1°40′) gave about +2 % CQ at a given CT (p. 5-6).
- Theory used by Harrington (p. 6): coax modelled as one 4-blade rotor of equal solidity. Section drag cd0 = δ0 + δ1·α + δ2·α², with δ0 = cd0 at CT = 0, a = 5.73 /rad. Tip loss: outer **3 %** of span produces no thrust but has profile drag. The method "can be predicted with the same degree of accuracy as … a single-rotor configuration" for spacings of 8-9.5 % D.

## Digitized data — Rotor 1, Fig. 4 (yaw trimmed) [D-ag, *digitized*]
Method: rendered at 300 dpi; fitted a bilinear pixel→data map to all printed gridlines (rms residual ≈ 4×10⁻⁷ in CQ and 9×10⁻⁶ in CT); read each symbol's centre dot against local gridlines. Estimated reading uncertainty is about ±3×10⁻⁶ in CQ and ±3×10⁻⁵ in CT for isolated symbols, larger where symbols overlap (flagged). Check: the top coax point gives M = 0.636 (report: 0.635), and the top single-rotor point gives 0.609 (report: 0.615).

### Coaxial, σ = 0.054, ΩR = 500 ft/s (circles)
| CQ | CT | note |
|---|---|---|
| 0.000078 | ~0.0000 | symbol centred on the axis; consistent with the printed CQ0 = 0.0000777 |
| 0.000083 | 0.000225 | |
| 0.000091 | 0.000661 | |
| 0.000104 | 0.001021 | |
| 0.000124 | 0.001513 | |
| ~0.000147-0.000152 | ~0.00201-0.00204 | 2-3 overlapping circles plus one square; not separable |
| 0.0001776 | 0.002485 | |
| 0.0001853 | 0.002593 | |
| 0.000208 | 0.003016 | |
| 0.000228 | 0.003126 | |
| 0.000240 | 0.003291 | |
| 0.000277 | 0.003743 | two adjacent circles |
| 0.000272 | 0.003821 | two adjacent circles |
| 0.000308 | 0.004217 | |
| 0.000354 | 0.004615 | overlaps a square |
| 0.000390 | 0.004926 | |
| 0.0004205 | 0.005204 | |
| 0.0004625 | 0.005575 | highest coax point; report states CT max 0.00557 |

### Coaxial, σ = 0.054, ΩR = 450 ft/s (squares)
| CQ | CT |
|---|---|
| ~0.000142 | ~0.00200 (in the cluster, low confidence) |
| 0.000200 | 0.002887 |
| 0.0002545 | 0.003637 |
| 0.000345 | 0.004587 |
| 0.000393 | 0.005078 |
| 0.000457 | 0.005692 |
| 0.000535 | 0.006265 |

### Coaxial, σ = 0.054, ΩR = 327 ft/s (diamonds; low-Re case)
| CQ | CT |
|---|---|
| 0.000161 | 0.00171 |
| 0.000195 | 0.00231 |
| 0.000226 | 0.002681 |
| 0.000266 | 0.003158 |
| 0.000322 | 0.003834 |
| 0.000362 | 0.004382 |
| 0.000414 | 0.005029 |
| 0.000477 | 0.005608 |
| 0.000525 | 0.005997 |

### Single rotor, σ = 0.027, ΩR = 500 ft/s (Δ = lower rotor alone, ◺ = upper rotor alone)
| rotor | CQ | CT | note |
|---|---|---|---|
| lower | 0.0000354 | 0.000179 | |
| lower | 0.0000431 | 0.000333 | |
| upper | 0.0000408 | 0.000405 | |
| upper | ~0.000051 | ~0.00072 | no centre dot visible, low confidence |
| lower | 0.0000555 | 0.000741 | |
| upper | 0.0000598 | 0.000961 | |
| lower | 0.0000676 | 0.001054 | |
| upper | 0.0000704 | 0.00125 | |
| upper | 0.0000793 | 0.001456 | overlapping, low confidence |
| lower | 0.0000796 | 0.001407 | |
| lower | 0.0000899 | 0.001538 | |
| upper | 0.0001037 | 0.001796 | |
| lower | 0.0001067 | 0.001865 | |
| lower | 0.0001181 | 0.002064 | |
| upper | 0.0001288 | 0.002208 | |
| lower | 0.0001373 | 0.002348 | |
| upper | 0.0001586 | 0.002645 | |
| lower | 0.0001748 | 0.002825 | |
| upper | ~0.000191 | ~0.00295 | partly hidden, low confidence |
| lower | 0.0001944 | 0.0031 | |
| lower | 0.000236 | 0.003468 | highest single point; report states CT max 0.00346 |
Several more single-rotor points cluster at CT < 0.0002, CQ ≈ 0.00003-0.00004. I did not read them.

## Digitized data — Rotor 2, Fig. 8 (yaw trimmed, cr/ct = 1) [D-ag, *digitized*]
Same method (rms gridline residual 3×10⁻⁷ CQ, 5×10⁻⁶ CT).

### Coaxial, σ = 0.152, ΩR = 392 ft/s (circles)
| CQ | CT |
|---|---|
| 0.000266 | 0.002056 |
| 0.000280 | 0.0022 |
| 0.000399 | 0.004017 |
| 0.000420 | 0.00418 |
| 0.000548 | 0.00543 |
| 0.000580 | 0.005705 |
| 0.000705 | 0.006792 (two overlapping circles) |
| 0.000710 | 0.006846 |

### Coaxial, σ = 0.152, ΩR = 327 ft/s (squares)
| CQ | CT |
|---|---|
| 0.000257 | 0.001959 |
| 0.0002695 | 0.002239 |
| 0.000388 | 0.0039 |
| 0.000399 | 0.003811 |
| 0.000494 | 0.004976 |
| 0.000501 | 0.005029 |
| 0.000633 | 0.006201 |
| 0.000643 | 0.00641 |
| 0.000770 | 0.00744 |
| 0.000802 | 0.007455 |
| 0.000954 | 0.008698 |
| 0.000973 | 0.008775 |

### Single (lower) rotor, σ = 0.076, ΩR = 262 ft/s (diamonds)
| CQ | CT |
|---|---|
| 0.000126 | 0.000878 |
| 0.000136 | 0.001007 |
| 0.000142 | 0.001212 |
| 0.000179 | 0.00178 |
| 0.000180 | 0.00189 |
| 0.0002086 | 0.002383 |
| 0.000252 | 0.003005 (overlaps a triangle) |
| 0.000287 | 0.003244 |
| 0.000360 | 0.004199 |
| 0.000387 | 0.004527 |
| 0.000438 | 0.004981 |
| 0.000534 | 0.005813 |

### Single (lower) rotor, σ = 0.076, ΩR = 392 ft/s (triangles)
| CQ | CT |
|---|---|
| 0.0001955 | 0.002129 |
| 0.000238 | 0.002695 |
| ~0.000252 | ~0.003005 (under a diamond, low confidence) |

## Caveats for using this as a BEMT validation set
- Numbers come from my reading of 1951 scanned plots, not from tabulated values. Use a tolerance band of at least ±3 % in CQ at mid and high CT. Below CT ≈ 0.001 the relative error is larger.
- The coax CT and CQ are **total system** coefficients normalized by a single disk area, and σ includes both rotors. When comparing with a coaxial BEMT, compare total thrust against total torque (sum of upper and lower torque; yaw is trimmed so the two torques are about equal).
- Rotor 1 is untwisted and tapered, with thick wooden NACA 00xx sections (t/c ~15-30 %). Harrington says profile drag dominates the prediction accuracy ("accurate knowledge of the zero-lift drag … is required", p. 7). A Venus low-Re rotor will sit at much lower Re than this data (~10⁶).
- The scale effect between 327 and 450 ft/s (p. 5) means the 327 ft/s set should not be mixed with the 500 ft/s set when fitting cd0.
- The root cutout is not given in the text. The values above are my reading of Fig. 1.
- Rotor 2 twist is not stated explicitly in the text I read. The text says rotor 2 was "similar in design to rotor 1 except …" (p. 4), and since rotor 1 is untwisted, untwisted is the likely reading. Treat it as an assumption.
