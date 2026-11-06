# Ansys cross-check — units_m (REHEARSAL_fake_ansys_crosscheck_template.csv)

**DISCREPANCY: 2 of 11 metrics outside tolerance (max_deformation_mm, load_point_deformation_mm); most likely cause — units: mm vs m (factor 1/1000) (named by 2: max_deformation_mm, load_point_deformation_mm)**

| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |
|---|---|---|---|---|---|---|
| mass_kg | 0.8515 | 0.8515 | 1 | ±2 % | OK |  |
| volume_mm3 | 1.085e+05 | 1.085e+05 | 1 | ±2 % | OK |  |
| max_deformation_mm | 0.1338 | 0.0001365 | 0.00102 | ±10 % | CHECK | units: mm vs m (factor 1/1000); boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction |
| load_point_deformation_mm | 0.08989 | 9.169e-05 | 0.00102 | ±10 % | CHECK | units: mm vs m (factor 1/1000) |
| strain_energy_J | 0.1143 | 0.1166 | 1.02 | ±10 % | OK |  |
| compliance_J | 0.2287 | 0.2333 | 1.02 | ±10 % | OK |  |
| max_von_mises_MPa | 166.7 | 176.8 | 1.06 | ±25 % | OK |  |
| von_mises_outside_MPa | 166.7 | 176.8 | 1.06 | ±15 % | OK |  |
| min_safety_factor | 0.9761 | 0.9209 | 0.9434 | ±15 % | OK |  |
| retained_volume_fraction | 1 | 1 | 1 | ±5 % | OK |  |
| reaction_force_N | 2544 | 2544 | 1 | ±1 % | OK |  |
