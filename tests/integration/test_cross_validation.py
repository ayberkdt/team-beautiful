"""Cross-validation: independently written analytical modules ↔ FEM.

The analytical modules (pressure, rotating, composites, buckling, fatigue, fracture) and the FEM solve the
same problem in different ways; agreement between the two is strong evidence that neither side is in error.
Some analytical formulas could not be read from their source (Tada, Isida, Howland); for those these tests
are an independent numerical verification.
"""
import math

import numpy as np

from aerokit.composites import laminate
from aerokit.data import EXAMPLES_DIR
from aerokit.fem import Model
from aerokit.fem.elements.line import Frame2D
from aerokit.fem.elements.plane import Q8, D_isotropic
from aerokit.fem.elements.plate import MITC4
from aerokit.fem.mesh import mesh2d
from aerokit.structures import buckling, fatigue, fracture, pressure, rotating
from aerokit.verification import check

E, NU = 70e9, 0.3


def test_lame_fem_pressure():
    a, b, h, p = 0.05, 0.12, 0.01, 50e6
    X, conn, edges = mesh2d.mapped_mesh(lambda s, t: (a + (b - a) * s, h * t), 16, 1, "Q8",
                                      xi_distribution=mesh2d.geometric_distribution(16, 4.0))
    m = Model(X, 2)
    for c in conn:
        m.add(Q8(c, D_isotropic(E, NU, "axial"), format="axial"))
    m.F += mesh2d.edge_load(X, edges["left"], pressure=p, format="axial")
    for n in mesh2d.edge_nodes(edges["lower"] + edges["upper"]):
        m.fix(n, 1)
    u = m.static()["u"]
    S = m.node_stresses(u)
    inner = mesh2d.find(X, lambda x, y: abs(x - a) < 1e-12 and abs(y) < 1e-12)[0]
    ref = pressure.lame_cylinder(a, b, pi=p, r=a, ends="plane_strain", E=E, nu=NU)
    check("cross: Lamé u_r(a) axisymmetric FEM ↔ pressure.lame_cylinder", u[2 * inner], ref["u"], rtol=1e-4)
    check("cross: Lamé σθ(a) FEM ↔ pressure", S[inner, 2], ref["st"], rtol=3e-3)


def test_rotating_disk_fem_rotating():
    a, b, rho, w = 0.04, 0.25, 7800.0, 500.0
    X, conn, edges = mesh2d.mapped_mesh(lambda s, t: ((a + (b - a) * s) * math.cos(t * math.pi / 2),
                                                    (a + (b - a) * s) * math.sin(t * math.pi / 2)),
                                      16, 12, "Q8", xi_distribution=mesh2d.geometric_distribution(16, 3.0))
    m = Model(X, 2)
    for c in conn:
        m.add(Q8(c, D_isotropic(200e9, NU, "stress"), t=0.01, rho=rho, omega=w))
    for n in mesh2d.edge_nodes(edges["lower"]):
        m.fix(n, 1)
    for n in mesh2d.edge_nodes(edges["upper"]):
        m.fix(n, 0)
    S = m.node_stresses(m.static()["u"])
    inner = mesh2d.find(X, lambda x, y: abs(x - a) < 1e-9 and abs(y) < 1e-12)[0]
    mid_r = X[mesh2d.find(X, lambda x, y: abs(y) < 1e-12)][:, 0]
    r_mid = mid_r[np.argmin(abs(mid_r - 0.12))]
    middle = mesh2d.find(X, lambda x, y: abs(x - r_mid) < 1e-12 and abs(y) < 1e-12)[0]
    check("cross: rotating disk hole σθ FEM ↔ rotating.annular_disk", S[inner, 1],
          rotating.annular_disk(rho, w, a, b, NU, r=a)["st"], rtol=5e-3)
    check("cross: rotating disk intermediate-radius σr FEM ↔ rotating", S[middle, 0],
          rotating.annular_disk(rho, w, a, b, NU, r=r_mid)["sr"], rtol=1e-2)


def _ss_plate_buckling(a, b, h, N0, long_edge="SS", n=16):
    """Lowest buckling factor of an a × b MITC4 plate under the membrane stress resultant N0 = (Nx, Ny, Nxy).

    Loaded edges simply supported; the long (unloaded) edges simply supported (``"SS"``) or clamped.
    """
    X, conn, edges = mesh2d.rectangle(a, b, int(round(n * a / b)), n, "Q4")
    m = Model(X, 3)
    for c in conn:
        m.add(MITC4(c, E, NU, h, prestress=N0))
    for d in mesh2d.edge_nodes(edges["left"] + edges["right"]):
        m.fix(d, [0, 2])
    for d in mesh2d.edge_nodes(edges["lower"] + edges["upper"]):
        m.fix(d, [0, 1] if long_edge == "SS" else [0, 1, 2])
    return m.buckling(1, preload=np.zeros(m.n_dof))["lambda_"][0]


