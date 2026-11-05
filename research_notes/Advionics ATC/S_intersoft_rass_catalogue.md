# S_intersoft_rass_catalogue: RASS® Product Catalogue (IE-CD-00107-012)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2025/07/IE-CD-00107-012-RASS-spread-HR-2.pdf (linked from https://intersoft-electronics.com/knowledge-center/)
- **Date read:** 2026-11-04
- **How I read it:** the PDF is 33 MB and WebFetch refused it. I loaded it into memory with Python/PyMuPDF and read the extracted text (about 3,190 lines). No file was saved.
- **Publisher:** Intersoft Electronics NV (Olen, BE), Advionics' sister company in the IE Group.

## What the document says

### Portfolio structure [D-ag]
RASS stands for "Radar Analysis Support System". The portfolio has 4 categories:
1. **Test equipment** for radar system analysis.
2. **Software tools for monitoring**, using "opportunity traffic".
3. **Simulators** for system performance testing: RES® and RTG.
4. **Radar analysis services**: FAT, SAT, flight trial, periodic maintenance and troubleshooting.

Further points:
- All tools are "manufacturer independent".
- Named users: civil and military ATC organisations, radar and radome manufacturers, ANSPs, and ADS-B ground-station manufacturers.
- Non-radar CNS scope: "ILS, DME, VOR, TACAN, PAPI, G-A-G and SatCom".
- SkyRF "reduces the need for flight checks by up to 50%".

### "Top-down" analysis of the radar chain [D-ag]
Quantities checked for each element:

| Chain element | Quantities listed |
|---|---|
| Transponder | classification, monitoring, properties |
| Antenna system | gain, tilt/levelling, alignment, polarisation, **reflections**, RF properties |
| Transmission | RF cabling, waveguides, rotary joint, coupler losses, phase matching, VSWR, directionality |
| Rx/Tx | Tx power, pulse shape, PRF/stagger, Rx sensitivity, Rx bandwidth, STC, accuracy |
| Processor | **accuracy, degarbling, load, delay, resolution, code validation, probability of detection** |
| Environment simulation | PSR/SSR targets, other interrogations, **FRUIT**, ACAS, ADS-B, reflectors, weather, jammers, clutter |
| Encoder | mechanical, turning gear, ACP/ARP errors, stability, windload |

### Test equipment [D-ag]

**RFA641 Radar Field Analyser.** On-site checks of (M)SSR and PSR "in L and S band", with the radar left in operation.
- Measures:
  - uplink HPD, and downlink HPD with the RIM782;
  - Rx sensitivity, bandwidth and (sectorial) STC/DSTC sweeps;
  - Tx power, spectrum, pulse shape, timing, mode and stagger.
- Generates:
  - FRUIT and ADS-B scenarios;
  - Mode-S interrogations for transponder verification;
  - targets for non-pulse-compression PSR;
  - a "Remote Field Monitor", which mimics an SSR A/C transponder.
- Out-of-Tolerance Detection (OTD) is checked against EUROCONTROL standards: 3 dB beamwidth, crossovers, punch-throughs, 1st sidelobe and back-lobe level.
- Numbers:
  - frequency "900MHz – 3.0GHz" (3.5 GHz optional);
  - HPD recording "from a distance of up to 40Km";
  - Rx sensitivity "-75dBm";
  - YIG 3 dB bandwidth "25MHz";
  - Mode A/C pulse "450ns"; Mode-S pulse "500ns";
  - weight "14kg";
  - downlink remote site at "maximum 2km";
  - downlink HPDs "measured at 1090 Mhz".
- A solar measurement gives the PSR vertical polar diagram and the electrical tilt from sun noise.

**RFX474.** X-band extension "for on-site performance checks of military hostile fire locating radars or **precision approach radars on airports**".

**RFT646 Radar RF Testset.**
- A dual-channel VNA covering "900-3500 MHz".
- Measures rotary joints, cable VSWR and loss, and finds LVA column faults.
- Does near-field scans of 3D PSR arrays (Martello S723/S743, Lockheed Martin FPS-117/77), "typical < 2 hours".
- Max Tx "<10dBm"; linear sensitivity "-20 … to -80dBm".

**RIM782 Radar Interface Module.**
- Records PSR, SSR and Mode-S video together with plot and track data.
- Links each plot to its raw video, so you can see why a plot appeared or disappeared.
- 6 video inputs, 2 recorded at a time; sampling "8MHz(2channels)/16MHz (1channel)"; 12-bit.
- Serial input "up to 128 Kb/s". Protocols include U-HDLC/LAPB/X.25 (ASTERIX, RDIF), CD1/CD2/ASR9, LINK 1 and AIRCAT500.

**UDR765 USB Data Recorder.**
- Passive ("spy-mode") recording of 2 serial lines plus the LAN (UDP/TCP).
- UTC timestamps with "µs resolution". The GPS450 gives "accuracy of 50μs", which is used to measure extraction and processing delay.
- Exports to SASS-C-compatible or RASS formats (.S4/.D6).

