# 03_Advionics — Automated Precision Approach Guidance

**Task (6 Nov 2026):** replace the PAR controller. Radar data in, heading and glide-slope corrections out, a clear cue
to the pilot. Weights: clarity 30 %, technical logic 25 %, demonstration 25 %, safety awareness 20 %.

**Our answer: HYBRID.** Needles, FAA position words and a heading target on a display, updated with every radar plot. Voice
only when it matters, and below every aircraft alert. Faults follow FAA JO 7110.65. Replayed open loop on 1000 recorded tracks and one
real radar talk-down; no pilot has flown it. Educational concept on simulated and recorded data. Not approved or ready for flight use.

**Open the demo:** `cases/case_10_par_hybrid_cue/outputs/par_cue_demo.html` (offline, voices inside).

| Folder | What |
|---|---|
| `official_2026-11-06/` | task PDF, `00_OFFICIAL_TASK_vs_KIT.md` (what the task asks, what changed) |
| `cases/case_10_par_hybrid_cue/` | **the solution:** runner, results, figure, demo |
| `cases/case_4_par_talkdown/` | reference: the human talk-down we replace |
| `cases/case_9_guidance_uplink/` | reference: a data link from the ground to the cockpit, timeout trade-off |
| `templates/par_cue.html` | demo page source; the runner fills it |
| `research/` | `R2` PAR, `R3` controller and pilot workload catalogue, `R4` cue intensity, `R5` real data and models, `R6` FAA rules; sponsor sources |
| `submission/latex/` | report starter |
| `complex/` | the fuller version, kept to one side: formula, extra rules, their tests and results |

Code in `src/aerokit/atc/`: `parcue.py` (logic), `parradar.py` (radar), `parflight.py` (flight), `cue_intensity.py` (alert
level), `voice_arbiter.py` (voice priority). Tests: `tests/test_atc_parcue.py`, `test_atc_cue_intensity.py`,
`test_atc_voice_arbiter.py`.

Run from the project root:

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
python 03_Advionics/cases/case_10_par_hybrid_cue/run.py
```

Preview server `atc-demo` (`.claude/launch.json`) serves this folder.

Everything prepared before the task was known (voice-to-display, lost comms, radar decoding, doc 24, its research and
tests of those parts) is in `prev_guess/03_Advionics/comms_kit_2026-11-05/`.
