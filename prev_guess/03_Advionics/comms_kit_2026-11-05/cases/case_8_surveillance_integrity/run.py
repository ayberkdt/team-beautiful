"""Case 8 — surveillance integrity: a spoofed / displaced ADS-B position on final, detected by multilateration of
the same 1090 MHz signal. CRC is not authentication. (IFF Mode 5 authentication: not modelled — gap.)

    python 03_Advionics/cases/case_8_surveillance_integrity/run.py [--quick] [--set sigma_t_ns=5]

Reuses ``aerokit.atc.mlat`` (tdoa_measure, solve_tdoa, gdop, adsb_consistency) and ``aerokit.atc.modes``
(encode_position + is_valid: a spoofer's squitter passes the CRC).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import Case, figure_set, md_table, save_figure  # noqa: E402

from aerokit.atc import modes as M  # noqa: E402
from aerokit.atc.mlat import adsb_consistency, gdop, solve_tdoa, tdoa_measure  # noqa: E402
from aerokit.atc.translate import wilson  # noqa: E402


def main(argv: list[str] | None = None) -> dict:
    c = Case(__file__, argv, "ADS-B vs MLAT consistency: detection vs spoof offset")
    p = c.p
    rng = np.random.default_rng(int(p["seed"]))
    st = np.array(p["stations_m"], float)
    tgt = np.array(p["target_m"], float)
    sig = p["sigma_t_ns"] * 1e-9
    rows, fix_err = [], []
    for off in p["offsets_m"]:
        flags = 0
        for _ in range(int(p["trials"])):
            fix = solve_tdoa(tdoa_measure(tgt, st, sig, rng), st, tgt + rng.normal(0, 200, 3), sigma_t=sig)
            if off == 0:
                fix_err.append(float(np.linalg.norm(fix.position[:2] - tgt[:2])))
            ang = rng.uniform(0, 2 * math.pi)
            claimed = tgt + np.array([off * math.cos(ang), off * math.sin(ang), 0.0])
            claimed[:2] += rng.normal(0, p["adsb_sigma_m"], 2)
            flags += adsb_consistency(claimed, fix, k=p["k_sigma"], floor_m=p["floor_m"], adsb_sigma_m=p["adsb_sigma_m"],
                                      dims=2)["flag"]
        lo, hi = wilson(flags, int(p["trials"]))
        rows.append({"offset_m": off, "flag_pct": 100 * flags / int(p["trials"]), "ci": (100 * lo, 100 * hi)})
    fa = rows[0]["flag_pct"] if rows and rows[0]["offset_m"] == 0 else float("nan")
    d99 = next((r["offset_m"] for r in rows if r["offset_m"] > 0 and r["flag_pct"] >= 99), None)
    g = gdop(tgt, st)
    lat, lon = 51.0 + tgt[1] / 111_320, 4.0 + tgt[0] / (111_320 * math.cos(math.radians(51)))
    spoof = M.encode_position(p["icao"], lat + 0.01, lon, 2000, False)
    key = [("false alarms on honest ADS-B", f"{fa:.1f} % of {int(p['trials'])} (offset 0)"),
           ("offset detected in >= 99 % of trials", f"{d99} m" if d99 is not None else "not reached in the sweep"),
           ("honest MLAT horizontal error", f"median {np.median(fix_err):.1f} m, P95 {np.percentile(fix_err, 95):.1f} m"
                                            f" (GDOP {g:.2f}); spoofed squitter CRC valid: {M.is_valid(spoof)}")]
    body = ["## Detection of a displaced ADS-B position vs offset", "",
            md_table([{"offset_m": r["offset_m"], "flagged_pct": f"{r['flag_pct']:.1f}",
                       "ci95": f"{r['ci'][0]:.1f}-{r['ci'][1]:.1f}"} for r in rows], ["offset_m", "flagged_pct", "ci95"]),
            "", f"Geometry: {len(st)} receivers, target {p['target_m']} m, timing σ {p['sigma_t_ns']:g} ns, honest "
                f"ADS-B noise σ {p['adsb_sigma_m']:g} m, test (horizontal, MLAT + ADS-B covariance): Mahalanobis > {p['k_sigma']:g} and distance > "
                f"{p['floor_m']:g} m.", "",
            f"CRC is not authentication: the spoofed squitter `{spoof}` (claims a position 1.1 km north) passes the "
            f"Mode S CRC (`modes.is_valid` = {M.is_valid(spoof)}). What a spoofer cannot fake is the time of arrival "
            "at each receiver — that is what MLAT checks.", "",
            "Gaps: no clock-synchronisation error model, no NIC/NACp/SIL decoding, no Mode 5 (military IFF "
            "authentication) model; RES-style injection (up to 2048 targets with FRUIT and reflections, "
            "S_intersoft_res_page [D-ag]) would be the test bench."]
    figs = []
    if not c.args.no_fig:
        dw, S = figure_set(c)
        S.nicelik("offset", "Spoofed position offset", "m", eksen="x")
        S.nicelik("flagged", "Reports flagged as inconsistent", "%", eksen="y", sinir=(0, 102))
        S.varlik("MLAT consistency check")
        fig, ax = S.figur(oran=0.55)
        xs = [r["offset_m"] for r in rows]
        stl = S.stil("MLAT consistency check")
        ax.fill_between(xs, [r["ci"][0] for r in rows], [r["ci"][1] for r in rows], color=stl["color"], alpha=0.15,
                        linewidth=0)
        ax.plot(xs, [r["flag_pct"] for r in rows], marker="o", **stl)
        S.eksen(ax, x="offset", y="flagged")
        dw.etiket.cizgi_sonu(ax)
        figs.append(save_figure(S, fig, c.out, "C8_spoof_detection_vs_offset"))
    c.finish("Case 8 — surveillance integrity (ADS-B spoofing vs MLAT)", key, "\n".join(body), figs)
    return {"rows": rows, "false_alarm_pct": fa, "d99": d99, "spoof_crc_valid": M.is_valid(spoof), "key": key}


if __name__ == "__main__":
    main()
