"""Case 1 — ATC voice → text → structured clearance → cockpit display ("translate signal" = speech).

    python 03_Advionics/cases/case_1_voice_to_display/run.py [--quick] [--set snr_db=[30,20,10]] [--params m.json]

Reuses ``aerokit.atc.translate`` (voice_trace, voice_sweep → clearance.parse, channel.WordChannel,
commhealth.AdvisoryDisplay). Real speech in the loop: ``03_Advionics/scripts/atc_live.py`` (Windows SAPI).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.atc.channel import WordChannel  # noqa: E402
from aerokit.atc.translate import voice_sweep, voice_trace  # noqa: E402


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "voice -> display Monte Carlo + one stage trace")
    p = c.p
    ch = WordChannel(wer_floor=p["wer_floor"], wer_ceiling=p["wer_ceiling"], snr_mid_db=p["snr_mid_db"],
                     snr_width_db=p["snr_width_db"], p_confident_error=p["p_confident_error"])
    res = voice_sweep(p["phrases"], p["snr_db"], p["n_per_snr"], own_callsign=p["own_callsign"],
                      other_phrase=p["other_phrase"], p_other=p["p_other"], channel=ch,
                      known_runways=p["known_runways"], hi=p["hi"], lo=p["lo"], seed=p["seed"])
    trace = voice_trace(p["phrases"][0], p["trace_snr_db"], own_callsign=p["own_callsign"], seed=p["trace_seed"],
                        channel=ch, known_runways=p["known_runways"], hi=p["hi"], lo=p["lo"])
    rows = []
    for i, snr in enumerate(res["snr_db"]):
        cons, nai = res["conservative"][i], res["naive"][i]
        rows.append({"snr": snr, "wer": res["wer_pct"][i], "n": res["n_instructions"][i],
                     "c_ok": cons["correct_pct"], "c_wrong": cons["wrong_per_1000"], "c_wh": cons["withheld_pct"],
                     "n_ok": nai["correct_pct"], "n_wrong": nai["wrong_per_1000"], "n_wh": nai["withheld_pct"]})
    good = [r for r in rows if r["snr"] >= 21] or rows[-1:]
    low = [r for r in rows if r["snr"] <= 9] or rows[:1]
    ratio = sum(r["n_wrong"] for r in good) / max(sum(r["c_wrong"] for r in good), 1e-9)
    key = [("wrong values per 1000, SNR >= 21 dB",
            f"conservative {min(r['c_wrong'] for r in good):.0f}-{max(r['c_wrong'] for r in good):.0f} vs naive "
            f"{min(r['n_wrong'] for r in good):.0f}-{max(r['n_wrong'] for r in good):.0f} (x{ratio:.1f} fewer)"),
           ("withheld (SAY AGAIN), SNR <= 9 dB",
            f"conservative {min(r['c_wh'] for r in low):.0f}-{max(r['c_wh'] for r in low):.0f} % "
            f"(the price of never guessing)"),
           ("stage trace @ %g dB" % p["trace_snr_db"], trace[-1].output)]
    body = ["## Result table (word-error model, all parameters [Y])", "",
            md_table(rows, ["snr", "wer", "n", "c_ok", "c_wrong", "c_wh", "n_ok", "n_wrong", "n_wh"],
                     {"wer": ".1f", "c_ok": ".1f", "c_wrong": ".1f", "c_wh": ".1f", "n_ok": ".1f", "n_wrong": ".1f",
                      "n_wh": ".1f"}),
            "", "Columns: snr dB; wer = simulated word error %; n = instructions; c_ = conservative parser "
            "(confidence masking, ambiguity, runway check), n_ = naive parser (every word at face value); ok %, wrong "
            "per 1000 instructions, wh = withheld %.", "",
            "## Stage-by-stage trace (where the signal becomes a display item)", ""]
    body += [f"{i + 1}. **{s.name}** — `{s.output}`" + (f" ({s.note})" if s.note else "") for i, s in enumerate(trace)]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("snr", "Signal-to-noise ratio of the voice channel", "dB", eksen="x")
        S.nicelik("wrong", "Wrong values shown as confirmed", "per 1000 instructions", eksen="y")
        S.varlik("Naive parser")
        S.varlik("Conservative parser")
        fig, ax = S.figur(oran=0.55)
        for name, k in (("Naive parser", "naive"), ("Conservative parser", "conservative")):
            st = S.stil(name)
            ax.fill_between(res["snr_db"], [r["wrong_ci"][0] for r in res[k]], [r["wrong_ci"][1] for r in res[k]],
                            color=st["color"], alpha=0.15, linewidth=0)
            ax.plot(res["snr_db"], [r["wrong_per_1000"] for r in res[k]], **st)
        S.eksen(ax, x="snr", y="wrong")
        ax.set_ylim(0, None)
        dw.etiket.cizgi_sonu(ax)
        figs.append(save_figure(S, fig, c.out, "C1_voice_wrong_vs_snr"))
    c.finish("Case 1 — voice to display", key, "\n".join(body), figs)
    return {"rows": rows, "trace": trace, "key": key}


if __name__ == "__main__":
    main()
