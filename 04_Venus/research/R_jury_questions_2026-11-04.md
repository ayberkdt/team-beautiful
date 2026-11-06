# VESPER (doc 25): the 10 most damaging jury questions

Jury: a planetary scientist and a LuGus Studios drone-simulator engineer. Source read cold: `04_Venus/docs/25_lugus_venus_rotorcraft.md`
(all 633 lines, 4 Nov 2026). Probed: `src/aerokit/venus/{power,sizing,descent,design,materials,link,bemt,performance}.py`,
`04_Venus/outputs/sensitivity.json`, notes `D_landis_haag_2013_solar.md`, `D_venkatapathy_2017_venus_edd.md`,
`D_dutta_2012_venus_entry.md`, `B_izraelevitz2025_aerobot.md`, `K_review_doc25.md`. My numerical probes are in
`D:\tmp_ideathon\venus\r5\probe.py`, which runs the team's own code read-only. Line numbers are doc-25 lines.

Ranked from most to least damaging.

---

## 1. Your rear solar face gives 42 % of the power. Which flight-qualified triple-junction cell is bifacial at 0.85?

**Why it hurts.** The doc says "bifacial triple-junction cells (29 % AM0 array) … the underside earns ~73 % of the
topside [Y bifaciality 0.85]" (l.185–188). Everything built on sunlight rests on this assumption: "an overhead Sun even
covers hover" (l.49), the cos z 0.595 threshold, the 44 h of solar flight and the 2.2× noon margin (l.443).
- In code, `power.SolarArray.power` adds `rear = front × solar_ratio_up_down × bifaciality`, with `bifaciality = 0.85  # [Y]`.
  The rear face is therefore 1 − 1/1.73 = **42 % of the array output**.
- The source of the front-face number does not cover the rear. `D_landis_haag_2013_solar.md` says Landis & Haag assume
  "no albedo/upwelling light from the cloud deck (relevant for bifacial…)".
- `sensitivity.json` has no bifaciality case and no up/down-ratio case. The only solar case is cell efficiency.
- My rerun with the team's code (`probe.py`) gives:

  | Bifaciality | Noon output | Loiter window | Noon hover on solar? |
  |---:|---:|---:|---|
  | 0.85 | 2965 W | 45.8 h | yes |
  | 0.5 | 2448 W | 40.6 h | yes |
  | 0 | 1710 W | 26.7 h | no, never |

- Domain knowledge, not checked in the notes: standard space triple-junction cells (GaInP/GaAs/Ge) have an opaque Ge
  bottom cell and full back metal, so their bifaciality is about zero.

The cross-check in §7.1 ("Sun threshold: code 0.595 / closed form 0.595, −0.0 %") is not independent. It reuses the
same Eddington law [Y] and the same 0.85.

**A good answer needs.** A named cell technology with measured rear response, or a monofacial baseline. The design
would then be re-closed: a smaller window (~27 h), hover never on solar, and possibly a larger deck and more mass.
Bifaciality and the up/down ratio also belong in F9/F10.

**Already answered?** **No.** The value is tagged [Y] (l.188) but never stress-tested.

---

## 2. (Planetary scientist) Why fly a rotorcraft at all? JPL's variable-altitude aerobot, which you cite, controls altitude over 52–62 km for months. You fly 49 h with 3 kg. What science do you get that VEGA (1985) did not?

**Why it hurts.**
- The doc's rehearsed answer contradicts its own source. It says a rotor "controls altitude, which balloons cannot"
  (l.593–594). Its cited note `B_izraelevitz2025_aerobot.md` describes a variable-altitude aerobot flown in 2022 at
  Venus-54–55 km density. That note gives a full-scale altitude range of "52–62 km", a goal of "117 Earth days", and
  "15–230 kg payload".
- VESPER's own numbers come close to VEGA's: 49 h and 11 500 km of drift, against VEGA's 46 h and ~11 600 km with
  7 kg gondolas (l.400–401).
- The science is all [Y]. Section 6 gives one sentence of goals (l.401–403). The doc names no instruments, gives no
  measurement requirements, and has no traceability. Only `design.json` labels the 3 kg / 30 W payload as
  "nephelometer, aerosol mass spectrometer, T/p/wind/turbulence, camera" (Y).
- The 55 km altitude was chosen for battery temperature, not science (l.117–125).
- The lower cloud is visited for **5 min, twice** (dives to 51 km, l.398). The upper cloud (56.5–70 km, where the UV
  absorber sits) is never sampled.

