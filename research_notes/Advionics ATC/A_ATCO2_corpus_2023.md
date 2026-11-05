# A_ATCO2_corpus_2023 — ATCO2 corpus (LiveATC-style VHF data, 5281 h) plus ATC corpora overview

## Citation
Zuluaga-Gomez, J., Veselý, K., Szöke, I., Blatt, A., Motlicek, P., Kocour, M., Rigault, M., Choukri, K., Prasad, A., Sarfjoo, S. S., Nigmatulina, I., Cevenini, C., Kolčárek, P., Tart, A., Černocký, J., Klakow, D. (2022/2023). "ATCO2 corpus: A Large-Scale Dataset for Research on Automatic Speech Recognition and Natural Language Understanding of Air Traffic Control Communications." arXiv:2211.04054v2 (15 Jun 2023), preprint "under review". DOI 10.48550/arXiv.2211.04054.
URL: https://arxiv.org/abs/2211.04054 . Data: https://www.atco2.org/data (1 h free); ELDA ELRA-S0484.
Partners include Idiap, BUT, Saarland Univ., ELDA, Honeywell (Brno), OpenSky Network.

Date read: 2026-11-04. Read: full PDF (29 pp.) extracted with PyMuPDF and keyword-searched (not read line by line). [D-ag]

## Data [D-ag]
- ATCO2-PL-set: 5281 h of unlabelled VHF ATC audio from ~10 airports, collected by volunteer receivers. Each sample has a pseudo-transcript, a WADA-SNR estimate, an English-detection score, and callsign context from OpenSky.
- ATCO2-test-set: ~4 h (3.4 h in stats table) with gold transcripts plus NER tags (callsign/command/value), SNR ≤ 15 dB. Free 1.1 h subset. Airports: LKTB, LKPR, LZIB, LSGS, LSZH, LSZB, YSSY. 16 kHz 16-bit.
- Per-airport mean SNR (English data, Table 3), mean/std in dB: Tallinn 4.6/7.8, Prague 14.2/8.2, Brno 4.1/15.7, Sion 10.0/8.0, Bern 15.4/10.7, Zurich 7.8/7.7, Bratislava 5.4/8.7, Brisbane 10.2/5.8, Sydney 3.1/7.0.
- Paper's wording: "very noisy voice recordings (often below 15 dB SNR)".
- Annotation cost: "eight to ten man-hours effort" per hour of raw dialogue.

## Other ATC corpora listed in the paper (Table 1) [D-ag]
| Corpus | Type | Accent | Hours | Public |
|---|---|---|---|---|
| HAAWAII | real, Iceland + London | Icelandic, British | 47 | no |
| MALORCA | real, Vienna + Prague | German, Czech | 13 | no |
| AIRBUS | real, Toulouse-Blagnac | French | 100 | no |
| ATCOSIM | simulated studio, added cockpit noise | Swiss German, German, French | 10.7 | yes |
| UWB-ATCC | real, Prague | Czech | 13.2 | yes |
| LDC-ATCC (LDC94S14) | real, 3 US airports (Logan, Washington National, DFW) | American | 26.2 | yes |
| HIWIRE | simulated, cockpit noise | French, Greek, Italian, Spanish | 28.7 | yes |

## Metric and numbers [D-ag]
ASR baselines (Kaldi hybrid trained on pseudo-labelled ATCO2 subsets, Table 5), WER %:
| Training data | ATCO2 test (4 h) | ATCO2 test 1 h | MALORCA Vienna (clean, ATCo only, 8 kHz) |
|---|---|---|---|
| 5281 h all ATCO2 | 22.3 | 15.8 | 11.1 |
| 4500 h English only | 22.5 | 15.7 | 10.0 |
| 3600 h filtered (ELD > 0.7, SNR > 0 dB, conf > 0.8) | 22.5 | 15.8 | 9.3 |
| 1500 h with SNR > 16 dB only | 23.4 | 16.7 | 11.9 |
| Seed system (135 h supervised + 700 h) | 26.6 | 18.6 | 4.8 (Vienna was in its training data) |
- Removing noisy (SNR < 16 dB) training data made results worse. Noisy training data is needed.
- The paper states standard ASR on such data gives "WERs of ∼30% or above". It cites "under 5% WER" as the needed commercial performance.
- NER on gold text (BERT, 5-fold): F1 0.97 callsign, 0.82 command, 0.87 value. Command F1 varied 0.79–0.85 between folds.
- Speaker-role detection (ATCo vs pilot) on text: average F1 0.78–0.84. Pilots are harder.
- Callsign boosting in semi-supervised training: −17.5% relative WER on callsign words.

## Failure modes reported [D-ag]
- Noise (SNR mostly < 15 dB), accents, high speech rate, and local conventions create a strong domain shift between airports.
- Non-ATC corpora (LibriSpeech etc.) do not help.
- The command class is hardest: several commands per utterance, or mixed commands.
- The free 1 h set is easier than the 4 h set (15.8% vs 22.3%), so WER depends a lot on which subset is used.

## Relevance to us [Y]
- ATCO2 is the closest public match to what a cockpit hears: VHF, mixed pilots and ATCo, 3–15 dB SNR. A realistic target is about 15–22% WER from a well-adapted hybrid model, not the 3–5% of clean controller-mic data.
- The free 1 h subset is usable for a demo or evaluation within the Ideathon timeframe. License should be checked before redistribution.
- Since callsign F1 (0.97) is much higher than command F1 (0.82), the display should show confidence per field.
