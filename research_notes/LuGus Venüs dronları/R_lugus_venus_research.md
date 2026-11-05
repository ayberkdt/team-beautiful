# LuGus Studios: "Drones on Venus": research note for EUROAVIA Ideathon 2026

Prepared 2026-11-03, the day before the challenges are revealed. English. Every factual line has a source URL
and one of these tags:

- **[D]**: I read it on the source page or document during this session (WebFetch or local PDF text extraction).
- **[A]**: it came only from a search-engine summary or snippet. I did not open the primary page.
- **[Y]**: my own judgement, inference or calculation. Calculations are reproducible from
  `C:\Users\ayber\AppData\Local\Temp\claude\D--Masaustu-Ideathon-2026\5b6739d5-84c2-4008-bc95-72d94cabd8d3\scratchpad\tools\venus_calc.py`,
  and the output was saved next to it in `...\scratchpad\txt\venus_calc_out.txt`.

A "[D, secondary]" tag means I read the page, but the page is itself a secondary source, such as Wikipedia.
Do not quote [A] or [Y] items to the jury as hard facts without a caveat.

---

## 0. Headline findings (read this first)

1. **LuGus Studios is not a VR/digital-twin studio in Ghent.** It is a game and simulation studio in
   **Hasselt (Limburg, Flanders)**, founded in 2011. Its flagship product is the FPV drone simulator **Liftoff**.
   Its own site says it is "experts in high-fidelity drone simulation".
   [D] https://www.lugus-studios.be/ · [D] https://awards.belgiangames.be/studio/lugus-studios/
2. **LuGus has already put drones on another planet.** In 2022 it built a **Mars Drone Simulator** with the Italian
   drone company Skypersonic, "powered by Liftoff simulation technology". The simulator was used as a training
   tool for **NASA's Mars Analog Mission**, and ESA astronaut Roberto Vittori tested it.
   [D] https://www.lugus-studios.be/portfolio/mars-drone-simulator · [D] https://www.liftoff-game.com/node/221
3. **LuGus announced a consumer game, "Liftoff: Offworld"**, in August 2022. The announcement calls it a "physics
   sandbox layer" whose aim is to let players fly drones across the solar system, "just like NASA is doing today
   with the Ingenuity drone on Mars".
   [D] https://www.liftoff-game.com/node/215 · [D] https://www.liftoff-game.com/node/221
   I found no release of Offworld. [A] https://www.liftoff-game.com/news/community-questions-answered calls it
   "experimental" and "in full swing" (June 2023) [D on that page].
   → **"Drones on Venus" looks like the next planet for Offworld and Liftoff Core.** [Y]
4. In December 2025 LuGus won **Best Tech Provider** at the Belgian Game Awards. The citation names its **"Liftoff
   Core Modular Engine"** and its role in "NASA's analog Mars mission simulation", and says it enhances
   "efficiency and sustainability".
   [D] https://www.gamespress.com/The-winners-of-the-Belgian-Game-Awards-2025-have-been-announced
5. **The physics coincidence to build the pitch on [Y, computed]:** at **50–55 km** on Venus, gas density is about
   **0.94–1.6 kg/m³** and g = 8.87 m/s². A given multirotor therefore needs about the **same hover power as on
   Earth at sea level** (10 kg vehicle, 1 m disk: about 690 W at 55 km against about 700 W on Earth, ideal).
   The Liftoff flight model is essentially "Earth-valid" in the Venus cloud layer. What changes is the environment:
   60–100 m/s super-rotating wind, sulfuric acid, no GNSS or magnetic field, a 2.3–14.3 min light delay, and days
   of night. Near the **surface**, density is about **66 kg/m³**, so hover power falls about **8.6×**. At 735 K,
   however, no conventional battery, motor or silicon chip survives.
6. **Likely shape of the task [Y]:** a *simulation-ready* conceptual design, that is, a drone or drone system for
   Venus plus the physics, environment and training/operations model needed to simulate it. It is less likely to
   be a pure spacecraft-engineering brief. Prepare **both** a credible vehicle concept **and** a "how we would
   simulate and train for it" layer.

Things I could **not** find: (a) any web page with the spoiler text "LuGus Studios: Drones on Venus" or any
2026 sponsor list. The spoiler was neither on ideathon.euroavia.eu, nor in the local welcome PDF, nor in search
results. (b) Any LuGus–Venus, LuGus–ESA or LuGus–EUROAVIA link. (c) Any technical detail of how the Mars simulator
modelled Mars physics. (d) The original Seiff et al. 1985 VIRA tables. (e) The NASA NSSDC Venus fact sheet, which
timed out repeatedly. Details are in §9.

---

## 1. The event (to frame the 5-hour assumption)

| Item | What the source says | Tag / source |
|---|---|---|
| Dates | 3–8 November 2026, Brugge, hosted by EUROAVIA (AS) Oostende | [D] https://ideathon.euroavia.eu/ |
| Challenges | "four real-world industrial challenges set by leading aerospace companies"; confidential until the morning of 4 Nov | [D] https://ideathon.euroavia.eu/ |
| Jury | "a jury of industry and academic experts"; no criteria listed on the website | [D] https://ideathon.euroavia.eu/ |
| Language | English | [D] https://ideathon.euroavia.eu/ |
| Venue | KU Leuven Bruges campus; accommodation at Lybeer Hostel | [D] local file `D:\Masaustu\Ideathon 2026\EUROAVIA Ideathon 2026.pdf` (welcome booklet) |
| Schedule | 4/11: welcome, then competition; 5/11: competition morning and afternoon; 6/11: competition morning and afternoon, Cultural Night; 7/11: team presentations morning and afternoon; 8/11 departures | [D] same PDF (schedule grid; cell-to-day mapping read from extracted text, so roughly ±1 block) |
| Task framing | "UNDERSTAND – CREATE – REFINE – PITCH … It's not just about having the best technical answer. It's about creativity, teamwork, problem-solving" | [D] same PDF |

- The brief says each challenge is a ~5-hour sprint judged on feasibility, innovation, sustainability and
  presentation. Neither the website nor the PDF states this; I take it from the briefing, not a source. [Y]
- The PDF schedule shows about five competition blocks over 4–6 Nov. That is consistent with four challenges of
  roughly a half-day each. [Y]
- **Possible local link:** the LuGus homepage client wall appears to include **KU Leuven** (logo inferred from
  image file names by the fetch tool), and the venue is KU Leuven Bruges. The CosmiClean project lists KU Leuven
  as a partner [D] https://www.lugus-studios.be/portfolio/cosmiclean. This is a weak hint only. [Y]

---

## 2. Who is LuGus Studios? (confidence: high)

### 2.1 Identity

| Fact | Detail | Tag / source |
|---|---|---|
| Legal name and address | LuGus Studios BV, Aldestraat 48 bus 0001, 3500 **Hasselt**, Belgium | [D] https://www.lugus-studios.be/ |
| Founded | 2011 (Belgian Game Awards page gives 01/10/2011) by **Kevin Haelterman** and **Tom Lissens** | [D] https://awards.belgiangames.be/studio/lugus-studios/ |
| Name | From Lugus, the Celtic sun-god "of arts, trade and constant evolution" | [A] search snippet (indiedb/BGA) |
| Size | BGA lists 11; the team page shows 13 people incl. 2 external specialists | [D] https://awards.belgiangames.be/studio/lugus-studios/ · [D] https://www.lugus-studios.be/team |
| Tagline | "Serious about games"; "We build interactive experiences that push simulation and games beyond entertainment"; "As experts in high-fidelity drone simulation" | [D] https://www.lugus-studios.be/ |
| Services | Serious games, custom simulators, entertainment titles; concept research, launch, marketing, maintenance; six-step iterative process with paper/screen prototypes and user tests | [D] https://www.lugus-studios.be/how-we-work |
| Community role | Opened "Spawn Point", a co-working space for game developers in Hasselt (26 Jan 2026); founder Haelterman sits on the Flemish Games Association board | [D] https://www.lugus-studios.be/latest-news · [D] https://www.lugus-studios.be/team |
| Awards | BGA 2025 Best Tech Provider (Liftoff, Liftoff Core); six BGA 2023 nominations; BGA 2019 Best Business Award; IndieCade 2022 award for Midnight Protocol | [D] https://www.gamespress.com/The-winners-of-the-Belgian-Game-Awards-2025-have-been-announced · [D] https://www.lugus-studios.be/latest-news · [D] https://ir.redcatholdings.com/news-events/press-releases/detail/22/red-cat-holdings-signs-letter-of-intent-to-acquire-lugus-studios |

**Disambiguation.** The brief guessed "Ghent". Every source I read places LuGus in **Hasselt**. One Wikipedia list
reportedly says Genk [A] https://en.wikipedia.org/wiki/Video_games_in_Belgium (not opened). A separate "Lugus"
general partnership exists in Tongeren-Borgloon [A] https://busibee.be/en/0828229550-lugus. It is unrelated as
far as I can tell [Y]. I found no other aerospace company called LuGus. [A]

### 2.2 Portfolio: what matters for "Drones on Venus"

