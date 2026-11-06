# A_vega1985_balloons_lander — VEGA-1/2 balloons (1985, ~54 km) and VEGA-2 lander profile

## Citations

1. **Data archive (read in full):** Lorenz, R. D., Crisp, D., Huber, L. (2020), *Vega 1 and Vega 2 Balloon and
   Lander Archive*, VEGA1/VEGA2-V-2/3-VENUS-1.0, NASA PDS Atmospheres Node.
   `https://atmos.nmsu.edu/PDS/data/vega_5001/` — files read: `data/vg1bl_rdr.dat/.lbl`, `vg2bl_rdr.dat/.lbl`
   (level 3: P, T, entropy, nephelometer, radius, lat, lon, U, V, W_a, W_b; 2040 rows each),
   `vg2lr.dat/.lbl` (VEGA-2 lander METEO P–T–z profile, 431 rows), `catalog/dataset.cat`,
   and the instrument description `https://pds.nasa.gov/data/pds3/backup/202002-vega/vega_5001/ORIGvg12bl_inst`.
   Related paper (not read): Lorenz, R. D. et al. (2018), *Icarus* 305:277–283, doi:10.1016/j.icarus.2017.12.044.
2. **NASA TM-88516 (read: overview pp. 8–12, Kremnev et al. pp. 18–21, Linkin et al. pp. 38–42, Andreev et al.
   pp. 44–47, Kerzhanovich et al. pp. 51–56, Blamont et al. pp. 58–61):** Sagdeev, R. Z. et al. (1986),
   "An overview of the Soviet VEGA balloon experiment and studies of the atmosphere of Venus", translation of
   *Pis'ma v Astronomicheskiy Zhurnal* 12(1):5–95, NASA TM-88516, May 1986.
   `https://ntrs.nasa.gov/api/citations/19870009888/downloads/19870009888.pdf`
3. **JPL TDA report (read p. 1):** Stelzried, C. T., Preston, R. A., Hildebrand, C. E., Wilcher, J. H., Ellis, J.
   (1986), "The Venus Balloon Project", TDA Progress Report 42-85.
   `https://ntrs.nasa.gov/api/citations/19860018820/downloads/19860018820.pdf`
4. **Science 1986 papers — abstracts only [A]** (Caltech authors repository metadata pages):
   - Sagdeev, R. Z. et al. (1986), "Overview of VEGA Venus balloon in situ meteorological measurements",
     *Science* 231(4744):1411–1414, doi:10.1126/science.231.4744.1411.
   - Linkin, V. M. et al. (1986), "VEGA balloon dynamics and vertical winds in the Venus middle cloud region",
     *Science* 231:1417–1419, doi:10.1126/science.231.4744.1417.
   - Kremnev, R. S. et al. (1986), "VEGA balloon system and instrumentation", *Science* 231:1408–1411 (pages per
     PDS ref.cat search snippet; not opened).
   - Crisp, D., Ingersoll, A. P., Hildebrand, C. E., Preston, R. A. (1990), "VEGA balloon meteorological
     measurements", *Adv. Space Res.* 10(5):109–124, doi:10.1016/0273-1177(90)90172-V.

## Balloon system [D-ag unless marked]

| Item | Value | Source |
|---|---|---|
| Envelope | closed spherical superpressure, Teflon fabric + Teflon film | TM-88516 p. 19 |
| Diameter | **3.4 m** at nominal 30 mbar overpressure (TM-88516 p. 19); **3.54 m nominal** (PDS instrument file) — the two primary-ish sources disagree | both |
| Volume | 19.6 m³ at zero overpressure; +1.0 m³ per +10 mbar | TM-88516 p. 19 |
| Total mass | **21 kg** = 12.5 kg envelope + 2.0 kg helium + 6.5 kg gondola | TM-88516 pp. 19–20 |
| Gondola | 6.5 kg (TM-88516) vs 6.9 kg (PDS file); ~1.2 m long, 13 m tether | both |
| Lift gas | helium | TM-88516 |
| Float altitude | "53-54 km" design/observed (TM-88516 p. 9, 19); "54 km" (TDA report) | |
| Deployment | at ~midnight local time; VEGA-1 8°1′N 176°9′E, VEGA-2 7°5′S 179°8′E (TM p. 9) | |
| Lifetime | 46 h each (battery-limited); 11–13 Jun and 15–17 Jun 1985 | TM p. 9–10; TDA p. 1 |
| Altitude loss over flight | ~500 m (helium diffusion), partly compensated by solar heating on dayside | TM p. 11 |
| Total system mass incl. deployment hardware | 120 kg | TM p. 8 |
| Transmitter | 1667.9 MHz, ~4.5 W | TM p. 21 |

