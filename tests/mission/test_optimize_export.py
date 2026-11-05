"""Optimiser (grid + refine, Pareto) and STK hand-off files (CSV, KML, GeoJSON, Aviator sheet)."""
from __future__ import annotations

import csv
import io
import json
import math
import os
import xml.etree.ElementTree as ET

import numpy as np
import pytest

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.performance import (best_climb_speed, best_endurance_speed, best_range_speed, max_rate_of_climb,
                                      rate_of_climb)
from aerokit.aero.propulsion import Turboprop
from aerokit.mission import export as X
from aerokit.mission.geodesy import LocalFrame, direct
from aerokit.mission.optimize import optimize_search, pareto_front
from aerokit.mission.patterns import parallel_track
from aerokit.output.writers import UnsafePathError


@pytest.fixture(scope="module")
def ac():
    return Aircraft("rehearsal", 5974 * G0, 27.5, 9, 0.0280, 0.783, Turboprop(1667e3), W_fuel=0.156 * 5974 * G0)


@pytest.fixture(scope="module")
def route():
    fr = LocalFrame(39.0, 34.6)
    p = parallel_track("10 km", "8 km", "2 km", orientation="20 deg", frame=fr)
    lat, lon = p.geodetic()
    return lat, lon


def test_optimizer_grid_refine_and_pareto(ac):
    base = (39.0, 30.0)
    center = direct(*base, 90.0, 400e3)[:2]
    r = optimize_search(ac, base, center, 50e3, 50e3, math.radians(60), altitudes=(1000.0, 2000.0),
                        speed_factors=(1.0, 1.2), overlaps=(0.0, 0.2), dt=60.0)
    feas = [c for c in r.candidates if c.feasible]
    assert r.best.feasible and len(r.candidates) > 8
    assert r.best.covered_area >= max(c.covered_area for c in feas) - 1e-6
    for c in feas:
        assert c.spacing == pytest.approx(2 * c.altitude * math.tan(math.radians(30)) * (1 - c.overlap))
        assert 0.0 <= c.coverage <= 1.0 + 1e-12 and c.fuel_margin >= -1e-6
    # Pareto: sorted by fuel, coverage strictly increasing, nothing dominates a member
    for a, b in zip(r.pareto[:-1], r.pareto[1:], strict=True):
        assert a.fuel_used <= b.fuel_used and a.coverage < b.coverage
    for m in r.pareto:
        assert not any(c.fuel_used < m.fuel_used and c.coverage > m.coverage + 1e-9 for c in feas)
    assert pareto_front(r.candidates) == r.pareto
    assert "Pareto" in r.pareto_table().title and r.table().rows
    with pytest.raises(ValueError):
        optimize_search(ac, base, center, 50e3, 50e3, 1.0, altitudes=(1000.0,), max_altitude=500.0)


def test_kml_parses_back_with_same_coordinates(route):
    lat, lon = route
    text = X.waypoints_kml(lat, lon, 1500.0)
    root = ET.fromstring(text.encode("utf-8"))
    ns = {"k": X.KML_NS}
    assert root.tag == f"{{{X.KML_NS}}}kml"
    line = root.find(".//k:LineString/k:coordinates", ns).text.split()
    got = np.array([[float(v) for v in t.split(",")] for t in line])
    assert np.allclose(got[:, 0], lon, atol=1e-9) and np.allclose(got[:, 1], lat, atol=1e-9)
    assert np.allclose(got[:, 2], 1500.0)
    pts = root.findall(".//k:Point/k:coordinates", ns)
    assert len(pts) == len(lat)
    names = [e.text for e in root.findall("./k:Document/k:Placemark/k:name", ns)]
    assert names[0] == "route" and names[1] == "WP001"


def test_kml_escapes_names():
    text = X.waypoints_kml([1.0], [2.0], names=["<a & b>"])
    root = ET.fromstring(text)
    assert any(e.text == "<a & b>" for e in root.iter(f"{{{X.KML_NS}}}name"))


