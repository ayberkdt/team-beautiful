# Bracket redesign run — dryrun_bracket

Input: `studies\final_2026\ansys\inputs\dryrun_bracket.step` (surface) · voxel 1.30 mm · 32524 elements · 118467 DOFs · working temperature **300 °C** · element H8IM · total 965 s.

All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength criterion: von Mises outside the hole zones (radius + 3 voxels) ≤ Fty(T) at limit load and ≤ Ftu(T) at 1.5 × limit [Y].

## 1. Set-up

| Hole | Axis | Ø (mm) | Centre (mm) | Role |
|---|---|---|---|---|
| H1 | x | 11.91 | 4.1, 30.0, 52.0 | load |
| H2 | z | 6.55 | 30.0, 12.0, 4.1 | support |
| H3 | z | 6.55 | 30.0, 48.0, 4.1 | support |
| H4 | z | 8.96 | 75.0, 12.0, 4.1 | support |
| H5 | z | 8.96 | 75.0, 48.0, 4.1 | support |

| Load case | Loads |
|---|---|
| LC1 +x | H1 bearing F = [1634.9, 0.0, 0.0] N |
| LC2 +y | H1 bearing F = [0.0, 1634.9, 0.0] N |
| LC3 +z | H1 bearing F = [0.0, 0.0, 1634.9] N |

Non-design rings: 2316 of 32524 elements kept solid.

## 2. Initial design, structural_steel at 300 °C

Mass **0.5771 kg** (voxel volume 73522 mm³).

| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |
|---|---|---|---|---|---|
| LC1 +x | 0.0797 | 0.09139 | 130.2 | 131.3 | 1635 |
| LC2 +y | 0.06375 | 0.07674 | 77.62 | 150.7 | 1635 |
| LC3 +z | 0.03278 | 0.02776 | 54.77 | 93.75 | 1635 |

Thinnest members (distance-transform ridge): minimum 4.5 mm = 3.5 voxels, 10th percentile 7.2 mm = 5.5 voxels.

**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of 300 °C (reference 22 °C) with the bores fixed, constrained expansion alone gives von Mises 1061 MPa outside the hole zones (E α ΔT = 609.4 MPa, α = 1.2e-05 /K). Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the mentors (§11 Q1).

At 20 °C the worst deformation is 0.0728 mm (vs 0.0797 mm at 300 °C: ratio 1.095 = E(20)/E(T)).

### Mesh convergence (initial design)

| Voxel (mm) | Elements | Max deformation (mm) | Compliance (J) | vM outside (MPa) | Volume (mm³) |
|---|---|---|---|---|---|
| 1.95 | 9688 | 0.08475 | 0.09865 | 113.8 | 70359 |
| 1.30 | 32524 | 0.0797 | 0.09139 | 130.2 | 71145 |
| 0.97 | 78293 | 0.07901 | 0.08901 | 133.9 | 71854 |

### Conforming check: 10-node tetrahedra on the exact geometry (Ansys SOLID187 analogue)

gmsh/OCC mesh of the CAD, same set-up, consistent bore loads, PARDISO. Compare THESE numbers with an Ansys run; the voxel-vs-T10 gap is a measured discretisation effect.

| Mesh size (mm) | T10 elements | Volume (mm³) | Max deformation (mm) | vM outside (MPa) | vM max (MPa) | Time (s) |
|---|---|---|---|---|---|---|
| 2.60 | 28723 | 73522 | 0.07605 | 106.8 | 230.4 | 50 |
| 1.69 | 78805 | 73522 | 0.07652 | 123.2 | 221.7 | 125 |

Voxel / T10 (finest): deformation 1.042, vM outside 1.057. A vM outside that grows with refinement marks a sharp re-entrant edge (singular): Ansys will show the same growth; judge such peaks with a fillet or at a probe away from the edge.

Chosen layout (topo 25 %, ti64_lpbf) re-meshed from its smoothed STL: 42096 T10, deformation 0.3016 mm, vM outside 388.5 MPa at limit load, utilisation **0.775** (voxel 0.477).

