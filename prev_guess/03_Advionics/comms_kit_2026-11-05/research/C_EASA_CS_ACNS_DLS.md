# C_EASA_CS_ACNS_DLS: Easy Access Rules for Airborne Communications, Navigation and Surveillance (CS-ACNS), CS ACNS.B.DLS.B1.070 / B1.075 CPDLC message sets

- **Issuing body:** EASA. CS-ACNS **Issue 4** (19 May 2022), ED Decision 2022/008/R.
- **URL:** https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-airborne-communications?page=15
- **Date read:** 2026-11-04 (through a summarising fetch tool; message IDs and meanings as returned)

## Content [D-ag]
- B1.070, ATN B1 CPDLC **uplink** messages (selection):
  - UM0 UNABLE; UM1 STANDBY; UM3 ROGER/acknowledge; UM4 AFFIRM; UM5 NEGATIVE;
  - UM19 maintain level; **UM20 CLIMB TO [level]**; **UM23 DESCEND TO [level]**;
  - UM117 CONTACT [unit][frequency]; UM120 MONITOR [unit][frequency];
  - UM123 SQUAWK [code]; UM179 SQUAWK IDENT;
  - **UM157 CHECK STUCK MICROPHONE [frequency]**;
  - UM159 ERROR; UM160 NEXT DATA AUTHORITY; UM162 SERVICE UNAVAILABLE;
  - UM183 free text; **UM190 FLY HEADING [degrees]**; UM227 LOGICAL ACKNOWLEDGEMENT.
  - Also listed: UM26-29, UM46-55, UM74 etc.
- B1.075, **downlink** messages (selection): DM0 WILCO; DM1 UNABLE; DM2 STANDBY; DM3 ROGER; DM4 AFFIRM; DM5 NEGATIVE; DM6 request level; DM18 request speed; DM22 request direct; DM32 present level; DM62 ERROR; DM65/66 due to weather / aircraft performance; DM81/82 can / cannot accept level; DM98 free text; DM100 logical acknowledgement; DM106 preferred level; DM109 top of descent time.
- AMC1 B1.070: response type "A/N" is answered with DM2, DM4 or DM5. Response type "R" is answered with DM2, DM3 or DM1.
- The B1.030 integrity and B1.035 continuity sections and the ED-110B/ED-120 references were only listed in the table of contents. **No latency numbers were obtained.**
- There are **no** approach-clearance messages in this list (no "cleared ILS approach"). The ATN B1 set covers en-route level, heading, direct, contact and squawk.

## Relevance to us [Y]
This is the exact vocabulary of European CPDLC. A "translate the signal" display that turns voice into text would be most useful if it **normalised** spoken clearances into this message structure (e.g. a spoken "climb flight level two hundred" becomes the UM20 [FL200] format). That makes voice and data clearances look the same to the crew. Approach clearances are not part of ATN B1, which leaves a gap for approach guidance.
