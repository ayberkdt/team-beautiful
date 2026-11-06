# Team Beetiful — EUROAVIA Ideathon 2026

Our own work for the EUROAVIA Ideathon 2026 (Bruges, 3–8 Nov 2026): the `aerokit` Python toolkit, the competition
notes, material catalogues, analysis scripts, results and figures. This repository is **public**, so it contains
**only work made by the team**. Exported from the working folder with `scripts/export_github.py`;
`EXPORT_MANIFEST.txt` lists every file with a SHA-256 prefix.

## Layout

One self-contained folder per challenge, one folder for shared rules and notes, one archive.

| Folder | What |
|---|---|
| `00_Common/` | shared notes, report template, coordination |
| `01_Ansys/` | aircraft bracket redesign |
| `02_EASA/` | canopy alert retrofit |
| `03_Advionics/` | automated PAR guidance: radar → correction → pilot cue |
| `04_Venus/` | rotorcraft on Venus |
| `prev_guess/` | everything prepared before the real tasks were known |
| `src/aerokit/`, `tests/`, `scripts/` | shared library, its tests, shared tools |

## Not in this repository (on purpose)

| Left out | Why | Where to get it |
|---|---|---|
| Organiser files: challenge cards and task sheets, intro slides, Discovery CAD (`.dsco`), Granta material selection and eco-audit reports | third-party files given to participants | from the team chat / Drive; put them in `01_Ansys/official_2026-11-05/files/` |
| Any part geometry rebuilt from the organiser CAD (`*.step`, `*.stl`) | it is the organiser's design | rebuild with `python 01_Ansys/official_2026-11-05/visuals/scripts/build_exact.py` (reads `derived/features.json`) |
| The Synopsys introduction (marked "Proprietary. Do Not Share.") and our notes built from it (docs 10–14 and their reports) | the sponsor asked us not to share it | ask the team |
| Handbooks, regulations, papers (e.g. MIL-HDBK-5J) | third-party documents; every value cites its source and URL | the URLs in the catalogues and `00_Common/docs/references.md` |
| Run caches (`*.pkl`), videos, files over 20 MB | size | re-run the commands below |

## Where to start (Ansys bracket challenge)

| File | What it is |
|---|---|
| `01_Ansys/official_2026-11-05/setup/boundary_conditions.md` | the official part: measured geometry, supports, load cases LC1a/b/c + LC2, pass criteria, hand checks, open questions for the mentor |
| `01_Ansys/official_2026-11-05/analysis/organiser_materials.py` | the organisers' Granta data for S275N, Al 2618-T6 and Ti-8Al-1Mo-1V (23 °C) and an eco-audit model that reproduces their initial-design report to ±1 % |
| `01_Ansys/official_2026-11-05/analysis/material_swap.py` | material-only swap on the unchanged geometry: mass, deflection, utilisation, cost, life CO₂ |
| `01_Ansys/official_2026-11-05/catalogue/materials_catalogue.md` | our sourced catalogue of the same three materials at 23 / 300 / 350 °C (MIL-HDBK-5J, EN 1993-1-2) and the contradictions we found in the organisers' list |
| `01_Ansys/official_2026-11-05/runs/` | baseline FEA of the initial steel part (fixed bolt bores / bolt seats), topology runs |
| `01_Ansys/official_2026-11-05/visuals/` | renders, load/BC diagram, dimensioned views (+ scripts) |
| `01_Ansys/docs/22_ansys_bracket_final.md` | the toolchain: one command from CAD to report, validation, known traps |

Other challenges: `02_EASA/docs/23_easa_canopy_retrofit.md`, `03_Advionics/README.md`, `04_Venus/docs/25_lugus_venus_rotorcraft.md`.

Tags used in every document: **[D]** read in the primary source, **[D-org]** organisers' file, **[S]** secondary
source, **[K]** computed here (command given), **[Y]** our assumption.

## Install

Python ≥ 3.11.

```bash
python -m pip install -e ".[plot,cad,dev]"
python -m pytest -q
```

STEP import, exact CAD export and the 10-node tetrahedral check also need `gmsh` (and optionally `pypardiso`,
`pyamg`) — see `01_Ansys/docs/22_ansys_bracket_final.md` §1 "Environment". Without them everything else runs, only slower.
On Windows set `PYTHONIOENCODING=utf-8` before running scripts that print audit tables.

## Bracket in one command

```bash
python 01_Ansys/scripts/bracket_day.py <part.step> --setup 01_Ansys/official_2026-11-05/setup/setup_official_fixed_bores.json --case day1
```

Output goes to `01_Ansys/outputs/cases/<case>/` (`report.md`, `result.json`, figures, MatML material cards,
eco audit, Ansys cross-check template).
