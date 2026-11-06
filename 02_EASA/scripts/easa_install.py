"""EASA retrofit installation figures: electrical schematic (E1) and sensor location sketch (M1).

    python 02_EASA/scripts/easa_install.py

Schematic, not to scale. Geometry facts from AAIB-28120 p. 8-10 (three steel shoot bolts on the canopy frame engage
roller lugs on the fuselage along the LEFT cockpit edge; canopy hinged on the right; bolt end a 15 mm ramp with 5 mm
rise; handles 70 mm locked / 60 mm partial) [D, `research/R0_AAIB_G-MIIL_report.md`]. Everything else (bracket
form, sensor gap, wire types, input choices) is our design [Y], described in `docs/28_retrofit_installation.md`.
Writes `02_EASA/outputs/install/` (PNG + PDF + datawiz audit, set `install.seti.json`).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from day_common import protect_streams  # noqa: E402

OUT = ROOT / "02_EASA" / "outputs" / "install"
NEW, OLD, EDGE_NEW, EDGE_OLD = "#dbe9f5", "#f2f2f2", "#0072b2", "#7f7f7f"


def main() -> int:
    protect_streams()
    import datawiz as dw
    import matplotlib.patches as mp

    OUT.mkdir(parents=True, exist_ok=True)
    S = dw.Seti(str(OUT / "install.seti.json"), hedef="sunum-tam")

    def box(ax, x, y, w, h, text, new=True, bold=False):
        ax.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.012",
                                       facecolor=NEW if new else OLD, edgecolor=EDGE_NEW if new else EDGE_OLD,
                                       linewidth=1.5 if new else 1))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontweight="bold" if bold else "normal")

    def arrow(ax, a, b, new=True, style="-|>", ls="-"):
        ax.annotate("", xy=b, xytext=a, arrowprops={"arrowstyle": style, "color": EDGE_NEW if new else EDGE_OLD,
                                                    "lw": 1.4 if new else 1, "linestyle": ls})

    # E1 — electrical schematic (block level)
    fig, ax = S.figur(oran=0.56)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.10, 0.96, "Inputs", ha="center", fontweight="bold")
    ax.text(0.50, 0.96, "Alert unit", ha="center", fontweight="bold")
    ax.text(0.88, 0.96, "Outputs", ha="center", fontweight="bold")
    box(ax, 0.01, 0.70, 0.19, 0.19, "4 sensors\n(NAMUR,\n2 wires each)")
    box(ax, 0.01, 0.47, 0.19, 0.16, "Throttle lever\nswitch")
    box(ax, 0.01, 0.26, 0.19, 0.16, "MAP, rpm,\nIAS, GPS")
    box(ax, 0.01, 0.04, 0.19, 0.16, "Bus, 5 A\nbreaker", new=False)
    box(ax, 0.36, 0.14, 0.28, 0.72, "line monitor\n\nphase logic\n\nhardware AND\n(green)\n\nself-test\nevent log")
    outs = [("3-colour lamps", 0.76), ("Audio panel\nalert input", 0.58), ("Knob shaker", 0.42),
            ("Gate solenoid", 0.26), ("EFIS discrete\n(optional)", 0.08)]
    for text, y in outs:
        box(ax, 0.78, y, 0.21, 0.13, text, new="optional" not in text)
        arrow(ax, (0.64, min(max(y + 0.065, 0.2), 0.8)), (0.775, y + 0.065))
    for y in (0.795, 0.55, 0.34):
        arrow(ax, (0.205, y), (0.355, y))
    arrow(ax, (0.205, 0.12), (0.355, 0.20), new=False)
    S.kaydet(fig, str(OUT / "E1_electrical_schematic"), sessiz=True)

    # M1 — sensor locations, top view of the left cockpit rail (schematic, not to scale) + side detail
    fig, ax = S.figur(oran=0.56)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.30, 0.96, "Left rail, top view (not to scale)", ha="center", fontweight="bold")
    ax.text(0.80, 0.96, "One lug, side view", ha="center", fontweight="bold")
    ax.add_patch(mp.Rectangle((0.03, 0.58), 0.54, 0.10, facecolor=OLD, edgecolor=EDGE_OLD))
    ax.text(0.30, 0.74, "canopy frame (moves)", ha="center", va="center")
    ax.add_patch(mp.Rectangle((0.03, 0.40), 0.54, 0.10, facecolor=OLD, edgecolor=EDGE_OLD))
    ax.text(0.30, 0.33, "fuselage rim (fixed)", ha="center", va="center")
    ax.plot([0.03, 0.57], [0.54, 0.54], color="#d55e00", lw=1.4, ls="--")
    for x, lab in ((0.10, "front"), (0.30, "centre"), (0.50, "rear")):
        ax.add_patch(mp.Rectangle((x - 0.012, 0.50), 0.024, 0.08, facecolor="#7f7f7f", edgecolor="#4d4d4d"))
        ax.add_patch(mp.Rectangle((x - 0.03, 0.42), 0.06, 0.07, facecolor=NEW, edgecolor=EDGE_NEW, lw=1.5))
        ax.text(x, 0.63, lab, ha="center", va="center")
    ax.add_patch(mp.Rectangle((0.375, 0.42), 0.05, 0.07, facecolor=NEW, edgecolor=EDGE_NEW, lw=1.5))
    ax.text(0.40, 0.455, "S0", ha="center", va="center", color="#0b3c5d")
    ax.text(0.30, 0.16, "blue = new sensors, fuselage side only\nS0 = seated sensor; dashed = split line",
            ha="center", va="center", color="#0b3c5d")
    # side detail
    ax.add_patch(mp.Rectangle((0.66, 0.55), 0.20, 0.06, facecolor="#7f7f7f", edgecolor="#4d4d4d"))
    ax.text(0.70, 0.66, "shoot bolt (ramp tip)", ha="center", va="center")
    ax.add_patch(mp.Rectangle((0.83, 0.47), 0.10, 0.22, facecolor="#e6e6e6", edgecolor="#4d4d4d", lw=1.2))
    ax.text(0.88, 0.75, "roller lug", ha="center")
    ax.add_patch(mp.Rectangle((0.84, 0.28), 0.08, 0.10, facecolor=NEW, edgecolor=EDGE_NEW, lw=1.5))
    ax.text(0.88, 0.20, "sensor on a\nbracket", ha="center", va="center")
    ax.annotate("", xy=(0.88, 0.47), xytext=(0.88, 0.385),
                arrowprops={"arrowstyle": "<->", "color": EDGE_NEW, "lw": 1.2})
    ax.text(0.70, 0.43, "gap to bolt tip\nat full lock", ha="center", va="center", color="#0b3c5d")
    S.kaydet(fig, str(OUT / "M1_sensor_locations"), sessiz=True)
    for n in ("E1_electrical_schematic", "M1_sensor_locations"):
        print(n + ": " + (OUT / f"{n}.denetim.txt").read_text(encoding="utf-8").splitlines()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
