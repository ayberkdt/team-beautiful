"""Requirements-driven design pipeline: reproduces the 2023 rehearsal, sensitivity, sustainability."""
import math

import pytest

from aerokit.data import example_path
from aerokit.design import sustainability as su
from aerokit.design.labels import display_value, label, signed_percent
from aerokit.design.pipeline import lift_slope, lift_slope_helmbold
from aerokit.design.requirements import load_assumptions, load_requirements
from aerokit.design.sensitivity import tornado
from aerokit.design.sizing import size
from aerokit.units import UnitError
from aerokit.verification import check, check_true, expect_error

REQ = example_path("design", "ansys_2023_requirements.json")
DOC04 = "prev_guess/01_Ansys/docs/04_2023_example_solution.md §1 (aerokit sizing raymer, 2026-10-25)"
#: docs/04 predates the power-weight coupling; it is reproduced with the coupling switched off
REHEARSAL = {"power_weight_coupling": "off"}


@pytest.mark.parametrize("fraction, text", [(-3.8e-8, "0.0 %"), (0.0, "0.0 %"), (0.566, "+56.6 %"),
                                            (-0.401, "-40.1 %"), (-0.0004, "0.0 %")])
def test_signed_percent_has_no_negative_zero(fraction, text):
    assert signed_percent(fraction) == text


def test_reproduces_rehearsal():
    r = size(load_requirements(REQ), load_assumptions(REHEARSAL))
    check("W0 [kg]", r.mass, 5974, atol=0.5, source=DOC04)
    check("S [m²]", r.S, 27.5, atol=0.05, source=DOC04)
    check("installed power [kW]", r.P_installed / 1e3, 1667, atol=0.5, source=DOC04)
    check("P/W ceiling [W/N]", r.constraints["Ceiling 10000 m"], 28.45, atol=0.005, source=DOC04)
    check("P/W Vmax [W/N]", r.constraints["Vmax 500 km/h (0 m)"], 28.38, atol=0.005, source=DOC04)
    check("P/W climb [W/N]", r.constraints["Climb 10 m/s (SL)"], 17.70, atol=0.005, source=DOC04)
    check("P/W take-off [W/N]", r.constraints["Take-off run 800 m"], 10.88, atol=0.005, source=DOC04)
    check_true("ceiling governs", r.governing == "Ceiling 10000 m", r.governing)
    check("aircraft object carries the sized values", r.aircraft.W0, r.W0, rtol=1e-12)


def test_psfc_unit_bridge():
    """The pipeline stores PSFC in SI; the Raymer helpers take lb/(hp·h): both conversions must agree."""
    from aerokit import units
    from aerokit.aero import sizing as rs
    check("units lb/(hp·h) factor = sizing.c_bhp_si(1)", units.parse("1 lb/(hp*h)", "psfc"), rs.c_bhp_si(1.0),
          rtol=1e-6, source="two independent constant sets (units.py vs sizing.py)")


def test_requirements_validation(tmp_path):
    bad = tmp_path / "r.json"
    bad.write_text('{"rnage": "1300 km"}', encoding="utf-8")
    with pytest.raises(UnitError):
        load_requirements(bad)
    bad.write_text('{"range": "1300 km/h"}', encoding="utf-8")
    with pytest.raises(UnitError):
        load_requirements(bad)
    bad.write_text('[1, 2]', encoding="utf-8")
    with pytest.raises(ValueError):
        load_requirements(bad)
    with pytest.raises(UnitError):
        load_assumptions({"power_lapse": "magic"})
    with pytest.raises(KeyError):
        size(load_requirements({"crew": 1, "stall_speed": "150 km/h"}), load_assumptions())


def test_sensitivity_and_lapse_finding():
    base, rows = tornado(load_requirements(REQ), load_assumptions())
    by = {r.key: r for r in rows}
    check_true("K_LD has the largest power swing", rows[0].key == "K_LD", rows[0].key)
    check_true("power lapse exponent 0.7–1.0 changes the installed power by < 1 %",
               by["power_lapse_n"].power_swing / base.P_installed < 0.01,
               f"{by['power_lapse_n'].power_swing / 1e3:.1f} kW", source="this study (corrects docs/04 §1)")
    check_true("at n = 0.7 the Vmax constraint governs", by["power_lapse_n"].governing_low.startswith("Vmax"))


def test_helmbold_and_labels():
    check("Helmbold → 2π for AR → ∞", lift_slope_helmbold(1e6), 2 * math.pi, rtol=1e-5,
          source="Anderson 2017 Eq. 5.81 limit")
    check("Helmbold, AR = 1", lift_slope_helmbold(1.0), 2 * math.pi / (math.sqrt(5.0) + 2.0), rtol=1e-12,
          source="Anderson 2017 Eq. 5.81 with a0 = 2π")
    check_true("labels never use E notation", "e-0" not in label("psfc_cruise", 7.456e-7, 9.1e-7))
    check_true("PSFC shown in lb/(hp·h)", display_value("psfc_cruise", 8.2849e-7) == "0.5")
    expect_error("AR ≤ 0 rejected", lift_slope_helmbold, 0.0, error=ValueError)


