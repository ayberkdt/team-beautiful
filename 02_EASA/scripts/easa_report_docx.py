"""Fill the organisers' Word template with the EASA report draft (kit piece 03) → 02_EASA/submission/.

    python -I 02_EASA/scripts/easa_report_docx.py            # docx + Word: update the table of contents, export PDF
    python -I 02_EASA/scripts/easa_report_docx.py --no-word  # docx only (TOC keeps the template's placeholder lines)

Source text: ``02_EASA/kit/03_report_draft.md`` (sections "## 1." … "## References"). Template:
``00_Common/rules_and_templates/originals_2026-11-05/Ideathon_Template_2026.docx`` (cover, TOC, numbered Heading1,
Montserrat body). Figures (``FIGURES``): 1 = F1a + F1b, 2 = F8 (response time), 3 = F7 (compliance sweep), all from
``outputs/figures``. Tables 5 and 6 are generated from ``outputs/tradeoffs/tradeoffs.json`` (``{{table:cues}}``,
``{{table:sensors}}``, copies in ``outputs/report_tables``). Citations ``[@key]`` become blue [n] links to a numbered
reference list built from the ``- @key:`` lines of the draft. The docx is regenerated from the draft every time: edit the draft, not the docx
(or stop running this script once the team starts editing in Word).

python-docx is not installed on this laptop, so the script edits the template's XML with the standard library. Word
(COM, via PowerShell) updates the TOC and exports the PDF; the page count is printed for the 5-page rule (cover and TOC
before the body, references after it, as in the Ansys report).
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EASA = ROOT / "02_EASA"
DRAFT = EASA / "kit" / "03_report_draft.md"
TEMPLATE = ROOT / "00_Common" / "rules_and_templates" / "originals_2026-11-05" / "Ideathon_Template_2026.docx"
OUT_DIR = EASA / "submission"
OUT = OUT_DIR / "Team_Beetiful_EASA_Report.docx"
PDF = OUT.with_suffix(".pdf")

TITLE = "LOCK-SENSE"
SUBTITLE = ["A retrofit canopy-lock alert for the Extra NG",
            "Team Beetiful · EUROAVIA Ideathon 2026 · EASA challenge"]

O = EASA / "outputs"
F = O / "figures"  # sunumatik redraws by the "EASA görevi hazırlığı" session; older PNGs are the fallback
FIGURES = {  # figure number → ([(preferred, fallback), ...], width of each image in mm)
    1: ([(F / "F1a.png", O / "day" / "C5_lock_related_by_phase.png"),
         (F / "F1b.png", O / "day" / "C6_lock_related_by_type.png")], 72),
    2: ([(F / "F10.png", None)], 176),
    3: ([(F / "P1_phase_logic.png", None)], 176),
    4: ([(F / "F8.png", None)], 160),
    5: ([(F / "P2_compliance.png", F / "F7.png")], 122),
}


def pick(pref: Path, fallback: Path | None) -> Path:
    if pref.exists():
        return pref
    if fallback is not None and fallback.exists():
        print(f"  figure fallback: {pref.name} missing, using {fallback.relative_to(ROOT).as_posix()}")
        return fallback
    raise FileNotFoundError(f"{pref} (no fallback)")


TEXT_W = 11906 - 2 * 964  # dxa: A4 width minus the template's 17 mm side margins
FONT = '<w:rFonts w:ascii="Montserrat" w:hAnsi="Montserrat"/>'
HFONT = '<w:rFonts w:ascii="Montserrat Medium" w:hAnsi="Montserrat Medium"/>'
EMU_PER_MM = 36000

R_IMG = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
R_LINK = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
BULLET_NUM_ID = 90
CITE_COLOR = "1F5FBF"  # blue for [n] citations and reference URLs
FLOAT = True  # figures float to the top of their page


# ---------------------------------------------------------------- inline markdown → runs
def clean(t: str) -> str:
    """Draft conventions → report text: kit pointers dropped, [source] → (source), code ticks removed."""
    t = re.sub(r"\s*\(kit `\d+`\)", "", t)
    t = re.sub(r"\s*\(kit `\d+`;\s*", " (", t)
    t = re.sub(r",?\s*kit `\d+`", "", t)
    t = re.sub(r"\[([^\]]+)\]", r"(\1)", t)
    t = t.replace("`", "")
    return re.sub(r"[ \t]+", " ", t).strip()


def cite_runs(tok: str, size: int | None) -> str:
    """⟦3:App. A;5:⟧ → blue "[3, App. A, 5]" with each number linked to its reference bookmark."""
    rpr = FONT + f'<w:color w:val="{CITE_COLOR}"/>' + \
        (f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "") + '<w:lang w:val="en-GB"/>'

    def r(txt: str) -> str:
        return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{html.escape(txt, quote=False)}</w:t></w:r>'

    out = [r("[")]
    for k, item in enumerate(tok.split(";")):
        n, loc = item.split(":", 1)
        if k:
            out.append(r(", "))
        out.append(f'<w:hyperlink w:anchor="ref_{n}" w:history="1">{r(n)}</w:hyperlink>')
        if loc:
            out.append(r(", " + loc))
    out.append(r("]"))
    return "".join(out)


def runs(t: str, size: int | None = None, bold_all: bool = False, italic_all: bool = False) -> str:
    out = []
    for part in re.split(r"(⟦[^⟧]+⟧|\*\*[^*]+\*\*|\*[^*]+\*)", t):
        if not part:
            continue
        if part.startswith("⟦"):
            out.append(cite_runs(part[1:-1], size))
            continue
        b = bold_all or part.startswith("**")
        i = italic_all or (part.startswith("*") and not part.startswith("**"))
        txt = part.strip("*") if part.startswith("*") else part
        rpr = FONT + ("<w:b/>" if b else "") + ("<w:i/>" if i else "") + \
            (f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "") + '<w:lang w:val="en-GB"/>'
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{html.escape(txt, quote=False)}</w:t></w:r>')
    return "".join(out)


def para(t: str, *, size: int | None = None, jc: str = "both", after: int | None = None, before: int | None = None,
         keep_next: bool = False, bold: bool = False, italic: bool = False, ind: str = "", num: bool = False) -> str:
    sp = ""
    if after is not None or before is not None:
        sp = "<w:spacing" + (f' w:before="{before}"' if before is not None else "") + \
             (f' w:after="{after}"' if after is not None else "") + "/>"
    ppr = ("<w:keepNext/>" if keep_next else "") + \
          (f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{BULLET_NUM_ID}"/></w:numPr>' if num else "") + \
          sp + ind + f'<w:jc w:val="{jc}"/>'
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs(t, size, bold, italic)}</w:p>"


def heading(t: str, new_page: bool = False, level: int = 1) -> str:
    pb = "<w:pageBreakBefore/>" if new_page else ""
    sp = '<w:spacing w:before="160" w:after="80"/>' if level == 2 else ""
    return (f'<w:p><w:pPr><w:pStyle w:val="Heading{level}"/>{pb}{sp}<w:rPr>{HFONT}</w:rPr></w:pPr>'
            f'<w:r><w:rPr>{HFONT}</w:rPr><w:t xml:space="preserve">{html.escape(t, quote=False)}</w:t></w:r></w:p>')


PAGE_BREAK = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# ---------------------------------------------------------------- figures and table
class Media:
    def __init__(self):
        self.files: list[tuple[str, bytes]] = []
        self.rels: list[tuple[str, str]] = []
        self.links: list[tuple[str, str]] = []

    def link(self, url: str) -> str:
        rid = f"rIdLnk{len(self.links) + 1}"
        self.links.append((rid, url))
        return rid

    def add(self, png: Path) -> str:
        k = len(self.files) + 1
        name, rid = f"report_fig{k}.png", f"rIdRep{k}"
        self.files.append((name, png.read_bytes()))
        self.rels.append((rid, f"media/{name}"))
        return rid


def png_size(p: Path) -> tuple[int, int]:
    b = p.read_bytes()[16:24]
    return int.from_bytes(b[:4], "big"), int.from_bytes(b[4:], "big")


def image_run(rid: str, png: Path, width_mm: float, pid: int) -> str:
    w, h = png_size(png)
    cx = int(width_mm * EMU_PER_MM)
    cy = int(cx * h / w)
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{pid}" name="Figure {pid}" descr="{html.escape(png.stem)}"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{pid}" name="{png.name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
            '</wp:inline></w:drawing></w:r>')


NO_FLOAT = {2, 3, 5}  # the phase diagram sits inline below Table 1: as a float its caption split from the image
FLOAT_BOTTOM = {1}  # Figure 1 sits at the foot of page 3, below §1–§2, not above the first heading


def figure(n: int, caption: str, media: Media) -> str:
    pairs, w = FIGURES[n]
    imgs = [pick(a, b) for a, b in pairs]
    body = "".join(image_run(media.add(p), p, w, 500 + 10 * n + i) for i, p in enumerate(imgs))
    pic = f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="0" w:after="40"/><w:jc w:val="center"/></w:pPr>{body}</w:p>'
    cap = para(f"**Figure {n}.** {caption}", size=18, jc="left", after=0)
    if not FLOAT or n in NO_FLOAT:
        return pic + cap
    # floating one-cell table at the top of the page where the next paragraph falls (LaTeX [t]): text fills the
    # space a too-tall inline figure would leave empty; tblOverlap=never stacks two floats on one page
    return (f'<w:tbl><w:tblPr><w:tblpPr w:leftFromText="0" w:rightFromText="0" w:topFromText="{240 if n in FLOAT_BOTTOM else 0}" w:bottomFromText="{0 if n in FLOAT_BOTTOM else 240}" '
            f'w:vertAnchor="margin" w:horzAnchor="margin" w:tblpXSpec="center" w:tblpYSpec="{'bottom' if n in FLOAT_BOTTOM else 'top'}"/>'
            f'<w:tblOverlap w:val="never"/><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
            f'<w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{TEXT_W}"/></w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>'
            f'<w:tc><w:tcPr><w:tcW w:w="{TEXT_W}" w:type="dxa"/></w:tcPr>{pic}{cap}</w:tc></w:tr></w:tbl>')


def table(rows: list[list[str]]) -> str:
    by_header = {"Element": [1350, 2300, 6328], "Phase": [1600, 4100, 4278],
                 "Study and setting": [2600, 1900, 3000, 2478], "No.": [500, 5600, 3878],
                 "Cue set": [5378, 2300, 2300], "Sensor": [3378, 1500, 1700, 1700, 1700]}
    head = rows[0][0].split(" (")[0]
    widths = by_header.get(head) or [TEXT_W // len(rows[0])] * (len(rows[0]) - 1) + \
        [TEXT_W - (TEXT_W // len(rows[0])) * (len(rows[0]) - 1)]
    assert sum(widths) == TEXT_W, (head, sum(widths))
    num_re = re.compile(r"^(\*\*)?[\d .,×]+(\*\*)?$")
    numeric = [all(num_re.match(r[j]) for r in rows[1:] if r[j]) for j in range(len(rows[0]))]
    thick, thin = 'w:sz="12"', 'w:sz="4"'

    def cell(t: str, w: int, header: bool, top: bool, bottom: bool, mid: bool, keep: bool = False,
             jc: str = "left") -> str:
        b = ""
        if top:
            b += f'<w:top w:val="single" {thick} w:space="0" w:color="000000"/>'
        if mid:
            b += f'<w:bottom w:val="single" {thin} w:space="0" w:color="000000"/>'
        elif bottom:
            b += f'<w:bottom w:val="single" {thick} w:space="0" w:color="000000"/>'
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/><w:tcBorders>{b}</w:tcBorders></w:tcPr>'
                f'<w:p><w:pPr>{"<w:keepNext/>" if header or keep else ""}<w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/><w:jc w:val="{jc}"/></w:pPr>'
                + f'</w:p><w:p><w:pPr><w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/><w:jc w:val="{jc}"/></w:pPr>'.join(
                    runs(clean(x), 15, bold_all=header) for x in t.split("<br>")) + '</w:p></w:tc>')

    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    out = [f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
           '<w:tblCellMar><w:left w:w="57" w:type="dxa"/><w:right w:w="57" w:type="dxa"/></w:tblCellMar>'
           f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>']
    for k, r in enumerate(rows):
        hdr = k == 0
        trpr = "<w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if hdr else "") + "</w:trPr>"
        # short tables stay in one piece; long ones may break, but never leave the last row alone
        if head == "No.":  # the steps table may break only between mounting (1 to 4) and wiring (5 on)
            keep = k == 0 or k == len(rows) - 2
        else:
            keep = k < len(rows) - 1 if len(rows) <= 8 else k == len(rows) - 2
        out.append("<w:tr>" + trpr + "".join(cell(t, w, hdr, hdr, k == len(rows) - 1, hdr, keep,
                                                 "right" if numeric[j] else "left")
                                            for j, (t, w) in enumerate(zip(r, widths))) + "</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


# ---------------------------------------------------------------- draft → body XML
def parse_refs(refs: str) -> dict[str, str]:
    out, cur = {}, None
    for ln in refs.splitlines():
        m = re.match(r"^- @(\w+):\s*(.*)$", ln)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2).strip()
        elif cur and ln.startswith("  ") and ln.strip():
            out[cur] += " " + ln.strip()
    return out


def number_citations(main: str, refs: dict[str, str]) -> tuple[str, list[str]]:
    """[@a, p. 9; @b] → ⟦1:p. 9;2:⟧, numbered in order of first use."""
    order: list[str] = []

    def one(m: re.Match) -> str:
        items = []
        for it in m.group(1).split(";"):
            it = it.strip()
            mm = re.match(r"@(\w+)(?:,\s*(.+))?$", it)
            if not mm:
                raise ValueError(f"bad citation item {it!r}")
            key = mm.group(1)
            if key not in refs:
                raise KeyError(f"citation @{key} has no '- @{key}:' line under References")
            if key not in order:
                order.append(key)
            items.append(f"{order.index(key) + 1}:{mm.group(2) or ''}")
        return "⟦" + ";".join(items) + "⟧"

    return re.sub(r"\[(@[^\]]+)\]", one, main), order


def body_xml(md: str, media: Media) -> tuple[str, list[str], str]:
    body = md.split("## Title:")[1]
    main, refs = body.split("## References", 1)
    main = main[main.index("## 1."):]
    main = main.replace("{{table:cues}}", gen_table("cues")).replace("{{table:sensors}}", gen_table("sensors"))
    ref_map = parse_refs(refs)
    main, order = number_citations(main, ref_map)
    unused = [k for k in ref_map if k not in order]
    print(f"citations: {len(order)} references cited" + (f"; not cited, dropped: {', '.join(unused)}" if unused else ""))
    out, headings = [], []
    blocks = re.split(r"\n\s*\n", main.strip())
    pending_table_caption = None
    for blk in blocks:
        b = blk.strip()
        if b.startswith("### "):
            out.append(heading(b[4:].splitlines()[0].strip(), level=2))
            continue
        if b.startswith("## "):
            h = re.sub(r"^##\s+\d+\.\s*", "", b.splitlines()[0])
            h = re.sub(r"\s*\*\(R\d.*\)\*\s*$", "", h).strip()
            headings.append(h)
            out.append(heading(h))
            continue
        m = re.match(r"\*Figure (\d) caption:\*\s*\"(.+)\"\s*$", " ".join(b.split()), re.S)
        if m:
            out.append(figure(int(m.group(1)), clean(m.group(2)), media))
            continue
        m = re.match(r"\*Table (\d) \(title above the table\):\*\s*\"(.+)\"\s*$", " ".join(b.split()), re.S)
        if m:
            pending_table_caption = (m.group(1), clean(m.group(2)))
            continue
        if b.startswith("|"):
            lines = [ln for ln in b.splitlines() if ln.strip().startswith("|") and not re.match(r"^\|[:\- |]+\|$", ln.strip())]
            rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
            if pending_table_caption:
                n, cap = pending_table_caption
                out.append(para(f"**Table {n}.** {cap}", size=18, jc="left", before=60, after=80, keep_next=True))
                pending_table_caption = None
            out.append(table(rows))
            out.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="80" w:lineRule="exact"/></w:pPr></w:p>')  # air below the table
            continue
        m = re.match(r"\*Table (\d) note:\*\s*(.+)$", " ".join(b.split()), re.S)
        if m:
            out.append(para(clean(m.group(2)), size=15, jc="left", before=0, after=120))
            continue
        lines = b.splitlines()
        if len(lines) > 1 and re.fullmatch(r"\*[A-Z][^*]{1,40}\*", lines[0].strip()):  # "*Define*" + steps
            items, cur = [], ""
            for ln in lines[1:]:
                if re.match(r"^\s*\d+\.\s", ln):
                    if cur:
                        items.append(cur)
                    cur = ln.strip()
                else:
                    cur += " " + ln.strip()
            items.append(cur)
            label = lines[0].strip().strip("*")
            out.append(para(f"**{label}:** " + " ".join(clean(i) for i in items), after=80))
            continue
        if all(re.match(r"^\s*(\d+\.\s|-\s|\s{2,}\S)", ln) for ln in lines) and re.match(r"^\s*(\d+\.|-)\s", lines[0]):
            items, cur = [], ""
            for ln in lines:
                if re.match(r"^\s*(\d+\.|-)\s", ln):
                    if cur:
                        items.append(cur)
                    cur = ln.strip()
                else:
                    cur += " " + ln.strip()
            items.append(cur)
            for it in items:
                if it.startswith("- "):
                    out.append(para(clean(it[2:]), after=60, num=True,
                                    ind='<w:ind w:left="357" w:hanging="357"/>'))
                else:
                    nm = re.match(r"(\d+)\.\s+(.*)", it)
                    out.append(para(f"{nm.group(1)}. " + clean(nm.group(2)), after=40,
                                    ind='<w:ind w:left="357" w:hanging="357"/>'))
            continue
        if re.fullmatch(r"\*[A-Z][^*]{1,40}\*", b):  # block label inside the twelve steps
            out.append(para(b.strip("*"), bold=True, after=40, before=120, keep_next=True, jc="left"))
            continue
        out.append(para(clean(" ".join(ln.strip() for ln in lines)), after=90))
    # references on their own page (not counted by the 5-page rule), numbered in order of first citation
    ref_xml = [heading("References", new_page=True)]
    headings.append("References")
    rpr = FONT + '<w:sz w:val="17"/><w:szCs w:val="17"/><w:lang w:val="en-GB"/>'
    for n, key in enumerate(order, 1):
        txt = ref_map[key]
        m = re.search(r"\s(https?://\S+?)\.?$", txt)
        url = m.group(1) if m else None
        if url:
            txt = txt[:m.start()].rstrip()
        txt = txt.rstrip(".") + "."
        link = ""
        if url:
            rid = media.link(url)
            link = (f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve"> </w:t></w:r>'
                    f'<w:hyperlink r:id="{rid}" w:history="1"><w:r><w:rPr>{FONT}<w:color w:val="{CITE_COLOR}"/>'
                    f'<w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr><w:t xml:space="preserve">{html.escape(url, quote=False)}'
                    '</w:t></w:r></w:hyperlink>')
        ref_xml.append(
            '<w:p><w:pPr><w:tabs><w:tab w:val="left" w:pos="454"/></w:tabs><w:spacing w:after="50"/>'
            '<w:ind w:left="454" w:hanging="454"/><w:jc w:val="left"/></w:pPr>'
            f'<w:bookmarkStart w:id="{9000 + n}" w:name="ref_{n}"/>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:t>[{n}]</w:t></w:r><w:bookmarkEnd w:id="{9000 + n}"/>'
            f'<w:r><w:rPr>{rpr}</w:rPr><w:tab/></w:r>{runs(clean(txt), 17)}{link}</w:p>')
    return "".join(out), headings, "".join(ref_xml)


def fill_cover(x: str) -> str:
    def box(x: str, placeholder: str, new_paras_xml: str, cy: int | None) -> str:
        i = x.index(f"<w:t>{placeholder}</w:t>")
        s = x.rfind("<w:txbxContent>", 0, i) + len("<w:txbxContent>")
        e = x.index("</w:txbxContent>", i)
        x = x[:s] + new_paras_xml + x[e:]
        if cy:
            a = x.rfind("<wp:anchor ", 0, s)
            seg = x[a:s]
            seg2 = re.sub(r'(<wp:extent cx="\d+" cy=")\d+', rf"\g<1>{cy}", seg)
            seg2 = re.sub(r'(<a:ext cx="\d+" cy=")\d+', rf"\g<1>{cy}", seg2)
            x = x[:a] + seg2 + x[s:]
        return x

    tf = '<w:rFonts w:ascii="Montserrat Medium" w:hAnsi="Montserrat Medium"/>'
    t = (f'<w:p><w:pPr><w:spacing w:after="0"/><w:rPr>{tf}<w:sz w:val="60"/></w:rPr></w:pPr><w:r><w:rPr>{tf}'
         f'<w:sz w:val="60"/><w:szCs w:val="60"/></w:rPr><w:t>{html.escape(TITLE)}</w:t></w:r></w:p>')
    sub = "".join(f'<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr>{tf}<w:sz w:val="26"/><w:szCs w:val="26"/>'
                  f'</w:rPr><w:t>{html.escape(s)}</w:t></w:r></w:p>' for s in SUBTITLE)
    x = box(x, "Title", t, None)
    x = box(x, "Subtitle", sub, 1150000)
    return x


def add_bullets(numbering: str) -> str:
    absn = (f'<w:abstractNum w:abstractNumId="{BULLET_NUM_ID}"><w:multiLevelType w:val="hybridMultilevel"/>'
            '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val=""/>'
            '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="357" w:hanging="357"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr></w:lvl></w:abstractNum>')
    num = f'<w:num w:numId="{BULLET_NUM_ID}"><w:abstractNumId w:val="{BULLET_NUM_ID}"/></w:num>'
    i = numbering.index("<w:num ")  # abstractNums must precede nums
    numbering = numbering[:i] + absn + numbering[i:]
    return numbering.replace("</w:numbering>", num + "</w:numbering>")


def build() -> Path:
    md = DRAFT.read_text(encoding="utf-8")
    media = Media()
    main_xml, headings, ref_xml = body_xml(md, media)
    zin = zipfile.ZipFile(TEMPLATE)
    parts = {n: zin.read(n) for n in zin.namelist()}
    x = parts["word/document.xml"].decode("utf-8")
    x = fill_cover(x)
    # body: from the end of the TOC block to the section properties
    s = x.index("</w:sdt>") + len("</w:sdt>")
    e = x.rindex("<w:sectPr")
    x = x[:s] + PAGE_BREAK + main_xml + ref_xml + x[e:]
    parts["word/document.xml"] = x.encode("utf-8")
    parts["word/numbering.xml"] = add_bullets(parts["word/numbering.xml"].decode("utf-8")).encode("utf-8")
    rels = parts["word/_rels/document.xml.rels"].decode("utf-8")
    rels = rels.replace("</Relationships>", "".join(
        f'<Relationship Id="{rid}" Type="{R_IMG}" Target="{tgt}"/>' for rid, tgt in media.rels) + "".join(
        f'<Relationship Id="{rid}" Type="{R_LINK}" Target="{html.escape(u)}" TargetMode="External"/>'
        for rid, u in media.links) + "</Relationships>")
    parts["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    for name, data in media.files:
        parts[f"word/media/{name}"] = data
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for n, d in parts.items():
            z.writestr(n, d)
    print(f"wrote {OUT.relative_to(ROOT).as_posix()} ({len(headings)} sections, {len(media.files)} images)")
    return OUT


WORD_PS = r"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
  $d = $w.Documents.Open('{docx}')
  foreach ($t in $d.TablesOfContents) { $t.Update() }
  $d.Save()
  $d.ExportAsFixedFormat('{pdf}', 17)
  $n = $d.ComputeStatistics(2)
  $refs = $null
  foreach ($p in $d.Paragraphs) { if ($p.Range.Text.Trim() -eq 'References' -and $p.Style.NameLocal -ne 'Normal') { $refs = $p.Range.Information(3) } }
  "pages=$n references_page=$refs"
  $d.Close($true)
} finally { $w.Quit() }
"""


