"""Units, propulsion, aircraft model and ISA — checked against Anderson (2017) where possible."""
import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from aerokit import units as U
from aerokit.aero import atmosphere as A
from aerokit.aero import performance as P
from aerokit.aero.aircraft import Aircraft
from aerokit.aero.propulsion import Turbofan, Turboprop, lapse_ratio
from aerokit.verification import check, check_true, expect_error

ANDERSON_D = "Anderson 2017, Fundamentals of Aerodynamics 6th ed., Appendix D (PDF pp. 1118-1121)"
# (geometric h_G, geopotential h, T [K], p [Pa], rho [kg/m3]) as printed in Appendix D
APPENDIX_D = [(1000, 1000, 281.66, 8.9876e4, 1.1117), (3000, 2999, 268.67, 7.0121e4, 0.90926),
              (5000, 4996, 255.69, 5.4048e4, 0.73643), (10000, 9984, 223.26, 2.6500e4, 0.41351),
              (11000, 10981, 216.78, 2.2700e4, 0.36480), (15000, 14965, 216.66, 1.2112e4, 0.19475)]


def test_isa_matches_anderson_appendix_d():
    for hg, h, T, p, rho in APPENDIX_D:
        check(f"geopotential altitude of h_G = {hg} m", A.geopotential_altitude(hg), h, atol=0.6, source=ANDERSON_D)
        d = A.isa(A.geopotential_altitude(hg))
        check(f"ISA T at h_G = {hg} m", d["T"], T, rtol=1e-4, source=ANDERSON_D)
        check(f"ISA p at h_G = {hg} m", d["p"], p, rtol=2e-4, source=ANDERSON_D)
        check(f"ISA rho at h_G = {hg} m", d["rho"], rho, rtol=2e-4, source=ANDERSON_D)
    check("geometric ↔ geopotential round trip", A.geometric_altitude(A.geopotential_altitude(12345.0)), 12345.0,
          rtol=1e-12)


@pytest.mark.parametrize("text, dim, si", [
    ("1300 km", "length", 1.3e6), ("10 000 [m]", "length", 1e4), ("1,300 km", "length", 1.3e6),
    ("150 km/h", "speed", 150 / 3.6), ("100 ft/min", "speed", 0.508), ("30 min", "time", 1800.0),
    ("200 kg", "mass", 200.0), ("1667 kW", "power", 1.667e6), ("0.5 lb/(hp*h)", "psfc", 8.2849e-7),
    ("60 deg", "angle", math.pi / 3), ("5 %", "dimensionless", 0.05), ("10 m/s", "speed", 10.0),
])
def test_unit_parsing(text, dim, si):
    assert U.parse(text, dim) == pytest.approx(si, rel=1e-4)


@pytest.mark.parametrize("text, dim", [("10.000 m", "length"), ("150 km", "speed"), ("3 furlong", "length"),
                                       ("12,5 m", "length"), ("inf m", "length"), ("abc", "length"),
                                       ("200 lb", "force"), ("1 m", "volume")])
def test_unit_errors(text, dim):
    with pytest.raises(U.UnitError):
        U.parse(text, dim)


def test_unit_mapping_rejects_unknown_keys():
    with pytest.raises(U.UnitError):
        U.parse_mapping({"rnage": "1300 km"}, {"range": "length"})
    assert U.parse_mapping({"range": "1300 km"}, {"range": "length"}) == {"range": 1.3e6}


@settings(max_examples=100, deadline=None)
@given(st.floats(min_value=1e-3, max_value=1e7, allow_nan=False))
def test_unit_round_trip(x):
    for dim, unit in (("length", "nmi"), ("speed", "kt"), ("power", "hp"), ("psfc", "lb/(hp*h)")):
        assert U.parse(f"{U.to_unit(x, unit, dim)!r} {unit}", dim) == pytest.approx(x, rel=1e-12)


def _rehearsal():
    return Aircraft("rehearsal", 5974 * 9.80665, 27.5, 9.0, 0.0280, 0.783, Turboprop(1667e3),
                    CLmax_clean=1.5, CLmax_takeoff=1.7, CLmax_landing=2.0)


def test_aircraft_polar_and_speeds():
    ac = _rehearsal()
    check("L/Dmax = 1/(2√(CD0 K)) of the rehearsal polar", ac.LD_max, 14.06, rtol=1e-3,
          source="docs/04 §1 (L/Dmax 14.1)")
    V = P.speed_max_LD(ac, 3000.0)
    check("drag at V(L/D)max = W/(L/D)max", ac.drag(V, 3000.0), ac.W0 / ac.LD_max, rtol=1e-12, source="derivation")
    Vp = P.speed_min_power(ac, 3000.0)
    check("V_minP = V_(L/D)max / 3^(1/4)", Vp, V / 3 ** 0.25, rtol=1e-12, source="derivation")
    check("stall speed at CLmax landing = requirement 150 km/h", ac.stall_speed(0.0, CLmax=2.0) * 3.6, 150.0,
          rtol=2e-3, source="Ansys 2023 card; sized by aerokit sizing raymer")


def test_fuel_flow_units():
    ac = _rehearsal()
    hand = 0.5 * 0.45359237 / 0.74569987 * ac.power_required(140, 3000) / 0.8 / 1e3     # kg/h by hand
    check("fuel flow = psfc · P_req/η (0.5 lb/(hp·h))", ac.fuel_flow(140, 3000) * 3600 / 9.80665, hand, rtol=1e-6,
          source="hand calculation (a hand-typed default was once 10× wrong)")


def test_rehearsal_climb_cross_check():
    ac = _rehearsal()
    check_true("SL max ROC above the 10 m/s requirement", P.max_rate_of_climb(ac, 0.0) > 10.0)
    check("max ROC at 10 000 m ≈ 0.508 m/s (sized to the service ceiling)", P.max_rate_of_climb(ac, 10000.0), 0.508,
          rtol=0.05, source="constraint diagram: ceiling governs (docs/04 §1)")


def test_engine_models():
    tp = Turboprop(1e6, lapse="sigma^n", n=0.7)
    check("σ^0.7 lapse at 5 km", tp.shaft_power(5000.0) / 1e6, A.sigma(5000.0) ** 0.7, rtol=1e-12)
    check("table lapse interpolation", lapse_ratio(500.0, "table", table=((0, 1.0), (1000, 0.9))), 0.95)
    tf = Turbofan(20e3)
    check("turbofan thrust power = T V", tf.thrust_power(100.0, 0.0), 2e6, rtol=1e-12)
    expect_error("propeller thrust at V = 0 rejected", tp.thrust, 0.0, 0.0, error=ValueError)
    expect_error("unknown lapse model rejected", lapse_ratio, 0.0, "magic", error=ValueError)
    expect_error("efficiency above 1 rejected", Turboprop, 1e6, 1.2, error=ValueError)
    expect_error("fuel ≥ W0 rejected", Aircraft, "x", 1e4, 10, 8, 0.03, 0.8, tp, W_fuel=2e4, error=ValueError)
    expect_error("e > 1 rejected", Aircraft, "x", 1e4, 10, 8, 0.03, 1.2, tp, error=ValueError)
