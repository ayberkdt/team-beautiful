# Bracket redesign run — initial_exact

Input: `studies\final_2026\ansys\official_2026-11-05\visuals\initial_exact.step` (surface) · voxel 7.80 mm · 41077 elements · 145050 DOFs · working temperature **300 °C** · element H8IM · total 276 s.

All numbers below are computed by `aerokit.bracket` [K] from the files in this folder. Loads and supports are those of `setup.json` (check them: a proposal unless a human edited it). Strength criterion: von Mises outside the hole zones (radius + 3 voxels) ≤ Fty(T) at limit load and ≤ Ftu(T) at 1.5 × limit [Y].

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

Non-design rings: 12102 of 41077 elements kept solid.

## 2. Initial design, structural_steel at 300 °C

Mass **152.2707 kg** (voxel volume 19397542 mm³).

| Case | Max deformation (mm) | Compliance (J) | von Mises outside zones (MPa) | Max von Mises anywhere (MPa) | Reaction sum (N) |
|---|---|---|---|---|---|
| LC1a Fz+97 kN, Fy+24 kN each pin | 0.1922 | 16.05 | 55.31 | 222.7 | 1.998e+05 |
| LC1b Fz+97 kN, Fy-24 kN each pin | 0.2098 | 16.46 | 68.93 | 213.1 | 1.998e+05 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | 0.2056 | 18.93 | 64.25 | 213.1 | 1.94e+05 |
| LC2 My 2000 N m (1000 per pin bore) | 0.007706 | 0.1146 | 4.533 | 22.08 | 8.061e-09 |

Thinnest members (distance-transform ridge): minimum 27.3 mm = 3.5 voxels, 10th percentile 42.9 mm = 5.5 voxels.

**Thermal sensitivity** [K]: if Mechanical applies a Thermal Condition of 300 °C (reference 22 °C) with the bores fixed, constrained expansion alone gives von Mises 1124 MPa outside the hole zones (E α ΔT = 609.4 MPa, α = 1.2e-05 /K). Our strength check assumes the mounts expand with the bracket (no thermal stress) [Y] — ask the mentors (§11 Q1).

At 20 °C the worst deformation is 0.1917 mm (vs 0.2098 mm at 300 °C: ratio 1.095 = E(20)/E(T)).

## 3. Topology optimisation (SIMP, density filter + projection, OC)

| Design | Target | Kept | Iterations | Grey (%) | Overhang violations | vM outside at limit load (MPa) |
|---|---|---|---|---|---|---|
| topo 41 % | 0.41 | 0.410 | 50 | 1.8 | 0 | 238.5 |

Stress is the same for every isotropic material (ν = 0.3); run times: topo 41 % 245 s.

## 4. Materials and eco audit at 300 °C (every material on every layout)

| Material (route) | Tmax (°C) | E(T) (GPa) | Fty(T) (MPa) | Lightest passing design | Mass (kg) | Utilisation |
|---|---|---|---|---|---|---|
| Structural Steel (Ansys Engineering Data default) (machined) | 400 | 182.7 | 163 | initial | 152.3 | 0.423 |
| 17-4PH H1025 (wrought data; L-PBF route) (AM) | 316 | 173.0 | 816 | topo 41 % | 61.51 | 0.396 |
| Ti-6Al-4V (L-PBF, stress relieved / HIP) (AM) | 350 | 96.8 | 590 | initial | 85.54 | 0.138 |
| Inconel 718 (L-PBF, solution + double age) (AM) | 700 | 184.0 | 1096 | topo 41 % | 64.22 | 0.281 |
| Scalmalloy (Al-Mg-Sc, L-PBF) (AM) | 150 | 29.0 | 60 | fails Tmax | — | — |

**Choice [K]:** ss_17_4ph · topo 41 % · 61.5135 kg (baseline 152.2707 kg, saving 59.6 %).

Material cards: `materials/` (MatML XML for Engineering Data + one Markdown card each, with sources).

Eco audit by phase (baseline vs every candidate): `eco_audit.md`.

### Life screening at 300 °C (limit-load cycles 0 → σ, knock-downs for temperature and AM surface)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the 0 → σ cycle; σ = FE von Mises at limit load (includes Kt, notch sensitivity q = 1 [Y]). Margin > 1: below the endurance value at the reference cycle count. Screening only (`aerokit.bracket.lifecheck`).

| Material | Layout | σ limit (MPa) | Se,ref R = −1 (MPa) | k_surface | k_T | Se(T) (MPa) | σar (MPa) | Margin | Margin, machined surface |
|---|---|---|---|---|---|---|---|---|---|
| Structural Steel | initial (voxel) | 68.93 | 86.2 | 1.00 | 0.977 | 84.2 | 48.74 | 1.73 | 1.73 |
| 17-4PH H1025 | topo 41 % (voxel) | — | — | — | — | — | — | no endurance value in our sources | — |
| Ti-6Al-4V | initial (voxel) | 68.93 | 600 | 0.29 | 0.712 | 124.7 | 48.74 | 2.56 | 8.77 |
| Inconel 718 | topo 41 % (voxel) | 238.5 | 298 | 0.42 | 0.927 | 116 | 168.6 | 0.69 | 1.64 |

