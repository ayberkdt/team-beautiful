# 23 · EASA challenge — Canopy alert system retrofit (Extra NG)

> **5 Nov ~16:30: official task received** — `02_EASA/official_2026-11-05/00_OFFICIAL_TASK_vs_KIT.md`. Certification is to be
> disregarded (the approval items below are context only), feedback elements include vibration and engine shut-down
> (answered in `kit/12_feedback_matrix.md`), and the talk is `kit/02_talk_4min.md`.

## Friday morning checklist (10 lines)

1. Shell: set the D: temp variables of `docs/21` and `PYTHONPATH=src`. Check the time with `Get-Date`.
2. `python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json` → exit 0 in **≈ 21 s**, last lines "0 errors" (dry run §9).
3. `python -m pytest -q tests/test_canopy.py tests/test_canopy_day.py` → **24 passed** in ≈ 12 s.
4. Open `02_EASA/outputs/C1…C6_*.png`: slides 2, 3, 5 and 6.
5. Open `outputs/day/fault_demo.html` (slide 7) and `annunciator_mockup.html` (slide 4).
6. Have `02_EASA/docs/glossary.md` open for the "word list".
7. First sentence: **"Closed is not locked."** G-MIIL was a bonding/fatigue failure per AAIB, the BFU disagrees, and the
   regulators say most openings are partial locks.
8. Ask mentor questions 1 and 6 (§6) first: they decide whether the structural cause and the word list matter.
9. "Why not more sensors / an interlock?" → §3.3 table. Hard questions → §6b (10 jury questions with sourced answers).
10. Never claim the alert would have prevented G-MIIL. Our rates are labelled assumptions, and the cry-wolf numbers are
    abstract-level.

---

Task (handwritten notes, `00_Common/organiser_notes/03_EASA_Canopy_Alert_Retrofit.md`, not official text): propose a
retrofit canopy alert system for an aircraft of our choice and outline step by step how to retrofit it to reduce
**unlocked-canopy events**; motivated by the 2 April 2022 accident to Extra NG G-MIIL; "no budget limit, be creative".

Tags: **[D]** read by the main session from the primary source · **[D-ag]** read by a subagent (note named) ·
**[K]** computed here (command given) · **[Y]** our judgement/assumption.

**Summary.**
- **Example aircraft: Extra NG.** Two regulators (EASA AD 2025-0156, FAA AD 2026-04-12) attribute its in-flight canopy openings
  to partial or improper locks [D]. No public source shows a canopy warning on it (POH not read), and its three-bolt latch is
  published in measurable detail. Back-up type: Diamond DA40.
- **Design LOCK-SENSE:** one fuselage-side inductive sensor per shoot-bolt lug plus a seated sensor, self-checking outputs,
  and green only when locking is proven.
  - Taxi: amber. Take-off power and in flight: red plus voice.
  - Sensor fault: amber on the ground, red at take-off power (unconfirmed = not locked).
  - About 0.5–0.6 kg, < 2 W. Approved as a minor change.
- **Numbers [K]:**
  - A frame "closed" switch misses every partial lock.
  - LOCK-SENSE cuts take-off-with-unlocked-canopy risk about 1 900× if pilots act on every alert, but only about 3× if they
    trust it as much as its nuisance-alarm rate deserves.
  - The fault demo shows only two double faults can give a false green.
- **Evidence:**
  - 241 investigated openings (126 lock-related, 60 % of those in the initial climb), each row with its report URL.
  - An independent audit found 1.5 % field errors; all were fixed.

Files:
- One command reproduces every number and figure: `python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json` →
  `02_EASA/outputs/`. It writes `report.md`, `result.json`, figures C1–C6 (PNG + PDF + datawiz audit, 0 HATA each,
  set consistent) and `fault_demo.html`.
- Code: `src/aerokit/canopy/` (mechanism, sensors, logic, faults, fta, montecarlo, barriers, fmea). Tests:
  `tests/test_canopy.py` + `tests/test_canopy_day.py` (24 tests, 125 numerical checks).
- Plan: `02_EASA/docs/retrofit_plan.md`. Word list: `glossary.md`. Cockpit mock-up: `annunciator_mockup.html`
  (ux gate: `annunciator_mockup.denetim.md`). Fault demo ux audit: `fault_demo.denetim.md`.
- Evidence catalogue: `02_EASA/research/00_INDEX.md`.

---

**Day kit (5 Nov):** `02_EASA/kit/00_KIT_INDEX.md` — mentor decision tree, 4:00 talk, report draft (R1–R6), traceability, AFMS, ICA, BOM, any-aircraft study, concept trade, figures K1–K4.

---

## 1. The critical distinction — say this in the first minute

| | G-MIIL, 2 Apr 2022 (the motivating accident) | The hazard the challenge asks about |
|---|---|---|
| What happened | Canopy **broke up** in level flight at 184 KIAS; pilot lost sight in one eye, bailed out; aircraft destroyed (AAIB pp. 1–2) [D] | Canopy **not fully locked** → opens or departs in flight |
| Official cause | AAIB: inadequate **bonding** between inner and outer frame → stress in the PMMA → **fatigue cracks** → failure (AAIB pp. 25–27) [D] | EASA AD 2025-0156: in-flight openings/detachments caused "in most cases" by a **partially or improperly locked canopy**; FAA AD 2026-04-12: "because of a partially or improperly locked canopy" [D] |
| Disagreement | **BFU (State of Design) does not accept** the fatigue scenario; says it is "most probable" the canopy **was not completely locked** (AAIB App. A, p. 28) [D] | Same type, SP-HMM: two in-flight openings; 2023: pawls "engaged only partially", not precluded by the design (PKBWL 2023-0061 p. 6) [D] |
| Would a lock alert have helped? | Not against bond/fatigue failure. But a **recorded lock state** would have settled the AAIB/BFU dispute [Y] | Yes, this is exactly what it detects |

