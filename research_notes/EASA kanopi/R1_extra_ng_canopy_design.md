# R1 — Extra NG canopy design facts (public sources) + Extra service publications

- read by: subagent R1
- date read: 2026-11-04
- Tags: [D-ag] = read from source; [Y] = inference.

## Sources
| File (D:\tmp_ideathon\easa\dl\reg\) | URL | sha256(16) |
|---|---|---|
| TCDS_104842.pdf: EASA TCDS **EASA.A.620 EXTRA NG, Issue 04, 02 Dec 2020** (12 pp.) | https://www.easa.europa.eu/en/downloads/104842/en | 365c1fe9e4c8ab7a |
| Extra_SB-NG-2-22A.pdf: SB-NG-2-22 Issue A, 23.12.2022, "Canopy Frame Improvement" (7 pp.) | https://extraaircraft.com/wp-content/uploads/2024/02/SB-NG-2-22A.pdf | c74f2df099af485d |
| PKBWL_2022_1097_RK_EN.pdf: PKBWL Final Report 2022/1097, SP-HMM, 18 Mar 2022, EPKP (10 pp.) | https://pkbwl.gov.pl/wp-content/uploads/2023/01/2022_1097_RK_EN.pdf | bf7a61faf38bf2b2 |
| PKBWL_2023_0061_RK_ENG.pdf: PKBWL Final Report 2023-0061, SP-HMM, 4 Aug 2023, dated 11 June 2024 (8 pp.) | https://pkbwl.gov.pl/wp-content/uploads/2023/08/2023_0061_RK_ENG.pdf | 4afd1f9ff3758b3e |
| Extra_SB-NG-1-22A.pdf (fuel/smoke tank chafing) and Extra_SL-NG-2-22A.pdf (tail spring bracket) | extraaircraft.com/wp-content/uploads/2024/02/ | not canopy-related |

- The TCDS web page says the current issue is Issue 04. [D-ag via WebFetch]

## TCDS EASA.A.620 Issue 04 [D-ag]
- TC holder: Extra Aerobatic Aircraft GmbH, Schermbeck. Manufacturer: Extra Flugzeugproduktions- und Vertriebs GmbH, Hünxe. (p.5)
- EASA application date 12 Dec 2014. **EASA TC date 11 Oct 2019.** (p.5)
- Certification basis: **CS-23 incl. Amdt 4** (17 July 2015); reference date 11 Oct 2016. (p.5)
  - SC: smoke system.
  - ELOS: stall-warning removal (ELOS-B23-0207-01), double-action seat belt, engine control position/shape.
  - **No canopy-specific SC/ELOS listed.**
- Category: CS-23 Normal and Aerobatic. Description: tandem two-seat unlimited aerobatic aircraft, carbon composite. (p.6)
- VNE 221 KIAS. ACRO I ±10 g at 820 kg (single seat). (p.6–7)
- Minimum crew: 1 pilot, **rear seat**. Max passengers: 1, front seat. (p.8)
- The only canopy mention: "Levelling Means: Canopy frame". (p.8)
- No canopy warning, latch or jettison data in the TCDS. (whole document searched for "canopy")

## Canopy and latch mechanism (PKBWL 2022/1097, printed pp.6–8) [D-ag]
- Canopy hinged on **three hinges on the starboard side**; it opens to the right. (p.6)
- Locking: pull the **sliding handle on the pilot's left** (port).
  - The text says the handle is connected with "two pawls" engaging fittings on the cockpit side.
  - Fig. 7 labels "Pawl 1" and "Pawls 2 and 3" on a **common pushrod**. So three pawls in total. [D-ag: the figure labels conflict with the "two pawls" sentence; 2023-0061 confirms three]
- The mechanism has unlocked and locked settings and "a notch (dead point)" activated in the locked position. (p.6)
- **Two handles on the same pushrod**, one for the rear seat and one for the front seat. Fig. 9 shows rear and front handles and sliders. (pp.6, 8)
- **Jettison:** "in case of unlocking (canopy jettisoning), the canopy moves automatically back on the hinge guides and detaches from an airplane." (p.6)
- Each port fitting is held by 2 screws and has a roller on top. The roller raises the force pressing the frame to the fuselage and, with the rubber seal, suppresses vibration. (p.6)
- A spring acts on the pushrod toward "locked" (Fig. 8). (p.7)
- 2022/1097 event: the canopy opened at about **350 km/h** in level flight, broke, and part detached. (p.5)
  - Cause: frame vibration from loss of stiffness, which unlocked the pawls.
  - Contributing factors: probable frame crack, loosened rear fitting screws, speed near VNE.
  - Human factor not a cause. No SRs. (pp.9–10)

