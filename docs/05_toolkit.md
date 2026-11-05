# 05 · Calculation tools: aerokit (mechanics, FEM, materials, CAD, preliminary design)

Prepared: 2026-10-25. Package: `src/aerokit/` (Python ≥ 3.11, 3.12.1 on this machine; numpy, scipy; matplotlib + datawiz for figures; optional pyvista for CAD). Layout and installation: `README.md`.
**Verification:** `python -m pytest` (from the root directory). Every numerical check carries its expected value and its source; at the end of the session the line `aerokit numerical checks: N/N passed` is printed.

Tags:
- **[D]** I read it from the source.
- **[A]** a sub-agent read it.
- **[T]** derivation or independent numerical check.
- **[K]** run with a command in this session (command given next to it).

Commands work from the project root with `PYTHONPATH=src` or after `pip install -e .`. The short form `aerokit <group> <command>` used in the text means `python -m aerokit <group> <command>` (the `aerokit` script exists only after installation).

---

## 1. Layout

| Folder | Contents |
|---|---|
| `src/aerokit/` | package: `aero`, `structures`, `composites`, `materials`, `fem`, `optimization`, `cad`, `output`, `references`, `cli`, `verification.py` |
| `src/aerokit/data/examples/` | example models: `cantilever_frame.json`, `plate_q8.json`, `truss_bridge.json`; `cad/wing_naca2412.stl`, `cad/box.stl`, `cad/profile_L.dxf` |
| `src/aerokit/materials/data/` | 48 MIL-HDBK-5J material pages (Markdown) + `index.md` + `figures/` |
| `tests/` | pytest suite: one folder per subpackage + `integration`, `security`, `typing`, `robustness` |
| `scripts/` | `flow_tables.py`, `build_references.py`, `make_figures.py`, `materials/extract_mil_hdbk_5.py`, `materials/verify_tables.py` |
| `docs/` | these notes (00–05) and the generated `references.md` |
| `references/` | `competition/` (competition PDFs), `materials/` (MIL-HDBK-5J PDF, CMH-17 8552/IM7 PDF, `verification_report.md`) |
| `outputs/` | example figures (PNG, PDF, CVD preview, `*.denetim.txt`) |
| `archive/` | v1 note and the old `hesap` package (`hesap_legacy_2026-10-25.zip`) |

## 2. Command line (7 groups)

| Group | Commands | What it does |
|---|---|---|
| `aero` | `isa` · `flow` | ISA table; Re, Mach, first cell, layer count, Fluent cell budget (`--growth`, `--surface`) |
| `geometry` | `airfoil` · `planform` · `cad` | NACA 4 points (`--naca --chord --output`); trapezoidal wing dimensions; **STL/OBJ/PLY import → geometry report + optional tetrahedral FEM** (`--fem`) |
| `mechanics` | `tensor` · `wing` · `section` · `buckling` · `vessel` · `life` · `joint` | stress tensor; wing root (`--c-root --c-tip --t-skin`); section (including DXF); column/plate/cylinder buckling; Lamé and rotating disk; fatigue and crack; bolt margins |
| `composite` | `lamina` · `failure` · `layup` | CLT + Tsai-Wu; laminate constants + FPF/LPF (8 criteria); layup optimisation |
| `fem` | `solve` · `example` · `convergence` · `topology` · `optimum` · `verify` | solve a JSON model; examples; mesh convergence (GCI); SIMP topology; minimum-mass truss; FEM tests |
| `sizing` | `raymer` · `design` · `mission` · `validate` · `vn` · `point` · `box` | Raymer + constraint diagram; **requirements file → sized design, compliance, sensitivity, figures, report** (`design`); **search-mission plan, coverage, waypoints, STK Aviator sheet** (`mission`); King Air 350i validation (`validate`); FAR 23 V-n; optimum design point; minimum-mass wing box |
| `materials` | `list` · `allowable` · `curve` | catalogue (`--handbook`: 48 MIL-HDBK-5J pages); A/B/S-basis allowables; Ramberg-Osgood curve |

Options of each group and command: `python -m aerokit <group> --help`, `python -m aerokit <group> <command> --help`.

```bash
python -m aerokit --help
```

**Output format.** Every command ends with a single `Result:` sentence and a single `Next step:` line. `--format text|md|json|csv` selects the format; `--out rapor.md` writes the same report to a file (format from the extension: `.txt`, `.md`, `.json`, `.csv`).

