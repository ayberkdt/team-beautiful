---
material: ncamp-8552-im7
material_name: Hexcel 8552 IM7 unidirectional tape (prepreg); NCAMP shared database
source_document: NCAMP Report No. NCP-RP-2013-015 Rev A, A Comparison of Equivalence Criteria and Basis Values for HEXCEL 8552 IM7 Unidirectional Tape computed from the NCAMP shared database, Elizabeth Clarkson, National Center for Advanced Materials Performance (NCAMP), National Institute for Aviation Research, Wichita State University, report date Oct 31, 2013
source_file: references/materials/ncamp-ncp-rp-2013-015/cmh17-generic-basis-8552-im7-revA.pdf
source_sha256: 7daa0724788bf7b85aaadc0d24bb21fcfa33405b7dc341e6f39a71cd5939a03d
source_bytes: 1925554
source_pages: 97
source_origin: downloaded from cmh17.org (stated in the task; the download URL is not recorded here)
running_header: every page from PDF page 3 on prints 'May 24, 2013 NCP-RP-2013-015 N/C'; the cover (PDF page 1) and revision list (PDF page 2) say Rev A, Oct 31, 2013 ('Army Data Values Redacted. Sections 3.5 and 3.6 updated.')
printed_page_numbers: equal to the PDF page numbers
approval_caveat: "Generic basis values have not yet been approved by the CMH-17 organization." (PDF page 12)
units: the tables print no unit; strengths, standard deviations, basis values and acceptance limits are ksi (axis label 'ksi' on the figures of the same data, e.g. Figure 6 on PDF page 29); 'Coeff Var.' is printed in percent; 'Count' is a number of specimens. The report contains no modulus (msi) values.
conditions: CTD, RTD, ETD, ETW as printed; the only temperature stated is 250°F for the NCAMP ETW results (PDF page 41, '180°F for the HEXCEL Product data versus 250°F for the NCAMP results'); the report gives no CTD/ETD temperature and no moisture conditioning details
not_in_source: E1t, E1c, E2, nu12, G12, F2tu, F2cu, bearing, cured ply thickness, fibre volume, density
extraction: automatic (scripts/materials/extract_ncamp_8552_im7.py, PyMuPDF words); all table numbers parsed automatically; only the '## Test descriptions' section is transcribed by hand (marked manual)
---

# Hexcel 8552 IM7 unidirectional tape — NCAMP NCP-RP-2013-015 Rev A

Strength data of the NCAMP shared database (one qualification sample, units A01-A03, and
equivalency samples from other composite part manufacturers, units A2-A12). Basis values are
given by three methods as printed: qualification (CMH-17 Rev G Section 8.3), pooled data (ANOVA)
and generic (NCAMP approach of this report, not approved by CMH-17).
Cell syntax: `84.42` = value as printed; `53.86 [*]` = value printed with an asterisk (see the
table note); `NA` = printed NA; `5.91%` = printed percentage. Each row carries its PDF page.

## Test descriptions

- extraction: manual (transcribed from the prose on PDF pages 26, 27, 32 and 39; layup subscripts read from the text layer)

| test | description | layup | data | environments | pdf page |
|:---|:---|:---|:---|:---|---:|
| UNC0 | Unnotched Compression | [90/0/90]5 | normalized | RTD, ETD, ETW | 26 |
| OHC1 | Quasi-Isotropic Open Hole Compression | [45/0/-45/90]3S | normalized | RTD, ETW | 26 |
| 0° compression | 0° Compression Strength from UNC0 Data (computed via the formulas of NCP-RP-2009-028 Rev B section 2.5) | — | computed | RTD, ETD, ETW | 27 |
| LT | Longitudinal Tension | [0]6 | normalized | CTD, RTD, ETW | 32 |
| UNT0 | Unnotched Tension | [0/90]2s | normalized | CTD, RTD, ETW | 32 |
| OHT1 | Quasi-Isotropic Open Hole Tension | [45/0/-45/90]2s | normalized | CTD, RTD, ETW | 32 |
| IPS | In-Plane Shear (strength at 5% strain; 0.2% offset strength) | [45/−45]3s | not normalized | 5% strain: RTD, ETW; 0.2% offset: CTD, RTD, ETW | 39 |
| SBS | Short Beam Strength | [0]34 | not normalized | RTD, ETW | 39 |

## Table 4

- title: Compression Strength Units
- kind: units
- pdf_page: 26
- extraction: automatic
- groups: UNC0; OHC1
- note: *Unit A6 fails the generic equivalence test for the mean values of the compression strength properties

| page | row | UNC0 / RTD | UNC0 / ETD | UNC0 / ETW | OHC1 / RTD | OHC1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|
| 26 | Unit A01 | NA | NA | NA | 49.7776 | 36.5261 |
| 26 | Unit A02 | 94.5802 | 74.0958 | 64.8118 | 48.7187 | 35.2038 |
| 26 | Unit A03 | 94.3659 | 78.3914 | 63.2988 | 48.6380 | 34.6467 |
| 26 | Unit A2 | 96.2747 | 73.5424 | 69.2822 | 49.0295 | 35.7920 |
| 26 | Unit A4 | 93.7557 | 64.3706 | 67.2491 | 49.2890 | 35.9984 |
| 26 | Unit A5 | 92.6674 | 72.4021 | 65.1376 | 49.8663 | 34.9689 |
| 26 | Unit A6 | 79.3685 | 78.5173 | 64.1723 | 49.3351 | 35.0254 |
| 26 | Unit A8 | 97.0097 | 74.0357 | 66.0642 | 48.9825 | 35.4048 |
| 26 | Unit A9 | 97.6087 | 75.5440 | 67.5306 | 48.5799 | 35.2421 |
| 26 | Unit A10 | 97.6081 | 76.1733 | 64.9995 | 48.4162 | 35.0181 |
| 26 | Unit A11 | 96.2567 | 73.5567 | 63.1538 | 50.3488 | 35.8527 |
| 26 | Unit A12 | 97.8144 | 76.8109 | 65.9994 | 49.2527 | 36.8756 |
| 26 | Unit Average | 94.3009 | 74.3127 | 65.6090 | 49.1862 | 35.5462 |

## Table 5

- title: UNC0 and OHC1 Strength Equivalence Acceptance Limits, Basis Values and Estimates
- kind: basis
- pdf_page: 27
- extraction: automatic
- groups: UNC0; OHC1
- note: * Alternate Generic Basis Value Method used due to large within company variance

