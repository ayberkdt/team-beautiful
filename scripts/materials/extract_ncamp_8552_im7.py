"""Extract the property tables of NCAMP report NCP-RP-2013-015 Rev A into Markdown.

Source: E. Clarkson, *A Comparison of Equivalence Criteria and Basis Values for
HEXCEL 8552 IM7 Unidirectional Tape computed from the NCAMP shared database*,
NCAMP Report NCP-RP-2013-015 Rev A, Oct 31, 2013 (97 pages).

The PDF is treated as untrusted *data*: it is only opened and read with PyMuPDF.
Run with the isolated interpreter flag from the project root::

    python -I scripts/materials/extract_ncamp_8552_im7.py \
        references/materials/ncamp-ncp-rp-2013-015/cmh17-generic-basis-8552-im7-revA.pdf \
        --out src/aerokit/materials/data/composites/ncamp-8552-im7.md

What the report contains (read from the PDF, not assumed): strength data only.
Equivalence/basis tables 4-16 (unit means, qualification/pooled/generic B- and
A-basis values, acceptance limits) and the summary statistics tables 17-37
(average, standard deviation, coefficient of variation, max, min, specimen
count per unit and for the pooled dataset). It prints no moduli, no Poisson's
ratio, no transverse strengths, no bearing data, no cured ply thickness and no
fibre volume. Tables 1-3 (method comparison, critical values, failure counts)
are not material properties and are not extracted.

How the parser works (no manual transcription of numbers)
---------------------------------------------------------
Words come from ``page.get_text("words")`` and are grouped into text lines by
their vertical centre (tolerance 2.5 pt).

* Tables 4-16: the line starting with ``Environment`` defines one data column
  per environment token (CTD/RTD/ETD/ETW) at the token's horizontal centre.
  Words between the caption and that line, right of the row-label column, are
  the test (group) headers; they are merged into phrases by horizontal overlap
  (gap <= 6 pt, across lines) and every column takes the phrase with the
  nearest centre. The phrase list must equal the expected one in ``SPECS``
  (a check, the header text is still read from the page).
* Tables 17-37: the line containing ``Qual.`` gives the columns ``Qual.``,
  ``A01`` ... ``A12`` and ``Dataset`` (the pooled dataset, printed as
  "Pooled Dataset" on two lines). Rows must be Average, Std Dev., Coeff Var.,
  Max, Min, Count. A line holding only ``NA`` tokens is a merged cell spanning
  rows; its ``NA`` is written into every row of that column that has no value.
* Every value token (``12.34``, ``12.34*``, ``5.91%``, ``NA``) is assigned to
  the nearest column centre; a token farther than 45 % of the column pitch
  from every centre, or two tokens in one cell, raise an error instead of
  guessing. A line whose first word starts with ``*`` is a table footnote.

Values are written exactly as printed (strings), never rounded or converted.
The only hand-written content is the ``## Test descriptions`` section (layups
and conditions transcribed from the report's prose, marked ``manual``).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

SOURCE_REL = "references/materials/ncamp-ncp-rp-2013-015/cmh17-generic-basis-8552-im7-revA.pdf"
EXPECTED_PAGES = 97

ENV_TOKENS = ("CTD", "RTD", "ETD", "ETW")
STATS_COLUMNS = ("Qual.", "A01", "A02", "A03", "A2", "A4", "A5", "A6", "A8", "A9", "A10", "A11", "A12", "Dataset")
STATS_ROWS = ("Average", "Std Dev.", "Coeff Var.", "Max", "Min", "Count")
VALUE_RE = re.compile(r"^(?:\d+(?:\.\d+)?\*?|\d+(?:\.\d+)?%|NA)$")
RUNNING_HEADER_MAX_Y = 60.0
FOOTER_MIN_Y = 715.0


@dataclass(frozen=True)
class Spec:
    table: int
    page: int
    kind: str                      # "units" | "basis" | "limits" | "stats"
    groups: tuple[str, ...] = ()   # expected test headers (grouped tables)
    continues_on: int | None = None


GROUP_C = ("UNC0", "OHC1")
GROUP_T9 = ("Longitudinal Tension", "Unnotched Tension", "Open Hole Tension")
GROUP_T = ("LT", "UNT0", "OHT1")
GROUP_S13 = ("Short Beam Strength", "In-Plane Shear Strength @ 5% Strain", "In-Plane Shear 0.2% Offset Strength")
GROUP_S14 = ("Short Beam Strength", "In-Plane Shear Strength @ 5% Strain", "In-Plane Shear 0.2% Offset Strength")

SPECS: tuple[Spec, ...] = (
    Spec(4, 26, "units", GROUP_C),
    Spec(5, 27, "basis", GROUP_C),
    Spec(6, 28, "basis", ("0° Compression Strength from UNC0 Data",)),
    Spec(7, 28, "limits", GROUP_C),
    Spec(8, 28, "limits", GROUP_C),
    Spec(9, 32, "units", GROUP_T9),
    Spec(10, 33, "basis", GROUP_T),
    Spec(11, 33, "limits", GROUP_T),
    Spec(12, 33, "limits", GROUP_T),
    Spec(13, 39, "units", GROUP_S13, continues_on=40),
    Spec(14, 40, "basis", GROUP_S14),
    Spec(15, 41, "limits", GROUP_S14),
    Spec(16, 41, "limits", GROUP_S14),
) + tuple(Spec(t, p, "stats") for t, p in (
    (17, 45), (18, 48), (19, 50), (20, 53), (21, 55), (22, 58), (23, 61), (24, 63), (25, 66), (26, 68),
    (27, 70), (28, 73), (29, 75), (30, 77), (31, 80), (32, 83), (33, 85), (34, 87), (35, 90), (36, 92), (37, 96)))

# --------------------------------------------------------------------------- manual content
#: Transcribed by hand from the report prose (PDF pages given); flagged "manual" in the md.
TEST_DESCRIPTIONS: tuple[tuple[str, str, str, str, str, str], ...] = (
    # test, description as printed, layup as printed, data, environments, pdf page
    ("UNC0", "Unnotched Compression", "[90/0/90]5", "normalized", "RTD, ETD, ETW", "26"),
    ("OHC1", "Quasi-Isotropic Open Hole Compression", "[45/0/-45/90]3S", "normalized", "RTD, ETW", "26"),
    ("0° compression", "0° Compression Strength from UNC0 Data (computed via the formulas of NCP-RP-2009-028 "
     "Rev B section 2.5)", "—", "computed", "RTD, ETD, ETW", "27"),
    ("LT", "Longitudinal Tension", "[0]6", "normalized", "CTD, RTD, ETW", "32"),
    ("UNT0", "Unnotched Tension", "[0/90]2s", "normalized", "CTD, RTD, ETW", "32"),
    ("OHT1", "Quasi-Isotropic Open Hole Tension", "[45/0/-45/90]2s", "normalized", "CTD, RTD, ETW", "32"),
    ("IPS", "In-Plane Shear (strength at 5% strain; 0.2% offset strength)", "[45/−45]3s", "not normalized",
     "5% strain: RTD, ETW; 0.2% offset: CTD, RTD, ETW", "39"),
    ("SBS", "Short Beam Strength", "[0]34", "not normalized", "RTD, ETW", "39"),
)


# --------------------------------------------------------------------------- geometry helpers


@dataclass
class Word:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def xc(self) -> float:
        return 0.5 * (self.x0 + self.x1)

    @property
    def yc(self) -> float:
        return 0.5 * (self.y0 + self.y1)


@dataclass
class Line:
    y: float
    words: list[Word] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)


def page_lines(page: fitz.Page) -> list[Line]:
    words = [Word(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]
    words.sort(key=lambda w: (w.yc, w.x0))
    lines: list[Line] = []
    for w in words:
        if lines and abs(lines[-1].y - w.yc) <= 2.5:
            lines[-1].words.append(w)
        else:
            lines.append(Line(w.yc, [w]))
    for ln in lines:
        ln.words.sort(key=lambda w: w.x0)
    return lines


class ExtractionError(RuntimeError):
    pass


def find_caption(lines: list[Line], table: int, page: int) -> int:
    hits = [i for i, ln in enumerate(lines)
            if len(ln.words) > 2 and ln.words[0].text == "Table" and ln.words[1].text == str(table)]
    if len(hits) != 1:
        raise ExtractionError(f"Table {table}: expected one caption on PDF page {page}, found {len(hits)}")
    return hits[0]


def assign(value_words: list[Word], centres: list[float], where: str) -> dict[int, Word]:
    pitch = min((b - a for a, b in zip(centres, centres[1:], strict=False)), default=200.0)
    out: dict[int, Word] = {}
    for w in value_words:
        j = min(range(len(centres)), key=lambda k: abs(centres[k] - w.xc))
        if abs(centres[j] - w.xc) > 0.45 * pitch:
            raise ExtractionError(f"{where}: token {w.text!r} at x={w.xc:.1f} is not under any column")
        if j in out:
            raise ExtractionError(f"{where}: two tokens in column {j}: {out[j].text!r}, {w.text!r}")
        out[j] = w
    return out


def cell_text(raw: str) -> str:
    """Printed token -> md cell (``12.3*`` -> ``12.3 [*]``)."""
    if raw.endswith("*"):
        return f"{raw[:-1]} [*]"
    return raw


@dataclass
class Table:
    spec: Spec
    title: str
    columns: list[str]
    rows: list[tuple[int, str, list[str]]]           # (pdf page, label, cells)
    notes: list[str]
    meta: list[tuple[str, str]]


def merge_phrases(words: list[Word]) -> list[tuple[float, float, str]]:
    """Merge header words into phrases by horizontal overlap (gap <= 6 pt), across lines."""
    clusters: list[list[Word]] = []
    for w in sorted(words, key=lambda w: w.x0):
        if clusters and w.x0 <= max(v.x1 for v in clusters[-1]) + 6.0:
            clusters[-1].append(w)
        else:
            clusters.append([w])
    out = []
    for c in clusters:
        text_words = sorted(c, key=lambda w: (round(w.yc), w.x0))
        out.append((min(w.x0 for w in c), max(w.x1 for w in c), " ".join(w.text for w in text_words)))
    return out


def extract_grouped(doc: fitz.Document, spec: Spec) -> Table:
    lines = page_lines(doc[spec.page - 1])
    ci = find_caption(lines, spec.table, spec.page)
    title = " ".join(w.text for w in lines[ci].words[2:])
    env_i = next((i for i in range(ci + 1, len(lines)) if lines[i].words[0].text == "Environment"), None)
    if env_i is None:
        raise ExtractionError(f"Table {spec.table}: no 'Environment' line")
    env_words = lines[env_i].words[1:]
    if not env_words or any(w.text not in ENV_TOKENS for w in env_words):
        raise ExtractionError(f"Table {spec.table}: unexpected environment line {lines[env_i].text!r}")
    centres = [w.xc for w in env_words]
    boundary = env_words[0].x0 - 2.0
    band: list[Word] = []
    label_words: list[Word] = []
    for ln in lines[ci + 1:env_i]:
        lead = 0
        while lead < len(ln.words) and ln.words[lead].text in ("Test", "Property"):
            lead += 1
        label_words += ln.words[:lead]
        band += ln.words[lead:]
    if " ".join(w.text for w in label_words) not in ("Property", "Test Property"):
        raise ExtractionError(f"Table {spec.table}: unexpected header label {label_words}")
    phrases = merge_phrases(band)
    if tuple(p[2] for p in phrases) != spec.groups:
        raise ExtractionError(f"Table {spec.table}: header phrases {[p[2] for p in phrases]} != {spec.groups}")
    groups = [min(phrases, key=lambda p: abs(0.5 * (p[0] + p[1]) - c))[2] for c in centres]
    for g in spec.groups:  # each group must own a contiguous, non-empty run of columns
        idx = [k for k, x in enumerate(groups) if x == g]
        if not idx or idx != list(range(idx[0], idx[-1] + 1)):
            raise ExtractionError(f"Table {spec.table}: group {g!r} has columns {idx}")
    columns = [f"{g} / {w.text}" for g, w in zip(groups, env_words, strict=True)]

    rows: list[tuple[int, str, list[str]]] = []
    notes: list[str] = []
    pages = [(spec.page, lines[env_i + 1:])]
    if spec.continues_on is not None:
        pages.append((spec.continues_on, page_lines(doc[spec.continues_on - 1])))
    done = False
    for pno, body in pages:
        for ln in body:
            if done:
                break
            if ln.y < RUNNING_HEADER_MAX_Y:
                continue
            if ln.y > FOOTER_MIN_Y:
                break
            if ln.words[0].text.startswith("*"):
                notes.append(ln.text)
                done = True
                break
            labels = [w for w in ln.words if w.x1 < boundary and not VALUE_RE.match(w.text)]
            values = [w for w in ln.words if w not in labels]
            if not values or not labels or any(not VALUE_RE.match(w.text) for w in values):
                done = True
                break
            cells = assign(values, centres, f"Table {spec.table} p{pno} {ln.text!r}")
            if len(cells) != len(centres):
                raise ExtractionError(f"Table {spec.table} p{pno}: row {ln.text!r} has {len(cells)} of "
                                      f"{len(centres)} cells")
            label = " ".join(w.text for w in labels)
            rows.append((pno, label, [cell_text(cells[k].text) for k in range(len(centres))]))
        if done:
            break
    if not rows:
        raise ExtractionError(f"Table {spec.table}: no data rows")
    meta = [("groups", "; ".join(spec.groups))]
    return Table(spec, title, columns, rows, notes, meta)


def extract_stats(doc: fitz.Document, spec: Spec) -> Table:
    lines = page_lines(doc[spec.page - 1])
    ci = find_caption(lines, spec.table, spec.page)
    title = " ".join(w.text for w in lines[ci].words[2:])
    hi = next((i for i in range(ci + 1, len(lines)) if lines[i].words[0].text == "Qual."), None)
    if hi is None:
        raise ExtractionError(f"Table {spec.table}: no 'Qual.' header line")
    head = lines[hi].words
    if tuple(w.text for w in head) != STATS_COLUMNS:
        raise ExtractionError(f"Table {spec.table}: header {[w.text for w in head]}")
    centres = [w.xc for w in head]
    boundary = head[0].x0 - 2.0
    heading = [ln.text for ln in lines[ci + 1:hi]]
    in_table_title = heading[0] if heading else ""
    if not heading or "by Batch and Company" not in in_table_title:
        raise ExtractionError(f"Table {spec.table}: no in-table title line, got {heading}")
    pooled_ok = any(w.text == "Pooled" and abs(w.xc - centres[-1]) < 20 for ln in lines[ci + 1:hi] for w in ln.words)
    if not pooled_ok:
        raise ExtractionError(f"Table {spec.table}: 'Pooled' heading not found above the 'Dataset' column")
    columns = ["Qual.", *STATS_COLUMNS[1:-1], "Pooled"]
    rows: dict[str, list[str]] = {}
    spans: list[tuple[int, str]] = []
    for ln in lines[hi + 1:]:
        if ln.y > FOOTER_MIN_Y:
            break
        labels = [w for w in ln.words if w.x1 < boundary]
        values = [w for w in ln.words if w.x1 >= boundary]
        label = " ".join(w.text for w in labels)
        if not labels:
            if values and all(w.text == "NA" for w in values):
                for j, w in assign(values, centres, f"Table {spec.table} NA line").items():
                    spans.append((j, w.text))
                continue
            break
        if label not in STATS_ROWS or label in rows:
            break
        if any(not VALUE_RE.match(w.text) or w.text.endswith("*") for w in values):
            raise ExtractionError(f"Table {spec.table}: malformed row {ln.text!r}")
        cells = assign(values, centres, f"Table {spec.table} {label}")
        rows[label] = [cells[k].text if k in cells else "—" for k in range(len(centres))]
    if tuple(rows) != STATS_ROWS:
        raise ExtractionError(f"Table {spec.table}: rows {list(rows)} != {STATS_ROWS}")
    notes = []
    for j, text in spans:
        filled = [r for r in STATS_ROWS if rows[r][j] == "—"]
        if not filled:
            raise ExtractionError(f"Table {spec.table}: spanning {text} over a full column {columns[j]}")
        for r in filled:
            rows[r][j] = text
        notes.append(f"column {columns[j]}: one '{text}' is printed in a cell spanning rows {', '.join(filled)}; "
                     "it is repeated in each of them")
    for r in STATS_ROWS:
        if "—" in rows[r]:
            raise ExtractionError(f"Table {spec.table}: empty cell in row {r}: {rows[r]}")
    meta = [("in_table_title", in_table_title)]
    return Table(spec, title, columns, [(spec.page, r, rows[r]) for r in STATS_ROWS], notes, meta)


# --------------------------------------------------------------------------- page facts


def page_text(doc: fitz.Document, pno: int) -> str:
    return " ".join(doc[pno - 1].get_text("text").split())


def require(doc: fitz.Document, pno: int, phrase: str) -> str:
    if phrase not in page_text(doc, pno):
        raise ExtractionError(f"PDF page {pno} does not contain {phrase!r}")
    return phrase


# --------------------------------------------------------------------------- markdown


def render(doc: fitz.Document, tables: list[Table], sha: str, size: int) -> str:
    title = require(doc, 1, "A Comparison of Equivalence Criteria and Basis Values for HEXCEL 8552 IM7 "
                            "Unidirectional Tape computed from the NCAMP shared database")
    require(doc, 1, "Report No: NCP-RP-2013-015 Rev A")
    require(doc, 1, "Report Date: Oct 31, 2013")
    require(doc, 1, "Elizabeth Clarkson, Ph.D.")
    caveat = require(doc, 12, "Generic basis values have not yet been approved by the CMH-17 organization.")
    require(doc, 2, "Army Data Values Redacted.")
    require(doc, 41, "180°F for the HEXCEL Product data versus 250°F for the NCAMP results.")
    require(doc, 29, "ksi")
    require(doc, 12, "NCAMP Material Specification NMS 128/2")
    require(doc, 97, "Hexcel 8552 IM7 Unidirectional Prepreg 190 gsm & 35%RC")
    out = [
        "---",
        "material: ncamp-8552-im7",
        "material_name: Hexcel 8552 IM7 unidirectional tape (prepreg); NCAMP shared database",
        f"source_document: NCAMP Report No. NCP-RP-2013-015 Rev A, {title}, Elizabeth Clarkson, National Center "
        "for Advanced Materials Performance (NCAMP), National Institute for Aviation Research, Wichita State "
        "University, report date Oct 31, 2013",
        f"source_file: {SOURCE_REL}",
        f"source_sha256: {sha}",
        f"source_bytes: {size}",
        f"source_pages: {doc.page_count}",
        "source_origin: downloaded from cmh17.org (stated in the task; the download URL is not recorded here)",
        "running_header: every page from PDF page 3 on prints 'May 24, 2013 NCP-RP-2013-015 N/C'; the cover "
        "(PDF page 1) and revision list (PDF page 2) say Rev A, Oct 31, 2013 ('Army Data Values Redacted. "
        "Sections 3.5 and 3.6 updated.')",
        "printed_page_numbers: equal to the PDF page numbers",
        f"approval_caveat: \"{caveat}\" (PDF page 12)",
        "units: the tables print no unit; strengths, standard deviations, basis values and acceptance limits are "
        "ksi (axis label 'ksi' on the figures of the same data, e.g. Figure 6 on PDF page 29); 'Coeff Var.' is "
        "printed in percent; 'Count' is a number of specimens. The report contains no modulus (msi) values.",
        "conditions: CTD, RTD, ETD, ETW as printed; the only temperature stated is 250°F for the NCAMP ETW "
        "results (PDF page 41, '180°F for the HEXCEL Product data versus 250°F for the NCAMP results'); the "
        "report gives no CTD/ETD temperature and no moisture conditioning details",
        "not_in_source: E1t, E1c, E2, nu12, G12, F2tu, F2cu, bearing, cured ply thickness, fibre volume, density",
        "extraction: automatic (scripts/materials/extract_ncamp_8552_im7.py, PyMuPDF words); all table numbers "
        "parsed automatically; only the '## Test descriptions' section is transcribed by hand (marked manual)",
        "---",
        "",
        "# Hexcel 8552 IM7 unidirectional tape — NCAMP NCP-RP-2013-015 Rev A",
        "",
        "Strength data of the NCAMP shared database (one qualification sample, units A01-A03, and",
        "equivalency samples from other composite part manufacturers, units A2-A12). Basis values are",
        "given by three methods as printed: qualification (CMH-17 Rev G Section 8.3), pooled data (ANOVA)",
        "and generic (NCAMP approach of this report, not approved by CMH-17).",
        "Cell syntax: `84.42` = value as printed; `53.86 [*]` = value printed with an asterisk (see the",
        "table note); `NA` = printed NA; `5.91%` = printed percentage. Each row carries its PDF page.",
        "",
        "## Test descriptions",
        "",
        "- extraction: manual (transcribed from the prose on PDF pages 26, 27, 32 and 39; layup subscripts "
        "read from the text layer)",
        "",
        "| test | description | layup | data | environments | pdf page |",
        "|:---|:---|:---|:---|:---|---:|",
    ]
    out +=[f"| {' | '.join(row)} |" for row in TEST_DESCRIPTIONS]
    out.append("")
    for t in tables:
        out += [f"## Table {t.spec.table}", "", f"- title: {t.title}", f"- kind: {t.spec.kind}",
                "- pdf_page: " + ", ".join(str(p) for p in dict.fromkeys(r[0] for r in t.rows)),
                "- extraction: automatic"]
        out += [f"- {k}: {v}" for k, v in t.meta]
        out += [f"- note: {n}" for n in t.notes]
        out.append("")
        out.append("| page | row | " + " | ".join(t.columns) + " |")
        out.append("|---:|:---|" + "|".join(["---:"] * len(t.columns)) + "|")
        for pno, label, cells in t.rows:
            out.append(f"| {pno} | {label} | " + " | ".join(cells) + " |")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    data = args.pdf.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    doc = fitz.open(stream=data, filetype="pdf")
    if doc.page_count != EXPECTED_PAGES:
        raise ExtractionError(f"expected {EXPECTED_PAGES} pages, got {doc.page_count}")
    tables = [extract_stats(doc, s) if s.kind == "stats" else extract_grouped(doc, s) for s in SPECS]
    text = render(doc, tables, sha, len(data))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8", newline="\n")
    n = sum(len(c) for t in tables for _, _, c in t.rows)
    print(f"wrote {args.out}: {len(tables)} tables, {n} cells, sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