```bash
python -m aerokit aero isa --h 0 3000 10000 --out outputs/isa.md
```
```bash
python -m aerokit aero isa --h 0 --format json
```

Examples:
```bash
python -m aerokit geometry cad src/aerokit/data/examples/cad/wing_naca2412.stl --material 6061-T6 --fem --axis y --load 500 --load-direction z
```
```bash
python -m aerokit sizing vn --mass 5974 --S 27.5 --c 1.81 --CLmax 2.0 --CLa 5.2 --plot outputs/vn
```
```bash
python -m aerokit fem solve src/aerokit/data/examples/plate_q8.json --plot outputs/plate
```
```bash
python -m aerokit fem example cantilever_frame
```
```bash
python -m aerokit composite failure --sequence "0,45,-45,90,s" --material IM7-8552 --criterion puck
```
```bash
python -m aerokit materials allowable 7075-T6 --thickness 2
```

On error a one-line message is given (e.g. `Error (KeyError): ...`, exit code 1). For the full traceback set the environment variable `AEROKIT_TRACE=1`.

## 3. Python modules

| Subpackage | Module | Contents |
|---|---|---|
| `aero` | `atmosphere` | ISA 0–20 km (`isa`, `sigma`) |
| | `flow` | Re, Mach, first cell (y⁺), boundary layer, layer count, cell budget, grid sequence, GCI (`gci`), AoA velocity components |
| | `geometry` | NACA 4 (`naca4`), trapezoidal planform (`planform`), point file |
| | `wing` | Schrenk load, shear and moment, FAR 23 n (`n_limit_far23_normal`) |
| | `loads` | V-n (FAR 23/25 manoeuvre + gust), design speeds, landing load, root bending |
| | `sizing` | Raymer: take-off weight, mission fractions, constraint diagram |
| | `stability` | CLα (DATCOM), downwash, neutral point, static margin, trim, tail sizing |
| | `weight` | mass, CG, %MAC, inertia; CG envelope; Raymer GA group weights |
| `structures` | `tensor` | `Stress`: principal values and directions, invariants, von Mises, Tresca, plane traction, transformation; Hooke, Voigt, Mohr |
| | `section` | arbitrary polygon via Green's theorem (with holes, composite); thin-walled open section (`ThinOpenSection`: shear centre, J, Cw); multi-cell torsion |
| | `beam` | rectangular/tube/I/box section, Bredt, Euler, plate buckling, SP-8007 γ (`sp8007_reduction`), margin of safety |
| | `buckling` | Euler/Johnson/secant, Ramberg-Osgood tangent modulus, plate compression/shear/bending k, interaction, plasticity η, crippling (Gerard), SP-8007 cylinders, lateral-torsional |
| | `joints` | shear/bearing/net section/tear-out, bolt group, Swift/Huth flexibility, preload and stiffness, NASA-STD-5020B |
| | `pressure`, `rotating` | thin/thick cylinder and sphere, interference fit, autofrettage; rotating disk/ring/rod, burst speed, thermal term |
| | `contact` | Hertz sphere, cylinder, elliptical |
| | `fatigue`, `fracture` | S-N, ε-N, Marin, mean stress, ASTM E1049 rainflow, Miner, Kt/Neuber; SIF, residual strength, critical crack, Paris/Walker/Forman |
| | `structural_sizing` | flange/skin/rib/boom sizing, multi-boom section, tube, wing mass |
| `composites` | `lamina`, `laminate` | single-material CLT + Tsai-Wu; micromechanics, off-axis constants, ABD, hygrothermal, 8 failure criteria (including Puck, LaRC03), progressive failure, orthotropic plate buckling, sandwich |
| `materials` | `library`, `handbook` | catalogue (typical values) and `design_values`; MIL-HDBK-5J reader (`get_allowable`, Ramberg-Osgood). Details §5 |
| `fem` | (submodules) | see §4 below |
| `optimization` | `sizing`, `topology`, `design`, `laminate` | see §7 below |
| `cad` | `surface`, `readers`, `dxf`, `report` | see §6 below |
| `output` | `tables`, `report`, `console`, `writers`, `figures` | see §9 below |
| `references` | `cite`, `REFERENCES` | see §8 below |
| (root) | `verification` | `check`, `check_true`, `expect_error`, `summary`: sourced numerical check log |

## 4. FEM (`aerokit.fem`)

