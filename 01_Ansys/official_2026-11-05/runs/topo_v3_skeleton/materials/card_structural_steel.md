# Material card — Structural Steel (Ansys Engineering Data default)

Route assumed: **machined from plate / welded** · 3-D printable: **no** · working temperature **300 °C**.

Tags: D = read from the primary source (values whose source starts with "pool" carry the tag recorded in `materials_pool.json`, built 2026-11-01…03 and not re-read on 2026-11-04), D-ag = read from the primary source by a research sub-agent on 2026-11-04 (URL in the source), S = secondary, Y = assumption or proxy.

| Property | 20 °C | 300 °C | Source | Tag |
|---|---|---|---|---|
| Density | 7850 kg/m³ |  | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Young's modulus E | 200 GPa | 182.7 | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Poisson's ratio | 0.3  |  | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Tensile yield Fty (0.2 %) | 250 MPa | 162.8 | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Tensile ultimate Ftu | 460 MPa | 414.2 | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Max service temperature | 400 °C |  | EN 1993-1-2 Table 3.1: k_y = 1.000 up to 400 C (fire design, 2 % strain) [D-ag] | Y |
| Fatigue (endurance / 1e6-1e7) | 86.2 MPa |  | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04): S-N at 1e6 cycles, zero mean (ASME BPV VIII-2 Table 5-110.1) | D |
| CTE | 12 µm/(m K) |  | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Thermal conductivity | 60.5 W/(m K) |  | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Specific heat | 434 J/(kg K) |  | Ansys Engineering Data 23.1.0.209 export 'Structural Steel', github.com/ansys/pymaterials-manager tests/data/steel_eglass_air.xml (local copy read 2026-11-04) | D |
| Embodied CO₂ (primary) | 1.8 kg CO₂e/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction: low-carbon steel primary 1.8 kg CO2/kg (Ashby pp. 463-469) [D-ag] | D-ag |
| Embodied energy (primary) | 26.5 MJ/kg |  | Ashby 2013 via 'Useful numbers for environmental studies' reproduction: low-carbon steel primary 25-28 MJ/kg, midpoint | D-ag |
| Embodied CO₂ (recycled) | NOT FOUND | | | |
| Price (stock / powder) | 0.77 EUR/kg |  | SMM news 2026-08-03: NW European S235 plate 888 USD/t = 770 EUR/t EXW (news.metal.com 104039523, opened by sub-agent) [D-ag]; S235 as the proxy grade | D-ag |

Temperature factors E, Fty, Ftu at 300 °C: 0.913, 0.651, 0.900 — Fty: EN 10028-2 minimum Rp0.2 of P235GH (t <= 16 mm) 153 MPa at 300 C vs 235 MPa at RT, ratio 0.651 (Salzgitter reproduction, read by sub-agent 2026-11-04) [D-ag]; E and Ftu: MIL-HDBK-5J Fig. 2.3.1.1.4 / 2.3.1.1.1 AISI low-alloy steels at 572 F (proxy) [D curve, Y use] [D-ag/Y].

Notes:
- EN 1993-1-2 Table 3.1 at 300 C: k_y 1.000, k_p 0.613, k_E 0.800 (fire design; sensitivity) [D-ag]
- MIL-HDBK-5J low-alloy Fty factor at 572 F would be 0.800 (heat-treated alloy steels; not used: less conservative than EN 10028-2 for a structural carbon steel)
- E(300 C) cross-check: ASME B31.1 carbon steel 29.5 -> 26.7 Msi (ratio 0.905) via Engineering ToolBox, column reading ambiguous [D-ag]
- Not normally made by powder-bed AM: baseline route is machining from plate [Y]

Ansys import: Engineering Data → File → Import Engineering Data → `materials_engineering_data.xml` (not tested on this laptop; the XML is checked by parsing it back).
