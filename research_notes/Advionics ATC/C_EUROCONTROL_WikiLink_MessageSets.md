# C_EUROCONTROL_WikiLink_MessageSets: "Message sets supported by each ANSP" (EUROCONTROL WikiLink)

- **Issuing body:** EUROCONTROL (WikiLink, datalink support wiki)
- **URL:** https://ext.eurocontrol.int/WikiLink/index.php/Message_sets_supported_by_each_ANSP
- **Date read:** 2026-11-04 (no page date shown)

## Content [D-ag]
- ANSPs listed: MUAC, DFS, DSNA, AENA, Skyguide, IAA-Shannon, NAVP, NATS, ENAV, Austrocontrol, HungaroControl.
- Marked **mandatory (M)**: UM0, UM1, UM19, **UM20**, UM23, UM74 PROCEED DIRECT TO, UM117 CONTACT, **UM157 CHECK STUCK MICROPHONE**, UM159, UM160, UM162, UM183, **UM190 FLY HEADING**, UM227. UM120 MONITOR is optional (only IAA-Shannon).
- Note 1: DSNA is not committed to UM157 ("technical complexity and limited operational interest") and prefers free text UM183.
- Note 2: ENAV is analysing UM171-174 (vertical rate), because aircraft often have not completed the clearance when the **"120-second ground timer"** expires.
- Note 3: ED-120 Change 2: ANSPs accommodating FANS 1/A(+) must display DM55, DM56 and DM112 (emergency messages); expected by January 2015. Under GOLD v1.0 the replies are ROGER PAN / ROGER MAYDAY.

## Relevance to us [Y]
CPDLC dialogues have a **120 s** ground response timer. That is far too slow for approach-phase instructions, which are seconds-critical. This supports keeping the approach on voice and using text only as a support channel.
