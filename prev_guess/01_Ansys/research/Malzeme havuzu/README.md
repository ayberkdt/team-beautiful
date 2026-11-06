# Material pool (materials_pool.json)

Built on 2026-11-03 for EUROAVIA Ideathon 2026 (Ansys challenge). The pool holds 31 materials and 264 property entries. Each entry has a value, a unit, a source and a tag. The tag count is 185 D, 35 S and 44 Y. The JSON parses with `json.load`; a check script also confirmed the units, tags and sources and found 0 problems.

## How the values were obtained

1. **Reused first, with tags inherited.** These project files were reused: `Üç sapma alanı/A_*.md`, `B_*.md` and `C_*.md`, `Hafifletme derin araştırma 2/alloy_datasheets.md` and `cost_data.md`, `prev_guess/01_Ansys/tradeoff/build_studies.py`, and `src/aerokit/materials/eco.py` and `library.py`.
   - Numbers from these files keep the tag their note gave them. Each source string names the note.
   - These values were read in the 2026-11-01/02 sessions, partly by sub-agents. They were not re-read on 2026-11-03.
2. **MIL-HDBK-5J (31 Jan 2003), local PDF** `references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf`.
   - **Design allowables:** read from the project's automatic table extraction in `src/aerokit/materials/data/*.md`. This covers 2024, 6061, 7050, 7075, Ti-6Al-4V, 17-4PH, 15-5PH, 300M and Inconel 718.
   - **Read directly from the PDF text on 2026-11-03:** the 2618, AZ31B and fatigue sections.
   - **Read from page images:** the physical-property figures (k, CTE) for 15-5PH, AZ31B and 4340, and the S-N figures for Ti-6Al-4V, 718, 7050 and 300M.
   - **Strength basis:** the A-basis column for the first thickness range, L direction, unless the entry's `condition` says otherwise. These are allowables, not typical values.
3. **Fatigue at 10^7.** The value comes from solving MIL-HDBK-5J's best-fit equations at N = 10^7, mostly at R = −1. These rows are tagged Y because the equation is D but the solving is mine. Where a page image was available I checked the result against the plotted curve (7050, 718, 300M).
   - Exception: for Ti-6Al-4V the curve ends at about 4×10^6 cycles, so the pool gives the reading at the curve end (331 MPa), tagged D. Extrapolating the equation to 10^7 would give 283 MPa.
4. **Primary sources downloaded on 2026-11-03.** All are tagged D and were read with pdftotext:
   - EOS IN625 data sheets (M290 06.2022 sheet and the multi-system sheet)
   - Victrex PEEK 450G TDS (Nov 2019)
   - Stratasys ULTEM 9085 data sheet (reseller-hosted copy)
   - Stratasys FDM Nylon 12CF rev 0925a
   - EOS PA 2200: the web data sheet (last changed 20.10.2026) and the 2004 product information sheet
   - Eckart A205 sheet (Sept 2020)
   - Aubert & Duval Ti5553 sheet
   - ICE v2.0 summary tables
5. **CO2.**
   - Wrought Al: ICE v2.0, 12.79 primary and 1.81 recycled kg CO2e/kg. The `low`/`high` keys carry the range 6.6–15.1 (European Aluminium, IAI).
   - Mg: IMA/DLR, 25.8 primary and 1.1 recycled.
   - Ti, stainless and Ni: Ashby 2013 family values through the compilation in eco.py, tagged S.
   - CFRP and CF/PEEK: rule-of-mixtures estimates from build_studies.py, tagged Y.
   - Steel 300M and PA12: generic ICE proxies (steel bar & rod, nylon 6), tagged Y.
6. **Prices.** Only the values in cost_data.md were used: Al plate, Ti plate, and powders for AlSi10Mg, Scalmalloy, Ti64, 17-4PH and In718. No new price research was done. Currency and year are in the `unit`.

## Conflicts found

1. **Typical vs allowable.** library.py and the B notes hold AA typical values:
   - 7075-T6: 503/572 MPa typical vs MIL A-basis 483/538.
   - 6061-T6: 276/310 typical vs MIL A-basis 248/290.
   - 2024-T351: AA typical Fty 324 MPa is below MIL A-basis 331 MPa (already flagged in the library.py docstring).
