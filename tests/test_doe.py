"""Response-surface helper (aerokit.design.doe) on functions with known answers."""
from aerokit.design import doe
from aerokit.verification import check, check_true, expect_error


def test_plan_and_exact_quadratic():
    pts = doe.plan({"t": (1.0, 3.0), "r": (0.0, 2.0)}, levels=3)
    check("3 x 3 full factorial", float(len(pts)), 9.0, atol=0.0)
    f = lambda p: 2.0 + 0.5 * p["t"] - 0.3 * p["r"] + 0.2 * p["t"] * p["r"] + 0.1 * p["t"] ** 2  # noqa: E731
    s = doe.fit(pts, [f(p) for p in pts])
    check("quadratic recovered exactly inside the box", float(s({"t": 2.3, "r": 1.7})[0]), f({"t": 2.3, "r": 1.7}),
          rtol=1e-10)
    check("R2 = 1 for an exact quadratic", s.r2, 1.0, rtol=1e-12)
    check("leave-one-out error = 0 for an exact quadratic", s.loo_rmse, 0.0, atol=1e-9)


def test_constrained_optimum():
    # minimise mass = x^2 + y^2 subject to stress = 10 - x - y <= 6 (i.e. x + y >= 4): optimum (2, 2), mass 8
    pts = doe.plan({"x": (0.0, 4.0), "y": (0.0, 4.0)}, levels=3)
    mass = doe.fit(pts, [p["x"] ** 2 + p["y"] ** 2 for p in pts])
    stress = doe.fit(pts, [10 - p["x"] - p["y"] for p in pts])
    best = doe.optimise(mass, {"stress": (stress, 6.0)}, n=81)
    check("constrained optimum x", best["point"]["x"], 2.0, atol=0.06)
    check("constrained optimum mass", best["objective"], 8.0, rtol=0.01)
    check_true("constraint met at the optimum", best["stress_pred"] <= 6.0 + 1e-9)
    check_true("infeasible limit reported", not doe.optimise(mass, {"stress": (stress, 1.0)})["feasible"])
    expect_error("too few runs for the quadratic", doe.fit, pts[:4], [1, 2, 3, 4], error=ValueError)
