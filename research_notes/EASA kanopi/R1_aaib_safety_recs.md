# R1 — AAIB Safety Recommendations from G-MIIL (2024-004, 2024-005) and EASA replies

- read by: subagent R1
- date read: 2026-11-04
- Tags: [D-ag] = read from source; [Y] = inference.
- Scope: the SR chain only. I did not re-read the body of AAIB report 04/2024; the main session handles that.

## Sources
| File (D:\tmp_ideathon\easa\dl\reg\) | URL | sha256(16) |
|---|---|---|
| G-MIIL_SR_doc.pdf: AAIB "G-MIIL Safety Recommendation Document", footer "Updated 29/January/2025" | https://assets.publishing.service.gov.uk/media/67a2193fad556423b636ca0d/G-MIIL_Safety_Recommendation_Document.pdf | 0e84725e50eee3d0 |
| EASA_142301.pdf: EASA **Annual Safety Recommendations Review 2025** (18th ed.; SRs received in 2024) | https://www.easa.europa.eu/en/downloads/142301/en | 4593e54befb7e8d8 |
| EASA_ASRR2026_143946.pdf: EASA **Annual Safety Recommendations Review 2026** (19th ed.; SRs received in 2025; published 29/07/2026) | https://www.easa.europa.eu/en/downloads/143946/en | 1c46f4c18ac503dc |
| EASA_ASRR_140203.pdf: EASA ASRR 2024 (SRs received in 2023), searched only | https://www.easa.europa.eu/en/downloads/140203/en | 975f8bf554ac7e17 |
| gov.uk page | https://www.gov.uk/aaib-reports/aaib-investigation-to-extra-ng-g-miil | (WebFetch) |

- The gov.uk page was published 22 Feb 2024. It links only the 04/24 report, the 29 Jan 2025 SR document and abbreviations. [D-ag]
- An older SR document (media/66c5fc84…) appears in search results. It returned HTTP 410 (gone), so it was NOT READ.

## AAIB synopsis as written in the SR document (p.1) [D-ag]
- The canopy "broke up without warning" in straight and level flight at **184 KIAS**.
- Cause per AAIB: a lack of appropriate bonding between the inner and outer canopy frame at the front, which led to fatigue cracking of the transparency.
- "One Safety Action ... and two Safety Recommendations."

## SR 2024-004 (EASA ref. UNKG-2024-004) [D-ag]
- Made 16 Feb 2024. Recommendation: EASA should "ensure the canopies fitted to all Extra NG aircraft are manufactured to meet the required certification standards and can withstand expected aerodynamic and flight loads."
- EASA interim reply, 26 Apr 2024 (SR doc p.1–2; ASRR 2025 PDF p.106):
  - EASA and Extra reviewed the canopy design data.
  - The bonding process is unchanged from the EA 300, which had "no similar in-service occurrence".
  - The TCH ran a CFD analysis "under conservative assumptions" showing compliance.
  - EASA is evaluating a voluntary one-time **NDT** of in-service frame bonding.
  - **EASA "is also considering the scenario presented by [BFU] on the role that the change in the locking mechanism of the canopy of the Extra NG compared to the previous models might have had in the accident."**
- Status in the SR doc (29 Jan 2025): **Open**. AAIB assessment: **Partially Adequate**. Action status "Planned Action Ongoing", **update due 01 May 2025**.
- ASRR 2025 status: Open.
- **ASRR 2026** (replies sent in 2025): **UNKG-2024-004 does not appear**. I searched the whole text for "2024-004", "Extra" and "G-MIIL" and found none. [D-ag]
  - So EASA published no reply to 2024-004 during 2025 in that report. [Y]
  - The final status of 2024-004 is **unknown**. [NOT VERIFIED]

## SR 2024-005 (EASA ref. UNKG-2024-005) [D-ag]
- Made 16 Feb 2024. Recommendation: EASA should "assess the effectiveness of SB-NG-2-22 in rectifying inadequate bonding".
- AAIB justification (SR doc p.2):
  - The adhesion of the SB foam is unknown.
  - The foam is applied only at the front.
  - The SB does not fix the side-frame or hinge-bracket bonding anomalies.
