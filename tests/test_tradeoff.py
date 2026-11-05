"""Material × route trade-off (aerokit.design.tradeoff), checked by hand on a two-material study."""
import copy
import json

from aerokit.design import tradeoff as T
from aerokit.verification import check, check_true, expect_error

F = lambda v, lo=None, hi=None, tag="Y": {"value": v, "low": v if lo is None else lo, "high": v if hi is None else hi,
                                         "unit": "", "source": "test", "tag": tag}
BASE = {
    "name": "hand", "case": "tie_stiff", "reference_material": "A", "reference_mass": F(2.0),
    "lifecycle": {"fuel_per_kg_per_flight": F(0.1, 0.05, 0.15), "flights": F(1000.0), "co2_per_kg_fuel": F(3.0),
                  "grid_co2_per_MJ": F(0.1)},
    "materials": {"A": {"E": 70e9, "rho": 2800.0, "co2_per_kg": F(10.0)},
                  "B": {"E": 70e9, "rho": 1400.0, "co2_per_kg": F(100.0, 50.0, 150.0)}},
    "routes": {"mill": {"buy_to_fly": F(5.0), "process_MJ_per_kg": F(2.0), "mass_factor": F(1.0)}},
    "objectives": ["mass_kg", "co2_total_kg"],
}


def test_hand_values():
    r = {x.material: x for x in T.evaluate(T._parse(BASE))}
    check("B has half the density at equal E → half the mass", r["B"].mass_kg, 1.0, rtol=1e-12)
    check("A production = 2·5·10 + 2·5·2·0.1", r["A"].co2_production_kg, 102.0, rtol=1e-12)
    check("A use = 2·0.1·1000·3", r["A"].co2_use_kg, 600.0, rtol=1e-12)
    check("B total = 1·5·100 + 1·5·0.2 + 300", r["B"].co2_total_kg, 801.0, rtol=1e-12)
    check_true("both on the Pareto front (B lighter, A cleaner)",
               len(T.pareto(list(r.values()), ("mass_kg", "co2_total_kg"))) == 2)


def test_tornado_and_monte_carlo():
    s = T._parse(BASE)
    tor = {t["factor"]: t for t in T.tornado(s)}
    # nominal: A 702, B 801 → best A, margin 99. Fuel factor high (0.15): A 102 + 900, B 501 + 450 → B wins.
    check("fuel factor high flips the margin: 951 − 1002", tor["lifecycle.fuel_per_kg_per_flight"]["margin_high"],
          951.0 - 1002.0, rtol=1e-12)
    check_true("… and is flagged as reversing", tor["lifecycle.fuel_per_kg_per_flight"]["reverses"])
    mc = T.monte_carlo(s, samples=400, seed=3)
    check("probabilities sum to 1", sum(mc["p_best"].values()), 1.0, rtol=1e-12)
    check_true("both options win sometimes under these ranges", 0 < mc["p_best"]["A / mill"] < 1, mc["p_best"])
    check_true("same seed, same result", T.monte_carlo(s, 400, 3) == mc)


def test_penalty_and_validation():
    raw = copy.deepcopy(BASE)
    raw["exchange"] = {"mass_kg": 1000.0, "co2_total_kg": 1.0}
    z = T.penalty(T.evaluate(T._parse(raw)), raw["exchange"])
    check("Z(B) = 1000·1 + 801", z["B / mill"], 1801.0, rtol=1e-12)
    bad = copy.deepcopy(BASE)
    bad["lifecycle"]["flights"] = 1000
    expect_error("bare number refused (no provenance)", T._parse, bad, error=ValueError)
    bad = copy.deepcopy(BASE)
    bad["materials"]["A"]["co2_per_kg"] = F(10.0, 12.0, 15.0)
    expect_error("value outside [low, high]", T._parse, bad, error=ValueError)
    bad = copy.deepcopy(BASE)
    bad["objectives"] = ["mass_kg", "cost"]
    expect_error("cost objective without prices", T._parse, bad, error=ValueError)


def test_study_file_roundtrip(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(BASE), encoding="utf-8")
    out = T.run(T.load_study(p), samples=50)
    check_true("JSON-serialisable result", json.loads(json.dumps(out))["study"] == "hand")
    check_true("weak inputs listed (all tagged Y here)", "lifecycle.flights" in out["weak_inputs"])


