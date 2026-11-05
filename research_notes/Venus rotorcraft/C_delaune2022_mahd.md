# C_delaune2022_mahd — Mid-Air Helicopter Delivery at Mars Using a Jetpack (MAHD)

## Citation
Delaune, J.; Izraelevitz, J.; Sirlin, S.; Sternberg, D.; Giersch, L.; Tosi, L. P.; Skliyanskiy, E.; Young, L.; Mischna, M.; Withrow-Maser, S.; Mueller, J.; Bowman, J.; Wallace, M. S.; Grip, H. F.; Matthies, L.; Johnson, W.; Keennon, M.; Pipenberg, B.; Patel, H.; Lim, C.; Schutte, A.; Veismann, M.; Cummings, H.; Conley, S.; Bapst, J.; Tzanetos, T.; Brockers, R.; Jain, A.; Bayard, D.; Chmielewski, A.; Toupet, O.; Burdick, J.; Gharib, M.; Balaram, J. (2022). *Mid-Air Helicopter Delivery at Mars Using a Jetpack.* 2022 IEEE Aerospace Conference, pp. 1-20. DOI: 10.1109/AERO53065.2022.9843825. arXiv: 2203.03704.
PDF: https://arxiv.org/pdf/2203.03704
Note: the task brief called this "SHADE". The paper's own name for the concept is **MAHD**. I did not find a paper titled SHADE.

## What was read
Full arXiv text, 20 pages (pypdf): abstract, Sections 2-4 (MSH summary, system architecture, mass table, concept of operations), Section 5 flow-interaction summary, Section 7 Monte Carlo, Section 8 take-off. The EDL timeline figure (Fig. 5) was read only through its extracted text labels.

Tag: [D-ag] read in this paper. [derived] my arithmetic.

## Numbers [D-ag]
**MSH vehicle (Sec. 2):** hexacopter, six rotors of **1.28 m** diameter with four blades each. Vehicle 2.38 m stowed, 3.97 m deployed. Mass **31.2 kg**. Carries 5 kg science payload up to **13.3 km** or **6.5 min** hover (abstract: "up to 13 km"). For comparison, the Ingenuity design value was 0.18 km or 1.5 min, against 625 m (flight 9) and 2.8 min (flight 12) actually flown. MAHD gives **+150 % science payload**, +27 % range and +30 % hover time versus an airbag-lander-optimized MSH (Table 2, text p. 3).

**Architecture (Sec. 3):**
- 2.65 m, 70° sphere-cone heritage aeroshell (Pathfinder/MER/Phoenix/InSight). 11.8 m DGB parachute (InSight).
- Jetpack: 4 thrusters (MR-107N-like, hydrazine, max **269 N** steady thrust, min ON 20 ms, Isp 220 s, cant 15°), 10 tanks of 1.3 L each. 95 cm diameter, with a 35 cm porthole for the nav sensor. Wet mass 49.52 kg incl. margins (Table 3 allocates 46.9 kg).
- **Mass allocation (Table 3):** MSH 37.4 kg (31.2 + 20 %), jetpack 46.9 kg, aeroshell 190.7 kg, **total entry 275 kg**. The lightest previous Mars entry was Phoenix at 573 kg.
- GNC runs on the helicopter computer and sensors. The jetpack is controlled through an umbilical.

**Sequence (Sec. 4, Fig. 5):**
1. Entry at 125 km, 8.3 km/s, FPA −14°. Ballistic entry. Parachute deployed at M = 1.55, q = 232 Pa (≈ 400 m/s).
2. Heatshield jettison at **12.2 km AGL**.
3. Helicopter range-visual-inertial navigation on at **2.4 km AGL**.
4. Jetpack + helicopter separate from backshell at **600 m AGL** → **3 s free fall** → thrusters fire, divert away from the backshell, decelerate (powered deceleration starts ~400 m AGL; simulated case went from 43 m/s at 374 m AGL to 0 m/s at 200 m AGL).
5. Terrain-relative hover at **200 m AGL**. Jetpack holds a hover platform for **12 s** so the helicopter can spin up. Divert distance 42 m. Divert and arrest take ~20 s.
6. Jetpack thrust cut-off and helicopter separation at E+431 s. Jetpack free-falls away.
- Mass at powered descent: 84.0 kg. Reference site Eridania basin (37°S, 184°E), Ls 335°, 1000-1100 LMST.

**Winds and flow (Sec. 4-5):** horizontal winds at 200 m AGL up to **~30 m/s (3σ)** in Eridania (34.1 m/s 3σ cited later). 3σ wind difference 600 m vs 200 m = 15.1 m/s; 3σ change at 200 m over 5 s = 2.1 m/s. CFD of jet-rotor-wind interaction: downwash w < 10 m/s (compatible with take-off), but lateral velocity is amplified at the rotor positions.

**Monte Carlo (Sec. 7):** initial altitude 650 ± 1 m; vertical velocity −41.72 ± 3.16 m/s; lateral 7.67 ± 7.65 m/s, capped at 24.3 m/s. 500 runs. Residual jetpack rates < 0.2 deg/s (3σ) before take-off. Control: no gain limit, 54° phase margin, 3.7 Hz (loop crossover). Force-torque sensing resolution 2 N vertical, 0.3 N lateral, 0.2 N m; wind sensing < 1 m/s.

## Relevance to Venus (my inference)
- This is the closest published precedent for a **mid-air rotorcraft release from an entry backshell**. Key numbers: separation at 600 m AGL, 3 s free fall, ~200 m of powered arrest, and ~12 s spin-up on a stable platform.
- In dense Venus air (ρ ≈ 1 kg/m³ at 55 km) a rotorcraft can likely spin up and take over directly under a parachute or from free fall without a jetpack, since rotor thrust per unit area is ~60× Mars. This is unverified. See C_venus_rotorcraft for whether any published Venus concept does this.

## Caveats
- This is a concept study with preliminary simulations. No hardware was demonstrated.
- Some figure-text values (E+ times, entry state) come from extracted figure labels.
