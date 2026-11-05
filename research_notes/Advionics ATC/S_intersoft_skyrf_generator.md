# S_intersoft_skyrf_generator: SkyRF® Generator leaflet (IE-CD-01700-003)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2026/10/IE-CD-01700-003-SkyRF-Generator-single-page-1.pdf (linked from the Knowledge Center). The product page is https://intersoft-electronics.com/cns-test-equipment/simulators-and-signal-generators/skyrf-generator/. That page was already covered in R_advionics_research.md and I did not re-read it.
- **Date read:** 2026-11-04. I loaded the PDF into memory with PyMuPDF and read the extracted text.

## What it says [D-ag]
- **What it is:** a drone-borne target and scenario generator for IFF and PSR.
- **IFF and Mode S/5 simulation:**
  - SSR Modes 1, 2, 3/A and C, as both transponder and interrogator.
  - An add-on transponder module enables Mode S and Mode 5, for "NATO/AIMS" certification.
  - How it works: "The SkyRF® Module receives the Mode S/5 pulse and buffers it in its FPGA". The interrogation is delayed (to set range) and passed to a co-mounted transponder, which then replies.
- **PSR sensor alignment:** a dynamic 360° target with configurable Doppler, RCS and distance. It replaces the active reflectors used to align radar video to "touchdown zones and runway intersections".
- **Missile generation:** ballistic trajectories for testing counter-battery and missile-defence radars (Combat Management Systems).
- **Specifications:**
  - Radial targets: "multiple targets (#20)" at different speeds, Doppler, RCS and acceleration.
  - Modes 1/2/3/A/C/S/5L1/5L2; ADS-B; Mode 5 extended squitter (GNSS NMEA/ARINC input).
  - Certified transponders: "Ping 20SI" (civil) and "RT-2087" (military).
  - One scenario interface for combined PSR + SSR targets.
  - "40MHz instantaneous bandwidth"; "Target Range Resolution: 3.75m".
  - Simultaneous targets: "Short Range (<30km): 4"; "Long Range … 16".
  - 0 dBsm reach: "L-band 100kW 0dBsm: 4 - 500+ km"; "S-band 20kW 0dbsm: 2.5 - 500+ km".

## Relevance to us [Y]
- **Approach link:** the sponsor uses drone-borne RF targets to check radar alignment at **touchdown zones**.
- **FPGA hint:** the leaflet confirms FPGA-based real-time RF delay and replay inside the group.
- **Test idea:** a "drone as a moving test aircraft" could inject Mode S/ADS-B and PSR returns along a synthetic approach path. That would be a cheap and credible test method for any radar- or SSR-based approach monitor.
