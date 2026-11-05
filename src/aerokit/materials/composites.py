"""Reader for NCAMP composite strength data stored as Markdown data sheets.

The Markdown files in ``aerokit/materials/data/composites`` are produced by
``scripts/materials/extract_ncamp_8552_im7.py`` from NCAMP Report
NCP-RP-2013-015 Rev A (E. Clarkson, *A Comparison of Equivalence Criteria and
Basis Values for HEXCEL 8552 IM7 Unidirectional Tape computed from the NCAMP
shared database*, Oct 31, 2013). They keep the numbers exactly as printed
(ksi; percent for the coefficient of variation; specimen counts); this module
parses them with a strict parser and converts on request.

What the source provides — and what it does not
-----------------------------------------------
The report is a *strength* report. It prints, per environment (CTD, RTD,
ETD, ETW as available), qualification, pooled (ANOVA) and **generic**
B-/A-basis values, unit means and summary statistics for

* ``F1tu`` — longitudinal tension (LT, layup [0]6),
* ``F1cu`` — 0° compression strength computed from the UNC0 data (B/A only),
* ``F12su`` — in-plane shear strength at 5 % strain (IPS, [45/-45]3s),
* ``F12s0.2`` — in-plane shear 0.2 % offset strength,
* laminate tests ``UNT0``, ``UNC0``, ``OHT1``, ``OHC1`` and ``SBS``.

It prints **no** moduli (E1, E2), Poisson's ratio, G12, transverse strengths
(F2tu/F2cu, i.e. Yt/Yc), bearing data, cured ply thickness, fibre volume or
density. :func:`lamina_record` therefore returns only ``Xt``, ``Xc`` and
``S12`` from the report; the remaining keys can be taken, explicitly, from a
:data:`aerokit.materials.library.MATERIALS` record (``fill_from=``), with the
origin of every key recorded under ``"provenance"``.

Approval caveat (PDF page 12): "Generic basis values have not yet been
approved by the CMH-17 organization."

Examples
--------
>>> from aerokit.materials import composites as cm
>>> cm.get_lamina_property("IM7-8552", "F1tu", basis="B", environment="RTD", units="source")
280.74
"""

from __future__ import annotations

import functools
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

from aerokit.materials.handbook import KSI_TO_PA, MarkdownFormatError
from aerokit.references import cite

__all__ = [
    "DATA_DIR",
    "ENVIRONMENTS",
    "PROPERTIES",
    "BasisName",
    "Method",
    "Cell",
    "Column",
    "TableRow",
    "CompositeTable",
    "TestDescription",
    "CompositeSheet",
    "LaminaValue",
    "SampleStatistics",
    "MarkdownFormatError",
    "list_composites",
    "material_slug",
    "load_composite",
    "parse_composite_markdown",
    "lookup_lamina_property",
    "get_lamina_property",
    "sample_statistics",
    "lamina_record",
]

DATA_DIR: Final[Path] = Path(__file__).resolve().parent / "data" / "composites"

BasisName = Literal["A", "B", "mean"]
Method = Literal["generic", "pooled", "qualification"]
UnitSystem = Literal["SI", "source"]

ENVIRONMENTS: Final[tuple[str, ...]] = ("CTD", "RTD", "ETD", "ETW")
_KINDS: Final[frozenset[str]] = frozenset({"units", "basis", "limits", "stats"})
_STATS_ROWS: Final[tuple[str, ...]] = ("Average", "Std Dev.", "Coeff Var.", "Max", "Min", "Count")
_STATS_COLUMNS: Final[tuple[str, ...]] = ("Qual.", "A01", "A02", "A03", "A2", "A4", "A5", "A6", "A8", "A9",
                                          "A10", "A11", "A12", "Pooled")
_TEST_HEADER: Final[list[str]] = ["test", "description", "layup", "data", "environments", "pdf page"]
_FRONT_KEYS: Final[tuple[str, ...]] = ("material", "material_name", "source_document", "source_file",
                                       "source_sha256", "approval_caveat", "units", "extraction")
_CELL_RE: Final = re.compile(r"^(?:(?P<num>\d+(?:\.\d+)?)(?P<pct>%)?(?: \[(?P<m>\*)\])?|(?P<na>NA)|—)$")
_SEP_RE: Final = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+$")
_COLUMN_RE: Final = re.compile(r"^(?P<g>[^|/]+?) / (?P<e>CTD|RTD|ETD|ETW)$")

#: material aliases (normalised: lower case, no spaces) -> data-sheet slug
_MATERIAL_ALIASES: Final[dict[str, str]] = {
    "im7-8552": "ncamp-8552-im7", "im7/8552": "ncamp-8552-im7", "8552-im7": "ncamp-8552-im7",
    "8552/im7": "ncamp-8552-im7", "hexcel8552im7": "ncamp-8552-im7",
}


# --------------------------------------------------------------------------- data classes


