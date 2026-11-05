---
material: steel-4130-qt
alloy: AISI 4130
temper_or_condition: Quenched and tempered
product_forms: Tubing
bases: S
source_document: MIL-HDBK-5J, Department of Defense Handbook: Metallic Materials and Elements for Aerospace Vehicle Structures, 31 January 2003 (Distribution Statement A: approved for public release; distribution is unlimited)
source_url: https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf
source_file: references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf
source_sha256: 67a4c320cc6c7f23ad155e428a21b3a940e489458a1570026e9b83c2901e6777
source_tables: 2.3.1.0(c2) (PDF page 72, printed page 2-18)
extraction: automatic (scripts/materials/extract_mil_hdbk_5.py); no manual transcription
units: as printed in the source (ksi; 10³ ksi; percent; lb/in.³); values copied digit for digit, never rounded or converted
---

# AISI 4130 Quenched and tempered — MIL-HDBK-5J design allowables

Each table row is one column of the source table (one thickness range and basis).
Cell syntax: `64` = value as printed; `51 [a]` = value with footnote marker a;
`—` = nothing printed ("..." or blank in the source); `— [c]` = no value, footnote c only.
Values that the source prints once across several columns (E, Ec, G, μ, ω and some others)
are repeated in every column they span. S-basis values are specification minima; A and B
are statistically based (MIL-HDBK-5J Section 1.4.1.1).

## Table 2.3.1.0(c2)

- title: Design Mechanical and Physical Properties of Air Melted Low-Alloy Steels
- pdf_page: 72
- printed_page: 2-18
- extraction: automatic
- elongation_label: e, percent
- note: e: 'See Table 2.3.1.0(e)' printed for columns 1, 2, 3
- not_extracted: C, K, and α: See Figure 2.3.1.0

| col | alloy | specification | form | condition | thickness (in.) | basis | Ftu (ksi) | Fty (ksi) | Fcy (ksi) | Fsu (ksi) | Fbru e/D=1.5 (ksi) | Fbru e/D=2.0 (ksi) | Fbry e/D=1.5 (ksi) | Fbry e/D=2.0 (ksi) | e (percent) | E (10³ ksi) | Ec (10³ ksi) | G (10³ ksi) | μ | ω (lb/in.³) |
|---:|:---|:---|:---|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | AISI 4130 | AMS 6361 AMS-T-6736 | Tubing | Quenched and tempered [a] | ≤0.188 | S | 125 | 100 | 109 | 75 | 194 | 251 | 146 | 175 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |
| 2 | AISI 4130 | AMS 6362 AMS-T-6736 | Tubing | Quenched and tempered [a] | ≤0.188 | S | 150 | 135 | 141 | 90 | 231 | 285 | 210 | 232 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |
| 3 | AISI 4130 | AMS-T-6736 | Tubing | Quenched and tempered [a] | All Walls | S | 180 | 165 | 173 | 108 | 277 | 342 | 257 | 284 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |

### Footnotes to Table 2.3.1.0(c2) (as printed)

- a: Design values are applicable only to parts for which the indicated Ftu has been substantiated by adequate quality control testing.

## Figures

| figure | pdf page | file | caption |
|:---|---:|:---|:---|
| 2.3.1.0 | 80 | figures/mil-hdbk-5j-p0080.png | Figure 2.3.1.0. Effect of temperature on the physical properties of 4130 and 4340 alloy steels. |
| 2.3.1.1.1 | 81 | figures/mil-hdbk-5j-p0081.png | Figure 2.3.1.1.1. Effect of temperature on the tensile ultimate strength (Ftu) and tensile yield strength (Fty) of AISI low-alloy steels (all products). |
| 2.3.1.1.4 | 83 | figures/mil-hdbk-5j-p0083.png | Figure 2.3.1.1.4. Effect of temperature on the tensile and compressive modulus (E and Ec) of AISI low-alloy steels. |
