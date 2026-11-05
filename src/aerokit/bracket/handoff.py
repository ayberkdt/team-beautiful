"""Hand-off of a bracket run to the film session (``D:\\Video Simulations\\Ideathon-2026-Ansys``, read-only for us).

Writes ``studies/final_2026/ansys/handoff/<case>/`` in the input format the film already reads (its README,
"Girdi dosyası" table, read on 2026-11-04):

``girdi.json``     film input: ``parca_adi``, ``sonuc``, ``yukler``, ``geometri`` {dosya, birim, hizala, yukari},
                   ``yogunluk`` {dosya, anahtar "runs", kok_mm, yukari}, ``gerilme_csv``
``result.json``    ``ranking[]`` (material, route, mass_kg, co2_production_kg, co2_use_kg, volume, sigma_ult_Pa,
                   utilisation, ultimate_N); ``ranking[0]`` is the chosen option
``yukler.json``    supports (cylinders) and forces in mm / N, same frame as the STL and the density grid
``yogunluk.json``  ``runs[i].density`` as [x][y][z] (z up), ``runs[i].volume``, ``meta.voxel_mm``
``parca.stl``      smooth surface of the chosen layout (mm)
``baslangic.stl``  initial design (exact CAD surface for drawings, else the voxel surface)
``gerilme.txt``    nodal von Mises of the chosen layout at ULTIMATE load on its surface, Mechanical
                   "Export Text File" layout (X/Y/Z Location (mm), Equivalent (von-Mises) Stress (MPa))
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


from aerokit.bracket.pipeline import Options, Study, film_result, save_json

__all__ = ["write"]

README = """# Bracket hand-off for the film — {case}

Written by `aerokit.bracket.handoff` ({stamp}) from `{src}`. Same coordinate frame (mm, z up) in every file.

| File | What | Film key |
|---|---|---|
| `girdi.json` | film input (paths relative to this folder) | `node film.mjs <this>/girdi.json` |
| `result.json` | `ranking[]`: chosen material first; mass, CO₂e production/use, retained volume, σ at ultimate, utilisation | `sonuc` |
| `yukler.json` | supports (fixed hole bores as cylinders) and forces/moments, mm and N | `yukler` |
| `yogunluk.json` | density fields `runs[i].density` [x][y][z], `runs[i].volume`, `meta.voxel_mm`, `meta.origin_mm` | `yogunluk` |
| `parca.stl` | smooth STL of the chosen layout ({chosen}) | `geometri` |
| `baslangic.stl` | initial design surface | (extra) |
| `gerilme.txt` | von Mises at ultimate load on the chosen layout's surface (Mechanical export layout) | `gerilme_csv` |
| `eco_audit.json`, `eco_audit.md` | Eco Audit by phase, baseline and every candidate | (extra) |
| `materials/` | MatML Engineering Data XML + one card per material (E, Fty, Ftu at 20 °C and T, sources) | (extra) |

`result.json` also carries `details` (the full study record: materials with `stress_basis` T10/voxel per layout,
eco, T10 checks, bolt check). Rows on the T10-verified layout use the T10 stress for every material.

