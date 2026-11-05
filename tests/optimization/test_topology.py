"""Topology optimization (aerokit.optimization.topology): KE, numbering, filter, sensitivities, OC, MMA, top88.

References (read from the source in this repository):
- Andreassen, Clausen, Schevenels, Lazarov & Sigmund 2011, Struct Multidisc Optim 43:1–16 (top88),
  KU Leuven Lirias preprint: KE (lines 8–12), Fig. 3 (MBB 60×20: c = 216.81 sensitivity filter,
  c = 233.71 density filter), Fig. 8 (Heaviside, rmin = 1.8: c = 189.14). The paper does NOT give
  iteration counts; the iteration checks are regressions against this translation's own result.
- Svanberg 1987 "beam" problem and MMA iterations: Deetman, GCMMA-MMA-Python,
  examples/mma_beam2.py and mma_beam2.log (Python counterpart of Svanberg's MATLAB code).
  Svanberg's 2007 notes ("MMA and GCMMA") could not be downloaded and were not read.
- Gray measure M_nd: Sigmund 2007, Struct Multidisc Optim 33:401 (definition given in the task; paper not read).
"""
import math

import numpy as np
from scipy.optimize import minimize

from aerokit.optimization import topology as T
from aerokit.fem import Model
from aerokit.fem.mesh import mesh2d
from aerokit.fem.elements.plane import Q4, D_isotropic
from aerokit.fem.elements.solid import H8, D_isotropic3d
from aerokit.verification import check, check_true, expect_error

SOURCE88 = "Andreassen et al. 2011 (top88), Struct Multidisc Optim 43:1–16"
_CACHE = {}


def _top88(ft, rmin=2.4):
    """The 60×20 MBB runs are used by several tests; each is run once."""
    if (ft, rmin) not in _CACHE:
        _CACHE[(ft, rmin)] = T.top88(60, 20, 0.5, 3, rmin, ft)
    return _CACHE[(ft, rmin)]


def _fd_gradient(problem, dens, x, beta=1.0, h=1e-6):
    g = np.zeros_like(x)
    for e in range(x.size):
        xp, xm = x.copy(), x.copy()
        xp[e] += h
        xm[e] -= h
        g[e] = (T.compliance_and_gradient(problem, dens, xp, beta)[0]
                - T.compliance_and_gradient(problem, dens, xm, beta)[0]) / (2 * h)
    return g


# ---------------- element stiffnesses ----------------
def test_ke_q4_closed_form():
    nu = 0.3
    KE = T.ke_q4(nu)
    # by hand from top88 lines 8–12: KE[0,0] = (12 − 4ν)/(24(1 − ν²)), KE[0,1] = (3 + 3ν)/(24(1 − ν²)),
    # KE[0,7] = (3 − 9ν)/(24(1 − ν²)) (A12[0,3] = 3, B12[0,3] = −9)
    k = 1 / (24 * (1 - nu ** 2))
    check("KE[0,0] = (12 − 4ν)/(24(1−ν²))", KE[0, 0], (12 - 4 * nu) * k, rtol=1e-15, source=SOURCE88 + ", lines 8–12")
    check("KE[0,1] = (3 + 3ν)/(24(1−ν²))", KE[0, 1], (3 + 3 * nu) * k, rtol=1e-15, source=SOURCE88)
    check("KE[0,7] = (3 − 9ν)/(24(1−ν²))", KE[0, 7], (3 - 9 * nu) * k, rtol=1e-15, source=SOURCE88)
    check_true("KE symmetric", np.array_equal(KE, KE.T))
    w = np.linalg.eigvalsh(KE)
    check("KE: 3 zero-energy modes", int(np.sum(np.abs(w) < 1e-12)), 3, source="derivation: 2-D rigid body")
    # independent: aerokit.fem plane Q4 with 2×2 Gauss, unit square, nodes counter-clockwise from lower-left
    X = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    for n in (0.3, 0.0, 0.25, 0.45):
        Kq = Q4([0, 1, 2, 3], D_isotropic(1.0, n, "stress")).k(X)
        # Exact equality: 2×2 Gauss is the exact integral for the bilinear Q4; the difference is only
        # floating-point rounding at the ±1/√3 points (|KE| ~ 0.5 → 1e-15 absolute ≈ 10 ulp).
        check(f"KE(ν={n}) = Q4 2×2 Gauss (fem plane element) — largest difference", np.abs(T.ke_q4(n) - Kq).max(), 0.0,
              atol=1e-15, source="aerokit.fem.elements.plane.Q4 + D_isotropic(1, ν, 'stress')")


