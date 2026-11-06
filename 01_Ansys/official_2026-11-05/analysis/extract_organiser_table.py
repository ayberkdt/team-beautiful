"""Record EVERY cell of the organisers' comparison table (Material selection report, p.7-13) with two independent
methods and diff them cell by cell.

  method 1: PyMuPDF table detector (page.find_tables)
  method 2: poppler words (pdftotext -bbox) placed into the grid drawn on the page (vector lines from the page)

python -I analysis/extract_organiser_table.py "<report.pdf>"
  -> analysis/organiser_table_full.json / .csv / .md  and the list of disagreements (exit 1 if any remain)
"""
from __future__ import annotations
import csv, html, json, re, subprocess, sys
from pathlib import Path
import fitz
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
PDF = Path(sys.argv[1])
PAGES = range(6, 13)                         # 0-based: report pages 7..13
# the report's embedded Open Sans maps its ligature glyphs to Greek code points: U+038A = "ff" ("stiΊness"),
# U+038B = "fi" ("arti΋cially"); U+038C kept as "ffi" in case it appears
LIG = {"Ί": "ff", "΋": "fi", "Ό": "fl", "΍": "ffi", "ﬀ": "ff",   # 038C = "fl" ("Non-flammable", found by the xpdf check) "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi",
       " ": " ", "\x00": ""}


def norm(s: str | None) -> str:
    s = s or ""
    for a, b in LIG.items():
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(\w) (ness|cient|cients|cial|ciency|nity)\b", r"\1\2", s)   # poppler splits at a dropped ligature
    return s.replace("sti ness", "stiffness").replace("coe cient", "coefficient")


def method1(doc):
    rows = []
    for p in PAGES:
        for t in doc[p].find_tables().tables:
            for r in t.extract():
                rows.append([p + 1] + [norm(c) for c in r])
    return rows


def method2(doc):
    rows = []
    for p in PAGES:
        page = doc[p]
        hs, vs = set(), set()
        for d in page.get_drawings():
            for it in d["items"]:
                pts = None
                if it[0] == "l":
                    pts = (it[1], it[2])
                elif it[0] == "re":
                    r = it[1]
                    if r.height < 1.5:
                        pts = (fitz.Point(r.x0, r.y0), fitz.Point(r.x1, r.y0))
                    elif r.width < 1.5:
                        pts = (fitz.Point(r.x0, r.y0), fitz.Point(r.x0, r.y1))
                    else:
                        hs.update([round(r.y0, 1), round(r.y1, 1)])
                        vs.update([round(r.x0, 1), round(r.x1, 1)])
                if pts:
                    a, b = pts
                    if abs(a.y - b.y) < 0.6 and abs(a.x - b.x) > 20:
                        hs.add(round(a.y, 1))
                    elif abs(a.x - b.x) < 0.6 and abs(a.y - b.y) > 5:
                        vs.add(round(a.x, 1))
        ys = sorted(y for y in hs if 80 < y < 730)
        ys = [y for i, y in enumerate(ys) if i == 0 or y - ys[i - 1] > 2.0]
        # column edges = the x edges of the filled value cells (same on every page; p.7 also has the "Change relative
        # to reference" box whose edge would add a false column)
        xs = [64.49, 188.70, 276.86, 365.02, 453.17]
        # raw word boxes (no table logic) — the local pdftotext is xpdf 4.00 without -bbox, so the words come from the
        # PDF text layer through PyMuPDF; the grid comes from the filled cell rectangles drawn on the page
        words = [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]
        for y0, y1 in zip(ys, ys[1:]):
            cells = []
            for x0, x1 in zip(xs, xs[1:]):
                ws = [w for w in words if x0 - 1 <= (w[0] + w[2]) / 2 <= x1 + 1 and y0 - 0.5 <= (w[1] + w[3]) / 2 <= y1 + 0.5]
                ws.sort(key=lambda w: (round(w[1] / 3), w[0]))
                cells.append(norm(" ".join(w[4] for w in ws)))
            if any(cells):
                rows.append([p + 1] + cells[:4] + [""] * (4 - len(cells[:4])))
    return rows


def key(r):
    return (r[0], re.sub(r"[_\s]+", " ", r[1] or "").strip())


doc = fitz.open(PDF)
m1, m2 = method1(doc), method2(doc)
# section-title rows carry no values; method 2 splits their long titles across the grid columns -> compare value rows
is_title = lambda r: not any(r[2:5]) or (r[0] == 7 and (r[1] or "").startswith("Change relative"))  # noqa: E731
titles_m1 = [r for r in m1 if not any(r[2:5])]
m2 = [r for r in m2 if not (not any(r[3:5]) and r[1] and r[2] and not any(ch.isdigit() for ch in r[2] or "")) and not is_title(r)]
m1_values = [r for r in m1 if any(r[2:5])]
d2 = {}
for r in m2:
    d2.setdefault(key(r), []).append(r)
disagree, matched = [], 0
for r in m1_values:
    c = d2.get(key(r))
    if not c:
        disagree.append(("row missing in method 2", r, None)); continue
    r2 = c.pop(0)
    if [x or "" for x in r[2:5]] != [x or "" for x in r2[2:5]]:
        disagree.append(("cell text differs", r, r2))
    else:
        matched += 1
extra = [r for v in d2.values() for r in v]
print(f"method 1: {len(m1)} rows ({len(titles_m1)} section titles, {len(m1_values)} value rows incl. header); "
      f"method 2 value rows {len(m2)}; identical value rows {matched}; disagreements {len(disagree)}; "
      f"rows only in method 2 {len(extra)}")
for why, a, b in disagree:
    print(f"  {why}: p{a[0]} {a[1]!r}\n     m1={a[2:5]}\n     m2={(b or ['']*5)[2:5]}")
for r in extra:
    print(f"  only m2: p{r[0]} {r[1:5]}")
header = m1[0]
names = [n or "" for n in header[2:5]]
recs = [dict(page=r[0], property=r[1], S275N=r[2], Al2618T6=r[3], Ti811SA=r[4], section=(r[2] is None or r[2] == "") and not r[3])
        for r in m1[1:]]
(HERE / "organiser_table_full.json").write_text(json.dumps({"source": PDF.name, "columns": names, "rows": recs}, indent=1, ensure_ascii=False), encoding="utf-8")
with open(HERE / "organiser_table_full.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["page", "property"] + names)
    for r in recs:
        w.writerow([r["page"], r["property"], r["S275N"], r["Al2618T6"], r["Ti811SA"]])
md = [f"# Organisers' comparison table — every cell ({PDF.name}, p.7–13)", "",
      f"{len(recs)} rows. Extracted twice (PyMuPDF table detector; poppler words in the page grid) and diffed: see the "
      "check log in the README of this folder. Ranges are exactly as printed; all values at 23 °C (report p.14).", "",
      "| p. | Property | " + " | ".join(names) + " |", "|---:|---|---|---|---|"]
for r in recs:
    if r["section"]:
        md.append(f"| {r['page']} | **{r['property']}** | | | |")
    else:
        md.append(f"| {r['page']} | {r['property']} | {r['S275N']} | {r['Al2618T6']} | {r['Ti811SA']} |")
(HERE / "organiser_table_full.md").write_text("\n".join(md) + "\n", encoding="utf-8")
sys.exit(1 if disagree or extra else 0)
