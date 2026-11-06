# Material screening gate — which materials go to the topology evaluation

12 materials in, 6 survive. Command: `python -I analysis/screening.py` (seconds). Baseline FEA: vM 57.9 MPa outside the hole zones, 0.2047 mm at E = 182.7 GPa (runs/baseline_fixed_bores). Bounds are screening estimates [Y], not designs.

| Gate | Material | Source | Lower-bound mass (kg) | Governs | Life CO₂ lower bound (t) | Reason |
|---|---|---|---:|---|---:|---|
| pass | Titanium, near-alpha alloy, Ti-8Al-1Mo-1V, single annealed | org (values) | 15.5 | stiffness | 5.9 | survives |
| pass | Carbon steel, AISI 1010, annealed | org (name only) | 19.2 | min gauge | 6.6 | survives |
| pass | Carbon steel, AISI 1015, annealed | org (name only) | 19.2 | min gauge | 6.6 | survives |
| pass | Carbon steel, AISI 1015, normalized | org (name only) | 19.2 | min gauge | 6.6 | survives |
| pass | Carbon steel, AISI 1020, annealed | org (name only) | 19.2 | min gauge | 6.6 | survives |
| pass | Carbon steel, AISI 1020, as rolled | org (name only) | 19.2 | min gauge | 6.6 | survives |
| G5 | Bronze, CuAl10, cold worked | org (name only) | 27.8 | stiffness | 9.4 | dominated: best possible 9.4 t CO2 > Titanium, near-alpha alloy, Ti-8Al-1Mo-1V, single annealed topo 25 % (T10-verified) 8.1 t |
| G0 | Structural steel, S275N, normalized | org (values) | 19.2 | min gauge | 6.6 | reference material to be replaced (card) |
| G1 | Al(2009)-15%SiC(w) MMC powder | org (name only) | 13.6 | stiffness | 4.7 | aluminium: no Tmax in data, family rule [Y] (< 300 °C) |
| G1 | Aluminum, 2618, T6 | org (values) | 16.3 | stiffness | 5.8 | max service temperature (250, 300) °C, card needs > 300 °C |
| G2 | Bake hardening steel, YS260, cold rolled | org (name only) | 19.2 | min gauge | 6.6 | no casting / AM / powder route in its data (-rolled automotive sheet (EN 10268 HC260B); grade is...) |
| G3 | Aluminum, 8009, rapid solidification | org (name only) | 14.6 | stiffness | 5.0 | K1c 9.5 MPa m^0.5 at 316 °C (TL) < 10 at working temperature |
