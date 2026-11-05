# R3 — Part-ML, release to service, Part-66, MEL/dispatch (Part-NCO), UK route

- read by: subagent R3
- date read: 2026-11-04
- Tags: **[D-ag]** = read in the source this session (paragraph given); **[Y]** = my inference.

## Sources (downloaded to `D:\tmp_ideathon\easa\dl\cert\`)

| File | URL | Version / date |
|---|---|---|
| EAR_ContAW.pdf | https://www.easa.europa.eu/en/downloads/95788/en | Easy Access Rules for Continuing Airworthiness (Reg. (EU) No 1321/2014), published **September 2025** (landing page: rules adopted after 10 Sep 2025 not included) |
| EAR_AirOps.pdf | https://www.easa.europa.eu/en/downloads/20342/en | Easy Access Rules for Air Operations (Reg. (EU) No 965/2012), **Revision 24, March 2026** |
| CS-STAN_Issue4.pdf | https://www.easa.europa.eu/en/downloads/136407/en | CS-STAN Issue 4, 27 Apr 2022 |
| UK CAA web page (WebFetch, not saved) | https://www.caa.co.uk/General-aviation/Aircraft-ownership-and-maintenance/Modifications-and-Repairs | live page, fetched 2026-11-04 |

---

## 1. Applicability of Part-ML

- **Reg. 1321/2014 Art. 3(2)**: Annex Vb (Part-ML) applies to non-complex (a) aeroplanes ≤ 2 730 kg MTOM, (b) rotorcraft ≤ 1 200 kg / ≤ 4 occupants, (c) other ELA2; Part-M applies instead if listed on an air carrier AOC. [D-ag]
- → Extra NG (950 kg) and DA 40 (≤ 1 310 kg) fall under **Part-ML** when not on an airline AOC. [Y]

## 2. Data for the modification

- **ML.A.304**: modifications carried out using data (a) approved by EASA; (b) approved by a Part 21 DOA; **(c) contained in the requirements referred to in 21.A.90B / 21.A.431B (= CS-STAN)**; (d) Part 21 Light standard changes/repairs (21L.A.62/102/202/222); (e) declared by a Part 21 Light declarant. [D-ag]
- → A canopy-alert kit approved as a minor change (EASA or DOA) is valid data under ML.A.304(a)/(b); the annunciator part alone could use (c) CS-SC110a. [Y]

## 3. Aircraft maintenance programme (AMP)

- **ML.A.302(b)**: AMP declared by the owner (no CAMO/CAO) or approved by the CAMO/CAO; must be kept updated. [D-ag]
- **ML.A.302(c)(2)**: AMP includes MIP tasks, or DAH ICA, or declarant ICA; **(c)(5)(a)** must consider "specific installed equipment and modifications of the aircraft". [D-ag]
- → After the retrofit, the **ICA of the change (sensor functional test, switch rigging check, annunciator lamp test interval) must be added to the AMP**. [Y]

## 4. Release to service (CRS) and who may install

- **ML.A.801(b)**: CRS by (1) certifying staff of an approved maintenance organisation (Part-145 / Part-CAO / Part-M Subpart F), (2) independent certifying staff (Part-66 licence), or (3) pilot-owner per ML.A.803. [D-ag]
- **AMC1 ML.A.801 §1** (ED 2023/013/R): only persons entitled to release after maintenance may embody an SC/SR; the releasing person takes responsibility that CS-STAN is met and not in conflict with TC-holder data, incl. design adequacy, parts, documentation, manuals/ICA; CS-STAN may bar the pilot-owner. **§4**: **EASA Form 123** documents the SC; logbook entry refers to it; Form 123 and CRS signed by the same person. [D-ag]
- **ML.A.803(b)** + **Appendix II (b)**: pilot-owner (Part-NCO aircraft) may only do limited maintenance; not allowed if task (5) "requires ... system tests or operational checks for avionics equipment", (2) removal of major assemblies, (4) special/calibrated tools, etc. [D-ag]
- **CS-SC110a §6**: "not suitable for the release to service of the aircraft by the pilot-owner." [D-ag]
- **Part-66 66.A.20(a)**: **B1** — structure, powerplant, mechanical & electrical systems + avionics needing only simple tests; **B2/B2L** — avionics/electrical; **B3** — aeroplane structure, power plant, mechanical and electrical systems + avionics needing only simple tests (the B3 aircraft scope/mass limit was not read: NOT VERIFIED); **L** — aircraft structure, powerplant, mechanical and electrical systems (L licence privileges continue beyond what was read). [D-ag for headings/text read]
- → Installer for both types: a Part-CAO / Part-145 organisation or independent Part-66 B1, B3 or L (with appropriate rating) certifying staff; **not the pilot-owner**. [Y]

## 5. Defects and dispatch with the canopy alert inoperative

