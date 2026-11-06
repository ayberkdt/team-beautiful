# Rehearsal C (thermal): system bracket between two CFRP frames next to an APU bay, invented card, not an official task

Ultimate load 3450 N (limit 2000 N); element 2.5 mm; deflection mesh factor 1.069; stress check 1.0000.

| Option | Retained volume | Mass (g) | Utilisation per check | Deflection (mm) | f1 (Hz) | Governs | Life CO₂ (kg) |
|---|---:|---:|---|---:|---:|---|---:|
| AlSi10Mg TO + AM | 15 % | 33 | strength 0.61 · deflection 0.40 · thermal 0.67 | 0.202 | – | thermal | 599 |
| 2618-T61 TO + machined | 15 % | 34 | strength 0.47 · deflection 0.37 · thermal 0.52 | 0.185 | – | thermal | 622 |
| 7075-T6 TO + machined | 15 % | 35 | strength 0.67 · deflection 0.43 · thermal 0.75 | 0.213 | – | thermal | 632 |
| Ti-6Al-4V TO + AM | 15 % | 54 | strength 0.17 · deflection 0.27 · thermal 0.16 | 0.137 | – | deflection | 996 |
| Inconel 718 TO + AM | 15 % | 100 | strength 0.10 · deflection 0.14 · thermal 0.13 | 0.071 | – | deflection | 1827 |

Excluded: Scalmalloy (service 150.0 C > 100.0 C: properties fall sharply above 373 K (Mehta et al. 2022, Metals 12:57); yield 319 MPa at 150 C and 60 MPa at 300 C vs 475 MPa at room temperature (Colibrium Additive datasheet 2025-08-21))

2-D plane stress; element-centre von Mises excluding elements near the load and supports; deflection multiplied by the 4x-mesh factor; yield at ultimate as the allowable; thermal: uniform dT, supports held by a structure growing with structure_alpha
