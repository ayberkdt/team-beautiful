# 03 · Structural mechanics constraints (Ansys Mechanical, ACP)

Prepared: 2026-10-25. Event context and tags: [00_overview.md](00_overview.md). Geometry prerequisites: [01_geometry_constraints.md](01_geometry_constraints.md).

**Tags**
- **[D]** I read it from the source in this session.
- **[A]** a sub-agent read it.
- **[S]** search summary only.
- **[Y]** judgement.
- **[H]** calculation/test (`python -m pytest`; in the 2026-10-25 run, numerical checks 2523/2523).

Ansys Help versions: v242 = 2024 R2, v251/v252 = 2025 R1/R2, v261 = 2026 R1.

---

## 0. Quick decision flow

1. **Hand calculation** (minutes): `aerokit mechanics wing`, `aerokit mechanics tensor`, `aerokit composite lamina`. Find the critical mode and the margin of safety (MS).
2. **Mechanical** (hours): model only the region the hand calculation found critical. The 128K node limit forces you to choose the model (§1).
3. **Report:** give the difference between the hand calculation and the FEA as a percentage. If the difference is large, write down the reason.

---

## 1. Licence and node budget

| # | Constraint | Source |
|---|---|---|
| MA-01 | Student structural limit **128K nodes/elements**, at most 4 cores. | [D] Ansys Student page |
| MA-02 | **Node/element ratio:** tet10 (SOLID187) ≈ 1.3 · hex20 (SOLID186) ≈ 4.2 · tet4 ≈ 0.15 · hex8 ≈ 1.1 · SHELL181 ≈ 1 · BEAM188 ≈ 1. With quadratic tets the node count hits the limit first (≈ 95–100K elements). Shell and beam elements reduce the count many times over. | [A] the sub-agent's Delaunay script; judgement |
| MA-03 | Default element order: solid body **quadratic** (SOLID187/186), surface and line body **linear** (SHELL181/BEAM188). The order can be changed per body. | [A] wb_msh v261 |
| MA-04 | At solve time, contact and remote boundary condition elements are added to the count. Even if the mesh statistics appear to be below the limit, the solution may be rejected. Target ≤ 110K nodes. | [S] forum · [Y] |

## 2. Mesh quality

| # | Constraint | Source |
|---|---|---|
| MB-01 | **Standard Mechanical error limits:** Element Quality < 5e-4 (3D) / < 0.01 (2D); Jacobian ratio (Gauss) < 0.025. **Warning (target) limit:** Element Quality < 0.05. There is no error limit for warping and aspect ratio. | [A] ds_Shape_Checking v261 (the table came back flattened, check the columns on the page) |
| MB-02 | Element Quality ranges 0–1 (1 a perfect cube); the Jacobian should be close to 1, ≤ 0 is not acceptable. | [A] v261 |
| MB-03 | Skewness bands: 0–0.25 excellent · 0.25–0.5 good · 0.5–0.75 fair · 0.75–0.9 poor · 0.9–1 bad. In 3D a good average is ≈ 0.4. | [A] msh_skewness v261 |
| MB-04 | Do not use the linear tet (degenerate) element in a critical region. In a tet-shaped linear static analysis, the quadratic element gives "better results at less cost". | [A] MAPDL Modeling Guide v251 |
| MB-05 | If you model a thin wall with solid elements, a single element through the thickness does not capture bending. Either use ≥ 2–3 quadratic elements or switch to shells. | [A] forum (community member) · [Y] |

## 3. Convergence and singularity

| # | Constraint | Source |
|---|---|---|
| MC-01 | The Convergence tool's **Allowable Change default is 20%**; reduce it to **≤ 5%**. Refinement Depth default is 2. The Zienkiewicz-Zhu error estimate is used; it gives the best results with an all-tet mesh. | [A] ds_Convergence v261 · [Y] 5% |
| MC-02 | **Adaptive convergence does not work with:** layered sections, orthotropic material, mixed-order mesh, mesh connections, linked systems. That is, it cannot be used for composites; try 3 mesh densities by hand. | [A] v261 |
| MC-03 | NAFEMS: do at least 3 runs, plot the stress at a fixed point against mesh density. With local refinement the transition zone should be ≥ 3 elements away. NAFEMS gives no percentage criterion. | [A] NAFEMS knowledge base |
| MC-04 | **Singularity:** at a zero-radius interior corner the stress grows without bound. Model the real fillet radius. Sources of peak stress at a Fixed Support edge are the Poisson effect, restrained thermal expansion and point supports. Remedy: 3-2-1 support, deformable behaviour or a support distributed over a small area. | [A] NAFEMS · [A] Ansys employee, forum 2024-12-17 |
| MC-05 | **Singular or real?** A singular stress keeps growing as the mesh is refined; the neighbouring stress and the displacement converge. Read the result a few elements away from the singularity. | [S] Ansys course |