| Project | Relevance | Tag / source |
|---|---|---|
| **Liftoff: FPV Drone Racing** (PC, released 13 Sep 2018 after Early Access from 2015; dev and publisher LuGus) | "realistic and fully simulated physics and advanced flight dynamics"; level editor; online PvP; 7,205 English reviews, 95 % positive | [D] https://store.steampowered.com/app/410340/Liftoff_FPV_Drone_Racing/ |
| Liftoff: Drone Racing (PS4/Xbox One, Jan 2021); Liftoff: Micro Drones (Early Access Nov 2021; full release 4 Aug 2025) | The same simulation core across platforms and drone scales | [D] https://www.lugus-studios.be/latest-news?page=1 · [A] https://automaton-media.com/articles/newsjp/liftoff-micro-drones-20250805-352158/ |
| **Liftoff: XR Drone** (Meta Quest, 2024, free) | Drone flight in VR with an AR interface. XR capability exists. | [D] https://www.lugus-studios.be/portfolio/liftoff-xr-drone |
| **Mars Drone Simulator** (client Skypersonic, dated 01/09/2022) | "powered by Liftoff® simulation technology"; "currently being used as a training tool for NASA's Mars Analog Mission"; tested by ESA astronaut Roberto Vittori; "testing ground for … Liftoff: Offworld" | [D] https://www.lugus-studios.be/portfolio/mars-drone-simulator |
| **Liftoff: Offworld** (announced 22 Aug 2022) | "a physics sandbox layer" on top of Liftoff, "all about exploration", Early Access "first for PC, Mac and Linux" | [D] https://www.liftoff-game.com/node/215 |
| **Liftoff Core / Liftoff Academy** (enterprise arm) | "custom simulations for … industrial applications, research and development", pilot training; clients include the University of Zurich (custom build "to give access to more tools and data", human vs autonomous flight research), IUDRO, Skypersonic | [D] https://www.liftoff-game.com/node/15 |
| Skypersonic Simulator (11 May 2020) | Standalone trainer for the Skycopter inspection drone, part of the Liftoff Core programme | [D] https://www.liftoff-game.com/node/111 |
| **INTERREG BeNeDrone** (kick-off 9 Sep 2025; ref. Int6A069; 13 NL/BE partners) | Medical drone transport. Includes "virtual training environments where professionals and policymakers can prepare". LuGus is said to work on a "Drone Route Simulator" [A]. | [D] https://www.lugus-studios.be/portfolio/interreg-benedrone-project · [A] search snippet |
| CosmiClean (EIT RawMaterials; partners KU Leuven, Newcastle, TalTech, Arkema, BASF) | Space-themed educational recycling game. Shows a **sustainability / circular-economy** angle. | [D] https://www.lugus-studios.be/portfolio/cosmiclean |
| WoodworksVR, Snoezel VR, CHARMING (chemistry education ETN), Battery Workbench, Midnight Protocol, Battle for Donetsk, … | Serious-game and VR breadth; education and health | [D] https://www.lugus-studios.be/projects · [D] https://www.lugus-studios.be/latest-news?page=1 |
| Partnerships | DJI (DJI FPV drone in Liftoff, Mar 2022); Drone Legends (school drone curriculum, Nov 2022); astragon (publisher, 2019) | [D] https://www.lugus-studios.be/latest-news |

### 2.3 Tech stack

- **Unity.** Liftoff moved to Unity 2018.4 in a 2022 physics update and relies less on Unity's built-in physics,
  using its own flight controller model. [A] https://gamingonlinux.com/2022/01/liftoff-fpv-drone-racing-gets-a-huge-physics-update-new-racing-environment
  The team page lists Unity only in one artist's skills [D] https://www.lugus-studios.be/team.
- A 2023 "complete overhaul of Liftoff's core technology" was carried out to make future games "future-proof"
  [D] https://www.liftoff-game.com/news/community-questions-answered. This is likely what became
  "Liftoff Core Modular Engine" [Y].
- I found no Unreal, no WebGL product, and no published physics documentation. [D for absence on the pages read]
- **Team profile:** game and digital designers, computer-science programmers and technical artists. The team page
  describes no aerospace engineers [D] https://www.lugus-studios.be/team. → The jury from LuGus is likely to value
  **clear physical reasoning that could be turned into simulation parameters**, plus gameplay/training value. They
  are less likely to be impressed by heavy spacecraft jargon. [Y]

### 2.4 Corporate context

- In May 2021 Red Cat Holdings (US drone company) signed a **non-binding** letter of intent to acquire LuGus. The
  deal was to extend Red Cat into "Drone Pilot Training", and Liftoff Academy was to cover industrial training
  (oil and gas pipelines, cell towers, automotive plants).
  [D] https://ir.redcatholdings.com/news-events/press-releases/detail/22/red-cat-holdings-signs-letter-of-intent-to-acquire-lugus-studios
- I found **no evidence that the deal closed**. Red Cat 10-K excerpts in search results list other acquisitions
  but not LuGus [A]. LuGus still presents itself as independent in 2025–2026 [D lugus-studios.be]. Skypersonic is
  also a Red Cat subsidiary [A] https://executivebiz.com/?p=369950. That explains the NASA path:
  Red Cat/Skypersonic → NASA CHAPEA analog → LuGus simulator. [Y]
- On 24 Feb 2023 LuGus published an essay on Liftoff and FPV drones in the Ukraine war [D, title only, from the
  news list]. The studio is aware of dual-use issues. Keep a Venus concept clearly civil/scientific. [Y]

### 2.5 Links to ESA, Belgian space and VR training

- **ESA:** the only link is astronaut Vittori testing the Mars simulator [D]. There is no ESA contract on record
  in what I read. [D for absence]
- **BELSPO:** BelSPO leads procurement of instruments for ESA's EnVision Venus orbiter
  [D] https://www.esa.int/Science_Exploration/Space_Science/EnVision_factsheet. That is a Belgian Venus link for
  the pitch, but **not** a LuGus link. [Y]
- Redwire Space Kruibeke, ESA Redu, Euro Space Center Transinne: **no link to LuGus found.** I did not research
  these companies' own Venus work. [D for absence on LuGus pages; not searched further]
- **VR/XR training:** Liftoff XR Drone (Quest), WoodworksVR, BeNeDrone virtual training environments [D, above].

### 2.6 What LuGus probably wants out of this challenge [Y]

- **New content for Offworld or a training simulator:** a believable Venus drone, its flight envelope, environment
  model (density, wind, turbulence, acid, light, heat), mission objectives, and failure modes that are fun and
  educational to simulate.
- **Showcasing Liftoff Core as a tech provider:** the jury citation explicitly mentions research use and
  sustainability [D gamespress]. A team that shows how a simulator **reduces real hardware tests**, de-risks a
  mission and **trains operators** speaks their language.
- **Outreach and education:** their roots are in serious games for education [D BGA page].

---

## 3. The Venus environment

### 3.1 Bulk planet

