---
material: steel-4130-nt
alloy: AISI 4130
temper_or_condition: Normalized and tempered, stress relieved
product_forms: Sheet, strip, plate, and tubing
bases: S
source_document: MIL-HDBK-5J, Department of Defense Handbook: Metallic Materials and Elements for Aerospace Vehicle Structures, 31 January 2003 (Distribution Statement A: approved for public release; distribution is unlimited)
source_url: https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf
source_file: references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf
source_sha256: 67a4c320cc6c7f23ad155e428a21b3a940e489458a1570026e9b83c2901e6777
source_tables: 2.3.1.0(c1) (PDF page 71, printed page 2-17)
extraction: automatic (scripts/materials/extract_mil_hdbk_5.py); no manual transcription
units: as printed in the source (ksi; 10³ ksi; percent; lb/in.³); values copied digit for digit, never rounded or converted
---

# AISI 4130 Normalized and tempered, stress relieved — MIL-HDBK-5J design allowables

Each table row is one column of the source table (one thickness range and basis).
Cell syntax: `64` = value as printed; `51 [a]` = value with footnote marker a;
`—` = nothing printed ("..." or blank in the source); `— [c]` = no value, footnote c only.
Values that the source prints once across several columns (E, Ec, G, μ, ω and some others)
are repeated in every column they span. S-basis values are specification minima; A and B
are statistically based (MIL-HDBK-5J Section 1.4.1.1).

## Table 2.3.1.0(c1)

- title: Design Mechanical and Physical Properties of Air Melted Low-Alloy Steels
- pdf_page: 71
- printed_page: 2-17
- extraction: automatic
- elongation_label: e, percent
- note: e: 'See Table 2.3.1.0(d)' printed for columns 1, 2, 3, 4, 5, 6
- not_extracted: C, K, and α: See Figure 2.3.1.0

| col | alloy | specification | form | condition | thickness (in.) | basis | Ftu (ksi) | Fty (ksi) | Fcy (ksi) | Fsu (ksi) | Fbru e/D=1.5 (ksi) | Fbru e/D=2.0 (ksi) | Fbry e/D=1.5 (ksi) | Fbry e/D=2.0 (ksi) | e (percent) | E (10³ ksi) | Ec (10³ ksi) | G (10³ ksi) | μ | ω (lb/in.³) |
|---:|:---|:---|:---|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | AISI 4130 | AMS 6360 AMS 6373 AMS 6374 AMS-T-6736 AMS-S-18729 | Sheet, strip, plate, and tubing | Normalized and tempered, stress relieved [b] | ≤0.188 | S | 95 | 75 | 75 | 57 | — | 200 | — | 129 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |
| 2 | AISI 4130 | AMS 6360 AMS 6373 AMS 6374 AMS-T-6736 AMS-S-18729 | Sheet, strip, plate, and tubing | Normalized and tempered, stress relieved [b] | >0.188 | S | 90 | 70 | 70 | 54 | — | 190 | — | 120 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |

### Footnotes to Table 2.3.1.0(c1) (as printed)

- a: Noncurrent specification.
- b: Design values are applicable only to parts for which the indicated Ftu has been substantiated by adequate quality control testing.

## Figures

| figure | pdf page | file | caption |
|:---|---:|:---|:---|
| 2.3.1.0 | 80 | figures/mil-hdbk-5j-p0080.png | Figure 2.3.1.0. Effect of temperature on the physical properties of 4130 and 4340 alloy steels. |
| 2.3.1.1.1 | 81 | figures/mil-hdbk-5j-p0081.png | Figure 2.3.1.1.1. Effect of temperature on the tensile ultimate strength (Ftu) and tensile yield strength (Fty) of AISI low-alloy steels (all products). |
| 2.3.1.1.4 | 83 | figures/mil-hdbk-5j-p0083.png | Figure 2.3.1.1.4. Effect of temperature on the tensile and compressive modulus (E and Ec) of AISI low-alloy steels. |
