# A_Pellegrini2019_Airbus_ATC_challenge — Airbus ATC speech recognition challenge 2018 (ASR + callsign detection)

## Citation
Pellegrini, T., Farinas, J., Delpech, E., Lancelot, F. (2019). "The Airbus Air Traffic Control speech recognition 2018 challenge: towards ATC automatic transcription and call sign detection." Proc. Interspeech 2019. arXiv:1810.12614 (v2, 10 Mar 2020). IRIT / Université Paul Sabatier and Airbus, Toulouse.
URL: https://arxiv.org/abs/1810.12614

Date read: 2026-11-04. Read: full PDF (5 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]. Interspeech 2019 venue taken from the citation in HAAWAII papers ([16] there, which says 2020) and my memory; not checked on the ISCA site. [A] for venue.

## Data [D-ag]
- Airbus corpus (not public), Toulouse-Blagnac. 50 h manually transcribed were used: 40 h train, 5 h eval. Utterances are isolated and shuffled, with metadata removed.
- Mix: pilots 54%, controllers 43%, ATIS 3%. Approach 72%, tower 25%. Approach/tower utterances average ~4.3–4.5 s; ATIS ~28–31 s.
- Audio: described as "bad (VHF quality + noise)", diverse non-native accents, high speech rate, code-switching, possible Lombard effect. SNR not quantified.
- 22 teams submitted.

## Metric [D-ag]
WER (lower-cased, equal weights). Callsign detection (CSD) F1. Ranking used the harmonic mean of normalised (1 − WER) and normalised F1.

## Numbers [D-ag]
- Best (Vocapia-LIMSI): WER 7.62% (ins 1.29 / del 3.14 / sub 3.19); CSD F1 82.41% (precision 81.99%, recall 82.82%).
- Other top-5 WERs: 8.42%, 8.76%, 9.41%, 9.55%. Top-5 CSD F1 is about 77–82%.
- Best system by subgroup (Table 4): WER ATIS 5.1%, approach 8.1%, tower 7.8%, **controllers 5.5%, pilots 10.5%**, female 5.5%, male 8.2%. CSD F1: controllers 86.8%, pilots 79.0%. I read the 6 F1 values as approach/tower/C/P/F/M because ATIS has no callsigns; the column mapping is my reading.
- "Transcribing pilots' speech was found to be twice as harder [sic]".
- Deletions and substitutions (~3%) are about twice as frequent as insertions (~1.5%). Precision exceeds recall for most CSD systems, so missed callsigns are more frequent than false ones.

## Failure modes reported [D-ag]
- Adding external data gave no gain or a loss. The eval set is very close to train. The authors call this "a robustness issue".
- Pilot speech (VHF-received in this corpus) has about 2x the WER of controller speech.
- Callsigns are missed more than hallucinated.

## Relevance to us [Y]
- Airbus itself framed pilot-side benefits (listening for own callsign, understanding accented or noisy messages, remembering clearances). That is exactly our use case. Citable as sponsor-adjacent motivation (Airbus authorship, read).
- ~7.6% WER and ~82% callsign F1 on a single-airport closed set is the 2018 SOTA. Generalisation was not shown.
- Missed-callsign dominance means a cockpit system should fail "silent" for own callsign rarely. Tune for recall on own callsign, since we know it in advance.
