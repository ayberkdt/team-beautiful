# R_00_summary — Advionics ATC surveillance research: key numbers and test vectors

Compiled 2026-11-04 by the research agent from the R_*.md files in this folder. Every value below was read this session from the source named in the last column. "[C-ag]" marks an agent cross-check computation, which is not a source. Values are copied verbatim; nothing has been rounded.

## Files in this folder
| File | Source | Class |
|---|---|---|
| R_1090_riddle.md | Sun, *The 1090 MHz Riddle* 2nd ed., mode-s.org/1090mhz | primary textbook (TU Delft OPEN) |
| R_atcrbs_wiki.md | Wikipedia "Air traffic control radar beacon system" | secondary |
| R_ssr_wiki.md | Wikipedia "Secondary surveillance radar" | secondary |
| R_gillham_wiki.md | Wikipedia "Gillham code" (decoding section disputed) | secondary |
| R_eurocontrol_modeS_IC.md | EUROCONTROL, Principles of Mode S Operation and Interrogator Codes, Ed 2.3, 2003 | primary (draft) |
| R_esassp.md | EUROCONTROL-SPEC-147 ESASSP Vol 1, Ed 1.3, 21/03/2024 | primary |
| R_eurocontrol_radar_std_1997.md | EUROCONTROL Radar Surveillance Standard SUR.ET1.ST01.1000-STD-01-01, 1997 | primary (superseded by ESASSP for system level) |
| R_faa_order_1812_8_arsr4.md | FAA Order 1812.8, ARSR-4 requirements | primary |
| R_asr_wiki.md | Wikipedia "Airport surveillance radar" | secondary |
| R_radar_eq_swerling_wiki.md | Wikipedia "Radar" (range equation) and "Fluctuation loss" | secondary |
| R_eurocontrol_wind_turbines.md | EUROCONTROL-GUID-130, Ed 1.2, 2014 | primary |
| R_icao_suricg7_ip14_wam.md | ICAO APAC SURICG/7 IP/14 (China), 2022, WAM test | State paper (measured values) |
| R_mlat_wiki.md | Wikipedia "Pseudo-range multilateration" | secondary |
| R_eurocontrol_artas_asterix.md | EUROCONTROL ARTAS page, ASTERIX page, Category status list 22/10/2025 | primary |
| R_blom_imm_atc.md | Blom, Yang, Bar-Shalom, IMM in ATC (short paper) | primary-ish (by the inventors) |
| R_alpha_beta_wiki.md | Wikipedia "Alpha beta filter" | secondary |
| R_eurocontrol_stca_spec.md | EUROCONTROL-SPEC-0108 STCA, Ed 1.0, 2007 | primary |
| R_ils_wiki.md | Wikipedia "Instrument landing system" | secondary |
| R_faa_aim_ch1.md | FAA AIM Ch 1 Sec 1 (ILS 1-1-9, WAAS 1-1-18, GBAS 1-1-19) | primary (US) |
| R_par_enri_soumu.md | ENRI (Japan) PAR overview, summarising ICAO Annex 10 Vol I 3.2.3 | secondary summary |
| R_lpv_par_wiki.md | Wikipedia "Localizer performance with vertical guidance" and "Precision approach radar" | secondary |
| R_14cfr_91_227_adsb.md | 14 CFR § 91.227 ADS-B Out performance | primary (US) |

## Key numbers: approach-area surveillance must reach ≤ 5 s update, ≤ 300 m RMS (3 NM) and ≤ 200 m RMS (2.5 NM)
Grouped in signal-chain order (signal → sensor → system → tracker → display → approach aid), not alphabetically.