def word_pass() -> None:
    ps = WORD_PS.replace("{docx}", str(OUT)).replace("{pdf}", str(PDF))
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=240)
    print((r.stdout or "").strip() or r.stderr.strip())
    m = re.search(r"pages=(\d+) references_page=(\d+)", r.stdout or "")
    if m:
        body_pages = int(m.group(2)) - 3  # cover p1, TOC p2, body from p3 to the page before the references
        print(f"body pages (p3 to p{int(m.group(2)) - 1}) = {body_pages} of 5 " +
              ("OK" if body_pages <= 5 else "OVER — cut the draft"))
        print(f"wrote {PDF.relative_to(ROOT).as_posix()}")


TRADEOFFS = O / "tradeoffs" / "tradeoffs.json"


def rf(x: float) -> str:
    """Same rounding as tradeoffs.md: one decimal below 100, thin-space thousands above."""
    return f"{x:,.0f}".replace(",", " ") if x >= 100 else f"{x:.1f}"


CUE_ROWS = [  # (label, section of tradeoffs.json, key); order = the order of the argument in §5
    ("No system (handle check only)", "main", "O0"),
    ("Task-sheet example: one microswitch, EFIS message, tone", "main", "O2"),
    ("Red lamp", "main", "O3"),
    ("Lamp, voice and taxi chime", "main", "O4"),
    ("**Lamp, voice, chime and lap-belt pad (chosen)**", "main", "O5"),
]
SENSOR_LABELS = {"S1": "**Inductive, line-monitored (chosen)**", "S4": "Snap switch with self-test",
                 "S2": "Bare bolt contact with resistors", "S5": "Hall sensor and magnet",
                 "S6": "Linkage sensor (LVDT) and seated sensor", "S7": "Handle switch alone"}
