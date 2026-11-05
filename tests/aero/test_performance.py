"""Tests of the extended point performance in aerokit.aero.performance (P0-2).

Closed forms are derived in the docstrings of the functions under test (parabolic polar: Anderson 2017,
Eq. 6.24, read from the user's PDF; performance models after Raymer 2018 Ch. 17, *not read in this
session*, so every expected value here is a derivation, not a book number). The 2023 rehearsal design is
the one of docs/04_2023_example_solution.md (W0 5974 kg, S 27.5 m², 1667 kW).
"""
import math

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from aerokit.aero import performance as P
from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.atmosphere import isa
from aerokit.aero.propulsion import Turbofan, Turboprop
from aerokit.verification import check, check_true, expect_error

POLAR = "Anderson 2017 Eq. 6.24 (parabolic polar) + derivation"
DOC04 = "docs/04_2023_example_solution.md (2023 card / rehearsal sizing)"
MAINT = "maintainer measurement quoted in the P0-2 task brief (2026-10-25)"

W0_REH = 5974 * G0
PAYLOAD_REH = 1474 * G0                       # 4 crew + 10 pax at 91 kg + 200 kg (docs/04 §1)


def _rehearsal(**kw):
    base = dict(W_fuel=0.156 * W0_REH, W_empty=0.597 * W0_REH, W_payload=PAYLOAD_REH)   # Wf/W0, We/W0: docs/04
    base.update(kw)
    return Aircraft("rehearsal 2023", W0_REH, 27.5, 9.0, 0.0280, 0.783,
                    Turboprop(P_sl=1667e3, eta=0.8, eta_takeoff=0.6), 1.5, 1.7, 2.0, **base)


def _jet():
    return Aircraft("jet", 1.0e5, 30.0, 8.0, 0.020, 0.80, Turbofan(T_sl=3.0e4), 1.5, 1.8, 2.2)


REQ_2023 = {"range": 1300e3, "loiter": 30 * 60.0, "stall_speed": 150 / 3.6, "max_speed": 500 / 3.6,
            "service_ceiling": 10000.0, "rate_of_climb": 10.0, "takeoff_ground_roll": 800.0,
            "payload": PAYLOAD_REH}


def test_polar_optima_closed_form():
    ac = _rehearsal()
    for h in (0.0, 3000.0, 8000.0):
        v_ld, v_mp = P.speed_max_LD(ac, h), P.speed_min_power(ac, h)
        check(f"C_L at V_(L/D)max = √(C_D0/K), h = {h:g}", ac.CL(v_ld, h), math.sqrt(ac.CD0 / ac.K), rtol=1e-12,
              source=POLAR)
        check(f"C_L at V_minP = √(3 C_D0/K), h = {h:g}", ac.CL(v_mp, h), math.sqrt(3 * ac.CD0 / ac.K), rtol=1e-12,
              source=POLAR)
        check(f"D_min = W/(L/D)max, h = {h:g}", ac.drag(v_ld, h), ac.W0 / ac.LD_max, rtol=1e-12, source=POLAR)
        check_true(f"V_minP = 3^(-1/4) V_(L/D)max, h = {h:g}", math.isclose(v_mp, v_ld * 3 ** -0.25, rel_tol=1e-12),
                   source="derivation: V ∝ C_L^(-1/2)")


