# R8 — Reaction time and time budgets: what alert design the take-off needs

Read by **subagent R8-timing**, **2026-11-05**. Purpose: turn reaction-time data and a take-off time budget into
numbers for the canopy alert (stages, onset latency, gate speed, voice timing, wording).

**Tags.**
- **[D-ag]**: read at the source by R8 in this session. URL and page, section or table are given.
- **[D-ag abstract]**: only the abstract was read (Europe PMC REST record or repository page).
- **[D-ag (R6)] / [D-ag (R7)] / [D-ag (R4)]**: read at source by an earlier subagent; R8 did not re-open it. See that file.
- **[Y]**: secondary source, my calculation, or my interpretation.

Downloads (untrusted data): `D:\tmp_ideathon\easa\dl\r8_timing\`. Text was extracted with `python -I` scripts kept
outside that folder (session scratchpad). The arithmetic is in `timeline_calc.py`; its full printed record is
`timeline_calc_output.txt` (same scratchpad, `...\scratchpad\r8\`). Every number in §B and §E comes from that record.

**Scope.** Does not repeat R4 (AC 25.1322-1 inhibits, cry-wolf), R6 (Callan 2018, Dehais), R7 (Politis 2016 RT per
modality, Patterson pulse timing, voice length, vibration). It uses their numbers by reference.

## Sources

| # | Source | URL | What R8 read |
|---|---|---|---|
| S1 | 14 CFR 25.109 Accelerate-stop distance (eCFR, version 2025-01-01) | https://www.ecfr.gov/api/versioner/v1/full/2025-01-01/title-14.xml?part=25&section=25.109 | (a)(1)(i)–(iv), (a)(2)(i)–(iii), (f) |
| S2 | FAA AC 25-7D, *Flight Test Guide for Certification of Transport Category Airplanes*, 05/04/2018 | https://www.faa.gov/documentLibrary/media/Advisory_Circular/25-7D.pdf | §4.3.6.1–4.3.6.9 and Fig. 4-1, pp. 4-22 to 4-24 (PDF pp. 54–56) |
| S3 | Landman, Groen, van Paassen, Bronkhorst, Mulder (2017). The influence of surprise on upset recovery performance in airline pilots. *Int. J. Aerosp. Psychol.* 27(1-2):2–14 | https://publications.tno.nl/publication/34625732/BZHKWE/landman-2017-influence.pdf | abstract; method (PDF pp. 5–7); Table 3 (PDF p. 10) |
| S4 | NLR-CR-2018-242, *Startle Effect Management*, final report of EASA research project EASA_REP_RESEA_2015_3 (NLR with KLM), 2018 | https://www.easa.europa.eu/sites/default/files/dfu/EASA_Research_Startle_Effect_Managements_Final_Report.pdf | §2.2.2 (p. 13, PDF p. 19); p. 21 (PDF p. 27) |
| S5 | Greenall J. (Balearic Helicopters), *Emergencies – training the brain*, slides hosted by EASA | https://www.easa.europa.eu/en/downloads/143329/en | slide 11 |
| S6 | Gardini, Chiavelli, Scarpari, de Andrade (2022). Conceptual models of startle, surprise and automation bias... *J. Aerosp. Technol. Manag.* 14:e3022 (review) | https://jatm.com.br/jatm/article/download/1282/954/6238 | p. 3 (summaries of Casner 2013 and Martin 2016) |
| S7 | Der & Deary (2017). The relationship between intelligence and reaction time varies with age... *Intelligence* (PMC5608941) | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5608941/fullTextXML | introduction (Hick 1952); Table 1 |
| S8 | Woods, Wyma, Yund, Herron, Reed (2015). Factors influencing the latency of simple reaction time. *Front. Hum. Neurosci.* 9:131 | https://public-pages-files-2025.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2015.00131/text | abstract (the page served only the abstract) |
| S9 | Green M., "Driver reaction time" (web article by the author of Green 2000) | https://www.visualexpert.com/Resources/reactiontime.html | sections Expectation, Urgency, Cognitive Load, Psychological Refractory Period, Response Complexity, Age |
| S10 | NHTSA, Visual-Manual Driver Distraction Guidelines, 78 FR 24818 (26 Apr 2013) | https://www.govinfo.gov/link/fr/78/24861 (PDF of the whole notice) | FR pp. 24826, 24828, 24850, 24854, 24861 |
| S11 | Suied, Susini, McAdams (2008). Evaluating warning sound urgency with reaction times. *J. Exp. Psychol. Appl.* PMID 18808274 | Europe PMC REST search API | abstract |
| S12 | Haas & Casali (1995). Perceived urgency of and response time to multi-tone and FM warning signals in broadband noise. *Ergonomics*. PMID 7498190 | same | abstract |
| S13 | Marshall, Lee, Austria (2007). Alerts for in-vehicle information systems: annoyance, urgency, and appropriateness. *Hum. Factors*. PMID 17315851 | same | abstract |
| S14 | Hellier, Edworthy, Weedon, Walters, Adams (2002). The perceived urgency of speech warnings: semantics versus acoustics. *Hum. Factors*. PMID 12118864 | same | abstract |
| S15 | Scrivens L.S. (2024). *Study on pilot response time to reject takeoff with one engine inoperative.* MS thesis, Florida Institute of Technology | https://repository.fit.edu/etd/1482 | abstract |
| S16 | Extra Aircraft product pages, Extra NG and Extra 330LX | https://extraaircraft.com/ng ; https://extraaircraft.com/330lx/ | specification lists |
| S17 | AOPA aircraft guide, Extra 300 | https://www.aopa.org/go-fly/aircraft-and-ownership/aircraft-guide/aircraft/extra-300 | specifications |
| S18 | Team dataset `R2_occurrences.csv` + `R5_occurrences_add.csv` (read at source by R2/R5) | local | `notes` column of the 26 lock-related initial-climb rows that state a height (my parse) |

## Findings

### A. How long people and pilots take to respond

1. **Simple RT in the lab is ~0.2–0.35 s.** Mean simple RT 231 ms (213 ms after hardware correction), n = 1469, age
   18–65 [D-ag abstract, S8]. UK population cohorts: simple RT mean **290 / 318 / 354 ms** at ages 30 / 50 / 69
   (SD 74 / 97 / 112) [D-ag, S7 Table 1].
2. **One choice more costs ~0.25–0.4 s (Hick–Hyman).** In the same cohorts the 4-choice RT mean is **539 / 623 / 729 ms**
   (SD 72 / 93 / 105) [D-ag, S7 Table 1]. So four choices add 249 / 305 / 375 ms over simple RT [Y, arithmetic].
   S7 restates Hick (1952): RT grows with the number of choices [D-ag, S7 introduction]. The usual form
   RT = a + b·log2(N + 1) was not read at a primary source [Y].
3. **Age.** Simple RT slows by **0.55 ms per year**; stimulus detection time does not change with age; the slowing is
   on the motor side [D-ag abstract, S8]. From age 30 to 69: +64 ms simple, +190 ms 4-choice [Y, from S7 Table 1].
   Green: simple reflexive responses slow little in healthy older adults; complex tasks slow much more [D-ag, S9 Age].
4. **Expectation dominates.** Green's best estimates for braking: fully expected **0.7 s** ("0.5 is perception and
   0.2 is movement"), unexpected but common **about 1.25 s**, surprise **1.5 s** (side incursion) [D-ag, S9
   Expectation]. He says there is no single universal RT [D-ag, S9]. These values come from his web article; the
   2000 paper itself (Transp. Hum. Factors 2(3):195–216) was blocked (403) and **not read**.
5. **Load and second responses.** Cognitive load adds "0.3 to as high a second or more" [D-ag, S9 Cognitive Load].
   After one response, a new response is slower (psychological refractory period; no number given) [D-ag, S9].
   Steering is 0.15–0.3 s faster than braking [D-ag, S9 Response Complexity].
6. **Real flight, aural alert under load:** mean hit RT 792 ms, ~38 % missed [D-ag (R6), Callan 2018].
   **Driving lab, braking to warnings:** A 0.77 s, V 0.77 s, T 0.78 s, multimodal 0.71–0.73 s [D-ag (R7), Politis
   2016]. These are **expected** cues in a lab; they are a floor, not a design value [Y].
7. **Surprise doubles pilot response time on a trained manoeuvre.** 20 airline pilots, motion simulator, stall:
   response time **2.02 s (SD 0.92) anticipated vs 4.12 s (SD 1.08) surprised**, Δ = 2.10 s, p < .001, d = 2.09
   [D-ag, S3 Table 3]. Response time ran from tailwind onset to first significant control input, so it includes the
   time the stall took to develop [D-ag, S3 PDF p. 7].
8. **Casner 2013 (747 simulator, 18 pilots, via a review):** unexpected low-altitude stall: response times **1.9 to
   18.2 s**; two pilots never applied maximum power [Y, secondary — S6 p. 3; original not read].
9. **Startle.** The reflex lasts < 1 s (mild) up to 1.5 s (intense). Startle stops ongoing action; the disruption
   lasts **100 ms to 3 s for simple tasks and up to 10 s for complex motor tasks** (NLR citing Rivera 2014)
   [D-ag, S4 §2.2.2, p. 13]. A loud sound startles even when announced [D-ag, S4 p. 15 (PDF p. 21)]. Training targets
   the effects beyond 3 s [D-ag, S4 p. 21]. A helicopter chief pilot's EASA-hosted slides say physical recovery
   "up to 3 seconds", cognitive 30–60 s (no data) [D-ag, S5 slide 11; weak].
10. **Martin et al. 2016 (737 simulator, 18 pilots):** startle (cargo-fire bell plus bang) before a go-around. The
    review reports impaired performance [Y, secondary — S6 p. 3]. A web search summary gives "about 5 s" more delay
    for affected pilots [Y, NOT VERIFIED; the paper is behind a Hogrefe paywall and was not tried].
11. **Rejected take-off RT (twin, simulator, n = 7):** unannounced engine failure on the roll; **median < 2 s, mean a
    little over 3 s** including outliers; more multi-engine hours and recent experience gave faster responses
    [D-ag abstract, S15].
12. **What certification assumes.** 14 CFR 25.109 adds "a distance equivalent to 2 seconds at the V1" to both
    accelerate-stop distances [D-ag, S1 (a)(1)(iv), (a)(2)(iii)]. AC 25-7D: the recognition time used in the AFM is
    "the demonstrated time or one second, whichever is greater", measured on test pilots who know a failure is coming;
    if a warning light is used, the time runs from the failure through light-on to first action [D-ag, S2 §4.3.6.4,
    p. 4-24]. Each later action gets +1 s; **+2 s if a command to another crew member is needed** [D-ag, S2
    §4.3.6.7]. The time delays "are not intended to allow extra time for making a decision" [D-ag, S2 §4.3.6,
    p. 4-23]. [Y] So 1 s is a floor for a trained, primed pilot doing one action — not a median for a surprised one.

**Design RT used below [Y].** For a surprised pilot who must perceive a red/voice/vibration alert at take-off power
and start closing the throttle: **median 1.5 s, 95th percentile 3.0 s.** Basis: Green surprise 1.5 s (A4);
RTO median < 2 s (A11); AC 25-7D floor 1 s (A12); 95th from the RTO mean > 3 s (A11) and the 3 s startle disruption
(A9). It assumes the alert **is** noticed. With ~38 % of aural alerts missed under load (A6) the real upper tail is
longer; the redundant lamp and vibration are there to cut that tail. Then add +1 s to the next action (brakes) (A12).

### B. Time budget of an Extra-class take-off [Y unless tagged]

13. **Aircraft data read.** Extra NG: Lycoming AEIO-580-B1A, 315 hp; MTOW 950 kg (normal), 820 kg (acro);
    Vs **56 kt at 950 kg**, 50 kt at 750 kg [D-ag, S16 NG]. Extra 330LX: Vs 60 kt at 950 kg, 55 kt at 820 kg; two-pilot
    acro MTOW 870 kg [D-ag, S16 330LX]. Extra 300: 300 hp, 2,095 lb, Vs1 60 kt [D-ag, S17]. **No take-off distance,
    lift-off speed or climb rate was found at a readable source** (see NOT VERIFIED).
14. **Assumptions** (all [Y]): lift-off **65 kt** (≈ 1.16 × Vs 56 kt). Ground roll: **short case 112 m** (the
    Extra 330LX POH worked example at 870 kg, seen only in a search snippet, not verified) and **long case 200 m**
    (heavy, warm, grass). Constant acceleration. Braking deceleration 2.5 m/s² (tailwheel, dry hard runway, no
    nose-over). +1 s from throttle closed to braking.
15. **Results** (`timeline_calc_output.txt`):
    - Short case: a = 4.99 m/s² (0.51 g); **30 kt at 3.1 s (24 m), 40 kt at 4.1 s (42 m), lift-off at 6.7 s**.
    - Long case: a = 2.80 m/s² (0.28 g); **30 kt at 5.5 s (43 m), 40 kt at 7.4 s (76 m), lift-off at 12.0 s**.
    - Constant acceleration overstates early speed (the engine needs ~1 s to reach full power). This makes the
      budget slightly pessimistic, which is the safe side.
16. **Alert onset options.**
    - **A — throttle-lever switch.** The latch state has been stable through the taxi, so the 0.5 s latch
      persistence is already satisfied at t = 0. Lever switch debounce 0.2 s + logic 0.05 s + voice start 0.1 s =
      **0.35 s**.
    - **B — rpm threshold.** rpm crosses ~1.0 s after the lever moves, then 0.5 s persistence (if applied to the
      trigger) + logic + voice start = **1.65 s**.
17. **Margin to a 30 kt reject gate** (time left after alert onset; then speed at the pilot's first action):

    | Case | Onset | 30 kt reached | Time left after onset | Speed at median action | Speed at 95th action |
    |---|---|---|---|---|---|
    | Short roll (112 m) | A, 0.35 s | 3.1 s | 2.7 s | 18 kt | 33 kt |
    | Short roll (112 m) | B, 1.65 s | 3.1 s | 1.4 s | 31 kt | 45 kt |
    | Long roll (200 m) | A, 0.35 s | 5.5 s | 5.2 s | 10 kt | 18 kt |
    | Long roll (200 m) | B, 1.65 s | 5.5 s | 3.9 s | 17 kt | 25 kt |

    Hand-written table; numbers from `timeline_calc_output.txt`.
    - [Y] With the rpm trigger (B) in the short case, **even the median pilot acts after 30 kt**. With the lever
      switch (A), the median pilot acts at 18 kt and the 95th at 33 kt.
    - Stop distance is not the limit: total distance to a stop is 35 m (A, median) to 185 m (B, 95th, from 45 kt)
      [Y, record]. The limit is tailwheel control under hard braking at 40+ kt and the startle risk, not runway.
18. **Voice length vs speed.** "CANOPY, CANOPY" ≈ 1.2 s [D-ag (R7), auditory rec. 10]. Onset A, short case: first
    pair ends at **1.5 s / 15 kt**, second pair at 2.8 s / 27 kt. Onset B: first pair ends at 2.9 s / 28 kt
    [Y, record]. So **at most two voice pairs fit before 30 kt; the decision rests on the first one.**
19. **After lift-off.** Time from lift-off to height, with 2 s transition (assumed) and climb 1,000 / 2,000 /
    3,000 fpm: **100 ft at LOF + 8 / 5 / 4 s; 300 ft at LOF + 20 / 11 / 8 s** [Y, record]. No Extra climb rate was
    read at source.
20. **Where openings happen in the climb (our data).** 26 lock-related initial-climb rows state a height in the
    notes (4 excluded because the height is not the opening height). Number next to "ft" (upper bound of a range):
    **median 200 ft; 31 % at ≤ 50 ft; 42 % at ≤ 100 ft; 65 % at ≤ 300 ft** [Y, my parse of S18; mixed types incl.
    gliders on tow, not Extra-specific].
21. **Why openings come after lift-off.** Suction on the canopy scales with dynamic pressure q ∝ V². At 92 kt q is
    **2.0 ×** its lift-off value; at 110 kt **2.9 ×** [Y, record]. A partly latched canopy can hold on the roll
    and let go in the climb. [Y] This fits 76 of 126 lock-related events in the initial climb vs 17 on the roll
    (`00_INDEX.md`). The fix must come from **sensors before take-off**, not from what the pilot feels on the roll.

### C. What the budget means for the design [Y unless tagged]

22. **The best decision point is stationary.** On the roll the budget is 1.4–5.2 s (B17). Stopped at the holding
    point or line-up, it is unlimited, and a glance check is safe. The strongest stage is a red alert at
    **run-up / line-up power with ground speed ≈ 0**, before t = 0.
23. **Trigger on the lever, not on rpm or airspeed.** It buys 1.3 s (onset 0.35 s vs 1.65 s), which is the whole
    difference between "median pilot acts below 30 kt" and "median pilot acts above 30 kt" in the short case (B17).
    Keep the 0.5 s persistence on the **latch sensors**, which are stable during taxi; do not add it to the trigger.
24. **An automatic ground gate gives more time than any alert.** An automatic action at lever advance acts at
    ~0.35–0.5 s (≈ 3–5 kt, short case). It does not depend on RT, surprise or missed alerts (A6–A11). Its false trip
    costs only a stop at walking speed. An alert alone depends on a 1.5 s median / 3.0 s 95th human RT.
25. **One alert, one meaning, one action.** Each extra choice costs ~0.25–0.4 s (A2). Below the gate, red means
    "close the throttle and stop". No diagnosis on the roll.
26. **Do not verify on the roll.** Glances away from the road over **2.0 s** raise crash/near-crash risk; NHTSA's
    criteria: mean glance ≤ 2 s, 85 % of glances ≤ 2 s, total ≤ 12 s [D-ag, S10 pp. 24826, 24828]. Reading 170
    characters took glances ≤ 1.14 s each [D-ag, S10 p. 24850, citing Hoffman 2005]. [Y] On a take-off roll any
    head-down look is costly; the procedure is reject first, look at the bolt windows when stopped. Each bolt window
    should be readable in **one glance under ~1 s** (one colour band, no reading).
27. **Checklist placement.** Put the canopy item **last** in the line-up check, right before the throttle, so the
    check and t = 0 are seconds apart. Back it with the system: green must be earned by the sensors (design rule).
    No primary source read on first-vs-last item omission for this case (see NOT VERIFIED).
28. **Voice deferral of a NEW alert (40 kt → LOF + 10 s).** At LOF + 10 s the aircraft is at ~130 / 270 / 400 ft
    (1,000 / 2,000 / 3,000 fpm) [Y, record]. Our data put the median opening at 200 ft and 42 % at ≤ 100 ft (B20). So
    the deferred voice arrives **after about half of initial-climb openings would already have happened**. The lamp
    and vibration are not deferred. This is a real trade-off with the missed-alert risk at peak load (R4, R7). An
    option to test: shorten to LOF + 5 s (~100–150 ft at 2,000–3,000 fpm).
29. **Avoid commanding an abort above the gate.** Startle stops ongoing action for up to 3 s and can cause abrupt
    inputs (A9). A strong throttle-hand vibration above the gate invites a power cut at 50–65 kt or in the climb
    (R7 haptic finding 36: 22 % false-alarm braking with strong hand vibration). Suggest: vibration only below the
    gate speed; above it, lamp (and later voice) only.

### D. Urgency mapping and startle

30. **Shorter gaps = faster responses.** RT falls as the inter-onset interval of pulses falls; irregular timing
    captures attention [D-ag abstract, S11]. Higher level and shorter inter-pulse interval raise urgency and cut RT;
    RT falls as perceived urgency rises [D-ag abstract, S12]. Edworthy/Hellier urgency parameters and Patterson pulse
    timing (inter-pulse < 150 ms for urgent): see R7 auditory findings 18, 30 [D-ag (R7)].
31. **Urgency has a cost: annoyance.** Pulse duration, inter-pulse interval, duty cycle and sound type raise urgency
    more than annoyance; for low-urgency situations annoyance drives perceived appropriateness [D-ag abstract, S13].
    [Y] Use urgent sound only for red at take-off power; keep the taxi amber chime soft (R7 auditory rec. 11).
32. **Words carry urgency too.** Urgent speaking style (higher pitch, wider range, louder) raised urgency; word
    meaning also mattered when acoustics were held equal [D-ag abstract, S14]. AC 25.1322-1 advises against a voice
    with "tension or panic" [D-ag (R4)].
33. **Startle limit.** ISO 7731 example of a fright reaction: > 30 dB rise in 0.5 s [D-ag (R7) auditory finding 15].
    [Y] Requirement: urgent, but onset ramped and level ≤ 15–25 dB above masked threshold (R7), so the red alert does
    not itself trigger the 0.1–3 s startle freeze (A9).

## E. Timeline (t = 0 at throttle forward)

Hand-written table. Speeds and times from `timeline_calc_output.txt` (constant acceleration, lift-off 65 kt).
RT stage assumes onset A (lever switch) unless marked B. Margin = time left to the 30 kt gate (negative = acts after it).

| t short / long (s) | Speed short / long (kt) | Event | Alert stage | Pilot RT (median / 95th) | Margin to 30 kt gate (short / long) |
|---|---|---|---|---|---|
| < 0 | 0 | Taxi, run-up, line-up; aircraft stationary at the end | Amber in taxi; proposed red + voice at run-up/line-up power | not limited | unlimited |
| 0.0 | 0 | Throttle lever starts forward | — | — | 3.1 / 5.5 s to gate |
| 0.35 | 3 / 2 | Onset A: lever switch trips | Red flashing + "CANOPY, CANOPY" + vibration, all at once | starts | — |
| 1.0 / 1.0 | 10 / 5 | rpm passes threshold (trigger B) | — | — | — |
| 1.5 / 1.5 | 15 / 8 | First voice pair ends (A) | Voice pair 2 starts | — | — |
| 1.65 | 16 / 9 | Onset B: rpm trigger + 0.5 s persistence | (B) all channels start | starts (B) | — |
| 1.9 | 18 / 10 | Median pilot starts closing throttle (A) | — | 1.5 s | +1.2 / +3.6 s |
| 2.8 / 2.8 | 27 / 15 | Second voice pair ends (A) | Rough tone burst follows (R7) | — | — |
| 3.1 / 5.5 | 30 / 30 | 30 kt: current reject gate closes | Gate ends; voice of a new alert deferred | — | 0 |
| 3.2 | 31 / 17 | Median pilot acts (B) | — | 1.5 s (B) | −0.1 / +2.3 s |
| 3.4 | 33 / 18 | 95th-percentile pilot acts (A) | — | 3.0 s | −0.3 / +2.1 s |
| 4.1 / 7.4 | 40 / 40 | 40 kt | — | — | — |
| 4.7 | 45 / 25 | 95th-percentile pilot acts (B) | — | 3.0 s (B) | −1.6 / +0.8 s |
| 6.7 / 12.0 | 65 / 65 | Lift-off (assumed) | Lamp stays red; no voice for a new alert | — | — |
| LOF + 3 to 5 | ~70–90 | 50 ft (31 % of climb openings by here) | — | — | — |
| LOF + 4 to 8 | ~80–100 | 100 ft (42 % of climb openings by here) | — | — | — |
| LOF + 10 | climb speed | ~130–400 ft (median opening 200 ft) | Deferred voice of a NEW alert starts | — | — |

In the margin column each cell gives short case / long case for the pilot in that row.

Table check: datawiz `tablo.denetle` was run on 2026-11-05 on the B17 table and on a numeric extract of this
timeline (t, short-case speed). **0 HATA.** One UYARI: mixed decimals in t (0.35 and 1.65 s vs one decimal elsewhere).
Deliberate: the two onset values are sums of 0.05 s steps (B16). Script `tablecheck.py` is in the R8 scratchpad.

## F. Numeric design requirements (proposed) [Y]

| # | Requirement | Number | Basis |
|---|---|---|---|
| T1 | Red + voice stage at run-up / line-up power while stationary (not only at take-off power) | ground speed < 5 kt | C22 |
| T2 | Take-off trigger from a throttle-lever position switch, not rpm or airspeed | onset ≤ 0.35 s after the switch trips; never > 0.5 s | B16, C23 |
| T3 | Latch-sensor persistence filter runs continuously in taxi, not restarted by the trigger | 0.5 s | B16 |
| T4 | Lamp, voice and vibration start together | within 50 ms of each other | R7 haptic; A6 |
| T5 | First "CANOPY, CANOPY" ends before 20 kt in the short case | ≤ 2.0 s after lever advance | B18 |
| T6 | No attention tone in front of the voice | 0 ms prefix | R7 auditory finding 25 |
| T7 | Reject instruction valid up to a gate that the 95th-percentile pilot can meet | gate ≥ 35 kt with onset A (95th acts at 33 kt, short case); or keep 30 kt and accept ~5 % act at 30–35 kt | B17 |
| T8 | If an automatic ground action is used, it acts on lever advance | ≤ 0.5 s, i.e. below ~5 kt | C24 |
| T9 | Vibration only below the gate speed | stops at gate speed | C29 |
| T10 | Red below the gate means one action: close throttle, then brake | 1 action + 1 s to brakes | A2, A12 |
| T11 | Urgent pulses: inter-pulse gap short, onset ramped, no sudden jump | gap < 150 ms; ≤ 30 dB rise per 0.5 s | D30, D33 |
| T12 | Bolt windows readable in one glance, when stopped | ≤ 1 s per window, total check ≤ 5 s | C26 |
| T13 | Canopy item last in the line-up check, right before throttle | last item | C27 |
| T14 | Re-check the new-alert voice deferral against opening heights | test LOF + 5 s vs LOF + 10 s | C28 |
| T15 | Design RT used for margins | median 1.5 s, 95th 3.0 s; +0.2 s for older pilots | A1–A12 |

Hand-written table.

## NOT VERIFIED / not obtained

1. **No Extra take-off roll, lift-off speed or climb rate at a readable source.** Tried once each:
   aeroexpo 330LX brochure (403); manualshive 330LX POH (blocked by "Anubis" bot protection); manualzilla 330LX POH
   (403); apstraining.com Extra 300L POH and spec sheet (404); pilotenschule.ch 330LX checklist and briefing (404).
   The 112 m ground roll at 870 kg and the 65 KIAS rotation come from search snippets only.
2. **Green (2000)** paper: Taylor & Francis 403. Only Green's own web article was read (A4).
3. **Martin et al. 2016** and **Casner et al. 2013**: only via a review (S6) or search summary. NASA NTRS search for
   Casner 2013 returned 0 results. PubMed web pages showed a cookie wall; abstracts came from the Europe PMC API.
4. **Hick (1952), Hyman (1953)** original papers: not tried (paywalled journals). Formula tagged [Y].
5. **Pilot RT percentiles** for a canopy-type alert at take-off: no study found. The 1.5 s / 3.0 s design values are
   my synthesis (§A, last paragraph).
6. **Checklist first-vs-last item omission rates**: not searched in this session. See R6 (Degani & Wiener, Dismukes &
   Berman) for what is on file.
7. Extra NG braking deceleration and the effect of hard braking at 40+ kt on a tailwheel aerobatic aircraft: no source.
8. The opening heights in B20 come from free-text notes, mixed aircraft types, and my exclusion of 4 rows.
