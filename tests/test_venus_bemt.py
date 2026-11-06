"""BEMT validation: closed-form limits and published rotor test data.

Data (read by the research agent; see 04_Venus/research/):
* Knight & Hefner 1937, NACA TN 626, Tables I-IV (printed): 2-5 blade rotor, R 0.762 m, c 0.0508 m, NACA 0015,
  untwisted, 960 rpm; coefficients there use ½ρ, so standard = printed / 2. Section polar at Re 242 000 from the
  same report (Tables V-VI): lift slope ~5.6/rad, cd_min 0.0113, cl_max ~0.93 → the rotor is *predicted*, not fitted.
* Harrington 1951, NACA TN 2318, rotor 1 (digitised Figs. 4): single and coaxial, 500 ft/s tip speed; cd0 from the
  printed zero-thrust torque C_Q0 = 7.77e-5 (coax) → 0.0115.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from aerokit.venus import bemt as B

AIR = B.FlowState(1.225, 1.79e-5, 340.3)      # sea-level test conditions (assumed; not printed in the reports)

KH = {2: [(6, 0.00442, 0.000316), (8, 0.0065, 0.000494), (10, 0.00847, 0.000691), (12, 0.0099, 0.000878)],
      3: [(6, 0.00548, 0.000474), (8, 0.00833, 0.000735), (10, 0.01125, 0.001048), (12, 0.0137, 0.001357)],
      4: [(6, 0.00645, 0.00062), (8, 0.00981, 0.00092), (10, 0.01382, 0.001395), (12, 0.01745, 0.00191)],
      5: [(6, 0.00694, 0.00068), (8, 0.01103, 0.001086), (10, 0.01548, 0.001635), (12, 0.0200, 0.00228)]}
NACA0015_242K = B.Airfoil(cl_alpha=5.6, alpha0=0.0, cl_max=0.93, cd0=0.0113, d1=0.0, d2=0.7, re_ref=242000)

IN = 0.0254
R_H = 150 * IN


def _harrington_rotor1(theta: float) -> B.Rotor:
    af = B.Airfoil(cd0=0.0115, re_ref=1.3e6, cl_max=1.3)
    return B.Rotor(R_H, 2, (12.43 - 0.0534 * 22.5) * IN, (12.43 - 0.0534 * 150) * IN, theta, 0.0, 0.15, af)


def test_ideal_twist_limit_gives_uniform_inflow_and_fm_sqrt_annulus():
    af = B.Airfoil(cd0=0.0, d1=0.0, d2=0.0, cl_max=10.0)
    rot = B.Rotor(1.0, 4, 0.08, 0.08, 8.0, root_cutout=0.2, airfoil=af, ideal_twist=True)
    r = B.solve(rot, 200.0, B.FlowState(1.225, 1.8e-5, 1e9), tip_loss=False, n=200)
    assert r.lam.max() / r.lam.min() - 1 < 0.03
    assert r.FM == pytest.approx(math.sqrt(1 - 0.2 ** 2), abs=0.005)
    assert r.profile_CP == pytest.approx(0.0, abs=1e-12)


def test_tip_loss_and_profile_drag_lower_fm():
    rot = B.Rotor(1.0, 2, 0.08, 0.08, 8.0, root_cutout=0.15, airfoil=B.Airfoil(cd0=0.0, d1=0.0, d2=0.0))
    no_loss = B.solve(rot, 200.0, AIR, tip_loss=False).FM
    with_loss = B.solve(rot, 200.0, AIR).FM
    with_drag = B.solve(B.Rotor(1.0, 2, 0.08, 0.08, 8.0, root_cutout=0.15), 200.0, AIR).FM
    assert with_drag < with_loss < no_loss


@pytest.mark.parametrize("blades", [2, 3, 4, 5])
def test_knight_hefner_predicted_within_tolerance(blades):
    rot = B.Rotor(0.762, blades, 0.0508, 0.0508, 0.0, 0.0, 0.167, NACA0015_242K)
    om = 960 * 2 * math.pi / 60
    eT, eQ = [], []
    for th, ct, cq in KH[blades]:
        r = B.solve(B.with_collective(rot, th), om, AIR)
        eT.append(r.CT / (ct / 2) - 1)
        eQ.append(r.CP / (cq / 2) - 1)
    assert max(abs(e) for e in eT) < 0.13
    assert max(abs(e) for e in eQ) < 0.10
    assert math.sqrt(np.mean(np.square(eT + eQ))) < 0.08


def test_harrington_rotor1_single_torque_within_8_percent():
    data = [(0.001054, 0.0000676), (0.001407, 0.0000796), (0.001865, 0.0001067), (0.002348, 0.0001373),
            (0.002825, 0.0001748), (0.0031, 0.0001944), (0.003468, 0.000236)]
    vt = 500 * 0.3048
    cts, cqs = [], []
    for th in np.arange(2.0, 15.0, 1.0):
        r = B.solve(_harrington_rotor1(th), vt / R_H, AIR)
        cts.append(r.CT)
        cqs.append(r.CP)
    err = [np.interp(ct, cts, cqs) / cq - 1 for ct, cq in data]
    assert max(abs(e) for e in err) < 0.08


def test_harrington_rotor1_coaxial_with_calibrated_interference():
    """k_upper = 0.3 was fitted to these points with a torque trim (rms 3 %); untrimmed equal collectives stay
    within 7 % above C_T = 0.0025, and k_upper = 0 under-predicts torque (the reason for the parameter)."""
    data = [(0.002485, 0.0001776), (0.003016, 0.000208), (0.003743, 0.000277), (0.004615, 0.000354),
            (0.005204, 0.0004205), (0.005575, 0.0004625)]
    vt = 500 * 0.3048
    om = vt / R_H
    A = math.pi * R_H ** 2

    def curve(k: float):
        cts, cqs = [], []
        for th in np.arange(5.0, 15.0, 1.0):
            c = B.coaxial(_harrington_rotor1(th), _harrington_rotor1(th), om, om, AIR, k_upper=k)
            cts.append(c.thrust / (1.225 * A * vt ** 2))
            cqs.append(c.power / (1.225 * A * vt ** 3))
        return [np.interp(ct, cts, cqs) / cq - 1 for ct, cq in data]

    e3 = curve(0.3)
    assert max(abs(e) for e in e3) < 0.07
    e0 = curve(0.0)
    assert np.mean(e0) < np.mean(e3) - 0.03


def test_coaxial_interference_factor_matches_literature_band():
    """Syal 2008 (via the agent): ideal torque-balanced κ_int 1.266, BEMT on Harrington ~1.26."""
    vt = 500 * 0.3048
    c = B.coaxial(_harrington_rotor1(10.0), _harrington_rotor1(10.0), vt / R_H, vt / R_H, AIR)
    assert 1.15 < c.kappa_int < 1.40


def test_solve_for_thrust_and_collective_round_trip():
    rot = B.Rotor(0.8, 2, 0.12, 0.08, 12.0, -10.0, 0.15)
    flow = B.FlowState(0.889, 1.5e-5, 270.0)
    r = B.solve_for_thrust(rot, 40.0, flow)
    assert r.thrust == pytest.approx(40.0, rel=1e-4)
    rot2, r2 = B.solve_collective(rot, 40.0, r.omega, flow)
    assert rot2.theta75_deg == pytest.approx(12.0, abs=1e-3)
    assert r2.power == pytest.approx(r.power, rel=1e-4)


def test_compressibility_raises_lift_slope():
    af = B.Airfoil()
    cl0, _ = af.coefficients(math.radians(4), 1e6, 0.0)
    cl6, _ = af.coefficients(math.radians(4), 1e6, 0.6)
    assert cl6 == pytest.approx(cl0 / math.sqrt(1 - 0.36), rel=1e-9)
