"""Entry physics: arrival speed, Allen-Eggers limit, Pioneer Venus large-probe trajectory, heating constants."""
from __future__ import annotations

import math

import numpy as np
import pytest

from aerokit.venus import entry as E


def test_hohmann_vinf_and_entry_speed():
    vinf = E.hohmann_vinf()
    assert 2600 < vinf < 2800                    # textbook ~2.7 km/s
    ve = E.entry_speed(vinf, 200e3)
    assert ve == pytest.approx(math.sqrt(vinf ** 2 + 2 * E.MU_VENUS / (6051.8e3 + 200e3)))
    assert 10.4e3 < ve < 10.7e3


@pytest.mark.parametrize("gamma", [-30.0, -45.0])
def test_allen_eggers_peak_deceleration_for_steep_entry(gamma):
    H, rho0 = 7000.0, 65.0
    veh = E.EntryVehicle(300.0, 1.42, 1.05)
    r = E.fly_entry(veh, 11000.0, gamma, h0=200e3, dt=0.01, density_fn=lambda h: rho0 * math.exp(-h / H))
    assert r.peak_g == pytest.approx(E.allen_eggers_peak_g(11000.0, gamma, H), rel=0.03)


def test_pioneer_venus_large_probe_trajectory_matches_published_points():
    """Tauber, Palmer & Prabhu 2012 Table 1 (via research note D_tauber_venus_rad_2012): β 190 kg/m², 11.584 km/s,
    −31.829° at 137.78 km; (t, V, h) points of their trajectory and the peak radiative flux 2449 W/cm²."""
    m, d = 316.0, 1.42
    veh = E.EntryVehicle(m, d, m / (190.0 * math.pi * d * d / 4.0), nose_radius_m=0.363)
    r = E.fly_entry(veh, 11584.0, -31.829, h0=137.78e3, dt=0.005)
    for t, V, h in ((8.0, 11310.0, 89.24e3), (8.6, 10880.0, 85.77e3), (9.2, 10028.0, 82.49e3), (10.4, 7015.0, 77.12e3)):
        i = int(np.argmin(abs(r.t - t)))
        assert r.V[i] == pytest.approx(V, rel=0.01)
        assert r.h[i] == pytest.approx(h, abs=200.0)
    assert np.nanmax(r.q_rad) / 1e4 == pytest.approx(2449.0, rel=0.05)
    assert 250 < r.peak_g < 320                 # SP-461: 280 g; Venkatapathy 2016: 276 g (agent notes)


def test_sutton_graves_constants():
    assert E.K_SUTTON_GRAVES_VENUS == pytest.approx(1.897e-4, rel=1e-3)
    # same conversion for Earth air K = 0.1113 gives the textbook 1.74e-4
    assert 0.1113 / (2 * 101325 ** 0.5) == pytest.approx(1.748e-4, rel=1e-3)
    q = E.sutton_graves(1e-3, 10000.0, 1.0)
    assert q == pytest.approx(1.897e-4 * math.sqrt(1e-3) * 1e12, rel=1e-3)


def test_tauber_radiative_reproduces_table_points():
    # inputs/outputs of Table 1 (agent re-evaluation): (V, rho) -> W/cm² with r_N 0.363 m
    assert E.tauber_radiative(3.26e-3, 10880.0, 0.363) / 1e4 == pytest.approx(2450.0, rel=0.01)
    assert E.tauber_radiative(2.13e-2, 7015.0, 0.363) / 1e4 == pytest.approx(318.0, rel=0.02)
    with pytest.raises(ValueError):
        E.tauber_radiative(1e-3, 13000.0, 0.5)


def test_shallow_entry_lowers_peak_g():
    veh = E.EntryVehicle(150.0, 1.6, 1.05, nose_radius_m=0.5)
    steep = E.fly_entry(veh, 10800.0, -30.0)
    shallow = E.fly_entry(veh, 10800.0, -10.0)
    assert shallow.peak_g < 0.5 * steep.peak_g
    assert shallow.stop_reason == "stop speed"


@pytest.mark.parametrize("beta,gamma,V,D,shape,g_ref", [
    (367, -20.5, 10.7, 2.4, "sphere", 150),      # Venera 9  (Dutta et al. 2012 Table 1, via agent note)
    (412, -18.23, 10.7, 2.4, "sphere", 130),     # Vega 1
    (190, -41.5, 11.5, 0.7653, "cone45", 350),   # PV Night
    (188, -32.4, 11.5, 1.4228, "cone45", 276),   # PV Large
])
def test_historical_entries_peak_g_within_10_percent(beta, gamma, V, D, shape, g_ref):
    rn = D / 2 if shape == "sphere" else D / 4
    m = beta * 1.05 * math.pi * D * D / 4
    r = E.fly_entry(E.EntryVehicle(m, D, 1.05, nose_radius_m=rn), V * 1e3, gamma, h0=200e3, dt=0.01)
    assert r.peak_g == pytest.approx(g_ref, rel=0.10)


def test_davinci_needs_its_145_km_interface():
    veh = E.EntryVehicle(100.0 * 1.05 * math.pi * 2.24 ** 2 / 4, 2.24, 1.05, nose_radius_m=0.56)
    skip = E.fly_entry(veh, 10.4e3, -6.3, h0=200e3)
    ok = E.fly_entry(veh, 10.4e3, -6.3, h0=145e3)
    assert skip.peak_g < 1.0                                     # grazes and skips out at a 200 km interface
    assert ok.peak_g == pytest.approx(32.0, rel=0.15)            # published 32 g
