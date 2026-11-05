# C_LINK2000_TestTool_IH0617: "Automated CM/CPDLC Ground Tool, User Guidance Specifications", LINK 2000+ Test Facility Project

- **Issuing body:** EUROCONTROL (LINK 2000+ programme, EEC). Ref. LINK2000/EEC/DOC/IH0617, Issue 1.3, **29/04/11**. Author Isabelle Herail.
- **URL:** https://www.eurocontrol.int/archive_download/all/node/12344
- **Date read:** 2026-11-04 (PDF text extracted with pdftotext)
- **Caveat:** this is a **test-tool** manual, not an operational standard. Its timer values are said to follow Ref 1 = ED-110 (ATN Baseline 1 interoperability). The timer table extracted with broken layout, so the pairing of names and values below is my best reading.

## Content [D-ag, with layout caveat]
- §4.4.2 timers: "tts" (time to wait for the operational response) **120 seconds**; "tr" (technical response, wait for Logical Acknowledgement) **40 seconds**. Other values in the table: 2 seconds and 40 seconds (labels mis-aligned in extraction). The text notes that "All the timers are configurable values."
- §4.4.1: test session timer **20 minutes**.
- §3.5: after an abnormal termination, the session ends on a **Provider Abort due to TP4 timer expiry, which is 6 minutes**.
- Message list includes UM157 CHECK STUCK MICROPHONE.

## Relevance to us [Y]
This is consistent with the 120 s operational response timeout in C_EUROCONTROL_WikiLink_MessageSets and the 2026 leaflet. Timeouts of tens of seconds to minutes confirm that CPDLC works on a timescale of minutes, not seconds.
