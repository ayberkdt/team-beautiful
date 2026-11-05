"""Write the FICTIONAL EASA rehearsal data pack: an unstabilised approach, long landing and runway excursion.

    python scripts/make_rehearsal_pack.py          # → studies/cards_2026/easa_rehearsal.json + easa_rehearsal_track.csv

Nothing here is a real occurrence. The flight path is built in the runway frame of ``aerokit.approach`` (synthetic
runway at 51.0° N 3.0° E, course 262°, 2500 m), then sampled like ADS-B: one position per second with 5 m
horizontal noise and altitude in 25 ft steps (both assumed values for a rehearsal, not a receiver specification).
The pack's narrative, ATC lines, findings and barrier states are invented to exercise the investigation tools.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit import approach as A  # noqa: E402

OUT = ROOT / "studies" / "cards_2026"
RWY = A.Runway(51.0, 3.0, 10.0, 262.0, length=2500.0)
KT, FT, G = A.KT, A.FT, 9.80665


def profile() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """True along-track x (+ before the threshold), cross-track y, height z above the threshold, ground speed."""
    dt = 0.1
    x, t = 12_000.0, 0.0
    decel = 0.20 * G
    T, X, Y, Z, V = [], [], [], [], []
    touchdown = -1200.0                       # 1200 m past the threshold (floated: crossed at ~100 ft)
    v = 0.0
    while True:
        if x > 0:                             # airborne: high and fast, closing on the path late
            path = float(A.glide_path_height(RWY, x))
            excess = np.interp(x, [0.0, 1500.0, 4000.0, 12_000.0], [15.0, 30.0, 110.0, 260.0])
            z = path + excess
            v = float(np.interp(x, [0.0, 3000.0, 12_000.0], [160.0, 165.0, 185.0])) * KT
        elif x > touchdown:                    # flare and float
            z = float(np.interp(x, [touchdown, 0.0], [0.0, 30.0 + 15.24]))
            v = 160 * KT - (0.0 - x) * 0.002
        else:                                  # braking on the runway and beyond
            z = 0.0
            v = max(0.0, v - decel * dt)
            if v < 0.5:
                break
        y = 6.0 * math.sin(t / 25.0) if x > 0 else 2.0
        T.append(t)
        X.append(x)
        Y.append(y)
        Z.append(z)
        V.append(v)
        x -= v * dt
        t += dt
    return np.array(T), np.array(X), np.array(Y), np.array(Z)


def main() -> int:
    rng = np.random.default_rng(42)
    t, x, y, z = profile()
    keep = np.flatnonzero(np.isclose(t % 1.0, 0.0, atol=0.05) | np.isclose(t % 1.0, 1.0, atol=0.05))
    t, x, y, z = t[keep], x[keep], y[keep], z[keep]
    lat, lon, h = RWY.from_runway(x + rng.normal(0, 5.0, x.size), y + rng.normal(0, 5.0, y.size), z)
    alt_ft = np.round((np.asarray(h) / FT) / 25.0) * 25.0             # ADS-B-like 25 ft steps
    t0 = 21 * 3600 + 10 * 60                                           # 21:10:00 UTC, fictional
    rows = [{"t_utc_s": round(t0 + ti, 1), "lat": round(float(a), 7), "lon": round(float(b), 7),
             "alt_ft": float(c)} for ti, a, b, c in zip(t, lat, lon, alt_ft, strict=True)]
    csv_path = OUT / "easa_rehearsal_track.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    pack = {
        "name": "FICTIONAL rehearsal: unstabilised approach, long landing and runway excursion",
        "fictional": True,
        "note": "Invented to rehearse the EASA slot. Not a real occurrence; every fact below is made up.",
        "track_csv": csv_path.name,
        "time_zero_utc_s": t0,
        "runway": {"name": "RWY 26 (synthetic)", "lat": RWY.lat, "lon": RWY.lon, "elevation_m": RWY.elevation,
                   "course_deg": RWY.course_deg, "length_m": RWY.length, "glide_path_deg": 3.0, "tch_m": 15.24},
        "aircraft": {"type": "twin-jet, 150 seats (fictional)", "persons_on_board": 143, "vref_kt": 135},
        "smoothing_window_s": 9,
        "fdm_rules": [
            {"name": "sink rate > 1000 fpm below 1000 ft", "series": "vertical_speed_fpm", "op": "<",
             "limit": -1000, "min_s": 3, "band_ft": [50, 1000]},
            {"name": "ground speed > VREF + 20 kt below 1000 ft", "series": "ground_speed_kt", "op": ">",
             "limit": 155, "min_s": 3, "band_ft": [0, 1000]},
            {"name": "above the glide path by > 1 dot (~0.35 deg) below 1000 ft", "series": "path_dev_deg",
             "op": ">", "limit": 0.35, "min_s": 3, "band_ft": [50, 1000]}],
        "events": [
            {"t_utc": "21:10:05", "source": "ATC", "text": "cleared ILS RWY 26, maintain 180 kt to 4 NM"},
            {"t_utc": "21:09:30", "source": "ATIS", "text": "wind 080/10 kt (tailwind on RWY 26), runway wet"},
            {"t_utc": "21:12:10", "source": "CVR (summary)", "text": "PF: 'we will make it'; no go-around call"},
            {"t_utc": "21:11:10", "source": "ATC", "text": "cleared to land RWY 26"}],
        "hfacs": {
            "Decision errors": ["continued an approach unstable at 1000 ft and 500 ft"],
            "Crew resource management": ["PM did not call 'go around' at the stabilisation gate"],
            "Adverse mental states": ["plan continuation bias under schedule pressure"],
            "Physical environment": ["tailwind and wet runway reduced the stopping margin"],
            "Inadequate supervision": ["FDM had flagged unstable approaches on this route without follow-up"],
            "Organisational climate": ["on-time performance targets emphasised in crew briefings"]},
        "ercs": {"key_risk_area": "excursion", "severity": "S",
                 "severity_reason": "assessed: a ~60 kt overrun into the runway end area makes a hull loss "
                                    "with 20-100 fatalities the credible worst outcome, not the loss of all 143 "
                                    "on board (judgement)",
                 "barriers": {"design": "failed", "tactical planning": "failed",
                              "regulations and procedures": "failed", "situational awareness": "failed",
                              "warning systems": "failed", "late recovery": "failed", "protections": "stopped",
                              "low energy": "remaining"}},
        "safety_recommendations": [
            {"to": "operator", "text": "add a mandatory 'stable / go around' call at 1000 ft and 500 ft with "
                                      "no-fault go-around policy; audit compliance through FDM within 6 months"},
            {"to": "operator", "text": "close the loop on FDM unstable-approach events: crew debrief within 14 "
                                      "days and route-level trend review each quarter"},
            {"to": "aerodrome operator", "text": "assess a runway end safety area or arresting system for "
                                                "RWY 26 within 12 months"},
            {"to": "EASA", "text": "evaluate certification of on-board runway overrun awareness and alerting for "
                                  "new large aeroplanes (systemic; SRUR candidate)"}],
    }
    (OUT / "easa_rehearsal.json").write_text(json.dumps(pack, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {csv_path.relative_to(ROOT)} ({len(rows)} fixes) and studies/cards_2026/easa_rehearsal.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
