"""3-D solid elements (T4, T10, H8), surface loads and tetrahedral meshing from a surface.

References: constant-strain patch test (after the idea of the MacNeal & Harder 1985 solid patch; in this
test the interior nodes are randomly distorted), uniaxial tension and hydrostatic pressure (exact),
Timoshenko beam, Euler-Bernoulli cantilever frequency (βL = 1.8751).
"""
import math
import numpy as np

from aerokit.fem import Model
from aerokit.fem.mesh import mesh3d
from aerokit.fem.elements.solid import T4, T10, H8, D_isotropic3d
from aerokit.verification import check, check_true, expect_error

E, NU, RHO = 70e9, 0.3, 2700.0
CLASS = {"T4": T4, "T10": T10, "H8": H8}


def _model(X, el, kind, rho=0.0):
    m = Model(X, 3)
    D = D_isotropic3d(E, NU)
    for e in el:
        m.add(CLASS[kind](e, D, rho=rho))
    return m


def test_element_properties():
    D = D_isotropic3d(E, NU)
    Xt = np.array([[0.0, 0, 0], [1.1, 0.1, 0], [0.2, 0.9, 0.1], [0.1, 0.2, 1.2]])
    X10, t10 = mesh3d.t4_to_t10(Xt, [[0, 1, 2, 3]])
    Xh = mesh3d.H8_CORNER_EXAMPLE if hasattr(mesh3d, "H8_CORNER_EXAMPLE") else None
    Xh = np.array([[0, 0, 0], [1, 0, 0.05], [1.1, 1, 0], [0, 0.9, 0], [0, 0, 1], [1, 0.1, 1], [1, 1, 1.1],
                   [-0.1, 1, 1]], float)
    for name, e, X in (("T4", T4([0, 1, 2, 3], D), Xt), ("T10", T10(t10[0], D), X10),
                       ("H8", H8(list(range(8)), D), Xh)):
        k = e.k(X)
        w = np.linalg.eigvalsh(k)
        n0 = int(np.sum(np.abs(w) < 1e-9 * w.max()))
        check(f"{name}: 6 rigid-body modes", n0, 6, source="derivation: 3 translations + 3 rotations")
        check_true(f"{name}: symmetric, positive semi-definite", np.allclose(k, k.T) and w.min() > -1e-9 * w.max())
    check("T4 volume = |det|/6", T4([0, 1, 2, 3], D).volume(Xt), mesh3d.tet_volume(Xt, [0, 1, 2, 3]), rtol=1e-12)
    expect_error("inverted T4 raises an error", T4([0, 2, 1, 3], D).k, Xt, error=ValueError)


def test_mass_and_volume():
    for kind in ("T4", "T10", "H8"):
        X, el = mesh3d.box(2.0, 1.0, 0.5, 2, 2, 1, kind)
        m = _model(X, el, kind, rho=RHO)
        M = m.M().toarray()
        check(f"{kind} box: x-direction total mass = ρV", M[0::3, 0::3].sum(), RHO * 1.0, rtol=1e-12)
        if kind != "H8":
            Ml = m.M(lumped=True).toarray()
            check(f"{kind} lumped mass total is conserved", np.trace(Ml) / 3, RHO * 1.0, rtol=1e-12)
            check_true(f"{kind} lumped mass diagonal is positive", np.all(np.diag(Ml) > 0))


def _patch(kind):
    rng = np.random.default_rng(7)
    X, el = mesh3d.box(1.0, 1.0, 1.0, 2, 2, 2, "H8" if kind == "H8" else "T4")
    inner = [i for i, p in enumerate(X) if np.all((p > 1e-9) & (p < 1 - 1e-9))]
    X[inner] += rng.uniform(-0.12, 0.12, (len(inner), 3))
    if kind == "T10":
        X, el = mesh3d.t4_to_t10(X, el)
        inner = [i for i, p in enumerate(X) if np.all((p > 1e-9) & (p < 1 - 1e-9))]
    return X, el, inner


