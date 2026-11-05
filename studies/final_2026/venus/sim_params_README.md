# `sim_params.json` — VESPER parameters for the LuGus simulator

Regenerate: `python scripts/venus_sim_params.py` (needs `PYTHONPATH=src`). Built from the same code as
`docs/25_lugus_venus_rotorcraft.md`, so the numbers match the doc and `design.json` (same `version`).

## Value format

Every scalar is `{"value", "unit", "tag", "source"}`. Tables carry one `{unit, tag, source}` block per column.

| Tag | Meaning |
|---|---|
| `D` | primary data read in this session (PDS tables, NIST) |
| `D-ag` | read at the source by a research agent (notes in `research_notes/Venus rotorcraft/`) |
| `K` | computed by `aerokit.venus` |
| `Y` | assumption: change it freely in the simulator |

## Sections

| Key | What it holds | How to use it |
|---|---|---|
| `atmosphere_and_wind.rows` | 30–80 km every 0.5 km: T, p, ρ (+ probe envelope), sound speed, viscosity, g, westward wind (mean + band), solar array output with the Sun overhead, up/down flux ratio | interpolate linearly in `altitude_m`; `null` means no measured band there |
| `atmosphere_and_wind` scalars | sun-angle law, vertical/horizontal gust σ and correlation time, VEGA-2 downdraft episode, meridional wind | Dryden-like noise with σ and τ; replay the downdraft as a scenario |
| `vehicle` | mass, CG, inertia, drag area; rotor positions/spins/radius/inertia; rotor curve at 55 km; heave derivative; vortex-ring band; drive, power and thermal parameters | rotor curve: thrust and torque × ρ(h)/ρ(55 km) at the same rpm and pitch |
| `limits` | temperatures, tip Mach, airspeed, g, acid exposure, altitude bands | end or warn the scenario when crossed |
| `failure_modes` | trigger → effect → recovery for motor out, vortex ring, downdraft, hot battery, low sun, night, latch failure, acid | inject one at a time |
| `deployment_replay` | release at 61 km → pull-out (time, altitude, descent rate) | check the simulator's pull-out against it |
| `mission_series` | whole flight (h, km, battery Wh, solar W, demand W, cos zenith, interior °C) | reference run for the day scenario |

## Frames

Body: x forward (between arms 1 and 6), y left, z up. World: x east, z up. The wind blows westward (−x) at the
tabulated speed. Fly in the air-mass frame (the mean wind only carries the vehicle); add gusts on top.

## Known limits of the data

- Outside 40–64 km the atmosphere is a VIRA-like secondary table, with no envelope.
- The forward-flight model is valid to advance ratio ~0.43 (~30 m/s). Station keeping against the 49–84 m/s wind is
  outside it and outside the power budget.
- Rotor data are BEMT (torque rms 6.3 % against Earth rotor tests), not Venus measurements.
