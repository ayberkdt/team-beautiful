"""Linear dynamics: Newmark/HHT, central difference, modal superposition, harmonic response.

Reference solutions are closed forms of the SDOF oscillator (Chopra 2012; Clough & Penzien 1993),
the Newmark (1959) and Hilber-Hughes-Taylor (1977) amplification properties, the Euler-Bernoulli
cantilever frequency and the Jury stability conditions of the central-difference recurrence.
"""
import math

import numpy as np
import scipy.linalg as sla
from scipy.optimize import minimize_scalar

from aerokit.fem import Model
from aerokit.fem import dynamics as dyn
from aerokit.fem.elements.discrete import Dashpot, PointMass, Spring
from aerokit.fem.elements.line import Frame2D
from aerokit.verification import check, check_true, expect_error

K_S, M_S = 4.0e4, 10.0                     # SDOF: ω = 63.25 rad/s, T = 0.0993 s
W_S = math.sqrt(K_S / M_S)
T_S = 2 * math.pi / W_S


def _sdof(c=0.0):
    md = Model([[0.0, 0.0]], ndof=1)
    md.add(Spring(0, None, K_S, ndof=1, dof=0))
    md.add(PointMass(0, M_S, ndof=1))
    if c:
        md.add(Dashpot(0, None, c, ndof=1, dof=0))
    return md


def _chain(n=3, k=1.0e4, m=2.0):
    """Fixed-free spring-mass chain 0 —k— 1 —k— … —k— n."""
    md = Model([[float(i), 0.0] for i in range(n + 1)], ndof=1)
    for i in range(n):
        md.add(Spring(i, i + 1, k, ndof=1, dof=0))
        md.add(PointMass(i + 1, m, ndof=1))
    md.fix(0, 0)
    return md


def _cantilever(n_el=8, L=1.0):
    E, b, h, rho = 70e9, 0.02, 0.01, 2700.0
    A, I = b * h, b * h ** 3 / 12
    md = Model([[L * i / n_el, 0.0] for i in range(n_el + 1)], ndof=3)
    for i in range(n_el):
        md.add(Frame2D(i, i + 1, E, A, I, rho=rho))
    md.fix(0, [0, 1, 2])
    f1 = 1.875104068711961 ** 2 / (2 * math.pi) * math.sqrt(E * I / (rho * A * L ** 4))
    return md, f1


# ---------------------------------------------------------------------------------------------- Newmark
def test_newmark_step_load_second_order():
    F = 100.0
    errs = []
    for n in (50, 100, 200):
        t = np.linspace(0.0, 2 * T_S, 2 * n + 1)
        r = dyn.newmark(_sdof(), t, load=np.array([F]))
        exact = F / K_S * (1 - np.cos(W_S * t))
        errs.append(np.max(np.abs(r.u[0] - exact)) / (F / K_S))
    p1, p2 = math.log2(errs[0] / errs[1]), math.log2(errs[1] / errs[2])
    check("Newmark avg. acceleration, step load: error at Δt = T/200 below 1e-3", errs[2], 0.0, atol=1e-3,
          source="Chopra 2012: u = (F/k)(1 − cos ωt)")
    check("Newmark avg. acceleration: observed order (T/50 → T/100) ≈ 2", p1, 2.0, rtol=0.02,
          source="Newmark 1959 / Hughes 2000: trapezoidal rule is second-order accurate")
    check("Newmark avg. acceleration: observed order (T/100 → T/200) ≈ 2", p2, 2.0, rtol=0.02,
          source="Newmark 1959 / Hughes 2000: trapezoidal rule is second-order accurate")
    r = dyn.newmark(_sdof(), np.linspace(0, T_S, 11), load=np.array([F]))
    check("Newmark: consistent initial acceleration a0 = F/m", r.a[0, 0], F / M_S, rtol=1e-12,
          source="derivation: M a0 = F0 − C v0 − K u0")