| Quantity | Value | Unit | Source file |
|---|---|---|---|
| SSR interrogation / reply frequency | 1030 / 1090 | MHz | R_ssr_wiki, R_1090_riddle |
| Mode A / Mode C P1–P3 spacing | 8 / 21 | μs | R_ssr_wiki, R_atcrbs_wiki, R_1090_riddle |
| P2 (SLS) after P1 | 2 | μs | R_ssr_wiki, R_atcrbs_wiki |
| Interrogation pulse width | 0.8 | μs | R_atcrbs_wiki, R_1090_riddle |
| Reply F1–F2 spacing | 20.3 | μs | R_atcrbs_wiki, R_1090_riddle |
| Reply slot pitch / pulse width | 1.45 / 0.45 | μs | R_atcrbs_wiki |
| SPI after F2 | 4.35 | μs | R_atcrbs_wiki |
| Transponder reply delay | 3.0 | μs | R_atcrbs_wiki |
| Typical SSR interrogation rate | 450–500 | per s | R_atcrbs_wiki |
| Mode A codes / Mode S addresses | 4096 / 16,777,216 | — | R_1090_riddle, R_eurocontrol_modeS_IC |
| Mode S reply preamble / bit period | 8 / 1 | μs | R_1090_riddle |
| Mode S frame length short / long | 56 / 112 | bit | R_1090_riddle |
| CRC-24 generator | 0x1FFF409 (= 0xFFF409 + x^24) | — | R_1090_riddle |
| CPR N_Z | 15 | — | R_1090_riddle |
| CPR local-decoding reference radius (airborne / surface) | 180 / 45 | NM | R_1090_riddle |
| Global CPR pair window | 10 | s | R_1090_riddle |
| ADS-B v2 airborne position / velocity rate | 2 / 2 | Hz | R_1090_riddle |
| Mode S all-call lockout | 18 | s | R_eurocontrol_modeS_IC |
| II-Codes / SI-Codes | 16 / 63 | — | R_eurocontrol_modeS_IC |
| SSR range accuracy: standard / monopulse / Mode S | 230 / 13 / 7 | m rms | R_ssr_wiki |
| SSR sensor Pd (1997 standard) | > 97 | % | R_eurocontrol_radar_std_1997 |
| SSR random error σ range / azimuth | < 70 / < 0.08° | m / deg | R_eurocontrol_radar_std_1997 |
| PSR sensor Pd (1997 standard) | > 90 | % | R_eurocontrol_radar_std_1997 |
| PSR false reports per scan | < 20 | — | R_eurocontrol_radar_std_1997 |
| PSR random error σ range / azimuth | < 120 / < 0.15° | m / deg | R_eurocontrol_radar_std_1997 |
| Tracker scenario antenna revolution: TMA / en route | 4 / 12 | s | R_eurocontrol_radar_std_1997 |
| Display update: TMA / en route (1997) | ≤ 5 / ≤ 8 | s | R_eurocontrol_radar_std_1997 |
| ASR-9: band / rotation / range | 2.7–2.9 GHz (US PSR) / 4.8 s (12.5 RPM) / 60 NM | — | R_asr_wiki |
| ARSR-4: band / scan / range | 1,215–1,400 MHz / 12 ± 0.1 s / 5–250 NM | — | R_faa_order_1812_8_arsr4 |
| ARSR-4 detection, Swerling I 1 m² | 165 | NM | R_faa_order_1812_8_arsr4 |
| ESASSP 5 NM: MI / RMS / PU | ≤ 8 s / ≤ 500 m / ≥ 97 % | — | R_esassp |
| ESASSP 3 NM: MI / RMS / PU | ≤ 5 s / ≤ 300 m / ≥ 97 % | — | R_esassp |
| ESASSP 2.5 NM final approach: MI / RMS / PU | ≤ 5 s / ≤ 200 m / ≥ 99 % | — | R_esassp |
| ESASSP non-cooperative only PU (5 / 3 NM) | > 90 | % | R_esassp |
| Wind turbine safeguarding / detailed zone PSR / SSR | 500 m / 15 km / 16 km | — | R_eurocontrol_wind_turbines |
| WAM / ADS-B / Mode S radar measured accuracy (Chengdu final) | 6–7 / ~20 / ~200 | m | R_icao_suricg7_ip14_wam |
| ADS-B NACp 8 EPU | < 93 (0.05 NM) | m | R_1090_riddle, R_14cfr_91_227_adsb |
| US ADS-B Out minimum: NACp / NIC / SIL | < 0.05 NM / < 0.2 NM / ≤ 1e-7 | — | R_14cfr_91_227_adsb |
| ADS-B total / uncompensated latency | ≤ 2.0 / ≤ 0.6 | s | R_14cfr_91_227_adsb |
| ARTAS nominal capacity | 30 sensors / 4,096 tracks | — | R_eurocontrol_artas_asterix |
| ARTAS share of European flights | close to 90 % at 43 ACCs | — | R_eurocontrol_artas_asterix |
| STCA warning time horizon | up to 2 | min | R_eurocontrol_stca_spec |
| ILS LOC band (40 channels) | 108.10–111.95 | MHz | R_faa_aim_ch1, R_ils_wiki |
| ILS GS allocated channels / band | 329.15–335.00 / 328.6–335.4 | MHz | R_faa_aim_ch1 / R_ils_wiki |
| ILS tones | 90 and 150 | Hz | R_ils_wiki |
| GS angle / beam width | 3° / 1.4° | deg | R_faa_aim_ch1 |
| LOC course width at threshold | 700 | ft | R_faa_aim_ch1 |
| CAT I DH (ICAO/EASA) | ≥ 60 m (FAA ≥ 200 ft) | — | R_ils_wiki |
| LPV HAL / VAL (LPV-200) / VAL (≥ 250 ft) | 40 / 35 / 50 | m | R_faa_aim_ch1 |
| GBAS ground reference stations | ≥ 4 | — | R_faa_aim_ch1 |
| PAR coverage / sector (Annex 10 summary) | ≥ 9 NM / AZ 20°, EL 7° | — | R_par_enri_soumu |
| PAR accuracy EL / AZ | 0.4 % R + 10 % offset / 0.6 % R + 10 % offset | — | R_par_enri_soumu |
| PAR example frequency / update | 9080 ± 80 MHz / ≤ 1 s | — | R_par_enri_soumu |

