# Alloy-level datasheet properties for candidate lightweight aerospace bracket/fitting materials

Scope: only materials that `src/aerokit/materials/library.py` does not already hold (7075-T6, 6061-T6, 2024-T351, Ti-6Al-4V supplier minimums and IM7/AS4-8552 plies are left out on purpose). Research date: 2026-11-01.

**Evidence tags (never upgraded):**
- **[FULL]**: I downloaded the PDF in this session and read its text myself (pdftotext). Local copies are in `C:\Users\ayber\AppData\Local\Temp\claude\D--Masaustu-Ideathon-2026\714d4e11-5f6c-4b97-92c6-474562b59cf2\scratchpad\dl_alloy\`.
- **[FETCH]**: I read the page through the WebFetch tool and asked it to quote verbatim. A model does that extraction, so this tag is weaker than [FULL] and stronger than [SNIPPET].
- **[SNIPPET]**: the value appears only in search-result text. I did not open the source.
- **UNVERIFIED (memory)**: the value comes from my background knowledge, not from a source read in this session.

**Units:** each value is given as printed, with the SI conversion in braces {…}. I used 1 ksi = 6.894757 MPa, 1 Msi = 6.894757 GPa and 1 lb/in³ = 27 679.9 kg/m³.

**Fatigue:** no datasheet I read in full gives a numeric fatigue strength (with R and cycles) for any material below. Every fatigue cell is therefore a gap.

---

## Q1. Al 7050-T7451 plate

### Takeaway
I found no producer datasheet (Arconic/Howmet, Kaiser or Constellium) that I could open. The Alcoa sheet on Prospector needs a login. The only figures available are distributor values from search snippets, and they conflict, so 7050-T7451 has no verified number in these notes.

### Cited Findings
- Density 2.83 g/cc {2830 kg/m³}. Source: a MatWeb-derived page, Aluminum Association typical data marked "NOT FOR DESIGN". Typical UTS ≈ 524 MPa, YS ≈ 469 MPa, elongation ≈ 11 %. [SNIPPET]. Link: [scribd 7050](https://www.scribd.com/document/98668921/7050)
- AMS 4050 plate table, thickness over 6.3 up to and including 51 mm, row printed as "441 MPa | 510 MPa | 9". [SNIPPET]. The search summary read this as 510 MPa minimum yield, which is not plausible. The more likely reading is Rp0.2 441 / Rm 510 / A 9 %, but the column headers were not visible. Link: [Referans Metal AMS 4050 7050-T7451](https://www.referansmetal.com/alasimli-aluminyum/product/58/levha-plaka/ams-4050-alzn6cumgzr-7050-t7451?lang=en)
- A typical range of 480–520 MPa yield and 540–590 MPa UTS, from the same distributor site. [SNIPPET]. This conflicts with the MatWeb values above. Same link.
- E ≈ 70.3 GPa in a journal table and 71.7 GPa from a German distributor. [SNIPPET]. Links: [CJME table](https://cjme.springeropen.com/articles/10.1186/s10033-020-00456-0/tables/1), [referansmetal](https://www.referansmetal.com/print/58/ams-4050-alzn6cumgzr-7050-t7451.pdf)
- Alcoa describes T7451 (formerly T73651) as having "better SCC resistance and excellent exfoliation resistance at slightly lower strength levels" than T7651. [SNIPPET]. Link: [Prospector Alcoa 7050-T7451](https://metals.ulprospector.com/ja/datasheet/e272683/alcoa-7050-t7451)
- The governing specification is SAE AMS 4050 (latest revision listed: AMS4050K, April 2021). It is paywalled. [SNIPPET]. Link: [SAE AMS4050K](https://saemobilus.sae.org/content/AMS4050K)
- Indirect only: Smiths HP gives Airware 2050-T84 as −4 % density, +8 % strength and +7 % stiffness relative to 7050-T7451. [FULL]. See Q2.

### Inferences
- The relative claims for 2050 and the snippet density of 2830 kg/m³ do not reproduce 2050's printed density of 2.70 g/cm³: 2830 × 0.96 = 2717. The comparison basis (thickness, typical or minimum) is not stated, so treat the percentages as marketing deltas, not as a way to back-calculate 7050 values.

### Gaps
- No primary 7050-T7451 typical or minimum table was read. To close this, buy AMS 4050 or MMPDS, or get a Prospector login for the Alcoa sheet.
- No fatigue data, service temperature, CO₂ figure or price.

---

## Q2. Al-Li 2050-T84, 2099-T83 and 2195-T8/T84

### Takeaway
- **2050-T84:** fully verified from a distributor sheet that reproduces the Constellium Airware data (minimums by thickness, typical E and density).
- **2099-T83:** a Smiths Metal Centres extrusion sheet [FULL], but two of its MPa conversions contradict its own ksi values.
- **2195:** no primary numeric source was opened.

### Cited Findings: Airware 2050-T84 plate
Source for this table: Smiths High Performance, "Airware® 2050 (T84 Plate)" technical datasheet, revision SHP/english/datasheets/airware-2050/11.02.2025, page 2, "Mechanical Properties" table. [FULL]. Link: [Smiths HP Airware 2050 PDF](https://www.smithshp.com/assets/pdf/aluminium/aluminium-lithium/airware-2050-aluminium-lithium-english.pdf)

| Thickness, mm (in) | UTS L min, MPa (ksi) | YS L min, MPa (ksi) | El. L min, % | K1c L-T min, MPa√m (ksi√in) |
|---|---|---|---|---|
| 12.7–38.1 (0.5–1.5) | 503 (73) | 476 (69) | 8 | 36 (33) |
| 38.1–50.8 (1.5–2) | 496 (72) | 462 (67) | 8 | 34 (31) |
| 50.8–76.2 (2–3) | 496 (72) | 462 (67) | 7 | 31 (28) |
| 76.2–101.6 (3–4) | 490 (71) | 462 (67) | 6 | 29 (26) |
| 101.6–127 (4–5) | 490 (71) | 455 (66) | 5 | 28 (25) |
| 125–175 (5–6.9), as printed | 490 (71) | 455 (66) | 4 | 24 (22) |

Further values from the same sheet:
- E (tension), typical: 76.5 GPa (11.1 msi).
- Density, typical: 2.70 g/cm³ (0.098 lb/in³) {2700 kg/m³}.
- SCC (ASTM G47): max 450 MPa (65.2 ksi) LT and 350 MPa (50.7 ksi) ST.
- Page 1 gives these figures against 7050-T7451: −4 % density, +7 % stiffness, +8 % strength, +6 % toughness, +25 % fatigue resistance, +46 % corrosion resistance. The same sheet says the alloy "can be repeatedly recycled without loss in performance".
- Only L-direction strength minimums are printed. There are no LT or ST strengths and no fatigue S-N data.

Constellium sources:
- The Airware brochure states the same deltas for "Airware® 2050-T84 vs 7050-T7451", "Comparaison for a 75 mm / 3 in plate", and describes it as a "thick plate product (12 – 165" mm. It also says "recycling uses only 5% of the energy needed" (sentence cut off in the extract). [FULL]. Link: [Constellium Airware brochure PDF](https://res.cloudinary.com/constellium/image/upload/v1666252249/PDF%20documents/Product%20and%20data%20sheets/constellium_airware_brochure_finale_dt56xa.pdf)
- The Constellium aerospace-plates web page says "Airware® can achieve up to 20% weight reduction" when combined with optimised design. It gives no per-alloy CO₂ figure. [FETCH]. Link: [Constellium aerospace plates](https://constellium.com/products/aerospace-plates)
- The specification is AMS 4413 (plate 12.70–165.10 mm). [SNIPPET]. Link: [SAE AMS4413A](https://saemobilus.sae.org/standards/ams4413a-aluminum-alloy-plate-35cu-10li-040mg-035mn-045ag-012zr-2050-t84-solution-heat-treated-stress-relieved-artificially-aged)

### Cited Findings: 2099-T83 extrusions
Source for this table: Smiths Metal Centres, "2099 Technical Datasheet", © 2023, single page, "Mechanical Properties" table. [FULL]. The sheet does not say whether the values are typical or minimum. Link: [Smiths Metal 2099 PDF](https://www.smithmetal.com/pdf/lithium/2099-lithium.pdf)

| Thickness | Property | Printed value | My SI conversion of the ksi value |
|---|---|---|---|
| 0.50–0.999" | UTS L | 81 ksi (560 MPa) | 558 MPa |
| 0.50–0.999" | UTS LT | 76 ksi (525 MPa) | 524 MPa |
| 0.50–0.999" | YS L | 76 ksi (525 MPa) | 524 MPa |
| 0.50–0.999" | YS LT | 70 ksi (485 MPa) | 483 MPa |
| 0.50–0.999" | El. L | 9 % | — |
| 1.00–2.5" | UTS L | 83 ksi (595 MPa) | 572 MPa |
| 1.00–2.5" | UTS LT | 75 ksi (520 MPa) | 517 MPa |
| 1.00–2.5" | YS L | 78 ksi (505 MPa) | 538 MPa |
| 1.00–2.5" | YS LT | 68 ksi (470 MPa) | 469 MPa |
| 1.00–2.5" | El. L | 9 % | — |
| — | Tension modulus | 11.3 Msi (78 GPa) | 77.9 GPa |

- **Internal inconsistency:** for 1.00–2.5", 83 ksi is printed as 595 MPa (it converts to 572) and 78 ksi as 505 MPa (it converts to 538). Trust neither column without checking against AMS 4287.
- Other sheet content: extrusions are available from 0.050 to 3.00 inch (1.2–76 mm), and the composition is Cu 2.40–3.00 and Li 1.60–2.00.
- **The sheet gives no density.**
- Smiths HP "Ultimate" 2099 sheet (Rev. 2021), minimums for 20–84 mm: Rm 560 MPa, Rp0.2 520 MPa, A 5 %. [SNIPPET]. My download of the PDF returned HTML, so I could not read it. Link: [SHP 2099 PDF](https://www.smithshp.com/pdf/2099-aluminium-lithium.pdf)
- The specification is AMS 4287 (latest AMS4287C, 2025). [SNIPPET]. Link: [SAE AMS4287A](https://saemobilus.sae.org/standards/ams4287a-aluminum-alloy-extrusion-27cu-18li-07zn-03mn-03mg-008zr-2099-t83-solution-heat-treated-stress-relieved-stretching-1-4-aged)

### Cited Findings: 2195
- The Constellium brochure has two comparison graphics, "Airware® 2195-T84 vs. 2219-T87 (Comparison for 25.4 mm/1.0 in)" and "Airware® 2050-T84 vs. 2219-T87 (Comparison for 50.8 mm/2.0 in)". The extracted text gives percentages (+50 %, equivalent, +5 %, +42 %, −5 %, +20 %) but loses the mapping to properties (tensile yield, toughness, modulus, compressive, density). I cannot attribute them reliably. [FULL text, unresolvable layout]. Link: same brochure as above.
- The brochure says 2195 enabled "weight savings of around 11%, i.e. 3,200 kg" on a launcher tank redesign. [FULL]. Same brochure.
- Constellium offers 2195 in T8 sheet and plate, and in T34 plate that the end user ages to T82; "Mill aged T84 plates are also available upon request". [SNIPPET]. Link: [Constellium aerospace plates](https://constellium.com/products/aerospace-plates)
- Secondary sources conflict:
  - Stanford Advanced Materials: ≈552 MPa UTS, 517 MPa YS, E 71 GPa.
  - MakeItFrom: 590/560 MPa, E 69 GPa, density 3.0 g/cm³.
  - A Chinese supplier: 586/548 MPa, E 76 GPa, 2.72 g/cm³, 8.4 %, temper not stated.
  - All [SNIPPET]. I do not trust any of them. Links: [SAM 2195](https://samaterials.com/aluminium/1774-2195-aluminum-lithium-alloy.html), [MakeItFrom 2195-T8](https://www.makeitfrom.com/material-properties/2195-2195-T8-Aluminum)
- The governing specification is AMS 4474 (2195-T8 sheet and plate, latest AMS4474C). The primary datasheet is "Airware 2195-T84 Plate data sheet, Constellium, May 2017", which an ASM Handbook chapter cites. [SNIPPET]. Link: [ASM Handbook 2195 chapter](https://dl.asminternational.org/handbooks/edited-volume/91/chapter/2087940/2195Al-Li-Plate-Alloy)

### Inferences
- For a bracket, 2050-T84 is the only Al-Li grade here with verified thick-plate minimums. Its ≥455–476 MPa YS (L) at 2700 kg/m³ and 76.5 GPa gives E/ρ ≈ 28.3 MJ/kg. That E/ρ is my calculation, not a sourced value.

### Gaps
- The 2195-T84 numeric table (Constellium May 2017 sheet, not found online).
- 2099 density.
- LT/ST data, fatigue, max service temperature and prices for all three alloys.
- No per-alloy kg CO₂/kg from Constellium or Arconic. The only general statement is "recycling uses only 5% of the energy".

---

## Q3. AlSi10Mg (L-PBF) and Scalmalloy

### Takeaway
The EOS AlSi10Mg sheet I read is a 2017 German FlexLine sheet. It gives as-built values and stress-relieved (270 °C/90 min) values by XY and Z, but **no T6 values** and **no modulus**.

For Scalmalloy, the sheet I read is a 3D Systems sheet. It uses the APWORKS-advised stress relief and adopts some values from the APWORKS datasheet, which itself was not retrievable. It gives about 490–500 MPa Rp0.2 isotropically, but **no modulus**.

### Cited Findings: EOS Aluminium AlSi10Mg
Source: EOS "Materialdatenblatt – FlexLine, EOS Aluminium AlSi10Mg", CR507 v01 / Date 12.2017, EOS M290, parameter set AlSi10Mg_Speed1.2, powder 9011-0024, pages 3–4. This copy is hosted by techpilot.com. [FULL]. Link: [EOS AlSi10Mg MDS (DE), techpilot copy](https://cdn.techpilot.com/public/132713/documents/4b7c1a54-6356-48a4-9cda-7a02f7f11853/alsi10mg_9011-0024_m290_material_data_sheet_12-17_de.pdf)

- Page 1 is inconsistent: it says the alloy is "speziell für die Verarbeitung auf EOS M 400 Systemen optimiert" (optimised for M 400 systems), but the system listed is the M290.
- Density: "Dichte 2,67 g/cm3" {2670 kg/m³}, measured to ISO 3369.
- Tensile testing to EN ISO 6892-1:2009 B10. The values are means of horizontal and vertical specimens.

| Condition | Direction | Rm, MPa | Rp0.2, MPa | A, % |
|---|---|---|---|---|
| As built | Horizontal (XY) | 460 ± 20 (67 ± 3 ksi) | 270 ± 10 (39 ± 2 ksi) | 10 ± 2 |
| As built | Vertical (Z) | 470 ± 20 (68 ± 3 ksi) | 235 ± 10 (34 ± 2 ksi) | 6 ± 2 |
| Stress relieved 270 °C / 90 min | Horizontal (XY) | 340 (49 ksi) | 220 (32 ksi) | 12 |
| Stress relieved 270 °C / 90 min | Vertical (Z) | 350 (51 ksi) | 225 (33 ksi) | 9 |

Other AlSi10Mg sources:
- The current EOS English sheet exists (Premium/Core TRL labelling), but my download returned HTML and I did not read its numbers. Link: [EOS AlSi10Mg MDS EN](https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Aluminium_AlSi10Mg/Material_Datasheet_EOS_Aluminium_AlSi10Mg_EN.pdf)
- An EOS process data sheet states that EOS T6 heat treatment "does not typically have a significant effect on fatigue strength". [SNIPPET]. Link: [EOS PDS AlSi10Mg M400-4 30 µm](https://www.eos.info/metal-solutions/data-sheets/aluminium/pds-eos-aluminium-alsi10mg-eos-m-400-4-30um)

### Cited Findings: Scalmalloy (3D Systems certified, APWORKS material)
Source: 3D Systems "Certified Scalmalloy® (A)" datasheet, PN 10123B 02-22, 2 pages. [FULL]. Link: [3D Systems Scalmalloy PDF](https://3dsystems.com/sites/default/files/2022-02/3d-systems-certified-scalmalloy(a)-datasheet-usen-2022-02-23-a-print.pdf)

- Condition "SR" is 325 °C for 4 h with air cooling ("heat treatment advised by APWORKS").
- Testing is to ASTM E8 with round type-4 specimens, on DMP Flex/Factory 350.
- Values are "based on average and 95% tolerance interval with 95% confidence".

| Layer thickness | Direction | UTS, MPa (ksi) | Rp0.2, MPa (ksi) | Plastic elongation, % |
|---|---|---|---|---|
| 30 µm | XY | 520 ± 10 (75 ± 2) | 490 ± 10 (71 ± 2) | 15.8 ± 2.7 |
| 30 µm | Z | 520 ± 15 (75 ± 2) | 490 ± 15 (71 ± 2) | 15.8 ± 2.6 |
| 60 µm | XY | 530 ± 10 (77 ± 2) | 500 ± 10 (72 ± 2) | 14.0 ± 3.4 |
| 60 µm | Z | 520 ± 10 (75 ± 2) | 490 ± 10 (71 ± 2) | 13.1 ± 3.0 |

Further values from the same sheet:
- Theoretical density 2.67 g/cm³ (0.096 lb/in³) {2670 kg/m³}. The sheet labels this "Value from literature" and, by footnote 8, adopted from the APWORKS datasheet.
- Relative density 99.6–99.8 %.
- The sheet gives no elastic modulus, fatigue or service temperature.
- The APWORKS datasheet itself did not appear in search, and the [APWORKS materials page](https://apworks.de/materials) gives no numbers. [SNIPPET]

### Inferences
- Scalmalloy's Rp0.2 (~490 MPa) is about twice that of stress-relieved AlSi10Mg (~220 MPa) at the same printed density, 2.67 g/cm³, and it shows almost no XY/Z anisotropy. Note that the AlSi10Mg sheet is EOS M290 data and the Scalmalloy sheet is 3D Systems DMP data, so this is a cross-machine comparison.

### Gaps
- AlSi10Mg in T6 (EOS current EN sheet not read).
- E for both alloys.
- Fatigue (R, N) for both.
- APWORKS EPD/CO₂ and powder price: not found, and I did not search environdec.com within the budget.

---

## Q4. Ti-6Al-4V ELI by L-PBF (EOS), EBM (Colibrium/Arcam) and as-HIPed

### Takeaway
- **EOS L-PBF Ti64ELI, 800 °C/2 h:** ≈945–965 MPa Rp0.2 and 1055–1075 MPa Rm on the M290. That is above the EBM as-built values.
- **Colibrium EBM Spectra L Grade 23, as built:** ≈907–940 MPa YS and 986–1015 MPa UTS, with "--" in the modulus column.
- **As-HIPed:** no source found.

### Cited Findings: EOS Titanium Ti64ELI, L-PBF
Source: EOS combined PDF (M290 sheet 06.2022, pages 1–5, then FlexLine M400 sheet SPU CR390 / 07.22, pages 1–4). [FULL]. Link: [EOS Ti64ELI MDS M290/M400](https://EOS.info/05-datasheet-images/Assets_MDS_Metal/EOS_Titanium_Ti64ELI/Material_DataSheet_EOS_Titanium_Ti64Eli_EOSM290_EOSM400_en.pdf)

M290 (EOSINT M 290 400 W, 30 µm, Ti64ELI_Performance_M291 1.10):
- Composition corresponds to ASTM F136 and F3001.
- Part density "Approx. 4.41 g/cm3" {4410 kg/m³}.
- Heat treatment: 800 °C for 2 h in argon. Tensile testing to ISO 6892-1 A14.

| Direction | Rm | Rp0.2 | A | Z |
|---|---|---|---|---|
| Horizontal | 1055 MPa | 945 MPa | 13 % | > 25 % |
| Vertical | 1075 MPa | 965 MPa | 14 % | > 25 % |

M400 SF (Ti64ELI_030_FlexM400_100, 30 µm):
- Part density 4.4 g/cm³.
- Values are averages of horizontal and vertical specimens.

| Condition | Rm | Rp0.2 | A |
|---|---|---|---|
| As built | typ. 1270 MPa | typ. 1100 MPa | typ. 8.7 % |
| Heat treated, 2 h at 800 °C in Ar | typ. 1040 MPa | typ. 930 MPa | typ. 14.0 % |

- Neither EOS sheet gives an E or fatigue value.

### Cited Findings: Colibrium Additive (ex-Arcam) EBM Ti6Al4V Grade 23 (ELI), Spectra L v1.2
Source: "SpectraLv1.2_Ti6Al4V-Gr23_CMDS_20240709_RevB", 7 pages. Condition is as built, with tensile testing to ASTM E8. H means horizontal (X or Y) and V means vertical (Z). [FULL]. Link: [Colibrium Spectra L Ti64 Gr23 PDF](https://www.colibriumadditive.com/sites/default/files/SpectraLv1.2_Ti6Al4V-Gr23_CMDS_20240709_RevB.pdf)

| Process theme | Direction | 0.2 % YS, MPa | UTS, MPa | Elongation, % | Area reduction, % |
|---|---|---|---|---|---|
| 6.4.0 Line Melt, 70 µm | H | 907 | 986 | 13.77 | 33.56 |
| 6.4.0 Line Melt, 70 µm | V | 918 | 996 | 16.28 | 42.4 |
| 6.4.1 Point Melt, 50 µm | H | 940 | 1015 | 12.5 | 33 |
| 6.4.1 Point Melt, 50 µm | V | 935 | 1005 | 13.5 | 42 |

- **Line Melt elongation and area reduction:** the layout extraction scrambled these columns. 13.77 % H, 16.28 % V and RA 33.56/42.4 % is my most likely reading.
- Archimedes density is 99.5 % (Line Melt) and 99.7 % (Point Melt). These are relative values; the sheet gives no absolute g/cm³.
- The modulus column is printed as "--".
- The sheet states: "All parameters of this configuration dramatically exceed the requirements of ASTM F3001."

### Cited Findings: as-HIPed
- No producer HIP datasheet was opened. The GE Additive Q10plus Ti64 (Grade 5) sheet failed to download (HTML), so it is not used. Link: [GE Ti64 Q10 70 µm](https://www.ge.com/additive/sites/default/files/2023-03/TI64%20Q10%2070um%20V2.1.pdf)

### Inferences
- EBM as-built strength is close to EOS L-PBF after its 800 °C heat treatment, about 90–95 % of it. EBM shows little H/V anisotropy in strength but more in RA.

### Gaps
- E (not stated by EOS or Colibrium).
- Fatigue (R, N).
- HIP condition data (to close: NASA MSFC-SPEC-3717 data, NIST AM-Bench, or the EOS/GE HIP process data sheets).
- Price and EPD.

---

## Q5. 17-4PH H1025

### Takeaway
I found no mill bulletin (AK Steel/Cleveland-Cliffs or Carpenter) that I could open. The H1025 row comes from a distributor copy of the AMS 5643 bar table [FETCH]. It matches AMS 5643 minimums as I remember them, so the source's "typical" label may be wrong.

### Cited Findings
- AMS 5643 bar, H1025, printed as "155 145 12 45 331-401". That is UTS 155 ksi {1069 MPa}, 0.2 % YS 145 ksi {1000 MPa}, elongation in 2D 12 %, RA 45 %, and hardness 331–401 (an HB-range value under a column labelled Rockwell C). The table is headed "Typical Mechanical Properties". [FETCH]. Link: [Aircraft Materials AMS 5643](https://aircraftmaterials.com/data/alstst/alstst/ams5643.html)
- Density 7.78 g/cc (0.281 lb/in³) {7780 kg/m³}. Source: a MatWeb print of "AK Steel 17-4 PH, Condition A", "Information provided by AK Steel". [FULL]. Link: [Quickparts copy of the MatWeb/AK Steel sheet](https://quickparts.com/wp-content/uploads/2024/05/Stainless-Steel-17-4-PH.pdf)
- United Performance Metals datasheet:
  - Density 0.2820 lb/in³ {7806 kg/m³}.
  - Service environments "up to 600°F (316°C)".
  - It also prints generic values of UTS 160 ksi (1103 MPa), YS 145 ksi (1000 MPa), elongation 5.0 % and HRC 35, without stating the condition. These are **not** H1025.
  - [FULL]. Link: [Upmet 17-4 PH PDF](https://www.upmet.com/sites/default/files/datasheets/17-4-ph.pdf)
- Bibus metric H1025 minimums: Rp0.2 1000 MPa, Rm 1070 MPa, A 11 %. [SNIPPET]. Link: [Bibus 17-4PH](https://sd-metals.bibus.com/de-en/materials/itm/17-4PH-1-4548/)

### Gaps
- E: UNVERIFIED (memory) ≈ 197 GPa.
- Fatigue data, a mill-bulletin H1025 table, and price.

---

## Q6. Inconel 718, AM (EOS L-PBF), aged

### Takeaway
On the EOS M290 at 40 µm, after AMS 2774/AMS 5662 solution plus double ageing, IN718 reaches Rp0.2 1145 MPa (V) / 1240 MPa (H) and Rm 1375 / 1505 MPa. EOS rates the alloy as strong up to 700 °C.

### Cited Findings
Source: EOS "EOS NickelAlloy IN718 Material Data Sheet", Premium, V1.0, CR696, 2020-02, multi-page PDF. [FULL]. Link: [EOS IN718 MDS](https://eos.info/05-datasheet-images/Assets_MDS_Metal/EOS_NickelAlloy_IN718/Material_DataSheet_EOS_NickelAlloy_IN718_en.pdf)

- Heat treatment, "conform to AMS 2774 and AMS 5662":
  - Solution anneal at 954 °C for 1 h per 25 mm, air or argon cool.
  - Age at 718 °C for 8 h, furnace cool to 621 °C, hold at 621 °C for a total precipitation time of 18 h, air or argon cool.
- Density: "Average density … min 8.15 g/cm3" {≥ 8150 kg/m³}.

| Parameter set | Condition | Direction | Rp0.2, MPa | Rm, MPa | A, % | Samples (n) |
|---|---|---|---|---|---|---|
| M290 40 µm (IN718 Performance 2.0) | Heat treated | Vertical | 1145 | 1375 | 17 | 54 |
| M290 40 µm (IN718 Performance 2.0) | Heat treated | Horizontal | 1240 | 1505 | 12 | 26 |
| M290 40 µm (IN718 Performance 2.0) | As manufactured | Vertical | 650 | 970 | 32 | 41 |
| M290 40 µm (IN718 Performance 2.0) | As manufactured | Horizontal | 800 | 1090 | 25 | 36 |
| M290 40 µm HiPro | Heat treated | Vertical | 1180 | 1420 | 13 | — |
| M290 40 µm HiPro | Heat treated | Horizontal | 1270 | 1530 | 14 | — |
| M290 80 µm HiPro | Heat treated | Vertical | 1200 | 1440 | 15 | — |
| M290 80 µm HiPro | Heat treated | Horizontal | 1240 | 1500 | 14 | — |

- Page 1 statement: "good tensile, fatigue, creep and rupture strength at temperatures up to 700 °C (1290 °F)". It gives no fatigue numbers.
- The PDF also contains M400-4 sections with elevated-temperature tensile and Larson-Miller creep data, which I have not tabulated here.

### Gaps
- E: UNVERIFIED (memory) ≈ 200 GPa.
- Fatigue (R, N).
- Price.

---

## Q7. Mg WE43 / Elektron 43 (Luxfer MEL)

### Takeaway
The Luxfer datasheet PDFs could not be retrieved. Plain downloads and WebFetch both redirected to the Luxfer homepage, and a retry that sent a referrer header was blocked as bot-check circumvention, so I stopped. Only snippet-level facts exist.

### Cited Findings
- Elektron 43 is "a lightweight, high-strength wrought magnesium alloy for use at temperatures up to 250˚C". It is available as rolled plate (AMS 4371), forging feedstock and extrusions, with "Specific gravity: 1.83" {≈1830 kg/m³}. Extrusions reach maximum strength in T5. [SNIPPET]. Links: [Luxfer Elektron 43 datasheet PDF](https://www.luxfermeltechnologies.com/wp-content/uploads/2024/11/Elektron®-43-Datasheet.pdf), [Luxfer Elektron 43 extruded](https://www.luxfermeltechnologies.com/?p=3198)
- The Elektron WE43B casting alloy is rated for use up to 300 °C and is described as "maintaining its mechanical properties at elevated temperatures, without the use of either silver or thorium". [SNIPPET]. Link: [Luxfer WE43B datasheet PDF](https://www.luxfermeltechnologies.com/wp-content/uploads/2024/11/Elektron-WE43B-Datasheet.pdf)
- Elektron 43 has undergone FAA flammability testing. [SNIPPET]. Same Luxfer link.

### Gaps
- All mechanical values (E, Rp0.2, UTS, A, fatigue) for WE43B-T6 and Elektron 43-T5. To close: download the Luxfer PDFs manually in a browser, or use the ASM Alloy Digest Mg-76.

---

## Q8. Carbon-fibre thermoplastic laminates (Victrex AE 250 / LMPAEK, Toray Cetex TC1225) and quasi-isotropic IM7/8552

### Takeaway
- **Victrex LMPAEK UDT AS4 TDS [FULL]:** gives UD and open-hole properties. 0° tension is 2320 MPa / 130 GPa; OHT is 391 MPa and OHC is 314 MPa; laminate density is 1.576 g/cm³.
- **Hexcel 8552 [FULL]:** gives an IM7 quasi-isotropic (25/50/25) unnotched tensile strength of 104 ksi {717 MPa}, but **no QI modulus**.
- **TC1225:** NCAMP reports are behind Incapsula bot protection, so only snippets are available.

### Cited Findings: Victrex
Source: Victrex "VICTREX LMPAEK™ UDT AS4-143-34" TDS, Revision January 2025, pages 1–2. All conditions RTA unless stated. [FULL]. Link: [Victrex LMPAEK UDT AS4-143-34 TDS](https://cdn.victrex.com/-/media/downloads/datasheets/tds_victrex-lmpaek-udt-as4-143-34.pdf)

The sheet states the product is NCAMP-approved.

Physical and polymer properties:
- Fibre: Hexcel HexTow AS4 12K. FAW 143 gsm, RC 34 %, CPT 0.137 mm, fibre volume 58.10 %.
- Laminate density 1.576 g/cm³ {1576 kg/m³}.
- Base polymer: Tm 305 °C, Tg onset 149 °C (300 °F), density 1.30 g/cm³.

| Property | Test method | Value as printed |
|---|---|---|
| 0° tensile strength | ASTM D3039 | 2320 MPa (336.4 ksi) |
| 0° tensile modulus | ASTM D3039 | 130 GPa (18.9 Msi) |
| 0° compression strength | ASTM D6641 | 1420 MPa |
| 0° compression modulus | ASTM D6641 | 120 GPa |
| 90° compression strength | ASTM D6641 | 192 MPa |
| 90° compression modulus | ASTM D6641 | 9.6 GPa |
| In-plane shear strength | EN 6031 | 145 MPa |
| In-plane shear modulus | EN 6031 | 4.5 GPa |
| OHC, RTA | ASTM D6484 | 314 MPa (45.5 ksi) |
| OHC, ETW (121 °C after 71 °C/85 % RH) | ASTM D6484 | 243 MPa |
| OHT | ASTM D5766 | 391 MPa (56.7 ksi) |
| 0° flexural strength | ASTM D790 | 1360 MPa |
| CAI at 6.67 J/mm | ASTM D7137 | 289 MPa (42 ksi) |

- The layup of the OHT/OHC/CAI coupons is not stated on the TDS.

Victrex AE 250 technical paper (CAMX 2018), Table 1, "Typical mechanical properties of VICTREX AE™ 250 PAEK polymer", neat resin at 23 °C. [FULL]. Link: [Victrex AE 250 CAMX 2018 paper](https://www.victrex.com/-/media/downloads/whitepapers/victrex-ae-250---technical-paper-camx-2018_2.pdf)
- Tensile yield strength 90 MPa, tensile elongation at break 15 %, tensile modulus 3.5 GPa (ISO 527); flexural strength 150 MPa, flexural modulus 3.3 GPa (ISO 178).
- Quasi-isotropic [+45/0/−45/90]3S results (CAI, FHT, OHC, plain tension) are reported only as oven-consolidated vs press-consolidated percentages, for example "CAI 103%" and "OHC 102%", with no absolute values. [FULL]

Mapping between the two Victrex documents:
- I assume AE 250 is the Victrex LMPAEK-based composite family. I did not verify this in either document, so it is UNVERIFIED (memory). Treat the TDS numbers as "Victrex LMPAEK UDT AS4", not strictly "AE 250".
- NCAMP has qualified AE 250 with AS4 12K UD, report CAM-RP-2021-025 (352 pp.). I could not open it. [SNIPPET]. Link: [NIAR AE250 MPDR](https://wichita.edu/industry_and_defense/NIAR/Documents/CAM-RP-2021-025-NC-Victrex-AE250-AS4-12k-Uni-MPDR-Rev-NC-11.18.22.pdf)

### Cited Findings: Toray Cetex TC1225 (LM-PAEK)
- NCAMP specification NMS 122/1 (T700 unitape, 145 gsm) [SNIPPET]:
  - Laminate density (ASTM D792) 1.56–1.60 g/cc avg {1560–1600 kg/m³}.
  - Cured ply thickness 0.0050–0.0060 in {0.127–0.152 mm}.
  - 0° tension ([0]8) requirement ≥ 245 ksi {≥ 1689 MPa}.
  - My download was blocked by Incapsula and I did not try to bypass it. Link: [NIAR NMS 122/1](https://wichita.edu/industry_and_defense/NIAR/Documents/NMS-122-Slash-1-Rev-February-21-2020-T700-Unitape.pdf)
- TC1225 T1100GC: Tg 147 °C. [SNIPPET]. Link: [Total Materia TC1225 T1100GC](https://www.totalmateria.com/en-us/material/5178556)
- The full data is in NCAMP MPDR CAM-RP-2025-016 Rev A (2026-02-24, T700GC UD), which I could not retrieve. Link: [NIAR TC1225 T700GC MPDR](https://www.wichita.edu/industry_and_defense/NIAR/Documents/Toray-TC1225-LM-PAEK-T700GC-UNI-Qualification-CAM-RP-2025-016-RevA-2.24.2026-MPDR-Final.pdf)

### Cited Findings: Hexcel HexPly 8552 / IM7
Source: Hexcel "HexPly® 8552 Product Data Sheet" (US), © 2020, pages 1 and 4. [FULL]. Link: [Hexcel 8552 US datasheet](https://hexcel.com/wp-content/uploads/2026/01/HexPly_8552_us_DataSheet.pdf)
- Service temperature: "Service Temperature up to 250°F" {121 °C}.
- In the mechanical-properties table, each row lists values for AS4 first and IM7 second.

| Property (77 °F, dry) | AS4 | IM7 | IM7 in SI |
|---|---|---|---|
| QI 25/50/25 tensile strength, ksi | 107 | 104 | 717 MPa |
| QI OHT, ksi | 63.5 | 62.1 | 428 MPa |
| QI OHC, ksi | 47.8 | 48.9 | 337 MPa |
| QI CAI, ksi | 34.6 | 31 | 214 MPa |
| UD 0° tensile strength, ksi | 310 | 395 | 2723 MPa |
| UD 0° tensile modulus, msi | 19.6 | 23.8 | 164.1 GPa |
| UD 0° tensile elongation, % | 1.55 | 1.62 | — |
| UD 90° tensile strength, ksi | 9.27 | 9.3 | 64.1 MPa |
| UD 90° tensile modulus, msi | 1.39 | 1.70 | 11.7 GPa |
| UD 0° compression strength, ksi | 222 | 245 | 1689 MPa |
| UD 0° compression modulus, msi | 18.6 | 21.7 | 149.6 GPa |

- **The sheet gives no QI laminate modulus.**

Hexcel HexTow IM7 fibre datasheet [FULL]. Link: [Hexcel IM7 datasheet](https://hexcel.com/wp-content/uploads/2025/12/IM7_HexTow_DataSheet.pdf)
- Fibre: density 1.78 g/cm³ and tensile modulus 40.0 Msi (276 GPa).
- "Typical HexPly 8552 Composite Properties" at 60 % fibre volume: 0° tensile 395 ksi (2,723 MPa), 0° modulus 23.8 Msi (164 GPa), OHT 62.1 ksi (428 MPa), OHC 48.9 ksi (337 MPa).

### Inferences
- A QI E for IM7/8552 is not given by any source I read. It would have to be computed with CLT from the ply properties already in `library.py`, and labelled as a calculation.
- On the Victrex sheet, OHT (391 MPa) and OHC (314 MPa) are about 9 % and 7 % below the IM7/8552 QI values (428/337 MPa). The layups may differ, so this is indicative only.

### Gaps
- TC1225 laminate numbers, AE 250 absolute QI values, and a QI modulus for any system.
- Max service temperature for the thermoplastics beyond Tg (149 °C for LMPAEK, 147 °C for TC1225 T1100GC).
- Toray or Victrex EPDs/CO₂ and prices: not found or not searched.

---

## Final summary table (SI)

Notation: tags are as defined at the top. "—" means the source does not state the value. XY = horizontal and Z = vertical (build direction). For Al-Li, L = longitudinal.

| Material / condition | ρ, kg/m³ | E, GPa | Rp0.2, MPa | UTS, MPa | A, % | Max service T | Source (tag) |
|---|---|---|---|---|---|---|---|
| 7050-T7451 plate | 2830 [SNIPPET] | 70.3–71.7 [SNIPPET] | 441 (AMS 4050 min, 6.3–51 mm, reading uncertain) / 469 typ (conflicting) [SNIPPET] | 510 min / 524 typ [SNIPPET] | 9 min / 11 typ [SNIPPET] | — | referansmetal, scribd/MatWeb (SNIPPET) |
| Airware 2050-T84 plate, L min, 12.7–38.1 mm | 2700 typ [FULL] | 76.5 typ [FULL] | 476 [FULL] | 503 [FULL] | 8 [FULL] | — | Smiths HP 2050 sheet p.2 |
| Airware 2050-T84 plate, L min, 125–175 mm | 2700 typ [FULL] | 76.5 [FULL] | 455 [FULL] | 490 [FULL] | 4 [FULL] | — | Smiths HP 2050 sheet p.2 |
| 2099-T83 extr., 0.50–0.999", L (typical/min not stated) | — | 78 (11.3 Msi) [FULL] | 524 (76 ksi) [FULL] | 558 (81 ksi) [FULL] | 9 [FULL] | — | Smiths Metal 2099 sheet |
| 2195-T8/T84 | conflicting 2700–3000 [SNIPPET] | 69–76 [SNIPPET] | 517–560 [SNIPPET] | 552–590 [SNIPPET] | — | — | SAM / MakeItFrom (SNIPPET, not reliable) |
| AlSi10Mg L-PBF, as built, XY / Z | 2670 [FULL] | — | 270 / 235 [FULL] | 460 / 470 [FULL] | 10 / 6 [FULL] | — | EOS MDS DE 12.2017 p.4 |
| AlSi10Mg L-PBF, SR 270 °C/90 min, XY / Z (not T6) | 2670 [FULL] | — | 220 / 225 [FULL] | 340 / 350 [FULL] | 12 / 9 [FULL] | — | EOS MDS DE 12.2017 p.4 |
| Scalmalloy L-PBF, SR 325 °C/4 h, 30 µm, XY / Z | 2670 (theoretical, from APWORKS) [FULL] | — | 490 / 490 [FULL] | 520 / 520 [FULL] | 15.8 / 15.8 [FULL] | — | 3D Systems PN 10123B |
| Scalmalloy L-PBF, SR, 60 µm, XY / Z | 2670 [FULL] | — | 500 / 490 [FULL] | 530 / 520 [FULL] | 14.0 / 13.1 [FULL] | — | 3D Systems PN 10123B |
| Ti64ELI L-PBF EOS M290, 800 °C/2 h, H / V | ≈4410 [FULL] | — | 945 / 965 [FULL] | 1055 / 1075 [FULL] | 13 / 14 [FULL] | — | EOS Ti64ELI MDS 06.2022 p.4 |
| Ti64ELI L-PBF EOS M400, as built (H+V mean) | 4400 [FULL] | — | 1100 [FULL] | 1270 [FULL] | 8.7 [FULL] | — | EOS FlexLine M400 07.22 |
| Ti64ELI L-PBF EOS M400, 800 °C/2 h (H+V mean) | 4400 [FULL] | — | 930 [FULL] | 1040 [FULL] | 14.0 [FULL] | — | EOS FlexLine M400 07.22 |
| Ti64 Gr23 EBM Spectra L, Point Melt 50 µm, as built, H / V | — (99.7 % relative) [FULL] | "--" [FULL] | 940 / 935 [FULL] | 1015 / 1005 [FULL] | 12.5 / 13.5 [FULL] | — | Colibrium CMDS 20240709 RevB |
| Ti64 Gr23 EBM Spectra L, Line Melt 70 µm, as built, H / V | — (99.5 %) [FULL] | "--" [FULL] | 907 / 918 [FULL] | 986 / 996 [FULL] | 13.77 / 16.28 (layout uncertain) [FULL] | — | Colibrium CMDS 20240709 RevB |
| Ti64 ELI as-HIPed | — | — | — | — | — | — | GAP |
| 17-4PH H1025 bar (AMS 5643) | 7780 (AK Steel, Cond. A) [FULL] | — (≈197 UNVERIFIED (memory)) | 1000 (145 ksi) [FETCH] | 1069 (155 ksi) [FETCH] | 12 [FETCH] | 316 °C (600 °F) [FULL, Upmet] | aircraftmaterials AMS 5643; Quickparts/MatWeb AK Steel; Upmet |
| IN718 L-PBF EOS M290 40 µm, AMS 5662 aged, V / H | ≥8150 [FULL] | — (≈200 UNVERIFIED (memory)) | 1145 / 1240 [FULL] | 1375 / 1505 [FULL] | 17 / 12 [FULL] | "up to 700 °C" [FULL] | EOS IN718 MDS V1.0 2020-02 |
| Elektron 43 (WE43 wrought) | 1830 (SG 1.83) [SNIPPET] | — | — | — | — | 250 °C [SNIPPET] | Luxfer MEL (SNIPPET) |
| Elektron WE43B cast | — | — | — | — | — | 300 °C [SNIPPET] | Luxfer MEL (SNIPPET) |
| Victrex LMPAEK UDT AS4, UD 0° | 1576 [FULL] | 130 (0° tension) [FULL] | n/a | 2320 (0° tension); OHT 391; OHC 314 [FULL] | — | Tg onset 149 °C [FULL] | Victrex TDS Jan 2025 |
| Toray Cetex TC1225 T700 UD | 1560–1600 (spec) [SNIPPET] | — | n/a | ≥1689 0° (spec requirement) [SNIPPET] | — | Tg 147 °C (T1100GC) [SNIPPET] | NIAR NMS 122/1; Total Materia |
| IM7/8552, QI 25/50/25, 77 °F dry | — (fibre 1780, Vf 60 %) [FULL] | **not given** | n/a | 717 unnotched; OHT 428; OHC 337; CAI 214 [FULL] | — | 121 °C (250 °F) [FULL] | Hexcel 8552 US PDS p.4; IM7 PDS |

**Eco and price column (all materials):** the only alloy-level eco statement I found:
- Recycling Airware "uses only 5% of the energy needed" (brochure, [FULL]; sentence cut off in the extract).
- Constellium's "11.4 lb CO₂ avoided per lb recycled" (2012) is an avoided-emissions claim, not a product footprint. [SNIPPET]. Link: [AlCircle Constellium recycling](https://www.alcircle.com/news/aluminum-supplier-constellium-advances-science-of-recycling-10869)

No per-alloy kg CO₂/kg EPD (Constellium, Arconic, Hydro CIRCAL, APWorks, Toray, Victrex) and no credible price indication was found or read. Both are open gaps (G-14-type): environdec.com was not searched within the tool budget.
