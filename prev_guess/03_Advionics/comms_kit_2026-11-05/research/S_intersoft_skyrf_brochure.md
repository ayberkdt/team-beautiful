# S_intersoft_skyrf_brochure: "Drone-based CNS measurements / Introduction to SkyRF®" (IE-CD-01677-004)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2026/10/IE-CD-01677-004-Drone-based-CNS-measurements-single-page-1.pdf (linked from the Knowledge Center)
- **Date read:** 2026-11-04. The file is 14 MB. I loaded it into memory with PyMuPDF and read the extracted text.
- **Author named:** Domien De Ruyck, Managing Director, Intersoft Services.

## What it says [D-ag]

### General
- SkyRF® was developed by **Intersoft Electronics and Skyguide**.
- It measures CNS parameters "in a single 10-minute flight" and can combine systems, e.g. ILS and DME.
- With good correlation to ground measurements, "test flights can be reduced to one campaign per year, according to ICAO 8071". The brochure says this cuts "CO2 emissions and noise pollution by 50%".
- **Drones used:**
  - RTK drones DJI M350, IF800 and IF1200A, with centimetre-level positioning.
  - Variants on the "blue list", compliant with the US NDAA.
- **Operations:**
  - Automatic flights, with a pilot present for safety.
  - Live link, direct or over cellular VPN.
  - Time-synchronised recording.
  - Example cadence: Skyguide flies monthly ILS measurements.
- **Maturity:** "Operationally proven solution for more than 7 years".

### ILS/DME
- SkyRF flies 3 trajectories:
  - **Mini-Orbit**: LLZ/DME.
  - **Vertical**: GP/DME profile.
  - **Mini-Approach**: LLZ, GP and DME measured together.
- Measured: course, clearance, frequency and power from the 90/150 Hz AM signals, plus DDM.
- The live "ILS Preflight Checker" shows:
  - GP angle and sector widths;
  - LLZ displacement error;
  - course/clearance ratio;
  - **threshold crossing height** in normal and alarm conditions.
- Claim: "ILS/DME measurement in a single 15 minutes drone flight". The general section says a 10-minute flight; both figures appear in the same brochure.

### VOR/DME/TACAN
- Trajectories: radial and orbits.
- Measured: azimuth error, FM deviation, RF level, and 30 Hz / 9960 Hz modulation depths. The cone of silence is analysed.

### Radar antenna patterns
- Covers PSR, SSR/IFF and combined systems, "in a single 15-minute flight".
- Measures HPD and VPD at positive elevation, in the far field.
- Data converts into RASS format for OTD analysis.
- Also measures the receive VPD and beam combining, using geo-referenced CW signals.
- Can measure the radiation patterns of G-A-G radio systems (VHF/UHF/L/S/C band).

### PAPI
- Measures:
  - PAPI system angle;
  - transition angles per unit;
  - angular coverage, horizontality, symmetry and relative brightness.
- Uses a camera with image processing (binary images, erosion and dilation) on a DJI Zenmuse H30.
- Flight takes "less than fifteen minutes".
- Compliant with ICAO 8071, STANAG 3374 and FAA 8200.1.

### Other uses
- Satellite ground-antenna tests.
- **Naval CNS:**
  - co-site analysis around the vessel;
  - tracking test, where the drone transmits its GPS position and the ship's antenna tracks the drone.

### SkyRF CNS receiver specs
- Frequency "70MHz - 6GHz".
- Min input "-80dBm | with LNA: -100dBm".
- ADC 2×12 bit; dynamic range "72dB".
- DME accuracy "< 12m".
- ILS max output rate "300Hz".
- LOC DDM uncertainty "≤ 0.02 % DDM"; GP "≤ 0.04 % DDM".
- VOR azimuth uncertainty "≤ ±0.04deg".
- TACAN bearing std "< 0.1°".

### PSR/SSR measurement specs
- 100 MHz – 6 GHz; "40 MHz" instantaneous bandwidth.
- SSR uplink 1030 MHz and downlink 1090 MHz.
- Decodes Mode S interrogations; **"Mode 5 Pattern Recognition"**.
- HPD/VPD for the SUM, DELTA and SLS channels.
- RTK GNSS positioning; output in RASS-S native formats.

## Relevance to us [Y]
- **Approach link.** The sponsor already flies an **automated "Mini-Approach" drone trajectory** and measures **glide-path angle, DDM and threshold crossing height**. This is the most concrete approach-guidance link in the whole group.
- **Validation plan.** Any guidance concept should be validated with SkyRF. A concept where the drone verifies the guidance volume shows we know their product.
- **Sustainability numbers** (say "up to 50%"):
  - 50% fewer flight checks;
  - 50% less CO2;
  - no runway downtime.
