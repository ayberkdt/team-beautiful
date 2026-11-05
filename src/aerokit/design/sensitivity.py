"""One-at-a-time sensitivity of the sized design to every assumption (tornado data).

Each numeric assumption is moved to a low and a high value (default ±10 %, or a documented range),
the full sizing chain is re-run, and the change of take-off mass and installed power is recorded.
The power-lapse model is varied through its exponent (P/P_SL = σⁿ, n from 0.7 to 1.0) because it is
the most sensitive assumption of the 2023 rehearsal (docs/04 §1).
"""
from __future__ import annotations

from dataclasses import dataclass

from aerokit.design.requirements import Assumptions, Requirements
from aerokit.design.sizing import SizingResult, size

__all__ = ["SensitivityRow", "DEFAULT_RANGES", "tornado"]

#: absolute (low, high) ranges for assumptions whose ±10 % is not meaningful
DEFAULT_RANGES: dict[str, tuple[float, float]] = {
    "power_lapse_n": (0.7, 1.0),
    "propeller_efficiency": (0.75, 0.85),
    "takeoff_propeller_efficiency": (0.5, 0.7),
    "CLmax_landing": (1.8, 2.2),
    "empty_weight_factor": (1.0, 1.118),      # Raymer regression → King Air 350i calibration
    "CD0_override": (0.0, 0.0),               # not a free assumption (set by the drag build-up)
    "e_override": (0.0, 0.0),
}


@dataclass(frozen=True)
class SensitivityRow:
    """Result of moving one assumption to its low and high value."""

    key: str
    base: float
    low: float
    high: float
    mass_low: float
    mass_high: float
    power_low: float
    power_high: float
    governing_low: str
    governing_high: str

    @property
    def mass_swing(self) -> float:
        """|Δm| between the two ends [kg] (tornado ordering)."""
        return abs(self.mass_high - self.mass_low)

    @property
    def power_swing(self) -> float:
        """|ΔP| between the two ends [W]."""
        return abs(self.power_high - self.power_low)


def tornado(req: Requirements, asm: Assumptions, fraction: float = 0.10,
            ranges: dict[str, tuple[float, float]] | None = None,
            keys: tuple[str, ...] | None = None) -> tuple[SizingResult, list[SensitivityRow]]:
    """Run the sensitivity study; rows sorted by power swing (largest first).

    Assumptions that make the chain infeasible at one end are reported with NaN at that end.
    """
    if not 0 < fraction < 1:
        raise ValueError("fraction must be in (0, 1)")
    base = size(req, asm)
    rng = {**DEFAULT_RANGES, **(ranges or {})}
    numeric = [k for k, v in asm.values.items() if isinstance(v, int | float) and not isinstance(v, bool)]
    rows: list[SensitivityRow] = []
    for k in keys or tuple(numeric):
        if k not in asm.values:
            raise KeyError(f"unknown assumption {k!r}")
        b = float(asm[k])
        lo, hi = rng.get(k, (b * (1 - fraction), b * (1 + fraction)))
        ends = []
        for v in (lo, hi):
            changes: dict[str, object] = {k: v}
            if k == "power_lapse_n":
                changes["power_lapse"] = "sigma^n"
            try:
                r = size(req, asm.with_(**changes))
                ends.append((r.mass, r.P_installed, r.governing))
            except (ValueError, ArithmeticError):
                ends.append((float("nan"), float("nan"), "infeasible"))
        (m_lo, p_lo, g_lo), (m_hi, p_hi, g_hi) = ends
        rows.append(SensitivityRow(k, b, lo, hi, m_lo, m_hi, p_lo, p_hi, g_lo, g_hi))
    rows.sort(key=lambda r: -(r.power_swing if r.power_swing == r.power_swing else -1.0))
    return base, rows
