"""Projection / robust TO (aerokit.optimization.projection) and stress-constrained TO (stress_topo).

Formulas from Ferrari & Sigmund 2020, Qian & Sigmund 2013 and Holmberg et al. 2013 as read on 2026-11-03
(prev_guess/01_Ansys/research/Optimizasyon kaynakları/TO_kaynak_paketi.md). Every gradient is checked against central
differences; the size-rule values are the worked table of that pack.
"""
import numpy as np
import scipy.optimize as so

from aerokit.design import card_physics as cp
from aerokit.optimization import projection as pj
from aerokit.optimization import stress_topo as st
from aerokit.optimization import topology as tp
from aerokit.verification import check, check_true, expect_error


def test_projection_limits_and_derivatives():
    x = np.linspace(0, 1, 11)
    check("x̂(0) = 0", float(pj.project(x, 8.0, 0.4)[0]), 0.0, atol=1e-12)
    check("x̂(1) = 1", float(pj.project(x, 8.0, 0.4)[-1]), 1.0, atol=1e-12)
    h = 1e-6
    for beta, eta in ((1.0, 0.5), (8.0, 0.3), (32.0, 0.7)):
        xs = np.linspace(0.05, 0.95, 7)
        fd = (pj.project(xs + h, beta, eta) - pj.project(xs - h, beta, eta)) / (2 * h)
        check(f"∂x̂/∂x̃ = FD (β {beta}, η {eta})", float(np.abs(pj.project_dx(xs, beta, eta) - fd).max()), 0.0,
              atol=1e-5)
        fe = (pj.project(xs, beta, eta + h) - pj.project(xs, beta, eta - h)) / (2 * h)
        check(f"∂x̂/∂η = FD (β {beta}, η {eta})", float(np.abs(pj.project_deta(xs, beta, eta) - fe).max()), 0.0,
              atol=1e-5)


def test_volume_preserving_threshold():
    rng = np.random.default_rng(1)
    xt = rng.beta(0.6, 0.9, 400)
    for beta in (2.0, 16.0, 64.0):
        eta = pj.volume_preserving_eta(xt, beta)
        check(f"V(x̂(η*)) = V(x̃) at β {beta}", float(pj.project(xt, beta, eta).mean()), float(xt.mean()), atol=2e-6)


def test_qian_sigmund_size_rule():
    for eta_d, ratio in ((0.40, 0.63), (0.30, 0.89), (0.25, 1.00), (0.20, 1.11), (0.10, 1.37)):
        check(f"b/R for dilated η {eta_d} (pack §3c table)", pj.min_size_ratio(1 - eta_d), ratio, atol=0.005)
    for r in (0.3, 0.9, 1.0, 1.4, 1.9):
        check(f"Eq. 30 inverts Eq. 29 at b/R = {r}", pj.min_size_ratio(pj.eta_for_size(r)), r, rtol=1e-12)
    check("radius for a 4 mm member on 1 mm elements, η_e 0.75", pj.radius_for_member(4.0, 1.0), 4.0, rtol=1e-12)
    expect_error("eroded threshold below 0.5", pj.min_size_ratio, 0.4, error=ValueError)


def test_projected_chain_rule_volume_preserving():
    pr = tp.mbb_half(12, 6)
    P = pj.Projected(pr.grid, 1.5, pr.passive)
    rng = np.random.default_rng(2)
    x = rng.uniform(0.2, 0.8, pr.grid.nel)
    w = rng.normal(size=pr.grid.nel)
    beta = 6.0
    for vp in (False, True):
        eta = pj.volume_preserving_eta(P.filtered(x), beta) if vp else 0.4
        g = P.chain(x, w, beta, eta, vp)
        fd = np.zeros_like(x)
        h = 1e-6
        for i in range(0, x.size, 7):
            xp, xm = x.copy(), x.copy()
            xp[i] += h
            xm[i] -= h
            fd[i] = (w @ P.physical(xp, beta, 0.4 if not vp else eta, vp)
                     - w @ P.physical(xm, beta, 0.4 if not vp else eta, vp)) / (2 * h)
        idx = np.arange(0, x.size, 7)
        check(f"projected chain rule = FD (volume preserving {vp})", float(np.abs(g[idx] - fd[idx]).max()), 0.0,
              atol=2e-5)


