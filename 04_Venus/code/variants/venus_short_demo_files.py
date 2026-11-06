#!/usr/bin/env python3
"""Design and simulator files for the 0.5 kg short demonstrator. Variant only: the baseline in ``outputs/`` does not change.

Reuses the v0.7 builders (``venus_variant_v07``) with a different closed design. Payload becomes a flight camera and
recorder [Y]. No dives. Release at cos z 0.94 so the array covers hover for the whole demonstration [K].

    python 04_Venus/code/variants/venus_short_demo_files.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import venus_short_demo as SD  # noqa: E402
import venus_variant_v07 as V7  # noqa: E402

BU, S = V7.BU, V7.S
OUT = SD.OUT / "files_0p5kg"
PAYLOAD_KG, PAYLOAD_W = 0.5, 5.0
H0_DEG = SD.LATE_RELEASE_DEG
V7.VAR, V7.TMP, V7.VERSION = OUT, Path("D:/tmp_ideathon/venus_short"), "0.8"
V7.ME = "python 04_Venus/code/variants/venus_short_demo_files.py"
# simülatör taraması 14S7P, 2C 46,9 A: cos z 0,65 için 43,4 A nominal, 45,1 A yüksek; 0,60 sınırı aşar (submission/report_build/sim_release_floor.json)
RELEASE_FLOOR = 0.65
V7.RELEASE_MIN_MU0 = RELEASE_FLOOR


def vehicle() -> dict:
    raw = json.loads(BU.CURVES.read_text(encoding="utf-8"))
    ms = BU.build_models(raw, S.close(2.6, 70.0), BU._points())
    nom, prof = ms["nominal"], SD.NO_DIVES
    d_rec = BU.close_with_interaction(nom, payload_kg=PAYLOAD_KG, payload_W=PAYLOAD_W)
    tab = BU.power_table(d_rec, nom, prof)
    fl, horizon = BU.tuned_flight(d_rec, tab, prof, H0_DEG)
    case = BU.summarise(d_rec, tab, fl, horizon, H0_DEG)
    case["_flight"] = fl
    d = replace(d_rec, system=BU.isolated_system(d_rec), P_hover_elec_W=case["hover_W"], P_bucket_elec_W=case["loiter_W"],
                V_bucket=case["loiter_speed_m_s"], sustain_mu0_hover=case["mu0_hover"], sustain_mu0_loiter=case["mu0_loiter"])
    return {"d": d, "d_rec": d_rec, "case": case, "tab": tab, "prof": prof, "nom": nom}


def demo_doc(doc: dict) -> dict:
    """Turn the science text of the design document into the demonstrator."""
    doc["name"] = "VESPER-D: short rotorcraft flight demonstrator"
    steps = {s["step"]: s for s in doc["deployment_sequence"]}
    t9 = steps[9]["time_s"]
    steps[9]["name"] = "Descend at 1.5 m/s with 3.5 m/s forward to the 55 km cruise level, on sunlight; begin the demonstration"
    steps[10]["name"] = "Demonstration block: hover hold, forward flight, turns and altitude steps, 6 h after release [Y]"
    steps[10]["time_s"] = round(t9 + 3600.0, 0)
    steps[11]["name"] = "Extended flight until the sun is too low, then a controlled descent until the battery limit"
    pay = next(c for c in doc["vehicle"]["components"] if c["id"] == "payload")
    pay.update(name="Flight camera and data recorder", label="Flight camera", material="sapphire window, sealed Ti housing",
               size_m=[0.16, 0.16, 0.10], position_m=[0.0, 0.0, -0.21],
               note="proves the flight: video and flight log to the relay orbiter; no science objective [Y]")
    doc["operating_band"]["rationale"] = doc["operating_band"]["rationale"].split(";")[0] + "; battery charge window holds at 53-58 km"
    doc["note"] += " SHORT DEMONSTRATOR VARIANT: 0.5 kg payload, no dives, not confirmed by the team."
    return doc


def demo_ops(doc: dict) -> dict:
    """Görev izi: gösterim bloğu. Saat seyir irtifasına varıştan sayılır; sayfa görevi 55 km'de başlatır."""
    o = doc["operations"]
    t_c = next(e["t_h"] for e in o["events"] if e["event"] == "cruise altitude reached")
    rows = o["series_hourly"]
    keys = ("altitude_km", "battery_Wh", "solar_W", "demand_W", "cos_zenith", "interior_C")

    def at(t: float) -> dict:
        a = max((r for r in rows if r["t_h"] <= t), key=lambda r: r["t_h"])
        b = min((r for r in rows if r["t_h"] >= t), key=lambda r: r["t_h"])
        f = 0.0 if b["t_h"] == a["t_h"] else (t - a["t_h"]) / (b["t_h"] - a["t_h"])
        return {k: round(a[k] + f * (b[k] - a[k]), 3) for k in keys}

    t_end = SD.DEMO_H - t_c
    marks = [0.0, 1.0, 2.0, 3.0, 4.0, t_end]
    start = rows[2]                                     # t = 2 h: ilk tam seyir satırı; varış anı iniş satırına karışmasın
    series = [{"t_h": round(t, 2), **(at(max(t + t_c, start["t_h"])))} for t in marks]
    for r in series:
        r["altitude_km"] = 55.0
    o.update(series_hourly=series, release_hour_angle_deg=H0_DEG, mission_days=round(SD.DEMO_H / 24.0, 2), solar_sustained_hours=SD.DEMO_H,
             drift_distance_km=round(o["drift_speed_m_s"] * 3.6 * SD.DEMO_H, 0), time_origin=f"cruise reached, {t_c:.2f} h after release",
             events=[{"t_h": 0.0, "event": "demonstration starts at 55.0 km", "kind": "release", "altitude_km": 55.0},
                     {"t_h": round(t_end, 2), "event": "demonstration complete at 55.0 km", "kind": "sunset", "altitude_km": 55.0}])
    steps = {x["step"]: x for x in doc["deployment_sequence"]}
    steps[11].update(name="Demonstration complete; any further flight is a bonus, not a mission goal", altitude_km=55.0, time_s=round(steps[8]["time_s"] + SD.DEMO_H * 3600.0, 0))
    return doc


