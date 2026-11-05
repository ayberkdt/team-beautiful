# 22 · Ansys challenge — aircraft bracket redesign: our toolchain (4 Nov 2026, consolidated 23:10–23:55)

Task (handwritten notes, `research_notes/final_2026_notes/01_Ansys_Bracket_Redesign.md`, not the official text):
redesign the material and shape of an aircraft (mounting) bracket to cut mass and/or extend life, assess CO₂-eq over
the whole life; bare minimum = CAD of the initial design, material selection report + comparison table ("3"),
Eco Audit of the initial design, material card files; working temperature **300 °C**; 3-D printability; baseline
**structural steel**. The user decided not to install or use Ansys on this laptop: the code below reproduces what
Ansys Mechanical / Discovery / Granta EduPack would give so that at the event we can say "Ansys agrees" or "there is
a discrepancy, here is why".

Tags: **[D]** read from the primary source in this session, **[D-ag]** read from the primary source by a research
sub-agent (URL given), **[S]** secondary, **[K]** computed here (command given), **[Y]** our assumption.

## Friday morning checklist

1. Shell: `cd "D:\Masaustu\Ideathon 2026"`, set `PYTHONPATH=src;D:/tmp_ideathon/pylib`, `TEMP`/`TMP` = `D:/tmp_ideathon/ansys`.
2. Smoke test (seconds): `python -m pytest tests/test_bracket_matlist.py tests/test_bracket_handcheck.py -q -p no:cacheprovider`.
3. Save the organisers' CAD as `studies/final_2026/ansys/inputs/day1.step` and their materials as `day1_materials.csv`.
4. First run: `python scripts/bracket_day.py …/day1.step --materials …/day1_materials.csv --case day1 --handoff` (§1 for options); ≈ 17 min at the default size (dry run §7), `--quick` for a first look.
5. Read the printed body table, hole scan and material matches; a `RESULT: STOPPED` names exactly what to fix.
6. Edit `out/day1/setup.json` (hole roles, loads in N / N m, temperature, criterion) and run the same command again.
7. Read `out/day1/report.md` top to bottom: choice, T10 verification, life screening, bolt loads, Mechanical checklist.
8. Give `out/day1/crosscheck_template.csv` + the report §6 checklist to whoever runs Ansys.
9. Ansys numbers back → `python scripts/bracket_crosscheck.py studies/final_2026/ansys/out/day1` → verdict line.
10. Tell the film session the case name; never write fake or test data into `handoff/` (§6c).

## Where we stand (numbers from the run folders, 4 Nov evening)

* Rehearsals (§8): **sketch** → Ti-6Al-4V L-PBF, topology 25 %, **0.1196 kg vs 0.8515 kg steel (86.0 % lighter)**,
  T10-verified 264.5 MPa, utilisation 0.528 at 300 °C; life screening margin 0.67 as-built, 2.29 machined (§5b).
  **ge** (GE-type envelope with GE loads) → nothing passes at 300 °C (best: Inconel 718 initial, utilisation 1.10,
  sharp re-entrant edges). **ge_step** (same part from STEP, automatic holes, `--quick`) → Ti-6Al-4V 40 %, 0.4430 kg
  vs 1.9964 kg (77.8 % lighter). **dryrun_cold** (new STEP + misspelled material CSV, one cold command, 16 min 45 s, no manual step) →
  Ti-6Al-4V 25 %, 0.0803 kg vs 0.5771 kg (86.1 % lighter), T10 utilisation 0.775 (§7).
* Validated (§4): patch test exact; cantilever H8IM 0.986–0.990, T10 0.991–0.992; plate-with-hole Kt T10 +2.4 to
  +3.7 %; topology = repository top88-family code to 0.006 %; AM filter adjoint 7e-10; STEP round trip ≤ 0.24 %.
* Checks around the FEA: bolt loads vs Bruhn (§6b), life screening at temperature (§5b), Ansys cross-check with a
  verdict line, rehearsed on 3 cases with 3 planted errors + 1 clean control each: 12/12 verdicts right (§6c).
* Not used by the pipeline: the 3-D stress-constrained topology (`stress3d`, §4c) — 0/1 designs with projection, but
  the black-and-white voxel designs overshoot σ̄ by 42–83 % (projected), so it stays EXPERIMENTAL.
* Tests: full suite 1960 passed, 1 skipped (23:30, after the last code change); `mypy` clean on `src/aerokit/bracket`.

## 1. One command on the day

```bash
python scripts/bracket_day.py <organisers.step|.stl|drawing.json> --materials <list.csv> --case day1 --handoff
```

What happens, in order (each stage prints a time-stamped line; the last line is `RESULT: … NEXT: …`):

1. **Geometry.** STEP/IGES: bodies listed and fused into one solid (`out/<case>/cad/<name>_solid.step`; overlaps
   such as inserted bolts counted once). Disconnected solids → the run stops with the body table: choose with
   `--bodies largest` or `--bodies 1,3`. Rotated part: `--align pca` or `--rotate rx,ry,rz` (stored as `_frame`).
2. **Materials.** `--materials` (CSV column `material`/`name`, YAML, or one name per line) is matched to the 300 °C
   pool: exact designation → `alias`, typo → `close` (difflib ≥ 0.85 and 0.10 clear of the next alloy), otherwise
   the run **stops** (`RESULT: STOPPED`, exit 2, `out/<case>/materials_match.md`). A contradicting route word
   ("Ti-6Al-4V wrought") is matched and flagged `ROUTE DIFFERS`. Without `--materials`: all five pool materials.
3. **Holes and set-up.** STL/STEP bores are scanned at half the voxel size (a bore under 3 voxels would otherwise be
   lost: Ø4/Ø6 mm at 2 mm voxels before the fix); the voxel is refined until the smallest bore has 2.5 voxels of
   radius. First run: roles proposed (`roles_source` "auto") → **edit `setup.json`** and re-run ("edited").
   No loads given? `--calibrate 0.8` scales the proposed loads to baseline utilisation 0.8 [Y].
4. **FEA, convergence, topology, materials, T10 verification, eco audit, figures, film hand-off** (§2).

Other modes: `--report-only` rebuilds the documents from `out/<case>/study.pkl` (writes to `--out/--case`);
`--evaluate-only --setup …` evaluates a given shape (e.g. the team's Ansys topology STL: rehearsed on our 25 %
layout, 0.1217 kg vs 0.1196 kg, T10 262 → 267 MPa vs 264.5 MPa [K]); `--quick` for a fast look.
Material selection report alone: `python scripts/bracket_material_report.py`. Validation table:
`python scripts/bracket_validate.py [--slow]`. Ansys numbers back: `python scripts/bracket_crosscheck.py <out/case>
[--export mechanical_export.txt]` → verdict `AGREES`, `AGREES within tolerance, BUT <signature>` or
`DISCREPANCY: … most likely cause — …` (§6, §6c).

Environment (doc 21 §1): run with `PYTHONPATH="src;D:/tmp_ideathon/pylib"` and TEMP on D:. Packages installed **only**
into `D:\tmp_ideathon\pylib` (decided from need, all well-known PyPI): **gmsh 4.15.2** (STEP/IGES import, exact CAD
export, 10-node tet meshing; its DLL extracted by hand from the wheel because `pip --target` skips wheel data),
**pyamg 5.4.1** (AMG-PCG fallback solver), **pypardiso 0.4.7 + mkl 2026.2.0 + intel-openmp 2026.2.0** (MKL PARDISO
direct solver; DLLs in `pylib\mkl_bin`, located through `AEROKIT_MKL_BIN` or that default). Without them everything
still runs (SuperLU / Jacobi-CG, no STEP, no T10 check), only slower.

Known trap (found and fixed 4 Nov ~18:50): after `aerokit.cad.readers.read(<file>.step)` (which switches OpenCASCADE to
metres) a later gmsh 3-D mesh in the same process hangs. The bracket code reads STEP with its own reader in mm
(`cadout.read_step_surface`); all bracket gmsh calls also start from `restoreDefaults()` with one thread. The gmsh
tests run in a subprocess with a timeout so a hang can never stall the suite again.

## 2. What exists (`src/aerokit/bracket/`)

