"""Case 10 replay -> JSON and voice files for the 3D scene (Sunumatik preset ``par_approach``).

The scene never computes guidance. It reads what ``aerokit.atc.parcue`` produced, frame by frame. ``fly_replay`` does not
return the raw radar plots or the aircraft heading, so ``CueLogic`` is wrapped without changing that module: each plot and
what the gate did with it is recorded, and heading and sink are read from the caller's locals at that moment.

The ring on the display is the point on the ideal path T seconds ahead, with T the look-ahead of ``_update_targets``. Its
position is the same pursuit law as the assigned heading and rate, before rounding and hysteresis, and without wind trim:
the flight path marker shows the real track, so a wind needs no term. Marker in ring = velocity aimed at the path, and the
error decays with time constant T. The replay pilot of this scene flies that marker into the ring (:class:`RingPilot`).
The file keeps parcue's own assigned heading and rate (``hdg_assigned``, ``rod_fpm``); the page shows the ring's values, so
the pilot has one target. Case 10 results do not use this pilot.

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
from aerokit.atc.parflight import AIRCRAFT, KT, PilotModel  # noqa: E402

CASE = ROOT / "03_Advionics" / "cases" / "case_10_par_hybrid_cue"
RING_DEG = 1.25            # ring radius on the display
TURBULENCE_KT = float(sys.argv[sys.argv.index("--turb") + 1]) if "--turb" in sys.argv else 6.0   # [Y] calm day; ReplayConfig default is 15
DRIFT_TIME_S = 6.0         # [Y] the pilot reads drift from the marker, averaged over about this time
KEEP = ("t", "state", "lat_dots", "vert_dots", "hdg_rel_deg", "hdg_assigned", "aim_trk_deg", "aim_gam_deg", "ring_rod_fpm", "rod_fpm", "sink_fpm", "gs_ms", "hdg_new", "rod_new", "lat_word",
        "vert_word", "lat_trend", "vert_trend", "age_s", "voice", "range_nm", "height_ft", "closing_fast", "note", "level",
        "visual", "blink", "intensity", "x_m", "y_m", "z_dev_m", "height_m")


class RingPilot:
    """PilotModel, except that the vertical gain follows the ring: ``fly_replay`` reads it each step, _Recording sets it."""

    vertical_wc = 0.05

    def __getattr__(self, name):
        return getattr(PilotModel, name)


class _Recording(parcue.CueLogic):
    """CueLogic that remembers what the radar sent, what the gate did with it, and the aircraft state in the caller."""

    log: list[dict] = []
    state_log: dict = {}
    pilot: RingPilot | None = None
    drift_deg: float | None = None

    def step(self, t, plot, *args, **kwargs):
        before = dict(self._rej)
        out = super().step(t, plot, *args, **kwargs)
        loc = sys._getframe(1).f_locals
        if "psi" in loc:
            _Recording.state_log[round(t, 1)] = (float(loc["psi"]), float(loc.get("sink", 0.0)))
        if plot is not None:
            rej = any(self._rej[k] > before.get(k, 0) for k in self._rej)
            _Recording.log.append({"t": round(t, 1), "tm": round(plot.t, 1), "r": round(plot.range_m, 1),
                                   "y": round(plot.az_dev_m, 1), "z": round(plot.el_dev_m, 1), "rej": bool(rej)})
        self._ring(out, loc)
        return out

    def _ring(self, out: dict, loc: dict) -> None:
        """Add the ring and hand the pilot the heading that puts the marker in it. Only what the cue shows is used for the
        ring (filtered y and z, range, ground speed). Drift comes from the marker, which the pilot can see."""
        c = self.cfg
        out["hdg_assigned"], out["aim_trk_deg"], out["aim_gam_deg"], out["ring_rod_fpm"] = out["hdg_rel_deg"], None, None, None
        psi, tas, cross = loc.get("psi"), loc.get("tas"), loc.get("cross_f")
        if psi is not None and tas:
            now = math.degrees(math.atan2(cross, tas)) if cross is not None else -math.degrees(psi)
            d = _Recording.drift_deg
            _Recording.drift_deg = now if d is None else d + (now - d) / DRIFT_TIME_S
        if out["state"] != "VALID":
            return
        y, z, r, gs = float(self.ky.x[0]), float(self.kz.x[0]), out["range_nm"] * parcue.NM, out["gs_ms"]
        T = min(c.look_ahead_s, max(0.5 * r / gs, c.min_look_ahead_s))
        cap = c.cap_near_deg if r < c.near_nm * parcue.NM else c.cap_far_deg
        trk = max(-cap, min(cap, math.degrees(math.atan(-y / (gs * T)))))
        sink = gs * math.tan(math.radians(self.rwy.glide_path_deg)) + max(-c.max_rod_corr_ms, min(c.max_rod_corr_ms, z / T))
        out["aim_trk_deg"], out["aim_gam_deg"] = trk, -math.degrees(math.atan2(sink, gs))
        # One target on the display: a second, rounded heading beside the ring would be mode confusion.
        # hdg_assigned and rod_fpm stay in the file as parcue said them; hysteresis keeps them up to about 5 deg away.
        out["hdg_rel_deg"] = trk - (_Recording.drift_deg or 0.0)
        out["ring_rod_fpm"] = round(sink * parcue.FPM / 50.0) * 50.0
        _Recording.pilot.vertical_wc = 1.0 / T


def _clean(v):
    return round(v, 3) if isinstance(v, float) else v


def ring_stats(rows: list[dict]) -> None:
    """How often the marker sits in the ring, in valid frames. Track and flight path angle from the true positions, +-1 s."""
    hit = good = 0
    for i in range(1, len(rows) - 1):
        a, b, r = rows[i - 1], rows[i + 1], rows[i]
        if r["state"] != "VALID" or r["aim_trk_deg"] is None:
            continue
        dx = abs(b["x_m"] - a["x_m"])
        trk, gam = math.degrees(math.atan2(b["y_m"] - a["y_m"], dx)), math.degrees(math.atan2(b["height_m"] - a["height_m"], dx))
        good += 1
        hit += math.hypot(trk - r["aim_trk_deg"], gam - r["aim_gam_deg"]) <= RING_DEG
    print(f"   marker in ring: {hit}/{good} valid frames")


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
        _Recording.log, _Recording.state_log, _Recording.drift_deg = [], {}, None
        _Recording.pilot = RingPilot()
        frames = fly_replay(rwy, cfg, rc, pilot=_Recording.pilot, faults=faults, seed=int(p["seed"]))
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
        ring_stats(rows)
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
            "ring_deg": RING_DEG, "turbulence_kt": TURBULENCE_KT,
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