@dataclass(frozen=True)
class Cell:
    """One table cell exactly as printed.

    Attributes
    ----------
    raw:
        Printed digits without markers (``"53.86"``, ``"5.91"``); ``"NA"`` for a
        printed NA, ``""`` when nothing is printed.
    percent:
        ``True`` if the source prints a percent sign (coefficient of variation).
    markers:
        ``("*",)`` if the value is printed with an asterisk (see the table note).
    """

    raw: str
    percent: bool = False
    markers: tuple[str, ...] = ()

    @property
    def value(self) -> float | None:
        """The printed number, or ``None`` for ``NA`` / nothing printed."""
        if not self.raw or self.raw == "NA":
            return None
        return float(self.raw)


@dataclass(frozen=True)
class Column:
    """A data column: the test header and the environment as printed."""

    group: str
    environment: str


@dataclass(frozen=True)
class TableRow:
    """One printed row with its PDF page."""

    page: int
    label: str
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class CompositeTable:
    """A source table as stored in the Markdown file.

    For ``kind == "stats"`` (summary statistics by unit) the columns are the
    units ``Qual.``, ``A01`` ... ``A12`` and ``Pooled`` and ``Column.group`` is
    the unit name with an empty environment.
    """

    table_id: int
    title: str
    kind: str
    pdf_pages: tuple[int, ...]
    extraction: str
    columns: tuple[Column, ...]
    rows: tuple[TableRow, ...]
    notes: tuple[str, ...]
    meta: Mapping[str, str]

    def column_index(self, group: str, environment: str = "") -> int:
        """Index of the column ``group / environment``.

        Raises
        ------
        KeyError
            The column does not exist in this table.
        """
        for k, c in enumerate(self.columns):
            if c.group == group and c.environment == environment:
                return k
        have = ", ".join(f"{c.group} / {c.environment}" if c.environment else c.group for c in self.columns)
        raise KeyError(f"Table {self.table_id} has no column {group!r}/{environment!r}; columns: {have}")

    def row(self, pattern: str) -> TableRow:
        """The single row whose label fully matches the regular expression ``pattern``.

        Raises
        ------
        KeyError
            No row or more than one row matches.
        """
        hits = [r for r in self.rows if re.fullmatch(pattern, r.label)]
        if len(hits) != 1:
            raise KeyError(f"Table {self.table_id}: {len(hits)} rows match {pattern!r}; "
                           f"rows: {', '.join(r.label for r in self.rows)}")
        return hits[0]


@dataclass(frozen=True)
class TestDescription:
    """One entry of the ``## Test descriptions`` section (manual transcription)."""

    test: str
    description: str
    layup: str
    data: str
    environments: str
    pdf_page: int


@dataclass(frozen=True)
class CompositeSheet:
    """Parsed content of one composite data sheet."""

    slug: str
    front_matter: Mapping[str, str]
    tests: tuple[TestDescription, ...]
    tests_extraction: str
    tables: Mapping[int, CompositeTable]

    def table(self, table_id: int) -> CompositeTable:
        """Source table by number.

        Raises
        ------
        KeyError
            The table is not in the sheet.
        """
        if table_id not in self.tables:
            raise KeyError(f"{self.slug}: no Table {table_id}; tables: {', '.join(map(str, self.tables))}")
        return self.tables[table_id]


@dataclass(frozen=True)
class LaminaValue:
    """A looked-up strength with its provenance."""

    material: str
    property: str
    basis: str
    method: str
    environment: str
    value: float
    unit: str
    raw: str
    source_unit: str
    table_id: int
    pdf_page: int
    row_label: str
    column: str
    markers: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class SampleStatistics:
    """Summary statistics of one unit column (``Qual.``, ``A01`` ... or ``Pooled``)."""

    material: str
    property: str
    environment: str
    column: str
    mean: float
    std: float
    cv_percent: float
    maximum: float
    minimum: float
    count: int
    n_units: int
    unit: str
    table_id: int
    pdf_page: int
    in_table_title: str


# --------------------------------------------------------------------------- property catalogue


@dataclass(frozen=True)
class _Prop:
    description: str
    basis_table: int
    basis_group: str
    means_table: int | None
    means_group: str | None
    stats: Mapping[str, int]


_IPS5 = "In-Plane Shear Strength @ 5% Strain"
_IPS02 = "In-Plane Shear 0.2% Offset Strength"
_SBS = "Short Beam Strength"

