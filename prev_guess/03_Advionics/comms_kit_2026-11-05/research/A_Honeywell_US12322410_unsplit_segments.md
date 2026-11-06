# A_Honeywell_US12322410_unsplit_segments — Honeywell: handling unsplit segments in cockpit ATC transcription

## Citation
Agarwal, J. K. — Honeywell International Inc. "System and method for handling unsplit segments in transcription of air traffic communication (ATC)." US 12322410 B2. Priority 29 Apr 2022 (IN 202211025236); filed 13 Jun 2022; published 3 Jun 2025.
URL: https://patents.google.com/patent/US12322410B2/en

Date read: 2026-11-04. Read via WebFetch (model summary of the first 100 000 of 126 975 characters). [D-ag, via fetch summary]

## Content and numbers
- Problem: VAD merges controller and pilot turns because inter-speaker pauses are short. The patent says "almost 10-30 percent of unsplit segments are observed" in a flight.
- Pauses of 10–30 ms accumulate to ~120–150 ms. Pauses under ~20 ms are "significantly shorter" than normal ~30–40 ms. These are patent statements, not data from a measured study.
- Fix: re-decode with a split predictor that looks for repeated callsigns or critical phrases, so each instruction appears as its own message on the pilot display.
- No accuracy figures.

## Failure mode
Segmentation (VAD) errors merge messages, so a clearance for another aircraft can end up inside a message attributed to own ship.

## Relevance to us [Y]
- The 10–30% unsplit-segment claim is a concrete failure rate to design for. Split per callsign before parsing, and show one card per instruction.
- In the cockpit, own PTT gives a hard boundary for own transmissions. Only the receive side needs this splitter.
