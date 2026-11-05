"""aerokit.bracket.pipeline.rank_materials / decide: stress factors move the choice to a heavier layout; failing
fallback is flagged."""
from types import SimpleNamespace


from aerokit.bracket import matdata, pipeline


def fake_study(stress_25=450e6, stress_35=270e6, stress_init=130e6):
    designs = [
        {"label": "initial", "volfrac": 1.0, "volume_m3": 1.0e-4, "stress_unitE": {"LC": stress_init},
         "disp_unitE": 1.0, "compliance_unitE": 1.0, "vm_max_unitE": stress_init},
        {"label": "topo 35 %", "volfrac": 0.35, "volume_m3": 0.35e-4, "stress_unitE": {"LC": stress_35},
         "disp_unitE": 1.0, "compliance_unitE": 1.0, "vm_max_unitE": stress_35},
        {"label": "topo 25 %", "volfrac": 0.25, "volume_m3": 0.25e-4, "stress_unitE": {"LC": stress_25},
         "disp_unitE": 1.0, "compliance_unitE": 1.0, "vm_max_unitE": stress_25},
    ]
    return SimpleNamespace(T=300.0, designs=designs, materials=[], choice={}, eco={},
                           baseline={"mass_kg": 0.785, "material": "structural_steel"})


def test_knockdown_moves_choice_to_heavier_layout():
    st = fake_study()
    opt = pipeline.Options(log=False)
    cands = [matdata.get("ti64_lpbf")]
    pipeline.rank_materials(st, opt, cands)
    pipeline.decide(st, opt)
    assert st.choice["design"] == "topo 25 %" and st.choice["passes"]
    pipeline.rank_materials(st, opt, cands, {"topo 25 %": 1.336})      # T10 measured 34 % more stress
    pipeline.decide(st, opt)
    assert st.choice["design"] == "topo 35 %"
    row = next(r for r in st.materials[0]["designs"] if r["design"] == "topo 35 %")
    assert row["stress_factor"] == 1.0                                  # unmeasured: verified when chosen


def test_nothing_passes_gives_flagged_fallback():
    st = fake_study(stress_25=5e9, stress_35=4e9, stress_init=3e9)
    opt = pipeline.Options(log=False)
    pipeline.rank_materials(st, opt, [matdata.get("ti64_lpbf"), matdata.get("in718_lpbf")])
    pipeline.decide(st, opt)
    assert st.choice["passes"] is False
    assert st.choice["material"] == "in718_lpbf" and st.choice["design"] == "initial"
    assert st.choice["material"] in st.eco["candidates"]
