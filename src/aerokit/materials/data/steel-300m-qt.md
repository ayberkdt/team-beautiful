---
material: steel-300m-qt
alloy: 0.40C 300M
temper_or_condition: Quenched and tempered
product_forms: Bar, forging, tubing
bases: S
source_document: MIL-HDBK-5J, Department of Defense Handbook: Metallic Materials and Elements for Aerospace Vehicle Structures, 31 January 2003 (Distribution Statement A: approved for public release; distribution is unlimited)
source_url: https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf
source_file: references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf
source_sha256: 67a4c320cc6c7f23ad155e428a21b3a940e489458a1570026e9b83c2901e6777
source_tables: 2.3.1.0(f1) (PDF page 76, printed page 2-22)
extraction: automatic (scripts/materials/extract_mil_hdbk_5.py); no manual transcription
units: as printed in the source (ksi; 10³ ksi; percent; lb/in.³); values copied digit for digit, never rounded or converted
---

# 0.40C 300M Quenched and tempered — MIL-HDBK-5J design allowables

Each table row is one column of the source table (one thickness range and basis).
Cell syntax: `64` = value as printed; `51 [a]` = value with footnote marker a;
`—` = nothing printed ("..." or blank in the source); `— [c]` = no value, footnote c only.
Values that the source prints once across several columns (E, Ec, G, μ, ω and some others)
are repeated in every column they span. S-basis values are specification minima; A and B
are statistically based (MIL-HDBK-5J Section 1.4.1.1).

## Table 2.3.1.0(f1)

- title: Design Mechanical and Physical Properties of Low-Alloy Steels
- pdf_page: 76
- printed_page: 2-22
- extraction: automatic
- elongation_label: e, percent:
- not_extracted: C, K, and α: See Figure 2.3.1.0

| col | alloy | specification | form | condition | thickness (in.) | basis | Ftu (ksi) | Fty (ksi) | Fcy (ksi) | Fsu (ksi) | Fbru e/D=1.5 (ksi) | Fbru e/D=2.0 (ksi) | Fbry e/D=1.5 (ksi) | Fbry e/D=2.0 (ksi) | e L (percent) | e LT (percent) | E (10³ ksi) | Ec (10³ ksi) | G (10³ ksi) | μ | ω (lb/in.³) |
|---:|:---|:---|:---|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 0.40C 300M | AMS 6417 | Bar, forging, tubing | Quenched and tempered [b] | — [f] | S | 270 | 220 | 236 | 162 | 414 [g] | 506 [g] | 344 [c] | 379 [c] | 8 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |
| 8 | 0.42C 300M | AMS 6257 AMS 6419 | Bar, forging, tubing | Quenched and tempered [b] | — [f] | S | 280 | 230 | 247 | 168 | 430 [g] | 525 [g] | 360 [c] | 396 [c] | 7 | — | 29.0 | 29.0 | 11.0 | 0.32 | 0.283 |

### Footnotes to Table 2.3.1.0(f1) (as printed)

- a: Applicable to consumable-electrode vacuum-melted material only.
- b: Design values are applicable only to parts for which the indicated Ftu has been substantiated by adequate quality control testing.
- c: Thickness≤ 1.70 in. for quenching in molten salt at desired tempering temperature (martempering); ≤2.50 in. for quenching in oil at flow rate of 200 feet/min.
- d: Thickness≤ 3.50 in. for quenching in molten salt at desired tempering temperature (martempering); ≤5.00 in. for quenching in oil at flow rate of 200 feet/min.
- e: Thickness≤ 1.70 in. for quenching in molten salt at desired tempering temperature (martempering); ≤2.50 in. for quenching in oil at flow rate of 200 feet/min.; ≤3.50 in. for quenching in water at a flow rate of 200 feet/min.
- f: Thickness ≤5.00 in. for quenching in oil at a flow rate of 200 feet/min.
- g: Bearing values are “dry pin” values per Section 1.4.7.1.

## Figures

| figure | pdf page | file | caption |
|:---|---:|:---|:---|
| 2.3.1.1.1 | 81 | figures/mil-hdbk-5j-p0081.png | Figure 2.3.1.1.1. Effect of temperature on the tensile ultimate strength (Ftu) and tensile yield strength (Fty) of AISI low-alloy steels (all products). |
| 2.3.1.1.4 | 83 | figures/mil-hdbk-5j-p0083.png | Figure 2.3.1.1.4. Effect of temperature on the tensile and compressive modulus (E and Ec) of AISI low-alloy steels. |
