# A_vanEs2004_EUROCONTROL_air-ground_comm — EUROCONTROL Air-Ground Communication Safety Study (444 European incidents)

## Citation
van Es, G. (NLR) (2004). "Air-ground communication safety study: An analysis of pilot-controller occurrences." EUROCONTROL, European Air Traffic Management Programme, Edition 1.0, 16 Jun 2004, status "Released Issue", intended for General Public.
URL read (third-party mirror, not EUROCONTROL-hosted): https://www.leonardo-in-flight.nl/PDF/com_report_1[1].0.pdf
Official landing page for the follow-up action plan: https://www.eurocontrol.int/publication/european-action-plan-air-ground-communications-safety (not read)
Follow-up: Wever, R., van Es, G., Verbeek, M. (2006) "Air-Ground Communications Safety Study — Causes and Recommendations", Ed. 1.1 (SKYbrary bookshelf, not read [A]).

Date read: 2026-11-04. Read: full PDF text (50 pp.) extracted with PyMuPDF and keyword-searched. The document header matches EUROCONTROL format; authenticity of the mirror was not independently checked. [D-ag]

## Data [D-ag]
444 air-ground communication incidents in Europe, 2002 – Aug 2003. Commercial aircraft ≥ 5700 kg MTOM. These are 1% of all reported occurrences and 23% of ATC-related occurrences.

## Numbers [D-ag]
- Rate: 1.4 communication occurrences per 10 000 flights, and 2.4 per million instructions or clearances (on an estimated 183 million clearances).
- Generic problem distribution (Fig. 1): readback/hearback error 31%, loss of communication 20%, communication equipment problem 18%, hearback error 5%, no readback 3%, other 24%.
- Consequences (Fig. 2, counts): prolonged loss of communication 139, altitude deviation 92, none 92, wrong aircraft accepted clearance 70, loss of separation 30, runway transgression 25, heading/track deviation 20.
- Consequence of a readback/hearback error (Fig. 8): altitude deviation 38%, wrong aircraft accepted clearance 36%, loss of separation 7%, runway transgression 6%, heading/track deviation 5%.
- 65% of readback/hearback errors happen in climb and descent; 18% in cruise.
- Factors: similar callsign in 20% of occurrences, sleeping VHF receiver in 12%. Top six: similar callsigns, sleeping VHF receivers, frequency change, incorrect readback, radio interference, controller non-standard phraseology.
- Citing Cardosi 1994: < 1% of voice communications contain an error, and 60–80% of those are corrected by pilot or controller.
- Common chain: clearance taken by a similar-callsign aircraft, then altitude deviation. This was 35% of the 55 multi-consequence occurrences.

## Failure modes reported [D-ag]
- Similar callsigns, plus blocked transmissions (two aircraft reading back at once, which the controller hears as "partial or garbled").
- Expectation bias: the report's example is a pilot auto-reading back the usual "cleared to cross" instead of "hold short".
- Sleeping VHF receivers and missed frequency changes lead to prolonged loss of communication.

## Relevance to us [Y]
- The design problem is altitude in climb or descent, plus wrong-aircraft acceptance. That is 74% of readback/hearback consequences. A cockpit display should (1) show the cleared altitude prominently with unit (FL vs ft), and (2) gate on own callsign and warn on similar callsigns heard on frequency.
- "Prolonged loss of communication" is the most common consequence (139/444). A display that tracks "last ATC message heard / frequency handed to" helps with the sleeping-receiver and missed-handover cases. This fits the challenge's "degraded communication" angle.
