# R0 · Spot checks of subagent work by the main session (4 Nov 2026)

Purpose: the user rule says agent-read facts are [D-ag]; these re-reads test whether the agents' reading can be trusted.

| Claim (agent) | Re-read by main session | Result |
|---|---|---|
| R1: EASA AD 2025-0156 reason = "in most cases" partially/improperly locked canopy; placards + AFM rev. 16; no warning required | AD PDF pp. 1-3 in full (`R0_EASA_AD_2025-0156_and_PKBWL_2023-0061.md`) | confirmed |
| R1: PKBWL 2023-0061 — BFU/TCH: pawls only partially engaged; ECO-NG-22-09/23-07; NG061+; AI-NG-02-23 | PKBWL PDF pp. 1-8 in full (same note) | confirmed |
| R4: exida P+F NAMUR sensors 15.4 FIT safe / 9.63 FIT dangerous, Table 2 | `pf_cert0707.pdf` p. 3 Table 2; also found: with fail-safe (line-monitoring) interface 24.9 / 0.09 FIT (p. 4), SN 29500 basis | confirmed (+ new fact) |
| R2 row AAIB-25 G-FLOR Europa: 8th UK Europa door event; door detached at ~2 500 ft / 100 kt; lever can close with only the front shoot bolt engaged | AAIB Bulletin 1/2022 PDF (downloaded to `D:\tmp_ideathon\easa\dl\spot\flor.pdf`), lines on p. 1 ("eighth event") and analysis ("false impression that the door is closed and fully latched") | confirmed |
| R2 row NTSB-008 N3950L Grob G102 glider, 11 Jul 1987: canopy found unlatched, 1 fatal, destroyed | CAROL PDF (`n8.pdf`, 5 pages): "GLIDER CANOPY WAS FOUND UNLATCHED", 1 fatal, destroyed | confirmed |

Not re-read: the other 144 R2 rows, R3 regulatory paragraphs, R4 HF abstracts and MIL-HDBK-217F page images (OCR of the 217F scan is unreadable here; the agent read page images).
| R3: CS-SC110a "Installation of annunciators" covers new warning/caution/advisory lights; "canopy status" listed as a typical repeater; awareness only; not releasable by pilot-owner | CS-STAN Issue 4 (27 Apr 2022, Annex to ED Decision 2022/009/R) pp. 128–131, read in full from `D:\tmp_ideathon\easa\dl\cert\CS-STAN_Issue4.pdf`: §1 purpose incl. new warning/caution/advisory lights; §2 eligibility non-complex aeroplanes + ELA2; §3 AC 43.13-1B ch. 10–12 / ASTM F2639, F2490 load analysis, circuit protection, same bus bar as monitored system, red/amber/green colours; Config 2 note lists "canopy status"; §4 "for awareness only in Configurations 1 and 2"; §5 AFMS + ICA; §6 "not suitable for the release to service of the aircraft by the pilot-owner" | confirmed |
| R4: AC 23.1309-1E — Class I per-FH ceilings minor < 1e-3, major < 1e-4, hazardous < 1e-5, catastrophic < 1e-6; "No probable failure should result in a 'safe' indication of an 'unsafe' condition" | `D:\tmp_ideathon\easa\dl\hf\ac23_1309_1e.pdf` text: Figure 2 table rows (PDF p. 25) and §11.b sentence (text line 891) | confirmed |
| R4: Bliss, Gilson & Deaton 1995 abstract — ~90 % probability matching, ~10 % all-or-none; 25/50/75 % true-alarm conditions; 138 students | OpenAlex abstract saved by R4 (`openalex_hf.txt` line 2) | confirmed (abstract level only) |
| R3: CS 23.783(e)(3) visual "not fully closed and locked" warning applies only to doors forward of any engine or propeller (normal/utility/aerobatic) → voluntary on the Extra NG | EASA Easy Access Rules CS-23 Amdt 4 (Jun 2018) pp. 170–171, `D:\tmp_ideathon\easa\dl\cert\EAR_CS23_A4.pdf`: (e) "each external door forward of any engine or propeller on a normal, utility, or aerobatic category aeroplane"; (e)(3) visual warning + "erroneous closed and locked indication is improbable" | confirmed (2nd round) |
| R5 row R5-001 N50BS Globe Swift GC-1B, 10 Oct 1982: right side of canopy separated on take-off; pilot believed front pin engaged | NTSB CAROL PDF 70584 (`D:\tmp_ideathon\easa\dl\spot\r5_001.pdf`): "DURING TAKEOFF, THE RIGHT SIDE OF THE CANOPY SEPARATED"; "THE PILOT BELIEVED THAT THE FRONT CANOPY PIN WAS ..." | confirmed (2nd round) |
| R5 row R5-074 Grob G103 C Twin III Acro, 23 Jun 2021, BFU 21-0469-3X: video shows front-canopy lock lever unlocked through the winch launch; canopy opened ~30 m on final; fatal | BFU report PDF (12 pp., `bfu0469.pdf`): lever "senkrecht" → "nicht verriegelt" (Abb. 1–2, witness video); "etwa 30 m über Grund, öffnete sich die vordere Cockpithaube"; the pilot tried to close it | confirmed (2nd round) |
| R3: CS 23.807(b)(5) aerobatic aeroplanes must allow each occupant to abandon the aeroplane at any speed between VSO and VD | EAR CS-23 Amdt 4 (Jun 2018) p. 175, `EAR_CS23_A4.pdf`; (b) also lists "canopies" as acceptable emergency exits | confirmed (round 3) |

