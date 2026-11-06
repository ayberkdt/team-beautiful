# 17 · EASA — "Accident Investigation": what it can be and how we answer it

Prepared 2026-11-03 (evening before the opening). Tags: **[D]** read from the source in this session ·
**[D-ag]** read from the source by the research agent this session (its note: `research_notes/EASA kaza
soruşturması/R_easa_research.md`, 466 lines, every line tagged) · **[A]** search snippet only · **[K]** computed in
this repository (`prev_guess/00_general/scripts/challenges_2026_numbers.py` → `prev_guess/00_general/challenges_2026/`) · **[Y]** judgement.

> **Özet (TR).** EASA kaza *soruşturmacısı değil*: soruşturmayı ulusal kurum (Belçika'da AAIU(Be)) yürütür, EASA
> **danışman** olarak katılır, güvenlik tavsiyelerini (SR) alır ve yanıtlar, ECCAIRS/ERCS/Data4Safety/EPAS ile
> veriden öğrenir. En olası görev: (P1) verilen bir olay paketini 5 saatte soruşturmak — zaman çizelgesi, bariyer
> analizi, HFACS, ERCS puanı, SMART tavsiyeler. İkinci olası: (P2) olay raporlarında yapay zekâ ile öncül tespiti;
> üçüncü: (P3) enkazı ve veriyi daha hızlı bulmak. §4'te Brüksel SAS43M (5 Şubat 2026, taksi yolundan kalkış)
> olayı baştan sona örnek soruşturma olarak çözüldü; olgular AAIU ön raporundan okundu. Hesap araçları
> `aerokit.investigation` içinde (iz rekonstrüksiyonu, enerji, enkaz balistiği, kırılma noktası, arama yarıçapı,
> FDM olayları, HFACS).

## 1. Ground truth about the event and the sponsor

- The spoiler names the topic only: "EASA: Accident Investigation". Details come at the opening (4 Nov) [D: event
  message from the user]. Four challenges, all teams do all four; criteria: technical feasibility,
  innovation/creativity, sustainability, presentation quality [D: Regulations v1.1 §1.3–1.4].
- Event booklet schedule: competition blocks on **5 Nov and 6 Nov** (morning + afternoon), team presentations
  **7 Nov** [D: `EUROAVIA Ideathon 2026.pdf` p. 8]. Synopsys signs off "See you on November 5th" [D], so Ansys is
  probably one of the 5 Nov slots; the EASA slot is unknown [Y].
- EASA's only documented link with EUROAVIA is **GEN Days** (Cologne, Nov 2025): themes automation/AI, drones,
  sustainability, air operations & safety [D-ag]. No EASA student hackathon on investigation was found [D-ag].
  Read the jury as *safety-system people* (safety data, certification, SR follow-up), not field investigators [Y].

## 2. What EASA does — and does not do — in an investigation (the frame the jury will check)

- **Reg. (EU) 996/2010**: each Member State has an independent **safety investigation authority (SIA)** (Art. 4);
  accidents and serious incidents *shall* be investigated, never to apportion blame (Art. 5) [D-ag].
- **EASA is an adviser** (Art. 8): it may visit the site, examine wreckage, receive documents and take part in
  read-outs **except cockpit voice/image recorders**, and may not take part in work that determines causes or
  formulates recommendations — EASA certifies the aircraft, so it would judge itself [D-ag; reason Y].
- Notification "without delay" (Art. 9) [D-ag]; protection of sensitive information — witness statements, CVR
  (Art. 14) [D-ag]; final report within 12 months "where possible", else an **interim statement each anniversary**
  (Art. 16) [D-ag]; SR addressee answers within **90 days**, SIA rates the reply within **60 days** (Art. 18) [D-ag].
- Preliminary report within **30 days** when public interest is high (Annex 13 Rec. 5.4.6, quoted in the AAIU(Be)
  report) [D].
- **SRs** must be **SMART** with **one main addressee**; EASA's committee (ISIRC) meets every 6 weeks; first reply
  ≤ 90 days; replies rated Adequate / Partially adequate / Not adequate [D-ag, EASA "golden rules" slides 2026].
- **Learning machinery**: occurrence reporting Reg. 376/2014 (report within 72 h) → ECCAIRS 2 / European Central
  Repository (ADREP taxonomy) → **ERCS** risk score → Safety Risk Portfolios in **EPAS** → Annual Safety Review;
  **Data4Safety** fuses FDM, reports, ATM and weather data (operational after 2026) [D-ag].
- **ERCS** (Reg. 2020/2034): severity letter A/E/I/M/S/X from the **Key Risk Area** and potential loss of life;
  probability from **8 barriers** weighted design 5, tactical planning 2, regulations/procedures 3, situational
  awareness 2, warning systems 3, late recovery 1, protections 1, low-energy 1 (max 18 → score 0–9); result such
  as "M2"; RED/YELLOW/GREEN [D-ag, EASA Easy Access Rules].
- EASA Annual Safety Review 2026, **Top Safety Topics**: runway incursions, approach path management, **GNSS
  interference**, **erroneous take-off parameters**, adverse weather, mid-air collision, inadvertent IMC, wildlife
  strikes, **conflict with unauthorised UAS**, **on-board (lithium) fires**; leading CAT aeroplane risk area:
  fire/smoke/pressurisation [D-ag].

## 3. Predicted challenge formulations, ranked [Y]

1. **P1 · Investigate a supplied scenario** (data pack: narrative, FDR extract, ATC transcript, photos). Output:
   classification, timeline, analysis model, causes vs contributing factors, ERCS score, SMART SRs, "what we still
   need". → §4 is the rehearsal; §5 the tools.
2. **P2 · AI/data to find precursors in occurrence data.** Reports doubled in 8 years while staff did not; EASA is
   already building three AI modules (narrative extractor, record-change highlighter, **ERCS classifier**) and
   warns that AI may "smooth" rare events [D-ag]. Strong answer: Level-1/2 assistant (EASA AI Roadmap 2.0) that
   pre-codes ADREP/ERCS with a rationale, novelty detector for rare events, FDM-exceedance fusion
   (`exceedance_events`), federated so data stays national; human analyst signs off.
3. **P3 · Find the wreckage and the data faster.** GADSS tracking ≤ 15 min, distress tracking ≥ 1 fix/min,
   locate within **6 NM** [D-ag]; CAT.GEN.MPA.210 location-in-distress from 1 Jan 2025 for new large aeroplanes
   [D-ag]; ULB 37.5 kHz ≥ 90 days, ~3–4 km detection; LF ULD 8.8 kHz [D-ag]. Area arithmetic [K-hand]: a 6 NM circle
   is π·11.1² ≈ **388 km²**, one 37.5 kHz pinger detection disk (3–4 km) is 28–50 km², so a 6 NM requirement still
   needs ~8–14 towed-array "disks". Tools: `containment_radius`, `glide_reach`, `debris_footprint`,
   `locate_breakup`, and the IAMSAR search patterns in `aerokit.mission`.
4. **P4 · Investigation process for UAS / eVTOL / hydrogen / battery aircraft.** 27 UAS accidents in EASA States
   in 2025 [D-ag]; UK AAIB Airspeeder (95 kg) fly-away as precedent [D-ag]. Answer: "investigation-by-design" —
   crash-protected logger with a minimum parameter list (incl. BMS cell data), cloud-log preservation order within
   hours, HV/H₂ first-responder protocol, digital twin delivered at certification for log replay.
5. **P5 · Make safety recommendations work.** 2024: 40 SRs to EASA, 97 replies to 92 SRs, 36 % still awaiting
   the SIA's assessment at year end [D-ag]. Answer: an SR "digital thread" (finding → SR → ERCS risk → EPAS issue →
   SPI that shows whether it worked), NLP to find similar SRs across States (SRUR candidates).
