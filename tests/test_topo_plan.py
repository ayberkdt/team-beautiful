"""Day-of conversions for topology runs (aerokit.design.topo_plan)."""
import json
from pathlib import Path

from aerokit.design import topo_plan as tpl
from aerokit.verification import check, check_true, expect_error

ROOT = Path(__file__).resolve().parents[1]


def test_conversions_ge_bracket():
    # GE envelope ~178.5 x 107.1 x 62.475 mm, Ti-6Al-4V 4430 kg/m3; Elmas's 0.731 kg design
    vol = 0.1785 * 0.1071 * 0.062475
    f = tpl.fraction_for_mass(0.731, 4430.0, vol)
    check("0.731 kg -> 13.8 % of the GE envelope", f, 0.731 / 4430.0 / vol, rtol=1e-12)
    check("Discovery volume reduction = 100 (1 - f)", tpl.discovery_target(f), 100 * (1 - f), rtol=1e-12)
    check("Mechanical percent to retain = 100 f", tpl.mechanical_target(f), 100 * f, rtol=1e-12)
    expect_error("mass larger than the envelope", tpl.fraction_for_mass, 50.0, 4430.0, vol, error=ValueError)


def test_knee_on_the_retain_sweep():
    d = json.loads((ROOT / "prev_guess" / "01_Ansys" / "retain_sweep" / "retain_sweep.json").read_text(encoding="utf-8"))
    v = [r["volume"] for r in d["runs"]]
    c = [r["compliance_rel"] for r in d["runs"]]
    k = tpl.knee(v, c)
    check_true(f"knee of the L-bracket sweep inside the swept range ({k['volume']})", min(v) < k["volume"] < max(v))
    t = tpl.trio({"mass": 1.0, "deformation": 1.0, "stress": 100.0}, {"mass": 0.71, "deformation": 1.14,
                                                                      "stress": 104.0})
    check("trio mass", t["mass"], -29.0, rtol=1e-9)
    check("trio stress", t["stress"], 4.0, rtol=1e-9)
