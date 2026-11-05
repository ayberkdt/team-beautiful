"""Cross-section sizing optimization: analytic sensitivities, FSD, OC, SLSQP, classical benchmarks.

References:
- Sensitivities: central finite differences (not an FEM-independent path, but independent of the
  derivatives), relative error < 1e-5.
- Assembly/responses: aerokit.fem.Model's own K, M, static, modal and buckling solvers.
- Closed forms: nodal equilibrium of a determinate truss (derived by hand), cantilever tip deflection
  PL³/(3EI), bar with a tip mass ω² = (EA/L)/(M0 + ρAL/2) (lumped mass), Euler P_cr = π²EI/L².
- Benchmarks: arXiv:1306.1454 (H-SAGA, Tables 1, 2, 10 — READ from the PDF in this repository),
  arXiv:2107.02205 (DIRECTGO App. B.2 — READ), Memphis CIVL 7117 homework 5b (25-bar node table — READ).
"""
import math
import warnings

import numpy as np
from scipy.optimize import minimize_scalar

from aerokit.verification import check, check_true, expect_error
from aerokit.fem import Model
from aerokit.fem.elements.line import Bar, Frame2D, Frame3D
from aerokit.optimization import sizing as bo

FD_TOL = 1e-5


# ---------------------------------------------------------------- helpers
def _fd(f, x, h=1e-5):
    """Central-difference Jacobian: f(x) vector (or scalar) → (m, n), relative step h·x.

    h = 1e-5 ≈ ε^(1/3) balances truncation (∝ h²) and round-off (∝ ε/h) error of central differences.
    h = 1e-6 gave 4e-6 round-off noise on the portal-frame eigenvalues (3e-8 at h = 1e-4: analytic correct).
    """
    x = np.asarray(x, dtype=float)
    f0 = np.atleast_1d(np.asarray(f(x), dtype=float)).ravel()
    J = np.zeros((f0.size, x.size))
    for i in range(x.size):
        d = h * x[i]
        xp, xm = x.copy(), x.copy()
        xp[i] += d
        xm[i] -= d
        J[:, i] = (np.atleast_1d(f(xp)).ravel() - np.atleast_1d(f(xm)).ravel()) / (2 * d)
    return J


def _fd_check(name, f, x, analytic, source="central difference, h = 1e-5·x"):
    """Row-scaled error max|J_an − J_fd| / max|J_fd| (absolute if the row is zero)."""
    Jf = _fd(f, x)
    Ja = np.atleast_2d(np.asarray(analytic, dtype=float)).reshape(Jf.shape)
    scale = np.maximum(np.abs(Jf).max(axis=1, keepdims=True), 1e-300)
    error = float((np.abs(Ja - Jf) / scale).max())
    return check_true(f"{name}: analytic derivative = central difference (relative error {error:.1e} < {FD_TOL:g})",
                      error < FD_TOL and np.all(np.isfinite(Ja)), f"error {error:.2e}", source=source)


def _ten_bar_random(seed=1, extra=True):
    pr0 = bo.ten_bar_truss(1)
    m = pr0.model
    extra_mass = {(d, y): 0.5 for d in range(4) for y in (0, 1)} if extra else None
    pr = bo.SizeProblem(m, lower=0.1, load_cases=[pr0.F[:, 0]], section=bo.filled_circle(), extra_mass=extra_mass)
    x = np.random.default_rng(seed).uniform(1.0, 30.0, pr.n)
    return pr, x


def _portal(section=None, extra=True):
    """Portal frame (SI): columns 3 m (2 elements), beam 4 m (2 elements); vertical + horizontal loads."""
    E, rho = 70e9, 2700.0
    X = [[0, 0], [0, 1.5], [0, 3], [2, 3], [4, 3], [4, 1.5], [4, 0]]
    m = Model(X, 3)
    for i in range(6):
        m.add(Frame2D(i, i + 1, E, 1.0, 1.0, rho=rho))
    m.fix(0, [0, 1, 2])
    m.fix(6, [0, 1, 2])
    F = bo.load_vector(m, [(2, 1, -4e4), (4, 1, -4e4), (2, 0, 3e3), (3, 1, -1e4)])
    m.F[:] = F
    extra_mass = {(3, 0): 50.0, (3, 1): 50.0} if extra else None
    pr = bo.SizeProblem(m, groups=[[0, 1], [2, 3], [4, 5]], lower=1e-5, load_cases=[F],
                        section=section or bo.thin_tube_ratio(10.0), extra_mass=extra_mass)
    return pr


