# 08 · Past Ideathon challenges (2023, 2024) — and why there is no 2022

Prepared 2026-10-25. Tags as in `00_overview.md`: **[D]** read from the source in this session ·
**[A]** read through a fetch summary (a small model quoted or paraphrased the page; not read line by line) ·
**[Y]** judgement. The challenge cards are summarised, not copied; numbers are given as printed.

## 1. There was no 2022 Ideathon

- EUROAVIA's own history post says the **first** Ideathon was organised in **2023**, as a two-phase
  hackathon [A: blog.euroavia.eu, "Chapter 9 – The comeback (2022-2023)", 20 Jan 2025].
- The Ideathon site lists only the 2023 and 2024 editions; `ideathon.euroavia.eu/2022-edition/` returns
  HTTP 404 [D, fetched 2026-10-25].
- EUROAVIA events of 2022 that can be mistaken for it: Air Cargo Challenge (Munich, July 2022), the Airbus
  Sloshing Rocket Workshop finals, and the new Future & Beyond career project [A].

## 2. 2023 edition (first edition)

Format [D: `prev_guess/00_general/past_competitions/brochure-2024.pdf` p. 6; A: 2023 edition page, Ansys blog]: phase 1 in
Terrassa (3–7 Sep 2023, 24-hour competition per `00_overview.md`), 5 teams / 23 participants, each team
chose one challenge; phase 2 (final) in Munich (5–9 Nov 2023), 2 teams / 8 participants, with new
challenges. Winner: UniBOss (EUROAVIA Forlì-Bologna); second EUROAVIA Bucharest [A: Ansys blog].

### 2a. Ansys — "Design and mission optimization of a crisis response aerial vehicle" (phase 1 card)

Source: `prev_guess/00_general/past_competitions/Ansys-challenge.pdf`, 4 pages [D, read in full 2026-10-25].

- **Task, leg 1:** conceptual design of a *medium-size* aircraft for crisis response (e.g. search and
  rescue), following a simplified workflow from Raymer, *Aircraft Design: A Conceptual Approach* (6th ed.)
  and Anderson, *Aircraft Performance and Design*; produce the basic performance parameters.
- **Requirements:** cruise range ≥ 1300 km · loiter 30 min · stall 150 km/h · max speed 500 km/h ·
  service ceiling 10 000 m · rate of climb 10 m/s · take-off ground roll 800 m · crew 4, up to 10
  passengers, 200 kg supplies.
- **Scope:** focus on meeting the performance criteria; do not go into configuration, structure or
  stability detail. Simplifying assumptions, educated guesses and omitted calculations are acceptable if
  justified; teams are judged on the engineering approach as a whole. Explicit warning about unit
  conversions.
- **Task, leg 2:** plan the optimal flight path to, from and within a predetermined search area for the
  best coverage with on-board imaging sensors, within fuel and performance limits, using Ansys STK.
- **Skills listed:** aircraft design fundamentals, mission planning, prioritisation and time management.
  Help links: STK help, Aviator, area coverage, a quadcopter example.

Our solution of this card: `04_2023_example_solution.md`, tool status `07_gap_analysis.md` §7–§8.

### 2b. GTD — "Monitoring and predictive maintenance of on-board reusable systems" (phase 1 card)

Source: `prev_guess/00_general/past_competitions/GTDs-challenge.pdf`, 3 pages [D, read in full 2026-10-25].

- **Context:** reusable launchers; two levers — real-time awareness of the launcher's system status in
  flight, and use of flight data for predictive maintenance on the ground before the next flight. Framing
  questions: the real cost impact of reusability on launch operations, and which strategies optimise it.
- **Task:** define the strategy/methodology for (1) an on-board system that monitors the launcher in
  flight — *which parameters to monitor and collect* — and (2) post-flight data processing to diagnose the
  first stage/booster on the ground — *what is degraded, what must be maintained, what has failed* — so
  that turnaround can be planned.
- **Encouraged methods:** IVHM (integrated vehicle health monitoring), degradation models, supervised
  models, regression; the in-flight data may be simulated. Model nominal and failure dynamics of the
  critical parameters and train a predictive-maintenance system.
- **Skills listed:** launcher equipment (sensors, actuators, avionics), reusability concepts, numerical
  modelling (MathWorks or similar), data mining (neural networks, machine learning).