#: canonical property -> where it is printed (table numbers of NCP-RP-2013-015 Rev A)
_PROPS: Final[dict[str, _Prop]] = {
    "F1tu": _Prop("longitudinal (0°) tension strength, LT test, layup [0]6, normalized", 10, "LT", 9,
                  "Longitudinal Tension", {"CTD": 22, "RTD": 23, "ETW": 24}),
    "F1cu": _Prop("0° compression strength computed from the UNC0 data (NCP-RP-2009-028 Rev B formulas)", 6,
                  "0° Compression Strength from UNC0 Data", None, None, {}),
    "F12su": _Prop("in-plane shear strength at 5% strain, IPS test, layup [45/-45]3s, as measured", 14, _IPS5,
                   13, _IPS5, {"RTD": 35, "ETW": 37}),
    "F12s0.2": _Prop("in-plane shear 0.2% offset strength, IPS test, layup [45/-45]3s, as measured", 14, _IPS02,
                     13, _IPS02, {"CTD": 33, "RTD": 34, "ETW": 36}),
    "UNT0": _Prop("unnotched tension strength, layup [0/90]2s, normalized", 10, "UNT0", 9, "Unnotched Tension",
                  {"CTD": 25, "RTD": 26, "ETW": 27}),
    "UNC0": _Prop("unnotched compression strength, layup [90/0/90]5, normalized", 5, "UNC0", 4, "UNC0",
                  {"RTD": 17, "ETD": 18, "ETW": 19}),
    "OHT1": _Prop("open-hole tension strength, quasi-isotropic [45/0/-45/90]2s, normalized", 10, "OHT1", 9,
                  "Open Hole Tension", {"CTD": 28, "RTD": 29, "ETW": 30}),
    "OHC1": _Prop("open-hole compression strength, quasi-isotropic [45/0/-45/90]3S, normalized", 5, "OHC1", 4,
                  "OHC1", {"RTD": 20, "ETW": 21}),
    "SBS": _Prop("short-beam strength, layup [0]34, as measured", 14, _SBS, 13, _SBS, {"RTD": 31, "ETW": 32}),
}
PROPERTIES: Final[tuple[str, ...]] = tuple(_PROPS)

_ALIASES: Final[dict[str, str]] = {
    **{k.lower(): k for k in _PROPS},
    "xt": "F1tu", "xc": "F1cu", "s12": "F12su", "f12s5%": "F12su", "f12s0.2%": "F12s0.2", "lt": "F1tu",
    "ips": "F12su", "oht": "OHT1", "ohc": "OHC1", "unt": "UNT0", "unc": "UNC0", "ilss": "SBS",
}
#: properties a user may ask for that the report does not contain
_NOT_IN_SOURCE: Final[frozenset[str]] = frozenset({
    "e1", "e1t", "e1c", "e2", "e2t", "e2c", "nu12", "g12", "yt", "yc", "f2tu", "f2cu", "t_layer", "cpt",
    "rho", "density", "vf", "fbru", "bearing", "fiber_volume", "fibre_volume",
})

_BASIS_ROWS: Final[dict[tuple[str, str], str]] = {
    ("qualification", "B"): r"Qual(?:ification|\.) B-(?:Basis|Estimate)(?: or B-Estimate)?",
    ("qualification", "A"): r"Qualification A-Estimate",
    ("pooled", "B"): r"Pooled Data B-basis(?: \(ANOVA\))?",
    ("pooled", "A"): r"Pooled Data A-basis(?: \(ANOVA\))?",
    ("generic", "B"): r"Generic B-basis",
    ("generic", "A"): r"Generic A-basis",
}
_UNIT_MEAN_ROW: Final[str] = r"Unit Av(?:g|erage)"
_METHODS: Final[tuple[str, ...]] = ("generic", "pooled", "qualification")


def _canonical_property(name: str) -> str:
    if name in _PROPS:
        return name
    key = _ALIASES.get(str(name).strip().lower())
    if key is not None:
        return key
    if str(name).strip().lower() in _NOT_IN_SOURCE:
        raise KeyError(f"{name!r} is not reported in NCAMP NCP-RP-2013-015 Rev A (strength data only: "
                       f"{', '.join(_PROPS)})")
    raise KeyError(f"unknown property {name!r}; known: {', '.join(_PROPS)} (aliases: Xt, Xc, S12, OHT, OHC, ...)")


# --------------------------------------------------------------------------- parsing


def _split_row(line: str, lineno: int) -> list[str]:
    if not (line.startswith("|") and line.endswith("|")):
        raise MarkdownFormatError(f"line {lineno}: table row must start and end with '|': {line!r}")
    return [c.strip() for c in line[1:-1].split("|")]


def _parse_cell(text: str, lineno: int) -> Cell:
    m = _CELL_RE.fullmatch(text)
    if not m:
        raise MarkdownFormatError(f"line {lineno}: malformed value cell {text!r}")
    if m.group("na"):
        return Cell("NA")
    if m.group("num") is None:
        return Cell("")
    return Cell(m.group("num"), bool(m.group("pct")), ("*",) if m.group("m") else ())


@dataclass
class _Section:
    name: str
    lineno: int
    meta: dict[str, list[str]]
    header: list[str] | None
    separator: bool
    rows: list[tuple[int, list[str]]]