def _determinate(E=70e9, rho=2700.0, E_cross=200e9, rho_cross=7850.0, P=1e5, a=1.0):
    """Determinate truss: the 10-bar truss without diagonals 8 and 10 (SI).

    Downward P at node 2 (index 1). Diagonals (7, 9) are steel, the other bars aluminium.
    """
    X = [[2 * a, a], [2 * a, 0], [a, a], [a, 0], [0, a], [0, 0]]
    link = [(5, 3), (3, 1), (6, 4), (4, 2), (3, 4), (1, 2), (5, 4), (3, 2)]   # original bars 1–7 and 9
    m = Model(X, 2)
    for k, (i, j) in enumerate(link):
        cross = k in (6, 7)
        m.add(Bar(i - 1, j - 1, E_cross if cross else E, 1e-4,
                  rho=rho_cross if cross else rho))
    m.fix(4, [0, 1])
    m.fix(5, [0, 1])
    m.load(1, 1, -P)
    s2 = math.sqrt(2)
    # Nodal equilibrium (by hand): node 2: N9 = √2P, N4 = −P; node 1 unloaded → N2 = N6 = 0;
    # node 3: N1 = P, N5 = −P; node 4: N7 = √2P, N3 = −2P.
    N = P * np.array([1, 0, -2, -1, -1, 0, s2, s2])
    L = a * np.array([1, 1, 1, 1, 1, 1, s2, s2])
    return m, N, L


# ---------------------------------------------------------------- section families
def test_section_families():
    a = 0.03
    k = bo.filled_square()
    check("solid square: I(A) = a⁴/12", k.I(a * a), a ** 4 / 12, rtol=1e-14, source="definition")
    check("solid square: W(A) = a³/6", k.W(a * a), a ** 3 / 6, rtol=1e-14, source="definition")
    d = 0.05
    c = bo.filled_circle()
    A_circ = math.pi * d * d / 4
    check("solid circle: I(A) = πd⁴/64", c.I(A_circ), math.pi * d ** 4 / 64, rtol=1e-14, source="definition")
    check("solid circle: W(A) = πd³/32", c.W(A_circ), math.pi * d ** 3 / 32, rtol=1e-14, source="definition")
    R, t = 0.05, 0.005
    Ab = 2 * math.pi * R * t
    b = bo.thin_tube_ratio(R / t)
    check("thin tube (fixed R/t): I = πR³t", b.I(Ab), math.pi * R ** 3 * t, rtol=1e-13, source="thin wall")
    check("thin tube (fixed R/t): W = πR²t", b.W(Ab), math.pi * R * R * t, rtol=1e-13, source="thin wall")
    b2 = bo.thin_tube_fixed_t(t)
    check("thin tube (fixed t): I = πR³t", b2.I(Ab), math.pi * R ** 3 * t, rtol=1e-13, source="thin wall")
    check("thin tube (fixed t): W = πR²t", b2.W(Ab), math.pi * R * R * t, rtol=1e-13, source="thin wall")
    h = 0.3
    ip = bo.i_profile_fixed_height(h)
    check("I-section: I = A h²/4 (two flanges at h/2)", ip.I(0.01), 0.01 * h * h / 4, rtol=1e-14)
    _fd_check("section family dI/dA (fixed-t tube, p = 3)", lambda x: b2.I(x[0]), np.array([Ab]), b2.dI(Ab))
    _fd_check("section family d(I/W)/dA (solid circle)", lambda x: c.I_W(x[0]), np.array([A_circ]), c.dI_W(A_circ))


# ---------------------------------------------------------------- consistency with the model
def test_responses_match_fem():
    pr, x = _ten_bar_random(extra=False)
    pr.apply(x)
    m = pr.model
    check("truss: sizing K = Model.K()", abs(pr.K(x) - m.K()).max(), 0.0, atol=1e-9 * abs(m.K()).max())
    check("truss: sizing M = Model.M()", abs(pr.M(x) - m.M()).max(), 0.0, atol=1e-12 * abs(m.M()).max())
    u = m.static()["u"]
    check("truss: tip displacement = Model.static()", pr.displacement(x, [3])[0], u[3], rtol=1e-10)
    sig = np.array([s["sigma"] for s in m.element_results(u)])
    check("truss: stresses = Model.element_results()", np.abs(pr.stresses(x)[0] - sig).max(), 0.0,
          atol=1e-10 * np.abs(sig).max())
    check("truss: compliance = 2 × Model.static() energy", pr.compliance(x), 2 * m.static()["energy"], rtol=1e-10)
    check("truss: f1 = Model.modal()", pr.frequencies(x, 1)["f"][0], m.modal(1)["f"][0], rtol=1e-10)

    pr = _portal(extra=False)
    x = np.array([2e-3, 3e-3, 1.5e-3])
    pr.apply(x)
    m = pr.model
    u = m.static()["u"]
    ss = m.element_results(u)
    S = pr.stresses(x)[0]
    A = pr.areas(x)
    W = pr.section.W(A)
    expected = []
    for e, s in enumerate(ss):
        for M in (s["M1"], s["M2"]):
            expected += [s["N"] / A[e] + M / W[e], s["N"] / A[e] - M / W[e]]
    check("frame: fiber stress N/A ± M/W = Frame2D stress output", np.abs(S - expected).max(), 0.0,
          atol=1e-9 * np.abs(expected).max())
    check("frame: f1 = Model.modal()", pr.frequencies(x, 1)["f"][0], m.modal(1)["f"][0], rtol=1e-9)
    check("frame: system buckling λ = Model.buckling()", pr.buckling_factor(x), m.buckling(1)["lambda_"][0],
          rtol=1e-9)


