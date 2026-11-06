# Notes for the report writer

From the technical session, 6 Nov 2026. Current facts: `cases/case_10_par_hybrid_cue/TECHNICAL.md`, `outputs/result.md`,
`outputs/validation.json`. Do not take numbers from `03_Advionics/complex/`: that is the earlier, fuller version.

## 1. Style

Use plain English in the spirit of ASD-STE100. Do not write that the text complies with ASD-STE100. Use the `articlecraft`
skill (`references/ste-inspired-clarity.md`) and run `scripts/article_lint.py` on the draft.

- One term for one concept. Use the term list below.
- At most about 25 words in a sentence. One idea in a sentence.
- Active voice. Put the condition before the action.
- Say each fact once. A caption gives the claim. The body does not repeat it.
- No circular text: no "as mentioned", "in summary", "this section describes".
- State what we did and what we found. Do not sell.

| Use | Do not use |
|---|---|
| cue | guidance system, assistant |
| missed approach | go-around (except when quoting a dataset label) |
| decision height (DH) | minimums |
| glidepath | glide path, glide slope (except ILS) |
| radar plot | measurement, sample |
| recorded track | real landing, as a test item |
| replay | flight test, trial |
| limit | threshold, for safety limits |

## 2. Claims to change in main.tex

1. **Line 133, caption.** Delete "so it is on the safe side". Wider scatter does not show that the simulation is conservative.
   The real aircraft flew ILS and the simulated aircraft flew the cue. Write: "Simulated scatter is wider than real scatter."
2. **Line 127.** Write "1000 recorded tracks", not "1000 real landings". Add that these are the first 1000 tracks that passed our
   filter, not a random sample.
3. **Line 144.** "Open loop" needs a plain sentence: "The aircraft did not react to the cue. No pilot saw it." 275 of the 1000
   tracks ended before DH.
4. **Line 147.** Add that the closure flag was tuned on the first 300 of these tracks and on the Smolensk track. So "fires on 6"
   is not an independent result. Use the independent result instead: on 2000 further tracks not used for tuning, 1959 stayed quiet,
   98.0 % had no guidance voice, and the flag fired on 10 (`outputs/validation_holdout.json`).
5. **Lines 152–156, Smolensk.**
   - Write "the one event we found", not "the one public event".
   - Use the conditional: "Our limit call would have come 88.5 s before it."
   - Say that the track comes from 13 report points.
   - Add: "If the radar itself was wrong, as the report suspects, the cue would inherit the error."
   - Do not write or imply that the cue would have prevented the accident.
6. **Line 221.** Write "a replay of 1000 recorded tracks", not "a check on 1000 real landings".
7. **Line 221, novelty.** The flight path marker and a guidance cue on a head-up display are existing ideas. Do not claim the ring as a
   new symbol. Our work is the logic behind it: FAA fault rules, a silent path and a voice that yields to aircraft alerts.
   Say why: "We use symbols that pilots already know."
8. **The ring.** The marker comes from aircraft sensors, not from the radar. A radar-derived rate is too noisy. An aircraft with no
   flight path marker cannot use the ring. It can use the needles, the heading and the words. Say this once.

## 3. Facts to keep exact

- **Missed approach.** Conditions: limits exceeded, position in doubt, radar contact lost or malfunction suspected. Form: the
  reason, then "if runway or approach lights not in sight, execute missed approach". None of these applies after DH.
- **Lost link.** Five seconds of silence is not a missed approach. The pilot applies the lost communications instruction.
- **Limit values.** ±0.5° and ±2° are not FAA values. The FAA prints no number. They come from one report, and a real system takes
  them per runway.
- **Timers.** 3 s and 4 NM are UK values (RA 3291). 5 s is ICAO's longest silence and the FAA lost communications interval.
- **FAA source.** The FAA site refused automated reading. We read a third-party copy of JO 7110.65BB dated 1-22-26. Say so once, in
  the references or limits.
- **Levels.** Quiet below 1 dot, advise at 1 dot, caution at 1.3 dots, warning in a missed approach state. There is no level 1.
- **Voice priority.** Three rules. An aircraft alert sounding: the cue is silent, and a warning waits. A transmission on: a routine
  call is dropped. The display never waits.
- **Removed from the design.** Gear prompt, tower clearance gate, CUE QUIET, NOT CORRECTING. Do not describe them as features.
  They may appear under next steps.

## 4. Model limits to state once

Pilot and aircraft are simple models. Reaction time on a PAR call has no source; 2 s is an analogy from EGPWS response. Multipath and
noise correlation are assumed. No measured PAR data was found.
