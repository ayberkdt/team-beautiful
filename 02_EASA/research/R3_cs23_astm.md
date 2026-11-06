# R3 — CS-23 / ASTM / FAR benchmark for a retrofit canopy alert

- read by: subagent R3
- date read: 2026-11-04
- Tags: **[D-ag]** = read in the source this session (paragraph given); **[Y]** = my inference, not stated in the source.

## Sources (all downloaded to `D:\tmp_ideathon\easa\dl\cert\`)

| File | URL | Version / date |
|---|---|---|
| EAR_CS23_A6_AMC5.pdf | https://www.easa.europa.eu/en/downloads/143630/en | Easy Access Rules CS-23, **CS Amendment 6, AMC/GM Issue 5** (ED Decision 2026/003/R), published May 2026 |
| EAR_CS23_A4.pdf | https://www.easa.europa.eu/en/downloads/47182/en | Easy Access Rules CS-23 **Amendment 4** (legacy, Jun 2018 EAR) |
| TCDS_EASA_A620_ExtraNG_AW.pdf | https://www.easa.europa.eu/en/downloads/104842/en | TCDS EASA.A.620 Extra NG, Issue 04, 02 Dec 2020 |
| tcds_44276.pdf | https://www.easa.europa.eu/en/downloads/44276/en | TCDSN (noise) EASA.IM.A.022 DA 40, Issue 2, 26 Mar 2025 |
| ecfr_25_783.xml | https://www.ecfr.gov/api/versioner/v1/full/2026-10-01/title-14.xml?part=25&section=25.783 | 14 CFR 25.783 as of 2026-10-01 |
| ecfr_23_783_2017.xml, ecfr_23_1322_2017.xml | eCFR versioner, date 2017-05-01 | legacy 14 CFR 23.783 / 23.1322 (pre-Amdt 23-64) |
| ecfr_23_2605.xml | eCFR versioner, date 2026-10-01 | 14 CFR 23.2605 |
| astm_*.html | https://store.astm.org/f3061_f3061m-24a.html , f3117_f3117m-24a, f3083_f3083m-20a, f3264-24, f3232_f3232m-25 | ASTM store abstract pages (Scope only) |

Note: the first CS-23 file I fetched as "Amdt 4" (download 47179) was in fact Amendment 3; it was deleted and replaced with 47182, whose header reads "Amendment 4". [D-ag]

---

## 1. Certification basis of the candidate aircraft

- **Extra NG**: EASA TC date 11 Oct 2019; reference date 11 Oct 2016; airworthiness requirements **"CS-23 incl. Amdt 4, effective July 17th, 2015"**; category Normal + Aerobatic; MTOW 950 kg; tandem two-seat, single engine, **tractor propeller**; SC-E23.0863-01 (smoke system); ELOS-B23-0207-01 (stall warning removal), ELOS-D23-0785d-01, ELOS-CS23 777/781 (TCDS EASA.A.620 Iss. 04, A.II and A.III). [D-ag]
  - → For the retrofit, the **legacy CS-23 Amdt 4 paragraphs (23.783, 23.807, 23.1309, 23.1322...) are the type-certification basis**, not CS 23.2xxx. [Y, follows from 21.A.95(b)1 "type-certification basis ... incorporated by reference in the type-certificate"]
  - ELA1 (≤1 200 kg, not complex) [Y from MTOW 950 kg + Art. 1(2)(i) — see R3_part21_changes_csstan.md].
- **DA 40**: noise TCDS EASA.IM.A.022 Iss. 2 lists TC holder **Diamond Aircraft Industries Inc., London, Ontario (Canada)** and take-off masses of 1 150 kg, 1 280 kg and 1 310 kg (MÄM 40-662) depending on variant/mod. [D-ag]
  - The "IM" prefix and Canadian holder suggest an imported (validated) product → minor changes may involve the State of Design authority under the EU–Canada arrangement. [Y — airworthiness TCDS EASA.A.022 and its certification basis **NOT read**]
  - ELA1 for the 1 150 kg variants, ELA2 for 1 280/1 310 kg variants [Y].

