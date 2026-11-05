# 07 · Gap analysis — what to add, what to strengthen

Prepared 2026-10-25, after P0–P1 of `06_development_plan.md` were implemented. Every finding below
comes from a command run on 2026-10-25; the command and its saved output are named next to it.
Tags: **[K]** measured by running the code · **[D]** read from the source document · **[Y]** judgement.

Scratch outputs (not part of the repository):
`%TEMP%\claude\D--Masaustu-Ideathon-2026\e8cfd731-d966-4b5e-94b2-b431befe411d\scratchpad\gap\`
(`stress.txt`, `extreme.txt`, `pytest_cov.txt`, `cov.json`).

---

## 1. Physics gaps in the design pipeline (highest risk)

Found by re-running `aerokit.design.pipeline.run` on changed requirements (`stress.py`, `extreme.py`) [K].

| # | Finding | Evidence | Why it matters |
|---|---|---|---|
| G1 | **Installed power does not feed back into weight.** We/W0 comes from the Raymer W0 regression only and the fuel fraction from Breguet with a fixed PSFC; neither sees the installed power. | Vmax 500 → 900 km/h: P 1667 → 9259 kW, **W0 stays 5974 kg**, 8/8 pass, no warning. Ceiling 18 000 m: 10 189 kW at 5974 kg. Stall 60 km/h: S 172 m², still 5974 kg. | A jury question "what if Vmax were higher?" gets a physically wrong answer with a green compliance table. |
| G2 | **`aircraft_type` changes only the empty-weight regression.** The chain always uses the propeller Breguet equations and a `Turboprop` engine; a `Turbofan` class exists in `aero.propulsion` but `design.sizing.size` never uses it. | `aircraft_type: "jet transport"`, Vmax 800 km/h at 10 km → sized as a 6462 kW *turboprop*, 8/8 pass. | A 2026 task about a jet (business jet, UAV with turbofan) cannot be done with the pipeline, and it fails silently instead of refusing. |
| G3 | **Landing distance is checked but not a sizing constraint.** | `landing_distance: "600 m"` → design unchanged, compliance 8/9, landing −10 %. The pipeline reports the failure but does not resize W/S. | The constraint diagram misses a standard line (Raymer Ch. 5); the user must iterate by hand. |
| G4 | **No validity-range guard on regressions and models.** | 20 kg cargo, no crew: W0 157 kg from the *twin turboprop* We/W0 regression; 900 km/h turboprop accepted (flight Mach ≈ 0.73, no propeller-Mach check). | Extrapolation outside the regression data and outside the propeller regime is not flagged. |
| G5 | **Wing loading is always the stall limit.** The design point is W/S = stall line, P/W = maximum of the constraints at that W/S. `sizing point` searches the diagram but is not used by `sizing design`. | `src/aerokit/design/sizing.py:127` (`WS = rs.ws_stall(...)`). | Fine for the 2023 card (stall governs W/S), but not a minimum-power or minimum-weight design point in general. |

What works and should be kept: changed range / payload / take-off roll / stall resize correctly
(range 2000 km → 7134 kg, 3000 km → 9555 kg, 20 pax → 9189 kg; `stress.txt`), and an infeasible
range (12 000 km) raises a clear `ValueError` [K].

## 2. Mission planning gaps

From `src/aerokit/design/mission_plan.py` and `src/aerokit/mission/*.py` (read 2026-10-25) [K].

| # | Finding | Evidence |
|---|---|---|
| M1 | **The mission optimiser is library-only.** `mission.optimize.optimize_search` (altitude × speed × spacing, Pareto front) is not called by `sizing mission`; the CLI plans one fixed altitude and pattern. | grep: no call from `design/mission_plan.py` or `cli/commands.py`. |
| M2 | **Search area is a rectangle only** (`area_width`, `area_length`), although `mission.coverage` handles any simple polygon. | `load_mission`, `mission_plan.py:67`. |
| M3 | **No wind** in the simulation or the route (no match for "wind" in `mission/`). | grep [K]. |
| M4 | **STK import untested** (no licence here) — the KML/CSV/GeoJSON are parsed by our tests, not by STK. | `cli/commands.py:714` warning. |

## 3. Discipline gaps for other challenge types

The 2026 challenges are announced on 4 Nov; the 2023 Ansys card was conceptual design + STK, but a
CFD or structural task is possible (`00_overview.md` §1) [D].

| # | Finding | Evidence |
|---|---|---|
| D1 | **No aerodynamic analysis method** to cross-check Fluent: no panel method, vortex-lattice or numerical lifting-line solver. `aero` gives ISA, Re/Mach/y⁺ set-up, NACA 4-digit points and planform geometry only. | `aerokit aero --help`, `aerokit geometry --help`; grep for panel/vortex/xfoil: nothing [K]. Anderson 6th ed. (the user's PDF, checked 2026-10-25 by `anderson_methods.py`) contains the source panel method (Figs. 3.40–3.41, PDF p. 310–313), the vortex panel method (section heading on PDF p. 392) and the numerical nonlinear lifting-line method (§5.4, book p. 465). The vortex lattice method is given only in outline: the book itself says its worked example is in its Reference 13 (PDF p. 497). So panel and lifting-line codes can be checked against this book; a VLM cannot. |
| D2 | **No shell element.** `MITC4` is a Mindlin plate (bending only, membrane pre-stress only for `kg`); wing-box skins cannot be modelled with coupled membrane + bending to cross-check Ansys Mechanical shells. | `fem/elements/plate.py:35` [K]. |
| D3 | `Frame3D`, 2-D continuum and solid elements have no geometric stiffness (`NotImplementedError`) → linear buckling only with `Frame2D` and `MITC4`. | `fem/elements/line.py:320`, `plane.py:428`, `solid.py:212-220` [K]. |
| D4 | Stability and component weights exist (`aero.stability`, `aero.weight`) but are not part of `sizing design` (no CG, static margin, tail sizing in the report). The 2023 card says not to go into stability [D], so this is low priority unless the 2026 card asks. | grep in `design/pipeline.py` [K]. |

## 4. Source gaps (verification debt)

Counted with `grep -ciE "not read|not verified|unverified|search summary|via csv|book not"` over
`src/aerokit` [K]. Largest: `aero/drag.py` 23, `materials/library.py` 14, `references/_optimization.py`
11, `materials/composites.py` 8, `aero/weight.py` 7.

| # | Gap | Effect |
|---|---|---|
| S1 | **Raymer 6th ed. not read.** Form factors, interference factors, Cf compressibility factor (`aero/drag.py`), group weights with equation numbers "from memory" (`aero/weight.py:14`), weight fractions and performance (Ch. 3, 5, 17). | The most-used design formulas are "as commonly quoted". |
| S2 | **Anderson, *Aircraft Performance and Design*** (the card's second book) not available; take-off/landing conventions unverified (`aero/performance.py:420, 524`). | King Air take-off error −40 % cannot be separated into model vs definition error. |
| S3 | King Air 350i wing area, `configuration.py` interference factors (Q 1.10, 1.5). (The CO₂ index 3.16 kg/kg was verified on 2026-10-25: ICAO CEC methodology v8; CORSIA Order 2021 art. 28(5).) | The validation row carries unverified inputs. |

Getting the Raymer PDF (e.g. from the course library) clears most of S1 in a few hours with the same
page-check script used for Anderson (22/22 citations checked).

## 5. Test gaps

`python -m pytest -q -p no:randomly --cov=aerokit` (2026-10-25, 8 min 39 s): **1022 passed, 1 skipped,
2912/2912 numerical checks, line coverage 93 %** (15 897 statements, 1068 missed; `pytest_cov.txt`,
`cov.json`) [K]. Lowest packages: `cli` 89.6 %, `units.py` 89.7 %, `materials` 91.7 %; lowest files
with ≥ 40 statements: `materials/library.py` 80 %, `cad/readers.py` 83 %, `output/console.py` 85 %.
Branch coverage was not measured.

Line coverage is not the weak spot. The weak spot is that **no test asserts physical plausibility
of off-design runs**: the cases of §1 (900 km/h turboprop, jet type, landing 600 m) all ran without a
test noticing. Add them as regression tests together with A1–A3, so that each guard is tested by the
case that exposed it.

## 6. Recommended actions (ordered by value for the event, [Y])

| Priority | Action | Effort | Closes | Verify by |
|---|---|---|---|---|
| A1 | Plausibility guards in `sizing design`: refuse non-propeller `aircraft_type` until a jet path exists; warn on flight Mach > 0.6 for propellers, on W0 outside the regression range, on P/W far above the class. Warnings go to the report and the CLI. | 0.5 day | G2 (refusal), G4 | the `extreme.py` cases each produce the expected warning/refusal |
| A2 | Power–weight coupling: engine mass from installed power (turboprop specific power, source to be read) added to We; fuel fraction recomputed from the sized engine. | 0.5–1 day | G1 | Vmax 900 km/h case grows W0; base case changes are reported, not hidden |
| A3 | Landing constraint (max W/S from landing distance) and a W/S choice = minimum P/W (or W0) over the feasible diagram, reusing `sizing point`. | 0.5 day | G3, G5 | landing 600 m case passes 9/9; base case unchanged (stall still governs) |
| A4 | Jet path: `Turbofan` + jet Breguet (range/loiter), TSFC assumptions, T/W constraint curves. | 1 day | G2 | closed-form Breguet checks; a published business-jet validation like the King Air one |
| A5 | Wire `optimize_search` into `sizing mission` (`--optimize`), polygon area input, constant wind. | 1 day | M1–M3 | optimiser beats the fixed plan on the rehearsal; wind-free result unchanged |
| A6 | Vortex panel method (PDF p. 392) + numerical nonlinear lifting line (§5.4) from Anderson 6th ed.; VLM only if a second source is found (the book gives it in outline). | 1.5 days | D1 | thin-airfoil limit (cl = 2πα), the book's figures/results for both methods (to be read when implementing); CLα vs `lift_slope` |
| A7 | Obtain Raymer 6th ed. (and Anderson *Aircraft Performance and Design*) and run the page-check script on every Raymer citation. | 0.5 day once the PDF is here | S1, S2 | n/n citations found on the cited page |
| A8 | Flat shell element (MITC4 plate + membrane) with drilling stabilisation. | 1.5–2 days | D2 | patch tests, Scordelis–Lo roof |
| A9 | Test gaps from §5. | 0.5 day | §5 | coverage re-measured |

Suggested order with 9 days left: A1 → A3 → A2 (one day together, they make the pipeline safe to
use on an unknown task) → A5 → A6 → A7 (as soon as the PDF exists) → A4 → A9 → A8.

## 7. Status of A1–A3 (implemented 2026-10-25)

Code: `src/aerokit/design/sizing.py` (guards, `wing_loading_limits`, `CLASS_POWER_REFERENCE`), new assumptions
`wing_loading`, `power_weight_coupling`, `engine_specific_power` (`design/requirements.py`), unit dimension
`specific_power`, references `wikipedia_pt6_2026` and `wikipedia_king_air_2026`. Tests:
`tests/aero/test_design_guards.py`, 19 tests covering the stress cases of §1. A mutation run
(`scratchpad/gap/mutate.py`) switched each guard off in turn; 8/8 mutations were caught by the tests.

| Case (§1) | Before | After [K] |
|---|---|---|
| Rehearsal, default assumptions | 5974 kg, 1667 kW | **6288 kg, 29.0 m², 1755 kW**; ΔWe/W0 = +0.0138 because its P/W (28.45 W/N) is above the King Air 350i (23.47 W/N). `power_weight_coupling: "off"` reproduces 5974 kg exactly. |
| Vmax 900 km/h, ceiling 18 km, stall 60 km/h | 8/8 pass at 5974 kg | `ValueError`: no weight solution; the message gives Wf/W0, the engine-mass correction and the governing constraint |
| Vmax 650 km/h | 5974 kg, 3534 kW | 9354 kg, 5534 kW; with the coupling off it warns that P/W is 2.6 × the class reference |
| `aircraft_type: "jet transport"` | sized as a 6462 kW turboprop | `ValueError: not a propeller class` |
| Landing 600 m | 8/9, landing −10 % | 9/9: landing sets W/S (1759 vs stall 2127 N/m²), 6660 kg, 37.1 m², Vmax governs |
| 20 kg cargo, no crew, twin-turboprop class | silent | warning: manned regression for an unmanned design |
| Vmax 700 km/h at 10 km | silent | warning: Mach 0.65, propeller compressibility not modelled |
| `wing_loading: "min_power"` (rehearsal) | — | W/S 2122 vs 2127 N/m²: the stall limit lies almost exactly at the ceiling/Vmax crossing, so the classic choice is already near the minimum P/W |

Side effects (reported, not hidden): the K_LD sensitivity grows to 1596–2394 kW (the coupling amplifies
power changes into weight); CLmax landing now changes W0; the power-lapse finding of docs/04 §1 still holds
(n 0.7–1.0 → 1748–1755 kW). Mission: 6.09 h on station and 79.2 % coverage, unchanged, because the fuel fraction
is the same and the aircraft scales; mission fuel 980 kg → 3096 kg CO₂.

Limits of the A1–A3 fix: the reference power loading is one aircraft (King Air 350i), and the engine specific power is
the *dry* PT6A-60A mass (nacelle, propeller and engine systems are not included, so the correction is low).
Other classes get no coupling and a warning. The 0.6 Mach and 2 × thresholds are aerokit judgement.

## 8. Status of A5 (implemented 2026-10-25)

Code: `mission/simulate.py` (`Wind`, per-segment `track`, wind on climb, transit, search and descent),
`mission/patterns.py` (`polygon_track`: PS/CS ladder clipped strip by strip to any simple polygon),
`mission/coverage.py` (exact rectangle method only for axis-aligned rectangles, raster otherwise),
`mission/optimize.py` (CS, polygon and wind), `design/mission_plan.py` (`area_polygon`, `wind_speed`/`wind_from`,
`min_/max_search_altitude`, `optimize()`), CLI `sizing mission --optimize`, example
`ansys_2023_mission_polygon_wind.json`. Tests: `tests/mission/test_polygon_wind_optimize.py` (19 tests); a
mutation run (`scratchpad/a5/mutate_a5.py`, outside the repository) broke wind, wind sign, polygon clipping, single-pass flying and the sensor
limit in turn: 6/6 caught.

| Check [K] | Result |
|---|---|
| Rectangle given as a polygon (0° and 30°) | identical waypoints to `parallel_track` (max difference 0.0 m) |
| No wind / `Wind(0)` | all 59 previous mission tests unchanged; Wind(0) fuel equal to 1e-12 |
| 40 km/h easterly, area 400 km east | cruise out −40.3 km/h, cruise back +39.7 km/h ground speed; search legs (N–S) slowed by the crosswind 214.7 → 208.8 km/h; coverage 95.7 → 93.3 % |
| `--optimize`, 2023 rehearsal (no sensor limit) | 56 candidates, best 3000 m, 268 km/h: **100 % covered in 3.35 h with 808 kg**, against 79.2 % for the fixed 1500 m plan (the refinement also tried 3375 m and kept 3000 m) |
| `--optimize`, polygon + wind example (limit 2500 m) | 46 candidates, best 2438 m, 261 km/h: 100 % of 1899 km² in 3.19 h, 789 kg |

Found and fixed while testing: when the whole pattern fitted, `plan()` kept "searching" (holding at the last
waypoint) until the reserve, so it reported 4.97 h and 980 kg instead of 3.35 h and 808 kg; the completeness
flag compared the geodesic route with the planar pattern length and printed "(fuel-limited)" for a complete
pattern. The plan now flies a complete pattern once.

Limits: search and transit speeds are the still-air optima (no wind-optimal speed); the reserve loiter and the
transit climbs/descents at the area fly in the air mass; the optimiser has no sensor-resolution model — set
`max_search_altitude`, otherwise a higher altitude always wins on swath. In the map figure the polygon outline is
hard to see under dense tracks.

## 9. Radio links from Sidera (2026-10-25)

The 2023 Ansys final (`08_past_challenges.md` §2c) asked for GPS/Cospas-Sarsat visibility, a UAS coverage plan
and a helicopter-to-command-centre radio link. The link part is now covered by `aerokit.comms`, copied from Sidera
(`05_toolkit.md`, "Radio links"; 14 modules and 2 excerpts, 159 Sidera tests passing identically in both environments). Check on
an assumed 60 km helicopter link (10 W, 2/6 dBi, 600 K, 64 kbit/s, free space): FSPL equals 20 log10(4πdf/c) to
0.01 dB from VHF to Ku, and C/N0 at 125 MHz equals the hand sum 12 − 109.95 − 21.78 + 228.6 = 108.87 dB-Hz.

Still missing for that task type [Y]:

| # | Gap | Sidera has it? | Cost to bring over |
|---|---|---|---|
| C1 | Satellite orbits and visibility from a ground point | — | **done 2026-10-25**: `aerokit.orbits` (Sidera leaves + nominal GPS/Galileo, GMST visibility); 51 tests, 6/6 mutations caught |
| C2 | TLE + SGP4 (real constellations) | yes (`io.interchange.tle`, `frames.teme`) | needs the `sgp4` package (not installed; a PyPI download) and current TLEs from CelesTrak at the event |
| C3 | Multi-hop relay as chained link budgets | — | **done 2026-10-25**: `aerokit.comms.chain` (transparent: noise densities add; regenerative: weakest hop) |
| C4 | Terrain line-of-sight / diffraction for the air–ground link (mountains) | horizon masks only (bodies-dependent) | not planned; state it as an assumption |
