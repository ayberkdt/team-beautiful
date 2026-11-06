# E_01 — Pioneer Venus probe atmosphere tables (LAS/SAS, PDS SED bundle), re-read 5 Nov 2026

- **Source (data):** Seiff et al., Pioneer Venus Special Events Data bundle, NASA PDS Atmospheres Node.
  - Descent: `https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/data_atm_struct/descent_low_atm/`
    `las_low_atm_state.csv`, `sas_day_low_atm_state.csv`, `sas_night_low_atm_state.csv`, `sas_north_low_atm_state.csv`, `las_low_atm_state_descr.txt`
  - Entry (70–137 km): `.../entry_mid_atm/sas_{day,night,north}_mid_atm_state.csv` (+ `_descr.txt`). `las_mid_atm_state.csv` returns 404.
- **Accessed:** 2026-11-05, curl; local copies `D:\tmp_ideathon\venus_research\pv\` (untrusted data, read only).
- **Read level:** full files, all rows. **[D]** for every value below.

## Format (from descriptor text, [D])
- Descent rows: GRT h:m:s, GRT s, altitude km, p (bar), T (K), ρ (kg/m³), ζ = p/(ρRT).
- Entry rows: GRT, GRT s, altitude km, V (km/s), path angle (deg), ρ (kg/m³), p (mbar), T (K). ρ from deceleration, p by hydrostatic integration, T from the equation of state; mean molecular weight varies with altitude (from ONMS/BNMS).
- All altitudes relative to 6052.0 km radius. Accuracy (Sounder): p, ρ 0.5 % of reading; T 1 K; altitude 0.4 % of reading. Descent speed on parachute 39→12 m/s; parachute jettison 45.4 km.
- Top of descent records: Sounder 64.83 km (246.3 K, 0.0925 bar, 0.1964 kg/m³); Day 66.85 km (233.2 K, 0.0641 bar); Night 65.14 km (238.3 K, 0.0905 bar); North 61.26 km (234.0 K, 0.165 bar).
- Entry records reach down to: Day 70.5 km (229.0 K, 29.1 mbar, ρ 0.0664 kg/m³), North 66.0 km (220.7 K, 61.6 mbar, ρ 0.146 kg/m³), Night 71.5 km (232.9 K, 26.8 mbar, ρ 0.0601 kg/m³).

## Values used (interpolated by this session, script `build_atm.py`, [K] on [D])
See `../data/venus_atmosphere_40_70km.csv`. Selected (4-probe mean / envelope over 4 probes + VEGA-2 lander):

| z km | T K (min–max) | p Pa | ρ kg/m³ (min–max) |
|---:|---|---:|---|
| 40 | 415.8 (413.5–417.2) | 341 378 | 4.314 (4.125–4.38) |
| 45 | 384.3 (381.7–387.6) | 192 066 | 2.623 (2.478–2.665) |
| 50 | 347.9 (343.7–351.8) | 102 884 | 1.550 (1.492–1.584) |
| 55 | 299.1 (292.6–302.8) | 50 794 | 0.889 (0.854–0.907) |
| 60 | 257.8 (243.4–268.1) | 22 210 | 0.451 (0.425–0.464) |
| 64 | 243.7 (241.2–247.0), 3 probes | 11 003 | 0.236 (0.228–0.243) |
| 65 | 239.0, 2 probes | 9 205 | 0.201 |
| 68 | 239.2, North entry data only | 4 140 | 0.090 |
| 70 | 236.7, North entry data only | 2 849 | 0.063 |

Probe sites (from earlier note A_pv_probes_seiff1980_pds, PDS mission page): Sounder 4.4°N 07:38 LT; Day 31.3°S 06:46; Night 28.7°S 00:07; North 59.3°N 03:35. **All night/morning: no afternoon sounding exists.**

## Caveats
- Above 64.8 km only one or two probes, and 66–70 km comes from the North probe *entry* data (59°N): this is a high-latitude, low-density case, not a mean. Use Venus-GRAM / RO data (E_07, E_08) as the 65–70 km reference.
- Gaps > 1.6 km in a record are not interpolated across (so n_pv_probes drops above 61 km).
