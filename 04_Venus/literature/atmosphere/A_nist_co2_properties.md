# A_nist_co2_properties — CO2 thermophysical properties for rotor aerodynamics (NIST WebBook)

## Citation

Lemmon, E. W., Bell, I. H., Huber, M. L., McLinden, M. O., "Thermophysical Properties of Fluid Systems",
in *NIST Chemistry WebBook, NIST Standard Reference Database 69*, Linstrom & Mallard eds., NIST
(accessed 2026-11-04). Fluid = carbon dioxide (ID C124389), isobaric tables.
(The WebBook "recommended citation" authors are from memory — not re-read this session.)

Underlying correlations, as listed on the WebBook page itself [D-ag]:
- Equation of state: Span, R., Wagner, W. (1996), *J. Phys. Chem. Ref. Data* 25(6):1509–1596,
  doi:10.1063/1.555991. Page states uncertainty in the vapour: 0.03–0.05 % density, 0.03 % speed of sound,
  0.15 % heat capacity (for p ≤ 30 MPa, T ≤ 523 K).
- Viscosity: Laesecke, A., Muzny, C. D. (2017), "Reference Correlation for the Viscosity of Carbon Dioxide",
  *J. Phys. Chem. Ref. Data* 46(1):013107, doi:10.1063/1.4977429. (NIST now uses this, not Fenghour,
  Wakeham & Vesovic 1998 which the brief mentioned; I did not read either paper's uncertainty statement.)
- Thermal conductivity: Huber, M. L., Sykioti, E. A., Assael, M. J., Perkins, R. A. (2016),
  *J. Phys. Chem. Ref. Data* 45(1):013102, doi:10.1063/1.4940892; page states ~1 % uncertainty below 0.1 MPa
  at 300–700 K.

## What I read

The tab-delimited data output (Action=Data) of the WebBook fluid program for CO2, isobars 0.02, 0.05, 0.1,
0.2 MPa, T = 230–400 K in 5 K steps. Saved to `D:\tmp_ideathon\venus\downloads\nist\co2_isobar_*MPa.txt`.
URL pattern:
`https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C124389&Type=IsoBar&Digits=5&P=0.05&THigh=400&TLow=230&TInc=5&RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm`

## Values [D-ag] (γ = cp/cv and ν = μ/ρ computed by me from the tabulated columns)

### p = 0.05 MPa (0.5 bar)

| T (K) | ρ (kg/m³) | cp (J/kg/K) | cv (J/kg/K) | γ | a (m/s) | μ (µPa·s) | k (W/m/K) | ν (m²/s) |
|---|---|---|---|---|---|---|---|---|
| 250 | 1.0634 | 798.2 | 605.4 | 1.319 | 248.44 | 12.581 | 0.01302 | 1.18e-5 |
| 275 | 0.96552 | 823.8 | 632.1 | 1.303 | 259.37 | 13.796 | 0.01485 | 1.43e-5 |
| 300 | 0.88434 | 849.2 | 658.1 | 1.290 | 269.77 | 14.998 | 0.01675 | 1.70e-5 |
| 325 | 0.81585 | 873.7 | 683.1 | 1.279 | 279.71 | 16.185 | 0.01869 | 1.98e-5 |
| 350 | 0.75726 | 897.1 | 706.8 | 1.269 | 289.27 | 17.353 | 0.02067 | 2.29e-5 |

### p = 0.1 MPa (1.0 bar)

| T (K) | ρ (kg/m³) | cp (J/kg/K) | cv (J/kg/K) | γ | a (m/s) | μ (µPa·s) | k (W/m/K) | ν (m²/s) |
|---|---|---|---|---|---|---|---|---|
| 250 | 2.1363 | 805.0 | 608.2 | 1.324 | 247.79 | 12.581 | 0.01305 | 5.89e-6 |
| 275 | 1.9374 | 828.5 | 633.9 | 1.307 | 258.89 | 13.799 | 0.01488 | 7.12e-6 |
| 300 | 1.7730 | 852.5 | 659.3 | 1.293 | 269.39 | 15.003 | 0.01677 | 8.46e-6 |
| 325 | 1.6348 | 876.2 | 683.9 | 1.281 | 279.42 | 16.191 | 0.01871 | 9.90e-6 |
| 350 | 1.5167 | 899.0 | 707.4 | 1.271 | 289.04 | 17.359 | 0.02069 | 1.15e-5 |

## Observations

- Viscosity is pressure-independent to <0.1 % in this range [D-ag]; μ ≈ 15.0 µPa·s at 300 K (air at 300 K is
  ~18.5 µPa·s — general knowledge, not checked here).
- Speed of sound at 300 K ≈ 270 m/s [D-ag] vs ~347 m/s for air at 300 K (general knowledge, not checked):
  rotor tip Mach limit bites ~22 % earlier in tip speed.
- γ ≈ 1.29 at 300 K [D-ag] (not 1.4).
- Sanity check against Pioneer Venus data: 4-probe mean at 55 km is T 299.1 K, p 0.508 bar, ρ 0.889 kg/m³
  (see `A_pv_probes_seiff1980_pds.md`); pure CO2 at 300 K, 0.5 bar gives 0.884 kg/m³ [D-ag]. Consistent; Venus
  gas has MW 43.44 (3.5 % N2) vs 44.01 for CO2, so real Venus ρ is ~1.3 % lower than pure CO2 at same T,p
  (my arithmetic).
- Adiabatic lapse rate g/cp with these cp values ≈ 10.3 K/km at 55 km (my calc; see stability section of
  `A_pv_probes_seiff1980_pds.md`).

## Caveats

- Pure CO2. Venus mixture is ~96.5 % CO2, 3.5 % N2 (by volume; not re-verified here). N2 would slightly raise
  cp and speed of sound, and slightly change μ (estimated <1–2 %, my estimate, unverified).
- Values for an ideal-gas-like regime; real-gas corrections at ≤1 bar are tiny (compressibility ζ≈0.998 in
  the PV data).
