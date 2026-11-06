# Use-phase and end-of-life effect of aircraft mass reduction; CFRP vs aluminium LCA payback

Compiled 2026-11-01. Source-status legend used on every line:
- **[FULL TEXT]**: I extracted the PDF text in this session and read the cited passage myself.
- **[PAGE]**: I fetched the web page in this session (a model summarised it, so the wording is not verbatim).
- **[SNIPPET]**: Seen only in a search-engine snippet or an abstract-level summary. Not verified.
- **UNVERIFIED (memory)**: From my own background knowledge. Not sourced here.

Scope note: I made about 20 tool calls. I read four primary documents in full text: Scelsi 2011, the Ansys/Granta Eco Audit white paper (2021), Steinegger/ZHAW 2017, and the Airbus 2022 end-of-life page (fetched). Timmis 2015 (Springer, paywalled, and the Loughborough repository returned 403) was **not** read in full.

---

## Q1. Published "fuel saved per kg" factors by aircraft class, and the lifetime assumptions behind them

### Takeaway
The only per-kg factor I verified in a primary text is Steinegger (ZHAW, 2017, not peer-reviewed, simBrief flight-plan simulations). It gives a marginal fuel burn of about 0.02–0.04 kg fuel per kg of mass per 1,000 km for the A320, A330 and A380, or 0.05–0.45 kg fuel per kg per trip depending on type and distance. The common "0.03–0.05 kg fuel per kg per flight hour" rule appears only in secondary or snippet sources. I found **no** verified per-kg factor for regional turboprops, business jets or helicopters.

### Cited Findings
- **Steinegger 2017, headline rate [FULL TEXT, p.1 abstract]:** "a reduction in weight by one kg saves ~ 0.02 to 0.03 kg of fuel per 1'000 km". The paper also says that carrying 1 kg takes on average about 0.2 kg fuel per 1,000 km (total, not marginal). Method: operational flight plans computed with simBrief; FL360, no wind; no taxi, alternate or contingency fuel; 105 kg per passenger; aircraft A320-200, A330-300, A380-800. Source: R. Steinegger, "Fuel Economy as Function of Weight and Distance", ZHAW, v1.0, 2 Dec 2017 — https://digitalcollection.zhaw.ch/bitstream/11475/1896/2/Steinegger_Fuel_Economy_for_Aircraft_Operation_as_a_Function_of_Weight_and_Distance_v1-0.pdf
- **Steinegger 2017, by type [FULL TEXT, p.4, fig. 7]:** the marginal fuel burn (MFB) as a function of payload "differs by the factor 2": **2.0 to 4.1 kg fuel / 100 kg · 1,000 km**, which is 0.020–0.041 kg/kg/1,000 km. Fig. 7d values: A322 2.8, A333 2.0, A388 4.1 (kg fuel / 100 kg · 1,000 km). Same URL.
- **Steinegger 2017, per trip [FULL TEXT, p.11, fig. 15]:** MFB in kg fuel per kg payload for each trip. Caveat: the table extracted poorly, so the column alignment is my reading.

  | Aircraft | 2,000 km | 4,000 km | 5,000 km | 7,000 km | 12,000 km |
  |---|---|---|---|---|---|
  | A322 | 0.07 | 0.12 | 0.16 | – | – |
  | A333 | 0.05 | 0.08 | 0.11 | 0.18 | – |
  | A388 | 0.10 | 0.17 | 0.18 | 0.26 | 0.45 |

  The conclusion (p.10) notes that "the fuel savings will be on every flight during the lifetime of the aircraft". The paper itself gives **no** lifetime (years or cycles) assumption. Same URL.
