# A_Nigmatulina2021_callsign_surveillance — Callsign recognition boosted with surveillance data (LiveATC vs MALORCA)

## Citation
Nigmatulina, I., Braun, R. A., Zuluaga-Gomez, J., Motlicek, P. (2021). "Improving callsign recognition with air-surveillance data in air-traffic communication." arXiv:2108.12156 [cs.CL], 27 Aug 2021. Funding: ATCO2 (H2020 864702) and HAAWAII (SESAR 884287). Idiap / Univ. Zurich / EPFL. Venue: arXiv preprint. Search snippets say it was submitted to Interspeech 2021; acceptance not verified.
URL / DOI: https://arxiv.org/abs/2108.12156 , 10.48550/arXiv.2108.12156

Date read: 2026-11-04. Read: full PDF text extracted with PyMuPDF. [D-ag]

## Data [D-ag]
- Acoustic model: CNN-TDNNF (Kaldi, LF-MMI). 195 h of supervised ATC speech, augmented with LiveATC-matched noise and speed perturbation to ~1200 h, plus 700 h semi-supervised LiveATC (Europe). 3-gram LM.
- Test sets built from ATCO2 test data with surveillance info (Table 2):
  - LiveATC: 472 utterances, all with a callsign, median 29 surveillance callsigns per utterance, 32 min.
  - LiveATC mix: 581 with / 29 without callsign, 40 min.
  - MALORCA Prague: 784 / 88, 5 callsigns per utterance, 82 min.
  - MALORCA Vienna: 877 / 38, 19 callsigns per utterance, 65 min.
- SNR stated: LiveATC VHF (pilots + ATCo) has "low SNR often below 10dB". MALORCA is "telephone quality speech with SNR usually above 20dB", ATCo only. Audio is filtered above 4 kHz.

## Metric [D-ag]
WER over the whole utterance; CallWER is WER on the callsign word sequence only; Acc is the share of fully correct callsigns (texterrors tool).

## Numbers (Table 3) [D-ag]
| Test set | Baseline WER | Baseline CallWER | Baseline callsign Acc | Best realistic (G+rescoring surveillance): WER / CallWER / Acc | Oracle (ground-truth callsign) Acc |
|---|---|---|---|---|---|
| LiveATC | 28.0% | 28.5% | 41.3% | 23.4% / 14.3% / 69.7% | 74.6% |
| LiveATC mix | 30.7% | 29.2% | 50.5% | 27.2% / 16.0% / 71.3% | 79.8% |
| MALORCA Prague | 3.1% | 2.2% | 94.2% | 3.1% / 1.0% / 97.4% | 97.7% |
| MALORCA Vienna | 9.2% | 6.6% | 84.6% | 8.2% / 1.7% / 96.3% | 97.6% |

Headline: +28.4% absolute callsign accuracy, and 45.2–74.2% relative callsign-WER improvement depending on the test set. [D-ag]

## Failure modes reported [D-ag]
- Noisy VHF (SNR < 10 dB): baseline gets only 41% of callsigns fully right, and WER is 28–31%.
- Boosting more candidate callsigns (up to 29 per utterance) makes it "easier for the system to pick the wrong one". Accuracy still rises.
- Example baseline errors: "hello sovar one nine lima" for "stobart two one nine lima"; "ryanair four bye bye" for "ryanair four tango mike".
- G-boosting doubles memory use because a new G.fst is built per update.

## Relevance to us [Y]
- This is the cleanest published SNR contrast for one ASR model: VHF < 10 dB gives about 28% WER, telephone-quality > 20 dB gives 3–9% WER. Cockpit reception of ATC over VHF is the LiveATC-like condition, not the MALORCA-like one.
- Context biasing transfers directly to the cockpit. Boost own callsign (known), the active flight plan waypoints, and expected values. Our own callsign is the strongest prior, much stronger than 5–29 radar candidates.
- Design rule: never show a callsign-gated clearance without a confidence check. 30% of LiveATC callsigns stay wrong even after boosting.
