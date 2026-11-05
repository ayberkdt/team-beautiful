# EASA kanopi — evidence catalogue (index)

Challenge: EASA "Canopy alert system retrofit" (notes: `research_notes/final_2026_notes/03_EASA_Canopy_Alert_Retrofit.md`).
Built 4 Nov 2026 by the EASA canopy session. One file per source or source group, each with URL, what was read
(page/section), date read and who read it.

**Who read what.**
- `R0_*` files were read by the **main session**; their facts are tagged [D].
- `R1`–`R4` files were read by **subagents**; their facts are tagged [D-ag].
- `R0_spot_checks_of_agent_work.md` lists 11 agent claims that the main session re-read. All 11 were confirmed.

Downloads (untrusted data, outside the repo): `D:\tmp_ideathon\easa\dl\{aaib,std,reg,occ,cert,hf,spot}\`.

| File | Source(s) | Read by | Key content |
|---|---|---|---|
| `R0_AAIB_G-MIIL_report.md` | AAIB-28120, Bulletin 4/2024, 28 pp. | main, in full | timeline, mechanism (3 bolts, 60/70 mm, forces), cause, SR 2024-004/005, BFU dissent |
| `R0_EASA_AD_2025-0156_and_PKBWL_2023-0061.md` | EASA AD 2025-0156 (3 pp.); PKBWL 2023-0061 (8 pp.) | main, in full | "in most cases a partially or improperly locked canopy"; SP-HMM partial engagement; ECOs |
| `R0_AAIB_SR_responses_2024-2025.md` | AAIB SR response document, updated 29 Jan 2025 | main, in full | 2024-004 open (NDT, BFU scenario considered); 2024-005 closed (latching improvement offered) |
| `R0_PKBWL_2022-1097_SP-HMM_first_event.md` | PKBWL 2022/1097 (10 pp.) | main, in full incl. conclusions | loose rear fitting, vibration precursor, no recorder, pawls found 'locked' after detachment |
| `R0_Extra_SB-NG-2-22_and_FAA_AD_2026-04-12.md` | Extra SB-NG-2-22A (7 pp.), SB-NG-1-22A, SL-NG-2-22A; FAA AD 2026-04-12 final rule | main, in full | SB applicability excludes NG026 (conflicts with AAIB p. 12); step 19 partial-lock wording; foam can block the latch; FAA $95/aircraft, 30 US aircraft; SB-NG-1-24 not obtainable (manufacturer site blocks automated requests) |
| `R0_NUREG_CR-1278_omission_HEPs.md` | Swain & Guttmann NUREG/CR-1278 Table 20-7 | main | omission HEP 0.001–0.01 per item, 0.05 if procedure not used (grounds p_partial) |
| `R_audit_2026-11-04.md` | independent audit: 15 random rows + 10 random doc-23 statements re-opened at source; corrections log | audit subagent + main | field error 1.5 % (0.4–5.2 %), all mismatches fixed |
| `R0_Honeywell_GAPS_proximity_sensor.md` | Honeywell GAPS/HAPS datasheet Tables 1–2 | main | < 60 g, < 10 mA, ≤ 3.5 mm sensing, MTBF 500 000 FH (vendor) |
| `R0_NASA_fault_tree_handbook.md` | NASA FTH v1.1 (2002) §7, App. B | main, partial | gate algebra, ½λT, importance measures (used in code) |
| `R0_FAA_AD_2010-25-01_DA40_door_annunciation.md` | FAA AD 2010-25-01, Fed. Reg. 75:75868–69 | main, comment sections | shared canopy/door light ignored during open-canopy taxi: field cry-wolf case |
| `R0_spot_checks_of_agent_work.md` | AD, PKBWL, exida, AAIB G-FLOR, NTSB-008, CS-STAN CS-SC110a | main | 11/11 agent claims confirmed (incl. AC 23.1309-1E, Bliss abstract, CS 23.783(e), two R5 rows) |
| `R1_aaib_safety_recs.md` | AAIB SR document (updated 29 Jan 2025); EASA annual SR reviews | R1 | SR 2024-004 open "partially adequate"; 2024-005 closed |
| `R1_easa_ad_2025-0156.md` | AD, PAD 25-017, comment-response document | R1 | compliance, pilot-owner, NG065+ |
| `R1_faa_ad.md` | FAA AD 2026-04-12 (Federal Register) | R1 | 30 US aircraft, ~$95 each |
| `R1_extra_ng_canopy_design.md` | TCDS EASA.A.620; PKBWL 2022/1097 pp. 6–8; SB-NG-2-22 | R1 | mechanism, jettison, no electrical warning on the type |
| `R1_caa_easa_bulletins.md` | CAA Safety Sense, MPD 2022-003 (Europa), EASA SIBs | R1 | no dedicated GA canopy leaflet; Europa mechanical-stop fix |
| `R2_occurrences.csv` | 146 occurrences (NTSB 88, AAIB 40, BEA 11, SUST 4, others 3), URL per row | R2 | dataset; 77 lock-related, 49 of those in initial climb |
| `R5_occurrences_add.csv` | 95 more occurrences (round 2): NTSB 62, BFU 14, BEA 10, PKBWL 8, AAIB 1; same schema, URL per row; no duplicates (round 3 fixed a merge key that had dropped one BFU row) | R5 | merged total 241 rows; 126 lock-related, 76 in initial climb |
| `R5_occurrences_add_sources.md` | queries, counts kept/excluded, leads, verified statistics (e.g. BFU 2022 study: 5 of 24 microlight component-failure cases were canopy/door openings, p. 42) | R5 | gaps: ATSB timeout, TSB 403 |
| `R2_occurrences_sources.md` | queries, statistics with pages, de-duplication | R2 | Europa 8 events; WT9 ≥ 12; DA20 3; Pitts under-reporting |
| `R3_cs23_astm.md` | CS-23 Amdt 4 and Amdt 6 + AMC; eCFR 23.783/1322/2605, 25.783 | R3 | 23.783(e)(3) forward-of-prop only; colours; egress |
| `R3_part21_changes_csstan.md` | Part 21 EAR (Nov 2025); CS-STAN Issue 4 | R3 | minor-change route; CS-SC110a |
| `R3_partml_ica_mel.md` | Part-ML, Part-66, Air Ops (NCO), UK | R3 | release to service, ML.A.403 deferral, MEL optional |
| `R4_alerting_human_factors.md` | AC 25.1322-1, AC 23.1311-1C, HF abstracts (Bliss, Wickens, Dixon, Dehais…) | R4 | cry-wolf, probability matching, inhibits, aural specs |
| `R4_sensor_failure_rates.md` | MIL-HDBK-217F N2, exida/P+F, Honeywell GAPS | R4 | λ tables (machine-readable) |
| `R6_hf_full_texts.md` | open full texts: NUREG/CR-1278, Degani & Wiener 1990, Dismukes & Berman 2010, FAA TC-07/22, Dehais 2019, Callan 2018, NTSB ERA10LA221/SEA01LA058; list of papers that stayed closed | R6 | omission rates, missed aural tones in real flight 38 %, ATC nuisance 81–87 % |
| `R4_do160_wiring.md` | AC 21-16G (DO-160G section list), AC 43.13-1B, Extra lookbook | R4 | DO-160 sections, wire/CB sizing |

**Gaps (searched, not obtained).**
- Not obtained: the Extra NG POH/AMM, SB-NG-1-24 text, ECO-NG-22-09/23-07, AI-NG-02-23, the DO-160G text, and the ASTM
  standards (paywalled).
- Full HF papers: only abstracts were read. The PKBWL 2022/1097 report itself was read by R1 only.
- BGA, TSB and ATSB statistics were not reachable. No BFU rows were found. The DA40 TCDS was not read.
