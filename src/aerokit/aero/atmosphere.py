"""ISA standard atmosphere, 0-20 km (troposphere and lower stratosphere).

Constants
---------
R : float
    Specific gas constant of dry air, 287.053 J/(kg K).
G0 : float
    Standard gravitational acceleration, 9.80665 m/s^2.
GAMMA : float
    Ratio of specific heats of air, 1.4.
L_TROPO : float
    Tropospheric temperature lapse rate, 0.0065 K/m.
T0, P0 : float
    Sea-level temperature 288.15 K and pressure 101 325 Pa.
"""
from __future__ import annotations

import math

from aerokit.references import cite

R = 287.053        # J/(kg·K)
G0 = 9.80665       # m/s²
GAMMA = 1.4
L_TROPO = 0.0065   # K/m
T0, P0 = 288.15, 101325.0


@cite("iso_2533_1975", note="ISA layers 0-11 km and 11-20 km; Sutherland viscosity law")
def isa(h: float) -> dict[str, float]:
    """International Standard Atmosphere properties at geopotential altitude ``h``.

    Parameters
    ----------
    h : float
        Geopotential altitude [m], 0 <= h <= 20 000.

    Returns
    -------
    dict[str, float]
        ``T`` temperature [K], ``p`` pressure [Pa], ``rho`` density [kg/m^3],
        ``mu`` dynamic viscosity [Pa s], ``nu`` kinematic viscosity [m^2/s],
        ``a`` speed of sound [m/s].

    Raises
    ------
    ValueError
        If ``h`` is outside 0-20 000 m.

    Notes
    -----
    Troposphere (h <= 11 km): T = T0 - L h, p = P0 (T/T0)^(g0/(L R)).
    Lower stratosphere (isothermal, T = 216.65 K): p = 22 632.06 exp(-g0 (h - 11 000)/(R T)).
    Viscosity from Sutherland's law, mu = 1.458e-6 T^1.5 / (T + 110.4).

    Examples
    --------
    >>> round(isa(0.0)["rho"], 3)
    1.225
    """
    if not 0 <= h <= 20000:
        raise ValueError("the ISA model is implemented for 0-20 000 m only")
    if h <= 11000:
        T = T0 - L_TROPO * h
        p = P0 * (T / T0) ** (G0 / (L_TROPO * R))
    else:
        T = 216.65
        p = 22632.06 * math.exp(-G0 * (h - 11000) / (R * T))
    rho = p / (R * T)
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)          # Sutherland
    return {"T": T, "p": p, "rho": rho, "mu": mu, "nu": mu / rho,
            "a": math.sqrt(GAMMA * R * T)}


def sigma(h: float) -> float:
    """Density ratio rho/rho0 at altitude ``h``.

    Parameters
    ----------
    h : float
        Geopotential altitude [m], 0 <= h <= 20 000.

    Returns
    -------
    float
        sigma = rho(h)/rho(0) [-].

    Raises
    ------
    ValueError
        If ``h`` is outside 0-20 000 m.

    Examples
    --------
    >>> sigma(0.0)
    1.0
    """
    return isa(h)["rho"] / isa(0)["rho"]


R_EARTH_GEOPOTENTIAL = 6_356_766.0    # m, Earth radius used for geopotential altitude


@cite("anderson_2017", note="Appendix D lists geometric h_G and geopotential h side by side (PDF pp. 1117-1125)")
def geopotential_altitude(h_geometric: float) -> float:
    """Geopotential altitude h = r h_G / (r + h_G) [m] from geometric altitude ``h_geometric`` [m].

    :func:`isa` takes geopotential altitude; GPS/STK altitudes are geometric. The difference is
    16 m at 10 km and 35 m at 15 km.
    """
    return R_EARTH_GEOPOTENTIAL * h_geometric / (R_EARTH_GEOPOTENTIAL + h_geometric)


def geometric_altitude(h_geopotential: float) -> float:
    """Inverse of :func:`geopotential_altitude` [m]."""
    if h_geopotential >= R_EARTH_GEOPOTENTIAL:
        raise ValueError("geopotential altitude out of range")
    return R_EARTH_GEOPOTENTIAL * h_geopotential / (R_EARTH_GEOPOTENTIAL - h_geopotential)
