"""Reader for MIL-HDBK-5J design allowables stored as Markdown data sheets.

The Markdown files in ``aerokit/materials/data`` are produced by
``scripts/materials/extract_mil_hdbk_5.py`` from MIL-HDBK-5J, *Metallic
Materials and Elements for Aerospace Vehicle Structures*, 31 January 2003
(Distribution Statement A). They keep the values exactly as printed in the
source (ksi, 10³ ksi, percent, lb/in.³); this module parses them with a strict
parser and converts on request.

Basis definitions (MIL-HDBK-5J, PDF page 1415 / printed 9-9 and PDF page 1684 /
printed A-6): **A-basis** is the lower of the statistically calculated T99
value and the specification minimum (S-basis); **B-basis** is the T90 value
(90 % of the population, 95 % confidence); **S-basis** is the specification
minimum. Hence ``A <= B`` and ``A <= S``; there is no fixed order between B and
S. Elongation values are S-values; moduli and physical properties are typical
values (Section 1.4.1.1, PDF page 19 / printed 1-7).

Examples
--------
>>> from aerokit.materials import handbook as hb
>>> hb.get_allowable("al-2024-t3", "Ftu", basis="A", direction="L",
...                  thickness=0.05, thickness_units="in", units="source")
64.0
"""

from __future__ import annotations

import enum
import functools
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, overload

import numpy as np
import numpy.typing as npt

from aerokit.references import cite

__all__ = [
    "DATA_DIR",
    "KSI_TO_PA",
    "LB_PER_IN3_TO_KG_PER_M3",
    "INCH_TO_M",
    "Basis",
    "Direction",
    "Cell",
    "ThicknessRange",
    "TableRow",
    "SourceTable",
    "RambergOsgoodEntry",
    "FigureRef",
    "MaterialSheet",
    "Allowable",
    "MarkdownFormatError",
    "list_materials",
    "load_material",
    "parse_material_markdown",
    "format_material_markdown",
    "get_allowable",
    "lookup_allowable",
    "ksi_to_pa",
    "ramberg_osgood_strain",
    "ramberg_osgood_stress",
    "ramberg_osgood_tangent_modulus",
    "ramberg_osgood_curve",
    "get_ramberg_osgood_n",
    "stress_strain_curve",
]

DATA_DIR: Final[Path] = Path(__file__).resolve().parent / "data"

#: 1 ksi = 1000 lbf/in² with 1 lbf = 4.4482216152605 N and 1 in = 0.0254 m (exact definitions).
KSI_TO_PA: Final[float] = 1000.0 * 4.4482216152605 / 0.0254**2
#: 1 lb/in³ with 1 lb = 0.45359237 kg (exact) and 1 in = 0.0254 m.
LB_PER_IN3_TO_KG_PER_M3: Final[float] = 0.45359237 / 0.0254**3
INCH_TO_M: Final[float] = 0.0254

UnitSystem = Literal["SI", "source"]
LengthUnit = Literal["m", "mm", "in"]


class Basis(enum.Enum):
    """Design-value basis (MIL-HDBK-5J Section 1.4.1.1 and Appendix A)."""

    A = "A"
    B = "B"
    S = "S"


class Direction(enum.Enum):
    """Grain direction as labelled in MIL-HDBK-5J tables."""

    L = "L"
    LT = "LT"
    ST = "ST"
    T = "T"


class MarkdownFormatError(ValueError):
    """A material Markdown file does not follow the strict data-sheet layout."""


# --------------------------------------------------------------------------- properties

#: canonical property -> (unit as printed in the source, directional?)
_PROPERTIES: Final[dict[str, tuple[str, bool]]] = {
    "Ftu": ("ksi", True),
    "Fty": ("ksi", True),
    "Fcy": ("ksi", True),
    "Fsu": ("ksi", False),
    "Fbru": ("ksi", False),
    "Fbry": ("ksi", False),
    "e": ("percent", True),
    "E": ("10³ ksi", False),
    "Ec": ("10³ ksi", False),
    "G": ("10³ ksi", False),
    "nu": ("", False),
    "rho": ("lb/in.³", False),
}
_DISPLAY_TO_PROP: Final[dict[str, str]] = {"μ": "nu", "ω": "rho"}
_ALIASES: Final[dict[str, str]] = {
    "ftu": "Ftu", "fty": "Fty", "fcy": "Fcy", "fsu": "Fsu", "fbru": "Fbru", "fbry": "Fbry",
    "e": "e", "elongation": "e", "E": "E", "ec": "Ec", "Ec": "Ec", "g": "G", "G": "G",
    "nu": "nu", "mu": "nu", "μ": "nu", "poisson": "nu", "rho": "rho", "density": "rho",
    "omega": "rho", "ω": "rho",
}
_PHYSICAL: Final[frozenset[str]] = frozenset({"E", "Ec", "G", "nu", "rho"})
_ATTRIBUTE_COLUMNS: Final[dict[str, str]] = {
    "alloy": "alloy",
    "specification": "specification",
    "form": "form",
    "temper": "temper",
    "condition": "condition",
    "thickness (in.)": "thickness",
}
_PROP_HEADER_RE: Final = re.compile(
    r"^(?P<p>Ftu|Fty|Fcy|Fsu|Fbru|Fbry|e|E|Ec|G|μ|ω)"
    r"(?: (?P<q>L|LT|ST|T|e/D=1\.5|e/D=2\.0))?"
    r"(?: \((?P<u>[^()]+)\))?$"
)
_VALUE_RE: Final = re.compile(r"^(?:(?P<num>\d+(?:\.\d+)?|\.\d+)|—)(?: \[(?P<fn>[a-z](?:,[a-z])*)\])?$")
_ATTR_RE: Final = re.compile(r"^(?P<text>[^\[\]|]*?)(?: \[(?P<fn>[a-z](?:,[a-z])*)\])?$")
_SEP_RE: Final = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+$")


