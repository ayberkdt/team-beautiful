"""Unit-safe input parsing: ``"1300 km"`` → ``1.3e6`` (SI) with a dimension check.

The 2023 Ansys task card warns explicitly: "Take extra care in the unit conversions you use during
your calculations!". All of aerokit computes in SI; this module is the single place where
human-written quantities are converted. A quantity is parsed only if its unit is known *and* has the
expected dimension, so ``"150 km"`` given where a speed is expected raises instead of silently
becoming 150 000.

Numbers may use spaces or thin spaces as thousands separators (``"10 000 m"``). The ambiguous
continental form ``"10.000 m"`` (one dot followed by exactly three digits) is rejected: write
``10000`` or ``10.0``.

>>> parse("1300 km", "length")
1300000.0
>>> round(parse("150 km/h", "speed"), 4)
41.6667
>>> f"{parse('0.5 lb/(hp*h)', 'psfc'):.4e}"
'8.2849e-07'
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

__all__ = ["UnitError", "UNITS", "DIMENSIONS", "parse", "parse_mapping", "convert", "to_unit"]

_LB = 0.45359237                       # kg, exact (international pound)
_LBF = _LB * 9.80665                   # N
_FT = 0.3048                           # m, exact
_HP = 745.69987158227022               # W (mechanical horsepower, 550 ft·lbf/s)


class UnitError(ValueError):
    """Unknown unit, wrong dimension or malformed quantity."""


# dimension name → {unit spelling: factor to SI}
UNITS: dict[str, dict[str, float]] = {
    "length": {"m": 1.0, "km": 1e3, "cm": 1e-2, "mm": 1e-3, "ft": _FT, "in": 0.0254, "nmi": 1852.0,
               "mi": 1609.344},
    "area": {"m2": 1.0, "m^2": 1.0, "m²": 1.0, "ft2": _FT ** 2, "ft^2": _FT ** 2, "ft²": _FT ** 2,
             "km2": 1e6, "km^2": 1e6, "km²": 1e6, "nmi2": 1852.0 ** 2, "nmi²": 1852.0 ** 2},
    "speed": {"m/s": 1.0, "km/h": 1 / 3.6, "kmh": 1 / 3.6, "kt": 1852.0 / 3600, "kts": 1852.0 / 3600,
              "knot": 1852.0 / 3600, "mph": 1609.344 / 3600, "ft/s": _FT, "ft/min": _FT / 60, "fpm": _FT / 60},
    "time": {"s": 1.0, "min": 60.0, "h": 3600.0, "hr": 3600.0},
    "mass": {"kg": 1.0, "t": 1e3, "lb": _LB, "lbm": _LB, "g": 1e-3},
    "force": {"N": 1.0, "kN": 1e3, "lbf": _LBF},
    "power": {"W": 1.0, "kW": 1e3, "MW": 1e6, "hp": _HP, "shp": _HP},
    "pressure": {"Pa": 1.0, "kPa": 1e3, "MPa": 1e6, "psi": _LBF / 0.0254 ** 2, "bar": 1e5},
    "wing_loading": {"N/m2": 1.0, "N/m^2": 1.0, "N/m²": 1.0, "kg/m2": 9.80665, "kg/m²": 9.80665,
                     "lb/ft2": _LBF / _FT ** 2, "lb/ft²": _LBF / _FT ** 2},
    "power_loading": {"W/N": 1.0, "W/kg": 1 / 9.80665, "hp/lb": _HP / _LBF},
    "specific_power": {"W/kg": 1.0, "kW/kg": 1e3, "hp/lb": _HP / _LB},
    # power-specific fuel consumption, weight basis: N of fuel per (W·s)
    "psfc": {"N/(W*s)": 1.0, "lb/(hp*h)": _LBF / (_HP * 3600), "lb/hp/h": _LBF / (_HP * 3600),
             "kg/(kW*h)": 9.80665 / (1e3 * 3600), "g/(kW*h)": 9.80665e-3 / (1e3 * 3600)},
    # thrust-specific fuel consumption, weight basis: N of fuel per (N·s) = 1/s
    "tsfc": {"1/s": 1.0, "1/h": 1 / 3600, "lb/(lbf*h)": 1 / 3600, "kg/(N*h)": 9.80665 / 3600},
    "temperature_difference": {"K": 1.0, "degC": 1.0},
    "angle": {"rad": 1.0, "deg": math.pi / 180, "°": math.pi / 180},
    "dimensionless": {"": 1.0, "-": 1.0, "%": 0.01},
    "count": {"": 1.0, "people": 1.0, "persons": 1.0, "pax": 1.0},
}
DIMENSIONS: tuple[str, ...] = tuple(UNITS)

_NUMBER = re.compile(r"^\s*([+\-−]?[\d\s  ,.]*\d(?:[eE][+\-]?\d+)?)\s*(.*?)\s*$")


def _number(text: str) -> float:
    raw = text.replace("−", "-").replace(" ", "").replace(" ", "").replace(" ", "")
    if re.fullmatch(r"[+\-]?\d{1,3}\.\d{3}", raw):
        raise UnitError(f"ambiguous number {text.strip()!r}: write 10000 or 10.0, not 10.000")
    if "," in raw:
        if re.fullmatch(r"[+\-]?\d{1,3}(,\d{3})+(\.\d+)?", raw):
            raw = raw.replace(",", "")                     # 1,300 → 1300
        else:
            raise UnitError(f"ambiguous decimal comma in {text.strip()!r}: use a decimal point")
    try:
        value = float(raw)
    except ValueError as exc:
        raise UnitError(f"not a number: {text.strip()!r}") from exc
    if not math.isfinite(value):
        raise UnitError(f"quantity must be finite: {text.strip()!r}")
    return value


def _unit(text: str) -> str:
    u = text.strip()
    if len(u) >= 2 and (u[0], u[-1]) in (("[", "]"), ("(", ")")) and u.count(u[0]) == 1:
        u = u[1:-1].strip()                     # "[m]" → "m", but keep "lb/(hp*h)" intact
    return u.replace("·", "*").replace(" ", "")


def parse(quantity: str | float | int, dimension: str, default_unit: str | None = None) -> float:
    """Convert ``quantity`` to SI after checking its dimension.

    Parameters
    ----------
    quantity : str or number
        ``"1300 km"``, ``"10 000 [m]"``, ``"0.5 lb/(hp*h)"``; a bare number is taken in
        ``default_unit`` (SI if ``None``).
    dimension : str
        One of :data:`DIMENSIONS`.
    default_unit : str, optional
        Unit of bare numbers.

    Raises
    ------
    UnitError
        Unknown dimension or unit, unit of another dimension, malformed or non-finite number.
    """
    if dimension not in UNITS:
        raise UnitError(f"unknown dimension {dimension!r}; choose one of {', '.join(DIMENSIONS)}")
    table = UNITS[dimension]
    if isinstance(quantity, bool):
        raise UnitError("a boolean is not a quantity")
    if isinstance(quantity, int | float):
        if not math.isfinite(quantity):
            raise UnitError("quantity must be finite")
        unit = default_unit or next(iter(table))
        return float(quantity) * _factor(table, unit, dimension)
    m = _NUMBER.match(str(quantity))
    if not m:
        raise UnitError(f"cannot read a quantity from {quantity!r}")
    value = _number(m.group(1))
    unit = _unit(m.group(2)) if m.group(2) else (default_unit or next(iter(table)))
    return value * _factor(table, unit, dimension)


def _factor(table: Mapping[str, float], unit: str, dimension: str) -> float:
    if unit in table:
        return table[unit]
    for dim, other in UNITS.items():
        if unit in other and dim != dimension:
            raise UnitError(f"unit {unit!r} is a {dim}, but a {dimension} is expected")
    raise UnitError(f"unknown {dimension} unit {unit!r}; known: {', '.join(k for k in table if k)}")


def convert(value: float, from_unit: str, to_unit_: str, dimension: str) -> float:
    """Convert between two units of the same dimension."""
    t = UNITS[dimension]
    return value * _factor(t, _unit(from_unit), dimension) / _factor(t, _unit(to_unit_), dimension)


def to_unit(value_si: float, unit: str, dimension: str) -> float:
    """Express an SI value in ``unit``."""
    return value_si / _factor(UNITS[dimension], _unit(unit), dimension)


def parse_mapping(data: Mapping[str, Any], schema: Mapping[str, str]) -> dict[str, float]:
    """Parse every ``key`` of ``schema`` (``{key: dimension}``) present in ``data`` to SI.

    Unknown keys in ``data`` raise, so a typo in a requirements file is never ignored.
    """
    unknown = set(data) - set(schema)
    if unknown:
        raise UnitError(f"unknown key(s): {', '.join(sorted(unknown))}; expected: {', '.join(schema)}")
    return {k: parse(v, schema[k]) for k, v in data.items()}