## PKBWL 2023-0061 (same aircraft SP-HMM, s/n NG026), pp.4–8 [D-ag]
- The canopy opened in level flight after aileron rolls at 1000 m AGL. The limit strap broke and the canopy hit the starboard wing. (p.2, p.4)
- The pilot was in the **rear seat**, with a passenger in front. (p.2)
- **All three roller brackets** on the port side were intact. The **three pawls** were intact and in the "Locked" position. (p.6, finding 6)
- Finding 1, from BFU and TCH: the pawls "were engaged only partially, which technically is not precluded by the cockpit latching system" if the pilot did not lock fully, with the **rear slider handle in its max. aft locking position**. (p.6)
- Finding 9: the passenger may have inadvertently loosened the locks during aerobatics. (p.6)
- Cause 1: the design "technically did not preclude its partial engagement". The locked position "is indicated by a placard (max. aft locking position)". (p.6)
- Cause 3: aerodynamic suction plus vibration loads partially engaged locks and drives them toward open. (p.6)
- No SRs. (p.7)
- TCH preventive actions (pp.7–8):
  1. **POH Revision 11**: pre-flight check (Section 4) and canopy closing and locking description (Section 7.7) reworded. New in-cockpit legend for the aft lock handle, Fig. 3 "Locked / Handle / Slider".
  2. **Engineering changes ECO-NG-22-09 and ECO-NG-23-07**: new pawl contour for extra retention, plus an **additional spring** that raises hold-down force.
  3. SB-NG-2-22 recommended.
  4. **s/n NG061 onward** get the modified locking system as standard.
  5. **AI-NG-02-23** (Assembly and Overhaul Manual) for preventive retrofit, offered **free of charge at the factory**.
- PKBWL states that G-MIIL "involved a spontaneous opening of the cockpit canopy in flight". (p.4)
  - This **conflicts with the AAIB**, which says the canopy broke up and the accident was not a latching event (SR doc p.3).
  - Treat PKBWL's sentence as a secondary characterisation. [Y]

## SB-NG-2-22 Issue A, 23.12.2022 [D-ag]
- Title "Canopy Frame Improvement". COMPLIANCE RECOMMENDED. Applies to **NG001–NG038 except NG026**.
- Approved under DOA EASA.21J.593. (p.1)
- "No required compliance time ... at customer's discretion". (p.1)
- Purpose: rework the adhesive bond between the inner and outer frame as a "mere precautionary measure". (p.1)
- Method:
  - Remove the canopy (AMM 53-20-01).
  - Drill 3 holes of Ø7 mm (A = locking side, B = hinge side, C = centre relief; 430 mm left/right of centre).
  - Inject 2-component PU foam. (pp.2–4)
- WARNING: too much foam "may block the locking mechanism". (p.2)
- **Step 19 (p.4): the clearest public description of the partial-lock state.**
  - "A released rear canopy handle will travel to a **partially locked position** where the shoot bolt lead wedge section is only engaged with the lug roller."
  - Full lock requires pulling the rear handle **fully rearward** to get "audible / acoustic and tactile confirmation that the shoot bolts are fully engaged". This means the roller sits on the top flat of the shoot bolt (Fig. 2, p.5).
- "New canopies already have improved bonding." Warranty: 1 man-hour. (p.6)

## Design-relevant inferences [Y]
- The existing Extra NG confirmation means are mechanical and human: the handle detent, a placard or legend, and an audible or tactile click. **I found no public evidence of any electrical canopy-unlocked warning on the Extra NG.**
- The physical quantity separating "partially locked" from "locked" is **pushrod or handle travel to the max-aft detent**: wedge section versus the top flat on the roller. A sensor at the rear handle full-aft position, or at a pawl or roller, is the natural detection point.
- Constraints for a retrofit:
  - Do not interfere with jettison, where the canopy slides aft and off the hinges.
  - Allow for the pushrod spring.
  - Cover both front and rear handles, which sit on the same pushrod.
  - Keep carbon-frame stress in mind: avoid drilling near the middle-pawl notch, where the crack started on SP-HMM.
- The locking system was changed from NG061 (ECO-NG-22-09/23-07), and the new placards came from NG065. So the fleet has at least three configuration states: pre-NG061; NG061–NG064; NG065+. Retrofits may also exist via AI-NG-02-23.

## NOT FOUND / NOT VERIFIED
- POH/AFM text (Rev 11, Rev 16): not public. Sections 4 and 7.7 are known only via PKBWL.
- SB-NG-1-24 text and the new placard wording (EX-01106.01).
- ECO-NG-22-09, ECO-NG-23-07 and AI-NG-02-23 documents: not found publicly.
- Whether the "improvement on the latching system" in EASA's 28 Nov 2024 reply is the same as these ECOs.
- Any canopy-open or unlocked warning light or switch on the Extra NG or EA 300: none found. Searches returned only RV and other types.
- Canopy jettison handle details (separate red handle or not): not confirmed. PKBWL says only that unlocking in flight releases the canopy aft.
- Fleet size: the FAA says 30 US-registered. Total production: not verified.
- I did not open the Extra website service page (extraaircraft.com/techservice.php); it returned HTTP 403 to curl.
