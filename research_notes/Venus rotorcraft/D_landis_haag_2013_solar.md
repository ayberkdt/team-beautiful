# D_landis_haag_2013_solar — Triple-junction solar power vs altitude in the Venus atmosphere

## Citation
Landis, G. A. (NASA Glenn) & Haag, E. (Australian National University) (2013). *Analysis of
Solar Cell Efficiency for Venus Atmosphere and Surface Missions.* AIAA conference paper,
11th International Energy Conversion Engineering Conference (IECEC), July 2013 (date
2013-07-14 per JAXA repository record; AIAA paper number not read — commonly cited as
AIAA 2013-4028 [A]). NTRS 20150016298.
https://ntrs.nasa.gov/api/citations/20150016298/downloads/20150016298.pdf

## What I read
Full 13-page paper (text extraction); Table 1 read from rendered image of p.10.

## Model assumptions [D-ag]
- Venus exoatmospheric ("Venus AM0") intensity **2600 W/m²** (p.5).
- Spectrum vs altitude from **Venera 11** spectrophotometer transmission data (p.5).
- Array efficiency at standard AM0 = **29 %** (= 32.2 % cell × 90 % packing factor) (p.9).
- Cell temperature = local atmospheric temperature; lapse ~7.7 °C/km (p.3). Sun near zenith,
  equatorial, local noon (p.9).
- Triple-junction (GaInP2/GaAs/Ge) is best at all altitudes; the Ge bottom cell never
  limits current, so dual-junction = triple-junction in current (p.6, p.9).
- At altitudes above ~50 km effective intensity exceeds Earth AM0, so the Voc intensity
  correction is slightly positive (p.8).

## Table 1 (p.10) — triple-junction array vs altitude [D-ag]
| Alt km | T °C | Voc int. factor | Voltage eff. | Current factor | "Effective" eff. | Limiting | Power W/m² |
|---|---|---|---|---|---|---|---|
| 40 | 175 | 0.98 | 14.80 % | 29.01 % | 4.29 % | Middle | 112.2 |
| 45 | 137 | 0.98 | 23.06 % | 30.09 % | 6.94 % | Middle | 181.4 |
| **50** | 107 | 0.99 | 25.09 % | 39.02 % | **9.79 %** | Middle | **256.0** |
| **55** | 69 | 1.01 | 27.65 % | 55.95 % | **15.47 %** | Middle | **404.4** |
| **60** | 19 | 1.01 | 30.79 % | 69.47 % | **21.39 %** | Middle | **559.2** |
| 0 (surface) | 462 | 0.87 | 5.20 % | 6.39 % | 0.33 % | Top | 8.7 |

"Effective efficiency" = array output / 2600 W/m² top-of-atmosphere; power = effective eff ×
2600 W/m² (p.10). Surface: 8.7 W/m² (0 km), 22 W/m² (5 km) (conclusions).

## Caveats
- **Temperatures in Table 1 are hotter than standard Venus models at cloud level** (e.g. 69 °C
  at 55 km, 107 °C at 50 km); JPL quotes ~+60…−20 °C for 52–62 km (D_jpl_aerobot_materials.md).
  The sibling note A_seiff1985_vira.md (written by another agent; I did not re-read VIRA
  itself) lists VIRA 350.5 K (77 °C) at 50 km and 302.3 K (29 °C) at 55 km, i.e. Landis's
  model is ~30–40 K hotter. If the real cell is that much cooler, power at 50–55 km would be
  somewhat higher than tabulated (triple-junction Voc falls with temperature).
- Overhead sun, single Venera-11 cloud profile; array horizontal; no albedo/upwelling light
  from the cloud deck (relevant for bifacial or tilted rotor-blade-mounted cells).
- No cover-glass/acid-coating losses (JPL coating test showed 5 % loss — D_jpl_solar_acid_2022.md).
- Temperature coefficients per cell type are shown only in a figure (Fig. 6), not transcribed.
