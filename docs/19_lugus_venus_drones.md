# 19 · LuGus Studios — "Drones on Venus": a simulation-ready concept

Prepared 2026-11-03. Tags as in doc 17: **[D]** read from the source in this session · **[D-ag]** read from the
source by the research agent (note: `research_notes/LuGus Venüs dronları/R_lugus_venus_research.md`, 969 lines) ·
**[A]** snippet only · **[K]** computed here (`aerokit.planetary`, `scripts/challenges_2026_numbers.py`,
`studies/challenges_2026/`) · **[Y]** judgement.

> **Özet (TR).** LuGus Studios, Hasselt'te bir **drone simülasyonu** stüdyosu (Liftoff: FPV Drone Racing; Unity
> tabanlı "Liftoff Core"). 2022'de Skypersonic ile **NASA Mars analog görevinde eğitim aracı olarak kullanılan
> bir Mars Drone Simulator** yaptılar ve "Liftoff: Offworld" ile güneş sisteminde drone uçurmayı duyurdular. Yani
> "Drones on Venus" büyük olasılıkla **simülasyona hazır bir kavramsal tasarım**: inandırıcı bir araç + onu
> simüle etmek için gereken fizik/ortam modeli + eğitim/oyun senaryoları. Kilit fiziksel gerçek: **50–55 km'de
> yoğunluk ~0,9–1,6 kg/m³, g = 8,7 m/s² → bir multikopter Dünya'daki kadar güçle havada kalır**; yüzeyde yoğunluk
> 65 kg/m³ (8,5× daha az güç) ama 462 °C ve 92 bar. Omurga konsept: **balon ana gemiden bırakılan, kısmen
> yüzer (helyumlu) kuadrotorlar** ("CLOUDHOPPER"), 50–62 km bandında, rüzgârla sürüklenerek çalışır. Simülatöre
> verilecek **Venüs ortam dosyası** hazır: `studies/challenges_2026/venus_environment.json` (0–100 km, 1 km adım,
> her alan kaynaklı).

## 1. The sponsor (verified)

- "**At LuGus Studios … we have created a Mars Drone Simulator, powered by Liftoff simulation technology**", a
  training tool for **NASA's Mars Analog Mission**, "tested by Italian Air Force officer and ESA astronaut Roberto
  Vittori"; **Liftoff: Offworld** "will allow you to explore the solar system with drones" — liftoff-game.com news
  of 23 Sep 2022 [D, read this session].
- LuGus Studios BV, Hasselt, founded 2011 (Kevin Haelterman, Tom Lissens), 11–13 people, "experts in high-fidelity
  drone simulation"; Liftoff (Steam, 2018; 95 % positive of 7 205 reviews), Liftoff: Micro Drones, Liftoff XR
  Drone (Quest), Liftoff Core / Academy for custom simulators (University of Zurich, Skypersonic); Belgian Game
  Awards 2025 *Best Tech Provider* for the "Liftoff Core Modular Engine", citing NASA analog work and "efficiency
  and sustainability"; serious games incl. CosmiClean (recycling, with KU Leuven) [D-ag].
- Team page shows game designers, programmers and technical artists — no aerospace engineers [D-ag]. No ESA,
  BELSPO or Belgian space-industry link found [D-ag].

**Consequence [Y].** The jury will value physics that *turns into simulation parameters*, gameplay/training value
grounded in real constraints, and a clean story — more than spacecraft jargon. Prepare a **vehicle** and a
**simulation & training layer**; if the brief says "game", "player", "simulator" or "training", lead with the
second (P3 below).

## 2. Environment numbers (what a simulator needs)

