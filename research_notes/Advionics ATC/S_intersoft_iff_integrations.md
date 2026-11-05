# S_intersoft_iff_integrations: IFF Integrations page (naval)

- **URL:** https://intersoft-electronics.com/radar-technology/iff-integrations/
- **Date read:** 2026-11-04 (WebFetch)

## What the page says [D-ag]

### Context
- Naval IFF has requirements different from land-based ATC. The technology "supports NATO standards".

### Products

**L-IESA® NR-IFF**
- A non-rotating, electronically steered IFF array for frigates and capital ships.
- Wraps around the mast.
- Uses beam steering and electronic levelling.
- "Compatible with any MSSR or STANAG/AIMS certified IFF interrogator".
- Modes 1, 2, 3/A, C, S, ADS-B, plus Mode 5 Level 1 and 2.
- Integrates with any onboard Combat Management System (CMS).

**L-IESA® Mini**
- A compact directional transponder antenna. It "prevents self-interference and eliminates coverage gaps" and helps meet NATO Mode 5.
- "Deployed on vessels of the German and Portuguese Navy".

**Secure IFF Cabinet**
- Originally designed for the German Navy.
- Houses the interrogator and handles the transition between unclassified and classified domains.
- Specs:
  - ">80 dB shielding"
  - stainless-steel Faraday cage
  - RF-to-optical conversion
  - "cabinet-in-a-cabinet"
  - "Compliant with NATO TEMPEST standard SDIP 27 Level A"

**Transponder Remote Control Unit (TRCU)**
- Controls IFF transponders over LAN using **ASTERIX Cat253** over TCP/IP, with a command whitelist.
- Sets all mode codes. Mode S squitter and Mode 5 Level 2 squitter can be enabled individually.
- Synchronises time with the ship's secure PNT source and feeds it to the transponder over **ARINC-429**.
- Reads position over NMEA and passes it to the transponder over ARINC-429.
- Has an OS-independent GUI.

### Not stated on the page
- Interrogator models, range, beam counts, and the 1030/1090 MHz frequencies.

### Customers named
- German Navy and Portuguese Navy.

## Relevance to us [Y]
- The jury knows the whole **cooperative-surveillance chain on ships** (interrogator → antenna → transponder → CMS), including **ASTERIX Cat253 control** and **ARINC-429 / NMEA PNT feeds**.
- A ship-deck UAS approach concept can reuse:
  - the ship's L-IESA as the interrogator and ranging sensor;
  - TRCU-style ASTERIX control;
  - the ship's secure PNT source.
- Naming these reuse paths would score well.
