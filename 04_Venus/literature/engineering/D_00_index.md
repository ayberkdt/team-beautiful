# D_00_index — Engineering constants for the Venus rotorcraft (research batch D, 2026-11-04)

Tags: **[D-ag]** = read in the source itself this session; **[A]** = abstract/snippet/secondary
only; "derived" = my arithmetic on [D-ag] inputs. All downloads are in
`D:\tmp_ideathon\venus\downloads\eng\` (data only). Every number below is detailed, with its
page/table, in the per-source file named in the right-hand column.

## 1. Entry heating
| Item | Value | Tag | File |
|---|---|---|---|
| Sutton–Graves def. K = q̇·sqrt(R/p_s)/(h_s−h_w), K in kg/(s·m^1.5·atm^0.5) | eq.(33) | D-ag | D_sutton_graves_1971 |
| K air / CO2 / N2 | 0.1113 / 0.1210 / 0.1112 | D-ag (Table II) | same |
| **k (SI, q = k·sqrt(ρ/Rn)·V³): Earth 1.748e-4, Venus (96.5/3.5 vol) 1.897e-4, Mars 1.902e-4, pure CO2 1.901e-4 kg^0.5/m** | k = K/(2·sqrt(101325)) | derived | same |
| Venus radiative fit, 10.03–12 km/s: q_rad = 8.497e-63·V^18·ρ^1.2·r_N^0.49 W/m² | eq.(2a) | D-ag | D_tauber_venus_rad_2012 |
| Venus radiative fit, V < 10.03 km/s: 2.195e-22·V^7.9·ρ^1.2·r_N^0.49 W/m² | eq.(2b) | D-ag | same |
| PV large probe peak q_rad (r_N 0.363 m) | 2449 W/cm² @ 85.8 km, 10.88 km/s | D-ag | same |
| PV large probe coupled-ablation peaks | rad 2027 (2275 non-abl.) W/cm²; conv 1382 W/cm² | D-ag | D_cabrera_west_pv |
| Heritage q_max (rad+conv, engineering est.) | PV Large 6.9, PV North 10.6, Vega 3.06–3.29, Venera 9/10 3.0–3.4 kW/cm² | D-ag (Table 1) | D_dutta_2012_venus_entry |
| HEEET rigid 3.5 m (β 225–300, γ −10.5…−12.5°) | 1600–2100 W/cm², 55–75 g, 20–30 kJ/cm² | D-ag | D_venkatapathy_2017_venus_edd |
| ADEPT deployable (β 25–40, γ −8.5…−9.5°) | 350–400 W/cm², 35–45 g, 7.5–10 kJ/cm² | D-ag | same |
| HEEET tests | ~7000 W/cm² at 5 atm (seams); Venus heat loads 12–36 kJ/cm²; > 40 % lighter than CP | D-ag | D_heeet_ellerby_2016 |
| Tauber & Sutton 1991 | Earth + Mars (97 % CO2) only — **no Venus** | A (abstract) | D_tauber_sutton_1991 |

Key caveat: at Venus, radiative ≈ convective at peak for a ~0.36 m nose (my check: S-G gives
~2300 W/cm² vs radiative 2450 W/cm² at the PV peak point); always add both.

## 2. Materials vs sulfuric acid
| Item | Value | Tag | File |
|---|---|---|---|
| JPL aerobot outer envelope | Teflon FEP / Kapton bilaminate, Ag 2nd-surface mirror α 0.08 ε 0.52 | D-ag (via WebFetch) | D_jpl_aerobot_materials |
| JPL acid test | 96.2 % H2SO4, 100 °C, 63 N tension (ZP material & seams) — survived; no rates published | D-ag | same |
| Inner reservoir | Vectran 200 den + TPU bladder; 61 kPa test | D-ag (via WebFetch) | same |
| FEP, conc. H2SO4, 120 °C, 168 h | 95 % tensile, 98 % elongation retained, 0.0 % weight gain | D-ag (manufacturer) | D_fep_chemical_resistance |
| FEP & PP films, 75–85 % H2SO4, 30 d | transmittance change within 2 %; PVC fails | D-ag | D_havoc_2016_acid |
| Solar coupon, Parylene-coated, 96 % H2SO4 96 h | no corrosion, no power loss; coating cost 5 % | D-ag | D_jpl_solar_acid_2022 |
| CP titanium | conc. acid RT 1.57 mm/y; 75 % RT 10.8 mm/y; 96 % vapour 38–66 °C nil | D-ag (manufacturer) | D_timet_titanium_h2so4 |
| 316L-type (Alleima 3R60) | 90–98 %: < 0.1 mm/y at ≤ 30 °C; 0.1–1 mm/y at 40–50 °C; > 1 mm/y at 80 °C; 60–85 % mostly > 1 mm/y | D-ag (manufacturer) | D_alleima_steel_h2so4 |
| CFRP/epoxy in conc. H2SO4 | no usable primary data found (only 10–40 % acid studies) | A | (gap) |

## 3. Batteries
| Item | Value | Tag | File |
|---|---|---|---|
| Ingenuity: 6s Sony VTC4, 2.0 Ah, 273 g, 44.4 Wh (25 °C)/38.8 Wh (0 °C), 360 W cont / 510 W peak | → 163 Wh/kg cell-level (derived) | D-ag | D_jpl_m2020_ingenuity_battery |
| Ingenuity allowed flight temp | +10…+25 °C (high-rate discharge); charge −5…+25 °C | D-ag | same |
| Panasonic NCR18650B | 243 Wh/kg, 48.5 g; charge 0…45 °C (0.25C below 10 °C); discharge −20…60 °C | D-ag (manufacturer) | D_panasonic_ncr18650b |
| Saft LSH 20 Li-SOCl2 primary | 468 Wh/kg, 65 W/kg, −60…+85 °C, 1.8 A max continuous | D-ag (manufacturer) | D_saft_lsh20 |
| DAVINCI descent sphere | rechargeable Li-ion ~2400 Wh (primary was baselined then dropped) | D-ag | D_davinci_probe_arch |
| VLF balloon | LiCFx primary 450 Wh/kg + ~12 W body solar | D-ag | D_agrawal_2022_vlf |
| Saft VES16 | ~155 Wh/kg, op. +10/+40 °C | A (snippets) | (not filed) |

## 4. Solar
| Item | Value | Tag | File |
|---|---|---|---|
| 3J array (29 % AM0) power at overhead sun | 50 km 256 W/m² (9.8 % "effective"), 55 km 404 W/m² (15.5 %), 60 km 559 W/m² (21.4 %) | D-ag (Table 1) | D_landis_haag_2013_solar |
| Venus TOA intensity | 2600 W/m² (Landis), ~2622 W/m² (Grandidier) | D-ag | both |
| Limiting junction 10–60 km | middle (GaAs); Ge never limits → 2J ≈ 3J | D-ag | D_landis_haag_2013_solar |
| 2J GaInP/GaAs Voc vs T (1 sun) | 2.27 V @ 25 °C → 0.72 V @ 465 °C (≈ −3.5 mV/°C avg, derived) | D-ag | D_grandidier_2020_liht |
| Venus-optimal top cell | GaInP ~200 nm for 10–50 km | D-ag | same |
| Caveat | Landis cell temps ~30–40 K hotter than VIRA at 50–55 km (per sibling note A_seiff1985_vira) | — | — |

## 5. Communications
| Item | Value | Tag | File |
|---|---|---|---|
| VEGA balloon DTE | 1667.914 MHz, ~4.5 W, omni −3…0 dB, 4 bit/s; received −165…−162 dBm on 64 m dishes | D-ag | D_vega_balloon_tda1986 |
| DAVINCI DS → carrier | S-band adaptive data rate; 154 Mbit worst / 636 Mbit likely / 1.2 Gbit best over ~1 h | D-ag | D_davinci_probe_arch |
| VEVA sonde → gondola UHF | 400 MHz, 1 W, 1 dBi/1 dBi, 200 km, 500 kbps; "100 kbps–2 Mb/s" with omni | D-ag | D_veva_cutts_1999 |
| VLF balloon relay | S-band 2.4 GHz crossed dipole; 6-h orbit; ~16 passes × 8–10 min per circumnavigation; 250 MB/14 d relay vs 25 MB DTE at 100 bps | D-ag | D_agrawal_2022_vlf |
| VAPS 2018 | relay orbiter circular equatorial preferred | D-ag | D_vaps_2018 |
| X-band absorptivity (Akatsuki RO) | ≈ 0.005 dB/km at 50 km, ~0 above 53 km, 0.07 dB/km at 42.5 km | D-ag (read off Fig. 6) | D_venus_microwave_absorption |
| UHF/S-band dB/km at 50–60 km | **not found** — Kolodner & Steffes 1998 gives S/X opacity laws (abstract only) | A | same |

## 6. Motors / electronics / thermal
| Item | Value | Tag | File |
|---|---|---|---|
| NdFeB max working temp | N 80, M 100, H 120, **SH 150**, UH 180, EH 200, AH 230 °C; N50/N52 only 60 °C | D-ag (manufacturer) | D_eclipse_magnets |
| SmCo | Sm2Co17 ~300 °C, H-grades 350 °C | D-ag (manufacturer) | same |
| AEC-Q100 grades (ambient) | G0 −40…150, **G1 −40…125**, G2 −40…105, G3 −40…85 °C | D-ag | D_aec_q100 |
| Gondola thermal precedents | DAVINCI: evacuated Ti sphere, 1-inch MLI, Be decks, internal −30…+50 °C; VLF: passive control adequate for 48–60 km | D-ag | D_davinci_probe_arch, D_agrawal_2022_vlf |

## 7. Navigation without GNSS
| Item | Value | Tag | File |
|---|---|---|---|
| VEGA VLBI | 20 telescopes; goals 15 km / 1 m/s; VEGA-2 max error < 24 km; altitude from pressure | D-ag | D_vega_balloon_tda1986 |
| VEVA | ranging + phase + altitude → ~10 km; sun sensor for re-acquisition | D-ag | D_veva_cutts_1999 |
| VAPS 2018 | no star sightings in cloud; Sun better than 10° "may be impractical"; no magnetic field; < 100 m localisation possible but ~30 % of time | D-ag | D_vaps_2018 |
| Ingenuity (comparison) | IMU 1600/3200 Hz, LRF 50 Hz, nav cam 30 Hz, 21-state EKF; drift 1–2 % (demos), 2–6 % (scouting); terrain-relative VIO — not usable above Venus clouds | D-ag | D_delaune_2021_ingenuity_nav |

## Gaps / not done
- Venus Flagship Mission Study 2009 not read.
- No official Chemours PTFE/PFA chart; no CFRP-in-concentrated-acid data; no parylene-only
  long-term data beyond the 96 h JPL coupon.
- No numeric UHF/S-band absorption at 50–60 km.
- Hall et al. 2021 AIAA aerobot paper not accessed (posters + JoA 2025 preprint used instead).
- Suspicious printed values flagged in files: DAVINCI "500 Mbps" fixed rate; VEVA "153 W" and
  "1.46e6 km".
