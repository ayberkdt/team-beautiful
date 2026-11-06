# S_intersoft_rass_sms_leaflet: "RASS® & SMS Solution" leaflet (IE-CD-01074-004)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2026/10/IE-CD-01074-004-RASS-Software-solutions-leaflet.pdf (linked from the Sensor Monitoring page)
- **Date read:** 2026-11-04. WebFetch saved the PDF, and I read its text with pdftotext.

## What it says [D-ag]

**Positioning**
- RASS performance evaluation and the SMS are "used worldwide as reference analysis and evaluation tools".
- Users are civil and military ANSPs, flight-calibration companies and radar manufacturers.
- The tools run in ATC centres (ATCCs) and at the radar site.
- They are "manufacturer and surveillance systems independent".

**Radar Comparator (RC)**
- Uses opportunity traffic to compute **Pd, processing delay, false plot rate and code probabilities**.
- Accuracy is given as range, range gain, azimuth and timestamp random errors.
- Standards it works to:
  - EUROCONTROL SUR.ET1.ST03.1000-STD-01-01
  - EUROCONTROL SUR/MODES/EMS/SPE-01
  - EUROCONTROL SUR.NET.ET1.ST01.1000-STD-01-01
  - ICAO Annex 10
  - ICAO Doc 8071
  - ICAO Doc 9684

**Coverage Map Calculator (CMC)**
- Builds high-resolution coverage maps from SRTM terrain data.

**Data Handling Module (DHM)**
- Can run as RMCDE (radar message conversion and distribution equipment).
- Records and replays data over Ethernet, serial and FDDI links.
- Changes framing, e.g. "serial data input in U-HDLC and output in UDP".
- Does **real-time protocol conversion**, correction and filtering (e.g. on the Mode S address or the presence of MB data), 24/7.
- Extracts ADS-B plots from video in real time: "Real-time ADS-B video to plot extraction, output as ASTERIX Category 21". This needs Intersoft UVR892 or RIM782 hardware, optionally with an ARF800.

**Multi Radar Display (MRD)**
- A PPI display for maintenance use.
- Also shows weather and analogue video (via the RIM782).
- "Quick switching between radar data sources (6 out of N selection)".
- "Advanced map editor and ATC controller features".

**Sensor Monitoring System (SMS)**
- Analyses multiple sensors in real time to protect the quality of service of the track output "to the Controller Work Positions".
- Features: early warning, audible and visual alarms, automated charts, reporting.

**Named use cases**
- Surveillance data processing and distribution checking
- Multi-radar maintenance display
- Sensor verification
- FAT/SAT of new ATM systems
- Test-flight analysis
- Traffic-of-opportunity analysis
- **Incident investigations**

**Offices:** head office in Olen; Intersoft Electronics USA in Florida.

The leaflet literally says "EUROCONTROL and ICAO compliment". This is presumably a typo for "compliant".

## Relevance to us [Y]
- The group sells "translate signal" work as a product: real-time protocol and signal conversion into ASTERIX, ADS-B video-to-CAT021 plot extraction, and a multi-sensor maintenance display.
- If the challenge is read as "voice/signal → display", an architecture that **outputs ASTERIX** and **feeds an MRD-like display** will sound native to the jury.
- Incident investigation and replay are named use cases, so a concept with logging and replay for safety analysis fits their thinking.
