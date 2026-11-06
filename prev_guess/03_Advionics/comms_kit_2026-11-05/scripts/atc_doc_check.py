"""Check that the computed numbers quoted in docs/24 still appear in the generated report.

    python 03_Advionics/scripts/atc_doc_check.py      # exit 1 if any quoted value is missing from outputs/report.md

Run after every `python 03_Advionics/scripts/atc_day.py`; when it fails, update docs/24 (and this table) from the new report.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
REPORT = ROOT / "03_Advionics" / "outputs" / "report.md"

#: label -> exact text that must be in the report (the doc quotes these values)
CHECKS = {
    "PSR Pd 0.934": "| PSR Pd per scan | 0.934",
    "Mode A valid/wrong 0.874/0.000": "0.874 / 0.000",
    "Mode C 0.832": "| Mode C valid, per reply | 0.832",
    "false PSR plots 3.0": "| False PSR plots per scan | 3.0",
    "ADS-B 0.993 / 19 m": "0.993 / 19 m",
    "ASTERIX 228 / 6251": "228 records in 6251 octets",
    "CRC 608 / 96 / 15": "ADS-B messages 608: repaired by CRC syndrome (1 bit) 96, rejected 15",
    "CV 5.8 ids, P95 1093": "| CV Kalman | [6, 7, 5, 6, 5, 6] | 5.8 | 20 | 1093 |",
    "IMM 2.0 ids, P95 368": "| IMM | [2, 2, 1, 3, 3, 1] | 2.0 | 16 | 368 |",
    "false tracks 7 / 38": "| 7 / 38 |",
    "Albersheim 13.1 / Swerling 21.1": "steady target (Albersheim) 13.1 dB, Swerling 1 21.1 dB",
    "hits 8, 4-of-8 0.990": "8.0; P(>= 4 of 8 replies) at 0.8 per reply = 0.990",
    "FRUIT-free 0.960/0.816/0.444": "1000/s: 0.960, 5000/s: 0.816, 20000/s: 0.444",
    "real ASR 30 dB": "| 30 | grammar | conservative | 82 | 0 | 18 | 0 |",
    "real ASR 20 dB": "| 20 | grammar | conservative | 55 | 0 | 45 | 25 |",
    "real ASR 15 dB": "| 15 | grammar | conservative | 45 | 0 | 55 | 31 |",
    "real ASR 10 dB": "| 10 | grammar | conservative | 5 | 0 | 95 | 81 |",
    "runway 35R at 0.99": "runway three five right qnh one zero one three\" (utterance confidence 0.99)",
    "threshold 0.95": "| 0.95 | 36 | 0 | 64 | 88 |",
    "PAR speech 30 dB": "| 30 | 24 | 14 | 0 | 10 |",
    "PAR speech 15 dB": "| 15 | 24 | 6 | 0 | 18 |",
    "word model 21 dB": "| 21 | 8 | 53 | 12 | 14 | 25 | 74 |",
    "word model 9 dB": "| 9 | 44 | 129 | 1 | 61 | 99 | 1 |",
    "word model 0 dB": "| 0 | 75 | 102 | 0 | 84 | 100 | 0 |",
    "CAT021 148 records": "148 records in 5403 octets",
    "SSR validation 3000/4": "| 3000 | 4 | 0.9947 | 0.0000 | 0.9947 |",
    "guidance GND lost 125-149": "| GND GUIDANCE LOST | 125-149 |",
    "guidance V FLAG 135-144": "| V FLAG | 135-144 |",
    "guidance MINIMUMS 206-216": "| MINIMUMS | 206-216 |",
    "guidance no clearance 0-19": "| NO APPROACH CLEARANCE | 0-19 |",
    "guidance 10 frames removed": "needles removed (V/L FLAG) in 10;",
    "SSR single 10000 wrong": "| 10000 | 1 | 0.5947 | 0.0053 | 0.6579 |",
    "SSR validation 10000/4": "| 10000 | 4 | 0.8211 | 0.0000 | 0.8737 |",
    "states reach ALL_COMMS_LOST": "ALL_COMMS_LOST @ 200 s",
    "PAR guidance lost at 102 s": "102 s PAR GUIDANCE LOST (7 s)",
    "PSR sweep MTI -50 dB 55.0": "| 0.003 | mti | 55.0 |",
    "PSR sweep MTD -50 dB 39.2": "| 0.003 | mtd | 39.2 |",
    "PSR sweep cmap -50 dB 3.1": "| 0.003 | mtd_cmap | 3.1 |",
    "PSR sweep fixed 450": "| 0.003 | fixed | 450.0 |",
    "tracks MTI 2953": "| MTI + CFAR | 57.0 | 0.45 | 2953 | 0 / 38 |",
    "tracks MTD 2072": "| MTD + CFAR | 40.4 | 0.51 | 2072 | 0 / 38 |",
    "tracks cmap 49": "| MTD + CFAR + clutter map | 2.6 | 0.82 | 49 | 37 / 38 |",
    "tracks cmap+init 3": "| MTD + CFAR + clutter map, PSR-only 3-of-4 and >= 40 kt | 2.6 | 0.82 | 3 | 36 / 38 |",
    "decoder 20 rows": "| surface track | track deg | 92.8125 | 92.8125 | yes | [D] |",
}


def main() -> int:
    text = REPORT.read_text(encoding="utf-8")
    missing = [k for k, v in CHECKS.items() if v not in text]
    print(f"doc-quoted values present in report: {len(CHECKS) - len(missing)}/{len(CHECKS)}")
    for k in missing:
        print(f"  MISSING: {k}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
