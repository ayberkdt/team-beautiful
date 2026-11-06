# EASA: Accident Investigation — research note for EUROAVIA Ideathon 2026

Prepared 3 November 2026 for the Bruges sprint (challenges revealed morning of 4 Nov 2026).
Language: English. Format: lists only (no tables), so it can be pasted into slides or notes.

## Evidence tags (read this first)

- **[D]** = I read it on the source page or document during this session (HTML page or PDF text I extracted myself).
- **[D-sec]** = I read it this session, but on a secondary source (news, encyclopaedia, vendor), not the primary report.
- **[A]** = from a search-result snippet or a search-engine summary only. I did not open the page. Treat it as a lead, not a fact.
- **[Y]** = my own judgement, inference or general background knowledge that I did not verify this session.
- If something could not be found, it says **NOT FOUND** or **NOT VERIFIED**.

Primary sources that failed to load this session (so anything from them is [A] or missing): EUR-Lex HTML pages (empty response), ICAO.int FAQ / fact-sheet pages (HTTP 404), the JTSB Haneda interim report (file > 10 MB), the Lithuanian SIA page for EC-MFE (HTTP 403), EASA SIB 2025-03 (EASA publication tool under maintenance).

---

## 0. What we know about the event itself

- Ideathon 2026: 3–8 Nov 2026, Brugge, hosted by AS Oostende; "Fast-Paced Hackathon" format; four challenges, each corresponding to one of the four competition slots; **all teams do all four challenges**; challenge details confidential until the morning of 4 Nov. [D] https://ideathon.euroavia.eu/wp-content/uploads/Ideathon-2026-Regulations-1.1.pdf
- Jury: "technical experts from the sponsoring companies" plus academic representatives if applicable. Criteria: **technical feasibility, innovation/creativity, sustainability, presentation quality**. No weights published. [D] same PDF
- Deliverable: "a conceptual solution for each challenge"; English only; BYOD; sponsors "may provide temporary licences or access to specialized engineering software". Sponsors may require an NDA. [D] same PDF
- Preliminary schedule shows competition blocks on 4 and 5 Nov, guest speakers, and "Team Presentations" in the afternoon of a later day; exact durations "will be finalized". [D] same PDF (schedule table text was partly scrambled in extraction, so the exact slot-to-day mapping is NOT VERIFIED)
- The public Ideathon pages do not name sponsors or EASA. [D] https://ideathon.euroavia.eu/ and https://euroavia.eu/event/ideathon-2026/
- Past editions: 2024 sponsors were ANSYS, Eurocontrol and IGA; challenges ran 48 h. [D] https://ideathon.euroavia.eu/2024-edition/ — 2023 challenges were GTD (predictive maintenance / RAMS of reusable launch systems) and Ansys (crisis-response aerial vehicle with digital mission engineering). [D] https://ideathon.euroavia.eu/2023-edition/
- Takeaway [Y]: past challenges were "define a methodology/strategy" and "conceptual design + simulate" types. Expect the EASA one to be a methodology/system-concept challenge, not a CAD task.

---

## 1. EASA's real role in accident investigation (vs. national SIAs)

### 1.1 The legal frame: Regulation (EU) No 996/2010

All [D] from the adopted text at https://www.legislation.gov.uk/eur/2010/996/adopted (this is the EU text as adopted in 2010; later amendments by Reg. 376/2014 and 2018/1139 are not reflected there).

- **Art. 2 definitions**
  - *Accident*: occurrence where a person is fatally or seriously injured, the aircraft sustains damage or structural failure needing major repair, or the aircraft is missing or completely inaccessible. [D]
  - *Serious incident*: an incident involving circumstances indicating "a high probability of an accident". [D]
  - *Incident*: an occurrence other than an accident that affects or could affect the safety of operation. [D]
  - *Safety investigation*: a process by a safety investigation authority "for the purpose of accident and incident prevention", including gathering and analysis of information, conclusions, cause determination, and safety recommendations where appropriate. [D]
  - *Causes*: determining causes "does not imply the assignment of fault" or liability. [D]
  - *Fatal injury*: death within 30 days of the accident. *Serious injury* covers e.g. hospitalisation over 48 h, fractures, certain burns. [D] (full list of serious-injury criteria: NOT VERIFIED this session)
- **Art. 4**: each Member State must have a permanent, independent national civil aviation safety investigation authority (SIA). [D] (confirmed via ASRR 2025 intro, see 1.3)
- **Art. 5**: accidents and serious incidents (of aircraft in the scope of the EASA Basic Regulation) "shall be the subject of a safety investigation" in the Member State of occurrence; investigations are "in no case" concerned with apportioning blame and are independent of judicial proceedings. [D]
  - Whether Art. 5 has a 2 250 kg threshold for certain aircraft categories: NOT VERIFIED.
- **Art. 6(2)**: one SIA may delegate the conduct of an investigation to another SIA. Real use: Austria's SUB handed the Swiss A220 HB-JCD investigation to the Swiss STSB in April 2025. [D] https://www.sust-stsb.admin.ch/r/inhalte/AV-berichte/HB-JCD_StatB_e.pdf
- **Art. 7**: European Network of Civil Aviation Safety Investigation Authorities (**ENCASIA**). Heads of SIAs. Tasks include improving investigation quality, sharing information, peer reviews, training, and reviewing SRs in the database. [D]
  - Art. 7(g) is the basis for identifying "Safety Recommendations of Union-wide Relevance" (SRUR). [D] ASRR 2025 Annex B (see 1.3)
- **Art. 8 — EASA's role is ADVISER, not investigator.** SIAs shall invite EASA (and the national CAAs concerned) to appoint a representative to participate:
  - (a) as an adviser to the investigator-in-charge in any safety investigation in a Member State;
  - (b) as an adviser assisting the Member State's accredited representative in investigations in third countries. [D] (full text quoted in ASRR 2025 Annex B: https://www.easa.europa.eu/en/downloads/142301/en)
  - Advisers may: visit the scene and examine wreckage; suggest areas of questioning and obtain witness information; receive pertinent documents; participate in read-outs of recorded media **except cockpit voice or image recorders**; participate in off-scene work (component examinations, tests, simulations) **except** when it is about determining causes or formulating safety recommendations. [D]
  - Art. 8(3): EASA and CAAs must support the investigation with information, advisers and equipment. [D]
  - Why: EASA is the certifying authority, so it has a conflict of interest on causes and SRs addressed to itself. [Y]
- **Art. 9**: anyone involved who knows of an accident/serious incident must notify the SIA of the State of Occurrence "without delay"; the SIA informs the Commission, EASA, ICAO and the States concerned. [D]
  - Example: AAIU(Be) notified Sweden (State of Operator/Registry), France (State of Design/Manufacture), ICAO and EASA the same day for the 5 Feb 2026 Brussels event. [D] https://mobilit.belgium.be/sites/default/files/documents/publications/2026/AAIU-2026-02-05-01-PRELIMINARY.pdf
- **Art. 14**: protection of sensitive safety information — witness statements and identities, medical data, drafts, cockpit voice/image recordings and transcripts may not be used for purposes other than the safety investigation. [D]
- **Art. 16**: report states its sole objective is prevention; protects anonymity; final report published within 12 months "where possible"; otherwise an **interim statement at each anniversary**. [D]
  - Practice: STSB status report on HB-JCD cites "Article 16 (7)" as the basis for the anniversary report. [D] (STSB PDF above)
- **Art. 17**: SRs may be issued at any stage; dated transmittal letter; an SR "shall in no case create a presumption of blame". [D]
- **Art. 18**: addressee acknowledges and informs the SIA **within 90 days** of actions taken or under consideration (and time to complete), or reasons for no action; SIA tells the addressee **within 60 days** whether the reply is adequate; SRs and responses recorded in the **central repository**. [D] (also quoted verbatim in EASA slide deck, below)