def _canonical_property(name: str) -> str:
    if name in _PROPERTIES:
        return name
    key = _ALIASES.get(name, _ALIASES.get(name.lower()))
    if key is None:
        raise KeyError(f"unknown property {name!r}; known: {', '.join(_PROPERTIES)} "
                       "(aliases: elongation, mu, density, ...)")
    return key


# --------------------------------------------------------------------------- data classes


@dataclass(frozen=True)
class Cell:
    """One table cell exactly as printed.

    Attributes
    ----------
    raw:
        The printed digits (``""`` when the source prints ``...`` or nothing).
    footnotes:
        Footnote markers attached to the value, e.g. ``("a",)``.
    """

    raw: str
    footnotes: tuple[str, ...] = ()

    @property
    def value(self) -> float | None:
        """The printed number as ``float`` or ``None`` when nothing is printed."""
        return float(self.raw) if self.raw else None


@dataclass(frozen=True)
class ThicknessRange:
    """A thickness range as printed (inches) with a half-last-digit tolerance.

    ``0.250-0.499`` covers ``[0.2495, 0.4995)`` in., so adjacent printed ranges
    tile the thickness axis without gaps or overlaps.
    """

    text: str
    lo: float
    hi: float

    @staticmethod
    def parse(text: str) -> ThicknessRange | None:
        """Parse ``a-b``, ``≤b``, ``<b``, ``≥a`` or ``>a``; ``None`` if not a range."""
        t = text.replace(" ", "")

        def half(s: str) -> float:
            return 0.5 * 10.0 ** -(len(s.split(".")[1]) if "." in s else 0)

        m = re.fullmatch(r"(\d*\.?\d+)-(\d*\.?\d+)", t)
        if m:
            a, b = m.group(1), m.group(2)
            return ThicknessRange(text, float(a) - half(a), float(b) + half(b))
        m = re.fullmatch(r"[≤<](\d*\.?\d+)", t)
        if m:
            return ThicknessRange(text, 0.0, float(m.group(1)) + half(m.group(1)))
        m = re.fullmatch(r"[≥>](\d*\.?\d+)", t)
        if m:
            b = m.group(1)
            lo = float(b) + half(b) if t[0] == ">" else float(b) - half(b)
            return ThicknessRange(text, lo, math.inf)
        return None

    def contains(self, thickness_in: float) -> bool:
        """``True`` if ``thickness_in`` (inches) lies in ``[lo, hi)``."""
        return self.lo <= thickness_in < self.hi


@dataclass(frozen=True)
class TableRow:
    """One source-table column (one thickness range and basis)."""

    column: int
    basis: Basis
    attributes: Mapping[str, Cell]
    values: Mapping[str, Cell]

    def attribute(self, key: str) -> str:
        """Printed text of ``alloy``/``specification``/``form``/``temper``/``condition``/``thickness``."""
        cell = self.attributes.get(key)
        return cell.raw if cell is not None else ""

    @property
    def thickness(self) -> ThicknessRange | None:
        return ThicknessRange.parse(self.attribute("thickness"))


@dataclass(frozen=True)
class SourceTable:
    """A MIL-HDBK-5J table (one PDF page) as stored in the Markdown file."""

    table_id: str
    title: str
    pdf_page: int
    printed_page: str
    elongation_label: str
    columns: tuple[str, ...]
    rows: tuple[TableRow, ...]
    notes: tuple[str, ...]
    footnotes: Mapping[str, str]

    @property
    def elongation_is_s_basis(self) -> bool:
        return "S-basis" in self.elongation_label


@dataclass(frozen=True)
class RambergOsgoodEntry:
    """A Ramberg-Osgood exponent read from a typical stress-strain figure."""

    figure: str
    pdf_page: int
    caption: str
    thickness: str
    curve: str
    n: float
    n_raw: str
    yield_raw: str

    @property
    def loading(self) -> str | None:
        """``"tension"``, ``"compression"`` or ``None`` if neither label nor caption says."""
        low = self.curve.lower()
        if "tension" in low:
            return "tension"
        if "comp" in low:
            return "compression"
        cap = self.caption.lower()
        tens, comp = "tensile" in cap or "tension" in cap, "compressive" in cap or "compression" in cap
        if tens and not comp:
            return "tension"
        if comp and not tens:
            return "compression"
        return None

    @property
    def directions(self) -> frozenset[str]:
        return frozenset(re.findall(r"\b(LT|ST|L|T)\b", self.curve.replace("-", " ")))

    @property
    def room_temperature(self) -> bool:
        if re.search(r"-?\d+\s*°?\s*F\b|\bhr\b", self.curve):
            return False
        return "RT" in self.curve or "room temperature" in self.caption.lower()


@dataclass(frozen=True)
class FigureRef:
    """A figure page PNG listed in a material file."""

    figure: str
    pdf_page: int
    file: str
    caption: str


@dataclass(frozen=True)
class MaterialSheet:
    """Parsed content of one material Markdown file."""

    slug: str
    front_matter: Mapping[str, str]
    tables: tuple[SourceTable, ...]
    ramberg_osgood: tuple[RambergOsgoodEntry, ...]
    figures: tuple[FigureRef, ...]

    @property
    def alloy(self) -> str:
        return self.front_matter["alloy"]

    @property
    def temper(self) -> str:
        return self.front_matter["temper_or_condition"]


@dataclass(frozen=True)
class Allowable:
    """A looked-up value with its provenance."""

    material: str
    property: str
    value: float
    unit: str
    raw: str
    source_unit: str
    basis: Basis | None
    direction: str | None
    table_id: str
    pdf_page: int
    printed_page: str
    column: int
    form: str
    specification: str
    thickness: str
    footnotes: tuple[str, ...]


# --------------------------------------------------------------------------- parsing


