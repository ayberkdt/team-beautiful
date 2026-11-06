# `sim_params.json` — VESPER parameters for the LuGus simulator

Built from the same code as
`04_Venus/docs/25_lugus_venus_rotorcraft.md`, so the numbers match the doc and `design.json` (same `version`).

## v0.7 variant note (44.63 kg, not confirmed)

This file is the **variant** of `outputs/sim_params_README.md`. The baseline `outputs/sim_params.json` is still v0.6
(43.66 kg, 80 s gust). Same schema and same keys; five rows are added to `limits`. Regenerate: `python 04_Venus/scripts/venus_variant_v07.py`. Do not use
`python 04_Venus/scripts/venus_sim_params.py` for it: that script writes the baseline.

- **Vertical gust correlation is 1500 s, not 80 s.** It is the Lagrangian 1/e time of the VEGA vertical wind
  (`research/data/venus_turbulence_model.json`, component A). A vehicle that moves through the cells sees a shorter
  time: 1/τ = 1/1500 s + V/5000 m, 409 s at 8.9 m/s. The 75.5 s VEGA sampling does not resolve periods under about
  150 s; the Dryden component C in the same file covers those. The 80 s value is withdrawn, it was an assumption.
- **Do not count interaction twice.** `vehicle.rotors.curve_at_55km` is an isolated rotor (factor 1.05), so the simulator
  adds its own wake model. `hover_electric_55km` and `loiter_electric_55km` already include nominal interaction; use them
  as reference values only.
- `max airspeed` holds the interaction ratio at its 20 m/s value above the last trimmed curve point.
- The simulator has not flown this mass. Pull-out current (52.7 A at cos z 0.68), canopy clearance and motor-out numbers
  in doc 25 were run at 43.66 kg.

Each changed scalar carries its old value in `source` as `[v0.7: was …]`. The full list is `sim_params_changes.json`.

