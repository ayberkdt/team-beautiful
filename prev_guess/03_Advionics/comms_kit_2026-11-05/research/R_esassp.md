# R_esassp — EUROCONTROL Specification for ATM Surveillance System Performance (ESASSP), Vol 1

## Citation
EUROCONTROL, *EUROCONTROL Specification for ATM Surveillance System Performance (Volume 1)*, EUROCONTROL-SPEC-147, Edition 1.3, edition date 21/03/2024, Released Issue, ISBN 978-2-87497-022-1.
URL (PDF): https://www.eurocontrol.int/sites/default/files/2024-03/Released%20Issue%20ESASSP%20%20Vol%201%20Ed%201.3.pdf
Landing page: https://www.eurocontrol.int/publication/eurocontrol-specification-atm-surveillance-system-performance-esassp
Date read: 2026-11-04. Read method: PDF text extracted with PyMuPDF, then the requirement tables read in full (doc pages 28–38, 98; PDF pages 30–40, 100).
Source class: PRIMARY.
Version note [D-ag]: the EUROCONTROL consultation page lists a proposed **Edition 2.0** (Vol 1 and Vol 2 PDFs dated 2026-06, `esassp-vol-1-ed-2-0.pdf`). According to the search snippet, consultation runs until 26 August 2026 [A]. The agent did NOT read Ed 2.0. The numbers below are from **Ed 1.3** and may be superseded.
Labels: [D-ag] read this session; [A] snippet only.

## Key framing [D-ag] (§3.2.1, doc p.28–29)
- Requirements come from European experience over recent decades, "mainly on the basis of radar technology". They are **technology-agnostic system requirements**, covering the whole surveillance chain (radar, MLAT, ADS-B, tracker).
- Table 3 = 5 NM (5N_C), Table 4 = 3 NM (3N_C), Table 5 = 2.5 NM on the same final approach (2.5N_C). Mandatory criteria are in bold; recommended criteria in normal font.
- Note: ESASSP does **not** state a sensor "Pd" figure. It uses "probability of update" (PU) of the system output per measurement interval (MI). For pure non-cooperative (PSR-only) legacy systems in low-density traffic, Annex D gives PU > 90 %.
- Required data items (doc p.28): position, pressure altitude, aircraft identity (ACID and/or Mode 3/A), emergency indicator, SPI, and cooperative/non-cooperative/combined and coasted status. Optional: ground speed, track angle, IAS, rate of climb/descent.

## Requirement table extract (mandatory; recommended in brackets) [D-ag]
| Item | 5 NM (Table 3, doc p.30–31) | 3 NM (Table 4, doc p.33–35) | 2.5 NM final approach (Table 5, doc p.36–38) |
|---|---|---|---|
| R1 measurement interval (MI) | ≤ 8 s (≤ 6 s) | ≤ 5 s (≤ 4 s) | ≤ 5 s (≤ 4 s) |
| R2 PU horizontal position | ≥ 97 % for 100 % of flights and ≥ 97 % global, data age ≤ 10 s (≥ 99 % global) | ≥ 97 % per flight and global, data age ≤ 7 s (≥ 99 % global) | ≥ 99 % per flight and global, data age ≤ 7 s |
| R3 missed 3D positions in long gaps (> 3 × MI + 10 %) | ≤ 0.5 % | ≤ 0.5 % | = 0 % |
| R4 horizontal position RMS error | ≤ 500 m global, < 550 m per flight (≤ 350 / 385 m) | ≤ 300 m global, < 330 m per flight (≤ 210 / 230 m) | ≤ 200 m global, < 210 m per flight (≤ 160 / 180 m) |
| R5 ≥3 consecutive correlated errors larger than | 926 m (0.5 NM): ≤ 0.03 % | 555 m (0.3 NM): ≤ 0.03 % | 460 m (0.25 NM): = 0 % |
| R6 relative time of applicability, close proximity | < 10 NM: ≤ 0.3 s RMS | < 6 NM: ≤ 0.3 s RMS | < 5 NM: ≤ 1 s (≤ 0.3 s RMS) |
| R7 PU pressure altitude, correct | ≥ 96 % global | ≥ 96 % | ≥ 96 % |
| R8 / R9 pressure-altitude data age | avg ≤ 4 s; ≥ 16 s treated as not available | same | same |
| R10 incorrect pressure altitude | ≤ 0.1 % | ≤ 0.1 % | ≤ 0.1 % |
| R11 pressure altitude unsigned error | ≤ 200/300 ft in 99.9 % (stable), ≤ 300 ft in 98.5 % (climb/descent) | same | ≤ 300 ft in 98.5 % |
| R12 delay of emergency/SPI change | ≤ 12 s | ≤ 7.5 s | N/A |
| R13 delay of identity change | ≤ 24 s | ≤ 15 s | N/A |
| R14 PU identity correct | ≥ 98 % global (≥ 98 % per flight) | ≥ 98 % | ≥ 98 % |
| R15 incorrect identity | ≤ 0.1 % | ≤ 0.1 % | ≤ 0.1 % |
| R16 ROCD RMS (optional) | ≤ 250 ft/min stable, ≤ 500 ft/min climbing | same | ≤ 500 ft/min |
| R17 track speed RMS (optional) | ≤ 6 m/s straight, ≤ 11 m/s turn (≤ 4 / 8) | same | ≤ 5 m/s straight (≤ 4) |
| R18 track angle RMS (optional) | ≤ 10° straight, ≤ 25° turn | same | ≤ 10° straight |
| R19 uncorrelated false target reports | < 10 per 900 NM² over 450 MIs | ≤ 2 per 100 NM² over 720 MIs | ≤ 1 over 720 MIs |
| R20 falsely confirmed tracks near true tracks | ≤ 2 per hour within 13000 m (7 NM) | ≤ 1 per hour within 16700 m (9 NM) | 0 |
| R21 continuity (critical failure) | ≤ 2.5·10⁻⁵ per hour | ≤ 2.5·10⁻⁵ per hour (recommended only, Note 4) | ≤ 2.5·10⁻⁵ per hour |
| R23 update time variation | — | — | 5th percentile ≥ mean − 0.5 s; 95th percentile ≤ mean + 0.5 s |
| R24/R25 IAS (optional) | — | — | PU ≥ 96 % (data age ≤ 16 s); data age ≤ 6 s in 90 % |

- 2.5 NM CAV for false-target checks: 10 NM along the approach path, ±2.5 NM laterally (doc p.36).
- Table 5 Note 3: with fewer than 100 samples, PU is computed as if the remaining samples up to 100 succeeded. "One miss will correspond to 99%", so in practice one miss is acceptable for R2.

## Annex D, non-cooperative only (legacy, low density) [D-ag] (doc p.98)
| | 5N_N | 3N_N |
|---|---|---|
| MI | ≤ 8 s | ≤ 5 s |
| PU horizontal position | > 90 % global | > 90 % global |
| Horizontal RMS | ≤ 500 m | ≤ 300 m |

## Relevance to us [Y]
This is the acceptance-criteria table for our automated approach guidance concept. If the prototype claims to support final-approach spacing (2.5 NM same-runway), the tracker output should be tested against MI ≤ 5 s, PU ≥ 99 %, RMS ≤ 200 m, zero long gaps, and the 0.5 s update-jitter band. The 3 NM terminal case needs RMS ≤ 300 m and MI ≤ 5 s; 5 NM en-route needs ≤ 500 m and ≤ 8 s. These can go directly on a slide ("spec → our measured value").
