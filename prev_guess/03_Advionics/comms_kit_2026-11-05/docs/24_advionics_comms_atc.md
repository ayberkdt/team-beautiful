# 24 · Advionics "Automated Approach Guidance" — comms, surveillance and "translate signal"

Prepared 4 Nov 2026 (laptop clock UTC+3) by the Advionics comms/ATC session. Companion to doc 18 (GNSS-independent
approach guidance, `aerokit.approach` / `aerokit.autoland`), which stays valid for the "guidance" reading.

Tags: **[D]** read from the source by this session · **[D-ag]** read by a research agent (one note per source in
`03_Advionics/research/`, prefix S_ sponsor, C_ comms, A_ speech recognition, R_ surveillance; each has URL,
date, section) · **[A]** search snippet only · **[K]** computed here (`python 03_Advionics/scripts/atc_day.py --asr`, numbers in
`03_Advionics/outputs/report.md`) · **[Y]** our judgement or model assumption.

> **Özet (TR).** Notlarda tam görev yok; elimizdeki kelimeler "radar expertise", "iletişim kesilirse", "translate
> signal", "[voice] sinyal display'e nasıl ulaşır". Sponsor (Intersoft/Advionics) bir **gözetim ölçüm ve sinyal
> dönüştürme** şirketi: radarın Pd'sini, hatasını, sahte hedefini ölçüyor; ADS-B'yi ASTERIX'e çeviriyor; ses ürünü
> yok. Bu yüzden üç yoruma da çalışan kod hazırladık: (H1) VHF ses → yapılandırılmış öneri ekranı, belirsiz rakamı
> asla kesinmiş gibi göstermeden; (H2) iletişim kaybında dürüst durum makinesi, **kayıp mesajı asla yeniden
> üretmeden**, SERA.14083 (2025: 20 dk, 7600/7601) uyumlu; (H3) radar sinyali → ekran: Mode A/C darbe dizisi, Mode S /
> ADS-B (CPR) çözücü, PSR/SSR bütçe ve Pd, MTI/MTD/CFAR/kargaşa haritası, IMM izleyici, ASTERIX CAT048/CAT021,
> radar skobu; (H7) **PAR konuşmalı
> yaklaşma**: radar ölçer, rehberlik sesle gelir, ses kesilirse 5 s sonra "PAR GUIDANCE LOST" — notlardaki her
> kelimeye uyan yorum; (H5/H7) yaklaşma göstergesi: geçerli kaynak yoksa ibreler kaldırılır, asla ortalanmaz.
> Kayıp kelime "NOT RECEIVED" olarak gösterilir, asla tahmin edilmez. Gerçek konuşma da döngüde:
> Windows SAPI ile sentetik pilot/kontrolör sesi → gürültü → tanıma → ayrıştırıcı; indirme yok.

## 0. Friday-morning decision card

| Mentor says… | Lead with | Demo (all offline) | Say these numbers |
|---|---|---|---|
| voice / radio / "translate" | H1 + H2 | `atc_live.py "..." --snr 15`, `cockpit_demo.html` | real ASR heard 25R as **35R at 0.99** — caught by the runway check; 0 wrong values shown at any SNR |
| comms lost | H2 + H4 | `cockpit_demo.html` 88-252 s | SERA.14083: **20 min**, 7600 / 7601; missing words → **NOT RECEIVED**, never filled in |
| radar / signals | H3 | `scope_demo.html`, report §5a | false track-scans **2953 → 3** (MTI → clutter map + strict PSR initiation); SSR codes 0.995/scan, 0 wrong |
| approach guidance / PAR | H7 + H5 | report §5b-5c, F7 | ground radar exposes a **25 m** bias; no valid source → needles **removed**, never centred |
| ILS / flight inspection | ILS slide | `test_atc_ils.py` | dead modulator reads DDM 0 = "on course" → we show **FLAG** |
| unclear | shared slides 1-2 | — | ask §9 question 1 |

Safety line for every branch: advisory only; nothing lost on the channel is ever reconstructed.

## 1. What we know and what we do not

- The notes (`00_Common/organiser_notes/02_Advionics_Automated_Approach_Guidance.md`, a transcription of
  handwritten notes, not official text): "Advionics → Radar Expertise", "Friday Morning Challenge", "İletişim
  kesilirse", "Translate signal", "Kule ile iletişim kesilirse [voice] sinyal display'e nasıl ulaşır gibi bir şey".
  The words voice, radio and translate were used by the speaker. **CPDLC, ADS-B, SSR, speech recognition are not in
  the notes** [D, notes file].
- Not known: whether "translate" means speech→text or RF→picture; whether comms are lost totally or degraded; whether
  the deliverable is a concept or a demo. All three are mentor questions (section 9).

## 2. The sponsor, and what it rewards

From the sponsor agent (53 notes, summary `S_00_summary.md`) [D-ag]:

- **Intersoft Electronics** (civil ATC/CNS) sells *measurement of surveillance and navaid quality*: RASS radar test
  and analysis (radar comparator: Pd, processing delay, false-plot rate, code probabilities, range/azimuth/time bias
  and random error, radar vs ADS-B), SMS real-time surveillance monitoring (KPIs Pd, update rate, integrity, latency,
  false plots; counts 7500/7600/7700 codes; split, reflected, side-lobe plots), RES SSR/Mode S/ADS-B target simulator
  (up to 2048 targets with FRUIT and reflections), RTG PSR target generator, SkyRF drone flight inspection with an
  automated "Mini-Approach", NGSP radar processing (fitted also to precision approach radars; "True 3D Height" from
  PSR as a transponder-failure backup), NORA non-rotating arrays, DHM protocol conversion (ADS-B → ASTERIX CAT021,
  legacy → ASTERIX) [S_intersoft_rass_catalogue, S_intersoft_sms_*, S_intersoft_ngsp_*, S_intersoft_nora_*].
- **Advionics NV** (Oostkamp) builds RF hardware; flagship L-IESA naval IFF (200 NM with 1200 W, beams re-pointed in
  100 ms) [S_intersoft_liesa_leaflet]. Jobs: hardware, test, production only [S_advionics_jobs_listing].
- **Not found:** any own speech or voice product, any own MLAT product, any public link to EUROAVIA [S_00_summary].
- Home page of advionics.be read by this session on 3 Nov (doc 18 §1) [D].

**So the jury is surveillance/RF people [Y].** Speak their KPI language (Pd, Pfa, bias + random error, update rate,
latency, false/split/garbled plots, code correctness, integrity), output **ASTERIX**, and verify with their kind of
tools (RES/RTG injection, radar-vs-ADS-B comparison, SkyRF flying the approach). A pure speech-AI pitch without the
surveillance side would miss them.

## 3. Interpretations, what we built for each, and the slide plan

