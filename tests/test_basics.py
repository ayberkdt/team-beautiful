"""Tests of the basic modules: atmosphere, flow, tensor, beam, wing, lamina, geometry, sizing."""
import math
import numpy as np

from aerokit.aero import atmosphere
from aerokit.aero import flow
from aerokit.structures import tensor
from aerokit.structures import beam
from aerokit.aero import wing
from aerokit.composites import lamina
from aerokit.aero import geometry
from aerokit.aero import sizing
from aerokit.verification import check


def test_atmosphere():
    a0 = atmosphere.isa(0)
    check("ISA ρ0 = 1.225 kg/m³", a0["rho"], 1.225, rtol=1e-4)
    check("ISA a0 = 340.29 m/s", a0["a"], 340.294, rtol=1e-4)
    check("ISA μ0 = 1.7894e-5 Pa·s", a0["mu"], 1.7894e-5, rtol=1e-3)
    a11 = atmosphere.isa(11000)
    check("ISA T(11 km) = 216.65 K", a11["T"], 216.65)
    check("ISA p(11 km) = 22632 Pa", a11["p"], 22632.06, rtol=1e-4)


def test_flow():
    # geometric series: first = 1, G = 2, 3 layers → 1 + 2 + 4 = 7 ≥ 7
    check("layer count, geometric series", flow.layer_count(1, 7, 2), 3)
    # GCI: f = 1 + 0.5 h² (p = 2 exactly), h = 1, 1.5, 2.25 (r = 1.5)
    f = [1 + 0.5 * h ** 2 for h in (1, 1.5, 2.25)]
    g = flow.gci(f[0], f[1], f[2], 1.5, 1.5)
    check("GCI apparent order p = 2", g["p"], 2.0, rtol=1e-6)
    check("GCI Richardson extrapolation = 1.0", g["f_ext"], 1.0, rtol=1e-9)
    uv = flow.speed_components(1.0, 6)
    check("AoA 6° → Ux 0.9945 (Ansys course)", uv["Ux"], 0.9945, rtol=1e-4)
    check("AoA 6° → Uy 0.1045 (Ansys course)", uv["Uy"], 0.1045, rtol=1e-3)


def test_tensor():
    s = 100e6
    single = tensor.Stress(sxx=s)
    check("uniaxial: von Mises = σ", single.von_mises(), s)
    check("uniaxial: Tresca = σ", single.tresca(), s)
    tau = 50e6
    shear = tensor.Stress(txy=tau)
    check("pure shear: von Mises = √3·τ", shear.von_mises(), math.sqrt(3) * tau)
    check("pure shear: Tresca = 2τ", shear.tresca(), 2 * tau)
    check("pure shear: σ1 = τ", shear.principal()[0][0], tau)
    hid = tensor.Stress(sxx=-5e6, syy=-5e6, szz=-5e6)
    check("hydrostatic: von Mises = 0", hid.von_mises(), 0.0, atol=1e-6)
    m = tensor.mohr_2d(80, -40, 25)
    check("Mohr centre 20", m["center"], 20)
    check("Mohr radius 65", m["radius"], 65)
    check("Mohr σ1 = 85", m["s1"], 85)
    check("Mohr σ2 = −45", m["s2"], -45)
    g = tensor.Stress(sxx=80, syy=-40, txy=25)
    rotated = g.rotate_z(m["theta_p"])
    check("principal axes: τxy = 0", rotated.s[0, 1], 0.0, atol=1e-9)
    check("principal axes: σx' = σ1", rotated.s[0, 0], 85)
    general = tensor.Stress(10, -20, 30, 5, -7, 12)
    R = general.rotate_z(37).rotate([[1, 0, 0], [0, math.cos(0.4), math.sin(0.4)],
                                 [0, -math.sin(0.4), math.cos(0.4)]])
    for i, (a, b) in enumerate(zip(general.invariants(), R.invariants(), strict=True)):
        check(f"rotation preserves I{i + 1}", b, a, rtol=1e-9, atol=1e-9)
    check("rotation preserves von Mises", R.von_mises(), general.von_mises(), rtol=1e-12)
    t, sn, tau_n = single.traction([1, 1, 0])
    check("45° plane: normal = σ/2", sn, s / 2)
    check("45° plane: shear = σ/2", tau_n, s / 2)
    E, nu = 70e9, 0.33
    eps = tensor.from_stress_strain(general, E, nu)
    back = tensor.from_strain_stress(eps, E, nu)
    check("Hooke round trip", float(np.max(np.abs(back.s - general.s))), 0.0, atol=1e-6)
    eps_single = tensor.from_stress_strain(single, E, nu)
    check("uniaxial: εxx = σ/E", eps_single[0, 0], s / E)
    check("uniaxial: εyy = −ν σ/E", eps_single[1, 1], -nu * s / E)