# ---------------------------------------------------------------- sensitivities
def test_sensitivity_truss_2d():
    pr, x = _ten_bar_random(seed=3)
    _fd_check("10-bar: mass", pr.mass, x, pr.mass(x, True)[1])
    _fd_check("10-bar: volume", pr.volume, x, pr.volume(x, True)[1])
    _fd_check("10-bar: compliance", pr.compliance, x, pr.compliance(x, True)[1])
    for y in ("direct", "adjoint"):
        _fd_check(f"10-bar: stresses ({y})", lambda z: pr.stresses(z)[0], x,
                  pr.stresses(x, True, method=y)[1][0])
        dof = [0, 1, 3, 5, 7]
        _fd_check(f"10-bar: displacements ({y})", lambda z: pr.displacement(z, dof), x,
                  pr.displacement(x, dof, derivative=True, method=y)[1])
        _fd_check(f"10-bar: Euler ratio −σ/σ_cr ({y})", lambda z: pr.euler_ratio(z)[0], x,
                  pr.euler_ratio(x, derivative=True, method=y)[1][0])
    g_d = pr.stresses(x, True, method="direct")[1]
    pr._cache = None
    g_e = pr.stresses(x, True, method="adjoint")[1]
    check("10-bar: direct and adjoint methods give the same derivative", np.abs(g_d - g_e).max(), 0.0,
          atol=1e-10 * np.abs(g_d).max(), source="two solution paths of the same linear system")
    s = pr.frequencies(x, 3, derivative=True)
    _fd_check("10-bar: eigenvalues λ1..3 (with extra mass, consistent mass)",
              lambda z: pr.frequencies(z, 3)["lambda_"], x, s["dlambda"])
    lam, d = pr.buckling_factor(x, derivative=True)
    _fd_check("10-bar: system buckling factor", lambda z: pr.buckling_factor(z), x, d)


def test_sensitivity_truss_3d_and_constraints():
    pr0 = bo.twenty_five_bar_truss()
    pr = bo.SizeProblem(pr0.model, groups=bo.TWENTY_FIVE_GROUPS, lower=0.01, load_cases=pr0.F.T,
                        section=bo.thin_tube_ratio(20), extra_mass=np.full(pr0.model.n_dof, 0.01),
                        batch_mass=True)
    x = np.random.default_rng(7).uniform(0.3, 3.0, pr.n)
    _fd_check("25-bar: compliance (2 load cases)", pr.compliance, x, pr.compliance(x, True)[1])
    _fd_check("25-bar: stresses LC2", lambda z: pr.stresses(z)[1], x, pr.stresses(x, True)[1][1])
    _fd_check("25-bar: displacements LC1", lambda z: pr.displacement(z, range(18)), x,
              pr.displacement(x, range(18), derivative=True)[1])
    _fd_check("25-bar: λ1, λ2 (lumped mass)", lambda z: pr.frequencies(z, 2)["lambda_"], x,
              pr.frequencies(x, 2, derivative=True)["dlambda"])
    pr.stress_limit(40.0, compression=20.0).displacement_limit([(0, 1), (1, 2)], 0.35)
    pr.euler_buckling_limit(K=0.8).frequency_limit(5.0).compliance_limit(50.0)
    g, J = pr.constraints(x, derivative=True)
    _fd_check(f"25-bar: Jacobian of all constraints ({g.size} rows, 5 constraint types)", pr.constraints, x, J)
    check_true("number of constraint names equals number of constraints", len(pr.constraint_names) == g.size,
               f"{len(pr.constraint_names)} / {g.size}")