**A good answer needs.** A science traceability matrix: questions, measurements, instruments with mass and power, and
the altitude and time they need. It should show one thing a balloon or aerobot cannot do (for example, fast repeated
vertical profiles at 3 m/s, or controlled sampling inside downdrafts), with numbers. The team should also delete the
"balloons cannot" line.

**Already answered?** **No.** There is only the one-liner, and it is contradicted by the team's own note.

---

## 3. Your peak g is above the ADEPT envelope but your heating is 30–40 % below it, at the same β and γ. Both cannot be "conservative". What is the heat shield made of, and how was its mass sized?

**Why it hurts.**
- The doc calls the model "conservative at the steep edge" because of g: 56 g against the 35–45 g envelope (l.503–505).
  The same note (`D_venkatapathy_2017_venus_edd.md`, l.23–24) gives that envelope **350–400 W/cm² and 7.5–10 kJ/cm²**.
  VESPER's numbers are **246 W/cm² and 3.9 kJ/cm²** (l.286). The doc never compares the heating.
- The team's own validation says heating is "possibly 30 % low for small cones" (l.341–343). VESPER is a 45° cone.
- The comparison point the doc cites is β ≈ 30, γ ≈ −10° at V 11.5 km/s and r_n 2.5 m (Dutta Fig. 1, 250–350 W/cm²,
  l.351–352).
  - Rough scaling, my own and not checked: Sutton–Graves goes as √(1/r_n)·V³. With r_n 0.93 m and V 10.78 km/s this
    gives ~1.3–1.6× **more**, not less.
  - The 18 W/cm² radiative term is extrapolated outside its fit (l.286).
- No TPS material is named anywhere. A grep for TPS, PICA, HEEET and phenolic finds nothing in the doc.
  - The heat-shield mass is a Landis fraction (13 % of 284 kg, `descent.LANDIS_FRACTIONS`), not a sizing.
  - The cited note says heritage carbon phenolic is "no longer viable".
  - β 25 is ADEPT (deployable) territory, but VESPER uses a **rigid** 3.7 m 45° cone. The doc does not show that a rigid
    shell fits in 284 kg.
- Two related weak points:
  - The 12 m main opens at Mach ~0.9 and 200 m/s, and "staged/reefed ≤ 5 g" is [Y] (l.365).
  - The abort column says "chute failure = loss".

**A good answer needs.** A TPS choice with an areal-mass estimate for 3.9–10 kJ/cm². Either a heating number
reconciled with ADEPT and Dutta, or a margin of ≥1.5× on heat flux. A rigid-aeroshell mass check, and the parachute
Mach/size choice justified against DAVINCI (1.8 m pilot at Mach 0.8, then a 5.8 m main).

**Already answered?** **Partly.** The g discrepancy is discussed. The heating discrepancy and the TPS are not.

---

## 4. You unfold 6 two-hinge arms, 12 folded blades and 6 solar petals on a bridle at 69 km, after 56 g. NASA Ames says mid-air deployment has only been shown for 2–4 folds. Where are the deployment kinematics, latch loads and stowed-structure stresses?

**Why it hurts.**
- The doc admits the precedent: "only been demonstrated for 2–4-fold aircraft" (l.243–244). It also calls folding and
  deployment the top open challenge (l.526–527).
- VESPER has 12 arm hinges, 12 blade folds, 6 petals, a bridle lowering and 6 spin-ups, which is 30+ deployment events
  (l.239–241, l.367–368). R1 is still the highest risk after mitigation (l.518).
- There is no structural check at the entry load. `structure.py` sizes arms only for "3° tilt under 1.6× thrust"
  (l.237–238). It has no entry or stowed load case, and nothing in `src/aerokit/venus/` mentions 56 g or 100 g except a
  risk-register string.
- The arms are 80 mm tubes at **0.8 mm minimum gauge** with a gearmotor can at the end. At 56 g each can (~0.55 kg)
  weighs ~300 N.
- "Qualify to 100 g" (l.446, l.509) is a test plan, not a margin.
- The stowed envelope comes from a 3-D model (1.57 × 2.12 m, l.241). It is not a packaging check against the inner
  mould line of a 45° cone plus backshell, a 12 m parachute and a bridle.

**A good answer needs.** A deployment sequence with timing and dynamics, including petal and blade unfolding in the
chute wake. Hinge/latch and stowed-support loads at 56 g with margins. A fault tree: what happens if one blade does not
unfold, which is not "an arm unlatched".

