"""Digitize the MIL-HDBK-5J figure pages listed in ``figures/index.md`` from their vector paths.

The PDF is treated as untrusted *data*: it is only opened and read with PyMuPDF.
Run with the isolated interpreter flag from the project root::

    python -I scripts/materials/digitize_figures.py \
        references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf \
        --index src/aerokit/materials/data/figures/index.md \
        --out src/aerokit/materials/data/curves

How it works (deterministic, no manual digitizing)
--------------------------------------------------
1. **Figure region.** Every caption line ``Figure <id>.`` on the page (indexed or
   not) is located; a figure occupies the band between the previous caption block
   (or the running header) and its own caption, so two figures on one page are
   separated by their captions.
2. **Text.** Text lines come from ``page.get_text("dict")``; small or raised/lowered
   digit spans become ``^``/``_`` (``10^3 ksi``, ``F_tu``). Type 3 fonts without a
   ToUnicode map whose glyphs are named by TrueType glyph id (``/G13``) are decoded
   with the standard Macintosh glyph order (gid + 29 = ASCII; pages 228, 638, 696).
   A line is *visible* if removing the text layer (redaction on an in-memory copy
   of the page) changes >= 0.5 % of the pixels of its box; hidden layers under
   white boxes are discarded. Of two overlapping lines the one painted later wins.
3. **Frame.** The plot frame is spanned by the longest axis-aligned stroked
   segments in the region: left/right from horizontal lines >= 90 % of the
   longest one, top/bottom from vertical lines >= 90 % of the longest one.
4. **Axes.** Numeric tick labels are grouped into rows below the frame (x axes,
   nearest first) and columns left/right of the frame (y axes, nearest first).
   A first least-squares fit on the label centres predicts each tick position; it
   is snapped to the nearest grid line / tick mark (purely horizontal/vertical
   strokes reaching the band between labels and frame) within ``SNAP_TOL`` (heavier
   stroke wins within 0.3 pt), and ``v = a*p + b`` (``log10 v`` for a geometric
   label sequence whose log fit is better) is refitted over all ticks. RMS and max
   residuals are reported as % of the axis span. Axis titles are the text lines
   between tick rows/columns.
5. **Curves.** Stroked, non-white, non-rectangle sub-paths inside the frame are
   flattened (cubic Beziers sampled at 16 points); paths crossing the frame are
   clipped to it. Excluded and counted: purely horizontal/vertical paths (after a
   0.1 pt simplification: frame, grid, ticks, reference lines, underlines), white
   strokes, dashed strokes, filled shapes (dash fragments, arrowheads), fragments
   shorter than 6 pt, *leaders* (<= 3 straight segments with one end at a label text
   or its white box, extended through kinks) and open arrowheads touching a leader.
   Pieces lying within half the stroke width of longer pieces are duplicates.
   Pieces of equal width meeting end-to-end at a node of degree 2 are chained if the
   curve does not reverse there. Shared low-x parts are attached: a dropped
   duplicate that ends where a curve starts is that curve's own path; a trunk whose
   end starts >= 2 branches is prepended to each; a curve starting on another
   curve's interior gets that curve's part to the left (recorded per curve).
6. **Labels**, in this order: (i) leaders - the tail picks the label whose centre
   line is nearest (stacked labels with one leader each are matched in vertical
   order), the tip (or the far vertex of a filled arrowhead) picks the nearest
   curve, which must be ``LEADER_MARGIN`` nearer than the second; (ii) text placed
   just beyond a curve end (end point inside the text height, gap <= ``END_GAP``);
   (iii) adjacent text within ``ADJ_TOL`` of one curve and clearly farther
   (``ADJ_RATIO``) from the others; (iv) the only label of a one-curve plot. A label
   that reaches two curves of the same kind is ambiguous and dropped. On
   stress-strain figures a curve whose stress falls while x grows is a
   tangent-modulus curve and is read on the axis titled "Tangent Modulus"; with
   several y axes the label must name the axis ("α, 4130" -> "α, 10-6 ...").
7. **Output.** Curves single-valued in x (backward steps <= ``BACKSTEP_TOL`` or pen
   retraces along the drawn line are left out) keep <= 60 source vertices chosen by
   Ramer-Douglas-Peucker with the smallest tolerance (padded to 20 points along the
   arc); curves single-valued in y (tangent modulus) likewise; other curves keep all
   source vertices. The max deviation from the source polyline is written per curve.

Every skipped element is listed in the output file; nothing is guessed.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np

SOURCE_REL = "references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf"
GENERATOR = "scripts/materials/digitize_figures.py"

AXIS_TOL = 0.25          # pt: a segment is horizontal/vertical if |dy| (|dx|) <= this
NODE_TOL = 0.35          # pt: two path ends are the same node
COVER_TOL = 0.4          # pt: duplicate-path tolerance
MIN_CURVE_LEN = 6.0      # pt: shorter stroked fragments are not curves
SNAP_TOL = 2.5           # pt: fitted tick position -> grid line / tick mark
LEADER_TAIL_TOL = 6.0    # pt: leader end to label box
LEADER_TIP_TOL = 3.0     # pt: leader tip to curve
LEADER_MARGIN = 0.75     # pt: second-nearest curve must be this much farther from the tip
ADJ_TOL = 12.0           # pt: label box to curve (no leader)
END_GAP = 45.0           # pt: max gap between a curve end and an end-of-line label
ADJ_RATIO = 1.5          # second-nearest curve must be >= ratio * nearest + 2 pt away
BACKSTEP_TOL = 1.0       # pt: tolerated backward x step (drawing artefacts, overlapping joins)
ARROW_LEN = 12.0         # pt: longest open arrowhead stroke
MAX_POINTS = 60
MIN_POINTS = 20

NUM_RE = re.compile(r"^[-−–]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?$|^[-−]?\.\d+$")
CAPTION_RE = re.compile(r"^Figure\s+(\d+(?:\.\d+)+(?:\([a-z0-9]+\))?)\.")
PRINTED_PAGE_RE = re.compile(r"^[1-9A-Z]-\d+$")
ANNOTATION_RE = re.compile(
    r"^(?:TYPICAL|Ramberg|n\s*\(|n\(|Thickness|Strength at|Exposure up|Modulus at|Elongation at|"
    r"Note|Dynamic modulus|Downloaded|MIL-HDBK|\d+ January|TYS|[ααKC] - )", re.I)


# --------------------------------------------------------------------------- data classes


@dataclass
class TLine:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    horizontal: bool
    vertical: bool
    size: float
    box: tuple[float, float, float, float] | None = None    # white label box drawn behind the text

    @property
    def cx(self) -> float:
        return 0.5 * (self.x0 + self.x1)

    @property
    def cy(self) -> float:
        return 0.5 * (self.y0 + self.y1)

    def dist(self, p: np.ndarray) -> float:
        dx = max(self.x0 - p[0], 0.0, p[0] - self.x1)
        dy = max(self.y0 - p[1], 0.0, p[1] - self.y1)
        return math.hypot(dx, dy)

    def centerline_dist(self, p: np.ndarray) -> float:
        """Distance to the horizontal centre line of the text (leaders start level with their label)."""
        return math.hypot(max(self.x0 - p[0], 0.0, p[0] - self.x1), p[1] - self.cy)

    def tail_dist(self, p: np.ndarray) -> float:
        """Distance to the text or to the white box drawn behind it (where leaders start)."""
        d = self.dist(p)
        if self.box:
            bx0, by0, bx1, by1 = self.box
            d = min(d, math.hypot(max(bx0 - p[0], 0.0, p[0] - bx1), max(by0 - p[1], 0.0, p[1] - by1)))
        return d


@dataclass
class Sub:
    pts: np.ndarray            # (n, 2) polyline in page points
    width: float
    dashed: bool
    didx: int                  # drawing index
    nseg: int                  # number of source segments (lines + curves)
    straight: bool             # only 'l' items

    @property
    def length(self) -> float:
        return float(np.sum(np.hypot(*np.diff(self.pts, axis=0).T))) if len(self.pts) > 1 else 0.0


@dataclass
class Axis:
    name: str                  # x1, x2, y1, y2 ...
    side: str                  # bottom, left, right
    title: str
    unit: str
    scale: str                 # linear | log
    a: float
    b: float
    ticks: list[tuple[float, float, bool]]   # (pixel, value, snapped)
    rms_pct: float
    max_pct: float

    def to_data(self, p: np.ndarray) -> np.ndarray:
        v = self.a * p + self.b
        return np.power(10.0, v) if self.scale == "log" else v

    def to_pixel(self, v: np.ndarray) -> np.ndarray:
        w = np.log10(v) if self.scale == "log" else v
        return (w - self.b) / self.a


@dataclass(eq=False)
class Chain:
    pts: np.ndarray
    width: float
    members: list[int]
    notes: list[str] = field(default_factory=list)
    label: str | None = None
    label_how: str = ""
    kind: str = ""             # stress-strain | tangent-modulus | curve


@dataclass
class FigureEntry:
    figure: str
    pdf_page: int
    printed_page: str
    file: str
    materials: list[str]
    caption: str


# --------------------------------------------------------------------------- index


def read_index(path: Path) -> list[FigureEntry]:
    out: list[FigureEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith(("| figure", "|:")):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            raise ValueError(f"bad index row: {line}")
        m = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", cells[3])
        if not m:
            raise ValueError(f"bad file cell: {cells[3]}")
        out.append(FigureEntry(cells[0], int(cells[1]), cells[2], m.group(2),
                               [s.strip() for s in cells[4].split(",")], cells[5]))
    return out


def figure_slug(fig: str) -> str:
    m = re.fullmatch(r"(\d+(?:\.\d+)+)(?:\(([a-z0-9]+)\))?", fig)
    if not m:
        raise ValueError(f"bad figure id {fig!r}")
    return "fig-" + m.group(1).replace(".", "-") + (m.group(2) or "")


# --------------------------------------------------------------------------- text


GLYPH_FIX = {"\ufffdF": "°F"}     # Symbol-font degree sign without Unicode mapping (page 80)


def _fix(s: str) -> str:
    for k, v in GLYPH_FIX.items():
        s = s.replace(k, v)
    return s


#: Standard Macintosh glyph order (TrueType 'post' format 2): glyph ids 3..97 are ASCII 32..126.
_MAC_EXTRA = {131: "°", 147: "±", 148: "≤", 149: "≥", 151: "µ"}


def type3_decoders(page: fitz.Page) -> dict[str, dict[str, str]]:
    """Code -> text for Type 3 fonts whose glyphs are named by TrueType glyph id (``/G13`` = gid 0x13).

    Several figure pages embed Arial as Type 3 fonts without a ToUnicode map; their glyph names are
    the original TrueType glyph ids, which follow the standard Macintosh order (gid + 29 = ASCII for
    gids 3..97; a few symbols in ``_MAC_EXTRA``). Unknown glyphs decode to U+FFFD.
    """
    doc = page.parent
    out: dict[str, dict[str, str]] = {}
    for xref, _ext, ftype, _base, name, _enc in page.get_fonts():
        if ftype != "Type3":
            continue
        obj = doc.xref_object(xref)
        m = re.search(r"/Encoding\s+(\d+)\s+0\s+R", obj)
        enc = doc.xref_object(int(m.group(1))) if m else obj
        dm = re.search(r"/Differences\s*\[([^\]]*)\]", enc)
        if not dm:
            continue
        table: dict[str, str] = {}
        code = 0
        for tok in dm.group(1).split():
            if tok.isdigit():
                code = int(tok)
                continue
            g = re.fullmatch(r"/G([0-9A-Fa-f]+)", tok)
            if g:
                gid = int(g.group(1), 16)
                table[chr(code)] = chr(gid + 29) if 3 <= gid <= 97 else _MAC_EXTRA.get(gid, "\ufffd")
            else:
                table[chr(code)] = "\ufffd"
            code += 1
        out[name] = table
    return out


def render_without_text(page: fitz.Page, zoom: float) -> tuple[np.ndarray, np.ndarray]:
    """Grey renderings of the page with and without its text layer (text removed by redaction on a copy)."""
    def grey(pg: fitz.Page) -> np.ndarray:
        pix = pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY, alpha=False)
        return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.int16)
    with_text = grey(page)
    tmp = fitz.open()
    tmp.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
    cp = tmp[0]
    cp.add_redact_annot(cp.rect)
    cp.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                        text=fitz.PDF_REDACT_TEXT_REMOVE)
    no_text = grey(cp)
    tmp.close()
    return with_text, no_text


def page_text_lines(page: fitz.Page, renders: tuple[np.ndarray, np.ndarray], zoom: float) -> list[TLine]:
    """Visible text lines. A line is visible if removing the text layer changes >= 0.5 % of the pixels
    in its box (text covered by a white box, or drawn in white, changes nothing)."""
    diff = np.abs(renders[0] - renders[1]) > 60
    out: list[TLine] = []
    d = page.get_text("dict")
    dec = type3_decoders(page)
    for b in d["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            for s in ln["spans"]:
                if s["font"] in dec:
                    s["text"] = "".join(dec[s["font"]].get(ch, ch if ch == " " else "\ufffd") for ch in s["text"])
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            dx, dy = ln["dir"]
            horizontal = abs(dy) < 1e-3 and dx > 0
            vertical = abs(dx) < 1e-3
            main = max(s["size"] for s in spans)
            parts: list[str] = []
            base = [s for s in spans if s["size"] >= 0.8 * main]
            ref = 0.5 * (base[0]["bbox"][1] + base[0]["bbox"][3]) if horizontal else 0.0
            for s in spans:
                t = s["text"]
                c = 0.5 * (s["bbox"][1] + s["bbox"][3])
                small = s["size"] < 0.8 * main
                shifted = abs(c - ref) > 0.2 * main and t.strip().isdigit()      # e.g. 10 + raised 3
                if horizontal and (small or shifted):
                    t = ("^" if c < ref - 0.5 else "_") + t.strip()
                parts.append(t)
            text = _fix(re.sub(r"\s+", " ", "".join(parts)).strip())
            x0, y0, x1, y1 = ln["bbox"]
            if horizontal:                       # leading/trailing blanks widen the box: trim them
                f, l_ = spans[0], spans[-1]
                lead = len(f["text"]) - len(f["text"].lstrip())
                trail = len(l_["text"]) - len(l_["text"].rstrip())
                x0 += lead * (f["bbox"][2] - f["bbox"][0]) / max(len(f["text"]), 1)
                x1 -= trail * (l_["bbox"][2] - l_["bbox"][0]) / max(len(l_["text"]), 1)
            # visibility on the rendered page
            ix0, iy0 = max(int(x0 * zoom), 0), max(int(y0 * zoom), 0)
            ix1, iy1 = min(int(math.ceil(x1 * zoom)), diff.shape[1]), min(int(math.ceil(y1 * zoom)), diff.shape[0])
            patch = diff[iy0:iy1, ix0:ix1]
            if patch.size == 0 or float(np.mean(patch)) < 0.005:
                continue
            out.append(TLine(text, x0, y0, x1, y1, horizontal, vertical, main))
    # overlapping text: the line painted later (content order) is the one on top; drop the earlier one
    keep = [True] * len(out)
    for i, a in enumerate(out):
        for j in range(i + 1, len(out)):
            b = out[j]
            ix = min(a.x1, b.x1) - max(a.x0, b.x0)
            iy = min(a.y1, b.y1) - max(a.y0, b.y0)
            if ix > 0 and iy > 0:
                small = min((a.x1 - a.x0) * (a.y1 - a.y0), (b.x1 - b.x0) * (b.y1 - b.y0))
                if small > 0 and ix * iy > 0.3 * small:
                    keep[i] = False
    return [ln for ln, k in zip(out, keep, strict=True) if k]


def printed_page(lines: list[TLine]) -> str:
    cands = [ln for ln in lines if ln.y0 > 700 and PRINTED_PAGE_RE.match(ln.text)]
    return cands[0].text if len(cands) == 1 else ""


def caption_blocks(page: fitz.Page) -> list[tuple[str, float, float, str]]:
    """(figure id, top y, bottom y, caption text) for each caption on the page, top to bottom."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        lines = b["lines"]
        texts = ["".join(s["text"] for s in ln["spans"]) for ln in lines]
        for i, t in enumerate(texts):
            m = CAPTION_RE.match(t.strip())
            if m:
                cap = " ".join(x.strip() for x in texts[i:])
                out.append((m.group(1), lines[i]["bbox"][1], b["bbox"][3], re.sub(r"\s+", " ", cap)))
                break
    return sorted(out, key=lambda c: c[1])


