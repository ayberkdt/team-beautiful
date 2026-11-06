# A_pv_lgc_composition — Pioneer Venus Large-Probe gas chromatograph (in-cloud composition)

## Citation

- **Data (read in full, 3 samples):** Pioneer Venus SED bundle, LGC collection,
  `https://atmos.nmsu.edu/PDS/data/PDS4/pv_sed_bundle/data_lgc/lgc_low_atm_comp.csv` (+ `.xml` label),
  NSSDCA PSPA-00034 file 028. Bundle DOI 10.17189/m5zf-6f12.
- Paper describing it (NOT read): Oyama, V. I. et al. (1980), "Pioneer Venus gas chromatography of the lower
  atmosphere of Venus", *J. Geophys. Res.* 85(A13):7891–7902 (citation from memory, not verified).

## Values [D-ag] (label units: CO2, N2, H2O in percent; others ppm; 888.0 = not applicable)

| Sample | Altitude (km)* | p (bar) | CO2 % (±1σ) | N2 % (±1σ) | H2O % (±1σ) | SO2 ppm (±1σ) | O2 ppm | Ar ppm | CO ppm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 51.6 | 0.698 | 95.4 (±2.5) | 4.6 (±0.02) | 0.06 (no σ) | 600 (no σ; upper-limit-like) | 43.6 ± 2.9 | 60.5 ± 5.5 | 32.2 ± 7.2 |
| 2 | 41.7 | 2.91 | 95.9 (±0.7) | 3.54 (±0.005) | 0.519 (±0.008) | 176 (+296/−0, 1σ) | 16.0 ± 0.9 | 63.8 ± 1.6 | 30.2 ± 2.1 |
| 3 | 21.6 | 17.8 | 96.4 (±0.1) | 3.41 (±0.002) | 0.135 (±0.002) | 185 ± 43 | n/a | 67.2 ± 0.3 | 19.9 ± 0.4 |

*Altitude interpolated from LAS data (label). Upper limits at 51.6 km (ppm): H2 200, CH4 10, H2S 40, OCS 40.

## Reading

- Bulk composition below the clouds: **CO2 ≈ 96.4 %, N2 ≈ 3.4–3.5 %** (most precise sample, 21.6 km) [D-ag].
  This supports MW ≈ 43.4 used by LAS (`A_pv_probes_seiff1980_pds.md`).
- SO2 ~180 ppm at 22–42 km [D-ag] with large uncertainty.
- The LGC H2O values (0.52 % at 41.7 km) are, to my knowledge, much higher than later remote-sensing values
  (tens of ppm) and were questioned in the literature — **this is my memory, not verified in this session**.
  Do not use LGC H2O for design.

## Caveats

- Three samples only, one sounding; the 51.6 km sample (in the cloud) has the largest errors.
- Marcq et al. 2018 composition review (Space Sci Rev 214:10) — attempted; the Springer PDF URL returned the
  HTML landing page without body text, so not read.