| page | row | UNC0 / RTD | UNC0 / ETD | UNC0 / ETW | OHC1 / RTD | OHC1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|
| 27 | Qualification B-Basis or B-Estimate | 84.42 | 65.44 | 54.90 | 46.15 | 32.58 |
| 27 | Qualification A-Estimate | 78.25 | 59.27 | 48.61 | 44.14 | 30.57 |
| 27 | Pooled Data B-basis (ANOVA) | 79.05 | 61.89 | 56.63 | 46.74 | 33.12 |
| 27 | Pooled Data A-basis (ANOVA) | 68.20 | 53.05 | 49.78 | 44.88 | 31.31 |
| 27 | Generic B-basis | 73.72 | 53.86 [*] | 50.94 [*] | 45.06 [*] | 31.48 [*] |
| 27 | Generic A-basis | 65.35 | 46.89 [*] | 43.95 [*] | 43.22 [*] | 29.79 [*] |

## Table 6

- title: Equivalence Acceptance Limits and Basis Values for 0° Compression
- kind: basis
- pdf_page: 28
- extraction: automatic
- groups: 0° Compression Strength from UNC0 Data

| page | row | 0° Compression Strength from UNC0 Data / RTD | 0° Compression Strength from UNC0 Data / ETD | 0° Compression Strength from UNC0 Data / ETW |
|---:|:---|---:|---:|---:|
| 28 | Qualification B-Estimate | 222.07 | 175.06 | 148.02 |
| 28 | Qualification A-Estimate | 205.65 | 158.64 | 131.27 |
| 28 | Generic B-basis | 193.85 | 144.02 | 136.94 |
| 28 | Generic A-basis | 171.81 | 125.38 | 118.14 |

## Table 7

- title: Compression Strength Equivalence Acceptance Limits for Unit Means
- kind: limits
- pdf_page: 28
- extraction: automatic
- groups: UNC0; OHC1

| page | row | UNC0 / RTD | UNC0 / ETD | UNC0 / ETW | OHC1 / RTD | OHC1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|
| 28 | Minimum Allowable Mean (Qual) | 90.71 | 72.14 | 60.69 | 47.87 | 34.53 |
| 28 | Minimum Allowable Mean (Pooled) | 89.06 | 69.47 | 61.66 | 48.11 | 34.55 |
| 28 | Minimum Allowable Mean (Generic) | 76.10 | 63.11 | 60.20 | 47.51 | 33.72 |

## Table 8

- title: Compression Strength Equivalence Acceptance Limits for Sample Minimum and Standard Deviation
- kind: limits
- pdf_page: 28
- extraction: automatic
- groups: UNC0; OHC1

| page | row | UNC0 / RTD | UNC0 / ETD | UNC0 / ETW | OHC1 / RTD | OHC1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|
| 28 | Minimum acceptable specimen value (Qual) | 79.42 | 62.05 | 50.00 | 44.24 | 31.61 |
| 28 | Minimum acceptable specimen value (Pooled) | 73.67 | 55.89 | 49.70 | 44.90 | 31.54 |
| 28 | Maximum acceptable standard deviation (Generic) | 9.29 | 10.55 | 10.62 | 2.81 | 2.57 |

## Table 9

- title: Tension Strength Units
- kind: units
- pdf_page: 32
- extraction: automatic
- groups: Longitudinal Tension; Unnotched Tension; Open Hole Tension

| page | row | Longitudinal Tension / CTD | Longitudinal Tension / RTD | Longitudinal Tension / ETW | Unnotched Tension / CTD | Unnotched Tension / RTD | Unnotched Tension / ETW | Open Hole Tension / CTD | Open Hole Tension / RTD | Open Hole Tension / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | Unit A01 | 351.0320 | 357.4946 | 317.5174 | 150.3135 | 172.7483 | 178.7057 | 55.6527 | 57.6876 | 65.5433 |
| 32 | Unit A02 | 363.5426 | 371.2816 | 342.2871 | 151.4152 | 169.1497 | 175.6726 | 57.8846 | 58.6289 | 67.7007 |
| 32 | Unit A03 | 357.6595 | 359.3027 | 348.9640 | 156.3816 | 172.2565 | 183.3173 | 60.0763 | 60.9131 | 67.7603 |
| 32 | Unit A2 | 350.1586 | 379.1181 | 315.6127 | 160.5452 | 178.8597 | 183.9735 | 57.8861 | 60.0071 | 68.8052 |
| 32 | Unit A4 | 371.5482 | 361.1002 | 331.0850 | 160.7040 | 183.0869 | 173.6907 | 57.7528 | 60.6131 | 65.5552 |
| 32 | Unit A5 | 337.7599 | 366.2555 | 336.1728 | 141.9117 | 165.1766 | 177.5706 | 54.4372 | 58.6046 | 64.1320 |
| 32 | Unit A6 | 343.4442 | 343.1527 | 327.7140 | 133.8409 | 160.5384 | 165.4421 | 55.9633 | 58.3777 | 64.7328 |
| 32 | Unit A8 | 333.9087 | 346.5323 | 332.2169 | 143.0282 | 163.7844 | 175.6588 | 53.1533 | 56.6409 | 65.4513 |
| 32 | Unit A9 | 347.3367 | 381.9309 | 373.0609 | 156.6349 | 181.5081 | 178.9732 | 58.3098 | 61.3172 | 67.3902 |
| 32 | Unit A10 | 346.2347 | 346.3821 | 334.1439 | 160.9649 | 180.8723 | 179.9383 | 54.0256 | 59.9221 | 69.8164 |
| 32 | Unit A11 | 321.6418 | 330.6077 | 289.0183 | 126.7326 | 155.6357 | 171.3294 | 49.1134 | 51.9466 | 62.6640 |
| 32 | Unit A12 | 392.3781 | 400.7486 | 360.1096 | 170.8795 | 188.4269 | 181.9095 | 61.9959 | 64.4384 | 69.3114 |
| 32 | HEXCEL | 373 | 395 | NA | NA | NA | NA | NA | NA | NA |
| 32 | Unit Avg | 353.0496 | 364.5313 | 333.9919 | 151.1127 | 172.6703 | 177.1818 | 56.3543 | 59.0915 | 66.5720 |

## Table 10

- title: LT, UNT0 and OHT1 Strength Equivalence Acceptance Limits and Basis Values
- kind: basis
- pdf_page: 33
- extraction: automatic
- groups: LT; UNT0; OHT1
- note: * Alternate Generic Basis Value Method used due to large within company variance