def test_ke_h8():
    X = (T.H8_CORNER + 1) / 2                              # unit cube, node order of solid.H8
    for n in (0.3, 0.2):
        Kh = H8(list(range(8)), D_isotropic3d(1.0, n)).k(X)
        check(f"KE_H8(ν={n}) = fem solid H8 (unit cube) — largest difference", np.abs(T.ke_h8(n) - Kh).max(), 0.0,
              atol=1e-14, source="aerokit.fem.elements.solid.H8 (rounding: |K| ~ 0.5, 24×24 sum)")
    w = np.linalg.eigvalsh(T.ke_h8())
    check("KE_H8: 6 zero-energy modes", int(np.sum(np.abs(w) < 1e-12)), 6, source="derivation: 3-D rigid body")


# ---------------- numbering and assembly ----------------
def test_numbering_top88():
    grid = T.Grid2D(3, 2)
    # 1-based MATLAB result of top88 lines 13–15 (nelx = 3, nely = 2), by hand:
    # nodenrs = [1 4 7 10; 2 5 8 11; 3 6 9 12]; element 1: edofVec = 2·1+1 = 3 →
    # [3 4 9 10 7 8 1 2]; element 2 (lower left): [5 6 11 12 9 10 3 4]
    check_true("edofMat element 0 = top88 [3 4 9 10 7 8 1 2] − 1", list(grid.edof[0] + 1) == [3, 4, 9, 10, 7, 8, 1, 2],
               source=SOURCE88 + ", lines 13–15")
    check_true("edofMat element 1 = top88 [5 6 11 12 9 10 3 4] − 1",
               list(grid.edof[1] + 1) == [5, 6, 11, 12, 9, 10, 3, 4])
    check("ndof = 2(nelx+1)(nely+1)", grid.ndof, 24)
    check("node(0, nely) = 0 (top left, top88 node 1)", grid.node(0, 2), 0)
    check("node(nelx, 0) = last node (bottom right)", grid.node(3, 0), 11)


def test_assembly_independent_fem():
    """Compliance of a random-density cantilever equals aerokit.fem (mesh2d.rectangle + Q4 + Model.static)."""
    nelx, nely, p, Emin = 6, 3, 3.0, 1e-9
    pr = T.cantilever(nelx, nely, penalty=p, Emin=Emin)
    rng = np.random.default_rng(1)
    xf = rng.uniform(0.2, 1.0, pr.grid.nel)
    c = pr.analysis(xf)[0]
    X, link, _ = mesh2d.rectangle(float(nelx), float(nely), nelx, nely, "Q4")
    m = Model(X, 2)
    center = pr.grid.element_center()
    for b in link:
        cx, cy = X[b].mean(axis=0)
        e = int(np.argmin(np.hypot(center[:, 0] - cx, center[:, 1] - cy)))
        m.add(Q4(b, D_isotropic(Emin + xf[e] ** p * (1 - Emin), 0.3, "stress")))
    for n in mesh2d.find(X, lambda x, y: abs(x) < 1e-9):
        m.fix(n, [0, 1])
    load = mesh2d.find(X, lambda x, y: abs(x - nelx) < 1e-9 and abs(y) < 1e-9)[0]
    m.load(load, 1, -1.0)
    u = m.static()["u"]
    check("compliance = Fᵀu (independent aerokit.fem assembly, random x̄)", c, m.F @ u, rtol=1e-10,
          source="aerokit.fem.Model + plane.Q4")


