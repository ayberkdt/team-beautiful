# R_1090_riddle — Junzi Sun, *The 1090 Megahertz Riddle* (2nd ed.)

## Citation
Sun, J. (2021). *The 1090 Megahertz Riddle: A Guide to Decoding Mode S and ADS-B Signals*, 2nd edition. TU Delft OPEN Publishing. DOI 10.34641/mg.11, ISBN 978-94-6366-402-8.
Online HTML edition: https://mode-s.org/1090mhz/ (chapter pages under `content/...`, listed per section below).
Date read: 2026-11-04. Read method: raw HTML fetched with curl, tags stripped locally, text read in full by the agent (no LLM summariser in between). Hex strings below were copied from that plain text.

Labels: [D-ag] = read directly by the agent in the source this session. [A] = snippet / secondary only. [C-ag] = computed by the agent this session with a small Python script (CRC-24, CPR, Gillham), used only to cross-check the book; it is NOT a source.

---

## 1. Introduction chapter — `content/introduction.html` [D-ag]
- SSR interrogates on 1030 MHz; transponder replies on 1090 MHz.
- Mode A/C interrogation pulses "about 0.8 μs wide". P1–P3 spacing "8 μs and 21 μs, respectively for Mode A and C".
- P2 comes from the omnidirectional antenna right after P1, for side-lobe suppression: if P2 is stronger than P1 the transponder treats the interrogation as a side-lobe one and ignores it.
- Mode A/C reply: framing pulses F1 and F2 "separated by 20.3 μs"; 13 pulse positions of 0.45 μs; the centre (X) position is always absent; the other 12 carry the bits. SPI may follow F2 after two empty positions.
  - Note: the book says the pulses "are separated by gaps of 1 μs". The usual statement (ICAO Annex 10 Vol IV, Wikipedia) is 1.45 μs pulse spacing, centre to centre (0.45 μs pulse + 1 μs gap = 1.45 μs). The two agree; they describe gap and pitch.
- The reply does not say whether it is Mode A or C. The radar knows from which interrogation it sent.
- Synchronous garbling: replies from aircraft in the same beam direction overlap. FRUIT = "False Replies Unsynchronized In Time" (replies to other radars).
- Mode A: 4 octal digits, so 4096 (8^4) codes. Mode S: 24-bit address, so 16,777,216 (2^24) addresses.
- Mode S reply: 8 μs preamble, then a 56 or 112 μs data block (1 bit per μs), PPM. Preamble bit pattern `1010000101000000`. Uplink uses DPSK; downlink uses PPM.
- Mode A/C/S all-call: P1–P3 are 8 or 21 μs apart, with an extra P4 of 1.6 μs. The book says this all-call is being phased out in favour of the Mode S-only all-call (UF11).
- PSR (introduction, a general statement): transmits "a one-microsecond pulse for every one millisecond" (the book says "commonly").
- Table 1.1, Mode S UF/DF formats with bit lengths: 0 (56, short ACAS), 4 (56, surveillance altitude), 5 (56, surveillance identity), 11 (56, all-call), 16 (112, long ACAS), 17 (112, extended squitter), 18 (112, ES/non-transponder), 19 (112, military ES), 20 (112, Comm-B altitude reply), 21 (112, Comm-B identity reply), 24 (112, Comm-D ELM). DF24 is identified by its first 2 bits only (`11`).
- ELS = BDS 1,0, 1,7, 2,0 and 3,0. EHS = BDS 4,0, 5,0 and 6,0.

