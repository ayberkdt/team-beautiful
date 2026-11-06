# VESPER v0.7 variant: 44.63 kg, 6 Nov profile

**Status: variant. The team has not confirmed 44.6 kg.** Nothing in `outputs/` outside this folder changed. Written by `python 04_Venus/scripts/venus_variant_v07.py` on 2026-11-06. Every number below is from that run, or read from `variants/budget_update/result.json` where the text says so.

## Mass: which component takes each gram

Grams from the unrounded breakdown in `variants/budget_update/result.json` (`baseline_breakdown` → `breakdown`).

| Component | v0.6 kg | v0.7 kg | Added g | Why |
|---|---:|---:|---:|---|
| rotors | 6.084 | 6.353 | +269 | blades + hubs +41 g (chord follows weight), motors + gearboxes +214 g (torque and power: weight and +3.42 % hover), ESCs +14 g |
| arms | 7.660 | 7.660 | +0 | no change |
| body | 3.153 | 3.203 | +50 | vessel grows 12 % of the battery mass added |
| battery | 6.740 | 7.162 | +422 | 0.5 h of hover at 2219 W instead of 2088 W |
| solar | 4.007 | 4.007 | +0 | no change |
| payload | 3.000 | 3.000 | +0 | no change |
| avionics | 1.200 | 1.200 | +0 | no change |
| antenna | 0.800 | 0.800 | +0 | no change |
| thermal | 0.876 | 0.902 | +26 | 6 % of the battery mass added |
| coating | 0.686 | 0.702 | +16 | 2 % of the base mass |
| attach | 0.800 | 0.800 | +0 | no change |
| wiring | 1.373 | 1.403 | +30 | 4 % of the base mass |
| contingency | 7.276 | 7.438 | +162 | 20 % of everything above |
| **sum** | **43.655** | **44.630** | **+975** | total_mass_kg 44.63 |

The v0.6 `design.json` lists 43.651 kg against 43.66 kg because `rotors` was rounded to 6.08 kg; here it keeps three decimals (6.353 kg), so the 13 components sum to 44.630 kg. `arms` stays 7.660 kg: the 0.8 mm minimum gauge governs the tube, not the load. Span, deck and rotor diameter do not change; blade chord does (table below).

## Mission and margins of this variant

Nominal interaction: 43.8 h flight, 38.7 h on sunlight, ends at 50.4 km with the battery at the 60 °C limit. Loiter 1622 W at 8.9 m/s, hover 2219 W, sun threshold cos z 0.678. Release at cos z 0.708. Pack 14S8P, 2C limit 53.6 A.

Gust model re-run at 44.63 kg and 8.9 m/s (doc 25 §4.7 is at 43.66 kg and 8.8 m/s): altitude RMS 5.8 m, peak 26.9 m, thrust peak 32.8 % W, margin 1.83×. Mission with component A held, 40 seeds: 42.6 / 43.8 / 44.5 h (p5 / median / p95), 2 runs end empty.

## Figures