**Architecture.**
- **`model.Model`:** nodes, elements, loads. Degree-of-freedom number `node · ndof + local`.
  - SPC: `Model.fix(node, dofs, value)`.
  - MPC (`Σ cᵢ uᵢ = r`): `add_mpc`, `tie`, `rigid_link_2d`. Eliminated with the master–slave transformation `u = T q + g`; the reduced `Tᵀ K T` stays symmetric positive definite (Cook 2002, Ch. 9).
  - Elements of the same type are assembled with a single BLAS call; the COO→CSR pattern is cached.
- **`solvers`:**
  - Direct: SuperLU sparse LU, `MMD_AT_PLUS_A` ordering, symmetric mode. `Factorization` is reused for new right-hand sides (load cases, Newmark and Newton steps).
  - Singular matrix: zero-stiffness degrees of freedom are reported by name (`SingularMatrixError`).
  - Every solution is verified by its relative residual (above `residual_tol` 1e-6 → error).
  - Iterative: PCG (Jacobi or ILU preconditioner). `method="auto"` switches to PCG above 400 000 unknowns.
  - Condition number estimate: Hager-Higham 1-norm (`condition_estimate`, `Model.condition_estimate`).
  - Eigenvalues (`generalized_eigh`): dense LAPACK for ≤ 500 unknowns, ARPACK above (falls back to LAPACK if it does not converge).
- **`results`:** typed result objects (`StaticResult`, `ModalResult`, `BucklingResult`, `TransientResult`, `HarmonicResult`, `NonlinearResult`, `SolverInfo`).
- **`reader`:** the CLI's JSON model input. **`mesh`:** `mesh2d` (mapped 2D: plate with hole, Cook, ring), `mesh3d` (box, **tetrahedral mesh from a closed surface**: winding number + Delaunay + sliver element removal).

**Elements (`elements`):**
- `line`: `Bar` (2D/3D truss), `Frame2D` (with geometric stiffness), `Frame3D`.
- `plane`: `T3`, `Q4`, `QM6` (incompatible modes), `Q8`. Plane stress / plane strain / axisymmetric; isotropic or orthotropic.
- `plate`: `MITC4` Mindlin (prestressed buckling).
- `solid`: `T4`, `T10`, `H8`.
- `discrete`: `Spring` (along a local degree of freedom or a direction vector), `Dashpot`, `PointMass`.
- `thermal`: `HeatT3`, `HeatQ4`, `HeatQ8`, `HeatTet4`, `HeatH8`.

**Analyses:**

| Analysis | Entry point | Note |
|---|---|---|
| Linear static | `Model.static(F=...)` | if `F` is `(n_dof, n_case)`, all load cases with a single factorisation |
| Modal | `Model.modal(n, lumped=...)` | consistent/lumped mass; participation factor `Γ = φᵀ M r` and effective mass `Γ²` (Bathe 2014 §10.2) |
| Linear buckling | `Model.buckling(n)` | `(K + λ K_G) φ = 0`; for large models `−K_G φ = μ K φ` with ARPACK |
| Dynamic | `dynamics` | `newmark` (Newmark-β, HHT-α), `central_difference` (lumped mass, `Δt < 2/ω_max`), `modal_superposition`, `harmonic` / `harmonic_modal`, Rayleigh damping. Homogeneous constraints only |
| Nonlinear | `nonlinear` | truss (total Lagrangian, St. Venant-Kirchhoff): `newton_raphson`, `arc_length` (Crisfield cylindrical arc length) |
| Thermal | `thermal` | steady heat conduction (`ndof = 1`), convection / heat flux boundary, `thermal_load` (α ΔT), `thermal_stresses` |
| Error estimation | `error_estimation` | Zienkiewicz-Zhu (`zz_error_estimate`, SPR or averaging), `effectivity_index`; 2D continuum |
| Mesh convergence | `convergence.study` | systematic refinement, observed order, Richardson, GCI |

**Loads:** edge and surface load (pressure/traction), body force, rotation (centrifugal).

