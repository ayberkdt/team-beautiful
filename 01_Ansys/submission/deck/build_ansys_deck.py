"""Build the 4-minute Ansys deck for Team Beetiful from the official template.

Source of truth: the submitted report PDF (5 Nov 2026, 15:04). Its text matches
01_Ansys/submission/final_report/Team_Beetiful_Ansys_Report.docx (15:02); the
figures are taken from that docx so they are the same pixels as in the PDF.

Run:  python build_ansys_deck.py
Out:  Team_Beetiful_Ansys_4min.pptx, fig/*.png, build_check.txt (overflow + timing)
"""
from __future__ import annotations

import copy
import io
import re
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Emu, Pt

DECK = Path(__file__).resolve().parent
ROOT = DECK.parents[2]
TEMPLATE = ROOT / "01_Ansys/submission/ANSYS_Ideathon_2026_sunum_TASLAK.pptx"
REPORT_DOCX = ROOT / "01_Ansys/submission/final_report/Team_Beetiful_Ansys_Report.docx"
LOGO = Path(r"D:\Kullanici\Downloads\Team Beetiful Arı Logosu.png")
OUT = DECK / "Team_Beetiful_Ansys_4min.pptx"
FIG = DECK / "fig"
CHECK = DECK / "build_check.txt"
SCRIPT = DECK / "talk_script.md"

FONT_DIR = Path(r"C:\Users\ayber\AppData\Local\Programs\MiKTeX\fonts\opentype\public\montserrat")
FONT = "Montserrat"

INK = RGBColor(0x40, 0x09, 0x41)      # template text colour
ACCENT = RGBColor(0x7C, 0x24, 0x80)   # template "POWERED BY" pill
GREY = RGBColor(0x59, 0x59, 0x59)
CARD = RGBColor(0xF5, 0xEE, 0xF5)

EMU_IN = 914400
WORDS_PER_SECOND_MAX = 2.3            # check: notes must be speakable in the planned time
TOTAL_MAX_S = 230                     # 3:50


def emu(inches: float) -> Emu:
    return Emu(int(round(inches * EMU_IN)))


# --------------------------------------------------------------------------- template handling
R_EMBED = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"


def clone_slide(prs, src):
    """Append a copy of template slide `src` (decorations + footer) to the deck."""
    new = prs.slides.add_slide(src.slide_layout)
    for shp in list(new.shapes):
        shp._element.getparent().remove(shp._element)
    rid_map = {}
    for rid, rel in src.part.rels.items():
        if rel.reltype.endswith("/image"):
            rid_map[rid] = new.part.relate_to(rel._target, rel.reltype)
    for el in src.shapes._spTree.iterchildren():
        tag = el.tag.split("}")[1]
        if tag in ("nvGrpSpPr", "grpSpPr"):
            continue
        new_el = copy.deepcopy(el)
        for node in new_el.iter():
            if R_EMBED in node.attrib:
                node.set(R_EMBED, rid_map[node.get(R_EMBED)])
        new.shapes._spTree.append(new_el)
    return new


def delete_slide(prs, slide):
    lst = prs.slides._sldIdLst
    for sld_id in list(lst):
        if prs.part.related_part(sld_id.rId) is slide.part:
            prs.part.drop_rel(sld_id.rId)
            lst.remove(sld_id)
            return
    raise RuntimeError("slide not found")


def replace_text(slide, old: str, new: str) -> int:
    n = 0
    for node in slide.shapes._spTree.iter():
        if node.tag.endswith("}t") and node.text == old:
            node.text = new
            n += 1
    return n


# --------------------------------------------------------------------------- text + measurement
_font_cache: dict = {}


def _font(size: float, bold: bool):
    key = (round(size * 4), bold)
    if key not in _font_cache:
        f = FONT_DIR / ("Montserrat-Bold.otf" if bold else "Montserrat-Regular.otf")
        _font_cache[key] = ImageFont.truetype(str(f), int(round(size * 4)))  # 4 px per pt
    return _font_cache[key]


def run_width_in(text: str, size: float, bold: bool) -> float:
    return _font(size, bold).getlength(text) / 4 / 72


NBSP = " "
UNITS = r"(°C|MPa·m½|MPa|mm|kg|km|kN|N·m|USD|t|%|×)"


def keep_together(t: str) -> str:
    """No line break inside '71 000', '300 °C', '≈ 52 000' (non-breaking spaces)."""
    t = re.sub(r"(\d) (?=\d{3}\b)", r"\1" + NBSP, t)
    t = re.sub(r"(\d) (?=" + UNITS + r"(?![A-Za-z]))", r"\1" + NBSP, t)
    t = re.sub(r"([≈≤≥<>−]) (?=\d)", r"\1" + NBSP, t)
    return t


