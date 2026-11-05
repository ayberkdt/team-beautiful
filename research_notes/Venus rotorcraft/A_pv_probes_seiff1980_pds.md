# A_pv_probes_seiff1980_pds — Pioneer Venus 4-probe atmosphere structure (LAS/SAS), raw PDS tables

## Citation

- **Data (what was actually read):** Seiff, A., Suomi, V. E., Barnes, A., Keating, G. M., Tomasko, M. G.,
  *Pioneer Venus Special Events Data (SED) Bundle*, NASA Planetary Data System, Atmospheres Node,
  DOI 10.17189/m5zf-6f12 (DOI string as printed on the PDS page; the PDS page writes it as
  `https://doi.10.17189/m5zf-6f12`, which is malformed — use `https://doi.org/10.17189/m5zf-6f12`, not tested).
  Files: `https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/data_atm_struct/descent_low_atm/`
  - `las_low_atm_state.csv` (+ `_descr.txt`, `.xml`) — Large ("Sounder") probe, 0–64.83 km, 576 rows
  - `sas_day_low_atm_state.csv` — Day probe, -0.10–66.85 km
  - `sas_night_low_atm_state.csv` — Night probe, -0.65–65.14 km
  - `sas_north_low_atm_state.csv` — North probe, 0.98–61.26 km
  - also read the headers of `entry_mid_atm/sas_*_mid_atm_state.csv` (entry phase, 70–137 km)
- **Paper that describes these data (NOT read, paywalled/blocked):** Seiff, A., Kirk, D. B., Young, R. E.,
  Blanchard, R. C., Findlay, J. T., Kelly, G. M., Sommer, S. C. (1980), "Measurements of thermal structure
  and thermal contrasts in the atmosphere of Venus and related dynamical observations: Results from the four
  Pioneer Venus probes", *J. Geophys. Res.* 85(A13), 7903–7933, doi:10.1029/JA085iA13p07903.
  (Author list from memory, not verified; Wiley abstract page returned HTTP 403 and ADS returned a
  human-verification page, which I did not bypass.)
- **Probe sites:** PDS Atmospheres Node page "Summary of the Pioneer Venus Mission",
  `https://atmos.nmsu.edu/data_and_services/atmospheres_data/PIONEER_Venus/pioneer_ins.html` (read in full).

## What I read

