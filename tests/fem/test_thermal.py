"""FEM heat conduction and thermal stress: slab, convection, fin, heat generation, patch tests,
clamped and free heated bodies.

Closed-form references are computed inside each test, independently of the FEM:
- Plane wall with fixed temperatures / convective face, fin with an adiabatic tip:
  Incropera, DeWitt, Bergman & Lavine, Fundamentals of Heat and Mass Transfer, 6th ed. (2007), Ch. 3
- Exact 2-D fin temperature: separation of variables, θ = Σ Cₙ cos(λₙ y) cosh(λₙ (L − x)) / cosh(λₙ L),
  λₙ tan(λₙ δ) = h/k, Cₙ = 2 sin(λₙ δ) / (λₙ δ + sin λₙ δ cos λₙ δ) (derived in the test)
- Thermal stress of restrained / free bodies: Boley & Weiner, Theory of Thermal Stresses (1960);
  plane strain: εz = 0 gives σx = −E α ΔT / (1 − ν) for εx = σy = 0 (derivation)
- Patch test: MacNeal & Harder 1985 patch geometry
"""
import math

import numpy as np
from scipy.optimize import brentq

from aerokit.fem import Model
from aerokit.fem.elements.line import Bar
from aerokit.fem.elements.plane import Q4, Q8, QM6, T3, D_isotropic, D_orthotropic
from aerokit.fem.elements.solid import H8, T4, T10, D_isotropic3d
from aerokit.fem.mesh import mesh2d, mesh3d
from aerokit.fem.thermal import (ConvectionBoundary, HeatFluxBoundary, HeatH8, HeatQ4, HeatQ8, HeatT3, HeatTet4,
                                 conductivity_matrix, thermal_load, thermal_stresses)
from aerokit.verification import check, check_true, expect_error

HEAT = {"T3": HeatT3, "Q4": HeatQ4, "Q8": HeatQ8}
PLANE = {"T3": T3, "Q4": Q4, "QM6": QM6, "Q8": Q8}
E, NU, ALPHA, DT = 70e9, 0.33, 23e-6, 150.0


def _heat_model(X, conn, kind, k, t=1.0, **kw):
    m = Model(X, 1)
    for c in conn:
        m.add(HEAT[kind](c, k, t=t, **kw))
    return m


def _plane_model(X, conn, kind, format="stress", t=1.0):
    m = Model(X, 2)
    D = D_isotropic(E, NU, format)
    for c in conn:
        m.add(PLANE[kind](c, D, format=format, t=t, nu=NU))
    return m


def _patch():
    """MacNeal & Harder 1985 membrane patch (0.24 × 0.12, four interior nodes) and its Q8 version."""
    X = np.array([[0, 0], [0.24, 0], [0.24, 0.12], [0, 0.12],
                  [0.04, 0.02], [0.18, 0.03], [0.16, 0.08], [0.08, 0.08]], dtype=float)
    q = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]]
    mid: dict[tuple[int, int], int] = {}
    X8 = list(X)
    q8 = []
    for e in q:
        extra = []
        for i in range(4):
            key = tuple(sorted((e[i], e[(i + 1) % 4])))
            if key not in mid:
                mid[key] = len(X8)
                X8.append(0.5 * (X[e[i]] + X[e[(i + 1) % 4]]))
            extra.append(mid[key])
        q8.append(e + extra)
    t3 = [c for e in q for c in ([e[0], e[1], e[2]], [e[0], e[2], e[3]])]
    return {"T3": (X, t3), "Q4": (X, q), "QM6": (X, q), "Q8": (np.array(X8), q8)}, {4, 5, 6, 7}


