# C_langelaan2017_titan — Energetics of Rotary-Wing Exploration of Titan

## Citation
Langelaan, Jack W.; Schmitz, Sven; Palacios, Jose; Lorenz, Ralph D. (2017). *Energetics of Rotary-Wing Exploration of Titan.* 2017 IEEE Aerospace Conference, Big Sky, MT (venue per search result listing). DOI: not checked.
PDF: https://www.aero.psu.edu/avia/pubs/LanSch17.pdf
(The task brief called this "Energetics of rotorcraft flight at Titan". The actual title is above.)

## What was read
Full text, 11 pages (pypdf): abstract, Sec. 2 (aeroshell packaging), Table 1, Table 2, the power model (Eqs. 21-25), the TREx results, and the motor/ceiling paragraph.

Tag: [D-ag] read in this paper. [derived] mine.

## Numbers [D-ag]
**Table 1 — Titan vs Earth surface:** g 1.35 vs 9.81 m/s²; ρ **5.428** vs 1.225 kg/m³ (×4.43); ν 1.23e-6 vs 1.46e-5 m²/s (×0.084); a 195 vs 340 m/s.

**Aeroshell packaging (Sec. 2, Eq. 5):** net disc area fraction f = N sin²(π/N) / (1 + sin²(π/N)) for N rotors packed in a circular aeroshell. Relative to a single rotor of aeroshell size: 4 rotors give **+33 %** net disc area (maximum), 6 rotors +20 % (open centre = one rotor disc), 8 rotors +2 %, and more than 8 gives less. Above 8, use coaxial rotors. For a 3 m aeroshell: single 3 m rotor ideal hover 221 W (115 kg vehicle); quad max net disc area 9.4 m², 191 W; a 500 kg quad needs 1736 W ideal. Actual hover power is 25-30 % above ideal.

**Table 2 — vehicle parameters:**
| | Bumblebee | TREx |
|---|---|---|
| rotors | 2 (1 coax) | **8 (4 coax)** |
| blades/rotor | 2 | 2 |
| R | 0.1 m | **0.65 m** |
| mean chord | 0.02 m | 0.10 m |
| c̄l (hover) | 0.4 | 0.4 |
| CT | 0.0170 | 0.0131 |
| empty mass | 0.75 kg | 320 kg |
| CD body / frontal area | 0.5 / 0.0121 m² | 0.5 / 0.5 m² |
| drivetrain η | 0.81 | 0.81 |
| battery | 0.25 kg at 100 Wh/kg, 11.1 V, 10 A | 30 kg at 100 Wh/kg, 50 V, 100 A |
| hotel power in flight | 20 W | 100 W |

**Results:**
- Tip speed in hover 21.6 m/s (Bumblebee) and **35.5 m/s (TREx)**. Tip Mach 0.11 and **0.18**, so the flow is incompressible: low g and high ρ outweigh the low speed of sound.
- Re for a hover-optimized blade (constant along span) ≈ 2.3×10⁵ (Bumblebee) and **2.0×10⁶ (TREx)**. Sections sit where wind-turbine, human-powered-aircraft and ultralight airfoils operate.
- TREx (350 kg): **hover aero power 1.87 kW**, FM = 0.72 (Eq. 32), cruise 1.32 kW at 9.5 m/s (max range). Max endurance at 6.5 m/s (2.06 h). Max range ~60 km. Body drag dominates above 9 m/s. Advance ratio exceeds 0.3 at 10.7 m/s and 0.4 at 14.5 m/s. Motor ~**550 rpm** (needs ~15 rpm/V at 50 V). Shaft power available 4050 W, giving max level speed ~17 m/s, **hover ceiling 32 km**, absolute ceiling 45 km.
- Bumblebee (1 kg): hover 3.63 W aero (ideal 2.7 W for 0.2 m rotor), cruise 3.17 W at 4 m/s. Avionics and heaters (~20 W) dominate energy.

**Power model (Eq. 21-25):** P = P_parasite + κ_ind·P_induced + P_profile + P_climb, with **κ_ind = 1.15 (McCormick)** and P_profile = ρA v_T³ σ c̄d/8 · (1 + 3μ²). Glauert momentum gives the induced velocity. Lift coefficient c̄l = 0.4 is recommended for preliminary design. The paper uses no separate coaxial interference factor; I found no "1.16"/k_int in the text.

## Venus relevance (my inference)
- The same sizing pipeline (aeroshell packaging fraction, then BEMT/momentum hover and forward power) transfers directly. Venus at 55 km (ρ ~1, g 8.87, a ~ 250-280 m/s in CO2, estimated by me) puts tip Mach back into the design (like Earth), unlike Titan.
- The aeroshell disc-area-fraction formula is directly reusable for packing a Venus multicopter in an entry probe.