| # | Reading of the notes | Likelihood [Y] | What answers it (code) |
|---|---|---|---|
| H1 | ATC **voice → cockpit display** ("translate signal" = speech to structured data) | high (words in the notes) | `atc.clearance`, `atc.channel`, `atc.asr_sapi`, cockpit mock-up |
| H2 | **Comm loss**: what reaches the display when the tower link degrades or fails | high | `atc.commhealth` state machine + advisory display, SERA.14083 |
| H3 | **Radar signal → ATC display** (sponsor's core: PSR/SSR/Mode S/ADS-B → plots → tracks → screen) | high for this sponsor | `atc.modeac`, `atc.modes`, `atc.radar`, `atc.tracker`, `atc.asterix`, `atc.traffic`, radar scope |
| H4 | **Lost comm seen from the ground**: how ATC knows (7600, no readback, IDENT check) and keeps separating | medium | scope shows 7600 as RADIO FAILURE; SERA.14083(b)(1) IDENT check = our TX_LOST evidence |
| H5 | **GNSS-independent approach guidance** from ground surveillance (doc 18 P1, PAR-like) | medium | `aerokit.approach` (doc 18) + `atc.radar` budgets |
| H6 | **Voice + surveillance correlation**: match spoken callsign to the track, readback/hearback check | medium | `clearance.resolve_callsign`, `readback_check`, `similar_callsigns` |
| H7 | **PAR talk-down**: a ground radar measures the aircraft on final and the guidance reaches the pilot *by voice*; "if communication is lost" the guidance stops; "translate signal" = radar deviation → voice phrase → cockpit display (or datalink) | **high — fits every word of the notes** [Y] | `atc.par` (measurement with Annex 10 PAR accuracy, talk-down generator, phrase → display parser, guidance-lost timer), reuses `aerokit.approach` |

Slide plan (one deck, the first two slides shared, then the branch the mentor confirms; every number from section 6):

- **Shared 1 — the chain.** Speech or RF → detection → decoding → validation → display, with *where it breaks*:
  VHF AM channel (noise, blocked transmissions), recogniser errors, garbled replies/FRUIT, CRC failure, track loss.
- **Shared 2 — the rule.** "The display may only show what was actually received, with its source and age; a lost
  message cannot be reconstructed." SERA.14083(b)(3): clearances are not blind-transmitted unless the originator asks.
- **H1 (3 slides).** (a) Live demo: phrase → noisy audio → recogniser → parser → panel (`atc_live.py`, then
  `cockpit_demo.html`).
  (b) "Two seven zero vs two zero zero": masked digit / AMBIGUOUS, never a confident wrong number. (c) F1/F2 and the
  real-ASR threshold curve (F5): integrity vs availability; why the threshold must be calibrated per recogniser.
- **H2 (2 slides).** (a) State machine NORMAL → DEGRADED → RX_LOST → ALTERNATE_AVAILABLE → ALL_COMMS_LOST with the
  evidence for each (F4). (b) What the crew sees: STALE with age, SERA.14083 reference (7600/7601, 20 min), CPDLC as
  non-urgent alternate, common-cause check (same bus/antenna is not an alternate).
- **H3 (3 slides).** (a) Same pulses = squawk or altitude (Mode A vs Mode C depends on P1–P3 spacing). (b) Mode S /
  ADS-B decode validated on published vectors + CRC 1-bit repair; ASTERIX CAT048 bytes. (c) PSR Pd vs range
  (Swerling 1, F3; the 8 dB steady-vs-fluctuating gap from the report) against the EUROCONTROL 90 % figure; IMM vs CV track continuity; scope demo.
- **H7 (2 slides, lead with it if the mentor says "radar guidance").** (a) Loop: PAR measures 1 Hz → controller
  phrase every ~5 s → VHF → pilot; our version generates the phrase automatically from the radar and also sends the
  deviation as data, so the cockpit can draw needles from either. (b) Voice lost on final: the panel shows "PAR
  GUIDANCE LOST" 2 s after the expected call (never extrapolates); the crew applies the lost-communication
  instruction given before final; the radar still sees the aircraft (scope) and the deviations can go by datalink.
  Bonus: the aircraft in the demo flies on a *biased* on-board source (25 m high, 40 m off) and the independent
  ground radar calls it — the doc 18 "independent monitor" argument in the sponsor's own technology.
- **Same rule on the navaid side (1 slide, optional).** An ILS receiver that lost its 90/150 Hz tones would read
  DDM = 0 and centre the needle — "on course" — unless it validates the signal first; `atc.ils` shows the FLAG
  instead. The SkyRF world (DDM measurement) in one picture: "a lost signal must never look like a good one."
- **H4/H6 (1 slide each).** 7600 on the scope; spoken callsign ↔ track correlation, similar-callsign warning.
- **Verification slide (all branches).** RES/RTG-style injection (our `traffic.py` is a software version), published
  test vectors, radar-vs-ADS-B comparison, shadow mode; KPI table in the sponsor's vocabulary.

## 4. Architecture (one picture for all readings)

```
 VHF voice (118-136.975 MHz AM)        SSR 1030/1090 MHz, Mode S, ADS-B 1090ES      PSR (S-band echo)
        |                                         |                                      |
 audio monitor: SNR, clipping,      pulse/bit decoding: F1-F2 bracket, garble,   I/Q burst -> MTI / MTD ->
 dropouts, squelch (channel.py)     multi-reply code validation, CRC-24 + 1-bit  CA-CFAR -> clutter map ->
                                    repair, CPR air/surface (modeac/modes)       plots (psr_processing.py)
        |                                         \___________________  ______________/
 recogniser (SAPI grammar /                                           \/
 dictation; any ASR) -> words      plots -> IMM tracker (gating, M-of-N, coasting, identity never overruled)
 + confidences + n-best                                   |
        |                         ASTERIX CAT048 (radar) + CAT021 (ADS-B) records (asterix.py)
 clearance parser: callsign,                              |
 values, masking, ambiguity,                    radar scope (scope.html): labels, history, 7600 alert
 validation, readback check                               |
        \__________________ comm-health state machine (commhealth.py) ___/
                                       |
              advisory display (cockpit.html): only received items, source, age, STALE, NOT RECEIVED
                                       |
 approach guidance panel (guidance.py): clearance + ground PAR uplink + on-board source -> needles, height,
 MINIMUMS; annunciates every lost/invalid/disagreeing source, removes needles rather than guessing
```

## 5. What exists now (all in this repo; tests `tests/test_atc*.py`, 173 tests)

| Module | Does | Validated against |
|---|---|---|
| `atc/modes.py` | Mode S CRC-24, single-bit repair by syndrome, DF4/5/11/17/20/21, callsign, Gillham/25 ft altitude, squawk, CPR global/local + encoder, surface position (TC 5-8, 90° zones), velocity, Comm-B BDS 2,0, encoders for synthetic traffic | Sun (2021) worked vectors [D] (KLM1023; 52.25720214843750 / 3.91937255859375, 38000 ft; 159.20 kt / 182.88° / −832 fpm; TAS 375 kt; DF4 36000 ft; DF5 0356; surface 52.320607 / 4.734735, 17 kt, 92.8125°) — 20/20 rows; 20 000/20 000 two-bit errors rejected; CRC/address/Comm-B vectors [D-ag]; 44 Gillham table rows incl. the octal column [D-ag]; all 8192 AC codes, NL over −90…90°, 300 random CRCs vs pyModeS 3.6.1 (independent implementation) [K] |
| `atc/modeac.py` | Mode A/C reply pulse trains (F1–F2 20.3 µs, 1.45 µs grid, SPI 4.35 µs), interrogation mode from P1–P3, garble and phantom-bracket flags, FRUIT injection | timings: Wikipedia SSR [D] + patents via snippet [A] + R_atcrbs_wiki [D-ag]; round trips |
| `atc/radar.py` | PSR radar equation, Albersheim, exact steady-target Pd (Marcum Q), Swerling 1, SSR up/down link (reuses `aerokit.approach` Friis/noise read-only), horizon, hits/scan, M-of-N, FRUIT-free probability | Albersheim vs exact Marcum Q (±0.02 Pd), 13.1 dB at Pd 0.9/Pfa 1e-6; Swerling 1 vs 200 000-sample Monte Carlo [K] |
| `atc/tracker.py` | polar→Cartesian covariance, alpha-beta, CV Kalman (Joseph form), 2-model IMM, global-nearest-neighbour gating (χ² 99 %), M-of-N confirmation, coasting, identity-gated association | NEES consistency; IMM beats CV in a 1.5°/s turn [K] |
| `atc/psr_processing.py` | I/Q-level PSR: noise, terrain clutter, wind farm, Swerling-1 echoes; fixed threshold, MTI 3-pulse canceller, MTD Doppler bank (Blackman-Harris, zero-velocity notch), CA-CFAR (single- and multi-look), recursive clutter map, plot clustering; optional in `traffic.Scenario(psr_chain=...)` | CFAR Pfa by Monte Carlo; MTI nulls at 0 and the blind speed; clutter map vs MTD on persistent clutter; notch hides tangential targets, clutter map does not |
| `atc/asterix.py` | CAT048 data block (CAT/LEN/FSPEC) with I048/010, 140, 020, 040, 070, 090, 220, 240, 161, 200; CAT021 ed. 2.7 (010, 040, 161, 071, 130, 080, 070, 145, 160, 170) | layouts and LSBs from EUROCONTROL Part 4 Ed. 1.15 [D]; FSPEC and item bytes checked by hand in tests |
| `atc/clearance.py` | ATC text/ASR words → structured clearance (heading, altitude/FL, speed, squawk, frequency, QNH, runway/ILS, go-around, direct, wind as INFO), `<gap>` / dropout → NOT_RECEIVED (never a guessed value), homophone in the callsign → "callsign unsure", per-digit confidence masking, *to/two* ambiguity, n-best disagreement → AMBIGUOUS, validation (3-digit heading 001–360, octal squawk, valid 25/8.33 kHz channel name, QNH 900–1100, climb/descend direction, runway exists at the destination), callsign check, readback comparison, channel name → operating frequency, surveillance callsign correlation, similar-callsign finder | 8.33 kHz naming from the Icom IC-A24 channel table [D]; readback list SERA.8015(e)(1) [D-ag]; the challenge-note test cases (section E3) as unit tests |
| `atc/channel.py` | VHF voice band-limit, noise at set SNR, clipping, dropouts, squelch; audio monitor (speech activity, SNR, clipping, dropout fraction); word-level recogniser error model | behaviour tests; parameters are [Y] |
| `atc/commhealth.py` | state machine NORMAL/DEGRADED/RX_LOST/TX_LOST/ALTERNATE_AVAILABLE/ALL_COMMS_LOST with evidence and hysteresis, stuck-microphone detection (PTT keyed > 30 s [Y]), independence check of alternates (bus/antenna), advisory display model (similar-callsign warning, 'last call was for X — not shown') | randomised invariant test: displayed ids ⊆ received ids, never newer than now, STALE in loss states, nothing received without carrier |
| `atc/par.py` | PAR measurement (Annex 10 accuracy figures via ENRI), talk-down phrases every 5 s from 1 Hz measurements, phrase → display state (unheard parts stay '?'), guidance-lost timer (5 s [A]), stop at DH | unit tests; biased-aircraft scenario on `aerokit.approach.simulate_approach` |
| `atc/ils.py` | ILS receiver in miniature: detected 90/150 Hz audio → depths → DDM → needle (±2 dots), validated first: no carrier, a missing tone or an implausible depth sum gives the FLAG, never a centred needle | unit tests (DDM within 0.003; dead modulator → FLAG) |
| `atc/guidance.py` | approach guidance panel: clearance (voice → parser → display) + ground PAR uplink + on-board source → lateral/vertical needles (dots), distance, height, glide-path height, MINIMUMS; annunciates NO APPROACH CLEARANCE, RWY MISMATCH, GND GUIDANCE LOST (> 5 s), NAV INTEGRITY (PL > 35 m), SOURCES DISAGREE (> 30 m, hysteresis), V/L FLAG (needles removed), COMM LOST; reuses `aerokit.approach` geometry read-only | unit tests; scripted end-to-end run, report §5c, F7 |
| `atc/mlat.py` | TDOA multilateration (weighted Gauss-Newton), covariance and GDOP from geometry, ADS-B-vs-MLAT position consistency flag (spoof check) | exact noise-free recovery; covariance vs Monte Carlo (±15 %); GDOP outside the network; 400 m ghost flagged, honest 10 m error not |
| `aerokit.comms` (existing, read-only) | link budgets, BER/modulation, channel models — for a datalink-design task | its own tests |
| `atc/datalink.py` | CPDLC uplink → display clearance (source 'CPDLC'), only UM20/74/117/190 mapped (identifiers read by the agent) | unit tests |
| `atc/asr_sapi.py` | Windows System.Speech TTS + recogniser (dictation, ATC phraseology grammar, PAR talk-down grammar), batch mode | used in `atc_day.py --asr`; grammar coverage checked with `EmulateRecognize` |
| `atc/traffic.py` | synthetic terminal area: truth → DF17 hex with bit errors, Mode A/C pulse trains with FRUIT (1 or 4 replies per mode with code validation), PSR plots (Swerling 1) or the I/Q chain (`psr_chain=`) → decoders → IMM tracker (optional strict PSR-only initiation) → (in `atc_day.py`) ASTERIX CAT048/CAT021 → scope; RASS-style KPIs vs truth | end-to-end statistics and KPIs in the report |
| `03_Advionics/scripts/atc_day.py`, `atc_html.py`, `atc_live.py`, `atc_doc_check.py` | report (+ `--asr`, `--psr` studies, cached), audited figures F1-F7, demo data; offline single-file demo pages; live speech demo (`--dropout`, `--text`); check that the 44 numbers quoted here are in the report | — |
| `03_Advionics/templates/cockpit.html`, `scope.html` | the two mock-ups (ux-yasalari: 0 HATA · 0 UYARI) | checker + live-DOM eye tests (section 10) |

## 6. Numbers to have on the table

Rules and standards:

| Value | Source |
|---|---|
| EU radio failure (SERA.14083, Reg. (EU) 2024/404): IFR keep last assigned speed and level **20 min**, then flight plan, descend at EAT/ETA, land within 30 min; **7600**; **7601** = IFR flight that meets VMC and whose pilot-in-command decides to continue in VMC: land at the nearest suitable aerodrome, report arrival; try all means incl. data link, satellite voice, mobile phone; no blind clearances unless originator asks; ATC checks the receiver with SSR code change / IDENT | [D] EASA eRules (read through a summarising fetch tool); applicable since 1 May 2025 [D-ag C_BCAA_ASIL_2025_02] |
| Old ICAO/EUR text: 7 min hold in IMC (still quoted in many AIPs — check which applies) | [D-ag C_AIP_Georgia_ENR18] |
| Voice watch stays when CPDLC is established (SERA.8035); mandatory voice readback items SERA.8015(e)(1): route, runway, altimeter, SSR code, frequency, level, heading, speed, transition level | [D-ag C_EASA_SERA_EAR] |
| VHF AM 118–136.975 MHz; 6K80A3EJN (25 kHz) / 5K00A3EJN (8.33 kHz); audio 300–3400 Hz (25) or 350–2500 Hz (8.33); Rx sensitivity −101 dBm | [D-ag C_ETSI_EN300676_1] |
| 8.33 kHz channel names: 118.005 / .010 / .015 operate at 118.0000 / .0083 / .0167 MHz | [D] Icom IC-A24 table |
| VDL Mode 2: D8PSK 10 500 symbol/s = 31.5 kbit/s | [D-ag C_ETSI_EN301841_1] |
| CPDLC practice 2026: time-critical stays on voice; ground timeout 120 s; revert to voice | [D-ag C_EUROCONTROL_CPDLC_RecPractices_2026] |
| Simultaneous AM transmissions: the stronger masks the weaker with little or no detection | [D-ag C_SKYbrary_USiT] |
| Loss of communication 4 % of EVAIR reports 2018–22; go-around in 48 % of those | [D-ag C_EVAIR_Bulletin25] |
| SSR 1030/1090 MHz; P1–P3 8 µs (A), 21 µs (C); P2 2 µs after P1 for side-lobe suppression; Mode C 100 ft, D1 unused; PRF ≤ 450 Hz | [D] Wikipedia SSR |
| ESASSP: 3 NM separation update ≤ 5 s, RMS ≤ 300 m, P(update) ≥ 97 %; 2.5 NM on final ≤ 5 s, ≤ 200 m, ≥ 99 % | [D-ag R_esassp] |
| EUROCONTROL 1997 (SUR.ET1.ST01.1000-STD-01-01, recommended figures): SSR Pd > 97 %, Mode A code > 98 %, Mode C > 96 %, validated false Mode A < 0.1 %, SSR σ < 70 m / 0.08°, bias < 100 m / 0.1°; PSR Pd > 90 %, < 20 false prev_guess/01_Ansys/reports/scan, σ < 120 m / 0.15° | [D] §6.3–6.4 (PDF text); 4 s TMA rotation [D-ag] |
| PAR (ICAO via ENRI): ≥ 9 NM, 20° az × 7° el, accuracy elevation 6 m / 0.4 % of range + 10 % of offset, azimuth 9 m / 0.6 % + 10 %, range 30 m / 3 %, update ≤ 1 s (how the fixed and percentage terms combine is not stated; Annex 10 not read; our model uses the larger [Y]) | [D-ag R_par_enri_soumu], checked by the audit `R_audit_2026-11-04.md` |
| PAR talk-down words: slightly/well above/below glide path, slightly/well left/right of course, "rapidly/slowly" trend, range at least once per mile, guidance to DH, missed approach outside safety limits | [D] code7700.com quoting AIM 5-4-11 / AFM 51-37 ¶6-17 (secondary) |
| PAR transmissions ≈ every 5 s; controller gives lost-comm instructions for a loss of more than 5 s on PAR final (15 s on surveillance final, ≤ 1 min on vectors to final): try a secondary/tower frequency, proceed VFR if possible, or fly the non-radar / published lost-comm procedure | [A] two independent search summaries of FAA JO 7110.65 (5-10-4, 5-12; one citing edition V, April 2014) and a Navy GCA manual; the FAA site (403), its PDF notices (403), the browser route (policy check) and the Navy mirror (bad certificate) all refused reading on 4 Nov — **present as "about 5 s"** |
| ARTAS: architecture "largely based on the IMM inspired design" of NLR (whose IMM research used uniform-motion, speed-change and left/right-turn modes); PDA later replaced by JPDA; close to 90 % of European daily flights at 43 ACCs | [D-ag R_blom_imm_atc, R_eurocontrol_artas_asterix]; wording corrected after the audit |

Speech recognition in ATC ([D-ag] unless marked, `A_00_summary.md`):

| Value | Source note |
|---|---|
| Hybrid ASR baseline WER per ATC test set with its SNR: NATS ≥ 20 dB 7.7 %, ISAVIA 15–20 dB 12.5 %, ATCO2-Test 10–15 dB 24.7 %, LiveATC-Test 5–15 dB 35.8 % (dataset level, not a controlled sweep); ATC audio "usually below 15 dB SNR" | **[D]** Zuluaga-Gomez et al., SLT 2022 (arXiv 2203.16822, PDF read by this session) |
| HAAWAII: ATCo WER 2.8–2.9 %, pilot 7.1–10.4 %; command extraction ATCo 92–93 %, pilot 71–80 %; readback errors in 1.3 % of utterances; detection 81–82 % at 67 % false alarms in ops | A_HAAWAII_readback_SID2022 |
| Callsign accuracy on VHF 41.3 % → 69.7 % with surveillance callsigns boosted | A_Nigmatulina2021_callsign_surveillance [D-ag]; the **+28.4 points absolute** and "up to 74.2 % relative improvement in WER of callsign recognition" are in the abstract **[D]** (arXiv 2108.12156, submitted to Interspeech 2021) |
| Off-the-shelf Whisper large-v3 zero-shot ~79 % WER on ATCO2 | A_Wee2025_SEA_accent_Whisper |
| MALORCA command recognition Prague 91.9 % (error 0.6 %), Vienna 85.2 % (error 3.2 %) | A_MALORCA_D5-3_final_report |
| Readback/hearback, tower (Cardosi 1994): < 1 % errors for 1–5 element messages, 1.4 % / 1.3 % for 6 / 7 elements; controllers missed 7 of 19. En route (Cardosi 1993, cited there): 8 % miscommunication for clearances with 5+ elements | C_Cardosi_1994_FAA_RD94_15, A_Cardosi1993_FAA_enroute_readback; split by study after the audit |

Computed here [K] (`outputs/report.md`, run of 4 Nov):

- Decoders: 20/20 published vectors decoded exactly (incl. surface position); 44/44 Gillham rows; 8192/8192 altitude
  codes equal to pyModeS; 20 000/20 000 random two-bit errors rejected.
- PSR (illustrative S-band terminal radar [Y]: 25 kW, 34 dBi, 1 MHz, NF 3 dB, losses 8 dB, 16 pulses coherent,
  Pfa 1e-6): Pd 0.9 for a Swerling-1 2 m² target ends at 24.8 NM, for 10 m² at 37.1 NM (`radar.psr_range_for_pd`); steady target needs 13.1 dB,
  Swerling 1 21.1 dB → **fluctuation costs ~8 dB**.
- SSR: 8 hits/scan (250 Hz, 2.4°, 4.8 s); P(≥ 4 of 8) = 0.990 at 0.8 per reply; FRUIT-free probability of a reply
  0.96 / 0.82 / 0.44 at 1000 / 5000 / 20 000 FRUIT/s.
- Tracker on the turning ownship (6 seeds, 6 aircraft): track broken into 5.8 ids per run with CV Kalman vs 2.0
  with IMM; P95 position error 1093 m (CV) vs 368 m (IMM) — an earlier 5-aircraft run gave 1.7 ids and P95 38 m (report since overwritten, console
  output only); re-initiated tracks (which start with zero velocity) are the likely cause of the larger tail [Y, not checked].
- Synthetic chain (6 aircraft incl. similar callsign BTL132, 38 scans): figures in `outputs/report.md` §5. KPIs in the
  sponsor's vocabulary, chain vs truth: PSR Pd 0.93/scan (EUROCONTROL 1997 recommends > 0.90), SSR Pd 1.00, Mode A
  code valid 0.87 per reply and **wrong 0.00** (garbled replies become "unknown", never a wrong code); measured with
  4 replies per mode and 2-must-agree validation: Mode A/C **0.995 / 0.995 per scan** at 3000 FRUIT/s (recommended
  > 0.98 / > 0.96), and at 10 000 FRUIT/s validation removes the 0.53 % wrong codes of single replies; Mode C valid
  0.83 per reply, false PSR
  plots 3.0/scan (< 20), ADS-B update 0.99/scan with median position error 19 m. Range/azimuth sigmas recover the
  injected noise (self-check, not equipment data).
- ASTERIX: 228 CAT048 records in 6251 octets (27.4 octets/record) and 148 CAT021 records in 5403 octets over the
  run; worst CAT021 position round trip 1.38 m.
- I/Q-level PSR (report §5a): false track-scans in 38 scans — MTI 2953, MTD 2072, MTD + clutter map 49, + strict
  PSR-only initiation **3** (baseline with random clutter plots 7); the no-transponder aircraft sits near the 53.5 m/s
  blind speed, so MTI/MTD never track it (0/38) and the clutter-map chain does (36-37/38).
- Voice → display (word model [Y]) and real SAPI recognition: tables in `outputs/report.md` §2–3 (see section 7 for the
  headline numbers of the final run).

## 7. Headline results

Full tables in `outputs/report.md` (§1 decoders, §2-3 speech, §4-5a radar, §5b PAR, §5c guidance). Speech first:

- **A real recogniser is sometimes confidently wrong.** SAPI grammar recognition of the synthetic voice through a
  300–3400 Hz channel at 30 dB returned "cleared ILS approach runway **three** five right" for *two five right* with
  utterance confidence **0.99** (final run, `outputs/report.md` §3). In a first run (16:40) the same phrase came back at 0.82 and
  "flight level one **tree** zero" for 120 at 0.81 — the recogniser is not deterministic run to run, and its
  confidence is not a guarantee. (That first run's `asr_sweep.json` was overwritten by the re-run without an anchor
  copy; its figures survive only in this session's console output — treat them as anecdotal.) A confidence gate alone let the 0.99 error through.
- **Context catches what confidence cannot.** With the destination's runway list (`known_runways`, from the
  navigation database/ATIS) the parser marks "runway 35R does not exist at this aerodrome" INVALID. Final run, SAPI
  grammar, conservative parser: **0 wrong values shown at every SNR** (30 → 0 dB); naive parser (best text at face
  value): 2 wrong values per SNR level from 15 to 30 dB. Correct values shown at 30 / 20 / 15 / 10 dB: 82 / 55 / 45 /
  5 % (the rest withheld; at 10 dB the recogniser rejects 81 % of utterances outright).
- **Display text is itself a translation.** SAPI dictation's display text wrote the callsign "one two three" as
  "1 to 3" (inverse text normalisation); parsed at face value that is callsign BTL1 → "not for us" for every message.
  The parser must work on the recogniser's lexical words, not on its pretty text.
- **The threshold is a calibration.** Threshold sweep (F5, SNR ≥ 10 dB pooled, 88 instructions): 0.5–0.9 give the
  same 47–48 % correct and 0 wrong (with the runway check); 0.95 drops correct to 36 %. For a product this curve is
  measured on recorded ATC speech, per recogniser.
- **PAR talk-down by real speech (H7).** 13 generated talk-down transmissions spoken by the Windows voice, through
  the band-limited noisy channel, recognised with a PAR-phrase grammar and parsed into needle classes (glidepath,
  course), utterance-confidence gate 0.7 [Y]: 30 dB 14/24 classes correct, 15 dB 6/24, 10 dB 0/24 — **0 wrong at
  every SNR**, the rest shown as "?" (`outputs/report.md` §5b).
- **Word-model sweep (F1/F2, assumption-driven).** At 21–30 dB the conservative parser shows 5–14 wrong values per
  1000 instructions vs 30–53 for the naive one, and withholds 17–25 % vs 11–14 %. At ≤ 9 dB it withholds ~100 % and
  shows ≤ 2 wrong per 1000, while the naive parser shows 94–129 (round 2: up from 74–115, because a homophone in
  the callsign now makes a call "unsure" — shown with CHECK CALLSIGN — instead of silently "not for us"). Residual errors are the model's "confidently wrong"
  share (15 %, [Y]); only readback/hearback and plausibility checks can catch those.
- **Missing words are shown as missing.** A dropout through the real channel and recogniser ("heading one night
  are zero descend and Maine take") gives HDG NOT RECEIVED and DESCEND NOT RECEIVED, callsign unsure — no value is
  completed from context.
- **Radar:** Doppler filtering alone leaves physical clutter that forms tracks (2953 / 2072 false track-scans); the
  clutter map plus a strict PSR-only initiation brings it to 3, and restores tangential and blind-speed targets over
  clear ground. SSR: validated codes 0.995 per scan with 0 wrong.
- **Approach guidance:** needles come from the independent ground source while it is valid and show the 25 m bias
  of the on-board source; with no valid source they are removed (10 frames in the script); after a ground-uplink loss
  the on-board fallback looks on path and only GND GUIDANCE LOST can be annunciated, not the bias.

## 8. Demo script (≈ 2 min) and safety limits

1. Open `outputs/scope_demo.html` (offline file). Press Play: labels come from decoded hex / pulse trains; NVA77 turns
   red "RADIO FAILURE" at 7600; one target is "PSR only, no transponder". Click a track; point at the hex → field
   panel and the ASTERIX line. (30 s)
2. Open `outputs/cockpit_demo.html`. The note line warns "Similar callsign on frequency: BTL132". Slider 20 s: "TURN
   LEFT HDG 270 / DESCEND 3000 FT", source and age; press **Confirm heard**. 46 s: a clearance for BTL132 was heard —
   not shown, one-line note only. 80 s: DEGRADED, "SPD 1?0 KT LOW CONFIDENCE" — the unsure digit is masked. 90 s:
   a partial transmission: "TURN RIGHT HDG 190 UNCONFIRMED", "DESCEND NOT RECEIVED", note "nothing is filled in". 150 s:
   RX_LOST, items STALE with age, SERA reminders. 172 s: ALTERNATE_AVAILABLE, "HDG 250" arrives **by CPDLC** (source
   shown). 220 s: ALL_COMMS_LOST. 252 s: recovered, a new voice clearance (ILS 25R, QNH 1013). (60 s)
3. PAR (H7): show `outputs/report.md` §5b — the talk-down transcript, "well above glidepath" calls on the biased
   aircraft, and "PAR GUIDANCE LOST (7 s)" after the voice drops at 100 s. (20 s)
4. Live speech: `python 03_Advionics/scripts/atc_live.py "beetle one two three cleared ils approach runway two five right" --snr 15`
   speaks the phrase with the Windows voice, passes it through the 300-3400 Hz channel at 15 dB, recognises and
   parses it (≤ 7 output lines). In our rehearsal it heard "runway **three** five right" and showed
   "ILS RWY ?? [LOW_CONFIDENCE]" — a real recognition error, withheld. `--text "..."` works without speech. (30 s)
5. Guidance (H5/H7): F7 + report §5c — the ground needle shows the aircraft 25 m high; V/L FLAG removes the needles
   for 10 s; GND GUIDANCE LOST while the on-board fallback looks on path. (20 s)

**Safety limits (say them before anyone asks):** advisory only, never commands the aircraft or the autopilot; never
creates, completes or "repairs" a clearance; a message lost on the channel cannot be reconstructed; recognised text is
unverified until the crew confirms by ear or readback is accepted; alternate channels count only if independent (bus,
antenna); not certified (DO-178C / DO-254 / ED-12C not attempted); recogniser is a desktop engine, not ATC-trained.

## 9. Mentor questions (ask in this order)

1. Is "translate signal" speech → text/display, or RF/radar signal → picture? (decides H1 vs H3) Is the guidance
   itself radar-based, like a PAR talk-down? (H7)
2. When comms are "lost", is it total loss, one-way (RX or TX), or degraded but audible?
3. Display for whom: the pilot (cockpit), the controller (scope), or both?
4. "Automated": automatic interpretation and alerting, or automatic flight guidance?
5. Which sources may we assume: VHF only, plus CPDLC/SATCOM, plus surveillance (SSR/ADS-B), PSR?
6. Which phase: approach and final only, or the whole terminal area?
7. What counts as success for you: Pd/false-alarm style numbers, latency, usability, safety argument?
8. Hardware (RF front-end, antenna) expected, or a software/system concept?
9. Is the guided vehicle a manned aircraft, a UAS (e.g. on a ship), or the inspection drone itself? (§15)

## 9b. Questions the jury may ask, with the answer we can defend

| Question | Answer (source) |
|---|---|
| "What if the recogniser is confidently wrong?" | It happened in our own test: runway 35R for 25R at 0.99 confidence. Confidence gates do not catch it; context does (runway list, octal squawk, valid 8.33 channel, climb/descend direction), and the crew's readback/hearback stays the barrier (§7, `test_confidently_wrong_runway_caught_by_context`). |
| "Why not just use CPDLC?" | It is the alternate, not the replacement: time-critical instructions stay on voice, voice watch remains with CPDLC (SERA.8035 [D-ag]), and the ATN B1 message set has no approach-clearance messages [D-ag C_EUROCONTROL_WikiLink_MessageSets]. Our display shows CPDLC items with their source. |
| "How do you know the link is lost and not just quiet?" | Silence alone never declares RX_LOST: it needs no carrier/traffic for 30 s **and** ≥ 2 unanswered calls; TX_LOST needs ATC asking "if you read…" twice while we hear the frequency (SERA.14083(b)(1): ATC checks the receiver with code change / IDENT [D]) or a failed TX self-test or a stuck PTT. Thresholds are [Y], tunable. |
| "What is your Pd / false alarm?" | Plot-level chain: PSR Pd 0.93/scan (EUROCONTROL 1997 recommends > 0.90 [D]), false PSR plots 3/scan (< 20 [D]). I/Q-level chain (report §5a): false plots/scan 450 / 55 / 39 / 3 (fixed / MTI / MTD / MTD + clutter map), false track-scans 2953 → 3 with strict PSR-only initiation; SSR codes 0.995 per scan validated, 0 wrong. Scene parameters are [Y]. |
| "Single-bit CRC correction — does it not create false messages?" | It repairs only syndromes of exactly one flipped bit outside the DF field; anything else is rejected. 96 of 608 messages repaired, 15 rejected at a 2e-3 bit error rate [K]. Measured: 20 000 of 20 000 random two-bit errors were rejected, none 'repaired' into a wrong message (`test_two_bit_errors_mostly_rejected_never_silently_wrong_dataframe`); three or more bit errors are not characterised, so plausibility checks (position jump, known ICAO) stay. |
| "Mode A or Mode C — how does the radar know?" | It does not from the reply: only the interrogation's P1–P3 spacing (8 µs A, 21 µs C [D]) tells; our decoder shows the same pulses as squawk and as altitude (`test_same_pulses_mean_different_things`). |
| "Why IMM?" | ARTAS (≈ 90 % of European flights) is built on an IMM-inspired design [D-ag]; in our turn the CV filter broke the ownship track into 5.8 ids per run, IMM into 2.0; P95 error 1093 m → 368 m [K]. |
| "Can a lost message be recovered?" | No. Not by ASR, not by AI. What we can do: show the last received item with its age, say STALE, point to SERA.14083, and accept a new message from an independent channel. |
| "Is this certifiable?" | Not as is: advisory display, DAL and DO-178C/ED-12C not attempted; the architecture keeps the crew in the loop and never sends anything to the autopilot, which is what keeps the assurance level low. |
| "How would Advionics/Intersoft test it?" | RES/RTG-style injection of SSR/Mode S/ADS-B and PSR targets with FRUIT and reflections (our `traffic.py` is a software stand-in), radar-vs-ADS-B comparison of bias and random error (our KPI table), SkyRF flying the approach for PAR/ILS, shadow mode. |

## 9c. Figures — datawiz gate

`outputs/F1…F7` (PNG + PDF + `.denetim.txt`), set `outputs/advionics.seti.json` (target `sunum-tam`): every figure
**0 HATA**; set consistency 0 HATA · 2 UYARI, both from F4, whose categorical state axis needs a wider left margin
and a category grid (accepted: the six state names are the content). Checked by eye: F1 (95 % Wilson bands), F3 (PSR
Pd vs range with the 0.9 line; the steady-target curve moved to the report table because its label collided with a
tick), F4, F5, F6 (log scale, dark marker edges), F7 (two annotation collisions fixed). Colour fixes made by the audit: palette yellow (1.3:1 on the background) and a 2.9:1 pink replaced or
direct-labelled.

| Figure | Claim it supports |
|---|---|
| F1 wrong values shown vs SNR | the masking/ambiguity/validation rules cut wrong-but-confirmed values by about an order of magnitude (model) |
| F2 withheld vs SNR | the price: more SAY AGAIN, ~100 % below 9 dB |
| F3 PSR Pd vs range | Swerling-1 targets of 2 / 10 m² cross Pd 0.9 at 24.8 / 37.1 NM with the illustrative budget [K] |
| F4 comm state timeline | the scripted approach walks through every state with evidence |
| F5 real-ASR threshold curve | with context checks 0 wrong values at any threshold; 0.95 only costs correct values |
| F7 vertical needle vs truth on final | the ground source shows the true deviation; needles are removed in the 10 s with no valid source; the on-board fallback hides its bias |
| F6 PSR false plots per scan by chain (log scale, 3 clutter-jitter levels) | the clutter-map chain stays at 1–12 false plots/scan at every jitter level, while MTI/MTD swing from ~1–3 (−60 dB) to 425–502 (−40 dB); at −60 dB MTI alone is marginally best (1.0 vs 1.2) |

## 10. HTML mock-ups — UX gate (ux-yasalari)

Budgets were written before the HTML (cockpit: 1 primary action "Confirm heard", 3 actions, 1 nav link; scope:
primary "Play", 3 actions, 1 nav link; ≤ 6 font sizes, 2 button styles, 1 accent). Checker
`node ux-yasa-denetimi.mjs cockpit.html` / `scope.html`: **0 HATA · 0 UYARI** each (static HTML). Live DOM checked
in the browser pane through a local server (`.claude/launch.json` entry `atc-demo`, port 8766): data load, labels,
state changes at 20/46/80/150/172/220/252/280 s; scope data-block overlaps over all 38 frames 4 → 0 after adding
four-position de-clutter; cockpit status colours fail a CVD simulation (green/amber/red), so every status is also
spelled out and border-coded (solid/dashed/double/dotted). The 20-row YASA DENETİMİ tables (and the `atc_live.py`
CLI check) are in `03_Advionics/outputs/ux_denetim.md`.

## 11. Environment, reproduction, verification

```powershell
$env:TEMP="D:\tmp_ideathon\advionics"; $env:TMP=$env:TEMP; $env:MPLCONFIGDIR="$env:TEMP\mpl"; $env:PYTHONPATH="src;D:\tmp_ideathon\pylib"; $env:PYTHONIOENCODING="utf-8"
python 03_Advionics/scripts/atc_day.py --asr        # report + figures + demo data (recognitions cached in outputs/asr_raw.json)
python 03_Advionics/scripts/atc_html.py             # offline single-file demos
python -m pytest -q tests/test_atc*.py --basetemp=D:/tmp_ideathon/advionics/pytest -p no:cacheprovider
```

- **pyModeS 3.6.1** installed to `D:\tmp_ideathon\pylib` (PyPI, well known) — only for cross-check tests; they skip
  when it is not on the path, so the full suite with `PYTHONPATH=src` does not need it.
- **Speech**: Windows System.Speech (built in; "Microsoft Speech Recognizer 8.0 for Windows (English - US)", voices
  Microsoft David/Zira). **No ASR package or model was downloaded.** A text-input path (`clearance.parse`) works
  everywhere.
- Live demo: `python 03_Advionics/scripts/atc_live.py "<phrase>" --snr 20` (or `--text "<phrase>"`). Found while testing: the
  desktop recogniser **rejects some clean full-band synthetic utterances** ("beetle one two three turn left heading
  two seven zero": rejected twice) but recognises the same audio after the 300-3400 Hz band limit at 30 dB
  (confidence 0.98); the script therefore always uses the channel model, which is also the honest demo.
- After regenerating: `python 03_Advionics/scripts/atc_doc_check.py` checks that the 44 computed values quoted here still appear
  in `outputs/report.md` (exit 1 otherwise).
- Studies: `atc_day.py --asr` re-scores cached recognitions; `--asr-fresh` re-records (~8 min); the PSR chain study
  is cached in `outputs/psr_chains.json`, `--psr-fresh` recomputes it (~15 min).

**Verified by this session [D]:** sponsor home page (doc 18); Sun (2021) pages for identification, airborne position,
velocity, surveillance replies and the book citation; pyModeS source (`_altcode.py`, `_bits.py`); Wikipedia SSR,
radar range equation, radar horizon; MathWorks Albersheim; EASA SERA.14083 (through a summarising fetch tool);
Icom IC-A24 8.33 kHz channel table; EUROCONTROL ASTERIX CAT048 Ed. 1.15 (PDF text); EUROCONTROL radar surveillance
standard 1997 §6.3–6.4 (PDF text); Zuluaga-Gomez et al. 2022 (arXiv abstract + PDF table); Nigmatulina et al.
2021 (arXiv abstract); code7700.com PAR page (secondary, quoting AIM/AFM). The FAA JO 7110.65 PAR section could
not be read (site refused the fetch tool; browser policy check failing). **Read only by agents [D-ag]:**
everything else in section 6 and the 120+ notes in `03_Advionics/research/`. **Snippet only [A]:** Mode A/C
reply-pulse patents; pyModeS paper bibliographic data.

## 12. Risks and open points

- The task may be none of H1–H7; the mentor questions come first on Friday morning.
- SERA.14083 changed in 2025 (20 min, 7601): many study materials still say 7 min; check the AIP of the State used.
- The word-level error model and all radar parameters are assumptions [Y]; no recorded ATC speech was used (ATCO2 /
  LiveATC have licence terms we did not check).
- 8.33 kHz naming checked only for 118.000–118.105 (pattern assumed to repeat).
- ASTERIX CAT048 implemented from the Ed. 1.15 PDF and compared with ed. 1.32 only through the asterix-specs
  rendering (no differences for our items); CAT021 ed. 2.7 from the same rendering, not the EUROCONTROL PDF.
- The I/Q PSR scene (terrain, wind farm, jitter) and all its numbers are assumptions [Y]; the chains show mechanisms,
  not equipment performance. Strict PSR-only initiation also hides hovering or very slow aircraft.
- The guidance panel cannot detect a bias in its only remaining source; it annunciates the loss of the independent
  one. PAR noise makes the disagreement monitor intermittent beyond ~4 NM.
- PAR: the 5 s transmission interval and the 5 s lost-communication rule rest on search summaries only (all FAA
  routes refused reading, 4 Nov, second attempt included) — present as "about 5 s"; `atc.par` keeps 5 s as a
  parameter (`ParGuidanceMonitor.lost_after_s`).

## 15. If the task is none of H1-H7: first hour

A fresh subagent played the Advionics engineer-mentor, read this doc cold and wrote five plausible task statements
outside H1-H7 (`03_Advionics/research/R_mentor_roleplay_2026-11-04.md`, all [Y]). What we would reuse in the
first hour, and what is missing:

| # | Statement (short) | Reuse in the first hour (module → demo) | Gap (more than an hour) |
|---|---|---|---|
| S1 | Ship-deck UAS recovery with the frigate's L-IESA-type IFF/Mode 5 array as the guidance sensor, no GNSS | `aerokit.autoland` EKF + solution-separation FDE with GNSS off and large elevation sigma; `atc.guidance` panel (needles removed when no valid source); `atc.radar` budgets; doc 18 P2 | moving deck frame (heave/pitch/roll), deck-motion prediction, L-band elevation error over sea, a short-range sensor for the last 200 m |
| S2 | Prove a new ILS/radar approach aid in tolerance with an automated drone (SkyRF-style) campaign before any flight check | `atc.ils` receiver (DDM, FLAG), `atc.par` measurement model, `aerokit.approach` geometry, F7-style plots; sponsor facts §2 | a signal-in-space model (DDM radiated at a point, beam bends), ICAO Doc 8071 / Annex 10 tolerances (not read), an acceptance statistic |
| S3 | Spoofed ADS-B / replayed Mode S on final: detect within seconds, keep a trustworthy picture, test with RES | `modes.encode_*` + `crc24` (valid CRC, false position), `traffic.Aircraft` events (ghost aircraft), **`atc.mlat` (added this round)**: TDOA fix + ADS-B consistency flag; tracker identity gating | NIC/NACp/SIL decoding, clock-sync model, a spoofer threat model, RES-style test plan |
| S4 | Design the uplink that carries radar-derived guidance as data: format, rate, latency, integrity, authentication, behaviour when messages stop | `atc.asterix` as a worked bit-exact format, `crc24`, `guidance.GuidancePanel` (GND GUIDANCE LOST after 5 s), `aerokit.comms` link budget / BER, `atc.datalink` | transport and loss/latency model, authentication |
| S5 | Verification and certification plan for an automated radar guidance station (RES/RTG injection, SkyRF, in-service monitoring, integrity argument) | KPI table in RASS vocabulary (report §5), `atc.psr_processing` chains, `traffic.Scenario` scenarios, `atc_doc_check.py`-style evidence discipline, §9b answers | requirements and hazard analysis; equipment-fault injection (calibration bias, latency, clock error); rare-event statistics (0 failures in ~3.0 × 10⁷ approaches to show 10⁻⁷ at 95 %, computed by the subagent and rechecked: ln(1/0.05)/10⁻⁷ = 3.0 × 10⁷ [K]) |

Recurring gaps across all five: a moving or arbitrary reference frame, equipment-fault injection, and (now closed)
multilateration. Fixed in this round: `atc.mlat` (5 tests) and a new mentor question (§9, question 9).

## 13. Round 2 (4 Nov, 21:10–00:45): what changed

1. **Primary radar at the I/Q level** (`atc/psr_processing.py`, `outputs/report.md` §5a, F6). Every range × azimuth
   cell gets a 16-pulse burst of noise, terrain clutter (45 dB, lognormal), a wind farm with Doppler spread and
   Swerling-1 aircraft. Four chains: fixed threshold, MTI (3-pulse canceller) + CFAR, MTD (Blackman-Harris Doppler
   bank, zero-velocity notch ±3 bins) + CFAR, MTD + recursive clutter map. CA-CFAR threshold: derived
   (α = N(Pfa^-1/N − 1), F(2L, 2NL) quantile for L looks) and checked by Monte Carlo. Results in this scene ([Y]
   parameters): false plots/scan ≈ 450 / 55 / 39 / 3 (jitter −50 dB). Full chain with the tracker: false track-scans
   in 38 scans — baseline random clutter 7; MTI 2953; MTD 2072; MTD + clutter map 49; + PSR-only 3-of-4 and ≥ 40 kt
   initiation **3**, with the no-transponder aircraft still tracked 36/38 scans. That aircraft is a live blind-speed
   case: its geometry gives a radial speed of about −53 m/s, next to the 53.5 m/s blind speed, so MTI and MTD
   never track it (0/38) while the clutter-map chain does (37/38). Lessons: physical clutter residue
   clusters and *forms tracks*; Doppler filtering alone is not enough; the clutter map also restores tangential and
   blind-speed (53.5 m/s) targets over clear ground; slow targets over terrain stay invisible (physics). Two of my
   own bugs were caught on the way and are recorded: a single-look CFAR multiplier on averaged MTI power (MTI saw
   nothing) and a ±1-bin notch inside a ±4-bin window main lobe (MTD ≈ 200 false plots).
2. **Mode S / ADS-B vectors.** Added surface position (TC 5–8): the book's pair (ref 51.990, 4.375) → 52.320607,
   4.734735; local → 52.320561, 4.735735; 17 kt, 92.8125° — all [D], read this round. CRC: 20 000 of 20 000 random
   two-bit errors rejected, none "repaired" into a wrong message. Vector table now 20 rows (`outputs/report.md` §1).
3. **ASTERIX.** Newest readable editions (asterix-specs rendering, rev 5cf64b6): CAT048 ed. 1.32 (2024-07-01)
   matches our Ed. 1.15 items and LSBs one to one (UAP FRN 1–14 identical; I048/090 confirmed *signed*; I048/140
   < 86 400 s). Added **CAT021 ed. 2.7** (ADS-B reports: 010, 040, 161, 071, 130, 080, 070, 145, 160, 170) with
   hand-checked FSPEC and two's-complement coordinates; the scope chain now also sends ADS-B tracks as CAT021
   (148 records in 5403 octets over the run; worst WGS-84 round-trip error 1.38 m against an LSB of ~2.4 m).
4. **"Not received", never fabricated.** New `<gap>` token and `NOT_RECEIVED` status: a keyword without its value,
   a value cut by a gap, or (in a transmission with a detected dropout) a value with too few digits shows
   "… NOT RECEIVED"; values that did arrive in a partial transmission show UNCONFIRMED; a homophone inside the
   callsign ("one to three") makes the call "callsign unsure", never "someone else's". Real audio, end to end:
   `atc_live.py "... heading one niner zero descend and maintain two thousand feet" --snr 25 --dropout 3.3:4.1` →
   grammar rejects, dictation fallback hears "... heading one night are zero descend and Maine take" →
   **TURN RIGHT HDG NOT RECEIVED | DESCEND NOT RECEIVED**, callsign unsure. Cockpit scenario: at 88 s a partial
   message shows HDG 190 UNCONFIRMED + DESCEND NOT RECEIVED with the note "Part of this transmission was not
   received (dropout) — nothing is filled in".
5. **PAR 5 s.** Still not readable from a primary source (FAA 403 on every route, browser policy check, Navy mirror
   certificate error); search summaries agree (≈ every 5 s; lost-comm action after 5 s on PAR final, 15 s on
   surveillance final, ≤ 1 min on vectors). Kept as [A], present as "about 5 s".
6. **SSR code validation (extra).** The chain now can decode 4 Mode A and 4 Mode C replies per scan (8 hits/scan)
   and accept a code only if ≥ 2 ungarbled replies agree. Measured at 3000 FRUIT/s: per-scan Mode A valid 0.874 →
   **0.995**, Mode C 0.832 → **0.995** (EUROCONTROL 1997 recommends > 98 % / > 96 %); the earlier 1 − (1 − p)⁴
   estimate (0.9997) was optimistic. At 10 000 FRUIT/s a single reply gives a **wrong** Mode A code 0.53 % of the
   time (> 0.1 % validated-false figure); validation brings it to 0.000 but validity falls to 0.82 — at that FRUIT
   rate a defruiter / Mode S is needed (`test_atc_traffic.py`).

## 14. Round 3 (4 Nov, 22:30–00:45): audit, dry run, guidance path

**Evidence audit** (fresh subagent, 12 values drawn with a seeded script; `03_Advionics/research/R_audit_2026-11-04.md`):
8 MATCH, 4 PARTIAL, 0 MISMATCH, 0 unreachable. All four partials fixed here: SERA.14083 (c)(6) 7601 wording (the
rule says an IFR flight that meets VMC and whose commander decides to continue in VMC — not "as VFR"; also fixed in
the cockpit reminder and the reference note); ARTAS described as "IMM-inspired design" (the four IMM modes belong to
the NLR research); Cardosi split by study (tower 1994 vs en-route 1993); PAR accuracy fixed terms added (elevation
6 m, azimuth 9 m, range 30 m) in the doc **and** in `par.par_measure` (larger of fixed and percentage term [Y]).
Side finding fixed: ETSI EN 300 676-1 V1.5.2 is dated 2011, not 2016.

**Dry run** (clean `powershell -NoProfile`, only the §11 environment line, 4 Nov 23:10, laptop):

| step (decision-card row) | command / page | time | result |
|---|---|---|---|
| H1 voice → display | `atc_live.py "... runway two five right" --snr 15` | 7.4 s (5.9 s after removing a redundant speech probe) | heard "three five right" → ILS RWY ?? LOW_CONFIDENCE — withheld |
| H2 partial transmission | `atc_live.py "... one niner zero ... two thousand feet" --snr 25 --dropout 3.3:4.1` | 8.0 s | HDG NOT RECEIVED, DESCEND NOT RECEIVED, callsign unsure |
| H6 other aircraft | `atc_live.py --text "beetle one three two ..."` | 0.5 s | NOT for us — not shown |
| H2/H4 replay | `outputs/cockpit_demo.html` (served) at 20/46/90/150/172/220/252 s | load 0.4 s, 3 ms per frame | every state of §8 appears at its time |
| H3 radar | `outputs/scope_demo.html` (served), all 38 frames | load 0.2 s, 5 ms per frame | labels, 7600 alert, CAT048 line |
| rebuild demos | `atc_html.py` | 0.3 s | — |

One thing to know: the browser pane of the desktop app shows local `file://` pages as static snapshots, so the
inline data does not run there; a normal browser opens the `outputs/*_demo.html` files directly, and
`python -m http.server 8766 --directory 03_Advionics` works everywhere. Regenerating everything
(`atc_day.py --asr` with caches) takes 25–60 s; `--asr-fresh` adds ~8 min, `--psr-fresh` ~15 min.

**Approach guidance end to end** (`atc/guidance.py`, report §5c, F7). Voice clearance "cleared ILS approach runway
two five right" (parser → advisory display) + ground PAR measurement up-linked every second + on-board source →
needles, distance, height, glide path, MINIMUMS. Scripted failures and what the pilot saw:

| condition | annunciation (when, s) | needles |
|---|---|---|
| clearance not yet received | NO APPROACH CLEARANCE (0-19) | drawn, labelled advisory |
| biased on-board source vs ground radar | SOURCES DISAGREE (most of the run; intermittent beyond ~4 NM where the PAR error is ~30 m) | from the ground source, showing the true ~25 m high |
| ground uplink stops at 120 s | GND GUIDANCE LOST (125-149) | on-board fallback — looks on path, bias not detectable alone |
| on-board PL > alert limit 135-145 s | NAV INTEGRITY + V FLAG + L FLAG (135-144) | **removed** (10 frames), never centred |
| decision height | MINIMUMS (206-216, latched) | crew decides |