class R:
    def __init__(self, text, size=28, bold=False, color=INK):
        self.text, self.size, self.bold, self.color = keep_together(text), size, bold, color


def P(*runs, align="l", after=0, line=1.0):
    return {"runs": list(runs), "align": align, "after": after, "line": line}


CHECKS: list[str] = []
RECTS: dict[int, list] = {}   # slide -> [(label, x, y, w, h)] of text actually drawn and pictures
SIZES: dict[int, set] = {}


def measure_para(p, width_in):
    """Greedy word wrap with real font metrics. Returns (lines, height_in, widest_in)."""
    tokens = []
    for r in p["runs"]:
        for part in re.split(r"( +)", r.text):
            if part:
                tokens.append((part, r))
    lines, cur, widest = 1, 0.0, 0.0
    for txt, r in tokens:
        w = run_width_in(txt, r.size, r.bold)
        if txt.strip(" ") == "":
            cur += w
            continue
        if cur + w > width_in + 1e-6 and cur > 0:
            lines += 1
            widest = max(widest, cur)
            cur = w
        else:
            cur += w
        if w > width_in + 1e-6:
            CHECKS.append(f"  WORD TOO WIDE: '{txt}' {w:.2f} in > {width_in:.2f} in")
    widest = max(widest, cur)
    size = max(r.size for r in p["runs"])
    height = lines * size * 1.2 * p["line"] / 72 + p["after"] / 72
    return lines, height, widest


def text(slide, sidx, x, y, w, h, paras, anchor="t", name=None):
    box = slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
    if name:
        box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    total_h, widest = 0.0, 0.0
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[p["align"]]
        para.space_after = Pt(p["after"])
        para.line_spacing = p["line"]
        for r in p["runs"]:
            run = para.add_run()
            run.text = r.text
            run.font.name = FONT
            run.font.size = Pt(r.size)
            run.font.bold = r.bold
            run.font.color.rgb = r.color
            SIZES.setdefault(sidx, set()).add(r.size)
        _, ph, pw_ = measure_para(p, w)
        total_h += ph
        widest = max(widest, min(pw_, w))
    ty = {"t": y, "m": y + (h - total_h) / 2, "b": y + h - total_h}[anchor]
    tx = {"l": x, "c": x + (w - widest) / 2, "r": x + w - widest}[paras[0]["align"]]
    RECTS.setdefault(sidx, []).append((name or paras[0]["runs"][0].text[:30], tx, ty, widest, total_h))
    status = "ok" if total_h <= h + 0.02 else "OVERFLOW"
    label = name or "".join(r.text for r in paras[0]["runs"])[:40]
    if status != "ok":
        CHECKS.append(f"  slide {sidx}: {status} '{label}' needs {total_h:.2f} in, box {h:.2f} in")
    return box


def card(slide, x, y, w, h, color=CARD):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, emu(x), emu(y), emu(w), emu(h))
    shp.adjustments[0] = min(0.12 / min(w, h), 0.5)  # 0.12 in radius everywhere
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def rule(slide, x, y, w, color=ACCENT, weight=0.06):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, emu(x), emu(y), emu(w), emu(weight))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def picture(slide, path, x, y, w, h, align="c", sidx=None):
    """Place an image inside the box (contain), never stretched."""
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px = x + {"l": 0, "c": (w - pw) / 2, "r": w - pw}[align]
    py = y + (h - ph) / 2
    slide.shapes.add_picture(str(path), emu(px), emu(py), emu(pw), emu(ph))
    if sidx is not None:
        RECTS.setdefault(sidx, []).append(("picture " + Path(path).name, px, py, pw, ph))
    return px, py, pw, ph


# --------------------------------------------------------------------------- figures from the report
def extract_figures():
    """Report figures, same pixels as the submitted PDF (docx media)."""
    FIG.mkdir(exist_ok=True)
    z = zipfile.ZipFile(REPORT_DOCX)
    fig1 = Image.open(io.BytesIO(z.read("word/media/image6.png"))).convert("RGB")  # Figure 1
    fig2 = Image.open(io.BytesIO(z.read("word/media/image3.jpg"))).convert("RGB")  # Figure 2
    fig3 = Image.open(io.BytesIO(z.read("word/media/image7.png"))).convert("RGB")  # Figure 3
    assert fig1.size == (4784, 824) and fig2.size == (1600, 735) and fig3.size == (4830, 824)
    crops = {
        # Figure 1 panels, geometry only (legend text cut; legend stated in caption)
        "fig1a_run1.png": (fig1, (640, 150, 1552, 824)),
        "fig1b_run2.png": (fig1, (2420, 70, 3590, 824)),
        "fig1c_final.png": (fig1, (3790, 66, 4600, 824)),
        # Figure 3a: original S275N part, Ansys, load case 1 (geometry only)
        "fig3a_steel.png": (fig3, (650, 200, 1450, 824)),
    }
    out = {}
    for name, (img, box) in crops.items():
        p = FIG / name
        img.crop(box).save(p)
        out[name] = p
    p = FIG / "fig2_tradeoff.png"
    fig2.save(p)
    out["fig2_tradeoff.png"] = p
    return out


