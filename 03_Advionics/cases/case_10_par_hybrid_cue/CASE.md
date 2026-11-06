# Case 10 — Official task: radar → correction → pilot cue (HYBRID)

**Task:** `official_2026-11-06/Advionics_challenge.pdf`. Replace the PAR controller. This case is the answer. Cases 4 and 9
are reference.

**Concept (5 lines)**
1. Radar model and limits from Annex 10; wind, turbulence and aircraft from sourced models.
2. Azimuth by heading, elevation by information, as ICAO asks. Position only for control.
3. FAA words on the display, updated every second. A heartbeat shows guidance is alive.
4. Voice only when it matters; it gives way to GPWS, TCAS and the radio.
5. Faults follow JO 7110.65: reason, then "if lights not in sight, execute missed approach". None after DH.

**Read:** `TECHNICAL.md`. **Numbers:** `outputs/result.md`, `outputs/validation.json`.

**Data for the mock-up:** `outputs/replay_data.json`, six scenarios. Reference page: `outputs/par_cue_demo.html`.

**Run:** `python 03_Advionics/cases/case_10_par_hybrid_cue/run.py`. Real data:
`python -I 03_Advionics/cases/case_10_par_hybrid_cue/validate_real.py` (needs the two open datasets; see its docstring).
