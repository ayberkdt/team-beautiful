"""Geometrically non-linear truss analysis (total Lagrangian, Green-Lagrange strain).

Benchmarks: the two-bar shallow (von Mises) truss, whose total-Lagrangian equilibrium path is
known in closed form (derived in :func:`_von_mises_load`; cf. the shallow-truss example of Crisfield 1991, Vol. 1, and
Bažant & Cedolin 1991 for the snap-through problem), a spring-loaded variant that snaps back, a
single bar under large stretch, and the small-load limit, which must equal the linear solution.
"""
import math

import numpy as np

from aerokit.fem import Model
from aerokit.fem import nonlinear as nl
from aerokit.fem.elements.discrete import Spring
from aerokit.fem.elements.line import Bar
from aerokit.verification import check, check_true, expect_error

A_HALF, H, E, AREA = 1.0, 0.1, 1.0e9, 1.0e-3            # half span, rise [m]; EA = 1e6 N
EA = E * AREA
L0 = math.hypot(A_HALF, H)
P_MAX = 2 * EA * H ** 3 / (3 * math.sqrt(3) * L0 ** 3)
W_CRIT = H * (1 - 1 / math.sqrt(3))


def _von_mises_load(w):
    """Closed-form equilibrium path ``P(w)`` of the two-bar (von Mises) truss.

    Supports at ``(±a, 0)``, apex at ``(0, h)``, vertical load ``P`` (downwards) at the apex and
    apex deflection ``w`` (downwards); by symmetry the apex does not move sideways. Each bar has
    ``L₀² = a² + h²`` and, deformed, axis vector ``d = (∓a, h − w)``, so the Green-Lagrange strain is
    ``E = (|d|² − L₀²)/(2L₀²) = (w² − 2hw)/(2L₀²)``. The bar force on the apex is
    ``f = (EA E/L₀) d``; vertical equilibrium of the two bars with the load gives
    ``2 (EA E/L₀)(h − w) = −P``, i.e. ::

        P(w) = (EA / L₀³) · w (h − w)(2h − w)

    (exact for St. Venant-Kirchhoff bars, no shallowness assumption). ``P`` vanishes at
    ``w = 0, h, 2h`` and is antisymmetric about ``w = h``; ``dP/dw = (EA/L₀³)(2h² − 6hw + 3w²)``
    vanishes at the limit point ``w_c = h(1 − 1/√3)``, where ``P_max = 2EA h³/(3√3 L₀³)``.
    """
    return EA / L0 ** 3 * w * (H - w) * (2 * H - w)


def _von_mises(spring=None, load=P_MAX):
    X = [[-A_HALF, 0.0], [A_HALF, 0.0], [0.0, H]] + ([[0.0, H + 0.1]] if spring else [])
    m = Model(X, 2)
    m.add(Bar(0, 2, E, AREA))
    m.add(Bar(1, 2, E, AREA))
    m.fix(0, [0, 1])
    m.fix(1, [0, 1])
    if spring:
        m.add(Spring(2, 3, spring, ndof=2, dof=1))
        m.fix(3, [0])
        m.load(3, 1, -load)
    else:
        m.load(2, 1, -load)
    return m


def test_von_mises_truss_arc_length_path():
    r = nl.arc_length(_von_mises(), 0.004, max_steps=200, adaptive=False, dof=5, u_limit=2.3 * H)
    w, lam = -r.u[5], r.load_factor
    P = lam * P_MAX
    check_true("arc length traced the whole path to w > 2.3h", r.converged and w[-1] >= 2.3 * H, w[-1] / H,
               source="Crisfield 1981: arc length passes limit points")
    check("von Mises truss: max |λP_ref − P(w)| / P_max over all converged points",
          np.max(np.abs(P - _von_mises_load(w))) / P_MAX, 0.0, atol=1e-7,
          source="derivation in _von_mises_load (Crisfield 1991 Vol. 1; Bažant & Cedolin 1991)")
    check("von Mises truss: apex stays on the symmetry axis", np.max(np.abs(r.u[4])), 0.0, atol=1e-12,
          source="symmetry")
    check_true("arc length: the deflection increases monotonically through the snap-through",
               np.all(np.diff(w) > 0), source="Crisfield 1981 root selection (no doubling back)")
    # limit point (first maximum, w < h): the cubic through the four points around it locates it
    k = int(np.argmax(np.where(w < H, lam, -np.inf)))
    sl = slice(k - 2, k + 2) if lam[k + 1] > lam[k - 1] else slice(k - 1, k + 3)
    c = np.polyfit(w[sl], P[sl], 3)
    roots = np.roots(np.polyder(c))
    wc = float(np.real(roots[np.argmin(np.abs(roots - W_CRIT))]))
    check("limit point deflection w_c = h(1 − 1/√3)", wc, W_CRIT, rtol=1e-6,
          source="derivation: dP/dw = 0 (Bažant & Cedolin 1991)")
    check("limit load P_max = 2EA h³/(3√3 L₀³)", np.polyval(c, wc), P_MAX, rtol=1e-8,
          source="derivation: P(w_c)")
    check_true("no converged point before the re-stiffening branch (w ≤ 2h) exceeds the limit load",
               lam[w <= 2 * H].max() <= 1 + 1e-9, lam[w <= 2 * H].max(), source="derivation")
    check("snap-through: minimum load = −P_max (antisymmetry about w = h)", lam.min(), -1.0, rtol=2e-3,
          source="derivation: P(2h − w) = −P(w)")
    ih = int(np.argmin(np.abs(w - H)))
    check_true("load factor changes sign at w = h and w = 2h", lam[ih - 1] > 0 > lam[ih + 1] and lam[-1] > 0,
               (lam[ih - 1], lam[ih + 1], lam[-1]), source="derivation: P(h) = P(2h) = 0")
    check_true("arc-length steps converge in few iterations", r.iterations.max() <= 6, r.iterations.max(),
               source="Crisfield 1981: quadratic convergence of the corrector")
    ra = nl.arc_length(_von_mises(), 0.004, max_steps=200, dof=5, u_limit=2.3 * H)
    check("adaptive arc length: same path", np.max(np.abs(ra.load_factor * P_MAX - _von_mises_load(-ra.u[5]))) / P_MAX,
          0.0, atol=1e-7, source="derivation in _von_mises_load")


