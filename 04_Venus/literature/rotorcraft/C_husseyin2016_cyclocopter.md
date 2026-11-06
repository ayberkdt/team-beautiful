# C_husseyin2016_cyclocopter — Design Considerations for a Stopped-Rotor Cyclocopter for Venus Exploration

## Citation
Husseyin, S. (NASA/ISU intern, NASA Ames). *Design Considerations for a Stopped-Rotor Cyclocopter for Venus Exploration.* NASA Ames internship report. NTRS 20160012563 (the year 2016 is inferred from the NTRS ID and not verified on the document).
PDF: https://ntrs.nasa.gov/api/citations/20160012563/downloads/20160012563.pdf
Cited as Ref. 8 in C_young2026_venus_aerial.

## What was read
pypdf text of 27 pages: abstract, introduction, mission description (Sec. II-D), Table 1 (flow properties). The CFD results and conclusions were only skimmed.

Tag: [D-ag] read in this report.

## Content [D-ag]
- Concept: a stopped-rotor **cyclocopter**. Cycloidal rotors provide lift and thrust in VTOL, and the vehicle flies as a fixed wing when the rotors are stopped. It is claimed to be capable of flying at all altitudes of Venus and of landing. Studied with RotCFD (momentum-source rotor model) at three yaw-angle configurations, plus a hovering cyclorotor case.
- Mission sequence (Sec. II-D): entry at 200 km → vehicle ejected → drop/glide to the altitude for upper-atmosphere flight → descend to 25 km taking measurements → radar descent → cyclorotors switched on for powered flight and site scouting → VTOL landing and take-off.
- Text values: surface 740 K, 93 bar; upper-atmosphere winds up to 100 m/s, near-surface 2.8 m/s; "Earth-like" pressure/temperature region at 50-75 km; temperature from 350 K (45 km) to 200 K (70 km). History: Vega balloons floated at ~53-55 km.
- **Table 1 (RotCFD inputs):** at "60 km": wind 100 m/s, **ρ 1.225 kg/m³**, T 263.15 K, R 192.5 J/kg K, γ 1.4, μ 1.6658e-5 Pa s, p 62.057 kPa. At 5 km: ρ 67 kg/m³, T 735.15 K, γ 1.368, μ 3.4368e-5, p 9486.7 kPa.

## Caveats
- **The "60 km" density of 1.225 kg/m³ and pressure of 62 kPa look inconsistent with standard Venus profiles**, which give roughly 0.2-0.3 bar and ~0.4-0.5 kg/m³ near 60 km. This is my recollection of VIRA-type values and is not verified in this session. The internship report appears to have used Earth sea-level density as a placeholder. **Do not use Table 1 as atmosphere data.** Use the team's atmosphere source.
- This is an internship report, not peer reviewed.
