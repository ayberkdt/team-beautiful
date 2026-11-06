"""Build the 4:00 EASA talk (Team Beetiful, LOCK-SENSE) from the organisers' template.

    $env:PYTHONIOENCODING="utf-8"; python "02_EASA/submission/deck/build_easa_deck.py"

Writes, all inside 02_EASA/submission/deck/:
  Team_Beetiful_EASA_4min.pptx   the deck (cover + 8 content slides, speaker notes on every slide)
  talk_script.md                 script, timing table, likely jury questions (generated from the same data)
  traceability.md                every slide claim -> page / section of the submitted report
  fig/                           report figures with the white background made transparent (pixels unchanged
                                 otherwise) and the cropped team logo

Source of truth for every claim: the submitted report  D:/Kullanici/Downloads/Team_Beetiful_EASA_Report (2).pdf
(9 pages, created 20:44:09). Page numbers below are the printed page numbers of that PDF.
Figures: the high-resolution PNGs that the report embeds (pixel-matched to the PDF images, max diff 44/255 after
resampling, no pixel above 60): F1a, F1b (Figure 1), F10 (Figure 2), P1_phase_logic (Figure 3),
P2_compliance (Figure 5).
"""
from __future__ import annotations

import copy
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(r"D:\Masaustu\Ideathon 2026")
DECK = ROOT / "02_EASA" / "submission" / "deck"
TEMPLATE = ROOT / "00_Common" / "rules_and_templates" / "originals_2026-11-05" / "Ideathon Template 2026.pptx.pptx"
OUT = DECK / "Team_Beetiful_EASA_4min.pptx"
FIGSRC = ROOT / "02_EASA" / "outputs" / "figures"
LOGO = Path(r"D:\Kullanici\Downloads\Team Beetiful Arı Logosu.png")
REPORT = "Team_Beetiful_EASA_Report (2).pdf"

TEAM_FOOTER = "TEAM BEETIFUL"
DATE = "07/11/2026"          # Team Presentations on Nov 7th: Regulations 1.1 §1.1 p.5 + booklet p.8 (template default too)

# template colours and font (read from the template XML: 400941, A95FA0; Montserrat)
PURPLE = RGBColor(0x40, 0x09, 0x41)
MAUVE = RGBColor(0xA9, 0x5F, 0xA0)
INK = RGBColor(0x3A, 0x3A, 0x3A)
TINT = RGBColor(0xF6, 0xEC, 0xF4)
RULE = RGBColor(0xE2, 0xCF, 0xDF)
FONT = "Montserrat"

# type scale (pt): display = title + big numbers; body = everything else
T_TITLE, T_BIG, T_MID, T_BODY, T_SMALL = 34, 54, 26, 22, 18

# content frame (inches) below the template's header band and "POWERED BY" pill, above the footer rule (10.33 in)
X0, XW = 0.9, 18.2
Y_TITLE, Y_TOP, Y_BOT = 2.28, 3.55, 10.0


