"""MITC4 plate element tests.

References are computed independently of the FEM:
- Navier double sine series, simply supported rectangular plate (Timoshenko & Woinowsky-Krieger,
  Theory of Plates and Shells, 2nd ed. 1959, §30; square plate center coefficient α = 0.00406)
- Natural frequencies of a simply supported plate ω_mn = π²(m²/a² + n²/b²)√(D/ρh) (Leissa, NASA SP-160, 1969)
- Buckling of a simply supported plate k = (mb/a + a/(mb))² (Timoshenko & Gere 1961 §9.2)
- Cantilever strip with ν = 0: Timoshenko beam δ = qL⁴/8D + qL²/(2κGh)
"""
import math
import numpy as np

from aerokit.fem import Model
from aerokit.fem.mesh import mesh2d
from aerokit.fem.elements.plate import MITC4
from aerokit.verification import check, check_true

E, NU = 200e9, 0.3


def _D(h, nu=NU):
    return E * h ** 3 / (12 * (1 - nu ** 2))


def _plate(a, b, nx, ny, h, q=0.0, rho=0.0, N0=(0.0, 0.0, 0.0), nu=NU, support="simple"):
    X, conn, edges = mesh2d.rectangle(a, b, nx, ny, "Q4")
    m = Model(X, 3)
    for c in conn:
        m.add(MITC4(c, E, nu, h, rho=rho, q=q, prestress=N0))
    if support == "simple":                                    # "hard" simple support
        for n in mesh2d.edge_nodes(edges["left"] + edges["right"]):
            m.fix(n, [0, 2])                             # w, βy (rotation along the edge)
        for n in mesh2d.edge_nodes(edges["lower"] + edges["upper"]):
            m.fix(n, [0, 1])
    return m, X


def _navier_w(x, y, a, b, q, D, n_terms=199):
    s = 0.0
    for mm in range(1, n_terms + 1, 2):
        for nn in range(1, n_terms + 1, 2):
            s += math.sin(mm * math.pi * x / a) * math.sin(nn * math.pi * y / b) / (
                mm * nn * ((mm / a) ** 2 + (nn / b) ** 2) ** 2)
    return 16 * q / (math.pi ** 6 * D) * s


def _center(X, a, b):
    return mesh2d.find(X, lambda x, y: abs(x - a / 2) < 1e-9 and abs(y - b / 2) < 1e-9)[0]


def test_element_properties():
    X = np.array([[0.0, 0.0], [1.1, 0.1], [1.3, 0.9], [-0.1, 1.2]])
    k = MITC4([0, 1, 2, 3], E, NU, 0.01).k(X)
    w = np.linalg.eigvalsh(k)
    n0 = int(np.sum(np.abs(w) < 1e-9 * w.max()))
    check("MITC4: exactly 3 zero-energy modes (no spurious modes)", n0, 3, source="Bathe & Dvorkin 1985")
    check_true("MITC4: symmetric", np.allclose(k, k.T))
    M = MITC4([0, 1, 2, 3], E, NU, 0.01, rho=7800).m(X)
    d1, d2 = X[2] - X[0], X[3] - X[1]                    # diagonals of the quadrilateral
    area = 0.5 * abs(d1[0] * d2[1] - d1[1] * d2[0])
    check("MITC4 mass: w-direction total = ρhA", M[0::3, 0::3].sum(), 7800 * 0.01 * area, rtol=1e-12)


def test_plate_patch_test():
    X = np.array([[0, 0], [0.24, 0], [0.24, 0.12], [0, 0.12],
                  [0.04, 0.02], [0.18, 0.03], [0.16, 0.08], [0.08, 0.08]], dtype=float)
    q = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
    h, Ep, nu = 0.001, 1e6, 0.25
    m = Model(X, 3)
    for c in q:
        m.add(MITC4(c, Ep, nu, h))
    exact = lambda x, y: (1e-3 * (x * x + x * y + y * y) / 2, -1e-3 * (x + y / 2), -1e-3 * (y + x / 2))
    for n in range(4):
        for j, v in enumerate(exact(*X[n])):
            m.fix(n, j, v)
    u = m.static()["u"]
    error = max(abs(u[3 * n + j] - exact(*X[n])[j]) for n in range(4, 8) for j in range(3))
    check("plate patch test (constant curvature): interior nodes exact", error, 0.0, atol=1e-14,
            source="MacNeal & Harder 1985 plate patch, w = 10⁻³(x²+xy+y²)/2")
    Db = Ep * h ** 3 / (12 * (1 - nu ** 2))
    Mx = np.array([r["M"][0] for r in m.element_results(u)])
    Mx_exact = Db * (-1e-3 - nu * 1e-3)
    check("plate patch test: Mx = Db(κx + νκy) in every element (relative)", np.abs(Mx / Mx_exact - 1).max(), 0.0,
            atol=1e-9)    # thin plate (h/L = 1/240): shear/bending stiffness ratio ~ (L/h)² amplifies round-off


