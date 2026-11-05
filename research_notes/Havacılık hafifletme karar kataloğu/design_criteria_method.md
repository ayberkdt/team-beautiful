# Structural design criteria and material-selection method for a lightweight (topology-optimised, re-materialised) aerospace bracket/fitting

Research date: 2026-11-01. Researcher: sub-agent (deep-research).

**How each finding was checked (applies to every line below):**
- **[FULL]**: I downloaded the primary document this session and read the quoted passage myself. For PDFs I converted them to text with `pdftotext` and read the lines. For eCFR I pulled the official XML and pulled out each section's text.
- **[SNIPPET]**: I saw it only in a web-search summary or snippet. I did not open the full text.
- **UNVERIFIED (memory)**: background knowledge with no source read this session. Do not cite it as sourced.

Primary files used (local copies in the session scratchpad):
- eCFR 14 CFR Part 25, full XML, version date 2026-10-01: `https://www.ecfr.gov/api/versioner/v1/full/2026-10-01/title-14.xml?part=25`. Human-readable page per section: `https://www.ecfr.gov/current/title-14/section-25.XXX`.
- FAA AC 20-107B Change 1, *Composite Aircraft Structure* (dated 8/24/2010): `https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf`
- EASA CM-S-008 **Issue 04**, *Additive Manufacturing*, issued 3 September 2025: `https://www.easa.europa.eu/en/downloads/142437/en`
- Yi M. et al. (NUAA), *A holistic review on fatigue properties of additively manufactured metals*, arXiv:2311.07046 (201 pages): `https://arxiv.org/pdf/2311.07046`
- Ashby, Coulter, Ball, Bream, *Granta EduPack Eco Audit Tool – A White Paper* (the cover says "Version 2.1 – January 2012 Granta Design Ltd."; the footer says "© 2021 ANSYS, Inc."): `https://ansys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf`

---

## Q1. Certification factors: limit vs ultimate load, 1.5, fitting, casting and special factors, A/B-basis design values, and what applies to AM parts

### Takeaway
The FAA rule text, read in full from eCFR, sets up the chain for a bracket:
- Limit load = the largest load expected in service.
- Ultimate load = limit load × 1.5 (§25.303).
- The structure must carry limit load with no harmful permanent deformation, and ultimate load for 3 s without failure (§25.305).
- Every fitting gets a further factor of ≥1.15 (§25.625), unless limit and ultimate tests simulate the real stresses in the fitting. Only the single highest special factor applies (§25.619).
- Strength must come from statistical design values: A-basis (99 %/95 %) for single load paths, B-basis (90 %/95 %) for redundant ones (§25.613).

For AM, EASA CM-S-008 Issue 04 (Sep 2025) says CS-25 itself needs no AM-specific change. What it asks for:
- design values that capture the variability of the whole AM process, including powder or wire and post-processing;
- certification effort scaled to how critical the part is (Class C/D = no or low criticality).