# ----------------------------------------------------------------------------- slide data
# Each slide: title, speaker, seconds, notes (STE), trace = [(claim on slide or in notes, report location)].
SLIDES = [
    dict(key="cover", speaker="Speaker 1", sec=6,
         notes="We are Team Beetiful. We present LOCK-SENSE, a canopy-lock alert for the Extra NG.",
         trace=[("LOCK-SENSE; Extra NG; EASA challenge; Team Beetiful", "p. 1 cover; p. 3 §1; p. 4 §3")]),
    dict(key="problem", speaker="Speaker 1", sec=32,
         title="A partly locked canopy looks the same as a locked one",
         notes=("The canopy of the Extra NG G-MIIL broke up at 184 knots. "
                "The AAIB found a bad frame bond. The BFU thought the canopy was not fully locked. "
                "The aircraft did not record the lock state, so nobody can settle this. "
                "The handles show the same 70 millimetre gap, locked or released. "
                "EASA AD 2025-0156 names a partly locked canopy as the main cause of openings. "
                "Our goal: fewer unnoticed unlocked take-offs, and a lock-state record."),
         trace=[("G-MIIL canopy broke up in level flight at 184 KIAS on 2 April 2022", "p. 3 §1 [1]"),
                ("AAIB: poor bonding of the canopy frame; BFU: not fully locked more probable", "p. 3 §1 [1, App. A]"),
                ("0 lock-state records: the aircraft did not record the lock state; nobody can settle it", "p. 3 §1"),
                ("70 mm handle gap both locked and open with handles released; frame edge looks the same", "p. 4 §2 [1, pp. 9, 20]"),
                ("AD 2025-0156: partly locked canopy = main cause of in-flight openings on this type", "p. 3 §1 [2]"),
                ("The type still has no electrical canopy warning", "p. 3 §1"),
                ("Goal: fewer take-offs with an unnoticed unlocked canopy, and a lock-state record", "p. 3 §1")]),
    dict(key="evidence", speaker="Speaker 1", sec=22,
         title="Lock-related openings cluster in the initial climb",
         notes=("Our catalogue has 241 investigated canopy and door events. "
                "126 were lock-related, and 16 were fatal. "
                "Most openings happen in the initial climb, on many aircraft types. "
                "On other types, every false 'locked' indication that we found came from one switch. "
                "It was on the handle, the drive or one pin."),
         trace=[("241 investigated canopy and door events from public reports", "p. 3 §2 [7]"),
                ("126 lock-related; 76 in the initial climb; 16 fatal", "p. 3-4 §2, Figure 1"),
                ("Figure 1 (a) flight phase, (b) type family", "p. 3 Figure 1"),
                ("Every false 'closed'/'locked' indication came from a switch on the handle, the drive or one pin "
                 "(DA40 PH-TIN, Pitts G-IIDY, RV-14A)", "p. 4 §2 [8-10]")]),
    dict(key="trade", speaker="Speaker 2", sec=31,
         title="Our choices reach a busy pilot and never take away power",
         notes=("For each element, we kept the option that reaches a busy pilot and never takes away engine power. "
                "We sense each bolt and the seat. One pin cannot see one bolt out. "
                "Inductive sensors give fewer false alerts. "
                "We use a voice without a lead tone, and a lap-belt pad. "
                "We removed engine shut-down, the gate and the throttle pawl. "
                "A fault there could take away power. So LOCK-SENSE only alerts."),
         trace=[("Table 1, all six rows (sensing point, sensor type, aural, vibration, barrier, G3X link)", "p. 5 Table 1"),
                ("Title = Table 1 caption: keep the option that reaches a busy pilot and never takes away engine power",
                 "p. 5 Table 1 caption"),
                ("Latch does not change; we add sensors and alerts only", "p. 3 §1 assumptions")]),
    dict(key="sensors", speaker="Speaker 2", sec=25,
         title="Green needs all four sensors; a partly locked bolt gives red",
         notes=("Four inductive sensors sit on the fuselage side, so the jettison path does not change. "
                "Three watch the bolt tips. One watches the seated frame. "
                "A sensor sees steel only at full lock. "
                "Green needs all four sensors. "
                "An open or a short circuit gives 'not locked'. "
                "No single electrical fault gave a false green."),
         trace=[("Figure 2: sensor sees the steel bolt tip only at full lock; partly locked -> off -> red", "p. 4 Figure 2"),
                ("4 inductive sensors, 3 bolt tips + seated frame, fuselage side, jettison path unchanged", "p. 4 §3"),
                ("Hardware AND: green CANOPY LOCKED lamp only when all four agree", "p. 4 §3"),
                ("Line monitoring: open or short -> fault -> 'not locked'", "p. 4 §3"),
                ("No single electrical fault gave a false green (13 fault cases)", "p. 7 §5")]),
    dict(key="logic", speaker="Speaker 3", sec=32,
         title="The red alert starts at line-up, before the take-off roll",
         notes=("The phase of flight sets the alerts. "
                "In taxi, an unlocked canopy gives only an amber lamp and one chime. "
                "At line-up, it gives a red lamp, the voice 'CANOPY, CANOPY' and the belt pad. "
                "With the lever trigger, the median pilot acts at 18 knots. An rpm trigger gives 31 knots. "
                "Pilots under high workload missed 38 percent of tones. Two or three cues act faster than one. "
                "The red lamp never waits."),
         trace=[("Figure 3 phase logic: taxi amber + one chime; line-up red lamp, voice, belt pad; ...", "p. 4 Figure 3"),
                ("Red alert starts at line-up, before the roll", "p. 5 §3"),
                ("Voice 'CANOPY, CANOPY'", "p. 4 §3"),
                ("Lever trigger: median 18 kt (95th 33 kt); rpm trigger: median 31 kt (95th 45 kt), brisk roll",
                 "p. 5 Figure 4 and caption"),
                ("38 % of headset tones missed under high workload; 2-3 cues faster than one", "p. 5 §3 [17, 19]"),
                ("Design for 1.5 s; 3.0 s as our 95th-percentile margin", "p. 5 §3 [20-22]"),
                ("New voice above 40 kt waits until 10 s after lift-off; red lamp never waits", "p. 5 §3")]),
    dict(key="retrofit", speaker="Speaker 3", sec=25,
         title="Twelve retrofit steps, each with a check that can fail",
         notes=("The retrofit has twelve steps. "
                "Steps 1 to 4 mount the sensors. First, we measure the bolt travel. We drill no new holes. "
                "Steps 5 to 8 wire and program the unit. "
                "Steps 9 to 12 test it: gauge checks, injected faults, an engine run and a check flight. "
                "Each step ends with a check that can fail."),
         trace=[("Table 2: twelve steps, 1-4 mount, 5-8 wire and program, 9-12 test; each ends with a check that can fail",
                 "p. 6 §4 Table 2 caption"),
                ("Step texts and pass checks (ratio r; no new holes; gap within 0.3 mm; jettison forces unchanged; "
                 "own breaker, peak 2.8 W; shielded loops; alerts within 0.5 s; bench run matches Figure 3; "
                 "10 of 10; faults logged; take-off power + aerobatic check flight; checklist line)", "p. 6 Table 2")]),
    dict(key="results", speaker="Speaker 4", sec=29,
         title="71× fewer unnoticed unsafe take-offs if pilots always act",
         notes=("A Monte Carlo model ran 200 000 take-offs per case. "
                "The task-sheet microswitch at one pin missed one bolt out in 67 percent of trials. "
                "Our four cues make an unnoticed unsafe take-off 71 times less likely, if the pilot always acts. "
                "If the pilot distrusts the alert, the gain is about 3 times. "
                "So the pilot sets the benefit. This is a model estimate."),
         trace=[("Monte Carlo, 200 000 simulated take-offs per case", "p. 6 §5"),
                ("One microswitch at one pin missed a single bolt out in 133 345 trials (0.67)", "p. 6 §5"),
                ("LOCK-SENSE never missed an unseated canopy", "p. 6 §5"),
                ("RF 71.3× (LOCK-SENSE, always acts); 2.8× (LOCK-SENSE, distrusts); comparison: task-sheet example, one microswitch, 4.6× (always acts)", "p. 6 Table 3, rows 'Lamp, voice, chime and lap-belt pad (chosen)' and 'Task-sheet example: one microswitch, EFIS message, tone'"),
                ("Figure 5: an alert helps much only when the pilot nearly always acts on it", "p. 7 Figure 5"),
                ("RF is a model estimate; does not count canopy losses or fatal accidents", "p. 6 §5")]),
    dict(key="close", speaker="Speaker 4", sec=27,
         title="LOCK-SENSE adds a warning for the hazard in AD 2025-0156",
         notes=("For EASA, LOCK-SENSE adds an electrical warning against the hazard in AD 2025-0156. "
                "It weighs 0.45 to 0.85 kilograms. It fits any canopy aircraft with one sensor per latch point. "
                "It cannot see a frame failure while the bolts stay locked. So a frame-bond NDT stays the defence. "
                "Next, we measure bolt travel on an aircraft and bench-test 30 sensors. Thank you."),
         trace=[("Electrical warning against the hazard named in AD 2025-0156", "p. 7 §6"),
                ("Senses each bolt where it enters its lug; log keeps the sensed lock state", "p. 7 §6"),
                ("About 0.45 to 0.85 kg and 1.8 W continuous power", "p. 7 §6"),
                ("Fits any canopy aircraft with one sensor per latch point", "p. 7 §6"),
                ("Cannot detect a frame failure while the bolts stay locked (AAIB cause on G-MIIL)", "p. 7 §5"),
                ("One-off NDT of the frame bond stays the defence against the AAIB cause", "p. 7 §6 [29]"),
                ("2 of 13 fault cases give a false green; fault shown at next powered opening, gauge check and handle check cover them", "p. 7 §5"),
                ("Pilot acts on 50 % of alerts (c = 0.5): only 2.0× (alert sets give 1.6× to 2.0×; Figure 5 label "
                 "'2.0× at c = 0.5')", "p. 7 §5, Figure 5"),
                ("Next: measure bolt travel on an aircraft; bench-test 30 sensors over 10 cycles; then vibration, "
                 "temperature, endurance and pilot-response tests", "p. 7 §6")]),
]

