# R7 — Interlocks, take-off inhibits and automatic engine shut-down

Read by: **subagent R7-interlock**, 2026-11-05. Not yet spot-checked by the main session.

**Tags.**
- [D-ag] = read at the source in this session by R7. URL and page/section given.
- [Y] = secondary source, search-engine snippet, or R7's own interpretation/arithmetic.

**Scope.** Interlocks and take-off inhibits; interlock defeat; engine loss after take-off versus canopy opening; design options for
the Extra NG. Not redone: the 14 CFR 25.703 take-off warning summary and the cry-wolf literature (see `R4_alerting_human_factors.md`
§1.3 and §2).

**Downloads** (untrusted data): `D:\tmp_ideathon\easa\dl\r7_interlock\`. Text extracts: `D:\tmp_ideathon\easa\txt_r7\`
(pdftotext). Python reading project CSVs was run with `python -I` from the scratchpad.

## Sources

| # | Source | What was read | URL |
|---|---|---|---|
| S1 | NTSB AAR-15/03, Gulfstream G-IV N121JM, Bedford MA, 31 May 2014 | Exec. summary pp. vii–ix; §1.3.2 pp. 12–13; §1.6 QAR p. 16; §1.10.2–1.10.5 pp. 23–25; §1.12.1 p. 29; analysis pp. 34, 46–47; findings | https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1503.pdf |
| S2 | CIAIAC A-032/2008, Spanair JK5022 MD-82 EC-HFP, Madrid, 20 Aug 2008 (English) | §1.18.8 pp. 143–147; §2.4.4 pp. 204–207; §3.2 Causes pp. 233–234 | https://www.faa.gov/sites/faa.gov/files/2022-11/Final%20CIAIAC%20Rpt%20Spanair%205022.pdf |
| S3 | NTSB AAR-88/05, Northwest 255 MD-82, Detroit, 16 Aug 1987 (ERAU OCR copy; the ntsb.gov scan has no text layer) | Analysis of CAWS power loss, report pp. 53–54 | https://libraryonline.erau.edu/online-full-text/ntsb/aircraft-accident-reports/AAR88-05.pdf |
| S4 | NTSB AAR-89/04, Delta 1141 B727, Dallas-Fort Worth, 31 Aug 1988 (ERAU OCR copy) | §1.6 p. 12; §1.16.2 p. 37; FAA fleet survey p. ~41; analysis p. 65; findings 9–10 p. 93 | https://libraryonline.erau.edu/online-full-text/ntsb/aircraft-accident-reports/AAR89-04.pdf |
| S5 | EASA CS-23 Amdt 4 (Easy Access Rules) | CS 23.679 (PDF p. 153); CS 23.1155 (PDF p. 239) | file from R3: `D:\tmp_ideathon\easa\dl\cert\EAR_CS23_A4.pdf` (EASA EAR CS-23) |
| S6 | HVBG/BGIA report "Manipulation von Schutzeinrichtungen an Maschinen" (2006), chapters 1–4 | §3.1.1 p. 23; §3.2.1–3.2.5 pp. 25–27; §3.2.8 p. 28; ch. 4 pp. 32, 35 | https://presse.dguv.de/medien/ifa/de/pub/rep/pdf/rep05/manipulation_schutzeinrichtungen/kapitel1bis4.pdf |
| S7 | TRB Special Report 278, *Buckling Up* (2004), ch. 3 | pp. 42–52 (read through WebFetch; quotes extracted by a summarising tool) | https://www.nationalacademies.org/read/10832/chapter/5 |
| S8 | BEA study "Reduction in engine power at take-off" (Sept 2022), France 2015–2019 | Whole study, pp. 2–11, Figure 7 checked as an image | https://bea.aero/fileadmin/user_upload/Reduction_in_engine_power_at_take-off.pdf |
| S9 | AOPA ASF 2002 Nall Report (2001 data) | PDF p. 6 (accident class); PDF p. 12 (take-offs and landings) | https://www.aopa.org/-/media/Files/AOPA/Home/Training-and-Safety/Nall-Report/02nall.pdf |
| S10 | AAIB Bulletin 3/2011, Pitts S-2B G-IIDY | pp. 36–37 (whole report) | https://assets.publishing.service.gov.uk/media/5422eb2440f0b61346000055/Pitts_S-2B_Special__G-IIDY_03-11.pdf |
| S11 | AAIB Bulletin 4/2005, Aero L-39C G-OALB | pp. 16–18 | https://assets.publishing.service.gov.uk/media/5422ff5740f0b6134200091d/G-OALB_4-05.pdf |
| S12 | NTSB ASR-19-01 (Boeing 737 MAX MCAS safety recommendation report, 2019) | PDF pp. 5 and 7 | https://www.ntsb.gov/investigations/AccidentReports/Reports/ASR1901.pdf |
| S13 | AOPA Pilot, "The 1998 Nall Report" (secondary; cites Rostykus et al., JAMA 1998;280(11):997–999) | whole article | https://www.aopa.org/news-and-media/all-news/1998/december/pilot/the-1998-nall-report |
| S14 | Team dataset `R2_occurrences.csv` + `R5_occurrences_add.csv` (241 rows) | re-counted by R7 with `python -I` | `02_EASA/research/` |

## Findings

### A. Take-off configuration warnings: what failed and why

1. **Spanair JK5022 (154 dead of 172 on board, CIAIAC synopsis).** The crew did not set flaps/slats. The TOWS did not sound. The CIAIAC cause names the
   checklist omissions **and** "the absence of an improper takeoff configuration warning". "The reason for the failure of the TOWS to
   function could not be reliably established." [D-ag, S2 §3.2 pp. 233–234]
2. **TOWS were certified as "non-essential" back-ups.** No reliability analysis was required. The FAA's 1988 study found 12
   configuration accidents or major incidents from 1958 to 1987, excluding Detroit. Six of them involved flaps or slats. [D-ag, S2 §2.4.4 pp. 204–205]
3. **A single fault disables the alert, and nothing tells the crew.** "The Detroit, Dallas and Barajas accidents show that the TOWS can be
   disabled on the ground by a simple fault in one of its components." The MMEL makes TOWS no-go, yet "the same fault can go
   unnoticed by the crew since the system does not provide any type of warning" that it has failed. [D-ag, S2 pp. 205–206]
4. **The CIAIAC's conclusion on alerts alone:** "the human factor, in conjunction with first-generation takeoff warning systems, is not
   enough of a barrier". Configuration-error accidents named in the report caused 475 deaths. NTSB counts 49 such accidents worldwide
   since 1968. [D-ag, S2 pp. 205–206]
5. **Northwest 255 (156 on board dead, plus 2 on the ground).** The TOWS had no power because the P-40 circuit breaker was open. NTSB
   could not say if the breaker failed or was opened on purpose. NTSB considered that a crew may open a breaker "as a switch" to stop
   **nuisance warnings** from the same CAWS power supply, and "cannot rule out this possibility". The checklist circuit-breaker check took
   2 seconds. [D-ag, S3 pp. 53–54]
6. **Delta 1141 (14 dead).** The TOWS throttle switch did not close (contamination or misalignment). Three weeks earlier the horn was
   written up as "weak and intermittent". Maintenance swapped the horn only, so the real fault stayed. [D-ag, S4 p. 12; p. 65; findings 9–10 p. 93]
7. **Nuisance avoidance eroded the margin (DL1141).** Per Boeing instructions, the switch cam had been machined so the TOWS armed at
   18.5–20.5° throttle lever angle instead of 11.5–13.5°. The purpose was "to prevent nuisance activations of the takeoff warning system
   when applying power to taxi" at high density altitude. [D-ag, S4 §1.16.2 p. 37]
8. **Fleet survey after DL1141:** 35 TOWS anomalies in 1,190 B727s (2.9 %). Twelve were in the throttle-lever switch. The FAA team
   recommended arming the TOWS on engine pressure ratio (actual power) instead of throttle position. [D-ag, S4 p. ~41]
9. **TOWS also works.** Of 365 ASRS take-off/initial-climb reports involving flaps (1988–2009), 88 were TOWS warnings for a wrong flap
   setting. In one B737 case the TOWS was silent (tripped breaker) and the crew noticed only at stick-shaker at about 100 ft. [D-ag, S2 §1.18.8.5 pp. 146–147]
10. **Light-aircraft canopy warnings in the team dataset.** Of the 126 lock-related openings, 9 rows say a warning was fitted. Notes
    in these rows describe: a sensor showing LOCKED when the canopy was not engaged (Pitts G-IIDY, RV-14 N6161 fatal, BD-10 N2BD);
    an alert seen and dismissed as a sensor fault (L-39 G-OALB); and a light not noticed in taxi (DA20 N527SS). [Y — R7 read the CSV
    notes only; the reports behind them were read by R2/R5, except G-IIDY and G-OALB (below)]
11. **Pitts S-2B G-IIDY.** A non-standard horn sounded "if the canopy locking lever was not in the fully locked position". The horn was
    silent. The canopy opened at take-off power and detached. The lever was still locked; the canopy "could not have engaged correctly on
    the aircraft fuselage". **The sensor watched the lever, not the latch engagement.** [D-ag, S10 pp. 36–37]
12. **L-39 G-OALB: a true alert dismissed because of past nuisance.** The "unlocked" light stayed on. The pilot (11,600 h) believed the
    microswitch was mis-adjusted, because "on a previous flight the light had been extinguished by twisting and pushing" the lock. He took
    off; the rear canopy detached at about 100 ft. The handle can be stowed without the canopy being locked. [D-ag, S11 pp. 16–18]

### B. Interlocks that already exist in aviation

13. **Gust-lock rule CS 23.679 (CS-23 Amdt 4):** a control lock must (a) give "an unmistakable warning when the lock is engaged"; (b) either
    disengage automatically or "limit the operation of the aeroplane ... in a manner that is apparent to the pilot prior to take-off"; and
    (c) have "a means to preclude the possibility of it becoming inadvertently engaged in flight". [D-ag, S5 PDF p. 153]
    — This is the exact pattern of our take-off gate: limit operation on the ground, never engage in flight. [Y]
14. **FAA interpretation of 14 CFR 25.679(a)(2) (letter of 29 Aug 2014):** throttle-advance blocking is an accepted example. The rule
    wording "Limit the operation of the airplane" exists "to prevent pilots from ignoring or mistaking visual and aural take off warnings".
    An "unmistakable warning" is "a warning that physically limits the operation of the airplane to prevent an unsafe takeoff". [D-ag, S1 §1.3.2 pp. 12–13]
15. **CS 23.1155 (turbine reverse/beta):** the control needs "a positive lock or stop at the flight idle position" and "a separate and
    distinct operation by the crew" to pass it. [D-ag, S5 PDF p. 239] — A design precedent for a gate that is overridden by a distinct
    action, not by force. [Y]
16. **G-IV N121JM (7 dead): the interlock existed and did not work.** It was meant to limit throttle lever angle (TLA) to 6° with the gust
    lock ON. Nine in-service G-IVs reached 18.2–24.2° TLA, i.e. "3 to 4 times greater" than intended. Worst-case tolerance analysis: 23°;
    up to 26° with wrong rigging. With the handle in an intermediate position, 41° TLA was possible. [D-ag, S1 pp. vii, 23–25]
17. **Compliance was shown by drawing review only.** No functional test was done. NTSB: a 6° interlock "would have prevented the airplane
    from achieving any significant acceleration, thus constituting an unmistakable warning that would most likely have prevented the
    accident. The same cannot be said for the other two protections, which depend on consistent flight crew adherence to SOPs." [D-ag, S1 pp. 46–47]
18. **The pilot met the stop and pressed on.** The throttles stopped at about 50 % of their normal travel. The PIC did not call it out or
    reject. He engaged the autothrottle. The likely explanation for the extra 7–8° of lever travel is that the gust-lock handle lock pin
    failed. After "lock is on" the crew still delayed braking by about 10 s. [D-ag, S1 pp. vii, 34 (§2 analysis)]
19. **Habitual non-compliance:** the QAR held 176 take-offs. NTSB found 2 complete and 16 partial flight-control checks (complete in
    1.1 % — R7 arithmetic). [D-ag, S1 §1.6 Flight Recorders p. 16; executive summary p. vii: "98% of their previous 175 takeoffs"]
20. **Gulfstream's own warning after the accident:** "Throttle movement is not an absolute indicator of the gust lock status." The planned fix
    included a stronger lock pin and **recurring checks** that the interlock still works. [D-ag, S1 §1.12.1 p. 29]
21. **No certified light-aircraft or gyroplane canopy-to-ignition/throttle interlock was found.** Only home-builder forum suggestions
    turned up (Sonex/RV threads). Not used as evidence. [Y]

### C. How often people defeat interlocks

22. **Machinery (HVBG/BGIA 2006).** 940 respondents estimate that "knapp 37 %" (just under 37 %) of protective devices on machines are
    permanently or temporarily defeated. Safety specialists estimate lower, but still about one third. [D-ag, S6 §3.1.1 p. 23]
23. In a second sample of 202 machines that had been manipulated: 27 accidents and 13 near misses (about 20 %). About 3/4 of
    defeats needed no special tool. 90 % can be undone quickly. For 30–40 % of the machines there was no safe way to do the job without
    defeating the guard. [D-ag, S6 §3.2.3–3.2.5 pp. 26–27]
24. Defeat is tolerated by the company in almost 60 % of cases and expected in about 14 %. 74 % say the device is easy to defeat.
    The main motive is saving time (22 % of answers). [D-ag, S6 §3.2.8 p. 28; ch. 4 p. 32]
25. **ISO 14119** (interlocking devices): the machine "shall be designed in such a way that it minimizes the motivation for defeating the
    interlocking devices" (2013, cl. 7; 2024 ed. cl. 8; Annex H on motivation). [Y — quoted by secondary sources; standard is paywalled]
26. **Car seat-belt ignition interlock, US model year 1974.** It was introduced "without extensive study or pilot testing". Belt use rose
    from about 28 % (1973 buzzer cars) to about 67 % (1974 interlock cars) in a 1976 NHTSA 19-city study. Another study found 59 %.
    Rental cars: 23 % with no system vs 56 % with reminder-interlock. [D-ag, S7 pp. 43–45]
27. **The decay:** "many motorists eventually disconnected the seat belt interlock or circumvented it". One third of drivers in each group
    said they would disconnect the system. The interlock "did not allow the driver to idle or drive at low speeds without wearing a belt".
    Congress then passed legislation that stopped NHTSA requiring it. [D-ag, S7 pp. 43–45, 50]
    — Lesson [Y]: an interlock that blocks normal low-energy use (taxi, idle) creates the motive to defeat. Our gate must not block taxi or
    run-up with the canopy open.
28. **Motorcycle side-stand engine cut-off:** no primary data on defeat rates found. [NOT VERIFIED]

### D. Engine loss at low height versus canopy opening

29. **Team dataset, re-counted by R7 (S14).** 241 rows. Lock-related (not_locked + partially_latched) = 126; fatal 16 (12.7 %).
    Initial climb 76, of which 9 fatal (11.8 %). Take-off roll 17, of which **0 fatal** (14 no injury, 1 minor, 2 unknown). Cruise 24. [D-ag, S14]
30. **BEA France 2015–2019, power reduction at take-off, light single-engine aeroplanes and microlights.** 68 accidents identified. The
    31-case investigated sample had **12 fatal** accidents. All 12 were loss of control in flight. [D-ag, S8 pp. 3, 5]
    — R7 arithmetic [Y]: fatal accidents = 12 in the sample + 1 fatal microlight left out = 13 of 68 = **19 %** of accidents. The investigated
    sample alone is 12/31 = 39 % (biased towards fatal cases, because 33 non-fatal uncertified accidents were not investigated).
31. **Turning kills; holding the axis does not (BEA Figure 7, read as an image).** Marked heading change / turn-back: 18 cases, 10 fatal
    (56 %). Axis held or slight turn: 9 cases, 0 fatal. Unknown path: 3 cases, 2 fatal. Aborted take-off: 1 case, 0 fatal (runway
    excursion). Where height was recorded, the maximum was 186 ft. Elsewhere it did not exceed 500 ft. [D-ag, S8 p. 10]
32. **High-power aircraft are most exposed.** "The latest generations of light and highly powered aircraft are particularly susceptible to
    loss of control during a sudden reduction in engine power during a steep climb." [D-ag, S8 §2.2.2 p. 9] — The Extra NG
    (Lycoming AEIO-580, TCDS EASA.A.620) is such an aircraft. [Y]
33. **Partial power loss is worse than total loss.** BEA cites the ATSB: consequences were "more serious in cases of partial reduction than
    in cases of total reduction". [D-ag, S8 p. 8, side note 2] ATSB figures (2000–2010, single-engine): 242 partial power losses after
    take-off with 9 fatal (3.7 %); 75 complete failures with 0 fatal. [Y — search snippet only; the ATSB site timed out twice]
34. **Experience does not protect.** All 5 dual-instruction accidents in the BEA sample were fatal. [D-ag, S8 pp. 3, 11]
35. **Low-speed rejects are benign.** BEA: light-aviation runway excursions "do not generally result in serious bodily injury" (most are on
    landing). [D-ag, S8 p. 11, side note 5]
36. **US take-off/climb accidents (2001 data).** In single-engine fixed-gear aeroplanes, 32 of 191 take-off/climb accidents were fatal
    (16.8 %). The rate was 30 % for retractables and 38.9 % for twins. Pilot-related take-off accidents: 20.5 % fatal vs 1 % for landing
    accidents. [D-ag, S9 PDF pp. 6, 12]
37. **Power-loss crash landings (US 1983–1992).** 8,411 crash landings with engine power loss during take-off or landing; 437 pilot
    deaths (5.2 %). [Y — S13, which cites Rostykus et al., JAMA 1998; the abstract was not read on PubMed]

### E. Automation acting on a bad sensor

38. **MCAS (B737 MAX).** On both accident flights, recorded AoA on one side was about 20° (Lion Air) or about 59° (Ethiopian) higher than
    on the other. "These erroneous AOA sensor inputs resulted in the MCAS activating". The pilots' responses "did not match the
    assumptions of pilot responses" used in the hazard classification. The failure-mode tests had not simulated the erroneous AoA itself.
    [D-ag, S12 PDF pp. 5, 7] — Analogy [Y]: an automatic in-flight engine shut-down triggered by a canopy sensor makes **one sensor fault
    into a forced landing**, as a false input made MCAS act.

## Comparison of options (Extra NG retrofit)

Fatality figures are from §D. "Fail-free" means a failure of the device cannot take away engine power or control in flight.

| Option | What it does | Stuck/failed engaged | Fails free / dead | Nuisance | Defeat route and evidence | Fail-safe / fail-free design | Verdict [Y] |
|---|---|---|---|---|---|---|---|
| A. Alert only (light + aural, armed by throttle advance), cf. 25.703 | Warns | Constant light/tone → learned dismissal (G-OALB #12) | Silent miss; latent unless self-tested (TOWS #3, #5, #6) | Drives breaker-pulling (NW255 #5) and threshold creep (DL1141 #7) | CB pull, ignore, tape over | Self-test, "CANOPY SYS" caution, latch-engagement sensing (#11) | Necessary but not enough (CIAIAC #4) |
| B. **Ground take-off gate** (our proposal): solenoid detent blocks forward throttle travel past run-up power while unlocked AND on ground AND IAS & GS < 30 kt | Physically limits operation before take-off (CS 23.679(b)(2) pattern) | On ground: no-go, safe. In air (mechanical jam): could stop re-advance past run-up power → needs breakout | Reverts to alert-only (A) | Each false gate = a stop at the holding point; repeated → override habit | Push-through (G-IV PIC pressed on, lock pin broke #18); disconnect (HVBG #22, belt #27) | Blocks forward motion only, never pulls the throttle back; arms only on ground; latches out once passed in a run; spring-free when unpowered; mechanical breakout for jam; functional test, not drawing review (#17); recurring check (#20) | **Recommended**, with changes below |
| C. Ground-only ignition/mixture cut or start inhibit | Kills or prevents engine on ground when unlocked | Engine cannot start: no-go. Logic error in air = engine loss | Reverts to A | High if pilots start/taxi with canopy open (unknown for Extra) | Disconnect, like the belt interlock that blocked low-speed use (#27) | Needs WOW/airspeed logic as robust as B; any logic fault in air = option E | Not recommended: same benefit as B, much worse failure mode |
| D. Automatic brake hold until locked | Holds brakes | Brakes stuck on in the roll → ground loop/nose-over in a tailwheel aircraft [Y] | Reverts to A | Moderate | Disconnect | Hard to make fail-free on a tailwheel type | Not recommended |
| E. **Automatic engine shut-down / power cut in flight** | Cuts power when canopy unlocked | — | — | Every false trigger = engine failure after take-off | — | Cannot be made fail-free: its success state is the hazard | **Reject.** Turns an 11.8 % fatal event (#29) into a ~19 % (13/68) to 39 % fatal event (#30), 56 % if the pilot turns back (#31); CS 23.679(c) principle (#13); MCAS analogy (#38) |
| F. Take-off power limiter (ECU/prop) | Caps power until locked | On ground = B. In air = a **partial** power loss, the worst kind (#33) | Reverts to A | As B | As B | Only acceptable if ground-only, then it is B with more parts (AEIO-580 has no FADEC [Y]) | Not recommended |
| G. Mechanical latch fix (positive over-centre, engagement window) | Removes the error | — | — | none | none | Out of scope of "alert device" but strongest | Recommend in parallel |

## Design implications [Y]

All items in this section are R7 interpretation.

1. **Keep the in-flight shut-down rejected.** On true events it raises P(fatal) from about 0.12 to at least about 0.19. On false triggers it
   adds pure risk. The take-off roll is where to act: 17 roll events, 0 fatal (#29); low-speed rejects are benign (#31, #35).
2. **The gate is an "unmistakable warning" in the FAA's sense (#14).** That is its main argument over alert-only (#4, #17).
3. **Replace the 50 N push-through as the normal override.** Make it "a separate and distinct operation" (#15), e.g. a guarded release
   trigger on the throttle. Show the reason ("CANOPY") at the throttle. The G-IV PIC met an unexplained stop and pushed on (#18).
   Keep a higher **mechanical breakout** force only as protection against a jammed detent in flight.
4. **Log every override and every gate event** (time, sensor states) for the next inspection. Defeat thrives where it has no consequence
   (#24). Logging also finds the flaky sensor that would otherwise cause G-OALB-style dismissal (#12).
5. **Sense latch engagement, not lever position** (G-IIDY #11; RV-14, BD-10 #10). Use 2-out-of-2 sensing for LOCKED, with a disagreement
   caution (see R4 §2 item 3).
6. **Arm on actual power or RPM, not only on lever position** (FAA B727 recommendation #8). Do not tune the threshold to remove nuisance
   (DL1141 #7). Choose it from data: above taxi and run-up power, below the power needed to accelerate.
7. **Never block taxi or run-up with the canopy open** (belt interlock lesson #27; HVBG motive #23–24).
8. **Self-test and failure annunciation; treat "gate inoperative" as no-go** (TOWS latent faults #3, #5, #6). Verify by functional test,
   not drawing review (#17). Add a recurring test (#20).
9. **The gate does not help cruise openings** (24 of 126 rows, #29). Those need the alert and the mechanical fix.

### Monte Carlo parameter ranges [Y]

Evidence-based ranges, not measurements. Use triangular (min, mode, max) unless stated.

| Parameter | Regime | Range | Basis |
|---|---|---|---|
| P(pilot overrides gate \| canopy truly unlocked) | High trust: nuisance ≤ 1 per 500 take-offs, distinct-action override, reason shown | (0.01, 0.05, 0.15) | Bliss probability matching ≈ 1 − PPV (R4 H4); verifiable state lowers cry-wolf (R4 H13) |
| same | Low trust: recent nuisance history, ≥ 1 nuisance per 20 take-offs, or simple push-through | (0.20, 0.45, 0.80) | G-OALB dismissed a true alert after earlier nuisance (#12); G-IV pressed past the stop (#18); HVBG ~1/3–37 % (#22); belt non-use 33–41 % even with interlock (#26) |
| P(pilot overrides \| gate is false) | any | (0.85, 0.95, 0.99) | desired behaviour; each event moves trust towards "low" |
| P(permanent defeat per aircraft-year: CB pulled, solenoid disconnected) | low nuisance | (0.005, 0.02, 0.05) | no aviation data; scaled down from industry rates |
| same | high nuisance | (0.15, 0.30, 0.40) | HVBG ~1/3 (#22); 1/3 of drivers said they would disconnect (#27); NW255 breaker scenario (#5) |
| P(fatal \| canopy opens in initial climb) | — | Beta(10, 68), mean 0.118 | 9/76 (#29) |
| P(fatal \| canopy opens on take-off roll / reject < 30 kt) | — | Beta(1, 18), mean 0.05; realistic mode ≈ 0.005 | 0/17 (#29); BEA aborted take-off 0/1 and side note 5 (#31, #35) |
| P(fatal \| engine loss at low height, given an accident) | light single | (0.10, 0.19, 0.40); skew high for the Extra | BEA 13/68 = 0.19 and 12/31 = 0.39 (#30); Nall 0.168 (#36); high-power aircraft (#32) |
| P(fatal \| engine loss at low height, any occurrence incl. no accident) | light single | (0.02, 0.05, 0.12) | ATSB 3.7 % partial, 0 % complete (#33, [Y]); Rostykus 5.2 % (#37, [Y]) |
| P(fatal \| automatic shut-down triggered by a true open canopy in climb) | — | (0.15, 0.25, 0.50) | engine loss plus open-canopy distraction; ≥ both single figures |
| P(fatal \| false automatic shut-down, canopy closed) | — | same as engine loss given an accident | #30, #38 |

## NOT VERIFIED

1. ATSB *Avoidable Accidents No. 3* (partial power loss) and AR-2013-107: the ATSB site timed out (curl, then WebFetch). The numbers
   242/9 and 75/0 come from a search snippet only.
2. Rostykus et al., JAMA 1998: abstract not read at the source; figures via AOPA (S13) and a listing.
3. NHTSA 1970s interlock reports on rosap.ntl.bts.gov (DOT-1145, DOT-1167): **403 Access Denied**; not bypassed. Belt figures are from
   TRB SR 278 only, and that was read through a summarising fetch tool.
4. ISO 14119 (2013/2024) text: paywalled. Clause wording is from secondary sources.
5. Motorcycle side-stand cut-off defeat rates: no primary source found.
6. FAA AD mandating the G-IV gust-lock retrofit: not read.
7. Whether Extra NG pilots start and taxi with the canopy open, run-up RPM, and throttle force limits: POH/AMM not obtained.
8. AC 25.703-1 / AMC 25.703 text: not read (only the CIAIAC summary in S2 pp. 206–207).
9. The NW255 and DL1141 page numbers come from OCR copies. Page "~41" (DL1141 fleet survey) is estimated from the PDF page offset.
10. No certified canopy-to-throttle/ignition interlock was found on any light aircraft or gyroplane. Absence of evidence only.
11. All Monte Carlo ranges are R7 judgement. They are anchored on the cited counts but not fitted to data.
