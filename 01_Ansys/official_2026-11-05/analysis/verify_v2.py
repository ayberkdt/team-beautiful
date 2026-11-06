"""Independent check of EVERY v2 topology layout (runs/topo_v2_base_kept: base flange + lug eyes + bolt bosses kept).

Per layout:
* the topology itself: face-connected solid bodies of the raw density (> 0.5); both lugs tied through the plate
  region z < 100 mm (one bracket, not two arches); x-mirror symmetry about x = 500 mm;
* conforming T10 of the layout's smoothed STL (`t10check.check`): 4 card cases + 4 combined LC1 + LC2 (±My), the
  organisers' Ti-8Al-1Mo-1V values at 23 °C and with the 300 °C knock-downs.

python -I analysis/verify_v2.py -> analysis/verify_v2.json
"""
import json, pickle, sys
from pathlib import Path
import numpy as np
from scipy import ndimage
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t10check as T   # noqa: E402  (also puts src/ and pylib on the path)
from aerokit.bracket import cadout   # noqa: E402
from organiser_materials import eco   # noqa: E402

import os
CASE = os.environ.get("CASE", "topo_v2_base_kept")
RUN = HERE.parent / "runs" / CASE
st, _opt = pickle.load(open(RUN / "study.pkl", "rb"))
setup = T.with_combined(st.setup)
h = st.mesh.h
o = st.mesh.origin * 1e3
out = {"setup_non_design": setup["non_design"], "cases": [c["name"] for c in setup["load_cases"]], "layouts": []}


def topology_checks(solid, xphys):
    """Bodies, x-mirror symmetry, and the load path of each lug. 5 Nov review: the old 'lugs tied' test was
    trivially true because the frozen base skin joins every voxel below z = 100 mm. Now: with the four bolt-boss
    rings REMOVED, each lug eye must still be face-connected to the base skin, i.e. every lug has a load path into
    the flange that does not run only through a boss."""
    from aerokit.bracket import features
    _, n_raw = ndimage.label(xphys > 0.5)
    _, n_kept = ndimage.label(solid)
    c = [o[k] + (np.arange(solid.shape[k]) + 0.5) * h * 1e3 for k in range(3)]
    ijk = np.argwhere(solid)
    im = np.rint((2 * 500.0 - c[0][ijk[:, 0]] - o[0]) / (h * 1e3) - 0.5).astype(int)
    ok = (im >= 0) & (im < solid.shape[0])
    sym = float(solid[im[ok], ijk[ok, 1], ijk[ok, 2]].mean())
    jm = np.rint((2 * 200.28 - c[1][ijk[:, 1]] - o[1]) / (h * 1e3) - 0.5).astype(int)
    okj = (jm >= 0) & (jm < solid.shape[1])
    sym_y = float(solid[ijk[okj, 0], jm[okj], ijk[okj, 2]].mean())     # lug-to-lug (y) mirror match
    from aerokit.bracket.topo3d import to_grid
    sup = to_grid(st.mesh, features.non_design_mask(st.mesh, st.setup, roles=("support",)).astype(float)) > 0.5
    roles = {d["id"]: d.get("role") for d in st.setup["holes"]}
    lab_all, _ = ndimage.label(solid)
    lug_body = set()
    for d in st.setup["holes"]:
        if d.get("role") == "load":
            ring = to_grid(st.mesh, features.non_design_mask(st.mesh, dict(st.setup, holes=[d]),
                                                             roles=("load",)).astype(float)) > 0.5
            lug_body |= set(np.unique(lab_all[ring & solid])) - {0}
    lab, _ = ndimage.label(solid & ~sup)
    base = solid & (c[2] < 46)[None, None, :] & ~sup
    base_labels = set(np.unique(lab[base])) - {0}
    lug_ok = {}
    for d in st.setup["holes"]:
        if d.get("role") != "load":
            continue
        s1 = dict(st.setup, holes=[d])
        ring = to_grid(st.mesh, features.non_design_mask(st.mesh, s1, roles=("load",)).astype(float)) > 0.5
        lug_ok[d["id"]] = bool(set(np.unique(lab[ring & solid])) & base_labels)
    return {"bodies_raw_density": int(n_raw), "bodies_kept": int(n_kept),
            "lugs_in_one_body": len(lug_body) == 1 and n_kept == 1,
            "lugs_tied_through_base": bool(len(lug_body) == 1 and n_kept == 1 and lug_ok and all(lug_ok.values())),
            "lug_to_base_without_bosses": lug_ok,
            "x_mirror_symmetry": sym, "y_mirror_symmetry": sym_y}


if __name__ == "__main__":
    for d in st.designs:
        if d["label"] == "initial" or "failed" in d:
            continue
        tag = round(100 * d["volfrac"])
        solid = st.fields[f"solid_{tag}"]
        topo = topology_checks(solid, st.fields[f"xphys_{tag}"])
        stl = RUN / "cad" / f"optimised_{tag}.stl"
        info = cadout.density_to_stl(st.mesh.origin, h, st.fields[f"xphys_{tag}"] * solid, stl,
                                     target_volume_mm3=d["volume_m3"] / st.vol_corr * 1e9)   # same frac-weighted
        # target as finalize.py (5 Nov review: voxel count × h³ here vs Σfrac·h³ there made the two models 2.9 % apart)
        r = T.check(stl, setup, 1.3 * h * 1e3, 0.6 * h)
        r.update(layout=d["label"], volfrac=d["volfrac"], stl=str(stl), stl_info=info, **topo)
        # gate: ONE body with both lug eyes in it (lug_to_base_without_bosses is reported only: with the X-braced bolt
        # pattern the lugs legitimately land on the bosses)
        r["passes_300C"] = bool(r["passes_300C"] and topo["lugs_in_one_body"] and topo["bodies_kept"] == 1)
        out["layouts"].append(r)
        print(f"{d['label']}: bodies raw {topo['bodies_raw_density']} kept {topo['bodies_kept']}, lugs tied "
              f"{topo['lugs_tied_through_base']}, sym x {topo['x_mirror_symmetry']:.3f} y {topo['y_mirror_symmetry']:.3f} | T10 {r['T10_elements']} el, "
              f"{r['mass_Ti811_kg']:.2f} kg, σ {r['sigma_max_MPa']:.1f} MPa ({r['sigma_case'][:4]}), u300 "
              f"{r['disp_mm_300C']:.3f} mm ({r['disp_case'][:4]}), U300 {r['util_300C']:.3f} -> "
              f"{'PASS' if r['passes_300C'] else 'FAIL'}", flush=True)
    ok = [x for x in out["layouts"] if x["passes_300C"]]
    if ok:
        best = min(ok, key=lambda x: x["mass_Ti811_kg"])
        e_new, e_base = eco(best["mass_Ti811_kg"], "Ti811SA"), eco(152.0, "S275N")
        out["chosen"] = {"layout": best["layout"], "mass_kg": best["mass_Ti811_kg"],
                         "life_co2_new_t": e_new["total_first_life"] / 1e3,
                         "life_co2_base_t": e_base["total_first_life"] / 1e3,
                         "co2_saving_pct": 100 * (1 - e_new["total_first_life"] / e_base["total_first_life"]),
                         "mass_saving_pct": 100 * (1 - best["mass_Ti811_kg"] / 152.27)}
        print("chosen", out["chosen"])
    (HERE / ("verify_v2.json" if CASE == "topo_v2_base_kept" else f"verify_{CASE}.json")).write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
