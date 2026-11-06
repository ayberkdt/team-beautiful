"""Case 7 — voice + surveillance correlation: readback/hearback check and spoken-callsign ↔ track matching.

    python 03_Advionics/cases/case_7_readback_correlation/run.py [--quick] [--set p_readback_error=0.013]

Reuses ``aerokit.atc.clearance`` (parse, readback_check, resolve_callsign, similar_callsigns) and
``aerokit.atc.channel`` (degrade_words). The point the literature makes (HAAWAII: 82 % detection at 67 % false
alarms in operations) is reproduced: real readback errors are rare, so false alarms dominate at low SNR.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.atc import clearance as CL  # noqa: E402
from aerokit.atc.channel import degrade_words  # noqa: E402
from aerokit.atc.translate import wilson  # noqa: E402

DIG = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "niner"]


def corrupt_one_digit(text: str, rng: np.random.Generator) -> str:
    """The pilot reads back one digit wrong (the classic readback error)."""
    w = text.split()
    idx = [i for i, x in enumerate(w) if x in DIG or x == "nine"]
    i = int(rng.choice(idx))
    cur = w[i] if w[i] != "nine" else "niner"
    w[i] = str(rng.choice([d for d in DIG if d != cur]))
    return " ".join(w)


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "readback check vs SNR + callsign correlation with surveillance")
    p = c.p
    rng = np.random.default_rng(int(p["seed"]))
    kw = {"own_callsign": p["own_callsign"], "hi": p["hi"], "lo": p["lo"]}
    rows = []
    for snr in p["snr_db"]:
        n_err = n_ok = det = fa = unver = 0
        for k in range(int(p["n_per_snr"])):
            body = p["clearances"][k % len(p["clearances"])]
            atc_text = f"{p['callsign_words']} {body}"
            is_err = rng.random() < p["p_readback_error"]
            rb_text = f"{corrupt_one_digit(body, rng) if is_err else body} {p['callsign_words']}"
            atc = CL.parse(degrade_words(atc_text, snr, seed=int(rng.integers(1 << 31))), **kw)
            rb = CL.parse(degrade_words(rb_text, snr, seed=int(rng.integers(1 << 31))), **kw)
            r = CL.readback_check(atc, rb)
            # a readback value heard confidently but invalid (e.g. squawk 4681) is also a readback alert
            atc_ok = {i.kind for i in atc.instructions if i.status == "CONFIRMED"}
            bad_rb = any(i.status == "INVALID" and i.conf >= p["hi"] and i.kind in atc_ok for i in rb.instructions)
            alert = bool(r.mismatched) or bad_rb
            unver += bool(r.missing or r.notes) and not alert
            if is_err:
                n_err += 1
                det += alert
            else:
                n_ok += 1
                fa += alert
        alerts = det + fa
        rows.append({"snr": snr, "n_err": n_err, "detect_pct": 100 * det / max(n_err, 1),
                     "detect_ci": tuple(100 * v for v in wilson(det, n_err)),
                     "fa_pct": 100 * fa / max(n_ok, 1), "fa_ci": tuple(100 * v for v in wilson(fa, n_ok)),
                     "ppv_pct": 100 * det / alerts if alerts else float("nan"),
                     "unverifiable_pct": 100 * unver / int(p["n_per_snr"])})
    corr = []
    pool = p["surveillance_callsigns"]
    for h in p["heard_callsigns"]:
        cs, how = CL.resolve_callsign(h, pool, p["min_similarity"])
        corr.append({"heard": h, "matched": cs or "-", "how": how})
    sim = CL.similar_callsigns(p["own_callsign"], pool)
    best = max(rows, key=lambda r: r["snr"])
    worst = min(rows, key=lambda r: r["snr"])
    key = [(f"readback errors caught @ {best['snr']} dB",
            f"{best['detect_pct']:.0f} % (n = {best['n_err']}), false alarms {best['fa_pct']:.1f} % of correct "
            f"readbacks, alerts that are real {best['ppv_pct']:.0f} %"),
           (f"same @ {worst['snr']} dB", f"{worst['detect_pct']:.0f} % caught, false alarms {worst['fa_pct']:.1f} %, "
                                         + (f"alerts that are real {worst['ppv_pct']:.0f} %; "
                                            if worst['ppv_pct'] == worst['ppv_pct'] else "no alerts; ")
                                         + 
                                         f"{worst['unverifiable_pct']:.0f} % unverifiable (check by ear)"),
           ("callsign correlation", "; ".join(f"{r['heard']}->{r['how']}" for r in corr)
            + f"; similar to own: {', '.join(sim) or 'none'}")]
    body = ["## Readback check vs SNR (both transmissions through the word-error model)", "",
            md_table(rows, ["snr", "n_err", "detect_pct", "fa_pct", "ppv_pct", "unverifiable_pct"],
                     {"detect_pct": ".1f", "fa_pct": ".2f", "ppv_pct": ".1f", "unverifiable_pct": ".1f"}), "",
            f"Base rate of real readback errors: {p['p_readback_error']:g} per exchange. An alert is raised only "
            "when both the clearance and the readback have the same field CONFIRMED with different values, or when the "
            "readback value was heard confidently but is invalid (e.g. a squawk with an 8); fields "
            "the recogniser could not confirm are 'unverifiable' (crew/controller checks by ear), never an alarm.",
            "", "## Spoken callsign ↔ surveillance track (resolve_callsign: may confirm one candidate, never choose)",
            "", md_table(corr, ["heard", "matched", "how"]), "",
            f"Similar callsigns to {p['own_callsign']} in the picture: {', '.join(sim) or 'none'} (shown as a "
            "warning line on the cockpit panel)."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("snr", "Signal-to-noise ratio of the voice channel", "dB", eksen="x")
        S.nicelik("alertrate", "Readback alerts", "%", eksen="y", sinir=(0, 100))
        S.varlik("Real errors caught")
        S.varlik("False alarms")
        fig, ax = S.figur(oran=0.55)
        xs = [r["snr"] for r in rows]
        for name, k in (("Real errors caught", "detect"), ("False alarms", "fa")):
            st = S.stil(name)
            ax.fill_between(xs, [r[f"{k}_ci"][0] for r in rows], [r[f"{k}_ci"][1] for r in rows],
                            color=st["color"], alpha=0.15, linewidth=0)
            ax.plot(xs, [r[f"{k}_pct"] for r in rows], **st)
        S.eksen(ax, x="snr", y="alertrate")
        dw.etiket.cizgi_sonu(ax)
        figs.append(save_figure(S, fig, c.out, "C7_readback_alerts_vs_snr"))
    c.finish("Case 7 — readback check and callsign correlation", key, "\n".join(body), figs)
    return {"rows": rows, "corr": corr, "similar": sim, "key": key}


if __name__ == "__main__":
    main()
