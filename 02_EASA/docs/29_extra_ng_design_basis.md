# 29 · Extra NG design basis — the aircraft, how "not locked" is detected on it, and the sensing trade-off

**Decision (team, 5 Nov 2026):** the example aircraft is the **Extra NG**. Everything below is specific to it.

**Sources.**
- Three new research notes (5 Nov evening):
  - `R9_extra_ng_canopy_cockpit_performance.md`: the aircraft, from Extra's own SBs and SLs, the TCDS, AAIB, BEA and AOPA.
  - `R9_lock_sensing_precedents.md`: how other aircraft detect "not locked".
  - `R9_not_locked_detection_physics.md`: the physics and the sensing options.
- The main session re-read 8 of their key claims at source; all were confirmed (`R0_spot_checks_of_agent_work.md`,
  round 6).
- Numbers come from `scripts/easa_tradeoffs.py` (`outputs/tradeoffs/tradeoffs.md` §8).
- Figures: `outputs/figures/F8.png` (take-off timeline) and `F9.png` (sensing options), both from
  `figures_src/build_figures.py`.

**Tags.**
- [D]: read at source by the main session.
- [D-ag]: read by a research subagent.
- [K]: computed.
- [Y]: judgement.

---

## 1. The Extra NG canopy as the pilot uses it

| Item | Fact | Tag / source |
|---|---|---|
| Hinge | Right side, three steel hinge pins. Opens to the right; a nylon lanyard holds it open. | [D] AAIB p. 8 |
| Locks | Three steel **shoot bolts** on the canopy frame engage **roller lugs** on the **left** fuselage sill. Each bolt ends in a ramp 15 mm long with 5 mm rise (3:1). | [D] AAIB p. 8 |
| Handles | Two identical sets, front and rear, on **one linkage tube**. A tension spring pulls the tube towards locked. To unlock, squeeze the sliding handle towards the fixed handle. | [D] AAIB p. 9 |
| The trap | Close the canopy and let go: the spring takes the handle only "just into the green lock area". Handle centres are **60 mm** apart (partial lock); full lock (**70 mm**) needs a pull **fully rearward**. 70 mm is also the reading when the canopy is **open with handles released**. | [D] AAIB pp. 9, 20 |
| Forces | 136 N to open from full lock, 90 N from partial lock, 60 N from partial to full lock. | [D] AAIB p. 20 (R0) |
| What the pilot can check | The bolts are hidden in the frame. There is **no visible difference** at the frame edge between partial and full lock. The cues are the handle against the placard and a "clunk" at full lock. | [D] AAIB pp. 10, 20 |
| Placard history | **SB-NG-1-24** replaces the initial placard (fitted up to NG064 and canopy serial 071) with a new one, "to reduce the misuse of the canopy locking". On the initial placard, a partly locked handle already sat in the green; on the new one, green covers only the far LOCK end. | [D] SB pp. 1–2; the green-area reading is from SB Fig. 1 [D-ag] |
| Mechanism states | NG001–060: original pawl contour. NG061+: new contour plus spring (ECO). Retrofit by AI-NG-01-23 / AI-NG-02-23. | [D-ag] R9-extra §1.4 |
| Checklist | Canopy latch is a before-take-off item. The POH text itself (Rev 18, 17 Nov 2025) needs registration and was not read. | [D-ag] AOPA; POH status sheet |
| Jettison | AAIB: push the canopy slightly forward while opening. PKBWL: it moves back on the hinge guides. The two descriptions conflict; unresolved without the POH. | [D] AAIB p. 11; [D-ag] PKBWL |

**Event pattern across the Extra family** (R9-extra §5 [D-ag]):
- The spring-loaded handle can rest in a near-locked position, and pilot checks keep missing it:
  - D-EFBY (Extra 300): the pilot pushed upward "by habit" and found nothing.
  - N300EX: the pilot says he checked "three times".
- On the older Extras the canopy opened **at rotation**. On the NG it stayed shut through take-off and opened **at high
  speed or after aerobatics** (SP-HMM twice; G-MIIL disputed).
- SP-HMM 2023: the front occupant may have loosened the locks in flight.

**Consequence for the design.** We need **both** a pre-take-off alert and **in-flight** monitoring. The in-flight
message must be "fly, do not re-latch": four reports show re-latch attempts opening the canopy fully (R8-latches).