def test_breguet_propeller_consistency():
    ac = _rehearsal()
    e = ac.engine
    w0, w1 = ac.W0, ac.W0 - 0.15 * ac.W0
    for h in (0.0, 3000.0, 7000.0):
        num = P.range_and_endurance(ac, h, w0, w1)
        check(f"range integral = Breguet (η/c)(L/D)ln(W0/W1), h = {h:g}", num["range"],
              P.breguet_range_propeller(e.eta, e.psfc, ac.LD_max, w0, w1), rtol=1e-6,
              source="derivation (Breguet), constant C_L at (L/D)max")
        cl = math.sqrt(ac.CD0 / ac.K)
        check(f"time integral = closed-form endurance at constant C_L, h = {h:g}", num["time"],
              P.breguet_endurance_propeller(e.eta, e.psfc, cl, 2 * ac.CD0, isa(h)["rho"], ac.S, w0, w1), rtol=1e-6,
              source="derivation: dt = −η dW/(c P_R), P_R ∝ W^1.5")
        check(f"mean speed = range/time, h = {h:g}", num["mean_speed"], num["range"] / num["time"], rtol=1e-14)
    # constant speed and altitude: R = (η/c) [atan(W0/Wc) − atan(W1/Wc)] / √(C_D0 K), Wc = qS√(C_D0/K)
    h, V = 3000.0, 110.0
    q = 0.5 * isa(h)["rho"] * V * V
    wc = q * ac.S * math.sqrt(ac.CD0 / ac.K)
    exact = e.eta / e.psfc * (math.atan(w0 / wc) - math.atan(w1 / wc)) / math.sqrt(ac.CD0 * ac.K)
    check("constant-V range integral = arctan closed form", P.range_and_endurance(ac, h, w0, w1, V=V)["range"], exact,
          rtol=1e-6, source="derivation: dR = −η dW/(c D), D = qS C_D0 + K W²/(qS)")
    check("constant-V time = range / V", P.range_and_endurance(ac, h, w0, w1, V=V)["time"], exact / V, rtol=1e-6,
          source="derivation")
    expect_error("W_end ≥ W_start raises", P.range_and_endurance, ac, 0.0, w1, w0, error=ValueError)
    expect_error("unknown speed schedule raises", P.range_and_endurance, ac, 0.0, w0, w1, speed="fast",
                 error=ValueError)
    expect_error("speed below stall raises", P.range_and_endurance, ac, 0.0, w0, w1, V=20.0, error=ValueError)
    expect_error("speed beyond P_A raises", P.range_and_endurance, ac, 0.0, w0, w1, V=200.0, error=ValueError)


def test_breguet_jet_consistency():
    ac = _jet()
    e = ac.engine
    w0, w1 = ac.W0, 0.8 * ac.W0
    h = 5000.0
    rho = isa(h)["rho"]
    cl = math.sqrt(ac.CD0 / (3 * ac.K))
    cd = ac.CD0 + ac.K * cl * cl
    check("jet range integral = (2/c_t)√(2/ρS)(√C_L/C_D)(√W0 − √W1)", P.range_and_endurance(ac, h, w0, w1)["range"],
          P.breguet_range_jet(e.tsfc, cl, cd, rho, ac.S, w0, w1), rtol=1e-6,
          source="derivation (Breguet jet), C_L = √(C_D0/3K)")
    check("jet endurance integral = (L/D)max ln(W0/W1)/c_t",
          P.range_and_endurance(ac, h, w0, w1, speed="endurance")["time"],
          P.breguet_endurance_jet(e.tsfc, ac.LD_max, w0, w1), rtol=1e-6, source="derivation (Breguet jet)")
    expect_error("Breguet helper rejects W1 ≥ W0", P.breguet_range_propeller, 0.8, 1e-6, 14.0, 1.0, 2.0,
                 error=ValueError)


