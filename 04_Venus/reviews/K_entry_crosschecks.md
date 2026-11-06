# K_entry_crosschecks — entry model checks run by the Venus session (4 Nov 2026)

Tag: **[K]** — computed by this session with `aerokit.venus.entry.fly_entry` (3-DOF planar, RK4); the reference
numbers are **[D-ag]** from the agent notes named. Commands are reproduced as Python one-liners in the session log;
the first two are also unit tests (`tests/test_venus_entry.py`).

| Check | Reference | Ours | Verdict |
|---|---|---|---|
| Allen–Eggers peak g, exponential atm H 7 km, 11 km/s, −30° / −45° | 162 / 229 g (closed form) | 159 / 231 g | within 3 % (steep, straight-line regime) |
| Allen–Eggers at −10° | 56 g | 31 g | expected disagreement: shallow trajectories curve (closed form invalid) |
| Pioneer Venus large probe, β 190, 11.584 km/s, −31.829° at 137.78 km (D_tauber_venus_rad_2012 Table 1) | V 11 310 / 10 880 / 10 028 / 7 015 m/s at 8.0 / 8.6 / 9.2 / 10.4 s; h 89.24 / 85.77 / 82.49 / 77.12 km | V within 1 %, h within 0.2 km | pass |
| same, peak radiative flux (Tauber 2012 fit at its own trajectory) | 2449 W/cm² | 2409 W/cm² | within 2 % |
| same, peak deceleration | 276 g (Venkatapathy 2016), 280 g (SP-461) | 288 g | within 4 % |
| ADEPT-like, β 44, −8.5°, 10.8 km/s, EI 200 km (B_venkatapathy2016_prabhu2013) | 32 g | 35 g | within 10 % |
| rigid 3.5 m 45°, β 208, −8.5° (same source) | 48 g | 29 g | **1.7× lower — unresolved** |

Diagnosis of the last row:
- Upper atmosphere: replacing our density (probe mean / VIRA-like table, isothermal above 100 km) with the
  Venus-GRAM average profile from the AMAT repository (`venus-gram-avg.dat`, downloaded by the atmosphere agent; GRAM
  density 1.19e-2 / 1.15e-3 / 7.97e-5 / 2.48e-7 kg/m³ at 80 / 90 / 100 / 120 km vs ours 1.26e-2 / 1.15e-3 /
  8.63e-5 / 3.30e-7) changes peak g by < 3 % (29.5 vs 28.8 g; 36.2 vs 35.4 g).
- Entry speed: 11.3 and 11.6 km/s lower the peak (24 and 20 g) — the wrong direction.
- Interface altitude: at shallow angles the result is very sensitive to where γ is defined (−8.5° at 175 km → 45 g,
  at 150 km → 57 g, because the hyperbolic trajectory *flattens* by ~3° between 200 and 100 km). The published case
  probably uses another reference altitude or a lifting trajectory; their slide text says the trajectory studies use a
  200 km interface (agent note, line 43), so this is not settled.

Consequence for VESPER: peak g at −9.5° (56 g) carries a factor ~1.7 model uncertainty → qualification to 100 g
(risk R9).

## Historical-entry validation (added 4 Nov ~22:10, `python 04_Venus/code/analysis/venus_entry_validation.py`)

Inputs and reference values: Dutta et al. 2012 Table 1 (note D_dutta_2012_venus_entry, [D-ag]; their n_max/q_max are engineering re-simulations), flight-reported g from SP-461 / Siddiqi 2018 notes. Result: peak g 3.5 % rms, max 7.5 % over 12 cases; heat flux within 10 % for Venera/Vega spheres, 20–34 % low for the PV 45° cones; Mach 0.8 altitude 64.0–66.1 km vs published chute/heat-shield events 64–67 km; DAVINCI (145 km interface, β swept 50–200): 29–34 g vs 32 g. Full table: 04_Venus/outputs/entry_validation.md.
