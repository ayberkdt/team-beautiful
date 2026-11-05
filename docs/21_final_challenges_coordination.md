# 21 · Final challenges (real notes, 4 Nov 2026) — parallel work rules

Source of the task notes: the user's six files in `C:\Users\ayber\Downloads\` (`01_Ansys_Bracket_Redesign.md`,
`02_Advionics_Automated_Approach_Guidance.md`, `03_EASA_Canopy_Alert_Retrofit.md`, `04_LuGus_Venus_Rotorcraft.md`,
`05_Cross_Challenge_Comparison.md`, `Tum_Gorevler_Detayli.md`). They are transcriptions of handwritten notes, **not the
official challenge text**. Copies for the sessions: `research_notes/final_2026_notes/` (read-only).

Work runs in parallel sessions until **23:00 GMT+1 on 4 Nov 2026 = 01:00 on 5 Nov in the laptop's clock (UTC+3)**.

## 1. Disk: C: is full (2.3 GB free on 4 Nov 15:55)

Nothing new may land on C:. In **every** shell command that can write temporary files set, for your own task folder:

```powershell
$env:TEMP="D:\tmp_ideathon\<task>"; $env:TMP=$env:TEMP; $env:MPLCONFIGDIR="$env:TEMP\mpl"; $env:PIP_CACHE_DIR="D:\tmp_ideathon\pipcache"; $env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
```

```bash
export TEMP="D:/tmp_ideathon/<task>" TMP="D:/tmp_ideathon/<task>" MPLCONFIGDIR="D:/tmp_ideathon/<task>/mpl" PIP_CACHE_DIR="D:/tmp_ideathon/pipcache" PYTHONPATH=src PYTHONIOENCODING=utf-8
```

`<task>` = `ansys`, `easa`, `advionics`, `venus`, `film`, `visual`. pytest: add `--basetemp=D:/tmp_ideathon/<task>/pytest`
and `-p no:cacheprovider`. Python lives on C:; a new package goes **only** to `D:\tmp_ideathon\pylib` (`pip install
--target D:\tmp_ideathon\pylib <pkg>`, then add it to `PYTHONPATH`), well-known PyPI packages only, and is listed in
your doc's "Environment" section. Node packages: inside the project folder on D:.

## 2. File ownership (this folder is not a git repo: two writers on one file = lost work)

| Session | Owns (create/edit freely) | Must not edit |
|---|---|---|
| Ansys bracket | `src/aerokit/bracket/` (new), `src/aerokit/materials/**`, `src/aerokit/optimization/**`, `src/aerokit/fem/**`, `src/aerokit/design/card*.py`, `scripts/bracket_*.py`, `scripts/card_day.py`, `studies/final_2026/ansys/`, `studies/cards/`, `docs/22_*.md`, `tests/test_bracket*.py` + tests of the modules it owns, `src/aerokit/references/_task_bracket.py` | everything else |
| EASA canopy | `src/aerokit/canopy/` (new), `scripts/canopy_*.py`, `studies/final_2026/easa/`, `research_notes/EASA kanopi/`, `docs/23_*.md`, `tests/test_canopy*.py`, `src/aerokit/references/_task_canopy.py` | everything else (`investigation.py` read-only) |
| Advionics comms/ATC | `src/aerokit/atc/` (new), `scripts/atc_*.py`, `studies/final_2026/advionics/`, `research_notes/Advionics ATC/`, `docs/24_*.md`, `tests/test_atc*.py`, `src/aerokit/references/_task_atc.py` | everything else (`approach.py`, `autoland.py`, `comms/` read-only) |
| Venus rotorcraft | `src/aerokit/venus/` (new), `src/aerokit/planetary.py`, `src/aerokit/venus_flight.py`, `scripts/venus_*.py`, `studies/final_2026/venus/`, `studies/cards_2026/venus*`, `research_notes/Venus rotorcraft/`, `docs/25_*.md`, `tests/test_venus*.py`, `tests/test_planetary.py`, `src/aerokit/references/_task_venus2.py` | everything else |
| Coordinator (this session) | this file, `README.md`, `docs/20_*.md`, `src/aerokit/references/__init__.py`, shared test infra | — |

