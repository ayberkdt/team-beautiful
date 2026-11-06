# Technical note — radar to pilot cue

Numbers: `outputs/result.md` (simulation, 100 seeds) and `outputs/validation.json` (real tracks), 6 Nov 2026. Code:
`src/aerokit/atc/` `parcue.py`, `parradar.py`, `parflight.py`, `cue_intensity.py`, `voice_arbiter.py`. Sources: `research/R2`
to `R6`. Tags: [K] computed here, [Y] our design value. Simulated and recorded data only. Not approved or ready for flight
use.

## 1. Chain

Radar plot (1 Hz) → filter and gate → heading target and glidepath information → alert level → voice arbiter → pilot.

The two axes are not treated alike, as in ICAO Doc 4444 8.9.7.2.4-5. In azimuth the pilot does not correct unless told, so
the output is a **heading**. In elevation the pilot corrects from the information alone, so the output is **position, trend
and an advisory rate of descent**. There are no turn or descend commands.

1. **Radar model.** Antenna set back 915 m, offset 120 m. Errors from Annex 10: azimuth max(0.6 % R + 10 % of deviation, 9 m),
   elevation max(0.4 % R + 10 %, 6 m), R from the antenna; distance 30 m plus 3 %. 1 sigma = limit / 2 [Y]. Half the
   variance is correlated over 5 s [Y]. Elevation multipath 0.05° [Y]. Plot detection 95 %, tested at 90 %.
2. **Filter.** One constant-velocity Kalman filter per axis, noise from the radar model at that range. A plot is rejected
   above 5 sigma on the innovation [Y]. The gate widens after each rejection, so noise cannot lock it out.
3. **Heading target.** Last known heading + offset term + slow trim. Offset term: remove the offset in 20 s, shorter near the
   runway. Limited to 10° beyond 3 NM, 5° inside. Changes at most every 5 s; at least 4° beyond 3 NM, 2° inside.
4. **Rate of descent.** 101.3 × GS × tan(angle) plus a height term, within about 1° of pitch.
5. **Words.** JO 7110.65BB 5-12-4: ON GLIDEPATH, ON COURSE, SLIGHTLY/WELL ABOVE/BELOW GLIDEPATH, SLIGHTLY/WELL LEFT/RIGHT OF
   COURSE. Trends: GOING, COMING DOWN/UP, CORRECTING, HOLDING, RAPIDLY. "On" is a third of the limit (Smolensk report); FAA and
   ICAO give no numbers.

## 2. Why this law

Three designs that used a radar-derived rate failed in closed loop [K]: a continuous correction (0 of 100 reached minimums), the
same in steps (0 of 100), and a drift estimate from a 10 s track (2–3° of noise at 5 NM). A rate from 1 Hz PAR plots is too
noisy for control. A controller avoids this the same way: give a heading, watch the position, adjust. The controller also knows
the heading last assigned, so the start heading is an input.

A rate is still used for **words and one alert**, never for targets.

## 3. What happens when data goes wrong

- **DELAYED.** Plot age above 3 s, outside 4 NM. Told at once (RA 3291 para 5). Needles stay, marked old. No new target.
- **INVALID.** 2 plots rejected in a row. Needle of that axis removed. 3 good plots restore it. Short only: the timers below
  still run.
- **RADAR LOST / RADAR SUSPECT.** No accepted plot for over 3 s inside 4 NM (RA 3291 para 7b), or over 5 s outside it (Doc 4444
  8.9.7.2.3). SUSPECT if plots arrive and are all rejected or too old. Latched. Missed approach call, section 4.
- **ELEVATION FAILED.** 2 frames with the elevation flag down. At once, with no wait (JO 7110.65 5-12-10). Latched.
- **LINK LOST.** No message for 5 s. This is **not** a missed approach. The pilot applies the instruction given before final:
  try the secondary frequency, proceed VFR if able, or fly the non-radar approach or lost communications procedure (5-10-4).
- **Below DH.** A fault removes the needle and makes no call.

Rule: no valid data, no new guidance, no extrapolation. 0 frames broke this in all fault runs [K].