| page | row | LT / CTD | LT / RTD | LT / ETW | UNT0 / CTD | UNT0 / RTD | UNT0 / ETW | OHT1 / CTD | OHT1 / RTD | OHT1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 33 | Qual. B-Basis or B-Estimate | 332.10 | 336.95 | 263.95 | 139.85 | 158.59 | 166.44 | 44.35 | 54.29 | 62.28 |
| 33 | Qualification A-Estimate | 314.58 | 319.53 | 201.74 | 131.31 | 150.06 | 157.91 | 34.78 | 51.08 | 59.06 |
| 33 | Pooled Data B-basis (ANOVA) | 302.31 | 305.61 | 273.84 | 121.62 | 147.56 | 161.60 | 47.87 | 51.52 | 60.65 |
| 33 | Pooled Data A-basis (ANOVA) | 267.92 | 265.01 | 229.91 | 100.95 | 129.61 | 150.47 | 42.00 | 46.19 | 56.43 |
| 33 | Generic B-basis | 273.31 | 280.74 | 240.28 | 96.37 | 129.03 | 150.54 [*] | 41.60 | 46.04 | 56.98 |
| 33 | Generic A-basis | 242.70 | 248.58 | 204.31 | 75.36 | 112.27 | 142.51 [*] | 35.94 | 41.03 | 53.30 |

## Table 11

- title: Tension Strength Equivalence Acceptance Limits for Unit Means
- kind: limits
- pdf_page: 33
- extraction: automatic
- groups: LT; UNT0; OHT1

| page | row | LT / CTD | LT / RTD | LT / ETW | UNT0 / CTD | UNT0 / RTD | UNT0 / ETW | OHT1 / CTD | OHT1 / RTD | OHT1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 33 | Minimum Allowable Mean (Qual) | 348.82 | 351.79 | 307.14 | 149.07 | 165.07 | 174.67 | 56.10 | 57.41 | 65.03 |
| 33 | Minimum Allowable Mean (Pooled) | 334.20 | 341.71 | 313.00 | 142.19 | 164.74 | 171.39 | 53.54 | 56.64 | 64.55 |
| 33 | Minimum Allowable Mean (Generic) | 285.24 | 293.29 | 254.31 | 104.57 | 135.56 | 157.76 | 43.81 | 47.99 | 58.42 |

## Table 12

- title: Tension Strength Equivalence Acceptance Limits for Sample Minimum and Standard Deviation
- kind: limits
- pdf_page: 33
- extraction: automatic
- groups: LT; UNT0; OHT1

| page | row | LT / CTD | LT / RTD | LT / ETW | UNT0 / CTD | UNT0 / RTD | UNT0 / ETW | OHT1 / CTD | OHT1 / RTD | OHT1 / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 33 | Min. specimen value (Qual) | 323.31 | 319.34 | 228.61 | 138.61 | 146.26 | 161.09 | 51.18 | 52.66 | 59.27 |
| 33 | Min. specimen value (Pooled) | 285.50 | 281.54 | 248.00 | 115.34 | 140.27 | 154.70 | 45.61 | 49.39 | 58.54 |
| 33 | Max. std. dev. (Generic) | 32.73 | 34.39 | 37.70 | 22.46 | 17.91 | 12.19 | 6.05 | 5.36 | 3.94 |

## Table 13

- title: Shear Strength Units
- kind: units
- pdf_page: 39, 40
- extraction: automatic
- groups: Short Beam Strength; In-Plane Shear Strength @ 5% Strain; In-Plane Shear 0.2% Offset Strength
- note: *Unit A11 fails the generic equivalence test for the mean values of the shear strength properties

| page | row | Short Beam Strength / RTD | Short Beam Strength / ETW | In-Plane Shear Strength @ 5% Strain / RTD | In-Plane Shear Strength @ 5% Strain / ETW | In-Plane Shear 0.2% Offset Strength / CTD | In-Plane Shear 0.2% Offset Strength / RTD | In-Plane Shear 0.2% Offset Strength / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 39 | Unit A01 | 17.3965 | 8.1751 | 13.0357 | 5.5692 | 11.0907 | 7.5913 | 3.3250 |
| 39 | Unit A02 | 16.9797 | 8.2567 | 13.2380 | 5.6957 | 11.3737 | 7.7992 | 3.4069 |
| 39 | Unit A03 | 16.9992 | 8.3377 | 13.4008 | 5.3430 | 11.4197 | 7.8687 | 3.1691 |
| 39 | Unit A2 | 17.3021 | 8.3685 | 13.2828 | 5.5231 | 10.7332 | 7.8106 | 3.1542 |
| 39 | Unit A4 | 17.4888 | 8.1074 | 13.1634 | 5.2817 | 10.4560 | 7.6322 | 3.1376 |
| 40 | Unit A5 | 17.3672 | 8.0070 | 13.0516 | 5.2250 | 10.6050 | 7.5683 | 3.1287 |
| 40 | Unit A6 | 16.9036 | 8.2122 | 12.9588 | 5.3020 | 10.3254 | 7.4333 | 3.0933 |
| 40 | Unit A8 | 18.0190 | 8.6433 | 13.0779 | 5.4912 | 10.9147 | 7.7718 | 3.2598 |
| 40 | Unit A9 | 17.3656 | 8.6895 | 13.1779 | 5.4811 | 10.8985 | 7.6934 | 3.2634 |
| 40 | Unit A10 | 16.8199 | 8.2190 | 13.4464 | 5.5872 | 10.7120 | 7.8001 | 3.2734 |
| 40 | Unit A11* | 15.3827 | 7.6878 | 12.8466 | 5.2022 | 10.4723 | 7.4405 | 2.9678 |
| 40 | Unit A12 | 17.2102 | 8.0537 | 13.4287 | 5.7775 | 10.5827 | 7.7973 | 3.4195 |
| 40 | HEXCEL | 19.9 | 11.6 | NA | NA | NA | NA | NA |
| 40 | Unit Avg | 17.3180 | 8.4891 | 13.1757 | 5.4566 | 10.7987 | 7.6839 | 3.2166 |

## Table 14

- title: Shear Strength Equivalence Acceptance Limits and Basis Values
- kind: basis
- pdf_page: 40
- extraction: automatic
- groups: Short Beam Strength; In-Plane Shear Strength @ 5% Strain; In-Plane Shear 0.2% Offset Strength
- note: * Alternate Generic Basis Value Method used due to large within company variance

| page | row | Short Beam Strength / RTD | Short Beam Strength / ETW | In-Plane Shear Strength @ 5% Strain / RTD | In-Plane Shear Strength @ 5% Strain / ETW | In-Plane Shear 0.2% Offset Strength / CTD | In-Plane Shear 0.2% Offset Strength / RTD | In-Plane Shear 0.2% Offset Strength / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 40 | Qualification B-Basis | 16.28 | 7.78 | 12.76 | 4.49 | 10.25 | 7.38 | 2.61 |
| 40 | Qualification A-Estimate | 15.67 | 6.67 | 12.43 | 3.75 | 9.50 | 6.32 | 2.12 |
| 40 | Pooled Data B-basis | 15.48 | 7.47 | 12.65 | 4.98 | 9.93 | 7.29 | 2.88 |
| 40 | Pooled Data A-basis | 14.33 | 6.93 | 12.28 | 4.64 | 9.33 | 7.01 | 2.64 |
| 40 | Generic B-basis | 14.70 | 7.37 | 12.38 | 4.68 | 9.34 | 7.07 | 2.67 |
| 40 | Generic A-basis | 13.68 | 6.92 | 12.07 | 4.38 | 8.76 | 6.82 | 2.45 |

