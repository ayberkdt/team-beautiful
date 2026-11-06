# R_14cfr_91_227_adsb — 14 CFR § 91.227, ADS-B Out equipment performance requirements (US)

## Citation
U.S. Code of Federal Regulations, Title 14, Part 91, § 91.227 "Automatic Dependent Surveillance-Broadcast (ADS-B) Out equipment performance requirements". Current version on eCFR at read time.
URL: https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-C/section-91.227 (read via the eCFR renderer API: https://www.ecfr.gov/api/renderer/v1/content/enhanced/current/title-14?part=91&section=91.227)
Date read: 2026-11-04. Source class: PRIMARY (US regulation). It is **US** law; the European equivalent (EU 1207/2011 as amended, and EASA CS-ACNS) was **not** read.
Labels: [D-ag] read this session.

## Facts [D-ag]
- (b): 1090 ES equipment per TSO-C166b / DO-260B, or TSO-C166c / DO-260C with Change 1. UAT per TSO-C154c/d, DO-282B/C (allowed outside Class A only).
- **(c)(1) performance**: NACp "less than 0.05 nautical miles" (i.e. NACp ≥ 8, EPU < 93 m; see the R_1090_riddle §7 table); NACv "less than 10 meters per second" (NACv ≥ 1); NIC "less than 0.2 nautical miles" (NIC ≥ 7); SDA "≤ 10⁻⁵ per flight hour"; SIL "≤ 10⁻⁷ per flight hour or per sample" (SIL = 3).
- (c)(2)–(3): changes in NACp, NACv, SDA and SIL must be broadcast within 10 s; changes in NIC within 12 s.
- (d): the minimum message set includes length and width, lat/lon, baro altitude, velocity, TCAS installed and RA status, Mode A code, aircraft identification, emergency status, IDENT, ICAO 24-bit address, emitter category, ADS-B In capability, geometric altitude, NACp, NACv, NIC, SDA and SIL.
- **(e) latency**: geometric position must be transmitted ≤ **2.0 s** after measurement, with at most **0.6 s uncompensated**; the rest must be compensated by extrapolation. Position and velocity at least **once per second** airborne or moving on the surface; at least every **5 s** when stationary on the surface.
- Mapping to NACp/NIC codes is the agent's own [C-ag] use of the R_1090_riddle.md tables (NACp 8 = <0.05 NM; NIC 7 = <0.2 NM). The regulation states distances, not code numbers.

## Relevance to us [Y]
This gives the quality gate for accepting ADS-B reports in our approach tracker: reject or down-weight below NACp 8, NIC 7 or SIL 3. It also gives the latency model (≤ 2.0 s total, ≤ 0.6 s uncompensated) for a time-alignment error budget, and the 1 Hz minimum rate (2 Hz typical from R_1090_riddle Table 1.4). Note the US vs EU source when presenting to a European sponsor.
