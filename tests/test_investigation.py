"""Track reconstruction, energy, debris ballistics, search radii, FDM events, HFACS (aerokit.investigation)."""
import math

import numpy as np

from aerokit import investigation as I
from aerokit.mission.geodesy import LocalFrame
from aerokit.verification import check, check_true, expect_error


def _turn(right: bool) -> I.TrackReconstruction:
    t = np.arange(0.0, 120.0, 1.0)
    R, V = 1000.0, 60.0
    w = V / R
    s = 1.0 if right else -1.0
    e = R * np.sin(w * t)                    # starts eastbound
    n = -s * R * (1 - np.cos(w * t))         # right turn → towards the south
    h = 1000.0 - 2.0 * t
    lat, lon, hh = LocalFrame(51.0, 3.0, 0.0).to_geodetic(e, n, h)
    return I.reconstruct_track(t, lat, lon, hh)


def test_reconstruct_coordinated_turn():
    tr = _turn(right=True)
    k = tr.t.size // 2
    w, V = 0.06, 60.0
    check("ground speed 60 m/s", tr.ground_speed[k], V, rtol=1e-3)
    check("right turn rate +3.44 °/s", tr.turn_rate_deg_s[k], math.degrees(w), rtol=1e-2)
    check("bank atan(V ω / g)", tr.bank_deg[k], math.degrees(math.atan(V * w / I.G0)), rtol=1e-2)
    check("vertical speed −2 m/s", tr.vertical_speed[k], -2.0, rtol=1e-3)
    check("load factor 1/cos φ", tr.load_factor[k], 1 / math.cos(math.atan(V * w / I.G0)), rtol=1e-2)
    check_true("left turn is negative", _turn(right=False).turn_rate_deg_s[k] < 0)
    expect_error("too few samples", I.reconstruct_track, [0, 1], [51, 51], [3, 3], [0, 0], error=ValueError)


def test_energy_state():
    es, ps = I.energy_state([0, 1, 2], [100, 100, 100], [50, 49, 48])
    check("E_s = h + V²/2g", es[0], 100 + 2500 / (2 * I.G0), rtol=1e-12)
    check_true("decelerating level: P_s < 0", np.all(ps < 0))


def test_ballistics():
    r = I.ballistic_trajectory(1e12, 1000.0, 100.0)
    check("vacuum limit: range V √(2h/g)", r.impact_x, 100 * math.sqrt(2000 / I.G0), rtol=1e-4,
          source="projectile in vacuum")
    check("vacuum limit: fall time √(2h/g)", r.time_of_fall, math.sqrt(2000 / I.G0), rtol=1e-4)
    heavy = I.ballistic_trajectory(5000.0, 3000.0, 0.0, wind_cross=0.0)
    light = I.ballistic_trajectory(5.0, 3000.0, 0.0)
    check_true("light fragments fall slower", light.time_of_fall > heavy.time_of_fall)
    term = math.sqrt(2 * 5.0 * I.G0 / 1.225)
    check("terminal speed near the ground √(2 β g / ρ)", light.impact_speed, term, rtol=0.02)
    stiff = I.ballistic_trajectory(1.0, 3048.0, 128.6, wind_cross=20.0)
    check_true("light fast fragment stays stable (stiff drag): lands near terminal speed, drifts downwind",
               stiff.impact_speed < 30 and stiff.impact_y > 0 and abs(stiff.impact_x) < 500, stiff)
    fp = I.debris_footprint([2, 20, 200, 2000], 9000.0, 220.0, wind_cross=15.0)
    check_true("heavier lands further along track", np.all(np.diff(fp[:, 1]) > 0), fp[:, 1])
    check_true("lighter drifts further with the wind", np.all(np.diff(fp[:, 2]) < 0), fp[:, 2])


def test_locate_breakup_recovers_origin():
    betas = [3.0, 30.0, 300.0]
    fp = I.debris_footprint(betas, 8000.0, 200.0, 0.0, 0.0, 0.0)
    # track 090: along = east, right = south
    e = 1200.0 + fp[:, 1]
    n = -700.0 - fp[:, 2]
    oe, on, rms = I.locate_breakup(e, n, betas, 8000.0, 200.0, 90.0)
    check("break-up east", oe, 1200.0, atol=1e-6)
    check("break-up north", on, -700.0, atol=1e-6)
    check("zero residual for consistent data", rms, 0.0, atol=1e-6)


