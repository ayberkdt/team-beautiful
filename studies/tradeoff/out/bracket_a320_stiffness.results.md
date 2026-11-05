# A320 cabin/system bracket, stiffness-limited (per kg of the conventional 7075-T6 machined part)

Index case `beam_stiff` · score: co2_total_kg

| Rank | Material | Route | Mass (kg) | CO₂ production (kg) | CO₂ use (kg) | CO₂ total (kg) | P(best) |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | AlSi10Mg | am_TO | 0.569 | 16 | 10355 | 10371 | 0.61 |
| 2 | Scalmalloy | am_TO | 0.581 | 118 | 10578 | 10696 | 0.39 |
| 3 | Ti-6Al-4V | am_TO | 0.764 | 61 | 13900 | 13961 | 0.00 |
| 4 | 2024-T351 | machined_TO | 0.784 | 78 | 14267 | 14345 | 0.00 |
| 5 | 7075-T6 | machined_TO | 0.800 | 80 | 14561 | 14641 | 0.00 |
| 6 | 7075-T6 | machined | 1.000 | 100 | 18202 | 18301 | 0.00 |
| 7 | Ti-6Al-4V | machined_TO | 1.018 | 383 | 18534 | 18916 | 0.00 |

Pareto set (mass_kg, co2_total_kg): AlSi10Mg / am_TO

| Factor | Range | Tag | Margin at low (kg) | Margin at high (kg) | Reverses choice |
|---|---|---|---:|---:|---|
| lifecycle.fuel_per_kg_per_flight | 0.07–0.16 kg fuel / kg carried / flight | A | 231 | 398 | no |
| lifecycle.flights | 30000–60000 flights over life | D | 241 | 380 | no |
| routes.am_TO.mass_factor | 0.5–0.7 - | A | 270 | 378 | no |
| routes.am_TO.buy_to_fly | 1.2–2 - | A | 304 | 358 | no |
| materials.Scalmalloy.co2_per_kg | 68–128 kg CO2 / kg | H | 272 | 324 | no |
| materials.AlSi10Mg.co2_per_kg | 4.5–22 kg CO2 / kg | D | 331 | 316 | no |
| lifecycle.grid_co2_per_MJ | 0.0112–0.1543 kg CO2 / MJ electricity | D | 324 | 324 | no |
| routes.am_TO.process_MJ_per_kg | 61–158.4 MJ / kg bought | A | 324 | 324 | no |
| materials.7075-T6.co2_per_kg | 4.5–22 kg CO2 / kg | D | 324 | 324 | no |
| materials.7075-T6.cost_by_route.machined.price_per_kg | 7.5–20 EUR/kg | Y | 324 | 324 | no |
| materials.7075-T6.cost_by_route.machined.route_cost_per_kg | 40–240 EUR/kg | S | 324 | 324 | no |
| materials.7075-T6.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 324 | 324 | no |
| materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 324 | 324 | no |
| materials.2024-T351.co2_per_kg | 4.5–22 kg CO2 / kg | D | 324 | 324 | no |
| materials.2024-T351.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 324 | 324 | no |
| materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 324 | 324 | no |
| materials.Ti-6Al-4V.co2_per_kg | 16.1–46.5 kg CO2 / kg | D | 324 | 324 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.price_per_kg | 29–96 EUR/kg | A | 324 | 324 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg | 120–620 EUR/kg | S | 324 | 324 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.price_per_kg | 71–180 EUR/kg | A | 324 | 324 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.route_cost_per_kg | 250–855 EUR/kg | A | 324 | 324 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.price_per_kg | 40–126 EUR/kg | A | 324 | 324 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 324 | 324 | no |
| materials.Scalmalloy.cost_by_route.am_TO.price_per_kg | 120–400 EUR/kg | Y | 324 | 324 | no |
| materials.Scalmalloy.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 324 | 324 | no |
| routes.machined.buy_to_fly | 8–33 - | A | 324 | 324 | no |
| routes.machined.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 324 | 324 | no |
| routes.machined_TO.buy_to_fly | 8–33 - | A | 324 | 324 | no |
| routes.machined_TO.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 324 | 324 | no |
| routes.machined_TO.mass_factor | 0.7–0.9 - | Y | 324 | 324 | no |

Inputs tagged S or Y (replace first): materials.2024-T351.cost_by_route.machined_TO.price_per_kg, materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg, materials.7075-T6.cost_by_route.machined.price_per_kg, materials.7075-T6.cost_by_route.machined.route_cost_per_kg, materials.7075-T6.cost_by_route.machined_TO.price_per_kg, materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg, materials.Scalmalloy.cost_by_route.am_TO.price_per_kg, materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg, reference_mass, routes.machined.mass_factor, routes.machined_TO.mass_factor