## Table 15

- title: Shear Strength Equivalence Acceptance Limits for Unit Means
- kind: limits
- pdf_page: 41
- extraction: automatic
- groups: Short Beam Strength; In-Plane Shear Strength @ 5% Strain; In-Plane Shear 0.2% Offset Strength

| page | row | Short Beam Strength / RTD | Short Beam Strength / ETW | In-Plane Shear Strength @ 5% Strain / RTD | In-Plane Shear Strength @ 5% Strain / ETW | In-Plane Shear 0.2% Offset Strength / CTD | In-Plane Shear 0.2% Offset Strength / RTD | In-Plane Shear 0.2% Offset Strength / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 41 | Minimum Allowable Mean (Qual) | 16.83 | 8.09 | 13.08 | 5.41 | 11.13 | 7.61 | 3.20 |
| 41 | Minimum Allowable Mean (Pooled) | 16.56 | 7.97 | 12.98 | 5.29 | 10.50 | 7.55 | 3.10 |
| 41 | Minimum Allowable Mean (Generic) | 15.23 | 7.59 | 12.54 | 4.84 | 9.63 | 7.19 | 2.78 |

## Table 16

- title: Shear Strength Equivalence Acceptance Limits for Sample Minimum and Standard Deviation
- kind: limits
- pdf_page: 41
- extraction: automatic
- groups: Short Beam Strength; In-Plane Shear Strength @ 5% Strain; In-Plane Shear 0.2% Offset Strength

| page | row | Short Beam Strength / RTD | Short Beam Strength / ETW | In-Plane Shear Strength @ 5% Strain / RTD | In-Plane Shear Strength @ 5% Strain / ETW | In-Plane Shear 0.2% Offset Strength / CTD | In-Plane Shear 0.2% Offset Strength / RTD | In-Plane Shear 0.2% Offset Strength / ETW |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 41 | Min. specimen value (Qual) | 15.96 | 7.60 | 12.66 | 5.03 | 10.65 | 7.17 | 2.89 |
| 41 | Min. specimen value (Pooled) | 14.98 | 7.18 | 12.45 | 4.83 | 9.66 | 7.15 | 2.77 |
| 41 | Max. std. dev. (Generic) | 1.116 | 0.480 | 0.339 | 0.330 | 0.625 | 0.264 | 0.235 |

## Table 17

- title: UNC0 RTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 45
- extraction: automatic
- in_table_title: UNC0 Normalized Strength RTD Condition by Batch and Company
- note: column A01: one 'NA' is printed in a cell spanning rows Average, Std Dev., Coeff Var., Max, Min, Count; it is repeated in each of them

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 45 | Average | 94.509 | NA | 94.580 | 94.366 | 96.275 | 93.756 | 92.667 | 79.368 | 97.010 | 97.609 | 97.608 | 96.257 | 97.814 | 94.234 |
| 45 | Std Dev. | 5.587 | NA | 4.750 | 8.272 | 3.413 | 9.282 | 5.368 | 8.404 | 3.089 | 3.699 | 6.090 | 3.900 | 4.690 | 7.618 |
| 45 | Coeff Var. | 5.91% | NA | 5.02% | 8.77% | 3.55% | 9.90% | 5.79% | 10.59% | 3.18% | 3.79% | 6.24% | 4.05% | 4.80% | 8.08% |
| 45 | Max | 99.743 | NA | 99.743 | 99.525 | 101.340 | 102.875 | 100.673 | 92.672 | 102.721 | 103.350 | 105.115 | 102.890 | 106.013 | 106.013 |
| 45 | Min | 84.825 | NA | 85.878 | 84.825 | 92.211 | 75.436 | 84.434 | 68.767 | 93.751 | 91.767 | 86.510 | 92.096 | 92.161 | 68.767 |
| 45 | Count | 9 | NA | 6 | 3 | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 8 | 9 | 88 |

## Table 18

- title: UNC0 ETD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 48
- extraction: automatic
- in_table_title: UNC0 Normalized Strength ETD Condition by Batch and Company
- note: column A01: one 'NA' is printed in a cell spanning rows Average, Std Dev., Coeff Var., Max, Min, Count; it is repeated in each of them

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 48 | Average | 75.528 | NA | 74.096 | 78.391 | 73.542 | 64.371 | 72.402 | 78.517 | 74.036 | 75.544 | 76.173 | 73.557 | 76.811 | 74.029 |
| 48 | Std Dev. | 4.992 | NA | 5.045 | 4.196 | 4.675 | 3.875 | 9.664 | 6.705 | 4.063 | 1.987 | 7.972 | 6.978 | 3.399 | 6.720 |
| 48 | Coeff Var. | 6.61% | NA | 6.81% | 5.35% | 6.36% | 6.02% | 13.35% | 8.54% | 5.49% | 2.63% | 10.47% | 9.49% | 4.43% | 9.08% |
| 48 | Max | 81.341 | NA | 79.697 | 81.341 | 80.106 | 69.285 | 90.012 | 90.070 | 79.610 | 78.981 | 82.644 | 87.108 | 80.216 | 90.070 |
| 48 | Min | 66.781 | NA | 66.781 | 73.587 | 65.292 | 57.193 | 58.826 | 68.447 | 69.236 | 72.769 | 61.592 | 65.099 | 71.335 | 57.193 |
| 48 | Count | 9 | NA | 6 | 3 | 9 | 9 | 11 | 9 | 9 | 10 | 9 | 9 | 9 | 93 |

## Table 19

