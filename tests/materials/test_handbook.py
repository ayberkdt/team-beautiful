"""Tests for aerokit.materials.handbook (MIL-HDBK-5J allowables reader).

Spot values were read from the rendered MIL-HDBK-5J pages (PDF page numbers
given per test) and are also confirmed on the cited page by
scripts/materials/verify_tables.py.
"""

from __future__ import annotations

import math
import re

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from aerokit.materials import handbook as hb

KSI = 6.894757293168361e6
ALL = hb.list_materials()


# --------------------------------------------------------------------------- data files


def test_materials_present() -> None:
    assert len(ALL) >= 20
    for slug in ("al-2024-t3", "al-2024-t351", "al-7075-t6", "al-7075-t651", "al-7075-t7351", "al-6061-t6",
                 "al-6061-t651", "al-7050-t7451", "al-2219-t87", "ti-6al-4v-annealed", "steel-4130-nt",
                 "ss-17-4ph-h1025", "ss-15-5ph-h1025", "steel-300m-qt", "inconel-718-sta"):
        assert slug in ALL, slug
    assert "index" not in ALL


@pytest.mark.parametrize("slug", ALL)
def test_every_file_parses_and_round_trips(slug: str) -> None:
    sheet = hb.load_material(slug)
    assert sheet.slug == slug
    assert sheet.tables
    for tab in sheet.tables:
        assert tab.rows
        assert all(r.basis in hb.Basis for r in tab.rows)
    text = hb.format_material_markdown(sheet)
    again = hb.parse_material_markdown(text, slug)
    assert again == sheet


@pytest.mark.parametrize("slug", ALL)
def test_source_sha_is_the_downloaded_pdf(slug: str) -> None:
    sha = hb.load_material(slug).front_matter["source_sha256"]
    assert sha == "67a4c320cc6c7f23ad155e428a21b3a940e489458a1570026e9b83c2901e6777"


# --------------------------------------------------------------------------- spot values


def test_2024_t3_sheet_ftu_a_l() -> None:
    # Table 3.2.3.0(b1), PDF page 373 (printed 3-71): 0.010-0.128 in., A-basis, Ftu L = 64 ksi
    a = hb.lookup_allowable("al-2024-t3", "Ftu", "A", "L", 0.05, units="source", thickness_units="in")
    assert (a.value, a.unit, a.table_id, a.pdf_page, a.thickness) == (64.0, "ksi", "3.2.3.0(b1)", 373, "0.010-0.128")
    si = hb.get_allowable("al-2024-t3", "Ftu", "A", "L", 0.05 * 0.0254)
    assert si == pytest.approx(64 * KSI, rel=1e-15)


def test_2024_t3_b_basis_and_elongation() -> None:
    # PDF page 373: B-basis 0.010-0.128 in. Ftu L = 65; e (LT, S-basis) 0.008-0.009 in. = 10 percent
    assert hb.get_allowable("al-2024-t3", "Ftu", "B", "L", 0.1, "source", thickness_units="in") == 65.0
    assert hb.get_allowable("al-2024-t3", "e", "S", "LT", 0.0085, "source", thickness_units="in") == 10.0
    assert hb.get_allowable("al-2024-t3", "e", "S", "LT", 0.0085, thickness_units="in") == pytest.approx(0.10)


def test_2024_t3_physical() -> None:
    # PDF page 373: E = 10.5 (10³ ksi), μ = 0.33, ω = 0.100 lb/in.³ for T3 sheet
    assert hb.get_allowable("al-2024-t3", "E", units="source") == 10.5
    assert hb.get_allowable("al-2024-t3", "E") == pytest.approx(10.5e3 * KSI)
    assert hb.get_allowable("al-2024-t3", "nu") == 0.33
    assert hb.get_allowable("al-2024-t3", "density") == pytest.approx(0.100 * 0.45359237 / 0.0254**3)


def test_ti_6al_4v_annealed_sheet() -> None:
    # Table 5.4.1.0(b), PDF page 945 (printed 5-53): sheet ≤0.1875 in., A: Ftu L 134, Fty L 126; E 16.0
    assert hb.get_allowable("ti-6al-4v-annealed", "Ftu", "A", "L", 0.1, "source", thickness_units="in") == 134.0
    assert hb.get_allowable("ti-6al-4v-annealed", "Fty", "A", "L", 0.1, "source", thickness_units="in") == 126.0
    a = hb.lookup_allowable("ti-6al-4v-annealed", "Fbru", "A", None, 0.1, "source", thickness_units="in",
                            e_over_d=1.5)
    assert (a.value, a.footnotes) == (213.0, ("d",))
    assert hb.get_allowable("ti-6al-4v-annealed", "E", units="source") == 16.0