def test_ceilings_and_time_to_climb():
    ac = _rehearsal()
    hs, ha = P.service_ceiling(ac), P.absolute_ceiling(ac)
    check("max ROC at the service ceiling = 0.508 m/s", P.max_rate_of_climb(ac, hs), 0.508, rtol=0, atol=1e-4,
          source="definition (100 ft/min); atol from the 1e-4 m/s speed tolerance of best_climb_speed")
    check("max ROC at the absolute ceiling = 0", P.max_rate_of_climb(ac, ha), 0.0, rtol=0, atol=1e-4,
          source="definition")
    check_true("service ceiling below absolute ceiling", hs < ha, (hs, ha))
    check_true("lower weight → higher service ceiling", P.service_ceiling(ac, 0.8 * ac.W0) > hs)
    big = ac.with_(engine=Turboprop(P_sl=2e7))
    small = ac.with_(engine=Turboprop(P_sl=1e5))
    expect_error("ceiling above 20 km is not bracketed", P.service_ceiling, big, error=ValueError)
    expect_error("no climb at sea level is not bracketed", P.absolute_ceiling, small, error=ValueError)
    # integrator vs the analytic linear-ROC case t = (H/ROC0) ln((H − h1)/(H − h2))
    roc0, H = 15.0, 9000.0
    lin = lambda h: roc0 * (1 - h / H)
    for h1, h2 in ((0.0, 6000.0), (1000.0, 8990.0)):
        exact = H / roc0 * math.log((H - h1) / (H - h2))
        check(f"climb_time, linear ROC, log substitution, {h1:g}→{h2:g} m", P.climb_time(lin, h1, h2, ceiling=H),
              exact, rtol=1e-12, source="derivation (exact for a linear profile)")
    check("climb_time, linear ROC, plain Gauss–Legendre 0→6000 m", P.climb_time(lin, 0.0, 6000.0),
          H / roc0 * math.log(H / (H - 6000.0)), rtol=1e-10, source="derivation")
    t50 = P.time_to_climb(ac, 0.0, 9000.0)
    check("time to climb converged (n = 50 vs n = 200)", t50, P.time_to_climb(ac, 0.0, 9000.0, n=200), rtol=1e-6,
          source="quadrature self-convergence")
    t_lin = ha / P.max_rate_of_climb(ac, 0.0) * math.log(ha / (ha - 9000.0))
    check_true("time to climb within 30 % of the linear-ROC estimate", abs(t50 / t_lin - 1) < 0.3, (t50, t_lin),
               source="derivation (linear ROC between SL and the absolute ceiling)")
    expect_error("time to climb to the absolute ceiling raises", P.time_to_climb, ac, 0.0, ha, error=ValueError)
    expect_error("climb_time h2 ≤ h1 raises", P.climb_time, lin, 100.0, 100.0, error=ValueError)
    expect_error("climb_time with ROC ≤ 0 raises", P.climb_time, lin, 0.0, 9500.0, error=ValueError)


def test_max_speed_and_envelope():
    for ac in (_rehearsal(), _jet()):
        for h in (0.0, 4000.0, 8000.0):
            v = P.max_speed(ac, h)
            check(f"{ac.name}: P_A = P_R at V_max, h = {h:g}", ac.power_available(v, h), ac.power_required(v, h),
                  rtol=1e-9, source="definition of V_max")
            check_true(f"{ac.name}: V_max above min-power speed, h = {h:g}", v > P.speed_min_power(ac, h))
            check_true(f"{ac.name}: excess power negative just above V_max, h = {h:g}",
                       ac.power_available(1.001 * v, h) < ac.power_required(1.001 * v, h))
    ac = _rehearsal()
    expect_error("V_max above the absolute ceiling raises", P.max_speed, ac, 12000.0, error=ValueError)
    env = P.flight_envelope(ac, [0.0, 5000.0, 10000.0, 15000.0])
    check_true("envelope V_stall increases with h", np.all(np.diff(env["V_stall"]) > 0), env["V_stall"])
    check_true("envelope closed at 15 km (NaN)", np.isnan(env["V_max"][-1]), env["V_max"])
    check("envelope V_max(0) = max_speed", env["V_max"][0], P.max_speed(ac, 0.0), rtol=1e-12)


def test_takeoff_closed_form():
    ac = _rehearsal()
    to = P.takeoff_distance(ac, obstacle=0.0)
    rho = isa(0.0)["rho"]
    vs = math.sqrt(2 * ac.W0 / (rho * ac.S * ac.CLmax_takeoff))
    v_lof = 1.1 * vs
    v7 = 0.7 * v_lof
    q = 0.5 * rho * v7 ** 2
    cl = ac.mu_roll / (2 * ac.K)
    T = ac.engine.eta_takeoff * ac.engine.P_sl / v7
    D = q * ac.S * (ac.CD0 + ac.K * cl ** 2)
    a = G0 * (T - D - ac.mu_roll * (ac.W0 - q * ac.S * cl)) / ac.W0
    check("V_LOF = 1.1 V_stall,TO", to["V_LOF"], v_lof, rtol=1e-12, source="model convention (assumption)")
    check("a_mean at 0.7 V_LOF", to["a_mean"], a, rtol=1e-12, source="derivation: m dV/dt = T − D − μ(W − L)")
    check("ground roll s = V_LOF²/(2 a_mean)", to["ground_roll"], v_lof ** 2 / (2 * a), rtol=1e-12,
          source="derivation (constant acceleration)")
    check("no air distance for obstacle = 0", to["air_distance"], 0.0, atol=1e-12)
    rot = P.takeoff_distance(ac, obstacle=0.0, t_rotation=3.0)
    check("rotation adds V_LOF·t", rot["rotation"], 3.0 * v_lof, rtol=1e-12, source="derivation")
    # air distance, both branches
    full = P.takeoff_distance(ac)
    R = (1.15 * vs) ** 2 / (G0 * 0.2)
    if full["climb"] == 0.0:
        check("obstacle cleared in the arc: s_T = √(R² − (R − h)²)", full["transition"],
              math.sqrt(R ** 2 - (R - 15.24) ** 2), rtol=1e-12, source="derivation (circular arc)")
    high = P.takeoff_distance(ac, obstacle=200.0)
    g = high["climb_angle"]
    check("straight climb reaches the obstacle: h_TR + s_C tan γ = h_obs",
          R * (1 - math.cos(g)) + high["climb"] * math.tan(g), 200.0, rtol=1e-12, source="derivation")
    check("total = sum of segments", high["total"], high["ground_roll"] + high["transition"] + high["climb"],
          rtol=1e-12)
    expect_error("no net accelerating force raises", P.takeoff_distance, ac, 0.0, None, None, 0.9, CL_ground=0.0,
                 error=ValueError)


