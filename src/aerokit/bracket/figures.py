"""Report figures of a bracket run, produced and audited with datawiz (one figure set per run folder).

FİGÜR BRİFİ (shared by the four figures; docs/22 §Figures):
  Okur: karma (team + jury) · hedef: genel-tek (88 mm, ≥ 8 pt) · tema: akademik (datawiz default set palette)
  F1 convergence  — "Deflection and stress settle as the voxel shrinks"; x voxel size (mm), y deflection (mm) /
                     von Mises outside the hole zones (MPa); 3 points, two small panels, points + line.
  F2 materials    — "<material> is the lightest option that passes at T"; horizontal bars of mass (kg) of the
                     lightest passing layout, zero-based, failing materials listed in the caption.
  F3 eco          — "The use phase dominates life CO₂e"; dot plot per phase, baseline vs redesign, log x
                     (positions, not bars, so a log axis is allowed).
  F4 history      — "Compliance converges within the iteration budget"; weighted compliance relative to the
                     initial (full) design vs iteration, log y, one line per volume fraction, direct labels.
Every figure goes through ``Seti.kaydet`` (figure audit + set consistency); a HATA raises (``kati=True``).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

__all__ = ["make_all"]


def _same_canvas(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pad two renders (H, W, C) to the same pixel size, centred, with the background colour of their corner."""
    H, W = max(a.shape[0], b.shape[0]), max(a.shape[1], b.shape[1])

    def pad(im: np.ndarray) -> np.ndarray:
        out = np.empty((H, W, *im.shape[2:]), dtype=im.dtype)
        out[...] = im[0, 0]
        y, x = (H - im.shape[0]) // 2, (W - im.shape[1]) // 2
        out[y:y + im.shape[0], x:x + im.shape[1]] = im
        return out
    return pad(a), pad(b)


def _render(stl: Path, size: tuple[int, int] = (900, 700)) -> np.ndarray | None:
    """Off-screen VTK render of an STL (iso view, neutral grey), cropped to the part; None without pyvista."""
    try:
        import pyvista as pv
    except ImportError:
        return None
    m: Any = pv.read(str(stl))
    p: Any = pv.Plotter(off_screen=True, window_size=list(size))
    p.set_background("white")
    p.add_mesh(m, color="#b9c4cf", smooth_shading=True, specular=0.3)
    p.view_isometric()
    img = np.asarray(p.screenshot(return_img=True))
    p.close()
    mask = np.any(img[:, :, :3] < 245, axis=2)
    if mask.any():
        r, c = np.flatnonzero(mask.any(1)), np.flatnonzero(mask.any(0))
        img = img[max(r[0] - 10, 0):r[-1] + 10, max(c[0] - 10, 0):c[-1] + 10]
    return img


def make_all(st: Any, folder: Path) -> dict[str, str]:
    """Write the figures, then fix common plot margins from datawiz's suggestion and write them again so the
    plot areas line up across the set (set-consistency check: no mixed margins)."""
    out = _make_all(st, folder)
    import datawiz as dw
    S = dw.Seti(str(folder / "bracket.seti.json"), hedef="genel-tek")
    if not S.d.get("kenar_mm"):
        S.kenar(*S.kenar_oner())
        out = _make_all(st, folder)
    return out