def test_lift_slope_follows_anderson_applicability():
    a, method = lift_slope(9.0)
    check("AR 9 → lifting line a0/(1 + a0/πAR)", a, 2 * math.pi / (1 + 2 / 9), rtol=1e-12,
          source="Anderson 2017 Eq. 5.69, PDF p. 478; 'AR > 4' rule PDF p. 497")
    check_true("AR 9 method is lifting line", "5.69" in method)
    a3, method3 = lift_slope(3.0)
    check("AR 3 → Helmbold", a3, lift_slope_helmbold(3.0), rtol=1e-12, source="Anderson 2017 Eq. 5.81, PDF p. 497")
    check_true("AR 3 method is Helmbold", "5.81" in method3)
    a_tau, _ = lift_slope(9.0, tau=0.1)
    check("τ = 0.1 → Eq. 5.70", a_tau, 2 * math.pi / (1 + 2 / 9 * 1.1), rtol=1e-12,
          source="Anderson 2017 Eq. 5.70, PDF p. 478")
    expect_error("τ ≥ 1 rejected", lift_slope, 9.0, tau=1.0, error=ValueError)


def test_sustainability():
    e = su.emissions(930.0, passengers=10, distance_km=1300.0)
    check("CO2 = 3.16 × fuel", e.co2_kg, 930 * 3.16, rtol=1e-12)
    check("fuel per pax-km", e.fuel_per_pax_km, 930 / 13000, rtol=1e-12)
    check("SAF 50 % blend, 80 % LCA reduction", su.saf_scenario(1000.0, 0.5, 0.8), 600.0, rtol=1e-12)
    h = su.hybrid_loiter(500e3, 1800.0, fuel_saved_kg=120.0, specific_energy_Wh_kg=250.0)
    check("battery mass = Pt/(η f e)", h.battery_mass_kg, 500e3 * 1800 / (0.9 * 0.8 * 250 * 3600), rtol=1e-12)
    check_true("battery heavier than the loiter fuel it replaces (250 Wh/kg)", h.mass_penalty_kg > 0)
    expect_error("negative fuel rejected", su.emissions, -1.0, error=ValueError)
    expect_error("blend > 1 rejected", su.saf_scenario, 1.0, 1.5, 0.5, error=ValueError)


def test_empty_weight_factor_growth():
    """W0 grows much faster than We/W0 (weight growth factor); default factor 1 reproduces docs/04."""
    req = load_requirements(REQ)
    base = size(req, load_assumptions(REHEARSAL))
    cal = size(req, load_assumptions({**REHEARSAL, "empty_weight_factor": 1.118}))
    check("factor 1.0 reproduces the rehearsal W0", base.mass, 5974, atol=0.5, source=DOC04)
    check_true("King Air calibration (×1.118 on We/W0) raises W0 by > 25 %", cal.mass / base.mass > 1.25,
               f"{cal.mass:.0f} kg vs {base.mass:.0f} kg")
    check("We/W0 is scaled exactly", cal.We_W0 / 1.118,
          __import__("aerokit.aero.sizing", fromlist=["x"]).empty_weight_ratio(cal.W0, "twin turboprop"), rtol=1e-8)   # fixed-point tolerance 1e-9
    expect_error("we_factor ≤ 0 rejected", __import__("aerokit.aero.sizing", fromlist=["x"]).takeoff_weight,
                 1e4, 0.1, "twin turboprop", we_factor=0.0, error=ValueError)


def test_king_air_validation_is_reported_not_tuned():
    from aerokit.design.validation import KING_AIR_350I, calibrate_lapse_exponent, validate_king_air
    rows = {r.quantity: r for r in validate_king_air()}
    for q in ("Service ceiling", "Maximum level speed (best altitude)", "Take-off distance to 50 ft",
              "Empty-weight fraction We/W0"):
        check_true(f"King Air 350i: {q} predicted within ±50 % (model-error band, not a pass criterion)",
                   abs(rows[q].error) < 0.5, f"{rows[q].error * 100:+.1f} %")
    check("published OEW/MTOW of the 350i", rows["Empty-weight fraction We/W0"].published, 4516 / 6804,
          rtol=1e-12, source=KING_AIR_350I["oew_kg"][1])
    n = calibrate_lapse_exponent()
    check_true("ceiling-calibrated lapse exponent is between 0.5 and 1", 0.5 < n < 1.0, f"n = {n:.3f}")


def test_full_pipeline_writes_report_and_audited_figures(tmp_path):
    from aerokit.design.pipeline import run
    r = run(REQ, {"drag_method": "buildup"}, tmp_path)
    for f in ("report.md", "constraint_diagram.png", "sensitivity_tornado.png", "vn_diagram.png", "payload_range.png"):
        check_true(f"pipeline wrote {f}", (tmp_path / f).exists())
    for f in tmp_path.glob("*.denetim.txt"):
        check_true(f"datawiz audit 0 errors: {f.name}", " 0 HATA" in f.read_text(encoding="utf-8").splitlines()[0])
    check_true("all 8 card requirements met (build-up drag)", all(c["passed"] for c in r.compliance),
               [c["requirement"] for c in r.compliance if not c["passed"]])
    text = (tmp_path / "report.md").read_text(encoding="utf-8")
    check_true("report has the compliance and sensitivity sections",
               "Requirement compliance" in text and "One-at-a-time sensitivity" in text and "Drag build-up" in text)
    check_true("report tables contain no E notation", "e+0" not in text and "e-0" not in text)
    check_true("build-up design lighter than the K_LD design", r.sizing.mass < 5974.0, f"{r.sizing.mass:.0f} kg")
