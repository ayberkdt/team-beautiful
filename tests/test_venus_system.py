"""VESPER system-level checks: sizing closure, performance, descent, thermal, link, navigation, control, hybrid,
mission simulation, risk register, design document."""
from __future__ import annotations

import json
import math

import numpy as np
import pytest

from aerokit import venus_flight as VF
from aerokit.venus import atmosphere as A
from aerokit.venus import bemt as B
from aerokit.venus import control as C
from aerokit.venus import descent as DS
from aerokit.venus import hybrid as H
from aerokit.venus import link as L
from aerokit.venus import navigation as N
from aerokit.venus import performance as F
from aerokit.venus import risk as R
from aerokit.venus import sizing as S
from aerokit.venus import thermal as T


@pytest.fixture(scope="module")
def design():
    return S.close(2.3, 70.0)


def test_closure_is_self_consistent(design):
    assert design.converged
    total = sum(design.breakdown.values())
    assert total == pytest.approx(design.gross_kg, rel=1e-3)
    assert design.breakdown["contingency"] == pytest.approx(design.gross_kg / 1.2 * 0.2, rel=1e-3)
    # rotor carries its share at the trimmed collective
    s = A.state(55e3)
    assert design.hover.per_rotor.thrust * 6 == pytest.approx(design.gross_kg * s.g, rel=1e-4)
    assert 0.08 < design.hover.per_rotor.CT / design.rotor.solidity * 1.0 < 0.12   # C_T/σ design 0.10


def test_bigger_rotors_lower_power_loading(design):
    small = S.close(1.7, 70.0)
    assert design.P_hover_elec_W / design.gross_kg < small.P_hover_elec_W / small.gross_kg


def test_one_hour_reserve_does_not_close_for_the_baseline():
    """Sensitivity finding: a 1 h no-sun hover reserve has a mass-growth factor above 1 (no design exists)."""
    from dataclasses import replace

    with pytest.raises(ValueError):
        S.close(2.6, 70.0, replace(S.Requirements(), reserve_hover_h=1.0))


def test_forward_flight_power_bucket(design):
    s = A.state(55e3)
    fl = B.FlowState(s.rho, s.mu, s.a)
    W = design.gross_kg * s.g
    p0 = F.forward_power(design.system, W, fl, 0.0)
    assert p0 == pytest.approx(design.hover.shaft_W, rel=1e-6)            # hover limit
    v, pb = F.bucket(design.system, W, fl)
    assert 5.0 < v < 12.0 and pb < 0.75 * p0
    assert F.forward_power(design.system, W, fl, 30.0) > p0               # parasite drag wins at high speed


def test_parachute_and_deployment():
    es = DS.entry_system(42.0)
    assert es["total"] == pytest.approx(210.0)
    assert sum(v for k, v in es.items() if not k.startswith("total")) == pytest.approx(210.0)
    r = DS.parachute_descent(220.0, 12.0, 79e3, 61e3, 200.0)
    assert 8.0 < r.V_end < 20.0
    pre = DS.deploy(42.0, 61e3, 12.0, 4.4, mode="pre-spun")
    drop = DS.deploy(42.0, 61e3, 12.0, 4.4, mode="drop-then-spin")
    assert pre.altitude_loss_m < 50.0 < 300.0 < drop.altitude_loss_m


def test_thermal_steady_and_diode():
    v = T.Vessel()
    hot, _ = T.vessel_steady(v, 50e3, 80.0)
    ok, _ = T.vessel_steady(v, 56e3, 80.0)
    cold, _ = T.vessel_steady(v, 62e3, 80.0)
    assert hot > 60.0 and 0.0 < ok < 45.0 and 0.0 < cold < 45.0
    assert T.conductance(v, 330.0, 340.0) == pytest.approx(v.G_ins)        # closed when the shell is hotter
    h = T.convection_coefficient(8.0, 0.6, 300.0, 0.889)
    assert 5.0 < h < 40.0