def test_landing_closed_form():
    ac = _rehearsal()
    ld = P.landing_distance(ac)
    rho = isa(0.0)["rho"]
    vs = math.sqrt(2 * ac.W0 / (rho * ac.S * ac.CLmax_landing))
    v_td = 1.15 * vs
    q = 0.5 * rho * (0.7 * v_td) ** 2
    a = G0 * (q * ac.S * ac.CD0 + 0.4 * ac.W0) / ac.W0
    check("approach speed 1.3 V_stall,L", ld["V_approach"], 1.3 * vs, rtol=1e-12, source="convention (assumption)")
    check("braking s = V_TD²/(2a), μ = 0.4, lift dumped", ld["braking"], v_td ** 2 / (2 * a), rtol=1e-12,
          source="derivation")
    check("free roll 1 s", ld["free_roll"], v_td, rtol=1e-12)
    R = (1.23 * vs) ** 2 / (G0 * 0.2)
    gam = math.radians(3.0)
    check("approach + flare reach 50 ft", ld["approach"] * math.tan(gam) + R * (1 - math.cos(gam)), 15.24,
          rtol=1e-12, source="derivation")
    rev = P.landing_distance(ac, reverse_thrust=0.5)
    check_true("reverse thrust shortens the braking roll", rev["braking"] < ld["braking"])
    expect_error("reverse_thrust > 1 raises", P.landing_distance, ac, reverse_thrust=1.5, error=ValueError)


def test_payload_range_corners():
    ac = _rehearsal()
    e = ac.engine
    pl_max, f_max = PAYLOAD_REH, 0.25 * ac.W0
    pr = P.payload_range(ac, pl_max, f_max, h_cruise=3000.0)
    check_true("four points", all(len(v) == 4 for v in pr.values()))
    check("start at zero range", pr["range"][0], 0.0, atol=0.0)
    check("A at MTOW", pr["takeoff_weight"][1], ac.W0, rtol=1e-12, source="definition of corner A")
    check("B at MTOW with full fuel", pr["takeoff_weight"][2], ac.W0, rtol=1e-12)
    check("C ferry payload = 0", pr["payload"][3], 0.0, atol=0.0)
    check_true("range increases A → B → C", np.all(np.diff(pr["range"]) > 0), pr["range"])
    w_to = ac.W_empty + f_max
    check("ferry range = Breguet", pr["range"][3],
          P.breguet_range_propeller(e.eta, e.psfc, ac.LD_max, w_to, w_to - 0.94 * f_max), rtol=1e-6,
          source="derivation (Breguet)")
    expect_error("no empty weight raises", P.payload_range, ac.with_(W_empty=0.0), pl_max, f_max, h_cruise=0.0,
                 error=ValueError)
    expect_error("payload filling MTOW raises", P.payload_range, ac, 0.5 * ac.W0, f_max, h_cruise=0.0,
                 error=ValueError)


