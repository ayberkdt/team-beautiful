"""Battery-electric fixed-wing and multirotor sizing (aerokit.design.electric)."""
import math

import pytest

from aerokit.design import electric as E
from aerokit.verification import check, check_true, expect_error

WH = E.WH_PER_KG
HEP = "Hepperle 2012 slides 16-20 (variables and limit cases; equations derived here)"


def test_range_equation_closed_form():
    r = E.battery_range(180 * WH, 0.7, 30.0, 0.5)
    check("R = E* η (L/D)(m_b/m) / g", r, 180 * 3600 * 0.7 / 9.80665 * 30 * 0.5, rtol=1e-12, source=HEP)
    check("range is linear in the battery fraction", E.battery_range(180 * WH, 0.7, 30.0, 0.25), r / 2, rtol=1e-12)


def test_sizing_is_the_inverse_of_the_range_equation():
    s = E.electric_takeoff_mass(360.0, 500e3, 180 * WH, 0.7, 30.0, 0.4)
    check("sized battery fraction flies exactly the range", E.battery_range(180 * WH, 0.7, 30.0, s["battery_fraction"]),
          500e3, rtol=1e-12)
    check("mass balance m = payload + empty + battery", s["mass"], 360 + s["empty_mass"] + s["battery_mass"],
          rtol=1e-12)
    r0 = E.electric_takeoff_mass(360.0, 0.0, 180 * WH, 0.7, 30.0, 0.4)
    check("R = 0 gives the minimum mass payload/(1 − m_e/m)", r0["mass"], 360 / 0.6, rtol=1e-12, source=HEP)


def test_payload_zero_limit_cannot_be_exceeded():
    rmax = E.max_range_payload_zero(180 * WH, 0.7, 30.0, 0.4)
    check("R_max = (E* η / g)(L/D)(1 − m_e/m)", rmax, 180 * 3600 * 0.7 / 9.80665 * 30 * 0.6, rtol=1e-12, source=HEP)
    expect_error("beyond R_max: no design", E.electric_takeoff_mass, 100.0, 1.001 * rmax, 180 * WH, 0.7, 30.0, 0.4,
                 error=ValueError)
    near = E.electric_takeoff_mass(100.0, 0.99 * rmax, 180 * WH, 0.7, 30.0, 0.4)
    check_true("just below R_max the mass explodes", near["mass"] > 50 * 100.0, near["mass"])


def test_endurance_and_hover_power():
    check("t = E* m_b η / P", E.battery_endurance(2.0, 200 * WH, 0.8, 400.0), 200 * 3600 * 2 * 0.8 / 400, rtol=1e-12)
    T, rho, A = 100.0, 1.225, 0.5
    vi = math.sqrt(T / (2 * rho * A))
    check("v_i = √(T/(2ρA))", E.induced_velocity(T, rho, A), vi, rtol=1e-12)
    check("P_ideal = T v_i", E.hover_power(T, rho, A), T * vi, rtol=1e-12)
    check("figure of merit divides the ideal power", E.hover_power(T, rho, A, 0.7), T * vi / 0.7, rtol=1e-12)
    check("P ∝ T^1.5", E.hover_power(2 * T, rho, A) / E.hover_power(T, rho, A), 2 ** 1.5, rtol=1e-12)
    check("P ∝ 1/√A", E.hover_power(T, rho, 2 * A) / E.hover_power(T, rho, A), 1 / math.sqrt(2), rtol=1e-12)
    expect_error("FM > 1 rejected", E.hover_power, T, rho, A, 1.2, error=ValueError)


def test_multirotor_fixed_point_satisfies_its_equations():
    kw = dict(specific_energy_J_kg=200 * WH, efficiency=0.85, figure_of_merit=0.7, empty_fraction=0.45)
    s = E.size_multirotor(5.0, 1200.0, 4, 0.6, **kw)
    area = 4 * math.pi * 0.3 ** 2
    P = E.hover_power(s.mass * 9.80665, 1.225, area, 0.7)
    check("hover power at the sized mass", s.hover_power, P, rtol=1e-9)
    check("battery = P t / (E* η)", s.battery_mass, P * 1200 / (200 * 3600 * 0.85), rtol=1e-9)
    check("m = (payload + battery)/(1 − m_e/m)", s.mass, (5.0 + s.battery_mass) / 0.55, rtol=1e-6)
    longer = E.size_multirotor(5.0, 1400.0, 4, 0.6, **kw)
    check_true("longer hover → heavier", longer.mass > s.mass)
    # 30 min with these values: f(m*) = 0.55 m* − 5 − k m*^1.5 < 0 at m* ≈ 22 kg (checked by hand) → no design
    expect_error("30 min hover out of reach with 0.6 m rotors", E.size_multirotor, 5.0, 1800.0, 4, 0.6,
                 error=ValueError, **kw)


def test_input_validation():
    for args in [(0.0, 0.7, 30, 0.5), (180 * WH, 0.0, 30, 0.5), (180 * WH, 0.7, -1, 0.5), (180 * WH, 0.7, 30, 1.0)]:
        with pytest.raises(ValueError):
            E.battery_range(*args)