Numbers on screen must come from these files. Chosen: **{material}**, {mass:.3f} kg vs baseline {base:.3f} kg
({saving:.1f} % lighter), working temperature {T:g} °C. The load set-up is `{setup_note}`.
Peak in `gerilme.txt` outside the hole zones should equal `ranking[0].sigma_ult_Pa` / 1e6 =
{sig:.1f} MPa (film checks within 5 %; exclusion zone {excl:.1f} mm around the support/load bores).
"""


def write(st: Study, opt: Options, folder: str | Path, source: str = "") -> dict[str, Any]:
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    res = film_result(st, opt)
    full = st.out / "result.json"            # report.write_all: same ranking + "details" (materials, eco, T10 …)
    if full.exists():
        doc = json.loads(full.read_text(encoding="utf-8"))
        if doc.get("ranking") == json.loads(json.dumps(res["ranking"])):
            res = doc                          # the film reads only this folder (request item 11)
    save_json(out / "result.json", res)
    for name in ("eco_audit.json", "eco_audit.md"):
        if (st.out / name).exists():
            shutil.copyfile(st.out / name, out / name)
    if (st.out / "materials").is_dir():
        shutil.copytree(st.out / "materials", out / "materials", dirs_exist_ok=True)
    # loads in the film format
    shutil.copyfile(st.out / "loads_film.json", out / "yukler.json")
    # densities
    shutil.copyfile(st.out / f"density_{st.out.name}.json", out / "yogunluk.json")
    chosen = st.choice.get("design", "initial") if st.choice else "initial"
    vtag = next((round(100 * d["volfrac"]) for d in st.designs if d["label"] == chosen and d["volfrac"] < 1), None)
    stl = st.out / "cad" / (f"optimised_{vtag}.stl" if vtag else "initial_voxels.stl")
    shutil.copyfile(stl, out / "parca.stl")
    ini = st.out / "cad" / "initial.stl"
    shutil.copyfile(ini if ini.exists() else st.out / "cad" / "initial_voxels.stl", out / "baslangic.stl")
    # stress map at ultimate load
    key = f"vm_surface_{vtag}" if vtag else "vm_surface_initial"
    files = {}
    t10 = (getattr(st, "tet", {}) or {}).get("chosen") or {}
    src_field = st.fields.get(key)
    if t10.get("_surface") is not None:       # verified T10 stresses of the chosen layout (same as sigma_ult)
        src_field = t10["_surface"]
    if src_field is not None:
        X, vm = src_field
        k = opt.limit_to_ultimate
        lines = ["Node Number\tX Location (mm)\tY Location (mm)\tZ Location (mm)\tEquivalent (von-Mises) Stress (MPa)"]
        for i, (p, v) in enumerate(zip(X * 1e3, vm * k / 1e6, strict=True), 1):
            lines.append(f"{i}\t{p[0]:.4f}\t{p[1]:.4f}\t{p[2]:.4f}\t{v:.4f}")
        (out / "gerilme.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        files["gerilme_csv"] = "gerilme.txt"
    origin = (st.mesh.origin * 1e3).tolist()
    girdi = {"_not": f"aerokit.bracket hand-off of '{st.name}'; every number from the files in this folder.",
             "parca_adi": st.name, "sonuc": "result.json", "yukler": "yukler.json",
             "geometri": {"dosya": "parca.stl", "birim": "mm", "hizala": "yok", "yukari": "z"},
             "yogunluk": {"dosya": "yogunluk.json", "anahtar": "runs", "kok_mm": origin, "yukari": "z",
                          "voksel_mm": st.mesh.h * 1e3},
             "malzeme": st.choice.get("material", "") if st.choice else "",
             "kaynak": f"aerokit.bracket pipeline · {source}", **files}
    (out / "girdi.json").write_text(json.dumps(girdi, indent=1, ensure_ascii=False), encoding="utf-8")
    r0 = res["ranking"][0] if res["ranking"] else {}
    import time
    (out / "README.md").write_text(README.format(
        case=st.out.name, stamp=time.strftime("%Y-%m-%d %H:%M"), src=source, chosen=chosen,
        material=r0.get("material", "-"), mass=r0.get("mass_kg", float("nan")), base=st.baseline["mass_kg"],
        saving=100 * (1 - r0.get("mass_kg", st.baseline["mass_kg"]) / st.baseline["mass_kg"]), T=st.T,
        setup_note=st.setup.get("_about", "")[:200], sig=r0.get("sigma_ult_Pa", float("nan")) / 1e6,
        excl=float(st.setup.get("exclusion_mm", 0))), encoding="utf-8")
    return {"folder": str(out), "files": sorted(p.name for p in out.iterdir())}
