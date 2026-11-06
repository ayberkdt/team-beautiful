"""aerokit.bracket.geometry / features: drawing voxelisation, surface voxelisation, holes, set-up application."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from aerokit.bracket import features, geometry, pipeline
from aerokit.bracket import voxfem as vf

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "01_Ansys" / "inputs"


def plate_with_holes():
    return geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [80, 40, 6]},
        {"op": "add", "type": "prism", "axis": "y", "polygon": [[30, 6], [50, 6], [50, 30]] +
         geometry.arc((40, 30), 10, 0, 180, 12), "range": [15, 25]},
        {"op": "cut", "type": "cylinder", "p0": [10, 10, -1], "p1": [10, 10, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [70, 10, -1], "p1": [70, 10, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [10, 30, -1], "p1": [10, 30, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [70, 30, -1], "p1": [70, 30, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [40, 10, 30], "p1": [40, 30, 30], "radius": 5},
    ]})


def test_drawing_volume_close_to_analytic():
    d = geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [40, 20, 10]},
        {"op": "cut", "type": "cylinder", "p0": [20, 10, -1], "p1": [20, 10, 11], "radius": 5}]})
    vm = geometry.voxelize_drawing(d, 1e-3)
    exact = 40 * 20 * 10 - math.pi * 25 * 10
    assert abs(vm.volume * 1e9 / exact - 1) < 0.02


def test_surface_voxelisation_matches_drawing():
    vm = geometry.voxelize_drawing(plate_with_holes(), 1e-3)
    V, F = geometry.drawing_to_surface(vm)
    vs = geometry.voxelize_surface(V, F, 1e-3)
    assert abs(vs.volume / vm.volume - 1) < 1e-9


def test_detect_and_classify_holes():
    vm = geometry.voxelize_drawing(plate_with_holes(), 1e-3)
    holes = features.detect_holes(vm)
    roles = features.classify(holes)
    by_axis = sorted((hl.axis, round(hl.radius * 1e3)) for hl in holes)
    assert by_axis == [(1, 5), (2, 4), (2, 4), (2, 4), (2, 4)]
    assert sum(r == "support" for r in roles.values()) == 4
    lug = next(hl for hl in holes if roles[hl.id] == "load")
    assert lug.axis == 1 and np.allclose(lug.center[[0, 2]], [40e-3, 30e-3], atol=1e-3)


def test_holes_from_drawing_exact_and_clevis_merge():
    d = geometry.load_drawing(INPUTS / "ge_bracket.json")
    holes = pipeline.holes_from_drawing(d)
    pin = [hl for hl in holes if hl.axis == 0]
    assert len(pin) == 1 and len(pin[0].segments) == 2
    assert abs(pin[0].radius * 2e3 - 19.05) < 1e-9
    assert sum(hl.axis == 2 for hl in holes) == 4


def test_classify_single_axis_by_diameter():
    mk = lambda i, r, c: features.Hole(f"H{i}", 2, np.array(c, float), r, [(0, 1)])  # noqa: E731
    hs = [mk(1, 4, [0, 0, 0]), mk(2, 4, [10, 0, 0]), mk(3, 4, [0, 10, 0]), mk(4, 7, [5, 5, 0])]
    assert features.classify(hs) == {"H1": "support", "H2": "support", "H3": "support", "H4": "load"}


def test_apply_setup_resultants_and_moment():
    vm = geometry.voxelize_drawing(plate_with_holes(), 2e-3)
    s = features.propose_setup(vm, features.detect_holes(vm), magnitude_N=1000.0)
    lug = next(h["id"] for h in s["holes"] if h["role"] == "load")
    s["load_cases"].append({"name": "LC4 moment", "loads": [{"hole": lug, "type": "moment", "moment_Nm": [0, 5.0, 0]}]})
    s["load_cases"].append({"name": "LC5 force", "loads": [{"hole": lug, "type": "force", "force_N": [0, 0, -300.0]}]})
    m = vf.VoxelMesh(vm.solid, vm.h, vm.origin)
    ap = features.apply_setup(m, s)
    sums = ap.F.reshape(-1, 3, ap.F.shape[1]).sum(0).T
    assert np.allclose(sums[0], [1000, 0, 0], atol=1e-6)
    assert np.allclose(sums[2], [0, 0, 1000], atol=1e-6)
    assert np.allclose(sums[3], 0, atol=1e-9)
    assert np.allclose(sums[4], [0, 0, -300], atol=1e-9)
    c = next(features.Hole.from_json(h) for h in s["holes"] if h["id"] == lug).center
    f = ap.F[:, 3].reshape(-1, 3)
    assert np.allclose(np.cross(m.X - c, f).sum(0), [0, 5.0, 0], atol=1e-9)
    res = vf.static(m, 200e9, 0.3, ap.F[:, :1], ap.fixed, method="direct")[0]
    assert np.allclose(res.reaction, [-1000, 0, 0], atol=1e-6)


def test_bearing_load_only_on_loaded_half():
    vm = geometry.voxelize_drawing(plate_with_holes(), 1e-3)
    s = features.propose_setup(vm, features.detect_holes(vm))
    m = vf.VoxelMesh(vm.solid, vm.h, vm.origin)
    ap = features.apply_setup(m, s)
    lug = next(features.Hole.from_json(h) for h in s["holes"] if h["role"] == "load")
    loaded = np.flatnonzero(np.abs(ap.F[:, 2].reshape(-1, 3)).sum(1) > 0)        # LC3 +z
    assert loaded.size and np.all(m.X[loaded, 2] >= lug.center[2] - 1e-9)


def test_non_design_ring_and_setup_roundtrip(tmp_path):
    vm = geometry.voxelize_drawing(plate_with_holes(), 1e-3)
    s = features.propose_setup(vm, features.detect_holes(vm))
    s2 = features.load_setup(features.save_setup(s, tmp_path / "s.json"))
    assert json.dumps(s, sort_keys=True, default=float) == json.dumps(s2, sort_keys=True, default=float)
    keep = features.non_design_mask(vf.VoxelMesh(vm.solid, vm.h, vm.origin), s2)
    assert 0.02 < keep.mean() < 0.5


def test_setup_without_supports_rejected():
    vm = geometry.voxelize_drawing(plate_with_holes(), 1e-3)
    s = features.propose_setup(vm, features.detect_holes(vm))
    s["supports"] = []
    with pytest.raises(ValueError, match="no supports"):
        features.apply_setup(vf.VoxelMesh(vm.solid, vm.h, vm.origin), s)


def test_pca_alignment_recovers_holes_of_a_rotated_part(tmp_path):
    from aerokit.optimization import extract
    vm0 = geometry.voxelize_drawing(plate_with_holes(), 1e-3)
    V, F = geometry.drawing_to_surface(vm0)
    R = pipeline.rotation_matrix(25, -40, 60)
    extract.write_stl(tmp_path / "rot.stl", ((V - V.mean(0)) @ R.T) * 1e3, F)
    g = pipeline.load_geometry(tmp_path / "rot.stl", unit="mm", align="pca")
    assert g.frame and abs(abs(np.linalg.det(np.asarray(g.frame["rotation_matrix"]))) - 1) < 1e-9
    vm = g.voxelize(1e-3)
    holes = features.detect_holes(vm)
    roles = features.classify(holes)
    assert sorted(roles.values()) == ["load", "support", "support", "support", "support"]
    with pytest.raises(ValueError):
        pipeline.load_geometry(INPUTS / "sketch_bracket.json", align="pca")


def test_member_thickness_of_plates():
    for n in (3, 4, 5, 6, 8):
        s = np.zeros((20, 20, 20), bool)
        s[:, :, 4:4 + n] = True
        t = geometry.member_thickness(s, 1e-3)
        assert abs(t["min_vox"] - n) <= 0.5 + 1e-9
