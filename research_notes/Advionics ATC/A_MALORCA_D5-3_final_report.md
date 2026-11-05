# A_MALORCA_D5-3_final_report — MALORCA Final Project Results Report (Prague / Vienna approach)

## Citation
MALORCA consortium (DLR, Idiap, Saarland University (USAAR), Austro Control, ANS CR). "D5.3 Final Project Results Report", MALORCA — Machine Learning of Speech Recognition Models for Controller Assistance. SESAR JU / H2020 project 698824. PDF metadata: author Paul Dunkley, dated 7 May 2018, 47 pages.
URL: https://sesarju.eu/sites/default/files/documents/projects/ER1-FPR/698824_MALORCA_D5.3_Publishable%20Project%20Results%20final%20report.pdf
CORDIS: https://cordis.europa.eu/project/id/698824/reporting (not read, snippet only [A])

Date read: 2026-11-04. Read: full PDF text extracted with PyMuPDF and keyword-searched. [D-ag]

## Data [D-ag]
- More than 100 h of radar data and controller–pilot voice for Vienna and Prague approach. 20% manually transcribed. 4 h transcribed (silence excluded) for each site was used as the evaluation set. The project started with 2 h transcribed per site and states it relies on "less than 50 hours of in-domain data".
- Audio: "8 kHz mono with low Signal-to-Noise (SNR) ration [sic]". The proposal had assumed 16 kHz and SNR > 20 dB (as in AcListant); this "needed a modification".
- Prague audio is better than Vienna: "SNR 5 dB difference". Absolute SNR values are not given.
- Only approach controller utterances are considered. Radar data is ASTERIX CAT 62.
- Proof-of-concept trials: nine controllers, Prague 23–24 Jan 2018 and Vienna 30 Jan 2018.

## Metric [D-ag]
- Command recognition rate: share of commands (callsign + type + value, e.g. DESCEND 8000 ft, REDUCE 220 kt) recognised correctly.
- Command recognition error rate: a command that is neither correctly recognised nor rejected, so it is wrongly shown to the user.
- Measured by comparing automatic and manual transcriptions/annotations on the 4 h evaluation sets.

## Numbers [D-ag]
| Item | Prague | Vienna |
|---|---|---|
| Basic ABSR command recognition rate (before learning) | 79.8% (~80%) | 60.0% |
| After unsupervised learning, command recognition rate | 91.9% (~92%) | 85.2% (also reported as 83% and 85%) |
| Command recognition error rate, baseline → trained | 7.9% → < 0.6% | 18.9% → 3.2% (another passage says "below 3.8%") |
| Command hypotheses predictor: cmd error rate | 15.4% → 1.0% | 19.7% → 4.2% |
| Average context size (predicted commands) | < 650 | < 1600 |

Other numbers [D-ag]:
- The plausibility checker cut the command recognition error rate from 10% to 2%, at the cost of rejecting some correct commands.
- Statistical LM vs grammar: −50% relative command error rate.
- Overall improvement: "approximately 15 – 20% absolute" in recognition rates.
- The report contains inconsistent Vienna values (83% / 85% / 85.2%; 3.2% / 3.8%). Quote ranges, not a single value.

## AcListant / AcListant-Strips numbers as quoted in this report [D-ag; originals not read]
- AcListant (2015, Düsseldorf approach, DLR + Saarland Univ.): command error rate below 1.7%, and command recognition rates up to 95% with error rates below 2%.
- AcListant-Strips: three times less clicking time for controllers, up to two more arrivals per hour, flight time −77 s per aircraft, 50–65 € (another passage says 50–65 litres) less fuel per A320 flight.
- "command recognition rates better than 95%": the controller corrects only one in twenty cases. A 90% rate cuts clicking time by a factor of 10.

## Failure modes reported [D-ag]
- Low SNR and 8 kHz audio. The 5 dB worse SNR in Vienna is given as the main reason for 3.2% vs 0.6% command error.
- Differing semantic interpretation of commands between sites. This motivated the common ontology (see A_Ontology_PJ16-04_DASC2018.md).
- Confidence-score estimation is "still a challenging task not properly addressed".
- Deployment cost: each ABSR model needs manual local adaptation for accents and phraseology deviations.

## Relevance to us [Y]
- Strongest published evidence that context (radar or flight plan, here "situational context") cuts command errors a lot: 18.9% to 3.2% in Vienna. For a cockpit, the equivalent context is own-ship state, FMS flight plan, current frequency and ATIS.
- The SNR effect is real and quantified as relative, not absolute. 5 dB worse SNR came with about 5x more command errors (with other confounders). VHF voice really is 8 kHz narrowband.
- The metric to show judges is command recognition rate plus command error rate, not WER. A rejection (shown as "unclear, verify") is better than a wrong value.
