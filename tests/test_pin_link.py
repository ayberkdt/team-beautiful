"""Two-pin link topology problem (aerokit.optimization.topology.pin_link) and its task-card geometry."""
from pathlib import Path

import numpy as np

from aerokit.design import card as C
from aerokit.optimization import topology as tp
from aerokit.verification import check, check_true, expect_error

ROOT = Path(__file__).resolve().parents[1]


def test_pin_link_problem():
    pr = tp.pin_link(90, 30, 5.0, 3.0, cases=((1.0, 0.0), (-1.0, 0.0), (0.0, -0.3)), P=2.0)
    check("three load cases", pr.F.shape[1], 3)
    for k, (fx, fy) in enumerate(((1.0, 0.0), (-1.0, 0.0), (0.0, -0.3))):
        check(f"case {k}: x resultant = fx P", pr.F[0::2, k].sum(), 2.0 * fx, atol=1e-12)
        check(f"case {k}: y resultant = fy P", pr.F[1::2, k].sum(), 2.0 * fy, atol=1e-12)
    m = pr.grid.element_center()
    d_left = np.hypot(m[:, 0] - 15.0, m[:, 1] - 15.0)
    check_true("bore elements are passive voids", np.all(pr.passive[d_left < 5.0] == 1))
    check_true("ring elements are passive solid", np.all(pr.passive[(d_left >= 5.0) & (d_left < 8.0)] == 2))
    fx_nodes = pr.grid.X[np.unique(pr.fixed // 2)]
    check_true("fixed nodes all on the left bore", np.all(np.abs(np.hypot(*(fx_nodes - 15.0).T) - 5.0) <= 0.75))
    tension = np.flatnonzero(pr.F[0::2, 0])
    check_true("tension pushes on the right half of the right bore", np.all(pr.grid.X[tension, 0] > 75.0))
    expect_error("bores overlap", tp.pin_link, 50, 30, 5.0, 3.0, error=ValueError)
    expect_error("ring larger than the half height", tp.pin_link, 90, 30, 13.0, 3.0, error=ValueError)
    expect_error("zero load case", tp.pin_link, 90, 30, 5.0, 3.0, cases=((0.0, 0.0),), error=ValueError)


def test_pin_link_card_stretch_against_bar_theory():
    card = C.load_card(ROOT / "studies" / "cards" / "rehearsal_pin_link.json")
    pr, _, h, _ = C.problem(card)
    solid = np.ones((pr.grid.nely, pr.grid.nelx))
    a = C.analyse(card, solid)
    g = card.geometry
    x = pr.grid.vector(solid)
    x[pr.passive == 1] = 0.0
    U = pr.analysis(x)[2]
    along = [abs(pr.F[:, k] @ U[:, k]) / np.abs(pr.F[:, k]).sum() for k in range(pr.F.shape[1])]
    # tension case against a plain bar between the bore edges, L / (E A) with unit E, t and P in element units;
    # holes and bearing make the real link softer, so the FE stretch must exceed the bar value
    length = (float(g["length_m"]) - float(g["height_m"]) - float(g["bore_diameter_m"])) / h
    bar = length / (float(g["height_m"]) / h)
    check_true("tension stretch above the plain-bar value (holes, bearing)", along[0] > bar)
    check_true("but within 3x of it", along[0] < 3 * bar)
    check("card deflection = worst case along the load", a["tip_unit"], max(along), rtol=1e-12)
    check_true("the side load governs (cantilever bending from the fixed pin)", int(np.argmax(along)) == 2)
    check_true("stress envelope finite and positive", np.isfinite(a["vm_unit_max"]) and a["vm_unit_max"] > 0)


def test_pin_link_mesh_refinement_has_no_mechanism():
    # regression (3 Nov): on a 4x mesh, bore-edge nodes inside the coarse void pixels floated among void elements
    # and the loaded ones made a mechanism (deflection factor ~6.6e4); the edge band and solid rings prevent it
    card = C.load_card(ROOT / "studies" / "cards" / "rehearsal_pin_link.json")
    pr, *_ = C.problem(card)
    mesh = C.mesh_check(card, np.ones((pr.grid.nely, pr.grid.nelx)))
    ratio = mesh[-1]["tip_unit"] / mesh[0]["tip_unit"]
    check_true(f"4x-mesh deflection factor near 1 (got {ratio:.3f})", 0.9 < ratio < 1.3)
