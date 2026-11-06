"""PREVIEW — geometry and loads only, no analysis.

Builds the film input package for the official EUROAVIA Ideathon 2026 Ansys bracket in the film pipeline's own input
format (``D:\\Video Simulations\\Ideathon-2026-Ansys``: ``hazirla.mjs`` + manifest schema ``ansys-film/1``,
``handoff_requests.md``). Geometry, supports, load cases, temperature, baseline material name and baseline mass only.
Every field that needs FEA / topology / eco results is left out (``null``) and listed in ``film.json["_missing"]``.

    export PYTHONPATH="src;D:/tmp_ideathon/pylib"
    python studies/final_2026/ansys/official_2026-11-05/film_preview/build_preview.py

Writes ONLY into this folder. Reads (never writes): ``../derived/``, ``../setup/``, ``../unpacked/dsco/``,
``../visuals/initial_exact.stl`` (if present), ``../catalogue/materials_catalogue.json`` (if present; linked, not copied),
``src/aerokit/bracket/report.py`` (``_film_loads``: the pipeline's own ``yukler.json`` writer).
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from aerokit.bracket.report import _film_loads

HERE = Path(__file__).resolve().parent
CASE = HERE.parent                                     # official_2026-11-05
TAG = "PREVIEW — geometry and loads only, no analysis"
SETUP = CASE / "setup" / "setup_official_fixed_bores.json"
STL_EXACT = CASE / "visuals" / "initial_exact.stl"
STL_FACETS = CASE / "derived" / "initial_from_facets.stl"
DSCO = CASE / "unpacked" / "dsco" / "SpaceClaim"
CATALOGUE = CASE / "catalogue" / "materials_catalogue.json"
# names only (task brief 2026-11-05); property values come later from ../catalogue/
BASELINE_MATERIAL = "Structural steel, S275N"          # exact label in the organiser's Discovery file (document.xml)
CANDIDATES = ["Aluminum 2618-T6", "Ti-8Al-1Mo-1V (single annealed)"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_stl(p: Path) -> np.ndarray:
    b = p.read_bytes()
    n = struct.unpack_from("<I", b, 80)[0]
    if len(b) != 84 + 50 * n:
        raise SystemExit(f"{p}: not a binary STL ({len(b)} bytes, header says {n} triangles)")
    rec = np.frombuffer(b, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
    return rec["v"].astype(np.float64)                 # (n, 3, 3) mm


def stl_volume_mm3(T: np.ndarray) -> float:
    return float(np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])).sum() / 6.0)


def organiser_density() -> tuple[float, list[str]]:
    vals, files = set(), []
    for f in sorted((DSCO / "Discovery").glob("table__*__dt1.xml")):
        for m in re.finditer(r'quantity="Density" unit="KilogramPerCubicMeter" value="([0-9.]+)"', f.read_text(encoding="utf-8", errors="replace")):
            vals.add(float(m.group(1)))
            files.append(f.name)
    if len(vals) != 1:
        raise SystemExit(f"organiser material tables carry {sorted(vals)} kg/m3 — expected exactly one density")
    return vals.pop(), files


def organiser_masses() -> list[float]:
    t = (DSCO / "document.xml").read_text(encoding="utf-8", errors="replace")
    return [float(v) for v in re.findall(r"<result><quantityType>Mass</quantityType><unit>Kilogram</unit><value>([0-9.]+)</value>", t)]


def main() -> int:
    stl_src = STL_EXACT if STL_EXACT.exists() else STL_FACETS
    T = read_stl(stl_src)
    vol = stl_volume_mm3(T)
    lo, hi = T.reshape(-1, 3).min(0), T.reshape(-1, 3).max(0)
    rho, rho_files = organiser_density()
    m_ours = vol * 1e-9 * rho
    masses = organiser_masses()
    m_org = min(masses, key=lambda m: abs(m - m_ours))     # the organiser monitor value of THIS geometry
    if abs(m_org - m_ours) / m_org > 0.005:
        raise SystemExit(f"no organiser mass within 0.5 % of STL volume x density ({m_ours:.3f} kg; monitors {masses})")

    # baslangic.stl: same triangles, header re-labelled PREVIEW (bytes 80.. identical to the source)
    src = stl_src.read_bytes()
    header = f"PREVIEW geometry only, no analysis - {stl_src.name}".encode("ascii")[:80].ljust(80, b" ")
    (HERE / "baslangic.stl").write_bytes(header + src[80:])

    # yukler.json: the pipeline's own writer (report._film_loads) on the official set-up; bbox = this STL (m)
    setup = json.loads(SETUP.read_text(encoding="utf-8"))
    st = SimpleNamespace(name=setup["name"], setup=setup, vm=SimpleNamespace(bbox=lambda: (lo / 1e3, hi / 1e3)))
    L = _film_loads(st)
    L["_not"] = f"{TAG}. " + L["_not"] + f" Source: {SETUP.relative_to(CASE).as_posix()}; envelope = bbox of baslangic.stl."
    (HERE / "yukler.json").write_text(json.dumps(L, indent=1, ensure_ascii=False), encoding="utf-8")

    cat = CATALOGUE if CATALOGUE.exists() else None
    # join key into catalogue/materials_catalogue.json "materials" (keys only, never values); written only if the key exists
    cat_keys = set(json.loads(cat.read_text(encoding="utf-8")).get("materials", {})) if cat else set()
    key_of = {BASELINE_MATERIAL: "S275N", CANDIDATES[0]: "Al2618", CANDIDATES[1]: "Ti811"}
    mats = [{"name": BASELINE_MATERIAL, "baseline": True}] + [{"name": n} for n in CANDIDATES]
    for m in mats:
        if key_of[m["name"]] in cat_keys:
            m["catalogue_key"] = key_of[m["name"]]
    film = {
        "schema": "ansys-film/1",
        "status": "preview",                           # not "final" -> film prints PROVISIONAL on the source line
        "_preview": TAG,
        "card": f"{TAG} · official EUROAVIA 2026 bracket (organiser CAD + card)",
        "part_name": "EUROAVIA 2026 cowling-support bracket (initial S275N design)",
        "temperature_C": setup["temperature_C"],
        "baseline": {"material": BASELINE_MATERIAL, "mass_kg": m_org, "geometry": "baslangic.stl", "unit": "mm", "up": "z",
                     "note": "organiser CAD, initial design"},
        "redesign": {"material": None, "route": None, "mass_kg": None, "geometry": None, "retained_volume": None},
        "loads": "yukler.json",
        "density": None,
        "print": None,
        "stress": None,
        "materials": mats,
        "materials_catalogue": str(cat.relative_to(CASE).as_posix()) if cat else None,
        "eco_audit": None,
        "cad_setup": {"holes": [{"id": h["id"], "role": h["role"], "center_mm": h["center_mm"], "diameter_mm": h["diameter_mm"],
                                 "axis": h["axis"]} for h in setup["holes"]],
                      "roles_source": "edited",
                      "about": "holes measured from the organiser CAD (derived/features.json); roles set from the organiser card "
                               "(setup/boundary_conditions.md §2–3, [Y] interpretation), not by the automatic scan"},
        "convergence": None,
        "crosscheck": None,
        "_missing": {
            "redesign.*": "no topology / redesign yet",
            "density": "no topology run on the official part",
            "print": "printability belongs to the redesign; omitted so shot 04 does not judge the steel baseline",
            "stress": "no FEA on the official part (no gerilme.txt / stress_300C.txt)",
            "materials[].density_kg_m3, Fty_*, curve, mass_kg, utilisation, passes, co2e_kg, stress_basis":
                "names only; values come from official_2026-11-05/catalogue/ and the analysis",
            "eco_audit": "no Eco Audit numbers in this package (organiser .prd set-up not evaluated here)",
            "convergence, crosscheck": "no optimiser run, no Ansys numbers",
        },
        "_kaynak": {
            "built": time.strftime("%Y-%m-%d %H:%M:%S"), "by": "film_preview/build_preview.py",
            "baslangic.stl": {"source": stl_src.relative_to(CASE).as_posix(), "source_sha256": sha(stl_src),
                              "triangles": int(len(T)), "volume_mm3": vol, "bbox_mm": [lo.tolist(), hi.tolist()]},
            "baseline.mass_kg": {"value_source": "unpacked/dsco/SpaceClaim/document.xml (Discovery Mass monitor)",
                                 "monitors_in_file_kg": masses, "check_volume_x_density_kg": m_ours,
                                 "density_kg_m3": rho, "density_source": [f"unpacked/dsco/SpaceClaim/Discovery/{f}" for f in rho_files]},
            "baseline.material": "unpacked/dsco/SpaceClaim/document.xml MaterialEntitySurrogate label",
            "temperature_C, cad_setup, yukler.json": SETUP.relative_to(CASE).as_posix() + f" (sha256 {sha(SETUP)})",
            "materials[].name (candidates)": "task brief 2026-11-05 (names only)",
        },
    }
    (HERE / "film.json").write_text(json.dumps(film, indent=1, ensure_ascii=False), encoding="utf-8")

    girdi = {
        "_not": f"{TAG}. Film input (paths relative to this folder): manifest film.json + loads. 'geometri' is the BASELINE "
                "CAD because hazirla.mjs requires geometri or yogunluk; there is no redesigned part yet.",
        "ansys": "film.json",
        "yukler": "yukler.json",
        "geometri": {"dosya": "baslangic.stl", "birim": "mm", "hizala": "yok", "yukari": "z"},
    }
    (HERE / "girdi.json").write_text(json.dumps(girdi, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"STL {stl_src.relative_to(CASE).as_posix()} · {len(T)} triangles · {vol / 1e9:.6f} m3 · x {rho:g} = {m_ours:.3f} kg "
          f"(organiser monitor {m_org:.3f} kg, diff {100 * (m_ours - m_org) / m_org:+.3f} %)")
    print(f"yukler.json: {len(L['destekler'])} supports, {len(L['kuvvetler'])} load entries · catalogue: {cat or 'not present'}")
    print(f"wrote {', '.join(sorted(p.name for p in HERE.iterdir() if p.is_file()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