def parse_composite_markdown(text: str, slug: str | None = None) -> CompositeSheet:
    """Parse one composite data sheet with a strict line-oriented parser.

    Parameters
    ----------
    text:
        File content.
    slug:
        Expected ``material`` front-matter value (normally the file stem).

    Returns
    -------
    CompositeSheet

    Raises
    ------
    MarkdownFormatError
        On any deviation: missing front-matter keys, malformed SHA-256,
        unknown sections or headings, rows with the wrong number of cells,
        malformed numbers or markers, unknown table kind or environment,
        a row page not listed in ``pdf_page``, summary-statistics tables
        without the six statistics rows, duplicate tables.
    """
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise MarkdownFormatError("line 1: front matter must start with '---'")
    fm: dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i] != "---":
        m = re.fullmatch(r"([a-z_0-9]+): (.+)", lines[i])
        if not m:
            raise MarkdownFormatError(f"line {i + 1}: malformed front matter {lines[i]!r}")
        if m.group(1) in fm:
            raise MarkdownFormatError(f"line {i + 1}: duplicate key {m.group(1)!r}")
        fm[m.group(1)] = m.group(2)
        i += 1
    if i >= len(lines):
        raise MarkdownFormatError("front matter is not closed with '---'")
    for key in _FRONT_KEYS:
        if key not in fm:
            raise MarkdownFormatError(f"front matter lacks {key!r}")
    if slug is not None and fm["material"] != slug:
        raise MarkdownFormatError(f"front matter material {fm['material']!r} != file name {slug!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", fm["source_sha256"]):
        raise MarkdownFormatError("source_sha256 must be 64 hex digits")

    sections: list[_Section] = []
    cur: _Section | None = None
    for k in range(i + 1, len(lines)):
        ln, lineno = lines[k], k + 1
        if ln.startswith("## "):
            m = re.fullmatch(r"## (Table \d+|Test descriptions)", ln)
            if not m:
                raise MarkdownFormatError(f"line {lineno}: unknown section {ln!r}")
            cur = _Section(m.group(1), lineno, {}, None, False, [])
            sections.append(cur)
            continue
        if ln.startswith("#") and cur is not None:
            raise MarkdownFormatError(f"line {lineno}: unexpected heading {ln!r}")
        if cur is None or not ln.strip():
            continue  # title and prose before the first section
        if ln.startswith("- "):
            if cur.header is not None:
                raise MarkdownFormatError(f"line {lineno}: metadata after the table: {ln!r}")
            m = re.fullmatch(r"- ([a-z_]+): (.+)", ln)
            if not m:
                raise MarkdownFormatError(f"line {lineno}: malformed metadata {ln!r}")
            cur.meta.setdefault(m.group(1), []).append(m.group(2))
            continue
        if ln.startswith("|"):
            cells = _split_row(ln, lineno)
            if cur.header is None:
                cur.header = cells
            elif not cur.separator:
                if not _SEP_RE.fullmatch(ln.replace(" ", "")) or len(cells) != len(cur.header):
                    raise MarkdownFormatError(f"line {lineno}: expected a separator row with {len(cur.header)} "
                                              "cells after the header")
                cur.separator = True
            else:
                if len(cells) != len(cur.header):
                    raise MarkdownFormatError(
                        f"line {lineno}: {len(cells)} cells but the header has {len(cur.header)}")
                cur.rows.append((lineno, cells))
            continue
        raise MarkdownFormatError(f"line {lineno}: unexpected text {ln!r}")

    tests: tuple[TestDescription, ...] = ()
    tests_extraction = ""
    tables: dict[int, CompositeTable] = {}
    for s in sections:
        if s.name == "Test descriptions":
            if tests:
                raise MarkdownFormatError(f"line {s.lineno}: duplicate 'Test descriptions' section")
            tests, tests_extraction = _build_tests(s)
        else:
            tab = _build_table(s)
            if tab.table_id in tables:
                raise MarkdownFormatError(f"line {s.lineno}: duplicate Table {tab.table_id}")
            tables[tab.table_id] = tab
    if not tables:
        raise MarkdownFormatError("no '## Table' section found")
    return CompositeSheet(fm["material"], dict(fm), tests, tests_extraction, tables)


def _one(s: _Section, key: str) -> str:
    vals = s.meta.get(key, [])
    if len(vals) != 1:
        raise MarkdownFormatError(f"{s.name} (line {s.lineno}): expected exactly one '- {key}:' line, "
                                  f"got {len(vals)}")
    return vals[0]


def _body(s: _Section) -> tuple[list[str], list[tuple[int, list[str]]]]:
    if s.header is None or not s.separator or not s.rows:
        raise MarkdownFormatError(f"{s.name} (line {s.lineno}): missing table, separator or rows")
    return s.header, s.rows


