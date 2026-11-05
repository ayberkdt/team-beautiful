"""Discrete elements: Spring, PointMass, Dashpot.

Expected values are closed forms independent of the FEM code: SDOF natural frequency
ω = √(k/m) (Chopra 2012, SDOF free vibration), series/parallel spring combinations and the statics of grounded
springs (equilibrium of a single node).
"""
import math

import numpy as np

from aerokit.fem import Model
from aerokit.fem.elements.discrete import Dashpot, PointMass, Spring
from aerokit.fem.elements.line import Frame2D
from aerokit.verification import check, check_true, expect_error


def test_spring_mass_natural_frequency():
    k, m = 2.5e5, 12.0
    md = Model([[0.0, 0.0], [1.0, 0.0]], ndof=2)
    md.add(Spring(0, 1, k, ndof=2, dof=0))
    md.add(PointMass(1, m, ndof=2))
    md.fix(0, [0, 1])
    md.fix(1, [1])
    r = md.modal(n=1)
    check("spring-mass: ω = √(k/m)", r.omega[0], math.sqrt(k / m), rtol=1e-12,
          source="Chopra 2012, SDOF free vibration ω_n = √(k/m)")
    check("spring-mass: mode mass-normalised (φᵀMφ = 1)", m * r.modes[2, 0] ** 2, 1.0, rtol=1e-12,
          source="derivation: mass normalisation")


def test_rotary_inertia_on_frame_node():
    # torsional spring kθ to ground + rotary inertia J at the free node of a 2-D frame model
    kt, J = 800.0, 0.02
    md = Model([[0.0, 0.0]], ndof=3)
    md.add(Spring(0, None, kt, ndof=3, dof=2))
    md.add(PointMass(0, 5.0, ndof=3, inertia=J))
    md.fix(0, [0, 1])
    check("rotational SDOF: ω = √(kθ/J)", md.modal(n=1).omega[0], math.sqrt(kt / J), rtol=1e-12,
          source="derivation: J θ̈ + kθ θ = 0")
    mm = PointMass(0, 5.0, ndof=3, inertia=J).m(np.zeros((1, 2)))
    check_true("point mass (2-D frame): diag(m, m, J)", np.allclose(mm, np.diag([5.0, 5.0, J])),
               source="definition")
    m3 = PointMass(0, 2.0, ndof=6, inertia=[1.0, 2.0, 3.0]).m(np.zeros((1, 3)))
    check_true("point mass (3-D frame): diag(m, m, m, Jx, Jy, Jz)",
               np.allclose(m3, np.diag([2.0, 2.0, 2.0, 1.0, 2.0, 3.0])), source="definition")


def test_springs_in_series_and_parallel():
    k1, k2, P = 3.0e4, 6.0e4, 120.0
    # series: 0 —k1— 1 —k2— 2, load at node 2
    ser = Model([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]], ndof=1)
    ser.add(Spring(0, 1, k1, ndof=1, dof=0))
    ser.add(Spring(1, 2, k2, ndof=1, dof=0))
    ser.fix(0, 0)
    ser.load(2, 0, P)
    u = ser.static().u
    check("series springs: k_eq = k1 k2/(k1 + k2)", P / u[2], k1 * k2 / (k1 + k2), rtol=1e-12,
          source="derivation: same force, added elongations")
    check("series springs: force in each spring = P",
          ser.element_results(u)[1]["force"], P, rtol=1e-12, source="derivation: equilibrium")
    # parallel: two springs between the same two nodes
    par = Model([[0.0, 0.0], [1.0, 0.0]], ndof=1)
    par.add(Spring(0, 1, k1, ndof=1, dof=0))
    par.add(Spring(0, 1, k2, ndof=1, dof=0))
    par.fix(0, 0)
    par.load(1, 0, P)
    check("parallel springs: k_eq = k1 + k2", P / par.static().u[1], k1 + k2, rtol=1e-12,
          source="derivation: same elongation, added forces")