### 1.2 ICAO Annex 13

- Current edition: Annex 13, **13th edition, July 2024** (as cited by BEA). [D] https://bea.aero/en/recommandations/introduction/
- ICAO SR definition: "a proposal of an accident investigation authority based on information derived from an investigation", never aimed at blame. [D] (BEA page)
- **Preliminary report**: Annex 13 Recommendation **5.4.6** — when an occurrence draws heightened public attention, the investigating authority should publish a written preliminary report **within 30 days**. [D] quoted in AAIU(Be) report AAIU-2026-02-05-01 (link above)
  - The separate ADREP Preliminary Report to ICAO within 30 days of the accident. [A] ICAO FAQ snippet (page returned 404 when fetched)
- **Interim statement on each anniversary** if the final report is not public within 12 months. [A] ICAO FAQ snippet; matches EU Art. 16 [D]
- Draft final report consultation with States: typically **60 days** for comments. [A] search summary — NOT VERIFIED against Annex 13 text
- **SR response within 90 days** (Annex 13 Std 6.10 area). [A] ICAO training slide snippet; the EU 90/60-day rule is [D] (Art. 18)
- Final report structure (Annex 13 Appendix): Title; Synopsis; **1 Factual information** (History of the flight; Injuries to persons; Damage to aircraft; Other damage; Personnel information; Aircraft information; Meteorological information; Communications; Flight recorders; Wreckage and impact information; Medical and pathological information; Fire; Survival aspects; Tests and research; Organisational and management information; Additional information; Useful or effective investigation techniques); **2 Analysis; 3 Conclusions; 4 Safety Recommendations; Appendices**. [D] https://skybrary.aero/articles/investigation-final-report
  - SKYbrary's list omitted "Aids to navigation" and "Aerodrome information"; both appear in real EU reports (e.g. AAIU(Be) 2.6 Aids to navigation, 2.8 Aerodrome information). [D] AAIU report; the canonical 1.1–1.18 numbering is [Y]
  - ICAO training material frames it as five parts: Introduction (Title, Synopsis), Factual, Analysis, Conclusions (findings, causes and/or contributing factors), SRs. [A]
- States with rights to participate: State of Occurrence (leads), Registry, Operator, Design, Manufacture; they appoint **Accredited Representatives (ACCREP)** with **advisers**; States of nationality of victims may appoint experts. [Y] general Annex 13 knowledge; practice confirmed in AAIU(Be) report (Sweden, France, then Norway as State of crew nationality to help transcribe CVR) [D]

### 1.3 How EASA actually handles safety recommendations

- EASA processes SRs through its **Safety Investigation & Reporting Section**; each SR goes to a Responsible Unit; replies approved at the **Internal Safety Investigation Response Committee (ISIRC)**, meeting **every 6 weeks**; **first reply within 90 days**. [D] EASA slides "The golden rules for sound and effective Safety Recommendations" (M. Colavita, ICAO-EASA forum 2026): https://www.icao.int/sites/default/files/APAC/Meetings/2026/2026%20ICAO%20EASA%20Forum/Presentations/Agenda%206%20-%20The%20golden%20rules%20for%20sound%20and%20effective%20safety%20recommendations.pdf
- Database: **SRIS (Safety Recommendation Information System), in place since January 2012**. [D] same slides. BEA calls the European platform "SRIS2". [D] BEA page
- ENCASIA WG6 harmonised taxonomy: Reply assessment = Adequate / Partially adequate / Not adequate; SR assessment = Agreement / Partial agreement / Disagreement; Status = Open / Closed. Final status is always set by the SIA. [D] same slides
- EASA's **SMART** rule for SRs: Specific, Measurable, Achievable, Relevant, Timely; one main addressee per SR; numbering like "AIBxyz/YEAR/progressive number"; discuss drafts early with the addressee. [D] same slides
- Classes: **SRGC** (Safety Recommendation of Global Concern, ICAO Doc 9756) and **SRUR** (Union-wide Relevance: systemic, not tied to one type/operator, or recurring across Europe). [D] ASRR 2025 Annex B
- EASA also uses the **full batch of SRs** (not just accepted ones) as input to its Safety Risk Management, example: Erroneous take-off parameters. [D] slides
- **Annual Safety Recommendations Review 2025** (18th edition, covers 2024): [D] https://www.easa.europa.eu/en/downloads/142301/en
  - **40 SRs** addressed to EASA in 2024 from **26 occurrences** (18 accidents → 30 SRs; 8 serious incidents → 10 SRs). No SR on UAVs in 2024.
  - Topics: procedures and regulations 52.5 %, aircraft/equipment/facilities 32.5 %, personnel 15 %.
  - EASA issued **97 formal replies to 92 SRs**; 55 final (80 % led to closure), 42 interim. SIAs rated 25 final replies adequate/partially adequate, 10 not adequate; 36 % of replies still pending SIA assessment at year end.
  - Trend: 80–100 SRs/yr to EASA until 2016, roughly halved in 2017, then 30–60/yr.
  - 2024 EASA technical-adviser deployments listed: A350 JA13XJ / Dash 8 Haneda (Japan); EMB-195 OY-GDC Belgrade (Serbia); ATR 72 PS-VPB (Brazil); B737F EC-MFE Vilnius (Lithuania); A220 HB-JCD near Graz (Austria); B737 HL-8088 Muan (South Korea).
- AIN reports the next review: 39 SRs received in 2025 from 20 events; ~78 SRs addressed. [A] https://backend.ainonline.com/aviation-news/air-transport/2026-08-03/easa-european-safety-recs-focus-aircraft-operations

### 1.4 Belgium: AAIU(Be)

- Air Accident Investigation Unit (Belgium), within FPS Mobility and Transport, **functionally independent** from the Belgian CAA (BCAA); ENCASIA member since 2010; sole purpose is prevention; does not apportion blame. Contact info.AAIU@mobilit.fgov.be. [D] https://mobilit.belgium.be/en/aviation/accidents-and-incidents/air-accident-investigation-unit-aaiu/air-accident-investigation
- Established under Royal Decree of 26 December 2022; reports de-identified and use gender-neutral language; phone +32 2 277 33 44; www.aaiu.belgium.be. [D] AAIU-2026-02-05-01 PDF
- Publishes preliminary reports, progress statements (anniversary), and final reports on mobilit.belgium.be. [A] search listing

### 1.5 EASA's safety-management machinery (where accident data ends up)

- **European Safety Risk Management (SRM)** process, set up by EASA in 2016; data-driven identification of safety issues → assessment → action; Collaborative Analysis Groups (CAGs) and Advisory Bodies. [D] ASRR 2025
- **EPAS 2026** (15th edition, published 18 Dec 2025): [D] https://www.easa.europa.eu/en/document-library/general-publications/european-plan-aviation-safety-epas-2026
  - Vol I strategic priorities (2023–2025 edition extended to end 2026). Addendum adds three priorities, one being **big data technologies for EU safety risk management**.
  - Vol II: 129 actions (15 new; 31 completed in 2025); new items cover PBN, **counter-drone**, flight simulator capability signatures.
  - Vol III = **Safety Risk Portfolios**; new safety issues **SI-9011 "In-flight fires in inaccessible areas"** and **SI-0060 "Out-of-spec synthetic aviation turbine fuels (SATF) in operations"**. Top 20 cross-domain safety issues list.
  - Sustainability hook [Y]: SI-0060 links SAF (RefuelEU) directly to safety; a fuel-quality forensic question is exactly what an investigation challenge could include.
