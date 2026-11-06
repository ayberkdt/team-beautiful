# Bracket redesign run — initial_exact

Input: `studies\final_2026\ansys\official_2026-11-05\visuals\initial_exact.step` (surface) · voxel 6.00 mm · 91918 elements · 312522 DOFs · working temperature **300 °C** · element H8IM · total 1145 s.

All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength criterion: von Mises outside the hole zones (radius + 3 voxels) × 1.5 ≤ Fty(T) (FoS on yield, mentor 5 Nov 2026); max displacement < 1.653 mm.

## 1. Set-up

| Hole | Axis | Ø (mm) | Centre (mm) | Role |
|---|---|---|---|---|
| H1 | y | 60.00 | 500.0, 65.0, 260.0 | load |
| H2 | y | 60.00 | 500.0, 335.6, 260.0 | load |
| H3 | z | 60.00 | 245.0, 95.0, 65.0 | support |
| H4 | z | 60.00 | 245.0, 305.0, 65.0 | support |
| H5 | z | 60.00 | 755.0, 95.0, 65.0 | support |
| H6 | z | 60.00 | 755.0, 305.0, 65.0 | support |

| Load case | Loads |
|---|---|
| LC1a Fz+97 kN, Fy+24 kN each pin | H1 bearing F = [0.0, 24000.0, 97000.0] N; H2 bearing F = [0.0, 24000.0, 97000.0] N |
| LC1b Fz+97 kN, Fy-24 kN each pin | H1 bearing F = [0.0, -24000.0, 97000.0] N; H2 bearing F = [0.0, -24000.0, 97000.0] N |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H1 bearing F = [0.0, 24000.0, 97000.0] N; H2 bearing F = [0.0, -24000.0, 97000.0] N |
| LC2 My 2000 N m (1000 per pin bore) | H1 moment M = [0.0, 1000.0, 0.0] N m; H2 moment M = [0.0, 1000.0, 0.0] N m |
| LC4 racking (pin alignment) Fx +24/-24 kN [Y] | H1 bearing F = [24000.0, 0.0, 0.0] N; H2 bearing F = [-24000.0, 0.0, 0.0] N |

Non-design rings: 14512 of 91918 elements kept solid.

## 2. Initial design, structural_steel at 300 °C

Mass **152.2707 kg** (voxel volume 19397542 mm³).

| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |
|---|---|---|---|---|---|
| LC1a Fz+97 kN, Fy+24 kN each pin | 0.1876 | 15.5 | 59.39 | 185.2 | 1.998e+05 |
| LC1b Fz+97 kN, Fy-24 kN each pin | 0.186 | 15.63 | 56.21 | 178.2 | 1.998e+05 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | 0.1832 | 17.87 | 55.6 | 185.3 | 1.94e+05 |
| LC2 My 2000 N m (1000 per pin bore) | 0.007672 | 0.1139 | 4.58 | 23.32 | 4.21e-09 |
| LC4 racking (pin alignment) Fx +24/-24 kN [Y] | 0.02531 | 0.9217 | 15.71 | 50.25 | 1.839e-09 |

Thinnest members (distance-transform ridge): minimum 23.8 mm = 4.0 voxels, 10th percentile 69.0 mm = 11.5 voxels.

**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of 300 °C (reference 22 °C) with the bores fixed, constrained expansion alone gives von Mises 1247 MPa outside the hole zones (E α ΔT = 609.4 MPa, α = 1.2e-05 /K). Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the mentors (§11 Q1).

At 20 °C the worst deformation is 0.1713 mm (vs 0.1876 mm at 300 °C: ratio 1.095 = E(20)/E(T)).

## 3. Topology optimisation (SIMP, density filter + projection, OC)

| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |
|---|---|---|---|---|---|---|
| topo 28 % | 0.28 | 0.281 | 60 | 1.4 | 0 | 273.9 |

Stress is the same for every isotropic material (ν = 0.3); run times: topo 28 % 1073 s.

## 4. Materials and eco audit at 300 °C (every material on every layout)

| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |
|---|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) (machined) | 400 | 182.7 | 163 | initial | 152.3 | 0.547 |
| 17-4PH H1025 (wrought data; L-PBF route) (AM) | 316 | 173.0 | 816 | topo 28 % | 42.03 | 0.503 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) (AM) | 350 | 96.8 | 590 | initial | 85.54 | 0.151 |
| Inconel 718 (L-PBF, solution + double age) (AM) | 700 | 184.0 | 1096 | topo 28 % | 43.89 | 0.375 |
| Scalmalloy (Al-Mg-Sc, L-PBF) (AM) | 150 | 29.0 | 60 | fails Tmax | — | — |