def test_geojson_and_csv_parse_back(route):
    lat, lon = route
    g = json.loads(X.waypoints_geojson(lat, lon, 1500.0))
    assert g["type"] == "FeatureCollection"
    coords = np.array(g["features"][0]["geometry"]["coordinates"])
    assert g["features"][0]["geometry"]["type"] == "LineString"
    assert np.array_equal(coords[:, 0], lon) and np.array_equal(coords[:, 1], lat)
    assert [f["geometry"]["coordinates"] for f in g["features"][1:]] == coords.tolist()
    rows = list(csv.DictReader(io.StringIO(X.waypoints_csv(lat, lon, 1500.0))))
    assert len(rows) == len(lat)
    assert np.allclose([float(r["lat_deg"]) for r in rows], lat, atol=1e-9)
    with pytest.raises(ValueError):
        X.waypoints_csv([91.0], [0.0])


def test_write_waypoints_atomic(tmp_path, route, monkeypatch):
    lat, lon = route
    paths = X.write_waypoints(tmp_path / "route", lat, lon, 1500.0, base_dir=tmp_path)
    assert sorted(os.path.basename(p) for p in paths) == ["route.csv", "route.geojson", "route.kml"]
    ET.parse(paths[1])
    before = (tmp_path / "route.kml").read_bytes()
    # a crash during the replace leaves the old file intact and no temporary file behind
    import aerokit.output.writers as W

    def boom(src, dst):
        raise OSError("simulated crash")
    monkeypatch.setattr(W.os, "replace", boom)
    with pytest.raises(OSError):
        X.write_waypoints(tmp_path / "route", lat[:2], lon[:2], 0.0, base_dir=tmp_path)
    monkeypatch.undo()
    assert (tmp_path / "route.kml").read_bytes() == before
    assert not [p for p in os.listdir(tmp_path) if p.endswith(".tmp")]
    with pytest.raises(UnsafePathError):
        X.write_waypoints(tmp_path / ".." / "escape", lat, lon, base_dir=tmp_path)


def test_aviator_sheet_equals_performance_outputs(ac, tmp_path):
    s = X.aviator_sheet(ac, altitudes=[0.0, 1500.0, 5000.0])
    W0 = ac.W0
    for h in (0.0, 1500.0, 5000.0):
        V = best_climb_speed(ac, h, W0)
        assert s.get("climb", "speed", h) == V
        assert s.get("climb", "rate", h) == rate_of_climb(ac, V, h, W0)
        assert s.get("limits", "stall_speed", h) == ac.stall_speed(h, W0)
        vmax = s.get("limits", "max_speed", h)
        assert abs(ac.power_available(vmax, h) - ac.power_required(vmax, h, W0)) < 1.0
    m0 = W0 / G0
    for h in (0.0,):
        assert s.get("cruise", "speed", h, m0) == best_range_speed(ac, h, W0)
        assert s.get("cruise", "fuel_flow", h, m0) == ac.fuel_flow(best_range_speed(ac, h, W0), h, W0) / G0
        assert s.get("loiter", "speed", h, m0) == best_endurance_speed(ac, h, W0)
    hs = s.get("ceilings", "service_ceiling")
    assert max_rate_of_climb(ac, hs, W0) == pytest.approx(100 * 0.3048 / 60, abs=2e-3)
    assert abs(max_rate_of_climb(ac, s.get("ceilings", "absolute_ceiling"), W0)) < 2e-3
    assert s.get("takeoff_landing", "liftoff_speed") == pytest.approx(1.1 * ac.stall_speed(0.0, W0, ac.CLmax_takeoff))
    assert "NOT verified" in s.markdown and "Climb at best rate of climb" in s.markdown
    rows = list(csv.DictReader(io.StringIO(s.csv)))
    assert len(rows) == len(s.values)
    assert all(float(r["value"]) == v.value or math.isnan(v.value) for r, v in zip(rows, s.values, strict=True))
    paths = X.write_aviator_sheet(tmp_path / "aviator", s, base_dir=tmp_path)
    assert [os.path.basename(p) for p in paths] == ["aviator.md", "aviator.csv"]
    with pytest.raises(KeyError):
        s.get("climb", "nonexistent")
