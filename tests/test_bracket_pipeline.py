"""End-to-end smoke test of aerokit.bracket.pipeline / report / handoff on a tiny drawing (no gmsh, no figures)."""
import json

import numpy as np
import pytest

from aerokit.bracket import crosscheck, handoff, pipeline, report


def tiny_drawing():
    return {"name": "tiny bracket", "units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [60, 24, 6]},
        {"op": "add", "type": "box", "min": [24, 6, 6], "max": [36, 18, 30]},
        {"op": "cut", "type": "cylinder", "p0": [8, 12, -1], "p1": [8, 12, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [52, 12, -1], "p1": [52, 12, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [23, 12, 22], "p1": [37, 12, 22], "radius": 4}]}


@pytest.fixture(scope="module")
def study(tmp_path_factory):
    out = tmp_path_factory.mktemp("bracket")
    src = out / "tiny.json"
    src.write_text(json.dumps(tiny_drawing()), encoding="utf-8")
    g = pipeline.load_geometry(src)
    opt = pipeline.Options(voxel_mm=2.0, volfracs=(0.5,), max_iter=12, convergence=False, tet_check=False,
                           magnitude_N=500.0, log=False)
    st = pipeline.run_design(g, out / "case", opt)
    return st, g, opt, out


def test_holes_roles_and_setup_written(study):
    st, *_ = study
    roles = sorted(h["role"] for h in st.setup["holes"])
    assert roles == ["load", "support", "support"]
    assert (st.out / "setup.json").exists()
    assert st.setup["exclusion_mm"] == pytest.approx(6.0)


def test_baseline_balanced_and_mass(study):
    st, *_ = study
    for c in st.baseline["at_T"]["cases"]:
        assert np.allclose(np.asarray(c["applied_N"]) + np.asarray(c["reaction_N"]), 0, atol=1e-6)
    exact = 60 * 24 * 6 + 12 * 12 * 24 - 2 * np.pi * 16 * 6 - np.pi * 16 * 12
    assert abs(st.baseline["volume_m3"] * 1e9 / exact - 1) < 0.05
    assert st.baseline["worst_T"]["max_disp_m"] > st.baseline["worst_20C"]["max_disp_m"]
    w = st.baseline["worst_T"]
    assert 0 < w["load_disp_m"] <= w["max_disp_m"] * (1 + 1e-9)


def test_designs_and_materials(study):
    st, *_ = study
    assert [d["label"] for d in st.designs] == ["initial", "topo 50 %"]
    assert 0.4 < st.designs[1]["volume_fraction_kept"] < 0.6
    keys = {m["key"] for m in st.materials}
    assert {"structural_steel", "ti64_lpbf", "in718_lpbf"} <= keys
    sc = next(m for m in st.materials if m["key"] == "scalmalloy")
    assert sc["best"] is None and not sc["temp_ok"]


def test_report_files_and_crosscheck_template(study):
    st, g, opt, out = study
    files = report.write_all(st, g, opt, figures=False)
    for f in ("report.md", "result.json", "eco_audit.md", "crosscheck_template.csv", "loads_film.json",
              "materials/materials_engineering_data.xml", "materials/card_structural_steel.md"):
        assert (st.out / f).exists(), f
    res = json.loads((st.out / "result.json").read_text(encoding="utf-8"))
    for r in res["ranking"]:
        for k in ("material", "route", "mass_kg", "co2_production_kg", "co2_use_kg"):
            assert k in r
    ours, ansys = crosscheck.read_template(st.out / "crosscheck_template.csv")
    assert ours["mass_kg"] == pytest.approx(st.baseline["mass_kg"], rel=1e-5)
    assert "cad" in files
    h = handoff.write(st, opt, out / "handoff", "test")
    for f in ("girdi.json", "result.json", "yukler.json", "yogunluk.json", "parca.stl", "README.md",
              "eco_audit.json", "materials"):
        assert f in h["files"]
    hres = json.loads((out / "handoff" / "result.json").read_text(encoding="utf-8"))
    assert hres["ranking"] == res["ranking"] and "materials" in hres["details"]      # film reads only the hand-off
    assert (out / "handoff" / "materials" / "card_structural_steel.md").exists()
    dens = json.loads((out / "handoff" / "yogunluk.json").read_text(encoding="utf-8"))
    assert np.asarray(dens["runs"][0]["density"]).shape == st.vm.shape


def test_evaluate_only_mode(tmp_path):
    src = tmp_path / "tiny.json"
    src.write_text(json.dumps(tiny_drawing()), encoding="utf-8")
    g = pipeline.load_geometry(src)
    opt = pipeline.Options(voxel_mm=2.0, volfracs=(), convergence=False, tet_check=False, magnitude_N=500.0,
                           log=False)
    st = pipeline.run_design(g, tmp_path / "case", opt)
    assert [d["label"] for d in st.designs] == ["initial"]
    assert st.choice and st.choice["design"] == "initial"
    assert "thermal" in st.baseline and st.baseline["thermal"]["E_alpha_dT_Pa"] > 0


def test_film_ranking_utilisation_matches_its_stress(study):
    """The film prints σ and U side by side: U must follow from the same σ (the hand-off once paired T10 σ with
    the voxel U)."""
    from aerokit.bracket import matdata
    st, _, opt, _ = study
    res = pipeline.film_result(st, opt)
    assert res["ranking"]
    names = {matdata.get(k).name: matdata.get(k) for k in matdata.names()}
    for r in res["ranking"]:
        m, s = names[r["material"]], r["sigma_ult_Pa"] / opt.limit_to_ultimate
        assert r["utilisation"] == pytest.approx(max(s / m.Fty_at(st.T), opt.limit_to_ultimate * s / m.Ftu_at(st.T)))
        assert "voxel_utilisation" in r


def test_verified_layout_stress_applies_to_every_material(study):
    """Stress is E-independent: once a layout is T10-verified, every material on it uses that stress (film chart)."""
    import copy
    st, _, opt, _ = study
    st2 = copy.copy(st)
    lay = st.choice["design"]
    st2.tet = {"chosen": {"worst": {"vm_outside_Pa": 1.0e6}}}
    mats = pipeline.verified_materials(st2, opt)
    rows = [r for x in mats for r in x["designs"] if r["design"] == lay]
    assert rows and all(r["vm_limit_Pa"] == 1.0e6 and r["stress_basis"] == "T10" for r in rows)
    assert all(r["stress_basis"] == "voxel" for x in mats for r in x["designs"] if r["design"] != lay)
    assert st.materials[0]["designs"][0].get("stress_basis") is None          # ranking itself untouched
    res = pipeline.film_result(st2, opt)
    same = [r for r in res["ranking"] if r["design"] == lay]
    assert all(r["sigma_ult_Pa"] == pytest.approx(opt.limit_to_ultimate * 1.0e6) for r in same)


def test_roles_source_auto_then_edited(tmp_path):
    src = tmp_path / "tiny.json"
    src.write_text(json.dumps(tiny_drawing()), encoding="utf-8")
    g = pipeline.load_geometry(src)
    opt = pipeline.Options(voxel_mm=2.0, volfracs=(), convergence=False, tet_check=False, log=False)
    st1 = pipeline.prepare(g, tmp_path / "c", opt)
    assert st1.setup["roles_source"] == "auto"
    st2 = pipeline.prepare(g, tmp_path / "c", opt)                     # re-read, untouched
    assert st2.setup["roles_source"] == "auto"
    s = json.loads((tmp_path / "c" / "setup.json").read_text(encoding="utf-8"))
    s["load_cases"][0]["loads"][0]["force_N"] = [0.0, 0.0, -123.0]       # a person edits a load
    (tmp_path / "c" / "setup.json").write_text(json.dumps(s), encoding="utf-8")
    assert pipeline.prepare(g, tmp_path / "c", opt).setup["roles_source"] == "edited"


def test_density_file_snapshots_on_the_chosen_run(study):
    st, *_ = study
    d = report._density_file(st)
    chosen = st.choice.get("design")
    for run in d["runs"]:
        assert "warm_start_from" in run
        if run["label"] == chosen:
            its = [s["iteration"] for s in run["snapshots"]]
            assert its and all(i % 5 == 0 for i in its[:-1]) and its[-1] == run["iterations"]
            assert np.asarray(run["snapshots"][-1]["density"]).shape == st.vm.shape
        else:
            assert "snapshots" not in run
    assert st.setup["roles_source"] == "auto"
