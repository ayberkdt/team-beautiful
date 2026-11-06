# S_00_summary: Advionics / Intersoft Electronics product lines, and what the jury will reward

- **Written:** 2026-11-04, for Team Beetiful (Advionics challenge "Automated Approach Guidance", presentations Fri 6 Nov).
- **Tags used:**
  - **[D-ag]** = I read it in this session on the named S_ file's source.
  - **[Y]** = my judgement.
  - **[A]** = a search snippet only.
- **Scope:** this summary builds on `..\Advionics yaklaşma rehberliği\R_advionics_research.md`. That note covers L-IESA basics, SkyRF basics, the Kongsberg LoI and IDI ownership.
- **Not re-read this session:** the Intersoft Navaids test-equipment and Navaids-services pages. Their content is confirmed indirectly by the SkyRF brochure and the ATC-services page.

## 1. Who does what
- **Advionics (Oostkamp)** builds RF hardware: design, manufacturing and test.
  - Its flagship is the **L-IESA® non-rotating naval IFF** antenna. It also makes a frigate radar antenna.
  - Its jobs are hardware design, test and production. There are no software or AI vacancies.
  - Sources: S_advionics_home, S_advionics_jobs_listing, S_advionics_job_hw_design.
- **Intersoft Electronics (Olen)** owns the civil ATC/CNS product lines:
  - **RASS** (radar test and analysis);
  - **SMS** (surveillance monitoring);
  - **RES/RTG** (simulators);
  - **SkyRF** (drone-based CNS measurement);
  - **NGSP / ASR-M / NORA** (radar processing and antennas);
  - ATC/airport services.
- The two companies share one engineering stack: RF, FPGA/CPLD, embedded, PCB, mechanical; 5 MHz–26 GHz; EN 9100. Sources: S_intersoft_product_development, S_advionics_product_development.

## 2. Product lines and the challenge reading each supports

The four readings are:
- **(a)** voice → display;
- **(b)** lost communication / lost transponder;
- **(c)** radar/SSR surveillance-based guidance or monitoring;
- **(d)** approach aids (ILS/PAPI/GBAS) and their verification.

