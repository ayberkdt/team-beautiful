"""Tracker: polar covariance, alpha-beta, Kalman consistency, M-of-N, coasting, identity gating."""
import math

import numpy as np
import pytest

from aerokit.atc.tracker import AlphaBeta, CvKalman, Plot, Tracker, polar_to_plot


def test_polar_covariance_cross_range_grows():
    p = polar_to_plot(0, 60 * 1852, 90.0, 50.0, 0.05)
    cov = np.array(p.cov)
    assert math.sqrt(cov[1, 1]) == pytest.approx(60 * 1852 * math.radians(0.05), rel=1e-6)   # cross-range = north
    assert math.sqrt(cov[0, 0]) == pytest.approx(50.0, rel=1e-6)


def test_alpha_beta_converges_on_straight_line():
    ab = AlphaBeta((0, 0), 0.0)
    for k in range(1, 40):
        ab.update((100.0 * k * 4, 0.0), 4.0 * k)
    assert ab.vel[0] == pytest.approx(100.0, rel=0.02)


def test_kalman_nees_consistent():
    rng = np.random.default_rng(0)
    nees = []
    for run in range(60):
        x, y, vx, vy = 0.0, 0.0, 120.0, -60.0
        sig = 60.0
        kf = None
        for k in range(30):
            t = 4.0 * k
            z = (x + vx * t + rng.normal(0, sig), y + vy * t + rng.normal(0, sig))
            pl = Plot(t, z, ((sig ** 2, 0), (0, sig ** 2)))
            if kf is None:
                kf = CvKalman(pl, q=0.01)
            else:
                kf.update(pl)
        e = kf.x - np.array([x + vx * t, y + vy * t, vx, vy])
        nees.append(e @ np.linalg.solve(kf.P, e))
    assert 2.5 < float(np.mean(nees)) < 6.0          # 4 states -> mean NEES ~ 4


def test_track_management_and_identity():
    tr = Tracker()
    for k in range(4):
        t = 4.0 * k
        tr.scan([Plot(t, (1000 + 200 * t, 0), ((900, 0), (0, 900)), "ADS-B", "ABC123"),
                 Plot(t, (1000 + 200 * t + 50, 30), ((900, 0), (0, 900)), "ADS-B", "DEF456")])
    live = tr.scan([])
    ids = {t.ident: t.status for t in live}
    assert ids == {"ABC123": "COASTING", "DEF456": "COASTING"}
    for k in range(5, 9):
        live = tr.scan([])
    assert live == []


def test_clutter_does_not_confirm():
    rng = np.random.default_rng(1)
    tr = Tracker()
    for k in range(10):
        plots = [Plot(4.0 * k, tuple(rng.uniform(-50_000, 50_000, 2)), ((2500, 0), (0, 2500)))]
        tr.scan(plots)
    assert not [t for t in tr.tracks if t.status == "CONFIRMED"]

def test_imm_follows_turn_better_than_cv():
    from aerokit.atc.tracker import ImmCv
    rng = np.random.default_rng(5)
    errs = {"cv": [], "imm": []}
    v, w = 113.0, math.radians(1.5)
    for run in range(20):
        filt = {}
        for k in range(45):
            t = 4.8 * k
            if t < 60:
                x, y = v * t, 0.0
            else:
                tt = t - 60
                ang = min(w * tt, math.pi / 2)
                x = v * 60 + v / w * math.sin(ang) + (v * (tt - ang / w) if ang >= math.pi / 2 else 0)
                y = -v / w * (1 - math.cos(ang))
            z = Plot(t, (x + rng.normal(0, 40), y + rng.normal(0, 40)), ((1600, 0), (0, 1600)))
            if not filt:
                filt = {"cv": CvKalman(z, q=0.5), "imm": ImmCv(z)}
            else:
                for f in filt.values():
                    f.update(z)
            if 70 < t < 100:
                for name, f in filt.items():
                    errs[name].append(math.hypot(f.x[0] - x, f.x[1] - y))
    assert np.mean(errs["imm"]) < 0.8 * np.mean(errs["cv"])
