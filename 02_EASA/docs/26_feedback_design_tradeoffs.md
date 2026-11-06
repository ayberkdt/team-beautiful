# 26 · Feedback elements — designs and trade-offs (official EASA task, 5 Nov 2026)

> Numbers updated 5 Nov evening after the reaction-time window and options O9/O10 were added to the model (`R8_*.md`). The integrated design catalogue with cost tiers is `27_design_catalogue.md`.

**Question.** The task sheet asks for an alert device and lists feedback elements: *"visual warning, auditory alert,
vibration, automatic engine shut-down, etc."* For the Extra NG, which combination works, and what does each element cost?

**Scope.** Alert system only. The latch itself is not changed, so there is no powered lock, latch fix or restraint
(user, 5 Nov). Certification and cost are set aside (task sheet).

**Sources.**
- Research notes: `02_EASA/research/R7_*.md`. Five topic notes, written 5 Nov by research subagents. The main session
  re-read 11 key claims at source; all were confirmed, and the scope notes are in `R0_spot_checks_of_agent_work.md`,
  round 4.
- Older notes: R4/R6 (alerting human factors), R0 (AAIB, EASA AD).
- Numbers: `python 02_EASA/scripts/easa_tradeoffs.py` writes `02_EASA/outputs/tradeoffs/tradeoffs.md` (all tables)
  and figures T1–T2 (datawiz: 0 HATA each; eye-checked).

**Tags.**
- [D]: read at source by the main session.
- [D-ag]: read at source by a subagent.
- [K]: computed.
- [Y]: our judgement.

---

## 1. Headline results

1. **Noticing, not sensing, is what limits an alert.**
   - The earlier "1 900×" assumed every alert is noticed. With realistic detection rates [D-ag + Y], LOCK-SENSE gives:
     - with a lamp alone: **4.3×**;
     - with lamp + voice: **23.5×**;
     - adding the throttle shaker: **79×**.
   - All three numbers assume a pilot who acts on every alert he notices, triggered by a throttle-lever switch, with a
     lognormal response time (median 1.5 s, 95th 3.0 s) that must fit before 40 kt (R8-timing) [K]. Triggered by rpm +
     0.5 s persistence instead, the shaker option falls from 79× to **15×** (O5r) [K].
   - The sensors miss a partial lock 4 times in 10 000 [K]. So the cues, not the sensors, are now the weak link.
2. **When pilots stop trusting it, every alert-only design falls to about 2–3×.**
   - The range is 1.3–13× over all uncertainties [K]. More cues barely help, because the problem is belief, not
     hearing.
   - PPV is 0.66 at our central nuisance rate, i.e. one alert in three is false [K].
   - The only element in scope that keeps a real gain under distrust is a **barrier on the ground**:
     - ground take-off gate: **16.3×** (5–95 %: 3.2–161×);
     - ground engine shut-down: **26×** (4.5–286×).
3. **In-flight engine shut-down puts the fatal risk back where no system is.**
   - It gives 35.3 fatal outcomes per 10⁶ flights, against 35.1 with no system [K].
   - Almost all of it comes from engine losses caused by false alerts in the air.
   - **Rejected.**
4. **Ground gate vs ground engine shut-down: a statistical tie.**
   - Over 4 000 uncertainty draws, each has the lowest fatal outcome about half the time (51 % gate, 47 % shut-down) [K].
   - In the multi-criteria score they are also tied: 0.757 vs 0.759, ranked first in 37 % vs 55 % of weight samples [K].
   - The shut-down's numeric edge comes from one judgement: we set a lower override probability for "restart and go"
     (0.30) than for a gate release (0.45) [Y].
   - **We choose the gate** because of its failure modes, not its numbers:
     - it can never cut the engine;
     - it keeps the engine running, so the pilot can just close the handle;
     - its worst credible failure (a detent jamming in flight) is covered by a mechanical breakout (R7-interlock).
   - R7-interlock reaches the same verdict on the ground ignition cut: "same benefit as B, much worse failure mode".
