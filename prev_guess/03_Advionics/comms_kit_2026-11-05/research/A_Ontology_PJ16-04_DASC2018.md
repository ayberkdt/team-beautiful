# A_Ontology_PJ16-04_DASC2018 — Common ontology for ATC command transcription (SESAR PJ.16-04)

## Citation
Helmke, H., Slotty, M., Poiger, M., Ferrer Herrer, D., Ohneiser, O., Vink, N., Cerna, A., Hartikainen, P., Josefsson, B., Langr, D., García Lasheras, R., Marin, G., Mevatne, O. G., Moos, S., Nilsson, M. N., Boyero Pérez, M. (2018). "Ontology for Transcription of ATC Speech Commands of SESAR 2020 Solution PJ.16-04." IEEE/AIAA 37th Digital Avionics Systems Conference (DASC), London, 23–27 Sep 2018. DOI 10.1109/DASC.2018.8569238.
Open copy: https://elib.dlr.de/123237/ (PDF 2018-10-01-PJ16-04-DASC-contribution-V-2-00.pdf)
Organisations: DLR, DFS, Frequentis, CRIDA/ENAIRE, NATS, ANS CR, Integra, LFV, Romatsa, Avinor, Thales, Indra, EUROCONTROL. SESAR grant 734141.

Date read: 2026-11-04. Read: full PDF (10 pp.) extracted with PyMuPDF. [D-ag]

## Structure of the ontology [D-ag]
- Utterance → one or more **instructions**, each prefixed with the **callsign** (or NO_CALLSIGN). The callsign is repeated per instruction even if spoken once. "break break" separates callsigns.
- Instruction = **Command** + optional **Condition(s)**.
- Command = **Type** (1–2 words) + **Value(s)** + **Unit** + optional **Qualifier**.
  - Units: FL, ft, none (altitude); kt, MA (speed); ft_min (vertical speed); NM.
  - "none" records that no unit was said. Example: FL vs ft ambiguity is kept explicit.
  - Qualifiers: LEFT, RIGHT, none (heading is mostly mandatory); BELOW, ABOVE, OR_BELOW, OR_ABOVE; OR_LESS, OR_GREATER.
- Condition = Conjunction (UNTIL / WHEN / IF) + Requirement (PASSING, REACHING altitude/FL/waypoint, ESTABLISHED LOC, INTERCEPT_GLIDEPATH, TOUCHDOWN_DISTANCE x NM, COMPLETED, READY, ABLE).
- Examples from the paper:
  - "csa one yankee golf left turn zero four zero" → `CSA1YG HEADING 040 LEFT`
  - "lufthansa two alpha maintain flight level one one zero" → `DLH2A MAINTAIN_ALTITUDE 110 FL`
  - "tower one one eight one five" → `TAP1LW CONTACT TOWER` + `TAP1LW CONTACT_FREQUENCY 118.150` (frequency always 6 digits)
  - "...descend with fifteen hundred feet per minute or greater until passing flight level seven zero" → `FIN5KA RATE_OF_DESCENT 1500 ft_min OR_GREATER UNTIL PASSING ALTITUDE 70 FL`
  - "...when established localizer reduce speed one six zero knots ... until four miles final" → `CSA707H REDUCE 160 kt WHEN ESTABLISHED LOC UNTIL TOUCHDOWN_DISTANCE 4 NM`
- Command categories: vertical (DESCEND, CLIMB, ALTITUDE, STOP_*, MAINTAIN_ALTITUDE), horizontal (HEADING, TURN_BY, DIRECT_TO, TRANSITION...), speed, holding, vertical speed, frequency change (CONTACT), report/request, landing clearances (CLEARED ILS RW26), taxi (LINEUP, VACATE, HOLD_SHORT...), clearance delivery, information (QNH, WINDSPEED), VFR, misc (CORRECTION, CALL_YOU_BACK).
- Size: about 100 command types in 14 categories. Approach, en-route, tower and ground are covered.
- Design rule: transcribe what was said, not what is implied. ALTITUDE stays ALTITUDE even if the context implies CLIMB. This differs from CPDLC.
- Predecessor AcListant ontology: only 4 elements (callsign, type, value, unit) and more than 30 types. It "reaches its limits" in MALORCA (conditional clearances, QNH, EXPECT_RUNWAY).

## Numbers in this paper [D-ag]
- MALORCA used only ~50 h of data. Chen & Kopald (MITRE) used 130 h. Google used >200 000 h (as cited).
- NATS ASR project 2002–2006 (London Terminal): >600 utterances per controller per hour at Heathrow approach. A recognition rate above 80% was needed for operational use, and no tested engine (Frequentis test system, Nuance 8.5, Telisma) met it.
- One NATS approach sector: more than 20% of utterances are information or courtesy (non-standard).
- AcListant: 95% command recognition rate with < 2% error rate. AcListant-Strips: radar-label workload reduced by a factor of three, and 60 l kerosene per flight saved (as cited, original not read).
- >9000 controller commands transcribed for MALORCA, >11 000 for AcListant-Strips.
- CRIDA (590 h transcribed): altitude commands are 5–15% of commands in upper sectors and 17–24% in lower sectors.
- Stated industry ASR activities: DFS VRR (BBN HARK AVOKE, since 2011, training), ENAIRE/CRIDA "VOICE" (since 2008), Frequentis (ASR in electronic strips; multi remote tower with DFS), Indra (training ASR, >50 words), Thales "Shape" (Nuance Recognizer 10 + hypotheses engine).
- CPDLC is mandatory oceanic only. GOLD manual: voice is preferred below 10 000 ft AGL.

## Failure modes / design issues reported [D-ag]
- ASR gives hypotheses with plausibilities, e.g. "REDUCE 160 kt" 0.9 vs "HEADING 160 LEFT" 0.6. A "Post Evaluation" module using mode-S, predicted commands, and EFS input is needed to reduce this to one command.
- Implicit readbacks (taxi) mean concept extraction is necessary but not sufficient for readback checks.
- Non-standard and conversational phrasing even by native speakers ("lapsing into conversational terms").

## Relevance to us [Y]
- Use this ontology as our display data model: callsign / type / value / unit / qualifier / condition. It is agreed by ~20 European stakeholders and is the HAAWAII format, so the judges will recognise it.
- Keep "unit = none" visible. If FL or ft was not heard, the display should say so rather than guess. This directly mitigates the FL vs altitude confusion.
- Conditions (WHEN/UNTIL/IF) must be shown as conditions, not as immediate actions. HAAWAII showed these are exactly what extractors miss.
- A cockpit-side Post Evaluation can use own-ship data (current FL/heading/speed, FMS route, tuned frequency) to resolve hypotheses.
