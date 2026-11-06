# Bracket redesign run — Sketch-type mounting bracket (rehearsal, invented dimensions)

Input: `01_Ansys\inputs\sketch_bracket.json` (drawing) · voxel 1.70 mm · 22439 elements · 83007 DOFs · working temperature **300 °C** · element H8IM · total 728 s.

All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength criterion: von Mises outside the hole zones (radius + 3 voxels) ≤ Fty(T) at limit load and ≤ Ftu(T) at 1.5 × limit [Y].

## 1. Set-up

| Hole | Axis | Ø (mm) | Centre (mm) | Role |
|---|---|---|---|---|
| H1 | y | 14.00 | 60.0, 30.0, 55.0 | load |
| H2 | z | 8.50 | 15.0, 15.0, 4.0 | support |
| H3 | z | 8.50 | 15.0, 45.0, 4.0 | support |
| H4 | z | 8.50 | 105.0, 15.0, 4.0 | support |
| H5 | z | 8.50 | 105.0, 45.0, 4.0 | support |

| Load case | Loads |
|---|---|
| LC1 +x | H1 bearing F = [2544.1, 0.0, 0.0] N |
| LC2 +y | H1 bearing F = [0.0, 2544.1, 0.0] N |
| LC3 +z | H1 bearing F = [0.0, 0.0, 2544.1] N |

Non-design rings: 1861 of 22439 elements kept solid.

## 2. Initial design, structural_steel at 300 °C

Mass **0.8515 kg** (voxel volume 108475 mm³; exact CAD volume 108475 mm³, voxel/CAD = 1.0000).

| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |
|---|---|---|---|---|---|
| LC1 +x | 0.007192 | 0.01473 | 37.72 | 60.07 | 2544 |
| LC2 +y | 0.1332 | 0.2244 | 130.2 | 130.2 | 2544 |
| LC3 +z | 0.004834 | 0.01043 | 22.75 | 59.82 | 2544 |

Thinnest members (distance-transform ridge): minimum 9.3 mm = 5.5 voxels, 10th percentile 9.3 mm = 5.5 voxels.

**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of 300 °C (reference 22 °C) with the bores fixed, constrained expansion alone gives von Mises 1198 MPa outside the hole zones (E α ΔT = 609.4 MPa, α = 1.2e-05 /K). Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the mentors (§11 Q1).

At 20 °C the worst deformation is 0.1217 mm (vs 0.1332 mm at 300 °C: ratio 1.095 = E(20)/E(T)).

### Mesh convergence (initial design)

| Voxel (mm) | Elements | Max deformation (mm) | Compliance (J) | vM outside (MPa) | Volume (mm³) |
|---|---|---|---|---|---|
| 2.55 | 6338 | 0.1516 | 0.2622 | 136.8 | 101602 |
| 1.70 | 22439 | 0.1332 | 0.2244 | 130.2 | 105021 |
| 1.27 | 52791 | 0.1393 | 0.238 | 165.1 | 105191 |

### Conforming check: 10-node tetrahedra on the exact geometry (Ansys SOLID187 analogue)

gmsh/OCC mesh of the CAD, same set-up, consistent bore loads, PARDISO. Compare THESE numbers with an Ansys run; the voxel-vs-T10 gap is a measured discretisation effect.

| Mesh size (mm) | T10 elements | Volume (mm³) | Max deformation (mm) | vM outside (MPa) | vM max (MPa) | Time (s) |
|---|---|---|---|---|---|---|
| 3.40 | 21386 | 108475 | 0.1325 | 131 | 131 | 42 |
| 2.21 | 56512 | 108475 | 0.1338 | 166.7 | 166.7 | 115 |

Voxel / T10 (finest): deformation 0.995, vM outside 0.781. A vM outside that grows with refinement marks a sharp re-entrant edge (singular): Ansys will show the same growth; judge such peaks with a fillet or at a probe away from the edge.

Chosen layout (topo 25 %, ti64_lpbf) re-meshed from its smoothed STL: 28079 T10, deformation 0.6938 mm, vM outside 264.5 MPa at limit load, utilisation **0.528** (voxel 0.894).

