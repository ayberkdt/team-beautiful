# A_ZuluagaGomez2020_ASR_benchmark_Interspeech — ASR benchmark for ATC (MALORCA, ATCOSIM, Airbus, LDC, UWB, HIWIRE)

## Citation
Zuluaga-Gomez, J., Motlicek, P., Zhan, Q., Veselý, K., Braun, R. (2020). "Automatic Speech Recognition Benchmark for Air-Traffic Communications." Proc. Interspeech 2020, Shanghai, 25–29 Oct 2020. arXiv:2006.10304. DOI 10.48550/arXiv.2006.10304 (ISCA archive: https://www.isca-archive.org/interspeech_2020/zuluagagomez20_interspeech.html — not opened)
URL: https://arxiv.org/abs/2006.10304

Date read: 2026-11-04. Read: full PDF (5 pp.) extracted with PyMuPDF. [D-ag]

## Data [D-ag]
In-domain ATC databases (Table 1): MALORCA 13 h (German/Czech accents), LDC ATCC 72.5 h (US), HIWIRE 28.3 h, ATCOSIM 10.67 h, UWB ATCC 20.6 h (Czech), AIRBUS 45 h (French). Out-of-domain for pre-training: LibriSpeech 960 h, CommonVoice 500 h.
- Train1 38.7 h (ATCOSIM + MALORCA + UWB). Train2 137.7 h (Airbus + LDC + HIWIRE). Tr1+Tr2 176.4 h.
- Test sets: ATCOSIM 2.5 h (speaker split 80/20), Prague 2.2 h, Vienna 1.9 h, Airbus 1 h (350 utterances self-made; the official 2018 Airbus challenge eval set was not released).
- SNR: not reported. Paper names "accents from non-English speakers, cockpit noise".

## Metric [D-ag]
WER, Kaldi LF-MMI hybrid models, 3-gram / 4-gram / 6-gram LM.

## Numbers (Table 3), WER % with 4-gram LM unless noted [D-ag]
| System | Vienna | Prague | Airbus | ATCOSIM |
|---|---|---|---|---|
| TDNNF-B, out-of-domain only (LibriSpeech + CommonVoice, ~1500 h) | 95.8 | 43.3 | 77.5 | 63.4 |
| TDNNF-TF-B adapted on Train1 | 7.1 | 9.0 | 51.4 | 7.3 |
| TDNNF-TF-B adapted on Train2 (accents not matched) | 26.2 | 17.8 | 14.6 | 20.5 |
| TDNNF Tr1+Tr2 | 6.6 | 7.9 | 14.4 | 5.2 |
| CNN+TDNNF Tr1+Tr2 | 6.7 | 7.9 | 14.7 | 5.1 (5.0 with LM-3) |
| TDNNF-BPE (6-gram) | 7.6 | **5.1** | 15.1 | 7.2 |
- Headline: average 7.75% WER over the four test sets. BPE gave 35% relative improvement on Prague. Compared to earlier MALORCA work: −29.8% (Vienna) and −37.9% (Prague) relative WER.

## Failure modes reported [D-ag]
- Out-of-domain (read, clean) speech models fail on ATC: 43–96% WER. "The ATC data is more noisy, the speakers talk much quicker, and the accents are stronger."
- Accent mismatch: Airbus test with Train1 (no French data) gives 51% WER, vs 14.6% when Airbus data is in training.
- OOV words and phonetic near-confusions, with the paper's examples: "hold in position" vs "holding position"; "climb to two thousand" vs "climb two two thousand".
- The Prague BPE advantage came entirely from fewer deletions (5x more deletions in word-based models), because OOV words are dropped.

## Relevance to us [Y]
- This is the reference for "generic ASR does not work" (43–96%) and for "multi-accent ATC data beats single-site data".
- The "to/two" example is a concrete number-confusion risk: "climb to two thousand" vs "climb two two thousand" (2000 vs 22000 ft). The display should check values for plausibility against aircraft state and envelope (e.g. ±altitude change limits, current FL).
