"""Phase logic of the alert unit as one block diagram (report Figure 3; replaces the old Table 2 and its paragraph).

    python -I 02_EASA/scripts/easa_phase_diagram.py   # → 02_EASA/outputs/figures/P1_phase_logic.{png,pdf} + datawiz audit

FİGÜR BRİFİ (datawiz)
- Message: the unit is always in one phase, and the phase sets which cues run when the canopy is not locked.
- Reader: EASA jury, one glance, printed at the full text width (176 mm) of the report.
- Form: five boxes left to right in flight order, one arrow between neighbours, one return arrow to Taxi.
  Each box: phase name, the condition that enters it (grey), the cues (colour = alert level).
- Colour: grey structure; amber = caution (Taxi), red = warning (Line-up to Airborne). Colour is backed by the words
  "amber"/"red", so the figure reads in grey scale and for colour-blind readers.
- Text: Montserrat (report body font), ≥ 7 pt at print size. No legend: the words carry the meaning.
- Source: the phase table of the report draft (kit/03, 5 Nov) and docs/26 §"Deferral".
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "02_EASA" / "figures_src" / "vendor" / "fonts"
OUT = ROOT / "02_EASA" / "outputs" / "figures" / "P1_phase_logic"
sys.path.insert(0, r"C:\Users\ayber\Desktop\Custom Yetenekler\datawiz\python")

GREY, INK, LINE = "#5f6368", "#202124", "#9aa0a6"
AMBER, RED = "#8a4b00", "#a8201a"  # text colours with >= 4.5:1 contrast on their tinted box
# alert level -> (box fill, header band, border); grey = no alert, amber = caution, red = warning
LEVEL = {"none": ("#f6f7f8", "#e1e4e8", "#b8bec7"), "amber": ("#fff6e8", "#fbd38d", "#e0a23a"),
         "red": ("#fdf0ef", "#f7b4ae", "#d9625a")}
PHASES = [  # name, entered when, cue lines, text colour, level
    ("Parked", "engine off", ["no alert", "green only if locked"], GREY, "none"),
    ("Taxi", "engine running", ["amber lamp", "one chime"], AMBER, "amber"),
    ("Line-up", "lever switch or MAP\nabove run-up, GS < 5 kt", ["red lamp", "voice", "belt pad"], RED, "red"),
    ("Take-off roll", "GS 5 kt or more,\nstill armed", ["red lamp, voice", "belt pad below 30 kt", "new voice held", "from 40 kt"], RED, "red"),
    ("Airborne", "IAS > 55 kt for 5 s\nand GPS > 40 kt", ["red lamp", "new voice held until", "10 s after lift-off"], RED, "red"),
]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import matplotlib.font_manager as fm
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    import datawiz as dw

    for f in FONTS.glob("Montserrat-*.ttf"):
        fm.fontManager.addfont(str(f))
    fig, ax = dw.figur(ortam="makale", hedef="science-cift", yukseklik_mm=40)
    import matplotlib as mpl
    mpl.rcParams["font.family"] = "Montserrat"
    ax.set_position([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    w, gap, top, bot = 17.4, 3.1, 39.2, 10.8
    band = 5.2
    xs = [0.3 + i * (w + gap) for i in range(len(PHASES))]
    for x, (name, enter, cues, col, lev) in zip(xs, PHASES):
        fill, head, edge = LEVEL[lev]
        ax.add_patch(FancyBboxPatch((x, bot), w, top - bot, boxstyle="round,pad=0,rounding_size=1.6",
                                    fc=fill, ec=edge, lw=0.9, zorder=1))
        ax.add_patch(FancyBboxPatch((x + 0.45, top - band - 0.45), w - 0.9, band, boxstyle="round,pad=0,rounding_size=1.2",
                                    fc=head, ec="none", zorder=2))
        cx = x + w / 2
        ax.text(cx, top - 0.45 - band / 2, name, ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK,
                family="Montserrat", zorder=3)
        ax.text(cx, top - band - 1.9, enter, ha="center", va="top", fontsize=7.2, color=GREY, family="Montserrat",
                linespacing=1.15, zorder=3)
        ax.plot([x + 2.0, x + w - 2.0], [top - 14.2, top - 14.2], color=edge, lw=0.6, zorder=3)
        for k, c in enumerate(cues):
            ax.text(cx, top - 15.3 - k * 3.2, c, ha="center", va="top", fontsize=7.2, color=col,
                    family="Montserrat", fontweight="medium", zorder=3)
    mid = (top + bot) / 2
    arrow = dict(arrowstyle="simple,head_length=0.9,head_width=0.9,tail_width=0.35", mutation_scale=9,
                 fc="#7a8089", ec="none", zorder=4)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        ax.add_patch(FancyArrowPatch((x0 + w + 0.35, mid), (x1 - 0.35, mid), **arrow))
    # return path: Airborne back to Taxi, one rounded arrow under the boxes
    xa, xt = xs[4] + w / 2, xs[1] + w / 2
    from matplotlib.path import Path as MPath
    yb, r = 6.4, 1.6  # bottom of the U and corner radius (axis units)
    verts = [(xa, bot - 0.2), (xa, yb + r), (xa, yb), (xa - r, yb), (xt + r, yb), (xt, yb), (xt, yb + r), (xt, bot - 0.3)]
    codes = [MPath.MOVETO, MPath.LINETO, MPath.CURVE3, MPath.CURVE3, MPath.LINETO, MPath.CURVE3, MPath.CURVE3, MPath.LINETO]
    ax.add_patch(FancyArrowPatch(path=MPath(verts, codes), arrowstyle="-|>,head_length=0.5,head_width=0.3",
                                 mutation_scale=9, color="#7a8089", lw=1.1, zorder=4))
    ax.text((xa + xt) / 2, 3.4, "back to Taxi: both arming inputs idle with IAS below 30 kt, "
            "or IAS and GPS speed below 30 kt for 5 s",
            ha="center", va="center", fontsize=7.2, color=GREY, family="Montserrat", zorder=5,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none"))
    res = dw.kaydet(fig, str(OUT), bicimler=("pdf", "png"), hedef="science-cift", rotus=False)
    return 1 if res.get("hata") else 0


if __name__ == "__main__":
    raise SystemExit(main())