| Product line (source) | What it does / key numbers [D-ag] | Supports |
|---|---|---|
| **RASS test equipment** (RFA641, RFT646, RIM782, UDR765, DRFA912, MSD840) (S_intersoft_rass_catalogue) | Top-down radar-chain checks: antenna HPD/VPD, Rx/Tx, encoder, video ↔ plot linking, ASTERIX/LAPB recording with 50 µs GPS timestamps. RFA641 covers 900 MHz–3.0 GHz; **RFX474 is aimed at precision approach radars on airports** | (c), (d) |
| **RASS software**: Radar Comparator, CMC, Pd & Accuracy tool, Mode-S Data Link Analyser (S_intersoft_rass_catalogue, S_intersoft_rass_sms_leaflet) | **Pd, processing delay, false-plot rate, code probabilities, range/azimuth/time bias and random errors**. Radar vs ADS-B comparison. Standards: EUROCONTROL SUR ET1, ICAO Doc 8071 / 9684 | (c) |
| **SMS** Surveillance/Sensor Monitoring System (S_intersoft_sms_brochure, S_intersoft_sms_adsb_leaflet, S_canso_sms_1M_hours) | Real-time KPIs: "detection probability, update rate, integrity, latency, false plots". Counts **multipath/reflections, sidelobe/ring-around, split plots**, 7500/7600/7700 codes. Also monitors **ILS LOC & GP**. More than 1,000,000 hours since 2011. Deployed in Singapore, Australia, Indonesia and Europe | (b), (c), (d) |
| **DHM / MRD3**: data handling and display (S_intersoft_rass_catalogue, S_intersoft_rass_sms_leaflet) | RMCDE, **real-time protocol conversion**, ADS-B video → **ASTERIX CAT021**, legacy formats → ASTERIX, replay into the MRT. MRD3 shows 6 sources at once, with "limited ATC controller features" | **(a)**, (c) |
| **RES®** SSR/IFF environment simulator (S_intersoft_res_page, S_intersoft_res_update_2025) | Up to **2048** Mode S / SSR / IFF / ADS-B targets at RF; Mode 5 L1/L2/2B; FRUIT, reflectors, jamming; Tx 1090 MHz, Rx 1030 MHz. ED-73, DO-260, EMS 4.0, STANAG 4193, AIMS | (c) and (b) testing |
| **RTG** PSR target generator (S_intersoft_psr_rtg) | Tests **Pd, Pfa, accuracy, resolution, plot latency, load**. Range 36 m–701 km; range resolution 21.4 mm; Doppler resolution 0.25 m/s; drone/stealth RCS | (c) testing |
| **SkyRF® drone** (S_intersoft_skyrf_brochure, S_intersoft_bhansa_case, S_intersoft_uk_entity) | ILS/DME via **"Mini-Approach"** trajectory: GP angle, DDM, **threshold crossing height**. PAPI angles. PSR/SSR HPD/VPD. Up to 50% fewer flight checks. LOC DDM uncertainty ≤ 0.02 %. Customers: BHANSA and Skyguide. New UK "hybrid flight inspection" entity (2 Nov 2026) | **(d)**, (c) |
| **SkyRF Generator** (S_intersoft_skyrf_generator) | Drone-borne Mode S/5 and PSR targets via FPGA delay; **PSR alignment at touchdown zones**; 3.75 m range resolution | (c), (d) |
| **NGSP / ASR-M / processing algorithms** (S_intersoft_ngsp_intro, S_intersoft_asrm_booklet, S_intersoft_processing_whitepaper, S_intersoft_mlu_brochure) | Used on "**Precision Approach**" radars among others. 16-bin MTD, CFAR, VCC (windfarm clutter −20 to −30 dB), **True 3D Height from PSR (no transponder needed)**, SSR reflection processing. Outputs ASTERIX CAT048/034/008/240/253. References: FAA 50+ ASR-8, NATO S723/743D, Hensoldt ASR-NG | **(b)**, (c) |
| **NORA®** non-rotating arrays (S_intersoft_nora_intro_pdf, S_intersoft_nora_page) | S- and L-band PSR and SSR/IFF; 3–12 m diameter; 16–64+ elements; 2–32 kW per beam; ±22.5° fine scan; **sector scan on runway areas**; tracking beam; monopulse | (c) |
| **L-IESA® NR-IFF** (S_intersoft_liesa_leaflet, S_intersoft_iff_integrations, S_esut_wilhelmshaven_2022) | 200 NM with a 1200 W interrogator; 360° coverage at up to 120 rpm; beam re-pointing in 100 ms; ±15° roll/pitch compensation; az accuracy < 0.1° RMS; Mode 5 L1/L2; Link-16 antenna integrated. **German Navy F123 (via Saab)**; L-IESA Mini on German and Portuguese navy vessels | (c) naval/UAS, (b) |
| **IFF integration items**: TRCU, secure cabinet, AIMS certification (S_intersoft_iff_integrations, S_intersoft_aims_cert) | Transponder control via **ASTERIX Cat253**; PNT fed to the transponder over ARINC-429 / NMEA; cabinet shielding > 80 dB; NATO AEtP 12 / AIMS | (b), (c) |
| **ATC & airport services** (S_intersoft_atc_airport_services) | **VCS voice communication systems, synthetic D-ATIS with datalink, aerial situation displays**, ILS installation and maintenance, **MLAT**, airfield lighting, AWOS, RF impact analysis. These read as installation/maintenance services, not own R&D products | **(a)**, (d) |
| **Drone detection / C-UAS** (S_intersoft_drone_detection) | Drone channel on ASR-M; Doppler for hovering targets; drone/bird classification; partners EM&E and Indra | (c) |

**Not found:**
- Any own MLAT/WAM product. MLAT appears only as an installed and monitored system.
- Any own ATC voice or speech-recognition product.
- Any public mention of EUROAVIA, ideathons or student challenges (S_search_euroavia_sponsor).

## 3. What this implies for the challenge readings [Y]
- **(c) Radar/SSR surveillance, and (d) approach aids and their verification, are the sponsor's core.**
  - The group sells **measurement of surveillance and navaid quality**, plus radar processing and antennas.
  - "Automated approach guidance" from this sponsor most naturally means one of two things:
    - a ground surveillance sensor producing approach-path deviations (PAR-like, cooperative and/or non-cooperative);
    - an automated approach aid whose **integrity is monitored and verified** the way they monitor radars.
