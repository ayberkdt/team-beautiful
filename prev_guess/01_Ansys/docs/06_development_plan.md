# 06 · Development plan — closing the gap to the Ansys-type challenge

Prepared: 2026-10-25 (9 days before the event, 3–8 Nov 2026, Brugge). Basis: the 2023 Ansys task card
`prev_guess/00_general/past_competitions/Ansys-challenge.pdf` (read in full, 4 pages) [D], the 2026 Regulations v1.1 [D],
the rehearsal `prev_guess/01_Ansys/docs/04_2023_example_solution.md` and a code inventory of `src/aerokit` (grep of every
public function, 2026-10-25).

Tags: **[D]** read from the source document · **[K]** checked in the code / by running it · **[Y]** judgement.

---

## 1. What the 2023 Ansys task actually asked for [D]

Title: *Design and mission optimization of a crisis response aerial vehicle*. Two legs:

1. **Conceptual design** (Raymer 6th ed. + Anderson, *Aircraft Performance and Design*) of a medium
   aircraft meeting: range ≥ 1300 km, 30 min loiter, stall 150 km/h, Vmax 500 km/h, service ceiling
   10 000 m, climb 10 m/s, take-off ground roll 800 m, 4 crew + 10 passengers + 200 kg supplies.
   The card says to *focus mainly on satisfying the performance criteria* and **not** go into
   configuration, structural and stability detail; simplifying assumptions are allowed if justified;
   "Take extra care in the unit conversions".
2. **Mission planning** in Ansys STK (Aviator + Coverage): plan the optimal flight path to, from and
   within a predetermined search area for best coverage with on-board imaging sensors while
   satisfying fuel and performance constraints.

Judging (2026 Regulations §1.4): **technical feasibility, innovation/creativity, sustainability,
presentation quality**; deliverables in English; challenges revealed on the morning of 4 Nov; BYOD,
sponsors may provide temporary licences.

## 2. How much of it the toolkit covers today

| Task element | Status | Evidence |
|---|---|---|
| Weight sizing W0 (Raymer fractions + empty-weight regression) | **done** | `sizing raymer` → W0 5974 kg [K] |
| Constraint diagram (climb, ceiling, Vmax, take-off, stall) | **table only** — no figure | `sizing raymer`, `sizing point` [K] |
| Design point optimisation, carpet plot, sensitivity, Monte Carlo | **library only** (`optimization.design`), no CLI/figure | [K] |
| Wing planform, V-n diagram, wing-box sizing, tail volume, CG | **done** (beyond the card's scope) | [K] |
| Drag polar | **weak**: L/Dmax = K_LD·√(AR/(Swet/Sref)) with K_LD and Swet/Sref *assumed* | docs/04 §1 |
| Engine model | **weak**: power ∝ σ — the governing ceiling constraint depends on it | docs/04 §1 |
| Mission fuel | **fixed Raymer fractions + Breguet**, no time-stepped mission | `aero.sizing` [K] |
| Performance check of the *final* design (Anderson): ROC(h), absolute/service ceiling, time to climb, Vmax(h), take-off/landing distance, range & endurance at best speeds, payload-range | **missing** | grep: no such functions [K] |
| Requirement compliance table (PASS/FAIL per requirement) | **missing** | [K] |
| Unit-safe inputs ("1300 km", "150 km/h") | **missing** (SI floats only) | [K] |
| Mission planning (route, search pattern, sensor swath, coverage, time on station) | **missing** | grep: nothing [K] |
| STK hand-off (waypoints, Aviator performance parameters) | **missing** | [K] |
| Presentation figures (constraint diagram, payload-range, mission profile, coverage map, tornado) | **missing** except V-n | [K] |
| Sustainability metrics (fuel/CO₂ per passenger-km, SAF, hybrid variant) | **missing** (one hand-computed line in docs/04 §5) | docs/04 |

**Estimate [Y]:** leg 1 is ~60 % covered (sizing yes, performance verification and justification no);
leg 2 is 0 % in code (STK itself is only available at the event).

## 3. Plan — ordered by score per day of work

Each item states how it will be verified; nothing is "done" without its test.

### P0 — must have before 3 Nov (≈ 4 days)

**P0-1 · One-command design pipeline (1 day).**
`aerokit design run requirements.json --out report/` → Markdown report + figures in one run:
requirements → constraint diagram **figure** with the chosen point → W0, S, P → V-n → planform →
assumption table (every assumption flagged, value + source) → compliance table. Requirements are
written with units (`"range": "1300 km"`, `"stall": "150 km/h"`) and parsed by a small unit layer
(SI internally; rejects unknown or dimensionally wrong units).
*Verify:* the rehearsal numbers of docs/04 reproduced exactly (W0 5974 kg, P/W 28.45 W/N); unit
round-trip and wrong-dimension tests; datawiz 0-error figures; ux-yasalari audit of the report.

**P0-2 · Anderson point performance of the final design (1.5 days).**
`aero.performance`: P_required / P_available vs V at altitude; max rate of climb vs h; absolute and
service ceiling (ROC = 0 / 0.508 m/s) solved, not assumed; time to climb; Vmax(h); take-off ground
roll with rolling friction and lift-off at 1.1–1.2 V_stall plus air distance; landing distance;
best-range and best-endurance speeds; Breguet range and endurance; **payload-range diagram**.
Output: a compliance table *requirement → computed value → margin → PASS/FAIL*.
*Verify:* closed forms (parabolic polar optima: V_(L/D)max, V for minimum power), consistency with
the constraint diagram (the sized point must pass every requirement with ≥ 0 margin), and the
worked examples of Anderson's book (to be checked against the book at the event; we do not have
it here — **not verified**).