# ---------------- filter ----------------
def test_filter():
    grid = T.Grid2D(12, 8)
    H, Hs = grid.filter_matrix(2.4)
    check_true("H symmetric", abs(H - H.T).max() == 0)
    W = (H.toarray() / Hs[:, None])
    check("filter weights sum to 1 in every row (largest deviation)", np.abs(W.sum(axis=1) - 1).max(), 0.0, atol=1e-15)
    dens = T.Density(grid, 2.4, 2)
    check("density filter preserves a uniform field (x = 0.37)", np.abs(dens.physical(np.full(grid.nel, 0.37)) - 0.37).max(),
          0.0, atol=1e-15)
    # interior element Hs, by hand: 2.4 + 4(1.4) + 4(2.4 − √2) + 4(0.4) + 8(2.4 − √5); √8 > 2.4 → 0
    expected = 2.4 + 4 * 1.4 + 4 * (2.4 - math.sqrt(2)) + 4 * 0.4 + 8 * (2.4 - math.sqrt(5))
    e = 6 * 8 + 4
    check("interior element Hs (rmin = 2.4) by hand", Hs[e], expected, rtol=1e-14, source=SOURCE88 + ", lines 25–44")
    check("corner element Hs (rmin = 2.4): 2.4 + 2(1.4) + (2.4−√2) + 2(0.4) + 2(2.4−√5)", Hs[0],
          2.4 + 2 * 1.4 + (2.4 - math.sqrt(2)) + 2 * 0.4 + 2 * (2.4 - math.sqrt(5)), rtol=1e-14)
    H1, _ = grid.filter_matrix(1.0)
    check("rmin = 1: H diagonal (no neighbours)", H1.nnz, grid.nel)
    grid3 = T.Grid3D(5, 4, 3)
    dens3 = T.Density(grid3, 1.8, 2)
    check("3-D density filter preserves a uniform field", np.abs(dens3.physical(np.full(grid3.nel, 0.6)) - 0.6).max(),
          0.0, atol=1e-15)
    # H symmetric → Hsᵀ x̃ = 1ᵀ H x = (Hᵀ1)ᵀ x = Hsᵀ x  (the Hs-weighted sum is preserved; the plain sum is not, at edges)
    xr = np.linspace(0, 1, grid.nel)
    check("density filter: Σ Hs·x̃ = Σ Hs·x", float(Hs @ dens.intermediate(xr)), float(Hs @ xr), rtol=1e-13,
          source="derivation: H symmetric")


# ---------------- sensitivities: central finite differences ----------------
def test_sensitivity_finite_difference():
    rng = np.random.default_rng(7)
    cases = [
        ("ft=0 (no filter), half MBB 6×4", T.mbb_half(6, 4), 1.5, 0, 1.0),
        ("ft=2 (density filter, chain rule), half MBB 6×4", T.mbb_half(6, 4), 1.8, 2, 1.0),
        ("ft=3 (Heaviside, β = 4), half MBB 6×4", T.mbb_half(6, 4), 1.8, 3, 4.0),
        ("ft=2, two load cases (Σc), cantilever 6×4", T.cantilever_two_load(6, 4), 1.8, 2, 1.0),
        ("ft=2, L-bracket 6×6 with passive elements", T.l_bracket(6), 1.6, 2, 1.0),
        ("ft=2, p = 1 (no penalty)", T.mbb_half(6, 4, penalty=1.0), 1.8, 2, 1.0),
        ("ft=2, 3-D cantilever 4×2×2", T.cantilever_3d(4, 2, 2), 1.5, 2, 1.0),
    ]
    for name, pr, rmin, ft, beta in cases:
        dens = T.Density(pr.grid, rmin, ft, pr.passive)
        for trial in range(2):
            x = rng.uniform(0.15, 0.95, pr.grid.nel)
            _, g = T.compliance_and_gradient(pr, dens, x, beta)
            gfd = _fd_gradient(pr, dens, x, beta)
            error = np.linalg.norm(g - gfd) / np.linalg.norm(gfd)
            check(f"dc/dx = central finite difference: {name} [random field {trial + 1}] (relative ‖·‖)", error, 0.0,
                  atol=1e-6, source="h = 1e-6 central difference; for ft=3 top88 Eqs. (21)–(23)")


# ---------------- scaling property ----------------
def test_uniform_design_scaling():
    pr = T.mbb_half(20, 8)
    c1 = pr.analysis(np.ones(pr.grid.nel))[0]
    for x in (0.3, 0.5, 0.8):
        c = pr.analysis(np.full(pr.grid.nel, x))[0]
        # K(x) = E(x) K(1) → U ∝ 1/E, c = c(1)·E(1)/E(x); since Emin = 1e-9, ≈ c(1)/x^p
        check(f"uniform x = {x}: c = c_solid / (Emin + x^p (E0 − Emin))", c, c1 / (pr.Emin + x ** 3 * (1 - pr.Emin)),
              rtol=1e-10, source="derivation: K linear in E")
        check(f"uniform x = {x}: c ≈ c_solid · x^(−p)", c, c1 / x ** 3, rtol=1e-7)


