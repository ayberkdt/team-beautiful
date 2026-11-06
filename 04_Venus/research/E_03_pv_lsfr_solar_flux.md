# E_03 — Pioneer Venus LSFR solar flux profile (PDS), re-read 5 Nov 2026

- **Source:** Tomasko et al. 1980 (JGR 85) data, `https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/data_lsfr/lsfr_solar_flux.csv` + `lsfr_solar_flux_descr.txt`.
- **Accessed:** 2026-11-05. Read level: full file + descriptor **[D]**.
- **Descriptor facts [D]:** columns time, p (atm), altitude (km, from the LAS table of 11 Apr 1979), then VIS (0.40–0.96 µm), COMBINED (0.41–1.78 µm) and NB (0.59–0.67 µm) down/up/net flux, W/m². "Below about 50 kilometers altitude the combined channel fluxes must be viewed with caution." Sounder site: solar zenith angle 65.7° (earlier note).
- Top sample 64.30 km: VIS down 389.7, up 353.8 W/m²; COMBINED down 525.2, up 468.0 W/m².

## Values [K on D] (COMBINED channel, interpolated)
| z km | down W/m² | down / down(64.3 km) | up/down |
|---:|---:|---:|---:|
| 40 | 170.4 | 0.32 | 0.776 |
| 45 | 177.2 | 0.34 | 0.778 |
| 50 | 233.1 | 0.44 | 0.836 |
| 55 | 302.6 | 0.58 | 0.863 |
| 60 | 399.3 | 0.76 | 0.872 |
| 64 | 515.7 | 0.98 | 0.891 |

Use: up/down = "albedo" seen by a bifacial panel's underside (0.84–0.89 at 50–64 km). The absolute numbers are for SZA 65.7° and a partial band; scale with a radiative model (doc 25 uses Landis & Haag 2013 for absolute array output).
LSFR measures hemispheric flux only; it cannot split direct and diffuse. Direct beam: see databook §3 (τ from E_13).