- title: UNC0 ETW Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 50
- extraction: automatic
- in_table_title: UNC0 Normalized Strength ETW Condition by Batch and Company
- note: column A01: one 'NA' is printed in a cell spanning rows Average, Std Dev., Coeff Var., Max, Min, Count; it is repeated in each of them

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | Average | 64.278 | NA | 64.812 | 63.299 | 69.282 | 67.249 | 65.138 | 64.172 | 66.064 | 67.531 | 65.000 | 63.154 | 65.999 | 65.675 |
| 50 | Std Dev. | 5.289 | NA | 5.181 | 5.834 | 8.504 | 3.886 | 4.855 | 6.979 | 5.744 | 7.964 | 2.861 | 5.265 | 5.554 | 5.916 |
| 50 | Coeff Var. | 8.23% | NA | 7.99% | 9.22% | 12.27% | 5.78% | 7.45% | 10.88% | 8.69% | 11.79% | 4.40% | 8.34% | 8.41% | 9.01% |
| 50 | Max | 70.950 | NA | 70.950 | 69.827 | 80.962 | 72.860 | 74.624 | 73.658 | 71.253 | 80.766 | 69.565 | 70.912 | 74.475 | 80.962 |
| 50 | Min | 53.938 | NA | 53.938 | 54.357 | 57.983 | 61.830 | 59.480 | 48.662 | 54.001 | 55.529 | 60.534 | 52.695 | 55.198 | 48.662 |
| 50 | Count | 17 | NA | 11 | 6 | 9 | 9 | 8 | 10 | 10 | 9 | 7 | 9 | 10 | 98 |

## Table 20

- title: OHC1 RTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 53
- extraction: automatic
- in_table_title: OHC1 Normalized Strength RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 53 | Average | 49.083 | 49.778 | 48.719 | 48.638 | 49.030 | 49.289 | 49.866 | 49.335 | 48.983 | 48.580 | 48.416 | 50.349 | 49.253 | 49.193 |
| 53 | Std Dev. | 1.793 | 1.679 | 0.997 | 2.475 | 1.187 | 1.498 | 1.618 | 2.020 | 0.790 | 1.846 | 1.715 | 1.517 | 1.160 | 1.591 |
| 53 | Coeff Var. | 3.65% | 3.37% | 2.05% | 5.09% | 2.42% | 3.04% | 3.24% | 4.10% | 1.61% | 3.80% | 3.54% | 3.01% | 2.36% | 3.23% |
| 53 | Max | 50.993 | 50.993 | 49.756 | 50.974 | 51.308 | 51.588 | 53.547 | 52.313 | 50.105 | 49.835 | 50.580 | 52.684 | 50.851 | 53.547 |
| 53 | Min | 43.909 | 46.316 | 47.400 | 43.909 | 47.019 | 46.152 | 47.783 | 45.453 | 47.607 | 44.643 | 44.805 | 48.378 | 47.320 | 43.909 |
| 53 | Count | 19 | 7 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 9 | 99 |

## Table 21

- title: OHC1 ETW Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 55
- extraction: automatic
- in_table_title: OHC1 Normalized Strength ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 55 | Average | 35.515 | 36.526 | 35.204 | 34.647 | 35.792 | 35.998 | 34.969 | 35.025 | 35.405 | 35.242 | 35.018 | 35.853 | 36.876 | 35.556 |
| 55 | Std Dev. | 1.445 | 1.611 | 0.896 | 1.072 | 1.883 | 1.498 | 1.067 | 0.993 | 1.383 | 1.393 | 1.166 | 1.620 | 1.867 | 1.486 |
| 55 | Coeff Var. | 4.07% | 4.41% | 2.54% | 3.09% | 5.26% | 4.16% | 3.05% | 2.83% | 3.91% | 3.95% | 3.33% | 4.52% | 5.06% | 4.18% |
| 55 | Max | 38.956 | 38.956 | 36.163 | 36.278 | 39.216 | 38.771 | 36.170 | 36.542 | 37.292 | 37.424 | 36.905 | 38.458 | 39.780 | 39.780 |
| 55 | Min | 33.080 | 33.628 | 34.144 | 33.080 | 33.148 | 34.256 | 33.309 | 33.362 | 33.659 | 33.322 | 33.378 | 34.354 | 34.143 | 33.080 |
| 55 | Count | 19 | 7 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 10 | 8 | 9 | 100 |

## Table 22

- title: LT CTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 58
- extraction: automatic
- in_table_title: LT Normalized Strength CTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 58 | Average | 357.389 | 351.032 | 363.543 | 357.659 | 350.159 | 371.548 | 337.760 | 343.444 | 333.909 | 347.337 | 346.235 | 321.642 | 392.378 | 350.559 |
| 58 | Std Dev. | 12.620 | 13.152 | 12.182 | 9.681 | 15.153 | 12.333 | 15.833 | 18.719 | 18.050 | 11.168 | 21.918 | 28.359 | 9.942 | 24.097 |
| 58 | Coeff Var. | 3.53% | 3.75% | 3.35% | 2.71% | 4.33% | 3.32% | 4.69% | 5.45% | 5.41% | 3.22% | 6.33% | 8.82% | 2.53% | 6.87% |
| 58 | Max | 379.970 | 365.950 | 379.970 | 373.715 | 370.680 | 389.723 | 359.500 | 362.058 | 359.779 | 363.285 | 372.951 | 363.820 | 404.634 | 404.634 |
| 58 | Min | 325.692 | 325.692 | 341.805 | 346.196 | 327.699 | 350.960 | 314.821 | 313.344 | 295.696 | 329.043 | 310.287 | 269.227 | 373.673 | 269.227 |
| 58 | Count | 22 | 8 | 8 | 6 | 9 | 9 | 8 | 9 | 9 | 8 | 9 | 10 | 8 | 101 |

## Table 23

- title: LT RTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 61
- extraction: automatic
- in_table_title: LT Normalized Strength RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 61 | Average | 362.693 | 357.495 | 371.282 | 359.303 | 379.118 | 361.100 | 366.255 | 343.153 | 346.532 | 381.931 | 346.382 | 330.608 | 400.749 | 361.929 |
| 61 | Std Dev. | 16.057 | 9.558 | 12.270 | 22.359 | 24.063 | 13.734 | 28.312 | 29.001 | 34.603 | 11.884 | 27.057 | 30.924 | 18.310 | 29.775 |
| 61 | Coeff Var. | 4.43% | 2.67% | 3.30% | 6.22% | 6.35% | 3.80% | 7.73% | 8.45% | 9.99% | 3.11% | 7.81% | 9.35% | 4.57% | 8.23% |
| 61 | Max | 392.322 | 370.552 | 392.322 | 391.912 | 407.079 | 379.155 | 402.359 | 373.059 | 401.632 | 404.009 | 375.023 | 366.703 | 428.406 | 428.406 |
| 61 | Min | 325.685 | 343.573 | 360.049 | 325.685 | 323.035 | 334.033 | 328.854 | 294.158 | 300.382 | 370.857 | 298.688 | 278.318 | 367.311 | 278.318 |
| 61 | Count | 18 | 6 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 99 |

## Table 24

