# E_05 — NIST Chemistry WebBook fluid properties, CO2 and N2 isobars, 5 Nov 2026

- **Source:** NIST Chemistry WebBook, SRD 69, "Thermophysical Properties of Fluid Systems":
  `https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C124389&Type=IsoBar&...` (CO2) and `ID=C7727379` (N2);
  P = 0.03, 0.1, 0.3, 1.0, 3.5 bar; T = 220–430 K in 5 K steps; units K, bar, kg/m³, m/s, µPa·s.
- **Accessed:** 2026-11-05 (curl, tab-separated data). Local `D:\tmp_ideathon\venus_research\nist\`. **[D]**
  (the equation-of-state and transport-correlation names were not re-read this session).
- Sample row [D]: CO2 at 1 bar, 220 K: ρ 2.43941 kg/m³, Cv 0.579075 J/(g K), Cp 0.780665 J/(g K), sound speed 233.446 m/s,
  viscosity 11.1066 µPa·s, conductivity 0.0109638 W/(m K).

## How the csv uses them [K]
- Bilinear interpolation in T and log p.
- Mixture 96.5 % CO2 + 3.5 % N2 by mole [Y, from the brief; PV gas chromatograph measured CO2 96.4 %, N2 3.41 % at
  21.6 km, earlier note A_pv_lgc_composition]: M = 43.45 g/mol (PV tables use 43.44).
- Speed of sound: a_mix = (a_NIST,CO2 / a_ideal,CO2) · sqrt(γ_mix R T / M_mix); γ_mix from mole-weighted Cp and Cv.
- Viscosity and conductivity: Wilke mixing rule.
- Result at 55 km (299.1 K, 0.508 bar): a 271.4 m/s, µ 15.03 µPa·s, ν 1.69×10⁻⁵ m²/s, γ 1.294, cp 853 J/(kg K),
  k 0.0169 W/(m K). Pure CO2 values in `sim_params.json`: µ 14.96 µPa·s, a 271.8 m/s — differences < 0.5 %.