So: **we do not claim the alert would have prevented G-MIIL.** We say G-MIIL is the case where the two possible
explanations could not be told apart, because nobody could prove whether the canopy had been locked. In both G-MIIL and
SP-HMM 2022 the spring pulled the bolts back into an "apparently locked position" after the event (AAIB p. 26; PKBWL 2022/1097
p. 7) [D]. Our system makes the lock state visible before take-off and records it. Ground NDT of the frame bond (option O5)
addresses the structural cause separately; EASA itself is evaluating such an NDT (SR 2024-004 response) [D].

---

## 2. Findings

### 2.1 Accident and type [D] (AAIB-28120, all 28 pages read; `R0_AAIB_G-MIIL_report.md`)

- Extra NG, s/n NG028, built 2021, ~40 FH; CS-23 Level 1 low-speed, certified Oct 2019, ±10 g; Garmin G1000 with data card;
  flown from the rear seat (pp. 3, 7).
- Canopy: single PMMA tear-drop, 2.9 mm (front) to 3.5 mm (rear), bonded in a carbon prepreg frame (EP121-C20-45, Loctite EA
  9395); hinged right (3 pins), lanyard-restrained; **3 steel shoot bolts** on one linkage tube + tension spring, engaging
  roller lugs on the left rim; ramp 15 mm × 5 mm rise, 3:1 (p. 8).
- Handle gap **70 mm** locked (and open-released), **60 mm** partially locked; pulling from partial to full needs **60 N**;
  opening from full 136 N, from partial 90 N (pp. 9, 20). **No observable visual difference** at the frame edge (p. 20).
- SB-NG-2-22 step 19 states the same thing in the manufacturer's words. Partial lock: "lead wedge section only engaged with
  the lug roller". Full lock: "the lug roller ... on the top flat", with an audible and tactile confirmation (SB p. 4) [D].
- Timeline: take-off 1037; aerobatics 5 300–7 300 ft; separation 1057:59 at 1 600 ft agl, 184 KIAS; last data 1058:34 at
  ~250 ft agl, ~7 000 ft/min (p. 5). Load factors printed inconsistently: max 3.8 g / min −1.2 g (p. 6) vs 3.6 g / −1.5 g
  (p. 25), both as printed.
- VNE 221 KIAS exceeded on four earlier flights (227–253 KIAS) in July 2021 (p. 6).
- Safety action: POH rev. Extra NG 1.11 (23 Dec 2022) adds "Pull the aft locking handle fully rearward to the end stop" (p. 27).
- SB-NG-2-22 (Issue A, 23.12.2022, non-mandatory; all 7 pp. read): bonding foam injected at the front frame; AAIB doubts its
  effect (pp. 12, 27).
  - The SB covers NG001–NG038 **except NG026**, which conflicts with AAIB p. 12 (that says it includes SP-HMM).
  - It warns that the foam can **block the locking mechanism** (SB p. 2).
- **SR 2024-004** (EASA: ensure canopies meet certification standards and loads), **SR 2024-005** (EASA: assess SB-NG-2-22)
  (pp. 26–27).

### 2.2 What happened next (regulatory chain) [D unless marked]

- **EASA AD 2025-0156** (issued 21 Jul 2025, effective 4 Aug 2025, all s/n): new handle **placards** per SB-NG-1-24 within
  3 months / 25 FH + AFM limitations update (rev. 16); pilot-owner may do it; NG065+ fitted from production. **No sensor or
  warning required** (AD pp. 1–3).
- **FAA AD 2026-04-12** (Amdt 39-23272; Fed. Reg. 91:51, 17 Mar 2026; effective 21 Apr 2026) mirrors it for all EXTRA NG.
  It affects 30 US aircraft; the placards cost $85 labour + $10 parts = $95 per aircraft and the POH revision $85. No NPRM
  comments were received.
- **PKBWL 2023-0061:** ECO-NG-22-09/23-07 (new pawl contour + extra spring), standard from **NG061**, free factory retrofit
  per AI-NG-02-23. The passenger may have knocked the handle in flight (pp. 6–8).
- **PKBWL 2022/1097** (first SP-HMM event, all 10 pp.):
  - Cause: frame vibration from loss of stiffness unlocked the pawls. Contributing: probable frame crack, loosened rear
    fitting, speed near VNE. No SRs.
  - A vibration precursor was reported one flight earlier, and the aircraft had no recorder.
- **AAIB SR responses** (document updated 29 Jan 2025; `R0_AAIB_SR_responses_2024-2025.md`):
  - SR 2024-004 is open, "Partially Adequate". EASA cites an unchanged bonding process from the EA 300 and a CFD analysis. It
    is evaluating a voluntary one-time **NDT** and **considering the BFU locking-mechanism scenario**. No status found after
    the 1 May 2025 update date.
  - SR 2024-005 is closed, "Partial Agreement". Extra offers a one-off frame inspection (AMM 20-10-06) and "an improvement on
    the latching system".
- No public evidence of any electrical canopy-unlocked warning on the Extra NG (R1 [D-ag]). EASA rejected a stronger-lock rule
  for sailplanes because it could compromise emergency opening (BELG-2024-001, R1 [D-ag]); an alert leaves locking effort and
  jettison untouched [Y].

