"""Lumped thermal model of the sealed avionics/battery vessel and of the rotor motors in the cloud layer.

**Vessel** — two nodes: the interior (battery + electronics, heat capacity ``C_i``) and the titanium shell (``C_s``).
Interior → shell through an insulation conductance ``G_ins = k A / t`` (silica aerogel blanket [Y]) in parallel with
a variable-conductance heat pipe / louvered radiator that opens above the set point (:func:`conductance`); shell →
ambient by forced convection and by radiation to a surrounding cloud deck taken at the local air temperature.
Shell absorbs sunlight on its projected area with absorptivity ``α`` (silvered FEP: α 0.08, ε 0.52 — JPL aerobot
envelope, research note D_jpl_aerobot_materials [D-ag]; a white PTFE skin is an alternative).

Forced convection over the cylindrical vessel (cross-flow, diameter ``D``): Churchill–Bernstein correlation
(Incropera et al. 2007, eq. 7.54)::

    Nu = 0.3 + 0.62 Re^½ Pr^⅓ / [1 + (0.4/Pr)^⅔]^¼ · [1 + (Re/282000)^⅝]^⅘

with CO₂ properties from :mod:`aerokit.venus.gas` (Pr = μ c_p / k). The air speed past the vessel is the flight
airspeed (the vessel is outside the rotor disks) plus a turbulence floor of 1 m/s (VEGA: σ ≈ 0.7 m/s) [Y].

**Motors** — copper and iron losses ``(1 − η_m) P_shaft`` leave through the motor can into the rotor's own inflow
(conductance per motor ``G_m`` [Y]). Limits: NdFeB SH grade 150 °C, Sm₂Co₁₇ ~300 °C (manufacturer data via note
D_eclipse_magnets) [D-ag]; electronics AEC-Q100 grade 1 −40…+125 °C [D-ag]; Li-ion charge 0–45 °C, discharge −20…60 °C
[D-ag].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from aerokit.references import cite
from aerokit.venus import atmosphere as A
from aerokit.venus import gas

__all__ = ["SIGMA_SB", "Vessel", "conductance", "convection_coefficient", "vessel_steady", "vessel_transient", "motor_temperature",
           "LIMITS_C"]

SIGMA_SB = 5.670374419e-8
LIMITS_C = {"li_ion_charge": (0.0, 45.0), "li_ion_discharge": (-20.0, 60.0), "electronics_aec_q100_g1": (-40.0, 125.0),
            "ndfeb_sh_magnet": (None, 150.0), "smco_magnet": (None, 300.0)}


@dataclass(frozen=True)
class Vessel:
    diameter_m: float = 0.60
    height_m: float = 0.32
    interior_heat_capacity_J_K: float = 12.0 * 900.0      # ~12 kg battery + electronics at ~900 J/(kg K) [Y]
    shell_heat_capacity_J_K: float = 3.0 * 530.0          # Ti shell ~3 kg, c_p 530 J/(kg K)
    insulation_k: float = 0.015                           # W/(m K), silica aerogel blanket [Y]
    insulation_t_m: float = 0.010
    absorptivity: float = 0.08                            # silvered FEP [D-ag]
    emissivity: float = 0.52                              # [D-ag]
    G_max_W_K: float = 12.0                               # variable-conductance heat pipe to shell fins, open [Y]
    setpoint_C: float = 25.0                              # interior target (Li-ion charge window 0-45 °C)

    @property
    def area(self) -> float:
        r = self.diameter_m / 2.0
        return 2.0 * math.pi * r * r + math.pi * self.diameter_m * self.height_m

    @property
    def G_ins(self) -> float:
        return self.insulation_k * self.area / self.insulation_t_m


@cite("incropera_2007", note="Churchill-Bernstein cylinder in cross flow")
def convection_coefficient(speed: float, diameter: float, T: float, rho: float) -> float:
    """Forced-convection coefficient [W/(m² K)] on a cylinder of ``diameter`` in CO₂ at ``speed``."""
    mu = gas.viscosity(T)
    k = gas.conductivity(T)
    cp = gas.cp_molar(T) / gas.M_MIX
    pr = mu * cp / k
    re = max(rho * speed * diameter / mu, 1.0)
    nu = 0.3 + 0.62 * re ** 0.5 * pr ** (1 / 3) / (1 + (0.4 / pr) ** (2 / 3)) ** 0.25 * \
        (1 + (re / 282000.0) ** 0.625) ** 0.8
    return nu * k / diameter


def conductance(v: Vessel, Ti: float, Ts: float | None = None) -> float:
    """Interior-shell conductance [W/K] of a variable-conductance path: insulation only below the set point, fully
    open ``G_max`` 10 K above it, linear in between; a diode — closed whenever the shell is warmer than the interior
    (``Ts`` given) — so a dive into hot air does not pump heat in (heat-pipe diode behaviour, [Y])."""
    if Ts is not None and Ts >= Ti:
        return v.G_ins
    x = min(max((Ti - 273.15 - v.setpoint_C) / 10.0, 0.0), 1.0)
    return v.G_ins + x * (v.G_max_W_K - v.G_ins)


def _shell_balance(v: Vessel, Ts: float, Ti: float, Ta: float, h_c: float, q_sun: float) -> float:
    """Net heat into the shell [W]."""
    proj = v.diameter_m * v.height_m
    return (conductance(v, Ti, Ts) * (Ti - Ts) + v.absorptivity * q_sun * proj - h_c * v.area * (Ts - Ta)
            - v.emissivity * SIGMA_SB * v.area * (Ts ** 4 - Ta ** 4))


def vessel_steady(v: Vessel, h: float, internal_W: float, airspeed: float = 9.0, sun_flux_W_m2: float = 0.0,
                  case: str = "mean") -> tuple[float, float]:
    """Steady interior and shell temperatures [°C] at altitude ``h`` with ``internal_W`` dissipated inside."""
    s = A.state(h, case)
    h_c = convection_coefficient(max(airspeed, 1.0), v.diameter_m, s.T, s.rho)
    lo, hi = s.T - 50.0, s.T + 300.0
    for _ in range(100):                    # Ts such that the shell balances (interior flux = internal_W)
        Ts = 0.5 * (lo + hi)
        out = (h_c * v.area * (Ts - s.T) + v.emissivity * SIGMA_SB * v.area * (Ts ** 4 - s.T ** 4)
               - v.absorptivity * sun_flux_W_m2 * v.diameter_m * v.height_m)
        if out > internal_W:
            hi = Ts
        else:
            lo = Ts
    lo_i, hi_i = Ts, Ts + internal_W / v.G_ins + 1.0
    for _ in range(100):                    # interior with the controlled conductance
        Ti = 0.5 * (lo_i + hi_i)
        if conductance(v, Ti, Ts) * (Ti - Ts) > internal_W:
            hi_i = Ti
        else:
            lo_i = Ti
    return Ti - 273.15, Ts - 273.15


def vessel_transient(v: Vessel, t: np.ndarray, h: np.ndarray, internal_W: np.ndarray, airspeed: np.ndarray,
                     sun_flux: np.ndarray | None = None, Ti0_C: float | None = None, case: str = "mean"
                     ) -> tuple[np.ndarray, np.ndarray]:
    """Explicit-Euler interior/shell temperatures [°C] along a trajectory (arrays on the same time grid)."""
    n = len(t)
    sun_flux = np.zeros(n) if sun_flux is None else sun_flux
    s0 = A.state(float(h[0]), case)
    Ti = (Ti0_C + 273.15) if Ti0_C is not None else s0.T
    Ts = s0.T
    out_i, out_s = np.empty(n), np.empty(n)
    for k in range(n):
        s = A.state(float(h[k]), case)
        h_c = convection_coefficient(max(float(airspeed[k]), 1.0), v.diameter_m, s.T, s.rho)
        if k:
            dt = float(t[k] - t[k - 1])
            sub = max(1, int(math.ceil(dt / 5.0)))
            for _ in range(sub):
                q_i = float(internal_W[k]) - conductance(v, Ti, Ts) * (Ti - Ts)
                q_s = _shell_balance(v, Ts, Ti, s.T, h_c, float(sun_flux[k]))
                Ti += q_i * dt / sub / v.interior_heat_capacity_J_K
                Ts += q_s * dt / sub / v.shell_heat_capacity_J_K
        out_i[k], out_s[k] = Ti - 273.15, Ts - 273.15
    return out_i, out_s


def motor_temperature(h: float, shaft_W: float, motor_efficiency: float = 0.88, G_motor_W_K: float = 3.0,
                      case: str = "mean") -> float:
    """Steady winding temperature [°C] of one motor: ambient + losses / conductance (``G_motor`` assumed)."""
    s = A.state(h, case)
    loss = shaft_W * (1.0 / motor_efficiency - 1.0)
    return s.T - 273.15 + loss / G_motor_W_K