## 2. ADS-B basics — `content/ads-b/1-basics.html` [D-ag]
- Frame 112 bits: DF(5) CA(3) ICAO(24) ME(56) PI(24). TC = ME bits 1–5 (message bits 33–37).
- DF17 comes from a Mode S transponder. DF18 comes from non-transponder ADS-B or TIS-B equipment (equipment that cannot be interrogated).
- CA: 0 = Level 1; 1–3 reserved; 4 = Level 2+ on ground; 5 = Level 2+ airborne; 6 = Level 2+ either; 7 = DR≠0 or FS 2,3,4,5.
- Table 1.3, Type Codes: 1–4 identification; 5–8 surface position; 9–18 airborne position (baro altitude); 19 airborne velocities; 20–22 airborne position (GNSS height); 23–27 reserved; 28 aircraft status; 29 target state and status; 31 operational status.
- Table 1.4, ADS-B v2 transmission rates (airborne): identification 0.2 Hz; airborne position 2 Hz; airborne velocity 2 Hz; target state (TC29) 0.8 Hz; operational status 0.2 Hz, or 1.25 Hz after a change. Surface position: 2 Hz when moving, 0.2 Hz when still.
- Versions: v0 = DO-260; v1 ≈ 2008 (DO-260A); v2 ≈ 2012 (DO-260B). The version number sits in TC31 ME bits 41–43.
- Example: `8D4840D6202CC371C32CE0576098` gives DF 17, CA 5, ICAO `4840D6`, TC 4. The book says this ICAO belongs to a Fokker 70, PH-KZD.

## 3. Aircraft identification — `content/ads-b/2-identification.html` [D-ag]
- ME layout: TC(5) CA(3) C1..C8 (6 bits each).
- Character map, verbatim: `#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### ###############0123456789######` (A–Z = 1–26, space = 32, 0–9 = 48–57; this is the lower 6 bits of ASCII).
- Wake category: TC4/CA1 Light (<7000 kg); TC4/CA2 Medium 1 (7000–34000 kg); TC4/CA3 Medium 2 (34000–136000 kg); TC4/CA5 Heavy (>136000 kg); TC4/CA7 rotorcraft; TC3/CA6 UAV.

## 4. Airborne position + CPR — `content/ads-b/3-airborne-position.html` [D-ag]
- ME layout: TC(5) SS(2) SAF(1) ALT(12) T(1) F(1) LAT-CPR(17) LON-CPR(17). F = message bit 54: 0 = even, 1 = odd.
- N_Z = 15 ("In Mode S, N_Z is defined to be 15").
- NL(lat) = floor{ 2π / arccos[ 1 − (1 − cos(π/(2 N_Z))) / cos²(π/180 · lat) ] }. Special cases: lat=0 gives NL=59; |lat|=87 gives NL=2; |lat|>87 gives NL=1.
- dLat_even = 360°/(4 N_Z) = 6°; dLat_odd = 360°/(4 N_Z − 1) = 360/59°.
- Global decoding: j = floor(59·latcpr_even − 60·latcpr_odd + ½); lat_even = dLat_even(mod(j,60) + latcpr_even); lat_odd = dLat_odd(mod(j,59) + latcpr_odd). If lat ≥ 270, subtract 360. If NL(lat_even) ≠ NL(lat_odd), stop and wait for a new pair. Use the more recent frame's latitude.
- Longitude: m = floor(loncpr_even·(NL−1) − loncpr_odd·NL + ½); n_even = max(NL,1); n_odd = max(NL−1,1); lon = (360/n)(mod(m,n) + loncpr). If lon ≥ 180, subtract 360.
- Local decoding: the reference must be within 180 NM. dLat = 360/(4N_Z − i) with i = 0 even, 1 odd. j = floor(lat_ref/dLat) + floor(mod(lat_ref,dLat)/dLat − latcpr + ½); lat = dLat(j + latcpr). dLon = 360/max(NL(lat) − i, 1); m = floor(lon_ref/dLon) + floor(mod(lon_ref,dLon)/dLon − loncpr + ½); lon = dLon(m + loncpr).
- 10 s rule: the example pair is "received within 10 seconds". The footnote treats a position decoded within 10 seconds as a valid reference.
- Altitude (TC 9–18): the Q bit is bit 8 of the 12-bit ALT field. Q=1 gives h = 25N − 1000 ft. Q=0 means 100 ft Gillham. All zeros means no altitude. TC 20–22 gives GNSS height in metres.
- Plausibility check: the decoded position must lie within receiver range, or several pairs must agree with each other.

