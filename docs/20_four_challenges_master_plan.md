# 20 · Four challenges, one plan — read this first on 4 November

Prepared 2026-11-03 after the organisers' spoiler. Docs 17–19 hold the detail for the three new sponsors; docs
10–16 for Ansys. Tags: **[D]** read from the source this session · **[D-ag]** read by a research agent this session
(notes in `research_notes/`) · **[K]** computed/run here · **[Y]** judgement.

> **Özet (TR).** Dört görev: Ansys (topoloji optimizasyonu), EASA (kaza soruşturması), Advionics (otomatik
> yaklaşma rehberliği), LuGus Studios (Venüs'te dronlar). Üç yeni sponsorun **kim olduğu doğrulandı** ve bu,
> görev tahminini değiştiriyor: Advionics bir RF/radar/IFF üreticisi (Oostkamp), LuGus bir drone simülasyon
> stüdyosu (Hasselt; NASA için Mars drone simülatörü yaptı), EASA soruşturmacı değil danışman/düzenleyici. Her
> biri için en olası görev, omurga cevap, sayılar ve 5 saatlik plan hazır. **Ansys için kurulum hâlâ engel**
> (bugün ölçüldü: Ansys Student kurulu değil, C:'de 5,1 GB boş). Açılış töreninde her sponsora sorulacak sorular §4'te.

## 1. Schedule as printed

Booklet p. 8 and Regulations §1.1 (both read as flattened PDF text, so the cell-to-day mapping can be off by one
block — confirm at the opening) [D]: 4 Nov welcome, meet & greet, speeches; **5 Nov and 6 Nov competition
(morning + afternoon blocks)**; 7 Nov team presentations; challenges revealed on 4 Nov. Synopsys wrote "See you on
November 5th" [D] → Ansys likely on 5 Nov [Y]. Each block is roughly 5 h [Y from the grid].

## 2. The four challenges at a glance

**Ansys (Synopsys) · Topology Optimization** — doc 10 (brief), 11 (side areas), 12 (five task scenarios), 13 (task
space), 14 (course playbook), 15 (materials), 16 (TO methods).
- Most likely: light, low-carbon aerospace bracket — topology optimisation in Discovery/Mechanical, material
  choice (performance indices), eco audit / life-cycle CO₂ [doc 10, from the sponsor deck p. 12].
- Day tool: `python scripts/card_day.py studies/cards/<card>.json` — **re-run today on the L-bracket rehearsal card
  in a scratch folder: exit 0, four options, three slide figures, set audit 0 errors** [K]. It crashed first on
  this laptop's console (code page 857 / Python cp1254 cannot print the audit's "→"); fixed in `card_day.py` by
  replacing unprintable characters. For every other script set `$env:PYTHONIOENCODING="utf-8"` first.
- **Blocker [K, measured 2026-11-03]**: Ansys Student is **not installed**; only the full 2023 R1 in `D:\ANSYS Inc\
  v231` (licence server at ITU, unreachable from here on 3 Nov per doc 10); **C: has 5.1 GB free** of 146 GB while
  Ansys Student asks for 50 GB [doc 10, D]; the GTX 1660 Ti (Turing) is not in Discovery's listed architectures.
  → Tonight: either free C: and install, or confirm another team laptop carries Ansys; ask Synopsys on 5 Nov about
  event licences and EduPack (doc 10 §7).

**EASA · Accident Investigation** — doc 17.
- EASA advises investigations (Reg. 996/2010 Art. 8), receives safety recommendations, runs ECCAIRS/ERCS/D4S/EPAS
  [D-ag]. Most likely: investigate a supplied scenario (timeline → barriers/HFACS → ERCS score → SMART SRs). Then:
  AI for precursors in occurrence data; locating wreckage/data faster.
- Rehearsal case solved in doc 17 §4: SAS43M, Brussels, 5 Feb 2026, take-off roll on taxiway E1, rejected at
  127 kt — facts read from the AAIU(Be) preliminary report [D].
- Tools: `aerokit.investigation` (track reconstruction, energy, debris ballistics, break-up location, search
  radius, FDM events, HFACS).

**Advionics · Automated Approach Guidance** — doc 18.
- Advionics NV (Oostkamp) designs and builds **RF, radar and IFF** equipment (L-IESA ship IFF array); no
  approach product of its own; sister company Intersoft flies ILS-measuring SkyRF drones [D, D-ag].
- Most likely: GNSS-independent approach guidance from a ground radar/transponder; UAS deck landing; jamming-
  resilient multi-sensor approach. Talk sensor physics + integrity.
- Tools: `aerokit.approach` (runway frame, deviations, wind, cold-temperature baro error, FSF stabilised gate,
  Monte Carlo approach simulator). Key computed result: at the 200 ft gate a 0.1° monopulse radar gives 1.9 m
  vertical P95 vs 2.8 m SBAS-like, while ISA−30 K pulls baro-VNAV ~5 m low [K].

**LuGus Studios · Drones on Venus** — doc 19.
- LuGus (Hasselt) makes the Liftoff drone simulator and built a **Mars Drone Simulator used for NASA analog
  training** [D]. Expect a simulation-ready design task, possibly a game/training brief.
- Key fact: at 55 km a quadrotor needs about Earth sea-level hover power (427 W vs 443 W for 5 kg on 0.5 m²) [K];
  helium lifts 0.84 kg/m³ there; winds 65–100 m/s; 2.3–14.3 min light delay.
- Tools: `aerokit.planetary`; simulator data file `studies/challenges_2026/venus_environment.json`.

## 3. Team routine for every slot [Y]

- **0:00–0:20 all**: read the card; requirement table with units; classify against the predicted P-list of that
  doc; one-sentence claim. Ask the sponsor mentor what they value most.
- **Roles**: lead analyst (main computation with our tools), second analyst (alternative concept + sensitivity +
  hand checks), sustainability owner (numbers, not adjectives), presenter (deck from minute 20).
- **Deck spine (8–10 slides)**: problem → requirement numbers → concept diagram → how it works / results →
  failure modes or sensitivity → regulation/certification fit → sustainability with numbers → roadmap/TRL →
  summary. Every number on a slide carries its source or "assumption".
- **Last 30 min**: rehearse, cut to time, check units, prepare 3 Q&A answers.

Sustainability that fits all four [Y]: simulation-first and digital methods cut hardware, travel and test flights;
quantify fuel/CO₂ (light-weighting fuel factor in doc 10; CDO 35 kg fuel per arrival [D-ag]; avoided search
hours); enabling technology for zero-emission aviation (investigation of battery/H₂ aircraft; drones replacing
helicopters; Venus as runaway-greenhouse science).

## 4. Questions to ask at the opening ceremony (4 Nov)

- **Ansys**: event licence or Student? Discovery on Turing GPUs? EduPack licence? Deliverables (slides only, or
  model files / eco-audit report)? Is AM in scope?
- **EASA**: is it a data pack to investigate or a concept to design? Who is the user — SIA, EASA, operator? Are
  SRs expected, and to whom?
- **Advionics**: manned aircraft or UAS? GNSS available or denied? Ground infrastructure allowed? Do they care
  most about the sensor hardware, the algorithms or the operational concept?
- **LuGus**: engineering concept, simulator content, or both? Target platform (Liftoff Core / Unity)? Should the
  deliverable include gameplay/training scenarios?

## 4a. Competition-day commands — one per sponsor (added 3 Nov evening) [K]

Each takes a JSON card (rehearsal cards in `studies/cards_2026/`), prints a report and a one-line result with the
next step, and writes `out/<card>/result.json`, `result.md` and three English slide figures (datawiz, sunum-tam,
every figure audited and eye-checked: 0 errors). Exit code 1 if any figure audit has an error. `--help` prints usage.
Copy the rehearsal card, change the numbers to the brief's, rerun.

| Slot | Command | What it answers | Rehearsal result |
|---|---|---|---|
| Ansys | `python scripts/card_day.py studies/cards/<card>.json` | topology options, mass, CO₂ | all six rehearsal cards run end to end (28–145 s each); new S3 card `rehearsal_pin_link.json` (two pins, three load cases): Scalmalloy 65 g / 7075 68 g at 50 %, Ti 74 g at 35 %, deflection governs (doc 12 §6) |
| Advionics | `python scripts/approach_day.py studies/cards_2026/approach_rehearsal.json` (~4 min measured, progress shown) | gate accuracy per sensor, protection levels vs LPV-200, spoof ramp vs dissimilar monitor, transponder link, **fused-navigation autoland with FDE** (`aerokit.autoland`) | 0.1° radar 1.9 m P95; spoof caught after 14 s at ~670 ft; autoland: solution-separation FDE lands 100 % with the spoofed GNSS excluded, innovation FDE lands 10 % (excludes the honest sensors) — doc 18 §5b |
| EASA | `python scripts/investigation_day.py studies/cards_2026/easa_rehearsal.json` | track reconstruction, gate states, energy excess, merged timeline, HFACS, ERCS, SRs | FICTIONAL pack: +320 ft and 171 kt GS at 1000 ft, threshold at 131 ft, touchdown 1142 m in, overrun 324 m; ERCS S1 RED |
| LuGus | `python scripts/venus_day.py studies/cards_2026/venus_rehearsal.json` | power to stay aloft vs altitude per concept, solar budget, station-keeping cost, simulator parameters, **time-stepped mission + `mission_replay.json`** (`aerokit.venus_flight`) | 10 kg: battery quad 1236 W, He-assisted quad 149 W, solar aeroplane 105 W at 55 km; holding station against 72 m/s costs 335 kW; dive mission 55→48→55 km: 3.3 h, 769 km drift, battery low 135/500 Wh, hull above 70 °C for 66 min — doc 19 §3b |

The EASA pack is generated by `python scripts/make_rehearsal_pack.py` and is **invented** (marked `fictional` in
the JSON and on every printed report). Running the merged timeline on it caught an inconsistency in the invented
pack itself ("cleared to land" after the aircraft had stopped) — exactly what the tool is for on the day.

New physics behind them (tested: `tests/test_approach.py`, `test_investigation.py`, `test_planetary.py`,
`test_day_tools.py`):
- `aerokit.approach`: `k_factor`/`protection_level` (K = Q⁻¹(P/2); 1e-7 → 5.33, Rippl & Perea 2018 read this
  session), `separation_threshold`, `fault_bound`, `ALERT_LIMITS`, `friis_received_power`, `thermal_noise_power`,
  `monopulse_angle_sigma` (k_m from a secondary source — assumption), and a sensor fault ramp + dissimilar monitor
  with detect-and-exclude in `simulate_approach`. Finding for the Advionics jury: a cooperative transponder reply
  gives > 50 dB SNR even at 10 NM, so **thermal noise is not the limit — calibration, multipath and bias are**.
- `aerokit.investigation`: `ercs_score` (EASA ERCS rules read this session through a fetch summary: weights
  5/2/3/2/3/1/1/1, score ⌈sum/2⌉, RED/YELLOW/GREEN, numerical equivalents), `accelerate_stop_distance`,
  `takeoff_acceleration_monitor` (erroneous take-off parameters / wrong-surface take-off).
- `aerokit.planetary`: `assisted_hover_power`, `envelope_drag_power`, `solar_power`, `venus_zonal_wind`,
  `venus_solar_fraction` (anchors now live in the module; `venus_environment.json` is byte-identical after the
  move).

## 4a-bis. Fastest Ansys route — no install, nothing deleted (found 4 Nov, 01:00) [D/K]

- **GPU settled** [K]: Ansys' own Discovery checker (`D:\ANSYS Inc\v231\Discovery\CudaCheck`, called through its
  .NET API without the window) returns **`AllDevicesCompatible`** for the GTX 1660 Ti (compute 7.5, 6 GB; CUDA
  runtime required 11.5, driver supports 13.1).
