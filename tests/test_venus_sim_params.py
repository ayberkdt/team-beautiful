"""Contract of studies/final_2026/venus/sim_params.json (written by scripts/venus_sim_params.py)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / "studies" / "final_2026" / "venus" / "sim_params.json"
TAGS = {"D", "D-ag", "K", "Y"}


def _walk(node: object, path: str, out: list[tuple[str, dict]]) -> None:
    if isinstance(node, dict):
        if "value" in node:
            out.append((path, node))
        for k, v in node.items():
            if k != "value":
                _walk(v, f"{path}.{k}", out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk(v, f"{path}[{i}]", out)


@pytest.fixture(scope="module")
def doc() -> dict:
    if not PATH.exists():
        pytest.skip("sim_params.json not generated")
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_every_value_has_unit_tag_source(doc: dict) -> None:
    vals: list[tuple[str, dict]] = []
    _walk(doc, "", vals)
    assert len(vals) > 30
    for path, v in vals:
        assert {"unit", "tag", "source"} <= set(v), path
        parts = {p.strip().split("(")[0].strip() for p in v["tag"].replace("+", "/").split("/")}
        assert parts & TAGS, (path, v["tag"])


def test_atmosphere_table_is_consistent(doc: dict) -> None:
    atm = doc["atmosphere_and_wind"]
    rows = atm["rows"]
    n = len(rows["altitude_m"])
    assert all(len(col) == n for col in rows.values())
    assert set(rows) == set(atm["columns"])
    i = rows["altitude_m"].index(55000.0)
    assert 0.85 < rows["density_kg_m3"][i] < 0.93          # probe envelope 0.867-0.907
    lo, hi = rows["density_low"][i], rows["density_high"][i]
    assert lo <= rows["density_kg_m3"][i] <= hi
    p = rows["pressure_Pa"]
    assert all(a > b for a, b in zip(p, p[1:]))               # monotone with altitude


def test_version_matches_design(doc: dict) -> None:
    design = json.loads((PATH.parent / "design.json").read_text(encoding="utf-8"))
    assert doc["version"] == design["version"]
    assert len(doc["failure_modes"]) >= 8 and all({"trigger", "effect", "recovery", "tag"} <= set(f)
                                                   for f in doc["failure_modes"])