TABLE_DIR = O / "report_tables"
CS_NAME = {"O5": "lamp, voice, chime, belt pad", "O4": "lamp, voice, chime"}


def SENSOR_SET(d: dict) -> str:
    """Table 6 uses the chosen set O5 once easa_tradeoffs.py writes it; until then O4, and the header says so."""
    if "O5_acts_c" in d["sensing_options"][0]:
        return "O5"
    print("  Table 6: tradeoffs.json has no O5 sensing columns yet, using O4 (lamp, voice, chime)")
    return "O4"


def gen_table(kind: str) -> str:
    """§5 tables straight from tradeoffs.json (also written to outputs/report_tables/ for the datawiz check)."""
    d = json.loads(TRADEOFFS.read_text(encoding="utf-8"))

    def b(lbl: str, x: str) -> str:
        return f"**{x}**" if lbl.startswith("**") else x
    if kind == "cues":
        head = ["Cue set (per-bolt inductive sensors)", "RF, always acts (×)", "RF, distrusts (×)"]
        rows = []
        for lbl, sec, k in CUE_ROWS:
            r = d[sec][k]
            rows.append([lbl, b(lbl, rf(r["rf_full_ind"])), b(lbl, rf(r["rf_matching_ind"]))])
    else:
        cs = SENSOR_SET(d)
        head = [f"Sensor ({CS_NAME[cs]})", "Sees one bolt out", "False alerts per 1 000 flights",
                "RF, always acts (×)", "RF, distrusts (×)"]
        so = sorted((r for r in d["sensing_options"] if r["key"] in SENSOR_LABELS),
                    key=lambda r: (-round(r[f"{cs}_acts_c"], 1), -r[f"{cs}_match_c"]))
        rows = []
        for r in so:
            lb = SENSOR_LABELS[r["key"]]
            rows.append([lb, b(lb, "no" if "one_bolt" in r["blind"] else "yes"), b(lb, f"{r['fa_c'] * 1000:.2f}"),
                         b(lb, rf(r[f"{cs}_acts_c"])), b(lb, rf(r[f"{cs}_match_c"]))])
    md = "\n".join("| " + " | ".join(r) + " |" for r in [head, [":---"] * len(head)] + rows)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    (TABLE_DIR / f"T_{kind}.md").write_text(md + "\n", encoding="utf-8")
    return md


