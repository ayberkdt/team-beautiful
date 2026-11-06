# VESPER budget update, 6 Nov 2026

`python 04_Venus/scripts/venus_budget_update.py`. Curves: `D:\Custom Yetenekler\sunumatik\.claude\worktrees\venus-rotorcraft-visual-44d0d1\presets\venus_rotorcraft\sim\guc_egrisi.json` (generated 2026-11-06T08:12:38.033Z, sha256 938bba1d9e5e). Legacy check: 49.18 h / 44.18 h (doc 25: 49.18 / 44.18).

## As built (43.66 kg, 4.45 m², 1044 Wh), 6 Nov profile

| Quantity | off | low | nominal | high |
|---|---:|---:|---:|---:|
| File minimum at 55 km (43.66 kg), W at m/s | 1325 at 8 | 1474 at 8 | 1572 at 9 | 1664 at 9 |
| Loiter in this budget, W | 1337 | 1487 | 1581 | 1673 |
| Loiter speed, m/s | 7.8 | 8.4 | 8.8 | 9.1 |
| Hover, W | 2088 | 2158 | 2158 | 2158 |
| Descent 1.5 m/s + 3.5 m/s forward, W | 951 | 1258 | 1448 | 1789 |
| Sun threshold cos z | 0.595 | 0.640 | 0.667 | 0.692 |
| Sun within, degrees of zenith | 53.5 | 50.2 | 48.2 | 46.2 |
| Sun window (closed form), h | 45.8 | 43.0 | 41.2 | 39.6 |
| Energy margin in the window | 1.77 | 1.63 | 1.56 | 1.50 |
| Release hour angle, deg | -51.3 | -48.0 | -45.8 | -43.8 |
| Flight on sunlight, h | 44.3 | 41.4 | 39.5 | 37.4 |
| Total flight, h | 49.7 | 46.4 | 44.5 | 42.2 |
| Drift, km | 11703 | 10943 | 10481 | 9950 |
| Lowest state of charge before sun loss | 64 % | 64 % | 65 % | 65 % |
| Battery peak before sunset, °C | 55.3 | 56.5 | 57.2 | 57.5 |
| Lowest altitude, km | 49.8 | 50.1 | 50.3 | 50.7 |
| End state of charge | 7 % | 7 % | 5 % | 6 % |
| Hover reserve, h (rule 0.5) | 0.500 | 0.484 | 0.484 | 0.484 |
| Hold at the dive floor, min (plan 5) | 5 | 5 | 5 | 3 |
| Check: sun_carries_loiter | yes | yes | yes | yes |
| Check: soc_floor | yes | yes | yes | yes |
| Check: dives_reach_floor | yes | yes | yes | yes |
| Check: dive_battery_below_60C | yes | yes | yes | yes |
| Check: dives_at_sun_rule | yes | yes | yes | yes |
| Check: hover_reserve | yes | NO | NO | NO |
| Check: charges_at_cruise | yes | yes | yes | yes |
| **Closes** | yes | NO | NO | NO |

## Recommended design (44.63 kg, 1109 Wh), 6 Nov profile

| Quantity | off | low | nominal | high |
|---|---:|---:|---:|---:|
| File minimum at 55 km (43.66 kg), W at m/s | 1325 at 8 | 1474 at 8 | 1572 at 9 | 1664 at 9 |
| Loiter in this budget, W | 1370 | 1524 | 1622 | 1715 |
| Loiter speed, m/s | 7.9 | 8.5 | 8.9 | 9.2 |
| Hover, W | 2147 | 2219 | 2219 | 2219 |
| Descent 1.5 m/s + 3.5 m/s forward, W | 986 | 1298 | 1492 | 1839 |
| Sun threshold cos z | 0.605 | 0.650 | 0.678 | 0.704 |
| Sun within, degrees of zenith | 52.7 | 49.4 | 47.3 | 45.3 |
| Sun window (closed form), h | 45.1 | 42.3 | 40.5 | 38.8 |
| Energy margin in the window | 1.74 | 1.60 | 1.53 | 1.47 |
| Release hour angle, deg | -50.6 | -47.1 | -44.9 | -42.8 |
| Flight on sunlight, h | 43.7 | 40.7 | 38.7 | 36.6 |
| Total flight, h | 49.2 | 45.9 | 43.8 | 41.5 |
| Drift, km | 11585 | 10810 | 10328 | 9785 |
| Lowest state of charge before sun loss | 66 % | 65 % | 65 % | 66 % |
| Battery peak before sunset, °C | 55.5 | 56.7 | 57.5 | 57.8 |
| Lowest altitude, km | 49.8 | 50.1 | 50.4 | 50.8 |
| End state of charge | 6 % | 6 % | 6 % | 7 % |
| Hover reserve, h (rule 0.5) | 0.517 | 0.500 | 0.500 | 0.500 |
| Hold at the dive floor, min (plan 5) | 5 | 5 | 5 | 3 |
| Check: sun_carries_loiter | yes | yes | yes | yes |
| Check: soc_floor | yes | yes | yes | yes |
| Check: dives_reach_floor | yes | yes | yes | yes |
| Check: dive_battery_below_60C | yes | yes | yes | yes |
| Check: dives_at_sun_rule | yes | yes | yes | yes |
| Check: hover_reserve | yes | yes | yes | yes |
| Check: charges_at_cruise | yes | yes | yes | yes |
| **Closes** | yes | yes | yes | yes |

