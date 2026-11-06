# 28 · Retrofit installation — how LOCK-SENSE is fitted to an Extra NG, and how it is accepted

> Updated 5 Nov evening with the Extra-specific findings of `docs/29_extra_ng_design_basis.md` (avionics base case G3X Touch, GMA 245R alert inputs, sensing trade-off, take-off numbers).

**Why this file exists.** An external review of `report.md` (5 Nov 2026; the file is now `outputs/day/analysis.md`) said the task's core deliverable was still
missing. The task asks how to retrofit the alert device to an aircraft, and the review asked for four things:
- a concrete mechanical and electrical installation;
- cockpit integration and the phase logic, with the reason for each input;
- ground tests with acceptance criteria;
- the limits of the tolerance study.

This file is that procedure for the recommended design (doc 27, Tier 4 / option O6).

**Figures.**
- `outputs/install/E1_electrical_schematic.png`
- `outputs/install/M1_sensor_locations.png`
- Both come from `scripts/easa_install.py`. Both are schematic and not to scale; datawiz 0 HATA; eye-checked.

**Tags.**
- [D]: read at source by the main session.
- [D-ag]: read by a research subagent.
- [K]: computed.
- [Y]: our design or judgement.

**Status.** This is a conceptual installation design. Every dimension marked "measure in step 2" must come from the
aircraft and from the manufacturer's data before any part is made. Certification is set aside, as the task says, so
nothing here claims approval.

---

## 0. What we know about the latch, and what we do not

**Known [D], from AAIB-28120 pp. 8–14 (`research/R0_AAIB_G-MIIL_report.md`):**
- The canopy is hinged on the right.
- Three steel shoot bolts on the canopy frame engage **roller lugs on the fuselage along the left cockpit edge**.
- Each bolt end is a ramp **15 mm long with a 5 mm rise**. The mechanical advantage is 3:1 as the roller climbs it,
  which compresses the seal.
- A tension spring holds the bolts on a linkage tube. There are two identical handle sets, front and rear.
- The handle centre distance is **70 mm locked and 60 mm partially locked**.
- The mechanism is enclosed in the frame: it is fitted before the outer skin is bonded on.
- After the G-MIIL break-up, the spring had pulled the bolts back into the "locked" position.

**Not known (no public source; manufacturer data or measurement needed):**
- the bolt travel per mm of handle;
- the bolt penetration into the lug at 60, 68 and 70 mm handle;
- the minimum safe engagement;
- the lug fastener pattern and the free space around each lug;
- the electrical bus voltage;
- the throttle quadrant layout (one lever or front and rear levers).

## 1. Mechanical installation (figure M1)

1. **Sensors at the receivers, fuselage side only.**
   - One inductive sensor (GAPS class: < 60 g, ≤ 3.5 mm sensing distance, 12–32 Vdc; datasheet [D]) beside each of
     the three roller lugs, facing the bolt tip at full engagement.
   - One seated sensor facing a passive steel target on the frame.
   - Nothing crosses the canopy/fuselage split line. The emergency opening and jettison path (push forward while
     opening, AAIB p. 11 [D]) is untouched.
2. **Brackets.** Machined aluminium angle brackets.
   - Mounting: under the existing lug fasteners, replaced by fasteners one grip-length longer of the same
     specification. **No new holes in the composite structure.**
   - If a lug pattern has no spare fastener, use a bonded bracket made under the manufacturer's composite repair
     instructions. Never drill a primary carbon structure ad hoc. The fuselage is all-composite (AAIB p. 3 [D]).
3. **Sensor gap.** Set the face-to-tip gap at full lock to about half the sensing distance (≈ 1.5–2 mm) [Y]. The
   bolt then reads clearly ACTIVE at full lock and clearly INACTIVE well before the 60 mm partial state. Measure it in
   step 2.
4. **Locking.** Jam nuts torque-striped, brackets safety-wired. This answers the "bracket moved" FMEA row.
5. **Bolt plunger flags (optional, doc 27).** A short spring-light plunger at each lug: a few newtons at most, so it
   cannot push pilots into a partial lock (R8-mechanical [D-ag]). It shows red until the bolt tip is home.
6. **Shaker:** an eccentric-mass motor (4.6 g class) potted into the throttle knob; flex lead along the lever
   (R7-haptic [D-ag]).
