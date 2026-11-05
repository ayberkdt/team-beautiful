# A_tomasko1980_lsfr_solar_flux — Solar flux inside the clouds (Pioneer Venus Large-Probe LSFR)

## Citations

1. **Data (read in full):** Pioneer Venus Large Probe Solar Flux Radiometer (LSFR) table, PDS4 SED bundle
   (Seiff, Suomi, Barnes, Keating, Tomasko; DOI 10.17189/m5zf-6f12):
   `https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/data_lsfr/lsfr_solar_flux.csv` (+ `_descr.txt`, `.xml`).
   373 data rows, 64.30 km → 0.12 km.
2. **Paper describing the data (NOT read; only search-snippet):** Tomasko, M. G., Doose, L. R., Smith, P. H.,
   Odell, A. P. (1980), "Measurements of the flux of sunlight in the atmosphere of Venus",
   *J. Geophys. Res.* 85(A13), 8167–8186, doi:10.1029/JA085iA13p08167.
3. **NASA report (read pp. 6–10 of the PDF text):** Tomasko, M. G. (1981, dated 15 Dec 1981), "The Thermal
   Balance of the Lower Atmosphere of Venus", NASA-CR-169900 (N83-19672), Final Report NAGW-55, Univ. of Arizona
   (chapter written for the *Venus* book, Hunten et al. eds., 1983).
   `https://ntrs.nasa.gov/api/citations/19830011401/downloads/19830011401.pdf`
4. **NASA report (skimmed):** Tomasko, M. G., Doose, L. R. (1982), "Absorption of sunlight in the atmosphere of
   Venus", NASA-CR-169874 (N83-18630). `https://ntrs.nasa.gov/api/citations/19830010359/downloads/19830010359.pdf`

## What the data are [D-ag] (descriptor file)

- Probe site 4.4°N, local time 07:38, **solar zenith angle 65.7°** (from PDS mission table; see
  `A_pv_probes_seiff1980_pds.md`). So fluxes are for cos(SZA) ≈ 0.41 (my arithmetic), not overhead sun.
- Channels: VIS 0.40–0.96 µm; COMBINED 0.41–1.78 µm (IR part unmeasurable after 19:10:46 GRT, and
  "below about 50 km the combined channel fluxes must be viewed with caution"); NB 0.59–0.67 µm.
- Altitude/pressure from an **April 1979 LAS table** (descriptor warns it may not be the latest).
- Units W/m² **in the instrument passband only** — not total solar.

## Numbers (linear interpolation in the table, by me) [D-ag]

| z (km) | VIS down | VIS up | VIS net | up/down VIS | COMB down | COMB up | COMB net | down(z)/down(64 km) VIS / COMB |
|---|---|---|---|---|---|---|---|---|
| 64 | 384.1 | 348.7 | 35.3 | 0.91 | 515.7 | 459.5 | 56.1 | 1.00 / 1.00 |
| 62 | 349.3 | 317.2 | 32.1 | 0.91 | 455.3 | 405.5 | 49.7 | 0.91 / 0.88 |
| 60 | 319.0 | 284.7 | 34.3 | 0.89 | 399.3 | 348.3 | 51.0 | 0.83 / 0.77 |
| 58 | 284.7 | 254.9 | 29.9 | 0.90 | 341.5 | 296.0 | 45.5 | 0.74 / 0.66 |
| 56 | 269.1 | 242.5 | 26.6 | 0.90 | 312.8 | 272.1 | 40.7 | 0.70 / 0.61 |
| 55 | 263.9 | 236.1 | 27.8 | 0.89 | 302.6 | 261.2 | 41.5 | 0.69 / 0.59 |
| 54 | 256.2 | 228.3 | 27.8 | 0.89 | 289.2 | 248.4 | 40.8 | 0.67 / 0.56 |
| 52 | 239.4 | 210.3 | 29.0 | 0.88 | 260.9 | 220.2 | 40.7 | 0.62 / 0.51 |
| 50 | 221.7 | 193.7 | 28.0 | 0.87 | 233.1 | 194.9 | 38.1 | 0.58 / 0.45 |
| 48 | 193.1 | 164.3 | 28.8 | 0.85 | 191.1 | 152.9 | 38.2 | 0.50 / 0.37 |
| 45 | 184.3 | 154.5 | 29.9 | 0.84 | 177.2 | 137.9 | 39.3 | 0.48 / 0.34 |
| 40 | 179.3 | 149.9 | 29.3 | 0.84 | 170.4 | 132.3 | 38.1 | 0.47 / 0.33 |

Top row of the file (64.30 km, 0.10 atm): VIS down/up/net 389.7/353.8/35.9; COMB 525.2/468.0/57.2 W/m² [D-ag].
Near-surface row (0.12 km): VIS down 19.8, up 3.2, net 16.6 W/m² [D-ag].

**Engineering reading (for solar-powered rotorcraft):** at 50–56 km the light field is almost isotropic:
upward flux is 87–90 % of downward (VIS) [D-ag]. A down-facing surface receives nearly as much as an
up-facing one. Net (down−up) is only ≈ 10–15 % of down [D-ag], consistent with the NASA report statement
that net flux is "a moderately small fraction (15%) of either one" at cloud level [D-ag, ref 3 p. 8].
Downward VIS flux at 55 km ≈ 0.69 of its 64 km value; at 50 km ≈ 0.58 [D-ag].

## Whole-atmosphere budget numbers from ref. 3 [D-ag, read in NTRS PDF pp. 7–10]

- Bolometric spherical albedo 0.77 ± 0.07 (Irvine); PV OIR emitted flux 157 ± 6 W/m², T_eff 229.4 ± 2.2 K.
- About half the absorbed sunlight is absorbed above 64 km.
- Between 64 and 57 km about 20 W/m² absorbed; between 57 and 48 km only ~8 W/m² more (cloud particles in this
  region have visible optical depth ~17); very little between 48 and 40 km; 15–20 W/m² between 40 and 15 km;
  ~17 W/m² at the surface (≈ 2.5 % of incident sunlight). These are **global-average** net-absorption
  numbers, not local fluxes.

## Caveats

- One sounding, SZA 65.7°, morning. Fluxes scale roughly with cos(SZA) and cloud opacity, which varies.
- Fluxes are in passbands (0.40–0.96 or 0.41–1.78 µm), not total solar; ratio columns are more transferable
  than absolute W/m².
- Ref. 4 reports a labeling error in the best-fit cloud model description (model F) of the 1980 paper
  [A — from search snippet, not checked in PDF text].
- The fraction of top-of-atmosphere flux reaching 64 km is NOT in the data file; I did not find it in a
  primary source in this session.
- Venera 11/12 (Moroz/Ekonomov) spectrophotometer profiles: not accessed in this session.
