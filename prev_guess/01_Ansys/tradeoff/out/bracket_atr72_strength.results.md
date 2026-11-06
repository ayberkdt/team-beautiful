# ATR 72-600 bracket, strength-limited (per kg of the conventional 7075-T6 machined part)

Index case `beam_strong` · score: co2_total_kg

| Rank | Material | Route | Mass (kg) | CO₂ production (kg) | CO₂ use (kg) | CO₂ total (kg) | P(best) |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Scalmalloy | am_TO | 0.580 | 117 | 2567 | 2684 | 0.81 |
| 2 | Ti-6Al-4V | am_TO | 0.679 | 54 | 3004 | 3059 | 0.19 |
| 3 | 7075-T6 | machined_TO | 0.800 | 80 | 3539 | 3619 | 0.00 |
| 4 | Ti-6Al-4V | machined_TO | 0.905 | 340 | 4005 | 4346 | 0.00 |
| 5 | AlSi10Mg | am_TO | 0.989 | 28 | 4377 | 4405 | 0.00 |
| 6 | 7075-T6 | machined | 1.000 | 100 | 4424 | 4524 | 0.00 |
| 7 | 2024-T351 | machined_TO | 1.061 | 106 | 4695 | 4800 | 0.00 |

Pareto set (mass_kg, co2_total_kg): Scalmalloy / am_TO

| Factor | Range | Tag | Margin at low (kg) | Margin at high (kg) | Reverses choice |
|---|---|---|---:|---:|---|
| lifecycle.flights | 30000–70000 flights over life | Y | 199 | 549 | no |
| lifecycle.fuel_per_kg_per_flight | 0.022–0.033 kg fuel / kg carried / flight | A | 281 | 453 | no |
| routes.am_TO.mass_factor | 0.5–0.7 - | A | 312 | 437 | no |
| materials.Scalmalloy.co2_per_kg | 68–128 kg CO2 / kg | H | 427 | 374 | no |
| routes.am_TO.buy_to_fly | 1.2–2 - | A | 387 | 353 | no |
| materials.Ti-6Al-4V.co2_per_kg | 16.1–46.5 kg CO2 / kg | D | 344 | 374 | no |
| lifecycle.grid_co2_per_MJ | 0.0112–0.1543 kg CO2 / MJ electricity | D | 374 | 376 | no |
| routes.am_TO.process_MJ_per_kg | 61–158.4 MJ / kg bought | A | 374 | 375 | no |
| materials.7075-T6.co2_per_kg | 4.5–22 kg CO2 / kg | D | 374 | 374 | no |
| materials.7075-T6.cost_by_route.machined.price_per_kg | 7.5–20 EUR/kg | Y | 374 | 374 | no |
| materials.7075-T6.cost_by_route.machined.route_cost_per_kg | 40–240 EUR/kg | S | 374 | 374 | no |
| materials.7075-T6.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 374 | 374 | no |
| materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 374 | 374 | no |
| materials.2024-T351.co2_per_kg | 4.5–22 kg CO2 / kg | D | 374 | 374 | no |
| materials.2024-T351.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 374 | 374 | no |
| materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 374 | 374 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.price_per_kg | 29–96 EUR/kg | A | 374 | 374 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg | 120–620 EUR/kg | S | 374 | 374 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.price_per_kg | 71–180 EUR/kg | A | 374 | 374 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.route_cost_per_kg | 250–855 EUR/kg | A | 374 | 374 | no |
| materials.AlSi10Mg.co2_per_kg | 4.5–22 kg CO2 / kg | D | 374 | 374 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.price_per_kg | 40–126 EUR/kg | A | 374 | 374 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 374 | 374 | no |
| materials.Scalmalloy.cost_by_route.am_TO.price_per_kg | 120–400 EUR/kg | Y | 374 | 374 | no |
| materials.Scalmalloy.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 374 | 374 | no |
| routes.machined.buy_to_fly | 8–33 - | A | 374 | 374 | no |
| routes.machined.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 374 | 374 | no |
| routes.machined_TO.buy_to_fly | 8–33 - | A | 374 | 374 | no |
| routes.machined_TO.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 374 | 374 | no |
| routes.machined_TO.mass_factor | 0.7–0.9 - | Y | 374 | 374 | no |

Inputs tagged S or Y (replace first): lifecycle.flights, materials.2024-T351.cost_by_route.machined_TO.price_per_kg, materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg, materials.7075-T6.cost_by_route.machined.price_per_kg, materials.7075-T6.cost_by_route.machined.route_cost_per_kg, materials.7075-T6.cost_by_route.machined_TO.price_per_kg, materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg, materials.Scalmalloy.cost_by_route.am_TO.price_per_kg, materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg, reference_mass, routes.machined.mass_factor, routes.machined_TO.mass_factor