def test_grounded_spring_statics():
    k, P = 5.0e3, 40.0
    md = Model([[0.0, 0.0]], ndof=2)
    md.add(Spring(0, None, k, ndof=2, dof=0))
    md.add(Spring(0, None, 2 * k, ndof=2, dof=1))
    md.load(0, 0, P)
    md.load(0, 1, -P)
    r = md.static()
    check("grounded spring x: u = P/k", r.u[0], P / k, rtol=1e-12, source="derivation: k u = P")
    check("grounded spring y: v = −P/(2k)", r.u[1], -P / (2 * k), rtol=1e-12, source="derivation: k u = P")
    check("grounded spring: force = P", md.element_results(r.u)[0]["force"], P, rtol=1e-12,
          source="derivation: equilibrium")
    # inclined grounded spring (30°) + a stiff spring blocking the normal direction
    th = math.radians(30.0)
    e, nrm = np.array([math.cos(th), math.sin(th)]), np.array([-math.sin(th), math.cos(th)])
    sk = Spring(0, None, k, ndof=2, direction=e * 3.0)          # length of the vector is irrelevant
    check_true("inclined spring: k e eᵀ", np.allclose(sk.k(np.zeros((1, 2))), k * np.outer(e, e)),
               source="derivation: projection on the spring axis")
    md2 = Model([[0.0, 0.0]], ndof=2)
    md2.add(sk)
    md2.add(Spring(0, None, 1e3 * k, ndof=2, direction=nrm))
    md2.load(0, 0, P * e[0])
    md2.load(0, 1, P * e[1])
    u = md2.static().u
    check("inclined grounded spring: displacement along axis = P/k", u @ e, P / k, rtol=1e-12,
          source="derivation: decoupled axial/normal springs")
    check("inclined grounded spring: no normal displacement", u @ nrm, 0.0, atol=1e-15,
          source="derivation: decoupled axial/normal springs")


def test_spring_supported_beam():
    # propped cantilever with an elastic prop: tip deflection = P / (k + 3EI/L³)
    E, A, I, L, k, P = 70e9, 1e-3, 2e-6, 2.0, 1.0e5, 1.0e3
    md = Model([[0.0, 0.0], [L, 0.0]], ndof=3)
    md.add(Frame2D(0, 1, E, A, I))
    md.add(Spring(1, None, k, ndof=3, dof=1))
    md.fix(0, [0, 1, 2])
    md.load(1, 1, -P)
    v = md.static().u[4]
    check("cantilever on a tip spring: v = −P/(k + 3EI/L³)", v, -P / (k + 3 * E * I / L ** 3), rtol=1e-10,
          source="derivation: springs in parallel (cantilever tip stiffness 3EI/L³, Young & Budynas 2002 beam table)")


def test_element_protocol_and_errors():
    X = np.zeros((2, 2))
    s = Spring(0, 1, 10.0, ndof=2, dof=1)
    d = Dashpot(0, 1, 3.0, ndof=2, direction=[0.0, 1.0])
    pm = PointMass(0, 1.0, ndof=2)
    for name, el, n in (("spring", s, 4), ("dashpot", d, 4), ("point mass", pm, 2)):
        check_true(f"{name}: kg is zero", np.all(el.kg(X, np.zeros(n)) == 0), source="definition")
    check_true("spring: massless", np.all(s.m(X) == 0), source="definition")
    check_true("dashpot: no stiffness or mass", np.all(d.k(X) == 0) and np.all(d.m(X) == 0), source="definition")
    check_true("dashpot: c = c0 [[1, −1], [−1, 1]] along y",
               np.allclose(d.c(X)[np.ix_([1, 3], [1, 3])], 3.0 * np.array([[1, -1], [-1, 1]])), source="definition")
    check("dashpot force from relative velocity", d.force(np.array([0.0, 1.0, 0.0, 3.0])), 6.0,
          source="definition: F = c Δv")
    check("spring force (tension positive)", s.stress(X, np.array([0.0, 0.0, 0.0, 0.02]))["force"], 0.2,
          source="definition: F = k Δu")
    check_true("grounded spring is a single-node element", Spring(3, None, 1.0, ndof=2, dof=0).nodes == [3],
               source="definition")
    expect_error("spring needs dof or direction", Spring, 0, 1, 1.0, 2, error=ValueError)
    expect_error("spring rejects both dof and direction", Spring, 0, 1, 1.0, 2, 0, [1.0, 0.0], error=ValueError)
    expect_error("spring rejects negative stiffness", Spring, 0, 1, -1.0, 2, 0, error=ValueError)
    expect_error("spring rejects zero direction", Spring, 0, 1, 1.0, 2, None, [0.0, 0.0], error=ValueError)
    expect_error("spring rejects dof out of range", Spring, 0, 1, 1.0, 2, 2, error=ValueError)
    expect_error("point mass rejects negative mass", PointMass, 0, -1.0, 2, error=ValueError)
    expect_error("point mass: wrong number of inertias", PointMass(0, 1.0, 6, inertia=[1.0, 2.0]).m,
                 np.zeros((1, 3)), error=ValueError)
