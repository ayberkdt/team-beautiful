"""5 Nov 2026 fixes: yield-based FoS (mentor), displacement criterion, frozen-region options, finalize SDF ops."""
import numpy as np

from aerokit.bracket import pipeline
from aerokit.bracket.finalize import _sdf, closing, opening


def test_strength_util_default_unchanged_and_yield_basis():
    opt = pipeline.Options()
    s, fty, ftu = 200e6, 500e6, 600e6
    assert pipeline.strength_util({}, opt, s, fty, ftu) == max(s / fty, 1.5 * s / ftu)
    su = {"design_criteria": {"strength_basis": "yield", "factor_of_safety": 1.5}}
    assert abs(pipeline.strength_util(su, opt, s, fty, ftu) - 1.5 * s / fty) < 1e-12
    assert pipeline.strength_util(su, opt, s, fty, ftu) > pipeline.strength_util({}, opt, s, fty, ftu)


def test_sdf_sign_and_half_voxel_boundary():
    m = np.zeros((20, 20, 20), bool)
    m[5:15, 5:15, 5:15] = True
    phi = _sdf(m, 2.0)
    assert phi[10, 10, 10] < 0 < phi[0, 0, 0]
    assert abs(phi[5, 10, 10] + 1.0) < 1e-6 and abs(phi[4, 10, 10] - 1.0) < 1e-6   # boundary half-way, h = 2


def test_opening_removes_thin_plate_closing_fills_slot():
    h = 1.0
    m = np.zeros((40, 40, 40), bool)
    m[5:35, 5:35, 5:35] = True
    m[18:20, :, :] = False                                   # 2-voxel slot through the cube
    thin = np.zeros_like(m)
    thin[10:30, 10:30, 19:21] = True                         # 2-voxel plate
    assert (closing(_sdf(m, h), 2.0, h) < 0)[19, 20, 20]     # slot narrower than 2 r is filled
    assert not (opening(_sdf(thin, h), 2.0, h) < 0).any()    # plate thinner than 2 r disappears


def test_load_ties_rule():
    from aerokit.bracket import features
    setup = {"holes": [
        {"id": "H1", "axis": "y", "center_mm": [500, 65, 260], "diameter_mm": 60, "segments_mm": [[30, 100]], "role": "load"},
        {"id": "H2", "axis": "y", "center_mm": [500, 335.56, 260], "diameter_mm": 60, "segments_mm": [[300, 371.12]], "role": "load"},
        {"id": "H3", "axis": "z", "center_mm": [245, 95, 65], "diameter_mm": 60, "segments_mm": [[30, 100]], "role": "support"}],
        "non_design": {"connect_loads": True, "tie_section_mm": 15.6}}
    (t,) = features.load_ties(setup, 7.8e-3)
    assert t["min"][1] == 30 and t["max"][1] == 371.12          # spans both lug segments along the pin axis
    assert abs(t["max"][2] - 100) < 1e-9 and abs(t["min"][2] - 84.4) < 1e-9   # top of the support region
    assert t["min"][0] < 500 < t["max"][0]
    assert features.load_ties({**setup, "non_design": {}}, 7.8e-3) == []


def test_detect_symmetry_official_and_negative():
    import copy
    import json
    from pathlib import Path
    from aerokit.bracket import features
    p = Path(__file__).resolve().parents[1] / "01_Ansys/official_2026-11-05/setup/setup_official_v3_skeleton.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    d = features.detect_symmetry(s)
    assert set(d) == {"x", "y"} and abs(d["x"] - 500) < 0.5
    s2 = copy.deepcopy(s)
    s2["load_cases"] = [c for c in s2["load_cases"] if not c["name"].startswith("LC1b")]
    assert set(features.detect_symmetry(s2)) == {"x"}
    s3 = copy.deepcopy(s)
    s3["holes"][2]["center_mm"][0] += 20
    assert features.detect_symmetry(s3) == {}
