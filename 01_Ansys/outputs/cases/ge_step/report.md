# Bracket redesign run — ge_bracket

Input: `01_Ansys\inputs\ge_bracket.step` (surface) · voxel 2.80 mm · 10848 elements · 44046 DOFs · working temperature **300 °C** · element H8IM · total 168 s.

All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength criterion: von Mises outside the hole zones (radius + 3 voxels) ≤ Fty(T) at limit load and ≤ Ftu(T) at 1.5 × limit [Y].

## 1. Set-up

| Hole | Axis | Ø (mm) | Centre (mm) | Role |
|---|---|---|---|---|
| H1 | x | 18.96 | -75.1, -56.7, 44.7 | load |
| H2 | z | 14.48 | -147.9, -34.0, 7.0 | support |
| H3 | z | 14.48 | -147.9, 19.2, 7.0 | support |
| H4 | z | 13.77 | -0.1, -37.8, 7.0 | support |
| H5 | z | 14.48 | 0.5, -0.4, 7.0 | support |

| Load case | Loads |
|---|---|
| LC1 +x | H1 bearing F = [2490.4, 0.0, 0.0] N |
| LC2 +y | H1 bearing F = [0.0, 2490.4, 0.0] N |
| LC3 +z | H1 bearing F = [0.0, 0.0, 2490.4] N |

Non-design rings: 1305 of 10848 elements kept solid.

## 2. Initial design, structural_steel at 300 °C

Mass **1.9964 kg** (voxel volume 254313 mm³).

| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |
|---|---|---|---|---|---|
| LC1 +x | 0.2294 | 0.243 | 130.2 | 130.2 | 2490 |
| LC2 +y | 0.05423 | 0.08218 | 63.59 | 63.59 | 2490 |
| LC3 +z | 0.04775 | 0.07844 | 48.41 | 73.17 | 2490 |

Thinnest members (distance-transform ridge): minimum 4.2 mm = 1.5 voxels, 10th percentile 9.8 mm = 3.5 voxels. **Below ~5 voxels the voxel model is too soft in bending** (GE: +21 % deformation at 3.5 voxels, +1 % at 6.3): trust the T10 numbers or rerun with a smaller `--voxel`.

**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of 300 °C (reference 22 °C) with the bores fixed, constrained expansion alone gives von Mises 1214 MPa outside the hole zones (E α ΔT = 609.4 MPa, α = 1.2e-05 /K). Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the mentors (§11 Q1).

At 20 °C the worst deformation is 0.2096 mm (vs 0.2294 mm at 300 °C: ratio 1.095 = E(20)/E(T)).

### Mesh convergence (initial design)

| Voxel (mm) | Elements | Max deformation (mm) | Compliance (J) | vM outside (MPa) | Volume (mm³) |
|---|---|---|---|---|---|
| 4.20 | 3586 | 0.1508 | 0.1673 | 114 | 254698 |
| 2.80 | 10848 | 0.2294 | 0.243 | 130.2 | 233439 |
| 2.10 | 28619 | 0.119 | 0.1599 | 96.72 | 250767 |

### Conforming check: 10-node tetrahedra on the exact geometry (Ansys SOLID187 analogue)

gmsh/OCC mesh of the CAD, same set-up, consistent bore loads, PARDISO. Compare THESE numbers with an Ansys run; the voxel-vs-T10 gap is a measured discretisation effect.

| Mesh size (mm) | T10 elements | Volume (mm³) | Max deformation (mm) | vM outside (MPa) | vM max (MPa) | Time (s) |
|---|---|---|---|---|---|---|
| 5.60 | 12981 | 254314 | 0.1572 | 4968 | 4968 | 15 |
| 3.64 | 32784 | 254313 | 0.1579 | 102.8 | 162.2 | 38 |

Voxel / T10 (finest): deformation 1.453, vM outside 1.267. A vM outside that grows with refinement marks a sharp re-entrant edge (singular): Ansys will show the same growth; judge such peaks with a fillet or at a probe away from the edge.

Chosen layout (topo 40 %, ti64_lpbf) re-meshed from its smoothed STL: 20491 T10, deformation 0.3899 mm, vM outside 135.8 MPa at limit load, utilisation **0.271** (voxel 0.297).

