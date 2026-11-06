# A_HAAWAII_framework_SID2023 — HAAWAII speech framework: SAD, speaker role, ASR WER, callsign boosting (NATS London, Isavia)

## Citation
Motlicek, P., Prasad, A., Nigmatulina, I., Helmke, H., Ohneiser, O., Kleinert, M. (2023). "Automatic Speech Analysis Framework for ATC Communication in HAAWAII." 13th SESAR Innovation Days (SID 2023), Seville. DOI 10.61009/SID.2023.1.40. SESAR grant 884287.
Open copy: https://elib.dlr.de/199970/ (PDF SIDs_2023_paper_72_final.pdf); also https://publications.idiap.ch/publications/show/5256

Date read: 2026-11-04. Read: full PDF (9 pp.) extracted with PyMuPDF. [D-ag]

## Data [D-ag]
- NATS: London TMA. Isavia: Iceland en-route. Train (ATCo/pilot): Isavia 9 h / 10 h; NATS 11.8 h / 12.3 h. Test: Isavia 0.5 h / 0.6 h; NATS 0.4 h / 0.4 h (Table II).
- Baseline ASR: 100 h public/other ATC data (LDC-ATCC, UWB-ATCC, ATCOSIM, MALORCA), speed-perturbed to 300 h, no HAAWAII data. HAAWAII ASR: ~195 h transcribed, ~575 h after perturbation. Kaldi CNN-TDNNF, 3-gram LM.
- SAD evaluation: 6.8 h / 1000 utterances of LiveATC VHF data (ATCO2).
- SNR: not reported numerically. Isavia has "different acoustic conditions, and accents".

## Numbers [D-ag]
ASR WER (Table VI):
| System | Isavia | NATS |
|---|---|---|
| Baseline ASR (no in-domain data) | – | 28.3% |
| HAAWAII ASR | 12.4% | 7.5% |

Callsign boosting (Table VII): WER / callsign-only WER / callsign accuracy:
| Boosting | Isavia | NATS |
|---|---|---|
| none | 12.4 / 5.0 / 87.9% | 7.5 / 4.1 / 86.7% |
| unigrams from surveillance | 12.3 / 3.7 / 90.7% | 7.4 / 3.6 / 88.0% |
| n-grams from surveillance (realistic) | 12.1 / 4.1 / 90.5% | 6.7 / 2.0 / 93.3% |
| ground-truth callsign (oracle) | 11.6 / 2.5 / 94.7% | 6.4 / 1.3 / 96.1% |

**Note:** the abstract's "about 96% and 95%" callsign accuracy for NATS / Isavia matches the **oracle** row (ground-truth callsign boosted), not the realistic surveillance-boosted row (93.3% / 90.5%). Quote 90–93% as the realistic figure. [D-ag numbers; the mapping is my reading of the table]

Adaptation to a new site (NATS, Table VIII), WER vs hours of target data (AM+LM): 0 h 28.3%; 1 h 23.0%; 2 h 22.5%; 4 h 18.4%; 10 h 15.6%; 13 h 13.9%.

Speaker role (ATCo vs pilot) accuracy (Table V): x-vector 76.5% (Isavia) / 83.8% (NATS); rule-based 82 / 85; CNN 91 / 93; BERT 93 / 96.

SAD on LiveATC VHF (Table III): best detection error rate 9.7% (multilingual ASR-based, LR fusion; FA 6.1%, miss 3.6%). WebRTC 16.5%; energy-based 13.3% (used in real time).

Speaker segmentation corrections by annotators: Isavia 9.4% deletions, 5.9% speaker changes; NATS 2.4% / 1.1%.

## Failure modes reported [D-ag]
- Pilot speech is "often obscured by background noise". Manually annotating pilot recordings is "twice as hard" as ATCo recordings (citing prior work).
- Without a PTT signal, SAD and speaker role must be inferred. Errors here propagate to ASR and understanding.
- 5% absolute WER gap between sites from acoustics and accent.
- Real-time requirement: "a few tens or hundreds of milliseconds" for readback detection and label pre-filling.

## Relevance to us [Y]
- In the cockpit we have PTT and own-transmit state, so we know when we spoke. ATC vs other-aircraft speech still needs role detection. Text-based BERT role detection reaches 93–96%.
- The adaptation curve is a usable planning number: ~10–13 h of local data takes WER from 28% to ~14–16%.
- Our own callsign is the cockpit equivalent of "ground-truth boosting". That is the oracle row: callsign accuracy ~95–96% on NATS/Isavia. Strong argument for callsign-gated display.
