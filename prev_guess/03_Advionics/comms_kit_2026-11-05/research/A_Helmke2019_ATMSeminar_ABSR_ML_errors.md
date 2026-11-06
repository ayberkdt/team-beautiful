# A_Helmke2019_ATMSeminar_ABSR_ML_errors — Per-command-type recognition and error analysis (MALORCA Prague/Vienna) plus AcListant recap

## Citation
Helmke, H., Kleinert, M., Rataj, J., Motlicek, P., Klakow, D., Kern, C., Hlousek, P. (2019). "Cost Reductions Enabled by Machine Learning in ATM — How can Automatic Speech Recognition enrich human operators' performance?" 13th USA/Europe ATM R&D Seminar (ATM2019), Vienna.
Open copy: https://www.lsv.uni-saarland.de/wp-content/publications/2019/HelKlei19.pdf
(Original AcListant-Strips paper: Helmke, Ohneiser, Mühlhausen, Wies, "Reducing controller workload with automatic speech recognition", DASC 2016, DOI 10.1109/DASC.2016.7778024. Not read; DLR elib has no full text, https://elib.dlr.de/105778.)

Date read: 2026-11-04. Read: full PDF (10 pp.) extracted with PyMuPDF and keyword-searched. [D-ag]

## Data [D-ag]
- Vienna test: 4211 commands from 3.84 h speech (21.1 h radar time). Prague test: 5339 commands from 4.69 h speech (25.7 h radar time).
- Training: ~4–5 h transcribed plus 18 h untranscribed per site.
- AcListant manual adaptation for one approach (Düsseldorf) cost about 1.3 M€.

## Metric definitions [D-ag]
- RR: correctly recognised and not rejected commands / given commands. Correct means callsign + type + value + qualifier are all right.
- ER: recognised commands that were not spoken and not rejected / given commands.
- PRR / PER: the same rates for pure ASR, without the command-prediction filter.
- CpER: share of given commands not predicted by the command predictor.

## Numbers [D-ag]
Vienna (Table 1), 0% → 100% untranscribed data used:
- RR 60.0 → 85.2%; ER 1.6 → 3.2%; PRR 67.2 → 86.4%; PER 18.9 → 6.6%; CpER 15.2 → 3.2%; predicted commands per situation 14 → 53.

Prague (Table 2):
- RR 79.8 → 91.9%; ER 0.29 → 0.60%; PRR 85.9 → 93.7%; PER 7.90 → 2.4%; CpER 8.1 → 2.3%.

Context filtering trade-off: in Vienna, PER 6.6% falls to ER 3.2% at the cost of RR 86.4% falling to 85.2%. Wrong outputs are removed, plus a few correct ones.

Per command type, pure ASR (Table 3), Vienna / Prague:
| Type | Vienna PRR / PER | Prague PRR / PER |
|---|---|---|
| All | 86.4 / 6.6% | 93.7 / 2.4% |
| DIRECT_TO | 79.8 / 12.8% | 87.3 / 4.6% |
| HEADING | 97.2 / 3.6% | 95.4 / 3.6% |
| TURN (rare) | 38.1 / 0% | 0 / 0% |
- DESCEND on Prague: 97.5% recognition, 0.2% error, with more than 930 training examples. MAINTAIN HEADING had only 16 training examples.
- Below-average types (two sites): MAINTAIN SPEED 31% / 85%; ALTITUDE 54% / 0%; MAINTAIN_ALTITUDE 60% / 80%.
- Extrapolation: 8x more data could give RR 90.2% (Vienna) and 92.6% (Prague).
- AcListant recap: Düsseldorf simulator, 50–65 l kerosene saved per flight. Shore et al. pilot study: command error below 5%.

## Failure modes reported [D-ag]
- Rare command types cannot be learned (24 ontology types never observed; e.g. TURN, TURN_BY, SQUAWK seen < 25 times).
- Unseen waypoints in DIRECT_TO (PR511, POLOM, ODNEM...). Spoken names mapped wrongly ("vlasim" → VLM not modelled).
- Annotator disagreement on the same utterance (4 different annotations of "resume own navigation proceed direct rapet"). This led to the PJ.16-04 ontology.
- Plausibility heuristics used: CLIMB for inbounds is rare; QNH does not change by 10 hPa within five minutes.

## Relevance to us [Y]
- Error rates differ hugely by command type. Altitude/descend is well recognised with enough data (97.5%), but DIRECT_TO waypoints (unseen names) are weak. A cockpit system can load the FMS database and the active route as vocabulary, which directly attacks the DIRECT_TO failure.
- Ready-made plausibility rules transfer to the cockpit: QNH vs last QNH, climb vs descent vs current phase, heading-change magnitude.
- Report RR and ER separately on our display slide. A "reject → ask" path is the safe design.