def test_4130_normalized_undirected() -> None:
    # Table 2.3.1.0(c1), PDF page 71 (printed 2-17): AISI 4130 ≤0.188 in., S: Ftu 95 ksi, ω 0.283
    a = hb.lookup_allowable("steel-4130-nt", "Ftu", "S", "L", 0.1, "source", thickness_units="in",
                            form="Sheet, strip")
    assert (a.value, a.direction, a.basis) == (95.0, None, hb.Basis.S)
    assert hb.get_allowable("steel-4130-nt", "rho", units="source") == 0.283


def test_300m_needs_specification_filter() -> None:
    # Table 2.3.1.0(f1), PDF page 76 (printed 2-22): 0.40C 300M Ftu 270, 0.42C 300M Ftu 280
    with pytest.raises(ValueError, match="ambiguous"):
        hb.get_allowable("steel-300m-qt", "Ftu", "S", "L", units="source")
    assert hb.get_allowable("steel-300m-qt", "Ftu", "S", "L", units="source", specification="AMS 6417") == 270.0
    assert hb.get_allowable("steel-300m-qt", "Ftu", "S", "L", units="source", specification="AMS 6419") == 280.0


def test_15_5ph_h1025_plate() -> None:
    # Table 2.6.7.0(c), PDF page 224 (printed 2-170): 0.187-0.625 in., S: Ftu L 154, LT 155
    assert hb.get_allowable("ss-15-5ph-h1025", "Ftu", "S", "L", 0.5, "source", thickness_units="in",
                            form="Plate") == 154.0
    assert hb.get_allowable("ss-15-5ph-h1025", "Ftu", "S", "LT", 0.5, "source", thickness_units="in",
                            form="Plate") == 155.0


def test_ramberg_osgood_n_from_figure() -> None:
    # Figure 3.2.3.1.6(a), PDF page 397: n(L-tension) = 50, n(LT-comp.) = 11 (2024-T3 sheet)
    assert hb.get_ramberg_osgood_n("al-2024-t3", "L", "tension").n == 50.0
    assert hb.get_ramberg_osgood_n("al-2024-t3", "LT", "compression").n == 11.0
    # Figure 3.2.3.1.6(i), PDF page 401: n(L-tension) = 42 with TYS 53 ksi (2024-T351 plate)
    e = hb.get_ramberg_osgood_n("al-2024-t351", "L", "tension")
    assert (e.n, e.yield_raw, e.figure) == (42.0, "53", "3.2.3.1.6(i)")
    # Figure 5.4.1.1.6(a), PDF page 956: RT entry only (n = 33), elevated temperatures excluded
    assert hb.get_ramberg_osgood_n("ti-6al-4v-annealed", None, "tension").n == 33.0


# --------------------------------------------------------------------------- units


def test_unit_conversion_constants() -> None:
    assert pytest.approx(6.894757, abs=5e-7) == hb.KSI_TO_PA / 1e6
    assert hb.ksi_to_pa(1.0) == hb.KSI_TO_PA
    assert pytest.approx(27679.9047, rel=1e-9) == hb.LB_PER_IN3_TO_KG_PER_M3


@given(st.floats(min_value=0.001, max_value=1000.0))
def test_si_equals_source_times_factor(t_scale: float) -> None:
    ksi = hb.get_allowable("al-7075-t6", "Ftu", "A", "L", 0.05, "source", thickness_units="in")
    pa = hb.get_allowable("al-7075-t6", "Ftu", "A", "L", 0.05 * 25.4, "SI", thickness_units="mm")
    assert pa == pytest.approx(ksi * 6.894757e6, rel=1e-7)
    assert hb.ksi_to_pa(t_scale) == pytest.approx(t_scale * 6.894757293168361e6, rel=1e-15)


# --------------------------------------------------------------------------- error paths


def test_unknown_material() -> None:
    with pytest.raises(KeyError, match="unknown material"):
        hb.load_material("al-9999-t6")


def test_unknown_property() -> None:
    with pytest.raises(KeyError, match="unknown property"):
        hb.get_allowable("al-2024-t3", "Fxx")