# --------------------------------------------------------------------------- content
X0, XW = 1.12, 17.76            # content left edge and width (matches template footer rule)
TITLE_Y, TITLE_H = 2.42, 0.80
BODY_Y, BODY_BOTTOM = 3.50, 10.05
SRC_Y = 9.72


TITLES = {1: "Cover: Team Beetiful, eco-redesign of the engine cowling bracket"}


def title(slide, sidx, txt):
    TITLES[sidx] = txt
    text(slide, sidx, X0, TITLE_Y, XW, TITLE_H, [P(R(txt, 40, True, INK))], anchor="t", name="Title")


def source(slide, sidx, txt):
    text(slide, sidx, X0, SRC_Y, XW, 0.32, [P(R("Report: " + txt, 18, False, GREY))], name="Source")


def stat(slide, sidx, x, y, w, number, unit, label, color=INK, nsize=60, label_h=0.9, name=None):
    """Big number (+ smaller unit) with a label under it."""
    runs = [R(number, nsize, True, color)]
    if unit:
        runs.append(R(" " + unit, 28, True, color))
    text(slide, sidx, x, y, w, nsize / 72 * 1.2, [P(*runs)], name=name or f"stat {number}")
    text(slide, sidx, x, y + nsize / 72 * 1.2 + 0.05, w, label_h, [P(R(label, 24, False, GREY))],
         name=f"label {number}")


NOTES = {}   # slide index -> (speaker, seconds, text)


def notes(slide, sidx, speaker, seconds, body):
    NOTES[sidx] = (speaker, seconds, body)
    tf = slide.notes_slide.notes_text_frame
    tf.text = f"{speaker} · {seconds} s\n{body}"