def _build_tests(s: _Section) -> tuple[tuple[TestDescription, ...], str]:
    header, rows = _body(s)
    if header != _TEST_HEADER:
        raise MarkdownFormatError(f"{s.name}: header must be {_TEST_HEADER}, got {header}")
    extraction = _one(s, "extraction")
    if not extraction.startswith(("manual", "automatic")):
        raise MarkdownFormatError(f"{s.name}: extraction must start with 'manual' or 'automatic'")
    out = []
    for lineno, c in rows:
        if not c[5].isdigit() or not all(c[:5]):
            raise MarkdownFormatError(f"line {lineno}: malformed test description row")
        out.append(TestDescription(c[0], c[1], c[2], c[3], c[4], int(c[5])))
    return tuple(out), extraction


def _build_table(s: _Section) -> CompositeTable:
    table_id = int(s.name.split()[1])
    header, rows = _body(s)
    kind = _one(s, "kind")
    if kind not in _KINDS:
        raise MarkdownFormatError(f"{s.name}: unknown kind {kind!r}; expected one of {sorted(_KINDS)}")
    extraction = _one(s, "extraction")
    if extraction not in ("automatic", "manual"):
        raise MarkdownFormatError(f"{s.name}: extraction must be 'automatic' or 'manual', got {extraction!r}")
    pages_text = _one(s, "pdf_page")
    if not re.fullmatch(r"\d+(?:, \d+)*", pages_text):
        raise MarkdownFormatError(f"{s.name}: pdf_page must be a comma-separated list of integers")
    pages = tuple(int(p) for p in pages_text.split(", "))
    if header[:2] != ["page", "row"] or len(header) < 3:
        raise MarkdownFormatError(f"{s.name}: header must start with 'page | row' and have data columns")
    columns: list[Column] = []
    if kind == "stats":
        if tuple(header[2:]) != _STATS_COLUMNS:
            raise MarkdownFormatError(f"{s.name}: statistics columns must be {list(_STATS_COLUMNS)}")
        columns = [Column(h, "") for h in header[2:]]
    else:
        for h in header[2:]:
            m = _COLUMN_RE.fullmatch(h)
            if not m:
                raise MarkdownFormatError(f"{s.name}: column {h!r} must be '<test> / CTD|RTD|ETD|ETW'")
            columns.append(Column(m.group("g"), m.group("e")))
        if len(set(columns)) != len(columns):
            raise MarkdownFormatError(f"{s.name}: duplicate columns")
    out: list[TableRow] = []
    for lineno, cells in rows:
        if not cells[0].isdigit() or int(cells[0]) not in pages:
            raise MarkdownFormatError(f"line {lineno}: page {cells[0]!r} is not one of pdf_page {pages}")
        if not cells[1]:
            raise MarkdownFormatError(f"line {lineno}: empty row label")
        out.append(TableRow(int(cells[0]), cells[1], tuple(_parse_cell(c, lineno) for c in cells[2:])))
    labels = [r.label for r in out]
    if len(set(labels)) != len(labels):
        raise MarkdownFormatError(f"{s.name}: duplicate row labels")
    if kind == "stats" and tuple(labels) != _STATS_ROWS:
        raise MarkdownFormatError(f"{s.name}: statistics rows must be {list(_STATS_ROWS)}, got {labels}")
    meta = {k: v[0] for k, v in s.meta.items() if k not in ("note",) and len(v) == 1}
    return CompositeTable(table_id, _one(s, "title"), kind, pages, extraction, tuple(columns), tuple(out),
                          tuple(s.meta.get("note", [])), meta)


# --------------------------------------------------------------------------- loading


@functools.lru_cache(maxsize=1)
def list_composites() -> tuple[str, ...]:
    """Composite data-sheet identifiers in :data:`DATA_DIR` (file stems, sorted)."""
    return tuple(sorted(p.stem for p in DATA_DIR.glob("*.md")))


def material_slug(material: str) -> str:
    """Data-sheet identifier of ``material`` (``"IM7-8552"`` -> ``"ncamp-8552-im7"``).

    Raises
    ------
    KeyError
        Unknown material; the message lists the available sheets and aliases.
    """
    if not isinstance(material, str) or not material.strip():
        raise KeyError("material must be a non-empty string")
    key = re.sub(r"\s+", "", material.strip().lower())
    slug = _MATERIAL_ALIASES.get(key, key)
    if slug not in list_composites():
        raise KeyError(f"unknown composite {material!r}; available: {', '.join(list_composites())} "
                       f"(aliases: {', '.join(sorted(_MATERIAL_ALIASES))})")
    return slug


@functools.lru_cache(maxsize=16)
def _load_slug(slug: str) -> CompositeSheet:
    text = (DATA_DIR / f"{slug}.md").read_text(encoding="utf-8")
    return parse_composite_markdown(text, slug)


def load_composite(material: str) -> CompositeSheet:
    """Load and parse one composite data sheet (cached per sheet, so aliases share one object).

    Parameters
    ----------
    material:
        Sheet identifier or alias, e.g. ``"ncamp-8552-im7"`` or ``"IM7-8552"``.

    Raises
    ------
    KeyError
        Unknown material.
    MarkdownFormatError
        The file is malformed.
    """
    return _load_slug(material_slug(material))