def test_sensitivity_frame():
    pr = _portal()
    x = np.array([2.2e-3, 3.1e-3, 1.7e-3])
    for y in ("direct", "adjoint"):
        pr._cache = None
        _fd_check(f"portal: fiber stresses N/A ± M/W ({y})", lambda z: pr.stresses(z)[0], x,
                  pr.stresses(x, True, method=y)[1][0])
    _fd_check("portal: displacement (horizontal top, rotation)", lambda z: pr.displacement(z, [6, 8, 10]), x,
              pr.displacement(x, [6, 8, 10], derivative=True)[1])
    _fd_check("portal: compliance", pr.compliance, x, pr.compliance(x, True)[1])
    _fd_check("portal: Euler ratio", lambda z: pr.euler_ratio(z)[0], x, pr.euler_ratio(x, derivative=True)[1][0])
    _fd_check("portal: λ1..2 (consistent + extra mass)", lambda z: pr.frequencies(z, 2)["lambda_"], x,
              pr.frequencies(x, 2, derivative=True)["dlambda"])
    _fd_check("portal: system buckling factor (design-dependent pre-load)", pr.buckling_factor, x,
              pr.buckling_factor(x, derivative=True)[1])
    pr2 = _portal(section=bo.thin_tube_fixed_t(4e-3))
    pr2.stress_limit(250e6).buckling_limit(3.0).frequency_limit(2.0).displacement_limit([(3, 1)], 0.01)
    _fd_check("portal (fixed-t tube, p = 3): Jacobian of all constraints", pr2.constraints, x,
              pr2.constraints(x, derivative=True)[1])


# ---------------------------------------------------------------- FSD
def test_fsd_determinate():
    sig = 150e6
    m, N, L = _determinate()
    pr = bo.SizeProblem(m, lower=1e-6)
    pr.apply(np.full(pr.n, 1e-4))
    Nfem = np.array([s["N"] for s in m.element_results(m.static()["u"])])
    check("determinate truss: FEM bar forces = hand nodal equilibrium", np.abs(Nfem - N).max(), 0.0,
          atol=1e-8 * np.abs(N).max(), source="derivation: nodal equilibrium (method of joints)")
    pr.stress_limit(sig)
    r = bo.fully_stressed_design(pr, x0=np.full(pr.n, 3e-4))
    expected = np.maximum(np.abs(N) / sig, 1e-6)
    check("FSD determinate: A = max(|N|/σ_allow, A_min) (largest relative difference)",
          np.max(np.abs(r.x - expected) / expected), 0.0, atol=1e-12,
          source="determinate: N independent of design → fully stressed design A = |N|/σ")
    check("FSD determinate: diagonal N9 A = √2·P/σ", r.x[7], math.sqrt(2) * 1e5 / sig, rtol=1e-12,
          source="derivation: equilibrium of node 2")
    check_true("FSD determinate: converges in 1 update + 1 verification step", r.successful and r.iteration <= 2,
               f"{r.iteration} iterations")
    S = pr.stresses(r.x)[0]
    loaded = np.abs(N) > 0
    check("FSD determinate: every loaded bar fully stressed |σ| = σ_allow", np.abs(np.abs(S[loaded]) / sig - 1).max(),
          0.0, atol=1e-10)
    check("FSD result: max violation 0", r.max_violation, 0.0, atol=1e-10)


def test_fsd_euler_single_bar():
    E, L, P = 70e9, 2.0, 5e4
    m = Model([[0.0, 0.0], [L, 0.0]], 2)
    m.add(Bar(0, 1, E, 1e-4, rho=2700.0))
    m.fix(0, [0, 1])
    m.fix(1, 1)
    m.load(1, 0, -P)
    pr = bo.SizeProblem(m, lower=1e-8, section=bo.filled_circle())
    pr.stress_limit(1e12).euler_buckling_limit()
    # π²E·A²/(4π)/L² = P → A = √(4 P L² /(π E))
    A_cr = math.sqrt(4 * P * L * L / (math.pi * E))
    r = bo.fully_stressed_design(pr, x0=[1e-4], euler_K=1.0)
    check("FSD + Euler (solid circular bar): A = √(4PL²/(πE))", r.x[0], A_cr, rtol=1e-10,
          source="derivation: P = π²EI/L², I = A²/(4π)")
    s = bo.slsqp(pr, x0=[1e-4])
    check("SLSQP + Euler constraint: same closed form", s.x[0], A_cr, rtol=1e-7,
          source="derivation: P = π²EI/L², I = A²/(4π)")


