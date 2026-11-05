"""Extract Pioneer Venus probe profiles from the raw PDS4 files into ``src/aerokit/venus/data/pv_profiles.json``.

    python -I scripts/venus_pds_extract.py D:/tmp_ideathon/venus/downloads/atmo

Inputs (downloaded by the atmosphere research agent from the PDS Atmospheres Node, pv_sed_bundle and the DLBI
bundle; data only, read as text):

* ``pvsed/{las,sas_day,sas_night,sas_north}_low_atm_state.csv`` — columns grt_hr_min, grt_sec, altitude [km],
  pressure [bar], temperature [K], density [kg/m³], zeta (labels in the matching .xml).
* ``dlbi/dlbi_{large,day,night,north}_atm_vel.tab`` — grt [s], probe velocity down / west / north relative to the
  crust and west / north relative to the atmosphere [m/s]. Wind = crust-relative − atmosphere-relative velocity.
  Altitude is assigned through grt → altitude of the same probe's state table (linear in time).
* ``pvsed/lsfr_solar_flux.csv`` — Large-probe solar flux radiometer: grt, pressure [atm], altitude [km], VIS
  (0.40–0.96 µm) down/up/net, COMBINED (0.41–1.78 µm) down/up/net, NB down/up/net [W/m², passband only];
  solar zenith angle 65.7° (agent note A_tomasko1980).

Output: 1-km grids (40–66 km) per probe plus mean/min/max, written deterministically. Every value is a linear
interpolation in the raw tables (our processing [K] of data read [D]).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROBES = {"large": "las_low_atm_state.csv", "day": "sas_day_low_atm_state.csv",
          "night": "sas_night_low_atm_state.csv", "north": "sas_north_low_atm_state.csv"}
DLBI = {"large": "dlbi_large_atm_vel.tab", "day": "dlbi_day_atm_vel.tab", "night": "dlbi_night_atm_vel.tab",
        "north": "dlbi_north_atm_vel.tab"}
GRID = list(range(40, 67))
OUT = Path(__file__).resolve().parents[1] / "src" / "aerokit" / "venus" / "data" / "pv_profiles.json"


def _state(path: Path) -> list[tuple[float, float, float, float, float]]:
    rows = []
    for line in path.read_text(encoding="latin-1").splitlines():
        parts = line.strip().split(",")
        if len(parts) < 7:
            continue
        try:
            t, z, p, T, rho = (float(parts[i]) for i in (1, 2, 3, 4, 5))
        except ValueError:
            continue
        rows.append((t, z, p, T, rho))
    return rows


def _interp(xs: list[float], ys: list[float], x: float) -> float | None:
    pts = sorted(zip(xs, ys))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (x - x0) / (x1 - x0) * (y1 - y0)
    return None


def _bin_mean(zs: list[float], vs: list[float], z: float, half: float = 0.5) -> float | None:
    sel = [v for zz, v in zip(zs, vs) if abs(zz - z) <= half]
    return sum(sel) / len(sel) if sel else None


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else Path("D:/tmp_ideathon/venus/downloads/atmo")
    out: dict = {"source": "PDS4 pv_sed_bundle (LAS/SAS state, LSFR) and DLBI bundle; extracted by "
                           "scripts/venus_pds_extract.py; 1-km linear interpolation (state, flux) and ±0.5 km bin "
                           "means (wind)", "grid_km": GRID, "probes": {}, "wind": {}, "lsfr": {}}
    time_alt = {}
    for name, fn in PROBES.items():
        rows = _state(root / "pvsed" / fn)
        z = [r[1] for r in rows]
        time_alt[name] = ([r[0] for r in rows], z)
        prof = {}
        for key, k in (("T_K", 3), ("p_bar", 2), ("rho", 4)):
            prof[key] = [None if (v := _interp(z, [r[k] for r in rows], g)) is None else round(v, 5) for g in GRID]
        prof["z_range_km"] = [round(min(z), 3), round(max(z), 3)]
        out["probes"][name] = prof
    for name, fn in DLBI.items():
        tz, zz = time_alt[name]
        zs, west, north = [], [], []
        for line in (root / "dlbi" / fn).read_text(encoding="latin-1").splitlines():
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                t, _down, w_c, n_c, w_a, n_a = (float(x) for x in parts[:6])
            except ValueError:
                continue
            z = _interp(tz, zz, t)
            if z is None:
                continue
            zs.append(z)
            west.append(w_c - w_a)
            north.append(n_c - n_a)
        out["wind"][name] = {"west_m_s": [None if (v := _bin_mean(zs, west, g)) is None else round(v, 2) for g in GRID],
                             "north_m_s": [None if (v := _bin_mean(zs, north, g)) is None else round(v, 2)
                                           for g in GRID]}
    zs, cols = [], {k: [] for k in ("vis_down", "vis_up", "comb_down", "comb_up")}
    for line in (root / "pvsed" / "lsfr_solar_flux.csv").read_text(encoding="latin-1").splitlines():
        parts = line.strip().split(",")
        if len(parts) < 9:
            continue
        try:
            z = float(parts[2])
            vals = [float(parts[i]) for i in (3, 4, 6, 7)]
        except ValueError:
            continue
        zs.append(z)
        for k, v in zip(cols, vals):
            cols[k].append(v)
    for k, vs in cols.items():
        out["lsfr"][k] = [None if (v := _interp(zs, vs, g)) is None else round(v, 2) for g in GRID]
    out["lsfr"]["solar_zenith_deg"] = 65.7
    out["lsfr"]["note"] = "passband fluxes W/m2 (VIS 0.40-0.96 um, COMBINED 0.41-1.78 um), Large probe, 4.4 N, 07:38 LT"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    for g in (50, 55, 60):
        i = GRID.index(g)
        print(g, {n: (p["T_K"][i], p["p_bar"][i], p["rho"][i]) for n, p in out["probes"].items()},
              {n: w["west_m_s"][i] for n, w in out["wind"].items()},
              {k: v[i] for k, v in out["lsfr"].items() if isinstance(v, list)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