# ---------------- conduction ----------------
def test_slab_linear_profile():
    L, H, t, k, T1, T2 = 0.1, 0.05, 0.004, 45.0, 300.0, 400.0
    q_exact = -k * (T2 - T1) / L
    for kind in ("T3", "Q4", "Q8"):
        X, conn, edges = mesh2d.rectangle(L, H, 5, 3, kind)
        m = _heat_model(X, conn, kind, k, t=t)
        for n in mesh2d.edge_nodes(edges["left"]):
            m.fix(n, 0, T1)
        for n in mesh2d.edge_nodes(edges["right"]):
            m.fix(n, 0, T2)
        r = m.static()
        err = np.abs(r.u - (T1 + (T2 - T1) * X[:, 0] / L)).max()
        check(f"slab {kind}: nodal temperatures follow T1 + ΔT x/L", err, 0.0, atol=1e-10 * (T2 - T1),
              source="Incropera et al. 2007, Ch. 3 plane wall (linear profile)")
        q = np.array([p["flux"] for s in m.element_results(r.u) for p in s["points"]])
        check(f"slab {kind}: heat flux qx = −k ΔT/L at every Gauss point", np.abs(q[:, 0] - q_exact).max(), 0.0,
              atol=1e-9 * abs(q_exact))
        check(f"slab {kind}: qy = 0", np.abs(q[:, 1]).max(), 0.0, atol=1e-9 * abs(q_exact))
        Q_in = r.reaction[mesh2d.edge_nodes(edges["left"])].sum()
        check(f"slab {kind}: heat flow through the cold face = k A ΔT / L", Q_in, q_exact * H * t, rtol=1e-10)
    # 3-D bricks and tetrahedra, orthotropic conductivity (only kx matters for a 1-D field)
    for name, kind, cls in (("HeatH8", "H8", HeatH8), ("HeatTet4", "T4", HeatTet4)):
        X, el = mesh3d.box(L, H, H, 4, 2, 2, kind)
        m = Model(X, 1)
        for c in el:
            m.add(cls(c, (k, 3 * k, 0.5 * k)))
        for n in mesh3d.find3(X, lambda x, y, z: abs(x) < 1e-12):
            m.fix(n, 0, T1)
        for n in mesh3d.find3(X, lambda x, y, z: abs(x - L) < 1e-12):
            m.fix(n, 0, T2)
        T = m.static().u
        check(f"slab {name} (orthotropic k): linear profile exact", np.abs(T - (T1 + (T2 - T1) * X[:, 0] / L)).max(),
              0.0, atol=1e-10 * (T2 - T1), source="Incropera et al. 2007, Ch. 3 plane wall")


def test_convective_face_and_heat_flux():
    """Fixed temperature on the left, film condition on the right: q = (T1 − T∞)/(L/k + 1/h)."""
    L, H, k, h, T1, Tinf = 0.2, 0.1, 15.0, 80.0, 500.0, 300.0
    q = (T1 - Tinf) / (L / k + 1 / h)
    for kind in ("T3", "Q4", "Q8"):
        X, conn, edges = mesh2d.rectangle(L, H, 4, 2, kind)
        m = _heat_model(X, conn, kind, k)
        for e in edges["right"]:
            m.add(ConvectionBoundary(e, h, Tinf))
        for n in mesh2d.edge_nodes(edges["left"]):
            m.fix(n, 0, T1)
        T = m.static().u
        exact = T1 - q * X[:, 0] / k
        check(f"convective face {kind}: T(x) = T1 − q x/k with q = (T1 − T∞)/(L/k + 1/h)",
              np.abs(T - exact).max(), 0.0, atol=1e-9 * (T1 - Tinf),
              source="Incropera et al. 2007, Ch. 3 thermal resistance network (conduction + convection)")
        loss = sum(r["heat_loss"] for e, r in zip(m.elements, m.element_results(T), strict=True)
                   if isinstance(e, ConvectionBoundary))
        check(f"convective face {kind}: convected heat = q·H", loss, q * H, rtol=1e-10)
    # 3-D: film condition on quadrilateral (H8) and triangular (T4) faces
    for kind, cls in (("H8", HeatH8), ("T4", HeatTet4)):
        X, el = mesh3d.box(L, H, H, 4, 2, 2, kind)
        m = Model(X, 1)
        for c in el:
            m.add(cls(c, k))
        if kind == "H8":
            faces = [[c[1], c[2], c[6], c[5]] for c in el if all(abs(X[c[i], 0] - L) < 1e-12 for i in (1, 2, 6, 5))]
        else:
            faces = [list(f) for f in mesh3d.boundary_faces(el) if all(abs(X[i, 0] - L) < 1e-12 for i in f)]
        for f in faces:
            m.add(ConvectionBoundary(f, h, Tinf))
        for n in mesh3d.find3(X, lambda x, y, z: abs(x) < 1e-12):
            m.fix(n, 0, T1)
        T = m.static().u
        check(f"convective face 3-D {kind}: linear profile with q = (T1 − T∞)/(L/k + 1/h)",
              np.abs(T - (T1 - q * X[:, 0] / k)).max(), 0.0, atol=1e-9 * (T1 - Tinf),
              source="Incropera et al. 2007, Ch. 3 thermal resistance network")
    # the same slab driven by a prescribed heat flux instead of the film condition
    X, conn, edges = mesh2d.rectangle(L, H, 4, 2, "Q8")
    m = _heat_model(X, conn, "Q8", k)
    for e in edges["right"]:
        m.add(HeatFluxBoundary(e, -q))
    for n in mesh2d.edge_nodes(edges["left"]):
        m.fix(n, 0, T1)
    T = m.static().u
    check("heat-flux face Q8: same linear profile as the convective face", np.abs(T - (T1 - q * X[:, 0] / k)).max(),
          0.0, atol=1e-9 * (T1 - Tinf), source="derivation: q leaves through the right face")