**Verified selection** (each chosen layout re-meshed with T10; when its T10 stress exceeds the voxel stress the ratio becomes that layout's stress factor, all materials are re-ranked and the new choice is checked again):

| Round | Material | Layout | Voxel vM (MPa) | T10 vM (MPa) | Factor | T10 utilisation |
|---|---|---|---|---|---|---|
| 1 | ti64_lpbf | topo 25 % | 239.1 | 388.5 | 1.625 | 0.775 |


## 3. Topology optimisation (SIMP, density filter + projection, OC)

| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |
|---|---|---|---|---|---|---|
| topo 50 % | 0.50 | 0.501 | 50 | 1.3 | 0 | 124.1 |
| topo 35 % | 0.35 | 0.351 | 50 | 1.9 | 0 | 171 |
| topo 25 % | 0.25 | 0.251 | 50 | 2.2 | 0 | 239.1 |

Stress is the same for every isotropic material (ν = 0.3); run times: topo 50 % 234 s, topo 35 % 193 s, topo 25 % 183 s.

## 4. Materials and eco audit at 300 °C (every material on every layout)

| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |
|---|---|---|---|---|---|---|
| Ti-6Al-4V (L-PBF, stress relieved / HIP) (AM) | 350 | 96.8 | 590 | topo 25 % | 0.08033 | 0.775 |
| Inconel 718 (L-PBF, solution + double age) (AM) | 700 | 184.0 | 1096 | topo 25 % | 0.1484 | 0.457 |
| 17-4PH H1025 (wrought data; L-PBF route) (AM) | 316 | 173.0 | 816 | topo 25 % | 0.1422 | 0.646 |
| Scalmalloy (Al-Mg-Sc, L-PBF) (AM) | 150 | 29.0 | 60 | fails Tmax | — | — |
| Structural Steel (Ansys Engineering Data default) (machined) | 400 | 182.7 | 163 | topo 50 % | 0.288 | 0.763 |

**Choice [K]:** ti64_lpbf · topo 25 % · 0.0803 kg (baseline 0.5771 kg, saving 86.1 %).

Material cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).

Eco audit by phase (baseline vs every candidate): `eco_audit.md`.

### Life screening at 300 °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).

| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | Margin | Margin, machined surface |
|---|---|---|---|---|---|---|---|---|---|
| Ti-6Al-4V | topo 25 % (T10) | 388.5 | 600 | 0.29 | 0.712 | 124.7 | 274.7 | 0.45 | 1.56 |
| Inconel 718 | topo 25 % (T10) | 388.5 | 298 | 0.42 | 0.927 | 116 | 274.7 | 0.42 | 1.01 |
| 17-4PH H1025 | topo 25 % (T10) | — | — | — | — | — | — | no endurance value in our sources | — |
| Structural Steel | topo 50 % (voxel) | 124.1 | 86.2 | 1.00 | 0.977 | 84.2 | 87.78 | 0.96 | 0.96 |

Sources: Ti-6Al-4V — endurance: pool 'Ti-6Al-4V L-PBF': Greitemeier via Afroz et al. 2022 Int J Fract 235 Table 3 [S]; Ti-6Al-4V — surface: HIP as-built surface / HIP + milled, same study (Greitemeier 175/600 MPa, R = −1), research_notes/Üç sapma alanı/A_titresim_yorulma.md §2 [S, ratio Y]; Ti-6Al-4V — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Ti-6Al-4V — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Inconel 718 — endurance: pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7 [Y]; Inconel 718 — surface: no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]; Inconel 718 — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Inconel 718 — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Structural Steel — endurance: Ansys Engineering Data 23.1 'Structural Steel' S-N at 1e6 cycles, zero mean [D]; Structural Steel — surface: machined from plate: reference surface kept [Y]; Structural Steel — temperature: Marin kd(T), Budynas & Nisbett Sec. 6-9 (steels) [D]; Structural Steel — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]

### Bolt loads: FEA vs classical bolt group (initial design)

Bolt axis z. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints.bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — size the bolts with the larger value.

| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | Clamp moment FEA (N m) |
|---|---|---|---|---|---|---|
| LC1 +x | H2 | 428 | 406 | -480 | -870 | 23.93 |
| LC1 +x | H3 | 450 | 411 | -475 | -870 | 24.17 |
| LC1 +x | H4 | 501 | 406 | 486 | 870 | 7.22 |
| LC1 +x | H5 | 498 | 411 | 469 | 870 | 6.97 |
| LC2 +y | H2 | 1269 | 1040 | -2101 | -1087 | 16.79 |
| LC2 +y | H3 | 1268 | 1040 | 2100 | 1087 | 16.78 |
| LC2 +y | H4 | 96 | 450 | 31 | -1087 | 0.46 |
| LC2 +y | H5 | 96 | 450 | -29 | 1087 | 0.44 |
| LC3 +z | H2 | 276 | 0 | -1017 | -1291 | 15.07 |
| LC3 +z | H3 | 276 | 0 | -1027 | -1292 | 15.33 |
| LC3 +z | H4 | 137 | 0 | 208 | 475 | 2.92 |
| LC3 +z | H5 | 136 | 0 | 202 | 473 | 2.82 |

## 5. Ansys cross-check

Fill the `ansys` column of `crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`, then run `python scripts/bracket_crosscheck.py D:\Masaustu\Ideathon 2026\studies\final_2026\ansys\out\dryrun_cold`.

## 6. Reproduce this set-up in Ansys Mechanical (checklist)

Object names are Mechanical's; this checklist was written from our set-up, not tested in Ansys here.

1. **Engineering Data**: File → Import → `materials/materials_engineering_data.xml`; assign *Structural Steel (Ansys Engineering Data default) @ 300 C (aerokit)* to the initial body (E is a table over temperature: set the body/environment temperature to 300 °C, otherwise Mechanical uses 22 °C).
2. **Supports** (one Fixed Support per bolt bore, select the cylindrical faces):
   - H2: Ø 6.55 mm, axis z, centre (30.0, 12.0, 4.1) mm → Fixed Support on the bore face
   - H3: Ø 6.55 mm, axis z, centre (30.0, 48.0, 4.1) mm → Fixed Support on the bore face
   - H4: Ø 8.96 mm, axis z, centre (75.0, 12.0, 4.1) mm → Fixed Support on the bore face
   - H5: Ø 8.96 mm, axis z, centre (75.0, 48.0, 4.1) mm → Fixed Support on the bore face
3. **Loads** (one load step or one analysis per case; units N, N·m):
   - LC1 +x: Bearing Load (components) on bore H1 (Ø 11.91): X 1634.9, Y 0.0, Z 0.0 N
   - LC2 +y: Bearing Load (components) on bore H1 (Ø 11.91): X 0.0, Y 1634.9, Z 0.0 N
   - LC3 +z: Bearing Load (components) on bore H1 (Ø 11.91): X 0.0, Y 0.0, Z 1634.9 N
4. **Mesh**: quadratic tets (default SOLID187); element size 2.6, 1.7 mm to match our T10 runs; refine once more for a convergence pair.
5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius + 3.9 mm.
6. **Topology Optimization** (Structural → Topology Optimization): Objective Minimize Compliance (all load steps); Response Constraint Mass/Volume = 25 % ; Exclusion Regions: the faces of every support and load bore with a ring of 0.75 × bore radius (≥ 2 × 1.3 mm); then Validation with the chosen material.

## 7. Figures

- `f1_convergence.png` — mesh convergence of the initial design at 300 °C (H8 incompatible-mode voxels, 3 levels): (a) max deformation, (b) peak von Mises outside the hole exclusion zones; audit: 0 HATA
- `f2_materials.png` — mass of the lightest passing layout per material at 300 °C; not passing: Scalmalloy; audit: 0 HATA
- `f3_eco.png` — CO₂e by life phase, baseline vs redesign (ti64_lpbf); audit: 0 HATA
- `f4_history.png` — weighted compliance of the optimisation runs relative to the initial design (each run warm-starts from the previous volume fraction); audit: 0 HATA
- `f5_shapes.png` — (a) initial design 0.577 kg structural_steel; (b) chosen topo 25 % in ti64_lpbf 0.080 kg (iso view, renders of the STL files in cad/); audit: 0 HATA