# --------------------------------------------------------------------------- drawings


def _bezier(p0: fitz.Point, p1: fitz.Point, p2: fitz.Point, p3: fitz.Point, n: int = 16) -> np.ndarray:
    t = np.linspace(0.0, 1.0, n + 1)[:, None]
    a = np.array([p0.x, p0.y])
    b = np.array([p1.x, p1.y])
    c = np.array([p2.x, p2.y])
    d = np.array([p3.x, p3.y])
    return ((1 - t) ** 3) * a + 3 * ((1 - t) ** 2) * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d


@dataclass
class PageGeom:
    subs: list[Sub]                     # stroked open sub-paths (non-white)
    axis_segments: list[tuple[float, float, float, float, float]]   # x0,y0,x1,y1,width
    filled: list[np.ndarray]            # filled shapes (vertices)
    n_white: int
    n_rect: int
    white_boxes: list[tuple[float, float, float, float]] = field(default_factory=list)


def page_geometry(page: fitz.Page) -> PageGeom:
    subs: list[Sub] = []
    axis_segments: list[tuple[float, float, float, float, float]] = []
    filled: list[np.ndarray] = []
    white_boxes: list[tuple[float, float, float, float]] = []
    n_white = n_rect = 0
    for di, d in enumerate(page.get_drawings()):
        stroke = d.get("color")
        typ = d["type"]
        fill = d.get("fill")
        if fill is not None and min(fill) > 0.9:
            for it in d["items"]:
                if it[0] == "re":
                    r = it[1]
                    white_boxes.append((r.x0, r.y0, r.x1, r.y1))
        if typ == "f":
            if fill is None or min(fill) > 0.9:
                n_white += 1
                continue
            pts = []
            for it in d["items"]:
                if it[0] == "l":
                    pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
                elif it[0] == "re":
                    r = it[1]
                    pts += [(r.x0, r.y0), (r.x1, r.y1)]
                    # thin filled rectangles act as lines (rules, underlines)
                    if min(r.width, r.height) < 0.9 and max(r.width, r.height) > 2:
                        axis_segments.append((r.x0, (r.y0 + r.y1) / 2, r.x1, (r.y0 + r.y1) / 2, r.height)
                                             if r.width >= r.height else
                                             ((r.x0 + r.x1) / 2, r.y0, (r.x0 + r.x1) / 2, r.y1, r.width))
                elif it[0] == "c":
                    pts += [(it[1].x, it[1].y), (it[4].x, it[4].y)]
                elif it[0] == "qu":
                    q = it[1]
                    pts += [(q.ul.x, q.ul.y), (q.lr.x, q.lr.y)]
            if pts:
                filled.append(np.array(pts))
            continue
        if stroke is None:
            continue
        if min(stroke) > 0.9:
            n_white += 1
            continue
        width = float(d.get("width") or 0.0)
        dashed = bool(d.get("dashes")) and d.get("dashes") not in ("[] 0", "[] 0.0")
        cur: list[np.ndarray] = []
        cur_n = 0
        cur_straight = True

        def flush(width: float = width, dashed: bool = dashed, di: int = di) -> None:
            nonlocal cur, cur_n, cur_straight
            if cur:
                pts = np.vstack(cur)
                keep = np.ones(len(pts), bool)
                keep[1:] = np.hypot(*np.diff(pts, axis=0).T) > 1e-6
                subs.append(Sub(pts[keep], width, dashed, di, cur_n, cur_straight))
            cur, cur_n, cur_straight = [], 0, True

        for it in d["items"]:
            kind = it[0]
            if kind == "re":
                flush()
                n_rect += 1
                r = it[1]
                for seg in ((r.x0, r.y0, r.x1, r.y0), (r.x1, r.y0, r.x1, r.y1), (r.x0, r.y1, r.x1, r.y1),
                            (r.x0, r.y0, r.x0, r.y1)):
                    axis_segments.append((*seg, width))
                continue
            if kind == "qu":
                flush()
                n_rect += 1
                continue
            if kind == "l":
                seg = np.array([[it[1].x, it[1].y], [it[2].x, it[2].y]])
            elif kind == "c":
                seg = _bezier(it[1], it[2], it[3], it[4])
                cur_straight = cur_straight and False
            else:
                continue
            if cur and np.hypot(*(cur[-1][-1] - seg[0])) > NODE_TOL:
                flush()
            if kind == "c":
                cur_straight = False
            cur.append(seg if not cur else seg[1:])
            cur_n += 1
        flush()
    # axis-aligned straight runs (>= 1 pt) of the purely horizontal/vertical sub-paths: frame, grid, ticks,
    # rules (vertical parts of curves are not grid lines and are left out)
    for s in subs:
        if len(s.pts) < 2 or not is_axis_aligned(s):
            continue
        simp = s.pts[rdp(s.pts, 0.1)] if len(s.pts) > 2 else s.pts
        for (xa, ya), (xb, yb) in zip(simp[:-1], simp[1:], strict=True):
            if math.hypot(xb - xa, yb - ya) >= 1.0 and (abs(ya - yb) <= AXIS_TOL or abs(xa - xb) <= AXIS_TOL):
                axis_segments.append((xa, ya, xb, yb, s.width))
    return PageGeom(subs, axis_segments, filled, n_white, n_rect, white_boxes)


