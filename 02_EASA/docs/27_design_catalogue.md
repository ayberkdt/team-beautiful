# 27 · Design catalogue — where to sense, how fast to alert, what mechanics add, and what each tier costs

**What this adds to doc 26.** Four research notes from 5 Nov evening:
- `R8_canopy_latch_mechanisms.md`: how this class of canopy locks.
- `R8_similar_systems_effectiveness_cost.md`: similar warning systems, how well they worked, and their cost.
- `R8_reaction_time_design.md`: time budget and response times.
- `R8_mechanical_interlock_catalogue.md`: mechanical ideas, including the team lead's key-flap idea.

The main session re-read 15 of their claims at source, and all were confirmed (`R0_spot_checks_of_agent_work.md`,
round 5).

The trade-off model now also counts whether the pilot can respond **in time**, and it compares two mechanical options
(O9, O10). Numbers come from `python 02_EASA/scripts/easa_tradeoffs.py`, which writes `outputs/tradeoffs/tradeoffs.md`
and figures T1–T2 (datawiz 0 HATA, eye-checked).

**Scope.** Alert system only. We do not change how the latch locks.

**Tags.**
- [D]: read at source by the main session.
- [D-ag]: read by a research subagent.
- [K]: computed.
- [Y]: judgement.

---

## 1. Where to sense: "one truth at the bolt"

**Finding.** On canopy after canopy, the handle or the linkage said "locked" while the latch was not engaged. All of
these were re-read at source [D]:
- **Pitts S-2B G-IIDY:** the horn on the locking lever stayed silent, yet the canopy was not engaged on the fuselage
  (AAIB 3/2011 p. 36).
- **L-39 G-OALB:** the external handle "can be stowed … regardless of whether or not the canopy has been locked"
  (AAIB 4/2005).
- **Duo Discus:** "the handle in locked position but not connected with the fuselage pins" (EASA AD 2024-0059).
- **Europa:** only the forward shoot bolt engaged, not the rear one (CAA MPD 2022-003).
- **CAP 232:** the canopy can be locked in a slightly-open position (BEA F-HKAP).
- **RV-14:** the microswitch signalled "closed" before the pins seated; the accident was fatal (NTSB CEN23FA359).
- **B747 UAL811:** the NTSB asked for the actual position of each latch cam and lock to be shown, independently
  (A-89-93, AAR-92/02).

**Our own type.** On the Extra NG the handle reads 70 mm both when it is locked and when it is released (AAIB-28120
pp. 8–9 [D]). So anything driven by the handle or the linkage tube is satisfied by an open canopy.

| Latch architecture (R8-latches taxonomy [D-ag/Y]) | Examples | Look-alike state | Where to sense | Where a passive indicator can go without changing the latch |
|---|---|---|---|---|
| A1 shoot bolts on one rod | **Extra NG**, Europa door | one bolt on its wedge or outside its guide | **each receiver lug**, fuselage side | bolt band visible at each lug; tell-tale plunger |
| A2 one rod, several housings | CAP 232 | locked in the vent housing | the "closed" housing only | mark on the closed housing |
| A3 rotary hooks + over-centre cam | T67, L-39, Sling 4 | hooks on their toes, short of over-centre | each hook's keeper | red hooks (the T67 fix, AAIB 12/96) |
| A4 one handle per side | DA20, ASK 21, Grob 103 | one side locked, one not | each side separately | each lever with its own mark |
| A5 frame lever + rods into fuselage pins | Duo Discus, DG-1000 | lever forward, pins not engaged | each fuselage pin | red mark (FAA AD 2025-04-14 for the Duo) |
| A6 single turn handle + tang | RV-12 | tang not fully under its block | the block | witness line |
| A7 interlock between two canopies | ASK 21 | bypassed if the rear is opened later | both canopies | — |

**Rule for any aircraft.**
- Fit one engagement sensor at each receiver and one seated sensor (doc 26 §3.1; kit `08`: a single sensor misses one
  point out (N−1)/N of the time [K]).