### 2.3 How common are unlocked-canopy events? (241 rows, each with its own report URL)

Sources: `R2_occurrences.csv` (146 rows) + `R5_occurrences_add.csv` (95 rows). Tags: rows [D-ag]; counts [K] (`report.md` §7,
figures C5–C6); 4 rows re-read by us + 15 audited (§2.7). **A sample of investigated events, not a rate.**

- **By investigator:** NTSB 150, AAIB 41, BEA 21, BFU 14, PKBWL 9, SUST 4, others 2.
- **126 are lock-related** (76 not locked, 50 partially latched); **16 of them fatal**.
- **By phase:** 76 of the 126 opened in the initial climb and 17 on the take-off roll (74 % together; figure C5). This is why
  the alert is armed at take-off power.
- **By type:** no family has more than 10 lock-related rows, and 52 sit in families with fewer than 3 (figure C6). The
  method must transfer across types.
- **Fitted warnings fail too:** 14 rows had a warning. Both new ones gave a false "closed": BD-10 N2BD (light out with the
  pins unengaged) and PS-28 F-HSAB (switch senses the lever, not the latches). This matches R2's N6161 and G-IIDY: the
  "closed ≠ locked" argument in the field.
- **DA40:** one "door open" light serves canopy and rear door. Pilots taxi with the canopy partly open, so the light is
  normally on and "the pilot ignores the annunciation" (FAA AD 2010-25-01 comment, Fed. Reg. 75:75868–69) [D]. Our rules
  follow: one indication per opening, and an open canopy during taxi is only an advisory.
- **BFU 21-0469** (Grob G103, 2021, fatal) [D]:
  - A witness video shows the front-canopy lever unlocked through the winch launch.
  - The canopy opened at ~30 m on final, and control was lost while the pilot tried to close it.
  - The AFMS therefore says: do not try to close the canopy in flight.
- **Europa (UK):** 8 door openings since 2003; the lever can close with only the front shoot bolt engaged (AAIB G-FLOR) [D].
- **WT9 Dynamic:** at least 12 earlier canopy openings; the maker recommended a new lock and an incomplete-closure warning
  (BEA2024-0375) [D-ag].
- **Pitts:** heavy under-reporting (1 CAA record in 10 years vs many pilot reports, AAIB G-IIDY) [D-ag].
- Unverified (snippets only): BGA "213 canopy openings", TSB "33 door-open accidents". ATSB and TSB Canada were not reachable.

### 2.4 Certification basis and route (R3 [D-ag]; key paragraphs re-read [D])

- Extra NG basis **CS-23 Amdt 4**; ELA1 (950 kg).
- **The alert is voluntary.** CS 23.783(e)(3)'s "not fully closed and locked" warning binds only doors forward of any engine or
  propeller (EAR CS-23 Amdt 4 pp. 170–171) [D]. We adopt its criterion anyway: an erroneous "closed and locked" indication must
  be improbable (R-4).
- Other relevant paragraphs:
  - 23.1309, and 23.1322 (red/amber/green).
  - 23.807(b)(5): an aerobatic aeroplane must let each occupant abandon it at any speed VSO–VD (p. 175) [D].
  - Amdt 6 equivalents: 23.2250(e), 23.2315(b), 23.2510, 23.2605(b)(c).
- **Route: minor change** (21.A.91), approved by EASA (21.A.95(a)1) or a DOA (21.A.263(c)(1)(2)). Consult EASA on the
  classification early (GM 21.A.91 §3.3).
  - CS-SC110a covers only the annunciator: "for awareness only", and not pilot-owner releasable (CS-STAN Issue 4
    pp. 128–131) [D]. The latch sensors are not a standard change.
- **Inoperative:** non-required equipment → deferral under ML.A.403, INOP placard, CB pulled (panel dark). An MEL is optional
  under NCO.GEN.155.

### 2.5 Human factors

- **Abstracts only (R4 [D-ag]):**
  - Below ~70 % reliability, diagnostic automation is worse than none (Wickens & Dixon 2007).
  - False alarms harm compliance and reliance; misses harm only reliance (Dixon, Wickens & McCarley 2007).
  - ~90 % of participants probability-match their response rate to alarm reliability (Bliss, Gilson & Deaton 1995; abstract
    re-read by us).
  - Alerts the operator can verify showed no cry-wolf effect (Wickens 2009). The handle legend makes ours verifiable.
- **Full texts (R6 [D-ag] unless marked):**
  - **Checklist-step omission** (NUREG/CR-1278 Table 20-7, re-read by us [D]): 0.001 per item (short list, check-off used),
    0.003–0.01 without check-off, 0.05 when the procedure is not used. This is the source of our partial-lock base rate (1e-3
    central, swept to 5e-2).
  - Airline line observations: 42 omitted or incorrect checklist items in 60 flights; 14 % of checklist deviations caught
    (Dismukes & Berman 2010).
  - Real flight (DR400): 38 % of aural tones missed (Callan 2018). High-workload simulator landing: 57.7 % missed (Dehais 2019).
    So voice is never the only cue.
  - ATC conflict alerts: 81–87 % nuisance (FAA TC-07/22).
  - NTSB ERA10LA221: an unlatched canopy rests closed on the ground and lifts after take-off.
- **Still not read in full:**
  - Bliss 1995, Wickens & Dixon 2007 and Dixon et al. 2007 are paywalled.
  - Wickens 2009: Sage served a bot check, which we did not bypass.
  - Dehais 2014: legally open on OATAO, but the server did not respond.

