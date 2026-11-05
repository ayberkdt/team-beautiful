"""Verify the NCAMP 8552 IM7 Markdown data sheet against the PDF with an independent parser.

The extractor (``extract_ncamp_8552_im7.py``) reads the PDF with PyMuPDF; this
script re-reads it with **pdfplumber** and reads the Markdown with its own small
regex reader (not ``aerokit.materials.composites``), so neither the extractor
nor the package parser checks itself. The PDF is untrusted data; run with::

    python -I scripts/materials/verify_ncamp.py \
        references/materials/ncamp-ncp-rp-2013-015/cmh17-generic-basis-8552-im7-revA.pdf \
        src/aerokit/materials/data/composites/ncamp-8552-im7.md \
        --report references/materials/ncamp_verification_report.md

Checks
------
1. presence: every printed token of the md (``84.42``, ``53.86*``, ``5.91%``,
   ``NA``) is a pdfplumber word on the row's cited PDF page;
2. row order: a pdfplumber text line on that page starts with the row label and
   continues with exactly the row's tokens in column order (merged ``NA``
   cells of the statistics tables are checked as their own line);
3. headers: the caption ``Table N <title>``, the ``Environment`` line (or the
   ``Qual. A01 ... A12 Dataset`` line) in md column order;
4. metadata: SHA-256, page count, caveat sentence; the manually transcribed
   layups (bracket text plus the smaller subscript characters that follow it);
5. sanity (reported, not forced): B <= mean, A <= B per method, CTD >= ETW and
   RTD >= ETW for matrix-dominated properties, and a comparison with
   ``aerokit.materials.library.MATERIALS["IM7-8552"]`` (Hexcel data sheet).

Exit code 1 if any check of 1-4 fails.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

KSI_TO_MPA = 6.894757293168361

ROW_RE = re.compile(r"^\| (\d+) \| ([^|]+?) \| (.+) \|$")
CELL_RE = re.compile(r"^(?:(\d+(?:\.\d+)?)(%)?(?: \[(\*)\])?|NA|—)$")


@dataclass
class MdTable:
    table_id: int
    title: str
    kind: str
    pages: list[int]
    columns: list[str]
    rows: list[tuple[int, str, list[str]]]       # (page, label, printed tokens; "" = nothing printed)
    notes: list[str]


def token(cell: str) -> str:
    """md cell -> token as printed on the page."""
    m = CELL_RE.fullmatch(cell)
    if not m:
        raise ValueError(f"malformed md cell {cell!r}")
    if cell == "—":
        return ""
    if cell == "NA":
        return "NA"
    return m.group(1) + (m.group(2) or "") + (m.group(3) or "")


def read_md(path: Path) -> tuple[dict[str, str], list[tuple[str, ...]], list[MdTable]]:
    text = path.read_text(encoding="utf-8").split("\n")
    end = text.index("---", 1)
    fm = dict(ln.split(": ", 1) for ln in text[1:end])
    tests: list[tuple[str, ...]] = []
    tables: list[MdTable] = []
    section = ""
    cur: MdTable | None = None
    for ln in text[end + 1:]:
        if ln.startswith("## "):
            section = ln[3:]
            cur = None
            if section.startswith("Table "):
                cur = MdTable(int(section.split()[1]), "", "", [], [], [], [])
                tables.append(cur)
            continue
        if section == "Test descriptions" and ln.startswith("| ") and not ln.startswith(("| test ", "|:")):
            tests.append(tuple(c.strip() for c in ln[1:-1].split("|")))
        if cur is None:
            continue
        if ln.startswith("- title: "):
            cur.title = ln[9:]
        elif ln.startswith("- kind: "):
            cur.kind = ln[8:]
        elif ln.startswith("- pdf_page: "):
            cur.pages = [int(p) for p in ln[12:].split(", ")]
        elif ln.startswith("- note: "):
            cur.notes.append(ln[8:])
        elif ln.startswith("| page | row | "):
            cur.columns = [c.strip() for c in ln[1:-1].split("|")][2:]
        elif ROW_RE.match(ln) and not ln.startswith("|---"):
            m = ROW_RE.match(ln)
            if m is None:
                continue
            cells = [c.strip() for c in m.group(3).split("|")]
            if len(cells) != len(cur.columns):
                raise ValueError(f"Table {cur.table_id}: row {m.group(2)!r} has {len(cells)} cells")
            cur.rows.append((int(m.group(1)), m.group(2), [token(c) for c in cells]))
    return fm, tests, tables


# --------------------------------------------------------------------------- pdfplumber side


class Page:
    def __init__(self, page: pdfplumber.page.Page) -> None:
        self.words = page.extract_words(keep_blank_chars=False, use_text_flow=True)
        self.chars = page.chars
        self.text = " ".join((page.extract_text() or "").split())
        self.tokens = Counter(w["text"] for w in self.words)
        lines: list[list[dict[str, object]]] = []
        for w in sorted(self.words, key=lambda w: (float(w["top"]), float(w["x0"]))):
            if lines and abs(float(lines[-1][0]["top"]) - float(w["top"])) <= 3.0:
                lines[-1].append(w)
            else:
                lines.append([w])
        self.lines = [[str(w["text"]) for w in sorted(ln, key=lambda w: float(w["x0"]))] for ln in lines]
        # Overprinted text: inside one line, words sharing an exact baseline form a layer; a layer whose
        # words overlap another layer horizontally cannot be visible text next to it (e.g. clipped cell
        # text). Each such line is also offered without one overlapping layer, and the removal is recorded.
        self.variants: list[tuple[list[str], list[str]]] = []
        for ln in lines:
            layers: dict[float, list[dict[str, object]]] = {}
            for w in ln:
                layers.setdefault(round(float(w["top"]), 1), []).append(w)
            for top, layer in layers.items():
                others = [w for t, ws in layers.items() if t != top for w in ws]
                overlaps = any(min(float(a["x1"]), float(b["x1"])) - max(float(a["x0"]), float(b["x0"])) > 2.0
                               for a in layer for b in others)
                if overlaps:
                    kept = sorted(others, key=lambda w: float(w["x0"]))
                    self.variants.append(([str(w["text"]) for w in kept], [str(w["text"]) for w in layer]))


OVERPRINTS: list[str] = []


def check_row(page: Page, label: str, tokens: list[str], where: str = "") -> bool:
    lab = label.split()
    for ln in page.lines:
        if ln[:len(lab)] == lab and ln[len(lab):] == tokens:
            return True
    for ln, removed in page.variants:
        if ln[:len(lab)] == lab and ln[len(lab):] == tokens:
            OVERPRINTS.append(f"{where}: matched after removing the overprinted word(s) {' '.join(removed)!r}")
            return True
    return False


@dataclass
class Result:
    checked: int = 0
    found: int = 0
    misses: list[str] | None = None

    def add(self, ok: bool, what: str) -> None:
        self.checked += 1
        if ok:
            self.found += 1
        else:
            if self.misses is None:
                self.misses = []
            self.misses.append(what)


def verify(pdf_path: Path, md_path: Path) -> tuple[list[str], bool, dict[str, object]]:
    data = pdf_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    fm, tests, tables = read_md(md_path)
    presence, rows_res, headers, meta = Result(), Result(), Result(), Result()
    with pdfplumber.open(pdf_path) as pdf:
        n_pages = len(pdf.pages)
        cache: dict[int, Page] = {}

        def page(p: int) -> Page:
            if p not in cache:
                cache[p] = Page(pdf.pages[p - 1])
            return cache[p]

        meta.add(fm.get("source_sha256") == sha, f"sha256 md {fm.get('source_sha256')} != pdf {sha}")
        meta.add(fm.get("source_pages") == str(n_pages), f"pages md {fm.get('source_pages')} != pdf {n_pages}")
        meta.add(fm.get("source_bytes") == str(len(data)), "source_bytes")
        cav = re.search(r'"(.+)" \(PDF page (\d+)\)', fm.get("approval_caveat", ""))
        meta.add(bool(cav) and cav is not None and cav.group(1) in page(int(cav.group(2))).text, "approval caveat")
        layups_full_size: list[str] = []
        for t in tests:
            test, layup, pno = t[0], t[2], int(t[5])
            if layup == "—":
                continue
            mm = re.fullmatch(r"(\[[^\]]+\])(\w*)", layup)
            if mm is None:
                meta.add(False, f"layup {layup!r} not parseable")
                continue
            chars = page(pno).chars
            s = "".join(str(c["text"]) for c in chars)
            needle = "layup " + mm.group(1)
            i = s.find(needle)
            ok = False
            while i >= 0 and not ok:
                j = i + len(needle)
                sub = s[j:j + len(mm.group(2))]
                if sub == mm.group(2):
                    small = all(float(chars[k]["size"]) < float(chars[j - 1]["size"]) for k in range(j, j + len(sub)))
                    if not small:
                        layups_full_size.append(f"{test} {layup} (PDF p. {pno})")
                    ok = True
                i = s.find(needle, i + 1)
            meta.add(ok, f"layup {test} {layup} on PDF page {pno}")

        for tab in tables:
            first = page(tab.pages[0])
            cap = " ".join(f"Table {tab.table_id} {tab.title}".split())
            headers.add(cap in first.text, f"Table {tab.table_id}: caption {cap!r} on PDF page {tab.pages[0]}")
            if tab.kind == "stats":
                want = ["Qual.", *tab.columns[1:-1], "Dataset"]
                headers.add(want in first.lines, f"Table {tab.table_id}: header line {want}")
            else:
                envs = [c.split(" / ")[1] for c in tab.columns]
                headers.add(["Environment", *envs] in first.lines, f"Table {tab.table_id}: environment line {envs}")
                for g in dict.fromkeys(c.split(" / ")[0] for c in tab.columns):
                    headers.add(all(w in first.tokens for w in g.split()), f"Table {tab.table_id}: group {g!r}")
            for pno, label, toks in tab.rows:
                pg = page(pno)
                for col, tok in zip(tab.columns, toks, strict=True):
                    if tok:
                        presence.add(pg.tokens[tok] > 0, f"Table {tab.table_id} p{pno} {label} / {col}: {tok}")
                span_na = tab.kind == "stats"
                expected = [t for t in toks if t and not (span_na and t == "NA")]
                rows_res.add(check_row(pg, label, expected, f"Table {tab.table_id} p{pno} row {label!r}"),
                             f"Table {tab.table_id} p{pno}: row {label!r} {expected}")
            if tab.kind == "stats" and any(t == "NA" for _, _, toks in tab.rows for t in toks):
                n_na_cols = len({k for _, _, toks in tab.rows for k, t in enumerate(toks) if t == "NA"})
                rows_res.add(["NA"] * n_na_cols in first.lines,
                             f"Table {tab.table_id}: merged NA line with {n_na_cols} token(s)")
    stats = {"tables": len(tables), "sha": sha, "bytes": len(data), "pages": n_pages,
             "layups_full_size": layups_full_size}
    ok = all(r.misses is None for r in (presence, rows_res, headers, meta))
    lines = report_tables(pdf_path, md_path, stats, presence, rows_res, headers, meta)
    return lines, ok, {**stats, "tables": tables}


def report_tables(pdf_path: Path, md_path: Path, stats: dict[str, object], presence: Result, rows: Result,
                  headers: Result, meta: Result) -> list[str]:
    out = [
        "# Verification report: NCAMP NCP-RP-2013-015 Rev A (Hexcel 8552 IM7) Markdown data sheet",
        "",
        f"- generated: {_dt.datetime.now().replace(microsecond=0).isoformat()} by "
        "`python -I scripts/materials/verify_ncamp.py`",
        f"- PDF: `{pdf_path.as_posix()}`, {stats['bytes']} bytes, SHA-256 `{stats['sha']}`, {stats['pages']} pages",
        f"- data: `{md_path.as_posix()}` ({stats['tables']} tables)",
        "- extractor: PyMuPDF words (`scripts/materials/extract_ncamp_8552_im7.py`); verifier: pdfplumber words, "
        "lines and characters, with its own Markdown reader",
        "",
        "## 1. Every md number on its cited PDF page",
        "",
        "| check | checked | found (pdfplumber) | missing |",
        "|:---|---:|---:|---:|",
        f"| tokens present on the row's page | {presence.checked} | {presence.found} | "
        f"{presence.checked - presence.found} |",
        f"| rows: label + tokens in column order on one line | {rows.checked} | {rows.found} | "
        f"{rows.checked - rows.found} |",
        f"| captions, environment/unit header lines, test headers | {headers.checked} | {headers.found} | "
        f"{headers.checked - headers.found} |",
        f"| metadata (SHA-256, pages, bytes, caveat, manual layups) | {meta.checked} | {meta.found} | "
        f"{meta.checked - meta.found} |",
        "",
        "### Misses",
        "",
    ]
    misses = [m for r in (presence, rows, headers, meta) for m in (r.misses or [])]
    out += [f"- {m}" for m in misses] or ["- none"]
    if OVERPRINTS:
        out += ["", "Overprinted text found by pdfplumber but not part of the visible row (PyMuPDF does not return",
                "it; when this check was written, a 200-dpi rendering of PDF page 40 showed only the md labels,",
                "without '(ANOVA)'):", ""]
        out += [f"- {m}" for m in OVERPRINTS]
    full = stats.get("layups_full_size") or []
    if isinstance(full, list) and full:
        out += ["", "Layup digits printed at full size (not as a subscript), transcribed as printed: "
                + "; ".join(str(x) for x in full) + "."]
    return out


# --------------------------------------------------------------------------- sanity checks


def value(tables: list[MdTable], table_id: int, row_re: str, column: str) -> tuple[float, str] | None:
    tab = next(t for t in tables if t.table_id == table_id)
    rows = [r for r in tab.rows if re.fullmatch(row_re, r[1])]
    if len(rows) != 1 or column not in tab.columns:
        return None
    tok = rows[0][2][tab.columns.index(column)]
    num = tok.rstrip("*%")
    if not re.fullmatch(r"\d+(?:\.\d+)?", num):
        return None
    return float(num), f"T{table_id} p{rows[0][0]} '{rows[0][1]}' {column} = {tok}"


PROPS = {  # name: (basis table, basis group, means table, means group, stats tables by env)
    "F1tu (LT)": (10, "LT", 9, "Longitudinal Tension", {"CTD": 22, "RTD": 23, "ETW": 24}),
    "F1cu (0° from UNC0)": (6, "0° Compression Strength from UNC0 Data", None, None, {}),
    "UNT0": (10, "UNT0", 9, "Unnotched Tension", {"CTD": 25, "RTD": 26, "ETW": 27}),
    "OHT1": (10, "OHT1", 9, "Open Hole Tension", {"CTD": 28, "RTD": 29, "ETW": 30}),
    "UNC0": (5, "UNC0", 4, "UNC0", {"RTD": 17, "ETD": 18, "ETW": 19}),
    "OHC1": (5, "OHC1", 4, "OHC1", {"RTD": 20, "ETW": 21}),
    "SBS": (14, "Short Beam Strength", 13, "Short Beam Strength", {"RTD": 31, "ETW": 32}),
    "F12su (IPS 5% strain)": (14, "In-Plane Shear Strength @ 5% Strain", 13, "In-Plane Shear Strength @ 5% Strain",
                              {"RTD": 35, "ETW": 37}),
    "F12s0.2 (IPS 0.2% offset)": (14, "In-Plane Shear 0.2% Offset Strength", 13,
                                  "In-Plane Shear 0.2% Offset Strength", {"CTD": 33, "RTD": 34, "ETW": 36}),
}
BASIS_ROWS = {
    "qualification": (r"Qual(?:ification|\.) B-(?:Basis|Estimate)(?: or B-Estimate)?", r"Qualification A-Estimate"),
    "pooled": (r"Pooled Data B-basis(?: \(ANOVA\))?", r"Pooled Data A-basis(?: \(ANOVA\))?"),
    "generic": (r"Generic B-basis", r"Generic A-basis"),
}
MATRIX_DOMINATED = ("UNC0", "OHC1", "SBS", "F12su (IPS 5% strain)", "F12s0.2 (IPS 0.2% offset)")


def sanity(tables: list[MdTable]) -> list[str]:
    out = ["", "## 2. Sanity checks (reported, not forced)", ""]
    counts: Counter[str] = Counter()
    viol: list[str] = []
    for name, (bt, bg, mt, mg, st) in PROPS.items():
        btab = next(t for t in tables if t.table_id == bt)
        envs = [c.split(" / ")[1] for c in btab.columns if c.split(" / ")[0] == bg]
        for env in envs:
            col = f"{bg} / {env}"
            means = {
                "generic": value(tables, mt, r"Unit Av(?:g|erage)", f"{mg} / {env}") if mt else None,
                "pooled": value(tables, st[env], "Average", "Pooled") if env in st else None,
                "qualification": value(tables, st[env], "Average", "Qual.") if env in st else None,
            }
            for meth, (brow, arow) in BASIS_ROWS.items():
                b, a = value(tables, bt, brow, col), value(tables, bt, arow, col)
                if b and a:
                    counts["A <= B (same method)"] += 1
                    if not a[0] <= b[0]:
                        viol.append(f"A > B: {name} {env} {meth}: {a[1]} > {b[1]}")
                mean = means[meth]
                if b and mean:
                    counts["B <= mean (same method)"] += 1
                    if not b[0] <= mean[0]:
                        viol.append(f"B > mean: {name} {env} {meth}: {b[1]} > {mean[1]}")
    out += ["Means used: generic -> 'Unit Average'/'Unit Avg' of the unit-means table (each unit weighted",
            "equally, as the report does); pooled -> 'Average' of the pooled dataset; qualification -> 'Average'",
            "of the 'Qual.' column (summary statistics tables).", "",
            "| check | comparisons | violations |", "|:---|---:|---:|"]
    for k in sorted(counts):
        out.append(f"| {k} | {counts[k]} | {sum(1 for v in viol if v.startswith(k.split()[0] + ' >'))} |")
    out += ["", "### Violations", ""] + ([f"- {v}" for v in viol] or ["- none"])

    out += ["", "### Environment ordering of matrix-dominated properties (generic B-basis and mean)", "",
            "| property | pair | generic B (ksi) | mean (ksi) | holds |", "|:---|:---|---:|---:|:---|"]
    for name in MATRIX_DOMINATED:
        bt, bg, mt, mg, _ = PROPS[name]
        btab = next(t for t in tables if t.table_id == bt)
        envs = [c.split(" / ")[1] for c in btab.columns if c.split(" / ")[0] == bg]
        for hi_env in ("CTD", "RTD"):
            if hi_env in envs and "ETW" in envs:
                bh = value(tables, bt, r"Generic B-basis", f"{bg} / {hi_env}")
                bl = value(tables, bt, r"Generic B-basis", f"{bg} / ETW")
                mh = value(tables, mt, r"Unit Av(?:g|erage)", f"{mg} / {hi_env}") if mt else None
                ml = value(tables, mt, r"Unit Av(?:g|erage)", f"{mg} / ETW") if mt else None
                if bh and bl and mh and ml:
                    holds = "yes" if bh[0] >= bl[0] and mh[0] >= ml[0] else "NO"
                    out.append(f"| {name} | {hi_env} >= ETW | {bh[0]:.2f} >= {bl[0]:.2f} | "
                               f"{mh[0]:.4f} >= {ml[0]:.4f} | {holds} |")
    out += ["", "Only the IPS 0.2% offset strength is printed for both CTD and ETW; the other matrix-dominated",
            "properties have no CTD column, so RTD >= ETW is listed as well. Fibre-dominated tension",
            "(UNT0, OHT1) is printed higher at ETW than at CTD in this report (e.g. OHT1 generic B 56.98 vs",
            "41.60 ksi); that is reported, not treated as an error."]
    return out


def library_comparison(tables: list[MdTable]) -> list[str]:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from aerokit.materials import library  # project code, imported after the PDF checks

    rec = library.MATERIALS["IM7-8552"]
    out = ["", "## 3. Comparison with `library.MATERIALS[\"IM7-8552\"]` (Hexcel HexPly 8552 data sheet, 25 °C dry)",
           "", f"Library record source: {rec['source']}; unverified: {'; '.join(rec['unverified'])}.", "",
           "| key | library (MPa) | NCAMP value | NCAMP (MPa) | difference vs library |",
           "|:---|---:|:---|---:|---:|"]

    def row(key: str, ref: tuple[float, str] | None, label: str) -> None:
        if ref is None:
            out.append(f"| {key} | {rec[key] / 1e6:.1f} | {label}: not printed | — | — |")
            return
        mpa = ref[0] * KSI_TO_MPA
        lib = rec[key] / 1e6
        out.append(f"| {key} | {lib:.1f} | {label}: {ref[1]} | {mpa:.1f} | {100 * (mpa - lib) / lib:+.1f} % |")

    row("Xt", value(tables, 9, "Unit Avg", "Longitudinal Tension / RTD"), "LT RTD mean of units")
    row("Xt", value(tables, 23, "Average", "Pooled"), "LT RTD pooled mean")
    row("Xt", value(tables, 9, "HEXCEL", "Longitudinal Tension / RTD"), "LT RTD 'HEXCEL' row (Hexcel product data)")
    row("Xt", value(tables, 10, "Generic B-basis", "LT / RTD"), "LT RTD generic B")
    row("Xc", value(tables, 6, r"Qualification B-Estimate", "0° Compression Strength from UNC0 Data / RTD"),
        "0° compression RTD qualification B-estimate")
    row("Xc", value(tables, 6, "Generic B-basis", "0° Compression Strength from UNC0 Data / RTD"),
        "0° compression RTD generic B")
    row("S12", value(tables, 13, "Unit Avg", "In-Plane Shear Strength @ 5% Strain / RTD"), "IPS 5% strain RTD mean")
    row("S12", value(tables, 14, "Generic B-basis", "In-Plane Shear Strength @ 5% Strain / RTD"),
        "IPS 5% strain RTD generic B")
    row("S12", value(tables, 13, "Unit Avg", "In-Plane Shear 0.2% Offset Strength / RTD"),
        "IPS 0.2% offset RTD mean")
    out += ["", "| key | library value | in NCP-RP-2013-015 Rev A |", "|:---|---:|:---|"]
    for key, unit, scale in (("E1", "GPa", 1e9), ("E2", "GPa", 1e9), ("nu12", "", 1.0), ("G12", "GPa", 1e9),
                             ("Yt", "MPa", 1e6), ("Yc", "MPa", 1e6), ("t_layer", "mm", 1e-3), ("rho", "kg/m³", 1.0)):
        out.append(f"| {key} | {rec[key] / scale:g} {unit} | not reported |")
    out += ["", "Previously unverified library fields: **nu12, G12 and Yc are not provided by this report** (it "
            "prints strengths only: no moduli, Poisson's ratio, transverse strengths, ply thickness or fibre "
            "volume). They remain unverified.",
            "", "The library Xt (2724 MPa) agrees with the 'HEXCEL' row of Table 9 (395 ksi), i.e. both are Hexcel "
            "product data; the NCAMP means are lower. NCAMP tension/compression data are normalized, the "
            "shear data are as measured (report PDF pages 26, 32, 39); the normalization basis is not stated in "
            "this report. The library S12 (120 MPa) is above both NCAMP IPS strengths; the Hexcel value's "
            "definition (strength at 5 % strain or ultimate) is not stated in the library record."]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("md", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args(argv)
    lines, ok, info = verify(args.pdf, args.md)
    tables = info["tables"]
    if not isinstance(tables, list):
        raise TypeError("internal: tables")
    lines += sanity(tables)
    lines += library_comparison(tables)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines[8:16]))
    print(f"report: {args.report}; {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
