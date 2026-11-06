# E_18 — LuGus Studios / Skypersonic Mars Drone Simulator: what is public (5 Nov 2026)

All pages read on 2026-11-05 via WebFetch (text summaries). Tags: **[D]** for the LuGus/Liftoff pages (first party);
**[D-ag]** for trade-press articles (secondary); **[A]** for search snippets.

## 1. LuGus portfolio page [D]
`https://www.lugus-studios.be/portfolio/mars-drone-simulator`
- Client: Skypersonic. Project date shown: 01/09/2022. LuGus Studios, Hasselt (Belgium).
- "Powered by Liftoff" simulation technology; a training tool for NASA's Mars Analog Mission.
- Tested by Italian Air Force officer and ESA astronaut Roberto Vittori.
- A testing ground for **Liftoff: Offworld** (consumer planetary drone simulator, Early Access planned).
- The page lists **no** physics details (gravity, atmosphere, wind, comms delay), engine, or hardware; it has screenshots
  and a video.

## 2. Liftoff news pages [D]
- `https://www.liftoff-game.com/node/221` (23 Sep 2022, "Simulating NASA missions"): same facts; the Mars project will
  help make Offworld "the ultimate planetary drone exploration simulator".
- `https://www.liftoff-game.com/node/215` (22 Aug 2022): Liftoff: Offworld is "all about exploration and physics
  experimentations", "a physics sandbox layer on top of the Liftoff simulation", inspired by Ingenuity; Early Access on
  PC, Mac, Linux; full reveal planned for 2023. No planet/gravity/atmosphere details on the page.

## 3. Liftoff physics (secondary) [D-ag]
- GamingOnLinux, 7 Jan 2022 (`https://gamingonlinux.com/2022/01/liftoff-fpv-drone-racing-gets-a-huge-physics-update-new-racing-environment`):
  update 1.4.0 — LuGus rebuilt the physics with a "new flight controller", relying less on Unity's built-in physics;
  an "A.I. PID tune" feature; Unity upgrade. So Liftoff is a **Unity** product with a custom flight-physics layer.
- A pilot blog (search snippet [A]) says Liftoff simulates prop wash, wind and battery sag.

## 4. Skypersonic and NASA analog missions [D-ag]
- DroneDJ, 4 Aug 2022 (`https://dronedj.com/2022/08/04/skypersonic-drone-nasa-mars/`): 15-day trials on Mt Etna
  (July 2022), Skycopter UAV flown by pilots in Houston; rover sampled rocks; five-year NASA partnership for a
  simulated Mars mission; habitat Mars Dune Alpha (1,700 ft², four crew); **Skyloc** system controls and tracks drones
  where GPS is unavailable; "Long Range Real-Time Remote Piloting".
- Potomac Officers Club, 2 Dec 2022 (`https://www.potomacofficersclub.com/news/skypersonic-delivers-drone-rover-piloting-platform-to-nasa/`):
  platform delivered for NASA's **CHAPEA** (Crew Health and Performance Exploration Analog: one-year crew stay in a
  1,700 ft² simulated Mars habitat at JSC, first mission planned summer 2023); system "does not rely on GPS signals";
  NASA personnel trained on Skypersonic's **"Martian Simulator"**, a virtual environment based on photos and videos of
  the Martian surface.
- [A] CHAPEA applies a Mars-like communication delay (up to 22 min one way) to crew communications (search snippet; not
  confirmed for the drone link).

## What this means for a Venus version [Y]
- The Mars product is a **pilot-training simulator on a game engine (Unity/Liftoff)**: real-time 6-DOF drone, planet
  terrain from imagery, GPS-denied control, remote piloting. Public sources give no Mars-specific physics numbers.
- A "Venus Drone Simulator" in the same family would keep: real-time 6-DOF + rotor model, pilot UI, scenario training.
  It must change: atmosphere model (dense CO2, altitude-dependent ρ/T), the **air-mass frame** (65–100 m/s super-rotation
  as a moving reference, no ground in view), cloud-deck visuals (diffuse light, 1–2 km visual range, layer tops),
  convective gusts/downdrafts, solar-power-limited endurance, acid/thermal limits, and **no live stick from Earth**
  (2.3–14.3 min one-way light time, doc 25) → autonomy and relay windows as gameplay.
