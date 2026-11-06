# D_tauber_venus_rad_2012 — Stagnation-point RADIATIVE heating fit for Venus entry

## Citation
Tauber, M. E., Palmer, G. E., & Prabhu, D. K. (2012). *Stagnation Point Radiative Heating
Relations for Venus Entry.* NASA Ames, report ARC-E-DAA-TN2887, NTRS 20120001655.
NTRS labels it "Preprint (Draft being sent to journal)"; the journal version was not checked.
URL: https://ntrs.nasa.gov/citations/20120001655
PDF: https://ntrs.nasa.gov/api/citations/20120001655/downloads/20120001655.pdf

## What I read
Full 6-page preprint (text extract + rendered image of p.3 for the equations).
Local copy: `D:\tmp_ideathon\venus\downloads\eng\tauber_venus_rad.pdf`.

## Numbers
- Atmosphere used: 96.5 % CO2 / 3.5 % N2 (Pioneer Venus measured) [D-ag, p.1–2]. The
  Pioneer Venus heat shields had been sized for 90 % CO2 / 10 % N2 [D-ag, p.1].
- **Eq. (2a), 10,028 ≤ V ≤ 12,000 m/s:**
  **q_rad = 8.497e-63 · V^18 · ρ^1.2 · r_N^0.49  [W/m²]** (SI: V m/s, ρ kg/m³, r_N m) [D-ag, p.3]
- **Eq. (2b), V < 10,028 m/s:**
  **q_rad = 2.195e-22 · V^7.9 · ρ^1.2 · r_N^0.49  [W/m²]** [D-ag, p.3]
- Non-adiabatic correction applied to the CFD/NEQAIR points (Eq. 1):
  q_rad/q_rad,adiab = 1/(1 + 3Γ^0.7), Γ = 2 q_rad,adiab / (0.5 ρ V³) [D-ag, p.2]
- The fit's source data: Pioneer Venus large probe, r_N = 0.363 m, β = 190 kg/m², entry
  11.584 km/s at −31.829° at 137.78 km [D-ag, p.3].
- Table 1 (p.4–5), computed vs Eq. 2 [D-ag]:

| t s | V m/s | ρ kg/m³ | alt km | q_rad CFD W/cm² | Eq.2 W/cm² |
|---|---|---|---|---|---|
| 7.0 | 11551 | 2.86e-4 | 95.22 | 519 | 388 |
| 8.0 | 11310 | 1.39e-3 | 89.24 | 1672 | 1770 |
| **8.6 (peak)** | 10880 | 3.26e-3 | 85.77 | **2449** | 2450 |
| 9.2 | 10028 | 6.92e-3 | 82.49 | 1396 | 1393 |
| 10.4 | 7015 | 2.13e-2 | 77.12 | 374 | 318 |

- Average absolute accuracy of the fit 8 %, skewed by −25 % at the first point (t = 7 s,
  nonequilibrium) [D-ag, p.3–4].
- Stagnation pressure during 92.22 → 77.12 km: 0.81 → 10.0 atm [D-ag, p.4]. Stated
  validity of the older Ref. 5 fits: 1–10 atm, r_N 0.20–0.75 m [D-ag, p.2].
- Present computations give a 15 % lower radiative heat load than the old (Page &
  Woodward 1972) rates [D-ag, p.4].

## My checks (calc, not in source)
Re-evaluated Eq. 2 with Table 1 inputs: 388, 2448, 1392, 1251, 319 W/cm² — matches the
paper's Eq.2 column, so the exponents above are read correctly.
For comparison, Sutton–Graves convective (k = 1.897e-4, cold wall, non-ablating) at the
8.6 s point gives ~2315 W/cm², i.e. radiative and convective are the same order at
Venus peak heating for a 0.36 m nose (my calc).

## Caveats
- Strong V^18 dependence: only use within 10–12 km/s; below 10,028 m/s switch to 2b.
- Fit anchored to a single trajectory/nose radius (0.363 m); extrapolation to large
  nose radii (rotorcraft aeroshell 2–4 m) is outside the fitted range.
- Fully catalytic cold wall; ablation absorption not included (Cabrera & West found
  ~11 % reduction from coupled ablation — see D_cabrera_west_pv.md).
- Preprint; peer-reviewed version may differ.
- Tauber & Sutton 1991 (JSR 28(1):40–42) is Earth and Mars only; see D_tauber_sutton_1991.md.