def test_rehearsal_regression_and_compliance():
    ac = _rehearsal()
    check("max ROC at SL ≈ 18.6 m/s", P.max_rate_of_climb(ac, 0.0), 18.6, rtol=0, atol=0.05, source=MAINT)
    check("max ROC at 10 000 m ≈ 0.50 m/s", P.max_rate_of_climb(ac, 10000.0), 0.50, rtol=0, atol=0.01, source=MAINT)
    check("service ceiling ≈ 10 000 m (within 2 %)", P.service_ceiling(ac), 10000.0, rtol=0.02,
          source=DOC04 + ": ceiling 10 000 m governs the installed power")
    check("V_max(SL) ≈ 500 km/h (within 1 %)", P.max_speed(ac, 0.0) * 3.6, 500.0, rtol=0.01,
          source=DOC04 + ": Vmax 500 km/h needs 1662 kW vs 1667 kW installed")
    rows = P.compliance(ac, REQ_2023)
    check("all 8 requirements of the 2023 card evaluated", len(rows), 8, source=DOC04)
    check_true("rows in the fixed order", [r["requirement"] for r in rows] ==
               ["range", "loiter", "stall_speed", "max_speed", "service_ceiling", "rate_of_climb",
                "takeoff_ground_roll", "payload"], [r["requirement"] for r in rows])
    for r in rows:
        check_true(f"{r['requirement']}: finite value, passed ⇔ margin ≥ 0",
                   math.isfinite(r["achieved"]) and r["passed"] == (r["margin"] >= 0) and r["method"], r)
    by = {r["requirement"]: r for r in rows}
    check("stall row = √(2W/(ρ S CLmax,L))", by["stall_speed"]["achieved"],
          math.sqrt(2 * ac.W0 / (isa(0.0)["rho"] * ac.S * 2.0)), rtol=1e-12, source="derivation")
    check("climb row = max_rate_of_climb(SL)", by["rate_of_climb"]["achieved"], P.max_rate_of_climb(ac, 0.0),
          rtol=1e-12)
    # mission consistency: range after the required loiter uses exactly the remaining fuel
    r_only = P.compliance(ac, {"range": 1300e3})[0]["achieved"]
    check_true("loiter reduces the achievable range", by["range"]["achieved"] < r_only,
               (by["range"]["achieved"], r_only))
    w_end = ac.W0 - 0.94 * ac.W_fuel
    check("range-only mission = Breguet on 94 % of the fuel", r_only,
          P.breguet_range_propeller(0.8, ac.engine.psfc, ac.LD_max, ac.W0, w_end), rtol=1e-6, source="derivation")
    expect_error("unknown requirement key raises", P.compliance, ac, {"rnage": 1.0}, error=ValueError)
    expect_error("range without fuel weight raises", P.compliance, ac.with_(W_fuel=0.0), {"range": 1e6},
                 error=ValueError)
    expect_error("payload without weights raises", P.compliance, ac.with_(W_empty=0.0, W_payload=0.0),
                 {"payload": 1.0}, error=ValueError)
    expect_error("non-positive requirement raises", P.compliance, ac, {"rate_of_climb": 0.0}, error=ValueError)
    land = P.compliance(ac, {"landing_distance": 900.0})[0]
    check("landing row = landing_distance total", land["achieved"], P.landing_distance(ac)["total"], rtol=1e-12)


@settings(max_examples=25, deadline=None)
@given(st.floats(0.0, 14000.0), st.floats(100.0, 5000.0))
def test_property_roc_decreases_with_altitude(h, dh):
    ac = _rehearsal()
    h2 = min(h + dh, 19000.0)
    check_true("ROC_max(h) decreasing", P.max_rate_of_climb(ac, h) > P.max_rate_of_climb(ac, h2), (h, h2))


@settings(max_examples=25, deadline=None)
@given(st.floats(0.6, 1.2), st.floats(0.01, 0.3))
def test_property_takeoff_increases_with_weight(f, df):
    ac = _rehearsal()
    a, b = P.takeoff_distance(ac, W=f * ac.W0), P.takeoff_distance(ac, W=(f + df) * ac.W0)
    check_true("ground roll increases with W", b["ground_roll"] > a["ground_roll"], (f, df))
    check_true("total to 50 ft increases with W", b["total"] > a["total"], (f, df))
