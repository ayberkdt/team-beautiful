# E_02 — Pioneer Venus DLBI wind tables (PDS), re-read 5 Nov 2026

- **Source:** Counselman et al., PV Differential Long Baseline Interferometry, PDS4 `pvmp_dlbi`:
  `https://atmos.nmsu.edu/PDS/data/PDS4/pvmp_dlbi/data/dlbi_{large,day,night,north}_atm_vel.tab` and `dlbi_large_atm_vel.xml` (label).
- **Accessed:** 2026-11-05. Local `D:\tmp_ideathon\venus_research\pv\`. Read level: full files **[D]**.
- **Columns (label, [D]):** grt (s), vel_down_rel_to_crust, vel_west_rel_to_crust, vel_north_rel_to_crust, vel_west_rel_to_atm, vel_north_rel_to_atm (all m/s). No altitude column.
- **Method [K]:** wind = (probe velocity rel. crust) − (probe velocity rel. atmosphere); altitude from GRT via the same probe's state table (E_01). Linear interpolation between wind samples, max gap 2.5 km (small-probe samples are 1.1–1.7 km apart; Large probe ~0.15 km).
- Coverage: Large 0.4–64.6 km (502 rows); Day 0.4–62.5 km; Night 0.0–61.4 km; North 1.7–59.3 km.

## Results [K on D] (westward u; northward v)

| z km | n | u mean | u min–max | v min–max |
|---:|---:|---:|---|---|
| 40 | 4 | 38.5 | 35.3–41.9 | −3.2…+0.1 |
| 45 | 4 | 52.5 | 48.0–59.4 | −0.5…+5.0 |
| 50 | 4 | 60.1 | 52.8–68.3 | −4.2…+3.9 |
| 52 | 4 | 60.8 | 53.0–70.2 | −7.1…+4.8 |
| 55 | 4 | 63.4 | 59.1–72.7 | −6.2…+1.6 |
| 58 | 4 | 74.0 | 66.3–84.3 | −1.3…+2.3 |
| 60 | 3 | 84.6 | 77.4–91.3 | +0.6…+5.8 |
| 62 | 2 | 99.9 | 96.2–103.7 | −1.0…+7.7 |
| 64 | 1 | 97.9 | — | +5.3 |

This reproduces doc 25's own 4-probe interpolation (60/63/74/85 m/s at 50/55/58/60 km) exactly. The doc 25 table column uses a "probes within ±0.5 km" mean (65 m/s at 55 km), 1.6–2 m/s higher; doc 25 already states this.
Large probe shear 56→60 km: 65.6 → 91.5 m/s ≈ 6.5 m/s per km [K].