- **Annual Safety Review 2026** (published late Oct 2026, covers 2025). Summary PDF: [D] https://www.easa.europa.eu/en/downloads/144325/en
  - 2025 accidents / fatal / fatalities / serious incidents:
    - CAT complex aeroplanes: 17 accidents, 1 fatal (an air taxi crash after declaring an emergency, 8 fatalities), 51 serious incidents, 17 serious injuries.
    - Non-commercial other aeroplanes: 156 accidents, 21 fatal, 40 fatalities.
    - Helicopters: 45 accidents, 9 fatal, 18 fatalities.
    - Sailplanes: 75 accidents, 15 fatal, 16 fatalities (LOC in 9 of 15 fatal).
    - Balloons: 14 accidents, 1 fatal.
    - **UAS: 27 accidents, 0 fatal, 12 serious incidents.**
    - Non-commercial rotorcraft: a **mid-air collision between two helicopters caused five fatalities**.
  - CAT aeroplane leading risks (ERCS, 2023–2025): 1 Fire/smoke/pressurisation, 2 Aircraft upset, 3 Airborne collision, 4 Collision on runway, 5 Excursion.
  - **Top Safety Topics**: Runway incursions; Approach path management; **GNSS interference**; **Erroneous take-off parameters**; Adverse weather encounters (CAT); Mid-air collision; Inadvertent entry into IMC (GA rotorcraft and small aeroplanes); Bird and wildlife strikes; **Conflict with unauthorised UAS**; **On-board fires (incl. lithium battery fires)**.
  - Headline: fatal accidents and fatalities "remained at or below the average for the previous 10 years" in almost all domains. [D] https://www.easa.europa.eu/en/node/144342

### 1.6 Occurrence reporting: Regulation (EU) No 376/2014

- Mandatory reporting for occurrences that may pose a "significant risk to aviation safety"; voluntary systems for everything else; individuals report **within 72 hours** of becoming aware; organisations report to their authority (or EASA) **no later than 72 hours**; national data go to the **European Central Repository (ECR)** within 30 days of entry in the national database. [D] https://skybrary.aero/articles/regulation-3762014-reporting-analysis-and-follow-occurrences-civil-aviation
- Organisation follow-up: preliminary analysis results **within 30 days**, final results **within 3 months**. [A] Swiss FOCA / UK CAA snippets
- List of mandatory occurrences: Implementing Reg. (EU) 2015/1018 (Annexes I–V: operations, technical, ANS, aerodromes/ground, non-complex aircraft). [D] SKYbrary page above
- Just Culture and reporter protection are a stated objective. [D] SKYbrary page

### 1.7 ECCAIRS 2, ADREP, ECR

- ECCAIRS 2 = "aviation occurrence reporting and safety data management platform developed and maintained by" EASA "on behalf of the European Commission"; EU States transmit to the ECR; also offered to non-EU States via ICAO; uses a common taxonomy aligned with ICAO **ADREP**. [D] https://www.easa.europa.eu/en/node/143347
- Reporting portal: aviationreporting.eu. [D] link on the EASA page
- ICAO says the full ADREP taxonomy is a subset of the ECCAIRS taxonomy. [A]

### 1.8 European Risk Classification Scheme (ERCS)

All [D] from EASA Easy Access Rules for Occurrence Reporting, ERCS chapter: https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-occurrence-reporting?page=8

- Legal basis: Commission Delegated Reg. (EU) **2020/2034** (scheme) and Implementing Reg. (EU) **2021/2082** (review/endorsement; conversion from RAT and ARMS-ERC).
- Scores the **risk of the occurrence, not its outcome**.
- Step 1 severity = Key Risk Area (KRA) + potential loss of life:
  - A no accident likelihood; E minor/serious injury or minor damage; I single fatality / life-changing injury / substantial damage; M 2–19 fatalities or hull loss; S 20–100; X > 100.
  - 10 KRAs: airborne collision, aircraft upset, collision on runway, excursion, fire/smoke/pressurisation, ground damage, obstacle collision in flight, terrain collision, other injuries, security. One KRA per occurrence.
- Step 1 probability = **8-barrier model** with weights: design 5, tactical planning 2, regulations/procedures 3, situational awareness 2, warning systems 3, late recovery 1, protections 1, low-energy occurrence 1. Sum of remaining/stopping barrier weights (0–18) → barrier score 0–9 (0 = worst outcome realised).
- Step 2: score such as "S5" or "M2"; RED (e.g. X0, X1, S0, M0, I0) = high risk; YELLOW (e.g. X3, S3, M2, I1, E0); GREEN (e.g. X5–X9).
- Numerical equivalents for aggregation: X0 = 1 000 000 … X9 = 0.001; S0 = 500 000; M0 = 100 000; I0 = 10 000; E0 = 1 000.
- Competent authorities apply ERCS from 2023. [A]

### 1.9 Data4Safety (D4S)

All [D] https://www.easa.europa.eu/domains/safety-management/data4safety unless noted.

- Voluntary EASA partnership to "identify systemic risks at EU level as well as their mitigations"; Just Culture principle.
- Data: safety reports, airline flight data (FDM), ATM traffic data, weather; later sustainability and (cyber)security.
- Members: founding NAAs (FR, IE, ES) and airlines (BA, easyJet, Iberia, KLM, Ryanair, Vueling); Oct 2023 expansion incl. Belgium NAA, Aer Lingus, Norwegian, TAP, Wizz, 8 ATM organisations (DFS, ENAV, Skyguide, Eurocontrol/MUAC…), Airbus, Boeing; ECA and IFATCA as workforce bodies.
- Platform run by a trusted third party, the **DPPO** (Data Processing and Protecting Organisation).
- Phases: feasibility 2015; proof of concept 2017–2022; development Sept 2022–2026; **operational after 2026**.
- Products: metrics dashboards (SPIs), blind benchmarking, "vulnerability discovery", directed studies (incorrect altimeter settings; insufficient take-off performance); a guidance document on **identifying unstable approaches from flight data**.
- Platform reportedly built on a Databricks lakehouse. [A] ICAO D4S briefing snippet
- EASA AI semi-automation of occurrence encoding runs as an "Occurrence Automations Platform – Data4Safety" (see 3.1). [D]

---

## 2. Investigation methodology toolkit

### 2.1 Phases of a real investigation (as seen in 2025–2026 EU reports)

- Notification → preservation of evidence → go-team decision → ACCREP/adviser appointments → recorder recovery and read-out → factual gathering → preliminary report (≤ 30 days if high public interest) → analysis → draft final report consultation → final report + SRs → SR follow-up. [Y] synthesis; individual steps evidenced below.
- Real-world example of evidence fusion: AAIU(Be) built the SAS43M timeline from crew/ATCO interviews, FDR, CVR, QAR, tower ambient voice recordings, ground surveillance radar and **CCTV**, "synchronized against the radar timeline". [D] AAIU-2026-02-05-01
- Recorder read-outs are often done in a larger SIA's lab: AAIU used BEA's Le Bourget facility; Lithuania's BFU read-out of EC-MFE FDR; Serbia's FDR/CVR read-out at BEA Paris. [D] AAIU report and ASRR 2025
- STSB on HB-JCD: "synchronising the audio recordings from the cockpit with the flight data recordings is an essential prerequisite"; additional **engine recordings** gave insight into the seconds before failure. [D] STSB status report
- On-scene decision: AAIU did not deploy immediately (no injuries/damage) but ordered evidence preservation and secured both recorders next morning. [D]

### 2.2 Evidence types

