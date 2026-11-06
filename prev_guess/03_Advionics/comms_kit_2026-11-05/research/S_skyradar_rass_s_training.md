# S_skyradar_rass_s_training: SkyRadar "Didactical Radar Training System RASS-S" (third party)

- **URL:** https://www.skyradar.com/hubfs/Catalogs-Manuals-New-Generation/RASS-S-Didactical-Training-System-System-Description.pdf
- **Date read:** 2026-11-04. WebFetch saved the PDF, and I read its text with pdftotext.
- **Publisher:** SkyRadar, a vendor of training systems. **This is not an Intersoft document.** It is version 2.0, dated 11-11-2018, so parts may be outdated.

## What it says [D-ag]
- **What RASS-S is:** "Radar Analysis Support System for Sites".
- **Training kit:** SkyRadar builds it around "standard RASS-S equipment" for ICAO/EASA ATSEP training. The kit also includes the **RASS-R** display software, licensed for "didactical use".

### SSR features
- Uplink and downlink antenna diagrams: HPD, beamwidth, pulse shapes, sidelobes, SLS, monopulse.
- Receiver measurements: sensitivity, bandwidth, (D)STC, and monopulse phase-amplitude alignment.
- Transmitter measurements: power, pulse shape, stagger.
- Video recordings: code, pulse shape, range, azimuth.
- **ASTERIX recordings and analysis: plot and track.**
- ADS-B.

### PSR features
- Antenna gain and beam pointing.
- Reflection measurements.
- Signal processing topics: I/Q, MTI, clutter, Doppler filters, pulse compression, target detection.

### Hardware details
- **RFA (Radar Field Analyser):** field use on "(M)SSR ATC and primary radars in L and S band".
  - Rx and Tx measurements.
  - FRUIT generation.
  - Mode S interrogation generation.
  - Target injection.
  - A "PARROT" function.
- **RIM:** records "up to 2 analog video signals (selected from 4 physically connected signals)". The 2025 catalogue lists 6 inputs, so the hardware revision has changed since this document.
- **Full hardware list:**
  - RFA and RIM.
  - DTI.
  - Didactical Primary Radar.
  - Data Recorder UDR.
  - Target Generator.
  - RASS-S and RASS-R workstations.
  - ASTERIX server.

## Relevance to us [Y]
- This is an independent source that confirms the product names. RASS-S is the site and hardware measurement part, and RASS-R the real-time radar-data analysis part.
- Intersoft's current website no longer uses the -S and -R suffixes as headings. It groups everything under "RASS®" (see S_intersoft_rass_catalogue.md).
- **In the pitch, say "RASS" rather than "RASS-R"** unless someone asks.