# ---------------------------------------------------------------- OC
def test_oc_determinate_closed_form():
    m, N, L = _determinate()
    P, dlt = 1e5, 4e-3
    pr = bo.SizeProblem(m, lower=1e-7)
    E, rho = pr.E, pr.rho
    # Derivation: δ = Σ N_i n_i L_i /(E_i A_i), n = N/P (unit load at the same point). Lagrangian:
    # ρ_i L_i − λ N_i n_i L_i /(E_i A_i²) = 0 → A_i = √(λ N_i n_i /(E_i ρ_i))   (L cancels!)
    # δ = δ* → √λ = Σ_j √(c_j ρ_j L_j) / δ*,  c_j = N_j n_j L_j / E_j.  W* = (Σ √(c ρ L))² / δ* + zero-force bars.
    n = N / P
    c = N * n * L / E
    loaded = c > 0
    S = np.sum(np.sqrt(c[loaded] * rho[loaded] * L[loaded]))
    A_exp = np.where(loaded, np.sqrt(np.where(loaded, c, 0) / (rho * L)) * S / dlt, 1e-7)
    W_exp = S ** 2 / dlt + np.sum(rho[~loaded] * L[~loaded] * 1e-7)
    r = bo.optimality_criterion(pr, constraint=(1, 1), limit=dlt, x0=np.full(pr.n, 1e-4))
    check("OC single displacement (determinate): A_i = √(N_i n_i/(E_i ρ_i))·S/δ* (largest relative difference)",
          np.max(np.abs(r.x[loaded] - A_exp[loaded]) / A_exp[loaded]), 0.0, atol=1e-9,
          source="derivation: Lagrangian stationarity, δ = Σ c_i/A_i (this file)")
    check("OC single displacement: W* = (Σ√(cρL))²/δ*", r.mass, W_exp, rtol=1e-9, source="derivation")
    check("OC: constraint active |u| = δ*", -pr.displacement(r.x, [m.dof(1, 1)])[0], dlt, rtol=1e-9)
    check_true("OC: zero-force bars at the lower bound", np.allclose(r.x[~loaded], 1e-7), f"{r.x[~loaded]}")
    ratio = A_exp[6] / A_exp[0]
    check("OC closed form: steel diagonal / aluminium chord ratio √(N7n7 E1ρ1/(N1n1 E7ρ7))", r.x[6] / r.x[0], ratio,
          rtol=1e-9, source="derivation: A ∝ √(N n/(Eρ)), independent of length")
    ru = bo.optimality_criterion(pr, constraint="compliance", limit=P * dlt, x0=np.full(pr.n, 1e-4))
    check("OC compliance constraint C* = P·δ*: same design (single load: C = P δ)", np.max(np.abs(ru.x - r.x) / r.x),
          0.0, atol=1e-8, source="derivation: C = Fᵀu = P·δ")
    check_true("OC history: constraint response at the limit in the last step", abs(r.history["R"][-1] / dlt - 1) < 1e-9,
               f"{r.history['R'][-1]:.6g}")


def test_oc_indeterminate_matches_slsqp():
    pr0 = bo.ten_bar_truss(1)
    pr = bo.SizeProblem(pr0.model, lower=0.1, load_cases=[pr0.F[:, 0]])
    C = 0.6 * pr.compliance(np.full(10, 10.0))
    r = bo.optimality_criterion(pr, constraint="compliance", limit=C, x0=np.full(10, 10.0))
    pr.compliance_limit(C)
    s = bo.slsqp(pr, x0=np.full(10, 10.0))
    check("10-bar compliance constraint: OC mass = SLSQP mass", r.mass, s.mass, rtol=1e-6,
          source="two independent methods, same convex problem (in reciprocal variables)")
    check_true("10-bar compliance constraint: OC converged and feasible", r.successful and r.max_violation < 1e-8,
               f"{r.iteration} it, violation {r.max_violation:.1e}")
    k = bo.kkt_audit(pr, r.x)
    check_true("10-bar compliance: KKT residual of the OC result < 1e-5", k["residual"] < 1e-5, f"{k['residual']:.1e}")


def test_cantilever_frame_closed_form():
    E, rho, Lt, P, dlt = 200e9, 7850.0, 2.0, 1e4, 5e-3
    n = 4
    m = Model([[Lt * i / n, 0.0] for i in range(n + 1)], 3)
    for i in range(n):
        m.add(Frame2D(i, i + 1, E, 1.0, 1.0, rho=rho))
    m.fix(0, [0, 1, 2])
    m.load(n, 1, -P)
    pr = bo.SizeProblem(m, groups=[list(range(n))], lower=1e-6, section=bo.filled_square())
    # δ = PL³/(3EI), I = A²/12 → A = √(4PL³/(Eδ*))
    A_exp = math.sqrt(4 * P * Lt ** 3 / (E * dlt))
    r = bo.optimality_criterion(pr, constraint=(n, 1), limit=dlt, x0=[1e-3])
    check("cantilever (solid square), OC: A = √(4PL³/(Eδ*))", r.x[0], A_exp, rtol=1e-9,
          source="Gere & Timoshenko: δ = PL³/(3EI); derivation")
    pr.displacement_limit([(n, 1)], dlt)
    s = bo.slsqp(pr, x0=[1e-3])
    check("cantilever (solid square), SLSQP: same closed form", s.x[0], A_exp, rtol=1e-7)
    check("cantilever: optimum mass ρ·A·L", s.mass, rho * A_exp * Lt, rtol=1e-7)


