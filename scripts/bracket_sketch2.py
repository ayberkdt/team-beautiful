"""sketch2 — the organisers' 5 Nov hand sketch (studies/final_2026/ansys/inputs/organiser_sketch_2026-11-05.png) as a
parametric drawing: a stadium-shaped plate with bolt holes and two arch features. GEOMETRY ONLY (no FEA, no topology).

    python scripts/bracket_sketch2.py                      # all four variants, default dimensions [Y]
    python scripts/bracket_sketch2.py --set L=180 --set W=80 --set arch_A_r=16 --variants loop

Every dimension is a named parameter (mm) in PARAMS; all values are our reading of a sketch without dimensions [Y]
and are replaced on the day with --set name=value. Variants (the sketch is ambiguous):

* ``loop``        — both arches are closed straps (half-annulus bridges standing on the plate; a pin, cable or
                    bolt passes through the opening under each arch, axis y); small plate hole under arch B;
* ``loop_nohole`` — as ``loop`` without that small hole;
* ``lug``         — both arches are upstanding lugs (tongue with a round head and a pin bore, axis y);
* ``lug_nohole``  — as ``lug`` without the small hole.

Per variant: studies/final_2026/ansys/inputs/sketch2_<variant>.json/.step/.stl, then a geometry-only check with the
day pipeline (``pipeline.prepare``: STEP read, hole scan, voxels, proposed roles, exact volume) into
studies/final_2026/ansys/inputs/sketch2_prep/<variant>/ (setup.json, check.json) and a 4-view preview
(sketch2_prep/<variant>/preview.png, datawiz-audited). handoff/ is never touched.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.bracket import cadout, geometry, pipeline  # noqa: E402

INPUTS = ROOT / "studies" / "final_2026" / "ansys" / "inputs"

PARAMS: dict[str, float] = {
    # plate (stadium: straight part L − W, round ends of radius W/2), x along the length, z up
    "L": 160.0, "W": 70.0, "t": 8.0,
    # bolt holes: 3 at each end (end centre + two near the edges), diameter for M8 clearance
    "bolt_d": 8.5, "bolt_end_x": 18.0, "bolt_edge_x": 32.0, "bolt_edge_y": 14.0,
    # arch A (the larger, "upper" one in the sketch): span along x
    "arch_A_x": 70.0, "arch_A_y": 48.0, "arch_A_r": 14.0, "arch_A_wall": 6.0, "arch_A_b": 12.0,
    # arch B (the smaller, "lower" one)
    "arch_B_x": 100.0, "arch_B_y": 22.0, "arch_B_r": 9.0, "arch_B_wall": 5.0, "arch_B_b": 10.0,
    # lug variant: height of the head centre above the plate top, as a multiple of the outer radius
    "lug_head": 1.0,
    # small plate hole under / next to arch B (sketch: small oval near the lower arch)
    "small_d": 6.0, "small_dx": 0.0, "small_dy": 0.0,
    # optional hole through the crown of arch A, axis z (0 = absent; the sketch shows a mark near the upper arch)
    "crown_A_d": 0.0,
}
VARIANTS = ("loop", "loop_nohole", "lug", "lug_nohole")


def _arch(p: dict[str, float], k: str, style: str) -> list[dict[str, Any]]:
    """Solids of one arch: a horseshoe prism (loop) or a tongue with a pin bore (lug); prism polygon in (x, z)."""
    x, y, r, a, b, t = (p[f"arch_{k}_x"], p[f"arch_{k}_y"], p[f"arch_{k}_r"], p[f"arch_{k}_wall"],
                        p[f"arch_{k}_b"], p["t"])
    R = r + a
    rng = [y - b / 2, y + b / 2]
    if style == "loop":
        poly = geometry.arc((x, t), R, 0, 180, 24) + geometry.arc((x, t), r, 180, 0, 24)
        return [{"op": "add", "type": "prism", "axis": "y", "polygon": poly, "range": rng}]
    zc = t + p["lug_head"] * R
    poly = [[x - R, t], [x + R, t]] + geometry.arc((x, zc), R, 0, 180, 24)
    return [{"op": "add", "type": "prism", "axis": "y", "polygon": poly, "range": rng},
            {"op": "cut", "type": "cylinder", "p0": [x, rng[0] - 1, zc], "p1": [x, rng[1] + 1, zc], "radius": r}]


def drawing(p: dict[str, float], variant: str) -> dict[str, Any]:
    style = "lug" if variant.startswith("lug") else "loop"
    L, W, t = p["L"], p["W"], p["t"]
    rr = W / 2
    plate = (geometry.arc((L - rr, rr), rr, -90, 90, 32) + geometry.arc((rr, rr), rr, 90, 270, 32))
    solids: list[dict[str, Any]] = [{"op": "add", "type": "prism", "axis": "z", "polygon": plate, "range": [0, t]}]
    solids += _arch(p, "A", style) + _arch(p, "B", style)
    bolts = [(p["bolt_end_x"], rr), (p["bolt_edge_x"], p["bolt_edge_y"]), (p["bolt_edge_x"], W - p["bolt_edge_y"])]
    bolts += [(L - x, y) for x, y in bolts]
    for x, y in bolts:
        solids.append({"op": "cut", "type": "cylinder", "p0": [x, y, -1], "p1": [x, y, t + 1], "radius": p["bolt_d"] / 2})
    if p["crown_A_d"] > 0:                         # through the curved crown (loop) or the head (lug), axis z
        x, y = p["arch_A_x"], p["arch_A_y"]
        top = t + (p["lug_head"] + 1) * (p["arch_A_r"] + p["arch_A_wall"]) + 1
        solids.append({"op": "cut", "type": "cylinder", "p0": [x, y, t + 1], "p1": [x, y, top],
                       "radius": p["crown_A_d"] / 2})
    if not variant.endswith("nohole"):
        x, y = p["arch_B_x"] + p["small_dx"], p["arch_B_y"] + p["small_dy"]
        solids.append({"op": "cut", "type": "cylinder", "p0": [x, y, -1], "p1": [x, y, t + 1], "radius": p["small_d"] / 2})
    return {"name": f"sketch2 {variant} (organisers' 5 Nov sketch, dimensions are our reading [Y])", "units": "mm",
            "parameters": p, "variant": variant,
            "_about": "generated by scripts/bracket_sketch2.py; change a dimension with --set name=value, not by hand",
            "solids": solids}


def _views(stl: Path) -> list[np.ndarray]:
    import pyvista as pv
    m: Any = pv.read(str(stl))
    out = []
    for view in ("iso", "xy", "xz", "yz"):
        pl: Any = pv.Plotter(off_screen=True, window_size=[900, 650])
        pl.set_background("white")
        pl.add_mesh(m, color="#b9c4cf", smooth_shading=True, specular=0.3)
        {"iso": pl.view_isometric, "xy": pl.view_xy, "xz": pl.view_xz, "yz": pl.view_yz}[view]()
        img = np.asarray(pl.screenshot(return_img=True))
        pl.close()
        mask = np.any(img[:, :, :3] < 245, axis=2)
        if mask.any():
            r, c = np.flatnonzero(mask.any(1)), np.flatnonzero(mask.any(0))
            img = img[max(r[0] - 10, 0):r[-1] + 10, max(c[0] - 10, 0):c[-1] + 10]
        out.append(img)
    H, W = max(i.shape[0] for i in out), max(i.shape[1] for i in out)
    padded = []
    for im in out:                                   # one canvas size → aligned panels
        c = np.full((H, W, im.shape[2]), 255, dtype=im.dtype)
        y, x = (H - im.shape[0]) // 2, (W - im.shape[1]) // 2
        c[y:y + im.shape[0], x:x + im.shape[1]] = im
        padded.append(c)
    return padded


def preview(stl: Path, folder: Path) -> dict[str, Any]:
    import datawiz as dw
    S = dw.Seti(str(folder / "sketch2.seti.json"), hedef="genel-tek")
    fig, axs = S.figur(genislik="tek", oran=0.75, nrows=2, ncols=2)
    for ax, im in zip(np.ravel(axs), _views(stl), strict=True):
        ax.imshow(im)
        ax.set_axis_off()
    dw.etiket.panel_harfleri(list(np.ravel(axs)))
    r = S.kaydet(fig, str(folder / "preview"), cvd=False, kati=True, sessiz=True)
    import matplotlib.pyplot as plt
    plt.close("all")
    return {"png": str(folder / "preview.png"), "audit_hata": r.get("hata", 0),
            "panels": "(a) iso, (b) top (x–y), (c) front (x–z), (d) side (y–z)"}


def check(variant: str, p: dict[str, float], do_preview: bool = True) -> dict[str, Any]:
    d = drawing(p, variant)
    js = INPUTS / f"sketch2_{variant}.json"
    js.write_text(json.dumps(d, indent=1), encoding="utf-8")
    cad = cadout.drawing_to_cad(geometry.load_drawing(d), INPUTS / f"sketch2_{variant}.step",
                                INPUTS / f"sketch2_{variant}.stl")
    bodies = cadout.step_bodies(INPUTS / f"sketch2_{variant}.step")
    folder = INPUTS / "sketch2_prep" / variant
    folder.mkdir(parents=True, exist_ok=True)
    g = pipeline.load_geometry(INPUTS / f"sketch2_{variant}.step", work_dir=folder / "cad")
    opt = pipeline.Options(volfracs=(), convergence=False, tet_check=False, log=False)
    st = pipeline.prepare(g, folder, opt)                      # geometry only: voxels, holes, set-up, volume
    exact = [s_ for s_ in d["solids"] if s_["op"] == "cut" and s_["type"] == "cylinder"]
    found = [{"id": h["id"], "axis": h["axis"], "d_mm": h["diameter_mm"],
              "c_mm": [round(v, 1) for v in h["center_mm"]], "role": h["role"]} for h in st.setup["holes"]]
    res = {"variant": variant, "solids_in_step": len(bodies), "volume_mm3": cad["volume_mm3"],
           "mass_steel_kg": cad["volume_mm3"] * 1e-9 * 7850.0,
           "bbox_mm": [[round(v, 2) for v in cad["bbox_mm"][0]], [round(v, 2) for v in cad["bbox_mm"][1]]],
           "voxel_mm": st.mesh.h * 1e3, "elements": int(st.mesh.ne),
           "holes_cut_in_drawing": len(exact), "holes_found_from_step": found,
           "supports": [s["hole"] for s in st.setup["supports"]],
           "load_holes": sorted({ld["hole"] for c in st.setup["load_cases"] for ld in c["loads"]})}
    if do_preview:
        res["preview"] = preview(INPUTS / f"sketch2_{variant}.stl", folder)
    (folder / "check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


LOAD_CASES = (("LC1 vertical pull-off (+z)", (0.0, 0.0, 1.0), 4000.0),
              ("LC2 lateral, in the arch plane (+x)", (1.0, 0.0, 0.0), 2500.0),
              ("LC3 along the arch axis (+y)", (0.0, 1.0, 0.0), 1500.0))
"""Load-case hypotheses [Y]: directions from the sketch's arch geometry, magnitudes invented (replace on the day, or
use --calibrate 0.8 if the organisers give none). Limit loads; ultimate = 1.5 × limit."""


def proposals(variant: str, p: dict[str, float]) -> list[Path]:
    """Set-up proposals from the geometry-only prep set-up: bolts = fixed bores, the small hole free, load on the
    arches (hypothesis "A" = arch A only, "AB" = shared equally by both); loop openings replaced by the exact arch
    circle (centre on the plate top, radius = inner radius) instead of the equivalent circle of the voxel scan."""
    import copy
    folder = INPUTS / "sketch2_prep" / variant
    base = json.loads((folder / "setup.json").read_text(encoding="utf-8"))
    arches = sorted((h for h in base["holes"] if h["axis"] == "y"), key=lambda h: -h["diameter_mm"])
    if len(arches) != 2:
        raise ValueError(f"{variant}: expected 2 arch openings, found {len(arches)}")
    ida, idb = arches[0]["id"], arches[1]["id"]
    if variant.startswith("loop"):
        for h, k in ((arches[0], "A"), (arches[1], "B")):
            h["center_mm"] = [p[f"arch_{k}_x"], p[f"arch_{k}_y"], p["t"]]
            h["diameter_mm"] = 2 * p[f"arch_{k}_r"]
            h["_note"] = ("exact arch circle (voxel scan gave the equal-area circle of the half-disc opening); "
                          "lateral loads also reach the plate top inside the opening [Y limitation]")
    small = [h["id"] for h in base["holes"] if h["axis"] == "z" and h["diameter_mm"] < 0.85 * p["bolt_d"]]
    for h in base["holes"]:
        h["role"] = "load" if h["id"] in (ida, idb) else ("free" if h["id"] in small else "support")
    out = []
    for hyp, ids in (("A", [ida]), ("AB", [ida, idb])):
        s = copy.deepcopy(base)
        s.pop("_proposal_signature", None)
        s["roles_source"] = "edited"
        s["supports"] = [{"hole": h["id"], "type": "fixed_bore"} for h in s["holes"] if h["role"] == "support"]
        s["load_cases"] = [{"name": name, "loads": [{"hole": i, "type": "bearing",
                                                      "force_N": [F * c / len(ids) for c in d]} for i in ids]}
                           for name, d, F in LOAD_CASES]
        s["design_criteria"] = {"limit_to_ultimate": 1.5,
                                "_about": "loads are LIMIT loads [Y]; ultimate = 1.5 × limit (CS 25.303)"}
        s["temperature_C"] = 300.0
        s["_about"] = (f"sketch2 {variant}, hypothesis {hyp}: load on {'arch A only' if hyp == 'A' else 'both arches, equal'}"
                       "; bolts fixed, small hole free; directions from the sketch, magnitudes [Y] invented — replace "
                       "on the day. Hole ids refer to THIS geometry: on the day copy load_cases and set the ids of the "
                       "day's own setup.json.")
        path = folder / f"setup_{hyp}.json"
        path.write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")
        out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", action="append", default=[], help="name=value (mm), e.g. L=180")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--no-preview", action="store_true")
    a = ap.parse_args(argv)
    p = dict(PARAMS)
    for kv in a.set:
        k, v = kv.split("=", 1)
        if k not in p:
            raise SystemExit(f"unknown parameter {k!r}; known: {', '.join(p)}")
        p[k] = float(v)
    for v in a.variants.split(","):
        r = check(v.strip(), p, not a.no_preview)
        r["proposals"] = [str(x) for x in proposals(v.strip(), p)]
        print(f"{v:12} solids {r['solids_in_step']} · volume {r['volume_mm3']:.0f} mm3 · steel {r['mass_steel_kg']:.3f} kg"
              f" · voxel {r['voxel_mm']:.2f} mm · holes found {len(r['holes_found_from_step'])} "
              f"(cut in drawing {r['holes_cut_in_drawing']}) · supports {len(r['supports'])} · load {r['load_holes']}"
              + (f" · preview {r['preview']['png']} ({r['preview']['audit_hata']} HATA)" if 'preview' in r else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