6. **P6 · Runway safety: wrong-surface take-off / take-off performance.** Host-country case (§4) and Belgrade
   OY-GDC 2024 (intersection with insufficient TODA, wrong runway in the EFB, FLEX left in the FMS) [D-ag].
7. **P7 · Cabin fire and smoke** (lithium batteries; HB-JCD Graz 2024 engine failure + smoke, one crew fatality;
   TC-SOM power bank, Copenhagen 2025) [D-ag].

Sustainability lines that fit every variant [Y]: faster location = fewer ship/aircraft search hours (fuel, CO₂);
crash sites are contamination events (fuel, composites, Li cells, PFAS foam); proportionate SRs avoid fleet-wide
retrofits/scrapping; good investigation capability is an *enabler* of SAF/H₂/battery aircraft (EPAS SI-0060
"out-of-spec synthetic fuels" links SAF to safety [D-ag]); digital read-outs and 3-D site models cut travel.

## 4. Rehearsal case — SAS43M, Brussels, 5 Feb 2026 (take-off roll on a taxiway)

Facts read from the AAIU(Be) preliminary report AAIU-2026-02-05-01 (40 pages) [D, this session]:
- SAS flight SAS43M, Airbus **A320neo**, cleared for take-off from **runway 07R**, lined up on **taxiway E1** and
  accelerated; **100 kt** call-out at 21:04:02; at 21:04:09 thrust levers to full reverse and braking at **127 kt
  IAS**; the first officer called a right turn as the taxiway end and a fence approached.
