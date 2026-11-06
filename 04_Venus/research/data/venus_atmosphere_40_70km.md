# `venus_atmosphere_40_70km.csv` — column guide

Written 2026-11-05. 61 rows, **40.0–70.0 km every 0.5 km**. Built by
`D:\tmp_ideathon\venus_research\build_atm.py` (`python -I build_atm.py <download_dir> <out.csv>`) from raw files
downloaded this session (notes E_01–E_07). Empty cell = no data at that altitude (never filled by guess).

## Tags of the columns
- **[D]** raw PDS / NIST / JPL data read this session; **[K]** our interpolation or calculation on [D];
  **[D-ag]** Venus-GRAM (tertiary VIRA-based model, E_07).

## Altitude reference
Pioneer Venus altitudes are above 6052.0 km radius (E_01); VEGA-2 lander altitudes are "reconstructed" (E_04); GRAM
uses 6051.89 km (E_07). The 0.11 km offset is ignored (< 1 % in ρ).

## Columns

| Column | Unit | Meaning | Source / tag |
|---|---|---|---|
| alt_km | km | altitude | grid |
| n_pv_probes | – | Pioneer Venus probes with data here (max 4) | E_01 [D] |
| n_soundings | – | PV probes + VEGA-2 lander with data here (max 5) | E_01, E_04 [D] |
| T_K_mean | K | mean of PV probes | [K] on E_01 |
| T_K_min, T_K_max | K | envelope over PV probes + VEGA-2 lander | [K] on E_01, E_04 |
| p_Pa_mean / _min / _max | Pa | geometric mean of PV probes / envelope (incl. VEGA-2) | [K] |
| rho_kgm3_mean / _min / _max | kg/m³ | geometric mean of PV probes / envelope (VEGA-2 ρ from ideal gas, M 43.44) | [K] |
| a_ms_mean / _min / _max | m/s | speed of sound of 96.5 % CO2 + 3.5 % N2 at (T_mean, p) / at (T_min, p) / (T_max, p) | [K] on NIST E_05 |
| mu_uPas | µPa·s | dynamic viscosity (Wilke mix of NIST CO2, N2) | [K] on E_05 |
| nu_m2s | m²/s | kinematic viscosity µ/ρ_mean | [K] |
| gamma | – | cp/cv of the mixture (real-gas NIST values) | [K] on E_05 |
| cp_JkgK | J/(kg K) | mixture cp | [K] on E_05 |
| k_WmK | W/(m K) | mixture thermal conductivity (for convection/thermal models) | [K] on E_05 |
| g_ms2 | m/s² | GM/(6052.0 km + z)², GM = 324858.592 km³/s² | [K] on E_06 |
| molar_mass_gmol | g/mol | 43.45 (96.5 % CO2, 3.5 % N2) | [K] |
| u_west_ms_mean / _min / _max | m/s | zonal wind (westward +), PV DLBI, interpolated per probe (gap ≤ 2.5 km); mean and probe range | [K] on E_02 |
| v_north_ms_min / _max | m/s | meridional wind range over the probes | [K] on E_02 |
| n_wind_probes | – | probes with a wind value here | E_02 |
| lsfr_comb_down_Wm2, lsfr_comb_up_Wm2 | W/m² | PV LSFR combined channel (0.41–1.78 µm), Sounder, solar zenith 65.7° | [D/K] E_03 |
| lsfr_down_over_top | – | down flux / down flux at 64.3 km (shape of the light profile) | [K] |
| lsfr_up_over_down | – | upward / downward flux = albedo seen from below by a bifacial panel | [K] |
| T_K_gram, p_Pa_gram, rho_kgm3_gram | K, Pa, kg/m³ | Venus-GRAM average profile (VIRA-based), log-interpolated to 0.5 km | [D-ag] E_07 |
| rho_gram_10N / 40N / 60N / 80N | kg/m³ | GRAM mean density at those latitudes | [D-ag] E_07 |
| rho_gram_lat_lo / _hi | kg/m³ | min of DENSLO / max of DENSHI over the four latitudes | [D-ag] E_07 |
| T_<probe>, rho_<probe> | K, kg/m³ | each sounding: large_4N_0738, day_31S_0646, night_29S_0007, north_59N_0335 (Pioneer Venus, 9 Dec 1978, local time in name), vega2_lander_7S_0100 (11 Jun 1985) | [K] on E_01, E_04 |

## Envelopes — what they cover and what they miss
- **Covered:** five night/morning soundings (00–08 h local time), latitudes 31°S–59°N, 1978 and 1985.
  At 55 km: T 292.6–302.8 K (mean 299.1), ρ 0.854–0.907 kg/m³ (mean 0.889), u 59–73 m/s (mean 63.4).
- **Not covered:** afternoon (no in-situ sounding exists), latitudes > 60°, decadal change. For those use: RO
  temperature differences ±5 K at 50–60 km low latitudes and ±10–15 K poleward of 50° above 60 km (E_08, earlier note
  A_limaye2018_banerjee2026), the GRAM latitude columns (ρ −25…−30 % at 65–70 km toward 80°N), and ±15 m/s decadal
  wind change (earlier note A_winds_cloudtracking_vex_akatsuki).
- **65–70 km:** only one or two probes, and 66–70 km is the North probe (59°N) entry data — a cold/thin high-latitude
  case. Prefer `*_gram` columns there for a low-latitude reference, and the PV values as the thin edge.
- **Winds above 64.6 km:** none in this file (no probe wind data there). Cloud-top 65–70 km: ~100 m/s at ±45°
  (E_11).

## Quick check values (55 km)
T 299.1 K, p 50 794 Pa, ρ 0.889 kg/m³, a 271.4 m/s, µ 15.03 µPa·s, ν 1.69×10⁻⁵ m²/s, γ 1.294, g 8.710 m/s²,
u 63.4 m/s west, up/down light 0.863. These match doc 25 / `sim_params.json` (ρ 0.8894, a 271.8, µ 14.96).