- **FDR**: hundreds to thousands of parameters (attitudes, speeds, engine, control positions, configuration). [Y]
- **CVR**: four channels typical (AAIU: "over 2 hours of audio … across four channels"). [D] AAIU
- **QAR / FDM data** from the operator (often more parameters, easier access). [D] AAIU used QAR
- **ATC**: radio/ambient recordings, surface movement radar, A-SMGCS safety-net logs. [D] AAIU (A-SMGCS alerts: departure from wrong runway, stop bar crossed, etc.)
- **ADS-B**: crowd-sourced (Flightradar24, ADS-B Exchange) — 1 Hz-ish position/altitude/speed; useful for early trajectory but not certified evidence. [Y]
- **CCTV / passenger video / social media** imagery. [D] AAIU used CCTV
- **Wreckage**: distribution map, impact angles, fracture surfaces, fire patterns; **drone photogrammetry** (2.5).
- **Maintenance records**, technical log, MEL use (Voepass: defect reported only verbally, not logged). [D-sec] https://aerocorner.com/news/voepass-atr-72-crash-investigation/
- **Human factors**: interviews, rosters/fatigue, training records, CRM, medical/toxicology. [Y]; AAIU focus list incl. "actions, workload, training, communication and working environment" of crew and ATCOs. [D]
- **Organisational**: operations manual, SMS, oversight by the authority (Voepass: regulator follow-up criticised). [D-sec]

### 2.3 Analysis models (cheat-sheet descriptions)

- **Reason "Swiss cheese"**: accidents when holes in successive defences line up; active failures vs latent conditions. HFACS is "heavily based upon" it. [A] https://skybrary.aero/articles/human-factors-analysis-and-classification-system-hfacs
- **HFACS** (Shappell & Wiegmann): 4 levels — Unsafe acts → Preconditions for unsafe acts → Unsafe supervision → Organisational influences; ~19 categories; goal is understanding, not blame. [A] same SKYbrary page and Wikipedia snippet
- **SHELL** (Edwards 1972, Hawkins 1975): Software, Hardware, Environment, Liveware (central L, interfaces L-S, L-H, L-E, L-L); error at mismatched interfaces. [A] https://skybrary.aero/articles/icao-shell-model
- **AcciMap** (Rasmussen): maps causal factors across levels from government/regulator down to physical events. [Y]
- **STAMP / CAST** (Leveson, MIT): accidents as inadequate control in a socio-technical control structure; CAST = Causal Analysis based on System Theory; treats software, humans, organisations uniformly; finds broader causes than root-cause analysis. [A] https://ul.com/sis/blog/introduction-to-stamp-stpa-and-cast and MIT theses https://dspace.mit.edu/handle/1721.1/118131
- **Bow-tie**: threats → (prevention barriers) → top event → (recovery barriers) → consequences. Fits ERCS's barrier thinking. [Y]
- **Fault Tree Analysis**: top-down Boolean logic, used in certification (CS-25.1309-type safety assessment). [Y]
- **Why-Because Analysis (WBA)** (Ladkin, Bielefeld): formal counterfactual test for causal links; produces a why-because graph. [Y]
- **Timeline / sequence-of-events** with synchronised clocks (UTC), anchored to radar or FDR time. [D] AAIU practice
- Practical pick for a 5-hour sprint [Y]: timeline → Swiss cheese / bow-tie picture for the jury → HFACS or CAST table for systemic factors → map each finding to a SMART SR and to an ERCS KRA.

### 2.4 Flight path and energy reconstruction

- Inputs: FDR/QAR, ADS-B, radar, GNSS from EFB/portable devices, video photogrammetry. [Y]
- Energy state: specific total energy E_s = h + V²/(2g); rate of change ~ (T − D)·V/W. Plot energy vs distance-to-threshold to show under/over-energy approaches (link to D4S unstable-approach work). [Y]
- Take-off performance checks: TORA/TODA vs computed distance; Belgrade: intersection D5 offered about 1 273 m. [A] search summary; the report's direct cause "take-off from an intersection that did not provide sufficient runway length (TODA)". [D] Serbian final report (below)
- Simulation/re-enactment in engineering simulators is standard ("tests and research"). [Y]

### 2.5 Drone survey of crash sites

- UK AAIB first used a drone at an accident site in **2014**; tasks: wreckage and site surveys, searching for wreckage, estimating heights of trees/objects, site safety assessments, **reconstructing flight paths**, supervising wreckage recovery. [D] https://www.gov.uk/government/publications/how-we-use-drones-at-air-accident-sites/how-we-use-drones-at-air-accident-sites
- Outputs: orthomosaic (example: 59 images from 50 m), 3D point cloud and mesh; measurements "up to an accuracy of 1 cm" from images at 40 m; flight "a matter of minutes", then "a few hours" processing; works in winds up to 20 kt; no rotor downwash disturbing debris. [D] same page (published 2018)
- AAIB flew drones at 23 sites in about 2 years. [A] ISASI paper snippet

---

## 3. Technology trends EASA cares about (challenge fuel)

### 3.1 AI / ML

- **AI Roadmap 2.0** published 10 May 2023: "human-centric approach"; covers safety, security, AI assurance, human factors, ethics. [D] https://www.easa.europa.eu/en/newsroom-and-events/news/easa-artificial-intelligence-roadmap-20-published
- **AI levels**: Level 1 = assistance to human; Level 2 = human-AI cooperation/collaboration (teaming); Level 3 = advanced automation. **Concept Paper Proposed Issue 03** released 3 Jun 2026 for comment until 12 Aug 2026, adds Level 3, reinforcement learning, symbolic AI. [D] https://www.easa.europa.eu/en/newsroom-and-events/news/easa-releases-latest-issue-its-concept-paper-artificial-intelligence
  - Level 3A (overridable) vs 3B (non-overridable). [A]
- **EASA's own AI for safety data** (R. Powel, Head of Safety Data Management, ICAO workshop 2025): [D] https://www.icao.int/sites/default/files/EURNAT/MeetingDocs/Safety%20workshops/2025%20Safety%20-%20ICAO%20workshop%20on%20use%20of%20artificial%20intelligence%20for%20safety%20data%20processing%20and%20analysis/5-EASA-AI-for-Safety-Data-Management.pdf
  - "Reporting doubled in the EASA Member States in 8 years", staffing did not.
  - Three modules: **A** Occurrence information extractor (topic extraction/summary, formatted narrative, mandatory field inference) — Q4/2025; **B** record-update difference highlighter — Q4/2025; **C** **ERCS classification** (propose KRA and loss-of-life category, barrier category, report-type detection, mapping RAT/ARMS) — Q2/2025.
  - EASA's own concerns: who changes the narrative at each stage; AI layers may "smooth the data to the extent that important elements are missed"; tools must work for rare accidents, not just the majority of incidents.
  - The slide also gives EASA-as-authority volumes (products, organisations, ECR contributions, 2024 reports) but the numbers were scrambled in text extraction: NOT VERIFIED.
- EASA AI Days 2025 agenda: Innovation Partnership Contracts on a Boeing auto-taxi AI system and a **Lufthansa LLM-based troubleshooting assistant**; panel on "Human oversight in Level 3 AI". [D] https://www.easa.europa.eu/en/downloads/141750/en
- **EASA AI Olympics 2026** (AI-based aviation systems showcase, AI Days Cologne 9–10 Sep 2026; capped at 50 entries). [A]
- Academic NLP on occurrence reports: transformer classifier can automate labelling "under the right conditions" (Jonk et al. 2023). [A] https://arxiv.org/abs/2301.05663

### 3.2 Flight data monitoring (FDM/FOQA)

- D4S fuses FDM from member airlines; guidance on unstable approaches from flight data. [D] D4S page
- Voepass final report: CENIPA found weaknesses in the operator's FDM in detecting the degradation; SR to ANAC to strengthen oversight of FDM. [D-sec] AeroCorner

### 3.3 Recorders and locating the aircraft

From Reg. (EU) 2015/2338 (amending 965/2012), EU text: [D] https://www.legislation.gov.uk/eur/2015/2338/annex