### 2.6 Sensor data

- Inductive NAMUR sensor: 15.4 FIT safe / 9.63 FIT dangerous; with a line-monitoring interface 0.09 FIT dangerous (exida
  report, Tables 2–3) [D]. These are the model's base rates (× 18 environment factor [Y]).
- MIL-HDBK-217F N2 §14.1 λb: snap-action 0.49, limit 4.3, reed 0.0010 per 10⁶ h; πE AIF 18 (R4 [D-ag]). These are the
  sensitivity rate sets.
- Aerospace example, Honeywell GAPS: < 60 g, 12–32 Vdc, < 10 mA, **≤ 3.5 mm sensing distance**, −55…115 °C, MTBF 500 000 FH
  (vendor), optional health-monitoring third output (`R0_Honeywell_GAPS_proximity_sensor.md`) [D].

### 2.7 Evidence quality (`R0_spot_checks_of_agent_work.md`, `R_audit_2026-11-04.md`)

- 12 agent claims re-read by the main session: 12 confirmed.
- **Independent audit.** A fresh subagent re-opened the sources of 15 random rows and 10 random statements (seed 20261104).

| Part | Clear mismatches | Including minor | Wilson 95 % (incl. minor) |
|---|---|---|---|
| Rows | 1 / 15 | 2 / 15 | 3.7–38 % |
| Fields | 1 / 135 | 2 / 135 = 1.5 % | 0.4–5.2 % |
| Statements | 0 / 10 | 2 / 10 | 5.7–51 % |

- **All mismatches were re-checked and fixed.** NTSB-001 → not_locked; NTSB-037 → mechanism_failure; two wording fixes.
- The audit also exposed a merge-key bug (two BFU events with unpublished registrations had been merged). It is fixed and
  tested.
- Both row errors under-coded a lock cause, so the lock-related counts are, if anything, low.

---

## 3. Design — "LOCK-SENSE" (architecture A3)

```
 canopy frame (moving, passive)          fuselage left rim (fixed, all wiring here)
 ┌────────────────────────────┐          ┌────────────────────────────────────────┐
 │ steel target ───────────── │ ·······→ │ S0 seated sensor (inductive)           │
 │ bolt 1 (front) ──────────→ │ ·······→ │ S1 at lug 1: bolt tip at full depth?   │──┐
 │ bolt 2 (centre) ─────────→ │ ·······→ │ S2 at lug 2                            │──┤ line-monitored
 │ bolt 3 (rear) ───────────→ │ ·······→ │ S3 at lug 3   (≤ 3.5 mm sensing gap)   │──┤ loops
 └────────────────────────────┘          └────────────────────────────────────────┘  │
                                         ┌──────────── alert unit ─────────────┐     │
  throttle switch / IAS (EFIS) ────────→ │ fusion: LOCKED = S0 ∧ S1 ∧ S2 ∧ S3   │ ←───┘
  master acknowledge ─────────────────→ │ phase logic, persistence, inhibits   │──→ green CANOPY LOCKED (hardware AND)
  14 V bus, own CB ───────────────────→ │ self-test, event log                 │──→ amber CAUTION / red WARNING (flash)
                                         └──────────────────────────────────────┘──→ voice "CANOPY" → audio panel
                                                                                  └──→ (O2) discrete → G1000 CAS + data card
```

- **Closed ≠ locked.** LOCKED needs seated **and** all three bolts. The bolt sensors see bolt depth directly. A handle switch
  can't, because the handle reads 70 mm both locked and open-released (AAIB p. 9) [D].
- **Nothing crosses the split line.** Emergency opening and jettison are unchanged (CS 23.807(b)(5)) [D].
- **Never a false green:**
  - Invalid codes or impossible combinations ("bolt sensed while not seated") give CANOPY SENS. It is **amber** on the ground
    and **red at take-off power**: unconfirmed is not locked.
  - Loss of power leaves the green lamp dark, and the checklist says "green ON" (AC 23.1309-1E §11.b [D]).
- **Phase logic** (`aerokit.canopy.logic`, tested):
  - Parked: an open canopy gives no alert. Taxi: amber with one chime.
  - Take-off power: red, flashing, voice. In flight: red after 0.5 s persistence.
  - A new alert's voice is deferred from 40 kt to 10 s after lift-off; the light still shows.
  - Acknowledge silences the voice; a new condition re-arms it.
- **Self-checks:** power-up lamp/voice test, and an open-canopy plausibility check that reveals a stuck bolt sensor on every
  powered opening.
- **Fault-injection demo** (`aerokit.canopy.faults`, `outputs/day/fault_demo.html`, `report.md` §6b) [K]:
  - 13 cases run through the real logic. Every single fault is caught or annunciated: wire break, short, stuck sensors, late
    rigging, and power loss (dark).
  - A false green appears only for two double conditions: a hazard plus a latent stuck sensor on the same bolt, and a partial
    lock plus all three sensors mis-rigged with one wrong gauge.
  - The demo found the amber-at-take-off gap that is now fixed.
- **Mass / power:** ≈ 0.5–0.6 kg; < 2 W (4 sensors < 60 g and < 10 mA each [D]; unit, lamps and harness [Y]).

### 3.1 What the analysis says (all [K], inputs tagged in `inputs.json`; 200 000 simulated flights per cell)

