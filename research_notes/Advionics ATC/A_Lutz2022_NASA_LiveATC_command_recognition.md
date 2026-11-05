# A_Lutz2022_NASA_LiveATC_command_recognition — NASA Ames: ASR + command recognition on LiveATC (KLAX), Appareo ASR, readback latency

## Citation
Lutz, M., Chatterji, G. (Crown Consulting at NASA Ames), Idris, H. (NASA Ames) (2022). "Characterization of Response Times based on Voice Communication and Traffic Surveillance Data." NASA NTRS 20220007116, file name indicates AIAA AVIATION 2022 (venue not stated in the extracted text; treat as [A]).
URL: https://ntrs.nasa.gov/citations/20220007116 (PDF: .../20220007116_Lutz_Aviation2022_NLP.pdf)

Date read: 2026-11-04. Read: full PDF (12 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]

## Data [D-ag]
- Voice: LiveATC.net, KLAX Approach Zuma/NW Arrival, 124.500 [MHz; paper writes "Hz"], 24 h on 1 Mar 2022. Tracks: ADS-B Exchange within 150 NM.
- Truth set: 600 transmissions, labelled by an IFR-rated pilot (1500+ h) who listened to the audio.
- ASR: Appareo Systems model (bi-directional LSTM). Trained on 500 h ATC plus ~6000 h of general audio.
- SNR: not reported. LiveATC is VHF receiver audio.

## Metric [D-ag]
- CRR: share of altitude, heading and speed commands with correct category and value.
- CDR: callsign detection rate. Callsigns are matched to ADS-B callsigns using Levenshtein distance.

## Numbers [D-ag]
- Appareo ASR: "6% WER on live cockpit ATC radio channels" (vendor-reported, cited by the authors; not measured in this paper).
- Off-the-shelf AWS ASR: about 62% WER on their expert-transcribed historical FAA audio.
- Table 4, CRR / CDR:
| | Altitude | Heading | Speed | All commands | Callsign |
|---|---|---|---|---|---|
| vs ASR transcription | 95.1% | 92.6% | 82.3% | 90.0% | 99.8% |
| vs truth (audio) | 94.2% | 91.4% | 70.2% | 85.3% | 83.4% |
- Pilot readback latency is about 0.6 s on average.
- Delay from end of clearance to maneuver start: about 17 s for altitude and heading, 25 s for speed. To maneuver end: 176 s, 69 s and 182 s.
- Literature they cite: Airbus 2018 challenge best WER 7.62%; callsign detection 95% (ref. 7) and 96.3% (ref. 9); NER F1 95.3%.

## Failure modes reported [D-ag]
- Speed commands are hardest (70.2%). The rule set misses phrases like "return to normal speed" and "maintain present speed".
- Callsign detection drops from 99.8% (on the transcript) to 83.4% (vs truth) because of airline and operator telephony names. The authors propose more training on airline names.
- Internal cockpit chatter must be filtered (Appareo segments by pause timeout).

## Relevance to us [Y]
- This is the only source read in this session with a WER figure from **cockpit-side** ATC radio: 6%, vendor claim, not independently verified. It shows that commercial cockpit-oriented ATC ASR exists (Appareo).
- Generic cloud ASR at ~62% WER on ATC confirms the Whisper zero-shot results (A_Wee2025) from another vendor.
- Per-command reliability ranking (altitude > heading > speed) is useful for the display. We could show speed commands with lower default confidence.