def test_navier_simply_supported_square_plate():
    a, h, q = 1.0, 0.01, 1e4
    D = _D(h)
    check("Navier series: square plate center coefficient 0.00406",
            _navier_w(0.5, 0.5, a, a, q, D) * D / (q * a ** 4), 0.00406, rtol=1e-3,
            source="Timoshenko & Woinowsky-Krieger 1959, Table 8")
    exact = _navier_w(0.5, 0.5, a, a, q, D)
    errors = []
    for n in (4, 8, 16):
        m, X = _plate(a, a, n, n, h, q=q)
        w = m.static()["u"][3 * _center(X, a, a)]
        errors.append(abs(w / exact - 1))
    check("MITC4 16×16: center deflection vs. Navier", errors[-1], 0.0, atol=3e-3,
            source="Navier series (199×199 terms), a/h = 100")
    check_true("MITC4: error decreases as the mesh is refined", errors[2] < errors[1] < errors[0],
               str([f"{e:.1e}" for e in errors]))
    # rectangular plate b = 2a
    m, X = _plate(a, 2 * a, 16, 32, h, q=q)
    w = m.static()["u"][3 * _center(X, a, 2 * a)]
    check("MITC4 rectangular b/a = 2: center deflection vs. Navier", w, _navier_w(0.5, 1.0, a, 2 * a, q, D),
            rtol=5e-3, source="Timoshenko & Woinowsky-Krieger: α = 0.01013 for b/a = 2")
    check("Navier b/a = 2 coefficient 0.01013", _navier_w(0.5, 1.0, a, 2 * a, q, D) * D / (q * a ** 4), 0.01013,
            rtol=1e-3, source="Timoshenko & Woinowsky-Krieger 1959, Table 8")


def test_no_shear_locking():
    a, q = 1.0, 1e3
    for h in (1e-3, 1e-4):
        D = _D(h)
        m, X = _plate(a, a, 8, 8, h, q=q)
        w = m.static()["u"][3 * _center(X, a, a)]
        check(f"MITC4 very thin plate a/h = {a / h:.0f}, 8×8: no locking", w, _navier_w(0.5, 0.5, a, a, q, D),
                rtol=1.5e-2, source="Bathe & Dvorkin 1985: MITC4 does not lock in the thin limit")


def test_plate_frequencies():
    a, b, h, rho = 1.0, 1.0, 0.01, 7800.0
    D = _D(h)
    m, _ = _plate(a, b, 16, 16, h, rho=rho)
    w = m.modal(3)["omega"]
    c = math.pi ** 2 * math.sqrt(D / (rho * h))
    check("SS square plate ω11 = 2π²√(D/ρh)/a²", w[0], c * (1 / a ** 2 + 1 / b ** 2), rtol=1e-2,
            source="Leissa 1969, NASA SP-160 §4.1")
    check("SS square plate ω12 = ω21 = 5π²√(D/ρh)/a²", w[1], c * (1 / a ** 2 + 4 / b ** 2), rtol=1.5e-2)
    check("SS square plate ω12 and ω21 equal (symmetry)", w[2], w[1], rtol=1e-8)


def test_plate_buckling():
    b, h = 1.0, 0.01
    D = _D(h)
    for ratio in (1.0, 1.5, 2.0):
        a = ratio * b
        k_exact = min((mm * b / a + a / (mm * b)) ** 2 for mm in range(1, 6))
        m, _ = _plate(a, b, int(16 * ratio), 16, h, N0=(-1.0, 0.0, 0.0))
        lam = m.buckling(1, preload=np.zeros(m.n_dof))["lambda_"][0]
        check(f"SS plate uniaxial compression a/b = {ratio:g}: k = {k_exact:.3f}", lam * b * b / (math.pi ** 2 * D),
                k_exact, rtol=1.5e-2, source="Timoshenko & Gere 1961 §9.2: k = (mb/a + a/mb)²")


def test_cantilever_strip_timoshenko():
    L, b, h, q = 1.0, 0.2, 0.02, 1e3
    X, conn, edges = mesh2d.rectangle(L, b, 16, 2, "Q4")
    m = Model(X, 3)
    for c in conn:
        m.add(MITC4(c, E, 0.0, h, q=q))
    for n in mesh2d.edge_nodes(edges["left"]):
        m.fix(n, [0, 1, 2])
    u = m.static()["u"]
    tip = [n for n in mesh2d.edge_nodes(edges["right"])]
    w = np.mean(u[3 * np.array(tip)])
    D = E * h ** 3 / 12
    G = E / 2
    expected = q * L ** 4 / (8 * D) + q * L ** 2 / (2 * (5 / 6) * G * h)
    check("cantilever plate strip (ν = 0): Timoshenko beam", w, expected, rtol=5e-3,
            source="derivation: at ν = 0 the plate strip equals a beam; shear κ = 5/6")