def test_newmark_energy_conservation_free_vibration():
    md, _ = _cantilever(n_el=6)
    md.load(6, 1, -50.0)
    u0 = md.static().u
    md.F[:] = 0.0
    t = np.linspace(0.0, 0.05, 1001)
    r = dyn.newmark(md, t, u0=u0, beta=0.25, gamma=0.5)
    E = r.energy[2]
    check("Newmark β=1/4, γ=1/2: total energy conserved in free vibration (cantilever)",
          np.max(np.abs(E - E[0])) / E[0], 0.0, atol=1e-10,
          source="Hughes 2000: trapezoidal rule conserves energy for linear undamped systems")
    check("free vibration starts with all energy as strain energy", r.energy[1, 0], E[0], rtol=1e-12,
          source="derivation: v0 = 0")


def _hht_amplification(Om, alpha):
    """Independent HHT amplification matrix for ü + ω²u = 0, state (u, Δt·v, Δt²·a), Δt = 1."""
    b, g, w2 = (1 - alpha) ** 2 / 4, (1 - 2 * alpha) / 2, Om ** 2
    L = np.array([[(1 + alpha) * w2, 0, 1], [1, 0, -b], [0, 1, -g]])
    R = np.array([[alpha * w2, 0, 0], [1, 1, 0.5 - b], [0, 1, 1 - g]])
    return np.linalg.solve(L, R)


def test_hht_alpha_dissipates_high_modes():
    # spectral radius at Ω → ∞ of the HHT amplification matrix: ρ∞ = (1 + α)/(1 − α)
    for alpha in (-0.1, -0.3):
        rho = np.max(np.abs(np.linalg.eigvals(_hht_amplification(1e6, alpha))))
        check(f"HHT α={alpha}: ρ∞ = (1+α)/(1−α)", rho, (1 + alpha) / (1 - alpha), rtol=1e-4,
              source="Hilber, Hughes & Taylor 1977")
    # the module reproduces the amplification-matrix recursion step by step
    alpha, Om = -0.3, 1000.0
    w = Om                                             # Δt = 1 s
    md = Model([[0.0, 0.0]], ndof=1)
    md.add(Spring(0, None, w * w, ndof=1, dof=0))
    md.add(PointMass(0, 1.0, ndof=1))
    r = dyn.newmark(md, np.arange(21.0), u0=np.array([1.0]), alpha=alpha)
    x, xs = np.array([1.0, 0.0, -w * w]), [1.0]
    Amp = _hht_amplification(Om, alpha)
    for _ in range(20):
        x = Amp @ x
        xs.append(x[0])
    check("HHT time history = independent amplification-matrix recursion", np.max(np.abs(r.u[0] - xs)), 0.0,
          atol=1e-12, source="Hilber, Hughes & Taylor 1977 (algorithm definition)")
    # two uncoupled oscillators: low (ωΔt = 0.05) and high (ωΔt = 100) frequency, both released from u = 1
    dt, wl, wh = 1e-3, 50.0, 1e5
    md = Model([[0.0, 0.0], [1.0, 0.0]], ndof=1)
    for node, wi in ((0, wl), (1, wh)):
        md.add(Spring(node, None, wi * wi, ndof=1, dof=0))
        md.add(PointMass(node, 1.0, ndof=1))
    t = np.arange(0, 126) * dt                          # ≈ one low-mode period (2π/50 = 0.1257 s)
    amp = {}
    for a in (0.0, -0.3):
        r = dyn.newmark(md, t, u0=np.array([1.0, 1.0]), alpha=a)
        el = 0.5 * r.v[0] ** 2 + 0.5 * wl ** 2 * r.u[0] ** 2          # modal energies (uncoupled DOFs)
        eh = 0.5 * r.v[1] ** 2 + 0.5 * wh ** 2 * r.u[1] ** 2
        check("energy history = sum of the two oscillator energies", np.max(np.abs(r.energy[2] - el - eh)) / eh[0],
              0.0, atol=1e-12, source="definition: ½vᵀMv + ½uᵀKu")
        amp[a] = (np.sqrt(el[-1] / el[0]), np.sqrt(eh[-1] / eh[0]))
    check("Newmark α=0: high mode not damped (amplitude ratio 1)", amp[0.0][1], 1.0, rtol=1e-9,
          source="Newmark 1959: average acceleration has no numerical dissipation")
    check_true("HHT α=−0.3: high mode amplitude decays below 1e-10 within 125 steps", amp[-0.3][1] < 1e-10,
               amp[-0.3][1], source="Hilber, Hughes & Taylor 1977: ρ(Ω=100) ≈ 0.55 per step")
    check("HHT α=−0.3: low mode (ωΔt = 0.05) loses < 0.5 % amplitude over one period", amp[-0.3][0], 1.0,
          rtol=5e-3, source="Hilber, Hughes & Taylor 1977: dissipation vanishes as ωΔt → 0")