**P0-3 · Engine/propulsion models + sensitivity (0.5 day).**
Selectable power lapse (σ, σ^n with n as a parameter, a turboprop lapse from the literature — source
to be read before use), propeller efficiency vs V, C_bhp. A **tornado chart** of W0 and installed
power against every assumption (power lapse, K_LD, Swet/Sref, C_bhp, η, CLmax).
*Verify:* tornado bars reproduce one-at-a-time reruns of P0-1 exactly; `optimization.design.sensitivity`
reused.

**P0-4 · Mission planning engine for leg 2 (1.5 days).**
`mission` package:
- WGS-84 great-circle legs (base → search area → base);
- search patterns from the IAMSAR manual (parallel track, creeping line, expanding square) with
  track spacing from the sensor swath (swath = 2 h tan(FOV/2), overlap factor);
- coverage fraction of a polygon (raster or exact clipping);
- time-stepped mission simulation using P0-2 performance (climb, cruise, search at best-endurance
  speed, return, reserve), giving time on station and the fuel margin;
- optimiser: altitude × speed × track spacing for maximum covered area within the fuel limit.
*Verify:* geodesic distances against known city pairs (Vincenty/Karney reference values), swath and
coverage on synthetic squares (exact answers), fuel integral vs Breguet for a pure-cruise mission.

**P0-5 · STK hand-off (0.5 day).**
Export waypoints as CSV, KML and GeoJSON, and an **Aviator parameter sheet** (climb/cruise/descent
speeds, rates, fuel flows, ceilings) produced from P0-2, ready to type into STK Aviator's
performance models. STK file formats are *not verified* here — confirm on the event licence; KML/CSV
are the safe fall-back. *Verify:* KML/GeoJSON validated by parsing; sheet values equal P0-2 outputs.

### P1 — strong differentiators (≈ 2 days)

**P1-1 · Drag build-up (Raymer component method, 1 day).** Skin friction (laminar/turbulent mix),
form factors, interference factors, wetted areas from the planform/fuselage estimate, miscellaneous
and leakage drag → CD0 and e, replacing the K_LD guess; report both side by side.
*Verify:* flat-plate Cf formulas against their sources; total CD0 of the King Air 350-class design in a
plausible band (cite the comparison source); K_LD estimate vs build-up difference reported.

**P1-2 · Validation against a real aircraft (0.5 day).** Run P0-1/P0-2 on the King Air 350 public
data (MTOW, S, power, cruise, ceiling — sources cited in docs/04 §2) and report the errors. This turns
"our tool" into "our *validated* tool" for the feasibility criterion.

**P1-3 · Sustainability module (0.5 day).** Block fuel, CO₂ (3.16 kg CO₂/kg fuel; verified 2026-10-25 from ICAO CEC v8 and CORSIA Order 2021),
fuel per passenger-km and per search-km², SAF blend scenario, and a hybrid-electric loiter variant
sized with battery specific energy as a parameter (innovation lever).
*Verify:* hand checks; mass balance closes.

### P2 — nice to have (if time remains)

- **P2-1** Slide-ready figure set (datawiz `sunum-tam` profile) and a one-page summary generator.
- **P2-2** Stability/trim check of the final configuration (modules exist: tail volume, neutral point).
- **P2-3** Uncertainty propagation (Monte Carlo already in `optimization.design`) on W0 and on the
  fuel margin of the mission.
- **P2-4** Coverage of the residual FEM/materials gaps from the limitations review (shell element,
  material non-linearity) — low value for this challenge type, so deliberately last.

## 4. Rehearsal and readiness

1. 1 Nov: full dry run of the 2023 task from `requirements.json` to slides, timed (target ≤ 2 h for leg 1).
2. 2 Nov: dry run with *changed* requirements (e.g. range 2000 km, ceiling 8000 m) to prove the
   pipeline is not tuned to one case.
3. Laptop check: Python 3.12 + numpy/scipy/matplotlib + datawiz, `python -m pytest -q` green
   (current baseline: 692 passed, 2523/2523 checks).

## 5. Risks

- Anderson's book is not in `references/`; P0-2 formulas will be cited to Raymer/Anderson and
  checked against the book only when it is available — until then marked unverified.
