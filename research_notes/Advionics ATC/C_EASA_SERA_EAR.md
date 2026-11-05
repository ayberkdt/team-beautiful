# C_EASA_SERA_EAR: Easy Access Rules for SERA (Regulation (EU) No 923/2012 as amended)

- **Issuing body:** European Union Aviation Safety Agency (EASA). The law itself is Commission Implementing Regulation (EU) No 923/2012 (SERA) with its amendments, including (EU) 2024/404 and (EU) 2024/1111.
- **URL (online eRules format):** https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-standardised-european
  - SERA.14083 anchor: `?erules-id=ERULES-1963177438-22770`
  - SERA.8015: `?erules-id=ERULES-1963177438-9942`
  - SERA.8035: `?erules-id=ERULES-1963177438-9952`
  - Appendix 1 (Signals): `?erules-id=ERULES-1963177438-9854`
  - SERA.13005: `?erules-id=ERULES-1963177438-9933`
  - SERA.14035/14040: `?erules-id=ERULES-1963177438-9893`
- **Revision:** the EASA landing page lists the "August 2025" revision, published 27/08/2025 (PDF https://www.easa.europa.eu/en/downloads/68174/en).
- **Date read:** 2026-11-04
- **How it was read:** through a fetch tool that turns the page into a summary. Numbers and short quotes below are what the tool returned from the page. EUR-Lex itself returned empty pages to the tool, so the Official Journal text was **not** compared word for word. Before quoting anything in the final deliverable, check it against the EASA PDF.

---

## 1. SERA.14083 Radio communication failure procedures (introduced by Regulation (EU) 2024/404) [D-ag]

**(a) Trying to re-establish contact.** If the aircraft cannot comply with SERA.8035(a), the crew first tries the previous channel, then another channel suitable for the route. If that fails, they try to reach (1) the appropriate ATS unit, (2) other ATS units, or (3) other aircraft, using all available means, "including data link, satellite voice and mobile phones". If they get through, they report that they could not make contact on the assigned channel. [D-ag]

**(b) ATC actions when an expected transmission is not received:**
- (1) With a surveillance service: the controller checks whether the aircraft's receiver works. If it does, ATC keeps providing service and gets clearances acknowledged through SSR code or ADS-B changes, or IDENT. [D-ag]
- (2) If that fails, the ATC unit (i) asks other ATS units to call the aircraft and relay, (ii) asks aircraft on the route to try to call it and relay, and (iii) notifies the operator as soon as possible. [D-ag]
- (3) If (2)(i) and (ii) fail, ATC clearances must **not** be sent by blind transmission unless the originator specifically asks for that. Other messages may be sent blind on the frequencies the aircraft is believed to monitor. [D-ag]

**(c) Aircraft procedure (when (a) fails):**
- (1) Aerodrome traffic at a controlled aerodrome: keep watch for visual signals. [D-ag]
- (2) Set Mode A Code "7600" and/or the ADS-B transmitter to show loss of air-ground communication, then apply (3) to (6). [D-ag]
- (3) **VFR:** continue in VMC, land at the nearest suitable aerodrome, and report arrival by the most expeditious means. [D-ag]
- (4) **IFR (except as in (5)):**
  - (i) Maintain the last assigned speed and level, or the minimum flight altitude if higher, for **"20 minutes"** after (A) failing to make a required report, or (B) setting 7600 and/or the ADS-B emergency or urgency mode, where a surveillance service is provided. After that, adjust level and speed to the **filed** flight plan, as amended by delay and modification messages. [D-ag]
  - (ii) If being vectored or on an RNAV offset: (A) with a specified limit, continue to that limit and then rejoin the last received and acknowledged route; (B) without a limit, rejoin no later than the next significant point. In both cases, respect the minimum flight altitude. [D-ag]
  - (iii) Proceed on the last received and acknowledged route clearance to the designated navigation aid or fix serving the destination, and hold there if needed to meet (iv). [D-ag]
  - (iv) Begin descent at, or as close as possible to, the last received and acknowledged **EAT**. If no EAT was received, begin at or near the **ETA**. [D-ag]
  - (v) Complete the instrument approach procedure for that aid or fix. [D-ag]
  - (vi) Land, if possible, within **"30 minutes"** after the ETA or the last acknowledged EAT, whichever is later. [D-ag]
- (5) **IFR on a SID or STAR:** fly the communication failure procedure published on the SID/STAR chart, where one is provided. [D-ag]
- (6) **IFR flight that encounters VMC and whose pilot-in-command decides to continue in VMC** (corrected after audit 2026-11-04; the text does not say "VFR"): set Mode A Code **"7601"**, land at the nearest suitable aerodrome, and report arrival by the most expeditious means. [D-ag]

**(d)** ATC service assumes that the aircraft follows (c). **(e)** The ATC unit passes the RCF information to all ATS units along the route. The ACC serving the destination collects information on alternates and other data from the filed flight plan. **(f)** When contact is re-established or the aircraft lands, the other units are informed. **(g)** Signals used in communication failure follow Appendix 1. [D-ag]

**Associated AMC/GM (all ED Decision 2024/007/R) [D-ag]:**
- AMC1 SERA.14083(b)(1): the controller checks the receiver by asking for an acknowledgement through a specified manoeuvre (observed on the track), IDENT, or an SSR/ADS-B code change.
- GM1 SERA.14083(b)(1): some first-generation ADS-B avionics cannot squawk IDENT while emergency or urgency mode is selected.
- AMC1 SERA.14083(b)(3): blind transmissions should include ATC actions and emergency instructions. They should go out on all available frequencies, including radio-navigation or approach-aid **voice** frequencies where practicable, and cover weather suitable for cloud-breaking and weather at suitable aerodromes.
- GM1 SERA.14083(c): when several aircraft may be affected (for example a ground station failure on HF), the safest course is to stick to the last acknowledged clearance.
- GM2 SERA.14083(c): when choosing the "nearest suitable aerodrome", consider runway characteristics, aerodrome facilities and how complex the environment is.
- GM1 SERA.14083(c)(4)(i)(B): some first-generation ADS-B avionics transmit only a general emergency alert, whatever code is selected.
- The tool did not return the text of AMC1/GM1/GM2 SERA.14083(d).

## 2. SERA.8035 Communications (as amended by Regulation (EU) 2024/404) [D-ag]
- (a) A controlled flight keeps a continuous air-ground **voice** watch on the appropriate channel and establishes two-way communication as needed. The ANSP may prescribe exceptions for aerodrome traffic at a controlled aerodrome.
- (a)(1) The voice watch "shall remain in effect when CPDLC has been established". (The wording is the same in the UK-retained text on legislation.gov.uk.)
- (b) If a communication failure prevents compliance with (a), the procedures of SERA.14083 apply.
- GM1 SERA.8035(a) (ED 2013/013/R): in an HF environment, SELCAL can satisfy the watch requirement.
- AMC1 SERA.8035 (ED 2016/023/R): direct pilot-controller communication should be established before ATS surveillance services are provided.
- AMC2 SERA.8035 (ED 2016/023/R): a CPDLC emergency message is acknowledged by the most efficient means. Otherwise CPDLC is answered by CPDLC and voice by voice.

## 3. SERA.8015(e) Read-back (tag shown: Regulation (EU) 2024/1111) [D-ag]
- (e)(1) Flight crew read back the safety-related parts of ATC clearances and instructions sent **by voice**:
  - (i) ATC route clearances;
  - (ii) clearances and instructions to enter, land on, take off from, hold short of, cross, taxi on and backtrack on any runway;
  - (iii) runway-in-use, altimeter settings, SSR codes, newly assigned communication channels, and "level instructions, heading and speed instructions";
  - (iv) transition levels, whether issued by the controller or contained in ATIS broadcasts.
- (e)(2) Other clearances, including conditional clearances and taxi instructions, are read back or acknowledged in a way that clearly shows they were understood and will be complied with.
- (e)(3) The controller listens to the read-back (hearback) and corrects any discrepancy immediately.
- (e)(4) CPDLC messages do not need a voice read-back unless the ANSP specifies otherwise. A GM adds that an ANSP may require voice acknowledgement for some CPDLC messages, especially trajectory changes.
- (e)(5)-(6) Vehicle drivers on the manoeuvring area read back the same kinds of items.

## 4. SERA.13001 / SERA.13005 Transponder (Regulation (EU) 2016/1185) [D-ag]
- 13001(a): "the pilot shall operate the transponder at all times during flight". 13001(b): "Pilots shall not operate the IDENT feature unless requested by ATS."
- 13005(a): Code **7700** = emergency; **7600** = "radio-communication failure"; **7500** = unlawful interference (use 7700 instead if circumstances warrant).
- 13005(b): when no ATS instruction is given, use **2000** (or the code the competent authority prescribes). When not receiving ATS, use **7000**.
- 13005(c): if the displayed code does not match the assigned one, the pilot is asked to confirm and reselect.
- Code 7601 does not appear in SERA.13005 (as returned). It appears only in SERA.14083(c)(6).

## 5. Number transmission and pronunciation (SERA.14035, SERA.14040) [D-ag]
- Call signs, headings, runway and wind: each digit spoken separately, e.g. "heading zero eight zero", "runway two seven", "wind two zero zero degrees seven zero knots".
- Flight levels: digits spoken separately except whole hundreds: "flight level one eight zero", "flight level two hundred".
- QNH: digits spoken separately, except 1000 hPa = "QNH one thousand". Examples: "QNH one zero zero nine", "QNH nine nine three".
- SSR codes: digits spoken separately, except whole thousands: "squawk two four zero zero", "squawk one thousand".
- Altitudes, cloud height, visibility, RVR: use HUNDRED/THOUSAND, e.g. "three thousand four hundred", "one two thousand" (12 000).
- Indicated airspeed: "two five zero knots", "three hundred knots".
- Decimals: the word DECIMAL, e.g. "ONE ZERO ZERO DECIMAL THREE".
- **VHF frequencies:** all six digits are spoken unless the 5th and 6th are both zero:
  - 118.000: "ONE ONE EIGHT DECIMAL ZERO"
  - **118.005: "ONE ONE EIGHT DECIMAL ZERO ZERO FIVE"**
  - 118.010: "ONE ONE EIGHT DECIMAL ZERO ONE ZERO"
  - 118.025: "...ZERO TWO FIVE"
  - 118.050: "...ZERO FIVE ZERO"
  - 118.100: "ONE ONE EIGHT DECIMAL ONE"
  - Caution note: in 25 kHz airspace, radios with only 25 kHz capability can select just the first five digits.
- Pronunciation table (SERA.14040): 0 ZE-RO, 1 WUN, 2 TOO, 3 **TREE**, 4 FOW-er, 5 **FIFE**, 6 SIX, 7 SEV-en, 8 AIT, 9 **NIN-er**, 10 TEN, 11 EE-LE-VEN, 12 TWELF, Decimal DAY-SEE-MAL, Hundred HUN-dred, Thousand TOU-SAND.

## 6. SERA.14045 / 14050 / 14055 / 14060 / 14065 / 14070 [D-ag]
- 14045 standard words: AFFIRM, NEGATIVE, APPROVED, CLEARED, STANDBY (not an approval or denial), UNABLE, WILCO, CORRECTION, SAY AGAIN, WORDS TWICE. ROGER must not be used to answer a read-back request or an AFFIRM/NEGATIVE question. OVER and OUT are not normally used on VHF. TAKE-OFF is used only for take-off clearance or its cancellation.
- 14050 call signs: Type (a) registration; Type (b) telephony designator plus last 4 characters of the registration; Type (c) telephony designator plus flight identification. **Type (c) may not be abbreviated.** Example: "SCANDINAVIAN 937" has no abbreviation. Mode S/ADS-B aircraft should use the call sign that matches the flight plan identification.
- 14055: no transmissions to an aircraft during take-off, the last part of final approach or the landing roll, except for safety. Abbreviated call signs only after ATC has used them. ATC clearances and read-backs always include the call sign.
- 14060: on frequency change, the aircraft is told by ATS. Otherwise it notifies ATS before changing.
- 14065: the first call after a changeover gives unit, call sign ("Heavy"/"Super" if applicable), level (including passing and cleared levels) and assigned speed. Level is given to the nearest full 30 m / 100 ft.
- 14070 radio check readability scale: 1 Unreadable, 2 Readable now and then, 3 Readable but with difficulty, 4 Readable, 5 Perfectly readable.

## 7. SERA.14080 Communications watch / 121.5 MHz [D-ag]
- Aircraft on long over-water flights, or in areas where an ELT is required, continuously guard **121.5 MHz**, except when using other VHF channels or when equipment or cockpit duties prevent it. They also guard it where interception or other hazards are possible and the competent authority requires it.
- Aeronautical stations keep a continuous watch on 121.5 MHz during their hours of service.
- AMC1: other flights should guard 121.5 MHz as far as possible.
- The text of SERA.14085 (blind transmission) and SERA.14095 (distress procedure detail) was not returned by the tool, so it is not recorded here. The UK-retained version of SERA.14085 (legislation.gov.uk) says: transmit twice, prefaced "TRANSMITTING BLIND". [D-ag, UK-retained text, not the current EU text]

## 8. Appendix 1 Signals (tag: Regulation (EU) 2024/1111) [D-ag]
Light signals from aerodrome control (Table AP 1-1):

| Signal | Aircraft in flight | Aircraft on the ground |
|---|---|---|
| Steady green | "Cleared to land" | "Cleared for take-off" |
| Steady red | "Give way to other aircraft and continue circling" | "Stop" |
| Series of green flashes | "Return for landing" | "Cleared to taxi" |
| Series of red flashes | "Aerodrome unsafe, do not land" | "Taxi clear of landing area in use" |
| Series of white flashes | "Land at this aerodrome and proceed to apron" | "Return to starting point on the aerodrome" |
| Red pyrotechnic | "Notwithstanding any previous instructions, do not land for the time being" | (not returned) |

- Acknowledgement by aircraft (3.1.2): in flight by day, rock the wings (except on base and final). At night, flash the landing lights on and off twice (or the navigation lights). On the ground by day, move the ailerons or rudder. At night, flash the lights twice.
- Distress (1.2.1): SOS; "MAYDAY"; a data-link message conveying MAYDAY; red rockets or flares; Mode A Code 7700. Urgency (1.3.2): XXX; "PAN, PAN"; a data-link urgency message.

## Relevance to us [Y]
This is the binding EU rule set that any "automated approach guidance" or "translate the signal" cockpit function has to respect. The key points: (1) after a radio failure the crew **must** fly a fixed, predictable profile (20 min hold of level and speed, then the filed plan, EAT/ETA descent, land within 30 min), because ATC separates **on the assumption** that it does. A system must not invent a different trajectory. (2) The rule itself lists data link, satellite voice **and mobile phones** as legitimate ways to re-establish contact. (3) Squawk 7600 versus 7601 tells ATC the pilot's intent. A display could suggest the right code, but the pilot sets it. (4) Read-back items in SERA.8015(e)(1) give the exact list of fields a speech-to-text display must capture and check: route, runway, QNH, squawk, frequency, level, heading, speed, transition level. (5) Number formats in SERA.14035 (e.g. 118.005 spoken "decimal zero zero five", FL "two hundred") are the grammar a speech parser must handle. (6) The light-gun table is the last-resort "signal" the system could help decode. (7) The voice watch stays mandatory even with CPDLC, so a text display can supplement voice but cannot replace it.
