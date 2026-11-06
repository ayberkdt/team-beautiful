# Satellite bracket, strength-limited, production only (per kg of the conventional 7075-T6 machined part)

Index case `beam_strong` · score: co2_total_kg

| Rank | Material | Route | Mass (kg) | CO₂ production (kg) | CO₂ use (kg) | CO₂ total (kg) | P(best) |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | AlSi10Mg | am_TO | 0.989 | 28 | 0 | 28 | 0.70 |
| 2 | Ti-6Al-4V | am_TO | 0.679 | 54 | 0 | 54 | 0.30 |
| 3 | 7075-T6 | machined_TO | 0.800 | 80 | 0 | 80 | 0.00 |
| 4 | 7075-T6 | machined | 1.000 | 100 | 0 | 100 | 0.00 |
| 5 | 2024-T351 | machined_TO | 1.061 | 106 | 0 | 106 | 0.00 |
| 6 | Scalmalloy | am_TO | 0.580 | 117 | 0 | 117 | 0.00 |
| 7 | Ti-6Al-4V | machined_TO | 0.905 | 340 | 0 | 340 | 0.00 |

Pareto set (mass_kg, co2_total_kg): Ti-6Al-4V / am_TO; AlSi10Mg / am_TO; Scalmalloy / am_TO

| Factor | Range | Tag | Margin at low (kg) | Margin at high (kg) | Reverses choice |
|---|---|---|---:|---:|---|
| materials.Ti-6Al-4V.co2_per_kg | 16.1–46.5 kg CO2 / kg | D | -5 | 26 | yes |
| materials.AlSi10Mg.co2_per_kg | 4.5–22 kg CO2 / kg | D | 37 | 11 | no |
| routes.am_TO.buy_to_fly | 1.2–2 - | A | 21 | 35 | no |
| routes.am_TO.mass_factor | 0.5–0.7 - | A | 22 | 31 | no |
| lifecycle.grid_co2_per_MJ | 0.0112–0.1543 kg CO2 / MJ electricity | D | 29 | 21 | no |
| routes.am_TO.process_MJ_per_kg | 61–158.4 MJ / kg bought | A | 28 | 25 | no |
| materials.7075-T6.co2_per_kg | 4.5–22 kg CO2 / kg | D | 26 | 26 | no |
| materials.7075-T6.cost_by_route.machined.price_per_kg | 7.5–20 EUR/kg | Y | 26 | 26 | no |
| materials.7075-T6.cost_by_route.machined.route_cost_per_kg | 40–240 EUR/kg | S | 26 | 26 | no |
| materials.7075-T6.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 26 | 26 | no |
| materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 26 | 26 | no |
| materials.2024-T351.co2_per_kg | 4.5–22 kg CO2 / kg | D | 26 | 26 | no |
| materials.2024-T351.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 26 | 26 | no |
| materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 26 | 26 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.price_per_kg | 29–96 EUR/kg | A | 26 | 26 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg | 120–620 EUR/kg | S | 26 | 26 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.price_per_kg | 71–180 EUR/kg | A | 26 | 26 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.route_cost_per_kg | 250–855 EUR/kg | A | 26 | 26 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.price_per_kg | 40–126 EUR/kg | A | 26 | 26 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 26 | 26 | no |
| materials.Scalmalloy.co2_per_kg | 68–128 kg CO2 / kg | H | 26 | 26 | no |
| materials.Scalmalloy.cost_by_route.am_TO.price_per_kg | 120–400 EUR/kg | Y | 26 | 26 | no |
| materials.Scalmalloy.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 26 | 26 | no |
| routes.machined.buy_to_fly | 8–33 - | A | 26 | 26 | no |
| routes.machined.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 26 | 26 | no |
| routes.machined_TO.buy_to_fly | 8–33 - | A | 26 | 26 | no |
| routes.machined_TO.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 26 | 26 | no |
| routes.machined_TO.mass_factor | 0.7–0.9 - | Y | 26 | 26 | no |

Inputs tagged S or Y (replace first): lifecycle.flights, lifecycle.fuel_per_kg_per_flight, materials.2024-T351.cost_by_route.machined_TO.price_per_kg, materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg, materials.7075-T6.cost_by_route.machined.price_per_kg, materials.7075-T6.cost_by_route.machined.route_cost_per_kg, materials.7075-T6.cost_by_route.machined_TO.price_per_kg, materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg, materials.Scalmalloy.cost_by_route.am_TO.price_per_kg, materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg, reference_mass, routes.machined.mass_factor, routes.machined_TO.mass_factor
