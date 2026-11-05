"""scripts/bracket_sketch2.py: the 5 Nov sketch geometry (curved arches, > 5 holes, a hole through a curved crown) is
accepted by the drawing voxeliser and the voxel hole detection used on the day (geometry only, no gmsh, no FEA)."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from aerokit.bracket import features, geometry

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bracket_sketch2", ROOT / "scripts" / "bracket_sketch2.py")
s2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s2)


def holes(variant, **over):
    p = {**s2.PARAMS, **over}
    vm = geometry.voxelize_drawing(geometry.load_drawing(s2.drawing(p, variant)), 1e-3)
    return vm, features.detect_holes(vm), p


@pytest.mark.parametrize("variant,n_y", [("loop", 2), ("lug", 2)])
def test_bolts_small_hole_and_arch_openings_found(variant, n_y):
    vm, hs, p = holes(variant)
    z = [h for h in hs if h.axis == 2]
    y = [h for h in hs if h.axis == 1]
    assert len(z) == 7 and len(y) == n_y                     # 6 bolts + small hole; one opening per arch
    assert np.allclose(sorted(2e3 * h.radius for h in z)[1:], p["bolt_d"], rtol=0.06)
    roles = features.classify(hs)
    assert {roles[h.id] for h in y} == {"load"}
    assert sum(r == "support" for r in roles.values()) >= 6


def test_lug_pin_bores_exact_and_loop_opening_is_an_equivalent_circle():
    _, hs, p = holes("lug")
    d = sorted(2e3 * h.radius for h in hs if h.axis == 1)
    assert np.allclose(d, [2 * p["arch_B_r"], 2 * p["arch_A_r"]], rtol=0.04)
    _, hs, p = holes("loop")
    a = max((h for h in hs if h.axis == 1), key=lambda h: h.radius)
    # half-disc opening r = 14 mm on the plate: fitted as a circle of equal area (Ø ≈ 2r/√2) above the plate
    assert 2e3 * a.radius == pytest.approx(2 * p["arch_A_r"] / np.sqrt(2), rel=0.08)
    assert a.center[2] * 1e3 > p["t"]


def test_hole_through_curved_crown_detected():
    _, hs, p = holes("loop", crown_A_d=6.0)
    crown = [h for h in hs if h.axis == 2 and abs(h.center[0] * 1e3 - p["arch_A_x"]) < 1.5
             and abs(h.center[1] * 1e3 - p["arch_A_y"]) < 1.5]
    assert len(crown) == 1 and 2e3 * crown[0].radius == pytest.approx(6.0, rel=0.15)


def test_parameters_change_the_drawing():
    d = s2.drawing({**s2.PARAMS, "L": 200.0}, "loop_nohole")
    assert d["parameters"]["L"] == 200.0 and not any(
        c["type"] == "cylinder" and abs(c["radius"] - s2.PARAMS["small_d"] / 2) < 1e-9 for c in d["solids"])