| Quantity | Value | Tag / source |
|---|---|---|
| Surface gravity | **8.87 m/s²** (90.7 % of Earth's) | [D] Landis 2001 Table 1, https://ntrs.nasa.gov/citations/20020022923 (PDF text) · [D, secondary] https://en.wikipedia.org/wiki/Venus |
| Mean radius | 6051.8 km | [D, secondary] Wikipedia Venus · [D] local `src/aerokit/comms/constants.py` (R_VENUS_MEAN = 6 051 800 m, cites JPL) |
| Sidereal rotation | −243.02 d (retrograde) | [D, secondary] https://en.wikipedia.org/wiki/Venus |
| Solar day | **116.75 Earth days**; Landis rounds to 117 d | [D, secondary] Wikipedia · [D] Landis 2001 |
| Orbital period / synodic period | 224.7 d / 583.9 d (1.6 yr between launch windows) | [D] Landis 2001 Table 1 |
| Solar constant at Venus (top of atmosphere) | **2600 W/m²** (Earth 1370); Landis 2001 gives 2.62 kW/m² | [D] Landis et al. 2002 IAC, https://ntrs.nasa.gov/citations/20030022791 · [D] Landis 2001 |
| Bond albedo | 0.76 (Landis gives 0.8) | [D, secondary] Wikipedia Venus · [D] Landis 2001 |
| Magnetic field | No permanent field, so **no compass** | [D] VAPS 2018 §5.2, https://solarsystem.nasa.gov/system/downloadable_items/2693_Venus_Aerial_Platforms_Final_Report_Summary_Report_10_25_2018.pdf |

### 3.2 Atmosphere composition and surface state

| Quantity | Value | Tag / source |
|---|---|---|
| CO₂ / N₂ | **96.5 % / 3.5 %** | [D, secondary] https://en.wikipedia.org/wiki/Atmosphere_of_Venus (cites Basilevsky 2003) · [D] Landis 2001 Table 1 |
| Trace gases | SO₂ 150 ppm, Ar 70 ppm, H₂O 20 ppm, CO 17 ppm | [D, secondary] Wikipedia Atmosphere of Venus |
| Mean molar mass | **43.45 g/mol** | [Y] computed from 96.5/3.5 |
| Surface temperature | **737 K** (464 °C) mean; Landis gives 462 ± 2 °C; Vega 2 lander measured 736 K | [D, secondary] Wikipedia Venus · [D] Landis 2001 · [D, secondary] https://en.wikipedia.org/wiki/Vega_program |
| Surface pressure | **~92–93 bar** (9.3 MPa); Vega 2 measured 91 atm; NASA test chamber uses 9.3 MPa | [D, secondary] Wikipedia · [D] NTRS 20240013278 (Neudeck) |
| Surface density | **~65 kg/m³** (Wikipedia, Young et al. 2026 table); my ideal-gas value is 66 kg/m³ | [D, secondary] Wikipedia Venus · [D] Young, Dominguez & Schatzman 2026 (see §4.6) · [Y] |
| VIRA surface (COSPAR) | 92.1 bar, 64.8 kg/m³; the snippet's "753 K" is probably a typo for 735 K | [A] https://spenvis.oma.be/ecss/e_st_10_04c/ecss_18_07_02.htm (server returned 503) |
| Speed of sound at surface | **410 m/s** (Young table); 419 m/s by my estimate | [D] Young et al. 2026 Table 2 · [Y] |
| Surface winds | Generally < 2 m/s, average 0.3–1.0 m/s; < 2.8 m/s quoted elsewhere | [D, secondary] Wikipedia Atmosphere of Venus · [A] 0.3–0.9 m/s from four Venera sites, NASA CR-20240000076 search snippet |
| Surface light | About 14,000 lux (overcast-Earth-like); visibility about 3 km | [D, secondary] Wikipedia Atmosphere of Venus (citation [55]) |
| Solar energy absorbed at ground | ~17 W/m² planet average (about 2.5 % of incident); ~15 W/m² at the Pioneer Venus large-probe site | [A] Tomasko et al. 1980, https://ntrs.nasa.gov/citations/19810042419 and Arizona summaries; I did not reach the paper text |

### 3.3 Vertical profile 0–100 km

The table uses temperature and pressure from Wikipedia "Atmosphere of Venus", which cites its ref. [33]; I did not
trace that reference [D, secondary]. Density and speed of sound are **my ideal-gas calculations** with
M = 43.45 g/mol and γ ≈ 1.25–1.29 [Y]. I could **not** obtain the original Seiff et al. 1985 VIRA tables
(Adv. Space Res. 5(11); NTRS record 19870027595 has no full text [A]). Treat densities as ±5 %; real-gas effects at
the surface are a few percent [Y].

| Altitude (km) | Temperature (K) | Pressure (bar) | Density (kg/m³) | Speed of sound (m/s) | Note |
|---:|---:|---:|---:|---:|---|
| 0 | 735 | 93 | 66 | 420 | surface |
| 5 | 697 | 68 | 51 | 410 | |
| 10 | 658 | 48 | 38 | 400 | |
| 15 | 621 | 33 | 28 | 390 | |
| 20 | 579 | 23 | 21 | 370 | |
| 25 | 537 | 15 | 15 | 360 | |
| 30 | 495 | 10 | 11 | 340 | |
| 35 | 453 | 6.0 | 6.9 | 330 | |
| 40 | 416 | 3.5 | 4.5 | 320 | |
| 45 | 383 | 2.0 | 2.7 | 310 | Landis: "about 80 °C at 45 km, 2 bar" |
| 50 | 348 | 1.1 | 1.6 | 290 | ≈ Earth sea-level pressure near 49.5–50 km |
| 55 | 300 | 0.54 | 0.94 | 270 | **27 °C**: the "habitable" layer |
| 60 | 263 | 0.24 | 0.47 | 250 | |
| 65 | 243 | 0.099 | 0.21 | 240 | top of main cloud |
| 70 | 230 | 0.037 | 0.085 | 240 | |
| 80 | 197 | 0.0048 | 0.013 | 220 | |
| 90 | 169 | 3.8 × 10⁻⁴ | 1.2 × 10⁻³ | 200 | |
| 100 | 161 | 2.7 × 10⁻⁵ | 8.7 × 10⁻⁵ | 200 | |

Table check: `datawiz.tablo.denetle` gave **0 HATA, 4 UYARI**. All four warnings are "values span 6–7 orders of
magnitude / mixed decimals" in the pressure and density columns. This is intrinsic to a 0–100 km profile. I handled
it by giving two significant figures and scientific notation for the smallest values [Y].

Cross-checks:

- Landis 2001: pressure is 2 bar at about 45 km and 0.2 bar at about 60 km; temperature is about 80 °C at 45 km
  and −35 °C at 60 km; scale law P = P₀·exp(−h/15.8 km); lapse rate about 8 °C/km [D Landis 2001].
- LLISSE slides: 50 km = 67 °C; 60 km = −23 °C; 70 km = −43 °C
  [D] https://ntrs.nasa.gov/api/citations/20190029198/downloads/20190029198.pdf
- Wikipedia: 293–310 K between 52.5 and 54 km; Earth sea-level pressure at about 49.5 km (Pätzold 2007)
  [D, secondary].

**"Habitable" or temperate layer:**

- VAPS 2018 defines the "temperate zone" as **50–65 km where T < 77 °C**, with brief excursions to the cloud base
  at **47 km (100 °C)** [D VAPS §2.2].
- HAVOC calls 50 km "relatively benign, with similar pressure, density, gravity, and radiation protection to the
  surface of Earth" [D] https://ntrs.nasa.gov/citations/20160006329.
- Landis suggests 50–54 km for a base [D, secondary, Wikipedia citing Landis 2003].

### 3.4 Clouds and acid

- Main cloud deck about 48–70 km. The upper cloud is 60–70 km; the densest layer is near 48.5 km; there are haze
  layers to about 90 km on the night side [D, secondary] Wikipedia Atmosphere of Venus.
- The cloud particles are mainly sulfuric acid droplets [D Landis 2001]. JPL tests aerobot envelopes and seams
  against **94 % H₂SO₄** at about 100 °C [D] Goel/Izraelevitz JPL poster,
  https://smd-cms.nasa.gov/wp-content/uploads/2023/11/goel-aerobot.pdf.
- Mode-3 particles (30–58 km) carry most of the cloud mass; their composition is unknown [D Landis 2001].
- **Phosphine controversy:** JCMT gave about 20 ppb. The ALMA reanalysis gives a planet average of about 1–4 ppb,
  with local peaks of about 5–10 ppb. Values from other measurements are "under ~5 ppb at 60+ km, up to ~100 ppb
  at 50+ km". All of this is disputed [D] https://arxiv.org/abs/2011.08176v2 (Greaves et al., Nature Astronomy
  2021). SOFIA found an upper limit of about 0.8 ppb [A] https://www.universetoday.com/158983/.

### 3.5 Winds (super-rotation)

| Altitude | Zonal wind | Tag / source |
|---|---|---|
| ~45 km | 44–45 m/s | [D] Landis 2001 Table 1 (Vega-measured) |
| ~53 km | 65 m/s | [D] Landis 2001 Table 1 |
| ~54 km (Vega balloons) | 11,500 km covered in about 2 Earth days, i.e. **~67 m/s** average | [D] VAPS 2018 Foreword; [Y] division |
| ~60 km | 100 m/s | [D] Landis 2001 |
| Cloud tops (~65–70 km) | ~95 m/s (Landis 2002); 100 ± 10 m/s below 50° latitude; circles the planet in ~4 days, about 60× the surface rotation | [D] Landis 2002 IAC · [D, secondary] Wikipedia citing Markiewicz 2007 / Svedhem 2007 |
| Surface | 0.3–1 m/s | §3.2 |

- To stay at the subsolar point, a craft needs only **13.4 km/h ground speed at the equator**, but it must fly
  against the 95–100 m/s wind [D Landis 2001]. The wind decreases toward the poles [D Landis 2001].
- The meridional (N–S) wind reverses near 60 km (Hadley cell; Khatuntsev 2017). A variable-altitude platform can
  use this to steer in latitude [D VAPS §3.2].
- The Vega balloons recorded strong vertical motions ("vortices more powerful than hurricanes") [A]
  https://centennialofflight.net/essay/Lighter_than_air/Planetary/LTA16.htm. I have **no source** for turbulence
  intensity numbers.

### 3.6 Light and solar power vs altitude

- At the cloud base (~50 km) solar intensity is **20–50 % of exo-atmospheric**, depending on wavelength. It rises
  to **~95 % at 65 km** [D Landis 2002 IAC, citing Ekonomov et al. in *Venus* 1983].
- At 60 km the **upward (reflected) flux is about 90 % of the downward flux**, so **bifacial** arrays on both wing
  surfaces produce power [D Landis 2001, citing Pioneer Venus data].
- The JPL aerobot envelope was designed for 2300 W/m² of solar radiative heating [D JPL poster].
- On the night side, a craft at the equator spends **nearly two Earth days in darkness**. Batteries alone cannot
  keep an airplane aloft through this, and it cannot glide around the night side [D Landis 2002 IAC].
- The HOTTech portfolio includes "Low Intensity High Temperature (LIHT) Solar Cells for Venus" (JPL) [D LLISSE
  2019 slides]. Low-light, high-temperature cells are a recognised technology gap. [Y]

### 3.7 Transport properties (Reynolds number, viscosity)

- CO₂ dynamic viscosity: I used ≈1.5 × 10⁻⁵ Pa·s at 300 K and ≈3.3 × 10⁻⁵ Pa·s at 735 K. **[Y], not verified
  this session.** Young et al.'s Table 2 leaves the Venus viscosity cell blank [D].
- With those values, a 0.1 m chord at 40 m/s gives **Re ≈ 2.5 × 10⁵ at 55 km** (terrestrial small-UAV regime) and
  **Re ≈ 8 × 10⁶ at the surface** [Y, computed].
- Young et al. (NASA Ames, 2026): "it is not fully understood how Reynolds number aerodynamic effects will behave,
  relative to that seen on Earth, due to the different atmospheric gas composition" [D]. Above the clouds, they
  judge the aerodynamics "typical of terrestrial applications" [D].
- Gas constant 189 J/(kg·K) and γ = 1.286 for Venus [D Young 2026 Table 2]. Note that Young lists the gas constant
  in the wrong units ("J/Mol K") [D].

### 3.8 Communications geometry

- One-way light time Earth–Venus is **2.3 min at closest (0.277 AU)** and **14.3 min at the far side (1.72 AU)**.
  [Y] computed from a_Venus = 0.72333566 AU [D local constants.py, cites JPL approx_pos] and a_Earth ≈ 1.0 AU.
- There are solar-conjunction outages around superior conjunction [Y, standard; not sourced here].
- Direct-to-Earth from an aerial platform is possible, but **an orbiter relay gives far higher data rates at lower
  platform power**. The best relay is a circular equatorial orbit [D VAPS §5.1]. A SmallSat relay is enough for most
  non-imaging concepts (Venus Bridge) [D VAPS §5.1, §7.3].
- Earth-based radio localisation of the platform can reach **< 100 m when it is on the Earth-facing side**, but
  only about **30 % of the time** because of link losses [D VAPS §5.2].