2. **7050-T7451.** Distributor "typical" snippets (469/524 and 480–520/540–590) disagree with each other. MIL A-basis (441/510/10 %) confirms the AMS 4050 snippet reading 441/510/9.
3. **Ti-6Al-4V fatigue.** Wrought annealed bar (MIL, R = −1) is about 330 MPa at about 4×10^6, with run-outs at about 410 MPa. AM milled + HIP (Greitemeier via Afroz) is 600 MPa. The specimens, surfaces and sources differ, so do not read this as "AM beats wrought".
4. **Inconel 718 E.** MIL gives 202.7 GPa (29.4 Msi); SMC-045 gives 200 GPa. EOS gives no E for AM 718, so the AM entry uses 200 [Y].
5. **Inconel 718 fatigue.** The MIL R = −1 sheet curve gives only about 298 MPa at 10^7 (belt-polished thin sheet). Treat it as sheet-specific.
6. **Al primary CO2.** The values spread by a factor of about 2: EU-made 6.6, Ashby 12, ICE 12.79, IAI global 15.1.
7. **Mg primary CO2.** IMA gives 25.8 (Pidgeon) or 17.8 (electrolytic); Ashby gives 36.
8. **Carbon fibre CO2.** JCMA 19.85, Ashby 33, Meng 68 (coal grid), ecoinvent 81.6. The CFRP value of 23.4 uses 33 as its centre.
9. **Tagging of Ashby CO2.** build_studies.py tags the Ashby-via-compilation Al value D; the B notes tag the same kind of value S. The pool uses S.
10. **PA 2200.** The EOS 2004 sheet (1700 MPa, 45 MPa, 20 %) differs from the current EOS web sheet (1650 MPa, 48 MPa, 18 %). The pool uses the current sheet for mechanical properties and the 2004 sheet for k, CTE and Tmax.
11. **ULTEM 9085 modulus.**
    - Stratasys gives 2.51 (XZ) / 2.41 (ZX) GPa.
    - Distributor sheets give 2.15–2.27 GPa.
    - SABIC moulded resin gives 2.85 GPa (ISO 527).
    - Printed yield (70 MPa) is above printed break (68 MPa) in XZ; that is as printed.
12. **Ti5553.** The Aubert & Duval sheet text prints "Vanadium 2.00" where 5 is nominal. The composition is not used.
13. **2198 vs 2050.** E is 76.5 GPa on both Smiths sheets, so it may be copied. Smiths lists Elektron 43 as a casting, while Luxfer describes it as wrought.
14. **15-5PH CTE.** The MIL figure interpolation gives about 11.0 ×10⁻⁶/K. Rolled Alloys prints 6.3 µin/in·°F (11.3 ×10⁻⁶/K) with no condition stated.
15. **300M CTE.** The 4340 proxy from the MIL figure gives 12.2 ×10⁻⁶/K. Secondary 300M pages give 11.3–11.5.
16. **Nylon 12CF CTE.** The PDF text layout does not show which value (115.7 or 37.31 µm/m·°C) belongs to which orientation, so CTE is omitted.

## Weak values (use with care)

- **WE43B / Elektron 43:** all values come from search snippets of Luxfer PDFs. The PDFs redirect to the homepage, and no workaround was tried.
- **A20X:** values are the typical ranges printed by the powder supplier, not allowables.
- **Proxies:**
  - Scalmalloy CO2 and price (Y)
  - AM Ti64 k and CTE (wrought values)
  - 2024-T351 fatigue (2024-T4 bar)
  - AZ31B fatigue (F-temper forged disk, not H24 sheet)
  - Polymer CO2 proxies

## NOT FOUND (property keys omitted)

- Al-Li 2050-T84: fatigue, k, CTE, Tmax. Its price is the conventional-Al placeholder [Y].
- Al-Li 2198-T8: elongation, fatigue, k, CTE, Tmax, price.
- 6061-T6 and 7050-T7451: Tmax.
- 7075-T73/T7351: fatigue, Tmax.
- 2618-T61: fatigue.
- AlSi10Mg: Tmax, recycled CO2.
- Scalmalloy: k, CTE, Tmax, recycled CO2.
- A20X/A205: fatigue (number), k, CTE, recycled CO2, price.
- Ti-6Al-4V wrought: Tmax. Ti-6Al-4V AM: recycled CO2.
- Ti-5553: E, fatigue, k, CTE, Tmax, price.
- 17-4PH H1025: fatigue. MIL has only an H900 curve.
- 15-5PH H1025 and 300M: Tmax, price.
- Inconel 718 wrought: price. Inconel 718 AM: fatigue, k, recycled CO2.
- Inconel 625 AM: fatigue, k, CTE, Tmax, recycled CO2, price.
- AZ31B: Tmax, price.
- WE43/Elektron 43: Ftu, elongation, fatigue, CTE, price.
- CFRP QI: elongation, fatigue, recycled CO2, price.
- GFRP 7781/913: fatigue, k, CTE, Tmax, CO2 recycled, price.
- CF/PEEK: fatigue, k, CTE, Tmax, FST results, recycled CO2, price.
- PEEK 450G: Ftu, fatigue, CO2 (only an unattributed web range of 7.5–13), price.
- ULTEM 9085: fatigue, k, CO2, price.
- PA 2200: fatigue, recycled CO2, price. EOS states "45% less CO2e" for CarbonReduced but gives no absolute number.
- PA12-CF: fatigue, CTE, CO2, price, FST data.
- Nomex HRH-10: everything except density. Shear values are in the entry's notes.
- Material not found at all: no T700 CFRP entry was made (IM7/8552 is used). No TIMETAL 555 or ATI sheet, no APWORKS sheet, no MMPDS (current edition, paywalled) and no AMS spec text was read.