def test_search_and_impact():
    check("50 % radius = σ √(2 ln 2)", I.containment_radius(100.0, 0.5), 100 * math.sqrt(2 * math.log(2)),
          rtol=1e-12, source="Rayleigh median")
    dist, drift = I.glide_reach(3000.0, 15.0, 10.0, 60.0)
    check("glide h · L/D", dist, 45000.0, rtol=1e-12)
    check("drift = wind × glide time", drift, 10.0 * 45000 / 60, rtol=1e-12)
    check("40 m/s stopped in 2 m ≈ 40.8 g", I.mean_deceleration_g(40.0, 2.0), 1600 / (4 * I.G0), rtol=1e-12)


def test_events_and_hfacs():
    t = np.arange(0.0, 20.0, 1.0)
    vs = np.where((t >= 5) & (t <= 12), -7.0, -3.0)
    h = np.linspace(600, 0, t.size)
    ev = I.exceedance_events(t, {"vs": vs}, [("sink > 1200 fpm", "vs", lambda v: v < -6.1, 3.0)], h, (0, 500))
    check_true("one event inside the band", len(ev) == 1, ev)
    check_true("event starts once below 500 m", ev[0].t_start >= 5.0, ev)
    rows = I.hfacs_table({"Organisational climate": ["schedule pressure"], "Decision errors": ["pressed on"]})
    check_true("unsafe acts listed first", rows[0][0] == "Unsafe acts", rows)
    expect_error("unknown category", I.hfacs_table, {"Bad luck": ["x"]}, error=KeyError)


def test_ercs_score():
    # SAS43M-type wrong-surface take-off: everything up to the late recovery failed, the crew's reject stopped it
    failed = {b: "failed" for b in ("design", "tactical planning", "regulations and procedures",
                                    "situational awareness", "warning systems")}
    r = I.ercs_score("collision on runway", "X", {**failed, "late recovery": "stopped", "protections": "remaining"})
    check("weight sum 1 + 1", r.barrier_sum, 2)
    check("score ceil(2/2) = 1", r.barrier_score, 1)
    check_true("X1 is RED", r.code == "X1" and r.colour == "RED")
    check("X1 numerical equivalent 1e5", r.value, 1.0e5, rtol=1e-12)
    all_left = {b: "remaining" for b in I.ERCS_BARRIERS if b != "low energy"}
    full = I.ercs_score("excursion", "M", {**all_left, "low energy": "remaining"})
    check("all 18 weights → 9", full.barrier_score, 9)
    check_true("M9 is GREEN", full.colour == "GREEN")
    check("M2 (weight 3) numerical 1000", I.ercs_score("excursion", "M", {"regulations and procedures": "remaining"}).value,
          1000.0, rtol=1e-12)
    m3 = I.ercs_score("excursion", "M", {"design": "remaining"})
    check_true("design alone: ceil(5/2) = 3 → M3 YELLOW, 100", m3.code == "M3" and m3.colour == "YELLOW"
               and m3.value == 100.0)
    check_true("E1 YELLOW", I.ercs_score("ground damage", "E", {"protections": "stopped"}).colour == "YELLOW")
    check_true("A has no colour", I.ercs_score("security", "A", {}).colour == "none")
    expect_error("low-energy barrier only for low-energy areas", I.ercs_score, "terrain collision", "S",
                 {"low energy": "remaining"}, error=ValueError)
    expect_error("unknown barrier", I.ercs_score, "excursion", "M", {"luck": "stopped"}, error=KeyError)
    expect_error("unknown area", I.ercs_score, "bird", "M", {}, error=KeyError)


def test_takeoff_roll():
    a, r, s, tot = I.accelerate_stop_distance(127 * 0.514444, 2.0, 3.0, reaction_s=2.0)
    v = 127 * 0.514444
    check("accelerate v²/2a", a, v ** 2 / 4.0, rtol=1e-12)
    check("stop v²/2d", s, v ** 2 / 6.0, rtol=1e-12)
    check("total = sum", tot, a + r + s, rtol=1e-12)
    t = np.arange(0.0, 40.0, 0.5)
    good = 2.0 * t
    check_true("nominal acceleration: no alert", I.takeoff_acceleration_monitor(t, good, 2.0) is None)
    slow = 1.5 * t                                 # 75 % of expected (e.g. mass typed 25 % too low)
    alert = I.takeoff_acceleration_monitor(t, slow, 2.0)
    check_true("low acceleration flagged once above 15 m/s", alert is not None and 10.0 <= alert <= 11.0)
    expect_error("bad fraction", I.takeoff_acceleration_monitor, t, good, 2.0, fraction=1.5, error=ValueError)