- **VPN ready** [K/D]: ITU gives students VPN through **GlobalProtect** ("Öğrencilerimiz GlobalProtect VPN üzerinden
  bağlantı sağlayabilmektedir", bidb.itu.edu.tr/hizmetler/vpn, read 4 Nov; reach: İTÜ/NET). GlobalProtect 6.2.0 is
  installed here, already set to portal `pvitu.itu.edu.tr`, service running. The licence server
  `lisanslar.cc.itu.edu.tr` (ports 1055/2325 in `ansyslmd.ini`) is unreachable without it.
- **Programs present** [K]: Discovery, SpaceClaim, Workbench, Mechanical 2023 R1 on D:.
- **So**: connect GlobalProtect with your ITU account (only you can sign in), then run
  `powershell -ExecutionPolicy Bypass -File scripts\check_ansys_ready.ps1` — it re-checks GPU, VPN, both licence
  ports and the programs, and prints "ready" or the first thing to fix. Not verified: that the student VPN routes to
  the licence server (the BIDB page says İTÜ/NET is reachable but does not list it) and that the licence pool has a
  free seat. Caveat: 2023 R1 is older than the event's release (menus may differ from doc 16 §2; additive and
  shape-optimisation modules failed to extract in 2024, doc 10).

## 4b. Ansys install: what is on C: (measured 3 Nov, 23:00) and the decision it needs

