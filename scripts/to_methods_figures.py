"""Figures G5 (stress-constrained L-beam vs compliance design) and G6 (density filter vs projection vs robust MBB).

    python scripts/to_methods_figures.py   # reads studies/scenarios/to_methods_study.json -> reports/figures_en/G5_*, G6_*
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402


def _panel(ax, density, title: str):
    im = ax.imshow(np.asarray(density), cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
    ax.set_title(title, loc="left")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return im


def g5(d: dict) -> None:
    s, c = d["stress_l_beam"], d["stress_l_beam"]["compliance_design"]
    fig, axs = dw.figur("makale", hedef="genel-cift", oran=0.5, ncols=2)
    _panel(axs[0], c["density"], f"Stiffest design, {c['mass_g']:.1f} g\npeak stress {c['max_stress_ratio']:.2f} × limit")
    im = _panel(axs[1], s["density"],
                f"Stress-constrained, {s['mass_g']:.1f} g\npeak stress {s['max_stress_ratio']:.2f} × limit")
    cb = fig.colorbar(im, ax=list(axs), shrink=0.35, ticks=[0, 0.5, 1])
    cb.set_label("Material density (–)")
    dw.kaydet(fig, str(ROOT / "reports" / "figures_en" / "G5_stress_l_beam"), hedef="genel-cift", cvd=False)


def g6(d: dict) -> None:
    r = d["robust_mbb"]
    fig, axs = dw.figur("makale", hedef="genel-cift", oran=1.05, nrows=3)
    c0 = r["density"]["compliance"]
    names = (("density", "Density filter"), ("projected", "Projection, η 0.5"),
             ("robust", "Robust, η 0.75 / 0.25"))
    im = None
    for ax, (key, name) in zip(axs, names):
        v = r[key]
        im = _panel(ax, v["density"], f"{name} · volume {v['volume']:.2f} · grey {v['gray']:.1f} % · "
                                      f"compliance {v['compliance'] / c0:.2f}×")
    cb = fig.colorbar(im, ax=list(axs), orientation="horizontal", shrink=0.4, aspect=30, ticks=[0, 0.5, 1])
    cb.set_label("Material density (–)")
    dw.kaydet(fig, str(ROOT / "reports" / "figures_en" / "G6_projection_mbb"), hedef="genel-cift", cvd=False)


def main() -> int:
    d = json.loads((ROOT / "studies" / "scenarios" / "to_methods_study.json").read_text(encoding="utf-8"))
    if "robust_mbb" in d:
        g6(d)
    if "stress_l_beam" in d:
        g5(d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