## 2. CS-23 Amendment 6 (objective-based) — requirements a canopy alert touches

| CS 23 point | Content (paraphrase; short quotes) | Tag |
|---|---|---|
| **CS 23.2250(e)** Design and construction principles | "Doors, canopies, and exits must be protected against inadvertent opening in flight, unless shown to create no hazard, when opened in flight." — **the only CS-23 Amdt 6 objective rule that names canopies + inadvertent opening.** | [D-ag] |
| AMC1 23.2250 (ED 2026/003/R) | MoC: ASTM F3264 §6.11; **F3061/F3061M-24a**; F3232/F3232M-25; F3114-21; F3380-19; F3408/F3408M-21 | [D-ag] |
| AMC2 23.2250 (CS-23 Amdt 4 mapping) | includes **23.783(b), (c)(1), (e) Doors**, 23.807(d)(2) Emergency exits, 23.775 windshields | [D-ag] |
| **CS 23.2315** Means of egress and emergency exits | (a)(2) means of egress "readily located and opened from the inside and outside"; **(b) "Aeroplanes approved for aerobatics must have a means to egress the aeroplane in flight."** → any latch sensor must not impede canopy jettison/opening. | [D-ag]; consequence [Y] |
| AMC1 23.2315 | F3264 §7.4; F3061/F3061M-24a; **F3083/F3083M-20a** (Emergency conditions, occupant safety & accommodations) | [D-ag] |
| AMC2 23.2315 | 23.783(a),(b),(c)(2)-(6),(d),(f),(g); 23.805; 23.807 ... | [D-ag] |
| AMC3 23.2315 (CS-VLA) | VLA.783 Exits, VLA.807 | [D-ag] |
| CS 23.2320(a)(3) | protect occupants from breakage of "windshields, windows, and canopies" | [D-ag] |
| **CS 23.2500(b)** | equipment required by TC/airspace/operating rules **or "whose improper functioning would lead to a hazard"** must perform intended function throughout envelope | [D-ag] |
| AMC1 23.2500 | F3264 §9.1; F3231-24, F3235-22, F3232-25, F3233-23b, F3229-23a, F3064-21, F3066-18, **F3117/F3117M-24a**, F3120-20, F3408-21; remark: F3061-24a §4.4.2 system-level verification "usually not acceptable" | [D-ag] |
| AMC2 23.2500 (Amdt 4 mapping) | 23.1301, 23.1309(a), 23.1351(b),(e),(f),(g), 23.1357, 23.1361, 23.1367 ... | [D-ag] |
| CS 23.2505 | installed per equipment limitations | [D-ag] |
| **CS 23.2510(a)** | catastrophic FC extremely improbable; hazardous extremely remote; major remote. (b) systems not covered by 23.2500 must not cause a hazard | [D-ag] |
| AMC1 23.2510 | F3264 §9.3; F3233-23b; **F3309/F3309M-24a (Simplified safety assessment)**; F3230-25 (Safety assessment); F3061-24a remark | [D-ag] |
| AMC2 23.2510 | 23.1309 etc. | [D-ag] |
| CS 23.2600(b) | controls/displays so crew can monitor; "must minimise flight crew errors" | [D-ag] |
| AMC1 23.2600 | F3264 §10.1; F3061-24a; F3232-25; F3062-20; F3063-21; F3064-21; F3114-21; F3408-21; remark on F3117-24a (hydrophobic coating) | [D-ag] |
| **CS 23.2605** Installation and operation information | (a) labelling; **(b) discernible means of providing ... "warnings, cautions, and normal indications"**; **(c) unsafe system condition info "in a timely manner" and "clear enough to avoid likely crew member errors"**; (d) safety equipment identifiable | [D-ag] |
| AMC1 23.2605 | F3264 §10.2; F3061-24a; F3232-25; F3233-23b; F3231-24; F3062-20; F3063-21; F3064-21; **F3117/F3117M-24a**; F3120-20; F3408-21 | [D-ag] |
| **AMC2 23.2605 (Amdt 4 mapping)** | includes **23.783(e)(3) Doors** and **23.1322 Warning, caution and advisory lights**, 23.703 take-off warning, 23.1309(d) | [D-ag] |
| AMC3 23.2605 (CS-VLA) | **VLA.783 Doors**, VLA.1322 | [D-ag] |
| CS 23.2610 | placards/markings, AFM must include marking/placard info (c) | [D-ag] |
| AMC1 23.2610 | F3264 §10.3; F3061-24a; F3063-21; F3117-24a; F3120-20; F3408-21 | [D-ag] |
| GM2 23.2010 | AMC1 = consensus standards at listed revisions; applicant must identify applicable content and seek EASA agreement ("building-block flexibility"); EASA accepted **ASTM F3264-24** | [D-ag] |
| GM3 23.2010 | table of ASTM F44 standards with revisions Issue 4 vs Issue 5 (PDF text extraction of this table was column-garbled; revisions above taken from the per-paragraph AMC1 lists instead) | [D-ag] |