def number_check(md: str) -> list[str]:
    """Every §5 number that comes from easa_tradeoffs.py must still match tradeoffs.json (the other session reruns it)."""
    d = json.loads(TRADEOFFS.read_text(encoding="utf-8"))
    m, v, u = d["main"], d["variants"], d["uncertainty"]
    text = " ".join(md.split())
    lo = min(u[k]["rf_matching"][0] for k in ("O3", "O4", "O5"))
    hi = max(u[k]["rf_matching"][2] for k in ("O3", "O4", "O5"))
    sw = d["compliance_sweep"]
    i05 = sw["c"].index(0.5)
    i005 = sw["c"].index(0.05)
    a05 = [sw[k][i05] for k in ("O3", "O4", "O5")]
    sens = d["sensing"]
    so = {r["key"]: r for r in d["sensing_options"]}
    ppv = m["O6"]["ppv_matching_ind"]
    leader = all(max((k for k in sw if k != "c"), key=lambda k: sw[k][i]) == "O6" for i in range(len(sw["c"])))
    claims = [
        f"missed a single bolt out in {sens['ORG']['k_miss']['one_bolt']:,} trials ({sens['ORG']['miss']['one_bolt']:.2f})".replace(",", " "),
        f"missed a partial lock {sens['A3']['k_miss']['partial']} times and one bolt out {sens['A3']['k_miss']['one_bolt']} times",
        f"upper bound {sens['A3']['miss_upper95']['unseated']:.0e}".replace("e-05", "e-5"),
        f"as alerts have been right ({ppv:.2f})",
        f"false-alert rate {m['O3']['fa_per_1000']:.2f} per 1 000 flights",
        f"{so['S1']['fa_c'] * 1000:.2f} for the inductive sensor, so the chosen set gives {rf(so['S1']['O5_match_c'])}× there",
        f"about {so['S1']['fa_u'] * 1000:.0f} false alerts per",
        f"gains nothing ({so['S1']['O5_match_u']:.1f}×)",
        f"(c = 0.5), the alert sets give {min(a05):.1f}× to {max(a05):.1f}×",
        f"set gives {m['O5']['rf_full_ind']:.0f}× when the pilot always acts and about {m['O5']['rf_matching_ind']:.0f}× when",
    ]
    _ = (lo, hi, i005)
    return [c for c in claims if c not in text]


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    md = DRAFT.read_text(encoding="utf-8")
    body = md.split("## Title:")[1].split("## References")[0]
    dashes = [ln.strip()[:70] for ln in body.splitlines() if ("—" in ln or "–" in ln) and not ln.startswith("## ")]
    print("dash scan (humanizer): " + ("OK" if not dashes else f"{len(dashes)} lines with — or –: " + " | ".join(dashes)))
    stale = number_check(md)
    print("number check vs tradeoffs.json: " + ("OK" if not stale else
          f"{len(stale)} STALE — the draft should say: " + " | ".join(stale)))
    build()
    if "--no-word" not in argv:
        word_pass()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