def is_axis_aligned(s: Sub) -> bool:
    """Only horizontal/vertical runs after simplification (RDP, 0.1 pt): grid, frame, ticks, rules."""
    simp = s.pts[rdp(s.pts, 0.1)] if len(s.pts) > 2 else s.pts
    d = np.diff(simp, axis=0)
    return bool(np.all((np.abs(d[:, 0]) <= AXIS_TOL) | (np.abs(d[:, 1]) <= AXIS_TOL)))


def seg_dist(p: np.ndarray, pts: np.ndarray) -> float:
    """Distance from point p to polyline pts."""
    if len(pts) == 1:
        return float(np.hypot(*(pts[0] - p)))
    a, b = pts[:-1], pts[1:]
    ab = b - a
    L2 = np.sum(ab * ab, axis=1)
    t = np.clip(np.sum((p - a) * ab, axis=1) / np.where(L2 > 0, L2, 1.0), 0.0, 1.0)
    q = a + t[:, None] * ab
    return float(np.min(np.hypot(*(q - p).T)))


def densify(pts: np.ndarray, step: float = 0.5) -> np.ndarray:
    """Insert points so that consecutive points are at most ``step`` pt apart."""
    if len(pts) < 2:
        return pts
    out = [pts[:1]]
    for a, b in zip(pts[:-1], pts[1:], strict=True):
        n = max(int(math.ceil(float(np.hypot(*(b - a))) / step)), 1)
        t = np.linspace(0.0, 1.0, n + 1)[1:, None]
        out.append(a + t * (b - a))
    return np.vstack(out)


def box_dist(ln: TLine, dense: np.ndarray) -> float:
    """Distance from a text box to a densified polyline (0 if they intersect)."""
    if len(dense) == 0:
        return math.inf
    dx = np.maximum.reduce([ln.x0 - dense[:, 0], np.zeros(len(dense)), dense[:, 0] - ln.x1])
    dy = np.maximum.reduce([ln.y0 - dense[:, 1], np.zeros(len(dense)), dense[:, 1] - ln.y1])
    return float(np.min(np.hypot(dx, dy)))


# --------------------------------------------------------------------------- frame and axes


def find_frame(geom: PageGeom, top: float, bottom: float) -> tuple[float, float, float, float] | None:
    hs = [(min(x0, x1), max(x0, x1), y0) for x0, y0, x1, y1, _ in geom.axis_segments
          if abs(y0 - y1) <= AXIS_TOL and top <= y0 <= bottom and abs(x1 - x0) > 20]
    vs = [(min(y0, y1), max(y0, y1), x0) for x0, y0, x1, y1, _ in geom.axis_segments
          if abs(x0 - x1) <= AXIS_TOL and top <= min(y0, y1) and max(y0, y1) <= bottom and abs(y1 - y0) > 20]
    if not hs or not vs:
        return None
    hmax = max(b - a for a, b, _ in hs)
    vmax = max(b - a for a, b, _ in vs)
    long_h = [h for h in hs if h[1] - h[0] >= 0.9 * hmax]
    long_v = [v for v in vs if v[1] - v[0] >= 0.9 * vmax]
    x0 = min(h[0] for h in long_h)
    x1 = max(h[1] for h in long_h)
    y0 = min(v[0] for v in long_v)
    y1 = max(v[1] for v in long_v)
    if x1 - x0 < 100 or y1 - y0 < 80:
        return None
    return (x0, y0, x1, y1)


def _num(text: str) -> float:
    return float(text.replace(",", "").replace("\u2212", "-").replace("\u2013", "-"))


def _cluster(items: list[TLine], key, tol: float) -> list[list[TLine]]:
    groups: list[list[TLine]] = []
    for it in sorted(items, key=key):
        if groups and abs(key(it) - key(groups[-1][-1])) <= tol:
            groups[-1].append(it)
        else:
            groups.append([it])
    return groups


def _fit(px: np.ndarray, vals: np.ndarray) -> tuple[str, float, float, float, float]:
    """Return (scale, a, b, rms %, max %) for the best of linear / log fits."""
    def lin(p: np.ndarray, v: np.ndarray) -> tuple[float, float, float, float]:
        A = np.vstack([p, np.ones_like(p)]).T
        (a, b), *_ = np.linalg.lstsq(A, v, rcond=None)
        r = A @ np.array([a, b]) - v
        span = float(np.ptp(v)) or 1.0
        return float(a), float(b), float(np.sqrt(np.mean(r * r)) / span * 100), float(np.max(np.abs(r)) / span * 100)
    a, b, rms, mx = lin(px, vals)
    if np.all(vals > 0) and len(vals) >= 3:
        s = np.sort(vals)
        ratios = s[1:] / s[:-1]
        if np.allclose(ratios, ratios[0], rtol=1e-6) and ratios[0] > 1.5:
            la, lb, lrms, lmx = lin(px, np.log10(vals))
            if lmx < mx:
                return "log", la, lb, lrms, lmx
    return "linear", a, b, rms, mx


def _snap(center: float, candidates: list[tuple[float, float]]) -> tuple[float, bool]:
    """Grid line / tick mark nearest to ``center`` within SNAP_TOL (heavier stroke wins within 0.3 pt)."""
    near = sorted((abs(p - center), -w, p) for p, w in candidates if abs(p - center) <= SNAP_TOL)
    if not near:
        return center, False
    close = [n for n in near if n[0] <= near[0][0] + 0.3]
    return min(close, key=lambda n: (n[1], n[0]))[2], True


def _snapped_fit(centers: list[float], vals: np.ndarray, candidates: list[tuple[float, float]]
                 ) -> tuple[list[float], list[bool], tuple[str, float, float, float, float]]:
    """Fit on label centres, snap each tick near its *fitted* position, refit on the snapped positions."""
    scale, a, b, _, _ = _fit(np.array(centers), vals)
    w = np.log10(vals) if scale == "log" else vals
    predicted = (w - b) / a
    pos, snapped = [], []
    for c, pr in zip(centers, predicted.tolist(), strict=True):
        q, ok = _snap(pr, candidates)
        pos.append(q if ok else c)
        snapped.append(ok)
    return pos, snapped, _fit(np.array(pos), vals)


