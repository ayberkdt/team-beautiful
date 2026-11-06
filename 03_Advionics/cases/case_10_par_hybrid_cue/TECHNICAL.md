# Technical note — radar to pilot cue

The short version, for the report. The full version is in `03_Advionics/complex/`. Sources: `research/R2` to `R6`. Numbers:
`outputs/result.md`, `outputs/validation.json`. Simulated and recorded data only. Not approved or ready for flight use.

## 1. How it works

Radar plot → filter → heading and glidepath information → pilot.

1. **Radar.** One plot per second. Errors follow ICAO Annex 10.
2. **Filter.** A Kalman filter per axis smooths the plots. A plot far from the prediction is rejected.
3. **Azimuth: a heading.** ICAO says the pilot does not correct in azimuth unless told. The heading aims to remove the offset in
   about 20 s. A slow trim follows the wind. It changes at most every 5 s.
4. **Elevation: information.** ICAO says the pilot corrects in elevation from the information alone. The system shows position,
   trend and a rate of descent. There are no turn or descend commands.
5. **Words.** FAA words: ON GLIDEPATH, SLIGHTLY ABOVE GLIDEPATH, WELL LEFT OF COURSE, COMING DOWN, HOLDING.

The law uses position only. Three designs that used a radar-derived rate failed: 0 of 100 runs reached decision height. A rate
from 1 Hz PAR plots is too noisy. A controller does the same: give a heading, watch the position, adjust.

## 2. How loud the cue is

The pilot flies. On the path the system is silent, as real alert systems are.

| Deviation | Display | Voice | Anchor |
|---|---|---|---|
| Below 1 dot | Needles | None | Silent on the path |
| 1 dot | Note | "Slightly …", once | FSF stable approach limit |
| 1.3 dots | Caution | "Well …", once | EGPWS Mode 5 soft alert |
| Missed approach state | Warning | Reason and condition, twice at most | JO 7110.65 5-10-14 |

A call repeats only for 20 % more deviation (EGPWS rule). What the radar cannot resolve is not alerted. A heartbeat on the display
shows that guidance is alive. Silence is safe only while it runs.

## 3. When data goes wrong

- **Delayed:** told after 3 s. Needles stay, marked old. No new heading.
- **Invalid:** the needle of that axis is removed. Good plots restore it.
- **Radar contact lost or suspected:** after 3 s inside 4 NM, 5 s outside. Latched.
- **Elevation failed:** at once.
- **Guidance link lost for 5 s:** this is not a missed approach. The pilot applies the lost communications instruction.

No valid data, no new guidance, no extrapolation.

## 4. Missed approach (FAA JO 7110.65BB 5-10-14)

**When:** safety limits exceeded, or radar contact lost or suspected, or elevation failed. **Never after decision height.**

**How:** the reason, then the condition. "Too low for safe approach. If runway or approach lights not in sight, execute missed
approach." The pilot decides.

Below decision height, position stays on as advisory only until the threshold (5-12-7).

The limits ±0.5° and ±2° come from one published set. The FAA prints no number. A real system takes them per runway.

## 5. Voice priority

The cue ranks below every line of the aircraft alert list (TSO-C151c Table 4-2). Three rules:

1. An aircraft alert (PULL UP, TERRAIN, TCAS RA, GLIDESLOPE) is sounding: the cue is silent. A warning waits until the alert ends.
2. A radio transmission is on: a routine call is dropped. A warning does not wait.
3. The display never waits.

## 6. Evidence

**Zurich: 1000 real landings.** The first version raised a false caution on 43 % of normal approaches. Simulation had not shown
this. Real data found it.

**Smolensk 2010: a real radar talk-down.** The radio said "on course, on glide path" five times, outside limits. The first
correction came 5.5 s before the first strike. Deviations and calls only; no finding on blame.

**PAR accuracy limits what the approach can achieve.** With a radar twice as good, more runs reach decision height. A standing
offset of about 25 m stays inside ON COURSE and near radar noise.

## 7. Limits

- No real pilot has flown the cue. We do not claim lower workload. Radar to needle is not new (ACLS Mode II).
- Pilot and aircraft are simple models. Multipath and noise correlation are assumed.
- Zurich approaches were flown on ILS, not PAR. ADS-B is not truth.
- A plausible wrong plot passes the gate. Small jumps far out are not caught.
- The ground-to-cockpit link is assumed.
- The FAA page refused automated reading. The text is a third-party copy of JO 7110.65BB, dated 1-22-26.
- Out of scope, kept in `complex/`: gear prompt, tower clearance, proceed visually.

## 8. Final numbers

Simulation, 100 runs, C-130H, light turbulence, 3 m/s crosswind:

- 99 of 100 reach decision height; with no cue, 1 of 100.
- 95 % error at decision height: 37 m lateral, 11 m vertical.
- Radar twice as good: 100 of 100. Reaction 4 s: 95. Moderate turbulence: 77.
- 0 frames show guidance without valid data.

Zurich, 1000 real landings on RWY 14, open loop:

- 985 stay fully quiet. 5 reach "slightly", 4 "well", 6 a missed approach state.
- 98.5 % have no guidance voice.
- 22 labelled go-arounds could be cut out of the data. The cue spoke before the climb in 11, median 15 s. Others may be for
  traffic or weather, with no deviation.

Zurich, 2000 further tracks, not used for any tuning:

- 1959 stay fully quiet. 13 reach "slightly", 4 "well", 24 a missed approach state.
- 98.0 % have no guidance voice. The closure flag fires on 10 tracks (0.5 %).
- We did not check whether the missed approach states were real excursions.

Smolensk, 200 noisy runs:

- Limit call in 200 of 200, median 88.5 s before the first strike. The real first correction came 5.5 s before.
- With the limit switched off, "Coming down rapidly" in 167 of 200, median 16.5 s before.
