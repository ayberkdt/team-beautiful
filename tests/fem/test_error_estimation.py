"""Zienkiewicz-Zhu error estimator: constant-stress patch, convergence on the Kirsch plate, effectivity
index against the exact solution, refinement suggestion on Cook's membrane.

References (closed forms are evaluated in the test, independently of the FEM):
- Kirsch (1898) plate with a hole: Timoshenko & Goodier, Theory of Elasticity, 3rd ed. (1970); the exact
  traction is applied on the outer boundary, so Kirsch's field is the exact solution of the quarter model
- Estimator and recovery: Zienkiewicz & Zhu 1987 (IJNME 24:337), 1992 (IJNME 33:1331)
- Energy-norm convergence rate O(h^p) for elements of degree p on smooth solutions: Zienkiewicz, Taylor &
  Zhu 2013 (a-priori error estimates)
"""
import json
import math

import numpy as np

from aerokit.fem import Model
from aerokit.fem.elements.plane import Q4, Q8, QM6, T3, D_isotropic
from aerokit.fem.error_estimation import (effectivity_index, exact_energy_error, recover_stresses,
                                          zz_error_estimate)
from aerokit.fem.mesh import mesh2d
from aerokit.verification import check, check_true, expect_error

CLASS = {"T3": T3, "Q4": Q4, "QM6": QM6, "Q8": Q8}
A, L, S0, E, NU = 1.0, 5.0, 100.0, 1000.0, 0.3


def _kirsch(x, y):
    r, th = math.hypot(x, y), math.atan2(y, x)
    q = A * A / (r * r)
    sr = S0 / 2 * (1 - q) + S0 / 2 * (1 - 4 * q + 3 * q * q) * math.cos(2 * th)
    st = S0 / 2 * (1 + q) - S0 / 2 * (1 + 3 * q * q) * math.cos(2 * th)
    trt = -S0 / 2 * (1 + 2 * q - 3 * q * q) * math.sin(2 * th)
    c, s = math.cos(th), math.sin(th)
    return (sr * c * c + st * s * s - 2 * trt * s * c, sr * s * s + st * c * c + 2 * trt * s * c,
            (sr - st) * s * c + trt * (c * c - s * s))


def _kirsch_model(kind, nr, nt):
    X, conn, edges = mesh2d.quarter_plate_with_hole(A, L, nr, nt, kind, ratio=4.0)
    m = Model(X, 2)
    for c in conn:
        m.add(CLASS[kind](c, D_isotropic(E, NU, "stress")))

    def traction(x, y):
        sx, sy, txy = _kirsch(x, y)
        n = (1.0, 0.0) if abs(x - L) < 1e-9 else (0.0, 1.0)
        return (sx * n[0] + txy * n[1], txy * n[0] + sy * n[1])
    m.F += mesh2d.edge_load(X, edges["right"], traction=traction)
    for n in mesh2d.edge_nodes(edges["lower"]):
        m.fix(n, 1)
    for n in mesh2d.edge_nodes(edges["upper"]):
        m.fix(n, 0)
    return m, m.static().u


def test_constant_stress_patch_has_zero_error():
    """MacNeal & Harder (1985) patch with the exact linear displacement field on the boundary."""
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
    meshes = {"T3": (X, [c for e in q for c in ([e[0], e[1], e[2]], [e[0], e[2], e[3]])]), "Q4": (X, q),
              "QM6": (X, q), "Q8": (np.array(X8), q8)}
    exact = lambda x, y: (1e-3 * (x + y / 2), 1e-3 * (y + x / 2))
    for kind, (Xp, conn) in meshes.items():
        m = Model(Xp, 2)
        for c in conn:
            m.add(CLASS[kind](c, D_isotropic(1e6, 0.25, "stress"), t=0.001))
        for n in range(Xp.shape[0]):
            if n not in (4, 5, 6, 7):
                ux, uy = exact(*Xp[n])
                m.fix(n, 0, ux)
                m.fix(n, 1, uy)
        u = m.static().u
        for method in ("spr", "average"):
            est = zz_error_estimate(m, u, method=method)
            check(f"constant-stress patch {kind} ({method}): η = 0", est.eta, 0.0, atol=1e-12,
                  source="Zienkiewicz & Zhu 1987: recovery reproduces a field the elements represent exactly")
            S = recover_stresses(m, u, method)
            check(f"constant-stress patch {kind} ({method}): recovered σx = 1333.3 at every node",
                  np.abs(S[:, 0] - 4000 / 3).max(), 0.0, atol=1e-8, source="MacNeal & Harder 1985: σx = σy = 1333")


