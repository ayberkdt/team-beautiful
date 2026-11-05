"""Venus cloud-layer atmosphere from in-situ data, with uncertainty bands (40–64 km).

**Data** — ``data/pv_profiles.json``, extracted by ``scripts/venus_pds_extract.py`` from the raw Pioneer Venus PDS4
tables (Large/Sounder, Day, Night and North probes, 9 Dec 1978; 00–08 h local time): temperature,
pressure, density on a 1-km grid; zonal (westward) and meridional wind from the DLBI tracking (±0.5 km bin means);
Large-probe solar flux radiometer (LSFR); probe sites 31.3°S–59.3°N (Day 31.3°S, Night 28.7°S, Large 4.4°N,
North 59.3°N; research note A_pv_probes_seiff1980_pds). Seiff et al. (1985) VIRA tables could not be obtained (research note
``A_seiff1985_vira.md``); the Wikipedia/VIRA-like table in :mod:`aerokit.planetary` sits at the warm/dense edge of
the probe envelope (tested), so it remains the fallback outside 40–64 km.

**Cases** — ``mean`` (average of the probes present), ``min``/``max`` envelope per quantity (each quantity's own
extreme, i.e. not one physical profile), and the named design cases ``thin`` (min ρ) and ``dense`` (max ρ).

**Wind band** — the probe spread (4 sites) widened with the values the research agent read from VEGA (66–69 m/s at
53–54 km), Venus Express (±10 m/s), Akatsuki (equatorial jet ~85 m/s, 2016) and decadal changes up to ~30 m/s
(Peralta 2018): ``zonal_wind_band`` returns (low, mean, high) with high/low = probe max/min ± 10 m/s [Y].

**Vertical wind / turbulence** — VEGA balloons at 53–55 km (research note ``A_vega1985_balloons_lander.md``):
σ 0.65–0.75 m/s, range −3.5…+2.0 m/s; the largest downdraft (VEGA-2) −2…−3.3 m/s over ~2 h pushed the balloon
~2.9 km down, recovery ~4 h; horizontal fluctuations up to 1–2
m/s at 30–130 s periods (×1.5 for instrument response). Exposed as :data:`VERTICAL_WIND` for the control design.
"""
from __future__ import annotations

import json
import math
import warnings
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from aerokit import planetary as P
from aerokit.references import cite
from aerokit.venus import gas

__all__ = ["PROBES", "State", "state", "zonal_wind", "zonal_wind_band", "meridional_wind_max", "VERTICAL_WIND",
           "CLOUD_LAYERS", "solar_ratio_up_down", "solar_down_relative", "Z_MIN", "Z_MAX", "profile_table"]

_DATA = Path(__file__).with_name("data") / "pv_profiles.json"
PROBES = ("large", "day", "night", "north")
Z_MIN, Z_MAX = 40e3, 64e3

# research note A_vega1985_balloons_lander.md (agent statistics on the PDS level-3 files and NASA TM-88516)
VERTICAL_WIND = {"altitude_km": (53.0, 55.0), "sigma_m_s": (0.65, 0.75), "min_m_s": -3.5, "max_m_s": 2.0,
                 "downdraft_episode_m_s": (2.0, 3.3), "downdraft_duration_h": (2.0, 2.0),
                 "horizontal_gust_m_s": 2.0 * 1.5, "gust_period_s": (30.0, 130.0), "tag": "D-ag"}
# Titov et al. 2018 (research note A_titov2018_clouds.md): layer boundaries and H2SO4 concentration
# H2SO4: observations 75-90 wt% (Titov p. 37); a model gives 98 % at the cloud bottom (~48 km), hence the lower-cloud
# upper bound
CLOUD_LAYERS = ({"name": "lower cloud", "base_km": 47.5, "top_km": 50.5, "h2so4_wt_pct": (75, 98)},
                {"name": "middle cloud", "base_km": 50.5, "top_km": 56.5, "h2so4_wt_pct": (75, 90)},
                {"name": "upper cloud", "base_km": 56.5, "top_km": 70.0, "h2so4_wt_pct": (75, 90)})


@lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def _column(kind: str, key: str) -> np.ndarray:
    d = _load()
    src = d["probes"] if kind == "probes" else d["wind"]
    arr = np.array([[np.nan if v is None else v for v in src[p][key]] for p in PROBES], dtype=float)
    return arr


def _grid() -> np.ndarray:
    return np.array(_load()["grid_km"], dtype=float) * 1e3


def _reduce(arr: np.ndarray, case: str) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        if case == "mean":
            return np.nanmean(arr, axis=0)
        if case == "min":
            return np.nanmin(arr, axis=0)
        if case == "max":
            return np.nanmax(arr, axis=0)
    raise ValueError(f"unknown case {case!r}")


@dataclass(frozen=True)
class State:
    h: float
    T: float
    p: float
    rho: float
    g: float
    a: float
    mu: float
    source: str


def _check(h: float) -> None:
    if not (math.isfinite(h) and Z_MIN <= h <= Z_MAX):
        raise ValueError(f"altitude {h / 1e3:.1f} km outside the probe range 40-64 km")


@cite("seiff_1980_pv_structure", "nist_webbook_co2_2026",
      note="PV probes T, p, rho (PDS); mean or envelope; a and mu from aerokit.venus.gas")