## 2. Cockpit and systems the retrofit plugs into

- **Avionics: the G3X is the design case.**
  - Extra's own service letter says "The EXTRA NG is equipped with a Garmin G3X Touch system", with a GEA 24 engine
    module (SL-NG-01-22 [D]).
  - The AAIB report says G-MIIL had a G1000 (fn. 1 [D]). R9-extra judges this an AAIB error, because the SL covers
    serials up to NG035, which includes G-MIIL (NG028).
  - We design for **G3X Touch**: its built-in "Canopy Closed" discrete gives yellow on the ground and flashing red with a
    tone at power or airborne (G3X IM p. 30-214 [D]).
  - **The G3X input is driven by our unit's LOCKED output, never by a raw switch.** The input is two-state and cannot
    see a short (Garmin note 13 [D]).
- **Audio:** GMA 245R on the left tunnel wall (SL-NG-03-22 [D]).
  - From NG048, ALERT 1 IN carries the GNX 375 traffic audio.
  - Use ALERT 2 (or a free alert input, to be confirmed per serial) plus the fail-safe input.
- **Electrical:** 12 V battery and 60 A alternator, so 14 V nominal [D-ag; 14 V is R9's inference]. The main electrical
  board sits behind the left gear cuff.
- **Engine controls:** throttle on the left wall. The pilot's left hand stays on it: "permanently on the throttle"
  (AAIB [D]).
  - The TCDS holds an **equivalence finding on the position and shape of the engine controls** [D-ag]. A shaker in the
    knob or a throttle gate would touch it.
  - Certification is set aside in this task, but in reality this would be the most debated change. A fall-back is a thin
    shaker sleeve on the lever below the knob.
- **Lamp location:** rear panel, top left beside the ASI, or the strip under the G3X bezel. Both are in the pilot's
  central view (R9-extra §3.3 [Y], from a lookbook photo).
- **Minimum crew:** one pilot, in the rear seat (TCDS [D-ag]).

## 3. How "not locked" can be detected on the Extra NG

### 3.1 What physically differs (R9-physics §1.4–1.5)

| Quantity | Full lock vs partial lock | Sees one bolt out? | Reads "locked" when open with handles released? |
|---|---|---|---|
| **Bolt tip position at each roller lug** | 10·r mm, where r = bolt mm per handle mm, **not published**, bracketed 0.5–1.5 | **yes** | no (no lug there) |
| Handle / linkage tube stroke | 10 mm at the handle [D] | **no** (common tube) | **yes** (70 mm) |
| Seal compression / frame gap | 0–5 mm, and only under uplift; no visible difference on the ground [D] | partly | no |
| Force / strain | no clean position information; a jammed bolt carries load | no | — |

**The real margin is small.** The trip point sits 2 mm of handle travel short of full lock, i.e. **2·r mm of bolt
(1–3 mm)**. With the project's hazard definition, a working trip window exists only if the total scatter is
≤ 0.45 mm handle-equivalent (R9-physics, `r9_window.py` [K]). Every per-bolt option meets this if r ≥ 1; none reliably
does if r ≈ 0.5. **So the first measurement on the aircraft is r** (bolt penetration at handle 60, 65, 67, 68, 69 and
70 mm).

### 3.2 What other aircraft teach (R9-precedents [D] / [D-ag])

- **Monitor directly, at each lock.** AC 25.783-1A asks for an indication that directly monitors the door closed,
  latched and locked, with an erroneous "locked" indication no more likely than 10⁻⁵ [D]. The FAA memo after UAL811
  says the same: monitor the positions "directly" [D].
- **Every false "locked" in the record read the handle, the drive or one pin, not each receiver.**
  - DA40 PH-TIN: one micro switch reads the front pin's aft movement [D]; both pins were out.
  - Pitts G-IIDY (lever horn), L-39 G-OALB (handle stows regardless), Duo Discus (handle locked, pins not connected) and
    RV-14 (switch set early, fatal) [D, R8/R7].
- **Nuisance alarms cause harm too.**
  - Fokker 100: a mis-rigged handle switch gave a false DOOR NOT LOCKED; the crew worked the handle and the door
    opened [D-ag].
  - AAIB G-LDGB: the door detached after the instructor pushed the handle in flight to demonstrate door warnings [D-ag].
- **Dormant sensor failures exist.** An Embraer AD added a 12-month sensor test because a jammed sensor showed "locked"
  [D-ag]. This supports our transition self-test on every flight.

### 3.3 Sensing options compared (model [K], `tradeoffs.md` §8, figure F9)

Each option runs through the same Monte Carlo with its own trip scatter, false-"locked" rate and nuisance rate. The
inputs (R9-physics §4.3) are judgement except where a datasheet exists. The table shows the risk reduction **when the
pilot distrusts the alert**, with the recommended cue set (lamp + voice + chime + shaker + ground gate).

| Option | Sees partial / one bolt / not seated | False + nuisance per 1 000 flights | Distrust RF (central) | Distrust RF if r = 0.5 | Verdict |
|---|---|---|---|---|---|
| **S1 Inductive × 3 + seated, line-monitored (LOCK-SENSE)** | Y / Y / Y | 0.14 | **44.6×** | 2.3× | **chosen** |
| S4 Snap-action switch × 3 at the lugs + self-test | Y / Y / Y | 0.31 | 16.3× | 2.3× | fall-back: exposed mechanism, rigging-sensitive |
| S2 Bare bolt contact × 3 with 1 k / 10 k resistors (team idea) | Y / Y / Y | 1.01 | 5.4× | 2.3× | demonstrator, not flight |
| S3 Bare bolt contact × 3, plain two-wire (team idea as first proposed) | Y / Y / Y | 1.01 | 5.3× | 2.3× | no: a harness short reads LOCKED |
| S5 Hall + magnet × 3 | Y / Y / Y | 3.59 | 3.0× | 2.2× | no: magnet drift widens the scatter |
| S6 LVDT on the linkage tube + seated sensor | Y / **N** / Y | 0.10 | 6.0× | 6.0× | add-on trend channel only |
| S7 Handle switch alone | Y / **N** / **N** | 0.10 | 5.7× | 5.7× | no: blind to one bolt, not seated and open-released |

**How to read it.**
- When pilots distrust the alert, the **nuisance rate decides the result**. The non-contact, hermetic inductive sensor has
  the lowest nuisance and keeps the most (44.6×).
  - The main trade-off model (doc 26/27) uses the more conservative nuisance rate of `inputs.json` (3e-4) and gives
    16.3× for the same design.
  - The 1e-4 used here is R9's judgement for a hermetic non-contact sensor. Treat 16–45× as the range.
- **Linkage and handle sensors are blind to one bolt out.** This is exactly the SP-HMM "loose rear fitting" case. Their
  ceiling is about 6× whatever the cues.
- **If r is only 0.5**, every per-bolt option drops to about 2× under distrust. The reason: full lock starts to read
  "not locked", so nuisance rises. Measuring r and re-deriving the trip window is a gate before any hardware.

### 3.4 The team's bolt-contact idea (circuit closes only at full lock)

- **Right location, wrong physics for flight** (R9-precedents and R9-physics agree):
  - Fretting took tin contacts from 1 mΩ to over 1 Ω in under 20 minutes at 10 cycles per minute; gold does not fret
    [D]. Under ±10 g aerobatic vibration this means in-flight nuisance alarms.
  - Water, salt film or metal swarf between ring and plate can bridge the gap and read "locked". With the resistor
    scheme, a leak below about 638 Ω fakes LOCKED (R9-physics [Y]).
  - The plate must be insulated from the roller lug. Otherwise current flows through structure, lug and roller, and the
    circuit reads "locked" at partial lock.
- **Resistors fix the wiring faults, not the contact faults.** With 1 kΩ in series and 10 kΩ in parallel there are four
  states:
  - about 1 kΩ: locked;
  - about 11 kΩ: not locked;
  - open circuit: fault;
  - about 0 Ω: fault.

  Wire breaks and harness shorts become faults, but contact drift and bridging remain.
- **Use:** an excellent **bench demonstrator** of the logic (cheap, visible, easy to explain). Gold-plated, sealed and
  insulated, it is the "basic tier" for aircraft without a power supply budget. The flight design stays inductive.

## 4. Extra NG design decisions (updated)

1. **Sensors.**
   - Three line-monitored inductive sensors on the left fuselage sill, one beside each roller lug, facing the bolt tip at
     full engagement, plus one seated sensor.
   - Nothing on the jettisonable canopy, and no drilling of the bonded carbon frame.
   - **Calibrate each trip on the aircraft:** the steel lug sits inside the sensor's metal keep-out zone (Ø 40.6 mm,
     R9-physics [D-ag]).