QA = [
    ("Why not one microswitch at the pin, as in the task sheet?",
     "One pin cannot see one bolt out. In our model, one microswitch at one pin missed a single bolt out "
     "in 133 345 of 200 000 trials (0.67). The task-sheet set gives 4.6×. Our set gives 71.3× when the pilot "
     "always acts.", "p. 5 Table 1; p. 6 §5, Table 3"),
    ("Why no take-off gate, throttle pawl or engine shut-down?",
     "These act on the engine or the throttle. A fault could take away power in flight. Figure 5 shows that "
     "a gate gives more on paper, but we removed it for safety. LOCK-SENSE only alerts.",
     "p. 5 Table 1 (Barrier); p. 7 Figure 5"),
    ("What if pilots stop trusting the alert?",
     "Then the pilot sets the benefit. With distrust, the chosen set gives about 3× (2.8×). With the "
     "inductive sensor's own false-alert rate (0.14 per 1 000 flights), it gives 5.0×. In taxi, an unlocked canopy gives "
     "only an amber lamp and one chime. Step 1 measures the bolt travel ratio first. At 0.5 mm per mm, "
     "scatter gives about 51 false alerts per 1 000 flights.", "p. 6 Table 3 note; p. 7 Table 4, §5; p. 4 Figure 3"),
    ("Would LOCK-SENSE have saved G-MIIL?",
     "Not against the AAIB cause. The system cannot detect a frame failure while the bolts stay locked. "
     "A one-off NDT of the frame bond stays the defence. But its log keeps the sensed lock state, "
     "so the next investigation has the record that G-MIIL did not have. It cannot prove that the frame was sound.", "p. 3 §1; p. 7 §5, §6"),
    ("How do you know that a sensor fault cannot show 'locked'?",
     "Line monitoring turns an open or a short into 'not locked'. We ran thirteen fault cases. No single "
     "electrical fault gave a false green. Two combined cases did. One is a bolt out with its own sensor stuck ON. "
     "The other is all three sensors rigged early with one wrong gauge. The stuck sensor shows as a fault at the "
     "next powered opening. The step 9 gauge check and the handle check cover the rest. Next, we bench-test 30 sensors over "
     "10 cycles.", "p. 4 §3; p. 7 §5, §6"),
]