def state(h: float, case: str = "mean") -> State:
    """Atmospheric state at ``h`` [m] for ``case`` in mean/min/max/thin/dense (40–64 km)."""
    _check(h)
    z = _grid()
    if case in ("thin", "dense"):
        rho_case = "min" if case == "thin" else "max"
        rho = float(np.interp(h, z, _reduce(_column("probes", "rho"), rho_case)))
        T = float(np.interp(h, z, _reduce(_column("probes", "T_K"), "mean")))
        p = rho * gas.R_SPECIFIC * T
        src = f"PV probes, {case} (rho {rho_case}, T mean)"
    else:
        T = float(np.interp(h, z, _reduce(_column("probes", "T_K"), case)))
        p = float(np.interp(h, z, _reduce(_column("probes", "p_bar"), case))) * 1e5
        rho = float(np.interp(h, z, _reduce(_column("probes", "rho"), case)))
        src = f"PV probes, {case}"
    return State(h, T, p, rho, P.venus_gravity(h), gas.speed_of_sound(T), gas.viscosity(T), src)


@cite("counselman_1980_pv_winds", note="DLBI zonal wind, 4 probe sites, ±0.5 km bins")
def zonal_wind(h: float, case: str = "mean") -> float:
    """Westward zonal wind [m/s] at ``h`` (positive = super-rotation direction)."""
    _check(h)
    arr = _column("wind", "west_m_s")
    col = _reduce(arr, case)
    z = _grid()
    ok = np.isfinite(col)
    return float(np.interp(h, z[ok], col[ok]))


def zonal_wind_band(h: float, widen: float = 10.0) -> tuple[float, float, float]:
    """(low, mean, high) zonal wind [m/s]: probe min/max widened by ``widen`` (VEX ±10 m/s, decadal changes) [Y]."""
    return zonal_wind(h, "min") - widen, zonal_wind(h, "mean"), zonal_wind(h, "max") + widen


def meridional_wind_max(h: float) -> float:
    """Largest |meridional wind| [m/s] among the probes within ±1 km of ``h``."""
    _check(h)
    arr = np.abs(_column("wind", "north_m_s"))
    z = _grid()
    sel = np.abs(z - h) <= 1e3
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.nanmax(arr[:, sel]))


def _lsfr(key: str) -> np.ndarray:
    return np.array([np.nan if v is None else v for v in _load()["lsfr"][key]], dtype=float)


@cite("tomasko_1980_solar_flux", note="PV LSFR up/down flux, VIS and COMBINED channels, SZA 65.7 deg")
def solar_ratio_up_down(h: float, channel: str = "comb") -> float:
    """Upward / downward solar flux at ``h`` (Large-probe radiometer)."""
    _check(h)
    up, down = _lsfr(f"{channel}_up"), _lsfr(f"{channel}_down")
    z = _grid()
    ok = np.isfinite(up) & np.isfinite(down)
    return float(np.interp(h, z[ok], (up / down)[ok]))


@cite("tomasko_1980_solar_flux", note="downward flux normalised to the 64 km value")
def solar_down_relative(h: float, channel: str = "comb") -> float:
    """Downward flux at ``h`` relative to its value at 64 km (shape of the in-cloud attenuation)."""
    _check(h)
    down = _lsfr(f"{channel}_down")
    z = _grid()
    ok = np.isfinite(down)
    ref = float(np.interp(64e3, z[ok], down[ok]))
    return float(np.interp(h, z[ok], down[ok])) / ref


def profile_table(lo_km: int = 30, hi_km: int = 80) -> list[dict]:
    """1-km table for hand-off: PV mean (with band) inside 40–64 km, :mod:`aerokit.planetary` outside."""
    rows = []
    for km in range(lo_km, hi_km + 1):
        h = km * 1e3
        if Z_MIN <= h <= Z_MAX:
            s, lo, hi = state(h), state(h, "min"), state(h, "max")
            wl, wm, wh = zonal_wind_band(h)
            rows.append({"altitude_km": km, "temperature_K": round(s.T, 2), "pressure_Pa": round(s.p, 1),
                         "density_kg_m3": round(s.rho, 4), "zonal_wind_m_s": round(wm, 1),
                         "speed_of_sound_m_s": round(s.a, 1), "gravity_m_s2": round(s.g, 3),
                         "temperature_band_K": [round(lo.T, 1), round(hi.T, 1)],
                         "density_band_kg_m3": [round(lo.rho, 4), round(hi.rho, 4)],
                         "zonal_wind_band_m_s": [round(wl, 1), round(wh, 1)],
                         "source": "Pioneer Venus probes (PDS), mean of 4 sites; band = site envelope", "tag": "D/K"})
        else:
            t = P.venus_atmosphere(h)
            rows.append({"altitude_km": km, "temperature_K": round(t.T, 2), "pressure_Pa": round(t.p, 1),
                         "density_kg_m3": round(t.rho, 4), "zonal_wind_m_s": round(P.venus_zonal_wind(h), 1),
                         "speed_of_sound_m_s": round(gas.speed_of_sound(t.T), 1), "gravity_m_s2": round(t.g, 3),
                         "source": "aerokit.planetary (VIRA-like table via Wikipedia; Landis wind anchors)",
                         "tag": "D(secondary)/Y"})
    return rows