def split_title(title: str) -> tuple[str, str]:
    """Quantity and unit as printed ("Stress, ksi" -> ("Stress", "ksi"))."""
    if "," in title:
        q, u = title.rsplit(",", 1)
        return q.strip(), u.strip()
    if re.match(r"^Percent", title, re.I):
        return title, "%"
    return title, ""


def find_axes(lines: list[TLine], geom: PageGeom, frame: tuple[float, float, float, float],
              top: float, bottom: float, skipped: list[str]) -> list[Axis]:
    fx0, fy0, fx1, fy1 = frame
    nums = [ln for ln in lines if ln.horizontal and NUM_RE.match(ln.text) and top <= ln.cy <= bottom]
    vsegs = [((x0 + x1) / 2, min(y0, y1), max(y0, y1), w) for x0, y0, x1, y1, w in geom.axis_segments
             if abs(x0 - x1) <= AXIS_TOL]
    hsegs = [((y0 + y1) / 2, min(x0, x1), max(x0, x1), w) for x0, y0, x1, y1, w in geom.axis_segments
             if abs(y0 - y1) <= AXIS_TOL]
    axes: list[Axis] = []
    # ---- x axes: rows below the frame
    below = [ln for ln in nums if fy1 - 3 <= ln.y0 and ln.cy <= fy1 + 90 and fx0 - 25 <= ln.cx <= fx1 + 25]
    rows = [r for r in _cluster(below, key=lambda t: t.cy, tol=2.0) if len(r) >= 3]
    texts = [ln for ln in lines if not NUM_RE.match(ln.text) and ln.horizontal and top <= ln.cy <= bottom]
    for k, row in enumerate(rows):
        row_bottom = max(t.y1 for t in row)
        nxt = min(t.y0 for t in rows[k + 1]) if k + 1 < len(rows) else row_bottom + 32
        row_cy = float(np.mean([t.cy for t in row]))
        titles = [t for t in texts if t.cy >= row_cy + 4 and t.y1 <= nxt + 1 and fx0 - 30 <= t.cx <= fx1 + 30
                  and not CAPTION_RE.match(t.text)]
        title = " / ".join(t.text for t in sorted(titles, key=lambda t: t.y0))
        row_top = min(t.y0 for t in row)
        band_lo = fy1 - 1.0 if k == 0 else row_top - 10.0
        cands = [(x, w) for x, ya, yb, w in vsegs if ya <= row_top + 0.5 and yb >= band_lo]
        vals = np.array([_num(t.text) for t in row])
        px, snapped, (scale, a, b, rms, mx) = _snapped_fit([t.cx for t in row], vals, cands)
        axes.append(Axis(f"x{k + 1}", "bottom", title, "", scale, a, b,
                         [(p, v, s) for p, v, s in zip(px, vals.tolist(), snapped, strict=True)], rms, mx))
    # ---- y axes: columns left / right of the frame
    vtexts = [ln for ln in lines if ln.vertical and not NUM_RE.match(ln.text) and top <= ln.cy <= bottom]
    for side in ("left", "right"):
        if side == "left":
            cand = [ln for ln in nums if fx0 - 80 <= ln.x1 <= fx0 + 1.5 and fy0 - 8 <= ln.cy <= fy1 + 8]
            cols = [c for c in _cluster(cand, key=lambda t: -t.x1, tol=2.5) if len(c) >= 3]
        else:
            cand = [ln for ln in nums if fx1 - 1.5 <= ln.x0 <= fx1 + 80 and fy0 - 8 <= ln.cy <= fy1 + 8]
            cols = [c for c in _cluster(cand, key=lambda t: t.x0, tol=2.5) if len(c) >= 3]
        for k, col in enumerate(cols):
            if side == "left":
                inner = min(t.x0 for t in col)
                outer = max(t.x1 for t in cols[k + 1]) if k + 1 < len(cols) else inner - 40
                titles = [t for t in vtexts if outer - 1 <= t.x0 and t.x1 <= inner + 1]
            else:
                inner = max(t.x1 for t in col)
                outer = min(t.x0 for t in cols[k + 1]) if k + 1 < len(cols) else inner + 40
                titles = [t for t in vtexts if inner - 1 <= t.x0 and t.x1 <= outer + 1]
            title = " / ".join(t.text for t in sorted(titles, key=lambda t: t.x0))
            if side == "left":
                edge = max(t.x1 for t in col)
                lo, hi = edge - 0.5, (fx0 + 1.0 if k == 0 else edge + 10.0)
            else:
                edge = min(t.x0 for t in col)
                lo, hi = (fx1 - 1.0 if k == 0 else edge - 10.0), edge + 0.5
            cands = [(y, w) for y, xa, xb, w in hsegs if xa <= hi and xb >= lo]
            vals = np.array([_num(t.text) for t in col])
            py, snapped, (scale, a, b, rms, mx) = _snapped_fit([t.cy for t in col], vals, cands)
            n = sum(1 for ax in axes if ax.name.startswith("y")) + 1
            axes.append(Axis(f"y{n}", side, title, "", scale, a, b,
                             [(p, v, s) for p, v, s in zip(py, vals.tolist(), snapped, strict=True)], rms, mx))
    for ax in axes:
        ax.unit = split_title(ax.title.split(" / ")[0])[1] if ax.title else ""
        if not ax.title:
            skipped.append(f"axis {ax.name} ({ax.side}): no axis title found next to its tick labels")
    return axes


# --------------------------------------------------------------------------- curves


def _inside(pts: np.ndarray, frame: tuple[float, float, float, float], pad: float) -> np.ndarray:
    x0, y0, x1, y1 = frame
    return (pts[:, 0] >= x0 - pad) & (pts[:, 0] <= x1 + pad) & (pts[:, 1] >= y0 - pad) & (pts[:, 1] <= y1 + pad)


def _node_key(p: np.ndarray, nodes: list[np.ndarray]) -> int:
    for i, q in enumerate(nodes):
        if abs(p[0] - q[0]) <= NODE_TOL and abs(p[1] - q[1]) <= NODE_TOL:
            return i
    nodes.append(p.copy())
    return len(nodes) - 1


def _covered(dense: np.ndarray, others: list[np.ndarray], tol: float) -> bool:
    """True if every point of ``dense`` lies within ``tol`` of the union of ``others`` (densified)."""
    if not others:
        return False
    allp = np.vstack(others)
    return all(float(np.min(np.hypot(*(allp - p).T))) <= tol for p in dense)


def _cover_tol(width: float) -> float:
    """Paths closer than half the stroke width are drawn on top of each other (indistinguishable)."""
    return max(COVER_TOL, 0.5 * width)


def _plen(pts: np.ndarray) -> float:
    return float(np.sum(np.hypot(*np.diff(pts, axis=0).T))) if len(pts) > 1 else 0.0


def chain_pieces(pieces: list[Sub], skipped: list[str]) -> list[Chain]:
    """Drop duplicate pieces, join pieces end to end at degree-2 nodes, then attach shared trunks."""
    order = sorted(range(len(pieces)), key=lambda i: -pieces[i].length)
    kept: list[Sub] = []
    kept_dense: list[np.ndarray] = []
    dropped: list[Sub] = []
    for i in order:
        s = pieces[i]
        d = densify(s.pts, 1.0)
        if _covered(d, kept_dense, _cover_tol(s.width)):
            skipped.append(f"duplicate path (drawing {s.didx}, {s.length:.0f} pt) lies on other curve paths; dropped")
            dropped.append(s)
            continue
        kept.append(s)
        kept_dense.append(densify(s.pts, 0.4))
    pieces = kept
    nodes: list[np.ndarray] = []
    ends: list[tuple[int, int]] = []
    for s in pieces:
        ends.append((_node_key(s.pts[0], nodes), _node_key(s.pts[-1], nodes)))
    incident: dict[int, list[tuple[int, int]]] = defaultdict(list)   # node -> [(piece, 0=start / 1=end)]
    for i, (a, b) in enumerate(ends):
        incident[a].append((i, 0))
        incident[b].append((i, 1))
    used = [False] * len(pieces)
    chains: list[Chain] = []

    def outward(i: int, e: int) -> np.ndarray:
        """Unit direction leaving the node along piece i (e = 0: node at its start, 1: at its end)."""
        pts = pieces[i].pts if e == 0 else pieces[i].pts[::-1]
        d = densify(pts, 0.5)
        k = min(len(d) - 1, 6)                       # ~3 pt away from the node
        v = d[k] - d[0]
        n = float(np.hypot(*v))
        return v / n if n > 0 else v

    def joinable(node: int) -> bool:
        inc = incident[node]
        if len(inc) != 2 or inc[0][0] == inc[1][0]:
            return False
        if abs(pieces[inc[0][0]].width - pieces[inc[1][0]].width) > 0.05:
            return False
        # a curve does not reverse: the two pieces must leave the node in opposite half-planes
        return float(np.dot(outward(*inc[0]), outward(*inc[1]))) < 0.0

    for i in range(len(pieces)):
        if used[i]:
            continue
        used[i] = True
        seq: list[tuple[int, bool]] = [(i, False)]          # (piece, reversed)
        for forward in (True, False):
            cur, cur_rev = seq[-1] if forward else seq[0]
            while True:
                at_end = forward != cur_rev                 # outer end of the current piece
                node = ends[cur][1] if at_end else ends[cur][0]
                if not joinable(node):
                    break
                j, e = next((j, e) for j, e in incident[node] if j != cur)
                if used[j]:
                    break
                used[j] = True
                rev = (e == 1) if forward else (e == 0)
                if forward:
                    seq.append((j, rev))
                else:
                    seq.insert(0, (j, rev))
                cur, cur_rev = j, rev
        parts: list[np.ndarray] = []
        for j, rev in seq:
            p = pieces[j].pts[::-1] if rev else pieces[j].pts
            parts.append(p if not parts else p[1:])
        chains.append(Chain(np.vstack(parts), pieces[i].width, [pieces[j].didx for j, _ in seq]))
    # a curve that starts where a dropped duplicate piece ends continues that piece (the curve's own drawn
    # low-x part, which lies on top of another curve): prepend it
    for c in chains:
        c.pts = _left_first(c.pts)
        grown = True
        while grown:
            grown = False
            for dp in dropped:
                q = _left_first(dp.pts)
                if float(np.hypot(*(q[-1] - c.pts[0]))) <= NODE_TOL and q[0][0] < c.pts[0][0] - 1.0:
                    c.pts = np.vstack([q, c.pts[1:]])
                    c.members = sorted(set(c.members) | {dp.didx})
                    c.notes.append(f"own low-x path (drawing {dp.didx}, drawn on top of another curve) prepended")
                    dropped = [x for x in dropped if x is not dp]
                    grown = True
                    break
    chains = _trunks(chains, skipped)
    # after trunks are attached, a chain drawn on top of the others is a duplicate
    chains.sort(key=lambda c: -_plen(c.pts))
    final: list[Chain] = []
    for c in chains:
        others = [densify(k.pts, 0.4) for k in chains if k is not c and (k in final or _plen(k.pts) > _plen(c.pts))]
        if _covered(densify(c.pts, 1.0), others, _cover_tol(c.width)):
            skipped.append(f"duplicate curve (drawings {sorted(set(c.members))}, {_plen(c.pts):.0f} pt) is drawn "
                           "on top of other curves; dropped")
            continue
        final.append(c)
    return final