- **CVR 25 h**: CAT.IDE.A.185 — aeroplanes MCTOM > 27 000 kg first issued individual CofA on or after **1 Jan 2021**: retain last **25 hours**; otherwise 2 hours. [D]
  - Real check: SAS A320neo at Brussels had "over 2 hours" CVR audio (under 27 t, so 2 h rule). [D] AAIU
  - Separate rule: CVR alternate power source for > 27 t aeroplanes CofA on/after 5 Sep 2022. [A]
- **ULD on recorders**: CVR and FDR (if not deployable) must have an underwater locating device with minimum transmission time of **90 days** (by 16 Jun 2018). [D]
- **Low-frequency ULD 8.8 kHz ± 1 kHz** (CAT.IDE.A.285(f), by 1 Jan 2019) for aeroplanes MCTOM > 27 000 kg with MOPSC > 19, and all > 45 500 kg; exempt if routes always within 180 NM of shore or if CAT.GEN.MPA.210 means are fitted. [D]
- **CAT.GEN.MPA.210 "Location of an aircraft in distress"** ("robust and automatic means to accurately determine … the location of the point of end of flight"):
  - Original 2015 text: CofA on/after 1 Jan 2021. [D] Reg 2015/2338
  - **Amended by Implementing Reg. (EU) 2022/2203** (OJ L 293, 14.11.2022): from **1 Jan 2025**, for aeroplanes MCTOM > 27 000 kg with MOPSC > 19, and all > 45 500 kg, **first CofA on/after 1 Jan 2024**. Reason: ICAO Annex 6 Amendment 48 postponed Std 6.18.1 (manufacturer equipage delays; ATS/RCC communication infrastructure). [D] Spanish OJ text https://www.boe.es/doue/2022/293/L00003-00004.pdf
  - Means: ELT(DT), deployable recorder with ELT, or other; Czech CAA granted a temporary exemption Aug 2025. [A]
- **Recorder preservation**: recorders must not be disabled in flight; after an accident/serious incident, recorders deactivated after the flight and data not erased; operator preserves original data **60 days** unless the SIA directs otherwise. [D] Reg 2015/2338 (CAT.GEN.MPA.105/195)
- **GADSS** (ICAO): Aircraft tracking every **15 min or less**; **Autonomous Distress Tracking** once triggered transmits position **at least once per minute**, aim to locate the accident site **within 6 NM radius**; Post-Flight Localisation & Recovery (ELT, ULB, recorders). [D] https://skybrary.aero/articles/global-aeronautical-distress-and-safety-system-gadss
- Flight data recovery options in GADSS: **data streaming** (triggered transmission) or **ADFR (automatic deployable flight recorder with integrated ELT)**. [A] Airbus GADSS briefing snippet
- **ULB 37.5 kHz**, one pulse per second, **≥ 90 days** (was 30 days before AF447), detection range about **3–4 km**; AF447 FDR found at about **3 900 m**; about 40 commercial aircraft lost at sea since early 1970s, recorders recovered in most cases; AAIB towfish works to 1 km depth. 8.8 kHz created after AF447 for longer range. [D] https://www.gov.uk/government/publications/getting-to-the-bottom-of-aircraft-accidents/getting-to-the-bottom-of-aircraft-accidents
  - 8.8 kHz detection range figure: NOT VERIFIED (vendor claims only).
- **ELT**: 406 MHz digital burst detected by Cospas-Sarsat satellites (ID + position); 121.5 MHz analog homing for final DF; satellites stopped processing 121.5 MHz on **1 Feb 2009**. [A] NOAA / Canada snippets
- UAS recorders: AAIB's Airspeeder report recommended flight data recording for UAS. [A] (the AAIB news page did not mention it [D], so treat as unconfirmed)

### 3.4 New entrants and sustainability-linked hazards

- **UAS**: 27 UAS accidents in EASA States in 2025 [D] ASR 2026 summary; "Conflict with unauthorised UAS" is a Top Safety Topic [D]; counter-drone actions in EPAS 2026 [D].
- **Lithium battery fires**: Top Safety Topic; leading CAT risk = fire/smoke/pressurisation [D] ASR 2026; EPAS SI-9011 in-flight fires in inaccessible areas [D]; EASA SIB 2025-03 (27 May 2025) "Passenger and Crew Awareness on the Risks of Lithium Batteries" [D] cited in Danish AIB statement; content (e.g. "carry PEDs in the cabin") [A].
- **SAF / synthetic fuels**: SI-0060 out-of-spec SATF in operations. [D] EPAS 2026
- **Hydrogen / battery-electric / eVTOL accident investigation**: no EU investigation of a hydrogen-aircraft or certified eVTOL accident found: NOT FOUND. Expected investigative issues [Y]: thermal runaway propagation evidence is destroyed by fire; BMS data must be crash-protected; cryogenic H2 leaks leave no residue; high-voltage hazards for first responders; distributed electric propulsion needs new recorder parameter lists.
- **GNSS interference**: Top Safety Topic. [D] ASR 2026 summary

---

## 4. EASA, EUROAVIA and student challenges

- **GEN Days**: "EASA, together with EUROAVIA, proudly presents the first edition of GEN Days" — at EASA, Cologne, late Nov 2025 (26–28 Nov per programme); themes **Emerging Technologies & Automation; Drones & New Airspace Users; Sustainable Aviation; Air Operations & Safety**; linked to EASA's **Future Workforce Challenges** initiative and ICAO NGAP; no accident-investigation content listed. [D] https://euroavia.eu/event/gen-days/ and https://euroavia.eu/gen-days/
  - About 50 students attended. [A] LinkedIn snippet
- EASA hackathon for students on accident investigation: **NOT FOUND**. EASA "Data4Safety hackathon": NOT FOUND. EASA student challenge: NOT FOUND (only the AI Olympics showcase for industry [A], and a past GA Safety Award closed 2019 [A]).
- EASA has run a student project with RMIT (Australia) on safety promotion via Riipen. [A] https://riipen.com/blog/improved-aviation-safety-promotion-and-enhanced-product-development-a-european-union-aviation-safety-agency-easa-riipen-case-study
- Inference [Y]: EASA's link to EUROAVIA is workforce/talent; their GEN Days themes are a good prior for the Ideathon jury's interests (automation/AI, drones, sustainability, safety).

---

## 5. Case studies (European or EASA-involved, 2024–2026)

### Case 1 — SAS A320neo take-off attempt from a taxiway, Brussels (EBBR), 5 Feb 2026 — Serious incident (AAIU(Be))
Source: AAIU-2026-02-05-01 preliminary, issued 6 Mar 2026 [D] https://mobilit.belgium.be/sites/default/files/documents/publications/2026/AAIU-2026-02-05-01-PRELIMINARY.pdf
- Night, winter; crew delayed all day (de-icing, slots), CTOT pressure, 42-min turnaround, difficult boarding. Cleared for take-off RWY 07R; aircraft lined up on **taxiway E1**, reached **100 kt**, F/O noticed ("No, this is wrong… Stop, stop"), reject at **127 kt IAS**; stopped near V1/C1, nose gear a few metres from runway guard lights; fenced works area and fuel station (65 m) nearby. 152 pax + 6 crew; no injuries, no damage.
- Classification logic: high probability of accident; "aborted take-off from a taxiway" is explicitly in Reg 996/2010 Annex examples of serious incidents. Category NAV.
- Crew mistook taxiway Outer 10 for C6 after the C6 stop bar went out ("And then the red line disappeared"); E1 information-sign light was **not operational**; tower A-SMGCS has a "departure from the wrong runway" safety net; ATCO noticed only after the reject.
- Immediate safety action: SAS acquiring **Airport Moving Map**; AAIU supports it. Further focus: A-SMGCS performance, aerodrome lighting/signage, "potential use of additional on-board or ground-based systems".
- EASA appointed a technical adviser. Recorders read out at BEA.
- Why it matters [Y]: host-country case, fresh, final report due ~Feb 2027; ideal "design a mitigation/investigation tool" seed (wrong-surface take-off alerting, e.g. ROPS/"runway alignment" check, A-SMGCS conformance).

