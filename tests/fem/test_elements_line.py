"""FEM 1-D elements: truss, 2-D frame, 3-D frame — static, modal, buckling.

References are independent of the FEM: closed-form beam/bar solutions (Timoshenko & Gere 1961;
Gere & Timoshenko, Mechanics of Materials), and the roots of the characteristic equations are found
separately with scipy.optimize.brentq.
"""
import math
import numpy as np
from scipy.optimize import brentq

from aerokit.fem import Model
from aerokit.fem.elements.line import Bar, Frame2D, Frame3D
from aerokit.verification import check, check_true, expect_error

E, A, I, RHO = 70e9, 1e-3, 2e-6, 2700.0


def _eigenvalue_zero_count(k, tol=1e-9):
    w = np.linalg.eigvalsh(k)
    return int(np.sum(np.abs(w) < tol * np.abs(w).max())), w


# ---------------- Truss ----------------
def test_bar_element_properties():
    X = np.array([[0.0, 0.0], [3.0, 4.0]])
    k = Bar(0, 1, E, A).k(X)
    check_true("bar 2-D: stiffness is symmetric", np.allclose(k, k.T))
    n0, w = _eigenvalue_zero_count(k)
    check("bar 2-D: 3 zero eigenvalues (2 translations + 1 rotation)", n0, 3, source="derivation: rank 1")
    check("bar 2-D: nonzero eigenvalue 2EA/L", w.max(), 2 * E * A / 5)
    X3 = np.array([[0.0, 0, 0], [1.0, 2, 2]])
    n0, _ = _eigenvalue_zero_count(Bar(0, 1, E, A, dim=3).k(X3))
    check("bar 3-D: 5 zero eigenvalues", n0, 5, source="derivation: rank 1")
    m = Bar(0, 1, E, A, rho=RHO).m(X)
    check("bar consistent mass: x-direction total = ρAL", m[0::2, 0::2].sum(), RHO * A * 5)
    expect_error("zero-length bar raises an error", Bar(0, 1, E, A).k, np.array([[1.0, 1], [1.0, 1]]),
                 error=ValueError)


def _v_truss(angle=0.0):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    R = np.array([[c, -s], [s, c]])
    X = np.array([[-3.0, 0.0], [3.0, 0.0], [0.0, -4.0]]) @ R.T
    m = Model(X, 2)
    m.add(Bar(0, 2, E, A))
    m.add(Bar(1, 2, E, A))
    for d in (0, 1):
        m.fix(d, [0, 1])
    P = 1e4
    load = R @ np.array([0.0, -P])
    m.load(2, 0, load[0])
    m.load(2, 1, load[1])
    return m, P, R


def test_v_truss_static():
    m, P, _ = _v_truss()
    r = m.static()
    N = [s["N"] for s in m.element_results(r["u"])]
    # Nodal equilibrium: 2N cosβ = P, cosβ = 4/5 → N = 0.625 P (tension)
    check("V truss: bar force 0.625P (static equilibrium)", N[0], 0.625 * P, source="derivation: nodal equilibrium")
    check("V truss: both bars equal", N[1], N[0])
    check("V truss: vertical deflection N·L/(EA·cosβ)", -r["u"][5], 0.625 * P * 5 / (E * A * 0.8),
            source="derivation: Castigliano")
    check("V truss: sum of reactions = P", r["reaction"][[1, 3]].sum(), P)
    check("V truss: work = 2 × strain energy", P * -r["u"][5] / 2, r["energy"])
    m2, P2, R = _v_truss(angle=37.0)
    r2 = m2.static()
    check("V truss rotated 37°: same bar force", m2.element_results(r2["u"])[0]["N"], 0.625 * P2)
    check("V truss rotated 37°: same displacement magnitude",
            np.linalg.norm(r2["u"][4:6]), np.linalg.norm(r["u"][4:6]))


