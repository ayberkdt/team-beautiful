# Triage plan (dry run)

Created 2026-11-05T22:25:41; destination for moved items: `D:\Masaustu\Ideathon 2026\prev_guess\03_Advionics\2026-11-05_unused`.

## Ranking

| # | Case | Score | Kept | Matched (count) |
|---|---|---|---|---|
| 1 | case_2_lost_comms | 11.5 | yes | if communication (1), tower is lost (1), is lost (1), lost (1) |
| 2 | case_1_voice_to_display | 7 | yes | voice (1), translat* (1), cockpit (1), display* (1) |
| 3 | case_3_radar_signal_to_display | 0 | no | - |
| 4 | case_4_par_talkdown | 0 | no | - |
| 5 | case_5_gnss_independent_approach | 0 | no | - |
| 6 | case_6_flight_inspection_ils_drone | 0 | no | - |
| 7 | case_7_readback_correlation | 0 | no | - |
| 8 | case_8_surveillance_integrity | 0 | no | - |
| 9 | case_9_guidance_uplink | 0 | no | - |

## Would move (25)

- `cases/case_3_radar_signal_to_display` — only used by case_3_radar_signal_to_display
- `cases/case_4_par_talkdown` — only used by case_4_par_talkdown
- `cases/case_5_gnss_independent_approach` — only used by case_5_gnss_independent_approach
- `cases/case_6_flight_inspection_ils_drone` — only used by case_6_flight_inspection_ils_drone
- `cases/case_7_readback_correlation` — only used by case_7_readback_correlation
- `cases/case_8_surveillance_integrity` — only used by case_8_surveillance_integrity
- `cases/case_9_guidance_uplink` — only used by case_9_guidance_uplink
- `outputs/F3_psr_pd_vs_range.denetim.txt` — only used by case_3_radar_signal_to_display
- `outputs/F3_psr_pd_vs_range.dw.json` — only used by case_3_radar_signal_to_display
- `outputs/F3_psr_pd_vs_range.pdf` — only used by case_3_radar_signal_to_display
- `outputs/F3_psr_pd_vs_range.png` — only used by case_3_radar_signal_to_display
- `outputs/F6_psr_false_plots.denetim.txt` — only used by case_3_radar_signal_to_display
- `outputs/F6_psr_false_plots.dw.json` — only used by case_3_radar_signal_to_display
- `outputs/F6_psr_false_plots.pdf` — only used by case_3_radar_signal_to_display
- `outputs/F6_psr_false_plots.png` — only used by case_3_radar_signal_to_display
- `outputs/F7_guidance_needle.denetim.txt` — only used by case_4_par_talkdown, case_5_gnss_independent_approach
- `outputs/F7_guidance_needle.dw.json` — only used by case_4_par_talkdown, case_5_gnss_independent_approach
- `outputs/F7_guidance_needle.pdf` — only used by case_4_par_talkdown, case_5_gnss_independent_approach
- `outputs/F7_guidance_needle.png` — only used by case_4_par_talkdown, case_5_gnss_independent_approach
- `outputs/guidance_panel.json` — only used by case_4_par_talkdown, case_5_gnss_independent_approach, case_9_guidance_uplink
- `outputs/par_asr_raw.json` — only used by case_4_par_talkdown
- `outputs/par_talkdown.json` — only used by case_4_par_talkdown
- `outputs/psr_chains.json` — only used by case_3_radar_signal_to_display
- `outputs/scope_data.js` — only used by case_3_radar_signal_to_display, case_8_surveillance_integrity
- `outputs/scope_demo.html` — only used by case_3_radar_signal_to_display, case_8_surveillance_integrity

## Stays (29)

- `cases/case_1_voice_to_display` — used by case_1_voice_to_display
- `cases/case_2_lost_comms` — used by case_2_lost_comms
- `outputs/F1_wrong_values_vs_snr.denetim.txt` — used by case_1_voice_to_display
- `outputs/F1_wrong_values_vs_snr.dw.json` — used by case_1_voice_to_display
- `outputs/F1_wrong_values_vs_snr.pdf` — used by case_1_voice_to_display
- `outputs/F1_wrong_values_vs_snr.png` — used by case_1_voice_to_display
- `outputs/F2_withheld_vs_snr.denetim.txt` — used by case_1_voice_to_display
- `outputs/F2_withheld_vs_snr.dw.json` — used by case_1_voice_to_display
- `outputs/F2_withheld_vs_snr.pdf` — used by case_1_voice_to_display
- `outputs/F2_withheld_vs_snr.png` — used by case_1_voice_to_display
- `outputs/F4_comm_state_timeline.denetim.txt` — used by case_2_lost_comms
- `outputs/F4_comm_state_timeline.dw.json` — used by case_2_lost_comms
- `outputs/F4_comm_state_timeline.pdf` — used by case_2_lost_comms
- `outputs/F4_comm_state_timeline.png` — used by case_2_lost_comms
- `outputs/F5_real_asr_threshold.denetim.txt` — used by case_1_voice_to_display
- `outputs/F5_real_asr_threshold.dw.json` — used by case_1_voice_to_display
- `outputs/F5_real_asr_threshold.pdf` — used by case_1_voice_to_display
- `outputs/F5_real_asr_threshold.png` — used by case_1_voice_to_display
- `outputs/asr_raw.json` — used by case_1_voice_to_display
- `outputs/asr_sweep.json` — used by case_1_voice_to_display
- `outputs/cockpit_data.js` — used by case_1_voice_to_display, case_2_lost_comms
- `outputs/cockpit_demo.html` — used by case_1_voice_to_display, case_2_lost_comms
- `README.md` — shared (not case-specific)
- `docs` — shared (not case-specific)
- `research` — shared (not case-specific)
- `scripts` — shared (not case-specific)
- `templates` — shared (not case-specific)
- `triage_plan.json` — shared (not case-specific)
- `triage_plan.md` — shared (not case-specific)

Task text:

> If communication with the tower is lost, how does the voice signal reach the cockpit display? Design the translation chain.