## Battery at each mission event, recommended design

### off

| t (h) | Event | z (km) | SoC | battery °C | cos z |
|---:|---|---:|---:|---:|---:|
| 0.00 | release at 61.0 km | 61.00 | 100 % | 25.0 | 0.635 |
| 1.12 | cruise altitude reached | 55.00 | 100 % | 30.2 | 0.670 |
| 6.75 | science dive 1 starts | 55.00 | 100 % | 37.6 | 0.821 |
| 7.28 | science dive 1 bottom | 52.12 | 100 % | 46.9 | 0.834 |
| 7.37 | climb back to cruise | 52.00 | 100 % | 49.5 | 0.835 |
| 20.00 | science dive 2 starts | 55.00 | 100 % | 37.6 | 0.998 |
| 20.53 | science dive 2 bottom | 52.12 | 100 % | 46.9 | 0.999 |
| 20.62 | climb back to cruise | 52.00 | 100 % | 49.5 | 0.999 |
| 44.22 | array no longer carries loiter | 55.00 | 100 % | 37.6 | 0.605 |
| 48.20 | sunset dive starts | 55.00 | 23 % | 37.6 | 0.468 |
| 49.17 | end: battery above 60 °C at 49.8 km | 49.78 | 6 % | 60.4 | 0.433 |

### low

| t (h) | Event | z (km) | SoC | battery °C | cos z |
|---:|---|---:|---:|---:|---:|
| 0.00 | release at 61.0 km | 61.00 | 100 % | 25.0 | 0.680 |
| 1.12 | cruise altitude reached | 55.00 | 100 % | 31.0 | 0.713 |
| 6.00 | science dive 1 starts | 55.00 | 100 % | 38.2 | 0.838 |
| 6.53 | science dive 1 bottom | 52.12 | 100 % | 48.4 | 0.849 |
| 6.62 | climb back to cruise | 52.00 | 100 % | 51.1 | 0.851 |
| 20.00 | science dive 2 starts | 55.00 | 100 % | 38.2 | 1.000 |
| 20.53 | science dive 2 bottom | 52.12 | 100 % | 48.4 | 1.000 |
| 20.62 | climb back to cruise | 52.00 | 100 % | 51.1 | 1.000 |
| 41.32 | array no longer carries loiter | 55.00 | 100 % | 38.2 | 0.650 |
| 44.97 | sunset dive starts | 55.00 | 35 % | 38.2 | 0.531 |
| 45.87 | end: battery above 60 °C at 50.1 km | 50.14 | 6 % | 60.5 | 0.499 |

### nominal

| t (h) | Event | z (km) | SoC | battery °C | cos z |
|---:|---|---:|---:|---:|---:|
| 0.00 | release at 61.0 km | 61.00 | 100 % | 25.0 | 0.708 |
| 1.12 | cruise altitude reached | 55.00 | 100 % | 31.4 | 0.739 |
| 6.00 | science dive 1 starts | 55.00 | 100 % | 38.6 | 0.858 |
| 6.53 | science dive 1 bottom | 52.12 | 100 % | 49.3 | 0.869 |
| 6.62 | climb back to cruise | 52.00 | 100 % | 52.1 | 0.871 |
| 20.00 | science dive 2 starts | 55.00 | 100 % | 38.6 | 1.000 |
| 20.53 | science dive 2 bottom | 52.12 | 100 % | 49.3 | 0.999 |
| 20.62 | climb back to cruise | 52.00 | 100 % | 52.1 | 0.998 |
| 39.48 | array no longer carries loiter | 55.00 | 100 % | 38.6 | 0.678 |
| 42.97 | sunset dive starts | 55.00 | 41 % | 38.6 | 0.567 |
| 43.82 | end: battery above 60 °C at 50.4 km | 50.41 | 6 % | 60.3 | 0.538 |

### high

