# Team Beetiful — EUROAVIA Ideathon 2026 preparation

Our own work for the EUROAVIA Ideathon 2026 (Bruges, 3–8 Nov 2026): the `aerokit` Python toolkit, the competition
notes, material catalogues, analysis scripts, results and figures. This repository is **public**, so it contains
**only work made by the team**. Exported from the working folder with `scripts/export_github.py`;
`EXPORT_MANIFEST.txt` lists every file with a SHA-256 prefix.

## Not in this repository (on purpose)

| Left out | Why | Where to get it |
|---|---|---|
| Organiser files: challenge card, intro slides, Discovery CAD (`.dsco`), Granta material selection and eco-audit reports | third-party files given to participants | from the team chat / Drive; put them in `studies/final_2026/ansys/official_2026-11-05/files/` |
| Any part geometry rebuilt from the organiser CAD (`*.step`, `*.stl`) | it is the organiser's design | rebuild with `python studies/final_2026/ansys/official_2026-11-05/visuals/scripts/build_exact.py` (reads `derived/features.json`) |
| The Synopsys introduction (marked "Proprietary. Do Not Share.") and our notes built from it (docs 10–14 and their reports) | the sponsor asked us not to share it | ask the team |
| Handbooks, regulations, papers (e.g. MIL-HDBK-5J) | third-party documents; every value cites its source and URL | the URLs in the catalogues and `docs/references.md` |
| Run caches (`*.pkl`), videos, files over 20 MB | size | re-run the commands below |

## Where to start (Ansys bracket challenge)

| File | What it is |
|---|---|
| `studies/final_2026/ansys/official_2026-11-05/setup/boundary_conditions.md` | the official part: measured geometry, supports, load cases LC1a/b/c + LC2, pass criteria, hand checks, open questions for the mentor |
| `studies/final_2026/ansys/official_2026-11-05/analysis/organiser_materials.py` | the organisers' Granta data for S275N, Al 2618-T6 and Ti-8Al-1Mo-1V (23 °C) and an eco-audit model that reproduces their initial-design report to ±1 % |
| `studies/final_2026/ansys/official_2026-11-05/analysis/material_swap.py` | material-only swap on the unchanged geometry: mass, deflection, utilisation, cost, life CO₂ |
| `studies/final_2026/ansys/official_2026-11-05/catalogue/materials_catalogue.md` | our sourced catalogue of the same three materials at 23 / 300 / 350 °C (MIL-HDBK-5J, EN 1993-1-2) and the contradictions we found in the organisers' list |
| `studies/final_2026/ansys/official_2026-11-05/runs/` | baseline FEA of the initial steel part (fixed bolt bores / bolt seats), topology runs |
| `studies/final_2026/ansys/official_2026-11-05/visuals/` | renders, load/BC diagram, dimensioned views (+ scripts) |
| `docs/22_ansys_bracket_final.md` | the toolchain: one command from CAD to report, validation, known traps |

Other challenges: `docs/23_easa_canopy_retrofit.md`, `docs/24_advionics_comms_atc.md`, `docs/25_lugus_venus_rotorcraft.md`.

Tags used in every document: **[D]** read in the primary source, **[D-org]** organisers' file, **[S]** secondary
source, **[K]** computed here (command given), **[Y]** our assumption.

## Install

Python ≥ 3.11.

```bash
python -m pip install -e ".[plot,cad,dev]"
python -m pytest -q
```

STEP import, exact CAD export and the 10-node tetrahedral check also need `gmsh` (and optionally `pypardiso`,
`pyamg`) — see `docs/22_ansys_bracket_final.md` §1 "Environment". Without them everything else runs, only slower.
On Windows set `PYTHONIOENCODING=utf-8` before running scripts that print audit tables.

## Bracket in one command

```bash
python scripts/bracket_day.py <part.step> --setup studies/final_2026/ansys/official_2026-11-05/setup/setup_official_fixed_bores.json --case day1
```

Output goes to `studies/final_2026/ansys/out/<case>/` (`report.md`, `result.json`, figures, MatML material cards,
eco audit, Ansys cross-check template).
