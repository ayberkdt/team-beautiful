# C_EASA_SIB_2019_13: EASA Safety Information Bulletin 2019-13, "Controller Pilot Data Link Communications over Very High Frequency Data Link Mode 2, Airborne Multi-Frequency Capability"

- **Issuing body:** EASA (Airworthiness, Operations, ATM/ANS). Issued **11 October 2019**.
- **URL read:** https://ulc.gov.pl/_download/operacje_lotnicze/SIB/EASA_SIB_2019-13_1.pdf (copy hosted by the Polish CAA, ULC)
- **Date read:** 2026-11-04 (PDF text extracted with pdftotext; 2 pages)

## Content [D-ag]
- Reference publications: 29/2009 as amended by 441/2014 (30 April 2014), 2015/310 (26 February 2015) and **2019/1170 (08 July 2019)**.
- VDL Mode 2 is the sub-network for CPDLC and also carries airline AOC and maintenance data.
- Additional frequencies have been deployed on the ground. They "can only be used if aircraft systems can be automatically tuned". The airborne **autotune/multi-frequency** capability "constitutes a key minimum feature". Aircraft that cannot be retuned degrade the performance and capacity of the network.
- The legal chain: Art. 6 of 29/2009 → Annex IV Part B → Annex III point 5 → ICAO Annex 10 Vol III ("autotune").
- Not considered an unsafe condition (no AD). EASA "may consider to limit or to prohibit non multi-frequency CPDLC operations".
- Recommendations: (1) verify autotune capability, otherwise compliance "is not achieved", so upgrade; (2) the same for CPDLC users; (3) upgrade non-CPDLC VDL2 users too.

## Relevance to us [Y]
The datalink "channel" is managed automatically by the avionics (autotune), unlike voice frequencies that the pilot dials. If the team's device touches radios, it must not interfere with the VDL2 radio (usually VHF3 set to DATA, see C_EUROCONTROL_CPDLC_RecPractices_2026) or tune voice onto data channels (see C_EUROCONTROL_Leaflet_Datalink_VHF).
