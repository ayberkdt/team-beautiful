# Ansys cross-check — units_m (REHEARSAL_fake_ansys_crosscheck_template.csv)

**DISCREPANCY: 2 of 11 metrics outside tolerance (max_deformation_mm, load_point_deformation_mm); most likely cause — units: mm vs m (factor 1/1000) (named by 1: max_deformation_mm)**

| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |
|---|---|---|---|---|---|---|
| mass_kg | 1.996 | 1.996 | 1 | ±2 % | OK |  |
| volume_mm3 | 2.543e+05 | 2.543e+05 | 1 | ±2 % | OK |  |
| max_deformation_mm | 0.6882 | 0.0007019 | 0.00102 | ±10 % | CHECK | units: mm vs m (factor 1/1000); boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction |
| load_point_deformation_mm | 0.4853 | 0.000495 | 0.00102 | ±10 % | CHECK | no signature matched: compare loads, supports and material assignment step by step |
| strain_energy_J | 8.296 | 8.462 | 1.02 | ±10 % | OK |  |
| compliance_J | 16.59 | 16.92 | 1.02 | ±10 % | OK |  |
| max_von_mises_MPa | 1070 | 1134 | 1.06 | ±25 % | OK |  |
| von_mises_outside_MPa | 1070 | 1134 | 1.06 | ±15 % | OK |  |
| min_safety_factor | 0.1521 | 0.1435 | 0.9434 | ±15 % | OK |  |
| retained_volume_fraction | 1 | 1 | 1 | ±5 % | OK |  |
| reaction_force_N | 4.226e+04 | 4.226e+04 | 1 | ±1 % | OK |  |