# ---------------- full / half MBB ----------------
def test_full_half_mbb():
    nx, ny = 16, 6
    half, full = T.mbb_half(nx, ny, P=1.0), T.mbb_full(2 * nx, ny, P=2.0)
    rng = np.random.default_rng(3)
    xy = rng.uniform(0.1, 1.0, (ny, nx))
    xt = np.hstack([xy[:, ::-1], xy])                    # left half mirrored, right half = half model
    cy = half.analysis(half.grid.vector(xy))[0]
    ct = full.analysis(full.grid.vector(xt))[0]
    check("c_full = 2 c_half (random mirrored design, P_full = 2 P_half)", ct, 2 * cy, rtol=1e-9,
          source="derivation: symmetry")
    check("c_full = 2 c_half (uniform x = 0.5)", full.analysis(np.full(full.grid.nel, 0.5))[0],
          2 * half.analysis(np.full(half.grid.nel, 0.5))[0], rtol=1e-9)
    # optimization: rmin = 1 means no filter (in the half model the filter is cut at the symmetry line, in
    # the full model it is not; so filtered runs are not mirror images). The OC bisection takes the same
    # decision with Σx̄_full = 2Σx̄_half.
    ry = T.topopt(half, 0.5, 1.0, ft=1, max_iter=25)
    rt = T.topopt(full, 0.5, 1.0, ft=1, max_iter=25)
    check("OC (unfiltered, 25 it.): c_full/c_half = 2 at every iteration (largest deviation)",
          np.abs(rt["compliance"] / ry["compliance"] - 2).max(), 0.0, atol=1e-7,
          source="derivation: symmetry; deviation is accumulated rounding")
    check("OC (unfiltered): right half of the full design = half design", np.abs(rt["xfiz"][:, nx:] - ry["xfiz"]).max(),
          0.0, atol=1e-6)


# ---------------- comparison with top88 MBB ----------------
def test_top88_mbb_sensitivity_filter():
    r = _top88(1)
    check("top88 MBB 60×20, ft=1: final compliance (Fig. 3: c = 216.81)", r["compliance"][-1], 216.81, atol=0.005,
          source=SOURCE88 + ", Fig. 3 top left; the paper gives 2 decimals → ±0.005")
    check_true("top88 ft=1: converged with change ≤ 0.01", r["converged"], r["iteration"])
    check("top88 ft=1: iteration count (NOT in the paper; this translation's result, regression)", r["iteration"], 106,
          source="regression — no published iteration count was read/found")
    check("top88 ft=1: gray measure M_nd % (regression)", r["gray"], 26.48, rtol=2e-3, source="regression")


def test_top88_mbb_density_filter():
    r = _top88(2)
    check("top88 MBB 60×20, ft=2: final compliance (Fig. 3: c = 233.71)", r["compliance"][-1], 233.71, atol=0.005,
          source=SOURCE88 + ", Fig. 3 bottom left; ±0.005 rounding")
    check_true("top88 ft=2: converged", r["converged"], r["iteration"])
    check("top88 ft=2: iteration count (NOT in the paper; regression)", r["iteration"], 144, source="regression")
    check("top88 ft=2: compliance of the final x̄ ≈ last printed compliance (change ≤ 0.01)", r["compliance_final"],
          r["compliance"][-1], rtol=1e-3)


def test_top88_heaviside():
    r = _top88(3, 1.8)
    check("top88 §5.4 Heaviside MBB 60×20 (rmin = 1.8): final compliance (Fig. 8: c = 189.14)", r["compliance"][-1],
          189.14, atol=0.005, source=SOURCE88 + ", Fig. 8 left; ±0.005 rounding")
    check("Heaviside: β reached 512", r["beta_final"], 512.0, source=SOURCE88 + " §5.4: β 1 → 512")
    check_true("Heaviside: ≤ 50 iterations per β level", np.all(np.unique(r["beta"], return_counts=True)[1] <= 50))
    check_true("Heaviside: nearly black-and-white, M_nd < 1 %", r["gray"] < 1.0, f"{r['gray']:.3f} %")
    check_true("Heaviside ft=3 is less gray than ft=1", r["gray"] < _top88(1)["gray"])


