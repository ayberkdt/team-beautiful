"""Case 4 — PAR talk-down: ground radar measures, guidance reaches the pilot by voice, voice lost on final.

    python 03_Advionics/cases/case_4_par_talkdown/run.py [--set voice_lost_at_s=80] [--set lost_after_s=6]

Reuses ``aerokit.approach`` (Runway, NavSensor, simulate_approach) and ``aerokit.atc.par`` (par_measure with the
Annex 10 accuracy figures via ENRI, talkdown_series, parse_talkdown, ParGuidanceMonitor).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.approach import ApproachSimConfig, NavSensor, Runway, deviation, simulate_approach  # noqa: E402
from aerokit.atc.par import ParGuidanceMonitor, TalkdownRules, parse_talkdown, talkdown_series  # noqa: E402

NM = 1852.0


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "PAR talk-down with a voice loss on final")
    p = c.p
    rwy = Runway(p["rwy_lat"], p["rwy_lon"], p["rwy_elev_m"], p["rwy_course_deg"])
    run = simulate_approach(rwy, NavSensor("biased on-board nav", bias=tuple(p["nav_bias_m"]),
                                           sigma=tuple(p["nav_sigma_m"])),
                            ApproachSimConfig(x0=p["start_range_nm"] * NM, y0=p["start_offset_m"],
                                              gust_sigma=p["gust_sigma"]), rng=np.random.default_rng(int(p["seed"])))
    rules = TalkdownRules(gp_slightly=p["gp_slightly_deg"], gp_well=p["gp_well_deg"])
    ser = talkdown_series(rwy, run.t, run.x, run.y, run.z, every_s=p["every_s"], update_s=p["update_s"],
                          seed=int(p["seed"]), rules=rules, decision_height_m=p["decision_height_m"])
    mon = ParGuidanceMonitor(lost_after_s=p["lost_after_s"], expected_every_s=p["every_s"])
    calls = []
    for m, ph in ser:
        heard = m.t < p["voice_lost_at_s"]
        st = parse_talkdown(ph, m.t)
        if heard:
            mon.receive(st)
        calls.append({"t": round(m.t, 1), "range_nm": round(m.range_m / NM, 2), "par_el_m": round(m.el_dev_m, 1),
                      "heard": heard, "display": f"GP {st.glidepath} / CRS {st.course}" if heard else "-",
                      "phrase": ph})
    t_end = float(run.t[-1])
    frames = []
    for tt in np.arange(0.0, t_end, 1.0):
        i = int(np.searchsorted(run.t, tt))
        i = min(i, len(run.t) - 1)
        v = mon.view(float(tt))
        frames.append({"t": float(tt), "true_el_m": float(deviation(rwy, run.x[i], run.y[i], run.z[i]).vertical_m),
                       "status": v["status"].split(" (")[0].split(" - ")[0], "display": v["display"],
                       "shown": None if v.get("state") is None else v["state"].glidepath})
    lost = [f for f in frames if f["status"].startswith("PAR GUIDANCE LOST")]
    t_lost = lost[0]["t"] if lost else None
    last_heard = max((cl["t"] for cl in calls if cl["heard"]), default=None)
    extrap = sum(1 for f in frames if f["t"] > (t_lost or 1e9) and f["shown"] is not None)
    overdue = sum(1 for f in frames if f["status"].startswith("PAR CALL OVERDUE"))
    around = [f for f in frames if t_lost is not None and last_heard - 1 <= f["t"] <= t_lost + 1]
    hcalls = [cl for cl in calls if cl["heard"]]
    true_at = [frames[min(int(cl["t"]), len(frames) - 1)]["true_el_m"] for cl in hcalls]
    rms = float(np.sqrt(np.mean([(cl["par_el_m"] - tv) ** 2 for cl, tv in zip(hcalls, true_at)]))) if hcalls else 0
    key = [("PAR vs truth on the heard calls", f"mean {np.mean([cl['par_el_m'] for cl in hcalls]):+.1f} m measured "
                                               f"vs {np.mean(true_at):+.1f} m true (RMS error {rms:.1f} m, "
                                               f"{len(hcalls)} calls); aircraft flies its on-board bias high"
            if hcalls else "no heard calls"),
           ("voice lost -> panel shows LOST", f"at {t_lost:.0f} s: {t_lost - last_heard:.0f} s after the last heard "
                                             f"call (rule > {p['lost_after_s']:g} s); before that the panel shows "
                                             f"'last call n s' (age counter), CALL OVERDUE frames: {overdue}"
            if t_lost is not None else "voice never lost in this run"),
           ("values shown after LOST", f"{extrap} (never extrapolated)")]
    body = ["## Talk-down calls (radar → phrase → cockpit display classes)", "",
            md_table(calls, ["t", "range_nm", "par_el_m", "heard", "display", "phrase"]), "",
            "Classes, not invented numbers: an unheard word stays '?' (parse_talkdown). After the loss the crew "
            "applies the lost-communication instruction given before final; the radar still sees the aircraft and "
            "could send the deviation as data (case 9).", "",
            "## Panel text around the voice loss (the class shown is 'as of the last call', with its age)", "",
            md_table([{"t": int(f["t"]), "panel": f["display"], "class": f["shown"] or "-"} for f in around],
                     ["t", "panel", "class"]), "",
            f"With calls every {p['every_s']:g} s and LOST after {p['lost_after_s']:g} s, the window between "
            f"'expected call missing' (> {p['every_s']:g} s + 0.5 s grace) and LOST is "
            f"{max(0.0, p['lost_after_s'] - p['every_s'] - 0.5):g} s, so no amber CALL OVERDUE frame appears; with a "
            "longer lost_after_s the amber state fills the gap."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("t", "Time", "s", eksen="x")
        S.nicelik("eldev", "Vertical deviation from the glide path", "m", eksen="y")
        S.varlik("True deviation", baglam=True)
        S.varlik("PAR measurement (heard)", renk="#1f3a93", degistir=True)
        fig, ax = S.figur(oran=0.55)
        ax.plot([f["t"] for f in frames], [f["true_el_m"] for f in frames], **S.stil("True deviation"))
        hc = [cl for cl in calls if cl["heard"]]
        st = S.stil("PAR measurement (heard)", tur="sacilim")
        ax.scatter([cl["t"] for cl in hc], [cl["par_el_m"] for cl in hc], zorder=3, **st)
        S.eksen(ax, x="t", y="eldev")
        dw.etiket.cizgi_sonu(ax)
        ys = [f["true_el_m"] for f in frames] + [cl["par_el_m"] for cl in hc]
        y_lo, y_hi = min(ys), max(ys)
        if hc:      # direct label for the points, top left (above the early, small true deviation)
            ax.text(frames[0]["t"] + 2, y_hi + 0.06 * (y_hi - y_lo), "PAR measurement (heard)",
                    color=st.get("color", "#1f3a93"), va="bottom", ha="left")
            ax.set_ylim(None, y_hi + 0.2 * (y_hi - y_lo))
        if t_lost is not None:
            dw.notlar.bolge(ax, t_lost, lost[-1]["t"] + 1)
            ax.text((t_lost + lost[-1]["t"]) / 2, y_lo + 0.15 * (y_hi - y_lo), "voice lost:\npanel shows LOST,\nno needle",
                    ha="center", va="bottom", color="#3b3b3b")
        figs.append(save_figure(S, fig, c.out, "C4_par_voice_loss"))
    c.finish("Case 4 — PAR talk-down and voice loss", key, "\n".join(body), figs)
    return {"calls": calls, "frames": frames, "t_lost": t_lost, "extrapolated": extrap, "key": key,
            "overdue": overdue}


if __name__ == "__main__":
    main()
