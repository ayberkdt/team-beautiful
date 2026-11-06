# Standards, phraseology and data formats — what we can quote, and from which note

Every row cites a research note in `03_Advionics/research/` (tags as in doc 24: [D] read by the session from the
source, [D-ag] read by a research agent, [A] search snippet only). **Gaps** are marked; do not quote a gap as fact.
Compiled 5 Nov 2026 from the notes only — nothing here was re-read from the primary source today.

## 1. Lost communication (the "iletişim kesilirse" branch)

| Item | Value | Note file | Tag |
|---|---|---|---|
| EU radio-failure rule | SERA.14083 (Reg. (EU) 2024/404), applicable 1 May 2025 | C_EASA_SERA_EAR; C_BCAA_ASIL_2025_02 | D-ag |
| IFR hold of last speed/level | **20 min** after a missed required report, or after setting 7600 / ADS-B emergency where a surveillance service is provided | C_EASA_SERA_EAR (c)(4)(i) | D-ag |
| Descent / landing | descend at last acknowledged EAT (else ETA); land within **30 min** after the later of ETA/EAT | C_EASA_SERA_EAR (c)(4)(iv),(vi) | D-ag |
| Codes | **7600** RCF; **7601** IFR in VMC, PIC decides to continue in VMC → nearest suitable aerodrome (EU only; CH: 7600 only) | C_EASA_SERA_EAR (c)(2),(c)(6); C_OpsGroup_SERA_2025 | D-ag |
| Other codes | 7700 emergency, 7500 unlawful interference, 2000 / 7000 | C_EASA_SERA_EAR (SERA.13005) | D-ag |
| ATC side | receiver check by IDENT / code change / manoeuvre; no blind *clearances* unless the originator asks | C_EASA_SERA_EAR (b)(1),(b)(3) + AMC1 | D-ag |
| Old ICAO/EUR text | **7 min** (still in many AIPs) | C_AIP_Georgia_ENR18 §3.3 b | D-ag |
| US | 14 CFR 91.185: highest of assigned / minimum IFR / expected altitude; EFC/ETA; no fixed hold | C_14CFR_91_185 | D-ag |
| Guard frequency | 121.5 MHz | C_EASA_SERA_EAR (SERA.14080) | D-ag |
| Code in software | `aerokit.atc.lostcomm.RULE_SETS` (EU / ICAO-EUR legacy / US) | — | — |
| **Gap** | ICAO Annex 2 3.6.5.2 and PANS-ATM Doc 4444 ch. 15.3 not read (paywalled); FAA AIM 6-4-1 / JO 7110.65 not readable (403) | C_00_summary; C_A_unverified_snippets | — |

## 2. Voice: phraseology and read-back

| Item | Value | Note file | Tag |
|---|---|---|---|
| Read-back items | route, runway, altimeter, SSR code, frequency, level, heading, speed, transition level; controller hearback (e)(3); CPDLC exempt (e)(4) | C_EASA_SERA_EAR (SERA.8015(e)) | D-ag |
| Voice watch with CPDLC | continuous voice watch "shall remain in effect when CPDLC has been established" | C_EASA_SERA_EAR (SERA.8035) | D-ag |
| Number pronunciation | 3 TREE, 5 FIFE, 9 NIN-er, DAY-SEE-MAL… | C_EASA_SERA_EAR (SERA.14040) | D-ag |
| 8.33 channel spoken | 118.005 = "ONE ONE EIGHT DECIMAL ZERO ZERO FIVE" | C_EASA_SERA_EAR (SERA.14035) | D-ag |
| ROGER / callsign rules | ROGER never answers a read-back request; Type (c) callsigns not abbreviated | C_EASA_SERA_EAR (SERA.14045/14050) | D-ag |
| No transmissions to aircraft on short final / take-off / landing roll (except safety) | SERA.14055 | C_00_summary item 9 | D-ag |
| Readback error base rates | < 1 % (1–5 elements), 1.4 / 1.3 % (6 / 7); controllers missed 7 of 19 (tower, Cardosi 1994); 8 % miscommunication for 5+ element clearances (en route, 1993) | C_Cardosi_1994_FAA_RD94_15; A_Cardosi1993_FAA_enroute_readback | D-ag |
| **Gap** | ICAO Doc 4444 ch. 12 / Doc 9432 phraseology **not read**; all phraseology above is the EU SERA text | C_00_summary | — |

## 3. VHF voice and data link radio

