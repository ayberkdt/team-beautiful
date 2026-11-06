"""Case 10 replay -> JSON for the 3D scene (Sunumatik preset ``par_approach``).

The scene never computes guidance. It reads what ``aerokit.atc.parcue`` produced, frame by frame. This script adds the
three things ``fly_replay`` does not return, without changing that module:

* raw radar plots: ``CueLogic`` is wrapped, so each plot and its accept/reject result is recorded;
* aircraft heading and sink: rebuilt from the shown targets with the same first-order pilot model. The rebuilt heading
  must reproduce the along-track position of the replay. That check is printed and the script fails if it does not hold.

Run from the project root:  python 03_Advionics/scripts/par_visual_export.py <out.json>
"""
from __future__ import annotations

import json
import math
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.approach import Runway  # noqa: E402
from aerokit.atc import parcue  # noqa: E402
from aerokit.atc.parcue import CueConfig, Fault, PilotModel, ReplayConfig, VOICE_TEXT, fly_replay  # noqa: E402

CASE = ROOT / "03_Advionics" / "cases" / "case_10_par_hybrid_cue"
FPM = parcue.FPM


class _Recording(parcue.CueLogic):
    """CueLogic that remembers what the radar sent and what the gate did with it."""

    log: list[dict] = []

    def step(self, t, plot):
        before = self._rejects
        out = super().step(t, plot)
        if plot is not None:
            rejected = self._rejects > before or not plot.valid
            _Recording.log.append({"t": round(t, 1), "tm": round(plot.t, 1), "r": round(plot.range_m, 1),
                                   "y": round(plot.az_dev_m, 1), "z": round(plot.el_dev_m, 1), "rej": bool(rejected)})
        return out


def rebuild(frames: list[dict], rc: ReplayConfig, pilot: PilotModel, tan_g: float) -> list[dict]:
    """Pilot model of ``fly_replay`` run again on the shown targets: 10 Hz heading and sink, plus the x check."""
    dt = rc.dt
    shown = (0.0, rc.gs_ms * tan_g * FPM)
    lag = deque([shown] * max(1, round(pilot.reaction_s / dt)))
    psi, sink = 0.0, rc.gs_ms * tan_g
    x = frames[0]["x_m"]
    per_s = round(1.0 / dt)
    out, worst, n = [], 0.0, 0
    end = frames[-1]["t"]
    go_around = False
    by_t = {f["t"]: f for f in frames}
    t_end = None
    while n * dt <= end + 1e-9:
        t = n * dt
        if n % per_s == 0:
            f = by_t[round(t, 1)]
            worst = max(worst, abs(x - f["x_m"]))
            if f["hdg_rel_deg"] is not None:
                shown = (f["hdg_rel_deg"], f["sink_fpm"])
            if f["state"] in parcue.END_STATES and t_end is None:
                t_end = t
                go_around = f["state"] != "MINIMUMS"
            out.append({"t": round(t, 1), "psi": round(psi, 5), "sink": round(sink, 3)})
        lag.append(shown)
        seen_h, seen_s = lag.popleft()
        if go_around:
            sink += (-pilot.go_around_climb_ms - sink) * dt / pilot.tau_s
        else:
            psi += (math.radians(seen_h) - psi) * dt / pilot.tau_s
            sink += (seen_s / FPM - sink) * dt / pilot.tau_s
        x -= rc.gs_ms * math.cos(psi) * dt
        n += 1
    return out, worst


def main(out_path: str) -> None:
    p = {k: v["value"] for k, v in json.loads((CASE / "params.json").read_text(encoding="utf-8"))["params"].items()}
    rwy = Runway(p["rwy_lat"], p["rwy_lon"], p["rwy_elev_m"], p["rwy_course_deg"])
    cfg = CueConfig()
    rc = ReplayConfig(start_range_nm=p["start_range_nm"], start_offset_m=p["start_offset_m"],
                      start_above_m=p["start_above_m"], crosswind_ms=p["crosswind_ms"])
    pilot = PilotModel()
    plan = [("A", "Return to path", ()),
            ("B", "Delayed and invalid data", (Fault("delay", p["delay_from_s"], p["delay_to_s"], p["delay_s"]),
                                               Fault("jump", p["jump_from_s"], p["jump_to_s"], p["jump_m"]))),
            ("C", "Guidance lost", (Fault("dropout", p["dropout_from_s"], 1e9),))]
    parcue.CueLogic = _Recording
    tan_g = math.tan(math.radians(rwy.glide_path_deg))
    scenarios = []
    for key, title, faults in plan:
        _Recording.log = []
        frames = fly_replay(rwy, cfg, rc, pilot, faults=faults, seed=int(p["seed"]))
        truth, worst = rebuild(frames, rc, pilot, tan_g)
        print(f"{key}: {len(frames)} frames, {len(_Recording.log)} plots, "
              f"{sum(q['rej'] for q in _Recording.log)} rejected, heading rebuild worst x error {worst:.3f} m, "
              f"end {frames[-1]['state']} x {frames[-1]['x_m']:.0f} z {frames[-1]['height_m']:.1f}")
        if worst > 1.0:
            raise SystemExit(f"heading rebuild does not match the replay in scenario {key}")
        keep = ("t", "state", "lat_dots", "vert_dots", "hdg_rel_deg", "sink_fpm", "hdg_new", "sink_new", "lat_word",
                "vert_word", "age_s", "voice", "range_nm", "height_ft", "x_m", "y_m", "z_dev_m", "height_m")
        rows = []
        for f, q in zip(frames, truth):
            row = {k: (round(f[k], 3) if isinstance(f[k], float) else f[k]) for k in keep}
            row.update(psi=q["psi"], sink_ms=q["sink"])
            rows.append(row)
        scenarios.append({"id": key, "title": title, "frames": rows, "plots": _Recording.log})
    data = {"schema": "par_visual/1", "source": "aerokit.atc.parcue via 03_Advionics/scripts/par_visual_export.py",
            "runway": {"course_deg": rwy.course_deg, "length_m": rwy.length, "glide_deg": rwy.glide_path_deg,
                       "tch_m": rwy.tch, "gpip_m": rwy.gpip},
            "cfg": {"lat_full_deg": cfg.lat_full_scale_deg, "vert_full_deg": cfg.vert_full_scale_deg,
                    "on_path_dots": cfg.on_path_dots, "dh_m": cfg.decision_height_m, "sector_deg": cfg.sector_deg,
                    "max_range_m": cfg.max_range_m},
            "replay": {"gs_ms": rc.gs_ms, "crosswind_ms": rc.crosswind_ms},
            "voice_text": VOICE_TEXT, "scenarios": scenarios}
    Path(out_path).write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("wrote", out_path, Path(out_path).stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
