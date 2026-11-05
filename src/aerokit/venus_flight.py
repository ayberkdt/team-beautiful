"""Time-stepped flight of a buoyancy-assisted drone in the Venus cloud layer (simulation-ready model).

**Vehicle.** A superpressure (fixed-volume) helium cell carries most of the weight; rotors trim the rest and drive
altitude changes. Because the cell volume is fixed, its net lift ``(ρ_atm − ρ_gas) V g`` (:func:`aerokit.planetary.
buoyant_lift_per_m3`) falls with altitude: the vehicle has a natural *float altitude* where lift equals weight, and
holding any other altitude costs rotor power. Vertical and horizontal motion use the effective mass
``m + m_gas + ½ ρ V`` (the added mass of air a sphere drags along, ``½ ρ V``, matters for a light envelope);
aerodynamic drag acts on the *air-relative* velocity, ``½ ρ |v_rel| v_rel C_D A``.

**Air-mass frame.** The zonal wind :func:`aerokit.planetary.venus_zonal_wind` (sourced anchors, interpolation
assumed) blows along +x (east). With no horizontal thrust the vehicle relaxes to the wind speed and drifts — the
cheap way to live on Venus; holding position against it would cost hundreds of kW (doc 19).

**Rotors and power.** Thrust up to the value the electrical power limit allows,
``T_max = (η P_max · FM √(2 ρ A))^{2/3}`` (momentum theory inverted), in either direction (reversible rotors —
assumption). Electrical power ``P = T^{3/2} / (FM √(2 ρ A)) / η + P_avionics``; climb-power and profile terms are not
modelled. Solar input is :func:`aerokit.planetary.solar_power` at the current altitude with a fixed sun factor (the
Venus solar day is 117 Earth days, so the sun barely moves during a mission of hours).

**Control.** A mission is a list of steps: ``{"goto": km, "rate": m/s}`` flies to an altitude at a capped vertical
speed, ``{"hold": km, "for_s": s}`` holds it. Vertical law: commanded rate ``clip(k_z Δz, ±rate)``, thrust
``m_eff k_v (ż_c − ż) + (m g − L)`` (feed-forward of the lift deficit), clipped to ``±T_max``.

**Thermal and energy.** Hull temperature relaxes to the ambient with a time constant (first order); the run records
the time above the electronics limit. The battery integrates ``P_solar − P``, clipped at empty and full; an empty
battery cuts the rotors.

Every number of the vehicle is an input; :func:`replay` turns a run into a 1 Hz JSON-ready list for a simulator
(Unity / Liftoff Core) to play back. Concept-level: one rigid point mass, no turbulence (no source found), no
meridional wind, no gas leakage or superpressure limit.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from aerokit import planetary as P
from aerokit.design.electric import hover_power

__all__ = ["VenusDrone", "FlightRun", "float_altitude", "max_thrust", "simulate_mission", "replay", "DayRun",
           "simulate_rotorcraft_day"]


@dataclass(frozen=True)
class VenusDrone:
    """Vehicle data (SI). ``mass_kg`` excludes the lifting gas."""

    mass_kg: float = 10.0
    gas_volume_m3: float = 9.0
    gas_molar_mass: float = P.M_HE
    rotor_area_m2: float = 1.13
    figure_of_merit: float = 0.65
    electrical_efficiency: float = 0.7
    max_power_W: float = 1500.0
    drag_area_m2: float = 1.5               # C_D A of envelope + frame
    avionics_W: float = 15.0
    battery_Wh: float = 500.0
    solar_area_m2: float = 1.0
    solar_efficiency: float = 0.2
    upward_ratio: float = 0.9
    sun_factor: float = 1.0 / math.pi
    thermal_tau_s: float = 600.0
    temp_limit_C: float = 70.0


@dataclass
class FlightRun:
    """Time histories (SI) and mission events of one run."""

    t: np.ndarray
    x: np.ndarray               # east, air-mass drift included [m]
    z: np.ndarray               # altitude [m]
    vz: np.ndarray
    u: np.ndarray               # eastward ground speed [m/s]
    wind: np.ndarray
    thrust: np.ndarray          # vertical rotor thrust [N], + up
    power: np.ndarray           # electrical draw [W]
    solar: np.ndarray           # solar input [W]
    energy_Wh: np.ndarray
    T_ambient_C: np.ndarray
    T_hull_C: np.ndarray
    events: list[tuple[float, str]] = field(default_factory=list)
    time_over_temp_s: float = 0.0
    brownout: bool = False


def _net_lift(d: VenusDrone, h: float) -> float:
    return P.buoyant_lift_per_m3(h, d.gas_molar_mass) * d.gas_volume_m3


def float_altitude(d: VenusDrone, lo: float = 30e3, hi: float = 75e3) -> float:
    """Altitude [m] where the cell's net lift equals the weight (bisection); raises if it is outside [lo, hi]."""
    def excess(h: float) -> float:
        return _net_lift(d, h) - d.mass_kg * P.venus_gravity(h)

    if excess(lo) * excess(hi) > 0:
        raise ValueError("no float altitude between the bounds: the cell is too small or too large")
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if excess(lo) * excess(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def max_thrust(d: VenusDrone, rho: float) -> float:
    """Largest rotor thrust [N] the electrical power limit allows (momentum theory, avionics excluded)."""
    shaft = max(d.max_power_W - d.avionics_W, 0.0) * d.electrical_efficiency
    return (shaft * d.figure_of_merit * math.sqrt(2 * rho * d.rotor_area_m2)) ** (2.0 / 3.0)


def _targets(mission: Sequence[Mapping[str, float]]) -> list[tuple[str, float, float]]:
    out = []
    for step in mission:
        if "goto" in step:
            out.append(("goto", float(step["goto"]) * 1e3, float(step.get("rate", 2.0))))
        elif "hold" in step:
            out.append(("hold", float(step["hold"]) * 1e3, float(step["for_s"])))
        else:
            raise ValueError(f"mission step needs 'goto' or 'hold': {step}")
    return out


def simulate_mission(d: VenusDrone, mission: Sequence[Mapping[str, float]], start_km: float, dt: float = 0.5,
                     k_z: float = 0.02, k_v: float = 0.5, max_time_s: float = 48 * 3600.0,
                     tolerance_m: float = 20.0) -> FlightRun:
    """Fly ``mission`` from rest at ``start_km`` (moving with the wind). See the module docstring."""
    if dt <= 0 or start_km <= 0:
        raise ValueError("dt and start_km must be > 0")
    steps = _targets(mission)
    z, x = start_km * 1e3, 0.0
    vz, u = 0.0, P.venus_zonal_wind(z)
    energy = d.battery_Wh
    T_hull = P.venus_atmosphere(z).T
    rec: dict[str, list[float]] = {k: [] for k in ("t", "x", "z", "vz", "u", "wind", "thrust", "power", "solar",
                                                   "energy", "Ta", "Th")}
    events: list[tuple[float, str]] = []
    over, brown = 0.0, False
    k, hold_until, t = 0, None, 0.0
    while k < len(steps) and t < max_time_s:
        kind, target, arg = steps[k]
        s = P.venus_atmosphere(z)
        wind = P.venus_zonal_wind(z)
        m_gas = P.gas_density(s.p, s.T, d.gas_molar_mass) * d.gas_volume_m3
        m_eff = d.mass_kg + m_gas + 0.5 * s.rho * d.gas_volume_m3
        deficit = d.mass_kg * s.g - _net_lift(d, z)
        rate = arg if kind == "goto" else 1.0
        vz_c = max(-rate, min(rate, k_z * (target - z)))
        T_lim = max_thrust(d, s.rho) if energy > 0 else 0.0
        thrust = max(-T_lim, min(T_lim, m_eff * k_v * (vz_c - vz) + deficit))
        p_el = hover_power(abs(thrust), s.rho, d.rotor_area_m2, d.figure_of_merit) / d.electrical_efficiency \
            if thrust else 0.0
        p_el += d.avionics_W
        try:
            p_sun = P.solar_power(d.solar_area_m2, d.solar_efficiency, z, d.sun_factor, d.upward_ratio)
        except ValueError:                  # below 50 km the light level is not sourced: count none
            p_sun = 0.0
        energy = min(d.battery_Wh, energy + (p_sun - p_el) * dt / 3600.0)
        if energy <= 0.0:
            energy = 0.0
            if not brown:
                brown = True
                events.append((t, "battery empty: rotors off"))
        drag_z = 0.5 * s.rho * abs(vz) * vz * d.drag_area_m2
        rel = u - wind
        drag_x = 0.5 * s.rho * abs(rel) * rel * d.drag_area_m2
        vz += (thrust - deficit - drag_z) / m_eff * dt
        u += -drag_x / m_eff * dt
        z += vz * dt
        x += u * dt
        T_hull += (s.T - T_hull) * dt / d.thermal_tau_s
        if T_hull - 273.15 > d.temp_limit_C:
            over += dt
        t += dt
        for key, val in (("t", t), ("x", x), ("z", z), ("vz", vz), ("u", u), ("wind", wind), ("thrust", thrust),
                         ("power", p_el), ("solar", p_sun), ("energy", energy), ("Ta", s.T - 273.15),
                         ("Th", T_hull - 273.15)):
            rec[key].append(val)
        if kind == "goto" and abs(target - z) < tolerance_m:
            events.append((t, f"reached {target / 1e3:.1f} km"))
            k += 1
        elif kind == "hold":
            if hold_until is None:
                hold_until = t + arg
            if t >= hold_until:
                events.append((t, f"held {target / 1e3:.1f} km for {arg:.0f} s"))
                k, hold_until = k + 1, None
    if k < len(steps):
        events.append((t, "mission time limit reached"))
    arr = {key: np.array(v) for key, v in rec.items()}
    return FlightRun(arr["t"], arr["x"], arr["z"], arr["vz"], arr["u"], arr["wind"], arr["thrust"], arr["power"],
                     arr["solar"], arr["energy"], arr["Ta"], arr["Th"], events, over, brown)


def replay(run: FlightRun, every_s: float = 1.0) -> list[dict[str, float]]:
    """Down-sampled, JSON-ready frames for a simulator to play back (SI; temperatures in °C)."""
    if every_s <= 0:
        raise ValueError("every_s must be > 0")
    out, next_t = [], 0.0
    for i, t in enumerate(run.t):
        if t + 1e-9 >= next_t:
            out.append({"t_s": round(float(t), 3), "east_m": round(float(run.x[i]), 2),
                        "altitude_m": round(float(run.z[i]), 2), "vertical_speed_m_s": round(float(run.vz[i]), 3),
                        "ground_speed_east_m_s": round(float(run.u[i]), 3),
                        "wind_east_m_s": round(float(run.wind[i]), 3),
                        "thrust_N": round(float(run.thrust[i]), 3), "power_W": round(float(run.power[i]), 2),
                        "solar_W": round(float(run.solar[i]), 2), "battery_Wh": round(float(run.energy_Wh[i]), 3),
                        "ambient_C": round(float(run.T_ambient_C[i]), 2), "hull_C": round(float(run.T_hull_C[i]), 2)})
            next_t += every_s
    return out


# ---------------------------------------------------------------------------------------------------------------
# Pure rotorcraft over a Venus air-mass day (added 4 Nov 2026 for the LuGus final: VESPER, aerokit.venus.*)
# ---------------------------------------------------------------------------------------------------------------

@dataclass
class DayRun:
    """Time histories of a multi-hour rotorcraft mission (SI, temperatures in °C, energy in Wh)."""

    t: np.ndarray
    z: np.ndarray
    x: np.ndarray                # westward drift with the air [m]
    mu0: np.ndarray
    p_need: np.ndarray           # electrical demand [W]
    p_solar: np.ndarray          # array output [W]
    energy_Wh: np.ndarray
    T_ambient_C: np.ndarray
    T_interior_C: np.ndarray
    mode: list[str]
    events: list[tuple[float, str]] = field(default_factory=list)
    flight_time_s: float = 0.0
    solar_sustained_s: float = 0.0
    no_charge_s: float = 0.0


def simulate_rotorcraft_day(design: Any, start_hour_angle_deg: float = -40.0, latitude_deg: float = 0.0,
                            cruise_km: float = 55.0, dives: tuple[tuple[float, float, float], ...] = (),
                            sunset_dive: bool = True, dt: float = 30.0, max_days: float = 7.0,
                            climb_rate: float = 3.0, battery_soc0: float = 1.0,
                            dive_abort_C: float = 50.0) -> DayRun:
    """Fly a closed :class:`aerokit.venus.sizing.Design` from release until its battery is empty.

    The vehicle loiters at its minimum-power (bucket) airspeed in the air-mass frame at ``cruise_km``; ``dives`` are
    ``(start_s, bottom_km, hold_s)`` science dives at ``climb_rate``; when the battery would not last into the dark
    it makes a final *sunset dive* (descends at ``climb_rate`` measuring until the battery is empty or too hot). A
    science dive is aborted (climb back) when the battery interior passes ``dive_abort_C``. Solar input:
    :class:`aerokit.venus.power.SolarArray` at the local cos(zenith) along the drift; battery charging is allowed only
    while the vessel interior is inside the Li-ion charge window (thermal model :mod:`aerokit.venus.thermal`).
    Atmosphere: Pioneer Venus probe mean (:mod:`aerokit.venus.atmosphere`).
    """
    from aerokit.venus import atmosphere as A
    from aerokit.venus import bemt as B
    from aerokit.venus import performance as F
    from aerokit.venus import power as PW
    from aerokit.venus import thermal as TH

    arr = PW.SolarArray(design.solar_area_m2, design.req.solar_efficiency)
    batt = design.req.battery
    cap = design.battery_Wh
    E = cap * battery_soc0
    vessel = TH.Vessel()
    sys_ = design.system
    eta = sys_.drive_efficiency
    m = design.gross_kg
    cruise = cruise_km * 1e3
    z = cruise
    x = 0.0
    s0 = A.state(z)
    Ti, Ts = s0.T, s0.T
    period = PW.air_mass_day_s(A.zonal_wind(z), z)
    H = math.radians(start_hour_angle_deg)
    rec: dict[str, list[float]] = {k: [] for k in ("t", "z", "x", "mu0", "pn", "ps", "E", "Ta", "Ti")}
    modes: list[str] = []
    events: list[tuple[float, str]] = [(0.0, f"release, loiter at {cruise_km:.1f} km")]
    t = 0.0
    sustained = no_charge = 0.0
    dive_plan = sorted(dives)
    dive_idx = 0
    target = cruise
    hold_until = None
    final = False
    cache: dict[float, float] = {}

    def loiter_power(h: float) -> float:
        key = round(h / 250.0) * 250.0
        if key not in cache:
            st = A.state(min(max(key, A.Z_MIN), A.Z_MAX))
            fl = B.FlowState(st.rho, st.mu, st.a)
            cache[key] = F.bucket(sys_, m * st.g, fl)[1] / eta
        return cache[key]

    while t < max_days * 86400.0:
        zc = min(max(z, A.Z_MIN), A.Z_MAX)
        st = A.state(zc)
        mu0 = math.cos(math.radians(latitude_deg)) * math.cos(H)
        p_sun = arr.power(zc, mu0) if mu0 > 0 else 0.0
        if not final and dive_idx < len(dive_plan) and t >= dive_plan[dive_idx][0] and target == cruise:
            target = dive_plan[dive_idx][1] * 1e3
            events.append((t, f"science dive to {dive_plan[dive_idx][1]:.1f} km"))
        if not final and target != cruise and abs(z - target) <= climb_rate * dt:
            if hold_until is None:
                hold_until = t + dive_plan[dive_idx][2]
            elif t >= hold_until:
                target, hold_until = cruise, None
                dive_idx += 1
                events.append((t, "climb back to cruise"))
        if not final and target < cruise and Ti - 273.15 > dive_abort_C:
            target, hold_until = cruise, None
            dive_idx += 1
            events.append((t, f"dive aborted at {z / 1e3:.1f} km: battery {Ti - 273.15:.0f} °C"))
        p_loiter = loiter_power(z)
        afternoon = math.sin(H) > 0.0
        if sunset_dive and not final and afternoon and p_sun < p_loiter + design.P_sys_W and \
                E < (p_loiter + design.P_sys_W - p_sun) * 0.9:
            final = True
            target = A.Z_MIN + 500.0
            events.append((t, "sunset dive: descend measuring until the battery is empty"))
        if abs(target - z) <= climb_rate * dt:
            vz = (target - z) / dt
        else:
            vz = math.copysign(climb_rate, target - z)
        p_need = p_loiter + design.P_sys_W + m * st.g * max(vz, 0.0) / eta
        net = p_sun - p_need
        if net > 0 and not batt.can_charge(Ti - 273.15):
            net = 0.0
            no_charge += dt
        if p_sun >= p_need:
            sustained += dt
        E = min(cap, E + net * dt / 3600.0)
        internal = design.P_sys_W * 0.8 + 0.03 * p_need
        h_c = TH.convection_coefficient(8.0, vessel.diameter_m, st.T, st.rho)
        for _ in range(6):
            q_i = internal - TH.conductance(vessel, Ti, Ts) * (Ti - Ts)
            q_s = TH._shell_balance(vessel, Ts, Ti, st.T, h_c, 0.0)
            Ti += q_i * dt / 6 / vessel.interior_heat_capacity_J_K
            Ts += q_s * dt / 6 / vessel.shell_heat_capacity_J_K
        for k, v in (("t", t), ("z", z), ("x", x), ("mu0", mu0), ("pn", p_need), ("ps", p_sun), ("E", E),
                     ("Ta", st.T - 273.15), ("Ti", Ti - 273.15)):
            rec[k].append(v)
        modes.append("final" if final else ("dive" if target != cruise else "loiter"))
        if E <= 0.0:
            events.append((t, f"battery empty at {z / 1e3:.1f} km: end of controlled flight"))
            break
        if not batt.can_discharge(Ti - 273.15) and final:
            events.append((t, f"battery above discharge limit ({Ti - 273.15:.0f} °C) at {z / 1e3:.1f} km: end"))
            break
        z += vz * dt
        x += A.zonal_wind(min(max(z, A.Z_MIN), A.Z_MAX)) * dt
        H += 2.0 * math.pi * dt / period
        t += dt
    a = {k: np.array(v) for k, v in rec.items()}
    return DayRun(a["t"], a["z"], a["x"], a["mu0"], a["pn"], a["ps"], a["E"], a["Ta"], a["Ti"], modes, events,
                  float(a["t"][-1]) if len(a["t"]) else 0.0, sustained, no_charge)
