# C_00_summary: ATC voice/data communication and lost-communication rules, key numbers and constraints

- **Scope:** Team Beetiful, EUROAVIA Ideathon 2026, Advionics challenge "Automated Approach Guidance" (handwritten notes: "if communication with the tower is lost", "translate signal", "how does the voice signal reach the display").
- **Date compiled:** 2026-11-04. All sources were read on this date. Tags: [D-ag] = read in the source; [A] = search snippet only (see C_A_unverified_snippets).
- **Biggest correction to common assumptions:** since **1 May 2025** the EU no longer uses the ICAO "7 minutes". SERA.14083 uses **20 minutes** in both radar and non-radar airspace, and adds squawk **7601**. Also, Regulations 29/2009 (data link) and 1079/2012 (8.33 kHz) are **repealed**. Their content now lives in (EU) 2023/1770 (AUR.COM).

## Key numbers: the EU lost-comms timer is 20 min, approach CPDLC timeouts are minutes, and voice remains the primary channel

Rows are ordered by topic: lost comms, then radio, then phraseology, then data link, then human-performance data.

| # | Quantity | Value | Unit | Source file | Tag |
|---:|---|---|---|---|---|
| 1 | EU RCF: hold last assigned speed and level (IFR) | 20 | min | C_EASA_SERA_EAR (SERA.14083(c)(4)(i)) | D-ag |
| 2 | EU RCF: land within, after ETA/EAT (whichever later) | 30 | min | C_EASA_SERA_EAR (SERA.14083(c)(4)(vi)) | D-ag |
| 3 | EU RCF applicable from | 1 May 2025 | date | C_BCAA_ASIL_2025_02; C_EASA_Community_SERA_changes | D-ag |
| 4 | ICAO/EUR pre-2025 RCF hold in IMC (radar) | 7 | min | C_AIP_Georgia_ENR18 (§3.3 b) | D-ag |
| 5 | ICAO Annex 2 non-radar hold (quoted) | 20 | min | C_IFATCA_WP96_2025 (§2.7) | D-ag |
| 6 | Squawk, radio-communication failure | 7600 | code | C_EASA_SERA_EAR (SERA.13005(a), 14083(c)(2)) | D-ag |
| 7 | Squawk, IFR flight that meets VMC and whose pilot-in-command decides to continue in VMC; land at nearest suitable aerodrome (EU only; wording corrected after audit 2026-11-04) | 7601 | code | C_EASA_SERA_EAR (SERA.14083(c)(6)) | D-ag |
| 8 | Squawk emergency / unlawful interference | 7700 / 7500 | code | C_EASA_SERA_EAR (SERA.13005(a)) | D-ag |
| 9 | Squawk default / not receiving ATS | 2000 / 7000 | code | C_EASA_SERA_EAR (SERA.13005(b)) | D-ag |
| 10 | RVSM vertical separation vs comms-failure aircraft | 2000 (600) | ft (m) | C_AIP_Georgia_ENR18 (§1.1 b.3) | D-ag |
| 11 | VHF voice band (EU scope) | 117.975-137 | MHz | C_EU_1079_2012 (Art. 2(1)); C_EU_2023_1770 (AUR.COM.3001) | D-ag |
| 12 | VHF channel range (25 kHz) | 118.000-136.975 | MHz | C_ETSI_EN300676_1 (cl. 4); C_ETSI_EN301841_1 (cl. 5.6) | D-ag |
| 13 | Number of 25 kHz channels | 760 | channels | C_ETSI_EN301841_1 (cl. 5.6) | D-ag |
| 14 | Voice emission class 25 kHz / 8.33 kHz | 6K80A3EJN / 5K00A3EJN | class | C_ETSI_EN300676_1 (cl. 4.2) | D-ag |
| 15 | Frequency tolerance 8.33 kHz equipment | ±1 | ppm | C_ETSI_EN300676_1 (cl. 7.2.3) | D-ag |
| 16 | Offset-carrier systems on 25 kHz | 2, 3, 4, 5 | carriers | C_ETSI_EN300676_1 (Table 1) | D-ag |
| 17 | AM modulation depth (min / max usable) | 85 / 95 | % | C_ETSI_EN300676_1 (cl. 7.4.1) | D-ag |
| 18 | Audio passband 8.33 kHz | 350 Hz-2.5 kHz | Hz | C_ETSI_EN300676_1 (cl. 7.4.4.3) | D-ag |
| 19 | Audio passband 25 kHz | 300 Hz-3.4 kHz | Hz | C_ETSI_EN300676_1 (cl. 7.4.4.4) | D-ag |
| 20 | Ground receiver sensitivity (12 dB SINAD) | -101 | dBm | C_ETSI_EN300676_1 (cl. 8.1.3) | D-ag |
| 21 | Transmitter attack time | < 20 | ms | C_ETSI_EN300676_1 (cl. 7.9.3) | D-ag |
| 22 | 8.33 kHz capability for new radios from | 17 November 2013 | date | C_EU_2023_1770 (AUR.COM.3005(1)) | D-ag |
| 23 | All radios 8.33-capable (historic, 1079/2012) | 31 December 2017 | date | C_EU_1079_2012 (Art. 4(5)) | D-ag |
| 24 | Datalink-reserved VHF segment (no voice) | 136.500-137.000 | MHz | C_EUROCONTROL_Leaflet_Datalink_VHF | D-ag |
| 25 | Emergency / guard frequency | 121.5 | MHz | C_EASA_SERA_EAR (SERA.14080) | D-ag |
| 26 | Readability scale | 1-5 | scale | C_EASA_SERA_EAR (SERA.14070) | D-ag |
| 27 | 8.33 channel name example spoken | 118.005 = "ONE ONE EIGHT DECIMAL ZERO ZERO FIVE" | text | C_EASA_SERA_EAR (SERA.14035) | D-ag |
| 28 | EU data link mandate applies above | FL 285 | level | C_EU_2023_1770 (AUR.COM.2001) | D-ag |
| 29 | VDL Mode 2 bit rate | 31 500 | bit/s | C_ETSI_EN301841_1 (cl. 6.1.6) | D-ag |
| 30 | VDL Mode 2 symbol rate | 10 500 | symbols/s | C_ETSI_EN301841_1 (cl. 6.1.6) | D-ag |
| 31 | VDL Mode 2 receiver sensitivity (BER 10^-3) | -98 | dBm | C_ETSI_EN301841_1 (cl. 6.2.1) | D-ag |
| 32 | ACARS (POA) bit rate | 2.4 | kbit/s | C_A_unverified_snippets (#1) | A |
| 33 | VDL2 frequencies available / in use (2024) | 12 / 6 | count | C_EUROCONTROL_DL_Perf_2024_page | D-ag |
| 34 | CPDLC ground response timer | 120 | s | C_EUROCONTROL_WikiLink_MessageSets; C_EUROCONTROL_CPDLC_RecPractices_2026 | D-ag |
| 35 | Airbus: re-confirm by voice if CPDLC message older than | 2 | min | C_EUROCONTROL_CPDLC_RecPractices_2026 | D-ag |
| 36 | Data link mandate (operators), after PA deferral | 5 February 2020 | date | C_EU_2015_310 (Art. 1(2)) | D-ag |
| 37 | CPDLC UM: climb / heading / stuck mic | UM20 / UM190 / UM157 | message ID | C_EASA_CS_ACNS_DLS; C_EUROCONTROL_WikiLink_MessageSets | D-ag |
| 38 | Tower readback error rate (8,444 messages) | < 1 | % | C_Cardosi_1994_FAA_RD94_15 | D-ag |
| 39 | Readback errors not caught by controller | 7 of 19 (37) | count (%) | C_Cardosi_1994_FAA_RD94_15 | D-ag |
| 40 | En-route miscommunication, 5+ element clearances (Cardosi 1993 en-route study; the 1994 tower data are < 1 % for 1-5 elements, 1.4 / 1.3 % for 6 / 7) | 8 | % | C_Cardosi_1994_FAA_RD94_15 (citing Cardosi 1993) | D-ag |
| 41 | Air-ground comms share of top-7 ATM occurrence contributors (2022) | 37 | % | C_EVAIR_Bulletin25 (p. 18) | D-ag |
| 42 | Loss of comm with no ATM involvement (2018-2022) | 68 | % | C_EVAIR_Bulletin25 (p. 21) | D-ag |
| 43 | LoC explained by radio availability / frequency change | 42 / 32 | % | C_EVAIR_Bulletin25 (p. 22) | D-ag |
| 44 | LoC events associated with go-around | 48 | % | C_EVAIR_Bulletin25 (p. 22) | D-ag |
| 45 | Call sign confusion reports by airlines (2018-2022) | > 800 | reports | C_EVAIR_Bulletin25 (pp. 4, 15) | D-ag |

Notes: values are written exactly as in the sources (verbatim numbers, mixed formats kept on purpose). "/" separates paired values in one row.

## What the cockpit system is NOT allowed to do under these rules

1. **Must not replace the voice watch.** A controlled flight keeps continuous air-ground voice watch, and this "shall remain in effect when CPDLC has been established" (SERA.8035(a)(1), C_EASA_SERA_EAR; Annex 2 as quoted in C_IFATCA_WP96_2025 §2.4-2.5). A text or "translate" display is a supplement.
2. **Must not fly a different lost-comms profile from SERA.14083(c).** ATC separates other traffic "based on the assumption" that the aircraft complies (SERA.14083(d); PANS-ATM as quoted in C_IFATCA_WP96_2025 §2.8). No automatic creative diversion, no early descent before EAT/ETA, no skipping the 20-minute hold.
3. **Must not choose 7600 versus 7601 on its own authority.** 7601 depends on the **pilot-in-command's decision** to continue in VMC (C_BCAA_ASIL_2025_02). The system can suggest; the pilot decides.
4. **Must not operate IDENT unless ATS asks for it** (SERA.13001(b)). Any code automation must respect SERA.13005 (assigned code, contingency codes).
5. **Must not treat a CPDLC or decoded text clearance as fresh or time-critical.** CPDLC is not used for time-critical instructions, stale messages (> 2 min) must be re-confirmed by voice, and on error you revert to voice (C_EUROCONTROL_CPDLC_RecPractices_2026).
6. **Must not drop or replace the crew's voice read-back.** The read-back items in SERA.8015(e)(1) (route, runway, QNH, SSR code, frequency, level, heading, speed, transition level) are still read back by voice, and the controller does the hearback (e)(3). Only CPDLC messages are exempt from voice read-back, under (e)(4).
7. **Must not transmit ATC clearances blind on ATC's behalf**, nor expect them: blind transmission of clearances is not allowed unless the originator specifically requests it (SERA.14083(b)(3)).
8. **Must not use the data-link VHF segment (136.500-137.000 MHz) for voice**, and must not override VDL2 autotune (C_EUROCONTROL_Leaflet_Datalink_VHF; C_EASA_SIB_2019_13).
9. **Must not transmit during take-off, the last part of final approach or the landing roll** (no automated calls; SERA.14055 bars ATC transmissions to the aircraft then, except for safety). An auto-reply or auto-readback during these phases would break this.
10. **Must not hard-code one rule set.** The EU (20 min + 7601), Switzerland (7600 only, 7601 "not yet implemented"), the UK (unchanged) and the US (14 CFR 91.185: highest of assigned / MIA / expected, no hold timer) all differ (C_OpsGroup_SERA_2025; C_14CFR_91_185).
11. **Must not use non-standard words when generating phraseology.** ROGER must not answer a read-back request or an AFFIRM/NEGATIVE question, and a Type (c) call sign may not be abbreviated (SERA.14045, SERA.14050).
12. **What it MAY do (explicitly allowed):** help re-establish contact "by all available means, including data link, satellite voice and mobile phones" (SERA.14083(a)), relay through other aircraft (SERA.14083(b)(2)(ii)), decode ATC light signals (Appendix 1), and guard 121.5 MHz (SERA.14080).

## Gaps (not verified in this session)
- ICAO Annex 2 3.6.5.2 and PANS-ATM Doc 4444 chapter 15.3 were **not** read directly (paywalled). Only quotations in C_IFATCA_WP96_2025 and the EUR text in C_AIP_Georgia_ENR18 were read. Doc 4444 4.5.7.5 and Doc 9432 were not read.
- FAA AIM 6-4-1 and JO 7110.65 were not read (HTTP 403).
- ICAO Annex 10 Vol III/V voice-quality figures and ED-120 / RCP latency numbers were not obtained from a primary source (see C_A_unverified_snippets #4).
- The EUROCONTROL datalink performance 2024 PDF (18.72 MB, provider-abort rates) was not downloaded.
- The EUR-Lex Official Journal texts could not be fetched. EU law was read through EASA eRules, legislation.gov.uk "as adopted" and lexaris.de.

## Relevance to us [Y]
These rules frame the team's concept. The approach phase is a **voice** environment (no EU data-link mandate below FL 285, CPDLC timeouts of 120 s, CPDLC not for time-critical use). Loss of communication is mainly an airborne-side radio or frequency-change problem that ends in go-arounds (EVAIR 68 % / 42 % / 32 % / 48 %). Voice readback errors are rare (< 1 %) but often uncaught (7 of 19). The defensible product is a **supplementary** system: it monitors radio health and frequency selection, turns the received voice into structured text (CPDLC-like fields), checks the crew's readback against it, and, if contact is lost, displays the mandated SERA.14083 profile (timers, code suggestion, next fix, EAT/ETA) without taking authority away from the pilot or changing the trajectory ATC expects.