From `aerokit.planetary` [K] (table values from Wikipedia's VIRA table [D]; density from the ideal gas):

- **50 km**: 75 °C, 1.07 bar, 1.60 kg/m³ · **55 km**: 27 °C, 0.53 bar, **0.925 kg/m³** · **60 km**: −10 °C,
  0.24 bar, 0.47 kg/m³ · **surface**: 462 °C, 92 bar, **65 kg/m³** (53× Earth sea level). 1 bar is at 50.5 km;
  0 °C at 58.6 km; 125 °C (electronics limit) at 42.7 km; 300 °C at 20.7 km [K, `numbers.json` venus_scalars].
- Gravity 8.87 m/s² at the surface [D], 8.71 at 55 km [K].
- **Winds**: ~45 m/s at 45 km, 65 m/s at 53 km, ~100 m/s at 60 km, ~95 m/s at the cloud tops; 0.3–1 m/s at the
  surface [D-ag Landis 2001/2002, VAPS 2018]. Drifting at 60 km circles the planet in **4.4 days**; at 60 m/s at
  55 km in 7.4 days [K].
- **Light**: 2600 W/m² above the atmosphere [D]; 20–50 % at the cloud base, ~95 % at 65 km; upward (reflected) flux
  ~90 % of downward at 60 km → **bifacial** panels [D-ag Landis]; nearly 2 Earth days of darkness on the night
  side at the equator [D-ag]; solar day 116.75 Earth days [D].
- **Clouds**: sulfuric-acid droplets, deck ~48–70 km [D]; JPL tests aerobot materials in 94 % H₂SO₄ [D-ag].
- **Light time** Earth–Venus 2.3–14.3 min one way [K] → no live piloting from Earth; supervisory control + autonomy.
- **Navigation**: no GNSS, no magnetic field, no stars inside clouds; use IMU, barometric altitude (p(h) is well
  known), radio ranging/Doppler to mothership and orbiter, inter-drone ranging; Earth VLBI tracked Vega [D-ag].

Simulator file [K]: `studies/challenges_2026/venus_environment.json` — 0–100 km at 1 km: T, p, ρ, g, speed of
sound (γ = 1.286 from Young et al. 2026 via the agent — approximate), zonal wind (sourced anchors, **linear
interpolation between them is our assumption**), downward solar fraction (sourced 50–65 km only). The file lists
what is *not* modelled: turbulence (no source found), meridional wind, day/night and latitude variation.

## 3. Vehicle physics [K, `studies/challenges_2026/tables.md`]

- **Hover** (`venus_hover`, 5 kg on 0.5 m² of rotor, FM 0.7): Earth sea level 443 W; **Venus 55 km 427 W**; 65 km
  892 W; 40 km 197 W; surface **52 W** (8.5× less than Earth). A Liftoff-tuned quad "feels" almost Earth-normal at
  55 km — the simulator's flight model barely changes there; the environment does.
- **Battery quadrotor at 55 km** (`venus_multirotor`, 4 × 0.6 m rotors, FM 0.65, η 0.7, empty fraction 0.5): 2 kg
  payload hovers 20 min with a 7.7 kg vehicle at 150 Wh/kg (5.3 kg at 250 Wh/kg); one hour only works with 0.5 kg
  payload at 250 Wh/kg (1.7 kg vehicle); 2 kg for one hour has no solution. → Pure rotor-borne flight is for
  *sorties*, not for living in the clouds.
- **Buoyancy** (`venus_buoyancy`): net lift at 55 km — hydrogen 0.88, helium 0.84, Earth air 0.31, nitrogen
  0.33 kg/m³; 100 kg needs 119 m³ of helium (6.1 m sphere). **Breathable air floats on Venus.** Sanity anchor:
  Vega's 3.54 m helium sphere carried 21 kg at 54 km [D-ag]; our model gives 0.84 × 23.2 m³ ≈ 19.5 kg at 55 km [K].
- **Solar aeroplane** (`venus_aeroplane`, C_L 0.8, L/D 15, η 0.6): a 10 kg / 2 m² aircraft flies at 10.8 m/s and
  needs ~105 W at 55 km, ~219 W at 65 km; 2 m² of 20 % cells above the clouds collect ~1 kW before attenuation,
  sun angle and night. To *hold position* against 95–100 m/s winds it must fly that fast — Landis' solar-aeroplane
  argument [D-ag].

### 3a. Concept trade and simulator parameters — day command (added 3 Nov evening) [K]

`python scripts/venus_day.py <card>.json` sizes each concept on the card across altitude and writes
`vehicles_for_simulator.json` (mass, weight, buoyant force, rotor/wing area, power, ρ, g, wind at the operating
altitude — the numbers a Liftoff/Unity flight model needs) plus figures `V1_power_altitude`, `V2_environment`,
`V3_station_keeping`. New functions: `P.assisted_hover_power` (gas lift subtracted before momentum theory),
`P.envelope_drag_power` (½ρV³C_D πr², C_D 0.3 assumed), `P.solar_power` (day-average factor 1/π, bifacial
`upward_ratio`), `P.venus_zonal_wind`, `P.venus_solar_fraction` (sourced anchors; interpolation is ours).

Rehearsal card, 10 kg at 55 km (all vehicle numbers assumptions): battery quadrotor **1236 W**; helium-assisted quad
with 9 m³ of He (76 % of the weight on gas) **149 W** — and 0 W below ~52 km, where the cell alone floats it; solar
aeroplane **105 W** at 10.8 m/s. A 1 m² 20 % bifacial panel gives **173 W averaged over a solar day** (543 W with the
Sun overhead) — so the He-assisted quad and the aeroplane can live on ~1 m² of cells, the battery quad would need ~7
m². Holding position against the 72 m/s wind with a 12 m³ envelope would take **~335 kW**: three orders of magnitude
more than staying aloft → the design lives in the air-mass frame. This replaces the agent's "~60 W at 85 % buoyancy"
estimate in §5 with a tested computation.

### 3b. Time-stepped mission simulator (added 4 Nov, 00:30) [K]

`aerokit.venus_flight` (tests `tests/test_venus_flight.py`): a superpressure (fixed-volume) helium cell + reversible
rotors + battery + solar + hull temperature, flown through a mission list (`goto` / `hold`) in the air-mass frame.
Physics that a game engine usually lacks and a Venus vehicle needs: the cell's lift falls with altitude, so the
vehicle has a **float altitude** (52.4 km for 10 kg on 9 m³ of helium) and pays rotor power anywhere else; added
mass ½ρV (the envelope drags ~4 kg of CO₂ along at 55 km); drag on the *air-relative* velocity, so with no thrust it
relaxes to the wind (tested); thrust capped by the power limit through inverted momentum theory.

`venus_day.py` flies the card's mission and writes `mission_replay.json` (1 Hz frames: position, altitude, speeds,
wind, thrust, power, solar, battery, ambient and hull temperature — load it into Unity/Liftoff Core to replay) and
figure `V4_mission`. Rehearsal (all vehicle numbers assumptions): hold 55 km, dive to 48 km at 3 m/s, sample 30 min,
climb back, hold 1 h → 3.3 h, **769 km drift** east, battery low point 135 of 500 Wh, peak draw 485 W; **the hull
reaches 89 °C and stays above the 70 °C electronics limit for 66 min**. A dip to 52 km for 10 min stays inside the
limit (test). Design line for the jury: sample the lower cloud deck in short dips or carry thermal mass/insulation —
the simulator turns that trade into minutes and watt-hours.