def test_thickness_out_of_range() -> None:
    with pytest.raises(ValueError, match="outside the tabulated ranges"):
        hb.get_allowable("al-2024-t3", "Ftu", "A", "L", 0.5, thickness_units="in")
    with pytest.raises(ValueError, match="positive"):
        hb.get_allowable("al-2024-t3", "Ftu", "A", "L", -1.0)


def test_ambiguous_without_thickness() -> None:
    with pytest.raises(ValueError, match="ambiguous"):
        hb.get_allowable("al-2024-t3", "Ftu", "A", "L")


def test_value_not_printed() -> None:
    with pytest.raises(ValueError, match="not printed"):
        hb.get_allowable("al-2024-t3", "Ftu", "A", "ST", 0.05, thickness_units="in")


def test_bad_arguments() -> None:
    with pytest.raises(ValueError, match="basis"):
        hb.get_allowable("al-2024-t3", "Ftu", "C", "L", 0.05, thickness_units="in")
    with pytest.raises(ValueError, match="direction"):
        hb.get_allowable("al-2024-t3", "Ftu", "A", "XX", 0.05, thickness_units="in")
    with pytest.raises(ValueError, match="e_over_d"):
        hb.get_allowable("al-2024-t3", "Fbru", "A", None, 0.05, thickness_units="in")
    with pytest.raises(ValueError, match="S-basis"):
        hb.get_allowable("al-2024-t3", "e", "A", "LT", 0.0085, thickness_units="in")
    with pytest.raises(KeyError, match="not tabulated"):
        hb.get_allowable("steel-4130-nt", "Ftu", "A", "L", 0.1, thickness_units="in")
    with pytest.raises(ValueError, match="units"):
        hb.get_allowable("al-2024-t3", "E", units="imperial")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- strict parser

GOOD = """---
material: test-x
alloy: 9999
temper_or_condition: T6
source_document: test
source_sha256: {sha}
source_tables: 1.1.1.1(b)
---

## Table 1.1.1.1(b)

- title: Test table
- pdf_page: 1
- printed_page: 1-1

| col | form | thickness (in.) | basis | Ftu L (ksi) | Fty L (ksi) | E (10³ ksi) |
|---:|:---|:---|:---|---:|---:|---:|
| 1 | Sheet | 0.010-0.249 | A | 64 | 47 [a] | 10.5 |
| 2 | Sheet | 0.010-0.249 | B | 66 | — | 10.5 |

### Footnotes to Table 1.1.1.1(b) (as printed)

- a: test footnote
""".replace("{sha}", "0" * 64)


def test_good_synthetic_parses() -> None:
    s = hb.parse_material_markdown(GOOD, "test-x")
    row = s.tables[0].rows[0]
    assert row.values["Fty L"] == hb.Cell("47", ("a",))
    assert s.tables[0].rows[1].values["Fty L"].value is None
    assert s.tables[0].footnotes == {"a": "test footnote"}
    assert hb.parse_material_markdown(hb.format_material_markdown(s), "test-x") == s


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("| 64 | 47 [a] |", "| 64x | 47 [a] |", "malformed value"),
        ("| 64 | 47 [a] |", "| 64 | 47 [A] |", "malformed value"),
        ("| 64 | 47 [a] |", "| 6.4.1 | 47 [a] |", "malformed value"),
        ("| 66 | — | 10.5 |", "| 66 | — |", "cells but the header"),
        ("Ftu L (ksi)", "Ftu L (MPa)", "must carry unit"),
        ("Ftu L (ksi)", "Fzz L (ksi)", "unknown column"),
        ("| B | 66", "| Q | 66", "unknown basis"),
        ("| 2 | Sheet", "| 1 | Sheet", "strictly increasing"),
        ("alloy: 9999\n", "", "lacks 'alloy'"),
        ("source_sha256: " + "0" * 64, "source_sha256: abc", "64 hex"),
        ("|---:|:---|", "|:---|", "separator"),
        ("- pdf_page: 1\n", "", "pdf_page"),
        ("## Table 1.1.1.1(b)", "## Tabel 1", "unknown section"),
        ("| 1 | Sheet", "1 | Sheet", "unexpected text"),
    ],
)
def test_malformed_markdown_rejected(old: str, new: str, message: str) -> None:
    assert old in GOOD
    bad = GOOD.replace(old, new, 1)
    with pytest.raises(hb.MarkdownFormatError, match=re.escape(message) if "'" in message else message):
        hb.parse_material_markdown(bad, "test-x")


def test_wrong_slug_rejected() -> None:
    with pytest.raises(hb.MarkdownFormatError, match="file name"):
        hb.parse_material_markdown(GOOD, "other")