def test_patch_test_3d():
    exact = lambda x, y, z: 1e-3 * np.array([x + 0.5 * y + 0.2 * z, 0.3 * x + y - 0.4 * z, -0.1 * x + 0.2 * y + z])
    for kind in ("T4", "T10", "H8"):
        X, el, inner = _patch(kind)
        m = _model(X, el, kind)
        inner_set = set(inner)
        for n in range(X.shape[0]):
            if n not in inner_set:
                for j, v in enumerate(exact(*X[n])):
                    m.fix(n, j, v)
        u = m.static()["u"]
        error = max(np.abs(u[3 * n:3 * n + 3] - exact(*X[n])).max() for n in inner)
        check(f"3-D patch test {kind}: distorted interior nodes exact", error, 0.0, atol=1e-14,
                source="Irons patch test; constant strain field")
        eps = np.array([p["eps"] for r in m.element_results(u) for p in r["points"]])
        check(f"3-D patch test {kind}: γxy = 0.8e-3 at every Gauss point", np.abs(eps[:, 5] - 0.8e-3).max(), 0.0,
                atol=1e-14)


def _bar_tension(kind):
    L, b = 2.0, 0.5
    X, el = mesh3d.box(L, b, b, 4, 2, 2, kind)
    m = _model(X, el, kind)
    for n in mesh3d.find3(X, lambda x, y, z: abs(x) < 1e-12):
        m.fix(n, 0)
    m.fix(mesh3d.find3(X, lambda x, y, z: abs(x) + abs(y) + abs(z) < 1e-12)[0], [1, 2])
    m.fix(mesh3d.find3(X, lambda x, y, z: abs(x) + abs(y - b) + abs(z) < 1e-12)[0], [2])
    return m, X, L, b


def test_uniaxial_tension_and_surface_load():
    s = 50e6
    for kind in ("T4", "T10", "H8"):
        m, X, L, b = _bar_tension(kind)
        if kind == "H8":
            face = []
            for e in m.elements:
                f = [d for d in e.nodes if abs(X[d, 0] - L) < 1e-12]
                if len(f) == 4:
                    face.append([e.nodes[i] for i in (1, 2, 6, 5)])       # x = +1 face, outward normal +x
        else:
            face = [f for f in mesh3d.boundary_faces([e.nodes[:4] for e in m.elements])
                   if all(abs(X[d, 0] - L) < 1e-12 for d in f)]
            if kind == "T10":
                face = [_t6(f, m) for f in face]
        F = mesh3d.surface_load(X, face, traction=lambda x, y, z: (s, 0.0, 0.0))
        check(f"{kind}: surface load total = σ·A", F[0::3].sum(), s * b * b, rtol=1e-12)
        m.F += F
        u = m.static()["u"]
        tip = mesh3d.find3(X, lambda x, y, z: abs(x - L) < 1e-12)
        check(f"{kind} uniaxial tension: end elongation σL/E", np.mean(u[3 * np.array(tip)]), s * L / E, rtol=1e-10,
                source="derivation: uniform stress field is exact in all elements")
        corner = mesh3d.find3(X, lambda x, y, z: abs(x - L) + abs(y - b) + abs(z) < 1e-12)[0]
        check(f"{kind} uniaxial tension: lateral contraction −νσb/E", u[3 * corner + 1],
                -NU * s * b / E, rtol=1e-9)


def _t6(f, m):
    """Adds the edge mid-side nodes to a T10 boundary face (corner triple)."""
    for e in m.elements:
        if set(f) <= set(e.nodes[:4]):
            middle = {}
            for k, (i, j) in enumerate(mesh3d.T10_EDGE):
                middle[frozenset((e.nodes[i], e.nodes[j]))] = e.nodes[4 + k]
            a, b, c = f
            return [a, b, c, middle[frozenset((a, b))], middle[frozenset((b, c))], middle[frozenset((c, a))]]
    raise AssertionError("face not found")


