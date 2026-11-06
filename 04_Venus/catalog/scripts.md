# Betik kataloğu: 18 Python dosyası, 5 klasör

Komutlar proje kökünden koşulur. Girdi ve çıktı adları aksi yazmıyorsa `04_Venus/outputs/` altındadır. Klasörler iş akışı sırasındadır. Klasör içinde sıra alfabetiktir, çünkü ad ile aranır.

## `code/pipeline/`

| Betik | Amaç (docstring) | Komut | Girdi | Çıktı |
|---|---|---|---|---|
| `final_compute.py` | VESPER numbers for ``venus_final``: BEMT validation set and the whole ``compute()`` chain. | doğrudan koşulmaz, `venus_final.py` çağırır | `trade_sizing.json`, `sensitivity.json`, `entry_validation.json` | bellekte sonuç sözlüğü |
| `final_figures.py` | Figures F1-F15 of ``venus_final`` (datawiz, audited on save); ``OUT`` is the folder they go to. | doğrudan koşulmaz, `venus_final.py` çağırır | sonuç sözlüğü | F1–F15 (`png`, `pdf`, `denetim.txt`, `dw.json`), `vesper.seti.json` |
| `final_report.py` | Markdown summary of the ``venus_final`` numbers (``result.md``). | doğrudan koşulmaz, `venus_final.py` çağırır | sonuç sözlüğü | `result.md` metni |
| `final_sim.py` | Flight-model parameters for ``venus_final`` (``vesper_for_simulator.json``); ``BASE`` is the baseline in use. | doğrudan koşulmaz, `venus_final.py` çağırır | sonuç sözlüğü | `vesper_for_simulator.json` içeriği |
| `venus_day.py` | Competition-day command for the LuGus slot: Venus concept card JSON → concept trade, simulator parameters and | `python 04_Venus/code/pipeline/venus_day.py --final` | `--final` ya da prova kartı (`prev_guess/04_Venus/cards/venus_rehearsal.json`) | `--final`: `venus_final.py` çıktıları. Kart: kartın yanında `out/<ad>/` |
| `venus_design.py` | Write ``04_Venus/outputs/design.json`` — the hand-off file for the 3-D visual session. | `python 04_Venus/code/pipeline/venus_design.py` | `aerokit.venus.design` | `design.json`, `versions/design_v*.json` |
| `venus_final.py` | LuGus final (4–5 Nov 2026): VESPER rotorcraft — numbers, audited figures and the design hand-off in one run. | `python 04_Venus/code/pipeline/venus_final.py` | `trade_sizing.json`, `sensitivity.json` | `result.json`, `result.md`, F1–F15, `vesper.seti.json`, `vesper.tutarlilik.txt`, `vesper_for_simulator.json`, `design.json`, `entry_validation.*` |
| `venus_sim_params.py` | Simulator-ready parameter file for LuGus (Liftoff Core / Unity): ``04_Venus/outputs/sim_params.json``. | `python 04_Venus/code/pipeline/venus_sim_params.py` | `vesper_for_simulator.json`, `aerokit.venus` | `sim_params.json` |

## `code/analysis/`

| Betik | Amaç (docstring) | Komut | Girdi | Çıktı |
|---|---|---|---|---|
| `venus_budget_update.py` | VESPER budget update, 6 Nov 2026: rotor-rotor interaction, the VEGA gust time scale and the flyable descent profile. | `python 04_Venus/code/analysis/venus_budget_update.py` | `guc_egrisi.json` (Sunumatik), `literature/data/venus_turbulence_model.json`, `sim_runs/sim_points.json` | `variants/budget_update/` (`result.json`, `result.md`, B1–B3) |
| `venus_crosscheck.py` | Independent cross-checks of VESPER's headline numbers with simpler methods (no BEMT, no simulation). | `python 04_Venus/code/analysis/venus_crosscheck.py` | `aerokit.venus` | `crosscheck.json`, `crosscheck.md` |
| `venus_entry_validation.py` | Entry-model validation against every historical Venus entry with published conditions. | `python 04_Venus/code/analysis/venus_entry_validation.py` | `aerokit.venus`, tarihsel giriş tablosu (betiğin içinde) | `entry_validation.json`, `entry_validation.md` |
| `venus_sensitivity.py` | One-at-a-time sensitivity of the VESPER baseline (D 2.6 m, tip speed 70 m/s, 55 km) and of the lighter 2.3 m point. | `python 04_Venus/code/analysis/venus_sensitivity.py` | `aerokit.venus` | `sensitivity.json` |
| `venus_trade.py` | Design-space sweep of the VESPER hexacopter: rotor diameter × hover tip speed × solar option. | `python 04_Venus/code/analysis/venus_trade.py` | `aerokit.venus.sizing` | `trade_sizing.json` |

## `code/data/`

| Betik | Amaç (docstring) | Komut | Girdi | Çıktı |
|---|---|---|---|---|
| `venus_pds_extract.py` | Extract Pioneer Venus probe profiles from the raw PDS4 files into ``src/aerokit/venus/data/pv_profiles.json``. | `python -I 04_Venus/code/data/venus_pds_extract.py <indirilenler>/atmo` | ham Pioneer Venus PDS tabloları | `src/aerokit/venus/data/pv_profiles.json` |

## `code/variants/`

| Betik | Amaç (docstring) | Komut | Girdi | Çıktı |
|---|---|---|---|---|
| `venus_short_demo.py` | Short technology-demonstrator variant: no science payload, no dives, one short daylight mission. | `python 04_Venus/code/variants/venus_short_demo.py` | `guc_egrisi.json`, `variants/budget_update/result.json` | `variants/short_demo/` |
| `venus_short_demo_files.py` | Design and simulator files for the 0.5 kg short demonstrator. Variant only: the baseline in ``outputs/`` does not change. | `python 04_Venus/code/variants/venus_short_demo_files.py` | `guc_egrisi.json`, `venus_variant_v07.py` | `variants/short_demo/files_0p5kg/` |
| `venus_variant_v07.py` | VESPER v0.7 variant: the recommended 44.63 kg design as VARIANT files. The baseline stays v0.6 until the user says yes. | `python 04_Venus/code/variants/venus_variant_v07.py` | `variants/budget_update/`, `outputs/` tabanı | `variants/v0_7_44p6kg/` |

## `code/catalog/`

| Betik | Amaç (docstring) | Komut | Girdi | Çıktı |
|---|---|---|---|---|
| `build_catalog.py` | Write the 04_Venus catalogues (components, figures, scripts, literature, data files) from the files on disk. | `python 04_Venus/code/catalog/build_catalog.py` | `outputs/`, `docs/25*.md`, `literature/`, `reviews/`, `code/` | `catalog/` içindeki üretilmiş dosyalar |