- title: LT ETW Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 63
- extraction: automatic
- in_table_title: LT Normalized Strength ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 63 | Average | 333.504 | 317.517 | 342.287 | 348.964 | 315.613 | 331.085 | 336.173 | 327.714 | 332.217 | 373.061 | 334.144 | 289.018 | 360.110 | 334.837 |
| 63 | Std Dev. | 38.823 | 47.214 | 31.354 | 25.623 | 36.305 | 11.681 | 23.450 | 24.456 | 28.623 | 17.806 | 14.219 | 14.355 | 11.714 | 32.161 |
| 63 | Coeff Var. | 11.64% | 14.87% | 9.16% | 7.34% | 11.50% | 3.53% | 6.98% | 7.46% | 8.62% | 4.77% | 4.26% | 4.97% | 3.25% | 9.61% |
| 63 | Max | 373.234 | 366.596 | 365.481 | 373.234 | 373.828 | 347.789 | 363.381 | 362.519 | 362.887 | 399.874 | 363.083 | 306.996 | 379.264 | 399.874 |
| 63 | Min | 244.533 | 244.533 | 296.033 | 309.103 | 267.229 | 313.086 | 304.802 | 293.684 | 287.692 | 340.226 | 315.959 | 272.831 | 344.398 | 244.533 |
| 63 | Count | 18 | 8 | 4 | 6 | 9 | 9 | 6 | 7 | 7 | 9 | 8 | 6 | 9 | 88 |

## Table 25

- title: UNT0 CTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 66
- extraction: automatic
- in_table_title: UNT0 Normalized Strength CTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 66 | Average | 152.578 | 150.313 | 151.415 | 156.382 | 160.545 | 160.704 | 141.912 | 133.841 | 143.028 | 156.635 | 160.965 | 126.733 | 170.879 | 151.206 |
| 66 | Std Dev. | 5.172 | 6.820 | 2.379 | 2.941 | 3.299 | 4.609 | 5.084 | 7.758 | 3.288 | 4.139 | 3.399 | 6.204 | 4.411 | 13.283 |
| 66 | Coeff Var. | 3.39% | 4.54% | 1.57% | 1.88% | 2.06% | 2.87% | 3.58% | 5.80% | 2.30% | 2.64% | 2.11% | 4.90% | 2.58% | 8.78% |
| 66 | Max | 159.854 | 158.607 | 153.556 | 159.854 | 167.134 | 168.782 | 149.406 | 144.259 | 147.253 | 161.809 | 166.757 | 132.016 | 177.646 | 177.646 |
| 66 | Min | 142.064 | 142.064 | 147.675 | 153.462 | 155.401 | 154.202 | 133.441 | 120.953 | 137.207 | 151.140 | 155.138 | 113.463 | 163.256 | 113.463 |
| 66 | Count | 19 | 7 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 9 | 99 |

## Table 26

- title: UNT0 RTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 68
- extraction: automatic
- in_table_title: UNT0 Normalized Strength RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 68 | Average | 171.385 | 172.748 | 169.150 | 172.257 | 178.860 | 183.087 | 165.177 | 160.538 | 163.784 | 181.508 | 180.872 | 155.636 | 188.427 | 172.962 |
| 68 | Std Dev. | 9.304 | 5.910 | 7.024 | 14.175 | 9.913 | 6.950 | 5.331 | 9.896 | 4.453 | 6.246 | 2.966 | 2.683 | 5.315 | 12.108 |
| 68 | Coeff Var. | 5.43% | 3.42% | 4.15% | 8.23% | 5.54% | 3.80% | 3.23% | 6.16% | 2.72% | 3.44% | 1.64% | 1.72% | 2.82% | 7.00% |
| 68 | Max | 182.904 | 181.648 | 178.704 | 182.904 | 189.105 | 191.406 | 171.385 | 169.709 | 170.317 | 188.463 | 184.239 | 159.397 | 194.189 | 194.189 |
| 68 | Min | 143.990 | 165.214 | 157.619 | 143.990 | 153.692 | 171.712 | 156.701 | 136.687 | 154.525 | 171.726 | 174.416 | 151.992 | 179.462 | 136.687 |
| 68 | Count | 18 | 6 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 9 | 98 |

## Table 27

- title: UNT0 ETW Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 70
- extraction: automatic
- in_table_title: UNT0 Normalized Strength ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 70 | Average | 179.232 | 178.706 | 175.673 | 183.317 | 183.973 | 173.691 | 177.571 | 165.442 | 175.659 | 178.973 | 179.938 | 171.329 | 181.909 | 176.995 |
| 70 | Std Dev. | 6.718 | 3.991 | 8.062 | 6.081 | 3.727 | 11.586 | 4.405 | 9.501 | 4.002 | 10.624 | 4.195 | 4.524 | 2.584 | 8.259 |
| 70 | Coeff Var. | 3.75% | 2.23% | 4.59% | 3.32% | 2.03% | 6.67% | 2.48% | 5.74% | 2.28% | 5.94% | 2.33% | 2.64% | 1.42% | 4.67% |
| 70 | Max | 189.181 | 185.594 | 188.028 | 189.181 | 187.946 | 182.432 | 185.620 | 173.958 | 183.062 | 190.235 | 188.827 | 175.745 | 185.944 | 190.235 |
| 70 | Min | 165.977 | 174.889 | 165.977 | 172.579 | 177.497 | 151.088 | 171.280 | 146.660 | 169.796 | 158.753 | 174.355 | 162.050 | 177.063 | 146.660 |
| 70 | Count | 18 | 6 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 99 |

## Table 28

- title: OHT1 CTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 73
- extraction: automatic
- in_table_title: OHT1 Normalized Strength CTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 73 | Average | 57.754 | 55.653 | 57.885 | 60.076 | 57.886 | 57.753 | 54.437 | 55.963 | 53.153 | 58.310 | 54.026 | 49.113 | 61.996 | 56.211 |
| 73 | Std Dev. | 2.433 | 1.581 | 1.772 | 1.582 | 1.965 | 1.140 | 2.398 | 3.857 | 1.362 | 2.163 | 1.815 | 2.806 | 1.943 | 3.927 |
| 73 | Coeff Var. | 4.21% | 2.84% | 3.06% | 2.63% | 3.39% | 1.97% | 4.41% | 6.89% | 2.56% | 3.71% | 3.36% | 5.71% | 3.13% | 6.99% |
| 73 | Max | 62.524 | 57.344 | 60.531 | 62.524 | 59.950 | 59.298 | 59.852 | 61.129 | 55.073 | 61.403 | 56.628 | 54.382 | 65.221 | 65.221 |
| 73 | Min | 53.645 | 53.645 | 55.549 | 58.229 | 54.387 | 55.944 | 51.134 | 49.420 | 51.389 | 54.873 | 50.937 | 46.315 | 57.993 | 46.315 |
| 73 | Count | 19 | 7 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 100 |

