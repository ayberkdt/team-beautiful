"""JSON input reading and example models (aerokit/data/examples/*.json)."""
from aerokit.data import EXAMPLES_DIR

import numpy as np

from aerokit.fem import reader
from aerokit.verification import check, check_true, expect_error
from aerokit.materials import library

EXAMPLES = EXAMPLES_DIR


def test_cantilever_frame_json():
    m, settings = reader.from_file(EXAMPLES / "cantilever_frame.json")
    o = reader.solve(m, settings)
    E = library.find("7075-T6")["E"]
    check("JSON cantilever: tip deflection PL³/3EI", o["max_disp"][1], -1000 * 2.0 ** 3 / (3 * E * 2e-6),
            rtol=1e-10, source="Gere & Timoshenko, Table G-1")
    check("JSON cantilever: sum of reactions + load = 0 (y)", o["reaction_total"][1], 1000.0, rtol=1e-10)


def test_truss_bridge_json():
    m, settings = reader.from_file(EXAMPLES / "truss_bridge.json")
    r = reader.solve(m, settings)["result"]
    N = [s["N"] for s in m.element_results(r["u"])]
    # Method of sections: R = 15 kN; bottom chord 1-2: M(6) = 15·3 − 10·1 = 35 kN·m → 35/1.5 tension
    check("Warren truss: bottom chord 1-2 tension 23.33 kN", N[1], 35e3 / 1.5, rtol=1e-9,
            source="derivation: Ritter method of sections")
    check("Warren truss: top chord 6-7 compression 26.67 kN", N[5], -40e3 / 1.5, rtol=1e-9)
    check("Warren truss: support reaction 15 kN", r["reaction"][1], 15e3, rtol=1e-9)


def test_plate_q8_json():
    m, settings = reader.from_file(EXAMPLES / "plate_q8.json")
    o = reader.solve(m, settings)
    mat = library.find("6061-T6")
    E, nu = mat["E"], mat["nu"]
    G = E / (2 * (1 + nu))
    t, h, L, P = 0.01, 0.1, 1.0, 1e4
    I = t * h ** 3 / 12
    timo = P * L ** 3 / (3 * E * I) + P * L / (5 / 6 * G * t * h)
    check("JSON Q8 plate: tip deflection ≈ Timoshenko beam", -o["max_disp"][1], timo, rtol=1e-2,
            source="derivation: Timoshenko beam (1% tolerance because of the clamped-edge effect)")


def test_input_errors():
    expect_error("unknown element type raises an error", reader.build_model,
               {"ndof": 2, "nodes": [[0, 0], [1, 0]], "elements": [{"kind": "No", "nodes": [0, 1], "E": 1}]},
               error=ValueError)
    expect_error("composite material on an isotropic element raises an error", reader.build_model,
               {"ndof": 2, "nodes": [[0, 0], [1, 0]],
                "elements": [{"kind": "Bar", "nodes": [0, 1], "material": "IM7-8552", "A": 1}]}, error=ValueError)
    m, settings = reader.build_model({"ndof": 3, "nodes": [[0, 0], [1, 0], [2, 0]],
                               "elements": [{"kind": "Frame2D", "nodes": [0, 1], "E": 70e9, "A": 1e-3, "I": 1e-6,
                                             "rho": 2700},
                                            {"kind": "Frame2D", "nodes": [1, 2], "E": 70e9, "A": 1e-3, "I": 1e-6,
                                             "rho": 2700}],
                               "fixed": [{"node": 0, "dof": [0, 1, 2]}], "analysis": "modal", "n": 2})
    o = reader.solve(m, settings)
    check_true("JSON modal: two positive frequencies", len(o["f"]) == 2 and np.all(o["f"] > 0), str(o["f"]))