def test_relay_link_geometry_and_rate():
    assert L.slant_range(55e3, 1000e3, 90.0) == pytest.approx(945e3, rel=1e-9)
    assert L.pass_duration(55e3, 1000e3) > L.pass_duration(55e3, 300e3)
    lk = L.RelayLink()
    assert L.link_rate(lk, 1000e3) == pytest.approx(4 * L.link_rate(lk, 2000e3), rel=1e-6)   # inverse square
    assert 10.0 < L.veva_check() < 25.0


def test_navigation_numbers():
    assert 50.0 < N.baro_altitude_error(55e3) < 500.0
    assert N.gyrocompass_ratio(1.0) < 0.1 < 1.0 < N.gyrocompass_ratio(0.01)
    assert N.ground_position_error(3600.0) == pytest.approx(math.hypot(2e3, 18e3))


def test_control_numbers(design):
    s = A.state(55e3)
    fl = B.FlowState(s.rho, s.mu, s.a)
    W = design.gross_kg * s.g
    vmax = C.max_airspeed(design.system, W, fl, design.hover.shaft_W * 1.6 ** 1.5)
    assert 10.0 < vmax < A.zonal_wind(55e3)                               # cannot hold station
    assert C.downdraft_hold_power(W, 3.0, 0.84) > 1000.0
    I = C.blade_inertia(0.3, 1.15, 2)
    assert C.rpm_response_time(I, 60.0, 2.0) > 0.2


def test_hybrid_vega_check():
    # VEGA: 21 kg floated at ~54 km by a ~3.4-3.5 m helium sphere (agent notes); our lift model, vehicle 8.5 kg
    h = H.size_hybrid(8.5, 1.0, 54e3, areal_kg_m2=H.VEGA_ENVELOPE_AREAL, sleep_W=0.0)
    assert 3.0 < h.diameter_m < 4.0
    assert h.floated_kg == pytest.approx(8.5 + h.envelope_kg)


def test_mission_simulation(design):
    r = VF.simulate_rotorcraft_day(design, start_hour_angle_deg=-45.0, dt=120.0,
                                   dives=((6 * 3600.0, 51.0, 300.0),))
    assert 30.0 < r.flight_time_s / 3600.0 < 60.0
    assert r.solar_sustained_s > 0.7 * r.flight_time_s
    assert np.all(np.diff(r.x) > 0)                                       # drifts west with the super-rotation
    assert r.T_interior_C.max() < 62.0        # the end event fires one step after crossing 60 °C
    early = VF.simulate_rotorcraft_day(design, start_hour_angle_deg=-80.0, dt=120.0)
    assert early.flight_time_s < r.flight_time_s


def test_risk_register_shape():
    assert len(R.RISKS) >= 8
    for r in R.RISKS:
        assert R.score(r, after=True) <= R.score(r)
        assert {"evidence", "mitigation"} <= set(r)
    assert R.colour_band(16) == "red" and R.colour_band(9) == "amber" and R.colour_band(4) == "green"


def test_design_json_on_disk_is_consistent():
    from pathlib import Path

    p = Path(__file__).resolve().parents[1] / "studies" / "final_2026" / "venus" / "design.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["schema"] == "venus_rotorcraft_design/1"
    comp = sum(c["mass_kg"] for c in d["vehicle"]["components"])
    assert comp == pytest.approx(d["vehicle"]["total_mass_kg"], rel=0.01)
    prof = d["atmosphere"]["profile"]
    assert [r["altitude_km"] for r in prof] == list(range(prof[0]["altitude_km"], prof[-1]["altitude_km"] + 1))
    v = d["vehicle"]["rotor"]
    assert v["arm_radius_m"] - v["diameter_m"] / 2 > d["vehicle"]["solar"]["circumradius_m"]


def test_arm_sizing_closed_form():
    from aerokit.venus import structure as ST

    a = ST.size_arm(2.7, 110.0, 0.08, min_wall=0.0)               # deflection-governed when no minimum gauge
    assert a.governing == "deflection"
    assert a.tip_deflection_m == pytest.approx(0.035 * 2.7, rel=1e-9)
    I = math.pi * 0.04 ** 3 * a.wall_m
    assert a.root_stress_Pa == pytest.approx(110.0 * 2.7 * 0.04 / I, rel=1e-9)
    thick = ST.size_arm(2.7, 110.0, 0.08)                          # 0.8 mm minimum gauge governs at 80 mm
    assert thick.governing == "minimum gauge" and thick.mass_per_m > a.mass_per_m


