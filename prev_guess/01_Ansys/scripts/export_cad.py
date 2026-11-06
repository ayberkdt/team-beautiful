"""Export topology previews for Discovery/SpaceClaim: 3-D voxel result -> STL, 2-D design -> DXF (mm).

    python prev_guess/01_Ansys/scripts/export_cad.py      # writes prev_guess/01_Ansys/scenarios/exports/*.stl, *.dxf and a summary JSON

Checks printed for each file: the mass enclosed by the exported geometry against the mass of the thresholded
topology result (they differ by the smoothing of the 0.5 iso-surface, a few per cent on coarse grids).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.optimization import extract as ex  # noqa: E402

OUT = ROOT / "prev_guess" / "01_Ansys" / "scenarios" / "exports"


def ge() -> list[dict]:
    d = json.loads((ROOT / "prev_guess" / "01_Ansys" / "scenarios" / "ge_bracket_preview.json").read_text(encoding="utf-8"))
    h = d["meta"]["voxel_mm"]
    rows = []
    for r in d["runs"]:
        rho = np.asarray(r["density"], float)
        level = ex.mass_preserving_level(rho, r["mass_kg"] / 4430.0 * 1e9, h)   # keep the thresholded mass
        V, F = ex.surface_nets(rho, level, h)
        V = ex.laplacian_smooth(V, F, 5)
        V = V + np.array([-163.3, -74.6, 0.0])               # back to the dolfiny frame used for the loads
        name = f"ge_bracket_{r['mass_kg']:.2f}kg".replace(".", "p") + ".stl"
        ex.write_stl(OUT / name, V, F, name="GE-type bracket preview, mm")
        vol_mm3 = ex.mesh_volume(V, F)
        rows.append({"file": name, "iso_level": round(level, 3), "triangles": int(len(F)), **ex.edge_report(F),
                     "mass_from_stl_kg": vol_mm3 * 1e-9 * 4430.0, "mass_topology_kg": r["mass_kg"]})
    return rows


def l_bracket() -> dict:
    d = json.loads((ROOT / "prev_guess" / "01_Ansys" / "retain_sweep" / "retain_sweep.json").read_text(encoding="utf-8"))
    run = next(r for r in d["runs"] if abs(r["volume"] - 0.35) < 1e-9)
    rho = np.asarray(run["density"], float)
    h = 120.0 / rho.shape[1]                                  # rehearsal card: 120 mm design space, 60 elements
    info = ex.to_dxf(OUT / "l_bracket_35pct.dxf", rho, h_mm=h, smooth=10)
    t_mm, rho_al = 10.0, 2670.0                              # card thickness, AlSi10Mg
    info.update(mass_from_dxf_g=info["area_mm2"] * t_mm * 1e-9 * rho_al * 1000,
                mass_thresholded_g=float((rho > 0.5).sum()) * h * h * t_mm * 1e-9 * rho_al * 1000,
                note="extrude 10 mm in Discovery; the bolted top edge and the load point are at the design-space "
                     "edges as in prev_guess/01_Ansys/cards/rehearsal_l_bracket.json")
    return info


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    out = {"ge": ge(), "l_bracket": l_bracket()}
    (OUT / "exports.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
