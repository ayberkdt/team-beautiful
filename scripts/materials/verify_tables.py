"""Re-open MIL-HDBK-5J and verify every number written to the material Markdown files.

Run from the project root (the PDF is untrusted input, so use ``-I``)::

    python -I scripts/materials/verify_tables.py \
        references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf \
        --data src/aerokit/materials/data \
        --typical src/aerokit/materials/library.py \
        --report references/materials/verification_report.md

Checks (deterministic; the report lists every miss):

1. Presence: every numeric cell of every md design table, and every
   Ramberg-Osgood n / yield value, must occur as a number on the cited PDF
   page, by two text extractors: pdfplumber (pdfminer; independent of the
   extractor, which uses PyMuPDF) and PyMuPDF ``get_text``.
2. Geometry (pdfplumber words): for each md row (= one source column) the
   printed mechanical values (strengths, elongation; the spanned elastic and
   physical constants excluded) must be found as pdfplumber words lying in one
   column of the page (centre within 6 pt across the table) in strictly
   increasing row order. This catches values attached to the wrong column or
   shuffled between rows, which a presence check cannot.
3. Printed page number and SHA-256 of the PDF match the md metadata.
4. Sanity: Fty <= Ftu; Fsu < Ftu; Fbry <= Fbru; e/D=1.5 <= e/D=2.0;
   A <= B and A <= S for the same table/product/thickness (A = min(T99, S),
   B = T90; PDF pages 1415 and 1684); B vs S is only reported (no rule);
   plausible E, G, μ, ω; G vs E/(2(1+μ)); elongation 1-30 %.
5. Comparison with the Aluminum Association typical values in the typical-value table
   (hesap/malzeme.py, since moved to src/aerokit/materials/library.py)
   (read with ``ast``; the file is not imported or modified): design allowables
   should be at or below typical values.

Exit code 1 if any md number is missing from its page, a geometry check fails,
or metadata disagree.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import fitz
import pdfplumber

NUM = re.compile(r"(?<![\d.])(?:\d+\.\d+|\.\d+|\d+)(?![\d])")
WORD_NUM = re.compile(r"^(\d+(?:\.\d+)?|\.\d+)[a-z]{0,2}[,;]?$")
KSI_TO_PA = 1000.0 * 4.4482216152605 / 0.0254**2
PHYSICAL = ("E ", "Ec ", "G ", "μ", "ω")


@dataclass
class MdRow:
    file: str
    table: str
    page: int
    printed: str
    col: int
    attrs: dict[str, str]
    values: dict[str, str]  # header -> cell text


def read_md_tables(path: Path) -> tuple[dict[str, str], list[MdRow], list[tuple[str, int, str, str, str]]]:
    """Independent minimal reader (does not use aerokit): front matter, table rows, RO rows."""
    text = path.read_text(encoding="utf-8").split("\n")
    fm: dict[str, str] = {}
    i = 1
    while text[i] != "---":
        k, _, v = text[i].partition(": ")
        fm[k] = v
        i += 1
    rows: list[MdRow] = []
    ro: list[tuple[str, int, str, str, str]] = []
    table = fig = ""
    page = 0
    printed = ""
    header: list[str] = []
    for ln in text[i + 1:]:
        if ln.startswith("## Table "):
            table, fig, header = ln[9:], "", []
        elif ln.startswith("### Figure "):
            fig, table, header = ln[11:], "", []
        elif ln.startswith(("## ", "### ")):
            table = fig = ""
            header = []
        elif ln.startswith("- pdf_page: "):
            page = int(ln[12:])
        elif ln.startswith("- printed_page: "):
            printed = ln[16:]
        elif ln.startswith("|") and (table or fig):
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if not header:
                header = cells
            elif set("".join(cells)) <= set(":- "):
                continue
            elif table:
                attrs = {h: c for h, c in zip(header, cells, strict=True) if not re.match(r"^(F|e |e$|E|G|μ|ω)", h)}
                vals = {h: c for h, c in zip(header, cells, strict=True) if h not in attrs}
                rows.append(MdRow(path.name, table, page, printed, int(cells[0]), attrs, vals))
            else:
                ro.append((fig, page, cells[0], cells[1], cells[2]))
    return fm, rows, ro


def number_of(cell: str) -> str:
    m = re.match(r"^(\d+(?:\.\d+)?|\.\d+)", cell)
    return m.group(1) if m else ""


class PlumberPage:
    """pdfplumber words of a page as (number, across, down) in table coordinates."""

    def __init__(self, page: pdfplumber.page.Page) -> None:
        rotated = sum(1 for c in page.chars if not c["upright"]) > len(page.chars) / 2
        if rotated:
            words = page.extract_words(line_dir_rotated="ltr", char_dir_rotated="btt")
        else:
            words = page.extract_words()
        self.text_numbers: set[str] = set()
        self.words: list[tuple[str, float, float]] = []
        h = float(page.height)
        for w in words:
            self.text_numbers.update(NUM.findall(w["text"]))
            m = WORD_NUM.match(w["text"])
            if not m:
                continue
            xc = (float(w["x0"]) + float(w["x1"])) / 2
            yc = (float(w["top"]) + float(w["bottom"])) / 2
            if w.get("upright", True):
                self.words.append((m.group(1), xc, yc))
            else:
                self.words.append((m.group(1), h - yc, xc))

    def column_sequence_found(self, seq: list[str], tol: float = 6.0) -> bool:
        for v0, c0, r0 in self.words:
            if v0 != seq[0]:
                continue
            r_prev, ok = r0, True
            for v in seq[1:]:
                nxt = [r for (x, c, r) in self.words if x == v and abs(c - c0) <= tol and r > r_prev + 1.0]
                if not nxt:
                    ok = False
                    break
                r_prev = min(nxt)
            if ok:
                return True
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--typical", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

    pdf_bytes = a.pdf.read_bytes()
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    doc = fitz.open(a.pdf)
    plumber = pdfplumber.open(a.pdf)
    cache_pl: dict[int, PlumberPage] = {}
    cache_mu: dict[int, set[str]] = {}

    def pl(p: int) -> PlumberPage:
        if p not in cache_pl:
            cache_pl[p] = PlumberPage(plumber.pages[p - 1])
        return cache_pl[p]

    def mupdf_nums(p: int) -> set[str]:
        if p not in cache_mu:
            cache_mu[p] = set(NUM.findall(doc[p - 1].get_text()))
        return cache_mu[p]

    files = sorted(f for f in a.data.glob("*.md") if f.name != "index.md")
    checked = found_pl = found_mu = 0
    misses: list[str] = []
    meta_issues: list[str] = []
    all_rows: list[MdRow] = []
    ro_checked = ro_found = 0
    for f in files:
        fm, rows, ro = read_md_tables(f)
        all_rows.extend(rows)
        if fm.get("source_sha256") != sha:
            meta_issues.append(f"{f.name}: source_sha256 differs from the PDF")
        if fm.get("material") != f.stem:
            meta_issues.append(f"{f.name}: front matter material {fm.get('material')!r} != file stem")
        for r in rows:
            for h, c in r.values.items():
                v = number_of(c)
                if not v:
                    continue
                checked += 1
                in_pl = v in pl(r.page).text_numbers
                in_mu = v in mupdf_nums(r.page)
                found_pl += in_pl
                found_mu += in_mu
                if not (in_pl and in_mu):
                    misses.append(f"{f.name} Table {r.table} p.{r.page} col {r.col} {h} = {v} "
                                  f"(pdfplumber {'yes' if in_pl else 'NO'}, PyMuPDF {'yes' if in_mu else 'NO'})")
        for fig, page, curve, n, y in ro:
            for v in (n, y):
                if v == "—":
                    continue
                ro_checked += 1
                ok = v in pl(page).text_numbers and v in mupdf_nums(page)
                ro_found += ok
                if not ok:
                    misses.append(f"{f.name} Figure {fig} p.{page} n({curve}) value {v} not found")

    seen_pages: dict[int, str] = {r.page: r.printed for r in all_rows}
    for p, printed in sorted(seen_pages.items()):
        foot = [w[4] for w in doc[p - 1].get_text("words") if w[1] > 0.9 * doc[p - 1].rect.height]
        if printed not in foot:
            meta_issues.append(f"PDF page {p}: md printed_page {printed!r} not in page footer {foot}")

    # geometry check on unique source columns
    uniq_rows = {(r.table, r.col): r for r in all_rows}
    geo_total = geo_ok = 0
    geo_fail: list[str] = []
    for (table, col), r in sorted(uniq_rows.items()):
        seq = [number_of(c) for h, c in r.values.items() if not h.startswith(PHYSICAL) and number_of(c)]
        if not seq:
            continue
        geo_total += 1
        if pl(r.page).column_sequence_found(seq):
            geo_ok += 1
        else:
            geo_fail.append(f"Table {table} p.{r.page} col {col}: {' '.join(seq)}")
    phys_total = 0
    phys_fail: list[str] = []
    for (table, col), r in sorted(uniq_rows.items()):
        seq = [number_of(c) for h, c in r.values.items() if h.startswith(PHYSICAL) and number_of(c)]
        if seq:
            phys_total += 1
            if not all(v in pl(r.page).text_numbers for v in seq):
                phys_fail.append(f"Table {table} p.{r.page} col {col}: {' '.join(seq)}")

    # sanity checks
    sanity: list[str] = []
    counts: dict[str, int] = defaultdict(int)

    def num(r: MdRow, h: str) -> float | None:
        v = number_of(r.values.get(h, ""))
        return float(v) if v else None

    fam_of = {(r.table, r.col): r.file.split("-")[0] for r in all_rows}
    for key, r in uniq_rows.items():
        tag = f"Table {r.table} p.{r.page} col {r.col} ({r.attrs.get('basis')}, t={r.attrs.get('thickness (in.)', '')})"
        for d in ("", " L", " LT", " ST", " T"):
            tu, ty = num(r, f"Ftu{d} (ksi)"), num(r, f"Fty{d} (ksi)")
            if tu is not None and ty is not None:
                counts["Fty <= Ftu"] += 1
                if ty > tu:
                    sanity.append(f"{tag}: Fty{d} {ty} > Ftu{d} {tu}")
        su = num(r, "Fsu (ksi)")
        tus = [x for x in (num(r, "Ftu L (ksi)"), num(r, "Ftu LT (ksi)"), num(r, "Ftu (ksi)")) if x is not None]
        if su is not None and tus:
            counts["Fsu < Ftu"] += 1
            if su >= min(tus):
                sanity.append(f"{tag}: Fsu {su} >= Ftu {min(tus)}")
        for ed in ("1.5", "2.0"):
            bu, by = num(r, f"Fbru e/D={ed} (ksi)"), num(r, f"Fbry e/D={ed} (ksi)")
            if bu is not None and by is not None:
                counts["Fbry <= Fbru"] += 1
                if by > bu:
                    sanity.append(f"{tag}: Fbry(e/D={ed}) {by} > Fbru {bu}")
        for p in ("Fbru", "Fbry"):
            x15, x20 = num(r, f"{p} e/D=1.5 (ksi)"), num(r, f"{p} e/D=2.0 (ksi)")
            if x15 is not None and x20 is not None:
                counts["bearing e/D=1.5 <= e/D=2.0"] += 1
                if x15 > x20:
                    sanity.append(f"{tag}: {p}(1.5) {x15} > {p}(2.0) {x20}")
        ranges = {"al": ((9.0, 11.5), (3.3, 4.4), (0.095, 0.105)),
                  "steel": ((27.0, 31.0), (10.0, 12.0), (0.27, 0.30)),
                  "ss": ((27.0, 31.0), (10.0, 12.0), (0.27, 0.30)),
                  "ti": ((15.0, 17.5), (5.8, 7.0), (0.155, 0.165)),
                  "inconel": ((27.0, 31.0), (10.0, 12.0), (0.29, 0.31))}[fam_of[key]]
        E, G, mu, rho = num(r, "E (10³ ksi)"), num(r, "G (10³ ksi)"), num(r, "μ"), num(r, "ω (lb/in.³)")
        for name, v, (lo, hi) in (("E", E, ranges[0]), ("G", G, ranges[1]), ("ω", rho, ranges[2])):
            if v is not None:
                counts[f"{name} in plausible range"] += 1
                if not lo <= v <= hi:
                    sanity.append(f"{tag} [{r.file}]: {name} = {v} outside plausible {lo}-{hi}")
        if mu is not None:
            counts["μ in 0.25-0.36"] += 1
            if not 0.25 <= mu <= 0.36:
                sanity.append(f"{tag}: μ = {mu} outside 0.25-0.36")
        if E is not None and G is not None and mu is not None:
            counts["G within 5 % of E/(2(1+μ))"] += 1
            g_iso = E / (2 * (1 + mu))
            if abs(G - g_iso) / g_iso > 0.05:
                sanity.append(f"{tag}: G {G} vs E/(2(1+μ)) = {g_iso:.2f} differs by more than 5 %")
        for h, c in r.values.items():
            if h.startswith("e "):
                v = number_of(c)
                if v:
                    counts["elongation 1-30 %"] += 1
                    if not 1 <= float(v) <= 30:
                        sanity.append(f"{tag}: elongation {v} % implausible")

    groups: dict[tuple[str, ...], dict[str, MdRow]] = defaultdict(dict)
    for r in uniq_rows.values():
        gkey = (r.table, r.attrs.get("alloy", ""), r.attrs.get("form", ""),
                r.attrs.get("temper", r.attrs.get("condition", "")), r.attrs.get("specification", ""),
                r.attrs.get("thickness (in.)", ""))
        if r.attrs["basis"] in groups[gkey]:
            sanity.append(f"duplicate basis {r.attrs['basis']} for {gkey}")
        groups[gkey][r.attrs["basis"]] = r
    b_vs_s: list[str] = []
    for gkey, by_basis in groups.items():
        for lo_b, hi_b, must in (("A", "B", True), ("A", "S", True), ("B", "S", False)):
            if lo_b in by_basis and hi_b in by_basis:
                ra, rb = by_basis[lo_b], by_basis[hi_b]
                for h in ra.values:
                    if not h.startswith("F"):
                        continue
                    va, vb = num(ra, h), num(rb, h)
                    if va is None or vb is None:
                        continue
                    counts[f"{lo_b} <= {hi_b} (same table/product/thickness)"] += 1
                    if va > vb:
                        msg = f"Table {gkey[0]} {gkey[2]} {gkey[3]} t={gkey[5]}: {h} {lo_b}={va} > {hi_b}={vb}"
                        (sanity if must else b_vs_s).append(msg)

    tree = ast.parse(a.typical.read_text(encoding="utf-8"))
    typ: dict[str, dict[str, object]] = {}
    names = ("MALZEMELER", "MATERIALS")  # hesap/malzeme.py, renamed aerokit/materials/library.py
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            typ = ast.literal_eval(node.value)
    if not typ:
        raise SystemExit(f"no MALZEMELER/MATERIALS dict in {a.typical}")
    mapping = {"7075-T6": ["al-7075-t6.md", "al-7075-t651.md"], "6061-T6": ["al-6061-t6.md", "al-6061-t651.md"],
               "2024-T351": ["al-2024-t351.md"], "Ti-6Al-4V": ["ti-6al-4v-annealed.md"]}
    typ_lines: list[str] = []
    typ_findings: list[str] = []
    for tkey, fnames in mapping.items():
        t = typ[tkey]
        for prop in ("Ftu", "Fty"):
            tv = float(t[prop]) / 1e6  # type: ignore[arg-type]
            vals = []
            for r in {(r.table, r.col, r.file): r for r in all_rows if r.file in fnames}.values():
                for h in r.values:
                    if re.fullmatch(prop + r"(?: (?:L|LT|T))? \(ksi\)", h):
                        v = num(r, h)
                        if v is not None:
                            vals.append((v * KSI_TO_PA / 1e6, r, h))
            above = [x for x in vals if x[0] > tv + 1.0]
            equal = [x for x in vals if tv < x[0] <= tv + 1.0]  # same ksi value, MPa rounding
            if vals:
                mx = max(vals, key=lambda x: x[0])
                desc = (f"{mx[0]:.1f} ({mx[1].file} Table {mx[1].table} col {mx[1].col}, "
                        f"{mx[1].attrs.get('basis')}, {mx[2]})")
            else:
                desc = "—"
            typ_lines.append(f"| {tkey} | {prop} | {tv:.0f} | {len(vals)} | {desc} | {len(above)} | {len(equal)} |")
            for v, r, h in above + equal:
                tag = "(within 1 MPa) " if (v, r, h) in equal else ""
                typ_findings.append(f"{tag}{tkey} typical {prop} {tv:.0f} MPa < allowable {v:.1f} MPa ({r.file} Table "
                                    f"{r.table} col {r.col} basis {r.attrs.get('basis')} {h} "
                                    f"t={r.attrs.get('thickness (in.)')})")
        E_typ = float(t["E"]) / 1e9  # type: ignore[arg-type]
        Es = sorted({v for v in (num(r, "E (10³ ksi)") for r in all_rows if r.file in fnames) if v is not None})
        typ_lines.append(f"| {tkey} | E (both typical) | {E_typ * 1e3:.0f} | {len(Es)} | "
                         + ", ".join(f"{e} ×10³ ksi = {e * 1e3 * KSI_TO_PA / 1e6:.0f}" for e in Es) + " | — | — |")

    now = dt.datetime.now().isoformat(timespec="seconds")
    n_design_miss = sum(1 for m in misses if " Figure " not in m)
    out = [
        "# Verification report: MIL-HDBK-5J material Markdown files",
        "",
        f"- generated: {now} by `python -I scripts/materials/verify_tables.py`",
        f"- PDF: `{a.pdf.as_posix()}`, {len(pdf_bytes)} bytes, SHA-256 `{sha}`, {doc.page_count} pages",
        f"- data: `{a.data.as_posix()}` ({len(files)} material files, {len(uniq_rows)} unique source columns)",
        "",
        "## 1. Presence of every md number on the cited PDF page",
        "",
        "| check | checked | found (pdfplumber) | found (PyMuPDF) | missing (either) |",
        "|:---|---:|---:|---:|---:|",
        f"| design-table cells | {checked} | {found_pl} | {found_mu} | {n_design_miss} |",
        f"| Ramberg-Osgood n / 0.2% yield | {ro_checked} | {ro_found} (both) | {ro_found} (both) | "
        f"{ro_checked - ro_found} |",
        "",
        "Cells are counted per material file; a source column shared by two tempers (\"T6 and T62\") is",
        "counted in both files.",
        "",
        "### Misses",
        "",
    ] + ([f"- {m}" for m in misses] or ["- none"]) + [
        "",
        "## 2. Geometry check (pdfplumber word positions)",
        "",
        f"- source columns with mechanical values: {geo_total}; values found in one page column in row order: "
        f"{geo_ok}; failed: {len(geo_fail)}",
        f"- source columns with elastic/physical constants (spanned cells, presence only): {phys_total}; "
        f"failed: {len(phys_fail)}",
        "",
    ] + ([f"- FAIL {m}" for m in geo_fail + phys_fail] or ["- no failures"]) + [
        "",
        "## 3. Metadata",
        "",
    ] + ([f"- {m}" for m in meta_issues] or ["- SHA-256, material ids and printed page numbers match."]) + [
        "",
        "## 4. Sanity checks",
        "",
        "| check | comparisons |",
        "|:---|---:|",
    ] + [f"| {k} | {v} |" for k, v in sorted(counts.items())] + [
        "",
        "A-basis is the lower of T99 and the specification minimum (PDF page 1415 / printed 9-9; PDF page 1684 /",
        "printed A-6), so A <= S and A <= B must hold. B vs S has no defined order and is only reported.",
        "",
        "### Violations / discrepancies",
        "",
    ] + ([f"- {m}" for m in sanity] or ["- none"]) + [
        "",
        "### B vs S (informational)",
        "",
    ] + ([f"- B > S: {m}" for m in b_vs_s] or ["- no pair with B > S"]) + [
        "",
        f"## 5. Comparison with the typical-value table ({a.typical.as_posix()})",
        "",
        "Strength allowables (L, LT, T and undirected; ST excluded) converted with 1 ksi = 6.894757 MPa.",
        "",
        "| typical key | property | typical (MPa) | values compared | max allowable (MPa) "
        "| above typical by > 1 MPa | above by <= 1 MPa |",
        "|:---|:---|---:|---:|:---|---:|---:|",
    ] + typ_lines + [
        "",
        "### Allowables above the typical value",
        "",
    ] + ([f"- {m}" for m in typ_findings] or ["- none"]) + [""]
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"design cells checked {checked}: pdfplumber found {found_pl}, PyMuPDF found {found_mu}, "
          f"missing {n_design_miss}; RO values {ro_checked}, found {ro_found}; geometry {geo_ok}/{geo_total} "
          f"(physical presence failures {len(phys_fail)}); metadata issues {len(meta_issues)}; "
          f"sanity findings {len(sanity)}; B>S pairs {len(b_vs_s)}; typical exceedances {len(typ_findings)}")
    return 1 if (misses or meta_issues or geo_fail or phys_fail) else 0


if __name__ == "__main__":
    raise SystemExit(main())