## 4. Missed approach: when and how (JO 7110.65BB 5-10-14)

Full text in `research/R6_faa_jo7110_65bb_par_rules.md`.

- **When:** safety limits exceeded; position in doubt; radar contact lost or malfunction suspected. **Never after DH.**
- **How:** the reason, then the condition. "Too low for safe approach. If runway or approach lights not in sight, execute
  missed approach." The pilot decides; a pilot who sees the lights continues. Other reasons: too high, too far left, too far
  right, radar contact lost, radar malfunction suspected, no glidepath information available.
- **Unconditional only for tower or traffic** (5-10-14d, 5-10-13): "Tower clearance not received. Execute missed approach."
  The 2 NM point is Doc 4444 8.9.6.1.8a.
- **Limits:** outside and staying outside for 3 s (AIM 5-4-11), on deviation minus 1 sigma of radar error. FAA prints no number.
  ±0.5° and ±2° are defaults from one published set (Smolensk report p. 257); a real system takes them per runway.
- **Procedure:** given before final (5-10-11), shown beside the call.
- **Guidance ends:** over the threshold, or when the pilot reports lights and proceeds visually (5-12-8). Below DH it is
  labelled advisory only (5-12-7).

## 5. Intensity: staying out of the way of an experienced pilot

Real systems are silent on the path. EGPWS Mode 5 starts at 1.3 dots below 1000 ft at about −6 dB, says one word, and repeats
only for 20 % more deviation. A correct alert about something already being fixed is still a nuisance. So:

- I = clip(H·(e − 0.5)/1.5 + G, 0, 1). e is the larger axis in alert dots, after removing what the radar cannot resolve. Low
  counts more than high (Mode 5 has no above-beam alert). G is ±0.10 from position trend over 5 s. H is 0.7 above 1500 ft, 1 below 1000 ft.
- L0 quiet: needles only. L1 note. L2 advise, about 1 dot (ALAR limit). L3 caution, about 1.3 dots (Mode 5). L4 warning: missed
  approach states.
- Voice level: noise + 5, + 11, + 15 dB, never above 90 dB(A). Loudness has only a few dB to use, since radio voice sits at
  84–88 dB(A). Intensity comes from fewer calls and from words.
- Repeat only for 20 % growth. Gaps 10 s, 5 s, 8 s. L4 twice at most. No L2 voice below 300 ft. No voice on the path, ever.
- One button, CUE QUIET: no L2 or L3 voice. L4 cannot be silenced.
- **A live heartbeat replaces the 5 s voice stream.** To a PAR pilot, 5 s of silence means lost communications, so silence is
  only safe while the heartbeat runs. This departs from 5-12-4a and needs a pilot trial.

Weights and level limits are ours [Y]; anchors are sourced. No pilot has tested them.

## 6. Voice priority: GPWS, PULL UP, TCAS, radio

Rules: one aural alert at a time; a higher alert may cut a lower one (AC 25.1322-1 8.b); a new system must not interfere with
alerting (6.e(3)). The list is TSO-C151c Table 4-2: windshear 1, sink rate pull up 2, closure pull up 3, terrain 4, ..., minimums
10, ..., sink rate 17, don't sink 18, glideslope 19, ..., bank angle 22. TCAS is inhibited while those sound.

Our cue is an add-on, so it ranks below every line of that table [Y].

- **Aircraft warning sounding (PULL UP, TERRAIN, WINDSHEAR, TCAS RA):** our voice is silent. A routine call is dropped. A level 4
  call waits and plays after it, up to 10 s; after that the display alone carries it.
- **Aircraft caution sounding (SINK RATE, GLIDESLOPE, BANK ANGLE):** the same.
- **Same meaning:** after GLIDESLOPE, "well below glidepath" is dropped for 15 s. After SINK RATE, "coming down rapidly". After
  MINIMUMS, "at decision height".
- **Radio:** routine calls wait for the end of the transmission, 3 s at most, then drop. Level 4 does not wait.
- **The display is never held.** The level and needles change at once whatever the voice does. In one study 8 of 14 pilots
  reported no alarm, so a critical call is never voice only.