def test_newmark_damped_sdof_matches_analytical():
    zeta, u0, v0 = 0.05, 0.01, 0.3
    c = 2 * zeta * math.sqrt(K_S * M_S)
    t = np.linspace(0.0, 3 * T_S, 3001)
    r = dyn.newmark(_sdof(c), t, u0=np.array([u0]), v0=np.array([v0]))
    wd = W_S * math.sqrt(1 - zeta ** 2)
    exact = np.exp(-zeta * W_S * t) * (u0 * np.cos(wd * t) + (v0 + zeta * W_S * u0) / wd * np.sin(wd * t))
    scale = math.hypot(u0, v0 / W_S)
    check("damped SDOF (dashpot), free vibration vs closed form: max error / amplitude",
          np.max(np.abs(r.u[0] - exact)) / scale, 0.0, atol=5e-5,
          source="Chopra 2012: underdamped free vibration")
    # the same damping as a Rayleigh pair (α_R = 2ζω, β_R = 0)
    r2 = dyn.newmark(_sdof(), t, u0=np.array([u0]), v0=np.array([v0]), damping=(2 * zeta * W_S, 0.0))
    check("Rayleigh α_R M = dashpot c: identical histories", np.max(np.abs(r2.u[0] - r.u[0])), 0.0, atol=1e-14,
          source="derivation: c = 2ζωm = α_R m")


def test_newmark_rejects_bad_input():
    md = _chain(2)
    t = np.linspace(0, 0.1, 11)
    md2 = _chain(2)
    md2.fix(2, 0, value=1e-3)
    expect_error("non-zero prescribed displacement rejected", dyn.newmark, md2, t, error=ValueError)
    expect_error("HHT alpha outside [−1/3, 0] rejected", dyn.newmark, md, t, alpha=-0.5, error=ValueError)
    expect_error("non-uniform time grid rejected", dyn.newmark, md, np.array([0.0, 0.1, 0.3]), error=ValueError)
    expect_error("load with wrong shape rejected", dyn.newmark, md, t, load=np.zeros((3, 5)), error=ValueError)
    expect_error("initial displacement violating a support rejected", dyn.newmark, md, t,
                 u0=np.array([1.0, 0.0, 0.0]), error=ValueError)


def test_newmark_with_mpc_equals_merged_model():
    # two masses tied by an MPC behave as one mass 2m on the spring
    k, m = 1.0e4, 1.5
    md = Model([[0.0, 0.0], [1.0, 0.0], [1.0, 0.0]], ndof=1)
    md.add(Spring(0, 1, k, ndof=1, dof=0))
    md.add(PointMass(1, m, ndof=1))
    md.add(PointMass(2, m, ndof=1))
    md.fix(0, 0)
    md.tie(1, 2, [0])
    w = math.sqrt(k / (2 * m))
    t = np.linspace(0, 2 * math.pi / w, 801)
    r = dyn.newmark(md, t, load=lambda tk: np.array([0.0, 0.0, 10.0]))
    exact = 10.0 / k * (1 - np.cos(w * t))
    check("MPC tie in dynamics: tied node follows the step-load closed form", np.max(np.abs(r.u[2] - exact)) / (10 / k),
          0.0, atol=2e-4, source="Chopra 2012: u = (F/k)(1 − cos ωt), ω = √(k/2m)")
    check_true("MPC tie: both nodes move together", np.allclose(r.u[1], r.u[2], rtol=0, atol=1e-15),
               source="constraint u1 = u2")