- **Scelsi et al. 2011, lifetime assumption [FULL TEXT, p.213, §3.2]:** civil aircraft "life time of 30 years and a daily range of 14 000 km", giving about **150 million km** over its life. Cruise speed is taken as 750 km/h for freight. Fuel is assumed proportional to total weight (BADA thrust-specific fuel model, constant T/W and cruise speed). Source: Scelsi L., Bonner M., Hodzic A., Soutis C., Wilson C., Scaife R., Ridgway K., eXPRESS Polymer Letters 5(3) 209–217 (2011), DOI 10.3144/expresspolymlett.2011.20 (the DOI is my UNVERIFIED (memory) reconstruction; the pages and volume are verified). PDF: https://real-j.mtak.hu/28365/5/EPL_2011_3_0228-0302.pdf (pp. 209–217 of the issue PDF).
- **Per-flight-hour rule of thumb [SNIPPET]:** "approximately 0.03–0.05 kg of fuel per flight hour" per kg removed. The same source estimates that 40 kg removed from a narrow-body at 3,000 h/yr saves about $10–15k/yr. This is a secondary blog, so low quality — https://planefyi.com/guides/sustainable-aviation/aircraft-weight-reduction/
- **ICAO 2002 workshop deck, K. Morris (BA) [SNIPPET]:** additional fuel ≈ "3-4% of weight increase x hours flown" (example: 500 kg for 10 h gives 150–200 kg fuel) — https://www2023.icao.int/Meetings/EnvironmentalWorkshops/Documents/2002-Workshop-OperationalMeasures-for-FuelEmissionsReduction/kevin_morris.pdf
- **ICAO/Transport Canada 2006 [SNIPPET]:** a 500 kg increase on a 1.5 h flight costs about 30–50 kg of extra fuel — https://www.icao.int:443/Meetings/EnvironmentalWorkshops/Documents/ICAO-TransportCanada-2006/Viscotchi.pdf
- **Patent text [SNIPPET]:** 0.02–0.04 kg fuel per kg per hour, and with an assumed 100,000 h life, about 4 t fuel per kg. This is an advocacy document — https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12138894
- **Léonard & Nylander via a secondary summary [SNIPPET]:** a 100 kg lighter aircraft saves 124–129 t of fuel over its lifetime (about 1.2–1.3 t/kg). I did not see the original — https://simpliflying.com/green/why-every-kilogram-counts-expliseat
- **Diehl, single-aisle (A321) [SNIPPET]:** at 3,600 operating h/yr, one product's weight saving saves about 1.1 t fuel and 3.3 t CO2 per aircraft per year. The saved mass was not given, so this cannot be turned into a per-kg rate — https://microsite.diehl.com/aviation-highlights/en/eco-efficiency/16g-partition/
- **Airline programmes [SNIPPET]:** easyJet's lighter paint is −27 kg per aircraft, with a fleet saving of 1,296 t fuel/yr by 2030 (https://onemileatatime.com/news/easyjet-lighter-paint-reduce-fuel-burn/). Lufthansa found about 100 kg per long-haul A340-300 and a group saving of >1,000 t kerosene/yr (https://lufthansagroup.com/media/downloads/en/responsibility/balance-2014-epaper/page59.html, which returned 403 to me).
- **Researchgate figure "Influence of weight reduction over lifetime fuel consumption for different aircraft sizes" [SNIPPET, title only]:** may be useful but I did not open it — https://www.researchgate.net/figure/nfluence-of-weight-reduction-over-lifetime-fuel-consumption-for-different-aircraft-sizes_fig1_342112857

### Inferences
- The flight-hour and per-km rules agree within a factor of ~2. My conversion: at about 800 km/h block-average, 0.02–0.04 kg/kg/1,000 km comes to about 0.016–0.032 kg/kg/h, which is below the 0.03–0.05 kg/kg/h blog rule. The blog rule probably includes climb, or fuel-for-fuel at longer stages. Treat the range as **0.02–0.05 kg fuel per kg per block hour** for jet airliners. This is an inference.
- A lifetime factor follows as (per-hour factor) × (block hours per year) × (years). Illustrative only (my arithmetic): a narrow-body at 3,000 h/yr for 25 yr with 0.03 kg/kg/h gives about 2.3 t fuel per kg, or about 7 t CO2 per kg using 3.16 kg CO2/kg fuel (UNVERIFIED (memory); this is the commonly used ICAO/CORSIA factor). The utilisation (3,000 h/yr) and life (25 yr) are UNVERIFIED (memory) typical values, not taken from a source read here. The 3,000 h/yr matches the planefyi snippet assumption. Scelsi's 30 yr × 14,000 km/day implies about 18,700 h/yr at 750 km/h, which is physically impossible (more than 8,760 h/yr). So Scelsi's 150 million km lifetime is an **overstatement**. Use it only to reproduce their result.
- Steinegger's per-trip table shows the sensitivity grows non-linearly with stage length (fuel-for-fuel effect). A wide-body on long sectors therefore gives more fuel per kg per trip, but not necessarily per hour.

