"""Battery-electric aircraft, UAV and multirotor/eVTOL first-order sizing.

**Fixed wing** (Hepperle 2012, slides 16–20; the relations are derived here because the slides show them as
images). The mass is constant in flight, so with battery energy ``E = E* m_b``, cruise power
``P = m g V / (η L/D)`` and range ``R = V t = V E / P``:

    R = (E* η / g) · (L/D) · (m_b / m)                                            (range)
    m = m_payload / (1 − m_e/m − g R / (E* η L/D))                               (sizing for a range)

``E*`` is the *pack* specific energy [J/kg], ``η`` the battery-to-thrust efficiency. Setting the payload to zero
gives the limit range ``R_max = (E* η / g)(L/D)(1 − m_e/m)`` that no design with this technology can exceed;
``R = 0`` gives the minimum mass ``m_payload / (1 − m_e/m)``. No reserve, climb or descent is included.

**Endurance** at the speed of minimum power: ``t = E* m_b η / P_min``.

**Hover** (actuator-disk momentum theory, derived here; no rotorcraft text was read): the ideal induced power of
a rotor of disk area ``A`` producing thrust ``T`` is ``P_i = T^{3/2} / √(2 ρ A)``; the shaft power is
``P_i / FM`` with the figure of merit ``FM`` (a parameter). The induced velocity is ``v_i = √(T / (2 ρ A))``.

All technology values (E*, η, FM, empty-mass fraction) are parameters to be chosen and justified.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from aerokit.references import cite

__all__ = ["G0", "WH_PER_KG", "battery_range", "battery_mass_fraction_for_range", "electric_takeoff_mass",
           "max_range_payload_zero", "battery_endurance", "hover_power", "induced_velocity", "MultirotorSizing",
           "size_multirotor"]

G0 = 9.80665
WH_PER_KG = 3600.0          # 1 Wh/kg in J/kg


def _positive(**kw: float) -> None:
    for k, v in kw.items():
        if not (math.isfinite(v) and v > 0):
            raise ValueError(f"{k} must be a positive finite number, got {v!r}")


def _fraction(name: str, v: float) -> None:
    if not 0.0 <= v < 1.0:
        raise ValueError(f"{name} must be in [0, 1), got {v!r}")


@cite("hepperle_2012", note="battery range, mass constant in flight (derived here)")
def battery_range(specific_energy_J_kg: float, efficiency: float, LD: float, battery_fraction: float) -> float:
    """Range [m] of a battery-electric aircraft: ``(E* η / g)(L/D)(m_b/m)``."""
    _positive(specific_energy_J_kg=specific_energy_J_kg, LD=LD)
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    _fraction("battery_fraction", battery_fraction)
    return specific_energy_J_kg * efficiency / G0 * LD * battery_fraction


def battery_mass_fraction_for_range(range_m: float, specific_energy_J_kg: float, efficiency: float,
                                    LD: float) -> float:
    """Battery mass fraction ``m_b/m = g R / (E* η L/D)`` needed for ``range_m``."""
    _positive(specific_energy_J_kg=specific_energy_J_kg, LD=LD)
    if not (range_m >= 0 and 0 < efficiency <= 1):
        raise ValueError("range must be >= 0 and efficiency in (0, 1]")
    return G0 * range_m / (specific_energy_J_kg * efficiency * LD)


@cite("hepperle_2012", note="sizing equation for a given range (slide 20, derived here)")
def electric_takeoff_mass(payload_kg: float, range_m: float, specific_energy_J_kg: float, efficiency: float,
                          LD: float, empty_fraction: float) -> dict[str, float]:
    """Take-off mass for ``range_m``: ``m = m_payload / (1 − m_e/m − m_b/m)``.

    Returns ``mass``, ``battery_mass``, ``empty_mass``, ``battery_fraction`` [kg, -].

    Raises
    ------
    ValueError
        No solution: empty and battery fractions reach 1 (the range is beyond this technology).
    """
    _positive(payload_kg=payload_kg)
    _fraction("empty_fraction", empty_fraction)
    fb = battery_mass_fraction_for_range(range_m, specific_energy_J_kg, efficiency, LD)
    rest = 1.0 - empty_fraction - fb
    if rest <= 0:
        r_max = max_range_payload_zero(specific_energy_J_kg, efficiency, LD, empty_fraction)
        raise ValueError(f"no solution: empty fraction {empty_fraction:.3f} + battery fraction {fb:.3f} >= 1 "
                         f"(maximum range with zero payload is {r_max / 1e3:.0f} km)")
    m = payload_kg / rest
    return {"mass": m, "battery_mass": fb * m, "empty_mass": empty_fraction * m, "battery_fraction": fb}


@cite("hepperle_2012", note="payload-zero limit range (slide 19)")
def max_range_payload_zero(specific_energy_J_kg: float, efficiency: float, LD: float, empty_fraction: float) -> float:
    """Range limit [m] with zero payload: ``(E* η / g)(L/D)(1 − m_e/m)``."""
    _fraction("empty_fraction", empty_fraction)
    _positive(specific_energy_J_kg=specific_energy_J_kg, LD=LD)
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    return specific_energy_J_kg * efficiency / G0 * LD * (1.0 - empty_fraction)


def battery_endurance(battery_mass_kg: float, specific_energy_J_kg: float, efficiency: float, power_W: float) -> float:
    """Endurance [s] drawing ``power_W`` (thrust power) from the battery: ``E* m_b η / P``."""
    _positive(battery_mass_kg=battery_mass_kg, specific_energy_J_kg=specific_energy_J_kg, power_W=power_W)
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    return specific_energy_J_kg * battery_mass_kg * efficiency / power_W


def induced_velocity(thrust_N: float, rho: float, disk_area_m2: float) -> float:
    """Momentum-theory induced velocity in hover ``√(T / (2 ρ A))`` [m/s]."""
    _positive(thrust_N=thrust_N, rho=rho, disk_area_m2=disk_area_m2)
    return math.sqrt(thrust_N / (2.0 * rho * disk_area_m2))


def hover_power(thrust_N: float, rho: float, disk_area_m2: float, figure_of_merit: float = 1.0) -> float:
    """Shaft power to hover [W]: ``T^{3/2} / (FM √(2 ρ A))`` (``FM = 1``: ideal induced power)."""
    if not 0 < figure_of_merit <= 1:
        raise ValueError("figure_of_merit must be in (0, 1]")
    return thrust_N * induced_velocity(thrust_N, rho, disk_area_m2) / figure_of_merit


@dataclass(frozen=True)
class MultirotorSizing:
    """Result of :func:`size_multirotor` (SI)."""

    mass: float
    battery_mass: float
    empty_mass: float
    hover_power: float
    disk_loading: float
    iterations: int


def size_multirotor(payload_kg: float, hover_time_s: float, rotor_count: int, rotor_diameter_m: float, *,
                    specific_energy_J_kg: float, efficiency: float, figure_of_merit: float, empty_fraction: float,
                    rho: float = 1.225, g: float = G0, tol_kg: float = 1e-6,
                    max_iter: int = 200) -> MultirotorSizing:
    """Mass of a battery multirotor that hovers for ``hover_time_s`` (``g``: local gravity, e.g. 8.87 on Venus).

    ``m (1 − m_e/m) = m_payload + m_b(m)`` with ``m_b = P_hover(m g) t / (E* η) = k m^{3/2}``; ``efficiency`` is
    battery to shaft. ``f(m) = m (1 − m_e/m) − m_payload − k m^{3/2}`` is concave with its maximum at
    ``m* = ((1 − m_e/m) / (1.5 k))²``: there is no design if ``f(m*) < 0``, otherwise the lighter root is bracketed
    in ``[m_payload/(1 − m_e/m), m*]`` and found by Brent's method (``iterations`` reports its function calls).

    Raises
    ------
    ValueError
        Invalid inputs, or no solution (the battery for the hover time weighs more than the rotors can lift).
    """
    from scipy.optimize import brentq

    _positive(payload_kg=payload_kg, hover_time_s=hover_time_s, rotor_diameter_m=rotor_diameter_m,
              specific_energy_J_kg=specific_energy_J_kg, g=g)
    if rotor_count < 1:
        raise ValueError("rotor_count must be >= 1")
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must be in (0, 1]")
    _fraction("empty_fraction", empty_fraction)
    area = rotor_count * math.pi * rotor_diameter_m ** 2 / 4.0
    k = hover_power(g, rho, area, figure_of_merit) * hover_time_s / (specific_energy_J_kg * efficiency)  # m_b/m^1.5
    free = 1.0 - empty_fraction

    def f(m: float) -> float:
        return float(m * free - payload_kg - k * m ** 1.5)

    m_star = (free / (1.5 * k)) ** 2
    if f(m_star) < 0:
        raise ValueError("no solution: the battery needed for the hover time grows faster than the lift "
                         "(shorten the hover time, enlarge the rotors or raise E*)")
    m, info = brentq(f, payload_kg / free, m_star, xtol=tol_kg, maxiter=max_iter, full_output=True)
    P = hover_power(m * g, rho, area, figure_of_merit)
    return MultirotorSizing(m, k * m ** 1.5, empty_fraction * m, P, m * g / area, int(info.function_calls))