def _fin_series(h, k, dlt, L, n_terms=60):
    lam = [brentq(lambda v: v * math.tan(v * dlt) - h / k, (j * math.pi + 1e-12) / dlt,
                  ((j + 0.5) * math.pi - 1e-12) / dlt) for j in range(n_terms)]

    def theta(x, y):                                       # θ/θb, overflow-safe cosh ratio
        s = 0.0
        for v in lam:
            C = 2 * math.sin(v * dlt) / (v * dlt + math.sin(v * dlt) * math.cos(v * dlt))
            s += C * math.cos(v * y) * (math.exp(-v * x) + math.exp(-v * (2 * L - x))) / (1 + math.exp(-2 * v * L))
        return s
    return theta


def test_convection_fin():
    """Straight rectangular fin of thickness 2δ, base temperature Tb, convection on both faces, adiabatic tip."""
    k, h, dlt, L, Tb, Tinf = 200.0, 25.0, 0.002, 0.05, 100.0, 20.0
    theta = _fin_series(h, k, dlt, L)
    mf = math.sqrt(h / (k * dlt))
    check("fin reference: 2-D series tip = 1-D fin cosh formula within O(Bi) (Bi = 2.5e-4)",
          theta(L, 0.0), 1 / math.cosh(mf * L), rtol=1e-4, source="Incropera et al. 2007, Ch. 3 fin, adiabatic tip")
    for kind, nx, ny, tol in (("Q4", 80, 4, 1e-5), ("Q8", 20, 2, 1e-8)):
        X, conn, edges = mesh2d.rectangle(L, 2 * dlt, nx, ny, kind, y0=-dlt)
        m = _heat_model(X, conn, kind, k)
        for e in edges["lower"] + edges["upper"]:
            m.add(ConvectionBoundary(e, h, Tinf))
        for n in mesh2d.edge_nodes(edges["left"]):
            m.fix(n, 0, Tb)
        r = m.static()
        tip = mesh2d.find(X, lambda x, y: abs(x - L) < 1e-12 and abs(y) < 1e-12)[0]
        # measured: Q4 80×4 3.7e-6, Q8 20×2 5.5e-10 relative to the exact series at the tip
        check(f"fin {kind} {nx}×{ny}: tip temperature = exact 2-D series", r.u[tip], Tinf + (Tb - Tinf) * theta(L, 0.0),
              rtol=tol, source="separation of variables (derived in the test); λₙ tan(λₙδ) = h/k")
        far = [i for i in range(X.shape[0]) if X[i, 0] >= 0.2 * L]
        err = max(abs(r.u[i] - Tinf - (Tb - Tinf) * theta(*X[i])) for i in far) / (Tb - Tinf)
        check_true(f"fin {kind}: nodal error (x ≥ 0.2 L) below 1e-4 of θb", err < 1e-4, f"{err:.2e}")
        q_base = r.reaction[mesh2d.edge_nodes(edges["left"])].sum()
        q_fin = math.sqrt(h * 2 * k * 2 * dlt) * (Tb - Tinf) * math.tanh(mf * L)
        check(f"fin {kind}: base heat rate = √(hPkA) θb tanh(mL) within O(Bi)", q_base, q_fin, rtol=2e-4,
              source="Incropera et al. 2007, Ch. 3 fin heat rate (per unit depth: P = 2, A = 2δ)")


def test_heat_generation_and_errors():
    L, H, k, Q, T0 = 0.04, 0.01, 2.0, 5e5, 20.0
    for kind in ("Q4", "Q8"):
        X, conn, edges = mesh2d.rectangle(L, H, 8, 2, kind)
        m = _heat_model(X, conn, kind, k, heat_source=Q)
        for n in mesh2d.edge_nodes(edges["left"] + edges["right"]):
            m.fix(n, 0, T0)
        T = m.static().u
        exact = T0 + Q * X[:, 0] * (L - X[:, 0]) / (2 * k)
        check(f"uniform heat generation {kind}: nodal T = T0 + Q x(L − x)/(2k)", np.abs(T - exact).max(), 0.0,
              atol=1e-9 * Q * L * L / (8 * k), source="Incropera et al. 2007, Ch. 3 plane wall with generation; "
              "linear elements are nodally exact in 1-D")
    expect_error("conductivity that is not positive definite raises", conductivity_matrix, [[1.0, 2.0], [2.0, 1.0]], 2,
                 error=ValueError)
    expect_error("HeatQ4 with 3 nodes raises", HeatQ4, [0, 1, 2], 1.0, error=ValueError)