### Cited Findings
**Limit and ultimate loads, 1.5 factor (14 CFR Part 25, current eCFR text) [FULL]**
- §25.301(a): strength requirements are given as limit loads ("the maximum loads to be expected in service") and ultimate loads ("limit loads multiplied by prescribed factors of safety"). Unless stated otherwise, prescribed loads are limit loads. Last amended by Amdt. 25-23 (1970). — [eCFR 14 CFR 25.301](https://www.ecfr.gov/current/title-14/section-25.301)
- §25.303: "Unless otherwise specified, a factor of safety of 1.5 must be applied to the prescribed limit load…". When a load is already given as ultimate, no further factor is needed unless specified. — [eCFR 14 CFR 25.303](https://www.ecfr.gov/current/title-14/section-25.303)
- §25.305(a): the structure must support limit loads "without detrimental permanent deformation".
- §25.305(b): it must support ultimate loads "without failure for at least 3 seconds". The 3-second limit does not apply when strength is shown by dynamic tests.
- §25.305(b): if compliance is by analysis, you must show one of three things: deformation effects are not significant, they are fully accounted for, or the methods are sufficient. This matters for FEA of a flexible topology-optimised part. — [eCFR 14 CFR 25.305](https://www.ecfr.gov/current/title-14/section-25.305)

**Special factors and how they combine [FULL]**
- §25.619: the 1.5 factor "must be multiplied by the **highest pertinent** special factor" from §§25.621–25.625. This applies to any part whose strength is (a) uncertain, (b) likely to deteriorate before normal replacement, or (c) "subject to appreciable variability because of uncertainties in manufacturing processes or inspection methods". Clause (c) is the hook regulators use for new processes such as AM. — [eCFR 14 CFR 25.619](https://www.ecfr.gov/current/title-14/section-25.619)
- In practice, ultimate design load for a fitting = 1.5 × 1.15 × limit = 1.725 × limit. This product is my arithmetic from §25.303 and §25.625. The rule does not state it.

**Fitting factor [FULL]**
- §25.625(a): a fitting is "a part or terminal used to join one structural member to another". If its strength is not proven by limit and ultimate load tests that simulate the real stresses in the fitting and the surrounding structure, a fitting factor "of at least 1.15" applies to:
  - the fitting itself,
  - the means of attachment,
  - the bearing on the joined members.
- §25.625(b): no fitting factor is needed for joints made under approved practice with comprehensive test data, or for a bearing surface that already carries a larger special factor.
- §25.625(c): an integral fitting is treated as a fitting "up to the point at which the section properties become typical of the member".
- §25.625(d): seats, berths, belts and harnesses use the factor in §25.785(f)(3) instead.
- Last amended by Amdt. 25-72 (1990). — [eCFR 14 CFR 25.625](https://www.ecfr.gov/current/title-14/section-25.625)
- §25.623 (bearing factors): a part with clearance (free fit) that is subject to pounding or vibration needs a bearing factor. None is needed if a larger special factor applies. — [eCFR 14 CFR 25.623](https://www.ecfr.gov/current/title-14/section-25.623)

**Casting factors, §25.621 (Amdt. 25-139, 79 FR 59429, 2 Oct 2014; latest in the eCFR text) [FULL]**
- **Critical casting**: one whose failure "could preclude continued safe flight and landing … or could result in serious injury to occupants". [§25.621(c)]
  - Factor **1.0**: allowed only with all of the following. [§25.621(c)(1)]
    - process qualification showing the coefficients of variation of the material properties are "equivalent to those of wrought alloy products";
    - process monitoring with coupons cut from prolongations;
    - 100 % surface inspection (visual plus liquid penetrant);
    - radiographic or equivalent inspection of internal areas;
    - one static test.
  - Factor **1.25**: 100 % surface and radiographic inspection, plus 3 static tests. Strength at the 1.25 ultimate load; deformation checked at 1.15 × limit. [§25.621(c)(2)]
  - Factor **1.50**: same inspections, plus 1 static test. [§25.621(c)(3)]
- **Non-critical castings** [§25.621(d)]:
  - 1.0 with specification coupons, full inspection and 3 sample static tests;
  - 1.25 with surface and radiographic inspection;
  - 1.5 with surface visual plus penetrant inspection;
  - **2.0** with visual inspection only.
- With respect to bearing stresses, casting factors "need not exceed 1.25". [§25.621(b)]
— [eCFR 14 CFR 25.621](https://www.ecfr.gov/current/title-14/section-25.621)

**Material design values (A-/B-basis) and materials/processes rules [FULL]**
- §25.613(a): design values must rest on "enough tests of material meeting approved specifications to establish design values on a statistical basis".
- §25.613(b)(1): **single load path** (failure of one member means loss of structural integrity) → "99 percent probability with 95 percent confidence" (A-basis).
- §25.613(b)(2): **redundant structure** → "90 percent probability with 95 percent confidence" (B-basis).
- §25.613(c): temperature and moisture effects must be considered where significant.
- §25.613(e): higher values are allowed with "premium selection", meaning each item is tested before use.
- Last amended by Amdt. 25-112 (2003). — [eCFR 14 CFR 25.613](https://www.ecfr.gov/current/title-14/section-25.613)
- §25.603: material suitability and durability must (a) rest on experience or tests, (b) meet approved specifications, and (c) account for environmental conditions. — [eCFR 14 CFR 25.603](https://www.ecfr.gov/current/title-14/section-25.603)
- §25.605: fabrication must "produce a consistently sound structure". Processes needing close control (examples given: gluing, spot welding, heat treating) need an approved process specification. "Each new aircraft fabrication method must be substantiated by a test program." This is the direct hook for AM. — [eCFR 14 CFR 25.605](https://www.ecfr.gov/current/title-14/section-25.605)
- §25.609: each part must be protected against weathering, corrosion and abrasion, with ventilation and drainage where needed. — [eCFR 14 CFR 25.609](https://www.ecfr.gov/current/title-14/section-25.609)

**MMPDS basis definitions, quoted inside EASA CM-S-008 Issue 04, Section 1 definitions (pp. 8–9) [FULL]**
- **A-basis (MMPDS)**: the lower of the statistically calculated T99 and the specification minimum (S-basis). At least 99 % of the population equals or exceeds the value, with 95 % confidence. Computed per MMPDS Vol. 1, or similar such as CMH-17.
- **B-basis**: at least 90 % of the population, with 95 % confidence.
- **S-basis**: computed per MMPDS Section 9.2.4.1. Using these values to show static strength compliance "may require further showing".
— [EASA CM-S-008 Issue 04](https://www.easa.europa.eu/en/downloads/142437/en)

**AM-specific guidance: EASA CM-S-008 Issue 04 (issued 3 Sep 2025) [FULL for the passages below]**
- Regulatory references on the cover: CS 2x.305, 2x.307, 2X.571, 2X.603, 2X.605, 2X.613, 2X.853 and others (p. 1).
- No CS-level change is needed for AM. Instead, the AMC to CS 25.603, 25.605 and 25.613 were revised in 2021 (CS-25 Amdt 27). The aim was to stress "representative design values which may be defined during material consolidation in the near-finished complex part configuration", including test/analysis pyramid definitions (Section 2, p. ~10).
- When certification is mainly by analysis, "design values account for variables introduced throughout the AM process … including … the constituent materials (e.g. powder or wire) and post processing" (§3.1.1, p. 12).
- For **no or low criticality parts (Class C and D)**, §3.1.2 (pp. 12–13) asks for:
  - conservative top-down and bottom-up safety assessments covering "all likely defect, damage and failure modes";
  - conservative design practice, including attachments. Redundant attachment points can help, but beware of "fretting, galvanic incompatibility, … access for inspection";
  - PCDs backed by material and process specifications;
  - MMPDS or CMH-17 S-basis data may support proportionate means of compliance (MoC), but it is coupon-based and needs extra influencing factors before it represents a complex part;
  - direct part testing ("Point Design"/"Detail") in addition to, or instead of, coupon tests.
- "Simplified MoC" for low criticality (Section 1 definitions, p. 9) includes:
  - reduced test numbers for B-basis, using normal-distribution factors;
  - Point Design testing;
  - "use of higher design factors";
  - equivalence with an accepted database.
- Version history [SNIPPET]: Issue 01 dated 04.04.2017, Issue 02 Nov 2020, Issue 03 30.04.2021, Issue 04 3 Sep 2025. Sources: search snippet of the [Issue 03 post-consultation PDF](https://www.easa.europa.eu:443/sites/default/files/dfu/cm-s-008_issue_03_-_final_post_consultation.pdf); the Issue 04 date comes from the Issue 04 PDF cover [FULL].

### Inferences
- A student bracket that connects members is a "fitting" under §25.625. The defensible static criterion is: Margin of Safety ≥ 0 at **1.5 × 1.15 × limit load**, using A-basis allowables if the bracket is a single load path, or B-basis if it is redundant. The 1.15 drops away only with a realistic limit-and-ultimate test.
- Treating an AM part like a casting is an analogy, not a rule. No AM factor exists in CS-25 or 14 CFR 25. But §25.619(c) ("uncertainties in manufacturing processes or inspection methods") and §25.621 give a citable precedent for a process-variability factor of 1.0 to 2.0, depending on inspection and testing. If the team applies an extra "AM factor", it should present it as an analogy to §25.621, not as a regulation.
- Because only the highest special factor applies (§25.619), the fitting factor (1.15) and any casting-type factor do not stack.

### Gaps
- **EASA CS-25 text was not read this session.** CS 25.303, 25.613, 25.619, 25.621 and 25.625 are generally numbered and worded like the FAR (UNVERIFIED (memory)). Check the current CS-25 Easy Access Rules (amendment 27 or later). The 2021 AMC changes to 25.603/605/613 are cited only through CM-S-008.
- FAA AM guidance (FAA AM Roadmap, any FAA AM policy or AC) was **not read**. No source.
- MMPDS and CMH-17 were not opened directly. They are paywalled. Definitions come only from CM-S-008's quotation.
- No regulatory source gives a numerical "AM factor". I found none.

---

## Q2. Fatigue and damage tolerance (§25.571); 2xxx vs 7xxx alloy choice; AM fatigue knock-downs (roughness, porosity, HIP)

### Takeaway
§25.571 (current text includes Amdt. 25-148, 2022/2023) requires an evaluation showing that catastrophic failure from fatigue, corrosion, manufacturing defects or accidental damage is avoided. The default is damage tolerance: crack growth from an assumed initial flaw, plus residual strength at limit-level conditions treated as ultimate. Safe-life is allowed only where damage tolerance is shown to be impractical.

For AM Ti-6Al-4V, the review I read in full says:
- as-built surface roughness is the dominant fatigue knock-down;
- HIP closes internal porosity but does not fix the surface;
- only HIP plus machining brings fatigue back to wrought-like levels.

The 2xxx-for-tension / 7xxx-for-compression rule rests here only on patent-literature snippets.

### Cited Findings
**§25.571, current eCFR text [FULL]** — [eCFR 14 CFR 25.571](https://www.ecfr.gov/current/title-14/section-25.571)
- (a): the evaluation must show "catastrophic failure due to fatigue, corrosion, manufacturing defects, or accidental damage, will be avoided throughout the operational life". It covers each part that could contribute to catastrophic failure, explicitly including "engine mounting, landing gear, and their related primary attachments".
- (a)(1): it must include load spectra, temperatures and humidities; identify principal structural elements (PSEs); and use analysis supported by test evidence.
- (a)(3): inspection thresholds for single-load-path structure must come from crack growth analysis or tests, "assuming the structure contains an initial flaw of the maximum probable size that could exist as a result of manufacturing or service-induced damage". This matters for AM parts with porosity and lack-of-fusion defects.
- (a)(3): a Limit of Validity (LOV) must be established.
- (b): the damage-tolerance evaluation determines probable locations and modes of damage, including widespread fatigue damage. Residual strength must cover limit manoeuvre, gust, rolling, yaw, pressurisation (×1.15 on maximum differential pressure) and ground loads, "considered as static ultimate loads".
- (c): safe-life (fatigue) evaluation is allowed only if "the applicant establishes that their application for particular structure is impractical" for damage tolerance. The part must then withstand the repeated loads "without detectable cracks", with "appropriate safe-life scatter factors".
- (e): discrete source damage, for example a 4-lb bird at Vc at sea level or 0.85Vc at 8000 ft, uncontained fan blade, and similar.
- Amendment trail in the text: Amdt. 25-45 (1978) … 25-132 (2010), 25-148 (87 FR 75710, Dec. 9 2022; 88 FR 2813, Jan. 18 2023).

**AM fatigue knock-downs and HIP: Yi et al., arXiv:2311.07046 [FULL for the passages below; review of primary studies]** — [arXiv 2311.07046](https://arxiv.org/pdf/2311.07046)
- p. ~34: for L-PBF Ti-6Al-4V, HIP "led to a more than 100% increase in the fatigue strength at 10^7 cycles (approximately 550–600 MPa)" compared with as-built and stress-relieved conditions. The review cites its ref. [47]. Experimental L-PBF Ti-6Al-4V data after HIP shows "a similar performance to that of the wrought material". Note: those 550–600 MPa values are for machined or polished specimens in the cited study; the review's surrounding context implies this, but I did not check ref. [47] myself.
- p. ~36: "HIP does not improve the surface roughness". The review cites Kahlin et al., who found no benefit from HIP over the annealed condition when the rough surface stays. HIP was "not … effective … in improving the fatigue behavior of notched specimens when the rough surface is not removed".
- p. ~39: for EBM Ti-6Al-4V, chemical polishing cut roughness and "increase[d] the fatigue strength by 60% (to 200 MPa)", citing Persenot et al. That puts the as-built EBM fatigue strength at about 125 MPa (my back-calculation; not stated). The review reports the ranking HIPed+Machined ≥ Machined ≥ HIPed+Etched ≥ Etched ≥ As-built (Fig. 42).
- p. ~44: SMAT surface nanostructuring of SLM Ti-6Al-4V, comparing SMAT / HIP / as-fabricated:
  - LCF: 675 / 430 / 350 MPa;
  - HCF: 580 / 377 / 290 MPa.
- p. ~45 (Fig. 49 discussion): "EBM Ti-6Al-4V parts with HIPed and machined post-processing exhibit comparable-to-superior fatigue life compared to traditional lamellar and bimodal microstructures".
- Corroborating abstracts [SNIPPET only]:
  - Cherna et al. (?), IJF vol. 119, pp. 173–184 (EBM Ti-6Al-4V review): fatigue life comparable to traditional lamellar Ti-6Al-4V needs both HIP and machining. — [ORNL listing](https://www.ornl.gov/publication/review-fatigue-behavior-ti-6al-4v-fabricated-electron-beam-melting-additive)
  - Molaei, Fatemi & Phan 2018, IJF 117: even after HIP, the rough surface dominates life reduction in thin-walled PBF specimens. Search snippet only.
  - Vayssette et al. 2019, IJF: "significant decrease of the HCF life mainly due to the surface roughness". — [SAM ENSAM](https://sam.ensam.eu/handle/10985/14799)

**2xxx (tension) vs 7xxx (compression) [SNIPPET only, patent literature]**
- "Alloy 2024 in the T3 temper has been a standard material for producing lower wing skins for many years owing to its high tolerance to damage." Upper wing skin "is typically a 7X50 alloy (7050 or 7150), or … 7055". Exceptions: the L1011 used 7075-T76 lower skins and the KC-135 used 7178-T6. — [US 5865911 (Alcoa) via USPTO](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5865911); [US 10400312](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10400312). Patent background sections only, not an authoritative design standard.

### Inferences
- For an AM Ti-6Al-4V bracket, the citable post-processing chain is HIP to close porosity, then machining or polishing of fatigue-critical surfaces. HIP alone is not enough if the as-built surface stays (arXiv 2311.07046, p. ~36).
- A topology-optimised bracket usually keeps as-built internal or lattice surfaces. The FEA fatigue check should use an as-built S-N curve or a surface knock-down there. Based on the EBM numbers above, the as-built level is roughly 0.6× the polished level (≈125 vs 200 MPa). That ratio is an inference from a single study.
- Tension-dominated, fatigue-critical members favour the 2xxx damage-tolerance class. Compression or stability-dominated members favour the higher-strength 7xxx. Here this rests only on patent snippets; the reasoning (damage tolerance vs strength) is consistent with §25.571's crack-growth focus.

### Gaps
- No primary source (MMPDS, textbook, OEM) was read for **2xxx vs 7xxx** fracture toughness and fatigue crack growth comparisons. The patent claims are unverified.
- The FAA AC 25.571-1D (damage tolerance guidance) was not read.
- No source read gives a numerical regulatory "AM fatigue knock-down factor". All numbers above are study-specific.
- I did not obtain numbers for **Al-Si10Mg or Scalmalloy AM fatigue**.

---

## Q3. Composite specifics: hot/wet knock-downs, BVID, design strain limits

### Takeaway
FAA AC 20-107B Ch. 1, read in full, gives the regulatory logic:
- design values must hold in the worst environment, and hot/wet is critical for some failure modes while cold/dry is critical for others;
- BVID must not reduce strength below ultimate load;
- impact damage is "accommodated by limiting the design strain levels".

It gives **no numerical strain limit**. The common "≈3000–4000 µε" figure appears only in non-authoritative sources I found.

### Cited Findings
**FAA AC 20-107B Change 1 (8/24/2010) [FULL]** — [AC 20-107B Ch.1 PDF](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf)
- §6.d, p. 6: develop environmental design criteria for humidity and temperature. §6.d(1): design values must be attained "with a high degree of confidence in the appropriate critical environmental exposures". The worst case "may not be the same for all structural details (e.g., hot wet conditions can be critical for some failure modes, while cold dry conditions may be worse for others)". Maximum moisture content relates to part thickness, diffusion and exposure.
- §6.e, p. 7: "Isolation layers are needed at the interfaces between some composite and metal materials to avoid corrosion (e.g., glass plies may be used to isolate carbon composite layers from aluminum)". Qualification of fasteners must cover galvanic corrosion and fastener-installation damage (delamination, fibre breakage).
- §6.f, p. 7: design values must come from stable, repeatable material under a mature specification and production-representative processing. For laminates, they are set at laminate level.
- §6.g, p. 7: "Different levels of impact damage are generally accommodated by limiting the design strain levels for ultimate and limit combined load design criteria."
- §7.e, p. 10: scatter is covered by allowables derived per 14 CFR 2x.613. Otherwise, overload factors are needed in the component test.
- §7.f, p. 10: impact damage up to the threshold of detectability "will not reduce the structural strength below ultimate load capability". The damage "at the threshold of reliable detection has been called barely visible impact damage (BVID)".
- §8.a(1)(c), pp. 12–13, Fig. 3: damage categories.
  - **Category 1** = BVID and allowable manufacturing defects; must keep **ultimate** load (1.5 factor of safety) for the life.
  - **Category 2** = VID found by scheduled inspection.
  - **Category 3** = obvious damage found within a few flights.
  - Categories 2 and 3 need residual strength at or above limit-level loads.

**Strain-limit numbers [SNIPPET only, low-authority]**
- A generic reference table (Engineers Edge) for a wet-layup carbon cloth laminate lists compression-after-impact (CAI) strain allowables of 3000 µε hot/wet (160 °F, 95 % RH), 3579 hot, 4111 RT and 4127 cold. The page warns these are "typical" values to be checked. — [Engineers Edge](https://engineersedge.com/materials/common_fiber_composites_13604.htm)
- A study flashcard gives a "general strain limit … typically 0.4% at ultimate load" so that BVID does not grow. — [Brainscape](https://brainscape.com/flashcards/d8-laminate-service-12608739/packs/21179944). Not citable.
- A CORDIS EU project report says composite aerostructure design follows a "no-growth" approach, with environment included in allowables. — [CORDIS 278156](https://cordis.europa.eu/project/id/278156/reporting/pl) [SNIPPET]

### Inferences
- A team should cite AC 20-107B §6.g and §7.f for **why** a strain cut-off is used. For the **number**, use project or material B-basis CAI data, or say plainly that ≈3000–4000 µε is a common industry rule of thumb and not regulatory text.
- Hot/wet knock-downs are material-specific and must be test-derived per §25.613(c) and AC 20-107B §6.d. There is no universal factor.

### Gaps
- **No authoritative source** (CMH-17 Vol. 3, NASA or OEM report) was read for the 3000–4000 µε design strain limit, or for numerical hot/wet knock-down factors. Leave both as UNVERIFIED, or source them before use.
- EASA AMC 20-29 (the EASA counterpart of AC 20-107B) was not read. CM-S-008 cites it only for the "Threat Assessment" definition (p. 9).

---

## Q4. Ashby method in Granta EduPack and how Eco Audit works

### Takeaway
Penalty-function and exchange-constant definitions come from Ansys Granta help pages, seen only as snippets. The Eco Audit mechanics come from the Ansys/Granta white paper, read in full. The translation, screening and ranking steps were **not read from a primary source** this session.

### Cited Findings
**Multi-objective trade-off: penalty function and exchange constants [SNIPPET]** — [Ansys Granta help: Material selection: penalty functions (v261)](https://ansyshelp.ansys.com/public/Views/Secured/Granta/v261/en/Selector/sel_edu/material_selection_penalty.html)
- Penalty function "Z = α1M1 + α2M2", where M1 and M2 are the performance indices of the two objectives and α1, α2 are exchange constants. "Optimum materials are those with the smallest value of Z."
- α2 "reflects how much the user is willing to pay for each unit of weight saving".
- On linear trade-off axes, optimum materials lie on a line of slope −1/α.
- Truck-panel example: at α = $5/kg, Mg and Al alloys are optimal; at α = $500/kg, CFRP-type composites become optimal.
- The same method is taught in Ansys lecture unit "Objectives in conflict" — [Ansys PPTOBJEN25 PDF](https://ansys.com/content/dam/web/academic/education-resources/2025r1/objectives-in-conflict-lecture-unit-pptobjen25.pdf) (not opened).
- Ashby's split of a design into function, constraints and objective [SNIPPET]. — [UIUC ME598 lecture notes](https://courses.grainger.illinois.edu/me598dm/sp2020/4.selection.pdf)

**Granta Eco Audit: white paper [FULL]** — [Eco Audit White Paper PDF](https://ansys.com/content/dam/amp/2021/august/webpage-requests/education-resources-dam-upload-batch-3/eco-audit-white-paper-PAPEAUEN21.pdf)
- Life phases (Section 2, p. ~5): material production, manufacture, transport, use, and disposal or end of life. Transport links the stages.
- Energy or CO2 footprint is chosen as the metric because it is easy to monitor, can be measured with relative precision, and is closely related to the other (Section 2).
- Strategy:
  - "one phase frequently dominates", and the dominant phase "becomes the first target";
  - if material production dominates → minimise mass and choose low embodied energy;
  - if the use phase dominates (for example transport products) → the strategy is minimising use energy, typically lightweighting;
  - "the best material choice to minimize one phase will not be the one that minimizes the others".
- Mechanics: the tool "multiplies the energy and CO2 per kg of each component by its mass, and totals them". Embodied and process energies and CO2 come from the same EduPack database. Output is bar charts and tables per phase.
- End of life (p. 9):
  - five options: "landfill, combustion for energy recovery, recycling, re-engineer, and reuse";
  - credit is given for **recycled content at the start of life**, and "no credit for recycling at the end", to avoid double counting. This conforms with PAS 2050 / BSI 2008;
  - the potential EoL saving (or penalty) is shown as a **separate cross-hatched bar** ("EoL potential");
  - combustion recovers energy but releases CO2.
- Precision: the method accepts data uncertainty because differences between phases are often large enough to dominate the imprecision (Section 2, and around line 384 of the text).

### Inferences
- Lightweighting an aircraft bracket is a use-phase-dominated case, since fuel burn over life usually outweighs embodied energy. That justifies the mass objective. This follows the white paper's logic for transport products. I did not see a white-paper number for aircraft brackets specifically.
- The EoL-potential bar lets the team show the recyclability benefit of an Al or Ti bracket against CFRP without double-counting it in the first-life total.

### Gaps
- The Ashby **translation** step (function / objective / constraints / free variables), **screening** (limit stages) and **ranking** (performance indices such as E^(1/2)/ρ for a light stiff beam) were **not read from a primary source** this session. They are UNVERIFIED (memory). Source them from Ashby, *Materials Selection in Mechanical Design* (Ch. 5–6), or the Ansys/Granta "Materials selection" lecture units before citing.
- Ansys Help pages may need an Ansys ID. Only snippets were seen.

---

## Q5. Galvanic corrosion (CFRP–Al), Mg in cabins (FAA flammability), Ti–CFRP compatibility

### Takeaway
- **CFRP–Al:** regulator guidance read in full says CFRP must be isolated from aluminium, for example with glass plies. Galvanic issues must be addressed in fastener qualification.
- **Magnesium in cabins:** the historical ban in seat standard SAE AS8049 was replaced by a flammability test (FAA Fire Test Handbook Ch. 25 oil-burner test). In 2015 EASA allowed Mg in specified A350 seat components via special conditions. All of this was seen only in snippets.
- **Ti–CFRP:** no source was read.

### Cited Findings
- AC 20-107B §6.e (p. 7): "glass plies may be used to isolate carbon composite layers from aluminum". Special fasteners "need to address the galvanic corrosion issues". [FULL] — [AC 20-107B Ch.1](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-107B_with_change_1.pdf)
- CM-S-008 Issue 04 §3.1.2 (p. 12): AM attachment design must avoid adverse effects on surrounding structure, including "galvanic incompatibility". [FULL] — [CM-S-008 Issue 04](https://www.easa.europa.eu/en/downloads/142437/en)
- §25.609: protection against corrosion. §25.853(a): cabin materials must meet the Appendix F Part I flammability test criteria. [FULL] — [eCFR 25.609](https://www.ecfr.gov/current/title-14/section-25.609); [eCFR 25.853](https://www.ecfr.gov/current/title-14/section-25.853)
- Magnesium in cabins [SNIPPET]:
  - SAE AS8049 §3.3.3 historically prohibited Mg alloys in cabin seat interiors, and TSO certification requires AS8049. Two new-generation alloys (Elektron WE43 and Elektron 21) self-extinguished shortly after the flame was removed. — [FAA Fire Safety: Use of Magnesium in Airplane Cabins](https://www.fire.tc.faa.gov/pdf/UseofMagnesiuminAirplaneCabins.pdf) (download failed; snippet only)
  - AS8049 Rev C replaced the ban with reference to the FAA Aircraft Materials Fire Test Handbook (DOT/FAA/AR-00/12) Chapter 25 oil-burner test. EASA issued special conditions for the A350-941 in 2015 allowing Mg in specific seat components, conditional on Ch. 25 testing. — [Canari, EASA CRI, FAA Materials WG Oct 2017](https://www.fire.tc.faa.gov/pdf/materials/Oct17Meeting/Canari-1017-EASACRI.pdf)
  - FAA working-group slides from 2018 list Ch. 25 for primary seat components, with work on non-seat cabin use (a proposed Ch. 26 radiant-panel test). — [Marker, FAA Mag Task Group, Mar 2018](https://www.fire.tc.faa.gov/pdf/materials/March18Meeting/Marker-0318-magtask.pdf)
  - Trade press, 2015: "ban is lifted" for seats. — [Runway Girl Network 2015](https://runwaygirlnetwork.com/2015/08/magnesium-alloys-to-be-used-in-aircraft-seats-as-ban-is-lifted/)
- "PS-ANM-25-17": **no search result confirmed** that this policy number exists or what it says. Do not cite it.

### Inferences
- A re-materialised bracket in contact with CFRP should prefer Ti or isolate Al (glass ply, sealant, wet-installed fasteners). The AC 20-107B citation supports the isolation requirement. That Ti is "compatible" with CFRP is UNVERIFIED (memory) here.
- Mg is a weak candidate for a cabin-side bracket. Even with Elektron-type alloys, the documented acceptance route seen covers **seat** components via the Ch. 25 test and special conditions, not general cabin structure.

### Gaps
- **Ti–CFRP galvanic compatibility**: no source read. Find a galvanic-series table (for example MIL-STD-889) or a NASA/OEM corrosion guide.
- The current FAA policy on Mg in cabins (number, date, scope) was not confirmed. The FAA fire-safety PDFs failed to download (HTML returned). Only snippets were seen.
- The CS-25 Appendix F / AMC 25.853 treatment of Mg was not checked.