| Verification | Result | Source |
|---|---|---|
| Patch test (2D T3/Q4/QM6/Q8, 3D T4/T10/H8, MITC4 plate) | exact (1e-14) | MacNeal & Harder 1985 [D] |
| Cook membrane Q4 / QM6 2×2 | 11.85 / 21.05 exactly | Bergan & Felippa 1985, Enercalc C-04 [D] |
| NAFEMS LE1 σyy(D) | 92.7 MPa, within 1% | NAFEMS / COMSOL / Abaqus [D] |
| Kirsch Kt = 3 (exact traction from the boundary) | within 0.5% | Timoshenko & Goodier §35 [T] |
| Lamé, rotating cylinder and disk | 0.1–0.5% | Timoshenko & Goodier §28, §32 [T] |
| Euler buckling (4 end conditions) | convergence order 4 verified | Timoshenko & Gere 1961 [T] |
| Beam/plate frequencies, Navier plate (0.00406, 0.01013) | 0.02–1% | Timoshenko & Woinowsky-Krieger [T, D coefficients] |
| Cross: FEM ↔ `structures.pressure`, `rotating`, `buckling`, `composites.laminate`, `fatigue` (Howland), `fracture` (Tada, Feddersen) | 0.1–2% | independent modules (`tests/integration`) |
| Cross: CAD wing T10 FEM ↔ sliced beam integral | 3.9% | [T] |

**My own errors fixed in the old `hesap` version:**
- The reference point of the Cook membrane (48, 52). When the corner (48, 60) was used, the result went to ~25.2.
- The T10 mass needed a degree-4 rule; the test caught the insufficient n = 3 rule.
- The sliver element threshold 0.02 discarded 8% of the volume; it was lowered to 0.005.

**Speed:** the stiffness of elements with the same type and material is assembled in batch (BLAS matmul). Same result as the loop: relative difference 4.8e-15 on 1920 T10 elements; speed 4.7× (first assembly) and 9.8× (second assembly with the cached pattern) [K, one-off script on the same mesh as `tests/fem/test_performance.py::test_batch_3d_equality_and_speed`]. Test threshold > 3×. The old note said 6.5×.

**Mesh convergence tool (`fem convergence`, `aerokit.fem.convergence.study`):** systematic refinement, observed order, Richardson and GCI. For Euler buckling it finds p ≈ 4; for the Cook membrane the Richardson value is 23.96. In the `plate_q8.json` example (1 2 4 times mesh) p = 1.72, GCI(fine) 0.023% [K, the `fem convergence` command below].

```bash
python -m aerokit fem convergence src/aerokit/data/examples/plate_q8.json
```
```bash
python -m aerokit fem verify
```

`fem verify` runs the FEM tests: 102 tests passed, 553/553 numerical checks, 53 s [K, 2026-10-25].

## 5. Materials (`aerokit.materials`)

| Layer | Contents |
|---|---|
| `library.MATERIALS` | preliminary design catalogue (SI). Aluminium values are AA **typical** (ASM/MatWeb), not design values. Every record carries `source` and the list of fields that could not be verified (`unverified`) |
| `library.design_values(name, basis, direction, thickness)` | the same record; strength, modulus and density replaced by MIL-HDBK-5J allowables |
| `handbook` | strict parser of the `materials/data/*.md` pages: `get_allowable`, `lookup_allowable`, `list_materials`, `load_material`, Ramberg-Osgood (`stress_strain_curve`, tangent modulus) |
| `materials/data/*.md` | 48 MIL-HDBK-5J pages [K, `handbook.list_materials()` → 48]: 2024, 2219, 6061, 7050, 7075 aluminium, 15-5PH, 17-4PH, 300M, 4130, Inconel 718, Ti-6Al-4V. Values as in the source (ksi); converted on request |

**Basis definition** (handbook docstring, citing MIL-HDBK-5J PDF pp. 1415 and 1684; I did not open the PDF in this session): A-basis the lesser of T99 and the specification minimum; B-basis T90; S-basis the specification minimum. Hence A ≤ B and A ≤ S.

**Verification report:** `references/materials/verification_report.md`. In the report (I did not regenerate it in this session, I read it from the file): 3553 design table cells and 65 Ramberg-Osgood values were found on the cited PDF page with two separate parsers (pdfplumber, PyMuPDF); missing 0. Generator: `scripts/materials/extract_mil_hdbk_5.py`; verifier: `scripts/materials/verify_tables.py`.

```python
from aerokit.materials import handbook, library
handbook.get_allowable("al-7075-t6", "Fty", basis="A", direction="L", thickness=2e-3)   # Pa → 4.826e8
library.design_values("7075-T6", basis="B", thickness=2e-3)                            # dict, Fty 4.964e8 Pa
```

Results [K, the two lines above, 2026-10-25]. The same A-basis value from the CLI: `materials allowable 7075-T6 --thickness 2` → Fty 482.6 MPa, Ftu 537.8 MPa (Table 3.7.6.0(b1), PDF p. 673).

```bash
python -m aerokit materials list --handbook
```
```bash
python -m aerokit materials curve 7075-T6 --thickness 2
```

