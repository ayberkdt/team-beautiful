"""Sourced material pool: 31 aerospace materials with tagged properties (density, E, strength, fatigue, thermal,
embodied CO₂, price) and the bridge to the Ashby ranking of :mod:`aerokit.materials.selection`.

The data file ``aerokit/data/materials/materials_pool.json`` is a copy of
``prev_guess/01_Ansys/research/Malzeme havuzu/materials_pool.json`` (built 2026-11-03 from MIL-HDBK-5J, manufacturer datasheets,
ICE v2.0 and the project's research notes; the README beside it lists the conflicts and gaps). Every property is
``{"value", "unit", "source", "tag"}`` with tag D (read from the primary source), S (secondary) or Y (estimate or
stand-in). Units: rho kg/m3, E GPa, Fty/Ftu/fatigue MPa, k W/mK, cte 1e-6/K, Tmax C, co2 kg CO2e/kg.

Design allowables (A/S-basis from MIL-HDBK-5J) and typical values are mixed in the pool by necessity; the
``source`` string says which. Read it before quoting a margin.
"""
from __future__ import annotations

import json
from collections.abc import Iterable
from functools import lru_cache
from typing import Any

from aerokit.data import DATA_DIR
from aerokit.materials.selection import Ranked, rank

__all__ = ["UNITS", "load", "names", "get", "value", "for_selection", "rank_pool"]

UNITS = {"rho": "kg/m3", "E": "GPa", "Fty": "MPa", "Ftu": "MPa", "fatigue": "MPa", "k": "W/mK", "cte": "1e-6/K",
         "Tmax": "C", "co2": "kg CO2e/kg", "co2_recycled": "kg CO2e/kg"}
"""Unit of each standard property key."""

_PATH = DATA_DIR / "materials" / "materials_pool.json"


@lru_cache(maxsize=1)
def load() -> dict[str, Any]:
    """The whole pool (``{"about", "materials": {name: record}}``)."""
    return json.loads(_PATH.read_text(encoding="utf-8"))


def names(family: str | None = None) -> list[str]:
    """Material names, optionally of one family (aluminium, titanium, steel, nickel, magnesium, composite, …)."""
    return [n for n, r in load()["materials"].items() if family is None or r.get("family") == family]


def get(name: str) -> dict[str, Any]:
    """One material record; raises KeyError with the close names when absent."""
    mats = load()["materials"]
    if name in mats:
        return mats[name]
    near = [n for n in mats if name.lower() in n.lower()]
    raise KeyError(f"{name!r} not in the pool" + (f"; did you mean {near}?" if near else ""))


def value(name: str, prop: str) -> float:
    """Numeric value of ``prop`` for ``name`` in the pool's unit (see :data:`UNITS`)."""
    p = get(name).get("properties", {})
    if prop not in p:
        raise KeyError(f"{name!r} has no {prop!r} in the pool")
    return float(p[prop]["value"])


def for_selection(name: str) -> dict[str, float]:
    """SI record for :func:`aerokit.materials.selection.rank`: ``E`` [Pa], ``Fty`` [Pa] when present, ``rho``."""
    p = get(name)["properties"]
    rec = {"rho": float(p["rho"]["value"])}
    if "E" in p:
        rec["E"] = float(p["E"]["value"]) * 1e9
    if "Fty" in p:
        rec["Fty"] = float(p["Fty"]["value"]) * 1e6
    return rec


def rank_pool(case: str, materials: Iterable[str] | None = None, co2: bool = False) -> list[Ranked]:
    """Ashby ranking over pool materials that have the property the case needs (and CO₂ when ``co2``)."""
    prop = {"tie_stiff": "E", "beam_stiff": "E", "panel_stiff": "E", "column_buckling": "E"}.get(case, "Fty")
    pool: dict[str, dict[str, float]] = {}
    co2_map: dict[str, float] = {}
    for n in (materials if materials is not None else names()):
        p = get(n)["properties"]
        if prop not in p or "rho" not in p or (co2 and "co2" not in p):
            continue
        pool[n] = for_selection(n)
        if co2:
            co2_map[n] = float(p["co2"]["value"])
    return rank(case, pool, co2_per_kg=co2_map if co2 else None)