**Mapping conclusion** [Y]: Under Amdt 6 a canopy alert is shown against **CS 23.2250(e)** (prevent inadvertent opening / show no hazard), **CS 23.2315(b)** (do not compromise in-flight egress), **CS 23.2500/2510** (function + safety assessment) and **CS 23.2605(b),(c)** (timely, unambiguous warning). EASA's own Amdt-4 cross-reference puts the old door-warning rule 23.783(e)(3) under 23.2605 and 23.783(e) under 23.2250.

## 3. Legacy CS-23 Amendment 4 (= Extra NG cert basis)

- **CS 23.783(c)(1)**: each external passenger or crew door must have means to lock and safeguard against inadvertent opening in flight "by persons, by cargo, or as a result of mechanical failure". [D-ag]
- **CS 23.783(e)** applies to "each external door on a commuter category aeroplane, each external door **forward of any engine or propeller** on a normal, utility, or aerobatic category aeroplane, and each door of the pressure vessel": (e)(1) lock/safeguard incl. single structural element failure; (e)(2) direct visual inspection of locking mechanism; **(e)(3) "a visual warning means to signal a flight-crew member if the external door is not fully closed and locked"**, erroneous "closed and locked" indication improbable for doors whose initial opening movement is not inward. [D-ag]
  - Extra NG and DA 40 have tractor propellers, so their canopies are **aft** of the propeller → 23.783(e)(3) **does not mandate** a warning on these types; the retrofit is a voluntary safety enhancement → "non-required equipment" for MEL/defect purposes unless the change itself makes it required. [Y]
  - Whether a canopy counts as an "external door" under 23.783 is not defined in the text read. [Y — NOT VERIFIED]
- **CS 23.807(a)(1)** excludes "aeroplanes with canopies" from the opposite-side emergency exit rule; **(b)** emergency exits may be "canopies"; **(b)(5)** aerobatic category: allow each occupant to abandon the aeroplane at any speed between VSO and VD; (c) proper functioning shown by tests. [D-ag]
- **CS 23.1309(a)(1)(ii)**: equipment must not adversely affect other equipment "unless there is a means to inform the pilot"; (a)(2) single-engine: minimise hazards from probable malfunction; **(b)(3)** "Warning information must be provided to alert the crew to unsafe system operating conditions", designed to minimise crew errors. [D-ag]
- **CS 23.1322**: if installed, lights must be (a) **red** warning (hazard, may require immediate corrective action), (b) **amber** caution (possible need for future corrective action), (c) **green** safe operation, (d) any other colour incl. white if sufficiently different, (e) effective under all probable cockpit lighting. [D-ag]
- AMC 23.783(b): only covers door location hazards (hot surfaces, sharp objects). No AMC on door indication found in Amdt 4. [D-ag]

## 4. FAA equivalents

