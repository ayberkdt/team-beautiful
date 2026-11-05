"""Scenario: the 2023 rehearsal aircraft searching a 50 km × 50 km area 400 km from base.

Assumptions (stated, not from the challenge card): base at 39.0 N 30.0 E, area centre 400 km due
east along the geodesic, parallel-track search at 1500 m with tracks north-south, 60° FOV nadir
imager, 10 % overlap, best-endurance search speed (≥ 1.2 V_stall), best-range transit, 30-min reserve
loiter, default taxi/take-off allowance, no wind. The numbers are printed (run with ``-s``).
"""
from __future__ import annotations

import math

import pytest

from aerokit.aero.aircraft import G0, Aircraft
from aerokit.aero.propulsion import Turboprop
from aerokit.mission.coverage import pattern_coverage
from aerokit.mission.geodesy import LocalFrame, direct, inverse
from aerokit.mission.patterns import parallel_track, sensor_swath, track_spacing
from aerokit.mission.simulate import FuelExhaustedError, max_time_on_station, search_mission


def test_rehearsal_aircraft_50km_area_400km_away():
    ac = Aircraft("rehearsal", 5974 * G0, 27.5, 9, 0.0280, 0.783, Turboprop(1667e3), W_fuel=0.156 * 5974 * G0)
    base = (39.0, 30.0)
    la, lo, _ = direct(*base, 90.0, 400e3)
    assert inverse(*base, la, lo).distance == pytest.approx(400e3, abs=1e-3)
    swath = sensor_swath("1500 m", "60 deg")
    S = track_spacing("1500 m", "60 deg", "10 %")
    pat = parallel_track("50 km", "50 km", S, frame=LocalFrame(la, lo))
    assert pat.n_legs + 1 == 2 * math.ceil(50e3 / S)

    T, res = max_time_on_station(ac, base, pat, 1500.0, dt=10.0)
    cov = pattern_coverage(pat, swath, distance=res.search_distance)
    full = pattern_coverage(pat, swath)
    with pytest.raises(FuelExhaustedError):
        search_mission(ac, base, pat, 1500.0, dt=10.0)          # the whole pattern does not fit

    print("\n" + res.timeline().to_text())
    print(f"swath {swath:.1f} m, spacing {S:.1f} m, {math.ceil(50e3 / S)} tracks, pattern {pat.length / 1e3:.1f} km")
    print(f"time on station {T / 3600:.2f} h, searched {res.search_distance / 1e3:.1f} km, "
          f"coverage {100 * cov.fraction:.1f} % (full pattern {100 * full.fraction:.1f} %), "
          f"fuel used {res.fuel_used / G0:.1f} kg of {ac.W_fuel / G0:.1f} kg, margin {res.fuel_margin / G0:.2f} kg")
    assert full.fraction == pytest.approx(1.0)
    assert 0.0 <= res.fuel_margin < 0.5 * G0
    assert 4.0 * 3600 < T < 8.0 * 3600
    assert 0.5 < cov.fraction < 1.0
