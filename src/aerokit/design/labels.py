"""Human-readable names and display units of the design assumptions (figures and reports)."""
from __future__ import annotations

from aerokit import units

__all__ = ["DISPLAY", "label", "display_value", "signed_percent"]

#: key → (display name, unit, dimension); unit "" means dimensionless
DISPLAY: dict[str, tuple[str, str, str]] = {
    "aspect_ratio": ("Aspect ratio", "", "dimensionless"),
    "K_LD": ("K_LD (L/D factor)", "", "dimensionless"),
    "wetted_area_ratio": ("Swet/Sref", "", "dimensionless"),
    "propeller_efficiency": ("Propeller efficiency", "", "dimensionless"),
    "takeoff_propeller_efficiency": ("Take-off propeller efficiency", "", "dimensionless"),
    "psfc_cruise": ("PSFC cruise", "lb/(hp*h)", "psfc"),
    "psfc_loiter": ("PSFC loiter", "lb/(hp*h)", "psfc"),
    "loiter_speed": ("Loiter speed", "km/h", "speed"),
    "CLmax_clean": ("CLmax clean", "", "dimensionless"),
    "CLmax_takeoff": ("CLmax take-off", "", "dimensionless"),
    "CLmax_landing": ("CLmax landing", "", "dimensionless"),
    "power_lapse_n": ("Power lapse exponent n (σⁿ)", "", "dimensionless"),
    "rolling_friction": ("Rolling friction μ", "", "dimensionless"),
    "taper_ratio": ("Taper ratio", "", "dimensionless"),
    "empty_weight_factor": ("Empty-weight factor (× Raymer)", "", "dimensionless"),
    "engine_specific_power": ("Engine specific power", "kW/kg", "specific_power"),
}


def display_value(key: str, value_si: float) -> str:
    """Value of an assumption in its display unit, 3 significant digits, never E notation."""
    name, unit, dim = DISPLAY.get(key, (key, "", "dimensionless"))
    v = units.to_unit(value_si, unit, dim) if unit else value_si
    text = f"{v:.3g}"
    if "e" in text:
        text = f"{v:.4f}".rstrip("0").rstrip(".")
    return text


def signed_percent(fraction: float, digits: int = 1) -> str:
    """``0.123`` → ``"+12.3 %"``; a value that rounds to zero prints ``"0.0 %"``, never ``"-0.0 %"``."""
    value = round(fraction * 100, digits)
    return f"{0.0:.{digits}f} %" if value == 0 else f"{value:+.{digits}f} %"


def label(key: str, low: float | None = None, high: float | None = None) -> str:
    """``"PSFC cruise 0.45–0.55 lb/(hp·h)"`` style label (range optional)."""
    name, unit, _ = DISPLAY.get(key, (key, "", "dimensionless"))
    rng = f" {display_value(key, low)}–{display_value(key, high)}" if low is not None and high is not None else ""
    return f"{name}{rng}" + (f" {unit.replace('*', '·')}" if unit and rng else "")