### Gaps
- No verified primary per-kg factor for **regional turboprop, business jet or helicopter**. ICCT, IATA, Airbus and Boeing per-kg rules were not found in primary form in this session.
- No primary source read for typical lifetime utilisation (block hours/yr, cycles, years) by class.
- Léonard & Nylander was not located in the original.

---

## Q2. Physics: Breguet mass-fuel sensitivity vs mass-induced-drag corrections

### Takeaway
I found no paper in this session that explicitly compares the Breguet f/(1−f) sensitivity with a "mass-induced drag" correction. The verified sources use either an empirical marginal fuel burn (Steinegger) or a "fuel proportional to total weight" assumption (Scelsi).

### Cited Findings
- **Scelsi 2011 [FULL TEXT, pp.212–213]:** uses BADA nominal fuel flow = η·T, with thrust-specific coefficients independent of mass. "If, as a first approximation, the thrust-to-weight ratio … and the cruise speed are assumed to be mantained constant … fuel consumption can be assumed to be proportional to the total weight of the aircraft." Transport is modelled as an LCA freight t·km process. URL as in Q1.
- **Steinegger 2017 [FULL TEXT, p.11]:** "The 'Fuel for fuel' effect is verified by empirical analysis. As it turns out, it is relatively small compared to the effects of operating a flight outside of optimum range." The paper's p.2 discusses angle of attack, with lift-induced drag rising with weight. The a.o.a. change from zero to maximum payload is about 1° (fig. 4). URL as in Q1.

### Inferences
- The Breguet derivation is my own derivation, not taken from a source read here. Range R = (V·L/D / (g·TSFC))·ln(W0/W1). Holding R and L/D constant, an added mass Δm carried for the whole mission changes fuel by ΔF ≈ Δm·(e^{R/k} − 1) = Δm·f/(1−f), where f = fuel fraction burned. This assumes L/D stays constant, i.e. the aircraft flies at its optimum CL by climbing, so the induced-drag increase is absorbed. If altitude or speed is fixed, the induced drag (∝ W²) makes the real sensitivity higher. This is the "mass-induced drag" correction direction.
- Sanity check (my arithmetic): f ≈ 0.10–0.15 for a 4,000–5,000 km narrow-body sector (UNVERIFIED (memory)) gives f/(1−f) ≈ 0.11–0.18 kg/kg per trip. That is consistent with Steinegger's 0.12–0.16 for the A322 at 4,000–5,000 km. So Breguet and the empirical data agree to first order for whole-mission mass.

### Gaps
- No primary paper comparing Breguet sensitivity to mass-induced-drag corrections was retrieved. Candidates to check include Torenbeek's "Advanced Aircraft Design" and NASA/ICCT cost-of-weight papers (UNVERIFIED (memory)).

---

## Q3. CFRP vs aluminium structure LCA: payback distances/times and CO2 totals

### Takeaway
Scelsi 2011 (read in full) is the cleanest quantitative payback source. A 10 kg Al-2024 panel replaced by an 8 kg CFRP panel (−20 % mass) breaks even after **45,000 km / 60 h** (climate change), **85,000 km / 113 h** (fossil fuel) or **70,000 km / 93 h** (Eco-indicator 99 single score). A steel tube replaced by CFRP breaks even after 3,600 km / 4.8 h of air transport. Timmis 2015 (B787-type all-composite LCA) concludes that composites give a lifetime CO2 benefit and could deliver 20–25 % of industry CO2 targets, but I saw this only at abstract level.

