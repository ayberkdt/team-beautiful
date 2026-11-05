"""PSR processing chains: CFAR false-alarm rate, MTI nulls, MTD and clutter map behaviour on a small grid."""
import math

import numpy as np
import pytest
from scipy import stats

from aerokit.atc import psr_processing as pp

SMALL = pp.PsrGrid(n_range=120, n_az=24)


def test_cfar_alpha_matches_f_quantile_and_monte_carlo():
    pfa, n = 1e-3, 16
    a = pp.cfar_alpha(pfa, n)
    assert a == pytest.approx(stats.f.isf(pfa, 2, 2 * n), rel=1e-9)
    rng = np.random.default_rng(0)
    p = rng.exponential(1.0, (20000, 50))
    det = pp.ca_cfar(p, pfa=pfa, n_ref=n, n_guard=2)
    assert det[20:-20].mean() == pytest.approx(pfa, rel=0.25)


def test_cfar_multi_look_false_alarm_rate():
    pfa, looks = 1e-3, 4
    rng = np.random.default_rng(1)
    p = rng.gamma(looks, 1.0 / looks, (20000, 50))
    det = pp.ca_cfar(p, pfa=pfa, looks=looks)
    assert det[20:-20].mean() == pytest.approx(pfa, rel=0.3)


def test_mti_nulls_zero_doppler_and_blind_speed():
    g = SMALL
    n = np.arange(g.n_pulses)

    def gain(v):
        fd = 2 * v / g.wavelength
        x = np.exp(1j * 2 * np.pi * fd * n / g.prf_hz)
        return float(np.mean(np.abs(pp.mti3(x)) ** 2) / 6.0)
    vb = pp.blind_speed(g)
    assert vb == pytest.approx(g.wavelength * g.prf_hz / 2)
    assert gain(0.0) < 1e-12 and gain(vb) < 1e-9
    assert gain(vb / 2) > 1.0                       # mid-band target passes with gain


def test_clutter_map_removes_persistent_clutter_keeps_moving_target():
    g = SMALL
    scene = pp.ClutterScene(terrain_box=(1.0, 10.0, 0.0, 360.0), terrain_fraction=0.5, windfarm_cells=((90, 5),))
    rng = np.random.default_rng(3)
    cm = pp.ClutterMap()
    for _ in range(6):
        pp.process_scan(pp.synthesize_scan(g, scene, [], rng), g, "mtd_cmap", cm)
    fa = {c: 0 for c in pp.CHAINS}
    hits = {c: 0 for c in pp.CHAINS}
    for k in range(6):
        e = pp.Echo(6 * 1852, 45 + 15 * k, 90.0, 30.0)      # moving target over terrain, new cell each scan
        z = pp.synthesize_scan(g, scene, [e], rng)
        for c in pp.CHAINS:
            d = pp.process_scan(z, g, c, cm if c == "mtd_cmap" else None)
            near = [abs(x.range_m - e.range_m) < 400 and abs((x.az_deg - e.az_deg + 180) % 360 - 180) < 16 for x in d]
            hits[c] += any(near)
            fa[c] += len(d) - sum(near)
    assert fa["mtd_cmap"] < fa["fixed"] / 10
    assert fa["mtd_cmap"] < fa["mtd"]
    assert hits["mtd_cmap"] >= 3 and hits["mtd"] >= 3


def test_mtd_notch_hides_tangential_target_clutter_map_does_not():
    g = SMALL
    scene = pp.ClutterScene(terrain_fraction=0.0, windfarm_cells=())
    rng = np.random.default_rng(5)
    cm = pp.ClutterMap()
    for _ in range(4):
        pp.process_scan(pp.synthesize_scan(g, scene, [], rng), g, "mtd_cmap", cm)
    hit = {"mtd": 0, "mtd_cmap": 0}
    for k in range(6):
        e = pp.Echo(8 * 1852, 30 + 15 * k, 0.0, 40.0)          # zero radial speed, moving across cells
        z = pp.synthesize_scan(g, scene, [e], rng)
        for c in hit:
            d = pp.process_scan(z, g, c, cm if c == "mtd_cmap" else None)
            hit[c] += any(abs(x.range_m - e.range_m) < 400 for x in d)
    assert hit["mtd"] == 0 and hit["mtd_cmap"] >= 4