Sources: Structural Steel — endurance: Ansys Engineering Data 23.1 'Structural Steel' S-N at 1e6 cycles, zero mean [D]; Structural Steel — surface: machined from plate: reference surface kept [Y]; Structural Steel — temperature: Marin kd(T), Budynas & Nisbett Sec. 6-9 (steels) [D]; Structural Steel — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Ti-6Al-4V — endurance: pool 'Ti-6Al-4V L-PBF': Greitemeier via Afroz et al. 2022 Int J Fract 235 Table 3 [S]; Ti-6Al-4V — surface: HIP as-built surface / HIP + milled, same study (Greitemeier 175/600 MPa, R = −1), research_notes/Üç sapma alanı/A_titresim_yorulma.md §2 [S, ratio Y]; Ti-6Al-4V — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Ti-6Al-4V — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]; Inconel 718 — endurance: pool 'Inconel 718 wrought (STA)': MIL-HDBK-5J best-fit equation solved at 1e7 [Y]; Inconel 718 — surface: no IN718 AM surface data: Ti-6Al-4V as-built / milled ratio 0.42 (Greitemeier 200/475) borrowed [Y]; Inconel 718 — temperature: Ftu(T)/Ftu(20 °C) of our strength curve [Y]; Inconel 718 — notch: FE stress includes Kt; q = 1 (Kf = Kt) [Y]

### Bolt loads: FEA vs classical bolt group (initial design)

Bolt axis z. FEA: sum of the nodal reactions on each fixed bore; classical: rigid plate, elastic fastener-group split of the in-plane force and torsion (Bruhn, `aerokit.structures.joints.bolt_group`) and a linear axial split of the out-of-plane moments [derived here]. A fixed bore is a rigid clamp: it also carries a clamp moment (last column) and, where the plate bends, in-plane forces that cancel between the bolts (FEA shear above classical with zero net in-plane load). A real bolt (pin + seat) carries less of both [Y]; the gap between the columns shows how much the bolt loads depend on that idealisation — size the bolts with the larger value.

| Case | Bolt | Shear FEA (N) | Shear classical (N) | Axial FEA (N) | Axial classical (N) | Clamp moment FEA (N m) |
|---|---|---|---|---|---|---|
| LC1a Fz+97 kN, Fy+24 kN each pin | H3 | 37549 | 12030 | -64162 | -69975 | 5972.67 |
| LC1a Fz+97 kN, Fy+24 kN each pin | H4 | 15721 | 12030 | -31758 | -26821 | 3398.98 |
| LC1a Fz+97 kN, Fy+24 kN each pin | H5 | 37548 | 11970 | -65180 | -70179 | 6242.74 |
| LC1a Fz+97 kN, Fy+24 kN each pin | H6 | 16068 | 11970 | -32900 | -27025 | 3595.59 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H3 | 15797 | 12030 | -31362 | -25370 | 3361.20 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H4 | 37692 | 12030 | -64594 | -71426 | 6077.98 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H5 | 15784 | 11970 | -31982 | -25574 | 3485.27 |
| LC1b Fz+97 kN, Fy-24 kN each pin | H6 | 37790 | 11970 | -66061 | -71630 | 6371.74 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H3 | 21472 | 4 | -47726 | -47667 | 4888.02 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H4 | 21567 | 4 | -48206 | -49129 | 4992.87 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H5 | 21515 | 4 | -48777 | -47871 | 5101.52 |
| LC1c Fz+97 kN, Fy +24/-24 kN (opposite, sensitivity) | H6 | 21602 | 4 | -49292 | -49333 | 5218.76 |
| LC2 My 2000 N m (1000 per pin bore) | H3 | 129 | 3 | -2754 | -1977 | 199.85 |
| LC2 My 2000 N m (1000 per pin bore) | H4 | 133 | 3 | -2733 | -1945 | 199.99 |
| LC2 My 2000 N m (1000 per pin bore) | H5 | 130 | 3 | 2712 | 1945 | 201.14 |
| LC2 My 2000 N m (1000 per pin bore) | H6 | 134 | 3 | 2776 | 1977 | 207.61 |

## 5. Ansys cross-check

Fill the `ansys` column of `crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`, then run `python scripts/bracket_crosscheck.py studies\final_2026\ansys\official_2026-11-05\runs\topo_v2_base_kept_41`.

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
4. **Mesh**: quadratic tets (default SOLID187); element size 3 × voxel mm to match our T10 runs; refine once more for a convergence pair.
5. **Results**: Total Deformation (max), Equivalent Stress (max, and a probe away from sharp edges), Strain Energy (×2 = our compliance), Force Reaction per support. Exclusion zone used by us: bore radius + 23.4 mm.
6. **Topology Optimization** (Structural → Topology Optimization): Objective Minimize Compliance (all load steps); Response Constraint Mass/Volume = 41 % ; Exclusion Regions: the faces of every support and load bore with a ring of 0.75 × bore radius (≥ 2 × 7.8 mm); then Validation with the chosen material.

## 7. Figures

- `f2_materials.png` — mass of the lightest passing layout per material at 300 °C; not passing: Scalmalloy; audit: 0 HATA
- `f3_eco.png` — CO₂e by life phase, baseline vs redesign (ss_17_4ph); audit: 0 HATA
- `f4_history.png` — weighted compliance of the optimisation runs relative to the initial design (each run warm-starts from the previous volume fraction); audit: 0 HATA
- `f5_shapes.png` — (a) initial design 152.271 kg structural_steel; (b) chosen topo 41 % in ss_17_4ph 61.514 kg (iso view, renders of the STL files in cad/); audit: 0 HATA