### Cited Findings
- **Scelsi 2011, study basis [FULL TEXT, p.211]:** SimaPro 7.1, Ecoinvent v2.0, Eco-indicator 99 (E) V2.05; UK grid mix. Tooling, transport and buildings are excluded. Mass basis: CFRP 20 % and GLARE 10 % lighter than Al, so the Al-2024 panel is 10 kg, CFRP 8 kg and GLARE 9 kg. CFRP is 65 % carbon fibre / 35 % epoxy by weight, autoclave-cured at about 68 kWh per panel. Al is "assumed … 100% recyclable" with the recycling saving "counted as positive emissions" (a substitution credit). CFRP and GLARE are landfilled ("no commercial recycling route available"). URL as in Q1.
- **Scelsi 2011, Table 1 [FULL TEXT, p.213], break-even vs Al-2024 panel:**

  | Impact category | CFRP distance (km) | CFRP time (h) | GLARE distance (km) | GLARE time (h) |
  |---|---|---|---|---|
  | Single score | 70,000 | 93 | 240,000 | 320 |
  | Fossil fuel | 85,000 | 113 | 105,000 | 140 |
  | Climate change | 45,000 | 60 | 120,000 | 160 |

  Over the full life, "Al-2024 is more environmentally harmful than CFRP and GLARE", and fossil fuel use dominates the total impact (p.213, fig. 2). Absolute CO2 totals are given only as Eco-indicator points in figures, not as kg CO2e.
- **Scelsi 2011, tube case study [FULL TEXT, pp.214–215, Table 2]:** a real AMRC/Boeing Sheffield component, a CFRP tube (about 660 mm long, 670 mm inner diameter, 10 mm wall; AFP 25 kW × 230 min plus autoclave 20 kW × 240 min) replacing a 5 mm-wall steel tube. Break-even single score: **air 3,600 km / 4.8 h**, road 13,600 km / 170 h, marine 373,000 km / 9,325 h. Incineration and landfill of CFRP had "approximately the same impact" in the model (p.214).
- **Timmis et al. 2015 [SNIPPET/abstract-level]:** "Environmental impact assessment of aviation emission reduction through the implementation of composite materials", Int J LCA 20(2):233–243, DOI 10.1007/s11367-014-0824-0. It is an LCA of an all-composite airframe based on the Boeing 787 Dreamliner using Eco-indicator 99. Reported findings: a lower single-score impact despite higher manufacturing impact, significant lifetime CO2 benefit, and the global shift to composites "could contribute 20–25 %" of industry CO2 reduction targets. I did **not** read the full text; the use-phase assumptions and payback numbers are unknown to me. Sources: https://dx.doi.org/10.1007%2Fs11367-014-0824-0 ; https://dspace.lboro.ac.uk/dspace-jspui/handle/2134/21192 (403 for me) ; https://acmanet.org/?p=9055 ; https://www.compositestoday.com/2014/12/new-research-shows-lighter-composite-planes-future/
- **Vidal et al. 2018 [SNIPPET]:** the paper I could find is "Life Cycle Assessment of Novel Aircraft Interior Panels Made from Renewable or Recyclable Polymers with Natural Fiber Reinforcements and Non-Halogenated Flame Retardants", J. Industrial Ecology 22(1):132–144, DOI 10.1111/jiec.12544. It covers **interior panels**, not CFRP fuselage — https://ideas.repec.org/a/bla/inecol/v22y2018i1p132-144.html ; https://repositori.uji.es/xmlui/handle/10234/166550
- **2023 Int J LCA framework paper [SNIPPET]:** critiques earlier aviation CFRP LCAs, including Timmis 2015, for "single impact category analysis" and uncommunicated data uncertainty. "A novel life cycle assessment and life cycle costing framework for carbon fibre-reinforced composite materials in the aviation industry" — https://link.springer.com/article/10.1007/s11367-023-02164-y ; open access: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10043863/ (not read in full in this session)
- **2024 comparative Al vs CFRP LCA [SNIPPET]:** even with a 1:1 buy-to-fly ratio and 100 % recycled aluminium, "CFRP was found to be preferable". I did not identify the paper reliably; it was surfaced in search results near https://www.politesi.polimi.it/handle/10589/253307 or the Cranfield record https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/a3170555-103f-46e6-b726-d394ac6e6fea/content. Not verified.

