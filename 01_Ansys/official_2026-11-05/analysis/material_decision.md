# Material decision — S275N vs Al 2618-T6 vs Ti-8Al-1Mo-1V (organisers' three candidates)

Written 5 Nov 2026. Data: the organisers' Granta EduPack 2026 R1 selection report (p.7–13, all at 23 °C) [D-org],
their initial-design eco-audit report [D-org], our FEA of the organisers' CAD [K], and our 300 °C catalogue (MIL-HDBK-5J,
EN 1993-1-2) [D]/[Y] for the temperature the card asks for. Every number comes from a script in this folder:
`organiser_materials.py`, `decision_indices.py`, `material_swap.py`, `screening.py`, `evaluate_layouts.py`.

## 1. Decision in one line

**Ti-8Al-1Mo-1V** — the only one of the three that meets every requirement of the card at > 300 °C; its strength
margin lets topology optimisation remove material until stiffness (not strength) governs, which gives the lightest
bracket and therefore the lowest life CO₂, because the use phase is 89–97 % of the life footprint per kg of part (Ti 88.9 %, S275N 97.3 %; `decision_indices.py`). **Al 2618-T6** is the
runner-up only if the jury accepts "≥ 300 °C" (their Granta filter) instead of "> 300 °C" (their card): on the same
topology layouts it would be slightly lighter (18.4 vs 21.3 kg, 6.5 vs 8.1 t) and far cheaper, but it sits exactly at
its temperature limit and has no strength data at 300 °C. **S275N** is the reference to replace.

Full requirement-by-requirement table, generated from the verified record of the organisers' report (183 rows × 3
materials, `organiser_table_full.md`): `conditions_matrix.md`.

## 2. Requirements check (card → organisers' data)

| Card requirement | S275N | Al 2618-T6 | Ti-8Al-1Mo-1V | Source |
|---|---|---|---|---|
| Working temperature > 300 °C | 471–501 °C ✔ | **250–300 °C ✘ (upper end = 300)** | 407–455 °C ✔ | report p.9 "Maximum service temperature" |
| Castable or 3-D printable | passes Granta stage 2; "Metal casting: Unsuitable" | passes stage 2; "Metal casting: Unsuitable" | passes stage 2; "Metal casting: Limited use" | report p.5, p.10 |
| K1c ≥ 10 MPa·m½ | 26.4–38.1 ✔ | 31–34 ✔ | 65–75 ✔ | report p.9 |
| Oxidation at 500 °C (margin above 300 °C) | Acceptable | **Unacceptable** | Acceptable | report p.11 |
| Stress-corrosion cracking | Slightly susceptible | **Highly susceptible** | Slightly susceptible | report p.11 |
| Fatigue strength at 10⁷ cycles | 194–233 MPa | 118–130 MPa | 529–579 MPa | report p.9 |
| Condition (heat treatment) | Normalized | **T6 — solution treated + artificially aged** (over-ages above its ageing temperature) | Single annealed (1450 °F, 8 h) | report p.7; MIL-HDBK-5J p.5-27 |
| Thermal expansion (µstrain/°C) — mismatch with a steel/Ti mount at ΔT ≈ 277 K | 11–13 | **21.5–22.6** | 8.73–9.18 | report p.9 |
| Galvanic potential (V) — with steel bolts (−0.51…−0.43) | −0.51…−0.43 | **−0.78…−0.70** (anodic to steel) | −0.13…−0.05 | report p.10 |
| Functional recycle | Yes | No | No | report p.13 |
| Critical elements > 5 wt % / sourcing risk | No / Low | Yes / **Very high** | Yes / Medium | report p.10 |

At 300 °C itself the organisers give no values (report p.14: functional temperature 23 °C). Our catalogue
(`catalogue/materials_catalogue.md`): S275N Fty × 0.78 and E × 0.80 at 300 °C (EN 1993-1-2) [D]; Ti-8-1-1 keeps 68.3 % of
Fty and 86.9 % of E (MIL-HDBK-5J Fig. 5.3.2.1.1/.4) [D-ag]; **2618-T61 has no design data above 204 °C**, and after 1000 h
at 204 °C keeps only 60 % of Ftu (MIL-HDBK-5J Fig. 3.2.13.1.1(a)) [D-ag] — the over-ageing of a T6 alloy run hotter
than its ageing temperature.

## 3. Which material index matters for this part

`decision_indices.py` [K], organiser mid-range values:

