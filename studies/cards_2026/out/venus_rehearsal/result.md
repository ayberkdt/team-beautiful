# LuGus rehearsal: which Venus drone, at which altitude, on which power

Rehearsal card. Masses, areas, efficiencies and figures of merit are ASSUMPTIONS for a 10 kg class daughter drone; replace with the challenge's own numbers.

## Operating point: 55 km

27 °C, 0.53 bar, ρ 0.925 kg/m³, g 8.71 m/s², zonal wind 72 m/s. A 1 m² bifacial panel gives 173 W averaged over a solar day (543 W with the Sun overhead).

| Concept | Power to stay aloft (W) | Specific power (W/kg) | Weight carried by gas | Panel for day average (m²) |
|---|---:|---:|---:|---:|
| Solar aeroplane | 105 | 11 | 0 % | 0.6 |
| Helium-assisted quad | 149 | 15 | 76 % | 0.9 |
| Battery quadrotor | 1236 | 124 | 0 % | 7.1 |

Holding position against the 72 m/s wind with a 12 m³ envelope would take 335 kW: live in the air-mass frame and drift.

Simulator parameters: `vehicles_for_simulator.json` (SI). Environment profile: `studies/challenges_2026/venus_environment.json`.

## Mission flown (time-stepped: superpressure He cell, rotors, battery, solar, hull temperature)

Float altitude of the cell alone 52.4 km. Mission 3.3 h, drifted 769 km east with the wind. Battery lowest 135 of 500 Wh, end 181 Wh; peak draw 485 W. Hull peak 89 °C, above the 70 °C electronics limit for 66 min.

| Time (h) | Event |
|---:|---|
| 0.17 | held 55.0 km for 600 s |
| 1.01 | reached 48.0 km |
| 1.51 | held 48.0 km for 1800 s |
| 2.35 | reached 55.0 km |
| 3.35 | held 55.0 km for 3600 s |

Replay for the simulator: `mission_replay.json` (1 Hz frames, SI, temperatures in °C).