- EASA reply 26 Apr 2024: the SB was precautionary and was "not to rectify an assumed inadequate bonding". EASA status: Closed – Disagreement. AAIB: Not Adequate, Open.
- EASA reply **28 Nov 2024** (SR doc p.2; ASRR 2025 PDF p.106):
  - EASA agrees the AAIB conclusion of 28/06/2024 (AAIB-28120) on the SB scope is correct.
  - EASA still holds that NG canopies comply with certification requirements even without the SB.
  - The manufacturer will recommend a **one-off inspection of canopy frames per AMM 20-10-06**.
  - "not overlooking the possibility that the canopy was not correctly latched, the manufacturer is offering an **improvement on the latching system** together with a proactive replacement of the outer canopy frame, or even replacing with a new canopy".
  - EASA status: **Closed – Partial Agreement**.
- AAIB feedback (SR doc p.3):
  - "The AAIB concluded that the accident was **not** a result of improper latching of the canopy."
  - The AAIB accepts that the improvements, once completed, should ensure airworthiness.
  - The AAIB notes that certification relies on consistent manufacture to drawings, and "The canopy fitted to G-MIIL was not."
  - Status: **Closed**, AAIB assessment **Partially Adequate**, Planned Action Completed.

## Other EASA SR replies relevant to canopy-lock alerting (context) [D-ag]
- **BELG-2024-001** (ASK-13 D-0019, 17/05/2022; ASRR 2025 PDF p.42):
  - The SR asked for a sailplane design requirement against unwanted canopy opening.
  - EASA final reply 19/12/2024: **Closed – Disagreement**. EASA argues that more robust locking features could compromise emergency opening or jettison. It cites CS 22.777(a)/(d) and CS 22.807, and concludes "there is no need to amend CS-22".
  - Relevance [Y]: this is a likely objection to any lock-hardware change. An *alert* that does not add locking effort or impede jettison avoids it.
- **AUST-2023-004** (DR400 towing a Duo Discus; ASRR 2025 PDF p.37):
  - The canopy opened after take-off, leading to a crash.
  - EASA mandated TN 396-6 via AD 2024-0059. Status: Closed – Agreement.
- **GERF-2025-002** (B757 G-DHKZ; ASRR 2026 printed p.33):
  - The SR asks EASA to reconsider the risk of a cargo door that is not fully closed, latched and locked, and to "adopt the cockpit warning devices required in the FAA STC ST01529SE". Status: Open.
  - Relevance [Y]: an investigation body is again asking for *warning devices* for latch state, though in a large-aeroplane context.

## Key tension to flag [Y]
- The AAIB says G-MIIL was **not** a latching event. EASA (via BFU) keeps the latching or locking-mechanism-change scenario open. EASA AD 2025-0156 then addresses partial or improper locking fleet-wide.
- The team should not claim that G-MIIL was an unlocked-canopy accident. A safer framing: G-MIIL triggered a review that surfaced a **separate, fleet-wide partial-lock hazard** (see PKBWL SP-HMM in R1_extra_ng_canopy_design.md).

## NOT FOUND / NOT VERIFIED
- Any AAIB update on 2024-004 after 29 Jan 2025 (due 01 May 2025): none linked on gov.uk as of 2026-11-04.
- The EASA SRIS (online SR database) entry: I did not query it. Only the annual reviews were read.
- The BFU document describing the "locking mechanism change" scenario: not found.
- The "One Safety Action" by the manufacturer is named in the SR doc but not described there. I take it to be SB-NG-2-22 [Y], but the AAIB report body is the main session's job.
- Whether the "improvement on the latching system" EASA mentions equals ECO-NG-22-09 / ECO-NG-23-07 / AI-NG-02-23 (named by PKBWL): probably [Y], NOT VERIFIED.