def test_tripod_3d():
    h, a = 4.0, 3.0
    X = [[a * math.cos(t), a * math.sin(t), 0.0] for t in np.radians([90, 210, 330])] + [[0, 0, h]]
    m = Model(X, 3)
    for i in range(3):
        m.add(Bar(i, 3, E, A, dim=3))
        m.fix(i, [0, 1, 2])
    P = 3e4
    m.load(3, 2, -P)
    r = m.static()
    N = m.element_results(r["u"])[0]["N"]
    check("tripod: each leg in compression −P/(3 cosβ)", N, -P / (3 * h / 5), source="derivation: nodal equilibrium")
    check("tripod: apex does not move horizontally", np.abs(r["u"][9:11]).max(), 0.0, atol=1e-15)


def test_bar_clamped_at_both_ends():
    L, n = 2.0, 8
    m = Model([[L * i / n, 0.0] for i in range(n + 1)], 2)
    for i in range(n):
        m.add(Bar(i, i + 1, E, A))
    for i in range(n + 1):
        m.fix(i, 1)
    m.fix(0, 0)
    m.fix(n, 0)
    P, j = 5e3, 3                                      # a = 0.75 m, b = 1.25 m
    m.load(j, 0, P)
    r = m.static()
    check("statically indeterminate bar: left reaction −P·b/L", r["reaction"][0], -P * 1.25 / L,
            source="derivation: compatibility")
    check("statically indeterminate bar: right reaction −P·a/L", r["reaction"][2 * n], -P * 0.75 / L)


def test_bar_axial_vibration_bounds():
    L, n = 1.0, 20
    m = Model([[L * i / n, 0.0] for i in range(n + 1)], 2)
    for i in range(n):
        m.add(Bar(i, i + 1, E, A, rho=RHO))
    for i in range(n + 1):
        m.fix(i, 1)
    m.fix(0, 0)
    exact = [(2 * k - 1) * math.pi / (2 * L) * math.sqrt(E / RHO) for k in (1, 2, 3)]
    consistent = m.modal(3)["omega"]
    lumped = m.modal(3, lumped=True)["omega"]
    for k in range(3):
        check_true(f"clamped-free bar mode {k + 1}: consistent mass upper bound, lumped mass lower bound",
              lumped[k] < exact[k] < consistent[k], f"{lumped[k]:.6g} < {exact[k]:.6g} < {consistent[k]:.6g}",
              source="Cook et al. 2002 §11.4: consistent-mass frequency converges from above")
    check("clamped-free bar mode 1: (π/2L)√(E/ρ), 20 elements", consistent[0], exact[0], rtol=1e-3,
            source="Rao, Mechanical Vibrations: ωn = (2n−1)πc/(2L)")


def test_truss_buckling_rigid_bar_spring():
    # Rigid post pinned at the base + horizontal spring k at the top: P_cr = k·L (Timoshenko & Gere 1961 §2.1)
    L, k = 2.0, 5e5
    X = np.array([[0.0, 0.0], [0.0, L], [1.0, L]])
    m = Model(X, 2)
    m.add(Bar(0, 1, E * 1e4, A))                   # practically rigid post
    m.add(Bar(1, 2, k * 1.0 / A, A))                # EA/Ls = k
    m.fix(0, [0, 1])
    m.fix(2, [0, 1])
    m.load(1, 1, -1.0)
    lam = m.buckling(1)["lambda_"][0]
    check("truss buckling: rigid post + spring P_cr = kL", lam, k * L, rtol=1e-4,
            source="Timoshenko & Gere 1961 §2.1 (rigid bar-spring model)")


# ---------------- 2-D frame ----------------
def _cantilever(n, L=2.0, angle=0.0, q=0.0):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    m = Model([[c * L * i / n, s * L * i / n] for i in range(n + 1)], 3)
    for i in range(n):
        m.add(Frame2D(i, i + 1, E, A, I, rho=RHO, q=q))
    m.fix(0, [0, 1, 2])
    return m, L


def test_frame2d_element():
    k = Frame2D(0, 1, E, A, I).k(np.array([[0.0, 0], [1.2, 0.5]]))
    check_true("frame 2-D: symmetric", np.allclose(k, k.T))
    n0, _ = _eigenvalue_zero_count(k)
    check("frame 2-D: 3 rigid-body modes", n0, 3, source="derivation")