## 4. Modelling choice: shell, solid, beam

| # | Constraint | Source |
|---|---|---|
| MD-01 | **Shell rule:** if t/L < 1/10, shell; if t/L < 1/20, thin-shell behaviour. Ansys/NAFEMS give no numerical rule. | [S] PTC 1:10 · [Y] |
| MD-02 | SHELL181 is for thin to moderately thick shells and uses first-order shear (Mindlin-Reissner). Offset options Top / Middle (default) / Bottom / User. | [S] v261 · [S] v242 |
| MD-03 | At shell–shell and shell–beam joints prefer **Share Topology** over bonded contact. Solid and shell nodes cannot be merged (different number of degrees of freedom). | [S] |
| MD-04 | **Contact default is Bonded** (automatically detected contacts are bonded, gaps are closed). The Program Controlled formulation for bonded is **MPC**; with MPC the contact pressure comes out as zero. "Large gaps and faces bonded together can result in fictitious moments." A large pinball region glues everything inside it. In shell–solid contact the contact side should be the shell and the target side the solid. | [A] v261 · v252 |
| MD-05 | Recommended model for a wing box: shell (skin, spar web, rib) + beam (stringer, spar flange). The node budget stays comfortable. | [Y] |

## 5. Boundary conditions and loads

| # | Constraint | Source |
|---|---|---|
| ME-01 | **Frictionless Support** only restrains motion normal to the surface; on a flat surface it is equivalent to a symmetry condition. | [A] v242 |
| ME-02 | **Remote point behaviour:** Deformable (like RBE3), Rigid (like CERIG), Coupled, Beam. A rigid connection "significantly stiffens" the model at the attachment point; under thermal load it gives artificial stress. Start with Deformable for the wing root attachment. | [A] v261 |
| ME-03 | **Bearing Load** applies a cosine-distributed radial pressure to part of a cylinder. If there is an axial component the solver gives an error. One load per cylinder, solid bodies only. | [A] v261 |
| ME-04 | **Inertia relief** for a free-flying aircraft: only in linear static analysis; the supports should take only the 6 rigid-body degrees of freedom; density must be defined. Not valid in a symmetric half model. | [S] |
| ME-05 | If weak springs are on, check that their reactions are ≈ 0. | [S] |
| ME-06 | Instead of a point load use a load distributed over a surface or a remote force (see MC-04). | [Y] |

## 6. Flow → structure (one-way FSI)

| # | Constraint | Source |
|---|---|---|
| MF-01 | Connect the Fluent **Solution** cell to the Static Structural **Setup** cell; an Imported Load folder is created. To pick up the load, select the CFD surface, right-click > Import Load. | [A] v242 |
| MF-02 | **"Mechanical-Based Mapping only imports normal pressure."** If wall shear stress is needed, use the CFD Results Interpolator. This option gives a **Load Transfer Summary** comparing the CFD net force with the transferred net force; put this check in the report. | [A] v242 |
| MF-03 | **Mapping validation:** Insert > Validation; Reverse Validation, Distance Based Average Comparison or Undefined Points (nodes to which no value was mapped). | [A] v261 |
| MF-04 | The wetted surfaces should be at the same location and in the same units in both models (file 01, GE-05). No Student-specific constraint was found; both are in the package. | [Y] |

## 7. Composites (ACP)

| # | Constraint | Source |
|---|---|---|
| MG-01 | ACP Pre & Post is in the Student package. | [D] |
| MG-02 | ACP failure criteria: max. strain, max. stress, Tsai-Wu, Tsai-Hill, Hashin, Puck, LaRC, Cuntze, sandwich, von Mises. | [A] ACP Theory v251 |
| MG-03 | **Ansys guidance:** "The use of all-inclusive quadratic failure criteria is not advised" (Tsai-Wu, Tsai-Hill, Hoffman). Use a criterion that separates the failure modes; Puck + Max Stress + LaRC together are more conservative. `aerokit composite lamina` gives Tsai-Wu for a quick preliminary estimate; verify in ACP with a mode-separating criterion. | [A] ACP UG v252 |
| MG-04 | The layup should be symmetric and balanced (B = 0, A16 = 0). For quasi-isotropic [0/±45/90]s, A11 = A22 and A66 = (A11 − A12)/2. | [H] tests |
| MG-05 | Adaptive convergence does not work in orthotropic and layered models (MC-02). | [A] |