2. **Rigging per configuration.** Set the trip per pawl configuration (NG001–060 vs NG061+) and re-check after any
   canopy removal, SB-NG-2-22 foam work or canopy replacement.
3. **Self-test on every flight.** Every canopy opening must show each bolt sensor going INACTIVE and then ACTIVE (a
   transition test), so a stuck sensor cannot stay hidden (Embraer AD lesson).
4. **Lamp.** Rear panel, top left by the ASI, or under the G3X bezel. Legend "CANOPY UNLOCKED" / "CANOPY LOCKED". A
   front repeater is recommended, because the front handle can be moved in flight.
5. **G3X integration.** The unit's LOCKED output drives a GEA 24 discrete set to "Canopy Closed" (G3X crew alert) and
   is logged on the G3X data card. That gives a recorded lock state, which would have settled the AAIB–BFU dispute.
6. **Audio.** GMA 245R ALERT 2 (confirm it is free on each serial) and the fail-safe input. Voice "CANOPY, CANOPY".
7. **Power.** From the 14 V bus through a dedicated breaker on the centre-console panel.
8. **Arming.** A throttle-lever switch (onset 0.35 s) plus MAP from the G3X EIS as the independent second input
   (doc 28 §4).
9. **Shaker and gate.** Keep both in the design (they carry the distrust gain), and state the TCDS engine-control
   equivalence as the real-world caveat. The fall-back is a lever sleeve instead of a knob change.