def test_conduction_patch_test():
    meshes, inner = _patch()
    a, b, c = 10.0, 300.0, -150.0
    k = np.array([[3.0, 0.5], [0.5, 1.5]])                     # anisotropic tensor
    for kind in ("T3", "Q4", "Q8"):
        X, conn = meshes[kind]
        m = _heat_model(X, conn, kind, k)
        free = inner if kind != "Q8" else inner
        for n in range(X.shape[0]):
            if n not in free:
                m.fix(n, 0, a + b * X[n, 0] + c * X[n, 1])
        T = m.static().u
        err = max(abs(T[n] - (a + b * X[n, 0] + c * X[n, 1])) for n in free)
        check(f"conduction patch {kind}: interior temperatures exact for T = a + bx + cy", err, 0.0, atol=1e-12,
              source="MacNeal & Harder 1985 patch geometry; linear field is in every element's basis")
        q = np.array([p["flux"] for s in m.element_results(T) for p in s["points"]])
        check(f"conduction patch {kind}: flux −k∇T constant at every Gauss point",
              np.abs(q - (-k @ np.array([b, c]))).max(), 0.0, atol=1e-9)


# ---------------- thermal stress ----------------
def test_clamped_bar_uniform_heating():
    L, H = 1.0, 0.1
    s_stress = -E * ALPHA * DT
    for kind in ("T3", "Q4", "QM6", "Q8"):
        for format, expected in (("stress", s_stress), ("strain", -E * ALPHA * DT / (1 - NU))):
            X, conn, _ = mesh2d.rectangle(L, H, 10, 2, kind)
            m = _plane_model(X, conn, kind, format, t=0.01)
            for n in mesh2d.find(X, lambda x, y: abs(x) < 1e-12 or abs(x - L) < 1e-12):
                m.fix(n, 0)
            m.fix(0, 1)
            dT = np.full(m.n_node, DT)
            u = m.static(F=thermal_load(m, dT, ALPHA)).u
            res = thermal_stresses(m, u, dT, ALPHA)
            s = np.array([p["sigma"] for r in res for p in r["points"]])
            source = ("Boley & Weiner 1960: fully restrained bar σ = −EαΔT" if format == "stress" else
                      "derivation: εx = σy = εz = 0 → σx = −EαΔT/(1−ν) = −(1+ν)αΔT·E/(1−ν²)")
            check(f"clamped bar {kind} plane {format}: σx", np.abs(s[:, 0] / expected - 1).max(), 0.0, atol=1e-9,
                  source=source)
            check(f"clamped bar {kind} plane {format}: σy = τxy = 0", np.abs(s[:, 1:]).max(), 0.0,
                  atol=1e-9 * abs(expected))
            if format == "strain":
                sz = np.array([p["sigma_z"] for r in res for p in r["points"]])
                check(f"clamped bar {kind} plane strain: σz = νσx − EαΔT", np.abs(sz - (NU * expected - E * ALPHA * DT)).max(),
                      0.0, atol=1e-9 * abs(expected), source="derivation: εz = 0")
    # truss bar between two walls: N = −EAαΔT, wall reactions ±EAαΔT
    m = Model([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]], 2)
    for i in range(2):
        m.add(Bar(i, i + 1, E, 1e-4))
    m.fix(0, [0, 1])
    m.fix(2, [0, 1])
    m.fix(1, 1)
    dT = np.array([DT, DT, DT])
    r = m.static(F=thermal_load(m, dT, ALPHA))
    check("clamped Bar: σ = −EαΔT", thermal_stresses(m, r.u, dT, ALPHA)[0]["sigma"], s_stress, rtol=1e-12,
          source="Boley & Weiner 1960")
    check("clamped Bar: left wall pushes with +EAαΔT (+x)", r.reaction[0], E * 1e-4 * ALPHA * DT, rtol=1e-12)