def test_hydrostatic_pressure():
    p = 10e6
    X, el = mesh3d.box(1.0, 1.0, 1.0, 2, 2, 2, "T4")
    m = _model(X, el, "T4")
    face = mesh3d.boundary_faces(el)
    m.F += mesh3d.surface_load(X, face, pressure=p)
    check("pressure resultant on a closed surface is zero", np.abs(m.F.reshape(-1, 3).sum(axis=0)).max(), 0.0,
            atol=1e-6)
    o = mesh3d.find3(X, lambda x, y, z: abs(x) + abs(y) + abs(z) < 1e-12)[0]
    m.fix(o, [0, 1, 2])
    m.fix(mesh3d.find3(X, lambda x, y, z: abs(x - 1) + abs(y) + abs(z) < 1e-12)[0], [1, 2])
    m.fix(mesh3d.find3(X, lambda x, y, z: abs(x) + abs(y - 1) + abs(z) < 1e-12)[0], [2])
    r = m.static()
    s = np.array([q["sigma"] for e in m.element_results(r["u"]) for q in e["points"]])
    check("hydrostatic pressure: σx = σy = σz = −p in every element", np.abs(s[:, :3] + p).max(), 0.0, atol=1e-3)
    K = E / (3 * (1 - 2 * NU))
    far = mesh3d.find3(X, lambda x, y, z: abs(x - 1) + abs(y - 1) + abs(z - 1) < 1e-12)[0]
    vol = 1 + (r["u"][3 * far:][:3]).sum()
    check("hydrostatic pressure: volumetric strain −p/K", (vol - 1), -p / K, rtol=1e-9,
            source="derivation: K = E/3(1−2ν)")


def test_cantilever_3d_timoshenko():
    L, b, h, P = 1.0, 0.1, 0.1, 1e3
    I, A, G = b * h ** 3 / 12, b * h, E / (2 * (1 + NU))
    timo = P * L ** 3 / (3 * E * I) + P * L / (5 / 6 * G * A)
    result = {}
    for kind, n in (("T10", (10, 2, 2)), ("H8", (20, 4, 4))):
        X, el = mesh3d.box(L, b, h, *n, kind)
        m = _model(X, el, kind)
        for d in mesh3d.find3(X, lambda x, y, z: abs(x) < 1e-12):
            m.fix(d, [0, 1, 2])
        tip = mesh3d.find3(X, lambda x, y, z: abs(x - L) < 1e-12)
        if kind == "T10":
            face = [_t6(f, m) for f in mesh3d.boundary_faces([e.nodes[:4] for e in m.elements])
                   if all(abs(X[d, 0] - L) < 1e-12 for d in f)]
        else:
            face = [[e.nodes[i] for i in (1, 2, 6, 5)] for e in m.elements
                   if sum(abs(X[d, 0] - L) < 1e-12 for d in e.nodes) == 4]
        m.F += mesh3d.surface_load(X, face, traction=lambda x, y, z: (0.0, 0.0, -P / (b * h)))
        u = m.static()["u"]
        result[kind] = -np.mean(u[3 * np.array(tip) + 2])
    check("3-D cantilever T10 (10×2×2): Timoshenko beam", result["T10"], timo, rtol=2e-2,
            source="derivation: Timoshenko beam, κ = 5/6; 2% because of the Poisson constraint at the clamped end")
    check_true("3-D cantilever H8: stiffer than T10 due to shear locking", result["H8"] < result["T10"],
          f"H8/T10 = {result['H8'] / result['T10']:.3f}",
          source="Cook et al. 2002 §7: parasitic shear in the trilinear brick")


def test_cantilever_3d_frequency():
    L, b = 1.0, 0.05
    X, el = mesh3d.box(L, b, b, 12, 1, 1, "T10")
    m = _model(X, el, "T10", rho=RHO)
    for d in mesh3d.find3(X, lambda x, y, z: abs(x) < 1e-12):
        m.fix(d, [0, 1, 2])
    w = m.modal(1)["omega"][0]
    I, A = b ** 4 / 12, b * b
    exact = 1.8751 ** 2 * math.sqrt(E * I / (RHO * A * L ** 4))
    check("3-D cantilever T10 first bending frequency ≈ Euler-Bernoulli", w, exact, rtol=3e-2,
            source="Rao, Mechanical Vibrations: β1L = 1.8751 (L/b = 20, small shear effect)")


