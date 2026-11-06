"""Case 10 — official Advionics task: radar -> correction -> pilot cue, HYBRID (visual every plot, voice on changes).

    python 03_Advionics/cases/case_10_par_hybrid_cue/run.py [--set crosswind_ms=5] [--no-fig]

Writes result.md, the figure and the offline demo ``outputs/par_cue_demo.html`` (data and voices inlined). Reuses
``aerokit.atc.parcue`` (filter, targets, validity, closed loop), ``parradar``, ``parflight``, ``cue_intensity`` and
``aerokit.atc.asr_sapi`` (Windows voice). Real tracks: ``validate_real.py``.
"""
from __future__ import annotations

import base64
import json
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.approach import Runway  # noqa: E402
from aerokit.atc.parradar import RadarConfig  # noqa: E402
from aerokit.atc.cue_intensity import VOICE_TEXT  # noqa: E402
from aerokit.atc.parcue import (MISSED_STATES, CueConfig, Fault, PilotModel, ReplayConfig, cue_changes,  # noqa: E402
                                dh_frame, fly_replay)

NM = 1852.0
TEMPLATE = Path(__file__).resolve().parents[2] / "templates" / "par_cue.html"


def _r(v, n=1):
    return None if v is None else round(float(v), n)


def _slim(f: dict, course: float) -> dict:
    """One frame for the page: only what the display and the outside view draw."""
    hdg = None if f["hdg_rel_deg"] is None else int(round((course + f["hdg_rel_deg"]) % 360)) or 360
    return {"t": f["t"], "s": f["state"], "ld": _r(f["lat_dots"], 2), "vd": _r(f["vert_dots"], 2), "hdg": hdg,
            "sink": f["rod_fpm"], "lw": f["lat_word"], "vw": f["vert_word"], "lt": f["lat_trend"], "vt": f["vert_trend"],
            "age": _r(f["age_s"]), "hb": f["heartbeat"], "lvl": f["level"], "vis": f["visual"], "blink": f["blink"],
            "v": f["voice"], "dba": f["voice_dba"], "tone": f["tone_first"], "note": f["note"],
            "rn": _r(f["range_nm"], 2), "hf": _r(f["height_ft"], 0), "x": _r(f["x_m"], 0), "y": _r(f["y_m"], 1),
            "z": _r(f["height_m"], 1), "dz": _r(f["z_dev_m"], 1)}


def _chapters(frames: list[dict]) -> list[dict]:
    """The story of a replay, read from the frames themselves."""
    out = [{"t": frames[0]["t"], "label": "Off path"}]
    labels = {"DELAYED": "Radar delayed", "INVALID": "Data invalid", "RADAR LOST": "Radar contact lost",
              "RADAR SUSPECT": "Radar malfunction suspected", "OUTSIDE LIMITS": "Outside limits",
              "ELEVATION FAILED": "Elevation failed", "LINK LOST": "Guidance link lost", "ADVISORY": "At decision height",
              "OVER THRESHOLD": "Over threshold"}
    first = next((f for f in frames if f["hdg_new"] or f["rod_new"]), None)
    if first:
        out.append({"t": first["t"], "label": "Correcting"})
    onp = next((f for f in frames if f["lat_word"] == "ON COURSE" and f["vert_word"] == "ON GLIDEPATH"), None)
    if onp:
        out.append({"t": onp["t"], "label": "On path"})
    for a, b in zip(frames, frames[1:]):
        if a["state"] != b["state"] and b["state"] in labels:
            out.append({"t": b["t"], "label": labels[b["state"]]})
        elif a["state"] in ("DELAYED", "INVALID") and b["state"] == "VALID":
            out.append({"t": b["t"], "label": "Guidance back"})
    return sorted(out, key=lambda c: c["t"])


def _end_text(fr: list[dict]) -> str:
    e = dh_frame(fr)
    if e is None:
        return f"Missed approach flown. Height {fr[-1]['height_m'] * 3.28084:.0f} ft and climbing."
    side = "right" if e["y_m"] >= 0 else "left"
    vert = "above" if e["z_dev_m"] >= 0 else "below"
    return f"At decision height: {abs(e['y_m']):.0f} m {side} of the centreline, {abs(e['z_dev_m']):.0f} m {vert} the path."