def _left_first(pts: np.ndarray) -> np.ndarray:
    return pts if pts[-1][0] >= pts[0][0] else pts[::-1]


def _project(p: np.ndarray, pts: np.ndarray) -> tuple[float, int, np.ndarray]:
    """(distance, segment index, foot point) of the projection of p on polyline pts."""
    a, b = pts[:-1], pts[1:]
    ab = b - a
    L2 = np.sum(ab * ab, axis=1)
    t = np.clip(np.sum((p - a) * ab, axis=1) / np.where(L2 > 0, L2, 1.0), 0.0, 1.0)
    q = a + t[:, None] * ab
    d = np.hypot(*(q - p).T)
    k = int(np.argmin(d))
    return float(d[k]), k, q[k]


def _after(pts: np.ndarray, q: np.ndarray, tol: float) -> np.ndarray:
    """Drop the leading points of ``pts`` that sit at the junction ``q`` (within tol, not right of it)."""
    k = 0
    while k < len(pts) - 1 and float(np.hypot(*(pts[k] - q))) <= tol and pts[k][0] <= q[0] + 1e-9:
        k += 1
    return pts[k:]


def _trunks(chains: list[Chain], skipped: list[str]) -> list[Chain]:
    """Attach the shared low-x part (trunk) to curves that branch off it.

    * end-point rule: a chain whose right end is the left end of >= 2 other chains is a trunk; it is
      prepended to each of them and removed;
    * interior rule: a chain whose left end lies on the interior of another chain (within NODE_TOL)
      gets that chain's part to the left of the junction prepended.
    """
    out = [c for c in chains]
    for c in out:
        c.pts = _left_first(c.pts)
    changed = True
    while changed:
        changed = False
        for t in out:
            right = t.pts[-1]
            tol = _cover_tol(t.width)
            branches = [c for c in out if c is not t and float(np.hypot(*(c.pts[0] - right))) <= tol
                        and c.pts[-1][0] > c.pts[0][0] + 1.0]
            if len(branches) >= 2:
                for c in branches:
                    c.pts = np.vstack([t.pts, _after(c.pts, right, tol)])
                    c.members = sorted(set(c.members) | set(t.members))
                    c.notes.append(f"shared trunk (drawings {sorted(set(t.members))}) prepended at its end "
                                   f"({right[0]:.1f}, {right[1]:.1f}) pt")
                skipped.append(f"trunk path (drawings {sorted(set(t.members))}) is shared by {len(branches)} "
                               "branches: prepended to each of them, not kept as a separate curve")
                out = [c for c in out if c is not t]
                changed = True
                break
        if changed:
            continue
        for c in out:
            p = c.pts[0]
            for h in out:
                if h is c or len(h.pts) < 2:
                    continue
                d, k, q = _project(p, h.pts)
                at_start = float(np.hypot(*(q - h.pts[0]))) <= 1.0
                at_end = float(np.hypot(*(q - h.pts[-1]))) <= NODE_TOL
                if d > _cover_tol(h.width) or at_start or at_end:
                    continue
                prefix = np.vstack([h.pts[:k + 1], q[None, :]])
                c.pts = np.vstack([prefix, _after(c.pts, q, _cover_tol(h.width))])
                c.members = sorted(set(c.members) | set(h.members))
                c.notes.append(f"starts on curve drawn as drawings {sorted(set(h.members))} at "
                               f"({q[0]:.1f}, {q[1]:.1f}) pt; that curve's part to the left was prepended")
                changed = True
                break
            if changed:
                break
    return out


def classify_paths(geom: PageGeom, frame: tuple[float, float, float, float], labels: list[TLine],
                   skipped: list[str]) -> tuple[list[Sub], list[Sub]]:
    """Split stroked sub-paths into curve pieces and leaders; count the rest."""
    pieces: list[Sub] = []
    leaders: list[Sub] = []
    counts: dict[str, int] = defaultdict(int)
    for s in geom.subs:
        if len(s.pts) < 2:
            continue
        ins = _inside(s.pts, frame, 2.0)
        if not _inside(s.pts, frame, 45.0).any():
            continue
        if is_axis_aligned(s):
            if ins.all():
                counts["horizontal/vertical stroke (frame, grid line, tick mark, reference line or underline)"] += 1
            continue
        if s.straight and s.nseg <= 3 and labels:
            tail = min(min(ln.tail_dist(s.pts[0]), ln.tail_dist(s.pts[-1])) for ln in labels)
            if tail <= LEADER_TAIL_TOL:
                leaders.append(s)
                continue
        if not ins.all():
            if not ins.any():
                continue
            # keep the runs inside the frame; the parts outside are not on this plot
            runs, cur = [], []
            for q, inside in zip(s.pts, ins, strict=True):
                if inside:
                    cur.append(q)
                elif cur:
                    runs.append(cur)
                    cur = []
            if cur:
                runs.append(cur)
            kept = [Sub(np.array(r), s.width, s.dashed, s.didx, s.nseg, s.straight) for r in runs if len(r) >= 2]
            kept = [k for k in kept if k.length >= MIN_CURVE_LEN]
            skipped.append(f"stroked path (drawing {s.didx}, {s.length:.0f} pt) crosses the plot frame; clipped "
                           f"to the frame ({sum(k.length for k in kept):.0f} pt kept)")
            if s.dashed or not kept:
                continue
            pieces.extend(kept)
            continue
        if s.dashed:
            skipped.append(f"dashed stroke (drawing {s.didx}, {s.length:.0f} pt) not digitized")
            continue
        if s.length < MIN_CURVE_LEN:
            counts[f"stroked fragment shorter than {MIN_CURVE_LEN:g} pt"] += 1
            continue
        pieces.append(s)
    # kinked leaders: a straight stroke continuing a leader at its tip (the end away from the label)
    changed = True
    while changed and leaders:
        changed = False
        for ld in leaders:
            d0 = min(ln.tail_dist(ld.pts[0]) for ln in labels)
            d1 = min(ln.tail_dist(ld.pts[-1]) for ln in labels)
            tip = ld.pts[-1] if d0 <= d1 else ld.pts[0]
            for s in pieces:
                if not (s.straight and s.nseg <= 3 and abs(s.width - ld.width) <= 0.05):
                    continue
                for end, other in ((s.pts[0], s.pts[-1]), (s.pts[-1], s.pts[0])):
                    if float(np.hypot(*(end - tip))) <= NODE_TOL and float(np.hypot(*(other - tip))) > 1.0:
                        cont = s.pts if end is s.pts[0] else s.pts[::-1]
                        base = ld.pts if d0 <= d1 else ld.pts[::-1]
                        ld.pts = np.vstack([base, cont[1:]])
                        counts["leader continuation stroke (kinked leader) joined to its leader"] += 1
                        pieces = [q for q in pieces if q is not s]
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    # arrowheads drawn as open strokes: short straight strokes touching a leader end
    if leaders:
        lends = np.array([e for ld in leaders for e in (ld.pts[0], ld.pts[-1])])
        heads = [s for s in pieces if s.straight and s.nseg <= 2
                 and float(np.max(np.hypot(*np.diff(s.pts, axis=0).T))) < ARROW_LEN
                 and min(float(np.min(np.hypot(*(lends - q).T))) for q in s.pts) <= 2.0]
        if heads:
            counts[f"arrowhead stroke (<= 2 straight strokes < {ARROW_LEN:g} pt touching a leader)"] += len(heads)
            pieces = [s for s in pieces if not any(s is h for h in heads)]
    nfill = sum(1 for f in geom.filled if _inside(f, frame, 2.0).all())
    if nfill:
        counts["filled shape (dash fragment, arrowhead, marker or rule) - never read as a curve"] += nfill
    for k, v in sorted(counts.items()):
        skipped.append(f"{v} x {k}")
    return pieces, leaders