**Known inconsistency** (`library` docstring): the AA typical Fty value of 2024-T351 (324 MPa) is below the MIL-HDBK-5J sheet A-basis values (48–50 ksi); the Ti-6Al-4V record is a supplier minimum.

## 6. CAD import (`aerokit.cad`)

| Format | Status |
|---|---|
| STL (ASCII/binary), OBJ, PLY | built-in reading (+ STL/OBJ writing), hardened against corrupt files, tested |
| glTF, VTK | via pyvista (pyvista is installed on this machine) |
| DXF (LINE, LWPOLYLINE + arc, POLYLINE, CIRCLE, ARC) | built-in; section properties `mechanics section --shape dxf --dxf <file>` |
| **STEP / IGES** | **requires the `gmsh` package (not installed).** Export STL from Discovery/SpaceClaim or `pip install gmsh` |

```bash
python -m aerokit mechanics section --shape dxf --dxf src/aerokit/data/examples/cad/profile_L.dxf
```

**Discovery/SpaceClaim → STL workflow (gmsh will not be installed; decision of 2026-10-25).** The menu names and Discovery's STL unit behaviour are general knowledge; Discovery was not opened in this session and they were **not verified**. On the first export, check against the dimensions in the read report.
1. In Discovery select the body → File > Save As (or Export) → **STL**. Choose binary; ASCII is also read.
2. Note the unit (an STL file carries no unit). In the CLI `--unit mm` (default). If the dimensions are 1000 times larger/smaller than expected, the unit is wrong.
3. Surface resolution (tessellation/deviation tolerance): on curved surfaces an angular deviation of ~5–10° is sufficient. Very fine tolerances make the file larger and do not speed up the FEM mesh.
4. Provide each body as a separate STL. If bodies in contact in an assembly are merged into one STL, the report says "body count > 1" and separate files are needed for FEM.
5. If the report says "not watertight": close it in Discovery with Repair > Gaps/Missing Faces and export again.

**Geometry report (`geometry cad`):**
- topology: watertightness, manifoldness, orientation; repair suggestion;
- volume, area, mass, centre of gravity, principal inertias;
- bounding boxes, slenderness;
- frontal areas (x/y/z);
- for wing-like bodies, chord and t/c along the span.

Interpretations are labelled "(heuristic)" and state their thresholds. `--fem` fixes the min face of the selected axis (`--axis`), applies a load (`--load`, `--load-direction`) to the max face and reports the largest displacement, the von Mises value and the safety against yield. This is a preliminary design mesh: stress peaks depend on the mesh, reduce `--h` and look at the convergence. Example wing (`wing_naca2412.stl`, 6061-T6, 500 N): 14.1 mm, 20.5 MPa, 38 820 degrees of freedom, 65.5 s [K, the `geometry cad` command in §2].

**Known limits:**
- the oriented box is relative to the inertia axes;
- for cambered airfoils t/c comes out slightly large (median t/c 0.122 on the example wing [K]);
- ELLIPSE and blocks are not supported in DXF;
- no buckling for 3D solid elements.

## 7. Optimisation (`aerokit.optimization`)

| Module | Contents | Verification |
|---|---|---|
| `sizing` | Truss/frame section optimisation: mass, compliance, stress, displacement, Euler, frequency and system buckling constraints. **Analytical sensitivities** (direct + adjoint). FSD, OC, SLSQP; KKT check | 3-bar 263.8958; 10-bar case 1 **5060.85 lb**, case 2 4676.92 lb; 25-bar **545.16 lb**. All the same as the literature (arXiv:1306.1454 tables, [A]). Sensitivities within 2.8e-7 of finite differences. The 10-bar optimum was also run separately in an earlier session: 5060.8537 lb [D] |
| `topology` | SIMP (top88): sensitivity/density/Heaviside filter, OC and MMA, passive elements, multiple loads, MBB/cantilever/L-bracket, small 3D | MBB 60×20: ft 1 **216.81**, ft 2 **233.71**, ft 3 **189.14**. Identical to Andreassen et al. 2011 Figures 3 and 8 [A]; ft 1 was re-run in this session: 216.814, 106 iterations [K]. KE within 1.7e-16 of `aerokit.fem` Q4. MMA matches the log of Svanberg's beam example to 4 digits |
| `design` | Constraint diagram optimum (with KKT check). Raymer carpet and SLSQP (AR, W/S, P/W). **Minimum-mass wing box**: regional skin/web thickness, stringer/rib spacing; yield, ultimate, panel/stringer/web buckling. Tube sizing. Sweep (grid/LHS), Pareto, flexibility. **Reliability**: Monte Carlo P_f (Wilson interval), FORM (HL-RF) | In the governing mode MS ≈ 0 (\|MS\| < 1e-12), the others ≥ 0. FORM exact β in the linear/lognormal case. The design point is the same as `sizing raymer` (P/W 28.45; `sizing point` and `sizing raymer` in this session [K]) |
| `laminate` | Lamination parameters (V, W) and the feasible region. Layup optimisation: exhaustive search, genetic algorithm, permutation, continuous angle; objective buckling, stiffness, FPF, strain | Le Riche 1994 (Haftka group) thesis tables: 64 plies λ = 3973.01, 48 plies 9998.19 and the global optimum by exhaustive search over 3^12 [A]. Table 3.1 row 1 strength value differs by 3.2e-4, unexplained |