| t (h) | Event | z (km) | SoC | battery °C | cos z |
|---:|---|---:|---:|---:|---:|
| 0.00 | release at 61.0 km | 61.00 | 100 % | 25.0 | 0.734 |
| 1.12 | cruise altitude reached | 55.00 | 95 % | 32.2 | 0.764 |
| 6.00 | science dive 1 starts | 55.00 | 100 % | 39.0 | 0.876 |
| 6.53 | science dive 1 bottom | 52.12 | 100 % | 50.8 | 0.887 |
| 6.58 | dive aborted: battery above 52 °C | 52.00 | 100 % | 52.5 | 0.888 |
| 20.00 | science dive 2 starts | 55.00 | 100 % | 39.0 | 0.998 |
| 20.53 | science dive 2 bottom | 52.12 | 100 % | 50.8 | 0.996 |
| 20.58 | dive aborted: battery above 52 °C | 52.00 | 100 % | 52.5 | 0.996 |
| 37.70 | array no longer carries loiter | 55.00 | 100 % | 39.0 | 0.704 |
| 40.72 | sunset dive starts | 55.00 | 56 % | 39.0 | 0.611 |
| 41.50 | end: battery above 60 °C at 50.8 km | 50.77 | 7 % | 60.2 | 0.585 |

## Science dive floor at 1.5 m/s down (nominal, 50 °C abort off)

| Floor (km) | Climb (m/s) | Battery at bottom (°C) | Peak (°C) | Lowest SoC |
|---:|---:|---:|---:|---:|
| 51.0 | 3.0 | 55.0 | 64.4 | 49 % |
| 51.5 | 3.0 | 51.7 | 60.6 | 58 % |
| 52.0 | 3.0 | 49.1 | 57.2 | 65 % |
| 52.5 | 3.0 | 46.1 | 53.5 | 71 % |
| 53.0 | 3.0 | 43.6 | 50.1 | 78 % |
| 52.0 | 2.0 | 49.1 | 57.6 | 71 % |
| 52.0 | 1.5 | 49.6 | 58.4 | 78 % |

## Simulator end state against this budget

| Run | Interaction | Air | Start cos z | Start SoC | Sim end SoC | Budget end SoC | Sim peak °C (1 node) | Budget peak °C (2 nodes) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| as simulated 5 Nov: afternoon, cos z 0.70 | nominal | seed 1 | 0.70 | 100 % | 17 % | 16 % | 58.3 | 63.2 |
| same, interaction off | off | seed 1 | 0.70 | 100 % | 26 % | 27 % | 57.6 | 61.1 |
| same, calm air | nominal | calm | 0.70 | 100 % | 21 % | 16 % | 58.7 | 63.2 |
| dive at cos z 0.80 (morning) | nominal | seed 1 | 0.80 | 100 % | 42 % | 43 % | 55.9 | 63.2 |
| dive at cos z 0.87, calm | nominal | calm | 0.87 | 100 % | 56 % | 53 % | 56.0 | 63.2 |
| dive at cos z 0.87, seed 2 | nominal | seed 2 | 0.87 | 100 % | 22 % | 53 % | 59.8 | 63.2 |
| dive at cos z 0.87, seed 3 | nominal | seed 3 | 0.87 | 100 % | 48 % | 53 % | 56.0 | 63.2 |
| dive near noon | nominal | seed 1 | 1.00 | 100 % | 68 % | 68 % | 54.3 | 63.2 |
| sunset as simulated: forced SoC 35 %, cos z 0.12 | nominal | seed 1 | 0.12 | 35 % | 0 % | -0 % | 48.5 | 38.5 |
| sunset at mission state, at 60 C | nominal | seed 1 | 0.61 | 50 % | 14 % | 22 % | 60.0 | 60.0 |

Simulator dives to 52 km (cos z 0.87, nominal): seed 1: max tilt 12.2°, lowest SoC 70 %, peak 51.4 °C; seed 2: max tilt 12.3°, lowest SoC 35 %, peak 54.8 °C; seed 3: max tilt 8.1°, lowest SoC 61 %, peak 52.2 °C.

Simulator dives to 51 km (cos z 0.87, nominal): seed 1: max tilt 10.7°, lowest SoC 52 %, peak 55.1 °C; seed 2: max tilt 10.8°, lowest SoC 21 %, peak 59.8 °C; seed 3: max tilt 8.2°, lowest SoC 48 %, peak 56.0 °C.

## Gust re-run

| Model | z RMS (m) | z peak (m) | Thrust RMS / W | Thrust peak / W |
|---|---:|---:|---:|---:|
| Doc 25: σ 0.7, 80 s, 2 h, one seed | 4.1 | 11.0 | 0.049 | 0.140 |
| Same loop, 1500 s, 20 h, one seed | 4.5 | 14.0 | 0.052 | 0.164 |
| Component A, hover, 1500 s, 49 h × 32 | 5.1 | 20.6 | 0.058 | 0.240 |
| A + C, loiter, τ 412 s, 49 h × 32 | 5.9 | 26.9 | 0.069 | 0.329 |