## Horizontal winds [D-ag]

- Mean zonal (westward) speed from Doppler: **69 ± 1 m/s (VEGA-1), 66 ± 1 m/s (VEGA-2)** at 53–54 km
  (TM-88516 Andreev et al., abstract and p. 44: fits u0 = 69.3 and 66.4 m/s). Doppler residuals imply
  wind variations of not more than 4–6 m/s.
- PDS level-3 file, VLBI-derived U (westward negative) — my statistics over flag ≥ 2 rows:
  VEGA-1 U = −68.7 ± 1.7 m/s (range −70.9 to −64.6, n = 61); VEGA-2 U = −64.8 ± 1.8 m/s (−68.2 to −60.6, n = 57).
- Meridional V: VEGA-1 +0.3 ± 1.5 m/s (−2.4 to +4.1); VEGA-2 +2.2 ± 1.7 m/s (−6.3 to +4.4) [D-ag, my stats];
  Crisp et al. 1990 abstract: VEGA-2 had ~2.5 m/s equatorward (northward) drift [A].
- Latitudes during flight: VEGA-1 7.96–9.08°N, VEGA-2 6.38–3.22°S; longitude span ~100° [D-ag].

## Pressure, temperature at float [D-ag, my stats, flag ≥ 2, excluding first hour]

| | VEGA-1 | VEGA-2 |
|---|---|---|
| p mean ± sd (hPa) | 577.8 ± 26.8 (529–708) | 577.7 ± 62.7 (524–884) |
| T mean ± sd (K) | 314.0 ± 3.3 (308.6–328.8) | 307.2 ± 6.9 (300.4–336.8) |
| Radius (km from centre) | 6105.2–6106.6 | 6103.2–6106.7 |

- VEGA-1 was **6.5 K warmer than VEGA-2 at the same pressure** for the whole flight (TM-88516 Linkin et al.,
  p. 36–37) [D-ag] → a real, persistent horizontal T contrast at ~54 km, not instrument error (both sensors
  agreed to ~1 K; VEGA-2 balloon agreed with VEGA-2 lander to <0.5 K).
- P–T points fall on adiabats within ±0.5 K → layer essentially adiabatic; session V39 suggests slight stability
  ~0.3 K/km (TM p. 39) [D-ag]. Crisp et al. 1990 abstract: static stability usually 0–2.0 K/km [A].

## Vertical winds and turbulence

From the PDS level-3 file [D-ag, my statistics, flag ≥ 2]:

| | W_a (air relative to balloon, anemometer) | W_b (balloon vertical speed) |
|---|---|---|
| VEGA-1 | mean −0.50, sd 0.66, range −3.50…+1.46 m/s; median |W_a| 0.48, 90th pct 1.27, 99th pct 2.66 m/s | sd 0.47, range −1.14…+3.31 m/s |
| VEGA-2 | mean −0.48, sd 0.73, range −3.29…+1.96 m/s; median |W_a| 0.31, 90th pct 1.61, 99th pct 2.93 m/s | sd 0.41, range −1.41…+2.75 m/s |

