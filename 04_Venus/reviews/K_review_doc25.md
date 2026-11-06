# K_review_doc25 — independent fact-check of `04_Venus/docs/25_lugus_venus_rotorcraft.md` (4 Nov 2026)

Scope: every [D-ag] statement and every untagged factual claim about a mission, paper, dataset or product in doc 25,
checked against the notes in this folder (`A_*`, `B_*`, `C_*`, `D_*`, `K_*`, indexes). [K] numbers spot-checked against
`04_Venus/outputs/result.json`, `design.json`, and also `out/sensitivity.json`, `out/trade_sizing.json`,
`out/vesper_for_simulator.json` (all read in this check). No web access; no other file edited.
Line numbers = `04_Venus/docs/25_lugus_venus_rotorcraft.md` as read on 4 Nov 2026.

**Result: 116 claims checked — 84 OK, 32 not OK** (4 WRONG, 9 UNSUPPORTED, 1 A-only, 12 ROUNDING, 6 CONTRADICTION).
Rows 1–9 are the ones that change meaning; rows 10–32 are lower impact.

## Not OK

| # | doc line/section | claim as written | what the note/JSON says (file + quote ≤ 15 words) | verdict | suggested correction |
|---|---|---|---|---|---|
| 1 | l.65, §3 (tag [D]) | PV probes "(4.4°N–59.3°N, 00–08 h local time, Dec 1978)" | `A_pv_probes_seiff1980_pds.md` metadata: "Day \| 31.3 S" … "Night \| 28.7 S" (also `A_counselman1980…`: "Day 31.3S \| Night 28.7S") | WRONG | "31.3°S–59.3°N (\|lat\| 4.4–59.3°)". The same error is in `A_00_index.md` ("4.4°N–59.3°N") and in the A_pv note's own Result paragraph, so fix those as well |
| 2 | l.117, §4.2 | "Design rules from MSH [D-ag]: C_T/σ = 0.10 at hover" | `C_johnson2020_msh.md`: "C_T/σ = 0.11 initial (10 % above MH), later 0.115" | WRONG | "MSH: C_T/σ 0.11 → 0.115 (≈0.10 implied for Ingenuity)". If VESPER uses 0.10, tag it [Y] |
| 3 | l.211, §4.9 | "The Landis 9 m-span airplane fit the same shell with two folds per wing [D-ag]" | `B_landis_venus_airplane.md`: RASC airplane: "Span 9 m"; "Folded into a 3.7 m diameter aeroshell". It gives no fold count. "Wing folds in two places" refers to the *small* concept (1.2–1.3 m shell) | WRONG (misattributed; also "per wing" ≠ "in two places") | "The Landis 9 m-span airplane fit a 3.7 m aeroshell [D-ag]; Landis's smaller concept folded its wing in two places [D-ag]". Fix `design.json` `vehicle.stowed.fits` too |
| 4 | l.143, F8 caption | "BEMT predicts measured rotor torque within ±10 % (rms 6.3 %)" | `result.json` `bemt_validation.max_abs_error_hover_range` = 0.2067. Point 16 (K&H 5-blade, θ 4°): measured 0.000198, predicted 0.000239 (+20.7 %) | CONTRADICTION ([K] vs [K]) | "rms 6.3 %; 26 of 27 points within ±10 % (worst +21 %, 5-blade θ 4°)" |
| 5 | l.290–292, §7 (also `K_entry_crosschecks.md`, R9) | rigid 3.5 m, β 208, −8.5°: "29 vs 48 g; Venkatapathy 2016 via agent" → "1.7× lower … unresolved" | `B_venkatapathy2016_prabhu2013.md`: "column-to-label mapping garbled by text extraction". The other column reads 23 g | UNSUPPORTED (the source reading itself is uncertain) | State that the 48 g value comes from a garbled slide extraction (the alternative column is 23 g), so the "1.7× discrepancy" may be an extraction artefact. Re-read slide ~32 as an image before keeping the factor 1.7 |
| 6 | l.21, 34, 238, 290 (VESPER 56 g at β 25, −9.5°) | the narrative says our shallow-entry g is *lower* than or matches published cases | `D_venkatapathy_2017_venus_edd.md`: "ADEPT deployable … β 25–40 … −8.5…−9.5° … 35–45 g". `D_dutta_2012_venus_entry.md`: β≈30, γ≈−10° gives "~50–60 g" (contour read) | CONTRADICTION (relevant source not cited) | Add: "Venkatapathy 2017 gives 35–45 g for β 25–40 at −8.5…−9.5° (ours is higher, 56 g); Dutta 2012 contours give 50–60 g at β 30, −10° (consistent)" |
| 7 | l.25 (TR), l.122, l.278 F10, l.24 | "every adverse case closes and still flies ≥ 44 h" / "keeps ≥ 44 h" | `sensitivity.json` robustness, geared 2.6 m, "cells 180 Wh/kg": `flight_h` 43.77 | ROUNDING | "≥ 43.7 h" or "~44 h" (not "≥ 44") |
| 8 | l.76, §3 (also `result.json` R3, `design.json` lower cloud 75–98) | "droplets of 75–98 wt% H₂SO₄ (Titov 2018) [D-ag]" | `A_titov2018_clouds.md`: data "consistent with 75–90 wt%"; "98 % at cloud bottom (~48 km)" is a Krasnopolsky **model**. `design.json` middle cloud = 75–90 | ROUNDING (model value merged with observations; contradicts design.json for the 50.5–56.5 km layer) | "75–90 wt% observed (Titov 2018); model up to 98 % at the ~48 km cloud base" |
| 9 | l.151–152, §4.3 (also R6) | rpm control "too slow for Hz-level attitude control by differential thrust, which the MSH study flagged for large rotors [D-ag]" | `C_johnson2020_msh.md` Table 5 is about flap frequency: coax "1.537/rev = 32.1 Hz … large coaxial is hard to make controllable". Nothing about rpm/differential-thrust response | UNSUPPORTED (misattribution) | Make the rpm-response point [K] only; cite MSH only for "low flap frequency of a large coaxial vs control bandwidth" |
| 10 | l.78–79, l.189, `design.json` | "downdraft episodes 2–4 m/s for 1–2 h [D-ag]" | Only the synthesis in `A_00_index.md` ("2–4 m/s, lasting ~1–2 h") says this. The per-source `A_vega1985_balloons_lander.md` gives the largest event "W_a −2 to −3.3 m/s … recovered over ~4 h"; "3.5 m/s" is [A] (Sagdeev abstract); Blamont "maxima 4–5 m/s" "may be lower" | UNSUPPORTED (index synthesis; not in any per-source note) | "largest VEGA-2 event: −2…−3.3 m/s, ~2 h down, ~4 h recovery [D-ag data]; up to 3.5 m/s [A]" |
| 11 | l.186, §4.7 | "VEGA-like turbulence (σ 0.7 m/s, 80 s correlation [D-ag statistics])" | No note gives a correlation time. Closest are "30–130 s periods" (horizontal) and "cell sizes … (60 s scale)" (`A_vega1985…`) | UNSUPPORTED | Tag 80 s [Y] ("chosen within the 30–130 s band") |
| 12 | l.80, §3 | "60 ± 10 m/s (Venus Express)" (listed next to 53–54 km) | `A_winds_cloudtracking_vex_akatsuki.md`: "1.74 µm, night \| ~47 km \| −60 ± 10 m/s"; at ~61 km "−62 ± 10" | ROUNDING (altitude condition dropped) | "60 ± 10 m/s at ~47 km and 62 ± 10 m/s at ~61 km (VEX/VIRTIS 2006–07)" |
| 13 | l.193, §4.7 | Sun fixes inside clouds "may be impractical" (VAPS [D-ag]) | `D_vaps_2018.md`: "locating the Sun to better than 10° may be impractical" | ROUNDING (qualifier dropped; changes meaning) | "Sun direction better than 10° 'may be impractical' (VAPS)" |
| 14 | l.109, §4.1 | "Syal 2008 ideal 1.27 [D-ag]" | `C_syal2008_coaxial.md` Table 2.1: "1.2808" (equal thrust), "1.2657 (minimum)" (torque balance) | ROUNDING | "Syal 2008 ideal 1.27–1.28 (1.266 torque-balanced, 1.281 equal thrust)" |
| 15 | l.109, §4.1 | MSH found a large coaxial "hard to make controllable" (in quotes) | `C_johnson2020_msh.md`: "Conclusion: a large coaxial is hard to make controllable on Mars" — the agent's summary line, not marked as verbatim | UNSUPPORTED (as a quotation) | Drop the quotation marks, or have someone check the TM wording |
| 16 | l.56, §2 | entry integrator "vs Allen–Eggers (≤ 3 %)" | `K_entry_crosschecks.md`: within 3 % only at −30°/−45°; "at −10° … 56 g … 31 g … expected disagreement" | ROUNDING (condition dropped) | "vs Allen–Eggers at steep angles (−30°, −45°: ≤ 3 %)" |
| 17 | l.247, F3 caption | "Pioneer Venus' steep entry reached ~290 g" | `B_fimmel1983_sp461.md`: "Peak deceleration 280 g"; `B_venkatapathy…`: Large 276 g. 288 g is *our model* (`result.json` `pv_peak_g` 288.4) | CONTRADICTION (model value given as flight fact; l.21/238 correctly say 280 g) | "Pioneer Venus' steep entry: 280 g (SP-461); our model gives 288 g" |
| 18 | l.251, §5 | Vega balloons "inflated at 54 km within ~5 min of entry" [D-ag] | `B_vega_balloon.md`: PDS catalog tagged "[A — authoritative NASA archive summary …]"; the note also says the catalog is "internally a little loose" | A-only | Tag [A]. Keep "extracted at 61 km" [D-ag] (Siddiqi) |
| 19 | l.250, §5 | Venera 9–14 parachutes "opened at ~62–65 km and were dropped at 46–47 km" | `B_siddiqi2018.md`: drop altitudes only for V11/12 ("46 km") and V14 ("47 km"); V9 mains at 62 km, "~20 min on mains" (no drop altitude); V10/13 not given | ROUNDING (generalised from 3 of 6 landers) | "opened at 62–65 km (V9, V14); released at 46–47 km (V11, V12, V14)" |
| 20 | l.238, §5 | "18 W/cm² radiative (Tauber 2012 [D-ag])" for the 3.7 m capsule | `D_tauber_venus_rad_2012.md`: "Fit anchored to a single trajectory/nose radius (0.363 m)"; large nose radii "outside the fitted range" | UNSUPPORTED (applied outside the source's condition; V 10.78 km/s is inside 10.03–12) | Add "extrapolated in nose radius beyond the 0.363 m fit point" next to the 18 W/cm² |
| 21 | l.47, §2 | "four research agents read the primary PDFs" | e.g. `B_siddiqi2018.md` "authoritative but secondary"; `B_vega_balloon.md` PDS "[A]"; `C_ingenuity_jpl.md` "via fetch-tool extraction"; `D_fep…` distributor sheet | ROUNDING (overclaim) | "read the sources listed in each note (primary where obtainable; secondary/[A] marked in the notes)" |
| 22 | l.282, l.347 vs l.30, l.134 | "Re ~2×10⁵" vs "Reynolds 1.7×10⁵" | `result.json` `vehicle.re75` = 174 569 | CONTRADICTION (minor rounding) | Use "1.7×10⁵" everywhere |
| 23 | l.138, l.183 | max airspeed "~23 m/s" | `vesper_for_simulator.json` `max_airspeed_m_s` = 24.0 | CONTRADICTION (minor) | Align the two (say which one `control.max_airspeed` returns) |
| 24 | l.163 vs l.284 vs l.331; `design.json` | Sun circles the air mass in "~6.5 Earth days", night "77 h" (l.284) vs night "78 h" (l.331) | `design.json` `operations.circumnavigation_days` = 6.79; `result.json` hybrid `night_energy_Wh` 1950 at 25 W = 78 h | CONTRADICTION (minor; 6.79 d is probably the circumnavigation, 6.5 d the solar period relative to the air mass) | Label the two quantities in design.json/doc; use one night length (77 or 78 h) |
| 25 | l.157, §4.4 | "Parylene + FEP cover (−5 % [D-ag])" | `D_jpl_solar_acid_2022.md`: "5 % power loss from the coating" on a Parylene-coated coverglass coupon; FEP was not in that test | ROUNDING (condition) | "Parylene coat −5 % (JPL coupon); FEP cover loss not measured [Y]" |
| 26 | l.312, §7 | "NASA Ames 2026: the biggest challenge for Venus aircraft [D-ag]" | `B_young2026_venus_aerial.md`: "biggest technical challenge" stated for ATC (above-cloud) flyers | ROUNDING (scope widened) | "…for above-cloud Venus aircraft" |
| 27 | l.263, §6 | "VEGA's 11 600 km in 46 h [D-ag]" | `B_siddiqi2018.md`: "46.5 h, ~11,600 km"; `B_vaps2018.md`: "46 h … 11,000 km" | ROUNDING (two sources mixed) | "11 600 km in 46.5 h (Siddiqi)" |
| 28 | l.350, §9 | "FEP/PFA … (0 % uptake at 120 °C [D-ag])" | `D_fep_chemical_resistance.md`: FEP only; PFA "similar to PTFE" is qualitative/[A] | ROUNDING (minor) | "FEP 0 % uptake at 120 °C" |
| 29 | l.193, §4.7 | "Venus' 2.99×10⁻⁷ rad/s rotation" | not in any note (§2 lists only GM of Venus/Sun as session-read). Arithmetic matches a 243-day sidereal rotation — not verified in a source here | UNSUPPORTED (no source in the notes) | Cite JPL SSD (if the session read it) or tag [Y] |
| 30 | l.96, l.100 | latitude flight times 49/48/44/32 h; direct-drive "9.3 kg of motors" | not present in `result.json`, `sensitivity.json` or `design.json` | UNSUPPORTED (not reproducible from the named outputs) | Name the command/file that produced them |
| 31 | l.118, §4.2 | "Trade over 72 closed designs" | `trade_sizing.json`: 72 rows, 69 with `converged: true` | WRONG | "72 designs (69 closed)" |
| 32 | l.238, §5 | "Sutton–Graves, k = 1.897×10⁻⁴ [D-ag]" | `D_sutton_graves_1971.md`: k is "[derived from D-ag; composition … not re-verified]"; p_s≈ρV² makes "k a few % lower" in reality | UNSUPPORTED as [D-ag] (agent-derived constant, not printed in TR R-376) | Tag "[K from D-ag K=0.1210/0.1112, eq. 44]" and note the ~few % Newtonian approximation |

## OK

| # | doc line/section | claim as written | what the note/JSON says (file + quote ≤ 15 words) | verdict | suggested correction |
|---|---|---|---|---|---|
| 33 | l.43 | NIST CO₂ Cp, μ, k, a 225–400 K | `K_nist_co2_properties.md`: 0.1 MPa table 225–400 K | OK | — |
| 34 | l.46 | VIRA not obtained (ADS 403/CAPTCHA, NTRS none) | `A_seiff1985_vira.md`: "HTTP 403"; "CAPTCHA"; NTRS "no downloadable file" | OK | — |
| 35 | l.51 | Knight & Hefner "20 printed points" | `result.json`: 20 K&H points; values match `C_knight_hefner1937.md` Tables I–IV ÷2 | OK | — |
| 36 | l.52 | Harrington rotor 1 cd₀ from printed zero-thrust torque | `C_harrington1951.md`: "C_Q0 … = 0.0000777"; 7 lower-rotor points match the digitised table | OK | — |
| 37 | l.53, l.18 | torque rms 6.3 % over 27 points | `result.json` `rms_error` 0.0628, 27 points | OK | — |
| 38 | l.55 | PV trajectory: speed within 1 %, alt 0.2 km at 4 points; 2409 vs 2449 W/cm² | `K_entry_crosschecks.md`; `D_tauber_venus_rad_2012.md`: "8.6 (peak) … 2449" | OK | — |
| 39 | l.65 | 00–08 h LT, Dec 1978 | `A_pv_probes…`: LT 0:07, 3:35, 6:46, 7:38; "Entry date 9 Dec 1978" | OK | — |
| 40 | l.70 | 50 km: 74.7 °C, 1.029 bar, 1.550, band 1.52–1.58, wind 60 (43–78) | `A_pv_probes…` mean 347.9 K / 1.029 / 1.550; probes 1.515–1.584; DLBI 53–68 ±10 | OK | — |
| 41 | l.71 | 53 km: 46.6 °C, 0.683 bar, 1.118 | no 53 km row; interpolation of 52/54 km means gives ≈319.7 K, 0.682, 1.117 | OK | — |
| 42 | l.72, l.15 | 55 km: 26.0 °C, 0.508, 0.889, 0.867–0.907, 65 (49–84) | mean 299.1 K / 0.508 / 0.889; probes 0.867–0.907; DLBI 59–74 ±10; `result.json` atmosphere_55km | OK | — |
| 43 | l.73 | 58 km: −2.1 °C, 0.314, 0.606, 0.58–0.62, 76 (55–96) | mean 271.1 / 0.314 / 0.606; probes 0.583–0.623; DLBI 65–86 | OK | — |
| 44 | l.74 | 60 km: −15.4 °C, 0.223, 0.452, 0.43–0.46, 85 (69–101) | mean 257.8 / 0.223 / 0.452; probes 0.429–0.464; DLBI 79–91 | OK | — |
| 45 | l.76 | cloud layers 47.5–50.5 / 50.5–56.5 / 56.5–70 km | `A_titov2018_clouds.md` Table 1 | OK | — |
| 46 | l.77 | 51–56 km near-adiabatic at all four probes, ±1 K/km | `A_pv_probes…`: "within about ±1 K/km between ~51 and ~56 km" (agent's calc) | OK | — |
| 47 | l.78 | VEGA vertical air motion σ 0.65–0.75, −3.5…+2 m/s | `A_vega1985…`: sd 0.66 / 0.73; ranges −3.50…+1.46, −3.29…+1.96 | OK | — |
| 48 | l.79 | horizontal fluctuations up to 1–2 m/s at 30–130 s | `A_vega1985…`: "0.05–1 m/s (VEGA-2), up to 2 m/s (VEGA-1)" | OK | — |
| 49 | l.79 | zonal wind 66–69 m/s at 53–54 km (VEGA) | `A_vega1985…`: "69 ± 1 m/s (VEGA-1), 66 ± 1 m/s (VEGA-2)" | OK | — |
| 50 | l.80 | decadal changes up to 30 m/s | `A_winds…`: "Decadal variation … up to 30 m/s" (Peralta 2018) | OK | — |
| 51 | l.81 | lightning: Akatsuki 16.8 h, no flashes [A] | `A_lorenz2018_lightning.md`: "42 nightside passes, 16.8 h … no lightning flashes" [A] | OK (correctly tagged A) | — |
| 52 | l.90 | NCR18650B charge 0–45 °C, discharge −20…60 °C | `D_panasonic_ncr18650b.md`: "charge 0…+45 °C; discharge −20…+60 °C" | OK | — |
| 53 | l.94 | Landis & Haag 256 / 404 / 559 W/m² at 50/55/60 km | `D_landis_haag_2013_solar.md` Table 1: 256.0 / 404.4 / 559.2 | OK | — |
| 54 | l.93 | hover 1.59 / 2.09 / 2.91 / 3.99 kW; +21 %, +39 % | `result.json` power_vs_altitude: 1592 / 2088 / 2909 / 3991 W; 2518/2088 = 1.21 | OK | — |
| 55 | l.91 | interior 37 / 27 / ~25 / 57 / 84 °C | `result.json` interior_C 36.6 (55), 26.7 (58), 25.0–25.6 (60–64), 56.5 (53), 83.8 (50) | OK | — |
| 56 | l.96 | 58 km: 51 kg, 41 h vs 44 kg, 49 h | `sensitivity.json`: 51.40 kg / 41.17 h; baseline 43.66 / 49.18 | OK | — |
| 57 | l.109 | MSH coax flap 1.54/rev, 32 Hz; hexacopter chosen | `C_johnson2020_msh.md`: "coax 1.537/rev = 32.1 Hz"; "hexacopter was preferred" | OK | — |
| 58 | l.111 | MSH 31 kg hex in a 2.5 m aeroshell | `C_johnson2020_msh.md`: "31 kg hexacopter … within a 2.5 m diameter aeroshell" | OK | — |
| 59 | l.117 | 40 % thrust margin; tip Mach 0.7–0.8 | `C_johnson2020_msh.md`: "40 % thrust margin"; "Tip Mach 0.7 → 0.8" | OK | — |
| 60 | l.119–120 | 55 m/s: cos z 0.58, +3 kg; 90 m/s: −1 kg, 0.65 | `trade_sizing.json` (2.6 m, deck): 46.85 kg / 0.582; 43.66 / 0.595; 42.83 / 0.649 | OK | — |
| 61 | l.121, F10 | direct drive diverges for 180 Wh/kg or 5 N·m/kg; closes at 54.6 kg | `sensitivity.json` robustness gear 1.0: two "diverges"; nominal 54.58 kg | OK | — |
| 62 | l.122 | 2.6 m keeps ~6–11 h more than 2.3 m | `sensitivity.json`: differences 6.9–10.5 h | OK | — |
| 63 | l.30, 132–137 | 514 rpm, M 0.26, σ 0.027, 78/47 mm, −12°, 7.0°, FM 0.60, 11.9 N/m², 272 W | `result.json` vehicle; `design.json` rotor; simulator `shaft_W_total` 1632/6 = 272 | OK | — |
| 64 | l.134 | Ingenuity Re ~1.1×10⁴ | `C_johnson2020_msh.md` Table 3 MH "Re (75 % R) … 11,412" | OK | — |
| 65 | l.136 | MSH 8.5 N/m² = 2.29 kg/m² × 3.71 m/s² | MSH "disk loading [kg/m²] … 2.29"; `C_balaram2018.md` "Mars 3.71 m/s²" | OK | — |
| 66 | l.139 | MSH hex 1.55/rev, Ingenuity ~2/rev | MSH Table 5: "hex 1.546/rev"; "MH flap frequency 2.02/rev" | OK | — |
| 67 | l.144 | K&H NACA 0015 polar at Re 2.4×10⁵ | `C_knight_hefner1937.md`: "same Reynolds Number (242,000)" | OK | — |
| 68 | l.147 | Sm₂Co₁₇ ≈300 °C; NdFeB SH 150 °C | `D_eclipse_magnets.md`: "Sm2Co17 standard ≈ +300 °C"; "SH … 150 °C" | OK | — |
| 69 | l.149, F4 | motors + gearboxes 3.3 kg | `result.json` breakdown motors 3.325 | OK | — |
| 70 | l.157 (tag [D]) | cloud deck reflects 84–89 % back up at 50–62 km | `A_tomasko1980_lsfr…` COMB up/down 0.84 (50) … 0.89 (62); VIS 0.87–0.91 (SZA 65.7°) | OK | — |
| 71 | l.157 | 29 % AM0 array | `D_landis_haag_2013_solar.md`: "Array efficiency at standard AM0 = 29 %" | OK | — |
| 72 | l.159, l.19 | 2.97 kW overhead at 55 km | `result.json` P_solar_overhead_W 2965 | OK | — |
| 73 | l.161 | 243 Wh/kg; 1.04 kWh; 0.5 h hover | NCR18650B "243 Wh/kg"; battery_Wh 1044 (= 6.74 kg × 243 × 0.75 × 0.85); 1044/2088 = 0.50 h | OK | — |
| 74 | l.165, F6 | release hour angle −51° | `design.json` release_hour_angle_deg −51.3 | OK | — |
| 75 | l.168 | FEP 95 % strength, 168 h conc. H₂SO₄ 120 °C, 0 % gain | `D_fep_chemical_resistance.md`: "120 °C / 248 °F, 168 h \| 95 % … 0.0 %" | OK | — |
| 76 | l.169 | JPL FEP/Kapton survived 96 % acid at 100 °C under load | `D_jpl_aerobot_materials.md`: "96.2 % H2SO4 at 100 °C under 63 N tension" | OK | — |
| 77 | l.170 | Parylene cells: no loss after 96 h in 96 % acid | `D_jpl_solar_acid_2022.md`: "no detectable performance loss after 96 h in 96 % H2SO4" | OK | — |
| 78 | l.170 | bare Ti 1.6 mm/y conc. acid RT; not in 96 % vapour | `D_timet_titanium_h2so4.md`: "62 mpy (1.57 mm/y)"; "96 % vapours … Nil" (38, 66 °C) | OK | — |
| 79 | l.171 | 316L only cold and concentrated | `D_alleima_steel_h2so4.md`: "< 0.1 mm/y in 90–98 % acid at ≤ 30 °C" | OK | — |
| 80 | l.171 | no data for CFRP in concentrated acid | `D_00_index.md`: "no usable primary data found" | OK | — |
| 81 | l.176 | silvered FEP α 0.08, ε 0.52 | `D_jpl_aerobot_materials.md`: "α = 0.08, ε = 0.52" | OK | — |
| 82 | l.190 | 0.4 kWh to ride a downdraft and climb back | `result.json` R5 "~0.37 kWh" | OK | — |
| 83 | l.191 | baro altitude ±0.19 km | `result.json` baro_error_m_55km 186 | OK | — |
| 84 | l.192 | no magnetic field (VAPS) | `D_vaps_2018.md`: "no permanent magnetic field for attitude" | OK | — |
| 85 | l.193 | gyrocompass ratio 6 | `result.json` gyrocompass_ratio_0p01 6.17 | OK | — |
| 86 | l.194 | Ingenuity drift 1–6 % | `D_delaune_2021_ingenuity_nav.md`: "~1–2 % … scouting flights ~2–6 %" | OK | — |
| 87 | l.196 | light time 2.3–14.3 min (doc 19) | `docs/19…` l.53: "2.3–14.3 min one way [K]" (consistent; not source-verified) | OK | — |
| 88 | l.199 | 13 min passes, ~330 Mbit/pass | `result.json` pass_min 12.98, Mbit_per_pass 329.5 | OK | — |
| 89 | l.200 | X-band ~0.005 dB/km at 50 km; ~0 above 53 km | `D_venus_microwave_absorption.md`: "≈ 0.005 dB/km at 50 km"; "0.000–0.003 dB/km above ~53 km" | OK (single profile, lat −43°) | — |
| 90 | l.201 | VEVA 400 MHz, 1 W, 200 km, 500 kbps; 18 dB margin | `D_veva_cutts_1999.md` Table 2 row; `result.json` veva_margin_dB 18.3 | OK | — |
| 91 | l.202 | DAVINCI 154 Mbit–1.2 Gbit in ~1 h, S-band relay | `D_davinci_probe_arch.md`: "worst 154 Mbit … best 1.2 Gbit"; "Adjustable Data Rate (ADR) S-band link" | OK | — |
| 92 | l.210 | stowed ~1.5 × 2.0 m; visual model 1.57 × 2.12 m | `design.json` stowed 1.5 / 1.97 m; note "1.57 x 2.12 m" | OK | — |
| 93 | l.212 | mid-air deployment only demonstrated for 2–4-fold aircraft | `B_young2026_venus_aerial.md`: "limited to aircraft with two to four wing folds" | OK | — |
| 94 | l.221–227 | design.json v0.5, schema, 13 components, arms 30°+60°·i, 2.7 m, span 8.0 m; simulator 43.7 kg, inertia 33/33/65 | `design.json` version 0.5, 13 components, azimuths 30…330; simulator mass 43.651, I 33.19/33.19/65.09 | OK | — |
| 95 | l.236–239 | 200 km, 10.78 km/s, −9.5°; 284 kg, β 25.1; 56 g at 92 km; 228 + 18 W/cm²; 3.9 kJ/cm²; 79 km; 716 s; 12.8 m/s | `result.json` entry: 283.8, 25.13, 56.07 @ 92.4 km, 228.1, 18.0, 3.94, 79.3, 716.3, 12.81 | OK | — |
| 96 | l.237 | vehicle 20 %, Landis fractions + 30 % | `B_landis_venus_airplane.md` table (20/7/13/12/8/10/15/15 %, +30 %); `result.json` mass_budget matches | OK | — |
| 97 | l.238, l.21 | PV large probe 280 g in SP-461 | `B_fimmel1983_sp461.md`: "Peak deceleration 280 g" | OK | — |
| 98 | l.241 | Dragonfly: rotors spun under main chute, release below 2.9 m/s | `C_pensado2025_dragonfly_edl.md`: "posed … spun up"; "down velocity < 2.9 m/s" | OK | — |
| 99 | l.242, l.22 | 26 m vs 559 m; MAHD 3 s free fall + 12 s spin-up | `result.json` 26.4 / 558.9 m; `C_delaune2022_mahd.md`: "3 s free fall"; "12 s" spin-up | OK | — |
| 100 | l.243 | 3 m/s to 55 km, ~33 min | `design.json` 856 → 2856 s | OK | — |
| 101 | l.248 | PV β 190, −31.8° (Tauber 2012) | `D_tauber_venus_rad_2012.md`: "β = 190 kg/m², entry 11.584 km/s at −31.829°" | OK | — |
| 102 | l.250 | Venera 9–14 entered at −18…−23° | `B_venkatapathy…`: "(−18, −23)"; `B_abramovich…`: V9 "−20°30′" | OK | — |
| 103 | l.251 | Vega balloon extracted at 61 km; floated 53–54 km for 46 h | `B_siddiqi2018.md` "at 61 kilometers altitude"; `A_vega1985…` "53-54 km", "46 h each" | OK | — |
| 104 | l.252 | DAVINCI 10.4 km/s, −6.3°, 32 g, 1.8 m pilot at Mach 0.8, 5.8 m main ~70 km | `B_davinci.md` (decoded font): all values as written | OK | — |
| 105 | l.261–263 | dives at 6 h/20 h; 48.5 h; 47.3 km at 49.2 h; 11 500 km; ~30 % of circumference | `result.json` events 21600/72000 s, 174480 s, 47.3 km, 49.18 h; drift 11 546 km | OK | — |
| 106 | l.272 F9 | no single assumption costs more than ~8 h | `sensitivity.json`: worst finite = 58 km, 49.18 → 41.17 h | OK | — |
| 107 | l.283 | hover ~48 W/kg; Mars ~160–200 W/kg (MSH/Ingenuity) | 2088/43.66 = 47.8; MSH "≈ 158 W/kg", Ingenuity "≈ 200 W/kg" (both agent-derived) | OK (derived) | — |
| 108 | l.284 | 1.34 kW × 77 h ≈ 103 kWh | arithmetic correct (see row 24 for 77 vs 78 h) | OK | — |
| 109 | l.287 | Ingenuity 163 Wh/kg cells | `D_jpl_m2020_ingenuity_battery.md`: "163 Wh/kg cell-level at 25 °C" (derived) | OK | — |
| 110 | l.288 | 180 Wh/kg: 52.5 kg, 44 h; 30 % contingency: 51.5 kg, 44 h | `sensitivity.json`: 52.53 / 43.75 h; 51.47 / 44.42 h | OK | — |
| 111 | l.290 | ADEPT β 44, −8.5°: 35 vs 32 g | `B_venkatapathy…`: "β 44 kg/m², EFPA −8.5° → 32 g"; K note 35 g | OK | — |
| 112 | l.293 | Venus-GRAM profile changes peak g < 3 % | `K_entry_crosschecks.md`: "29.5 vs 28.8 g; 36.2 vs 35.4 g" | OK | — |
| 113 | l.303, l.319–320 | Earth drops at 1–2 km match Venus 54–55 km; JPL prototype flew this in 2022 | `B_izraelevitz2025_aerobot.md`: "54 km … ↔ Earth 1.1 km"; "55 km … 2.2 km"; "July 2022" | OK | — |
| 114 | l.321, l.323 | Ingenuity tested in CO₂ in JPL 25-ft chamber; JPL 100 °C acid protocol | `C_balaram2018.md` "JPL 25-ft Space Simulator"; `D_jpl_aerobot_materials.md` "100 °C" | OK | — |
| 115 | l.330–333 | 5.7 m, 94 m³, 20 kg envelope, 12.6 kg battery for 78 h at 25 W, ~62 kg tanks; VEGA 0.33 kg/m² | `result.json` hybrid 5.65 m, 94.5 m³, 20.06, 12.58, 1950 Wh, 61.8; 12.5 kg / π·3.4–3.54² = 0.32–0.34 | OK | — |
| 116 | l.333 | VEGA floated 21 kg on a 3.4–3.5 m sphere for 46 h | `A_vega1985…`: "21 kg", "3.4 m … 3.54 m nominal", "46 h each" | OK | — |

## Notes on method

- "OK" means the number, unit and condition match the note. It does not mean the note's own reading of the primary
  source was re-verified: no primary PDFs were opened in this check.
- Some rows marked OK are agent arithmetic ([derived]/[calc] in the notes) that the doc tags [D-ag]: rows 46, 107, 109,
  and the Landis fractions in row 96. `README.md` allows this, but those values were not read off a page.
- Not checkable from the files named (left out of the count): Hohmann v∞ 2.71 km/s and ~146 d, 3.4 km/s capture,
  coax-model rms 3 %, gust-response 4 m RMS / 11 m peak / 14 %, blade 1.7/rev and 11 Hz, arm stress 68 MPa,
  "~185 Wh/kg / ~5.2 N·m/kg" closure limits, and "~4 800 W/cm²" for PV in our model. None of these appears in
  `result.json` or `design.json`.

## Resolution by the Venus session (4 Nov 2026, ~19:50 UTC+3)

The Venus session checked the meaning-changing findings against the notes itself before acting:
- Pioneer Venus probe latitudes: the A_pv_probes table gives Day 31.3°S and Night 28.7°S. Fixed to 31.3°S–59.3°N in docs/25 and in the `atmosphere.py` docstring. The same wording in `A_00_index.md` was left as the agent wrote it.
- MSH C_T/σ: the note gives 0.11–0.115. The doc now says so; our 0.10 is marked [Y], chosen for extra stall margin.
- Landis fold count: fixed in docs/25 and `design.json` (`stowed.fits`).
- F8 caption: now reads "26 of 27 points within ±10 %, worst 21 %".
- 48 g rigid case: the doc now states that the column mapping may be garbled. Added the ADEPT envelope 35–45 g (Venkatapathy 2017): our model gives 37 g at −8.5° and 56 g at −9.5°.
- "≥ 44 h" corrected to "≥ 43.8 h".
- H₂SO₄: 75–90 wt% observed; 98 % is a model value at the cloud base.
- MSH attribution: the rpm-response argument is now marked [K]; MSH is credited only for rejecting the large coaxial.
- Downdraft: replaced with the note's actual event (VEGA-2, −2…−3.3 m/s over ~2 h, ~2.9 km down, 4 h to recover) in docs/25, `atmosphere.VERTICAL_WIND`, `control.py` and `risk.py`.
- Gust correlation time: 80 s is tagged [Y], inside the measured 30–130 s.
- Rotation rate is marked [K]; it is computed from the sidereal period.
- Tauber radiative: the doc now says the fit is extrapolated in nose radius.
- k: the doc now says it was derived by the agent.
- Vega inflation timing is tagged [A].
- Rounding fixes applied as suggested: VEX at ~47 km, Sun fix "better than 10°", Syal 1.27–1.28, Allen–Eggers steep only, Venera 11/12/14, Parylene-only test, Ames above-cloud, VEGA distance [A], FEP vs PFA.
- Contradictions resolved:
  - Pioneer Venus 288 g (model) vs 276–280 g (reported)
  - Re 1.7×10⁵ throughout
  - max airspeed in `vesper_for_simulator.json` is now computed (22.75 m/s) instead of hard-coded 24
  - air-mass day 6.5 d vs circumnavigation 6.8 d explained
  - night 78 h
- "72 closed designs" corrected to "72 design points (69 close)".
- The latitude study is now written to `result.json` (`latitude_study`).