**Local plot and track analysis tools.**
- Inventory display.
- LAPB/X.25/ASTERIX analyser.
- **Pd and Accuracy Tool**, which compares results against a RES reference scenario.
- **Data Link Analyser** for Mode-S. It traces transponder ↔ radar ↔ ATC ↔ GDLP using ASTERIX Cat48 and Cat18, with "440 different recorded and calculated parameter and data fields".
- **Cluster Analysis for Mode-S** (POEMS clusters).

**Worked example (radar vs ADS-B).** A Mode-S radar showed an "azimuth bias increase of about 0.45° for elevation angles greater than 10°", caused by LVA beam widening. The MSSR did not.

**RGI1193 gyroscope/inclinometer** for encoder and levelling checks: range "±15°", sensitivity "0.01°", sampling "up to 1000Hz".

**Additional products.**
- UPM772 USB power meter.
- **DRFA912 Digital RF Analyser**: analyses Mode-S DPSK phase flips against Annex 10, and PSR chirp. Range "650 to 4000MHz".
- IFL520 IF-to-log converter, IF 10–500 MHz.
- **MSD840 Mode-S Decoder**: decodes 3A/C, Mode-S All-Call/Roll-Call, and IFF modes 1, 2 and 4.
- DTI529 Didactical Test Interrogator.

### Software tools for monitoring [D-ag]

**RTQC (Real Time Quality Control).** RASS runs "24 hours a day" on a radar site or in an ATCC, with remote monitoring and endless-loop recording.

**DHM Data Handling Module.** The input/output "backbone". It can run as an **RMCDE** (Radar Message Conversion & Distribution Equipment). Functions:
- recording and replay;
- reframing, e.g. serial U-HDLC in and UDP out;
- **real-time protocol conversion**;
- real-time correction of range/azimuth eccentricity and altitude;
- filtering on any field, e.g. S-address or MB data;
- 24/7 operation;
- "Real-time ADS-B video to plot extraction, output as ASTERIX Category 21". This needs a UVR892 or RIM782, optionally with an ARF800.
- Conversion example: legacy AIRCAT500 converted to an ASTERIX stream.
- Data Replay re-injects recordings, restamped with current UTC, into the ATCC multi-radar tracker (MRT).

**MRD3 Multi Radar Display.** A PPI maintenance display.
- Inputs: PSR, MSSR and Mode-S radars, ADS-B, MLAT and MRT data (e.g. ARTAS), plus weather, video and status.
- "6 sources of data can be displayed simultaneously".
- Map editor, "Limited ATC controller features", real-time ASTERIX CAT048 text view, and QNH correction.

**Radar Comparator, mono (RCM) and dual (RCD).**
- Standards:
  - EUROCONTROL SUR.ET1.ST03.1000-STD-01-01 (radar sensor performance analysis);
  - SUR/MODES/EMS/SPE-01 (Mode S station);
  - SUR.NET.ET1.ST01.1000-STD-01-01;
  - ICAO Annex 10, **ICAO Doc 8071** and **ICAO Doc 9684**.
- RCM uses one source of opportunity traffic. It computes **Pd, processing delay, false plot rate and code probabilities**, plus accuracy (range, azimuth and timestamp random errors).
- RCD uses two sources. It computes:
  - **systematic errors**: range, range gain, azimuth and time biases;
  - **random errors**: range/azimuth, X/Y, or longitudinal/transversal standard deviation.
- RCD produces "true trajectories" that are more accurate than either source. It also supports **radar vs ADS-B** comparison.
- Transponder delay deviations of "±0.25µs and ±0.5µs" can be measured.
- Corrections applied:
  - barometric height, using soundings retrieved over the internet;
  - refraction;
  - ACP encoder eccentricity.

**CMC Coverage Map Calculator.**
- Uses SRTM terrain at "1 to 3 arc seconds", a 4/3 Earth model and screening angles.
- Plots outside coverage are excluded from Pd and accuracy.

**SMS Surveillance Monitoring System.** Real-time multi-sensor QoS monitoring with alarms.
- Monitored sources: PSR/SSR/Mode-S, ADS-B, MLAT, A-SMGCS, ASDE-X and system tracks (e.g. ARTAS).
- Deployed in "Singapore, Australia, Indonesia, European ATM's".
- Links sensor Pd to a lower risk of a "Violation of Controlled Airspace (VCA)".
- Inputs:
  - ASTERIX **CAT001, 002, 008, 010, 011, 017, 018, 019, 020, 021, 030, 031, 034, 048, 062, 063, 065**;
  - CD1/2, ASR9, AIRCAT500, RAT31, LINK 1 and others.
