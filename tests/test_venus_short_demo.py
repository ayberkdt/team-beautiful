"""04_Venus/outputs/variants/short_demo: the no-science demonstrator variant stays consistent with the 6 Nov budget."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "04_Venus" / "outputs" / "variants" / "short_demo" / "result.json"
BUDGET = ROOT / "04_Venus" / "outputs" / "variants" / "budget_update" / "result.json"


@pytest.fixture(scope="module")
def res() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_three_kg_row_is_the_budget_design(res: dict) -> None:
    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    assert res["rows"][0]["payload_kg"] == 3.0
    assert res["rows"][0]["gross_kg"] == pytest.approx(budget["recommended_design"]["gross_kg"], rel=1e-9)


def test_less_payload_means_lighter_and_cheaper(res: dict) -> None:
    rows = res["rows"]
    assert all(r["converged"] for r in rows)
    for a, b in zip(rows, rows[1:], strict=False):
        assert b["gross_kg"] < a["gross_kg"] and b["hover_W"] < a["hover_W"] and b["mu0_loiter"] < a["mu0_loiter"]


def test_growth_factor_matches_the_sensitivity_study(res: dict) -> None:
    assert 2.3 < res["crosscheck"]["growth_kg_per_kg"] < 2.7


def test_late_release_keeps_the_array_above_hover(res: dict) -> None:
    for r in res["rows"]:
        assert r["demo_late"]["min_array_over_hover"] > 1.0
        assert r["demo_late"]["min_soc"] >= 0.99
        assert r["reserve_h"] >= 0.499


def test_selected_design_has_no_science() -> None:
    doc = json.loads((RESULT.parent / "files_0p5kg" / "design.json").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in doc["vehicle"]["components"]}
    assert comps["payload"]["mass_kg"] == pytest.approx(0.5)
    assert "nephelometer" not in comps["payload"]["name"].lower()
    assert sum(c["mass_kg"] for c in comps.values()) == pytest.approx(doc["vehicle"]["total_mass_kg"], abs=5e-4)
    assert doc["operations"]["release_hour_angle_deg"] == pytest.approx(-20.0)
    assert not any("dive" in e["event"] for e in doc["operations"]["events"])