### Inferences
- Scelsi's payback is tiny compared with an aircraft life of tens of thousands of hours: 60–113 h against Q1's order-of-magnitude 50,000–75,000 h life (UNVERIFIED (memory)). The CFRP-vs-Al ranking for a moving airframe part is therefore insensitive to the end-of-life choice and to manufacturing-energy uncertainty. This matches the Eco Audit white paper's statement that the use phase dominates (Q4).
- Scelsi's credit scheme favours aluminium (substitution credit for Al recycling, none for CFRP) and still shows CFRP winning. So the result is conservative for CFRP.

### Gaps
- Timmis 2015 full text: the actual payback (flights/years), CO2 totals and lifetime assumptions were not retrieved.
- No Lufthansa or Airbus primary CFRP-vs-Al LCA was found in this session.
- No CO2e totals in kg from a verified source. Scelsi reports Eco-indicator points only.

---

## Q4. End of life: AFRA, PAMELA, recycling rates, CFRP recycling, and Eco Audit credit methods

### Takeaway
Airbus's own page (fetched) says Tarmac Aerosave recycles **92 % of an aircraft's total weight** and >99 % of CFM engine parts. PAMELA demonstrated up to **85 %** on an A300 (snippet). For CFRP, thermal recycling is cited at about **3–30 MJ/kg**, against 183–594 MJ/kg for virgin fibre (snippet from a 2026 review). Recovered-fibre strength depends strongly on the process: solvolysis retains about 95–98 %, and air pyrolysis at ≥600 °C degrades strength a lot (snippets). Granta/Ansys Eco Audit uses the **recycled-content method** in the main bars and reports the end-of-life credit only as a separate hatched "EoL potential" bar (full text).

### Cited Findings
- **Airbus 2022 [PAGE]:** "92% of an aircraft's total weight and more than 99% of its engine parts (CFM) is recycled by Tarmac Aerosave." A320 composition: aluminium and Al-Li alloys 72 %, steel 9 %, titanium 6 %. The A350 is over 50 % composite by structure. Tarmac Aerosave was founded in 2007 out of the Airbus-coordinated PAMELA project. The HELACS project (started early 2022) addresses dismantling and recycling of large composite structures. No composite recycling rate is given — https://aircraft.airbus.com/en/newsroom/news/2022-11-end-of-life-reusing-recycling-rethinking
- **PAMELA (LIFE05 ENV/F/000059) [SNIPPET]:** demonstrated on an A300 "recycling up to 85% of plane components", against an earlier rate of about 60 %; 61 t of the airframe were recycled, completed in 2007. Composites were then only about 4 % of an A300 — https://webgate.ec.europa.eu/life/publicWebsite/project/LIFE05-ENV-F-000059/process-for-advanced-management-of-end-of-life-of-aircraft ; https://live.ainonline.com/aviation-news/business-aviation/2008-06-02/airbus-studies-green-solution-aircraft-dismantling-work
- **AFRA [SNIPPET]:** founded 2006; publishes the Best Management Practice guide for aircraft disassembly and recycling. Membership is reported as 72 or 80 (2022), and the sources conflict. No AFRA primary document was read — https://en.wikipedia.org/wiki/Aircraft_recycling
- **Boeing recycling rate:** not found in this session (gap).
- **CFRP recycling energy [SNIPPET]:** virgin CF 183–594 MJ/kg against thermal recycling about 3–30 MJ/kg (Alsubaie & Yang, ICMR 2026, Strathclyde) — https://strathprints.strath.ac.uk/97460/1/Alsubaie-Yang-ICMR-2026-Recycled-carbon-fibre-in-circular-economy-applications.pdf . A lab-scale pyrolysis LCA at 500 °C gives about 110 MJ/kg rCF cumulative energy demand. The conflict with the 3–30 MJ/kg range is probably due to scale and system boundary (my guess) — https://programme.exordo.com/isie2017/delegates/presentation/436/ (attribution uncertain).
- **Recovered fibre quality [SNIPPET]:** pyrolysis in air at ≥873 K "greatly reduced tensile strength", while superheated steam preserved strength (Obunai et al., Composites Part A, 2023) — https://techxplore.com/news/2023-11-reclaiming-carbon-fibers-discarded-composite.amp ; reactive pyrolysis preserves strength better than conventional pyrolysis (Tecnalia) — https://scienceportal.tecnalia.com/en/publications/towards-sustainable-composite-manufacturing-with-recycled-carbon--2/ ; solvolysis retention is about 95 % (ZnCl2) and up to 98 % (supercritical fluid) — https://www.urp.udel.edu/?p=16079 and https://pubs.rsc.org/en/content/articlepdf/2019/ra/c8ra08958b (which source holds which number was not checked).
- **Ansys/Granta Eco Audit white paper (Ashby, Coulter, Ball, Bream; v3, Oct 2021) [FULL TEXT, p.9]:** five end-of-life options: landfill, combustion for energy recovery, recycling, re-engineer, reuse. Credit rule: "We therefore assign a credit to the use of materials with recycle content at the start of life, and give no credit for recycling at the end". This is stated to avoid double counting and to conform with PAS 2050 / BSI 2008. The end-of-life benefit is shown as a separate cross-hatched "EoL potential" bar (Fig. 8). p.12: when asked, the tool replaces virgin-material energy and CO2 with values for "the recycle fraction in current supply". PDF: https://ansys.synopsys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf (landing page https://www.ansys.com/academic/educators/education-resources/eco-audit-white-paper redirects to ansys.synopsys.com).
- **Eco Audit use phase, mobile mode [FULL TEXT, p.10]:** "Products that are part of a transport system carry an additional energy and CO2 penalty by contributing to its weight." The user picks a fuel and mobility type and enters usage and daily distance. The paper does **not** list the aircraft MJ/t·km factor; it must be read from the tool's look-up table or help. p.6: for a civil aircraft (Fig. 4) the use phase consumes more energy than all other phases combined. A dominant phase typically accounts for "60% or more".

