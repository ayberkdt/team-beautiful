"""Conceptual aircraft model shared by performance, mission planning and STK export.

Aerodynamics: parabolic drag polar ``C_D = C_D0 + K C_L²`` with ``K = 1/(π e AR)``, ``e`` the Oswald
efficiency factor of the complete aeroplane (Anderson 2017, Eq. 6.24; e typically 0.7–0.85).
Propulsion: an engine object from :mod:`aerokit.aero.propulsion`. All quantities SI; weights in N.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Any

from aerokit.aero.atmosphere import isa
from aerokit.aero.propulsion import Turbofan, Turboprop
from aerokit.references import cite

__all__ = ["Aircraft", "G0"]

G0 = 9.80665


@cite("anderson_2017", note="drag polar C_D = C_D0 + C_L²/(π e AR), Eq. 6.24 (PDF p. 538)")
@dataclass(frozen=True)
class Aircraft:
    """Conceptual-design aeroplane.

    Attributes
    ----------
    name : str
    W0 : float
        Maximum take-off weight [N].
    S : float
        Reference wing area [m²].
    AR : float
        Aspect ratio [-].
    CD0, e : float
        Zero-lift drag coefficient and Oswald efficiency factor.
    engine : Turboprop or Turbofan
    CLmax_clean, CLmax_takeoff, CLmax_landing : float
    W_fuel : float
        Usable fuel weight at W0 [N].
    W_empty, W_payload : float
        Operating empty and design payload weight [N] (0 if unknown).
    mu_roll : float
        Rolling friction coefficient on the runway.
    """

    name: str
    W0: float
    S: float
    AR: float
    CD0: float
    e: float
    engine: Turboprop | Turbofan
    CLmax_clean: float = 1.5
    CLmax_takeoff: float = 1.7
    CLmax_landing: float = 2.0
    W_fuel: float = 0.0
    W_empty: float = 0.0
    W_payload: float = 0.0
    mu_roll: float = 0.03

    def __post_init__(self) -> None:
        for k in ("W0", "S", "AR", "CD0", "e", "CLmax_clean", "CLmax_takeoff", "CLmax_landing"):
            v = getattr(self, k)
            if not (isinstance(v, int | float) and math.isfinite(v) and v > 0):
                raise ValueError(f"{k} must be a positive finite number, got {v!r}")
        if not 0 < self.e <= 1:
            raise ValueError("Oswald efficiency e must be in (0, 1]")
        for k in ("W_fuel", "W_empty", "W_payload", "mu_roll"):
            if getattr(self, k) < 0:
                raise ValueError(f"{k} must be >= 0")
        if self.W_fuel >= self.W0:
            raise ValueError("fuel weight must be smaller than W0")

    # ------------------------------------------------------------------ aerodynamics
    @property
    def K(self) -> float:
        """Induced-drag factor 1/(π e AR)."""
        return 1.0 / (math.pi * self.e * self.AR)

    @property
    def LD_max(self) -> float:
        """Maximum lift-to-drag ratio 1/(2√(C_D0 K)) of the parabolic polar."""
        return 1.0 / (2.0 * math.sqrt(self.CD0 * self.K))

    def CL(self, V: float, h: float, W: float | None = None, n: float = 1.0) -> float:
        """Lift coefficient for load factor ``n`` at speed ``V`` [m/s] and altitude ``h`` [m]."""
        q = 0.5 * isa(h)["rho"] * V * V
        if not q > 0:
            raise ValueError("speed must be > 0")
        return n * (self.W0 if W is None else W) / (q * self.S)

    def drag(self, V: float, h: float, W: float | None = None, n: float = 1.0) -> float:
        """Drag [N] in steady flight."""
        cl = self.CL(V, h, W, n)
        return 0.5 * isa(h)["rho"] * V * V * self.S * (self.CD0 + self.K * cl * cl)

    def power_required(self, V: float, h: float, W: float | None = None) -> float:
        """Thrust power required for level flight D·V [W]."""
        return self.drag(V, h, W) * V

    def power_available(self, V: float, h: float, takeoff: bool = False) -> float:
        """Full-throttle thrust power [W]."""
        return self.engine.thrust_power(V, h, takeoff)

    def stall_speed(self, h: float, W: float | None = None, CLmax: float | None = None) -> float:
        """1-g stall speed [m/s] (clean CLmax unless given)."""
        cl = self.CLmax_clean if CLmax is None else CLmax
        return math.sqrt(2.0 * (self.W0 if W is None else W) / (isa(h)["rho"] * self.S * cl))

    def fuel_flow(self, V: float, h: float, W: float | None = None) -> float:
        """Fuel weight flow in steady level flight [N/s]."""
        return self.engine.fuel_flow(V, h, self.power_required(V, h, W))

    # ------------------------------------------------------------------ helpers
    @property
    def wing_loading(self) -> float:
        """W0/S [N/m²]."""
        return self.W0 / self.S

    def with_(self, **changes: Any) -> Aircraft:
        """Copy with some attributes changed (used by sensitivity studies)."""
        return replace(self, **changes)
