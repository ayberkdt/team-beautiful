# Eco data for aerospace structural materials (embodied energy, CO2, recycling, price)

Researched 2026-11-01. Provenance key used throughout:
- **[FULL-PDF]** = I downloaded the PDF and extracted its text myself (pdftotext), so I read the exact table.
- **[FULL-FETCH]** = full web page read through the fetch tool. A small model summarised it, so the wording is the tool's; the numbers were quoted back as page text.
- **[SNIPPET]** = only seen in a search-engine summary or snippet. Not read in the source. Check before citing.
- **UNVERIFIED (memory)** = not found in any source this session.

Recommended practice for competition day: **the numbers that count are the ones in the team's own Granta EduPack install** (open each record, then "Eco properties"). Use this file to sanity-check EduPack and to explain the spread between sources, not as a replacement for it.

---

## Q1. What does Ashby "Materials and the Environment" (2nd ed., 2013) / EduPack say? Is there a public table that reproduces it?

### Takeaway
A free 12-page PDF, "Useful Numbers for Environmental Studies – Ch. 1 Materials" (2017), reproduces Ashby 2nd ed. (2013) data sheet values with page numbers. It covers **material families**: aluminium, Mg alloys, Ti alloys, stainless, Ni superalloys, CFRP, GFRP and epoxy. It has **no per-alloy rows** (no separate 2024, 7075, Al-Li or 718). I found no official Ansys/Granta public table during this session.

### Cited Findings
All values below come from one source. I read it in full [FULL-PDF]: https://Polybags.Co.uk/environmentally-friendly/useful-numbers-for-environmental-studies.pdf (PDF title "UsefulNumbers-01-Materials", created 2017-02-08). Its ref. [4] = *Ashby, M.F., 2013, Materials and the Environment – Eco-Informed Material Choice, 2nd ed., Butterworth-Heinemann*. Its ref. [5] = Schubert et al. 1996, Automotive Engineering. The page numbers are the ones the PDF gives for Ashby's book.

| Family (Ashby 2nd ed.) | Primary embodied energy (MJ/kg) | Primary CO2 (kg/kg) | Recycling energy (MJ/kg) | Recycling CO2 (kg/kg) | Recycle fraction in current supply | Where in PDF / Ashby page |
|---|---|---|---|---|---|---|
| Aluminium (generic) | 210 ± 10 (compiled from several data sets; excludes fabrication) | 12 | 26 (cast), 26.7 (wrought), from Schubert 1996 [5], not Ashby | 2.1 (average) | 41–45 % (2012 estimate) | PDF p.1; Ashby p.471 |
| Magnesium alloys | 300–330 | 36 | 23–26 | 2.9 | 36–41 % | PDF p.3; Ashby p.473 |
| Titanium alloys | 650–720 | 46.5 | 78–96 | 5.2 | 23 % | PDF p.4; Ashby pp.127, 474, 487, 488 |
| Stainless steel | 81–88 | 5.0 | 11–13 | 0.73 | 35–40 % | PDF p.3; Ashby pp.463–469 |
| Nickel-based superalloys (proxy for Inconel 718) | 221–244 | 11.6 | 33.8–37.5 | 2.14 | 22–26 % | PDF p.4; Ashby pp.483, 485 |
| Carbon fibre (fibre only) | 450–500 | 33–36 | – | – | – | PDF p.10, "Miscellaneous materials" |
| Fiberglass (GFRP) | 107–118 | 7.47–8.26 | – | – | – | PDF p.11 |
| Epoxy (resin) | 127–140 | 6.8–7.5 | – | – | – | PDF p.5, polymer table, Ashby Ch.15 |

- The same PDF also gives these **processing energies**, from Ashby p.133 (PDF p.9):
  - Autoclave moulding of composites: **100–300 MJ/kg**, the largest shaping energy in the table.
  - Filament winding: 2.7–4.0 MJ/kg.
  - Spray/lay-up: 14–18 MJ/kg.
  - Metal powder forming: 20–30 MJ/kg.
  - Casting: 8–12 MJ/kg.
  - Extrusion/foil rolling: 10–20 MJ/kg.
  - Epoxy moulding: 21–23 MJ/kg, 1.7–1.85 kg CO2/kg (Ashby pp.492–525, PDF p.10).
  - [FULL-PDF] same URL.
  - Caution: the pdftotext layout mode scrambles the CO2 columns of the shaping table. The energy column is reliable. Read the CO2 values on the PDF itself.
