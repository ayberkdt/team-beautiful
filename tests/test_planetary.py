"""Venus atmosphere, buoyancy, gravity-aware rotor sizing and light time (aerokit.planetary)."""
import math

from aerokit import planetary as P
from aerokit.design import electric as E
from aerokit.verification import check, check_true, expect_error

WV = "Wikipedia 'Atmosphere of Venus' table (read 2026-11-03)"


def test_table_nodes_and_ideal_gas():
    s = P.venus_atmosphere(0.0)
    check("surface T = 462 °C", s.T, 735.15, rtol=1e-12, source=WV)
    check("surface p = 92.10 bar", s.p, 92.10e5, rtol=1e-12, source=WV)
    check("ideal-gas surface density p M / (R T)", s.rho, 92.10e5 * P.M_VENUS / (P.R_UNIVERSAL * 735.15), rtol=1e-12)
    check("mean molar mass 96.5 % CO2 + 3.5 % N2", P.M_VENUS, 43.4497e-3, rtol=1e-4)
    s55 = P.venus_atmosphere(55e3)
    check("55 km: 27 °C", s55.T, 300.15, rtol=1e-12, source=WV)
    check("55 km: 0.5314 bar", s55.p, 0.5314e5, rtol=1e-12, source=WV)
    mid = P.venus_atmosphere(52.5e3)
    check("ln p interpolated halfway between 50 and 55 km", mid.p, math.sqrt(1.066e5 * 0.5314e5), rtol=1e-12)
    check_true("52.5 km temperature inside 293–310 K quoted for 52.5–54 km", 293 <= mid.T <= 330, mid.T,
               source=WV)
    expect_error("above 100 km refused", P.venus_atmosphere, 101e3, error=ValueError)


def test_inverse_lookups_and_gravity():
    check("1 bar between the 50 km (1.066) and 55 km nodes", P.altitude_for_pressure(1e5),
          50e3 + 5e3 * math.log(1.066 / 1.0) / math.log(1.066 / 0.5314), rtol=1e-12)
    check("round trip T → h → T", P.venus_atmosphere(P.altitude_for_temperature(320.0)).T, 320.0, rtol=1e-12)
    check("g(0) = 8.87", P.venus_gravity(0.0), 8.87, rtol=1e-12, source="Wikipedia 'Venus'")
    check("inverse square at 55 km", P.venus_gravity(55e3), 8.87 * (6051.8 / 6106.8) ** 2, rtol=1e-12)


def test_buoyancy():
    s = P.venus_atmosphere(55e3)
    lift_h2 = P.buoyant_lift_per_m3(55e3, P.M_H2)
    check("H2 lift (ρ_atm − ρ_H2) g", lift_h2, s.rho * (1 - P.M_H2 / P.M_VENUS) * s.g, rtol=1e-12)
    check_true("Earth air is a lifting gas on Venus", P.buoyant_lift_per_m3(55e3, P.M_AIR_EARTH) > 0)
    check_true("CO2 does not lift", P.buoyant_lift_per_m3(55e3, P.M_CO2) < 0)
    check_true("superheat adds lift", P.buoyant_lift_per_m3(55e3, P.M_HE, 10.0) > P.buoyant_lift_per_m3(55e3, P.M_HE))
    check("volume floats the mass", P.balloon_volume(100.0, 55e3, P.M_H2) * lift_h2, 100.0 * s.g, rtol=1e-12)
    expect_error("CO2 balloon refused", P.balloon_volume, 10.0, 55e3, P.M_CO2, error=ValueError)


def test_rotor_and_wing_on_venus():
    s = P.venus_atmosphere(55e3)
    pe = E.hover_power(5 * 9.80665, 1.225, 0.5, 0.7)
    pv = E.hover_power(5 * s.g, s.rho, 0.5, 0.7)
    check("hover power scales as (g)^1.5 / sqrt(rho)", pv / pe, (s.g / 9.80665) ** 1.5 * math.sqrt(1.225 / s.rho),
          rtol=1e-12)
    sz = E.size_multirotor(0.5, 600, 4, 0.5, specific_energy_J_kg=150 * 3600, efficiency=0.7, figure_of_merit=0.65,
                           empty_fraction=0.5, rho=s.rho, g=s.g)
    check("multirotor weight / disk area uses local g", sz.disk_loading, sz.mass * s.g / (4 * math.pi * 0.0625),
          rtol=1e-12)
    v = P.level_flight_speed(10.0, 2.0, 0.8, s.rho, s.g)
    check("level flight lift = weight", 0.5 * s.rho * v ** 2 * 2.0 * 0.8, 10.0 * s.g, rtol=1e-12)
    check("power m g V / (L/D η)", P.level_flight_power(10.0, v, 15.0, 0.6, s.g), 10 * s.g * v / 9.0, rtol=1e-12)


def test_time_scales():
    check("100 m/s at 60 km: ~4.4 days round Venus", P.circumnavigation_time(100.0, 60e3) / 86400.0,
          2 * math.pi * 6111.8e3 / 100.0 / 86400.0, rtol=1e-12)
    lo, hi = P.light_time_bounds()
    check("min light time 0.2767 AU / c", lo, (1 - 0.723332) * 149_597_870_700.0 / 299_792_458.0, rtol=1e-12)
    check_true("max light time ~14.3 min", 14.0 < hi / 60 < 14.6, hi / 60)


def test_wind_and_light_profiles():
    check("wind anchor 60 km", P.venus_zonal_wind(60e3), 100.0, rtol=1e-12)
    check("wind midway 45-53 km", P.venus_zonal_wind(49e3), (44.5 + 65.0) / 2, rtol=1e-12)
    check("light 0.35 at 50 km", P.venus_solar_fraction(50e3), 0.35, rtol=1e-12)
    check("light 1 above 65 km", P.venus_solar_fraction(70e3), 1.0, rtol=1e-12)
    expect_error("no sourced light below 50 km", P.venus_solar_fraction, 40e3, error=ValueError)
    check("solar power 1 m² at 65 km, η 1, sub-solar", P.solar_power(1.0, 1.0, 65e3, sun_factor=1.0),
          P.VENUS_SOLAR_FLUX_TOP * 0.95, rtol=1e-12)
    check("bifacial adds the upward share", P.solar_power(1.0, 0.2, 60e3, upward_ratio=0.9),
          1.9 * P.solar_power(1.0, 0.2, 60e3), rtol=1e-12)


def test_assisted_hover_and_drag():
    from aerokit.design.electric import hover_power
    s = P.venus_atmosphere(55e3)
    check("no gas = plain hover", P.assisted_hover_power(10.0, 55e3, P.M_HE, 0.0, 1.0, 0.7),
          hover_power(10.0 * s.g, s.rho, 1.0, 0.7), rtol=1e-12)
    v_float = P.balloon_volume(10.0, 55e3, P.M_HE)
    check("cell that floats the vehicle → 0 W", P.assisted_hover_power(10.0, 55e3, P.M_HE, v_float, 1.0), 0.0)
    half = P.assisted_hover_power(10.0, 55e3, P.M_HE, 0.5 * v_float, 1.0, 0.7)
    check("half buoyancy → (1/2)^1.5 of the power", half, 0.5 ** 1.5 * hover_power(10.0 * s.g, s.rho, 1.0, 0.7),
          rtol=1e-9)
    r = (3 * 100.0 / (4 * math.pi)) ** (1 / 3)
    check("drag power ½ρV³C_D πr²", P.envelope_drag_power(100.0, 10.0, 55e3, 0.3),
          0.5 * s.rho * 1000.0 * 0.3 * math.pi * r * r, rtol=1e-12)
