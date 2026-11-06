# B_00_index — Venus entry / descent / deployment precedents (master table)

Compiled 2026-11-04 for EUROAVIA Ideathon 2026 (LuGus "Fly on Venus", Q3: how does the rotorcraft get there).

**Tags:** [D-ag] = read in the source itself this session · [A] = only from abstract / catalogue summary / secondary · [calc] = my arithmetic from sourced numbers (formula given) · "—" = not found in any source read (do NOT fill from memory).
**Source keys** (one file each, same folder): SID = B_siddiqi2018 · SP461 = B_fimmel1983_sp461 · VS16/PR13 = B_venkatapathy2016_prabhu2013 · GIR = B_girija2023_probe_dataset · DAV = B_davinci · VAPS = B_vaps2018 · AERO = B_izraelevitz2025_aerobot · POST = B_jpl_aerobot_posters · VEGA = B_vega_balloon · LAN = B_landis_venus_airplane · YNG26 = B_young2026_venus_aerial · RWD = B_young2004_rwd_husseyin2016 · VAMP = B_vamp · ABR = B_abramovich1976_venera9_10 · V56 = B_venera56_tass1969

β convention: β = m/(C_D·A). Where a source gives only m and D, I give m/A [calc]; dividing by C_D ≈ 1.05 (45° sphere-cone, value used by PR13) gives β.

## 1. Flown entry probes and landers

