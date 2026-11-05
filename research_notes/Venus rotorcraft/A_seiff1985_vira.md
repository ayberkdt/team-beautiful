# A_seiff1985_vira — VIRA lower-atmosphere model (Seiff et al. 1985): access status + machine reproduction

## Citation (target)

Seiff, A., Schofield, J. T., Kliore, A. J., Taylor, F. W., Limaye, S. S., Revercomb, H. E., Sromovsky, L. A.,
Kerzhanovich, V. V., Moroz, V. I., Marov, M. Ya. (1985), "Models of the structure of the atmosphere of Venus
from the surface to 100 kilometers altitude", *Adv. Space Res.* 5(11):3–58, doi:10.1016/0273-1177(85)90197-8.
(First five authors confirmed from the NTRS record 19870027595; the rest from memory, not verified.)

## Access status — original paper NOT read

Tried:
- NTRS record 19870027595 (API JSON read): type "Reprint", **no downloadable file**.
- ADS full-text scan `articles.adsabs.harvard.edu/pdf/1985AdSpR...5k...3S`: HTTP 403.
- ADS abstract page: returns a human-verification (CAPTCHA) page — not bypassed.
- ECSS-E-ST-10-04C Venus annex on SPENVIS (`spenvis.oma.be/ecss/e_st_10_04c/ecss_18_07_02.htm`):
  HTTP 503 "site unavailable". Wayback availability API: HTTP 429.
- GitHub search for Venus-GRAM / VIRA data files: no hits (NASA distributes Venus-GRAM via software.nasa.gov,
  MFS-32314-1, request-based).
- Elsevier publisher copy: paywalled, not attempted.

**So no number in this file comes from the Seiff et al. 1985 tables themselves.**

## Machine reproduction used instead: Venus-GRAM output (VIRA-based) [D-ag of a tertiary product]

Source file: `https://raw.githubusercontent.com/athulpg007/AMAT/master/atmdata/Venus/venus-gram-avg.dat`
(AMAT aerocapture toolkit, A. P. Girija; its README states the GRAM profiles are "samples of atmospheric data
from Global Reference Atmospheric Model (GRAM) software ... developed by NASA Marshall Space Flight Center").
Venus-GRAM below 100 km "is based on" VIRA and "VIRA data depends on height and latitude" (Justh 2017, NASA
GRAM workshop slides, NTRS 20170012290, p. 3 [D-ag]). Which latitude band/options generated the AMAT "avg"
file is **not documented** in the file; its density column is identical to AMAT's `LAT10N.txt` DENSAV
column, so it is most likely the VIRA low-latitude (<30°) profile. Surface row: 735.3 K, 92.09 bar,
64.79 kg/m³ — matches the commonly quoted VIRA surface values (my memory, not verified against Seiff 1985).
Reference radius in the companion LAT files: 6051.89 km (vs 6052.0 km for Pioneer Venus probe altitudes).

| z (km) | T (K) | p (bar) | ρ (kg/m³) | a (m/s) |
|---|---|---|---|---|
| 40 | 417.6 | 3.5010 | 4.4040 | 320.1 |
| 45 | 385.4 | 1.9790 | 2.6930 | 307.8 |
| 48 | 366.4 | 1.3750 | 1.9670 | 300.2 |
| 50 | 350.5 | 1.0660 | 1.5940 | 293.6 |
| 52 | 333.3 | 0.8168 | 1.2840 | 286.4 |
| 53 | 323.0 | 0.7109 | 1.1530 | 281.9 |
| 54 | 312.8 | 0.6163 | 1.0320 | 277.4 |
| 55 | 302.3 | 0.5314 | 0.9207 | 272.8 |
| 56 | 291.8 | 0.4559 | 0.8183 | 268.0 |
| 57 | 282.5 | 0.3891 | 0.7212 | 263.7 |
| 58 | 275.2 | 0.3306 | 0.6289 | 260.3 |
| 60 | 262.8 | 0.2357 | 0.4694 | 254.4 |
| 62 | 254.5 | 0.1659 | 0.3411 | 250.4 |
| 64 | 247.5 | 0.1156 | 0.2443 | 247.0 |
| 65 | 244.3 | 0.0960 | 0.2055 | 245.4 |
| 70 | 229.8 | 0.0369 | 0.0839 | 238.1 |

Latitude dependence of mean density (DENSAV) from AMAT `LAT10N/40N/60N/80N.txt` (first profile block)
[D-ag, tertiary], kg/m³:

| z (km) | 10°N | 40°N | 60°N | 80°N |
|---|---|---|---|---|
| 45 | 2.693 | 2.700 | 2.720 | 2.766 |
| 50 | 1.594 | 1.587 | 1.588 | 1.613 |
| 55 | 0.921 | 0.916 | 0.906 | 0.886 |
| 60 | 0.469 | 0.472 | 0.467 | 0.410 |
| 65 | 0.206 | 0.201 | 0.187 | 0.159 |

Venus-GRAM low/high density envelope (DENSLO/DENSHI) at 10°N: 50 km 1.563–1.626; 55 km 0.897–0.945;
60 km 0.454–0.485 kg/m³ → about **±2–3 %** (my arithmetic). This is the GRAM dispersion model, not a VIRA
statement.

## Cross-check against primary in-situ data (my comparison)

| z | VIRA/GRAM T, p, ρ | PV 4-probe mean T, p, ρ | VEGA-2 lander T, p |
|---|---|---|---|
| 50 | 350.5, 1.066, 1.594 | 347.9, 1.029, 1.550 | 345.2, 0.986 |
| 55 | 302.3, 0.531, 0.921 | 299.1, 0.508, 0.889 | 295.4, 0.483 |
| 60 | 262.8, 0.236, 0.469 | 257.8, 0.223, 0.452 | 259.3, 0.211 |

VIRA/GRAM is 2.5–5 K warmer, 3.5–5 % higher p and ~3 % higher ρ than the PV probe mean at 50–60 km.
Differences of this size are within the probe-to-probe spread (`A_pv_probes_seiff1980_pds.md`) and
consistent with Banerjee et al. 2026 (see `A_limaye2018_banerjee2026_thermal_review.md`) who find VGRAM
low/mid-latitude temperatures differ from radio occultations by >5 K up to ~60 km.

## Static stability statement

Could not read VIRA's own stability text. Primary-data result (PV probes, VEGA) is in
`A_pv_probes_seiff1980_pds.md` and `A_vega1985_balloons_lander.md`: near-neutral ~51–56 km.

## Caveats

- Tertiary chain: Seiff 1985 tables → Venus-GRAM (MSFC) → AMAT data file. Exact GRAM options unknown.
- If the team needs the authoritative VIRA tables, the library/ILL copy of Adv. Space Res. 5(11) is required.
