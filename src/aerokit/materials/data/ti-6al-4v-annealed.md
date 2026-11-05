---
material: ti-6al-4v-annealed
alloy: Ti-6Al-4V
temper_or_condition: Annealed
product_forms: Plate; Sheet
bases: A, B
source_document: MIL-HDBK-5J, Department of Defense Handbook: Metallic Materials and Elements for Aerospace Vehicle Structures, 31 January 2003 (Distribution Statement A: approved for public release; distribution is unlimited)
source_url: https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf
source_file: references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf
source_sha256: 67a4c320cc6c7f23ad155e428a21b3a940e489458a1570026e9b83c2901e6777
source_tables: 5.4.1.0(b) (PDF page 945, printed page 5-53)
extraction: automatic (scripts/materials/extract_mil_hdbk_5.py); no manual transcription
units: as printed in the source (ksi; 10³ ksi; percent; lb/in.³); values copied digit for digit, never rounded or converted
---

# Ti-6Al-4V Annealed — MIL-HDBK-5J design allowables

Each table row is one column of the source table (one thickness range and basis).
Cell syntax: `64` = value as printed; `51 [a]` = value with footnote marker a;
`—` = nothing printed ("..." or blank in the source); `— [c]` = no value, footnote c only.
Values that the source prints once across several columns (E, Ec, G, μ, ω and some others)
are repeated in every column they span. S-basis values are specification minima; A and B
are statistically based (MIL-HDBK-5J Section 1.4.1.1).

## Table 5.4.1.0(b)

- title: Design Mechanical and Physical Properties of Ti-6Al-4V Sheet, Strip, and Plate
- pdf_page: 945
- printed_page: 5-53
- extraction: automatic
- elongation_label: e, percent (S-basis):
- not_extracted: C, K, and α: See Figure 4.5.1.0

| col | specification | form | condition | thickness (in.) | basis | Ftu L (ksi) | Ftu LT (ksi) | Fty L (ksi) | Fty LT (ksi) | Fcy L (ksi) | Fcy LT (ksi) | Fsu (ksi) | Fbru e/D=1.5 (ksi) | Fbru e/D=2.0 (ksi) | Fbry e/D=1.5 (ksi) | Fbry e/D=2.0 (ksi) | e L (percent) | e LT (percent) | E (10³ ksi) | Ec (10³ ksi) | G (10³ ksi) | μ | ω (lb/in.³) |
|---:|:---|:---|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | AMS 4911 and AMS-T-9046, Comp. AB-1 [a] | Sheet | Annealed | ≤0.1875 | A | 134 | 134 | 126 | 126 | 133 | 135 | 87 | 213 [d] | 272 [d] | 171 [c] | 208 [d] | 8 [e] | 8 [e] | 16.0 | 16.4 | 6.2 | 0.31 | 0.160 |
| 2 | AMS 4911 and AMS-T-9046, Comp. AB-1 [a] | Sheet | Annealed | ≤0.1875 | B | 139 | 139 | 131 | 131 | 138 | 141 | 90 | 221 [d] | 283 [d] | 178 [d] | 217 [d] | — | — | 16.0 | 16.4 | 6.2 | 0.31 | 0.160 |
| 3 | AMS 4911 and AMS-T-9046, Comp. AB-1 [a] | Plate | Annealed | 0.1875-2.000 | A | 130 [b] | 130 [b] | 120 | 120 [b] | 124 | 130 | 79 | 206 [d] | 260 [d] | 164 [d] | 194 [d] | 10 | 10 | 16.0 | 16.4 | 6.2 | 0.31 | 0.160 |
| 4 | AMS 4911 and AMS-T-9046, Comp. AB-1 [a] | Plate | Annealed | 0.1875-2.000 | B | 135 | 138 | 125 | 131 | 129 | 142 | 84 | 214 [d] | 276 [d] | 179 [d] | 212 [d] | — | — | 16.0 | 16.4 | 6.2 | 0.31 | 0.160 |
| 5 | AMS 4911 and AMS-T-9046, Comp. AB-1 [a] | Plate | Annealed | 2.001-4.000 | A | 130 [c] | 130 [c] | 118 | 118 | 122 | 128 | 79 | 206 [d] | 260 [d] | 161 [d] | 191 [d] | 10 | 10 | 16.0 | 16.4 | 6.2 | 0.31 | 0.160 |
| 6 | AMS 4911 and AMS-T-9046, Comp. AB-1 [a] | Plate | Annealed | 2.001-4.000 | B | 137 | 137 | 123 | 129 | 127 | 140 | 84 | 217 [d] | 274 [d] | 176 [d] | 209 [d] | — | — | 16.0 | 16.4 | 6.2 | 0.31 | 0.160 |