## Round 4 — R7 notes (5 Nov 2026, main session, files read with grep/pdftotext from `D:\tmp_ideathon\easa\dl\r7_*`)

| Agent claim | What the main session read | Result |
|---|---|---|
| R7-sensing/visual/aural: G3X "Canopy Closed" input — solid yellow CANOPY OPEN; flashing red + alert tone when engine power is increased or airborne | `r7_visual/garmin_190-01115-01_az.txt` lines 27104–27109 and 36599–36602 (G3X Touch install manual Rev AZ) | confirmed |
| R7-sensing: Garmin recommends wiring the grounded state as the normal (canopy closed) state against broken wire/microswitch | same file, lines 19578–19581 (note 13) | confirmed; that the scheme cannot see a short to ground is the agent's (and our) inference |
| R7-sensing: NTSB CEN23FA359 RV-14 — micro switch installed so it signalled a closed canopy before the pins were fully seated; probable cause | `r7_sensing/CEN23FA359.pdf` (pdftotext) lines 49–50, 66–68, 77–80; one switch on the left frame per Van's instructions (l. 258) | confirmed |
| R7-aural: Patterson CAA 82017 — 10 dB above threshold "easy to detect", 15 dB "difficult to miss"; on propeller aircraft components below 1.0 kHz "essentially useless" | `r7_aural/patterson_caa82017_cam.txt` lines 639–642, 2054–2057, 1266–1270 | confirmed |
| R7-visual: HF-STD-001B — flashing red for emergency conditions, about equal on/off, 3 to 5 flashes per second (§5.4.2.1.1.5) | `r7_visual/hfstd001b.txt` lines 12085–12090 (and the same rule as §5.4.2.2.1.29, line 12338) | confirmed (the main session first thought the section number was wrong; it was not) |
| R7-visual: AC 23.1311-1C Table 3 Note 4 — warnings/cautions within 15°; up to 35° acceptable with a unique aural tone or a master warning within 15° | `r7_visual/ac_23_1311-1C.txt` lines 1663–1667 | confirmed; the 35° clause matters for a rear-seat lamp |
| R7-interlock: our catalogue — initial climb 9 fatal of 76 (11.8 %), take-off roll 0 of 17, total 16 of 126 | recomputed by the main session from `R2_occurrences.csv` + `R5_occurrences_add.csv` via `canopy_day.load_occurrences()` (cause_class not_locked + partially_latched) | confirmed |
| R7-interlock: Nall 2002 — 16.8 % (32 of 191) of single-engine fixed-gear take-off/climb accidents fatal | `r7_interlock/AOPA_02nall.pdf` (pdftotext) line 233 | confirmed — note: all take-off/climb accidents, not engine-failure accidents only |
| R7-interlock: BEA 2015–19 power loss at take-off — turn-back 10 of 18 fatal, axis held 0 of 9; "13 of 68 = 19 %" | `r7_interlock/BEA_reduction_power_TO.pdf` (pdftotext) lines 288–299 (table), line 35 "All 12 fatal accidents in the sample", line 142 "of the 68 accidents identified" | table confirmed; 13/68 is the agent's arithmetic (tagged [Y] in R7), BEA itself states 12 fatal in its analysed sample |
| R7-interlock: HVBG 2006 — about 37 % of machine guards manipulated | `r7_interlock/HVBG_manip_k1-4.pdf` (pdftotext) line 340: "Nach Einschätzung der 940 Befragten sind knapp 37 % der Schutzeinrichtungen … manipuliert" | confirmed — note: a respondents' estimate, not a measured count |
| R7-haptic: Meng 2015 — high-intensity hand cue 22.3 % (SE 4.3 %) vs low-intensity 4.2 % | `r7_haptic/epmc_PMC4512524.txt` | confirmed |

