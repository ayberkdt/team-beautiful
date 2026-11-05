# R_asr_wiki — Wikipedia, "Airport surveillance radar"

## Citation
Wikipedia contributors, "Airport surveillance radar", English Wikipedia, last edit 03:07, 12 April 2026 (from the page history). URL: https://en.wikipedia.org/wiki/Airport_surveillance_radar (raw wikitext read).
Date read: 2026-11-04. Source class: SECONDARY. It cites FAA "Airport Surveillance Radar" pages and radartutorial.eu.
Labels: [D-ag] read this session.

## Facts [D-ag]
- Intro: at large airports an ASR typically covers "a radius of 60 miles (96 km)" below 25,000 ft. Types section: "All ASRs have the common requirements of detecting aircraft out to a range of 60 miles and an elevation of 25,000 feet."
- Primary radar section (US): 2.7–2.9 GHz, S band, 25 kW peak and 2.1 kW average radiated power. The beam is about 1° wide and fan-shaped. It scans the airspace "about every 5 seconds".
- Secondary radar section: 1030 MHz interrogation at 160–1500 W peak; replies on 1090 MHz.
- **ASR-9** (Westinghouse, first installed 1989, at 135 locations): klystron, S-band 2.5–2.9 GHz (as stated), circular polarisation, 1.3 MW peak, 1 μs pulse, PRF 325–1200 pps. It detects 1 m² RCS at 111 km, with 450 ft range resolution. It has two stacked beams 4° apart (lower Tx/Rx, upper receive-only for nearby high targets). Antenna gain 34 dB; beamwidth 5° in elevation and 1.4° in azimuth. It rotates at **12.5 RPM, i.e. 4.8 s per scan**. It uses a digital MTD processor (Doppler plus clutter map) and is "theoretically capable of tracking a maximum of 700 aircraft".
- ASR-8: analog, 60 NM, two frequencies at least 60 MHz apart.
- ASR-11 / DASR: the fully digital successor (this section was not read in full).

## Relevance to us [Y]
This supports the "terminal radar = S-band, ~60 NM, ~4.8 s update" parameter set for our approach-area sensor model. Pair it with R_faa_order_1812_8_arsr4.md (en route: L-band, 250 NM, 12 s) for the contrast slide. Secondary source: before quoting ASR-9 numbers to the sponsor, check them against the FAA or radartutorial.