def test_free_body_uniform_heating_is_stress_free():
    meshes, inner = _patch()
    for kind in ("T3", "Q4", "QM6", "Q8"):
        for format, factor in (("stress", 1.0), ("strain", 1 + NU)):
            X, conn = meshes[kind]
            m = _plane_model(X, conn, kind, format)
            m.fix(0, [0, 1])
            m.fix(1, 1)                                            # statically determinate supports
            dT = np.full(m.n_node, DT)
            u = m.static(F=thermal_load(m, dT, ALPHA)).u.reshape(-1, 2)
            res = thermal_stresses(m, u.ravel(), dT, ALPHA)
            s = np.array([p["sigma"] for r in res for p in r["points"]])
            check(f"free patch {kind} plane {format}: stress-free under uniform ΔT", np.abs(s).max(), 0.0,
                  atol=1e-9 * E * ALPHA * DT, source="Boley & Weiner 1960: unrestrained uniform heating")
            check(f"free patch {kind} plane {format}: u = {factor:.2f}·αΔT·x",
                  np.abs(u - factor * ALPHA * DT * X).max(), 0.0, atol=1e-12,
                  source="plane strain: εz = 0 gives in-plane strain (1+ν)αΔT")
    # axisymmetric free ring: u_r = α ΔT r
    X, conn, _ = mesh2d.rectangle(0.1, 0.05, 4, 2, "Q8", x0=0.05)
    m = _plane_model(X, conn, "Q8", "axisymmetric")
    m.fix(0, 1)
    dT = np.full(m.n_node, DT)
    u = m.static(F=thermal_load(m, dT, ALPHA)).u
    check("free axisymmetric ring Q8: u_r = αΔT r", np.abs(u[0::2] - ALPHA * DT * X[:, 0]).max(), 0.0, atol=1e-12,
          source="Boley & Weiner 1960")
    # solids: free block expands freely, confined block σ = −EαΔT/(1−2ν)
    D = D_isotropic3d(E, NU)
    for kind, cls in (("H8", H8), ("T4", T4), ("T10", T10)):
        X, el = mesh3d.box(1.0, 0.5, 0.4, 2, 2, 2, kind)
        free = Model(X, 3)
        confined = Model(X, 3)
        for c in el:
            free.add(cls(c, D))
            confined.add(cls(c, D))
        free.fix(0, [0, 1, 2])
        free.fix(mesh3d.find3(X, lambda x, y, z: abs(x - 1) + abs(y) + abs(z) < 1e-12)[0], [1, 2])
        free.fix(mesh3d.find3(X, lambda x, y, z: abs(x) + abs(y - 0.5) + abs(z) < 1e-12)[0], [2])
        dT = np.full(free.n_node, DT)
        u = free.static(F=thermal_load(free, dT, ALPHA)).u
        s = np.array([p["sigma"] for r in thermal_stresses(free, u, dT, ALPHA) for p in r["points"]])
        check(f"free block {kind}: stress-free, u = αΔT x", np.abs(u.reshape(-1, 3) - ALPHA * DT * X).max(), 0.0,
              atol=1e-12, source="Boley & Weiner 1960")
        check(f"free block {kind}: σ = 0", np.abs(s).max(), 0.0, atol=1e-9 * E * ALPHA * DT)
        for d, L in enumerate((1.0, 0.5, 0.4)):
            for n in mesh3d.find3(X, lambda x, y, z, d=d, L=L: abs((x, y, z)[d]) < 1e-12 or abs((x, y, z)[d] - L) < 1e-12):
                confined.fix(n, d)
        u = confined.static(F=thermal_load(confined, dT, ALPHA)).u
        s = np.array([p["sigma"] for r in thermal_stresses(confined, u, dT, ALPHA) for p in r["points"]])
        expected = -E * ALPHA * DT / (1 - 2 * NU)
        check(f"confined block {kind}: σx = σy = σz = −EαΔT/(1−2ν)", np.abs(s[:, :3] / expected - 1).max(), 0.0,
              atol=1e-9, source="derivation: ε = 0 → σ = −(3λ+2μ)αΔT")