CLI:
```bash
python -m aerokit fem topology --problem mbb --nelx 60 --nely 20 --volume 0.5 --rmin 2.4 --ft 1 --plot outputs/topo
```
```bash
python -m aerokit fem optimum src/aerokit/data/examples/truss_bridge.json --tension 150 --disp-node 2 --disp-limit 0.01 --plot outputs/truss_opt
```
```bash
python -m aerokit sizing point
```
```bash
python -m aerokit sizing box --mass 5974 --n 3.14 --b 15.73 --c-root 2.33 --c-tip 1.17 --regions 6
```
```bash
python -m aerokit composite layup --material IM7-8552 --load 1 0.5 --objective buckling
```

## 8. Reference registry (`aerokit.references`)

- `@cite("key", note=...)` ties a function to a source: the key is checked at import time (a typo fails immediately), written into `obj.__references__`, and a `References` section is added to the docstring.
- The registry is split by topic (`_core`, `_aero`, `_structures`, `_composites`, `_fem`, `_fem_dynamics`, `_optimization`, `_cad`, `_materials`); `REFERENCES` merges them and rejects duplicate keys. 161 sources [K, `len(REFERENCES)`].
- `docs/references.md` is **generated** from this registry, not edited by hand. Its header says 161 sources · 531 citations · 7 uncited sources; `--check` said the file is up to date [K].

```bash
python scripts/build_references.py --check
```

## 9. Output layer (`aerokit.output`)

| Module | Contents |
|---|---|
| `tables` | `Table`: text, Markdown, CSV, JSON; numbers right-aligned, text left-aligned, no vertical rules, units in the header |
| `report` | `Report`: tables, notes, warnings, `Result:` and `Next step:`; text/Markdown/JSON. `format_from_path` selects the format from the extension |
| `console` | the commands' `table`, `note`, `warn`, `file`, `result` calls; inside `capture` they fill the report, outside they print directly |
| `writers` | atomic writes (temporary file + `os.replace`); path checks: NUL/control characters, device names, allowed extensions, optionally staying within a base directory (`../` and symlink escapes are blocked) |
| `figures` | `fem` (stress contour, deformed frame, truss areas), `aero` (V-n, span loads), `optimization` (topology map). `_common.save` writes PNG + PDF + CVD preview + `<name>.denetim.txt`; a figure is not used unless `report.errors` is 0 |

Figures pass the `datawiz` audit; 0 errors in this session's `sizing vn`, `fem solve`, `fem topology`, `fem optimum` runs [K]. All `outputs/` figures: `scripts/make_figures.py` (not run in this session).

## 10. Tests (`tests/`)

| Folder | What it checks |
|---|---|
| subpackage folders (`aero`, `structures`, `composites`, `materials`, `fem`, `optimization`, `cad`, `output`, `cli`) | numerical criteria; every `check` carries the expected value and its source (`aerokit.verification`) |
| `integration` | cross-verification: FEM ↔ independent hand-calculation modules |
| `security` | AST scan of the source (`eval`/`exec`, unsafe serialisation etc. forbidden); output path checks, atomic writes |
| `cad/test_reader_security.py` | a corrupt/malicious CAD file always gives `ValueError`; a size in the header cannot make it allocate more memory than the file |
| `typing` | `mypy` 0 errors package-wide, `--strict` on core modules; type annotations on the public API; `py.typed` |
| `robustness` | property-based tests with hypothesis: physical invariants, input validation, serialisation |

```bash
python -m pytest -q
```
```bash
python -m pytest -q -m "not slow"
```
```bash
python -m pytest -q tests/structures
```