- Vega used 20 radio telescopes in two networks (Soviet and CNES-coordinated). The balloons transmitted at
  2048 bit/s with 5 W [D, secondary] https://en.wikipedia.org/wiki/Vega_program.

---

## 4. Prior art

### 4.1 Missions flown

| Mission | What was done | Tag / source |
|---|---|---|
| **Vega 1 & 2 balloons (June 1985)** | 3.54 m helium **superpressure** spheres with a **PTFE**-surfaced envelope; 6.9 kg gondola on a 13 m tether; **21 kg** total; deployed at ~55 km, dropped to ~50 km while inflating, floated at **54 km**; > 46 h until the batteries ran out (60 h design); measured T, p, wind, aerosol, light; 2048 bit/s, 5 W | [D, secondary] https://en.wikipedia.org/wiki/Vega_program · [D] VAPS 2018 (3.5 m, 7 kg, 46 h, 11,000–11,500 km) |
| Vega landers | Vega 2 measured 91 atm and 736 K at the surface; anorthosite-troctolite sample | [D, secondary] Wikipedia Vega program |
| Venera landers | Surface life limited by thermal mass; "best to date ~127 mins" | [D] Kremic et al. 2019 IPPW slides (LLISSE) |
| Pioneer Venus (1978) | Orbiter plus four entry probes; Pioneer Venus small probes used a 1.2–1.3 m aeroshell, which Landis re-used as the packaging constraint for his airplane | [D] Landis 2001, 2002 |
| Venus Express (ESA 2005), Akatsuki (JAXA 2010), Parker Solar Probe flybys 2018–2024 | Atmosphere and winds from orbit | [D] Young et al. 2026 Table 1 · [D] VAPS §5.3 |
| Total | "Over forty missions"; surface hardware survives "an hour or so" | [D] Young et al. 2026 |

### 4.2 Planned and near-term missions (status as of Nov 2026)

| Mission | Status | Tag / source |
|---|---|---|
| **ESA EnVision** | Orbiter; Ariane 6 (64) launch **planned Nov 2031**; 15-month cruise; 11 months aerobraking; 220–510 km polar orbit; VenSAR (NASA), SRS, VenSpec-M/U/H, RSE; **BelSPO** procures an instrument; Thales Alenia Space prime (contract 28 Jan 2025) | [D] https://www.esa.int/Science_Exploration/Space_Science/EnVision_factsheet |
| EnVision slip and NASA exit? | Reports say the launch slipped to 2032 and NASA ended participation (Oct 2026). **Not confirmed from ESA/NASA.** | [A] https://en.wikipedia.org/wiki/EnVision, hwbusters.com snippet |
| **NASA DAVINCI** | Descent probe plus flybys. FY2026 budget proposed cancellation; Congress funded it; launch reported as Dec 2030 | [A] https://payloadspace.com/venus-exploration-hangs-in-the-balance/ and others |
| **NASA VERITAS** | Radar orbiter; launch reported Nov 2032 | [A] same group of search results |
| **Rocket Lab / MIT Venus Life Finder** | ~20 kg, 40 cm probe; one autofluorescence nephelometer; samples **60–45 km** for **3–5 minutes** while falling; Electron/Photon originally | [D] https://www.planetary.org/space-missions/rocket-lab-venus-mission (page partly dated) |
| VLF launch status | Unscheduled; now tied to Neutron readiness | [A] https://www.space.com/astronomy/venus/rocket-issues-delay-1st-ever-private-mission-to-venus-we-are-awaiting-neutron-readiness |
| **MIT-led Venus Life Finder Mission Study** (Breakthrough, Dec 2021; arXiv 2112.05153) | Series: probe → balloon → cloud sample return; balloon "best aerial platform for extended sampling" | [A] https://astrobiology.com/2022/08/venus-life-finder-missions-motivation-and-summary.html · MDPI page returned 403 |
| NIAC Phase I "Venus Atmosphere and Cloud Particle Sample Return" (Seager) | Balloon gondola collects samples, rises to ~70 km, launches an ascent vehicle to an orbiter | [A] https://www.nasa.gov/science-research/planetary-science/planetary-environments-atmospheres/venus-atmosphere-and-cloud-particle-sample-return-for-astrobiology |

### 4.3 Aerial-platform concepts and studies

**NASA/JPL Venus Aerial Platforms Study (KISS, Oct 2018, JPL D-102569)**
[D] https://solarsystem.nasa.gov/system/downloadable_items/2693_Venus_Aerial_Platforms_Final_Report_Summary_Report_10_25_2018.pdf

- 52 experts compared fixed-altitude balloons, four variable-altitude balloon types, a solar airplane and a hybrid
  airship (VAMP). The four balloon types are phase-change fluid, mechanical compression, pumped helium, and air
  ballast like Google Loon.
- **Conclusion:** "variable altitude balloons are the optimal choice". There are "no technological show-stoppers".
- Variable altitude in the nominal range of 50–60 km is the "sweet spot". The 40–60 km extended range gives more
  science but is less mature.
- A 7.4 m superpressure balloon carries a 110 kg gondola with 25–30 kg of science.
- The solar airplane must fly at ~100 m/s against the wind to stay sunlit. It cannot cross the night side and cannot
  go deep because clouds block sunlight.
- **Sondes:** "sondes as small as 5 kg could carry a useful payload of 1 kg and survive and operate all the way to
  the surface enabling close up imaging". → **The drone-swarm-from-a-mothership idea has an official precedent.**
- On GN&C, viewing stars from inside the cloud deck is infeasible. Sun location better than 10° may be impractical,
  and there is no magnetic field.
- On modelling, the study explicitly calls for Venus environment models, platform models, sensor models and an
  **autonomy simulation environment**: "The platform may be out of contact with ground controllers for periods in
  which the vehicle travels thousands of kilometers". → **This is exactly LuGus's competence.** [Y]
- Google Loon flew 190 days at 20 km, which the study treats as "equivalent to 70 km on Venus".

**JPL variable-altitude aerobot (JPL + Near Space Corp. + WashU)**
[D] https://www.jpl.nasa.gov/news/jpls-venus-aerial-robotic-balloon-prototype-aces-test-flights (10 Oct 2022) ·
[D] https://smd-cms.nasa.gov/wp-content/uploads/2023/11/goel-aerobot.pdf

- "Balloon within a balloon". The inner reservoir is Vectran-reinforced and pressurised with helium. The outer
  balloon is metallised and Teflon-coated against acid and sunlight.
- Pumping helium between the two changes buoyancy and therefore altitude.
- Full scale is **12–15 m diameter**, carries **100–200 kg** of gondola (design points 100–230 kg), and controls
  altitude between **52 and 62 km**. The goal is at least 100 days of circumnavigation.
- Subscale (1:3) prototypes flew twice in **July 2022** over the Black Rock Desert, at densities matching
  **54–55 km on Venus**. Both were recovered.
- The envelope must inflate in about **10 minutes** while hanging from a parachute.
- JPL used the **FLOATS** flight-dynamics model (DARTS toolkit), validated against hangar flights. → **Simulation
  is part of the real programme.**
- TRL 5 evaluation was planned for Fall 2023. Science includes infrasound from venusquakes, cloud chemistry and
  remnant magnetism.
- A later paper "Flight Demonstration and Model Validation of a Prototype Variable-Altitude Venus Aerobot" exists
  [A] https://arxiv.org/abs/2411.06643 (not opened).

**Landis (NASA Glenn) solar airplane, 2001–2004**
[D] Landis 2001 STAIF, https://ntrs.nasa.gov/citations/20020022923 ·
[D] Landis, LaMarre & Colozza 2002 IAC-02-Q.4.2.03, https://ntrs.nasa.gov/citations/20030022791

- Venus is "perhaps the easiest planet in the solar system for flight of a long-duration solar airplane" [D 2001].
- Folding wing (2 folds) fitted to a 1.2–1.3 m Pioneer-Venus-small-probe aeroshell. The plane unfolds and drops
  from the parachute at **65–70 km**, then descends to its working altitude.
- The analysis used **65–75 km** flight altitude. The plane can glide down for hours and then climb back.
- An inflatable-wing alternative builds on NASA Dryden I-2000 tests.
- Acid: "all exposed surfaces … coated by materials impervious to chemical attack", e.g. glass plus Teflon over the
  arrays. "Sulfuric acid is a common industrial chemical, and the technology of dealing with it is well developed."
- Science: super-rotation, UV absorber, mode-3 particles, sulfur cycle and volcanic plumes. Radar from tens of km
  gives **10× resolution and 100× less power** than orbit. It also suggests **dropping surface probes**, **formation
  flight of 2+ aircraft**, a **fleet of solar aircraft** for a climate "snapshot", and life detection (CO, H₂S/SO₂,
  OCS disequilibrium per Schulze-Makuch).
- "A significant benefit of the Venus airplane will be its 'fun' factor". → Quote this to LuGus [D 2001].
- Colozza 2004, "Feasibility of a Long Duration Solar Powered Aircraft on Venus", AIAA 2004-5558, is cited by
  Young 2026 [D]. I did not read it.

**Northrop Grumman VAMP (Venus Atmospheric Maneuverable Platform)**
[D] Sen et al., EPSC2015-873, https://meetingorganizer.copernicus.org/EPSC2015/EPSC2015-873.pdf

- A semi-buoyant inflatable aircraft with a ballistic coefficient below 50 Pa. It deploys **before** entry and
  enters **without an aeroshell**.
- Operates at 52–68 km. Subsonic flight begins at about 94 km and reaches the 68 km cruise in under an hour.
- Nominal life **~150 days**, more than 20 circumnavigations at mid-latitude, with orbiter relay.
- Per VAPS, VAMP rises to 60 km on solar power by day and sinks to 50 km by night, and can move in latitude
  [D VAPS §3.4].
