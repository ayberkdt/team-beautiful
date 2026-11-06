"""Case 10 replay -> JSON and voice files for the 3D scene (Sunumatik preset ``par_approach``).

The scene never computes guidance. It reads what ``aerokit.atc.parcue`` produced, frame by frame. ``fly_replay`` does not
return the raw radar plots or the aircraft heading, so ``CueLogic`` is wrapped without changing that module: each plot and
what the gate did with it is recorded, and heading and sink are read from the caller's locals at that moment.

Run from the project root:  python 03_Advionics/scripts/par_visual_export.py <preset folder> [--no-voice]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.approach import Runway  # noqa: E402
from aerokit.atc import parcue  # noqa: E402
from aerokit.atc.cue_intensity import VOICE_TEXT  # noqa: E402
from aerokit.atc.parcue import CueConfig, Fault, ReplayConfig, fly_replay  # noqa: E402
from aerokit.atc.parflight import AIRCRAFT, KT  # noqa: E402

CASE = ROOT / "03_Advionics" / "cases" / "case_10_par_hybrid_cue"
RING_DEG = 1.25            # ring radius on the display
TURBULENCE_KT = 6.0        # [Y] calm day for the demo replay; Monte Carlo in Case 10 keeps the default
KEEP = ("t", "state", "lat_dots", "vert_dots", "hdg_rel_deg", "rod_fpm", "sink_fpm", "gs_ms", "hdg_new", "rod_new", "lat_word",
        "vert_word", "lat_trend", "vert_trend", "age_s", "voice", "range_nm", "height_ft", "closing_fast", "note", "level",
        "visual", "blink", "intensity", "x_m", "y_m", "z_dev_m", "height_m")


class _Recording(parcue.CueLogic):
    """CueLogic that remembers what the radar sent, what the gate did with it, and the aircraft state in the caller."""

    log: list[dict] = []
    state_log: dict = {}

    def step(self, t, plot):
        before = dict(self._rej)
        out = super().step(t, plot)
        loc = sys._getframe(1).f_locals
        if "psi" in loc:
            _Recording.state_log[round(t, 1)] = (float(loc["psi"]), float(loc.get("sink", 0.0)))
        if plot is not None:
            rej = any(self._rej[k] > before.get(k, 0) for k in self._rej)
            _Recording.log.append({"t": round(t, 1), "tm": round(plot.t, 1), "r": round(plot.range_m, 1),
                                   "y": round(plot.az_dev_m, 1), "z": round(plot.el_dev_m, 1), "rej": bool(rej)})
        return out


def _clean(v):
    return round(v, 3) if isinstance(v, float) else v


def aim_point(rows: list[dict], gs: float, ring_deg: float) -> None:
    """Ring target for the display: the heading and descent the system assigned, smoothed over 3 s so the ring glides.

    No new guidance. Holding the assigned heading and rate puts the flight path marker in the ring. Prints how often the
    replay pilot is inside it, in valid frames."""
    for i, r in enumerate(rows):
        near = [q for q in rows[max(0, i - 1):i + 2] if q["hdg_rel_deg"] is not None and q["rod_fpm"] is not None]
        ok = r["hdg_rel_deg"] is not None and bool(near)
        r["aim_hdg_deg"] = round(sum(q["hdg_rel_deg"] for q in near) / len(near), 3) if ok else None
        rod = sum(q["rod_fpm"] for q in near) / len(near) / parcue.FPM if ok else None
        r["aim_gam_deg"] = round(-math.degrees(math.atan2(rod, gs)), 3) if ok else None
    good = hit = 0
    lat, ver = [], []
    for i in range(2, len(rows) - 2):
        a, b, r = rows[i - 2], rows[i + 2], rows[i]
        if r["state"] != "VALID" or r["aim_hdg_deg"] is None:
            continue
        dx, dz = b["x_m"] - a["x_m"], b["height_m"] - a["height_m"]
        e_l, e_v = r["aim_hdg_deg"] - math.degrees(r["psi"]), math.degrees(math.atan2(dz, abs(dx))) - r["aim_gam_deg"]
        lat.append(abs(e_l))
        ver.append(abs(e_v))
        good += 1
        hit += math.hypot(e_l, e_v) <= ring_deg
    print(f"   marker in ring: {hit}/{good} valid frames, median error lat {sorted(lat)[len(lat) // 2]:.2f} deg, vert {sorted(ver)[len(ver) // 2]:.2f} deg")


def main(folder: str, voice: bool) -> None:
    out = Path(folder)
    p = {k: v["value"] for k, v in json.loads((CASE / "params.json").read_text(encoding="utf-8"))["params"].items()}
    rwy = Runway(p["rwy_lat"], p["rwy_lon"], p["rwy_elev_m"], p["rwy_course_deg"])
    cfg = CueConfig()
    rc = ReplayConfig(aircraft=AIRCRAFT["A320"], start_range_nm=p["start_range_nm"], start_offset_m=p["start_offset_m"],
                      start_above_m=p["start_above_m"], crosswind_ms=p["crosswind_ms"], turbulence_w20_kt=TURBULENCE_KT)
    plan = [("A", "Return to path", ()),
            ("B", "Delayed and invalid data", (Fault("delay", p["delay_from_s"], p["delay_to_s"], p["delay_s"]),
                                               Fault("jump", p["jump_from_s"], p["jump_to_s"], p["jump_m"]))),
            ("C", "Guidance lost", (Fault("dropout", p["dropout_from_s"], 1e9),))]
    parcue.CueLogic = _Recording
    scenarios, used = [], set()
    for key, title, faults in plan:
        _Recording.log, _Recording.state_log = [], {}
        frames = fly_replay(rwy, cfg, rc, faults=faults, seed=int(p["seed"]))
        rows = []
        for f in frames:
            psi, sink = _Recording.state_log.get(round(f["t"], 1), (None, None))
            if psi is None:
                raise SystemExit(f"no aircraft state at t={f['t']} in scenario {key}: fly_replay changed")
            row = {k: _clean(f.get(k)) for k in KEEP}
            row.update(psi=round(psi, 5), sink_ms=round(sink, 3))
            rows.append(row)
            if f.get("voice"):
                used.add(f["voice"])
        aim_point(rows, rc.aircraft.vat_kt * KT, RING_DEG)
        states = []
        for r in rows:
            if not states or states[-1][1] != r["state"]:
                states.append((r["t"], r["state"]))
        print(f"{key}: {len(rows)} frames, {len(_Recording.log)} plots, {sum(q['rej'] for q in _Recording.log)} rejected, "
              f"{states}, end x {rows[-1]['x_m']:.0f} z {rows[-1]['height_m']:.1f}, voice "
              f"{[(r['t'], r['voice']) for r in rows if r['voice']]}")
        scenarios.append({"id": key, "title": title, "frames": rows, "plots": _Recording.log})
    data = {"schema": "par_visual/2", "source": "aerokit.atc.parcue via 03_Advionics/scripts/par_visual_export.py",
            "runway": {"course_deg": rwy.course_deg, "length_m": rwy.length, "glide_deg": rwy.glide_path_deg,
                       "tch_m": rwy.tch, "gpip_m": rwy.gpip},
            "cfg": {"lat_full_deg": cfg.lat_full_scale_deg, "vert_full_deg": cfg.vert_full_scale_deg,
                    "on_fraction": cfg.on_fraction, "limit_lat_deg": cfg.limit_lat_deg, "limit_vert_deg": cfg.limit_vert_deg,
                    "dh_ft": cfg.dh_ft, "sector_deg": cfg.sector_deg, "max_range_m": cfg.max_range_m},
            "replay": {"gs_ms": rc.aircraft.vat_kt * KT, "crosswind_ms": rc.crosswind_ms, "aircraft": rc.aircraft.name},
            "voice_text": VOICE_TEXT, "scenarios": scenarios}
    (out / "par_replay.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("wrote", out / "par_replay.json", (out / "par_replay.json").stat().st_size, "bytes")
    if voice:
        from aerokit.atc.asr_sapi import synthesize
        for k in sorted(used):
            synthesize(VOICE_TEXT[k], out / "voice" / f"{k}.wav")
        print("voices:", sorted(used))


if __name__ == "__main__":
    main(sys.argv[1], "--no-voice" not in sys.argv)