- 14 CFR 23.783 (eCFR 2017-05-01 point-in-time, pre Amdt 23-64): text identical in substance to CS 23.783 incl. (e)(3) "visual warning means ... not fully closed and locked". [D-ag]
- 14 CFR 23.1322 (same date): red/amber/green/other colours, identical; history "Amdt. 23-17 ... Amdt. 23-43". [D-ag]
- 14 CFR 23.2605 (2026-10-01): (a)–(c) same as CS 23.2605(a)–(c); no (d) in FAA text. [D-ag]

## 5. Benchmark: 14 CFR 25.783 "closed, latched, locked" (eCFR 2026-10-01)

- (a)(2) door that could be a hazard if it unlatches: unlatching from "fully closed, latched, and locked" must be extremely improbable (safety analysis). [D-ag]
- (d)(1) provision to latch; (d)(2) no force tending to unlatch, plus means to secure latches **independent of the locking system**; (d)(5) lock cannot be placed locked unless latched; (d)(6) cannot unlatch with locks locked. [D-ag]
- **(e) Warning, caution, and advisory indications**: (e)(1) positive means at each door operator station that close, latch, lock completed; (e)(2) indication if not fully closed, latched, locked; **(e)(3) visual means on flight deck**, erroneous closed-latched-locked indication improbable; **(e)(4) aural warning before/at initial take-off roll** if door not closed/latched/locked and opening would prevent safe take-off and return. [D-ag]
- (f) direct visual inspection provision "without ambiguity"; (h) criteria for doors that are "not a hazard". [D-ag]
- → Design lesson for the retrofit: sense **latched** (latch hooks/pins engaged) and **locked** (handle/secondary lock in locked position) separately, not just "closed" (canopy down); provide a take-off-phase alert (e.g. throttle/airspeed-armed) and ensure a sensor failure cannot give a false "safe" indication. [Y]

## 6. ASTM standards — what could and could not be seen

- ASTM F3061/F3061M (store page shows -24a, -25 active): scope lists topics "Basic Information, Electrical Systems, ... Instrumentation, **Mechanical Systems and Equipment**, Exterior Lighting ..." — no explicit "doors/canopies" in scope. [D-ag]
- ASTM F3117/F3117M (-24a; -25a active): "crew interface aspects of airworthiness and design"; crew includes flight crew and maintenance crew. [D-ag]
- ASTM F3083/F3083M-20a: "emergency conditions, occupant safety and accommodations for occupants and cargo". [D-ag]
- ASTM F3264-24: index specification mapping consensus standards to the rules. [D-ag]
- ASTM F3232/F3232M-25: flight controls; Annex A1 maps MoC to CS-23 Amdt 5+ / 14 CFR 23 Amdt 64+. [D-ag]
- **Which ASTM paragraph holds the door/canopy latch + indication requirement and the alert-colour requirement could not be read (paywalled).** Best inference: latching/indication in **F3061** (mechanical systems) and/or **F3083** (occupant accommodations, the successor of 23.783/807 content); alert colours in **F3117** (crew interface, successor of 23.1322). Basis: AMC1 23.2250 / 23.2315 / 23.2605 lists and AMC2 mappings above. [Y]

## NOT VERIFIED

1. Content and paragraph numbers inside ASTM F3061-24a, F3083-20a, F3117-24a, F3264-24 (§6.11, §7.4, §9.x, §10.2 cited only as headings from EASA AMC1 lists) — paywalled; only store "Scope" abstracts read.
2. Whether ASTM F3117 keeps the red/amber/green scheme verbatim and whether it adds aural/master-warning provisions.
3. DA 40 airworthiness TCDS EASA.A.022 (certification basis, door/canopy configuration, State of Design) — not downloaded; only the noise TCDS was read.
4. Whether a canopy is an "external door" under CS 23.783 — no definition found.
5. Extra NG AFM/POH (EX-01701.00) and AMM (EX-01702.00): whether a canopy warning already exists as standard or option — not read. TCDS Note 3 refers to "AFM/POH Supplements" for optional equipment.
6. GM3 23.2010 revision table — PDF extraction garbled; revisions taken from individual AMC1 paragraphs instead.
7. Any EASA CRI / CM on canopy unlatching for aerobatic aeroplanes — not searched.