- "~100 lb payload" and "10 % buoyant / 110 km/h" figures appear in secondary sources [A]
  https://en.wikipedia.org/wiki/Venus_Atmospheric_Maneuverable_Platform. The Northrop page I fetched no longer
  mentions VAMP [D].

**NASA Langley HAVOC (2015)**
[D] Arney & Jones, AIAA SPACE 2015, https://ntrs.nasa.gov/citations/20160006329 ·
[D] https://www.nasa.gov/general/havoc/

- Solar-powered airships at **50 km**. The programme is evolutionary, starting robotic and ending with a crew of two
  for **30 days**.
- Its stated challenges include aerocapture, in-atmosphere insertion and inflation, and protecting solar panels and
  structure from acid.
- A 21 m³ habitat and an SLS Block IIB dependency are mentioned [A IEEE Spectrum snippet].

### 4.4 Rotorcraft and "drones" specifically: the closest prior art

**Young, Dominguez & Schatzman (NASA Ames), "Past, Present, and Future Conceptual Designs for Venus Aerial
Explorers"**, VFS Vertical Lift Aircraft Design & Aeromechanics Specialists' Conference, San José, **27–29 Jan
2026**, DOI 10.4050/SM-2026-VLADA-5216.
[D] https://rotorcraft.arc.nasa.gov/Publications/files/Venus%20Aerial%20Explorers_Paper_v6C.pdf
**This is the most relevant and most recent paper. Read its figures if time allows.**

- It sorts flyers into four classes:
  - **above the clouds (ATC, > 60 km)**
  - **below the clouds (BTC, < 50 km)**
  - **near or on surface (NOS, < 10 km)**
  - **dive or cycle (DC)**
- **ATC:** almost always solar-electric **flying wings**. The main challenge is **mid-air deployment from the
  aeroshell**, plus dive/pull-out and aeroelastic stability of hinged wings. Prior mid-air deployment experience is
  limited to 2–4 wing folds. Propeller blades may need spring-loaded unfolding.
- **BTC (25–50 km):** re-purpose the NASA Langley **ARES Mars airplane** with an external **MMRTG**. An MMRTG gives
  "approximately a hundred watts", but much less at Venus because the temperature difference is small, so it
  cannot sustain level flight. Use it for instruments and battery-charged bursts of propulsion. Add **dropsondes**.
- **NOS:** a twin-hull pressurised hybrid rotorcraft with tilting wings and propellers, or a **stopped cycloidal
  rotor** vehicle. Electronics "heat death" limits it to **a few hours**. "Despite the major environmental
  challenges it poses, rotary-wing flight near the surface should not be abandoned."
- **DC:** **rotary-wing decelerators** (descent probe with autorotating rotor; Young et al. 2004 IPPW), a
  **samara-seed microprobe** (MiSSiVE, 2013), a **lifting-body autogyro** (LBA) entry vehicle with deployable
  side-by-side rotors, the **"Petey"** stopped-rotor UAV cycling between altitudes for thermal control, and a
  falcon-stoop bio-inspired dive.
- Its technology challenge list includes new actuators, motors, power electronics and batteries for below-cloud and
  surface flight, and "AI/ML applications for vehicle GNC and autonomy in flight on Venus". The test list includes
  pools, lakes and oceans as analogues, volcanic geysers, and Earth airship demonstrators.
- The team plans NIAC proposals.

Other rotorcraft items:

- Stopped-rotor cyclocopter for Venus, said to be able to fly "at all atmospheric levels of Venus as well as landing
  on the surface" (Husseyin, NASA Ames intern report, 2016) [A] https://ntrs.nasa.gov/citations/20160012563.
- Russian studies of **multirotor aircraft for Venus** (Bauman MSTU; Vestnik MAI) [A]
  https://engjournal.bmstu.ru/eng/catalog/arse/adb/2255.html · https://www.vestnikmai.ru/eng/publications.php?ID=180649.
- Landis, Oleson & Colozza, "A Conceptual Architecture for Venus Surface Sample Return", AIAA ASCEND 2024. Young
  cites it for "cycling" vehicles [D citation only].

### 4.5 Long-lived surface technology (relevant to any "surface drone")

**SiC JFET-R integrated circuits (NASA Glenn, P. Neudeck)**
[D] https://ntrs.nasa.gov/citations/20240013278 (abstract, Dec 2024)

- Operated for **over 1 year at 500 °C** in air.
- Operated **60 days in 460 °C / 9.3 MPa caustic Venus surface conditions** (GEER chamber).
- Survived 7 Mrad(Si) TID, and worked from −190 °C to +812 °C.
- A commercial foundry is moving toward mass production. Complexity is "far below silicon-based ICs".
- The 60-day test used **175-transistor clock ICs, unshielded** [A NASA project page snippet]. An earlier GEER run
  of 521 h was published in AIP Advances (2016) [A].

**LLISSE (Long-Lived In-situ Solar System Explorer, NASA Glenn)**
[D] Kremic et al., IPPW July 2019, https://ntrs.nasa.gov/api/citations/20190029198/downloads/20190029198.pdf

- Design approach: "design lander to function indefinitely without pressure or temperature control – use all high
  temperature components".
- Goal: 60 days in Venus conditions, with comms at 1–10 MHz and a thermal battery.
- Mass ~10 kg; a larger SAEVe concept is ~25 kg for 120 days [A].
- Data are sent to the orbiter about every 8 h [A].
- The molten-salt battery is "first to demonstrate the capability to operate at Venus temperatures for an entire
  Venus solar day" [A] https://science.nasa.gov/technology/technology-highlights/providing-power-on-earth-s-evil-twin.
- **Material results from GEER exposure** [D, same slides]:

  | Material | Result |
  |---|---|
  | Au, Ir | no reaction but mobile |
  | SiC, AlN | no reaction |
  | Cu | forms Cu₂S |
  | Ni | forms NiS |
  | Inconel 625 | NiS + CrₓOᵧ |
  | 304 SS | low corrosion |
  | Sputtered Al | reacts with HF |
  | Ti | surface oxide |

  "Reactive chemistry is an under appreciated issue". **Copper wiring is a problem.**
- **HOTTech tasks** [D, same slides]:
  - 500 °C electronics packaging
  - high-temperature primary batteries (HiTALL) and a Li–S battery
  - **LIHT solar cells**
  - SiC chemical sensors
  - diamond electronics
  - **high-temperature GaN microprocessor** (Univ. of Arizona)
  - **TRL 6 Venus electric motor and position sensor** (Honeybee Robotics)
  - vacuum field-emission devices above 500 °C
  - chip-scale clocks

**Wind power at the surface**
[D] Colozza, NASA/CR-20240000076, https://ntrs.nasa.gov/citations/20240000076

- A small vertical-axis turbine sized for a LLISSE probe produces "usable amounts of power for a low-power Venus
  lander" once it is turning, but it is "not capable of starting on its own".
- The report suggests a starting motor or a horizontal-axis design.
- An older 2013 Glenn study compared a land-sailing rover with a turbine-powered rover [A]
  https://ntrs.nasa.gov/citations/20130010972.

**Venus Bridge (VEXAG, 2018)**

- A very low-cost orbiter plus in-situ element, such as a Vega-size superpressure balloon. The orbiter provides
  relay, localisation and science.
- Treated as a Class D opportunity [D VAPS §7.3].

### 4.6 Analogues: Ingenuity and Dragonfly

**Ingenuity (Mars)**
[D] https://science.nasa.gov/mission/mars-2020-perseverance/ingenuity-mars-helicopter/

- 1.8 kg; rotor span about 1.2 m.
- Solar panel charges Li-ion batteries, enough for one 90 s flight per sol; about 350 W average in flight.
- **72 flights** from 19 Apr 2021 to 18 Jan 2024; 128.8 min and 17.0 km in total.
- It was a tech demo planned for 5 flights in 30 days. The final flight damaged rotor blades [A news coverage].
- Lessons for Venus [Y]:
  - start as a technology demonstration;
  - autonomy is mandatory;
  - relay through a mothership (Perseverance there; a balloon or orbiter on Venus);
  - "unplanned longevity" is the outreach story.

**Dragonfly (Titan)**

- A nuclear (MMRTG) **octocopter relocatable lander**. Launch window **5–25 July 2028** on Falcon Heavy; arrival
  2034 [A] https://en.wikipedia.org/wiki/Dragonfly_(Titan_space_probe) and NASA statements in search results.
- Landing mass is reported as ~875 kg [A, sources conflict].
- Titan density is 5.4 kg/m³ against 1.225 on Earth [D Young 2026 Table 2].
- The Venus surface (66 kg/m³) is about **12× denser than Titan** [Y]. Dragonfly's dense-atmosphere rotor
  experience is the nearest analogue for a near-surface Venus rotorcraft. Its 94 K temperature is the opposite
  thermal problem [Y].

---

## 5. Engineering consequences (numbers to carry into the room)

### 5.1 Rotor and propeller sizing: hover power scales as 1/√ρ

Ideal hover power is P = T^1.5 / √(2ρA). The case below is a **10 kg vehicle** with an equivalent 1.0 m-diameter
disk (A = 0.785 m²), and figure of merit 0.65 for the "real" column [Y, computed].

