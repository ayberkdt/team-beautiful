# C_ingenuity_jpl — Ingenuity actual flight record (NASA/JPL official pages)

## Sources
1. NASA Science, *Ingenuity Mars Helicopter* mission page. https://science.nasa.gov/mission/mars-2020-perseverance/ingenuity-mars-helicopter/ (accessed 2026-11-04)
2. NASA JPL news, *After Three Years on Mars, NASA's Ingenuity Helicopter Mission Ends*, 25 Jan 2024. https://www.jpl.nasa.gov/news/after-three-years-on-mars-nasas-ingenuity-helicopter-mission-ends/ (accessed 2026-11-04)
3. Grip, H. F., NASA blog *Flying on Mars Is Getting Harder and Harder*, Sept 2021. https://science.nasa.gov/blog/flying-on-mars-is-getting-harder-and-harder (accessed 2026-11-04)
4. Secondary (not NASA): Digital Trends flight-log summary, found only as a search snippet → values tagged [A].

## What was read
Pages 1-3 fetched with WebFetch. The text was extracted by the fetch tool, and the quoted phrases below are the ones it returned from the page. I did not view the pages' graphics (e.g. the flight-log infographic) myself. Tag [D-ag] here means "official NASA page text, via fetch-tool extraction". Source 4 was seen only in a search summary.

## Numbers
| Quantity | Value | Source | Tag |
|---|---|---|---|
| Mass | 1.8 kg ("3.97 pounds (1.8 kilograms)") | 1 | [D-ag] |
| Rotor span | ~1.2 m tip to tip | 1 | [D-ag] |
| Average flight power | "approximately 350 Watts of average power during flight" | 1 | [D-ag] |
| Design flight | one 90 s flight per sol, recharged by solar panel; range up to 300 m, altitude up to 5 m | 1 | [D-ag] |
| Flights flown | **72** (plan: up to 5 in 30 days) | 1, 2 | [D-ag] |
| Total flight time | **128.8 min** ("more than two hours" in source 2) | 1, 2 | [D-ag] |
| Total distance | **17.0 km** (10.5 mi); "more than 14 times farther than planned" | 1, 2 | [D-ag] |
| Max altitude | **24.0 m** (78.7 ft) | 1 | [D-ag] |
| Max ground speed | **10 m/s** (22.4 mph), from the flight-log graphic caption | 1 | [D-ag] (graphic caption, via fetch) |
| Airfields | 48 different airfields; 3 emergency landings | 2 | [D-ag] |
| Mission dates | landed 18 Feb 2021; first flight 19 Apr 2021; last flight (72) 18 Jan 2024; end announced 25 Jan 2024 | 1, 2 | [D-ag] |
| End of mission | one or more rotor blades damaged during landing of flight 72 (12 m max altitude, 4.5 s hover, 1 m/s descent, contact lost ~1 m above surface) | 2 | [D-ag] |
| Operating time on Mars | almost 1,000 sols, "more than 33 times longer than originally planned" | 2 | [D-ag] |
| Design density range | **0.0145-0.0185 kg/m³** (1.2-1.5 % Earth SL) | 3 | [D-ag] |
| Thrust margin | ≥ **30 %** at 0.0145 kg/m³; would fall to ~**8 %** at 0.012 kg/m³ (near stall) | 3 | [D-ag] |
| Rotor speed history | flights up to 2,537 rpm; 2,800 rpm ground spin; first 2,700 rpm flight = Flight 14 (Oct 2021) | 3 (+ search snippet for the date) | [D-ag] (date [A]) |
| Tip Mach | "nearly 0.8 Mach" at blade tips at 2,800 rpm, including wind and vehicle motion | 3 | [D-ag] |
| Speed of sound on Mars | "about ¾" of Earth's | 3 | [D-ag] |
| Longest single flight | 705 m (flight 69) | 4 | [A] |
| Longest airtime | 169.5 s (flight 12) | 4 | [A] |
| 24 m altitude | was a hover-only test (flight 61) | 4 | [A] |

## Deployment from the rover (for comparison with mid-air release) [A]
Source: search-result summaries of NASA/JPL news (science.nasa.gov item, space.com, spaceexplored.com, March 2021). I did not open a NASA page.
- Debris shield dropped on 21 Mar 2021 (sol 30). Ingenuity then rotated down out of the rover belly over a multi-sol sequence: bolt-breaking device, unfold, legs deploy. Sources say "six-sol" or "10 sols" (they disagree).
- In the final position it hung ~**13 cm (5 in)** above the surface on one bolt and a few dozen contacts. Its six cells were charged from the rover until the final sol. Then it was dropped 13 cm and the rover drove away so the solar panel could charge.
- Contrast with C_delaune2022_mahd (mid-air, 600 m AGL separation, jetpack) and C_balaram2018 (designed passive drop ≤ 0.3 m at landing).

## Lessons for a Venus rotorcraft (my inferences, not from the sources)
- Ingenuity's real envelope (10 m/s, 24 m, 72 flights, ~2.5 h total) is a demonstrated benchmark for autonomous planetary rotorcraft GNC: IMU + laser altimeter + downward visual velocimetry (C_balaram2018, C_grip2018).
- Ingenuity had to raise rpm as density dropped, to keep thrust margin above 8-30 %. A Venus aerial vehicle at 50-60 km faces density changing with altitude (~0.5-1.6 kg/m³), so the same rpm/collective margin logic applies, but tip Mach is far less constraining in dense CO2. The speed of sound in CO2 at ~300 K is ~270 m/s; I estimated this and did not verify it in a source.