def test_frequency_constraint_closed_form():
    E, rho, L, M0, f_min = 70e9, 2700.0, 1.5, 200.0, 400.0
    m = Model([[0.0, 0.0], [L, 0.0]], 2)
    m.add(Bar(0, 1, E, 1e-4, rho=rho))
    m.fix(0, [0, 1])
    m.fix(1, 1)
    m.load(1, 0, 1.0)
    pr = bo.SizeProblem(m, lower=1e-8, extra_mass={(1, 0): M0}, batch_mass=True)
    w2 = (2 * math.pi * f_min) ** 2
    # ω² = (EA/L) / (M0 + ρAL/2) → A = ω² M0 / (E/L − ω² ρ L/2)
    A_exp = w2 * M0 / (E / L - w2 * rho * L / 2)
    check("bar with tip mass: ω² = (EA/L)/(M0 + ρAL/2)", pr.frequencies([A_exp])["f"][0], f_min, rtol=1e-12,
          source="derivation: single DOF, lumped mass")
    pr.frequency_limit(f_min)
    s = bo.slsqp(pr, x0=[1e-3])
    check("frequency-constrained minimum mass: A = ω²M0/(E/L − ω²ρL/2)", s.x[0], A_exp, rtol=1e-7,
          source="derivation")
    check_true("frequency constraint active", "frequency f1" in s.active_constraints, f"{s.active_constraints}")


# ---------------------------------------------------------------- benchmark problems
def test_three_bar_truss():
    pr = bo.three_bar_truss()
    lit = bo.LITERATURE["three_bar"]
    # FE ↔ closed form: σ1 = P(√2x1+x2)/(√2x1²+2x1x2), σ2(vertical) = P/(x1+√2x2), σ3 = −P x2/(√2x1²+2x1x2)
    x = np.array([0.6, 0.3])
    S = pr.stresses(x)[0]
    x1, x2, P = 0.6, 0.3, 2.0
    share = math.sqrt(2) * x1 ** 2 + 2 * x1 * x2
    check("three-bar: FE σ1 = P(√2x1+x2)/(√2x1²+2x1x2) (g1)", S[0], P * (math.sqrt(2) * x1 + x2) / share,
          rtol=1e-12, source=lit["source"])
    check("three-bar: FE σ2 = P/(x1+√2x2) (g3)", S[1], P / (x1 + math.sqrt(2) * x2), rtol=1e-12)
    check("three-bar: FE σ3 = −P·x2/(√2x1²+2x1x2) (g2)", S[2], -P * x2 / share, rtol=1e-12)
    r = bo.slsqp(pr, x0=[0.5, 0.5], objective="volume")
    check("three-bar: volume optimum 263.89584337", r.objective, lit["objective"], rtol=1e-9, source=lit["source"])
    # The literature x at this flat optimum differs between sources in the 7th digit (DIRECTGO 0.78867531,
    # surfaces library 0.7886751346); hence 1e-6 absolute for x.
    check("three-bar: x1* = 0.78867531", r.x[0], lit["x"][0], atol=1e-6, source=lit["source"])
    check("three-bar: x2* = 0.40824778", r.x[1], lit["x"][1], atol=1e-6, source=lit["source"])

    def f_g1(x1):                       # with g1 active, x2(x1) = √2·x1(1−x1)/(2x1−1)
        return 100 * (2 * math.sqrt(2) * x1 + math.sqrt(2) * x1 * (1 - x1) / (2 * x1 - 1))
    t = minimize_scalar(f_g1, bounds=(0.55, 0.99), method="bounded", options={"xatol": 1e-12})
    check("three-bar: equals the 1-D closed-form minimum along g1", r.objective, t.fun, rtol=1e-10,
          source="derivation: x2(x1) from g1 = 0")
    k = bo.kkt_audit(pr, r.x, objective="volume")
    check_true("three-bar: KKT residual < 1e-6", k["residual"] < 1e-6, f"{k['residual']:.1e}")
    check_true("three-bar: KKT multipliers ≥ 0 (unconstrained least squares)", k["mu_min"] > -1e-8, f"{k['mu_min']:.2e}")
    check("three-bar: complementary slackness max|μ g|", k["complementarity"], 0.0, atol=1e-8)
    check_true("three-bar: active constraint g1 (tension of symmetric bars 1/3 in the two load cases)",
               set(r.active_constraints) == {"stress tension e1 LC1", "stress tension e3 LC2"},
               f"{r.active_constraints}", source=lit["source"])


