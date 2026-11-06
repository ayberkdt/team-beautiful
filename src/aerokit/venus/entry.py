"""Interplanetary arrival and ballistic atmospheric entry at Venus (planar, point mass, non-rotating planet).

**Arrival.** Hohmann transfer between circular coplanar orbits gives the hyperbolic excess speed at Venus
(:func:`hohmann_vinf`); the entry speed at the entry interface follows from energy, ``V_E = √(v∞² + 2μ/r_EI)``
(:func:`entry_speed`). Real launch windows give v∞ of 3–4.5 km/s; the Hohmann value is the lower bound.

**Equations of motion** (Vinh, Busemann & Culp 1980 form; γ < 0 descending; no lift by default)::

    dV/dt = −D/m − g sin γ
    dγ/dt = [L/m − (g − V²/r) cos γ] / V
    dh/dt = V sin γ ,   ds/dt = V cos γ · R/r ,   D = ½ ρ V² C_D A = ½ ρ V² m / β

integrated with fixed-step RK4. Density: :func:`aerokit.planetary.venus_atmosphere` below 100 km; above it an
isothermal extension at the 100 km temperature (scale height ``R T / (M g)``) — *our assumption*; the upper
atmosphere above 100 km varies strongly day/night (not modelled).

**Validation.** For an exponential atmosphere and straight-line ballistic entry, Allen & Eggers (1958) give the peak
deceleration ``a_max = V_E² |sin γ_E| / (2 e H)`` independent of β, reached where ``ρ = β |sin γ| / H`` — the
integrator reproduces it (tests). The real-atmosphere peak from the table is then compared with Pioneer Venus and
Venera values read by the research agent (``04_Venus/literature/missions/B_*.md``).

**Heating.** Stagnation-point convective heating by Sutton & Graves (1971), ``q = k √(ρ/R_n) V³`` with the constant
for the Venus CO₂/N₂ mixture (:data:`K_SUTTON_GRAVES_VENUS`); radiative heating, important above ~10 km/s at Venus,
is *not* modelled here (stated wherever the number is used).
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from aerokit import planetary as P
from aerokit.references import cite

__all__ = ["MU_SUN", "MU_VENUS", "K_SUTTON_GRAVES_VENUS", "tauber_radiative", "hohmann_vinf", "entry_speed", "density",
           "EntryVehicle", "EntryResult", "fly_entry", "allen_eggers_peak_g", "sutton_graves",
           "ballistic_coefficient"]

MU_SUN = 1.32712440041279419e20       # m³/s², JPL SSD astrodynamic parameters [D]
MU_VENUS = 3.24858592e14              # m³/s², JPL SSD (Venus system) [D]
G0 = 9.80665
# Sutton & Graves stagnation-point constant for the Venus atmosphere [kg^0.5 / m]: Table II of TR R-376 (CO2 0.1210,
# N2 0.1112 kg s^-1 m^-1.5 atm^-0.5, read by the research agent), mixed by eq. (44) for 97.7 % CO2 by mass ->
# K = 0.12075, converted with p_s ≈ ρV², h_s − h_w ≈ V²/2: k = K / (2 √101325) (agent's derivation, arithmetic
# re-checked here). Earth air (K = 0.1113) gives 1.748e-4 by the same route.
K_SUTTON_GRAVES_VENUS: float | None = 0.12075 / (2.0 * 101325.0 ** 0.5)

_H100 = 100e3


@cite("jpl_ssd_constants_2026", note="GM of Sun and Venus; Hohmann between circular coplanar orbits")
def hohmann_vinf(r1_au: float = 1.0, r2_au: float = P.VENUS_SEMI_MAJOR_AU) -> float:
    """Hyperbolic excess speed [m/s] on arrival at the inner planet of a Hohmann transfer (circular orbits)."""
    r1, r2 = r1_au * P.AU, r2_au * P.AU
    a = 0.5 * (r1 + r2)
    v_transfer = math.sqrt(MU_SUN * (2.0 / r2 - 1.0 / a))
    return abs(v_transfer - math.sqrt(MU_SUN / r2))


@cite("jpl_ssd_constants_2026", note="vis-viva on the approach hyperbola")
def entry_speed(v_inf: float, entry_altitude: float = 200e3) -> float:
    """Inertial speed [m/s] at the entry interface for a hyperbolic excess ``v_inf`` [m/s]."""
    if v_inf < 0 or entry_altitude < 0:
        raise ValueError("v_inf and altitude must be >= 0")
    return math.sqrt(v_inf ** 2 + 2.0 * MU_VENUS / (P.VENUS_RADIUS + entry_altitude))


def density(h: float) -> float:
    """Atmospheric density [kg/m³]: reference table to 100 km, isothermal extension above (assumption)."""
    if h <= _H100:
        return P.venus_atmosphere(max(h, 0.0)).rho
    s = P.venus_atmosphere(_H100)
    H = P.R_UNIVERSAL * s.T / (P.M_VENUS * s.g)
    return s.rho * math.exp(-(h - _H100) / H)


def ballistic_coefficient(mass_kg: float, diameter_m: float, drag_coefficient: float) -> float:
    """β = m / (C_D A) [kg/m²]."""
    if min(mass_kg, diameter_m, drag_coefficient) <= 0:
        raise ValueError("inputs must be > 0")
    return mass_kg / (drag_coefficient * math.pi * diameter_m ** 2 / 4.0)


@dataclass(frozen=True)
class EntryVehicle:
    """Entry capsule. ``nose_radius_m`` is for stagnation heating."""

    mass_kg: float
    diameter_m: float
    drag_coefficient: float = 1.05       # 45° sphere-cone, hypersonic (assumption, typical Newtonian-range value)
    nose_radius_m: float = 0.5
    lift_to_drag: float = 0.0

    @property
    def beta(self) -> float:
        return ballistic_coefficient(self.mass_kg, self.diameter_m, self.drag_coefficient)


@dataclass
class EntryResult:
    t: np.ndarray
    h: np.ndarray
    V: np.ndarray
    gamma: np.ndarray
    s: np.ndarray
    decel_g: np.ndarray          # drag deceleration / g0
    q_conv: np.ndarray           # W/m², nan when no constant is set
    q_rad: np.ndarray            # W/m², Tauber et al. 2012 fit
    peak_g: float
    peak_g_altitude: float
    peak_q: float
    heat_load: float             # J/m²
    stop_reason: str


def _rhs(y: np.ndarray, veh: EntryVehicle, dens: Callable[[float], float] | None = None) -> np.ndarray:
    V, gam, h, _s = y
    r = P.VENUS_RADIUS + h
    g = P.VENUS_G0 * (P.VENUS_RADIUS / r) ** 2
    rho = (dens or density)(h)
    D_m = 0.5 * rho * V * V / veh.beta
    L_m = veh.lift_to_drag * D_m
    return np.array([-D_m - g * math.sin(gam),
                     (L_m - (g - V * V / r) * math.cos(gam)) / V,
                     V * math.sin(gam),
                     V * math.cos(gam) * P.VENUS_RADIUS / r])


@cite("sutton_graves_1971", note="q = k sqrt(rho/Rn) V^3, convective only")
def sutton_graves(rho: float, V: float, nose_radius: float, k: float | None = None) -> float:
    """Stagnation-point convective heat flux [W/m²]; ``k`` defaults to :data:`K_SUTTON_GRAVES_VENUS`."""
    k = K_SUTTON_GRAVES_VENUS if k is None else k
    if k is None:
        return float("nan")
    if rho < 0 or V < 0 or nose_radius <= 0:
        raise ValueError("rho, V >= 0 and nose radius > 0")
    return k * math.sqrt(rho / nose_radius) * V ** 3


@cite("tauber_palmer_prabhu_2012", note="eq. 2a (10.028-12 km/s) and 2b (< 10.028 km/s), 96.5 % CO2")
def tauber_radiative(rho: float, V: float, nose_radius: float) -> float:
    """Stagnation-point radiative heat flux [W/m²] for Venus entry (Tauber, Palmer & Prabhu 2012 fit, read by the
    research agent: ``8.497e-63 V^18 ρ^1.2 r_N^0.49`` above 10 028 m/s, ``2.195e-22 V^7.9 ρ^1.2 r_N^0.49`` below).
    Fitted to the Pioneer Venus large-probe trajectory (r_N 0.363 m); extrapolation to large nose radii and above
    12 km/s is outside the fit (the function refuses above 12.5 km/s)."""
    if rho < 0 or V < 0 or nose_radius <= 0:
        raise ValueError("rho, V >= 0 and nose radius > 0")
    if V > 12500.0:
        raise ValueError("outside the fit (V > 12.5 km/s)")
    if V >= 10028.0:
        return 8.497e-63 * V ** 18 * rho ** 1.2 * nose_radius ** 0.49
    return 2.195e-22 * V ** 7.9 * rho ** 1.2 * nose_radius ** 0.49


@cite("vinh_1980_hypersonic", "jpl_ssd_constants_2026",
      note="planar 3-DOF point mass over a spherical non-rotating planet")
def fly_entry(veh: EntryVehicle, V0: float, gamma0_deg: float, h0: float = 200e3, dt: float = 0.02,
              stop_speed: float = 200.0, stop_altitude: float = 40e3, k_sg: float | None = None,
              density_fn: Callable[[float], float] | None = None) -> EntryResult:
    """Integrate the entry from ``h0`` until the speed drops to ``stop_speed`` (≈ subsonic, parachute) or the
    altitude reaches ``stop_altitude``. ``density_fn(h)`` replaces the atmosphere (validation)."""
    if V0 <= 0 or not -90 < gamma0_deg < 0 or dt <= 0:
        raise ValueError("V0 > 0, -90 < gamma0 < 0 deg, dt > 0")
    y = np.array([V0, math.radians(gamma0_deg), h0, 0.0])
    t = 0.0
    T: list[float] = []
    H: list[float] = []
    VV: list[float] = []
    GG: list[float] = []
    SS: list[float] = []
    A: list[float] = []
    Q: list[float] = []
    QR: list[float] = []
    reason = "time limit"
    for _ in range(int(3600 / dt)):
        V, gam, h, s = y
        rho = (density_fn or density)(h)
        a = 0.5 * rho * V * V / veh.beta / G0
        q = sutton_graves(rho, V, veh.nose_radius_m, k_sg)
        qr = tauber_radiative(rho, V, veh.nose_radius_m) if V <= 12500.0 else float("nan")
        for lst, v in ((T, t), (H, h), (VV, V), (GG, gam), (SS, s), (A, a), (Q, q), (QR, qr)):
            lst.append(v)
        if V <= stop_speed:
            reason = "stop speed"
            break
        if h <= stop_altitude:
            reason = "stop altitude"
            break
        k1 = _rhs(y, veh, density_fn)
        k2 = _rhs(y + 0.5 * dt * k1, veh, density_fn)
        k3 = _rhs(y + 0.5 * dt * k2, veh, density_fn)
        k4 = _rhs(y + dt * k3, veh, density_fn)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
    arr = [np.array(v) for v in (T, H, VV, GG, SS, A, Q, QR)]
    i = int(np.argmax(arr[5]))
    qa = arr[6]
    peak_q = float(np.nanmax(qa)) if np.isfinite(qa).any() else float("nan")
    load = float(np.trapezoid(qa, arr[0])) if np.isfinite(qa).all() else float("nan")
    return EntryResult(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], qa, arr[7], float(arr[5][i]),
                       float(arr[1][i]), peak_q, load, reason)


@cite("allen_eggers_1958", note="exponential atmosphere, straight-line ballistic entry")
def allen_eggers_peak_g(V_entry: float, gamma_deg: float, scale_height: float) -> float:
    """Peak deceleration [g₀] ``V_E² |sin γ| / (2 e H g₀)``."""
    if V_entry <= 0 or scale_height <= 0 or gamma_deg == 0:
        raise ValueError("V > 0, H > 0, gamma != 0")
    return V_entry ** 2 * abs(math.sin(math.radians(gamma_deg))) / (2.0 * math.e * scale_height) / G0