def _make_all(st: Any, folder: Path) -> dict[str, str]:
    import matplotlib
    matplotlib.use("Agg")
    import datawiz as dw

    folder.mkdir(parents=True, exist_ok=True)
    S = dw.Seti(str(folder / "bracket.seti.json"), hedef="genel-tek")
    S.nicelik("voxel", "Voxel size", "mm", eksen="x")
    S.nicelik("defl", "Max deformation", "mm", eksen="y")
    S.nicelik("vm", "Peak von Mises", "MPa", eksen="y")
    S.nicelik("mass", "Mass", "kg", eksen="x")
    S.nicelik("co2", "CO₂e", "kg", eksen="x", olcek="log")
    S.nicelik("iter", "Iteration", None, eksen="x")
    S.nicelik("cnorm", "Relative compliance", None, eksen="y", olcek="log")
    out: dict[str, str] = {}
    T = st.T

    # ---------------------------------------------------------------- F1 convergence
    if len(st.convergence) >= 2:
        conv = sorted(st.convergence, key=lambda c: c["h_mm"])
        h = np.array([c["h_mm"] for c in conv])
        fig, axs = S.figur(genislik="tek", oran=1.1, nrows=2, sharex=True)
        S.varlik("initial design")
        st_ = S.stil("initial design", tur="cizgi", isaretli=True)
        axs[0].plot(h, [c["max_disp_m"] * 1e3 for c in conv], **st_)
        axs[1].plot(h, [c["vm_outside_Pa"] / 1e6 for c in conv], **st_)
        S.eksen(axs[0], y="defl")
        S.eksen(axs[1], x="voxel", y="vm")
        dw.etiket.panel_harfleri(axs)
        p = folder / "f1_convergence"
        r = S.kaydet(fig, str(p), cvd=True, kati=True, sessiz=True)
        out[str(p) + ".png"] = (f"mesh convergence of the initial design at {T:g} °C (H8 incompatible-mode "
                                f"voxels, {len(conv)} levels): (a) max deformation, (b) peak von Mises outside the "
                                f"hole exclusion zones; audit: {r.get('hata', 0)} HATA")
    # ---------------------------------------------------------------- F2 materials
    rows = [(x["name"].split(" (")[0], x["best"]["mass_kg"]) for x in st.materials if x["best"]]
    if rows:
        rows.sort(key=lambda r: r[1])
        fig, ax = S.figur(genislik="tek", oran=0.55)
        names = [r[0] for r in rows][::-1]
        vals = [r[1] for r in rows][::-1]
        S.varlik("passing material")
        c = S.renk("passing material")
        ax.barh(names, vals, color=dw.renk.alan_tonu(c), edgecolor=c, linewidth=1.0)
        ax.grid(False, axis="y")
        for i, v in enumerate(vals):
            ax.text(v, i, f" {v:.3f}", va="center", fontsize=8)
        ax.set_xlim(0, max(vals) * 1.25)
        S.eksen(ax, x="mass")
        ax.set_ylabel("Material")
        p = folder / "f2_materials"
        r = S.kaydet(fig, str(p), cvd=True, kati=True, sessiz=True)
        fails = [x["name"].split(" (")[0] for x in st.materials if not x["best"]]
        out[str(p) + ".png"] = (f"mass of the lightest passing layout per material at {T:g} °C; not passing: "
                                f"{', '.join(fails) or 'none'}; audit: {r.get('hata', 0)} HATA")
    # ---------------------------------------------------------------- F3 eco
    if st.choice and st.choice["material"] in st.eco["candidates"]:
        base = st.eco["baseline"]["phases"]
        new = st.eco["candidates"][st.choice["material"]]["audit"]["phases"]
        phases = [k for k in base if base[k]["co2_kg"] > 0 or new[k]["co2_kg"] > 0]
        fig, ax = S.figur(genislik="tek", oran=0.6)
        S.varlik("baseline", baglam=True)
        S.varlik("redesign")
        y = np.arange(len(phases))[::-1]
        ax.scatter([max(base[k]["co2_kg"], 1e-3) for k in phases], y + 0.15, **S.stil("baseline", tur="sacilim"))
        ax.scatter([max(new[k]["co2_kg"], 1e-3) for k in phases], y - 0.15, **S.stil("redesign", tur="sacilim"))
        ax.set_yticks(y, [k.replace("_", " ") for k in phases])
        S.eksen(ax, x="co2")
        from matplotlib.ticker import FuncFormatter, LogLocator  # noqa: F401
        from matplotlib.ticker import FixedLocator
        vals = [max(ph[k]["co2_kg"], 1e-3) for ph in (base, new) for k in phases]
        e0, e1 = int(np.floor(np.log10(min(vals)))), int(np.ceil(np.log10(max(vals))))
        step = 1 if e1 - e0 <= 4 else 2                       # at most ~5 labelled decades (no tick overlap)
        ax.xaxis.set_major_locator(FixedLocator([10.0 ** e for e in range(e0, e1 + 1, step)]))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=(1.0,), numticks=30))
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda v, _: f"{v:,.0f}" if v >= 1 else f"{v:.{max(0, int(np.ceil(-np.log10(v) - 1e-9)))}f}"))
        lo = min(max(ph[k]["co2_kg"], 1e-3) for ph in (base, new) for k in phases)
        ax.set_xlim(left=10 ** np.floor(np.log10(lo)))
        ax.set_ylabel("Life phase")
        dw.lejant.yerlestir(ax)
        dw.cila(fig, tik=False)          # keep the decade ticks set above (cila's log locator labels every decade)
        p = folder / "f3_eco"
        r = S.kaydet(fig, str(p), cvd=True, kati=True, sessiz=True)
        out[str(p) + ".png"] = (f"CO₂e by life phase, baseline vs redesign ({st.choice['material']}); audit: "
                                f"{r.get('hata', 0)} HATA")
    # ---------------------------------------------------------------- F4 history
    hist = [d for d in st.designs[1:] if d.get("compliance_history")]
    n_cases = len(st.setup["load_cases"])
    if hist:
        fig, ax = S.figur(genislik="tek", oran=0.65)
        for d in hist:
            c = np.asarray(d["compliance_history"]) / n_cases     # weights 1/c0 → initial design = n_cases
            S.varlik(d["label"])
            ax.plot(np.arange(1, len(c) + 1), c, **S.stil(d["label"]))
        S.eksen(ax, x="iter", y="cnorm")
        dw.etiket.cizgi_sonu(ax)
        p = folder / "f4_history"
        r = S.kaydet(fig, str(p), cvd=True, kati=True, sessiz=True)
        out[str(p) + ".png"] = (f"weighted compliance of the optimisation runs relative to the initial design "
                                f"(each run warm-starts from the previous volume fraction); audit: "
                                f"{r.get('hata', 0)} HATA")
    # ---------------------------------------------------------------- F5 initial vs chosen (renders)
    if st.choice:
        cad = st.out / "cad"
        ini = cad / "initial.stl" if (cad / "initial.stl").exists() else cad / "initial_voxels.stl"
        d = next((x for x in st.designs if x["label"] == st.choice["design"]), None)
        cho = cad / f"optimised_{round(100 * d['volfrac'])}.stl" if d and d["volfrac"] < 1 else ini
        a, b = (_render(ini), _render(cho)) if ini.exists() and cho.exists() else (None, None)
        if a is not None and b is not None:
            a, b = _same_canvas(a, b)               # equal pixel boxes → equal axes boxes (panel alignment)
            fig, axs = S.figur(genislik="tek", oran=0.5, ncols=2)
            for ax, im in zip(axs, (a, b), strict=True):
                ax.imshow(im)
                ax.set_axis_off()
            dw.etiket.panel_harfleri(axs)
            p = folder / "f5_shapes"
            r = S.kaydet(fig, str(p), cvd=False, kati=True, sessiz=True)
            out[str(p) + ".png"] = (f"(a) initial design {st.baseline['mass_kg']:.3f} kg {st.baseline['material']}; "
                                    f"(b) chosen {st.choice['design']} in {st.choice['material']} "
                                    f"{st.choice['mass_kg']:.3f} kg (iso view, renders of the STL files in cad/); "
                                    f"audit: {r.get('hata', 0)} HATA")
    import matplotlib.pyplot as plt
    plt.close("all")
    return out
