# Word list — canopy alert retrofit (EASA challenge)

Prepared for the unclear line in the notes, "we will get word 1st / word list?" (meaning not verified). These are crisp
working definitions in our own words. Where a definition rests on a source, the source is named. Tags: [D] read by us,
[D-ag] read by a subagent, [Y] our wording or judgement.

## Canopy and latch

| Term | Definition |
|---|---|
| **Canopy** | Transparent cockpit cover that opens as one unit. On the Extra NG it is a single-piece PMMA "tear-drop" bonded into a carbon-fibre frame, hinged on the right (AAIB p. 8) [D]. |
| **Transparency** | The see-through part of a canopy or windshield (here PMMA, 2.9–3.5 mm thick) (AAIB p. 8) [D]. |
| **PMMA** | Poly-methyl methacrylate, "acrylic"; brittle, notch- and fatigue-sensitive at bonded edges (AAIB pp. 22–23) [D]. |
| **Shoot bolt / pawl** | Sliding bolt on the canopy that is driven into a fuselage fitting to lock it. Extra NG: three on one linkage tube (AAIB p. 8; PKBWL calls them pawls) [D]. |
| **Roller lug** | Fuselage fitting with a roller that the bolt's ramp runs over; the ramp compresses the seal (3:1 advantage) (AAIB p. 8) [D]. |
| **Linkage tube / pushrod** | Common bar that moves all three bolts together, held locked by a tension spring (AAIB p. 9) [D]. |
| **Detent** | Mechanical stop or notch that holds a lever in a position and gives a felt "click". |
| **Closed** | The canopy is down on the rim. It says nothing about the bolts. |
| **Latched** | The latch members are engaged, so the canopy cannot open by itself. |
| **Locked** | The latch is engaged **and** held there by a separate locking means. 14 CFR 25.783 treats closed, latched and locked as three separate indications (R3 [D-ag]). |
| **Partially locked** | Extra NG state when the handle is released but not pulled aft: the bolts are only on the start of the ramp; 60 mm handle gap instead of 70 mm; no visible difference at the frame (AAIB pp. 9, 20) [D]. |
| **Unlocked-canopy event** | Take-off or flight with the canopy not fully locked, whether or not it opens. |
| **Inadvertent opening** | Opening not intended by the crew: partial lock + air loads, an occupant knocking the handle, or a mechanism failure. |
| **Jettison** | Deliberate release of the canopy in an emergency; Extra NG: push slightly forward while opening and it detaches at the hinge line (AAIB p. 11) [D]. |
| **Placard / legend** | Marking at the handle showing the LOCK position; EASA AD 2025-0156 mandated new ones (P/N EX-01106.01-(X)) [D]. |
| **Bonding (adhesive)** | Joining parts with glue (here Loctite EA 9395 epoxy on peel-ply surfaces). **Adhesive failure** = separation at the interface; **cohesive failure** = the glue itself splits (AAIB pp. 8, 21) [D]. |
| **Peel ply** | Fabric layer removed before bonding to leave a clean, rough surface (AAIB p. 8 fn. 3) [D]. |
| **Fatigue crack** | Crack that grows under repeated loading until it reaches a critical length (G-MIIL cause per AAIB) [D]. |

## Sensors and electronics

