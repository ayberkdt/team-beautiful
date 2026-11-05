"""Flight control in strong winds: air-relative vs ground-relative, gust and downdraft authority, rotor response.

* **Station keeping is impossible**: maximum airspeed (power-limited, :func:`max_airspeed`) is ~20–30 m/s against a
  60–90 m/s zonal wind; the control objective is the air-mass frame (position relative to the moving air, altitude),
  ground track is a planning output.
* **Downdrafts** (VEGA-2: −2…−3.3 m/s over ~2 h, ~2.9 km down; research note A_vega1985 [D-ag]): holding altitude in a downdraft ``w``
  costs extra power ``W w / η`` (:func:`downdraft_hold_power`); riding it costs the energy to climb back,
  ``m g Δh / η`` (:func:`downdraft_ride_energy`).
* **Rotor-speed (rpm) control bandwidth**: a fixed-pitch rotor changes thrust by changing speed; the time to raise
  thrust by ``f`` with spare motor torque ``ΔQ`` is ``I ΔΩ / ΔQ`` with ``ΔΩ ≈ Ω (√(1+f) − 1)``
  (:func:`rpm_response_time`). Large slow rotors respond in ~0.3–1 s. That is ample for *altitude* in Venus' slow
  vertical gusts (:func:`gust_response`: correlation times 30–130 s) but too slow for *attitude* control by
  differential thrust (Hz-level bandwidth) — the reason the Mars Science Helicopter study found large rotors hard to
  control (note C_johnson2020_msh [D-ag]) and why VESPER carries per-rotor collective-pitch actuators [Y].
* **Heave damping**: :func:`heave_derivative` (BEMT in climb at fixed rotor speed) — the rotor resists vertical motion
  relative to the air; the vehicle follows vertical air motion with a time constant ``m / |∂T/∂w|``.
"""
from __future__ import annotations

import math

import numpy as np

from aerokit.venus import bemt as B
from aerokit.venus import performance as F

__all__ = ["max_airspeed", "downdraft_hold_power", "downdraft_ride_energy", "blade_inertia", "rpm_response_time",
           "heave_derivative", "gust_response"]


def max_airspeed(sys_: F.RotorSystem, weight_N: float, flow: B.FlowState, shaft_limit_W: float) -> float:
    """Largest level-flight airspeed [m/s] whose shaft power stays below ``shaft_limit_W``."""
    best = 0.0
    for V in np.arange(0.0, 60.0, 0.25):
        if F.forward_power(sys_, weight_N, flow, float(V)) <= shaft_limit_W:
            best = float(V)
        elif V > 5.0:
            break
    return best


def downdraft_hold_power(weight_N: float, w: float, drive_efficiency: float) -> float:
    """Extra electrical power [W] to hold altitude in a downdraft ``w`` [m/s] (climb at ``w`` relative to air)."""
    return weight_N * abs(w) / drive_efficiency


def downdraft_ride_energy(weight_N: float, dh: float, drive_efficiency: float) -> float:
    """Electrical energy [J] to climb back ``dh`` [m] after riding a downdraft."""
    return weight_N * abs(dh) / drive_efficiency


def blade_inertia(blade_mass_kg: float, radius_m: float, blades: int, hub_kg: float = 0.12,
                  hub_radius_m: float = 0.08) -> float:
    """Rotor polar moment of inertia [kg m²]: uniform blades (m R²/3 each) + hub disc."""
    return blades * blade_mass_kg * radius_m ** 2 / 3.0 + 0.5 * hub_kg * hub_radius_m ** 2


def rpm_response_time(inertia: float, omega: float, spare_torque: float, thrust_step: float = 0.2) -> float:
    """Time [s] to raise thrust by ``thrust_step`` (fraction) by speeding up a fixed-pitch rotor."""
    if spare_torque <= 0:
        raise ValueError("spare torque must be > 0")
    d_omega = omega * (math.sqrt(1.0 + thrust_step) - 1.0)
    return inertia * d_omega / spare_torque


def heave_derivative(sys_: F.RotorSystem, weight_N: float, flow: B.FlowState, dv: float = 0.25) -> float:
    """∂T/∂w [N per m/s] of the whole vehicle at fixed rotor speed and pitch (BEMT in axial climb, central
    difference): the rotor's natural heave damping. Negative: climbing through the air lowers thrust."""
    hp = F.hover(sys_, weight_N, flow)
    om = hp.per_rotor.omega
    up = B.solve(sys_.rotor, om, flow, climb=dv).thrust
    dn = B.solve(sys_.rotor, om, flow, climb=-dv).thrust if dv < hp.v_h else up
    return sys_.count * (up - dn) / (2.0 * dv)


def gust_response(mass_kg: float, weight_N: float, Z_w: float, actuator_tau_s: float, sigma_w: float = 0.7,
                  gust_time_s: float = 80.0, kp: float = 0.02, kd: float = 0.6, duration_s: float = 7200.0,
                  dt: float = 0.05, seed: int = 1) -> dict:
    """Altitude hold in a first-order (Gauss–Markov) vertical gust ``w`` with standard deviation ``sigma_w`` and
    correlation time ``gust_time_s`` (VEGA: σ 0.65–0.75 m/s, fluctuations at 30–130 s periods [D-ag]).

    Vertical dynamics in the air-mass frame: ``m z̈ = ΔT + Z_w (ż − w)``, thrust command
    ``ΔT_c = −m (kp z + kd ż)`` (per-unit-mass gains [Y]) through a first-order actuator lag ``τ`` (collective pitch
    ~0.1 s, rotor-speed control ~1 s from :func:`rpm_response_time`). Returns RMS/peak altitude error and thrust."""
    import numpy as _np

    rng = _np.random.default_rng(seed)
    a = math.exp(-dt / gust_time_s)
    b = sigma_w * math.sqrt(1.0 - a * a)
    z = zd = dT = w = 0.0
    zs, ts = [], []
    for _ in range(int(duration_s / dt)):
        w = a * w + b * rng.standard_normal()
        cmd = -mass_kg * (kp * z + kd * zd)
        dT += (cmd - dT) * dt / actuator_tau_s
        zdd = (dT + Z_w * (zd - w)) / mass_kg
        zd += zdd * dt
        z += zd * dt
        zs.append(z)
        ts.append(dT)
    zs_a, ts_a = _np.array(zs), _np.array(ts)
    return {"z_rms_m": float(_np.sqrt(_np.mean(zs_a ** 2))), "z_peak_m": float(_np.max(_np.abs(zs_a))),
            "dT_rms_N": float(_np.sqrt(_np.mean(ts_a ** 2))), "dT_peak_over_W": float(_np.max(_np.abs(ts_a)) / weight_N)}