# ---------------------------------------------------------------------------------------------- central difference
def test_central_difference_stability_and_accuracy():
    md = _chain(3)
    K, M = md.K().toarray()[1:, 1:], md.M(lumped=True).toarray()[1:, 1:]
    wmax = math.sqrt(sla.eigh(K, M, eigvals_only=True).max())
    dtcr = dyn.critical_time_step(md)
    check("central difference: Δt_cr = 2/ω_max (dense eigensolution)", dtcr, 2 / wmax, rtol=1e-10,
          source="Bathe 2014 / Hughes 2000: central difference stability limit")
    t_bad = np.arange(0, 50) * 1.01 * dtcr
    expect_error("central difference above Δt_cr raises ValueError", dyn.central_difference, md, t_bad,
                 u0=np.array([0.0, 1e-3, 2e-3, 3e-3]), error=ValueError)
    # just below the limit: bounded over many steps (with damping as well: Jury conditions, Ω ≤ 2)
    u0 = np.array([0.0, 1e-3, -2e-3, 3e-3])
    for damping in ((0.0, 0.0), (5.0, 1e-4)):
        r = dyn.central_difference(md, np.arange(0, 4000) * 0.98 * dtcr, u0=u0, damping=damping)
        check_true(f"central difference at 0.98 Δt_cr stays bounded (damping {damping})",
                   np.max(np.abs(r.u)) < 10 * np.max(np.abs(u0)), np.max(np.abs(r.u)),
                   source="derivation: Jury conditions of (1+ζΩ)z² − (2−Ω²)z + (1−ζΩ)")
    # accuracy: SDOF free vibration, second order
    errs = []
    for n in (40, 80):
        t = np.linspace(0, 2 * T_S, 2 * n + 1)
        r = dyn.central_difference(_sdof(), t, u0=np.array([0.01]))
        errs.append(np.max(np.abs(r.u[0] - 0.01 * np.cos(W_S * t))) / 0.01)
    check("central difference, Δt = T/80: error below 1e-2", errs[1], 0.0, atol=1e-2,
          source="Chopra 2012: u = u0 cos ωt")
    check("central difference: observed order ≈ 2", math.log2(errs[0] / errs[1]), 2.0, rtol=0.03,
          source="Hughes 2000: central difference is second-order accurate")
    rn = dyn.newmark(_sdof(), np.linspace(0, T_S, 201), load=np.array([50.0]))
    rc = dyn.central_difference(_sdof(), np.linspace(0, T_S, 201), load=np.array([50.0]))
    check("central difference vs Newmark (Δt = T/200), step load", np.max(np.abs(rc.u - rn.u)) / (50 / K_S), 0.0,
          atol=2e-3, source="both second order; difference O(Δt²)")


# ---------------------------------------------------------------------------------------------- modal
def test_modal_superposition_equals_direct_newmark():
    md, _ = _cantilever(n_el=4)
    md.load(4, 1, -100.0)
    t = np.linspace(0, 0.02, 401)
    load = lambda tk: md.F * min(tk / 0.005, 1.0)      # ramp then hold
    alpha_r, beta_r = 3.0, 2e-6
    rd = dyn.newmark(md, t, load=load, damping=(alpha_r, beta_r))
    rm = dyn.modal_superposition(md, t, load=load, rayleigh=(alpha_r, beta_r), method="newmark")
    scale = np.max(np.abs(rd.u))
    check("modal superposition (all 12 modes, Newmark on SDOFs) = direct Newmark, same Δt",
          np.max(np.abs(rm.u - rd.u)) / scale, 0.0, atol=1e-9,
          source="derivation: Newmark is linear and Rayleigh damping is classical (modes decouple)")
    check("modal vs direct: accelerations", np.max(np.abs(rm.a - rd.a)) / np.max(np.abs(rd.a)), 0.0, atol=1e-8,
          source="derivation: as above")
    # exact piecewise-linear recurrence converges to the same history as Δt → 0
    re = dyn.modal_superposition(md, t, load=load, rayleigh=(alpha_r, beta_r), method="exact")
    tf = np.linspace(0, 0.02, 3201)
    rf = dyn.newmark(md, tf, load=load, damping=(alpha_r, beta_r))
    check("exact modal recurrence vs direct Newmark with Δt/8 (tip)", np.max(np.abs(re.u[13] - rf.u[13, ::8])) / scale,
          0.0, atol=1e-5, source="Newmark error O(Δt²) → 0")


