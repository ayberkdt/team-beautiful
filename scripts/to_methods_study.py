"""Studies behind docs/16 (TO methods catalogue): stress-constrained L-beam against Holmberg et al. (2013), the
compliance design at the same mass, robust/projected MBB and the AM filter at the paper's defaults.

    python scripts/to_methods_study.py            # ~15-25 min -> studies/scenarios/to_methods_study.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.optimization import projection as pj  # noqa: E402
from aerokit.optimization import stress_topo as st  # noqa: E402
from aerokit.optimization import topo_mapped as tm  # noqa: E402
from aerokit.optimization import topology as tp  # noqa: E402
from aerokit.optimization.am_filter import AMFilter2D, overhang_violations  # noqa: E402

OUT = ROOT / "studies" / "scenarios" / "to_methods_study.json"
RHO_AL = 2.8e-9                        # t/mm3, Holmberg's aluminium; thickness 1 mm


def _save(data: dict) -> None:
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")


def stress_l_beam(n: int) -> dict:
    pr, ev, h = st.holmberg_l_beam(n)
    t0 = time.time()
    r = st.topopt_stress(pr, 350.0, rmin=1.5, evaluate=ev, n_clusters=10, h=h, max_iter=1000, verbose=True)
    free = pr.passive == 0
    mass_g = lambda xf: float(np.sum(xf) * h * h * 1.0 * RHO_AL * 1e6)          # noqa: E731  (t -> g)
    xf = pr.grid.vector(r["xfiz"])
    out = {"grid": n, "h_mm": h, "iterations": r["iteration"], "seconds": round(time.time() - t0, 1),
           "mass_g": mass_g(xf), "mass_fraction_free": r["mass_fraction"], "compliance_Nmm": r["compliance"],
           "max_stress_ratio": r["max_stress_ratio"], "share_over_limit": r["share_over_limit"],
           "constraints": np.round(r["constraints"], 4).tolist(), "gray": tp.gray_measure(xf[free]),
           "density": np.asarray(r["xfiz"]).round(3).tolist(),
           "holmberg_table1": {"mass_g": 24.76, "compliance_Nmm": 10330}}
    # compliance design with the same total volume
    vol = float(xf.mean())
    rc = tp.topopt(pr, vol, 1.5, ft=2, max_iter=400)
    xc = pr.grid.vector(rc["xfiz"])
    sc = st.StressConstraint(pr, 350.0, ev, 10, h=h)
    _, Uc = sc.solve(xc)
    s = sc.stresses(xc, Uc)[sc.eval_idx] / 350.0
    out["compliance_design"] = {"mass_g": mass_g(xc), "compliance_Nmm": float(rc["compliance_final"]),
                                "max_stress_ratio": float(s.max()),
                                "share_over_limit": float(np.mean(s[xc[sc.eval_idx] > 0.5] > 1.0)),
                                "density": np.asarray(rc["xfiz"]).round(3).tolist()}
    return out


def robust_mbb() -> dict:
    pr = tp.mbb_half(120, 40)
    res = {}
    for key, kw in (("density", None), ("projected", {"eta": 0.5}), ("robust", {"robust": 0.25})):
        if kw is None:
            r = tp.topopt(pr, 0.5, 4.0, ft=2, max_iter=400)
            res[key] = {"compliance": float(r["compliance_final"]), "gray": float(r["gray"]),
                        "volume": float(np.mean(r["xfiz"])), "density": np.asarray(r["xfiz"]).round(3).tolist()}
            continue
        r = pj.topopt_projected(pr, 0.5, 4.0, max_iter=600, **kw)
        res[key] = {"compliance": float(r["compliance_final"]), "gray": float(r["gray"]),
                    "volume": r["volume_blueprint"], "iterations": r["iteration"], "beta": r["beta_final"],
                    "max_jump": float(np.max(r["compliance"][1:] / r["compliance"][:-1])),
                    "density": np.asarray(r["xfiz"]).round(3).tolist()}
        if "robust" in kw:
            res[key].update(compliance_eroded=r["compliance_eroded"], compliance_dilated=r["compliance_dilated"],
                            volume_dilated=r["volume_dilated"],
                            min_member_rule_elements=4.0 * pj.min_size_ratio(0.75))
    return res


def am_defaults() -> dict:
    pr = tp.mbb_half(60, 20)
    out = {}
    for key, f, move in (("cilamce_P80_eps1e-3_move0.1", AMFilter2D("S", P=80.0, eps=1e-3), 0.1),
                         ("langelaar_P40_eps1e-4_move0.1", AMFilter2D("S"), 0.1),
                         ("langelaar_P40_eps1e-4_move0.05", AMFilter2D("S"), 0.05)):
        r = tm.topopt_mapped(pr, 0.5, 2.0, move=move, max_iter=300, am=f)
        out[key] = {"compliance": float(r["compliance_final"]), "violations": overhang_violations(r["xfiz"], "S"),
                    "gray": float(r["gray"]), "iterations": r["iteration"], "max_density": float(np.max(r["xfiz"]))}
        print(key, out[key], flush=True)
    return out


def main() -> int:
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 100
    data: dict = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for key, fn in (("am", am_defaults), ("robust_mbb", robust_mbb), ("stress_l_beam", lambda: stress_l_beam(n))):
        if key in data and "--redo" not in sys.argv:
            continue
        print(f"== {key}", flush=True)
        data[key] = fn()
        _save(data)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "density"} if isinstance(v, dict) else v
                      for k, v in data.items()}, default=str)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