- An older CES release (CES 2005) gave about **55 kg of carbon per kg** of Ti alloy extraction, as quoted by Rajemi et al. 2009. That is carbon, not CO2. Source: https://yadda.icm.edu.pl/baztech/element/bwmeta1.element.baztech-3fa97f8d-13a2-46c4-b77e-c1f748a4cf13/c/10_Rajemi_Energy_JME_2009_1.pdf [SNIPPET]
- The Ashby 3rd edition (2021) includes data sheets with "embodied energy and process energies, carbon footprints, and recycling data", according to the publisher page https://shop.elsevier.com/books/catalog/isbn/9780128215210 [SNIPPET]. I did not see the 3rd-edition values.

### Inferences
- In Ashby's table, the AM alloys (AlSi10Mg, Scalmalloy) and Al-Li are covered only by the generic aluminium row. AM powder adds a powder-production step on top, which this table does not include.
- The carbon fibre row is **fibre only**. A CFRP laminate is roughly 60 % fibre by volume plus epoxy plus prepreg and autoclave energy. Computing a laminate value requires a rule of mixtures plus 100–300 MJ/kg for the autoclave. EduPack's CFRP records already include this, which is another reason to use the EduPack record rather than the fibre value.

### Gaps
- No public source this session gives per-alloy EduPack eco values (2024-T3, 7075-T6, 7050-T7451, 2099/2195/2050, 6061-T6, AlSi10Mg, Scalmalloy, 17-4PH, In718, PEEK/PEKK, IM7/8552). **Read them from EduPack on the day.**
- I did not find an Ansys "Eco data sheet" PDF at ansys.com/academic/educators/education-resources. I did not search that site directly.

---

## Q2. ICE (Bath), IAI and peer-reviewed LCAs: how big is the spread, and why?

### Takeaway
For primary aluminium the spread is about **4 to 22+ kg CO2e/kg**. Electricity source for smelting is the dominant driver:
- 2023 global average (IAI): **14.8**
- Ashby: 12
- European consumption mix: about 10
- ICE v3: about 9.2

For titanium, one 2025 LCA shows that the grid alone moves Ti-6Al-4V ingot from **37.3** (Chinese grid) to **16.1** (hydro) kg CO2e/kg.

### Cited Findings
**Aluminium**
- IAI aluminium carbon footprint FAQ, https://international-aluminium.org/landing/aluminium-carbon-footprint-faqs/ [FULL-FETCH]:
  - Most cradle-to-gate primary footprints "fall in the range 4.5–22 t CO2e per tonne primary aluminium". Best practice reaches ≤4 t.
  - **2023 global average 14.8 t CO2e/t**.
  - Electrolysis electricity alone is 8.6 t of that.
  - By power source, the FAQ chart shows "Hydro ~10, Gas ~13, Coal ~30" t CO2e/t. This conflicts with the 4.5–22 "most" range on the same page; the chart is probably plotting full-chain or worst-case values. Flag this if you use it.
