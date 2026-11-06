"""views_dimensioned.png/.pdf: front (x-z), right side (y-z) and top (x-y) views, third-angle projection.

Drawn analytically from geom.py (the numbers measured in derived/features.json); every dimension printed is
computed from those numbers at run time. Visible lines thick, tangent edges thin, hidden lines dashed,
centre lines dash-dot.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import geom as G  # noqa: E402

import datawiz as dw  # noqa: E402
import matplotlib as mpl  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon  # noqa: E402

FIG_W, FIG_H = 305.0, 145.0
DRAW_W = 204.0                      # mm of the figure used by the drawing; the rest is the notes column
U0, U1, V0, V1 = -40.0, 1385.0, -178.0, 905.0
INK = "#1a1a1a"
DIMC = "#1e68a9"                    # akademik mavi: dimensions
GREY = "#6b7078"
FS, FS_T = 18, 20
LW_VIS, LW_THIN, LW_DIM = 1.6, 0.6, 0.8
DY_TOP = 431.37 - G.Y0              # top view: v = y + DY_TOP
DU_SIDE = 1001.0 - G.Y0             # side view: u = y + DU_SIDE


def fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s


class Draw:
    def __init__(self, ax):
        self.ax = ax

    def line(self, pts, lw=LW_VIS, color=INK, ls="-", z=3):
        pts = np.asarray(pts, float)
        self.ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=z)

    def hidden(self, pts):
        self.line(pts, lw=0.9, color=GREY, ls=(0, (5, 3)))

    def centre(self, pts):
        self.line(pts, lw=LW_THIN, color=GREY, ls=(0, (14, 3, 2, 3)))

    def thin(self, pts):
        self.line(pts, lw=LW_THIN, color=GREY)

    def arrow(self, a, b, color=DIMC):
        self.ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle="-|>", mutation_scale=13, color=color,
                                          lw=LW_DIM, shrinkA=0, shrinkB=0, zorder=4))

    def dim_h(self, x1, x2, y, refs, text, above=True, gap=5.0, over=5.0):
        """Horizontal dimension between x1 and x2 with its line at height y; refs = (y_ref1, y_ref2)."""
        s = 1 if y > refs[0] else -1
        for x, yr in ((x1, refs[0]), (x2, refs[1])):
            self.line([[x, yr + s * gap], [x, y + s * over]], lw=LW_THIN, color=DIMC)
        xm = (x1 + x2) / 2
        self.arrow((xm, y), (x1, y))
        self.arrow((xm, y), (x2, y))
        self.ax.text(xm, y + (11 if above else -9), text, color=DIMC, fontsize=FS, ha="center",
                     va="bottom" if above else "top", zorder=5)

    def dim_v(self, y1, y2, x, refs, text, left=True, gap=5.0, over=8.0):
        s = 1 if x > refs[0] else -1
        for yy, xr in ((y1, refs[0]), (y2, refs[1])):
            self.line([[xr + s * gap, yy], [x + s * over, yy]], lw=LW_THIN, color=DIMC)
        ym = (y1 + y2) / 2
        self.arrow((x, ym), (x, y1))
        self.arrow((x, ym), (x, y2))
        self.ax.text(x + (-8 if left else 8), ym, text, color=DIMC, fontsize=FS, rotation=90, ha="right" if left
                     else "left", va="center", zorder=5)

    def leader(self, tip, knee, text, right=True):
        """Leader with arrow on the feature, short shoulder, text at the shoulder end."""
        self.line([knee, tip], lw=LW_THIN, color=DIMC, z=4)
        self.arrow(knee, tip)
        end = (knee[0] + (28 if right else -28), knee[1])
        self.line([knee, end], lw=LW_THIN, color=DIMC, z=4)
        self.ax.text(end[0] + (6 if right else -6), end[1], text, color=DIMC, fontsize=FS,
                     ha="left" if right else "right", va="center", zorder=5)


def lug_outline_xz() -> np.ndarray:
    """Front-view outline of a lug from plate top (z = 100) over fillet, flank, top arc, flank, fillet."""
    Rf, Lf = G.FLANK_R, G.FLANK_L

    def arc(c, r, a0, a1, n=50):
        t = np.linspace(a0, a1, n)
        return np.column_stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t)])

    fR = math.atan2(Rf["t_fil"][1] - G.FIL_R[1], Rf["t_fil"][0] - G.FIL_R[0])
    fL = math.atan2(Lf["t_fil"][1] - G.FIL_L[1], Lf["t_fil"][0] - G.FIL_L[0])
    aR = math.atan2(Rf["t_arc"][1] - G.ARC_C[1], Rf["t_arc"][0] - G.ARC_C[0])
    aL = math.atan2(Lf["t_arc"][1] - G.ARC_C[1], Lf["t_arc"][0] - G.ARC_C[0])
    return np.vstack([arc(G.FIL_R, G.R_FIL, -math.pi / 2, fR), arc(G.ARC_C, G.R_ARC, aR, aL),
                      arc(G.FIL_L, G.R_FIL, fL, -math.pi / 2)])


def rounded_rect(x0, y0, x1, y1, r, n=30):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        t = np.radians(np.linspace(a0, a0 + 90, n))
        pts.append(np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)]))
    p = np.vstack(pts)
    return np.vstack([p, p[:1]])


def front(D: Draw) -> None:
    ax = D.ax
    x0, x1, z0, z1 = G.X0, G.X1, G.Z0, G.Z1
    lug = lug_outline_xz()
    D.line(np.vstack([[[x0, z1], [x0, z0], [x1, z0], [x1, z1], [G.FIL_R[0], z1]], lug, [[x0, z1]]]))
    ax.add_patch(Circle(G.PIN, G.R_BORE, fill=False, ec=INK, lw=LW_VIS, zorder=3))
    D.centre([[G.PIN[0] - 48, G.PIN[1]], [G.PIN[0] + 48, G.PIN[1]]])
    D.centre([[G.PIN[0], z0 - 12], [G.PIN[0], G.Z_TOP + 12]])
    for bx in sorted({b[0] for b in G.BOLTS}):
        for xx in (bx - G.R_BORE, bx + G.R_BORE):
            D.hidden([[xx, z0], [xx, z1]])
        D.centre([[bx, z0 - 12], [bx, z1 + 12]])
    # dimensions
    D.dim_h(x0, x1, z0 - 95, (z0, z0), fmt(x1 - x0), above=False)
    D.dim_v(z0, z1, x0 - 50, (x0, x0), fmt(z1 - z0))
    D.dim_v(z0, G.PIN[1], x0 - 130, (x0, G.PIN[0] - G.R_BORE - 10), fmt(G.PIN[1] - z0))
    D.dim_v(z0, G.Z_TOP, x1 + 55, (x1, G.ARC_C[0]), fmt(G.Z_TOP - z0), left=False)
    # radii and bore
    t = math.radians(118)
    D.leader((G.ARC_C[0] + G.R_ARC * math.cos(t), G.ARC_C[1] + G.R_ARC * math.sin(t)), (330, 368),
             f"R{fmt(G.R_ARC)}", right=False)
    Rf = G.FLANK_R
    fR = math.atan2(Rf["t_fil"][1] - G.FIL_R[1], Rf["t_fil"][0] - G.FIL_R[0])
    tm = (fR + (-math.pi / 2)) / 2                     # mid-angle of the right root fillet arc
    D.leader((G.FIL_R[0] + G.R_FIL * math.cos(tm), G.FIL_R[1] + G.R_FIL * math.sin(tm)), (700, 210),
             f"4× R{fmt(G.R_FIL)}")
    tb = math.radians(40)
    D.leader((G.PIN[0] + G.R_BORE * math.cos(tb), G.PIN[1] + G.R_BORE * math.sin(tb)), (625, 288),
             f"2× Ø{fmt(2 * G.R_BORE)}")
    # datum A on the underside
    xa = 400.0
    ax.add_patch(Polygon([[xa - 9, z0], [xa + 9, z0], [xa, z0 - 15]], closed=True, fc=INK, ec=INK, zorder=4))
    D.line([[xa, z0 - 15], [xa, z0 - 34]], lw=LW_THIN)
    ax.add_patch(Polygon([[xa - 19, z0 - 34], [xa + 19, z0 - 34], [xa + 19, z0 - 74], [xa - 19, z0 - 74]],
                         closed=True, fill=False, ec=INK, lw=LW_THIN, zorder=4))
    ax.text(xa, z0 - 54, "A", fontsize=FS, ha="center", va="center", color=INK, zorder=5)


def top(D: Draw) -> None:
    ax = D.ax
    dy = DY_TOP
    rr = rounded_rect(G.X0, G.Y0 + dy, G.X1, G.Y1 + dy, G.R_CORNER)
    D.line(rr)
    for bx, by in G.BOLTS:
        ax.add_patch(Circle((bx, by + dy), G.R_BORE, fill=False, ec=INK, lw=LW_VIS, zorder=3))
        D.centre([[bx - 40, by + dy], [bx + 40, by + dy]])
        D.centre([[bx, by + dy - 38], [bx, by + dy + 38]])
    # lugs: inner faces meet the plate top (visible); tangent edges thin; pin bore hidden
    (ya0, ya1), (yb0, yb1) = G.LUGS
    D.line([[G.FIL_L[0], ya1 + dy], [G.FIL_R[0], ya1 + dy]])
    D.line([[G.FIL_L[0], yb0 + dy], [G.FIL_R[0], yb0 + dy]])
    xs = [G.FIL_L[0], G.FLANK_L["t_fil"][0], G.FLANK_L["t_arc"][0], G.FLANK_R["t_arc"][0],
          G.FLANK_R["t_fil"][0], G.FIL_R[0]]
    for x in xs:
        for y0, y1 in G.LUGS:
            D.thin([[x, y0 + dy], [x, y1 + dy]])
    for y0, y1 in G.LUGS:
        for xx in (G.PIN[0] - G.R_BORE, G.PIN[0] + G.R_BORE):
            D.hidden([[xx, y0 + dy], [xx, y1 + dy]])
    D.centre([[G.PIN[0], G.Y0 + dy - 15], [G.PIN[0], G.Y1 + dy + 15]])
    # dimensions
    (b1x, b1y), (_, b2y) = G.BOLTS[0], G.BOLTS[1]
    b3x = G.BOLTS[2][0]
    D.dim_h(b1x, b3x, G.Y1 + dy + 55, (b2y + dy + 43, b2y + dy + 43), fmt(b3x - b1x))
    D.dim_v(b1y + dy, b2y + dy, G.X1 + 55, (b3x + 45, b3x + 45), fmt(b2y - b1y), left=False)
    c45 = math.cos(math.radians(45))
    cx, cy = G.X1 - G.R_CORNER, G.Y1 - G.R_CORNER + dy
    D.leader((cx + G.R_CORNER * c45, cy + G.R_CORNER * c45), (cx + G.R_CORNER * c45 + 60, cy + G.R_CORNER + 40),
             f"4× R{fmt(G.R_CORNER)}")
    # 4x bore callout between the two left bores, short arrow up to the upper one
    ym = (b1y + b2y) / 2 + dy
    D.ax.text(b1x, ym, f"4× Ø{fmt(2 * G.R_BORE)}", color=DIMC, fontsize=FS, ha="center", va="center", zorder=5)
    tb = math.radians(-70)
    D.arrow((b1x + 8, ym + 30), (b1x + G.R_BORE * math.cos(tb), b2y + dy + G.R_BORE * math.sin(tb)))


def side(D: Draw) -> None:
    du = DU_SIDE
    (ya0, ya1), (yb0, yb1) = G.LUGS
    z0, z1, zt = G.Z0, G.Z1, G.Z_TOP
    U = lambda y: y + du  # noqa: E731
    D.line([[U(ya0), z0], [U(yb1), z0], [U(yb1), zt], [U(yb0), zt], [U(yb0), z1], [U(ya1), z1], [U(ya1), zt],
            [U(ya0), zt], [U(ya0), z0]])
    # tangent edges (arc/flank, flank/fillet, fillet/plate) across each lug
    for zz in (G.FLANK_R["t_arc"][1], G.FLANK_R["t_fil"][1], z1):
        for y0, y1 in G.LUGS:
            D.thin([[U(y0), zz], [U(y1), zz]])
    for y0, y1 in G.LUGS:
        for zz in (G.PIN[1] - G.R_BORE, G.PIN[1] + G.R_BORE):
            D.hidden([[U(y0), zz], [U(y1), zz]])
    D.centre([[U(ya0) - 15, G.PIN[1]], [U(yb1) + 15, G.PIN[1]]])
    for by in sorted({b[1] for b in G.BOLTS}):
        for yy in (by - G.R_BORE, by + G.R_BORE):
            D.hidden([[U(yy), z0], [U(yy), z1]])
        D.centre([[U(by), z0 - 12], [U(by), z1 + 12]])
    # dimensions: chain over the lugs, overall below
    yl = zt + 55
    D.dim_h(U(ya0), U(ya1), yl, (zt, zt), fmt(ya1 - ya0))
    D.dim_h(U(ya1), U(yb0), yl, (zt, zt), fmt(yb0 - ya1))
    D.dim_h(U(yb0), U(yb1), yl, (zt, zt), fmt(yb1 - yb0))
    D.dim_h(U(G.Y0), U(G.Y1), z0 - 95, (z0, z0), fmt(G.Y1 - G.Y0), above=False)


def main() -> None:
    vc = json.loads((G.HERE / "out" / "volume_check.json").read_text())
    fig, ax = dw.figur("sunum", hedef="sunum-tam", yukseklik_mm=FIG_H, palet="akademik")
    mpl.rcParams["savefig.dpi"] = 300
    ax.set_position([0, 0, DRAW_W / FIG_W, 1])
    ax.set_xlim(U0, U1)
    ax.set_ylim(V0, V1)
    ax.set_aspect("equal", adjustable="box", anchor="W")
    ax.set_axis_off()
    D = Draw(ax)
    front(D)
    top(D)
    side(D)
    # view names
    ax.text(G.X0, V0 + 4, "Front view (x–z)", fontsize=FS_T, fontweight="bold", ha="left", va="bottom",
            color=INK)
    ax.text(DU_SIDE + G.Y0, V0 + 4, "Right view (y–z)", fontsize=FS_T, fontweight="bold", ha="left",
            va="bottom", color=INK)
    ax.text(DU_SIDE + G.Y0, DY_TOP + 200, "Top view (x–y)", fontsize=FS_T, fontweight="bold", ha="left",
            va="bottom", color=INK)
    # notes column
    tx = fig.add_axes([DRAW_W / FIG_W, 0, 1 - DRAW_W / FIG_W, 1])
    tx.set_axis_off()
    tx.set_xlim(0, 1)
    tx.set_ylim(0, 1)
    notes = [
        ("Initial bracket (S275N)", INK, FS_T, "bold"),
        ("Dimensions in mm", GREY, FS, "normal"),
        ("Third-angle projection", GREY, FS, "normal"),
        (None, None, None, None),
        ("Datum A = underside", INK, FS, "normal"),
        (f"(CAD z = {fmt(G.Z0)}).", INK, FS, "normal"),
        (f"Pin axis: CAD z = {fmt(G.PIN[1])},", INK, FS, "normal"),
        (f"i.e. {fmt(G.PIN[1] - G.Z0)} above A.", INK, FS, "normal"),
        (None, None, None, None),
        (f"Lugs {fmt(G.LUGS[0][1] - G.LUGS[0][0])} and {fmt(G.LUGS[1][1] - G.LUGS[1][0])} thick", INK, FS,
         "normal"),
        (f"Flanks at {G.FLANK_R['angle_deg']:.1f}° to the plate", INK, FS, "normal"),
        (f"Volume {vc['exact_brep_volume_m3']:.6f} m³", INK, FS, "normal"),
        (f"= {vc['exact_mass_kg_at_7850']:.2f} kg at 7850 kg/m³", INK, FS, "normal"),
    ]
    y = 0.96
    for t, c, s, w in notes:
        if t is None:
            y -= 0.03
            continue
        tx.text(0.04, y, t, color=c, fontsize=s, fontweight=w, ha="left", va="top")
        y -= 0.072
    tx.text(0.04, 0.03, "Source: derived/features.json\n(organisers' Discovery file)", color=GREY, fontsize=FS,
            ha="left", va="bottom", linespacing=1.15)
    rep = dw.kaydet(fig, str(G.VIS / "views_dimensioned"), bicimler=("png", "pdf", "svg"), hedef="sunum-tam",
                    cvd=False)
    print(rep["rapor"])


if __name__ == "__main__":
    main()
