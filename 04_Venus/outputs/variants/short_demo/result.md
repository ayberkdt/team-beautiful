# Short demonstrator variant

Written by `python 04_Venus/code/variants/venus_short_demo.py`. Status: variant, not confirmed by the team.
Power model: 6 Nov budget, nominal interaction, current `guc_egrisi.json`. The simulator has **not** flown these designs.

| Payload kg | Gross kg | Battery Wh | Hover W | Loiter W | Sun carries loiter, cos z | Sun carries hover, cos z | Longest flight h | Entry mass kg |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.0 | 44.63 | 1109 | 2219 | 1632 | 0.681 | 0.832 | 43.5 | 290 |
| 1.5 | 40.75 | 982 | 1964 | 1457 | 0.631 | 0.769 | 46.7 | 265 |
| 0.5 | 38.23 | 901 | 1803 | 1346 | 0.598 | 0.727 | 48.6 | 248 |
| 0.0 | 36.98 | 862 | 1724 | 1292 | 0.582 | 0.706 | 49.6 | 240 |

## 6 h demonstration, no dives

| Payload kg | Release | cos z | Cruise reached h | Lowest SoC | Peak interior °C | Array / hover, lowest | Array / loiter, lowest |
|---:|:---|---:|---:|---:|---:|---:|---:|
| 3.0 | early | 0.71 | 1.12 | 0.98 | 38.6 | 0.84 | 1.14 |
| 3.0 | late | 0.94 | 1.12 | 1.00 | 38.6 | 1.24 | 1.69 |
| 1.5 | early | 0.66 | 1.12 | 0.99 | 36.3 | 0.86 | 1.15 |
| 1.5 | late | 0.94 | 1.12 | 1.00 | 36.3 | 1.40 | 1.89 |
| 0.5 | early | 0.63 | 1.12 | 0.99 | 34.8 | 0.87 | 1.17 |
| 0.5 | late | 0.94 | 1.12 | 1.00 | 34.8 | 1.53 | 2.04 |
| 0.0 | early | 0.61 | 1.12 | 1.00 | 34.3 | 0.88 | 1.17 |
| 0.0 | late | 0.94 | 1.12 | 1.00 | 34.3 | 1.60 | 2.13 |

## Checks

- 3 kg row against the budget: 44.63 kg here, 44.63 kg in `budget_update/result.json`.
- With dives, 3 kg: 43.5 h here, 43.5 h printed in `v0_7_44p6kg/CHANGES.md`, 43.8 h in `budget_update/result.json` (older curves).
- Mass growth: 2.55 kg of gross per kg of payload here; 2.4 to 2.5 in `sensitivity.json` (4 Nov, isolated rotors).
- No payload, by interaction case: low 36.26 kg, loiter 1185 W, late-release lowest SoC 1.00, nominal 36.98 kg, loiter 1292 W, late-release lowest SoC 1.00, high 37.72 kg, loiter 1399 W, late-release lowest SoC 1.00.

## Could the solar deck go?

Release to the end of a 1 h hold needs 2578 Wh at 1152 W descent. At 155 usable Wh/kg that is 16.6 kg of battery, against 9.6 kg for deck plus battery now. [K on Y, no closure, contingency not applied]

## Not done

- Pull-out battery current and canopy clearance were not rerun for these masses.
- Mission thresholds (1 h hold, 6 h demonstration) are proposals, not sponsor numbers.
- `design.json` and `sim_params.json` were not written for this variant.