# --------------------------------------------------------------------------- lookup


def _as_basis(basis: str) -> str:
    b = str(basis).strip()
    if b.upper() in ("A", "B"):
        return b.upper()
    if b.lower() == "mean":
        return "mean"
    raise ValueError(f"basis must be 'A', 'B' or 'mean', got {basis!r}")


def _as_method(method: str) -> str:
    m = str(method).strip().lower()
    if m not in _METHODS:
        raise ValueError(f"method must be one of {', '.join(_METHODS)}, got {method!r}")
    return m


def _as_environment(environment: str) -> str:
    e = str(environment).strip().upper()
    if e not in ENVIRONMENTS:
        raise ValueError(f"environment must be one of {', '.join(ENVIRONMENTS)}, got {environment!r}")
    return e


def _environments(sheet: CompositeSheet, prop: _Prop) -> list[str]:
    tab = sheet.table(prop.basis_table)
    return [c.environment for c in tab.columns if c.group == prop.basis_group]


def _convert(value: float, units: str) -> tuple[float, str]:
    if units == "source":
        return value, "ksi"
    if units == "SI":
        return value * KSI_TO_PA, "Pa"
    raise ValueError(f"units must be 'SI' or 'source', got {units!r}")


@cite("ncamp_2013_8552_im7", note="Tables 4-16 (basis values, unit means), 17-37 (summary statistics)")
def lookup_lamina_property(
    material: str,
    property: str,
    basis: BasisName | str = "B",
    environment: str = "RTD",
    units: UnitSystem = "SI",
    *,
    method: Method | str = "generic",
) -> LaminaValue:
    """Look up one NCAMP strength value with full provenance.

    Parameters
    ----------
    material:
        Composite identifier or alias (``"IM7-8552"``, ``"ncamp-8552-im7"``).
    property:
        ``F1tu`` (alias ``Xt``), ``F1cu`` (``Xc``), ``F12su`` (``S12``; strength
        at 5 % strain), ``F12s0.2`` (0.2 % offset), ``UNT0``, ``UNC0``,
        ``OHT1`` (``OHT``), ``OHC1`` (``OHC``) or ``SBS``.
    basis:
        ``"B"``, ``"A"`` or ``"mean"``.
    environment:
        ``"CTD"``, ``"RTD"``, ``"ETD"`` or ``"ETW"`` (as tested for the property).
    units:
        ``"SI"`` (Pa) or ``"source"`` (ksi exactly as printed).
    method:
        ``"generic"`` (default; the report's generic basis values, *not approved
        by CMH-17*), ``"pooled"`` (pooled data, ANOVA) or ``"qualification"``
        (qualification sample; some values are printed as estimates, see
        ``row_label``). For ``basis="mean"``: generic -> the average of the unit
        means ("Unit Average"/"Unit Avg"), pooled -> pooled-dataset average,
        qualification -> average of the qualification data (``Qual.`` column).

    Returns
    -------
    LaminaValue

    Raises
    ------
    KeyError
        Unknown material or property, a property not in the report (E1, nu12,
        G12, Yc, ...), a property not tested in ``environment``, or a value the
        report does not print for this basis/method (e.g. the mean of ``F1cu``).
    ValueError
        Invalid ``basis``, ``environment``, ``method`` or ``units``.

    Notes
    -----
    A ``"*"`` marker means the generic value was computed with the alternate
    method (large within-company variance), as noted under the source table.
    """
    sheet = load_composite(material)
    name = _canonical_property(property)
    prop = _PROPS[name]
    b = _as_basis(basis)
    env = _as_environment(environment)
    meth = _as_method(method)
    if units not in ("SI", "source"):
        raise ValueError(f"units must be 'SI' or 'source', got {units!r}")
    envs = _environments(sheet, prop)
    if env not in envs:
        raise KeyError(f"{name} is not tested in {env} in {sheet.slug}; environments: {', '.join(envs)}")
    note = sheet.front_matter["approval_caveat"] if meth == "generic" and b != "mean" else ""
    if b != "mean":
        tab = sheet.table(prop.basis_table)
        try:
            row = tab.row(_BASIS_ROWS[(meth, b)])
        except KeyError:
            raise KeyError(f"{name}: Table {tab.table_id} prints no {meth} {b}-basis row; rows: "
                           f"{', '.join(r.label for r in tab.rows)}") from None
        col = tab.column_index(prop.basis_group, env)
        col_name = f"{prop.basis_group} / {env}"
    elif meth == "generic":
        if prop.means_table is None or prop.means_group is None:
            raise KeyError(f"{name}: the report prints no mean value (only B/A values in Table {prop.basis_table})")
        tab = sheet.table(prop.means_table)
        row = tab.row(_UNIT_MEAN_ROW)
        col = tab.column_index(prop.means_group, env)
        col_name = f"{prop.means_group} / {env}"
    else:
        if env not in prop.stats:
            raise KeyError(f"{name}: no summary statistics table for {env}")
        tab = sheet.table(prop.stats[env])
        row = tab.row("Average")
        col_name = "Pooled" if meth == "pooled" else "Qual."
        col = tab.column_index(col_name)
    cell = row.cells[col]
    if cell.value is None:
        raise KeyError(f"{name} {b} ({meth}, {env}) is not printed (cell {cell.raw or 'empty'!r}) in "
                       f"Table {tab.table_id}, PDF page {row.page}")
    if "*" in cell.markers and tab.notes:
        note = (note + " " if note else "") + "; ".join(tab.notes)
    value, unit = _convert(cell.value, units)
    return LaminaValue(material=sheet.slug, property=name, basis=b, method=meth, environment=env, value=value,
                       unit=unit, raw=cell.raw, source_unit="ksi", table_id=tab.table_id, pdf_page=row.page,
                       row_label=row.label, column=col_name, markers=cell.markers, note=note)


