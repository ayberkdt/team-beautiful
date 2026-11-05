# 09 · 2026 playbook — likely challenges and a 5-hour plan for each

Prepared 2026-10-25. Tags: **[D]** read from the source in this session · **[A]** read through a fetch summary ·
**[K]** run in this repository · **[Y]** judgement.

## 1. What the format forces [D: Regulations v1.1, 30/06/2026, §1.1, §1.3, §1.4; site checked 2026-10-25]

- Four challenges, one per competition slot; **every team does all four** and submits a conceptual solution for
  each. Challenges are revealed on the morning of 4 Nov.
- The preliminary schedule shows four competition blocks: 5 and 6 Nov, roughly 09:00–14:00 and 16:00–21:00 —
  **about five hours each** (read off the table; durations "not finalized").
- Team presentations on 7 Nov. Criteria: technical feasibility, innovation/creativity, **sustainability**,
  presentation quality (no weights). English only. BYOD; sponsors "may provide" licences.
- Sponsors and challenge topics for 2026 are **not published**.

Consequence [Y]: each slot is a self-contained sprint — read, assume, compute, check, present — with no time to
build tools. Everything below is ready to run.

## 2. What is likely, and why [Y, from the evidence in `08_past_challenges.md`]

| Family | Evidence | Likelihood [Y] | Ready in aerokit |
|---|---|---|---|
| F1 Conceptual aircraft design + mission | Ansys 2023 phase 1 card [D] | high if Ansys returns (sponsor in 2023 and 2024 [A]) | `sizing design`, `sizing mission --optimize`, `sizing validate` |
| F2 UAV / drone / eVTOL (electric) | Ansys 2023 final used a UAS [A]; sustainability theme | medium–high | `aerokit.design.electric` (new) + `mission` coverage |
| F3 Digital mission engineering: satellites, visibility, links | Ansys 2023 final: GPS/Cospas-Sarsat visibility, relay, comms [A] | medium–high | `aerokit.orbits`, `aerokit.comms`, `comms.chain` |
| F4 Air traffic / airport operations + emissions | EUROCONTROL and İGA set 2024 challenges, theme sustainability [D brochure, A blog] | medium | `aerokit.operations` (new), `mission.geodesy`, `aero.performance`, ICAO CO₂ |
| F5 Health monitoring / predictive maintenance | GTD 2023 card [D] | medium | `aerokit.reliability` (new) |
| F6 Structures / CFD set-up (Ansys Mechanical, Fluent) | Ansys is a simulation vendor; no past card was CFD [D]. **1 Nov: the Synopsys introduction asks for structural FEA** [D doc 10] | ~~low–medium~~ **high (structures)** | `fem`, `mechanics`, `materials`, `aero flow`, docs 02–03 |
| **F7 Light-weighting: topology + material selection + eco audit** (added 1 Nov) | Synopsys introduction 27 Oct 2026, p. 12 skills and pp. 12–13 courses [D doc 10] | **high for the Ansys slot** | `fem topology`, `materials.selection`, `design.sustainability.lightweighting / eco_audit / payback_missions`; recipe in doc 10 §6 |

No 2026 sponsor is known; the host region is **not** used as evidence (no source read). Sustainability is a
criterion for every challenge, so every solution gets a sustainability slide with numbers (§5).

## 3. The five-hour slot (team of 3–5) [Y]

| Time | Whole team | Lead analyst | Second analyst | Presenter |
|---|---|---|---|---|
| 0:00–0:20 | read the card; requirement table **with units** (what is asked, what is judged) | — | — | slide skeleton (§6) |
| 0:20–0:45 | pick the family (§4), the method, and the 3–5 assumptions that matter | baseline run | find data for the assumptions | title, problem slide |
| 0:45–2:30 | — | main computation | sensitivity / alternative concept | figures as they arrive |
| 2:30–3:15 | — | sustainability numbers (§5) | sanity checks (units, limits, hand check) | results slides |
| 3:15–4:30 | — | answer questions from the presenter | risks and next steps | full deck |
| 4:30–5:00 | dry run, cut to the time limit, final unit check | | | |

Rules of thumb: a justified simple model beats an unfinished complex one (the 2023 card said so explicitly [D]);
every number on a slide has a source or an assumption tag; one sensitivity chart per challenge.

## 4. Recipes per family

### F1 Conceptual aircraft
Inputs: range, payload, speeds, ceiling, field lengths. Run
`python -m aerokit sizing design <req.json> --out-dir out` (units in the JSON; compliance, tornado, V-n,
payload-range; 3.3 s with `--no-figures` [K], the figures add their render time). Guards refuse jet classes and warn on Mach/power outliers (`07_gap_analysis.md` §7).
Validate the model against a real aircraft (`sizing validate`). Not available: jet sizing path (A4), stability.

