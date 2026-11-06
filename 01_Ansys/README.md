# 01_Ansys — aircraft bracket redesign (Ansys / Synopsys challenge)

Everything for this challenge is in this folder; the shared Python library is `src/aerokit/bracket/` (tests:
`tests/test_bracket_*.py`). Pre-reveal predictions for this challenge: `prev_guess/01_Ansys/`. Rules, scoring and
the report/deck templates: `00_Common/rules_and_templates/`.

| Folder | What |
|---|---|
| `docs/` | `22_ansys_bracket_final.md` — toolchain, validation, open questions |
| `inputs/` | rehearsal geometry and set-ups; organiser sketch (5 Nov); Synopsys introduction (**Do Not Share**) |
| `official_2026-11-05/` | organiser files (`files/`, `unpacked/`), derived geometry, set-ups, analysis scripts, runs, visuals (coordinator-owned) |
| `scripts/` | `bracket_*.py` day commands, `check_ansys_ready.ps1`, `free_c_for_ansys.ps1` |
| `outputs/` | `cases/<case>/`, `handoff/<case>/`, `material_selection/`, `validation/`, `rehearsal_crosscheck/` |
| `submission/` | report/deck drafts, `KARARLAR.md` decision log, `trade_off/`, `report_figs/`, `final_report/` (report docx + Ansys screenshots) |

Full description, validation and open items: `01_Ansys/docs/22_ansys_bracket_final.md`.

## On the day (organisers give a STEP / STL / drawing)

```powershell
$env:PYTHONPATH="src;D:\tmp_ideathon\pylib"; $env:TEMP="D:\tmp_ideathon\ansys"; $env:TMP=$env:TEMP
python 01_Ansys/scripts/bracket_day.py <their.step> --case day1 --handoff          # 1st run: proposes setup.json
#   edit 01_Ansys/outputs/cases/day1/setup.json  (hole roles, loads N / N m, temperature, criterion)
python 01_Ansys/scripts/bracket_day.py <their.step> --case day1 --handoff          # 2nd run: uses the edited set-up
python 01_Ansys/scripts/bracket_crosscheck.py 01_Ansys/outputs/cases/day1    # after the Ansys column is filled
```

Ansys produced its own optimised STL? `python 01_Ansys/scripts/bracket_day.py ansys_result.stl --unit mm --setup
01_Ansys/outputs/cases/day1/setup.json --case day1_ansys --evaluate-only` evaluates that shape with our set-up.

Only a dimensioned drawing? Write it as a drawing JSON (boxes, cylinders, prisms with `arc`s; `cut` cylinders are
holes) like `inputs/sketch_bracket.json` (generator: `01_Ansys/scripts/bracket_make_examples.py`). No loads given? add
`--calibrate 0.8`. In a hurry: `--quick` (≈ 5 min).

## Folders

| Path | What |
|---|---|
| `inputs/` | rehearsal geometry: `sketch_bracket.json` (invented, sketch-like), `ge_bracket.json` + `.step` (GE-type envelope), `ge_setup.json` (GE loads) |
| `outputs/cases/<case>/` | one run: `report.md`, `result.json`, `setup.json`, `cad/` (initial STEP/STL, optimised STL), `materials/` (MatML + cards), `eco_audit.*`, `crosscheck_template*.csv`, `figures/` (datawiz-audited), `study.pkl` (for `--report-only`) |
| `outputs/handoff/<case>/` | files for the film session in its input format (`girdi.json`, `result.json`, `yukler.json`, `yogunluk.json`, `parca.stl`, `gerilme.txt`) |
| `outputs/material_selection/` | geometry-independent material selection report, comparison CSV, MatML, cards, figure (`01_Ansys/scripts/bracket_material_report.py`) |
| `outputs/validation/` | validation table (`01_Ansys/scripts/bracket_validate.py [--slow]`) |

Rehearsal cases: `sketch` (loads calibrated so steel has utilisation 0.8), `ge` (GE/GrabCAD loads, AM overhang
filter; nothing passes at 300 °C on this sharp-edged envelope — an honest negative result), `ge_step` (same part
read from STEP with automatic hole detection and proposed loads, `--quick`).