- My calculation from that FAQ checklist: electricity is about 60 % of the 2023 total.
- IAI press release (Dec 2024): primary intensity fell from 15.1 (2022) to **14.8 t CO2e/t (2023)**, −11.5 % since 2020. Source: https://kyodonewsprwire.jp/release/202412131670 [SNIPPET]
- ING (Nov 2024, citing IAI): in 2023, 72 % of China's aluminium capacity was coal-fired and about 19 % hydro; Asia excluding China was 86 % coal. Source: https://think.ing.com/articles/green-aluminium-bundle-understanding-aluminiums-emissions [SNIPPET; the full page refused the connection]
- Hydro example: the Alouette smelter (Québec) estimated **3.9 t CO2e/t** (2019, Scope 1–3), per the same ING search result [SNIPPET].
- China at about 15–17 t CO2e/t, from AlCircle, which names no source: https://www.alcircle.com/news/790-mt-of-emissions-and-counting-chinas-18-tcoe-aluminium-production-in-a-1-5c-world-117321 [SNIPPET, low quality]
- IAI dataset method note: the 2005–2018 data sets are "NOT COMPARABLE" to 2019–2021 because of changes in method and background data. Electricity emissions use IEA regional factors. Source: https://international-aluminium.org/statistics/greenhouse-gas-emissions-primary-aluminium/ [FULL-FETCH; the regional numbers did not load in text]
- ICE v3 (2019) "Aluminium, general" **9.16 kg CO2e/kg** and cast 9.22, as reproduced by HKUST: https://cejcheng.people.ust.hk/ec/carbonInventoryLocalized.html [SNIPPET]. A calculator site gives 8.24 for ICE v3: https://datadrivenaec.com/tools/embodied-carbon-calculator-by-material [SNIPPET]. These two disagree.
- ICE v4.0 was launched in Nov 2024 (webinar slides): https://circularecology.com/wp-content/uploads/2024/11/Webinar-2-ICE-V4.0-Launch-28-Nov-24.pdf [SNIPPET; I did not read v4 values]
- European Aluminium / ÖKOBAUDAT: primary (EU consumption mix) about **10.1 kg CO2e/kg**, recycled about **0.26**, under EN 15804+A2. Source: https://greencalculus.com/standards/european-aluminium-environmental-profile-report/ [SNIPPET]
- Energy Star / Aluminum Extruders Council (2008): 207 MJ/kg virgin vs 12 MJ/kg recycled. Source: https://www.energystar.gov/sites/default/files/specs/AluminummExtrudersCouncil_15Aug08.pdf [SNIPPET; data before 2010]

**Titanium (spread driven by the grid)**
- Lessard, Darunte, Jayanathan (Apple), *J. Sustainable Metallurgy* 2025, supplementary information, Table S-2. Source: https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs40831-025-01258-1/MediaObjects/40831_2025_1258_MOESM1_ESM.pdf [FULL-PDF]. Results for Ti-6Al-4V ingot, cradle-to-gate, sponge inventory from Gao et al. 2018:

  | Ti-6Al-4V ingot | Average Chinese grid (kg CO2e/kg) | Hydroelectricity (kg CO2e/kg) |
  |---|---|---|
  | Primary | **37.3** | **16.1** |
  | Recycled | **3.1** | **0.2** |

  - The "Electricity (sponge + EBeam melting)" line is **21.9** on the Chinese grid and **1.4** on hydro.
  - Other contributors are the same in both scenarios: direct emissions 2.5, NaOH 2.3, Mg 4.7, vanadium 1.7.
  - Column alignment comes from text extraction. The totals line "37.3 16.1 3.1 0.2" is unambiguous.
- The same supplement, Table S-3, gives stainless 316L ingot: primary **11.4 kg CO2e/kg**, 80 % recycled content **3.3** [FULL-PDF]. This is a proxy for 17-4PH, not the same alloy.
- Nuss & Eckelman 2014, PLoS ONE 9(7):e101298, covers 63 metals (ecoinvent 2.2, global 2008 data). The per-kg values are only in Figs. 2/3A and Table S38, which I could not read. Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0101298 [FULL-FETCH of text; no numbers obtained]

### Inferences
- **Why the spread:**
  1. Smelting electricity: coal vs hydro alone moves aluminium by about 10 t CO2e/t and titanium by about 20 kg CO2e/kg.
  2. System boundary: whether casting and fabrication are included, and whether direct PFC emissions are counted.
  3. Data year: Ashby compiles data sets mostly from before 2012, IAI uses 2023, ICE v3 dates to 2019.
  4. Geography of the mix: global average (IAI, dominated by China) vs EU consumption mix (European Aluminium, ÖKOBAUDAT) vs UK construction mix (ICE).
- Recommendation for the eco audit: run a **sensitivity case** with low (hydro, about 4–10) and high (China coal, about 15–20+) primary Al values. Show that the material ranking holds, or does not, across that range.
- The ICE database is a construction database and has no aerospace alloys. Use it only as a cross-check for generic aluminium and steel.

### Gaps
- I could not read the IAI regional table (China, GCC, North America, Europe) in text. The page loads it dynamically.
- No ICE value for Ti, CFRP or Mg was found this session.
- Gao et al. 2018 (J. Clean. Prod. 174:771–779, Kroll sponge in China): I did not read it, so I have no sponge-only number.

---

## Q3. Carbon fibre production energy and CO2, and the PAN precursor share

