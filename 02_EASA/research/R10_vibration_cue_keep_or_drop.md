# R10: Throttle-knob vibration cue, keep or drop?

Read by **subagent R10**, **2026-11-05**. Purpose: decide whether the throttle-knob vibration cue (eccentric-mass motor, 4.6 g class, potted in the knob) should stay in the design. The design already has a dedicated lamp, the voice "CANOPY, CANOPY" and a taxi chime, armed by a throttle-lever switch.

**Tags.**
- **[D]**: I read it at the source page or PDF in this session. URL and page or section are given.
- **[D-ag]**: I read only an abstract, a repository record, a press page or another secondary page.
- **[R7] / [R8]**: fact from `R7_haptic_alerting.md`, `R7_visual_alerting.md`, `R7_auditory_alerting.md` or `R8_reaction_time_design.md`. Read at source by that subagent. I did not re-open the source.
- **[Y]**: my judgement or arithmetic, or a search snippet I could not open.

Downloads (untrusted data) are in the session scratchpad, folder `r10dl\`. Text was extracted with `pdftotext` and `python -I`. The local CS-23, CS-STAN and TCDS copies in `D:\tmp_ideathon\easa\dl\cert\` were downloaded by R3; I re-read the paragraphs quoted here in this session.

## Sources

| # | Source | URL or file | What I read | Tag |
|---|---|---|---|---|
| S1 | 14 CFR 23.1141, 23.1143, 23.777, 23.779, 23.781 (eCFR point-in-time 2017-03-01, before Amdt 23-64) | https://www.ecfr.gov/api/versioner/v1/full/2017-03-01/title-14.xml?part=23&section=23.1141 (same pattern for each section) | full section text | D |
| S2 | 14 CFR 23.2400, 23.2600, 23.2605, 23.2610 (eCFR 2025-01-01) | https://www.ecfr.gov/api/versioner/v1/full/2025-01-01/title-14.xml?part=23&section=23.2600 (same pattern) | full section text | D |
| S3 | EASA Easy Access Rules CS-23 Amendment 4 (Jun 2018) | https://www.easa.europa.eu/en/downloads/47182/en (local `EAR_CS23_A4.txt`) | CS 23.777 (p. 167), CS 23.781 (p. 170), CS 23.1141 (p. 237), CS 23.1143 (p. 238), Flight Test Guide para 266 (p. 418) | D |
| S4 | EASA Easy Access Rules CS-23 Amdt 6, AMC/GM Issue 5 (May 2026) | https://www.easa.europa.eu/en/downloads/143630/en (local `EAR_CS23_A6_AMC5.txt`) | AMC2 23.2400 Amdt 4 mapping (pp. 79–80); AMC2 23.2600 Amdt 4 mapping (p. 109) | D |
| S5 | EASA TCDS EASA.A.620 Extra NG, Issue 04 | local `TCDS_EASA_A620_ExtraNG_AW.txt` | A.II Certification Basis, p. 5 of 12 | D |
| S6 | EASA CS-STAN Issue 4, Standard Change CS-SC252a | https://www.easa.europa.eu/en/downloads/136407/en (local `CS-STAN_Issue4.txt`) | CS-SC252a, pp. 159–160 | D |
| S7 | AAIB Bulletin 7/2006, Replica SE5A G-BMDB | https://assets.publishing.service.gov.uk/media/5422eb15ed915d1374000051/Replica_SE5A__G-BMDB_07-06.pdf | full bulletin, p. 89 | D |
| S8 | AOPA, "Training tip: Friction afflictions", 6 May 2019 | https://www.aopa.org/news-and-media/all-news/2019/may/06/training-tip-friction-afflictions | full article | D |
| S9 | AIN, "Rotorcraft Update: JetRanger gets stickshaker", 5 Aug 2008 | https://ainonline.com/aviation-news/business-aviation/2008-08-05/rotorcraft-update-jetranger-gets-stickshaker | full item | D |
| S10 | FlightGlobal, "Safe Flight's shake-up of warning systems", 15 Jun 1999 | https://www.flightglobal.com/safe-flights-shake-up-of-warning-systems/26865.article | full item | D |
| S11 | Müllhäuser, Lusardi et al. (2020). US-German joint flight/simulator evaluation of collective tactile cueing: shaker vs soft stop. VFS 76th Forum | https://saemobilus.sae.org/papers/us-german-joint-flight-simulator-evaluation-collective-tactile-cueing-torque-limit-avoidance-shaker-vs-soft-stop-f-0076-2020-16401 | abstract | D-ag |
| S12 | Safe Flight patent US 6,002,349 (1999), helicopter anti-torque limit warning (pedal shaker) | https://patents.google.com/patent/US6002349A/en | description | D |
| S13 | AvWeb, "AEA: IS&S announces retrofit autothrottles for turboprops", 26 Mar 2018 | https://www.avweb.com/avionics/aea-iss-announces-retrofit-autothrottles-for-turboprops | full item | D-ag |
| S14 | Carré, Tan, Mylon, Lewis (2017). Influence of medical gloves on fingerpad friction and feel. *Wear* 376-377:324–328 (accepted version) | https://eprints.whiterose.ac.uk/id/eprint/112273/ | abstract; "Threshold for perception of vibration" results; Fig. 5, Fig. 6 text | D |
| S15 | Kiss, Boldt, Pfleging, Schneegass (2018). Navigation systems for motorcyclists: exploring wearable tactile feedback. CHI 2018, doi 10.1145/3173574.3174191 | https://www.medien.ifi.lmu.de/pubdb/publications/pub/kiss2018motorcyclenavi/kiss2018motorcyclenavi.pdf | Related work (p. 2), on-body vibration results (p. 3) | D |
| S16 | Travis & Schoppe (1994). Vibrotactile thresholds with diver's gloves. ASA 128th meeting abstract 3aPP9 | https://www.auditory.org/asamtgs/asa94aus/3aPP/3aPP9.html | abstract | D-ag |
| S17 | Juravle, Deubel, Tan, Spence (2010). Changes in tactile sensitivity over the time-course of a goal-directed movement. *Behav. Brain Res.* 208:391–401. PMID 20018212 | Europe PMC REST API | abstract | D-ag |
| S18 | Zhu, Ma, Choi, Hu, Hu, Peng, He (2025). The effectiveness of unimodal and multimodal warnings on drivers' response time: a meta-analysis. *Appl. Sci.* 15:527 | https://mdpi-res.com/d_attachment/applsci/applsci-15-00527/article_deploy/applsci-15-00527.pdf | abstract; Table 2 (p. 9); §3.3.2 (p. 11); §4.3.2 (p. 21) | D |
| S19 | Diederich & Colonius (2004). Bimodal and trimodal multisensory enhancement. *Percept. Psychophys.* PMID 15813202 | Europe PMC REST API | abstract | D-ag |
| S20 | Hecht, Reiner, Karni (2008). Multisensory enhancement: gains in choice and in simple response times. *Exp. Brain Res.* PMID 18478210 | Europe PMC REST API | abstract | D-ag |
| S21 | Salzer, Oron-Gilad, Ronen, Parmet (2011). Vibrotactile "on-thigh" alerting system in the cockpit. *Human Factors* 53:118–131. PMID 21702330 | Europe PMC REST API | abstract | D-ag |
| S22 | Nikolic & Sarter (2001). Peripheral visual feedback. *Human Factors* 43:30–38. PMID 11474762 | Europe PMC REST API | abstract | D-ag |
| S23 | Petermeijer, Doubek, de Winter (2017). Driver response times to auditory, visual and tactile take-over requests: 101 participants. IEEE SMC | https://research.tudelft.nl/en/publications/driver-response-times-to-auditory-visual-and-tactile-take-over-re | abstract | D-ag |
| S24 | Fitch G.M. (2008). Driver comprehension of integrated collision avoidance system alerts presented through a haptic driver seat. PhD, Virginia Tech | https://vtechworks.lib.vt.edu/handle/10919/26281 | abstract | D-ag |
| S25 | Ohio State University press release, "Vibrations may deliver crucial information to pilots", 7 Aug 2000 (on Sklar & Sarter 1999) | https://news.osu.edu/vibrations-may-deliver-crucial-information-to-pilots/ | full text | D-ag |
| S26 | Wilson, Van Bree, Cleveland, Charakuru, Petros, Ferraro, Tavakolian (2026). Evaluation of tactile cueing embedded in an aviation headset on pilot altitude control. *JAAER* 35(2) | https://commons.erau.edu/jaaer/vol35/iss2/8 | abstract | D-ag |
| S27 | AvWeb, "WingX Pro7 on Pebble watch", 1 Apr 2014 | https://avweb.com/flight-safety/wingx-pro7-on-pebble-watch/ | full item | D-ag |
| S28 | NTSB AAR-10/01, Colgan Air 3407 (2010) | https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1001.pdf | §2 analysis pp. 87, 89; finding 11 p. 152; probable cause | D |
| S29 | BEA observations on the EAIB final report, ET302 (B737-8 ET-AVJ) | https://bea.aero/en/investigation-reports/notified-events/detail/accident-to-the-boeing-737-registered-et-avj-and-operated-by-ethiopian-airlines-on-10-03-2019-near-bishoftu-investigation-led-by-eaib-ethiopia/ | page text, "Sequence of events" and crew sections | D |
| S30 | AAIB, Boeing 747-4Q8 G-VHOT, 7 Dec 2006 (Bulletin 8/2008), report page | https://www.gov.uk/aaib-reports/boeing-747-4q8-g-vhot-7-december-2006 | page summary only | D-ag |
| S31 | Popov M. (2020). The influence of vibration on friction: a contact-mechanical perspective. *Front. Mech. Eng.* 6, doi 10.3389/fmech.2020.00069 | https://public-pages-files-2025.frontiersin.org/journals/mechanical-engineering/articles/10.3389/fmech.2020.00069/text | abstract | D-ag |

## Findings by question

### Q1. Vibrating engine or throttle controls in service, and the rules

**Precedents found.**
1. **Helicopter collective shaker, certified and in service.** Safe Flight's system "uses a shaker on the collective to provide tactile limit warnings" for torque and exhaust gas temperature. Low-speed shake at caution, high-speed shake at the limit. It "is standard equipment on the Bell 430" and an option on the Bell 427; an STC exists for the Bell 206B [D, S9]. In a helicopter the collective is the main power control, so this is the closest in-service precedent for a vibrating power control [Y].
2. **Same product, 1999 description.** It monitors transmission torque, EGT, gas producer speed and rotor speed with "increasingly vigorous vibration as danger approaches". When the pilot lowers the collective, "the shaking stops" [D, S10]. No safety concern is mentioned in either trade article [D, S9, S10].
3. **Flight test: pilots preferred a soft stop over the shaker.** Five pilots flew a JUH-60A (RASCAL) in flight, four flew an H135 simulator, high-performance take-offs with torque protection. The soft stop reduced workload more than the shaker and was preferred. The shaker is "a viable alternative" when an active inceptor cannot be used. No numbers in the abstract [D-ag, S11].
4. **Fixed-wing haptic throttle warning: one product, no detail.** IS&S ThrustSense autothrottle lists a "haptic throttle warning" among its features; the system was certified on the PC-12 (2018 article) [D-ag, S13]. I found no description of what triggers it, how it feels, or how it was certified (see NOT VERIFIED).
5. **Pedal shaker exists for helicopter yaw limits.** The shaker is "directly attached to the foot pedal, or to the foot pedal operating mechanism", using an eccentric weight, an annular weight or a solenoid plunger [D, S12]. A pedal shaker on the F-4 for stall warning is known from forum and safety-magazine snippets only [Y, NOT VERIFIED].
6. **No piston-aircraft throttle-knob vibrator in service was found.** Searches for "throttle shaker", haptic throttle studies and GA autothrottle haptics returned only patents, simulator-hobby posts and the items above [Y, search record].

**Requirement texts (legacy CS-23 Amdt 4 is the Extra NG basis).**
7. **Extra NG basis and an existing ELOS on the engine controls.** TCDS A.II: "CS-23 incl. Amdt 4, effective July 17th, 2015". Equivalent Safety Findings include "ELOS-CS23 777/781, Position and shape of Engine Controls" [D, S5 p. 5]. So the throttle position and knob shape are already accepted by an equivalent-safety finding, not by direct compliance [Y]. A changed knob would have to be checked against that ELOS, whose content I could not read.
8. **CS 23.1141(c)**, Powerplant controls: general: "Each control must be able to maintain any necessary position without – (1) Constant attention by flight-crew members; or (2) Tendency to creep due to control loads or vibration." [D, S3 p. 237]. 14 CFR 23.1141(c) has the same words [D, S1].
9. **CS 23.1141(d)**: "Each control must be able to withstand operating loads without failure or excessive deflection." [D, S3 p. 237].
10. **Flight Test Guide para 266** (in the CS-23 Amdt 4 EAR): "Controls are required to maintain any position set by the pilot without tendency to creep due to vibration or control loads." [D, S3 p. 418].
11. **CS 23.1143(c)**: "Each power, thrust or supercharger control must give a positive and immediate responsive means of controlling its engine or supercharger." [D, S3 p. 238].
12. **CS 23.777(a)**: "Each cockpit control must be located and (except where its function is obvious) identified to provide convenient operation and to prevent confusion and inadvertent operation." **(b)**: "...full and unrestricted movement of each control without interference from either his clothing or the cockpit structure." [D, S3 p. 167]. 14 CFR 23.777(d) adds: "Power (thrust) levers must be easily distinguishable from other controls, and provide for accurate, consistent operation." [D, S1].
13. **CS 23.781(b)**: "Powerplant control knobs must conform to the general shapes (but not necessarily the exact sizes of specific proportions) in the following figures" [D, S3 p. 170]. The figure did not survive text extraction.
14. **Current objective rules (Amdt 6 / Part 23 Amdt 64).** 14 CFR 23.2600(b): the applicant "must install flight, navigation, surveillance, and powerplant controls and displays so flightcrew members can monitor and perform defined tasks... The system and equipment design must minimize flightcrew errors, which could result in additional hazards." [D, S2]. 23.2605(c): unsafe-condition information "must be provided in a timely manner to the crewmember responsible for taking corrective action. The information must be clear enough to avoid likely crewmember errors." [D, S2]. 23.2400(c)(4): the powerplant installation must account for "Vibration and fatigue." [D, S2].
15. **EASA maps the old paragraphs to the new ones.** AMC2 23.2400 lists "23.1141(b), (c), (d) Powerplant controls: general" [D, S4 p. 79]. AMC2 23.2600 lists 23.777, 23.779, 23.781 and 23.1141(g) [D, S4 p. 109]. So the creep-by-vibration requirement still lives under CS 23.2400 [Y].
16. **ASTM equivalents could not be read.** AMC1 23.2600/2605 cite ASTM F3117 and others (R3 file). The ASTM texts are paywalled (see NOT VERIFIED).
17. **EASA's own standard change for tactile warnings shows the conditions it sets.** CS-SC252a "Installation of a tactile stall warning indicator system", for "Sailplanes... and ELA2 aircraft except VLR" [D, S6 p. 159]. Conditions:
    - "activated by the signal that triggers a warning (visual and/or aural cue)";
    - a system that "slightly moves the control surfaces (e.g. stick vibrator) must be adjusted to prevent adverse effects upon the aircraft dynamics";
    - "the pilot must have the possibility to manually inhibit" it, and the inhibit must "catch the pilots' attention when inhibited";
    - connected only to "the power supply, trigger signal... and the stick";
    - "advisory or supplementary manner (no hazard, no credit basis)" [D, S6 pp. 159–160].
    The Extra NG (950 kg) is ELA1, a subset of ELA2 [R3]. But SC252a covers a stall warning on the stick, not a canopy alert on a throttle [Y]. **No standard-change route exists for a vibrating throttle** [Y, from reading the SC scope].

**What a knob vibrator touches, in my reading [Y].** 23.1141(c)(2) creep by vibration (the alert itself is a vibration source on the lever); 23.1141(d) loads on the lever; 23.781(b) knob shape and the existing ELOS 777/781; 23.777(b) a flex lead must not limit lever travel; 23.2600(b) "minimize flightcrew errors". None of these forbids a vibrator. Each needs a test or analysis. Note that the arming switch on the lever already touches the throttle installation, but a position switch has no moving mass on the knob.

### Q2. Throttle creep or power change caused by vibration

18. **Engine vibration moved a loose throttle.** SE5A replica, 2006: the pilot was "not tightening the throttle friction nut sufficiently which allowed the throttle to vibrate towards the open position." [D, S7 p. 89]. The aircraft moved off with nobody fully in control and nosed over [D, S7].
19. **Instructors know the effect.** AOPA: older trainers were prone "to having the throttle vibrate out of position even with the friction lock carefully adjusted"; "Avoiding throttle slippage is the reason your instructor nags you to keep a hand on the throttle." An ASRS search on "friction lock" gave 24 reports, not all throttles [D, S8].
20. **Vibration lowers friction in general.** Tribology work treats "active control of static and sliding friction by normal, tangential and transverse oscillations" [D-ag, S31 abstract]. I did not read a number for a throttle-type friction lock [Y].
21. **No evidence was found that an alert vibrator on a lever caused creep.** No report, test or paper. The risk is plausible from 18–20 and from 23.1141(c)(2), but its size is unknown [Y]. A rough scale: the 307-103 ERM gives about 7 G p-p on a 100 g sled (R7), which is a force of about 7 N p-p at about 200 Hz [Y, arithmetic]. This is the same order as a light friction setting. It must be tested on the real quadrant with the friction lock at its loosest normal setting.

### Q3. Masking by engine vibration, and gloves

22. **Handlebar vibration masked hand cues on motorcycles.** Bial et al. found glove cues distinguishable in the lab, but in real riding "hardly differentiable. The main reason for that is the existing level of vibrations at the handlebar of motorbikes." [D, S15 p. 2, reporting Bial et al.; Bial not read].
23. **The waist had the least ride vibration; the wrist the most.** Mean jerk: waist 1.86 m/s³, shoulders 1.92, calf 2.84, arm 3.50, wrist 4.81. The authors conclude "smart watches do not seem to be suitable devices for providing feedback while riding a motorcycle" [D, S15 p. 3]. The waist is 2.6 times quieter than the wrist by this measure [Y, arithmetic].
24. **Pilots warned about cockpit vibration.** Sarter: "There is also the risk that existing vibrations on the flight deck may interfere with the perception of the tactor feedback" [D-ag, S25].
25. **Gloves raise the amplitude needed, but a strong cue survives thin gloves.** 14 participants, 440 Hz: all perceived every signal at amplitude ratio 0.4 or above "regardless of whether gloves were donned". At ratio 0.1: bare finger 43–50 %, single latex glove 14–22 %, double glove 0 % [D, S14 Results, Fig. 5]. Gloves also cut frequency discrimination: at 150 Hz vs 100 Hz, correct "dropped to around 60 % when gloves were donned" [D, S14 Fig. 6 text]. Note: the abstract says gloves "reduce the amplitude threshold"; the data show gloves made weak signals harder to feel [Y, my reading of the results].
26. **Thicker gloves change the threshold curve.** Diver's gloves "do have an effect" on thresholds at 100–400 Hz, and the glove type changes the curve shape. No dB values in the abstract [D-ag, S16].
27. **No data for flight gloves (Nomex or leather) or for a piston-aircraft throttle were found.** No numbers for masking of a hand tactor by piston-engine vibration were found [Y, search record].
28. **The cue fires while the hand is moving the lever.** On the moving hand, tactile thresholds were lower in motor preparation and after the movement, and "increased thresholds (i.e., poorer performance) during the execution period" [D-ag, S17]. The arming trigger is throttle advance, so the first knob pulses arrive during the movement [Y]. Sarter also reported that pilots "sometimes didn't notice vibrations that occurred while the arm wearing the tactor was busy with some other task, such as manipulating aircraft controls" [D-ag, S25].

### Q4. Alternatives that leave the engine controls alone

29. **Lap belt / waist.**
    - Hand and waist tactors gave the same braking RT (843 vs 841 ms), and the waist gave fewer false-alarm actions at high intensity (10.9 % vs 22.3 %) [R7, Meng et al. 2015].
    - Waist is the quietest body site on a motorcycle (finding 23) [D, S15].
    - Torso and belt displays worked at +8 to +9 Gz (TNO) and in a UH-60 simulator (TSAS) [R7].
    - Aviation use: military research and flight trials only. No in-service product found [Y].
30. **Seat pan or thigh.**
    - Cockpit thigh tactors (Israel Aerospace Industries prototype) gave vertical directional cues; "The benefit of adding compatible tactile cues compared with visual and auditory cues alone has yet to be reinforced." [D-ag, S21].
    - Car seat alerts on a test track: with a real crash threat, alerted drivers "returned their gaze to the road sooner, released the throttle sooner, pressed the brake sooner"; half lifted off the throttle before looking back at the road [D-ag, S24]. No ms values in the abstract.
    - Seat vibration works well as a warning but less well for direction [D-ag, Petermeijer et al. 2017, Accid. Anal. Prev. 99:218–227, PMID 27978486, Europe PMC abstract].
    - A back parachute and aerobatic g change the seat contact [R7; Y].
31. **Wrist-worn or wearable.**
    - Sklar & Sarter (1999), 21 flight instructors in a simulator: visual-only cues detected 83 % of mode changes; wrist-tactor groups "nearly all of the time"; one event ~2 s vs ~5 s [D-ag, S25]. Missed when the tactor arm was busy (finding 28).
    - The wrist has the highest ride vibration (finding 23) [D, S15].
    - Consumer pilot wearables exist (WingX on Pebble: altitude, fix, below 1,000 ft, timer), with no approval and no effectiveness data [D-ag, S27]. No Garmin watch alert or worn stall/AoA wearable study was found [Y].
    - A worn device is not part of the aircraft and cannot be relied on for a safety alert [Y].
32. **Headset ear-seal tactors (new candidate).** 39 FAA pilots, X-Plane Piper Archer with G1000, two approaches; the tactile group made "41% fewer altitude deviations (p = .001)" [D-ag, S26]. No RT data. It shares the headset failure mode with the voice (headset unplugged = both lost) [Y].
33. **Rudder pedals.** Pedal shakers exist (helicopter yaw-limit patent, S12; F-4 stall warning, snippet only). On a tailwheel take-off roll the feet are working the rudder and brakes, and a pedal is a primary flight control [Y]. A Van's forum post (snippet only) calls a shaker on reversible flight controls "not a good idea" [Y, NOT VERIFIED]. No RT data found.
34. **Flashing master-warning light in the periphery.**
    - Peripheral visual displays gave "higher detection rates and faster response times" for uncommanded automation changes in a cockpit simulator, without hurting concurrent visual tasks [D-ag, S22].
    - Flash 3–5 Hz, ≥ 25 mm, top centre of panel; red is poorly seen in the periphery; AC 23.1311-1C suggests a large flashing "STALL" for peripheral capture [R7 visual].
    - Context can defeat a flashing cue ("why pilots miss the green box") [R7 visual, abstract only].
35. **Louder or spatial (3-D) audio.**
    - 3-D TCAS audio cut target acquisition from 2.63 s to 2.13 s [R7 auditory]. A canopy alert needs no search, so the gain is small [R7 auditory, Y].
    - Level target +15 to +25 dB over the masked threshold under the headset; a hot microphone adds up to 30 dB [R7 auditory].
    - Louder is not free: a rise of more than 30 dB in 0.5 s is an ISO 7731 fright example [R8].

### Q5. What a third modality adds when light + voice are present

36. **Meta-analysis (60 articles, 308 studies, driving): trimodal is not significantly faster than bimodal.**
    - Visual-auditory vs visual-auditory-tactile: Hedges' g = 0.54 (95 % CI −0.49 to 1.57, p = 0.22) [D, S18 Table 2 p. 9; §3.3.2 p. 11].
    - Visual-tactile vs VAT: g = 0.40 (−0.29 to 1.00). Auditory-tactile vs VAT: g = 0.26 (−0.25 to 0.77) [D, S18 Table 2].
    - The authors: response time under trimodal warnings was "slightly shorter" but not significant, and the gain declines "with the increasing number of modalities", which they link to cognitive overload [D, S18 pp. 11, 21].
    - One included study found trimodal helped younger drivers but "simple unimodal (visual) warnings generated the best outcome for older drivers" [D, S18 p. 21, citing Lundqvist & Eriksson 2019].
37. **In the same meta-analysis, adding touch to sound does help.** Auditory vs auditory-tactile: g = 0.38 (0.04 to 0.72), significant. Tactile vs auditory-tactile: g = 0.46 (0.10 to 0.82). Tactile alone beat visual alone (g = 0.74) and visual alone was not significant against no warning [D, S18 abstract, Table 2]. So touch adds most when it is paired with sound and there is no strong visual cue [Y].
38. **Lab driving study: no gain from the third channel.** Mean braking RT AV 0.71 s = ATV 0.71 s; AT 0.72, TV 0.73; single channels 0.77–0.78 s [R7, Politis 2016 Exp. 3].
39. **Basic psychophysics: trimodal is faster, most of all when the signals are weak.** Trimodal responses were faster than bimodal; "Response enhancement increased with decreasing auditory and tactile stimulus intensity" [D-ag, S19]. Gains were larger in choice RT than in simple RT [D-ag, S20]. [Y] This is the case where vibration earns its place: when the voice is masked (radio, hot mic) and the lamp is off-axis.
40. **Cockpit study: added value of touch over the existing audio-visual alerts not shown.** Salzer et al.: "has yet to be reinforced" [D-ag, S21].
41. **Tactile substitutes well for sound.** Auditory and tactile take-over requests were faster than visual; "auditory and tactile stimuli appear equally effective" whatever the side task (reading, calling, video), 101 participants [D-ag, S23]. Tactile was less hurt than auditory by conversation (+53 vs +148 ms) [R7, Mohebbi 2009]. Real-flight aural alerts were missed ~38 % under load [R8, Callan 2018].
42. **Prewett/Burke meta-analyses (2006, 2012).** Snippets say visual-tactile beat visual-only (overall g ≈ 0.38; RT g ≈ 0.63; high workload g ≈ 0.84), and tactile alerts can replace visual alerts [Y, search snippets; ACM and IEEE pages blocked]. These compare V+T against V only, not against A+V.
43. **No study was found that measured miss rate (not RT) for light + voice vs light + voice + vibration in a cockpit or under high noise.** This is the gap that matters most for our case [Y, search record].

### Q6. When the haptic alert itself was the problem

44. **Colgan 3407 (2009): wrong control input within 1 s of the stick shaker.** "The aft control column input occurred within 1 second of the stick shaker activation", possibly "a rough grab in response to being startled" [D, S28 p. 87]. Finding 11: "The captain's response to stick shaker activation should have been automatic, but his improper flight control inputs were inconsistent with his training and were instead consistent with startle and confusion." [D, S28 p. 152]. Probable cause: "the captain's inappropriate response to the activation of the stick shaker" [D, S28]. The shaker worked as designed; the reaction on the shaken control was wrong [Y].
45. **ET302 (2019): a false shaker from lift-off.** "the left stick shaker activated and remained active until near the end of the recording" after an AoA vane failure [D, S29]. BEA: the first officer "seems to show that he was overwhelmed by the events on board from the moment the stick shaker triggered"; the captain's early autopilot attempts "may be symptomatic of a state of stress that had been rapidly developping following the activation of the stick shaker and Master Caution immediately after take-off" [D, S29]. A false, continuous haptic cue at take-off raised stress and workload [Y]. Many other factors (MCAS, trim) drove the outcome [Y].
46. **G-VHOT (2006): false shakers near V1.** Both stick shakers activated shortly before V1 on two take-offs; the crew continued once and rejected once (stopped about two-thirds down the runway, no damage). Cause pointed to an air data computer [D-ag, S30 summary]. A false haptic alert near decision speed forces a stop-or-go decision [Y].
47. **Lab: strong hand vibration produced more wrong actions.** Hands high intensity 22.3 % false-alarm braking vs waist 10.9 % [R7, Meng 2015].
48. **No case of a mechanically runaway shaker motor (stuck on by an electrical fault) causing an incident was found** [Y, search record]. The ET302 shaker was "runaway" in the sense of a false sensor input, not a motor fault.

## What vibration adds over light + voice (bottom line)

1. **Speed: almost nothing.** Adding touch to light + voice gave 0 ms in the lab (finding 38) and a non-significant effect in a 308-study meta-analysis (finding 36). [D, S18; R7]
2. **Robustness: probably something, not measured.** Touch helps most when the other signals are weak (finding 39) and it survives talking load better than sound (finding 41). It is a backup if the voice is masked or the headset is off and the lamp is outside the line of sight. No cockpit study measured this miss-rate benefit (finding 43). [D-ag, S19, S23; R7]
3. **Cost on the throttle knob specifically:** a primary engine control with an existing ELOS on position and shape (finding 7), an explicit creep-by-vibration rule (findings 8, 10), no standard-change route (finding 17), masking by engine vibration through the lever and gloves (findings 22, 25), reduced feel during the lever movement that triggers it (finding 28), and more wrong abrupt actions with strong hand cues (findings 44, 47). [D, S3, S5, S6, S15, S28; D-ag, S17; R7]

**My judgement [Y]: drop the throttle-knob vibration.** Its benefit (a backup channel) is real but unmeasured, and the same backup can be had at a body site that does not touch the engine control. If the team wants a third channel, move it to the lap belt / waist, keep it single-meaning, medium intensity, take-off phase only, with a pilot inhibit as CS-SC252a requires for tactile stall warnings.

## Options without touching the engine controls

| Option | Detection / RT evidence | Aviation use | Main risk for Extra NG take-off | Tag |
|---|---|---|---|---|
| Throttle-knob vibrator (baseline, for comparison) | Hand = waist RT, 843 vs 841 ms; misses < 1 % when felt | Helicopter collective shaker in service; no piston throttle knob | Engine control rules, creep test, masking via lever, wrong action 22 % at high intensity | R7; D (S3, S5, S9) |
| Lap-belt / waist tactor | Same RT as hand; false-alarm action 10.9 % vs 22.3 % (high intensity); quietest body site | Research only (TSAS, TNO at +9 Gz) | Whole-body vibration masking not measured; harness and parachute contact | R7; D (S15) |
| Seat-pan / thigh tactor | Car: earlier gaze return, throttle release, braking; cockpit: added value over A+V not shown | Thigh prototype (IAI) | Parachute pack, g load, whole-body vibration | D-ag (S21, S24) |
| Wrist-worn (watch type) | 83 % visual-only vs nearly all with wrist tactor; ~2 s vs ~5 s | Consumer apps only, no approval | Missed when arm is busy; highest body vibration; not part of aircraft | D-ag (S25, S27); D (S15) |
| Headset ear-seal tactor | 41 % fewer altitude deviations, 39 pilots, simulator | Research prototype | Lost with the headset, like the voice | D-ag (S26) |
| Rudder-pedal shaker | No RT data found | F-4 (snippet only); helicopter yaw-limit patent | Primary flight control; feet busy on a tailwheel roll | D (S12); Y |
| Flashing master-warning light, peripheral | Peripheral display: higher detection and faster RT in cockpit sim | Standard practice (G1000, MIL-STD-411F) | Off-axis on the roll; context can hide it | D-ag (S22); R7 visual |
| Louder or 3-D audio | 3-D: −0.5 s for target search; little gain without search | TCAS 3-D trials | Startle above +30 dB in 0.5 s; hot mic masks it | R7 auditory; R8 |

Hand-written table. Rows run from the current baseline to options with weaker evidence for this use.

Table check: datawiz `tablo.denetle` was run on 2026-11-05 on both tables in this note (Sources, 31 rows; Options, 8 rows). It returned an empty list for each: **0 HATA, 0 UYARI**. Script: `r10_tablecheck.py` in the session scratchpad.

## NOT VERIFIED

1. **ASTM F3117, F3062 and other consensus standards** cited in AMC1 23.2600/2605: paywalled; no paragraph read. I could not check if they keep the "creep due to vibration" text.
2. **Content of ELOS-CS23 777/781** for the Extra NG: only its title in the TCDS was read. What it accepts about the throttle position and knob is unknown.
3. **IS&S ThrustSense "haptic throttle warning"**: listed as a feature in one trade article only. Trigger, feel, certification basis and service experience not found. The Flying review returned HTTP 410.
4. **F-4 pedal shaker**: activation values and "masked by airframe buffet" come from a forum post and a search snippet of TAC Attack 1967 (acc.af.mil returned 403 and an HTML page).
5. **Van's Air Force post** on shakers and reversible controls: 403; snippet only.
6. **Prewett et al. 2006 / 2012 and Burke et al. 2006 meta-analyses**: ACM DL 403, researchr connection refused, Semantic Scholar gave no abstract. Effect sizes are from search snippets.
7. **Petermeijer et al. 2017 (101 participants)**: RT values not read; TU Delft repository file connection refused.
8. **Morioka & Griffin 2008** (thresholds at hand, seat, feet): the Southampton link returned an HTML page instead of the PDF.
9. **Bial et al.** (motorcycle glove cues): only as reported in Kiss et al. 2018.
10. **Ryu et al. 2010** (in-vehicle vibration spectra): repository abstract via search summary only; no masking numbers.
11. **Flight-glove attenuation** (Nomex, leather) of a hand vibrotactile cue: no study found.
12. **Vibration amplitude at the Extra NG throttle knob** at idle, 2,400 and 2,600 rpm: no data found; must be measured.
13. **Creep of a friction-locked throttle under a knob vibrator**: no test found. The 7 N p-p force estimate is my arithmetic from the R7 datasheet value.
14. **Garmin watch alerts used by pilots, and worn stall/AoA devices**: no product with aviation approval and no study found.
15. **GM-type seat alerts in service**: effectiveness numbers not found (Fitch 2008 abstract has no values).
16. **Lion Air 610 report** (false stick shaker): not read in this session.
17. **A cockpit study measuring miss rate of light + voice vs light + voice + vibration** under noise or high workload: searched, none found. This is the key gap.
18. **Facts tagged [R7]/[R8]** were read at source by those subagents, not re-opened by me.
