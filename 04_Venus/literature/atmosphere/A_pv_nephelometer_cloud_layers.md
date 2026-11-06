# A_pv_nephelometer_cloud_layers — Cloud vertical structure at 4 sites (Pioneer Venus nephelometers, raw PDS)

## Citations

- **Data (read in full):** Pioneer Venus SED bundle, nephelometer collection (LN = large probe, SN = small
  probes), `https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/data_neph/{ln,sn_day,sn_night,sn_north}_backscatter.csv`
  (+ .xml). Columns [D-ag]: GRT (HH:MM:SS.s), backscatter cross section in 1/(m·sr), event note.
  Source: NSSDCA PSPA-00034 file 053, Table 1.2. Bundle DOI 10.17189/m5zf-6f12.
- Paper describing it (NOT read): Ragent, B., Blamont, J. (1980), "The structure of the clouds of Venus:
  results of the Pioneer Venus nephelometer experiment", *J. Geophys. Res.* 85(A13):8089–8105
  (cited as "Ragent and Blamont, J. Geophys. Res. 85, 8099 (1980)" in NASA TM-88516 — page differs; not verified).

## Processing (mine)

GRT → altitude via each probe's LAS/SAS state table (same GRT base), backscatter averaged in 1-km bins.
Script `D:\tmp_ideathon\venus\scripts\neph.py`. Rows before "WINDOW COVER OPENED" events are not cloud data
(e.g. the Night-probe 65 km bin value 2.95×10⁻² is pre-cover-opening — artifact).

## Mean backscatter, 10⁻⁴ m⁻¹ sr⁻¹ [D-ag, binned by me]

| z (km) | Large 4.4N | Day 31.3S | Night 28.7S | North 59.3N |
|---|---|---|---|---|
| 64 | 1.27 | 0.49 | 1.31 | n/a |
| 62 | 1.50 | 0.86 | 1.65 | n/a |
| 60 | 1.58 | 0.91 | 1.74 | 2.05 |
| 58 | 1.43 | 0.87 | 1.79 | 2.35 |
| 57 | 1.35 | 1.19 | 2.02 | 2.35 |
| 56 | 1.51 | 1.30 | 2.26 | 2.46 |
| 55 | 1.80 | 1.39 | 2.33 | 2.67 |
| 54 | 1.86 | 1.48 | 2.35 | 2.76 |
| 53 | 1.91 | 1.54 | 2.53 | 2.90 |
| 52 | 1.90 | 1.58 | 2.58 | 2.87 |
| 51 | 1.84 | 1.32 | 2.41 | 2.96 |
| 50 | 1.55 | 0.63 | 2.92 | 2.53 |
| 49 | 2.56 | 0.49 | 2.82 | 1.95 |
| 48 | 2.50 | 0.37 | 2.95 | 2.06 |
| 47 | 1.24 | 0.38 | 2.14 | 1.65 |
| 46 | 1.02 | 0.36 | 1.39 | 1.65 |
| 40 | 1.00 | 0.33 | 1.31 | 1.64 |
| 30 | 1.00 | 0.38 | 1.34 | 1.63 |

## Reading (my interpretation)

- Each probe has a flat sub-cloud level (30–45 km: ≈1.0, 0.34, 1.3, 1.6) that is an **instrument-specific
  offset/background**, so compare each probe's excess over its own sub-cloud level, not absolute numbers.
- **Cloud base:** Large ≈ 47 km (sharp drop 48→47); Night ≈ 47 km; North ≈ 49–50 km; Day ≈ 50 km
  (Day shows almost no lower-cloud enhancement) → **cloud base 47–50 km depending on site**.
- **Lower-cloud dense layer at 48–49 km** in Large and Night probes (largest excess), absent at Day site —
  consistent with Titov et al. 2018 statement that some probes saw the 47–50 km optically thick layer and some
  did not.
- Middle cloud 51–56 km: steady enhanced backscatter at all four sites; slight minimum at ~57–58 km in Large
  (the "gap" near 56–58 km noted by Titov et al.).
- Data above ~64 km sparse/absent in these files.

## Caveats

- Backscatter calibration and day-light contamination (Day probe) not reviewed — Ragent & Blamont 1980 not read.
- Mass loading cannot be derived from backscatter alone without particle-size assumptions.
