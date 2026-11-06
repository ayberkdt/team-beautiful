# Case catalog — Advionics "Automated Approach Guidance" (reveal day: Fri 6 Nov morning)

Likelihood is our judgement [Y] from the organiser note ("Radar Expertise", "İletişim kesilirse", "Translate signal",
"[voice] sinyal display'e nasıl ulaşır"; speaker said *voice, radio, translate*) and the sponsor profile
(`research/S_00_summary.md`). Trigger weights used by the triage tool: `cases/triage_keywords.json`. Numbers: each
case's `outputs/result.md` (full runs of 5 Nov). Every runner: `python 03_Advionics/cases/<case>/run.py [--quick]
[--set name=value] [--params mentor.json] [--out dir] [--no-fig]`.

| Case | Trigger words (top) | Likelihood [Y] | Code entry point | Figure (outputs/) | Demo | Time to adapt [Y] |
|---|---|---|---|---|---|---|
| 1 voice → display | voice, speech, transcribe, translate, VHF, clearance, ses/telsiz | high | `case_1_voice_to_display/run.py` → `atc.translate.voice_sweep/voice_trace`, `atc.clearance` | C1 wrong values vs SNR (conservative 5–14 vs naive 30–53 per 1000) | `scripts/atc_live.py "..." --snr 15`; `outputs/cockpit_demo.html` | 15 min (phrases/SNR in params) |
| 2 lost comms | communication lost, radio failure, 7600, degraded, backup, kesilirse | high | `case_2_lost_comms/run.py` → `atc.commhealth`, `atc.lostcomm` | C2 comm-state timeline (0 unreceived items shown) | `cockpit_demo.html` 88–252 s | 15 min (timings, rule set) |
| 3 radar signal → display | radar, PSR, SSR, Mode S, ADS-B, plots, tracks, ASTERIX, clutter | high (sponsor core) | `case_3_radar_signal_to_display/run.py` → `atc.translate.adsb_trace/modes_ber_outcomes`, `atc.traffic` | C3 Mode S outcome vs BER (0 of 18 000 wrong) | `outputs/scope_demo.html` | 20 min |
| 4 PAR talk-down | precision approach radar, talk-down, GCA, glide path, voice guidance | high (fits every note word) | `case_4_par_talkdown/run.py` → `atc.par`, `aerokit.approach` | C4 PAR vs truth + LOST band | report §5b, F7 | 20 min |
| 5 GNSS-independent approach | without GNSS, jamming, autoland, ship deck, integrity, LPV | medium-low (pre-reveal guess) | `case_5_gnss_independent_approach/run.py` → `aerokit.approach` | C5 95 % gate error per source vs VAL 35 m | `prev_guess/03_Advionics/scripts/approach_day.py` | 30 min (sensor list) |
| 6 flight inspection (drone, ILS) | flight inspection, ILS, localizer, DDM, drone, SkyRF, tolerance | medium-low | `case_6_flight_inspection_ils_drone/run.py` → `atc.ils` | C6 DDM vs truth with FLAG bands | `tests/test_atc_ils.py` | 30 min (+ tolerances from mentor) |
| 7 readback + callsign correlation | readback, hearback, callsign, similar callsign, wrong aircraft, correlate | medium | `case_7_readback_correlation/run.py` → `clearance.readback_check/resolve_callsign` | C7 alerts vs SNR (81 % caught, 33 % of alerts real @ 30 dB) | `atc_live.py --text "beetle one three two ..."` | 20 min |
| 8 surveillance integrity (spoofing, IFF) | spoof, fake, ghost, MLAT, WAM, authentication, Mode 5, IFF | low-medium | `case_8_surveillance_integrity/run.py` → `atc.mlat`, `atc.modes` | C8 detection vs offset (≥ 99 % from 150 m, 0 % false) | — | 30 min; Mode 5 is a gap |
| 9 guidance uplink as data | uplink, data link, message format, latency, time to alert, messages stop | low-medium | `case_9_guidance_uplink/run.py` → `atc.uplink`, `atc.guidance` | C9 nuisance LOST vs loss rate per timeout | — | 30 min |

Shared slides for every branch: the chain (signal → detection → decoding → validation → display, where it breaks) and
the rule ("the display shows only what was received, with source and age; a lost message is never reconstructed").
Standards and formats to quote: `cases/CATALOG_standards.md`. Procedure on the day: `cases/REVEAL_DAY.md`.