### Case 2 — Marathon Airlines E195 (for Air Serbia), OY-GDC, Belgrade, 18 Feb 2024 — Accident (Serbian CINS)
Source: final report, Aug 2025 [D] https://pkbwl.gov.pl/wp-content/uploads/2024/02/2024-0005_Final-report_OY-GDC-1.pdf
- Lined up at D5 instead of planned D6; ATC told crew the D5 distance and recommended returning to D6, but ATC cannot forbid take-off (SERA.2015, PIC authority); crew took off; aircraft struck the ILS localizer antenna (ILS downgraded CAT III → CAT I), fuel leak from left wing root, returned and landed; parked at a contact stand while fuel leaked.
- **Direct cause**: take-off from an intersection without sufficient TODA. **Indirect**: undisciplined taxi communication; wrong runway entered in the EFB performance app; FMS not updated — "FLEX 33" left instead of no-flex TOGA, FLAPS 1 instead of FLAPS 4.
- SRs: extraordinary proficiency checks for captain and F/O (to Italian and Hellenic CAAs + operator); OM revisions (runway-change and line-up checklist) — done during investigation; airport emergency plan to mandate isolated stand — done.
- EASA adviser attended FDR/CVR read-out at BEA. [D] ASRR 2025
- Teaching point [Y]: some SRs target individuals (proficiency checks), which sits uneasily with the "no blame" and SMART guidance; a team can propose systemic SRs (e.g. TOPMS / take-off performance monitoring, EFB cross-checks against FMS position). "Erroneous take-off parameters" is an EASA Top Safety Topic [D].

### Case 3 — Swiss A220-300 HB-JCD, engine failure and cabin smoke, near Graz, 23 Dec 2024 — Accident (SUB → STSB)
Source: STSB status report (anniversary) [D] https://www.sust-stsb.admin.ch/r/inhalte/AV-berichte/HB-JCD_StatB_e.pdf
- FL400, left PW1500G failed, smoke entered cabin and cockpit, diversion to Graz, emergency evacuation on runway; a cabin crew member died on 30 Dec 2024.
- Investigation lead transferred from Austria's SUB to Switzerland's STSB under Art. 6(2) Reg 996/2010 (request 9 Apr 2025, accepted 11 Apr 2025). Preliminary report 17 Mar 2025 per Annex 13 Rec. 5.4.6.
- Work streams: engine teardown with Pratt & Whitney (USA); how smoke reached the cabin; **Protective Breathing Equipment (PBE)** examined for defects; emergency procedures in cockpit and cabin; systemic: engine, smoke hoods, procedures, manuals.
- Contested: a HAW Hamburg paper criticises the investigation's handling of the bleed-air smoke path. [A] (advocacy, not official)
- Why it matters [Y]: fire/smoke is the #1 CAT risk area in ASR 2026; cabin-safety equipment; cross-border handover; an investigation that will exceed 12 months.

### Case 4 — Leonardo AW169 G-VSKP, Leicester, 27 Oct 2018 — fatal accident (UK AAIB, AAR 1/2023)
Source: [D] https://www.gov.uk/aaib-reports/aircraft-accident-report-aar-1-slash-2023-leonardo-aw169-g-vskp ; SR document updated 27 May 2025 [D] https://assets.publishing.service.gov.uk/media/667299ecf92bc4be25da7dd0/G-VSKP_Safety_Recommendation_Document.pdf
- Tail rotor duplex bearing seized (lubrication breakdown, surface-initiated rolling contact fatigue under combined axial and bending loads) → loss of tail rotor pitch control → unrecoverable yaw → impact and post-crash fire; 5 fatalities.
- Contributory: load-survey results not shared with the bearing supplier; CS-29 lacks explicit rolling-contact-fatigue requirements; no inspection of removed critical-part bearings; system failure sequences not fully considered in certification.
- **8 SRs, all to EASA** (CS-29). Statuses (May 2025): several "Closed – Disagreement" or "Closed – Partial agreement" with AAIB assessment **"Not Adequate"** (e.g. 2023-018, 2023-021, 2023-023, 2023-024); 2023-019 and 2023-022 open/partially adequate; 2023-020 closed/adequate. EASA's reply to 2023-018: the applicant is already responsible under Part 21 (21.A.20), so no new prescriptive CS requirement. [D]
- Also 16 Service Bulletins and 9 EASA ADs on AW169/AW189. [D]
- Why it matters [Y]: textbook example of the SR "dialogue" and of EASA's certification role vs. AIB view; great for an "SR effectiveness" challenge.

### Case 5 — Voepass ATR 72-500 PS-VPB, Vinhedo (Brazil), 9 Aug 2024 — fatal LOC-I in icing (CENIPA)
Source: [D-sec] https://aerocorner.com/news/voepass-atr-72-crash-investigation/ ; final report PDF hosted by ICAO [A] https://www.icao.int/sites/default/files/SAM/AIG/Documents/Final%20Reports/BRA09AGO2024RF.pdf
- 62 fatalities; final report released 23 Jul 2026 with 19 contributing factors. [D-sec]
- Severe icing with degraded de-icing; crew cycled de-icing; eight low-speed warnings without recovery; nose-up on stall leading to ~68 s flat spin; right-wing de-icing fault reported verbally on three flights but never logged ("culture of informality"); weak FDM; regulator did not act on earlier audit findings. [D-sec]
- SRs: **EASA with ATR to review the "degraded performance" alert logic**; ANAC to strengthen oversight of FDM and risk management. [D-sec]
- EASA technical adviser went on site with the French go-team (BEA + ATR). [D] ASRR 2025
- Why it matters [Y]: EASA as State-of-Design authority receiving SRs from a non-EU SIA; LOC-I (Top risk "aircraft upset"); FDM precursor detection.

### Case 6 — SunExpress B737-8 TC-SOM, power bank thermal runaway, Copenhagen, 20 Dec 2025 — Serious incident (Danish AIB)
Source: statement 2025-614, published 4 May 2026 [D] https://havarikommissionen.dk/undersoegelsesresultater/soeg-i-luftfart/2026/statement-2025-614
- During pushback, a power bank in a passenger's trouser pocket went into thermal runaway; thrown on the floor; SCCM discharged halon after ~15–20 s, then submerged the device in water in a bin in the aft lavatory; engines shut down; RFFS called. One serious injury (14-year-old, ~10 cm second-degree burn). Passengers standing/shouting hampered the crew.
- AIB closed the investigation after the preliminary phase, no SRs; references EASA SIB 2025-03.
- Related: Dutch Safety Board on an Air France A220 evacuation after a power-bank fire, 12 Jun 2025. [A]
- Why it matters [Y]: cheap, high-frequency, sustainability-adjacent (batteries everywhere); detection/containment concept challenge.

### Case 7 — Alauda Airspeeder Mk II (95 kg UAS), Goodwood, 4 Jul 2019 — UAS accident (UK AAIB, Feb 2021)
Source: [D] https://www.gov.uk/government/news/aaib-report-alauda-airspeeder-mk-ii-loss-of-control-resulting-in-a-fly-away-and-eventual-crash
- Loss of control in a demo; **kill switch had no effect**; climbed to ~8 000 ft into a Gatwick holding area; crashed 40 m from occupied houses, 700 m outside the operating area after battery depletion.
- Not designed/built/tested to any recognisable standards; safety case errors; regulator granted exemption without inspecting. **15 SRs** on airworthiness standards, safety management and oversight.
- SR to EASA on design/production/maintenance standards for UAS above 80 J; flight data recording on UAS. [A] (secondary snippets)
- Why it matters [Y]: prototype for "how do we investigate eVTOL/UAS accidents" — no recorder, no crew, data on the ground station.