def _split_row(line: str, lineno: int) -> list[str]:
    if not (line.startswith("|") and line.endswith("|")):
        raise MarkdownFormatError(f"line {lineno}: table row must start and end with '|': {line!r}")
    return [c.strip() for c in line[1:-1].split("|")]


def _parse_value(text: str, lineno: int) -> Cell:
    m = _VALUE_RE.fullmatch(text)
    if not m:
        raise MarkdownFormatError(f"line {lineno}: malformed value cell {text!r}")
    fns = tuple(m.group("fn").split(",")) if m.group("fn") else ()
    return Cell(m.group("num") or "", fns)


def _parse_attr(text: str, lineno: int) -> Cell:
    m = _ATTR_RE.fullmatch(text)
    if not m or not m.group("text"):
        raise MarkdownFormatError(f"line {lineno}: malformed attribute cell {text!r}")
    fns = tuple(m.group("fn").split(",")) if m.group("fn") else ()
    raw = m.group("text")
    return Cell("" if raw == "—" else raw, fns)


def _column_key(header: str, lineno: int) -> str:
    m = _PROP_HEADER_RE.fullmatch(header)
    if not m:
        raise MarkdownFormatError(f"line {lineno}: unknown column {header!r}")
    prop = _DISPLAY_TO_PROP.get(m.group("p"), m.group("p"))
    unit = m.group("u") or ""
    if unit != _PROPERTIES[prop][0]:
        raise MarkdownFormatError(
            f"line {lineno}: column {header!r} must carry unit {_PROPERTIES[prop][0]!r}, got {unit!r}")
    return prop + (" " + m.group("q") if m.group("q") else "")


@dataclass
class _Section:
    kind: str
    name: str
    meta: dict[str, list[str]]
    header: list[str] | None
    rows: list[tuple[int, list[str]]]
    footnotes: dict[str, str]


