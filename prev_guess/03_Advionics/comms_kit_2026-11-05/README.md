# Advionics comms kit (4–5 Nov 2026), archived 6 Nov

Prepared before the official task was known, from the reading "voice to display, lost comms". The official task is
radar → correction → pilot cue, so this kit is no longer in `03_Advionics/`. Nothing was deleted.

- Cases 1, 2, 3, 5, 6, 7, 8, catalogues, triage tool and its keywords: `cases/`, `scripts/triage.py`
- Doc 24: `docs/`. Research notes: `research/`. Figures and old demos: `outputs/`, `templates/`
- `cases/_common.py` is a copy so these runners still run. Their tests stay in `tests/test_atc_cases.py`.
- `scripts/atc_*.py` still point at the old `03_Advionics` paths. They are not expected to run from here.

Undo the move, from the project root:

```powershell
python prev_guess/03_Advionics/comms_kit_2026-11-05/scripts/triage.py --undo prev_guess/03_Advionics/comms_kit_2026-11-05/manifest.json
```

Copy `scripts/triage.py` out of this folder first: it is itself in the manifest.
