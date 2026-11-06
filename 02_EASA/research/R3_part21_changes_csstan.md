# R3 — Part 21 change classification, Part 21 Light, CS-STAN (canopy alert retrofit)

- read by: subagent R3
- date read: 2026-11-04
- Tags: **[D-ag]** = read in the source this session (paragraph given); **[Y]** = my inference.

## Sources (downloaded to `D:\tmp_ideathon\easa\dl\cert\`)

| File | URL | Version / date |
|---|---|---|
| EAR_Part21.pdf | https://www.easa.europa.eu/en/downloads/20143/en | Easy Access Rules for Initial Airworthiness and Environmental Protection (Reg. (EU) No 748/2012), published **November 2025** (page footer "Nov 2025"; landing page says "check if any rule was adopted after 28 Nov 2025") |
| CS-STAN_Issue4.pdf | https://www.easa.europa.eu/en/downloads/136407/en | **CS-STAN Issue 4**, 27 April 2022 (Annex to ED Decision 2022/009/R); file replaced 28/04/2022. The EASA CS-STAN page (https://www.easa.europa.eu/en/certification-specifications/cs-stan-standard-changes-and-standard-repairs) lists Issue 4 as the latest. |
| TCDS_EASA_A620_ExtraNG_AW.pdf | https://www.easa.europa.eu/en/downloads/104842/en | TCDS EASA.A.620 Extra NG Iss. 04, 02 Dec 2020 |

---

## 1. Definitions (Reg. 748/2012 cover regulation)

- **Art. 1(2)(i) ELA1** aeroplane: MTOM ≤ 1 200 kg, not complex motor-powered. **Art. 1(2)(j) ELA2** aeroplane: MTOM ≤ 2 000 kg, not complex. [D-ag]
- **Art. 1(2)(d)** "Part 21 Light" = Annex Ib. [D-ag]
- **Art. 2(2)(a)**: certificates may alternatively be issued under Annex Ib (Part 21 Light) for an aeroplane ≤ 2 000 kg MTOM with max operational seating of four. **Art. 2(3)(a)**: declaration of design compliance for aeroplane ≤ 1 200 kg, not jet, max two seats. [D-ag]
- **Art. 2a(1)**: a holder of a TC/STC issued under Part 21 could, **until 25 August 2025**, ask EASA to keep the type design under Part 21 Light. [D-ag]
- Extra NG: MTOW 950 kg, 2 seats, TC under Part 21 (TCDS EASA.A.620) → ELA1. [D-ag for data; ELA1 [Y]]
- DA 40: 1 150–1 310 kg depending on variant (noise TCDS) → ELA1 or ELA2. [Y]
- Whether Extra or Diamond used Art. 2a to move their TC to Part 21 Light: **not verified** (the TCDS read is Issue 04, Dec 2020, which is earlier than Part 21 Light). Default assumption: **Part 21 Annex I applies** to both. [Y]

## 2. Classification of changes — Part 21 Subpart D

- **21.A.90A** scope: Subpart D approves changes to TCs; also defines standard changes that need no approval. [D-ag]
- **21.A.90B(a)** standard changes: changes to a TC for (1)(i) aeroplanes ≤ 5 700 kg MTOM ...; (2) that follow design data in EASA CS (incl. associated ICA); (3) not in conflict with TC-holder data. **21.A.90B(b)**: 21.A.91–21.A.109 do not apply. GM 21.A.90B: CS-STAN is that CS; guidance in AMC M.A.801. [D-ag]
- **21.A.90C** stand-alone ICA changes: only by the design approval holder. [D-ag]
- **21.A.91** (Reg. 2025/1065): change is "minor" if no appreciable effect on mass, balance, structural strength, reliability, operational characteristics, noise/emissions, OSD or other airworthiness characteristics; all others major. [D-ag]
- **GM 21.A.91 §3.3**: "Wherever there is doubt as to the classification of a change, EASA should be consulted"; reasons for classification should be recorded. [D-ag]
- **GM 21.A.91 §3.4** — major when (a) special condition / ESF needed; (b) new interpretation of CS; (c) compliance methods not previously accepted; (d) considerable new substantiation; **(e) change alters airworthiness or operating limitations**; (f) mandated by AD; **(g) introduces or affects functions whose failure effect is catastrophic or hazardous.** [D-ag]
- **GM 21.A.91 §3.6**: AFM revisions associated with minor type-design changes are minor. [D-ag]
- **Appendix A to GM 21.A.91**, §3 Flight: major includes "changes to the flight protection or warning system" (in context of changes that adversely affect handling qualities). §4 Systems (for systems assessed under CS 25.1309): failure effect Cat/Haz → major; failure effect **'major'** → major if new MoC, or "**the change affects the pilot/system interface (displays, controls, approved procedures)**", or new type of function. [D-ag]
- **No example in GM 21.A.91 explicitly says adding a warning light/annunciator is minor or major.** [D-ag: searched GM text for "warning|indicat|door|canop|annunciat"]
- Assessment for a canopy alert [Y]:
  - Failure modes: (1) missed alert (canopy unlatched, no warning) = same as today's un-equipped aircraft → at most the existing hazard; (2) false "canopy unlocked" alert → distraction/unnecessary abort; (3) false "locked" (if pilot comes to rely on it) → could be major. A simple-safety assessment (ASTM F3309 / CS 23.1309) would likely put failure effects at minor/major, **not hazardous/catastrophic**, provided the AFMS keeps the visual/physical pre-take-off check as primary and the system does not interfere with canopy jettison (CS 23.807(b)(5)).
  - It adds an emergency/abnormal procedure to the AFMS but does not change limitations → §3.4(e) not triggered.
  - Hence **minor change** is the most likely classification; the §4 "pilot/system interface" criterion is written for CS-25 systems and would push to major only if the failure effect is classified 'major' and EASA applies it by analogy → **consult EASA early (§3.3).**