# ----------------------------------------------------------------------------- pptx helpers
def duplicate_slide(prs, src):
    """Append a copy of `src` (same layout, all shapes, image relationships re-pointed)."""
    new = prs.slides.add_slide(src.slide_layout)
    for shp in list(new.shapes):
        shp._element.getparent().remove(shp._element)
    rmap = {}
    for rid, rel in src.part.rels.items():
        if rel.reltype.endswith("/notesSlide") or rel.reltype.endswith("/slideLayout"):
            continue
        rmap[rid] = (new.part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref) if rel.is_external
                     else new.part.relate_to(rel.target_part, rel.reltype))
    src_tree, dst_tree = src.shapes._spTree, new.shapes._spTree
    for el in src_tree:
        if el.tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            continue
        dst_tree.append(copy.deepcopy(el))
    bg = src._element.cSld.find(qn("p:bg"))
    if bg is not None:
        new._element.cSld.insert(0, copy.deepcopy(bg))
    for node in new._element.iter():
        for att in (qn("r:embed"), qn("r:link"), qn("r:id")):
            if node.get(att) in rmap:
                node.set(att, rmap[node.get(att)])
    return new


def set_text_keep_format(shape, text):
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    p0.runs[0].text = text
    for r in p0.runs[1:]:
        r.text = ""
    for p in tf.paragraphs[1:]:
        for r in p.runs:
            r.text = ""


def footer(slide, page):
    for g in slide.shapes:
        if g.shape_type == 6:
            for s in g.shapes:
                if s.has_text_frame and s.text_frame.text.strip():
                    t = s.text_frame.text.strip()
                    if "/" in t:
                        set_text_keep_format(s, DATE)
                    elif t.upper() == "TEAM NAME":
                        set_text_keep_format(s, TEAM_FOOTER)
                    elif t.isdigit():
                        set_text_keep_format(s, str(page))


