#!/usr/bin/env python3
"""Compare the Word template with its LaTeX replica, page by page.

What it does
  1. Renders the Word template (.docx) to PDF with Microsoft Word (COM,
     ExportAsFixedFormat).  The .docx is copied to a temp folder first and
     opened read-only, so the original is never touched.
  2. (optional, --compile) compiles the LaTeX file with latexmk -lualatex.
  3. Renders both PDFs to PNG (default 100 dpi) and writes, per page,
       compare/page_NN.png   Word | LaTeX | overlay
     The overlay shows Word ink in red and LaTeX ink in blue; where both
     agree the ink is dark grey/black.
  4. Measures
       - pixel difference per page: share of pixels whose grey value differs
         by more than 32 (of 255), and the mean absolute grey difference;
       - text: every word (font name, size, x of the first glyph origin,
         baseline y) in both PDFs, matched in reading order; lists words
         whose size differs by > 0.5 pt or whose position differs by > 1 mm.
  5. Writes compare/report.md and compare/text_deviations.csv.

Usage (from this folder, Windows):
  python compare.py                       # render Word, compare example_lorem.pdf
  python compare.py --compile             # also compile example_lorem.tex first
  python compare.py --no-word             # reuse compare/word_template.pdf
  python compare.py --docx X.docx --latex Y.pdf --out compare_y

Needs: PyMuPDF (fitz), Pillow, numpy, pywin32 (only for the Word step).
"""
import argparse
import csv
import difflib
import os
import shutil
import subprocess
import sys
import tempfile

import fitz  # PyMuPDF
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DOCX = os.path.normpath(os.path.join(
    HERE, "..", "rules_and_templates", "originals_2026-11-05",
    "Ideathon_Template_2026.docx"))
MM = 72.0 / 25.4          # 1 mm in pt
POS_TOL = 1.0 * MM        # 1 mm
SIZE_TOL = 0.5            # pt


# ---------------------------------------------------------------- Word step
def render_word(docx, pdf_out):
    import win32com.client  # pywin32
    tmpdir = tempfile.mkdtemp(prefix="ideathon_cmp_",
                              dir=os.environ.get("IDEATHON_TMP", r"D:\tmp_ideathon")
                              if os.path.isdir(r"D:\tmp_ideathon") else None)
    tmp = os.path.join(tmpdir, "template_copy.docx")
    shutil.copyfile(docx, tmp)
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(tmp, ReadOnly=True, AddToRecentFiles=False)
        doc.ExportAsFixedFormat(os.path.abspath(pdf_out), 17)  # 17 = PDF
        doc.Close(0)
    finally:
        word.Quit()
    shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- text
def clean_font(name):
    if "+" in name and len(name.split("+")[0]) == 6:
        name = name.split("+", 1)[1]
    return name


def norm_font(name):
    return "".join(ch for ch in name.lower() if ch not in " -,_")


