"""Plausibility guards of the sizing chain (docs/07 A1–A3).

Every case here is an off-design run of the 2023 requirements that passed silently before the guards
existed (docs/07 §1, stress study of 2026-10-25): a jet class sized as a turboprop, a landing distance
that was only checked afterwards, and installed power that never fed back into the weight.
"""
import math

import numpy as np
import pytest

from aerokit.aero import performance as perf
from aerokit.aero.aircraft import G0
from aerokit.data import example_path
from aerokit.design import sizing as ds
from aerokit.design.pipeline import run
from aerokit.design.requirements import load_assumptions, load_requirements
from aerokit.design.validation import KING_AIR_350I
from aerokit.verification import check, check_true, expect_error

REQ = load_requirements(example_path("design", "ansys_2023_requirements.json"))
OFF = {"power_weight_coupling": "off"}


def req(**changes):
    return load_requirements({**REQ.raw, **changes})


# --- A1: classes and warnings ----------------------------------------------------------------------
@pytest.mark.parametrize("kind", ["jet transport", "jet trainer", "jet fighter", "sailplane"])
def test_non_propeller_classes_are_refused(kind):
    with pytest.raises(ValueError, match="not a propeller class"):
        ds.size(REQ, load_assumptions({"aircraft_type": kind}))


def test_unknown_class_and_mixed_class():
    expect_error("unknown aircraft_type rejected", ds.size, REQ, load_assumptions({"aircraft_type": "airship"}),
                 error=KeyError)
    s = ds.size(REQ, load_assumptions({**OFF, "aircraft_type": "military cargo/bomber"}))
    check_true("mixed propeller/jet class sized with a warning", any("mixes propeller and jet" in w for w in s.warnings),
               s.warnings)


def test_manned_regression_for_unmanned_design_is_flagged():
    uav = req(crew=0, passengers=0, cargo_mass="20 kg")
    s = ds.size(uav, load_assumptions())
    check_true("no-people design on a manned regression warns", any("fitted to manned" in w for w in s.warnings))
    s2 = ds.size(REQ, load_assumptions({**OFF, "aircraft_type": "UAV small"}))
    check_true("people on an unmanned regression warns", any("unmanned-aircraft regression" in w for w in s2.warnings))
    s3 = ds.size(uav, load_assumptions({"aircraft_type": "UAV small"}))
    check_true("UAV class without people: no manned/unmanned warning",
               not any("manned" in w for w in s3.warnings), s3.warnings)


def test_propeller_mach_warning():
    fast = req(max_speed="700 km/h", max_speed_altitude="10000 m", service_ceiling="11000 m")
    s = ds.size(fast, load_assumptions(OFF))
    mach = 700 / 3.6 / 299.53   # ISA speed of sound at 10 km ≈ 299.5 m/s
    check_true("Mach > 0.6 at 10 km flagged", any("propeller compressibility" in w for w in s.warnings), s.warnings)
    check_true("flight Mach of the case really is above the threshold", mach > ds.PROPELLER_MACH_WARNING, mach)
    s0 = ds.size(REQ, load_assumptions(OFF))
    check_true("rehearsal (Mach 0.41 at SL) has no warning", s0.warnings == (), s0.warnings)


def test_power_loading_far_above_class_is_flagged():
    s = ds.size(req(max_speed="650 km/h"), load_assumptions(OFF))
    ref = ds.CLASS_POWER_REFERENCE["twin turboprop"].power_loading
    check_true("650 km/h case is > 2 × the King Air power loading", 2 * ref < s.PW, f"{s.PW:.1f} vs {ref:.1f} W/N")
    check_true("... and is flagged", any("× the twin turboprop reference" in w for w in s.warnings), s.warnings)


def test_invalid_rule_strings():
    for k, v in (("wing_loading", "smallest"), ("power_weight_coupling", "maybe")):
        expect_error(f"{k}={v!r} rejected", ds.size, REQ, load_assumptions({k: v}), error=ValueError)


# --- A3: landing constraint and W/S choice ---------------------------------------------------------
def test_landing_distance_limits_wing_loading():
    """landing 600 m: before, the design was unchanged and failed −10 %; now it is sized for it."""
    r = run(req(landing_distance="600 m"), None, None, figures=False)
    s = r.sizing
    check_true("landing sets W/S", s.ws_basis == "landing limit", s.ws_basis)
    check_true("landing limit below the stall limit", s.ws_limits["landing"] < s.ws_limits["stall"], s.ws_limits)
    total = perf.landing_distance(s.aircraft)["total"]
    check("sized design lands in exactly 600 m (same model as the compliance table)", total, 600.0, rtol=1e-6)
    check_true("all 9 requirements met", all(c["passed"] for c in r.compliance),
               [c["requirement"] for c in r.compliance if not c["passed"]])


