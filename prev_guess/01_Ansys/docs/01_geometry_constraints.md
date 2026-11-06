# 01 · Geometry constraints (CAD for CFD and structural analysis)

Prepared: 2026-10-25. For tags and event context: [00_overview.md](00_overview.md).
**[D]** I read it in this session · **[A]** a sub-agent read it · **[S]** search summary only · **[Y]** judgement · **[H]** calculation/test.

Rule: **one geometry serves both analyses.** The fluid model needs the outer surface, the structural model needs the midsurface or the solid body. Derive both from the same Discovery file. When you change one, update the other.

---

## 1. Software and files

| # | Constraint | Source |
|---|---|---|
| GA-01 | The Student package includes Discovery, SpaceClaim and DesignModeler. | [D] Ansys Student page |
| GA-02 | SpaceClaim is in maintenance mode; it cannot be installed after 2027. **The main tool is Discovery**, SpaceClaim is the fallback. | [A] CADFEM blog |
| GA-03 | Discovery Student requires a dedicated NVIDIA card; if the card is unsuitable, it does not start. This machine has a GTX 1660 Ti (6 GB); it is not in the page's architecture list. **On installation day, try starting it first thing.** If it does not start, switch to DesignModeler or SpaceClaim. | [D] page · [D] `nvidia-smi` |
| GA-04 | Student has no native CAD readers. Use STEP, IGES and Parasolid (x_t). | [S] forum |
| GA-05 | The "No Geometry Export" item on the page is not explained. If export is needed, try it early. If not, keep the whole chain inside Workbench. | [D] |
| GA-06 | A newer version opens an older file, not the other way round. Save templates in the version that will be used at the event. | [Y] |

## 2. Units, axes, naming

| # | Constraint | Source |
|---|---|---|
| GB-01 | **Metre, kg, s.** Check the units when importing. Ansys's ONERA M6 example uses inches; the 2023 card gave an explicit warning about unit conversion. | [A] · [D] card |
| GB-02 | **Axis convention:** x in the flow direction (leading edge to trailing edge), y spanwise (right wing +y), z up. Symmetry plane y = 0. In Fluent the AoA is given via the velocity components (in the x–z plane). | [Y] |
| GB-03 | **Names:** the fluid body's name should contain `fluid`. Boundaries should be named like `inlet`, `outlet`, `symmetry`, `farfield`, `wing`, `fuselage`. Fluent Meshing automatically assigns the boundary type to surfaces whose names contain inlet/outlet/symmetry. Check before Update. | [A] Ansys blog |
| GB-04 | In the structural model, prepare named selections (`spar_root`, `rib_*`, `skin_upper`). Supports and loads are attached to them; no reselection is needed when the geometry changes. | [Y] |

## 3. Aerodynamic surface

| # | Constraint | Source |
|---|---|---|
| GC-01 | **Airfoil points** must be dense at the leading and trailing edges (cosine spacing). Generator: `aerokit.aero.geometry.naca4`. The NACA 4-digit equation is tested: for 0012 max. thickness 12%, at 0.30c. | [H] tests |
| GC-02 | **Trailing edge:** the open NACA coefficient (−0.1015) gives a thickness of 0.00252c for 0012 [H]. This is a blunt trailing edge suitable for meshing. If a sharp trailing edge is needed, close it fully with −0.1036; do not leave a strip surface of near-zero thickness. Have ≥ 3–5 cells on a blunt trailing edge (CRM-NLF requires ≥ 12 [A]). | [H] · [Y] |
| GC-03 | **Planform:** computation of b, c_root, c_tip and MAC from S, AR and λ: `aerokit.aero.geometry.planform`. The MAC is the reference length; in a half model the reference area is S/2. | [H] |
| GC-04 | Close the wing tip (rounded or flat). An open tip surface is not watertight. | [Y] |
| GC-05 | Do not leave a narrow interior angle at the wing–fuselage junction; add a small fillet or fairing. Inflation layers collide in the corner. | [Y] |
| GC-06 | Delete features smaller than the target surface size: gaps of < 5 cells, tiny fillets, rivets, detailed landing gear. Clean up gap, overlap and sliver surfaces with Discovery Repair. | [S] · [Y] |
| GC-07 | The watertight workflow requires flawless geometry; there must be no gaps or leaks. For CAD that cannot be cleaned, switch to the fault-tolerant workflow. | [A] PyFluent ONERA M6 example |

## 4. Fluid volume

| # | Constraint | Source |
|---|---|---|
| GD-01 | The Describe Geometry step of the watertight workflow has no option for an enclosed external-flow volume. **Draw the far field in CAD.** Two ways: (a) subtract the body from a box and select "only fluid regions with no voids"; (b) box + Share Topology. The fault-tolerant workflow has an "Add an enclosure?" option. | [A] |
| GD-02 | **Domain size** (details in file 02). 2D: far-field radius ≥ 20–50 c. 3D: inlet ≥ 10–15 c, outlet ≥ 20–30 c, lateral ≥ 10–20 c. Blockage < 1%. | [A] · [Y] |
| GD-03 | **Half model:** the symmetry plane must be exactly at y = 0 and planar. The fuselage must be cut by the plane, and the wing root must sit on the plane. | [Y] |
| GD-04 | **BOI (body of influence)** bodies: a box extending a few chords from the trailing edge for the wake region, a cylinder around the tip for the tip vortex. They do not take part in the flow, they only refine the mesh. | [A] |
| GD-05 | There should be a single fluid body. If there is a propeller or rotor, a separate region is needed (MRF/sliding mesh); its budget can exceed 1 M cells. In that case prefer a simplification such as an actuator disk / fan boundary and state it in the report. | [Y] |

## 5. Structural geometry

| # | Constraint | Source |
|---|---|---|
| GE-01 | **Thin-walled parts** (skin, spar web, rib) should be modelled as midsurfaces for shell elements. Use midsurface extraction in Discovery/SpaceClaim. The thickness property is assigned to the surface. Details and threshold in file 03. | [Y] |
| GE-02 | The intersection edges of shell parts should be joined with shared topology (Share Topology); if they are not joined, load is not transferred or a bonded contact is needed. | [Y] |
| GE-03 | **Wing box idealisation:** front and rear spar (typically at 15–25% and 60–75% chord) + upper/lower skin + ribs. Quick hand calculation: `aerokit.structures.beam.box`. The thin box I value agrees within 1% with the exact hollow rectangle at t/h = 1%. | [H] tests · [Y] spar positions |
| GE-04 | Split the surface (split face) for support and load regions. E.g. root attachment region, fuel tank pressure region. Point loads and sharp interior corners produce singular stresses. | [Y] |
| GE-05 | **Flow → structure (one-way FSI):** if the Fluent pressure is to be transferred to Mechanical, the wetted surfaces must be at the same location and in the same units in both models. | [Y] · details in file 03 |

## 6. Conceptual design geometry (2023-type task)

| # | Constraint | Source |
|---|---|---|
| GF-01 | The 2023 Ansys card asked to leave configuration details out of scope and focus on **performance**. Keep the geometry at conceptual level: planform, section, tail volume coefficients, fuselage length. | [D] card |
| GF-02 | The numerical planform comes from W/S and AR in the `aerokit sizing raymer` output. The CAD is its **visualisation**; if CFD is needed, it is built with the same dimensions. | [H] |

## 7. Quick commands

```bash
python -m aerokit geometry airfoil --naca 2412 --chord 0.25 --output profil_2412.txt
```
```bash
python -m aerokit geometry planform --S 30 --AR 9 --taper 0.5
```