def test_beam():
    b = beam.tube(0.05, 0.002)
    check("tube: J = 2I", b["J"], 2 * b["I"])
    d = beam.rectangle(0.02, 0.04)
    check("rectangle I = bh³/12", d["I"], 0.02 * 0.04 ** 3 / 12)
    check("Euler pinned-pinned π²EI/L²", beam.euler_column(1, 1, 1), math.pi ** 2)
    # thin box I ↔ exact hollow rectangle (outer b+t, h+t; inner b−t, h−t), t/h = 1/100
    bb, hh, t = 0.3, 0.1, 0.001
    exact = ((bb + t) * (hh + t) ** 3 - (bb - t) * (hh - t) ** 3) / 12
    check("thin box I ≈ exact (t/h = 1%)", beam.box(bb, hh, t, t)["I"], exact, rtol=0.01)
    # Bredt: thin tube J ≈ 2πR³t
    R, tt = 0.05, 0.0005
    J_bredt = 4 * (math.pi * R ** 2) ** 2 / (2 * math.pi * R / tt)
    check("Bredt J = 2πR³t (thin tube)", J_bredt, 2 * math.pi * R ** 3 * tt)
    check("margin of safety MS = 400/(1.5·200) − 1", beam.safety_margin(400, 200, 1.5), 400 / 300 - 1)
    # SP-8007, r/t = 256 → φ = 1 → γ = 1 − 0.901(1 − e⁻¹)
    check("SP-8007 axial γ (r/t 256)", beam.sp8007_reduction(256, 1), 1 - 0.901 * (1 - math.exp(-1)))
    check("SP-8007 γ → 1 as r/t → 0", beam.sp8007_reduction(1e-9, 1), 1.0, rtol=1e-5)


def test_wing():
    W, n, bs = 50000.0, 3.8, 16.0
    y = wing.span_loads(W, n, bs, 2.0, 2.0, distribution="ellipse", n_point=4001)
    check("ellipse: half-wing lift nW/2", y["V"][0], n * W / 2, rtol=2e-3)
    check("ellipse: root moment nWb/(3π)", y["M"][0], wing.ellipse_root_moment(W, n, bs), rtol=3e-3)
    tr = wing.span_loads(W, 1, bs, 2.0, 2.0, distribution="trapezoid", n_point=4001)
    check("rectangular wing, uniform load: root moment W·b/8", tr["M"][0], W * bs / 8, rtol=1e-4)
    # FAR 23.337: 2.1 + 24000/(W+10000); W = 14000 lb → 3.1; 2000 lb → 3.8 cap
    check("FAR 23.337 n (14 000 lb) = 3.1", wing.n_limit_far23_normal(14000 * 4.4482216152605)[0], 3.1)
    check("FAR 23.337 n upper limit 3.8", wing.n_limit_far23_normal(2000 * 4.4482216152605)[0], 3.8)
    check("FAR 23.337 negative = −0.4n", wing.n_limit_far23_normal(14000 * 4.4482216152605)[1], -1.24)
    sc = wing.span_loads(W, 1, bs, 2.4, 1.2, n_point=4001)
    check("Schrenk: half-wing lift W/2", sc["V"][0], W / 2, rtol=2e-3)


def test_lamina():
    Q = lamina.Q_matrix(140e9, 10e9, 0.3, 5e9)
    A, B, D, _ = lamina.abd(Q, [(0, 1e-3)])
    check("single 0° ply: A11 = Q11·t", A[0, 0], Q[0, 0] * 1e-3)
    Q90 = lamina.Qbar(Q, 90)
    check("Q̄(90°)11 = Q22", Q90[0, 0], Q[1, 1], rtol=1e-9)
    qi = [(0, 1.25e-4), (45, 1.25e-4), (-45, 1.25e-4), (90, 1.25e-4)]
    qi = qi + qi[::-1]
    A, B, D, _ = lamina.abd(Q, qi)
    check("quasi-isotropic: A11 = A22", A[1, 1], A[0, 0], rtol=1e-9)
    check("quasi-isotropic: A16 = 0", A[0, 2], 0.0, atol=1e-3)
    check("symmetric layup: B = 0", float(np.max(np.abs(B))), 0.0, atol=1e-6)
    check("quasi-isotropic: A66 = (A11 − A12)/2", A[2, 2], (A[0, 0] - A[0, 1]) / 2, rtol=1e-9)
    r = lamina.layer_stresses(Q, [(0, 1e-3)], N=np.array([1e5, 0, 0]))
    check("single 0° ply: σ1 = N/t", r["layers"][0]["sig12"][0], 1e8, rtol=1e-9)
    tw = lamina.tsai_wu((1500e6, 0, 0), 1500e6, 1200e6, 50e6, 250e6, 70e6)
    # σ1 = Xt: F11·Xt² + F1·Xt = Xt/Xc + 1 − Xt/Xc = 1 → index and safety factor exactly 1
    check("Tsai-Wu: σ1 = Xt → index 1", tw["index"], 1.0, rtol=1e-12)
    check("Tsai-Wu: σ1 = Xt → safety factor 1", tw["safety"], 1.0, rtol=1e-12)
    # equilibrium: the thickness-weighted sum of ply stresses equals N (global axes)
    sequence = [(0, 1.31e-4), (45, 1.31e-4), (-45, 1.31e-4), (90, 1.31e-4)]
    sequence = sequence + sequence[::-1]
    rr = lamina.layer_stresses(Q, sequence, N=np.array([1.5e5, 2e4, -1e4]))
    total = sum(np.linalg.inv(lamina.T_stress(k["angle"])) @ k["sig12"] * 1.31e-4 for k in rr["layers"])
    check("CLT equilibrium: Σσx·t = Nx", total[0], 1.5e5, rtol=1e-9)
    check("CLT equilibrium: Σσy·t = Ny", total[1], 2e4, rtol=1e-9)
    check("CLT equilibrium: Στxy·t = Nxy", total[2], -1e4, rtol=1e-9)
    tw2 = lamina.tsai_wu((0, 0, 70e6), 1500e6, 1200e6, 50e6, 250e6, 70e6)
    check("Tsai-Wu: pure shear τ = S → index 1", tw2["index"], 1.0)


