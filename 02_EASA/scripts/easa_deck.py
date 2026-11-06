"""Build the 4:00 EASA talk as a .pptx from the organisers' template (kit piece 02 → 02_EASA/submission/).

    python 02_EASA/scripts/easa_deck.py

Needs: python-pptx, the organisers' template in 00_Common/rules_and_templates/originals_2026-11-05/, the figures written
by canopy_day.py (C1, C3, C5) and easa_kit.py (K1, K3, K4), and the pptx skill's add_slide.py (duplicates the template's
decorated content slide with all package bookkeeping; path below, override with $env:PPTX_SKILL).
Slide text = claims of 02_talk_4min.md; the spoken text goes into the speaker notes, not onto the slides.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
EASA = ROOT / "02_EASA"
TEMPLATE = ROOT / "00_Common" / "rules_and_templates" / "originals_2026-11-05" / "Ideathon Template 2026.pptx.pptx"
OUT = EASA / "submission" / "EASA_LOCK-SENSE_4min.pptx"
SKILL = Path(os.environ.get("PPTX_SKILL", r"C:\Users\ayber\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc"
             r"\local-agent-mode-sessions\skills-plugin\e8eba8c6-dc22-4385-919d-0d5b82addb98"
             r"\446231bc-08e2-4318-a4b1-c62b4b719eae\skills\pptx"))
TEAM, DATE = "Team Beetiful", "06/11/2026"     # EASA slot on Friday 6 Nov (doc 23 checklist)

FIG = {"C1": EASA / "outputs" / "day" / "C1_missed_alert_by_architecture.png", "C3": EASA / "outputs" / "day" / "C3_cry_wolf.png",
       "C5": EASA / "outputs" / "day" / "C5_lock_related_by_phase.png", "K1": EASA / "outputs" / "kit" / "K1_concept_ladder.png",
       "K3": EASA / "outputs" / "kit" / "K3_retrofit_process.png",
       "K4": EASA / "outputs" / "kit" / "K4_lock_sense_architecture.png"}

SLIDES = [  # title (claim), visual spec, caption, notes key in 02_talk_4min.md
    ("Closed is not locked", ("cards",), None, "S1 · slide 1"),
    ("Openings come early, on every type, and a door switch sees nothing", ("two", "C5", "C1"),
     "Left: 126 lock-related of 241 investigated openings, by phase. Right: missed-alert probability by architecture.",
     "S1 · slide 2"),
    ("LOCK-SENSE: green must be earned", ("one", "K4"),
     "Quiet in taxi with the canopy open · throttle forward unlocked: red + voice + shaker + ground-only gate · "
     "no engine shut-down", "S2 · slide 3"),
    ("1 900× if pilots act, 3× if they stop trusting it", ("one", "C3"),
     "Nuisance budget R-3: false alerts ≤ 1/10 of the hazard rate · 13 injected faults: only 2 double faults give a false green",
     "S3 · slide 4"),
    ("Twelve steps to fit the alert", ("one", "K3"),
     "Every block ends with a test the next block depends on · G1000 discrete or standalone unit", "S3/S4 · slide 5"),
    ("Record the lock now, remove the omission next", ("one", "K1"),
     "The unit logs the lock state · first step: bench test of the sensor switching scatter (≥ 30 sensors × 10 cycles)",
     "S4 · slide 6"),
]
CARDS = [("G-MIIL: three bodies, two stories", ["AAIB: inadequate bonding → fatigue cracks → break-up at 184\u00a0KIAS",
                                                "BFU (State of Design): most probably not completely locked",
                                                "EASA AD 2025-0156: openings \u201cin most cases\u201d from a partially or "
                                                "improperly locked canopy"]),
         ("What nobody could prove", ["Nothing recorded whether it was locked",
                                      "The pilot was sure he had locked it",
                                      "Handle at 70\u00a0mm both locked and released: visual and handle check both missable"])]


def notes() -> dict[str, str]:
    t = (EASA / "kit" / "02_talk_4min.md").read_text(encoding="utf-8")
    sec = t.split("## Spoken text")[1].split("## Backup")[0]
    out = {}
    for p in sec.split("\n\n"):
        m = re.match(r"\*\*(.+?)\((\d+) s\)\.\*\*\s*(.*)", p, re.S)
        if m:
            out[m.group(1).strip()] = f"[{m.group(2)} s] " + " ".join(m.group(3).split())
    return out


def duplicate(n: int) -> None:
    script = SKILL / "scripts" / "add_slide.py"
    if not script.is_file():
        sys.exit(f"pptx skill not found at {SKILL} (set $env:PPTX_SKILL)")
    for i in range(n):
        last = f"slide{2 + i}.xml"
        r = subprocess.run([sys.executable, str(script), str(OUT), "slide2.xml", "--after", last, "-o", str(OUT)],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stdout + r.stderr)


def set_runs(shape, text: str) -> None:
    """Replace the text of a template text frame keeping its first run's formatting."""
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    if p0.runs:
        p0.runs[0].text = text
        for r in p0.runs[1:]:
            r.text = ""
    for p in tf.paragraphs[1:]:
        for r in p.runs:
            r.text = ""