| Mission (year) | Entry speed | EFPA | Entry mass / size | β (kg/m²) | Peak g | Heat shield | Parachute system | Descent duration | Landing speed / loads | Surface lifetime |
|---|---|---|---|---|---|---|---|---|---|---|
| **Venera 4** (1967) | 11 km/s [D-ag SID] | (−62,−78)° range V3–6 [D-ag VS16]; −80° [D-ag GIR] | lander 383 kg, ~1 m sphere [D-ag SID] | ~450 (V3–6) [D-ag VS16] | **300 g** "experienced", 300 g design [D-ag SID; V56 implies 300 g]; **500 g** [D-ag GIR] — conflict | "thick ablative heatshield" [D-ag SID] | deployed at 210 m/s [D-ag SID] | 93 min of data, lost at ~28 km (crushed) [D-ag SID] | not survived | none |
| **Venera 5** (1969) | 11.17 km/s [D-ag SID, V56] | (−62,−78) range [D-ag VS16] | 410 kg [D-ag SID]; 405 kg, ~1 m [D-ag V56] | m/A = 516 [calc 405/(π·0.5²)] | 450 g design [D-ag SID, V56] | — | main + drogue; main area "decreased by several factors"; canopy >500 °C; opened at 210 m/s [D-ag V56, SID] | 53 min on chute [D-ag V56]; 52.5 min data, lost ~18 km at 27 atm [D-ag SID] | not survived | none |
| **Venera 6** (1969) | 11.17 km/s [D-ag SID] | idem | 405 kg [D-ag SID] | as V5 | 450 g design | — | as V5 | 51 min, lost ~18 km [D-ag SID] | not survived | none |
| **Venera 7** (1970) | 11.5 km/s at 135 km [D-ag SID] | ~(−60,−77) V7–8 [D-ag VS16] | lander 490 kg [D-ag SID]; 1 m [D-ag VS16] | 422–500 [D-ag VS16] | — (DOU-1M accelerometer flown, value not given) | — | deployed 60 km at 200 m/s; probably tore/collapsed [D-ag SID] | ~35 min chute deploy→impact [calc from SID times 04:59:10→05:34:10] | **17 m/s** impact [D-ag SID] | 22 min 58 s [D-ag SID] |
| **Venera 8** (1972) | 11.6 km/s [D-ag SID] | ~(−60,−77) [D-ag VS16] | lander 495 kg [D-ag SID] | 422–500 [D-ag VS16] | **335 g** [D-ag SID] | shock-layer gas >12,000 °C [D-ag SID] | "upgraded"; entry braked to 250 m/s [D-ag SID] | — | soft landing (value —) | 50 min 11 s [D-ag SID] |
| **Venera 9** (1975) | 10.7 km/s (printed "km/hour", typo) [D-ag SID] | **−20°30′** [D-ag ABR]; design −20 to −23° [D-ag ABR] | entry sphere **1,560 kg, 2.4 m**; lander 660 kg [D-ag SID] | 139–170 [D-ag VS16]; but m/A = 345 for 1,560 kg [calc] — VS16 value matches 660 kg/(1.05·A) = 139 [calc], i.e. VS16 likely used lander mass | — | — | cover jettison ~65 km → drogue + chute pulling upper shell → 250→150 m/s → drag chute → 50 m/s → **3 mains, 180 m² total, at 62 km**; lower hemisphere off +4 s; ~20 min on mains; then free fall on **disc aerobrake** [D-ag SID] | entry→landing **74.5 min** [calc from ABR 06:53:50→08:08:23 MSK] | **~7 m/s**, crushable toroidal ring [D-ag SID] | 53 min (orbiter-relay limited) [D-ag SID] |
| **Venera 10** (1975) | — | (−18,−23) range [D-ag VS16] | 1,560 kg [D-ag SID] | as V9 | **168 g** [D-ag SID] | 12,000 °C shock [D-ag SID] | as V9 [D-ag SID] | — | — | **65 min** (design 30) [D-ag SID] |
| **Venera 11** (1978) | 11.2 km/s [D-ag SID] | (−18,−23) range | — | — | — | — | **3 chutes: 1.4, 6, 24 m²**; final chute jettisoned **46 km**; then circular airbrake with flaps [D-ag SID] | free fall 52 min 58 s [D-ag SID] | ~8 m/s [D-ag SID] | 95 min (relay-limited) [D-ag SID] |
| **Venera 12** (1978) | 11.2 km/s [D-ag SID] | (−18,−23) range | **1,645 kg** entry; **750 kg** landed [D-ag SID] | m/A = 364 (if 2.4 m) [calc] | — | — | as V11; release at 46 km [D-ag SID] | free fall 52 min 11 s [D-ag SID] | soft | **110 min** [D-ag SID] |
| **Venera 13** (1982) | — | (−18,−23) range | **1,643.72 kg** [D-ag SID] | — | — | — | — | ~1 h [D-ag SID] | **~7.5 m/s** [D-ag SID] | **127 min** (planned 32) [D-ag SID] |
| **Venera 14** (1982) | — | (−18,−23) range | 750 kg lander [D-ag SID] | — | — | — | main chute **63.5 km → released 47 km** [D-ag SID] | — | soft | 57 min [D-ag SID] |
| Venera 15/16 (1983) | orbiters only — no entry [D-ag SID] | | | | | | | | | |
| **Vega 1/2 landers** (1985) | ~11 km/s at 125 km [A PDS in VEGA] | (−18,−23) range [D-ag VS16] | descent module **1,500 kg** [D-ag SID] | — | — | — | cap chute 64 km (see balloon row) | — | — | 56 / 57 min [D-ag SID]; Vega-1 "20 minutes" [A PDS] — conflict |
| **Pioneer Venus Large** (1978) | **11.54 km/s** [D-ag PR13]; 11.6 [D-ag SID]; 41,800 km/h [D-ag SP461] | **−32.4°** [D-ag VS16, PR13]; −33.8° [D-ag DAV/Dutta23] | **316.5 kg**, **1.42 m** [D-ag PR13]; 315 kg, ~1.5 m [D-ag SP461]; Ti pressure vessel 73.2 cm | **188–190** [D-ag VS16, PR13]; m/A 200 [calc] | **276 g** [D-ag VS16]; 280 g [D-ag SP461] | 45° sphere-cone, **carbon phenolic** (FDCP) [D-ag SP461, PR13]; TPS fraction **13%** [D-ag VS16 chart] | mortar pilot → aft cover → **conical-ribbon** main; heat shield off **67 km**, chute released **47 km**; **17:07 min** on chute [D-ag SP461] | **54:21** entry→impact [D-ag SP461] | **32 km/h ≈ 8.9 m/s**, not designed to survive [D-ag SP461] | none |
| **PV North small** | ~11.7 km/s (42,000 km/h, all probes) [D-ag SP461] | **−68.7°** [D-ag VS16] | **90 kg**, 0.76 m [D-ag SID] / 0.8 m [D-ag SP461] | 190 [D-ag VS16]; m/A 198 (0.76 m) [calc] | **487 g** [D-ag VS16]; "458 g" steepest [D-ag SP461] | 45° cone, carbon phenolic, Ti aeroshell [D-ag SP461] | none | 53:00 [D-ag SP461/NMSU] | impact, no survival | none |
| **PV Night small** | idem | **−41.5°** [D-ag VS16] | 90 kg | 190 | **350 g** [D-ag VS16] | idem | none | 55:52 | impact | ~2 s [D-ag SP461] |
| **PV Day small** | idem | **−25.4°** [D-ag VS16] | 90 kg | 190 | **219 g** [D-ag VS16]; ~223 g [D-ag SP461] | idem | none | 55:41 | survived impact | **67:37** [D-ag SP461, SID] |

