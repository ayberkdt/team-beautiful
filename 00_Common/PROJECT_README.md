# Team Beetiful — EUROAVIA Ideathon 2026

One folder per challenge, in event order; each holds everything for that challenge (docs, inputs, scripts,
outputs, research, submission) and opens with a README. The shared Python library `src/aerokit` and its test-suite
stay at the root.

```
00_Common/      rules + scoring, report/deck templates, organiser task notes, parallel-work rules, bibliography
01_Ansys/       bracket redesign           docs/ inputs/ official_2026-11-05/ scripts/ outputs/ submission/
02_EASA/        canopy alert retrofit      docs/ inputs/ research/ scripts/ outputs/
03_Advionics/   automated PAR guidance (radar -> pilot cue)   official_2026-11-06/ cases/ research/ templates/ submission/
04_Venus/       VESPER rotorcraft          docs/ literature/ code/ catalog/ reviews/ outputs/
prev_guess/     all preparation from before the real tasks (per challenge + 00_general)
src/aerokit/    the library (bracket/, canopy/, atc/, comms/, venus/ … see below)
tests/          pytest suite for the library and the day scripts
scripts/        shared tools: day_common.py, build_references.py, export_github.py, materials/
references/     MIL-HDBK-5J / NCAMP source PDFs + verification reports (data source of src/aerokit/materials)
```

Numbered docs: 00–16 → `prev_guess/01_Ansys/docs/`, 17 → `prev_guess/02_EASA/docs/`, 18 →
`prev_guess/03_Advionics/docs/`, 19 → `prev_guess/04_Venus/docs/`, 20 → `prev_guess/00_general/docs/`, 21 →
`00_Common/docs/`, 22 → `01_Ansys/docs/`, 23 → `02_EASA/docs/`, 24 → `prev_guess/03_Advionics/comms_kit_2026-11-05/docs/`, 25 → `04_Venus/docs/`.
Commands in the docs are run from this root folder with `PYTHONPATH=src`.

# aerokit — Ideathon 2026 engineering toolkit

Aerospace structures, finite elements, materials data and conceptual design in one Python
package (SI units, tension positive). Every formula and benchmark is tied to a literature
source (`@cite`, see [00_Common/docs/references.md](00_Common/docs/references.md)) and checked by the test-suite.

## Layout

```
src/aerokit/
  aero/          atmosphere, flow (Re, y+, GCI), geometry, wing loads, V-n, stability, weight, sizing,
                 aircraft model, propulsion, point performance, drag build-up
  design/        requirements → sizing → compliance → sensitivity → report; mission plan; validation
  mission/       geodesy, IAMSAR search patterns, coverage, mission simulation, STK/KML export
  units.py       unit-safe parsing of "1300 km", "150 km/h", "0.5 lb/(hp*h)"
  structures/    stress tensor, sections, beams, buckling, joints, pressure vessels, rotating parts, contact,
                 fatigue, fracture, structural sizing
  composites/    lamina, laminate (CLT, failure criteria, progressive failure, sandwich)
  materials/     catalogue (typical values) + MIL-HDBK-5J design allowables parsed to Markdown (data/*.md)
  fem/           Model, constraints (SPC/MPC), sparse solvers, elements (bar, frames, plane, plate, solid,
                 discrete), meshing, statics, modal, buckling, dynamics, non-linear truss, heat conduction,
                 error estimation, mesh convergence
  optimization/  truss/frame sizing, SIMP topology, design-point and wing-box optimisation, laminate stacking
  cad/           STL/OBJ/PLY/DXF readers (hardened against malformed files), surface tools, geometry report
  output/        tables, reports (text/Markdown/JSON/CSV), safe atomic writers, datawiz-audited figures
  references/    bibliography registry and the @cite decorator
  cli/           command-line interface (python -m aerokit)
  bracket/       Ansys bracket pipeline (geometry, voxel/T10 FEM, 3-D topology, eco audit, hand checks)
  canopy/        EASA canopy alert: faults, FMEA, FTA, sensors, logic, Monte Carlo
  atc/, comms/   Advionics: Mode A/C/S, ASTERIX, radar, MLAT, tracker, clearances, link budgets
  venus/         LuGus Venus rotorcraft (atmosphere, entry, BEMT, design); venus_flight.py mission
tests/           pytest suite (numerical benchmarks with sources, security, typing, property-based)
scripts/         shared generators (materials extraction + verification, references page, GitHub export)
references/      MIL-HDBK-5J / NCAMP source PDFs and verification reports
```

## Install and test

```bash
python -m pip install -e ".[plot,dev]"
```

```bash
python -m pytest -q
```

The suite prints `aerokit numerical checks: N/N passed`; each check carries its literature
source. `-m "not slow"` skips the mypy run.

## Command line

```bash
python -m aerokit --help
```

Top-level groups: `aero`, `geometry`, `mechanics`, `composite`, `fem`, `sizing`, `materials`.

Conceptual design and mission (Ansys-type task, see `prev_guess/01_Ansys/docs/06_development_plan.md`):

```bash
python -m aerokit sizing design src/aerokit/data/examples/design/ansys_2023_requirements.json --drag buildup --out-dir design_report
```

```bash
python -m aerokit sizing mission src/aerokit/data/examples/design/ansys_2023_mission.json --requirements src/aerokit/data/examples/design/ansys_2023_requirements.json --out-dir mission_plan
```

```bash
python -m aerokit sizing validate
```
Every command ends with one `Result:` sentence and one `Next step:`; `--format md|json|csv`
or `--out report.md` (format from the extension) writes the same report as a file.

## Materials data

`src/aerokit/materials/data/*.md` holds 48 MIL-HDBK-5J material sheets extracted
automatically from the public-release PDF (`scripts/materials/extract_mil_hdbk_5.py`). Every
number was re-found on its cited PDF page by two independent PDF parsers
(`scripts/materials/verify_tables.py`, report in `references/materials/verification_report.md`).

```python
from aerokit.materials import handbook, library
handbook.get_allowable("al-7075-t6", "Fty", basis="A", direction="L", thickness=2e-3)   # Pa
library.design_values("7075-T6", basis="B", thickness=2e-3)                            # record with allowables
```

The handbook's vector figures (effect of temperature, stress-strain, tangent modulus) are digitized
into `src/aerokit/materials/data/curves/*.md` (`scripts/materials/digitize_figures.py`; checks and
overlays in `references/materials/curve_verification_report.md`). Raster-only figures are listed
there as skipped, and reading them raises an error instead of returning a guess.

```python
from aerokit.materials import curves
curves.temperature_factor("al-2024-t3", "Ftu", 400, exposure=0.5)   # % of room-temperature Ftu (74.6)
```