def test_blade_flap_frequency_above_one_per_rev():
    from aerokit.venus import structure as ST

    b = ST.blade_flap(1.3, 0.15, 0.22, 0.09, 0.12, 50.0, 35.0)
    assert b.flap_rotating_per_rev > 1.5                          # MSH hexacopter 1.55/rev (agent note)
    assert b.tip_deflection_m < 0.05
    slow = ST.blade_flap(1.3, 0.15, 0.22, 0.09, 0.12, 5.0, 35.0)
    assert slow.flap_rotating_per_rev > b.flap_rotating_per_rev    # stiffness dominates at low rotor speed


def test_heave_damping_and_gust_hold(design):
    s = A.state(55e3)
    fl = B.FlowState(s.rho, s.mu, s.a)
    W = design.gross_kg * s.g
    Zw = C.heave_derivative(design.system, W, fl)
    assert Zw < 0                                                   # climbing through the air lowers thrust
    # closed form for a fixed-pitch rotor with uniform inflow (blade element + momentum, linearised about hover):
    # dC_T/dλ_c = -(σa/8) / (1 + σa/(16 λ_i)); BEMT adds tip loss and root cut-out -> within 15 %
    sig, a = design.rotor.solidity, design.rotor.airfoil.cl_alpha
    vt = design.hover.per_rotor.tip_speed
    lam_i = design.hover.v_h / vt
    dct = -(sig * a / 8.0) / (1.0 + sig * a / (16.0 * lam_i))
    closed = 6 * dct * s.rho * design.rotor.disk_area * vt
    assert Zw == pytest.approx(closed, rel=0.15)
    held = C.gust_response(design.gross_kg, W, Zw, 0.1, kp=0.1, kd=1.0, duration_s=1800.0)
    free = C.gust_response(design.gross_kg, W, Zw, 0.1, kp=0.0, kd=0.0, duration_s=1800.0)
    assert held["z_rms_m"] < 20.0 < free["z_rms_m"]
    assert held["dT_peak_over_W"] < 0.6                             # inside the 1.6 thrust margin


def test_design_json_events_are_machine_readable():
    from pathlib import Path

    p = Path(__file__).resolve().parents[1] / "studies" / "final_2026" / "venus" / "design.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    ev = d["operations"]["events"]
    assert ev[0]["kind"] == "release" and ev[-1]["kind"] == "end"
    assert all(40.0 < e["altitude_km"] < 62.0 for e in ev)
    assert all(e["kind"] != "other" for e in ev)
    labels = [c["label"] for c in d["vehicle"]["components"]]
    assert all(len(x) <= 24 for x in labels)


def test_terminal_descent_never_lands_alive():
    A_disk = 6 * math.pi * 1.3 ** 2
    wind = DS.terminal_descent(43.7, 1.2 * A_disk, 47e3, 60.0)
    fail = DS.terminal_descent(43.7, 0.45, 47e3, 60.0)
    assert wind.t_surface_s > 5 * fail.t_surface_s                 # windmilling rotors are a decelerator
    for r in (wind, fail):
        assert r.t_electronics_125C_s is not None and r.t_electronics_125C_s < r.t_surface_s
        assert r.h_electronics_125C_m > 10e3
    placed = DS.terminal_descent(43.7, 1.2 * A_disk, 0.5, 25.0)
    assert 5 * 60 < placed.t_electronics_125C_s < 127 * 60         # far below Venera 13's 127 min


def test_deployment_monte_carlo_forward_beats_vertical(design):
    vh = 3.9
    fwd = DS.deployment_monte_carlo(design.gross_kg, 227.0, 12.0, vh, n=40, procedure="forward")
    ver = DS.deployment_monte_carlo(design.gross_kg, 227.0, 12.0, vh, n=40, procedure="vertical")
    assert (fwd.vrs_time_s == 0).all() and (ver.vrs_time_s > 0).all()
    assert np.percentile(fwd.altitude_loss_m, 90) < np.percentile(ver.altitude_loss_m, 90) < 300.0
    assert fwd.swing_deg.max() < 5.0
