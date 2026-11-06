# Traceability — every slide claim → submitted report

Source of truth: `D:\Kullanici\Downloads\Team_Beetiful_Ansys_Report.pdf` (8 pages, created 5 Nov 2026 15:04:42).
Page numbers below are the PDF page numbers (cover = p1). Text was extracted with PyMuPDF and read in this session.

## Report version check

| File | Time | Text vs submitted PDF |
|---|---|---|
| `final_report/Team_Beetiful_Ansys_Report.docx` | 15:02 | **Same text.** Word-level diff shows only page numbers, TOC numbers and line-break hyphens. Its media are the PDF figures. |
| `final_report/Team_Beetiful_Ansys_Report_final.docx` | 15:09 | **Not submitted. Differs:** adds "(Figure 4)" in §3 and a new **Figure 4** (smoothed final geometry in Ansys, steel properties: LC1 78.5 MPa / 0.19 mm, LC2 5.2 MPa / 0.006 mm). The deck does **not** use Figure 4. |

Figures in the deck are taken from the 15:02 docx media (same pixels as the PDF):
`image6.png` = Fig. 1, `image3.jpg` = Fig. 2, `image7.png` = Fig. 3. Fig. 1 and Fig. 3a are cropped to the
geometry (legend text removed; legend meaning given in the slide source line). Fig. 2 is used whole and unchanged.

## Slide-by-slide

