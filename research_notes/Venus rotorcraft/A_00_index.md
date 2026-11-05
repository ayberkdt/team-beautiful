# A_00_index — Venus atmosphere from primary sources (research block A)

Written 2026-11-04. Tags: **[D-ag]** = read in the source's own text/table/data file in this session;
**[A]** = only from abstract / search snippet / secondary page. Every interpolation, mean or statistic computed
from a data file is marked as mine in the per-source notes; scripts are in `D:\tmp_ideathon\venus\scripts\`,
downloaded data in `D:\tmp_ideathon\venus\downloads\`.

## Files

| File | Source | What was read | Key content |
|---|---|---|---|
| `A_pv_probes_seiff1980_pds.md` | Pioneer Venus LAS/SAS raw tables (PDS SED bundle), Seiff et al. 1980 | full data files | T, p, ρ at 4 sites; site spread; lapse rate vs adiabatic |
| `A_counselman1980_pv_dlbi_winds.md` | PV DLBI wind tables (PDS), Counselman et al. 1980 | full data files + user guide | zonal/meridional wind 10–64 km at 4 sites |
| `A_tomasko1980_lsfr_solar_flux.md` | PV LSFR solar-flux table (PDS); Tomasko NASA-CR-169900 | full data file; report pp. 6–10 | up/down/net flux 64→0 km |
| `A_pv_nephelometer_cloud_layers.md` | PV nephelometers (PDS) | full data files | cloud base 47–50 km by site |
| `A_pv_lgc_composition.md` | PV gas chromatograph (PDS) | full data file | CO2/N2/SO2 at 51.6, 41.7, 21.6 km |
| `A_vega1985_balloons_lander.md` | VEGA balloon + VEGA-2 lander archive (PDS, Lorenz et al. 2020); NASA TM-88516 | full data files; TM pp. 8–61 | balloon specs, 54 km P/T, vertical winds, turbulence, zonal wind; lander profile |
| `A_seiff1985_vira.md` | VIRA (Seiff et al. 1985) | **original not accessible**; Venus-GRAM output (AMAT repo) used | VIRA-based T, p, ρ, a vs z; latitude ρ |
| `A_limaye2018_banerjee2026_thermal_review.md` | Limaye et al. 2018 SSR; Banerjee et al. 2026 arXiv | full PDFs (key pages) | variability bands, stability, VIRA validity |
| `A_winds_cloudtracking_vex_akatsuki.md` | Sánchez-Lavega 2008; Horinouchi 2017 (preprint); Peralta 2018 (preprint) | full PDFs | cloud-tracked winds 47/61/66 km; equatorial jet; decadal ±15 m/s |
| `A_titov2018_clouds.md` | Titov et al. 2018 SSR | full PDF (key pages) | layer table, particle modes, H2SO4 wt% |
| `A_lorenz2018_lightning.md` | Lorenz 2018 PEPS; Titov 2018 §8; Lorenz 2019 GRL [A] | full PDF | lightning contested; LAC non-detection |
| `A_nist_co2_properties.md` | NIST WebBook (Span–Wagner; Laesecke–Muzny; Huber) | data tables | μ, a, γ, cp, ρ of CO2 at 250–350 K, 0.5/1 bar |
| `A_kerzhanovich_limaye1985_vira_winds.md` | VIRA wind chapter | **not accessible** | — |
| `A_knollenberg_hunten1980_lcps.md` | PV LCPS paper | **not read directly** | substitute pointers |
| `A_venera_flux_moroz_ekonomov.md` | Venera flux profiles | **not accessed** | secondary statements only |

## Best values at 45–65 km

"PV mean" = mean of the four Pioneer Venus probes (Dec 1978; 31.3°S–59.3°N per the PDS SED page — corrected 4 Nov after the audit, was "4.4°N–59.3°N"; 00–08 h LT), interpolated by me
from the PDS tables [D-ag data]. "min/max" = envelope over the four PV probes, the VEGA-2 lander (Jun 1985,
~7°S, 01 h LT) and VIRA-via-Venus-GRAM. "VIRA" = Venus-GRAM average profile (tertiary reproduction of
Seiff et al. 1985, low latitude). Altitudes: PV relative to 6052.0 km radius; GRAM 6051.89 km.
Tables generated with `datawiz.tablo.markdown_tablo` from `D:\tmp_ideathon\venus\scripts\index_table.py`.

**VIRA is warmer and denser than the in-situ soundings: it sits at the top of the envelope for p and ρ at every level.**

Temperature

| z (km) | T PV mean (K) | T min (K) | T max (K) | T VIRA (K) |
|---:|---:|---:|---:|---:|
| 45 | 384.3 | 381.7 | 387.6 | 385.4 |
| 50 | 347.9 | 343.7 | 351.8 | 350.5 |
| 52 | 329.8 | 323.5 | 334.3 | 333.3 |
| 54 | 309.5 | 303.0 | 313.8 | 312.8 |
| 55 | 299.1 | 292.6 | 302.8 | 302.3 |
| 56 | 288.5 | 282.1 | 291.8 | 291.8 |
| 58 | 271.1 | 262.2 | 276.0 | 275.2 |
| 60 | 257.8 | 243.4 | 268.1 | 262.8 |
| 62 | 251.7 | 249.4 | 256.3 | 254.5 |
| 65 | 239.0 | 238.6 | 244.3 | 244.3 |

Pressure

| z (km) | p PV mean (bar) | p min (bar) | p max (bar) | p VIRA (bar) |
|---:|---:|---:|---:|---:|
| 45 | 1.921 | 1.838 | 1.979 | 1.979 |
| 50 | 1.029 | 0.986 | 1.066 | 1.066 |
| 52 | 0.786 | 0.751 | 0.817 | 0.817 |
| 54 | 0.590 | 0.562 | 0.616 | 0.616 |
| 55 | 0.508 | 0.483 | 0.531 | 0.531 |
| 56 | 0.435 | 0.413 | 0.456 | 0.456 |
| 58 | 0.314 | 0.298 | 0.331 | 0.331 |
| 60 | 0.223 | 0.210 | 0.236 | 0.236 |
| 62 | 0.159 | 0.148 | 0.166 | 0.166 |
| 65 | 0.092 | 0.092 | 0.096 | 0.096 |

Density

| z (km) | ρ PV mean (kg/m³) | ρ min (kg/m³) | ρ max (kg/m³) | ρ VIRA (kg/m³) |
|---:|---:|---:|---:|---:|
| 45 | 2.624 | 2.478 | 2.693 | 2.693 |
| 50 | 1.550 | 1.492 | 1.594 | 1.594 |
| 52 | 1.248 | 1.204 | 1.284 | 1.284 |
| 54 | 0.999 | 0.962 | 1.032 | 1.032 |
| 55 | 0.889 | 0.854 | 0.921 | 0.921 |
| 56 | 0.790 | 0.755 | 0.818 | 0.818 |
| 58 | 0.606 | 0.572 | 0.629 | 0.629 |
| 60 | 0.452 | 0.426 | 0.469 | 0.469 |
| 62 | 0.331 | 0.302 | 0.341 | 0.341 |
| 65 | 0.202 | 0.200 | 0.205 | 0.205 |

Row notes: 62 km PV mean = 3 probes (North stops at 61.3 km); 65 km PV mean = Day + Night only (Sounder file
tops at 64.83 km: 246.3 K, 0.0925 bar, 0.1964 kg/m³); VEGA-2 lander tops at 62.9 km. VEGA-2 lander ρ is my
ideal-gas calculation (MW 43.44). Real-world band is wider than this envelope: Banerjee et al. 2026 find
VIRA/GRAM–radio-occultation differences >5 K at low/mid latitudes ≤60 km and >10 K poleward of ~50° at 60–80 km;
VEGA-1 vs VEGA-2 differed by 6.5 K at the same pressure (~54 km).

Zonal wind (westward, PV DLBI 4 probes, ±0.5 km bins; `scripts/index_wind.py`) [D-ag data]

| z (km) | n probes | u mean (m/s) | u min (m/s) | u max (m/s) | max abs meridional (m/s) |
|---:|---:|---:|---:|---:|---:|
| 45 | 4 | 53 | 48 | 60 | 5 |
| 50 | 4 | 60 | 53 | 68 | 4 |
| 52 | 4 | 61 | 53 | 70 | 7 |
| 54 | 4 | 63 | 58 | 70 | 7 |
| 55 | 3 | 65 | 59 | 74 | 6 |
| 56 | 3 | 62 | 60 | 66 | 2 |
| 58 | 3 | 76 | 65 | 86 | 4 |
| 60 | 2 | 85 | 79 | 91 | 6 |
| 62 | 1 | 96 | 96 | 96 | 8 |
| 64 | 1 | 98 | 98 | 98 | 5 |

Other wind sources to widen the band (all [D-ag]):
- 53–54 km VEGA balloons (Jun 1985, ±8° lat): 69 ± 1 and 66 ± 1 m/s (Doppler); VLBI U 60.6–70.9 m/s; V −6.3…+4.4 m/s.
- ~47 km VEX/VIRTIS 2006–07: 60 ± 10 m/s; ~61 km: 62 ± 10 m/s (75 ± 10 in Apr 2006); ~66 km: 102 ± 10 m/s.
- 45–60 km layer Akatsuki 2016: equatorial jet ~85 m/s; zonal means ~10 m/s faster than VEX.
- Decadal variability of nightside lower-cloud winds up to 30 m/s (oscillation amplitude ~15 m/s) (Peralta 2018).
- Shear: <1 m/s per km 47–61 km, 8 ± 2 m/s per km 61–66 km (VIRTIS); PV Large probe 56→60 km ≈ 6 m/s per km.

**Suggested design band (my synthesis): zonal wind at 50–56 km = 65 m/s nominal, 50–90 m/s envelope;
meridional ≤ 10 m/s.**

Vertical wind and turbulence (data exist only near 50–55 km)

| Altitude | Quantity | Value | Source |
|---|---|---|---|
| 53–55 km (float), down to ~51 km in events | air vertical speed rel. balloon, W_a | sd 0.65–0.75 m/s; range −3.5…+2.0 m/s; |W_a| > 1 m/s in 17 % of samples | VEGA PDS level-3 files, my stats [D-ag] |
| 53–54 km | downdraft episodes | 2–4 m/s, lasting ~1–2 h; VEGA-2 pushed down ~3 km (588→884 hPa) | TM-88516 [D-ag]; PDS data [D-ag]; Science 1986 abstract 3.5 m/s [A] |
| 53–54 km | typical vertical wind | 1–2 m/s; maxima 4–5 m/s (possibly overestimated) | Blamont et al., TM-88516 p. 52 [D-ag] |
| 53–54 km | horizontal velocity fluctuation, 30–130 s periods | 0.05–1 m/s (VEGA-2), up to 2 m/s (VEGA-1); real ≈1.5× measured; turbulent >50 % of time | Kerzhanovich et al., TM-88516 [D-ag] |
| ~45–60 km, all latitudes | Richardson number | low → turbulence possible | Limaye 2018 citing Piccialli 2012 [D-ag] |
| 51–56 km | static stability | near-neutral (−dT/dz ≈ Γ_ad ≈ 9.8–10.4 K/km within ±1 K/km) at all 4 PV sites | my calc from PV data [D-ag data] |
| 45–50 and 57–64 km | static stability | stable; −dT/dz 2–9 K/km below adiabatic; N ≈ 0.008–0.019 s⁻¹ | my calc from PV data |

## Other headline numbers

- Solar (PV LSFR, SZA 65.7°): up/down flux ratio 0.87–0.90 at 50–56 km; down flux at 55 km ≈ 0.69 (VIS) of the
  64 km value; net ≈ 10–15 % of down [D-ag].
- Clouds: lower 47.5–50.5, middle 50.5–56.5, upper 56.5–70 km; τ(0.63 µm) 6–12 / 8–10 / 6–8; H2SO4 75–90 wt%
  (98 % at cloud bottom in models) [D-ag, Titov 2018]. PV nephelometers: cloud base 47–50 km by site.
- CO2 at 300 K, 0.5 bar: μ = 15.0 µPa·s, a = 269.8 m/s, γ = 1.290, cp = 849 J/(kg K) [D-ag, NIST].
- Bulk composition: CO2 96.4 %, N2 3.41 % at 21.6 km (PV LGC) [D-ag].
- Lightning: unproven; Akatsuki LAC 16.8 h, no flashes → optical rate >1000× below Earth's [A, Lorenz 2019];
  Lorenz 2018: "sporadic discharges different from Earth — not excluded" [D-ag].

## Gaps

- Authoritative VIRA tables (Seiff 1985) and VIRA wind chapter (Kerzhanovich & Limaye 1985) not obtained (paywall/CAPTCHA).
- Cloud mass loading (mg/m³) not obtained.
- No afternoon in-situ sounding exists in the data used (all PV/VEGA at 00–08 h LT).
