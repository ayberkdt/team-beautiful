# Case 8 — Surveillance integrity: spoofed / displaced ADS-B on final (and the IFF / Mode 5 angle)

**Task wording that triggers it:** "spoofing", "fake / ghost targets", "ADS-B integrity", "multilateration / WAM",
"authentication", "cyber", "IFF / Mode 5". Sponsor fit: RES injects up to 2048 Mode S/ADS-B targets with FRUIT and
reflections (S_intersoft_res_page); SMS monitors MLAT and ADS-B (S_intersoft_sms_adsb_leaflet); L-IESA Mode 5 IFF.

**Concept (5 lines)**
1. CRC is not authentication: a spoofer's squitter passes the Mode S CRC (shown with `modes.encode_position`).
2. What a spoofer cannot fake is the time of arrival at each receiver: TDOA multilateration of the same 1090 MHz reply.
3. Consistency test in the horizontal plane, MLAT covariance + ADS-B's own noise, Mahalanobis > k and > floor.
4. Display rule: an inconsistent target is shown as UNVERIFIED, never silently dropped or silently trusted.
5. Test plan with the sponsor's tools: RES scenarios, radar-vs-ADS-B comparison, SMS-style live KPIs.

**Three numbers** (`outputs/result.md`, 5 receivers, 2 ns timing [Y])
- False alarms on honest ADS-B (15 m noise): **0.0 %** of 600.
- Offset flagged in ≥ 99 % of trials from **150 m**; ~50 % at 75 m (detection curve in C8).
- Honest MLAT horizontal error median **1.2 m**, P95 **3.2 m** (WAM measured 6–7 m on final, R_icao_suricg7_ip14_wam).

**What the jury wants to hear:** receiver siting and GDOP (3-D GDOP 37.8 here: height is poorly fixed from the ground,
so altitude is checked against Mode C/S), clock synchronisation, Pfa/Pmd of the test, RES-based test cases.

**Risks / limits (gaps):** no clock-sync error model, no NIC/NACp/SIL decoding, no burst/replay timing model;
**IFF Mode 5 (cryptographic) not modelled** — only named as the military answer; parameters [Y].

**Mentor questions:** Civil ADS-B/Mode S, or military IFF (Mode 5)? Which sensors may the ground use (MLAT, PSR)?
What must the display do with an unverified target?

**Run:** `python 03_Advionics/cases/case_8_surveillance_integrity/run.py [--quick] [--set sigma_t_ns=5]`.
Reuses `atc.mlat` (new `adsb_sigma_m`, `dims` options), `atc.modes`.