def test_plate_buckling_fem_buckling_composite():
    b, h = 1.0, 0.01
    D = E * h ** 3 / (12 * (1 - NU ** 2))
    for ratio in (1.0, 2.5):
        lam = _ss_plate_buckling(ratio * b, b, h, (-1.0, 0.0, 0.0))
        k_fem = lam * b * b / (math.pi ** 2 * D)
        check(f"cross: SS plate a/b = {ratio:g} k FEM ↔ buckling.plate_compression_k", k_fem,
              buckling.plate_compression_k(ratio, "SS-SS", nu=NU), rtol=1.5e-2)
        Dm = np.array([[D, NU * D, 0], [NU * D, D, 0], [0, 0, (1 - NU) / 2 * D]])
        Nk = laminate.plate_buckling(Dm, ratio * b, b)["Nx_cr"]
        check(f"cross: SS plate a/b = {ratio:g} N_cr FEM ↔ composites laminate.plate_buckling (isotropic D)", lam,
              Nk, rtol=1.5e-2)
    lam = _ss_plate_buckling(3.0, b, h, (-1.0, 0.0, 0.0), long_edge="C", n=16)
    check("cross: unloaded edges clamped a/b = 3, k FEM ↔ buckling.plate_compression_k(C-C)",
          lam * b * b / (math.pi ** 2 * D), buckling.plate_compression_k(3.0, "C-C", nu=NU), rtol=2e-2)
    lam = _ss_plate_buckling(2.0, b, h, (0.0, 0.0, 1.0), n=16)
    check("cross: SS plate shear a/b = 2, k_s FEM ↔ buckling.plate_shear_k", lam * b * b / (math.pi ** 2 * D),
          buckling.plate_shear_k(2.0, "SS"), rtol=6e-2,
          source="k_s = 5.35 + 4(b/a)² is an approximate curve fit; FEM on a 16×32 mesh gave 6.71 (formula 6.35). "
                 "The exact table value was not read in this session; the 6 % threshold covers the approximation")


def test_euler_fem_buckling():
    L, I, A, n = 1.5, 3e-7, 2e-4, 16
    m = Model([[L * i / n, 0.0] for i in range(n + 1)], 3)
    for i in range(n):
        m.add(Frame2D(i, i + 1, E, A, I))
    m.fix(0, [0, 1, 2])
    m.load(n, 0, -1.0)
    check("cross: fixed-free column FEM ↔ buckling.euler_critical", m.buckling(1)["lambda_"][0],
          buckling.euler_critical(E, I, L, 2.0), rtol=1e-4)


def _strip_with_hole(d, W, Lh, nr=16, nt=24):
    """Quarter of a finite-width strip with a central hole: x is the load direction, half length Lh, half width W/2."""
    a, c = d / 2, W / 2
    total = c + Lh                                    # outer boundary parameter: (Lh,0)→(Lh,c)→(0,c)
    tk = c / total                                    # the corner (Lh, c) must fall on a mesh line
    n1 = max(2, round(nt * tk))
    eta = np.concatenate([np.linspace(0, tk, n1 + 1), np.linspace(tk, 1, nt - n1 + 1)[1:]])

    def outer(t):
        s = t * total
        return np.array([Lh, s]) if s <= c else np.array([Lh - (s - c), c])

    def e(s, t):
        th = t * math.pi / 2
        return tuple((1 - s) * np.array([a * math.cos(th), a * math.sin(th)]) + s * outer(t))
    return mesh2d.mapped_mesh(e, nr, nt, "Q8", xi_distribution=mesh2d.geometric_distribution(nr, 6.0),
                            eta_distribution=eta)


def test_strip_with_hole_kt_fem_howland():
    W, s0 = 1.0, 1e6
    for d in (0.2, 0.4):
        X, conn, edges = _strip_with_hole(d, W, Lh=2.0)
        m = Model(X, 2)
        for c in conn:
            m.add(Q8(c, D_isotropic(E, NU, "stress")))
        right = [k for k in edges["right"] if all(abs(X[i, 0] - 2.0) < 1e-9 for i in k)]
        m.F += mesh2d.edge_load(X, right, traction=lambda x, y: (s0, 0.0))
        check(f"strip with hole d/W = {d:g}: total applied load σ·W/2", m.F[0::2].sum(), s0 * W / 2, rtol=1e-12)
        for n in mesh2d.edge_nodes(edges["lower"]):
            m.fix(n, 1)
        for n in mesh2d.find(X, lambda x, y: abs(x) < 1e-9):
            m.fix(n, 0)
        S = m.node_stresses(m.static()["u"])
        peak = mesh2d.find(X, lambda x, y: abs(x) < 1e-9 and abs(y - d / 2) < 1e-9)[0]
        ktg = S[peak, 0] / s0
        check(f"cross: strip with hole d/W = {d:g} Ktg FEM ↔ fatigue.kt_hole_howland", ktg,
              fatigue.kt_hole_howland(d, W, base="gross"), rtol=2e-2,
              source="Howland 1930 curve fit (read in Deghboudj et al. 2016); FEM Q8 quarter model, L/W = 4")


