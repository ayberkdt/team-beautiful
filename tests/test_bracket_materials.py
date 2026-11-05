"""aerokit.bracket.matdata / cards / ecoaudit / crosscheck."""
import math
from pathlib import Path

import numpy as np
import pytest

from aerokit.bracket import cards, crosscheck, ecoaudit, matdata
from aerokit.materials import curves

ROOT = Path(__file__).resolve().parents[1]


def test_structural_steel_is_the_ansys_default():
    m = matdata.get("structural_steel")
    assert (m.rho.value, m.E.value, m.nu.value, m.Fty.value, m.Ftu.value) == (7850, 200e9, 0.3, 250e6, 460e6)
    assert m.cte.value == 1.2e-5 and m.k.value == 60.5 and m.cp.value == 434
    # EN 10028-2 P235GH: 153 / 235 at 300 C
    assert math.isclose(m.Fty_at(300.0) / m.Fty.value, 153 / 235)


def test_temperature_factors_from_mil_curves():
    m = matdata.get("ti64_lpbf")
    f = curves.curve_value("5.4.1.1.1", "F_ty", 572.0) / curves.curve_value("5.4.1.1.1", "F_ty", 70.0)
    assert math.isclose(m.Fty_at(300.0) / m.Fty.value, f)
    assert 0.55 < f < 0.70
    s = matdata.get("structural_steel")
    assert 0.88 < s.E_at(300.0) / s.E.value < 0.95


def test_interpolation_and_range():
    m = matdata.get("in718_lpbf")
    assert m.E_at(20.0) == m.E.value
    assert m.E.value * 184 / 200 < m.E_at(160.0) < m.E.value
    with pytest.raises(ValueError):
        m.E_at(400.0)


def test_aluminium_fails_300C_screen():
    sc = matdata.get("scalmalloy")
    assert sc.Fty_at(300.0) == pytest.approx(60e6)
    assert sc.Tmax.value < 300


def test_every_candidate_has_sources():
    for m in matdata.CANDIDATES.values():
        for p in (m.rho, m.E, m.Fty, m.Ftu, m.co2):
            assert p.source and p.tag in ("D", "D-ag", "S", "Y")
        assert m.k_source


def test_matml_roundtrip_and_real_export_layout(tmp_path):
    mats = [matdata.get(k) for k in matdata.names()]
    p = cards.write_matml(tmp_path / "ed.xml", mats, 300.0)
    back = cards.read_matml(p)
    assert len(back) == len(mats)
    steel = next(v for k, v in back.items() if k.startswith("Structural Steel"))
    assert steel["Density"] == 7850
    assert steel["Young's Modulus"][0] == 2e11
    assert math.isclose(steel["Young's Modulus"][1], matdata.get("structural_steel").E_at(300.0), rel_tol=1e-9)
    assert steel["Temperature [Elasticity]"] == [20.0, 300.0]
    assert math.isclose(steel["Tensile Yield Strength"], 153e6 / 235 * 250, rel_tol=1e-9)
    assert math.isclose(steel["Shear Modulus"][0], 2e11 / 2.6, rel_tol=1e-9)
    text = p.read_text(encoding="utf-8")
    for tag in ("<EngineeringData", "<MatML_Doc>", 'property="pr4"', 'parameter="pa88"', "7.88860905221012e-31",
                '<Unit power="-3">', "Variable Type"):
        assert tag in text


def test_markdown_card_lists_sources():
    s = cards.markdown_card(matdata.get("ti64_lpbf"))
    assert "Ti-6Al-4V" in s and "| Tensile yield" in s and "MIL-HDBK-5J" in s


def test_eco_audit_phases_and_hand_calc():
    m = matdata.get("structural_steel")
    inp = ecoaudit.EcoInputs(route="machined", buy_to_fly=8.0, transport_km=1000.0, life_km=6.0e7)
    a = ecoaudit.audit(1.0, m, inp)
    assert a.phases["material"].co2_kg == pytest.approx(8 * 1.8)
    assert a.phases["transport"].energy_MJ == pytest.approx(1e-3 * 1000 * 0.94)
    assert a.phases["use"].co2_kg == pytest.approx(1e-3 * 6.0e7 * 6.5 * 0.072)
    assert a.use_marginal_co2_kg == pytest.approx(125 * 25 * 3.16)
    assert a.total.co2_kg == pytest.approx(sum(p.co2_kg for p in a.phases.values()))


def test_eco_compare_lighter_part_saves_use_phase():
    steel, ti = matdata.get("structural_steel"), matdata.get("ti64_lpbf")
    base = ecoaudit.audit(1.0, steel, ecoaudit.EcoInputs(route="machined"))
    new = ecoaudit.audit(0.3, ti, ecoaudit.EcoInputs(route="am"))
    c = ecoaudit.compare(base, new)
    assert c["phases"]["use"]["delta_co2_kg"] < 0
    assert c["mass_saving_kg"] == pytest.approx(0.7)
    assert c["break_even_km"] >= 0