def test_spring_loaded_truss_snap_back():
    # a soft spring between the load and the apex: v = w + P/k_s, dv/dw < 0 where P' < −k_s (snap-back)
    ks = 0.3 * EA * H ** 2 / L0 ** 3
    r = nl.arc_length(_von_mises(spring=ks), 0.004, max_steps=400, adaptive=False, dof=7, u_limit=2.5 * H)
    w, v, lam = -r.u[5], -r.u[7], r.load_factor
    check("snap-back: truss equilibrium P(w) along the path", np.max(np.abs(lam * P_MAX - _von_mises_load(w))) / P_MAX,
          0.0, atol=1e-7, source="derivation in _von_mises_load")
    check("snap-back: spring compatibility v = w + P/k_s", np.max(np.abs(v - (w + lam * P_MAX / ks))) / H, 0.0,
          atol=1e-10, source="derivation: series spring")
    check_true("snap-back traced: the loaded-point displacement decreases on part of the path",
               np.any(np.diff(v) < 0) and v[-1] >= 2.5 * H, (v.min(), v.max()),
               source="Crisfield 1981 / Riks 1979: arc length follows snap-back")


def test_single_bar_large_stretch():
    L, ea = 2.0, 1.0e5
    for stretch in (1.5, 0.8):
        m = Model([[0.0, 0.0], [L, 0.0]], 2)
        m.add(Bar(0, 1, ea, 1.0))
        m.fix(0, [0, 1])
        m.fix(1, [1])
        P = ea * (stretch ** 2 - 1) / 2 * stretch
        m.load(1, 0, P)
        r = nl.newton_raphson(m, 10)
        check(f"single bar, stretch {stretch}: u = (λs − 1) L", r.u[2, -1], (stretch - 1) * L, rtol=1e-10,
              source="closed form: P = EA·(λs² − 1)/2·λs (Green strain, St. Venant-Kirchhoff)")
        check(f"single bar, stretch {stretch}: true axial force = P", nl.axial_forces(m, r.u[:, -1])[0], P, rtol=1e-10,
              source="closed form: N = EA E ℓ/L₀")
        check(f"single bar, stretch {stretch}: strain energy ½EA L₀ E²", nl.strain_energy(m, r.u[:, -1]),
              0.5 * ea * L * ((stretch ** 2 - 1) / 2) ** 2, rtol=1e-10, source="definition")
        check_true("Newton converges quadratically (≤ 6 iterations per step)", r.iterations.max() <= 6,
                   r.iterations, source="full Newton with consistent tangent")


