"""Approach guidance panel: needles from the valid source, annunciations instead of guesses."""
from aerokit.approach import Runway, glide_path_height
from aerokit.atc.guidance import GuidancePanel, SourceReading

RWY = Runway(51.0, 4.0, 10.0, 250.0)


def on_path(name, t, x, dz=0.0, dy=0.0, pl=None):
    return SourceReading(name, t, x, dy, float(glide_path_height(RWY, x)) + dz, pl)


def test_centred_on_path_and_clearance_required():
    p = GuidancePanel(RWY, "25R")
    p.receive(on_path("GND PAR uplink", 0.0, 5000))
    v = p.view(0.5, cleared_runway=None)
    assert abs(v["vert_dots"]) < 0.01 and abs(v["lat_dots"]) < 0.01
    assert "NO APPROACH CLEARANCE" in v["annunciations"]
    assert "RWY MISMATCH: cleared 25L, selected 25R" in p.view(0.5, "25L")["annunciations"]
    assert not [a for a in p.view(0.5, "25R")["annunciations"] if "CLEARANCE" in a or "MISMATCH" in a]


def test_stale_ground_source_falls_back_and_is_annunciated():
    p = GuidancePanel(RWY, "25R")
    p.receive(on_path("GND PAR uplink", 0.0, 5000, dz=20.0))
    p.receive(on_path("ON-BOARD", 6.0, 4800, dz=0.0, pl=10.0))
    v = p.view(6.0, "25R")
    assert v["source"] == "ON-BOARD" and any(a.startswith("GND GUIDANCE LOST") for a in v["annunciations"])


def test_no_valid_source_removes_needles_never_centres():
    p = GuidancePanel(RWY, "25R")
    p.receive(on_path("GND PAR uplink", 0.0, 5000))
    p.receive(on_path("ON-BOARD", 10.0, 4500, pl=80.0))               # PL above the 35 m alert limit
    v = p.view(10.0, "25R")
    assert v["vert_dots"] is None and v["lat_dots"] is None
    assert "V FLAG" in v["annunciations"] and "L FLAG" in v["annunciations"]
    assert any(a.startswith("NAV INTEGRITY") for a in v["annunciations"])


def test_disagreement_uses_ground_source_and_shows_true_deviation():
    p = GuidancePanel(RWY, "25R")
    p.receive(on_path("GND PAR uplink", 0.0, 4000, dz=25.0))           # ground radar: aircraft is 25 m high
    p.receive(on_path("ON-BOARD", 0.0, 4000, dz=0.0, dy=-40.0, pl=10.0))  # biased on-board: 'on path'
    v = p.view(0.5, "25R")
    assert v["source"] == "GND PAR uplink" and v["vert_dots"] > 0.5
    assert any(a.startswith("SOURCES DISAGREE") for a in v["annunciations"])


def test_minimums_latches():
    p = GuidancePanel(RWY, "25R")
    p.receive(on_path("GND PAR uplink", 0.0, 900, dz=-5.0))             # ~50 m height: below 200 ft
    assert p.view(0.1, "25R")["minimums"]
    p.receive(on_path("GND PAR uplink", 1.0, 1300, dz=10.0))            # noisy reading back above DH
    assert p.view(1.1, "25R")["minimums"]