- **ML.A.403(a)**: a defect that seriously endangers flight safety must be rectified before flight. [D-ag]
- **ML.A.403(b)(1)**: the **pilot** may defer defects "affecting non-required aircraft equipment"; (b)(2) with an MEL for required equipment; **(b)(3)** under Part-NCO the pilot may defer other defects with the owner's (or CAMO/CAO's) agreement; (b)(4) otherwise certifying staff. [D-ag]
- **ML.A.403(c)** rectify as soon as practicable within maintenance-data limits; **(d)** record deferred defect in the ML.A.305 record system, available to pilot. [D-ag]
- **GM1 ML.A.403**: "required" = required by the airworthiness code, air-ops rules, rules of the air or ATM. **AMC1 ML.A.403(d)**: deferred defects on the deferred-maintenance list (ML.A.305(d)(6)), rectified at next maintenance event. [D-ag]
- → The canopy alert is **not required** by CS 23.783(e) on these tractor types (see R3_cs23_astm.md) nor by NCO.IDE.A → the pilot can defer it under ML.A.403(b)(1), provided the minor-change AFMS does **not** list it as required equipment. Recommended AFMS wording: system INOP → placard "CANOPY WARN INOP", revert to visual/tactile latch check (original AFM procedure), record in tech log. [Y]

## 6. MEL under Part-NCO

- **NCO.GEN.155(a)**: "An MEL **may** be established" — optional for NCO; based on the MMEL, not less restrictive; **(b)** notified to the competent authority (not approved). [D-ag]
- **AMC1 NCO.GEN.155(c)(1)(vi)**: MEL preamble gives guidance on placarding inoperative items; controls/indicators of inoperative units accessible in flight "should be clearly placarded". **(d)** rectification intervals not less restrictive than MMEL (categories in CS-MMEL / CS-GEN-MMEL). [D-ag]
- **GM2 NCO.GEN.155(b)**: equipment not required for the operation that the operator wants to leave inoperative indefinitely is outside MEL scope → deactivate/remove by approved modification. [D-ag]
- **GM3 NCO.GEN.155**: MEL is alleviating; not to encourage operation with inoperative equipment. [D-ag]
- **NCO.IDE.A.105**: flight not commenced if equipment "required for the intended flight" is inoperative unless (a) per MEL if established, or (b) permit to fly. [D-ag]
- **NCO.GEN.105(a)(4)(iii)**: PIC checks required instruments/equipment installed and operative unless MEL (or equivalent) permits. [D-ag]
- **NCO.IDE.A.100(c)**: non-required equipment must not be used to comply with essential requirements / NCO.IDE.A.190/195 and "shall not affect the airworthiness of the aeroplane, even in the case of failures or malfunction". GM1 NCO.IDE.A.100(c)(a): installed non-required equipment still needs airworthiness approval. [D-ag]
- MMEL for ELA: **GM No 1 to 21.A.15(d)** (Part 21) — the list of installed equipment not on the required list constitutes the MMEL. [D-ag]
- → For a commercial operator (e.g. flight school under Part-ORO/Part-CAT/SPO) MEL rules differ — **not read** (only Part-NCO). [Y]

## 7. UK (post-Brexit) — short

- UK CAA page (fetched 2026-11-04): for **Part 21 aircraft**, changes classified minor/major per **21.A.91**; minor changes need **CAA approval unless done as a CS-STAN standard change** (CAA Form 123 records the SC/SR); anyone may apply; minor-change forms **SRG1723** (non-complex aeroplanes/helicopters and other ELA2) and SRG1726NR (complex); data pack = change definition, accomplishment instructions, ICA, AFMS, compliance evidence; CAA recommends the "Minor Change Certification Guidance Document" proforma; CAA then issues a Minor Change approval certificate. For **non-Part 21** aircraft, **CAP 1419** gives guidance on minor modifications. Major changes: Major Change approval, STC or Airworthiness Approval Note (AAN). [D-ag via WebFetch summary of the live page — paragraph numbers on the page not available]
- UK Reg. 748/2012 as retained: CAA regulatory library has 21.A.95 page (https://regulatorylibrary.caa.co.uk/748-2012/Content/Regs/01310_21A95_Requirements_for_approval_of_a_minor_change.htm) — **title seen in search results only, not read**.
- LAA (Light Aircraft Association) handles modifications to **Permit-to-Fly** (non-Part 21) aircraft — the CAA page did not mention the LAA; LAA procedures **not read**. Extra NG and DA 40 in the UK would normally be CofA (Part 21) aircraft, so the LAA route is not relevant to them. [Y]
- UK TCDS for DA 40 exists as UK.TC.A.00025 (search-result snippet only). [NOT VERIFIED]

## NOT VERIFIED

1. Part-CAO privileges (CAO.A.095) and Part-145 scope for embodying minor changes — not read.
2. Full Part-66 L-licence and B3 privilege text (only first part of 66.A.20 read).
3. MEL requirements for non-NCO operations (Part-ORO.MLR / Part-SPO / ATO training under Part-ORA) — not read.
4. CS-GEN-MMEL / CS-MMEL rectification-interval categories — not read.
5. UK: LAA modification procedure; UK CS-STAN equivalence/issue; CAP 1419 content; UK fees.
6. Whether a non-required canopy alert, once in the AFMS, becomes "required" by the AFM equipment list — depends on how the AFMS is written (design decision, not a rule found).