7. **Gate:** a solenoid detent on the throttle quadrant that only blocks **forward** travel past the run-up position.
   It never pulls the lever back. The detent is spring-retracted when unpowered. Release is a guarded trigger on the
   knob. A mechanical breakout covers a jam (R7-interlock [D-ag]).

## 2. Electrical installation (figure E1)

| Item | Design [Y] | Reason |
|---|---|---|
| Supply | own **5 A breaker "CANOPY WARN"** on the main bus; sensors 12–32 Vdc work on a 14 V or 28 V system | separate failure from other systems; GAPS range [D] |
| Sensor wiring | 2-wire NAMUR-style loops (shielded twisted pair, 22 AWG MIL-W-22759), one loop per sensor, routed along the left fuselage side away from the canopy hinge | line monitoring tells open (≤ 0.2 mA) and short (≥ 7 mA) from the signal states (R7-sensing [D-ag]) |
| Connectors | environmentally sealed, keyed, one per sensor at the bracket (field-replaceable) | maintenance; wrong-plug protection |
| Grounding | one star ground at the alert unit; shields grounded at the unit end only | avoids ground loops |
| Arming inputs | throttle-lever microswitch (primary), manifold pressure (independent second input), rpm (engine running), IAS and GPS ground speed (air/ground) | see §4 |
| Outputs | rear 3-colour lamp + front repeater; GMA 245R alert input (ALERT 2 or another free input; ALERT 1 carries GNX 375 traffic from NG048, SL-NG-03-22 [D]) **and** fail-safe input; knob shaker driver; gate solenoid driver; optional EFIS discrete | R7-aural/visual [D-ag] |
| EFIS link | **G3X Touch is the type design** (Extra SL-NG-01-22: "The EXTRA NG is equipped with a Garmin G3X Touch system", GEA 24 engine module [D]): one GEA 24 discrete set to "Canopy Closed", driven by the unit's own LOCKED output, never by a raw switch, and logged on the G3X data card. The AAIB names a G1000 for G-MIIL (fn. 1 [D]); if an aircraft has one, the unit stands alone | the G3X input is two-state and cannot see a short (Garmin note 13 [D]); our line-monitored unit does that work; conflict and reasoning in docs/29 §2 |
| Event log | non-volatile memory in the unit: every state change, gate event and override, with time | settles "was it locked?" (doc 27 Tier 5) |

## 3. Cockpit integration

| Element | Where | Check |
|---|---|---|
| Main lamp (rear seat, PIC) | top centre of the rear panel, just below the glareshield, on the pilot's centreline, 25 × 38 mm | within 15° head-down; on the take-off roll probably 25–40° off-axis, acceptable only with the unique voice cue (AC 23.1311-1C Note 4 [D]) — **measure in step 2** |
| Repeater (front seat) | same position, front panel, same logic, flash synchronised | AC 25.1322-1 [D-ag] |
| Voice "CANOPY, CANOPY" | both intercom positions through the audio panel | 15–25 dB above the masked threshold at take-off power under the pilots' headsets (Patterson CAA 82017 [D]) |
| Shaker | the knob of the throttle the PIC uses (both knobs if there are two levers) | felt through the pilot's glove at 2 600 rpm |
| Gate release | guarded trigger on the throttle knob; "CANOPY" shown at the quadrant | distinct act, not a push |

## 4. Logic and diagnostics

**Phase from the inputs.** Thresholds are proposals [Y]; the persistence filter on the latch sensors always runs.

| Phase | Condition | Alert behaviour |
|---|---|---|
| Parked | rpm below about 300 (engine not running) | lamp: green if locked, otherwise dark; quiet |
| Taxi | engine running, lever switch open, MAP below the run-up value, GPS GS < 30 kt | amber + one chime per state change |
| Line-up / run-up | lever switch closed **or** MAP above the run-up value, GS < 5 kt | red + voice + shaker; **gate engaged** (R8-timing T1) |
| Take-off roll | lever switch closed, IAS < 40 kt | red + voice + shaker (shaker stops at 30 kt, T9); gate free above 30 kt |
| Airborne | IAS > 55 kt for 5 s **and** GPS GS > 40 kt | red; a new voice alert deferred to lift-off + 5–10 s (T14, open); no shaker; no gate |