Not re-read: Politis 2016 thesis numbers (read online by the agent, not downloaded), ISO 7731 sample text, NAMUR levels, products and prices.

## Round 5 — R8 notes (5 Nov 2026, main session; grep on the agents' local copies under `D:\tmp_ideathon\easa\dl\r8_*` and `txt_r8`)

| Agent claim | What the main session read | Result |
|---|---|---|
| R8-timing: AC 25-7D §4.3.6.4 — Δtact1 is the demonstrated time from engine failure to the first pilot action; AFM expansion uses the longer of 1 s or the test time | `r8_timing/AC25-7D.txt` lines 2748–2752 and 5104–5108 | confirmed |
| R8-timing: Landman 2017 — response time 2.02 s (expected) vs 4.12 s (surprise) | `r8_timing/landman2017.txt` lines 495–500 (Table 3) | confirmed |
| R8-timing: our catalogue — median climb-opening height 200 ft, 42 % ≤ 100 ft (26 rows with a stated height) | agent's script output `scratchpad/r8/timeline_calc_output.txt`, list of 26 parsed heights and 4 exclusions shown | arithmetic confirmed; parse of free-text notes not re-done |
| R8-latches: Duo Discus — "handle in locked position but not connected with the fuselage pins" | `r8_latches/EASA_AD_2024-0059_DuoDiscus.txt` line 63 | confirmed |
| R8-latches: CAP 232 F-HKAP — canopy can be locked in a slightly-open position | `r8_latches/BEA_F-HKAP_CAP232_EN.txt` lines 91–95 | confirmed |
| R8-latches: L-39 G-OALB — handle can be stowed regardless of whether the canopy is locked | `r8_latches/AAIB_G-OALB_L39_4-05.txt` line 92 | confirmed |
| R8-latches: Pitts G-IIDY — horn on the locking lever silent; lever locked but canopy not engaged on the fuselage | `r8_latches/AAIB_G-IIDY_Pitts_S2B_3-11.txt` lines 33–47 | confirmed |
| R8-latches: Europa MPD 2022-003 — rear tapered shoot bolt not engaged, only the forward one | `r8_latches/CAA_MPD_2022-003_Europa.txt` lines 53–55 | confirmed |
| R8-systems: EASA AD 2011-10-13 — more than 30 in-flight rear-door losses on Diamond aircraft since 2004 | `r8_systems_cost/2011-11267.raw.txt` line 13 | confirmed |
| R8-systems: NTSB A-89-93 — positive indicators of latch cams and locks, independently | `r8_systems_cost/AAR92-02.txt` lines 3448–3451 | confirmed |
| R8-systems: Lie 2008 — belt use 97.5 % with reminders vs 85.8 % without | `r8_systems_cost/epmc_lie.json` (abstract) | confirmed (abstract) |
| R8-systems: AC 25.703-1 — nuisance warnings must be eliminated, they lead crews to disable the system | `r8_systems_cost/AC25-703-1.txt` lines 273–306 | confirmed (wording paraphrased) |
| R8-mechanical: AAIB AAR 1/2015 (A320 G-EUOE) — earlier fan-cowl measures "only partially effective": ~50 % reduction, 1 per 1.28 M to 1 per 2.42 M flight cycles | `txt_r8/G-EUOE.txt` lines 4212–4218, 4245 | confirmed |
| R8-mechanical: A320 fan-cowl latch key "cannot be removed unless the FCD front latch is safely closed", stowed in the flight deck | `txt_r8/FR_2018-09277.txt` lines 57–63 | confirmed |
| R8-mechanical: DC-10 vent-door linkage could be forced closed with about 120 lb on the handle | `txt_r8/AAR73-02.txt` line 582 | confirmed (OCR text) |

Not re-read: Cessna 172R POH p. 7-18 control-lock flag over the ignition switch (agent read it online), cost-tier labour estimates, part prices.

## Round 6 — R9 notes (5 Nov 2026 evening, main session; pdftotext/grep on `D:\tmp_ideathon\easa\dl\r9_*`)

