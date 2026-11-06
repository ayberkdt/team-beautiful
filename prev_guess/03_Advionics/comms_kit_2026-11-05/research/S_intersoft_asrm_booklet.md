# S_intersoft_asrm_booklet: "ASR-M® A modular approach to Airport Surveillance Radar" (IE-CD-01358-003)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2024/11/IE-CD-01358-003-ASR-M-HR.pdf
- **Date read:** 2026-11-04. WebFetch saved the PDF, and I read it with `pdftotext -layout`.

## What it says [D-ag]
- **Configurations.** ASR-M® comes in "four standard primary radar configurations": single or dual receive channels, each with or without a primary transmitter. Civil users usually need dual redundant channels; military users less so.
- **Signal chain.** It is modular from the RF signal at the antenna "all the way to the ASTERIX output" (RF to IF, combining, extraction). The building blocks are standard COTS units.
- **Core algorithms:**
  - **Dual-beam processing.**
  - **VCC®** (Vertical Clutter Cancellation, patented): uses the lower beam to shape the upper beam and suppress clutter at elevation, e.g. wind turbines. The booklet says its high sensitivity "also improves drone detection".
  - **Median filtering**: rejects RF interference such as 5G.
  - Doppler processing.
- **Key modules:**
  - **ISP (IF Signal Processor):** takes beam IF in and puts plots and beam video out. Runs "VCC, Median Filtering, 16-channel MTD, CFAR, adaptive clutter maps, and soft STC".
  - **RDPS (Radar Data Processing Server):** plots from all beams plus the SSR/IFF sensor. After beam combining, "3D height can be calculated". Also does sensor combining, scan-to-scan correlation, **"SSR reflection processing, and false plot filtering"**.
  - **SCU (System Control Unit):** triggers and timing.
  - **FSU-R (Frequency Synthesizer Unit & Receiver):** clocks, local oscillators, transmit and test waveforms, and RF-to-IF receivers.
- **Bands and interfaces.** Available for "S and L band operation". SSR data can come in "from any MSSR interrogator". ASTERIX goes out to the ATM system.
- **Lifecycle claims.** It has an "infinite lifetime" through module upgrades. CLIC (Closed-Loop Integration Concept) allows remote firmware and software updates.
- **ESG framing.** The booklet presents modularity as reducing power, components and logistics, and claims coexistence with telecom and wind-energy stakeholders.
- **No numeric performance specs** are given (no range, Pd or accuracy figures).

## Relevance to us [Y]
- The jury expects a **sensor → plot extractor → data processor (reflection and false-plot filtering, 3D height) → ASTERIX** chain. Our concept's block diagram should use these block names.
- The booklet also includes an **ESG/sustainability** section, which matches the Ideathon's "sustainability" judging criterion. The sponsor already pitches modularity and coexistence as ESG arguments.
