"""Figure of the S1 3-D preview: maximum-density projections (top, side, front) for each run.

    python scripts/ge_preview_figure.py   # studies/scenarios/ge_bracket_preview.json -> reports/figures_en/G1_*
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402

DATA = ROOT / "studies" / "scenarios" / "ge_bracket_preview.json"
OUT = ROOT / "reports" / "figures_en" / "G1_ge_preview"
VIEWS = (("top view (z)", 2), ("side view (x)", 0), ("front view (y)", 1))      # (title, projection axis)


def main() -> int:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    nx, ny, nz = d["meta"].get("grid", [40, 24, 14])
    runs = d["runs"]
    fig, axs = dw.figur("makale", hedef="genel-cift", oran=0.55, nrows=len(runs), ncols=3)
    axs = np.atleast_2d(axs)
    im = None
    for i, r in enumerate(runs):
        rho = np.asarray(r["density"], float).reshape(nx, ny, nz)
        for j, (name, axis) in enumerate(VIEWS):
            proj = rho.max(axis=axis)
            ax = axs[i, j]
            im = ax.imshow(proj.T, origin="lower", cmap="Greys", vmin=0, vmax=1, interpolation="nearest",
                           aspect="equal")
            ax.set_xticks([])
            ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(False)
            if i == 0:
                ax.set_title(name, loc="left")
            if j == 0:
                ax.set_ylabel(f"{r['mass_kg']:.2f} kg")
    cb = fig.colorbar(im, ax=list(axs.ravel()), shrink=0.5, ticks=[0, 0.5, 1])
    cb.set_label("Material density (–)")
    dw.kaydet(fig, str(OUT), hedef="genel-cift", cvd=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
