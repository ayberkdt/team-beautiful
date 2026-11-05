# A_00_summary — ATC speech recognition and understanding: published numbers (read 2026-11-04)

Scope: published WER, command and callsign recognition for ATC, readback-error base rates, and SNR effects. Built for the Team Beetiful Advionics concept (ATC voice → cockpit display, robust when communication degrades). Every number below links to an `A_*.md` file in this folder, which carries the citation, URL and [D-ag]/[A] marks. Values marked [A] in their source file are not used in the table, except where flagged.

## Table: WER rises about 3–5x from clean ground-line audio to VHF, and generic ASR fails outright

Column notes:
- "Callsign" = callsign recognition/extraction rate or accuracy (definitions differ per paper).
- "Command recognition" = share of commands with callsign + type + value correct (HAAWAII: command extraction rate per utterance).
- SNR column: "not stated" means the paper gives no dB value.
- WER is rounded to 1 decimal; exact values are in the source files (e.g. 3.86, 7.62, 7.75).
- Table produced with datawiz `tablo.markdown_tablo`, sorted by WER. `tablo.denetle` gave 2 UYARI (mixed decimals in the raw data, fixed by uniform 1-decimal output) and 0 HATA.

| System | Data | SNR (dB) | WER (%) | Command recognition (%) | Command error (%) | Callsign (%) | Source file |
|:---|:---|:---|---:|---:|---:|---:|:---|
| HAAWAII rule-based ASRU | NATS London, ATCo | not stated | 2.8 | 93.2 | 3.6 | 97.5 | A_HAAWAII_readback_SID2022 |
| HAAWAII rule-based ASRU | Isavia en-route, ATCo | not stated | 2.9 | 92.3 | 4.3 | 96.9 | A_HAAWAII_readback_SID2022 |
| Kaldi + surveillance callsign boost | MALORCA Prague, ATCo | > 20 | 3.1 | — | — | 97.4 | A_Nigmatulina2021_callsign_surveillance |
| Distil-Whisper + LoRA (random split) | LDC ATC0, US, ATCo + pilot | not stated | 3.9 | — | — | — | A_Mirzaei2025_DistilWhisper_LoRA_LDC |
| DLR/Idiap ABSR, tower (LIT) | Remote tower sim, ATCo | not stated | 5.1 | 91.4 | 4.5 | 98.4 | A_Ohneiser2022_Tower_Sol97-2_SID2022 |
| wav2vec2-L-60k (32 h fine-tune) | NATS London | ≥ 20 | 5.4 | — | — | — | A_ZuluagaGomez2022_wav2vec2_ATC_SNR |
| Airbus challenge winner (Vocapia-LIMSI) | Toulouse, controllers | not stated (VHF) | 5.5 | — | — | — | A_Pellegrini2019_Airbus_ATC_challenge |
| Appareo ASR (vendor WER) + NASA parser | LiveATC KLAX approach | not stated (VHF) | 6.0 | 85.3 | — | 83.4 | A_Lutz2022_NASA_LiveATC_command_recognition |
| HAAWAII ASR + n-gram callsign boost | NATS London, mixed | ≥ 20 | 6.7 | — | — | 93.3 | A_HAAWAII_framework_SID2023 |
| HAAWAII rule-based ASRU | NATS London, pilot | not stated | 7.1 | 79.9 | 11.5 | 95.9 | A_HAAWAII_readback_SID2022 |
| wav2vec2-L-60k (32 h fine-tune) | Isavia | 15–20 | 7.3 | — | — | — | A_ZuluagaGomez2022_wav2vec2_ATC_SNR |
| Kaldi TDNNF, 176 h multi-site | 4 test sets, average | not stated | 7.8 | — | — | — | A_ZuluagaGomez2020_ASR_benchmark_Interspeech |
| Kaldi + surveillance callsign boost | MALORCA Vienna, ATCo | > 20 | 8.2 | — | — | 96.3 | A_Nigmatulina2021_callsign_surveillance |
| Whisper small, SEA fine-tune | SEA-accented military ATC | not stated | 9.8 | — | — | — | A_Wee2025_SEA_accent_Whisper |
| HAAWAII rule-based ASRU | Isavia en-route, pilot | not stated | 10.4 | 71.3 | 9.7 | 88.4 | A_HAAWAII_readback_SID2022 |
| Airbus challenge winner (Vocapia-LIMSI) | Toulouse, pilots | not stated (VHF) | 10.5 | — | — | — | A_Pellegrini2019_Airbus_ATC_challenge |
| HAAWAII ASR + n-gram callsign boost | Isavia en-route, mixed | 15–20 | 12.1 | — | — | 90.5 | A_HAAWAII_framework_SID2023 |
| Leonardo ABSR, tower (BUL) | Tower sim, ATCo | not stated (8 kHz) | 16.9 | 64.6 | 5.1 | 89.8 | A_Ohneiser2022_Tower_Sol97-2_SID2022 |
| XLS-R (132 h fine-tune) | ATCO2-Test VHF | 10–15 | 19.8 | — | — | — | A_ZuluagaGomez2022_wav2vec2_ATC_SNR |
| Kaldi trained on 5281 h ATCO2 pseudo-labels | ATCO2 test 4 h VHF | ≤ 15 | 22.3 | — | — | — | A_ATCO2_corpus_2023 |
| Kaldi + surveillance callsign boost | LiveATC VHF, ATCo + pilot | < 10 | 23.4 | — | — | 69.7 | A_Nigmatulina2021_callsign_surveillance |
| XLS-R (132 h fine-tune) | LiveATC-Test VHF | 5–15 | 24.9 | — | — | — | A_ZuluagaGomez2022_wav2vec2_ATC_SNR |
| Generic ATC hybrid, no site data | NATS London, mixed | ≥ 20 | 28.3 | — | — | — | A_HAAWAII_framework_SID2023 |
| Whisper-ATC large-v3 (ATCO2-tuned), third-party test | ATCO2 | ≤ 15 | 37.6 | — | — | — | A_Wee2025_SEA_accent_Whisper |
| AWS generic ASR | FAA historical audio | not stated | 62.0 | — | — | — | A_Lutz2022_NASA_LiveATC_command_recognition |
| Whisper large-v3, zero-shot | ATCO2 | ≤ 15 | 79.0 | — | — | — | A_Wee2025_SEA_accent_Whisper |
| Out-of-domain model (LibriSpeech + CV only) | Vienna approach | not stated | 95.8 | — | — | — | A_ZuluagaGomez2020_ASR_benchmark_Interspeech |
| MALORCA ABSR (radar context) | Prague approach, ATCo | 5 dB better than Vienna | — | 91.9 | 0.6 | — | A_Helmke2019_ATMSeminar_ABSR_ML_errors |
| MALORCA ABSR (radar context) | Vienna approach, ATCo | low (8 kHz) | — | 85.2 | 3.2 | — | A_Helmke2019_ATMSeminar_ABSR_ML_errors |
| AcListant ABSR (as cited in MALORCA report) | Düsseldorf approach, ATCo (sim) | not stated | — | 95.0 | 1.7 | — | A_MALORCA_D5-3_final_report |
| Indra ABSR, remote tower (NOR) | Remote tower sim, ATCo | not stated (8 kHz) | — | 76.0 | — | 81.2 | A_Ohneiser2022_Tower_Sol97-2_SID2022 |