def test_oc_volume_and_compliance_history():
    for ft in (1, 2):
        r = _top88(ft)
        # The OC bisection stops at (l2 − l1)/(l1 + l2) ≤ 1e-3; the last lmid is one end of the interval
        # → |Δλ|/λ ≲ 2e-3. For elements not at a bound x ∝ λ^(−1/2) → |ΔV|/V ≲ 1e-3 → |ΔV| ≤ 0.5 · 1e-3 = 5e-4.
        check(f"ft={ft}: |V − V*| ≤ 5e-4 after every OC update (largest)", np.abs(r["volume_new"] - 0.5).max(),
              0.0, atol=5e-4, source="derivation: OC bisection tolerance 1e-3 (top88 line 71)")
        check(f"ft={ft}: initial design volume = V*", r["volume"][0], 0.5, rtol=1e-15)
        u = r["compliance"]
        increment = np.diff(u[10:]) / u[11:]
        # OC is heuristic and not guaranteed monotone: small increases occur after iteration 10
        # (ft=1: largest relative 8e-4, ft=2: 5e-5 — volume oscillation of ±2e-4 and the move limit).
        check_true(f"ft={ft}: c is NOT monotone after iteration 10 but every increase is < 1e-3 relative",
                   increment.max() < 1e-3,
                   f"number of increases {int(np.sum(increment > 0))}, largest {increment.max():.1e}")
        check_true(f"ft={ft}: final compliance below half of the initial compliance", u[-1] < 0.5 * u[0],
                   f"{u[0]:.1f} → {u[-1]:.2f}")


# ---------------- passive elements ----------------
def test_passive_elements():
    pr = T.l_bracket(30)
    r = T.topopt(pr, 0.4, 1.5, ft=2, max_iter=60)
    xf = pr.grid.vector(r["xfiz"])
    check_true("L-bracket: passive void elements x̄ = 0 (exact)", np.all(xf[pr.passive == 1] == 0.0),
               int(np.sum(pr.passive == 1)))
    check_true("L-bracket: design variable of passive elements x = 0",
               np.all(pr.grid.vector(r["x"])[pr.passive == 1] == 0.0))
    check("L-bracket: passive area = n² − (n − 12)² (ratio 0.4, n = 30 → 18×18)", int(np.sum(pr.passive == 1)), 18 * 18)
    check("L-bracket: final volume V*", r["volume_new"][-1], 0.4, atol=5e-4, source="OC tolerance (derivation above)")
    # passive solid region: in the MBB the upper-right 4×4 block stays at x̄ = 1
    grid = T.Grid2D(30, 10)
    passive = np.zeros(grid.shape, dtype=int)
    passive[:4, -4:] = 2
    passive[5:8, 10:14] = 1
    prm = T.mbb_half(30, 10, passive=passive)
    for ft in (1, 2, 3):
        r = T.topopt(prm, 0.5, 1.5, ft=ft, max_iter=40)
        check_true(f"MBB ft={ft}: passive solid x̄ = 1 and passive void x̄ = 0 (exact)",
                   np.all(r["xfiz"][passive == 2] == 1.0) and np.all(r["xfiz"][passive == 1] == 0.0))
    r = T.topopt(prm, 0.5, 1.5, ft=2, optimizer="MMA", max_iter=40)
    check_true("MBB MMA: passive elements fixed",
               np.all(r["xfiz"][passive == 2] == 1.0) and np.all(r["xfiz"][passive == 1] == 0.0))


# ---------------- multiple loads ----------------
def test_multiple_load():
    pr = T.cantilever_two_load(20, 20)
    grid = pr.grid
    rng = np.random.default_rng(5)
    xf = rng.uniform(0.1, 1, grid.nel)
    c = pr.analysis(xf)[0]
    p1 = T.Problem(grid, pr.F[:, 0], pr.fixed)
    p2 = T.Problem(grid, pr.F[:, 1], pr.fixed)
    check("two load cases: c = c₁ + c₂", c, p1.analysis(xf)[0] + p2.analysis(xf)[0], rtol=1e-12,
          source=SOURCE88 + " Eq. (20)")
    r = T.topopt(pr, 0.4, 2.0, ft=1, max_iter=300)
    check_true("cantilever with two loads (top88 §5.2, 20×20): converged", r["converged"], r["iteration"])
    xs = r["xfiz"]
    # loads of opposite sign in y at the top/bottom corners: the optimum must be symmetric about the horizontal axis
    check("two loads: design top-bottom symmetric (largest difference)", np.abs(xs - xs[::-1, :]).max(), 0.0, atol=1e-6,
          source="derivation: the problem is mirror symmetric about the horizontal axis")