| Slide | Claim / number on slide or in notes | Report location |
|---|---|---|
| 1 | Team Beetiful; eco-redesign of the (engine) cowling bracket | p1 title "Eco-Redesign Cowling Bracket · Team Beetiful"; §1 p3 "engine cowling" |
| 1 | Ansys challenge · EUROAVIA Ideathon 2026 | p8 team line |
| 1 | "2026", footer date 07/11/2026 | template text, unchanged (not from report) |
| 2 | 97 % of life-cycle CO₂ from flight; 51.2 of 52.6 t CO₂-eq | §1 p3 |
| 2 | Material and manufacture 2.6 % | §1 p3 |
| 2 | 152 kg S275N steel part | §1 p3 |
| 2 | 720 000 km per kg per year; 337 kg CO₂ per kg | §1 p3 |
| 2 | Question: extra production CO₂ accepted to remove 1 kg | §1 p3 |
| 3 | Picture: original S275N part, Ansys, load case 1 | Fig. 3a p6 |
| 3 | 4 bolt holes, 2 lugs with 60 mm pin holes | §1 p3 |
| 3 | 97 kN vertical and 24 kN along the pin on each pin hole; 24 kN push the lugs together | Table 1 p3 (load case 1) |
| 3 | Torsion 2 000 N·m, half on each pin hole | Table 1 p3 (load case 2) |
| 3 | Safety factor 1.5 on yield | Table 1 p3 |
| 3 | Max. displacement 1.65 mm (661/400) | Table 1 p3 |
| 3 | Working temperature above 300 °C | Table 1 p3 |
| 3 | Fracture toughness ≥ 10 MPa·m½; castable or 3D-printable | Table 1 p3 |
| 3 | Bolt and pin hole positions fixed | Table 1 p3; §1 p3 |
| 4 | 3 904 materials → 196 pass the Granta screen → 3 shortlisted by the organisers | §2 p3 |
| 4 | 2 analysed: steel and titanium | §2 p4 "Steel and titanium both went on to the optimisation" (count of 2 is read from this sentence) |
| 4 | S275N: 471–501 °C, allowable 107 MPa, reference | Table 2 p4 |
| 4 | Al 2618-T6: 250–300 °C, no margin; stress-corrosion high; sourcing very high; eliminated | Table 2 p4; §2 p4 |
| 4 | Ti-8Al-1Mo-1V: 407–455 °C, allowable 345 MPa, selected | Table 2 p4 |
| 4 | Producing 1 kg Ti emits 11.6× the CO₂ of 1 kg steel | §2 p4 |
| 4 | Same shape: paid back in 71 000 km = 18 of 180 flight days | §2 p4 |
| 5 | Load case 1 drives the optimisation: 69.5 MPa against 5.2 MPa torsion (steel part) | §2 p4; Table 3 p6 |
| 5 | Run 1: whole part free, plate removed, two arms, bolts no longer act as one group | §2 p4; Fig. 1a p5 |
| 5 | Run 2: base plate and bolt bosses kept | §2 p4; Fig. 1b p5 |
| 5 | Final: smoothed geometry, 45 % of the original volume | §2 p4 (smoothed, Fig. 1c); §2 p5 (45 % volume) |
| 5 | grey = keep, beige = marginal | Fig. 1 caption p5 |
| 6 | Figure: life-cycle CO₂ vs volume; mass / CO₂ / cost ratios | Fig. 2 p5 (unchanged) |
| 6 | 45 % volume → 25 % mass, 27 % life-cycle CO₂, 4.9× raw-material cost | §2 p5 |
| 6 (notes) | CO₂ grows 1.6× faster for steel; steel would need 27 % volume to match | §2 p5 |
| 7 | Stress LC1 78.5 MPa (Ansys, smoothed final geometry); allowable 345 MPa | §3 p5 |
| 7 | Own FE LC1 142 MPa, LC2 35 MPa, displacement 0.87 mm | Table 3 p6 |
| 7 | Displacement 0.36–0.38 mm at 300 °C; limit 1.65 mm | §3 p5 |
| 7 | Stress LC2 5.2 MPa (Ansys) | §3 p5 |
| 7 | Checked three ways: hand calculation, own FE code, Ansys | §3 p5; §5 p7 |
| 7 | Not modelled: fatigue at 300 °C; porosity and rough surface of printed Ti; thermal stress from constrained mounts; Ti-8Al-1Mo-1V powder supply must be confirmed | §3 p6 |
| 8 | −72 %: 14.6 t instead of 52.6 t in the one-year scenario | §4 p7 |
| 8 | 114 kg lighter; 38 t less CO₂ per aircraft in the first year | §4 p7 |
| 8 | Extra 0.25 t production CO₂ paid back after about 4 200 km, roughly one flight day | §4 p6–7 |
| 8 | ≈ 52 000 USD per bracket (laser powder-bed printing estimate) | §4 p7; refs [2], [6] |
| 8 | ≈ 1 360 USD per t CO₂ avoided in year one, falling with years in service | §4 p7 |
| 9 | Choose material and shape in one loop; a material poor per kg can win against 720 000 km of flight | §5 p7 |
| 9 | −72 % CO₂, 25 % of the mass, 114 kg lighter | §4 p7; §2 p5 |
| 9 | Next step: print prototype → close porosity (HIP) → fatigue test at 300 °C → agree qualification route | §4 p7 |
| Q&A | Galvanic −0.78 to −0.70 V vs −0.51 to −0.43 V; oxidation | §2 p4; Table 2 p4 |
| Q&A | Raw material 950 USD vs 196 USD; printing ~1 350 USD/kg (Ti-6Al-4V data) | §4 p7; ref [6] |
| Q&A | Allowable = yield at 300 °C / 1.5; stress independent of modulus (linear model) | Table 2 caption p4; §3 p5 |

Words on slides that are not report facts: "Benefit", "Drawback: cost" (report: "Cost is the drawback"),
"Next step", "Thank you. Questions?", the source lines, and the template's "2026" / date.

## Inconsistencies inside the submitted report (not fixed; the deck avoids them or follows the text)

| Item | Where | Deck choice |
|---|---|---|
| Final Ti mass 38.5 kg (Table 3) vs 38.4 kg (Table 4) | p6 | No final mass on slides; 114 kg lighter (§4) used |
| Steel life-cycle CO₂ 52.6 t (text) vs "Initial S275N part 52.7 t" label in Fig. 2a | p3, p5 | Slides use 52.6 t; Fig. 2 shown unchanged |
| Ti final design 14.5 t (§2 p5, Fig. 2a) vs 14.6 t (§4 p7) vs 14 570 kg (Table 4) | p5–7 | Slide 8 uses 14.6 t (§4) |
| Yellow highlight marks still visible in Table 3 (142, 35, 0.87, 38.5, "–") | p6 | No effect on deck |