- The tablet ground chart (LIDO) was used; its **Airport Moving Map** function (real-time own position) "was not
  integrated into the application being used".
- Notified to ICAO and EASA among others; States appointed accredited representatives with technical advisers.
Further details from the agent's reading of the same report [D-ag]: night, crew delayed all day, slot pressure;
crew mistook a taxiway for C6 after the C6 stop bar went out; the E1 information sign light was not working; the
tower A-SMGCS has a wrong-runway safety net but the ATCO noticed only after the reject; recorders read out at BEA.

How we would present it in 5 h (this is the P1 template):
1. **Classification** — serious incident: an aborted take-off from a taxiway is listed among serious-incident
   examples in Reg. 996/2010's annex [D-ag]. No injuries, no damage.
2. **Timeline** — one horizontal strip, UTC: pushback/delay context → taxi clearance → line-up on E1 → thrust set →
   100 kt (21:04:02) → reject at 127 kt (21:04:09) → stop. Times only from the report.
3. **Barriers (Swiss cheese ↔ ERCS barriers)** — design (taxiway geometry/lighting looks like a runway at night),
   tactical planning (taxi briefing under time pressure), procedures (line-up check of runway identity),
   situational awareness (no moving map; stop-bar cue lost), warning systems (A-SMGCS alert reached the ATCO too
   late; no on-board runway-alignment alert), late recovery (first officer's call at ~100 kt — **the barrier
   that held**).
4. **HFACS** — `aerokit.investigation.hfacs_table` turns findings into ordered rows, e.g. *Perceptual errors*:
   taxiway taken for the runway; *Technological environment*: no AMM, unlit sign; *Adverse mental states*: time
   pressure; *Organisational process*: EFB configuration choice. Mark every row as hypothesis until the final
   report.
5. **ERCS score [Y, illustrative]** — KRA *collision on runway/excursion*-type; 158 persons on board → potential
   loss class **X** (> 100); only "late recovery" held → a low barrier score → a RED-band score. Say the
   arithmetic out loud: the jury cares that we know the scheme, not that our digit is final.
6. **SMART SRs (one addressee each)** — to the operator: integrate AMM own-ship position in the EFB within 6 months
   (SAS already started this [D-ag]); to the aerodrome operator: monitor sign/stop-bar lighting serviceability with
   an alert to the tower; to the ANSP: route the A-SMGCS wrong-surface alert to the ATCO with a one-word
   call-out; to EASA: assess a certification standard for on-board runway-alignment alerting on new large
   aeroplanes (SRUR candidate — systemic, not airport-specific).
7. **What we still need** — CVR content (crew cross-check wording), lighting logs, A-SMGCS alert timing, fatigue
   data. Showing open questions earns credibility.
8. **Sustainability** — a software/EFB fix on existing hardware instead of retrofits; no taxiway rebuild; avoid
   grounding.

## 5. Calculation toolkit (`aerokit.investigation`, tests `tests/test_investigation.py`)

```python
from aerokit import investigation as I
tr = I.reconstruct_track(t, lat, lon, alt_m, window_s=9)      # ADS-B/FDR → GS, track, V/S, turn rate, bank, n
es, ps = I.energy_state(tr.t, tr.height, tr.ground_speed)      # E_s = h + V²/2g and dE_s/dt
fp = I.debris_footprint([1, 10, 100, 1000], h0=10_668, speed=247, wind_cross=20)   # impact points by β
e, n, rms = I.locate_breakup(found_e, found_n, betas, 10_668, 247, track_deg=90)  # inverse: break-up point
r95 = I.containment_radius(sigma_m, 0.95); reach, drift = I.glide_reach(h, LD, wind, tas)
events = I.exceedance_events(t, {"vs": vs}, [("sink > 1000 fpm", "vs", lambda v: v < -5.08, 3)], h, (0, 305))
rows = I.hfacs_table({"Perceptual errors": ["taxiway taken for runway"]})
```

Verified behaviours [K, tests]: the coordinated-turn bank equals atan(Vω/g) within 1 %; vacuum fall reproduces
V√(2h/g); a light fragment lands at its terminal speed √(2βg/ρ) within 2 %; `locate_breakup` recovers a known
break-up point exactly. One numerical bug was found and fixed while generating the tables: very light fragments
(β = 1 kg/m²) at 128 m/s have a drag time constant of ~0.02 s, which made a fixed 0.05 s RK4 step diverge; the step
is now limited to a fifth of that time constant, and a test covers the case.

