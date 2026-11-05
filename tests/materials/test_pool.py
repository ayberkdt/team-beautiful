"""Material pool (aerokit.materials.pool): schema, units, agreement with the study files, ranking bridge."""
import hashlib
import json
from pathlib import Path

from aerokit.materials import pool
from aerokit.verification import check, check_true, expect_error

ROOT = Path(__file__).resolve().parents[2]


def test_schema_units_and_tags():
    mats = pool.load()["materials"]
    check_true("31 or more materials", len(mats) >= 31)
    bad = []
    for name, rec in mats.items():
        for k, v in rec.get("properties", {}).items():
            if not isinstance(v.get("value"), int | float) or not v.get("source") or v.get("tag") not in "DSY":
                bad.append((name, k))
            if k in pool.UNITS and v.get("unit") != pool.UNITS[k]:
                bad.append((name, k, v.get("unit")))
    check_true(f"every entry has a number, a source, a D/S/Y tag and the standard unit ({bad[:3]})", not bad)
    rhos = [r["properties"]["rho"]["value"] for r in mats.values() if "rho" in r["properties"]]
    check_true("densities between a honeycomb core and nickel alloys", min(rhos) >= 20 and max(rhos) <= 9000)


def test_bundled_copy_matches_research_notes():
    src = ROOT / "research_notes" / "Malzeme havuzu" / "materials_pool.json"
    if src.exists():
        bundled = ROOT / "src" / "aerokit" / "data" / "materials" / "materials_pool.json"
        check_true("package copy is identical to the research-notes pool",
                   hashlib.sha256(src.read_bytes()).hexdigest() == hashlib.sha256(bundled.read_bytes()).hexdigest())


def test_agrees_with_study_values_and_ranks():
    study = json.loads((ROOT / "studies" / "tradeoff" / "bracket_a320_strength.json").read_text(encoding="utf-8"))
    check("AlSi10Mg E agrees with the study file", pool.value("AlSi10Mg L-PBF", "E") * 1e9,
          study["materials"]["AlSi10Mg"]["E"], rtol=1e-9)
    check("Scalmalloy E agrees with the study file", pool.value("Scalmalloy L-PBF", "E") * 1e9,
          study["materials"]["Scalmalloy"]["E"], rtol=1e-9)
    top = pool.rank_pool("panel_stiff")
    check_true("stiff panel: a composite or magnesium leads, not a steel",
               pool.get(top[0].name)["family"] in ("composite", "magnesium", "polymer", "core"))
    strong = pool.rank_pool("tie_strong", pool.names("aluminium") + pool.names("titanium") + pool.names("steel"))
    check_true("strong tie among metals: titanium or a high-strength steel leads",
               pool.get(strong[0].name)["family"] in ("titanium", "steel"))
    expect_error("unknown material", pool.get, "unobtainium", error=KeyError)