### Case 8 — Swiftair B737-400SF EC-MFE (for DHL), Vilnius, 25 Nov 2024 — fatal accident (Lithuania)
- Crashed 0.87 NM short of runway on approach; 1 fatality; EASA adviser at BFU FDR read-out. [D] ASRR 2025
- Interim report (31 Mar 2025): flaps retracted; crew on wrong ATC frequency after handoff. [A] Lithuanian SIA page snippet (page blocked, HTTP 403)
- Parallel criminal investigation: prosecutors say human error, sought to question pilot as a suspect. [A] Reuters snippet
- Why it matters [Y]: illustrates the tension between safety investigation (Art. 14 protection) and judicial investigation.

### Case 9 — Two Robinson R44, mid-air collision, Eura (Finland), 17 May 2025 — fatal (Otkes)
- 5 fatalities; helicopters from Tallinn, registered in Estonia and Austria; flew side by side; Otkes interim report published. [A] news snippets
- ASR 2026 confirms "a mid-air collision involving two helicopters caused five fatalities" in 2025. [D] ASR 2026 summary
- Why it matters [Y]: GA formation flying, electronic conspicuity, mid-air = Top Safety Topic.

### Case 10 — JAL A350 JA13XJ / JCG Dash 8 JA722A, Tokyo Haneda, 2 Jan 2024 — runway collision (JTSB)
- 5 of 6 Dash 8 crew died; all 379 on the A350 evacuated. EASA adviser travelled on site with the BEA ACCREP and EU go-team. [D] ASRR 2025
- JTSB interim report 25 Dec 2024. [A] (PDF too large to fetch)
- Why it matters [Y]: runway incursion + evacuation of a composite-fuselage aircraft; a strong "cabin survivability" case.

---

## 6. Predictions: what the EASA challenge could be

General [Y]: The title "EASA: Accident Investigation" plus a ~5-hour slot and "conceptual solution" judging suggests either (a) a **mini-investigation** of a supplied scenario, or (b) a **concept for a tool/process that improves investigations or the learning loop**. Because EASA is not itself an investigator (Art. 8 adviser role), a well-informed EASA jury will reward teams that place their idea correctly in the EU system (SIA leads; EASA advises, receives SRs, runs ECR/ERCS/D4S/EPAS). Sustainability must be argued in every answer.

Ranked by my estimated likelihood [Y]:

### P1 — "Here is an accident scenario (data pack). Investigate it: reconstruct, find causes, issue safety recommendations." (most likely)
- Jury expects: correct classification (accident / serious incident), Annex 13 report skeleton, an evidence-based timeline, a systemic model (Swiss cheese/HFACS/CAST/bow-tie), separation of findings vs causes vs contributing factors, **SMART SRs with one addressee each**, no blame language, and awareness of who acts (SIA vs EASA vs NAA vs operator vs manufacturer).
- Numbers to have ready: 30-day preliminary (Rec. 5.4.6), 12-month final / anniversary interim statement, 90-day SR reply + 60-day adequacy (Art. 18), EASA first reply ≤ 90 days, ISIRC every 6 weeks, CVR 2 h vs 25 h, recorder data preservation 60 days, 8.8 kHz/37.5 kHz ULDs and 90 days, ELT 406/121.5 MHz.
- Strong answer sketch: 1-slide timeline; Swiss-cheese/bow-tie graphic mapped to the 8 ERCS barriers; ERCS score of the event (e.g. "M2" style); 4–6 SRs (mix of operator, NAA, EASA certification, airport/ANSP), each tagged SRUR-candidate or not; a "what we would still need to know" list (shows investigative honesty); sustainability: recommendations that avoid fleet-wide groundings or heavy retrofits when a software/procedure fix suffices, digital-first investigation (remote read-outs, fewer site trips), and environmental clean-up of crash sites (fuel, composites, batteries).
- Likely scenario seeds: wrong-surface take-off (Brussels 2026), erroneous take-off parameters (Belgrade 2024), smoke in cabin (Graz 2024), power-bank fire (Copenhagen 2025), icing LOC-I (Voepass), UAS fly-away (Goodwood).