## 3. Who may apply / approve

- **21.A.92(b)**: "Any natural or legal person may apply for approval of a minor change"; (a) only TC holder may apply for a major change under Subpart D, others go to Subpart E (STC). [D-ag]
- **21.A.93(b)**: application includes a certification programme (21.A.20). [D-ag]
- **21.A.95(a)**: minor changes classified and approved by **1. the Agency; or 2. a DOA within privileges of 21.A.263(c)(1) and (2)**. [D-ag]
- **21.A.95(b)**: approval only when change and affected areas comply with the TC basis, compliance declared and recorded, and no unsafe feature. **21.A.95(c)**: later CS may be used if they "do not affect the demonstration of compliance" → CS-23 Amdt 6 + ASTM could be used for parts of a minor change on the Amdt-4 Extra NG. **21.A.95(e)**: applicant submits substantiation + compliance statement to EASA. **21.A.95(f)**: approval limited to specific configuration(s). [D-ag]
- AMC 21.A.95(a): 21.A.95(e) only for projects applied to EASA; DOA holders approving under privilege produce the data but do not submit it. [D-ag]
- **21.A.263(c)**: DOA privileges (1) classify changes; (2) approve minor changes under Part 21 or Part 21 Light; (3) declare compliance of minor changes for Part 21 Light declared designs. [D-ag]
- **21.A.97(a)**: major changes approved by EASA or DOA under 21.A.263(c)(1) and (8). [D-ag]
- **Subpart E STC**: 21.A.111 scope; **21.A.112B(a)** DOA required; **(b) alternative procedures (AP to DOA)** with Agency agreement; **(c)** for ELA1 products (21.A.14(c)) capability may be shown by EASA acceptance of the certification programme. [D-ag]
- **21.A.14(b)** AP-DOA for ELA2 aircraft (TC applicants); **21.A.14(c)** ELA1: acceptance of certification programme. AMC1 21.A.14(b) describes AP-DOA procedures also applicable to 21.A.112B(b). [D-ag]
- Note: a minor change applicant does **not** need a DOA or AP-DOA — it can apply directly to EASA (21.A.92(b) + 21.A.95(a)1). [Y from D-ag text]

## 4. ICA

- **21.A.7(a)**: holder of TC, STC, **design change** or repair approval shall develop or reference ICA. **21.A.7(b)2**: STC / design change holder provides ICA to all known operators upon release to service of the modified product. [D-ag]
- (Older numbering 21.A.61 / 21.A.120A no longer present in the Nov 2025 EAR; ICA is now 21.A.7, Reg. 2024/1108.) [D-ag: grep found no 21.A.61/21.A.120A headings]
- Part 21 Light equivalent: **21L.A.9** Instructions for continued airworthiness (heading only read). [D-ag heading; content NOT read]
- CS-STAN: **CS STAN.50** — ICA update is part of the SC, no separate approval; template in GM1 STAN.50. [D-ag]

## 5. MMEL for ELA

- **GM No 1 to 21.A.15(d)**: for ELA1/ELA2 the applicant may develop a list of required equipment in TCDS and/or AFM/POH; together with operational equipment requirements this gives equipment that must be operative; "the list of the other installed equipment that may be inoperative constitutes the MMEL." [D-ag]

## 6. Part 21 Light (Annex Ib, Reg. (EU) 2022/1358) — only if the TC is held under Part 21 Light

