"""Tests for aerokit.materials.composites (NCAMP NCP-RP-2013-015 Rev A, Hexcel 8552 IM7).

Spot values are as printed on the cited PDF pages of
references/materials/ncamp-ncp-rp-2013-015/cmh17-generic-basis-8552-im7-revA.pdf;
every number of the data sheet is also re-found on its page with pdfplumber by
scripts/materials/verify_ncamp.py (report: references/materials/ncamp_verification_report.md).
"""

from __future__ import annotations

import math

import pytest

from aerokit.composites import laminate as lam
from aerokit.materials import composites as cm
from aerokit.materials import library

KSI = 6.894757293168361e6
SLUG = "ncamp-8552-im7"
MD = cm.DATA_DIR / f"{SLUG}.md"


def _text() -> str:
    return MD.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- data file


def test_sheet_parses_and_has_all_tables() -> None:
    sheet = cm.load_composite(SLUG)
    assert cm.list_composites() == (SLUG,)
    assert sorted(sheet.tables) == list(range(4, 38))
    assert len(sheet.front_matter["source_sha256"]) == 64
    assert "not yet been approved by the CMH-17 organization" in sheet.front_matter["approval_caveat"]
    assert all(t.extraction == "automatic" for t in sheet.tables.values())
    assert sheet.tests_extraction.startswith("manual")
    assert {t.test for t in sheet.tests} >= {"LT", "UNT0", "OHT1", "UNC0", "OHC1", "IPS", "SBS"}
    n = sum(1 for t in sheet.tables.values() for r in t.rows for c in r.cells if c.raw)
    assert n == 2317


def test_aliases_resolve_to_the_sheet() -> None:
    for name in ("IM7-8552", "im7/8552", "8552-IM7", " ncamp-8552-im7 "):
        assert cm.material_slug(name) == SLUG
    assert cm.load_composite("IM7-8552") is cm.load_composite(SLUG)


@pytest.mark.parametrize("prop, basis, env, method, ksi, table, page", [
    ("F1tu", "B", "RTD", "generic", 280.74, 10, 33),
    ("F1tu", "A", "ETW", "qualification", 201.74, 10, 33),
    ("F1tu", "B", "CTD", "pooled", 302.31, 10, 33),
    ("F1tu", "mean", "RTD", "generic", 364.5313, 9, 32),
    ("F1tu", "mean", "RTD", "pooled", 361.929, 23, 61),
    ("F1cu", "B", "RTD", "generic", 193.85, 6, 28),
    ("F1cu", "B", "ETD", "qualification", 175.06, 6, 28),
    ("F12su", "B", "ETW", "generic", 4.68, 14, 40),
    ("F12s0.2", "A", "CTD", "generic", 8.76, 14, 40),
    ("SBS", "B", "RTD", "qualification", 16.28, 14, 40),
    ("UNC0", "B", "ETD", "generic", 53.86, 5, 27),
    ("OHC1", "mean", "ETW", "generic", 35.5462, 4, 26),
    ("OHT1", "B", "ETW", "generic", 56.98, 10, 33),
    ("UNT0", "mean", "CTD", "qualification", 152.578, 25, 66),
])
def test_spot_values_with_page(prop: str, basis: str, env: str, method: str, ksi: float, table: int,
                               page: int) -> None:
    v = cm.lookup_lamina_property("IM7-8552", prop, basis, env, units="source", method=method)
    assert v.value == ksi and v.unit == "ksi"
    assert (v.table_id, v.pdf_page) == (table, page)
    si = cm.get_lamina_property("IM7-8552", prop, basis, env, method=method)
    assert si == pytest.approx(ksi * KSI, rel=1e-12)