def test_robust_mbb_is_crisper_and_ordered():
    r = pj.topopt_projected(tp.mbb_half(60, 20), 0.5, 3.0, robust=0.25, beta_max=32.0, max_iter=300)
    check_true(f"eroded compliance ≥ dilated ({r['compliance_eroded']:.1f} vs {r['compliance_dilated']:.1f})",
               r["compliance_eroded"] >= r["compliance_dilated"])
    check("dilated volume meets V* = 0.5", r["volume_dilated"], 0.5, atol=0.01)
    check_true(f"blueprint volume below the dilated one ({r['volume_blueprint']:.3f})", r["volume_blueprint"] < 0.5)
    check_true(f"blueprint M_nd below 10 % ({r['gray']:.1f} %)", r["gray"] < 10.0)


def test_centroid_stress_matches_card_physics():
    pr = tp.cantilever(8, 4)
    _, _, U = pr.analysis(np.ones(pr.grid.nel))
    S = st.element_stress(pr, U)
    ref = cp.centre_stress(pr.grid, U, 0.3)
    check("centroid stress = card_physics.centre_stress", float(np.abs(S - ref).max()), 0.0, atol=1e-9)


def test_stress_gradient_matches_finite_differences():
    pr = tp.l_bracket(10, P=1.0)
    ev = pr.passive == 0
    sc = st.StressConstraint(pr, 2.0, ev, n_clusters=3, p=8.0)
    rng = np.random.default_rng(4)
    rho = np.where(pr.passive == 0, rng.uniform(0.3, 0.9, pr.grid.nel), 0.0)
    lu, U = sc.solve(rho)
    sc.recluster(rho, U)
    g, dg = sc.gradient(rho, U, lu)
    h = 1e-6
    idx = np.flatnonzero(ev)[::5]
    for i in range(len(g)):
        fd = []
        for e in idx:
            rp, rm = rho.copy(), rho.copy()
            rp[e] += h
            rm[e] -= h
            fd.append((sc.values(rp, sc.solve(rp)[1])[i] - sc.values(rm, sc.solve(rm)[1])[i]) / (2 * h))
        err = float(np.abs(dg[i, idx] - np.array(fd)).max() / max(np.abs(fd).max(), 1e-12))
        check(f"∂σ^PN/∂ρ (cluster {i}) = FD, relative", err, 0.0, atol=1e-5)


def test_mma_multi_against_slsqp():
    # convex test: min Σ x² s.t. two ball constraints, x in [0, 5]^3
    c1, c2 = np.array([5.0, 2.0, 1.0]), np.array([3.0, 4.0, 3.0])

    def gs(x):
        return np.array([np.sum((x - c1) ** 2) / 9 - 1, np.sum((x - c2) ** 2) / 9 - 1])

    def dgs(x):
        return np.array([2 * (x - c1) / 9, 2 * (x - c2) / 9])

    x = np.array([4.0, 3.0, 2.0])
    lo, hi = np.zeros(3), np.full(3, 5.0)
    xo1 = xo2 = x.copy()
    low = upp = None
    for k in range(1, 80):
        low, upp = tp.mma_asymptote(k, x, xo1, xo2, low, upp, lo, hi)
        xn, _ = st.mma_multi(x, lo, hi, low, upp, 2 * x, gs(x), dgs(x), move=0.5)
        xo2, xo1, x = xo1, x.copy(), xn
    ref = so.minimize(lambda z: z @ z, np.array([4.0, 3.0, 2.0]), jac=lambda z: 2 * z, method="SLSQP",
                      bounds=[(0, 5)] * 3, constraints=[{"type": "ineq", "fun": lambda z: -gs(z),
                                                         "jac": lambda z: -dgs(z)}], options={"ftol": 1e-12})
    check("MMA (m = 2) optimum = SLSQP optimum", float(np.abs(x - ref.x).max()), 0.0, atol=1e-4)


def test_holmberg_l_beam_setup():
    pr, ev, h = st.holmberg_l_beam(20)
    check("element size L/n", h, 10.0, rtol=1e-12)
    check("3 x 2 load elements fixed solid", int(np.sum(pr.passive == 2)), 6)
    check("free elements = 64 % of the square minus the load patch", int(ev.sum()), int(0.64 * 400) - 6)