- **21L.A.21** scope: aeroplane ≤ 2 000 kg MTOM, ≤ 4 seats ... [D-ag]
- **21L.A.61(a)**: Subpart D applies to changes to TCs "for products certified in accordance with this Annex". [D-ag]
- **21L.A.62**: standard changes (CS-STAN, per GM1 21L.A.62); 21L.A.63–70 not applicable to them. [D-ag]
- **21L.A.63(b)** minor-change definition (same wording minus OSD); (c) otherwise major. [D-ag]
- **21L.A.64(b)** any person may apply for a minor change. [D-ag]
- **21L.A.67**: applicant demonstrates compliance with TC basis **or, if chosen, with CS applicable on the date of application** (a)(2); declares compliance (b); submits justification + declaration to the Agency (c). [D-ag]
- **21L.A.69**: DOA may approve under 21.A.263(c)(2)/(8) privileges without application. [D-ag]
- **21L.A.101–108**: changes to declared designs (declaration of design compliance) — headings read only. [D-ag headings]

## 7. CS-STAN Issue 4 — is there a standard change for a canopy alert?

- **CS STAN.00**: SCs/SRs designed per CS-STAN are not subject to an approval process; "Other changes/repairs not included in these Subparts cannot be considered SCs/SRs." [D-ag]
- **CS STAN.05**: always use latest SC revision; record it on EASA Form 123. [D-ag]
- **CS STAN.20**: an SC cannot be used to remove/reduce existing limitations. **CS STAN.30**: SC usable on any type unless in conflict with TC-holder AFM / approved ICA; AD takes precedence. [D-ag]
- **CS STAN.48**: installation check flight rules (pilot qualification, briefing, risk assessment; no permit to fly needed; recorded in Form 123 Block 6). [D-ag]
- **CS-SC110a "Installation of annunciators"** (Group Cabin) — the relevant one: [D-ag]
  - §1 Purpose: installation of annunciators; "installation of new warning, caution, or advisory lights is also covered". Config 1: single annunciator; Config 2: integrated annunciator, VFR only; Config 3: integrated annunciator (ACU) VFR night / IFR, must be ETSO-authorised and based on an EASA-certified "reference installation".
  - §2 Eligibility: "Aeroplanes that are not complex motor-powered aircraft, and any other ELA2 aircraft." → Extra NG and DA 40 both eligible. [D-ag text; eligibility conclusion Y]
  - §3 Methods: AC 43.13-2B ch. 1–2; AC 43.13-1B ch. 10–12 or ASTM F2639-18; ASTM F2490-20 (electrical load). Parts eligible without EASA Form 1; circuit protection; same bus as monitored system; colours **red** (immediate response), **amber** (immediate awareness, subsequent response), **green** (safe operation), others e.g. white.
  - Config 2 note: typical repeater inputs include "**canopy status**" (with fuel, oil, volts, EGT, carb ice ...). Config 2 aggregated annunciators "cannot replace required annunciators"; installation check flight unless ground test is adequate.
  - §4 Limitations: "can only be used to replace an existing annunciator or install an annunciator that aggregates aircraft warnings for awareness only in Configurations 1 and 2."
  - §5 Manuals: AFMS for operation; ICA update incl. actions after annunciator failure.
  - **§6 Release to service: "not suitable for the release to service of the aircraft by the pilot-owner."**
- Other SCs checked: CS-SC062a (awareness function/device — about outside environment, not aircraft systems); CS-SC036b (external visual awareness lights); CS-SC105b (mounting systems); CS-SR803a (temporary canopy crack repair). No SC covers installing a **sensor/switch on the canopy latch/locking mechanism**. [D-ag: grep "canopy|door" over full CS-STAN text]
- Conclusion [Y]: CS-STAN can cover the **cockpit annunciator part** (light + wiring + circuit breaker) and, for Config 2, the "canopy status" awareness repeater. It **cannot** cover the latch-sensing hardware on the canopy mechanism (not listed → CS STAN.00), and its use is "awareness only". A complete closed/latched/locked alert therefore needs a **minor change approval** (21.A.95). A hybrid (sensor kit approved as minor change + annunciator per CS-SC110a) is possible but adds paperwork without saving the approval step.

## NOT VERIFIED

1. Whether a newer CS-STAN issue (Issue 5) has been published after Issue 4 — the EASA CS-STAN page fetched today lists Issue 4 as latest; no EAR for CS-STAN was found (that URL returned 404).
2. AMC1 21L.A.63 / AMC1 21L.A.67 content beyond keyword search; 21L.A.9 ICA text.
3. Whether Extra Aerobatic GmbH or Diamond transferred their TCs to Part 21 Light under Art. 2a.
4. Whether Extra Aerobatic GmbH or Diamond holds a DOA with minor-change privilege (likely, as TC holders, but not checked in the EASA DOA list).
5. The EU–Canada bilateral (TIP) rules for minor changes on the DA 40 (TCCA State of Design) — not read.
6. EASA fees (Fees & Charges Regulation) for a minor change application — not read.
