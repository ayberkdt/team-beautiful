# C_AIP_Georgia_ENR18: AIP Georgia ENR 1.8 "Regional supplementary procedures" §3, Action in the event of Air-Ground Communication Failure

- **Issuing body:** Sakaeronavigatsia Ltd (Georgian Air Navigation), AIP Georgia, AIRAC AMDT 01/2023. Page date 18 MAY 2023.
- **URL:** https://airnav.ge/eaip/2024-03-07-AIRAC/pdf/UG-ENR-1.8.pdf
- **Date read:** 2026-11-04 (PDF text extracted with pdftotext)
- **Why this source:** ENR 1.8 carries the ICAO EUR **regional supplementary procedures** (Doc 7030). Georgia is outside the EU, so this is the pre-SERA-2025, ICAO-style "7 minutes" text, reproduced word for word by a state AIS. I could not open ICAO Annex 2 or Doc 4444 directly (paywalled).

## Content (pages ENR 1.8-1 and 1.8-2) [D-ag]
- **3.1** Once two-way communication is known to have failed, ATC keeps separation "based on the assumption that the aircraft will operate in accordance with 3.2 or 3.3".
- **3.2 VMC:** a. set transponder to Code 7600; b. continue to fly in VMC; c. land at the nearest suitable aerodrome; d. report the arrival time by the most expeditious means.
- **3.3 IMC** (or when continuing under 3.2 is not feasible):
  - a. set Code 7600;
  - b. "maintain for a period of 7 minutes the last assigned speed and level or the minimum flight altitude" if higher. The 7 minutes start:
    - (1) on a route without compulsory reporting points: when the assigned level or minimum flight altitude is reached, or when the transponder is set to 7600, **whichever is later**;
    - (2) on a route with compulsory reporting points: at the latest of reaching the level, the previously reported pilot estimate for the reporting point, or a failed position report.
  - Note: "The period of 7 minutes is to allow the necessary air traffic control and coordination measures."
  - c. then adjust level and speed to the **filed** flight plan;
  - d. if vectored or on an RNAV offset without a limit, rejoin the current flight plan route no later than the next significant point;
  - e. proceed to the designated navaid and hold if needed;
  - f. begin descent at or close to the last acknowledged EAT, otherwise at or close to the ETA;
  - g. fly a normal instrument approach;
  - h. land, if possible, "within thirty minutes after the estimated time of arrival" or the last acknowledged EAT, whichever is later.
  - Note: "Pilots are reminded that the aircraft may not be in an area of secondary surveillance radar coverage."
- RVSM (ENR 1.8 §1.1 b.3): **2000 FT (600 M)** vertical separation applies between an aircraft with a communications failure and any other aircraft in EUR RVSM airspace (FL 290 to FL 410).

## Relevance to us [Y]
This is the "classic" 7-minute EUR/ICAO procedure, shown for contrast with the EU 20-minute rule (C_EASA_SERA_EAR). It also shows that a comms-failure aircraft triggers **doubled vertical separation** (2000 ft) in RVSM airspace, which a guidance display should know about. The exact start-of-timer logic ("whichever is later") is deterministic and can be implemented as a timer state machine.
