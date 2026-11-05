# aerokit — Ideathon 2026 engineering toolkit

Aerospace structures, finite elements, materials data and conceptual design in one Python
package (SI units, tension positive). Every formula and benchmark is tied to a literature
source (`@cite`, see [docs/references.md](docs/references.md)) and checked by the test-suite.

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
tests/           pytest suite (numerical benchmarks with sources, security, typing, property-based)
scripts/         reproducible data/doc generators (materials extraction + verification, references page)
docs/            competition notes (Turkish) and generated references
references/      source PDFs (competition documents, MIL-HDBK-5J)
outputs/         generated figures
archive/         legacy Turkish package (hesap_legacy_2026-10-25.zip) and old notes
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

Conceptual design and mission (Ansys-type task, see `docs/06_development_plan.md`):

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