| Environment | ρ (kg/m³) | g (m/s²) | Induced velocity (m/s) | Ideal hover power (W) | With FM 0.65 (W) |
|---|---:|---:|---:|---:|---:|
| Earth, sea level | 1.2 | 9.81 | 7.1 | 700 | 1100 |
| Mars (Young table ρ) | 0.012 | 3.71 | 45 | 1700 | 2600 |
| Venus 60 km | 0.47 | 8.87 | 11 | 970 | 1500 |
| **Venus 55 km** | **0.94** | 8.87 | 7.8 | **690** | **1100** |
| Venus 50 km | 1.6 | 8.87 | 5.9 | 520 | 810 |
| Venus 30 km | 11 | 8.87 | 2.3 | 210 | 320 |
| Venus 10 km | 38 | 8.87 | 1.2 | 110 | 170 |
| **Venus surface** | **66** | 8.87 | 0.92 | **82** | **130** |
| Titan surface | 5.4 | 1.35 | 1.3 | 17 | 26 |

Inputs and checks:

- The Mars density 0.0117 kg/m³ and Titan density 5.4 kg/m³ come from Young et al. 2026 Table 2 [D]. Titan
  g = 1.35 is [Y, not verified].
- Table check: `tablo.denetle` was run on the profile table only. This table is hand-formatted to two significant
  figures [Y].

Interpretation [Y]:

- **At 50–55 km an Earth multirotor works roughly as designed.** A Liftoff-tuned drone (prop pitch, motor KV,
  battery) would "feel" familiar. Simulation parameters change mainly through ρ, g, wind and gusts.
- **At the surface** the induced velocity falls below 1 m/s and power drops about 8.6×. You get **large, slow
  rotors** (low tip Mach, since the speed of sound is about 410 m/s), very high blade loads per unit speed, and
  strong ground effect. Dynamic pressure 0.5ρV² at 50 m/s is about **83 kPa at the surface** against about
  **1.2 kPa at 55 km** [Y].
- A **1 m/s surface breeze** on Venus has the same dynamic pressure (~33 Pa) as a **7.4 m/s wind on Earth** [Y].
  Even gentle Venus surface winds push hard, which also makes wind turbines work.
- **Buoyancy reduces rotor work everywhere.** See §5.2. A hybrid buoyant drone ("blimp-copter") only needs rotors
  for manoeuvring and trim. That is the energy-optimal design.
- **Station-keeping against super-rotation with rotors is impossible** on battery power. A quadrotor in still air
  reaches tens of m/s for minutes, while the wind is 60–100 m/s for days. → Operate **in the air-mass frame**: drift
  with the wind, as balloons do, and use rotors for local sampling and altitude changes. Or use a fixed-wing
  airplane for ground-relative control (Landis). [Y, consistent with VAPS §3.3 [D]]

### 5.2 Buoyancy in a CO₂ atmosphere

The table gives gross lift per m³ of lifting gas at ambient p and T, before envelope mass and superpressure
[Y, computed]. Ambient molar mass is 43.45 g/mol.

| Gas (M, g/mol) | 50 km (kg/m³) | 55 km (kg/m³) | 60 km (kg/m³) | Surface (kg/m³) |
|---|---:|---:|---:|---:|
| H₂ (2.0) | 1.5 | 0.89 | 0.45 | 63 |
| He (4.0) | 1.5 | 0.85 | 0.43 | 60 |
| N₂ (28.0) | 0.58 | 0.33 | 0.17 | 24 |
| Earth air 79/21 (29.0) | 0.54 | 0.31 | 0.16 | 22 |
| O₂ (32.0) | 0.43 | 0.25 | 0.13 | 18 |

Interpretation [Y]:

- **Breathable air is a lifting gas on Venus.** It gives about 37 % of helium's lift at 55 km. This is the basis of
  HAVOC and "cloud city" ideas. The surface numbers are hypothetical, because the envelope would have to survive
  735 K. JPL has studied metal-bellows balloons; I did not read that here.
- **Helium vs hydrogen:** hydrogen gives only about 5 % more lift. Helium is inert, and the JPL aerobot uses it
  [D JPL]. Hydrogen leaks more and raises a flammability question. That question is moot in an O₂-free atmosphere,
  but matters during ground handling.
- **Sizing example (55 km):** a 20 kg drone-plus-envelope needs about **24 m³ of He**, a sphere of about 3.6 m
  diameter. That matches Vega's 3.54 m sphere for 21 kg [D Vega]. **Use Vega as a sanity anchor in the pitch.**
- The **JPL aerobot (12–15 m, 100–200 kg)** sets the "mothership" scale [D].

### 5.3 Materials against H₂SO₄ and heat

- **PTFE/FEP (Teflon) coatings** on envelopes and arrays [D Vega PTFE; D JPL Teflon-coated outer balloon; D Landis
  glass + Teflon].
- **Vectran** reinforcement for pressure layers [D JPL]. Metallisation reduces solar heating [D JPL].
- Heat-sealed seams were tested by acid immersion at elevated temperature [D JPL poster].
- For hot and surface operation:
  - **SiC, AlN** and **304 stainless** behave well [D LLISSE GEER table];
  - **avoid Cu, Ni, Ag–Cu braze and sputtered Al** [D same];
  - Au and Ir are inert but mobile [D].
- Sensor windows: sapphire or quartz are typical in Venus probe designs. **[Y, not verified this session]**
- Propellers and rotors for the cloud layer: carbon fibre with a fluoropolymer coating or encapsulation [Y]. Motors
  should be sealed and purged, with bearings protected from acid aerosol [Y].

### 5.4 Thermal

- In the 50–65 km band, T is below 77 °C, so conventional electronics work [D VAPS]. Short excursions to 47 km
  (100 °C) are possible with passive thermal mass [D VAPS §4.2.3].
- The **"cycle" strategy**, diving into heat and climbing back to cool, is an established concept [D Young 2026,
  Fig. 13 "cycling … for thermal control"].
- Below the clouds, conventional electronics survive only with thermal mass or phase-change material, and last
  minutes to hours [D: Venera ~127 min, LLISSE slides]. The alternative is all-high-temperature electronics (SiC/GaN)
  with very limited computing [D Neudeck].
- **Implication for a surface "drone":** either a short-lived sprint (< 2 h) with an insulated, phase-change-cooled
  avionics core, or a slow, simple SiC vehicle. **Autonomy and imaging would then live on the balloon or mothership
  above.** [Y]

### 5.5 Power

| Option | Where it works | Tag / source |
|---|---|---|
| Solar, bifacial | > 50 km; ~95 % of 2600 W/m² at 65 km; 20–50 % at the cloud base | [D] Landis 2002, 2001 |
| Solar on the night side | Nothing for ~2 Earth days at the equator, so drift-mode platforms must survive the night on batteries or by floating passively | [D] Landis 2002 · [Y] |
| Li-ion batteries | Cloud layer only, below ~60 °C [Y] | — |
| Molten-salt thermal battery | Surface, days to months, very low power | [D] LLISSE slides · [A] NASA power page |
| MMRTG (~100 W nominal; Pu-238) | Below clouds, degraded output because ΔT is small; good for instruments, not flight | [D] Young 2026 |
| Wind turbine | Surface, low power, needs a starter | [D] Colozza 2024 CR |
| Wireless power or beamed laser from a balloon to a surface drone | Speculative | [Y] |
| Buoyancy as an "energy store" | Climb with gas transfer, glide down: free horizontal transport | [Y]; the "Petey" and "cycling" concepts [D Young 2026] |

### 5.6 Communications

- The drone talks to its **mothership** (balloon/aerobot) or directly to an **orbiter relay**. The mothership talks
  to the orbiter, and the orbiter talks to Earth [D VAPS §5.1; JPL "companion orbiter … relays it to Earth"].
- The light time of **2.3–14.3 min one way** rules out joystick piloting from Earth [Y computed]. **Even an FPV
  racing pilot cannot fly it live.**
  - Simulator angle: train operators on **supervisory control with delay**, as with Mars rover and Ingenuity
    planning. [Y]
  - Alternatively, train **mission designers** in the simulator and use **autonomy** for flight. [Y]
- Vega achieved 2048 bit/s with 5 W direct to Earth from 54 km [D, secondary].

### 5.7 Navigation without GNSS

- Impossible or unavailable: GNSS, magnetic compass (no field), stars from inside the clouds [D VAPS §5.2].
- Sun sensing may be worse than 10° [D VAPS §5.2]. Above about 65 km the Sun disk becomes usable [Y].
- Available [Y unless marked]:
  - **IMU** dead reckoning;
  - **barometric altitude** (excellent, given the well-mapped p(h));
  - airspeed/wind sensors;
  - **radio ranging and Doppler to the orbiter or mothership**;
  - Earth VLBI-type tracking as with Vega [D] (< 100 m about 30 % of the time [D]);
  - **inter-drone ranging in a swarm**;
  - **near-IR surface imaging** through the 1 µm windows on the night side for terrain-relative navigation
    [Y; not sourced here];
  - radar altimetry over terrain for low-altitude drones [Y].
- Attitude needs gyro-compassing from planetary rotation. Venus rotates very slowly (243 d), so this is very
  weak [Y]. → Star trackers on the mothership above the clouds, relayed attitude, or Sun sensing at high altitude
  [Y].

### 5.8 Autonomy

- VAPS states the requirement directly: an "autonomous control system will ensure that the platform remains in a
  safe zone constrained by temperature and the solar radiation environment and executes timely scientific
  operations including deployment of probes and sondes" [D VAPS §6.4.4].
- Young 2026 lists AI/ML for GNC and autonomy as a technology challenge [D].
- Ingenuity flew autonomously from uplinked plans [Y; the NASA page did not describe its navigation].

### 5.9 Entry and deployment

- Rigid aeroshell → parachute → inflate the balloon in about 10 min [D JPL], or unfold the airplane at 65–70 km and
  drop it [D Landis 2001].
- Alternatively, inflate before entry and enter without an aeroshell (VAMP) [D].
- Mid-air deployment of folded wings is the hardest step [D Young 2026].
- **Drones deployed from a balloon gondola** need no entry system of their own. VAPS 5 kg sondes are the precedent
  [D VAPS]. That makes **"mothership + daughter drones" the most feasible drone architecture.** [Y]

