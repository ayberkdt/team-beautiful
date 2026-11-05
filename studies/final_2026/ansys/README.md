# Ansys challenge — bracket redesign: working folder

Full description, validation and open items: `docs/22_ansys_bracket_final.md`.

## On the day (organisers give a STEP / STL / drawing)

```powershell
$env:PYTHONPATH="src;D:\tmp_ideathon\pylib"; $env:TEMP="D:\tmp_ideathon\ansys"; $env:TMP=$env:TEMP
python scripts/bracket_day.py <their.step> --case day1 --handoff          # 1st run: proposes setup.json
#   edit studies/final_2026/ansys/out/day1/setup.json  (hole roles, loads N / N m, temperature, criterion)
python scripts/bracket_day.py <their.step> --case day1 --handoff          # 2nd run: uses the edited set-up
python scripts/bracket_crosscheck.py studies/final_2026/ansys/out/day1    # after the Ansys column is filled
```

Ansys produced its own optimised STL? `python scripts/bracket_day.py ansys_result.stl --unit mm --setup
studies/final_2026/ansys/out/day1/setup.json --case day1_ansys --evaluate-only` evaluates that shape with our set-up.

Only a dimensioned drawing? Write it as a drawing JSON (boxes, cylinders, prisms with `arc`s; `cut` cylinders are
holes) like `inputs/sketch_bracket.json` (generator: `scripts/bracket_make_examples.py`). No loads given? add
`--calibrate 0.8`. In a hurry: `--quick` (≈ 5 min).

## Folders

| Path | What |
|---|---|
| `inputs/` | rehearsal geometry: `sketch_bracket.json` (invented, sketch-like), `ge_bracket.json` + `.step` (GE-type envelope), `ge_setup.json` (GE loads) |
| `out/<case>/` | one run: `report.md`, `result.json`, `setup.json`, `cad/` (initial STEP/STL, optimised STL), `materials/` (MatML + cards), `eco_audit.*`, `crosscheck_template*.csv`, `figures/` (datawiz-audited), `study.pkl` (for `--report-only`) |
| `handoff/<case>/` | files for the film session in its input format (`girdi.json`, `result.json`, `yukler.json`, `yogunluk.json`, `parca.stl`, `gerilme.txt`) |
| `material_selection/` | geometry-independent material selection report, comparison CSV, MatML, cards, figure (`scripts/bracket_material_report.py`) |
| `validation/` | validation table (`scripts/bracket_validate.py [--slow]`) |

Rehearsal cases: `sketch` (loads calibrated so steel has utilisation 0.8), `ge` (GE/GrabCAD loads, AM overhang
filter; nothing passes at 300 °C on this sharp-edged envelope — an honest negative result), `ge_step` (same part
read from STEP with automatic hole detection and proposed loads, `--quick`).
