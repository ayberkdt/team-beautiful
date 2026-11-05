# B_venkatapathy2016_prabhu2013 — two NASA Ames Venus-entry presentations

## Citations
1. Venkatapathy, E., & Smith, B. (2016). *Entry at Venus*. Short course presentation, 13th International Planetary Probe Workshop (IPPW-13), Laurel MD, 13–17 June 2016. NTRS 20160012771. https://ntrs.nasa.gov/citations/20160012771 (PDF 45 slides, downloaded 2026-11-04).
2. Prabhu, D. K., Allen, G. A., Hwang, H. H., Cappuccio, G., Spilker, T. R., & Moses, R. W. (2013). *Ballistic Entries at Venus*. 10th IPPW, San Jose CA, 17–21 June 2013. NTRS 20140005557. https://ntrs.nasa.gov/citations/20140005557 (PDF 34 slides).

## What I read
Full text of both decks (pypdf text layer). Key tables: Venkatapathy & Smith slide 4 ("Historical Perspective: Venera 4-9 and P-V Entry Systems"), slide 11 (Pioneer Venus altitude vs deceleration + table), slides 29–31 (VITaL), slide ~32 (ADEPT vs rigid comparison); Prabhu et al. slides 6–8.

These are NASA engineering presentations (authoritative secondary; they compile mission data, not the original flight reports). Values read in the slides are tagged [D-ag] = read in this source; the slides themselves do not cite primary references for each cell.

## Numbers

### Venkatapathy & Smith 2016, slide 4 — historical entry systems [D-ag]
| Mission | Forebody shape | Ballistic coeff. (kg/m²) | Dia. (m) | Entry angle (°) |
|---|---|---|---|---|
| Venera 3–6 | Sphere | ~450 | 1 | (−62, −78) |
| Venera 7 and 8 | "Circum-ellipsoid" | ~422–500 | 1 | ~(−60, −77) |
| Venera 9 – Vega 2 | Sphere | ~139–170 | 2.4 | (−18, −23) |
| PV small probes | 45° sphere-cone | 190 | 0.77 | −68.7, −41.5, −25.4 |
| PV large probe | 45° sphere-cone | 188 | 1.42 | −32.4 |

### Slide 11 — Pioneer Venus probes [D-ag]
| Probe | EFPA (°) | BC (kg/m²) | Max g |
|---|---|---|---|
| North | −68.7 | 190 | 487 |
| Night | −41.5 | 190 | 350 |
| Large | −32.4 | 188 | 276 |
| Day | −25.4 | 190 | 219 |
(EFPA defined as angle between velocity vector and local horizon at entry interface.)
Note: SP-461 text gives 458 g (steepest) and ~223 g (shallowest) and 280 g (Large) — differences of a few % between sources (see B_fimmel1983_sp461).

### Other slide facts [D-ag]
- Venus escape speed 10.3 km/s; hyperbolic entry speeds at Venus range 10.5–12.5 km/s (slide 7).
- All Venus entries to date were ballistic (zero-lift) (slide 6).
- TPS mass fractions (chart, slide ~29): **Pioneer Venus 13%**, Galileo 50%, Apollo 13.7%, Viking 2.8%, MPF 8.2%, MER 12%, Stardust 22%, Genesis 18%.
- VITaL decadal lander concept: 45° sphere-cone same shape as PV large probe; 1,051 kg lander + 1,051 kg aeroshell = **2,102 kg entry mass**; design g-limit 200 g; result EFPA −23.35° at 11.3 km/s (slides 29–31). Carbon phenolic is a poor insulator, so design pushes steep entry → high heat rate, low heat load, high g.
- Comparison (slide ~32): rigid 45° sphere-cone, 3.5 m, β 208 kg/m², EFPA −8.5° → **48 g**, 1242 W/cm², 2.5 atm; same at steeper? (second column 23 g, 818 W/cm², 1.2 atm — column-to-label mapping garbled by text extraction); **ADEPT 70° deployable, 6 m, β 44 kg/m², EFPA −8.5° → 32 g, 203 W/cm², 0.34 atm**. Units printed "kg/m3" for β (typo; should be kg/m²).

### Prabhu et al. 2013, slide 6 [D-ag]
- PV Large Probe: entry mass **316.5 kg**, entry velocity **11.54 km/s**, EFPA **−32.4°**, 45° sphere-cone, diameter **1.42 m**, entry BC **190 kg/m²**, heat shield **FDCP** (fully dense carbon phenolic).
- β table assumes C_D = 1.05 for a 45° sphere-cone (e.g. 2000 kg on 3.5 m → 198 kg/m²).
- Trajectory studies terminate at Mach 0.8 = parachute deploy; entry interface 200 km; constraint sets 100 g / 200 g ("200 g limit assumes centrifuges are available") and 5 / 10 bar stagnation pressure ("10 bar limit is from Pioneer Venus Large & Day Probes").

## Caveats
- PV large-probe diameter: 1.42 m here vs "about 1.5 m" in SP-461 — 1.42 m is probably the aeroshell base diameter used for β; SP-461 rounds.
- The Venera rows are ranges, compiled; they are useful for order-of-magnitude only.

## Quote
"All of the Venus entry missions to-date have been ballistic entry" (Venkatapathy & Smith, slide 6).