### Takeaway
Published PAN-based CF values span about **170 MJ/kg** (process energy only) to about **200–900 MJ/kg** (cradle-to-gate primary energy), and about **13–36 kg CO2e/kg**. A 2024 hotspot analysis attributes about **37 %** of CF climate impact to the PAN precursor and **59 %** to process energy.

### Cited Findings
- "Bringing Light into the Dark—Overview of Environmental Impacts of Carbon Fiber Production and Potential Levers for Reduction", *Polymers* 2024. I did not capture the authors; the search listing suggests a Fraunhofer affiliation. Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10780919/ [FULL-FETCH, first 100 k of 131 k characters]
  - Process energy: **170 MJ (thermal + electric) per kg CF** (Section 3.2, Table 1; reviewed by an industry advisory board).
  - Climate-change share (Fig. 4a): energy **59 %**, PAN **37 %**.
  - Fossil-resource share (Fig. 4b): energy 48 %, PAN 50 %. Within PAN, acrylonitrile accounts for 76 % of the climate impact.
  - Electricity-mix scenarios (abstract): **13.0–34.1 kg CO2e/kg CF** and fossil resource use **262.3–497.9 MJ/kg CF**.
    - China grid: 34.1 kg CO2e/kg and 497.9 MJ/kg.
    - Japan: 485.1 MJ/kg.
    - Renewables plus an optimised process cuts climate impact by about 53 %.
  - Section 7 quotes 13–29 for the global scenarios. That is not fully consistent with the abstract, so check Figs. 5–8 before citing.
