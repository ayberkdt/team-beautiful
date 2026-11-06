"""Evaluate every screening survivor on every topology layout of ONE run (layouts are material-independent).
python -I analysis/evaluate_layouts.py runs/topo_fixed_bores/result.json   -> analysis/layout_evaluation.{json,md}

Per layout the run stores, for E = 1 Pa: stress_unitE[case] (von Mises outside the hole zones, Pa — independent
of E) and disp_unitE (max |u| × E). For a material: sigma = max_case(stress) × T10 stress factor (if the run
measured one for that layout, else 1), u = disp_unitE / E. Pass: 1.5 × sigma <= Fy and u <= L/400.
Fy/E at 23 °C are the organisers' values [D-org] (pool values for pool survivors); the 300 °C column applies our
catalogue knock-downs [Y] where we have them.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from screening import screen, life_co2, U_LIM, FOS   # noqa: E402

K300 = {"Titanium, near-alpha alloy, Ti-8Al-1Mo-1V, single annealed": (0.683, 0.869),   # (Fty, E) catalogue [Y]
        "Aluminum, 2618, T6": (None, None)}


def main(result_path: str) -> None:
    r = json.loads(Path(result_path).read_text(encoding="utf-8"))
    d = r["details"]
    sf = d.get("stress_factors", {}) or {}
    # the organisers' three: Ti-8-1-1 = screening survivor; 2618 = flagged sensitivity (fails >300 °C);
    # S275N = reference, evaluated only to show the shape-only gain
    rows = screen()
    out = []
    for m in rows:
        E = m["E"] * 1e9
        for lay in d["designs"]:
            s = max(lay["stress_unitE"].values()) * sf.get(lay["label"], 1.0) / 1e6
            u = lay["disp_unitE"] / E * 1e3
            k = K300.get(m["name"], (None, None))
            mass = lay["volume_m3"] * m["rho"]
            rec = dict(material=m["name"], layout=lay["label"], volfrac=lay["volfrac"], mass_kg=mass,
                       sigma_MPa=s, stress_factor=sf.get(lay["label"], 1.0), util=FOS * s / m["Fy"], disp_mm=u,
                       disp_ok=u <= U_LIM, passes=(FOS * s <= m["Fy"] and u <= U_LIM), co2_life_t=life_co2(mass, m) / 1e3,
                       cost_USD=(mass * m["price"]) if m["price"] else None)
            if k[0]:
                rec.update(util_300=FOS * s / (m["Fy"] * k[0]), disp_300=u / k[1],
                           passes_300=(FOS * s <= m["Fy"] * k[0] and u / k[1] <= U_LIM))
            out.append(rec)
    (HERE / "layout_evaluation.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = ["| Material | Layout | Mass (kg) | σ (MPa) | Util. 23 °C | u (mm) | Pass 23 °C | Pass 300 °C | Life CO₂ (t) | Cost (USD) |",
             "|---|---|---:|---:|---:|---:|---|---|---:|---:|"]
    for x in out:
        p3 = {True: "yes", False: "no"}.get(x.get("passes_300"), "n/a")
        cost = f"{x['cost_USD']:.0f}" if x["cost_USD"] else "–"
        lines.append(f"| {x['material']} | {x['layout']} | {x['mass_kg']:.1f} | {x['sigma_MPa']:.0f} | {x['util']:.2f} | "
                     f"{x['disp_mm']:.3f} | {'yes' if x['passes'] else 'no'} | {p3} | {x['co2_life_t']:.1f} | {cost} |")
    best = {}
    for x in out:
        ok = x.get("passes_300", x["passes"]) if x["material"] in K300 and K300[x["material"]][0] else x["passes"]
        if ok and (x["material"] not in best or x["mass_kg"] < best[x["material"]]["mass_kg"]):
            best[x["material"]] = x
    lines += ["", "Lightest passing layout per material:", ""]
    for k, x in sorted(best.items(), key=lambda kv: kv[1]["co2_life_t"]):
        lines.append(f"- {k}: {x['layout']}, {x['mass_kg']:.1f} kg, life CO₂ {x['co2_life_t']:.1f} t, util {x['util']:.2f}, u {x['disp_mm']:.3f} mm")
    (HERE / "layout_evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