# ---------------- MMA ----------------
def _beam2(x):
    a = np.array([61.0, 37.0, 19.0, 7.0, 1.0])
    return 0.0624 * x.sum(), 0.0624 * np.ones(5), float((a / x ** 3).sum() - 1), -3 * a / x ** 4


def test_mma_svanberg_beam():
    # Deetman mma_beam2.log, outvector2 (4 decimals): designs of iterations 1–6 and outvector1 objective values
    log_x = [[5.6966, 5.1410, 4.3965, 3.3533, 1.8596], [5.8375, 5.1815, 4.3913, 3.4435, 2.4100],
             [6.0071, 5.3200, 4.5236, 3.5002, 2.0608], [6.0132, 5.3033, 4.4970, 3.4995, 2.1555],
             [6.0163, 5.3080, 4.4953, 3.5008, 2.1534], [6.0160, 5.3087, 4.4947, 3.5012, 2.1530]]
    log_f = [1.2759, 1.3269, 1.3361, 1.3396, 1.3400, 1.3400]
    x = 5 * np.ones(5)
    x1 = x.copy()
    x2 = x.copy()
    low = upp = None
    xmin, xmax = np.ones(5), 10 * np.ones(5)
    source = "Deetman, GCMMA-MMA-Python examples/mma_beam2.log (Svanberg 1987 beam problem)"
    for k in range(1, 12):
        f0, df0, g, dg = _beam2(x)
        low, upp = T.mma_asymptote(k, x, x1, x2, low, upp, xmin, xmax)
        xn, lam, y = T.mma_subproblem(x, xmin, xmax, low, upp, df0, g, dg, move=1.0)
        x2, x1, x = x1, x.copy(), xn
        if k <= 6:
            # log has 4 decimals → ±5e-5 rounding; the reference interior-point solver stops at epsimin = 1e-7 → 6e-5
            check(f"MMA iteration {k}: x = log (largest difference)", np.abs(x - log_x[k - 1]).max(), 0.0, atol=6e-5,
                  source=source)
            check(f"MMA iteration {k}: objective = log", _beam2(x)[0], log_f[k - 1], atol=6e-5, source=source)
    # analytic optimum: KKT c = 3λ aⱼ/xⱼ⁴, constraint active → xⱼ = (3λaⱼ/c)^(1/4)
    a, c = np.array([61.0, 37.0, 19.0, 7.0, 1.0]), 0.0624
    lam = ((c / 3) ** 0.75 * np.sum(a ** 0.25)) ** (4 / 3)
    xs = (3 * lam * a / c) ** 0.25
    check("MMA after 11 iterations: x = analytic KKT optimum (largest relative difference)", np.abs(x / xs - 1).max(),
          0.0, atol=1e-5, source="derivation: Lagrange conditions")
    check("MMA: f* = 0.0624 Σ x* (analytic 1.33996)", _beam2(x)[0], c * xs.sum(), rtol=1e-7)


