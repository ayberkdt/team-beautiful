# Reveal day — the first 10 minutes after the Advionics task is announced

Environment (once, PowerShell, project root):

```powershell
$env:TEMP="D:\tmp_ideathon\advionics"; $env:TMP=$env:TEMP; $env:MPLCONFIGDIR="D:\tmp_ideathon\mpl"; $env:PYTHONPATH="src"; $env:PYTHONIOENCODING="utf-8"
```

| Min | Step | Command / action |
|---|---|---|
| 0–1 | Paste the official task text into a file (keep the original wording) | `03_Advionics/cases/task_official.txt` (UTF-8; a Notepad BOM is fine) |
| 1–2 | Triage (dry run, moves nothing) | `python 03_Advionics/scripts/triage.py 03_Advionics/cases/task_official.txt` |
| 2–4 | Read the ranking and `03_Advionics/triage_plan.md` (kept cases, what would move). Override if the reading is wrong: `--keep case_X` / `--drop case_Y` | same command + `--keep ...` |
| 4–5 | Ask the mentor the open question of the top case (each `CASE.md` → "Mentor questions"); doc 24 §9 question 1 first if the ranking is split | — |
| 5–6 | Apply the move (manifest written; reversible) | same command + `--apply` → moved to `prev_guess/03_Advionics/<date>_unused/`; undo: `python 03_Advionics/scripts/triage.py --undo "<manifest path printed>"` |
| 6–9 | Run the kept case runners; drop the mentor's numbers in with `--set name=value` or `--params mentor.json` | `python 03_Advionics/cases/<case>/run.py` (each 2–18 s full) |
| 9–10 | Put on slides: each kept case's figure + its 3 key numbers (from `outputs/result.md`) + the shared rule slide | table below |

Never moved by `--apply`: `docs/`, `research/`, `scripts/`, `templates/`, `submission/`, `cases/*.md`, `cases/_common.py`,
the triage files, `outputs/report.md`; a legacy output stays if any kept case claims it (`triage_keywords.json` →
`case_assets`). If no keyword matches, every case is kept.

## Which figure goes on which slide

| Kept case | Slide figure | Claim sentence (slide title) | Live demo |
|---|---|---|---|
| 1 voice → display | `case_1_voice_to_display/outputs/C1_voice_wrong_vs_snr.png` (+ legacy F5 real-ASR threshold) | Masking and context checks cut wrong-but-confirmed values about four- to tenfold; the price is SAY AGAIN | `scripts/atc_live.py "..." --snr 15` |
| 2 lost comms | `case_2_lost_comms/outputs/C2_comm_state_timeline.png` | Each state needs evidence; in loss states nothing new is shown, nothing lost is rebuilt | `outputs/cockpit_demo.html` |
| 3 radar → display | `case_3_radar_signal_to_display/outputs/C3_message_outcome_vs_ber.png` (+ legacy F3, F6) | Corrupted Mode S messages are repaired or rejected, never displayed wrong | `outputs/scope_demo.html` |
| 4 PAR talk-down | `case_4_par_talkdown/outputs/C4_par_voice_loss.png` (+ legacy F7) | The ground radar sees the drift; when the voice stops the panel says LOST, it never extrapolates | report §5b |
| 5 GNSS-independent | `case_5_gnss_independent_approach/outputs/C5_gate_deviation_by_source.png` | A ground sensor keeps the gate error within the alert limit without GNSS and catches a spoofed GNSS | — |
| 6 flight inspection | `case_6_flight_inspection_ils_drone/outputs/C6_ils_inspection_ddm.png` | The inspection receiver tracks the DDM and shows FLAG on every fault — never a centred needle | — |
| 7 readback | `case_7_readback_correlation/outputs/C7_readback_alerts_vs_snr.png` | Real readback errors are rare, so false alarms dominate unless the checker stays silent when unsure | `atc_live.py --text "..."` |
| 8 integrity | `case_8_surveillance_integrity/outputs/C8_spoof_detection_vs_offset.png` | CRC is not authentication; time of arrival is — MLAT flags offsets ≥ 150 m with no false alarms | — |
| 9 uplink | `case_9_guidance_uplink/outputs/C9_uplink_timeout_tradeoff.png` | The loss timeout trades alert speed against nuisance alarms | — |

After the move, regenerate anything legacy that is still kept: `python 03_Advionics/scripts/atc_day.py` (report +
F1–F7) and `python 03_Advionics/scripts/atc_html.py` (demo pages); check `python 03_Advionics/scripts/atc_doc_check.py`.