## 4. Predicted formulations, ranked [Y] (detail in the research note §6)

1. **P1 · Design a drone (system) to explore Venus + what is needed to simulate it.** Backbone concept below.
2. **P2 · Near-surface / surface drone.** Be honest about 735 K / 92 bar: "descent sprinters" — unpowered
   autorotating samara drones dropped from the balloon, a short powered hop below 10 km from an insulated,
   phase-change-cooled core (≤ 1–2 h; Venera landers lasted ~127 min [D-ag]), then a SiC weather station (SiC ICs
   ran 60 days at 460 °C but are simple [D-ag]).
3. **P3 · Game / simulation / training scenario.** "Liftoff: Offworld — Venus Cloud Expedition": altitude biome
   ladder (70 km thin & bright → 55 km Earth-like flight in a 70 m/s air mass → 48 km hot, dark, turbulent →
   surface "hell dive" in 65 kg/m³ air with a heat timer); mechanics: air-mass reference frame, light-delay
   waypoint mode (2–14 min), buoyancy tuning (He/air/H₂), bifacial solar budget, acid damage meter, thermal timer;
   one environment data file drives all of it.
4. **P4 · Swarm** for simultaneous multi-point measurement (wind shear, waves, cloud microphysics), inter-drone
   ranging, bistatic radar option [D-ag Landis 2002].
