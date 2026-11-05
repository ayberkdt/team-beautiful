# A_HAAWAII_readback_SID2022 — Readback error detection by ASRU (HAAWAII, Isavia + NATS)

## Citation
Helmke, H., Ondřej, K., Shetty, S., Arilíusson, H., Simiganoschi, T. S., Kleinert, M., Ohneiser, O., Ehr, H., Zuluaga-Gomez, J., Smrz, P. (2022).
"Readback Error Detection by Automatic Speech Recognition and Understanding — Results of HAAWAII project for Isavia's Enroute Airspace."
12th SESAR Innovation Days (SID 2022), Budapest, 5–8 Dec 2022.
URL: https://www.sesarju.eu/sites/default/files/documents/sid/2022/paper_3.pdf
Project: HAAWAII (SESAR JU, H2020 grant 884287). Partners in author list: DLR, Brno Univ. of Technology, Isavia ANS, Idiap.

Date read: 2026-11-04. Read: full PDF text (9 pages) extracted with PyMuPDF. [D-ag]

## Data [D-ag]
- Validation airspaces: NATS London approach area and Isavia ANS (Iceland) en-route/oceanic.
- Readback evaluation set: 7.7 h (silence-reduced) Isavia ops-room recordings, 21 Jul – 2 Sep 2020; ~40 of ~90 Isavia ACC/OAC ATCos.
- 3090 ATCo + 3630 pilot utterances manually transcribed (only half manually annotated); 6720 utterances grouped into 2200 communication threads; 87 readback-error samples after manual classification.
- Training for data-driven readback detector: 129 000 synthetic pairs (79 000 with errors, 8 error kinds; 50 000 correct) generated from 37 441 manually transcribed HAAWAII utterances (NATS + Isavia).
- Proof-of-concept: 6 Isavia ATCos, 2 days in May 2022, 76 ATCo + 76 pilot utterances; 51 with readback error (20 altitude, 11 speed, 4 DIRECT_TO, 1 frequency, 4 runway, 8 squawk), 25 correct.
- SNR of data: not stated in this paper. Described as "noisy voice data from the operations room". [D-ag]

## Metrics and how measured [D-ag]
- WER: Levenshtein distance on words.
- Command-level extraction rate and error rate: share of utterances whose complete set of commands (with conditions) is extracted correctly, or wrongly.
- Callsign-level extraction rate and error rate.
- "Unkn rate": share of recognised words that the extractor did not use.
- Readback detection: D-RB (detected), FA (false alarms), Detect. (recall), FAR = 1 − precision, Acc., F1.

## Numbers — ASR + text-to-concept, rule-based (Table II) [D-ag]
| ANSP | Speaker | WER | Cmd extract | Cmd error | Callsign extract | Callsign error | Unkn |
|---|---|---|---|---|---|---|---|
| NATS | ATCo | 2.8% | 93.2% | 3.6% | 97.5% | 2.3% | 10.2% |
| NATS | Pilot | 7.1% | 79.9% | 11.5% | 95.9% | 2.9% | 10.2% |
| Isavia | ATCo | 2.9% | 92.3% | 4.3% | 96.9% | 2.4% | 15.3% |
| Isavia | Pilot | 10.4% | 71.3% | 9.7% | 88.4% | 5.8% | 18.8% |
| NATS gold text (WER 0) | ATCo | 0% | 96.4% | 1.7% | 98.5% | 1.3% | 10.7% |
| NATS gold text | Pilot | 0% | 91.5% | 3.1% | 97.7% | 1.7% | 10.0% |
| Isavia gold text | ATCo | 0% | 93.9% | 4.2% | 97.6% | 1.7% | 15.6% |
| Isavia gold text | Pilot | 0% | 88.3% | 5.4% | 96.4% | 1.7% | 16.1% |

Data-driven extractor (T5 fine-tuned, Table III) is worse: e.g. NATS ATCo cmd extract 89.9% (vs 93.2%), Isavia pilot 66.4% (vs 71.3%). Rule-based "slightly, but significantly" better. [D-ag]

## Numbers — readback error detection [D-ag]
Ops-room, 87 real readback-error samples (Table V):
| Setting | Detected | FA | Detect. | FAR | Acc. | F1 |
|---|---|---|---|---|---|---|
| Gold annotation | 84 | 19 | 97% | 18% | 99% | 88% |
| Gold transcription | 82 | 113 | 94% | 58% | 95% | 58% |
| Data-driven alone | 37 | 133 | 43% | 78% | 92% | 29% |
| Rule-based alone | 72 | 163 | 83% | 69% | 92% | 45% |
| Combined | 71 | 145 | 82% | 67% | 93% | 47% |

Proof-of-concept (Table VI): combined 82% detection, 13% FAR, F1 85%. Abstract says 80% / 11%; the table and conclusion say 82% / 13%. Internal inconsistency; use the table values. [D-ag]
Synthetic validation set: 98.1% detection, 1.6% FA (not comparable to real data). [D-ag]

## Base rates from this paper [D-ag]
- "Between one and two percent of the utterances contain a readback error."
- Ops data: 4% of 2200 threads contain a readback-error sample, which is 1.3% of utterances.
- Of 87 samples: 12% wrong readback, 51% missing readback, 22% hearback (not corrected), 15% other (Table VIII).
- Cited literature (not read here, [A] for the originals): en-route ATCos detect 90% of readback errors (Cardosi 1993). Tower and approach ATCos detect 63% and 50% (Cardosi 1994; Morrow 1993). ~40% of miscommunications lead to altitude deviations, ~20% involve similar callsigns (van Es 2004). 10% are speed/heading mix-ups (Bürki-Cohen 1995).

## Failure modes reported [D-ag]
- Text-to-concept is the weakest link: FAR jumps 18% to 58% from gold annotation to gold transcription. Adding real ASR only raises it from 58% to 67%.
- Pilot utterances are shortened and abbreviated: pilot command extraction drops to 71–80% vs ~92–93% for ATCos.
- No flight plan data for Isavia: 10% of addressed callsigns were not in the surveillance data.
- Rare or non-standard phrasing is not extracted: "on conversion" (speed change at Mach/IAS switch), time restrictions ("cross rapax 0838 or later"), "free speed".
- Data-driven extractor hallucinates: "completely wrong or nonsensical outputs". It is also harder to certify.
- Low base rate inflates the false-alarm rate. The authors' arithmetic: 85% correct classification gives about 88% FAR.
- A dropped final word ("victor" in a spelled waypoint) caused a false readback error.

## Relevance to us [Y]
- A cockpit display that shows recognised clearances must accept that pilot-side or degraded speech gives ~10% WER and only 71–80% fully correct command extraction, even with surveillance context.
- Comparing on concepts beats comparing on words (Table I example: same meaning, different words). Our display should compare structured (callsign, type, value, unit) tuples, not text.
- Readback errors are rare (~1–2% of utterances). Any alerting must be designed around false alarms. 67% FAR on real ops data is the published reality check.
- Callsign extraction stays at 88–96% even when command extraction degrades. Callsign-gating ("is this message for me?") is the most robust first function.
