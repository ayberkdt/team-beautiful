"""Fused-navigation autoland with fault detection and exclusion (aerokit.autoland)."""
import math

import numpy as np

from aerokit import approach as A
from aerokit import autoland as L
from aerokit.verification import check, check_true, expect_error

RWY = A.Runway(51.0, 3.0, 10.0, 262.0)
SPOOF = {"gnss_ramp": (0.0, 0.0, -1.0), "gnss_ramp_start": 20.0}


def test_radar_jacobian_matches_finite_differences():
    p, site = np.array([2500.0, 40.0, 140.0]), (-300.0, 150.0, 2.0)
    h, H = L.radar_measurement(p, site)
    check("range", h[0], float(np.linalg.norm(p - np.array(site))), rtol=1e-12)
    num = np.zeros((3, 3))
    for j in range(3):
        e = np.zeros(3)
        e[j] = 1e-3
        num[:, j] = (L.radar_measurement(p + e, site)[0] - L.radar_measurement(p - e, site)[0]) / 2e-3
    check_true("analytic Jacobian = central differences", np.allclose(H, num, rtol=1e-5, atol=1e-10))
    expect_error("straight above the radar", L.radar_measurement, np.array(site), site, error=ValueError)


def test_flare_height_continuity():
    check("h_f = (V_s - sink_td) tau", L.flare_height(3.67, 3.0, 0.6), (3.67 - 0.6) * 3.0, rtol=1e-12)
    expect_error("touchdown sink above path sink", L.flare_height, 1.0, 3.0, 2.0, error=ValueError)


def test_nominal_autoland():
    r = L.simulate_autoland(RWY, rng=np.random.default_rng(1))
    err = np.sqrt(((r.est - r.true) ** 2).mean(axis=0))
    check_true(f"fused position error below 1 m rms per axis ({err.round(2)})", np.all(err < 1.0))
    check_true("no sensor excluded in a fault-free approach", r.excluded == {})
    check_true("touchdown inside the box", r.in_box)
    check_true("touchdown sink below 2 m/s (target 0.6 + sink lag)", 0.3 < r.touchdown_sink < 2.0)


def test_separation_fde_excludes_the_spoofed_gnss():
    r = L.simulate_autoland(RWY, L.FusionConfig(**SPOOF), rng=np.random.default_rng(1))
    check_true("only GNSS excluded", set(r.excluded) == {"gnss"})
    check_true("excluded within 10 s of the ramp start", 20.0 < r.excluded["gnss"] < 30.0)
    check_true("still lands inside the box", r.in_box)


def test_innovation_fde_is_scenario_dependent_separation_is_not():
    # innovation gating: from 6 km the drifting precise source drags the estimate and the honest sensors are
    # excluded (no landing); from 4 km it happens to exclude the GNSS. Separation excludes the GNSS from both.
    inn = L.FusionConfig(**SPOOF, fde_mode="innovation")
    r6 = L.simulate_autoland(RWY, inn, L.AutolandConfig(x0=6000.0), np.random.default_rng(1))
    check_true("6 km, innovation: an honest sensor is excluded", bool({"baro", "radar", "radalt"} & set(r6.excluded)))
    check_true("6 km, innovation: the spoofed GNSS is kept and there is no touchdown",
               "gnss" not in r6.excluded and math.isnan(r6.touchdown_x))
    r4 = L.simulate_autoland(RWY, inn, L.AutolandConfig(x0=4000.0), np.random.default_rng(1))
    check_true("4 km, innovation: GNSS excluded this time", set(r4.excluded) == {"gnss"})
    sep = L.FusionConfig(**SPOOF)
    r4s = L.simulate_autoland(RWY, sep, L.AutolandConfig(x0=4000.0), np.random.default_rng(1))
    check_true("4 km, separation: GNSS excluded, lands in the box", set(r4s.excluded) == {"gnss"} and r4s.in_box)
    expect_error("unknown mode", L.simulate_autoland, RWY, L.FusionConfig(fde_mode="vote"), error=ValueError)


def test_cold_baro_bias_learned_without_gnss():
    r = L.simulate_autoland(RWY, L.FusionConfig(gnss_sigma=None, baro_bias=6.4), rng=np.random.default_rng(1))
    check("baro bias estimated from radar + radio altimeter", r.baro_bias_est, 6.4, atol=1.0)
    check_true("lands in the box with no GNSS at all", r.in_box)


def test_monte_carlo_no_false_alarms():
    mc = L.monte_carlo_autoland(RWY, L.FusionConfig(),
                                L.AutolandConfig(wind_speed=10.0, wind_from_rel_deg=40.0, gust_sigma=2.0), runs=8, seed=3)
    check("every run lands in the box", mc["in_box_share"], 1.0)
    check_true("no exclusions fault-free", all(mc[f"excluded_{k}_share"] == 0 for k in ("gnss", "radar", "baro")))
    check_true("touchdown spread finite", math.isfinite(mc["touchdown_sigma_m"]))
