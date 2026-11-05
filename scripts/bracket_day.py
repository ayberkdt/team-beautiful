"""Competition-day bracket command: geometry in, every deliverable out.

    python scripts/bracket_day.py <geometry> [--setup setup.json] [--case NAME] [options]

<geometry>: a parametric drawing JSON (see aerokit.bracket.geometry), or STL/OBJ/PLY/STEP/IGES (STEP/IGES need gmsh
in D:/tmp_ideathon/pylib, see docs/22). Output: studies/final_2026/ansys/out/<case>/ (report.md, result.json,
setup.json, cad/, materials/, eco_audit.*, crosscheck_template*.csv, figures/, density + loads for the film).

First run without --setup: holes are detected and a set-up is PROPOSED and saved as out/<case>/setup.json. Edit roles,
supports, load directions and magnitudes there (mm, N, N m) and run again: the edited copy is picked up.

Evaluate a shape someone else optimised (Ansys Discovery/Mechanical STL export) with our set-up:
    python scripts/bracket_day.py ansys_result.stl --unit mm --setup studies/final_2026/ansys/out/day1/setup.json --case day1_ansys --evaluate-only

Examples
    python scripts/bracket_day.py studies/final_2026/ansys/inputs/sketch_bracket.json --case sketch
    python scripts/bracket_day.py studies/final_2026/ansys/inputs/ge_bracket.json --setup studies/final_2026/ansys/inputs/ge_setup.json --case ge
    python scripts/bracket_day.py organisers.step --unit mm --magnitude 5000 --case day1 --quick
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for extra in (r"D:\tmp_ideathon\pylib",):
    if os.path.isdir(extra) and extra not in sys.path:
        sys.path.append(extra)

from aerokit.bracket import pipeline, report  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("geometry", help="drawing JSON, STL/OBJ/PLY or STEP/IGES")
    gg = ap.add_argument_group("geometry")
    gg.add_argument("--unit", default="mm", help="length unit of STL/OBJ/PLY input (STEP carries its own)")
    gg.add_argument("--align", choices=("pca",), help="rotate a STL/STEP part onto its principal axes")
    gg.add_argument("--rotate", help="rotate a STL/STEP part: 'rx,ry,rz' in degrees (applied about its centroid)")
    gg.add_argument("--bodies", help="multi-body STEP: 'all' (fused, default), 'largest' or 1-based indices '1,3'")
    gi = ap.add_argument_group("loads and materials")
    gi.add_argument("--setup", help="edited set-up JSON (else out/<case>/setup.json, else proposed)")
    gi.add_argument("--temperature", type=float, help="working temperature in C (default: set-up, 300)")
    gi.add_argument("--materials", help="organisers' material list (CSV/YAML/TXT); every name must match the pool, "
                    "else the run stops with a table (out/<case>/materials_match.md)")
    gi.add_argument("--magnitude", type=float, default=10_000.0, help="proposed load magnitude [N] (no set-up)")
    gi.add_argument("--calibrate", type=float, help="scale all loads so the baseline initial design has this "
                    "utilisation (use only when no loads are given)")
    gm = ap.add_argument_group("modes")
    gr = ap.add_argument_group("run size")
    gm.add_argument("--quick", action="store_true", help="12k elements, 2 volume fractions, 30 iterations")
    gr.add_argument("--elements", type=int, default=25_000, help="target number of voxel elements")
    gr.add_argument("--voxel", type=float, help="voxel edge in mm (default: from --elements)")
    gr.add_argument("--volfracs", default="0.5,0.35,0.25", help="volume fractions to optimise, comma separated")
    gr.add_argument("--iters", type=int, default=50, help="optimisation iterations per volume fraction")
    gm.add_argument("--evaluate-only", action="store_true",
                    help="no topology: evaluate the given shape (e.g. an Ansys/Discovery result STL) with --setup")
    gc = ap.add_argument_group("checks")
    gc.add_argument("--am-filter", action="store_true", help="45 deg overhang filter along the build direction")
    gc.add_argument("--no-convergence", action="store_true", help="skip the 3-level voxel convergence")
    gc.add_argument("--no-tet", action="store_true", help="skip the conforming T10 check (gmsh)")
    gc.add_argument("--tet-levels", type=int, default=2, choices=(1, 2, 3), help="T10 mesh levels of the initial design")
    go = ap.add_argument_group("output")
    go.add_argument("--case", help="output folder name (default: geometry file stem)")
    go.add_argument("--out", default=str(ROOT / "studies" / "final_2026" / "ansys" / "out"))
    go.add_argument("--handoff", action="store_true", help="also write studies/final_2026/ansys/handoff/<case>/")
    go.add_argument("--no-figures", action="store_true")
    gm.add_argument("--report-only", action="store_true", help="rewrite the deliverables from out/<case>/study.pkl")
    gm.add_argument("--reverify", action="store_true", help="with --report-only: redo the T10 checks and selection")
    a = ap.parse_args(argv)
    opt = pipeline.Options(target_elements=a.elements, voxel_mm=a.voxel, temperature_C=a.temperature,
                           volfracs=tuple(float(v) for v in a.volfracs.split(",")), max_iter=a.iters,
                           am_filter=a.am_filter, convergence=not a.no_convergence, unit=a.unit,
                           magnitude_N=a.magnitude, tet_check=not a.no_tet,
                           tet_sizes_vox=(2.0, 1.3, 0.9)[:a.tet_levels], calibrate_utilisation=a.calibrate)
    if a.quick:
        opt.target_elements, opt.volfracs, opt.max_iter = 12_000, (0.4, 0.25), 30
    if a.evaluate_only:
        opt.volfracs = ()
    rot = tuple(float(v) for v in a.rotate.split(",")) if a.rotate else None
    case = a.case or Path(a.geometry).stem
    out = Path(a.out) / case
    if a.materials:
        from aerokit.bracket import matlist
        mres = matlist.resolve(matlist.read_list(a.materials))
        out.mkdir(parents=True, exist_ok=True)
        (out / "materials_match.md").write_text(f"# Material list `{a.materials}` matched to the pool\n\n"
                                                + matlist.markdown(mres), encoding="utf-8")
        for r in mres["rows"]:
            flag = " ROUTE DIFFERS" if r.get("route_differs") else ""
            print(f"material '{r['entry']}' -> {r['status']}{flag}: {r.get('name', '-')}"
                  + (f" ({r['note']})" if r.get("note") else ""))
        if not mres["ok"]:
            print(f"RESULT: STOPPED - {len(mres['problems'])} material name(s) not matched to the pool. NEXT: fix "
                  f"the names in {a.materials} (see {out / 'materials_match.md'}) and run again")
            return 2
        opt.candidates = mres["keys"]
    bodies = None if a.bodies in (None, "all", "largest") else [int(v) for v in a.bodies.split(",")]
    g = pipeline.load_geometry(a.geometry, unit=a.unit, rotate=rot, align=a.align,
                               bodies=a.bodies if bodies is None else bodies, work_dir=out / "cad")
    if g.bodies:
        for b in g.bodies["bodies"]:
            mark = "used" if b["index"] in g.bodies["selected"] else "dropped"
            print(f"STEP body {b['index']}: {b['volume_mm3']:.0f} mm3, bbox {b['bbox_mm']} mm -> {mark}")
        print(f"fused into one solid: {g.bodies['fused_volume_mm3']:.0f} mm3 (overlap removed "
              f"{g.bodies['overlap_mm3']:.0f} mm3, e.g. inserted bolts) -> {g.bodies['file']}")
    import pickle
    pk = out / "study.pkl"
    if a.report_only and pk.exists():
        with pk.open("rb") as f:
            st, opt = pickle.load(f)  # noqa: S301 - our own cache file written by this script
        st.out = out                  # write where --out/--case say, not where the cache was made (copied caches)
        if not hasattr(st, "verification"):                   # study cached by an older version
            st.verification, st.stress_factors = [], {}
        pipeline.decide(st, opt)
        if "thermal" not in st.baseline:
            pipeline.thermal_sensitivity(st, opt)
        checked = bool(st.verification) or bool((getattr(st, "tet", {}) or {}).get("initial"))
        if opt.tet_check and not a.no_tet and (not checked or a.reverify):    # GE: nothing passes → no verification
            cands = [pipeline.matdata.get(k) for k in (opt.candidates or pipeline.matdata.names())]
            pipeline.conforming_check(st, g, opt)
            pipeline.verify_choice(st, g, opt, cands)
            with pk.open("wb") as f:
                pickle.dump((st, opt), f)
    else:
        st = pipeline.run_design(g, out, opt, a.setup)
        with pk.open("wb") as f:
            pickle.dump((st, opt), f)
    files = report.write_all(st, g, opt, figures=not a.no_figures)
    if a.handoff:
        from aerokit.bracket import handoff
        h = handoff.write(st, opt, ROOT / "studies" / "final_2026" / "ansys" / "handoff" / case, a.geometry)
        print(f"film hand-off: {h['folder']}")
    for p, cap in files.get("figures", {}).items():
        print(f"figure: {p} - {cap}")
    print(f"report: {out / 'report.md'}")
    if st.choice:
        saving = 100 * (1 - st.choice["mass_kg"] / st.baseline["mass_kg"])
        change = f"{saving:.1f} % lighter" if saving >= 0 else f"{-saving:.1f} % heavier"
        if st.choice.get("passes", True):
            print(f"RESULT: {st.choice['material']} / {st.choice['design']} / {st.choice['mass_kg']:.4f} kg vs "
                  f"baseline {st.baseline['mass_kg']:.4f} kg ({change}). NEXT: check setup.json, then fill the "
                  f"ansys column of {out / 'crosscheck_template.csv'}")
        else:
            print(f"RESULT: FAILS - no material passes; least utilised {st.choice['material']} / "
                  f"{st.choice['design']} (utilisation {st.choice['utilisation']:.2f}, {change}). NEXT: check loads, "
                  f"criterion and sharp edges in {out / 'setup.json'}")
    else:
        print(f"RESULT: no AM material passes on any layout. NEXT: check loads and criteria in {out / 'setup.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