def test_grouped_factors_move_together():
    raw = copy.deepcopy(BASE)
    raw["materials"]["C"] = {"E": 70e9, "rho": 1400.0, "co2_per_kg": F(100.0, 50.0, 150.0)}
    raw["materials"]["B"]["co2_per_kg"]["group"] = "same_route"
    raw["materials"]["C"]["co2_per_kg"]["group"] = "same_route"
    raw["lifecycle"]["fuel_per_kg_per_flight"] = F(0.1)
    mc = T.monte_carlo(T._parse(raw), samples=300, seed=5)
    check_true("identical grouped options tie in every sample → C (listed after B) never wins",
               mc["p_best"]["C / mill"] == 0.0 and 0 < mc["p_best"]["B / mill"] < 1, mc["p_best"])
    q = mc["quantiles"]
    check("grouped draws give identical quantiles", q["B / mill"]["co2_total_kg"]["p95"],
          q["C / mill"]["co2_total_kg"]["p95"], rtol=1e-12)


def test_cost_by_route_and_penalty():
    raw = copy.deepcopy(BASE)
    raw["materials"]["A"]["cost_by_route"] = {"mill": {"price_per_kg": F(10.0), "route_cost_per_kg": F(100.0)}}
    raw["materials"]["B"]["cost_by_route"] = {"mill": {"price_per_kg": F(200.0), "route_cost_per_kg": F(500.0)}}
    raw["objectives"] = ["mass_kg", "co2_total_kg", "cost"]
    raw["exchange"] = {"cost": 1.0, "mass_kg": 500.0}
    r = {x.material: x for x in T.evaluate(T._parse(raw))}
    check("A cost = 2 kg x 5 x 10 + 2 x 100", r["A"].cost, 300.0, rtol=1e-12)
    check("B cost = 1 x 5 x 200 + 1 x 500", r["B"].cost, 1500.0, rtol=1e-12)
    z = T.penalty(list(r.values()), raw["exchange"])
    check("Z(A) = 300 + 500 x 2", z["A / mill"], 1300.0, rtol=1e-12)
    check("Z(B) = 1500 + 500 x 1", z["B / mill"], 2000.0, rtol=1e-12)
    bad = copy.deepcopy(raw)
    del bad["materials"]["B"]["cost_by_route"]
    expect_error("cost objective needs a cost for every option", T._parse, bad, error=ValueError)


def test_end_of_life_and_screening():
    raw = copy.deepcopy(BASE)
    raw["materials"]["A"]["eol_credit_per_kg"] = F(8.0)
    raw["materials"]["B"].update({"max_service_C": 80.0, "flags": ["fst_cabin"]})
    s = T._parse(raw)
    r = {x.material: x for x in T.evaluate(s)}
    check("A end-of-life potential = −2 kg · 8", r["A"].co2_eol_potential_kg, -16.0, rtol=1e-12)
    check("EoL kept out of the life total", r["A"].co2_total_kg, 702.0, rtol=1e-12)
    check("… and counted in the EoL objective", r["A"].co2_total_with_eol_kg, 686.0, rtol=1e-12)
    check("no credit given → zero potential", r["B"].co2_eol_potential_kg, 0.0, atol=0.0)
    raw["constraints"] = {"service_temperature_C": 120.0}
    s = T._parse(raw)
    check_true("B screened out above its 80 C ceiling", [o[0] for o in s.options] == ["A"]
               and "80" in s.screened[0]["reason"])
    raw["constraints"] = {"require": ["fst_cabin"]}
    check_true("A lacks the cabin flammability flag", [o[0] for o in T._parse(raw).options] == ["B"])
    raw["constraints"] = {"require": ["fst_cabin"], "service_temperature_C": 120.0}
    expect_error("all options screened", T._parse, raw, error=ValueError)


def test_material_and_process_split():
    r = {x.material: x for x in T.evaluate(T._parse(BASE))}
    check("A material share = 2 kg x btf 5 x 10", r["A"].co2_material_kg, 100.0, rtol=1e-12)
    check("A process share = 2 x 5 x 2 MJ x 0.1", r["A"].as_dict()["co2_process_kg"], 2.0, rtol=1e-12)