**Choice [K]:** ss_17_4ph · topo 28 % · 42.0344 kg (baseline 152.2707 kg, saving 72.4 %).

Material cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).

Eco audit by phase (baseline vs every candidate): `eco_audit.md`.

### Life screening at 300 °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).

| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | Margin | Margin, machined surface |
|---|---|---|---|---|---|---|---|---|---|
| Structural Steel | initial (voxel) | 59.39 | 86.2 | 1.00 | 0.977 | 84.2 | 42 | 2.01 | 2.01 |
| 17-4PH H1025 | topo 28 % (voxel) | — | — | — | — | — | — | no endurance value in our sources | — |
| Ti-6Al-4V | initial (voxel) | 59.39 | 600 | 0.29 | 0.712 | 124.7 | 42 | 2.97 | 10.18 |
| Inconel 718 | topo 28 % (voxel) | 273.9 | 298 | 0.42 | 0.927 | 116 | 193.7 | 0.60 | 1.43 |

Sources: Structural Steel — endurance: Ansys Engineering Data 23.1 'Structural Steel' S-N at 1e6 cycles, zero mean [D]; Structural Steel — surface: machined from plate: reference surface kept [Y]; Structural Steel — temperature: Marin kd(T), Budynas & Nisbett Sec. 6-9 (steels) [D]; Structural Steel — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Ti-6Al-4V — endurance: pool 'Ti-6Al-4V L-PBF': Greitemeier via Afroz et al. 2022 Int J Fract 235 Table 3 [S]; Ti-6Al-4V — surface: HIP as-built surface / HIP + milled, same study (Greitemeier 175/600 MPa, R = −1), research_notes/Üç sapma alanı/A_titresim_yorulma.md §2 [S, ratio Y]; Ti-6Al-4V — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Ti-6Al-4V — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Inconel 718 — endurance: pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7 [Y]; Inconel 718 — surface: no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]; Inconel 718 — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Inconel 718 — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]

### Bolt loads: FEA vs classical bolt group (initial design)

Bolt axis z. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints.bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — size the bolts with the larger value.

| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | Clamp moment FEA (N m) |
|---|---|---|---|---|---|---|
| LC1a Fz+97 kN, Fy+24 kN each pin | H3 | 38282 | 11997 | -64679 | -70188 | 6006.71 |
| LC1a Fz+97 kN, Fy+24 kN each pin | H4 | 15955 | 11997 | -32225 | -26750 | 3404.67 |
| LC1a Fz+97 kN, Fy+24 kN each pin | H5 | 38313 | 12003 | -64864 | -70250 | 6021.72 |
| LC1a Fz+97 kN, Fy+24 kN each pin | H6 | 15947 | 12003 | -32232 | -26812 | 3406.82 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H3 | 15803 | 11997 | -31846 | -25830 | 3384.13 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H4 | 38552 | 11997 | -65060 | -71107 | 6045.04 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H5 | 15801 | 12003 | -32025 | -25893 | 3397.50 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H6 | 38564 | 12003 | -65069 | -71170 | 6047.16 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H3 | 22042 | 4 | -48330 | -48028 | 4921.79 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H4 | 22237 | 4 | -48575 | -48910 | 4956.17 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H5 | 22040 | 4 | -48514 | -48090 | 4936.23 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H6 | 22229 | 4 | -48581 | -48972 | 4958.01 |
| LC2 My 2000 N m (1000 per pin bore) | H3 | 113 | 7 | -2724 | -1961 | 196.11 |
| LC2 My 2000 N m (1000 per pin bore) | H4 | 132 | 7 | -2713 | -1961 | 195.21 |
| LC2 My 2000 N m (1000 per pin bore) | H5 | 113 | 7 | 2724 | 1961 | 196.24 |
| LC2 My 2000 N m (1000 per pin bore) | H6 | 131 | 7 | 2713 | 1961 | 195.29 |
| LC4 racking (pin alignment) Fx +24/-24 kN [Y] | H3 | 8302 | 5875 | -11452 | -13 | 724.08 |
| LC4 racking (pin alignment) Fx +24/-24 kN [Y] | H4 | 7987 | 5875 | 11397 | -13 | 716.94 |
| LC4 racking (pin alignment) Fx +24/-24 kN [Y] | H5 | 7982 | 5875 | 11452 | 13 | 720.59 |
| LC4 racking (pin alignment) Fx +24/-24 kN [Y] | H6 | 8300 | 5875 | -11396 | 13 | 720.88 |

