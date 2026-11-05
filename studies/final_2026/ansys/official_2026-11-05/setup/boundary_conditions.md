# Official bracket — loads and boundary conditions (5 Nov 2026)

Sources read in this session: `files/Ideathon_Challenge_Ansys_2026.docx` (challenge card), `files/Eurovia Challenge 2026
CAD file.dsco` (Discovery 2024 R2 file: geometry, material card, saved solver logs), `files/Eurovia challenge 2026
introduction - Ansys.pptx` (slides 18–24), `files/Reference steel bracket eco assessment.prd`. Tags: **[D-org]**
organisers' file, **[K]** computed here (command given), **[Y]** our interpretation.

## 1. Geometry (measured from the Discovery tessellation)

Command: `python -I <scratch>/parse_facets.py` and `features.py` → `derived/initial_from_facets.stl` (mm),
`derived/features.json`. Volume 0.019400 m³ → **152.29 kg** at 7850 kg/m³ [K]; the file's own mass monitor says
152.27 kg and the eco-audit file 152 kg [D-org] → the reconstruction is right to 0.02 %.

| Feature | Value [K] |
|---|---|
| Base plate | x 170–831.01, y 30–371.12, z 30–100 mm → 661.01 × 341.12 × 70 mm, corner radius R100 |
| 4 bolt holes (axis z, through the plate) | Ø60 (fit 59.96, tessellation chord) at (x, y) = (245, 95), (245, 305), (755, 95), (755, 305); pattern 510 × 210 mm |
| 2 lugs | y 30–100 (70 mm) and y 300–371.12 (**71.12 mm** — not symmetric by 1.12 mm), from the plate top z = 100 to z = 321.37 |
| Lug profile (x–z) | top arc R80 centred (500, 241.37); flanks inclined 80° (normal (±0.985, 0, 0.171)); root fillets R80 centred (326.95, 180) and (673, 180) |
| Pin holes (axis y) | Ø60 at (x, z) = (500, 260) — **18.6 mm above the arc centre**, so the ligament above the pin is 31.4 mm and 47.8 mm at the sides |
| Largest dimension | 661.01 mm (x) → displacement limit 661.01/400 = **1.653 mm** |
| Frame | Discovery world axes, z up (triad in slide 18 image) |

## 2. Supports

Card: "Locations and in between distances of fixed support, or where the load is applied, should stay the same."
The card does not say which face is fixed.

| Option | Definition | Use |
|---|---|---|
| **S1 (primary)** | Fixed Support on the 4 bolt-bore cylindrical faces (all DOF) | baseline + topology; matches "locations of fixed support" = bolt holes [Y] |
| S2 (sensitivity) | bolt seat: fixed annulus r … 1.8 r on the plate underside around each bore | shows how much the peak at the bore edge depends on S1 (doc 22 §6b: fixed bores act as rigid clamps) |
| S3 (evidence) | whole underside face (z = 30) fixed | the organisers' saved Discovery runs 1–2 fixed an area of 207 400 mm² (Dirichlet count × voxel², two voxel sizes agree to 0.2 %) vs our underside face 205 599 mm² (+0.9 %); bores are only 52 722 mm² [K]. Runs 3–4 were on another geometry (max length 0.83 vs 0.85 m) and do not match. So the reference model **probably** fixed the underside, not the bolts — not certain, ask the mentor (§6) |

S3 cannot be run in our code today (support types: `fixed_bore`, `bolt_seat`); in Ansys it is one click. S3 makes
the plate almost rigid, so its stresses will be much lower than S1 — a design passing S1 is conservative.

## 3. Loads

Card [D-org]: "Loading condition 1 static vertical on each hole (0; +/-24kN ; 97kN)"; "Loading condition 2 static
torsional 2000N.m (My)"; "Factor of Safety of 1.5". The saved Discovery solve has "BC Force 2" = one force per pin
hole [D-org], so "each hole" = each of the 2 pin holes [Y]. The saved results (peak 0.142 MPa, slide 18 image) are
not at these loads.

| Case | Per pin hole H1 (y 30–100) | Per pin hole H2 (y 300–371) | Resultant on the part |
|---|---|---|---|
| LC1a | F = (0, +24, +97) kN | (0, +24, +97) kN | Fz 194 kN, Fy +48 kN |
| LC1b | (0, −24, +97) kN | (0, −24, +97) kN | Fz 194 kN, Fy −48 kN |
| LC1c (sensitivity) | (0, +24, +97) kN | (0, −24, +97) kN | Fz 194 kN, lugs pulled apart |
| LC2 | My = 1000 N·m | My = 1000 N·m | My 2000 N·m about the pin axis |

