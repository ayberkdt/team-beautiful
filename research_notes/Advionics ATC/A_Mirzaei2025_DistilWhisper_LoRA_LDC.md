# A_Mirzaei2025_DistilWhisper_LoRA_LDC — Distil-Whisper + LoRA on the LDC ATC0 corpus (US)

## Citation
Mirzaei, S., Arzate, J., Vijay, Y. (2025). "Enhancing Aviation Communication Transcription: Fine-Tuning Distil-Whisper with LoRA." arXiv:2503.22692. arXiv comment: "Under review by Journal of Aerospace Information Systems". Affiliations: Cal Poly Pomona, Edwards AFB Test Center, Skyryse.
URL: https://arxiv.org/abs/2503.22692

Date read: 2026-11-04. Read: full PDF text (14 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]

## Data [D-ag]
- LDC Air Traffic Control Corpus (ATC0, LDC94S14): ~70 h of controller and pilot transmissions near DFW, Boston Logan and Washington National. 8 kHz 16-bit, one FAA frequency monitored 1–2 h per file without squelch.
- 29 091 utterances after cleaning. "UNINTELLIGIBLE" rows were dropped, and numbers were normalised to words.
- 5-fold cross-validation over rows: 23 273 train / 5 818 test per fold.
- SNR: not reported.

## Metric [D-ag]
WER = (S + D + I) / N.

## Numbers [D-ag]
- Best: average WER 3.86% across 5 folds (LoRA alpha 256, rank 256 or 512; lr 5e-4, 5 epochs, batch 6).
- Before LoRA tuning, with alpha 64 / rank 32, lr 5e-4, 5 epochs, batch 6: per-fold WER 3.21, 11.27, 3.26, 3.19, 5.06%. One fold is much worse.
- With a low learning rate (1e-5, 3 epochs), WER was 43–53%. This shows how badly an under-adapted Whisper does on this data. It is not a zero-shot baseline; no zero-shot WER is reported.
- The paper gives its own rule of thumb: < 10% WER is "suitable for many ASR applications", < 5% is "excellent". [D-ag]

## Caveats and failure modes [D-ag + own reading]
- The split is random over rows, not by speaker or by airport. The same controllers and frequencies appear in train and test, so 3.86% is optimistic. The authors list "out-of-distribution testing" as future work. [D-ag for statement; optimism inference is mine]
- Dropping unintelligible utterances removes exactly the hard, degraded cases. [D-ag that they were dropped]
- Fold variance (3.2% to 11.3% in one setting) shows sensitivity to the data partition.

## Relevance to us [Y]
- Shows that a small, cockpit-deployable Whisper variant can reach low-single-digit WER on in-distribution US VHF ATC. Treat 3.86% as a best case, not a field number.
- For our pitch: quote it only together with the Whisper-ATC cross-dataset numbers (A_vanDoorn2024_WhisperATC.md) and ATCO2 (15–22%) to stay honest.
