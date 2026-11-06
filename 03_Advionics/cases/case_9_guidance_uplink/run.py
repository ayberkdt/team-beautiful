"""Case 9 — radar-derived guidance sent to the aircraft as data: bit format, CRC, loss timeout, what the panel shows
when messages stop.

    python 03_Advionics/cases/case_9_guidance_uplink/run.py [--set rate_hz=2] [--set timeouts_s=[1,2,4]]

Reuses ``aerokit.atc.uplink`` (pack/unpack with CRC-24, quantisation, exact nuisance-alarm probability + Monte
Carlo), ``aerokit.atc.par`` (par_measure), ``aerokit.atc.guidance`` (GuidancePanel: GND GUIDANCE LOST, needles
removed) and ``aerokit.approach`` (simulate_approach). Not modelled: authentication, transport, channel load.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.approach import ApproachSimConfig, NavSensor, Runway, glide_path_height, simulate_approach  # noqa: E402
from aerokit.atc import uplink as U  # noqa: E402
from aerokit.atc.guidance import GuidanceConfig, GuidancePanel, SourceReading  # noqa: E402
from aerokit.atc.par import par_measure  # noqa: E402
from aerokit.atc.translate import flip_bits  # noqa: E402


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "guidance uplink: format, CRC, loss timeout trade-off, panel behaviour")
    p = c.p
    rng = np.random.default_rng(int(p["seed"]))
    fmt = tuple(U.Field(n, int(b), float(lsb), bool(s)) for n, b, lsb, s in p["fields"])
    nbits = U.format_bits(fmt)
    q = U.quantisation_errors(fmt)
    # CRC: corrupt packed messages, count corruptions that pass
    undetected = corrupted = 0
    for _ in range(int(p["crc_trials"])):
        vals = {"seq": int(rng.integers(256)), "t_meas_s": float(rng.uniform(0, 1000)),
                "range_m": float(rng.uniform(0, 15000)), "el_dev_m": float(rng.uniform(-100, 100)),
                "az_dev_m": float(rng.uniform(-300, 300)), "valid": 1, "quality": int(rng.integers(8))}
        w = U.pack(vals, fmt)
        rx, nf = flip_bits(f"{w:0{(nbits + 3) // 4}X}", p["crc_ber"], rng)
        if nf:
            corrupted += 1
            undetected += U.unpack(int(rx, 16), fmt) is not None
    # timeout trade-off (exact) + Monte Carlo check at the design point
    curves = {t: [100 * U.nuisance_alarm_probability(pl, p["rate_hz"], t, p["approach_s"]) for pl in p["p_loss"]]
              for t in p["timeouts_s"]}
    design = {t: (U.nuisance_alarm_probability(p["p_loss_design"], p["rate_hz"], t, p["approach_s"]),
                  U.simulate_gaps(p["p_loss_design"], p["rate_hz"], t, p["approach_s"], int(p["mc_runs"]),
                                  seed=int(p["seed"])))
              for t in p["timeouts_s"]}
    # end to end: PAR measurements up-linked with losses -> pilot panel
    rwy = Runway(51.0, 4.0, 10.0, 250.0)
    run = simulate_approach(rwy, NavSensor("truth-following"), ApproachSimConfig(x0=5 * 1852.0),
                            rng=np.random.default_rng(1))
    panel = GuidancePanel(rwy, "25R", GuidanceConfig(stale_after_s=p["demo_timeout_s"]))
    lost_frames = frames = removed = 0
    next_t = 0.0
    for ti, xi, yi, zi in zip(run.t, run.x, run.y, run.z):
        if ti + 1e-9 < next_t:
            continue
        next_t = float(ti) + 1.0 / p["rate_hz"]
        if rng.random() >= p["demo_p_loss"]:
            m = par_measure(rwy, float(ti), float(xi), float(yi), float(zi), rng)
            word = U.pack({"seq": frames % 256, "t_meas_s": float(ti), "range_m": m.range_m, "el_dev_m": m.el_dev_m,
                           "az_dev_m": m.az_dev_m, "valid": 1, "quality": 7}, fmt)
            d = U.unpack(word, fmt)
            panel.receive(SourceReading("GND PAR uplink", float(ti), float(xi), d["az_dev_m"],
                                        float(glide_path_height(rwy, xi)) + d["el_dev_m"]))
        v = panel.view(float(ti), "25R")
        frames += 1
        lost_frames += any(a.startswith("GND GUIDANCE LOST") for a in v["annunciations"])
        removed += v["vert_dots"] is None
    key = [("message", f"{nbits} bits incl. CRC-24 -> {nbits * p['rate_hz']:.0f} bit/s at {p['rate_hz']:g} Hz; "
                       f"worst rounding: el {q['el_dev_m']:.2f} m, az {q['az_dev_m']:.3f} m "
                       f"(vs VAL {p['vertical_alert_limit_m']:g} m)"),
           (f"nuisance LOST per approach @ loss {p['p_loss_design']:g}",
            "; ".join(f"timeout {t:g} s: {100 * a:.2f} % (MC {100 * b:.2f} %)" for t, (a, b) in design.items())),
           ("CRC-24 on corrupted uplinks", f"{undetected} of {corrupted} corrupted messages accepted "
                                           f"(BER {p['crc_ber']:g}); CRC is not authentication")]
    body = ["## Message format", "",
            md_table([{"field": f.name, "bits": f.bits, "lsb": f.lsb, "signed": f.signed,
                       "span": f"{f.span[0]:g} .. {f.span[1]:g}", "max_rounding": f"{f.lsb / 2:g}"} for f in fmt],
                     ["field", "bits", "lsb", "signed", "span", "max_rounding"]), "",
            "Time of *measurement* (not of transmission) lets the receiver compute the data age; the sequence "
            "number reveals lost or replayed messages (replay of an old valid message is still possible without "
            "authentication).", "",
            "## Probability of at least one spurious GUIDANCE LOST per approach (independent losses, exact)", "",
            md_table([{"p_loss": pl, **{f"timeout {t:g} s (%)": f"{curves[t][i]:.3g}" for t in p["timeouts_s"]}}
                      for i, pl in enumerate(p["p_loss"])],
                     ["p_loss"] + [f"timeout {t:g} s (%)" for t in p["timeouts_s"]]), "",
            f"Time to alert after a real stop is at most timeout + one message interval "
            f"({1 / p['rate_hz']:g} s) + latency (latency not modelled).", "",
            "## End to end through the pilot panel (atc.guidance.GuidancePanel)", "",
            f"PAR measurements up-linked at {p['rate_hz']:g} Hz with {100 * p['demo_p_loss']:.0f} % random loss, "
            f"timeout {p['demo_timeout_s']:g} s: {lost_frames} of {frames} frames annunciated GND GUIDANCE LOST; "
            f"needles removed in {removed} frames (no other source in this run) — never held at the last value."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("ploss", "Message loss probability", None, eksen="x")
        S.nicelik("nuis", "Approaches with a spurious GUIDANCE LOST", "%", eksen="y", sinir=(0, 100))
        names = [f"Timeout {t:g} s" for t in p["timeouts_s"]]
        for n in names:
            S.varlik(n)
        fig, ax = S.figur(oran=0.55)
        for t, n in zip(p["timeouts_s"], names):
            ax.plot(p["p_loss"], curves[t], marker="o", **S.stil(n))
        ax.set_xscale("log")
        import math
        sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
        dec = range(math.floor(math.log10(min(p["p_loss"]))), math.floor(math.log10(max(p["p_loss"]))) + 1)
        ax.set_xticks([10.0 ** d for d in dec], [f"10{str(d).translate(sup)}" for d in dec])
        ax.minorticks_off()
        S.eksen(ax, x="ploss", y="nuis")
        ax.set_xlim(min(p["p_loss"]) / 1.3, max(p["p_loss"]) * 1.3)
        dw.etiket.cizgi_sonu(ax)
        figs.append(save_figure(S, fig, c.out, "C9_uplink_timeout_tradeoff"))
    c.finish("Case 9 — guidance uplink as data", key, "\n".join(body), figs)
    return {"nbits": nbits, "undetected": undetected, "corrupted": corrupted, "design": design,
            "lost_frames": lost_frames, "frames": frames, "removed": removed, "key": key}


if __name__ == "__main__":
    main()