## 2. Vega balloons (1985) — the only flown aerial deployment
| Item | Value | Tag / source |
|---|---|---|
| Entry interface | 125 km, ~11 km/s | [A] PDS vega1_host.cat (VEGA) |
| Cap parachute opens → released | 64 km → 63 km (+15 s) | [A] VEGA |
| Balloon package extracted by parachute | 61 km (+40 s) | [A] VEGA; "61 km" also [D-ag SID] |
| Second chute opens, extracts furled balloon | 55 km, 200 s after entry | [A] VEGA |
| Balloon inflated (He); chute + inflation system jettisoned | +100 s, 54 km | [A] VEGA |
| Ballast dropped | ~50 km | [A] VEGA |
| Float reached | 53–54 km (mean 53.6 km, 535 mbar) 15–25 min after entry | [A] VEGA |
| Balloon / gondola | 3.5 m dia, 7 kg gondola | [D-ag VAPS] |
| Mass: balloon system vs floating | 121 kg vs 21 kg (payload/system 0.06) | [D-ag Cutts 1999 in VEGA]; ~20.8 kg [D-ag SID] |
| Lifetime / distance | 46.5 h [D-ag SID]; 46 h, 11,000 km [D-ag VAPS]; 11,600 km [A VEGA] | |
| Winds | ~69–70 m/s westward; downdrafts to 3.5 m/s, 2.5 km excursions | [A] VEGA (PDS + Science abstracts) |

