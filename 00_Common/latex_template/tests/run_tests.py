#!/usr/bin/env python3
"""Checks of the parts of the class that the lorem-ipsum template does not
exercise.  Run from this folder:  python run_tests.py   (needs lualatex,
PyMuPDF).  Writes results.md.

1. Line breaking.  linebreak_fit.docx / linebreak_holdout.docx are copies of
   the Word template whose body was replaced by 70 / 80 justified Montserrat
   paragraphs of random lorem words (the holdout set also has hyphenated
   words, numbers and brackets); *_word.pdf are Word's PDFs of them.  The
   .tex files hold the same paragraphs.  The script compares every printed
   line (text and page) of the LaTeX PDF with Word's.  The rule constants in
   ideathon2026-linebreak.lua were tuned on the "fit" set; the "holdout" set
   was made afterwards and is an honest test.
2. References / table / figure: compared with
   ../../../02_EASA/submission/Team_Beetiful_EASA_Report.pdf (page 8: the
   reference list; page 5: Table 1; page 4: Figure 2 and its caption).
"""
import difflib
import os
import subprocess
from collections import defaultdict

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
EASA = os.path.normpath(os.path.join(HERE, "..", "..", "..", "02_EASA", "submission",
                                     "Team_Beetiful_EASA_Report.pdf"))


def compile_tex(name):
    """Compile tests/<name>.tex from the class folder (fonts are found via
    the relative path ./fonts/ only when the job runs there)."""
    root = os.path.dirname(HERE)
    r = subprocess.run(["lualatex", "-interaction=nonstopmode", "-output-directory=tests",
                        "tests/" + name + ".tex"], cwd=root, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    log = open(os.path.join(HERE, name + ".log"), encoding="utf-8", errors="replace").read()
    bad = [l for l in log.splitlines() if l.startswith("!") or ".lua:" in l]
    if bad:
        raise SystemExit(f"{name}: errors in log: {bad[:3]}")
    return os.path.join(HERE, name + ".pdf")


def lines(fn, maxsize=12):
    d = fitz.open(fn)
    out = []
    for pno, p in enumerate(d):
        rows = defaultdict(list)
        for b in p.get_text("rawdict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if s["size"] > maxsize:
                        continue
                    for c in s["chars"]:
                        y = c["origin"][1]
                        if y > 760 or y < 95:
                            continue
                        rows[round(y)].append(c)
        for y in sorted(rows):
            cs = sorted(rows[y], key=lambda c: c["origin"][0])
            txt, prev = "", None
            for c in cs:
                if c["c"] == " ":
                    txt += " "
                    prev = None
                    continue
                if prev is not None and c["origin"][0] - prev > 1.6:
                    txt += " "
                txt += c["c"]
                prev = c["bbox"][2]
            # Word's PDF maps the "fi" ligature glyph oddly ("fni i")
            t = " ".join(txt.split()).replace("fni i", "fini")
            out.append((pno + 1, y, t))
    return out


def compare_lines(word_pdf, latex_pdf):
    a, b = lines(word_pdf), lines(latex_pdf)
    sm = difflib.SequenceMatcher(a=[t for _, _, t in a], b=[t for _, _, t in b], autojunk=False)
    same = 0
    same_page = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            same += i2 - i1
            same_page += sum(1 for k in range(i2 - i1) if a[i1 + k][0] == b[j1 + k][0])
    diffs = [(a[i1][2] if i1 < len(a) else "", b[j1][2] if j1 < len(b) else "")
             for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]
    return len(a), len(b), same, same_page, a[-1][0], b[-1][0], diffs


def spans(fn, pno):
    p = fitz.open(fn)[pno]
    out = []
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                out.append((s["origin"][1], s["bbox"][0], s["size"], s["font"], s["text"]))
    return out, p


def main():
    rep = ["# Extra checks (tests/run_tests.py)\n"]
    rep.append("## 1. Line breaking against Word\n")
    rep.append("| set | lines Word | lines LaTeX | identical lines | identical and on the same page | pages W/L |")
    rep.append("|---|---:|---:|---:|---:|---:|")
    details = []
    for name in ("linebreak_fit", "linebreak_holdout"):
        pdf = compile_tex(name)
        na, nb, same, samep, pa, pb, diffs = compare_lines(os.path.join(HERE, name + "_word.pdf"), pdf)
        rep.append(f"| {name} | {na} | {nb} | {same} ({100 * same / na:.1f} %) | {samep} | {pa}/{pb} |")
        for w, l in diffs:
            details.append(f"- {name}: Word `{w[-60:]}` / LaTeX `{l[-60:]}`")
    if details:
        rep.append("\nFirst line of each differing block:\n")
        rep += details

    rep.append("\n## 2. Reference list, table and figure against the EASA report\n")
    pdf = compile_tex("easa_references")
    wa = lines(EASA, 9)
    wa = [x for x in wa if x[0] == 8]
    la = lines(pdf, 9)
    sm = difflib.SequenceMatcher(a=[t for _, _, t in wa[:12]], b=[t for _, _, t in la], autojunk=False)
    m = [(wa[i1 + k], la[j1 + k]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == "equal"
         for k in range(i2 - i1)]
    dy = max(abs(x[1] - y[1]) for x, y in m) if m else float("nan")
    rep.append(f"- References [1]-[5] (EASA page 8): {len(m)} of {min(12, len(la))} printed lines identical; "
               f"max baseline difference {dy:.2f} bp (rounded baselines).")

    pdf = compile_tex("easa_table_figure")
    ws, wp = spans(EASA, 4)
    ls, lp = spans(pdf, 0)
    def table_geo(sp, page):
        cap = [s for s in sp if s[4].startswith("Table 1.")][0][0]
        rules = sorted(round(d["rect"].y0 - cap, 2) for d in page.get_drawings() if d["rect"].width > 60)
        rules = sorted(set(rules))
        rows = sorted(set(round(s[0] - cap, 2) for s in sp if s[2] < 8.5 and abs(s[1] - 51) < 1.5))
        return rules, rows
    wr, wrow = table_geo(ws, wp)
    lr, lrow = table_geo(ls, lp)
    rep.append(f"- Table 1 rules, bp below the caption baseline: Word {wr}, LaTeX {lr}")
    rep.append(f"- Table 1 first-column baselines, bp below the caption baseline: Word {wrow}, LaTeX {lrow}")
    fs, fp = spans(EASA, 3)
    def fig_geo(sp, page, word):
        cap = [s for s in sp if s[4].startswith(word)][0][0]
        imgs = [i["bbox"] for i in page.get_image_info() if i["bbox"][2] - i["bbox"][0] > 400 and i["bbox"][1] > 50]
        bottom = [b[3] for b in imgs if b[3] < cap][-1]
        return round(cap - bottom, 2)
    rep.append(f"- Figure: picture bottom to caption baseline: Word {fig_geo(fs, fp, 'Figure 2.')} bp, "
               f"LaTeX {fig_geo(ls, lp, 'Figure 1.')} bp")
    out = "\n".join(rep) + "\n"
    open(os.path.join(HERE, "results.md"), "w", encoding="utf-8").write(out)
    print(out)


if __name__ == "__main__":
    main()