## 5. Surface position — `content/ads-b/4-surface-position.html` [D-ag]
- dLat is 90°/(4N_Z) or 90°/(4N_Z − 1), and dLon is 90°/n (four times smaller than airborne). The original encoding is 19 bits, of which 17 are sent, so a reference position is needed. Local decoding needs a reference within 45 NM.
- Movement (ground speed) quantisation: 1 = stopped (<0.125 kt); 2–8 in 0.125 kt steps; 9–12 in 0.25 kt; 13–38 in 0.5 kt; 39–93 in 1 kt (15–70 kt); 94–108 in 2 kt; 109–123 in 5 kt; 124 means ≥175 kt.
- Track = 360·n/128 degrees, valid when S = 1.

## 6. Airborne velocity — `content/ads-b/5-airborne-velocity.html` [D-ag]
- TC 19. ST 1/2 = ground speed (ST2 has 4 kt resolution, supersonic). ST 3/4 = airspeed plus magnetic heading.
- VR: VS = ±64·(VR − 1) ft/min. Svr 0 = up, 1 = down. VrSrc 0 = GNSS, 1 = baro.
- GNSS–baro difference: Δh = s(n − 1)·25 ft.

## 7. Uncertainty — `content/ads-b/7-uncertainty.html` [D-ag]
- NACp table (EPU / VEPU, 95%): 11 <3 m / <4 m; 10 <10 m / <15 m; 9 <30 m / <45 m; 8 <0.05 NM (93 m); 7 <0.1 NM (185 m); 6 <0.3 NM (556 m); 5 <0.5 NM (926 m); 4 <1.0 NM (1852 m); 3 <2 NM; 2 <4 NM; 1 <10 NM; 0 >10 NM or unknown. NACp sits in TC31, message bits 77–80.
- EPU ≈ Rc/2.5 for NACp ≥ 9, and ≈ Rc/2.0 for NACp < 9.
- NIC v1/v2: with TC 9 → 11 (<7.5 m), TC 10 → 10 (<25 m), TC 11 → 9/8 (<75 m / <0.1 NM), TC 12 → 7 (<0.2 NM), TC 13 → 6 (<0.3, 0.5 or 0.6 NM depending on the supplement bits), TC 14 → 5 (<1.0 NM), TC 15 → 4 (<2 NM), TC 16 → 3/2 (<4 / <8 NM), TC 17 → 1 (<20 NM), TC 18 → 0. Caution: the HTML table uses row-spans that flattened during extraction. Supplement-bit details should be re-checked in the PDF.
- SIL: 1 <1e-3; 2 <1e-5; 3 <1e-7 (P-RC).
- NACv: 1 <10 m/s; 2 <3 m/s; 3 <1 m/s; 4 <0.3 m/s (horizontal).

## 8. Error control — `content/ads-b/8-error-control.html` [D-ag]
- G(x) = x^24+x^23+x^22+x^21+x^20+x^19+x^18+x^17+x^16+x^15+x^14+x^13+x^12+x^10+x^3+1, binary `1111111111111010000001001`, hex "1FFF409". The task's 0xFFF409 is the same polynomial with the implicit x^24 term dropped.
- Receiver check: run the CRC over all 112 bits; the remainder must be 0.

## 9. Mode S basics, all-call, surveillance — `content/mode-s/1-basics.html`, `2-allcall.html`, `3-surveillance.html` [D-ag]
- Short = 56 bits, long = 112 bits. The final 24 bits are parity: plain CRC for ES (PI), Address Parity (AP = CRC XOR ICAO) for DF 4/5/20/21, or Data Parity (overlaid with the BDS).
- DF11 all-call: DF(5) CA(3) AA(24) PI(24). PI = CRC XOR interrogator identifier (II/SI). II = 0 means an acquisition squitter.
- DF4/5: DF(5) FS(3) DR(5) UM(6) AC or ID(13, bits 20–32) AP(24).
- FS: 000 airborne; 001 on ground; 010 alert, airborne; 011 alert, ground; 100 alert + SPI; 101 SPI, no alert.
- AC13: M = bit 7 (message bit 28) and Q = bit 9 (message bit 30). All zeros = invalid. M=1 = metres. M=0,Q=1 gives 25N − 1000 ft over the 11 remaining bits. M=0,Q=0 = Gillham, 100 ft.
- Gillham procedure (the book cites DO-260 and ICAO Annex 10 Vol IV): reorder the bits to D2 D4 A1 A2 A4 B1 B2 B4 C1 C2 C4. The first 8 bits are a Gray-coded 500 ft count N500; the last 3 are the 100 ft count N100. N100 ∈ {0,5,6} is invalid; 7 maps to 5; if N500 is odd, N100 becomes 6 − N100. Then **h = 500·N500 + 100·N100 − 1300 ft**.
- ID13 bit order: `C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4`. Each squawk digit is A4A2A1 B4B2B1 C4C2C1 D4D2D1, read as octal.
- In the AC13 Gillham field the Q position holds D1 (the AC table header shows "0 B1 0" at the M and Q slots).