## 3. Planned / studied systems
| System | Entry speed | EFPA | Mass / size | β | Peak g | TPS | Parachute / deployment | Descent | Landing | Surface | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **DAVINCI** (planned, launch slipped to ~2031) | **10.4 km/s** | **−6.3°** | ES 45° sphere-cone **2.24 m** (2023) / **2.54 m** approx (2026); DS **200 kg**, 0.87 m sphere, 0.98 m across drag plates | — (ES mass not found) | **32 g** | carbon–carbon (ACC) | pilot **DGB 1.8 m** at **Mach 0.8** (g-trigger + timer) → main **DGB 5.8 m** at ~70 km; heat shield off; main released ~32 min after AEI (145 km) | **59.7 min** ref (57.0–66.7 min 99%) | **18.7 m/s** (survival not required) | ~18 min possible | [D-ag DAV] (2023 values decoded from shifted font) |
| VITaL (decadal lander study) | 11.3 km/s | −23.35° | 2,102 kg (1,051 lander + 1,051 aeroshell), 3.5 m 45° | — | ≤200 g design | carbon phenolic | — | — | — | — | [D-ag VS16] |
| ADEPT-VITaL (deployable) | — | −8.5° | 6 m, 70° | 44 | 32 g | — | — | — | — | — | [D-ag VS16] |
| Rigid 45° 3.5 m (comparison) | — | −8.5° | 3.5 m | 208 | 48 g | — | — | — | — | — | [D-ag VS16] |
| JPL variable-altitude aerobot (2022 1/3-scale test; full scale ~12.5 m, 100 kg gondola) | — | — | prototype: ZP 5 m (Teflon-FEP/Kapton), SP 2.5 m (Vectran + TPU); balloon 21.3 kg, BCM 19.5 kg, gondola 7.0 kg | — | — | rigid aeroshell (VAPS) | **hanging inflation under parachute, ~10 min**, ZP slightly ahead of SP; zig-zag packing, extraction tested; deployment TRL 4 | — | float 52–62 km | goal 117 d | [D-ag AERO, POST, VAPS] |
| VAPS SP balloon (30 kg payload) | — | — | ~750 kg arrival; 7.4 m balloon carries 110 kg gondola | — | — | rigid | inflate after entry | — | 54 km | — | [D-ag VAPS] |
| Landis RASC Venus airplane | — | — | airplane 103 kg, 9 m span, folded in **3.7 m** aeroshell; entry 515 kg (670 kg w/ 30%) | — | — | Pioneer-scaled | chute **10%**, deployment mechanism **15%**, airplane **20%** of entry mass; small concept: unfold then **drop from chute at 65–70 km** | — | flies 65–75 km | — | [D-ag LAN] |
| Ames rotary-wing decelerator | — | — | 200 kg probe, 0.7 m pressure vessel, **3 × 0.42 m rotors** | — | — | — | release from aeroshell → boom/rotor deploy → spin-up → vortex-ring transition → autorotation | — | **8.5 m/s** design | — | [D-ag RWD] |
| VAMP (NG / L'Garde) | — | — | press: 55 m / 900 kg etc. [A] | **< 50 Pa** [A] | — | none (inflated in orbit) | deploys before entry | — | 50–60 km | months–1 yr [A] | [A VAMP], [D-ag VAPS] |

## 4. Gaps (not found in any source read this session)
- Venera heat-shield material and TPS mass fraction; Venera 9–14 aerobrake-disk diameter; Venera parachute diameters (only areas for V9 mains 180 m² total and V11 1.4/6/24 m²); peak g for Venera 7, 9, 11–14; EFPA per individual Venera after V9.
- DAVINCI entry-system mass (→ β) and DS–CRIS data rate except "≥ 36 kbps at touchdown" requirement (Dutta 2026 deck, in DAV).
- Gatto et al. 2024 (aerobot inflation sequence, Acta Astronautica 214:757–773) — PDF blocked (HTTP 403); Kremnev 1986 Science full text (paywall); NSSDCA catalogue pages (server unreachable from this machine).

## 5. Conflicts to cite explicitly
1. Venera 4 peak g: 300 g (SID; consistent with V56 "450 = 1.5 × Venera 4") vs 500 g (GIR).
2. PV Large EFPA −32.4° (VS16, PR13) vs −33.8° (Dutta 2023); peak g 276 vs 280; diameter 1.42 vs ~1.5 m; mass 316.5 vs 315 kg.
3. PV North peak g 487 (VS16) vs 458 (SP461).
4. Venera 9–Vega β: VS16 "139–170" corresponds to 660 kg lander, not 1,560 kg entry sphere (m/A 345) [calc].
5. Vega-1 lander surface time 56 min (SID) vs 20 min (PDS).
6. Landis small airplane aeroshell "1.2–1.3 m = PV small probe", but SP-461/SID give PV small probes 0.76–0.8 m.
7. Siddiqi typos: Venera 9 "10.7 km/hour"; Vega "two balloons each"; Venera 11 landing date.