**Full run of 2026-10-25** [K, `python -m pytest -q`]: 690 passed, 2 failed, 1 skipped (no symlink permission), 364 s; **numerical checks 2523/2523**. The two failing tests were from hypothesis (`test_ro_inverse_and_tangent`: slow input generation health check; `test_table_renders_any_text`: an extra line when the header is `"\n"`). Both passed when re-run on their own. `-m "not slow"` run: 690 passed, 1 skipped, 2 deselected, 2523/2523 checks, 417 s, exit code 0 [K]. `tests/structures`: 64 tests, 564/564 checks [K].

## 11. Unverified or assumed items (summary)

- Raymer 6th edition table numbers (sources are 4th/5th edition). The GA group weights (`aero.weight`) are not from the book but from two independent reimplementations [A].
- For the composite, Hexcel has no ν12, G12, Yc (assumption; `unverified` in the `library.MATERIALS` record). The Puck GFRP parameters are partially verified.
- The aluminium values in the catalogue are AA "typical", not design (A/B-basis). For design values use `materials allowable` / `handbook.get_allowable`.
- The shear buckling formula 5.35 + 4(b/a)² is approximate; FEM gives 6.71 at a/b = 2, the formula 6.35.
- The gmsh STEP path was never run.
- The ASTM E1049 standard is paywalled; the rainflow example counts are from a secondary source + traced by hand.
- `geometry airfoil --file-format dm` (DesignModeler format) is "not verified" in the help text.

## Conceptual design and mission planning (added 2026-10-25)

See `docs/06_development_plan.md` §6 for the verified numbers. Inputs are JSON files with units
(`src/aerokit/data/examples/design/ansys_2023_requirements.json`, `ansys_2023_mission.json`); unknown keys
and wrong units are rejected.

```bash
python -m aerokit sizing design src/aerokit/data/examples/design/ansys_2023_requirements.json --drag buildup --out-dir design_report
```

```bash
python -m aerokit sizing mission src/aerokit/data/examples/design/ansys_2023_mission.json --requirements src/aerokit/data/examples/design/ansys_2023_requirements.json --out-dir mission_plan
```

`--optimize` first searches altitude × search speed × overlap for the largest covered area (then the least
fuel) and plans the best point; it prints the best 5 candidates and warns if the best altitude is the top of
the grid while no sensor limit is set. A mission file may give the area as a polygon and a constant wind
(`ansys_2023_mission_polygon_wind.json`):

```json
{"area_polygon": [[39.10, 34.40], [39.30, 34.85], [38.95, 35.05], [38.75, 34.60]],
 "wind_speed": "40 km/h", "wind_from": "90 deg", "max_search_altitude": "2500 m"}
```

```bash
python -m aerokit sizing mission src/aerokit/data/examples/design/ansys_2023_mission_polygon_wind.json --requirements src/aerokit/data/examples/design/ansys_2023_requirements.json --optimize --out-dir mission_plan
```


## Radio links (`aerokit.comms`, copied from Sidera on 2026-10-25)