def label_candidates(lines: list[TLine], frame: tuple[float, float, float, float],
                     axes: list[Axis]) -> list[TLine]:
    x0, y0, x1, y1 = frame
    titles = {t for ax in axes for t in ax.title.split(" / ")}
    out = []
    for ln in lines:
        if not ln.horizontal or NUM_RE.match(ln.text) or ln.text in titles or CAPTION_RE.match(ln.text):
            continue
        if ANNOTATION_RE.match(ln.text):
            continue
        if x0 - 45 <= ln.cx <= x1 + 45 and y0 - 15 <= ln.cy <= y1 - 1:
            out.append(ln)
    return out


def _leader_tails(leaders: list[Sub], labels: list[TLine]) -> list[tuple[Sub, np.ndarray, np.ndarray, list[int]]]:
    """(leader, tail, tip, labels whose text or white box the tail touches) for each leader."""
    out = []
    for ld in leaders:
        ends = [ld.pts[0], ld.pts[-1]]
        dists = [[ln.tail_dist(e) for ln in labels] for e in ends]
        ti = 0 if min(dists[0]) <= min(dists[1]) else 1
        touching = [i for i, dd in enumerate(dists[ti]) if dd <= LEADER_TAIL_TOL]
        out.append((ld, ends[ti], ends[1 - ti], touching))
    return out


def _stack_assignment(tails: list[tuple[Sub, np.ndarray, np.ndarray, list[int]]], labels: list[TLine]
                      ) -> dict[int, int]:
    """Leader -> label for stacks of labels (same left edge, one leader each), by vertical order.

    Several leaders that start at a column of stacked labels (left edges within 2 pt) do not cross at
    their tails, so when the numbers of leaders and labels in the stack are equal the i-th tail from the
    top belongs to the i-th label from the top. Stacks where the counts differ are left to the
    nearest-centre-line rule.
    """
    result: dict[int, int] = {}
    cols = _cluster(list(labels), key=lambda t: t.x0, tol=2.0)
    for col in cols:
        if len(col) < 2:
            continue
        idx = [labels.index(t) for t in col]
        members = [k for k, (_, _, _, touch) in enumerate(tails) if touch and set(touch) <= set(idx)
                   and any(i in idx for i in touch)]
        if len(members) != len(idx):
            continue
        by_tail = sorted(members, key=lambda k: float(tails[k][1][1]))
        by_label = sorted(idx, key=lambda i: labels[i].cy)
        for k, i in zip(by_tail, by_label, strict=True):
            result[k] = i
    return result


def attach_labels(chains: list[Chain], leaders: list[Sub], labels: list[TLine], geom: PageGeom,
                  skipped: list[str]) -> None:
    """Attach label texts to curves (leaders, end-of-line text, adjacent text, sole label); see module doc."""
    dense = [densify(c.pts, 0.5) for c in chains]
    got: dict[int, set[str]] = defaultdict(set)
    how: dict[int, set[str]] = defaultdict(set)
    used_labels: set[int] = set()
    tails = _leader_tails(leaders, labels)
    stacked = _stack_assignment(tails, labels)
    # ---- 1. leaders
    for k, (ld, tail, tip, touching) in enumerate(tails):
        if not touching:
            continue
        if k in stacked:
            li = stacked[k]
            rule = "leader (label stack order)"
        else:
            near = sorted((labels[i].centerline_dist(tail), i) for i in touching)
            if len(near) > 1 and near[1][0] - near[0][0] < 0.5:
                skipped.append(f"leader (drawing {ld.didx}) starts between labels '{labels[near[0][1]].text}' "
                               f"and '{labels[near[1][1]].text}'; ambiguous, not attached")
                used_labels.update(i for _, i in near[:2])
                continue
            li = near[0][1]
            rule = "leader"
        lab = labels[li]
        used_labels.add(li)
        # arrowhead: a small filled shape touching the tip -> use its farthest vertex
        for f in geom.filled:
            if np.ptp(f[:, 0]) < 8 and np.ptp(f[:, 1]) < 8:
                dd = np.hypot(*(f - tip).T)
                if dd.min() <= 1.5:
                    tip = f[int(np.argmax(dd))]
                    break
        if not chains:
            continue
        d = sorted((seg_dist(tip, dc), j) for j, dc in enumerate(dense))
        if d[0][0] > LEADER_TIP_TOL:
            skipped.append(f"leader from label '{lab.text}' (drawing {ld.didx}) ends {d[0][0]:.1f} pt from the "
                           f"nearest curve (> {LEADER_TIP_TOL:g} pt); not attached")
            continue
        if len(d) > 1 and d[1][0] - d[0][0] < LEADER_MARGIN:
            skipped.append(f"leader from label '{lab.text}' (drawing {ld.didx}) ends between two curves "
                           f"({d[0][0]:.2f} vs {d[1][0]:.2f} pt); ambiguous, not attached")
            continue
        got[d[0][1]].add(lab.text)
        how[d[0][1]].add(rule)
    # ---- 2. end-of-line labels: text set just beyond a curve end, the end point inside the text's height
    ends_lr = [(c.pts[int(np.argmin(c.pts[:, 0]))], c.pts[int(np.argmax(c.pts[:, 0]))]) for c in chains]
    cand: dict[int, list[int]] = defaultdict(list)
    for li, lab in enumerate(labels):
        if li in used_labels:
            continue
        for k, (le, re_) in enumerate(ends_lr):
            if k in got:
                continue
            right_ok = lab.y0 - 1.5 <= re_[1] <= lab.y1 + 1.5 and 0.0 <= lab.x0 - re_[0] <= END_GAP
            left_ok = lab.y0 - 1.5 <= le[1] <= lab.y1 + 1.5 and 0.0 <= le[0] - lab.x1 <= END_GAP
            if right_ok or left_ok:
                cand[li].append(k)
    owners: dict[int, list[int]] = defaultdict(list)
    for li, ks in cand.items():
        if len(ks) == 1:
            owners[ks[0]].append(li)
    for k, lis in owners.items():
        if len(lis) == 1:
            got[k].add(labels[lis[0]].text)
            how[k].add("text at curve end")
            used_labels.add(lis[0])
    # ---- 3. adjacent text (no leader): nearest curve, clearly nearer than the second
    for li, lab in enumerate(labels):
        if li in used_labels or not chains:
            continue
        d = sorted((box_dist(lab, dc), k) for k, dc in enumerate(dense))
        if d[0][0] > ADJ_TOL:
            continue                                     # not next to a curve: free text
        if len(d) > 1 and d[1][0] < ADJ_RATIO * d[0][0] + 2.0:
            skipped.append(f"label '{lab.text}' is {d[0][0]:.1f} pt from one curve and {d[1][0]:.1f} pt from "
                           "another; ambiguous, not attached")
            used_labels.add(li)
            continue
        got[d[0][1]].add(lab.text)
        how[d[0][1]].add("adjacent text")
        used_labels.add(li)
    # ---- 4. one curve and one label left in the plot
    if len(chains) == 1 and not got and len(labels) == 1:
        got[0].add(labels[0].text)
        how[0].add("only label and only curve in the plot")
    for k, c in enumerate(chains):
        names = got.get(k, set())
        if len(names) == 1:
            c.label = next(iter(names))
            c.label_how = "+".join(sorted(how[k]))
        elif len(names) > 1:
            skipped.append(f"a curve received several labels {sorted(names)}; ambiguous, left unlabeled")


# --------------------------------------------------------------------------- resampling