def parse_material_markdown(text: str, slug: str | None = None) -> MaterialSheet:
    """Parse one material data sheet with a strict line-oriented parser.

    Parameters
    ----------
    text:
        File content.
    slug:
        Expected ``material`` front-matter value (normally the file stem).

    Returns
    -------
    MaterialSheet

    Raises
    ------
    MarkdownFormatError
        On any deviation: missing front matter keys, rows with the wrong
        number of cells, malformed numbers or footnote markers, unknown
        columns or units, non-increasing column numbers, unknown basis.
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
    for key in ("material", "alloy", "temper_or_condition", "source_document", "source_sha256", "source_tables"):
        if key not in fm:
            raise MarkdownFormatError(f"front matter lacks {key!r}")
    if slug is not None and fm["material"] != slug:
        raise MarkdownFormatError(f"front matter material {fm['material']!r} != file name {slug!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", fm["source_sha256"]):
        raise MarkdownFormatError("source_sha256 must be 64 hex digits")

    sections: list[_Section] = []
    cur: _Section | None = None
    in_footnotes = False
    for k in range(i + 1, len(lines)):
        ln, lineno = lines[k], k + 1
        if ln.startswith("## "):
            in_footnotes = False
            m = re.fullmatch(r"## Table (\d+\.\d+\.\d+\.\d+\([a-z]\d?\))", ln)
            if m:
                cur = _Section("table", m.group(1), {}, None, [], {})
            elif ln == "## Ramberg-Osgood parameters":
                cur = _Section("ro-intro", "", {}, None, [], {})
            elif ln == "## Figures":
                cur = _Section("figures", "", {}, None, [], {})
            else:
                raise MarkdownFormatError(f"line {lineno}: unknown section {ln!r}")
            sections.append(cur)
            continue
        if ln.startswith("### "):
            m = re.fullmatch(r"### Footnotes to Table (\S+) \(as printed\)", ln)
            if m and cur is not None and cur.kind == "table" and m.group(1) == cur.name:
                in_footnotes = True
                continue
            m = re.fullmatch(r"### Figure (\S+)", ln)
            if m and cur is not None and cur.kind in ("ro-intro", "ro"):
                cur = _Section("ro", m.group(1), {}, None, [], {})
                sections.append(cur)
                in_footnotes = False
                continue
            raise MarkdownFormatError(f"line {lineno}: unexpected heading {ln!r}")
        if cur is None or not ln.strip():
            continue
        if in_footnotes:
            m = re.fullmatch(r"- (?:([a-z]): )?(.+)", ln)
            if not m:
                raise MarkdownFormatError(f"line {lineno}: malformed footnote {ln!r}")
            cur.footnotes[m.group(1) or ""] = m.group(2)
            continue
        if ln.startswith("- "):
            if cur.header is not None:
                raise MarkdownFormatError(f"line {lineno}: metadata after the table: {ln!r}")
            m = re.fullmatch(r"- ([a-z_]+): (.*)", ln)
            if not m:
                raise MarkdownFormatError(f"line {lineno}: malformed metadata {ln!r}")
            cur.meta.setdefault(m.group(1), []).append(m.group(2))
            continue
        if ln.startswith("|"):
            cells = _split_row(ln, lineno)
            if cur.header is None:
                cur.header = cells
                continue
            if not cur.rows and _SEP_RE.fullmatch(ln.replace(" ", "")):
                if len(cells) != len(cur.header):
                    raise MarkdownFormatError(f"line {lineno}: separator has {len(cells)} cells, "
                                              f"header {len(cur.header)}")
                cur.rows.append((lineno, []))  # marker: separator seen
                continue
            if not cur.rows:
                raise MarkdownFormatError(f"line {lineno}: table without separator row")
            if len(cells) != len(cur.header):
                raise MarkdownFormatError(
                    f"line {lineno}: {len(cells)} cells but the header has {len(cur.header)}")
            cur.rows.append((lineno, cells))
            continue
        if cur.kind == "ro-intro":
            continue  # explanatory prose under "## Ramberg-Osgood parameters"
        raise MarkdownFormatError(f"line {lineno}: unexpected text {ln!r}")

    tables: list[SourceTable] = []
    ro: list[RambergOsgoodEntry] = []
    figs: list[FigureRef] = []
    for s in sections:
        if s.kind == "table":
            tables.append(_build_table(s))
        elif s.kind == "ro":
            ro.extend(_build_ro(s))
        elif s.kind == "figures":
            figs.extend(_build_figs(s))
    if not tables:
        raise MarkdownFormatError("no '## Table' section found")
    return MaterialSheet(fm["material"], dict(fm), tuple(tables), tuple(ro), tuple(figs))


def _one(meta: Mapping[str, list[str]], key: str, name: str) -> str:
    vals = meta.get(key, [])
    if len(vals) != 1:
        raise MarkdownFormatError(f"section {name}: expected exactly one '- {key}:' line, got {len(vals)}")
    return vals[0]


def _body(s: _Section) -> tuple[list[str], list[tuple[int, list[str]]]]:
    if s.header is None or not s.rows:
        raise MarkdownFormatError(f"section {s.name or s.kind}: missing table")
    return s.header, [r for r in s.rows[1:]]


def _build_table(s: _Section) -> SourceTable:
    header, rows = _body(s)
    if header[0] != "col" or "basis" not in header:
        raise MarkdownFormatError(f"table {s.name}: header must start with 'col' and contain 'basis'")
    keys: list[tuple[str, str]] = []  # (kind, key)
    for h in header[1:]:
        if h == "basis":
            keys.append(("basis", "basis"))
        elif h in _ATTRIBUTE_COLUMNS:
            keys.append(("attr", _ATTRIBUTE_COLUMNS[h]))
        else:
            keys.append(("value", _column_key(h, rows[0][0] - 2 if rows else 0)))
    seen = [k for _, k in keys]
    if len(set(seen)) != len(seen):
        raise MarkdownFormatError(f"table {s.name}: duplicate columns")
    out: list[TableRow] = []
    last = 0
    for lineno, cells in rows:
        if not re.fullmatch(r"\d+", cells[0]) or int(cells[0]) <= last:
            raise MarkdownFormatError(f"line {lineno}: 'col' must be a strictly increasing integer")
        last = int(cells[0])
        attrs: dict[str, Cell] = {}
        vals: dict[str, Cell] = {}
        basis: Basis | None = None
        for (kind, key), text in zip(keys, cells[1:], strict=True):
            if kind == "basis":
                try:
                    basis = Basis(text)
                except ValueError:
                    raise MarkdownFormatError(f"line {lineno}: unknown basis {text!r}") from None
            elif kind == "attr":
                attrs[key] = _parse_attr(text, lineno)
            else:
                vals[key] = _parse_value(text, lineno)
        if basis is None:
            raise MarkdownFormatError(f"table {s.name}: row without a basis column")
        out.append(TableRow(last, basis, attrs, vals))
    pdf_page = _one(s.meta, "pdf_page", s.name)
    if not pdf_page.isdigit():
        raise MarkdownFormatError(f"table {s.name}: pdf_page must be an integer")
    return SourceTable(
        table_id=s.name,
        title=_one(s.meta, "title", s.name),
        pdf_page=int(pdf_page),
        printed_page=_one(s.meta, "printed_page", s.name),
        elongation_label=(s.meta.get("elongation_label") or [""])[0],
        columns=tuple(k for kind, k in keys if kind == "value"),
        rows=tuple(out),
        notes=tuple(s.meta.get("note", [])),
        footnotes=dict(s.footnotes),
    )


def _build_ro(s: _Section) -> list[RambergOsgoodEntry]:
    header, rows = _body(s)
    if header != ["curve", "n", "0.2% yield (ksi)"]:
        raise MarkdownFormatError(f"figure {s.name}: unexpected Ramberg-Osgood header {header}")
    page = _one(s.meta, "pdf_page", s.name)
    if not page.isdigit():
        raise MarkdownFormatError(f"figure {s.name}: pdf_page must be an integer")
    out = []
    for lineno, (curve, n, y) in ((ln, c) for ln, c in rows):
        if not re.fullmatch(r"\d+(?:\.\d+)?", n):
            raise MarkdownFormatError(f"line {lineno}: malformed n {n!r}")
        if not re.fullmatch(r"\d+(?:\.\d+)?|—", y):
            raise MarkdownFormatError(f"line {lineno}: malformed yield {y!r}")
        out.append(RambergOsgoodEntry(s.name, int(page), _one(s.meta, "caption", s.name),
                                      _one(s.meta, "thickness", s.name), curve, float(n), n, "" if y == "—" else y))
    return out


def _build_figs(s: _Section) -> list[FigureRef]:
    header, rows = _body(s)
    if header != ["figure", "pdf page", "file", "caption"]:
        raise MarkdownFormatError(f"figures: unexpected header {header}")
    out = []
    for lineno, (fig, page, file, cap) in ((ln, c) for ln, c in rows):
        if not page.isdigit():
            raise MarkdownFormatError(f"line {lineno}: malformed page {page!r}")
        out.append(FigureRef(fig, int(page), file, cap))
    return out


def _cell_text(cell: Cell) -> str:
    base = cell.raw or "—"
    return f"{base} [{','.join(cell.footnotes)}]" if cell.footnotes else base


def _header_name(key: str) -> str:
    prop, _, qual = key.partition(" ")
    unit = _PROPERTIES[prop][0]
    shown = {"nu": "μ", "rho": "ω"}.get(prop, prop) + (" " + qual if qual else "")
    return f"{shown} ({unit})" if unit else shown


def format_material_markdown(sheet: MaterialSheet) -> str:
    """Serialise a :class:`MaterialSheet` in the strict layout read by :func:`parse_material_markdown`.

    ``parse_material_markdown(format_material_markdown(s)) == s`` holds for every
    sheet produced by the parser (round trip). Explanatory prose and metadata
    lines that the parser ignores are not reproduced.
    """
    attr_names = {v: k for k, v in _ATTRIBUTE_COLUMNS.items()}
    out = ["---"] + [f"{k}: {v}" for k, v in sheet.front_matter.items()] + ["---", ""]
    for tab in sheet.tables:
        out += [f"## Table {tab.table_id}", "", f"- title: {tab.title}", f"- pdf_page: {tab.pdf_page}",
                f"- printed_page: {tab.printed_page}"]
        if tab.elongation_label:
            out.append(f"- elongation_label: {tab.elongation_label}")
        out += [f"- note: {n}" for n in tab.notes] + [""]
        attrs = list(tab.rows[0].attributes) if tab.rows else []
        header = ["col"] + [attr_names[a] for a in attrs] + ["basis"] + [_header_name(k) for k in tab.columns]
        out.append("| " + " | ".join(header) + " |")
        out.append("|" + "|".join(["---:"] + [":---"] * (len(attrs) + 1) + ["---:"] * len(tab.columns)) + "|")
        for row in tab.rows:
            cells = [str(row.column)] + [_cell_text(row.attributes[a]) for a in attrs] + [row.basis.value]
            cells += [_cell_text(row.values[k]) for k in tab.columns]
            out.append("| " + " | ".join(cells) + " |")
        out += ["", f"### Footnotes to Table {tab.table_id} (as printed)", ""]
        out += [f"- {k}: {v}" if k else f"- {v}" for k, v in tab.footnotes.items()] + [""]
    if sheet.ramberg_osgood:
        out += ["## Ramberg-Osgood parameters", ""]
        for fig in dict.fromkeys(e.figure for e in sheet.ramberg_osgood):
            es = [e for e in sheet.ramberg_osgood if e.figure == fig]
            out += [f"### Figure {fig}", "", f"- pdf_page: {es[0].pdf_page}", f"- caption: {es[0].caption}",
                    f"- thickness: {es[0].thickness}", "", "| curve | n | 0.2% yield (ksi) |", "|:---|---:|---:|"]
            out += [f"| {e.curve} | {e.n_raw} | {e.yield_raw or '—'} |" for e in es] + [""]
    if sheet.figures:
        out += ["## Figures", "", "| figure | pdf page | file | caption |", "|:---|---:|:---|:---|"]
        out += [f"| {f.figure} | {f.pdf_page} | {f.file} | {f.caption} |" for f in sheet.figures] + [""]
    return "\n".join(out)


# --------------------------------------------------------------------------- loading


@functools.lru_cache(maxsize=1)
def list_materials() -> tuple[str, ...]:
    """Material identifiers available in :data:`DATA_DIR` (file stems, sorted).

    Returns
    -------
    tuple of str
        E.g. ``("al-2024-t3", "al-2024-t351", ...)``.
    """
    return tuple(sorted(p.stem for p in DATA_DIR.glob("*.md") if p.stem != "index"))


@functools.lru_cache(maxsize=256)
def load_material(material: str) -> MaterialSheet:
    """Load and parse one material sheet (cached).

    Parameters
    ----------
    material:
        Identifier such as ``"al-7075-t651"`` (case-insensitive).

    Raises
    ------
    KeyError
        Unknown material; the message lists close matches.
    MarkdownFormatError
        The file is malformed.
    """
    slug = material.strip().lower()
    if slug not in list_materials():
        close = [m for m in list_materials() if slug.split("-")[0] in m and any(
            part in m for part in slug.split("-")[1:])] or list(list_materials())
        raise KeyError(f"unknown material {material!r}; available: {', '.join(close)}")
    text = (DATA_DIR / f"{slug}.md").read_text(encoding="utf-8")
    return parse_material_markdown(text, slug)


# --------------------------------------------------------------------------- lookup


def ksi_to_pa(value_ksi: float) -> float:
    """Convert ksi to Pa (1 ksi = 6.894757293168361 MPa)."""
    return value_ksi * KSI_TO_PA


def _to_si(value: float, unit: str) -> tuple[float, str]:
    if unit == "ksi":
        return value * KSI_TO_PA, "Pa"
    if unit == "10³ ksi":
        return value * 1e3 * KSI_TO_PA, "Pa"
    if unit == "percent":
        return value / 100.0, "1"
    if unit == "lb/in.³":
        return value * LB_PER_IN3_TO_KG_PER_M3, "kg/m^3"
    return value, "1"


def _thickness_in(thickness: float | None, units: LengthUnit) -> float | None:
    if thickness is None:
        return None
    if not math.isfinite(thickness) or thickness <= 0:
        raise ValueError(f"thickness must be a positive finite number, got {thickness!r}")
    factor = {"in": 1.0, "m": 1.0 / INCH_TO_M, "mm": 1.0 / (1000.0 * INCH_TO_M)}
    if units not in factor:
        raise ValueError(f"thickness_units must be 'm', 'mm' or 'in', got {units!r}")
    return thickness * factor[units]


def _as_basis(basis: Basis | str) -> Basis:
    if isinstance(basis, Basis):
        return basis
    try:
        return Basis(str(basis).upper())
    except ValueError:
        raise ValueError(f"basis must be 'A', 'B' or 'S', got {basis!r}") from None


def _as_direction(direction: Direction | str | None) -> str | None:
    if direction is None:
        return None
    if isinstance(direction, Direction):
        return direction.value
    d = str(direction).upper()
    if d not in Direction.__members__:
        raise ValueError(f"direction must be one of L, LT, ST, T or None, got {direction!r}")
    return d


def _matches(row: TableRow, key: str, text: str | None) -> bool:
    return text is None or text.lower() in row.attribute(key).lower()


@cite("mil_hdbk_5j_2003", note="design-allowable tables, Ch. 2-6; basis definitions Sec. 1.4.1.1")
def lookup_allowable(
    material: str,
    property: str,
    basis: Basis | str = "A",
    direction: Direction | str | None = "L",
    thickness: float | None = None,
    units: UnitSystem = "SI",
    *,
    thickness_units: LengthUnit = "m",
    e_over_d: float | None = None,
    form: str | None = None,
    specification: str | None = None,
    temper: str | None = None,
) -> Allowable:
    """Look up one MIL-HDBK-5J value with full provenance.

    Parameters
    ----------
    material:
        Material identifier, see :func:`list_materials`.
    property:
        ``Ftu``, ``Fty``, ``Fcy``, ``Fsu``, ``Fbru``, ``Fbry``, ``e`` (elongation),
        ``E``, ``Ec``, ``G``, ``nu`` (Poisson's ratio μ) or ``rho`` (density ω).
    basis:
        ``"A"``, ``"B"`` or ``"S"``. Ignored for ``E``, ``Ec``, ``G``, ``nu``
        and ``rho`` (typical values). Elongation printed as "(S-basis)"
        requires ``basis="S"``.
    direction:
        ``"L"``, ``"LT"``, ``"ST"`` or ``"T"`` for ``Ftu``, ``Fty``, ``Fcy``
        and ``e``. If the source table gives the property without a direction
        (e.g. steel tables), that value is returned and ``Allowable.direction``
        is ``None``. Ignored for the other properties.
    thickness:
        Product thickness. ``None`` is allowed only if the value does not
        depend on thickness for the selected rows.
    units:
        ``"SI"`` (Pa, kg/m³, strain fraction for elongation) or ``"source"``
        (ksi, 10³ ksi, percent, lb/in.³ exactly as printed).
    thickness_units:
        Unit of ``thickness``: ``"m"`` (default), ``"mm"`` or ``"in"``.
    e_over_d:
        Edge-distance ratio, 1.5 or 2.0, required for ``Fbru``/``Fbry``.
    form, specification, temper:
        Optional case-insensitive substring filters on the printed column
        headers (e.g. ``form="plate"``).

    Returns
    -------
    Allowable

    Raises
    ------
    KeyError
        Unknown material or property, or property not tabulated for it.
    ValueError
        Invalid argument, thickness outside every tabulated range, value not
        printed ("..."), or several different values match (the message lists
        them and the filters that separate them).

    Notes
    -----
    Source: MIL-HDBK-5J design tables cited per row (``table_id``, ``pdf_page``).
    Thickness ranges are matched with a tolerance of half the last printed
    digit (see :class:`ThicknessRange`).
    """
    sheet = load_material(material)
    prop = _canonical_property(property)
    b = _as_basis(basis)
    d = _as_direction(direction)
    t_in = _thickness_in(thickness, thickness_units)
    unit, directional = _PROPERTIES[prop]
    if units not in ("SI", "source"):
        raise ValueError(f"units must be 'SI' or 'source', got {units!r}")
    if prop in ("Fbru", "Fbry"):
        if e_over_d is None or not any(math.isclose(e_over_d, x) for x in (1.5, 2.0)):
            raise ValueError(f"{prop} needs e_over_d=1.5 or e_over_d=2.0, got {e_over_d!r}")
        keys = [f"{prop} e/D={'1.5' if math.isclose(e_over_d, 1.5) else '2.0'}"]
    elif directional:
        if d is None:
            raise ValueError(f"{prop} is directional; pass direction='L', 'LT', 'ST' or 'T'")
        keys = [f"{prop} {d}", prop]
    else:
        keys = [prop]

    candidates: list[tuple[SourceTable, TableRow, str]] = []
    for tab in sheet.tables:
        key = next((k for k in keys if k in tab.columns), None)
        if key is None:
            continue
        ignore_basis = prop in _PHYSICAL or (prop == "e" and tab.elongation_is_s_basis)
        if prop == "e" and tab.elongation_is_s_basis and b is not Basis.S:
            raise ValueError(f"elongation in Table {tab.table_id} is printed as S-basis; pass basis='S'")
        for row in tab.rows:
            if not ignore_basis and row.basis is not b:
                continue
            if not (_matches(row, "form", form) and _matches(row, "specification", specification)
                    and (_matches(row, "temper", temper) or _matches(row, "condition", temper))):
                continue
            candidates.append((tab, row, key))
    if not candidates:
        available = sorted({k for tab in sheet.tables for k in tab.columns})
        bases = sorted({r.basis.value for tab in sheet.tables for r in tab.rows})
        raise KeyError(f"{prop} (keys tried: {keys}) with basis {b.value} and the given filters is not "
                       f"tabulated for {sheet.slug}; columns: {', '.join(available)}; bases: {', '.join(bases)}")

    if t_in is not None:
        in_range: list[tuple[SourceTable, TableRow, str]] = []
        for c in candidates:
            rng = c[1].thickness
            if rng is not None and rng.contains(t_in):
                in_range.append(c)
        if not in_range:
            ranges = sorted({c[1].attribute("thickness") or "(not printed)" for c in candidates})
            raise ValueError(f"thickness {t_in:.4f} in. is outside the tabulated ranges for {sheet.slug} "
                             f"{prop} basis {b.value}: {', '.join(ranges)}")
        candidates = in_range

    with_value = [c for c in candidates if c[1].values[c[2]].value is not None]
    if not with_value:
        fns = sorted({f for c in candidates for f in c[1].values[c[2]].footnotes})
        notes = [n for c in candidates for n in c[0].notes if n.startswith(c[2].split()[0] + ":")]
        extra = (f"; footnotes {fns}: " + "; ".join(candidates[0][0].footnotes.get(f, "") for f in fns)) if fns else ""
        extra += ("; notes: " + " / ".join(dict.fromkeys(notes))) if notes else ""
        raise ValueError(f"{prop} is not printed (\"...\") for {sheet.slug} with these arguments{extra}")
    distinct = {c[1].values[c[2]].raw for c in with_value}
    if len(distinct) > 1:
        desc = "; ".join(
            f"{c[1].values[c[2]].raw} (Table {c[0].table_id} col {c[1].column}: form={c[1].attribute('form')!r}, "
            f"spec={c[1].attribute('specification')!r}, thickness={c[1].attribute('thickness')!r})"
            for c in with_value)
        raise ValueError(f"{prop} is ambiguous for {sheet.slug}: {desc}. "
                         "Pass thickness=, form=, specification= or temper= to select one.")
    tab, row, key = with_value[0]
    cell = row.values[key]
    if cell.value is None:                       # filtered above; kept explicit for python -O
        raise ValueError(f"{prop} has no printed value for {sheet.slug}")
    value, out_unit = (cell.value, unit) if units == "source" else _to_si(cell.value, unit)
    q = key.split(" ", 1)[1] if " " in key else None
    return Allowable(
        material=sheet.slug, property=prop, value=value, unit=out_unit, raw=cell.raw, source_unit=unit,
        basis=None if prop in _PHYSICAL else (Basis.S if prop == "e" and tab.elongation_is_s_basis else row.basis),
        direction=q if q in Direction.__members__ else None,
        table_id=tab.table_id, pdf_page=tab.pdf_page, printed_page=tab.printed_page, column=row.column,
        form=row.attribute("form"), specification=row.attribute("specification"),
        thickness=row.attribute("thickness"), footnotes=cell.footnotes,
    )


@cite("mil_hdbk_5j_2003")
def get_allowable(
    material: str,
    property: str,
    basis: Basis | str = "A",
    direction: Direction | str | None = "L",
    thickness: float | None = None,
    units: UnitSystem = "SI",
    *,
    thickness_units: LengthUnit = "m",
    e_over_d: float | None = None,
    form: str | None = None,
    specification: str | None = None,
    temper: str | None = None,
) -> float:
    """Return one MIL-HDBK-5J value as ``float``.

    Same parameters and errors as :func:`lookup_allowable`, which also returns
    the provenance (table, PDF page, footnotes). Strengths and moduli are in Pa
    with ``units="SI"`` (density kg/m³, elongation as a strain fraction), or in
    the printed source units with ``units="source"``.

    Examples
    --------
    >>> get_allowable("al-7075-t651", "Fty", "B", "LT", thickness=25.4, thickness_units="mm",
    ...               units="source")  # doctest: +SKIP
    """
    return lookup_allowable(material, property, basis, direction, thickness, units,
                            thickness_units=thickness_units, e_over_d=e_over_d, form=form,
                            specification=specification, temper=temper).value


# --------------------------------------------------------------------------- Ramberg-Osgood

FloatArray = npt.NDArray[np.float64]


def _check_ro(E: float, f02: float, n: float) -> None:
    if not (E > 0 and f02 > 0 and n > 0) or not all(map(math.isfinite, (E, f02, n))):
        raise ValueError(f"need E > 0, f0.2 > 0 and n > 0 (finite); got E={E}, f02={f02}, n={n}")


@overload
def ramberg_osgood_strain(stress: float, E: float, f02: float, n: float) -> float: ...
@overload
def ramberg_osgood_strain(stress: FloatArray, E: float, f02: float, n: float) -> FloatArray: ...
@cite("ramberg_osgood_1943", "mil_hdbk_5j_2003", note="Eq. 9.8.4.1.2(b), PDF p. 1594")
def ramberg_osgood_strain(stress: float | FloatArray, E: float, f02: float, n: float) -> float | FloatArray:
    """Total strain from the Ramberg-Osgood relation.

    ``e = f/E + 0.002 (f/f0.2)^n`` — MIL-HDBK-5J Eq. 9.8.4.1.2(b), PDF page
    1594 (printed 9-188), after Ramberg & Osgood, NACA TN-902 (1943). Applied
    odd-symmetrically for negative stress (compression magnitudes).

    Parameters
    ----------
    stress:
        Stress, same unit as ``E`` and ``f02``.
    E:
        Modulus of elasticity (typical value from the property table).
    f02:
        0.2 % offset yield stress (TYS or CYS).
    n:
        Ramberg-Osgood exponent.

    Returns
    -------
    float or numpy.ndarray
        Total strain; at ``stress == f02`` the plastic part is exactly 0.002.
    """
    _check_ro(E, f02, n)
    s = np.asarray(stress, dtype=np.float64)
    eps = s / E + 0.002 * np.sign(s) * np.abs(s / f02) ** n
    if isinstance(stress, np.ndarray):
        return eps
    return float(eps)


@overload
def ramberg_osgood_tangent_modulus(stress: float, E: float, f02: float, n: float) -> float: ...
@overload
def ramberg_osgood_tangent_modulus(stress: FloatArray, E: float, f02: float, n: float) -> FloatArray: ...
@cite("ramberg_osgood_1943", "mil_hdbk_5j_2003", note="Eq. 9.8.4.2(b), PDF p. 1597")
def ramberg_osgood_tangent_modulus(stress: float | FloatArray, E: float, f02: float,
                                   n: float) -> float | FloatArray:
    """Tangent modulus ``Et = 1 / (1/E + 0.002 n/f0.2 (f/f0.2)^(n-1))``.

    MIL-HDBK-5J Eq. 9.8.4.2(b), PDF page 1597 (printed 9-191). Uses ``|f|``.
    """
    _check_ro(E, f02, n)
    s = np.abs(np.asarray(stress, dtype=np.float64))
    et = 1.0 / (1.0 / E + 0.002 * n / f02 * (s / f02) ** (n - 1.0))
    if isinstance(stress, np.ndarray):
        return et
    return float(et)


@overload
def ramberg_osgood_stress(strain: float, E: float, f02: float, n: float) -> float: ...
@overload
def ramberg_osgood_stress(strain: FloatArray, E: float, f02: float, n: float) -> FloatArray: ...
@cite("ramberg_osgood_1943")
def ramberg_osgood_stress(strain: float | FloatArray, E: float, f02: float, n: float) -> float | FloatArray:
    """Invert Eq. 9.8.4.1.2(b): stress for a given total strain (bisection, ~1e-15 rel.)."""
    _check_ro(E, f02, n)
    e = np.asarray(strain, dtype=np.float64)
    target = np.abs(e)
    lo = np.zeros_like(target)
    # each term is non-negative, so stress <= E*strain and stress <= f02*(strain/0.002)^(1/n)
    hi: FloatArray = np.minimum(target * E, f02 * np.power(target / 0.002, 1.0 / n))
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f = mid / E + 0.002 * (mid / f02) ** n - target
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f < 0, hi, mid)
    s = np.sign(e) * 0.5 * (lo + hi)
    if isinstance(strain, np.ndarray):
        return s
    return float(s)


@cite("ramberg_osgood_1943", "mil_hdbk_5j_2003")
def ramberg_osgood_curve(E: float, f02: float, n: float, stress_max: float | None = None,
                         num: int = 201) -> tuple[FloatArray, FloatArray]:
    """Sample a Ramberg-Osgood stress-strain curve from zero to ``stress_max``.

    Parameters
    ----------
    E, f02, n:
        See :func:`ramberg_osgood_strain`.
    stress_max:
        Upper stress (default ``1.2 * f02``). MIL-HDBK-5J notes the relation is
        "sufficiently accurate for use up to the yield strength" and cannot give
        full-range curves (Section 9.8.4.1.2).
    num:
        Number of points (>= 2). The point ``f02`` is always included.

    Returns
    -------
    (strain, stress):
        Two arrays of equal length, increasing.
    """
    _check_ro(E, f02, n)
    if num < 2:
        raise ValueError("num must be >= 2")
    top = 1.2 * f02 if stress_max is None else stress_max
    if not top > 0:
        raise ValueError("stress_max must be > 0")
    stress = np.union1d(np.linspace(0.0, top, num), np.array([f02]) if f02 <= top else np.array([]))
    return ramberg_osgood_strain(stress, E, f02, n), stress


def get_ramberg_osgood_n(material: str, direction: Direction | str | None = "L",
                         loading: Literal["tension", "compression"] = "tension") -> RambergOsgoodEntry:
    """Room-temperature Ramberg-Osgood exponent read from a typical-curve figure.

    Parameters
    ----------
    material:
        Material identifier.
    direction:
        Grain direction that must appear in the curve label (e.g. "L-tension");
        ``None`` accepts labels without a direction (e.g. "H1025", "RT").
    loading:
        ``"tension"`` or ``"compression"``.

    Raises
    ------
    KeyError
        No matching room-temperature entry; the message lists what exists.
    ValueError
        Several entries with different n match.
    """
    sheet = load_material(material)
    d = _as_direction(direction)
    if loading not in ("tension", "compression"):
        raise ValueError(f"loading must be 'tension' or 'compression', got {loading!r}")
    hits = [e for e in sheet.ramberg_osgood
            if e.room_temperature and e.loading == loading
            and ((d is None and not e.directions) or (d is not None and d in e.directions))]
    if not hits:
        have = "; ".join(f"{e.figure}: n ({e.curve}) = {e.n_raw}" for e in sheet.ramberg_osgood) or "none"
        raise KeyError(f"no room-temperature {loading} n for direction {d} in {sheet.slug}; entries: {have}")
    if len({e.n_raw for e in hits}) > 1:
        raise ValueError(f"several n values match for {sheet.slug}: "
                         + "; ".join(f"{e.figure} ({e.curve}, thickness {e.thickness}) = {e.n_raw}" for e in hits))
    return hits[0]


def stress_strain_curve(
    material: str,
    basis: Basis | str = "A",
    direction: Direction | str = "L",
    thickness: float | None = None,
    loading: Literal["tension", "compression"] = "tension",
    *,
    thickness_units: LengthUnit = "m",
    form: str | None = None,
    num: int = 201,
    stress_max_factor: float = 1.0,
) -> tuple[FloatArray, FloatArray]:
    """Stress-strain curve (SI) from tabulated E/Ec, Fty/Fcy and the figure's n.

    Uses ``E`` (tension) or ``Ec`` (compression) and ``Fty``/``Fcy`` of the
    selected basis as ``f0.2`` in Eq. 9.8.4.1.2(b). Note: MIL-HDBK-5J derives n
    from *typical* curves (where f0.2 is the typical TYS/CYS); combining it
    with a design-basis yield is a common engineering approximation, not a
    handbook-defined design curve.

    Returns
    -------
    (strain, stress_Pa)
    """
    e_key, f_key = ("E", "Fty") if loading == "tension" else ("Ec", "Fcy")
    E = get_allowable(material, e_key, thickness=thickness, thickness_units=thickness_units, form=form)
    f02 = get_allowable(material, f_key, basis, direction, thickness, thickness_units=thickness_units, form=form)
    n = get_ramberg_osgood_n(material, direction, loading).n
    return ramberg_osgood_curve(E, f02, n, stress_max=stress_max_factor * f02 * 1.0, num=num)


def _iter_numeric_cells(sheet: MaterialSheet) -> Iterable[tuple[SourceTable, TableRow, str, Cell]]:
    """Yield every printed numeric cell (helper for verification and tests)."""
    for tab in sheet.tables:
        for row in tab.rows:
            for key, cell in row.values.items():
                if cell.raw:
                    yield tab, row, key, cell


def numeric_cells(material: str) -> Sequence[tuple[str, int, int, str, str]]:
    """``(table_id, pdf_page, column, key, raw)`` for every printed number of a material."""
    return [(t.table_id, t.pdf_page, r.column, k, c.raw) for t, r, k, c in _iter_numeric_cells(load_material(material))]