- STK file import formats are unverified; plan to finish STK work on the event licence.
- The 2026 Ansys challenge is unknown until 4 Nov; P0-1/P0-2 are generic for any aircraft
  conceptual task, P0-4 is specific to search/coverage missions.

---

## 6. Implementation status (2026-10-25, end of day)

All P0 items and the three P1 items are implemented and tested. Numbers below come from the commands
named next to them (run on 2026-10-25) [K].

| Item | Where | Status and evidence |
|---|---|---|
| P0-1 pipeline | `aerokit.design` (`requirements`, `sizing`, `pipeline`), `aerokit.units`, CLI `sizing design` | Reproduces docs/04 exactly (W0 5974 kg, S 27.5 m², 1667 kW, P/W 17.70 / 28.45 / 28.38 / 10.88 W/N; `tests/aero/test_design_pipeline.py`). Report + 4 datawiz-audited figures (0 errors) in ~30 s. |
| P0-2 performance | `aerokit.aero.performance` | Ceilings, time to climb, V_max/envelope, take-off/landing, range/endurance, payload-range, compliance. 188 checks (Breguet equalities to 1e-6). Rehearsal design: **8/8 card requirements met**; the service ceiling sits exactly on the sizing constraint (ROC 0.5079995 vs 0.508 m/s). |
| P0-3 engine + sensitivity | `aerokit.aero.propulsion`, `aerokit.design.sensitivity`, tornado figure | **Finding: the power lapse is not the most sensitive assumption** (σⁿ, n 0.7–1.0 → 1662–1667 kW, Vmax takes over). K_LD ±10 % → 1540–2116 kW is the largest swing; docs/04 §1 corrected. |
| P0-4 mission | `aerokit.mission` (geodesy, IAMSAR patterns, coverage, simulation, optimiser), `aerokit.design.mission_plan`, CLI `sizing mission` | Rehearsal search (50 × 50 km area 400 km away, 1500 m, 60° FOV): 6.09 h on station, 79 % covered (K_LD design); 6.21 h, 81 % (build-up design). Vincenty round trip < 0.01 mm; cruise fuel vs Breguet < 0.12 %. |
| P0-5 STK hand-off | `aerokit.mission.export` | Waypoints CSV/KML/GeoJSON + Aviator parameter sheet (md/csv). STK formats **not verified** (no licence here). |
| P1-1 drag build-up | `aerokit.aero.drag`, `aerokit.design.configuration` (`drag_method="buildup"`) | Anderson Examples 4.8–4.11, 18.2, 19.1–19.2 reproduced. Build-up L/Dmax 16.6 vs K_LD 14.1 → **W0 5666 kg, 1459 kW** (−5 %, −12.5 %); fixed point in 4 iterations. |
| P1-2 validation | `aerokit.design.validation`, CLI `sizing validate` | King Air 350i (Wikipedia, read today; wing area unverified): ceiling −10 %, max speed −7 %, take-off −40 % (definition unknown), **empty weight −11 %**. With the King Air We/W0 calibration (×1.118) the 2023 design grows to 7939 kg / 2215 kW — the largest uncertainty of the result. Ceiling-calibrated lapse n = 0.835. |
| P1-3 sustainability | `aerokit.design.sustainability`, in `sizing mission` | Mission fuel 798 kg → 2521 kg CO₂, 0.39 kg fuel per km² searched (build-up design; K_LD design: 931 kg → 2942 kg, 0.47 kg/km²); SAF and hybrid-loiter helpers (factors are parameters, not verified facts). |

**Follow-up (docs/07 §7):** plausibility guards, landing W/S limit and power-weight coupling added. The
default `sizing design` result is now 6288 kg / 1755 kW; the docs/04 numbers above are reproduced with
`power_weight_coupling: "off"`.

**Book check:** the user's PDF is Anderson, *Fundamentals of Aerodynamics* 6th ed. (2017) — not
*Aircraft Performance and Design* named on the card. It has no performance chapters; it is now the
source for skin friction, drag polar, lift slope and the standard atmosphere (our ISA agrees
with its Appendix D within 0.006 %, `tests/aero/test_core_models.py`). The performance models remain
cited to Raymer Ch. 17 as **not read in this session**.

All 22 Anderson page citations in the code were re-checked against the PDF by script (cited label
found on the cited page: 22/22; formula text compared for Eqs. 4.86, 4.88, 4.92, 5.81, 6.24, 6.25,
18.53). One correction followed: Anderson recommends Helmbold (Eq. 5.81) for AR < 4 and the
lifting-line Eq. 5.69/5.70 for "AR > 4, as a rule of thumb" (PDF p. 497). The design pipeline used
Helmbold for AR 9; it now uses `lift_slope`, which picks the formula by AR. Effect at AR 9:
CLα 5.040 → 5.141 1/rad (+2.0 %); n_max/n_min unchanged (3.14 / −1.25, maneuver-governed).

**Still open:** P2 items; STK file formats on the event licence; Raymer and Anderson *Aircraft
Performance and Design* not available, so take-off/landing conventions are unverified; wing area of the
King Air 350i not from a primary source.
