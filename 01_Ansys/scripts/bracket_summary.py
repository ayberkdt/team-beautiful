"""Markdown summary of the bracket runs in 01_Ansys/outputs/cases/*/result.json (for docs/22 §8).

    python 01_Ansys/scripts/bracket_summary.py [case ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
OUT = ROOT / "01_Ansys" / "outputs" / "cases"


def _prod(a: dict) -> float:
    """Cradle-to-gate CO2e as in eco_audit.md "Production total": material + manufacture + transport."""
    return sum(a["phases"][k]["co2_kg"] for k in ("material", "manufacture", "transport"))


def one(case: Path) -> str:
    r = json.loads((case / "result.json").read_text(encoding="utf-8"))
    d = r["details"]
    b = d["baseline"]
    ch = d.get("choice") or {}
    s = f"### `{case.name}` — {r['case']}\n\n"
    s += (f"Voxel {d['voxel']['h_m'] * 1e3:.2f} mm, {d['voxel']['elements']} elements, T = {r['temperature_C']:g} °C, "
          f"total {d['timings'].get('total_s', 0):.0f} s. Baseline {b['material']} on the initial design: "
          f"**{b['mass_kg']:.4f} kg**, worst deformation {b['worst_T']['max_disp_m'] * 1e3:.4g} mm, worst von Mises "
          f"outside the hole zones {b['worst_T']['vm_outside_Pa'] / 1e6:.4g} MPa (voxel H8IM).\n\n")
    tet = d.get("tet") or {}
    if tet.get("initial"):
        t = tet["initial"][-1]
        s += (f"T10 conforming check of the initial design ({t['size_mm']:.2f} mm, {t['elements']} elements): "
              f"deformation {t['worst']['max_disp_m'] * 1e3:.4g} mm (voxel/T10 "
              f"{b['worst_T']['max_disp_m'] / t['worst']['max_disp_m']:.3f}), vM outside "
              f"{t['worst']['vm_outside_Pa'] / 1e6:.4g} MPa.\n\n")
    s += "| Layout | Kept | vM outside the hole zones at limit load, voxel (MPa) | Status |\n|---|---|---|---|\n"
    for x in d["designs"][1:]:
        vm = max(x["stress_unitE"].values())
        s += (f"| {x['label']} | {x['volume_fraction_kept']:.3f} | {vm / 1e6:.4g} | "
              f"{'FAILED: ' + x['failed'] if x.get('failed') else 'ok'} |\n")
    for v in d.get("verification") or []:
        s += (f"\nVerification: {v['material']} / {v['design']}: voxel {v['voxel_stress_Pa'] / 1e6:.4g} MPa, T10 "
              f"{v['t10_stress_Pa'] / 1e6:.4g} MPa (factor {v['factor']:.3f}), T10 utilisation {v['t10_utilisation']:.3f}"
              f" → {'passes' if v['passes'] else 'fails, re-ranked'}.")
    if ch:
        s += (f"\n\n**Choice:** {ch['material']} · {ch['design']} · {ch['mass_kg']:.4f} kg "
              f"({abs(100 * (1 - ch['mass_kg'] / b['mass_kg'])):.1f} % "
              f"{'lighter' if ch['mass_kg'] <= b['mass_kg'] else 'heavier'} than the baseline, ranking utilisation {ch['utilisation']:.3f} (voxel stress × the layout's T10 factor where measured)"
              f"{'' if ch.get('passes', True) else ', FAILS — no candidate passes'}).\n")
    eco = d.get("eco") or {}
    if ch and ch.get("material") in (eco.get("candidates") or {}):
        a = eco["candidates"][ch["material"]]["audit"]
        bb = eco["baseline"]
        s += (f"\nEco audit (kg CO₂e): baseline production (material + manufacture + transport) {_prod(bb):.4g}"
              f", life {bb['total']['co2_kg']:.4g}; chosen production "
              f"{_prod(a):.4g}, life {a['total']['co2_kg']:.4g}.\n")
    return s + "\n"


def main(argv: list[str]) -> int:
    cases = [OUT / c for c in argv] if argv else sorted(p for p in OUT.iterdir() if (p / "result.json").exists())
    md = "".join(one(c) for c in cases)
    sys.stdout.buffer.write(md.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