| Architecture | P(miss \| partial lock) | P(miss \| one bolt out) | Risk reduction, pilot always acts | …pilot probability-matches |
|---|---|---|---|---|
| A0 no system | 1 | 1 | 1× | 1× |
| A1 seated switch only | **1.0** | **1.0** | 1.0× | 1.0× |
| A2 seated + rear bolt | 7.3e-4 | **0.67** | 9.9× | 2.3× |
| **A3 seated + 3 bolts (chosen)** | 5.1e-4 | 6.4e-4 | **1 900×** (95 % lower bound 1 570×) | 3.0× |
| A4 dual everything | 4.4e-4 | 5.5e-4 | 2 190× | 3.0× |

The stress terms behind these numbers are [Y]: systematic mis-rigging at 1e-3 per flight and nuisance alerts at 3e-4 per
flight. The partial-lock base rate is 1e-3 per flight (NUREG/CR-1278 [D]).

1. A "closed" switch is worthless against this hazard (C1).
2. One sensor per bolt is needed; doubling channels buys almost nothing (A3 vs A4).
3. The residual is set by **systematic rigging error** and **pilot compliance**, not by random sensor failure. In the fault
   tree, the importance of the alert-ignored and mis-rig terms is ≈ 1 and of the sensor terms ≈ 1e-15. Hence the go/no-go
   rigging gauge in the ICA.
4. **Cry wolf decides the benefit (C3).** With probability matching the reduction falls to ~3× once nuisance alerts equal half
   the unalerted-hazard rate. Across the [Y] grid it spans 1.1× to 1 125×. Requirement R-3: nuisance ≤ 1/10 of the hazard
   rate, and the alert must be verifiable at the handle.

- **Trip window (C2).** With 0.3 mm rigging s.d. the trip point must be 67.5–68.7 mm handle-equivalent for both errors to stay
  < 1e-3. At 0.5 mm the window narrows to 67.9–68.2 mm.
- **ERCS (C4).** Take-off with a partial lock goes from **M1 RED** to **M3 YELLOW** with the warning barrier; in-flight unlock
  goes from M3 to M4 GREEN (barrier states [Y]).
- **Logic trace** of a G-MIIL-type morning: `report.md` §6.

### 3.2 Creative options (feasibility; detail in `retrofit_plan.md`)

| Option | Feasibility | What it adds |
|---|---|---|
| O1 analog bolt-depth sensing (= B in §3.3) | medium | Self-calibrating; catches rigging drift and trends bolt play/vibration (SP-HMM 2022: loose fitting and a vibration precursor one flight earlier, PKBWL 2022/1097) [D] |
| O2 G1000 CAS + recorded lock discrete | needs the TC holder | Would have settled the G-MIIL dispute |
| O3 haptic throttle cue | medium | Salient when the voice is masked |
| O4 take-off interlock | **rejected** | Could restrict power; would make the change major |
| O5 canopy-bond SHM / NDT | in-flight: low; ground NDT in ICA: high (EASA itself evaluating an NDT) | The only option against the actual G-MIIL cause |
| O6 RFID bolt tags | low | Per-bolt presence without wiring to the canopy |
| O7 camera + vision | low–medium | Independent visual channel with a picture log |
| O8 EFB app | high, awareness only | Checklist auto-tick, event log, fleet statistics |
| O9 helmet + visor guidance | high | AAIB pp. 23–24: a visor would probably have prevented the injury |

### 3.3 Costly-but-feasible options worked to the same depth as LOCK-SENSE

Risks are [K] (`report.md` §1, "Options at depth": same model and inputs). The option effect factors (`inputs.json` →
`options`) are [Y]. LOCK-SENSE mass and power come from the GAPS datasheet [D]; all other masses, powers and cost classes are
estimates [Y].

| | **LOCK-SENSE (A3, baseline)** | **B · LOCK-SENSE Plus** | **C · Powered over-centre lock** | **D · Two-stage canopy restraint** |
|---|---|---|---|---|
| What it is | 1 seated + 1 switching sensor per lug, self-checking, alert unit | A3 + a second, **analog** eddy-current channel per lug (+ second seated sensor). It learns the full-lock position each flight and must agree with the switch | Electric actuator on the linkage tube drives the bolts **over centre** to full lock once seated. It holds with no power. Manual handles override via a break-away link. A3 gives the position feedback | Keeps an **unlocked** canopy within a few cm of closed in flight. It releases fully only with the deliberate jettison motion (AAIB p. 11) [D] |
| Failure it removes | partial lock, one bolt out, unseated (if the pilot acts) | the two residual false-green cases (common mis-rig; latent stuck sensor on the hazardous bolt) | **the hazard itself**: omission of the final aft pull (NUREG 0.001 per step [D]); a knocked handle | **the consequences**: separation, wing/tail strike (PKBWL 2023-0061 p. 4 [D]), parts on the ground (AD reason [D]), wind blast |
| New failure modes | false alarms (cry wolf) | more nuisance (P(false) 2e-5 vs 0); self-calibration software | actuator stops short (seen by A3); jam; **must never drive towards unlock**; break-away must not block egress | could hinder **bail-out**, which CS 23.807(b)(5) requires at any speed VSO–VD (p. 175) [D]; frame/hinge loads at ~180 KIAS |
| Risk / flight, pilot always acts [K] | 3.1e-7 (1 900×) | 3.5e-8 (16 800×) | 8.4e-8 (7 100×) | probability unchanged; severity lower [Y] |
| Risk / flight, probability matching [K] | 2.0e-4 (3.0×) | 2.1e-4 (2.9×): nuisance-limited | 9.8e-5 (6.1×): fewer hazards to warn about | — |
| Mass / power | 0.5–0.6 kg; < 2 W [D + Y] | 0.9–1.1 kg; < 3 W [Y] | 1.2–1.8 kg; 20–50 W for ~2 s per lock cycle, 0 W holding [Y] | 0.2–0.4 kg; 0 W [Y] |
| Certification route | minor change (EASA or DOA); CS-SC110a for the lamp only | likely minor, plus software assurance (AC 23.1309-1E) → consult EASA early | **major change** (new latch function, egress, possibly catastrophic failure effect, GM 21.A.91 §3.4(g)) → TC holder (Extra DOA EASA.21J.593) or STC | **major change** (structure + egress) → TC holder or STC with flight test |
| Cost class [Y] | low | medium | high | medium–high |
| Verdict | **recommended first step** | upgrade only once nuisance is controlled; under probability matching it gains nothing | **most effective; only with the TC holder.** It continues Extra's own ECO path (pawl contour + spring, PKBWL 2023-0061 p. 7) [D] | study with the TC holder; must not obstruct jettison. G-MIIL's pilot survived by bailing out (AAIB p. 2) [D] |

