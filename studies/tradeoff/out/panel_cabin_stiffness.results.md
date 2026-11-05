# A320 cabin panel, stiffness-limited, monolithic plate (per 3 kg of the 2024-T3 reference panel)

Index case `panel_stiff` · score: co2_total_kg

| Rank | Material | Route | Mass (kg) | CO₂ production (kg) | CO₂ use (kg) | CO₂ total (kg) | P(best) |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | CFRP QI IM7/8552 | autoclave_layup | 1.832 | 84 | 33349 | 33433 | 1.00 |
| 2 | CF/PEEK 5HS | thermoplastic_press | 2.005 | 58 | 36500 | 36558 | 0.00 |
| 3 | Flax/epoxy | autoclave_layup | 2.584 | 52 | 47030 | 47082 | 0.00 |
| 4 | Al-Li 2050-T84 | sheet_formed | 2.870 | 49 | 52236 | 52284 | 0.00 |
| 5 | Glass/phenolic 7781 | autoclave_layup | 2.947 | 76 | 53638 | 53714 | 0.00 |
| 6 | 2024-T3 | sheet_formed | 3.000 | 51 | 54605 | 54656 | 0.00 |

Pareto set (mass_kg, co2_total_kg): CFRP QI IM7/8552 / autoclave_layup

| Factor | Range | Tag | Margin at low (kg) | Margin at high (kg) | Reverses choice |
|---|---|---|---:|---:|---|
| reference_mass | 2–5 kg | Y | 2084 | 5209 | no |
| lifecycle.fuel_per_kg_per_flight | 0.07–0.16 kg fuel / kg carried / flight | A | 1813 | 4176 | no |
| lifecycle.flights | 30000–60000 flights over life | D | 1944 | 3913 | no |
| materials.CFRP QI IM7/8552.co2_per_kg | 14.9–46.2 kg CO2 / kg | H | 3146 | 3071 | no |
| materials.CF/PEEK 5HS.co2_per_kg | 14.7–44.9 kg CO2 / kg | H | 3105 | 3178 | no |
| lifecycle.grid_co2_per_MJ | 0.0112–0.1543 kg CO2 / MJ electricity | D | 3147 | 3083 | no |
| routes.autoclave_layup.process_MJ_per_kg | 100–300 MJ/kg | S | 3140 | 3112 | no |
| routes.autoclave_layup.buy_to_fly | 1.1–1.5 - | Y | 3139 | 3113 | no |
| routes.thermoplastic_press.buy_to_fly | 1.1–1.4 - | Y | 3121 | 3135 | no |
| routes.thermoplastic_press.process_MJ_per_kg | 11–16 MJ/kg | S | 3125 | 3126 | no |
| materials.2024-T3.co2_per_kg | 6.6–15.1 kg CO2 / kg | D | 3126 | 3126 | no |
| materials.2024-T3.eol_credit_per_kg | 4.07–12.49 kg CO2 / kg | H | 3126 | 3126 | no |
| materials.Al-Li 2050-T84.co2_per_kg | 6.6–15.1 kg CO2 / kg | Y | 3126 | 3126 | no |
| materials.Al-Li 2050-T84.eol_credit_per_kg | 4.07–12.49 kg CO2 / kg | Y | 3126 | 3126 | no |
| materials.CFRP QI IM7/8552.eol_credit_per_kg | 0–23 kg CO2 / kg | S | 3126 | 3126 | no |
| materials.Glass/phenolic 7781.co2_per_kg | 7.47–8.26 kg CO2 / kg | D | 3126 | 3126 | no |
| materials.Flax/epoxy.co2_per_kg | 3.4–4 kg CO2 / kg | H | 3126 | 3126 | no |
| materials.CF/PEEK 5HS.eol_credit_per_kg | 0–23 kg CO2 / kg | Y | 3126 | 3126 | no |
| routes.sheet_formed.buy_to_fly | 1.1–1.6 - | Y | 3126 | 3126 | no |
| routes.sheet_formed.process_MJ_per_kg | 3–5 MJ/kg | S | 3126 | 3126 | no |

Inputs tagged S or Y (replace first): materials.Al-Li 2050-T84.co2_per_kg, materials.Al-Li 2050-T84.eol_credit_per_kg, materials.CF/PEEK 5HS.eol_credit_per_kg, materials.CFRP QI IM7/8552.eol_credit_per_kg, reference_mass, routes.autoclave_layup.buy_to_fly, routes.autoclave_layup.mass_factor, routes.autoclave_layup.process_MJ_per_kg, routes.sheet_formed.buy_to_fly, routes.sheet_formed.mass_factor, routes.sheet_formed.process_MJ_per_kg, routes.thermoplastic_press.buy_to_fly, routes.thermoplastic_press.mass_factor, routes.thermoplastic_press.process_MJ_per_kg