### F2 Electric UAV / drone / eVTOL
`aerokit.design.electric`:
`battery_range(E*, η, L/D, m_b/m)`, `electric_takeoff_mass(payload, R, E*, η, L/D, m_e/m)` (with the zero-payload
range limit as an error message), `battery_endurance`, `hover_power(T, ρ, A, FM)`, `size_multirotor(...)`.
Technology values (E* pack Wh/kg, η, FM, m_e/m) are parameters: state and vary them (Hepperle's example: 180 Wh/kg,
70 %, L/D 30 [D]). Coverage of a search area: `sizing mission --optimize` with a polygon and wind.

### F3 Satellites, visibility, links
`aerokit.orbits`: `gps_baseline_24()`, `galileo_nominal_24()`, `geostationary`, `walker`, `circular`;
`visibility.count_in_view`, `access_windows`, `common_view`, `link_geometry`. `aerokit.comms`: `evaluate_link`
(EIRP → C/N0 → Eb/N0 → margin), ITU-R rain/gas for Earth–space paths, antennas, DVB-S2 MODCOD;
`comms.chain.evaluate_chain` for bent-pipe or regenerative relays. Statistics only — real-time positions need
TLE/SGP4 (not installed). Terrain is not modelled.

### F4 Air traffic and airports
`aerokit.operations`: `mm1/md1/mg1` (runway as a server; M/D/1 for fixed separations), `mmc` (stands, desks,
security lanes; Erlang C), `runway_capacity_per_hour(separations, mix)`, `peak_queue(demand, capacity)` for
overload hours (delay, max queue, when it clears), `co2_per_passenger_icao(...)` (ICAO CEC v8 [D]). Route lengths:
`mission.geodesy.inverse`; fuel of a flight: `aero.performance.range_and_endurance` / Breguet with stated L/D and
SFC. Not available: BADA aircraft performance, ICAO engine emission databank (NOx, LTO), contrail model.

### F5 Health monitoring / predictive maintenance
`aerokit.reliability`: `Weibull` (R, h, MTTF, B-life, conditional reliability), `fit_weibull(failures, censored)`
(right-censored MLE [D NIST §8.4.1.2]), `series/parallel/k_out_of_n_reliability`, `estimate_rul(t, health,
threshold, "linear"|"exponential")` with a bootstrap interval (measured coverage 85 % at a nominal 90 % [K]),
`synthetic_degradation(...)` for simulated run-to-failure data. Structure of an answer: what to monitor (sensors ↔
failure modes), health indicator, threshold, RUL, maintenance decision, cost/availability. Not available: machine
learning libraries (scikit-learn is not installed).

### F6 Structures / CFD set-up
`03_mechanical_constraints.md`, `02_fluids_constraints.md`; `aerokit mechanics wing/buckling/section`,
`materials allowable` (MIL-HDBK-5J), `fem solve`, `aero flow` (Re, y⁺, cell budget). Ansys licences are the
sponsor's to provide.

## 5. Sustainability numbers (every challenge)

- CO₂ = 3.16 kg per kg Jet-A (ICAO CEC v8; CORSIA Order 2021 art. 28(5)) [D] — tank-to-wake only.
- Per passenger: `operations.co2_per_passenger_icao`; per mission and per km²: `design.sustainability.emissions`.
- Levers to quantify, not just name: SAF blend × life-cycle factor (`saf_scenario`, factor is a parameter),
  battery or hybrid segment (`hybrid_loiter`, `design.electric`), lower delay/holding (`peak_queue` delay × fuel
  flow), predictive maintenance (fewer spare parts, fewer unscheduled flights).

## 6. Slide skeleton (8 slides) [Y]

1. Problem and what is judged (one line each criterion).
2. Requirements table (as given → units → what we optimise).
3. Concept and method (one diagram; why this model).
4. Assumptions table (value, source or "assumed", effect).
5. Results (one figure, one table; margins).
6. Sensitivity (tornado) and validation / hand check.
7. Sustainability (numbers from §5).
8. Risks, limits, next steps.

## 7. Before the event

1. Timed dry run of the 2023 Ansys card in 5 hours, slides included (`06_development_plan.md` §4).
2. One dry run per new family (F2, F4, F5) on an invented card, to time the recipes.
3. Install check on the event laptop: `python -m pytest -q` green; Ansys/STK licence status (`00_overview.md` §3).
