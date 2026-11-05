# S_intersoft_ngsp_intro: "Introduction to NGSP®" (IE-CD-01524-001)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2024/06/IE-CD-01524-001-Introduction-to-NGSP.pdf
- **Date read:** 2026-11-04. WebFetch saved the PDF; I read it with `pdftotext -layout`.

## What it says [D-ag]
- **What NGSP® is:** an exciter, a receiver and signal/data processing electronics. It has been used to upgrade combined primary and secondary radars, "ranging from ASR/Terminal Approach, Gap Filler, and **Precision Approach** to En-Route and Long-Range 3D military systems".
- **How it scales:**
  - It works with dual-beam and multi-stacked-beam radars.
  - It is combined with SSR.
  - It can be fully or partially redundant.
- **Performance features:**
  - Concurrent multi-beam digitising, which improves Pd and allows separating targets by elevation.
  - **High resolution:** "typ. dual frequency 4MHz LFM" and a **"16 Doppler Filters"** MTD.
  - Processing chain listed: "10Mhz A/D Converter & I/Q", pulse correlator, VCC, median filter, 16-channel MTD, primitive report extractor, plot extractor.
- **VCC (Vertical Clutter Canceller, patented):** driven by wind-farm clutter. "Since 2013" it has been operational on ASR and en-route systems worldwide, civil and military.
- **Interference suppression:**
  - Covers 4G/5G, radio towers, neighbouring radars, and ECCM against pulse jammers.
  - Uses a slow-time median filter, optionally combined with frequency agility.
  - Gives the operator a jammer strobe.
- **RDPS (Radar Data Processing Server):**
  - Functions: beam combiner, optional weather processing, 3D height calculator, sensor combiner, scan-to-scan correlator, **SSR Reflection Processor**, **False Plot Analyzer**, optional tracker, radar data formatter.
  - **3D height:** even on a dual COSEC² ASR antenna, height comes from phase and amplitude differences between the beams.
  - **RCS-based classification:** removes birds and "angels" using height plus RCS.
  - **SCC (Slow Clutter Cancellation):** removes anomalous-propagation clutter.
  - **Positional accuracy:** "super-resolution due to beam fitting in fast time (range) and slow time (azimuth)".
  - **Weather output:** "6-Level Weather Data Output" calibrated to NWS standards.
  - **Multilateration:** "Multi-lateration is possible as a combination of multiple radars needs slant range correction (3D measurement)".
- **ASTERIX outputs:**
  - **CAT 008** weather
  - **CAT 034** status and jamming
  - **CAT 048** plots/tracks
  - **CAT 240** video
  - **CAT 253** command and control

## Relevance to us [Y]
- NGSP has been fitted to **Precision Approach radars**. This is the most direct link between the sponsor's own technology and approach guidance.
- **True 3D Height on a primary radar** gives an aircraft's height without a transponder. That makes it a natural backup for lost-transponder or lost-comm approach monitoring.
- Quote the exact ASTERIX categories (048 / 034 / 008 / 240 / 253) when describing our interfaces.
