# YASA DENETİMİ — annunciator_mockup.html · 2026-11-04 · denetleyici koşuldu

**20/20 ölçüldü · 0 HATA · 0 UYARI · TESLİM**

Commands: `node ".../ux-yasalari/scripts/ux-yasa-denetimi.mjs" 02_EASA/outputs/mockups/annunciator_mockup.html` → exit 0,
"0 HATA · 0 UYARI · 32 öğe · görünüm 3", run after the last edit (warning message lamp amber → red). Eye-test values were
measured in the browser pane by `getBoundingClientRect()` at 375×812 (mobile preset). At desktop width the pane was hidden
and reported a 0 px viewport, so the desktop numbers were discarded and only the screenshot was used.

| # | Yasa | Ölçüm | Eşik | Durum | Gerekçe |
|---|---|---|---|---|---|
| 1 | Hick | nav 0 · max 3 actions per view (Next, Back, Restart) · 0 select | ≤ 7 · ≤ 5 · ≤ 7 | geçti (otomatik) | |
| 2 | Fitts | buttons 103×44, 68×44, 85×44 px (mobile); no inputs; primary first and leftmost; no destructive action (Restart only rewinds the demo) | ≥ 44 px · ≤ 24 px | geçti | |
| 3 | Jakob | native `<button>`s (Enter/Space), page scroll untouched, no custom cursor | 0 sapma | geçti | |
| 4 | Seçim Yükü | 0 radio/cards; the 8-step list is a progress list, not a choice | ≤ 5 | geçti | |
| 5 | Yakınlık | inner gaps 8 px (lamp↔lamp, title↔text, button↔button) · outer 32 px (panel↔step) = 1:4 | ≤ 1:2 | geçti | |
| 6 | Benzerlik | 4 font-size tokens (14/16/20/28) · 2 radii (4/8) · 0 shadows · 2 button styles | ≤ 6 · ≤ 4 · ≤ 2 | geçti (otomatik) | |
| 7 | Tekdüze Bağlılık | 0 cards, 0 nested | ≤ 12 · 0 | geçti (otomatik) | |
| 8 | Ortak Bölge | 4 top-level regions: panel, step, list, note; no single-item box | ≤ 4 | geçti | |
| 9 | Prägnanz | glass 0 · glow 0 · gradient 0 | 0 · 0 · ≤ 3 | geçti (otomatik) | |
| 10 | Von Restorff | 1 primary (Next step); the accent is neutral ink, so red/amber/green stay reserved for the lamps | 1 · ≤ 2 | geçti (otomatik) | |
| 11 | Miller | 0 form fields · 0 tables · 8 steps in one ordered list (progress, shown not chosen) | ≤ 7 · ≤ 7 | geçti | |
| 12 | Sıra Konumu | no nav; step list first = power-up lamp test, last = in-flight unlock: the two cases the design must get right | birincil görevler | geçti | |
| 13 | Doherty | state change is synchronous in the click handler (no network, no timers); the only animation is the 1 s lamp flash, which turns off under `prefers-reduced-motion` and is replaced by a dashed outline | < 400 ms | geçti | |
| 14 | Zeigarnik | "n of 8" in the step title + `aria-current` on the list | ≥ 3 steps → gösterge | geçti | |
| 15 | Zirve-Son | last step ends on a clear action ("Slow down, fly the aircraft, land"); no empty/error states because the data are static | ilgili ekranlar | geçti | |
| 16 | Parkinson | 0 required fields | ≤ %50 | geçti (otomatik) | |
| 17 | Tesler | 0 inputs: the phase and alert are derived from the scenario step; nothing asked | gerekçe | geçti | |
| 18 | Postel | no input to normalise | 0 | geçti (otomatik) | |
| 19 | Occam | 32 elements; each maps to a task: 3 lamps + phase/voice (task 1), title/why (task 2), 3 controls, progress list, source note | 0 eşlenemeyen | geçti | |
| 20 | Pareto | mobile first screen (812 px): panel + step text + controls occupy about 0–560 px ≈ 69 % | ≥ %60 | geçti | |

Risks: the lamp colours (#1f9d55 / #e0a000 / #d23b2e) were picked for the mock-up only. Real annunciator colours and
luminance must meet CS 23.1322 and the equipment's sunlight-readability specification; neither was measured here.