def test_small_load_limit_equals_linear_static():
    # asymmetric three-bar truss, loads in x and y
    X = [[0.0, 0.0], [2.0, 0.0], [4.0, 0.5], [1.5, 1.8]]
    m = Model(X, 2)
    for i, ea in ((0, 2e8), (1, 1e8), (2, 3e8)):
        m.add(Bar(i, 3, ea, 1.0))
        m.fix(i, [0, 1])
    m.load(3, 0, 30.0)
    m.load(3, 1, -50.0)
    lin = m.static().u
    r = nl.newton_raphson(m, 1)
    check("small load: non-linear = linear static (Model.static)", np.max(np.abs(r.u[:, -1] - lin)) / np.max(np.abs(lin)),
          0.0, atol=1e-6, source="derivation: Green strain → small strain as u/L → 0")
    # consistent tangent: K_t(0) is the linear stiffness, and K_t(u) = ∂f_int/∂u (central differences)
    check("tangent at u = 0 equals the linear stiffness", abs(nl.tangent_stiffness(m, np.zeros(8)) - m.K()).max(), 0.0,
          atol=1e-6, source="derivation: E = 0 → no initial-stress term")
    rng = np.random.default_rng(1)
    u = rng.normal(scale=0.2, size=8)
    Kt = nl.tangent_stiffness(m, u).toarray()
    h = 1e-6
    J = np.column_stack([(nl.internal_force(m, u + h * e) - nl.internal_force(m, u - h * e)) / (2 * h)
                         for e in np.eye(8)])
    check("consistent tangent = finite-difference Jacobian of f_int (large u)", np.max(np.abs(Kt - J)) / np.max(np.abs(Kt)),
          0.0, atol=1e-7, source="derivation: K_t = ∂f_int/∂u")
    check("tangent is symmetric", np.max(np.abs(Kt - Kt.T)), 0.0, atol=1e-6, source="hyperelastic bar")
    # 3-D truss tangent as well
    m3 = Model([[0.0, 0, 0], [1.0, 0, 0], [0.0, 1, 0], [0.3, 0.3, 1.0]], 3)
    for i in range(3):
        m3.add(Bar(i, 3, 1e6, 1.0, 0.0, 3))           # (rho, 3-D) positional
    u3 = rng.normal(scale=0.2, size=12)
    K3 = nl.tangent_stiffness(m3, u3).toarray()
    J3 = np.column_stack([(nl.internal_force(m3, u3 + h * e) - nl.internal_force(m3, u3 - h * e)) / (2 * h)
                          for e in np.eye(12)])
    check("3-D truss: tangent = finite-difference Jacobian", np.max(np.abs(K3 - J3)) / np.max(np.abs(K3)), 0.0,
          atol=1e-7, source="derivation: K_t = ∂f_int/∂u")


def test_newton_fails_beyond_limit_point():
    m = _von_mises()
    try:
        nl.newton_raphson(m, [0.5, 0.9, 1.1])
    except nl.ConvergenceError as exc:
        err = exc
    else:
        err = None
    check_true("load control beyond the limit point raises ConvergenceError (a ValueError)",
               isinstance(err, nl.ConvergenceError) and isinstance(err, ValueError), source="documented behaviour")
    check("ConvergenceError keeps the last converged load factor", err.load_factor, 0.9, rtol=1e-15,
          source="documented behaviour")
    check_true("ConvergenceError.result holds the converged part of the path",
               np.allclose(err.result.load_factor, [0.0, 0.5, 0.9]) and not err.result.converged,
               err.result.load_factor, source="documented behaviour")
    w9 = -err.result.u[5, -1]
    check("last converged state lies on the analytical path (λ = 0.9)", _von_mises_load(w9), 0.9 * P_MAX, rtol=1e-8,
          source="derivation in _von_mises_load")
    # without the divergence check Newton may jump to the remote (inverted) branch w > 2h
    r = nl.newton_raphson(m, [0.5, 0.9, 1.1], divergence_check=False)
    wj = -r.u[5, -1]
    check_true("without divergence check: static jump to the inverted branch (w > 2h)", wj > 2 * H, wj / H,
               source="derivation: P(w) = 1.1 P_max has only the root beyond 2h")
    check("jumped state satisfies P(w) = 1.1 P_max", _von_mises_load(wj), 1.1 * P_MAX, rtol=1e-8,
          source="derivation in _von_mises_load")
    expect_error("Newton under load control past the limit point (fewer steps)", nl.newton_raphson, m, [0.6, 1.2],
                 error=nl.ConvergenceError)


def test_input_errors():
    m = _von_mises()
    m2 = _von_mises()
    m2.fix(2, [0], value=1e-3)
    expect_error("non-homogeneous constraint rejected", nl.newton_raphson, m2, 2, error=ValueError)
    m3 = Model([[0.0, 0.0], [1.0, 0.0]], 2)
    m3.add(Bar(0, 1, E, AREA))
    m3.fix(0, [0, 1])
    expect_error("zero reference load rejected", nl.newton_raphson, m3, 2, error=ValueError)
    expect_error("negative arc length rejected", nl.arc_length, m, -0.1, error=ValueError)
    from aerokit.fem.elements.line import Frame2D
    m4 = Model([[0.0, 0.0], [1.0, 0.0]], 3)
    m4.add(Frame2D(0, 1, E, AREA, 1e-6))
    m4.fix(0, [0, 1, 2])
    m4.load(1, 1, 1.0)
    expect_error("element without non-linear formulation rejected", nl.newton_raphson, m4, 2, error=ValueError)
