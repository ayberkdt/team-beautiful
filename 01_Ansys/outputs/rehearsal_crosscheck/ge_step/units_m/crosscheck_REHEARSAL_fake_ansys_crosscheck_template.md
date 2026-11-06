# Ansys cross-check — units_m (REHEARSAL_fake_ansys_crosscheck_template.csv)

**DISCREPANCY: 2 of 11 metrics outside tolerance (max_deformation_mm, load_point_deformation_mm); most likely cause — units: mm vs m (factor 1/1000) (named by 1: max_deformation_mm)**

| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |
|---|---|---|---|---|---|---|
| mass_kg | 1.996 | 1.996 | 1 | ±2 % | OK |  |
| volume_mm3 | 2.543e+05 | 2.543e+05 | 1 | ±2 % | OK |  |
| max_deformation_mm | 0.1579 | 0.0001611 | 0.00102 | ±10 % | CHECK | units: mm vs m (factor 1/1000); boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction |
| load_point_deformation_mm | 0.08713 | 8.887e-05 | 0.00102 | ±10 % | CHECK | no signature matched: compare loads, supports and material assignment step by step |
| strain_energy_J | 0.1084 | 0.1106 | 1.02 | ±10 % | OK |  |
| compliance_J | 0.2168 | 0.2212 | 1.02 | ±10 % | OK |  |
| max_von_mises_MPa | 162.2 | 171.9 | 1.06 | ±25 % | OK |  |
| von_mises_outside_MPa | 102.8 | 108.9 | 1.06 | ±15 % | OK |  |
| min_safety_factor | 1.584 | 1.494 | 0.9434 | ±15 % | OK |  |
| retained_volume_fraction | 1 | 1 | 1 | ±5 % | OK |  |
| reaction_force_N | 2490 | 2490 | 1 | ±1 % | OK |  |
