"""Figures of the Advionics report, through one datawiz set. Output: ../latex/figures/.

    python 03_Advionics/submission/report_build/report_figures.py

Reads report_numbers.json, cases/case_10_par_hybrid_cue/outputs/validation.json and the Smolensk table in validate_real.py.
"""
from __future__ import annotations

import json
import math
import sys
from importlib import util
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "pyproject.toml").is_file())
sys.path.insert(0, str(ROOT / "src"))
import datawiz as dw  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402

CASE = ROOT / "03_Advionics" / "cases" / "case_10_par_hybrid_cue"
OUT = HERE.parent / "latex" / "figures"
N = json.loads((HERE / "report_numbers.json").read_text(encoding="utf-8"))
V = json.loads((CASE / "outputs" / "validation.json").read_text(encoding="utf-8"))

S = dw.Seti(str(HERE / "report.seti.json"), hedef="genel-tek")
S.nicelik("nm", "Distance to touchdown", "NM", eksen="x")
S.nicelik("km", "Distance to threshold", "km", eksen="x")
S.nicelik("lat", "Lateral deviation", "m", eksen="y")
S.nicelik("vert", "Vertical deviation", "m", eksen="y")
S.nicelik("lat_sd", "Lateral scatter, SD", "m", eksen="y", sinir=(0, 20))
S.nicelik("vert_sd", "Vertical scatter, SD", "m", eksen="y", sinir=(0, 20))
S.varlik("No cue", baglam=True)
S.varlik("Zurich", renk="#000000", isaret="o", cizgi="-", degistir=True)
S.varlik("Sim, ring", renk="#1f3a93", isaret="s", cizgi="-", degistir=True)
S.varlik("Sim, heading", renk="#d55e00", isaret="^", cizgi="--", degistir=True)
S.varlik("ILS, St Louis", baglam=True)


def save(fig, name: str) -> None:
    S.kaydet(fig, str(OUT / name), sessiz=True)
    plt.close(fig)
    print(name, (OUT / f"{name}.denetim.txt").read_text(encoding="utf-8").splitlines()[0])


def return_to_path() -> None:
    fig, axs = S.figur(genislik="cift", ncols=2, yukseklik_mm=44)
    f = N["figure"]
    for ax, cue, ring, nocue, q in ((axs[0], f["cue_y"], f["ring_y"], f["nocue_y"], "lat"),
                                    (axs[1], f["cue_z"], f["ring_z"], f["nocue_z"], "vert")):
        ax.fill_between(cue["nm"], cue["p5"], cue["p95"], color="#d55e00", alpha=0.18, lw=0)
        ax.fill_between(ring["nm"], ring["p5"], ring["p95"], color="#1f3a93", alpha=0.25, lw=0)
        ax.plot(nocue["nm"], nocue["p50"], **S.stil("No cue"))
        ax.plot(cue["nm"], cue["p50"], **S.stil("Sim, heading"))
        ax.plot(ring["nm"], ring["p50"], **S.stil("Sim, ring"))
        ax.axhline(0, color="#555555", lw=0.6)
        S.eksen(ax, x="nm", y=q)
        ax.set_xlim(5.05, 0.6)
    axs[0].set_ylim(-110, 175)
    axs[0].text(2.6, 112, "No cue", color="#6b6b6b", ha="center", va="center")
    axs[0].text(2.75, -98, "Heading target", color="#d55e00", ha="center", va="center")
    axs[0].text(2.9, 62, "Ring", color="#1f3a93", ha="center", va="center")
    S.panel_harfleri(axs)
    save(fig, "F2_return_to_path")


def agreement() -> None:
    fig, axs = S.figur(genislik="cift", ncols=3, yukseklik_mm=47)
    z = N["zurich"]["rows"]
    ring, head = N["sim"]["on_path_ring"]["rows"], N["sim"]["on_path_annex10_radar"]["rows"]
    ils = [(5, 20), (4, 15), (3, 13), (2, 9), (1, 6)]
    for ax, key, q in ((axs[0], "lat_sd_m", "lat_sd"), (axs[1], "vert_sd_m", "vert_sd")):
        ax.plot([r["nm"] for r in head], [r[key] for r in head], **S.stil("Sim, heading", isaretli=True))
        ax.plot([r["nm"] for r in ring], [r[key] for r in ring], **S.stil("Sim, ring", isaretli=True))
        ax.plot([r["nm"] for r in z], [r[key] for r in z], **S.stil("Zurich", isaretli=True))
        S.eksen(ax, x="nm", y=q)
        ax.set_xlim(5.2, 0.7)
        ax.set_xticks([5, 4, 3, 2, 1])
    axs[0].plot([a for a, _ in ils], [b for _, b in ils], **S.stil("ILS, St Louis"))
    axs[0].text(4.15, 19.2, "ILS, St Louis", color="#6b6b6b", ha="left", va="center")
    axs[0].text(1.5, 14.2, "Sim, heading", color="#d55e00", ha="center", va="center")
    axs[0].text(1.6, 2.6, "Zurich", color="#000000", ha="center", va="center")
    axs[0].text(3.75, 11.6, "Sim, ring", color="#1f3a93", ha="center", va="center")
    smolensk(axs[2])
    S.panel_harfleri(axs)
    save(fig, "F3_real_data")


