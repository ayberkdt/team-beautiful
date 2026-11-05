# D_dutta_2012_venus_entry — Past Venus entries (β, γ, V, g, q) and low-β entry trades

## Citation
Dutta, S., Smith, B., Prabhu, D., & Venkatapathy, E. (2012). *Mission Sizing and Trade
Studies for Low Ballistic Coefficient Entry Systems to Venus.* 2012 IEEE Aerospace
Conference, Big Sky, MT. IEEE 978-1-4577-0557-1/12. NTRS 20120006657.
PDF: https://ntrs.nasa.gov/api/citations/20120006657/downloads/20120006657.pdf

## What I read
Full text extract (14 pp.); Table 1 and Fig. 1 read from rendered image of p.2.
Local copy: `D:\tmp_ideathon\venus\downloads\eng\ntrs20120006657.pdf`.

## Table 1, p.2 — "Past successful Venus entry missions" [D-ag]
(V for a 200 km interface; n_max and q_max simulated from engineering estimates; q_max =
cold-wall convective + radiative, per table footnotes)

| Mission | β kg/m² | γ deg | V km/s | Shape | D m | n_max g | q_max kW/cm² |
|---|---|---|---|---|---|---|---|
| Venera 4 (1967) | 519 | −78 | 10.7 | sphere | 1.0 | 450 | 9.66 |
| Venera 8 (1972) | 670 | −77 | 11.6 | circumellipsoid | 1.0 | 500 | 30.0 |
| Venera 9/10 (1975) | 367 | −20.5/−23 | 10.7 | sphere | 2.4 | 150/170 | 3.04/3.37 |
| PV North (1978) | 190 | −68.7 | 11.5 | 45° sphere-cone | 0.7653 | 487 | 10.6 |
| PV Night | 190 | −41.5 | 11.5 | 45° sph-cone | 0.7653 | 350 | 7.8 |
| PV Day | 190 | −25.4 | 11.5 | 45° sph-cone | 0.7653 | 219 | 5.2 |
| **PV Large** | 188 | −32.4 | 11.5 | 45° sph-cone | 1.4228 | 276 | **6.9** |
| Venera 11–14 | 376–387 | −18 to −21 | 11.2 | sphere | 2.4 | 138–167 | 4.35 |
| **Vega 1 / Vega 2 (1984)** | 412 | −18.23/−19.08 | 10.7/10.8 | sphere | 2.4 | 130/139 | **3.06/3.29** |

## Other numbers [D-ag]
- Fig. 1 (p.2): V = 11.5 km/s, nose radius 2.5 m; contours of β (5–55 kg/m²) vs γ
  (−14 to −8°). Reading from the figure: β ≈ 30 kg/m², γ ≈ −10° gives peak q ≈ 250–350
  W/cm² and ~50–60 g; β ≈ 10, γ ≈ −9° gives ~100–150 W/cm² [D-ag, read off contour plot,
  ±1 contour].
- Text p.1: shallow-γ, low-β deployables reach ~50–60 g and peak heat flux ~400 W/cm².
- Text p.2: past missions all had β > 100 kg/m², peak deceleration > 100 g, peak total
  heat flux of order 1000 W/cm².
- ADEPT analysis: cold-wall convective flux ≤ 200 W/cm², impact pressure ≤ 0.14 atm
  (ADEPT geometries, Figs. 14–15). For a 2000 kg, 8 m, 70° sphere-cone, radiative was
  "roughly 40% to 55% larger" than convective (as extracted; text partly garbled) [D-ag,
  verify on page image before quoting].

## Caveats
- Table q_max values are the authors' engineering re-simulations, not flight measurements.
- Units in table header are kW/cm² (Venera 8: 30 kW/cm² is an outlier from β 670, γ −77°).
- These are rigid steep-entry heritage cases; a rotorcraft delivery capsule would be
  designed in the β 30–300, γ −8…−25° regime (see D_venkatapathy_2017_venus_edd.md).