def test_cantilever_tip_load():
    for angle in (0.0, 30.0):
        m, L = _cantilever(1, angle=angle)
        P = 1e3
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        m.load(1, 0, -s * P)
        m.load(1, 1, c * P)  # load perpendicular to the axis
        u = m.static()["u"]
        perpendicular = -s * u[3] + c * u[4]
        check(f"cantilever tip load ({angle:g}°): δ = PL³/3EI, exact with one element", perpendicular,
                P * L ** 3 / (3 * E * I), rtol=1e-10, source="Gere & Timoshenko, Mechanics of Materials, Table G-1")
        check(f"cantilever tip load ({angle:g}°): θ = PL²/2EI", u[5], P * L ** 2 / (2 * E * I), rtol=1e-10)


def test_cantilever_distributed_load():
    q = -2e3
    m, L = _cantilever(4, q=q)
    r = m.static()
    check("cantilever distributed load: tip δ = qL⁴/8EI (exact at nodes)", r["u"][-2], q * L ** 4 / (8 * E * I),
            rtol=1e-10, source="Gere & Timoshenko, Table G-1")
    check("cantilever distributed load: root reaction −qL", r["reaction"][1], -q * L)
    check("cantilever distributed load: root moment −qL²/2", r["reaction"][2], -q * L ** 2 / 2)
    inner = m.element_results(r["u"])[0]
    check("cantilever distributed load: internal moment at root qL²/2 (sagging positive)", inner["M1"],
            q * L ** 2 / 2, rtol=1e-10)


def _beam(n, L, q, left, right):
    m = Model([[L * i / n, 0.0] for i in range(n + 1)], 3)
    for i in range(n):
        m.add(Frame2D(i, i + 1, E, A, I, q=q))
    m.fix(0, left)
    m.fix(n, right)
    return m


def test_indeterminate_beams():
    L, q = 3.0, -1e3
    m = _beam(2, L, q, [0, 1, 2], [0, 1, 2])
    r = m.static()
    check("clamped-clamped, distributed load: midspan δ = qL⁴/384EI", r["u"][4], q * L ** 4 / (384 * E * I),
            rtol=1e-10, source="Gere & Timoshenko, Table G-2")
    check("clamped-clamped: end moment qL²/12", r["reaction"][2], -q * L ** 2 / 12, rtol=1e-10)
    m = _beam(6, L, q, [0, 1, 2], [1])
    r = m.static()
    check("clamped-pinned (propped), distributed load: pin reaction −3qL/8", r["reaction"][6 * 3 + 1],
            -3 * q * L / 8, rtol=1e-10, source="Gere & Timoshenko, Table G-2")
    m = _beam(8, L, q, [0, 1], [1])
    r = m.static()
    check("simply supported beam, distributed load: midspan δ = 5qL⁴/384EI", r["u"][4 * 3 + 1],
            5 * q * L ** 4 / (384 * E * I), rtol=1e-10, source="Gere & Timoshenko, Table G-2")


def test_l_frame_2d_and_3d():
    H, L, P = 3.0, 2.0, 1e3
    m = Model([[0.0, 0.0], [0.0, H], [L, H]], 3)
    m.add(Frame2D(0, 1, E, A, I))
    m.add(Frame2D(1, 2, E, A, I))
    m.fix(0, [0, 1, 2])
    m.load(2, 1, -P)
    u = m.static()["u"]
    expected = P * L ** 3 / (3 * E * I) + P * L ** 2 * H / (E * I) + P * H / (E * A)
    check("L frame: tip deflection PL³/3EI + PL²H/EI + PH/EA", -u[7], expected, rtol=1e-10,
            source="derivation: unit-load method (bending + axial shortening of the column)")
    G, J = E / 2.6, 3e-6
    m3 = Model([[0.0, 0, 0], [0.0, H, 0], [L, H, 0]], 6)
    m3.add(Frame3D(0, 1, E, G, A, I, I, J, ref=(1, 0, 0)))
    m3.add(Frame3D(1, 2, E, G, A, I, I, J, ref=(0, 1, 0)))
    m3.fix(0, range(6))
    m3.load(2, 1, -P)
    u3 = m3.static()["u"]
    check("L frame: Frame3D in-plane result equals Frame2D", -u3[13], expected, rtol=1e-10)
    check("L frame 3-D: no out-of-plane displacement", np.abs(u3[2::6]).max(), 0.0, atol=1e-14)


