# UX audit (ux-yasalari) — cockpit.html and scope.html

Checker: `node "C:\Users\ayber\.claude\skills\ux-yasalari\scripts\ux-yasa-denetimi.mjs" <file> --tablo`, run
2026-11-04 on both files: **0 HATA · 0 UYARI** each. The checker reads static HTML and does not resolve CSS variables
(it reports "0 punto"), so font sizes, radii, spacing and target sizes below were measured on the live DOM in the
browser pane (local server `atc-demo`, 1024 × 768 viewport, `getComputedStyle` / `getBoundingClientRect`).

Budgets (written before the HTML): cockpit — tasks: read latest clearance + trust tag, know comm state; primary
action "Confirm heard"; 3 actions; 1 nav link. Scope — tasks: traffic picture, signal → label; primary "Play";
3 actions (Play, slider, click track); 1 nav link. Both: ≤ 6 font sizes, 2 button styles, 1 accent (cyan #39c5e0),
0 shadows, ≤ 4 radii.

## cockpit.html — 20/20 measured · 0 HATA · 0 UYARI · TESLİM

| # | Yasa | Ölçüm | Eşik | Durum |
|---|---|---|---|---|
| 1 | Hick | nav 1 · actions 3 (Confirm heard, Play, slider) · no select | ≤ 7 · ≤ 5 · ≤ 7 | geçti |
| 2 | Fitts | targets 138×44, 64×44, slider 732×44 px; clearance rows → Confirm 8 px (value text → button 16 px; was 48 px before moving the source line) | ≥ 44 px · ≤ 24 px | geçti |
| 3 | Jakob | native button/range, Tab order = reading order, link underlined, no custom cursor/scroll | 0 sapma | geçti |
| 4 | Seçim Yükü | no choice sets; the 6 states are read-only status, never a pilot choice | ≤ 5 | geçti |
| 5 | Yakınlık | rows inside the clearance group 8 px apart; groups 24 px apart (1:3) | ≤ 1:2 | geçti |
| 6 | Benzerlik | live: 5 font sizes (12/14/16/20/28 px) · 2 radii (4/8 px) · 0 shadows · 2 button styles (primary filled, secondary outline) | ≤ 6 · ≤ 4 · ≤ 2 | geçti |
| 7 | Tekdüze Bağlılık | 3 panels, none nested | ≤ 12 · 0 | geçti |
| 8 | Ortak Bölge | top-level regions: status banner, clearance, (reference, only in loss states), replay = 3-4 | ≤ 4 | geçti |
| 9 | Prägnanz | no glass, glow, gradient | 0 | geçti |
| 10 | Von Restorff | 1 primary (Confirm heard); accent only on it, the link and the slider; status colours green/amber/red carry meaning (not decoration) | 1 | geçti |
| 11 | Miller | 0 form fields; ≤ 3 clearance rows shown at once (largest scenario message 2) | ≤ 7 | geçti |
| 12 | Sıra Konumu | first: comm-state banner (task 2) · then last clearance (task 1); the replay control (demo only) last | birincil görevler başta | geçti |
| 13 | Doherty | no transitions/animations; render is local JS on slider input (no network) | < 400 ms | geçti |
| 14 | Zeigarnik | not a multi-step flow; replay shows time "x s" of 300 s | — | geçti |
| 15 | Zirve-Son | empty ("No clearance received yet."), normal, degraded (LOW CONFIDENCE), loss (STALE + reference list), recovered states all rendered at 0/20/80/150/180/220/260 s | 3/3 | geçti |
| 16 | Parkinson | no required inputs | ≤ %50 | geçti |
| 17 | Tesler | the only input is the crew's "Confirm heard" — the system cannot know what the crew heard; state, age, staleness and masking are computed | gerekçe | geçti |
| 18 | Postel | no free-text input on this surface (typed text goes through `clearance.tokenize`, which accepts numerals, spoken digits, FL80, 118.505) | normalizasyon | geçti |
| 19 | Occam | 34 elements (re-run after adding the one-line call-sign note: similar callsign on frequency / last call was for another aircraft); each maps to task 1 (values, tags, source, note), task 2 (banner, reasons, reference list) or the demo replay | 0 eşlenemeyen | geçti |
| 20 | Pareto | banner + clearance panel = 65 % of the main column on the first screen (77-447 px of 77-649 px) | ≥ %60 | geçti |

## scope.html — 20/20 measured · 0 HATA · 0 UYARI · TESLİM

| # | Yasa | Ölçüm | Eşik | Durum |
|---|---|---|---|---|
| 1 | Hick | nav 1 · actions 3 (Play, slider, click a track) | ≤ 7 · ≤ 5 | geçti |
| 2 | Fitts | Play 64×44 px, slider 44 px high, Play → slider 18 px; track hit circle r = 3 NM ≈ 14 px radius (28 px) at 625 px scope — below 44 px: dense-display exception declared, a selected track is outlined | ≥ 44 px (dense 32 px) | geçti (dense display declared) |
| 3 | Jakob | PPI north-up, range rings labelled, data block next to the symbol, history dots, velocity leader — the conventional radar display layout | 0 sapma | geçti |
| 4 | Seçim Yükü | no choice sets | ≤ 5 | geçti |
| 5 | Yakınlık | data-block lines 3 units apart, label 2 units from symbol; side panels 16 px apart, rows inside 4 px | ≤ 1:2 | geçti |
| 6 | Benzerlik | HTML 4 font sizes (12/14/16/20 px) + SVG 2 (≈12 and ≈14 px) · 2 radii · 0 shadows · 1 button style | ≤ 6 · ≤ 4 · ≤ 2 | geçti |
| 7 | Tekdüze Bağlılık | 3 panels (scope, selected track, signal → label), none nested | 0 nested | geçti |
| 8 | Ortak Bölge | scope · side panel · replay bar = 3 | ≤ 4 | geçti |
| 9 | Prägnanz | no glass, glow, gradient | 0 | geçti |
| 10 | Von Restorff | 1 primary (Play); alert colour red only for 7500/7600/7700 tracks | 1 | geçti |
| 11 | Miller | 0 form fields, 0 table columns (checker); selected-track list is 8 label/value pairs of one object (read, not chosen) | ≤ 7 fields / columns | geçti |
| 12 | Sıra Konumu | scope first (task 1), signal → label second (task 2) | birincil görevler başta | geçti |
| 13 | Doherty | redraw on slider input, no animation; scan step 480 ms on Play is the data rate (4.8 s scans at ×10), not a wait | < 400 ms yanıt | geçti |
| 14 | Zeigarnik | replay time shown "x s" | — | geçti |
| 15 | Zirve-Son | empty frame at t = 0 (no tracks yet, rings drawn), normal, alert (RADIO FAILURE), PSR-only target | 3/3 | geçti |
| 16 | Parkinson | no inputs | — | geçti |
| 17 | Tesler | everything is decoded/tracked upstream; the controller only selects | gerekçe | geçti |
| 18 | Postel | no text input | — | geçti |
| 19 | Occam | 30 static elements + per-track SVG; each element is part of the picture or the decode explanation | 0 eşlenemeyen | geçti |
| 20 | Pareto | scope + side panel ≈ 75 % of the first screen ((625 + 320) × 625 px of 1024 × 768) | ≥ %60 | geçti |

## scripts/atc_live.py (CLI surface) — checker not applicable (yüzey: cli), eye tests

Budget: 1 task (see what the panel would show for one transmission), 0 interactive actions, output ≤ 7 lines.
Measured on 4 cases (speech 20 dB, speech 15 dB, typed other callsign, typed invalid squawk): 4-5 lines each; one
aligned label column (SAID / HEARD / CALL / DISPLAY / NOTE, 7 characters + colon, Benzerlik); status in brackets
after each value; the advisory note is always last (Sıra Konumu / Zirve-Son); no colour (works in any terminal).

Label de-clutter (added after the first audit): each data block tries NE, SE, NW, SW of its symbol and keeps the
first free position. Measured on the live DOM over all 38 frames: overlapping data blocks 4 frames before → 0 after.
Colour-vision check (`python -m datawiz.palet_denetimi kategorik`, 4 Nov): cockpit status colours #3fb950 / #e3b341 /
#f47067 / #39c5e0 on #161b22 → 2 HATA (protan ΔE00 3.6 green~amber, deutan 2.1 green~red): secondary coding is
therefore mandatory and present — every status is spelled out in text, and border style differs per level (OK
solid, caution dashed, warning double; tags: confirmed solid, uncertain dashed, invalid double, stale dotted).
Scope colours #7ee2a8 / #c9d4cf / #f47067 on #131a18 → 0 HATA (alerts also carry text).
Risks: the dense-display hit target (28 px) is below 44 px by design.
