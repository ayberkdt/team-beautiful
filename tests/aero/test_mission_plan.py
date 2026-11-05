"""Leg-2 mission plan on top of the sizing pipeline."""
import json

import pytest

from aerokit.data import example_path
from aerokit.design.mission_plan import load_mission, map_figure, plan, write_outputs
from aerokit.design.requirements import load_assumptions, load_requirements
from aerokit.design.sizing import size
from aerokit.units import UnitError
from aerokit.verification import check, check_true

MISSION = example_path("design", "ansys_2023_mission.json")
REQ = example_path("design", "ansys_2023_requirements.json")


@pytest.fixture(scope="module")
def sized():
    return size(load_requirements(REQ), load_assumptions())


def test_mission_plan_rehearsal(sized, tmp_path):
    mp = plan(sized.aircraft, load_mission(MISSION))
    check("swath = 2 h tan(30°)", mp.swath, 2 * 1500 * 3 ** -0.5, rtol=1e-12, source="nadir imager geometry")
    check("area of the 50 km × 50 km square", mp.area_km2, 2500.0, rtol=1e-3, source="geometry")
    check_true("fuel-limited: the full pattern does not fit", not mp.full_pattern_fits)
    check_true("time on station between 5 and 7 h", 5 * 3600 < mp.time_on_station < 7 * 3600,
               f"{mp.time_on_station / 3600:.2f} h")
    check("fuel used = all usable fuel (reserve flown)", mp.result.fuel_used, sized.aircraft.W_fuel, rtol=1e-3)
    check_true("route starts and ends at the base", mp.route_names[0] == mp.route_names[-1] == "BASE")
    files = write_outputs(sized.aircraft, mp, tmp_path)
    check_true("waypoints and Aviator sheet written", len(files) == 5, files)
    gj = json.loads((tmp_path / "waypoints.geojson").read_text(encoding="utf-8"))
    check_true("GeoJSON parses and has the route", "features" in gj and len(gj["features"]) > 2)
    fig = map_figure(mp, str(tmp_path / "map"))
    check("mission map audit 0 errors", fig.report.errors, 0)


@pytest.mark.parametrize("bad", [{"base": [99, 0]}, {"base": [39, 30], "area_width": "50 km"},
                                 {"base": [39, 30], "areaa_width": "50 km"},
                                 {"base": [39, 30], "area_center": [39, 31], "area_width": "50 km/h"}])
def test_mission_file_validation(bad):
    with pytest.raises((UnitError, ValueError)):
        load_mission(bad)