def test_modal_exact_recurrence_sdof():
    F = 100.0
    t = np.linspace(0.0, 2 * T_S, 41)                  # coarse: 20 steps per period
    r = dyn.modal_superposition(_sdof(), t, load=np.array([F]))
    check("exact modal recurrence, step load: no time-step error", np.max(np.abs(r.u[0] - F / K_S * (1 - np.cos(W_S * t)))),
          0.0, atol=1e-15, source="Chopra 2012: u = (F/k)(1 − cos ωt)")
    zeta, u0 = 0.1, 0.02
    r = dyn.modal_superposition(_sdof(), t, zeta=zeta, u0=np.array([u0]))
    wd = W_S * math.sqrt(1 - zeta ** 2)
    exact = u0 * np.exp(-zeta * W_S * t) * (np.cos(wd * t) + zeta * W_S / wd * np.sin(wd * t))
    check("exact modal recurrence, damped free vibration", np.max(np.abs(r.u[0] - exact)) / u0, 0.0, atol=1e-12,
          source="Chopra 2012: underdamped free vibration")
    # ramp load p = r t: exact u = (r/k)(t − sin(ωt)/ω)
    rate = 2.0e3
    r = dyn.modal_superposition(_sdof(), t, load=lambda tk: np.array([rate * tk]))
    exact = rate / K_S * (t - np.sin(W_S * t) / W_S)
    check("exact modal recurrence, ramp load", np.max(np.abs(r.u[0] - exact)) / np.max(np.abs(exact)), 0.0,
          atol=1e-12, source="Chopra 2012: ramp-force response")
    expect_error("modal superposition refuses non-classical dashpot damping", dyn.modal_superposition,
                 _sdof(c=1.0), t, error=ValueError)


def test_rayleigh_coefficients():
    zeta, f1, f2 = 0.02, 3.0, 40.0
    a, b = dyn.rayleigh_coefficients(zeta, f1, f2)
    z = lambda f: a / (4 * math.pi * f) + b * math.pi * f
    check("Rayleigh: ζ(f1) = target", z(f1), zeta, rtol=1e-12, source="Chopra 2012: ζ = α/(2ω) + βω/2")
    check("Rayleigh: ζ(f2) = target", z(f2), zeta, rtol=1e-12, source="Chopra 2012: ζ = α/(2ω) + βω/2")
    check_true("Rayleigh: ζ below target between f1 and f2", z(math.sqrt(f1 * f2)) < zeta, z(math.sqrt(f1 * f2)),
               source="derivation: ζ(ω) is convex with its minimum inside [ω1, ω2]")
    w1, w2 = 2 * math.pi * f1, 2 * math.pi * f2
    check("Rayleigh closed form α = 2ζω1ω2/(ω1+ω2)", a, 2 * zeta * w1 * w2 / (w1 + w2), rtol=1e-12,
          source="Chopra 2012")
    a2, b2 = dyn.rayleigh_coefficients((0.01, 0.05), f1, f2)
    check("Rayleigh, two targets: ζ(f2) = 0.05", a2 / (4 * math.pi * f2) + b2 * math.pi * f2, 0.05, rtol=1e-12,
          source="derivation: 2×2 linear system")
    md, _ = _cantilever(n_el=4)
    C = dyn.damping_matrix(md, a, b)
    check("damping_matrix = αM + βK", abs(C - (a * md.M() + b * md.K())).max(), 0.0, atol=1e-12,
          source="definition")
    expect_error("Rayleigh: equal frequencies rejected", dyn.rayleigh_coefficients, 0.02, 5.0, 5.0, error=ValueError)


