"""Eco-Audit-style figure of a trade-off study: life CO2 by phase, and production with the end-of-life potential apart.

    python prev_guess/01_Ansys/scripts/eco_audit_figure.py prev_guess/01_Ansys/tradeoff/panel_cabin_stiffness.json   # -> prev_guess/01_Ansys/reports/figures_en/G3_*

(a) material + manufacture + use per option (stacked); (b) the production phases at a readable scale, with the
end-of-life potential as its own hatched bar (Granta's Eco Audit shows it beside the life total, never inside it).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402

from aerokit.design import tradeoff as T  # noqa: E402

ROUTE_EN = {"machined": "machined", "machined_TO": "TO + machined", "am_TO": "TO + AM", "sheet_formed": "sheet",
            "autoclave_layup": "autoclave", "thermoplastic_press": "press"}


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else ROOT / "prev_guess" / "01_Ansys" / "tradeoff" / "panel_cabin_stiffness.json"
    res = sorted(T.evaluate(T.load_study(path)), key=lambda r: r.co2_total_kg)
    names = [f"{r.material} {ROUTE_EN.get(r.route, r.route)}" for r in res]
    mat = np.array([r.co2_material_kg for r in res]) / 1000
    proc = np.array([r.co2_production_kg - r.co2_material_kg for r in res]) / 1000
    use = np.array([r.co2_use_kg for r in res]) / 1000
    eol = np.array([r.co2_eol_potential_kg for r in res]) / 1000
    cols = dw.paletler.kategorik()
    fig, axs = dw.figur("makale", hedef="genel-cift", oran=0.55, ncols=2, sharey=True)
    y = np.arange(len(res))
    a, b = axs
    left = np.zeros(len(res))
    for v, name, c in ((mat, "Material", cols[0]), (proc, "Manufacture", cols[1]), (use, "Use (fuel)", "#8c8c8c")):
        a.barh(y, v, left=left, color=dw.renk.alan_tonu(c), edgecolor=c, height=0.6, label=name)
        left = left + v
    a.set_yticks(y, names)
    a.set_xlabel("Life CO₂ (t)")
    a.set_title("(a) Whole life", loc="left")
    left = np.zeros(len(res))
    for v, c in ((mat, cols[0]), (proc, cols[1])):
        b.barh(y, v * 1000, left=left, color=dw.renk.alan_tonu(c), edgecolor=c, height=0.6)
        left = left + v * 1000
    b.barh(y, eol * 1000, color="white", edgecolor="#4d4d4d", hatch="///", height=0.6,
           label="End-of-life potential")
    b.axvline(0, color="#4d4d4d", lw=0.8)
    b.set_xlabel("Production CO₂ and end-of-life potential (kg)")
    b.set_title("(b) Production, end of life apart", loc="left")
    dw.lejant.ortak(fig, [a, b])
    out = ROOT / "prev_guess" / "01_Ansys" / "reports" / "figures_en" / f"G3_eco_audit_{path.stem}"
    dw.kaydet(fig, str(out), hedef="genel-cift", cvd=True)
    for n, m_, p_, u_, e_ in zip(names, mat, proc, use, eol, strict=True):
        print(f"{n:<34} material {1000 * m_:7.1f} kg  manufacture {1000 * p_:7.1f} kg  use {u_:7.2f} t  "
              f"EoL {1000 * e_:7.1f} kg  production share {100 * (m_ + p_) / (m_ + p_ + u_):.2f} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
