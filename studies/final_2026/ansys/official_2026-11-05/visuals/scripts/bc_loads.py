"""bc_loads.png/.pdf: supports and loads of the official set-up on the initial bracket (no FEA result).

Every value comes from setup/setup_official_fixed_bores.json (read at run time) and boundary_conditions.md.
Left: 3-D view (pyvista render; fixed-support faces blue, bearing faces red) with arrows, symbols and labels
drawn in matplotlib at the projected 3-D positions, so the datawiz audit measures every label.
Right: pin-bore detail in the x-z plane (view along +y) for the bearing distribution and My, plus the load cases.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import geom as G  # noqa: E402
import render3d as R  # noqa: E402

import datawiz as dw  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon  # noqa: E402

TEMA = dw.paletler.tema("akademik")
C_SUP, C_F, C_M = TEMA["kategorik"][0], TEMA["kategorik"][1], TEMA["kategorik"][3]   # mavi, vermilyon, eflatun
INK = TEMA["murekkep"]
GREY = "#555a61"
STEEL = "#c3c8ce"
FIG_W, FIG_H = 305.0, 145.0            # datawiz sunum-tam, mm
IMG_W_MM = 178.0
DPI = 300
SS = 2
FS_L, FS_M, FS_S = 22, 20, 18          # label / row / note (3 sizes)


def read_setup() -> dict:
    S = json.loads(G.SETUP.read_text(encoding="utf-8"))
    holes = {h["id"]: h for h in S["holes"]}
    lc = {c["name"].split()[0]: c for c in S["load_cases"]}
    f1 = lc["LC1a"]["loads"][0]["force_N"]
    f2 = lc["LC1b"]["loads"][0]["force_N"]
    m = lc["LC2"]["loads"][0]["moment_Nm"]
    assert all(L["force_N"][2] == f1[2] for L in lc["LC1a"]["loads"] + lc["LC1b"]["loads"])
    assert all(L["type"] == "bearing" for L in lc["LC1a"]["loads"])
    return {
        "holes": holes,
        "supports": [s["hole"] for s in S["supports"] if s["type"] == "fixed_bore"],
        "Fz_kN": f1[2] / 1e3, "Fy_a_kN": f1[1] / 1e3, "Fy_b_kN": f2[1] / 1e3,
        "My_per_bore": m[1], "My_total": sum(L["moment_Nm"][1] for L in lc["LC2"]["loads"]),
        "d_pin": holes["H1"]["diameter_mm"],
    }


def render_part(W: int, H: int):
    """Render the part with coloured BC faces; return (image, plotter, source) — plotter kept for projection."""
    part, src = R.load_part()
    c = part.cell_centers().points
    nrm = part.compute_normals(cell_normals=True, point_normals=False)["Normals"]
    sup = np.zeros(part.n_cells, bool)
    for bx, by in G.BOLTS:
        r = np.hypot(c[:, 0] - bx, c[:, 1] - by)
        sup |= (np.abs(r - G.R_BORE) < 0.8) & (c[:, 2] > G.Z0 - 0.1) & (c[:, 2] < G.Z1 + 0.1) & (np.abs(nrm[:, 2]) < 0.5)
    r = np.hypot(c[:, 0] - G.PIN[0], c[:, 2] - G.PIN[1])
    brg = (np.abs(r - G.R_BORE) < 0.8) & (c[:, 2] > G.PIN[1]) & (np.abs(nrm[:, 1]) < 0.5)
    rest = ~(sup | brg)
    p = R.new_plotter("light", (W * SS, H * SS))
    R.add_studio_lights(p, "light")
    R.add_ground(p, "light")
    R.add_part(p, part.extract_cells(np.where(rest)[0]).extract_surface(), "light")
    R.add_part(p, part.extract_cells(np.where(sup)[0]).extract_surface(), "light", color=C_SUP)
    R.add_part(p, part.extract_cells(np.where(brg)[0]).extract_surface(), "light", color=C_F)
    R.set_camera(p, -116.0, 34.0, 1600.0, view_angle=24.0, focal=R.CENTER + np.array([10.0, -60.0, 15.0]))
    R.add_edges(p, R.load_edges(), "light", lw=1.6 * SS)
    img = R.snap(p, None, (W, H))
    return img, p, src


def lug_profile(z_cut: float) -> np.ndarray:
    """Lug outline in x-z (flank, top arc R80, flank) above z_cut (which must lie on the flanks), closed polygon."""
    Rf, Lf = G.FLANK_R, G.FLANK_L
    assert max(Rf["t_fil"][1], Lf["t_fil"][1]) <= z_cut <= min(Rf["t_arc"][1], Lf["t_arc"][1])
    ax_, az_ = G.ARC_C
    aR = math.atan2(Rf["t_arc"][1] - az_, Rf["t_arc"][0] - ax_)
    aL = math.atan2(Lf["t_arc"][1] - az_, Lf["t_arc"][0] - ax_)
    t = np.linspace(aR, aL, 120)
    top = np.column_stack([ax_ + G.R_ARC * np.cos(t), az_ + G.R_ARC * np.sin(t)])
    xr = (Rf["c"] - Rf["n"][1] * z_cut) / Rf["n"][0]
    xl = (Lf["c"] - Lf["n"][1] * z_cut) / Lf["n"][0]
    return np.vstack([[xr, z_cut], top, [xl, z_cut]])


def detail(ax, S) -> None:
    """Pin-bore detail, x-z plane seen along +y (x right, z up; +y into the page)."""
    px_, pz_ = G.PIN
    r = G.R_BORE
    z_cut = 175.0
    poly = lug_profile(z_cut)
    xs = poly[:, 0]
    ax.add_patch(Polygon(poly, closed=True, fc=STEEL, ec=GREY, lw=1.6, zorder=1))
    ax.add_patch(Circle((px_, pz_), r, fc="white", ec=GREY, lw=1.6, zorder=2))
    # cut line (break) and centre lines
    ax.plot([xs.min() - 6, xs.max() + 6], [z_cut, z_cut], color=GREY, lw=1.2, ls=(0, (6, 3)), zorder=2)
    ax.plot([px_ - 48, px_ + 48], [pz_, pz_], color=GREY, lw=1.0, ls=(0, (10, 3, 2, 3)), zorder=3)
    ax.plot([px_, px_], [pz_ - 48, pz_ + 48], color=GREY, lw=1.0, ls=(0, (10, 3, 2, 3)), zorder=3)
    # cosine bearing pressure on the upper half: arrows from inside the bore onto the wall, radial outward
    for th in np.radians(np.linspace(15, 165, 7)):
        L = 22 * math.sin(th)
        if L < 3:
            continue
        a = (px_ + (r - L) * math.cos(th), pz_ + (r - L) * math.sin(th))
        b = (px_ + r * math.cos(th), pz_ + r * math.sin(th))
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=C_F, lw=1.8,
                                     shrinkA=0, shrinkB=0, zorder=5))
    # resultant Fz
    ax.add_patch(FancyArrowPatch((px_, G.Z_TOP + 8), (px_, G.Z_TOP + 68), arrowstyle="-|>",
                                 mutation_scale=26, color=C_F, lw=4, shrinkA=0, shrinkB=0, zorder=5))
    ax.text(px_ + 12, G.Z_TOP + 40, f"Fz {S['Fz_kN']:.0f} kN", color=C_F, fontsize=FS_M, fontweight="bold",
            ha="left", va="center")
    # +My about +y (into the page): rotates +z towards +x = clockwise on this view
    rm = 50.0
    ax.add_patch(Arc((px_, pz_), 2 * rm, 2 * rm, theta1=200, theta2=340, color=C_M, lw=3.5, zorder=4))
    t_end = math.radians(200)
    tip = (px_ + rm * math.cos(t_end), pz_ + rm * math.sin(t_end))
    pre = (px_ + rm * math.cos(t_end + 0.12), pz_ + rm * math.sin(t_end + 0.12))
    # arc drawn ccw from 200 to 340 deg; clockwise sense => arrow head at 200 deg
    ax.add_patch(FancyArrowPatch(pre, tip, arrowstyle="-|>", mutation_scale=24, color=C_M, lw=3.5,
                                 shrinkA=0, shrinkB=0, zorder=5))
    ax.text(px_, z_cut - 10, f"My {S['My_per_bore']:.0f} N·m per bore", color=C_M, fontsize=FS_M,
            fontweight="bold", ha="center", va="top")
    # +y into the page symbol (Fy acts along it)
    ax.add_patch(Circle((px_ - 150, G.Z_TOP + 0), 11, fc="white", ec=INK, lw=1.8, zorder=5))
    d = 11 / math.sqrt(2)
    for s_ in (1, -1):
        ax.plot([px_ - 150 - d, px_ - 150 + d], [G.Z_TOP + 0 - s_ * d, G.Z_TOP + 0 + s_ * d], color=INK,
                lw=1.8, zorder=6)
    ax.text(px_ - 132, G.Z_TOP + 0, "y", color=INK, fontsize=FS_M, style="italic", ha="left", va="center")
    ax.annotate("", xy=(px_ - 150, G.Z_TOP + 50), xytext=(px_ - 150, G.Z_TOP + 14),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8, mutation_scale=16))
    ax.text(px_ - 150, G.Z_TOP + 52, "z", color=INK, fontsize=FS_M, style="italic", ha="center", va="bottom")
    ax.plot([px_ - 104, px_ - r], [pz_, pz_], color=GREY, lw=1.2, zorder=3)
    ax.text(px_ - 108, pz_, f"Ø{S['d_pin']:.0f} mm", color=GREY, fontsize=FS_S, ha="right", va="center")
    ax.set_xlim(px_ - 205, px_ + 160)
    ax.set_ylim(z_cut - 52, G.Z_TOP + 150)
    ax.set_aspect("equal")
    ax.set_axis_off()


def main() -> None:
    S = read_setup()
    fig, ax = dw.figur("sunum", hedef="sunum-tam", yukseklik_mm=FIG_H, palet="akademik")
    import matplotlib as mpl
    mpl.rcParams["savefig.dpi"] = DPI       # 305 mm at 300 dpi = 3602 px (theme default 200 dpi = 2401 px)
    W = int(round(IMG_W_MM / 25.4 * DPI))
    H = int(round(FIG_H / 25.4 * DPI))
    img, p, src = render_part(W, H)
    P = lambda pts: R.world_to_px(p, np.asarray(pts, float), ss=SS)  # noqa: E731

    ax.set_position([0, 0, IMG_W_MM / FIG_W, 1])
    ax.imshow(img, extent=(0, W, H, 0), interpolation="lanczos")
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_axis_off()
    halo = [pe.withStroke(linewidth=6, foreground="white")]

    def arrow(a, b, color, lw=4.0, style="-|>", ms=26, z=5):
        ax.add_patch(FancyArrowPatch(tuple(a), tuple(b), arrowstyle=style, mutation_scale=ms, color=color,
                                     lw=lw, shrinkA=0, shrinkB=0, zorder=z, joinstyle="miter",
                                     capstyle="butt"))

    def label(xy, s, color, ha="left", va="center", size=FS_L, **kw):
        return ax.text(*xy, s, color=color, ha=ha, va=va, fontsize=size, path_effects=halo, zorder=8, **kw)

    yc = {k: S["holes"][k]["center_mm"][1] for k in ("H1", "H2")}
    px_, pz_ = G.PIN

    # pin axis centre line
    ca = P([[px_, -175.0, pz_], [px_, G.Y1 + 60, pz_]])
    ax.plot(ca[:, 0], ca[:, 1], color=GREY, lw=1.6, ls=(0, (14, 4, 3, 4)), zorder=3)

    # resultant Fz per pin bore: arrow above each lug, label beside the tip (H2 left, H1 right)
    for h, side in (("H2", -1), ("H1", +1)):
        a, b = P([[px_, yc[h], G.Z_TOP + 15], [px_, yc[h], G.Z_TOP + 120]])
        arrow(a, b, C_F, lw=5, ms=34)
        label(b + [side * 26, 18], f"Fz {S['Fz_kN']:.0f} kN", C_F, ha="left" if side > 0 else "right",
              va="center", fontweight="bold")

    # Fy along the pin axis (double-headed: + in LC1a, - in LC1b): in front of H1 and in the gap at H2
    fy = abs(S["Fy_a_kN"])
    a, b = P([[px_, -170.0, pz_], [px_, -25.0, pz_]])
    arrow(a, b, C_F, lw=4, style="<|-|>", ms=26)
    label(a + [28, 0], f"Fy ±{fy:.0f} kN", C_F, ha="left", va="center", fontweight="bold")
    a2, b2 = P([[px_, 130.0, pz_], [px_, 285.0, pz_]])
    arrow(a2, b2, C_F, lw=4, style="<|-|>", ms=26)
    label(a2 + [-62, 14], f"Fy ±{fy:.0f} kN", C_F, ha="right", va="center", fontweight="bold")

    # fixed supports: Ansys-style triangle + hatched ground on each bolt bore
    for hid in S["supports"]:
        bx, by, _ = S["holes"][hid]["center_mm"]
        c0 = P([[bx, by, G.Z1]])[0]
        s = 24.0
        tri = np.array([c0, c0 + [-s, -1.6 * s], c0 + [s, -1.6 * s]])
        ax.add_patch(Polygon(tri, closed=True, fc=C_SUP, ec="white", lw=1.5, zorder=6))
        yb = c0[1] - 1.6 * s
        ax.plot([c0[0] - 1.5 * s, c0[0] + 1.5 * s], [yb - 6, yb - 6], color=C_SUP, lw=3, zorder=6)
        for k in np.linspace(-1.3, 1.3, 6):
            x = c0[0] + k * s
            ax.plot([x, x - 12], [yb - 6, yb - 22], color=C_SUP, lw=2, zorder=6)
    label((40, H - 40), "Fixed support: 4 bolt bores, all DOF", C_SUP, ha="left", va="bottom",
          fontweight="bold")

    # global triad (directions projected at the part centre), top-left corner
    o3 = R.CENTER
    oo = P([o3])[0]
    org = np.array([150.0, 230.0])
    for vec, name in [((1, 0, 0), "x"), ((0, 1, 0), "y"), ((0, 0, 1), "z")]:
        d = P([o3 + 100 * np.array(vec)])[0] - oo
        d = d / np.linalg.norm(d) * 110
        arrow(org, org + d, INK, lw=2.5, ms=18)
        label(org + d * 1.38, name, INK, ha="center", va="center", size=FS_M, style="italic")

    # right column: detail (top) + load cases (bottom)
    x0 = IMG_W_MM / FIG_W
    dax = fig.add_axes([x0, 0.43, 1 - x0, 0.57])
    detail(dax, S)
    dax.text(0.02, 0.985, "Pin bore, view along +y", transform=dax.transAxes, color=INK, fontsize=FS_M,
             fontweight="bold", ha="left", va="top")
    tx = fig.add_axes([x0, 0, 1 - x0, 0.43])
    tx.set_axis_off()
    tx.set_xlim(0, 1)
    tx.set_ylim(0, 1)
    fyb = f"{S['Fy_b_kN']:.0f}".replace("-", "−")
    rows = [
        (f"LC1a   Fz +{S['Fz_kN']:.0f} kN,  Fy +{abs(S['Fy_a_kN']):.0f} kN", C_F, FS_M),
        (f"LC1b   Fz +{S['Fz_kN']:.0f} kN,  Fy {fyb} kN", C_F, FS_M),
        (f"LC2     My +{S['My_per_bore']:.0f} N·m  ({S['My_total']:.0f} total)", C_M, FS_M),
        ("Separate cases; values per pin bore.", GREY, FS_S),
        ("Set-up only, not an FEA result.", GREY, FS_S),
    ]
    y = 0.93
    for txt, col, size in rows:
        tx.text(0.03, y, txt, color=col, fontsize=size, ha="left", va="top")
        y -= 0.205 if size == FS_M else 0.17

    p.close()
    rep = dw.kaydet(fig, str(G.VIS / "bc_loads"), bicimler=("png", "pdf"), hedef="sunum-tam", cvd=True)
    print(rep["rapor"])
    print("geometry:", src)


if __name__ == "__main__":
    main()
