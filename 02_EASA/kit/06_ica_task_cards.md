# EASA kit · 06 — Instructions for Continued Airworthiness: task cards (draft)

**Status: competition draft.** ICA are required for a change (21.A.7) and must enter the aircraft maintenance programme
(ML.A.302(c)(5)(a)) — research note R3 [D-ag]. Intervals and values are ours [Y] unless tagged; gauge values come from
the trip-window analysis (C2) [K]. Installation, release and these tasks need a Part-CAO/Part-145 organisation or
independent Part-66 certifying staff, **not** the pilot-owner (ML.A.801(b); CS-SC110a §6 for the annunciator part) [D-ag].

| Task | Title | Interval [Y] | Who |
|---|---|---|---|
| T1 | Functional test of all annunciations | 100 h / annual, and after any canopy, lug or alert-unit work | B1/B3/L or Part-145 |
| T2 | Rigging check with the go/no-go gauge | 100 h / annual; after canopy removal, SB-NG-2-22 foam work, lug or bracket work | same |
| T3 | Sensor face and target inspection, cleaning | 100 h / annual | same |
| T4 | Event-log download and nuisance review | 100 h / annual and after any in-flight alert | same; review by the CAMO/owner |
| T5 | Canopy frame bond and transparency edge inspection (second barrier, AAIB cause) | annual [Y]; method to be agreed with the TC holder | NDT-qualified staff |
| T6 | Harness and connector inspection | annual | same |

---

### T1 · Functional test

1. Master ON: power-up test shows every legend and the voice (R-11).
2. Canopy open, handles released, parked → no alert (dark) and **not** green (logic table, `retrofit_plan.md` step 7).
3. Canopy seated, handle released but not pulled aft (partial lock, hazard H1) → **not green**; with the throttle above
   the take-off threshold (engine off, switch simulated per the installation drawing) → red flashing + voice.
4. Full lock → green.
5. One bolt held back by hand at a time (H2), three times → not green each time.
6. Pull the alert-unit circuit breaker → green goes **dark** (R-5). Reset.
7. Disconnect one sensor connector → CANOPY SENS (R-4). Reconnect.
8. Record results on the task card; any deviation = system inoperative (defer per AFMS §2).

### T2 · Rigging check with the go/no-go gauge

Gauge: two spacers that hold the aft handle at **67.0 mm** and at **69.0 mm** (handle centre distance as measured by
the AAIB, 60 mm partial / 70 mm full lock [D]) — `retrofit_plan.md` step 9.

1. Insert the 67.0 mm spacer, lock against it → every bolt sensor must read **not engaged**: no green.
2. Insert the 69.0 mm spacer → every bolt sensor must read **engaged**: green.
3. Both conditions per sensor; adjust the bracket shims if either fails, then repeat T1.
4. Why it matters: the fault tree shows systematic rigging error dominates the residual risk (importance ≈ 1, sensor
   terms ≈ 1e-15) [K], and the trip point must stay inside 67.5–68.7 mm for 0.3 mm rigging scatter [K]. If the bench
   test (plan step 8) measures more scatter, the gauge values are recomputed from C2.

### T3 · Sensor face and target inspection

1. Inspect the four sensor faces and the steel targets/bolt tips for damage, contamination, corrosion.
2. Clean with a lint-free cloth and a solvent compatible with the sensor housing (per the sensor CMM) [Y].
3. Check bracket security (torque per drawing) and that the sensing gap is within the sensor's range (≤ 3.5 mm, Honeywell
   GAPS datasheet [D]).

### T4 · Event-log download and nuisance review

1. Download the log (ground connector or EFB link, option O8).
2. Count per 1 000 flights: nuisance alerts (alert with the canopy found locked) and caught partial locks.
3. Compare with requirement R-3 (nuisance ≤ 1/10 of the unalerted-hazard rate). Repeated nuisance from one sensor →
   T2 + T3 on that sensor.
4. Send fleet counts to the TC holder / EASA (plan step 12): this is how the assumed rates of the study get replaced.

### T5 · Canopy frame bond and transparency edge inspection (separate barrier)

The lock alert does **not** address the AAIB G-MIIL cause (bonding → fatigue cracks). This task is the second barrier.

1. Visual inspection of the transparency edge along the frame for cracks and crazing.
2. Bond-line check of the inner/outer frame (tap test or ultrasonic method as specified by the TC holder) [Y].
3. EASA itself is evaluating such an NDT in its response to AAIB safety recommendation 2024-004 [D, doc 23 §1]; adopt
   its method when published.

### T6 · Harness and connector inspection

1. Harness on the fuselage side only; check routing clear of the canopy mechanism and the jettison path (R-9).
2. Chafing, clamp security, connector locking; dedicated ground wire intact (carbon fuselage is not a return path,
   AC 43.13-1B §11-66c [D-ag]).
