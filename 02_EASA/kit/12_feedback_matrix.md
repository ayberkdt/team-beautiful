# EASA kit · 12 — Feedback elements: what the pilot gets, when (official task, 5 Nov)

The official task sheet (`official_2026-11-05/EASA retrofit challenge.docx`) asks us to choose the feedback elements:
*"Visual warning, Auditory alert, Vibration, Automatic Engine Shut-down, etc."* It also says to disregard certification
and cost. This piece records what we picked for each element and why. Tags: [D] read at source · [K] computed by
`canopy_day.py` · [Y] our judgement.

## 1. The matrix (Extra NG, LOCK-SENSE)

"Not locked" means the canopy is not seated, or any of the three shoot bolts is short of full depth, or a sensor code is
invalid. An unconfirmed lock counts as not locked.

| Phase (how detected) | Visual | Auditory | Vibration (throttle knob) | Take-off gate | Engine |
|---|---|---|---|---|---|
| Parked, engine off | green if locked, dark otherwise | — | — | — | — |
| Taxi, canopy open for air (ground, throttle below run-up) | amber CANOPY | one chime | — | — | runs |
| Run-up / throttle beyond run-up on the ground | red, flashing | voice "CANOPY" | pulses | **holds the throttle at the run-up detent** | runs |
| Take-off roll (IAS ≥ 40 kt) | red, flashing | voice deferred 40 kt → 10 s after lift-off (new alerts only) | pulses | free (never active above 30 kt) | runs |
| In flight (0.5 s persistence) | red, flashing | voice "CANOPY" | pulses | free | runs |
| Sensor fault | amber on the ground, red at take-off power | as the phase | as the phase | as "not locked" | runs |

Phase logic, persistence, the voice deferral and the sensor-fault rule are already implemented and tested in
`src/aerokit/canopy/logic.py` (`tests/test_canopy.py`) [K]. The vibration cue and the take-off gate are new on 5 Nov
and are **not modelled** in the Monte Carlo yet.

## 2. Each element

**Visual [kept].** Three colours: green CANOPY LOCKED is the only "safe" state and must be earned by all four sensors;
amber = caution; red, flashing = warning. On the Extra NG the lamp sits in the rear-seat glare shield with a repeater
in front, and the same state goes to the G1000 as a crew-alert message (integrated variant, §3).

**Auditory [kept].** One chime in taxi; at take-off power and in flight the single word "CANOPY", always paired with the
light. Quiet in taxi with the canopy open on purpose: this is the official worked example's idea ("prevents annoying
nuisance alarms while taxiing … but triggers a loud scream if one pushes the throttle forward") [D], and our cry-wolf
result says why it matters: 1 900× if pilots act on every alert, about 3× once nuisance alerts teach them to ignore it [K].

**Vibration [added: throttle-knob shaker].** A small eccentric-mass motor in the throttle knob pulses while the alert is
red. Why the throttle: the G-MIIL pilot "flew with his left hand permanently on the throttle" (EASA case-study slide 8,
speaker notes) [D], so the hand is on the cue exactly when it matters. Why vibration at all: the voice can be masked or
lost. G-MIIL's pilot lost his headset and glasses when the canopy broke up (slide 7 notes) [D]. Mass and power are
small (a phone-class vibration motor is a few grams and well under 1 W while running [Y]). Mounting it in a stick grip
was rejected: aerobatic stick inputs would mask it [Y].

**Take-off gate [added, ground only].** A solenoid-driven detent in the throttle quadrant holds the lever at run-up power
while the canopy is not locked **and** the aircraft is on the ground (IAS < 30 kt and GPS ground speed < 30 kt) [Y].
- It does not cut or reduce power. It only stops the lever from going further.
- A firm push breaks through the detent (breakout force about 50 N [Y]), so a failed sensor can never trap a pilot.
  Overriding the gate is a deliberate act, and the event log records it.
- With the solenoid unpowered, the detent is retracted. A power loss or failed alert unit therefore leaves the throttle
  free (fail-free), and the dark green lamp already tells the pilot something is wrong.
- It is never active above 30 kt or in the air.
- Why: alerts alone collapse to about 3× under distrust; the only option in our trade that keeps more (C, powered lock,
  6×) does it by removing the hazard instead of warning about it [K]. The gate brings that idea to the take-off decision
  without touching the latch.

**Automatic engine shut-down [rejected].**
- In the air: 76 of 126 lock-related openings happened in the initial climb and 17 on the take-off roll [K, catalogue].
  An open canopy is survivable in most cases (16 of the 126 lock-related openings were fatal [K, catalogue]); shutting
  the engine there would turn it into a forced landing at low height.
- On the ground: the gate does the same job (no take-off with an unlocked canopy) and keeps the engine running, so the
  pilot can simply close the handle and continue.

## 3. Two installation variants (the task: "depends on what aircraft you choose, with what instrumentation")

| | Integrated (glass cockpit) | Standalone (analogue panel) |
|---|---|---|
| Example | Extra NG: Garmin G1000 EFIS [D, AAIB p. 3 fn. 1] | steam-gauge aerobatic types, gliders, older home-builts |
| Logic | LOCK-SENSE alert unit (hardware AND for green) + one discrete into the EFIS | the same alert unit on its own |
| Display | lamp + EFIS crew-alert message | lamp only |
| Audio | audio-panel alert input | small speaker / headset injector |
| Recording | EFIS data card **and** the unit's own event log | unit's event log |
| Phase inputs | throttle switch, IAS and GPS speed from the EFIS | throttle switch + a pitot pressure switch |

The green lamp never depends on EFIS software: if the EFIS fails, the lamp still works.

## 4. How this relates to the organisers' worked example

Their example (one microswitch at one locking pin into an EFIS discrete) is our **level 1**. We keep its logic idea
(quiet in taxi, loud at throttle forward). We step up in three places:

1. **One sensor per latch point.** The Extra NG has three shoot bolts (front, centre, rear: case-study slide 25) [D]. One
   switch at one pin misses a single bolt out (N − 1)/N of the time, two in three on this type [K, kit `08`].
2. **Locked, not closed.** The input is labelled CANOPY LOCKED, never "Canopy Closed".
3. **Self-checking outputs.** A plain switch to ground reads "locked" when the wire chafes to ground, and nobody sees it.
   Line-monitored sensors turn that into a sensor fault (amber or red) instead of a false green [K, fault demo].