def smolensk(ax) -> None:
    spec = util.spec_from_file_location("validate_real", CASE / "validate_real.py")
    m = util.module_from_spec(spec)
    sys.modules["validate_real"] = m
    spec.loader.exec_module(m)
    gp = math.tan(math.radians(2.0 + 40.0 / 60.0))
    x = np.array([r[1] for r in m.SMOLENSK], float)
    dev = np.array([r[2] for r in m.SMOLENSK], float) - (x * gp + 14.8)
    r = np.linspace(1.0, 10.2, 60) * 1000
    lim = np.maximum(r * math.tan(math.radians(0.5)), 18.0)
    ax.fill_between(r / 1000, -lim, lim, color="#e6e6e6", lw=0)
    ax.axhline(0, color="#555555", lw=0.6)
    ax.plot(x / 1000, dev, **S.stil("Zurich"))
    calls = [8300, 6649, 4591, 3456, 2521]
    ax.plot([c / 1000 for c in calls], np.interp(calls, x[::-1], dev[::-1]), ls="none", marker="o", ms=4.5, mfc="white",
            mec="#000000", mew=0.9)
    first = V["smolensk"]["with_limits"]["timeline"]
    lim_call = next(f for f in first if f["state"] == "OUTSIDE LIMITS")
    ax.plot([lim_call["range_km"]], [float(np.interp(lim_call["range_km"] * 1000, x[::-1], dev[::-1]))], ls="none", marker="D",
            ms=5.5, color="#d55e00")
    S.eksen(ax, x="km", y="vert")
    ax.set_xlim(10.4, 0.9)
    ax.set_ylim(-110, 175)
    ax.text(9.9, 160, "Cue: limit call", color="#d55e00", ha="left", va="center")
    ax.text(5.8, 150, "Radio: on path", color="#000000", ha="left", va="center")
    ax.text(9.7, -62, "Limit band", color="#6b6b6b", ha="left", va="center")


EDGE = [pe.withStroke(linewidth=2.2, foreground="#10202e")]


def _ring(ax, x, y, r, col, lw=1.2):
    for a0, a1 in ((16, 164), (196, 258), (282, 344)):
        a = np.radians(np.linspace(a0, a1, 40))
        ax.plot(x + r * np.cos(a), y + r * np.sin(a), color=col, lw=lw, solid_capstyle="round", zorder=5, path_effects=EDGE)


def _marker(ax, x, y, col="#7dffb0"):
    r = 0.55
    a = np.linspace(0, 2 * np.pi, 40)
    ax.plot(x + r * np.cos(a), y + r * np.sin(a), color=col, lw=1.2, zorder=6, path_effects=EDGE)
    ax.plot([x - 2.5 * r, x - r], [y, y], color=col, lw=1.2, zorder=6, path_effects=EDGE)
    ax.plot([x + r, x + 2.5 * r], [y, y], color=col, lw=1.2, zorder=6, path_effects=EDGE)
    ax.plot([x, x], [y + r, y + 2.2 * r], color=col, lw=1.2, zorder=6, path_effects=EDGE)


def _diamond(ax, x, y, old: bool):
    p = plt.Polygon([(x - 0.75, y), (x, y + 0.75), (x + 0.75, y), (x, y - 0.75)], closed=True, zorder=7,
                    fc="none" if old else "white", ec="#ffb000" if old else "black", lw=1.2 if old else 0.6,
                    ls=(0, (2, 1)) if old else "-")
    ax.add_patch(p)