The order the analysis gives: B only after the nuisance budget R-3 is met. C attacks the root, the human omission, so it beats B
under realistic pilot behaviour. D is complementary consequence mitigation, not an alternative.

---

## 4. Process — the 12 steps (full version: `02_EASA/docs/retrofit_plan.md`)

| # | Step | Key output | Who |
|---|---|---|---|
| 1 | Select the example aircraft: **Extra NG** (back-up DA40) | one-paragraph justification (ADs, PKBWL, AAIB, measurable latch) | design team |
| 2 | Baseline survey | POH §4/§7.7, AMM, SB-NG-1-24, ECOs; measured lug geometry and the ≤ 3.5 mm sensor gap; pre/post-NG061 split | design team + TC-holder data |
| 3 | Hazards H1–H7 | hazard list incl. false green and egress | design team |
| 4 | Requirements R-1…R-12 | testable spec: trip window, nuisance budget, colours, voice, ≤ 0.6 kg / ≤ 2 W | design team |
| 5 | Sensor selection | inductive at each lug + seated; rejects the frame switch | design team |
| 6 | Installation design | brackets, fuselage-side harness, CB, AC 43.13-1B practice, DO-160G sections | design team / DOA |
| 7 | Electronics + logic | alert unit as coded and tested, incl. the fault-demo cases | design team |
| 8 | Bench test | measured σ_trip on the real bolt material, fault injection, environment | lab |
| 9 | Ground / functional test | go/no-go gauge, all states, **jettison test**, engine-run nuisance check | Part-CAO/145 + DOA |
| 10 | Safety assessment | FHA, FMEA, FTA vs AC 23.1309-1E ceilings, ERCS | DOA |
| 11 | Approval | minor change by EASA or DOA; AFMS + ICA; CS-SC110a only for the lamp | EASA / DOA |
| 12 | Operation & maintenance | AFMS "green ON", "do not try to close the canopy in flight"; ICA rigging check each 100 h / annual and after any canopy work (SB-NG-2-22 can block the latch); INOP deferral; briefing; nuisance monitoring | operator, CAMO/CAO, pilot |

---

## 5. Risks and limits of this work

- **Assumed rates.** The hazard mix, pilot-check miss rates, mis-rig and nuisance rates, the option effect factors and the
  60–70 mm → bolt-depth mapping are [Y]. The partial-lock base rate is anchored on NUREG/CR-1278 [D]. The study sweeps the
  rates that matter (C2, C3, exposure grid). Fleet data from step 12 would replace them.
- **Abstract-level cry-wolf evidence.** Probability matching is our worst-case model; a verifiable alert probably does better.
- **Unread primary documents:**
  - SB-NG-1-24: no public copy, and Extra's tech-service page refuses automated requests, which we did not bypass.
  - ECO-NG-22-09/23-07, AI-NG-02-23, the POH/AMM, DO-160G and the ASTM standards.
  - The installation details therefore need the TC holder's data.
- **The dataset is a sample of investigated events, not a rate.** Expected residual field error in unaudited rows is about
  1–2 % (§2.7).
- **ERCS barrier states** are our judgement.

## 6. Questions for the mentor

1. Is G-MIIL only the motivation, or do you expect us to address its structural cause (bonding/fatigue) as well?
2. Should the design target the Extra NG specifically, or show a method that transfers to any type?
3. Should we treat the BFU's dissent as a live hypothesis, or stay with the AAIB conclusion?
4. Is a take-off interlock acceptable to you, or only alerting? We rejected the interlock; is that the expected answer?
5. Do you want certification depth (minor change vs STC), or design depth?
6. What is the "word list" in the notes: a glossary you will give us, a required vocabulary, or the alert wording?
7. Would EASA see a lock alert as a reason to relax pilot checks? We say no: the handle check stays primary.
8. PKBWL 2022/1097 argues an unlocked canopy would have fallen off during taxi. AAIB argues positive g re-seats a partially
   locked bolt. Which partial-lock behaviour should our hazard model assume?

## 6b. Jury questions (cold review by an independent subagent, ranked; answers sourced)