def _find_root(betaL_interval, f):
    return brentq(f, *betaL_interval, xtol=1e-14)


def test_cantilever_bending_frequencies():
    m, L = _cantilever(20)
    w = m.modal(3)["omega"]
    # Roots of cos βL · cosh βL = −1 (found independently)
    root = [_find_root(a, lambda x: math.cos(x) * math.cosh(x) + 1) for a in ((1, 3), (4, 6), (7, 9))]
    check("cantilever: β1L = 1.8751", root[0], 1.8751, rtol=1e-4, source="Rao, Mechanical Vibrations, Table 8.4")
    c = math.sqrt(E * I / (RHO * A * L ** 4))
    for k in range(3):
        exact = root[k] ** 2 * c
        check(f"cantilever bending mode {k + 1} (20 elements)", w[k], exact, rtol=2e-4,
                source="Euler-Bernoulli: ω = (βL)²√(EI/ρAL⁴)")
        check_true(f"cantilever mode {k + 1}: consistent mass upper bound", w[k] >= exact * (1 - 1e-12))


def test_simply_supported_beam_frequency():
    L = 3.0
    m = _beam(20, L, 0.0, [0, 1], [1])
    for e in m.elements:
        e.rho = RHO
    w = m.modal(2)["omega"]
    for k in (1, 2):
        exact = (k * math.pi / L) ** 2 * math.sqrt(E * I / (RHO * A))
        check(f"simply supported beam bending mode {k}", w[k - 1], exact, rtol=1e-4,
                source="Rao: ωn = (nπ/L)²√(EI/ρA)")


def _column(n, L, left, right, angle=0.0):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    m = Model([[c * L * i / n, s * L * i / n] for i in range(n + 1)], 3)
    for i in range(n):
        m.add(Frame2D(i, i + 1, E, A, I))
    m.fix(0, left)
    m.fix(n, right)
    m.load(n, 0, -c)
    m.load(n, 1, -s)  # unit compression
    return m


def test_column_buckling():
    L = 2.0
    pe = math.pi ** 2 * E * I / L ** 2
    x_fp = brentq(lambda x: math.tan(x) - x, 4.0, 4.6, xtol=1e-14)   # clamped-pinned: tan kL = kL
    cases = [("pinned-pinned", [0, 1], [1], 1.0),
                ("clamped-free", [0, 1, 2], [], 0.25),
                ("clamped-clamped (sliding end)", [0, 1, 2], [1, 2], 4.0),
                ("clamped-pinned", [0, 1, 2], [1], x_fp ** 2 / math.pi ** 2)]
    for name, left, right, factor in cases:
        errors = []
        for n in (4, 8, 16, 32):
            lam = _column(n, L, left, right).buckling(1)["lambda_"][0]
            errors.append(lam / (factor * pe) - 1)
        check(f"Euler buckling, {name}: P_cr/P_E = {factor:.4f} (32 elements)", errors[-1], 0.0, atol=1e-5,
                source="Timoshenko & Gere 1961 §2.3–2.4; root of tan x = x found independently")
        check_true(f"Euler buckling, {name}: error positive and monotonically decreasing",
              all(h > -1e-12 for h in errors) and all(errors[i + 1] <= errors[i] + 1e-12 for i in range(3)),
              str([f"{h:.2e}" for h in errors]), source="Cook et al. 2002 §18.5: cubic mesh converges from above")
        p = math.log2(errors[1] / errors[2])
        check_true(f"Euler buckling, {name}: convergence order ≈ 4 (h⁴)", 3.7 < p < 4.3, f"p = {p:.2f}",
              source="derivation: cubic Hermite eigenvalue error O(h⁴)")
    # A pinned column rotated by 45° is not tested here: its tip node cannot be supported perpendicular
    # to the axis (no skewed supports), so instead of clamping both ends in x-y and applying the axial
    # load at an intermediate node, rotation invariance is checked in statics (cantilever test).
    m2 = _column(16, L, [0, 1], [1])
    lam0 = m2.buckling(1)["lambda_"][0]
    check("buckling mode 2 (pinned) = 4·P_E", m2.buckling(2)["lambda_"][1], 4 * pe, rtol=1e-3)
    check("buckling: 16 elements pinned ≈ P_E", lam0, pe, rtol=2e-5)


