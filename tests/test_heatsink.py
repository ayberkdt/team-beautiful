"""Plate-fin heat sink (aerokit.design.heatsink) against the fin ODE and the correlations it implements."""
import math

import numpy as np

from aerokit.design import heatsink as hs
from aerokit.verification import check, check_true, expect_error


def test_fin_efficiency_against_finite_difference():
    # theta'' = m^2 theta, theta(0) = 1, theta'(H) = 0; q = -k A_c theta'(0); eta = q / (h P H)
    h, k, t, H = 50.0, 160.0, 1e-3, 0.03
    m2 = 2 * h / (k * t)
    n = 4000
    x = np.linspace(0, H, n + 1)
    dx = x[1] - x[0]
    A = np.zeros((n + 1, n + 1))
    b = np.zeros(n + 1)
    A[0, 0], b[0] = 1.0, 1.0
    for i in range(1, n):
        A[i, i - 1], A[i, i], A[i, i + 1] = 1.0, -2.0 - m2 * dx * dx, 1.0
    A[n, n - 1], A[n, n] = 2.0, -2.0 - m2 * dx * dx            # ghost node for theta'(H) = 0
    theta = np.linalg.solve(A, b)
    q = -k * t * (-3 * theta[0] + 4 * theta[1] - theta[2]) / (2 * dx)     # per unit fin length
    check("fin efficiency = tanh(mH)/(mH) (finite-difference fin)", q / (h * 2 * H), hs.fin_efficiency(h, k, t, H),
          rtol=1e-4)
    check_true("short, conductive fin is almost fully effective", hs.fin_efficiency(1.0, 400.0, 2e-3, 1e-3) > 0.999)


def test_correlations():
    air = hs.AIR_25C
    U, L = 2.0, 0.1
    Re = U * L / air["nu"]
    check("forced: h L / k = 0.664 Re^0.5 Pr^(1/3)", hs.forced_h(U, L) * L / air["k"],
          0.664 * math.sqrt(Re) * air["Pr"] ** (1 / 3), rtol=1e-12)
    h = hs.natural_h(30.0, 0.1)
    check_true(f"natural convection h in the usual 2-10 W/m2K band for a 0.1 m plate (got {h:.2f})", 2 < h < 10)
    expect_error("Rayleigh outside the laminar range", hs.natural_h, 30.0, 5.0, error=ValueError)


def test_energy_balance_and_sweep():
    sink = hs.HeatSink(W=0.08, L=0.1, t_b=3e-3, H=0.03, t=1e-3, n=12)
    r = hs.evaluate(sink, k=160.0, rho=2700.0, Q=40.0, U=None)
    A = (0.08 - 12e-3) * 0.1 + r["fin_efficiency"] * 12 * 2 * 0.03 * 0.1
    R = 3e-3 / (160.0 * 0.08 * 0.1) + 1 / (r["h_W_m2K"] * A)
    check("natural: converged dT = Q R with h at that dT", r["dT_K"], 40.0 * R, rtol=1e-9)
    check("mass = rho x (base + fins)", r["mass_kg"], 2700.0 * (0.08 * 0.1 * 3e-3 + 12 * 0.03 * 1e-3 * 0.1),
          rtol=1e-12)
    ok = hs.sweep(0.08, 0.1, 3e-3, 0.03, 160.0, 2700.0, 20.0, U=2.0, dT_max=40.0)
    check_true("sweep returns feasible designs lightest first",
               bool(ok) and all(a["mass_kg"] <= b["mass_kg"] for a, b in zip(ok, ok[1:], strict=False))
               and all(x["dT_K"] <= 40.0 for x in ok))


def test_elenbaas_spacing_and_gap_screen():
    air = hs.AIR_25C
    dT, L = 40.0, 0.1
    b = hs.elenbaas_spacing(dT, L)
    T = 298.15 + dT / 2
    Ra_b = 9.81 / T * dT * b ** 3 / (air["nu"] * air["nu"] / air["Pr"])
    check("Elenbaas optimum: channel Rayleigh Ra_b b/L = 50", Ra_b * b / L, 50.0, rtol=1e-9)
    ok = hs.sweep(0.08, 0.1, 3e-3, 0.03, 160.0, 2700.0, 50.0, U=None, dT_max=40.0)
    check_true("natural sweep keeps only gaps >= b_opt", all(x["gap_ok"] for x in ok))
