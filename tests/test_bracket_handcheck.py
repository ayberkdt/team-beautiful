"""aerokit.bracket.handcheck: FEA bolt reactions vs the classical rigid-plate bolt-group split."""
import numpy as np
import pytest

from aerokit.bracket import features, geometry, handcheck
from aerokit.bracket import voxfem as vf


@pytest.fixture(scope="module")
def plate():
    d = geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [80, 40, 6]},
        {"op": "add", "type": "prism", "axis": "y", "polygon": [[30, 6], [50, 6], [50, 30]] +
         geometry.arc((40, 30), 10, 0, 180, 12), "range": [15, 25]},
        *[{"op": "cut", "type": "cylinder", "p0": [x, y, -1], "p1": [x, y, 7], "radius": 4}
          for x, y in ((10, 10), (70, 10), (10, 30), (70, 30))],
        {"op": "cut", "type": "cylinder", "p0": [40, 10, 30], "p1": [40, 30, 30], "radius": 5},
    ]})
    vm = geometry.voxelize_drawing(d, 1e-3)
    s = features.propose_setup(vm, features.detect_holes(vm), magnitude_N=1000.0)
    lug = next(h["id"] for h in s["holes"] if h["role"] == "load")
    s["load_cases"].append({"name": "LC4 torsion", "loads": [{"hole": lug, "type": "moment", "moment_Nm": [0, 0, 10.0]}]})
    m = vf.VoxelMesh(vm.solid, vm.h, vm.origin)
    fea = handcheck.bolt_reactions(m, s, 200e9)
    cl = handcheck.classical_bolt_loads(s, fea["_applied"], fea["_mesh_X"])
    return s, m, fea, cl


def test_fea_bolt_reactions_close_equilibrium_with_clamp_moments(plate):
    s, m, fea, _ = plate
    ap = fea["_applied"]
    holes = {d["id"]: features.Hole.from_json(d) for d in s["holes"]}
    for k, case in enumerate(fea["cases"]):
        f = ap.F[:, k].reshape(-1, 3)
        R = np.array([fea["reaction_N"][case][h] for h in fea["holes"]])
        assert np.allclose(R.sum(0), -f.sum(0), atol=1e-6 * 1000)
        Mr = sum(np.cross(holes[h].center, fea["reaction_N"][case][h]) + np.asarray(fea["clamp_moment_Nm"][case][h])
                 for h in fea["holes"])
        assert np.allclose(Mr, -np.cross(m.X, f).sum(0), atol=1e-6 * 30)


def test_classical_split_matches_hand_numbers(plate):
    _, _, fea, cl = plate
    assert cl is not None and cl["axis"] == "z"
    rows = {(r["case"], r["hole"]): r for r in handcheck.compare_bolts(fea, cl)}
    # LC1: 1000 N in x at the lug pin (z = 30 mm), bolt mid-plane z = 3 mm, bolts at x = ±30 mm:
    # shear 250 N per bolt, axial ± 1000·0.027/(4·0.030) = 225 N
    lc1 = [r for (c, _), r in rows.items() if c.startswith("LC1")]
    assert np.allclose([r["classical_shear_N"] for r in lc1], 250.0)
    assert np.allclose(sorted(abs(r["classical_axial_N"]) for r in lc1), 225.0)
    # LC2: 1000 N in y, bolts at y = ±10 mm: axial ± 1000·0.027/(4·0.010) = 675 N
    assert np.allclose([abs(r["classical_axial_N"]) for (c, _), r in rows.items() if c.startswith("LC2")], 675.0)
    # LC4: 10 N m about z, r = √(30² + 10²) mm, Σr² = 4 r² → 10 r / Σr² per bolt
    r0 = np.hypot(0.030, 0.010)
    assert np.allclose([r["classical_shear_N"] for (c, _), r in rows.items() if c.startswith("LC4")],
                       10.0 * r0 / (4 * r0 ** 2))


def test_fea_and_classical_agree_where_the_plate_is_stiff(plate):
    """In-plane shear and torsion go through the stiff plate plane (rigid-plate method within ~10 %); the axial
    split under out-of-plane moment does not — there the clamped bores carry clamp moments (plate bending)."""
    _, _, fea, cl = plate
    rows = handcheck.compare_bolts(fea, cl)
    for r in rows:
        if r["case"].startswith(("LC1", "LC4")):
            assert r["fea_shear_N"] == pytest.approx(r["classical_shear_N"], rel=0.10)
        if r["case"].startswith("LC3"):                      # pure pull-off: symmetric, 250 N each
            assert r["fea_axial_N"] == pytest.approx(r["classical_axial_N"], rel=1e-3)
    assert max(r["fea_clamp_moment_Nm"] for r in rows if r["case"].startswith("LC1")) > 0.5


def test_bolt_seat_reactions_are_collected_from_the_seat(plate):
    """bolt_seat fixes a face annulus, not the bore: the reactions must still add up to the applied load."""
    s, m, _, _ = plate
    s2 = {**s, "supports": [{**sp, "type": "bolt_seat"} for sp in s["supports"]]}
    fea = handcheck.bolt_reactions(m, s2, 200e9)
    f = fea["_applied"].F.reshape(-1, 3, len(fea["cases"])).sum(0).T
    for k, case in enumerate(fea["cases"]):
        R = np.array([fea["reaction_N"][case][h] for h in fea["holes"]])
        assert np.allclose(R.sum(0), -f[k], atol=1e-3)
        assert np.all(np.linalg.norm(R, axis=1) > 0.05 * np.linalg.norm(f[k]) / len(R))   # every bolt carries load


def test_mixed_axes_return_none(plate):
    s, _, fea, _ = plate
    s2 = {**s, "supports": s["supports"] + [{"hole": next(h["id"] for h in s["holes"] if h["role"] == "load")}]}
    assert handcheck.classical_bolt_loads(s2, fea["_applied"], fea["_mesh_X"]) is None
    assert handcheck.compare_bolts(fea, None) == []
