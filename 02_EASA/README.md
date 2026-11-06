# 02_EASA — canopy alert system retrofit (Extra NG)

Everything for this challenge is in this folder. Shared library: `src/aerokit/canopy/` (fault tree, FMEA, sensors,
logic, Monte Carlo); tests: `tests/test_canopy.py`, `tests/test_canopy_day.py`. Pre-reveal prediction ("Accident
Investigation", doc 17): `prev_guess/02_EASA/`. Task note: `00_Common/organiser_notes/03_EASA_Canopy_Alert_Retrofit.md`.

| Folder | What |
|---|---|
| `official_2026-11-05/` | **official task** (task sheet docx + EASA case-study pptx, sha256) and `00_OFFICIAL_TASK_vs_KIT.md` — read first |
| `figures_src/` → `outputs/figures/` | **report figures in the sunumatik style** (F1a/F1b phase and type, F2 architecture, F3 process, F4 risk reduction, F5 wiring, F6 sensor locations, F7 compliance sweep, F8 take-off timeline): `python 02_EASA/figures_src/build_figures.py` renders them in headless Chrome at 3× and audits overlaps, overflow and clipping |
| `docs/29_extra_ng_design_basis.md` | **Extra NG design basis**: canopy hardware and operation, placard SB, cockpit (G3X, GMA 245R, 14 V, throttle ELOS), event pattern, physics of not-locked detection, seven-option sensing trade-off (incl. the bolt-contact idea), measurements needed; research `research/R9_*.md` |
| `docs/28_retrofit_installation.md` | **installation procedure**: mechanical and electrical installation, cockpit integration, phase logic, tolerance limits, ground acceptance tests G1–G17; figures `outputs/install/` from `scripts/easa_install.py` |
| `docs/27_design_catalogue.md` | **design catalogue**: where to sense per latch type, take-off time budget and timing requirements, mechanical-interlock verdicts (incl. the key-flap idea), cheap → expensive cost tiers with model results; research `research/R8_*.md` |
| `docs/26_feedback_design_tradeoffs.md` | **designs and trade-offs of the feedback elements** (light, voice, vibration, gate, engine shut-down, sensing); numbers from `scripts/easa_tradeoffs.py` → `outputs/tradeoffs/` (inputs `inputs/cues.json`, research `research/R7_*.md`) |
| `docs/` | `23_easa_canopy_retrofit.md` (main document, Friday checklist first), `retrofit_plan.md`, `glossary.md` |
| `inputs/` | `inputs.json` — every number the day command uses |
| `research/` | `00_INDEX.md` first; `R0_*` primary sources (AAIB G-MIIL, EASA AD 2025-0156, …), `R1`–`R6` topic notes, occurrence tables (`R2_occurrences.csv`, `R5_occurrences_add.csv`), evidence audit |
| `kit/` | **day kit** — start at `kit/00_KIT_INDEX.md`: mentor decision tree, 4:00 talk, 5-page report draft, traceability, AFMS, ICA task cards, BOM, any-aircraft study, concept trade |
| `scripts/` | `canopy_day.py` — the day command; `easa_kit.py` — kit tables, figures K1–K4 and checks; `easa_tradeoffs.py`; `easa_install.py`; `easa_deck.py` — the deck; `easa_report_docx.py` — the Word report |
| **`submission/`** | **what we hand in: the Word report `Team_Beetiful_EASA_Report.docx` (+ PDF) and the 4:00 deck** — see `submission/README.md` |
| `outputs/` | generated results, one folder per script (`day/`, `kit/`, `tradeoffs/`, `install/`, `mockups/`) — see `outputs/00_INDEX.md` |

Run (from the project root):

```powershell
$env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json      # -> 02_EASA/outputs/day/
python 02_EASA/scripts/easa_tradeoffs.py                              # -> 02_EASA/outputs/tradeoffs/
python 02_EASA/scripts/easa_kit.py                                    # -> 02_EASA/kit/, 02_EASA/outputs/kit/
python -I 02_EASA/scripts/easa_deck.py                                # -> 02_EASA/submission/ (deck)
python -I 02_EASA/scripts/easa_report_docx.py                         # -> 02_EASA/submission/ (Word report + PDF)
```

The talk is **4:00 with a hard cut** (`Rules and Criteria.xlsx`): use `kit/02_talk_4min.md`, not the 7-minute slide plan
in doc 23 §7.