def text(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT, name="txt"):
    """paras: list of paragraphs; each paragraph = list of runs (text, size, bold, color)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.0)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if i:
            p.space_before = Pt(6)
        for (t, size, bold, color) in runs:
            r = p.add_run()
            r.text = t
            r.font.name, r.font.size, r.font.bold = FONT, Pt(size), bold
            r.font.color.rgb = color
    return tb


def rect(slide, x, y, w, h, color, name="rect"):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.name = name
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def title(slide, t):
    text(slide, X0, Y_TITLE, XW, 1.05, [[(t, T_TITLE, True, PURPLE)]], anchor=MSO_ANCHOR.MIDDLE, name="title")


def stat(slide, x, y, w, h, big, label, big_size=T_BIG, label_size=T_BODY, color=PURPLE, bar=MAUVE):
    """Large number with a short label under it; a thin template-mauve bar marks the group."""
    rect(slide, x, y + 0.12, 0.07, h - 0.24, bar, name="bar")
    bh = big_size / 72 * 1.25
    text(slide, x + 0.3, y, w - 0.3, bh, [[(big, big_size, True, color)]], name="big")
    text(slide, x + 0.3, y + bh, w - 0.3, h - bh, [[(label, label_size, False, INK)]], name="label")


def picture(slide, path, x, y, w=None, h=None):
    with Image.open(path) as im:
        ar = im.width / im.height
    if w is None:
        w = h * ar
    if h is None:
        h = w / ar
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w), Inches(h))
    pic.name = "figure"
    return w, h


# ----------------------------------------------------------------------------- figure preparation
def prep_figures():
    """Copy report figures into deck/fig with the white background made transparent (no other pixel change)."""
    out = DECK / "fig"
    out.mkdir(exist_ok=True)
    names = {"F1a": "fig1a_phase.png", "F1b": "fig1b_type.png", "F10": "fig2_sensor.png",
             "P1_phase_logic": "fig3_phase_logic.png", "P2_compliance": "fig5_compliance.png"}

    def clear_white(im):
        arr = np.asarray(im.convert("RGBA")).astype(np.float32)
        m = arr[..., :3].min(axis=2)
        # white -> transparent; near-white anti-alias halo (246..254) -> linear alpha ramp; colours untouched
        ramp = np.clip((255.0 - m) / 9.0, 0.0, 1.0)
        arr[..., 3] = np.where(m >= 246, arr[..., 3] * ramp, arr[..., 3])
        return Image.fromarray(arr.round().astype(np.uint8), "RGBA")

    paths = {}
    for src, dst in names.items():
        clear_white(Image.open(FIGSRC / f"{src}.png")).save(out / dst)
        paths[src] = out / dst
    logo = Image.open(LOGO).convert("RGB")
    gray = logo.convert("L").point(lambda v: 255 if v < 235 else 0)
    box = gray.getbbox()
    pad = 10
    box = (max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, logo.width), min(box[3] + pad, logo.height))
    clear_white(logo.crop(box)).save(out / "team_logo.png")
    paths["logo"] = out / "team_logo.png"
    return paths


# ----------------------------------------------------------------------------- slides
def s_cover(sl, fig):
    for s in sl.shapes:
        if s.has_text_frame:
            t = s.text_frame.text.strip()
            if t == "TEAM NAME":
                set_text_keep_format(s, "TEAM BEETIFUL")
                s.width = Inches(7.6)
                s.text_frame.word_wrap = False
                s.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
            elif t == "Short description":
                tf = s.text_frame
                set_text_keep_format(s, "LOCK-SENSE · EASA challenge")
                p = tf.add_paragraph()
                r0 = tf.paragraphs[0].runs[0]
                r = p.add_run()
                r.text = "A canopy-lock alert retrofit for the Extra NG"
                r.font.name, r.font.size, r.font.bold = r0.font.name, r0.font.size, False
                r.font.color.rgb = PURPLE
                s.width, s.height = Inches(7.6), Inches(1.0)
                tf.word_wrap = True
                for para in tf.paragraphs:
                    para.alignment = PP_ALIGN.LEFT
    picture(sl, fig["logo"], 1.0, 0.75, h=2.75)


def s_problem(sl, fig):
    w, gap, y = 5.6, 0.7, Y_TOP + 0.2
    items = [("184 KIAS", "G-MIIL's canopy broke up in level flight on 2 April 2022."),
             ("0", "lock-state records. AAIB: frame bond. BFU: not fully locked. Nobody can settle it."),
             ("70 mm", "handle gap when locked and when released. The frame edge looks the same too.")]
    for i, (big, lab) in enumerate(items):
        stat(sl, X0 + i * (w + gap), y, w, 3.0, big, lab)
    text(sl, X0, 7.25, XW, 1.2,
         [[("EASA AD 2025-0156: ", T_BODY, True, PURPLE),
           ("a partly locked canopy is the main cause of in-flight openings on this type. "
            "It still has no electrical canopy warning.", T_BODY, False, INK)]], anchor=MSO_ANCHOR.MIDDLE,
         name="band_txt")
    text(sl, X0, 8.75, XW, 0.9,
         [[("Our goal: ", T_MID, True, MAUVE),
           ("fewer unnoticed unlocked take-offs, and a lock-state record.", T_MID, True, PURPLE)]],
         anchor=MSO_ANCHOR.MIDDLE, name="goal")


def s_evidence(sl, fig):
    fw = 6.35
    _, fh = picture(sl, fig["F1a"], X0, Y_TOP, w=fw)
    picture(sl, fig["F1b"], X0 + fw + 0.25, Y_TOP, w=fw)
    xs, ws = 14.55, 4.55
    for i, (big, lab) in enumerate([("241", "investigated canopy and door events"),
                                    ("126", "lock-related"),
                                    ("16", "fatal")]):
        stat(sl, xs, Y_TOP + i * 1.78, ws, 1.65, big, lab)
    text(sl, X0, 9.05, XW, 0.9,
         [[("Every false \u201clocked\u201d indication we found came from one switch: ", T_BODY, True, PURPLE),
           ("on the handle, the drive or one pin (DA40, Pitts, RV-14A).", T_BODY, False, INK)]],
         anchor=MSO_ANCHOR.MIDDLE, name="foot")


def s_trade(sl, fig):
    cols = [(X0, 2.9), (X0 + 3.1, 5.0), (X0 + 8.3, 9.9)]
    rows = [("Sensing point", "Each bolt and the seat", "One pin, the handle or the linkage cannot see one bolt out"),
            ("Sensor type", "Line-monitored inductive", "Snap switch, Hall sensor, bare contact: more false alerts"),
            ("Aural", "Voice, no lead tone", "A lead tone slowed responses"),
            ("Vibration", "Lap-belt pad", "A stick shaker means \u201cstall\u201d; a knob shaker sits on an engine control"),
            ("Barrier", "None: alerts only", "Engine shut-down, take-off gate, throttle pawl: a fault could take away power"),
            ("G3X link", "Unit output into the G3X", "A raw switch reads a short to ground as \u201cclosed\u201d")]
    y = Y_TOP
    for (cx, cw), h in zip(cols, ("Element", "Our choice", "Rejected, and why")):
        text(sl, cx, y, cw, 0.5, [[(h.upper(), T_SMALL, True, MAUVE)]], anchor=MSO_ANCHOR.BOTTOM, name="th")
    y += 0.6
    rh = 0.98
    for i, row in enumerate(rows):
        if row[0] == "Barrier":
            rect(sl, X0 - 0.15, y, XW + 0.3, rh, TINT, name="hl")
        else:
            rect(sl, X0, y, XW, 0.02, RULE, name="rule")
        for j, ((cx, cw), cell) in enumerate(zip(cols, row)):
            style = [(T_BODY, True, PURPLE), (T_BODY, True, INK), (T_BODY, False, INK)][j]
            text(sl, cx, y, cw, rh, [[(cell, *style)]], anchor=MSO_ANCHOR.MIDDLE, name="td")
        y += rh
    rect(sl, X0, y, XW, 0.02, RULE, name="rule")


def s_sensors(sl, fig):
    _, fh = picture(sl, fig["F10"], X0, Y_TOP, w=XW)
    y, w, gap = Y_TOP + fh + 0.35, 5.6, 0.7
    items = [("4", "inductive sensors on the fuselage side. Jettison path unchanged."),
             ("1", "hardware AND: green CANOPY LOCKED only when all four agree."),
             ("0", "single electrical faults gave a false green in our fault runs.")]
    for i, (big, lab) in enumerate(items):
        stat(sl, X0 + i * (w + gap), y, w, Y_BOT - y, big, lab)


def s_logic(sl, fig):
    _, fh = picture(sl, fig["P1_phase_logic"], X0, Y_TOP, w=XW)
    y, w, gap = Y_TOP + fh + 0.35, 5.6, 0.7
    items = [("18 kt", "median pilot action with the lever trigger. rpm trigger: 31 kt."),
             ("38 %", "of headset tones missed under high workload."),
             ("1.5 s", "design response time. 3.0 s is our 95th-percentile margin.")]
    for i, (big, lab) in enumerate(items):
        stat(sl, X0 + i * (w + gap), y, w, Y_BOT - y, big, lab)


def s_retrofit(sl, fig):
    groups = [("1\u20134  Mount", [("1", "Measure bolt travel ratio r", "trip window known first"),
                                   ("2", "Bracket under lug fasteners", "no new holes"),
                                   ("3", "Set sensor gap at full lock", "within 0.3 mm"),
                                   ("4", "Seated sensor on the frame", "jettison forces unchanged")]),
              ("5\u20138  Wire and program", [("5", "Own breaker", "peak load 2.8 W"),
                                              ("6", "One shielded loop per sensor", "shields grounded at unit end"),
                                              ("7", "Connect inputs and alerts", "alerts within 0.5 s"),
                                              ("8", "Load the phase logic", "bench run matches the logic")]),
              ("9\u201312  Test", [("9", "Gauge each bolt", "right 10 times of 10"),
                                   ("10", "Inject faults", "each fault logged"),
                                   ("11", "Engine run, aerobatic flight", "no nuisance alert"),
                                   ("12", "Add to the checklist", "handle, green ON, no G3X alert")])]
    w, gap = 5.6, 0.7
    for gi, (head, steps) in enumerate(groups):
        x = X0 + gi * (w + gap)
        text(sl, x, Y_TOP, w, 0.6, [[(head, T_MID, True, MAUVE)]], anchor=MSO_ANCHOR.BOTTOM, name="gh")
        rect(sl, x, Y_TOP + 0.7, w, 0.04, MAUVE, name="grule")
        y = Y_TOP + 0.95
        for num, act, chk in steps:
            text(sl, x, y, 0.65, 1.3, [[(num, T_BODY, True, MAUVE)]], name="num")
            text(sl, x + 0.65, y, w - 0.65, 1.3,
                 [[(act, T_BODY, True, PURPLE)], [("\u2713 " + chk, T_SMALL, False, INK)]], name="step")
            y += 1.37


def s_results(sl, fig):
    for i, (big, lab) in enumerate([("71×", "LOCK-SENSE, pilot always acts"),
                                    ("2.8×", "LOCK-SENSE, distrusting pilot"),
                                    ("4.6×", "for comparison: task-sheet example (one microswitch), pilot always acts")]):
        stat(sl, X0, Y_TOP + i * 2.0, 5.2, 1.85 if i < 2 else 2.4, big, lab,
             color=PURPLE if i < 2 else INK, bar=MAUVE if i < 2 else RULE)
    fx = 6.3
    fw = 19.2 - fx
    _, fh = picture(sl, fig["P2_compliance"], fx, Y_TOP + 0.1, w=fw)
    text(sl, fx, Y_TOP + fh + 0.35, fw, 1.9,
         [[("Monte Carlo, 200 000 take-offs per case. ", T_SMALL, True, PURPLE),
           ("One microswitch at one pin missed one bolt out in 67 % of trials. "
            "LOCK-SENSE never missed an unseated canopy.", T_SMALL, False, INK)],
          [("Model estimate. It does not count canopy losses or fatal accidents.", T_SMALL, False, INK)]],
         name="note")


def s_close(sl, fig):
    cols = [("Value", ["Senses each bolt at its lug",
                       "Logs the lock state for investigators",
                       "0.45\u20130.85 kg, 1.8 W",
                       "Fits any canopy aircraft: one sensor per latch point"]),
            ("Limits", ["Cannot see a frame failure with the bolts locked (G-MIIL)",
                        "Frame-bond NDT stays the defence",
                        "2 of 13 fault cases give a false green; checks cover them",
                        "Pilot acts on 50 %: only 2.0×"]),
            ("Next step", ["Measure bolt travel on an aircraft",
                           "Bench-test 30 sensors × 10 cycles",
                           "Then vibration, temperature, endurance and pilot-response tests"])]
    w, gap = 5.6, 0.7
    for ci, (head, items) in enumerate(cols):
        x = X0 + ci * (w + gap)
        text(sl, x, Y_TOP, w, 0.6, [[(head, T_MID, True, MAUVE)]], anchor=MSO_ANCHOR.BOTTOM, name="ch")
        rect(sl, x, Y_TOP + 0.7, w, 0.04, MAUVE, name="crule")
        tb = text(sl, x, Y_TOP + 0.95, w, 4.9, [[(it, T_BODY, False, INK)] for it in items], name="col")
        for p in tb.text_frame.paragraphs[1:]:
            p.space_before = Pt(16)
    text(sl, X0, 9.05, XW, 0.9, [[("Thank you. Questions?", T_MID, True, PURPLE)]],
         anchor=MSO_ANCHOR.MIDDLE, name="thanks")


BUILDERS = {"cover": s_cover, "problem": s_problem, "evidence": s_evidence, "trade": s_trade,
            "sensors": s_sensors, "logic": s_logic, "retrofit": s_retrofit, "results": s_results, "close": s_close}


# ----------------------------------------------------------------------------- notes, script, trace
def mmss(s):
    return f"{s // 60}:{s % 60:02d}"


def timeline():
    t, rows = 0, []
    for i, s in enumerate(SLIDES, 1):
        rows.append((i, s, t, t + s["sec"]))
        t += s["sec"]
    return rows, t


def note_text(i, s, t0, t1):
    words = len(s["notes"].split())
    return (f"[{s['speaker']} · {s['sec']} s · {mmss(t0)}\u2013{mmss(t1)} · {words} words]\n"
            f"{s['notes']}")


def write_script(total):
    rows, _ = timeline()
    L = ["# LOCK-SENSE · 4:00 talk script (Team Beetiful, EASA challenge)", "",
         f"Generated by `build_easa_deck.py`. Source of every claim: `{REPORT}` (submitted 5 Nov 2026). "
         "Language: ASD-STE100 style. Target pace: about 2.3 words per second.", "",
         "## Timing", "",
         "| # | Slide | Speaker | Target (s) | Clock | Words | Words/s |",
         "|---|---|---|---:|---|---:|---:|"]
    for i, s, t0, t1 in rows:
        w = len(s["notes"].split())
        L.append(f"| {i} | {s.get('title', 'Cover')} | {s['speaker']} | {s['sec']} | {mmss(t0)}\u2013{mmss(t1)} | "
                 f"{w} | {w / s['sec']:.2f} |")
    per = {}
    for s in SLIDES:
        per[s["speaker"]] = per.get(s["speaker"], 0) + s["sec"]
    L += ["", f"**Total: {total} s = {mmss(total)}** (hard cut at 4:00; {240 - total} s reserve). "
          + " · ".join(f"{k}: {v} s" for k, v in per.items()), "",
          "Hand-overs at slide changes: Speaker 1 \u2192 2 at slide 4; 2 \u2192 3 at slide 6; 3 \u2192 4 at slide 8. The report lists no member names, so the script uses Speaker 1\u20134. "
          "Start the clock on the first word.", "", "## Script", ""]
    for i, s, t0, t1 in rows:
        L += [f"### Slide {i} · {s.get('title', 'Cover')}", "",
              f"*{s['speaker']} · {s['sec']} s · {mmss(t0)}\u2013{mmss(t1)}*", "", s["notes"], ""]
    L += ["## Likely jury questions (answers only from the report)", ""]
    for k, (q, a, src) in enumerate(QA, 1):
        L += [f"**Q{k}. {q}**", "", a, "", f"*Source: {src}.*", ""]
    (DECK / "talk_script.md").write_text("\n".join(L), encoding="utf-8")


def write_trace():
    L = ["# Traceability · Team_Beetiful_EASA_4min.pptx", "",
         f"Every number and claim on the slides and in the speaker notes, mapped to the submitted report "
         f"`D:/Kullanici/Downloads/{REPORT}` (9 pages, PDF created 5 Nov 2026 20:44:09). "
         "Page = printed page number. Generated by `build_easa_deck.py` from the same data that builds the slides.", "",
         "| Slide | Claim / number | Report location |", "|---|---|---|"]
    for i, s in enumerate(SLIDES, 1):
        for claim, loc in s["trace"]:
            L.append(f"| {i} | {claim} | {loc} |")
    L += ["", "Figures on slides: slide 3 = Figure 1 (a, b), p. 3; slide 5 = Figure 2, p. 4; slide 6 = Figure 3, p. 4; "
          "slide 8 = Figure 5, p. 7. Only change: white background set transparent so the template decoration "
          "shows through. Figure 4 is not shown; its two medians (18 kt, 31 kt) are quoted on slide 6.", "",
          "Not from the report: footer date 07/11/2026 (Team Presentations day, Regulations 1.1 §1.1 p.5 and booklet p.8), team logo, template decoration.",
          ""]
    for k, (q, a, src) in enumerate(QA, 1):
        L.append(f"- Q&A {k}: {src}")
    (DECK / "traceability.md").write_text("\n".join(L), encoding="utf-8")


# ----------------------------------------------------------------------------- metrics for the UX audit
def metrics(prs):
    sw, sh = prs.slide_width, prs.slide_height
    print("\nMETRICS (own shapes only; template decoration excluded)")
    allsizes = set()
    for i, sl in enumerate(prs.slides, 1):
        sizes, words, lefts, boxes, issues = set(), 0, set(), [], []
        for s in sl.shapes:
            if s.name in ("txt", "title", "big", "label", "band_txt", "goal", "foot", "th", "td", "gh", "num", "step",
                          "note", "ch", "col", "thanks", "figure", "band", "hl"):
                if s.left < 0 or s.top < 0 or s.left + s.width > sw or s.top + s.height > sh:
                    issues.append(f"off-slide {s.name}")
                if s.top + s.height > Inches(10.05) and s.name != "figure":
                    issues.append(f"below content frame {s.name} ({(s.top + s.height) / 914400:.2f} in)")
                if s.name not in ("band", "hl"):
                    lefts.add(round(s.left / 914400, 2))
                if s.name in ("figure",):
                    boxes.append((s.name, s.left, s.top, s.left + s.width, s.top + s.height))
                if s.has_text_frame:
                    for p in s.text_frame.paragraphs:
                        for r in p.runs:
                            if r.font.size:
                                sizes.add(r.font.size.pt)
                            words += len(r.text.split())
        allsizes |= sizes
        print(f" slide {i}: words on slide {words} · font sizes {sorted(sizes)} · min {min(sizes) if sizes else '-'} pt"
              f" · left axes {len(lefts)} {sorted(lefts)} · figures {len(boxes)} · issues {issues or 0}")
    print(f" deck font sizes (own): {sorted(allsizes)}")


def main():
    if not TEMPLATE.is_file():
        sys.exit(f"template missing: {TEMPLATE}")
    DECK.mkdir(parents=True, exist_ok=True)
    fig = prep_figures()
    shutil.copy2(TEMPLATE, OUT)
    prs = Presentation(str(OUT))
    content_src = prs.slides[1]
    for _ in range(len(SLIDES) - 2):
        duplicate_slide(prs, content_src)
    rows, total = timeline()
    for (i, s, t0, t1), sl in zip(rows, prs.slides):
        if s["key"] != "cover":
            footer(sl, i)
            title(sl, s["title"])
        BUILDERS[s["key"]](sl, fig)
        sl.notes_slide.notes_text_frame.text = note_text(i, s, t0, t1)
    prs.save(str(OUT))
    write_script(total)
    write_trace()
    print(f"wrote {OUT} ({len(prs.slides)} slides), total {total} s = {mmss(total)}")
    for i, s, t0, t1 in rows:
        w = len(s["notes"].split())
        print(f"  {i}. {s['speaker']:<9} {s['sec']:>3} s  {w:>3} words  {w / s['sec']:.2f} w/s  {s.get('title', 'Cover')}")
    metrics(prs)
    if total > 230:
        sys.exit("TOTAL OVER 3:50")


if __name__ == "__main__":
    main()
