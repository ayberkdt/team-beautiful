# Ansys cross-check — room_temperature (REHEARSAL_fake_ansys_crosscheck_template.csv)

**AGREES within tolerance, BUT a signature is hidden inside it — temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical (named by 4: max_deformation_mm, load_point_deformation_mm, strain_energy_J, compliance_J)**

| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |
|---|---|---|---|---|---|---|
| mass_kg | 0.8515 | 0.8515 | 1 | ±2 % | OK |  |
| volume_mm3 | 1.085e+05 | 1.085e+05 | 1 | ±2 % | OK |  |
| max_deformation_mm | 0.1338 | 0.1222 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| load_point_deformation_mm | 0.08989 | 0.0821 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| strain_energy_J | 0.1143 | 0.1044 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| compliance_J | 0.2287 | 0.2089 | 0.9134 | ±10 % | OK | temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature (ratio E(T)/E(20) = 0.913): set the temperature in Mechanical |
| max_von_mises_MPa | 166.7 | 176.8 | 1.06 | ±25 % | OK |  |
| von_mises_outside_MPa | 166.7 | 176.8 | 1.06 | ±15 % | OK |  |
| min_safety_factor | 0.9761 | 0.9209 | 0.9434 | ±15 % | OK |  |
| retained_volume_fraction | 1 | 1 | 1 | ±5 % | OK |  |
| reaction_force_N | 2544 | 2544 | 1 | ±1 % | OK |  |
