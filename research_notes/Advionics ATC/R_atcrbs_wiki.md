# R_atcrbs_wiki — Wikipedia, "Air traffic control radar beacon system"

## Citation
Wikipedia contributors, "Air traffic control radar beacon system", English Wikipedia, last edit 22:08, 2 September 2026 (from the page history).
URL: https://en.wikipedia.org/wiki/Air_traffic_control_radar_beacon_system (raw wikitext read).
Date read: 2026-11-04. Source class: SECONDARY. Parts of the SLS section carry a "Cleanup section: unreferenced material added in 2006" banner.
Labels: [D-ag] = read in the article this session.

## Facts

### Theory of operation [D-ag]
- Interrogation is on 1030 MHz. Interrogations "typically" run at "450 - 500 interrogations/second".
- The transponder replies on 1090 MHz "after a 3.0 μs delay".
- Old sliding-window azimuth = the centre of the first and last reply azimuths. This causes "track jitter", which is why monopulse was introduced.
- PSR signal falls with the 4th power of range; transponder (SSR) signal with the square.

### The interrogation [D-ag]
- P1, P2 and P3 are each 0.8 μs. Mode 3/A uses P1–P3 = 8.0 μs; Mode C 21 μs; Mode 2 5 μs (military).

### The reply [D-ag]
- "15 time slots, each 1.45 μs in width". Information is carried by the presence or absence of a 0.45 μs pulse in each slot.
- Slot order, verbatim: **`F1 C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4 F2   SPI`**
- F1–F2 spacing: "These are spaced 20.3 μs apart."
- Mode A: 4 octal digits, each sent as 3 pulses (A4A2A1, B4B2B1, C4C2C1, D4D2D1).
- Mode C: Gillham code (Gray), 100 ft increments, pressure altitude. If no encoder is fitted, the transponder may send framing pulses only.
- The X bit is only used for test targets (historically BOMARC; possibly drones).
- SPI: "positioned 4.35μs past the F2 pulse (3 time slots)". Ident adds SPI for "about 20 seconds", which the article puts at two to four antenna rotations.

### Side-lobe suppression [D-ag]
- Classic SLS: P2 is 2 μs after P1, sent from the omni antenna (or difference channel). It is calibrated to arrive stronger than P1 and P3 except when the main beam points at the aircraft.
- Quoted TSO-C74c §2.6c (cleanup-flagged section): suppression lasts "35 ±10 microseconds". It must be 99 % efficient between 3 dB and 50 dB above MTL, when P2 ≥ P1 and the pulses are spaced "2.0 ±0.15 microsecond".

### Radar display [D-ag]
- A flight data processor (FDP) links the beacon code to the flight plan. The data block shows callsign, next fix, assigned and current altitude, etc. "ATCRBS does not display aircraft heading."

## Derived [C-ag], not from the source
15 slots × 1.45 μs: F1 is at slot 0 and F2 at slot 14, so 14 × 1.45 = 20.3 μs. This matches the stated F1–F2 spacing. SPI sits 3 slots after F2, at 3 × 1.45 = 4.35 μs, also consistent.

## Relevance to us [Y]
This is the pulse-level timing for a Mode A/C reply decoder or simulator (slot pitch, framing, SPI). The bit order F1 C1 A1 … D4 F2 SPI is the same order the task's Gillham decoding assumes. Being secondary, it should be cited with "per ICAO Annex 10 Vol IV" only once Annex 10 has been read, which this agent did not do (Annex 10 is paywalled).