---

## 6. Predictions: how the challenge may be phrased (ranked)

Ranking reflects LuGus's portfolio (drone simulation, Mars sim for NASA, Offworld, training, education), the
one-line spoiler "Drones on Venus", the Ideathon's aerospace audience and a 5-hour format. All of §6 is **[Y]**,
except numbers that are cited back to §3–§5.

### P1 (most likely). "Design a drone (or drone system) that can explore Venus, and define what is needed to simulate it realistically"

- **Jury expects:**
  - a feasible vehicle for a chosen altitude band, with numbers;
  - the **environment parameters a simulator needs** (ρ, T, p, g, wind profile, turbulence, light, acid,
    comms delay);
  - mission objectives that are fun and meaningful;
  - a clear sustainability story;
  - a crisp pitch.
- **Strong concept: "CLOUDHOPPER"**, a **buoyancy-assisted quadrotor (hybrid) deployed from a variable-altitude
  aerobot**:
  - **Altitude band:** works at 50–62 km, with excursions down to 47 km; daughter drones "dip" to 45 km for
    minutes.
  - **Platform:** a small He envelope (~0.8–0.85 kg/m³ lift at 55 km) gives about 80–90 % static lift. 4 ducted,
    fluoropolymer-coated rotors handle trim, sampling manoeuvres and ±2 km altitude hops. Hover power for a 10 kg
    fully rotor-borne vehicle at 55 km is about 1.1 kW; with 85 % buoyancy it is about 60 W [Y, scaling T^1.5:
    0.15^1.5 × 1060 W ≈ 62 W]. Cross-check: Vega's 3.54 m sphere holds 23.2 m³ of He, which lifts ≈ 20 kg at
    55 km; Vega's actual total was 21 kg [Y computed / D Vega].
  - **Power:** bifacial thin-film solar on the envelope top and bottom (upward flux about 90 % of downward at 60 km)
    plus Li-ion for the night side. Drift in the air mass; at night, float passively at neutral buoyancy.
  - **Thermal:** stays below 77 °C. Dips use thermal mass and phase-change material. Dive/climb cycling for cooling
    follows Young 2026.
  - **Materials:** PTFE/FEP films, Vectran, sealed motors, sapphire sensor windows.
  - **Comms and navigation:** UHF link to the mothership, mothership to orbiter relay. Navigation uses IMU, baro,
    radio ranging to the mothership and orbiter, and inter-drone ranging.
  - **Autonomy:** onboard behaviour tree; humans plan days ahead.
  - **Deployment:** ride in the aerobot gondola; release after inflation (~10 min after parachute).
  - **Timeline:** launch, ~4–6 months cruise [Y], entry, 100-day aerobot mission; drones live weeks, and each
    sortie lasts hours.
  - **Science:** cloud-particle sampling (mode-3 particles, phosphine profile), turbulence and wind shear mapping,
    lightning and infrasound.
- **Simulation layer:**
  - inputs: VIRA-like profile, zonal wind 45→100 m/s from 45→60 km, gust model, light vs altitude, acid-exposure
    "damage meter", comms delay, night-side timer;
  - outputs: training scenarios such as "recover a drone in shear", "sample the mode-3 layer before battery
    runs out".
- **Sustainability:**
  - Venus as the **laboratory of the runaway greenhouse**; Landis: understanding Venus helps understand Earth's
    climate [D Landis 2002].
  - **Simulation-first development** cuts hardware test campaigns and travel. This is LuGus's "efficiency and
    sustainability" claim [D gamespress].
  - No nuclear power source; reusable mothership; no debris on the surface.

### P2. "Design a drone mission for the Venus *surface* (or near-surface)"

- **Jury expects:** a team that **confronts 735 K / 92 bar honestly** and does not hand-wave.
- **Key numbers:** ρ ≈ 66 kg/m³; hover power about 8.6× lower than on Earth; induced velocity < 1 m/s; surface
  wind 0.3–1 m/s; about 2 % of sunlight reaches the ground; SiC ICs have lasted 60 days but are simple;
  conventional landers last about 2 h.
- **Strong concept: "DESCENT SPRINTERS"**:
  - A balloon mothership at 55 km drops **5–10 kg autorotating "samara" daughter drones** (VAPS sondes; Young's
    rotary-wing decelerators and MiSSiVE).
  - Each drone descends **unpowered**, autorotating in the dense air. Below 10 km it **powers its rotor briefly**
    (thermal battery or Li-ion in an insulated, phase-change-cooled core, ≤ 1–2 h) to **hover-hop between 2–3 sites**
    (terrain imaging, tessera geology) and lands.
  - On landing it becomes a **SiC weather/seismic station** like LLISSE, possibly with a small wind turbine plus a
    starter motor [D Colozza].
  - **Comms:** VHF/UHF up to the mothership or orbiter.
  - **Materials:** SiC, AlN, 304 SS, Au contacts; no Cu or Ni exposed.
- **Optional fixed-wing alternative:** a high-density glider of Young's lifting-body-autogyro type.
- **Sustainability:** spin-off to **high-temperature electronics for geothermal wells, jet engines and EV power
  electronics**. SiC is a commercial wide-band-gap technology, and Cree invested $1 B in SiC capacity
  [D, link cited in LLISSE slides]. Also **acid- and corrosion-resistant materials**.

### P3. "Build a game, simulation or training scenario: flying drones on Venus with realistic physics"

This could be a GAME challenge, not a spacecraft one. If the brief says "game", "simulation", "player" or
"training", switch to this mode.

- **Jury expects:**
  - correct physics parameters, as in the tables above;
  - **core loop and gameplay mechanics** grounded in real constraints;
  - progression and educational value;
  - a feasible implementation in Liftoff Core / Unity;
  - an accessibility and outreach angle.
- **Strong concept: "Liftoff: Offworld – Venus Cloud Expedition"**:
  - **Biome ladder:**
    - 70 km: thin, cold, bright; easy wing flight.
    - 55 km: Earth-like flight; strong steady wind; acid haze that slowly corrodes props.
    - 48 km: hot, dark, turbulent; very limited time.
    - Surface "hell dive": dense "underwater-like" flight, a heat timer, slow huge rotors, 14,000 lux orange light,
      3 km visibility.
  - **Mechanics:**
    - a **wind-relative frame**: the mothership drifts at about 67 m/s and the player flies relative to the air
      mass;
    - a **light-delay mode** where the player programmes waypoints, 2–14 min apparent latency;
    - **buoyancy tuning** (He vs air vs H₂ envelopes);
    - **solar budget** with bifacial panels;
    - **acid damage**;
    - **thermal budget**.
  - **Missions:** sample the cloud layer; find the "phosphine" plume; rescue a downed drone; map a volcano by radar.
  - **Training value:** supervisory-control training for real operators (NASA Mars analog precedent [D]).
  - **Data:** ship the atmosphere profile as a data file, which suits a modular engine [Y].
- **Sustainability:**
  - **digital-twin testing** replaces physical prototypes;
  - outreach on climate (runaway greenhouse);
  - inclusive STEM education (their Drone Legends school partnership [D]);
  - long-lived software rather than disposable hardware.

### P4. "Design a swarm of drones to map or monitor Venus (atmosphere or surface)"

- **Jury expects:** a reason for a swarm, namely **simultaneous multi-point measurement**, and coordination without
  GNSS.
- **Precedent:** Landis's "fleet of solar-powered airplanes … 'snapshot' of the climate" and formation flight for
  correlation measurements [D Landis 2002].
- **Strong concept:** 1 aerobot mothership plus 6–12 buoyant micro-drones in a 3-D formation spanning 50–62 km and
  tens of km horizontally. The swarm measures wind shear, gravity waves and cloud microphysics at the same moment.
  - **Navigation:** inter-drone radio ranging (UWB-like) plus mothership/orbiter ranging.
  - **Resilience:** the swarm is graceful-degradation by design.
  - A **bistatic radar** option uses one transmitter and several receivers for surface imaging [D Landis 2002:
    "one aircraft transmit while one or more different aircraft receive"].
- **Sustainability:** small, cheap and redundant units (less mass per unit science), plus **Earth spin-offs:
  GNSS-denied swarm navigation** for disaster response and medical drones (BeNeDrone link [D]).

### P5. "Deploy drones from a balloon or entry vehicle: design the deployment and mission architecture"

- **Jury expects:** an end-to-end timeline from launch through cruise, entry, parachute, inflation, release and
  operations, plus failure modes.
- **Key numbers:**
  - aeroshell 1.2–1.3 m (Pioneer Venus small probe) for one airplane [D];
  - inflation in about 10 min [D];
  - airplane release at 65–70 km [D];
  - VAMP flips this and deploys before entry [D];
  - mid-air unfolding is the hardest step [D Young 2026].
- **Strong concept:** a single entry vehicle carrying an aerobot whose gondola holds 4 folded daughter drones. They
  are released one at a time over 100 days, each deployment simulated beforehand in Liftoff Core to tune the release
  sequence.

### P6. "Cloud sample return or life search with drones"

- **Jury expects:** a link to the **Venus Life Finder** logic and an honest treatment of the **phosphine controversy**
  (1–20 ppb, contested [D arXiv]).
- **Strong concept:** a drone collects droplets at 48–60 km and docks with the aerobot. The aerobot rises to about
  70 km, where an ascent vehicle launches (NIAC concept [A]). Planetary protection applies, both ways [Y].
- This is risky in 5 hours. Use it as a "Phase 3 vision" slide rather than the main concept. [Y]

### P7. "VR / visualisation for mission operators or the public"

- Low probability, but LuGus does XR [D].
- **Concept:** an XR operations console that fuses mothership and drone telemetry with a delay-aware "predicted
  state" ghost. It doubles as a public experience, for example at the **Euro Space Center**. That is a Belgian
  outreach venue; I did not research it.

