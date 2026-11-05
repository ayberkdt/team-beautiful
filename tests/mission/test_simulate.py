"""Mission simulation: fuel integral vs Breguet, fuel exhaustion, segment physics, time on station."""
from __future__ import annotations

import math

import pytest

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.atmosphere import isa
from aerokit.aero.performance import best_climb_speed, best_endurance_speed, rate_of_climb
from aerokit.aero.propulsion import Turboprop
from aerokit.mission.geodesy import LocalFrame, direct
from aerokit.mission.patterns import parallel_track
from aerokit.mission.simulate import (Climb, Cruise, Descent, FuelExhaustedError, Loiter, TaxiTakeoff,
                                      max_time_on_station, search_mission, simulate)
from aerokit.verification import check


@pytest.fixture(scope="module")
def ac():
    return Aircraft("rehearsal", 5974 * G0, 27.5, 9, 0.0280, 0.783, Turboprop(1667e3), W_fuel=0.156 * 5974 * G0)


def _cruise_constants(ac, V, h):
    q = 0.5 * isa(h)["rho"] * V * V
    return q * ac.S * ac.CD0, ac.K / (q * ac.S)          # D = A + B W²


@pytest.mark.parametrize("V,h,frac", [(80.0, 3000.0, 0.10), (70.0, 1500.0, 0.15), (95.0, 6000.0, 0.05)])
def test_pure_cruise_fuel_vs_breguet(ac, V, h, frac):
    """Constant V and h, propeller: ds = −(η/c) dW / D(W).

    * exact closed form: R = (η/c)/√(AB) [atan(W0√(B/A)) − atan(W1√(B/A))];
    * Breguet (propeller form) R = (η/c)(L/D) ln(W0/W1) with L/D at the mean weight — within 0.5 %.
    """
    eta, c = ac.engine.eta, ac.engine.psfc
    W0, Wf = ac.W0, frac * ac.W0
    W1 = W0 - Wf
    A, B = _cruise_constants(ac, V, h)
    R_exact = eta / c / math.sqrt(A * B) * (math.atan(W0 * math.sqrt(B / A)) - math.atan(W1 * math.sqrt(B / A)))
    LD = 0.5 * (W0 + W1) / (A + B * (0.5 * (W0 + W1)) ** 2)
    R_breguet = eta / c * LD * math.log(W0 / W1)
    r = simulate(ac, [Cruise(R_exact, V)], fuel=1.2 * Wf, h_start=h, dt=10.0)
    check(f"cruise fuel vs exact constant-V integral ({V} m/s, {h} m)", r.fuel_used, Wf, rtol=1e-6,
          source="closed-form integral of dW/ds = -(c/η)(A + B W²)")
    rb = simulate(ac, [Cruise(R_breguet, V)], fuel=1.2 * Wf, h_start=h, dt=10.0)
    check(f"cruise fuel vs Breguet ({V} m/s, {h} m)", rb.fuel_used, Wf, rtol=5e-3,
          source="Breguet range, propeller form, L/D at mean weight")
    assert r.records[0].duration == pytest.approx(R_exact / V, rel=1e-9)


def test_loiter_fuel_matches_closed_form(ac):
    """Constant-V loiter: dW/dt = −(c/η)V(A + BW²) → t = (η/(cV))/√(AB)·[atan(...)]."""
    V, h, T = 65.0, 1500.0, 3 * 3600.0
    A, B = _cruise_constants(ac, V, h)
    eta, c = ac.engine.eta, ac.engine.psfc
    k = math.sqrt(B / A)
    W1 = math.tan(math.atan(ac.W0 * k) - T * c * V * math.sqrt(A * B) / eta) / k
    r = simulate(ac, [Loiter(T, V)], h_start=h, dt=30.0)
    check("loiter fuel vs closed form", r.fuel_used, ac.W0 - W1, rtol=1e-6, source="closed-form constant-V loiter")


def test_running_out_of_fuel_raises(ac):
    with pytest.raises(FuelExhaustedError, match="cruise") as ei:
        simulate(ac, [TaxiTakeoff(), Climb(3000.0), Cruise(5000e3)], dt=20.0)
    assert 0 < ei.value.distance < 5000e3 and ei.value.time > 0
    # allow_negative_fuel continues (root finding only)
    r = simulate(ac, [Cruise(5000e3)], h_start=3000.0, allow_negative_fuel=True, dt=60.0)
    assert r.fuel_remaining < 0


