"""Engine models for conceptual performance: turboprop/piston (shaft power) and turbofan (thrust).

Altitude lapse is the most sensitive assumption of the 2023 rehearsal (the 10 000 m ceiling governs
the installed power, docs/04 §1), so it is an explicit, selectable model here:

* ``"sigma"``    — P(h)/P_SL = σ (density ratio), the rehearsal's assumption;
* ``"sigma^n"``  — P(h)/P_SL = σⁿ with ``n`` given (n < 1: less loss with altitude);
* ``"table"``    — interpolation in a user-supplied engine deck ``[(h, ratio), ...]``.

No lapse exponent is asserted as "correct" here: ``n`` must come from engine data or be varied in a
sensitivity study (:mod:`aerokit.aero.design_study`). Fuel consumption is weight-specific
(N of fuel per W·s or per N·s); use :func:`aerokit.units.parse` with ``"lb/(hp*h)"`` or
``"lb/(lbf*h)"`` to enter handbook values.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from aerokit.aero.atmosphere import sigma
from aerokit.references import cite
from aerokit.units import parse

__all__ = ["Turboprop", "Turbofan", "lapse_ratio"]

# defaults through the unit layer: a hand-typed 8.4e-8 was once 10× wrong here
_PSFC_DEFAULT = parse("0.5 lb/(hp*h)", "psfc")
_TSFC_DEFAULT = parse("0.6 lb/(lbf*h)", "tsfc")


def lapse_ratio(h: float, model: str = "sigma", n: float = 1.0,
                table: Sequence[tuple[float, float]] = ()) -> float:
    """Available-power (or thrust) ratio P(h)/P_SL.

    Raises
    ------
    ValueError
        Unknown model, non-positive exponent, or an engine table that is empty or not increasing in h.
    """
    if model == "sigma":
        return float(sigma(h))
    if model == "sigma^n":
        if not n > 0:
            raise ValueError("lapse exponent n must be > 0")
        return float(sigma(h)) ** n
    if model == "table":
        if len(table) < 2:
            raise ValueError("an engine table needs at least two (h, ratio) points")
        hs, rs = np.array([p[0] for p in table], float), np.array([p[1] for p in table], float)
        if np.any(np.diff(hs) <= 0) or np.any(rs <= 0):
            raise ValueError("engine table altitudes must increase and ratios be positive")
        if not hs[0] <= h <= hs[-1]:
            raise ValueError(f"altitude {h:g} m outside the engine table ({hs[0]:g}–{hs[-1]:g} m)")
        return float(np.interp(h, hs, rs))
    raise ValueError(f"unknown lapse model {model!r} (sigma, sigma^n, table)")


@cite("raymer_2018", note="propeller thrust T = η_p P/V; ground-run thrust taken at 0.7 V_LOF "
                         "(conceptual-sizing practice; book not read in this session)")
@dataclass(frozen=True)
class Turboprop:
    """Shaft-power engine(s) with a propeller.

    Attributes
    ----------
    P_sl : float
        Total installed shaft power at sea level [W].
    eta : float
        Propeller efficiency in climb/cruise [-].
    eta_takeoff : float
        Effective propeller efficiency during the take-off run [-].
    psfc : float
        Power-specific fuel consumption, weight basis [N/(W·s)].
    lapse, n, table
        Altitude lapse model, see :func:`lapse_ratio`.
    """

    P_sl: float
    eta: float = 0.8
    eta_takeoff: float = 0.6
    psfc: float = _PSFC_DEFAULT                # 0.5 lb/(hp·h) — the rehearsal's cruise value
    lapse: str = "sigma"
    n: float = 1.0
    table: tuple[tuple[float, float], ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.P_sl > 0:
            raise ValueError("P_sl must be > 0")
        for name in ("eta", "eta_takeoff"):
            v = getattr(self, name)
            if not 0 < v <= 1:
                raise ValueError(f"{name} must be in (0, 1]")
        if not self.psfc > 0:
            raise ValueError("psfc must be > 0")
        lapse_ratio(0.0 if not self.table else self.table[0][0], self.lapse, self.n, self.table)

    def shaft_power(self, h: float, throttle: float = 1.0) -> float:
        """Shaft power at altitude [W]."""
        if not 0 <= throttle <= 1:
            raise ValueError("throttle must be in [0, 1]")
        return throttle * self.P_sl * lapse_ratio(h, self.lapse, self.n, self.table)

    def thrust_power(self, V: float, h: float, takeoff: bool = False) -> float:
        """Available thrust power η·P(h) at full throttle [W] (independent of V)."""
        del V
        return (self.eta_takeoff if takeoff else self.eta) * self.shaft_power(h)

    def thrust(self, V: float, h: float, takeoff: bool = False) -> float:
        """Thrust η P / V [N] (``V`` > 0; for the take-off run evaluate at ≈ 0.7 V_LOF)."""
        if not V > 0:
            raise ValueError("thrust of a propeller needs V > 0 (use 0.7 V_LOF for the ground run)")
        return self.thrust_power(V, h, takeoff) / V

    def fuel_flow(self, V: float, h: float, thrust_power: float) -> float:
        """Fuel weight flow [N/s] to deliver ``thrust_power`` = T·V [W] (shaft power = TV/η)."""
        del V, h                                    # psfc taken constant with speed and altitude
        if thrust_power < 0:
            raise ValueError("thrust power must be >= 0")
        return self.psfc * thrust_power / self.eta


@dataclass(frozen=True)
class Turbofan:
    """Thrust engine(s): sea-level static thrust with a lapse model and a TSFC [1/s]."""

    T_sl: float
    tsfc: float = _TSFC_DEFAULT                  # 0.6 lb/(lbf·h)
    lapse: str = "sigma"
    n: float = 1.0
    table: tuple[tuple[float, float], ...] = field(default=())

    def __post_init__(self) -> None:
        if not self.T_sl > 0 or not self.tsfc > 0:
            raise ValueError("T_sl and tsfc must be > 0")

    def thrust(self, V: float, h: float, takeoff: bool = False) -> float:
        """Available thrust [N] (taken independent of V)."""
        del V, takeoff
        return self.T_sl * lapse_ratio(h, self.lapse, self.n, self.table)

    def thrust_power(self, V: float, h: float, takeoff: bool = False) -> float:
        """Available thrust power T(h)·V [W]."""
        return self.thrust(V, h, takeoff) * V

    def fuel_flow(self, V: float, h: float, thrust_power: float) -> float:
        """Fuel weight flow [N/s] = TSFC · T with T = thrust_power / V."""
        del h
        if not V > 0 or thrust_power < 0:
            raise ValueError("V must be > 0 and thrust power >= 0")
        return self.tsfc * thrust_power / V
