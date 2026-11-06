"""Model 3 of 3: finalize the chosen v2 topology layout into a manufacturing-ready solid and re-verify it.

  model 1  initial design            visuals/initial_exact.step (S275N, 152.27 kg)
  model 2  topology-optimised shape  runs/topo_v2_base_kept/cad/optimised_<tag>.stl (smoothed iso-surface)
  model 3  finalized shape           runs/topo_v2_base_kept/cad/finalized_<tag>.stl (this script)

python -I analysis/finalize_v2.py <tag> [r_open_mm r_close_mm] -> analysis/finalize_v2_<tag>.json
"""
import json, pickle, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t10check as T   # noqa: E402
from aerokit.bracket import pipeline   # noqa: E402
from aerokit.bracket.finalize import FinalizeParams, finalize   # noqa: E402
from organiser_materials import eco   # noqa: E402

tag = int(sys.argv[1])
prm = FinalizeParams()
if len(sys.argv) > 3:
    prm.r_open_mm, prm.r_close_mm = float(sys.argv[2]), float(sys.argv[3])
import os
CASE = os.environ.get("CASE", "topo_v2_base_kept")
RUN = HERE.parent / "runs" / CASE
st, _opt = pickle.load(open(RUN / "study.pkl", "rb"))
geom = pipeline.load_geometry(HERE.parent / "visuals" / "initial_exact.step")
stl = RUN / "cad" / f"finalized_{tag}.stl"
if os.environ.get("T10_ONLY") and stl.exists():         # re-check an existing finalized STL (no re-finalize)
    fin = json.loads((HERE / f"finalize_{CASE}_{tag}.json").read_text(encoding="utf-8"))["finalize"]
else:
    fin = finalize(st, geom, tag, stl, prm)
setup = T.with_combined(st.setup)
# bores are exact cylinders on the finalized part, so a tighter node tolerance than for the voxel iso-surface
r = T.check(stl, setup, 1.3 * st.mesh.h * 1e3, 0.25 * st.mesh.h)
e_new, e_base = eco(r["mass_Ti811_kg"], "Ti811SA"), eco(152.0, "S275N")
r["eco"] = {"life_co2_new_t": e_new["total_first_life"] / 1e3, "life_co2_base_t": e_base["total_first_life"] / 1e3,
            "co2_saving_pct": 100 * (1 - e_new["total_first_life"] / e_base["total_first_life"]),
            "mass_saving_pct": 100 * (1 - r["mass_Ti811_kg"] / 152.27), "phases_new": e_new, "phases_base": e_base}
# manufacturing gate (5 Nov review: the old voids test was always true): one body, watertight, no enclosed void left
# (voids are filled by construction, so the count only reports how many were filled), wall p1 >= 1.2 mm (LPBF
# unsupported-wall rule, literature_finalize.md §6.6). Overhang is reported, not gated (supports are allowed).
manuf_ok = bool(fin["bodies"] == 1 and fin["open_or_nonmanifold_edges"] == 0 and fin["wall_p1_mm"] >= 1.2)
out = {"finalize": fin, "t10": r, "manufacturing_checks_pass": bool(manuf_ok),
       "passes_all": bool(manuf_ok and r["passes_300C"])}
(HERE / f"finalize_{CASE}_{tag}.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
print(f"finalized {tag}: {r['mass_Ti811_kg']:.2f} kg, σ {r['sigma_max_MPa']:.1f} MPa ({r['sigma_case'][:4]}) at "
      f"{r['sigma_at_mm']}, u300 {r['disp_mm_300C']:.3f} mm, U300 {r['util_300C']:.3f}, CO2 {r['eco']['life_co2_new_t']:.2f} t "
      f"({r['eco']['co2_saving_pct']:.1f} %) -> {'PASS' if out['passes_all'] else 'FAIL'}")