## 8. Buckling and modal

| # | Constraint | Source |
|---|---|---|
| MH-01 | Eigenvalue Buckling gives the theoretical strength of an ideal elastic structure, "often yields quick but non-conservative results" and requires a prestressed static analysis first. Critical load F_cr = λ·F_applied (linear baseline). | [A] v261 · [S] course |
| MH-02 | **Thin cylinder knockdown factor (NASA SP-8007):** γ = 1 − 0.901(1 − e^−φ), φ = √(r/t)/16, r/t < 1500; 0.731 in bending. 0.75 for closely spaced, moderately sized stiffening. For composite cylinders 0.65 is not a universal value. Calculation: `aerokit.structures.beam.sp8007_reduction`. | [A] NTRS · [H] |
| MH-03 | **Panel buckling (hand calculation):** σ_cr = k·π²E/(12(1−ν²))·(t/b)², k = 4 (all four edges simply supported, long plate). The rib spacing / stringer spacing sets b. `aerokit mechanics wing --panel-b`. | [Y] classical |
| MH-04 | In a free-free modal analysis the 6 rigid-body modes should be ≈ 0 Hz. If not, the model is grounded somewhere (often penalty contact). | [S] |

## 9. Design criteria

| # | Constraint | Source |
|---|---|---|
| MI-01 | **Factor of safety 1.5 × limit load = ultimate load.** At limit load there must be no detrimental permanent deformation, at ultimate load no failure for at least 3 s. | [A] 14 CFR 25.303 / 25.305; 23.2230 |
| MI-02 | **Margin of safety** MS = allowable/(1.5·limit) − 1 ≥ 0 (MIT 16.20). `aerokit` reports it with two criteria: yield at limit load (FS 1.0), ultimate at ultimate load (FS 1.5). | [A] MIT OCW · [H] |
| MI-03 | **Load factor, transport (25.337):** n = 2.1 + 24 000/(W_lb + 10 000); at least 2.5, need not exceed 3.8. Negative −1.0. | [A] |
| MI-04 | **Load factor, Part 23 normal (old 23.337):** same formula, capped at 3.8; utility 4.4, aerobatic 6.0. Negative = −0.4·n. The current Part 23 is performance-based. `aerokit mechanics wing` uses this if n is not given (5974 kg → n = 3.14). | [A] govinfo 2011 CFR · [H] |
| MI-05 | No regulatory text was read for unmanned vehicles (STANAG 4671 could not be obtained). Use 1.5 for UAVs as well and state it in the report. | [Y] |

## 10. Materials

Values were read from the source PDFs. The aluminium values are **AA "typical"** values, not design (MMPDS A/B-basis) values; say so in the report.

**Aluminium and titanium.** In specific yield strength Ti-6Al-4V (0.19) and 7075-T6 (0.18) are neck and neck; 6061-T6 is at half of that (0.10) [D, ASM/MatWeb printouts; Ti: Aubert & Duval; ratios Fty/ρ, MPa/(kg/m³)·10³, H].

| Material | E (GPa) | ν | ρ (kg/m³) | Fty (MPa) | Ftu (MPa) | Fatigue 5e8 (MPa) |
|:---|---:|---:|---:|---:|---:|---:|
| Al 7075-T6 | 71.7 | 0.33 | 2810 | 503 | 572 | 159 |
| Al 2024-T351 | 73.1 | 0.33 | 2780 | 324 | 469 | 138 |
| Al 6061-T6 | 68.9 | 0.33* | 2700 | 276 | 310 | 97 |
| Ti-6Al-4V annealed | 110.0 | 0.34* | 4430 | > 827 | > 896 | – |
| PLA print (horizontal) | 2.3 | 0.35* | 1240 | 51 | 51* | – |

\* Not verified or assumed: for 6061, ν is an "estimate" in the source; for Ti, ν is the middle of a range; for PLA, ν and Ftu = Fty are assumptions. For PLA the interlayer strength is 17 MPa [A].

**Carbon/epoxy UD ply.** IM7 is 16% stiffer than AS4 in the fibre direction [D, Hexcel HexPly 8552 EU data sheet, 25 °C dry].