def test_tet_mesh_from_surface():
    # Box surface → tetrahedral mesh: volume is exact for a convex body
    Xb, elb = mesh3d.box(1.0, 0.5, 0.3, 2, 2, 1, "T4")
    F = np.array(mesh3d.boundary_faces(elb))
    X, tet, info = mesh3d.tet_mesh_from_surface(Xb, F, h=0.1)
    check("tet from surface (box): mesh volume = surface volume", info["ratio"], 1.0, rtol=1e-9,
            source="derivation: convex")
    check("surface volume 0.15 from the signed-volume formula", info["volume_surface"], 0.15, rtol=1e-12)
    w = mesh3d.winding_number(Xb, F, np.array([[0.5, 0.25, 0.15], [1.5, 0.25, 0.15], [0.999, 0.25, 0.15]]))
    check("winding number: interior point 1", w[0], 1.0, atol=1e-9, source="Jacobson et al. 2013")
    check("winding number: exterior point 0", w[1], 0.0, atol=1e-9)
    check("winding number: interior point very close to the surface 1", w[2], 1.0, atol=1e-6)
    # L-shaped (non-convex) body: surface of the union of two boxes
    Xa, ela = mesh3d.box(1.0, 0.4, 0.2, 5, 2, 1, "T4")
    Xc, elc = mesh3d.box(0.4, 0.6, 0.2, 2, 3, 1, "T4", x0=(0.0, 0.4, 0.0))
    Xl = np.vstack([Xa, Xc])
    ell = elb = ela + [[i + Xa.shape[0] for i in t] for t in elc]
    # merge coincident nodes
    unique_X, inverse = np.unique(np.round(Xl, 9), axis=0, return_inverse=True)
    ell = [[int(inverse[i]) for i in t] for t in ell]
    Fl = np.array(mesh3d.boundary_faces(ell))
    X, tet, info = mesh3d.tet_mesh_from_surface(unique_X, Fl, h=0.07)
    check("tet from surface (non-convex L): volume ratio ≈ 1", info["ratio"], 1.0, rtol=2e-2,
            source="derivation: tets not conforming to the boundary may occur at the re-entrant corner; 2% threshold")
    check("L body surface volume 0.08 + 0.048", info["volume_surface"], 0.4 * 0.2 + 0.4 * 0.6 * 0.2, rtol=1e-12)
    m = _model(X, tet, "T4")
    for d in mesh3d.find3(X, lambda x, y, z: abs(x) < 1e-9):
        m.fix(d, [0, 1, 2])
    m.F[2::3] -= 1.0
    r = m.static()
    check_true("tet mesh from surface is solvable (not singular)", np.all(np.isfinite(r["u"])),
               f"residual {r['residual']:.1e}")


def test_tetrahedron_rules():
    from aerokit.fem.elements.solid import rule_tet, rule_tet_duffy
    exact = lambda a, b, c: math.factorial(a) * math.factorial(b) * math.factorial(c) / math.factorial(a + b + c + 3)
    for name, rule, degree in (("4-point", rule_tet(4), 2), ("Duffy n=3", rule_tet_duffy(3), 3),
                              ("Duffy n=4", rule_tet_duffy(4), 5)):
        error = 0.0
        for a in range(degree + 1):
            for b in range(degree + 1 - a):
                for c in range(degree + 1 - a - b):
                    I = sum(w * p[0] ** a * p[1] ** b * p[2] ** c for p, w in rule)
                    error = max(error, abs(I / exact(a, b, c) - 1))
        check(f"tetrahedron rule {name}: monomials of degree ≤ {degree} exact", error, 0.0, atol=1e-12,
                source="∫ xᵃyᵇzᶜ dV = a!b!c!/(a+b+c+3)! (reference tetrahedron)")
