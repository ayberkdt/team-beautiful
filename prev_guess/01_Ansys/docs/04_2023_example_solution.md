# 04 · Example solution of the 2023 Ansys task (rehearsal)

Prepared: 2026-10-25. Task card: [prev_guess/00_general/past_competitions/Ansys-challenge.pdf](../../00_general/past_competitions/Ansys-challenge.pdf) [D].

**Purpose:** to be able to set up the same chain within minutes when the challenge is announced. This is a rehearsal. The numbers are given as the tools produced them; **assumptions** are marked line by line. In the real task, change the assumptions according to the requirements.

**Requirements (from the card):**
- Cruise range ≥ 1300 km, 30 min loiter.
- Stall 150 km/h, Vmax 500 km/h.
- Service ceiling 10 000 m, climb 10 m/s.
- Take-off run 800 m.
- 4 crew + 10 passengers + 200 kg equipment.

The card cites Raymer and Anderson as sources, leaves configuration/structure/stability out of scope, and asks for a mission plan with STK as the second leg [D].

---

## 1. Weight and constraint diagram

```bash
python -m aerokit sizing raymer
```

The default values are this task's requirements. Output (2026-10-25, `aerokit` version; the numbers are the same as the earlier `hesap` output):

```
Constraint diagram (W/S at the stall limit)
Constraint           P/W (W/N)  Power (kW)
-------------------  ---------  ----------
Climb 10 m/s (SL)        17.70        1037
Ceiling 10000 m          28.45        1667
Vmax 500 km/h (0 m)      28.38        1662
Take-off run 800 m       10.88         637

Quantity                Value                  Source / assumption
----------------------  ---------------------  ------------------------------------
Payload + crew          1474 kg                91 kg/person (Raymer example 200 lb)
L/Dmax · e · CD0        14.1 · 0.783 · 0.0280  KLD 11, Swet/Sref 5.5 assumed
Mission fraction Wx/W0  0.8530                 Raymer Table 3.2 + Breguet
Wf/W0 · We/W0           0.156 · 0.597          Raymer Table 3.1 (twin turboprop)
Take-off mass W0        5974 kg                fixed-point iteration
W/S · wing area         2127 N/m² · 27.5 m²    CLmax landing 2
Installed power (SL)    1667 kW                governing: Ceiling 10000 m

Result: W0 ≈ 5974 kg, S ≈ 27.5 m², power ≈ 1667 kW (Ceiling 10000 m governs).

> *Update 2026-10-25:* `sizing design` now couples engine mass to installed power (docs/07 §7). With its
> defaults the same requirements give **6288 kg, 29.0 m², 1755 kW**; `"power_weight_coupling": "off"` in the
> assumptions file reproduces the numbers above.
```

| Input | Value | Source |
|---|---|---|
| Empty weight regression | A 0.96 · C −0.05 (W0 lb) | [D] Raymer Table 3.1, VT AOE 4065 A4 slide 55 |
| Warm-up-takeoff / climb / landing fraction | 0.970 / 0.985 / 0.995 | [D] Raymer Table 3.2, VT A4 |
| Reserve + trapped fuel | ×1.06 | [D] VT A4 |
| Turboprop C_bhp cruise / loiter | 0.5 / 0.6 lb/(hp·h) | [D] METU AE172 lecture 5 |
| Propeller efficiency | 0.8 | [S] Raymer Table 3.4 |
| For propellers, cruise L/D = (L/D)max, loiter 0.866·(L/D)max | | [A] |
| Mass per person | 91 kg | [D] Raymer example 4 people = 800 lb |
| AR | 9 | **assumption** (comparable aircraft: C-212 AR 10, CN-235 AR 11.27 [A]) |
| L/Dmax = 11·√(AR/5.5) | 14.1 | [A] K_LD 11 (CSV, attributed to Raymer); Swet/Sref 5.5 **assumption** |
| Oswald e | 0.783 | [A] Raymer straight-wing formula |
| CLmax landing / take-off / clean | 2.0 / 1.7 / 1.5 | [D] **choice** within the ranges of Scholz Table 5.1 |
| Power lapse P/P_DS | σ | **assumption** (no engine data) |
| Propeller efficiency at take-off / rolling μ | 0.6 / 0.03 | **assumption** |
| Loiter speed | 250 km/h | **assumption** |