# ---------------------------------------------------------------------------------------------- harmonic
def test_cantilever_harmonic_peak_at_first_natural_frequency():
    md, f1_beam = _cantilever(n_el=10)
    tip = 10 * 3 + 1
    md.load(10, 1, 1.0)
    f1 = md.modal(n=1).f[0]
    check("cantilever f1 (10 Frame2D, consistent mass) vs Euler-Bernoulli", f1, f1_beam, rtol=1e-4,
          source="Euler-Bernoulli cantilever: (β1 L)² = 1.8751² (Timoshenko & Gere / Clough & Penzien 1993)")
    zeta = 0.01
    amp = lambda f: -abs(dyn.harmonic(md, [f], damping=zeta).U[tip, 0])
    opt = minimize_scalar(amp, bounds=(0.9 * f1, 1.1 * f1), method="bounded", options={"xatol": 1e-7 * f1})
    check("harmonic (hysteretic ζ = 0.01): tip response peaks at f1 from Model.modal", opt.x, f1, rtol=2e-5,
          source="Clough & Penzien 1993: hysteretic FRF |1/(ω1²(1+2iζ) − ω²)| peaks at ω1")
    check("harmonic: peak amplitude ≈ φ_tip²/(2ζω1²) (single-mode estimate)", -opt.fun,
          md.modal(n=1).modes[tip, 0] ** 2 / (2 * zeta * (2 * math.pi * f1) ** 2), rtol=1e-2,
          source="Clough & Penzien 1993: resonant amplification 1/(2ζ)")
    fs = np.array([0.0, 0.5 * f1, 1.3 * f1, 4.0 * f1])
    rd = dyn.harmonic(md, fs, damping=zeta)
    rm = dyn.harmonic_modal(md, fs, zeta=zeta, hysteretic=True)
    check("harmonic direct = modal (all modes, hysteretic)", np.max(np.abs(rd.U - rm.U)) / np.max(np.abs(rd.U)), 0.0,
          atol=1e-9, source="derivation: K(1+2iζ) − ω²M diagonalises in the mass-normalised modes")
    us = md.static().u
    check("harmonic at f = 0 (undamped) = static solution",
          np.max(np.abs(dyn.harmonic(md, [0.0]).U[:, 0] - us)) / np.max(np.abs(us)), 0.0, atol=1e-10,
          source="derivation: ω = 0 → K U = F")
    a, b = dyn.rayleigh_coefficients(0.02, f1, 5 * f1)
    rv = dyn.harmonic(md, fs, damping=(a, b))
    rvm = dyn.harmonic_modal(md, fs, rayleigh=(a, b))
    check("harmonic direct = modal (all modes, Rayleigh viscous)", np.max(np.abs(rv.U - rvm.U)) / np.max(np.abs(rv.U)),
          0.0, atol=1e-9, source="derivation: classical damping decouples")
    # SDOF viscous: |U| = (F/k) / √((1 − r²)² + (2ζr)²)
    c = 2 * 0.05 * math.sqrt(K_S * M_S)
    sd = _sdof(c)
    r_ = 0.8
    U = dyn.harmonic(sd, [r_ * W_S / (2 * math.pi)], F=np.array([1.0])).U[0, 0]
    check("SDOF dashpot FRF amplitude", abs(U), (1 / K_S) / math.sqrt((1 - r_ ** 2) ** 2 + (2 * 0.05 * r_) ** 2),
          rtol=1e-12, source="Chopra 2012: dynamic response factor R_d")