Frames carry `voice_held` and `voice_dropped`. Scenario F shows this.

## 7. Validation on real data [K]

**Zurich, 1000 real landings on RWY 14** (MIT data; open loop; PAR error added on top; one height constant removed per flight):

- Real scatter: lateral 10 m at 5 NM to 4 m at 1 NM, close to Hall and Soares. Vertical 15 m to 5 m.
- Before tuning, 43 % of normal approaches raised a false caution, 171 of 174 in a 400-flight check from the closure flag.
  Simulation had not shown this. After tuning: 907 of 1000 stay at L0, 67 reach L1, 12 L2, 8 L3, 6 L4.
- At 90 % plot detection, 8 of 1000 end in a false RADAR LOST (4 misses in a row inside 4 NM).
- 22 of 66 labelled go-arounds could be cut out of this data. The cue spoke before the climb in 10, median 20 s. Others may be for
  traffic or weather, with no deviation.

**Smolensk 2010, a real radar talk-down** (report table, 13 points; deviations and calls only, no finding on blame). The radio
said "on course, on glide path" five times. The first correction came 5.5 s before the first strike.

- Our limit call: 200 of 200 noisy runs, median 88.5 s before.
- With the limit disabled, to test the low part: "Coming down rapidly" in 170 of 200 runs, median 16.5 s before.
- Tuning trade-off: the closure flag was tuned against both data sets. Tighter settings cost detections (200 → 170 of 200).
- If the radar itself is wrong, as the report suspects here, the cue inherits it. A plausible wrong plot passes the gate.

## 8. Simulation results [K]

- 98 of 100 reach DH. 95 % error at DH 32 m lateral, 11 m vertical. With no cue, 1 of 100. Median 1 voice call, 10 target changes.
- Radar twice as good: 100 of 100. **PAR accuracy limits what the approach can achieve.** Vertical scatter is near radar error.
- Reaction 4 s: 95. Moderate turbulence: 78. Detection 90 %: 96.
- Fault reaction, all 100 runs: delay told after 3 s; radar stop inside 4 NM after 3 s; jump after 1 s (90 of 100 in that scenario).

## 9. Where it stops working [K]

- **Small jumps.** Far out, 200 m is caught in 14 %, 300 m in 100 %. Near, 100 m in 10 %, 150 m in 92 %.
- **Offset and wind.** 300 m with 5 m/s gives 75 of 100; with 10 m/s, 38. 150 m with 10 m/s gives 77. 450 m at 5 NM is outside
  the limit: 0 of 100, the limit working as designed.
- **Moderate turbulence** 78 of 100.

## 10. Not shown

- No real pilot has flown the cue. Do not claim lower workload: one study found no difference between flight director and raw
  data. Radar to needle is not new either: ACLS Mode II is close.
- Pilot and aircraft are simple models. Reaction time on a PAR call has no source; 2 s is the EGPWS peak, by analogy.
- Multipath amplitude and noise correlation are assumed. No measured PAR data was found.
- Zurich approaches were flown on ILS, not PAR, and ADS-B is not truth.
- The ground-to-cockpit link is assumed. Case 9 covers its format and timeout.
- Current FAA page not read directly (403): the text is a third-party copy of JO 7110.65BB, 1-22-26. Limit values are not FAA.
- Not modelled: APPROACHING GLIDEPATH, BEGIN DESCENT, mile calls by voice, surveillance approach after elevation failure, and
  avoiding capture of both axes at once (RA 3291 para 28).

## 11. Data for other front ends

`outputs/replay_data.json`: scenarios A return to path, B delayed and invalid, C radar lost, D elevation failure, E link lost, F
aircraft alert. One frame per second. Keys: `t`, `s` state, `ld`/`vd` needle dots (null = removed; + right, + above), `hdg`,
`sink` advisory rate, `lw`/`vw` position words, `lt`/`vt` trend words, `lvl` level 0–4, `vis`, `blink`, `v` voice key, `dba`,
`tone`, `hb` heartbeat, `age`, `note`, `rn`, `hf`; truth `x`, `y`, `z`, `dz`. `chapters` and `end` give the story.
