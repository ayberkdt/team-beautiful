# Ansys cross-check — room_temperature (REHEARSAL_fake_ansys_crosscheck_template.csv)

**AGREES within tolerance, BUT a signature is hidden inside it — temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical (named by 4: max_deformation_mm, load_point_deformation_mm, strain_energy_J, compliance_J)**

| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |
|---|---|---|---|---|---|---|
| mass_kg | 1.996 | 1.996 | 1 | ±2 % | OK |  |
| volume_mm3 | 2.543e+05 | 2.543e+05 | 1 | ±2 % | OK |  |
| max_deformation_mm | 0.1579 | 0.1442 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| load_point_deformation_mm | 0.08713 | 0.07958 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| strain_energy_J | 0.1084 | 0.09903 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| compliance_J | 0.2168 | 0.1981 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| max_von_mises_MPa | 162.2 | 171.9 | 1.06 | ±25 % | OK |  |
| von_mises_outside_MPa | 102.8 | 108.9 | 1.06 | ±15 % | OK |  |
| min_safety_factor | 1.584 | 1.494 | 0.9434 | ±15 % | OK |  |
| retained_volume_fraction | 1 | 1 | 1 | ±5 % | OK |  |
| reaction_force_N | 2490 | 2490 | 1 | ±1 % | OK |  |
