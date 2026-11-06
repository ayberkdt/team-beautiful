# Cost inputs for a material × route trade-off of a small aerospace bracket (cost = m_bought·C_mat + m_finished·C_route)

Scope and tag legend. Researched 2026-11-01. This note builds on `tradeoff_methods.md` (Lindemann 2012, Walker 2013) and does not repeat them.

Tags:
- **[FULL]**: I extracted the PDF text myself this session (`pdftotext`) and read the passage.
- **[FULL-fetch]**: the page was fetched in full this session, but the text reached me through the WebFetch extraction model, not raw. Numbers were requested verbatim. Treat this tag as one step weaker than [FULL].
- **[SNIPPET]**: from a search-result summary only.
- **UNVERIFIED (memory)**: from my training memory, not read this session.
- **[derived]**: my arithmetic on the cited numbers.

Currency conversion, used everywhere below: **1 EUR = 1.1537 USD** and **1 EUR = 0.85740 GBP** (so 1 GBP = 1.1663 EUR). These are ECB reference rates of **16 Sep 2026**, read from [Banca d'Italia, cambi_rif_20260916](https://www.bancaditalia.it/compiti/operazioni-cambi/cambio/cambi_rif_20260916) [FULL-fetch]. I found no October 2026 rate. No inflation adjustment is applied: a 2012 € figure stays a 2012 €.

Access failures and things I did not do:
- The ICAO 2006 Morris "cost of weight" deck returned 404, and the 2002 deck host did not resolve.
- No Wohlers or Roland Berger figure was obtained. Both are paywalled, and I did not attempt to bypass them.
- I found no Scalmalloy price.
- Atzeni & Salmi 2012 and Rickenbacher 2013 were not read directly. Their numbers below come via NIST SP 1176.

---

## Q1. Material price per kg

### Takeaway
- **Wrought aerospace Al plate at mill level:** about **€7.5/kg**. This is Constellium Aerospace & Transportation revenue per tonne, 2024 [derived]. It is several times the commodity ingot price; the LME level itself is UNVERIFIED (memory).
- **Ti-6Al-4V sheet/plate:** **$15–50/lb ≈ €29–96/kg** (Dutta & Froes, 2014).
- **Ti-6Al-4V L-PBF powder:** **€130–162/kg** at the cheapest of 11 quoting suppliers in 2021 (Fraunhofer IAPT survey). Coarse EBM-type cuts are **€71–97/kg**.
- **AlSi10Mg powder:** **$78–145/kg** (2021–2024 sources).
- **Scalmalloy:** no public price was found.

### Cited Findings

**Aerospace aluminium plate (mill product, not ingot)**
- **Constellium Q4/FY2024 results release, 20 Feb 2025, Aerospace & Transportation segment table, FY2024:** shipments **209 kt**, revenue **$1,816 M**. FY2023 was 219 kt and $1,868 M. Shipments fell "due to lower shipments of TID rolled products, partially offset by higher shipments of aerospace rolled products". **[FULL-fetch]**, from a reprint of the GlobeNewswire release. — [StockTitan reprint](https://stocktitan.net/news/CSTM/constellium-reports-fourth-quarter-and-full-year-2024-results-38ltwxmy9nvu.html); primary filing is the [Constellium FY2024 10-K](https://www.sec.gov/Archives/edgar/data/1563411/000156341125000005/cstm-20241231.htm), which I did not read.
  - [derived] $1,816 M / 209 kt = **$8.69/kg ≈ €7.53/kg**, averaged over 2024.
  - Caveat: the segment mixes aerospace plate with transportation, industry and defence (TID) products. It is a mill-gate average that includes metal pass-through, not a distributor price for a cut-to-size block.
- **Dutta & Froes (AM&P, Feb 2014), as reproduced in Froes, "Additive Manufacturing of Titanium Alloys", EWI deck, slide 3, table "Cost of Titanium / Comparisons" ($/pound)** **[FULL]**:
  - Aluminium: ingot **1.15 $/lb**, sheet **1.00–5.00 $/lb**.
  - Titanium: ingot **9.07 $/lb**, sheet **15.00–50.00 $/lb**.
  - The row labels are partly garbled in the text layer. I read the rows as ore / metal / ingot / sheet. — [Froes EWI PDF](https://ewi.org/wp-content/uploads/2014/10/06A-Froes-AM-South-Africa.pdf)
  - [derived] Al sheet $2.2–11.0/kg ≈ **€1.9–9.5/kg**. Ti sheet $33–110/kg ≈ **€29–96/kg**. Ti ingot $20/kg ≈ €17/kg.
- **Marketplace figures [SNIPPET, low quality]:**
  - 7075-T7351 plate at "$3.20–3.80" per kg (10–50 mm) and "$3.50–4.20" per kg (50–150 mm). This is an unsourced seller blog. — [Alibaba seller blog 2026](https://seller.alibaba.com/blogs/2026/southeast-asia/aluminum-plate/7075-t7351-stress-relieved-guide-alibaba-b2b)
  - Gr5 Ti plate listings at $13.80–26/kg (50 kg MOQ). — [aggregated search summary](https://breakingac.com/news/2025/sep/03/how-much-is-titanium-currently/)
  - These sit near or below mill averages, so they are probably not certified aerospace stock. **Do not use.**
- **Where Ti part cost goes [SNIPPET, secondary citing Kraft 2004 DOE/ORNL]:** for a component made from plate, 14 % sponge, 34 % mill products, 52 % machining. The same summary gives Ti sheet as 8–50 $/lb contained. — [Kraft 2004 report, record](https://corpora.tika.apache.org/base/docs/govdocs1/047/047504.pdf) (the download failed, so the report itself was not read)

**Ti-6Al-4V powder**
- **Fraunhofer IAPT, "Cost Effective Powders for LBM", Alliance Deep Dive 2021** **[FULL]**:
  - Survey method, §7.3, PDF p. 12 (printed pp. 22–23): quotes from 22 suppliers, 15 responded, 4 outliers removed, 11 analysed. Powder was Ti6Al4V ELI (grade 23), quoted 1 Jun–31 Aug 2021, with "currency conversions … carried out on September 2, 2021".
  - Fig. 13, cheapest provider per segment:

    | Size cut | 100 kg | 1,000 kg |
    |---|---|---|
    | Standard (20–63 µm) | **162.31 /kg** | **130.20 /kg** |
    | Coarse (45–106 µm) | **97.20 /kg** | **71.20 /kg** |

  - The coarse cuts "are also listed as EBM or LMD powders".
  - Ordering 1,000 kg instead of 100 kg cut the standard-cut price by 12 % on average and the coarse-cut price by 19 %. Coarse instead of standard saved 38 % at 100 kg and 44 % at 1,000 kg on average.
  - Abstract (printed p. 3): standard powder has "High costs (180 /kg)".
  - PDF p. 6: "One kilogram of Ti6Al4V costs around three to five times more than a typical AM aluminum alloy such as AlSi10Mg."
  - Currency caveat: the € symbol is lost in the text layer. EUR is inferred from the Fraunhofer source and the stated currency conversion.
  - The averages (mean values) are shown only graphically in Fig. 12 and were not readable.
  - — [IAPT PDF](https://iapt.fraunhofer.de/content/dam/iapt/documents/Alliance/alliance-event-oktober-2021/2021-10-28_AllianceDeepDive_Cost%20Effective%20Powders%20for%20LBM.pdf)
- **Simpson (Barnes Global Advisors), "Plotting a Pathway to Profitable AM", Additive Manufacturing Media, 11 May 2021** **[FULL-fetch]**. Powder inputs: **Ti-6Al-4V $360/kg**, **AlSi10Mg $78/kg**, 17-4PH $91/kg, In718 $120/kg. — [AM Media](https://www.additivemanufacturing.media/articles/plotting-a-pathway-to-profitable-am)
- **Market-research average [SNIPPET]:** "USD 142.5 per kilogram" for Ti alloy AM powder in 2024. The sourcing is opaque. — [Intel Market Research](https://www.intelmarketresearch.com/titanium-alloy-powder-for-additive-market-56608)

**AlSi10Mg powder**
- **Depboylu, Popa, Oyama, Ono, "Towards affordable aluminum additive manufacturing…", SFF Symp. 2024, p. 1 (Introduction)** **[FULL]**:
  - "the cost of NExP-1 powder is set to approximately 85 USD/kg, while prices for standard AlSi10Mg feedstock of 30-60 µm particle diameters from North American suppliers can range between 135-145 USD/kg."
  - — [UT Austin SFF archive PDF](https://utw10945.utweb.utexas.edu/sites/default/files/2024/58%20Towards%20Affordable%20Aluminum%20Additive%20Manufactur.pdf)
  - [derived] €117–126/kg standard, €74/kg NExP-1.
- Simpson 2021: **$78/kg ≈ €68/kg** [FULL-fetch, above].

**Scalmalloy powder**
- No per-kg price was found. Carpenter offers it on request-for-quote. BAM sells a certified-reference AlMgSc powder at €267 for an unstated quantity [SNIPPET]. — [Carpenter](https://carpentertechnology.com/alloy-finder/scalmalloy); [BAM webshop](https://webshop.bam.de/webshop_en/bam-m319.html)

### Inferences
- **Ingot vs plate:** the LME is a primary-ingot commodity price, about $2.4–2.6/kg in 2024–25 (UNVERIFIED (memory)). Constellium's A&T average (~$8.7/kg, 2024) is roughly 3–3.5× that. A small cut-to-size 7075-T7351 block bought from a distributor will cost more than the mill average. That distributor premium is UNVERIFIED (memory).
- For a student model, use ~€10/kg for Al plate as the base and swing it to €20/kg. Al material cost is small next to route cost anyway; check this with your BTF.
- **Two internal-consistency checks on the powder figures:**
  - IAPT's "Ti is 3–5× AlSi10Mg" plus Ti at 130–162 €/kg implies AlSi10Mg ≈ €26–54/kg [derived]. That is below Depboylu's North American $135–145/kg. Regional and lot-size spread is large, so carry a wide range.
  - Simpson's $360/kg for Ti-6Al-4V is about 2× the IAPT cheapest-supplier figure. Simpson reflects a US OEM-branded list price; IAPT reflects the cheapest of 11 quotes.

### Gaps
- No aerospace distributor price list for 7075-T7351 or 2024-T351 plate was found publicly.
- The LME price was not read this session.
- No Wohlers or AMPower powder-price table was read.
- No Scalmalloy price was found. UNVERIFIED (memory): Sc-bearing powder carries a large premium over AlSi10Mg; treat about 2–3× as a placeholder only.

---

## Q2. L-PBF part cost per kg / per cm³ and its trend

### Takeaway
Reported L-PBF part costs span about an order of magnitude:
- **Lower bound, AMPOWER in-house metal AM:** about **€250–300/kg** for aluminium (≈0.80 €/cm³) and about €165/kg for stainless steel, around 2022–23.
- **Upper bound, Simpson 2021 single-laser EOS M290 model:** about **$1,300–2,300/kg** all-in.
- Machine time dominates: 45–78 % of cost in Lindemann's variants (NIST). Post-processing is about 8 % (Lindemann via NIST) to 26 % (Simpson's industry average).
- Trend: AMPOWER expects aluminium AM to fall to **€100–200/kg by 2030**. This is a forecast, not data.

### Cited Findings
- **Thomas & Gilbert, NIST SP 1176 "Costs and Cost Effectiveness of Additive Manufacturing", Dec 2014, DOI [10.6028/NIST.SP.1176](https://doi.org/10.6028/NIST.SP.1176)** **[FULL]**. Read from the [NIST PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1176.pdf); page numbers below are printed page numbers.
  - **pp. 16–17, Fig. 3.3:** re-analysis of Lindemann 2012 (316L, ~190 parts). Varying build rate (6.3/12/20 cm³/h), utilisation (4,500/6,000/7,800 h/yr), material (40/89/600 /kg) and investment (200/320/500 k):
    - "On average, the machine costs accounted for 62.9 %". Machine cost was the largest item "in all but one case, where material costs were increased to 600 /kg."
    - Materials averaged 18.0 %.
    - "Post processing, preparation, oven heating, and building process fix were approximately 8.4 %, 5.4 %, 3.3 %, and 1.9 %".
    - At 20 cm³/h, the machine share drops to 47 % and material rises to 23 % (Fig. 3.3 panel).
  - **p. 20:** Hopkinson & Dickens 2003: machine costs "ranged from 23 % to 75 % of a metal part". Lindemann 2012: "45 % to 78 %". Machines cost "$0.1 million typically for polymer systems and $1.0 million typically for metal systems".
  - **p. 15 and Table 4.2, p. 32:** Atzeni & Salmi, aluminium-alloy landing-gear part for a 1:5 scale Piaggio P180 model.
    - Laser powder-bed route (NIST calls it "selective laser sintering") total **526.31 per part**: material 25.81, pre-processing 8.00, processing 472.50, post-processing 20.00.
    - HPDC: **21.29 + 21,000/N**, with material 2.59.
    - Break-even at **42 parts** (Fig. 4.4).
    - Processing alone is ~90 % of the AM part cost [derived: 472.50/526.31].
    - Currency is € per NIST's convention for this study (the symbol is lost in the text layer).
  - **p. 33:** Allen 2006 (aero-engine Ti parts) concluded AM is cost-effective "where the buy/fly ratio is 12-1". AM is attractive for high-BTF, complex, high-material-cost, slow-to-machine parts.
- **AMPOWER, "Additive Manufacturing Part Cost and Pricing" (insight page, undated; image uploads dated 2023/09)** **[FULL-fetch]**:
  - "The cost structure of in-house metal Additive Manufacturing commences at 0.80 EUR/cm³ for aluminum or 298 EUR/kg and 1.29 EUR/cm³ for stainless steel alloys, equating to 165 EUR/kg."
  - The page gives no breakdown, no machine rate and no technology split.
  - — [AMPOWER insight](https://ampower.eu/insights/additive-manufacturing-part-cost-and-pricing/)
- **AMPOWER, "Addressable market metal AM" study page (undated; uploads dated 2022/09)** **[FULL-fetch]**:
  - "In aluminum AM applications, component production costs are approximately 250 to 300 EUR per kg."
  - With productivity improvements by 2030, "a cost reduction to 100-200 EUR per kg is anticipated."
  - — [AMPOWER study](https://ampower.eu/studies/addressable-market-metal-am/)
- **Simpson 2021 (EOS M290, single laser)** **[FULL-fetch]**:
  - Inputs: machine "$50/hr (fully burdened)"; In718 build rate 4.2 mm³/s with an 80 % decrement, giving 98.58 g/h.
  - In718: printing $0.51/g; multiplier 1.689 = 1/0.592; total **$1,060/kg**.
  - Industry-average shares: printing (machine + material) **59.2 %**, pre-processing **14.4 %**, post-processing **26.4 %**.
  - Totals for other alloys: **Ti-6Al-4V $1,347/kg**, **AlSi10Mg $2,285/kg**, **17-4PH $1,287/kg**. Their build rates are not printed.
  - — [AM Media](https://www.additivemanufacturing.media/articles/plotting-a-pathway-to-profitable-am)
- Lindemann-derived machine-only figures (≈540 €/kg deposited, base; ≈70 €/kg, optimised; 2012) are already in `tradeoff_methods.md` Q5.

### Inferences
- **Reverse-engineering Simpson [derived]:** $50/h ÷ 98.58 g/h = $0.507/g, so the "printing $0.51/g" is machine-only. ($507 + $120 powder)/0.592 = $1,059 ✓.
  - Applying the same structure, machine cost per kg is: Ti-6Al-4V 1,347×0.592 − 360 ≈ **$437/kg**; AlSi10Mg 2,285×0.592 − 78 ≈ **$1,275/kg**. The AlSi10Mg figure is high because Al is light and is built at 30 µm layers.
  - Route cost excluding powder ≈ total − powder price: **AlSi10Mg ≈ $2,207/kg (€1,913)**, **Ti-6Al-4V ≈ $987/kg (€855)**.
- **Avoid double counting in your model.** C_route must exclude powder if the powder is already in m_bought·C_mat.
  - Simpson's and AMPOWER's figures are totals that include material. Whether AMPOWER includes powder is not stated; I assume it does.
  - Excluding powder from AMPOWER [derived; powder ≈ €80/kg Al, ≈ €25/kg steel, assumed]:
    - Al: 0.80 € − 80 €/kg × 2.68 g/cm³ ≈ 0.59 €/cm³ ≈ **€220/kg**.
    - Stainless: 1.29 € − ~0.2 € ≈ 1.1 €/cm³.
    - Scaling the stainless figure per volume to Ti (4.43 g/cm³) gives ≈ **€250/kg** of Ti.
  - Densities 2.68 / 4.43 / 7.9 g/cm³ are UNVERIFIED (memory). The 2.68 value reproduces AMPOWER's own 0.80 €/cm³ ↔ 298 €/kg.
- **Per-kg cost hides geometry.** L-PBF cost scales with volume and build height, not mass. Al is cheaper per cm³ but dearer per kg than Ti. If the bracket volume is known, prefer €/cm³.
- **Trend [derived]:**
  - NIST/Lindemann 2012: ~540 €/kg machine-only for steel at 6.3 cm³/h.
  - Simpson 2021: ~$400–1,300/kg machine-only for a single-laser machine.
  - AMPOWER 2022–23: €165–300/kg all-in.
  - AMPOWER 2030 forecast: €100–200/kg.
  - So the direction is down. The sources are not like-for-like (machine generation, multi-laser vs single, in-house vs bought), so no rate of decline should be quoted.

### Gaps
- No primary 2020+ machine-hour rate in €/h for multi-laser L-PBF was found.
- No Wohlers or Roland Berger cost-per-part series was read.
- I found no aerospace-qualified (HIP, CT inspection) L-PBF cost premium.

---

## Q3. CNC machining cost (shop rate, material removal rate)

### Takeaway
Only order-of-magnitude, weakly sourced shop rates were found: 5-axis about **$100–200+/h** and 3-axis about $50–80/h (US, vendor blogs [SNIPPET]). Combined with Walker's removal rates [FULL, earlier note], the route cost of a high-BTF Ti part is **~€10²–10³ per kg finished**, and Al is several times lower [derived].

### Cited Findings
- **Shop rates [SNIPPET, vendor sources]:**
  - "5-axis machining running $100–$200+ per hour", with a 3-axis milling table at "$50–$80/h".
  - "a feature that takes 5 minutes to machine in aluminum may take 25–40 minutes in titanium".
  - Aerospace work carries a traceability/QMS premium.
  - — [Fabcon 5-axis cost article](https://fabcon.com/articles/?p=132); [mfgrobots aerospace CNC](https://www.mfgrobots.com/Article/mfg/it/54225.html)
- **Cross-check rate:** Simpson's fully burdened L-PBF machine rate of "$50/hr" [FULL-fetch], and Lindemann's ≈27 /h machine-only (`tradeoff_methods.md`).
- **Titanium cost structure:**
  - Walker 2013 (in the earlier note): material 43.6 %, machining 27 %, cutters 10.4 %; maximum MRR 3–35 in³/min (29–336 lb/h); cutters ≈ $4/kg removed [derived there].
  - Kraft via secondary [SNIPPET]: machining 52 % of a plate-made Ti component.
- **Buy-to-fly context:**
  - Martina (Cranfield), WAAM slides: "Average buy-to-fly ratio for airframes is 5" (early slide, slide number not pinned) **[FULL]**.
  - Slide 8 **[FULL]**: WAAM "Specific deposition cost (dependant upon BTF): Ti: £300/kg, Al: £20/kg, Mild steel: £25/kg". WAAM BTF "typical 1.5, always < 2"; build rates 0.5–4 kg/h (Ti ~1 kg/h).
  - No date is visible on the deck.
  - — [Martina PDF](https://conferences.ncl.ac.uk/additivemx/ponencias/Filomeno_Martina_Mexico_short.pdf)
  - NIST p. 33 [FULL]: AM break-even at BTF ≈ 12:1 for aero-engine Ti (Allen 2006).

### Inferences (template [derived], assumptions flagged)
- Machining cost per kg finished: **C_route,mach ≈ (BTF − 1) × (R / MRR_eff + c_cut)**, with MRR_eff in kg removed per hour. Add setup, programming and inspection per batch separately.
- **Ti example:**
  - R = €130/h (≈ $150/h, the middle of the snippet band). MRR_eff = 2–13 kg/h: 13 kg/h is Walker's light-machine maximum; 2 kg/h is an assumed realistic average for small-part roughing plus finishing (UNVERIFIED).
  - c_cut ≈ €3.5/kg (Walker-derived).
  - At BTF 10 this gives 9 × (10–65 + 3.5) ≈ **€120–620/kg finished**.
- **Al example:**
  - MRR_eff 5–30 kg/h (UNVERIFIED (memory); Al machines several times faster) and negligible cutter cost.
  - At BTF 10 this gives 9 × (4–26) ≈ **€40–240/kg finished**.
- For a *small* bracket, setup and fixturing per part can exceed the per-kg terms. Show a batch-size sensitivity.

### Gaps
- No primary or institutional shop-rate survey was read: no German Maschinenstundensatz benchmark, no EU aerospace supplier rate.
- No published average (not maximum) MRR was found for aerospace Ti or Al pocketing.

---

## Q4. Aircraft value of weight saving per kg (to compare with Ashby α)

### Takeaway
A fuel-only bottom-up estimate gives **€36–181 per kg per year** at 2025–2026 jet fuel prices. Over 25 years this is **≈ €420–2,100/kg discounted** at 7 %, or €900–4,500/kg undiscounted [derived]. The low discounted end overlaps Ashby (100–500 £/kg ≈ €117–583/kg) and NRC 2003 ($200/lb ≈ €382/kg). The high end shows that the 2026 fuel spike (IATA forecast $152/bbl) roughly doubles α.

### Cited Findings
- **IATA Fuel Fact Sheet, "Updated: 6/2026", p. 1** **[FULL]**:
  - After the late-February 2026 Strait of Hormuz closure, "jet fuel prices rose above USD 200 per barrel by mid-April".
  - "we forecast an average jet fuel price of USD 152 per barrel in 2026--almost 70% higher than in 2025."
  - The SAF price assumption is "USD 2,872 per tonne (USD 374 per barrel)".
  - — [IATA fuel fact sheet](https://www.iata.org/en/iata-repository/pressroom/fact-sheets/fact-sheet-fuel)
  - [derived] The 2025 average is ≈ 152/1.7 ≈ **$89/bbl**. This matches IATA's June-2025 forecast of ~$86/bbl [SNIPPET, S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/agriculture/060225-airlines-see-relief-with-86-jet-fuel-saf-costs-hinder-sustainability-iata-chief).
  - IATA's own SAF pair implies 2,872/374 = **7.68 bbl/t**, i.e. ≈ 130 kg/bbl [derived]. Using 0.80 kg/L × 159 L/bbl (UNVERIFIED (memory)) instead gives 127 kg/bbl.
  - Jet fuel per kg [derived]: **$0.70/kg (2025)** and **$1.20/kg (2026 forecast)**, i.e. €0.61 and €1.04.
- **Marginal fuel per kg carried:**
  - Rule of thumb "3.5 % per flight hour" (OpenAirlines), i.e. 0.035 kg fuel per kg per hour [SNIPPET]. An ICAO 2006 workshop deck (Morris) gives "3–4 %" and assumes 5,000 h/yr and $740/t [SNIPPET; the deck itself returned 404]. — [OpenAirlines blog](https://blog.openairlines.com/how-to-use-the-cost-of-weight-to-be-more-fuel-efficient); [ICAO Morris 2006](https://www.icao.int:443/Meetings/EnvironmentalWorkshops/Documents/ICAO-TransportCanada-2006/Morris.pdf)
  - Steinegger (ZHAW 2017): 0.02–0.03 kg fuel per kg per 1,000 km [SNIPPET, in the earlier note]. That is ≈ 0.016–0.024 kg/kg/h at ~800 km/h; the cruise speed is UNVERIFIED (memory).
- **Prior anchors** (from `tradeoff_methods.md`, not repeated in detail): NRC 2003 "$200 per pound" over a 100,000 h fuselage life [FULL there]; Ashby 2000 Table 3, civil aircraft 100–500 £/kg [FULL there].

### Inferences [derived]
- Per kg per year = (0.02–0.035 kg fuel/kg/h) × (3,000–5,000 h/yr) × ($0.70–1.20/kg) = **$42–209/kg/yr ≈ €36–181/kg/yr**.
  - The 5,000 h/yr upper bound is from the Morris snippet. The 3,000 h lower bound is UNVERIFIED (memory) for a short-haul narrowbody.
- Over a 25-year life: undiscounted ≈ €900–4,500/kg. Discounted at 7 % (annuity factor 11.65; the rate is an assumption) ≈ **€420–2,110/kg**.
- NRC's $441/kg over 100,000 h implies $0.0044/kg/h. That is about 3–6× below the 2025–26 bottom-up figure ($0.014–0.042/kg/h), which is consistent with 2003-era fuel prices. **α scales linearly with fuel price, so state the fuel year.**
- These are fuel-only values. Payload-revenue α (Ashby's basis) and CO2/ETS cost would add to them. Keep CO2 separate, per `tradeoff_methods.md` Q4.

### Gaps
- No airline or OEM primary source stating "$ per kg per year" was read in full. The Morris deck could not be retrieved.
- Utilisation hours by aircraft class are not sourced here.

---

## Recommended inputs (EUR/kg; 1 EUR = 1.1537 USD = 0.8574 GBP, ECB 16 Sep 2026; nominal, not inflation-adjusted)

| Input | Value | Low | High | Basis (tag) |
|---|---|---|---|---|
| Al 7075-T7351 / 2024-T351 plate, C_mat | 10 | 7.5 | 20 | Low: Constellium A&T 2024 mill average [FULL-fetch → derived]. Value and high: distributor premium, UNVERIFIED (memory). Not LME ingot. |
| Ti-6Al-4V plate/bar, C_mat | 50 | 29 | 96 | Dutta & Froes 2014, $15–50/lb sheet [FULL] |
| AlSi10Mg powder (L-PBF) | 80 | 40 | 126 | Simpson 2021 $78 [FULL-fetch]; Depboylu 2024 $135–145 [FULL]; low from IAPT ratio [derived] |
| Scalmalloy powder | 200 | 120 | 400 | **UNVERIFIED (memory) placeholder**; no source found |
| Ti-6Al-4V powder, L-PBF (15–63 µm) | 180 | 130 | 312 | IAPT 2021 cheapest 130–162, "180" headline [FULL]; Simpson 2021 $360 [FULL-fetch] |
| Ti-6Al-4V powder, EBM (45–106 µm) | 110 | 71 | 180 | IAPT 2021 coarse cheapest 71–97 [FULL]; high UNVERIFIED |
| L-PBF Al route, C_route (excl. powder, per kg finished) | 500 | 220 | 1,910 | AMPOWER ~2023 [FULL-fetch → derived]; Simpson 2021 [FULL-fetch → derived] |
| L-PBF Ti route, C_route (excl. powder) | 500 | 250 | 855 | AMPOWER stainless per-cm³ scaled [derived]; Simpson 2021 [derived] |
| CNC Ti route, C_route (BTF ≈ 10) | 300 | 120 | 620 | Walker MRR [FULL, earlier note] + snippet shop rate [SNIPPET] → [derived] |
| CNC Al route, C_route (BTF ≈ 10) | 100 | 40 | 240 | snippet shop rate + MRR UNVERIFIED → [derived] |
| α, civil-aircraft value of mass saved (per kg, life) | 500 | 120 | 2,100 | Ashby 100–500 £/kg [FULL]; NRC €382 [FULL]; fuel bottom-up NPV €420–2,110 [derived] |

Use notes:
- C_route values exclude feedstock, so do not add powder twice.
- Machining C_route scales with (BTF − 1). Recompute it for your BTF instead of using the table value blindly.
- L-PBF figures are per kg finished but are really volume- and height-driven.
- The weakest inputs are Scalmalloy, Al plate distributor price and CNC shop rate. Put them on the tornado first.
