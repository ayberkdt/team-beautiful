# A_PJ10-W2-96_ASR_TRL6_Openday2022 — SESAR PJ.10-W2 Solution 96 ASR (TRL6), Leonardo open-day slides

## Citation
Mansi, S. (Leonardo, Sol.96 leader) (2022). "PJ.10-W2 PROSA Sol.96 ASR — Benefits of Speech Recognition in Air Traffic Control Management." SESAR 2020 open day, EXE-05, Oslo, 26 Sep 2022 (slides, 10 pp.). SESAR JU grant 874464.
URL: https://www.sintef.no/contentassets/70a888aa746f4206a46b81b8304f8c16/nr-7-mansi-sesar-3-ju-_-pj.10-_-w2_sol.96-asr_openday-29th-pf-september-oslo.pdf

Date read: 2026-11-04. Read: full PDF text extracted with PyMuPDF. [D-ag]

## Content [D-ag]
- Partners: Leonardo, DLR, NLR, ANS CR, Austro Control/COOPANS, Croatia Control/COOPANS, ENAIRE, Indra, SINTEF. Medium TMA and en-route; ATCos are the end users.
- TRL6 real-time simulations: Leonardo Rome 05-2022; ACG at Brunswick 10-2022; ENAIRE Madrid 11-2021; SINTEF Oslo 09-2022. Target release 30-04-2023.
- Lineage: Wave 1 PJ.16-04 defined the ontology. Wave 2 PJ.10-96 integrates ASR into an operational-like controller working position.
- HMI pattern (useful for us): recognised commands are pre-filled into the radar label **in yellow**. If not rejected **within 10 seconds** they turn normal green. Commands are shown while the ATCo is still speaking. The callsign is highlighted when recognised in pilot or controller utterances. If the flight is CPDLC-equipped, the CPDLC command mask opens instead.
- No recognition-rate numbers are on the slides.

## Failure modes
None quantified on the slides.

## Relevance to us [Y]
- This is a proven, SESAR-validated confirmation pattern: "tentative colour → auto-accept after timeout unless rejected". We can mirror it in the cockpit: an amber "heard" state, then white/green after own readback matches, and red if the readback differs.
- It shows the industry path ontology → CWP integration at TRL6. On the cockpit side there is no equivalent SESAR solution in what I read. That gap is our niche (inference from the sources read in this session, not an exhaustive search).
