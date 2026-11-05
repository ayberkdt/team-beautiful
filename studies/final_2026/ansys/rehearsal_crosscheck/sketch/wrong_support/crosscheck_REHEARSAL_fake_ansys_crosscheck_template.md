# Ansys cross-check — wrong_support (REHEARSAL_fake_ansys_crosscheck_template.csv)

**DISCREPANCY: 7 of 11 metrics outside tolerance (max_deformation_mm, load_point_deformation_mm, strain_energy_J, compliance_J, max_von_mises_MPa, von_mises_outside_MPa, min_safety_factor); most likely cause — boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction (named by 3: max_deformation_mm, strain_energy_J, compliance_J)**

| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |
|---|---|---|---|---|---|---|
| mass_kg | 0.8515 | 0.8515 | 1 | ±2 % | OK |  |
| volume_mm3 | 1.085e+05 | 1.085e+05 | 1 | ±2 % | OK |  |
| max_deformation_mm | 0.1338 | 0.3078 | 2.3 | ±10 % | CHECK | boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction |
| load_point_deformation_mm | 0.08989 | 0.2068 | 2.3 | ±10 % | CHECK | no signature matched: compare loads, supports and material assignment step by step |
| strain_energy_J | 0.1143 | 0.263 | 2.3 | ±10 % | CHECK | boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction |
| compliance_J | 0.2287 | 0.526 | 2.3 | ±10 % | CHECK | boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction |
| max_von_mises_MPa | 166.7 | 283.5 | 1.7 | ±25 % | CHECK | singular peak at a fixed support or point/edge load: Ansys conforming tets resolve the re-entrant corner and the peak grows with refinement; compare 'von_mises_outside_MPa' |
| von_mises_outside_MPa | 166.7 | 283.5 | 1.7 | ±15 % | CHECK | stress: voxel staircase lowers/raises local peaks at curved edges; compare at the same point (probe) and with nodal averaging on |
| min_safety_factor | 0.9761 | 0.5742 | 0.5882 | ±15 % | CHECK | safety factor: check which strength Ansys used (Tensile Yield at 22 °C vs at the working temperature) and whether the factor includes the 1.5 ultimate factor |
| retained_volume_fraction | 1 | 1 | 1 | ±5 % | OK |  |
| reaction_force_N | 2544 | 2544 | 1 | ±1 % | OK |  |
