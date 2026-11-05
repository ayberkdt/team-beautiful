"""Automatic mesh-convergence tool: known convergence orders and Richardson extrapolation."""
import math

from aerokit.fem import Model
from aerokit.fem.mesh import mesh2d
from aerokit.fem.elements.line import Frame2D
from aerokit.fem.elements.plane import QM6, D_isotropic
from aerokit.fem.convergence import study
from aerokit.verification import check, check_true, expect_error

E, I, A = 70e9, 2e-6, 1e-3


def test_euler_buckling_order_and_richardson():
    L = 2.0
    pe = math.pi ** 2 * E * I / L ** 2

    def solve(n):
        m = Model([[L * i / n, 0.0] for i in range(n + 1)], 3)
        for i in range(n):
            m.add(Frame2D(i, i + 1, E, A, I))
        m.fix(0, [0, 1])
        m.fix(n, [1])
        m.load(n, 0, -1.0)
        return m.buckling(1)["lambda_"][0]
    s = study(solve, (4, 8, 16), label="P_cr")
    check("convergence: observed order p ≈ 4 for Euler buckling", s["p"], 4.0, rtol=2e-2,
            source="eigenvalue error O(h⁴) for the cubic Hermite element (measured with 4, 8, 16, 32 "
                   "during development)")
    check("convergence: Richardson value closer to P_E than the finest mesh", abs(s["f_ext"] / pe - 1), 0.0,
            atol=1e-6)
    check_true("convergence: Richardson error < finest-mesh error", abs(s["f_ext"] - pe) < abs(s["values"][-1] - pe))
    check_true("convergence: GCI bounds the true error (|f1 − P_E|/f1 ≤ GCI)",
          abs(s["values"][-1] - pe) / s["values"][-1] <= s["gci_fine"] + 1e-15, s["interpretation"])


def test_cook_membrane_richardson():
    def solve(n):
        X, conn, edges = mesh2d.cook(n, n, "QM6")
        m = Model(X, 2)
        for c in conn:
            m.add(QM6(c, D_isotropic(1.0, 1 / 3, "stress")))
        m.F += mesh2d.edge_load(X, edges["right"], traction=lambda x, y: (0.0, 1.0 / 16))
        for d in mesh2d.edge_nodes(edges["left"]):
            m.fix(d, [0, 1])
        u = m.static()["u"]
        C = mesh2d.find(X, lambda x, y: abs(x - 48) < 1e-9 and abs(y - 52) < 1e-9)[0]
        return u[2 * C + 1]
    s = study(solve, (4, 8, 16), label="v_C")
    check("convergence: Cook's membrane QM6 Richardson value ≈ 23.96", s["f_ext"], 23.96, rtol=2e-3,
            source="Bergan & Felippa 1985 ref. 23.9; Enercalc 64×64 incompatible 23.96 (as read in the source)")
    check_true("convergence: Cook's membrane monotonic (non-oscillatory)", not s["oscillatory"], s["interpretation"])


def test_input_errors():
    expect_error("two levels raise an error", study, lambda n: 1.0, (4, 8), error=ValueError)
    expect_error("non-increasing levels raise an error", study, lambda n: 1.0, (8, 4, 16), error=ValueError)
    s = study(lambda n: 2.0, (2, 4, 8))
    check("constant result: GCI = 0", s["gci_fine"], 0.0)