| Module | Does | Validation (scripts/bracket_validate.py, tests/test_bracket_*.py) |
|---|---|---|
| `geometry` | parametric CSG drawing JSON (box, cylinder, prism with arcs, sphere; add/cut in order); voxelisation with **partial volume** (3×3×3 samples per voxel for drawings, 2×2×2 half-voxels for surfaces, solid if > ½) | sketch bracket volume vs exact B-rep: −1.9 / −0.7 / −0.2 % at 2.55 / 1.70 / 1.28 mm [K] |
| `cadout` | drawing → exact STEP + STL (gmsh/OCC); density field → smooth STL (VTK flying edges + Taubin) | drawing → STEP → gmsh surface → voxels: +0.00 % (2 mm), +0.24 % (1 mm) (`validation/validation.md`) [K] |
| `features` | through/blind hole detection (slice-wise enclosed voids, roundness, collinear merge = clevis), role proposal, editable set-up JSON, loads: bearing (cosine on loaded half, ≈ Ansys Bearing Load), force (uniform), moment (rigid distribution), supports: fixed bore / bolt seat; non-design rings | GE clevis found as one hole with 2 segments; resultants and moment exact to 1e-9 N [K] (tests) |
| `voxfem` | 3-D linear static on voxels, H8 and **H8 incompatible modes** (Taylor-Beresford-Wilson), nodal-averaged stress (Ansys convention), PARDISO / SuperLU / AMG-PCG | patch test 3e-14; cantilever H8IM 0.986 (1 voxel thick) … 0.990, H8 locks 0.643 → 0.957 [K] |
| `tetfem` | **conforming 10-node tets** (gmsh mesh of the exact CAD or of an optimised STL) — the Ansys SOLID187 analogue | cantilever 0.991 / 0.992 of Timoshenko; plate-with-hole Kt see §4 [K] |
| `topo3d` | SIMP compliance, several load cases (weights 1/c₀), density filter, tanh projection with β continuation, OC, keep/void regions, **3-D Langelaar AM overhang filter**, warm start across volume fractions | equals repo `topology.topopt` (top88 family) to 0.006 % after 30 it.; AM adjoint error 7e-10 [K] |
| `matdata` | 5 candidates with E, Fty, Ftu vs temperature (20 → 300 °C), sources per value | see §3 |
| `cards` | Ansys Engineering Data **MatML XML** (Workbench 23.1 layout, E(T) table) + Markdown card per material; parser for real exports | round trip + parses a real Workbench 23.1 export [K] |
| `ecoaudit` | Granta-EduPack-structured eco audit (material, manufacture, transport, use, EoL potential) with every factor tagged | hand calculations in tests |
| `crosscheck` | Ansys-vs-ours table with tolerances and discrepancy signatures; reads Mechanical "Export Text File" | tests with synthetic cases |
| `stress3d` | 3-D stress-constrained topology: minimum mass s.t. Holmberg's stress-level clustered P-norms (p = 8, q = ½), optional tanh projection with β continuation (β-scaled move limit, trust-region fallback), threshold re-analysis — §4c | gradient = finite differences with and without projection (2 load cases); L-beam vs Holmberg 2013 §4c |
| `matlist` | organisers' material list → pool keys with a decision table; stops on unknown/ambiguous names | `tests/test_bracket_matlist.py` (16 tests) |
| `lifecheck` | fatigue screening at T: Se,ref(R = −1) × k_surface (as-built AM) × k_T against Goodman/SWT of the 0 → σ limit-load cycle | `tests/test_bracket_lifecheck.py` |
| `handcheck` | FEA reaction per support bolt (Σ nodal reactions on the bore, plus its clamp moment) next to the classical rigid-plate bolt-group split (Bruhn, via `structures.joints.bolt_group`; linear axial split of out-of-plane moments) — §6b | `tests/test_bracket_handcheck.py`: force and moment equilibrium closed to 1e-6; hand numbers 250 / 225 / 675 / 79.1 N; FEA shear and torsion within 10 % of the classical split; bolt-seat reactions sum to the applied load [K] |
| `pipeline`, `report`, `figures`, `handoff` | one call → all files; datawiz-audited figures; film hand-off | `tests/test_bracket_pipeline.py` |

Pipeline steps (`pipeline.run_design`): voxelise (voxel size from the element target, refined so the smallest
support/load bore has a radius of at least 2.5 voxels, capped at 80 000 elements) → set-up (read or proposed) →
exact CAD volume (gmsh) used for every mass → baseline FEA at 20 °C and T → 3-level voxel convergence → topology at
each volume fraction (warm-started) → every material on every layout → choice → **conforming T10 check** of the
initial design (2 mesh sizes) and of the chosen layout → **verified selection**: if the chosen layout's T10 stress
exceeds its voxel stress, the ratio becomes that layout's stress factor (unmeasured layouts keep factor 1 and are
measured when they become the choice), all materials are re-ranked and the new choice is checked again (≤ 4 rounds)
→ eco audits → files. The chosen layout's STL is extracted at the contour level that matches the voxel layout's
volume (±1 %): a fixed 0.5 level kept only 62 % of a thin 25 % layout's volume, in 3 bodies, and made its T10 check
report 8× the voxel stress.

Material independence used by the pipeline: for a homogeneous isotropic part under prescribed loads the stress field
does not depend on E and displacements scale with 1/E (ν held at 0.3). Layouts are optimised once; every material is
then checked on every layout and the lightest **passing** (material, layout) pair is chosen.

Strength criterion [Y until the organisers give one]: set-up loads are limit loads; von Mises outside the hole
zones (bore radius + `exclusion_mm`, fixed in mm across meshes) ≤ Fty(T) at limit and ≤ Ftu(T) at 1.5 × limit
(CS 25.303 factor). GE rehearsal: factor 1.0 (GE challenge criterion "no yield", Carter et al. 2014 [D-ag]).

## 3. Materials at 300 °C

| Candidate | ρ (kg/m³) | E 20 → 300 °C (GPa) | Fty 20 → 300 °C (MPa) | Source of the 300 °C factor | Tmax (°C) | Route |
|---|---|---|---|---|---|---|
| Structural Steel (Ansys default) | 7850 [D] | 200 → 182.7 | 250 → 162.8 | Fty: EN 10028-2 P235GH Rp0.2 153/235 = 0.651 (Salzgitter reproduction) [D-ag]; E: MIL-HDBK-5J Fig. 2.3.1.1.4 low-alloy 0.913 [D curve, Y use] | 400 (EN 1993-1-2 k_y = 1 to 400 °C, fire design; source [D-ag], use as service limit [Y] — the strength uses the lower EN 10028-2 factor 0.651) | machined plate |
| 17-4PH H1025 | 7806 | 196.5 → 173.0 | 1000 → 816 | MIL-HDBK-5J Fig. 2.6.9.2.1 / 2.6.9.1.4 [D] | 316 [pool] | L-PBF + HIP + H1025 |
| Ti-6Al-4V L-PBF | 4410 | 110 → 96.8 | 945 → 590 | Fty: MIL Fig. 5.4.1.1.1 annealed wrought 0.624 [D]; E 0.88 from TIMET 6-4 Table 2 trend [D-ag] | 350 (EOS Ti64 ELI) [D-ag] | L-PBF + HIP |
| Inconel 718 L-PBF | 8150 | 200 → 184 | 1145 → 1096 | Special Metals bulletin Tables 4, 19 at 600 °F [D-ag] | 700 [pool] | L-PBF + STA |
| Scalmalloy L-PBF | 2670 | 69 → 29 | 490 → 60 | Colibrium M2 Al-Mg-Sc CMDS Rev B [D-ag] | 150 → **fails the 300 °C screen** | L-PBF |

Structural Steel room-temperature values (7850 kg/m³, 200 GPa, ν 0.3, Fty = Fcy 250 MPa, Ftu 460 MPa, CTE 1.2e-5 /°C,
k 60.5 W/m°C, cp 434 J/kg°C, S-N from ASME VIII-2 Table 5-110.1) were read from a real Workbench 23.1.0.209 Engineering
Data export (`pymaterials-manager/tests/data/steel_eglass_air.xml`, local copy read this session) [D]. Ansys gives no
temperature dependence for it: if the team keeps "Structural Steel" at 22 °C in Mechanical while we use 300 °C, the
cross-check flags "temperature" (deformation ratio 0.913).

Screening result (`python scripts/bracket_material_report.py` → `studies/final_2026/ansys/material_selection/`) [K]:
mass of a strength-limited bracket arm (Ashby index Fty^2/3/ρ) relative to the best at 300 °C — Ti-6Al-4V 1.00,
Inconel 718 1.22, 17-4PH 1.43, Structural Steel 4.20; Scalmalloy fails the 300 °C screen (it is the lightest at
20 °C). Least embodied CO₂ per unit strength (cradle to gate): 17-4PH. Prices found: steel plate 0.77 EUR/kg,
Ti-6Al-4V powder production cost 70.6 EUR/kg [D-ag]; 17-4PH, IN718 and Scalmalloy prices NOT FOUND.

