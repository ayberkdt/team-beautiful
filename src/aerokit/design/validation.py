"""Validation of the analysis chain against a real aircraft (King Air 350i).

Published data (Wikipedia "Beechcraft Super King Air", Specifications table, 350i column, read on
2026-10-25; the table cites the 2016 Beechcraft product cards, which were not read): MTOW 6 804 kg,
OEW 4 516 kg, span 17.65 m, 2 × 783 kW (PT6A-60A), maximum cruise 578 km/h, take-off 1 006 m, ceiling
10 668 m (the page does not say which variant this ceiling belongs to). The **wing area 28.8 m² is
not on that page** (it comes from docs/04 §2, a sub-agent summary) and is an unverified input.

The model is *not* tuned to these values: drag comes from the component build-up of
:mod:`aerokit.design.configuration`, propulsion uses the default turboprop assumptions. The output is
a table of predicted vs published values with the error, so the size of the model error is visible.
"""
from __future__ import annotations

from dataclasses import dataclass

from aerokit.aero import performance as perf
from aerokit.aero import sizing as rs
from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.propulsion import Turboprop
from aerokit.design.configuration import buildup_polar

__all__ = ["KING_AIR_350I", "ValidationRow", "validate_king_air"]

KING_AIR_350I: dict[str, tuple[float, str]] = {
    "mtow_kg": (6804.0, "Wikipedia 350i column (read 2026-10-25)"),
    "oew_kg": (4516.0, "Wikipedia 350i column"),
    "span_m": (17.65, "Wikipedia 350i column"),
    "power_W": (2 * 783e3, "Wikipedia: 2 × PT6A-60A, 783 kW each"),
    "max_cruise_kmh": (578.0, "Wikipedia 350i column (altitude not given)"),
    "takeoff_m": (1006.0, "Wikipedia 350i column (definition not given; compared with the 50 ft distance)"),
    "ceiling_m": (10668.0, "Wikipedia 'Ceiling' row (variant not given)"),
    "wing_area_m2": (28.8, "docs/04 §2 [A] — NOT on the Wikipedia page, unverified"),
}


@dataclass(frozen=True)
class ValidationRow:
    """Predicted vs published value."""

    quantity: str
    published: float
    predicted: float
    unit: str
    note: str

    @property
    def error(self) -> float:
        """(predicted − published)/published."""
        return (self.predicted - self.published) / self.published


def validate_king_air(cruise_altitude: float = 7000.0, taper: float = 0.45) -> list[ValidationRow]:
    """Predict King Air 350i performance with the toolkit and compare with the published values."""
    v = {k: x[0] for k, x in KING_AIR_350I.items()}
    W0, S = v["mtow_kg"] * G0, v["wing_area_m2"]
    AR = v["span_m"] ** 2 / S
    polar = buildup_polar(S, AR, taper, v["max_cruise_kmh"] / 3.6, cruise_altitude)
    ac = Aircraft("King Air 350i (model)", W0, S, AR, float(polar.CD0), float(polar.e), Turboprop(v["power_W"]),
                  W_empty=v["oew_kg"] * G0)
    rows = [ValidationRow("Service ceiling", v["ceiling_m"], perf.service_ceiling(ac), "m",
                          "σ power lapse, MTOW, η 0.8")]
    best_v, best_h = 0.0, 0.0
    for h in range(0, 9001, 500):
        try:
            vh = perf.max_speed(ac, float(h))
        except ValueError:
            continue
        if vh > best_v:
            best_v, best_h = vh, float(h)
    rows.append(ValidationRow("Maximum level speed (best altitude)", v["max_cruise_kmh"], best_v * 3.6, "km/h",
                              f"model maximum at {best_h:.0f} m; published value is 'maximum cruise'"))
    to = perf.takeoff_distance(ac)
    rows.append(ValidationRow("Take-off distance to 50 ft", v["takeoff_m"], float(to["total"]), "m",
                              "CLmax TO 1.7, η_TO 0.6 (assumptions); published definition unknown"))
    rows.append(ValidationRow("Empty-weight fraction We/W0", v["oew_kg"] / v["mtow_kg"],
                              rs.empty_weight_ratio(W0, "twin turboprop"), "-",
                              "Raymer Table 3.1 twin-turboprop regression"))
    rows.append(ValidationRow("L/Dmax (build-up)", float("nan"), float(polar.LD_max), "-",
                              f"CD0 {polar.CD0:.4f}, e {polar.e:.3f}; no published value to compare"))
    return rows


def calibrate_lapse_exponent(target_ceiling: float | None = None, cruise_altitude: float = 7000.0,
                             taper: float = 0.45) -> float:
    """Exponent n of P/P_SL = σⁿ that makes the model King Air 350i reach the published ceiling.

    This is an explicit, one-aircraft calibration (state it when used); it does not make the speed
    match as well — see :func:`validate_king_air`.
    """
    from scipy.optimize import brentq

    v = {k: x[0] for k, x in KING_AIR_350I.items()}
    target = v["ceiling_m"] if target_ceiling is None else target_ceiling
    S = v["wing_area_m2"]
    AR = v["span_m"] ** 2 / S
    polar = buildup_polar(S, AR, taper, v["max_cruise_kmh"] / 3.6, cruise_altitude)

    def miss(n: float) -> float:
        ac = Aircraft("k", v["mtow_kg"] * G0, S, AR, float(polar.CD0), float(polar.e),
                      Turboprop(v["power_W"], lapse="sigma^n", n=n))
        return perf.service_ceiling(ac) - target
    return float(brentq(miss, 0.5, 1.0, xtol=1e-6))