The link-budget stack of Sidera (the author's own package, `D:\sidera`, commit `02029b76`) was copied with only
the import paths changed; `src/aerokit/comms/SOURCES.md` lists every file with its source module and sha256.
Sidera's own tests for these modules came along (`tests/comms/`, 159 tests) and give the same 159 passes in
Sidera's environment and here.

| Module | What it gives |
|---|---|
| `rf` | dB conversions, free-space path loss, noise power, C/N0, Eb/N0, polarisation and Gaussian-beam losses |
| `antennas` | fixed gain, parabolic dish (gain ↔ diameter, beamwidth), Gaussian beam, tapered aperture, tabulated, ITU-R S.465 |
| `terminals` | transmitter (EIRP, feeder loss), receiver (G/T at a stated reference plane) |
| `geometry` | link geometry from two states: range, range rate, Doppler, light time |
| `channel`, `itu_earth`, `refraction` | free space, fixed allowance, ITU-R P.618/P.676/P.838/P.840/P.453 Earth–space rain, gas, cloud, scintillation; refraction-limited elevation |
| `budget` | one-way link: EIRP → losses → C/N0 → Eb/N0 → margin, with the atmospheric double-counting guard |
| `digital`, `modcod` | uncoded BER (AWGN), Shannon bound, fixed-rate links, DVB-S2 MODCOD table and ACM |
| `dsn`, `dsn_atmosphere` | DSN 810-005 pointing loss, sky noise, zenith attenuation |
| `data_volume` | `∫ R_b dt` of a sampled rate history (three explicit rules) |

Limits: `itu_earth` is the **Earth–space slant-path** set (P.618); a terrestrial or air–ground path (helicopter
to command centre) has no P.530/P.526 terrain diffraction here, and the rain height is a latitude fallback, not
the P.839 map. Satellite visibility (orbits, Earth rotation, access windows) and multi-hop relay networks were
**not** copied: in Sidera they depend on its body catalogue, IERS Earth orientation and ephemeris layers.

```python
from aerokit.comms import (CommunicationLink, CommunicationTerminal, FixedGainAntenna, FreeSpaceOnly, Receiver,
                           Transmitter, evaluate_link, geometry_from_states)
```

## Orbits and satellite visibility (`aerokit.orbits`, 2026-10-25)

`kepler_j2`, `two_body` and `gmst` (GMST82) are copied from Sidera (`src/aerokit/orbits/SOURCES.md`);
`constellations` and `visibility` are aerokit code on top, and `aerokit.comms.chain` chains link budgets.

- **Propagation:** mean elements, Kepler's equation, first-order J2 secular rates; Earth-fixed position by
  `R3(GMST82)` with UT1 = UTC. No precession/nutation/polar motion, no lunisolar perturbations, no short-period J2:
  for visibility statistics, not navigation.
- **Nominal constellations:** `gps_baseline_24()` (GPS SPS PS 2008 Table 3.2-1, epoch 1993-07-01),
  `galileo_nominal_24()` (EUSPA GSC Walker 24/3/1, epoch 2016-11-21), plus `geostationary`, `circular`, `walker`.
  GPS and Galileo satellites carry the Cospas-Sarsat MEOSAR repeaters (21 and 23 in use in May 2024).
- **Visibility:** `look_angles`, `count_in_view`, `access_windows` (bisected edges), `common_view` (one satellite
  above both masks: the bent-pipe relay condition), `link_geometry` (feeds `evaluate_link`).
- **Chains:** `evaluate_chain(hops, "transparent" | "regenerative", bit_rate_bps=…, required_ebn0_db=…)`.

Checks [K]: the GPS slots propagated to their ascending nodes land on the table's ground-track crossings within
0.0063° (worst of the 24 slots, mod 180°; the table rounds to 0.01°, test tolerance 0.02°); GMST82 at the table epoch differs from the printed
18h36m14.4s by 1.1 s; the J2-only node regression is −0.0388°/day against the published −0.04187°/day (lunisolar
terms not modelled, judgement). Everest (27.99°N, 86.93°E, 8 km, 10° mask) on 5 Nov 2026: 5–9 GPS and 5–9 Galileo
satellites in view; MEOSAR common view with Kathmandu (5° mask) 100 % of the day, at least 11 satellites.

```python
from aerokit.orbits import constellations as C, visibility as V
site = V.GroundSite("Everest", 27.9881, 86.9250, 8000.0, mask_deg=10.0)
n = V.count_in_view(C.gps_baseline_24(), site, V.time_grid(t0, t1, 300.0))
```

## Electric aircraft, reliability and operations (2026-10-25)

For the challenge families of `09_2026_playbook.md` §2 (F2, F4, F5). All aerokit code; sources in `docs/references.md`.

| Module | Contents | Checked against [K] |
|---|---|---|
| `aerokit.design.electric` | battery range and sizing (Hepperle 2012 form, derived), zero-payload range limit, endurance, momentum-theory hover power, multirotor sizing (concave root, Brent) | closed forms; R = 0 minimum mass; T^1.5 and 1/√A scaling; infeasible hover refused |
| `aerokit.reliability` | Weibull (NIST §8.1.6.2), right-censored MLE (§8.4.1.2), series/parallel/k-of-n, RUL by linear/exponential trend + residual bootstrap, synthetic degradation | scipy `weibull_min.fit` to 1e-4; censored fit within 5 % on n = 4000; exact RUL for noiseless data; interval coverage 85 % at nominal 90 % |
| `aerokit.operations` | M/M/1, M/D/1, M/G/1 (Pollaczek–Khinchine), M/M/c (Erlang C), runway capacity, deterministic peak-hour queue, ICAO CEC per-passenger CO₂ | M/M/c(c = 1) = M/M/1; Erlang C 4/9 by hand; peak queue by hand; conservation of movements |

The CO₂ index 3.16 kg/kg is now read from its sources (ICAO CEC methodology v8; UK CORSIA Order 2021 art. 28(5)).