def _ten_bar_check(case, x0):
    pr = bo.ten_bar_truss(case)
    lit = bo.LITERATURE[f"ten_bar_{case}"]
    A_lit = np.array(lit["A"])
    # Weight of the literature areas in this model: verifies geometry/density/connectivity (optimizer-independent)
    check(f"10-bar case {case}: weight of the literature areas (within table rounding)",
          pr.mass(A_lit), lit["weight"], atol=0.01 if case == 1 else 0.5,
          source=lit["source"] + " — case 1: areas to 4 decimals, weight to 0.01 lb; case 2: areas to 2 decimals, "
                                 "±0.005 in² × Σρ_iL_i ≈ 430 lb/in² → at most ±2 lb, 0.5 lb chosen")
    check_true(f"10-bar case {case}: literature design feasible in this model (violation < 1e-3, rounding)",
               pr.max_violation(A_lit) < 1e-3, f"{pr.max_violation(A_lit):.1e}")
    r = bo.slsqp(pr, x0=x0)
    # The literature weight is rounded to 0.01 lb → |ΔW| ≤ 0.01 lb.
    check(f"10-bar case {case}: optimum weight {lit['weight']} lb", r.mass, lit["weight"], atol=0.01,
          source=lit["source"])
    # Areas: case 1 table has 4 decimals (±5e-5), case 2 table 2 decimals (±5e-3); some margin: 1e-4 / 6e-3.
    tol = 1e-4 if case == 1 else 6e-3
    check(f"10-bar case {case}: areas equal the literature (largest absolute difference, in²)",
          np.abs(r.x - A_lit).max(), 0.0, atol=tol, source=lit["source"])
    check(f"10-bar case {case}: all constraints satisfied at the optimum", r.max_violation, 0.0, atol=1e-8)
    check_true(f"10-bar case {case}: SLSQP successful, history consistent",
               r.successful and len(r.history["mass"]) >= 2 and abs(r.history["mass"][-1] - r.mass) < 1e-9
               and np.array_equal(r.history["x"][0], x0) and r.history["violation"][-1] == r.max_violation,
               f"{r.iteration} it, {len(r.history['mass'])} records")
    k = bo.kkt_audit(pr, r.x)
    check_true(f"10-bar case {case}: KKT residual < 1e-5", k["residual"] < 1e-5, f"{k['residual']:.1e}")
    check_true(f"10-bar case {case}: KKT multipliers ≥ 0", k["mu_min"] > -1e-8, f"{k['mu_min']:.2e}")
    check(f"10-bar case {case}: complementary slackness", k["complementarity"], 0.0, atol=1e-8)
    return r


def test_ten_bar_case1():
    r = _ten_bar_check(1, np.full(10, 10.0))
    check_true("10-bar case 1: the displacement (node 1 vertical) governs the design",
               "displacement n1.1 (−) LC1" in r.active_constraints, f"{r.active_constraints}")
    check_true("text summary produced", "Method: SLSQP" in r.summary() and "Active constraints" in r.summary())


def test_ten_bar_case2():
    _ten_bar_check(2, np.full(10, 10.0))


def test_twenty_five_bar():
    pr = bo.twenty_five_bar_truss()
    lit = bo.LITERATURE["twenty_five_bar"]
    A_lit = np.array(lit["A"])
    check("25-bar: weight of the literature areas = 545.16 lb (connectivity/geometry verification)",
          pr.mass(A_lit), lit["weight"], atol=0.01, source=lit["source"])
    check_true("25-bar: literature design feasible in this model (violation < 1e-4, rounding)",
               pr.max_violation(A_lit) < 1e-4, f"{pr.max_violation(A_lit):.1e}")
    r = bo.slsqp(pr, x0=np.full(8, 2.0))
    check("25-bar: optimum weight 545.16 lb (Lamberti), table rounded to 0.01 lb", r.mass, lit["weight"],
          atol=0.01, source=lit["source"])
    check("25-bar: within 0.1 lb of Schmit & Farshi 545.22 lb", r.mass, lit["other"]["Schmit & Farshi"],
          atol=0.1, source=lit["source"])
    check("25-bar: areas (largest absolute difference, table to 4 decimals)", np.abs(r.x - A_lit).max(), 0.0,
          atol=2e-4, source=lit["source"])
    check("25-bar: all constraints satisfied", r.max_violation, 0.0, atol=1e-8)
    k = bo.kkt_audit(pr, r.x)
    check_true("25-bar: KKT residual < 1e-5", k["residual"] < 1e-5, f"{k['residual']:.1e}")
    check_true("25-bar: KKT multipliers ≥ 0", k["mu_min"] > -1e-8, f"{k['mu_min']:.2e}")


def test_frame_slsqp_constraints():
    pr = _portal()
    pr.stress_limit(150e6).displacement_limit([(3, 1), (2, 0)], 0.01).euler_buckling_limit()
    pr.frequency_limit(3.0).buckling_limit(4.0)
    r = bo.slsqp(pr, x0=np.full(3, 5e-3))
    check_true("portal: SLSQP successful and all constraints satisfied (violation < 1e-8)",
               r.successful and r.max_violation < 1e-8, f"{r.message}, violation {r.max_violation:.1e}")
    check_true("portal: at least one constraint active", len(r.active_constraints) > 0, f"{r.active_constraints}")
    k = bo.kkt_audit(pr, r.x)
    check_true("portal: KKT residual < 1e-5", k["residual"] < 1e-5, f"{k['residual']:.1e}")
    check_true("portal: history recorded from start to end, violation < 1e-8 in the last record",
               r.history["violation"][-1] < 1e-8 and len(r.history["violation"]) >= 2
               and abs(r.history["mass"][-1] - r.mass) < 1e-12,
               f"{len(r.history['violation'])} records, first violation {r.history['violation'][0]:.2e}")


