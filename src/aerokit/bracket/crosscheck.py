"""Compare an Ansys Mechanical/Discovery result with ours and explain the differences.

Inputs: our ``result.json`` metrics and Ansys numbers, either typed into the template CSV written by
:func:`write_template` (one row per metric) or read from a Mechanical "Export Text File" of a result object
(:func:`read_mechanical_export`: columns such as ``X Location (mm)`` … ``Equivalent (von-Mises) Stress (MPa)`` or
``Total Deformation (mm)``; Pa/m columns are converted).

Each metric has a tolerance [Y, team judgement, see docs/22]; outside it, the ratio Ansys/ours is matched against
the signatures of common set-up errors (units, density, temperature-dependent modulus, limit vs ultimate load,
supports, singular peaks, mesh) and the likely causes are listed.
"""
from __future__ import annotations

import csv
import io
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

__all__ = ["METRICS", "Row", "compare", "verdict", "write_template", "read_template", "read_mechanical_export",
           "peak_outside", "markdown"]

# metric → (unit, tolerance (relative), description)
METRICS: dict[str, tuple[str, float, str]] = {
    "mass_kg": ("kg", 0.02, "part mass (geometry × density)"),
    "volume_mm3": ("mm3", 0.02, "part volume"),
    "max_deformation_mm": ("mm", 0.10, "maximum total deformation (worst load case)"),
    "load_point_deformation_mm": ("mm", 0.10, "mean deformation of the loaded bore (probe: average over the bore face)"),
    "strain_energy_J": ("J", 0.10, "strain energy = compliance / 2 (worst load case)"),
    "compliance_J": ("J", 0.10, "compliance F·u (worst load case)"),
    "max_von_mises_MPa": ("MPa", 0.25, "maximum equivalent stress anywhere (singular at supports: loose)"),
    "von_mises_outside_MPa": ("MPa", 0.15, "maximum equivalent stress outside the support/load zones"),
    "min_safety_factor": ("-", 0.15, "minimum safety factor (yield at temperature / von Mises)"),
    "retained_volume_fraction": ("-", 0.05, "topology: retained volume / design-space volume"),
    "reaction_force_N": ("N", 0.01, "sum of support reactions (equals the applied load)"),
}


@dataclass
class Row:
    metric: str
    ours: float | None
    ansys: float | None
    ratio: float | None
    tolerance: float
    status: str
    causes: list[str]


def _causes(metric: str, r: float, ctx: dict[str, Any]) -> list[str]:
    """Likely causes for an Ansys/ours ratio ``r`` outside tolerance."""
    out: list[str] = []
    near = lambda a, b, tol=0.03: abs(a / b - 1) <= tol  # noqa: E731
    for f, why in ((1e3, "units: mm vs m (factor 1000)"), (1e-3, "units: mm vs m (factor 1/1000)"),
                   (1e6, "units: Pa vs MPa or mm² vs m²"), (1e-6, "units: MPa vs Pa"),
                   (1e9, "units: mm³ vs m³ or Pa vs GPa"), (1e-9, "units: m³ vs mm³"),
                   (25.4, "units: inch vs mm"), (1 / 25.4, "units: mm vs inch"),
                   (4.448, "units: lbf vs N"), (1 / 4.448, "units: N vs lbf")):
        if near(r, f, 0.02):
            out.append(why)
    rho = ctx.get("density_ratio_candidates", {})
    if metric in ("mass_kg",):
        for name, k in rho.items():
            if abs(k - 1) > 0.02 and near(r, k, 0.01):       # a genuinely different material, matched closely
                out.append(f"density: Ansys material looks like {name} (density ratio {k:.3f})")
    if metric in ("max_deformation_mm", "load_point_deformation_mm", "strain_energy_J", "compliance_J"):
        kE = ctx.get("kE")                     # E(T)/E(20 °C) of our material
        # deformation ∝ 1/E: Ansys/ours = E_ours/E_ansys
        if kE and near(r, kE, 0.02):
            out.append(f"temperature: Ansys used E at 20-22 °C (stiffer), ours E at the working temperature "
                       f"(ratio E(T)/E(20) = {kE:.3f}): set the temperature in Mechanical")
        if kE and near(r, 1 / kE, 0.02):
            out.append(f"temperature: Ansys used E at the working temperature, ours at 20 °C (ratio {1 / kE:.3f})")
        for name, k in ctx.get("E_ratio_candidates", {}).items():
            if abs(k - 1) > 0.03 and near(r, k, 0.03):      # a genuinely different modulus (not our own material)
                out.append(f"material: Ansys modulus looks like {name} (E ratio {1 / k:.3f})")
    if metric in ("max_deformation_mm", "max_von_mises_MPa", "von_mises_outside_MPa", "reaction_force_N"):
        for f in (1.5, 1 / 1.5):
            if near(r, f, 0.02):
                out.append("load level: limit vs ultimate (factor 1.5)")
    if metric in ("strain_energy_J",) and near(r, 0.5, 0.03):
        out.append("definition: strain energy = compliance / 2 — compare like with like")
    if metric in ("compliance_J",) and near(r, 2.0, 0.03):
        out.append("definition: Ansys strain energy × 2 = compliance")
    th = ctx.get("thermal_vm_MPa")
    if th and metric in ("max_von_mises_MPa", "von_mises_outside_MPa") and r > 1.15:
        o = ctx.get("ours", {}).get(metric)
        if o and (near(r * o, o + th, 0.25) or near(r * o, th, 0.25)):
            out.append(f"thermal: Ansys stress ≈ ours + constrained expansion ({th:.0f} MPa): a Thermal Condition "
                       "with fixed supports? Ask whether the mounts expand with the bracket")
    if metric == "max_von_mises_MPa" and r > 1.25:
        out.append("singular peak at a fixed support or point/edge load: Ansys conforming tets resolve the "
                   "re-entrant corner and the peak grows with refinement; compare 'von_mises_outside_MPa'")
    if metric in ("max_deformation_mm", "compliance_J", "strain_energy_J"):
        if 0.85 <= r < 0.97:
            out.append("discretisation: Ansys (SOLID187 tets, smooth holes) is slightly stiffer/softer than the voxel "
                       "model; check our 3-level mesh convergence and Ansys mesh convergence")
        if r < 0.7 or r > 1.4:
            out.append("boundary conditions: fixed bore vs bolt seat / remote-point (rigid vs deformable) differs; "
                       "or a load applied on a different face or direction")
    if metric == "retained_volume_fraction":
        out.append("topology: Ansys response constraint is % of the design region (exclusion regions not counted) "
                   "vs ours % of all solid voxels; or a different minimum member size / filter radius")
    if metric == "min_safety_factor":
        out.append("safety factor: check which strength Ansys used (Tensile Yield at 22 °C vs at the working "
                   "temperature) and whether the factor includes the 1.5 ultimate factor")
    if metric == "von_mises_outside_MPa" and (r > 1.15 or r < 0.87):
        out.append("stress: voxel staircase lowers/raises local peaks at curved edges; compare at the same point "
                   "(probe) and with nodal averaging on")
    if not out:
        out.append("no signature matched: compare loads, supports and material assignment step by step")
    return out