## 5. Ansys cross-check

Fill the `ansys` column of `crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`, then run `python scripts/bracket_crosscheck.py studies\final_2026\ansys\official_2026-11-05\runs\topo_v4_xbrace`.

## 6. Reproduce this set-up in Ansys Mechanical (checklist)

Object names are Mechanical's; this checklist was written from our set-up, not tested in Ansys here.

1. **Engineering Data**: File → Import → `materials/materials_engineering_data.xml`; assign *Structural Steel (Ansys Engineering Data default) @ 300 C (aerokit)* to the initial body (E is a table over temperature: set the body/environment temperature to 300 °C, otherwise Mechanical uses 22 °C).
2. **Supports** (one Fixed Support per bolt bore, select the cylindrical faces):
   - H3: Ø 60.00 mm, axis z, centre (245.0, 95.0, 65.0) mm → Fixed Support on the bore face
   - H4: Ø 60.00 mm, axis z, centre (245.0, 305.0, 65.0) mm → Fixed Support on the bore face
   - H5: Ø 60.00 mm, axis z, centre (755.0, 95.0, 65.0) mm → Fixed Support on the bore face
   - H6: Ø 60.00 mm, axis z, centre (755.0, 305.0, 65.0) mm → Fixed Support on the bore face
3. **Loads** (one load step or one analysis per case; units N, N·m):
   - LC1a Fz+97 kN, Fy+24 kN each pin: Bearing Load (components) on bore H1 (Ø 60.00): X 0.0, Y 24000.0, Z 97000.0 N
   - LC1a Fz+97 kN, Fy+24 kN each pin: Bearing Load (components) on bore H2 (Ø 60.00): X 0.0, Y 24000.0, Z 97000.0 N
   - LC1b Fz+97 kN, Fy-24 kN each pin: Bearing Load (components) on bore H1 (Ø 60.00): X 0.0, Y -24000.0, Z 97000.0 N
   - LC1b Fz+97 kN, Fy-24 kN each pin: Bearing Load (components) on bore H2 (Ø 60.00): X 0.0, Y -24000.0, Z 97000.0 N
   - LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity): Bearing Load (components) on bore H1 (Ø 60.00): X 0.0, Y 24000.0, Z 97000.0 N
   - LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity): Bearing Load (components) on bore H2 (Ø 60.00): X 0.0, Y -24000.0, Z 97000.0 N
   - LC2 My 2000 N m (1000 per pin bore): Moment, scoped to bore H1, behaviour Deformable: X 0.00, Y 1000.00, Z 0.00 N·m
   - LC2 My 2000 N m (1000 per pin bore): Moment, scoped to bore H2, behaviour Deformable: X 0.00, Y 1000.00, Z 0.00 N·m
   - LC4 racking (pin alignment) Fx +24/-24 kN [Y]: Bearing Load (components) on bore H1 (Ø 60.00): X 24000.0, Y 0.0, Z 0.0 N
   - LC4 racking (pin alignment) Fx +24/-24 kN [Y]: Bearing Load (components) on bore H2 (Ø 60.00): X -24000.0, Y 0.0, Z 0.0 N
4. **Mesh**: quadratic tets (default SOLID187); element size 3 × voxel mm to match our T10 runs; refine once more for a convergence pair.
5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius + 18.0 mm.
6. **Topology Optimization** (Structural → Topology Optimization): Objective Minimize Compliance (all load steps); Response Constraint Mass/Volume = 28 % ; Exclusion Regions: the faces of every support and load bore with a ring of 0.75 × bore radius (support), 1.047 × bore radius (load) (≥ 2 × 6.0 mm); then Validation with the chosen material.

## 7. Figures

- `f2_materials.png` — mass of the lightest passing layout per material at 300 °C; not passing: Scalmalloy; audit: 0 HATA
- `f3_eco.png` — CO₂e by life phase, baseline vs redesign (ss_17_4ph); audit: 0 HATA
- `f4_history.png` — weighted compliance of the optimisation runs relative to the initial design (each run warm-starts from the previous volume fraction); audit: 0 HATA
- `f5_shapes.png` — (a) initial design 152.271 kg structural_steel; (b) chosen topo 28 % in ss_17_4ph 42.034 kg (iso view, renders of the STL files in cad/); audit: 0 HATA
