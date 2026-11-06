# E_04 — VEGA-1/2 balloon level-3 data and VEGA-2 lander profile (PDS), re-read 5 Nov 2026

- **Source:** VEGA team / R. Lorenz (JHU APL) PDS3 archive `https://atmos.nmsu.edu/PDS/data/vega_5001/data/`:
  `vg1bl_rdr.dat/.lbl`, `vg2bl_rdr.dat/.lbl` (2040 rows each, 23 columns), `vg2lr.dat/.lbl` (VEGA-2 lander METEO, 431 rows).
- **Accessed:** 2026-11-05. Local `D:\tmp_ideathon\venus_research\vega\`. Read level: full files + labels **[D]**.
- **Label facts [D]:** columns time (s since 11 Jun 1985 00:00 UT), pressure (hPa), T (K), entropy, nephelometer
  backscatter, radius (km), latitude, longitude (rad), U zonal, V meridional, **W_a "Vertical Wind speed indicated by
  Anemometer"**, W_b "Modeled true vertical speed of balloon" (m/s); each with a quality flag (0 none, 1 bad, 2–3 good
  with decommutation doubt, 4 high quality). VEGA-1 start 1985-06-11T02:17:12, stop 1985-06-12T21:01:02.
  Local solar time (Lorenz note in the label): VEGA-1 LST = 0.4 + 0.156 t(h) (starts just after midnight, ends ~08:02);
  VEGA-2 LST = 1.01 + 0.15 t (ends ~08:20). Lander file: record, time (s), p (bar), T (K), reconstructed altitude (m);
  top 62.92 km (0.126 bar, 262.80 K).

## Statistics computed here [K on D]
Script `D:\tmp_ideathon\venus_research\vega_stats.py`, samples with flag ≥ 2.

| Quantity | VEGA-1 | VEGA-2 |
|---|---|---|
| W_a samples / interval | 780 / 75.5 s | 748 / 75.5 s |
| W_a mean | −0.50 m/s | −0.48 m/s |
| W_a standard deviation | **0.663 m/s** | **0.731 m/s** |
| W_a min / max | −3.50 / +1.46 m/s | −3.29 / +1.96 m/s |
| W_a 1st / 99th percentile | −2.75 / +0.88 | −2.94 / +0.38 |
| fraction with abs(W_a) > 1 m/s / > 2 m/s | 0.174 / 0.036 | 0.174 / 0.056 |
| W_a autocorrelation at 75, 150, 300, 600, 900, 1200, 1800 s | 0.93, 0.83, 0.78, 0.71, 0.63, 0.53, 0.29 | 0.96, 0.95, 0.78, 0.59, 0.59, 0.56, 0.28 |
| most negative 1-h mean W_a | −2.23 m/s | −1.71 m/s |
| U (westward) mean ± sd, range | 68.7 ± 1.7, 64.6–70.9 m/s (61 fixes) | 64.8 ± 1.8, 60.6–68.2 m/s (57 fixes) |
| V (meridional) mean ± sd, range | +0.3 ± 1.5, −2.4…+4.1 m/s | +2.2 ± 1.8, −6.3…+4.4 m/s |
| pressure mean, range | 580 hPa, 529–882 hPa | 580 hPa, 524–901 hPa |
| temperature mean, range | 314.2 K, 308.6–343.6 K | 307.5 K, 300.4–339.1 K |

Read-outs:
- σ_w ≈ 0.7 m/s confirms doc 25's 0.65–0.75 m/s.
- **The vertical-wind correlation time is long: 1/e at about 1500 s (25 min)**, not tens of seconds. The 75 s sampling
  cannot see faster gusts. So the measured σ_w describes convective cells (mesoscale), not small-scale turbulence.
- Both W_a records have a −0.5 m/s mean. A 46 h mean downdraft is not physical for a floating balloon, so treat it as
  instrument/model bias [Y].
- The pressure maxima (882 and 901 hPa) are the large downdraft excursions (float pressure ~535 hPa).
- VEGA-2 lander at 55 km: 295.4 K, 0.483 bar, ρ 0.854 kg/m³ (ρ from the ideal gas law with M = 43.44, [K]) — the
  coldest and least dense sounding at 50–56 km; it sets the lower edge of the csv envelope there.
