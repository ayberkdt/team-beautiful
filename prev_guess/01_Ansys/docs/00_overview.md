> The Turkish originals of docs 00–05 are archived in `prev_guess/00_general/archive/docs_tr_2026-10-25/`.

# 00 · EUROAVIA Ideathon 2026: overview and index

Prepared 2026-10-25. Event 3–8 November 2026, Bruges (Belgium). Challenges will be announced on the morning of 4 November.

## File map

| File | Contents |
|---|---|
| **00_overview.md** | format, past editions, installation and licence constraints, preparation list, unknowns, sources |
| [01_geometry_constraints.md](01_geometry_constraints.md) | CAD, units, naming, aerodynamic surface, fluid volume, structural geometry |
| [02_fluids_constraints.md](02_fluids_constraints.md) | Fluent: flow conditions, ISA/Re tables, mesh, solver, convergence |
| [03_mechanical_constraints.md](03_mechanical_constraints.md) | Mechanical/ACP: node budget, mesh quality, singularity, boundary conditions, FSI, buckling, load factors, materials |
| [04_2023_example_solution.md](04_2023_example_solution.md) | rehearsal solution of the 2023 Ansys task with the tools |
| [05_toolkit.md](05_toolkit.md) | aerokit package: CLI, Python modules, FEM, materials (MIL-HDBK-5J), CAD import, preliminary design, verification summary |
| [06_development_plan.md](06_development_plan.md) | plan against the 2023 Ansys task and its implementation status |
| [07_gap_analysis.md](07_gap_analysis.md) | measured gaps (off-design physics, mission, CFD/FEM cross-checks, sources, tests) and ordered actions |
| [08_past_challenges.md](08_past_challenges.md) | all known challenges of 2023 and 2024 with sources; why there was no 2022 edition |
| [09_2026_playbook.md](09_2026_playbook.md) | 2026 format, likely challenge families, a 5-hour slot plan and the aerokit recipe for each |
| [../reports/Havacılık hafifletme karar kataloğu.md](../reports/Havacılık%20hafifletme%20karar%20kataloğu.md) | **decision catalogue for the Ansys light-weighting task**: 25 decisions, conflict register, sourced data appendix, gaps for EduPack |
| [10_synopsys_2026_brief.md](10_synopsys_2026_brief.md) | **Synopsys/Ansys introduction of 27 Oct 2026**: skills asked (FEA, topology, materials selection, life cycle), courses, install blockers, F7 recipe |
| `src/aerokit/` | Python package: `python -m aerokit --help`; verification `python -m pytest` (from the root directory, `PYTHONPATH=src` or `pip install -e .`) |
| `outputs/` | example figures (with datawiz audit reports) |
| `references/competition/` | Regulations v1.1, 2023 challenge cards, 2023/2024 brochures (PDF) |
| `prev_guess/01_Ansys/scripts/flow_tables.py` | generator of the ISA/Re tables; `--check` compares the tables in file 02; the same function is also provided by `aerokit aero isa` and `aerokit aero flow` |
| `prev_guess/00_general/archive/` | single-file version before the split (v1, `ansys_constraints_v1_2026-10-25.md`); its content was moved to 00–03. Old `hesap` package: `hesap_legacy_2026-10-25.zip` |

## Evidence tags

Each item states the type of its source.

| Tag | Meaning |
|---|---|
| **[D]** | I read it from its source in this session. |
| **[A]** | A sub-agent opened and read the page; I did not re-read it. |
| **[S]** | Seen only in a search summary. |
| **[Y]** | Engineering judgement; no source. |
| **[H]** | Calculation or test in this session. |

---

## 1. This year's format is different

