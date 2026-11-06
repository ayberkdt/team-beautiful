# R0 · Honeywell GAPS / HAPS aerospace proximity sensors — datasheet (round 3)

- **Source:** Honeywell, "General Aerospace Proximity Sensors (GAPS) and High-performance Aerospace Proximity Sensors (HAPS)"
  datasheet 000843-2-EN, downloaded by subagent R4 to `D:\tmp_ideathon\easa\dl\hf\honeywell_gaps_haps.pdf` (URL in
  `R4_sensor_failure_rates.md`).
- **Read by:** main session, 4 Nov 2026 (round 3), Tables 1–2 via `pdftotext`. Tags [D]. Vendor claims, not independent data.

| Parameter (Table 1/2) | GAPS | HAPS |
|---|---|---|
| Weight | **< 60 g** (inline), 85 g (right-angle) | 60–150 g |
| Sensing distance | **3.5 mm max** | 4 mm max |
| Body | stainless steel, hermetically sealed | same |
| Length | 55 mm max | 60 mm max |
| **MTBF** | **500 000 flight hours** (method not stated) | 500 000 FH |
| Supply | 12–32 Vdc | 12–28 Vdc |
| Supply current | **< 10 mA** | < 10 mA |
| Operating temperature | −55 °C to 115 °C | same |
| Power-on delay | < 1 s | < 1 s |
| Target material | 17-4 PH stainless steel, heat treated | same |
| Health monitoring | optional third output state ("Integral Health Monitoring") | same |
| DO-160G examples | §15 magnetic effect Cat A; §16 power input Cat A; §17 voltage spike Cat A (others in Table 2) | same |
| Technology | ECKO (eddy current killed oscillator) | — |

## Consequences for LOCK-SENSE [Y]

1. **Mass and power.** 4 sensors × < 60 g ≈ 0.24 kg, plus the alert unit, annunciators and harness (our estimate 0.25–0.35 kg)
   → **about 0.5–0.6 kg in total**. The earlier requirement R-10 (< 0.3 kg) was too optimistic and is corrected. Sensor
   power is 4 × 10 mA × 14 V ≈ 0.6 W, plus the unit and lamps → **< 2 W**.
2. **Sensing distance ≤ 3.5 mm.** The sensor face must sit within 3.5 mm of the bolt tip at full engagement, and well beyond
   3.5 mm at partial engagement. This must be measured on the aircraft (retrofit step 2). The AAIB ramp geometry (15 mm long,
   5 mm rise) suggests millimetre-scale bolt travel between the partial and full positions; whether that travel is axial at the
   sensor location is not published.
3. **Target.** The datasheet calibrates on 17-4 PH steel; the Extra shoot bolts are "steel" (AAIB p. 8), alloy not published →
   bench calibration on the real bolt (step 8).
4. **The third output state** (health monitoring) gives the same "fault ≠ inactive" coding our logic assumes.