Reading: for the approach phase, ESASSP's 2.5 NM column (≤ 5 s, ≤ 200 m RMS, ≥ 99 % PU, zero long gaps) is the bar. The measured WAM (6–7 m) and ADS-B (~20 m) figures clear it easily; the measured Mode S radar figure (~200 m) sits right at the limit.

## Test vectors (character-exact, from R_1090_riddle.md unless noted)
| # | Message (hex) | Expected | Page |
|---|---|---|---|
| T1 | `8D4840D6202CC371C32CE0576098` | DF17, CA5, ICAO 4840D6, TC4, category 0, callsign `KLM1023_` | ads-b/1-basics, 2-identification |
| T2 | even `8D40621D58C382D690C8AC2863A7` (t0=1457996402, newer) + odd `8D40621D58C386435CC412692AD6` (t1=1457996400) | j=8; lat_even 52.25720214843750; lat_odd 52.26578017412606; NL 36; m=0; lon 3.91937255859375 | ads-b/3-airborne-position |
| T3 | `8D40621D58C382D690C8AC2863A7`, ref (52.258, 3.918) | lat 52.2572021484375, lon 3.91937255859375 | same |
| T4 | `8D40621D58C382D690C8AC2863A7` | altitude 38000 ft (Q=1, N=1560) | same |
| T5 | `8D485020994409940838175B284F` | GS 159.20 kt (pyModeS 159), track 182.88°, VS −832 ft/min, GNSS−baro +550 ft | ads-b/5-airborne-velocity |
| T6 | `8DA05F219B06B6AF189400CBC33F` | TAS 375 kt, heading 243.98°, VS −2304 ft/min | same |
| T7 | `8C4841753AAB238733C8CD4020B1` (t0=1457996410) + `8C4841753A8A35323FAEBDAC702D` (t1=1457996412), ref (51.990, 4.375) | 52.320607, 4.734735 | ads-b/4-surface-position |
| T8 | `8C4841753A9A153237AEF0F275BE`, ref (52.320607, 4.734735) | 52.320561, 4.735735; 17 kt; track 92.8125° | same |
| T9 | `8D406B902015A678D4D220AA4BDA` | CRC of data = AA4BDA; full CRC 0 | ads-b/8-error-control |
| T10 | `8D4CA251204994B1C36E60A5343D` | CRC remainder 16 (corrupt) | same |
| T11 | `A0001838CA380031440000F24177` | ICAO 3C6DD0 (payload CRC CE2CA7) | mode-s/1-basics |
| T12 | `5D484FDEA248F5` | DF11, CA5, AA 484FDE, II/SI 22 | mode-s/2-allcall |
| T13 | `2000171806A983` | 36000 ft (DF4, Q=1, not Gillham) | mode-s/3-surveillance |
| T14 | `2A00516D492B80` | squawk 0356 | mode-s/3-surveillance |
| T15 | `A000083E202CC371C31DE0AA1CCF` | BDS 2,0 callsign `KLM1017_` | mode-s/6-els |
| T16 | `A0000638FA81C10000000081A92F` | BDS 1,7 caps: 05 06 07 08 09 20 40 50 51 52 60 | mode-s/6-els |
| G1–G44 | Gillham 12-bit [D1 D2 D4 A1 A2 A4 B1 B2 B4 C1 C2 C4], e.g. `000 000 011 010` → 0 ft; `000 000 000 001` → −1200 ft; `000 000 111 100` → 1300 ft; `000 000 100 001` → 2700 ft; `010 000 000 001` → 126700 ft | full table in R_gillham_wiki.md | Wikipedia "Gillham code" |

Cross-checks [C-ag]: an inline Python run on 2026-11-04 reproduced T1–T4, T5 (−8/−159 → 159.201 kt, 182.880°), T6, CRC = 0 for T1–T9 and the surface frames, 16 for T10, T11, T12 (0x16), T13 (Q=1, 36000), T14 and T15. The 1090 Riddle Gillham algorithm matched 12/12 sampled rows of the Wikipedia table.
Book typos to encode correctly: T5 prints "(−9, −160)" where the inputs should read (−8, −159). T6 prints TC "5"; the correct value is 19. T8's pyModeS output repeats T7's result; use the hand-computed 52.320561, 4.735735. In T7 the book's prose says the "even" frame is most recent, but the odd frame (t1) is.

## Open gaps (not verified this session)
- ICAO Annex 10 Vol IV and Vol I and EUROCAE ED-117A/ED-142/ED-129 are paywalled, so their normative values were not read. MLAT accuracy limits come only from a measured test (IP/14).
- ESASSP Ed 2.0 (proposed, 2026-06) was not read; Ed 1.3 values may change.
- GBAS numeric alert limits, MSAW parameters and a standard data-block layout were not found in a primary source.
- Table rule check: the datawiz-tablo rules were applied by hand (title above the table states the finding; natural order; units in their own column; no rounding because values are verbatim). The `tablo.denetle` script was not run, because the table is text-valued and the task restricts writes to this folder.

## Relevance to us [Y]
This page is the single place to look for slides and unit tests. The test vectors drive the decoder tests, and the ESASSP 2.5 NM / 3 NM rows define what "good enough" means for an automated approach guidance concept.
