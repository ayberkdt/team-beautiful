"""Discovery-style constraints for SIMP (aerokit.optimization.topo_mapped)."""
import numpy as np

from aerokit.optimization import topo_mapped as tm
from aerokit.optimization import topology as tp
from aerokit.verification import check, check_true


def test_identity_map_reproduces_topopt_density_filter():
    pr = tp.mbb_half(30, 10)
    ref = tp.topopt(pr, 0.5, 1.5, ft=2, max_iter=40)
    got = tm.topopt_mapped(pr, 0.5, 1.5, max_iter=40)
    check("identity map: same final compliance as topopt ft=2", got["compliance_final"], ref["compliance_final"],
          rtol=1e-6)
    check("identity map: same design", float(np.abs(got["xfiz"] - ref["xfiz"]).max()), 0.0, atol=1e-6)


def test_mirror_symmetry_is_exact_under_an_asymmetric_load():
    g = tp.Grid2D(40, 20)
    fixed = [g.dof(ix, 20, d) for ix in (0, 40) for d in (0, 1)]          # both bottom corners pinned
    pr = tp.Problem(g, {g.dof(12, 0, 1): -1.0}, fixed)                    # load off-centre on the top edge
    P = tm.group_map(g, mirror=[1])
    r = tm.topopt_mapped(pr, 0.4, 1.5, P=P, max_iter=60)
    free = tm.topopt_mapped(pr, 0.4, 1.5, max_iter=60)
    check("mirrored design is symmetric", tm.symmetry_error(g, g.vector(r["xfiz"]), 1), 0.0, atol=1e-12)
    check_true("the unconstrained design is not symmetric", tm.symmetry_error(g, g.vector(free["xfiz"]), 1) > 0.1)
    check_true("symmetry costs stiffness under an off-centre load",
               r["compliance_final"] >= free["compliance_final"] * (1 - 1e-6))
    check("volume target met", float(r["xfiz"].mean()), 0.4, rtol=2e-3)


def test_extrusion_and_min_volume():
    pr = tp.cantilever_3d(12, 6, 4)
    P = tm.group_map(pr.grid, extrude=[2])
    r = tm.topopt_mapped(pr, 0.3, 1.5, P=P, max_iter=25)
    check("extruded along z: no variation in z", tm.extrusion_error(pr.grid, pr.grid.vector(r["xfiz"]), 2), 0.0,
          atol=1e-12)
    # smallest volume whose compliance stays below twice the compliance at 50 %
    pr2 = tp.mbb_half(30, 10)
    c50 = tp.topopt(pr2, 0.5, 1.5, ft=2, max_iter=40)["compliance_final"]
    out = tm.min_volume(lambda v: tp.topopt(pr2, v, 1.5, ft=2, max_iter=40),
                        lambda d: d["compliance_final"] <= 2 * c50, lo=0.15, hi=0.5, tol=0.02)
    check_true("bisection returns a passing design below the starting volume",
               out["feasible"] and out["volume"] < 0.5 and out["design"]["compliance_final"] <= 2 * c50)