def main() -> int:
    if "--yalniz-ops" in sys.argv:
        f = OUT / "design.json"
        V7._write(f, json.dumps(demo_ops(json.loads(f.read_text(encoding="utf-8"))), indent=1, ensure_ascii=False))
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    V7.TMP.mkdir(parents=True, exist_ok=True)
    m = vehicle()
    d, case = m["d"], m["case"]
    res = V7.vehicle_chain(m)
    gust = BU.gust_study(d, case["loiter_speed_m_s"], 8)
    gust_mc = BU.gust_mission(d, m["tab"], m["prof"], H0_DEG, case["sunset_horizon_h"], case["loiter_speed_m_s"], 8)
    with V7.patched(res):
        c = V7.VFN.compute()
    V7.corrected(c, m, gust, gust_mc)
    orijinal = V7.DES.design_document

    def tam_toplam(b=None):
        """Toplam kütle 3 ondalıkla: v0.7 denetimi 0,0005 kg ister, tasarım dosyası 2 ondalığa yuvarlar."""
        out = orijinal(b)
        bd = d.breakdown
        rot = next(x for x in out["vehicle"]["components"] if x["id"] == "rotors")
        kalan = sum(x["mass_kg"] for x in out["vehicle"]["components"] if x["id"] != "rotors")
        out["vehicle"]["total_mass_kg"] = round(kalan + round(bd["blades+hubs"] + bd["motors"] + bd["ESCs"], 3), 3)
        del rot
        return out

    with V7.patched(res), V7.mock.patch.object(V7.DES, "design_document", tam_toplam):
        doc = demo_ops(demo_doc(V7.design_doc(c, m, res)))
    V7._write(OUT / "design.json", json.dumps(doc, indent=1, ensure_ascii=False))
    with V7.patched(res, doc):
        sim, _ = V7.sim_doc(c, m, doc, gust)
    V7._write(OUT / "sim_params.json", json.dumps(sim, indent=1, ensure_ascii=False))
    print(f"{doc['vehicle']['total_mass_kg']} kg, components {sum(x['mass_kg'] for x in doc['vehicle']['components']):.3f} kg, "
          f"gust thrust peak {gust['A_plus_C_loiter']['dT_peak_max_over_W']:.2f} W, flight {case['flight_h']:.1f} h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
