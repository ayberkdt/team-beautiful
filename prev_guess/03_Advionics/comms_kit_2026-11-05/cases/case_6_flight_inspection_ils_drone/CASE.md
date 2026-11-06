# Case 6 — Drone flight inspection of an approach aid (SkyRF-style "Mini-Approach")

**Task wording that triggers it:** "flight inspection / flight check", "ILS / localizer / glide slope", "DDM", "drone
measures the signal in space", "PAPI", "commissioning", "pass or fail against tolerances". Sponsor fit: SkyRF drone
with automated Mini-Approach, LOC DDM uncertainty ≤ 0.02 % (S_intersoft_skyrf_brochure [D-ag]).

**Concept (5 lines)**
1. The drone flies a mini-approach with a lateral weave; truth reference = its RTK position, independent of the aid.
2. Inspection receiver: detected 90/150 Hz audio → depths → DDM, **validated first** (carrier, both tones, depth sum).
3. A fault (dead tone, no carrier) reads FLAG — never DDM 0 = "on course".
4. Acceptance statistic: mean (measured − reference) DDM with a 95 % interval vs the tolerance → PASS / FAIL.
5. The same receiver logic is the cockpit rule: a lost signal must never look like a good one.

**Three numbers** (`outputs/result.md`)
- Course alignment: measured **+0.00399 DDM ± 0.00002** (95 %, n = 212) vs injected +0.0040 → PASS at a placeholder
  tolerance 0.01 DDM; with `--set aid_bias_ddm=0.02` → FAIL (tested).
- Faults: **28 of 28** fault samples FLAG, **0** centred needles, **0** false FLAGs.
- One reading σ = **0.00015 DDM** at 30 dB (compare SkyRF's ≤ 0.02 % = 0.0002 DDM claim).

**What the jury wants to hear:** truth-reference uncertainty budget (RTK, time sync, lever arm, antenna phase centre),
how many passes for a confident verdict, Level 1/2/3 monitoring ladder, SMS also monitors ILS LOC/GP.

**Risks / limits (gaps):** no signal-in-space model (antenna array pattern, beam bends, ground plane); **ICAO Doc
8071 / Annex 10 tolerances not read** — the tolerance is a parameter; drone dynamics not modelled.

**Mentor questions:** Which aid (ILS, PAR, radar, PAPI)? Which tolerances do you use? Is the drone the guided vehicle
or the measuring instrument? Is a trend-monitoring story wanted?

**Run:** `python 03_Advionics/cases/case_6_flight_inspection_ils_drone/run.py [--set aid_bias_ddm=0.012] [--set tolerance_ddm=0.008]`.
Reuses `atc.ils`, `aerokit.approach`.