def test_geometry():
    x, y = geometry.naca4("0012", n=401)
    check("NACA 0012 max. thickness 12 %", float(np.max(y) - np.min(y)), 0.12, rtol=2e-3)
    check("NACA 0012 max. thickness at x ≈ 0.30c", float(x[np.argmax(y)]), 0.30, atol=0.01)
    # open trailing edge: 2·5t·(0.2969 − 0.1260 − 0.3516 + 0.2843 − 0.1015) = 0.00252 (t = 0.12)
    check("NACA 0012 open trailing-edge thickness 0.00252c", geometry.trailing_edge_thickness(x, y), 0.00252, rtol=1e-3)
    xc, yc = geometry.naca4("0012", closed_trailing_edge=True)
    check("NACA 0012 closed trailing-edge thickness 0", geometry.trailing_edge_thickness(xc, yc), 0.0, atol=1e-6)
    x2, y2 = geometry.naca4("2412", n=401)
    camber = 0.5 * (y2[:401][::-1] + y2[400:])
    check("NACA 2412 max. camber 2 %", float(np.max(camber)), 0.02, rtol=0.01)
    p = geometry.planform(10.0, 8.0, 1.0)
    check("rectangular wing MAC = c", p["MAC"], p["c_root"])
    p2 = geometry.planform(10.0, 8.0, 0.5)
    check("planform area is preserved", 0.5 * (p2["c_root"] + p2["c_tip"]) * p2["b"], 10.0)


def test_size():
    # Raymer ch. 3.6.4 worked example (VT AOE 4065 A4 slides 63–66): jet, R = 1500 nm, M 0.6
    cruise = sizing.cruise_jet(9_114_000 * 0.3048, 0.5, 596.9 * 0.3048, 13.9)
    check("Raymer example cruise fraction 0.858", cruise, 0.858, rtol=1e-3)
    loiter = sizing.loiter_jet(10_800, 0.4, 16)
    check("Raymer example 3 h loiter fraction 0.9277", loiter, 0.9277, rtol=1e-4)
    mission = 0.97 * 0.985 * cruise * loiter * cruise * sizing.loiter_jet(1200, 0.4, 16) * 0.995
    check("Raymer example mission fraction 0.6441", mission, 0.6441, rtol=1e-3)
    wf = sizing.fuel_ratio(mission)
    check("Raymer example Wf/W0 = 0.3773", wf, 0.3773, rtol=2e-3)
    s = sizing.takeoff_weight(10_800 * sizing.LB_N, wf, "military cargo/bomber")
    check("Raymer example W0 ≈ 56 700 lb", s["W0"] / sizing.LB_N, 56_700, rtol=5e-3)
    # propeller Breguet: SI form ↔ US form with the 375 constant (R in miles, C_bhp in lb/hp/h)
    R_mile = 800.0
    us_form = math.exp(-R_mile * 0.5 / (375 * 0.8 * 12))
    check("propeller Breguet SI = form with 375", sizing.cruise_propeller(R_mile * 1609.344, 0.5, 0.8, 12),
            us_form, rtol=1e-4)
    check("service ceiling 100 ft/min = 0.508 m/s", sizing.SERVICE_CEILING_VV, 0.508, rtol=1e-3)
    # Slide 68 uses K = 0.054 (inconsistent with 1/(π·7·0.8) = 0.0568; an inconsistency on the slide).
    # The formula is checked with the slide's K: e = 1/(π·7·0.054).
    CD0, K = sizing.cd0_ldmax(16, 7, 1 / (math.pi * 7 * 0.054))
    check("Raymer example CD0 ≈ 0.0181 (L/Dmax 16, K 0.054)", CD0, 0.0181, rtol=2e-3)
