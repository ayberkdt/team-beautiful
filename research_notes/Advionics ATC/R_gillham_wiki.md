# R_gillham_wiki — Wikipedia, "Gillham code"

## Citation
Wikipedia contributors, "Gillham code", English Wikipedia. URL: https://en.wikipedia.org/wiki/Gillham_code (raw wikitext read).
Date read: 2026-11-04. Source class: SECONDARY. The "Decoding" section carries a **"Disputed section" (August 2022)** banner. Its references include AirSport Avionics (Phillips 1998), K. Stewart 2010 (CCS forum), and US patent 3805041.
Labels: [D-ag] = read in the article this session; [C-ag] = agent computation (not a source).

## Facts

### Coding [D-ag]
- Altitude travels as 11 parallel lines, `D2–D4–A1–A2–A4–B1–B2–B4–C1–C2–C4`. D1 exists but "is unused and always set to 0".
- Up to 30,700 ft no D bits are needed (9-wire). Up to 62,700 ft needs D4 (10-wire). Up to 126,700 ft needs D4 and D2 (11-wire).

### Decoding [D-ag] (disputed section)
- D2 (msb) to B4 (lsb) form an 8-bit reflected binary (Gray) code counting 500 ft steps "above a base altitude of −1000±250 ft".
- C1 C2 C4 form a 5-state code for the 100 ft offset. If the 500 ft code has **even** parity, codes `001, 011, 010, 110, 100` mean −200, −100, 0, +100, +200 ft. If it has **odd** parity, the assignment is reversed. Codes `000, 101, 111` are not used.

### Table (test vectors). Bit string order [D1 D2 D4 – A1 A2 A4 – B1 B2 B4 – C1 C2 C4], squawk-style octal [ABCD], height [ft]. Copied verbatim [D-ag]:
| Gillham binary | Octal ABCD | ft |
|---|---|---|
| `000 000 000 001` | 0040 | −1200 |
| `000 000 000 011` | 0060 | −1100 |
| `000 000 000 010` | 0020 | −1000 |
| `000 000 000 110` | 0030 | −900 |
| `000 000 000 100` | 0010 | −800 |
| `000 000 001 100` | 0410 | −700 |
| `000 000 001 110` | 0430 | −600 |
| `000 000 001 010` | 0420 | −500 |
| `000 000 001 011` | 0460 | −400 |
| `000 000 001 001` | 0440 | −300 |
| `000 000 011 001` | 0640 | −200 |
| `000 000 011 011` | 0660 | −100 |
| `000 000 011 010` | 0620 | 0 |
| `000 000 011 110` | 0630 | 100 |
| `000 000 011 100` | 0610 | 200 |
| `000 000 010 100` | 0210 | 300 |
| `000 000 010 110` | 0230 | 400 |
| `000 000 010 010` | 0220 | 500 |
| `000 000 010 011` | 0260 | 600 |
| `000 000 010 001` | 0240 | 700 |
| `000 000 110 001` | 0340 | 800 |
| `000 000 110 011` | 0360 | 900 |
| `000 000 110 010` | 0320 | 1000 |
| `000 000 110 110` | 0330 | 1100 |
| `000 000 110 100` | 0310 | 1200 |
| `000 000 111 100` | 0710 | 1300 |
| `000 000 111 110` | 0730 | 1400 |
| `000 000 111 010` | 0720 | 1500 |
| `000 000 111 011` | 0760 | 1600 |
| `000 000 111 001` | 0740 | 1700 |
| `000 000 101 001` | 0540 | 1800 |
| `000 000 101 011` | 0560 | 1900 |
| `000 000 101 010` | 0520 | 2000 |
| `000 000 101 110` | 0530 | 2100 |
| `000 000 101 100` | 0510 | 2200 |
| `000 000 100 100` | 0110 | 2300 |
| `000 000 100 110` | 0130 | 2400 |
| `000 000 100 010` | 0120 | 2500 |
| `000 000 100 011` | 0160 | 2600 |
| `000 000 100 001` | 0140 | 2700 |
| `010 000 000 110` | 0032 | 126400 |
| `010 000 000 010` | 0022 | 126500 |
| `010 000 000 011` | 0062 | 126600 |
| `010 000 000 001` | 0042 | 126700 |

Caution [C-ag, own reading of the table]: the octal column orders digits A B C D, and each digit is weighted A4·4 + A2·2 + A1. The binary column orders groups D, A, B, C, and within each group lists bits LSB-first (x1 x2 x4). Worked example for the 0 ft row: binary `000 000 011 010` gives B1 B2 B4 = 0 1 1, so B = 6, and C1 C2 C4 = 0 1 0, so C = 2. That makes octal 0620 ✓.

### Cross-check [C-ag]
A Python check (2026-11-04) ran the 1090 Riddle algorithm (R_1090_riddle.md §9: N500 = Gray⁻¹(D2 D4 A1 A2 A4 B1 B2 B4), N100 = Gray⁻¹(C1 C2 C4); N100 ∈ {0,5,6} invalid; 7→5; odd N500 → N100 = 6 − N100; h = 500·N500 + 100·N100 − 1300) on 12 rows: −1200, −1100, −1000, −900, −800, −700, 0, 1200, 1300, 2700, 126400, 126700. **All 12 matched.** The two sources agree.

## Relevance to us [Y]
This table is the Mode C (Q=0) Gillham test set that the 1090 Riddle lacks (its DF4 example has Q=1). The tests should map pulse/bit names to the decoder explicitly, because the bit order differs between the reply train (C1 A1 C2 A2 C4 A4 X B1 D1 B2 D2 B4 D4) and this table (D1 D2 D4 A1 A2 A4 B1 B2 B4 C1 C2 C4).