def test_crosscheck_signatures(tmp_path):
    ours = {"mass_kg": 1.0, "max_deformation_mm": 0.5, "max_von_mises_MPa": 200.0, "von_mises_outside_MPa": 150.0,
            "compliance_J": 2.0, "strain_energy_J": 1.0}
    ansys = {"mass_kg": 1000.0, "max_deformation_mm": 0.5 / 0.913, "max_von_mises_MPa": 400.0,
             "von_mises_outside_MPa": 151.0, "compliance_J": 2.0, "strain_energy_J": 1.0}
    rows = {r.metric: r for r in crosscheck.compare(ours, ansys, {"kE": 0.913})}
    assert rows["mass_kg"].status == "CHECK" and any("1000" in c for c in rows["mass_kg"].causes)
    assert any("temperature" in c for c in rows["max_deformation_mm"].causes)
    # Ansys/ours = 1/0.913 means Ansys deformed MORE: Ansys used the softer E(T), ours E(20 °C)
    assert any("ours at 20" in c for c in rows["max_deformation_mm"].causes)
    r2 = crosscheck.compare({"max_deformation_mm": 1.0}, {"max_deformation_mm": 0.913}, {"kE": 0.913})
    assert any("Ansys used E at 20-22" in c for c in next(r for r in r2 if r.metric == "max_deformation_mm").causes)
    assert any("singular" in c for c in rows["max_von_mises_MPa"].causes)
    assert rows["von_mises_outside_MPa"].status == "OK"
    assert rows["min_safety_factor"].status == "missing"
    p = crosscheck.write_template(tmp_path / "t.csv", ours)
    o2, a2 = crosscheck.read_template(p)
    assert o2["mass_kg"] == 1.0 and a2["mass_kg"] is None
    assert "Ansys/ours" in crosscheck.markdown(list(rows.values()))


def test_mechanical_export_parser_and_zone_peak(tmp_path):
    txt = ("Node Number\tX Location (m)\tY Location (m)\tZ Location (m)\tEquivalent (von-Mises) Stress (Pa)\n"
           "1\t0.010\t0.000\t0.000\t5.0e8\n2\t0.050\t0.000\t0.000\t2.0e8\n3\t0.060\t0.010\t0.000\t1.0e8\n")
    p = tmp_path / "s.txt"
    p.write_text(txt, encoding="utf-8")
    ex = crosscheck.read_mechanical_export(p)
    assert ex["unit"] == "MPa" and np.allclose(ex["value"], [500, 200, 100])
    assert np.allclose(ex["xyz"][0], [10, 0, 0])
    pk = crosscheck.peak_outside(ex["xyz"], ex["value"],
                                 [{"axis": "z", "center_mm": [10, 0, 0], "diameter_mm": 4}], 2.0)
    assert pk["max"] == 200 and pk["max_all"] == 500


def test_eco_steel_families_added():
    from aerokit.materials import eco
    assert eco.co2_per_kg("carbon_steel") == 1.8 and eco.co2_per_kg("low_alloy_steel") == 2.0
    with pytest.raises(ValueError):
        eco.co2_per_kg("carbon_steel", recycled_content=0.5)      # no recycled route recorded


def test_crosscheck_thermal_signature():
    ours = {"von_mises_outside_MPa": 130.0}
    ansys = {"von_mises_outside_MPa": 130.0 + 480.0}
    rows = {r.metric: r for r in crosscheck.compare(ours, ansys, {"thermal_vm_MPa": 470.0})}
    assert any(c.startswith("thermal") for c in rows["von_mises_outside_MPa"].causes)


def test_crosscheck_verdict_lines():
    from aerokit.bracket import crosscheck as cc
    ours = {"max_deformation_mm": 1.0, "compliance_J": 1.0, "strain_energy_J": 0.5, "mass_kg": 1.0}
    assert cc.verdict(cc.compare(ours, {})).startswith("NO DATA")
    assert cc.verdict(cc.compare(ours, dict(ours))).startswith("AGREES:")
    v = cc.verdict(cc.compare(ours, {**ours, "max_deformation_mm": 1e-3}))
    assert v.startswith("DISCREPANCY") and "units" in v
    hid = cc.verdict(cc.compare(ours, {k: x * 0.913 if k != "mass_kg" else x for k, x in ours.items()},
                                {"kE": 0.913}))
    assert hid.startswith("AGREES within tolerance, BUT") and "temperature" in hid