| Index | S275N | Al 2618-T6 | Ti-8-1-1 | What it predicts |
|---|---|---|---|---|
| ρ/E (tie stiffness) | 37.3 (1.00) | 37.2 (1.00) | 35.3 (**0.95**) | mass of a stiffness-limited, topology-optimised part (members in tension/compression) |
| ρ/√E (beam stiffness, organisers' chart) | 541 (1.00) | 320 (**0.59**) | 393 (0.73) | mass of a fixed-length beam with free section — not the shape a topology result takes |
| ρ/Fy (strength) | 38.3 (1.00) | 8.6 (0.22) | 5.8 (**0.15**) | mass of a strength-limited part |
| Production CO₂ (virgin + powder forming), kg/kg | 9.0 | 17.1 | 42.0 | report p.11–12 |
| Life CO₂ per kg of part (card settings) | 346 | 354 | 379 | use phase alone 337 kg/kg |
| Price, USD/kg | 1.26 | 3.30 | 24.6 | report p.8 |

Reading: on stiffness all three metals are the same (E/ρ: S275N 25.5–28.1, 2618 26.1–27.7, Ti-8-1-1 27.7–29.1 MN·m/kg, report p.8 "Specific stiffness"), so a
material change alone does not buy stiffness-limited mass. What separates them is **how far topology optimisation
can thin the part before strength or temperature stops it**: steel stops early (ρ/Fy 38), aluminium and titanium can
go down to the stiffness limit — if their strength survives 300 °C, which only titanium's data show.

## 4. Same geometry, material swapped (no redesign) — `material_swap.py` [K]

| Material | Mass | Max deflection (limit 1.653 mm) | Utilisation 23 °C / 300 °C | Material cost | Life CO₂ |
|---|---|---|---|---|---|
| S275N | 152.3 kg | 0.18 mm | 0.42 / 0.54 | 192 USD | 52.7 t |
| Al 2618-T6 | 53.3 kg | 0.51 mm | 0.27 / n/a | 176 USD | 18.9 t (−64 %) |
| Ti-8-1-1 | 84.9 kg | 0.30 mm | 0.11 / 0.17 | 2087 USD | 32.2 t (−39 %) |

Utilisation = 1.5 × 57.9 MPa / Fy,min (vM outside the hole zones, voxel FEA, `runs/baseline_fixed_bores/report.md`).

## 5. Redesign: topology layouts × materials

One topology run serves every material (stress is E-independent, displacement ∝ 1/E): `runs/topo_fixed_bores/`
(SIMP, 40 k voxels, 4 load cases, bores kept as non-design rings = 12.6 % of the part, layouts 35 / 25 / 20 %);
evaluation `evaluate_layouts.py` → `layout_evaluation.md` [K]. The 20 % layout breaks: on the conforming T10 mesh its
stress is 6.1× the voxel value (thin members), so it is not usable.

| Material | Lightest passing layout | Mass | Life CO₂ | Material cost | Limited by |
|---|---|---|---|---|---|
| S275N (reference) | 35 % | 52.7 kg | 18.2 t | 66 USD | strength (util 0.94 at 23 °C; fails at 300 °C with the EN 0.78 knock-down) |
| Al 2618-T6 (fails > 300 °C) | 35 % | 18.4 kg | 6.5 t | 61 USD | stiffness (1.49 mm at 23 °C; no E or strength data at 300 °C) |
| **Ti-8Al-1Mo-1V** | **25 %, T10-verified** | **21.3 kg** | **8.1 t** | **524 USD** | stiffness at 300 °C (1.53 mm of 1.653) |

Chosen design, checked on the conforming 10-node mesh of the layout STL (52 521 elements), `final_choice.py` [K]:

| Check | 23 °C | 300 °C | Limit |
|---|---|---|---|
| Max displacement (worst case LC1b) | 1.33 mm | 1.53 mm | 1.653 mm (L/400) |
| Utilisation 1.5 × σ_vM / Fy (σ = 257 MPa at (603, 95, 136) mm) | 0.51 | 0.75 | ≤ 1 |
| Mass | 21.3 kg vs 152.3 kg steel → **−86 %** | | |
| Life CO₂ (first life, card settings) | 8.1 t vs 52.6 t → **−84.6 %** | | |
| Material cost | 524 vs 192 USD → +332 USD = **7.5 USD per tonne CO₂ avoided** | | |

The voxel model gives 1.74 mm at 300 °C for the same layout (fails); the conforming T10 mesh — the Ansys SOLID187
analogue, validated in doc 22 §4 — gives 1.53 mm (passes, 7 % margin). Ansys should be run on this layout to confirm.
300 °C values use our catalogue knock-downs (Ti E × 0.869, Fty × 0.683, MIL-HDBK-5J) because the organisers' data are
at 23 °C.

Appendix — the other names printed on report p.1 (no values given by the organisers; data `named_materials.json`,
mostly secondary sources): only Al 8009 RS could compete on mass (bound 14.6 kg) but its TL toughness at 316 °C is 9.5 <
10 MPa·m½; the others are eliminated by temperature, process or on the shared layouts (`screening.md`). The decision
above uses the organisers' three only. Screening-method note: did the gate decide correctly without topology? Correction made after this run: the first version bounded
strength by assuming stress ∝ 1/f; the run shows stress grows SLOWER (×1.86 at 35 %, ×3.48 at 25 % instead of ×2.86 /
×4.0) because the optimiser removes the least-stressed material first, so that "bound" was not a lower bound (it
predicted ≥ 64.5 kg for S275N; the 35 % layout gives 52.7 kg). Displacement grows FASTER than 1/f (×2.87 / ×4.90), so
the stiffness bound is rigorous. The gate now eliminates only on data (G0–G3) and on the rigorous stiffness / non-design
bound (G5): with the Ti design as reference the bronze is dominated (≥ 9.4 t > 8.1 t); the plain steels survive the gate
(bound 6.6 t) and are then rejected on the shared layouts at no extra topology cost — they need ≥ 35 % volume
(25 % fails strength, utilisation 1.17–1.88) → ≥ 52.7 kg, 18.2 t.

## 6. Why not the other two

- **S275N:** the card asks to replace it; optimised, its strength stops it at the 35 % layout (utilisation 0.94 at
  23 °C, above 1 at 300 °C): 52.7 kg and 18.2 t CO₂ — 2.5× the mass and 2.2× the CO₂ of the titanium design (§5).
- **Al 2618-T6:** passes the organisers' Granta filter only because "any part of record within selection" lets a
  250–300 °C range pass "≥ 300"; the card says "> 300 °C". At the working temperature it has no sourced strength, its
  oxidation rating at 500 °C is "Unacceptable", it is "Highly susceptible" to stress-corrosion cracking, casting is
  "Unsuitable" and L-PBF printing is only reported for chemically modified 2618. Two more points from the organisers'
  own record: its expansion (21.5–22.6 µstrain/°C) is about twice a steel mount's (11–13), so heating to 300 °C on
  fixed bolts adds thermal stress, and its galvanic potential (−0.78…−0.70 V) makes it the anode against steel bolts;
  its sourcing risk is rated "Very high". Honest framing for the jury: best on
  cost and beam index, disqualified on the one requirement that defines an engine-cowling bracket.

## 7. Risks of the choice and how we answer them

| Risk | Evidence | Answer |
|---|---|---|
| Price ~19× steel per kg | 24.6 vs 1.26 USD/kg (report p.8) | redesigned mass in §5 (screening lower bound 15.5 kg vs 152.3 kg steel), and the card ranks CO₂ over the full life, where the use phase dominates |
| Production CO₂ 42 kg/kg | report p.11–12 | the use phase costs 337 kg CO₂ per kg of part per year; every kg removed outweighs production 8× |
| Process: casting "Limited use", no peer-reviewed L-PBF study of Ti-8-1-1 | report p.10; catalogue §4 | powder route is in Granta's stage 2; fallback with the same layout: Ti-6Al-4V L-PBF (process-proven) — flagged as outside the list |
| "Single annealed" gives top strength but not top toughness | MIL-HDBK-5J p.5-27 [D] | K1c 65–75 still ≫ 10; propose duplex anneal if the jury asks |
| Sharp lug-root corner (singular peak in T10) | runs/baseline + peak probe: (327, 100, 100) mm | add a fillet there in the redesign; judge stress away from the singular edge |

## 8. Open questions for the mentor

1. Is "> 300 °C" strict (card) or "≥ 300 °C" (their Granta filter)? It decides whether 2618 is admissible.
2. May the redesign change the heat treatment (single → duplex anneal)?
3. Is the 196-record passing list available? Only 10 names are printed (report p.1).