### Footnotes to Table 5.4.1.0(b) (as printed)

- a: MIL-T-9046 was canceled and superceded by AMS-T-9046
- b: The rounded T99 values are higher than specification values as follows: Ftu(L) = 131 ksi, Ftu(LT) = 132 ksi, and Fty(LT) = 123 ksi.
- c: The rounded T99 values are higher than specification values as follows: Ftu(L) = 133 ksi and Ftu(LT) = 133 ksi.
- d: Bearing values are “dry pin” values per Section 1.4.7.1.
- e: 8%—0.025 to 0.062 in. and 10%—0.063 in. and above.
- f: 5%—0.050 in. and above; 4%—0.033 to 0.049 in. and 3%—0.032 in. and below.

## Ramberg-Osgood parameters

Read from the typical stress-strain figures (text annotations on the figure). Typical curves:
not design allowables. Equation 9.8.4.1.2(b), PDF page 1594:
e_total = f/E + 0.002 (f/f0.2ys)^n.

### Figure 5.4.1.1.6(a)

- pdf_page: 956
- caption: Figure 5.4.1.1.6(a). Typical tensile stress-strain curves at cryogenic, room, and elevated temperatures for annealed Ti-6Al-4V alloy extrusion.
- thickness: —

| curve | n | 0.2% yield (ksi) |
|:---|---:|---:|
| -423 °F | 20 | — |
| -321 °F | 21 | — |
| -110 °F | 20 | — |
| RT | 33 | — |
| 400 °F | 29 | — |
| 700 °F | 19 | — |
| 900 °F | 9.6 | — |

### Figure 5.4.1.1.6(b)

- pdf_page: 957
- caption: Figure 5.4.1.1.6(b). Typical compressive stress-strain curves at room and elevated temperatures for annealed Ti-6Al-4V alloy extrusion.
- thickness: —

| curve | n | 0.2% yield (ksi) |
|:---|---:|---:|
| RT | 21 | — |
| 400 F | 19 | — |
| 700 F | 14 | — |
| 900 F | 9.8 | — |

## Figures

| figure | pdf page | file | caption |
|:---|---:|:---|:---|
| 5.4.1.1.1 | 953 | figures/mil-hdbk-5j-p0953.png | Figure 5.4.1.1.1. Effect of temperature on the tensile ultimate strength (Ftu) and the tensile yield strength (Fty) of annealed Ti-6Al-4V alloy (all wrought products). |
| 5.4.1.1.4 | 955 | figures/mil-hdbk-5j-p0955.png | Figure 5.4.1.1.4. Effect of temperature on the tensile and compressive moduli (E and Ec) of annealed Ti-6Al-4V alloy sheet and bar. |
| 5.4.1.1.6(a) | 956 | figures/mil-hdbk-5j-p0956.png | Figure 5.4.1.1.6(a). Typical tensile stress-strain curves at cryogenic, room, and elevated temperatures for annealed Ti-6Al-4V alloy extrusion. |
| 5.4.1.1.6(b) | 957 | figures/mil-hdbk-5j-p0957.png | Figure 5.4.1.1.6(b). Typical compressive stress-strain curves at room and elevated temperatures for annealed Ti-6Al-4V alloy extrusion. |
| 5.4.1.1.6(c) | 957 | figures/mil-hdbk-5j-p0957.png | Figure 5.4.1.1.6(c). Typical compressive tangent-modulus curves at room and elevated temperatures for annealed Ti-6Al-4V alloy extrusion. |
