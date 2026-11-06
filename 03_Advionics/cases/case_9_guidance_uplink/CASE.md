# Case 9 — Radar-derived guidance sent as data (no voice in between)

**Task wording that triggers it:** "uplink", "data link", "message format", "latency / update rate", "time to alert",
"what happens when messages stop", "send the deviation to the aircraft". Origin: mentor role-play statement S4
(R_mentor_roleplay_2026-11-04.md, [Y]); spoiler fit: "translate signal" + "if communication is lost".

**Concept (5 lines)**
1. 96-bit message: seq, time of *measurement*, range, vertical/lateral deviation, valid flag, quality, CRC-24.
2. LSBs justified against the guidance tolerance (rounding ≤ 0.05 m vertical vs a 35 m alert limit).
3. Receiver: CRC fail → discard; no message for `timeout` → GND GUIDANCE LOST, needles removed (atc.guidance).
4. Timeout trade-off: faster alert vs nuisance alarms, computed exactly (run-length formula) and by Monte Carlo.
5. Not solved here: authentication (CRC ≠ authentication), transport choice (Mode S Comm-A / VDL2 / dedicated), load.

**Three numbers** (`outputs/result.md`)
- **96 bits** incl. CRC-24 → 96 bit/s at 1 Hz; worst rounding el **0.05 m**, az **0.125 m**.
- Nuisance LOST per 180 s approach at 5 % message loss: timeout 2 s **34.8 %**, 3 s **2.1 %**, 5 s **0.01 %**
  (Monte Carlo 34.2 / 1.5 / 0.0 %).
- CRC: **0 of 1832** corrupted messages accepted (BER 1e-3).

**What the jury wants to hear:** a bit-level format they could implement, a link budget (VDL Mode 2 31.5 kbit/s,
C_ETSI_EN301841_1; Mode S uplink), time-to-alert budget, behaviour on stale data, test with RES / SkyRF Generator.

**Risks / limits:** independent losses only (no bursts); latency not modelled; no authentication; field widths [Y];
the Comm-A payload size is from general knowledge, not read.

**Mentor questions:** May guidance go by data instead of voice? Which link (Mode S, VDL2, new)? Required time to alert
and integrity? Is authentication in scope?

**Run:** `python 03_Advionics/cases/case_9_guidance_uplink/run.py [--set rate_hz=2] [--set timeouts_s=[1,2,4]]`.
Reuses `atc.uplink`, `atc.par`, `atc.guidance`, `aerokit.approach`.