def build():
    figs = extract_figures()
    prs = Presentation(str(TEMPLATE))
    cover, content_tpl = prs.slides[0], prs.slides[1]

    # ---------------- slide 1: cover (template slide 1, edited in place)
    s = 1
    assert replace_text(cover, "TEAM NAME", "TEAM BEETIFUL") == 1
    assert replace_text(cover, "Short description", "Eco-redesign of the engine cowling bracket") == 1
    for shp in cover.shapes:
        if shp.has_text_frame and shp.text_frame.text in ("Eco-redesign of the engine cowling bracket",
                                                           "TEAM BEETIFUL"):
            shp.width = emu(8.0)          # template boxes are ~3 in wide and centred; keep one line, left edge
            shp.text_frame.word_wrap = False
            for para in shp.text_frame.paragraphs:
                para.alignment = PP_ALIGN.LEFT
    # team logo in the empty upper-left area of the white panel (near-white made transparent)
    logo = Image.open(LOGO).convert("RGBA")
    px_ = logo.load()
    for yy in range(logo.size[1]):
        for xx in range(logo.size[0]):
            r_, g_, b_, _ = px_[xx, yy]
            if r_ > 245 and g_ > 245 and b_ > 245:
                px_[xx, yy] = (255, 255, 255, 0)
    logo_p = FIG / "team_logo_transparent.png"
    logo.save(logo_p)
    cover.shapes.add_picture(str(logo_p), emu(0.80), emu(0.45), emu(3.55), emu(3.55))
    text(cover, s, 1.12, 6.75, 8.0, 0.45, [P(R("Ansys challenge · EUROAVIA Ideathon 2026", 24, False, GREY))],
         name="Cover challenge")
    notes(cover, s, "Speaker 4", 10,
          "Good morning. We are Team Beetiful. We redesigned the engine cowling bracket. "
          "Our aim is less CO₂ over the life of the part.")

    slides = []

    def new_slide():
        sl = clone_slide(prs, content_tpl)
        slides.append(sl)
        # footer: set before any content is added, so only template text is touched
        assert replace_text(sl, "TEAM NAME", "TEAM BEETIFUL") == 1
        assert replace_text(sl, "2", str(len(slides) + 1)) == 1
        return sl

    # ---------------- slide 2: problem
    sl = new_slide(); s = 2
    title(sl, s, "Flight causes 97 % of the steel bracket's CO₂")
    text(sl, s, X0, 3.75, 7.6, 1.75, [P(R("97 %", 96, True, ACCENT))], name="hero 97")
    text(sl, s, X0, 5.45, 7.4, 1.4,
         [P(R("of the life-cycle CO₂ comes from flight: 51.2 of 52.6 t CO₂-eq", 28, False, INK))],
         name="hero label")
    text(sl, s, X0, 7.10, 7.6, 0.6,
         [P(R("Material and manufacture: only 2.6 %", 28, False, INK))], name="hero sub")
    rows = [("152", "kg", "S275N steel part today"),
            ("720 000", "km", "flown by each kilogram in one year"),
            ("337", "kg CO₂", "caused by each kilogram in one year")]
    for i, (n, u, lab) in enumerate(rows):
        y = 3.60 + i * 1.72
        stat(sl, s, 10.2, y, 8.6, n, u, lab, label_h=0.5)
    text(sl, s, X0, 8.95, XW, 0.5,
         [P(R("Question: how much extra production CO₂ can we accept to remove 1 kg?", 28, True, INK))],
         name="question")
    source(sl, s, "§1; Granta eco audit [3]")
    notes(sl, s, "Speaker 1", 25,
          "Today the bracket is a 152 kg part in S275N steel. "
          "The eco audit gives 52.6 t of CO₂ in the card scenario. "
          "Flight causes 97 % of this. "
          "Each kilogram flies 720 000 km a year and causes 337 kg of CO₂. "
          "So how much extra production CO₂ can we accept to remove one kilogram?")

    # ---------------- slide 3: requirements and load cases
    sl = new_slide(); s = 3
    title(sl, s, "The card fixes the holes, the loads and the limits")
    px, py, pw, ph = picture(sl, figs["fig3a_steel.png"], X0, 3.55, 5.6, 5.0, sidx=s)
    text(sl, s, X0, 8.75, 5.6, 0.85,
         [P(R("Original S275N part: 4 bolt holes, 2 lugs with 60 mm pin holes (Fig. 3a)", 18, False, GREY))],
         name="fig caption")
    gx, gw = 7.35, 11.53
    text(sl, s, gx, 3.50, gw, 0.45, [P(R("Load cases", 24, True, INK))], name="g1")
    tw = gw / 3
    stat(sl, s, gx, 4.05, tw - 0.2, "97", "kN", "vertical, each pin hole (case 1)", nsize=60, label_h=0.8)
    stat(sl, s, gx + tw, 4.05, tw - 0.2, "24", "kN", "along the pin, pushes lugs together", nsize=60, label_h=0.8)
    stat(sl, s, gx + 2 * tw, 4.05, tw - 0.2, "2 000", "N·m", "torsion, half on each pin hole (case 2)",
         nsize=60, label_h=0.8)
    rule(sl, gx, 6.15, gw, color=CARD, weight=0.04)
    text(sl, s, gx, 6.35, gw, 0.45, [P(R("Limits", 24, True, INK))], name="g2")
    lw = gw / 4
    stat(sl, s, gx, 6.90, lw - 0.2, "1.5", "", "safety factor on yield", nsize=60, label_h=0.8)
    stat(sl, s, gx + lw, 6.90, lw - 0.2, "1.65", "mm", "max. displacement", nsize=60,
         label_h=0.8, color=ACCENT)
    stat(sl, s, gx + 2 * lw, 6.90, lw - 0.2, "300", "°C", "min. working temperature", nsize=60, label_h=0.8)
    stat(sl, s, gx + 3 * lw, 6.90, lw - 0.2, "10", "", "min. toughness, MPa·m½", nsize=60, label_h=0.8)
    text(sl, s, gx, 9.05, gw, 0.5,
         [P(R("Castable or 3D-printable. Bolt and pin hole positions stay fixed.", 24, False, INK))],
         name="fixed")
    source(sl, s, "§1, Table 1; card [1]")
    notes(sl, s, "Speaker 1", 27,
          "The card fixes the bolt and pin holes. "
          "Load case 1 puts 97 kN vertical and 24 kN along the pin on each hole. "
          "The 24 kN loads push the lugs together. "
          "Load case 2 is a torsion of 2 000 N·m. "
          "The safety factor is 1.5 on yield. The displacement limit is 1.65 mm. "
          "The material must work above 300 °C.")

    # ---------------- slide 4: material screen
    sl = new_slide(); s = 4
    title(sl, s, "Granta screen: titanium stays, aluminium fails")
    funnel = [("3 904", "materials in Granta"),
              ("196", "pass the Granta screen"),
              ("3", "shortlisted by the organisers"),
              ("2", "analysed: steel and titanium")]
    fw = XW / 4
    for i, (n, lab) in enumerate(funnel):
        stat(sl, s, X0 + i * fw, 3.45, fw - 0.45, n, "", lab, nsize=60, label_h=0.85)
        if i < 3:
            text(sl, s, X0 + i * fw + fw - 0.55, 3.55, 0.5, 0.8, [P(R("→", 40, True, GREY))], name="arrow")
    cw = (XW - 2 * 0.3) / 3
    cards = [("S275N steel", "Reference", "471–501 °C · allowable 107 MPa", INK),
             ("Al 2618-T6", "Eliminated", "250–300 °C: no margin. High stress-corrosion and sourcing risk", GREY),
             ("Ti-8Al-1Mo-1V", "Selected", "407–455 °C · allowable 345 MPa", ACCENT)]
    for i, (name, verdict, why, col) in enumerate(cards):
        cx = X0 + i * (cw + 0.3)
        card(sl, cx, 5.75, cw, 2.55)
        text(sl, s, cx + 0.3, 5.90, cw - 0.6, 0.5, [P(R(name, 28, True, INK))], name=f"card {name}")
        text(sl, s, cx + 0.3, 6.42, cw - 0.6, 0.45, [P(R(verdict, 24, True, col))], name=f"verdict {name}")
        text(sl, s, cx + 0.3, 6.92, cw - 0.6, 1.25, [P(R(why, 24, False, INK))], name=f"why {name}")
    text(sl, s, X0, 8.55, XW, 1.0,
         [P(R("Producing 1 kg of titanium emits 11.6× the CO₂ of 1 kg of steel. "
              "In the same shape, flight pays this back in 71 000 km = 18 of 180 flight days.", 28, False, INK))],
         name="payback")
    source(sl, s, "§2, Table 2; Granta selection report [2]")
    notes(sl, s, "Speaker 2", 30,
          "We changed material and shape together. "
          "The Granta screen kept 196 of 3 904 materials. The organisers gave three. "
          "Aluminium has no margin at 300 °C. "
          "It also has a high stress-corrosion risk and a very high sourcing risk. So we removed it. "
          "Titanium makes 11.6 times more CO₂ per kilogram than steel. "
          "But in the same shape, flight pays this back in 18 flight days.")

    # ---------------- slide 5: topology optimisation
    sl = new_slide(); s = 5
    title(sl, s, "Topology optimisation keeps the base plate")
    text(sl, s, X0, 3.35, XW, 0.5,
         [P(R("Load case 1 drives the optimisation: 69.5 MPa against 5.2 MPa for torsion (steel part).",
              24, False, INK))], name="driver")
    panels = [(figs["fig1a_run1.png"], "Run 1: whole part free", "Plate removed; bolts no longer act as one group", GREY),
              (figs["fig1b_run2.png"], "Run 2: base plate kept", "Plate and bolt bosses kept", INK),
              (figs["fig1c_final.png"], "Final geometry", "Smoothed; 45 % of the original volume", ACCENT)]
    ratios = [Image.open(p).size[0] / Image.open(p).size[1] for p, *_ in panels]
    gap = 0.35
    ph_in = min(3.85, (XW - 2 * gap) / sum(ratios))
    x = X0 + (XW - 2 * gap - ph_in * sum(ratios)) / 2
    for (p, head, sub, col), r in zip(panels, ratios):
        w = ph_in * r
        picture(sl, p, x, 4.05, w, ph_in, sidx=s)
        text(sl, s, x, 4.05 + ph_in + 0.15, max(w, 4.6), 0.45, [P(R(head, 24, True, col))], name=f"head {head}")
        text(sl, s, x, 4.05 + ph_in + 0.62, max(w, 4.6) if r < 1.2 else w, 0.85,
             [P(R(sub, 24, False, GREY))], name=f"sub {head}")
        x += w + gap
    source(sl, s, "§2, Fig. 1 (grey = keep, beige = marginal); Table 3")
    notes(sl, s, "Speaker 2", 30,
          "Load case 1 drove the topology optimisation in Ansys Mechanical. "
          "On the steel part it gives 69.5 MPa. The torsion gives only 5.2 MPa. "
          "In run 1 the whole part was free. The optimiser removed the base plate and left two arms. "
          "Then the bolts do not work as one group. "
          "In run 2 we kept the base plate and the bolt bosses. Then we smoothed the result.")

    # ---------------- slide 6: trade-off
    sl = new_slide(); s = 6
    title(sl, s, "Titanium at 45 % volume: 25 % mass, 27 % CO₂")
    fx, fy, fw_, fh = picture(sl, figs["fig2_tradeoff.png"], X0, 3.45, 13.3, 6.15, align="l", sidx=s)
    cx = 15.05
    text(sl, s, cx, 3.55, 3.83, 0.85, [P(R("Against the original steel part", 24, True, INK))],
         name="vs label")
    stat(sl, s, cx, 4.60, 3.83, "25 %", "", "mass", nsize=60, label_h=0.45)
    stat(sl, s, cx, 6.25, 3.83, "27 %", "", "life-cycle CO₂", color=ACCENT, nsize=60, label_h=0.45)
    stat(sl, s, cx, 7.90, 3.83, "4.9×", "", "raw-material cost", nsize=60, label_h=0.45)
    source(sl, s, "§2, Fig. 2 (card scenario [1–3])")
    notes(sl, s, "Speaker 3", 26,
          "Life-cycle CO₂ increases with part volume, 1.6 times faster for steel. "
          "Our titanium part keeps 45 % of the volume. "
          "A steel part must decrease to 27 % to give the same CO₂. "
          "Against the original part, titanium has 25 % of the mass and 27 % of the CO₂. "
          "The material cost is 4.9 times higher.")

    # ---------------- slide 7: verification and limits
    sl = new_slide(); s = 7
    title(sl, s, "The titanium part meets every limit")
    tiles = [("Stress, load case 1", "78.5", "MPa", "Allowable 345 MPa", "Own FE: 142 MPa", ACCENT),
             ("Displacement, load case 1", "0.36–0.38", "mm", "Limit 1.65 mm", "At 300 °C. Own FE: 0.87 mm", INK),
             ("Stress, load case 2", "5.2", "MPa", "Allowable 345 MPa", "Own FE: 35 MPa", INK)]
    tg = 0.3
    tw = (XW - 2 * tg) / 3
    for i, (head, n, u, lim, own, col) in enumerate(tiles):
        tx = X0 + i * (tw + tg)
        card(sl, tx, 3.45, tw, 3.30)
        text(sl, s, tx + 0.3, 3.65, tw - 0.6, 0.45, [P(R(head, 24, True, INK))], name=f"tile {head}")
        text(sl, s, tx + 0.3, 4.20, tw - 0.6, 1.0, [P(R(n, 60, True, col), R(" " + u, 28, True, col))],
             name=f"tile n {head}")
        text(sl, s, tx + 0.3, 5.30, tw - 0.6, 0.45, [P(R(lim, 24, True, INK))], name=f"tile lim {head}")
        text(sl, s, tx + 0.3, 5.85, tw - 0.6, 0.8, [P(R(own, 24, False, GREY))], name=f"tile own {head}")
    text(sl, s, X0, 6.95, XW, 0.45,
         [P(R("Checked three ways: hand calculation, own FE code, Ansys (smoothed final geometry).",
              24, False, INK))], name="method")
    text(sl, s, X0, 7.75, XW, 0.45, [P(R("Not modelled", 24, True, INK))], name="nm head")
    items = ["Fatigue at 300 °C", "Porosity and rough surface of printed titanium",
             "Thermal stress from constrained mounts", "Ti-8Al-1Mo-1V powder supply (to confirm)"]
    colw = (XW - 0.4) / 2
    for i, t in enumerate(items):
        text(sl, s, X0 + (i // 2) * (colw + 0.4), 8.25 + (i % 2) * 0.55, colw, 0.45,
             [P(R("– " + t, 24, False, INK))], name=f"nm {i}")
    source(sl, s, "§3, Table 3")
    notes(sl, s, "Speaker 3", 30,
          "We first checked the set-up on the steel part with a hand calculation, our own code and Ansys. "
          "In load case 1, the final part has 78.5 MPa in Ansys and 142 MPa in our code. "
          "Both are below the allowable 345 MPa. "
          "The displacement at 300 °C is 0.36 to 0.38 mm. The limit is 1.65 mm. "
          "We did not model fatigue, porosity or thermal stress.")

    # ---------------- slide 8: value
    sl = new_slide(); s = 8
    title(sl, s, "Year one: 114 kg lighter, 38 t less CO₂ per aircraft")
    text(sl, s, X0, 3.45, XW, 0.45, [P(R("Benefit", 24, True, INK))], name="benefit")
    bw = XW / 3
    stat(sl, s, X0, 3.95, bw - 0.4, "−72 %", "", "life-cycle CO₂: 14.6 t instead of 52.6 t", color=ACCENT,
         nsize=60, label_h=0.9)
    stat(sl, s, X0 + bw, 3.95, bw - 0.4, "114", "kg", "lighter part", nsize=60, label_h=0.9)
    stat(sl, s, X0 + 2 * bw, 3.95, bw - 0.4, "4 200", "km", "pay back the extra 0.25 t production CO₂ (≈ 1 flight day)",
         nsize=60, label_h=0.9)
    rule(sl, X0, 6.45, XW, color=CARD, weight=0.04)
    text(sl, s, X0, 6.65, XW, 0.45, [P(R("Drawback: cost", 24, True, INK))], name="cost")
    stat(sl, s, X0, 7.15, bw - 0.4, "≈ 52 000", "USD", "per printed bracket", nsize=60, label_h=0.9)
    stat(sl, s, X0 + bw, 7.15, 2 * bw - 0.4, "≈ 1 360", "USD", "per t CO₂ avoided in year one; falls with each year in service",
         nsize=60, label_h=0.9)
    source(sl, s, "§4, Table 4; cost [2, 6]")
    notes(sl, s, "Speaker 4", 30,
          "In one year, the final part causes 14.6 t of CO₂ instead of 52.6 t. That is 72 % less. "
          "The part is 114 kg lighter and saves 38 t of CO₂ per aircraft. "
          "Flight pays back the extra production CO₂ in about 4 200 km. "
          "Cost is the drawback: about 52 000 USD per bracket, "
          "or 1 360 USD per tonne of CO₂ in year one.")

    # ---------------- slide 9: closing
    sl = new_slide(); s = 9
    title(sl, s, "Choose material and shape in one loop")
    text(sl, s, X0, 3.45, 11.5, 1.4,
         [P(R("A material that looks poor per kilogram can win against 720 000 km of flight.", 28, False, INK))],
         name="idea")
    stat(sl, s, X0, 5.05, 3.6, "−72 %", "", "life-cycle CO₂", color=ACCENT, nsize=60, label_h=0.45)
    stat(sl, s, X0 + 3.9, 5.05, 3.6, "25 %", "", "of the mass", nsize=60, label_h=0.45)
    stat(sl, s, X0 + 7.8, 5.05, 3.8, "114", "kg", "lighter part", nsize=60, label_h=0.45)
    text(sl, s, X0, 7.35, XW, 0.45, [P(R("Next step", 24, True, INK))], name="next head")
    steps = ["Print a prototype", "Close porosity (HIP)", "Fatigue test at 300 °C", "Agree qualification route"]
    # one process line, no box per step (a box around a single item breaks the common-region rule)
    text(sl, s, X0, 7.85, XW, 0.5, [P(R("   →   ".join(steps), 24, True, INK))], name="steps")
    text(sl, s, X0, 9.05, XW, 0.5,
         [P(R("Thank you. Questions?", 28, True, INK))], name="thanks")
    source(sl, s, "§4, §5")
    notes(sl, s, "Speaker 4", 20,
          "Our main idea: choose material and shape in one loop. "
          "A material that looks poor per kilogram can win in flight. "
          "Next, we print a prototype, close its porosity and do a fatigue test at 300 °C. "
          "Thank you. We are ready for your questions.")

    # ---------------- footer numbers, remove template content slide
    delete_slide(prs, content_tpl)
    prs.save(str(OUT))


def report():
    lines = ["build check — " + OUT.name, "", "Overflow / wrap checks:"]
    lines += CHECKS or ["  none: every text box fits (Montserrat metrics, 1.2 line height)"]
    lines += ["", "Overlap checks (drawn text height, pictures; gap < 0.05 in counts):"]
    ov = []
    for sidx, rects in sorted(RECTS.items()):
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if (a[1] < b[1] + b[3] and b[1] < a[1] + a[3] and
                        a[2] < b[2] + b[4] + 0.05 and b[2] < a[2] + a[4] + 0.05):
                    ov.append(f"  slide {sidx}: '{a[0]}' overlaps '{b[0]}'")
    CHECKS.extend(ov)
    lines += ov or ["  none"]
    lines += ["", "Font sizes per slide (pt):"]
    allsz = set()
    for s in sorted(SIZES):
        allsz |= SIZES[s]
        lines.append(f"  slide {s}: {sorted(SIZES[s])} ({len(SIZES[s])} sizes)")
    lines.append(f"  deck (script-made text): {sorted(allsz)} ({len(allsz)} sizes); template adds 34, 24, 18 + Arial 23.7/34.8")
    lines += ["", "Timing (notes):", "  slide | speaker   | s  | words | words/s"]
    total = 0
    bad = False
    for s in sorted(NOTES):
        sp, sec, body = NOTES[s]
        n = len(re.findall(r"[^\s]+", body))
        total += sec
        rate = n / sec
        flag = "" if rate <= WORDS_PER_SECOND_MAX else "  TOO FAST"
        bad |= bool(flag)
        lines.append(f"  {s:5d} | {sp} | {sec:2d} | {n:5d} | {rate:.2f}{flag}")
    lines.append(f"  total {total} s = {total // 60}:{total % 60:02d} (max {TOTAL_MAX_S} s)")
    bad |= total > TOTAL_MAX_S
    long_sent = []
    for s, (_, _, body) in NOTES.items():
        for sent in re.split(r"(?<=[.?!:])\s+", body):
            n = len(sent.split())
            if n > 20:
                long_sent.append(f"  slide {s}: {n} words: {sent}")
    lines += ["", "Note sentences > 20 words:"] + (long_sent or ["  none"])
    CHECK.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 1 if (CHECKS or bad) else 0


QA = [
    ("Aluminium is the lightest candidate. Why did you remove it?",
     "At 250–300 °C it has no temperature margin. This is true for the card limit (> 300 °C) and for the Granta "
     "limit (≥ 300 °C). It also fails on oxidation, stress-corrosion cracking and sourcing risk. "
     "Against steel bolts it is the anode of a galvanic couple: −0.78 to −0.70 V against −0.51 to −0.43 V.",
     "§2, Table 2"),
    ("Your own FE code gives 142 MPa, Ansys gives 78.5 MPa. Why the difference?",
     "The values come from two different models. Our own FE uses the 45 % layout and reads the stress away from "
     "the bolt bores. Ansys uses the smoothed final geometry and gives the maximum over the whole part. "
     "Both values are below the allowable stress of 345 MPa.",
     "§3, Table 3 and its caption"),
    ("Ansys used room-temperature properties. Is the part safe at 300 °C?",
     "Yes, on the strength side. The allowable stress is the yield strength at 300 °C divided by 1.5. "
     "In the linear model the stress does not change with the modulus. "
     "The displacement increases with the modulus ratio to 0.36–0.38 mm at 300 °C. The limit is 1.65 mm.",
     "§3"),
    ("The titanium part costs much more. Is it worth it?",
     "The raw material costs about 950 USD against 196 USD for steel. Laser powder-bed printing costs about "
     "1 350 USD per kg of finished part (Ti-6Al-4V data). This gives about 52 000 USD per bracket. "
     "That is about 1 360 USD per tonne of CO₂ avoided in year one. This value decreases with each year in service.",
     "§4; references [2], [6]"),
    ("What about fatigue, porosity and certification?",
     "We did not model fatigue at 300 °C, the porosity and rough surface of printed titanium, or thermal stress. "
     "Our next step is a printed prototype. We close its porosity by hot isostatic pressing and do a fatigue test "
     "at 300 °C. Then we agree the qualification route with the authority. We must also confirm the supply of "
     "Ti-8Al-1Mo-1V powder.",
     "§3, §4"),
]


def write_script():
    out = ["# Team Beetiful · Ansys challenge · 4-minute talk script", "",
           "Generated by `build_ansys_deck.py` from the same text as the speaker notes in "
           "`Team_Beetiful_Ansys_4min.pptx`. Source of every fact: the submitted report PDF "
           "(5 Nov 2026, 15:04). Language: ASD-STE100 style (short sentences, active voice).", "",
           "## Timing", "",
           "| Slide | Title | Speaker | Seconds | Ends at |",
           "|---:|---|---|---:|---:|"]
    t = 0
    for sidx in sorted(NOTES):
        sp, sec, _ = NOTES[sidx]
        t += sec
        out.append(f"| {sidx} | {TITLES[sidx]} | {sp} | {sec} | {t // 60}:{t % 60:02d} |")
    per = {}
    for sp, sec, _ in NOTES.values():
        per[sp] = per.get(sp, 0) + sec
    out += ["", f"Total: **{t} s = {t // 60}:{t % 60:02d}** (hard cut at 4:00; {240 - t} s reserve for "
            "hand-over and pauses).", "",
            "Speaking time: " + ", ".join(f"{k} {v} s" for k, v in sorted(per.items())) + ".", "",
            "Four speakers (the report lists four team members; the rules ask the whole team to speak). "
            "Speaker 4 opens and closes the talk.", ""]
    prev, hand = None, []
    for sidx in sorted(NOTES):
        sp = NOTES[sidx][0]
        if prev and sp != prev:
            hand.append(f"before slide {sidx}: {prev} → {sp}")
        prev = sp
    out += ["Hand-overs: " + "; ".join(hand) + ".", "", "## Script", ""]
    for sidx in sorted(NOTES):
        sp, sec, body = NOTES[sidx]
        out += [f"### Slide {sidx} · {TITLES[sidx]}", "", f"*{sp} · {sec} s*", ""]
        out += [sent + "  " for sent in re.split(r"(?<=[.?!])\s+", body)]   # one sentence per line
        out.append("")
    out += ["## Likely jury questions", "",
            "Answers use only facts from the submitted report. Any team member can answer.", ""]
    for i, (q, a, src) in enumerate(QA, 1):
        out += [f"**Q{i}. {q}**", "", f"{a} *(Report {src})*", ""]
    SCRIPT.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    build()
    write_script()
    sys.exit(report())