**Hedging strategy for the day [Y]:** prepare P1 as the backbone. It contains the P4 swarm and P5 deployment
elements, and a "surface sprinter" daughter drone from P2. Add a "simulation & training layer" slide that turns into
P3 if the brief is game-like.

---

## 7. What the jury will probe (prepare one-line answers) [Y]

1. *"How does your drone cope with 100 m/s winds?"* It does not fight them. It lives in the air-mass frame, as Vega
   did, and only an airplane at about 100 m/s can station-keep [D VAPS §3.3].
2. *"Why not just a balloon?"* Rotors add local, vertical and lateral authority: sampling a specific plume, dipping
   below the cloud base, recovering. VAPS found most of the science gain comes from **vertical** control [D VAPS
   §4.1.1]. Our drones are the vertical-control extension.
3. *"How do you navigate?"* With baro, IMU, radio ranging to the mothership and orbiter, inter-drone ranging and
   Earth tracking. Not stars, not a compass [D VAPS §5.2].
4. *"How do you survive the acid?"* PTFE/FEP films, Teflon-coated envelope, sealed motors; flight heritage on Vega
   and JPL acid tests at 94 % H₂SO₄ [D].
5. *"Night side?"* There are about 2 Earth days of darkness at the equator [D Landis]. Float passively at neutral
   buoyancy, run minimal electronics, keep drones docked.
6. *"Power at the surface?"* Very little sunlight reaches the ground (about 2 % of incident is absorbed) [A]. Use a
   thermal battery and a turbine for trickle power, and run surface drones as sprints.
7. *"Electronics at 460 °C?"* SiC ICs ran 60 days at 460 °C / 9.3 MPa, but with low complexity [D Neudeck]. Keep
   heavy computing above the clouds.
8. *"Is this feasible this decade?"* The JPL aerobot reached TRL 5 evaluation (2023 target), drones are small
   add-ons, and EnVision and DAVINCI provide context and relay opportunities. **Check the slip claims before quoting
   any date.**
9. *"Sustainability?"* Climate science, simulation-first development, SiC and acid-resistant spin-offs, no
   radioisotopes, low mass.
10. *"What would LuGus build?"* An Offworld Venus biome, an operator trainer, and a public outreach module, all from
    one environment data file.

---

## 8. Five-hour sprint plan (suggestion) [Y]

| Time | Activity | Output |
|---|---|---|
| 0:00–0:20 | Read the brief; classify it as P1–P7; agree a one-sentence claim | Problem statement + success criteria |
| 0:20–1:00 | Pick the altitude band and architecture (mothership + drones?) and fill the numbers from §3–§5 | Requirements table |
| 1:00–2:30 | Vehicle sizing (buoyancy, rotor, power, thermal), CONOPS timeline, comms/navigation, materials | 1 config sketch, 1 mass/power table, 1 timeline |
| 2:30–3:15 | Simulation/training layer (parameters, scenarios) and sustainability | 2 slides |
| 3:15–4:30 | Build slides (~10–12): title, problem, environment, concept, numbers, CONOPS, simulation, sustainability, risks/TRL, roadmap, ask | Deck |
| 4:30–5:00 | Rehearse twice; Q&A drill from §7 | Pitch |

---

## 9. What I could not verify or find (explicit)

1. **The spoiler itself.** No public page shows "LuGus Studios: Drones on Venus", the 2026 sponsor list, judging
   criteria or the challenge length. It is not on https://ideathon.euroavia.eu/, not on /countdown/, and not in the
   local welcome PDF. The 2024 brochure PDF was not text-readable through the fetch tool.
2. **LuGus ↔ Venus, ESA, EUROAVIA or Belgian space companies:** none found. The only ESA touchpoint is astronaut
   Vittori testing the Mars sim.
3. **Liftoff physics internals** (how Mars gravity and density were modelled; whether the engine supports variable
   ρ, g, wind fields or buoyancy): not published in what I read.
4. **Liftoff: Offworld release status:** no release found after June 2023.
5. **Red Cat acquisition outcome:** LOI only; closure not found.
6. **Original VIRA (Seiff et al. 1985) tables:** not obtained. The profile here comes from Wikipedia's table plus my
   ideal-gas densities. The NASA NSSDC Venus fact sheet timed out three times, and SPENVIS returned 503.
7. **CO₂ viscosity values:** my own assumptions, not verified.
8. **Surface solar flux numbers** (17 W/m², 2.5 %): search snippets only.
9. **Mission statuses:** EnVision Nov 2031 is [D] from ESA's factsheet; the slip to 2032 and NASA exit are [A].
   DAVINCI and VERITAS dates are [A]. Rocket Lab VLF launch is unscheduled [A]. Dragonfly July 2028 is [A].
10. **VAMP mass and wingspan; HAVOC airship size:** not found in primary sources.
11. **Turbulence intensity in the cloud layer:** no quantitative source found.
12. **Venus rotorcraft hover experiments:** none found. Venus helicopter work is conceptual (Young 2026; Russian
    papers [A]).

## 10. Source list (primary first)

- LuGus Studios site: https://www.lugus-studios.be/ (pages: projects, how-we-work, team, latest-news,
  portfolio/mars-drone-simulator, portfolio/interreg-benedrone-project, portfolio/liftoff-xr-drone,
  portfolio/cosmiclean) [D]
- Liftoff site: https://www.liftoff-game.com/node/215 (Offworld reveal), /node/221 (Simulating NASA missions),
  /node/15 (Liftoff Core/Academy), /node/111 (Skypersonic sim), /news/community-questions-answered [D]
- Belgian Game Awards studio page: https://awards.belgiangames.be/studio/lugus-studios/ [D]; BGA 2025 winners
  press release: https://www.gamespress.com/The-winners-of-the-Belgian-Game-Awards-2025-have-been-announced [D]
- Red Cat LOI press release (5 May 2021):
  https://ir.redcatholdings.com/news-events/press-releases/detail/22/red-cat-holdings-signs-letter-of-intent-to-acquire-lugus-studios [D]
- Steam Liftoff page: https://store.steampowered.com/app/410340/Liftoff_FPV_Drone_Racing/ [D]
- EUROAVIA Ideathon: https://ideathon.euroavia.eu/ [D]; local `EUROAVIA Ideathon 2026.pdf` [D]
- Landis 2001 STAIF, "Exploring Venus by Solar Airplane": https://ntrs.nasa.gov/citations/20020022923 [D]
- Landis, LaMarre, Colozza 2002 IAC, "Venus Atmospheric Exploration by Solar Aircraft":
  https://ntrs.nasa.gov/citations/20030022791 [D]
- Venus Aerial Platforms Study, Summary Report, JPL D-102569 (Oct 2018):
  https://solarsystem.nasa.gov/system/downloadable_items/2693_Venus_Aerial_Platforms_Final_Report_Summary_Report_10_25_2018.pdf [D]
- JPL aerobot news (10 Oct 2022):
  https://www.jpl.nasa.gov/news/jpls-venus-aerial-robotic-balloon-prototype-aces-test-flights [D]; JPL aerobot
  poster: https://smd-cms.nasa.gov/wp-content/uploads/2023/11/goel-aerobot.pdf [D]
- Young, Dominguez, Schatzman 2026, "Past, Present, and Future Conceptual Designs for Venus Aerial Explorers":
  https://rotorcraft.arc.nasa.gov/Publications/files/Venus%20Aerial%20Explorers_Paper_v6C.pdf [D]
- Sen et al. 2015, VAMP, EPSC2015-873: https://meetingorganizer.copernicus.org/EPSC2015/EPSC2015-873.pdf [D]
- Arney & Jones 2015, HAVOC: https://ntrs.nasa.gov/citations/20160006329 [D]; https://www.nasa.gov/general/havoc/ [D]
- Kremic et al. 2019, Long Duration Venus Probes and Landers (LLISSE):
  https://ntrs.nasa.gov/api/citations/20190029198/downloads/20190029198.pdf [D]
- Neudeck 2024, SiC ASICs: https://ntrs.nasa.gov/citations/20240013278 [D]
- Colozza 2024/25, Venus VAWT: https://ntrs.nasa.gov/citations/20240000076 [D]
- Greaves et al. 2021, "Re-analysis of Phosphine in Venus' Clouds": https://arxiv.org/abs/2011.08176v2 [D]
- ESA EnVision factsheet: https://www.esa.int/Science_Exploration/Space_Science/EnVision_factsheet [D]
- NASA Ingenuity: https://science.nasa.gov/mission/mars-2020-perseverance/ingenuity-mars-helicopter/ [D]
- Planetary Society, Rocket Lab VLF: https://www.planetary.org/space-missions/rocket-lab-venus-mission [D]
- Tomasko, Doose & Smith 1979, Science 205:80: https://experts.arizona.edu/en/publications/absorption-of-sunlight-in-the-atmosphere-of-venus/ [D abstract]
- Wikipedia (secondary): https://en.wikipedia.org/wiki/Venus, https://en.wikipedia.org/wiki/Atmosphere_of_Venus,
  https://en.wikipedia.org/wiki/Vega_program [D, secondary]
- Search-only [A]: SPENVIS VIRA summary; Tomasko 1980 17 W/m²; DAVINCI/VERITAS status (payloadspace, space.com);
  EnVision slip (Wikipedia/hwbusters); Dragonfly (Wikipedia, NASA statements); VLF status (space.com); Red Cat 10-K
  excerpts; Skypersonic/NASA CHAPEA (dronedj, executivebiz, geospatialworld); stopped-rotor cyclocopter (NTRS
  20160012563); Russian multirotor papers; Liftoff Unity 2018.4 (gamingonlinux).
