# EASA kit · 02 — The 4:00 talk (replaces the 7-minute slide plan of doc 23 §7)

**Why this file exists.** Doc 23 §7 plans 9 slides in about 420 s. The organisers' `Rules and Criteria.xlsx`
(`00_Common/rules_and_templates/originals_2026-11-05/`, read 5 Nov) says: *"4 minutes per challenge, followed by Q&A. You
will be cut off at 4:00"*, and P4 (5 points) asks for *"within 4:00, whole team involved"*. So: 6 slides, 225 s spoken,
15 s reserve. Everything cut here moves to backup slides for Q&A (P2, 7 points, includes Q&A).

**Updated 5 Nov after the official task** (`02_EASA/official_2026-11-05/00_OFFICIAL_TASK_vs_KIT.md`): certification is to be
disregarded, so the approval route is gone from the talk. The feedback elements named in the task (visual, auditory,
vibration, engine shut-down) are answered on slide 3 (kit `12`). Slide 1 now shows that three bodies disagree, which is the
theme of the EASA case-study presentation.

Speakers S1–S4 are placeholders; give each person one block and rehearse with a stopwatch. The word count and time per
block are printed by `easa_kit.py` at 2.3 words/s.

| t (s) | Slide — claim as title | Visual | Speaker | Criterion it serves |
|---|---|---|---|---|
| 0–35 | **1. Closed is not locked.** | two cards: *G-MIIL: three bodies, two stories* (AAIB: bonding → fatigue; BFU: not completely locked; EASA AD 2025-0156: partially or improperly locked) vs *what was missing* (no lock record; pilot sure he locked it; visual and handle check both missable) | S1 | P1 problem, R1 |
| 35–70 | **2. It happens early, on every type — and a door switch sees nothing.** | C5 (phase) left, C1 (miss by architecture) right | S1 | P1, P3 |
| 70–125 | **3. LOCK-SENSE: green must be earned.** | K4 architecture (four sensors → four cues + G1000) | S2 | P1 solution, P3 |
| 125–165 | **4. What the numbers say: 1 900× if pilots act, 3× if they do not trust it.** | C3 (cry wolf) + one line: "every single fault caught; only 2 double faults give a false green" | S3 | P2 persuasiveness |
| 165–200 | **5. Twelve steps to fit the alert.** | K3 process (Define → Design → Build & test → Operate, a test gate after each) | S3 / S4 | P1, R2 |
| 200–220 | **6. Record the lock now, remove the omission next.** | K1 ladder A1 → A3 → B → C | S4 | P2, R5 |
| 220–240 | reserve | — | — | P4 time |

## Spoken text (draft; trim to your own words, keep the numbers)

**S1 · slide 1 (35 s).** "On 2 April 2022 the canopy of Extra NG G-MIIL broke up at 184 knots. The AAIB found poor
bonding and fatigue cracks. The German State of Design disagreed, and EASA's airworthiness directive on this type targets
a canopy that is not properly locked. Three bodies, two stories, and nobody could prove which, because nothing recorded
whether it was locked. The pilot was sure he had locked it. Closed is not locked."

**S1 · slide 2 (35 s).** "We collected 241 investigated canopy and door openings. 126 were lock-related, and 76 of those
happened in the initial climb. On the Extra NG the handle sits at 70 millimetres both when it is locked and when it is
released, and the frame looks the same, so the visual check and the handle check can both be missed. A 'canopy closed'
switch misses every partial lock in our simulation."

**S2 · slide 3 (55 s).** "LOCK-SENSE puts one inductive sensor at each of the three shoot-bolt lugs, plus one seated
sensor, all on the fuselage side. Green CANOPY LOCKED lights only when all four agree, through a hardware AND. Taxiing
with the canopy open for air, the pilot gets amber and one chime, nothing more. Throttle forward while unlocked: red, the
voice 'CANOPY', the throttle knob vibrates under the hand that stays on it, and a ground-only gate holds the lever at
run-up power until a firm push. We never shut the engine down: most openings happen in the climb, where the engine is
what you need."

**S3 · slide 4 (40 s).** "With pilots who always act, the risk of taking off unlocked drops about 1 900 times. But if
nuisance alerts teach pilots to ignore it, the gain falls to about three times. So nuisance is a design requirement,
false alerts at most a tenth of the real hazard rate, and the gate turns ignoring the alert into a deliberate push. We
injected 13 faults into the real logic: every single fault is caught; only two double faults give a false green."

**S3/S4 · slide 5 (35 s).** "Twelve steps to fit it. Define: pick the aircraft, survey the latch and the panel, and list
how the checks get missed. Design: testable requirements, sensors and cues, the logic. Build and test: mount and rig with
a go/no-go gauge, wire it into the G1000 or a standalone unit, bench-test every fault, ground-test every state. Then a
flight check, pilot training, and a gauge check at every annual."

**S4 · slide 6 (20 s).** "And the next disputed investigation will not have to guess: the unit records the lock state.
No budget limit means a ladder: LOCK-SENSE now, then a powered lock that removes the omission itself. Our first step is
a bench test."

## Backup slides (Q&A only, in this order)

1. Feedback matrix and why no engine shut-down (kit `12`) — "why not shut the engine down?"
2. The organisers' microswitch example vs ours: one sensor per bolt, LOCKED not "closed", self-checking (kit `12` §4,
   K2) — "why not one microswitch?"
3. C2 trip window (67.5–68.7 mm at σ 0.3 mm) — doc 23 §6b Q7.
4. Fault-injection demo (`02_EASA/outputs/day/fault_demo.html`) — live, one person drives it.
5. Complacency sensitivity (1 138× / 2.6×) — §6b Q2.
6. Options B/C/D at depth (doc 23 §3.3) and the bond NDT for the AAIB cause — §6b Q10.
7. Data limits: rates are [Y] except the NUREG base rate — §6b Q1, Q9.

## Rehearsal check (tick before the slot)

- [ ] Full run under 3:50 twice in a row with a stopwatch.
- [ ] Every team member speaks at least one block (P4).
- [ ] Slide titles are the claims above (P3: "not walls of text").
- [ ] The words "would have prevented G-MIIL" appear nowhere.
- [ ] Someone has watched the case-study video of slide 39 (*Canopy Failures and Checklist Discipline*, latch styles at
      2:15) and can answer a question on it.
