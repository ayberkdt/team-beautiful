# S_intersoft_sms_brochure: "Sensor Monitoring System" brochure

- **URL:** https://intersoft-electronics.com/wp-content/uploads/2026/10/IE-CD-0xxxx-001-SMS-1-1.pdf
- **Date read:** 2026-11-04. WebFetch saved the PDF, and I read the text with pdftotext.

## What it says [D-ag]

### The problem it addresses
- ANSP networks mix PSR, SSR, Mode-S, ADS-B and MLAT sensors from several manufacturers, each in a different data format.
- KPIs "such as detection probability, integrity, update rate, and accuracy must be monitored continuously".
- Thresholds come from ICAO PANS-ATM. Cooperative sensors (ADS-B, MLAT) are held to EUROCAE ED standards.
- Correct identification ("via Mode-S address, code assignment") is described as critical.

### Architecture
1. **Sensor data acquisition layer**
   - A Sensor Interface Unit (SIU) normalises sensor data and forwards it.
   - Network gateways take in ASTERIX or manufacturer-specific protocols.
   - **Optional GNSS time-sync modules are offered for MLAT and Mode-S.**
   - Health and status inputs cover built-in test (BITE), temperatures and power.
2. **SMS server**
   - On-premise, virtual machine, or geo-redundant cluster.
3. **Client applications**
   - A web dashboard.
   - Engineering plots, quoted as: "azimuth errors, range accuracy, SSR code statistics, Mode-S ELS/EHS validation, ADS-B/MLAT comparison".
   - Replay for incident analysis.
   - A maintenance planner.

### What it computes and how it alerts
- **KPIs:** "detection probability, update rate, integrity, latency, false plots, and coverage quality".
- **Alarm examples:** loss of coverage, "timing drift, low SNR, abnormal plot patterns".
- **Alert channels:** e-mail, SNMP, SMS text message, and notification to the ATC centre.
- **Proof claim:** "Over a million live operational hours".
- **Engine:** it "applies advanced analytics using Intersoft Electronics RASS® engines".

## Relevance to us [Y]
- This brochure is the sponsor's own list of what matters: detection probability, integrity, update rate, accuracy, latency, false plots and identification. We should use exactly these as the **KPI table of our concept**.
- MLAT shows up twice: as a monitored sensor, and as the reason for offering GNSS time-sync modules.
