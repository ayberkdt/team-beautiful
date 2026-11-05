"""AM overhang filter (aerokit.optimization.am_filter): exact adjoint and the 45-degree support rule."""
import numpy as np

from aerokit.optimization.am_filter import AMFilter2D, overhang_violations
from aerokit.verification import check, check_true


def test_backward_matches_finite_differences_every_base():
    rng = np.random.default_rng(3)
    x = rng.uniform(0.05, 0.95, (6, 7))
    w = rng.normal(size=(6, 7))
    for base in ("S", "N", "E", "W"):
        f = AMFilter2D(base, P=20.0, eps=1e-3)            # milder P keeps the finite-difference step meaningful
        g = f.backward(x, w)
        fd = np.zeros_like(x)
        h = 1e-6
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                xp, xm = x.copy(), x.copy()
                xp[i, j] += h
                xm[i, j] -= h
                fd[i, j] = (np.sum(w * f.forward(xp)) - np.sum(w * f.forward(xm))) / (2 * h)
        check(f"adjoint = finite differences, base {base}", float(np.abs(g - fd).max()), 0.0, atol=1e-5)


def test_support_rule():
    f = AMFilter2D("S")
    a = np.zeros((6, 8))
    a[1, 2:6] = 1.0                                       # a floating bar, nothing below it
    check_true("an unsupported bar is not printed", float(f.forward(a).max()) < 0.1)
    st = np.zeros((6, 8))
    for k in range(6):                                    # 45-degree staircase from the base plate
        st[5 - k, k] = 1.0
    check_true("a 45-degree staircase is printed", float(f.forward(st).min(initial=1.0, where=st > 0)) > 0.9)
    check("staircase has no overhang violation", float(overhang_violations(st)), 0.0, atol=0.0)
    check("floating bar has four violations", float(overhang_violations(a)), 4.0, atol=0.0)


def test_topology_with_am_filter_is_self_supporting():
    from aerokit.optimization import topo_mapped as tm
    from aerokit.optimization import topology as tp
    pr = tp.mbb_half(30, 10)
    free = tm.topopt_mapped(pr, 0.5, 1.5, move=0.1, max_iter=60)
    am = tm.topopt_mapped(pr, 0.5, 1.5, move=0.1, max_iter=60, am="S")
    v_free, v_am = overhang_violations(free["xfiz"], "S"), overhang_violations(am["xfiz"], "S")
    check_true(f"AM filter cuts overhang violations ({v_free} -> {v_am})", v_am < v_free)
    check_true("self-support costs stiffness", am["compliance_final"] >= free["compliance_final"] * 0.99)
