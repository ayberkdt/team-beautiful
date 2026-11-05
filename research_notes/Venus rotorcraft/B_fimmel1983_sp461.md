# B_fimmel1983_sp461 — Fimmel, Colin & Burgess, *Pioneer Venus* (NASA SP-461)

## Citation
Fimmel, R. O., Colin, L., & Burgess, E. (1983). *Pioneer Venus*. NASA SP-461, NASA Scientific and Technical Information Branch, Washington DC. NTRS 19830022069.
URL: https://ntrs.nasa.gov/citations/19830022069 (PDF: https://ntrs.nasa.gov/api/citations/19830022069/downloads/19830022069.pdf, 35.5 MB, 257 PDF pages; downloaded 2026-11-04).

## What I read
Full text (OCR layer extracted with pypdf) of: ch. 2 parachute development story (printed p. 28–29, PDF p. 40–41); ch. 3 probe descriptions "The Large Probe" / "The Small Probes" (printed p. 49–53, PDF p. 60–64, incl. Fig. 3-17/3-19/3-21 captions); ch. 5 encounter narrative and **Table 5-2 "Important entry events"** (printed p. ~100–101, PDF p. 111–113).
OCR of Table 5-2 is partly garbled (column headers). Printed page numbers are approximate where the OCR lost them.

## Numbers — all [D-ag] (read in this PDF)

### Large Probe
- Mass "about 315 kg (695 lb)", diameter "about 1.5 m (5 ft)" (p. 49). (Siddiqi gives 316.5 kg.)
- Aeroshell: **45° blunt cone**, hemispherical nose, one-piece **aluminum** with machined rings; forward heat shield **carbon phenolic** ablator; other aeroshell surfaces and aft cover a low-density elastomeric coating; aft cover fiberglass honeycomb (p. 49, 51).
- Titanium pressure vessel **73.2 cm** diameter, 3 bolted pieces, N2 fill at 102 kPa; 2.5 cm multilayer Kapton blanket inside; beryllium shelves as heat sinks (p. 50).
- Peak deceleration **280 g** "soon after entry" (p. 51).
- Parachute sequence (p. 51, Fig. 3-19): pilot chute **mortar-fired** from aeroshell side compartment → pulls aft cover (released by explosive bolt) → aft cover pulls main chute from compartment in conical aeroshell → once stable, ties to aeroshell severed (explosive nuts / cable cutters) → main chute pulls pressure vessel out of aeroshell.
- "The heat shield was jettisoned about **67 km** ... About **47 km** ... the parachute was released"; surface reached ~**55 min** after entry; spin vanes < 1 rpm (p. 51).
- Entry: decelerated from **41,800 to 727 km/h (≈11.6 km/s → 202 m/s) within 38 s** (p. 100). Instruments running 43 s after entry at ~66 km.
- Table 5-2: time on parachute **17:07 (min:s)**; descent time entry (200 km) to impact **54:21**; impact speed "only **32 km/hr**" (≈8.9 m/s); main chute jettison 11:03:28 PST spacecraft time; no surface operations.
- Telemetry 256 bit/s direct to Earth, 40 W S-band (4 × 10 W); 40 A·h Ag-Zn battery; 3072-bit blackout memory (p. 51–52).
- Main parachute design history (p. 28–29): first design (gores failed to open, shredded in F-4 drop tests at El Centro and Ames 40×80 ft tunnel) abandoned for an **earlier conical-ribbon design**; system balloon-drop test Dec 1976 at White Sands from 31 km, chute deploy planned at 16 km, failed (probe tumbled, deployed tail-first at 18 km, clevises broke); second drop succeeded. Design intent: 17 min chute descent then free fall. **No canopy diameter given** in the parts I read.

### Small Probes (North, Day, Night) — identical
- Each "0.8 m (30 in.) in diameter and weighed **90 kg** (200 lb)" (p. 53). (Siddiqi: 76 cm.)
- No parachute; heat shield + afterbody stay attached to surface; same **45° blunt cone**, aeroshell **titanium** monocoque (because it must survive to the surface), bonded **carbon phenolic** heat shield; interior **xenon** fill (~21% of air's conductivity) (p. 53, p. 100).
- Spin reduced from ~48 rpm to 17 rpm ~5 min before entry by yo-yo weights on 2.4 m cables (p. 53).
- All probes entered at about **42,000 km/h (≈11.7 km/s)** at 200 km altitude (p. 53, p. 100).
- Peak deceleration: steepest-entry probe **458 g**; shallowest **~223 g** (p. 53). Radio blackout ~10 s.
- Afterbody doors open ~70 km.
- Table 5-2 descent times (entry to impact): 53:00(?), 55:41, 55:52 min:s (OCR of the North value uncertain). The Day Probe survived impact: surface operations **67:37**; one other probe ~2 s.

## Derived (my arithmetic, not in source) — tag [calc]
- Large probe m/A = 315 / (π·0.75²) = 178 kg/m². Small probe m/A = 90 / (π·0.4²) = 179 kg/m². Ballistic coefficient β = m/(C_D A) needs C_D, which this source does not give; for a 45° sphere-cone hypersonic C_D ≈ 1.0–1.1 is a general textbook value (NOT verified here), giving β ≈ 160–180 kg/m².
- Average deceleration in the 38 s pulse: (11,610 − 202)/38 ≈ 300 m/s² ≈ 31 g mean (peak 280 g is far higher — pulse is short and peaked).

## Caveats
- No flight-path angles given in the parts read (only "steepest/shallowest" entries). See B_seiff1980 for angles.
- Table 5-2 column headers are OCR-garbled; Day Probe identification is from the 67:37 surface time (matches Siddiqi).
- Cross-check [A]: NASA PDS Atmospheres Node page "Special Venus events" (https://atmos.nmsu.edu/data_and_services/atmospheres_data/PIONEER_Venus/special_venus_events.html, read via fetch summary) lists entry (200 km) / impact UT for Large 18:45:32/19:39:53, North 18:49:40/19:42:40, Day 18:52:18/19:47:59, Night 18:56:13/19:52:05 → descent 54:21, 53:00, 55:41, 55:52 (column order Large, North, Day, Night confirmed); masses bus 290 kg, large 315 kg, small 90 kg each.

## Quote
"abandoned in favor of an earlier conical ribbon design" (p. 29).
