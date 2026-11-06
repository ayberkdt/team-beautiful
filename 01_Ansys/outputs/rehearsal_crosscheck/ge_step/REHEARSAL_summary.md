# REHEARSAL — FAKE ANSYS DATA: one planted error per scenario

Folder `01_Ansys\outputs\cases\ge_step`; fake Ansys numbers = ours × the factors below; verdict from `01_Ansys/scripts/bracket_crosscheck.py`.

| Scenario | Planted | Expected in verdict | Verdict | Caught |
|---|---|---|---|---|
| correct | compliance_J × 1.02, load_point_deformation_mm × 1.02, max_deformation_mm × 1.02, max_von_mises_MPa × 1.06, min_safety_factor × 0.943, strain_energy_J × 1.02, von_mises_outside_MPa × 1.06 | AGREES | AGREES: 11 of 11 compared metrics inside tolerance | yes |
| units_m | load_point_deformation_mm × 0.00102, max_deformation_mm × 0.00102 | units | DISCREPANCY: 2 of 11 metrics outside tolerance (max_deformation_mm, load_point_deformation_mm); most likely cause — units: mm vs m (factor 1/1000) (named by 1: max_deformation_mm) | yes |
| wrong_support | compliance_J × 2.3, load_point_deformation_mm × 2.3, max_deformation_mm × 2.3, max_von_mises_MPa × 1.7, min_safety_factor × 0.588, strain_energy_J × 2.3, von_mises_outside_MPa × 1.7 | boundary conditions | DISCREPANCY: 7 of 11 metrics outside tolerance (max_deformation_mm, load_point_deformation_mm, strain_energy_J, compliance_J, max_von_mises_MPa, von_mises_outside_MPa, min_safety_factor); most likely cause — boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; or a load applied on a different face or direction (named by 3: max_deformation_mm, strain_energy_J, compliance_J) | yes |
| room_temperature | compliance_J × 0.913, load_point_deformation_mm × 0.913, max_deformation_mm × 0.913, strain_energy_J × 0.913 | temperature | AGREES within tolerance, BUT a signature is hidden inside it — temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical (named by 4: max_deformation_mm, load_point_deformation_mm, strain_energy_J, compliance_J) | yes |
