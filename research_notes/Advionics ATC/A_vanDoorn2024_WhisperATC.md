# A_vanDoorn2024_WhisperATC — Whisper-ATC: open Whisper models fine-tuned on ATCO2 / ATCOSIM

## Citation
van Doorn, J. L., Sun, J., Hoekstra, J. M. (with Jonk, P., de Vries, V. in the repository record; author lists differ between sources) (2024). "Whisper-ATC: Open Models for Air Traffic Control Automatic Speech Recognition with Accuracy." International Conference on Research in Air Transportation (ICRAT 2024), Singapore. TU Delft repository: https://repository.tudelft.nl/record/uuid:8e02d222-5775-441d-94d2-96c26156cf43
Related MSc thesis: van Doorn, "Applying Large-Scale Weakly-Supervised Automatic Speech Recognition to Air Traffic Control", http://resolver.tudelft.nl/uuid:8aa780bf-47b6-4f81-b112-29e23bc06a7d
Code and models: https://github.com/jlvdoorn/WhisperATC ; https://huggingface.co/jlvdoorn

Date read: 2026-11-04. **The paper PDF could not be opened**: TU Delft repository refused the connection (ECONNREFUSED) twice; file links returned 0 bytes. The GitHub README and one HF model card were read. [D-ag only where marked]

## Data
- ATCO2-ASR (HF doi 10.57967/hf/1377), ATCOSIM (10.57967/hf/1378), and the combination (10.57967/hf/1379). The combination is used only for training. [D-ag, GitHub README]
- Split: "A random split is made in the data where 80% will be used for training and 20% for validaiton [sic]". [D-ag, README]
- Another paper (A_Wee2025) says the ATCO2 model was trained on only 2 h of ATCO2-released data. [D-ag in Wee2025; consistent with the 1 h free ATCO2 set plus partner data — not verified]

## Numbers
- ATCO2: WER 13.5%; ATCOSIM: WER 1.17% random split, 3.88% speaker split. Region-specific fine-tuning gives "up to 60%" improvement in real-world scenarios. [A — search-engine snippet of the TU Delft record, not read in the paper]
- Wee et al. 2025 cite Whisper-ATC at 1.19% WER on ATCOSIM. [D-ag in A_Wee2025]
- HF model card jlvdoorn/whisper-large-v3-atco2-asr: final eval WER 17.04% (range 16.33–20.42% over checkpoints); the evaluation set is not stated ("More information needed"). [D-ag]
- Independent cross-test (Wee 2025, their pipeline): jlvdoorn/large-v3-atco2-asr gets WER 37.6% on ATCO2, 46.3% on ATCOSIM, 55.3% on SEA-accented. [D-ag in A_Wee2025]

## Failure modes
- Random utterance split vs speaker split: 1.17% vs 3.88% on ATCOSIM, about 3x worse with unseen speakers. [A]
- Third-party evaluation gives much higher WER than the authors' own (17% vs 38% on ATCO2), so normalisation and test subset matter a lot. [D-ag numbers; reason is my inference]
- ATCOSIM is simulated studio speech (clean), so 1–4% WER there does not transfer to VHF.

## Relevance to us [Y]
- Open weights exist (Apache/MIT-style HF models; license not checked). A prototype could start from jlvdoorn/whisper-large-v3-atco2-asr rather than raw Whisper.
- To be honest in the pitch, quote three numbers: about 1–4% on clean simulated speech, 13–17% on in-domain VHF (authors), and about 38–55% cross-domain (independent). That spread is exactly the "degraded communication" problem in the challenge.
- TODO if time: retry the TU Delft PDF to upgrade the [A] values to [D-ag].