def _monte_carlo(rwy, cfg, rc, n: int) -> list[dict]:
    rows = []
    cases = [("Baseline pilot", {}), ("Reaction 4 s", {"pilot": PilotModel(reaction_s=4.0)}),
             ("Tighter height loop (0.45 rad/s)", {"pilot": PilotModel(vertical_wc=0.45)}),
             ("Holds heading 3 deg off", {"pilot": PilotModel(heading_error_deg=3.0)}),
             ("Moderate turbulence", {"rc": replace(rc, turbulence_w20_kt=30.0)}),
             ("Plot detection 90 %", {"radar": RadarConfig(detection=0.90)}),
             ("Radar twice as good", {"radar": RadarConfig(sigma_of_limit=0.25)}),
             ("No cue", {"pilot": PilotModel(follows_cue=False)})]
    for name, kw in cases:
        args = {"rc": rc, **kw}
        runs = [fly_replay(rwy, cfg, seed=s, **args) for s in range(n)]
        ends = Counter(r[-1]["state"] for r in runs)
        gate = [g for g in map(dh_frame, runs) if g is not None]
        rows.append({"case": name, "minimums": len(gate), "limits": ends.get("OUTSIDE LIMITS", 0),
                     "lost": sum(ends.get(k, 0) for k in MISSED_STATES if k != "OUTSIDE LIMITS"),
                     "lat95_m": round(float(np.percentile([abs(g["y_m"]) for g in gate], 95))) if gate else "-",
                     "vert95_m": round(float(np.percentile([abs(g["z_dev_m"]) for g in gate], 95))) if gate else "-",
                     "changes": float(np.median([cue_changes(r) for r in runs])),
                     "voice": float(np.median([sum(1 for f in r if f["voice"]) for r in runs]))})
    return rows


def _fault_timing(rwy, cfg, rc, plan, p, n: int) -> tuple[list[dict], dict, int]:
    """How fast each fault is shown, over n seeds. A run that ended earlier for another reason is left out of the time."""
    rows = []
    b_faults, c_faults = plan[1][2], plan[2][2]
    runs_b = [fly_replay(rwy, cfg, rc, faults=b_faults, seed=s) for s in range(n)]
    runs_c = [fly_replay(rwy, cfg, rc, faults=c_faults, seed=s) for s in range(n)]
    for name, runs, state, t0 in (("Delay 4 s", runs_b, "DELAYED", p["delay_from_s"]),
                                  ("Jump 400 m", runs_b, "INVALID", p["jump_from_s"]),
                                  ("Radar stop", runs_c, "RADAR LOST", p["dropout_from_s"])):
        d = [next(f["t"] for f in r if f["state"] == state) - t0 for r in runs if any(f["state"] == state for f in r)]
        rows.append({"fault": name, "shown_in_runs": len(d), "of": n, "median_s": float(np.median(d)) if d else "-",
                     "worst_s": float(np.max(d)) if d else "-"})
    ends = Counter(r[-1]["state"] for r in runs_b)
    bad = sum(1 for r in runs_b + runs_c for f in r
              if f["state"] in MISSED_STATES and (f["lat_dots"] is not None or f["hdg_rel_deg"] is not None))
    return rows, dict(ends), bad


def _jump_sweep(rwy, cfg, rc, n: int) -> list[dict]:
    """The smallest radar jump the gate catches, far out and close in, and what an uncaught jump does to the aircraft."""
    rows = []
    for size in (30, 60, 100, 150, 200, 300, 400):
        row = {"jump_m": size}
        for key, t0 in (("far", 25.0), ("near", 85.0)):
            caught, worst = 0, []
            for s in range(n):
                clean = fly_replay(rwy, cfg, rc, seed=s)
                r = fly_replay(rwy, cfg, rc, faults=(Fault("jump", t0, t0 + 4.0, float(size)),), seed=s)
                caught += any(f["state"] == "INVALID" for f in r)
                m = min(len(clean), len(r))
                worst.append(max(abs(a["y_m"] - b["y_m"]) for a, b in zip(clean[:m], r[:m])))
            row[f"{key}_caught_pct"] = round(100.0 * caught / n)
            row[f"{key}_moved_m"] = round(float(np.percentile(worst, 95)))
        rows.append(row)
    return rows


def _envelope(rwy, cfg, base_rc, n: int) -> list[dict]:
    """Where the concept stops working: start offset and crosswind."""
    rows = []
    for off in (150.0, 300.0, 450.0):
        for wind in (0.0, 5.0, 10.0):
            rc = replace(base_rc, start_offset_m=off, crosswind_ms=wind)
            frames = [fly_replay(rwy, cfg, rc, seed=s) for s in range(n)]
            gate = [g for g in map(dh_frame, frames) if g is not None]
            rows.append({"offset_m": int(off), "wind_ms": int(wind), "minimums": len(gate), "of": n,
                         "lat95_m": round(float(np.percentile([abs(g["y_m"]) for g in gate], 95))) if gate else "-"})
    return rows