def test_landing_limit_is_inactive_when_generous_and_raises_when_impossible():
    s = ds.size(req(landing_distance="2000 m"), load_assumptions(OFF))
    check_true("2000 m landing: stall still sets W/S", s.ws_basis == "stall limit", s.ws_basis)
    check("... and the rehearsal W0 is unchanged", s.mass, 5974, atol=0.5,
          source="docs/04 §1 (coupling off)")
    expect_error("50 m landing is unattainable", ds.size, req(landing_distance="50 m"), load_assumptions(),
                 error=ValueError)


def test_min_power_wing_loading_is_a_minimum():
    asm = load_assumptions({**OFF, "wing_loading": "min_power"})
    s = ds.size(REQ, asm)
    s_max = ds.size(REQ, load_assumptions(OFF))
    check_true("min-power W/S ≤ the stall limit", s.ws_limits["stall"] * (1 + 1e-12) >= s.WS)
    check_true("min-power P/W ≤ P/W at the stall limit", s.PW <= s_max.PW + 1e-9, f"{s.PW:.4f} vs {s_max.PW:.4f}")
    grid = np.linspace(0.25 * s.ws_limits["stall"], s.ws_limits["stall"], 400)
    brute = min(max(v[0] for v in ds.constraint_curves(REQ, asm, np.array([w])).values()) for w in grid)
    check("min-power P/W equals a 400-point brute-force minimum", s.PW, brute, rtol=2e-3)


# --- A2: power–weight coupling ---------------------------------------------------------------------
def test_coupling_formula_and_reference_data():
    kw = KING_AIR_350I
    ref = ds.CLASS_POWER_REFERENCE["twin turboprop"].power_loading
    check("reference P/W = King Air 350i installed power / MTOW", ref, kw["power_W"][0] / (kw["mtow_kg"][0] * G0),
          rtol=1e-12, source=kw["power_W"][1])
    asm = load_assumptions()
    check("default engine specific power = PT6A-60A 780 kW / 221 kg", asm["engine_specific_power"], 780e3 / 221,
          rtol=1e-3, source="Wikipedia PT6 table, read 2026-10-25")
    s = ds.size(REQ, asm)
    check("ΔWe/W0 = g (P/W − ref)/p_eng", s.engine_we_add, G0 * (s.PW - ref) / asm["engine_specific_power"],
          rtol=1e-12)
    off = ds.size(REQ, load_assumptions(OFF))
    check_true("coupling raises the rehearsal design (its P/W is above the King Air's)",
               s.mass > off.mass and s.engine_we_add > 0, f"{off.mass:.0f} → {s.mass:.0f} kg")
    check("power loading is unchanged by the coupling (it depends on W/S only)", s.PW, off.PW, rtol=1e-12)


def test_power_now_feeds_back_into_weight():
    """Before: Vmax 500 → 650 km/h multiplied the power and left W0 at 5974 kg."""
    base = ds.size(REQ, load_assumptions())
    fast = ds.size(req(max_speed="650 km/h"), load_assumptions())
    check_true("Vmax 650 km/h is heavier than Vmax 500 km/h", fast.mass > 1.2 * base.mass,
               f"{base.mass:.0f} → {fast.mass:.0f} kg")
    slow_stall = ds.size(req(stall_speed="110 km/h"), load_assumptions())
    check_true("stall 110 km/h (big wing, high Vmax power) is heavier", slow_stall.mass > base.mass)


@pytest.mark.parametrize("changes", [{"max_speed": "900 km/h"}, {"service_ceiling": "18000 m"},
                                     {"stall_speed": "60 km/h"}])
def test_physically_impossible_turboprops_now_raise(changes):
    """These passed 8/8 at 5974 kg before the coupling (docs/07 §1, extreme.txt)."""
    with pytest.raises(ValueError, match="engine-mass correction"):
        ds.size(req(**changes), load_assumptions())


def test_class_without_reference_skips_coupling_with_warning():
    s = ds.size(REQ, load_assumptions({"aircraft_type": "GA twin engine"}))
    check_true("no reference → no correction", s.engine_we_add == 0.0)
    check_true("... and says so", any("coupling not applied" in w for w in s.warnings), s.warnings)


def test_requirement_changes_still_resize_monotonically():
    masses = [ds.size(req(range=f"{r} km"), load_assumptions()).mass for r in (1300, 2000, 3000)]
    check_true("W0 grows with range", masses[0] < masses[1] < masses[2], [round(m) for m in masses])
    check_true("finite results", all(math.isfinite(m) for m in masses))
    expect_error("12 000 km is infeasible", ds.size, req(range="12000 km"), load_assumptions(), error=ValueError)
