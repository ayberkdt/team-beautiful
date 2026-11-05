# C_pensado2025_dragonfly_edl — Dragonfly Entry and Descent Modeling and Simulation Overview (mid-air rotorcraft release under parachute)

## Citation
Pensado, Alejandro R.; Winski, Richard; Williams, James; Robb, Caleb (Analytical Mechanics Associates / NASA Langley EDL team) (2025). *Dragonfly Mission Entry and Descent Modeling and Simulation Overview.* AIAA SciTech 2025 Forum. NTRS 20240014477.
PDF: https://ntrs.nasa.gov/api/citations/20240014477/downloads/SciTech2025_DragonflyEntry_Descent_Overview.pdf
(The AIAA paper number and DOI were not checked.)

## What was read
pypdf text, 19 pages: Sec. I-II (concept of operations), the modelling list, the parachute section, the trigger logic, and Sec. IV results with Tables 1-2. Figures were not viewed.

Tag: [D-ag] read in this paper. [A] = from search snippets only.

## Numbers [D-ag]
- Aeroshell **4.5 m**, 60° sphere-cone (Genesis-derived). Entry mass **CBE 2309 kg / MPV 2600 kg** (post-PDR 2023).
- Cruise spin 1.5 → 2 rpm before entry. Entry interface 1270 km. ~10 g peak deceleration (requirement < 12 g). Peak heat flux 280 W/cm² (requirement < 310).
- **8.25 m DGB drogue** at ~Mach 1.5, with a smart trigger keeping total AoA ≤ 15°. **~108 min under drogue**. Then a **16.7 m ringslot main** is deployed by pressure trigger (requirement: main deploy altitude 4000-6000 m).
- **Heatshield released 120 s after main deploy.** This starts **Preparation for Powered Flight (PPF)**: the lander is **lowered into a "posed" configuration** so that its rotors are in the airflow and can be spun up without contact risk. The **lander rotors are used to null the entry-vehicle spin** (despin deadbands ±2 / ±3 deg/s; requirement ±4.9 deg/s; pose-event spin metric 31 deg/s) to allow optical navigation.
- **Lander release trigger enabled at nominal 1000 m altitude, down velocity 2.9 m/s.** Release window ~1000 → 800 m, with attitude-rate limits and ≥ 2 s since the last despin event. Requirements: altitude at release > 800 m (1 %-tile), down velocity < 2.9 m/s (99 %-tile). Total descent < 150 min.
- Then **transition to powered flight (TPF)**: the lander needs enough altitude to manoeuvre away from the backshell and main parachute, enter free flight and search for its first landing site.
- Monte Carlo: 10,000 samples. All four scenarios meet the release-altitude requirement 100 % and the down-velocity requirement 99.7-100 % (Table 2).

## Not confirmed [A]
- "Released ~1.2 km" (task brief): this paper gives **~1000-800 m**. A 2026 SciTech paper (NTRS 20250011718, not read) reportedly gives ~900 m.
- Lander mass "~875 kg": not stated in this paper (entry mass 2309-2600 kg incl. aeroshell). Unverified.

## Relevance to Venus (my inference)
- This is the **most mature published sequence for releasing a rotorcraft from a backshell under a parachute in a dense atmosphere**: pose rotors in the airflow → spin up while still attached → use rotor thrust/torque for despin → release at low descent rate (2.9 m/s) → fly away from parachute and backshell. It maps directly onto a Venus cloud-layer deployment at ~55-60 km, where ρ ≈ 0.5-1 kg/m³. That density is lower than Titan's 5.4 kg/m³, so the required release altitude margin and descent rate would need re-sizing.
