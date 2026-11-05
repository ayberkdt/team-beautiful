"""aerokit.bracket.cadout / tetfem: exact CAD export, STEP round trip, conforming 10-node tets (needs gmsh).

The checks run in a fresh Python subprocess: inside the full suite (after tests/comms) gmsh's 3-D mesher was seen
to hang on 2026-11-04 (cause not found; it passes alone and in the production CLI, which is a fresh process).
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

PYLIB = "D:/tmp_ideathon/pylib"
if __name__ != "__main__":
    if os.path.isdir(PYLIB) and PYLIB not in sys.path:
        sys.path.append(PYLIB)
    pytest.importorskip("gmsh")


def test_gmsh_checks_in_subprocess(tmp_path):
    env = dict(os.environ)
    root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = os.pathsep.join([str(root / "src"), PYLIB, env.get("PYTHONPATH", "")])
    r = subprocess.run([sys.executable, __file__, str(tmp_path)], capture_output=True, text=True, timeout=600,
                       env=env, cwd=str(root))
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-3000:]
    assert "ALL OK" in r.stdout


from aerokit.bracket import cadout, geometry, tetfem  # noqa: E402
from aerokit.bracket import voxfem as vf  # noqa: E402


def box_with_hole():
    return geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [40, 20, 10]},
        {"op": "cut", "type": "cylinder", "p0": [20, 10, -1], "p1": [20, 10, 11], "radius": 5}]})


def check_drawing_to_step_exact_volume_and_roundtrip(tmp_path):
    r = cadout.drawing_to_cad(box_with_hole(), tmp_path / "b.step", tmp_path / "b.stl")
    assert r["volume_mm3"] == pytest.approx(40 * 20 * 10 - np.pi * 25 * 10, rel=1e-6)
    V, F = cadout.read_any(tmp_path / "b.step")
    vs = geometry.voxelize_surface(V, F, 1e-3)
    assert abs(vs.volume_frac * 1e9 / r["volume_mm3"] - 1) < 0.02


def check_t10_cantilever(tmp_path):
    d = geometry.load_drawing({"units": "mm", "solids": [{"op": "add", "type": "box", "min": [0, 0, 0],
                                                           "max": [100, 10, 10]}]})
    cadout.drawing_to_cad(d, tmp_path / "beam.step")
    m = tetfem.mesh_cad(tmp_path / "beam.step", 5.0)
    assert m.volume * 1e9 == pytest.approx(1e4, rel=1e-9)
    E, nu, P = 200e9, 0.3, 1000.0
    K, _ = tetfem._stiffness(m, E, nu)
    a = tetfem._face_weights(m)
    fix = np.flatnonzero(np.isclose(m.X[:, 0], 0))
    tip = np.flatnonzero(np.isclose(m.X[:, 0], 0.1))
    F = np.zeros(m.ndof)
    F[3 * tip + 2] = -P * a[tip] / a[tip].sum()
    U, _ = vf.solve(K, F, (3 * fix[:, None] + np.arange(3)).ravel(), m.X, method="direct")
    I = 0.01 ** 4 / 12
    timo = P * 0.1 ** 3 / (3 * E * I) + P * 0.1 / (5 / 6 * E / 2.6 * 1e-4)
    ratio = -(U[3 * tip + 2] * a[tip]).sum() / a[tip].sum() / timo
    assert 0.97 < ratio < 1.01          # [K] 0.9905 at 5 mm


def check_t10_setup_balance(tmp_path):
    d = geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [60, 20, 6]},
        {"op": "cut", "type": "cylinder", "p0": [8, 10, -1], "p1": [8, 10, 7], "radius": 3},
        {"op": "cut", "type": "cylinder", "p0": [52, 10, -1], "p1": [52, 10, 7], "radius": 4}]})
    cadout.drawing_to_cad(d, tmp_path / "p.step")
    m = tetfem.mesh_cad(tmp_path / "p.step", 3.0)
    setup = {"holes": [
        {"id": "H1", "axis": "z", "center_mm": [8, 10, 3], "diameter_mm": 6, "segments_mm": [[0, 6]], "role": "support"},
        {"id": "H2", "axis": "z", "center_mm": [52, 10, 3], "diameter_mm": 8, "segments_mm": [[0, 6]], "role": "load"}],
        "supports": [{"hole": "H1", "type": "fixed_bore"}],
        "load_cases": [{"name": "LC1", "loads": [{"hole": "H2", "type": "bearing", "force_N": [500.0, 0, 0]}]},
                       {"name": "LC2", "loads": [{"hole": "H2", "type": "moment", "moment_Nm": [0, 0, 2.0]}]}],
        "exclusion_mm": 2.0}
    r = tetfem.static_t10(m, setup, 200e9)
    assert len(r["cases"]) == 2
    c1, c2 = r["cases"]
    assert c1["compliance_J"] > 0 and c2["compliance_J"] > 0
    assert c1["vm_outside_Pa"] <= c1["vm_max_Pa"]
    # bar in tension between the holes: mean stress order P / (b t) = 500 / (20 mm x 6 mm) = 4.2 MPa
    assert 2e6 < c1["vm_outside_Pa"] < 60e6


def _multi_body_step(path):
    """Plate with a hole (1), a bolt pushed through the plate (2, overlaps 1), a separate block (3)."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
        p = gmsh.model.occ.addBox(0, 0, 0, 60, 30, 8)
        gmsh.model.occ.cut([(3, p)], [(3, gmsh.model.occ.addCylinder(15, 15, -1, 0, 0, 10, 4))])
        gmsh.model.occ.addCylinder(45, 15, -4, 0, 0, 16, 3)
        gmsh.model.occ.addBox(80, 0, 0, 10, 10, 10)
        gmsh.model.occ.synchronize()
        gmsh.write(str(path))
    finally:
        gmsh.finalize()


