# Trade-off studies — machine-readable version

This folder is written for an agent (or a person working like one). It holds study files that
`aerokit.design.tradeoff` evaluates deterministically, and the rules for changing them on the day of the Ansys task.
The human-readable version, which has the same numbers with figures and narrative, is in `reports/`.

## Files

| File | Role |
|---|---|
| `bracket_a320_strength.json` | strength-limited bracket (`beam_strong`), A320 use phase, 5 options |
| `bracket_a320_stiffness.json` | the same with the stiffness index (`beam_stiff`) |
| `bracket_atr72_strength.json` | regional turboprop use phase |
| `bracket_satellite_strength.json` | no use phase: production CO₂ only |
| `bracket_satellite_penalty.json` | satellite with Z = 3000·mass + 0.0743·CO₂ (Ashby space exchange constant, EU ETS 2025) |
| `bracket_a320_cost.json` | A320 strength case with cost: Z = cost + 500·mass + 0.0743·CO₂ (EUR) |
| `bracket_hot_strength.json` | strength case with 2618-T61 and Inconel 718 added for hot zones (area C, docs/11); kept apart so the A320 Monte Carlo draws do not move |
| `panel_cabin_stiffness.json` | cabin panel, `panel_stiff`, metals vs CFRP, CF/PEEK, flax, glass/phenolic; end-of-life credits (area B) |
| `panel_cabin_fst.json` | the same with `constraints.require = ["fst_cabin"]`: only materials that pass the cabin fire tests |
| `panel_cabin_eol.json` | the same ranked with the end-of-life potential counted (sensitivity only) |
| `build_studies.py` | writes the ten study files from one base definition |
| `../cards/*.json`, `scripts/card_day.py` | task-card pipeline (geometry, loads, limits → designs, checks, ranking, slide figures); schema in `aerokit.design.card` |
| `decision_rules.json` | the decision catalogue as condition → default → evidence records: D-01 … D-26 main path, D-27 … D-40 the three side areas (field `area`) |
| `out/<study>.results.json` | output of `scripts/tradeoff_study.py` (do not edit by hand) |

Run: `python scripts/tradeoff_study.py studies/tradeoff/<study>.json` (writes `out/`). Tests: `tests/test_tradeoff.py`.

## Schema of a study file

```text
name                 str
case                 one of aerokit.materials.selection.CASES (tie_stiff, tie_strong, beam_stiff, beam_strong,
                     panel_stiff, panel_strong, column_buckling)
reference_material   key of materials; reference_mass is the mass of that material on the route with mass_factor 1
reference_mass       Factor [kg]
lifecycle            fuel_per_kg_per_flight [kg/kg/flight], flights [-], co2_per_kg_fuel [kg/kg],
                     grid_co2_per_MJ [kg/MJ electricity]                         — all Factor
materials.<name>     E [Pa], Fty [Pa], rho [kg/m3] (plain numbers, SI), properties_source str,
                     co2_per_kg Factor [kg CO2/kg], optional price_per_kg Factor,
                     optional cost_by_route.<route>: {price_per_kg, route_cost_per_kg} Factors (preferred),
                     optional eol_credit_per_kg Factor [kg CO2 avoided per kg of part at end of life],
                     optional max_service_C [C], optional flags [str] (e.g. "fst_cabin")
routes.<name>        buy_to_fly, process_MJ_per_kg [MJ per kg bought], mass_factor [-] — Factor;
                     optional cost_per_kg Factor (cost per kg of finished part)
options              "all" or [{material, route}, …]
objectives           subset of mass_kg, co2_production_kg, co2_use_kg, co2_total_kg, co2_total_with_eol_kg, cost
constraints          optional {service_temperature_C, require: [flag, …]}: options that fail are removed and
                     listed under "screened" in the result
exchange             optional {objective: alpha}; score = Σ alpha·objective (Ashby penalty); without it,
                     score = co2_total_kg
```

A **Factor** is `{"value", "low", "high", "unit", "source", "tag"}` plus an optional `"group"`. Factors sharing a group are drawn from the same uniform quantile in the Monte Carlo (e.g. `primary_al` for all wrought/cast aluminium CO₂ values). A bare number is refused. `low ≤ value ≤ high`
is enforced. Tags: `D` read from source in the writing session · `A` read by a sub-agent · `S` snippet only ·
`Y` assumption · `H` calculated.

## Model (exact)

```text
M      = reference_mass · I(reference_material) / I(material) · mass_factor(route)     I = performance index of `case`
prod   = M · btf · co2_per_kg + M · btf · process_MJ_per_kg · grid_co2_per_MJ
use    = M · fuel_per_kg_per_flight · flights · co2_per_kg_fuel
total  = prod + use
cost   = M · btf · price_per_kg + M · cost_per_kg        (only if both are given)
eol    = −M · eol_credit_per_kg                          (reported apart; added only in co2_total_with_eol_kg)
```

The Monte Carlo draws every Factor uniformly in [low, high], independently, and counts which option has the lowest
score. The tornado moves one Factor to low and to high and reports `margin = score(runner-up) − score(best)`; a
negative margin means that one input alone reverses the nominal choice.

## Rules for editing on the day

1. Replace inputs in the order of `weak_inputs`, then by tornado `swing`. Do not touch `D` inputs unless EduPack
   gives an alloy-specific value; in that case keep the old value in `source`.
2. Keep every new number as a Factor with `source` = where it was read (EduPack record name, datasheet URL + page)
   and an honest tag. Never upgrade a tag.
3. The mass factors of the routes are the strongest lever and are assumptions until the topology run exists:
   overwrite them with `validated mass / reference mass` from Discovery or Mechanical **after** reconstruction
   and validation (catalogue D-13).
4. An AM option is only valid for a printable alloy: 7075 and 2024 are not offered on `am_TO` (hot-cracking in
   powder-bed fusion is the usual reason; not verified with a source in this work). Use AlSi10Mg, Scalmalloy or
   Ti-6Al-4V for AM. Scalmalloy only below 373 K (properties fall sharply above it, Mehta et al. 2022).
5. A result is reportable only when the Monte Carlo `p_best` of the chosen option is ≥ 0.8 **or** the report says
   which tornado factor would reverse it.
6. Do not mix marginal and average fuel factors (catalogue C-22). `fuel_per_kg_per_flight` here is marginal.

## Reading the result

* `nominal`, sorted by score, with production, use and total CO₂ split.
* `pareto` — non-dominated on `objectives`; if it has one member, that option wins on every objective.
* `monte_carlo.p_best` — robustness of the choice to the stated ranges, not a probability of truth.
* `tornado` — which inputs to measure first.