def words_of_page(page):
    """Words with font, size, first-glyph origin and baseline.

    A word ends at a space character or at a horizontal gap larger than
    0.15 em between glyphs (LaTeX does not write space glyphs)."""
    words = []
    raw = page.get_text("rawdict")
    for block in raw["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                font = clean_font(span["font"])
                size = span["size"]
                cur = None
                prev_x1 = None
                for ch in span["chars"]:
                    c = ch["c"]
                    if c.isspace() or c == "\u00a0":
                        if cur:
                            words.append(cur)
                        cur = None
                        prev_x1 = None
                        continue
                    x0 = ch["origin"][0]
                    if cur is not None and prev_x1 is not None and \
                            x0 - prev_x1 > 0.15 * size:
                        words.append(cur)
                        cur = None
                    if cur is None:
                        cur = {"text": "", "font": font, "size": size,
                               "x": x0, "y": ch["origin"][1],
                               "x1": ch["bbox"][2]}
                    cur["text"] += c
                    cur["x1"] = ch["bbox"][2]
                    prev_x1 = ch["bbox"][2]
                if cur:
                    words.append(cur)
    # reading order: by baseline (rounded), then x
    words.sort(key=lambda w: (round(w["y"] / 2.0), w["x"]))
    return words


def match_words(wa, wb):
    sa = [w["text"] for w in wa]
    sb = [w["text"] for w in wb]
    sm = difflib.SequenceMatcher(a=sa, b=sb, autojunk=False)
    pairs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            pairs += [(wa[i1 + k], wb[j1 + k]) for k in range(i2 - i1)]
    return pairs, sm.ratio()


# ---------------------------------------------------------------- pixels
def render_png(page, dpi):
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img


def side_by_side(img_w, img_l, title):
    w = max(img_w.width, img_l.width)
    h = max(img_w.height, img_l.height)
    a = Image.new("RGB", (w, h), "white"); a.paste(img_w, (0, 0))
    b = Image.new("RGB", (w, h), "white"); b.paste(img_l, (0, 0))
    ga = np.asarray(a.convert("L"), dtype=np.int16)
    gb = np.asarray(b.convert("L"), dtype=np.int16)
    diff = np.abs(ga - gb)
    changed = float((diff > 32).mean() * 100.0)
    mean_abs = float(diff.mean())
    # tolerant variant: a pixel only counts if no pixel within +-1 px in the
    # other image is within 32 grey levels (ignores sub-pixel shifts and
    # anti-aliasing, keeps real differences such as moved or missing ink)
    best = diff.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            sh = np.roll(np.roll(gb, dy, axis=0), dx, axis=1)
            best = np.minimum(best, np.abs(ga - sh))
    changed_tol = float((best > 32).mean() * 100.0)
    # overlay: Word ink -> red channel off, LaTeX ink -> blue channel off
    ov = np.full((h, w, 3), 255, dtype=np.uint8)
    ov[..., 0] = gb.clip(0, 255)          # red stays where LaTeX is white
    ov[..., 1] = np.minimum(ga, gb).clip(0, 255)
    ov[..., 2] = ga.clip(0, 255)          # blue stays where Word is white
    overlay = Image.fromarray(ov, "RGB")
    pad = 40
    canvas = Image.new("RGB", (3 * w + 4 * 10, h + pad), (235, 235, 235))
    for k, im in enumerate((a, b, overlay)):
        canvas.paste(im, (10 + k * (w + 10), pad))
    d = ImageDraw.Draw(canvas)
    try:
        fnt = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        fnt = ImageFont.load_default()
    labels = ["Word", "LaTeX", "overlay: red = Word only, blue = LaTeX only"]
    for k, lab in enumerate(labels):
        d.text((10 + k * (w + 10), 8), f"{title}  {lab}", fill="black", font=fnt)
    return canvas, changed, mean_abs, changed_tol


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docx", default=DEFAULT_DOCX)
    ap.add_argument("--word-pdf", default=None,
                    help="Word PDF to use/produce (default: <out>/word_template.pdf)")
    ap.add_argument("--latex", default=os.path.join(HERE, "example_lorem.pdf"))
    ap.add_argument("--out", default=os.path.join(HERE, "compare"))
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--no-word", action="store_true",
                    help="do not run Word; reuse the existing Word PDF")
    ap.add_argument("--compile", action="store_true",
                    help="compile the .tex next to --latex with latexmk -lualatex first")
    ap.add_argument("--pages", default=None,
                    help="page pairs to compare, e.g. '8:1,9:2' (Word:LaTeX); default 1:1, 2:2, ...")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    word_pdf = args.word_pdf or os.path.join(args.out, "word_template.pdf")

    if not args.no_word or not os.path.exists(word_pdf):
        print("rendering Word PDF:", word_pdf)
        render_word(args.docx, word_pdf)
    if args.compile:
        tex = os.path.splitext(args.latex)[0] + ".tex"
        subprocess.run(["latexmk", "-lualatex", "-interaction=nonstopmode",
                        os.path.basename(tex)], cwd=os.path.dirname(tex) or ".",
                       check=True)

    dw = fitz.open(word_pdf)
    dl = fitz.open(args.latex)
    if args.pages:
        pairs_pg = [tuple(int(x) - 1 for x in p.split(":")) for p in args.pages.split(",")]
    else:
        pairs_pg = [(i, i) for i in range(min(dw.page_count, dl.page_count))]

    rows = []
    devs = []
    fontpairs = {}
    for i, j in pairs_pg:
        pw, pl = dw[i], dl[j]
        iw = render_png(pw, args.dpi)
        il = render_png(pl, args.dpi)
        canvas, changed, mean_abs, changed_tol = side_by_side(iw, il, f"page {i + 1}")
        canvas.save(os.path.join(args.out, f"page_{i + 1:02d}.png"))
        iw.save(os.path.join(args.out, f"page_{i + 1:02d}_word.png"))
        il.save(os.path.join(args.out, f"page_{i + 1:02d}_latex.png"))

        ww, wl = words_of_page(pw), words_of_page(pl)
        pairs, ratio = match_words(ww, wl)
        dxs, dys, dss = [], [], []
        nfont = 0
        nfont_norm = 0
        ndev = 0
        for a, b in pairs:
            dx = b["x"] - a["x"]
            dy = b["y"] - a["y"]
            ds = b["size"] - a["size"]
            dxs.append(abs(dx)); dys.append(abs(dy)); dss.append(abs(ds))
            fontpairs[(a["font"], b["font"])] = fontpairs.get((a["font"], b["font"]), 0) + 1
            fdiff = a["font"] != b["font"]
            fdiff_n = norm_font(a["font"]) != norm_font(b["font"])
            nfont += fdiff
            nfont_norm += fdiff_n
            if abs(dx) > POS_TOL or abs(dy) > POS_TOL or abs(ds) > SIZE_TOL or fdiff_n:
                ndev += 1
                devs.append({"page": f"{i + 1}:{j + 1}", "word": a["text"],
                             "word_font": a["font"], "latex_font": b["font"],
                             "word_size": round(a["size"], 2), "latex_size": round(b["size"], 2),
                             "word_x": round(a["x"], 2), "latex_x": round(b["x"], 2),
                             "word_y": round(a["y"], 2), "latex_y": round(b["y"], 2),
                             "dx_mm": round(dx / MM, 2), "dy_mm": round(dy / MM, 2),
                             "dsize_pt": round(ds, 2)})
        rows.append({
            "page": f"{i + 1}" if i == j else f"{i + 1}:{j + 1}", "changed_pct": changed, "changed_tol": changed_tol, "mean_abs": mean_abs,
            "words_word": len(ww), "words_latex": len(wl), "matched": len(pairs),
            "ratio": ratio,
            "max_dx_mm": max(dxs) / MM if dxs else 0.0,
            "max_dy_mm": max(dys) / MM if dys else 0.0,
            "mean_dx_mm": (sum(dxs) / len(dxs) / MM) if dxs else 0.0,
            "mean_dy_mm": (sum(dys) / len(dys) / MM) if dys else 0.0,
            "max_dsize": max(dss) if dss else 0.0,
            "font_mismatch": nfont, "font_mismatch_norm": nfont_norm, "deviations": ndev})

    with open(os.path.join(args.out, "text_deviations.csv"), "w", newline="",
              encoding="utf-8") as f:
        fields = ["page", "word", "word_font", "latex_font", "word_size", "latex_size",
                  "word_x", "latex_x", "word_y", "latex_y", "dx_mm", "dy_mm", "dsize_pt"]
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        for d in devs:
            wr.writerow(d)

    lines = []
    lines.append("# Word template vs LaTeX replica\n")
    lines.append(f"- Word PDF: `{os.path.relpath(word_pdf, HERE)}` ({dw.page_count} pages)")
    lines.append(f"- LaTeX PDF: `{os.path.relpath(args.latex, HERE)}` ({dl.page_count} pages)")
    lines.append(f"- Raster: {args.dpi} dpi; 'changed' = pixels whose grey value differs by > 32/255")
    lines.append(f"- Text tolerance: size > {SIZE_TOL} pt or position > 1 mm, or different font (after normalising: case, space, hyphen, comma)")
    lines.append("- 'font diff raw' counts words whose PDF font name differs literally (Word writes 'Montserrat Medium', LuaTeX cannot write a space and writes 'Montserrat-Medium')\n")
    lines.append("| page (W:L) | changed px % | changed px % (+-1 px tolerant) | mean abs grey | words W/L | matched | max dx mm | max dy mm | mean dx mm | mean dy mm | max dsize pt | font diff raw | font diff normalised | deviations |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(f"| {r['page']} | {r['changed_pct']:.2f} | {r['changed_tol']:.2f} | {r['mean_abs']:.2f} | "
                     f"{r['words_word']}/{r['words_latex']} | {r['matched']} | "
                     f"{r['max_dx_mm']:.2f} | {r['max_dy_mm']:.2f} | {r['mean_dx_mm']:.2f} | "
                     f"{r['mean_dy_mm']:.2f} | {r['max_dsize']:.2f} | {r['font_mismatch']} | {r['font_mismatch_norm']} | {r['deviations']} |")
    lines.append("\n## Font names (Word -> LaTeX, matched words)\n")
    lines.append("| Word | LaTeX | words |")
    lines.append("|---|---|---:|")
    for (a, b), n in sorted(fontpairs.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {a} | {b} | {n} |")
    if devs:
        lines.append("\n## First 40 deviations (all in text_deviations.csv)\n")
        lines.append("| page | word | font W / L | size W / L | x W / L | y W / L | dx mm | dy mm |")
        lines.append("|---:|---|---|---|---|---|---:|---:|")
        for d in devs[:40]:
            lines.append(f"| {d['page']} | {d['word']} | {d['word_font']} / {d['latex_font']} | "
                         f"{d['word_size']} / {d['latex_size']} | {d['word_x']} / {d['latex_x']} | "
                         f"{d['word_y']} / {d['latex_y']} | {d['dx_mm']} | {d['dy_mm']} |")
    if dw.page_count != dl.page_count:
        lines.append(f"\n**Page count differs: Word {dw.page_count}, LaTeX {dl.page_count}.**")
    rep = "\n".join(lines) + "\n"
    with open(os.path.join(args.out, "report.md"), "w", encoding="utf-8") as f:
        f.write(rep)
    print(rep)


if __name__ == "__main__":
    main()
