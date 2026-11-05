"""Approach geometry, wind triangle, cold-temperature error, stabilised criteria and the simulator."""
import math

import numpy as np

from aerokit import approach as A
from aerokit.verification import check, check_true, expect_error

FSF = "FSF ALAR Briefing Note 7.1 (read 2026-11-03)"
RWY = A.Runway(51.0, 3.0, 10.0, 262.0)


def test_runway_frame_round_trip_and_path():
    lat, lon, h = RWY.from_runway(5000.0, 120.0, 300.0)
    x, y, z = RWY.to_runway(lat, lon, h)
    check("x round trip", float(x), 5000.0, atol=1e-6)
    check("y round trip", float(y), 120.0, atol=1e-6)
    check("z round trip", float(z), 300.0, atol=1e-6)
    check("TCH at the threshold", float(A.glide_path_height(RWY, 0.0)), 15.24, rtol=1e-12)
    check("3° path at 1 NM", float(A.glide_path_height(RWY, 1852.0)), 15.24 + 1852 * math.tan(math.radians(3)),
          rtol=1e-12)
    check("GPIP = −TCH / tan γ", RWY.gpip, -15.24 / math.tan(math.radians(3)), rtol=1e-12)


def test_deviations():
    d = A.deviation(RWY, 4000.0, 0.0, float(A.glide_path_height(RWY, 4000.0)))
    check("on path: zero angular deviation", float(d.vertical_angle_deg), 0.0, atol=1e-12)
    d = A.deviation(RWY, 4000.0, 50.0, float(A.glide_path_height(RWY, 4000.0)) + 20.0)
    check("linear vertical deviation", float(d.vertical_m), 20.0, rtol=1e-12)
    check("angular lateral from the localizer",
          float(d.lateral_angle_deg), math.degrees(math.atan2(50, 4000 + 2500 + 300)), rtol=1e-12)
    check("dots clip at full scale", float(A.to_dots(3.0, 1.0)), 2.0, rtol=1e-12)


def test_wind_and_descent():
    crab, gs, head = A.wind_triangle(70.0, 262.0, 262.0, 10.0)
    check("pure headwind: no crab", crab, 0.0, atol=1e-12)
    check("GS = TAS − headwind", gs, 60.0, rtol=1e-12)
    crab, gs, _ = A.wind_triangle(70.0, 0.0, 90.0, 10.0)
    check("crosswind from the right: crab asin(w/V)", crab, math.degrees(math.asin(10 / 70)), rtol=1e-12)
    check("3° descent rate at 140 kt ≈ 743 fpm (GS × tan 3°)", A.descent_rate(140 * A.KT, 3.0) / A.FPM,
          140 * 6076.12 / 60 * math.tan(math.radians(3)), rtol=1e-4)
    check("CDA distance from 3000 ft at 3°", A.distance_for_descent(3000 * A.FT, 3.0) / 1852,
          3000 * 0.3048 / math.tan(math.radians(3)) / 1852, rtol=1e-12)
    expect_error("crosswind above TAS", A.wind_triangle, 10.0, 0.0, 90.0, 20.0, error=ValueError)


def test_cold_temperature():
    check("ISA column: true = indicated", A.cold_temperature_true_height(300.0, 0.0, 0.0), 300.0, rtol=1e-12)
    low = A.cold_temperature_true_height(1000 * A.FT, 0.0, -30.0)
    check("−30 K near sea level ≈ 1 − 30/287 of the height", low / (1000 * A.FT), 1 - 30 / 287.2, rtol=2e-3)
    check_true("warm air: higher than indicated", A.cold_temperature_true_height(300.0, 0.0, 15.0) > 300.0)


def test_stability_gate():
    c = A.StabilityCriteria()
    check("speed window VREF … VREF + 20 kt", c.speed_high / A.KT, 20.0, rtol=1e-12, source=FSF)
    check("gate 1000 ft", c.gate_height / A.FT, 1000.0, rtol=1e-12, source=FSF)
    h = np.array([1500, 900, 600, 300]) * A.FT
    v = A.stability_violations(h, [30 * A.KT, 5 * A.KT, 25 * A.KT, 5 * A.KT], [1200 * A.FPM, 800 * A.FPM,
                               800 * A.FPM, 1100 * A.FPM], [0, 0.5, 0, 1.5], [0, 0, 0, 0])
    reasons = [r for _, r in v]
    check_true("above the gate ignored", all(i > 0 for i, _ in v), v)
    check_true("speed at 600 ft flagged", any("VREF+25" in r for r in reasons), reasons)
    check_true("sink and 1.5 dot at 300 ft flagged", sum(i == 3 for i, _ in v) == 2, v)


