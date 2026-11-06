"""Competition-day command for the Advionics slot: approach card JSON → integrity numbers and slide figures.

    python prev_guess/03_Advionics/scripts/approach_day.py prev_guess/03_Advionics/cards/approach_rehearsal.json     # ~1-2 min (Monte Carlo)

Writes ``<card folder>/out/<card>/result.json`` and ``result.md`` and three English slide figures (datawiz,
sunum-tam): ``A1_gate_accuracy`` (deviation at the gate per navigation source), ``A2_spoof_monitor`` (a spoofing
ramp with and without a dissimilar monitor) and ``A3_angle_error_range`` (angle error → position error by range).
Every sensor number comes from the card; the card marks which ones are assumptions.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit import approach as A  # noqa: E402
from aerokit import autoland as AL  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from day_common import audit_summary, console_text, progress, protect_streams, sig, wants_help  # noqa: E402

NM = 1852.0


def sensors_from_card(card: dict) -> dict[str, A.NavSensor]:
    """Card sensor entries → NavSensor. Radar and vision errors scale with the range to the gate."""
    r = card["radar_range_at_gate_m"]
    out = {}
    for s in card["sensors"]:
        if "angle_deg" in s:
            ang = r * math.radians(s["angle_deg"])
            sig = (s["range_sigma_m"], ang, ang)
        elif "range_fraction" in s:
            sig = (s["along_sigma_m"], s["range_fraction"] * r, s["range_fraction"] * r)
        else:
            sig = tuple(s["sigma_m"])
        out[s["name"]] = A.NavSensor(s["name"], bias=tuple(s.get("bias_m", (0.0, 0.0, 0.0))), sigma=sig,
                                     tau=s["tau_s"])
    return out


def run(card: dict) -> tuple[dict, dict]:
    rw = card["runway"]
    rwy = A.Runway(rw["lat"], rw["lon"], rw["elevation_m"], rw["course_deg"], glide_path_deg=rw["glide_path_deg"],
                   tch=rw["tch_m"])
    sm = card["sim"]
    cfg = A.ApproachSimConfig(x0=sm["x0_m"], y0=sm["y0_m"], z0_above_path=sm["z0_above_path_m"],
                              wind_speed=sm["wind_speed_ms"], wind_from_rel_deg=sm["wind_from_rel_deg"],
                              gust_sigma=sm["gust_sigma_ms"], tas=sm["tas_ms"])
    sensors = sensors_from_card(card)
    gate = card["gate_ft"] * A.FT
    stats = {}
    for i, (name, s) in enumerate(sensors.items(), 1):      # one source at a time, so the user sees progress
        progress(f"Monte Carlo {i}/{len(sensors)}: {name}, {card['runs']} approaches")
        stats.update(A.monte_carlo_approach(rwy, {name: s}, gate_height=gate, runs=card["runs"], cfg=cfg,
                                            seed=card["seed"]))
    hal, val = A.ALERT_LIMITS[card["alert_limit"]]
    risk = card["integrity_risk"]
    rows = []
    for name, s in sensors.items():
        st = stats[name]
        vpl = A.protection_level(s.sigma[2], risk) + abs(s.bias[2])
        hpl = A.protection_level(s.sigma[1], risk) + abs(s.bias[1])
        rows.append({"source": name, "sigma_m": list(s.sigma), "bias_m": list(s.bias),
                     "vertical_mean_m": st["vertical_mean"], "vertical_p95_m": st["vertical_p95_abs"],
                     "lateral_p95_m": st["lateral_p95_abs"], "vpl_m": vpl, "hpl_m": hpl,
                     "meets_alert_limits": bool(vpl < val and hpl < hal)})

    sp = card["spoof"]
    prim, mon = sensors[sp["primary"]], sensors[sp["monitor"]]
    faulted = A.NavSensor(prim.name + " (spoofed)", prim.bias, prim.sigma, prim.tau, tuple(sp["ramp_m_s"]),
                          sp["ramp_start_s"])
    thr = tuple(A.separation_threshold(a, b, sp["p_false_alert"]) for a, b in zip(prim.sigma, mon.sigma, strict=True))
    cfg_s = A.ApproachSimConfig(x0=sp["x0_m"], tas=sm["tas_ms"])
    blind = A.simulate_approach(rwy, faulted, cfg_s, np.random.default_rng(sp["seed"]))
    guard = A.simulate_approach(rwy, faulted, cfg_s, np.random.default_rng(sp["seed"]), monitor=mon, threshold=thr)
    bound_v = A.fault_bound(thr[2], math.hypot(prim.sigma[2], mon.sigma[2]), sp["p_missed_detection"])
    spoof = {"threshold_m": list(thr), "vertical_fault_bound_m": bound_v, "ramp_m_s": sp["ramp_m_s"],
             "ramp_start_s": sp["ramp_start_s"], "alarm_t_s": guard.extra.get("alarm_t"),
             "alarm_height_m": guard.extra.get("alarm_height"),
             "detection_delay_s": (guard.extra["alarm_t"] - sp["ramp_start_s"]) if "alarm_t" in guard.extra else None,
             "undetected_error_m": guard.extra["undetected_error"],
             "monitored_dev_at_gate_m": guard.at_height(gate)[0] if guard.z.min() <= gate else None,
             "unmonitored_dev_at_end_m": float(blind.vertical_dev[-1]),
             "unmonitored_min_height_m": float(blind.z.min())}

    ln = card["link"]
    noise = A.thermal_noise_power(ln["bandwidth_hz"], ln["noise_figure_db"])
    link = []
    for rnm in ln["ranges_nm"]:
        pr = A.friis_received_power(ln["p_tx_w"], ln["gain_tx_dbi"], ln["gain_rx_dbi"], ln["frequency_hz"],
                                    rnm * NM, ln["losses_db"])
        snr = pr / noise
        sig_deg = A.monopulse_angle_sigma(ln["beamwidth_deg"], snr, ln["k_m"]) / math.sqrt(ln["samples"])
        link.append({"range_nm": rnm, "received_dbm": 10 * math.log10(pr / 1e-3), "snr_db": 10 * math.log10(snr),
                     "angle_sigma_deg": sig_deg, "position_sigma_m": rnm * NM * math.radians(sig_deg)})
    out = {"card": card["name"], "note": card.get("note", ""), "gate_ft": card["gate_ft"], "runs": card["runs"],
           "alert_limit": card["alert_limit"], "hal_m": hal, "val_m": val, "integrity_risk": risk,
           "k_factor": A.k_factor(risk), "sources": rows, "spoof": spoof, "link": link, "link_note": ln["note"]}
    series = {"blind": blind, "guard": guard}
    if "autoland" in card:
        out["autoland"], series["autoland"] = autoland_study(rwy, card)
    return out, series


def autoland_study(rwy: A.Runway, card: dict) -> tuple[list[dict], dict]:
    """Fused-navigation autoland (``aerokit.autoland``): four scenarios × Monte Carlo, plus one spoofed run per
    FDE mode for the slide."""
    al = card["autoland"]
    sp = card["spoof"]
    radar = AL.GroundRadar(tuple(al["radar_site_m"]), *al["radar_sigma"])
    cfg = AL.AutolandConfig(x0=al["x0_m"], tas=card["sim"]["tas_ms"], wind_speed=card["sim"]["wind_speed_ms"],
                            wind_from_rel_deg=card["sim"]["wind_from_rel_deg"], gust_sigma=card["sim"]["gust_sigma_ms"],
                            touchdown_box=tuple(al["touchdown_box_m"]))
    spoof = {"gnss_ramp": tuple(sp["ramp_m_s"]), "gnss_ramp_start": sp["ramp_start_s"]}
    scenarios = [("Fault-free, all sensors", AL.FusionConfig(radar=radar)),
                 ("GNSS spoof, solution-separation FDE", AL.FusionConfig(radar=radar, **spoof)),
                 ("GNSS spoof, innovation FDE", AL.FusionConfig(radar=radar, fde_mode="innovation", **spoof)),
                 ("No GNSS, cold baro", AL.FusionConfig(radar=radar, gnss_sigma=None,
                                                        baro_bias=al["baro_bias_cold_m"]))]
    rows = []
    for i, (name, fusion) in enumerate(scenarios, 1):
        progress(f"autoland {i}/{len(scenarios)}: {name}, {al['runs']} approaches")
        mc = AL.monte_carlo_autoland(rwy, fusion, cfg, runs=al["runs"], seed=al["seed"])
        rows.append({"scenario": name, **mc})
    one = {mode: AL.simulate_autoland(rwy, AL.FusionConfig(radar=radar, fde_mode=mode, **spoof), cfg,
                                      np.random.default_rng(al["seed"]))
           for mode in ("separation", "innovation")}
    return rows, one


def markdown(out: dict) -> str:
    L = [f"# {out['card']}", "", out["note"], "",
         f"## Gate accuracy and integrity at {out['gate_ft']} ft ({out['runs']} runs per source)", "",
         f"Protection level = K·σ + |bias| with K = {out['k_factor']:.2f} "
         f"(integrity risk {out['integrity_risk']:.0e}); "
         f"{out['alert_limit']} limits HAL {out['hal_m']:.0f} m, VAL {out['val_m']:.0f} m.", "",
         "| Navigation source | Vertical mean (m) | Vertical P95 (m) | Lateral P95 (m) | VPL (m) | HPL (m) "
         "| Inside limits |", "|---|---:|---:|---:|---:|---:|---|"]
    for r in sorted(out["sources"], key=lambda r: r["vertical_p95_m"]):
        L.append(f"| {r['source']} | {r['vertical_mean_m']:.1f} | {r['vertical_p95_m']:.1f} | {r['lateral_p95_m']:.1f} "
                 f"| {r['vpl_m']:.1f} | {r['hpl_m']:.1f} | {'yes' if r['meets_alert_limits'] else 'no'} |")
    s = out["spoof"]
    L += ["", "## Spoofing ramp against a dissimilar monitor", ""]
    if s["alarm_t_s"] is None:
        L.append("No alarm: the ramp never separated the sources beyond the threshold.")
    else:
        L.append(f"Ramp {s['ramp_m_s']} m/s from t = {s['ramp_start_s']:.0f} s. Thresholds (along, cross, vertical) "
                 f"{', '.join(f'{v:.1f}' for v in s['threshold_m'])} m. Alarm after {s['detection_delay_s']:.1f} s at "
                 f"{s['alarm_height_m'] / A.FT:.0f} ft; largest undetected error {s['undetected_error_m']:.1f} m "
                 f"(bound {s['vertical_fault_bound_m']:.1f} m).")
    if s["monitored_dev_at_gate_m"] is not None:
        L.append(f"With the monitor the aircraft is {s['monitored_dev_at_gate_m']:+.1f} m from the path at the gate.")
    L.append(f"Without it the aircraft ends {s['unmonitored_dev_at_end_m']:+.0f} m from the path and never descends "
             f"below {s['unmonitored_min_height_m'] / A.FT:.0f} ft before the glide-path intercept.")
    L += ["", "## Transponder-reply link and monopulse angle noise", "", out["link_note"], "",
          "| Range (NM) | Received (dBm) | SNR (dB) | Angle σ (°) | Position σ (m) |", "|---:|---:|---:|---:|---:|"]
    for r in out["link"]:
        L.append(f"| {r['range_nm']:.1f} | {r['received_dbm']:.0f} | {r['snr_db']:.0f} | {sig(r['angle_sigma_deg'])} "
                 f"| {sig(r['position_sigma_m'])} |")
    worst = min(r["snr_db"] for r in out["link"])
    if worst > 30:
        L += ["", f"Thermal noise is not the limit: a cooperative reply gives at least {worst:.0f} dB SNR here, so "
              "the angle accuracy of a real installation is set by calibration bias, multipath near the ground and "
              "the reply's pulse timing. Treat the angle σ in the Monte Carlo as that bias/multipath budget."]
    if "autoland" in out:
        L += ["", "## Autoland on fused navigation (EKF: GNSS + ground radar + baro + radio altimeter, IMU-driven)", "",
              "| Scenario | Landed | In touchdown box | Touchdown (m past thr.) | Sink at touchdown (m/s) "
              "| GNSS excluded | Honest sensor excluded |", "|---|---:|---:|---|---:|---:|---:|"]
        for r in out["autoland"]:
            honest = max(r["excluded_radar_share"], r["excluded_baro_share"], r["excluded_radalt_share"])
            spread = (f"{r['touchdown_mean_m']:.0f} ± {r['touchdown_sigma_m']:.0f}"
                      if r["landed_share"] > 0 and r["touchdown_sigma_m"] == r["touchdown_sigma_m"] else "–")
            sink = f"{r['sink_mean_ms']:.1f}" if r["landed_share"] > 0 else "–"
            L.append(f"| {r['scenario']} | {100 * r['landed_share']:.0f} % | {100 * r['in_box_share']:.0f} % | "
                     f"{spread} | {sink} | {100 * r['excluded_gnss_share']:.0f} % | {100 * honest:.0f} % |")
        L += ["", "Innovation gating can exclude the honest sensors when a precise source drifts slowly (it drags the "
              "estimate with it); the solution-separation bank tests whole solutions with one sensor left out and "
              "excludes the faulty one."]
    L += ["", "Model results with the card's stated sensor parameters, not equipment data. Multipath near the "
          "ground, datalink latency and wrong-aircraft association are not modelled.", ""]
    return "\n".join(L)


def figures(out: dict, series: dict, card: dict, folder: Path) -> None:
    import datawiz as dw
    S = dw.Seti(str(folder / "approach.seti.json"), hedef="sunum-tam")
    S.nicelik("dev95", "Deviation at the gate, P95", "m", eksen="x")
    S.nicelik("source", "Navigation source", None, eksen="y")
    S.nicelik("t", "Time on approach", "s", eksen="x")
    S.nicelik("vdev", "Vertical deviation from the path", "m", eksen="y")
    S.nicelik("range", "Distance from the ground sensor", "NM", eksen="x")
    S.nicelik("poserr", "Position error for the angle error", "m", eksen="y")
    for n in ("Vertical", "Lateral", "No monitor", "Monitored"):
        S.varlik(n)
    S.nicelik("dist", "Distance to the threshold", "km", eksen="x")
    S.nicelik("hgt", "True height above the threshold", "m", eksen="y")
    if "autoland" in series:
        S.varlik("Separation FDE")
        S.varlik("Innovation FDE")
        S.varlik("3° path", baglam=True)
    angles = [f"{a:g}°" for a in card["angle_accuracies_deg"]]
    for i, n in enumerate(angles):                  # the middle accuracy is the design point; the others are context
        S.varlik(n, baglam=(i != len(angles) // 2))
    for _ in range(2):
        _slides(S, out, series, card, folder, angles)
        if S.d.get("kenar_mm"):
            break
        left, bottom, right, top = S.kenar_oner()
        S.kenar(left, bottom, right + 14.0, top)          # room for the direct labels at the line ends


def _slides(S, out: dict, series: dict, card: dict, folder: Path, angles: list[str]) -> None:
    import datawiz as dw
    rows = sorted(out["sources"], key=lambda r: r["vertical_p95_m"], reverse=True)
    fig, ax = S.figur(oran=0.55)
    yy = np.arange(len(rows))
    # the two axes sit 0.12 row apart inside each row, so equal values (radar 0.1°) do not hide one another
    ax.scatter([r["vertical_p95_m"] for r in rows], yy + 0.12, **S.stil("Vertical", tur="sacilim"))
    ax.scatter([r["lateral_p95_m"] for r in rows], yy - 0.12, **S.stil("Lateral", tur="sacilim"))
    ax.set_yticks(yy, [r["source"] for r in rows])
    ax.set_xlim(0, max(max(r["vertical_p95_m"], r["lateral_p95_m"]) for r in rows) * 1.1)
    S.eksen(ax, x="dev95", y="source")
    dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(folder / "A1_gate_accuracy"), sessiz=True)

    s = out["spoof"]
    fig, ax = S.figur(oran=0.55)
    for key, name in (("blind", "No monitor"), ("guard", "Monitored")):
        r = series[key]
        ax.plot(r.t, r.vertical_dev, **S.stil(name))
    S.eksen(ax, x="t", y="vdev")
    dw.etiket.cizgi_sonu(ax)
    if s["alarm_t_s"] is not None:
        dw.notlar.bolge(ax, s["ramp_start_s"], s["alarm_t_s"])
        dw.notlar.ok(ax, ((s["ramp_start_s"] + s["alarm_t_s"]) / 2, 0.5 * max(series["blind"].vertical_dev)),
                     f"spoofed, undetected {s['detection_delay_s']:.0f} s", nokta=False)
    else:
        dw.notlar.referans(ax, x=s["ramp_start_s"], metin="spoof starts")
    S.kaydet(fig, str(folder / "A2_spoof_monitor"), sessiz=True)

    fig, ax = S.figur(oran=0.55)
    rng = np.linspace(0.3, 10.0, 60)
    for a, n in zip(card["angle_accuracies_deg"], angles, strict=True):
        ax.plot(rng, rng * NM * math.radians(a), **S.stil(n))
    S.eksen(ax, x="range", y="poserr")
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, None)
    dw.etiket.cizgi_sonu(ax)
    gate_nm = (card["gate_ft"] * A.FT / math.tan(math.radians(card["runway"]["glide_path_deg"]))) / NM
    dw.notlar.referans(ax, x=gate_nm, metin=f"{card['gate_ft']} ft on the path")
    S.kaydet(fig, str(folder / "A3_angle_error_range"), sessiz=True)

    if "autoland" in series:
        rw = card["runway"]
        rwy = A.Runway(rw["lat"], rw["lon"], rw["elevation_m"], rw["course_deg"],
                       glide_path_deg=rw["glide_path_deg"], tch=rw["tch_m"])
        fig, ax = S.figur(oran=0.55)
        sep = series["autoland"]["separation"]
        km = sep.true[:, 0] / 1000
        ax.plot(km, A.glide_path_height(rwy, np.maximum(sep.true[:, 0], rwy.gpip)), **S.stil("3° path"))
        lines = []
        for mode, name in (("separation", "Separation FDE"), ("innovation", "Innovation FDE")):
            r = series["autoland"][mode]
            keep = r.true[:, 0] >= km.min() * 1000 - 1.0          # the unlanded run circles on; show the approach
            lines += ax.plot(r.true[keep, 0] / 1000, r.true[keep, 2], **S.stil(name))
        ax.invert_xaxis()
        ax.set_ylim(bottom=0)
        S.eksen(ax, x="dist", y="hgt")
        dw.etiket.cizgi_sonu(ax, lines)
        S.kaydet(fig, str(folder / "A4_autoland_fde"), sessiz=True)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if wants_help(argv):
        print(console_text(__doc__))
        return 0 if argv else 2
    path = Path(argv[0])
    card = json.loads(path.read_text(encoding="utf-8"))
    protect_streams()
    out, series = run(card)
    folder = path.parent / "out" / path.stem
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    (folder / "result.md").write_text(markdown(out), encoding="utf-8")
    progress("drawing and auditing the slide figures")
    figures(out, series, card, folder)
    errors, audit = audit_summary(folder)
    best = min(out["sources"], key=lambda r: r["vertical_p95_m"])
    sp = out["spoof"]
    caught = (f"the spoof was caught after {sp['detection_delay_s']:.0f} s" if sp["alarm_t_s"] is not None
              else "the spoof was NOT caught")
    print(console_text(markdown(out)))
    print(console_text(audit))
    print(console_text(f"Result: {best['source']} holds {best['vertical_p95_m']:.1f} m (P95, vertical) at the gate and "
                       f"{caught}. Next: replace the card's assumed sensor numbers with the brief's and rerun; "
                       f"slides and report are in {folder}"))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