**Verified selection** (each chosen layout re-meshed with T10; when its T10 stress exceeds the voxel stress the ratio becomes that layout's stress factor, all materials are re-ranked and the new choice is checked again):

| Round | Material | Layout | Voxel vM (MPa) | T10 vM (MPa) | Factor | T10 utilisation |
|---|---|---|---|---|---|---|
| 1 | ti64_lpbf | topo 25 % | 392.1 | 501.8 | 1.280 | 1.001 |
| 2 | ti64_lpbf | topo 40 % | 148.9 | 135.8 | 1.000 | 0.271 |


## 3. Topology optimisation (SIMP, density filter + projection, OC)

| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |
|---|---|---|---|---|---|---|
| topo 40 % | 0.40 | 0.399 | 30 | 6.4 | 0 | 148.9 |
| topo 25 % | 0.25 | 0.251 | 30 | 7.3 | 0 | 392.1 |

Stress is the same for every isotropic material (ν = 0.3); run times: topo 40 % 20 s, topo 25 % 21 s.

## 4. Materials and eco audit at 300 °C (every material on every layout)

| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |
|---|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) (machined) | 400 | 182.7 | 163 | topo 40 % | 0.7886 | 0.915 |
| 17-4PH H1025 (wrought data; L-PBF route) (AM) | 316 | 173.0 | 816 | topo 25 % | 0.4906 | 0.834 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) (AM) | 350 | 96.8 | 590 | topo 40 % | 0.443 | 0.297 |
| Inconel 718 (L-PBF, solution + double age) (AM) | 700 | 184.0 | 1096 | topo 25 % | 0.5122 | 0.591 |
| Scalmalloy (Al-Mg-Sc, L-PBF) (AM) | 150 | 29.0 | 60 | fails Tmax | — | — |

**Choice [K]:** ti64_lpbf · topo 40 % · 0.4430 kg (baseline 1.9964 kg, saving 77.8 %).

Material cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).

Eco audit by phase (baseline vs every candidate): `eco_audit.md`.

### Life screening at 300 °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).

| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | Margin | Margin, machined surface |
|---|---|---|---|---|---|---|---|---|---|
| Structural Steel | topo 40 % (T10) | 135.8 | 86.2 | 1.00 | 0.977 | 84.2 | 95.99 | 0.88 | 0.88 |
| 17-4PH H1025 | topo 25 % (voxel) | — | — | — | — | — | — | no endurance value in our sources | — |
| Ti-6Al-4V | topo 40 % (T10) | 135.8 | 600 | 0.29 | 0.712 | 124.7 | 95.99 | 1.30 | 4.45 |
| Inconel 718 | topo 25 % (voxel) | 501.8 | 298 | 0.42 | 0.927 | 116 | 354.8 | 0.33 | 0.78 |

Sources: Structural Steel — endurance: Ansys Engineering Data 23.1 'Structural Steel' S-N at 1e6 cycles, zero mean [D]; Structural Steel — surface: machined from plate: reference surface kept [Y]; Structural Steel — temperature: Marin kd(T), Budynas & Nisbett Sec. 6-9 (steels) [D]; Structural Steel — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Ti-6Al-4V — endurance: pool 'Ti-6Al-4V L-PBF': Greitemeier via Afroz et al. 2022 Int J Fract 235 Table 3 [S]; Ti-6Al-4V — surface: HIP as-built surface / HIP + milled, same study (Greitemeier 175/600 MPa, R = −1), prev_guess/01_Ansys/research/Üç sapma alanı/A_titresim_yorulma.md §2 [S, ratio Y]; Ti-6Al-4V — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Ti-6Al-4V — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Inconel 718 — endurance: pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7 [Y]; Inconel 718 — surface: no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]; Inconel 718 — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Inconel 718 — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]

### Bolt loads: FEA vs classical bolt group (initial design)

Bolt axis z. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints.bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — size the bolts with the larger value.

| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | Clamp moment FEA (N m) |
|---|---|---|---|---|---|---|
| LC1 +x | H2 | 1018 | 788 | -981 | -411 | 24.82 |
| LC1 +x | H3 | 352 | 581 | 6 | -225 | 1.56 |
| LC1 +x | H4 | 872 | 803 | 920 | 251 | 24.11 |
| LC1 +x | H5 | 483 | 656 | 55 | 385 | 4.75 |
| LC2 +y | H2 | 881 | 639 | -566 | -1180 | 28.17 |
| LC2 +y | H3 | 664 | 639 | 581 | 1183 | 17.00 |
| LC2 +y | H4 | 663 | 606 | -728 | -834 | 26.97 |
| LC2 +y | H5 | 673 | 606 | 714 | 831 | 19.07 |
| LC3 +z | H2 | 159 | 0 | -1476 | -2012 | 49.13 |
| LC3 +z | H3 | 50 | 0 | 186 | 728 | 1.48 |
| LC3 +z | H4 | 151 | 0 | -1339 | -1568 | 43.81 |
| LC3 +z | H5 | 50 | 0 | 138 | 362 | 6.29 |

## 5. Ansys cross-check

Fill the `ansys` column of `crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`, then run `python 01_Ansys/scripts/bracket_crosscheck.py D:\Masaustu\Ideathon 2026\studies\final_2026\ansys\out\ge_step`.

## 6. Reproduce this set-up in Ansys Mechanical (checklist)

Object names are Mechanical's; this checklist was written from our set-up, not tested in Ansys here.

1. **Engineering Data**: File → Import → `materials/materials_engineering_data.xml`; assign *Structural Steel (Ansys Engineering Data default) @ 300 C (aerokit)* to the initial body (E is a table over temperature: set the body/environment temperature to 300 °C, otherwise Mechanical uses 22 °C).
2. **Supports** (one Fixed Support per bolt bore, select the cylindrical faces):
   - H2: Ø 14.48 mm, axis z, centre (-147.9, -34.0, 7.0) mm → Fixed Support on the bore face
   - H3: Ø 14.48 mm, axis z, centre (-147.9, 19.2, 7.0) mm → Fixed Support on the bore face
   - H4: Ø 13.77 mm, axis z, centre (-0.1, -37.8, 7.0) mm → Fixed Support on the bore face
   - H5: Ø 14.48 mm, axis z, centre (0.5, -0.4, 7.0) mm → Fixed Support on the bore face
3. **Loads** (one load step or one analysis per case; units N, N·m):
   - LC1 +x: Bearing Load (components) on bore H1 (Ø 18.96): X 2490.4, Y 0.0, Z 0.0 N
   - LC2 +y: Bearing Load (components) on bore H1 (Ø 18.96): X 0.0, Y 2490.4, Z 0.0 N
   - LC3 +z: Bearing Load (components) on bore H1 (Ø 18.96): X 0.0, Y 0.0, Z 2490.4 N
4. **Mesh**: quadratic tets (default SOLID187); element size 5.6, 3.6 mm to match our T10 runs; refine once more for a convergence pair.
5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius + 8.4 mm.
6. **Topology Optimization** (Structural → Topology Optimization): Objective Minimize Compliance (all load steps); Response Constraint Mass/Volume = 40 % ; Exclusion Regions: the faces of every support and load bore with a ring of 0.75 × bore radius (≥ 2 × 2.8 mm); then Validation with the chosen material.

## 7. Figures

- `f1_convergence.png` — mesh convergence of the initial design at 300 °C (H8 incompatible-mode voxels, 3 levels): (a) max deformation, (b) peak von Mises outside the hole exclusion zones; audit: 0 HATA
- `f2_materials.png` — mass of the lightest passing layout per material at 300 °C; not passing: Scalmalloy; audit: 0 HATA
- `f3_eco.png` — CO₂e by life phase, baseline vs redesign (ti64_lpbf); audit: 0 HATA
- `f4_history.png` — weighted compliance of the optimisation runs relative to the initial design (each run warm-starts from the previous volume fraction); audit: 0 HATA
- `f5_shapes.png` — (a) initial design 1.996 kg structural_steel; (b) chosen topo 40 % in ti64_lpbf 0.443 kg (iso view, renders of the STL files in cad/); audit: 0 HATA