**Interpretation** [Y]:
- **The governing constraint is the 10 000 m ceiling.** *Correction (2026-10-25, `aerokit.design.sensitivity.tornado`):* the power lapse is **not** the most sensitive assumption. Varying P/P_SL = σⁿ with n from 0.7 to 1.0 changes the installed power by only 5 kW (1662–1667 kW), because the Vmax 500 km/h constraint (28.38 W/N) is almost equal and takes over when the ceiling relaxes. The largest sensitivity is K_LD: ±10 % gives 1540–2116 kW, followed by propeller efficiency and Swet/Sref (tornado in `sizing design` report).
- The ceiling and Vmax 500 km/h constraints are almost equal, both require ~1.66 MW.
- The 800 m take-off is easily met.

## 2. Comparison with similar aircraft

**The design falls in the band of the King Air 350.** It is the only comparable aircraft that meets the ceiling and speed pair [A, Wikipedia/aeropedia spec sections].

| Aircraft | MTOW (kg) | S (m²) | Power (kW) | Cruise (km/h) | Ceiling (m) |
|:---|---:|---:|---:|---:|---:|
| This design (calculation) | 5 974 | 27.5 | 1 667 | – | 10 000 (requirement) |
| King Air 350 | 6 805 | 28.8 | 1 566 | 558 | 10 668 |
| Pilatus PC-12NG (single engine) | 4 740 | 25.8 | 890 | 528 | 9 144 |
| Dornier 228NG | 6 575 | 32.0 | 1 158 | 413 | 7 620 |
| CASA C-212-400 | 7 700 | 41.0 | 1 342 | 354 | 7 925 |

The power column is number of engines × engine power. King Air 350 2×783 kW, Do 228NG 2×579 kW, C-212 2×671 kW [A].

## 3. Wing planform

```bash
python -m aerokit geometry planform --S 27.5 --AR 9 --taper 0.5
```

Output: b = 15.73 m, c_root = 2.33 m, c_tip = 1.17 m, MAC = 1.81 m (y = 3.50 m). Taper 0.5 **assumption**.

## 4. Wing root structural check

```bash
python -m aerokit mechanics wing --mass 5974 --b 15.73 --c-root 2.33 --c-tip 1.17 --box-b 1.05 --box-h 0.29 --t-skin 0.004 --t-spar 0.005 --panel-b 0.10 --material 7075-T6
```

```
Quantity                  Value        Note
------------------------  -----------  -----------------------
Root shear (limit)           91.85 kN
Root moment (limit)       313.95 kN·m
Skin bending stress         231.2 MPa  at limit load
Spar shear stress            31.7 MPa  webs carry the shear
MS yield (limit)                +1.18  Fty 503 MPa
MS ultimate (×1.5)              +0.65  Ftu 572 MPa
MS panel buckling (×1.5)        +0.22  σ_cr 423.5 MPa, b 0.1 m

Assumptions: Schrenk distribution, no wing-weight relief, constant box section at the root, n = 3.14 (FAR 23.337 normal category).

Result: Critical mode buckling, MS = +0.22 (sufficient).
```

**Assumptions:**
- Box width 1.05 m (≈ 45% chord, spars at ~15% and ~60%).
- Box height 0.29 m (≈ 12% chord).
- Skin 4 mm, spar web 5 mm.
- Stringer/rib spacing 0.10 m.
- No load relief from the wing weight (conservative).

**Observation** [H]: with a panel spacing of 0.15 m the buckling MS would be −0.46 (σ_cr 188.2 MPa; `mechanics wing --panel-b 0.15` and the old `hesap` package in the archive give the same result, 2026-10-25; the −0.44 in the previous version of this note was wrong). The critical mode is **buckling**, not yield. This is the first thing to verify in Mechanical.

## 5. What goes into the presentation

1. On a single slide: requirements → constraint diagram → selected point (W/S, P/W).
2. Assumption table and the most sensitive assumption: K_LD (drag estimate), from the tornado chart.
3. Comparison with similar aircraft: the design is in the King Air 350 band.
4. Wing root MS table and that the critical mode is buckling.
5. **Sustainability:** starting from the fuel fraction 0.156, the fuel mass including reserves (≈ 930 kg [H: 0.156 × 5974]). Improvement levers: higher AR, lower C_bhp, SAF compatibility.
6. The second leg of the card was the STK mission plan; this document does not cover it.
