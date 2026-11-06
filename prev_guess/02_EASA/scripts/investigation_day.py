"""Competition-day command for the EASA slot: occurrence data pack JSON → analysis, timeline and slide figures.

    python prev_guess/02_EASA/scripts/investigation_day.py prev_guess/02_EASA/cards/easa_rehearsal.json

The pack names a position track CSV (``t_utc_s, lat, lon, alt_ft``: ADS-B, radar or an FDR extract), the runway,
FDM rules, narrative events, HFACS findings, ERCS barrier states and draft safety recommendations. The command
reconstructs the flight path (``aerokit.investigation``), measures it against the runway and the 3° path
(``aerokit.approach``), merges data-derived and narrative events into one timeline, scores ERCS and writes
``<pack folder>/out/<pack>/result.json``, ``result.md`` and three English slide figures (datawiz, sunum-tam):
``E1_vertical_profile``, ``E2_speed_profile`` and ``E3_ercs_barriers``.

Speeds from positions are GROUND speeds; indicated airspeed needs the FDR. The report says so.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from day_common import audit_summary, console_text, progress, protect_streams, wants_help  # noqa: E402

from aerokit import approach as A  # noqa: E402
from aerokit import investigation as I  # noqa: E402
from aerokit.mission.geodesy import LocalFrame  # noqa: E402

FT, KT, FPM, G = A.FT, A.KT, A.FPM, I.G0
_OPS = {">": np.greater, "<": np.less}


def hms(t: float) -> str:
    t = int(round(t)) % 86400
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


def seconds(text: str) -> float:
    h, m, s = (float(v) for v in text.split(":"))
    return 3600 * h + 60 * m + s


def load_track(pack: dict, folder: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with (folder / pack["track_csv"]).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    cols = {k: np.array([float(r[k]) for r in rows]) for k in ("t_utc_s", "lat", "lon", "alt_ft")}
    return cols["t_utc_s"], cols["lat"], cols["lon"], cols["alt_ft"] * FT


def first(mask: np.ndarray) -> int | None:
    idx = np.flatnonzero(mask)
    return int(idx[0]) if idx.size else None


def analyse(pack: dict, folder: Path) -> tuple[dict, dict]:
    t_utc, lat, lon, h = load_track(pack, folder)
    tr = I.reconstruct_track(t_utc, lat, lon, h, window_s=pack.get("smoothing_window_s", 9))
    rw = pack["runway"]
    rwy = A.Runway(rw["lat"], rw["lon"], rw["elevation_m"], rw["course_deg"], length=rw["length_m"],
                   glide_path_deg=rw["glide_path_deg"], tch=rw["tch_m"])
    la, lo, hh = LocalFrame(float(lat[0]), float(lon[0]), 0.0).to_geodetic(tr.east, tr.north, tr.height)
    x, y, z = rwy.to_runway(la, lo, hh)
    dev = A.deviation(rwy, x, y, z)
    series = {"vertical_speed_fpm": tr.vertical_speed / FPM, "ground_speed_kt": tr.ground_speed / KT,
              "path_dev_deg": np.where(x > 0, dev.vertical_angle_deg, 0.0), "height_ft": z / FT}
    events = []
    for r in pack["fdm_rules"]:
        lim, op = r["limit"], _OPS[r["op"]]
        band = tuple(b * FT for b in r["band_ft"]) if "band_ft" in r else None
        for ev in I.exceedance_events(tr.t, series, [(r["name"], r["series"], lambda v, o=op, L=lim: o(v, L),
                                                      r["min_s"])], z if band else None, band):
            events.append({"t": ev.t_start, "t_end": ev.t_end, "source": "FDM (computed)",
                           "text": f"{ev.name}: peak {ev.peak:.2f}, {ev.t_end - ev.t_start:.0f} s"})

    vref = pack["aircraft"]["vref_kt"] * KT
    gs = tr.ground_speed
    path = A.glide_path_height(rwy, np.maximum(x, rwy.gpip))
    milestones: dict[str, dict] = {}

    def mark(key: str, i: int | None, text: str) -> None:
        if i is None:
            return
        milestones[key] = {"t": float(tr.t[i]), "x_m": float(x[i]), "height_ft": float(z[i] / FT),
                           "gs_kt": float(gs[i] / KT), "vs_fpm": float(series["vertical_speed_fpm"][i]),
                           "path_excess_ft": float((z[i] - path[i]) / FT) if x[i] > 0 else None,
                           "energy_excess_ft": float(((z[i] - path[i]) + (gs[i] ** 2 - vref ** 2) / (2 * G)) / FT)
                           if x[i] > 0 else None}
        events.append({"t": float(tr.t[i]), "source": "track (computed)", "text": text.format(**milestones[key])})

    mark("gate_1000", first((z <= 1000 * FT) & (x > 0)),
         "1000 ft gate: {gs_kt:.0f} kt GS, {vs_fpm:.0f} fpm, {path_excess_ft:+.0f} ft vs path")
    mark("gate_500", first((z <= 500 * FT) & (x > 0)),
         "500 ft gate: {gs_kt:.0f} kt GS, {vs_fpm:.0f} fpm, {path_excess_ft:+.0f} ft vs path")
    mark("threshold", first(x <= 0), "threshold crossed at {height_ft:.0f} ft, {gs_kt:.0f} kt GS")
    mark("touchdown", first((x < 0) & (z < 3.0)), "touchdown {x_m:.0f} m (negative = past the threshold)")
    i_end = first(x <= -rw["length_m"])
    mark("runway_end", i_end, "runway end passed at {gs_kt:.0f} kt GS")
    i_stop = first((x < 0) & (gs < 1.0))
    i_stop = i_stop if i_stop is not None else tr.t.size - 1
    mark("stop", i_stop, "stopped / last fix {x_m:.0f} m")
    for e in pack["events"]:
        events.append({"t": seconds(e["t_utc"]), "source": e["source"], "text": e["text"]})
    events.sort(key=lambda e: e["t"])

    rows = I.hfacs_table(pack["hfacs"])
    er = pack["ercs"]
    ercs = I.ercs_score(er["key_risk_area"], er["severity"], er["barriers"])
    overrun = float(-x[i_stop] - rw["length_m"])
    out = {"pack": pack["name"], "fictional": pack.get("fictional", False), "note": pack.get("note", ""),
           "runway": rw["name"], "persons_on_board": pack["aircraft"]["persons_on_board"],
           "vref_kt": pack["aircraft"]["vref_kt"], "fixes": int(t_utc.size), "milestones": milestones,
           "overrun_m": overrun, "timeline": [{**e, "t_utc": hms(e["t"])} for e in events],
           "hfacs": [{"level": a, "category": b, "finding": c} for a, b, c in rows],
           "ercs": {"code": ercs.code, "colour": ercs.colour, "barrier_sum": ercs.barrier_sum,
                    "barrier_score": ercs.barrier_score, "value": ercs.value, "counted": list(ercs.counted),
                    "key_risk_area": er["key_risk_area"], "states": er["barriers"],
                    "severity_reason": er.get("severity_reason", "no reason given in the pack")},
           "safety_recommendations": pack["safety_recommendations"]}
    curves = {"x": x, "z": z, "path": A.glide_path_height(rwy, np.maximum(x, 0.0)), "gs": gs, "t": tr.t,
              "length": rw["length_m"], "vref": vref}
    return out, curves


def markdown(out: dict) -> str:
    L = [f"# {out['pack']}", ""]
    if out["fictional"]:
        L += ["**FICTIONAL PACK — rehearsal only.** " + out["note"], ""]
    m = out["milestones"]
    L += ["## What the track shows (computed; speeds are ground speeds — IAS needs the FDR)", ""]
    for key, label in (("gate_1000", "1000 ft gate"), ("gate_500", "500 ft gate")):
        if key in m:
            g = m[key]
            L.append(f"- {label}: {g['gs_kt']:.0f} kt GS (VREF {out['vref_kt']} kt), {g['vs_fpm']:.0f} fpm, "
                     f"{g['path_excess_ft']:+.0f} ft above the 3° path, energy excess {g['energy_excess_ft']:+.0f} ft "
                     "(height + speed above VREF, as height)")
    if "threshold" in m:
        L.append(f"- Threshold crossed at {m['threshold']['height_ft']:.0f} ft and {m['threshold']['gs_kt']:.0f} kt "
                 "GS (nominal 50 ft)")
    if "touchdown" in m:
        L.append(f"- Touchdown {-m['touchdown']['x_m']:.0f} m past the threshold")
    if "runway_end" in m:
        L.append(f"- Runway end passed at {m['runway_end']['gs_kt']:.0f} kt GS; "
                 f"stopped {out['overrun_m']:.0f} m beyond")
    L += ["", f"## Timeline ({out['fixes']} position fixes merged with the pack's events)", "",
          "| UTC | Source | Event |", "|---|---|---|"]
    L += [f"| {e['t_utc']} | {e['source']} | {e['text']} |" for e in out["timeline"]]
    L += ["", "## Human factors (HFACS; hypotheses until the final report)", "",
          "| Level | Category | Finding |", "|---|---|---|"]
    L += [f"| {r['level']} | {r['category']} | {r['finding']} |" for r in out["hfacs"]]
    e = out["ercs"]
    L += ["", "## ERCS risk score", "",
          f"Key risk area **{e['key_risk_area']}**, potential loss class **{e['code'][0]}** "
          f"({out['persons_on_board']} on board; {e['severity_reason']}). Barriers that stopped or remained: "
          f"{', '.join(e['counted']) or 'none'} → weight sum {e['barrier_sum']} → score {e['barrier_score']}. "
          f"**{e['code']} — {e['colour']}** (numerical equivalent {e['value']:g}).", "",
          "## Draft safety recommendations (one addressee each)", ""]
    L += [f"{i}. To the **{r['to']}**: {r['text']}." for i, r in enumerate(out["safety_recommendations"], 1)]
    L += ["", "Wording: causal and contributing factors, no blame (Reg. (EU) 996/2010 Art. 5). Still needed: FDR "
          "(IAS, thrust, brakes, spoilers), CVR transcript, runway friction, crew duty records.", ""]
    return "\n".join(L)


def figures(out: dict, c: dict, folder: Path) -> None:
    import datawiz as dw
    S = dw.Seti(str(folder / "investigation.seti.json"), hedef="sunum-tam")
    S.nicelik("dist", "Distance to the threshold", "km", eksen="x")
    S.nicelik("hgt", "Height above the threshold", "ft", eksen="y")
    S.nicelik("gs", "Ground speed", "kt", eksen="y")
    S.nicelik("barrier", "ERCS barrier", None, eksen="y")
    S.nicelik("weight", "Barrier weight", None, eksen="x")
    S.varlik("Flown")
    S.varlik("3° path", baglam=True)
    S.varlik("Held", renk="#009e73")          # green = held, vermilion = failed: the reader's own convention
    S.varlik("Failed", renk="#d55e00")
    for _ in range(2):
        _slides(S, out, c, folder)
        if S.d.get("kenar_mm"):
            break
        left, bottom, right, top = S.kenar_oner()
        S.kenar(left, bottom, right + 10.0, top)


def _slides(S, out: dict, c: dict, folder: Path) -> None:
    import datawiz as dw
    km = c["x"] / 1000.0
    air = c["x"] > -50.0
    fig, ax = S.figur(oran=0.55)
    ax.plot(km[air], c["path"][air] / FT, **S.stil("3° path"))
    flown, = ax.plot(km[air], c["z"][air] / FT, **S.stil("Flown"))
    ax.invert_xaxis()
    ax.set_ylim(0, None)
    S.eksen(ax, x="dist", y="hgt")
    dw.etiket.cizgi_sonu(ax, [flown])

    g = out["milestones"].get("gate_1000")
    if g:
        dw.notlar.ok(ax, (g["x_m"] / 1000, g["height_ft"]), f"1000 ft: {g['path_excess_ft']:+.0f} ft high, "
                     f"{g['gs_kt']:.0f} kt")
    ax.set_ylim(bottom=0)
    # label the reference path at its far end, in the gap between the two lines (on an inverted axis a label at
    # the right end lands on the axis and one mid-way crosses both lines)
    i0 = int(np.argmax(km[air]))
    ax.annotate("3° path", (km[air][i0], c["path"][air][i0] / FT), xytext=(4, 6), textcoords="offset points",
                ha="left", va="bottom", color=S.renk("3° path"))
    S.kaydet(fig, str(folder / "E1_vertical_profile"), sessiz=True)

    fig, ax = S.figur(oran=0.55)
    ax.plot(km, c["gs"] / KT, **S.stil("Flown"))
    ax.invert_xaxis()
    ax.set_ylim(0, None)
    dw.notlar.bolge(ax, 0.0, -c["length"] / 1000, metin="runway")
    dw.notlar.referans(ax, y=out["vref_kt"] + 20, metin="VREF + 20 kt")
    S.eksen(ax, x="dist", y="gs")
    e = out["milestones"].get("runway_end")
    if e:
        dw.notlar.ok(ax, (e["x_m"] / 1000, e["gs_kt"]), f"runway end at {e['gs_kt']:.0f} kt")
    S.kaydet(fig, str(folder / "E2_speed_profile"), sessiz=True)

    er = out["ercs"]
    names = [b for b in er["states"] if er["states"][b] != "n/a"]
    from aerokit.investigation import ERCS_BARRIERS
    fig, ax = S.figur(oran=0.55)
    yy = np.arange(len(names))[::-1]
    held = [er["states"][b] in ("stopped", "remaining") for b in names]
    for flag, lab in ((True, "Held"), (False, "Failed")):
        sel = [i for i, h in enumerate(held) if h == flag]
        ax.barh(yy[sel], [ERCS_BARRIERS[names[i]] for i in sel], height=0.45, **S.stil(lab, tur="cubuk"))
    for i, b in enumerate(names):
        ax.annotate(er["states"][b], (ERCS_BARRIERS[b], yy[i]), xytext=(4, 0), textcoords="offset points",
                    va="center")
    ax.set_yticks(yy, names)
    ax.set_xlim(0, 6.5)
    S.eksen(ax, x="weight", y="barrier")
    S.kaydet(fig, str(folder / "E3_ercs_barriers"), sessiz=True)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if wants_help(argv):
        print(console_text(__doc__))
        return 0 if argv else 2
    protect_streams()
    path = Path(argv[0])
    pack = json.loads(path.read_text(encoding="utf-8"))
    out, curves = analyse(pack, path.parent)
    folder = path.parent / "out" / path.stem
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    (folder / "result.md").write_text(markdown(out), encoding="utf-8")
    progress("drawing and auditing the slide figures")
    figures(out, curves, folder)
    errors, audit = audit_summary(folder)
    e = out["ercs"]
    print(console_text(markdown(out)))
    print(console_text(audit))
    print(console_text(f"Result: ERCS {e['code']} ({e['colour']}), {len(out['timeline'])} timeline entries, "
                       f"{len(out['safety_recommendations'])} draft recommendations. Next: check each computed event "
                       f"against the pack's narrative, then build the slides from {folder / 'result.md'}"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
