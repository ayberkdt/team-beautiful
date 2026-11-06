# A_ZuluagaGomez2022_wav2vec2_ATC_SNR — wav2vec 2.0 / XLS-R on ATC, with per-dataset SNR bands and WER

## Citation
Zuluaga-Gomez, J., Prasad, A., Nigmatulina, I., Sarfjoo, S. S., Motlicek, P., Kleinert, M., Helmke, H., Ohneiser, O., Zhan, Q. (2022). "How Does Pre-trained Wav2Vec 2.0 Perform on Domain-Shifted ASR? An Extensive Benchmark on Air Traffic Control Communications." arXiv:2203.16822v2 (17 Oct 2022). Published in IEEE Spoken Language Technology Workshop (SLT) 2022 per my prior knowledge; not verified in the PDF text extracted. [A for venue]
URL: https://arxiv.org/abs/2203.16822

Date read: 2026-11-04. Read: full PDF (8 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]

## Data and SNR (Table 1) [D-ag]
| Dataset | Train / Test | SNR [dB] | Hybrid SOTA WER |
|---|---|---|---|
| NATS (London approach, HAAWAII, 8 kHz) | 18 h / 0.9 h | ≥ 20 | 7.7% |
| ISAVIA (Iceland en-route, 8 kHz) | 14 h / 1 h | 15–20 | 12.5% |
| ATCO2-Test (VHF, 7 airports) | – / 1.1 h | 10–15 | 24.7% |
| LiveATC-Test (VHF, pilots + ATCo) | – / 1.8 h | 5–15 | 35.8% |
| LDC-ATCC | 23 h / 2.6 h | 10–15 | – |
| UWB-ATCC | 10.4 h / 2.6 h | ≥ 20 | – |
| ATCOSIM | 8 h / 2.4 h | ≥ 20 | – |
- The paper's general statement: ATC "usually below 15 dB SNR, which is the default in ATC environments". [D-ag]

## Numbers — E2E models (Table 2), WER %, greedy / +4-gram LM [D-ag]
| Model | NATS | ISAVIA | ATCO2-Test | LiveATC-Test |
|---|---|---|---|---|
| Hybrid baseline (Kaldi, 132 h) | 7.7 | 12.5 | 24.7 | 35.8 |
| w2v2-L-60k, 32 h fine-tune | 6.8 / **5.4** | 8.8 / **7.3** | 34.6 / 31.2 | 39.8 / 34.5 |
| w2v2-XLS-R+, 132 h fine-tune | 9.0 / 7.4 | 10.4 / 8.3 | 22.8 / **19.8** | 29.7 / **24.9** |
- Relative WER reduction vs hybrid: 30% (NATS) and 41% (ISAVIA) with w2v2-L-60k; 19% (ATCO2) and 30% (LiveATC) with XLS-R+.
- Adding the broader 132 h set made the clean in-domain sets worse (NATS 6.8 → 9.3%) but the noisy sets much better.

## Failure modes reported [D-ag]
- WER rises steeply as SNR falls. Across datasets (confounded with accent and domain): ≥ 20 dB about 5–8%; 15–20 dB about 7–12%; 10–15 dB about 20–25%; 5–15 dB about 25–36%.
- E2E models need GPUs for real time and are harder to stream than hybrid. The authors say hybrid is still the industrial default.

## Relevance to us [Y]
- This is the best available single table linking SNR band to WER for ATC (dataset-level, not a controlled sweep). It is the core evidence for the "degraded communication" claim: going from good ground-line audio (≥ 20 dB) to typical VHF (5–15 dB) multiplies WER by about 3–5x.
- Design numbers: assume 20–35% WER on degraded VHF. Without context biasing and a constrained ontology, a raw transcript would be unusable at that level. Display structured, confidence-gated fields instead.
- Multilingual pre-training (XLS-R) helps on accented, noisy data. That is relevant for international cockpit use.
