"""Ansys vs aerokit agreement table for a bracket run.

    python 01_Ansys/scripts/bracket_crosscheck.py <outputs/cases/case folder> [--csv crosscheck_template.csv] [--export sonuc.txt]

Reads the filled template (column 'ansys'); with --export also reads a Mechanical "Export Text File" of the
equivalent stress (or total deformation) and reports its peak outside the hole zones of the run's setup.json
(same rule as ours). Writes crosscheck_<template stem>.md next to the template and prints it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.bracket import crosscheck, matdata  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--csv", default="crosscheck_template.csv")
    ap.add_argument("--export", help="Mechanical text export (stress or deformation)")
    ap.add_argument("--margin-vox", type=float, default=3.0)
    a = ap.parse_args(argv)
    folder = Path(a.folder)
    ours, ansys = crosscheck.read_template(folder / a.csv)
    setup = json.loads((folder / "setup.json").read_text(encoding="utf-8"))
    extra = ""
    if a.export:
        ex = crosscheck.read_mechanical_export(a.export)
        zones = [h for h in setup["holes"] if h.get("role") in ("support", "load")]
        pk = crosscheck.peak_outside(ex["xyz"], ex["value"], zones, a.margin_vox * setup["voxel_mm"])
        key = "von_mises_outside_MPa" if ex["unit"] == "MPa" else "max_deformation_mm"
        if ansys.get(key) is None:
            ansys[key] = pk["max"]
        if ex["unit"] == "MPa" and ansys.get("max_von_mises_MPa") is None:
            ansys["max_von_mises_MPa"] = pk.get("max_all")
        extra = (f"\nExport `{a.export}`: {ex['quantity']}, {len(ex['value'])} points; peak outside zones "
                 f"{pk['max']:.4g} {ex['unit']} at {pk['at_mm']} mm; peak anywhere {pk.get('max_all', float('nan')):.4g} "
                 f"at {pk.get('at_all_mm')} mm.\n")
        res = folder / "result.json"
        if res.exists() and ex["unit"] == "MPa" and pk["at_mm"] is not None:
            import numpy as np
            det = json.loads(res.read_text(encoding="utf-8")).get("details", {})
            cases = det.get("baseline", {}).get("at_T", {}).get("cases", [])
            if cases:
                w = max(cases, key=lambda c: c["vm_outside_Pa"])
                ours_at = np.asarray(w["vm_outside_at_m"]) * 1e3
                dist = float(np.linalg.norm(ours_at - np.asarray(pk["at_mm"])))
                lim = 2 * setup.get("exclusion_mm", 3 * setup.get("voxel_mm", 1.0))
                extra += (f"\nPeak location: ours ({', '.join(f'{v:.1f}' for v in ours_at)}) mm in {w['name']} vs Ansys "
                          f"({', '.join(f'{v:.1f}' for v in pk['at_mm'])}) mm: distance {dist:.1f} mm "
                          f"({'same region' if dist <= lim else 'DIFFERENT region: check load case, BCs, sharp edges'}; "
                          f"limit {lim:.1f} mm).\n")
    base = matdata.get("structural_steel")
    ctx = {"kE": base.E_at(setup.get("temperature_C", 300.0)) / base.E.value,
           "density_ratio_candidates": {m.name: m.rho.value / base.rho.value for m in matdata.CANDIDATES.values()},
           "E_ratio_candidates": {m.name: base.E.value / m.E.value for m in matdata.CANDIDATES.values()}}
    res = folder / "result.json"
    if res.exists():
        th = json.loads(res.read_text(encoding="utf-8")).get("details", {}).get("baseline", {}).get("thermal")
        if th:
            ctx["thermal_vm_MPa"] = th["vm_outside_Pa"] / 1e6
    rows = crosscheck.compare(ours, ansys, ctx)
    v = crosscheck.verdict(rows)
    md = f"# Ansys cross-check — {folder.name} ({a.csv})\n\n**{v}**\n\n" + crosscheck.markdown(rows) + extra
    path = folder / f"crosscheck_{Path(a.csv).stem}.md"
    path.write_text(md, encoding="utf-8")
    sys.stdout.buffer.write(md.encode("utf-8"))
    print(f"\nwritten: {path}")
    print(f"RESULT: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