def test_spot_value_on_stats_table_page() -> None:
    """Table 23 (PDF p. 61) is the LT RTD summary-statistics table; check it against the raw md text."""
    s = cm.sample_statistics("IM7-8552", "Xt", "RTD", units="source")
    assert (s.table_id, s.pdf_page, s.count, s.column) == (23, 61, 99, "Pooled")
    assert "| 61 | Average |" in _text() and "| 361.929 |" in _text()
    assert s.cv_percent == 8.23 and s.n_units == 12
    assert s.minimum <= s.mean <= s.maximum
    q = cm.sample_statistics("IM7-8552", "UNC0", "RTD", column="Qual.", units="source")
    assert (q.mean, q.count, q.table_id, q.pdf_page) == (94.509, 9, 17, 45)
    with pytest.raises(KeyError, match="NA"):
        cm.sample_statistics("IM7-8552", "UNC0", "RTD", column="A01")


def test_alternate_method_marker_and_caveat() -> None:
    v = cm.lookup_lamina_property("IM7-8552", "UNC0", "B", "ETW", units="source")
    assert v.markers == ("*",) and "Alternate Generic Basis Value Method" in v.note
    assert "CMH-17" in v.note
    q = cm.lookup_lamina_property("IM7-8552", "UNC0", "B", "RTD", units="source", method="qualification")
    assert q.markers == () and q.note == "" and q.row_label == "Qualification B-Basis or B-Estimate"


def test_unit_conversion() -> None:
    src = cm.get_lamina_property("IM7-8552", "S12", "B", "RTD", units="source")
    si = cm.get_lamina_property("IM7-8552", "S12", "B", "RTD", units="SI")
    assert src == 12.38
    assert si == pytest.approx(12.38 * 6.894757293168361e6, rel=1e-12)
    assert math.isclose(si / 1e6, 85.357, rel_tol=1e-4)
    stats = cm.sample_statistics("IM7-8552", "S12", "ETW")
    assert stats.unit == "Pa" and stats.mean == pytest.approx(5.451 * KSI)


def test_basis_ordering_holds_for_every_value() -> None:
    for prop in cm.PROPERTIES:
        for env in cm.ENVIRONMENTS:
            for method in ("generic", "pooled", "qualification"):
                try:
                    b = cm.get_lamina_property(SLUG, prop, "B", env, "source", method=method)
                    a = cm.get_lamina_property(SLUG, prop, "A", env, "source", method=method)
                except KeyError:
                    continue
                assert a <= b, (prop, env, method)


# --------------------------------------------------------------------------- errors


def test_error_paths() -> None:
    with pytest.raises(KeyError, match="unknown property"):
        cm.get_lamina_property(SLUG, "Fxyz")
    for missing in ("E1", "nu12", "G12", "Yc", "F2cu"):
        with pytest.raises(KeyError, match="not reported"):
            cm.get_lamina_property(SLUG, missing)
    with pytest.raises(ValueError, match="environment"):
        cm.get_lamina_property(SLUG, "F1tu", environment="HOT")
    with pytest.raises(KeyError, match="not tested in ETD"):
        cm.get_lamina_property(SLUG, "F1tu", environment="ETD")
    with pytest.raises(ValueError, match="basis"):
        cm.get_lamina_property(SLUG, "F1tu", basis="S")
    with pytest.raises(ValueError, match="method"):
        cm.get_lamina_property(SLUG, "F1tu", method="cmh17")
    with pytest.raises(ValueError, match="units"):
        cm.get_lamina_property(SLUG, "F1tu", units="imperial")  # type: ignore[arg-type]
    with pytest.raises(KeyError, match="no mean"):
        cm.get_lamina_property(SLUG, "F1cu", basis="mean")
    with pytest.raises(KeyError, match="pooled"):
        cm.get_lamina_property(SLUG, "F1cu", method="pooled")
    with pytest.raises(KeyError, match="unknown composite"):
        cm.load_composite("T300-914")
    with pytest.raises(KeyError):
        cm.material_slug("")


# --------------------------------------------------------------------------- strict parser