def test_thermal_patch_test():
    meshes, inner = _patch()
    for kind in ("T3", "Q4", "QM6", "Q8"):
        X, conn = meshes[kind]
        m = _plane_model(X, conn, kind)
        for n in range(X.shape[0]):
            if n not in inner:
                m.fix(n, 0, ALPHA * DT * X[n, 0])
                m.fix(n, 1, ALPHA * DT * X[n, 1])
        dT = np.full(m.n_node, DT)
        u = m.static(F=thermal_load(m, dT, ALPHA)).u
        err = max(abs(u[2 * n] - ALPHA * DT * X[n, 0]) + abs(u[2 * n + 1] - ALPHA * DT * X[n, 1]) for n in inner)
        check(f"thermal patch {kind}: interior displacements = free expansion", err, 0.0, atol=1e-15,
              source="MacNeal & Harder 1985 patch; constant initial strain must be reproduced exactly")
        s = np.array([p["sigma"] for r in thermal_stresses(m, u, dT, ALPHA) for p in r["points"]])
        check(f"thermal patch {kind}: σ = 0 at every Gauss point", np.abs(s).max(), 0.0, atol=1e-12 * E * ALPHA * DT)


def test_linear_temperature_free_plate_and_coupling():
    """A free plate with a linear temperature field is stress-free (compatible thermal strain).

    The temperature comes from a conduction solution on the same Q8 mesh (heat → stress coupling).
    """
    L, H, T1, T2 = 0.4, 0.2, 0.0, 200.0
    X, conn, edges = mesh2d.rectangle(L, H, 4, 2, "Q8")
    heat = _heat_model(X, conn, "Q8", 120.0)
    for n in mesh2d.edge_nodes(edges["left"]):
        heat.fix(n, 0, T1)
    for n in mesh2d.edge_nodes(edges["right"]):
        heat.fix(n, 0, T2)
    dT = heat.static().u
    m = _plane_model(X, conn, "Q8")
    m.fix(0, [0, 1])
    m.fix(mesh2d.find(X, lambda x, y: abs(x - L) < 1e-12 and abs(y) < 1e-12)[0], 1)
    u = m.static(F=thermal_load(m, dT, ALPHA)).u.reshape(-1, 2)
    s = np.array([p["sigma"] for r in thermal_stresses(m, u.ravel(), dT, ALPHA) for p in r["points"]])
    check("linear ΔT, free Q8 plate: stress-free", np.abs(s).max(), 0.0, atol=1e-8 * E * ALPHA * T2,
          source="Boley & Weiner 1960: linear temperature in a free plate gives no stress")
    b = (T2 - T1) / L
    x, y = X[:, 0], X[:, 1]
    exact = np.column_stack([ALPHA * b * (x * x - y * y) / 2, ALPHA * b * x * y])
    check("linear ΔT, free Q8 plate: u = αb(x² − y²)/2, v = αbxy (rigid motion removed by the supports)",
          np.abs(u - exact).max(), 0.0, atol=1e-13, source="derivation: εx = εy = αbx, γxy = 0")
    # fully restrained (u = 0) Q4 strip with ΔT linear in x: σx = σy = −EαΔT(x)/(1−ν) at each Gauss point
    X, conn, _ = mesh2d.rectangle(1.0, 0.1, 8, 1, "Q4")
    m = _plane_model(X, conn, "Q4")
    dT = DT * X[:, 0]
    pts = [p for r in thermal_stresses(m, np.zeros(m.n_dof), dT, ALPHA) for p in r["points"]]
    s = np.array([p["sigma"] for p in pts])
    xg = np.array([p["x"][0] for p in pts])
    check("restrained Q4 strip, linear ΔT: σx = σy = −EαΔT(x)/(1−ν) at the Gauss points",
          np.abs(s[:, :2] + (E * ALPHA * DT * xg / (1 - NU))[:, None]).max(), 0.0, atol=1e-6 * E * ALPHA * DT,
          source="derivation: ε = 0 in plane stress, ΔT interpolated with the shape functions")

def test_thermal_errors():
    X, conn, _ = mesh2d.rectangle(1.0, 1.0, 1, 1, "Q4")
    m = Model(X, 2)
    m.add(Q4(conn[0], D_orthotropic(140e9, 10e9, 0.3, 5e9, 30.0), format="strain"))
    expect_error("plane strain with anisotropic D and no ν raises", thermal_load, m, np.ones(4), ALPHA,
                 error=ValueError)
    check_true("plane strain anisotropic: explicit alpha vector accepted",
               np.all(np.isfinite(thermal_load(m, np.ones(4), [1e-6, 2e-5, 0.0]))))
    expect_error("wrong dT length raises", thermal_load, m, np.ones(3), ALPHA, error=ValueError)
    h = Model(X, 1)
    h.add(HeatQ4(conn[0], 1.0))
    expect_error("thermal load on a conduction element raises TypeError", thermal_load, h, np.ones(4), ALPHA,
                 error=TypeError)
