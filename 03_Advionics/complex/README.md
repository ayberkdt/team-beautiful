# complex — full version, kept to one side

The brief says "Keep it simple". These parts were taken out of the main system on 6 Nov 2026. Nothing was lost: this folder
holds the full code, its tests, its note and its results. It is not part of the build or the test run. The mock-up scene
is separate and did not change.

| Taken out | Why it can wait | Where |
|---|---|---|
| Intensity formula (height weight, trend term, above-path factor) | A table gives the same result; see below | `src/cue_intensity.py` |
| Sound ladder +5, +11, +15 dB | Not measured in a cockpit | same |
| CUE QUIET button | Not used in the demo. Good idea for "next step" | same |
| Same-meaning filter and hold timers | Three rules are enough | `src/voice_arbiter.py` |
| NOT CORRECTING word | Not primary | `src/parcue.py` |
| Gear prompt, tower clearance gate, tower break | The system does not know gear state or clearance | same |
| Pilot proceeds visually (5-12-8a4), missed approach text | Needs pilot input | same |
| x1.5 band for target changes on the path | No effect on the standing offset | same |

**Effect of taking them out, 1000 real Zurich landings:** quiet approaches 907 → 985, approaches with no guidance voice 97.8 % →
98.5 %. Smolensk "coming down rapidly": 170 → 167 of 200. The formula gained nothing measurable. Full numbers:
`result_full.md`, `validation_full.json`, `TECHNICAL_full.md`.

To restore: copy `src/*.py` to `src/aerokit/atc/` and `tests/*.py` to `tests/`.
