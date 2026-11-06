# Case 5 — GNSS-independent automated approach guidance from a ground sensor

**Task wording that triggers it:** "without GNSS / GPS", "jamming", "automatic landing", "automated approach",
"UAS on a ship deck", "integrity / alert limit / protection level", "SBAS / GBAS / LPV". Pre-reveal prediction
(doc 18, `prev_guess/03_Advionics/`).

**Concept (5 lines)**
1. A ground radar / IFF array (sponsor's world: PSR/SSR/NORA/L-IESA) measures range + angles → aircraft position.
2. Angle error becomes position error R·δ: 0.05° at 1.5 km ≈ 1.3 m — dissimilar to GNSS.
3. Monte Carlo of the approach to the 200 ft gate per navigation source (`aerokit.approach`).
4. Dissimilar monitor: radar vs GNSS separation test with a stated false-alert rate; threshold + fault bound vs VAL.
5. Panel rule (atc.guidance): no valid source → needles removed, never centred.

**Three numbers** (`outputs/result.md`, 100 runs per source)
- 95 % vertical error at the gate: GNSS **4.9 m**, ground radar 0.05° **2.1 m**, 0.1° **4.4 m**, spoofed GNSS
  (0.5 m/s ramp) **57.5 m** — VAL 35 m (LPV-200).
- Spoofed GNSS alone: **55 m** undetected; with the radar monitor: alarm at **280 m** height, largest undetected **15 m**.
- Monitor threshold / fault bound: **14.5 m / 24.6 m** vs VAL 35 m.

**What the jury wants to hear:** error budget from the antenna's own numbers (L-IESA az < 0.1° RMS, 100 ms beam
re-pointing), elevation as the weak axis (sea/ground multipath), cooperative + non-cooperative sensors, verification
with SkyRF and RES.

**Risks / limits:** sensor sigmas are [Y]; no moving deck frame, no multipath model; integrity numbers are
single-fault simplified forms; Annex 10 APV figures from a secondary transcription.

**Mentor questions:** Guided vehicle: manned aircraft, UAS, or ship-deck recovery? Which ground sensor may we assume?
Is automatic flight control in scope, or guidance display only?

**Run:** `python 03_Advionics/cases/case_5_gnss_independent_approach/run.py [--quick] [--set radar_range_at_gate_m=2500]`
· earlier card version: `prev_guess/03_Advionics/scripts/approach_day.py`. Reuses `aerokit.approach`.