- **Four challenges, four slots; every team does all four** and submits a conceptual solution for each [D, Regulations v1.1 §1.3]. In previous years each team chose a single challenge: 24 hours in 2023, 48 hours in 2024 [D 2024 brochure; A 2023 blog].
- The "Competition" blocks are on 5 and 6 November; slot durations "not finalized" [D]. **Inference:** a few hours per challenge [Y].
- **Evaluation criteria:** technical feasibility, innovation/creativity, **sustainability**, presentation quality. No weights given [D §1.4].
- **BYOD.** Sponsors "may provide temporary licences" [D §1.3].
- **Language:** submissions and presentations entirely in English [D §1.2.3].
- **Update 2026-11-01:** the Synopsys/Ansys introduction (27 Oct) lists the skills for the 2026 Ansys challenge as structural FEA, optimisation/trade-offs, materials selection and life-cycle thinking (Discovery topology, Mechanical, Granta EduPack). See `10_synopsys_2026_brief.md`; the paragraph below is the 25 Oct view.
- **The Ansys challenge may not be CFD.** On the 2023 card the task was conceptual aircraft sizing + **STK** mission planning [D]. STK is not in the Ansys Student package [D]. Preparation therefore has three legs: CFD (02), structures (03), conceptual design + mission (04, §4).

## 2. Past editions

| Year | Location | Format | Sponsor challenges | Winner |
|---|---|---|---|---|
| 2023 | Terrassa (3–7 Sep) → Munich (5–9 Nov) | 24 hours, single challenge | Ansys: conceptual aircraft + STK. GTD: health monitoring (IVHM) and predictive maintenance for a reusable launcher | UniBOss (Forlì-Bologna) [A] |
| 2024 | Toulouse ENAC (26–31 Oct) → Zagreb (1–6 Dec) | 48 hours, single challenge, theme sustainability | Ansys, Eurocontrol, IGA | AVAION (Patras), Eurocontrol challenge [A] |
| 2025 | not found | – | – | – |
| 2026 | Bruges (3–8 Nov), single phase | 4 challenges × 4 slots | no sponsor name in the regulations | – [D] |

**Lessons from the 2023 cards** [D]:
- **Ansys card:** "evaluated on your engineering approach as a whole". Justified simplification is accepted. There is an explicit warning about unit conversion.
- **GTD card:** parameters to monitor in flight, post-flight diagnosis, degradation models, supervised learning. Required skills: sensors/avionics, reusability, numerical modelling (Mathworks), data mining.
- **Lesson:** challenges are not only simulation; **systems thinking + justification** is also required [Y].

## 3. Installation and licence constraints (K)

**Measured on this machine** [D, `Get-CimInstance`, `nvidia-smi`, `Get-PSDrive`, 2026-10-25]:
- Graphics card: GTX 1660 Ti, 6 GB.
- Memory: 15.9 GB RAM.
- Processor: i7-9750H, 6 cores.
- **4.28 GB free space on drive C:**.
- A full Ansys 2023 R1 with a licence server is installed under `D:\ANSYS Inc\v231`.

| # | Constraint | Source |
|---|---|---|
| K-01 | Student limits: flow 1 M cells/nodes, structural 128K nodes/elements, 4 cores in Fluent. | [D] |
| K-02 | The limits section starts with **"No Geometry Export"**; its scope is not explained. | [D] |
| K-03 | **Installation prerequisite: there must be a physical C: drive.** The page also asks for 50 GB of disk space. C: has 4.28 GB free (25 Oct); **3.42 GB on 1 Nov** [K]: **free up space on C: before the meeting.** | [D] |
| K-04 | Page: "Uninstall any existing Ansys products" and "The Ansys Student installation will overwrite any existing installations." The 2023 R1 installation on D: is affected. Do not uninstall anything until the licence type is clear. | [D] |
| K-05 | Discovery requires a dedicated NVIDIA card; the page lists only Kepler/Maxwell/Pascal, the 1660 Ti is Turing. If unsuitable, it does not start. **Try it first thing at installation.** | [D] |
| K-06 | One-time SheerID verification; licence valid until 31/03/2027; installation requires administrator rights. | [D] |
| K-07 | SpaceClaim is removed in 2027; the main tool is Discovery. | [A] |
| K-08 | A newer version opens an older file, not the other way round. Save templates in the event's version. | [Y] |
| K-09 | If the sponsor provides a temporary Academic/Research licence, the limits may be lifted. | [Y] |
| K-10 | **Granta EduPack is not in the Ansys Student bundle** (not listed on the student page, 1 Nov); it usually needs a university licence. The 2026 Ansys courses use it (doc 10 §3). | [D] fetch summary |