- **Das 2011**, *Int. J. LCA* 16(3):268–282. Literature summaries list it at **704 MJ/kg and 31 kg CO2e/kg** for PAN CF. I saw this in a search summary of ICCM23 slide deck 552 (https://iccm-central.org/Proceedings/ICCM23proceedings/papers/ICCM23_PPT_552.pdf) [SNIPPET; the URL now returns 404]. The same summary lists other PAN CF values of about 771–1,169 MJ/kg [SNIPPET]. ORNL record: https://www.ornl.gov/publication/life-cycle-assessment-carbon-fiber-reinforced-polymer-composites
- Virgin CF manufacture **198–595 MJ/kg**, quoted in a Nottingham CF-recycling paper: https://nottingham-repository.worktribe.com/OutputFile/940143 [SNIPPET]
- A 2025 Springer review states that about 90 % of CF is PAN-based and that the precursor is more than 50 % of CF *cost*. It gives roughly epoxy about 78 MJ/kg and prepreg about 40 MJ/kg, and fabrication energy of 200–900 MJ/kg; the review itself writes "kJ/kg" in one place, which looks like a typo. Source: https://link.springer.com/article/10.1007/s42114-025-01497-6 [SNIPPET]
- Ashby 2nd ed.: CF 450–500 MJ/kg, 33–36 kg CO2/kg. GFRP 107–118 MJ/kg, 7.47–8.26 kg CO2/kg. See the Q1 table [FULL-PDF].
- Suzuki & Takahashi (2005) and Witik et al. (2011/2013): **I did not find their numbers this session.** Remembered values (Suzuki & Takahashi about 286 MJ/kg CF; Witik about 183–286 MJ/kg) are **UNVERIFIED (memory)**. Do not cite them.

### Inferences
- The spread comes from:
  1. Boundary: process energy only (170) vs cradle-to-gate primary energy including PAN (about 260–700+).
  2. Grid: a factor of about 2.6 in CO2.
  3. Plant scale: lab-scale data overestimates.
- For a CFRP part, the fibre value is not the part value. Add the resin (epoxy 127–140 MJ/kg per Ashby), prepregging, and autoclave cure (100–300 MJ/kg per Ashby). Scrap is also high: buy-to-fly for prepreg layup is commonly 1.2–1.5, which is **UNVERIFIED (memory)**.

### Gaps
- No verified eco data for PEEK/PEKK thermoplastic matrices or for CF/PEEK (APC-2, Toray TC1200) laminates.
- No verified IM7/8552-specific LCA.

---

## Q4. Titanium: Kroll energy and CO2, and what powder atomisation adds

### Takeaway
Primary Ti-6Al-4V ingot is about **16 (hydro) to 37 (Chinese grid) kg CO2e/kg** (Lessard et al. 2025), against Ashby's 46.5 kg CO2/kg and 650–720 MJ/kg. Gas-atomised Ti-6Al-4V powder LCAs report about **20–28 kg CO2e/kg**. Those powder figures are from search snippets only and their boundaries differ, so treat the AM powder premium as uncertain.

### Cited Findings
- Ti-6Al-4V ingot: primary 37.3 / 16.1, recycled 3.1 / 0.2 kg CO2e/kg (Chinese grid / hydro). Lessard et al. 2025, Table S-2 [FULL-PDF]; URL in Q2.
- Ashby Ti alloys: 650–720 MJ/kg, 46.5 kg CO2/kg, recycled 78–96 MJ/kg and 5.2 kg CO2/kg, recycle fraction 23 % [FULL-PDF]; see Q1.
- Kroll sponge needs "around 25 kWh per kilogram of sponge" (about 90 MJ/kg electricity, my conversion). Source: DRDO Defence Science Journal, https://publications.drdo.gov.in/ojs/index.php/dsj/article/download/5966/3094 [SNIPPET; older data]
- Powder production:
  - 6K vendor LCA (UniMelt plasma, recycled feed): 56,268 MJ and 2,748 kg CO2e per 100 kg Ti powder, i.e. about 563 MJ/kg and 27.5 kg CO2e/kg (my arithmetic). The boundary is "cradle-to-end user". Source: https://go.6kinc.com/hubfs/LCA/Foresight_6K_Ti_LCA_FINAL.pdf [SNIPPET; vendor-commissioned]
  - Xiao et al. 2024, *Autonomous Intelligent Systems*: Ti alloy powder life-cycle about **20 kg CO2e/kg**, slightly above Ni-alloy powder. Source: https://journal.hep.com.cn/ais/EN/10.1007/s43684-024-00079-5 [SNIPPET]
  - Spreafico & Ordek 2025: atomisation plus chlorination are more than 70 % of the impact of Ti6Al4V powder. Source: https://aisberg.unibg.it/handle/10446/303990 [SNIPPET]
  - Herrera et al. 2023 (Sustainability 15:6649): ball milling is 87.8 % lower in kg CO2e than gas atomisation for Ti6Al4V powder. Source: https://ideas.repec.org/a/gam/jsusta/v15y2023i8p6649-d1123487.html [SNIPPET]
  - IperionX (company press release, 2023): recycled Ti powder **7.8 kg CO2e/kg**, "80 % lower" than Kroll-route ingot. Source: https://iperionx.com/lca [SNIPPET; commercial interest]
- Norgate et al. 2007 (Ti about 361 MJ/kg, about 35.7 kg CO2e/kg): **UNVERIFIED (memory)**, and the data predate 2010.

### Inferences
- The powder values do not separate "ingot plus atomisation" from "sponge plus atomisation", so the increment from atomisation alone cannot be read from these sources.
- Order of magnitude: powder is at least as carbon-intensive as ingot, and AM buy-to-fly (about 1.1–1.5, vs 10–20 for machined forgings; **UNVERIFIED (memory)**) is where AM wins back the difference.

### Gaps
- No verified kWh/kg for gas atomisation alone. Read Spreafico & Ordek 2025 or Herrera 2023 in full to get one.
- No verified powder data for AlSi10Mg or Scalmalloy.

---

## Q5. Is recycled aluminium about 5 % of primary energy?

### Takeaway
**About 5 % holds only for remelting clean scrap**, consistent with an IAI-attributed 186 vs 8.3 GJ/t. Older or wider-boundary data give **6–12 %**: Ashby's reproduction gives 26 vs 210 MJ/kg, about 12 %. On CO2, European Aluminium's recycled figure of 0.26 vs 10.1 kg CO2e/kg is about 3 %, but that ratio depends on allocation.

### Cited Findings
- Recycling saves "95% of the energy it would take to make primary aluminium". Source: Australian Aluminium Council (IAI member), submission to the Productivity Commission, https://pc.gov.au/__data/assets/pdf_file/0003/387462/sub086-circular-economy.pdf [SNIPPET]
- Primary about 186 GJ/t vs recycled 8.3 GJ/t (about 4.5 %), attributed to IAI. Source: https://climate.selectra.com/es/reciclaje/aluminio [SNIPPET; secondary]. Another secondary source gives 13.6 GJ/t for recycling (about 7 %): https://www.okonrecycling.com/industrial-scrap-metal-recycling/steel-and-aluminum/aluminum-recycling-costs/ [SNIPPET]
- Ashby reproduction: primary 210 ± 10 MJ/kg vs recycled 26–26.7 MJ/kg (Schubert 1996), about 12 % [FULL-PDF].
- Energy Star / AEC 2008: 12 vs 207 MJ/kg, about 6 % [SNIPPET].
- European Aluminium / ÖKOBAUDAT: recycled 0.26 vs primary 10.1 kg CO2e/kg [SNIPPET]. Q2 has the URL.

### Inferences
- Aerospace caveat: 2xxx and 7xxx plate needs tight Fe and Si limits, so aerospace plate is made mostly from primary metal plus prime scrap. The "recycled content" lever in EduPack should be set conservatively, for example the default recycle fraction rather than 100 %. I found no source for the actual recycled content of aerospace plate; this is a **gap**.

### Gaps
- No primary IAI fact-sheet text was read this session. Every "5 %" source above is secondary or a snippet.

---

## Consolidated competition table

How to read it:
- **Eco columns:** as sourced above.
- **Mechanical columns:** **UNVERIFIED (memory)**, typical handbook values (MMPDS or datasheet order of magnitude). Check them in EduPack before using in a calculation.
- **Price column:** UNVERIFIED (memory), order of magnitude only. No authoritative 2024–26 price series was found; the only price sources seen were vendor and blog pages, listed below.

| Material | ρ (g/cm³) [mem] | E (GPa) [mem] | σy / σUTS typical (MPa) [mem] | Primary EE (MJ/kg) | Primary CO2 (kg CO2e/kg) | Recycled-route value | Recycle fraction in supply | Price (USD/kg) [mem] | EoL recyclability |
|---|---|---|---|---|---|---|---|---|---|
| Al 2024-T3/T351 | 2.78 | 73 | 325 / 470 | Ashby generic Al: 200–220 | Ashby 12; IAI 2023 global 14.8; range 4–22 (IAI); ICE v3 about 9.2 [snip]; EU mix about 10.1 [snip] | 26–27 MJ/kg, 2.1 kg CO2/kg (Ashby repro.); EU 0.26 kg CO2e/kg [snip] | 41–45 % (2012, Ashby) for generic Al | about 5–15 (aerospace plate) | High (remelt); alloy segregation needed for 2xxx/7xxx |
| Al 7075-T6 | 2.81 | 71.7 | 503 / 572 | as above | as above | as above | as above | about 5–15 | as above |
| Al 7050-T7451 | 2.83 | 71.7 | 455 / 525 (thick plate) | as above | as above | as above | as above | about 6–15 | as above |
| Al-Li 2099 / 2195 / 2050 | about 2.63 / 2.71 / 2.70 | about 77–80 | about 470–520 / 500–560 (2195-T8 higher) | **No verified data**; Li adds burden (unquantified) | **No verified data** | – | – | about 15–40 | Recyclable, but Li scrap must be kept separate |
| Al 6061-T6 | 2.70 | 68.9 | 276 / 310 | generic Al | generic Al | generic Al | generic Al | about 3–6 | High |
| AlSi10Mg (AM) | 2.67 | about 70 | about 230–270 / 350–450 (as built) | generic Al + powder step (unquantified) | – | – | – | powder about 30–80 | Powder reuse; parts remelt |
| Scalmalloy (AM) | 2.67 | about 70 | about 470–500 / 520 | **No verified data** (Sc burden unknown) | – | – | – | powder about 150–300+ | as above |
| Ti-6Al-4V wrought | 4.43 | 114 | 880 / 950 | Ashby 650–720 | Ashby 46.5; Lessard 2025: 37.3 (CN grid) / 16.1 (hydro) | Ashby 78–96 MJ/kg, 5.2 kg CO2; Lessard recycled 3.1 / 0.2 | 23 % (Ashby) | about 30–60 (plate/bar) | High value; revert (scrap remelted for reuse) needs VAR/EB remelt and clean scrap |
| Ti-6Al-4V AM powder | 4.43 | about 110 | about 900–1000 / 1000–1100 (HIP) | 6K: about 563 MJ/kg incl. upstream [snip, vendor] | about 20 (Xiao 2024) to 27.5 (6K) [snip] | IperionX recycled powder 7.8 [snip, vendor] | – | about 150–400 | Powder reuse is limited by oxygen pickup |
| CFRP thermoset (IM7/8552) | about 1.57–1.60 | about 60–70 (quasi-isotropic); about 160 (0° UD) | about 600–900 (QI); about 2,500 (0° UD) | Fibre: Ashby 450–500; Polymers 2024: 262–498 (fossil); Das 2011: 704 [snip]. Epoxy 127–140. Autoclave +100–300 | Fibre: Ashby 33–36; Polymers 2024: 13.0–34.1; Das 31 [snip]. Epoxy 6.8–7.5 | rCF (pyrolysis): no verified number | about 0 % | prepreg about 40–120 | **Poor**: pyrolysis or solvolysis gives shortened fibres; mostly landfill or incineration |
| CFRP thermoplastic (CF/PEEK, CF/PEKK) | about 1.55–1.60 | similar to thermoset | similar | **No verified data** for PEEK/PEKK | – | – | – | about 100–200+ | Better: re-meltable and weldable, but rarely recycled in practice |
| GFRP (E-glass/epoxy) | about 1.9–2.0 | about 20–40 | about 300–600 | Ashby 107–118 | Ashby 7.47–8.26 | – | about 0 % | about 3–10 | Poor (mostly cement kiln, landfill) |
| Mg AZ31B | 1.77 | 45 | 200 / 260 | Ashby Mg alloys 300–330 | Ashby 36 | 23–26 MJ/kg, 2.9 kg CO2 | 36–41 % | about 3–8 | Recyclable; flux remelt |
| Mg WE43 | 1.84 | 44 | about 170–200 / 250–300 | as above (rare-earth burden not included) | as above | as above | as above | about 30–60 | as above |
| 17-4PH stainless (H1025) | 7.8 | 197 | about 1,000 / 1,070 | Ashby stainless 81–88 | Ashby 5.0; Lessard 316L 11.4 (primary), 3.3 (80 % RC) | 11–13 MJ/kg, 0.73 kg CO2 | 35–40 % | about 5–15 | High |
| Maraging 300 | 8.0 | 190 | about 1,900–2,000 / 2,000 | **No verified data** (18 % Ni, Co, Mo: likely above stainless) | – | – | – | about 20–40 | High (Ni/Co value) |
| Inconel 718 | 8.19 | 200 | about 1,030–1,100 / 1,240–1,380 | Ashby Ni superalloys 221–244 | Ashby 11.6 | 33.8–37.5 MJ/kg, 2.14 kg CO2 | 22–26 % | about 30–80 | High value; revert loop used in industry |

Price sources seen. All are low quality and none is an aerospace benchmark:
- Vendor blog: Ti-6Al-4V material cost is 5–10 times 7075-T6, and finished parts 3–6 times. Source: https://cnc.bozemetal.com/blog/titanium-vs-aluminum-aerospace-structural-components-material-selection-trade-off/ [SNIPPET]
- Prepreg about $15–60/kg ply. Source: https://new.risingsunartscentre.org/news/carbon-fiber-cost-per-kg-prices-ranges-and-key-drivers-2026.html [SNIPPET; dubious site]

### Magnesium flammability note
FAA/EASA rules for Mg alloys in the cabin (FAA policy accepting Mg in seat structures since about 2015; flammability test per SAE AS8049) are **UNVERIFIED (memory)**. I did not search for them this session.
- As I recall, WE43 passed the FAA burner test while AZ31 was not accepted for cabin interiors. This is also **UNVERIFIED (memory)**.
- Before claiming Mg is acceptable for a cabin part, check FAA Policy Statement PS-ANM-25-xx and the FAA Fire Safety Branch reports.

## Remaining gaps (summary)
1. Per-alloy eco values for every Al grade, Al-Li, AM alloys, PEEK/PEKK and maraging. Use EduPack.
2. IAI regional intensities (China vs GCC vs Europe vs North America) for 2023.
3. Gao et al. 2018 sponge-only Kroll energy and CO2.
4. Suzuki & Takahashi and Witik CF values: not read.
5. An authoritative price series. EduPack's price field is the practical option on the day.
6. Mechanical properties are memory only. Use MMPDS or EduPack.
