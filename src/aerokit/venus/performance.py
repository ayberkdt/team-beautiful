"""Multirotor performance at Venus: BEMT hover, forward flight (power bucket), climb, control margin.

**Hover.** Each of ``n`` identical rotors carries ``W/n``; :func:`aerokit.venus.bemt.solve_for_thrust` (fixed
pitch, rpm trim) gives power, rpm, tip Mach, Reynolds, figure of merit. Rotor-rotor interaction of a hexacopter in
hover is neglected (rotors do not overlap) [Y].

**Forward flight (level, air-relative speed V).** Uniform-inflow momentum theory (Glauert) with the BEMT hover
values as calibration (Johnson, *Helicopter Theory*; not read in this session — standard result, tested against the
hover limit)::

    v_i² = (−V² + √(V⁴ + 4 v_h⁴)) / 2          (small disk tilt)
    P = κ T v_i + P₀ (1 + 4.65 μ²) + ½ ρ V³ f_e ,   μ = V / ΩR

with ``κ`` = BEMT induced power / ideal momentum power, ``P₀`` = BEMT profile power in hover, ``f_e`` the
equivalent flat-plate drag area of the airframe [Y]. Climb adds ``W V_c`` (momentum theory, ``v_i`` reduction
neglected — conservative).

**Electrical power** = shaft / (motor × ESC efficiency) + avionics + payload + heaters.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from aerokit.references import cite
from aerokit.venus import bemt as B

__all__ = ["RotorSystem", "HoverPoint", "hover", "forward_power", "power_curve", "bucket", "max_thrust_ratio"]


@dataclass(frozen=True)
class RotorSystem:
    """``n`` identical fixed-pitch rotors driven by electric motors."""

    rotor: B.Rotor
    count: int = 6
    motor_efficiency: float = 0.88          # BLDC at part load [Y]
    esc_efficiency: float = 0.96            # [Y]
    drag_area_m2: float = 0.45              # equivalent flat plate f_e of the airframe [Y]
    max_tip_mach: float = 0.7               # Ingenuity-like cap (C notes: tip Mach ~0.7) [D-ag/Y]
    bemt_power_factor: float = 1.05         # BEMT under-predicts torque ~5 % at hover pitch (Knight & Hefner test) [K]

    @property
    def drive_efficiency(self) -> float:
        return self.motor_efficiency * self.esc_efficiency

    @property
    def disk_area(self) -> float:
        return self.count * self.rotor.disk_area


@dataclass(frozen=True)
class HoverPoint:
    weight_N: float
    rho: float
    per_rotor: B.BEMTResult
    shaft_W: float
    electric_W: float
    rpm: float
    FM: float
    kappa: float
    profile_W: float
    v_h: float


@cite("leishman_2006_helicopter", note="BEMT hover; kappa = induced / ideal")
def hover(sys_: RotorSystem, weight_N: float, flow: B.FlowState) -> HoverPoint:
    """Hover of the whole vehicle (``weight_N``) in ``flow``."""
    return _hover_cached(sys_, round(weight_N, 6), flow)


@lru_cache(maxsize=4096)
def _hover_cached(sys_: RotorSystem, weight_N: float, flow: B.FlowState) -> HoverPoint:
    return hover_from(sys_, weight_N, flow, B.solve_for_thrust(sys_.rotor, weight_N / sys_.count, flow))


def hover_from(sys_: RotorSystem, weight_N: float, flow: B.FlowState, r: B.BEMTResult) -> HoverPoint:
    """Hover point from an existing per-rotor BEMT result that carries ``weight_N / count``."""
    T = weight_N / sys_.count
    A = sys_.rotor.disk_area
    p_ideal = T ** 1.5 / math.sqrt(2.0 * flow.rho * A)
    p_ind = r.induced_CP * flow.rho * A * r.tip_speed ** 3
    p_0 = r.profile_CP * flow.rho * A * r.tip_speed ** 3
    shaft = r.power * sys_.count * sys_.bemt_power_factor
    k = sys_.bemt_power_factor
    return HoverPoint(weight_N, flow.rho, r, shaft, shaft / sys_.drive_efficiency, r.omega * 30.0 / math.pi,
                      r.FM / k, k * p_ind / p_ideal, k * p_0 * sys_.count, math.sqrt(T / (2.0 * flow.rho * A)))


def forward_power(sys_: RotorSystem, weight_N: float, flow: B.FlowState, V: float, climb: float = 0.0) -> float:
    """Shaft power [W] in level flight at air-relative speed ``V`` (plus climb rate ``climb``)."""
    if V < 0:
        raise ValueError("V >= 0")
    hp = hover(sys_, weight_N, flow)
    vh = hp.v_h
    vi = math.sqrt((-V * V + math.sqrt(V ** 4 + 4.0 * vh ** 4)) / 2.0)
    mu = V / hp.per_rotor.tip_speed
    induced = hp.kappa * weight_N * vi
    profile = hp.profile_W * (1.0 + 4.65 * mu * mu)
    parasite = 0.5 * flow.rho * V ** 3 * sys_.drag_area_m2
    return induced + profile + parasite + weight_N * max(climb, 0.0)


def power_curve(sys_: RotorSystem, weight_N: float, flow: B.FlowState,
                speeds: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    speeds = np.linspace(0.0, 30.0, 61) if speeds is None else speeds
    return speeds, np.array([forward_power(sys_, weight_N, flow, float(v)) for v in speeds])


def bucket(sys_: RotorSystem, weight_N: float, flow: B.FlowState) -> tuple[float, float]:
    """(speed [m/s], shaft power [W]) of minimum power in level flight."""
    v, p = power_curve(sys_, weight_N, flow, np.linspace(0.0, 25.0, 251))
    i = int(np.argmin(p))
    return float(v[i]), float(p[i])


def max_thrust_ratio(sys_: RotorSystem, weight_N: float, flow: B.FlowState) -> float:
    """Thrust/weight available when every rotor runs at the tip-Mach cap (fixed pitch, stall included)."""
    om = sys_.max_tip_mach * flow.a / sys_.rotor.radius
    r = B.solve(sys_.rotor, om, flow)
    return r.thrust * sys_.count / weight_N