def display() -> None:
    """Four frames of the replay shown on the display, same symbols and sign rules as the mock-up (par-gosterge.mjs)."""
    path = Path("D:/Custom Yetenekler/sunumatik/.claude/worktrees/par-approach-visual/presets/par_approach/par_replay.json")
    d = json.loads(path.read_text(encoding="utf-8"))
    sc = {s["id"]: s["frames"] for s in d["scenarios"]}
    ring_r = d["ring_deg"]
    plan = (("A", 14, "QUIET", "Off path"), ("A", 60, "QUIET", "On path"), ("B", 18, "ADVISE: DELAYED", "Data old"),
            ("C", 76, "WARNING: RADAR LOST", "Data lost"))
    fig, axs = S.figur(genislik="cift", ncols=4, yukseklik_mm=43, layout="compressed")
    white = [pe.withStroke(linewidth=1.6, foreground="#10202e")]
    for ax, (sid, t, status, _) in zip(axs, plan):
        fr = sc[sid]
        i = next(k for k, f in enumerate(fr) if f["t"] == t)
        f, a, b = fr[i], fr[i - 1], fr[i + 1]
        dx = abs(b["x_m"] - a["x_m"])
        trk = math.degrees(math.atan2(b["y_m"] - a["y_m"], dx))
        gam = math.degrees(math.atan2(b["height_m"] - a["height_m"], dx))
        psi = math.degrees(f["psi"])
        hor = -(gam + 5.0)                           # horizon below the nose; 5 deg of angle of attack is schematic
        ax.set_xlim(-9.6, 11.9)
        ax.set_ylim(-11.3, 11.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.add_patch(plt.Rectangle((-9.1, hor), 18.2, 9.3 - hor, fc="#2f6fa8", ec="none", zorder=1))
        ax.add_patch(plt.Rectangle((-9.1, -9.3), 18.2, hor + 9.3, fc="#7a4f2a", ec="none", zorder=1))
        ax.plot([-9.1, 9.1], [hor, hor], color="white", lw=0.9, zorder=2)
        for dg in (-5, -2.5, 2.5, 5):
            w = 2.6 if dg % 5 == 0 else 1.2
            if abs(hor + dg) < 9:
                ax.plot([-w, w], [hor + dg, hor + dg], color="white", lw=0.6, zorder=2)
        for s in (-1, 1):                            # fixed aircraft symbol
            ax.plot([s * 5.2, s * 2.2, s * 2.2], [0, 0, -0.9], color="black", lw=1.2, zorder=4)
        mx, my = trk - psi, hor + gam
        _marker(ax, mx, my)
        if f["aim_trk_deg"] is not None:
            hx, hy = f["aim_trk_deg"] - psi, hor + f["aim_gam_deg"]
            inside = math.hypot(hx - mx, hy - my) <= 0.8 * ring_r
            _ring(ax, hx, hy, ring_r, "#7dffb0" if inside else "#35d0ff")
            if t == 14:
                ax.text(hx - 0.2, hy + 2.3, "Ring", ha="center", va="center", color="white", fontsize=8, zorder=9, path_effects=white)
                ax.text(mx - 0.4, my - 2.5, "Marker", ha="center", va="center", color="white", fontsize=8, zorder=9, path_effects=white)
        # scales: glide path right, course below; 1 dot = 3.7 and 4 deg on the mock-up
        for n in (-2, -1, 1, 2):
            ax.plot([10.6], [n * 3.7], marker="o", ms=2.6, mfc="none", mec="black", mew=0.6, ls="none")
            ax.plot([n * 4.0], [-10.4], marker="o", ms=2.6, mfc="none", mec="black", mew=0.6, ls="none")
        ax.plot([10.0, 11.2], [0, 0], color="black", lw=0.8)
        ax.plot([0, 0], [-11.0, -9.8], color="black", lw=0.8)
        if f["lat_dots"] is not None:
            old = f["state"] == "DELAYED"
            _diamond(ax, 10.6, -f["vert_dots"] * 3.7, old)
            _diamond(ax, -f["lat_dots"] * 4.0, -10.4, old)
        ax.text(0, 10.3, status, ha="center", va="center", color="black", fontsize=8)
        if f["state"] == "RADAR LOST":
            ax.add_patch(plt.Rectangle((-5.2, 1.6), 10.4, 3.2, fc="#b00020", ec="none", zorder=8))
            ax.text(0, 3.2, "GO AROUND", ha="center", va="center", color="white", fontsize=8.5, zorder=9)
    S.panel_harfleri(axs)
    save(fig, "F4_display")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    return_to_path()
    agreement()
    display()
