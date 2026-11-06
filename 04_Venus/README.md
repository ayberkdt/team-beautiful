# 04_Venus — VESPER (LuGus "Fly on Venus", final 2026)

Everything for this challenge is in this folder; the shared library is `src/aerokit/venus/` + `src/aerokit/venus_flight.py`
(tests: `tests/test_venus_*.py`). Pre-reveal predictions ("Drones on Venus", doc 19): `prev_guess/04_Venus/`.

| Folder | What |
|---|---|
| `docs/` | `25_lugus_venus_rotorcraft.md` — the main document |
| `research/` | source notes (`R_*` read, `K_*` computed checks), jury questions |
| `scripts/` | `venus_*.py` (day command: `python 04_Venus/scripts/venus_day.py --final`) |
| `outputs/` | every generated file, listed below (paths relative to `outputs/`) |

Owner: the Venus session (see `00_Common/docs/21_final_challenges_coordination.md`).

| File | What | Produced by |
|---|---|---|
| `design.json` | **hand-off to the 3-D visual** (schema `venus_rotorcraft_design/1`): atmosphere 30–80 km with bands and solar fraction, operating band, rotor/body/solar geometry, 13 labelled components (position, size, mass, material, colour, label), stowed envelope, entry + deployment sequence (altitude, time), mission events and hourly series | `python 04_Venus/scripts/venus_design.py` (also run by `venus_day.py --final`) |
| `versions/` | every previous `design.json`, anchored before overwrite (name = version + hash) | same |
| `result.json`, `result.md` | all computed numbers (vehicle, entry, mission, link, hybrid, BEMT validation, risks) | `python 04_Venus/scripts/venus_day.py --final` |
| `F1…F15.{png,pdf}` + `*.denetim.txt` | audited slide figures (datawiz, `sunum-tam`); set contract `vesper.seti.json`, consistency `vesper.tutarlilik.txt` | same |
| `trade_sizing.json` | 72 closed designs (rotor diameter × tip speed × solar option) | `python 04_Venus/scripts/venus_trade.py` (~8 min) |
| `variants/out_variant_*/`, `variants/design_variant_*.json` | what-if runs with mentor numbers (`--payload-kg`, `--cruise-km`, `--rotor-d`); never overwrite the baseline files | `python 04_Venus/scripts/venus_day.py --final --payload-kg 5` |
| `variants/budget_update/` | 6 Nov budget: rotor–rotor interaction, VEGA gust time scale, flyable descent, closed-design options (`result.json`, `result.md`, B1–B3, `sim_runs/`) | `python 04_Venus/scripts/venus_budget_update.py` (~13 min; reads `guc_egrisi.json`) |
| `sensitivity.json` | one-at-a-time sensitivity (19 closed designs re-flown) | `python 04_Venus/scripts/venus_sensitivity.py` (~6 min) |
| `sim_params.json` (+ `sim_params_README.md`) | **simulator parameters for LuGus**: atmosphere/wind/solar table 30–80 km, rotor curve, mass/inertia, limits, failure modes, deployment replay, mission series; every value with unit, tag and source | `python 04_Venus/scripts/venus_sim_params.py` |
| `crosscheck.json`, `.md` | headline numbers re-derived by simpler methods (momentum theory + FM range, top-down mass fraction, hand energy balance) | `python 04_Venus/scripts/venus_crosscheck.py` |
| `entry_validation.json`, `.md` | entry model vs 12 historical Venus entries + DAVINCI | `python 04_Venus/scripts/venus_entry_validation.py` |

Stable contract for the visual: ids and keys do not change between versions; numbers may. Units SI; frame: origin at
the body centre, x forward between arms 1 and 6, y left, z up, hover with arms deployed. Tags on every block:
`D` read from primary data in this session, `D-ag` read by a research agent, `K` computed, `Y` assumption.
