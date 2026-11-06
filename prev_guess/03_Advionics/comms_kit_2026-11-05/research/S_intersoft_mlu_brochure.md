# S_intersoft_mlu_brochure: "Midlife Upgrade Projects for ASR, En-Route and Air Defence radar" (IE-CD00109-011)

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2025/03/IE-CD00109-011-Midlife-Upgrade-Projects-MLU-final-1-1.pdf
- **Date read:** 2026-11-04. I loaded the 17.9 MB PDF into memory with PyMuPDF and read the full extracted text.

## What it says [D-ag]
- **Track record.** Intersoft has run mid-life-upgrade (MLU) projects on civil and military ASR and long-range radars "since the early 2000s". NGSP® is the core of each upgrade. NORA® is an optional add-on.
- **Challenges listed:**
  - obsolescence
  - wind farms, 4G/5G and traffic density
  - regulation (RoHS/REACH, ITU)
  - a separation change, quoted as: "the air traffic separation standard shifted from 5NM to 3NM"
- **True 3D Height on ASR.** Civil ATC depends on SSR for height, "which is mandatory in civil aviation, but can cause tragedy in case of transponder failure". The phase/amplitude difference between two cosec² beams gives elevation, and from that, RCS.
- **Advanced algorithms:**
  - pulse compression done by FFT
  - windowed mismatched filters to suppress time sidelobes
  - "MTD with 16-bin Doppler"
  - CFAR that uses signal history
  - VCC, which reduces tower and nacelle returns by "20- 30 dB" and blade clutter by "up to 20 dB"
  - SCC against anomalous propagation
- **NORA® in this brochure:**
  - S- and L-band arrays for ASR and en-route radar.
  - ±22.5° fine scan, then the array is stepped by one element.
  - Options: confirmation look-backs and sector scanning ("windfarm or runway areas"), dual surveillance beams, and a tracking beam.
  - **PSR and SSR co-located: "two rings under a radome".**
- **Phased MLU path:**
  - Phase 1: NGSP receiver and processor, with a fully redundant system in "a single 19" rack".
  - Phase 2: solid-state transmitter.
  - Phase 3: NORA with "integrated GaN power electronics".
  - The new system is validated in **shadow mode**, running in parallel with the legacy system.
  - **CLIC** (Closed Loop Integration Concept) provides remote commissioning, support and security updates, citing the EU Cyber Resilience Act (CRA).
- **References, quoted exactly:**
  - "Upgrade of 50+ ASR-8 systems for the FAA under the CTD project"
  - "Upgrade of S723/743D long range radars for NATO and other Air Forces"
  - "Upgrade of TPS43/70/75 tactical radar in Europe, the USA and South America"
  - "Upgrade of TA-10 and ASR-8 systems for European Air Forces"
  - "Integration of NGSP technologies in Hensoldt ASR-NG"

## Relevance to us [Y]
- The named references (the **FAA, NATO, European Air Forces, Hensoldt**) are customer names we can cite carefully.
- The jury's culture values **shadow-mode validation** and **phased, retrofit-first deployment**. Building both into our deployment plan would resonate.
- The 5 NM → 3 NM separation point also links surveillance accuracy and update rate to capacity, which is useful for a sustainability or capacity argument.
