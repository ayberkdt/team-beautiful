# R_mlat_wiki — Wikipedia, "Pseudo-range multilateration"

## Citation
Wikipedia contributors, "Pseudo-range multilateration", English Wikipedia, last edit 22:39, 9 July 2026. URL: https://en.wikipedia.org/wiki/Pseudo-range_multilateration (raw wikitext read; "Multilateration" redirects to "Trilateration", so this is the relevant article).
Date read: 2026-11-04. Source class: SECONDARY; banner "Lead too long" (2022). Only the lead and the DOP section were read.
Labels: [D-ag] read this session.

## Facts [D-ag]
- TOF = TOA − TOT; pseudo-range PR = TOF·s. The station clocks are synchronised; the vehicle's clock is not.
- In **surveillance MLAT** the vehicle transmits and the stations receive: there is one unknown TOT and several known TOAs. In navigation (hyperbolic navigation) the stations transmit.
- With d dimensions and m measurements, m ≥ d + 1 is required. Either solve for TOT plus d coordinates, or form m − 1 TDOAs (at least d) and solve for the coordinates. TDOA systems are "hyperbolic" systems.
- Geometry: a DOP analysis drives the number and placement of stations. HDOP is the sensitivity of the horizontal solution to TOA errors. GDOP relates to the Cramér–Rao bound (cites Chaffee & Abel 1994).

## Derived note [C-ag], not from the source
For 3-D surveillance from 1090 MHz replies: d = 3 gives at least 4 receivers. If Mode C/S altitude is used as a constraint (d = 2 horizontal), 3 receivers suffice. Range-error scale: c × 1 ns ≈ 0.3 m per receiver timing error before GDOP. Both are standard textbook relations, not quoted from this article.

## Relevance to us [Y]
Background for an MLAT slide (TDOA hyperbolae, receiver count, GDOP-driven siting). Pair it with R_icao_suricg7_ip14_wam.md for real accuracy figures. The ED-142 / ED-117 normative numbers could NOT be read (paywalled EUROCAE); state this gap on the slide.