## Table 29

- title: OHT1 RTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 75
- extraction: automatic
- in_table_title: OHT1 Normalized Strength RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 75 | Average | 59.003 | 57.688 | 58.629 | 60.913 | 60.007 | 60.613 | 58.605 | 58.378 | 56.641 | 61.317 | 59.922 | 51.947 | 64.438 | 59.079 |
| 75 | Std Dev. | 2.350 | 2.133 | 0.705 | 2.636 | 0.864 | 2.257 | 1.713 | 2.348 | 1.209 | 1.458 | 3.697 | 2.471 | 1.501 | 3.589 |
| 75 | Coeff Var. | 3.98% | 3.70% | 1.20% | 4.33% | 1.44% | 3.72% | 2.92% | 4.02% | 2.13% | 2.38% | 6.17% | 4.76% | 2.33% | 6.08% |
| 75 | Max | 64.610 | 60.825 | 59.915 | 64.610 | 61.112 | 64.590 | 61.951 | 62.687 | 57.908 | 63.748 | 68.039 | 54.940 | 67.266 | 68.039 |
| 75 | Min | 54.120 | 54.120 | 57.922 | 57.440 | 58.594 | 58.015 | 56.184 | 54.486 | 54.665 | 59.638 | 54.411 | 47.802 | 61.973 | 47.802 |
| 75 | Count | 19 | 7 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 100 |

## Table 30

- title: OHT1 ETW Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 77
- extraction: automatic
- in_table_title: OHT1 Normalized Strength ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 77 | Average | 66.966 | 65.543 | 67.701 | 67.760 | 68.805 | 65.555 | 64.132 | 64.733 | 65.451 | 67.390 | 69.816 | 62.664 | 69.311 | 66.570 |
| 77 | Std Dev. | 2.850 | 2.608 | 3.847 | 1.715 | 1.295 | 1.730 | 1.257 | 2.157 | 3.304 | 2.051 | 1.171 | 1.881 | 1.847 | 2.976 |
| 77 | Coeff Var. | 4.26% | 3.98% | 5.68% | 2.53% | 1.88% | 2.64% | 1.96% | 3.33% | 5.05% | 3.04% | 1.68% | 3.00% | 2.66% | 4.47% |
| 77 | Max | 72.587 | 69.218 | 72.587 | 70.579 | 70.541 | 67.941 | 65.768 | 69.044 | 69.278 | 69.944 | 71.326 | 65.975 | 71.048 | 72.587 |
| 77 | Min | 62.154 | 62.926 | 62.154 | 65.716 | 66.650 | 63.188 | 61.153 | 61.231 | 59.869 | 64.211 | 67.260 | 60.096 | 65.204 | 59.869 |
| 77 | Count | 20 | 7 | 6 | 7 | 9 | 9 | 9 | 9 | 9 | 10 | 9 | 9 | 10 | 103 |

## Table 31

- title: SBS RTD Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 80
- extraction: automatic
- in_table_title: Short Beam Strength as measured RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 80 | Average | 17.125 | 17.396 | 16.980 | 16.999 | 17.302 | 17.489 | 17.367 | 16.904 | 18.019 | 17.366 | 16.820 | 15.383 | 17.210 | 17.098 |
| 80 | Std Dev. | 0.430 | 0.328 | 0.586 | 0.214 | 0.323 | 0.333 | 0.218 | 0.147 | 0.083 | 0.238 | 0.663 | 1.258 | 0.159 | 0.786 |
| 80 | Coeff Var. | 2.51% | 1.88% | 3.45% | 1.26% | 1.87% | 1.90% | 1.25% | 0.87% | 0.46% | 1.37% | 3.94% | 8.18% | 0.92% | 4.60% |
| 80 | Max | 17.780 | 17.780 | 17.649 | 17.398 | 17.719 | 17.893 | 17.598 | 17.111 | 18.129 | 17.710 | 17.321 | 17.088 | 17.433 | 18.129 |
| 80 | Min | 16.198 | 16.916 | 16.198 | 16.794 | 16.638 | 16.732 | 16.911 | 16.681 | 17.912 | 17.047 | 15.382 | 13.531 | 16.944 | 13.531 |
| 80 | Count | 18 | 6 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 10 | 9 | 9 | 100 |

## Table 32

- title: SBS ETW Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 83
- extraction: automatic
- in_table_title: Short Beam Strength as measured ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 83 | Average | 8.252 | 8.175 | 8.257 | 8.338 | 8.368 | 8.107 | 8.007 | 8.212 | 8.643 | 8.690 | 8.219 | 7.688 | 8.054 | 8.229 |
| 83 | Std Dev. | 0.242 | 0.119 | 0.175 | 0.381 | 0.189 | 0.276 | 0.097 | 0.446 | 0.216 | 0.423 | 0.123 | 0.490 | 0.187 | 0.388 |
| 83 | Coeff Var. | 2.93% | 1.45% | 2.12% | 4.57% | 2.26% | 3.41% | 1.22% | 5.43% | 2.50% | 4.87% | 1.50% | 6.37% | 2.32% | 4.72% |
| 83 | Max | 8.820 | 8.419 | 8.538 | 8.820 | 8.788 | 8.629 | 8.193 | 9.093 | 8.982 | 9.452 | 8.413 | 8.540 | 8.303 | 9.452 |
| 83 | Min | 7.863 | 8.038 | 8.074 | 7.863 | 8.168 | 7.862 | 7.869 | 7.839 | 8.366 | 8.246 | 8.103 | 7.068 | 7.871 | 7.068 |
| 83 | Count | 19 | 7 | 6 | 6 | 9 | 7 | 9 | 8 | 9 | 9 | 9 | 9 | 9 | 97 |

## Table 33

- title: IPS CTD 0.2% Offset Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 85
- extraction: automatic
- in_table_title: IPS 0.2% Offset Strength as measured CTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 85 | Average | 11.295 | 11.091 | 11.374 | 11.420 | 10.733 | 10.456 | 10.605 | 10.325 | 10.915 | 10.898 | 10.712 | 10.472 | 10.583 | 10.776 |
| 85 | Std Dev. | 0.238 | 0.200 | 0.226 | 0.151 | 0.225 | 0.122 | 0.141 | 0.137 | 0.289 | 0.377 | 0.083 | 0.626 | 0.134 | 0.413 |
| 85 | Coeff Var. | 2.10% | 1.81% | 1.98% | 1.33% | 2.10% | 1.17% | 1.33% | 1.33% | 2.65% | 3.46% | 0.77% | 5.98% | 1.27% | 3.83% |
| 85 | Max | 11.661 | 11.460 | 11.661 | 11.565 | 11.143 | 10.610 | 10.895 | 10.600 | 11.611 | 11.604 | 10.815 | 11.787 | 10.839 | 11.787 |
| 85 | Min | 10.779 | 10.779 | 11.067 | 11.211 | 10.442 | 10.287 | 10.421 | 10.110 | 10.630 | 10.207 | 10.599 | 9.615 | 10.416 | 9.615 |
| 85 | Count | 21 | 7 | 7 | 7 | 9 | 9 | 8 | 9 | 9 | 9 | 9 | 8 | 8 | 99 |

