"""Requirements and assumptions files for the conceptual-design pipeline.

Both are JSON objects whose values carry units (``"range": "1300 km"``), parsed with
:mod:`aerokit.units`. Unknown keys raise, so a typo never silently falls back to a default. Every
assumption keeps its default *and* a note of where the value comes from, so the report can print a
complete assumption table.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aerokit import units

__all__ = ["REQUIREMENT_SCHEMA", "ASSUMPTION_SCHEMA", "ASSUMPTION_DEFAULTS", "Requirements", "Assumptions",
           "load_requirements", "load_assumptions"]

REQUIREMENT_SCHEMA: dict[str, str] = {
    "range": "length", "loiter": "time", "stall_speed": "speed", "max_speed": "speed",
    "max_speed_altitude": "length", "service_ceiling": "length", "rate_of_climb": "speed",
    "takeoff_ground_roll": "length", "landing_distance": "length", "crew": "count", "passengers": "count",
    "person_mass": "mass", "cargo_mass": "mass",
}
_TEXT_KEYS = {"name", "source", "notes"}

#: key → (dimension, default, source of the default)
ASSUMPTION_DEFAULTS: dict[str, tuple[str, Any, str]] = {
    "aircraft_type": ("text", "twin turboprop", "Raymer Table 3.1 class (assumption)"),
    "aspect_ratio": ("dimensionless", 9.0, "assumption; comparable: C-212 AR 10, CN-235 AR 11.27"),
    "K_LD": ("dimensionless", 11.0, "Raymer K_LD for retractable-gear propeller aircraft (via CSV, not read)"),
    "wetted_area_ratio": ("dimensionless", 5.5, "assumption"),
    "propeller_efficiency": ("dimensionless", 0.8, "Raymer Table 3.4 (search summary)"),
    "takeoff_propeller_efficiency": ("dimensionless", 0.6, "assumption"),
    "psfc_cruise": ("psfc", "0.5 lb/(hp*h)", "turboprop, METU AE172 lecture 5"),
    "psfc_loiter": ("psfc", "0.6 lb/(hp*h)", "turboprop, METU AE172 lecture 5"),
    "loiter_speed": ("speed", "250 km/h", "assumption"),
    "CLmax_clean": ("dimensionless", 1.5, "choice within Scholz Table 5.1 range 1.2-1.8"),
    "CLmax_takeoff": ("dimensionless", 1.7, "choice within Scholz Table 5.1 range 1.4-2.0"),
    "CLmax_landing": ("dimensionless", 2.0, "choice within Scholz Table 5.1 range 1.6-2.5"),
    "power_lapse": ("text", "sigma", "assumption P/P_SL = σ (most sensitive, docs/04 §1)"),
    "power_lapse_n": ("dimensionless", 1.0, "exponent for power_lapse = 'sigma^n'"),
    "rolling_friction": ("dimensionless", 0.03, "assumption, paved runway"),
    "taper_ratio": ("dimensionless", 0.5, "assumption"),
    "drag_method": ("text", "kld", "kld = L/Dmax from K_LD·√(AR/(Swet/Sref)); buildup = component build-up"),
    "CD0_override": ("dimensionless", 0.0, "0 = not used; > 0 replaces the K_LD-derived CD0"),
    "e_override": ("dimensionless", 0.0, "0 = not used; > 0 replaces the Raymer Oswald e"),
    "cruise_altitude": ("length", "3000 m", "assumption (drag build-up Reynolds number)"),
    "empty_weight_factor": ("dimensionless", 1.0, "multiplier on Raymer We/W0; King Air 350i calibration 1.118 "
                                                  "(aerokit.design.validation)"),
    "wing_loading": ("text", "max", "max = largest W/S allowed by stall and landing (smallest wing); "
                                    "min_power = W/S of the lowest governing P/W below that limit"),
    "power_weight_coupling": ("text", "on", "on = engine mass follows the installed power relative to the class "
                                            "reference (design.sizing.CLASS_POWER_REFERENCE); off = Raymer We/W0 "
                                            "only, reproduces docs/04"),
    "engine_specific_power": ("specific_power", "3.53 kW/kg", "PT6A-60A 780 kW / 221 kg dry (Wikipedia PT6, read "
                                                              "2026-10-25); dry engine, no nacelle or propeller"),
}
ASSUMPTION_SCHEMA = {k: v[0] for k, v in ASSUMPTION_DEFAULTS.items()}


def _parse(data: Mapping[str, Any], schema: Mapping[str, str], what: str) -> dict[str, Any]:
    unknown = set(data) - set(schema) - _TEXT_KEYS
    if unknown:
        raise units.UnitError(f"unknown {what} key(s): {', '.join(sorted(unknown))}; "
                              f"expected: {', '.join(schema)}")
    out: dict[str, Any] = {}
    for k, v in data.items():
        if k in _TEXT_KEYS or schema.get(k) == "text":
            if not isinstance(v, str):
                raise units.UnitError(f"{what} {k!r} must be text")
            out[k] = v
        else:
            out[k] = units.parse(v, schema[k])
    return out


@dataclass(frozen=True)
class Requirements:
    """Mission/performance requirements in SI (missing ones are ``None``)."""

    values: Mapping[str, float]
    name: str = "requirements"
    raw: Mapping[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: float | None = None) -> float | None:
        """SI value of ``key`` (or ``default``)."""
        return self.values.get(key, default)

    def require(self, key: str) -> float:
        """SI value of ``key``; raise ``KeyError`` with a helpful message if missing."""
        if key not in self.values:
            raise KeyError(f"requirement {key!r} is needed by this calculation but not given")
        return float(self.values[key])

    @property
    def payload_mass(self) -> float:
        """Crew + passengers × person mass + cargo [kg]."""
        n = self.values.get("crew", 0.0) + self.values.get("passengers", 0.0)
        return n * self.values.get("person_mass", 91.0) + self.values.get("cargo_mass", 0.0)


@dataclass(frozen=True)
class Assumptions:
    """Design assumptions in SI with their sources."""

    values: Mapping[str, Any]
    sources: Mapping[str, str]
    raw: Mapping[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

    def with_(self, **changes: Any) -> Assumptions:
        """Copy with some SI values changed (sensitivity studies)."""
        unknown = set(changes) - set(self.values)
        if unknown:
            raise KeyError(f"unknown assumption(s): {', '.join(sorted(unknown))}")
        return Assumptions({**self.values, **changes}, {**self.sources, **{k: "sensitivity variation"
                                                                          for k in changes}}, self.raw)

    def table(self) -> list[list[str]]:
        """Rows ``[key, value as given, source]`` for the report."""
        rows = []
        for k, (_dim, default, _) in ASSUMPTION_DEFAULTS.items():
            given = self.raw.get(k, default)
            rows.append([k, str(given), self.sources[k]])
        return rows


def _load_json(path: str | Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(path, Mapping):
        return dict(path)
    p = Path(path)
    if p.stat().st_size > 1_000_000:
        raise ValueError(f"{p} is larger than 1 MB; not a requirements file")
    with open(p, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{p}: top level must be a JSON object")
    return data


def load_requirements(path: str | Path | Mapping[str, Any]) -> Requirements:
    """Read and unit-parse a requirements file (or mapping)."""
    raw = _load_json(path)
    vals = _parse(raw, REQUIREMENT_SCHEMA, "requirement")
    name = str(vals.pop("name", raw.get("name", "requirements")))
    for k in ("source", "notes"):
        vals.pop(k, None)
    return Requirements({k: float(v) for k, v in vals.items()}, name, raw)


def load_assumptions(path: str | Path | Mapping[str, Any] | None = None) -> Assumptions:
    """Read assumptions (missing keys take their documented defaults)."""
    raw = _load_json(path) if path is not None else {}
    parsed = _parse(raw, ASSUMPTION_SCHEMA, "assumption")
    vals: dict[str, Any] = {}
    sources: dict[str, str] = {}
    for k, (dim, default, src) in ASSUMPTION_DEFAULTS.items():
        if k in parsed:
            vals[k], sources[k] = parsed[k], "given in the assumptions file"
        else:
            vals[k] = default if dim == "text" else units.parse(default, dim)
            sources[k] = src
    if vals["power_lapse"] not in ("sigma", "sigma^n"):
        raise units.UnitError("power_lapse must be 'sigma' or 'sigma^n'")
    if vals["drag_method"] not in ("kld", "buildup"):
        raise units.UnitError("drag_method must be 'kld' or 'buildup'")
    return Assumptions(vals, sources, raw)
