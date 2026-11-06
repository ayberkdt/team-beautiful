# Requirements re-check (5 Nov 2026, 12:35–12:40)

Re-read from the source files in `Files.zip` (sha256 53dd8d51…, unchanged) and the two organiser PDFs; organiser values
machine-diffed with `python -I analysis/verify_organiser_values.py "files/Material selection report Ideathon challenge.pdf"`
→ **75 values, 0 mismatches**; eco model vs the initial-design eco report: material −0.04 %, manufacture +0.01 %,
transport −1.0 %, use +0.03 %, disposal 0.0 % (text-extracted), total and EoL compared by eye (52.6 t / −336 kg).

| # | Card text (Ideathon_Challenge_Ansys_2026.docx) | How we apply it | Where | Status |
|---|---|---|---|---|
| 1 | "Working temperature >300°C" | strict ">": upper end of Granta max service temperature must exceed 300 °C | screening.py G1 | ✔ — note: organisers' own Granta filter used "≥ 300", any part of record (report p.4) → 2618 (250–300) passes their filter but not their card; mentor question |
| 2 | "Ability to be casted or 3D printed" | organiser records: Granta stage 2 (AM or casting tree) result, all three passed (report p.5) | screening.py G2 | ✔ — note: report p.10 "Metal casting": S275N Unsuitable, 2618 Unsuitable, Ti-8-1-1 Limited use; the report has no AM-suitability row |
| 3 | "Minimum fracture toughness of 10MPa.m^1/2" | K1c lower end ≥ 10 | G3 | ✔ all three (26.4 / 31 / 65) |
| 4 | "Objectives: minimizing weight, cost and CO2 eq ideally on full life cycle" | report mass, cost (mass × price), life CO₂ for every option | material_swap.py, evaluate_layouts.py | ✔ |
| 5 | "Locations and in between distances of fixed support, or where the load is applied, should stay the same" | 6 bores kept as non-design rings in topology | setup + pipeline | ✔ |
| 6 | "Loading condition 1 static vertical on each hole (0; +/-24kN ; 97kN)" | per PIN hole F = (Fx, Fy, Fz) = (0, ±24, 97) kN; LC1a +24, LC1b −24, LC1c opposite (sensitivity) | setup_official_fixed_bores.json | ✔ interpretation [Y] documented; "vertical" + a y-component is ambiguous → mentor |
| 7 | "Loading condition 2 static torsional 2000N.m (My)" | 2000 N·m about y, split 1000/1000 over the pin bores | setup | ✔ [Y] split |
| 8 | "Factor of Safety of 1.5" | 1.5 × σ_vM,max ≤ Fy (lower end of range) | evaluate_layouts.py | ✔ on yield — confirmed by the mentor 5 Nov ~13:45 (300 °C value still our assumption) |
| 9 | "Max displacement to remain below 1/400 of largest dimension" | 661.01 mm / 400 = 1.653 mm | screening.py, evaluate_layouts.py | ✔ |
| 10 | "Material phase impact should use the virgin grade production value" | CO₂ virgin grade (report p.11) | organiser_materials.py | ✔ |
| 11 | "Manufacturing is considered via metal powder forming process" | "Metal powder forming, climate change" (report p.12) | organiser_materials.py | ✔ |
| 12 | "CO2(transport)=part mass(kg)*500* 0.241" | applied per TONNE: the report gives 18.5 kg for 152 kg (literal kg reading would give 18 316 kg) | organiser_materials.py | ✔ — the card formula's unit is off by 1000; we follow the report |
| 13 | "1 year, 180 days per year, 4000km per day; CO2(use)=part mass(kg)*distance(km)*0.000468" | 720 000 km → 337 kg CO₂ per kg of part | organiser_materials.py | ✔ matches report 5.12e4 kg |
| 14 | "Recycled at end of life" | disposal 0.049 kg/kg (report scaled) + EoL potential −(virgin − recycling) | organiser_materials.py | ✔ matches −336 kg |
| 15 | "Using the provided top candidates materials list and properties … replace the initial design steel" | candidates = the 3 with properties (report p.7–13); the 9 other printed names screened as an extra | screening.py | ✔ |
| 16 | Provided files: "Material card files for simulation discovery" | **not in the zip and not in the two PDFs**; the .dsco holds only the S275N card | — | ✘ missing → ask the mentor; our MatML cards are a stand-in |

Corrections made during this check: `material_decision.md` use-phase share "~90–97 %" → "89–97 %" (Ti 88.9 %); specific
stiffness "26–28" → the report's ranges 25.5–28.1 / 26.1–27.7 / 27.7–29.1 MN·m/kg.