def test_climb_follows_rate_of_climb_and_ceiling_raises(ac):
    r = simulate(ac, [Climb(3000.0)], dt=5.0)
    rec = r.records[0]
    # time ≈ ∫ dh / ROC_max(h) at roughly constant weight (fuel for the climb is < 1 % of W0)
    import numpy as np
    hs = np.linspace(0, 3000, 301)
    roc = np.array([rate_of_climb(ac, best_climb_speed(ac, h, ac.W0), h, ac.W0) for h in hs])
    t_ref = float(np.trapezoid(1 / roc, hs))
    assert rec.duration == pytest.approx(t_ref, rel=5e-3)
    assert rec.h_end == 3000.0 and rec.fuel > 0
    with pytest.raises(ValueError, match="ceiling"):
        simulate(ac, [Climb(15000.0)], dt=30.0)


def test_speed_limits_and_descent(ac):
    vs = ac.stall_speed(1500.0, ac.W0)
    with pytest.raises(ValueError, match="1.2 V_stall"):
        simulate(ac, [Cruise(10e3, 1.1 * vs)], h_start=1500.0)
    with pytest.raises(ValueError, match="power"):
        simulate(ac, [Cruise(10e3, 200.0)], h_start=1500.0)
    r = simulate(ac, [Descent(0.0, rate=5.0, speed=70.0)], h_start=1500.0, dt=10.0)
    assert r.records[0].duration == pytest.approx(300.0) and r.records[0].h_end == 0.0
    assert r.records[0].distance == pytest.approx(math.sqrt(70 ** 2 - 25) * 300.0)


def test_taxi_allowance_models(ac):
    r = simulate(ac, [TaxiTakeoff()])
    psfc, P = ac.engine.psfc, ac.engine.P_sl
    assert r.fuel_used == pytest.approx(psfc * P * (600 * 0.1 + 60))
    r2 = simulate(ac, [TaxiTakeoff(fuel_fraction=0.03)])
    assert r2.fuel_used == pytest.approx(0.03 * ac.W0)


def test_search_mission_bookkeeping_and_station_time(ac):
    base = (39.0, 30.0)
    la, lo, _ = direct(*base, 90.0, 250e3)
    pat = parallel_track("20 km", "20 km", "1.5 km", frame=LocalFrame(la, lo))
    r = search_mission(ac, base, pat, 1500.0, dt=20.0)
    kinds = [x.kind for x in r.records]
    assert kinds == ["ground", "climb", "cruise", "search", "cruise", "reserve", "descent"]
    search = r.records[3]
    assert search.distance == pytest.approx(pat.length, rel=1e-4)
    assert r.time_on_station == pytest.approx(search.duration)
    assert r.records[5].duration == pytest.approx(1800.0)
    for a, b in zip(r.records[:-1], r.records[1:], strict=True):
        assert a.t_end == pytest.approx(b.t_start) and a.W_end == pytest.approx(b.W_start)
    assert r.fuel_used == pytest.approx(r.W_start - r.records[-1].W_end)
    table = r.timeline()
    assert table.headers[0] == "segment" and len(table.rows) == 7
    T, rm = max_time_on_station(ac, base, pat, 1500.0, dt=20.0)
    ff = ac.fuel_flow(best_endurance_speed(ac, 1500.0, ac.W0), 1500.0, ac.W0)
    assert 0.0 <= rm.fuel_margin < 3 * ff
    assert rm.time_on_station == pytest.approx(T)
    assert r.time_on_station < T                 # the 20 km box leaves fuel to spare
    rf = search_mission(ac, base, pat, 1500.0, reserve=0.1, dt=20.0)
    assert rf.reserve_fuel == pytest.approx(0.1 * ac.W_fuel) and "reserve" not in [x.kind for x in rf.records]
    rc = search_mission(ac, base, pat, 1500.0, cruise_altitude=3000.0, dt=20.0)
    assert [x.name for x in rc.records][3] == "descent to search altitude"


def test_unreachable_area_raises(ac):
    base = (39.0, 30.0)
    la, lo, _ = direct(*base, 90.0, 1500e3)
    pat = parallel_track("20 km", "20 km", "1.5 km", frame=LocalFrame(la, lo))
    with pytest.raises(FuelExhaustedError):
        search_mission(ac, base, pat, 1500.0, dt=60.0)
    with pytest.raises(ValueError, match="cannot be reached"):
        max_time_on_station(ac, base, pat, 1500.0, dt=60.0)