Measured [K, `Get-PSDrive`, recursive folder sums; nothing deleted or moved]: **C: 4.3 GB free** of 145.5 GB (it
was 5.1 GB in the morning); D: 333 GB free. Ansys Student needs **50 GB and "a physical C:/ drive"**; the official
install steps also say **"Uninstall any existing Ansys products"** before installing [D, ansys.synopsys.com student
page, read 3 Nov]. The page says nothing about installing to D:; one Ansys forum thread (2021) reports a "Critical
Error" when the install directory was on D:, not fixed by moving TEMP/TMP to D: [D, forum thread].

Largest folders under `C:\Users\ayber` (GB): `AppData\Roaming\.minecraft` 10.6 · `AppData\Local\Temp` 8.9 ·
`Documents` 8.4 · `AppData\Local\Programs` 9.9 · `AppData\Local\Packages` 7.0 · `Downloads` 4.6 · `.gemini` 3.9 ·
`AppData\Local\uv` 3.7 · `.codex` 3.7 · `.cache` 3.1 · `OneDrive` 2.4 · `.tudat` 2.1 · `AppData\Local\CrashDumps`
1.2. `.claude` (14.7 GB) holds this assistant's session history — leave it. `C:\ProgramData` 11.0, `C:\Program
Files` 14.5, `C:\Windows` 36.1.

A first rough estimate (all of Temp, all of `.cache`) suggested ~45 GB free without touching programs; the dry
run below, which keeps anything modified in the last 3 days, measures **~40 GB** — still short of 50. **This is the owner's call** (what may be deleted, what may move).

**Ready-made, dry-run by default:** `powershell -ExecutionPolicy Bypass -File scripts\free_c_for_ansys.ps1` lists
(deletes nothing); `-Apply` deletes only the safe group after a typed `Y`. Dry run measured at 23:40 [K]: safe group
**11.8 GB** (Claude Code temp folders of sessions older than 3 days 6.6 GB — this session's folder is always kept —,
uv cache 3.7, crash dumps 1.2, 1272 small temp items 0.3) → C: ~16 GB; plus moving `.minecraft`, Documents and
Downloads to D: by hand (23.6 GB) → **~40 GB**; plus Codex runtimes (`-IncludeOptional`, 2.7) → ~42 GB. The last
~8 GB need an uninstall or a vendor cache, all read-only measured and **not** in the script: NVIDIA App
`UpdateFramework` 4.4 GB and NVIDIA `Downloader` 1.4 GB (driver package caches — not verified safe to delete by
hand; clear from the NVIDIA App if it offers it), Docker Desktop 4.1 GB program + 1.8 GB data (uninstall from
Settings if unused). Python (7.0 GB) stays — the whole toolchain runs on it.

Other facts measured tonight [K/D, doc 10 table]: GTX 1660 Ti **meets the Discovery 2025 R2 minimum** (Maxwell or
newer, 4 GB) — the earlier "Turing unknown" is resolved for 2025 R2; the laptop runs Windows 11 **Home**, which the
Discovery page does not list (risk, not a known blocker); ITU licence server still unreachable; page file is already
on D:. Two faster alternatives:
another team laptop carries Ansys; or ask Synopsys on 5 Nov for an event machine/licence. Do not uninstall 2023 R1
(D:) before a working replacement exists, even though the installer page asks for it — that conflict is noted in
doc 10.

## 5. What was verified today, and what was not

Run here [K]: 1468 tests passed, 3545/3545 numerical checks; one test (`tests/orbits/test_two_body.py::
test_import_is_light`) fails because it starts a subprocess and `aerokit` is not pip-installed on this Python; it
passes with `PYTHONPATH=src` (environment, not code; `python -m pip install -e ".[plot,dev]"` from the README
removes it). New modules: `aerokit.planetary`, `aerokit.approach`, `aerokit.investigation` with 3 test files;
ruff and mypy clean on the package. Numbers for docs 17–19 come only from `scripts/challenges_2026_numbers.py`
(13 tables; `table_audit.txt` lists 0 errors, warnings only for intentionally wide-ranging columns).

Defects found and fixed while building this: RK4 instability for light fast debris (fixed, test added); simulator
lateral law used heading instead of ground track and an air-referenced path angle (fixed); `card_day.py` console
crash (fixed); a Monte Carlo table title that claimed the baro bias "dominates" when vision/INS was worse
(corrected); FSF speed window was first coded as −5/+10 kt, the FSF note says VREF to VREF + 20 kt (corrected from
the PDF).

Not verified by anyone: the four challenge texts themselves (only the one-line spoiler); jury members; VIRA primary
tables; several mission dates; Annex 13 primary text. Each doc ends with its own open items.
