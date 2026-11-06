"""Case 3 — radar / RF signal → plots → tracks → ASTERIX → display ("translate signal" = surveillance).

    python 03_Advionics/cases/case_3_radar_signal_to_display/run.py [--quick] [--set bers=[0.001,0.01]]

Reuses ``aerokit.atc.translate`` (adsb_trace, mode_a_trace, modes_ber_outcomes → modes CRC-24 + single-bit repair,
asterix CAT021), ``aerokit.atc.radar`` (PSR SNR, Swerling-1 Pd) and ``aerokit.atc.traffic`` (full chain + KPIs).
Demo page: ``03_Advionics/outputs/scope_demo.html`` (built by ``scripts/atc_html.py``).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.atc import radar as R  # noqa: E402
from aerokit.atc.translate import adsb_trace, mode_a_trace, modes_ber_outcomes  # noqa: E402

NM = 1852.0


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "Mode S message outcomes vs BER, ADS-B/SSR stage traces, PSR budget")
    p = c.p
    ber = modes_ber_outcomes(p["bers"], int(p["n_messages"]), seed=p["seed"], icao_hex=p["icao"])
    tr = adsb_trace(p["callsign"], p["icao"], p["lat"], p["lon"], p["alt_ft"], ber=p["trace_ber"],
                    seed=p["trace_seed"])
    tra = mode_a_trace(p["squawk"], fruit_per_s=p["fruit_per_s"], seed=p["seed"])
    psr = []
    ref = R.psr_snr(p["psr_power_w"], p["psr_gain_dbi"], p["psr_freq_hz"], 1.0, 10 * NM, p["psr_bw_hz"],
                    p["psr_nf_db"], p["psr_losses_db"], n_coherent=int(p["psr_pulses"]))
    for rcs in p["rcs_m2"]:
        r_m = R.psr_range_for_pd(p["pd_required"], p["pfa"], ref * rcs, 10 * NM)
        psr.append({"rcs": rcs, "range_nm": r_m / NM})
    total_wrong = sum(r["counts"]["wrong"] for r in ber["rows"])
    total = sum(r["n"] for r in ber["rows"])
    at1e3 = min(ber["rows"], key=lambda r: abs(math.log10(r["ber"]) + 3))
    key = [("wrong messages displayed (all BERs)",
            f"{total_wrong} of {total} (95 % upper bound {100 * (1 - 0.05 ** (1 / total)):.2f} %)"),
           (f"reaching the display at BER {at1e3['ber']:g}",
            f"{100 * (at1e3['intact'] + at1e3['repaired']):.1f} % ({100 * at1e3['repaired']:.1f} % repaired, "
            f"{100 * at1e3['rejected']:.1f} % rejected)"),
           (f"PSR Pd {p['pd_required']} range (Swerling 1)",
            ", ".join(f"{r['rcs']:g} m2: {r['range_nm']:.1f} NM" for r in psr))]
    body = ["## Mode S extended squitter outcome vs bit error rate", "",
            md_table([{"ber": r["ber"], "bits": r["mean_flipped_bits"], "intact": 100 * r["intact"],
                       "repaired": 100 * r["repaired"], "rejected": 100 * r["rejected"], "wrong": r["counts"]["wrong"],
                       "n": r["n"]} for r in ber["rows"]], ["ber", "bits", "intact", "repaired", "rejected", "wrong", "n"],
                     {"bits": ".2f", "intact": ".1f", "repaired": ".1f", "rejected": ".1f"}), "",
            "intact/repaired/rejected in %, wrong = count of messages that would reach the display with content "
            "different from what was sent; bits = mean flipped bits per 112-bit message.", "",
            "## ADS-B stage trace (signal → display)", ""]
    body += [f"{i + 1}. **{s.name}** — `{s.output}`" + (f" ({s.note})" if s.note else "") for i, s in enumerate(tr)]
    body += ["", f"## Mode A stage trace (FRUIT {p['fruit_per_s']:g}/s)", ""]
    body += [f"{i + 1}. **{s.name}** — `{s.output}`" + (f" ({s.note})" if s.note else "") for i, s in enumerate(tra)]
    kpi = None
    if p["run_traffic"]:
        from aerokit.atc.traffic import Scenario, simulate
        sc = Scenario(seed=int(p["seed"]), psr_power_w=p["psr_power_w"], psr_gain_dbi=p["psr_gain_dbi"],
                      psr_freq_hz=p["psr_freq_hz"], psr_bw_hz=p["psr_bw_hz"], psr_nf_db=p["psr_nf_db"],
                      psr_losses_db=p["psr_losses_db"], psr_pulses=int(p["psr_pulses"]), pfa=p["pfa"],
                      fruit_per_s=p["fruit_per_s"])
        sim = simulate(sc)
        kpi = sim["stats"]["kpi"]
        body += ["", "## Full synthetic chain (traffic.simulate): RASS-style KPIs vs truth [K]", "",
                 md_table([{"kpi": k, "value": f"{v:.3f}" if isinstance(v, float) else v} for k, v in kpi.items()],
                          ["kpi", "value"]), "",
                 "Reference figures (EUROCONTROL 1997, R_eurocontrol_radar_std_1997 [D]): SSR Pd > 97 %, Mode A "
                 "> 98 %, Mode C > 96 %, PSR Pd > 90 %, < 20 false PSR reports/scan."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("ber", "Bit error rate", None, eksen="x")
        S.nicelik("msgshare", "Share of Mode S messages", "%", eksen="y", sinir=(0, 100))
        for n in ("Intact", "Repaired (1 bit)", "Rejected", "Wrong shown"):
            S.varlik(n)
        fig, ax = S.figur(oran=0.55)
        xs = [r["ber"] for r in ber["rows"]]
        for name, k in (("Intact", "intact"), ("Repaired (1 bit)", "repaired"), ("Rejected", "rejected"),
                        ("Wrong shown", "wrong")):
            ax.plot(xs, [100 * r[k] for r in ber["rows"]], marker="o", **S.stil(name))
        ax.set_xscale("log")
        sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
        decades = range(math.floor(math.log10(min(xs))), math.floor(math.log10(max(xs))) + 1)
        ax.set_xticks([10.0 ** d for d in decades], [f"10{str(d).translate(sup)}" for d in decades])
        ax.minorticks_off()
        S.eksen(ax, x="ber", y="msgshare")
        ax.set_xlim(min(xs) / 1.3, max(xs) * 1.3)
        ax.set_ylim(-6, 102)                      # room for the 'Wrong shown' label on the zero line
        dw.etiket.cizgi_sonu(ax)
        figs.append(save_figure(S, fig, c.out, "C3_message_outcome_vs_ber"))
    c.finish("Case 3 — radar / RF signal to display", key, "\n".join(body), figs)
    return {"ber": ber, "psr": psr, "kpi": kpi, "trace": tr, "key": key}


if __name__ == "__main__":
    main()