- Never sense at the handle.
- Set every switch point with a gauge at full and at partial engagement, and keep the record.
- Re-check it after any canopy work. Rigging drifts: the DG-1000 rear locking rod unscrews (85 FR 47638 [D-ag]).

**In-flight wording.** Four reports show that trying to re-latch in flight made the canopy open fully: CAP 232, T67A
G-BIZN, and two SportCruisers (R8-latches [D-ag]). So the in-flight message is "fly, do not re-latch", and the alert
must come **before** take-off.

---

## 2. How fast: the take-off time budget

All arithmetic is in R8-timing, using a constant-acceleration model and lift-off at 65 kt. No Extra performance figures
were obtainable, so 112 m and 200 m rolls bracket the range [Y].

| From throttle forward | Short roll | Long roll |
|---|---|---|
| 30 kt (gate limit) | 3.1 s | 5.5 s |
| 40 kt (reject window end used in the model) | 4.1 s | 7.4 s |
| Lift-off (65 kt) | 6.7 s | 12.0 s |

**Response time.**
- Certification assumes at least 1 s to recognise a failure, even for test pilots who expect it (AC 25-7D §4.3.6.4 [D]).
- Surprise roughly doubles response time: 2.02 s expected vs 4.12 s surprised (Landman 2017 Table 3 [D]).
- Design values: median 1.5 s, 95th percentile 3.0 s [Y, R8 synthesis].

**What the model says [K].**
- With a throttle-lever trigger (onset 0.35 s), a pilot who notices and believes the alert acts before 40 kt in 99.3 %
  of cases.
- With an rpm trigger plus 0.5 s persistence (onset 1.65 s), this falls to about 94 %.
- That small drop costs a lot when the pilot acts on every alert: the shaker option falls from **79× to 15×** (O5 vs O5r).
- The organisers' G3X example triggers on "engine power increased" (G3X IM p. 30-214 [D]), i.e. late.
- A barrier acts on the lever itself and is not limited by response time.

**Requirements adopted from R8-timing** (T-numbers as there; the last column says how we use each).