| Item | Value | Note file | Tag |
|---|---|---|---|
| Band / channels | 117.975–137 MHz (EU scope); 118.000–136.975 MHz, 760 × 25 kHz channels | C_EU_2023_1770; C_ETSI_EN300676_1; C_ETSI_EN301841_1 | D-ag |
| Emission / audio | 6K80A3EJN (25 kHz) 300–3400 Hz; 5K00A3EJN (8.33 kHz) 350–2500 Hz; AM depth 85–95 % | C_ETSI_EN300676_1 | D-ag |
| Receiver sensitivity | −101 dBm (12 dB SINAD, ground) | C_ETSI_EN300676_1 | D-ag |
| 8.33 kHz naming | 118.005 / .010 / .015 operate at 118.0000 / .0083 / .0167 MHz (checked only 118.000–118.105) | doc 24 §6 (Icom IC-A24 table) | D |
| 8.33 mandate | new radios from 17 Nov 2013; all radios by 31 Dec 2017 (1079/2012, now repealed → 2023/1770) | C_EU_1079_2012; C_EU_2023_1770 | D-ag |
| Data-link VHF segment | 136.500–137.000 MHz, no voice | C_EUROCONTROL_Leaflet_Datalink_VHF | D-ag |
| VDL Mode 2 | D8PSK 10 500 symbol/s = 31.5 kbit/s; Rx −98 dBm | C_ETSI_EN301841_1 | D-ag |
| Simultaneous transmissions | stronger AM carrier masks the weaker, little or no detection | C_SKYbrary_USiT | D-ag |
| **Gap** | Annex 10 Vol III/V voice-quality figures, ED-120 / RCP latencies not from a primary source | C_A_unverified_snippets #4 | — |

## 4. CPDLC message sets (Europe: ATN B1 over VDL Mode 2)

| Item | Value | Note file | Tag |
|---|---|---|---|
| Uplinks (selection) | UM0 UNABLE, UM1 STANDBY, UM19 maintain, **UM20 CLIMB TO**, UM23 DESCEND TO, UM74 DIRECT TO, UM117 CONTACT, UM123 SQUAWK, **UM157 CHECK STUCK MICROPHONE**, UM183 free text, **UM190 FLY HEADING**, UM227 LACK | C_EASA_CS_ACNS_DLS; C_EUROCONTROL_WikiLink_MessageSets | D-ag |
| Downlinks (selection) | DM0 WILCO, DM1 UNABLE, DM2 STANDBY, DM3 ROGER, DM6 request level, DM62 ERROR, DM100 LACK | C_EASA_CS_ACNS_DLS | D-ag |
| **No approach clearances** in ATN B1 (no "cleared ILS approach") | — | C_EASA_CS_ACNS_DLS | D-ag |
| Timers / practice | ground response timer 120 s; time-critical stays on voice; Airbus: re-confirm by voice if > 2 min old | C_EUROCONTROL_CPDLC_RecPractices_2026 | D-ag |
| Services | DLIC, ACM, ACL, AMC (microphone check); mandate above FL 285 | C_EU_29_2009; C_EU_2023_1770 | D-ag |
| In code | `aerokit.atc.datalink` maps UM20 / 74 / 117 / 157 / 190 only | — | — |

## 5. SSR / Mode S / ADS-B signals

| Item | Value | Note file | Tag |
|---|---|---|---|
| Frequencies | 1030 MHz interrogation / 1090 MHz reply | R_ssr_wiki; R_1090_riddle | D-ag |
| Mode A / C | P1–P3 8 / 21 µs; P2 (SLS) 2 µs after P1; reply F1–F2 20.3 µs, 1.45 µs grid, 0.45 µs pulses, SPI 4.35 µs after F2; 4096 codes; Mode C 100 ft | R_00_summary (R_ssr_wiki, R_atcrbs_wiki) | D-ag |
| Mode S frame | preamble 8 µs, 1 µs/bit; 56 or 112 bits; CRC-24 generator 0x1FFF409 | R_1090_riddle | D-ag |
| Downlink formats | DF0 short ACAS (56), **DF4** altitude (56), **DF5** identity (56), **DF11** all-call (56), DF16 long ACAS, **DF17** extended squitter (transponder), **DF18** ES non-transponder / TIS-B, DF19 military ES, **DF20/21** Comm-B altitude / identity, DF24 Comm-D ELM | R_1090_riddle Table 1.1 | D-ag |
| Parity | PI (plain CRC) for ES; AP = CRC XOR address for DF4/5/20/21; DF11 PI = CRC XOR II/SI | R_1090_riddle | D-ag |
| ADS-B rates / CPR | airborne position and velocity 2 Hz; CPR NZ = 15; local reference radius 180 NM (airborne) / 45 NM (surface); global pair window 10 s | R_1090_riddle | D-ag |
| Test vectors | T1–T16 + Gillham G1–G44 (all reproduced by `atc.modes`, 20/20 in report §1) | R_00_summary | D / D-ag |
| Mode S acquisition | all-call lockout 18 s; II 0–15, SI 1–63 | R_eurocontrol_modeS_IC | D-ag |
| US ADS-B Out minimum | NACp < 0.05 NM, NIC < 0.2 NM, SIL ≤ 1e-7; latency ≤ 2.0 s total / ≤ 0.6 s uncompensated | R_14cfr_91_227_adsb | D-ag |
| **Gap** | ICAO Annex 10 Vol IV, ED-73 / ED-117A / ED-129 / ED-142 (paywalled); NIC/NACp/SIL not decoded in code; **Mode 5 (military IFF) format not read** — only that RES and L-IESA support Mode 5 L1/L2 (S_intersoft_res_page, S_intersoft_liesa_leaflet) | R_00_summary; S_00_summary | — |

