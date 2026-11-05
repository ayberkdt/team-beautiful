# D_timet_titanium_h2so4 — Titanium corrosion in sulfuric acid (manufacturer data)

## Citation
Titanium Metals Corporation (TIMET). *Corrosion Resistance of Titanium.* Technical manual
(undated brochure, 44 pp.). https://www.timet.com/assets/local/documents/technicalmanuals/corrosion.pdf
**Manufacturer data.**

## What I read
Text extraction; "Sulfuric Acid" section (brochure p.15 / PDF p.19) and the
"Titanium Corrosion Rate Data – Timetal Commercially Pure Grades" table (PDF p.41ff,
R = corrosion rate, mpy (mm/y)).

## Numbers — CP titanium [D-ag, manufacturer]
Text (p.15): unalloyed Ti resistant only to ~20 % H2SO4 at 0 °C and ~5 % at room temperature;
TIMETAL 50A .15Pd to ~45 % at RT; boiling acid attacks unalloyed Ti from 0.5 %; Ti-6Al-4V
"somewhat less resistance than unalloyed titanium". Oxidizers (Fe³⁺, Cu²⁺, HNO3, CrO3, Cl2)
inhibit attack.

Table (aerated with air unless noted; mpy → mm/y as printed):
| H2SO4 wt% | Temp | Rate |
|---|---|---|
| 40 | 35 °C | 340 mpy (8.64 mm/y) |
| 75 | 35 °C | 42 (1.07 mm/y) |
| 75 | room | 427 (10.8 mm/y) |
| 80 | room | 316 (8.03 mm/y) |
| **Concentrated** | room | **62 mpy (1.57 mm/y)** |
| Concentrated | boiling | 212 (5.38 mm/y) |
| **96 % vapours** | 38 °C and 66 °C | **Nil** |
| 96 % vapours | 93–149 °C | 0.4–0.5 mpy (0.010–0.013 mm/y) |

## Interpretation for the design (mine)
Bare titanium (incl. Ti-6Al-4V) is NOT acceptable for wetted contact with liquid 75–98 %
H2SO4 (mm/y-scale rates); it fares well in acid vapour. Ti parts on a Venus rotorcraft must be
coated (FEP/PFA/Parylene) or kept out of droplet impingement. Consistent with Alleima table
(CP Ti rated "2 = not usable" at 90–98 %, see D_alleima_steel_h2so4.md).

## Caveats
Laboratory immersion in pure acid; Venus droplets are micron-scale aerosol with possible
impurities; "concentrated" not defined numerically in the table row.
