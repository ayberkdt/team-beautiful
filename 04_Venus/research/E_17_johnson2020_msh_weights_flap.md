# E_17 — Johnson et al. 2020, Mars Science Helicopter: weight model, design rules, flap dynamics

- **Citation:** Johnson, W., et al. (2020), "Mars Science Helicopter Conceptual Design", NASA/TM-2020-220485
  (full author list not re-checked this session; see the earlier note C_johnson2020_msh).
- **URL:** `https://ntrs.nasa.gov/api/citations/20200002139/downloads/1405_Johnson_Final_080420%5B1%5D.pdf`, accessed
  2026-11-05; local `D:\tmp_ideathon\venus_research\pdf\msh2020.pdf`. Read level: pp. 17–23 and 42 (text) and the
  weights list on p. 19 rendered as an image to read the exponents **[D]**.

## Design rules [D] (p. 17–18)
- Payload 2.02 kg, 35 W; avionics 1.2 kg; contingency 20 % of empty weight; battery reserve 20 % of mission energy.
- Design blade loading C_T/σ = 0.11 (Mars Helicopter MH: 0.10, which allows +40 % thrust for control).
- Hover tip Mach 0.7 (a = 233.1 m/s on Mars at −50 °C → 163.2 m/s tip speed); cruise 30 m/s = minimum-power speed;
  advancing-tip Mach 0.83.
- Motors sized to **150 % of hover power**; direct drive (~1200 rpm coax, ~3000 rpm hexacopter); efficiency 68 %
  (motor + controller 80 %, servo power 15 % of rotor power).
- Battery: 278 Wh/kg cell, 230 Wh/kg pack, 218.5 Wh/kg end of life; 420 Wh/L; usable 70 % (10–80 % DoD); discharge
  efficiency 88–92 %; average ~10C for a 6 min mission.
- Solar: 2.0 kg/m² cells.
- Drag: fuselage D/q = 1.2 · 27.5 (W/1000)^(2/3) m² (W in kg); landing gear 0.05 m²; rotor hub C_D 0.003 × disk area
  (0.0015 faired), pylon 0.015; hexacopter arms 0.003 × disk area.

## Weight model, NDARC calibrated to the Mars Helicopter [D] (p. 19)
| Group | Relation |
|---|---|
| Blade | W_blade = 1.1 · A_blade kg (A_blade = blade area, m²) |
| Hub | W_hub = 0.05 · (W / N_rotor) kg per rotor |
| Shaft | W_shaft = 0.15 · L_shaft kg, L_shaft = 0.15 R, per rotor |
| Arms (hexacopter) | W_support = 0.2 · R kg per rotor |
| Fuselage | W_fuselage = 28 · (W/1000)^(2/3) (W in kg) |
| Landing gear | W_gear = 0.067 · W |
| Motor | **W_motor = 0.076 · Q^0.86** (Q = rotor torque; unit not printed on this page — N·m assumed) |
| Solar cells | 2.0 kg/m² |
| Battery | 218.5 Wh/kg (pack, end of life) |
| Flight controls | W_control = 0.84 · W_blade |
| Avionics | 1.2 kg |
| Contingency | 20 % of empty weight; designs stopped closing above ~35 % (p. 42) |

## Flap dynamics [D] (p. 23)
- On Earth, aerodynamic flap damping is "on the order of 50% critical". The **Mars Helicopter blade: flap frequency
  ~2/rev, Lock number γ = 0.3, about 3 % critical damping** → strong resonant peaks at ν−1 and ν+1 /rev; JPL made the
  blades and hub very stiff and rolled the control gain off below the modes.
- Rotor frequencies scale with rpm; for fixed tip speed Ω = V_tip/R, so dimensional rotor frequencies drop as rotors
  grow, while the control bandwidth need is fixed.

## Venus read-out [K]
VESPER at 55 km: γ = ρ a c R⁴ / I_b ≈ 0.889 × 5.7 × 0.055 m × 1.3⁴ m⁴ / 0.0854 kg m² ≈ **9.3** (a = 5.7 /rad [Y];
c at 0.75R from doc 25 chord 78→47 mm; I_b = half of the sim_params rotor polar inertia 0.1708 kg m² [Y]).
That is Earth-helicopter-like (Earth rotors typically ~8–10 [Y, general knowledge, not read this session]):
Venus blades are well damped, unlike Mars. γ scales with ρ: 16 at 50 km, 4.7 at 60 km, 2.5 at 64 km.