- Platform: Linux servers, Windows consoles, raw-data archive of "more than 90 days".
- Level 1 report e-mailed "every 24 hours".
- **SMS statistics** (exact categories):
  - **Data counters**: special codes **7500/7600/7700**, CRC errors, delay.
  - **Mono-sensor statistics**:
    - code probabilities: valid, correct and incorrect A/C code, and overall false A/C ratio;
    - PSR/SSR association probability;
    - **Pd for PSR, SSR, Mode-S and ADS-B**;
    - missed plots and PSR false plots;
    - **multiple SSR target reports "categorized as multipath and reflections"**;
    - **"Sidelobe, backlobe and ringaround detections, split plots or non-classified plots"**;
    - average gap size and PSR/SSR jumps;
    - positional accuracy;
    - **resolution statistics** (Pd in resolution zones).
  - **Dual-sensor statistics**: range and azimuth bias, range gain, relative time bias, and ADS-B random error along and across track.

### Simulators [D-ag]

**RTG Radar Target Generator (PSR).**
- How it works: it detects the radar pulse, waits a fixed precise delay, then re-transmits it with set power, pulse width, frequency and Doppler.
- Use: as a Remote Test Target in the field, or for on-site injection.
- Versions:

  | Model | Band | Frequency |
  |---|---|---|
  | RTG1002 | L/S | "1001MHz to 3450MHz" |
  | RTG1062 | C | "4200MHz to 6400MHz" |
  | RTG1063 | X | "8.7GHz to 10.5GHz" |
  | RTG1085 | UHF | "400MHz to 460MHz" |

- RTG1002 target specs:
  - range "Min. 36m, max. 701km";
  - range resolution "21.4mm … sampling at 7GHz";
  - range accuracy "Bias 0.1m linearity 0.5ppm";
  - max speed "8190m/s"; Doppler resolution "0.25m/s";
  - output "Min -100dBm, max 0dBm"; dynamic range "100dB".
- One target per beam dwell. A second RTG is used for resolution tests.

**RES® Radar Environment Simulator (SSR/Mode S/IFF).**
- "up to 2048 SSR or Mode-S targets, reflectors, and LVA antenna behaviors on an RF level", injected straight into the radar's antenna connectors.
- The radar output is compared with the input scenario. Results: "radar accuracy, biases, measured Pd, reflection elimination, false plot rate".
- Can also generate scenarios at radar-data level: ASTERIX **Cat 001/002, 34/48, 021 and 62**, or RDIF, over serial or LAN.
- **Mode 5 Level 2 and 2B**. Moving platforms for ship-board tests. Couples with the RTG for combined SSR-PSR testing.
- ADS-B squitter "complying with D0 260".
- "the only available tool that allows a user to simulate full Mode-S data link for up to 2048 targets".
- Standards:
  - ICAO Doc 9871 and Annex 10 Vol IV;
  - EUROCONTROL EMS3.11/EMS4.0;
  - RTCA DO-260/A/B/C / EUROCAE ED-101;
  - EUROCAE ED-73 (up to rev F);
  - STANAG 4193 Ed3;
  - DoD AIMS 03-1000/17-1000.
- Bad-transponder simulation:
  - RF offset "-10..+10 MHz";
  - pulse width and position "-200..+200 ns";
  - amplitude "-30..+6 dB";
  - "4-level overlap SSR/ADS-B/FRUIT waveforms + jamming signals".
- Antenna simulation:
  - 4 RF channels: Sum, Delta, Omni and ADS-B;
  - VPD "up to 16" patterns;
  - antenna types: LVA, rotating phased array, and non-rotating phased array.
- Tx "1090MHz ± 10 MHz"; Rx "1030MHz ± 10 kHz".
- Mode 5 and military options are "only available for cleared customers".

### Services [D-ag]
- **Level 1**: data analysis and monitoring, repeated every 6 months.
- **Level 2**: sensor baseline analysis.
- **Level 3**: commissioning and specialised measurements (RTG/RES).
- **Flight Check Analysis.** Combines:
  - a DGPS reference trajectory;
  - ADS-B traffic of opportunity (ARF800 receiver);
  - simultaneous PSR/SSR recording at the radar head.

  It assesses whether the radar is ready before expensive flight checks are flown.

## Relevance to us [Y]
This is the clearest picture of what the sponsor group sells: **measurement of surveillance quality**.

**The jury's vocabulary:**
- Pd and false plot rate.
- Code validity and correctness.
- **Reflections and multipath**, sidelobe and ring-around detections, and **split plots**.
- Resolution.
- Range and azimuth bias.
- Processing delay.
- Coverage with terrain screening.

**Their standards:** EUROCONTROL SUR ET1, ICAO Doc 8071 and 9684, ED-73 and DO-260.

**Their data plumbing:** ASTERIX CAT048, 021, 062 and 034, RMCDE, and protocol conversion.

**What our concept should do:**
- State its **Pd, accuracy (bias and random), latency and integrity** in these exact terms.
- Propose how it would be **verified**: RES/RTG injection, SkyRF flights, and radar-vs-ADS-B comparison.
- Speak ASTERIX at its interfaces.

**Hooks to use:**
- The RFX474 is explicitly aimed at **precision approach radars on airports**.
- RTQC/SMS real-time quality monitoring with alarms is a ready-made model for an **integrity monitor** for an automated approach aid.
