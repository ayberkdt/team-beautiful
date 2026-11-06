# C_SKYbrary_USiT: "Blocked Transmissions / Undetected Simultaneous Transmissions (USiT)"

- **Issuing body:** SKYbrary Aviation Safety (run by EUROCONTROL with partners)
- **URL:** https://skybrary.aero/articles/blocked-transmissions-undetected-simultaneous-transmissions-usit
- **Date read:** 2026-11-04 (article date not shown in the fetched text)
- **Section numbers:** none. Headings: Definition / Scenarios / Effects / Contributory factors / Defences.

## Content [D-ag]
- Definition (quoting EUROCAE, VoIP ATM requirements, 2009-02): transmissions that "overlap in such a way that the controller is not aware" that more than one occurred.
- Overlap types: **garbled** (equal strength, usually detected); **partial** (the weaker signal is "clipped"); **full** (the stronger masks the weaker, so "no (or little) detection can be expected").
- Scenarios: (1) two pilots: stepped-on transmission, "call swamping" with **Best Signal Selection** multi-receiver ground systems, and call-blocking on cross-coupled frequencies; (2) controller and pilot transmitting together; (3) multi-receiver blind spot in difficult terrain.
- Contributory factors include similar call signs, expectation bias, high load, frequency coupling during sector collapse, and differences in signal strength. "Modern transmitters produce no audible feedback" during overlaps. **AM receivers eliminate the weaker signal.**
- Examples listed: San Diego 10 June 2021 (blocked go-around instruction); Venice 18 October 2022 (go-around issued at about 100 ft AGL; the crew tried 121.5); Toronto 7 March 2020 (an unheard rejected-take-off call); LaGuardia 22 March 2026 (CRJ900 struck a firefighting vehicle after an unrecognised cancellation of its crossing clearance; 2 pilots killed).
- No numerical incidence statistics; the page says only that incidence rises "with the steady growth of air traffic".
- Defences: ground systems that detect overlaps and alert, e.g. by "re-inserting the 'noise' on the frequency"; airborne anti-blocking devices; limiting frequency coupling; good R/T practice; questioning a clearance you are unsure was meant for you.
- Search-result snippets (not the fetched page) also describe a "stuck microphone" as one that stays live after the switch is released, and point to CPDLC **UM157 "CHECK STUCK MICROPHONE"**. **[A]** for the snippet wording. UM157 itself is confirmed in C_EASA_CS_ACNS_DLS.

## Relevance to us [Y]
This is the core failure mode of shared-channel analogue voice. A single blocked or stepped-on call (e.g. a go-around) can be lost **without anyone noticing**. A cockpit system can detect locally that its own receiver got a garbled or heterodyned signal, or that its own PTT has been keyed too long (stuck mic), and warn the crew. It must not assume that silence means "no instruction".