### P2 — "Use AI/data to detect accident precursors earlier / make occurrence data useful" (very plausible; EASA's AI Roadmap + D4S + 376/2014 workload problem)
- Jury expects: knowledge of ECCAIRS 2/ECR/ADREP, ERCS, D4S, Just Culture and data protection (Art. 14 / 376/2014), EASA AI levels (1/2/3) and trustworthiness (explainability, human oversight), and awareness that reports doubled in 8 years.
- Numbers: 72 h reporting, ECR transfer within 30 days, ERCS letters/digits and barrier weights, 10 KRAs, D4S operational phase after 2026.
- Strong answer sketch: Level-1/2 AI assistant that (i) pre-codes ADREP fields and proposes ERCS KRA/barriers with confidence and rationale (EASA Module A–C), (ii) clusters narratives across States to flag emerging safety issues for the EPAS Safety Risk Portfolio, (iii) fuses FDM exceedances with reports to find "near-accident" precursors; human analyst stays in the loop; guard against "smoothing" rare events (EASA's own worry) with an anomaly/novelty detector; federated learning so data stays national (privacy + less data movement). Sustainability: compute-light models, fewer manual hours; can also mine fuel/SAF-related occurrences (SI-0060).

### P3 — "Find the wreckage and the data faster" (locating aircraft/recorders, timely data recovery, crash-site survey)
- Jury expects: GADSS (15-min tracking, ADT 1/min, 6 NM), CAT.GEN.MPA.210 (2025, CofA ≥ 2024, > 27 t & > 19 seats or > 45.5 t), ULD 90 days, 8.8 kHz LF ULD, 37.5 kHz range 3–4 km, ADFR vs streaming trade-off, satellite bandwidth cost, privacy of CVR (Art. 14), survivability.
- Strong answer sketch: tiered concept — (1) triggered transmission of a compact "last-minutes" FDR snapshot on distress triggers, (2) deployable ELT/recorder for over-water, (3) drone swarm + photogrammetry (1 cm @ 40 m) for land sites with automatic debris mapping, (4) AUV with LF hydrophone for sea. Show search-area math (e.g. 6 NM radius ≈ 390 km² vs 37.5 kHz detection radius 3–4 km). Sustainability: shorter ship/aircraft search time → large fuel/CO2 savings; reusable drones instead of helicopters; avoid seabed disturbance.

### P4 — "Design the investigation process for new aircraft: eVTOL / UAS / hydrogen / battery-electric"
- Jury expects: what changes vs. classic Annex 13 work (no crew, data in ground control station, cloud logs, BMS data, high-voltage and H2 hazards, rapid software updates, U-space data); EASA categories of UAS operations; ASR 2026 UAS accident count (27); Goodwood lessons (kill switch, standards, recorders).
- Strong answer sketch: "Investigation-by-design" requirements: mandatory crash-protected data logger with minimum parameter list for UAS above a mass/energy threshold; cloud log preservation order within hours; first-responder protocol for HV batteries and H2; thermal-runaway forensic kit; digital twin of the vehicle supplied at certification to replay logs. Sustainability: enables safe adoption of zero-emission aircraft; battery/H2 failure data feeds design improvement.

### P5 — "Close the loop: make safety recommendations more effective" (SR lifecycle, ECR/SRIS)
- Jury expects: Art. 17/18 timelines, ENCASIA WG6 taxonomy, SMART, SRUR/SRGC, ASRR stats (40 SRs in 2024; 97 replies; 36 % pending assessment; disagreements like G-VSKP).
- Strong answer sketch: an SR "digital thread" — each SR linked to findings, ERCS risk, EPAS safety issue and measurable SPIs; dashboard tracking effectiveness after closure (did occurrence rates change?); NLP to spot similar SRs across States (SRUR candidates); early-dialogue workflow before issuance. Sustainability: fewer redundant actions, paperless, prioritises effort where risk reduction per euro is highest.

### P6 — "Runway safety: prevent wrong-surface take-offs / take-off performance errors" (host-country flavour)
- Jury expects: Brussels SAS43M facts, Belgrade OY-GDC facts, A-SMGCS safety nets, stop bars (auto re-illuminate after 89 s at EBBR [D] AAIU), AMM, EFB performance cross-checks, TOPMS.
- Strong answer sketch: on-board "runway conformance" check (GNSS + airport database + heading + width + lighting pattern, possibly camera-based) that alerts before thrust set; ground-side A-SMGCS conformance alert to ATCO; EFB-FMS-position consistency check for take-off data. Sustainability: avoids taxiway damage/rebuilds and fleet groundings; software solution on existing hardware.

### P7 — "Cabin fire / smoke investigation and survivability" (lithium batteries, bleed-air smoke, PBE)
- Jury expects: ASR 2026 #1 CAT risk fire/smoke; SI-9011; SIB 2025-03; HB-JCD and TC-SOM facts.
- Strong answer sketch: cabin thermal/smoke sensor network with event recording for investigators (where/when did smoke start), standard containment kit, PBE health monitoring; investigation protocol for battery remnants (CT scanning). Sustainability: preventing aircraft write-offs; battery recycling logistics.

### Cross-cutting sustainability angles to reuse [Y]
- Search/rescue and recovery operations burn a lot of fuel; faster location = less emissions.
- Crash sites are contamination events (fuel, hydraulic fluid, composites fibres, Li batteries, PFAS firefighting foam).
- New propulsion (SAF, H2, batteries) creates new failure modes; good investigation capability is an enabler of decarbonisation.
- Digital investigation (remote read-out, cloud collaboration, 3D models) cuts travel.
- Proportionate SRs avoid unnecessary retrofits and scrapping.

---

## 7. Cheat-sheet: key numbers and definitions

Definitions (EU Reg 996/2010 Art. 2) [D]
- Accident: fatal/serious injury, or damage needing major repair, or aircraft missing/inaccessible.
- Serious incident: incident with "a high probability of an accident". Example in the Annex list: aborted take-off on a taxiway [D AAIU]; runway incursions severity A, overruns/excursions, system failures, flight outside envelope, multiple redundant navigation system failure [D ASRR 2025 Annex B].
- Incident: any other occurrence affecting or could affect safety.
- Fatal injury: death within 30 days.
- Serious injury: e.g. hospitalisation > 48 h, fractures, certain burns [D partial]; full criteria NOT VERIFIED.
- Time window of an accident (boarding to disembarkation; for unmanned, ready-to-move to rest) [Y] — NOT VERIFIED this session.

Timelines
- Notify SIA: "without delay" (Art. 9). [D]
- Preliminary report: within 30 days when high public attention (Annex 13 Rec. 5.4.6). [D via AAIU]
- Final report: within 12 months where possible; interim statement at each anniversary (Art. 16; Art. 16(7)). [D]
- SR reply by addressee: 90 days; SIA adequacy decision: 60 days (Art. 18). [D]
- EASA first reply: ≤ 90 calendar days; ISIRC every 6 weeks. [D]
- Draft final report comments from States: 60 days. [A]
- Occurrence report (376/2014): 72 h individuals and organisations; ECR transfer 30 days [D]; organisation preliminary analysis 30 days, final 3 months [A].
- Operator preserves recorder data: 60 days unless SIA directs otherwise. [D]

Recorders and locators (EU Part-CAT) [D unless tagged]
- CVR: 25 h for aeroplanes MCTOM > 27 t with first CofA ≥ 1 Jan 2021; otherwise 2 h.
- ULD on FDR/CVR: ≥ 90 days transmission (by 16 Jun 2018).
- LF ULD: 8.8 kHz ± 1 kHz (by 1 Jan 2019) for > 27 t & > 19 seats, or > 45.5 t; exemption within 180 NM of shore or with MPA.210 means.
- Standard ULB: 37.5 kHz, 1 pulse/s, ≥ 90 days (was 30), range 3–4 km [D gov.uk].
- Location of aircraft in distress (CAT.GEN.MPA.210): from 1 Jan 2025, > 27 t & > 19 seats or > 45.5 t, first CofA ≥ 1 Jan 2024 [D Reg 2022/2203].
- GADSS: tracking ≤ 15 min; ADT ≥ 1 position/min; locate within 6 NM [D SKYbrary].
- ELT: 406 MHz (satellite, digital ID/position), 121.5 MHz (homing); satellites stopped 121.5 MHz on 1 Feb 2009 [A].
- FDR minimum duration 25 h for large aeroplanes [Y] — NOT VERIFIED this session.

ERCS [D]
- Severity A/E/I/M/S/X; 10 KRAs; 8 barriers with weights 5/2/3/2/3/1/1/1 (max 18) → barrier score 0–9; score like "M2"; RED/YELLOW/GREEN; X0 = 1 000 000.

People and bodies
- SIA / AIB: national (AAIU(Be), BEA, BFU, AAIB, STSB, SHK, Otkes…); ENCASIA = their EU network. [D]
- EASA: adviser to IIC (Art. 8), SR addressee, ECCAIRS 2/ECR operator, ERCS, D4S, EPAS, ASR. [D]
- ACCREP = accredited representative of a participating State; advisers assist them. [D/Y]
- SRUR = Union-wide relevance (ENCASIA, Art. 7(g)); SRGC = global concern (ICAO Doc 9756). [D]

EASA documents to name-drop [D]
- EPAS 2026 (Vol I/II/III, Safety Risk Portfolios, SI-9011, SI-0060).
- Annual Safety Review 2026 (Top Safety Topics list in §1.5).
- Annual Safety Recommendations Review 2025 (18th edition).
- AI Roadmap 2.0 (May 2023); AI Concept Paper Proposed Issue 03 (Jun 2026, Level 3).
- SIB 2025-03 lithium batteries (27 May 2025).

---

## 8. Five-hour sprint playbook (any of P1–P7) [Y]

- 0:00–0:20 Read brief; classify; define the user (SIA? EASA? operator?); write the one-sentence problem.
- 0:20–1:30 Facts/timeline or system concept; split work: investigator, data/AI, systems/hardware, sustainability+slides.
- 1:30–3:00 Analysis/design: model (bow-tie/CAST) or architecture; quantify one thing (search area, time saved, ERCS score, FTE hours saved).
- 3:00–4:00 SMART SRs or requirements list; feasibility (TRL, cost, certification path: who approves it?); sustainability KPI.
- 4:00–5:00 Slides: problem → evidence → concept → numbers → regulation fit (996/2010, 376/2014, Part-CAT) → sustainability → roadmap; rehearse 2 min.
- Language rules: say "causal and contributing factors", "safety recommendation to …", never "the pilot was guilty".

---

## 9. Open items / things I could not verify

- Ideathon 2026 sponsor list and whether EASA is literally the sponsor: NOT FOUND on public pages.
- Any EASA or EUROAVIA accident-investigation hackathon: NOT FOUND.
- Annex 13 primary text (90-day SR reply in Annex 13 itself, 60-day draft comments, ADREP 30-day preliminary): [A] only.
- Full serious-injury definition and accident time window wording: NOT VERIFIED.
- FDR 25-h duration requirement: NOT VERIFIED.
- 8.8 kHz ULD detection range: NOT VERIFIED.
- Lithuanian EC-MFE interim report content and Haneda JTSB interim content: [A] only.
- Voepass details rely on a secondary source (AeroCorner) [D-sec]; CENIPA PDF not opened.
- EASA SIB 2025-03 text not opened (tool down); only its existence/date [D].
- Reg 376/2014 30-day/3-month organisation analysis deadlines: [A].
