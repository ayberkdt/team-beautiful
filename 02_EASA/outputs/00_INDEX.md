# 02_EASA/outputs — what is here and who makes it

**The report and the deck are not here:** they are in `../submission/` (what we hand in).
Everything in this folder is generated; rerun the script, do not edit by hand. One sub-folder per script:

| Folder | Made by (from the project root) | Contents | Used in |
|---|---|---|---|
| `day/` | `python 02_EASA/scripts/canopy_day.py 02_EASA/inputs/inputs.json` | Monte Carlo sensing study: `analysis.md` (full write-up, was `report.md`), `result.json`, figures `C1`–`C6`, `fault_demo.html` | report Figure 1 = `C5` + `C6`; deck `C1`, `C3`, `C5` |
| `kit/` | `python 02_EASA/scripts/easa_kit.py` | figures `K1`–`K4` (concept ladder, any-aircraft latch points, 12-step process, architecture) | report Figure 2 = `K4`, Figure 3 = `K3`; deck |
| `tradeoffs/` | `python 02_EASA/scripts/easa_tradeoffs.py` | feedback-element trade-off: `tradeoffs.md` / `.json` (all tables), figures `T1`–`T3` | report §5 numbers and Figure 4 = `T1` |
| `install/` | `python 02_EASA/scripts/easa_install.py` | retrofit installation figures `E1` (electrical schematic), `M1` (sensor locations) for `docs/28` | not yet in the report |
| `mockups/` | hand-made | `annunciator_mockup.html` + its UX audit | backup / Q&A |

Each figure comes as `.png` (for Word and PowerPoint) and `.pdf`, with its datawiz audit `*.denetim.txt` (must say 0 HATA).
Set files `*.seti.json` and `*.tutarlilik.txt` keep colours and axes consistent within a folder.

Order after an input change: `canopy_day.py` → `easa_tradeoffs.py` → `easa_kit.py` → `easa_deck.py` →
`easa_report_docx.py` (the last two read from here).
