# Manufacturing-phase energy and CO2 for aerospace parts: machining vs AM, and composite processing

Research date: 2026-11-01. Scope: the "manufacture" phase (and the material/buy-mass effect that is tied to it) of an eco audit of a topology-optimised aerospace bracket/fitting (EUROAVIA Ideathon 2026, Ansys/Granta EduPack).

**Verification labels used on every number**
- **[FULL TEXT]**: I read the primary document text myself in this session (PDF extracted with `pdftotext`, or the HTML article itself).
- **[SNIPPET]**: I saw it only in a search-engine snippet or abstract summary. I did not open the paper. Check it before you cite it.
- **[UNVERIFIED (memory)]**: from my background knowledge. No source was opened.

**Access problems found in this session:** Elsevier/ScienceDirect, Wiley JIE, the IRIS repositories at unipa.it and polito.it, and the Nottingham repository all returned HTTP 403 to both WebFetch and curl. MIT DSpace returned 429. As a result, I could **not** read the full texts of Huang et al. 2016, Ingarao/Priarone et al. 2018, Kellens et al. 2017 (JIE and Procedia CIRP), Priarone et al. 2017/2021, or the 2023 LCA of CNC/WAAM/SLM. Their numbers below are [SNIPPET] only.

Unit conversion used for ORNL values: 1 MJ/kg = 429.92 Btu/lb. 1 Btu = 1.05506 kJ. The ORNL report itself prints both units for Appendix 3–4, and those printed pairs agree with this factor.

---

## Q1. Typical buy-to-fly (BTF) ratios for aerospace parts by route

### Takeaway
Machining Ti or Al aerospace parts from plate, billet or forging typically gives a BTF of about 8:1 to 33:1. Powder-bed AM (EBM, L-PBF) is typically modelled at about 1.2–1.5:1, and WAAM/arc-DED preforms at about 1.1–6:1. The only BTF values I read in full text are the ORNL bracket case studies (33:1 and 8:1 machined vs 1.5:1 EBM) and the Suárez 2023 forged-preform figure (>10).