5. **P5 · Deployment architecture** — entry → parachute → balloon inflation in ~10 min [D-ag JPL] → daughter drones
   released from the gondola over a 100-day mission.
6. P6 cloud sample return / life search (phosphine is contested: ~1–20 ppb [D-ag]) — as a "phase 3" vision slide.
7. P7 XR operator console with a delay-aware predicted-state "ghost".

## 5. Backbone concept: CLOUDHOPPER (P1, absorbs P4/P5 and a P2 daughter) [Y with K numbers]

- **Mothership**: variable-altitude helium aerobot (JPL class, 12–15 m, 100–200 kg [D-ag]) drifting at 52–60 km
  with the super-rotation; star tracker/Sun sensor above the clouds on excursions; UHF to the drones, relay to an
  orbiter.
- **Daughters (4–8)**: 8–10 kg buoyancy-assisted quadrotors; a ~1 m³ class helium cell carries most of the weight
  (0.84 kg/m³ at 55 km), rotors only trim and hop ±2 km; ducted, fluoropolymer-coated props; sealed motors;
  sapphire windows [Y]. Hover-only power at 55 km would be ~1 kW for 10 kg; buoyancy cuts it by more than an order
  of magnitude (the agent computes ~60 W at 85 % buoyancy [D-ag calc]).
- **Power**: bifacial thin film on envelope top and bottom; Li-ion only in the 0–60 °C band; float passively
  through the ~2-day night.
- **Thermal**: live at 52–60 km (≤ 75 °C); dives to 45–48 km for minutes on thermal mass, climb back to cool.
- **Autonomy and ops**: behaviour-tree autonomy on board; humans plan days ahead (Ingenuity style); the simulator
  trains this supervisory loop with the real light delay.
- **Science**: cloud-particle sampling (mode-3 particles), wind-shear and turbulence mapping, lightning/infrasound.
- **What LuGus would build**: the Venus biome for Offworld, an operator trainer, an outreach module — all from
  `venus_environment.json`.

## 6. Sustainability lines [Y unless tagged]

Venus as the laboratory of a **runaway greenhouse** (climate science for Earth) [D-ag Landis 2002]; **simulation
first** cuts hardware test campaigns — LuGus' own award citation names efficiency and sustainability [D-ag];
no radioisotope power; reusable mothership; tiny mass per unit science (swarm); Earth spin-offs: high-temperature
SiC electronics (geothermal, engines, EV power electronics), acid-resistant materials, GNSS-free swarm navigation
for medical drones (LuGus' BeNeDrone project [D-ag]).

## 7. Five-hour plan and jury questions [Y]

- 0:00–0:20 Classify the brief (P1…P7); one-sentence claim. 0:20–1:00 altitude band + architecture; fill §2–3
  numbers. 1:00–2:30 sizing (buoyancy, rotor, power, thermal), CONOPS timeline, comms/navigation, materials —
  rerun `aerokit.planetary` with our own mass/area. 2:30–3:15 simulation & training layer, sustainability.
  3:15–4:30 deck (10–12 slides). 4:30–5:00 rehearse + Q&A.
- One-line answers to rehearse: 100 m/s wind → we live in the air-mass frame; why not just a balloon → vertical
  control is where most science gain is [D-ag VAPS]; navigation → baro + IMU + radio ranging; acid → PTFE/FEP
  (Vega flew it) [D-ag]; night → passive float; surface power → thermal battery, sprints; electronics at 460 °C →
  SiC, keep computing above the clouds; feasibility → JPL aerobot prototypes, EnVision/DAVINCI context (**check
  mission dates before quoting — several are snippet-only** [D-ag §9]).

## 8. Open items

VIRA primary tables (Seiff 1985) not read by anyone; CO₂ viscosity and Reynolds numbers are the agent's
assumptions; surface sunlight (~2.5 %) snippet-only; no turbulence data; mission dates (DAVINCI, VERITAS, EnVision)
partly snippet-only; no detail on how LuGus modelled Mars physics [D-ag §9].