| Value | Old | New | Unit | Tag | Source |
|---|---|---|---|---|---|
| `atmosphere_and_wind.vertical_gust_correlation` | 80 | 1500 | s | K | VEGA W_a autocorrelation: R(300 s)=0.78, R(600 s)=0.59-0.71, R(1200 s)=0.53-0.56, R(180… |
| `vehicle.mass` | 43.6552 | 44.6298 | kg | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interacti… |
| `vehicle.cg` | [-0.0, -0.0, 0.04] | [-0.0, -0.0, 0.0394] | m | K | component layout of the variant design.json [v0.7: was [-0.0, -0.0, 0.04] in v0.6] |
| `vehicle.inertia` | [[33.194, -0.0, 0.0], [-0.0, 33.194, 0.0], [0.0, 0.0, 65.088]] | [[34.196, -0.0, 0.0], [-0.0, 34.196, 0.0], [0.0, 0.0, 67.078]] | kg m^2 | K | point masses + rods from the variant design.json [v0.7: was [[33.194, -0.0, 0.0], [-0.0… |
| `vehicle.rotors.polar_inertia` | 0.1708 | 0.1746 | kg m^2 | K | blade rods; aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_wi… |
| `vehicle.rotors.collective_hover` | 7.0442 | 7.0825 | deg | K | BEMT trim at 55 km; aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.… |
| `vehicle.rotors.curve_at_55km.rows` | 27 rows | 27 rows | table | K | rebuilt for the variant; rows in sim_params.json |
| `vehicle.rotors.heave_derivative` | -31.7835 | -32.4113 | N/(m/s) | K | BEMT dT/dw at fixed rpm, pitch (whole vehicle); aerokit.venus.sizing.close with hover +… |
| `vehicle.rotors.v_h_55km` | 2.59062 | 2.61938 | m/s | K | momentum theory per rotor; aerokit.venus.sizing.close with hover +3.42 % (venus_budget_… |
| `vehicle.drive.rpm_response_20pct` | 0.30479 | 0.302856 | s | K | rotor inertia / spare torque; aerokit.venus.sizing.close with hover +3.42 % (venus_budg… |
| `vehicle.power.battery_capacity` | 1044.14 | 1109.48 | Wh | K | 0.5 h of 2219 W hover; aerokit.venus.sizing.close with hover +3.42 % (venus_budget_upda… |
| `vehicle.power.hover_electric_55km` | 2088.28 | 2218.96 | W | K/Y | BEMT + hover interaction +3.42 % (guc_egrisi.json, extrapolated to 0.04 D [Y]) [v0.7: w… |
| `vehicle.power.loiter_electric_55km` | 1336.53 | 1621.53 | W | K/Y | aerokit level power x nominal interaction ratio (guc_egrisi.json) [v0.7: was 1336.52909… |
| `vehicle.power.loiter_airspeed` | 7.8 | 8.9 | m/s | K/Y | minimum-power speed with nominal interaction [v0.7: was 7.8 in v0.6] |
| `limits[science dive floor]` | 51 | 52 | km | K | battery 57.5 degC peak after the 5 min hold at 52 km at 1.5 m/s down (venus_budget_upda… |
| `limits[dive abort battery temperature]` | null | 52 | degC | K/Y | doc 25 §0: 50 -> 52 degC, the 5 min hold at 52 km at 1.5 m/s needs it; venus_budget_upd… |
| `limits[release sun height, minimum cos z]` | null | 0.68 | - | K/Y | doc 25 §0: 52.7 A at cos z 0.68 against the 2C limit; simulator at 43.66 kg, not rerun … |
| `limits[release rotor speed, maximum]` | null | 668.5 | rpm | K | doc 25 §5.2: 1.30 x hover rpm, back-EMF cap [v0.7: new row] |
| `limits[descent to cruise]` | null | {"down_m_s": 1.5, "forward_m_s": 3.5} | m/s | K/Y | doc 25 §5.2: outside the vortex-ring band; venus_budget_update.Profile [v0.7: new row] |
| `limits[battery discharge current 2C]` | null | 53.6 | A | K/Y | 14S8P pack (venus_budget_update.pack at 1109 Wh); 2C is an aerokit input, not a measure… |
| `failure_modes[downdraft].effect` | +1.4 kW to hold altitude | +1.5 kW to hold altitude | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[downdraft].recovery` | ride it within 51-58 km, climb back (0.4 kWh) | ride it within 52-58 km, climb back (0.4 kWh) | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[battery hot].trigger` | interior > 50 degC during a dive | interior > 52 degC during a dive | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[sun too low].trigger` | cos zenith < 0.595 at 55 km | cos zenith < 0.678 at 55 km | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[sun too low].effect` | battery drains at ~1.3 kW | battery drains, up to ~376 W before the sunset dive | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[sun too low].recovery` | ~0.8 h on battery, then sunset dive | ~3.5 h on battery, then sunset dive | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[night].effect` | 0 W solar; 1.04 kWh vs ~103 kWh needed (loiter power x half the 154 h air-mass day) | 0 W solar; 1.11 kWh vs ~125 kWh needed (loiter power x half the 154 h air-mass day) | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `failure_modes[acid degradation].recovery` | mission ends at ~49 h anyway | mission ends at ~44 h anyway | - | K | recomputed for the variant (python 04_Venus/scripts/venus_variant_v07.py) |
| `deployment_replay.rows` | 338 rows | 340 rows | table | K | rebuilt for the variant; rows in sim_params.json |
| `mission_series.rows` | 50 rows | 44 rows | table | K | rebuilt for the variant; rows in sim_params.json |

## Value format

Every scalar is `{"value", "unit", "tag", "source"}`. Tables carry one `{unit, tag, source}` block per column.

| Tag | Meaning |
|---|---|
| `D` | primary data read in this session (PDS tables, NIST) |
| `D-ag` | read at the source by a research agent (notes in `04_Venus/research/`) |
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