### Cited Findings
- **ORNL/DOE 2014, Case Study 1** (Ti-6Al-4V aircraft cabin bracket for galleys and lavatories, same geometry). Conventional route is forging plus machining at **BTF 33:1** (initial mass 0.89 lb, final 0.027 lb). The EBM route is **BTF 1.5:1** (0.044 lb powder for a 0.027 lb part). Source: Nimbalkar, Cox, Visconti, Cresko, *Life Cycle Energy Assessment Methodology, Tool and Case Studies for Additive Manufacturing*, ORNL/TM-2014/93, July 2014, report pp. 54–56, Figure 11 and Table 6. **[FULL TEXT]** — [ORNL PDF](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf)
- **ORNL 2014, Case Study 2** (topology-optimised Ti-6Al-4V cabin bracket). The conventional machined bracket has **BTF 8:1** (19.22 lb stock, 2.4 lb part). The topology-optimised EBM bracket has **BTF 1.5:1** (1.26 lb powder, 0.84 lb part). The report states it is **65 % lighter**. Report pp. 57–58, Figure 12 and Table 7. **[FULL TEXT]** — [ORNL PDF](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf)
- **Suárez et al. 2023**, *Materials* 16(22):7177, DOI [10.3390/ma16227177](https://doi.org/10.3390/ma16227177). The forged-preform route for aeronautical Ti-6Al-4V parts has a "high Buy To Fly (BTF) ratio (>10)" (Abstract). The paper says WAAM "significantly mitigates" BTF but gives **no number** for it. Its arc-DED Ti-6Al-4V deposition rate is **1.3 kg/h** at 4.3 m/min wire feed (1.2 mm wire) and 0.8 kg/h at 2.7 m/min (Section 2.4, Table 2). It explicitly does not measure energy or CO2. **[FULL TEXT]** — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10672625/)
- **Atescan-Yuksek et al. 2024** (IJAMT, below) cite a prior study [their ref. 18] that compared CFRP with aluminium at **BTF 1:1 and 8:1** (Introduction). **[FULL TEXT]** of the citing paper; the cited study itself was not read. — [Cranfield repository PDF](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content), DOI [10.1007/s00170-024-13241-3](https://doi.org/10.1007/s00170-024-13241-3)
- A secondary source says conventional BTF for aircraft Al and Ti components ranges from **12:1 to 25:1**, citing Huang et al. (2015/2016). **[SNIPPET]** I did not confirm this in Huang's paper. — seen in search results around [ORNL Impact record](https://impact.ornl.gov/en/publications/energy-and-emissions-saving-potential-of-additive-manufacturing-t/)
- Northwestern press release (2015, on the Huang et al. work) says a 1 kg bracket made conventionally can need about **10 kg** of raw material (≈10:1). **[SNIPPET]** — [Northwestern McCormick](https://www.mccormick.northwestern.edu/news/articles/2015/06/saving-money-and-the-environment-with-3-d-printing.html)
- WAAM case figures (secondary): a landing-gear part goes from **≈11.5:1** machined from billet to **≈1.14:1** with a WAAM near-net preform. A Fokker-related part goes from **37:1** from solid billet to **6.3:1** with WAAM. **[SNIPPET]**; these came from a 2015 International Titanium Association conference presentation and a 2016 trade blog. — [ITA Titanium Europe 2015 (Addison)](https://cdn.ymaws.com/titanium.org/resource/resmgr/AddisonAdrianTiEU2015-3DAddi.pdf); [Inside Metal AM 2016](https://insidemetaladditivemanufacturing.com/2016/04/03/building-large-metallic-parts-with-wire-arc-additive-manufacturing/)
- Ti forgings: a figure attributed to Barnes et al. gives BTF **≈21** for Ti forgings and **≈11** for machined parts. **[SNIPPET]** — [ResearchGate figure](https://www.researchgate.net/figure/The-effect-on-buy-to-fly-ratios-on-conventional-vs-additive-manufacturing_fig4_312115931). A MATEC 2020 (Ti-2019) paper on Ti forgings gives about **9:1** for forged-and-machined parts. **[SNIPPET]** — [MATEC](https://www.matec-conferences.org/articles/matecconf/pdf/2020/17/matecconf_ti2019_02005.pdf)
- [UNVERIFIED (memory)] Near-net Ti forgings are often quoted at about 3–8:1. L-PBF parts are often quoted at about 1.2–2:1 once supports and machining allowance are counted. Al parts machined from thick plate (e.g. 7050/7075 ribs) are often quoted at 10–20:1.

### Inferences
- For a topology-optimised bracket, the machined baseline BTF is the most sensitive manufacture-related input. ORNL's own two brackets differ by 4× (33:1 vs 8:1). The team should **calculate** BTF from their own geometry: stock bounding block mass ÷ final part mass. A literature value should not be assumed.
- Topology-optimised shapes tend to push the machined BTF **up**, because the part shrinks while the bounding stock barely changes. This makes AM look comparatively better (inference from the ORNL Case 2 geometry, not a cited claim).

### Gaps
- No full-text source read here gives L-PBF or DED BTF as a measured value. The ORNL report uses 1.5:1 for EBM as an assumption.
- I could not read Huang et al. 2016 Table/SI values for BTF by material (publisher returned 403).

---

## Q2. Specific energy consumption (SEC) of L-PBF, EBM, DED, WAAM vs CNC; powder atomisation

### Takeaway
Process-electricity SEC for metal powder-bed AM is around 60–160 MJ/kg melted. That is 1–2 orders of magnitude above machining, which is about 3–8 MJ/kg for finishing (Ashby values in ORNL) and about 100 MJ/kg for "heavy" machining. Gas atomisation adds only about 15 MJ/kg on top of about 610 MJ/kg embodied energy for primary Ti-6Al-4V. So for Ti, the **material** (buy mass) dominates the cradle-to-gate energy, not the process.

### Cited Findings
**ORNL/TM-2014/93 appendix tables** (read in full text, PDF pp. 74–76 = report pp. 72–74):
- Appendix 4a, "AM processes embodied energy" (data source Baumers 2013 unless noted). **SLM 118.2 MJ/kg** (50,800 Btu/lb). **DMLS 158.4 MJ/kg**. **EBM 118.9 MJ/kg** (51,133 Btu/lb; this is the value used in both bracket case studies). Powder-bed average 131.8 MJ/kg. **DMD (laser DED) 98.3 MJ/kg**. DED average 118.2 MJ/kg. FDM 178.0 MJ/kg (Stratasys). **[FULL TEXT]** — [ORNL PDF](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf)
- Appendix 4b (reference only, from Bourhis 2013). **Arcam A1 EBM, Ti-6Al-4V: 61 MJ/kg**. MTT SLM 250 with 316L: 112 MJ/kg. EOSINT M250 Xtended (bronze-Ni): 19 MJ/kg. **[FULL TEXT]** — same PDF
- Appendix 3b, secondary processes (Ashby). **Machining heavy 108.9 MJ/kg**. **Machining finishing (light) 8 MJ/kg**. Grinding 30 MJ/kg. Water-jet/EDM/laser 2,750 MJ/kg. Baked coatings 65 MJ/kg. Appendix 3a, primary shaping: **rough rolling/forging 15.9 MJ/kg**, casting 10 MJ/kg, metal powder forming 25 MJ/kg. **[FULL TEXT]** — same PDF
- Appendix 1, materials (Ashby). **Ti-6Al-4V primary 263,328 Btu/lb ≈ 612.5 MJ/kg**, recycled 37,403 Btu/lb ≈ 87.0 MJ/kg. **Ti-6Al-4V powder 269,691 Btu/lb ≈ 627.3 MJ/kg** primary, described as "Ti alloy + atomization (14.8 MJ/kg)". **Al alloys 90,284 Btu/lb ≈ 210 MJ/kg** primary, 11,178 Btu/lb ≈ 26 MJ/kg recycled. CFRP 204,213 Btu/lb ≈ 475 MJ/kg. **[FULL TEXT]** (MJ/kg values converted by me from the printed Btu/lb; the atomisation value of 14.8 MJ/kg is printed in the table) — same PDF
- The ORNL report itself notes that "Detailed data about MJ/kg (or Btu/lb) for AM processes ... is often lacking" (Section on limitations, report p. ~49). **[FULL TEXT]**

**Other sources (not read in full):**
- Kellens et al. 2017, *J. Industrial Ecology* 21(S1):S49–S68, DOI [10.1111/jiec.12629](https://doi.org/10.1111/jiec.12629). The specific energy of current AM systems is **"1 to 2 orders of magnitude higher"** than that of conventional processes. **[SNIPPET]** (abstract via repository record) — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/119453)
- Baumers et al., SFF Symposium 2010. In their comparison, EBM used about **2.2 kWh** per build or part versus about **7.3 kWh** for SLM, attributed to EBM's faster build. **[SNIPPET]**; the table was garbled — [UT Austin SFF 2010 PDF](http://utw10945.utweb.utexas.edu/Manuscripts/2010/2010-25-Baumers.pdf)
- A PoliTo course exercise (Priarone group) gives EBM Ti-6Al-4V electric SEC as **60–177 MJ/kg**, assuming 20 % support mass and 10 % machining allowance. **[SNIPPET]**; the PDF redirected and could not be opened — [PRz/PoliTo exercise](https://maestro.prz.edu.pl/fcp/eGBUKOQtTKlQhbx08SlkTUgVKQ2pgTx0DDiA-WAJVQG9WFVZpCFghUHcKVj0GQUw/1180/code_RB0QRPwlQIEdwBEQoGhkfBlAHXTgg/outputs/am-machining_comparison_-_exercise-1.pdf)
- 2026 critical review of WAAM sustainability (IJAMT): **SLM 7.30–17.06 kWh/kg** vs **WAAM 3.06–5.39 kWh/kg** across three parts. In another cited case, WAAM is about 16.8 kWh/kg, CNC about 22.8 kWh/kg and SLM about 70.2 kWh/kg. **[SNIPPET]** — [Springer, DOI 10.1007/s00170-026-18690-6](https://link.springer.com/article/10.1007/s00170-026-18690-6)
- 2023 LCA/LCC of pure subtractive vs WAAM vs SLM (J. Manufacturing Processes, ScienceDirect S1526612523005856). SLM needs **307 MJ** cumulative energy for the part, which is ≈3× CNC milling and ≈5× WAAM. **[SNIPPET]**; HTTP 403 — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1526612523005856)
- Ti powder production: the 6K Additive (vendor) LCA gives **56,268 MJ and 2,748 kg CO2e per 100 kg** of Ti powder (≈563 MJ/kg, ≈27.5 kg CO2e/kg) for its UniMelt route, compared with plasma atomisation. **[SNIPPET]**; vendor document, boundaries not checked — [6K Foresight LCA](https://go.6kinc.com/hubfs/LCA/Foresight_6K_Ti_LCA_FINAL.pdf). Xiao et al. 2024 report about **20 kg CO2e/kg** life-cycle for Ti alloy powder. **[SNIPPET]**, no URL to the paper itself was confirmed. Spreafico & Ördek 2025 give a parametric gas-atomisation LCA for Ti-6Al-4V, with energy varying more than 5-fold with parameters (slag TiO2, electrode diameter, argon pressure). **[SNIPPET]** — [Tampere University portal](https://researchportal.tuni.fi/en/publications/parametric-lca-model-for-ti6al4v-powder-production/)

### Inferences
- **Order-of-magnitude rule for an EduPack eco audit:** with ORNL's values, one kg of Ti-6Al-4V that is melted by EBM costs about 119 MJ of process energy. One kg of primary Ti-6Al-4V costs about 612 MJ of material energy. A machined bracket at BTF 8:1 therefore carries about 4,900 MJ of material energy per kg of finished part. The EBM part at BTF 1.5:1 carries about 940 MJ of powder energy plus about 180 MJ of EBM energy per kg of finished part. (My arithmetic from ORNL App. 1 and App. 4a; no recycling credit.)
- **Derived break-even BTF (my inference, not a published figure):** EBM (BTF 1.5) energy is 1.5 × (627.3 + 118.9) ≈ 1,119 MJ per kg of finished part. Machining energy is BTF × (612.5 + ~8). These are equal at **BTF ≈ 1.8**. In words: with ORNL inputs and no scrap credit, EBM wins cradle-to-gate whenever the machined BTF is above about 2. This matches the qualitative Ingarao/Priarone finding below that EBM loses when only a small amount of material has to be removed. With 80 % scrap recycling credit (ORNL assumes 80 %), the threshold rises. The team should recalculate it with the EduPack values for their alloy.
- Note on how Granta EduPack probably books this: in an eco audit the buy-mass effect most likely shows up in the **material** phase, if the team enters stock mass and scrap, not in the **manufacture** phase. I did **not** verify this behaviour in EduPack in this session. Check the EduPack eco-audit help for how "process" rows and "% removed" are handled.

### Gaps
- I did not read in full any SEC values for L-PBF from modern machines (EOS M400, SLM 500, etc.). The ORNL/Baumers 2013 values date from machines of roughly 2010–2013.
- No WAAM SEC was read in full text. The values seen (3–17 kWh/kg) are snippets.
- No peer-reviewed gas-atomisation-only MJ/kg for Ti-6Al-4V was read in full, other than ORNL's 14.8 MJ/kg (whose original source is not stated beyond Ashby/derived).
- A snippet reported WAAM SEC of 1.3 kWh/kg during deposition versus 45.01 kWh/kg once post-processing is included. I could not attribute this to a specific URL, so it is excluded.

---

## Q3. Key peer-reviewed comparisons and their break-even conditions

### Takeaway
All the studies that were located agree that, for flying parts, the **use phase dominates** and AM's manufacturing-phase penalty is small compared with the material saved through low BTF and the fuel saved by lighter weight. Break-even depends on two things: the machined BTF (AM loses when little material is removed), and whether redesign reduces mass. The only quantitative break-even I read in full text is the ORNL bracket data. The Huang, Ingarao and Priarone thresholds remain [SNIPPET] or unread.

### Cited Findings
- **ORNL 2014, Case 1** (same geometry, Ti bracket, 15-year life, long-haul aircraft at 4,971 mi/day for 255 days/yr). Per part: material energy CM **78,383 Btu** vs AM **8,794 Btu**. Manufacturing energy CM **3,195 Btu** vs AM **2,308 Btu**. Use phase **1,120,311 Btu** for both. Total CM 1,197,464 vs AM 1,126,988 Btu, a saving of 70,476 Btu (≈5.9 %), almost all from the material phase. Report p. 54, Table 6. **[FULL TEXT]** — [ORNL PDF](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf)
- **ORNL 2014, Case 2** (topology-optimised, 65 % lighter). Material energy CM **2,021,120 Btu** (≈2,132 MJ) vs AM **263,900 Btu** (≈278 MJ). Manufacturing energy CM **65,485 Btu** (≈69.1 MJ) vs AM **65,872 Btu** (≈69.5 MJ), so the two are **essentially equal**. Use phase CM 99,583,158 Btu vs AM 34,854,105 Btu. Total CM 101.3 MMBtu vs AM 35.0 MMBtu, a saving of 66.2 MMBtu (≈65 %). Use phase is **98.3 %** of the CM life cycle, and manufacturing is about **0.06 %**. Report pp. 57–58, Table 7. **[FULL TEXT]** (percentages are my arithmetic) — same PDF
- **Huang, Riddle, Graziano, Warren, Das, Nimbalkar, Cresko, Masanet 2016**, *J. Cleaner Production* 135:1559–1570, DOI [10.1016/j.jclepro.2015.04.109](https://doi.org/10.1016/j.jclepro.2015.04.109). US fleet-wide life-cycle primary energy savings of **70–173 million GJ/yr by 2050** (one record says 70–174). Cumulative savings of **1.2–2.8 billion GJ**. Cumulative GHG reduction of **92.1–215.0 Mt CO2e**. **[SNIPPET]** (abstract; the two ORNL records disagree on 173 vs 174) — [ORNL Impact](https://impact.ornl.gov/en/publications/energy-and-emissions-saving-potential-of-additive-manufacturing-t/); [ORNL publication page](https://www.ornl.gov/publication/energy-and-emissions-saving-potential-additive-manufacturing-case-lightweight-aircraft). Press coverage gives a **4–7 % aircraft weight reduction** and up to **6.4 % fuel reduction**. **[SNIPPET]**, secondary — [eeNews Europe](https://www.eenewseurope.com/en/3-d-printed-aircraft-parts-will-save-weight-fuel-says-study)
- **Ingarao, Priarone, Deng, Paoletti, Settineri 2018**, *J. Industrial Ecology* (DOI [10.1111/jiec.12523](https://doi.org/10.1111/jiec.12523)), cradle-to-grave comparison of EBM vs machining for Ti-6Al-4V. EBM "could be a more energy-efficient approach than conventional machining, even without re-designing the component", due to raw-material efficiency. But "when a small amount of material has to be machined off, the high energy intensity of an EBM process" penalises it. **[SNIPPET]** (abstract; the full text returned 403, so no numeric threshold was read) — [IRIS UniPA record](https://iris.unipa.it/handle/10447/225481)
- **Atescan-Yuksek, Mills, Ayre, Koziol, Salonitis 2024**, IJAMT, DOI [10.1007/s00170-024-13241-3](https://doi.org/10.1007/s00170-024-13241-3), wing-skin panel, Al-7075 vs five CFRP routes, ReCiPe 2016, Ecoinvent 3.6, 150 million km life. Manufacturing + disposal CO2e: **Al 604 kg**; NCF CF-epoxy 2,940 kg; woven CF-epoxy 2,780 kg; CF-PA6 prepreg 5,660 kg; CF-PA6 injection 3,590 kg; CFSMC 2,420 kg (Table 5). Whole life: Al 7.56 × 10⁶ kg vs NCF CF-epoxy 4.14 × 10⁶ kg (Table 5). Composites overtake Al after **≈100,000–300,000 km** of flight (7–21 days at 14,000 km/day) (Fig. 5 and text). Use phase dominates: whole-life CO2e is 6,700× the manufacturing + disposal CO2e for Al, and 720× for CF-PA6 prepreg. **[FULL TEXT]** — [Cranfield PDF](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content)
- [UNVERIFIED (memory)] Priarone et al. (≈2017–2021) frame the decision as a break-even map. Its axes are the solid-to-cavity ratio or BTF of the machined part versus the mass reduction from redesign. They report that EBM/L-PBF pays off cradle-to-gate only above a certain BTF, and that any mass saving then dominates through the use phase. I could not open the PoliTo manuscript (403) to get the numbers.
- [UNVERIFIED (memory)] Industry cases often quoted: the GE LEAP fuel nozzle (L-PBF CoCr, 20 parts consolidated into 1, about 25 % lighter). The Airbus A350 XWB first L-PBF Ti-6Al-4V pylon or cabin brackets (about 2017). The Airbus/APWorks "Bionic Partition" for the A320 (about 45 % lighter, Autodesk generative design). None of these were opened in this session, and none give manufacture-phase MJ/kg.

### Inferences
- **Decision rule A (manufacture + material, same geometry):** prefer powder-bed AM over machining when the machined BTF is above about 2 (ORNL-based estimate, Q2 inference). Near-net forgings at BTF of about 1.3–2 may beat AM cradle-to-gate (consistent with the Ingarao/Priarone abstract).
- **Decision rule B (with topology optimisation):** once a redesign removes mass, use-phase savings outweigh any manufacturing-phase difference by 2–3 orders of magnitude in ORNL Case 2. So in the eco audit, the manufacture-phase choice is a secondary lever. The headline lever is final mass multiplied by flight distance.
- For the slide: the "manufacture" bar in EduPack will be tiny. The team should state that this is expected, citing ORNL Case 2 (manufacturing ≈0.06 % of life-cycle energy).

### Gaps
- No full-text numeric break-even BTF or mass-reduction threshold from Huang 2016, Ingarao 2018 or Priarone was obtained (all 403).
- Faludi et al. and Kellens et al. 2017 Procedia CIRP were not reached.
- No primary Airbus, GE, APWorks, Materialise or EOS document with energy or CO2 per part was found or read.

---

## Q4. CFRP part processing energy: autoclave vs OOA vs RTM vs thermoplastic press forming

### Takeaway
Process energy for CFRP (excluding fibre) is about 10–40 MJ/kg for curing and moulding. Prepreg production adds about 40 MJ/kg, and an older Ashby value for autoclave moulding is as high as 200 MJ/kg. All of this is small next to carbon fibre itself at about 200–900 MJ/kg. Fibre production, not the consolidation route, dominates the CFRP part's manufacturing footprint.

### Cited Findings
- **Atescan-Yuksek et al. 2024, Table 3** (process embodied energy, MJ/kg). The extracted PDF text glues superscript footnote numbers onto the values; my readings are listed, and the raw text is given in brackets.
  - **Wet compression moulding 11.3** [raw "11.31", footnote 1 = Ecoinvent]
  - **Injection moulding + heating 25.3** [raw "25.31"]
  - **Prepreg production 40** [raw "404", footnote 4 = their ref. 19]
  - **Curing (prepreg) 11.8** [raw "11.84"]
  - **Fabric production 2.6** [raw "2.63"]
  - **Al sheet rolling 9.6** [raw "9.61"]
  - **Al machining 3.0** [raw "3.05", likely footnote 5]
  - **Carbon fibre production 870** [raw "8702", footnote 2]

  Table 2 (material embodied energy, MJ/kg): Al ingot 157.6, carbon fibre 870, PA6 122.5, epoxy 97.4, vinyl ester 120.5. The paper uses 2.98 MJ primary per 1 MJ of electricity (EU grid efficiency about 33 %) (Sect. 3.1). **[FULL TEXT]**; I read the pdftotext extraction, and the footnote-digit interpretation is mine — [Cranfield PDF](https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content)
- **ORNL 2014 Appendix 3a** (Ashby primary shaping, MJ/kg): **autoclave moulding 200**; compression moulding 13.5; spray/lay-up 16; filament winding 3.35. **[FULL TEXT]** — [ORNL PDF](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf). Note the roughly 10× disagreement for autoclave between Ashby (200 MJ/kg) and the Atescan-Yuksek curing value (11.8 MJ/kg). That gap probably comes from different boundaries (whole autoclave run vs per-kg cure energy at full load), but this explanation is not verified.
- A Springer review (2025) gives prepreg manufacturing at about **40 MJ/kg**, **autoclave curing at about 21 MJ/kg**, and carbon fibre at **200–900 MJ/kg**. **[SNIPPET]** — [Springer, Adv. Compos. Hybrid Mater.](https://link.springer.com/article/10.1007/s42114-025-01497-6)
- The whole finished CFRP aerospace component is about **300–500 MJ/kg** (citing Pimenta & Pinho 2011; Liu & Barlow 2017). **[SNIPPET]** — [ScienceDirect S2666789426000711](https://www.sciencedirect.com/science/article/pii/S2666789426000711)
- A vehicle-door study using RTM reports an overall CFRP manufacturing energy intensity of **474 MJ/kg** (fibre included). **[SNIPPET]** — [ResearchGate](https://www.researchgate.net/publication/282853443_The_manufacturing_energy_intensity_of_carbon_fiber_reinforced_polymer_composites_and_its_effect_on_life_cycle_energy_use_for_vehicle_door_lightweighting)
- Toray says its local-heating OOA process gives about **50 % energy saving** versus conventional autoclave fabrication. **[SNIPPET]**; vendor press — [PlasticsToday](https://www.plasticstoday.com/plastics-processing/out-of-autoclave-process-slashes-large-aerospace-component-fabrication-time-by-half)
- ESAFORM 2021 comparative LCA of autoclave, pressure-bag, LP-RTM, HP-RTM and C-RTM (automotive). The snippet says C-RTM cuts manufacturing **time** by 68 % versus autoclave. I saw no energy values. **[SNIPPET]**; HTTP 503 — [ESAFORM 2021](https://popups.uliege.be/esaform21/index.php?id=2542)

### Inferences
- For a CFRP bracket alternative in EduPack: (a) carbon fibre at about 870 MJ/kg dominates; (b) the choice of cure route (autoclave vs OOA vs RTM vs press) shifts the per-kg total by only about 1–5 %, unless the Ashby 200 MJ/kg autoclave value is used. The team should state which value EduPack uses for its composite process rows.
- Thermoplastic (CF-PA6) prepreg had the highest manufacturing CO2e in the Atescan-Yuksek study (5,660 kg vs 2,940 kg for NCF epoxy wet compression). The cause was the prepreg production step. Thermoplastic is therefore not automatically the "green" choice in the manufacture phase.

### Gaps
- No full-text MJ/kg value specifically for **thermoplastic press forming** or stamp forming (e.g. CF-PEEK or CF-PEKK aerospace clips) was found.
- No full-text RTM-vs-autoclave energy per kg for aerospace parts was read. The ESAFORM paper and the TU Delft autoclave thermodynamic model (Composites A, 2023) were not readable.

---

## Q5. Post-processing share (HIP, heat treatment, support removal, machining of AM parts)

### Takeaway
I found no full-text source in this session that quantifies the post-processing share of AM energy for aerospace Ti parts. ORNL Appendix 3b gives generic per-kg intensities that can stand in for these steps, but no HIP value.

### Cited Findings
- ORNL Appendix 3b (Ashby): machining finishing **8 MJ/kg**, grinding **30 MJ/kg**, EDM/wire cutting (used for build-plate removal) **2,750 MJ/kg** (per kg removed). ORNL's AM energy formula includes separate terms for support-structure mass and post-machining mass fractions (`MAM_SP,% × EIAM_SP` and `MAM_PostM,%`, report Sect. AM Calculator, eq. for EE_AM,Intermd). **[FULL TEXT]** — [ORNL PDF](https://info.ornl.gov/sites/publications/Files/Pub215708.pdf)
- The PoliTo/Priarone teaching exercise assumes **20 % support mass** and a **10 % machining allowance** for EBM Ti-6Al-4V. **[SNIPPET]** — [exercise PDF link](https://maestro.prz.edu.pl/fcp/eGBUKOQtTKlQhbx08SlkTUgVKQ2pgTx0DDiA-WAJVQG9WFVZpCFghUHcKVj0GQUw/1180/code_RB0QRPwlQIEdwBEQoGhkfBlAHXTgg/outputs/am-machining_comparison_-_exercise-1.pdf)
- Kellens et al. 2017 Procedia CIRP 61 cover powder production and post-treatment in their AM LCI framework. **[SNIPPET]**, no numbers — [UHasselt record](https://documentserver.uhasselt.be/handle/1942/26484)
- [UNVERIFIED (memory)] HIP of Ti-6Al-4V is a batch process at about 900–920 °C and about 100 MPa for 2–4 h. Its per-kg energy depends strongly on furnace load. Post-processing is often quoted as roughly 5–30 % of AM part production energy. I have no source for this range.

### Inferences
- For the eco audit, model the AM route as follows: powder mass = final mass × (1 + support fraction ~0.2 + allowance ~0.1). Add the EBM or L-PBF SEC on the melted mass. Add finishing machining at about 8 MJ/kg on the removed allowance. Include HIP and heat treatment as a sensitivity case rather than as a sourced point value.

### Gaps
- No sourced HIP MJ/kg value.
- No sourced share of post-processing in total L-PBF or EBM part energy for aerospace Ti.
- Support-removal energy by wire-EDM per part is not quantified in any source I read. The ORNL per-kg value of 2,750 MJ/kg applies to the material removed, and that small mass is unknown.