# ---------------- 3-D frame ----------------
def test_frame3d_element_and_cantilever():
    G, Iy, Iz, J, L = E / 2.6, 3e-6, 1.5e-6, 2e-6, 1.7
    k = Frame3D(0, 1, E, G, A, Iy, Iz, J).k(np.array([[0.0, 0, 0], [0.3, 1.0, 0.8]]))
    check_true("frame 3-D: symmetric", np.allclose(k, k.T))
    n0, _ = _eigenvalue_zero_count(k)
    check("frame 3-D: 6 rigid-body modes", n0, 6, source="derivation")
    for direction, name, expected in ((1, "y load → PL³/3EIz", 1 / (3 * E * Iz)),
                                      (2, "z load → PL³/3EIy", 1 / (3 * E * Iy))):
        m = Model([[0.0, 0, 0], [L, 0, 0]], 6)
        m.add(Frame3D(0, 1, E, G, A, Iy, Iz, J, ref=(0, 1, 0)))
        m.fix(0, range(6))
        m.load(1, direction, 1e3)
        check(f"3-D cantilever {name}", m.static()["u"][6 + direction], 1e3 * L ** 3 * expected, rtol=1e-10,
                source="Gere & Timoshenko, Table G-1")
    m = Model([[0.0, 0, 0], [L, 0, 0]], 6)
    m.add(Frame3D(0, 1, E, G, A, Iy, Iz, J, ref=(0, 1, 0)))
    m.fix(0, range(6))
    m.load(1, 3, 500.0)
    m.load(1, 0, 2e4)
    u = m.static()["u"]
    check("3-D cantilever torsion θ = TL/GJ", u[9], 500 * L / (G * J), rtol=1e-10)
    check("3-D cantilever axial δ = PL/EA", u[6], 2e4 * L / (E * A), rtol=1e-10)
    d = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)
    m = Model([[0.0, 0, 0], list(L * d)], 6)
    m.add(Frame3D(0, 1, E, G, A, Iy, Iy, J, ref=(0, 0, 1)))
    m.fix(0, range(6))
    perpendicular = np.cross(d, [0, 0, 1.0])
    perpendicular /= np.linalg.norm(perpendicular)
    for j in range(3):
        m.load(1, j, 1e3 * perpendicular[j])
    u = m.static()["u"]
    check("3-D skewed cantilever (Iy = Iz): δ = PL³/3EI", np.linalg.norm(u[6:9]), 1e3 * L ** 3 / (3 * E * Iy),
            rtol=1e-10)


def test_frame3d_torsion_frequency():
    G, J, L, n = E / 2.6, 2e-6, 1.0, 20
    Iy = Iz = J / 2                                   # circular section: Ip = J
    m = Model([[L * i / n, 0, 0] for i in range(n + 1)], 6)
    for i in range(n):
        m.add(Frame3D(i, i + 1, E, G, A, Iy, Iz, J, rho=RHO, ref=(0, 1, 0)))
    m.fix(0, range(6))
    for i in range(1, n + 1):
        m.fix(i, [0, 1, 2, 4, 5])                 # only torsion is free
    w = m.modal(1)["omega"][0]
    exact = math.pi / (2 * L) * math.sqrt(G * J / (RHO * J))
    check("clamped-free shaft torsional frequency (π/2L)√(GJ/ρIp)", w, exact, rtol=1e-3,
            source="Rao, Mechanical Vibrations: torsional vibration")


def test_model_errors():
    m = Model([[0.0, 0], [1.0, 0]], 3)
    expect_error("ndof mismatch raises an error", m.add, Bar(0, 1, E, A), error=ValueError)
    m.add(Frame2D(0, 1, E, A, I))
    m.load(1, 1, 1.0)
    expect_error("model without boundary conditions raises a singularity error", m.static, error=ValueError)
    expect_error("nonexistent node raises an error", m.add, Frame2D(0, 5, E, A, I), error=ValueError)
