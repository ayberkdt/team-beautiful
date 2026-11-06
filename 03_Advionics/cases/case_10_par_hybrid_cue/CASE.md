# Case 10 — Official task: radar → correction → pilot cue (HYBRID)

**Task:** `official_2026-11-06/Advionics_challenge.pdf`. Replace the PAR controller. This case is the answer; cases 1–9
are pre-reveal preparation.

**Concept (5 lines)**
1. PAR plots at 1 Hz go through an alpha-beta filter with a gate. A plot far from the prediction is rejected.
2. Heading target = course + offset term + slow wind trim. Descent target = nominal for the ground speed + height term.
   Position only: a rate from 1 Hz PAR plots is too noisy (two rate-based laws failed, 0 of 100 runs reached minimums).
3. Needles move with every plot. Targets change in display steps, at most every 5 s. Pilot holds the last target.
4. Voice only for important changes: off-path corrections, on path, data faults, minimums.
5. Delayed: old needle, marked, no new target. Invalid: needles removed. Lost, outside limits: go around, latched.

**Numbers:** see `outputs/result.md`.

**Demo:** `outputs/par_cue_demo.html` (offline, voices inlined). Scenarios A return to path, B delayed and invalid data,
C guidance lost. Replay runs at 2× real time.

**Limits:** pilot and aircraft are simple models; no real pilot has used the display; gains are design values; small
jumps below the gate are not detected at long range; about 5 s has no primary source; go-around on LOST is our rule;
the link from the ground to the cockpit is assumed. Educational concept, not approved or ready for flight use.

**Run:** `python 03_Advionics/cases/case_10_par_hybrid_cue/run.py [--set crosswind_ms=5]` · code `aerokit.atc.parcue`,
tests `tests/test_atc_parcue.py`.