def compare(ours: dict[str, float | None], ansys: dict[str, float | None],
            context: dict[str, Any] | None = None, tolerances: dict[str, float] | None = None) -> list[Row]:
    """Agreement table: ratio Ansys/ours per metric with status OK / CHECK / missing."""
    ctx = dict(context or {})
    ctx.setdefault("ours", ours)
    rows: list[Row] = []
    for metric, (_unit, tol, _d) in METRICS.items():
        tol = (tolerances or {}).get(metric, tol)
        a, o = ansys.get(metric), ours.get(metric)
        if a is None or o is None or math.isnan(float(a)) or math.isnan(float(o)):
            rows.append(Row(metric, o, a, None, tol, "missing", []))
            continue
        if o == 0:
            rows.append(Row(metric, o, a, None, tol, "CHECK", ["ours is zero"]))
            continue
        r = float(a) / float(o)
        ok = abs(r - 1) <= tol
        causes = _causes(metric, r, ctx)
        if ok:     # inside tolerance: keep only exact signatures (a 9 % E(T) effect can hide inside ±10 %)
            causes = [c for c in causes if c.split(":")[0] in ("temperature", "units", "density", "material",
                                                                "load level", "definition")]
        rows.append(Row(metric, float(o), float(a), r, tol, "OK" if ok else "CHECK", causes))
    return rows


def write_template(path: str | Path, ours: dict[str, float | None], case: str = "") -> Path:
    """CSV for the team to fill during the Ansys run: metric, unit, ours, ansys (empty), description."""
    p = Path(path)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "unit", "ours", "ansys", "description"])
        for k, (u, tol, d) in METRICS.items():
            v = ours.get(k)
            w.writerow([k, u, "" if v is None else f"{v:.6g}", "", f"{d} (tolerance ±{100 * tol:.0f} %) {case}"])
    return p


def read_template(path: str | Path) -> tuple[dict[str, float | None], dict[str, float | None]]:
    """(ours, ansys) from a filled template."""
    ours: dict[str, float | None] = {}
    ansys: dict[str, float | None] = {}
    with Path(path).open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            k = row["metric"].strip()
            ours[k] = float(row["ours"]) if row.get("ours", "").strip() else None
            ansys[k] = float(row["ansys"]) if row.get("ansys", "").strip() else None
    return ours, ansys


_UNIT = {"mm": 1.0, "m": 1000.0, "MPa": 1.0, "Pa": 1e-6, "GPa": 1e3, "kPa": 1e-3, "in": 25.4, "psi": 6.894757e-3}


