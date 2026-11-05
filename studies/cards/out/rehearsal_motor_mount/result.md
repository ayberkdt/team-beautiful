# Rehearsal A (vibration + fatigue): eVTOL motor-mount arm, invented card, not an official task

Ultimate load 1035 N (limit 600 N); element 2.5 mm; deflection mesh factor 1.191; stress check 1.0000.

| Option | Retained volume | Mass (g) | Utilisation per check | Deflection (mm) | f1 (Hz) | Governs | Life CO₂ (kg) |
|---|---:|---:|---|---:|---:|---|---:|
| AlSi10Mg TO + AM | 30 % | 72 | strength 0.44 · frequency 0.93 · fatigue 0.36 | 0.458 | 161 | frequency | 1314 |
| Scalmalloy TO + AM | 30 % | 72 | strength 0.20 · frequency 0.95 · fatigue 0.32 | 0.478 | 158 | frequency | 1327 |
| 7075-T6 TO + machined | 30 % | 76 | strength 0.19 · frequency 0.93 · fatigue 0.14 | 0.460 | 161 | frequency | 1384 |
| Ti-6Al-4V TO + AM | 30 % | 120 | strength 0.12 · frequency 0.76 · fatigue 0.11 | 0.300 | 198 | frequency | 2187 |

2-D plane stress; element-centre von Mises excluding elements near the load and supports; deflection multiplied by the 4x-mesh factor; yield at ultimate as the allowable; f1 from the solid elements with consistent mass; fatigue: Goodman on peak unit stress, no notch factor
