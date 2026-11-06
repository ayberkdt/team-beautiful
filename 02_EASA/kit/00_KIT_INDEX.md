# EASA day kit — pieces to assemble on the day

**Official task received 5 Nov ~16:30:** read `../official_2026-11-05/00_OFFICIAL_TASK_vs_KIT.md` first (certification
disregarded; feedback elements incl. vibration and engine shut-down; EASA's own view that G-MIIL was not properly locked).

Each piece stands on its own; pick them with `01_mentor_branches.md` once the mentor has answered. Generated pieces
come from one command and are never edited by hand:

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json     # ~21 s: C1–C6, report.md, result.json, fault demo
python 02_EASA/scripts/easa_kit.py                                  # ~10 s: kit tables 04/07/08/11 + figures K1–K4 + checks
python -I 02_EASA/scripts/easa_deck.py                              # ~5 s: the 4:00 deck (.pptx) -> 02_EASA/submission/
python -I 02_EASA/scripts/easa_report_docx.py                       # ~40 s: piece 03 -> Word report + PDF in 02_EASA/submission/
python -m pytest -q tests/test_canopy.py tests/test_canopy_day.py tests/test_easa_kit.py
```

| # | Piece | What it gives you | Made by | Criterion |
|---|---|---|---|---|
| 01 | `01_mentor_branches.md` | mentor answer → which pieces, first 20 minutes | hand | — |
| 02 | `02_talk_4min.md` | **4:00 talk**: 6 slides, timed script for 4 speakers, backup slides (doc 23 §7 was 7 min); updated to the official task 5 Nov | hand; timing checked by `easa_kit.py` | P1–P4 |
| 03 | `03_report_draft.md` | 5-page report text mapped to R1–R6, figure captions, references | hand; word count checked | R1–R6 |
| 04 | `04_traceability.md` / `.csv` | R-1…R-14 → hazards → design → verification → basis | `easa_kit.py` | R2, R3, R6 |
| 05 | `05_afms_draft.md` | flight-manual supplement + A6 pilot checklist card | hand | R5 |
| 06 | `06_ica_task_cards.md` | six maintenance tasks incl. go/no-go gauge and the bond inspection (AAIB cause) | hand | R3, R5 |
| 07 | `07_bom_budget.md` | parts incl. shaker and gate, mass 530–985 g, power 1.76 W continuous vs R-10 (≤ 1 kg) | `easa_kit.py` | R3 |
| 08 | `08_other_aircraft.md` | "any aircraft": 1–5 latch points, one sensor per point needed [K] | `easa_kit.py` | R1, R4 |
| 12 | `12_feedback_matrix.md` | **official task's feedback elements**: visual, auditory, throttle-knob vibration, ground-only take-off gate; engine shut-down rejected; G1000 vs standalone variant; the organisers' microswitch example as level 1 | hand | R2, R4 |
| 11 | `11_concept_trade.md` | A1–A4, B, C side by side: 1 900× vs 3×; C keeps 6× | `easa_kit.py` | R2, R4 |
| D | `../submission/EASA_LOCK-SENSE_4min.pptx` | **the 4:00 deck** from the organisers' template: cover + 6 slides, speaker notes = talk 02; UX audit `../submission/EASA_LOCK-SENSE_4min.ux_denetim.md` | `easa_deck.py` | P1–P4 |
| K1 | `../outputs/kit/K1_concept_ladder.png` | slide 6 / backup: alert-only options collapse under distrust | `easa_kit.py` (datawiz 0 HATA) | P3 |
| K2 | `../outputs/kit/K2_any_aircraft_latch_points.png` | backup for mentor Q2 | same | P3 |
| K3 | `../outputs/kit/K3_retrofit_process.png` | slide 5: twelve steps in four blocks, a test after each (no approval gates) | same | P3, R2 |
| K4 | `../outputs/kit/K4_lock_sense_architecture.png` | slide 3: architecture, four sensors → four cues + G1000 | same | P3, R2 |

Existing pieces this kit builds on: `../docs/23_easa_canopy_retrofit.md` (findings, jury questions §6b),
`../docs/retrofit_plan.md` (the 12 steps), `../docs/glossary.md` (word list), `../outputs/` (see `../outputs/00_INDEX.md`:
`day/` C1–C6 and fault demo, `tradeoffs/`, `install/`, `mockups/`), `../research/00_INDEX.md` (sources).

Report docx: `../submission/Team_Beetiful_EASA_Report.docx` (+ PDF), built from piece 03 by
`02_EASA/scripts/easa_report_docx.py` into the organisers' template; it checks the §5 numbers against
`outputs/tradeoffs/tradeoffs.json` and the 5-page body limit.