### Inferences
- For the Ideathon eco audit, the Eco Audit default (recycled-content in the main bars, EoL potential hatched) treats Al and CFRP symmetrically. An Al part gets no end-of-life recycling credit in the main total unless recycled content is selected. This differs from Scelsi's substitution credit for Al. State which convention is used.
- Airframe recycling rates of 85–92 % come mainly from metal-dominated A300/A320 airframes. They should not be applied to a CFRP component. For a CFRP part, "landfill" or "combust" is the defensible default EoL in Eco Audit, with "downcycle" (rCF as non-structural or chopped fibre) as a sensitivity case. This is an inference; the strength-loss evidence above is from snippets.

### Gaps
- AFRA BMP document, Boeing recycling rate and 787 composite EoL data were not retrieved.
- Paired energy and fibre-property data for the same recycling process were not found.
- The Eco Audit aircraft mobility factors (MJ/t·km for short-haul or long-haul jet, helicopter) are not in the white paper text and need reading inside Granta EduPack.

---

## Q5. Transport phase magnitude

### Takeaway
Two sources read in full say transport is minor for aircraft parts. Eco Audit's Fig. 4 places the use phase above all other phases for a civil aircraft, and Scelsi excluded transport of materials as a minor contribution. Neither gives a numeric share for an aerospace part, though.

### Cited Findings
- **Scelsi 2011 [FULL TEXT, p.211]:** "Neither environmental impacts associated with the manufacturing of tools, transport and buildings … are included in the analyses. These aspects have been excluded due to their minor contribution to the goal of the study." URL as in Q1.
- **Eco Audit white paper [FULL TEXT, pp.5–6, 10–12]:** the transport phase is mass × distance × the MJ/t·km and kgCO2/t·km of the chosen mode. Worked example: a 14 t truck at **0.87 MJ/t·km, 0.062 kgCO2/t·km** (p.12, PET bottle case). For a civil aircraft the use phase consumes more energy "than the sum of all the others" (p.6, Fig. 4). PDF as in Q4.

### Inferences
- Illustrative arithmetic, mine: 1 kg moved 2,000 km by truck costs 0.002 t × 2,000 km × 0.87 MJ/t·km ≈ 3.5 MJ. That is negligible next to CFRP embodied energy (hundreds of MJ/kg, per the Q4 snippet) and the use-phase fuel (tonnes of fuel per kg, Q1 inference). Transport is therefore likely below 1 % of the life total unless the part is air-freighted over long distances.

### Gaps
- No aerospace-specific source giving a transport share in % was read. The Eco Audit air-freight factor was not extracted.
