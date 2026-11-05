# D_jpl_m2020_ingenuity_battery — Ingenuity (Sony VTC4) and Perseverance battery limits

## Citation
West, W., Smart, M., & Herman, J. (NASA JPL) (2021). *Battery System Design, Testing, and
Operation for the Mars Perseverance Rover and Ingenuity Helicopter.* Presentation (25
slides), © 2021 Caltech. Hosted by NASA:
https://www.nasa.gov/wp-content/uploads/2024/01/battery-system-design-testing-and-operation-for-the-mars-perseverance-rover-and-ingenuity-helicopter.pdf
(Slides cite Smart et al., Pacific Power Source Symposium 2019, for the VTC4 data.)

## What I read
Full text extraction; slides 4–5 (rover) and 18–19 (helicopter).

## Ingenuity battery (slide 18–19) [D-ag]
- **6 series Sony SE US18650 VTC4** Li-ion cells, 15.0–25.2 V; nameplate **2.00 Ah/cell**;
  cell max discharge > 25 A; max charge 4.25 V (manufacturer), 4.20 V operational.
- Power: continuous 60 W × 6 = **360 W**; peak 85 W × 6 = **510 W**.
- Estimated BOL energy: **44.4 Wh at 25 °C; 38.8 Wh at 0 °C**.
- Cell mass **45.5 g × 6 = 273 g**.
- Allowable temperatures: flight (high-rate discharge) **+10…+25 °C**; survival (low-rate
  discharge) −15…+25 °C; surface low-rate charge −5…+25 °C; non-operational (cruise)
  −20…+45 °C; cruise SOC kept 20–35 %.
- High-power test at 10 °C, 80 % SOC: 187 s at 510 W peak / 370 W nominal; max cell current
  30.159 A; min projected battery voltage 16.905 V. Battery heated to ~20 °C before real flights.

Derived (my calc): 44.4 Wh / 0.273 kg = **163 Wh/kg cell-level at 25 °C**; 142 Wh/kg at 0 °C.

## Perseverance rover battery (slides 4–5) [D-ag]
EaglePicher, 8s2p, 43 Ah/string, graphite/NCA; requirement 2408 Wh at 20 °C; operating
−20…+30 °C with charge and discharge permitted; AFT −20…+35 °C; cell-to-cell gradient ≤ 5 °C.

## Caveats
Ingenuity limits are mission-imposed operational limits (conservative), not the cell
datasheet. They show JPL kept a high-power COTS 18650 between +10 and +25 °C for flight.
