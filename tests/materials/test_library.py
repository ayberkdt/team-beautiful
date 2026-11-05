"""Material catalogue and its link to the MIL-HDBK-5J allowables."""
from __future__ import annotations

import pytest

from aerokit.materials import handbook, library


def test_find_is_forgiving_and_strict():
    assert library.find("7075-t6") is library.find("7075 T6") is library.find("7075_T6")
    for bad in ("", "   ", "unobtainium"):
        with pytest.raises(KeyError):
            library.find(bad)


@pytest.mark.parametrize("name", list(library.MATERIALS))
def test_records_are_complete_and_sourced(name):
    r = library.MATERIALS[name]
    assert r["source"] and isinstance(r["unverified"], list)
    assert r["rho"] > 0
    if "E1" in r:
        assert r["Xt"] > r["Yt"] > 0
    else:
        assert 0 < r["Fty"] <= r["Ftu"] and 0 < r["nu"] < 0.5


@pytest.mark.parametrize("name, thickness", [("7075-T6", 2e-3), ("6061-T6", 3e-3), ("2024-T351", 20e-3),
                                             ("Ti-6Al-4V", 2e-3)])
def test_design_values_equal_handbook(name, thickness):
    d = library.design_values(name, "A", "L", thickness=thickness)
    slug = library.HANDBOOK_SLUG[name]
    for prop in ("Ftu", "Fty"):
        assert d[prop] == handbook.get_allowable(slug, prop, "A", "L", thickness)
    assert "MIL-HDBK-5J Table" in d["source"]
    assert d["Fty"] <= d["Ftu"]


@pytest.mark.parametrize("name", ["7075-T6", "6061-T6"])
def test_a_basis_not_above_typical(name):
    """Design allowables must not exceed AA typical strength (MPa rounding tolerance 1 MPa)."""
    d, typ = library.design_values(name, "A", "L", thickness=2e-3), library.find(name)
    assert d["Ftu"] <= typ["Ftu"] + 1e6 and d["Fty"] <= typ["Fty"] + 1e6


def test_a_not_above_b():
    a = library.design_values("7075-T6", "A", "L", thickness=2e-3)
    b = library.design_values("7075-T6", "B", "L", thickness=2e-3)
    assert a["Ftu"] <= b["Ftu"] and a["Fty"] <= b["Fty"]


def test_design_values_errors():
    with pytest.raises(KeyError):
        library.design_values("PLA-baski")
    with pytest.raises(ValueError):
        library.design_values("7075-T6", "A", "L", thickness=1.0)       # 1 m sheet does not exist