## Table 34

- title: IPS RTD 0.2% Offset Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 87
- extraction: automatic
- in_table_title: IPS 0.2% Offset Strength as measured RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 87 | Average | 7.756 | 7.591 | 7.799 | 7.869 | 7.811 | 7.632 | 7.568 | 7.433 | 7.772 | 7.693 | 7.800 | 7.440 | 7.797 | 7.679 |
| 87 | Std Dev. | 0.218 | 0.077 | 0.195 | 0.268 | 0.112 | 0.148 | 0.190 | 0.094 | 0.208 | 0.099 | 0.076 | 0.090 | 0.076 | 0.195 |
| 87 | Coeff Var. | 2.81% | 1.02% | 2.51% | 3.40% | 1.44% | 1.94% | 2.51% | 1.26% | 2.68% | 1.28% | 0.97% | 1.20% | 0.98% | 2.54% |
| 87 | Max | 8.279 | 7.698 | 8.117 | 8.279 | 8.003 | 7.892 | 7.694 | 7.628 | 8.157 | 7.847 | 7.905 | 7.575 | 7.942 | 8.279 |
| 87 | Min | 7.481 | 7.481 | 7.600 | 7.591 | 7.655 | 7.424 | 7.016 | 7.296 | 7.530 | 7.535 | 7.694 | 7.296 | 7.653 | 7.016 |
| 87 | Count | 16 | 5 | 6 | 5 | 11 | 9 | 11 | 10 | 9 | 9 | 9 | 9 | 13 | 106 |

## Table 35

- title: IPS RTD Strength at 5% Strain Summary Statistics by Unit
- kind: stats
- pdf_page: 90
- extraction: automatic
- in_table_title: IPS Strength at 5% Strain as measured RTD Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 90 | Average | 13.225 | 13.036 | 13.238 | 13.401 | 13.283 | 13.163 | 13.052 | 12.959 | 13.078 | 13.178 | 13.446 | 12.847 | 13.429 | 13.157 |
| 90 | Std Dev. | 0.211 | 0.170 | 0.131 | 0.167 | 0.206 | 0.195 | 0.147 | 0.234 | 0.317 | 0.181 | 0.186 | 0.189 | 0.164 | 0.263 |
| 90 | Coeff Var. | 1.60% | 1.30% | 0.99% | 1.25% | 1.55% | 1.48% | 1.12% | 1.80% | 2.42% | 1.37% | 1.38% | 1.47% | 1.22% | 2.00% |
| 90 | Max | 13.609 | 13.228 | 13.405 | 13.609 | 13.622 | 13.426 | 13.297 | 13.260 | 13.581 | 13.375 | 13.670 | 13.149 | 13.733 | 13.733 |
| 90 | Min | 12.855 | 12.855 | 13.092 | 13.200 | 13.017 | 12.835 | 12.875 | 12.482 | 12.730 | 12.870 | 13.215 | 12.530 | 13.169 | 12.482 |
| 90 | Count | 12 | 4 | 4 | 4 | 9 | 9 | 9 | 8 | 9 | 9 | 4 | 9 | 10 | 88 |

## Table 36

- title: IPS ETW 0.2% Offset Strength Summary Statistics by Unit
- kind: stats
- pdf_page: 92
- extraction: automatic
- in_table_title: IPS 0.2% Offset Strength as measured ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 92 | Average | 3.307 | 3.325 | 3.407 | 3.169 | 3.154 | 3.138 | 3.129 | 3.093 | 3.260 | 3.263 | 3.273 | 2.968 | 3.420 | 3.214 |
| 92 | Std Dev. | 0.153 | 0.053 | 0.171 | 0.115 | 0.138 | 0.158 | 0.134 | 0.051 | 0.050 | 0.112 | 0.083 | 0.063 | 0.042 | 0.163 |
| 92 | Coeff Var. | 4.63% | 1.60% | 5.03% | 3.63% | 4.37% | 5.03% | 4.27% | 1.65% | 1.53% | 3.43% | 2.54% | 2.12% | 1.23% | 5.06% |
| 92 | Max | 3.627 | 3.408 | 3.627 | 3.304 | 3.404 | 3.462 | 3.376 | 3.167 | 3.331 | 3.416 | 3.374 | 3.068 | 3.479 | 3.627 |
| 92 | Min | 3.050 | 3.262 | 3.090 | 3.050 | 3.034 | 2.864 | 2.890 | 3.022 | 3.168 | 3.030 | 3.137 | 2.895 | 3.349 | 2.864 |
| 92 | Count | 20 | 7 | 7 | 6 | 10 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 10 | 103 |

## Table 37

- title: IPS ETW Strength at 5% Strain Summary Statistics by Unit
- kind: stats
- pdf_page: 96
- extraction: automatic
- in_table_title: IPS Strength at 5% Strain as measured ETW Condition by Batch and Company

| page | row | Qual. | A01 | A02 | A03 | A2 | A4 | A5 | A6 | A8 | A9 | A10 | A11 | A12 | Pooled |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 96 | Average | 5.538 | 5.569 | 5.696 | 5.343 | 5.523 | 5.282 | 5.225 | 5.302 | 5.491 | 5.481 | 5.587 | 5.202 | 5.777 | 5.451 |
| 96 | Std Dev. | 0.187 | 0.097 | 0.167 | 0.101 | 0.216 | 0.196 | 0.198 | 0.098 | 0.114 | 0.147 | 0.155 | 0.092 | 0.176 | 0.231 |
| 96 | Coeff Var. | 3.38% | 1.74% | 2.94% | 1.90% | 3.91% | 3.71% | 3.79% | 1.84% | 2.07% | 2.68% | 2.78% | 1.77% | 3.05% | 4.24% |
| 96 | Max | 5.954 | 5.706 | 5.954 | 5.456 | 5.937 | 5.621 | 5.566 | 5.452 | 5.632 | 5.779 | 5.915 | 5.366 | 6.119 | 6.119 |
| 96 | Min | 5.178 | 5.447 | 5.434 | 5.178 | 5.231 | 5.063 | 4.979 | 5.186 | 5.267 | 5.269 | 5.417 | 5.045 | 5.542 | 4.979 |
| 96 | Count | 19 | 7 | 6 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 100 |