**Why these inputs.**
- **Lever switch:** the earliest signal. Alert onset is 0.35 s, against 1.65 s for rpm plus persistence. That
  difference changes the "acts" RF from 79× to 15× (O5 vs O5r) [K].
- **MAP as the second arming input:** on a constant-speed propeller the rpm reaches the governed value early. MAP
  follows actual power independently of the lever switch. This answers R7-interlock's "arm on actual power" and covers
  a failed lever switch.
- **IAS and GPS together for air/ground:** the Extra has no weight-on-wheels switch. Two independent speeds stop a
  single failure from arming the gate in flight.

**Self-checks and the fault log.**
- **Line monitoring:** an open circuit or a short on any loop gives FAULT, shown as "not locked", meaning amber on the
  ground and red at take-off power.
- **Disagreement checks:**
  - a bolt sensed while the canopy is not seated gives CANOPY SENS;
  - the two arming inputs disagreeing for more than 5 s gives CANOPY SYS.
- **Power-up test, observed by the pilot:** all lamp colours, the word "CANOPY", one shaker burst, and the gate
  engaging and releasing once. Each pilot sees, hears and feels these, so the test cannot report "pass" on its own.
- **Event log:** time-stamped states, faults, gate stops and overrides. Downloaded at each annual inspection.

**What the code already covers.** `src/aerokit/canopy/logic.py` and `tests/test_canopy.py` implement the phase logic,
the persistence filter, the voice deferral and sensor-fault handling, and the 13-case fault-injection demo exercises
them [K]. **Not yet in the code:** the MAP input, the gate driver, the shaker driver and the CANOPY SYS disagreement
check.

## 5. Mechanical tolerance — what the review asked for

1. **Handle position vs bolt penetration.** AAIB gives handle positions, not penetration, so 68 mm is a
   handle-equivalent trip point, not a proven safe engagement [D].
   - **Step 2 measures:** penetration δ of each bolt into its lug at handle 60, 65, 67, 68, 69 and 70 mm, three times
     each.
   - **Outputs:** the δ(handle) curve, and the gate δ_min for safe engagement, taken from the manufacturer's
     structural data. The sensor trip is then set at δ_trip ≥ δ_min + 3σ (rigging plus sensor).
2. **Sensor and mount tolerance.** The trip window from the tolerance study is 67.5–68.7 mm handle-equivalent at
   σ 0.3 mm [K]. The bench test (step 9) measures the real switching scatter on the actual bolt steel and replaces the
   assumed σ.
3. **Frame flex.** The canopy distorts at speed, and Van's warns this can disengage a switch (R7-sensing [D-ag]).
   - Fuselage-side sensing sees the bolt tip, not the frame, which reduces this effect.
   - The flight check (step 11) logs nuisance alerts during aerobatics.
4. **Vibration and wear.** The DG-1000 rear locking rod unscrews in service (85 FR 47638 [D-ag]).
   - Mitigations: re-check the trip at every annual and after any canopy work; record the result; torque stripes on the
     brackets.
5. **How independent are three sensors on one linkage?**
   - For a **partial lock** all three bolts move together, so the three sensors are **redundant**: any one of them
     sees it. That protects against a single sensor failure, not against a common rigging error.
   - For **one bolt out** (a loose fitting, a guide missed, as in the Europa MPD [D]) they are the **only**
     independent information. One sensor misses this (N−1)/N of the time (kit `08`) [K].
   - The Monte Carlo models exactly this split: a common partial lock and an independent one-bolt-out case, plus a
     common mis-rig case (`montecarlo.py`).

## 6. Ground verification — acceptance criteria

All thresholds are design proposals [Y], except where a source is given. "Pass" means every item, recorded on a signed
test sheet kept with the aircraft records.

