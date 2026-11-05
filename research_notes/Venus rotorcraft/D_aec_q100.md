# D_aec_q100 — Automotive IC operating temperature grades

## Citation
Automotive Electronics Council. *AEC-Q100 Rev-H: Failure Mechanism Based Stress Test
Qualification for Integrated Circuits.* September 11, 2014.
http://www.aecouncil.com/Documents/AEC_Q100_Rev_H_Base_Document.pdf

## What I read
48-page standard (text extraction); §1.3.4 Table 1 and the stress-test table rows (TC, PTC,
HTSL, HTOL).

## Numbers [D-ag]
**Table 1 — Part operating temperature grades (ambient):**
| Grade | Ambient range |
|---|---|
| 0 | −40 °C to +150 °C |
| 1 | −40 °C to +125 °C |
| 2 | −40 °C to +105 °C |
| 3 | −40 °C to +85 °C |
(Rev H eliminated Grade 4, 0…+70 °C.)
- HTOL: Grade 0 +150 °C Ta 1000 h; Grade 1 +125 °C; Grade 2 +105 °C; Grade 3 +85 °C (1000 h).
- Temperature cycling: Grade 0 −55…+150 °C 2000 cycles; Grade 1 −55…+150 °C 1000 cycles;
  Grade 2 −55…+125 °C 1000 cycles; Grade 3 −55…+125 °C 500 cycles.
- Power temperature cycling: Grade 0 −40…+150 °C, Grade 1 −40…+125 °C, Grades 2–3 −40…+105 °C,
  1000 cycles.
- HTSL (storage): Grade 0 +175 °C 1000 h or +150 °C 2000 h; Grade 1 +150 °C 1000 h or +175 °C
  500 h; Grades 2–3 +125 °C 1000 h or +150 °C 500 h.

## Relevance (mine)
Grade 1 (+125 °C ambient) electronics would tolerate the 50–60 km environment with margin for
self-heating; the Li-ion cells (≤ 45–60 °C) and NdFeB magnets (80 °C N-grade), not the
electronics, set the thermal ceiling of the vehicle.

## Caveats
Ambient (not junction) qualification; radiation tolerance not covered.