Reading the table: in-domain, context-aided systems on controller microphone audio reach 3–8% WER and 92–98% callsign recognition. The same class of model on VHF-received audio (ATCO2/LiveATC, 5–15 dB) gets 20–25% WER. Generic or zero-shot models get 62–96%.

## SNR → WER (dataset-level, confounded with accent and domain) — from A_ZuluagaGomez2022_wav2vec2_ATC_SNR [D-ag]
- ≥ 20 dB (NATS): 5.4–7.7% WER
- 15–20 dB (Isavia): 7.3–12.5%
- 10–15 dB (ATCO2-Test): 19.8–24.7%
- 5–15 dB (LiveATC-Test): 24.9–35.8%

Corroborating data:
- A_Nigmatulina2021: telephone > 20 dB gives 3.1–9.2% WER; VHF < 10 dB gives 28.0%.
- A_ATCO2_corpus_2023: per-airport mean SNR 3.1–15.4 dB.
- A_MALORCA: 5 dB SNR gap comes with 0.6% vs 3.2% command error.

## Failure modes with numbers
1. **Pilot / radio-received speech is about 2x worse than controller speech.**
   - Airbus: 5.5% vs 10.5% WER, callsign F1 86.8% vs 79.0% (A_Pellegrini2019).
   - HAAWAII: pilot command extraction 71–80% vs ATCo 92–93% (A_HAAWAII_readback_SID2022).
   - ENAIRE/Indra: flight crew callsign 49–67% vs ATCo 84–87% [A, unread] (A_Garcia2023).
2. **Text-to-concept, not only ASR, is the weak link.** With perfect transcripts, Isavia pilot command extraction is still only 88.3%. The readback-alert false-alarm rate rises 18% → 58% from gold annotation to gold transcript, and only 58% → 67% from adding real ASR (A_HAAWAII_readback_SID2022).
3. **Low base rate means many false alarms.**
   - Readback errors are in 1.3% of utterances (4% of threads).
   - Real ops: 82% detection at 67% false-alarm rate. Lab: 82% at 13% (A_HAAWAII_readback_SID2022).
   - En-route FAA tapes: < 1% of full readbacks wrong, 2% of partial readbacks (A_Cardosi1993).
