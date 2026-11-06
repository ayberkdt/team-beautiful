# Technical note — radar to pilot cue

All numbers are from `outputs/result.md` (6 Nov 2026, 100 seeds unless stated). Code: `src/aerokit/atc/parcue.py`.
Tags: [K] computed, [Y] our design value, [A] search summary only. Simulated data only; not approved or ready for flight
use.

## 1. Chain

Radar plot (1 Hz) → filter and gate → targets → cue → pilot. A validity monitor runs beside the chain and can stop it.

1. **Input.** One plot per second: range, lateral deviation, vertical deviation, time of measurement, valid flag. Noise
   follows the PAR accuracy model in `atc.par.par_measure` (figures via ENRI; Annex 10 not read).
2. **Filter.** Alpha-beta per axis, α = 0.30, β = 0.04 [Y]. The rate only predicts the next plot.
3. **Gate.** Reject a plot further than 5σ from the prediction, not below 15 m [Y]. The gate widens by 50 % per rejected
   plot, so noise cannot lock the filter out.
4. **Targets.** Position only.
   - Heading target = course − atan(y / (GS·T)) + trim. Offset term limited to ±10°.
   - Trim integrates the same term with an 80 s time constant, limited to ±10°. It learns the wind: a radar sees no
     wind and no heading.
   - Descent target = GS·tan(γ) + z / T. Height term limited to ±2.5 m/s (about 500 ft/min).
   - T = 20 s, shortened to half the time to go near the runway, not below 8 s.
5. **Cue.** Needles move with every plot. Targets move in steps of 2° and 100 ft/min, at most every 5 s. On the path, a
   target needs twice the reason to change. Pilot holds the last target.
6. **Wording.** TURN and DESCEND MORE/LESS move towards the path. EASE and RESUME DESCENT end a correction, so a word
   never points away from the needle.
7. **Voice.** Only off the path by more than 0.5 dot, only towards the path, at least 4 s apart. Fault calls have no
   limit. Median 6 calls per approach [K].

## 2. Why this law

Two earlier laws failed in closed loop [K], and the reason is the main technical finding:

- Relative correction from filtered radar rate, continuous: 0 of 100 runs reached minimums.
- The same law in discrete steps: 0 of 100.

A rate derived from 1 Hz PAR plots is too noisy at 5 NM. A corrected aircraft oscillates and diverges. A controller
avoids this by the same method we now use: give a heading, watch the position, adjust.

## 3. Validity rules

- **DELAYED:** plot age above 2 s. Old needle stays, marked. No new target.
- **INVALID:** 2 rejected plots in a row, or valid flag false. Needles removed, flags shown. Hold last target. 3 good
  plots restore the cue.
- **LOST:** no accepted plot for over 5 s [A]. Needles removed. Go around. Latched: a radar that returns does not
  restart guidance.
- **OUTSIDE LIMITS:** at or beyond 2 dots, outside coverage or sector. Go around. Latched. Below 1000 m range the angle
  limit is off, because minimums come first.
- **MINIMUMS:** 200 ft. Guidance ends; pilot decides.

Rule: no valid data, no new guidance, no extrapolation. 0 frames broke this in all fault runs [K].

## 4. Results [K]

- **Closed loop:** 99 of 100 runs reach minimums. 95 % error there: 25 m lateral, 9 m vertical. With no cue: 0 of 100.
- **The 1 run that did not:** seed 4 is truly 17.6 m low at 1.5 km. OUTSIDE LIMITS is the correct call.
- **Pilot sensitivity:** reaction 3 s 97 of 100; slow response 98; heading held 3° off 99 (the trim removes it).
- **False alarms:** 0 DELAYED or INVALID frames in 100 clean runs.
- **Fault reaction:** delay shown after 2 s, jump after 1 s, radar stop after 5 s; same in all 100 runs.
- **Scenario B:** 98 of 100 reach minimums after both faults.

## 5. Where it stops working [K]

- **Small jumps far out.** At about 4 NM, a 100 m jump is caught in 26 % of runs, 150 m in 98 %. Near (about 1.7 NM),
  60 m is caught in 96 %. An uncaught jump pulls the cue. This is the main blind spot.
- **A caught fault still costs position.** Holding the last target during a correction moved the aircraft about 60 m at
  about 4 NM, against 13 m near.
- **Start offset.** 300 m works up to 5 m/s crosswind (99 of 100). With 10 m/s it drops to 12 of 100: wind carries the
  aircraft past 2 dots before the first correction. 450 m at 5 NM is 2.78°, outside the 2.5° full scale: 0 of 100,
  which is the limit working as designed.
- **Crosswind.** At 150 m offset, 10 m/s still gives 99 of 100, with 95 % lateral error up from 21 m to 39 m.

## 6. Not shown

- Pilot and aircraft are first-order models [Y]. No real pilot has flown the cue.
- Gains and thresholds are design values, tuned on this simulator only.
- Noise is white Gaussian. Multipath on the elevation axis is correlated and will be harder for the gate.
- The ground-to-cockpit link is assumed. Case 9 covers message format and timeout, not this closed loop.
- About 5 s for LOST has no primary source. Go-around on LOST is our rule.

## 7. Data for other front ends

`outputs/replay_data.json`: scenarios A, B, C, one frame per second. Keys: `t` time, `s` state, `ld`/`vd` needle dots
(null = removed; + right / + above), `hdg` heading target, `sink` descent target (ft/min), `lw`/`vw` command words, `age`
plot age, `v` voice key, `rn` range NM, `hf` height ft; truth `x`, `y`, `z`, `dz` (m). `chapters` and `end` give the story.