def read_mechanical_export(path: str | Path) -> dict[str, Any]:
    """Columns of a Mechanical "Export Text File" (tab, comma or semicolon separated) in mm and MPa.

    Returns ``{"xyz": (n, 3) mm, "value": (n,), "quantity": name, "unit": "MPa"|"mm"}`` for the last numeric column
    (the result) and the X/Y/Z location columns.
    """
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    sep = "\t" if "\t" in lines[0] else (";" if ";" in lines[0] else ",")
    header = [h.strip() for h in lines[0].split(sep)]
    rows = list(csv.reader(io.StringIO("\n".join(lines[1:])), delimiter=sep))

    def unit_of(h: str) -> str:
        m = re.search(r"\(([^)]+)\)\s*$", h)
        return m.group(1).strip() if m else ""

    loc = []
    for axis in ("X", "Y", "Z"):
        j = next((i for i, h in enumerate(header) if h.upper().startswith(f"{axis} LOCATION")), None)
        if j is None:
            raise ValueError(f"no '{axis} Location' column in {path}")
        loc.append(j)
    jv = len(header) - 1
    data = np.array([[float(r[i].replace(",", ".")) if sep != "," else float(r[i]) for i in loc + [jv]]
                     for r in rows if len(r) > jv and r[jv].strip()])
    xyz = data[:, :3] * _UNIT.get(unit_of(header[loc[0]]), 1.0)
    vu = unit_of(header[jv])
    val = data[:, 3] * _UNIT.get(vu, 1.0)
    unit = "MPa" if vu in ("MPa", "Pa", "GPa", "kPa", "psi") else "mm"
    return {"xyz": xyz, "value": val, "quantity": header[jv], "unit": unit}


def peak_outside(xyz_mm: np.ndarray, value: np.ndarray, zones: list[dict[str, Any]], margin_mm: float) -> dict[str, Any]:
    """Maximum of ``value`` outside cylindrical zones (hole axis, centre, radius) grown by ``margin_mm``."""
    keep = np.ones(len(value), bool)
    for z in zones:
        ax = "xyz".index(z["axis"])
        d = xyz_mm - np.asarray(z["center_mm"])
        rad = np.linalg.norm(np.delete(d, ax, axis=1), axis=1)
        keep &= rad > 0.5 * z["diameter_mm"] + margin_mm
    if not keep.any():
        return {"max": float("nan"), "at_mm": None, "points": 0}
    i = int(np.argmax(np.where(keep, value, -np.inf)))
    return {"max": float(value[i]), "at_mm": [float(v) for v in xyz_mm[i]], "points": int(keep.sum()),
            "max_all": float(value.max()), "at_all_mm": [float(v) for v in xyz_mm[int(np.argmax(value))]]}


_EXACT = ("units", "temperature", "load level", "density", "material", "definition")
"""Cause categories that are numerical signatures (a ratio matched a known factor) — ranked before the vague ones."""


def verdict(rows: list[Row]) -> str:
    """One line: AGREES (every compared metric inside tolerance) or DISCREPANCY with the most likely cause (the
    cause category named by most out-of-tolerance metrics, exact signatures first)."""
    checked = [r for r in rows if r.status != "missing"]
    bad = [r for r in checked if r.status == "CHECK"]
    if not checked:
        return "NO DATA: fill the ansys column first"
    if not bad:
        hidden: dict[str, list[str]] = {}            # exact signatures inside tolerance (e.g. E(T)/E(22 °C) = 0.93)
        for r in checked:
            for c in r.causes:
                if c.split(":")[0] in _EXACT:
                    hidden.setdefault(c, []).append(r.metric)
        if hidden:
            c, ms = max(hidden.items(), key=lambda kv: len(kv[1]))
            if len(ms) >= 2:
                return (f"AGREES within tolerance, BUT a signature is hidden inside it — {c} "
                        f"(named by {len(ms)}: {', '.join(ms)})")
        return f"AGREES: {len(checked)} of {len(checked)} compared metrics inside tolerance"
    votes: dict[str, list[str]] = {}
    for r in bad:
        for c in r.causes:
            votes.setdefault(c.split(":")[0], []).append(r.metric)
    if not votes:
        return f"DISCREPANCY: {len(bad)} of {len(checked)} metrics outside tolerance, no signature matched"
    best = max(votes, key=lambda k: (k in _EXACT, len(votes[k])))
    cause = next(c for r in bad for c in r.causes if c.split(":")[0] == best)
    return (f"DISCREPANCY: {len(bad)} of {len(checked)} metrics outside tolerance "
            f"({', '.join(r.metric for r in bad)}); most likely cause — {cause} "
            f"(named by {len(votes[best])}: {', '.join(votes[best])})")


def markdown(rows: list[Row]) -> str:
    s = "| Metric | Ours | Ansys | Ansys/ours | Tolerance | Status | Likely causes |\n|---|---|---|---|---|---|---|\n"
    for r in rows:
        f = lambda v: "—" if v is None else f"{v:.4g}"  # noqa: E731
        s += (f"| {r.metric} | {f(r.ours)} | {f(r.ansys)} | {f(r.ratio)} | ±{100 * r.tolerance:.0f} % | {r.status} | "
              f"{'; '.join(r.causes)} |\n")
    return s