def test_simulator_converges_and_sensor_bias_shows():
    cfg = A.ApproachSimConfig(x0=8000.0, y0=150.0, z0_above_path=60.0, wind_from_rel_deg=40.0, wind_speed=10.0)
    run = A.simulate_approach(RWY, A.NavSensor("perfect"), cfg, np.random.default_rng(0))
    dv, dl = run.at_height(200 * A.FT)
    check_true("perfect nav: within 2 m vertically at 200 ft", abs(dv) < 2.0, dv)
    check_true("perfect nav: within 1 m laterally in a crosswind", abs(dl) < 1.0, dl)
    stats = A.monte_carlo_approach(RWY, [A.NavSensor("biased", bias=(0.0, 0.0, 15.0))], runs=3, cfg=cfg)
    check("a +15 m sensed-height bias puts the aircraft ~15 m low", stats["biased"]["vertical_mean"], -15.0,
          atol=2.0)


def test_integrity_factors():
    check("SBAS K_v = 5.33 at 1e-7 (Rippl & Perea 2018)", A.k_factor(1e-7), 5.33, rtol=2e-3)
    check("PL = K sigma", A.protection_level(2.0), 2.0 * A.k_factor(1e-7), rtol=1e-12)
    check("threshold sqrt(sa^2+sb^2)", A.separation_threshold(3.0, 4.0, 0.05), 5.0 * 1.959964, rtol=1e-5)
    check("fault bound T + Q^-1(1e-3) sigma", A.fault_bound(10.0, 1.0, 1e-3), 10.0 + 3.090232, rtol=1e-5)
    check_true("LPV-200 VAL 35 m", A.ALERT_LIMITS["LPV-200"] == (40.0, 35.0))
    expect_error("risk out of range", A.k_factor, 1.5, error=ValueError)


def test_rf_physics():
    # 250 W reply at 1090 MHz over 10 km, 0 dBi both ends: Pt (lambda/4 pi R)^2
    lam = 299_792_458.0 / 1090e6
    check("Friis by hand", A.friis_received_power(250.0, 0.0, 0.0, 1090e6, 10e3), 250 * (lam / (4 * math.pi * 1e4)) ** 2,
          rtol=1e-12)
    check("kTB at 1 MHz, NF 0 dB", A.thermal_noise_power(1e6, 0.0), 1.380649e-23 * 290 * 1e6, rtol=1e-12)
    check("monopulse 1 deg, 20 dB → 0.044 deg", A.monopulse_angle_sigma(1.0, 100.0), 1 / (1.6 * math.sqrt(200)), rtol=1e-12)


def test_spoofing_ramp_is_detected_and_excluded():
    cfg = A.ApproachSimConfig(x0=6000.0)
    spoofed = A.NavSensor("gnss", sigma=(1.0, 1.0, 1.5), tau=5.0, ramp=(0.0, 0.0, -1.0), ramp_start=20.0)
    radar = A.NavSensor("radar", sigma=(3.0, 2.0, 2.0), tau=2.0)
    thr = tuple(A.separation_threshold(a, b, 1e-5) for a, b in zip((1.0, 1.0, 1.5), (3.0, 2.0, 2.0), strict=True))
    blind = A.simulate_approach(RWY, spoofed, cfg, np.random.default_rng(3))
    guarded = A.simulate_approach(RWY, spoofed, cfg, np.random.default_rng(3), monitor=radar, threshold=thr)
    check_true("unmonitored: the ramp keeps the aircraft high past the GPIP (sensed low → climbs)",
               blind.vertical_dev[-1] > 40.0 and blind.z.min() > 61.0)
    check_true("monitor alarms after the ramp starts", guarded.extra["alarm_t"] > 20.0)
    check_true("undetected error stays under the vertical threshold + noise",
               guarded.extra["undetected_error"] < thr[2] + 3 * 1.5)
    check_true("after exclusion the aircraft is back near the path at 200 ft", abs(guarded.at_height(61.0)[0]) < 8.0)
    expect_error("monitor without threshold", A.simulate_approach, RWY, spoofed, cfg, None, radar, error=ValueError)