A -3.5 m/s downdraft held: thrust 0.293 W, altitude offset 25 m, +1658 W. Holding one 0.7 m/s cell for 1500 s costs 138 Wh. Nominal mission with component A held, 40 seeds: 43.1 / 44.4 / 45.0 h (p5 / median / p95), lowest SoC before sun loss 62 %, 3 runs end with an empty battery.

## Closed designs for the nominal case

| Option | Gross kg | Deck m² | Battery Wh | Span m | Loiter W | cos z | Sun h | Flight h | High h | Cruise interior °C | Closes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| re-closed, 0.10 m gap | 44.6 | 4.45 | 1109 | 8.0 | 1622 | 0.678 | 38.7 | 43.8 | 41.5 | 36.6 | yes |
| gap 0.26 m (0.1 D) | 46.7 | 5.03 | 1171 | 8.3 | 1699 | 0.645 | 41.0 | 45.9 | 43.9 | 36.6 | yes |
| gap 0.52 m (0.2 D) | 50.3 | 6.04 | 1282 | 8.8 | 1834 | 0.600 | 43.8 | 48.6 | 46.8 | 36.6 | yes |
| gap 0.78 m (0.3 D) | 60.9 | 7.14 | 1634 | 9.4 | 2269 | 0.619 | 42.5 | 47.5 | 45.8 | 36.6 | NO |
| halo deck 0.15 m | 60.1 | 8.29 | 1627 | 8.0 | 2291 | 0.562 | 46.1 | 50.6 | 48.9 | 36.6 | NO |
| halo deck 0.30 m | 81.2 | 12.27 | 2428 | 8.0 | 3300 | 0.552 | 46.7 | 50.9 | 49.4 | 36.6 | NO |
| battery 0.75 h hover | 62.1 | 4.45 | 2550 | 8.0 | 2384 | 0.871 | 22.4 | 29.7 | 25.0 | 36.6 | NO |
| battery 1.0 h hover | no closure: mass closure diverges: growth factor above 1 | | | | | | | | | | |
| cruise 54 km | 43.1 | 4.45 | 1023 | 8.0 | 1606 | 0.717 | 37.9 | 41.8 | 39.7 | 46.5 | NO |
| cruise 56 km | 46.6 | 4.45 | 1219 | 8.0 | 1751 | 0.682 | 40.0 | 45.5 | 43.0 | 30.5 | yes |

## Pull-out battery current against the 53.6 A 2C limit (simulator, 43.66 kg, 14S8P)

| Release cos z | Peak A | Bus W | Array W |
|---:|---:|---:|---:|
| 0.630 | 56.7 | 5258 | 2187 |
| 0.635 | 56.3 | 5265 | 2215 |
| 0.681 | 52.7 | 5325 | 2455 |
| 0.708 | 50.1 | 5340 | 2605 |
| 0.734 | 47.3 | 5340 | 2750 |

## Model uncertainty carried by these numbers

Wake model fitted to NASA MTB wind-tunnel thrust ratios (tip gap 0.47 D, kw 0.50; low/high 0.30/0.70, rms 0.041). The fit covers V ≥ 3.5 m/s and may under-predict below that. VESPER's 0.04 D gap is outside the tested range. `guc_egrisi.json` predates a yaw-shed change; level trim agrees (harness 1578 W at 7.8 m/s). Low to high is the bracket on these curves, not a confidence interval.


Recommended: **re-closed, 0.10 m gap**. Entry: 284 → 290 kg, β 25.1 → 25.7 kg/m², 56.1 → 56.0 g.

## Figure briefs (written before drawing)

- **B1 power curve.** Message: interaction lifts minimum power at 55 km and moves it from 8 to 9 m/s. Reader: mixed jury.
  Target: sunum-tam. Data: airspeed vs electric power, four cases, `trim_ok` rows only. Form: lines, direct labels.
- **B2 mission.** Message: every case stays far above the battery floor; more interaction only shortens the day.
  Reader: mixed jury. Data: altitude and state of charge vs time, four cases, recommended design. Form: two panels.
- **B3 options.** Message: small changes buy hours cheaply; a bigger deck or battery costs far more mass.
  Reader: mixed jury. Data: one point per closed design; battery 0.75 h (62 kg, 30 h), halo 0.30 m (81 kg) and battery
  1.0 h (no closure) are off this scale and stay in the table. Form: labelled scatter (flight time is the outcome, so
  it stays on y although it is a duration).