| Term | Definition |
|---|---|
| **Microswitch (snap-action)** | Mechanical contact switch with a fast snap mechanism; 217F calls it "sensitive", λb 0.49 per 10⁶ h (R4 [D-ag]). |
| **Limit switch** | Rugged lever-operated switch, λb 4.3 per 10⁶ h (217F §14.1, R4 [D-ag]). |
| **Reed switch** | Magnetically closed glass-sealed contact; λb 0.0010 per 10⁶ h (R4 [D-ag]). |
| **Hall-effect sensor** | Solid-state magnetic-field sensor; needs a magnet target. |
| **Inductive proximity sensor** | Contactless sensor that detects a metal target by its effect on an oscillator; senses the steel bolt tip [Y]. |
| **NAMUR sensor** | Two-wire proximity-sensor interface with defined current levels. With a line-monitoring input, wire breaks and shorts become detectable faults (exida report: 0.09 FIT dangerous with fail-safe interface vs 9.63 FIT without) [D]. |
| **Form-C / complementary output** | Two outputs that must always disagree; "both" or "neither" means a fault. Our self-check [Y]. |
| **Line monitoring** | Detecting open or short circuits in a sensor loop. |
| **Encoder / LVDT** | Continuous position sensor (option O1). |
| **Trip point** | Position at which an on/off sensor changes state; ours is set inside the 67.5–68.7 mm window [K]. |
| **Rigging** | Mechanical adjustment of a sensor or linkage to its specified position; checked with a **go/no-go gauge**. |
| **Persistence filter / debounce** | A state change is believed only after it lasts a set time (0.5 s here) [Y]. |
| **Annunciator** | Cockpit light with a text legend. |
| **CAS** | Crew alerting system: the EFIS message list (G1000 on the Extra NG, AAIB p. 3 fn. 1) [D]. |
| **Discrete** | On/off electrical signal between systems. |
| **DO-160G** | RTCA environmental test standard for airborne equipment (sections for temperature, vibration, shock, EMI, lightning…) (R4 [D-ag]). |
| **EWIS** | Electrical wiring interconnection system: the wires, connectors and clamps as a system. |
| **FIT** | Failures per 10⁹ device-hours. |
| **MTBF** | Mean time between failures. |

## Alerting and human factors

| Term | Definition |
|---|---|
| **Warning** | Red: hazard needing immediate crew action (CS 23.1322; CS-SC110a §3) [D-ag / D]. |
| **Caution** | Amber: needs awareness now and action later [D-ag / D]. |
| **Advisory** | Status information, white or another non-alert colour. |
| **Positive indication** | A "safe" light that is lit only when the safe state is proven, so a dead system cannot look safe [Y]. |
| **Aural alert / voice** | Tone or spoken message; must be paired with a visual cue (inattentional deafness: 39 % of GA pilots missed an aural alarm under load, Dehais 2014 abstract, R4 [D-ag]). |
| **Master warning / acknowledge** | Push-button that silences the aural part; the light stays until the condition clears. |
| **Inhibit** | Deliberate suppression of an alert in a phase where it would do more harm than good (e.g. near rotation). |
| **Arming** | The point from which an alert becomes active (here: take-off power applied). |
| **False alarm** | Alert with no real hazard caused by the system itself. **Nuisance alert**: the alert is technically correct but not useful in that context. AC 25.1322-1 App. 5 defines them separately (R4 [D-ag]). |
| **Missed alert** | Real hazard, no alert. |
| **Positive predictive value (PPV)** | Share of alerts that are real. |
| **Cry-wolf effect** | Responses slow or stop after repeated false alarms (Breznitz; Bliss et al. 1995: probability matching, R4 [D-ag]). |
| **Probability matching** | Responding to alarms at a rate equal to their perceived reliability (Bliss, Gilson & Deaton 1995 abstract) [D-ag]. |
| **Compliance / reliance** | Acting when the alert fires / trusting silence when it does not (Dixon, Wickens & McCarley 2007) [D-ag]. |
| **Automation complacency / over-reliance** | Skipping the own check because "the light will tell me". |
| **Take-off configuration warning** | Transport-category warning (FAR 25.703) when take-off power is set with an unsafe configuration; our arming analogy (R4 [D-ag]). |

## Safety analysis

| Term | Definition |
|---|---|
| **FHA** | Functional hazard assessment: what each function failure would do, classified by severity. |
| **FMEA** | Failure modes and effects analysis, component by component. |
| **Fault tree (FTA)** | Top event broken into AND/OR combinations of basic events (NASA Fault Tree Handbook 2002) [D]. |
| **Minimal cut set** | Smallest set of basic events that together cause the top event [D, NASA FTH]. |
| **Fussell-Vesely / Birnbaum / RAW / RRW** | Importance measures: share of risk / sensitivity / risk if the event occurs / risk if it never occurs [D, NASA FTH pp. 90–91]. |
| **Common-cause failure** | One cause defeating several "redundant" items (one wrong rigging gauge for all three sensors). |
| **Latent failure** | Failure that stays hidden until a test or demand reveals it; mean unavailability ≈ ½λT (NASA FTH Eq. 7.6) [D]. |
| **Failure-condition classes** | No safety effect / minor / major / hazardous / catastrophic; Class I per-FH ceilings 1e-3 / 1e-4 / 1e-5 / 1e-6 (AC 23.1309-1E Fig. 2, R4 [D-ag]). |
| **Monte Carlo** | Estimating probabilities by simulating many random cases. |
| **ERCS** | European Risk Classification Scheme (Reg. (EU) 2020/2034): severity class × barrier score → risk code such as M3. |
| **Barrier** | Anything that stops an event becoming an accident (design, procedures, situational awareness, warning systems, recovery, protections). |
| **HFACS** | Human Factors Analysis and Classification System (four levels). |

