# A_Ohneiser2022_Tower_Sol97-2_SID2022 — Tower/ground ASR validations (SESAR Solution 97.2, DLR / Indra / Leonardo)

## Citation
Ohneiser, O., Helmke, H., Shetty, S., Kleinert, M., Ehr, H., Murauskas, Š., Pagirys, T., Balogh, G., Tønnesen, A., Kis-Pál, G., Tichy, R., Horváth, V., Kling, F., Rinaldi, W., Mansi, S., Piazzolla, G., Usanovic, H. (2022). "Understanding Tower Controller Communication for Support in Air Traffic Control Displays." 12th SESAR Innovation Days (SID 2022), Budapest.
URL: https://www.sesarju.eu/sites/default/files/documents/sid/2022/paper_5.pdf

Date read: 2026-11-04. Read: full PDF (8 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]

## Data [D-ag]
Three simulator validations with 22 ATCos from 4 ANSPs:
- LIT: DLR + Idiap STT (Kaldi), multiple remote tower plus ground, Lithuanian (ON) and Austrian (ACG) ATCos, 16 kHz. Generic models adapted with only 2500 utterances (3.6 h ON + 0.9 h ACG).
- NOR: Indra Navia + HungaroControl (Indra voice system), remote tower, 6 Hungarian ATCos, 8 kHz.
- BUL: Leonardo (Kaldi), 8 kHz.
- Controller-side speech only, push-to-talk segmented. SNR not reported.

## Numbers [D-ag]
| Metric | LIT (DLR/Idiap) | NOR (Indra) | BUL (Leonardo) |
|---|---|---|---|
| WER | 5.1% (4.4% solution runs, offline). Online: 13.6% (9.8% solution runs) | – | 16.9% |
| Utterances | 2427 | 934 | 454 |
| Callsign recognition rate | 98.4% | 81.2% | 89.8% |
| Callsign error rate | 0.9% | (cut off in extract) | – |
| Command recognition rate | 91.4% (94.6% for types seen ≥ 25 times, error 3.5%; online 82.9%) | 76.0% | 64.6% |
| Command error rate | 4.5% | – | 5.1% |
| Command rejection rate | 5.0% | – | 35.4% |
- Abstract summary: callsign 81–98%, command 65–91%, and a "slight reduction" in workload at a low workload level.
- Workload: Bedford scale showed no significant difference. ISA workload decreased slightly with ABSR in LIT.
- The paper cites HAAWAII benchmarks: WER < 4% (ATCo) and 7–11% (pilots), callsign error < 2%, command error < 7%.
- The paper gives targets from the approach and en-route experience: command recognition > 95% and command error < 2.5% "significantly reduce ATCo workload".

## Failure modes reported [D-ag]
- Offline vs online (streaming) gap: WER 4.4% offline vs 9.8% online for the same runs.
- Recording mismatch (sampling rate, microphones, face masks, background noise) between training and use.
- Simulator speech differs from ops-room speech ("ATCos speak differently in simulations").
- NOR does not cover conditional and non-standard clearances. 5 of 6 NOR ATCos changed their pronunciation so the system would understand.

## Relevance to us [Y]
- Streaming roughly doubles WER compared to offline. A cockpit display must be real-time, so we should budget for the online number and could re-decode offline after end of transmission to refine.
- The 95% / 2.5% target from the ATC side is a useful acceptance criterion to quote for "useful enough to reduce workload".
