"""Venus environment and first-order sizing of aerial platforms there (balloons, rotorcraft, aeroplanes).

**Atmosphere.** The temperature/pressure table (0–100 km, 5–10 km steps) is the one printed in Wikipedia's
"Atmosphere of Venus" (read 2026-11-03), whose numbers are those usually quoted from the Venus International
Reference Atmosphere (VIRA). Between nodes the temperature is interpolated linearly and ``ln p`` linearly (an
isothermal-layer approximation); the density follows from the ideal-gas law with the mean molar mass of
96.5 % CO₂ + 3.5 % N₂ (43.45 g/mol). Two known limits, both stated rather than hidden:

* the table's pressure column is labelled "atm" on the page; VIRA uses bar. The 1.3 % difference is below the
  day/night and latitude spread of the real atmosphere; :data:`PRESSURE_UNIT_PA` makes the choice explicit (bar).
* CO₂ at 92 bar and 735 K is not quite ideal; the ideal-gas surface density (≈ 65 kg/m³) is a few per cent
  off. Use it for sizing, not for an entry-probe heat-shield.

**Lift.** A zero-pressure balloon at the ambient ``p, T`` lifts ``(ρ_atm − ρ_gas) V g`` with
``ρ_gas = p M_gas / (R T)``. Because the Venus atmosphere is mostly CO₂ (44 g/mol), even nitrogen or Earth air is
a lifting gas there. Rotor hover power uses actuator-disk momentum theory (``aerokit.design.electric``); a
denser atmosphere lowers the induced power as ``1/√ρ``, gravity is 0.904 g₀.

**Time and light.** The super-rotating cloud layer (~100 m/s at the cloud tops) carries a free-floating platform
round the planet in a few Earth days; :func:`circumnavigation_time` gives the number for any wind. One-way light
time Earth–Venus is bounded with circular coplanar orbits by :func:`light_time_bounds`.

**Wind and light profiles.** :func:`venus_zonal_wind` and :func:`venus_solar_fraction` interpolate the sourced
anchor values in :data:`ZONAL_WIND_ANCHORS` and :data:`SOLAR_FRACTION_ANCHORS` (Landis 2001/2002 and VAPS 2018,
read by the research agent). Linear interpolation between anchors is *our assumption*; below 50 km the light
level is not sourced and the function refuses.

**Buoyancy-assisted rotorcraft.** :func:`assisted_hover_power` subtracts the lift of a gas cell from the weight
before the momentum-theory hover power; :func:`envelope_drag_power` is the power to push a spherical envelope
through the air at a given airspeed, ``½ ρ V³ C_D π r²`` — the reason a balloon cannot hold station against the
super-rotation and lives in the air-mass frame instead.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from aerokit.references import cite

__all__ = ["R_UNIVERSAL", "M_CO2", "M_N2", "M_HE", "M_H2", "M_AIR_EARTH", "M_VENUS", "PRESSURE_UNIT_PA",
           "VENUS_RADIUS", "VENUS_G0", "VENUS_SOLAR_FLUX_TOP", "VENUS_SIDEREAL_DAY_S", "VENUS_SOLAR_DAY_S",
           "VENUS_SEMI_MAJOR_AU", "AU", "C_LIGHT", "VIRA_TABLE", "VenusState", "venus_atmosphere",
           "venus_gravity", "altitude_for_pressure", "altitude_for_temperature", "gas_density",
           "buoyant_lift_per_m3", "balloon_volume", "level_flight_speed", "level_flight_power",
           "circumnavigation_time", "light_time_bounds", "ZONAL_WIND_ANCHORS", "SOLAR_FRACTION_ANCHORS",
           "venus_zonal_wind", "venus_solar_fraction", "assisted_hover_power", "envelope_drag_power",
           "solar_power"]

R_UNIVERSAL = 8.314462618        # J/(mol K), exact (SI 2019)
M_CO2 = 44.0095e-3               # kg/mol
M_N2 = 28.0134e-3
M_HE = 4.002602e-3
M_H2 = 2.01588e-3
M_AIR_EARTH = 0.78084 * M_N2 + 0.20946 * 31.9988e-3 + 0.00934 * 39.948e-3   # dry air, major species only
M_VENUS = 0.965 * M_CO2 + 0.035 * M_N2                                    # 43.45 g/mol
PRESSURE_UNIT_PA = 1.0e5          # the table's pressure unit taken as bar (see module docstring)

VENUS_RADIUS = 6051.8e3           # m
VENUS_G0 = 8.87                   # m/s², surface
VENUS_SOLAR_FLUX_TOP = 2600.0     # W/m², above the atmosphere
VENUS_SIDEREAL_DAY_S = 243.0226 * 86400.0
VENUS_SOLAR_DAY_S = 116.75 * 86400.0
VENUS_SEMI_MAJOR_AU = 0.723332
AU = 149_597_870_700.0            # m
C_LIGHT = 299_792_458.0           # m/s

# (altitude km, temperature °C, pressure in PRESSURE_UNIT_PA) as printed on the cited page
VIRA_TABLE: tuple[tuple[float, float, float], ...] = (
    (0, 462, 92.10), (5, 424, 66.65), (10, 385, 47.39), (15, 348, 33.04), (20, 306, 22.52), (25, 264, 14.93),
    (30, 222, 9.851), (35, 180, 5.917), (40, 143, 3.501), (45, 110, 1.979), (50, 75, 1.066), (55, 27, 0.5314),
    (60, -10, 0.2357), (65, -30, 0.09765), (70, -43, 0.03690), (80, -76, 0.004760), (90, -104, 0.0003736),
    (100, -112, 0.00002660),
)
_H = np.array([r[0] for r in VIRA_TABLE]) * 1e3
_T = np.array([r[1] for r in VIRA_TABLE]) + 273.15
_LNP = np.log(np.array([r[2] for r in VIRA_TABLE]) * PRESSURE_UNIT_PA)


@dataclass(frozen=True)
class VenusState:
    """Ambient state at geometric altitude ``h`` [m]: temperature [K], pressure [Pa], density [kg/m³], gravity."""

    h: float
    T: float
    p: float
    rho: float
    g: float


def _check_altitude(h: float) -> None:
    if not (math.isfinite(h) and _H[0] <= h <= _H[-1]):
        raise ValueError(f"altitude {h:.0f} m outside the tabulated 0–100 km")


@cite("wikipedia_venus_2026", note="mean radius 6051.8 km, surface gravity 8.87 m/s²")
def venus_gravity(h: float) -> float:
    """Gravity at altitude ``h`` [m]: ``g₀ (R / (R + h))²``."""
    if not math.isfinite(h) or h < -VENUS_RADIUS / 2:
        raise ValueError("altitude must be finite and above the planet's centre")
    return VENUS_G0 * (VENUS_RADIUS / (VENUS_RADIUS + h)) ** 2


@cite("wikipedia_venus_atmosphere_2026", "iupac_2019_constants",
      note="table T(h), p(h); T linear and ln p linear between nodes; ideal gas with M = 43.45 g/mol")
def venus_atmosphere(h: float) -> VenusState:
    """Temperature, pressure and density of the Venus reference atmosphere at ``h`` [m] (0–100 km)."""
    _check_altitude(h)
    T = float(np.interp(h, _H, _T))
    p = float(math.exp(np.interp(h, _H, _LNP)))
    return VenusState(h, T, p, gas_density(p, T, M_VENUS), venus_gravity(h))


def _invert(values: np.ndarray, target: float, name: str) -> float:
    # values decrease monotonically with altitude in the table
    if not (values[-1] <= target <= values[0]):
        raise ValueError(f"{name} {target:g} outside the tabulated range [{values[-1]:g}, {values[0]:g}]")
    return float(np.interp(target, values[::-1], _H[::-1]))


@cite("wikipedia_venus_atmosphere_2026", note="inverse of the tabulated p(h)")
def altitude_for_pressure(p_pa: float) -> float:
    """Altitude [m] where the reference pressure equals ``p_pa`` (e.g. 1 bar ≈ 50 km)."""
    if p_pa <= 0:
        raise ValueError("pressure must be > 0")
    return _invert(_LNP, math.log(p_pa), "ln pressure")


@cite("wikipedia_venus_atmosphere_2026", note="inverse of the tabulated T(h), monotonic up to 100 km")
def altitude_for_temperature(T_K: float) -> float:
    """Altitude [m] where the reference temperature equals ``T_K`` (e.g. electronics limit)."""
    return _invert(_T, T_K, "temperature")


@cite("iupac_2019_constants", note="ideal gas ρ = p M / (R T)")
def gas_density(p_pa: float, T_K: float, molar_mass: float) -> float:
    """Ideal-gas density [kg/m³]."""
    if p_pa <= 0 or T_K <= 0 or molar_mass <= 0:
        raise ValueError("pressure, temperature and molar mass must be > 0")
    return p_pa * molar_mass / (R_UNIVERSAL * T_K)


def buoyant_lift_per_m3(h: float, gas_molar_mass: float, superheat_K: float = 0.0) -> float:
    """Net buoyant force per m³ of envelope [N/m³] at Venus altitude ``h``: ``(ρ_atm − ρ_gas) g``.

    The gas is at ambient pressure (zero-pressure balloon); ``superheat_K`` warms it above ambient (solar heating).
    """
    s = venus_atmosphere(h)
    rho_gas = gas_density(s.p, s.T + superheat_K, gas_molar_mass)
    return (s.rho - rho_gas) * s.g


def balloon_volume(mass_kg: float, h: float, gas_molar_mass: float, superheat_K: float = 0.0) -> float:
    """Envelope volume [m³] that floats ``mass_kg`` (envelope, gas excluded, plus gondola) at altitude ``h``."""
    if mass_kg <= 0:
        raise ValueError("mass must be > 0")
    lift = buoyant_lift_per_m3(h, gas_molar_mass, superheat_K)
    if lift <= 0:
        raise ValueError("this gas does not lift in the Venus atmosphere at this altitude")
    return mass_kg * venus_gravity(h) / lift


def level_flight_speed(mass_kg: float, wing_area_m2: float, CL: float, rho: float, g: float = VENUS_G0) -> float:
    """Speed [m/s] for lift = weight: ``√(2 m g / (ρ S C_L))``."""
    if min(mass_kg, wing_area_m2, CL, rho, g) <= 0:
        raise ValueError("all inputs must be > 0")
    return math.sqrt(2.0 * mass_kg * g / (rho * wing_area_m2 * CL))


def level_flight_power(mass_kg: float, speed: float, LD: float, efficiency: float, g: float = VENUS_G0) -> float:
    """Electrical power [W] for level flight: ``m g V / (L/D · η)``."""
    if min(mass_kg, speed, LD, g) <= 0 or not 0 < efficiency <= 1:
        raise ValueError("inputs must be > 0 and efficiency in (0, 1]")
    return mass_kg * g * speed / (LD * efficiency)


@cite("wikipedia_venus_2026", note="radius; the wind speed is an input (cloud-top ~100 m/s per the atmosphere page)")
def circumnavigation_time(wind_speed: float, h: float) -> float:
    """Time [s] for a platform drifting with a zonal wind ``wind_speed`` to circle Venus at the equator."""
    if wind_speed <= 0:
        raise ValueError("wind speed must be > 0")
    return 2.0 * math.pi * (VENUS_RADIUS + h) / wind_speed


@cite("wikipedia_venus_2026", "iupac_2019_constants", note="circular coplanar orbits: |1 ∓ a_V| AU / c")
def light_time_bounds() -> tuple[float, float]:
    """One-way light time Earth–Venus [s] at inferior and superior conjunction (circular orbits)."""
    return ((1.0 - VENUS_SEMI_MAJOR_AU) * AU / C_LIGHT, (1.0 + VENUS_SEMI_MAJOR_AU) * AU / C_LIGHT)


# (altitude km, eastward zonal wind m/s): Landis 2001 Table 1 (45, 53, 60 km), Vega balloon drift (54 km, VAPS 2018),
# Landis 2002 (cloud tops), surface 0.3-1 m/s (Landis 2001) — all read by the research agent
ZONAL_WIND_ANCHORS: tuple[tuple[float, float], ...] = ((0.0, 0.5), (45.0, 44.5), (53.0, 65.0), (54.0, 67.0),
                                                       (60.0, 100.0), (67.0, 95.0))
# (altitude km, downward solar flux / top-of-atmosphere): Landis 2002 citing Ekonomov et al. 1983 (20-50 % at the
# cloud base, 0.35 used; ~95 % at 65 km); 1.0 above 65 km is assumed
SOLAR_FRACTION_ANCHORS: tuple[tuple[float, float], ...] = ((50.0, 0.35), (65.0, 0.95))


@cite("landis_2001_venus", "landis_2002_venus", note="anchors; linear interpolation between them is an assumption")
def venus_zonal_wind(h: float) -> float:
    """Eastward zonal wind [m/s] at altitude ``h`` [m] (equatorial; constant above the highest anchor)."""
    _check_altitude(h)
    km = h / 1e3
    return float(np.interp(km, [a for a, _ in ZONAL_WIND_ANCHORS], [v for _, v in ZONAL_WIND_ANCHORS]))


@cite("landis_2002_venus", note="downward flux fraction 0.35 at 50 km, 0.95 at 65 km; 1.0 above assumed")
def venus_solar_fraction(h: float) -> float:
    """Downward solar flux as a fraction of the top-of-atmosphere value at altitude ``h`` [m], 50–100 km only."""
    _check_altitude(h)
    km = h / 1e3
    if km < SOLAR_FRACTION_ANCHORS[0][0]:
        raise ValueError("no sourced light level below 50 km")
    if km > SOLAR_FRACTION_ANCHORS[-1][0]:
        return 1.0
    return float(np.interp(km, [a for a, _ in SOLAR_FRACTION_ANCHORS], [v for _, v in SOLAR_FRACTION_ANCHORS]))


def solar_power(area_m2: float, efficiency: float, h: float, sun_factor: float = 1.0 / math.pi,
                upward_ratio: float = 0.0) -> float:
    """Mean electrical power [W] of a panel at altitude ``h``: top flux × :func:`venus_solar_fraction` × area ×
    efficiency × ``sun_factor``. The default ``1/π`` is the mean of ``max(cos θ, 0)`` over a full solar day for
    a horizontal panel at the equator (day and night); use 1.0 for the sub-solar point. ``upward_ratio`` adds the
    cloud-reflected flux collected by a bifacial panel's underside (Landis 2002: ~0.9 of the downward flux at
    60 km, via the research agent)."""
    if area_m2 < 0 or not 0 < efficiency <= 1 or sun_factor < 0 or upward_ratio < 0:
        raise ValueError("area, sun factor, upward ratio >= 0 and efficiency in (0, 1]")
    return VENUS_SOLAR_FLUX_TOP * venus_solar_fraction(h) * (1 + upward_ratio) * area_m2 * efficiency * sun_factor


def assisted_hover_power(mass_kg: float, h: float, gas_molar_mass: float, gas_volume_m3: float,
                         rotor_area_m2: float, figure_of_merit: float = 0.7) -> float:
    """Shaft power [W] to hover a vehicle of ``mass_kg`` (envelope included, lifting gas excluded) whose gas cell of
    ``gas_volume_m3`` carries part of the weight, at Venus altitude ``h``. Zero when the cell alone floats the
    vehicle (then it must vent, pump or push down to descend)."""
    from aerokit.design.electric import hover_power

    if mass_kg <= 0 or gas_volume_m3 < 0 or rotor_area_m2 <= 0:
        raise ValueError("mass and rotor area must be > 0, gas volume >= 0")
    s = venus_atmosphere(h)
    net = mass_kg * s.g - buoyant_lift_per_m3(h, gas_molar_mass) * gas_volume_m3
    if net <= 0:
        return 0.0
    return hover_power(net, s.rho, rotor_area_m2, figure_of_merit)


def envelope_drag_power(volume_m3: float, airspeed: float, h: float, drag_coefficient: float = 0.3) -> float:
    """Power [W] to push a spherical envelope of ``volume_m3`` through the air at ``airspeed`` (air-mass frame):
    ``½ ρ V³ C_D π r²``. ``C_D`` 0.3 is an assumed subcritical-sphere-like value, not data."""
    if volume_m3 <= 0 or airspeed < 0 or drag_coefficient <= 0:
        raise ValueError("volume > 0, airspeed >= 0, C_D > 0")
    r = (3 * volume_m3 / (4 * math.pi)) ** (1 / 3)
    return 0.5 * venus_atmosphere(h).rho * airspeed ** 3 * drag_coefficient * math.pi * r ** 2