def _voices(out: Path) -> dict:
    """Windows voice -> WAV -> base64 for the page. Any failure leaves the on-screen caption as the only voice output."""
    from aerokit.atc import asr_sapi
    res = {}
    if not asr_sapi.available():
        return {k: {"text": v, "b64": ""} for k, v in VOICE_TEXT.items()}
    vdir = out / "voice"
    for k, text in VOICE_TEXT.items():
        wav = asr_sapi.synthesize(text, vdir / f"{k}.wav", rate=1)
        res[k] = {"text": text, "b64": base64.b64encode(wav.read_bytes()).decode("ascii")}
    return res


def _page(out: Path, scenarios: list[dict], voices: dict) -> Path:
    html = TEMPLATE.read_text(encoding="utf-8")
    tag = '<script src="par_cue_data.js"></script>'
    if tag not in html:
        raise SystemExit(f"{TEMPLATE} does not reference {tag}")
    data = json.dumps({"scenarios": scenarios, "voice": voices}, ensure_ascii=False, separators=(",", ":"))
    html = html.replace(tag, "<script>window.PAR=" + data.replace("</", "<\\/") + ";</script>")
    p = out / "par_cue_demo.html"
    p.write_text(html, encoding="utf-8")
    return p


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "Radar to pilot cue, closed loop, with delayed, invalid and lost data")
    p = c.p
    rwy = Runway(p["rwy_lat"], p["rwy_lon"], p["rwy_elev_m"], p["rwy_course_deg"])
    cfg = CueConfig()
    rc = ReplayConfig(start_range_nm=p["start_range_nm"], start_offset_m=p["start_offset_m"],
                      start_above_m=p["start_above_m"], crosswind_ms=p["crosswind_ms"])
    seed = int(p["seed"])
    plan = [("A", "Return to path", ()),
            ("B", "Delayed and invalid data", (Fault("delay", p["delay_from_s"], p["delay_to_s"], p["delay_s"]),
                                               Fault("jump", p["jump_from_s"], p["jump_to_s"], p["jump_m"]))),
            ("C", "Radar contact lost", (Fault("dropout", p["dropout_from_s"], 1e9),)),
            ("D", "Elevation failure", (Fault("el_invalid", p["dropout_from_s"], 1e9),)),
            ("E", "Guidance link lost", (Fault("link", p["dropout_from_s"], 1e9),))]
    runs = {k: fly_replay(rwy, cfg, rc, faults=f, seed=seed) for k, _, f in plan}
    # an aircraft alert during a cue call: the cue gives way, the display stays
    alert_rc = replace(rc, start_offset_m=320.0, aircraft_alerts=((3.0, 14.0, "TERRAIN"), (60.0, 70.0, "GLIDESLOPE")),
                       radio=((40.0, 46.0),))
    runs["F"] = fly_replay(rwy, cfg, alert_rc, seed=seed)
    plan.append(("F", "Aircraft alert sounding", ()))
    base = fly_replay(rwy, cfg, rc, pilot=PilotModel(follows_cue=False), seed=seed)
    mc = _monte_carlo(rwy, cfg, rc, int(p["mc_runs"]))
    n = int(p["mc_runs"])
    timing, b_ends, b_bad = _fault_timing(rwy, cfg, rc, plan, p, n)
    sweep = _jump_sweep(rwy, cfg, rc, max(n // 2, 2))
    envelope = _envelope(rwy, cfg, rc, n)
    b = mc[0]
    a_end = runs["A"][-1]
    lost_t = next(f["t"] for f in runs["C"] if f["state"] == "RADAR LOST")
    delayed = [f for f in runs["B"] if f["state"] == "DELAYED"]
    invalid = [f for f in runs["B"] if f["state"] == "INVALID"]
    shown_bad = sum(1 for k in "BC" for f in runs[k]
                    if f["state"] in MISSED_STATES and (f["lat_dots"] is not None or f["hdg_rel_deg"] is not None))
    key = [("closed loop", f"{b['minimums']} of {n} runs reach minimums; 95 % error there {b['lat95_m']} m lateral, "
                           f"{b['vert95_m']} m vertical; with no cue {mc[-1]['minimums']} of {n}"),
           ("cue load", f"median {b['changes']:.0f} target changes and {b['voice']:.0f} voice calls per approach"),
           ("bad data", f"delay shown in {len(delayed)} s, jump rejected for {len(invalid)} s, radar stop at "
                        f"{p['dropout_from_s']:.0f} s gives RADAR LOST at {lost_t:.0f} s; {shown_bad} frames show guidance "
                        "without valid data")]
    calls = [{"t": f["t"], "voice": VOICE_TEXT[f["voice"]], "level": f["level"], "dBA": f["voice_dba"]}
             for f in runs["A"] if f["voice"]]
    changes = [{"t": f["t"], "lateral": f["lat_word"], "heading": int(round(p["rwy_course_deg"] + f["hdg_rel_deg"])),
                "vertical": f["vert_word"], "rod_fpm": f["rod_fpm"], "offset_m": round(f["y_m"]), "high_m": round(f["z_dev_m"])}
               for f in runs["A"] if f["hdg_new"] or f["rod_new"]]
    body = ["## Monte Carlo (seeds 0 to n-1, same start and wind)", "",
            md_table(mc, ["case", "minimums", "limits", "lost", "lat95_m", "vert95_m", "changes", "voice"],
                     {"changes": ".0f", "voice": ".0f"}), "",
            "## Fault reaction (scenario B and C faults, all seeds)", "",
            md_table(timing, ["fault", "shown_in_runs", "of", "median_s", "worst_s"]), "",
            f"Scenario B ends: {b_ends}. Frames showing guidance without valid data, all runs: {b_bad}.", "",
            "## Smallest radar jump caught (both axes, 4 s long; far = t 25 s, near = t 85 s)", "",
            "`moved_m`: 95 % of the largest change in true lateral position against the same run with no jump.", "",
            md_table(sweep, list(sweep[0])), "",
            "## Envelope: start offset and crosswind", "", md_table(envelope, list(envelope[0])), "",
            "## Scenario A: target changes", "", md_table(changes, list(changes[0])), "",
            "## Scenario A: voice calls", "", md_table(calls, ["t", "voice", "level", "dBA"]), "",
            f"Scenario A ends: {_end_text(runs['A'])} Replay seed {seed}; the table above gives the spread.", "",
            "Limits: see TECHNICAL.md section 6. Simulated data only. Not approved or ready for flight use."]
    figs = []
    if not c.args.no_fig:
        scen = [{"id": k, "title": title, "frames": [_slim(f, p["rwy_course_deg"]) for f in runs[k]],
                 "chapters": _chapters(runs[k]), "end": _end_text(runs[k])} for k, title, _ in plan]
        # plain data for any other front end (mock-up): no voices, one frame per second, keys as in _slim
        (c.out / "replay_data.json").write_text(json.dumps({"scenarios": scen}, ensure_ascii=False, indent=0),
                                                encoding="utf-8")
        page = _page(c.out, scen, _voices(c.out))
        body += ["", f"Demo: `{page.name}` ({page.stat().st_size / 1024:.0f} kB, offline)."]
        dw, S = figure_set(c)
        S.nicelik("t", "Time", "s", eksen="x")
        S.nicelik("y", "Lateral deviation, true", "m", eksen="y")
        S.varlik("No cue", baglam=True)
        S.varlik("With cue", renk="#1f3a93", degistir=True)
        fig, ax = S.figur(oran=0.55)
        ax.plot([f["t"] for f in base], [f["y_m"] for f in base], **S.stil("No cue"))
        ax.plot([f["t"] for f in runs["A"]], [f["y_m"] for f in runs["A"]], **S.stil("With cue"))
        S.eksen(ax, x="t", y="y")
        # direct labels in free space: at the end of the line, "With cue" sits on the centreline
        ax.text(26, 95, "With cue", color=S.stil("With cue").get("color"), va="bottom", ha="left")
        ax.text(base[-1]["t"] + 2, base[-1]["y_m"], "No cue", color="#6b6b6b", va="center", ha="left")
        dw.notlar.referans(ax, y=0, metin="Centreline", konum="sag")
        figs.append(save_figure(S, fig, c.out, "C10_return_to_path"))
    c.finish("Case 10 — radar to pilot cue (HYBRID)", key, "\n".join(body), figs)
    return {"runs": runs, "mc": mc, "key": key, "lost_t": lost_t, "shown_bad": shown_bad}


if __name__ == "__main__":
    main()
