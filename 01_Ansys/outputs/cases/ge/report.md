# Bracket redesign run — GE-type engine bracket (envelope approximation)

Input: `01_Ansys\inputs\ge_bracket.json` (drawing) · voxel 2.20 mm · 22947 elements · 87870 DOFs · working temperature **300 °C** · element H8IM · total 525 s.

All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength criterion: von Mises outside the hole zones (radius + 3 voxels) ≤ Fty(T) at limit load and ≤ Ftu(T) at 1 × limit [Y].

## 1. Set-up

| Hole | Axis | Ø (mm) | Centre (mm) | Role |
|---|---|---|---|---|
| H1 | x | 19.05 | -74.0, -56.8, 44.6 | load |
| H2 | z | 14.17 | -148.1, -33.6, 7.5 | support |
| H3 | z | 14.17 | -148.1, 18.5, 7.5 | support |
| H4 | z | 14.17 | 0.0, -38.1, 7.5 | support |
| H5 | z | 14.17 | 0.0, 0.0, 7.5 | support |

| Load case | Loads |
|---|---|
| LC1 vertical 8000 lbf | H1 bearing F = [0, 0, 35585.8] N |
| LC2 horizontal 8500 lbf | H1 bearing F = [0, -37809.9, 0] N |
| LC3 42 deg 9500 lbf | H1 bearing F = [0, -28276.2, 31403.9] N |
| LC4 torsion 5000 lbf in | H1 moment M = [0, 0, -564.9] N m |

Non-design rings: 2820 of 22947 elements kept solid.

## 2. Initial design, structural_steel at 300 °C

Mass **1.9964 kg** (voxel volume 254313 mm³; exact CAD volume 254313 mm³, voxel/CAD = 1.0000).

| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |
|---|---|---|---|---|---|
| LC1 vertical 8000 lbf | 0.7136 | 16.32 | 937.3 | 937.3 | 3.559e+04 |
| LC2 horizontal 8500 lbf | 0.8342 | 19.72 | 1210 | 1210 | 3.781e+04 |
| LC3 42 deg 9500 lbf | 0.3145 | 10.42 | 621.6 | 663.5 | 4.226e+04 |
| LC4 torsion 5000 lbf in | 0.2164 | 4.199 | 519.8 | 519.8 | 6.165e-09 |

Thinnest members (distance-transform ridge): minimum 7.7 mm = 3.5 voxels, 10th percentile 7.7 mm = 3.5 voxels. **Below ~5 voxels the voxel model is too soft in bending** (GE: +21 % deformation at 3.5 voxels, +1 % at 6.3): trust the T10 numbers or rerun with a smaller `--voxel`.

**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of 300 °C (reference 22 °C) with the bores fixed, constrained expansion alone gives von Mises 1205 MPa outside the hole zones (E α ΔT = 609.4 MPa, α = 1.2e-05 /K). Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the mentors (§11 Q1).

At 20 °C the worst deformation is 0.7619 mm (vs 0.8342 mm at 300 °C: ratio 1.095 = E(20)/E(T)).

### Mesh convergence (initial design)

| Voxel (mm) | Elements | Max deformation (mm) | Compliance (J) | vM outside (MPa) | Volume (mm³) |
|---|---|---|---|---|---|
| 3.30 | 7587 | 0.6552 | 15.49 | 776.8 | 248558 |
| 2.20 | 22947 | 0.8342 | 19.72 | 1210 | 237637 |
| 1.65 | 55453 | 0.7876 | 18.54 | 1200 | 245208 |

### Conforming check: 10-node tetrahedra on the exact geometry (Ansys SOLID187 analogue)

gmsh/OCC mesh of the CAD, same set-up, consistent bore loads, PARDISO. Compare THESE numbers with an Ansys run; the voxel-vs-T10 gap is a measured discretisation effect.

| Mesh size (mm) | T10 elements | Volume (mm³) | Max deformation (mm) | vM outside (MPa) | vM max (MPa) | Time (s) |
|---|---|---|---|---|---|---|
| 4.40 | 20550 | 254314 | 0.6836 | 883.9 | 883.9 | 23 |
| 2.86 | 58580 | 254313 | 0.6882 | 1070 | 1070 | 73 |

Voxel / T10 (finest): deformation 1.212, vM outside 1.131. A vM outside that grows with refinement marks a sharp re-entrant edge (singular): Ansys will show the same growth; judge such peaks with a fillet or at a probe away from the edge.


## 3. Topology optimisation (SIMP, density filter + projection, OC)

| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |
|---|---|---|---|---|---|---|
| topo 50 % | 0.50 | 0.501 | 50 | 2.2 | 0 | 1510 |
| topo 35 % | 0.35 | 0.351 | 50 | 2.6 | 0 | 2361 |
| topo 25 % | 0.25 | 0.250 | 50 | 2.4 | 0 | 3950 |

Stress is the same for every isotropic material (ν = 0.3); run times: topo 50 % 134 s, topo 35 % 132 s, topo 25 % 121 s.

## 4. Materials and eco audit at 300 °C (every material on every layout)

| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |
|---|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) (machined) | 400 | 182.7 | 163 | none passes | — | — |
| 17-4PH H1025 (wrought data; L-PBF route) (AM) | 316 | 173.0 | 816 | none passes | — | — |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) (AM) | 350 | 96.8 | 590 | none passes | — | — |
| Inconel 718 (L-PBF, solution + double age) (AM) | 700 | 184.0 | 1096 | none passes | — | — |
| Scalmalloy (Al-Mg-Sc, L-PBF) (AM) | 150 | 29.0 | 60 | fails Tmax | — | — |

