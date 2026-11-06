# E_14 — Johnson 2005: model for vortex ring state (VRS) influence on rotorcraft flight dynamics

- **Citation:** Johnson, W. (2005), "Model for Vortex Ring State Influence on Rotorcraft Flight Dynamics",
  NASA/TP-2005-213477, NASA Ames (NTRS 20060024029).
- **URL:** `https://rotorcraft.arc.nasa.gov/Publications/files/Johnson%20TP-2005-213477.pdf`, accessed 2026-11-05;
  local `D:\tmp_ideathon\venus_research\pdf\johnson2005_vrs.pdf`. Read level: VRS boundaries and model sections,
  Tables 3–4 (pdftotext) **[D]**.

## Values [D]
- VRS scales primarily with **v_h = sqrt(T/(2ρA))**; solidity, twist and configuration are secondary (p. 14).
- The vertical motion is unstable where d(Vz+v)/dVz < 0, "roughly Vz/vh = −0.5 to −1.5" (p. 2, Fig. 3).
- Wolkovitch-type criterion: VRS when sqrt(k²Vx² + (Vz+v)²)/v_h < 0.74, k = 0.65 (0.60–0.74 fits) (p. 12).
- Helicopter flight test (Dauphin D6075, Taghizad et al.): below 20 km/h forward speed the upper boundary is at a low,
  nearly constant descent rate, Vz ≈ −4 m/s (p. 13).
- **Table 4 model parameters (velocities / v_h):** baseline A: VzA = −1.5; B: VzB = −2.1; C: VxC = 0.75.
  VRS model D: VzD = −0.2; N: **VzN = −0.45**, (V+v)N = 0.85; X: **VzX = −1.5**, (V+v)X = 1.25; E: VzE = −2.0;
  M: **VxM = 0.95** (VRS effect vanishes for Vx/v_h ≥ 0.95).
- Simpler baseline (ref. 52 form): Vz + v = Vz (a Vz² − b + c Vx²) inside 1.5Vx² + (2Vz+3)² < 1, with a = 0.373,
  b = 0.991, c = 0.598 (p. 14).
- Transient: first-order lag on the inflow increment, dΔv/dt·τ + Δv = v_QS − v_TRIM; τ given in rotor revolutions (p. 15).
- Measured VRS fluctuation frequencies scale with v_h/R (Table 2: ωR/v_h ~0.1–5 depending on test).
- Algorithm (Table 3): if Vz ≥ 0 or Vx ≥ VxC use momentum theory; otherwise cubic-polynomial bridges between the
  momentum-theory branches, then a VRS increment with zero slope at the stability boundary.

## VESPER numbers [K]
v_h = 2.59 m/s at 55 km (sim_params) → unstable descent band **1.17–3.89 m/s**; leave it with forward airspeed
≥ 0.95 v_h = **2.5 m/s**. Doc 25's "descent to cruise at 3 m/s" (61 → 55 km) is inside this band if flown vertically.