def rdp(pts: np.ndarray, eps: float) -> np.ndarray:
    """Ramer-Douglas-Peucker simplification; returns indices of kept vertices (always both ends)."""
    keep = np.zeros(len(pts), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        ab = b - a
        L = float(np.hypot(*ab))
        seg = pts[i + 1:j]
        if L == 0:
            d = np.hypot(*(seg - a).T)
        else:
            d = np.abs(ab[0] * (seg[:, 1] - a[1]) - ab[1] * (seg[:, 0] - a[0])) / L
        k = int(np.argmax(d))
        if d[k] > eps:
            m = i + 1 + k
            keep[m] = True
            stack += [(i, m), (m, j)]
    return np.flatnonzero(keep)


def max_dev(src: np.ndarray, simp: np.ndarray) -> float:
    """Max distance (pt) from the source polyline's points to the simplified polyline."""
    sd = densify(src, 0.25)
    return max(seg_dist(p, simp) for p in sd[:: max(len(sd) // 400, 1)])


def resample(pts: np.ndarray) -> tuple[np.ndarray, float]:
    """Keep <= MAX_POINTS source vertices with the smallest RDP tolerance; pad to MIN_POINTS."""
    if len(pts) <= MAX_POINTS:
        idx = np.arange(len(pts))
    else:
        lo, hi = 0.0, 5.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if len(rdp(pts, mid)) > MAX_POINTS:
                lo = mid
            else:
                hi = mid
        idx = rdp(pts, hi)
    out = pts[idx]
    if len(out) < MIN_POINTS:
        # add points uniformly in arc length (on the polyline, so the shape is unchanged)
        s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
        extra_s = np.linspace(0.0, s[-1], MIN_POINTS - len(out) + 2)[1:-1]
        ex = np.column_stack([np.interp(extra_s, s, pts[:, 0]), np.interp(extra_s, s, pts[:, 1])])
        allp = np.vstack([out, ex])
        s_all = np.concatenate([s[idx], extra_s])
        out = allp[np.argsort(s_all, kind="stable")]
    return out, max_dev(pts, out)


def _monotone_resample(pts: np.ndarray, axis: int) -> tuple[np.ndarray, float, int]:
    """Keep the vertices that advance strictly along page ``axis`` (0 = x, 1 = y), then resample.

    Returns (points, max deviation from the source polyline in pt, number of vertices left out).
    """
    mono = [0]
    for i in range(1, len(pts)):
        if pts[i][axis] > pts[mono[-1]][axis] + 0.01:
            mono.append(i)
    if mono[-1] != len(pts) - 1 and len(mono) > 1 and pts[-1][axis] > pts[mono[-2]][axis] + 0.01:
        mono[-1] = len(pts) - 1
    out, _ = resample(pts[mono])
    return out, max_dev(pts, out), len(pts) - len(mono)


def is_function_of_x(pts: np.ndarray, width: float) -> bool:
    """True if the curve is single-valued in x.

    Allowed: backward x steps up to max(BACKSTEP_TOL, half the stroke width) (overlapping joins), and
    longer backward runs that retrace the already drawn line within half the stroke width (pen retrace).
    Not allowed: any other backward run, or a constant-x run longer than 1 pt (a vertical part).
    """
    tol = max(BACKSTEP_TOL, 0.5 * width)
    xmax = float(pts[0][0])
    imax = 0
    for i in range(1, len(pts)):
        x = float(pts[i][0])
        if x >= xmax:
            xmax, imax = x, i
        elif x < xmax - tol and seg_dist(pts[i], pts[:imax + 1]) > _cover_tol(width):
            return False
    d = np.diff(pts, axis=0)
    run = 0.0
    for dx, dy in d:
        run = run + abs(dy) if abs(dx) <= 0.02 else 0.0
        if run > 1.0:
            return False
    return True


# --------------------------------------------------------------------------- figure


@dataclass
class CurveOut:
    label: str
    label_how: str
    kind: str
    x_axis: str
    y_axis: str
    x_title: str
    y_title: str
    x_unit: str
    y_unit: str
    function_of_x: bool
    function_of_y: bool
    source_vertices: int
    resample_err_pt: float
    x: np.ndarray
    y: np.ndarray
    pts: np.ndarray            # page points of the written vertices (for overlays)
    notes: list[str]


@dataclass
class FigureOut:
    entry: FigureEntry
    status: str
    kind: str
    caption_found: bool
    printed_page_found: str
    frame: tuple[float, float, float, float] | None
    region: tuple[float, float]
    axes: list[Axis]
    curves: list[CurveOut]
    skipped: list[str]
    annotations: list[str]


def figure_kind(caption: str) -> str:
    c = caption.lower()
    if "physical properties" in c:
        return "physical-properties"
    if "effect of temperature" in c or "effect of exposure" in c:
        return "effect-of-temperature"
    if "stress-strain" in c:
        return "stress-strain"
    if "tangent-modulus" in c or "tangent modulus" in c:
        return "tangent-modulus"
    return "other"


def _nows(s: str) -> str:
    return re.sub(r"\s+", "", s)


def _pick_title(ax: Axis, kind: str) -> str:
    parts = [p for p in ax.title.split(" / ") if p]
    if not parts:
        return ""
    if kind == "tangent-modulus":
        hit = [p for p in parts if "tangent" in p.lower()]
    elif kind == "stress-strain":
        hit = [p for p in parts if "strain" in p.lower()]
    else:
        hit = parts
    return hit[0] if hit else ""


def process_figure(doc: fitz.Document, entry: FigureEntry, cache: dict[int, tuple]) -> FigureOut:
    pno = entry.pdf_page
    if pno not in cache:
        page = doc[pno - 1]
        zoom = 2.0
        cache[pno] = (page, page_text_lines(page, render_without_text(page, zoom), zoom), page_geometry(page),
                      caption_blocks(page),
                      _nows(page.get_text("text")))
    page, lines, geom, caps, page_text = cache[pno]
    skipped: list[str] = []
    kind = figure_kind(entry.caption)
    caption_found = _nows(entry.caption) in page_text
    pp = printed_page(lines)
    idx = [k for k, c in enumerate(caps) if c[0] == entry.figure]
    if len(idx) != 1:
        return FigureOut(entry, "skipped", kind, caption_found, pp, None, (0, 0), [], [],
                         [f"caption 'Figure {entry.figure}.' found {len(idx)} times on the page; region unknown"], [])
    k = idx[0]
    top = caps[k - 1][2] + 1.0 if k > 0 else 50.0
    bottom = caps[k][1] - 1.0
    region = (top, bottom)
    images = [b for b in page.get_text("dict")["blocks"] if b["type"] == 1
              and b["bbox"][1] < bottom and b["bbox"][3] > top
              and (min(b["bbox"][3], bottom) - max(b["bbox"][1], top)) > 0.5 * (bottom - top)]
    frame = find_frame(geom, top, bottom)
    if frame is None:
        why = ("the figure is a raster image (no vector paths to read)" if images
               else "no plot frame found among the vector paths")
        return FigureOut(entry, "skipped", kind, caption_found, pp, None, region, [], [], [why], [])
    axes = find_axes(lines, geom, frame, top, bottom, skipped)
    xs = [a for a in axes if a.name.startswith("x")]
    ys = [a for a in axes if a.name.startswith("y")]
    if not xs or not ys:
        why = "no numeric tick labels on " + ("x" if not xs else "y") + " axis"
        if images:
            why += "; the plot is a raster image"
        return FigureOut(entry, "skipped", kind, caption_found, pp, frame, region, axes, [], [why], [])
    labels = label_candidates(lines, frame, axes)
    for ln in labels:
        fits = [b for b in geom.white_boxes if b[0] <= ln.cx <= b[2] and b[1] <= ln.cy <= b[3]
                and (b[3] - b[1]) <= 3.0 * (ln.y1 - ln.y0) + 4.0 and (b[2] - b[0]) <= (ln.x1 - ln.x0) + 60.0]
        if fits:
            ln.box = min(fits, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    annotations = [ln.text for ln in lines if ln.horizontal and ANNOTATION_RE.match(ln.text)
                   and frame[0] - 5 <= ln.cx <= frame[2] + 5 and frame[1] - 5 <= ln.cy <= frame[3] + 5]
    pieces, leaders = classify_paths(geom, frame, labels, skipped)
    chains = chain_pieces(pieces, skipped)
    attach_labels(chains, leaders, labels, geom, skipped)
    curves: list[CurveOut] = []
    names: dict[str, int] = defaultdict(int)
    for c in chains:
        # curve kind on stress-strain / tangent-modulus figures
        ck = "curve"
        if kind in ("stress-strain", "tangent-modulus"):
            left, right = (c.pts[0], c.pts[-1]) if c.pts[0][0] <= c.pts[-1][0] else (c.pts[-1], c.pts[0])
            falls = right[1] > left[1]                      # page y grows downwards: stress falls
            ck = "tangent-modulus" if (kind == "tangent-modulus" or falls) else "stress-strain"
        # x axis
        if len(xs) == 1:
            ax = xs[0]
        else:
            want = "tangent" if ck == "tangent-modulus" else "strain"
            hit = [a for a in xs if want in a.title.lower()]
            if len(hit) != 1:
                skipped.append(f"curve '{c.label or 'unlabeled'}' (drawings {sorted(set(c.members))}): "
                               f"{len(xs)} x axes and none uniquely titled '{want}'; not digitized")
                continue
            ax = hit[0]
        # y axis
        if len(ys) == 1:
            ay = ys[0]
        else:
            sym = c.label.split(",")[0].strip() if c.label and "," in c.label else None
            hit = [a for a in ys if sym and a.title.split(",")[0].strip() == sym]
            if len(hit) != 1:
                skipped.append(f"curve '{c.label or 'unlabeled'}' (drawings {sorted(set(c.members))}): "
                               f"{len(ys)} y axes and the label does not name one of them; not digitized")
                continue
            ay = hit[0]
        x_title = _pick_title(ax, ck) if ck != "curve" else ax.title.split(" / ")[0]
        if not x_title:
            skipped.append(f"curve '{c.label}': x-axis title for a {ck} curve not found; not digitized")
            continue
        y_title = ay.title.split(" / ")[0]
        pts = c.pts
        if ax.to_data(pts[-1:, 0])[0] < ax.to_data(pts[:1, 0])[0]:
            pts = pts[::-1]
        keep = np.ones(len(pts), bool)
        keep[1:] = np.hypot(*np.diff(pts, axis=0).T) > 0.02
        pts = pts[keep]
        function = is_function_of_x(pts, c.width)
        # single-valued in y (stress), e.g. tangent-modulus curves with their vertical part at Et = E
        page_y_up = pts[-1][1] >= pts[0][1]
        swapped = pts[:, ::-1] if page_y_up else pts[::-1, ::-1]
        function_y = (not function) and is_function_of_x(swapped, c.width)
        if function:
            out_pts, err, dropped = _monotone_resample(pts, 0)
        elif function_y:
            out_pts, err, dropped = _monotone_resample(pts if page_y_up else pts[::-1], 1)
            if not page_y_up:
                out_pts = out_pts[::-1]
        else:
            out_pts, err, dropped = pts, 0.0, 0
        if dropped:
            c.notes.append(f"{dropped} source vertices that step back along the "
                           f"{'x' if function else 'y'} direction (pen retrace / joins) left out")
        x = ax.to_data(out_pts[:, 0])
        y = ay.to_data(out_pts[:, 1])
        if c.label:
            base = c.label + (" (tangent modulus)" if ck == "tangent-modulus" and kind == "stress-strain" else "")
        else:
            base = "unlabeled"
            skipped.append(f"curve from drawings {sorted(set(c.members))}: no label could be attached "
                           "(kept as 'unlabeled')")
        names[base] += 1
        curves.append(CurveOut(base, c.label_how or "none", ck, ax.name, ay.name, x_title, y_title,
                               split_title(x_title)[1], split_title(y_title)[1], function, function_y, len(pts), err,
                               x, y, out_pts, list(c.notes)))
    # a label attached to several curves of the same kind cannot tell them apart: drop it (ambiguous)
    dup = {n for n, k in names.items() if k > 1 and n != "unlabeled"}
    for n in sorted(dup):
        skipped.append(f"label '{n}' reached {names[n]} curves of the same kind; ambiguous, those curves are "
                       "left unlabeled")
    for cv in curves:
        if cv.label in dup:
            cv.notes.append(f"label '{cv.label}' also reached another curve; dropped as ambiguous")
            cv.label, cv.label_how = "unlabeled", "none"
    n_unl = sum(cv.label == "unlabeled" for cv in curves)
    if n_unl > 1:
        k = 0
        for cv in sorted(curves, key=lambda c: float(c.x[0])):
            if cv.label == "unlabeled":
                k += 1
                cv.label = f"unlabeled #{k}"
    status = "digitized" if curves else "skipped"
    if not curves:
        skipped.append("no curve could be digitized")
    return FigureOut(entry, status, kind, caption_found, pp, frame, region, axes, curves, skipped, annotations)


# --------------------------------------------------------------------------- output


def _decimals(span: float) -> int:
    return max(0, int(math.ceil(-math.log10(max(span, 1e-12) * 1e-4))))


def _fmt(v: float, dec: int) -> str:
    s = f"{v:.{dec}f}"
    return "0" + s[s.index("."):] if s.startswith("-0.") and float(s) == 0 else s


def write_markdown(fo: FigureOut) -> str:
    e = fo.entry
    L: list[str] = []
    L.append(f"# Digitized curves: Figure {e.figure}")
    L.append("")
    L.append(f"Generated by `{GENERATOR}` from the vector paths of MIL-HDBK-5J ({SOURCE_REL}); do not edit.")
    L.append("Typical curves read from a handbook figure: not design allowables.")
    L.append("")
    L.append("## Figure")
    L.append("")
    L.append(f"- figure: {e.figure}")
    L.append(f"- caption: {e.caption}")
    L.append(f"- pdf_page: {e.pdf_page}")
    L.append(f"- printed_page: {e.printed_page}")
    L.append(f"- materials: {', '.join(e.materials)}")
    L.append(f"- page_png: ../figures/{e.file}")
    L.append(f"- kind: {fo.kind}")
    L.append(f"- status: {fo.status}")
    L.append("- method: PyMuPDF get_drawings() vector paths + get_text('dict') tick labels; least-squares "
             "pixel-to-data map per axis; see the generator docstring")
    if fo.frame:
        L.append("- frame_pt: " + ", ".join(f"{v:.2f}" for v in fo.frame))
    L.append("- annotations: " + (" | ".join(a.replace("|", "/") for a in fo.annotations) or "none"))
    L.append("")
    L.append("## Axes")
    L.append("")
    L.append("| axis | side | title | unit | scale | ticks | snapped | a | b | rms residual (% span) "
             "| max residual (% span) | tick values |")
    L.append("|:---|:---|:---|:---|:---|---:|---:|---:|---:|---:|---:|:---|")
    for a in fo.axes:
        tv = "; ".join(f"{t[1]:g}" for t in sorted(a.ticks, key=lambda t: t[1]))
        L.append(f"| {a.name} | {a.side} | {a.title or '—'} | {a.unit or '—'} | {a.scale} | {len(a.ticks)} | "
                 f"{sum(1 for t in a.ticks if t[2])} | {a.a:.8g} | {a.b:.8g} | {a.rms_pct:.4f} | {a.max_pct:.4f} | "
                 f"{tv} |")
    L.append("")
    L.append("## Skipped elements")
    L.append("")
    for s in fo.skipped or ["none"]:
        L.append(f"- {s}")
    for c in fo.curves:
        ax = next(a for a in fo.axes if a.name == c.x_axis)
        ay = next(a for a in fo.axes if a.name == c.y_axis)
        dx = _decimals(float(np.ptp([t[1] for t in ax.ticks])))
        dy = _decimals(float(np.ptp([t[1] for t in ay.ticks])))
        L.append("")
        L.append(f"## Curve: {c.label}")
        L.append("")
        L.append(f"- label_source: {c.label_how}")
        L.append(f"- kind: {c.kind}")
        L.append(f"- x_axis: {c.x_axis}")
        L.append(f"- y_axis: {c.y_axis}")
        L.append(f"- x_title: {c.x_title}")
        L.append(f"- y_title: {c.y_title}")
        L.append(f"- function_of_x: {'yes' if c.function_of_x else 'no'}")
        L.append(f"- function_of_y: {'yes' if c.function_of_y else 'no'}")
        L.append(f"- source_vertices: {c.source_vertices}")
        L.append(f"- points: {len(c.x)}")
        L.append(f"- resampling_max_error_pt: {c.resample_err_pt:.3f}")
        L.append("- notes: " + ("; ".join(c.notes) or "none"))
        L.append("")
        L.append(f"| x ({c.x_unit or '-'}) | y ({c.y_unit or '-'}) |")
        L.append("|---:|---:|")
        for xv, yv in zip(c.x, c.y, strict=True):
            L.append(f"| {_fmt(float(xv), dx)} | {_fmt(float(yv), dy)} |")
    L.append("")
    return "\n".join(L)


def write_index(results: list[FigureOut]) -> str:
    L = ["# Digitized MIL-HDBK-5J figure curves", "",
         f"Generated by `{GENERATOR}`; one file per figure in `figures/index.md`. Read them with",
         "`aerokit.materials.curves`. Typical curves: not design allowables.", "",
         "| figure | file | pdf page | printed page | kind | status | curves | materials |",
         "|:---|:---|---:|:---|:---|:---|---:|:---|"]
    for fo in results:
        e = fo.entry
        slug = figure_slug(e.figure)
        L.append(f"| {e.figure} | [{slug}.md]({slug}.md) | {e.pdf_page} | {e.printed_page} | {fo.kind} | "
                 f"{fo.status} | {len(fo.curves)} | {', '.join(e.materials)} |")
    L.append("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--index", type=Path, default=Path("src/aerokit/materials/data/figures/index.md"))
    ap.add_argument("--out", type=Path, default=Path("src/aerokit/materials/data/curves"))
    ap.add_argument("--only", default=None, help="comma-separated figure ids (debugging)")
    ap.add_argument("--json", type=Path, default=None, help="also dump overlay geometry as JSON")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    entries = read_index(args.index)
    if args.only:
        want = set(args.only.split(","))
        entries = [e for e in entries if e.figure in want]
    doc = fitz.open(args.pdf)
    cache: dict[int, tuple] = {}
    results = [process_figure(doc, e, cache) for e in entries]
    args.out.mkdir(parents=True, exist_ok=True)
    for fo in results:
        (args.out / f"{figure_slug(fo.entry.figure)}.md").write_text(write_markdown(fo), encoding="utf-8")
    if not args.only:
        (args.out / "index.md").write_text(write_index(results), encoding="utf-8")
    if args.json:
        import json
        dump = {fo.entry.figure: {
            "page": fo.entry.pdf_page, "frame": fo.frame, "region": fo.region,
            "curves": [{"label": c.label, "pts": c.pts.tolist()} for c in fo.curves],
            "axes": [{"name": a.name, "ticks": a.ticks, "a": a.a, "b": a.b, "scale": a.scale} for a in fo.axes],
        } for fo in results}
        args.json.write_text(json.dumps(dump), encoding="utf-8")
    n_curves = sum(len(fo.curves) for fo in results)
    n_pts = sum(len(c.x) for fo in results for c in fo.curves)
    print(f"figures: {len(results)}  digitized: {sum(fo.status == 'digitized' for fo in results)}  "
          f"curves: {n_curves}  points: {n_pts}")
    for fo in results:
        worst = max((a.max_pct for a in fo.axes), default=float("nan"))
        print(f"  {fo.entry.figure:14s} {fo.status:9s} curves={len(fo.curves):2d} "
              f"axes={','.join(a.name for a in fo.axes) or '-':12s} max_resid={worst:.3f}%  "
              f"labels={[c.label for c in fo.curves]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