## Regulation and continuing airworthiness

| Term | Definition |
|---|---|
| **EASA** | European Union Aviation Safety Agency; Extra NG type certificate EASA.A.620 [D]. |
| **AAIB / BFU / PKBWL / BEA / NTSB** | Accident investigation bodies of the UK / Germany / Poland / France / USA. |
| **Safety recommendation (SR)** | Investigator's proposal to an addressee (AAIB SR 2024-004 and 2024-005 to EASA) [D]. |
| **State of Design** | Country of the type-certificate holder (Germany for Extra), represented by the BFU; it may append comments to the report (AAIB App. A) [D]. |
| **AD** | Airworthiness Directive: mandatory action (EASA AD 2025-0156: placards + AFM) [D]. |
| **PAD** | Proposed AD put out for comment (PAD 25-017, R1 [D-ag]). |
| **SB / SL** | Service Bulletin / Service Letter from the manufacturer (SB-NG-2-22 frame bonding; SB-NG-1-24 placards) [D]. |
| **AMOC** | Alternative method of compliance with an AD [D, AD p. 3]. |
| **TC / TCDS** | Type certificate / its data sheet with the certification basis. |
| **CS-23** | EASA certification specification for normal-category aeroplanes; the Extra NG basis is Amendment 4 (R3 [D-ag]). |
| **Amendment 5/6, ASTM consensus standards** | Objective-based CS-23 whose acceptable means are mostly ASTM F-standards (F3061, F3117, F3264…) (R3 [D-ag]; ASTM texts paywalled). |
| **Part 21** | EU rules for design and production approval (Reg. (EU) 748/2012). |
| **Minor / major change** | 21.A.91: minor if no appreciable effect on mass, strength, reliability, operational characteristics…; otherwise major (R3 [D-ag]). |
| **STC** | Supplemental type certificate, used for a major change by a non-TC-holder. |
| **Standard change (CS-STAN)** | Pre-approved change data that need no design approval, e.g. CS-SC110a annunciators [D]. |
| **DOA / AP-DOA** | Design organisation approval / alternative procedures to DOA. |
| **ELA1 / ELA2** | European light aircraft classes: ≤ 1 200 kg / ≤ 2 000 kg, not complex (R3 [D-ag]). |
| **Part-ML** | Light-aircraft continuing-airworthiness rules (Annex Vb to Reg. 1321/2014). |
| **AMP** | Aircraft maintenance programme. |
| **ICA** | Instructions for continued airworthiness (21.A.7): how to inspect, test and maintain the change. |
| **AFM / POH / AFMS** | Flight manual / pilot's operating handbook / flight-manual supplement for an installed change. |
| **MEL / MMEL** | (Master) minimum equipment list: what may be inoperative at dispatch; optional under NCO (R3 [D-ag]). |
| **Deferred defect / INOP placard** | Recorded, limited postponement of a repair with a cockpit placard (ML.A.403) (R3 [D-ag]). |
| **CRS** | Certificate of release to service after maintenance. |
| **Part-CAO / Part-145 / Part-66** | Light-aircraft maintenance organisation / maintenance organisation / licensed engineers. |
| **NCO** | Non-commercial operations with other-than-complex aircraft (Air Ops Part-NCO). |
| **VNE / VNO / KIAS** | Never-exceed speed (221 KIAS on the Extra NG, AAIB p. 6) / max structural cruising speed / knots indicated airspeed [D]. |
