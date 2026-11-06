"""Case 6 — drone flight inspection of an approach aid (SkyRF-style "Mini-Approach"): measure the DDM in space,
flag faults, give a pass/fail statistic.

    python 03_Advionics/cases/case_6_flight_inspection_ils_drone/run.py [--set aid_bias_ddm=0.012] [--set tolerance_ddm=0.008]

Reuses ``aerokit.atc.ils`` (ils_baseband, read_ils: validate first, FLAG instead of a centred needle) and
``aerokit.approach`` (Runway, deviation). GAP: no signal-in-space model (antenna pattern, beam bends), and the ICAO
Doc 8071 / Annex 10 tolerances were not read — the tolerance is a parameter.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.approach import Runway, deviation, glide_path_height  # noqa: E402
from aerokit.atc.ils import ils_baseband, read_ils  # noqa: E402


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "drone ILS inspection: DDM vs truth, FLAG on faults, acceptance statistic")
    p = c.p
    rng = np.random.default_rng(int(p["seed"]))
    rwy = Runway(p["rwy_lat"], p["rwy_lon"], p["rwy_elev_m"], p["rwy_course_deg"])
    dur = (p["start_range_m"] - p["end_range_m"]) / p["ground_speed_mps"]
    samples = []
    for k, t in enumerate(np.arange(0.0, dur, p["sample_s"])):
        x = p["start_range_m"] - p["ground_speed_mps"] * t
        y = p["weave_amplitude_m"] * math.sin(2 * math.pi * t / p["weave_period_s"])
        z = float(glide_path_height(rwy, x))
        ang = float(deviation(rwy, x, y, z).lateral_angle_deg)
        true_ddm = p["full_scale_ddm"] * ang / p["full_scale_deg"]
        # what the drone *thinks* the truth is: RTK position error -> DDM error at this range
        y_err = float(rng.normal(0, p["truth_sigma_m"]))
        ref_ddm = p["full_scale_ddm"] * float(deviation(rwy, x, y + y_err, z).lateral_angle_deg) / p["full_scale_deg"]
        fault = next((f[2] for f in p["faults"] if f[0] <= t < f[1]), None)
        sig = ils_baseband(true_ddm + p["aid_bias_ddm"], snr_db=p["snr_db"],
                           carrier=0.0 if fault == "carrier_off" else 1.0,
                           tones=(fault != "tone90_off", fault != "tone150_off"), seed=int(p["seed"]) * 100000 + k)
        r = read_ils(sig, 8000, full_scale_ddm=p["full_scale_ddm"])
        samples.append({"t": float(t), "x": x, "true_ddm": true_ddm, "ref_ddm": ref_ddm, "fault": fault,
                        "ddm": r.ddm, "flag": r.flag, "reason": r.reason, "dots": r.dots})
    valid = [s for s in samples if not s["flag"]]
    err = np.array([s["ddm"] - s["ref_ddm"] for s in valid])
    bias, sd = float(err.mean()), float(err.std(ddof=1))
    half = 1.96 * sd / math.sqrt(len(err))
    verdict = "PASS" if abs(bias) + half <= p["tolerance_ddm"] else "FAIL"
    in_fault = [s for s in samples if s["fault"]]
    flagged_fault = sum(s["flag"] for s in in_fault)
    false_flag = sum(s["flag"] for s in samples if not s["fault"])
    centred = sum(1 for s in in_fault if not s["flag"] and s["dots"] is not None and abs(s["dots"]) < 0.05)
    key = [("measured course alignment error", f"{bias:+.5f} DDM ± {half:.5f} (95 %, n = {len(err)}) vs injected "
                                               f"{p['aid_bias_ddm']:+.4f} -> {verdict} at tolerance "
                                               f"{p['tolerance_ddm']:g} DDM [tolerance is a placeholder]"),
           ("fault samples shown as FLAG", f"{flagged_fault} of {len(in_fault)} (centred needle during a fault: "
                                           f"{centred}); false FLAG outside faults: {false_flag}"),
           ("noise of one reading", f"σ = {sd:.5f} DDM at {p['snr_db']:g} dB detected-audio SNR")]
    reasons: dict[str, int] = {}
    for s in in_fault:
        reasons[s["reason"]] = reasons.get(s["reason"], 0) + 1
    body = ["## Inspection run", "",
            f"Mini-approach from {p['start_range_m']:g} m to {p['end_range_m']:g} m before the threshold on the glide "
            f"path, lateral weave ±{p['weave_amplitude_m']:g} m, one reading every {p['sample_s']:g} s "
            f"({len(samples)} readings). Faults injected: {p['faults']}. FLAG reasons during faults: {reasons}.", "",
            "Acceptance statistic: mean(measured DDM − reference DDM) over valid readings with a 95 % normal "
            "interval; PASS if |mean| + half-width ≤ tolerance. The reference comes from the drone's RTK position "
            "(independent of the aid). A product needs Doc 8071 tolerances, a signal-in-space model and the "
            "drone's antenna/lever-arm budget.", "",
            md_table([{"t": f"{s['t']:.1f}", "true_ddm": f"{s['true_ddm']:+.4f}",
                       "measured": "FLAG" if s["flag"] else f"{s['ddm']:+.4f}", "reason": s["reason"],
                       "fault": s["fault"] or "-"} for s in samples[:: max(1, len(samples) // 16)]],
                     ["t", "true_ddm", "measured", "reason", "fault"])]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("t", "Time", "s", eksen="x")
        S.nicelik("ddm", "Localizer difference in depth of modulation", "DDM", eksen="y")
        S.varlik("True DDM", baglam=True)
        S.varlik("Measured DDM", renk="#6a3d9a", degistir=True)    # palette slot was yellow (1.3:1)
        fig, ax = S.figur(oran=0.55)
        ax.plot([s["t"] for s in samples], [s["true_ddm"] for s in samples], **S.stil("True DDM"))
        ax.plot([s["t"] for s in samples], [np.nan if s["flag"] else s["ddm"] for s in samples],
                **S.stil("Measured DDM"))
        S.eksen(ax, x="t", y="ddm")
        dw.etiket.cizgi_sonu(ax)
        ys = [s["true_ddm"] for s in samples] + [s["ddm"] for s in samples if not s["flag"]]
        hi, lo = max(ys), min(ys)
        ax.set_ylim(lo - 0.05 * (hi - lo), hi + 0.25 * (hi - lo))
        for f0, f1, kind in p["faults"]:
            dw.notlar.bolge(ax, f0, f1)
            ax.text((f0 + f1) / 2, hi + 0.08 * (hi - lo), "FLAG", ha="center", va="bottom", color="#3b3b3b")
        import matplotlib.patheffects as pe
        for txt in ax.texts:        # background halo: band edges and the zero line pass behind the labels
            txt.set_path_effects([pe.withStroke(linewidth=5, foreground="#fafaf7")])
        figs.append(save_figure(S, fig, c.out, "C6_ils_inspection_ddm"))
    c.finish("Case 6 — drone flight inspection of an approach aid", key, "\n".join(body), figs)
    return {"bias": bias, "half": half, "verdict": verdict, "flagged_fault": flagged_fault, "n_fault": len(in_fault),
            "centred": centred, "false_flag": false_flag, "key": key}


if __name__ == "__main__":
    main()