4. **Complex clearances.** Readback error rate goes from 0.7% to 1.4% from 3 to 4 elements. Clearances with ≥ 5 elements are 4% of clearances but 26% of errors, with 8% miscommunication (A_Cardosi1993).
5. **What goes wrong in readbacks.**
   - Frequencies 37%, crossing restrictions 18% (A_Cardosi1993).
   - Consequences: altitude deviation 38%, wrong aircraft accepted clearance 36% (A_vanEs2004).
   - 65% of readback/hearback errors happen in climb or descent (A_vanEs2004).
6. **Similar callsigns and the wrong aircraft.**
   - Similar callsign cited in 20% of 444 European incidents (A_vanEs2004).
   - 0.8% of en-route clearances answered with a different callsign; only 39% of those corrected (A_Cardosi1993).
7. **Digit confusion.** The 10 000 / 11 000 ft pair is 38% of 191 misinterpreted-altitude ASRS deviations (A_ASRS_Directline1991_10vs11k_altitude). "Climb to two thousand" vs "climb two two thousand" is a named ASR confusion (A_ZuluagaGomez2020). No dataset-level statistic for to/two or for/four was found.
8. **Hearback.**
   - Controllers miss 11% of readback errors en route (A_Cardosi1993).
   - Tower and approach controllers detect only 63% and 50%, as cited (A_HAAWAII_readback_SID2022; originals not read).
   - 22% of the 87 Isavia readback samples went uncorrected (A_HAAWAII_readback_SID2022).
9. **Context helps a lot.**
   - Surveillance callsign boosting on LiveATC: callsign accuracy 41.3% → 69.7% (A_Nigmatulina2021).
   - MALORCA Vienna command error 18.9% → 3.2% with radar context (A_MALORCA, A_Helmke2019).
   - Caveat: the abstract's "96/95% callsign" figure in A_HAAWAII_framework_SID2023 is the oracle (ground-truth boost). The realistic figure is 93.3% / 90.5%.
10. **Command types differ.**
    - DESCEND 97.5%; DIRECT_TO 80–87% with 5–13% errors because of unseen waypoint names (A_Helmke2019).
    - Speed commands only 70.2% vs altitude 94.2% on KLAX (A_Lutz2022).
11. **Domain and accent shift.**
    - Whisper zero-shot 79–96% WER (A_Wee2025).
    - Accent-tuned models fall from 9.8% to 51–57% on other regions (A_Wee2025).
    - Out-of-domain hybrid 43–96% (A_ZuluagaGomez2020).
12. **Streaming and segmentation.**
    - Online WER 9.8% vs offline 4.4% on the same runs (A_Ohneiser2022).
    - Honeywell patent claims 10–30% of segments are left unsplit (two speakers merged) (A_Honeywell_US12322410_unsplit_segments).

## Gaps and items not verified in this session
- Whisper-ATC paper (van Doorn 2024) was not reachable. Its 13.5% ATCO2 and 1.17% / 3.88% ATCOSIM WERs are [A].
- The ENAIRE/Indra Aerospace 2023 paper was not reachable (403). The 49–67% flight-crew callsign figure is [A].
- Airbus DragonFly's ATC-taxi transcription comes from a paywalled snippet [A]. The Skies article that was read does not mention ASR.
- AcListant-Strips originals (DASC 2016, ATM 2015/2017) were not read. Workload ÷3, 50–65 l (or €) fuel per flight, and +2 landings/h are quoted via the MALORCA and ontology papers.
- Cardosi 1998 ASRS analysis (DOT/FAA/AR-98/17) could not be downloaded (DTIC/ROSAP blocked).
- Frequentis, Thales and Indra operational products: only the descriptions in A_Ontology_PJ16-04_DASC2018 (2018) and the TRL6 slides (A_PJ10-W2-96) were read. No 2024–2026 operational deployment was confirmed.
- Garmin and Collins cockpit ATC-transcription products: none found in the searches run.

## Relevance to us [Y]
- Design point for degraded VHF: assume 20–35% WER. Display structured fields (callsign / type / value / unit / condition per the PJ.16-04 ontology), each with a confidence. Bias decoding on own callsign plus FMS route and waypoint vocabulary.
- Callsign gating is the most robust function: 88–98% even when command extraction drops. Altitude and frequency deserve the most UI weight, since they make up most readback-error consequences.
- Do not sell readback alerting on detection rate alone. The published real-ops false-alarm rate is 67%.