- |W_a| > 1 m/s in 17 % of samples for both balloons [D-ag, my stats].
- **Largest event:** VEGA-2 at mission hours ~32.6–34.7 (file time base): pressure rose from 588 to 884 hPa
  (balloon pushed down; ln(884/588) ≈ 0.41 scale heights ≈ 2.9 km at H≈7 km — my arithmetic), W_a −2 to −3.3
  m/s, W_b down to −1.4 m/s; recovered over ~4 h [D-ag]. Sagdeev et al. 1986 Science abstract: downdrafts up
  to 3.5 m/s pushed balloons up to 2.5 km below float [A]. Linkin et al. 1986 Science: peak 3 m/s [A].
- Blamont et al. (TM-88516 p. 52) [D-ag]: typical vertical winds 1–2 m/s; typical w > 0.5 m/s, maxima 4–5 m/s,
  "the maximum amplitudes may be lower" because of decoding ambiguities. Downdrafts dominate the record
  likely because balloons collect in convergence zones (sampling bias, not real mean subsidence).
- Kerzhanovich et al. (TM-88516 pp. 46–55) [D-ag]: Doppler (0.5 s sampling) velocity fluctuations at
  30–130 s periods: 0.05–1 m/s (VEGA-2), up to 2 m/s (VEGA-1); real wind variations ≈1.5× the measured
  balloon variations; turbulence (threshold 0.2 m/s) present >50 % of the time, day and night; calm↔turbulent
  transitions within 1–3 h; inferred cell sizes ~several hundred m (60 s scale) and tens of km (30–60 min).
  Gondola pendulum period 7–8 s; balloon float oscillation 300–400 s, ~0.2 m/s.
- Crisp et al. 1990 abstract [A]: vertical winds 1–3 m/s, turbulent episodes ~1 h, upward heat fluxes 0–350 W/m².

**Rotorcraft implication (my inference):** design for sustained vertical gusts of ±1 m/s routinely,
±3–3.5 m/s in hour-long episodes, and horizontal turbulent velocity fluctuations up to ~2–3 m/s on
30–130 s timescales, all embedded in a ~66–69 m/s westward mean flow at 54 km.

## VEGA-2 lander METEO profile (11 Jun 1985 descent at ~1 am LST, ~7°S) [D-ag, interpolated by me]

From `vg2lr.dat` (OCR'd from Linkin et al. 1987 tabulation, hand-corrected by Lorenz). Altitude is
"reconstructed"; ρ is **my** ideal-gas calc with MW 43.44 (not in file).

| z (km) | T (K) | p (bar) | ρ (kg/m³, my calc) | dT/dz (K/km, ±0.75 km fit) |
|---|---|---|---|---|
| 45 | 387.6 | 1.838 | 2.48 | −5.4 |
| 48 | 363.4 | 1.276 | 1.84 | −8.8 |
| 50 | 345.2 | 0.986 | 1.49 | −9.9 |
| 52 | 325.8 | 0.751 | 1.20 | −10.2 |
| 54 | 305.4 | 0.562 | 0.96 | −10.8 |
| 55 | 295.4 | 0.483 | 0.85 | −10.1 |
| 56 | 285.8 | 0.413 | 0.76 | −7.2 |
| 58 | 272.0 | 0.298 | 0.57 | −7.2 |
| 60 | 259.3 | 0.211 | 0.43 | −4.4 |
| 62 | 256.3 | 0.148 | 0.30 | (+4.2, near top of record; suspect start-of-descent transient) |

Top of record 62.92 km (0.126 bar, 262.8 K). VEGA-2 lander is ~3–4 K colder than PV probe mean at 50–56 km
(compare `A_pv_probes_seiff1980_pds.md`); TM-88516 states below 55 km the lander P–T is close to adiabatic.

## Caveats

- Telemetry compression (6 LSBs sent, MSBs estimated) → occasional ambiguous jumps; quality flags given.
- W_a shows a systematic ~−0.5 m/s mean in both balloons — possibly anemometer stiction/bias (the dataset
  catalog mentions stiction near zero RPM); treat mean W_a as unreliable, fluctuations as more trustworthy.
- Only ~46 h × 2 balloons, night → early morning, ±8° latitude.
- Altitude of balloons from radius: 6103–6107 km; subtract planetary radius (6051.8–6052 km) to get ~51–55 km.