### 2c. The Munich final

**Who set it:** both partners — the EUROAVIA finals post names "GDT Systems" (read: GTD) and ANSYS, each team
being assigned a task; 24 hours in dedicated rooms; finalists UniBOss (AS Forlì-Bologna) and Ad Mundum
(AS Bucharest); UniBOss won with "great knowledge of the tool provided by ANSYS" and a solution the sponsor
had not expected [A: blog.euroavia.eu "Ideathon Finals in Munich", 27 Dec 2023]. The post does not describe the
tasks.

**The Ansys STK scenario ("Operation Skywatch")** — source: Ansys blog "University Students Develop
Mission-Ready Skills with STK", 23 Feb 2024 (S. Coleman, J. Procario) [A]. The article says the two finalists
completed *new* challenges in Munich but does not state that this scenario was the final's; it differs from the
phase-1 card, so it is most likely the final [Y].

- **Scenario (fictional):** a group of students trapped by an avalanche on Mount Everest (Sagarmatha National
  Park, Nepal), having ignored warnings of a (fictional) Lukla meteorological agency; this year's competitors
  are the rescuers.
- **Task 1 — asset visibility:** do the climbers' personal locator beacons (PLBs) get enough GPS reception to
  fix the group's position?
- **Task 2 — multi-hop visibility:** assuming they do, can the PLB distress signal reach the command centre by
  relaying through the Cospas-Sarsat constellation (search-and-rescue satellites in GEO, LEO and MEO)?
- **Task 3 — UAS trajectory, sensor and coverage:** after the distress ping, a UAS with a thermal imaging sensor
  is sent; design its trajectory to survey as much of the area as possible (sensor coverage analysis).
- **Task 4 — communications:** a rescue helicopter flies the group back to the command centre and the pilot must
  report the group's health in flight; students compared frequency bands and modelled a transmitter and a
  receiver to set up the best two-way link. The article gives no link budget numbers, ground stations or data
  rates.
- Tool: STK throughout; EUROAVIA's president is quoted that the challenge would not have been possible without it.

**GTD's final task:** not described in any source found.

## 3. 2024 edition

Format [D: `brochure-2024.pdf` pp. 3–5]: theme **sustainability**; phase 1 Toulouse (ENAC, 26–31 Oct 2024),
phase 2 Zagreb (1–6 Dec 2024); teams of 3–4 choose one company challenge in phase 1, each challenge's
winner goes to the final; **48-hour** competition. Sponsors/challenge providers: Ansys, EUROCONTROL, İGA
(Istanbul Airport academy) [A: 2024 edition page, finale blog of 28 Dec 2024]. Toulouse: 33 participants,
9 teams, 48 h with mentors; the top three teams went to Zagreb, unnamed in the post [A: blog.euroavia.eu
"A Journey through Innovation, EUROAVIA Ideathon 2024 from AS Toulouse", 28 Nov 2024]. Final: started 2 Dec
2024, 14:15 CET, 48 h, each team assigned a unique challenge [A]. Winner: AVAION (AS Patras) [A]; `00_overview.md` records it as the EUROCONTROL challenge
[A, not re-checked].

**The 2024 challenge texts were not found:** the edition page, the brochure, the Toulouse and Zagreb posts give
no titles or descriptions, the regulations pages return 404, and three searches (2026-10-25) found no published
cards (only the 2023 GTD and Ansys cards are on the site). Ask the organisers, or past
participants, if they matter.

## 4. What this means for 2026 [Y]

- Every known Ansys challenge was **conceptual design + digital mission engineering (STK)**, not CFD:
  2023 phase 1 (aircraft sizing + coverage) and 2023 final (UAS + sensor + visibility/communications).
  A 2026 Ansys task in the same family would add satellite visibility and link-budget questions, which
  `aerokit` does not cover (no orbit propagation, no access/visibility or RF link model).
- Non-Ansys challenges were **systems/data** problems (GTD: IVHM and predictive maintenance) and, in 2024,
  aviation operations providers (EUROCONTROL, İGA) under a sustainability theme — expect air-traffic,
  airport or emissions questions.
- 2026 differs in format: four challenges, every team does all four (`00_overview.md` §1), so breadth and
  fast justified estimates matter more than one deep model.
