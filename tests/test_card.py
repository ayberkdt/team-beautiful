"""Task-card pipeline (aerokit.design.card) against the rehearsal numbers and closed-form checks."""
import json
from pathlib import Path

import numpy as np

from aerokit.design import card as C
from aerokit.verification import check, check_true, expect_error

ROOT = Path(__file__).resolve().parents[1]


def _rehearsal_designs():
    runs = json.loads((ROOT / "prev_guess" / "01_Ansys" / "retain_sweep" / "retain_sweep.json").read_text(encoding="utf-8"))["runs"]
    return [{"volume": r["volume"], "density": np.asarray(r["density"])} for r in runs]


def test_matches_rehearsal_script():
    card = C.load_card(ROOT / "prev_guess" / "01_Ansys" / "cards" / "rehearsal_l_bracket.json")
    out = C.run(card, _rehearsal_designs())
    ref = json.loads((ROOT / "prev_guess" / "01_Ansys" / "rehearsal" / "rehearsal.json").read_text(encoding="utf-8"))
    check("ultimate load 1.5 x 1.15 x 2 kN", out["ultimate_N"], 3450.0, rtol=1e-12)
    check("same 4x-mesh deflection factor", out["deflection_mesh_factor"], ref["deflection_mesh_factor"], rtol=1e-9)
    names = {"Scalmalloy": "Scalmalloy TO + Eİ", "AlSi10Mg": "AlSi10Mg TO + Eİ"}
    for row in out["rows"]:
        if row["material"] not in names:
            continue
        r = next(x for x in ref["rows"] if x["option"] == names[row["material"]] and x["volume"] == row["volume"])
        check(f"{row['material']} {row['volume']}: mass", 1000 * row["mass_kg"], r["mass_g"], rtol=1e-9)
        check(f"{row['material']} {row['volume']}: deflection", 1000 * row["deflection_m"],
              r["deflection_mm_refined"], rtol=1e-9)
    check_true("deflection governs the rehearsal card", out["ranking"][0]["governs"] == "deflection")


def test_temperature_screen_and_validation(tmp_path):
    raw = json.loads((ROOT / "prev_guess" / "01_Ansys" / "cards" / "rehearsal_l_bracket.json").read_text(encoding="utf-8"))
    raw["limits"]["service_temperature_C"] = 150
    raw["volumes"] = [0.5]
    p = tmp_path / "hot.json"
    p.write_text(json.dumps(raw), encoding="utf-8")
    card = C.load_card(p, root=ROOT)
    out = C.run(card, [_rehearsal_designs()[0]])
    check_true("Scalmalloy screened out above 100 C", [e["material"] for e in out["excluded"]] == ["Scalmalloy"])
    raw["geometry"]["type"] = "sphere"
    p.write_text(json.dumps(raw), encoding="utf-8")
    expect_error("unknown geometry", C.load_card, p, root=ROOT, error=ValueError)


def test_cantilever_tip_against_beam_theory():
    # Slender solid cantilever 40 x 4 elements, tip load at mid-height: Timoshenko tip deflection
    # delta = P L^3/(3 E I) + P L/(kappa G A); unit E, t, P; Q4 is stiff in bending, so allow 25 %.
    raw = json.loads((ROOT / "prev_guess" / "01_Ansys" / "cards" / "template_cantilever.json").read_text(encoding="utf-8"))
    raw["geometry"].update({"length_m": 1.0, "height_m": 0.1, "elements": 40, "load_at": "middle"})
    card = C._parse(raw, ROOT)
    a = C.analyse(card, np.ones((4, 40)))
    L, H, nu = 40.0, 4.0, 0.3
    I_, A = H ** 3 / 12, H
    G = 1 / (2 * (1 + nu))
    delta = L ** 3 / (3 * I_) + L / (5 / 6 * G * A)
    check("Q4 tip deflection within 25 % of beam theory", a["tip_unit"], delta, rtol=0.25)
    check("stress recovery in uniform tension", C.tension_check(), 1.0, rtol=1e-6)