**Verified selection** (each chosen layout re-meshed with T10; when its T10 stress exceeds the voxel stress the ratio becomes that layout's stress factor, all materials are re-ranked and the new choice is checked again):

| Round | Material | Layout | Voxel vM (MPa) | T10 vM (MPa) | Factor | T10 utilisation |
|---|---|---|---|---|---|---|
| 1 | ti64_lpbf | topo 25 % | 447.8 | 264.5 | 1.000 | 0.528 |


## 3. Topology optimisation (SIMP, density filter + projection, OC)

| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |
|---|---|---|---|---|---|---|
| topo 50 % | 0.50 | 0.500 | 50 | 1.0 | 0 | 202 |
| topo 35 % | 0.35 | 0.351 | 50 | 1.4 | 0 | 273.2 |
| topo 25 % | 0.25 | 0.251 | 50 | 1.4 | 0 | 447.8 |

Stress is the same for every isotropic material (ν = 0.3); run times: topo 50 % 110 s, topo 35 % 140 s, topo 25 % 160 s.

## 4. Materials and eco audit at 300 °C (every material on every layout)

| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |
|---|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) (machined) | 400 | 182.7 | 163 | initial | 0.8515 | 0.8 |
| 17-4PH H1025 (wrought data; L-PBF route) (AM) | 316 | 173.0 | 816 | topo 25 % | 0.2117 | 0.744 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) (AM) | 350 | 96.8 | 590 | topo 25 % | 0.1196 | 0.894 |
| Inconel 718 (L-PBF, solution + double age) (AM) | 700 | 184.0 | 1096 | topo 25 % | 0.221 | 0.527 |
| Scalmalloy (Al-Mg-Sc, L-PBF) (AM) | 150 | 29.0 | 60 | fails Tmax | — | — |

**Choice [K]:** ti64_lpbf · topo 25 % · 0.1196 kg (baseline 0.8515 kg, saving 86.0 %).

Material cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).

Eco audit by phase (baseline vs every candidate): `eco_audit.md`.

### Life screening at 300 °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).

| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | Margin | Margin, machined surface |
|---|---|---|---|---|---|---|---|---|---|
| Structural Steel | initial (voxel) | 130.2 | 86.2 | 1.00 | 0.977 | 84.2 | 92.07 | 0.91 | 0.91 |
| 17-4PH H1025 | topo 25 % (T10) | — | — | — | — | — | — | no endurance value in our sources | — |
| Ti-6Al-4V | topo 25 % (T10) | 264.5 | 600 | 0.29 | 0.712 | 124.7 | 187 | 0.67 | 2.29 |
| Inconel 718 | topo 25 % (T10) | 264.5 | 298 | 0.42 | 0.927 | 116 | 187 | 0.62 | 1.48 |

Sources: Structural Steel — endurance: Ansys Engineering Data 23.1 'Structural Steel' S-N at 1e6 cycles, zero mean [D]; Structural Steel — surface: machined from plate: reference surface kept [Y]; Structural Steel — temperature: Marin kd(T), Budynas & Nisbett Sec. 6-9 (steels) [D]; Structural Steel — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Ti-6Al-4V — endurance: pool 'Ti-6Al-4V L-PBF': Greitemeier via Afroz et al. 2022 Int J Fract 235 Table 3 [S]; Ti-6Al-4V — surface: HIP as-built surface / HIP + milled, same study (Greitemeier 175/600 MPa, R = −1), prev_guess/01_Ansys/research/Üç sapma alanı/A_titresim_yorulma.md §2 [S, ratio Y]; Ti-6Al-4V — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Ti-6Al-4V — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Inconel 718 — endurance: pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7 [Y]; Inconel 718 — surface: no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]; Inconel 718 — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Inconel 718 — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]

### Bolt loads: FEA vs classical bolt group (initial design)

Bolt axis z. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints.bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — size the bolts with the larger value.

| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | Clamp moment FEA (N m) |
|---|---|---|---|---|---|---|
| LC1 +x | H2 | 690 | 637 | -742 | -719 | 4.81 |
| LC1 +x | H3 | 694 | 635 | -750 | -719 | 4.96 |
| LC1 +x | H4 | 651 | 637 | 735 | 719 | 4.74 |
| LC1 +x | H5 | 661 | 635 | 756 | 719 | 5.14 |
| LC2 +y | H2 | 962 | 640 | -2102 | -2146 | 17.91 |
| LC2 +y | H3 | 946 | 640 | 2082 | 2146 | 16.28 |
| LC2 +y | H4 | 942 | 632 | -2132 | -2146 | 18.96 |
| LC2 +y | H5 | 953 | 632 | 2152 | 2146 | 19.20 |
| LC3 +z | H2 | 337 | 0 | -642 | -647 | 4.86 |
| LC3 +z | H3 | 338 | 0 | -621 | -626 | 4.68 |
| LC3 +z | H4 | 336 | 0 | -636 | -646 | 4.92 |
| LC3 +z | H5 | 340 | 0 | -644 | -625 | 5.26 |

## 5. Ansys cross-check

Fill the `ansys` column of `crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`, then run `python 01_Ansys/scripts/bracket_crosscheck.py D:\Masaustu\Ideathon 2026\studies\final_2026\ansys\out\sketch`.

## 6. Reproduce this set-up in Ansys Mechanical (checklist)

Object names are Mechanical's; this checklist was written from our set-up, not tested in Ansys here.

1. **Engineering Data**: File → Import → `materials/materials_engineering_data.xml`; assign *Structural Steel (Ansys Engineering Data default) @ 300 C (aerokit)* to the initial body (E is a table over temperature: set the body/environment temperature to 300 °C, otherwise Mechanical uses 22 °C).
2. **Supports** (one Fixed Support per bolt bore, select the cylindrical faces):
   - H2: Ø 8.50 mm, axis z, centre (15.0, 15.0, 4.0) mm → Fixed Support on the bore face
   - H3: Ø 8.50 mm, axis z, centre (15.0, 45.0, 4.0) mm → Fixed Support on the bore face
   - H4: Ø 8.50 mm, axis z, centre (105.0, 15.0, 4.0) mm → Fixed Support on the bore face
   - H5: Ø 8.50 mm, axis z, centre (105.0, 45.0, 4.0) mm → Fixed Support on the bore face
3. **Loads** (one load step or one analysis per case; units N, N·m):
   - LC1 +x: Bearing Load (components) on bore H1 (Ø 14.00): X 2544.1, Y 0.0, Z 0.0 N
   - LC2 +y: Bearing Load (components) on bore H1 (Ø 14.00): X 0.0, Y 2544.1, Z 0.0 N
   - LC3 +z: Bearing Load (components) on bore H1 (Ø 14.00): X 0.0, Y 0.0, Z 2544.1 N
4. **Mesh**: quadratic tets (default SOLID187); element size 3.4, 2.2 mm to match our T10 runs; refine once more for a convergence pair.
5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius + 5.1 mm.
6. **Topology Optimization** (Structural → Topology Optimization): Objective Minimize Compliance (all load steps); Response Constraint Mass/Volume = 25 % ; Exclusion Regions: the faces of every support and load bore with a ring of 0.75 × bore radius (≥ 2 × 1.7 mm); then Validation with the chosen material.

## 7. Figures

- `f1_convergence.png` — mesh convergence of the initial design at 300 °C (H8 incompatible-mode voxels, 3 levels): (a) max deformation, (b) peak von Mises outside the hole exclusion zones; audit: 0 HATA
- `f2_materials.png` — mass of the lightest passing layout per material at 300 °C; not passing: Scalmalloy; audit: 0 HATA
- `f3_eco.png` — CO₂e by life phase, baseline vs redesign (ti64_lpbf); audit: 0 HATA
- `f4_history.png` — weighted compliance of the optimisation runs relative to the initial design (each run warm-starts from the previous volume fraction); audit: 0 HATA
- `f5_shapes.png` — (a) initial design 0.852 kg structural_steel; (b) chosen topo 25 % in ti64_lpbf 0.120 kg (iso view, renders of the STL files in cad/); audit: 0 HATA