| # | Requirement | Number | Status in our design |
|---|---|---|---|
| T2 | Take-off trigger from a throttle-lever switch | onset ≤ 0.35 s, never > 0.5 s | **adopted**. Rpm/power is kept as a second, independent arming input in case the switch fails (R7-interlock asked for "actual power") |
| T3 | Latch persistence filter runs continuously in taxi, not restarted by the trigger | 0.5 s | **adopted** (already so in `logic.py`) |
| T1 | Red + voice at run-up / line-up power while stationary | ground speed < 5 kt | **adopted**. This gives the most time of all |
| T4 | Lamp, voice and vibration start together | within 50 ms | adopted |
| T5 | First "CANOPY, CANOPY" ends early on the roll | ≤ 2.0 s after lever advance | adopted (voice pair ≈ 1.2 s) |
| T8 | Any automatic ground action acts on lever advance | ≤ 0.5 s (below ~5 kt) | **adopted for the gate** |
| T9 | Vibration only below the gate speed | stops at 30 kt | **adopted**. This changes doc 26: no shaker on the fast roll or in the air, to avoid abrupt high-speed aborts and in-flight throttle reactions |
| T13 | Canopy item **last** in the line-up check, right before the throttle | last | adopted **in addition to** first place in the before-start check: Degani & Wiener recommend duplicating "killer items" (R6 [D-ag]) |
| T14 | Re-check the new-alert voice deferral against opening heights | test LOF + 5 s vs + 10 s | **open**. 42 % of climb openings with a stated height were at or below 100 ft, roughly lift-off + 4–8 s (our catalogue, 26 rows, agent's parse) [K] |
| T12 | Bolt windows readable in one glance, and only when stopped | ≤ 1 s each, ≤ 5 s total | adopted for the optional bolt marks |

---

## 3. Mechanical ideas: catalogue and verdicts

The team lead's seed idea is a flap at the key or ignition that will not open until the canopy is locked, but will not
close while the key is in. It has real precedents:
- The Cessna 172R control lock carries a flag that covers the ignition switch (POH p. 7-18; agent-read [D-ag]).
- The A320 fan-cowl latch key "cannot be removed unless the FCD front latch is safely closed" and must be stowed in the
  flight deck (FAA NPRM 83 FR 19648 [D]).

R8-mechanical ranked the ideas (scores [Y]). The two that can be modelled now have model numbers.

| Idea | Senses | Precedent | Model [K] RF acts / distrust; fatal per 10⁶ | Verdict |
|---|---|---|---|---|
| **Bolt plunger at each lug driving a visible flag and the electric sensor** ("one truth at the bolt") | bolt | 747 relief doors driven from the handle linkage gave a false "locked" (AAR-92/02) [D]; the lesson is to drive the flag from the bolt | as O6m: 1 805× / 15.7×; 2.24 | **adopt** with the recommended design: the pilot can check the same part the sensor reads |
| Tell-tales or paint at each lug | bolt | A320 fan cowls: paint, flags and tell-tales cut losses only ~50 %, from 1 per 1.28 M to 1 per 2.42 M flight cycles, "only partially effective" (AAIB AAR 1/2015) [D] | O1 alone: 1.5× / 1.5×; 24.1 | **cheap tier only**; a cross-check, never the whole answer |
| Flag in view driven by the linkage tube | tube | — | not modelled | **reject on the Extra NG**: the tube reads the same open-released and locked (AAIB pp. 8–9) |
| **Mechanical throttle pawl** driven by cables from the bolt plungers, distinct release | bolt via cable | G-IV throttle stop (pilot pushed past it; NTSB AAR-15/03) [D-ag] | **O9: 602× / 11.2×; 3.16** | **no-electrics alternative** to the electric gate. A cable has 3–6 mm of slack in a 10 mm signal, and there is no ground/air logic |
| **Starter guard flap** released only when all bolts are home (seed idea, start-only form) | bolt via cable | Cessna 172R flag over the ignition [D-ag] | **O10: 153× / 5.0×; 7.00** | **weak**: catches only "unlocked at start". The last closure is what matters: in SEA01LA058 the canopy was opened and closed several times and the last closure was not latched (R6 [D-ag]) |
| Key or flap that stops the canopy being **unlocked** (seed idea, second reading) | — | — | — | **reject**: blocks egress and jettison (CS 23.807(b)(5)) and is a latch change |
| Mixture or fuel-valve interlock, harness interlock | — | — | — | **reject**: they can starve the engine or trap the pilot |

**Reading.**
- Of the mechanical ideas, the pawl comes closest to the electric gate (11.2× vs 16.3× under distrust).
- The seed idea in its start-only form is a third as strong as the gate under distrust (5.0× vs 16.3×), for one reason:
  it guards the wrong moment.
- Moving the same idea to the **throttle** turns the key-flap idea into the gate. That is our recommendation, and it
  keeps the team lead's principle: "the next step is physically blocked until the bolts are home".

---

## 4. Cheap to expensive: the cost tiers

**Where the numbers come from.**
- Costs: R8-systems Table 2. Parts are catalogue prices seen 5 Nov 2026; labour is estimated by R8 [Y] and anchored on
  FAA AD work-hour paragraphs; labour priced at USD 85/h. Certification is excluded, as the task says.
- Model columns [K]: from `tradeoffs.md`.

| Tier | What is fitted | Approx. cost per aircraft | Mass | Model option | RF acts / distrust [K] | Fatal per 10⁶ flights [K] | Evidence the tier can claim |
|---|---|---|---|---|---|---|---|
| **0** Procedures | placard, checklist item first and last, "closed–locked–checked" call-out | ≈ USD 180 | ≈ 0 | O0 | 1× / 1× | 35.1 | weakest: omission HEP 0.001–0.01 per item (NUREG [D]); the Duo Discus fix existed 19 years and a fatal accident still happened in 2023 (R8-systems) |
| **1** Passive marks | band on each bolt, view port or mirror, placard | USD 275–420 | < 50 g | O1 | 1.5× / 1.5× | 24.1 | regulators accept them, but A320 shows only ~50 % effect [D] |
| **2** Single switch + lamp or EFIS (organisers' example) | one switch at one pin, red lamp or G3X discrete | USD 700–1 050 | 0.1–0.2 kg | O2 | 4.6× / 2.0× | 17.5 | mixed: every DA40/42 had a door warning and still lost more than 30 doors (EASA AD 2011-10-13 [D]); a car "mild" reminder gives 93 % vs 82 % belt use (R8-systems) |
| **3** Per-point sensing + lamp + voice | one inductive sensor per bolt + seated, 3-state lamp, voice | USD 2 300–3 600 + EUR 398 (commercial sensors); USD 4 700–6 000 with MIL switches | 0.5–0.8 kg | O4 | 23.5× / 2.7× | 13.0 | strongest documented alert: NTSB A-89-93 per-latch indication [D]; belt reminders 97.5 % vs 85.8 % (Lie 2008 [D]) |
| **4** + vibration + ground gate (**recommended**) | throttle-knob shaker below 30 kt; solenoid gate with guarded release and log; bolt-plunger flags | USD 6 000–9 000 (gate and shaker prices not found: order of magnitude) | + 0.3–0.6 kg | **O6** (O6m with flags) | **1 236× / 16.3×** (1 805× / 15.7×) | **2.15** (2.24) | the FAA treats a throttle stop as an "unmistakable warning" [D-ag]; haptic warnings are left switched on more than audible ones (IIHS 2024 [D-ag]) |
| 4-M No-electrics variant | Tier 3 + mechanical throttle pawl by cable | similar labour, fewer electrics [Y] | + 0.3–0.5 kg [Y] | O9 | 602× / 11.2× | 3.16 | no power needed; cable slack is the weak point |
| **5** Integrated EFIS + recorder | Tier 4 + line-monitored sensors into the EFIS, crew-alert message, lock-state recording | USD 8 000–12 000+ | + 0.3–0.5 kg | O6 + EFIS message (adds little at take-off: lamp → EFIS message changes 23.5× to 21×, O4e) | ≈ O6 | ≈ 2.2 | the recorder answers "was it locked?", which neither PKBWL nor AAIB/BFU could settle (R0 [D]); this is EASA's own disputed question |

**Where the money buys the most.**
- Tiers 0–3 multiply the cost about 20 times. Under distrust the gain only grows from 1× to 2.7×.
- **Tier 3 → 4** costs 2–3 times more and raises the distrust gain **six-fold** (2.7× → 16.3×). Fatal outcomes fall
  from 13.0 to 2.15 per 10⁶ flights [K].
- Tier 5 adds little at take-off. It pays off in the investigation after an event, which is what the EASA case study was
  about.

## 5. Three packaged designs for the report

| Package | Tiers | For whom | Content |
|---|---|---|---|
| **Basic** | 1 + 3 without voice, or 1 + 2 upgraded to one sensor per point | owners of light singles, gliders, home-builts; aircraft without intercom or throttle (gliders) | bolt bands + one sensor per receiver + 3-state lamp; checklist item first and last |
| **Recommended (Extra NG)** | 4 | aerobatic and powered canopy aircraft | LOCK-SENSE, lamp "CANOPY UNLOCKED"/"LOCKED", voice "CANOPY, CANOPY", knob shaker below 30 kt, ground gate on lever advance with guarded release and log, bolt-plunger flags, red stage at line-up |
| **Full** | 5 | glass-cockpit fleets, training organisations | Recommended + EFIS crew-alert message + lock-state recording on the EFIS card |

## 6. Limits

- **Costs:** labour hours are R8 estimates. No catalogue prices were found for the gate solenoid or the vibration motor,
  so Tiers 4–5 are order of magnitude only.
- **Timing:** no Extra NG take-off performance was obtainable. The 112–200 m rolls bracket the range [Y].
- **Mechanical options:** O9 and O10 use judgement values for failure to engage and for reopening after start.
- **Passive marks:** no measured effect exists for general aviation. A320 fan cowls are the only quantified analogue.
- Everything in doc 26 §5 still applies: detection probabilities are judgement, probability matching is a worst-case
  behaviour model, and the fatal numbers are relative only.