| Material | E1 (GPa) | E2 (GPa) | Xt (MPa) | Xc (MPa) | Yt (MPa) | S12 (MPa) | Ply (mm) |
|:---|---:|---:|---:|---:|---:|---:|---:|
| IM7/8552 | 164 | 12 | 2724 | 1690 | 64 | 120 | 0.131 |
| AS4/8552 | 141 | 10 | 2207 | 1531 | 81 | 114 | 0.130 |

The data sheet has **no ν12, G12 and Yc.** Marked as assumptions in the module: for IM7 ν12 0.32, G12 5.29 GPa, Yc 200 MPa; for AS4 ν12 0.30, G12 5.0 GPa, Yc 200 MPa. List: `python -m aerokit materials list`.

## 11. Sources

**Ansys Help** (root: https://ansyshelp.ansys.com/public/Views/Secured/corp/)
- [A] Shape checking: v261/en/wb_msh/ds_Shape_Checking.html
- [A] Midside nodes: v261/en/wb_msh/ds_solid_element_midside_nodes.html
- [A] Convergence: v261/en/wb_sim/ds_Convergence.html
- [A] Contact: v261/en/wb_sim/ds_Contact_Definition.html · v252/en/wb_sim/ds_Contact_Advanced.html
- [A] Frictionless support: v242/en/wb_sim/ds_Frictionless_Surface.html
- [A] Geometry behaviors: v261/en/wb_sim/ds_Geometry_Behavior.html
- [A] Bearing load: v261/en/wb_sim/ds_Bolt_Load.html
- [A] One-way FSI: v242/en/wb_sim/ds_fluid_structure_interaction_imported.html
- [A] Mapping validation: v261/en/wb_sim/sect_mapping_validation_611.html
- [A] ACP failure criteria: v251/en/acp_comp_thry/ACP_Failure_Criteria.html · v252/en/acp_ug/acp_compmodel_compfailure.html
- [A] Eigenvalue buckling: v261/en/wb2_help/wb2h_linbucklingAN.html

**Other**
- [A] NAFEMS mesh convergence: https://www.nafems.org/publications/knowledge-base/the-importance-of-mesh-convergence-part-1/
- [A] Ansys forum, singularity (2024-12-17): https://innovationspace.ansys.com/forum/forums/topic/artificial-stresses-at-the-fixed-points-in-thermo-structural-analysis
- [A] NASA SP-8007: https://ntrs.nasa.gov/api/citations/19690013955/downloads/19690013955.pdf
- [A] 14 CFR: https://www.law.cornell.edu/cfr/text/14/25.303 (/25.305, /25.337) · https://www.govinfo.gov/content/pkg/CFR-2011-title14-vol1/pdf/CFR-2011-title14-vol1-sec23-337.pdf
- [A] MIT 16.20 Unit 2: https://ocw.mit.edu/courses/16-20-structural-mechanics-fall-2002/a722d26411ef738a180981153dee1b50_unit2.pdf
- [D] Material PDFs: file 00 §6

## 12. Calculation tools (details: [05_toolkit.md](05_toolkit.md))

| Command | What it does | Verification test |
|---|---|---|
| `aerokit mechanics tensor --s σxx σyy σzz τxy τyz τxz` | principal stresses and directions, invariants, von Mises, Tresca, τmax, safety | uniaxial, pure shear, hydrostatic, Mohr, invariant preservation under transformation, Hooke round trip |
| `aerokit mechanics wing ...` | Schrenk span load, root shear and moment, box beam stress, yield/ultimate/buckling MS | elliptic root moment nWb/(3π), rectangular wing Wb/8, thin box I and Bredt J |
| `aerokit composite lamina --sequence "0,45,-45,90,s" --material IM7-8552` | CLT ABD, ply stresses, Tsai-Wu safety | Q̄(90°), quasi-isotropic A, B = 0, equilibrium Σσ·t = N, Tsai-Wu = 1 boundary |
| `aerokit.structures.beam` (Python) | Euler column, plate buckling, SP-8007 γ, I/tube/box sections | Euler π²EI/L², SP-8007 φ = 1 |
| `aerokit.structures.tensor` (Python) | strain ↔ stress, Voigt, plane traction, Mohr | as above |

Example (the wing of the 2023 task, details in file 04):
```bash
python -m aerokit mechanics wing --mass 5974 --b 15.73 --c-root 2.33 --c-tip 1.17 --box-b 1.05 --box-h 0.29 --t-skin 0.004 --t-spar 0.005 --panel-b 0.10 --material 7075-T6
```