@pytest.mark.parametrize("old, new, msg", [
    ("source_sha256: 7daa", "source_sha256: zzaa", "sha256"),
    ("approval_caveat:", "approval_cav:", "approval_caveat"),
    ("| 33 | Generic B-basis | 273.31 |", "| 33 | Generic B-basis | 273.31x |", "malformed value"),
    ("| 33 | Generic B-basis | 273.31 |", "| 33 | Generic B-basis | 273.31 | 1 |", "cells"),
    ("| 33 | Generic B-basis | 273.31 |", "| 34 | Generic B-basis | 273.31 |", "pdf_page"),
    ("- kind: basis\n- pdf_page: 33", "- kind: magic\n- pdf_page: 33", "kind"),
    ("| page | row | LT / CTD |", "| page | row | LT / HOT |", "column"),
    ("## Table 10", "## Tabelle 10", "unknown section"),
    ("| 45 | Count |", "| 45 | Counts |", "statistics rows"),
    ("- title: Tension Strength Units", "title: Tension Strength Units", "unexpected text"),
])
def test_malformed_markdown_rejected(old: str, new: str, msg: str) -> None:
    text = _text()
    assert old in text
    bad = text.replace(old, new, 1)
    with pytest.raises(cm.MarkdownFormatError, match=msg):
        cm.parse_composite_markdown(bad, SLUG)


def test_parser_rejects_wrong_slug_and_missing_front_matter() -> None:
    with pytest.raises(cm.MarkdownFormatError, match="file name"):
        cm.parse_composite_markdown(_text(), "other")
    with pytest.raises(cm.MarkdownFormatError, match="front matter"):
        cm.parse_composite_markdown("# no front matter\n")
    head = _text().split("\n## ")[0]
    with pytest.raises(cm.MarkdownFormatError, match="no '## Table'"):
        cm.parse_composite_markdown(head + "\n")


# --------------------------------------------------------------------------- lamina record + CLT


def test_lamina_record_report_only() -> None:
    r = cm.lamina_record("IM7-8552", "B", "RTD")
    assert r["Xt"] == pytest.approx(280.74 * KSI)
    assert r["Xc"] == pytest.approx(193.85 * KSI)
    assert r["S12"] == pytest.approx(12.38 * KSI)
    assert "E1" not in r and set(r["missing"]) == {"E1", "E2", "nu12", "G12", "Yt", "Yc", "t_layer", "rho"}
    assert "Table 10, PDF p. 33" in r["provenance"]["Xt"]
    assert any("CMH-17" in u for u in r["unverified"])


def test_lamina_record_errors() -> None:
    with pytest.raises(KeyError, match="RTD, ETW"):
        cm.lamina_record("IM7-8552", "B", "ETD")
    with pytest.raises(KeyError, match="Xc"):
        cm.lamina_record("IM7-8552", "mean", "RTD")
    with pytest.raises(KeyError):
        cm.lamina_record("IM7-8552", fill_from="no-such-material")


def test_lamina_record_with_clt_smoke() -> None:
    lib = library.MATERIALS["IM7-8552"]
    r = cm.lamina_record("IM7-8552", "B", "ETW", fill_from="IM7-8552")
    assert set(lib) - {"name", "source", "unverified"} <= set(r)
    assert r["E1"] == lib["E1"] and r["missing"] == []
    assert r["provenance"]["G12"].startswith("aerokit.materials.library")
    assert any(u.startswith("G12") for u in r["unverified"]) and any("ETW" in u for u in r["unverified"])
    t = r["t_layer"]
    ply = lam.layers(r, [(a, t) for a in (0, 45, -45, 90, 90, -45, 45, 0)])
    c = lam.laminate_constants(ply)
    assert c["h"] == pytest.approx(8 * t)
    assert 0 < c["Ex"] < r["E1"] and c["Ex"] == pytest.approx(c["Ey"], rel=1e-9)
    assert c["Gxy"] == pytest.approx(c["Ex"] / (2 * (1 + c["nuxy"])), rel=1e-9)  # quasi-isotropic
    assert lib["Xt"] == 2724e6  # library record untouched by fill_from