| Figure | State | Audit |
|---|---|---|
| F1_altitude_justification | numbers unchanged, same PNG bytes as baseline | figür denetimi: 0 HATA · 0 UYARI · 1 BİLGİ · TESLİM EDİLEBİLİR |
| F2_power_vs_altitude | regenerated | figür denetimi: 0 HATA · 1 UYARI · 2 BİLGİ · TESLİM EDİLEBİLİR |
| F3_entry | regenerated | figür denetimi: 0 HATA · 0 UYARI · 2 BİLGİ · TESLİM EDİLEBİLİR |
| F4_mass_budget | regenerated | figür denetimi: 0 HATA · 0 UYARI · 1 BİLGİ · TESLİM EDİLEBİLİR |
| F5_risk_matrix | numbers unchanged, same PNG bytes as baseline | figür denetimi: 0 HATA · 0 UYARI · 0 BİLGİ · TESLİM EDİLEBİLİR |
| F6_mission | regenerated | figür denetimi: 0 HATA · 0 UYARI · 1 BİLGİ · TESLİM EDİLEBİLİR |
| F7_trade | regenerated | figür denetimi: 0 HATA · 1 UYARI · 2 BİLGİ · TESLİM EDİLEBİLİR |
| F8_bemt_validation | numbers unchanged, same PNG bytes as baseline | figür denetimi: 0 HATA · 0 UYARI · 1 BİLGİ · TESLİM EDİLEBİLİR |
| F9_sensitivity | not regenerated: no variant sensitivity.json | - |
| F10_robustness | not regenerated: no variant sensitivity.json | - |
| F11_entry_validation | numbers unchanged, same PNG bytes as baseline | figür denetimi: 0 HATA · 0 UYARI · 2 BİLGİ · TESLİM EDİLEBİLİR |
| F12_deployment_monte_carlo | regenerated | figür denetimi: 0 HATA · 0 UYARI · 1 BİLGİ · TESLİM EDİLEBİLİR |
| F13_day_and_station_keeping | regenerated | figür denetimi: 0 HATA · 1 UYARI · 2 BİLGİ · TESLİM EDİLEBİLİR |
| F14_end_of_mission | regenerated | figür denetimi: 0 HATA · 0 UYARI · 2 BİLGİ · TESLİM EDİLEBİLİR |
| F15_margins | regenerated | figür denetimi: 0 HATA · 0 UYARI · 0 BİLGİ · TESLİM EDİLEBİLİR |

## Figure briefs (written before drawing)

Set: `vesper.seti.json` copied from the baseline, so colours, axes and margins stay those of F1–F15. Reader: mixed jury.
Target: `sunum-tam`. Each brief gives the message; form and data are the baseline figure's unless stated.

- **F2.** Power with interaction leaves the array a smaller margin; loiter sits at 1.62 kW at 55 km.
- **F3.** One more kilogram of vehicle does not move the entry: still 56 g.
- **F4.** The added mass is mostly battery, motors and the 20 % contingency on them. Thermal joins the "other" bar.
- **F6.** The mission now starts at 61 km and ends at 50.4 km at the 60 °C limit. The altitude axis is set for that range.
- **F7.** Trade shape stays; every point carries the interaction, so the sun threshold is higher.
- **F9, F10.** Sensitivities and rotor choices re-flown with interaction and the 6 Nov profile.
- **F12.** Pull-out loss barely changes with mass.
- **F13.** The sun window shrinks against the higher loiter line.
- **F14.** The fall starts at 50.4 km, not 47.3 km.
- **F15.** Thrust against gust peak is the tightest flight margin with the 1500 s gust.

## design.json: every changed value

83 changed leaves. `operations.events` and `operations.series_hourly` are replaced whole; their rows are in `design.json`. Same list as JSON: `changes_full.json`.

