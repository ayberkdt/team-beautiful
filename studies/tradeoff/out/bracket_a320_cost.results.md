# A320 bracket, strength-limited, penalty Z = cost + 500 x mass + 0.0743 x CO2 (EUR, per kg conventional part)

Index case `beam_strong` · score: penalty

| Rank | Material | Route | Mass (kg) | CO₂ production (kg) | CO₂ use (kg) | CO₂ total (kg) | P(best) |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Scalmalloy | am_TO | 0.580 | 117 | 10560 | 10677 | 0.26 |
| 2 | 7075-T6 | machined_TO | 0.800 | 80 | 14561 | 14641 | 0.31 |
| 3 | Ti-6Al-4V | am_TO | 0.679 | 54 | 12359 | 12414 | 0.43 |
| 4 | 7075-T6 | machined | 1.000 | 100 | 18202 | 18301 | 0.00 |
| 5 | 2024-T351 | machined_TO | 1.061 | 106 | 19315 | 19420 | 0.00 |
| 6 | Ti-6Al-4V | machined_TO | 0.905 | 340 | 16479 | 16819 | 0.00 |
| 7 | AlSi10Mg | am_TO | 0.989 | 28 | 18009 | 18037 | 0.00 |

Pareto set (mass_kg, co2_total_kg, cost): 7075-T6 / machined_TO; Ti-6Al-4V / am_TO; Scalmalloy / am_TO

| Factor | Range | Tag | Margin at low (kg) | Margin at high (kg) | Reverses choice |
|---|---|---|---:|---:|---|
| materials.Scalmalloy.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 247 | -734 | yes |
| routes.am_TO.mass_factor | 0.5–0.7 - | A | 342 | -174 | yes |
| routes.machined_TO.mass_factor | 0.7–0.9 - | Y | -120 | 288 | yes |
| materials.Scalmalloy.cost_by_route.am_TO.price_per_kg | 120–400 EUR/kg | Y | 154 | -90 | yes |
| lifecycle.fuel_per_kg_per_flight | 0.07–0.16 kg fuel / kg carried / flight | A | -40 | 183 | yes |
| routes.machined_TO.buy_to_fly | 8–33 - | A | 84 | 303 | no |
| lifecycle.flights | 30000–60000 flights over life | D | -27 | 159 | yes |
| materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 36 | 196 | no |
| routes.am_TO.buy_to_fly | 1.2–2 - | A | 121 | 23 | no |
| materials.7075-T6.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 68 | 148 | no |
| materials.7075-T6.co2_per_kg | 4.5–22 kg CO2 / kg | D | 81 | 89 | no |
| materials.Scalmalloy.co2_per_kg | 68–128 kg CO2 / kg | H | 88 | 84 | no |
| routes.machined_TO.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 84 | 87 | no |
| lifecycle.grid_co2_per_MJ | 0.0112–0.1543 kg CO2 / MJ electricity | D | 85 | 84 | no |
| routes.am_TO.process_MJ_per_kg | 61–158.4 MJ / kg bought | A | 85 | 84 | no |
| materials.7075-T6.cost_by_route.machined.price_per_kg | 7.5–20 EUR/kg | Y | 84 | 84 | no |
| materials.7075-T6.cost_by_route.machined.route_cost_per_kg | 40–240 EUR/kg | S | 84 | 84 | no |
| materials.2024-T351.co2_per_kg | 4.5–22 kg CO2 / kg | D | 84 | 84 | no |
| materials.2024-T351.cost_by_route.machined_TO.price_per_kg | 7.5–20 EUR/kg | Y | 84 | 84 | no |
| materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg | 40–240 EUR/kg | S | 84 | 84 | no |
| materials.Ti-6Al-4V.co2_per_kg | 16.1–46.5 kg CO2 / kg | D | 84 | 84 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.price_per_kg | 29–96 EUR/kg | A | 84 | 84 | no |
| materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg | 120–620 EUR/kg | S | 84 | 84 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.price_per_kg | 71–180 EUR/kg | A | 84 | 84 | no |
| materials.Ti-6Al-4V.cost_by_route.am_TO.route_cost_per_kg | 250–855 EUR/kg | A | 84 | 84 | no |
| materials.AlSi10Mg.co2_per_kg | 4.5–22 kg CO2 / kg | D | 84 | 84 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.price_per_kg | 40–126 EUR/kg | A | 84 | 84 | no |
| materials.AlSi10Mg.cost_by_route.am_TO.route_cost_per_kg | 220–1910 EUR/kg | A | 84 | 84 | no |
| routes.machined.buy_to_fly | 8–33 - | A | 84 | 84 | no |
| routes.machined.process_MJ_per_kg | 8–108.9 MJ / kg bought | A | 84 | 84 | no |

Inputs tagged S or Y (replace first): materials.2024-T351.cost_by_route.machined_TO.price_per_kg, materials.2024-T351.cost_by_route.machined_TO.route_cost_per_kg, materials.7075-T6.cost_by_route.machined.price_per_kg, materials.7075-T6.cost_by_route.machined.route_cost_per_kg, materials.7075-T6.cost_by_route.machined_TO.price_per_kg, materials.7075-T6.cost_by_route.machined_TO.route_cost_per_kg, materials.Scalmalloy.cost_by_route.am_TO.price_per_kg, materials.Ti-6Al-4V.cost_by_route.machined_TO.route_cost_per_kg, reference_mass, routes.machined.mass_factor, routes.machined_TO.mass_factor