Shared rules:
- `docs/references.md` is generated: after adding references run `python scripts/build_references.py` (deterministic; any session may run it, last run wins and includes every module).
- Hand-off between sessions is by **files**: the Ansys session writes `studies/final_2026/ansys/handoff/` for the film; the Venus session writes `studies/final_2026/venus/design.json` for the visual.
- Before overwriting an existing file you own, copy the old version to `D:\tmp_ideathon\<task>\anchor\` (user rule: anchor before overwrite).

## 3. User rules every session follows (from the user's CLAUDE.md)

- No fact stated without reading its source **in your session**; otherwise write "not verified". Cite file/command/URL with every number.
- Mark every value: `[D]` read from a primary source by you, `[D-ag]` read by a subagent, `[K]` computed here (with the command), `[Y]` our judgement / assumption.
- Any figure/plot/table → `datawiz` skill (FİGÜR BRİFİ first, `dw.kaydet` audit with 0 HATA, look at the PNG). Any visible surface (HTML, CLI output, slide) → `ux-yasalari` skill (GÖREV BÜTÇESİ first, 20-row YASA DENETİMİ before delivery).
- Expensive or irreversible work: verify from data first that it is needed.
- Never delete the user's files; never enter credentials.
- Run your own tests often; the full suite (`python -m pytest -q`) must stay green at the end.

## 4. Status log (coordinator)

| Local time (UTC+3) | Event |
|---|---|
| 4 Nov 15:55 | rules written; per-task reference modules `_task_bracket/_canopy/_atc/_venus2` registered (199 references, `build_references.py --check` up to date) |
| 4 Nov ~16:10 | six sessions started: `ansys-bracket`, `ansys-film` (cwd `D:\Video Simulations\Ideathon-2026-Ansys`), `easa-canopy`, `advionics-atc`, `venus-rotorcraft`, `venus-visual` (cwd `D:\Custom Yetenekler\sunumatik`, own worktree branch) |
| 4 Nov 21:04 | all six idle after round 1; docs 22–25 exist (22: 33 KB, 23: 22 KB, 24: 38 KB, 25: 35 KB); C: 3.8 GB free, D: 326.6 GB. Round 2 sent to every session (bracket: 3-D stress TO with projection + benchmark, multi-body STEP / material-list matching, hot fatigue, fake-Ansys cross-check rehearsal; film: TO evolution + cross-check scenes; EASA: free primary docs, wider occurrence catalogue, one example aircraft; Advionics: MTI/CFAR, Mode S test vectors, ASTERIX newer edition, degraded-voice demo; Venus: entry validation vs PV/Venera/Vega, deployment Monte Carlo, day-in-the-life, end-of-mission; visual: quality pass + mission-sequence). Stop time 00:45 |
| 4 Nov ~21:10 | full suite (coordinator, `-x`, temp on D:) reached 100 % with no failure, 1 skip (symlinks), 3779/3779 numerical checks; `references.md` was stale → regenerated (265 references, old copy `D:\tmp_ideathon\coord\references.md.bak-2110`), `--check` up to date |
| 4 Nov 21:45 | EASA round 2: example aircraft Extra NG (`retrofit_plan.md` l. 31), `canopy/faults.py` + `out/fault_demo.html` (ux checker exit 0), canopy tests 23 passed (coordinator re-run); occurrence widening (R5) in progress |
| 4 Nov 22:00 | film round 2: 4 MP4s present (`teslim/` sketch 21:23/21:32, `teslim/handoff_ge/` 21:44/21:54); film requests 13 (density snapshots) and 15 (cross-check) relayed to bracket; rule: fake-Ansys rehearsal goes to `studies/final_2026/ansys/rehearsal_crosscheck/`, never under hand-off names or in delivered films |
| 4 Nov 22:38 | round 2 checked: docs 22–25 updated 22:05–22:25; EASA R5 95 rows (all with URL) + R2 146; Venus `design.json` v0.6, 70 files in `venus/out`; ATC tests 160 passed / 3 skipped (coordinator re-run); bracket fake-Ansys rehearsal 4/4 planted errors caught (`out/sketch/ansys_rehearsal/summary.md`); rehearsal film apart in `teslim/prova_capraz_REHEARSAL/`, delivered films unchanged. Round 3 (evidence audit by fresh subagent + cross-checks) sent to EASA, Advionics, Venus |
| 4 Nov 23:03 | round 3 checked: audit files `R_audit_2026-11-04.md` in the three research folders (EASA 1.5 % field error rate; Advionics 8 match / 4 partial / 0 wrong; Venus 1 minor mismatch + 3 context errors in 15); `venus/sim_params.json` (75 KB); bracket hand-off has density snapshots; `stress3d` stays EXPERIMENTAL (doc 22 §4c, grey 9.5 % but verified rounds diverge). Round 4 sent: cold timed dry runs + doc consolidation + Friday checklists; visual final refresh. Stop 00:45 |
| 4 Nov 23:18 | film re-cut from the 22:52 hand-off: `teslim/ideathon-film-1080p-20261104-225711.mp4`, `…-4x5-20261104-230100.mp4`, `teslim/handoff_ge/…-230450.mp4`, `…-231125.mp4` (files present; shot 03 plays real density snapshots); Venus round 4 done (per-probe β, doc 25 consolidated, design.json v0.6 sha 03dbe848); visual final commit `e27e9cd` on `claude/venus-rotorcraft-visual-44d0d1` (verified with git log; not merged, not pushed) |
| 4 Nov 23:31 | round 4 reports: bracket cold dry run (new STEP + misspelled material CSV → all deliverables, one command, 16 min 45 s, `out/dryrun_cold/`); EASA cold run 21.2 s; docs 22/23/25 open with a Friday checklist, doc 24 with a decision card (checked with grep). Advionics' full run had 1 failure = FEM timing test that passes alone (suspected CPU load from parallel renders). Film final re-cut running until ~00:25. Coordinator final suite started 23:31 |
| 4 Nov 23:39 | coordinator full suite: **1960 passed, 1 skipped, 3790/3790 checks** (8 min 08 s, temp on D:; FEM timing test passed this time); `build_references.py --check` up to date |
| 4 Nov ~23:55 | film re-cut 23:26–23:36 after a cold dry run (`teslim/…-232603`, `…-232926`, `handoff_ge/…-233250`, `…-233601`; files present). Coordinator eye check of the 4:5 cut, frame 450 (shot 02 "300 °C"): title names Inconel 718 as best per kg but the orange highlight is the Ti-6Al-4V line, and end labels Inconel/Ti and Scalmalloy/steel are stacked so "134" and "20.7" are ambiguous → sent to the film session to fix and add a title-vs-highlight check |
| 4 Nov 23:58 | fix verified by eye on `teslim/ideathon-film-4x5-20261104-235159.mp4` frame 450: title "Inconel 718 and Ti-6Al-4V tie at about 134 kN·m/kg", every end label carries its value (134 / 134 / 105 / 22.5 / 20.7); phone copy sent to the user. Round 5 reports: jury/mentor sections added — doc 22 §11b, doc 23 §6b, doc 24 §15 (+ `atc/mlat.py`), doc 25 §7.2 |
| 5 Nov 00:02 | film: shot-02 fix in all four delivered films (Inconel 134.5 vs Ti 133.8 kN·m/kg → tie rule at 1 %); new film.mjs check (title names the highlighted series; end-label gap ≥ 1.2× font height). Delivered: `teslim/ideathon-film-1080p-20261104-234818.mp4`, `…-4x5-20261104-235159.mp4`, `handoff_ge/…-235523.mp4`, `…-235820.mp4`. Coordinator last suite started 00:03 |
| 5 Nov 00:09 | **final** coordinator suite: **1967 passed, 1 skipped, 3790/3790 checks** (6 min 55 s, temp on D:); `build_references.py --check` up to date. Night closed |
| 5 Nov 11:00 | user: today EASA + Ansys; the CAD will look like a hand sketch (oval plate, ~6–7 holes, two arches), saved as `studies/final_2026/ansys/inputs/organiser_sketch_2026-11-05.png`. User rule: **do not run the analysis now**. Bracket session asked for a parametric `sketch2` CAD + previews + setup/material proposals (geometry only, no FEA/topology); film session asked for framing/layout prep in a TEST folder only |
| 5 Nov 11:15 | **official Ansys files** (`Downloads\Files.zip`, sha256 53dd8d51…, moved) → `studies/final_2026/ansys/official_2026-11-05/` (owned by the coordinator: `files/`, `unpacked/`, `derived/`, `setup/`, `catalogue/`; other sessions read-only). Real CAD = plate 661×341×70 mm, 4 Ø60 bolt bores, 2 lugs with Ø60 pins, 152.29 kg S275N (facet volume; Discovery 152.27). Loads/BCs: `setup/boundary_conditions.md`; materials: S275N ref, Al 2618-T6, Ti-8Al-1Mo-1V (from the `.ces`). sketch2 superseded; bracket session told to pause |
| 5 Nov 11:25 | sketch2 ready, geometry only (4 variants `inputs/sketch2_{loop,loop_nohole,lug,lug_nohole}.*`, previews in `inputs/sketch2_prep/*/preview.png`, doc 22 §11c, 26 tests). Found `studies/final_2026/ansys/official_2026-11-05/` (Files.zip 11:13: `.dsco` CAD, challenge `.docx`, intro `.pptx`, `.ces`, `.prd`; `derived/initial_from_facets.stl`, `features.json`) written by the user's own session "Ansys challenge incelemesi" (local_7ee5e3e4…), not by a coordinated session. features.json: plate z = 100 mm, x 170–831, y 30–371 mm; two tilted lugs; Ø 59.96 mm pin bore at y ≈ 336 → real part ≈ 660 × 340 mm, much larger than sketch2. Asked the user before acting on it |
| 5 Nov 11:52 | film: official CAD PREVIEW (geometry + loads, no analysis) `teslim/official_cad_preview/…-1080p-20261105-115054.mp4`, `…-4x5-20261105-115109.mp4` (405 frames); coordinator eye check of frames 60 and 300: base plate with 4 bolt holes + two clevis lugs with pin bores, "S275N baseline: 152 kg", "4 fixed, 2 loaded (roles edited by hand)", footer "PREVIEW — geometry and loads only, no analysis"; 4:5 sent to the user. Bracket session paused (sketch2 superseded) |
