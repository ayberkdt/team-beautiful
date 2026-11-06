"""Check the cue on real approaches: Zurich ADS-B tracks and the Smolensk 2010 radar talk-down.

    python -I 03_Advionics/cases/case_10_par_hybrid_cue/validate_real.py [--data D:/tmp_ideathon/advionics_data] [--n 1000]

Open loop: the aircraft does not react to the cue. It tests the filter, gate, words, false alarms and how early the cue
sees a real excursion, not the closed loop.

Zurich data: Figshare 11406735 ``landing_dataset.parquet`` (MIT, 19,480 landings, Oct-Nov 2019), go-around labels Zenodo
7148117 (CC BY 4.0). Neither is stored in this project. ADS-B is not truth: tracks are treated as true, the PAR error model
is added on top. One constant height offset per runway is removed, so a bias common to all flights is not visible.

Smolensk data: Polish Committee Final Report 192/2010/11, pp. 214-216 (table in research/R5, A4). It gives 13 points. The
event is used for deviations and calls only, with no finding on blame.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from aerokit.approach import Runway, glide_path_height  # noqa: E402
from aerokit.atc.parcue import MISSED_STATES, CueConfig, dh_frame, fly_replay, replay_track  # noqa: E402
from aerokit.atc.parradar import RadarConfig  # noqa: E402

NM = 1852.0
OUT = Path(__file__).resolve().parent / "outputs"
#: LSZH RWY 14 end, true heading, elevation and displaced threshold from OurAirports; 3.0 deg from Zenodo 7148117
LSZH14 = {"lat": 47.483101, "lon": 8.53473, "elev_ft": 1402.0, "course": 137.0, "displaced_ft": 492.0, "gp": 3.0}
#: time [s] before first strike is 06:41:00.5; distance [m], height above airfield [m], left of centreline [m] or None
SMOLENSK = [("06:39:12", 10110, 502, 0), ("06:39:33", 8300, 528, 65), ("06:39:43.5", 7409, 470, None),
            ("06:39:52.5", 6649, 444, 115), ("06:40:00.5", 5974, 404, None), ("06:40:09", 5251, 341, None),
            ("06:40:16.5", 4591, 287, 130), ("06:40:29.5", 3456, 210, 100), ("06:40:41.5", 2521, 114, 80),
            ("06:40:44.5", 2291, 98, None), ("06:40:52", 1696, 39, None), ("06:40:55", 1459, 14, 70),
            ("06:40:57.5", 1265, 2, 65)]
STRIKE_S = 6 * 3600 + 41 * 60 + 0.5


def _runway_14() -> Runway:
    c = LSZH14
    back = c["displaced_ft"] * 0.3048
    lat = c["lat"] + back * math.cos(math.radians(c["course"])) / 111_194.9
    lon = c["lon"] + back * math.sin(math.radians(c["course"])) / (111_194.9 * math.cos(math.radians(c["lat"])))
    return Runway(lat, lon, c["elev_ft"] * 0.3048, c["course"], glide_path_deg=c["gp"])


def _load(path: Path):
    import pyarrow.parquet as pq
    cols = ["timestamp", "flight_id", "icao24", "latitude", "longitude", "geoaltitude", "groundspeed", "onground"]
    df = pq.read_table(path / "landing_dataset.parquet", columns=cols + ["runway"],
                       filters=[("runway", "=", "14")]).to_pandas()
    return df[~df.onground & df.geoaltitude.notna() & df.latitude.notna()]


def _tracks(df, rwy: Runway, n: int) -> list[dict]:
    """Final segments, 5 NM to about 200 ft, runway metres. Skips tracks with gaps or that do not fly the whole segment."""
    out = []
    for fid, g in df.groupby("flight_id", sort=False):
        lat, lon = g.latitude.to_numpy(), g.longitude.to_numpy()
        h = g.geoaltitude.to_numpy() * 0.3048
        x, y, z = rwy.to_runway(lat, lon, h)
        t = (g.timestamp - g.timestamp.iloc[0]).dt.total_seconds().to_numpy()
        sel = (x > 800.0) & (x < 5.2 * NM) & (np.abs(y) < 2000.0)
        if sel.sum() < 60:
            continue
        i = np.flatnonzero(sel)
        i = i[(i >= i[-1] - 240)]
        if x[i].max() < 4.5 * NM or x[i].min() > 1400.0 or np.max(np.diff(t[i])) > 4.0 or np.any(np.diff(x[i]) > 20.0):
            continue
        out.append({"id": fid, "icao": g.icao24.iloc[0], "t_end": float(t[i[-1]]), "t": t[i] - t[i[0]], "x": x[i], "y": y[i],
                    "z": z[i], "gs": float(g.groundspeed.iloc[i].median()) * 0.514444})
        if len(out) >= n:
            break
    return out


def _centre(tr: list[dict], rwy: Runway) -> tuple[float, float, float]:
    """Remove one constant per axis (heading of the data frame and geometric height offset), from the 1-3 NM medians."""
    ys, zs, xs = [], [], []
    for a in tr:
        m = (a["x"] > 1.0 * NM) & (a["x"] < 3.0 * NM)
        xs.append(a["x"][m])
        ys.append(a["y"][m])
        zs.append(a["z"][m] - glide_path_height(rwy, a["x"][m]))
    x, y, z = (np.concatenate(v) for v in (xs, ys, zs))
    slope, offset = np.polyfit(x, y, 1)
    z0 = float(np.median(z))
    for a, zk in zip(tr, zs):
        a["y"] = a["y"] - (slope * a["x"] + offset)
        a["z_bias"] = float(np.median(zk))        # geometric height differs by aircraft (R5 B2.4): one constant per flight
        a["z"] = a["z"] - a["z_bias"]
    return float(offset), float(math.degrees(math.atan(slope))), z0


def _scatter(tr: list[dict], rwy: Runway) -> list[dict]:
    rows = []
    for nm in (5, 4, 3, 2, 1):
        ys, zs = [], []
        for a in tr:
            k = int(np.argmin(np.abs(a["x"] - nm * NM)))
            if abs(a["x"][k] - nm * NM) < 150:
                ys.append(a["y"][k])
                zs.append(a["z"][k] - float(glide_path_height(rwy, a["x"][k])))
        rows.append({"nm": nm, "n": len(ys), "lat_sd_m": round(float(np.std(ys)), 1), "vert_sd_m": round(float(np.std(zs)), 1),
                     "lat_p99_m": round(float(np.percentile(np.abs(ys), 99)), 1),
                     "vert_p99_m": round(float(np.percentile(np.abs(zs), 99)), 1)})
    return rows


def _sim_scatter(n: int) -> list[dict]:
    rwy = Runway(51.0, 4.0, 10.0, 250.0)
    runs = [fly_replay(rwy, seed=s) for s in range(n)]
    rows = []
    for nm in (3, 2, 1):
        ys, zs = [], []
        for r in runs:
            f = min(r, key=lambda q: abs(q["x_m"] - nm * NM))
            ys.append(f["y_m"])
            zs.append(f["z_dev_m"])
        rows.append({"nm": nm, "lat_sd_m": round(float(np.std(ys)), 1), "vert_sd_m": round(float(np.std(zs)), 1)})
    return rows


def _replay_all(tr: list[dict], rwy: Runway, radar: RadarConfig) -> dict:
    ends, levels, voice = Counter(), Counter(), []
    bad = cues = 0
    for k, a in enumerate(tr):
        fr = replay_track(rwy, a["t"], a["x"], a["y"], a["z"], radar=radar, seed=k, stop_at_end_state=True)
        ends[fr[-1]["state"]] += 1
        levels[max(f["level"] for f in fr)] += 1
        voice.append(sum(1 for f in fr if f["voice"] and f["voice"] != "at_dh"))
        bad += any(f["state"] in ("INVALID", "DELAYED") for f in fr)
        cues += sum(bool(f["hdg_new"]) for f in fr)
    n = len(tr)
    return {"approaches": n, "end_states": dict(ends), "peak_level": {f"L{k}": v for k, v in sorted(levels.items())},
            "voice_median": float(np.median(voice)), "voice_p95": float(np.percentile(voice, 95)),
            "silent_share_pct": round(100.0 * sum(v == 0 for v in voice) / n, 1),
            "invalid_or_delayed_approaches": bad}


def _go_arounds(path: Path, df, rwy: Runway, z_bias: float) -> dict:
    """Real labelled go-arounds on RWY 14: did the cue speak before the climb began? Open loop, so "before" only says the
    deviation was visible; many go-arounds are for traffic or weather, with no deviation at all."""
    import pandas as pd
    ga = pd.read_csv(path / "go_arounds_minimal.csv.gz", usecols=["time", "icao24", "airport", "runway", "has_ga"])
    ga = ga[(ga.airport == "LSZH") & (ga.has_ga.astype(str).str.lower().isin(["true", "1"]))]
    ga["time"] = pd.to_datetime(ga.time, utc=True, errors="coerce")
    ga = ga[(ga.time >= "2019-10-01") & (ga.time < "2019-12-01")]
    r14 = ga[ga.runway.astype(str) == "14"]
    rows, found = [], 0
    for _, g in r14.iterrows():
        w = df[(df.icao24 == g.icao24) & (df.timestamp > g.time - pd.Timedelta(minutes=40)) & (df.timestamp <= g.time)]
        if len(w) < 60:
            continue
        x, y, h = rwy.to_runway(w.latitude.to_numpy(), w.longitude.to_numpy(), w.geoaltitude.to_numpy() * 0.3048)
        t = (w.timestamp - w.timestamp.iloc[0]).dt.total_seconds().to_numpy()
        dev = h - z_bias - glide_path_height(rwy, np.maximum(x, 0.0))
        fin = np.flatnonzero((x > 0.0) & (x < 5.2 * NM) & (np.abs(y) < 2000.0))
        if len(fin) < 40:
            continue
        low = fin[np.argmin(h[fin])]              # the lowest point of the first pass
        start = fin[0]
        if h[low:].max() - h[low] < 150.0 or low - start < 30:
            continue                              # no climb after it: this segment is not the missed approach
        found += 1
        climb = next((k for k in range(start + 10, low + 1) if dev[k] - dev[max(start, k - 10)] > 40.0), low)
        k = slice(start, low + 1)
        fr = replay_track(rwy, t[k] - t[start], x[k], y[k], h[k] - z_bias, seed=found)
        first = next((f for f in fr if f["level"] >= 2), None)
        rows.append({"lowest_m": round(float(h[low] - rwy.elevation), 0), "cue_before_climb_s":
                     None if first is None else round(float(t[climb] - t[start] - first["t"]), 0)})
    said = [r for r in rows if r["cue_before_climb_s"] is not None and r["cue_before_climb_s"] > 0]
    return {"lszh_go_arounds_oct_nov_2019": int(len(ga)), "on_rwy_14": int(len(r14)), "segments_found": found,
            "cue_spoke_before_climb": len(said), "median_lead_s": float(np.median([r["cue_before_climb_s"] for r in said]))
            if said else None}


def smolensk() -> dict:
    """The event track through the cue. The track has 13 points; lateral values between stated points are interpolated."""
    def sec(s: str) -> float:
        h, m, x = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(x)

    gp = 2.0 + 40.0 / 60.0
    rwy = Runway(54.8, 32.0, 0.0, 259.0, glide_path_deg=gp, tch=14.8)
    t = np.array([sec(r[0]) for r in SMOLENSK])
    t0 = t[0]
    x = np.array([r[1] for r in SMOLENSK], float)
    z = np.array([r[2] for r in SMOLENSK], float)
    known = [(sec(r[0]), -r[3]) for r in SMOLENSK if r[3] is not None]
    y = np.interp(t, [k[0] for k in known], [k[1] for k in known])
    cfg = CueConfig(dh_ft=100.0 / 0.3048)                     # this approach had a 100 m limit (R5 A4)
    no_limit = CueConfig(dh_ft=1.0, latch_limits=False)
    res = {}
    for name, c, runs in (("with_limits", cfg, 1), ("limits_off", no_limit, 1)):
        fr = replay_track(rwy, t - t0, x, y, z, cfg=c, noise=False)
        res[name] = {"timeline": [{"before_strike_s": round(STRIKE_S - (t0 + f["t"]), 1), "range_km": round(f["x_m"] / 1000, 2),
                                   "state": f["state"], "vert": f["vert_word"], "trend": f["vert_trend"], "level": f["level"],
                                   "voice": f["voice"], "fast": f["closing_fast"]}
                                  for f in fr if f["voice"] or f["closing_fast"] or f["state"] in ("OUTSIDE LIMITS", "ADVISORY")][:14]}
    noisy = []
    for s in range(200):
        fr = replay_track(rwy, t - t0, x, y, z, cfg=cfg, seed=s, stop_at_end_state=True)
        first = next((f for f in fr if f["state"] == "OUTSIDE LIMITS"), None)
        noisy.append(STRIKE_S - (t0 + first["t"]) if first else 0.0)
    fast = []
    for s in range(200):
        fr = replay_track(rwy, t - t0, x, y, z, cfg=no_limit, seed=s)
        first = next((f for f in fr if f["voice"] == "coming_down"), None)
        fast.append(STRIKE_S - (t0 + first["t"]) if first else 0.0)
    res["noise_200_runs"] = {"limit_called_before_strike_s_median": round(float(np.median(noisy)), 1),
                             "limit_called_runs": int(sum(v > 0 for v in noisy)),
                             "coming_down_before_strike_s_median": round(float(np.median([v for v in fast if v > 0] or [0])), 1),
                             "coming_down_runs": int(sum(v > 0 for v in fast))}
    res["real_first_radar_correction_before_strike_s"] = 5.5
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="D:/tmp_ideathon/advionics_data")
    ap.add_argument("--n", type=int, default=1000)
    a = ap.parse_args()
    path = Path(a.data)
    rwy = _runway_14()
    res: dict = {"smolensk": smolensk()}
    print("smolensk", json.dumps(res["smolensk"]["noise_200_runs"]), flush=True)
    df = _load(path)
    tr = _tracks(df, rwy, a.n)
    res["zurich_tracks"] = len(tr)
    res["zurich_centre_offset_m_heading_deg_height_m"] = _centre(tr, rwy)
    res["zurich_scatter"] = _scatter(tr, rwy)
    res["sim_scatter"] = _sim_scatter(100)
    res["zurich_replay_detection_95"] = _replay_all(tr, rwy, RadarConfig())
    res["zurich_replay_detection_90"] = _replay_all(tr, rwy, RadarConfig(detection=0.90))
    res["go_around_labels"] = _go_arounds(path, df, rwy, res["zurich_centre_offset_m_heading_deg_height_m"][2])
    (OUT / "validation.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "smolensk"}, indent=1))
    print(json.dumps(res["smolensk"], indent=0)[:3500])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