**Choice [K]:** in718_lpbf · initial · 2.0726 kg (baseline 1.9964 kg, saving -3.8 %) — **FAILS the strength criterion (utilisation 1.10); no candidate passes on any layout: check loads, criterion and sharp edges (fillets) before using this**.

Material cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).

Eco audit by phase (baseline vs every candidate): `eco_audit.md`.

### Life screening at 300 °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).

| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | Margin | Margin, machined surface |
|---|---|---|---|---|---|---|---|---|---|
| Inconel 718 | initial (voxel) | 1210 | 298 | 0.42 | 0.927 | 116 | 1152 | 0.10 | 0.24 |

Sources: Inconel 718 — endurance: pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7 [Y]; Inconel 718 — surface: no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]; Inconel 718 — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Inconel 718 — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]

### Bolt loads: FEA vs classical bolt group (initial design)

Bolt axis z. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints.bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — size the bolts with the larger value.

| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | Clamp moment FEA (N m) |
|---|---|---|---|---|---|---|
| LC1 vertical 8000 lbf | H2 | 2870 | 0 | -20106 | -28350 | 678.40 |
| LC1 vertical 8000 lbf | H3 | 838 | 0 | 2645 | 10529 | 22.19 |
| LC1 vertical 8000 lbf | H4 | 2862 | 0 | -20017 | -23098 | 663.15 |
| LC1 vertical 8000 lbf | H5 | 963 | 0 | 1892 | 5334 | 93.60 |
| LC2 horizontal 8500 lbf | H2 | 12942 | 9475 | 8346 | 17609 | 408.59 |
| LC2 horizontal 8500 lbf | H3 | 9669 | 9475 | -8563 | -17609 | 259.01 |
| LC2 horizontal 8500 lbf | H4 | 10343 | 9430 | 11473 | 12877 | 431.07 |
| LC2 horizontal 8500 lbf | H5 | 10522 | 9430 | -11256 | -12877 | 307.82 |
| LC3 42 deg 9500 lbf | H2 | 10038 | 7082 | -11364 | -11556 | 375.56 |
| LC3 42 deg 9500 lbf | H3 | 7901 | 7082 | -4219 | -4177 | 210.97 |
| LC3 42 deg 9500 lbf | H4 | 8182 | 7056 | -8879 | -10534 | 316.66 |
| LC3 42 deg 9500 lbf | H5 | 8658 | 7056 | -6941 | -5137 | 293.36 |
| LC4 torsion 5000 lbf in | H2 | 3021 | 1796 | -1144 | -8 | 74.41 |
| LC4 torsion 5000 lbf in | H3 | 953 | 1885 | 1185 | 3 | 32.14 |
| LC4 torsion 5000 lbf in | H4 | 2526 | 1827 | 1714 | -1 | 69.34 |
| LC4 torsion 5000 lbf in | H5 | 1476 | 1760 | -1755 | 7 | 40.76 |

## 5. Ansys cross-check

Fill the `ansys` column of `crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`, then run `python 01_Ansys/scripts/bracket_crosscheck.py D:\Masaustu\Ideathon 2026\studies\final_2026\ansys\out\ge`.

## 6. Reproduce this set-up in Ansys Mechanical (checklist)

Object names are Mechanical's; this checklist was written from our set-up, not tested in Ansys here.

1. **Engineering Data**: File → Import → `materials/materials_engineering_data.xml`; assign *Structural Steel (Ansys Engineering Data default) @ 300 C (aerokit)* to the initial body (E is a table over temperature: set the body/environment temperature to 300 °C, otherwise Mechanical uses 22 °C).
2. **Supports** (one Fixed Support per bolt bore, select the cylindrical faces):
   - H2: Ø 14.17 mm, axis z, centre (-148.1, -33.6, 7.5) mm → Fixed Support on the bore face
   - H3: Ø 14.17 mm, axis z, centre (-148.1, 18.5, 7.5) mm → Fixed Support on the bore face
   - H4: Ø 14.17 mm, axis z, centre (0.0, -38.1, 7.5) mm → Fixed Support on the bore face
   - H5: Ø 14.17 mm, axis z, centre (0.0, 0.0, 7.5) mm → Fixed Support on the bore face
3. **Loads** (one load step or one analysis per case; units N, N·m):
   - LC1 vertical 8000 lbf: Bearing Load (components) on bore H1 (Ø 19.05): X 0.0, Y 0.0, Z 35585.8 N
   - LC2 horizontal 8500 lbf: Bearing Load (components) on bore H1 (Ø 19.05): X 0.0, Y -37809.9, Z 0.0 N
   - LC3 42 deg 9500 lbf: Bearing Load (components) on bore H1 (Ø 19.05): X 0.0, Y -28276.2, Z 31403.9 N
   - LC4 torsion 5000 lbf in: Moment, scoped to bore H1, behaviour Deformable: X 0.00, Y 0.00, Z -564.92 N·m
4. **Mesh**: quadratic tets (default SOLID187); element size 4.4, 2.9 mm to match our T10 runs; refine once more for a convergence pair.
5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius + 6.6 mm.

## 7. Figures

- `f1_convergence.png` — mesh convergence of the initial design at 300 °C (H8 incompatible-mode voxels, 3 levels): (a) max deformation, (b) peak von Mises outside the hole exclusion zones; audit: 0 HATA
- `f3_eco.png` — CO₂e by life phase, baseline vs redesign (in718_lpbf); audit: 0 HATA
- `f4_history.png` — weighted compliance of the optimisation runs relative to the initial design (each run warm-starts from the previous volume fraction); audit: 0 HATA
- `f5_shapes.png` — (a) initial design 1.996 kg structural_steel; (b) chosen initial in in718_lpbf 2.073 kg (iso view, renders of the STL files in cad/); audit: 0 HATA
