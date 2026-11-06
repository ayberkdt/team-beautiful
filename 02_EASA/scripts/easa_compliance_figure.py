"""Report Figure 5: risk reduction against pilot compliance, drawn wide with a full grid (replaces F7 in the report).

    python -I 02_EASA/scripts/easa_compliance_figure.py   # → 02_EASA/outputs/figures/P2_compliance.{png,pdf} + audit

FİGÜR BRİFİ (datawiz)
- Message: an alert helps much only when the pilot nearly always acts on it; the chosen lap-belt set gives 2.0× at
  c = 0.5 and 71× at c = 1. The gate (rejected) is shown for scale only.
- Data: outputs/tradeoffs/tradeoffs.json → compliance_sweep (O3, O4, O5, O6; c = 0.05 to 1), central values.
- Form: line chart, x = c (linear 0 to 1), y = RF (log, 1× to 2 000×), full light grid in x and y, direct labels at the
  right end, no legend box. Chosen set in the accent colour and thicker; others grey; rejected gate dashed.
- Size: 140 mm wide (elsevier-bucuk profile), Montserrat, ≥ 7 pt at print size.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EASA = ROOT / "02_EASA"
FONTS = EASA / "figures_src" / "vendor" / "fonts"
OUT = EASA / "outputs" / "figures" / "P2_compliance"
sys.path.insert(0, r"C:\Users\ayber\Desktop\Custom Yetenekler\datawiz\python")

ACCENT, GREY, LIGHT, INK = "#2f4fa2", "#6b7280", "#b8bec7", "#202124"
SERIES = [  # key, label, colour, width, style
    ("O6", "+ gate (rejected)", LIGHT, 1.0, (0, (4, 3))),
    ("O5", "+ belt pad (chosen)", ACCENT, 2.0, "-"),
    ("O4", "lamp + voice", GREY, 1.0, "-"),
    ("O3", "lamp only", GREY, 1.0, (0, (1, 1.5))),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import matplotlib as mpl
    import matplotlib.font_manager as fm
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

    import datawiz as dw

    for f in FONTS.glob("Montserrat-*.ttf"):
        fm.fontManager.addfont(str(f))
    sw = json.loads((EASA / "outputs" / "tradeoffs" / "tradeoffs.json").read_text(encoding="utf-8"))["compliance_sweep"]
    c = sw["c"]
    fig, ax = dw.figur(ortam="makale", hedef="elsevier-bucuk", yukseklik_mm=46)
    mpl.rcParams["font.family"] = "Montserrat"
    for k, lab, col, lw, ls in SERIES:
        y = sw[k]
        ax.plot(c, y, color=col, lw=lw, ls=ls, solid_capstyle="round", zorder=3 if k == "O5" else 2)
        ax.text(1.02, y[-1], lab, color=INK if k == "O5" else GREY, fontsize=7.5, va="center", ha="left",
                fontweight="bold" if k == "O5" else "normal", family="Montserrat")
    i = c.index(0.5)
    v = sw["O5"][i]
    ax.plot([0.5], [v], marker="o", ms=4.5, mfc="white", mec=ACCENT, mew=1.4, zorder=4)
    ax.annotate(f"{v:.1f}× at c = 0.5", (0.5, v), xytext=(0.3, v * 7.0), ha="center", fontsize=7.5, color=ACCENT,
                family="Montserrat", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none"),
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8, shrinkA=2, shrinkB=3))
    ax.set_yscale("log")
    ax.set_xlim(0, 1)
    ax.set_ylim(0.9, 2000)
    ax.xaxis.set_major_locator(FixedLocator([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.1f}"))
    ax.yaxis.set_major_locator(FixedLocator([1, 3, 10, 30, 100, 300, 1000]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:,.0f}×".replace(",", " ")))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.grid(True, which="major", axis="both", color="#e3e6ea", lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel("Probability that the pilot acts on a noticed alert (c)", fontsize=7.5, family="Montserrat")
    ax.set_ylabel("Risk reduction (log)", fontsize=7.5, family="Montserrat")
    ax.tick_params(labelsize=7.5)
    fig.set_layout_engine("none")
    ax.set_position([0.105, 0.22, 0.655, 0.74])
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_family("Montserrat")
    res = dw.kaydet(fig, str(OUT), bicimler=("pdf", "png"), hedef="elsevier-bucuk", rotus=False, hizala=False)
    return 1 if res.get("hata") else 0


if __name__ == "__main__":
    raise SystemExit(main())