5. **How the gate is released matters as much as having one.**
   - A simple 50 N push-through gives **9.3×** and 3.8 fatal per 10⁶ flights.
   - A separate, guarded release with the reason shown gives **16.3×** and 2.2 [K].
   - Evidence: the G-IV pilot pressed past a throttle stop (NTSB AAR15-03, R7-interlock #18 [D-ag]). The FAA calls a
     "separate and distinct operation" the acceptable override (R7-interlock #15 [D-ag]).
6. **The organisers' worked example (one microswitch at one pin + EFIS message + tone) is a useful level 1 but not
   enough.**
   - It misses a single bolt out **2 times in 3** [K].
   - A short to ground reads as LOCKED. This is Garmin's own wiring note; that it cannot see the short is our
     inference [D].
   - A mis-set switch killed the RV-14 pilot (NTSB CEN23FA359 [D]).
   - It triggers on engine power (G3X IM [D]), i.e. late. RF: 4.6× if the pilot acts, 2.0× under distrust. Last in
     the multi-criteria ranking [K].

**What the absolute numbers mean.** Fatal outcomes per 10⁶ flights are **relative**. They rest on assumed hazard rates
and an assumed opening probability [Y]; there is no fleet data. Compare options with each other, not with accident
statistics.

---

## 2. Method in one paragraph

The sensing Monte Carlo (`aerokit.canopy.montecarlo`, 200 000 flights per cell) gives each architecture's miss
probability per hazard and its false-alert rate. The new cue layer (`aerokit.canopy.cues`, 9 tests) adds the pilot:

`risk = Σ_h u_h · [miss_h + (1 − miss_h) · (1 − D·c) · g]`

- **D** is the probability that at least one cue is noticed in time, weighted over conditions: normal 0.74, busy 0.25,
  no audio 0.01. Cues are combined two ways: as independent (upper bound) or fully dependent, i.e. the best single cue
  (lower bound).
- **c** is 1 when the pilot acts on every noticed alert. Under distrust it equals the alert's PPV (probability matching).
- **g** is the chance a barrier does not stop the take-off.
- **Fatal outcomes** add canopy openings (p_open × 9/76 fatal [D]) and the engine losses a device causes (BEA/Nall
  ranges [D]).
- **Inputs:** `02_EASA/inputs/cues.json`, one source and tag per value. Ranges are triangular; the nuisance and
  partial-lock rates are sampled on a log scale. The uncertainty run uses 4 000 draws.
- **Multi-criteria score:**
  - Three criteria are computed: effectiveness, distrust robustness, no new hazard.
  - Four are judged, each with a written reason: nuisance, any aircraft, retrofit effort, worst device failure.
  - The weights were accepted on 5 Nov. They are resampled 20 000 times to test how stable the ranking is.

---

## 3. Element by element

### 3.1 Sensing — what "locked" means

| Choice | Evidence | Verdict |
|---|---|---|
| **One sensor per latch point + one seated sensor** (LOCK-SENSE) | Misses a partial lock 4.4e-4, one bolt out 5.2e-4 [K]. Sense at the lug, not at the handle or drive: BD-10 pins missed the lugs with the light out; the L-39 SAFO reports separations "with a CANOPY LOCKED indication" (R7-sensing [D-ag]) | **chosen** |
| One switch at one pin (organisers' example) | Misses one bolt out 0.67 [K]; RV-14 switch set to "closed" before the pins seated, fatal [D] | level 1 only |
| Snap-action microswitch as the sensing element | Overtravel only ≥ 0.08 mm on the HM plunger, so it needs a lever (≥ 0.76 mm) and a rigid bracket; 25 000 operations; silver contacts unsuitable for low-current EFIS inputs, specify gold (R7-sensing [D-ag]) | acceptable with a lever, gold contacts and a gauge set-up |
| Reed + magnet | Operate ≥ 3.8 mm, release ≤ 12.7 mm: hysteresis too wide for mm-scale partial engagement; a wrong N.C. reed was once shipped in a kit (R7-sensing [D-ag]) | reject for depth sensing |
| Hall effect | 2.4–11.4 mm sensing distance; needs a magnet on each bolt (R7-sensing [D-ag]) | possible; magnet retention is a new failure mode |
| Inductive proximity (GAPS class) | ≤ 3.5 mm on the steel bolt tip, no target to fit, < 60 g (R0 [D]) | **chosen** |
| Line monitoring (NAMUR bands or end-of-line resistors) | Turns both open circuit and short to ground into FAULT; a plain switch-to-ground reads a short as LOCKED (R7-sensing [D-ag], Garmin note 13 [D]) | **required**; FAULT shows as "not locked" |

**Set-up is itself a failure mode** (RV-14). Each sensor's switch point is set with a go/no-go gauge at full and at
partial engagement. The result is recorded and re-checked at every annual inspection.

### 3.2 Visual

| Sub-option | RF acts / matches [K] | Evidence | Verdict |
|---|---|---|---|
| **Dedicated lamp**, top centre under the glareshield, 25 × 38 mm, red flashing 4 Hz, ≈ 1 000 cd/m² | O4 23.5× / 2.7× | Flash 3–5 Hz, equal on/off; steady if the flasher fails (HF-STD-001B §5.4.2.1.1.5–.6 [D]). Warnings within 15° of the line of sight, up to 35° only with a unique aural (AC 23.1311-1C Note 4 [D]). ≥ 514 cd/m² (MIL-STD-411F [D-ag]) | **chosen** |
| EFIS crew-alert message instead of the lamp | O4e 21× / 2.7× | G3X built-in function: yellow on the ground, flashing red at power or airborne (IM Rev AZ p. 30-214 [D]). The G1000 needs the aircraft maker to add a CAS message (R7-visual [D-ag]) | add **in addition** where an EFIS allows; never instead of the lamp |
| Front-seat repeater | — | Same logic as the main lamp, so both seats see it at the same moment (AC 25.1322-1 [D-ag]) | yes |

- **Legends:** green "CANOPY LOCKED" (earned only when all sensors agree), amber "CANOPY UNLOCKED" (ground),
  red flashing "CANOPY UNLOCKED".
- **Never "CANOPY OPEN":** the pilot sees a closed canopy and may disbelieve it (R7-visual).
- **Dark never means locked.**
- **Rear-seat problem:** on the take-off roll the lamp is probably 25–40° off the line of sight (not measured). That is
  why the visual cue alone reaches only 4.3×, and why it is paired with voice and vibration.

### 3.3 Auditory

| Sub-option | RF acts / matches [K] | Evidence | Verdict |
|---|---|---|---|
| **Voice "CANOPY, CANOPY"**, no lead tone, into an unswitched alert input | O4 23.5× / 2.7× | +15 dB over masked threshold is "difficult to miss", louder adds nothing; < 1 kHz useless on propeller aircraft (Patterson CAA 82017 [D]); a tone before the voice slowed responses (Simpson & Williams 1980, abstract [D-ag]) | **chosen** |
| Generic EFIS tone | O4t 21× / 2.7× | Must be matched to a meaning; can be confused with stall or gear tones (R7-aural) | second choice |
| Cockpit speaker for the headset-lost case | — | With the canopy gone, noise exceeds 100 dB(A); ISO 7731 §4.4 says use visual signals then (R7-aural [D-ag]) | reject; instead show "NO AUDIO" at power-up |
| Taxi chime, once, soft | included in O4 | Quiet while the canopy is open on purpose (task sheet worked example [D]); the DA40 shared light was ignored during open-canopy taxi (FAA AD 2010-25-01 [D]) | yes, once per state change |

- **Level:** 15–25 dB above the masked threshold under the headset, about 90–95 dB(A) at the ear for the warning.
- **Spectrum:** energy in 1–4 kHz.
- **Repetition:** the voice pair at onset, then every 15 s. After acknowledgement the sound stops but the red light
  stays.
- **Deferral:** a new voice alert stays deferred from 40 kt until 10 s after lift-off; the light is never deferred.
- **Expected detection:** about 0.62 on the take-off roll (Callan 2018 real DR400 flight, 61.9 % hits [D-ag, R6]).

### 3.4 Vibration

| Sub-option | RF acts / matches [K] | Evidence | Verdict |
|---|---|---|---|
| **Throttle-knob vibration**, eccentric-mass motor, pulsed 150/100 ms ×3, medium intensity | O5 79× / 2.9× (O4: 23.5× / 2.7×) | G-MIIL pilot's left hand stayed on the throttle (EASA case study slide 8 [D]). Tactile RT degrades less under load than auditory: +53 vs +148 ms (Mohebbi 2009, abstract [D-ag]). High-intensity hand cues caused 22.3 % wrong responses vs 4.2 % at low intensity (Meng 2015 [D]) | **chosen** |
| Stick shaker | — | Every pilot reads a stick shake as a stall warning; risk of a wrong push (R7-haptic) | reject |
| Lap-belt tactor | — | Works without hands; seat and back are blocked by the parachute (R7-haptic) | optional second tactor |

- **Frequency:** the Extra's propeller and firing lines sit at 120–135 Hz and 240–270 Hz [Y, from TCDS rpm]. So the
  cue is told apart by its **rhythm**, not its frequency.
- **Hardware:** 4.6 g motor, about 0.3 W only while alerting, about 15–30 g installed (Precision Microdrives datasheet
  [D-ag]).
- **What the shaker buys:** under distrust it adds almost nothing alone (2.7→2.9×). With the gate it doubles the
  "acts" gain: O6 1 236× vs O6n 585× [K]. Its value is to make the alert noticed when the voice is masked.

### 3.5 Barrier: take-off gate vs engine shut-down

| Option | RF acts / matches [K] | Fatal per 10⁶ flights [K] | Evidence | Verdict |
|---|---|---|---|---|
| **Ground take-off gate, separate guarded release, reason shown, override logged** | O6 1 236× / 16.3× | 2.15 (5–95 %: 0.39–10.5) | FAA treats a throttle stop as an "unmistakable warning" (G-IV report pp. 12–13 [D-ag]); 0 of 17 take-off-roll openings fatal [D] | **chosen** |
| Gate with 50 N push-through | O6p 950× / 9.3× | 3.79 | G-IV pilot pressed past the stop [D-ag] | reject the push-through; keep a breakout only for a jam |
| Engine shut-down on the ground (ignition cut) | O7 1 769× / 26× | 1.55 (0.74–7.9) | Same benefit as the gate; a logic fault in the air cuts the engine (R7-interlock) | tie on numbers; rejected on failure mode |
| Engine shut-down in flight | O8 1 769× / 26× | **35.3** (8.8–204) | Initial-climb openings 9/76 = 11.8 % fatal [D]; engine loss at take-off 17–19 %+ fatal (Nall 2002, BEA [D]); every false alert in the air becomes an engine loss | **reject** |
| Brake hold | — | — | Brakes stuck on in the roll ground-loop a tailwheel aircraft (R7-interlock) | reject |
| Power limiter | — | — | In the air it is a partial power loss, the worst kind (ATSB via BEA [D-ag]) | reject |

**Gate design rules** (R7-interlock design implications):
- It only blocks forward travel past run-up power. It never pulls the throttle back.
- It is armed only on the ground (IAS and GPS ground speed below 30 kt) and is armed on actual power or rpm, not on
  lever position alone.
- It never blocks taxi or run-up.
- Unpowered, it is free.
- It is released by a separate guarded action, with the reason "CANOPY" shown at the throttle.
- Every override is logged.
- "Gate inoperative" is shown on power-up.

### 3.6 Passive bolt marks (no electrics)

- A red band on each bolt shank, visible until the bolt is fully home.
- Under "pilot acts" they help: O5m 115× vs 79×, O6m 1 805× vs 1 236× [K].
- Under distrust they make no difference, or slightly worse: 16.3× → 15.7×. This is a property of the
  probability-matching model, not a real harm. Fewer hazards reach the alert, so its PPV drops and modelled trust falls.
- No evidence was found that marks alone prevent events (R7-visual).
- They need line of sight to each bolt, which may require a window in the frame inner skin. That is a structural change
  at the edge of our scope.
- **Keep as an optional walk-round cross-check. It also lets the pilot verify a red alert in seconds.**

### 3.7 Integration: EFIS or standalone

- **G1000 (the G-MIIL aircraft, AAIB p. 3 [D]):** no public description of spare discrete inputs, and CAS messages are
  set by the aircraft maker (R7-sensing/visual [D-ag]).
- **G3X Touch:** has a built-in Canopy Closed function [D].
- **Dynon SkyView:** analogue inputs could decode end-of-line states (R7-sensing [D-ag]).
- **Decision:** a **standalone alert unit** with its own lamp, audio feed, shaker and gate driver is the base design. An
  EFIS message and the EFIS data log are added where the EFIS allows.
- **Open point:** an unverified listing says some Extra NGs carry a G3X Touch. The G3X built-in logic could then host
  the message, but it uses a plain two-state input, so the line-monitored sensors still need our unit.

---

## 4. Recommended configuration (O6)

- **Sensing:** LOCK-SENSE, one inductive sensor per shoot bolt plus one seated sensor, line-monitored. Green only when
  all four agree; a FAULT counts as not locked.
- **Visual:** dedicated three-state lamp and a front repeater. Red flashing at 4 Hz at take-off power; amber on the
  ground; green earned.
- **Auditory:** voice "CANOPY, CANOPY" at take-off power and in flight; one soft chime in taxi; deferral 40 kt to 10 s
  after lift-off.
- **Vibration:** throttle-knob pulses while red, medium intensity.
- **Barrier:** ground take-off gate with a separate guarded release and logging. No engine shut-down, on the ground or
  in the air.
- **Optional:** bolt marks; EFIS message and log.

**Multi-criteria result:**
- O6 score 0.757, first in 37 % of weight samples, mean rank 1.8.
- O7 score 0.759, first in 55 %, mean rank 2.0 (tie; gate chosen on failure mode).
- O9 mechanical throttle pawl 0.710; O10 starter guard 0.638 (added 5 Nov evening, see doc 27).
- O5 score 0.619.

"No system" is ranked first in 8 % of samples. That happens only when the weights shift heavily to the four judgement
criteria, on which doing nothing scores perfectly.

---

## 5. Limits — what the model cannot see

- **Detection probabilities are judgement** built from laboratory, driving and light-aircraft data (R7). None was
  measured in an Extra NG.
- **Missing measurements:** the rear-seat lamp angle, cockpit noise and throttle vibration of the Extra. All three need
  a ground run.
- **Override probabilities** for the gate come from analogies: G-IV, machine-guard defeat (a respondents' estimate),
  the 1974 seat-belt interlock. There is no aviation measurement.
- **Probability matching is a worst-case behaviour model** (abstract-level evidence, R4). A pilot who can verify the
  canopy quickly probably trusts the alert more.
- **Fatal outcomes are relative.** The opening probability after an unlocked take-off is unknown (0.2–0.9 sampled).
- **The model covers the take-off decision.** Openings in cruise (24 of 126 [D]) get the alert but not the gate.

## 6. What this changes in the existing kit (not yet applied — the deck and report are paused)

1. Lamp legend "CANOPY UNLOCKED", never "OPEN"; voice "CANOPY" twice, no lead tone.
2. Gate: separate guarded release instead of the 50 N push-through; arm on rpm or power; log overrides.
3. Shaker: rhythm 150/100 ms ×3 and medium intensity.
4. Base design: standalone unit; EFIS as an addition (`kit/12` says the opposite and needs fixing).
5. Remove option C (powered lock) wherever it appears as a next step (scope rule).
6. Replace the "1 900×" headline with the realistic chain: 23.5× (lamp + voice), 79× (+ shaker), 1 236× (+ gate), and
   16.3× under distrust.
