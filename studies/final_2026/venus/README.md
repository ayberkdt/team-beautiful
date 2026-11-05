# studies/final_2026/venus — VESPER (LuGus "Fly on Venus", final 2026)

Owner: the Venus session (see `docs/21_final_challenges_coordination.md`). Main document: `docs/25_lugus_venus_rotorcraft.md`.

| File | What | Produced by |
|---|---|---|
| `design.json` | **hand-off to the 3-D visual** (schema `venus_rotorcraft_design/1`): atmosphere 30–80 km with bands and solar fraction, operating band, rotor/body/solar geometry, 13 labelled components (position, size, mass, material, colour, label), stowed envelope, entry + deployment sequence (altitude, time), mission events and hourly series | `python scripts/venus_design.py` (also run by `venus_day.py --final`) |
| `versions/` | every previous `design.json`, anchored before overwrite (name = version + hash) | same |
| `out/result.json`, `out/result.md` | all computed numbers (vehicle, entry, mission, link, hybrid, BEMT validation, risks) | `python scripts/venus_day.py --final` |
| `out/F1…F15.{png,pdf}` + `*.denetim.txt` | audited slide figures (datawiz, `sunum-tam`); set contract `vesper.seti.json`, consistency `vesper.tutarlilik.txt` | same |
| `out/trade_sizing.json` | 72 closed designs (rotor diameter × tip speed × solar option) | `python scripts/venus_trade.py` (~8 min) |
| `out_variant_*/`, `design_variant_*.json` | what-if runs with mentor numbers (`--payload-kg`, `--cruise-km`, `--rotor-d`); never overwrite the baseline files | `python scripts/venus_day.py --final --payload-kg 5` |
| `out/sensitivity.json` | one-at-a-time sensitivity (19 closed designs re-flown) | `python scripts/venus_sensitivity.py` (~6 min) |
| `sim_params.json` (+ `sim_params_README.md`) | **simulator parameters for LuGus**: atmosphere/wind/solar table 30–80 km, rotor curve, mass/inertia, limits, failure modes, deployment replay, mission series; every value with unit, tag and source | `python scripts/venus_sim_params.py` |
| `out/crosscheck.json`, `.md` | headline numbers re-derived by simpler methods (momentum theory + FM range, top-down mass fraction, hand energy balance) | `python scripts/venus_crosscheck.py` |
| `out/entry_validation.json`, `.md` | entry model vs 12 historical Venus entries + DAVINCI | `python scripts/venus_entry_validation.py` |

Stable contract for the visual: ids and keys do not change between versions; numbers may. Units SI; frame: origin at
the body centre, x forward between arms 1 and 6, y left, z up, hover with arms deployed. Tags on every block:
`D` read from primary data in this session, `D-ag` read by a research agent, `K` computed, `Y` assumption.