| # | Damaging question | Our answer (source) | Remaining gap |
|---|---|---|---|
| 1 | Which of your numbers come from flight data on this aircraft? | None of the rates do, and we say so. Partial-lock base rate: NUREG/CR-1278 omission 0.001–0.01 per step [D]. Every other rate is tagged [Y] and swept (§3.1 grid 1.1× to 1 125×). The 95 % bound covers sampling noise only. Known events on type: SP-HMM ×2 (PKBWL) [D] and G-MIIL (disputed); EASA gives no event count; FAA: 30 US aircraft [D] | **Open.** Fleet size and hours are not published, so the rates cannot be calibrated. Step 12 (event log) is how they would be |
| 2 | After 500 green flights pilots stop pulling to the end stop. Where is complacency? | Now modelled [K] (`report.md` §1, complacency sensitivity). With the system fitted, pilot-check misses rise to 0.9 (partial) and 0.99 (one bolt) [Y]. A3 still cuts risk **1 138×** with full compliance and **2.6×** under probability matching (vs 1 900× / 3.0×). So it stays net-positive. The FHA line "missed alert = no worse than today" is withdrawn: complacency makes a false green worse than minor | Partly closed. The plan's FHA now says this (step 10). Line checks and training stay the barrier |
| 3 | EASA mandated a $95 placard and Extra redesigned the pawls. What risk is left? | The placard and POH wording are awareness measures. PKBWL 2023-0061 found the design "technically did not preclude" partial engagement before the ECO [D]. The post-ECO pawl adds retention (contour + spring), but no public document says it **prevents** a partial lock [D, pp. 7–8] | **Open.** Post-ECO latch geometry unread, so the trip window must be re-derived per configuration (step 2 split, step 8 bench) |
| 4 | Every Extra NG event you cite happened in flight. Why build around take-off? | It covers both phases: red at take-off power **and** in flight after 0.5 s. SP-HMM 2023: pawls likely not fully engaged before flight (PKBWL cause 2) [D] → caught at taxi/take-off. SP-HMM 2022: a loose fitting and in-flight unlock [D] → in-flight warning + O1 play trend. Take-off arming comes from the catalogue: 74 % of lock-related openings were on the roll or in the climb, mostly other types [K] | Partly. The value of an in-flight warning (slow down, land) is argued, not measured |
| 5 | Could your red + voice cause a reject or low-level accident? | The light is never inhibited. Only a **new** alert's voice is deferred from 40 kt to 10 s after lift-off (AC 25.1322-1 inhibit logic, R4 [D-ag]). An alert present before the roll keeps its voice. AFMS: do not try to close the canopy (BFU 21-0469 fatal case) [D]; do not pull the handle in flight [Y] | **Open.** The reject rule and in-flight actions need the TC holder's canopy-open procedure (POH unread). The "minor" false-alarm class is asserted, to be confirmed by FHA |
| 6 | Who told you this is a minor change? | No one yet: R3 [D-ag] analysis of GM 21.A.91. We say "consult EASA early" (§3.3), and §3.4(g) makes it major if a failure effect is hazardous. With complacency credited (Q2) that is possible. The green lamp is a hardware AND, but the phase logic is software or AEH. Its assurance level must follow the FHA class (AC 23.1309-1E) [D-ag] | **Open.** Classification is a mentor/EASA question (§6 Q5). Fallback: the TC holder as applicant |
| 7 | Can a ≤ 3.5 mm inductive sensor hold a 1.2 mm window over ±10 g and −55…115 °C? | Not shown. The GAPS datasheet gives range, temperature and DO-160 categories [D] but no hysteresis or repeatability figure in the text we read. The 1.2 mm window assumes σ = 0.3 mm [Y]. Above 0.5 mm it closes (C2) [K] | **Open → bench test (step 8) is decisive.** If σ > 0.5 mm, use the analog channel (option B) or move sensing to the linkage tube, where travel is larger (10 mm handle travel, AAIB p. 9) [D] |
| 8 | How would you ever show nuisance ≤ 1/10 of the hazard rate? | Not before service. Design-induced nuisance is checked by ground run and flight test (step 9); the true rate needs the in-service event log (step 12). "Closed, not locked" in taxi is a **true** alert, not nuisance. The Extra NG canopy has a small sliding window the rear-seat pilot can open (AAIB p. 8) [D], so there is less reason to taxi unlocked than in the DA40 open-canopy taxi [D]; whether pilots do is unknown [Y] | Partly. A rule-of-three demonstration needs ~30 000 nuisance-free flights, which a small fleet cannot supply. It is a monitoring requirement, not a certification proof |
| 9 | No denominators and mostly unknown warning status: what does the catalogue prove? | Only patterns: phase distribution, type spread, "closed ≠ locked" failures of fitted switches. No rates; we say so (§2.3). Warning status is unknown in 221 of 241 rows [K]. The 14 rows with a warning are anecdotes, not a rate | Accepted as a limit |
| 10 | Would your recorder have survived G-MIIL? Why is the bond NDT an afterthought? | Yes for this case: G-MIIL's **G1000 memory card was recovered** and read, with every flight since July 2021 (AAIB pp. 3–4) [D]. A lock discrete logged there (O2) would have survived; SP-HMM had no recorder (PKBWL 2022/1097 p. 5) [D]. The bond NDT is the only answer to the AAIB cause, and EASA is evaluating one (SR 2024-004 response) [D]. We recommend it alongside LOCK-SENSE, not instead | Partly. O5 is not worked to the same depth as §3.3; in-flight SHM was not researched |

## 7. Slide plan (9 slides, about 7 minutes)

> **Superseded on 5 Nov:** the organisers' rules cut every talk at **4:00** (`Rules and Criteria.xlsx`, P4). Use the
> 6-slide, timed version in `02_EASA/kit/02_talk_4min.md`; the slides below remain as the backup pool for Q&A.

