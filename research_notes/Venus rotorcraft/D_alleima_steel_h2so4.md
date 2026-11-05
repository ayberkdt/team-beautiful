# D_alleima_steel_h2so4 — Stainless steels / Ti in sulfuric acid (iso-corrosion ratings)

## Citation
Alleima (formerly Sandvik Materials Technology). *Corrosion tables — Sulphuric acid.*
Web page, accessed 2026-11-04.
https://www.alleima.com/en/technical-center/corrosion-tables/sulphuric-acid/
**Manufacturer data.**

## What I read
Downloaded raw HTML, converted tables to text, read rows for 60–98 % H2SO4.
Local copy: `D:\tmp_ideathon\venus\downloads\eng\alleima_h2so4.html`.
(A WebFetch summary of the same page mis-aligned columns; the values below are from the raw table.)

## Legend [D-ag]
0 = < 0.1 mm/y (corrosion proof); 1 = 0.1–1.0 mm/y; 2 = > 1.0 mm/y (not usable).
Lab tests, pure chemicals, air-saturated solutions, annealed material.

## Ratings at high concentration [D-ag]
| Grade | 90%/20°C | 90%/40 | 94%/20 | 94%/40 | 94%/50 | 96%/20 | 96%/40 | 96%/50 | 98%/30 | 98%/50 | 98%/80 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Carbon steel | 0 | 2 | 0 | 2 | 2 | 0 | 2 | 2 | 1 | 2 | 2 |
| 3R12 (304L-type) | 0 | 2 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 2 | 2 |
| 3R60 (316L-type) | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 2 |
| 317L-type (18Cr13Ni3Mo) | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 2 |
| 2RK65 (904L) | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 2 |
| Sanicro 28 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| SAF 2507 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 |
| **Titanium (CP)** | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |

At 85 %: 3R60 rated 1 at 20–40 °C, 2 at 50 °C; 60–80 % range is "2" for 304L/316L types [D-ag].
(Mapping 3R12 ≈ 304L and 3R60 ≈ 316L is my knowledge of Alleima grade names, not stated on
this page.)

## Interpretation (mine)
316L-type stainless is "corrosion proof" (< 0.1 mm/y) in 90–98 % acid at ≤ 30 °C but degrades
to 0.1–1 mm/y at 40–50 °C and > 1 mm/y at 80 °C, and is bad at 60–85 % (dilution by
condensed water would be the worst case). Cloud-level temperature over 52–62 km is quoted as
roughly +60…−20 °C (Izraelevitz et al. 2025, see D_jpl_aerobot_materials.md; 50 km is warmer —
not verified here), so bare stainless is marginal; coat or use fluoropolymer.

## Caveats
Immersion of bulk metal; not aerosol; no stress/fatigue interaction.