**Questions for the installation meeting:**
1. Licence type and duration.
2. What "No Geometry Export" covers.
3. Whether STK is on the installation list.
4. Version (is it 2026 R1).

## 4. Preparation list (before 4 November)

1. **Machine:** free up space on C: → meeting → (if needed) uninstall 2023 R1 → install → open Discovery → test the cell/node limit: 0.9 M and 1.1 M cells, 100K and 130K nodes.
2. **2D airfoil template:** generate the airfoil with `aerokit geometry airfoil --naca`. In Fluent y⁺ ≈ 1, AoA sweep; compare with XFOIL.
3. **3D half-wing template:** ≤ 0.9 M cells, named surfaces, reference values entered.
4. **Mechanical wing box template:** shell + beam, ≤ 110K nodes, pressure transfer from Fluent and Load Transfer Summary.
5. **Conceptual design rehearsal:** redo file 04 once from scratch; change the assumptions and look at the sensitivity.
6. **STK** (if provided): flight profile with Aviator, area coverage with Coverage.
7. **Presentation template:** English; a separate sustainability heading in every solution.
8. **Laptop package:** the `src/aerokit/` package (project root), Python + numpy + scipy (tested with Python 3.12), these md files (`docs/`), `references/`.

## 5. Unknowns

- 2026 sponsors, challenge companies, prizes, jury.
- Submission format and criteria weights.
- Scope of "No Geometry Export"; the exact cell limit in 2026 R1 Student (1 048 576 only in a forum summary [S]).
- Whether Fluent Aero and the propeller models are enabled in Student.
- Whether Discovery starts with the GTX 1660 Ti.
- Raymer 6th edition table numbers (sources are 4th/5th edition).
- ν12, G12, Yc for the composite (not in the Hexcel data sheet).

## 6. Sources

**Event**
- [D] Regulations v1.1: https://ideathon.euroavia.eu/wp-content/uploads/Ideathon-2026-Regulations-1.1.pdf
- [D] 2023 Ansys card: https://ideathon.euroavia.eu/wp-content/uploads/2023/08/Ansys-challenge.pdf
- [D] 2024 brochure: https://ideathon.euroavia.eu/wp-content/uploads/brochure-2024.pdf
- [A] Edition pages and blogs: https://ideathon.euroavia.eu/2023-edition/ · https://ideathon.euroavia.eu/2024-edition/ · https://ansys.synopsys.com/blog/college-students-develop-mission-skills-with-stk

**Ansys**
- [D] Ansys Student: https://ansys.synopsys.com/academic/students/ansys-student
- [A] Ansys Help (v242–v261): ansyshelp.ansys.com. Page names are in files 02 and 03.

**Conceptual design**
- [D] Raymer tables (VT AOE 4065 A4): https://www.aoe.vt.edu/content/dam/aoe_vt_edu/people/faculty/praj/avd-fundamentals/A4%20-%20Initial%20Sizing%20-%20Takeoff%20Weight%20Estimation.pdf
- [D] METU AE172 lecture 5: https://www.ae.metu.edu.tr/~ae172/19/lecture5.pdf
- [D] Scholz ch.5: https://www.fzt.haw-hamburg.de/pers/Scholz/HOOU/AircraftDesign_5_PreliminarySizing.pdf

**Materials**
- [D] ASM/MatWeb printouts (quickparts.com, Aluminum-7075/6061, Aluminium-2024 PDFs)
- [D] Hexcel HexPly 8552 EU: https://hexcel.com/wp-content/uploads/2025/12/HexPly_8552_eu_DataSheet1.pdf
- [D] Aubert & Duval TA6V: https://www.aubertduval.com/wp-content/uploads/2024/12/TA6V_2_GB.pdf

**Regulations and method**
- [A] 14 CFR 25.303/305/337 (law.cornell.edu); old 23.337 (govinfo 2011)
- [A] MIT 16.20 Unit 2
- [A] NASA SP-8007
- [A] Celik et al. 2008
- [A] NAFEMS mesh convergence
