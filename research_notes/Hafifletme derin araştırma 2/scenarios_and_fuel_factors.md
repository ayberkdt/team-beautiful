# Ideathon 2026 Ansys challenge: likely task shapes, and fuel-per-kg factors for aircraft other than airliners

Research date: 2026-11-01. Tag legend: **[FULL]** = I read the full source text in this session (web page fetch, or a PDF fetched and then text-extracted locally with pypdf). **[SNIPPET]** = search-engine summary only; the source was not opened. **UNVERIFIED (memory)** = no source read in this session. No tag has been upgraded. All arithmetic is written out.

---

## A1. What comparable challenges asked (component, loads, envelope, constraints, deliverables, rubric)

### Takeaway
I found no public Ansys problem statement for the 2024 Ideathon. Only the 2023 Ansys brief is public. It was an aircraft-conceptual-design plus mission-planning task in STK, not a structural task, and it was judged on "engineering approach as a whole". The closest public match for "Discovery topology optimisation + Granta EduPack material selection + streamlined LCA" is Ansys's own **bike crank case study**. No public source I found gives load magnitudes for that kind of task.

### Cited Findings

**EUROAVIA Ideathon, past editions**
- 2023 edition: there were two challenges. GTD set "Monitoring and predictive maintenance of on-board reusable systems" (space, IVHM/RAMS). Ansys set "Design and mission optimization of a crisis response aerial vehicle", with keywords aircraft design, CFD, flight envelope and Digital Mission Engineering. — [ideathon.euroavia.eu/2023-edition](https://ideathon.euroavia.eu/2023-edition/) [FULL]
- Requirements in the 2023 Ansys technical card: cruise range ≥ 1300 km, loiter 30 min, stall ≤ 150 km/h, max speed 500 km/h, ceiling 10,000 m, rate of climb 10 m/s, take-off ground roll 800 m, crew of 4 + up to 10 passengers + 200 kg supplies. It names the Raymer (6th ed.) and Anderson workflows and Ansys STK for the second part of the challenge (mission flight path and sensor coverage). The card says teams should not go into "configuration, structural and stability characteristics". — [Ansys-challenge.pdf, pp. 2–3](https://ideathon.euroavia.eu/wp-content/uploads/2023/08/Ansys-challenge.pdf) [FULL]
- 2023 rubric (no weights published): teams "will be evaluated on your engineering approach as a whole" and not on each objective separately. The card also says that with the right justification "there is no such thing as a wrong answer". — same PDF, p. 3 [FULL]
- 2024 edition: the theme was **sustainability**. Teams had 3–4 members. Stage 1 was 26–31 Oct 2024 in Toulouse and stage 2 was 1–6 Dec 2024 in Zagreb, with a 48 h competition. In stage 1 each team picks one challenge proposed by a company. — [brochure-2024.pdf, pp. 3–5](https://ideathon.euroavia.eu/wp-content/uploads/brochure-2024.pdf) [FULL]
- The 2024 sponsors were Ansys, Eurocontrol and IGA. Neither the 2024 edition page nor the finale blog publishes any challenge statement. — [ideathon.euroavia.eu/2024-edition](https://ideathon.euroavia.eu/2024-edition/) [FULL]; [EUROAVIA blog, 2024-12-28](https://blog.euroavia.eu/2024/12/28/ideathon-finale-2024-as-zagreb/) [FULL]
- UniBoss (Forlì-Bologna) won the first edition. — [brochure-2024.pdf, p. 6](https://ideathon.euroavia.eu/wp-content/uploads/brochure-2024.pdf) [FULL]

**Ansys academic material for the same workflow**
- Bike crank case study: it pairs Granta EduPack material selection with Ansys Discovery FEA and topology optimisation to reduce the material in a bike crank. It adds a streamlined LCA of "ecological and economic impact" and a final trade-off of "key performance indices". The download is a case-study report plus simulation files (`bike-crank-case-study-casbiken23.zip`). The web page gives no loads, design space or material list. — [ansys.synopsys.com bike-crank-case-study](https://ansys.synopsys.com/academic/educators/education-resources/bike-crank-case-study) [FULL page; zip not opened]
- The Granta EduPack Eco Audit tool is described as a streamlined Life Cycle Inventory for design decisions. A theory white paper exists (model as of 2021). — [Eco Audit white paper page](https://www.ansys.com/academic/educators/education-resources/eco-audit-white-paper) [SNIPPET]
- Ansys Innovation Space has an AIM/Discovery application example that topology-optimises a bracket with **two fixed supports and one applied load** for the best strength-to-weight shape (release 19.1+). — [innovationspace.ansys.com forum topic](https://innovationspace.ansys.com/knowledge/forums/topic/discovery-aim-topology-optimization-of-a-bracket) [SNIPPET]
- ASEE paper: a student lab in which a bracket is scanned, lightened by topology optimisation and 3D printed. — [peer.asee.org/32598.pdf](https://peer.asee.org/32598.pdf) [SNIPPET]
- Ansys runs a separate International Materials Selection Challenge (IMSC) that uses Granta EduPack, and final reports for 2024 are published. — [2024 IMSC final reports](https://www.ansys.com/academic/educators/education-resources/2024-international-materials-selection-challenge-final-reports) [SNIPPET; the redirect was not followed, so the problem statement was not read]
- CADFEM blog "Saving CO2 with Ansys Topology Optimization" exists. — [blog.cadfem.net](https://blog.cadfem.net/en/saving-co2-with-ansys-topology-optimization) [SNIPPET, content not read]

**Canonical topology-optimisation challenge (not verified)**
- GE/GrabCAD jet engine bracket challenge (2013). From memory: Ti-6Al-4V, 4 bolt interfaces, a pin/clevis load. Load cases roughly 8,000 lbf vertical, 8,500 lbf horizontal, 9,500 lbf at 42° from vertical, and 5,000 lbf·in torsion. Judged on mass reduction under a stiffness/strength constraint. — **UNVERIFIED (memory)**. Read the GrabCAD challenge page before using any of these numbers.

### Inferences
- The 2023 Ansys brief and the 2024 sustainability theme show a pattern. The task is open-ended, judged on justified engineering approach rather than one optimal number, and has to fit into 48 h. For 2026 this suggests a simple geometry and 1–3 load cases, with marks for documented assumptions and trade-offs.
- The bike-crank case study is Ansys's own teaching template for exactly the Discovery → EduPack → LCA → trade-off chain. If the 2026 task is structural, judges will probably expect its structure: requirements, material screening, topology optimisation, validation, LCA, then a trade-off table.

### Gaps
- I found no public statement for the **2024 or 2025 Ansys Ideathon challenges**. The 2024 brochure (11 pages) has no challenge text.
- Not researched in this session (tool budget): Airbus Fly Your Ideas, AIAA design competitions with LCA, and the IMSC 2024 problem statement. Their load cases and rubrics are unknown.
- I did not open the contents of the bike-crank zip, so its load magnitudes and design envelope are unknown.

---

## A2. The 5 most likely task shapes for 2026 (ranking is INFERENCE)

### Takeaway
My inference is that the most likely shape is a small aircraft structural bracket or fitting under 1–3 static load cases. Teams would topology-optimise it in Discovery, choose between Al, Ti, steel, CFRP and AM alloys in EduPack, and justify the choice with an Eco Audit in which use-phase fuel is the decisive term.

### Cited Findings
- The basis for the ranking is in A1: [2023 Ansys card](https://ideathon.euroavia.eu/wp-content/uploads/2023/08/Ansys-challenge.pdf) [FULL], the [2024 sustainability theme](https://ideathon.euroavia.eu/wp-content/uploads/brochure-2024.pdf) [FULL], the [bike crank template](https://ansys.synopsys.com/academic/educators/education-resources/bike-crank-case-study) [FULL] and the [Innovation Space bracket](https://innovationspace.ansys.com/knowledge/forums/topic/discovery-aim-topology-optimization-of-a-bracket) [SNIPPET]. The "expected task" itself comes from the caller's brief (`docs/10_synopsys_2026_brief.md`), which I did not re-read in this session.

### Inferences (ranking)
1. **Airframe or engine bracket/fitting.** Examples: engine-mount bracket, seat-track or galley bracket, flap-hinge fitting. Design space is a block with bolt holes as frozen regions, there are 1–3 static load cases, and the topology-optimisation objective is minimum mass subject to stress or stiffness. The material shortlist would be Al 7075, Ti-6Al-4V, AM AlSi10Mg/Ti, CFRP. The Eco Audit covers material, manufacture (machining vs AM), use-phase fuel and end of life. Reasons: it matches the Innovation Space bracket and GE bracket archetypes, the bike-crank chain, and a 48 h budget.
2. **UAV/drone arm or eVTOL boom/rotor-arm.** It has a bending + torsion load from thrust and its use phase is electric (kWh). Reasons: the 2023 Ansys brief was about a UAV-type crisis-response vehicle, and eVTOL fits the sustainability theme. This shape needs an energy-per-kg factor (B6).
3. **Satellite or launcher bracket.** It is driven by quasi-static launch g-loads plus a first-natural-frequency constraint, and the use phase has no fuel. The Eco Audit is then dominated by material production, and cost per kg to orbit matters. Reason: the 2023 GTD challenge shows EUROAVIA accepts space topics.
4. **Cabin part made in high numbers** (seat frame or leg, tray-table arm). There are many parts per aircraft, so fleet-level kg × use-phase factor dominates, and certification load cases (for example 16 g dynamic) show up only as static equivalents.
5. **Wing rib, landing-gear link or door hinge**: a larger primary-structure part with multiple load cases. This is less likely in 48 h because of meshing, solve time and part complexity.

### Gaps
- I found no evidence that rules any of the five shapes out. The ranking is judgement only.

---

## B1. Marginal vs average fuel per kg (conflict C-22)

### Takeaway
Steinegger (ZHAW) states the two quantities separately. On average it takes about **0.2 kg of fuel to carry 1 kg of payload 1000 km**. The **marginal** saving per kg removed is only about **0.02–0.03 kg fuel per 1000 km**. A lightweighting credit has to use the marginal figure. Using fuel ÷ payload overstates the saving by about 6×.

### Cited Findings
- "it takes on average ~ 0.2 kg fuel to transport 1 kg of weight over a distance of 1'000 km". An extra ~0.02–0.03 kg fuel per 1000 km is needed for every kg added (the marginal fuel burn rate, MFB), and removing 1 kg saves the same amount. Basis: simBrief flight plans at 36,000 ft, no wind, no reserve fuel, 105 kg per passenger. Aircraft: A321 (A322), A330-300 (A333), A380-800 (A388) only. — [Steinegger, "Fuel Economy as Function of Weight and Distance", ZHAW, p. 1](https://digitalcollection.zhaw.ch/bitstream/11475/1896/6/Steinegger_Fuel_Economy_as_a_Function_of_Weight_and_Distance_v1-1.pdf) [FULL]
- Fig. 7d (p. 5), air distance 4,200 km. A321: trip fuel at zero payload 10.5 t, at max payload 12.6 t; MFBp 0.12 kg/kg; max payload 17.2 t. A333: 23.4 t / 27.5 t, MFBp 0.08. A388: 43.3 t / 59.1 t, MFBp 0.17. — same source, p. 5 [FULL]
- Fig. 15 (p. 11), MFB in kg fuel per kg payload at 2,000 / 4,000 / 5,000 km: A321 = 0.07 / 0.12 / 0.16. — same source, p. 11 [FULL]
- Trip fuel rises slightly progressively with distance because of the "fuel for fuel" effect. The effect is small compared with flying outside the optimum range. — same source, pp. 7, 11 [FULL]

Arithmetic (A321, 4,200 km, from Fig. 7d):
- Marginal: (12.6 − 10.5) t / 17.2 t = 0.122 kg/kg per flight. Per 1000 km: 0.122 / 4.2 = **0.029 kg/(kg·1000 km)**.
- "Average per kg payload": 12.6 / 17.2 / 4.2 = **0.174 kg/(kg·1000 km)**, which matches the ~0.2 headline.
- Ratio of marginal to average-per-payload: 0.029 / 0.174 = **0.17**, i.e. a ~6× overstatement if the average figure is used for a structural kg.
- The fair comparison is average fuel per kg of **aircraft** mass. That needs the A321 TOW, which the paper does not give. With TOW ≈ 85 t (**UNVERIFIED (memory)**): 12.6 / 85 / 4.2 ≈ 0.035, so marginal / average(TOW) ≈ 0.029 / 0.035 ≈ 0.8. This figure is illustrative only.

### Inferences
- There are three distinct quantities, and they must not be mixed: (i) fuel ÷ payload, about 0.17–0.2 per 1000 km and not valid for structural mass; (ii) fuel ÷ TOW, the average, about 0.03–0.04; (iii) dFuel/dm, the marginal, about 0.02–0.03 for airliners. The defensible figure for the Eco Audit use phase is (iii). If only (ii) is available, scale it by about 0.7–0.9.
- The reason marginal < average: part of the drag (parasite drag) does not depend on weight. At fixed speed and altitude only the induced-drag share grows with W (it grows as W²). At the minimum-drag speed dD/dW = D/W, so marginal equals average. Jets usually cruise faster than that, so marginal is smaller than average. This is standard performance theory, not taken from the sources above.

### Gaps
- Steinegger has **no turboprop, business jet or rotorcraft**. The values below are my own derivations from manufacturer data or physics.

---

## B2. Regional turboprop (ATR 72-600; Dash 8 not covered)

### Takeaway
ATR's own data put the average at about **0.069 kg fuel per kg of MTOW per 1000 km** on a 300 NM trip. The cruise-increment slope is about **0.057**. By analogy with B1, the marginal figure is probably about **0.04–0.05 kg/(kg·1000 km)** (inference).

### Cited Findings
- ATR 72-600 (PW127M/N, 72 seats): MTOW basic 22,800 kg (option 23,000 kg); MZFW 20,800 kg; typical in-service OEW 13,450 kg; max payload 7,550 kg; max fuel 5,000 kg. Cruise fuel flow 762 kg/h at 275 KTAS (510 km/h). 200 NM block fuel 638 kg (61 min); **300 NM block fuel 879 kg (84 min)**. — [ATR Factsheet ATR 72-600 (2020), p. 2](https://www.atr-aircraft.com/wp-content/uploads/2020/07/Factsheets_-_ATR_72-600.pdf) [FULL]
- The newer PW127XT factsheet gives 869 kg block fuel for 300 NM with 2,750 kg CO2 and claims a 3% block-fuel saving. ATR assumes 95 kg per passenger, EASA reserves and a 100 NM alternate. — [ATR_Fiche72-600-3.pdf (2022)](https://www.atr-aircraft.com/wp-content/uploads/2022/06/ATR_Fiche72-600-3.pdf) [SNIPPET; the file was too large to fetch]

Arithmetic (2020 sheet):
- 300 NM = 300 × 1.852 = 555.6 km.
- Average on an MTOW basis: 879 / 22,800 = 0.0386 per flight. Per 1000 km: 0.0386 / 0.5556 = **0.069 kg/(kg·1000 km)**.
- Average on an estimated TOW basis: ZFW = 13,450 + 72 × 95 = 20,290 kg (95 kg/pax is from the SNIPPET source). TOW ≥ 20,290 + 879 = 21,169 kg, excluding reserves. f = 879 / 21,169 = 0.0415 per flight, giving **0.075 per 1000 km**.
- Cruise increment between 200 and 300 NM: (879 − 638) kg / 185.2 km = 1.30 kg/km. Divided by 22,800 kg this is **5.7 × 10⁻⁵ kg/(kg·km) = 0.057 per 1000 km**. This strips out the climb and taxi fixed fuel, but it is still an average.
- Cruise fuel flow ÷ MTOW ÷ speed: 762 / 22,800 / 510 = 6.6 × 10⁻⁵ kg/(kg·km), i.e. 0.066 per 1000 km. This is consistent with the figures above.

### Inferences
- Applying the Steinegger marginal/average ratio of about 0.7–0.9 to 0.057–0.069 gives a **marginal of about 0.04–0.06 kg/(kg·1000 km)** for the ATR 72. This is higher than for airliners (0.02–0.03) because turboprop sectors are short and climb-dominated. **Label: inference, not measured.**
- Example for a lifetime credit, built only from assumptions: 0.05 × 0.5556 = 0.028 kg fuel per kg per 300 NM flight. Lifetime flight count is an assumption to be taken from the catalogue.

### Gaps
- **Dash 8-400 not researched.** I found no published fuel-vs-weight sensitivity for any turboprop; ATR's sheets give fuel against distance only.

---

## B3. Business jet (Challenger 350)

### Takeaway
I found no manufacturer fuel-vs-weight or block-fuel data. An illustrative average of about **0.05 kg/(kg·1000 km)** rests only on third-party fuel-burn figures that conflict with each other. Do not use it without a better source.

### Cited Findings
- Challenger 350: max range 3,200 nm (5,926 km), with NBAA IFR reserves, ISA, M0.80, 8 passengers and 2 crew. Typical cruise M0.80; initial cruise altitude at MTOW 43,000 ft. The factsheet gives **no weights and no fuel figures**. — [Bombardier Challenger 350 factsheet (04/24), p. 2](https://bombardier.com/sites/default/files/2024-04/Challenger350-factsheet.pdf) [FULL]
- MTOW 18,416 kg. — [defense.bombardier.com Challenger 350](https://defense.bombardier.com/en/aircraft/challenger-350) [SNIPPET]
- Third-party fuel burn figures conflict: 178 gph, 255 gph and 300 gph. — [aircraftcostcalculator / libertyjet / charter sites](https://www.aircraftcostcalculator.com/AircraftOperatingCosts/535/bombardier-challenger-350/) [SNIPPET, low quality]

Arithmetic (illustrative only):
- Jet-A ≈ 3.03 kg/gal (0.8 kg/L × 3.785 L, **UNVERIFIED (memory)**). 255 gph × 3.03 = 773 kg/h.
- Divided by MTOW: 773 / 18,416 = 0.042 per hour.
- TAS at M0.80 above 36 kft ≈ 0.80 × 295 m/s = 236 m/s ≈ 850 km/h (speed of sound **UNVERIFIED (memory)**). 0.042 / 0.85 = **0.049 kg/(kg·1000 km)**, as an average.
- The 178–300 gph spread gives **0.034–0.058**.

### Inferences
- A business jet flies far below MTOW for most of the time and at high altitude and Mach, so its marginal factor is probably close to the airliner range, about 0.03–0.04 (inference). Its annual utilisation is much lower (a few hundred hours per year, **UNVERIFIED (memory)**), so the lifetime credit per kg will be much smaller than for an airliner.

### Gaps
- No AFM or manufacturer block-fuel data was found, and I found no weight-sensitivity data at all.

---

## B4. Helicopter (H145; Bell 407 as a data proxy)

### Takeaway
In **cruise** the fuel flow of a light helicopter is only weakly sensitive to weight. FAA data for the Bell 407 show less than 5% fuel-flow change over a +14% weight range, so the elasticity is at most 0.35. In **hover**, momentum theory gives power ∝ W^1.5 (elasticity 1.5). The per-kg factor therefore depends on the hover/cruise mix, and using fuel ÷ MTOW is wrong in both directions.

### Cited Findings
- FAA AEDT helicopter fuel-burn report, Method 3, uses Bell 407 flight-manual charts: fuel flow against TAS at weights 4,600, 5,000 and 5,250 lb (sea level, 15 °C, 75 and 105 kt). "For these three weights … the difference is small (within 5%)". The report picks 5,000 lb as the reference weight. — [Helicopter Fuel Burn Modeling in AEDT, FAA AEE, report p. 23 / PDF p. 41, Fig. 7](https://rosap.ntl.bts.gov/view/dot/9351/dot_9351_DS1.pdf) [FULL]
- The same report models hover from ideal power as a function of instantaneous weight W, density ρ and rotor radius R (eq. 3.1), divided by the figure of merit (eq. 3.2), following Prouty. — same source, §3.3.1, PDF p. 30 [FULL; the equation glyphs were garbled in extraction, see Inferences]
- Its fuel model matches flight-manual cruise fuel consumption to about 4%. — same source, abstract [FULL]
- H145: standard fuel tank 723 kg; hover ceiling OGE 2,729 m. — [airbus.com H145 technical information](https://airbus.com/en/products-services/helicopters/civil-helicopters/h145/h145-technical-information) [SNIPPET]. H145M MTOW 3,800 kg. — [airbus.com H145M technical information](https://airbus.com/en/products-services/helicopters/military-helicopters/h145m/h145m-technical-information) [SNIPPET]
- EC145 fuel flow "245 kg/h", with no stated conditions. — [mobipalma.mobi page](https://mobipalma.mobi/lju43/ec145-fuel-consumption-per-hour) [SNIPPET, untrustworthy source]

Arithmetic:
- Bell 407 cruise elasticity: ΔW/W = (5,250 − 4,600) / 4,600 = 14.1%; ΔFF/FF ≤ 5%. ε = 0.05 / 0.141 ≤ **0.35**. So the marginal fuel flow per kg is ≤ 0.35 × (FF/W).
- Hover elasticity: P_ideal = W·√(W / (2ρπR²)) ∝ W^1.5, so ε = **1.5**. This is the standard momentum-theory form; the source's equation could not be read verbatim, so the exponent itself is **UNVERIFIED in this source**.
- Illustrative H145 average, mixing sources: 245 kg/h ÷ 3,800 kg = 0.064 per flight-hour. Marginal in cruise ≤ 0.35 × 0.064 = **≤ 0.023 kg fuel per kg per hour**. Marginal in hover ≈ 1.5 × 0.064 ≈ **0.097 per hour** (if hover fuel flow ≈ the 245 kg/h figure, which is unverified).

### Inferences
- For EMS or offshore helicopter missions that are mostly cruise, the marginal factor per flight-hour is about 0.3–0.4 × the average. Missions with a lot of hover (hoist, SAR) push it above the average. Report helicopter factors as kg fuel per kg per **flight-hour**, not per km.

### Gaps
- I found no official H145 fuel-flow-vs-gross-weight chart; the RFM performance section and the Airbus "H145 Flight Perfo" app would hold it. The Bell 407 Fig. 7 values could only be read as a bounded difference ("within 5%"), not as point values.

---

## B5. Large UAV / MALE

### Takeaway
No source was read. The only numbers I have are from memory.

### Cited Findings
- MQ-9-class figures: MTOW ≈ 4,760 kg, internal fuel ≈ 1,800 kg, endurance ≈ 27 h. — **UNVERIFIED (memory)**.

Arithmetic (memory inputs): 1,800 / 27 / 4,760 = **0.014 kg fuel per kg MTOW per hour**, as a mission average.

### Inferences
- A MALE aircraft loitering near its maximum-endurance speed flies close to the minimum-drag condition, where marginal ≈ average (see B1). So 0.014 per hour could serve as a first-order marginal factor (inference). Fuel mass falls a lot during the mission (fuel ≈ 38% of MTOW), so time-averaging matters.

### Gaps
- Not searched (tool budget). A primary source is needed: GA-ASI spec sheet or a USAF fact sheet.

---

## B6. eVTOL (energy per kg per km)

### Takeaway
Physics gives cruise energy per kg per km as e = g / (η·L/D) ≈ **0.25–0.4 Wh/(kg·km)**. Hover costs about **3–4 Wh/kg per minute**. On short urban trips hover dominates, so an eVTOL lightweighting credit should be given per flight cycle, not per km.

### Cited Findings
- Kasliwal et al. 2019, "Role of flying cars in sustainable mobility", Nat. Commun. 10:1555, DOI [10.1038/s41467-019-09426-0](https://doi.org/10.1038/s41467-019-09426-0). Hover dominates energy on short trips and cruise takes over at about 20 km. VTOL primary energy breaks even with a combustion car at about 120 km. — [Supplementary info PDF](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-019-09426-0/MediaObjects/41467_2019_9426_MOESM1_ESM.pdf) [SNIPPET; the article was not opened (login redirect)]
- Example model: 1,800 kg tilt-propeller eVTOL, disk loading 580 N/m², η_h = 0.7, hover power 362.3 kW, cruise power 40.8 kW. — [arXiv 2401.00806](https://arxiv.org/pdf/2401.00806) [SNIPPET; cruise speed not seen]

Arithmetic:
- Cruise: e = g / (η·L/D). With L/D = 12 and η = 0.75 (assumptions): 9.81 / 9 = 1.09 kJ/(kg·km) = **0.30 Wh/(kg·km)**. With L/D 10–15 and η 0.7–0.8 the range is 0.23–0.39 Wh/(kg·km).
- Hover per kg, arXiv case: 362.3 kW / 1,800 kg = 201 W/kg. That is 201 × 60 / 3600 = **3.35 Wh/kg per minute of hover**.
- Momentum-theory cross-check (inputs from that SNIPPET): v_i = √(580 / (2 × 1.225)) = 15.4 m/s; g·v_i = 151 W/kg; divided by 0.7 = 216 W/kg. This is within 8% of 201 W/kg.
- Cruise per kg, arXiv case: 40.8 kW / 1,800 kg = 22.7 W/kg. A per-km value cannot be derived without the cruise speed.

### Inferences
- Example: a 25 km mission with 2 min of hover. Per kg: 2 × 3.35 + 25 × 0.30 = 6.7 + 7.5 = 14.2 Wh. Converting to CO2 needs a grid intensity, which comes from the Eco Audit electricity mix. For eVTOL, unlike fuel-burning aircraft, hover makes marginal ≈ average or higher (elasticity 1.5).

### Gaps
- Kasliwal's own Wh/km values were not read. I found no measured flight data for an eVTOL.