**Already answered?** **Partly.** The doc lists this as an open challenge and has an Earth-drop test plan (l.533–535).
It has no analysis.

---

## 5. (LuGus) You spin the rotors up "at flat pitch, no thrust on the bridle" while falling at 13–15 m/s. A flat-pitch rotor in a 15 m/s up-flow is a windmill. Where is the rotor aerodynamics of the hang-and-release phase?

**Why it hurts.**
- The sequence says "rotors spun up at flat pitch (no thrust on the bridle)" at ~63 km (l.368; `design.py` step 7:
  "flat collective (no thrust on the bridle)").
- The model does not represent the rotor in that up-flow at all:
  - `descent.deploy` and `deployment_monte_carlo` model thrust as a **pure time ramp** from 1.0 W to 1.6 W
    (`thrust = W*(1+(margin−1)*min(t/ramp,1))`), with no dependence on inflow.
  - Vortex-ring state is a flat "thrust ×0.8 (helicopter practice, [Y])".
  - `bemt.solve` does not support descent: for negative climb it sets `base = max(λ_c, 0)`.
- My blade-element estimate (`probe.py`, the team's rotor and polar at θ₇₅ = 0, with windmill-state momentum):

  | Altitude | Descent | Thrust, all 6 rotors | Share of weight | Shaft torque per rotor |
  |---|---:|---:|---:|---:|
  | 63 km | 15.0 m/s | ~290 N | ~75 % | −6 to −7 N·m |
  | 61 km | 12.8 m/s | ~360 N | ~95 % | −6 to −7 N·m |

  The negative torque means the air drives the rotors. So the bridle unloads, and the rotors autorotate instead of
  needing ~2.3 s of motor spin-up. Caveat: this is my own crude estimate, and the post-stall polar is the team's [Y].
- The two headline deployment results are therefore outputs of [Y] ramps, not of rotor physics:
  - "26 m lost vs 559 m" (l.290);
  - "forward flight never enters VRS" (l.382–384). Forward and vertical pull-outs differ only by the 20 % [Y] cut
    (27 m vs 30 m median).

**A good answer needs.** A collective schedule for the hanging phase. Zero thrust needs roughly −15° at 0.75 R; is that
inside the pitch range? Motor braking/regeneration torque, and a check that the slack bridle cannot let the rotorcraft
rise into the backshell or canopy. A pull-out model whose thrust depends on inflow, which is exactly what the LuGus
simulator will need.

**Already answered?** **No.** The doc presents these numbers as [K] results.

---

## 6. Your acid margin is "FEP 168 h / 49 h = 3.4×". But the parts that fail are CFRP under a film wrap, PTFE shaft seals, articulating PFA-coated Ti hinges and pitch linkages. What is their tested exposure?

**Why it hurts.**
- The margin table (l.447) and F15 report the acid margin for the **best** material (FEP coupons) as the vehicle
  margin.
- The doc itself says "no data found for CFRP in concentrated acid … that wrap is a qualification item" (l.202–203).
  It lists "CFRP + FEP in concentrated acid for days" and "sealed motor-gearbox cans (lubrication, seal life) in acid
  aerosol" as open challenges (l.528–529).
- `materials.selection()` uses a "PTFE shaft seal" on a rotating shaft, and "Ti hinges PFA-coated" for hinges that must
  articulate at deployment.
- Bare Ti is "75 % RT 10.8 mm/y" (`materials.py`). The cloud is 75–90 wt%.
- The FEP wrap also faces 70 m/s droplet impact at the blade tips, and hinge lines where films crease.
- The two statements contradict each other: a 3.4× margin in §6.2 and an open challenge in §7.

**A good answer needs.** Either remove the row from the margin table, or replace it with the weakest-link item marked
"untested". A short argument on exposure: what dose of droplets the blades sweep through in 49 h. A seal concept (for
example a magnetic coupling through a hermetic can, with no dynamic seal) and coupon tests on wrapped CFRP at the hinge
and fold lines.

**Already answered?** **Partly.** The gap is admitted in §4.5 and §7, but the margin table hides it.

---

## 7. What happens if a VEGA-2-class downdraft (−3 m/s for ~2 h) hits during your 51 km science dive? Riding it takes you to ~48 km, where the battery passes 60 °C. Fighting it needs ~2.5 kW, more than the array gives at that hour.

**Why it hurts.**
- The doc says "ride it within 51–58 km" (l.221), and "any dive to 48 km passes 60 °C" (l.210). The dive headroom is
  already "1.13× — thinnest above 1" (l.451).
- The two policies collide when the downdraft starts at the bottom of a dive. With the team's code (`probe.py`), first
  dive at hour angle ≈ −37°, at 51 km:

  | Item | Power |
  |---|---:|
  | Loiter | 1076 W |
  | Holding altitude against 3 m/s | ~2500 W |
  | Array output at that hour | 1428 W |

  The 1.07 kW deficit drains the 1.04 kWh battery in under 1 h, against an event that lasts ~2 h. The battery is near
  57 °C and cannot charge above 45 °C.
- At 55 km just after release (hour angle −51°), holding needs 2.76 kW against an array output of 1.44 kW.
- The convective layer (51–56 km) is where VEGA saw these events (l.104–106). The doc only simulates them separately
  (dive alone, downdraft alone).

**A good answer needs.** A combined-case simulation: dive plus downdraft, at the early-morning and late-evening sun.
Dive rules such as "no dive unless the array ≥ X", "dive floor 52 km" or "abort upward at the first sign of a
downdraft". If the thermal margin is the binding one, a PCM or a higher dive floor.

**Already answered?** **No.** Each hazard is answered alone; the compound case is not.

---

## 8. Your F4 mass budget has no line for the six collective-pitch actuators you rely on for attitude control, nor for blade-fold hinges or petal mechanisms. With a growth factor of ~2.5 kg per kg, what is the real mass?

**Why it hurts.**
- The doc relies on "Per-rotor collective-pitch actuators for attitude control" (l.177–181). `design.py` labels the
  component "6 folding 2-blade rotors + 5:1 geared motors + **collective actuators**". Its mass, however, is
  `blades+hubs + motors + ESCs` only.
- `sizing.MassModel` has no actuator, pitch-bearing, blade-fold or petal-hinge term:
  - hub 0.12 kg per rotor;
  - `fold_hinge` 0.15 kg × 2 per arm, for the arm hinges only;
  - `attach` 0.8 kg for the bridle and pyros.
- The full printed breakdown (`probe.py`): blades+hubs 2.54, motors 3.33, ESCs 0.22, arms+hinges 7.66, solar 4.01,
  battery 6.74, vessel 3.15, thermal 0.88, avionics 1.2, comms 0.8, attach 0.8, payload 3.0, wiring 1.37, coating 0.69,
  contingency 7.28 = 43.66 kg.
- Growth factor from `sensitivity.json`: payload 3 → 5 kg moves gross mass 43.66 → 48.62 kg, so ~2.5 kg per kg.
- The doc already says the design sits near a cliff: a 1 h reserve "does not close" (l.191–192, l.499–502).
- The top-down cross-check is already 25–42 % lighter (l.551), and is explained away (l.560–566). Missing mechanisms
  push the other way.

**A good answer needs.** Mass lines for the actuators (6 sealed acid-proof units), the pitch bearings, 12 blade-fold
hinges and the petal mechanisms, then a re-closure. Or an explicit statement that these sit inside the 20 % contingency,
with how much of the contingency they use.

**Already answered?** **No.**

---

## 9. "How does it get there": who carries it, on what launcher, and how is the relay orbit reached? Your link budget assumes an overhead pass every 1.8 h, which only happens in a near-equatorial orbit you never specify.

**Why it hurts.**
- The carrier is the relay orbiter, but "capture into the 1000 km relay orbit would need ~3.4 km/s if propulsive …
  (open item)" (l.283).
- The doc gives no launch vehicle, no carrier mass and no launch mass. These are left as a mentor question (l.603–604).
- The data-volume claims (~330 Mbit per pass, "a 13-minute pass every ~1.8 h", l.230–231 and l.419) come from
  `link.pass_duration`, which assumes an **overhead** pass on every orbit. The code models no orbit inclination.
- My geometry, not modelled by the team: in a polar relay orbit, a vehicle drifting near the equator sits under the
  ±21° visibility band only ~24 % of the time, in ~1.6-day stretches. A 49 h mission could get almost no passes.
- Question 3 of the brief is answered mostly by the entry-to-release sequence.

**A good answer needs.** A mission-architecture line: launcher class, wet mass of the carrier with ~3.4 km/s (or an
aerobraking time), and the relay orbit inclination with a pass schedule over the 49 h. Or a flyby-carrier relay (as
DAVINCI uses) with its contact-time limits, or a direct-to-Earth fallback rate.

**Already answered?** **Partly.** The capture ΔV is stated and flagged open. The orbit geometry and launch mass are not.

---

## 10. You chose a hexacopter for motor-out tolerance and abort only at "≤ 4 healthy". Have you shown that an alternating-spin (PNPNPN) hex with one rotor dead is controllable in yaw, roll and pitch with your 60 % margin?

**Why it hurts.**
- The configuration table rejects the quad for "no motor-out tolerance" and picks the hex as "motor-out tolerant"
  (l.137–138).
- The abort logic says "5 of 6 flies: hex motor-out tolerance" (l.368), and the arms use "alternating spin" (l.256).
- The only motor-out modelling is `deployment_monte_carlo`, which multiplies the thrust margin by 5/6. There is no
  trim, controllability or power analysis with a rotor out.
- From memory, not checked in this session: Du, Quan & Cai (2015, *JGCD*) showed that the standard PNPNPN hexacopter
  is not fully controllable after certain single-rotor failures when thrust is limited to positive values.
  - VESPER's variable pitch could allow reverse thrust and fix this, but the doc does not argue it.
  - Losing one rotor's 5.1 N·m reaction torque must be trimmed by the others while they also carry 6/5 of the
    disk loading.
- R6 and the flap-dynamics risks use the same unvalidated control assumptions.

**A good answer needs.** A one-rotor-out trim: rotor thrusts and collectives, yaw balance and power, at 55 km and at
release. Either show it closes inside the 1.6× motor sizing, or change the spin pattern / abort rule. This is a natural
LuGus simulator test case.

**Already answered?** **No.** The doc asserts tolerance; it does not show it.

---

## Also noticed (lower impact, would cost credibility if asked)

- **Release time contradiction.** The mission releases at hour angle −51° in the morning, 16.6 h after dawn
  (l.195–196, l.426). Risk R2's mitigation says "release near noon" (l.519; `risk.py` R2). Releasing at noon would
  roughly halve the sunlit window.
- **Unexplained flight-time gap.** The hand flight time (46.5 h) differs from the simulated 49.2 h by 2.7 h "I have not
  split" (l.568–569). The 49 h headline is not independently reproduced.
- **Unvalidated BEMT inputs.** The BEMT validation airfoil (NACA 0015, Earth) is not the VESPER polar: cambered, with
  cl_max 1.3, all [Y] in `sizing.VENUS_AIRFOIL`. The hover-power bracket of −20…+11 % (l.550) is the honest
  uncertainty band.

## What I verified and what is my reading only

**Verified in code, output files or notes this session:**
- Bifaciality 0.85 [Y] and the 42 % rear share: `power.py`.
- No bifaciality case: `sensitivity.json`.
- Landis assumes no upwelling light: `D_landis_haag_2013_solar.md`.
- ADEPT 350–400 W/cm², 7.5–10 kJ/cm²: `D_venkatapathy_2017_venus_edd.md`.
- No TPS material named anywhere: grep.
- The aerobot's 52–62 km range and 117-day goal: `B_izraelevitz2025_aerobot.md`.
- Pull-out thrust is a time ramp, VRS is a flat ×0.8 [Y], and BEMT has no descent branch: `descent.py`, `bemt.py`.
- No actuator mass term: `sizing.py`, `design.py`.
- `materials.selection()` PTFE shaft seal: `materials.py`.
- Overhead-pass-only link geometry: `link.py`.
- Motor-out handled only as a 5/6 margin: `descent.py`; grep.
- No entry-g structural case: grep of `src/aerokit/venus/`.
- Bifaciality sweep, flat-pitch thrust and torque, and the dive-plus-downdraft power balance: my runs of the team's own
  functions (`D:\tmp_ideathon\venus\r5\probe.py`).

**My reading or domain knowledge, not checked in this session:**
- Space triple-junction cells being opaque-backed (Q1).
- The Sutton–Graves scaling of Dutta's contour to VESPER's nose radius and speed (Q3).
- The blade-element windmill estimate (Q5). It is my own model on the team's [Y] polar; the order of magnitude is
  robust, the exact numbers are not.
- The polar-orbit visibility fraction (Q9).
- The Du/Quan/Cai hexacopter controllability result (Q10), from memory.

No repo file was edited, created or deleted.
