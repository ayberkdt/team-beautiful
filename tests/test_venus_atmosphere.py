"""Venus atmosphere from Pioneer Venus data, CO2 properties, solar model."""
from __future__ import annotations

import math

import pytest

from aerokit import planetary as P
from aerokit.venus import atmosphere as A
from aerokit.venus import gas
from aerokit.venus import power as PW


def test_pv_mean_at_55_km_matches_agent_table_and_ideal_gas():
    s = A.state(55e3)
    assert s.T == pytest.approx(299.1, abs=0.2)          # A_00_index (agent) = own extraction
    assert s.p / 1e5 == pytest.approx(0.508, abs=0.002)
    assert s.rho == pytest.approx(0.889, abs=0.002)
    assert s.rho == pytest.approx(s.p / (gas.R_SPECIFIC * s.T), rel=0.01)


def test_vira_like_table_sits_at_dense_edge_of_probe_envelope():
    for km in (50, 52, 54, 55, 56, 58, 60):
        h = km * 1e3
        lo, hi = A.state(h, "min").rho, A.state(h, "max").rho
        assert lo <= A.state(h).rho <= hi
        assert P.venus_atmosphere(h).rho >= A.state(h).rho


def test_bands_and_cases_are_ordered():
    h = 55e3
    assert A.state(h, "thin").rho < A.state(h).rho < A.state(h, "dense").rho
    lo, mid, hi = A.zonal_wind_band(h)
    assert lo < mid < hi
    assert 55 < mid < 75                                 # VEGA 66-69 m/s at 53-54 km (agent)
    assert A.meridional_wind_max(h) < 10


def test_near_adiabatic_middle_cloud():
    """Agent finding: lapse rate ≈ adiabatic (9.8-10.4 K/km) at 51-56 km. Adiabatic g/cp computed here."""
    s = A.state(53.5e3)
    cp_mass = gas.cp_molar(s.T) / gas.M_MIX
    adiabatic = s.g / cp_mass * 1e3                      # K/km
    lapse = (A.state(51e3).T - A.state(56e3).T) / 5.0
    assert lapse == pytest.approx(adiabatic, abs=1.2)


def test_out_of_range_raises():
    with pytest.raises(ValueError):
        A.state(35e3)


def test_co2_properties_against_nist():
    # NIST CO2 at 300 K, 0.1 MPa: a 269.39 m/s (pure CO2); our mixture has 3.5 % N2 -> slightly faster
    assert gas.speed_of_sound(300.0) == pytest.approx(269.39, rel=0.015)
    assert gas.viscosity(300.0) == pytest.approx(15.003e-6, rel=1e-6)
    assert gas.viscosity(312.5) == pytest.approx(0.5 * (15.003e-6 + 16.191e-6), rel=1e-6)
    assert 1.28 < gas.gamma(300.0) < 1.31


def test_solar_model_nodes_and_crosscheck():
    assert PW.array_output_overhead(55e3) == pytest.approx(404.4, rel=1e-6)
    assert PW.array_output_overhead(60e3) == pytest.approx(559.2, rel=1e-6)
    # independent shape check: Landis-Haag 55/60 vs PV LSFR downward flux 55/60 within 10 %
    lh = 404.4 / 559.2
    lsfr = A.solar_down_relative(55e3) / A.solar_down_relative(60e3)
    assert lh == pytest.approx(lsfr, rel=0.10)
    assert 0.8 < A.solar_ratio_up_down(55e3) < 0.95
    assert PW.sun_factor(1.0) == pytest.approx(1.0)
    assert PW.sun_factor(0.0) == 0.0


def test_air_mass_day_length():
    d = PW.air_mass_day_s(65.0, 55e3) / 86400
    assert 6.0 < d < 7.0
    still = PW.air_mass_day_s(0.0, 55e3) / 86400
    assert still == pytest.approx(116.75, rel=1e-6)
    assert math.isclose(float(PW.mu0_history([0.0], 65.0, 55e3)[0]), 0.0, abs_tol=1e-12)