| # | Test | Method | Pass criterion |
|---|---|---|---|
| G1 | Sensor gap | feeler gauge at full lock, each sensor | gap within the set value ± 0.3 mm and inside the datasheet sensing distance (≤ 3.5 mm [D]) |
| G2 | Trip point, each bolt separately | go/no-go gauge: handle held at 67.5 and 68.7 mm-equivalent | 67.5 → UNLOCKED, 68.7 → LOCKED, 10 cycles each, no exception (window from C2 [K]) |
| G3 | Partial lock | handle released at the 60 mm state | red + voice + shaker at line-up power, 10 of 10 |
| G4 | One bolt out | shim each bolt short in turn | UNLOCKED for every bolt, 10 of 10 |
| G5 | Not seated | canopy resting open on the rim | OPEN or SENS, never LOCKED |
| G6 | Open circuit | unplug each sensor connector | CANOPY SENS within 1 s; green off |
| G7 | Short to ground | short each loop at the connector | CANOPY SENS within 1 s; green off (≥ 7 mA band) |
| G8 | Loss of power | pull the 5 A breaker | lamps dark, green off, shaker off, **gate free**: full lever travel at normal force |
| G9 | Alert latency | video or logic analyser from lever switch closure | lamp, voice and shaker start ≤ 0.5 s, within 50 ms of each other (R8-timing T2, T4 [D-ag]) |
| G10 | Gate | engine run at line-up with canopy unlocked; then IAS and GPS inputs simulated above 30 kt | holds the lever at run-up; guarded release frees it; never engages above 30 kt; breakout force measured and recorded |
| G11 | Audibility | engine run at take-off power, the pilots' own passive and ANR headsets | voice clearly heard by 3 of 3 pilots; level ≥ 15 dB above the masked threshold if measurable (Patterson [D]) |
| G12 | Lamp in sunlight | FAA daylight method: low sun, aircraft rotated | red reads red and catches attention at every sun angle; ≥ 514 cd/m² measured (MIL-STD-411F [D-ag]) |
| G13 | Shaker | accelerometer on the knob at 2 600 rpm | ≥ 5 m/s² rms and ≥ 10 dB above the background in its band; felt through a glove (R7-haptic [Y]) |
| G14 | Emergency opening and jettison | force to open and to jettison, before and after installation | unchanged within measurement scatter; nothing snags |
| G15 | Compass | compass swing with the gate solenoid and shaker powered | deviation within the existing card limits |
| G16 | Fault-injection set | the 13 cases of `fault_demo` reproduced on the aircraft with a test harness | each gives the state the demo predicts |
| G17 | Event log | run G3–G10, then download | every event present with time and state |

Flight check (step 11), then release: nuisance alerts in an aerobatic sequence and in turbulence (target: none); voice
audible at cruise noise; shaker felt; log reviewed.

## 7. What the numbers in this project are, and are not (review problems 1, 2, 4, 5)

- **The risk numbers are conditional model estimates.** They hold under the assumptions in `inputs.json` and
  `cues.json`, where every value carries a source and a tag. Most hazard rates and pilot-check misses are [Y].
- **What the risk measures.** It is the probability of a take-off with an **unnoticed unsafe lock**. It is not the
  probability of losing the canopy or of a fatal accident. Fatal outcomes are a separate, relative measure.
- **Compliance is now swept as an independent parameter**, from c = 0.05 to 1 (`tradeoffs.md` §6, figure T3). The
  option ranking is the same at every c, and the ground gate keeps a gain at low c (2.5× at c = 0.05, 8.2× at
  c = 0.5) where alert-only options give 1.1–2.0× [K].
- **Zero counts are bounds, not zeros.** The sensing table gives count/n, the seed and the 95 % Wilson upper bound.
  For example, A3 missed "not seated" 0 times in 200 000 flights, so the probability is ≤ 2e-5 [K].
- **Sensor failure-rate transfer.** The rates come from an industrial NAMUR FMEDA multiplied by the MIL-HDBK-217F
  environment factor; they are not an installation rate. The result hardly depends on them: dividing by 18 or
  multiplying by 10 changes the RF by at most 2 %. Only ×100 lowers the gate's distrust RF from 16.3× to 14.6×. Adding
  shorts changes nothing, because line monitoring turns a short into a FAULT (`tradeoffs.md` §7) [K].
- **Certification targets are context, not compliance.** AC 23.1309-1E targets apply to system failure conditions.
  Our risk combines human error, mechanism state and pilot behaviour, so it cannot be compared one-to-one. The task
  also sets certification aside.
- **The system cannot see a structural failure.** If the frame breaks while the bolts stay locked, the system shows
  LOCKED (the new FMEA row). It does not address the AAIB cause of G-MIIL.
- **The occurrence data** are in `research/R2_occurrences.csv` and `R5_occurrences_add.csv`, 241 rows with one source
  URL each. An audit found a 1.5 % field-error rate, corrected (`R_audit_2026-11-04.md`). The data are a sample of
  investigated events, not a rate.
