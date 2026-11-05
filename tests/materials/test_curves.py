"""Digitized MIL-HDBK-5J figure curves (aerokit.materials.curves).

Spot values were checked against the overlays in references/materials/curve_overlays/ (digitized points
drawn over the page images) and against the Ramberg-Osgood reconstruction in
references/materials/curve_verification_report.md.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from aerokit.materials import curves as cv
from aerokit.materials import handbook as hb

FIG_INDEX = hb.DATA_DIR / "figures" / "index.md"
RO_TOL_PCT = 3.0        # % of f0.2, stress <= f0.2 (the gate of scripts/materials/verify_curves.py)
RT_TOL = 2.0            # percentage points at 75 F


def _index_figures() -> list[str]:
    return [ln.split("|")[1].strip() for ln in FIG_INDEX.read_text(encoding="utf-8").splitlines()
            if ln.startswith("| ") and not ln.startswith("| figure")]


# --------------------------------------------------------------------------- files


def test_one_curve_file_per_indexed_figure():
    assert list(cv.list_figures()) == _index_figures()
    assert len(cv.list_figures()) == 43


@pytest.mark.parametrize("fid", _index_figures())
def test_every_curve_file_parses(fid):
    fc = cv.load_curve(fid)
    assert fc.figure == fid
    assert fc.status in ("digitized", "skipped")
    if fc.status == "skipped":
        assert not fc.curves and fc.skipped
        return
    names = {a.name for a in fc.axes}
    for c in fc.curves:
        assert c.x_axis in names and c.y_axis in names
        assert len(c.x) == len(c.y) >= 2
        assert all(math.isfinite(v) for v in c.x + c.y)
        if c.function_of_x:
            assert np.all(np.diff(c.x_array) > 0)
            assert len(c.x) <= 60
    used = {c.x_axis for c in fc.curves} | {c.y_axis for c in fc.curves}
    assert all(a.max_residual_pct <= 0.5 for a in fc.axes if a.name in used)


def test_counts():
    figs = [cv.load_curve(f) for f in cv.list_figures()]
    assert sum(f.status == "digitized" for f in figs) == 36
    assert sum(len(f.curves) for f in figs) >= 130


def test_raster_figures_are_skipped_with_reason():
    for fid in ("3.7.6.1.1(a)", "3.7.6.1.1(b)", "5.4.1.1.4", "6.3.5.1.1", "6.3.5.1.4(a)", "3.2.3.1.4"):
        fc = cv.load_curve(fid)
        assert fc.status == "skipped"
        assert "raster" in fc.skipped[0]


def test_figure_file_validates_ids():
    assert cv.figure_file("3.7.6.1.6(a)").name == "fig-3-7-6-1-6a.md"
    for bad in ("../etc/passwd", "3.7.6.1.6(a)/../x", "", "fig-3-7", "3.7(A)"):
        with pytest.raises(ValueError):
            cv.figure_file(bad)
    with pytest.raises(KeyError):
        cv.load_curve("9.9.9.9")


def test_list_curves_filters_by_material():
    allc = cv.list_curves()
    sub = cv.list_curves("al-7075-t6")
    assert sub and set(sub) <= set(allc)
    assert {c.figure for c in sub} == {"3.7.6.1.4", "3.7.6.1.6(a)"}
    with pytest.raises(KeyError):
        cv.list_curves("unobtainium-t6")


# --------------------------------------------------------------------------- spot values (checked on overlays)


@pytest.mark.parametrize("fid,label,x,expected,tol", [
    ("3.7.6.1.6(a)", "L - tension", 4.0, 41.15, 0.5),            # elastic line, E = 10.3e3 ksi -> 41.2 ksi
    ("3.2.3.1.1(a)", "1/2 hr", -400.0, 132.1, 1.5),               # cryogenic branch, overlay
    ("3.2.3.1.1(a)", "1/2 hr", 400.0, 74.6, 1.5),
    ("3.2.3.1.1(a)", "10,000 hr", 400.0, 38.9, 1.5),
    ("3.2.3.1.1(a)", "1/2 hr", 75.0, 100.0, 1.0),
])
def test_spot_values(fid, label, x, expected, tol):
    assert cv.curve_value(fid, label, x) == pytest.approx(expected, abs=tol)


def test_tangent_modulus_asymptote_equals_table_ec():
    # Inconel 718 casting: vertical part of the tangent-modulus curve at Et = Ec (30.9e3 ksi in the table)
    et = cv.curve_value("6.3.5.1.6(c)", "Compression (tangent modulus)", 20.0, along="y")
    assert et == pytest.approx(hb.get_allowable("inconel-718-sta", "Ec", units="source"), abs=0.4)


# --------------------------------------------------------------------------- interpolation


def test_linear_interpolation_between_points():
    c = cv.load_curve("3.7.6.1.6(g)").curve("L - tension")
    for i in (0, 10, len(c.x) - 2):
        xm = 0.5 * (c.x[i] + c.x[i + 1])
        assert cv.curve_value("3.7.6.1.6(g)", c.label, xm) == pytest.approx(0.5 * (c.y[i] + c.y[i + 1]))
        assert cv.curve_value("3.7.6.1.6(g)", c.label, c.x[i]) == pytest.approx(c.y[i])


def test_array_input_keeps_shape():
    c = cv.load_curve("3.7.6.1.6(g)").curve("L - tension")
    q = np.linspace(c.x[0], c.x[-1], 12).reshape(3, 4)
    out = cv.curve_value("3.7.6.1.6(g)", c.label, q)
    assert isinstance(out, np.ndarray) and out.shape == (3, 4)


@settings(max_examples=150, deadline=None)
@given(st.floats(min_value=0.0, max_value=1.0))
def test_interpolated_value_lies_between_neighbours(t):
    c = cv.load_curve("3.2.3.1.1(a)").curve("10 hr")
    x = c.x[0] + t * (c.x[-1] - c.x[0])
    v = cv.curve_value("3.2.3.1.1(a)", "10 hr", x)
    k = int(np.searchsorted(c.x_array, x, side="right")) - 1
    k = min(max(k, 0), len(c.x) - 2)
    lo, hi = sorted((c.y[k], c.y[k + 1]))
    assert lo - 1e-9 <= v <= hi + 1e-9


def test_out_of_range_is_an_error_not_extrapolation():
    c = cv.load_curve("3.7.6.1.6(g)").curve("L - tension")
    span = c.x[-1] - c.x[0]
    for bad in (c.x[0] - 0.01 * span, c.x[-1] + 0.01 * span, float("nan"), float("inf")):
        with pytest.raises(cv.OutOfRangeError, match="outside the digitized range"):
            cv.curve_value("3.7.6.1.6(g)", c.label, bad)
    with pytest.raises(cv.OutOfRangeError):
        cv.curve_value("3.7.6.1.6(g)", c.label, np.array([c.x[0], c.x[-1] + span]))


def test_non_function_curve_refuses_x_lookup():
    with pytest.raises(ValueError, match="not single-valued in x"):
        cv.curve_value("3.7.6.1.6(a)", "L - compression (tangent modulus)", 5.0)
    et = cv.curve_value("3.7.6.1.6(a)", "L - compression (tangent modulus)", 50.0, along="y")
    assert 8.5 < et < 10.3                     # Et at 50 ksi read along y (overlay: ~9.2e3 ksi)


def test_unknown_curve_lists_labels():
    with pytest.raises(KeyError, match="L - tension"):
        cv.curve_value("3.7.6.1.6(g)", "no such curve", 1.0)
    assert cv.load_curve("3.7.6.1.6(g)").curve("l - TENSION").label == "L - tension"


# --------------------------------------------------------------------------- malformed files


def _good_text() -> str:
    return cv.figure_file("3.7.6.1.6(g)").read_text(encoding="utf-8")


def _first_data_row(text: str) -> str:
    return next(ln for ln in text.splitlines() if re.fullmatch(r"\| -?[\d.]+ \| -?[\d.]+ \|", ln))


@pytest.mark.parametrize("mutate,msg", [
    (lambda t: t.replace("# Digitized curves: Figure", "# Curves:", 1), "first line"),
    (lambda t: t.replace("## Axes", "## Axis", 1), "missing section"),
    (lambda t: t.replace("- pdf_page: 700", "- pdf_page: seven hundred", 1), "pdf_page"),
    (lambda t: t.replace(_first_data_row(t), "| abc | 1.0 |", 1), "two numbers"),
    (lambda t: t.replace(_first_data_row(t), "| 1.0 | nan |", 1), "two numbers"),
    (lambda t: t.replace(_first_data_row(t), _first_data_row(t) + "\n" + _first_data_row(t), 1), "points says"),
    (lambda t: t.replace("- function_of_x: yes", "- function_of_x: maybe", 1), "function_of_x"),
    (lambda t: t.replace("- x_axis: x1", "- x_axis: x9", 1), "not an axis"),
    (lambda t: t.replace("## Curve: LT - tension", "## Curve: L - tension", 1), "duplicate curve label"),
    (lambda t: t.replace("|---:|---:|", "|:---|:---|", 1), "separator"),
    (lambda t: t.replace("- status: digitized", "- status: done", 1), "status"),
    (lambda t: t.replace("- kind: stress-strain\n", "- kind: pie\n", 1), "kind"),
])
def test_malformed_markdown_is_rejected(mutate, msg):
    good = _good_text()
    assert cv.parse_curve_markdown(good).figure == "3.7.6.1.6(g)"
    bad = mutate(good)
    assert bad != good
    with pytest.raises(cv.CurveFormatError, match=msg):
        cv.parse_curve_markdown(bad)


def test_non_increasing_x_rejected():
    good = _good_text()
    rows = [ln for ln in good.splitlines() if re.fullmatch(r"\| -?[\d.]+ \| -?[\d.]+ \|", ln)]
    swapped = good.replace(rows[1] + "\n" + rows[2], rows[2] + "\n" + rows[1], 1)
    with pytest.raises(cv.CurveFormatError, match="strictly"):
        cv.parse_curve_markdown(swapped)


# --------------------------------------------------------------------------- temperature factor


@pytest.mark.parametrize("material,prop,exposure", [
    ("al-2024-t3", "Ftu", 0.5), ("al-2024-t351", "Fty", "1/2 hr"), ("al-2219-t87", "Ftu", "½ hr"),
    ("al-2219-t87", "Fty", 10000), ("al-6061-t6", "Ftu", 0.5), ("al-6061-t6", "E", None),
    ("al-7075-t6", "E", None), ("al-7075-t651", "Ec", None), ("steel-4130-nt", "Ftu", None),
    ("steel-4130-qt", "Fty", 0.5), ("steel-4130-nt", "E", None), ("ss-15-5ph-h1025", "Ftu", None),
    ("ss-15-5ph-h1025", "Fty", None), ("ti-6al-4v-annealed", "Ftu", None), ("ti-6al-4v-annealed", "Fty", None),
])
def test_temperature_factor_is_100_percent_at_room_temperature(material, prop, exposure):
    assert cv.temperature_factor(material, prop, 75.0, exposure=exposure) == pytest.approx(100.0, abs=RT_TOL)


def test_temperature_factor_units_and_exposure_ordering():
    f = cv.temperature_factor("al-2024-t3", "Ftu", 400.0, exposure=0.5)
    assert cv.temperature_factor("al-2024-t3", "Ftu", (400.0 - 32.0) * 5 / 9, exposure=0.5,
                                 temperature_units="C") == pytest.approx(f)
    longer = cv.temperature_factor("al-2024-t3", "Ftu", 400.0, exposure="10,000 hr")
    assert longer < f


def test_temperature_factor_errors():
    with pytest.raises(ValueError, match="exposure"):
        cv.temperature_factor("al-2024-t3", "Ftu", 300.0)                     # several exposure curves
    with pytest.raises(ValueError, match="no curve for exposure"):
        cv.temperature_factor("al-2024-t3", "Ftu", 300.0, exposure=3.0)
    with pytest.raises(ValueError, match="up to"):
        cv.temperature_factor("steel-4130-nt", "Ftu", 300.0, exposure=10.0)   # figure: exposure up to 1/2 hr
    with pytest.raises(ValueError, match="raster"):
        cv.temperature_factor("al-7075-t6", "Ftu", 300.0, exposure=0.5)        # Fig. 3.7.6.1.1(a) is an image
    with pytest.raises(cv.OutOfRangeError):
        cv.temperature_factor("steel-4130-nt", "Ftu", 3000.0)
    with pytest.raises(KeyError):
        cv.temperature_factor("no-such-alloy", "Ftu", 75.0)
    with pytest.raises(ValueError, match="property"):
        cv.temperature_factor("al-2024-t3", "Fsu", 75.0)


@pytest.mark.parametrize("text,hours", [("1/2 hr", 0.5), ("½ hr", 0.5), ("10,000 hr", 1e4), ("10 hr", 10.0),
                                        ("Exposure", None), ("L - tension", None)])
def test_parse_exposure(text, hours):
    assert cv.parse_exposure_hours(text) == hours


# --------------------------------------------------------------------------- Ramberg-Osgood agreement


def _offset_yield(strain: np.ndarray, stress: np.ndarray, E: float) -> float:
    g = strain - stress / E - 0.002
    i = int(np.flatnonzero((g[:-1] < 0) & (g[1:] >= 0))[0])
    return float(stress[i] - g[i] * (stress[i + 1] - stress[i]) / (g[i + 1] - g[i]))


@pytest.mark.parametrize("fid,label,material,direction,loading", [
    ("3.7.6.1.6(a)", "L - tension", "al-7075-t6", "L", "tension"),
    ("3.7.6.1.6(g)", "LT - tension", "al-7075-t651", "LT", "tension"),
    ("3.7.6.1.6(h)", "L - compression", "al-7075-t651", "L", "compression"),
    ("3.2.3.1.6(i)", "L-tension", "al-2024-t351", "L", "tension"),
    ("3.2.3.1.6(a)", "LT - compression", "al-2024-t3", "LT", "compression"),
    ("3.2.3.1.6(i)", "L-compression", "al-2024-t351", "L", "compression"),
    ("3.7.4.2.6(a)", "Short Transverse", "al-7050-t7451", "ST", "tension"),
    ("5.4.1.1.6(a)", "RT", "ti-6al-4v-annealed", None, "tension"),
    ("2.6.9.2.6(a)", "H900", "ss-17-4ph-h900", None, "tension"),
])
def test_stress_strain_matches_ramberg_osgood(fid, label, material, direction, loading):
    entry = hb.get_ramberg_osgood_n(material, direction, loading)
    assert entry.figure == fid
    E = hb.get_allowable(material, "E" if loading == "tension" else "Ec", units="source") * 1000.0
    c = cv.load_curve(fid).curve(label)
    strain, stress = c.x_array * 1e-3, c.y_array
    f02 = float(entry.yield_raw) if entry.yield_raw else _offset_yield(strain, stress, E)
    ro = hb.ramberg_osgood_stress(strain, E, f02, entry.n)
    sel = stress <= f02
    assert np.max(np.abs(stress[sel] - ro[sel])) / f02 * 100.0 <= RO_TOL_PCT


def test_tangent_modulus_matches_ramberg_osgood():
    fid, material = "3.7.6.1.6(h)", "al-7075-t651"
    e = hb.get_ramberg_osgood_n(material, "L", "compression")
    Ec = hb.get_allowable(material, "Ec", units="source") * 1000.0
    ss = cv.load_curve(fid).curve("L - compression")
    f02 = _offset_yield(ss.x_array * 1e-3, ss.y_array, Ec)
    tm = cv.load_curve(fid).curve("L - compression (tangent modulus)")
    et_ro = hb.ramberg_osgood_tangent_modulus(tm.y_array, Ec, f02, e.n)
    sel = (tm.x_array * 1000.0 < 0.98 * Ec) & (tm.y_array <= f02)
    assert sel.sum() > 5
    # compare in stress at equal Et: the slope dEt/df is steep near f0.2, so compare via Et relative to Ec
    assert np.max(np.abs(tm.x_array[sel] * 1000.0 - et_ro[sel])) / Ec < 0.10


def test_known_discrepancy_7075_t6_clad_tangent_modulus():
    """Reported FAIL: the vertical part of the clad 7075-T6 Et curves is drawn at ~10.2e3 ksi, table Ec = 10.5e3."""
    tm = cv.load_curve("3.7.6.1.6(a)").curve("L - compression (tangent modulus)")
    assert max(tm.x) == pytest.approx(10.2, abs=0.1)
    assert hb.get_allowable("al-7075-t6", "Ec", units="source") == pytest.approx(10.5)
