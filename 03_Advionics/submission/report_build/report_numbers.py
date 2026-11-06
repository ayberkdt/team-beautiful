"""Numbers and series for the Advionics report that result.md and validation.json do not hold.

    python -I 03_Advionics/submission/report_build/report_numbers.py

Writes report_numbers.json beside this file. Everything is read from aerokit.atc.parcue and the Zurich data; nothing is
typed by hand. The closed-loop baseline here must match result.md.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from importlib import util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from aerokit.approach import Runway, glide_path_height  # noqa: E402
from aerokit.atc import parcue  # noqa: E402
from aerokit.atc.parcue import CueConfig, PilotModel, ReplayConfig, dh_frame, fly_replay  # noqa: E402
from aerokit.atc.parflight import AIRCRAFT  # noqa: E402
from aerokit.atc.parradar import RadarConfig  # noqa: E402

NM = 1852.0
CASE = ROOT / "03_Advionics" / "cases" / "case_10_par_hybrid_cue"
P = {k: v["value"] for k, v in json.loads((CASE / "params.json").read_text(encoding="utf-8"))["params"].items()}
RWY = Runway(P["rwy_lat"], P["rwy_lon"], P["rwy_elev_m"], P["rwy_course_deg"])
N = int(P["mc_runs"])
BASE = ReplayConfig(start_range_nm=P["start_range_nm"], start_offset_m=P["start_offset_m"], start_above_m=P["start_above_m"],
                    crosswind_ms=P["crosswind_ms"])


def load(name: str, path: Path):
    spec = util.spec_from_file_location(name, path)
    m = util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def at_nm(run: list[dict], nm: float) -> dict:
    return min(run, key=lambda q: abs(q["x_m"] - nm * NM))


def sim_stats(runs: list[list[dict]]) -> dict:
    """Scatter of the true position at each distance, and speed and sink on the 3 to 1 NM segment."""
    rows = []
    for nm in (3, 2, 1):
        fr = [at_nm(r, nm) for r in runs if r[-1]["x_m"] < nm * NM]
        rows.append({"nm": nm, "n": len(fr), "lat_sd_m": float(np.std([f["y_m"] for f in fr])),
                     "vert_sd_m": float(np.std([f["z_dev_m"] for f in fr]))})
    gs, sink = [], []
    for r in runs:
        seg = [f for f in r if NM < f["x_m"] < 3 * NM]
        if len(seg) < 10:
            continue
        t = np.array([f["t"] for f in seg])
        gs.append(-np.polyfit(t, [f["x_m"] for f in seg], 1)[0])
        sink.append(-np.polyfit(t, [f["height_m"] for f in seg], 1)[0])
    return {"rows": rows, "gs_kt_median": float(np.median(gs)) / 0.514444, "sink_fpm_median": float(np.median(sink)) * 196.85,
            "sink_fpm_p5": float(np.percentile(sink, 5)) * 196.85, "sink_fpm_p95": float(np.percentile(sink, 95)) * 196.85}


def real_stats(val, df, rwy: Runway, n: int) -> dict:
    tr = val._tracks(df, rwy, n)
    val._centre(tr, rwy)
    gs, sink, rows = [], [], []
    for a in tr:
        m = (a["x"] > NM) & (a["x"] < 3 * NM)
        gs.append(-np.polyfit(a["t"][m], a["x"][m], 1)[0])
        sink.append(-np.polyfit(a["t"][m], a["z"][m], 1)[0])
    for nm in (5, 4, 3, 2, 1):
        ys, zs, raw = [], [], []
        for a in tr:
            k = int(np.argmin(np.abs(a["x"] - nm * NM)))
            if abs(a["x"][k] - nm * NM) < 150:
                d = a["z"][k] - float(glide_path_height(rwy, a["x"][k]))
                ys.append(a["y"][k])
                zs.append(d)
                raw.append(d + a["z_bias"])
        rows.append({"nm": nm, "n": len(ys), "lat_sd_m": float(np.std(ys)), "vert_sd_m": float(np.std(zs)),
                     "vert_sd_with_flight_constant_m": float(np.std(raw))})
    return {"tracks": len(tr), "rows": rows, "gs_kt_median": float(np.median(gs)) / 0.514444,
            "gs_kt_p5": float(np.percentile(gs, 5)) / 0.514444, "gs_kt_p95": float(np.percentile(gs, 95)) / 0.514444,
            "sink_fpm_median": float(np.median(sink)) * 196.85, "sink_fpm_p5": float(np.percentile(sink, 5)) * 196.85,
            "sink_fpm_p95": float(np.percentile(sink, 95)) * 196.85}


def bands(runs: list[list[dict]], key: str) -> dict:
    """Median and 5-95 % of a true deviation against distance to the runway, on a 0.1 NM grid."""
    grid = np.arange(0.7, 5.01, 0.1)
    v = np.full((len(runs), len(grid)), np.nan)
    for i, r in enumerate(runs):
        x = np.array([f["x_m"] for f in r])[::-1] / NM
        y = np.array([f[key] for f in r])[::-1]
        keep = (grid >= x[0]) & (grid <= x[-1])
        v[i, keep] = np.interp(grid[keep], x, y)
    ok = np.sum(~np.isnan(v), axis=0) >= 0.5 * len(runs)
    return {"nm": grid[ok].round(2).tolist(), "p5": np.nanpercentile(v[:, ok], 5, axis=0).round(1).tolist(),
            "p50": np.nanpercentile(v[:, ok], 50, axis=0).round(1).tolist(),
            "p95": np.nanpercentile(v[:, ok], 95, axis=0).round(1).tolist()}


def ring_mc(exp, rc: ReplayConfig, n: int) -> dict:
    """The pilot flies the marker into the ring (RingPilot of the display export) instead of the rounded heading target."""
    logic = parcue.CueLogic
    parcue.CueLogic = exp._Recording
    runs = []
    hit = good = 0
    try:
        for s in range(n):
            exp._Recording.log, exp._Recording.state_log, exp._Recording.drift_deg = [], {}, None
            exp._Recording.pilot = exp.RingPilot()
            fr = fly_replay(RWY, CueConfig(), rc, pilot=exp._Recording.pilot, seed=s)
            runs.append(fr)
            for a, r, b in zip(fr, fr[1:], fr[2:]):
                if r["state"] != "VALID" or r.get("aim_trk_deg") is None:
                    continue
                dx = abs(b["x_m"] - a["x_m"])
                trk = math.degrees(math.atan2(b["y_m"] - a["y_m"], dx))
                gam = math.degrees(math.atan2(b["height_m"] - a["height_m"], dx))
                good += 1
                hit += math.hypot(trk - r["aim_trk_deg"], gam - r["aim_gam_deg"]) <= exp.RING_DEG
    finally:
        parcue.CueLogic = logic
    gate = [g for g in map(dh_frame, runs) if g is not None]
    return {"minimums": len(gate), "of": n, "lat95_m": float(np.percentile([abs(g["y_m"]) for g in gate], 95)),
            "vert95_m": float(np.percentile([abs(g["z_dev_m"]) for g in gate], 95)),
            "ends": {k: sum(r[-1]["state"] == k for r in runs) for k in {r[-1]["state"] for r in runs}},
            "marker_in_ring_pct": 100.0 * hit / max(good, 1)}


def main() -> None:
    out: dict = {"mc_runs": N}
    cfg = CueConfig()
    # closed loop figure: same runs as the Baseline row of result.md
    cue = [fly_replay(RWY, cfg, BASE, seed=s) for s in range(N)]
    nocue = [fly_replay(RWY, cfg, BASE, pilot=PilotModel(follows_cue=False), seed=s) for s in range(N)]
    gate = [g for g in map(dh_frame, cue) if g is not None]
    out["baseline"] = {"minimums": len(gate), "lat95_m": float(np.percentile([abs(g["y_m"]) for g in gate], 95)),
                       "vert95_m": float(np.percentile([abs(g["z_dev_m"]) for g in gate], 95))}
    out["figure"] = {"cue_y": bands(cue, "y_m"), "cue_z": bands(cue, "z_dev_m"), "nocue_y": bands(nocue, "y_m"),
                     "nocue_z": bands(nocue, "z_dev_m")}
    print("baseline", out["baseline"], flush=True)
    # like-for-like with Zurich: starts on the path, no steady wind, airliner speed
    onpath = ReplayConfig(aircraft=AIRCRAFT["A320"], start_range_nm=5.0, start_offset_m=0.0, start_above_m=0.0)
    perfect = RadarConfig(sigma_of_limit=0.0, multipath_deg=0.0, detection=1.0)
    out["sim"] = {"on_path_annex10_radar": sim_stats([fly_replay(RWY, cfg, onpath, seed=s) for s in range(N)]),
                  "on_path_half_error_radar": sim_stats([fly_replay(RWY, cfg, onpath, radar=RadarConfig(sigma_of_limit=0.25),
                                                                    seed=s) for s in range(N)]),
                  "on_path_perfect_radar": sim_stats([fly_replay(RWY, cfg, onpath, radar=perfect, seed=s) for s in range(N)]),
                  "offset_start_baseline": sim_stats(cue)}
    print("sim", json.dumps(out["sim"]), flush=True)
    exp = load("par_visual_export", ROOT / "03_Advionics" / "scripts" / "par_visual_export.py")
    out["ring"] = {"baseline": ring_mc(exp, BASE, N),
                   "moderate_turbulence": ring_mc(exp, replace(BASE, turbulence_w20_kt=30.0), N)}
    print("ring", out["ring"], flush=True)
    (HERE / "report_numbers.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    val = load("validate_real", CASE / "validate_real.py")
    rwy = val._runway_14()
    df = val._load(Path("D:/tmp_ideathon/advionics_data"))
    out["zurich"] = real_stats(val, df, rwy, 1000)
    (HERE / "report_numbers.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("zurich", json.dumps(out["zurich"], indent=0))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