@cite("ncamp_2013_8552_im7")
def get_lamina_property(
    material: str,
    property: str,
    basis: BasisName | str = "B",
    environment: str = "RTD",
    units: UnitSystem = "SI",
    *,
    method: Method | str = "generic",
) -> float:
    """Return one NCAMP strength value as ``float`` (Pa with ``units="SI"``, ksi with ``"source"``).

    Same parameters and errors as :func:`lookup_lamina_property`, which also
    returns the provenance (table, PDF page, row label, markers).

    Examples
    --------
    >>> get_lamina_property("IM7-8552", "S12", "B", "ETW", units="source")  # doctest: +SKIP
    4.68
    """
    return lookup_lamina_property(material, property, basis, environment, units, method=method).value


@cite("ncamp_2013_8552_im7", note="Tables 17-37, summary statistics by unit")
def sample_statistics(material: str, property: str, environment: str = "RTD", column: str = "Pooled",
                      units: UnitSystem = "SI") -> SampleStatistics:
    """Mean, standard deviation, CV, extremes and specimen count of one unit column.

    Parameters
    ----------
    material, property, environment:
        As for :func:`lookup_lamina_property` (``F1cu`` has no statistics table).
    column:
        ``"Pooled"`` (default, all units), ``"Qual."`` (qualification data) or a
        unit ``"A01"`` ... ``"A12"``.
    units:
        ``"SI"`` (Pa) or ``"source"`` (ksi) for mean, std, max and min.

    Returns
    -------
    SampleStatistics
        ``n_units`` counts the unit columns A01 ... A12 with a printed count.

    Raises
    ------
    KeyError
        Unknown material/property/column, or no statistics for ``environment``.
    ValueError
        Invalid environment or units.
    """
    sheet = load_composite(material)
    name = _canonical_property(property)
    env = _as_environment(environment)
    prop = _PROPS[name]
    if env not in prop.stats:
        raise KeyError(f"{name}: no summary statistics for {env}; available: {', '.join(prop.stats) or 'none'}")
    tab = sheet.table(prop.stats[env])
    col = tab.column_index(column)
    vals: dict[str, Cell] = {r.label: r.cells[col] for r in tab.rows}
    numbers = {k: c.value for k, c in vals.items()}
    if any(v is None for v in numbers.values()):
        raise KeyError(f"{name} {env}: column {column!r} of Table {tab.table_id} prints NA")
    count_row = tab.row("Count")
    n_units = sum(1 for k, c in enumerate(tab.columns)
                  if re.fullmatch(r"A\d+", c.group) and count_row.cells[k].value is not None)
    conv: dict[str, float] = {}
    unit = "ksi"
    for k in ("Average", "Std Dev.", "Max", "Min"):
        raw = numbers[k]
        if raw is None:  # excluded above; explicit for type narrowing and python -O
            raise KeyError(f"{name} {env}: {k} not printed")
        conv[k], unit = _convert(raw, units)
    cv, cnt = numbers["Coeff Var."], numbers["Count"]
    if cv is None or cnt is None or not vals["Coeff Var."].percent or not float(cnt).is_integer():
        raise MarkdownFormatError(f"Table {tab.table_id}: malformed Coeff Var./Count in column {column!r}")
    return SampleStatistics(material=sheet.slug, property=name, environment=env, column=column,
                            mean=conv["Average"], std=conv["Std Dev."], cv_percent=cv, maximum=conv["Max"],
                            minimum=conv["Min"], count=int(cnt), n_units=n_units, unit=unit,
                            table_id=tab.table_id, pdf_page=tab.rows[0].page,
                            in_table_title=tab.meta.get("in_table_title", ""))


#: lamina-record key -> NCAMP property
_RECORD_KEYS: Final[dict[str, str]] = {"Xt": "F1tu", "Xc": "F1cu", "S12": "F12su"}
#: record keys the report never provides
_FILL_KEYS: Final[tuple[str, ...]] = ("E1", "E2", "nu12", "G12", "Yt", "Yc", "t_layer", "rho")


