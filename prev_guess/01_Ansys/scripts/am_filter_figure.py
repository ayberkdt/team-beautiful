"""Figure G2: the same MBB half-beam optimised without and with the AM overhang filter (base plate at the bottom).

    python prev_guess/01_Ansys/scripts/am_filter_figure.py   # ~2 min -> prev_guess/01_Ansys/reports/figures_en/G2_am_filter.*, prev_guess/01_Ansys/scenarios/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402

from aerokit.optimization import topo_mapped as tm  # noqa: E402
from aerokit.optimization import topology as tp  # noqa: E402
from aerokit.optimization.am_filter import AMFilter2D, overhang_violations  # noqa: E402


def main() -> int:
    out = ROOT / "prev_guess" / "01_Ansys" / "scenarios" / "am_filter_demo.json"
    if out.exists() and "--redo" not in sys.argv:            # redraw from the saved runs
        data = json.loads(out.read_text(encoding="utf-8"))["runs"]
        return _figure(data)
    pr = tp.mbb_half(60, 20)
    runs = {"free": tm.topopt_mapped(pr, 0.5, 2.0, move=0.1, max_iter=150),
            "am": tm.topopt_mapped(pr, 0.5, 2.0, move=0.1, max_iter=150, am=AMFilter2D("S", P=80.0, eps=1e-3))}
    data = {k: {"compliance": float(r["compliance_final"]), "violations": overhang_violations(r["xfiz"], "S"),
                "grey_percent": float(r["gray"]), "density": np.asarray(r["xfiz"]).round(3).tolist()}
            for k, r in runs.items()}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"problem": "mbb_half(60, 20), V = 0.5, rmin 2.0, density filter, OC move 0.1, "
                                          "150 iterations, base plate at the bottom, AM filter P 80, eps 1e-3", "runs": data}),
                   encoding="utf-8")
    return _figure(data)


def _figure(data: dict) -> int:
    fig, axs = dw.figur("makale", hedef="genel-cift", oran=0.42, ncols=2)
    c0 = data["free"]["compliance"]
    for ax, key, name in ((axs[0], "free", "No AM filter"), (axs[1], "am", "AM filter, base at the bottom")):
        d = data[key]
        im = ax.imshow(np.asarray(d["density"]), cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
        ax.set_title(f"{name}\n{d['violations']} overhang violations · compliance {d['compliance'] / c0:.2f}×",
                     loc="left")
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
    cb = fig.colorbar(im, ax=list(axs), shrink=0.35, ticks=[0, 0.5, 1])
    cb.set_label("Material density (–)")
    dw.kaydet(fig, str(ROOT / "prev_guess" / "01_Ansys" / "reports" / "figures_en" / "G2_am_filter"), hedef="genel-cift", cvd=False)
    print({k: {kk: v for kk, v in d.items() if kk != "density"} for k, d in data.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
