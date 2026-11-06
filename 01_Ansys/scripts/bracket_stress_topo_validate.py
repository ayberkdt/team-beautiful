"""Validation runs of the 3-D stress-constrained topology (aerokit.bracket.stress3d).

    python 01_Ansys/scripts/bracket_stress_topo_validate.py lbeam --n 100 --iters 1000 [--proj] [--adaptive]
    python 01_Ansys/scripts/bracket_stress_topo_validate.py cantilever --iters 100 [--proj] [--adaptive]

* ``lbeam``: Holmberg, Torstenfelt & Klarbring 2013 §9.1 L-beam (L = 200 mm, 1500 N, aluminium E 71 GPa, ν 0.33,
  σ̄ 350 MPa, r0 = 1.5, 10 stress-level clusters, p = 8, q = ½, 3 × 2 load elements solid) extruded one voxel thick;
  mass in g for the published 1 mm beam with ρ = 2.8e-9 t/mm³ (as in prev_guess/01_Ansys/scripts/to_methods_study.py), compliance per
  1 mm of thickness. Published (Table 1, LiU post-print, read 3 Nov): 24.76 g, 10 330 N·mm.
* ``cantilever``: 40 × 12 × 6 voxels of 1 mm, clamped at x = 0, 500 N down on the lower 4 mm of the tip face,
  2 tip layers solid, σ̄ 250 MPa, no evaluation in the 2 layers at the clamp (singular edge).

Prints one JSON line (and appends it to 01_Ansys/outputs/validation/stress_topo_runs.jsonl): mass, grey
level, worst cluster P-norm, max relaxed stress ratio and the threshold (0.5) re-analysis true stress ratio.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.bracket import stress3d as s3  # noqa: E402
from aerokit.bracket import voxfem as vf  # noqa: E402

OUT = ROOT / "01_Ansys" / "outputs" / "validation" / "stress_topo_runs.jsonl"


def cantilever() -> tuple[vf.VoxelMesh, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    h, nx, ny, nz = 1e-3, 40, 12, 6
    m = vf.VoxelMesh(np.ones((nx, ny, nz), bool), h)
    fix = m.nodes_where(lambda X: np.isclose(X[:, 0], 0))
    fixed = (3 * fix[:, None] + np.arange(3)).ravel()
    tip = m.nodes_where(lambda X: np.isclose(X[:, 0], nx * h) & (X[:, 1] < 4 * h + 1e-9))
    F = np.zeros(m.ndof)
    F[3 * tip + 1] = -500.0 / len(tip)
    keep = m.ijk[:, 0] >= nx - 2
    return m, F, fixed, keep, ~keep & (m.ijk[:, 0] >= 2), 250e6


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case", choices=("lbeam", "cantilever"))
    ap.add_argument("--n", type=int, default=100, help="L-beam grid (n × n)")
    ap.add_argument("--iters", type=int, default=100)
    ap.add_argument("--proj", action="store_true", help="tanh projection with β continuation to 16")
    ap.add_argument("--adaptive", action="store_true", help="Le et al. adaptive normalisation of the cluster norms")
    ap.add_argument("--verified", action="store_true", help="projection + threshold re-analysis rounds "
                    "(stress3d.optimize_stress_verified)")
    ap.add_argument("--no-save", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    if a.case == "lbeam":
        mesh, F, fixed, keep, ev = s3.l_beam(a.n)
        sb, kw = 350e6, {"beta_start": a.iters // 3, "beta_every": max(10, a.iters // 12)}
    else:
        mesh, F, fixed, keep, ev, sb = cantilever()
        kw = {"beta_start": 40, "beta_every": 15}
    if a.verified:
        r = s3.optimize_stress_verified(mesh, F, fixed, sb, evaluate=ev, keep=keep, rmin=1.5, max_iter=a.iters,
                                        beta_max=16, n_clusters=10, **kw)
    else:
        r = s3.optimize_stress(mesh, F, fixed, sb, evaluate=ev, keep=keep, rmin=1.5, max_iter=a.iters,
                               projection=a.proj, beta_max=16, n_clusters=10, adaptive=a.adaptive, **kw)
    chk = s3.threshold_check(mesh, r["xphys"], F, fixed, sb, ev)
    row = {"case": a.case, "n": a.n if a.case == "lbeam" else None, "iters": r["iterations"],
           "proj": a.proj or a.verified,
           "adaptive": a.adaptive, "mass_fraction_design": round(r["mass_fraction"], 4),
           "mean_density_all": round(float(r["xphys"].mean()), 4), "grey_percent": round(r["grey_percent"], 2),
           "max_cluster_pnorm": round(r["max_pnorm"], 4), "max_relaxed_ratio": [round(v, 3) for v in r["max_stress_ratio"]],
           "threshold_true_ratio": [round(v, 3) for v in chk["max_true_ratio"]],
           "threshold_solid_fraction": round(chk["solid_fraction"], 4), "beta": r["beta"],
           "fallbacks": len(r["history"].get("fallbacks", [])), "seconds": round(time.time() - t0, 1),
           "stamp": time.strftime("%Y-%m-%d %H:%M"), "verified_mode": a.verified,
           "rounds_log": r.get("rounds_log"), "verified": r.get("verified")}
    if a.case == "lbeam":
        E, n = 71e9, a.n
        full_g = (n * n - (n - round(0.4 * n)) ** 2) * (200.0 / n) ** 2 * 2.8e-3
        row["mass_g_1mm"] = round(row["mean_density_all"] * full_g, 2)
        row["compliance_Nmm_1mm"] = round(r["compliance_unitE"][0] / E * 1e3 * (1e-3 / (0.2 / n)), 1)
        row["holmberg_2013_table1"] = {"mass_g": 24.76, "compliance_Nmm": 10330}
    line = json.dumps(row)
    print(line)
    if not a.no_save:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
