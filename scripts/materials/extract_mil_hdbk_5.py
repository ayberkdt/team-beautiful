"""Extract MIL-HDBK-5J design-allowable tables and figure pages into Markdown.

The PDF is treated as untrusted *data*: it is only opened and read with PyMuPDF.
Run with the isolated interpreter flag from the project root::

    python -I scripts/materials/extract_mil_hdbk_5.py \
        references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf \
        --out src/aerokit/materials/data

How the table parser works (no manual transcription)
----------------------------------------------------
MIL-HDBK-5J "Design Mechanical and Physical Properties" tables are vector text
with ruled cells. Many are printed rotated by 90 degrees. For each page:

1. Characters are read from ``page.get_text("rawdict")`` and mapped into
   *table coordinates* (``c`` = across the table, ``r`` = down the table), which
   undoes the page rotation. Glyphs from the ``WP-MathA`` font are mapped
   (0x06 -> "≤", 0x07 -> "≥", 0x28 -> "°"); "Ȧ" -> "ω", "Į" -> "α", "µ" -> "μ"
   (font re-encodings verified against the rendered page images).
2. Characters become tokens; tokens smaller than 0.8 x the body font size are
   sub/superscripts: small italic = subscript (``F_tu``), small digit =
   exponent (``10³``), small letter = footnote marker.
3. The ruling lines (thin filled rectangles) give the cell grid. The vertical
   rule that separates the row-label column from the data defines the header
   rows (one rule segment per header row).
4. The ``Basis`` row defines one data column per A/B/S letter. Every header
   cell and every data phrase is bounded by the nearest vertical rules; a
   phrase whose cell spans several columns is assigned to all of them
   (e.g. ``E`` printed once for a whole product group); otherwise phrases are
   matched to columns one-to-one or by nearest column centre. Any collision
   raises an error instead of guessing.
5. Row labels are parsed with a small state machine (``F_tu, ksi:`` then
   ``L``/``LT``/``ST``; ``F_bru`` then ``(e/D = 1.5)``/``(e/D = 2.0)``; ...).

Values are written exactly as printed (strings), never rounded or converted.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import statistics
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

SOURCE_URL = "https://everyspec.com/MIL-HDBK/MIL-HDBK-0001-0099/download.php?spec=MIL_HDBK_5J.139.pdf"
SOURCE_DOC = (
    "MIL-HDBK-5J, Department of Defense Handbook: Metallic Materials and Elements for "
    "Aerospace Vehicle Structures, 31 January 2003 (Distribution Statement A: approved for "
    "public release; distribution is unlimited)"
)
SOURCE_REL = "references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf"

WP_MATH = {0x06: "≤", 0x07: "≥", 0x28: "°"}
GLYPH_FIX = {"Ȧ": "ω", "Į": "α", "µ": "μ"}

# --------------------------------------------------------------------------- config


@dataclass(frozen=True)
class TablePage:
    """A table page to extract and how its columns map to material files."""

    page: int  # 1-based PDF page index
    prefix: str | None  # material slug prefix; None -> taken from ``alloys``
    alloy: str  # alloy designation written to the md (if no "Alloy" header row)
    temper_key: str  # header row giving the temper/condition ("temper" or "condition")
    alloys: tuple[tuple[str, str], ...] = ()  # (Alloy header text, slug prefix) to keep


TABLE_PAGES: tuple[TablePage, ...] = (
    # 2024 bare sheet and plate, Table 3.2.3.0(b1)-(b3)
    TablePage(373, "al-2024", "2024", "temper"),
    TablePage(374, "al-2024", "2024", "temper"),
    TablePage(375, "al-2024", "2024", "temper"),
    # 2219 sheet and plate, Table 3.2.8.0(b1)-(b3)
    TablePage(470, "al-2219", "2219", "temper"),
    TablePage(471, "al-2219", "2219", "temper"),
    TablePage(472, "al-2219", "2219", "temper"),
    # 6061 sheet, plate, Table 3.6.2.0(b1)-(b2)
    TablePage(566, "al-6061", "6061", "temper"),
    TablePage(567, "al-6061", "6061", "temper"),
    # 7050 plate, Table 3.7.4.0(b1)-(b2)
    TablePage(626, "al-7050", "7050", "temper"),
    TablePage(627, "al-7050", "7050", "temper"),
    # 7075 sheet and plate, Table 3.7.6.0(b1)-(b4)
    TablePage(673, "al-7075", "7075", "temper"),
    TablePage(674, "al-7075", "7075", "temper"),
    TablePage(675, "al-7075", "7075", "temper"),
    TablePage(676, "al-7075", "7075", "temper"),
    # Low-alloy steels, Table 2.3.1.0(c1), (c2), (f1)
    TablePage(71, None, "", "condition", (("AISI 4130", "steel-4130"),)),
    TablePage(72, None, "", "condition", (("AISI 4130", "steel-4130"),)),
    TablePage(76, None, "", "condition", (("0.40C 300M", "steel-300m"), ("0.42C 300M", "steel-300m"))),
    # 15-5PH bar/forging and plate, Table 2.6.7.0(b), (c)
    TablePage(223, "ss-15-5ph", "15-5PH", "condition"),
    TablePage(224, "ss-15-5ph", "15-5PH", "condition"),
    # 17-4PH sheet/strip/plate and bar, Table 2.6.9.0(b), (e)
    TablePage(251, "ss-17-4ph", "17-4PH", "condition"),
    TablePage(253, "ss-17-4ph", "17-4PH", "condition"),
    # Ti-6Al-4V sheet, strip and plate, Table 5.4.1.0(b)
    TablePage(945, "ti-6al-4v", "Ti-6Al-4V", "condition"),
    # Inconel 718 sheet/plate/tubing and bar/forging, Table 6.3.5.0(b), (c)
    TablePage(1092, "inconel-718", "Inconel 718", "condition"),
    TablePage(1093, "inconel-718", "Inconel 718", "condition"),
)

CONDITION_SLUGS = {
    "normalized and tempered, stress relieved": "nt",
    "quenched and tempered": "qt",
    "annealed": "annealed",
    "solution treated and aged": "sta",
    "solution treated and aged per indicated specification": "sta",
}


@dataclass(frozen=True)
class FigureSpec:
    """A figure to export (page PNG) and optionally parse Ramberg-Osgood n from."""

    fig_id: str
    page: int
    materials: tuple[tuple[str, str], ...] = ()  # (material slug, regex on curve label)
    parse_ro: bool = False


FIGURES: tuple[FigureSpec, ...] = (
    # 2024
    FigureSpec("3.2.3.1.1(a)", 389, (("al-2024-t3", ""), ("al-2024-t351", ""))),
    FigureSpec("3.2.3.1.1(b)", 390, (("al-2024-t3", ""), ("al-2024-t351", ""))),
    FigureSpec("3.2.3.1.4", 395, (("al-2024-t3", ""), ("al-2024-t351", ""))),
    FigureSpec("3.2.3.1.6(a)", 397, (("al-2024-t3", ""),), True),
    FigureSpec("3.2.3.1.6(i)", 401, (("al-2024-t351", ""),), True),
    # 2219-T87
    FigureSpec("3.2.8.4.1(a)", 491, (("al-2219-t87", ""),)),
    FigureSpec("3.2.8.4.1(b)", 492, (("al-2219-t87", ""),)),
    FigureSpec("3.2.8.4.6(a)", 493, (("al-2219-t87", ""),), True),
    # 6061-T6
    FigureSpec("3.6.2.2.1(a)", 576, (("al-6061-t6", ""), ("al-6061-t651", ""))),
    FigureSpec("3.6.2.2.1(b)", 577, (("al-6061-t6", ""), ("al-6061-t651", ""))),
    FigureSpec("3.6.2.2.4", 579, (("al-6061-t6", ""), ("al-6061-t651", ""))),
    FigureSpec("3.6.2.2.6(f)", 583, (("al-6061-t6", ""),), True),
    FigureSpec("3.6.2.2.6(g)", 584, (("al-6061-t6", ""),), True),
    # 7050-T7451
    FigureSpec("3.7.4.2.1", 638, (("al-7050-t7451", ""),)),
    FigureSpec("3.7.4.2.6(a)", 639, (("al-7050-t7451", ""),), True),
    FigureSpec("3.7.4.2.6(b)", 639, (("al-7050-t7451", ""),), True),
    # 7075-T6 / T651
    FigureSpec("3.7.6.1.1(a)", 691, (("al-7075-t6", ""), ("al-7075-t651", ""))),
    FigureSpec("3.7.6.1.1(b)", 691, (("al-7075-t6", ""), ("al-7075-t651", ""))),
    FigureSpec("3.7.6.1.4", 696, (("al-7075-t6", ""), ("al-7075-t651", ""), ("al-7075-t7351", ""))),
    FigureSpec("3.7.6.1.6(a)", 697, (("al-7075-t6", ""),), True),
    FigureSpec("3.7.6.1.6(g)", 700, (("al-7075-t651", ""),), True),
    FigureSpec("3.7.6.1.6(h)", 701, (("al-7075-t651", ""),), True),
    # Low-alloy steels (4130, 300M): only temperature-effect curves exist
    FigureSpec("2.3.1.0", 80, (("steel-4130-nt", ""), ("steel-4130-qt", ""))),
    FigureSpec("2.3.1.1.1", 81, (("steel-4130-nt", ""), ("steel-4130-qt", ""), ("steel-300m-qt", ""))),
    FigureSpec("2.3.1.1.4", 83, (("steel-4130-nt", ""), ("steel-4130-qt", ""), ("steel-300m-qt", ""))),
    # 15-5PH
    FigureSpec("2.6.7.1.1", 227, (("ss-15-5ph-h1025", ""),)),
    FigureSpec("2.6.7.1.4", 228, (("ss-15-5ph-h1025", ""),)),
    FigureSpec("2.6.7.1.6(a)", 229, (("ss-15-5ph-h1025", r"\bH1025\b"),), True),
    FigureSpec("2.6.7.1.6(b)", 229, (("ss-15-5ph-h1025", ""),)),
    FigureSpec("2.6.7.2.6(b)", 232, (("ss-15-5ph-h1025", ""),), True),
    # 17-4PH
    FigureSpec("2.6.9.1.4", 257, (("ss-17-4ph-h900", ""),)),
    FigureSpec("2.6.9.2.1", 261, (("ss-17-4ph-h1025", ""),)),
    FigureSpec(
        "2.6.9.2.6(a)",
        262,
        (("ss-17-4ph-h900", r"\bH900\b"), ("ss-17-4ph-h1025", r"\bH1025\b"), ("ss-17-4ph-h1150", r"\bH1150\b")),
        True,
    ),
    FigureSpec(
        "2.6.9.2.6(b)",
        262,
        (("ss-17-4ph-h1025", r"\bH1025\b"), ("ss-17-4ph-h1150", r"\bH1150\b")),
        True,
    ),
    # Ti-6Al-4V annealed
    FigureSpec("5.4.1.1.1", 953, (("ti-6al-4v-annealed", ""),)),
    FigureSpec("5.4.1.1.4", 955, (("ti-6al-4v-annealed", ""),)),
    FigureSpec("5.4.1.1.6(a)", 956, (("ti-6al-4v-annealed", ""),), True),
    FigureSpec("5.4.1.1.6(b)", 957, (("ti-6al-4v-annealed", ""),), True),
    FigureSpec("5.4.1.1.6(c)", 957, (("ti-6al-4v-annealed", ""),)),
    # Inconel 718
    FigureSpec("6.3.5.1.1", 1095, (("inconel-718-sta", ""),)),
    FigureSpec("6.3.5.1.4(a)", 1096, (("inconel-718-sta", ""),)),
    FigureSpec("6.3.5.1.6(a)", 1098, (("inconel-718-sta", ""),), True),
    FigureSpec("6.3.5.1.6(c)", 1099, (("inconel-718-sta", ""),), True),
)

# --------------------------------------------------------------------------- geometry


@dataclass
class Tok:
    """A token in table coordinates (c across, r down)."""

    text: str
    c0: float
    c1: float
    r0: float
    r1: float
    small: bool
    italic: bool

    @property
    def rc(self) -> float:
        return (self.r0 + self.r1) / 2

    @property
    def cc(self) -> float:
        return (self.c0 + self.c1) / 2


@dataclass(frozen=True)
class Rule:
    pos: float
    lo: float
    hi: float


def _map_char(ch: str, font: str) -> str:
    if font.startswith("WP-MathA"):
        return WP_MATH.get(ord(ch), "�")
    return GLYPH_FIX.get(ch, ch)


class PageGeom:
    """Tokens and ruling lines of one page in table coordinates."""

    def __init__(self, page: fitz.Page) -> None:
        self.page = page
        self.W = page.rect.width
        self.H = page.rect.height
        raw = page.get_text("rawdict")
        votes: Counter[str] = Counter()
        for b in raw["blocks"]:
            for ln in b.get("lines", []):
                votes[self._dir_key(ln["dir"])] += sum(len(s["chars"]) for s in ln["spans"])
        self.orient = votes.most_common(1)[0][0]
        sizes: list[float] = []
        for b in raw["blocks"]:
            for ln in b.get("lines", []):
                if self._dir_key(ln["dir"]) != self.orient:
                    continue
                for s in ln["spans"]:
                    sizes.extend([s["size"]] * len(s["chars"]))
        self.body = statistics.median(sizes)
        self.tokens: list[Tok] = []
        self.lines_raw: list[tuple[str, float, float, float, float]] = []  # text, c0, c1, r0, r1
        for b in raw["blocks"]:
            for ln in b.get("lines", []):
                if self._dir_key(ln["dir"]) != self.orient:
                    continue
                self._tokenize_line(ln)
        self.vrules: list[Rule] = []
        self.hrules: list[Rule] = []
        for g in page.get_drawings():
            fill = g.get("fill")
            if fill is not None and all(v > 0.9 for v in fill):
                continue  # white
            for it in g["items"]:
                if it[0] == "re":
                    x0, y0, x1, y1 = it[1].x0, it[1].y0, it[1].x1, it[1].y1
                elif it[0] == "l":
                    p1, p2 = it[1], it[2]
                    x0, y0, x1, y1 = min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)
                else:
                    continue
                c0, c1, r0, r1 = self.tf(x0, y0, x1, y1)
                if c1 - c0 <= 2.0 < r1 - r0:
                    self.vrules.append(Rule((c0 + c1) / 2, r0, r1))
                elif r1 - r0 <= 2.0 < c1 - c0:
                    self.hrules.append(Rule((r0 + r1) / 2, c0, c1))

    @staticmethod
    def _dir_key(d: tuple[float, float]) -> str:
        dx, dy = d
        if abs(dx - 1) < 0.1:
            return "up"
        if abs(dy + 1) < 0.1:
            return "ccw"
        if abs(dy - 1) < 0.1:
            return "cw"
        return "other"

    def tf(self, x0: float, y0: float, x1: float, y1: float) -> tuple[float, float, float, float]:
        """Page bbox -> (c0, c1, r0, r1) in table coordinates."""
        if self.orient == "ccw":
            return self.H - y1, self.H - y0, x0, x1
        if self.orient == "cw":
            return y0, y1, self.W - x1, self.W - x0
        return x0, x1, y0, y1

    def _tokenize_line(self, ln: dict) -> None:  # type: ignore[type-arg]
        cur: Tok | None = None
        line_text = []
        lc0 = lr0 = 1e9
        lc1 = lr1 = -1e9
        for s in ln["spans"]:
            small = s["size"] < 0.8 * self.body
            italic = "Italic" in s["font"] or bool(s["flags"] & 2)
            for ch in s["chars"]:
                t = _map_char(ch["c"], s["font"])
                c0, c1, r0, r1 = self.tf(*ch["bbox"])
                line_text.append(t)
                if t.isspace():
                    if cur is not None:
                        self.tokens.append(cur)
                    cur = None
                    continue
                lc0, lc1, lr0, lr1 = min(lc0, c0), max(lc1, c1), min(lr0, r0), max(lr1, r1)
                if cur is not None and (cur.small != small or c0 - cur.c1 > 1.2):
                    self.tokens.append(cur)
                    cur = None
                if cur is None:
                    cur = Tok(t, c0, c1, r0, r1, small, italic)
                else:
                    cur.text += t
                    cur.c1 = max(cur.c1, c1)
                    cur.r0 = min(cur.r0, r0)
                    cur.r1 = max(cur.r1, r1)
        if cur is not None:
            self.tokens.append(cur)
        self.lines_raw.append(("".join(line_text), lc0, lc1, lr0, lr1))

    def vrules_crossing(self, r: float) -> list[float]:
        return sorted({round(v.pos, 1) for v in self.vrules if v.lo - 0.6 <= r <= v.hi + 0.6})

    def lines(self, toks: list[Tok]) -> list[list[Tok]]:
        """Cluster normal tokens into text lines; attach small tokens to the nearest line."""
        normal = sorted((t for t in toks if not t.small), key=lambda t: t.rc)
        out: list[list[Tok]] = []
        for t in normal:
            if out and abs(t.rc - statistics.fmean(x.rc for x in out[-1])) < 2.2:
                out[-1].append(t)
            else:
                out.append([t])
        for t in (t for t in toks if t.small):
            best = None
            for ln in out:
                lo, hi = min(x.r0 for x in ln) - 2.5, max(x.r1 for x in ln) + 2.5
                if lo <= t.rc <= hi:
                    d = abs(t.rc - statistics.fmean(x.rc for x in ln))
                    if best is None or d < best[0]:
                        best = (d, ln)
            if best is None:
                out.append([t])
            else:
                best[1].append(t)
        out.sort(key=lambda ln: statistics.fmean(x.rc for x in ln))
        for ln in out:
            ln.sort(key=lambda t: t.c0)
        return out


def printed_page_number(page: fitz.Page) -> str:
    for w in page.get_text("words"):
        if w[1] > 0.9 * page.rect.height and re.fullmatch(r"\d+-\d+(?:/\d+-\d+)?", w[4]):
            return str(w[4])
    return ""


# --------------------------------------------------------------------------- phrases


@dataclass
class Phrase:
    text: str
    c0: float
    c1: float
    rc: float
    footnotes: list[str] = field(default_factory=list)

    @property
    def cc(self) -> float:
        return (self.c0 + self.c1) / 2


def build_phrases(g: PageGeom, line: list[Tok], cmin: float) -> list[Phrase]:
    """Merge tokens of one line (right of ``cmin``) into phrases, footnotes attached."""
    toks = [t for t in line if t.cc > cmin]
    if not toks:
        return []
    rc = statistics.fmean(t.rc for t in toks if not t.small) if any(not t.small for t in toks) else toks[0].rc
    rules = g.vrules_crossing(rc)
    out: list[Phrase] = []
    for t in toks:
        prev = out[-1] if out else None
        blocked = prev is not None and any(prev.c1 - 0.3 < p < t.c0 + 0.3 for p in rules)
        if t.small:
            if prev is not None and not blocked and t.c0 - prev.c1 < 2.5 and re.fullmatch(r"[a-z]+", t.text):
                prev.footnotes.extend(t.text)
                prev.c1 = max(prev.c1, t.c1)
            elif re.fullmatch(r"[a-z]+", t.text):
                out.append(Phrase("", t.c0, t.c1, rc, list(t.text)))
            elif prev is not None and not blocked:
                prev.text += "^" + t.text
                prev.c1 = max(prev.c1, t.c1)
            else:
                out.append(Phrase("^" + t.text, t.c0, t.c1, rc))
            continue
        if prev is not None and not blocked and t.c0 - prev.c1 < 3.6:
            prev.text = (prev.text + " " + t.text) if prev.text else t.text
            prev.c1 = max(prev.c1, t.c1)
        else:
            out.append(Phrase(t.text, t.c0, t.c1, rc))
    return out


def cell_bounds(g: PageGeom, ph: Phrase, left_edge: float, right_edge: float) -> tuple[float, float]:
    rules = g.vrules_crossing(ph.rc)
    left = max([p for p in rules if p <= ph.c0 + 0.5] or [left_edge])
    right = min([p for p in rules if p >= ph.c1 - 0.5] or [right_edge])
    return left, right


def norm_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(?<=[A-Za-z0-9])- (?=[A-Za-z0-9])", "-", s)  # line-broken "0.250- 1.000", "A- 250/11"
    s = re.sub(r"([≤≥<>]) (\d)", r"\1\2", s)
    s = s.replace("^3", "³").replace("^2", "²")
    s = s.replace(" ,", ",")
    return s


def is_missing(s: str) -> bool:
    return bool(re.fullmatch(r"(?:\.\s*){3,}", s.strip()))


NUM_RE = re.compile(r"\d+(?:\.\d+)?|\.\d+")

# --------------------------------------------------------------------------- table parsing


@dataclass
class Column:
    index: int
    cc: float
    basis: str
    header: dict[str, tuple[str, list[str]]] = field(default_factory=dict)
    values: dict[str, tuple[str, list[str], bool]] = field(default_factory=dict)  # key -> (raw, fn, spanned)
    notes: list[str] = field(default_factory=list)


@dataclass
class ParsedTable:
    page: int
    printed_page: str
    table_id: str
    title: str
    columns: list[Column]
    prop_order: list[str]
    prop_footnotes: dict[str, list[str]]
    elongation_label: str
    footnotes: list[tuple[str, str]]
    skipped_rows: list[str]
    notes: list[str]


def label_string(toks: list[Tok]) -> tuple[str, list[str]]:
    s = ""
    fns: list[str] = []
    for t in toks:
        if re.fullmatch(r"(?:\.)+", t.text):
            continue
        if t.small:
            if t.italic and not t.text.isdigit():
                s += "_" + t.text
            elif re.fullmatch(r"-?\d+", t.text):
                s += "^" + t.text
            else:
                fns.extend(t.text)
            continue
        s = (s + " " + t.text) if s else t.text
    s = re.sub(r"\s+([,:])", r"\1", s).strip()
    m = re.match(r"^(F_(?:tu|ty|cy|su|bru|bry))_([a-z])\b", s)
    if m:  # italic footnote marker printed right after the subscript
        fns.append(m.group(2))
        s = m.group(1) + s[m.end():]
    s = re.sub(r"(?:\s*\.)+$", "", s).strip() if not s.endswith("in.") else s
    return s, fns


PROP_RE = re.compile(r"^F_(tu|ty|cy|su|bru|bry)\b")
DIR_RE = re.compile(r"^(L|LT|ST|T)$")
ED_RE = re.compile(r"^\(e/D\s*=\s*(1\.5|2\.0)\)$")


def classify_label(label: str) -> tuple[str, str] | None:
    """Return (kind, value): kind in prop/dir/ed/e/phys/skip/section."""
    lab = label.strip()
    m = PROP_RE.match(lab)
    if m:
        return "prop", "F" + m.group(1)
    if DIR_RE.match(lab):
        return "dir", lab
    m = ED_RE.match(lab)
    if m:
        return "ed", m.group(1)
    if re.match(r"^e, percent", lab):
        return "e", lab
    if re.match(r"^E_c, 10\^3 ksi$", lab):
        return "phys", "Ec"
    if re.match(r"^E, 10\^3 ksi$", lab):
        return "phys", "E"
    if re.match(r"^G, 10\^3 ksi$", lab):
        return "phys", "G"
    if lab == "μ":
        return "phys", "nu"
    if re.match(r"^ω, lb/in\.(?:\^3)?$", lab):
        return "phys", "rho"
    if re.match(r"^RA, percent", lab):
        return "skipsection", lab
    if re.match(r"^(Mechanical Properties|Physical Properties)", lab):
        return "section", lab
    if re.match(r"^(C, K, and α|C, K|C,|K,|K and α|α,)", lab):
        return "skip", lab
    return None


UNITS = {
    "Ftu": "ksi", "Fty": "ksi", "Fcy": "ksi", "Fsu": "ksi", "Fbru": "ksi", "Fbry": "ksi",
    "e": "percent", "E": "10³ ksi", "Ec": "10³ ksi", "G": "10³ ksi", "nu": "", "rho": "lb/in.³",
}
PROP_DISPLAY = {"nu": "μ", "rho": "ω"}


def column_name(key: str) -> str:
    prop, _, qual = key.partition(" ")
    unit = UNITS[prop]
    name = PROP_DISPLAY.get(prop, prop) + (" " + qual if qual else "")
    return f"{name} ({unit})" if unit else name


def parse_table_page(doc: fitz.Document, pno: int) -> ParsedTable:
    page = doc[pno - 1]
    g = PageGeom(page)
    lines = g.lines(g.tokens)
    texts = [(ln, " ".join(t.text if not t.small else t.text for t in ln)) for ln in lines]

    # title
    title_idx = next(i for i, (_, s) in enumerate(texts) if re.match(r"^Table\s+\d", s))
    tl = lines[title_idx]
    title_raw = "".join((t.text if t.small else (" " + t.text)) for t in tl).strip()
    long_h = [h for h in g.hrules if h.hi - h.lo > 100]
    r_top = min(h.pos for h in long_h if h.pos > max(t.r1 for t in tl) - 1)
    for ln in lines[title_idx + 1:]:
        if statistics.fmean(t.rc for t in ln) < r_top:
            title_raw += " " + "".join((t.text if t.small else (" " + t.text)) for t in ln).strip()
    title_raw = re.sub(r"\s+", " ", title_raw)
    m = re.match(r"^Table\s+(\d+\.\d+\.\d+\.\d+)\s*\(\s*([a-z]\d?)\s*\)\.?\s*(.*)$", title_raw)
    if not m:
        raise ValueError(f"page {pno}: cannot parse title {title_raw!r}")
    table_id = f"{m.group(1)}({m.group(2)})"
    title = m.group(3).strip()
    title = re.sub(r"(\w)- (\w)", r"\1\2", title)  # "Alumi- num" -> "Aluminum"

    maxlen = max(h.hi - h.lo for h in g.hrules)
    c_right = max(h.hi for h in g.hrules if h.hi - h.lo > 0.6 * maxlen)

    # basis row
    b_idx = next(i for i, ln in enumerate(lines) if ln and ln[0].text.rstrip(".") == "Basis")
    bline = lines[b_idx]
    letters = [t for t in bline if not t.small and t.text in ("A", "B", "S")]
    if not letters and b_idx + 1 < len(lines):
        # some tables print the A/B/S letters one text line below the "Basis" label
        nxt = [t for t in lines[b_idx + 1] if not t.small]
        if nxt and all(t.text in ("A", "B", "S") for t in nxt):
            letters = nxt
            bline = bline + nxt
    if not letters:
        raise ValueError(f"page {pno}: no A/B/S letters in the Basis row")
    b_rc = statistics.fmean(t.rc for t in letters)
    rules_b = g.vrules_crossing(b_rc)
    first = min(t.c0 for t in letters)
    cands = [p for p in rules_b if p < first - 0.5]
    lb = max(cands) if cands else (max(t.c1 for t in bline if t.c1 < first) + first) / 2
    columns = [Column(i, t.cc, t.text) for i, t in enumerate(sorted(letters, key=lambda t: t.cc))]

    # bottom of the table: first long rule after the Basis row not followed by a data-row label
    r_bottom = 1e9
    for h in sorted((h for h in g.hrules if h.hi - h.lo > 0.6 * maxlen and h.pos > b_rc), key=lambda h: h.pos):
        nxt = [ln for ln in lines if statistics.fmean(t.rc for t in ln) > h.pos]
        if not nxt:
            r_bottom = h.pos
            break
        lab, _ = label_string([t for t in nxt[0] if t.cc < lb])
        if not lab or classify_label(lab) is None:
            r_bottom = h.pos
            break

    # header rows from label-boundary rule segments
    segs = sorted((v for v in g.vrules if abs(v.pos - lb) < 1.2), key=lambda v: v.lo)
    bseg = next((s for s in segs if s.lo - 0.6 <= b_rc <= s.hi + 0.6), None)
    if bseg is None:
        raise ValueError(f"page {pno}: no label-boundary rule at the Basis row")
    hsegs = [s for s in segs if s.hi <= bseg.lo + 0.7 and s.lo >= r_top - 1.5]
    header_lines = [ln for ln in lines if r_top < statistics.fmean(t.rc for t in ln) < bseg.lo]
    for s in hsegs:
        seg_lines = [ln for ln in header_lines if s.lo <= statistics.fmean(t.rc for t in ln) <= s.hi]
        label_toks = [t for ln in seg_lines for t in ln if t.cc < lb]
        if not label_toks:
            if any(t.cc > lb for ln in seg_lines for t in ln):
                raise ValueError(f"page {pno}: header segment {s} has values but no label")
            continue
        label, _ = label_string(label_toks)
        key = header_key(label)
        cells: dict[tuple[float, float], list[Phrase]] = {}
        for ln in seg_lines:
            for ph in build_phrases(g, ln, lb + 0.5):
                cells.setdefault(cell_bounds(g, ph, lb, c_right), []).append(ph)
        for (left, right), phs in cells.items():
            phs.sort(key=lambda p: (round(p.rc), p.c0))
            text = norm_text(" ".join(p.text for p in phs if p.text))
            fns = [f for p in phs for f in p.footnotes]
            hit = [c for c in columns if left - 0.5 <= c.cc <= right + 0.5]
            if not hit:
                raise ValueError(f"page {pno}: header cell {text!r} covers no column")
            for c in hit:
                if key in c.header:
                    raise ValueError(f"page {pno}: two {key} cells for column {c.index}")
                if key == "thickness":
                    text = re.sub(r"(\d)\s*-\s*(\d)", r"\1-\2", text)  # "7.001 - 8.000"
                if key == "thickness" and len(text) == 1 and text.islower():
                    c.header[key] = ("", fns + [text])  # footnote marker printed full size
                else:
                    c.header[key] = (text, fns)
    if not all("thickness" in c.header or True for c in columns):
        pass

    # data rows
    prop: str | None = None
    prop_order: list[str] = []
    prop_fn: dict[str, list[str]] = {}
    elong_label = ""
    skipped: list[str] = []
    notes: list[str] = []
    pending: list[Phrase] = []
    for ln in lines:
        rc = statistics.fmean(t.rc for t in ln if not t.small) if any(not t.small for t in ln) else ln[0].rc
        if not (bseg.hi < rc < r_bottom):
            continue
        label, lfn = label_string([t for t in ln if t.cc < lb])
        phrases = build_phrases(g, ln, lb + 0.5)
        cls = classify_label(label) if label else None
        if cls is None:
            if label or phrases:
                raise ValueError(f"page {pno}: unrecognised row label {label!r} with {[p.text for p in phrases]}")
            continue
        kind, val = cls
        key: str | None = None
        if kind in ("prop", "e") and phrases and all(not p.text for p in phrases):
            # footnote-only markers printed on the section line (e.g. "e, percent:" with "b"
            # above an empty "LT" row): they belong to the following direction row
            pending = phrases
            phrases = []
        elif kind == "dir" and pending:
            # merge; assign_row raises if a marker and a printed value fall in the same column
            phrases, pending = phrases + pending, []
        else:
            pending = []
        if kind == "prop":
            prop = val
            if lfn:
                prop_fn[val] = lfn
            if phrases:
                key = val
        elif kind == "e":
            prop = "e"
            elong_label = label
            if lfn:
                prop_fn["e"] = lfn
            if phrases:
                key = "e"
        elif kind == "skipsection":
            prop = "_skip"
            skipped.append(label)
            continue
        elif kind in ("dir", "ed") and prop == "_skip":
            skipped.append("  " + label + ": " + " | ".join(norm_text(p.text) for p in phrases))
            continue
        elif kind == "dir":
            if prop is None:
                raise ValueError(f"page {pno}: direction row {val} before any property")
            key = f"{prop} {val}"
        elif kind == "ed":
            if prop not in ("Fbru", "Fbry"):
                raise ValueError(f"page {pno}: e/D row under {prop}")
            key = f"{prop} e/D={val}"
        elif kind == "phys":
            prop = None
            key = val
            if lfn:
                prop_fn[val] = lfn
        elif kind == "skip":
            skipped.append(label + ": " + " | ".join(norm_text(p.text) for p in phrases))
            continue
        else:
            continue
        if key is None:
            continue
        if key in prop_order:
            raise ValueError(f"page {pno}: duplicate row {key}")
        prop_order.append(key)
        assign_row(g, pno, key, phrases, columns, lb, c_right, notes)

    footnotes = parse_footnotes(g, lines, r_bottom)
    return ParsedTable(pno, printed_page_number(page), table_id, title, columns, prop_order, prop_fn,
                       elong_label, footnotes, skipped, notes)


def header_key(label: str) -> str:
    low = label.lower()
    for k in ("specification", "form", "temper", "condition", "thickness", "alloy", "basis"):
        if low.startswith(k):
            return k
    raise ValueError(f"unknown header row label {label!r}")


def assign_row(g: PageGeom, pno: int, key: str, phrases: list[Phrase], columns: list[Column],
               lb: float, c_right: float, notes: list[str]) -> None:
    cells: dict[tuple[float, float], list[Phrase]] = {}
    for ph in phrases:
        cells.setdefault(cell_bounds(g, ph, lb, c_right), []).append(ph)
    for (left, right), phs in sorted(cells.items()):
        cols = [c for c in columns if left - 0.5 <= c.cc <= right + 0.5]
        phs.sort(key=lambda p: p.c0)
        if not cols:
            raise ValueError(f"page {pno}: row {key}: phrase {[p.text for p in phs]} outside every column")
        if len(phs) == len(cols):
            pairs = [(p, [c]) for p, c in zip(phs, cols, strict=True)]
        elif len(phs) == 1:
            pairs = [(phs[0], cols)]
        else:
            used: dict[int, Phrase] = {}
            pairs = []
            for p in phs:
                c = min(cols, key=lambda c: abs(c.cc - p.cc))
                if c.index in used:
                    raise ValueError(f"page {pno}: row {key}: two phrases map to column {c.index}")
                used[c.index] = p
                pairs.append((p, [c]))
        for p, cs in pairs:
            raw = norm_text(p.text)
            if is_missing(raw):
                raw = ""
            elif raw and not NUM_RE.fullmatch(raw):
                notes.append(f"{key}: {raw!r} printed for columns {', '.join(str(c.index + 1) for c in cs)}")
                raw = ""
            for c in cs:
                if key in c.values:
                    raise ValueError(f"page {pno}: row {key}: column {c.index} assigned twice")
                c.values[key] = (raw, list(p.footnotes), len(cs) > 1)


def parse_footnotes(g: PageGeom, lines: list[list[Tok]], r_bottom: float) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for ln in lines:
        rc = statistics.fmean(t.rc for t in ln)
        if rc <= r_bottom:
            continue
        text = ""
        prev_c1 = -1e9
        for t in ln:
            text += t.text if (text and t.c0 - prev_c1 < 0.8) else (" " + t.text)
            prev_c1 = t.c1
        text = text.strip()
        if re.fullmatch(r"\d+-\d+", text.strip()):
            continue
        if text.startswith("Table "):
            break  # a second table starts on the same page
        m = re.match(r"^([a-z])\s+(.*)$", text)
        if m:
            out.append((m.group(1), m.group(2).strip()))
        elif out:
            out[-1] = (out[-1][0], out[-1][1] + " " + text.strip())
        else:
            out.append(("", text.strip()))
    return [(k, re.sub(r"\s+", " ", v)) for k, v in out]


# --------------------------------------------------------------------------- materials


def temper_slugs(text: str) -> list[str]:
    """Slug(s) for a temper/condition; "T6 and T62" belongs to both T6 and T62."""
    t = text.strip()
    parts = [x.strip() for x in t.split(" and ")]
    if all(re.fullmatch(r"[TH]\d+[A-Z]?", x) for x in parts):
        return [x.lower() for x in parts]
    key = t.lower()
    if key in CONDITION_SLUGS:
        return [CONDITION_SLUGS[key]]
    raise ValueError(f"no slug rule for temper/condition {text!r}")


def temper_of(c: Column, cfg: TablePage) -> str:
    """Temper/condition of a column; some pages label the temper row "Condition"."""
    for key in (cfg.temper_key, "temper", "condition"):
        if c.header.get(key, ("", []))[0]:
            return c.header[key][0]
    return ""


@dataclass
class MaterialRow:
    table: ParsedTable
    column: Column


def collect_materials(tables: list[ParsedTable]) -> dict[str, list[MaterialRow]]:
    by_page = {tp.page: tp for tp in TABLE_PAGES}
    mats: dict[str, list[MaterialRow]] = {}
    for t in tables:
        cfg = by_page[t.page]
        for c in t.columns:
            if cfg.prefix is None:
                alloy = c.header.get("alloy", ("", []))[0]
                prefix = dict(cfg.alloys).get(alloy)
                if prefix is None:
                    continue
            else:
                prefix = cfg.prefix
            temper = temper_of(c, cfg)
            for ts in temper_slugs(temper):
                mats.setdefault(f"{prefix}-{ts}", []).append(MaterialRow(t, c))
    return mats


# --------------------------------------------------------------------------- figures


@dataclass
class ROEntry:
    fig_id: str
    page: int
    curve: str
    n: str
    yield_ksi: str
    thickness: str
    caption: str


def page_text_lines(doc: fitz.Document, pno: int) -> list[tuple[str, float, float, float]]:
    """(text, r0, r1, c0) for every line on the page in its own reading frame."""
    g = PageGeom(doc[pno - 1])
    out = []
    for text, c0, _c1, r0, r1 in g.lines_raw:
        if text.strip():
            out.append((re.sub(r"\s+", " ", text).strip(), r0, r1, c0))
    return sorted(out, key=lambda x: (round(x[1]), x[3]))


def figure_caption(doc: fitz.Document, spec: FigureSpec) -> tuple[str, float, float]:
    lines = page_text_lines(doc, spec.page)
    pat = re.compile(r"^Figure\s+" + re.escape(spec.fig_id) + r"\.?\s")
    for i, (text, r0, r1, _c0) in enumerate(lines):
        if pat.match(text + " "):
            cap = text
            for nxt in lines[i + 1:i + 3]:
                if (nxt[1] - r1 < 14 and not nxt[0].startswith("Figure")
                        and not re.fullmatch(r"\d+-\d+", nxt[0])):  # not the printed page number
                    cap += " " + nxt[0]
                    r1 = nxt[2]
                else:
                    break
            return re.sub(r"\s+", " ", cap), r0, r1
    raise ValueError(f"Figure {spec.fig_id} caption not found on PDF page {spec.page}")


RO_RE = re.compile(r"n\s*\(\s*([^)]*?)\s*\)\s*=\s*(\d+(?:\.\d+)?)(?:\s+(\d+(?:\.\d+)?))?\s*$")


def parse_ro(doc: fitz.Document, spec: FigureSpec) -> list[ROEntry]:
    lines = page_text_lines(doc, spec.page)
    caption, cap_r0, _ = figure_caption(doc, spec)
    caps = [r0 for (t, r0, _r1, _c) in lines if t.startswith("Figure ") and r0 < cap_r0 - 1]
    top = max(caps) if caps else -1e9
    region = [ln for ln in lines if top < ln[1] < cap_r0]
    thick = ""
    for t, *_ in region:
        m = re.match(r"^Thickness\s*[:=]?\s*(.+)$", t)
        if m:
            thick = m.group(1).strip()
    out = []
    has_ro = any("Ramberg" in t for t, *_ in region)
    for t, *_ in region:
        m = RO_RE.search(t)
        if m and has_ro:
            out.append(ROEntry(spec.fig_id, spec.page, re.sub(r"\s+", " ", m.group(1)), m.group(2),
                               m.group(3) or "", thick, caption))
    if spec.parse_ro and not out:
        raise ValueError(f"no Ramberg-Osgood n found for Figure {spec.fig_id}")
    return out


# --------------------------------------------------------------------------- writing


def cell_md(raw: str, fns: list[str]) -> str:
    base = raw if raw else "—"
    return f"{base} [{','.join(fns)}]" if fns else base


def esc(s: str) -> str:
    if "|" in s:
        raise ValueError(f"pipe in cell text {s!r}")
    return s


HEADER_KEYS = ("alloy", "specification", "form", "temper", "condition", "thickness", "basis")
HEADER_NAMES = {"thickness": "thickness (in.)"}


def write_material(slug: str, rows: list[MaterialRow], ro: list[ROEntry], figs: list[tuple[FigureSpec, str]],
                   sha: str, out: Path) -> dict[str, str]:
    first = rows[0]
    cfg = {tp.page: tp for tp in TABLE_PAGES}[first.table.page]
    alloy = first.column.header.get("alloy", (cfg.alloy, []))[0] or cfg.alloy
    temper = temper_of(first.column, cfg)
    suffix = slug.rsplit("-", 1)[1]
    temper = next((x.strip() for x in temper.split(" and ") if x.strip().lower() == suffix), temper)
    tables: list[ParsedTable] = []
    for r in rows:
        if r.table not in tables:
            tables.append(r.table)
    forms = sorted({r.column.header.get("form", ("", []))[0] for r in rows})
    bases = sorted({r.column.basis for r in rows})
    tlist = "; ".join(f"{t.table_id} (PDF page {t.page}, printed page {t.printed_page})" for t in tables)
    fm = [
        "---",
        f"material: {slug}",
        f"alloy: {alloy}",
        f"temper_or_condition: {temper}",
        f"product_forms: {'; '.join(forms)}",
        f"bases: {', '.join(bases)}",
        f"source_document: {SOURCE_DOC}",
        f"source_url: {SOURCE_URL}",
        f"source_file: {SOURCE_REL}",
        f"source_sha256: {sha}",
        f"source_tables: {tlist}",
        "extraction: automatic (scripts/materials/extract_mil_hdbk_5.py); no manual transcription",
        "units: as printed in the source (ksi; 10³ ksi; percent; lb/in.³); "
        "values copied digit for digit, never rounded or converted",
        "---",
        "",
        f"# {alloy} {temper} — MIL-HDBK-5J design allowables",
        "",
        "Each table row is one column of the source table (one thickness range and basis).",
        "Cell syntax: `64` = value as printed; `51 [a]` = value with footnote marker a;",
        "`—` = nothing printed (\"...\" or blank in the source); `— [c]` = no value, footnote c only.",
        "Values that the source prints once across several columns (E, Ec, G, μ, ω and some others)",
        "are repeated in every column they span. S-basis values are specification minima; A and B",
        "are statistically based (MIL-HDBK-5J Section 1.4.1.1).",
        "",
    ]
    lines = fm
    for t in tables:
        cols = [r.column for r in rows if r.table is t]
        lines += [f"## Table {t.table_id}", "",
                  f"- title: {t.title}",
                  f"- pdf_page: {t.page}",
                  f"- printed_page: {t.printed_page}",
                  "- extraction: automatic"]
        if t.elongation_label:
            lines.append(f"- elongation_label: {t.elongation_label.replace('_', '')}")
        for k, v in t.prop_footnotes.items():
            lines.append(f"- row_footnote: {PROP_DISPLAY.get(k, k)} [{','.join(v)}]")
        for n in t.notes:
            lines.append(f"- note: {n.replace('|', '/')}")
        for s in t.skipped_rows:
            lines.append(f"- not_extracted: {s.replace('|', '/')}")
        lines.append("")
        present_h = [k for k in HEADER_KEYS if any(k in c.header for c in cols) or k == "basis"]
        keys = [k for k in t.prop_order]
        hdr = ["col"] + [HEADER_NAMES.get(k, k) for k in present_h] + [column_name(k) for k in keys]
        lines.append("| " + " | ".join(hdr) + " |")
        aligns = ["---:"] + [":---"] * len(present_h) + ["---:"] * len(keys)
        lines.append("|" + "|".join(aligns) + "|")
        for c in cols:
            cells = [str(c.index + 1)]
            for k in present_h:
                if k == "basis":
                    cells.append(c.basis)
                else:
                    txt, fn = c.header.get(k, ("", []))
                    cells.append(esc(cell_md(txt, fn)))
            for k in keys:
                raw, fn, _sp = c.values.get(k, ("", [], False))
                cells.append(cell_md(raw, fn))
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
        lines.append(f"### Footnotes to Table {t.table_id} (as printed)")
        lines.append("")
        for k, v in t.footnotes:
            lines.append(f"- {k}: {v}" if k else f"- {v}")
        lines.append("")
    if ro:
        lines += ["## Ramberg-Osgood parameters", "",
                  "Read from the typical stress-strain figures (text annotations on the figure). Typical curves:",
                  "not design allowables. Equation 9.8.4.1.2(b), PDF page 1594:",
                  "e_total = f/E + 0.002 (f/f0.2ys)^n.",
                  ""]
        for fid in dict.fromkeys(e.fig_id for e in ro):
            es = [e for e in ro if e.fig_id == fid]
            lines += [f"### Figure {fid}", "",
                      f"- pdf_page: {es[0].page}",
                      f"- caption: {es[0].caption}",
                      f"- thickness: {es[0].thickness or '—'}",
                      "",
                      "| curve | n | 0.2% yield (ksi) |",
                      "|:---|---:|---:|"]
            for e in es:
                lines.append(f"| {esc(e.curve)} | {e.n} | {e.yield_ksi or '—'} |")
            lines.append("")
    if figs:
        lines += ["## Figures", "", "| figure | pdf page | file | caption |", "|:---|---:|:---|:---|"]
        for spec, cap in figs:
            lines.append(f"| {spec.fig_id} | {spec.page} | figures/{fig_png_name(spec.page)} | {esc(cap)} |")
        lines.append("")
    (out / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return {"slug": slug, "alloy": alloy, "temper": temper, "forms": "; ".join(forms),
            "bases": ", ".join(bases), "tables": tlist}


def fig_png_name(page: int) -> str:
    return f"mil-hdbk-5j-p{page:04d}.png"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--only-page", type=int, default=None, help="debug: parse one table page and print it")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    doc = fitz.open(a.pdf)
    if doc.page_count != 1733:
        raise SystemExit(f"unexpected page count {doc.page_count}; is this MIL-HDBK-5J?")
    if a.only_page:
        t = parse_table_page(doc, a.only_page)
        print(t.table_id, t.title, t.printed_page)
        for c in t.columns:
            print(c.index + 1, c.basis, {k: v[0] for k, v in c.header.items()})
            print("    ", {k: cell_md(v[0], v[1]) + ("*" if v[2] else "") for k, v in c.values.items()})
        print("prop_fn", t.prop_footnotes, "elong", t.elongation_label)
        print("notes", t.notes)
        print("skipped", t.skipped_rows)
        for f in t.footnotes:
            print("fn", f)
        return 0
    sha = hashlib.sha256(a.pdf.read_bytes()).hexdigest()
    tables = [parse_table_page(doc, tp.page) for tp in TABLE_PAGES]
    mats = collect_materials(tables)
    ro_by_mat: dict[str, list[ROEntry]] = {}
    figs_by_mat: dict[str, list[tuple[FigureSpec, str]]] = {}
    fig_rows = []
    for spec in FIGURES:
        cap, _, _ = figure_caption(doc, spec)
        fig_rows.append((spec, cap))
        entries = parse_ro(doc, spec) if spec.parse_ro else []
        for slug, rx in spec.materials:
            if slug not in mats:
                raise ValueError(f"figure {spec.fig_id} maps to unknown material {slug}")
            figs_by_mat.setdefault(slug, []).append((spec, cap))
            sel = [e for e in entries if not rx or re.search(rx, e.curve)]
            if spec.parse_ro and not sel:
                raise ValueError(f"figure {spec.fig_id}: no RO entry matches {rx!r} for {slug}")
            ro_by_mat.setdefault(slug, []).extend(sel)
    a.out.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for slug in sorted(mats):
        index_rows.append(write_material(slug, mats[slug], ro_by_mat.get(slug, []), figs_by_mat.get(slug, []),
                                         sha, a.out))
    write_index(a.out, index_rows, sha)
    figdir = a.out / "figures"
    figdir.mkdir(exist_ok=True)
    pages = sorted({s.page for s in FIGURES})
    if not a.no_png:
        for p in pages:
            pix = doc[p - 1].get_pixmap(dpi=a.dpi, colorspace=fitz.csGRAY)
            pix.save(figdir / fig_png_name(p))
    write_fig_index(doc, figdir, fig_rows, mats)
    nvals = sum(1 for rows in mats.values() for r in rows for v in r.column.values.values() if v[0])
    print(f"tables parsed: {len(tables)}; materials: {len(mats)}; numeric cells written: {nvals}; "
          f"figures: {len(FIGURES)} on {len(pages)} pages")
    return 0


def write_index(out: Path, rows: list[dict[str, str]], sha: str) -> None:
    lines = [
        "---",
        f"source_document: {SOURCE_DOC}",
        f"source_url: {SOURCE_URL}",
        f"source_file: {SOURCE_REL}",
        f"source_sha256: {sha}",
        "generated_by: scripts/materials/extract_mil_hdbk_5.py",
        "---",
        "",
        "# Material allowables index (MIL-HDBK-5J)",
        "",
        "One file per alloy and temper/condition. Values are as printed in the source (ksi, 10³ ksi,",
        "percent, lb/in.³). Verification: references/materials/verification_report.md.",
        "",
        "| material | alloy | temper or condition | product forms | bases | source tables |",
        "|:---|:---|:---|:---|:---|:---|",
    ]
    for r in rows:
        lines.append(f"| [{r['slug']}]({r['slug']}.md) | {r['alloy']} | {r['temper']} | {r['forms']} | "
                     f"{r['bases']} | {r['tables']} |")
    lines += ["", "Figures: [figures/index.md](figures/index.md).", ""]
    (out / "index.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_fig_index(doc: fitz.Document, figdir: Path, fig_rows: list[tuple[FigureSpec, str]],
                    mats: dict[str, list[MaterialRow]]) -> None:
    lines = [
        "# Figure pages extracted from MIL-HDBK-5J",
        "",
        "Whole PDF pages rendered to grayscale PNG (150 dpi). A page can hold two figures.",
        "",
        "| figure | pdf page | printed page | file | materials | caption |",
        "|:---|---:|:---|:---|:---|:---|",
    ]
    for spec, cap in fig_rows:
        pp = printed_page_number(doc[spec.page - 1])
        ms = ", ".join(s for s, _ in spec.materials)
        lines.append(f"| {spec.fig_id} | {spec.page} | {pp} | [{fig_png_name(spec.page)}]({fig_png_name(spec.page)}) "
                     f"| {ms} | {esc(cap)} |")
    lines.append("")
    (figdir / "index.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