# ---------------------------------------------------------------- invalid input
def test_faulty_inputs():
    pr0 = bo.ten_bar_truss(1)
    m = pr0.model
    F = [pr0.F[:, 0]]
    E = ValueError
    expect_error("group missing an element", bo.SizeProblem, m, groups=[[0, 1]], load_cases=F, error=E)
    expect_error("element repeated in groups", bo.SizeProblem, m, groups=[list(range(10)), [3]], load_cases=F,
                 error=E)
    expect_error("lower bound ≤ 0", bo.SizeProblem, m, lower=0.0, load_cases=F, error=E)
    expect_error("upper < lower", bo.SizeProblem, m, lower=1.0, upper=0.5, load_cases=F, error=E)
    expect_error("zero load case", bo.SizeProblem, m, load_cases=[np.zeros(m.n_dof)], error=E)
    expect_error("load of wrong length", bo.SizeProblem, m, load_cases=[np.ones(3)], error=E)
    expect_error("design of wrong length", pr0.mass, np.ones(9), error=E)
    expect_error("negative design", pr0.compliance, -np.ones(10), error=E)
    expect_error("Euler constraint without a section family", pr0.euler_buckling_limit, error=E)
    expect_error("negative stress limit", pr0.stress_limit, -25.0, error=E)
    expect_error("displacement limit on a fixed DOF", pr0.displacement_limit, [(4, 0)], 1.0, error=E)
    expect_error("unknown objective", pr0.objective, np.ones(10), "cost", error=E)
    m3 = Model([[0, 0, 0], [1, 0, 0]], 6)
    m3.add(Frame3D(0, 1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, ref=(0, 1, 0)))
    m3.fix(0, range(6))
    m3.load(1, 1, 1.0)
    expect_error("Frame3D not supported", bo.SizeProblem, m3, error=E)
    mc = Model([[0, 0], [1, 0]], 3)
    mc.add(Frame2D(0, 1, 1.0, 1.0, 1.0))
    mc.fix(0, [0, 1, 2])
    mc.load(1, 1, 1.0)
    expect_error("frame without a section family", bo.SizeProblem, mc, error=E)
    mq = Model([[0, 0], [1, 0]], 3)
    mq.add(Frame2D(0, 1, 1.0, 1.0, 1.0, q=-1.0))
    mq.fix(0, [0, 1, 2])
    expect_error("distributed load q on a frame not supported", bo.SizeProblem, mq, section=bo.filled_square(),
                 error=E)
    mz = Model([[0, 0], [1, 0]], 2)
    mz.add(Bar(0, 1, 1.0, 1.0))
    mz.fix(0, [0, 1])
    mz.fix(1, 1, value=0.01)
    mz.load(1, 0, 1.0)
    expect_error("prescribed displacement not supported", bo.SizeProblem, mz, error=E)
    mm = Model([[0, 0], [1, 0], [2, 0]], 2)
    mm.add(Bar(0, 1, 1.0, 1.0))
    mm.add(Bar(1, 2, 1.0, 1.0))
    mm.fix(0, [0, 1])
    mm.fix(1, 1)
    mm.fix(2, 1)
    mm.load(2, 0, 1.0)
    prm = bo.SizeProblem(mm)
    expect_error("mass objective with rho = 0", prm.mass, np.ones(2), error=E)
    expect_error("frequency constraint on a massless model", prm.frequency_limit, 10.0, error=E)
    expect_error("OC without a limit", bo.optimality_criterion, prm, "compliance", None, error=E)
    expect_error("FSD without a stress limit", bo.fully_stressed_design, prm, error=E)
    mk = Model([[0, 0], [1, 0], [1, 1]], 2)
    mk.add(Bar(0, 1, 1.0, 1.0))
    mk.add(Bar(1, 2, 1.0, 1.0))
    mk.fix(0, [0, 1])
    mk.load(2, 0, 1.0)
    prk = bo.SizeProblem(mk)
    expect_error("mechanism: singular stiffness", prk.compliance, np.ones(2), error=E)
    expect_error("section family: p ≤ 0", bo.SectionFamily, 1.0, 0.0, error=E)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        expect_error("benchmark: invalid 10-bar case", bo.ten_bar_truss, 3, error=E)