10. **In flight.** Red plus voice whenever any bolt leaves full lock. The message is "fly, do not re-latch". This covers
    the NG pattern of openings at speed and the front handle moved in flight.

## 5. Take-off time budget with Extra NG numbers (figure F8)

- **Lift-off at 80 KIAS, tail up at about 40 KIAS** (AOPA 2020 flight test [D-ag]). No NG take-off roll is published;
  the nearest is the Extra 300 at 105 m and 950 kg (BEA D-EFBY [D]).
- F8 keeps the two acceleration cases of the timing study (5.0 and 2.8 m/s²). This keeps the 30 kt and 40 kt times
  consistent with `cues.json`:
  - 30 kt at 3.1 or 5.5 s;
  - 40 kt at 4.1 or 7.4 s;
  - lift-off at 8.2 or 14.7 s after 169 or 302 m [K].
- **Brisk case:** with a lever-switch alert the median pilot acts at **18 kt** (95th percentile: 33 kt). With an rpm
  trigger the median pilot acts at **31 kt** (95th: 45 kt), past the 30 kt gate [K].
- **The best moment is before power:** the red stage at line-up (R8 T1), and the canopy item both in the before-take-off
  check and last at line-up.

## 6. Measurements needed on the aircraft (before any hardware)

1. **r:** bolt penetration at handle 60, 65, 67, 68, 69 and 70 mm, each bolt, three times. This decides the trip window
   and whether a per-bolt sensor can work at all.
2. Free space and sight line to each bolt tip at its lug, on the fuselage side.
3. Sensor face-to-tip gap at full lock, and the effect of the steel lug inside the keep-out zone (calibration curve).
4. Which GMA 245R alert inputs are free on the serial; G3X GEA 24 spare discretes.
5. Whether the front and rear throttles are linked; the lever's free length for a shaker sleeve or gate.
6. Cockpit noise and throttle vibration at take-off power (for the voice level and the shaker).
7. Which jettison motion the POH describes (forward push or aft movement), so that no part ever obstructs it.

## 7. What this changes in earlier documents

- **doc 28 §2 / §3:** the avionics base case becomes **G3X Touch**, with GEA 24 discrete and GMA 245R ALERT 2. The G1000
  path stays as the alternative. The audio row should not use ALERT 1 (GNX 375 from NG048).
- **docs 26/27:** the sensing choice is now backed by a seven-option trade (§3.3). The nuisance-rate range for the chosen
  sensor is 1e-4 to 3e-4, giving 16–45× under distrust with the recommended cues.
- **Report:** the "1 900×" headline is gone. The take-off figure (F8) now uses the AOPA lift-off speed of 80 KIAS.