def test_mma_subproblem_independent():
    """Dual bisection solution = SLSQP solution of the same convex subproblem (independent solver)."""
    rng = np.random.default_rng(11)
    n = 6
    for trial in range(3):
        x = rng.uniform(0.3, 0.7, n)
        low, upp = x - 0.5, x + 0.5
        df0 = -rng.uniform(0.5, 2.0, n) * (1 if trial else rng.choice([-1, 1], n))
        dg = rng.uniform(0.5, 1.5, n) / n
        g = 0.05
        xmma, lamd, y = T.mma_subproblem(x, np.zeros(n), np.ones(n), low, upp, df0, g, dg, move=0.3)
        # rebuild the subproblem in the test (formulas: Svanberg 1987 + Python counterpart of the 2007 code)
        alpha = np.maximum(np.maximum(low + 0.1 * (x - low), x - 0.3), 0)
        beta = np.minimum(np.minimum(upp - 0.1 * (upp - x), x + 0.3), 1)

        def pq(d):
            p, q = np.maximum(d, 0), np.maximum(-d, 0)
            e = 0.001 * (p + q) + 1e-5
            return (p + e) * (upp - x) ** 2, (q + e) * (x - low) ** 2
        p0, q0 = pq(df0)
        p1, q1 = pq(dg)
        b = np.sum(p1 / (upp - x) + q1 / (x - low)) - g
        f = lambda z: np.sum(p0 / (upp - z) + q0 / (z - low))
        gt = lambda z: b - np.sum(p1 / (upp - z) + q1 / (z - low))
        s = minimize(f, x, method="SLSQP", bounds=list(zip(alpha, beta, strict=True)),
                     constraints=[{"type": "ineq", "fun": gt}], options={"ftol": 1e-14, "maxiter": 500})
        check(f"MMA subproblem {trial + 1}: dual solution = SLSQP (largest difference)", np.abs(xmma - s.x).max(), 0.0,
              atol=1e-6, source="scipy.optimize.minimize SLSQP, ftol 1e-14 (SLSQP accuracy ~1e-7)")
        check_true(f"MMA subproblem {trial + 1}: y = 0 (artificial variable inactive)", y == 0.0)


def test_mma_topology():
    r = T.topopt(T.mbb_half(60, 20), 0.5, 2.4, ft=2, optimizer="MMA", move=0.2)
    oc = _top88(2)
    check_true("MMA (ft=2) MBB 60×20: converged", r["converged"], r["iteration"])
    # different optimizers may reach different local optima; ±1 % is expected for the same topology (observed −0.1 %)
    check("MMA (ft=2) MBB 60×20: compliance within ±1 % of the OC result", r["compliance"][-1], oc["compliance"][-1],
          rtol=1e-2, source="this module's OC result (233.71, matched top88 Fig. 3)")
    # MMA is not feasible at every iteration; at convergence the constraint is active and change ≤ 0.01
    # → |ΔV| ≪ 1e-4 (observed 6e-8)
    check("MMA: final volume = V* (±1e-4)", r["volume_new"][-1], 0.5, atol=1e-4)
    check_true("MMA: volume constraint violation < 1e-3 in the last 10 iterations",
               np.all(r["volume"][-10:] - 0.5 < 1e-3))


# ---------------- post-processing ----------------
def test_gray_and_thresholding():
    check("M_nd(0/1 field) = 0", T.gray_measure(np.array([0.0, 1.0, 1.0, 0.0])), 0.0, atol=1e-15)
    check("M_nd(0.5 field) = 100 %", T.gray_measure(np.full(10, 0.5)), 100.0, rtol=1e-15)
    check("M_nd([0.25, 1]) = (0.75 + 0)/2 × 100", T.gray_measure(np.array([0.25, 1.0])), 37.5, rtol=1e-15)
    a = np.array([[0.1, 0.6, 0.9], [0.5, 0.7, 0.2]])
    s = T.binarize(a, 0.5)
    check("threshold 0.5: number of solid elements (0.5 does not count as solid)", s["area"], 3)
    check("threshold 0.5: ratio", s["ratio"], 0.5)
    s = T.binarize(a, keep_volume=True)
    check("volume-preserving threshold: solid count = round(mean·n) = 3", s["area"], round(a.mean() * 6))
    check("volume-preserving threshold: threshold value = 3rd densest", s["threshold"], 0.6)
    r = _top88(1)
    pr = T.mbb_half(60, 20)
    s = T.binarize(r["xfiz"], keep_volume=True, problem=pr)
    check("MBB ft=1 thresholded: volume ratio 0.5 (±1/1200)", s["ratio"], 0.5, atol=1 / 1200)
    check_true("MBB ft=1 thresholded structure: compliance finite and of the same order as the gray design (0.7–1.3×)",
               0.7 * r["compliance_final"] < s["compliance"] < 1.3 * r["compliance_final"],
               f"{s['compliance']:.2f} / {r['compliance_final']:.2f}")