| # | Slide (claim as title) | Visual | ≈ s |
|---|---|---|---|
| 1 | **Closed is not locked.** AAIB: bonding; BFU: not locked; EASA AD: "in most cases ... partially or improperly locked" | §1 table | 50 |
| 2 | **The hazard is common, early and on every type.** 76 of 126 lock-related openings in the initial climb | C5 + C6 | 45 |
| 3 | **A "closed" switch sees nothing.** 3 bolts, 60 vs 70 mm, no visible difference | C1 | 45 |
| 4 | **LOCK-SENSE: green must be earned.** Fuselage-side sensors, phase logic, 0.5 kg | block diagram + `annunciator_mockup.html` | 60 |
| 5 | **Rigging precision is the design requirement.** Trip window 67.5–68.7 mm | C2 | 35 |
| 6 | **Cry wolf decides the benefit.** 1 900× vs 3×; nuisance budget; ERCS M1 → M3 | C3 + C4 | 55 |
| 7 | **What if a sensor fails?** 13 injected faults; only 2 double faults give a false green; the demo fixed a gap | `fault_demo.html` | 40 |
| 8 | **12-step retrofit:** minor change, AFMS, ICA, INOP deferral | §4 table | 50 |
| 9 | **Beyond budget:** powered over-centre lock (6.1×), LOCK-SENSE Plus, restraint, G1000 record, bond NDT | §3.3 table | 40 |

## 8. Who read what

- **Main session ([D], notes `R0_*`):**
  - Read in full: AAIB-28120 (28 pp.); the AAIB SR responses (Jan 2025); EASA AD 2025-0156; FAA AD 2026-04-12;
    PKBWL 2023-0061; PKBWL 2022/1097; Extra SB-NG-2-22A (+ SB-NG-1-22A and SL-NG-2-22A, not canopy-related).
  - Read in part: CS-STAN CS-SC110a; CS 23.783(e) and 23.807(b)(5); NUREG/CR-1278 Table 20-7; exida P+F FMEDA; the Honeywell
    GAPS datasheet; AC 23.1309-1E Fig. 2 and §11.b; the FAA AD 2010-25-01 DA40 comment; the NASA Fault Tree Handbook §7 /
    App. B; the Bliss 1995 abstract.
  - Re-read 6 dataset rows (G-FLOR, NTSB-008, R5-001, R5-074, and the two audit corrections).
- **Subagents ([D-ag]):**
  - R1: regulatory chain.
  - R2 + R5: the 241-row dataset.
  - R3: CS-23, Part 21, CS-STAN, Part-ML, Air Ops.
  - R4: MIL-HDBK-217F, HF abstracts, ACs, DO-160 summaries.
  - R6: open HF full texts.
  - Independent auditor: `R_audit_2026-11-04.md`.

## 9. Cold dry run (4 Nov 2026, 23:03, laptop UTC+3)

Fresh shell (`env -i` with only PATH, the D: temp variables and `PYTHONPATH=src`), output folder emptied first. The previous
outputs were moved to `D:\tmp_ideathon\easa\anchor\out_before_dryrun\`.

| Step | Result | Wall time |
|---|---|---|
| `python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json` | exit 0; 6 figures + set consistency, **0 errors**; `report.md`, `result.json` (241 occurrence rows, 13 fault cases), `fault_demo.html` | **21.2 s** |
| `python -m pytest -q tests/test_canopy.py tests/test_canopy_day.py` | **24 passed**, 125 checks | **12.1 s** |
| Open C1–C6 PNG, `fault_demo.html`, `annunciator_mockup.html` (browser pane) | all render; no console errors; C5 shows the 241-row counts | — |
| ux check of the regenerated `fault_demo.html` | 0 HATA · 1 UYARI (lamp colours, justified) | — |

Found and fixed: the manual ux audit of the fault demo lived inside `outputs/`, which a clean run regenerates. It now sits at
`02_EASA/outputs/day/fault_demo.denetim.md`.

## 10. Change log

- **Round 1 (4 Nov, 16:00–19:00).** Evidence catalogue; `aerokit.canopy`; Monte Carlo, FTA, FMEA and ERCS; figures C1–C5;
  12-step plan; glossary; mock-up.
- **Round 2 (21:00–22:30).**
  - Read SB-NG-2-22A, the FAA AD, PKBWL 2022/1097, CS 23.783(e) and NUREG/CR-1278.
  - Catalogue 146 → 241 rows; figure C6.
  - Extra NG named, with a back-up type.
  - Fault-injection demo → design change (red CANOPY SENS at take-off power).
- **Round 3 (22:40–00:45).**
  - Independent audit, with fixes and a merge-key bug repaired.
  - Re-run on 241 rows: C1–C4 identical; C5/C6 conclusions unchanged, take-off-roll share 9 % → 13 %.
  - Options B–D worked to depth.
  - R-10 mass corrected to ≤ 0.6 kg (GAPS datasheet) and the ≤ 3.5 mm sensor-gap constraint added.
  - This consolidation and the cold dry run.
  - Cold jury review (§6b): complacency sensitivity added (A3 stays 1 138× / 2.6×); summary and FHA wording corrected.

## Environment

No new packages. Temp files under `D:\tmp_ideathon\easa\` (downloads in `dl\`, anchors in `anchor\`). Python 3.12 with numpy,
pypdf, PyMuPDF and datawiz, all already installed.