def check_multi_body_step(tmp_path):
    from aerokit.bracket import pipeline
    src = tmp_path / "multi.step"
    _multi_body_step(src)
    plate, bolt, overlap = 60 * 30 * 8 - np.pi * 16 * 8, np.pi * 9 * 16, np.pi * 9 * 8
    t = cadout.step_bodies(src)
    assert [round(b["volume_mm3"], 3) for b in t] == [round(plate, 3), round(bolt, 3), 1000.0]
    r = cadout.normalise_step(src, tmp_path / "plate_bolt.step", [1, 2])
    assert r["fused_volume_mm3"] == pytest.approx(plate + bolt - overlap, rel=1e-9)       # union, bolt counted once
    assert r["overlap_mm3"] == pytest.approx(overlap, rel=1e-9) and r["solids_after_fuse"] == 1
    assert cadout.cad_volume(tmp_path / "plate_bolt.step") == pytest.approx(plate + bolt - overlap, rel=1e-9)
    g = pipeline.load_geometry(src, bodies="largest", work_dir=tmp_path / "w")
    assert g.bodies["selected"] == [1]
    vs = g.voxelize(1e-3)
    assert vs.volume_frac * 1e9 == pytest.approx(plate, rel=0.02)
    with pytest.raises(ValueError, match="separate solids remain"):              # 3 is not connected: never guess
        pipeline.load_geometry(src, work_dir=tmp_path / "w2")
    m = tetfem.mesh_cad(tmp_path / "plate_bolt.step", 3.0)                         # the fused solid meshes as one
    assert m.volume * 1e9 == pytest.approx(plate + bolt - overlap, rel=1e-3)


def check_step_small_bores_not_lost(tmp_path):
    """Bores of Ø4–16 mm in a STEP at 2 mm voxels: the half-voxel scan must still find all five (4 Nov: Ø4 and Ø6
    were lost at 2 mm before the scan)."""
    from aerokit.bracket import pipeline
    d = geometry.load_drawing({"units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [120, 50, 10]},
        *[{"op": "cut", "type": "cylinder", "p0": [x, 25, -1], "p1": [x, 25, 11], "radius": r}
          for x, r in ((12, 2.0), (30, 3.0), (52, 5.0), (80, 8.0))],
        {"op": "cut", "type": "cylinder", "p0": [105, -1, 5], "p1": [105, 51, 5], "radius": 3.0}]})
    cadout.drawing_to_cad(d, tmp_path / "holes.step")
    g = pipeline.load_geometry(tmp_path / "holes.step")
    opt = pipeline.Options(voxel_mm=2.0, volfracs=(), convergence=False, tet_check=False, log=False)
    st = pipeline.prepare(g, tmp_path / "case", opt)
    dia = sorted(h["diameter_mm"] for h in st.setup["holes"])
    assert len(dia) == 5
    assert np.allclose(dia, [4, 6, 6, 10, 16], rtol=0.08)


if __name__ == "__main__":
    from aerokit.bracket import cadout, geometry, tetfem  # noqa: F401
    from aerokit.bracket import voxfem as vf  # noqa: F401
    out = Path(sys.argv[1])
    for name, fn in list(globals().items()):
        if name.startswith("check_"):
            d = out / name
            d.mkdir(parents=True, exist_ok=True)
            fn(d)
            print(name, "ok", flush=True)
    print("ALL OK")