## 6. ASTERIX categories (EUROCONTROL list, status 22 Oct 2025)

| CAT | Content | Note file | Tag |
|---|---|---|---|
| 001 / 002 | legacy monoradar targets / service — **replaced by 048 / 034** | R_eurocontrol_artas_asterix | D-ag |
| **012 / 013 / 014** | **reserved for PAR** (target / service / weather reports) | R_eurocontrol_artas_asterix | D-ag |
| 019 / 020 | MLAT system status / MLAT target reports | R_eurocontrol_artas_asterix | D-ag |
| **021** | ADS-B target reports (ed. 2.7, 2 Jul 2025; implemented in `atc.asterix`) | R_eurocontrol_artas_asterix; doc 24 §13 | D-ag |
| 034 | monoradar service messages (North marker, sector) | R_eurocontrol_artas_asterix | D-ag |
| **048** | monoradar target reports PSR/SSR/Mode S (ed. 1.32; our encoder from Ed. 1.15, identical items) | R_eurocontrol_artas_asterix; doc 24 §5 | D / D-ag |
| 062 / 063 / 065 | SDPS system tracks (ARTAS output) / sensor status / SDPS status | R_eurocontrol_artas_asterix | D-ag |
| 004 | safety nets (STCA, MSAW) | R_eurocontrol_artas_asterix | D-ag |
| 008 / 240 / 253 | weather / radar video / command and control (NGSP outputs; Cat253 transponder control in IFF integration) | S_intersoft_ngsp_intro; S_intersoft_iff_integrations | D-ag |
| Sponsor's RASS reads | CAT001, 002, 008, 010, 011, 017–021, 030, 031, 034, 048, 062, 063, 065 | S_intersoft_rass_catalogue | D-ag |

## 7. Surveillance and approach performance figures

| Item | Value | Note file | Tag |
|---|---|---|---|
| EUROCONTROL 1997 (recommended) | SSR Pd > 97 %, Mode A > 98 %, Mode C > 96 %, false Mode A < 0.1 %; PSR Pd > 90 %, < 20 false reports/scan; σ SSR 70 m / 0.08°, PSR 120 m / 0.15° | R_eurocontrol_radar_std_1997 | D |
| ESASSP (2024) | 3 NM sep.: update ≤ 5 s, RMS ≤ 300 m, ≥ 97 %; 2.5 NM final: ≤ 5 s, ≤ 200 m, ≥ 99 % | R_esassp | D-ag |
| PAR (Annex 10 via ENRI) | ≥ 9 NM, 20° × 7°, el 6 m / 0.4 % R + 10 % offset, az 9 m / 0.6 % R + 10 %, range 30 m / 3 %, update ≤ 1 s | R_par_enri_soumu | D-ag |
| PAR talk-down timing | transmissions ~5 s; lost-comm action after ~5 s on PAR final | doc 24 §6 | **A only** |
| ILS | LOC 108.10–111.95 MHz, GS 328.6–335.4 MHz, 90/150 Hz tones, GS 3° | R_ils_wiki; R_faa_aim_ch1 | D-ag |
| LPV-200 | HAL 40 m, VAL 35 m | R_faa_aim_ch1 | D-ag |
| WAM / ADS-B / Mode S radar on final (one measured campaign) | 6–7 m / ~20 m / ~200 m | R_icao_suricg7_ip14_wam | D-ag |
| **Gap** | ICAO Doc 8071 (flight inspection tolerances) and Annex 10 Vol I tolerances **not read**; GBAS alert limits not found | R_00_summary; R_mentor_roleplay | — |