@cite("ncamp_2013_8552_im7", note="Xt: Table 10 (LT); Xc: Table 6; S12: Table 14 (IPS at 5% strain)")
def lamina_record(
    material: str = "IM7-8552",
    basis: BasisName | str = "B",
    environment: str = "RTD",
    *,
    method: Method | str = "generic",
    fill_from: str | None = None,
) -> dict[str, Any]:
    """Lamina record (SI) with the strength keys of :data:`aerokit.materials.library.MATERIALS`.

    Parameters
    ----------
    material:
        Composite identifier or alias.
    basis:
        ``"B"``, ``"A"`` or ``"mean"`` (``Xc`` has no mean in the report, so
        ``"mean"`` raises).
    environment:
        Environment; only ``"RTD"`` and ``"ETW"`` have all of Xt, Xc and S12.
    method:
        ``"generic"``, ``"pooled"`` or ``"qualification"`` (see
        :func:`lookup_lamina_property`).
    fill_from:
        Optional :mod:`aerokit.materials.library` catalogue name (e.g.
        ``"IM7-8552"``) whose ``E1, E2, nu12, G12, Yt, Yc, t_layer, rho`` fill
        the keys the NCAMP report does not provide. Without it the record holds
        only ``Xt``, ``Xc``, ``S12`` and cannot be used for stiffness (CLT).

    Returns
    -------
    dict
        ``Xt, Xc, S12`` [Pa] from the report, the filled keys (if any),
        ``name``, ``source``, ``basis``, ``method``, ``environment``,
        ``provenance`` (key -> table/page or catalogue origin), ``unverified``
        (fields flagged unverified in the catalogue, the CMH-17 approval caveat
        for generic values, and environment mismatches) and ``missing`` (record
        keys not supplied).

    Raises
    ------
    KeyError
        Unknown material or ``fill_from`` name, or one of Xt/Xc/S12 is not
        printed for this basis, method and environment.
    ValueError
        Invalid basis, environment or method.
    """
    sheet = load_composite(material)
    b, env, meth = _as_basis(basis), _as_environment(environment), _as_method(method)
    out: dict[str, Any] = {}
    provenance: dict[str, str] = {}
    unverified: list[str] = []
    problems: list[str] = []
    for key, prop in _RECORD_KEYS.items():
        try:
            v = lookup_lamina_property(sheet.slug, prop, b, env, "SI", method=meth)
        except KeyError as exc:
            problems.append(f"{key} ({prop}): {exc.args[0] if exc.args else exc}")
            continue
        out[key] = v.value
        star = " [*: alternate generic method]" if v.markers else ""
        provenance[key] = (f"NCAMP NCP-RP-2013-015 Rev A Table {v.table_id}, PDF p. {v.pdf_page}, "
                           f"'{v.row_label}', {v.column} = {v.raw} ksi{star}")
    if problems:
        complete = [e for e in ENVIRONMENTS if all(e in _environments(sheet, _PROPS[p]) for p in _RECORD_KEYS.values())]
        raise KeyError(f"lamina_record({sheet.slug!r}, {b!r}, {env!r}, method={meth!r}) is incomplete: "
                       + "; ".join(problems) + f". Environments with Xt, Xc and S12: {', '.join(complete)}")
    if meth == "generic":
        unverified.append("Xt, Xc, S12: generic basis values, not approved by CMH-17 (report PDF page 12)")
    missing: list[str] = []
    source = f"{sheet.front_matter['source_document']} (Xt, Xc, S12)"
    if fill_from is not None:
        from aerokit.materials import library  # local import: library is optional for this module
        rec = library.find(fill_from)
        filled = [k for k in _FILL_KEYS if k in rec]
        for k in filled:
            out[k] = rec[k]
            provenance[k] = f"aerokit.materials.library.MATERIALS[{fill_from!r}] ({rec.get('source', '')})"
        flagged = [str(u) for u in rec.get("unverified", []) if str(u).split()[0] in filled]
        unverified += [f"{u} (from library record {fill_from!r})" for u in flagged]
        if env != "RTD" and filled:
            unverified.append(f"{', '.join(filled)} come from {rec.get('name', fill_from)!r}, not from {env} tests")
        missing = [k for k in _FILL_KEYS if k not in rec]
        source += f"; {', '.join(filled)} from library record {fill_from!r}"
    else:
        missing = list(_FILL_KEYS)
    for k, v in out.items():
        if not (isinstance(v, int | float) and math.isfinite(float(v))):
            raise ValueError(f"lamina_record: {k} = {v!r} is not a finite number")
    out.update(name=f"{sheet.front_matter['material_name']} — {meth} {b}, {env}", source=source, basis=b,
               method=meth, environment=env, provenance=provenance, unverified=unverified, missing=missing)
    return out
