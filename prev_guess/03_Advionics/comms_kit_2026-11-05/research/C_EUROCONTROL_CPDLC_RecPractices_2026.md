# C_EUROCONTROL_CPDLC_RecPractices_2026: "Recommended Practices for CPDLC in Europe, 2026" (quick-reference leaflet)

- **Issuing body:** EUROCONTROL Operational Focus Group (ofg@eurocontrol.int). PDF metadata: created 7 April 2026.
- **URL:** https://ext.eurocontrol.int/WikiLink/images/9/97/Recommended_Practices_for_CPDLC_in_Europe_2026.pdf (linked from the WikiLink Document repository)
- **Date read:** 2026-11-04 (PDF text extracted with pdftotext)
- **Section headings:** Preparation for Log-On / When to Log-On / Why did my Log-On not work? / Why Still Voice Clearances If I Am Logged-On? / Uplink Message Handling / Good CPDLC Practices
- Secondary coverage: AIN, 28 May 2026, https://backend.ainonline.com/aviation-news/air-transport/2026-05-28/eurocontrol-issues-data-link-guidelines-operators (reports a **10 min** before-entry logon rule taken from an ICAO figure. That figure did not extract as text, so the 10 min is **[A]**.)

## Content [D-ag]
- "CPDLC Logon is mandatory in most of European airspace." "CPDLC usage helps to prevent Loss of Communication incidents".
- Use an ATN logon for Europe, "not FANS1/A".
- "Check CPDLC connection after passing 10.000 ft". Report UNABLE CPDLC unless the issue is due to known GNSS interference.
- Logon failure causes include a wrong logon identifier (e.g. EDVV instead of EDYY), a flight plan Field 18 CODE/ mismatch, and "Confirm VHF3 set to 'DATA'".
- **Why voice is still used:** "Time-critical situations (e.g. RoC/ RoD)", slow network or a lost uplink, customer service (an immediate voice clearance may prevent a level-off), and technical limits on the ATC side.
- "Any CPDLC clearance is valid until revoked or expired." ATC may confirm CPDLC clearances by voice because of network errors.
- Airbus: "If the message is over 2 minutes old, confirm with ATC via voice before acting." The **ground timeout is 120 seconds**.
- "A CPDLC clearance holds the same value as a voice clearance".
- Do not disconnect intentionally: "It is considered equal to disabling your radio!"
- "Error upon downlink? Revert to voice for clarification!"
- Reference: ICAO Doc 10037 GOLD Manual.

## Relevance to us [Y]
This is the current official European line: CPDLC is **not** for time-critical instructions, voice stays the fallback, and stale messages (> 2 min) must be re-confirmed by voice. This is the clearest argument that on **approach**, voice remains the primary channel. A cockpit "voice → text" display would sit next to voice, never replace it, and must time-stamp every message so the crew can tell how old it is.