# ---------------- 3-D ----------------
def test_3d_cantilever():
    pr = T.cantilever_3d(12, 4, 3)
    r = T.topopt(pr, 0.3, 1.5, ft=2, max_iter=60)
    check("3-D cantilever 12×4×3: |V − V*| ≤ 5e-4 after every update", np.abs(r["volume_new"] - 0.3).max(), 0.0,
          atol=5e-4, source="OC tolerance (same derivation as 2-D)")
    check_true("3-D cantilever: final compliance below the initial compliance", r["compliance"][-1] < r["compliance"][0],
               f"{r['compliance'][0]:.1f} → {r['compliance'][-1]:.1f}")
    check_true("3-D cantilever: density array (nelx, nely, nelz)", r["xfiz"].shape == (12, 4, 3))
    c1 = pr.analysis(np.ones(pr.grid.nel))[0]
    check("3-D uniform x = 0.5: c = c_solid/E(0.5)", pr.analysis(np.full(pr.grid.nel, 0.5))[0],
          c1 / (pr.Emin + 0.125 * (1 - pr.Emin)), rtol=1e-10)


# ---------------- invalid input ----------------
def test_faulty_input():
    pr = T.mbb_half(6, 3)
    expect_error("ft = 4 rejected", T.topopt, pr, 0.5, 1.5, ft=4, error=ValueError)
    expect_error("volume = 0 rejected", T.topopt, pr, 0.0, 1.5, error=ValueError)
    expect_error("optimizer 'SQP' rejected", T.topopt, pr, 0.5, 1.5, optimizer="SQP", error=ValueError)
    expect_error("rmin = 0 rejected", T.topopt, pr, 0.5, 0.0, error=ValueError)
    expect_error("nelx = 0 rejected", T.Grid2D, 0, 3, error=ValueError)
    expect_error("F with wrong size rejected", T.Problem, pr.grid, np.zeros(5), [0], error=ValueError)
    expect_error("problem without supports rejected", T.Problem, pr.grid, {1: -1.0}, [], error=ValueError)
    expect_error("passive = 3 rejected", T.mbb_half, 6, 3, passive=np.full((3, 6), 3), error=ValueError)
    expect_error("full MBB with odd nelx rejected", T.mbb_full, 7, 3, error=ValueError)
    expect_error("ν = 0.5 rejected", T.ke_q4, 0.5, error=ValueError)


def test_h8_grid_cantilever_converges_to_timoshenko():
    """Solid 3-D grid cantilever (L/d = 5, root fully clamped, uniform tip shear) against Timoshenko beam theory
    δ = PL³/(3EI) + PL/(κGA), κ = 5/6. Trilinear H8 elements are too stiff in bending when few elements span the
    depth; this is the correction to apply to coarse voxel previews (docs/12 §4, GE preview). Ratios measured on
    2026-11-03: 1 element 0.636, 2 → 0.856, 4 → 0.947, 8 → 0.975."""
    E, nu, P = 1.0, 0.3, 1.0
    ratios = []
    for n in (2, 4, 8):
        nx, ny, nz = 5 * n, n, n
        g = T.Grid3D(nx, ny, nz, nu)
        fixed = [g.dof(0, iy, iz, k) for iy in range(ny + 1) for iz in range(nz + 1) for k in range(3)]
        F = {}
        for iy in range(ny + 1):
            for iz in range(nz + 1):
                w = (0.5 if iy in (0, ny) else 1.0) * (0.5 if iz in (0, nz) else 1.0)
                F[g.dof(nx, iy, iz, 1)] = -P * w / (ny * nz)
        pr = T.Problem(g, F, fixed, E0=E, Emin=1e-9)
        _, _, U = pr.analysis(np.ones(g.nel))
        tip = -np.mean([U[g.dof(nx, iy, iz, 1), 0] for iy in range(ny + 1) for iz in range(nz + 1)])
        Ib, G, A = nz * ny ** 3 / 12, E / (2 * (1 + nu)), nz * ny
        ratios.append(tip / (P * nx ** 3 / (3 * E * Ib) + P * nx / (5 / 6 * G * A)))
    check("H8, 2 elements through the depth: FE/Timoshenko", ratios[0], 0.856, atol=0.005,
          source="regression, 2026-11-03")
    check("H8, 8 elements through the depth: FE/Timoshenko within 3 %", ratios[2], 1.0, atol=0.03,
          source="Timoshenko beam theory; the clamped root makes the FE slightly stiffer")
    check_true(f"monotone convergence {np.round(ratios, 3)}", ratios[0] < ratios[1] < ratios[2])