| Path | Old | New | Tag | Source |
|---|---|---|---|---|
| `version` | 0.6 | 0.7 | - | this variant |
| `note` | Generated by aerokit.venus (sizing loop + BEMT + entry/descent + mission simulation). T… | Generated by aerokit.venus (sizing loop + BEMT + entry/descent + mission simulation). T… | - | this variant |
| `atmosphere.source` | 40-64 km: Pioneer Venus 4-probe mean of T, p, rho; wind = mean of the probes with a DLB… | 40-64 km: Pioneer Venus 4-probe mean of T, p, rho; wind = mean of the probes with a DLB… | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.cloud_layers[0].h2so4_wt_pct` | [75, 98] | [75, 98] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.cloud_layers[1].h2so4_wt_pct` | [75, 90] | [75, 90] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.cloud_layers[2].h2so4_wt_pct` | [75, 90] | [75, 90] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.vertical_wind_54km.altitude_km` | [53.0, 55.0] | [53.0, 55.0] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.vertical_wind_54km.sigma_m_s` | [0.65, 0.75] | [0.65, 0.75] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.vertical_wind_54km.downdraft_episode_m_s` | [2.0, 3.3] | [2.0, 3.3] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.vertical_wind_54km.downdraft_duration_h` | [2.0, 2.0] | [2.0, 2.0] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `atmosphere.vertical_wind_54km.gust_period_s` | [30.0, 130.0] | [30.0, 130.0] | K | python 04_Venus/scripts/venus_variant_v07.py |
| `operating_band.rationale` | 55 km: 26 °C, 0.51 bar, ρ 0.889 kg/m³ (PV mean); battery charge window 0-45 °C holds at… | 55 km: 26 °C, 0.51 bar, ρ 0.889 kg/m³ (PV mean); battery charge window 0-45 °C holds at… | K | doc 25 §0: floor 52 km |
| `vehicle.total_mass_kg` | 43.66 | 44.63 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.rotor.root_chord_m` | 0.0779 | 0.0797 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.rotor.tip_chord_m` | 0.0468 | 0.0478 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.rotor.collective_75_deg` | 7.04 | 7.08 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.rotor.reynolds_75` | 175000 | 178000 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.rotor.figure_of_merit` | 0.604 | 0.586 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.rotor.solidity` | 0.0274 | 0.028 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.rotor.disk_loading_N_m2` | 11.94 | 12.2 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction); blade chord follows weight at fixed C_T/σ |
| `vehicle.performance_55km.hover_electric_W` | 2088 | 2219 | K/Y | venus_budget_update power table, nominal interaction |
| `vehicle.performance_55km.loiter_electric_W` | 1337 | 1622 | K/Y | venus_budget_update power table, nominal interaction |
| `vehicle.performance_55km.loiter_airspeed_m_s` | 7.8 | 8.9 | K/Y | venus_budget_update power table, nominal interaction |
| `vehicle.performance_55km.solar_sustains_loiter_above_mu0` | 0.595 | 0.678 | K/Y | venus_budget_update power table, nominal interaction |
| `vehicle.performance_55km.battery_Wh` | 1044 | 1109 | K/Y | venus_budget_update power table, nominal interaction |
| `vehicle.components[rotors].mass_kg` | 6.08 | 6.353 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[body].mass_kg` | 3.153 | 3.203 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[battery].name` | Li-ion battery 1044 Wh (inside vessel) | Li-ion battery 1109 Wh (inside vessel) | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[battery].mass_kg` | 6.74 | 7.162 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[thermal].mass_kg` | 0.876 | 0.902 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[coating].mass_kg` | 0.686 | 0.702 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[wiring].mass_kg` | 1.373 | 1.403 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `vehicle.components[contingency].mass_kg` | 7.276 | 7.438 | K | aerokit.venus.sizing.close with hover +3.42 % (venus_budget_update.close_with_interaction) |
| `entry.entry_mass_kg` | 283.8 | 290.1 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.ballistic_coefficient_kg_m2` | 25.1 | 25.7 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.peak_deceleration_g` | 56.1 | 56 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.peak_heat_flux_W_cm2.convective_sutton_graves` | 228 | 230 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.heat_load_kJ_cm2` | 3.94 | 3.99 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.parachute_deploy_km` | 79.3 | 79.2 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.heatshield_jettison_km` | 78.3 | 78.2 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.suspended_mass_kg` | 227 | 232.1 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.time_on_parachute_s` | 716 | 707 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.release_descent_rate_m_s` | 12.8 | 13 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.pullout_altitude_loss_m` | 26 | 27 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.pullout_altitude_loss_if_dropped_unspun_m` | 559 | 565 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.vehicle` | 43.7 | 44.6 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.heatshield_structure` | 15.3 | 15.6 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.heatshield_tps` | 28.4 | 29 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.backshell_structure` | 26.2 | 26.8 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.backshell_tps` | 17.5 | 17.9 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.parachute_system` | 21.8 | 22.3 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.deployment_mechanism` | 32.7 | 33.5 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.misc_comm_power_ballast` | 32.7 | 33.5 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.total` | 218.3 | 223.1 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `entry.mass_budget_kg.total_with_contingency` | 283.8 | 290.1 | K | entry chain of aerokit.venus.design.baseline at the new vehicle mass |
| `deployment_sequence[3].name` | Peak deceleration 56 g; peak heating 228 W/cm² convective + 18 radiative | Peak deceleration 56 g; peak heating 230 W/cm² convective + 18 radiative | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[3].altitude_km` | 92.4 | 92.3 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[4].altitude_km` | 79.3 | 79.2 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[4].time_s` | 139 | 140 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[5].altitude_km` | 78.3 | 78.2 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[5].time_s` | 149 | 150 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[6].time_s` | 390 | 387 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[7].time_s` | 713 | 705 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[7].load` | flat collective (no thrust on the bridle); spin-up ~2.3 s per rotor; alternating spins … | zero-lift collective, about -16 deg at 0.75 R (no thrust on the bridle at the 13.0 m/s … | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[8].name` | Release at 13 m/s descent; pull-out in 3.4 s, 26 m lost (forward flight through vortex-… | Release at 13 m/s descent on an rpm schedule up to 668 rpm (1.30 x hover); pull-out in … | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[8].time_s` | 856 | 846 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[8].decision` | release window 63-60 km, descent < 16 m/s, battery > 90 % | release window 63-60 km, descent < 16 m/s, battery > 90 %, cos z >= 0.68 (planned relea… | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[9].name` | Descend at 3 m/s to the 55 km cruise level; begin air-mass-frame science loiter | Descend at 1.5 m/s with 3.5 m/s forward to the 55 km cruise level, on sunlight; begin a… | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[9].time_s` | 2856 | 4866 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[10].name` | Solar-sustained flight ~44 h, science dives to 51 km | Solar-sustained flight ~39 h, science dives to 52 km (abort above 52 °C) | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[10].time_s` | 6456 | 8466 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[11].name` | Sunset: final dive measuring through the lower cloud until battery empty/too hot | Sunset: final dive measuring through the lower cloud to about 50.4 km, where the batter… | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[11].altitude_km` | 47.3 | 50.4 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[11].time_s` | 179916 | 158586 | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `deployment_sequence[12].name` | No landing: unpowered fall with windmilling rotors (~12 h to the surface, < 1 m/s); ele… | No landing: unpowered fall with windmilling rotors (~13 h to the surface, 0.6 m/s at im… | K/Y | doc 25 §0 and §5.2; numbers from this run |
| `operations.mission_days` | 2.05 | 1.83 | K | venus_budget_update.fly, nominal, 6 Nov profile |
| `operations.solar_sustained_hours` | 44.2 | 38.7 | K | venus_budget_update.fly, nominal, 6 Nov profile |
| `operations.drift_distance_km` | 11546 | 10328 | K | venus_budget_update.fly, nominal, 6 Nov profile |
| `operations.release_hour_angle_deg` | -51.3 | -44.9 | K | venus_budget_update.fly, nominal, 6 Nov profile |
| `operations.events` | 7 rows | 11 rows | K | venus_budget_update.fly, nominal, 6 Nov profile |
| `operations.series_hourly` | 50 rows | 44 rows | K | venus_budget_update.fly, nominal, 6 Nov profile |
| `generated_by` | python scripts/venus_design.py | python 04_Venus/scripts/venus_variant_v07.py | - | file stamp |
| `generated_at` | 2026-11-04T23:09+03:00 | 2026-11-06T12:50+03:00 | - | file stamp |

**Event kinds.** The visual's enum has no `other` (`tests/test_venus_system.py`), so `cruise altitude reached` is kind `release` and `array no longer carries loiter` is kind `sunset`.

## sim_params.json: every changed value

30 changed values. Same list as JSON: `sim_params_changes.json`.

| Path | Old | New | Unit | Tag | Source |
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

## Promotion: only after the team says yes

One command, from the repo root:

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"; python 04_Venus/scripts/venus_variant_v07.py --promote --yes
```

Without `--yes` it prints the plan and writes nothing. It refuses if any baseline file differs from
`baseline_hashes_before.json`. It copies every file it will replace to
`outputs/versions/baseline_v0.6_before_v0.7_<stamp>/`, checks each copy by hash, anchors `design_v0.6_<hash>.json` as
`venus_design.py` does, copies the variant over the baseline, checks each copy by hash and writes
`promotion_manifest.json`. **It has not been run.**