@settings(max_examples=200)
@given(st.text(alphabet="0123456789.-[]|abc —", min_size=1, max_size=8))
def test_value_cells_strict(text: str) -> None:
    ok = re.fullmatch(r"(?:\d+(?:\.\d+)?|\.\d+|—)(?: \[[a-z](?:,[a-z])*\])?", text) is not None
    bad = GOOD.replace("| 64 | 47 [a] |", f"| {text} | 47 [a] |", 1)
    if "|" in text or text != text.strip():
        return
    if ok:
        hb.parse_material_markdown(bad, "test-x")
    else:
        with pytest.raises(hb.MarkdownFormatError):
            hb.parse_material_markdown(bad, "test-x")


# --------------------------------------------------------------------------- thickness ranges


@given(st.integers(1, 9000), st.integers(1, 9000))
def test_thickness_ranges_tile(a: int, w: int) -> None:
    lo, hi = a / 1000, (a + w) / 1000
    r1 = hb.ThicknessRange.parse(f"{lo:.3f}-{hi:.3f}")
    r2 = hb.ThicknessRange.parse(f"{hi + 0.001:.3f}-{hi + 1:.3f}")
    assert r1 is not None and r2 is not None
    assert r1.contains(lo) and r1.contains(hi) and not r2.contains(hi)
    assert r2.contains(hi + 0.001)
    assert r1.hi == pytest.approx(r2.lo, abs=1e-12)  # no gap between printed ranges


def test_thickness_forms() -> None:
    le = hb.ThicknessRange.parse("≤0.188")
    gt = hb.ThicknessRange.parse(">0.188")
    assert le is not None and gt is not None
    assert le.contains(0.188) and not gt.contains(0.188) and gt.contains(0.19)
    assert hb.ThicknessRange.parse("O.D. >0.125 Wall >0.015") is None


# --------------------------------------------------------------------------- Ramberg-Osgood


@given(st.floats(1e3, 1e5), st.floats(10.0, 300.0), st.floats(2.0, 60.0))
def test_ro_passes_through_offset_yield(E: float, f02: float, n: float) -> None:
    eps = hb.ramberg_osgood_strain(f02, E, f02, n)
    assert eps - f02 / E == pytest.approx(0.002, rel=1e-12, abs=1e-15)


def test_ro_curve_contains_yield_point_exactly() -> None:
    E, f02, n = 10.5e3, 47.0, 50.0
    strain, stress = hb.ramberg_osgood_curve(E, f02, n, num=50)
    i = int(np.flatnonzero(stress == f02)[0])
    assert strain[i] - stress[i] / E == pytest.approx(0.002, rel=1e-13)
    assert np.all(np.diff(strain) > 0) and np.all(np.diff(stress) > 0)


@settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])   # slow only when the machine is busy
@given(st.floats(1e3, 1e5), st.floats(10.0, 300.0), st.floats(2.0, 60.0), st.floats(0.05, 1.3))
def test_ro_inverse_and_tangent(E: float, f02: float, n: float, ratio: float) -> None:
    s = ratio * f02
    e = hb.ramberg_osgood_strain(s, E, f02, n)
    assert hb.ramberg_osgood_stress(e, E, f02, n) == pytest.approx(s, rel=1e-9)
    h = 1e-6 * s
    num = 2 * h / (hb.ramberg_osgood_strain(s + h, E, f02, n) - hb.ramberg_osgood_strain(s - h, E, f02, n))
    assert hb.ramberg_osgood_tangent_modulus(s, E, f02, n) == pytest.approx(num, rel=1e-5)
    assert hb.ramberg_osgood_tangent_modulus(0.0, E, f02, n) == pytest.approx(E)


def test_ro_rejects_bad_parameters() -> None:
    with pytest.raises(ValueError):
        hb.ramberg_osgood_strain(1.0, -1.0, 1.0, 10.0)
    with pytest.raises(ValueError):
        hb.ramberg_osgood_curve(1.0, 1.0, math.nan)


def test_stress_strain_curve_from_tables() -> None:
    strain, stress = hb.stress_strain_curve("al-2024-t3", "A", "L", 0.05, thickness_units="in")
    f02 = hb.get_allowable("al-2024-t3", "Fty", "A", "L", 0.05, thickness_units="in")
    E = hb.get_allowable("al-2024-t3", "E")
    i = int(np.flatnonzero(stress == f02)[0])
    assert strain[i] == pytest.approx(f02 / E + 0.002, rel=1e-12)
