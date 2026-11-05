# R_eurocontrol_modeS_IC — EUROCONTROL, "Principles of Mode S Operation and Interrogator Codes"

## Citation
EUROCONTROL (EATMP), *Principles of Mode S Operation and Interrogator Codes*, Edition 2.3, 18/03/2003, status "Draft", intended for the general public. Contact: Scott Kelly, Surveillance. 35 PDF pages.
URL: https://www.eurocontrol.int/sites/default/files/publication/files/surveillance-modes-principles-of-modes-operation-and-interrogator-codes-20030318.pdf
Date read: 2026-11-04. Read method: PDF streamed and text-extracted with PyMuPDF, then key passages read by the agent. Page numbers below are PDF page indices.
Source class: PRIMARY (EUROCONTROL guidance material), but a 2003 draft. It cites ICAO Annex 10 for the numbers.
Labels: [D-ag] read this session.

## Facts
- p5 [D-ag]: The ICAO aircraft address is 24 bits, so "16,777,216 possible codes". It is allocated by the State of registry from a block per State. Military may change the address before a flight. Badly programmed addresses occur.
- p7–p8 [D-ag]: Acquisition and lockout. A target acquired in the all-call period is then interrogated selectively in the roll-call period. Lockout means the target does not reply to all-calls with that IC "for a period of 18 seconds". The sensor normally refreshes the lockout timer with every selective interrogation.
- p9 / p18 [D-ag]: Stochastic acquisition. All-calls can carry a reply probability of "1, ½, ¼, 1/8 or 1/16" (the fraction glyphs were partly garbled in extraction; 1 and 1/8, 1/16 legible). This separates closely spaced targets.
- p11–p12 [D-ag]: Intermittent lockout pattern (Figure 5): "Lockout Active (18s)" alternating with "No Lockout (10s)". The 10 s figure is called a recommended period.
- p16 [D-ag]: Uplink pulses are P1–P6 (ICAO Annex 10). P4 short (P4S) = 0.8 μs, which makes Mode S aircraft not reply. P4 long (P4L) = 1.6 μs, which brings Mode A/C replies from A/C transponders and Mode S-only all-call replies from Mode S.
- p19 [D-ag]: There are 16 II-Codes, 15 of them allowing multisite operation, plus 63 SI-Codes that work like II-Codes for lockout.
- p20 [D-ag]: II-Code = 0 is the special "non-selective" code.
- p16 (approx.) [D-ag]: SI-Code sensors fully support the ELS and EHS protocols.

## Relevance to us [Y]
Useful if the sponsor (radar/SSR experts) asks how a Mode S radar acquires and keeps a target: all-call → lockout (18 s) → roll-call, with IC codes (II 0–15, SI 1–63). It explains why a passive receiver hears DF11 replies with II/SI overlaid in the PI field (see R_1090_riddle T14, where II = 22 suggests an SI code, since it is >15; agent inference, not stated in the source).
