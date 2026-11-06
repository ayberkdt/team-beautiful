# A_Wee2025_SEA_accent_Whisper — Whisper fine-tuned on Southeast-Asian-accented ATC, with cross-dataset zero-shot baselines

## Citation
Wee, M. Y. Z., Wong, J. J. H., Lim, L., Tan, J. Y. W., Gupta, P., Lim, D., Tew, E. H., Han, A. K. S., Lim, Y. Z. (2025). "Adapting Automatic Speech Recognition for Accented Air Traffic Control Communications." arXiv:2502.20311. Republic of Singapore Air Force (AETHER / RAiD).
URL: https://arxiv.org/abs/2502.20311 (venue not stated in the text I read)

Date read: 2026-11-04. Read: full PDF (10 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]

## Data [D-ag]
- New SEA-accented ATC dataset, 37 h of region-specific training data (military context). Augmentations used audiomentations.
- Cross-tests on ATCO2 and ATCOSIM.
- SNR: not given numerically. The paper says ATC speech "often sounds muffled" with low SNR, from AM VHF/UHF radio noise, static and speech echo.

## Metric [D-ag]
"Combined WER" = (S + D + I) / N, pooled over the whole dataset. Text normalisation details were not checked; very high zero-shot WERs above 100% suggest number formatting and insertions or hallucinations are counted. [inference, not verified]

## Numbers (Table IV), WER as fraction [D-ag]
| Model | ATCO2 | ATCOSIM | SEA-accented |
|---|---|---|---|
| openai/whisper-small (zero-shot) | 0.964 | 0.911 | 1.226 |
| jlvdoorn/small-atco2-asr (Whisper-ATC) | 0.425 | 0.543 | 0.704 |
| sea-small (theirs) | 0.574 | 0.511 | **0.098** |
| openai/whisper-large-v3 (zero-shot) | 0.790 | 0.804 | 0.934 |
| jlvdoorn/large-v3-atco2-asr (Whisper-ATC) | **0.376** | 0.463 | 0.553 |
| openai/large-v3-turbo (zero-shot) | 0.899 | 0.817 | 1.197 |
| sea-large-v3-turbo (theirs) | 0.515 | **0.411** | 0.118 |

- Headline: 9.82% WER on in-domain SEA-accented ATC speech.
- Their literature table gives corpus sizes, some differing from the ATCO2 paper: LDC94S14A 72.5 h, ATCOSIM 10.7 h, UWB-ATCC 179 h (sic; the ATCO2 paper says 13.2 h), HAAWAII 34 h, MALORCA 10.9 h, AIRBUS-ATC 59 h, ATCO2 5285 h. Treat these as secondary.
- They cite Whisper-ATC at 1.19% WER on ATCOSIM, and say "WERs below 25%" may be acceptable for some transcription tasks.

## Failure modes reported [D-ag]
- Off-the-shelf Whisper fails on ATC: zero-shot WER 79–96% on ATCO2 and 80–91% on ATCOSIM in their evaluation pipeline.
- Accent and region overfit: the SEA model gets 9.8% at home but 51–57% on ATCO2/ATCOSIM. Whisper-ATC gets 38% on ATCO2 but 55% on SEA. Cause given: "variations in accents, terminology, and phraseology".
- Accent fine-tuning in Airbus's earlier work caused catastrophic forgetting of other accents (as reported by this paper, not read in the original).

## Relevance to us [Y]
- Strong, citable argument: consumer ASR "as is" does not work for ATC. Zero-shot Whisper large-v3 is near 80% WER here (pipeline caveat). Domain fine-tuning plus constrained decoding is mandatory.
- Generalisation across regions is the open risk. A cockpit product flies everywhere, so it needs multi-accent training, or a confidence-gated display that falls back to "audio only / verify".