Full CSV data tables (all rows) and the descriptor text files, downloaded to
`D:\tmp_ideathon\venus\downloads\atmo\pvsed\`. Values below at target altitudes are **my linear interpolation**
between adjacent tabulated rows (row spacing ≈ 0.15 km for LAS, 0.5–0.6 km for small probes), script
`D:\tmp_ideathon\venus\scripts\pvprof.py`. Lapse rates are least-squares slopes of T(z) over ±0.75 km
windows, script `D:\tmp_ideathon\venus\scripts\stab.py`. So the table values are [D-ag] data with a trivial
interpolation step (mine).

## Probe metadata [D-ag] (PDS mission summary table + descriptor files)

| Probe | Impact lat | Impact lon (°E) | Local Venus time | SZA (°) | R0 used (km) | g0 (m/s²) |
|---|---|---|---|---|---|---|
| Large / Sounder | 4.4 N | 304.0 | 7:38 | 65.7 | 6052.0 | 8.8694 |
| North | 59.3 N | 4.8 | 3:35 | 108.0 | 6053.0 | 8.8665 |
| Day | 31.3 S | 317.0 | 6:46 | 79.9 | 6051.9 | 8.8697 |
| Night | 28.7 S | 56.7 | 0:07 | 150.7 | 6051.4 | 8.8712 |

- All altitudes in all four files are relative to the **Sounder landing site, radius 6052.0 km** [D-ag]
  (descriptor: "ALL ALTITUDES ARE MEASURED RELATIVE TO THE 6052.0 KM RADIUS").
- Mean molecular weight input MW = 43.44 [D-ag]; compressibility ζ = p/(ρRT) ≈ 0.998 at 50–55 km [D-ag].
- Stated absolute accuracies [D-ag]: p and ρ 0.5 % of reading; T 1 K; altitude 0.4 % of reading.
- Sounder descent speed 39→12 m/s on parachute; parachute jettison at 45.4 km [D-ag].
- Entry date 9 Dec 1978 [D-ag].

## Numbers at target altitudes [D-ag, linearly interpolated by me]

T [K] / p [bar] / ρ [kg/m³]

| z (km) | Sounder 4.4N 07:38 | Day 31.3S 06:46 | Night 28.7S 00:07 | North 59.3N 03:35 | spread (max−min; % of 4-probe mean) T / p / ρ |
|---|---|---|---|---|---|
| 45 | 384.4 / 1.874 / 2.558 | 384.8 / 1.943 / 2.650 | 386.2 / 1.961 / 2.665 | 381.7 / 1.906 / 2.621 | 4.5 K / 4.5 % / 4.1 % |
| 48 | 364.9 / 1.299 / 1.868 | 366.8 / 1.347 / 1.926 | 366.9 / 1.361 / 1.946 | 358.3 / 1.315 / 1.925 | 8.6 K / 4.7 % / 4.1 % |
| 50 | 347.3 / 1.004 / 1.515 | 351.8 / 1.045 / 1.556 | 348.7 / 1.055 / 1.584 | 343.7 / 1.014 / 1.545 | 8.1 K / 4.9 % / 4.5 % |
| 52 | 329.5 / 0.767 / 1.219 | 334.3 / 0.800 / 1.254 | 331.9 / 0.806 / 1.272 | 323.5 / 0.771 / 1.248 | 10.8 K / 5.0 % / 4.2 % |
| 54 | 309.5 / 0.576 / 0.975 | 313.8 / 0.604 / 1.007 | 311.6 / 0.607 / 1.019 | 303.0 / 0.576 / 0.995 | 10.8 K / 5.2 % / 4.5 % |
| 55 | 299.4 / 0.496 / 0.867 | 302.8 / 0.521 / 0.900 | 301.8 / 0.523 / 0.907 | 292.6 / 0.494 / 0.884 | 10.2 K / 5.7 % / 4.5 % |
| 56 | 288.9 / 0.425 / 0.769 | 291.3 / 0.447 / 0.802 | 291.6 / 0.449 / 0.805 | 282.1 / 0.422 / 0.782 | 9.5 K / 6.2 % / 4.5 % |
| 58 | 276.0 / 0.307 / 0.583 | 271.4 / 0.323 / 0.623 | 274.8 / 0.325 / 0.618 | 262.2 / 0.302 / 0.602 | 13.8 K / 7.4 % / 6.6 % |
| 60 | 268.1 / 0.220 / 0.429 | 257.6 / 0.229 / 0.464 | 261.9 / 0.232 / 0.462 | 243.4 / 0.210 / 0.452 | 24.7 K / 9.5 % / 7.8 % |
| 62 | 254.8 / 0.155 / 0.318 | 249.4 / 0.160 / 0.336 | 250.9 / 0.162 / 0.338 | — (top 61.26 km) | 5.4 K / 4.6 % / 6.0 % (3 probes) |
| 64 | 247.0 / 0.108 / 0.228 | 242.7 / 0.111 / 0.239 | 241.2 / 0.112 / 0.243 | — | 5.8 K / 4.0 % / 6.3 % |
| 65 | top of LAS file is 64.83 km: 246.3 K, 0.0925 bar, 0.1964 kg/m³ (first row) | — | — | — | — |

Caveat on the 56–62 km small-probe values: small-probe rows are sparse there (they fall fast; sampling every 8 s),
so interpolation over ~1–2 km gaps; North probe 58–60 km values cover a gap.

## 4-probe mean (my arithmetic)

| z | mean T (K) | mean p (bar) | mean ρ (kg/m³) |
|---|---|---|---|
| 45 | 384.3 | 1.921 | 2.624 |
| 48 | 364.2 | 1.331 | 1.916 |
| 50 | 347.9 | 1.029 | 1.550 |
| 52 | 329.8 | 0.786 | 1.248 |
| 54 | 309.5 | 0.591 | 0.999 |
| 55 | 299.1 | 0.508 | 0.889 |
| 56 | 288.5 | 0.435 | 0.790 |
| 58 | 271.1 | 0.314 | 0.606 |
| 60 | 257.8 | 0.223 | 0.452 |
| 62 | 251.7 | 0.159 | 0.331 (3 probes) |
| 64 | 243.6 | 0.110 | 0.237 (3 probes) |

## Static stability (my computation from the above data) [D-ag data + own calc]

Adiabatic lapse rate Γ_ad = g/c_p with g = g0·(6052/(6052+z))² and c_p of pure CO2 from NIST WebBook
(Span–Wagner EOS; see `A_nist_co2_properties.md`) at the local (T,p). Pure-CO2 c_p; the 3.5 % N2 would raise
c_p by only ~0.4 % (my estimate) — negligible.

| z (km) | −dT/dz Sounder | Day | Night | North | Γ_ad (K/km) |
|---|---|---|---|---|---|
| 45 | 5.4 | 6.6 | 6.2 | 5.4 | 9.4 |
| 48 | 8.6 | 5.8 | 8.8 | 8.0 | 9.6 |
| 50 | 7.5 | 8.2 | 9.1 | 9.6 | 9.7 |
| 51 | 9.2 | 9.5 | 8.1 | 10.0 | 9.8 |
| 52 | 9.3 | 9.5 | 9.1 | 10.2 | 9.9 |
| 53 | 10.1 | 10.3 | 10.7 | 10.4 | 10.0 |
| 54 | 10.1 | 10.3 | 10.2 | 10.7 | 10.1 |
| 55 | 10.4 | 10.2 | 9.5 | 10.2 | 10.3 |
| 56 | 9.8 | 11.5 | n/a | n/a | 10.4 |
| 58 | 5.4 | n/a | n/a | n/a | 10.6 |
| 60 | 6.8 | n/a | n/a | n/a | 10.7 |
| 62 | 4.9 | n/a | n/a | n/a | 10.9 |
| 64 | 1.3 | n/a | n/a | n/a | 11.0 |

**Result:** in all four probes the lapse rate equals the adiabatic one within about ±1 K/km between
**~51 and ~56 km** (some windows marginally superadiabatic by up to +1.2 K/km, which is within the error of a
1-km slope given 1 K T accuracy) → **near-neutral (convective) layer ≈ 51–56 km** at all four sites
(4.4N to 59.3N, day and night). Below ~50 km and above ~57 km the layer is clearly stable
(−dT/dz 2–9 K/km less than adiabatic; Brunt–Väisälä N ≈ 0.008–0.019 s⁻¹, my calc).
Sounder data also show a weaker near-neutral stretch at 48.5–49 km (single probe).

## Caveats

- These are four single soundings (Dec 1978). Spread between them ≈ 5–11 K in T and ≈ 5 % in p at 45–56 km;
  this is a lower bound of real variability (latitude 4–59°, local time 00–08 h only; no afternoon probe).
- Pressures of the Sounder are ~4–6 % lower than the Day and Night probes at the same altitude but within ~0–2 % of the North probe;
  possibly an altitude-reference offset between probes or real variability; I did not read Seiff et al. 1980,
  so the cause is not established here.
- Altitude reference 6052.0 km radius. **Whether VIRA uses the same reference is not verified here.**
- North-probe 58–60 km rows are interpolated across a data gap.
