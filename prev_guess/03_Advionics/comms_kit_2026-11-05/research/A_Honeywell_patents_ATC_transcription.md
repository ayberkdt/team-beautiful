# A_Honeywell_patents_ATC_transcription — Honeywell US 12118982 B2: real-time constrained ATC transcription (cockpit)

(Second Honeywell patent is in its own file: A_Honeywell_US12322410_unsplit_segments.md)

## Citation
Agarwal, J., Thippeswamy, M. M. — Honeywell International Inc. "System and method for constraining air traffic communication (ATC) transcription in real-time." US 12118982 B2. Priority 11 Apr 2022 (IN 202211021488); filed 24 May 2022; published 15 Oct 2024.
URL: https://patents.google.com/patent/US12118982B2/en

Date read: 2026-11-04. Read via WebFetch (model summary of the first 100 000 of 124 471 characters). [D-ag, via fetch summary]

## Content
- An event detector catches flight-plan changes and flight-phase transitions from pilot input (highest priority), FMS data, ATC clearance data, and checklist/log.
- A keyword generator builds a wordlist: airports, NAVAIDs, procedures, SID/STAR, waypoints, callsigns.
- The system selects a pre-built constrained speech model covering the wordlist, or generates a new one and stores it.
- Triggers include radio handover clearances, clearance templates, and pilot checklist status. A mobile app can also trigger reconfiguration.
- Stated aims: lower memory and latency. No WER, accuracy or latency numbers.

## Not read (titles only, from search) [A]
Other cockpit ATC-transcription filings surfaced in search (assignee not checked): merging/splitting messages with user input (US 11983211), clearance playback in preferred accent/language (US 11289094), cockpit display for ATC conditional clearances (US 10157617), extracting speaker information (US 11961524), transcription playback with variable emphasis (US 12008289).

## Failure mode addressed
Unconstrained vocabulary (waypoints, procedures, callsigns) causes recognition errors. Their answer is a flight-plan-driven constrained LM. This matches the MALORCA/ATM2019 DIRECT_TO failure (unseen waypoints).

## Relevance to us [Y]
- A major avionics OEM is actively patenting cockpit ATC transcription. Cite as prior art and differentiate, e.g. on degraded-comm robustness, confidence/verification UX, and readback cross-check. A real product would need a freedom-to-operate check.
- No Honeywell product launch was found in this session's searches (search results only, not exhaustive).