Life screening (each run's report, §4; method and sources in §5b): limit-load cycles 0 → σ against the endurance
value corrected for 300 °C and for the as-built AM surface; endurance values exist for steel, Ti-6Al-4V, Inconel 718
(wrought, [Y] for AM) and Scalmalloy, none for 17-4PH. A screening, not a fatigue analysis.

CO₂ per kg (primary): steel 1.8 (Ashby via reproduction, low-carbon steel) [D-ag]; 17-4PH 5.0, Ti 46.5, IN718 11.6
(pool, Ashby family values) [D/S]; Scalmalloy 128 (pool) [S].

## 4. Validation table (python scripts/bracket_validate.py --slow → studies/final_2026/ansys/validation/validation.md)

Numbers below are copied from that file (run 4 Nov 19:36) [K]:

| Benchmark | Reference | Ours |
|---|---|---|
| patch test, uniform tension, H8 and H8IM | exact σz = 100 MPa | max error 3e-14 / 7e-14 |
| cantilever 100 × 10 × 10 mm, H8IM, 1 / 2 / 4 voxels thick | Timoshenko 2.0156 mm | 0.986 / 0.987 / 0.990 |
| same, plain H8 (shear locking) | same | 0.643 / 0.869 / 0.957 |
| same, T10 (gmsh), 5 / 2.5 mm | same | 0.991 / 0.992 |
| plate with hole, Kt_net, voxels 1.0 / 0.67 / 0.5 mm | Heywood 2.422 | −22 % / −20 % / −19 % |
| plate with hole, Kt_net, T10 2 / 1 mm | Heywood 2.422 | +3.7 % / +2.4 % |
| 3-D SIMP vs the repository's top88-family `topology.topopt` (24×8×4, 30 it.) | c = 160.3096 | −0.006 % |
| 3-D AM overhang filter adjoint | central differences | 7e-10 |
| MatML write → parse; parser on a real Workbench 23.1 export | written values; 7850 / 2e11 / 2.5e8 | all match |
| drawing → STEP → gmsh surface → voxels, 2 / 1 mm | exact B-rep 108 475 mm³ | +0.00 % / +0.24 % |
| Ferrari & Sigmund 2020 top3D125 cantilever (orientation) | c = 3993.7 | not reproduced: our c = 12.3 for a unit total load ≈ 7.7 × 10³ for a unit load per node; their load convention, penalty and continuation unconfirmed |

Reading: the voxel model is good for stiffness and layouts, biased low (≈ 20 %) for stress concentrations at
curved edges; the conforming T10 model is within 4 % of the classical Kt and is the one to compare with Ansys. That
is why the choice is verified with T10 (§2) and the cross-check template carries the T10 numbers.

Voxel vs T10 on the rehearsal parts (same set-up, 300 °C) [K]: sketch deformation 0.995 (voxel/T10), GE 1.21 at the
run's 2.2 mm voxels. The GE gap is resolution, not a model error: LC2 (8500 lbf) loaded-bore mean deformation
0.588 / 0.539 / 0.490 mm at 2.2 / 1.65 / 1.2 mm voxels vs T10 0.485 mm (2.86 mm tets); peak deformation 0.834 /
0.788 / 0.713 vs 0.688 mm — the 7.6 mm clevis arms are only 3.5 voxels thick at 2.2 mm. On the day: when a member is
thinner than ~5 voxels, trust the T10 numbers (the cross-check template already uses them) or rerun with `--voxel`. Peak stress outside the hole zones grows with refinement in
both models where the drawings have sharp re-entrant edges (sketch T10: 115 → 131 → 167 MPa at 5.1 / 3.4 / 2.2 mm;
GE T10: 884 → 1070 MPa at 4.4 / 2.9 mm): Ansys will show the same growth; compare at a probe or with fillets.

## 4b. Thermal load at 300 °C (sensitivity, not in the strength criterion)

`voxfem.static(..., thermal_strain=α ΔT)` adds the uniform-temperature load (incompatible modes condensed) and
returns σ = D(ε − ε_th). Checks [K] (tests/test_bracket_fea.py): free expansion → zero stress and exactly α ΔT L
elongation; a bar clamped at both ends → σx = −E α ΔT within 2.4 % (H8) / 2.1 % (H8IM). Each run reports the
**constrained expansion of the baseline** with the bores fixed at ΔT = T − 22 °C (the Engineering Data reference):
≈ 1200 MPa von Mises on all three rehearsal parts (E α ΔT = 609 MPa for Structural Steel, α 1.2e-5 /K) — far above
any strength. Our strength check assumes the mounts expand with the bracket [Y]; if the team's Mechanical model has a
Thermal Condition of 300 °C with fixed supports, its stresses will be dominated by this, and the cross-check flags
"thermal". Mentor question 1 decides which is right.

## 4c. 3-D stress-constrained topology (`aerokit.bracket.stress3d`) — EXPERIMENTAL, not in the pipeline

Formulation: Holmberg, Torstenfelt & Klarbring 2013 (P1), the same as the validated 2-D `optimization.stress_topo`
— minimum mass s.t. stress-level clustered P-norms (10 clusters per load case, re-clustered every iteration,
p = 8, relaxation x̄^½), density filter r = 1.5 voxels, MMA (repository `mma_multi`), one adjoint solve with all
cluster right-hand sides; new: tanh projection with β continuation 1 → 16 (β-scaled move limit, trust-region
fallback to the last near-feasible design), optional adaptive normalisation (Le et al. 2010 via Holmberg), threshold
re-analysis (x̄ > 0.5 solid, true von Mises / σ̄) and `optimize_stress_verified` (σ̄_eff lowered by the measured
overshoot, warm-started rounds). Gradient = finite differences with and without projection, 2 load cases
(`tests/test_bracket_stress3d.py`). Runs: `python scripts/bracket_stress_topo_validate.py …`, raw lines in
`studies/final_2026/ansys/validation/stress_topo_runs.jsonl` (cantilever) and `D:/tmp_ideathon/ansys/s3/*.log`
(L-beam runs started from a scratch copy with the same calls).

Promotion criteria, fixed before the results: (1) the L-beam without projection reproduces Holmberg's published
mass and compliance within 5 %; (2) the 100-iteration cantilever ends mostly 0/1 (grey < 10 %) **and** its
black-and-white design is within 2 % of σ̄; (3) the same for the projected L-beam.

**Holmberg L-beam, 3-D slab one voxel thick** (n = 100, h = 2 mm, 1000 MMA iterations, force scaled to the slab
thickness; mass for the published 1 mm beam with ρ = 2.8e-9 t/mm³) [K vs D]:

| Quantity | Holmberg 2013 Table 1 [D] | 2-D `stress_topo` (doc 16 §6.1) [K] | 3-D `stress3d`, no projection [K] |
|---|---|---|---|
| Mass | 24.76 g | 24.84 g (+0.3 %) | 23.47 g (**−5.2 %**) |
| Compliance | 10 330 N·mm | 10 216 N·mm (−1.1 %) | 9 931 N·mm (−3.9 %) |
| Worst cluster P-norm | ≤ 1 | 1.0005 | 1.0009 |
| Max relaxed σ_vM/σ̄ (single point) | — | 1.34 | 1.30 |
| Grey | — | — | 15.5 % |

Criterion (1): compliance inside 5 %, mass 0.2 points outside. The one-voxel slab is not a plane-stress Q4 model
(H8IM, σ_z free but present, 3-D von Mises), so a few per cent are expected; the 2-D code with the same formulation
is within 0.3 %. 

With projection (β 1 → 16 from iteration 333, doubled every 83; β-scaled move limit): 21.77 g (−12 %),
10 103 N·mm (−2.2 %), worst cluster P-norm 1.0008, grey **2.5 %** (plain 15.5 %). Threshold re-analysis (x̄ > 0.5
solid, true von Mises, design elements): plain 1.54 × σ̄, projected **1.42 × σ̄** — the same staircase-corner
overshoot as on the cantilever. The first projected attempt (fixed move 0.1) collapsed at the switch to β = 8
(mass 0.32 → 0.009, P-norm 1.5e6 within 25 iterations); the β-scaled move limit and the trust-region fallback fixed
that (second run stable to β = 16). Criterion (3) fails on stress.

**3-D cantilever** (40 × 12 × 6 voxels of 1 mm, 500 N, σ̄ 250 MPa, 100 iterations) [K]:

| Run | Mass fraction | Grey (%) | Worst cluster P-norm | Max relaxed σ/σ̄ | Thresholded true σ/σ̄ |
|---|---|---|---|---|---|
| plain (no projection) | 0.393 | 76.8 | 1.017 | 1.17 | 2.47 |
| plain + adaptive normalisation | 0.416 | 60.8 | 0.80 (normalised) | 1.015 | 1.63 |
| projection, β → 16 | 0.213 | **9.5** | 1.022 | 1.59 | 1.83 |
| projection + adaptive | 0.393 | 9.2 | 3.29 | 5.6 | 18 (diverged at a β step) |
| verified rounds (projection, σ̄_eff ← σ̄_eff / overshoot) | 0.213 → 0.383 → 0.462 → 0.520 | 9.5 → 12.0 → 10.8 → 9.7 | | | 1.83 → 1.11 → 1.10 → 26.6 |

What this shows: projection does what it should for the topology (grey 77 % → 9.5 % in 100 iterations: criterion
(2), first half, met). The stress control of the black-and-white **voxel** design is not reliable: the 10-cluster
mean P-norm lets the maximum overshoot (bound N^{1/p} ≈ 2 for ~280 points per cluster, Holmberg p. 6), and lowering
σ̄ does not remove the overshoot (1.11 → 1.10 while mass rises 0.38 → 0.46) because the peak sits at staircase
re-entrant corners of the thresholded voxels, which are singular and mesh dependent; the last round broke down.
Criterion (2) fails → **EXPERIMENTAL**. The pipeline keeps the method that is verified: compliance layouts at several
volume fractions, every material on every layout, and the choice re-checked with T10 tets on the volume-matched
smooth STL (stress factor per layout). What would make the 3-D stress TO usable: verify on the smoothed STL with T10
inside the rounds (not on voxels), more clusters or the adaptive factor without β steps, and a stress-free band at
re-entrant voxel corners — not attempted tonight.

## 5. Eco audit (Granta EduPack structure)

Phases and default factors (`ecoaudit.EcoInputs`): material = bought mass (part × buy-to-fly 8 machined / 1.3 AM [Y])
× primary CO₂ and energy; manufacture: L-PBF 31 kWh/kg (Baumers 2010, SLM250 316L) [D-ag] + atomisation 20 MJ/kg
(Kellens 2017 Table 2 range 7–32) [D-ag], machining = rolling 4 MJ/kg & 0.2 kg/kg (Ashby p. 133) [D] + 5 MJ/kg removed
[Y]; electricity 0.30 kg CO₂/kWh [Y, NOT VERIFIED]; transport 1000 km 32 t truck 0.94 MJ/t·km × 0.072 kg/MJ [S,
EduPack 2021 R1 help snippet]; use (EduPack mobile form) m × 6.0e7 km × 6.5 MJ/t·km × 0.072 [S + Y life], marginal
alternative Kellens 2017 Table 8 (12.5 t kerosene per 100 kg per year, short haul, 25 y) × 3.16 kg/kg (ICAO) [D-ag];
EoL potential = −m × 0.9 × (primary − recycled). On the day: type the same masses into EduPack and compare; EduPack's
"% removed" booking was not verified (research note `edupack_eco_audit_factors.md` Q3).

## 5b. Life screening at the working temperature (report §4, `aerokit.bracket.lifecheck`)

Se(T) = Se,ref(R = −1) × k_surface × k_T against σar = max(Goodman with Ftu(T), SWT) of the limit-load cycle 0 → σ;
σ = FE von Mises at limit load (contains Kt; notch sensitivity q = 1, conservative [Y]). Margin > 1: below the
endurance value at the reference cycle count. A screening, not a fatigue analysis.

| Material | Se,ref (MPa, R = −1) | k_surface (as-built AM) | k_T at 300 °C | Sources |
|---|---|---|---|---|
| Structural Steel | 86.2 at 1e6 (Ansys XML, ASME curve) [D] | 1 (machined plate) [Y] | 0.977 Marin kd (Budynas Sec. 6-9, steels) [D] | |
| Ti-6Al-4V L-PBF | 600 at 1e7, milled + HIP [S] | 0.29 = 175/600, HIP as-built / HIP + milled, same study [S, ratio Y] | 0.712 = Ftu(T)/Ftu(20) [Y] | Greitemeier via Afroz 2022 Table 3 |
| Scalmalloy | 87 σa at R = 0.1 → 109 at R = −1 (Goodman) [D, conversion Y] | 0.47 = 41/87 as-built / turned [D, ratio Y] | Ftu ratio [Y] | Musekamp 2021 Fig. 8 |
| Inconel 718 | 298 at 1e7, wrought STA [Y] | 0.42 borrowed from Ti-6Al-4V [Y] | 0.927 Ftu ratio [Y] | MIL-HDBK-5J equation |
| 17-4PH | none found | — | — | reported as "no data" |

What it says on the rehearsals (report tables, 21:40 regeneration): sketch chosen Ti-6Al-4V 25 % (T10 264.5 MPa)
margin **0.67 as-built**, 2.29 machined; Inconel 718 on the same layout 0.62 / 1.48; the steel baseline 0.91 (the
ASME curve includes design margins). ge_step Ti-6Al-4V 40 %: 1.30 as-built. So for the sketch layout the static
choice stands but **the surface finish decides life**: machine or polish the high-stress members, or take the 35 %
layout — a point for the presentation and a mentor question (load spectrum, required life).

## 6. Ansys cross-check

`crosscheck_template.csv` (initial design, baseline material) and `crosscheck_template_redesign.csv`: columns metric,
unit, ours, ansys, description. Tolerances [Y]: mass/volume 2 %, deformation and compliance 10 %, von Mises outside
the zones 15 %, peak von Mises anywhere 25 % (singular), safety factor 15 %, retained volume 5 %, reactions 1 %.
Signatures checked for any ratio: unit factors (1000, 1e6, 1e9, 25.4, 4.448), density of another candidate, E(T)
ratio (temperature not applied), E of another candidate, limit vs ultimate (1.5), strain energy vs compliance (½),
singular peak, discretisation band (0.85–0.97), BC change (< 0.7 or > 1.4), topology volume definition.

## 6b. Hand check of the bolt loads (report §4, "Bolt loads: FEA vs classical bolt group")

When all supports are bores on one axis, every report lists per load case and bolt: the FEA reaction (shear and
axial, from K u − f on the fixed bore DOFs), the classical rigid-plate split (in-plane force and torsion: elastic
fastener-group method of Bruhn through `aerokit.structures.joints.bolt_group`; out-of-plane moments: linear axial
split F_i = F_w/n + a v_i + b u_i [derived here]) and the clamp moment the fixed bore carries. Test plate
(80 × 40 × 6 mm, four M8-size bores, lug 27 mm above the bolt plane) [K]: in-plane shear and torsion agree within
10 %, pull-off is exact by symmetry, but under the overturning moment the FEA axial load is 341 N against 225 N
classical, because a fixed bore is a rigid clamp (clamp moments close the equilibrium). Sketch rehearsal (thicker
plate): axial within 5 %, but FEA shear 940–960 N against 632–640 N classical in LC2 and 337 N against 0 in LC3 —
in-plane forces from plate bending that cancel between the bolts. GE rehearsal (LC1, 35.6 kN pull-off, both columns
sum to the applied load): heaviest bolt (H2) 20.1 kN FEA vs 28.4 kN classical, H3 / H5 2.6 / 1.9 kN vs 10.5 / 5.3 kN,
with 660–680 N m clamp moments on the H2 and H4 bores — on this part the support idealisation changes bolt loads by up to
4×, which is worth a mentor question (bolt modelling). A real bolt (pin + seat) carries less clamp moment
and less of those forces [Y]; size bolts with the larger value, and expect Ansys with Fixed Supports on the bores to
give the FEA column, not the classical one.

Support-type sensitivity [K] (20:45, scratch script on the cached studies, baseline material at 300 °C; the
reports use `fixed_bore`): with `bolt_seat` supports (all DOFs of the seat annulus 1.8 r fixed, bore free) the
sketch axial loads stay within 16 % of the fixed-bore ones (LC2 2.41–2.43 vs 2.08–2.15 kN), but the self-cancelling
shear grows (LC2 1.65–1.70 kN vs 0.94–0.96 kN, classical 0.64 kN); on GE LC1 the heaviest axial bolt load goes from
20.1 kN (H2) to 22.6 kN (H4), and the H2 in-plane shear from 2.9 to 18.7 kN with zero net in-plane load. A seat clamped in all directions is as stiff
laterally as a bonded bolt; neither support type is a friction joint, so shear numbers from either are an upper
bound on what the bolt shank sees [Y]. Before this check `handcheck` summed only bore nodes and missed the seat
reactions (found by this comparison, fixed, test `test_bolt_seat_reactions_are_collected_from_the_seat`).

## 6c. Rehearsal: "the Ansys result arrives" [K]

`python scripts/bracket_ansys_rehearsal.py studies/final_2026/ansys/out/<case>` fills the `ansys` column of a copy
of the template with our numbers × planted factors and runs the real `bracket_crosscheck.py` on each. Output only
in `studies/final_2026/ansys/rehearsal_crosscheck/<case>/<scenario>/`, never in `out/` or `handoff/` and never under
the real names (the film treats a filled `crosscheck_template*.csv` / `crosscheck.json` in a hand-off as a real
Ansys result): `REHEARSAL_fake_ansys_crosscheck_template.csv` (every description starts "FAKE ANSYS DATA"),
`REHEARSAL.json` (`"fake_ansys_data": true`), summary `REHEARSAL_summary.md`:

| Scenario | Planted error | Verdict line (sketch; ge and ge_step identical in kind) |
|---|---|---|
| correct | none (deformation +2 %, stress +6 %: SOLID187 vs T10) | AGREES: 11 of 11 compared metrics inside tolerance |
| units_m | deformations typed in m into the mm column | DISCREPANCY: 2 of 11 … most likely cause — units: mm vs m (factor 1/1000) |
| wrong_support | a bolt support left out (deformation, energy × 2.3, stress × 1.7) | DISCREPANCY: 7 of 11 … most likely cause — boundary conditions … |
| room_temperature | Mechanical left at 22 °C (deformation × E(300)/E(22) = 0.913) | AGREES within tolerance, BUT a signature is hidden inside it — temperature … |

12 of 12 planted errors caught (sketch, ge, ge_step). The rehearsal found two defects that are fixed: (1) the
22 °C error hides inside the ±10 % deformation tolerance — the verdict now reports exact signatures found inside the
tolerance ("AGREES … BUT"); (2) the material signature matched the baseline's own modulus (ratio 1.000) and the
loose thermal signature (±25 %) outranked the BC change on GE — now only genuinely different moduli count and the
thermal band is not ranked as exact. Test: `tests/test_bracket_scripts.py::test_ansys_rehearsal_catches_every_planted_error`.

## 7. Rehearsals (studies/final_2026/ansys/out/)

`sketch` (invented mounting bracket like the organisers' sketch, loads calibrated `--calibrate 0.8`), `ge`
(GE-type bracket envelope, GE loads 35.6 / 37.8 / 42.3 kN and 564.9 N m, AM filter on) and `ge_step` (the same part
read from its STEP with automatic hole detection, proposed and calibrated loads, `--quick`: the day path) and
`dryrun_cold` (below). Numbers: each folder's `report.md`; §8 summarises all four.

**Cold dry run (23:03–23:20, `dryrun_cold`) [K].** A STEP never used before (angle bracket: base plate with Ø6.6 and
Ø9 bolt holes, web, gusset, Ø12 lug bore along x; `inputs/dryrun_bracket.step`, made from a drawing by
`cadout.drawing_to_cad`) and a material CSV with misspelled names (`inputs/dryrun_materials.csv`: "Ti6Al-4V",
"Inconnel 718", "17-4 PH stainless", "Scalmaloy", "Structual Steel"), one command in a fresh shell:
`python scripts/bracket_day.py …/dryrun_bracket.step --materials …/dryrun_materials.csv --calibrate 0.8 --case
dryrun_cold --handoff`. Exit 0, every deliverable written, no manual step. Wall clock **1005 s (16 min 45 s)**:

| Stage (log time stamps) | s |
|---|---|
| start, material matching (2 alias, 3 close), STEP read, hole scan (5 bores, Ø within 1 %), voxel 1.50 → 1.31 mm | 19 |
| voxelisation (32 524 elements), set-up proposed, exact CAD volume (73 522 mm³; voxels −2.46 %) | 4 |
| baseline at 20 / 300 °C, load calibration (× 0.1635), thermal sensitivity | 34 |
| 3-level voxel convergence (9 688 / 32 524 / 78 293 elements) | 46 |
| topology 50 / 35 / 25 % (234 + 193 + 183 s) | 616 |
| T10 check of the initial design, 2 meshes (28 723 / 78 805 elements) | 183 |
| T10 of the chosen layout + verified selection (T10/voxel 1.625 → utilisation 0.775, passes) | 67 |
| documents: CAD, material cards, eco audit, figures, report, film hand-off | 36 |

Result: Ti-6Al-4V L-PBF, topology 25 %, 0.0803 kg vs 0.5771 kg steel (86.1 % lighter); Scalmalloy fails at
300 °C. Found and fixed during the dry run: the two-panel shape figure (f5) had its panels 2.3 pt out of line
(datawiz UYARI) when the two renders had different pixel sizes — renders are now padded to one canvas
(`figures._same_canvas`), f5 0 HATA · 0 UYARI; documents rebuilt with `--report-only` in 20 s. Seen in the render: a
thin spur on the inner strut of the 25 % layout (thinnest member 4.5 mm = 3.5 voxels in the report) — smooth it in
CAD before printing. The hand-off went to `handoff/dryrun_cold/` (not used by the film).

Reproducibility [K] (20:20, `--report-only --reverify` on a copy of the sketch cache in D:\tmp_ideathon): the T10
re-check of the chosen 25 % layout gave the same 28 079 elements, 264.5 MPa, utilisation 0.528 and the same choice;
the GE T10 meshes of the initial design repeated 20 550 / 58 580 elements, 0.6882 mm, 1070.2 MPa (gmsh single
thread). `--report-only` no longer re-meshes when the T10 check of the initial design is already cached (it did so
for GE, where nothing passes and the verification list stays empty: GE report now 17 s; the T10 pair took 1 min 40 s before), and it
writes to `--out`/`--case` instead of the folder stored in the cache (the reproducibility run above overwrote
`out/sketch` with identical numbers but no figure list before this was fixed; the sketch report was regenerated and
its result block compared equal to the anchored copy).

## 8. Results of the rehearsal runs

Generated at 23:50 by `python scripts/bracket_summary.py sketch ge ge_step dryrun_cold` from the runs' result.json files [K]. "Ranking utilisation" is what the selection used (voxel stress, multiplied by the layout's T10/voxel factor where that factor is > 1); the T10 verification line gives the checked value. Production CO₂e = material + manufacture + transport, as in each `eco_audit.md`.

### `sketch` — Sketch-type mounting bracket (rehearsal, invented dimensions)

Voxel 1.70 mm, 22439 elements, T = 300 °C, total 728 s. Baseline structural_steel on the initial design: **0.8515 kg**, worst deformation 0.1332 mm, worst von Mises outside the hole zones 130.2 MPa (voxel H8IM).

T10 conforming check of the initial design (2.21 mm, 56512 elements): deformation 0.1338 mm (voxel/T10 0.995), vM outside 166.7 MPa.

| Layout | Kept | vM outside the hole zones at limit load, voxel (MPa) | Status |
|---|---|---|---|
| topo 50 % | 0.500 | 202 | ok |
| topo 35 % | 0.351 | 273.2 | ok |
| topo 25 % | 0.251 | 447.8 | ok |

Verification: ti64_lpbf / topo 25 %: voxel 447.8 MPa, T10 264.5 MPa (factor 1.000), T10 utilisation 0.528 → passes.

**Choice:** ti64_lpbf · topo 25 % · 0.1196 kg (86.0 % lighter than the baseline, ranking utilisation 0.894 (voxel stress × the layout's T10 factor where measured)).

Eco audit (kg CO₂e): baseline production (material + manufacture + transport) 16.17, life 2.393e+04; chosen production 8.942, life 3367.

### `ge` — GE-type engine bracket (envelope approximation)

Voxel 2.20 mm, 22947 elements, T = 300 °C, total 525 s. Baseline structural_steel on the initial design: **1.9964 kg**, worst deformation 0.8342 mm, worst von Mises outside the hole zones 1210 MPa (voxel H8IM).

T10 conforming check of the initial design (2.86 mm, 58580 elements): deformation 0.6882 mm (voxel/T10 1.212), vM outside 1070 MPa.

| Layout | Kept | vM outside the hole zones at limit load, voxel (MPa) | Status |
|---|---|---|---|
| topo 50 % | 0.501 | 1510 | ok |
| topo 35 % | 0.351 | 2361 | ok |
| topo 25 % | 0.250 | 3950 | ok |


**Choice:** in718_lpbf · initial · 2.0726 kg (3.8 % heavier than the baseline, ranking utilisation 1.104 (voxel stress × the layout's T10 factor where measured), FAILS — no candidate passes).

Eco audit (kg CO₂e): baseline production (material + manufacture + transport) 37.9, life 5.61e+04; chosen production 60.94, life 5.826e+04.

### `ge_step` — ge_bracket

Voxel 2.80 mm, 10848 elements, T = 300 °C, total 168 s. Baseline structural_steel on the initial design: **1.9964 kg**, worst deformation 0.2294 mm, worst von Mises outside the hole zones 130.2 MPa (voxel H8IM).

T10 conforming check of the initial design (3.64 mm, 32784 elements): deformation 0.1579 mm (voxel/T10 1.453), vM outside 102.8 MPa.

| Layout | Kept | vM outside the hole zones at limit load, voxel (MPa) | Status |
|---|---|---|---|
| topo 40 % | 0.399 | 148.9 | ok |
| topo 25 % | 0.251 | 392.1 | ok |

Verification: ti64_lpbf / topo 25 %: voxel 392.1 MPa, T10 501.8 MPa (factor 1.280), T10 utilisation 1.001 → fails, re-ranked.
Verification: ti64_lpbf / topo 40 %: voxel 148.9 MPa, T10 135.8 MPa (factor 1.000), T10 utilisation 0.271 → passes.

**Choice:** ti64_lpbf · topo 40 % · 0.4430 kg (77.8 % lighter than the baseline, ranking utilisation 0.297 (voxel stress × the layout's T10 factor where measured)).

Eco audit (kg CO₂e): baseline production (material + manufacture + transport) 37.9, life 5.61e+04; chosen production 33.13, life 1.247e+04.

### `dryrun_cold` — dryrun_bracket

Voxel 1.30 mm, 32524 elements, T = 300 °C, total 965 s. Baseline structural_steel on the initial design: **0.5771 kg**, worst deformation 0.0797 mm, worst von Mises outside the hole zones 130.2 MPa (voxel H8IM).

T10 conforming check of the initial design (1.69 mm, 78805 elements): deformation 0.07652 mm (voxel/T10 1.042), vM outside 123.2 MPa.

| Layout | Kept | vM outside the hole zones at limit load, voxel (MPa) | Status |
|---|---|---|---|
| topo 50 % | 0.501 | 124.1 | ok |
| topo 35 % | 0.351 | 171 | ok |
| topo 25 % | 0.251 | 239.1 | ok |

Verification: ti64_lpbf / topo 25 %: voxel 239.1 MPa, T10 388.5 MPa (factor 1.625), T10 utilisation 0.775 → passes.

**Choice:** ti64_lpbf · topo 25 % · 0.0803 kg (86.1 % lighter than the baseline, ranking utilisation 0.775 (voxel stress × the layout's T10 factor where measured)).

Eco audit (kg CO₂e): baseline production (material + manufacture + transport) 10.96, life 1.622e+04; chosen production 6.006, life 2262.

## 9. Film hand-off

`studies/final_2026/ansys/handoff/<case>/` in the film's input format (its README, "Girdi dosyası" table): `girdi.json`,
`result.json` (`ranking[]`), `yukler.json`, `yogunluk.json` (`runs[i].density` [x][y][z], `meta.voxel_mm`,
`meta.origin_mm`), `parca.stl`, `baslangic.stl`, `gerilme.txt` (Mechanical export layout, ultimate load). Run
`node film.mjs <that folder>/girdi.json` in `D:\Video Simulations\Ideathon-2026-Ansys`. Not run from here (the film
folder is read-only for this session).

Additions for the film's requests 13–15 (4 Nov evening; backward compatible, `handoff/CHANGES.md`):
`yogunluk.json` runs carry `warm_start_from` and the chosen run `snapshots` (iteration, density every 5 iterations:
`topo3d.optimize(snapshot_every=…)`, `Options.snapshot_every = 5`; cached studies retrofitted with
`scripts/bracket_snapshots.py --replay`, replay = cache to 3.1e-8); `result.json` → `details.setup.roles_source`
("auto" = proposal untouched, by a signature of roles/supports/loads; "edited" otherwise); `result.json` also
carries `stress_basis` per ranking row and the full `details`, plus `eco_audit.*` and `materials/` in the folder.
Fake Ansys data is never written to `handoff/` (§6c).

## 10. Open items and limits

* Ansys itself was not run: every "Ansys would give" statement is our model, validated against analytical and
  published references, not against Ansys output.
* Stress at sharp re-entrant edges is singular in both models; the utilisation of the **initial** design is therefore
  mesh dependent. The optimised layouts are exported as smoothed, volume-matched STLs and re-checked with T10;
  smoothing removes the voxel staircase but not thin members or spurs (dryrun_cold: a spur, thinnest member
  4.5 mm = 3.5 voxels, §7) — those need a CAD clean-up and a T10 re-check of the cleaned part.
* "Mixable Density" (Ansys 2025 R1 default topology method, doc 16) is proprietary: we reproduce the density-based
  SIMP family, not its code; layouts will differ in detail, retained volume and compliance trends should agree.
* Stress-constrained topology is done as a stress-aware volume search over layouts (lightest passing) + T10
  verification. The true 3-D optimiser (`stress3d`, §4c) now ends 0/1 with projection (grey 9.5 %) but its
  black-and-white voxel designs overshoot σ̄ by 42–83 % (projected; 54–147 % without projection) at staircase
  corners, so it stays EXPERIMENTAL
  (`topo3d.optimize_stress` is the older single-P-norm version, kept for its gradient test).
* Ti-6Al-4V E(300 °C) factor 0.88 is a trend reading (TIMET table at 230 °C); laser-DED data give 0.97 [D-ag].
* Electricity CO₂ factor, machining energy, buy-to-fly and life distance are assumptions [Y].
* STEP: multi-body files and assemblies are now listed, fused and checked (§1, our own multi-body STEP); a real
  organisers' assembly (product structure, units other than mm, surface-only bodies) was not available to test.
* Life: a screening at temperature with AM-surface knock-downs (§5b); k_T for the non-steels and the IN718
  surface factor are assumptions [Y], 17-4PH has no endurance value, notch sensitivity q = 1. No load spectrum,
  damage sum or porosity statistics.
* GE rehearsal uses our blocky envelope (sharp re-entrant edges → singular peaks; nothing passes at 300 °C with the GE
  loads). A real GE bracket STEP is public (dolfiny demo `ge_bracket_rotated_nonds.step`, research_notes R3 §1b):
  downloading it needs the user's OK; it would make the STEP rehearsal realistic.
* Voxel vs T10 deformation agreed within 0.5 % on the sketch bracket but differed by 21 % on GE at 2.2 mm voxels
  (thin 7.6 mm clevis arms ≈ 3.5 voxels); refined to 1.2 mm the voxel loaded-bore deformation is within 1 % of T10
  (§4). The cross-check template reports the T10 numbers and the mean deformation of the loaded bore.
* ruff: line-length (E501) findings left in the bracket files; no test enforces ruff in this repository.
* From the jury review (§11b): no lug bearing / net-section / shear-out check; thermal mismatch only for the steel
  baseline; no fitting or AM material factor; one T10 mesh on the chosen layout (no convergence pair); no stiffness
  criterion; AM overhang filter off in the sketch and dryrun rehearsals; HIP / heat-treatment energy missing from the
  eco audit; `--calibrate` uses the voxel stress (T10 of the same design can be ~28 % higher on sharp edges).

## 11. Questions for the mentors (from the notes, sharpened)

1. Is 300 °C a continuous service temperature or a short peak? (sets which strength curve: ½ h vs long exposure)
   And is the bracket free to expand (mounts at the same temperature / same CTE) or constrained? Constrained
   expansion alone gives ≈ 1.2 GPa in steel (§4b).
2. Load cases, magnitudes, and are they limit or ultimate? Which safety factor / criterion?
3. Will we receive CAD (STEP) or a drawing with dimensions? Which holes are bolted, which carry the load?
4. Does "3" mean three materials in the comparison table?
5. Is 3-D printing mandatory or an assessment criterion? Which machine/build direction?
6. Eco Audit only for the initial design, or also for the redesign? Which EduPack version and use-phase row?
7. Which Ansys products/licences do we get (Mechanical topology "Mixable Density", Discovery, Granta)?
8. How should the bolts be modelled: Fixed Support on the bore faces, a pin (cylindrical support) plus seat, or
   bolt/beam connections? On the GE rehearsal the choice moves individual bolt loads by up to 4× (§6b).

## 11b. Jury questions (hard review, 4 Nov 23:45) — and our answers

A fresh reviewer read this document cold, playing an Ansys/Synopsys jury, and ranked the ten most damaging
questions. Answers cite where the evidence is; where we have no answer we say so (gaps also in §10).

1. **"Your 86 % saving rests on loads you invented — and your own baseline is at yield."** True for the rehearsals:
   the sketch loads were calibrated so that steel has utilisation 0.8 on the *voxel* stress (130.2 MPa = 0.8 × Fty(300)
   162.8 MPa, `setup.json` `_calibration`, × 0.2544 [Y]); the converged T10 stress of the same design is 166.7 MPa
   (utilisation 1.02, §8). The saving is a *relative* result at equal loads; mass follows density × retained volume,
   and 25 % was the lowest fraction we searched (Ti utilisation 0.528 after T10 leaves room for less). On the day the
   organisers' loads replace the calibration; we will quote the result only with their loads.
2. **"You never ran Ansys — why trust 'Ansys agrees'?"** We do not claim Ansys output (§10, first bullet). What we
   claim is checked: patch test exact, cantilever 0.986–0.992 of Timoshenko, plate-with-hole Kt within +2.4/+3.7 % with
   T10 (the SOLID187 analogue), STEP volumes to 0.24 % (§4). The topology code agrees with our own top88-family port
   (−0.006 %); the external top3D125 benchmark was not reproduced (§4). The cross-check template + verdict (§6, §6c)
   is how the team's real Ansys numbers get compared on the day; the rehearsal tests the comparison logic only.
3. **"You exclude the bores from the stress check — where are bearing, net-section and shear-out of the lug?"**
   Not in the pipeline: von Mises is checked outside bore radius + `exclusion_mm` (§2), the rings are kept solid,
   and bolt loads are reported (§6b). The classical lug checks are a gap; the repository has
   `structures.joints.bearing_strength` for a hand check on the day with the §6b bolt loads [gap, §10].
4. **"Where do the 300 °C allowables come from?"** §3 table, value by value: steel Fty × 0.651 (EN 10028-2 P235GH
   [D-ag]); Ti-6Al-4V × 0.624 and 17-4PH from MIL-HDBK-5J curves [D]; IN718 Special Metals [D-ag]; Scalmalloy
   Colibrium [D-ag]. Two weaknesses we state: wrought temperature factors are applied to L-PBF material [Y]
   (`matdata.py`), and the MIL curves are short-exposure values — long service at 300 °C is mentor question 1.
   Room-temperature AM values are typical (datasheet), not A/B-basis allowables.
5. **"The brief says extend life — as printed, your part has less life margin than steel."** Our own screening says
   so (§5b): Ti 25 % as-built margin 0.67, machined 2.29; steel 0.91 (ASME curve with design margins). The remedy is
   surface finishing of the highly stressed members (machining, polishing or shot-peening; HIP alone does not fix the
   as-built surface, §5b sources) or a heavier layout. Screening only: k_T [Y], q = 1, no spectrum.
6. **"Rigid bores at 300 °C — what about real joints and thermal mismatch?"** The idealisation matters and we
   measured it: bolt loads move up to 4× between fixed bores, seats and the rigid-plate split (§6b); a constrained
   steel bracket at ΔT = 278 K sees ≈ 1200 MPa (§4b), so our strength check assumes free expansion [Y]. Thermal
   mismatch was computed for the steel baseline only — for Ti on a steel or aluminium mount it is not assessed [gap].
7. **"Limit or ultimate? Fitting factor? AM factor?"** Default: loads are limit, ultimate = 1.5 × limit (CS 25.303)
   [Y]. If the organisers give ultimate loads: `"design_criteria": {"limit_to_ultimate": 1.0}` in `setup.json` (no
   yield at the given loads; used for GE). A fitting factor (CS 25.625, 1.15 from general knowledge, NOT read this
   session) and an AM material factor are not applied; they can be applied by scaling the loads in `setup.json` [gap].
8. **"How accurate is a voxel mesh compared with SOLID187, and is the final design converged?"** Voxel stresses are
   not trusted for the choice: the T10/voxel stress ratio of the checked layouts was 0.59 (sketch 25 %: 264.5 vs
   447.8 MPa), 1.62 (dryrun 25 %), 1.28 and 0.91 (ge_step 25 % and 40 %; `result.json` → `verification`), which is
   why every choice is re-checked with T10 and a ratio > 1 feeds back into the ranking (§2). Gap:
   the chosen layout has one T10 mesh, not a convergence pair; the initial sketch design moves 131 → 167 MPa between
   two T10 meshes because of sharp re-entrant edges. No stiffness or frequency criterion was given: the chosen sketch
   layout deflects 5.2× the steel part (0.694 vs 0.133 mm) — a mentor question.
9. **"Compliance SIMP at fixed volume is not Mixable Density and not minimum mass. Is it printable?"** Minimum mass
   comes from the selection: lightest material × layout that passes after T10 (§2); stress-constrained topology is
   EXPERIMENTAL (§4c). Mixable Density is proprietary; we reproduce the density-based family (§10). The 45° overhang
   filter exists (`--am-filter`) but was off in sketch and dryrun_cold (on for ge); bores across the build
   direction, support and powder removal, residual stress and the dryrun spur (§7) need a print-preparation step.
10. **"Your eco audit is mass × an assumed distance."** Largely yes for the life total: the use phase dominates and
   rests on 6.0e7 km [Y] (§5); the eco report therefore also gives break-even distances and a marginal-fuel variant.
   Production: buy-to-fly 8 for the machined steel [Y] and grid 0.30 kg/kWh [Y, NOT VERIFIED]; HIP, heat-treatment and
   post-machining energy of the AM route are not included [gap]. Ti has twice the production CO₂ of 17-4PH (8.94 vs
   4.41 kg production total, sketch `eco_audit.md`).

## 11c. sketch2 prep — the organisers' 5 Nov hand sketch (geometry only, NO analysis run)

**SUPERSEDED 5 Nov 11:13:** the official challenge files arrived (`studies/final_2026/ansys/official_2026-11-05/`, owned by another session; read-only here). Do not prepare the day from sketch2; the section stays as a record of the geometry tools it exercised.

Sketch: `studies/final_2026/ansys/inputs/organiser_sketch_2026-11-05.png` (read 5 Nov ~11:05): an elongated,
rounded ("stadium") plate labelled "parça", about 6–7 small through-holes near its ends and edges, two arch-shaped
features standing on it (a larger and a smaller inverted U), a small hole next to the smaller arch. No dimensions.

**Parametric model** `python scripts/bracket_sketch2.py [--set name=value …] [--variants …]` — every dimension is a
named parameter in mm, all our reading [Y]: plate L 160 × W 70 × t 8 (round ends r = W/2); 6 bolt holes Ø8.5 (one
at each end centre, two near the edges at each end); arch A (larger) at x 70, y 48, inner r 14, wall 6, width 12;
arch B at x 100, y 22, inner r 9, wall 5, width 10; small hole Ø6 under arch B; optional hole through the crown of
arch A (`crown_A_d`, off). Variants for the ambiguous parts: `loop` / `loop_nohole` (arches = closed straps, a pin or
cable through the opening, axis y) and `lug` / `lug_nohole` (arches = lugs with a pin bore, axis y); "nohole" =
without the small hole. Files: `inputs/sketch2_<variant>.json / .step / .stl`; checks and proposals in
`inputs/sketch2_prep/<variant>/` (`check.json`, `setup.json` = the pipeline's own proposal, `setup_A.json`,
`setup_AB.json`, `preview.png`). Not in `out/` or `handoff/`.

Geometry-only checks [K] (`pipeline.prepare` on the STEP: STEP read, hole scan, voxels, exact volume; no FEA):

| Variant | Solids | Volume (mm³) | Steel mass (kg) | Bbox (mm) | Voxel (mm) | Holes found (z / y) | Proposed roles |
|---|---|---|---|---|---|---|---|
| loop | 1 | 83 819 | 0.658 | 160 × 70 × 28 | 1.20 | 7 / 2 | 7 supports (incl. the Ø6), 2 arch loads |
| loop_nohole | 1 | 84 045 | 0.660 | 160 × 70 × 28 | 1.50 | 6 / 2 | 6 supports, 2 arch loads |
| lug | 1 | 92 329 | 0.725 | 160 × 70 × 48 | 1.20 | 7 / 2 | 7 supports (incl. the Ø6), 2 arch loads |
| lug_nohole | 1 | 92 583 | 0.727 | 160 × 70 × 48 | 1.60 | 6 / 2 | 6 supports, 2 arch loads |

Preview images (4 views: iso, top, front, side; datawiz audit 0 HATA):
`studies/final_2026/ansys/inputs/sketch2_prep/{loop,loop_nohole,lug,lug_nohole}/preview.png`.

Does the pipeline accept this geometry? Yes, with one known limit [K]: curved arches, 9 holes and a hole through a
curved crown are found by the voxel hole scan (`tests/test_bracket_sketch2.py`, 5 tests: bolt diameters within 6 %,
lug pin bores within 4 %, crown hole Ø6 within 15 %, arches proposed as loads). The lug pin bores come out exact
(Ø27.9 / Ø18.0 for 28 / 18). A loop opening (half-disc between strap and plate) is fitted as the circle of equal
area (Ø19.5 at z 14.1 for r = 14 on the plate top), so the proposals replace it by the exact arch circle; even then a
**lateral** load on a loop is partly applied to the plate top inside the opening (the bearing distribution has no
notion of "strap only") — a limitation, stated in the proposal files [Y]. Proposed role of the Ø6 hole by the
pipeline: support (same axis as the bolts); our proposals set it **free** — a mentor question.

Set-up proposals (`setup_A.json`: load on arch A only; `setup_AB.json`: shared equally by both arches), bolts =
fixed bores, small hole free, limit loads with ultimate = 1.5 × limit, 300 °C; load cases [Y, magnitudes invented]:
LC1 vertical pull-off +z 4000 N, LC2 lateral in the arch plane +x 2500 N, LC3 along the arch axis +y 1500 N.
Applied to the mesh without solving: resultants exact for every case, 258–990 loaded nodes per arch. Hole ids refer
to our geometry: on the day, run once, then copy `load_cases` / `design_criteria` into the day's own `setup.json`
with its hole ids. Materials: `inputs/sketch2_materials.csv` (Structural Steel, Ti-6Al-4V, Inconel 718, 17-4PH,
Scalmalloy — all five match the pool as `alias`).

Command for the day (paste; replace the STEP name):

```bash
python scripts/bracket_day.py studies/final_2026/ansys/inputs/day1.step --materials studies/final_2026/ansys/inputs/sketch2_materials.csv --case day1 --handoff
```

then edit `studies/final_2026/ansys/out/day1/setup.json` (roles, `load_cases` from `setup_A.json` or
`setup_AB.json` with the day's hole ids, magnitudes from the organisers; no loads given → add `--calibrate 0.8`)
and run the same command again (≈ 17 min at the default size, §7).

Questions for the mentor about this shape:
1. Are the two arches straps (a pin / cable through the opening) or lugs with a pin bore? Which arch carries the
   load, or both — and how is it shared?
2. Load directions and magnitudes per arch: pull-off (normal to the plate), lateral in the arch plane, along the
   arch axis? Limit or ultimate?
3. Which holes are bolted (all six?), what is the small hole next to the lower arch for (bolt, locating pin,
   drain, lightening)? Fastener size and whether the bolts are fixed bores or seats on the plate underside.
4. Is the plate's underside a contact surface (bolted flat to a structure — then only bending of the plate between
   bolts matters) or are the bolts the only connection?
5. Are the arch dimensions and positions fixed (interface to a mating part) or part of the design space? May the
   plate outline change?
6. Build direction for printing: plate flat on the build plate (arches vertical) is the natural choice — allowed?

## 12. Interface gate (ux-yasalari) for the CLI output and report.md

GÖREV BÜTÇESİ — `scripts/bracket_day.py` (yüzey: cli) + `out/<case>/report.md` (written after the code; the gate
should have come first — applied retroactively on 4 Nov 17:45 and two findings fixed, see rows 1 and 13).
Birincil görev: geometry in → every deliverable out; then tell the user the one next step. Birincil eylem: one
command. Eylem/görünüm ≤ 5: 1 positional + options in 6 groups (re-measured 22:25 after --bodies/--materials: geometry 4, loads and materials 5, modes 4, run size 4, checks 4, output 4). Üst
düzey gezinti ≤ 7: report has 7 numbered sections. Seçenek kümesi: every option has a default. Geri bildirim:
timestamped stage lines, topology progress every 10 iterations. Stil: plain text, no colour. Tesler: voxel size,
hole roles, set-up, material list, convergence and T10 levels are automatic; only the geometry is required.

YASA DENETİMİ — CLI + report.md · 2026-11-04 · denetleyici: koşmadı (yüzey: cli/markdown, HTML yok)

Sonuç: 20/20 satır dolu · 0 HATA · 2 UYARI (gerekçeli) · 2 kapsam dışı · karar: TESLİM

| #  | Yasa | Ölçüm (sayı/gözlem) | Eşik | Durum | Gerekçe |
|----|------|---------------------|------|-------|---------|
| 1 | Hick | --help: önce 4 groups with 6 in run size and output (--evaluate-only, --reverify added later) → şimdi 6 groups, max 5 per group (22:25); report: önce 8 top-level sections → şimdi 7 (bolt loads, life screening added as ### under §4) | ≤ 7 · ≤ 5 | geçti | |
| 2 | Fitts | no pointer targets | — | kapsam dışı: CLI/markdown | |
| 3 | Jakob | argparse conventions (-h, --flag value / --flag=value, positional input) | 0 sapma | geçti | |
| 4 | Seçim Yükü | 25/25 options have defaults (--setup, --materials, --bodies: automatic when absent); `--quick` preset | varsayılan | geçti | |
| 5 | Yakınlık | report: one table per heading, blank line between groups; CLI: stage lines then figures then RESULT | gruplu | geçti | |
| 6 | Benzerlik | one table style; numbers .4g; units in headers "(mm)", "(MPa)", "(N)", "(N m)" (bolt table: forces to 1 N, moments to 0.01 N m) | tek biçim | geçti | |
| 7 | Tekdüze Bağlılık | each section = heading + table + one sentence | ≤ 12 | geçti | |
| 8 | Ortak Bölge | no boxes | — | kapsam dışı: markdown | |
| 9 | Prägnanz | no decoration, no colour | 0 | geçti | |
| 10 | Von Restorff | one bold "Choice [K]" line in the report; one "RESULT:" line in the CLI | 1 | geçti | |
| 11 | Miller | max table columns 7 (eco table was 9 → split into 6 + 6; topology 8 → 7; materials 8 → 7; bolt-load table 20:25: 7) | ≤ 7 | geçti | |
| 12 | Sıra Konumu | report first: set-up (what was assumed); last: Mechanical checklist + figures; CLI last: RESULT + NEXT | birincil görevler | geçti | |
| 13 | Doherty | stage lines every ≤ 3 min; önce topology 2-3 min silent → şimdi a line every 10 iterations (~30 s) | gösterge | UYARI | 30 s between lines is above 400 ms; per-iteration lines would flood the log |
| 14 | Zeigarnik | two-step day flow: first run prints "set-up PROPOSED -> edit … and re-run" | ≥ 3 adımda gösterge | geçti | 2 steps |
| 15 | Zirve-Son | success: "RESULT: material / layout / mass vs baseline. NEXT: …"; failure: "RESULT: FAILS … NEXT: check loads …"; stop: "RESULT: STOPPED - n material name(s) not matched … NEXT: fix the names …"; multi-body: error with the body table and the --bodies choice | 4/4 states | geçti | |
| 16 | Parkinson | required inputs 1/20 = 5 % | ≤ 50 % | geçti | |
| 17 | Tesler | required: geometry (system cannot know it); loads proposed, editable; multi-body STEP fused automatically, asks only when bodies are disconnected; material names matched automatically, asks only when unknown | gerekçe | geçti | |
| 18 | Postel | --unit mm/m/cm/in; volfracs comma list; STEP/STL/OBJ/PLY/JSON by extension; material list CSV/YAML/TXT, names case/space/hyphen-insensitive with typo tolerance | normalizasyon | geçti | |
| 19 | Occam | CLI end output 8 lines, each a file or the result | eşlenemeyen 0 | geçti | |
| 20 | Pareto | first screen of report.md = set-up + initial design; choice in §4 | ≥ 60 % | UYARI | the choice is in §4, not at the top: the set-up must be checked first (it may be a proposal) |

## 13. Figures (datawiz) — FİGÜR TESLİMİ

FİGÜR BRİFİ: in `src/aerokit/bracket/figures.py` (F1 convergence, F2 materials, F3 eco audit, F4 optimisation
history, F5 initial vs chosen renders) and `scripts/bracket_material_report.py` (relative mass at 20 / 300 °C).
Okur karma (team + jury), hedef `genel-tek` (88 mm), tema akademik; every figure saved through `Seti.kaydet(...,
kati=True)` (a HATA stops the run).

| Set | Figures | Figure audits | Set consistency |
|---|---|---|---|
| `out/sketch/figures` | f1–f5 | 0 HATA each (0–2 BİLGİ) | 0 HATA · 2 UYARI · SET TUTARLI |
| `out/ge/figures` | f1, f3, f4, f5 (no passing material → no f2) | 0 HATA each | 0 HATA · 1 UYARI · SET TUTARLI |
| `out/ge_step/figures` | f1–f5 | 0 HATA each | 0 HATA · 2 UYARI · SET TUTARLI |
| `material_selection/` | fig_relative_mass | 0 HATA · 2 BİLGİ | single figure |

Remaining UYARI (reasons): single-word axis titles ("Material", "Iteration") count as a different case style;
the bar chart (F2) uses a category grid, the others a value grid. Problems the gate caught and that were fixed
during the session: hyphen instead of U+2212 minus and E-notation on the log axis (F3), overlapping decade labels
(F3), overlapping dots (F3 dodge), saturated wide bars (F2 light fill), an axis title read as "quantity / unit"
(F4, set HATA), a title overflowing the figure (F4). Eye checks: F1 label overlap (fixed), F2 gridlines through value
labels (fixed), F4 misleading normalisation (fixed: relative to the initial design), F5 renders of the STL files.