| Agent claim | What the main session read | Result |
|---|---|---|
| R9-extra: Extra's own documents say the NG is equipped with a Garmin G3X Touch (GEA 24) | `r9_extra/SL-NG-01-22.pdf` line 17: "The EXTRA NG is equipped with a Garmin G3X Touch system"; line 26/41 GEA 24 | confirmed; conflicts with AAIB-28120 fn. 1 "Garmin manufactured G1000" for G-MIIL (re-read earlier [D]) — unresolved, design covers both |
| R9-extra: GMA 245R audio panel; traffic audio moved to ALERT 1 IN | `r9_extra/SL-NG-03-22.pdf` lines 13–28 | confirmed |
| R9-extra: SB-NG-1-24 is a placard SB (initial design up to NG064 / canopy 071), to reduce misuse of the canopy locking; POH Rev 16 update | `r9_extra/SB-NG-1-24.pdf` pp. 1–2 (text lines 4–31, 40–75) | confirmed; the "large green circle" reading comes from Fig. 1 (image), not re-checked |
| R9-extra: Extra 300 D-EFBY flight manual — ground roll 105 m at 950 kg | `r9_extra/BEA2016-0092.pdf` line 63 | confirmed |
| R9-precedents: AC 25.783-1A — single indication that directly monitors closed, latched and locked; erroneous indication ≤ 10⁻⁵ | `r9_sensing_precedents/AC_25_783-1A.txt` lines 625, 663 | confirmed |
| R9-precedents: FAA memo — indication must monitor closed, latched and locked positions "directly" | `Transport_Airplane_Directorate_Memorandum.txt` line 88 | confirmed |
| R9-precedents: DA40 PH-TIN — the front locking pin's aft movement operates one micro switch | `2011051_ph_tin_eng.txt` line 156 | confirmed (the "13 minutes" detail not re-read) |
| R9-precedents: fretting — tin contact from 1 mΩ to > 1 Ω in < 20 min at 10 cycles/min; gold not susceptible | `Gold-vs-Tin-for-Use-In-Contact-Applications.txt` lines 29–41 | confirmed |

Not re-read: AOPA 2020 flight-test numbers (80 KIAS lift-off, 40 KIAS tail-up; read online by the agent), GAPS grey band and Crouzet hysteresis values (R9-physics), Honeywell IHM and Safran patent wording.

## Round 7 (5 Nov 2026, evening): R10 vibration keep-or-drop

| # | Claim in R10 | Checked at | Result |
|---|---|---|---|
| 47 | 14 CFR 23.1141(c): each control must maintain any necessary position without "(2) Tendency to creep due to control loads or vibration" | eCFR point-in-time 2017-03-01, section 23.1141 (WebFetch, main session) | CONFIRMED, words identical |
| 48 | Zhu et al. 2025 (Appl. Sci. 15:527) Table 2: visual-auditory vs visual-auditory-tactile g = 0.54 (−0.49, 1.57), not significant; auditory vs auditory-tactile g = 0.38* (0.04, 0.72) | the article PDF, p. 9, Table 2 (PyMuPDF text, main session) | CONFIRMED. Note: "not significant" with a CI this wide means the benefit is not shown, not that it is zero (only 67 failsafe-N, few studies) |

## Round 8 (5 Nov 2026, ~20:40): report reference check (refcheck A)

| # | Claim | Checked at | Result |
|---|---|---|---|
| 49 | Report: "on SP-HMM the pawls were 'engaged only partially' [PKBWL]" | PKBWL 2023-0061 PDF p. 6, §3.1 Findings 1 and 6 (main session, PyMuPDF) | **REFUTED as worded.** Finding 1: "BFU and the aeroplane manufacturer (being TCH) deemed that the cockpit canopy pawls were engaged only partially". Finding 6: the three pawls "remained intact and in the 'Locked' position". The partial engagement is the BFU/TCH opinion, not a PKBWL finding. Earlier notes and the report wording overstated it. |
| 50 | Report: "a partly locked canopy shows no gap at the frame edge [AAIB pp. 9, 20]" | AAIB-28120 PDF p. 20 | **Wording off.** p. 20: "no observable visual differences between where the canopy frame and fuselage edges meet, when in the fully locked or partially locked condition". p. 9 confirms 70 mm for open-released and locked. |
| 51 | AAIB-28120 names a G1000 for G-MIIL | AAIB PDF p. 3, footnote 1 "Garmin manufactured G1000" | CONFIRMED; conflicts with Extra SL-NG-1-22 (G3X Touch). Still unresolved. |
| 52 | AC 25.783-1A asks for direct monitoring of "each lock" with a false "locked" ≤ 10⁻⁵ | AC 25.783-1A PDF, §12 text (main session) | **Overstated.** The AC asks for "a single indication that directly monitors the door in the closed, latched, and locked conditions"; the ≤ 10⁻⁵ applies to "erroneous closed, latched, and locked indication" for listed transport doors; elsewhere the locking means "need not directly monitor ... each latch". Report wording fixed via the report session. |
| 53 | GAPS sensing distance 3.5 mm max | Honeywell datasheet 000843, product table (main session) | CONFIRMED as the table value; the guaranteed actuation curve (Fig. 3) is lower (agent reads ~2.5 mm; graph, not re-measured). |