Generated numbers (full tables in `prev_guess/00_general/challenges_2026/tables.md`) [K]:
- **Debris sorts by ballistic coefficient**: from FL350 at 480 kt with a 20 m/s crosswind, β = 5000 kg/m² parts
  land ~9.5 km along track after ~54 s, β = 1 kg/m² panels drift ~41 km downwind over ~34 min. A debris line
  orthogonal to the track is the wind's signature; its heavy end points back to the break-up.
- **Search radius**: 95 % → 99 % containment adds ~24 % radius and ~54 % area (Rayleigh).
- **Glide reach** from FL350 at L/D 17: ~98 NM still air, plus ~19 NM drift in a 25 m/s wind.

### 5a. Day command and ERCS calculator (added 3 Nov evening) [K]

`python prev_guess/02_EASA/scripts/investigation_day.py <pack>.json` turns a data pack (track CSV `t_utc_s, lat, lon, alt_ft`, runway,
FDM rules, narrative events, HFACS findings, ERCS barrier states, draft SRs) into: reconstructed gate states (speed,
sink, height above the 3° path, **energy excess** = height excess + (V² − VREF²)/2g as feet), threshold crossing,
touchdown point, runway-end speed, overrun distance, FDM events, one merged and sorted timeline, the HFACS table,
the ERCS score with its arithmetic, and three slide figures (`E1_vertical_profile`, `E2_speed_profile`,
`E3_ercs_barriers`). Speeds from positions are ground speeds; the report says so.

- **ERCS** (`I.ercs_score(kra, severity, {barrier: state})`): rules read this session from the EASA Easy Access
  Rules through a fetch summary — only *stopped* and *remaining* barriers count; weights design 5, tactical
  planning 2, regulations/procedures 3, situational awareness 2, warning systems 3, late recovery 1, protections 1,
  low energy 1 (low-energy key risk areas only: ground damage, excursion, other injuries); score = ⌈sum/2⌉;
  RED X0–X2, S0–S2, M0–M1, I0; YELLOW X3–X4, S3–S4, M2–M3, I1–I2, E0–E1; numerical equivalent X0 = 10⁶ falling a
  decade per digit, S = X/2, M = X/10, I = X/100, E = X/1000. SAS43M-type check (only late recovery + protections
  held, class X): **X1, RED, 10⁵** (test).
- **Take-off roll** (P6): `I.accelerate_stop_distance(v_reject, accel, decel, reaction_s)` and
  `I.takeoff_acceleration_monitor(t, speed, expected_accel)` — the latter flags the first moment the measured
  acceleration drops below 85 % of the expected one (a mass typed 25 % low is flagged ~10 s into the roll in the
  test), the idea behind take-off monitoring that EASA's "erroneous take-off parameters" topic asks for.
- **Rehearsal pack** (`prev_guess/02_EASA/cards/easa_rehearsal.json`, **fictional**, made by
  `prev_guess/02_EASA/scripts/make_rehearsal_pack.py`): unstabilised approach → long landing → overrun. Output: +320 ft and 171 kt GS at
  1000 ft (energy excess +809 ft), threshold at 131 ft, touchdown 1142 m in, runway end at 63 kt GS, 324 m overrun,
  ERCS S1 RED with the severity reason stated in the pack. The merged timeline exposed a time inconsistency in the
  invented narrative on the first run — use the same check on the real pack.

## 6. Slides for this slot (8) [Y]

1. The question in one line + who owns the answer (SIA / EASA / operator / NAA).
2. Classification and facts (only what the pack states; source on the slide).
3. Timeline strip.
4. Barrier picture (bow-tie or Swiss cheese) mapped to the 8 ERCS barriers.
5. Causes vs contributing factors (HFACS table, "no blame" wording).
6. ERCS score with the arithmetic.
7. 4–6 SMART SRs, one addressee each, with SRUR flag.
8. Sustainability + what we would still investigate.

Wording rules: "causal and contributing factors", "safety recommendation to …", never "pilot error was the cause".

## 7. Open items

Not verified in this session by anyone: the full serious-injury definition; FDR 25-h duration; 8.8 kHz detection
range; Annex 13 primary text for the 60-day draft-comment period. EUR-Lex and ICAO pages did not load for the agent;
996/2010 was read from the adopted text on legislation.gov.uk (later amendments not reflected) [D-ag].
