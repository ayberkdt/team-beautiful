# R_eurocontrol_artas_asterix — EUROCONTROL ARTAS product page + ASTERIX page + "About the status of the Categories" list

## Citation
1. EUROCONTROL, "ARTAS — Air traffic management surveillance tracker and server" (product web page). https://www.eurocontrol.int/product/artas. The page mentions release 9.1.1; no page date was visible in the extracted text.
2. EUROCONTROL, "ASTERIX — All-purpose structured EUROCONTROL surveillance information exchange" (web page). https://www.eurocontrol.int/asterix
3. EUROCONTROL ASTERIX Maintenance Group, *About the status of the Categories*, dated 22/10/2025, 8-page PDF. https://www.eurocontrol.int/archive_download/all/node/11440 (linked from the ASTERIX page as "List of ASTERIX categories and their statuses", 22 October 2025).
Three EUROCONTROL web items are grouped here because they form one topic (SDPS plus its data format). Date read: 2026-11-04. Source class: PRIMARY (EUROCONTROL's own pages and documents).
Labels: [D-ag] read this session; [A] not verified.

## ARTAS (product page) [D-ag]
- ARTAS is a "European-wide distributed Surveillance Data Processing System (SDPS)". It processes "classical radar, Mode-S, WAM and ADS" and uses "proven multi-sensor tracking technology" with PSR, SSR, Mode S, WAM and ADS-B (terrestrial and space-based).
- It is distributed: identical units coordinate as one region-wide system. Sensors feed it over a Regional Surveillance WAN, and it serves tracks through SDDS to ATC units, safety nets, military units and flow management.
- Supports **5 NM** separation throughout the covered area. **3 NM** "may also be applied, following an in-depth operational evaluation" locally.
- Tracker Tuning Areas let parameters be set per volume (TMA, Inhibit Code Change Areas, en route, Ground Movement Areas).
- Software: about 2.1 million lines (ADA, C, Java, Python, Bash). Components (CSCI): Router-Bridge (RBR), Tracker (TRK), Server (SRV), System Manager (MMS). It runs on 1 node, or 2 nodes for full redundancy.
- Capacity: nominal 30 sensors and 4,096 system tracks. Recent releases go up to 255 sensors and 32,000 tracks ("subject to validation").
- Tracks "close to 90% of European daily flights at 43 Air Traffic Control Centres", with about 100 units deployed. It is also used in Iceland, South Africa, UAE, Qatar, Indonesia, PNG and the USA.
- ED-153 SWAL 3 compliant, ISO 9001. EC Declaration of Suitability for Use since 2012.
- **Tracker algorithm type: NOT stated on this page.** The page does not name IMM. A claim that ARTAS uses an IMM tracker must come from another source (e.g. the ARTAS tracker documentation or Blom et al.); the agent did not verify it [A, unverified].

## ASTERIX (web page) [D-ag]
- ASTERIX is a "down to the bit" data format for surveillance data exchange, designed for low bandwidth. Part 1 (EUROCONTROL Specification for Surveillance Data Exchange Part I) is Edition 3.1, 23 November 2021.
- Category ranges: 000–127 standard civil/military (allocated by the AMG); 128–240 special (national); 241–255 non-standard.
- The SAC (System Area Code) allotment table lists e.g. Turkey = 86 hex (binary 1000 0110); Turkey (MIL) = 85 and 87.

## Category list, status 22/10/2025 [D-ag]
| CAT | Description | Latest edition | Source / remark |
|---|---|---|---|
| 001 | Monoradar target reports (PSR, SSR, MSSR, excluding Mode S) | Ed 1.4, 18 Aug 2022 | **Replaced by CAT048** |
| 002 | Monoradar service messages (status, North marker, sector crossing) | Ed 1.2, 15 Mar 2024 | **Replaced by CAT034** |
| 004 | Safety nets messages | Ed 1.13, 04 Jun 2024 | Safety nets server (STCA, MSAW …) |
| 010 | Monosensor surface movement data | Ed 1.1, 01 Mar 2007 | SMR |
| 011 | A-SMGCS data | Ed 1.3, 11 May 2020 | |
| 012/013/014 | Monoradar target / service / weather reports | Reserved for **PAR** | |
| 015 / 016 | INCS target / configuration reports | 1.2 (2024) / 1.0 (2019) | Non-cooperative surveillance |
| 019 / 020 | MLT system status / MLT messages | 1.3 (2010) / 1.11, 02 Jul 2025 | Multilateration ground station |
| 021 | ADS-B target reports | 2.7, 02 Jul 2025 | ADS-B ground station |
| 023 | CNS/ATM ground station service messages | 1.3 (2021) | |
| 034 | Transmission of monoradar service messages | Ed 1.29, 15 Mar 2021 | PSR/SSR/MSSR/Mode S |
| 048 | Monoradar target reports | Ed 1.32, 01 Jul 2024 | PSR/SSR/MSSR/Mode S |
| 053 | ADS-B target reports (next version of 021) | under development | |
| 062 | System track data | Ed 1.21, 05 Jun 2025 | SDPS (e.g. ARTAS output) |
| 063 | Sensor status messages | Ed 1.7, 05 Jun 2025 | SDPS |
| 065 | SDPS service status | Ed 1.6, 21 Mar 2023 | SDPS |
| 094 | System track data (next version of 062) | under development | |
| 030 / 031 | Exchange of air situation pictures / sensor info | obsolete ARTAS categories, removed | |
| 129 | UAS identification reports | 1.2 (2019) | |
| 240 | Radar video transmission | 1.3 (2015) | Rotating radar |

## Relevance to us [Y]
If our prototype ingests or outputs surveillance data, the sponsor will expect ASTERIX. Use CAT048 for radar plots, CAT021 for ADS-B, CAT020 for MLAT, CAT062 for fused system tracks and CAT034 for radar service and North markers. CAT001/002 are legacy. The ARTAS facts let us position our tracker: we are not replacing ARTAS; our piece would sit downstream of a CAT062 feed for approach guidance. Open item: a citable source for ARTAS's tracker type (IMM).
