"""FE result checks (aerokit.design.fea_checks) on sequences with known behaviour and on the rehearsal mesh study."""
import json
from pathlib import Path

from aerokit.design import fea_checks as fc
from aerokit.verification import check, check_true

ROOT = Path(__file__).resolve().parents[1]


def test_second_order_sequence_extrapolates_exactly():
    f = lambda h: 100.0 + 3.0 * h ** 2  # noqa: E731
    v = fc.mesh_verdict([4.0, 2.0, 1.0], [f(4.0), f(2.0), f(1.0)])
    check("observed order 2", v["order"], 2.0, rtol=1e-6)
    check("Richardson value = exact limit", v["extrapolated"], 100.0, rtol=1e-9)


def test_singular_sequence_is_flagged():
    f = lambda h: 50.0 * h ** -0.5  # noqa: E731     a re-entrant corner: stress grows without bound
    v = fc.mesh_verdict([4.0, 2.0, 1.0], [f(4.0), f(2.0), f(1.0)])
    check_true("growing differences -> diverging", v["verdict"] == "diverging")


def test_rehearsal_mesh_study():
    out = json.loads((ROOT / "prev_guess" / "01_Ansys" / "cards" / "out" / "rehearsal_l_bracket" / "result.json").read_text(
        encoding="utf-8"))
    m = out["mesh_check"]
    sizes = [1.0 / r["refinement"] for r in m]
    tip = fc.mesh_verdict(sizes, [r["tip_unit"] for r in m])
    peak = fc.mesh_verdict(sizes, [r["vm_unit_max"] for r in m])
    p99 = fc.mesh_verdict(sizes, [r["vm_unit_p99"] for r in m])
    check_true("rehearsal tip deflection converges", tip["verdict"] in ("converged", "converging"))
    check_true("rehearsal peak stress diverges (corner singularity)", peak["verdict"] == "diverging")
    check_true("99th-percentile stress does not diverge", p99["verdict"] != "diverging")


def test_reactions_and_averaging():
    r = fc.reaction_balance([0, 0, 35586.0], [[0, 0, -10000.0], [0, 0, -12000.0], [0, 0, -13586.0]])
    check("balanced reactions", r["relative"], 0.0, atol=1e-12)
    check_true("20 % averaging gap is flagged", not fc.averaging_gap(480.0, 600.0)["ok"])