def test_kirsch_convergence_and_effectivity():
    """η falls at the a-priori energy-norm rate (≈ h¹ for Q4, h² for Q8); the effectivity θ = ‖e*‖/‖e‖ ≈ 1."""
    levels = ((4, 8), (8, 16), (16, 32))
    for kind, rate, (lo, hi) in (("Q4", 1.0, (0.8, 1.2)), ("Q8", 2.0, (1.6, 2.4))):
        eta, theta, theta_avg = [], [], []
        for nr, nt in levels:
            m, u = _kirsch_model(kind, nr, nt)
            est = zz_error_estimate(m, u, method="spr")
            ex, _ = exact_energy_error(m, u, _kirsch)
            eta.append(est.eta)
            theta.append(effectivity_index(est, ex))
            if kind == "Q4":
                theta_avg.append(effectivity_index(zz_error_estimate(m, u, method="average"), ex))
        p = math.log(eta[-2] / eta[-1]) / math.log(2)
        detail = f"η = {[f'{v:.3e}' for v in eta]}, θ = {[f'{v:.3f}' for v in theta]}"
        check_true(f"Kirsch {kind}: η decreases monotonically with refinement", eta[0] > eta[1] > eta[2], detail)
        # measured (this implementation): Q4 p = 0.925, Q8 p = 2.006 on the two finest meshes
        check_true(f"Kirsch {kind} SPR: observed rate of η in [{lo}, {hi}] (theory h^{rate:g})", lo <= p <= hi,
                   f"p = {p:.3f}; {detail}", source="Zienkiewicz, Taylor & Zhu 2013: ‖e‖ = O(h^p) on smooth solutions")
        # measured: θ(Q4, 16×32) = 0.988, θ(Q8, 16×32) = 0.905 (Q8 also carries the isoparametric hole-geometry error)
        check(f"Kirsch {kind} SPR 16×32: effectivity index θ ≈ 1", theta[-1], 1.0, atol=0.15,
              source="Zienkiewicz & Zhu 1992: SPR estimator is asymptotically exact (θ → 1)")
        if kind == "Q4":
            check(f"Kirsch {kind} nodal averaging 16×32: θ ≈ 1", theta_avg[-1], 1.0, atol=0.15,
                  source="Zienkiewicz & Zhu 1987 (linear elements)")


def test_refinement_suggestion_and_result():
    m, u = _kirsch_model("Q4", 8, 16)
    est = zz_error_estimate(m, u, fraction=0.5)
    top = int(est.elements[np.argmax(est.element_error)])
    r_top = min(math.hypot(*m.X[n]) for n in m.elements[top].nodes)
    check_true("Kirsch Q4: largest error indicator within r < 2a of the hole (stress concentration zone)", r_top < 2 * A,
               f"min radius of the worst element {r_top:.3f}")
    check_true("refinement list = elements with indicator ≥ 0.5·max",
               set(est.refine.tolist()) == {int(i) for i, v in zip(est.elements, est.element_error, strict=True)
                                            if v >= 0.5 * est.element_error.max()})
    check("fraction = 0 proposes every element", len(zz_error_estimate(m, u, fraction=0.0).refine), len(m.elements))
    check_true("fraction = 1 proposes only the worst element", zz_error_estimate(m, u, fraction=1.0).refine.tolist() == [top])
    check("‖e‖² = Σ element indicators²", est.error_norm ** 2, float((est.element_error ** 2).sum()), rtol=1e-12)
    # ∫σᵀD⁻¹σ dV is integrated with 3×3 points, K with 2×2; on distorted Q4 the integrand is rational
    # (measured relative difference 4e-6)
    check("‖u‖² ≈ uᵀKu (Q4, different quadrature)", est.energy_norm ** 2, float(u @ (m.K() @ u)), rtol=1e-4,
          source="derivation: ∫σᵀD⁻¹σ dV = ∫εᵀDε dV = uᵀKu")
    check_true("ErrorEstimate is a read-only mapping", est["eta"] is est.eta and "recovered" in est)
    check_true("ErrorEstimate.to_dict() is JSON serialisable", isinstance(json.dumps(est.to_dict()), str))
    expect_error("fraction outside [0, 1] raises", zz_error_estimate, m, u, "spr", 1.5, error=ValueError)
    expect_error("unknown recovery method raises", recover_stresses, m, u, "magic", error=ValueError)


def test_cook_membrane_indicator():
    """Cook's membrane (Q4 8×8): the error concentrates at the clamped edge corners (stress singularities)."""
    X, conn, edges = mesh2d.cook(8, 8, "Q4")
    m = Model(X, 2)
    for c in conn:
        m.add(Q4(c, D_isotropic(1.0, 1 / 3, "stress")))
    m.F += mesh2d.edge_load(X, edges["right"], traction=lambda x, y: (0.0, 1.0 / 16.0))
    for n in mesh2d.edge_nodes(edges["left"]):
        m.fix(n, [0, 1])
    u = m.static().u
    est = zz_error_estimate(m, u)
    top = int(est.elements[np.argmax(est.element_error)])
    check_true("Cook Q4: worst element touches the clamped edge x = 0",
               any(abs(m.X[n, 0]) < 1e-12 for n in m.elements[top].nodes),
               f"element {top}, η = {est.eta:.3f}", source="Bergan & Felippa 1985 geometry; clamped corners are singular")
    coarse = zz_error_estimate(*_cook(4))
    check_true("Cook Q4: η(8×8) < η(4×4)", est.eta < coarse.eta, f"{coarse.eta:.3f} → {est.eta:.3f}")


def _cook(n):
    X, conn, edges = mesh2d.cook(n, n, "Q4")
    m = Model(X, 2)
    for c in conn:
        m.add(Q4(c, D_isotropic(1.0, 1 / 3, "stress")))
    m.F += mesh2d.edge_load(X, edges["right"], traction=lambda x, y: (0.0, 1.0 / 16.0))
    for d in mesh2d.edge_nodes(edges["left"]):
        m.fix(d, [0, 1])
    return m, m.static().u