def footer(slide, page: int) -> None:
    for g in slide.shapes:
        if g.shape_type == 6:      # group
            for s in g.shapes:
                if s.has_text_frame and s.text_frame.text.strip():
                    txt = s.text_frame.text.strip()
                    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", txt):
                        set_runs(s, DATE)
                    elif txt.upper() == "TEAM NAME":
                        set_runs(s, TEAM)
                    elif txt.isdigit():
                        set_runs(s, str(page))


def build() -> Path:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.util import Inches, Pt

    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE, OUT)
    duplicate(len(SLIDES) - 1)
    prs = Presentation(str(OUT))
    nts = notes()
    ink, muted = RGBColor(0x1F, 0x1F, 0x1F), RGBColor(0x4D, 0x4D, 0x4D)

    # cover
    cover = prs.slides[0]
    for s in cover.shapes:
        if s.has_text_frame:
            t = s.text_frame.text.strip()
            if t in ("TEAM NAME", "Short description"):
                set_runs(s, TEAM if t == "TEAM NAME" else "EASA challenge · LOCK-SENSE")
                s.width = Inches(7.0)                      # white area of the cover ends near x = 9.5 in
                s.text_frame.word_wrap = False
                for para in s.text_frame.paragraphs:
                    para.alignment = PP_ALIGN.LEFT
    cover.notes_slide.notes_text_frame.text = "Cover. Start the clock on the first word of slide 2."

    def text_box(slide, x, y, w, h, text, size, bold=False, color=ink):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.text = text
        for p in tf.paragraphs:
            for r in p.runs:
                r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(size), bold, color, "Calibri"
        return tb

    for i, (title, spec, caption, key) in enumerate(SLIDES):
        sl = prs.slides[1 + i]
        footer(sl, i + 2)
        text_box(sl, 1.0, 2.3, 18.0, 0.9, title, 36, bold=True)      # below the template's top-left "POWERED BY" pill
        top, bottom = 3.35, 9.5 if caption else 10.1
        if spec[0] == "one":
            h = bottom - top
            w = h / 0.55
            if w > 18.0:
                w, h = 18.0, 18.0 * 0.55
            sl.shapes.add_picture(str(FIG[spec[1]]), Inches((20 - w) / 2), Inches(top), Inches(w), Inches(h))
        elif spec[0] == "two":
            w = 8.8
            h = w * 0.55
            for k, x in ((spec[1], 1.0), (spec[2], 10.2)):
                sl.shapes.add_picture(str(FIG[k]), Inches(x), Inches(top + 0.4), Inches(w), Inches(h))
        else:   # two text cards
            for j, (head, lines) in enumerate(CARDS):
                x = 1.0 + j * 9.25
                card = sl.shapes.add_shape(1, Inches(x), Inches(3.5), Inches(8.75), Inches(4.9))
                card.fill.solid()
                card.fill.fore_color.rgb = RGBColor(0xF2, 0xF2, 0xF2)
                card.line.fill.background()
                card.shadow.inherit = False
                text_box(sl, x + 0.4, 3.8, 7.95, 0.8, head, 28, bold=True)
                text_box(sl, x + 0.4, 4.8, 7.95, 4.6, "\n\n".join(lines), 22, color=muted)
        if caption:
            text_box(sl, 1.0, 9.62, 18.0, 0.7, caption, 18, color=muted)
        sl.notes_slide.notes_text_frame.text = nts.get(key, "")
    prs.save(str(OUT))
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"wrote {p.relative_to(ROOT).as_posix()} ({len(SLIDES) + 1} slides)")