Interpretation notes [Y]: (1) the triple is (Fx; Fy; Fz) in the CAD frame; "vertical" = z. (2) linear analysis, so the
sign of Fz only flips the stress sign; LC1a/LC1b differ only through the sign of Fy relative to Fz and are near mirror
images (lugs symmetric except the 1.12 mm). (3) 97 kN is **per hole** (194 kN total) — the literal reading; if the
mentor says total, all stresses halve. (4) LC1 and LC2 are separate cases (card numbers them), not combined.
(5) My is about the pin axis; a free pin cannot carry it, so it implies a clamped/keyed pin — split 50/50 on the two
bores (a single moment on both faces in Ansys behaves the same).

How each load is distributed:
* Fz (radial): **bearing** — cosine-weighted pressure on the upper half of the bore (the pin pulls the lug up) —
  Ansys Mechanical *Bearing Load*; our `type: "bearing"`.
* Fy (along the pin): uniform traction on the bore face (Ansys *Force* on the face); physically it enters through the
  pin head/washer on the lug side face — check that variant in Mechanical if Fy-driven stress governs.
* My: rigid distribution about the bore centroid (Ansys *Moment*, rigid behaviour; our `type: "moment"`).
* Ansys Discovery: one *Force* per bore face with (0, ±24 000, 97 000) N and one *Moment* 2000 N·m about y on both bore
  faces; *Fixed* on the 4 bolt bores. Discovery distributes forces uniformly (not bearing) → slightly lower bore-edge
  peaks than Mechanical.

## 4. Pass criteria

* Strength: σ_vM,max × 1.5 ≤ Fty(T ≥ 300 °C) of the material (FoS 1.5 on yield at working temperature) [Y on yield vs
  ultimate; card gives only "FoS 1.5"]. Peaks at the fixed bore edges in S1 are support singularities: report them and
  judge on the value outside a 1-element ring, as in doc 22.
* Stiffness: max |u| < 1.653 mm, using E at 300 °C.
* Material screen (card): T_work > 300 °C, castable or 3-D printable, K1c ≥ 10 MPa·m^½.

## 5. Hand checks (`python -I setup/hand_checks.py` → `setup/hand_checks.json`) [K]

| Quantity | Value |
|---|---|
| Pin bearing stress 97 kN / (60 × 70) | 23.1 MPa |
| Lug net-section tension at the pin | 14.5 MPa |
| Lug root out-of-plane bending from Fy (24 kN × 160 mm, b 188 × t 70) | 25.0 MPa (+ 7.4 MPa axial) |
| Plate bending between bolt rows (194 kN, span 510 mm), fixed–fixed / pinned bounds | 44 / 89 MPa (lugs stiffen the plate; FEA will be lower) |
| Bolt tension / shear in LC1 (4 equal bolts) | 48.5 kN / 12.0 kN each |
| Bolt axial from LC2 | ±1.96 kN |

So the steel part (S275N Fty 237.4 MPa at 23 °C [D-org]) is lightly stressed: allowable 237.4/1.5 = 158 MPa before any
temperature knock-down. There is a large mass margin, and with aluminium the stiffness limit may govern before strength.

## 6. Open questions for the mentor

1. Fixed support = 4 bolt bores, or the underside face (the saved Discovery runs suggest the underside)?
2. 97 kN and 24 kN per pin hole, or total? Are LC1 ±24 kN one case per sign (our LC1a/LC1b), or opposite on the two lugs?
3. FoS 1.5 on yield or on ultimate, and at 300 °C?
4. "Largest dimension" = 661 mm (bounding box) → 1.65 mm limit?
5. The pptx lists a material-selection report, comparison table and Discovery material cards as provided files; the
   zip contains only the `.ces` project (names, no property values) and the `.prd` eco audit set-up.
6. Eco formulas: transport `mass(kg) × 500 × 0.241` gives 18 316 kg CO₂ for 152 kg if read literally (kg·km), while the
   use phase `mass × km × 0.000468` is per kg·km (= 0.468 per t·km). The transport factor looks like a per-tonne value.
