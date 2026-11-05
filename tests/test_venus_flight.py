"""Time-stepped Venus drone flight (aerokit.venus_flight)."""
from dataclasses import replace

import numpy as np

from aerokit import planetary as P
from aerokit import venus_flight as V
from aerokit.design.electric import hover_power
from aerokit.verification import check, check_true, expect_error

D = V.VenusDrone()


def test_float_altitude_and_thrust_limit():
    h = V.float_altitude(D)
    check("lift = weight at the float altitude", P.buoyant_lift_per_m3(h, P.M_HE) * D.gas_volume_m3,
          D.mass_kg * P.venus_gravity(h), rtol=1e-6)
    rho = P.venus_atmosphere(55e3).rho
    T = V.max_thrust(D, rho)
    check("T_max inverts hover power at the power limit",
          hover_power(T, rho, D.rotor_area_m2, D.figure_of_merit) / D.electrical_efficiency + D.avionics_W,
          D.max_power_W, rtol=1e-9)
    expect_error("cell far too small", V.float_altitude, replace(D, gas_volume_m3=0.1), error=ValueError)


def test_unpowered_vehicle_settles_at_float_altitude_and_drifts_with_the_wind():
    glider = replace(D, max_power_W=D.avionics_W)          # no rotor power at all
    r = V.simulate_mission(glider, [{"hold": 55, "for_s": 6 * 3600}], 55.0, dt=1.0)
    check("settles at the float altitude (within 100 m)", r.z[-1], V.float_altitude(D), atol=100.0)
    check("moves with the air mass", r.u[-1] - r.wind[-1], 0.0, atol=0.05)
    check_true("rotors never produced thrust", np.all(r.thrust == 0.0))


def test_energy_bookkeeping():
    big = replace(D, battery_Wh=1e5, solar_area_m2=0.0)
    r = V.simulate_mission(big, [{"hold": 55, "for_s": 1800}], 55.0, dt=0.5)
    used = np.sum(r.power) * 0.5 / 3600.0
    check("battery drop = integral of the electrical power", big.battery_Wh - r.energy_Wh[-1], used, rtol=1e-9)


def test_dive_mission_events_and_thermal_limit():
    mission = [{"goto": 48, "rate": 3}, {"hold": 48, "for_s": 1800}, {"goto": 55, "rate": 3}]
    r = V.simulate_mission(D, mission, 55.0)
    names = [e[1] for e in r.events]
    check_true("events in mission order", names == ["reached 48.0 km", "held 48.0 km for 1800 s", "reached 55.0 km"])
    check_true("30 min at 48 km overheats the 70 C electronics", r.time_over_temp_s > 0)
    short = V.simulate_mission(D, [{"goto": 52, "rate": 3}, {"hold": 52, "for_s": 600}, {"goto": 55, "rate": 3}],
                               55.0)
    check("a 52 km dip stays within the limit", short.time_over_temp_s, 0.0)
    frames = V.replay(short, every_s=1.0)
    check_true("replay ~1 Hz", abs(len(frames) - short.t[-1]) <= 2)
    expect_error("bad mission step", V.simulate_mission, D, [{"fly": 50}], 55.0, error=ValueError)
