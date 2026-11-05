# R_ssr_wiki — Wikipedia, "Secondary surveillance radar"

## Citation
Wikipedia contributors, "Secondary surveillance radar", English Wikipedia. Revision current at read time: last edit 00:52, 5 October 2026 (from the page history).
URL: https://en.wikipedia.org/wiki/Secondary_surveillance_radar (read as raw wikitext via `?action=raw`).
Date read: 2026-11-04. Source class: SECONDARY (encyclopedia). The article cites ICAO Annex 10 Vol IV, ICAO Circular 174-AN/110, Stevens (Artech House), and Lincoln Lab ATC-42 and ATC-65. The article carries "more citations needed" (2007) and "MOS" (2025) banners.
Labels: [D-ag] = read in the article this session.

## Facts (section names as in the article)

### Overview / Standards [D-ag]
- ICAO chose 1030.0 MHz for interrogation and 1090.0 MHz for reply, so SSR could coexist with DME (960–1215 MHz).
- SSR Mode A, C and S are compatible with IFF Mode 3/A, C and S. Mode B and D are no longer in Annex 10.
- Mode S was standardised by ICAO in 1987 (Annex 10 Vol I, Amendment 67). It uses a 24-bit address per aircraft.
- Annex 10 Vol IV covers SSR operation and signals in space. Vol III Part 1 covers the Mode S data link.

### Interrogation modes (table) [D-ag]
| Mode | P1–P3 spacing | Purpose |
|---|---|---|
| A | 8 μs | Identity |
| B | 17 μs | Identity |
| C | 21 μs | Altitude |
| D | 25 μs | Undefined |
| S | 3.5 μs | Multipurpose |
- A Mode A reply has 12 data pulses between framing pulses F1 and F2; the X pulse is unused. A Mode C reply uses 11 pulses (no D1) and gives altitude in 100 ft steps.
- SLS: P2 comes from a second, mostly omnidirectional beam, "2 μs after P1". A transponder that sees P2 stronger than P1 does not reply.
- The Mode S interrogation is P1 and P2 in the main beam (so Mode A/C transponders treat it as a side lobe), then a long phase-modulated P6.

### Deficiencies (cites ICAO Circular 174-AN/110, 1983) [D-ag]
- Mode A: 4,096 codes. Some are reserved, so fewer are usable. Code/callsign conversion needs codes to be unique.
- Mode C: 100 ft increments.
- FRUIT: "False Replies Unsynchronized with Interrogator Transmissions", or "False Replies Unsynchronized In Time". These are replies to other ground stations on the shared 1090 MHz.
- Garble: FRUIT overlapping a wanted reply. Raising the interrogation rate is self-defeating.
- Synchronous garble: aircraft "within about two miles slant range" of each other give overlapping replies.
- Capture: a Mode A/C reply can occupy the transponder for "up to 120 μs".
- ICAO limits the interrogation repetition frequency (IRF) to ≤450 Hz (cites ICAO Doc 9684, 1997). In the 1990s, "≥ 70 active interrogator" were measured at 10,000 ft in the Frankfurt FIR.
- Early sliding-window azimuth estimation used the first and last replies. Hogtrough antennas ran from 1.9° to 6.0° azimuth beamwidth (Telefunken table).
- The LVA antenna has a cosec² elevation pattern, and a 5 ft vertical dimension became the international standard.

### Monopulse SSR comparison table (cites Stevens 1990) [D-ag]
| | Standard SSR | Monopulse SSR | Mode S |
|---|---|---|---|
| Replies per scan | 20–30 | 4–8 | 1 |
| Range accuracy | 230 m rms | 13 m rms | 7 m rms |
| Bearing accuracy | 0.08° rms | 0.04° rms | 0.04° rms |
| Height resolution | 100 ft | 100 ft | 25 ft |
| Data capacity (downlink) | 23 bits | 23 bits | 56–1,280 bits |
| Identity permutations | 4,096 | 4,096 | 16 million |
- According to the article (citing FAA 2004), MSSR accuracy let en-route separation drop from 10 NM to 5 NM.

### Mode S [D-ag]
- Mode S interrogation: two 0.8 μs pulses, then P6 with DPSK. The first phase reversal comes at 1.25 μs. Short P6 = 16.125 μs; long P6 = 30.25 μs.
- Reply: 4-pulse preamble, then PPM in 1 μs bit intervals (0.5 μs pulse in the first half = 1). The last 24 bits are address/parity. The parity can correct errors that span up to 24 μs (the length of a Mode A/C reply).
- All-call comes in two forms: the Mode A/C/S all-call (P4) and the Mode S-only all-call (UF11).
- UF used: 0, 4, 5, 11, 16, 20, 21, 24. DF used: 0, 4, 5, 11, 16, 17 (ES), 18 (TIS-B), 19 (military ES), 20, 21, 22 (military), 24.
- Comm-B: 256 registers of 56 bits. BDS 4,0 = selected vertical intent; 5,0 = roll, track rate, true track, GS; 6,0 = magnetic heading, IAS, Mach, vertical rate.
- Extended squitter versions 0, 1 and 2 are in ICAO Doc 9871 (Ed. 1 2008, Ed. 2 2012).

## Not in this article (checked)
The article text does not give the 20.3 μs F1–F2 spacing, the 1.45 μs pitch or the SPI position; those exist only in figures. They are taken from R_atcrbs_wiki.md and R_1090_riddle.md.

## Relevance to us [Y]
This backs the slide on SSR basics (frequencies, mode spacings, SLS, FRUIT/garble) and the accuracy comparison between SSR, MSSR and Mode S (230 / 13 / 7 m rms). It is a secondary source, so the slides should cite it as "Wikipedia, citing Stevens 1990 / ICAO Cir 174".
