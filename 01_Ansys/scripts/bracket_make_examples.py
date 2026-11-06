"""Write the two rehearsal drawings (parametric JSON) used by ``01_Ansys/scripts/bracket_day.py``.

    python 01_Ansys/scripts/bracket_make_examples.py

* ``sketch_bracket.json`` — a mounting bracket resembling the organisers' sketch [Y]: base plate with four bolt holes,
  an upright lug with a pin hole and two curved arms (gussets). All dimensions are our assumptions.
* ``ge_bracket.json`` — GE-type engine bracket envelope from ``prev_guess/01_Ansys/scripts/ge_bracket_preview.py`` constants (four bolts on
  the base, clevis with two arms around a 19.05 mm pin). Envelope dimensions as parsed there [Y]; loads GE/GrabCAD
  (Carter et al. 2014, Fig. 2: 8000 lbf up, 8500 lbf out, 9500 lbf at 42 deg, 5000 lbf in torsion).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
from aerokit.bracket.geometry import arc  # noqa: E402

OUT = ROOT / "01_Ansys" / "inputs"


def rounded_rect(x0, y0, x1, y1, r):
    pts = []
    pts += arc((x1 - r, y0 + r), r, -90, 0, 6)
    pts += arc((x1 - r, y1 - r), r, 0, 90, 6)
    pts += arc((x0 + r, y1 - r), r, 90, 180, 6)
    pts += arc((x0 + r, y0 + r), r, 180, 270, 6)
    return pts


def sketch() -> dict:
    t = 8.0
    solids = [{"op": "add", "type": "prism", "axis": "z", "polygon": rounded_rect(0, 0, 120, 60, 10), "range": [0, t]}]
    # upright lug in the x-z plane, 16 mm thick (y 22..38), rounded top around the pin at (60, 55)
    lug = [[38, t], [82, t], [80, 55]] + arc((60, 55), 20, 0, 180, 18) + [[40, 55]]
    solids.append({"op": "add", "type": "prism", "axis": "y", "polygon": lug, "range": [22, 38]})
    # two curved arms (gussets) from the plate to the lug, 8 mm thick (y 26..34)
    for sgn in (-1, 1):
        x_in, x_out = (40, 10) if sgn < 0 else (80, 110)
        curve = [[x_out + (x_in - x_out) * (1 - math.cos(a)), t + 40 * math.sin(a)]
                 for a in [i * math.pi / 2 / 12 for i in range(13)]]
        poly = [[x_out, t]] + curve + [[x_in, t]]
        solids.append({"op": "add", "type": "prism", "axis": "y", "polygon": poly, "range": [26, 34]})
    for x, y in ((15, 15), (105, 15), (15, 45), (105, 45)):
        solids.append({"op": "cut", "type": "cylinder", "p0": [x, y, -1], "p1": [x, y, t + 1], "radius": 4.25})
    solids.append({"op": "cut", "type": "cylinder", "p0": [60, 20, 55], "p1": [60, 40, 55], "radius": 7.0})
    return {"name": "Sketch-type mounting bracket (rehearsal, invented dimensions)", "units": "mm",
            "solids": solids,
            "_about": "Invented rehearsal geometry resembling the organisers' sketch: 4 bolt holes dia 8.5 in a "
                      "120 x 60 x 8 plate, lug with a dia 14 pin hole, two curved arms. Not the official part [Y]."}


def ge() -> dict:
    # frame and dimensions from prev_guess/01_Ansys/scripts/ge_bracket_preview.py (dolfiny STEP frame as parsed in R3 §1b) [Y]
    X0, Y0 = -163.3, -74.6
    L, W = 178.5, 107.1
    base_t = 12.0
    solids = [{"op": "add", "type": "box", "min": [X0, Y0, 0], "max": [X0 + L, Y0 + W, base_t]}]
    pin_y, pin_z, lug_r = -56.8, 44.6, 35.56 / 2
    for a, b in ((-92.1, -84.5), (-63.6, -55.9)):
        prof = [[pin_y - lug_r, 0], [pin_y + lug_r + 25, 0], [pin_y + lug_r, pin_z]] + \
            arc((pin_y, pin_z), lug_r, 0, 180, 18)
        solids.append({"op": "add", "type": "prism", "axis": "x", "polygon": prof, "range": [a, b]})
    for bx, by in ((-148.1, -33.6), (-148.1, 18.5), (0.0, -38.1), (0.0, 0.0)):
        solids.append({"op": "add", "type": "cylinder", "p0": [bx, by, 0], "p1": [bx, by, base_t + 3],
                       "radius": 30.48 / 2})
        solids.append({"op": "cut", "type": "cylinder", "p0": [bx, by, -1], "p1": [bx, by, base_t + 4],
                       "radius": 14.17 / 2})
    solids.append({"op": "cut", "type": "cylinder", "p0": [-100, pin_y, pin_z], "p1": [-45, pin_y, pin_z],
                   "radius": 19.05 / 2})
    return {"name": "GE-type engine bracket (envelope approximation)", "units": "mm", "solids": solids,
            "_about": "Approximate GE jet-engine bracket: base plate 178.5 x 107.1 x 12 mm with 4 bolt bosses "
                      "(dia 30.48, bolt dia 14.17) and a clevis (two 7.6 mm arms, pin dia 19.05). Envelope from "
                      "prev_guess/01_Ansys/scripts/ge_bracket_preview.py [Y]; the real part is a STEP file (GrabCAD), not this box."}


def ge_setup(h_mm: float = 3.0) -> dict:
    """Set-up of the GE-type bracket with the GE/GrabCAD load cases (Carter et al. 2014, Fig. 2; SI conversion
    1 lbf = 4.448222 N, 1 lbf in = 0.1129848 N m). LC4 torsion is applied about z as in
    prev_guess/01_Ansys/scripts/ge_bracket_preview.py and the film's ge_yukler.json [Y: axis as interpreted there]."""
    from aerokit.bracket import features, geometry, pipeline
    d = geometry.load_drawing(OUT / "ge_bracket.json")
    vm = geometry.voxelize_drawing(d, h_mm * 1e-3)
    holes = pipeline.holes_from_drawing(d)
    s = features.propose_setup(vm, holes, temperature_C=300.0)
    pin = next(hl["id"] for hl in s["holes"] if hl["role"] == "load")
    lbf, lbfin = 4.448222, 0.1129848
    c42, s42 = math.cos(math.radians(42)), math.sin(math.radians(42))
    s["load_cases"] = [
        {"name": "LC1 vertical 8000 lbf", "loads": [{"hole": pin, "type": "bearing", "force_N": [0, 0, 8000 * lbf]}]},
        {"name": "LC2 horizontal 8500 lbf", "loads": [{"hole": pin, "type": "bearing", "force_N": [0, -8500 * lbf, 0]}]},
        {"name": "LC3 42 deg 9500 lbf", "loads": [{"hole": pin, "type": "bearing",
                                                  "force_N": [0, -9500 * lbf * s42, 9500 * lbf * c42]}]},
        {"name": "LC4 torsion 5000 lbf in", "loads": [{"hole": pin, "type": "moment",
                                                       "moment_Nm": [0, 0, -5000 * lbfin]}]},
    ]
    s["design_criteria"] = {"limit_to_ultimate": 1.0,
                            "_about": "GE challenge criterion: no yield under each load case (Carter et al. 2014) "
                                      "- loads treated as ultimate design loads, factor 1.0 [Y reading]"}
    s["_about"] = ("GE-type bracket rehearsal set-up: roles from aerokit.bracket.features, loads from Carter et al. "
                   "2014 Fig. 2 (read by sub-agent), LC4 axis as in prev_guess/01_Ansys/scripts/ge_bracket_preview.py [Y].")
    return s


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, d in (("sketch_bracket.json", sketch()), ("ge_bracket.json", ge())):
        (OUT / name).write_text(json.dumps(d, indent=1), encoding="utf-8")
        print("wrote", OUT / name)
    (OUT / "ge_setup.json").write_text(json.dumps(ge_setup(), indent=1), encoding="utf-8")
    print("wrote", OUT / "ge_setup.json")