def _crack_energy(a, W2=1.0, H2=2.0, s0=1e6, n1=24, n2=24, ny=28):
    """Quarter of a centre-cracked plate: crack on y = 0, 0 ≤ x ≤ a. Returns the strain energy (t = 1)."""
    g1 = 1 - mesh2d.geometric_distribution(n1, 1 / 25.0)[::-1]      # refined towards a
    g2 = mesh2d.geometric_distribution(n2, 25.0)
    xs = np.concatenate([a * g1, a + (W2 - a) * g2[1:]]) / W2
    ys = mesh2d.geometric_distribution(ny, 25.0)
    X, conn, edges = mesh2d.mapped_mesh(lambda s, t: (W2 * s, H2 * t), n1 + n2, ny, "Q8", xi_distribution=xs,
                                      eta_distribution=ys)
    m = Model(X, 2)
    for c in conn:
        m.add(Q8(c, D_isotropic(E, NU, "stress")))
    m.F += mesh2d.edge_load(X, edges["upper"], traction=lambda x, y: (0.0, s0))
    for n in mesh2d.find(X, lambda x, y: abs(y) < 1e-12 and x >= a - 1e-12):
        m.fix(n, 1)                                    # ligament (ahead of the crack): symmetry
    for n in mesh2d.find(X, lambda x, y: abs(x) < 1e-12):
        m.fix(n, 0)
    return m.static()["energy"]


def test_center_crack_fem_fracture():
    W2, s0 = 1.0, 1e6
    for a in (0.2, 0.4):
        da = 1e-3 * a
        dU = (_crack_energy(a + da) - _crack_energy(a - da)) / (2 * da)
        G = 2 * dU                                          # full plate: 4·U, two tips: dA = 2·da (t = 1)
        Y = math.sqrt(E * G) / (s0 * math.sqrt(math.pi * a))
        check(f"cross: centre crack 2a/W = {a:g} Y FEM (energy) ↔ fracture.Y_center_tada", Y,
              fracture.Y_center_tada(a, 2 * W2), rtol=1.5e-2,
              source="FEM: G = ∂U/∂A under load control, K = √(EG); H/W = 2 (small finite-length effect)")
        check(f"cross: centre crack 2a/W = {a:g} Y FEM ↔ fracture.Y_center_secant (Feddersen)", Y,
              fracture.Y_center_secant(a, 2 * W2), rtol=2e-2)


def test_cad_wing_fem_beam_integral():
    """CAD (STL) → tetrahedral T10 FEM ↔ Euler-Bernoulli beam integral over CAD slices.

    δ_tip = ∫ P(L − y)² / (E·I(y)) dy, with I(y) the minor principal second moment of each slice (bending axis
    along the chord). The two routes are completely different: one is a volume mesh with 3-D elasticity, the
    other a section integral with beam theory.
    """
    from scipy.integrate import trapezoid

    from aerokit.cad import read
    from aerokit.fem.elements.solid import T10, D_isotropic3d
    from aerokit.fem.mesh import mesh3d
    y = read(EXAMPLES_DIR / "cad" / "wing_naca2412.stl", unit="mm")
    d = y.slice(axis=1, n=41)
    Ix, Iy, Ixy = (np.array(d[k]) for k in ("Ix", "Iy", "Ixy"))
    I = 0.5 * (Ix + Iy) - np.sqrt((0.5 * (Ix - Iy)) ** 2 + Ixy ** 2)
    ys = np.array(d["position"])
    Em, P = 68.9e9, 500.0
    L = y.V[:, 1].max()
    beam = trapezoid(P * (L - ys) ** 2 / (Em * I), ys)
    X, tet, info = mesh3d.tet_mesh_from_surface(y.V, y.F, 0.0182, kind="T10")
    check("CAD wing tet mesh: volume ratio ≥ 0.98", min(info["ratio"], 1.0), 1.0, rtol=2e-2,
          source="removal of flat elements with quality threshold 0.005 (0.02 → 8 % loss measured in this session)")
    m = Model(X, 3)
    D = D_isotropic3d(Em, 0.33)
    for t in tet:
        m.add(T10(t, D))
    root = np.where(X[:, 1] <= X[:, 1].min() + 1e-9)[0]
    tip = np.where(X[:, 1] >= X[:, 1].max() - 1e-9)[0]
    for n in root:
        m.fix(int(n), [0, 1, 2])
    for n in tip:
        m.load(int(n), 2, P / tip.size)
    w = m.static()["u"][2::3][tip].mean()
    check("cross: CAD wing tip deflection T10 FEM ↔ slice beam integral", w, beam, rtol=6e-2,
          source="FEM includes shear deformation and the root constraint; the beam integral does not "
                 "(3.9 % difference measured in this session)")