---

## TEST VECTORS (copied from the book text; character-exact)

| # | Page | Message (hex) | Expected (book) | [C-ag] cross-check |
|---|---|---|---|---|
| T1 | ads-b/1-basics, ads-b/2-identification | `8D4840D6202CC371C32CE0576098` | DF=17, CA=5, ICAO=`4840D6`, TC=4, CA(category)=0, callsign `KLM1023_` (trailing space) | CRC=0; callsign "KLM1023 " ✓ |
| T2 | ads-b/3-airborne-position (global) | even (most recent) `8D40621D58C382D690C8AC2863A7`, t0=1457996402; odd `8D40621D58C386435CC412692AD6`, t1=1457996400 | ICAO `40621D`; latcpr_even=93000, loncpr_even=51372, latcpr_odd=74158, loncpr_odd=50194 (/2^17); j=8; lat_even=52.25720214843750; lat_odd=52.26578017412606; NL=36 for both; m=0; n=36; lon=3.91937255859375; pyModeS `(52.2572, 3.91937)` | all values reproduced exactly ✓ |
| T3 | ads-b/3-airborne-position (local) | `8D40621D58C382D690C8AC2863A7`, ref (52.258, 3.918) | dLat=6, j=8, lat=52.2572021484375; dLon=10, m=0, lon=3.91937255859375 | ✓ (same frame as T2) |
| T4 | ads-b/3-airborne-position (altitude) | `8D40621D58C382D690C8AC2863A7` | ALT bits `110000111000`, Q=1, N=1560, altitude **38000 ft** | ALT field = 3128 decimal ✓ |
| T5 | ads-b/5-airborne-velocity (Msg A, ST1) | `8D485020994409940838175B284F` | ICAO `485020`; Sew=1, Vew=9, Sns=1, Vns=160 → Vx=−8, Vy=−159; GS 159.20 kt; track 182.88°; VR=14, Svr=1 → **−832 ft/min**; dAlt=23 → **+550 ft** (GNSS above baro); pyModeS `(159, 182.88, -832, 'GS')` | Vx=−8, Vy=−159, 159.2011, 182.8804° ✓. **Book typo:** the printed line "√((−9)²+(−160)²)" and "arctan2(−9,−160)" should read −8 and −159; the printed results 159.20 and 182.88 are correct for −8, −159 |
| T6 | ads-b/5-airborne-velocity (Msg B, ST3) | `8DA05F219B06B6AF189400CBC33F` | ICAO `A05F21`; ST=3; SH=1, HDG=694 → **243.98°**; T=1 (TAS); AS=376 → **375 kt**; VR=37, Svr=1 → **−2304 ft/min**; pyModeS `(375, 243.98, -2304, 'TAS')` | ✓. **Book typo:** the decimal row prints TC as "5"; binary 10011 = 19 (agent check gives TC=19) |
| T7 | ads-b/4-surface-position (global) | even `8C4841753AAB238733C8CD4020B1`, t0=1457996410; odd (most recent) `8C4841753A8A35323FAEBDAC702D`, t1=1457996412; ref (51.990, 4.375) | ICAO `484175`, TC=7; latcpr_even=115609, loncpr_even=116941, latcpr_odd=39199, loncpr_odd=110269; j=34; lat_even=52.323040008544920; lat_odd=52.320607072215964; NL=36; m=1; n=35; lon1=4.734734671456474; final **52.320607, 4.734735**; pyModeS `(52.32061, 4.73473)` | CRC=0 for both ✓. Note: the book text says "Since the even message is the most recent" but then uses lat_odd; the odd frame (t1) is the more recent one, so lat_odd is right |
| T8 | ads-b/4-surface-position (local) | `8C4841753A9A153237AEF0F275BE`, ref (52.320607, 4.734735) | latcpr=39195, loncpr=110320, odd; j=34; lat=52.32056051997815; dLon=90/35; m=1; lon=4.735735212053571; final **52.320561, 4.735735**; MOV=41 → **17 kt**; TRK=33 → **92.8125°**; pyModeS velocity `17 92.8 0 GS` | CRC=0 ✓. **Book inconsistency:** the pyModeS position_with_ref call uses ref (51.990, 4.375) and prints `(52.32061, 4.73473)`, which is the T7 value. Use the hand-calculated 52.320561, 4.735735 for this test |
| T9 | ads-b/8-error-control | `8D406B902015A678D4D220AA4BDA` | CRC remainder over the data `8D406B902015A678D4D220` = `AA4BDA` (binary 101010100100101111011010); full-message CRC = **0** | ✓ |
| T10 | ads-b/8-error-control | `8D4CA251204994B1C36E60A5343D` | pyModeS crc **16** (corrupted message) | 16 ✓ |
| T11 | mode-s/1-basics (ICAO recovery, AP) | `A0001838CA380031440000F24177` | payload CRC `CE2CA7`; AP `F24177`; ICAO **`3C6DD0`** | ✓ |
| T12 | mode-s/1-basics (Data Parity MA) | ICAO `DD33AA` XOR BDS 4,0 `440000` | Modified AA `9933AA` | — |
| T13 | mode-s/1-basics (two's complement) | sign 0, value `111010011` → 467; sign 1, same value → 467 − 2^9 = **−45** | — | — |
| T14 | mode-s/2-allcall (DF11) | `5D484FDEA248F5` | DF=11, CA=5, AA=**`484FDE`**, CRC/II = **22** | PI XOR CRC = 0x000016 = 22 ✓ |
| T15 | mode-s/3-surveillance (DF4 altitude) | `2000171806A983` | `pms.altcode` → **36000 ft** | AC13 = `1011100011000`, M=0, **Q=1** → 25 ft coding (N=1480, 25·1480 − 1000 = 36000) ✓. NOTE: this vector does NOT exercise Gillham; a Q=0 vector is needed from another source (see R_gillham_wiki.md) |
| T16 | mode-s/3-surveillance (DF5 identity) | `2A00516D492B80` | ID13 `1000101101101` = C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4 = 1 0 0 0 1 0 1 1 0 1 1 0 1; squawk **0356** | ✓. Note: this message's X bit is 1 |
| T17 | mode-s/6-els (BDS 2,0) | `A000083E202CC371C31DE0AA1CCF` | MB `202CC371C31DE0`, BDS 2,0, callsign **`KLM1017_`** | callsign "KLM1017 " ✓ (AP gives ICAO 484163 if error-free, [C-ag], not stated in book) |
| T18 | mode-s/6-els (BDS 1,7) | `A0000638FA81C10000000081A92F` | supported BDS: 05, 06, 07, 08, 09, 20, 40, 50, 51, 52, 60 (pyModeS list; the book's prose list omits 52) | — |

Cross-check script: inline Python run by the agent on 2026-11-04 (CRC-24 polynomial 0x1FFF409, CPR global formulas as above, NL function). Output: all ten DF17/DF18-style frames gave remainder 0 except T10 (16). T2 reproduced j=8, 52.2572021484375, 52.26578017412606, NL=36/36, m=0, 3.91937255859375. NL spot values [C-ag]: NL(0)=59, NL(30)=51, NL(45)=42, NL(60)=29, NL(80)=10.

---

## Relevance to us [Y]
This is the decoder spec and the unit-test suite for any ADS-B or Mode S part of the Automated Approach Guidance prototype. T1–T8 cover identification, CPR and velocity; T9–T11 and T14 cover CRC and address recovery; T15 and T16 cover DF4/DF5. Two gaps: a Gillham (Q=0) test vector has to come from another source, and the book's three typos/inconsistencies (T5, T6, T8) should be encoded in the tests the corrected way.