- **(b) Lost comm / lost transponder is a strong secondary reading.** The sponsor's own whitepapers argue True 3D Height as a backup for "transponder failure". SMS already counts 7600 squawks.
- **(a) Voice → display is adjacent, not core.** It touches their VCS / D-ATIS / situation-display services and their DHM conversion and MRD display.
  - If the challenge is speech-based, anchor it in **surveillance correlation**: match the spoken callsign to a Mode S / ADS-B track and output ASTERIX.
  - Add an **SMS-style quality monitor** on top.

## 4. Five things the jury will reward [Y, based on the sources above]
1. **Quantified performance in their own KPI vocabulary.** Use:
   - Pd and Pfa;
   - accuracy as **bias + random error**, range and azimuth;
   - update rate and latency;
   - false/split/reflected plots;
   - code/identity correctness;
   - **integrity and alerting**.

   Tie each number to a standard: EUROCONTROL SUR ET1, ICAO Doc 8071 / 9684, ED-73, DO-260; for approach, CS-AWO / Annex 10 from the R_ note. (S_intersoft_rass_catalogue, S_intersoft_sms_brochure)
2. **A verification and certification plan using their tools.** Proposed sequence:
   - **RES/RTG** scenario injection as Level 3 commissioning;
   - **SkyRF** flying the approach volume (Mini-Approach, PAPI, HPD/VPD);
   - **radar-vs-ADS-B** dual-source accuracy analysis;
   - **shadow mode** next to the legacy system.

   This mirrors their FAT → SAT → Level 1/2/3 service ladder. (S_intersoft_radar_services, S_intersoft_mlu_brochure, S_intersoft_skyrf_brochure)
3. **RF/physics realism and dissimilar sensors.** Show a link budget, band choice, and the angle error R·δ versus range. Address **multipath at low elevation and over flat sea**, which they already fix in L-IESA with VAPD.
   - Combine a **cooperative** source (Mode S / Mode 5 / ADS-B) with a **non-cooperative** one (PSR True 3D Height), so guidance survives transponder or GNSS loss.
   - Explain what happens under GNSS spoofing.

   (S_intersoft_liesa_leaflet, S_intersoft_processing_whitepaper)
4. **Interfaces and retrofit, not greenfield.**
   - Output **ASTERIX** (CAT048 plots, CAT021 ADS-B, CAT062 tracks; Cat253 for control).
   - Be manufacturer-independent and work with "any MSSR interrogator".
   - Use a phased or mid-life-upgrade path that reuses existing ASR/SSR/NORA/ILS assets.
   - Plan for real-time monitoring with alarms, SMS-style.

   (S_intersoft_ngsp_intro, S_intersoft_iff_integrations, S_intersoft_mlu_brochure)
5. **Dual-use and sustainability with credible numbers.**
   - Civil plus defence/naval: ship-deck UAS recovery using L-IESA and the ship's PNT.
   - Sustainability arguments the sponsor itself makes:
     - "up to 50% fewer flight checks / 50% less CO2" (SkyRF);
     - ESG through modularity and long life (ASR-M);
     - windfarm and 5G coexistence (VCC).
   - Quote these as the sponsor's claims, not ours.

   (S_intersoft_skyrf_brochure, S_intersoft_asrm_booklet, S_intersoft_news_list)

## 5. Cautions for the pitch
- **CEO name:** in 2026 press releases, **Luc Switten** is CEO of Advionics or of the IE Group. The 2025 VRT article named Jan Bonte. Do not name a CEO unless we check again. (S_advionics_new_facility_pr, S_advionics_kongsberg_loi)
- **RF test limit conflict:** Advionics' testing page says DC–**24** GHz, while the product-development page says **26** GHz. (S_advionics_testing)
- **L-IESA leaflet table:** I re-paired labels and values after a misaligned extraction. The capability-box figures (200 NM, 1200 W, 120 rpm, 100 ms, ±15°) are safe to quote. The table pairings (e.g. < 0.1° RMS = azimuth accuracy) are my reading. (S_intersoft_liesa_leaflet)
- **RASS-S / RASS-R:** these names come from a 2018 third-party document. The current site says "RASS®". (S_skyradar_rass_s_training, S_scribd_rass_r_failed)
- **CAAS Singapore as "first APAC SMS customer":** seen only in a snippet [A], not verified. (S_canso_sms_1M_hours)
