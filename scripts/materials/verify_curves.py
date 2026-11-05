"""Deterministic double-check of the digitized MIL-HDBK-5J curves; writes a Markdown report.

Run from the project root (the PDF is untrusted data and only parsed)::

    python -I scripts/materials/verify_curves.py \
        references/materials/mil-hdbk-5j/MIL-HDBK-5J.pdf \
        --report references/materials/curve_verification_report.md \
        --overlays references/materials/curve_overlays

Checks (thresholds fixed before looking at the results; see ``THRESHOLDS``):

(a) every caption of ``figures/index.md`` occurs on its cited PDF page (whitespace-insensitive) and the
    printed page number at the foot of that page equals the index entry; the curve file header repeats
    the index entry exactly;
(b) every axis fit used by a digitized curve has max residual <= ``AXIS_MAX_PCT`` % of the axis span;
(c) typical stress-strain figures: each digitized tension/compression curve that can be matched to a
    Ramberg-Osgood entry of the same figure (``handbook`` material sheets: n and, if printed, TYS/CYS)
    is compared with ``handbook.ramberg_osgood_stress`` at the digitized strains, using E (tension) or
    Ec (compression) from the material's property table; when the yield stress is not printed on the
    figure, the 0.2 %-offset yield of the digitized curve itself is used (stated per row). Max
    |stress deviation| is reported in % of f0.2 over the whole digitized range and over stress <= f0.2;
    the gate is the latter (MIL-HDBK-5J 9.8.4.1.2: the relation is "sufficiently accurate ... up to the
    yield strength"). Tangent-modulus curves are compared with ``handbook.ramberg_osgood_tangent_modulus``
    (stress at the digitized Et, by bisection on the handbook function);
(d) effect-of-temperature figures (percent of room-temperature value): value at 70 and 75 F within
    ``RT_TOL`` points of 100 %, non-increasing above room temperature (rises <= ``MONO_TOL`` points),
    0 <= value <= 110 % above room temperature, and longer exposure never stronger than shorter
    exposure (by more than ``EXPOSURE_TOL`` points) where both curves exist;
(e) overlays of every digitized curve on the page PNG crop, written to ``--overlays`` (inspect them).

Exit status 1 if any gated check fails (the report is written in any case).
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.materials import curves as cv  # noqa: E402
from aerokit.materials import handbook as hb  # noqa: E402

AXIS_MAX_PCT = 0.5        # % of axis span, max tick residual
RO_TOL_PCT = 3.0          # % of f0.2, max |stress deviation| for stress <= f0.2
RT_TOL = 2.0              # percentage points around 100 % at 70-75 F
MONO_TOL = 0.5            # percentage points: allowed rise above RT (drawing wiggle)
EXPOSURE_TOL = 1.0        # percentage points
THRESHOLDS = {"AXIS_MAX_PCT": AXIS_MAX_PCT, "RO_TOL_PCT": RO_TOL_PCT, "RT_TOL": RT_TOL,
              "MONO_TOL": MONO_TOL, "EXPOSURE_TOL": EXPOSURE_TOL}
FIG_INDEX = ROOT / "src" / "aerokit" / "materials" / "data" / "figures" / "index.md"


def _nows(s: str) -> str:
    return re.sub(r"\s+", "", s)


@dataclass
class Report:
    lines: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    def add(self, *ls: str) -> None:
        self.lines.extend(ls)

    def fail(self, msg: str) -> None:
        self.failures.append(msg)


def read_index() -> list[dict[str, str]]:
    out = []
    for line in FIG_INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| figure"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        out.append({"figure": c[0], "pdf_page": c[1], "printed_page": c[2], "materials": c[4], "caption": c[5]})
    return out


# --------------------------------------------------------------------------- (a)


def check_captions(doc: fitz.Document, rep: Report) -> None:
    rep.add("## (a) Captions and page numbers", "",
            "Caption text of `figures/index.md` searched (whitespace removed) in `page.get_text()` of the cited "
            "PDF page; printed page = the line matching `^[1-9A-Z]-\\d+$` below y = 700 pt.", "",
            "| figure | pdf page | caption found | printed page (index / PDF) | curve-file header = index |",
            "|:---|---:|:---|:---|:---|")
    entries = read_index()
    ok_cap = ok_pp = ok_hdr = 0
    for e in entries:
        page = doc[int(e["pdf_page"]) - 1]
        found = _nows(e["caption"]) in _nows(page.get_text("text"))
        foot = [b for b in page.get_text("dict")["blocks"] if b["type"] == 0]
        pps = []
        for b in foot:
            for ln in b["lines"]:
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if ln["bbox"][1] > 700 and re.fullmatch(r"[1-9A-Z]-\d+", t):
                    pps.append(t)
        pp = pps[0] if len(pps) == 1 else "/".join(pps) or "—"
        fc = cv.load_curve(e["figure"])
        hdr = (fc.caption == e["caption"] and str(fc.pdf_page) == e["pdf_page"]
               and fc.printed_page == e["printed_page"] and ", ".join(fc.materials) == e["materials"])
        ok_cap += found
        ok_pp += pp == e["printed_page"]
        ok_hdr += hdr
        if not found:
            rep.fail(f"(a) caption of {e['figure']} not found on PDF page {e['pdf_page']}")
        if pp != e["printed_page"]:
            rep.fail(f"(a) printed page of {e['figure']}: index {e['printed_page']}, PDF {pp}")
        if not hdr:
            rep.fail(f"(a) curve file header of {e['figure']} differs from figures/index.md")
        rep.add(f"| {e['figure']} | {e['pdf_page']} | {'yes' if found else 'NO'} | {e['printed_page']} / {pp} | "
                f"{'yes' if hdr else 'NO'} |")
    rep.add("", f"Result: captions found {ok_cap}/{len(entries)}; printed page matches {ok_pp}/{len(entries)}; "
            f"headers equal {ok_hdr}/{len(entries)}.", "")


# --------------------------------------------------------------------------- (b)


def check_axes(rep: Report) -> None:
    rep.add("## (b) Axis-mapping residuals", "",
            f"Gate: max tick residual <= {AXIS_MAX_PCT} % of the axis span for every axis that a curve uses. "
            "Residual = data value of the tick label minus the fitted map at the snapped tick position.", "",
            "| figure | status | axis | title | ticks (snapped) | rms % | max % | used | verdict |",
            "|:---|:---|:---|:---|---:|---:|---:|:---|:---|")
    worst = 0.0
    n_axes = 0
    for fid in cv.list_figures():
        fc = cv.load_curve(fid)
        if fc.status != "digitized":
            reason = fc.skipped[0] if fc.skipped else ""
            rep.add(f"| {fid} | skipped | — | {reason} | | | | | n/a |")
            continue
        used = {c.x_axis for c in fc.curves} | {c.y_axis for c in fc.curves}
        for a in fc.axes:
            u = a.name in used
            ok = a.max_residual_pct <= AXIS_MAX_PCT
            if u:
                n_axes += 1
                worst = max(worst, a.max_residual_pct)
                if not ok:
                    rep.fail(f"(b) {fid} axis {a.name}: max residual {a.max_residual_pct:.3f} %")
            rep.add(f"| {fid} | digitized | {a.name} | {a.title or '—'} | {a.ticks} ({a.snapped}) | "
                    f"{a.rms_residual_pct:.4f} | {a.max_residual_pct:.4f} | {'yes' if u else 'no'} | "
                    f"{('PASS' if ok else 'FAIL') if u else 'not used'} |")
    rep.add("", f"Result: {n_axes} axes used by curves; worst max residual {worst:.4f} % of span.", "")


# --------------------------------------------------------------------------- (c)

_DIR_WORDS = (("long transverse", "LT"), ("short transverse", "ST"), ("longitudinal", "L"))


def _dirs(label: str) -> frozenset[str]:
    t = label.lower()
    for w, d in _DIR_WORDS:
        t = t.replace(w, f" {d.lower()} ")
    t = t.replace("-", " ").replace("&", " ")
    return frozenset(x.upper() for x in re.findall(r"\b(lt|st|l)\b", t))


def _loading(label: str, kind: str, caption: str) -> str | None:
    low = label.lower()
    if kind == "tangent-modulus":
        return "compression"
    if "tension" in low:
        return "tension"
    if "comp" in low:
        return "compression"
    cap = caption.lower()
    tens = "tensile" in cap or "tension" in cap
    comp = "compressive" in cap or "compression" in cap
    if tens and not comp:
        return "tension"
    if comp and not tens and "tangent-modulus" not in cap.replace("compressive tangent-modulus", ""):
        return "compression"
    if comp and not tens:
        return "compression"
    return None


def _cond(label: str) -> str:
    return re.sub(r"[\s°]+", "", label.replace(" (tangent modulus)", "")).upper()


def _ro_entries(fc: cv.FigureCurves) -> list[tuple[str, hb.RambergOsgoodEntry]]:
    out: list[tuple[str, hb.RambergOsgoodEntry]] = []
    seen = set()
    for m in fc.materials:
        for e in hb.load_material(m).ramberg_osgood:
            if e.figure == fc.figure and (e.curve, e.n_raw) not in seen:
                seen.add((e.curve, e.n_raw))
                out.append((m, e))
    return out


def _match(c: cv.Curve, fc: cv.FigureCurves, entries: list[tuple[str, hb.RambergOsgoodEntry]]
           ) -> tuple[tuple[str, hb.RambergOsgoodEntry] | None, str]:
    load = _loading(c.label, c.kind, fc.caption)
    if c.label.startswith("unlabeled"):
        return None, "curve has no label"
    d = _dirs(c.label.replace(" (tangent modulus)", ""))
    same_load = [(m, e) for m, e in entries if e.loading == load]
    cands = []
    for m, e in same_load:
        if d and e.directions and (d <= e.directions or e.directions <= d):
            cands.append((m, e))          # e.g. "LT - compression" <-> "L & LT-comp."; "L and LT" <-> "L-", "LT-"
        elif not d and not e.directions and _cond(e.curve) == _cond(c.label):
            cands.append((m, e))          # condition / temperature labels: "H1025", "RT"
    generic = re.fullmatch(r"(tension|compression)( \(tangent modulus\))?", c.label.strip().lower())
    if not cands and not d and generic and len(same_load) == 1:
        cands = same_load                 # "Tension" on a figure with a single tension entry
    if not cands:
        return None, f"no Ramberg-Osgood entry of this figure matches label/loading ({load})"
    if len({(e.n_raw, e.yield_raw) for _, e in cands}) > 1:
        return None, "several entries with different n match: " + ", ".join(f"{e.curve} n={e.n_raw}"
                                                                          for _, e in cands)
    return cands[0], ""


_FORMS = ("sheet", "plate", "bar", "extrusion", "forging", "casting")


def _modulus(material: str, key: str, caption: str) -> tuple[float | None, str]:
    try:
        return hb.get_allowable(material, key, units="source"), f"{key} table value"
    except ValueError as exc:
        first_err = str(exc)
    for f in _FORMS:
        if f in caption.lower():
            try:
                return hb.get_allowable(material, key, units="source", form=f), f"{key} table value (form={f})"
            except (ValueError, KeyError):
                continue
    return None, f"{key} not unique in the table: {first_err[:120]}"


def _offset_yield(strain: np.ndarray, stress: np.ndarray, E_ksi: float) -> float | None:
    g = strain - stress / E_ksi - 0.002
    idx = np.flatnonzero((g[:-1] < 0) & (g[1:] >= 0))
    if not len(idx):
        return None
    i = int(idx[0])
    t = -g[i] / (g[i + 1] - g[i])
    return float(stress[i] + t * (stress[i + 1] - stress[i]))


def _stress_at_et(et: float, E: float, f02: float, n: float) -> float:
    lo, hi = 0.0, 3.0 * f02
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if hb.ramberg_osgood_tangent_modulus(mid, E, f02, n) > et:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


@dataclass
class RORow:
    figure: str
    curve: str
    entry: str
    n: float
    E: float
    f02: float
    f02_src: str
    dev_all: float
    dev_yield: float
    slope_dev: float | None
    npts: int
    verdict: str


def check_ro(rep: Report) -> list[RORow]:
    rep.add("## (c) Typical stress-strain curves vs Ramberg-Osgood", "",
            "RO: e = f/E + 0.002 (f/f0.2)^n (MIL-HDBK-5J Eq. 9.8.4.1.2(b)); n from the material sheet entry of "
            "the same figure (read from the figure annotations); E/Ec from the material's property table "
            "(10^3 ksi). Deviation = |f_digitized - f_RO(strain_digitized)| / f0.2 in %. Tangent modulus: "
            "|f_digitized - f_RO(Et_digitized)| / f0.2, points with Et < 0.98 Ec. "
            f"Gate: deviation over f <= f0.2 within {RO_TOL_PCT} %. The full-range value is reported, not gated. "
            "Last column: stress-strain rows = least-squares slope through the origin of the points with f <= 0.5 "
            "f0.2, vs E; tangent-modulus rows = largest digitized Et (vertical part) vs Ec.", "",
            "| figure | curve | RO entry (material) | n | E (ksi) | f0.2 (ksi) | f0.2 source | max dev, f <= f0.2 (%) "
            "| max dev, full range (%) | initial slope vs E / max Et vs Ec (%) | points | verdict |",
            "|:---|:---|:---|---:|---:|---:|:---|---:|---:|---:|---:|:---|")
    rows: list[RORow] = []
    skipped: list[str] = []
    for fid in cv.list_figures():
        fc = cv.load_curve(fid)
        if fc.kind not in ("stress-strain", "tangent-modulus") or fc.status != "digitized":
            continue
        entries = _ro_entries(fc)
        ann_n = sorted(re.findall(r"=\s*(\d+(?:\.\d+)?)", " ".join(a for a in fc.annotations if "n" in a)))
        ent_n = sorted(e.n_raw for _, e in entries)
        if entries and not set(ent_n) <= set(ann_n):
            rep.fail(f"(c) {fid}: n values of the material sheets {ent_n} not all among the figure annotations")
        for c in fc.curves:
            hit, why = _match(c, fc, entries)
            if hit is None:
                skipped.append(f"{fid} / {c.label}: {why}")
                continue
            m, e = hit
            if not e.room_temperature:
                skipped.append(f"{fid} / {c.label}: entry '{e.curve}' is not at room temperature (E at temperature "
                               "not available)")
                continue
            if "0.001" not in fc.axes[[a.name for a in fc.axes].index(c.x_axis)].title and c.kind != "tangent-modulus":
                skipped.append(f"{fid} / {c.label}: strain axis unit not '0.001 in./in.'")
                continue
            key = "E" if e.loading == "tension" else "Ec"
            E, esrc = _modulus(m, key, fc.caption)
            if E is None:
                skipped.append(f"{fid} / {c.label}: {esrc}")
                continue
            E_ksi = E * 1000.0
            if c.kind == "tangent-modulus":
                et = c.x_array * 1000.0
                f = c.y_array
                f02_src = "printed TYS/CYS" if e.yield_raw else ""
                if not e.yield_raw:
                    ss = [s for s in fc.curves if s.kind == "stress-strain" and
                          _match(s, fc, entries)[0] is not None and _match(s, fc, entries)[0][1] is e]
                    if len(ss) != 1:
                        skipped.append(f"{fid} / {c.label}: f0.2 not printed and no unique matching stress-strain "
                                       "curve to take the offset yield from")
                        continue
                    f02v = _offset_yield(ss[0].x_array * 1e-3, ss[0].y_array, E_ksi)
                    if f02v is None:
                        skipped.append(f"{fid} / {c.label}: offset yield of '{ss[0].label}' not reached")
                        continue
                    f02 = f02v
                    f02_src = f"0.2 % offset of digitized '{ss[0].label}'"
                else:
                    f02 = float(e.yield_raw)
                sel = et < 0.98 * E_ksi
                if sel.sum() < 3:
                    skipped.append(f"{fid} / {c.label}: fewer than 3 points with Et < 0.98 Ec")
                    continue
                f_ro = np.array([_stress_at_et(float(v), E_ksi, f02, e.n) for v in et[sel]])
                dev = np.abs(f[sel] - f_ro) / f02 * 100.0
                below = f[sel] <= f02
                dev_y = float(dev[below].max()) if below.any() else float("nan")
                slope = (float(et.max()) / E_ksi - 1.0) * 100.0          # vertical asymptote vs Ec
            else:
                strain = c.x_array * 1e-3
                f = c.y_array
                if e.yield_raw:
                    f02, f02_src = float(e.yield_raw), "printed TYS/CYS"
                else:
                    f02v = _offset_yield(strain, f, E_ksi)
                    if f02v is None:
                        skipped.append(f"{fid} / {c.label}: 0.2 % offset not reached on the digitized curve")
                        continue
                    f02, f02_src = f02v, "0.2 % offset of this digitized curve"
                f_ro = hb.ramberg_osgood_stress(strain, E_ksi, f02, e.n)
                dev = np.abs(f - f_ro) / f02 * 100.0
                below = f <= f02
                dev_y = float(dev[below].max()) if below.any() else float("nan")
                lin = (f <= 0.5 * f02) & (strain > 0)
                slope = (float(np.sum(strain[lin] * f[lin]) / np.sum(strain[lin] ** 2)) / E_ksi - 1.0) * 100.0 \
                    if lin.sum() >= 2 else None
            ok = math.isfinite(dev_y) and dev_y <= RO_TOL_PCT
            verdict = "PASS" if ok else "FAIL"
            if not ok:
                rep.fail(f"(c) {fid} / {c.label}: max RO deviation up to f0.2 = {dev_y:.2f} % of f0.2")
            row = RORow(fid, c.label, f"{e.curve} ({m})", e.n, E_ksi, f02, f02_src + f"; {esrc}", float(dev.max()),
                        dev_y, slope, int(len(dev)), verdict)
            rows.append(row)
            rep.add(f"| {fid} | {c.label} | {row.entry} | {e.n_raw} | {E_ksi:.0f} | {f02:.1f} | {row.f02_src} | "
                    f"{dev_y:.2f} | {row.dev_all:.2f} | {'—' if slope is None else f'{slope:+.1f}'} | {row.npts} | "
                    f"{verdict} |")
    npass = sum(r.verdict == "PASS" for r in rows)
    rep.add("", f"Result: {len(rows)} curves compared, {npass} PASS, {len(rows) - npass} FAIL.", "",
            "Curves of stress-strain figures not compared (reason):", "")
    rep.add(*[f"- {s}" for s in skipped] or ["- none"])
    rep.add("")
    return rows


# --------------------------------------------------------------------------- (d)


def check_temperature(rep: Report) -> None:
    rep.add("## (d) Effect-of-temperature curves", "",
            f"Gates: |value - 100| <= {RT_TOL} points at 70 F and 75 F (or at the first point if the curve starts "
            f"within 15 F above 75 F); above 75 F non-increasing (largest rise <= {MONO_TOL} points) and within "
            f"0-110 %; longer exposure <= shorter exposure + {EXPOSURE_TOL} points. Below room temperature values "
            "above 100 % are physical (cryogenic strengthening) and are reported, not gated - this departs from "
            "a literal '0-110 % everywhere' reading on purpose.", "",
            "| figure | curve | T range (F) | value at 70 F | value at 75 F | largest rise above RT | min/max above RT "
            "| max below RT | verdict |",
            "|:---|:---|:---|---:|---:|---:|:---|---:|:---|")
    exp_lines: list[str] = []
    for fid in cv.list_figures():
        fc = cv.load_curve(fid)
        if fc.kind != "effect-of-temperature" or fc.status != "digitized":
            continue
        for c in fc.curves:
            if not re.match(r"percent", c.y_title, re.I):
                continue
            x, y = c.x_array, c.y_array
            order = np.argsort(x, kind="stable")
            xs, ys = x[order], y[order]
            notes = []
            vals = {}
            for t in (70.0, 75.0):
                if xs[0] <= t <= xs[-1] and c.function_of_x:
                    vals[t] = cv.curve_value(fid, c.label, t)
            if not vals and xs[0] > 75.0 and xs[0] <= 90.0:
                vals[float(xs[0])] = float(ys[0])
                notes.append(f"starts at {xs[0]:.0f} F")
            rt_ok = bool(vals) and all(abs(v - 100.0) <= RT_TOL for v in vals.values())
            above = xs >= 75.0
            rise = float(np.max(np.diff(ys[above]))) if above.sum() > 1 else 0.0
            mono_ok = rise <= MONO_TOL
            rng_ok = bool(np.all((ys[above] >= 0) & (ys[above] <= 110))) if above.any() else True
            below = xs < 70.0
            unl = c.label.startswith("unlabeled")
            if not vals:
                notes.append("room temperature not on the digitized curve" if c.function_of_x
                             else "curve not single-valued in temperature")
                rt_ok = True                      # RT check not applicable (reported as N/A, not as PASS)
            ok = rt_ok and mono_ok and rng_ok
            verdict = ("PASS" if ok else "FAIL") + (" (RT check N/A)" if not vals else "")
            verdict += " (unlabeled)" if unl else ""
            if not ok:
                rep.fail(f"(d) {fid} / {c.label}: RT {vals} rise {rise:.2f} range ok {rng_ok}")
            v70 = f"{vals[70.0]:.1f}" if 70.0 in vals else "—"
            v75 = f"{vals[75.0]:.1f}" if 75.0 in vals else ("; ".join(f"{v:.1f} @ {k:.0f} F" for k, v in vals.items()
                                                                     if k not in (70.0,)) or "—")
            mm = f"{ys[above].min():.1f} / {ys[above].max():.1f}" if above.any() else "—"
            mb = f"{ys[below].max():.1f}" if below.any() else "—"
            rep.add(f"| {fid} | {c.label} | {xs[0]:.0f} to {xs[-1]:.0f} | {v70} | {v75} | {rise:.2f} | {mm} | {mb} | "
                    f"{verdict}{' - ' + '; '.join(notes) if notes else ''} |")
        # exposure ordering
        ex = sorted([(h, c) for c in fc.curves
                     if (h := cv.parse_exposure_hours(c.label)) is not None and c.function_of_x], key=lambda t: t[0])
        for (_h1, c1), (_h2, c2) in zip(ex, ex[1:], strict=False):
            lo = max(c1.x_range[0], c2.x_range[0], 75.0)
            hi = min(c1.x_range[1], c2.x_range[1])
            if hi <= lo:
                continue
            t = np.linspace(lo, hi, 200)
            d = cv.curve_value(fid, c2.label, t) - cv.curve_value(fid, c1.label, t)
            worst = float(d.max())
            ok = worst <= EXPOSURE_TOL
            if not ok:
                rep.fail(f"(d) {fid}: '{c2.label}' above '{c1.label}' by {worst:.2f} points at "
                         f"{t[int(np.argmax(d))]:.0f} F")
            exp_lines.append(f"| {fid} | {c1.label} -> {c2.label} | {lo:.0f} to {hi:.0f} | {worst:+.2f} | "
                             f"{'PASS' if ok else 'FAIL'} |")
    rep.add("", "Exposure ordering (value of the longer exposure minus the shorter one; must be <= "
            f"{EXPOSURE_TOL} points):", "", "| figure | pair | common T range (F) | max difference | verdict |",
            "|:---|:---|:---|---:|:---|", *(exp_lines or ["| — | — | — | — | — |"]), "")


# --------------------------------------------------------------------------- (e)


def overlays(out_dir: Path, rep: Report) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import datawiz as dw
    import matplotlib.image as mpimg

    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "src" / "aerokit" / "materials" / "data" / "figures"
    written: list[Path] = []
    audits: list[str] = []
    colors = dw.paletler.kategorik()
    for fid in cv.list_figures():
        fc = cv.load_curve(fid)
        if fc.status != "digitized" or fc.frame_pt is None:
            continue
        png = fig_dir / Path(fc.page_png).name
        img = mpimg.imread(png)
        scale = img.shape[1] / 612.0                        # px per pt (page width 612 pt)
        x0, y0, x1, y1 = fc.frame_pt
        pad = 40.0
        cx0, cy0 = max(x0 - pad, 0.0), max(y0 - pad, 0.0)
        cx1, cy1 = min(x1 + pad, 612.0), min(y1 + pad, 792.0)
        crop = img[int(cy0 * scale):int(cy1 * scale), int(cx0 * scale):int(cx1 * scale)]
        aspect = (cy1 - cy0) / (cx1 - cx0)
        fig, ax = dw.figur("web", hedef="web-640", oran=aspect)
        ax.imshow(crop, cmap="gray", extent=(cx0, cx1, cy1, cy0), alpha=0.55, interpolation="bilinear")
        axes = {a.name: a for a in fc.axes}
        for i, c in enumerate(fc.curves):
            ax_x, ax_y = axes[c.x_axis], axes[c.y_axis]

            def to_pt(v: np.ndarray, a: cv.AxisFit) -> np.ndarray:
                w = np.log10(v) if a.scale == "log" else v
                return (w - a.b) / a.a
            px, py = to_pt(c.x_array, ax_x), to_pt(c.y_array, ax_y)
            col = colors[i % len(colors)]
            ax.plot(px, py, "-", color=col, lw=1.0, marker="o", ms=2.2, mfc="none", mew=0.6)
            ax.annotate(f"{i + 1}", (px[-1], py[-1]), xytext=(3, 0), textcoords="offset points", color=col,
                        fontsize=9, va="center")
        for a in fc.axes:                                    # fitted tick positions
            for v in sorted({float(t) for t in _tick_values(a)}):
                p = (math.log10(v) - a.b) / a.a if a.scale == "log" else (v - a.b) / a.a
                if a.name.startswith("x"):
                    ax.plot([p, p], [y1 + 1, y1 + 5], color="#D55E00", lw=0.8)
                else:
                    ax.plot([x0 - 5, x0 - 1] if a.side == "left" else [x1 + 1, x1 + 5], [p, p], color="#D55E00",
                            lw=0.8)
        ax.set_xlim(cx0, cx1)
        ax.set_ylim(cy1, cy0)
        ax.set_axis_off()
        ax.set_title(f"Figure {fid}: " + "; ".join(f"{i + 1} = {c.label}" for i, c in enumerate(fc.curves)),
                     fontsize=9, loc="left", wrap=True)
        stem = out_dir / cv.figure_file(fid).stem
        res = dw.kaydet(fig, str(stem), bicimler=("png",), ortam="web", hedef="web-640", sessiz=True)
        matplotlib.pyplot.close(fig)
        written.append(stem.with_suffix(".png"))
        audits.append(f"| {fid} | {stem.name}.png | {_audit_summary(res, stem)} |")
    rep.add("## (e) Visual overlays", "",
            f"{len(written)} overlays in `{out_dir.relative_to(ROOT).as_posix()}/`: digitized points (circles) "
            "and curve numbers drawn over the 150 dpi page PNG; orange ticks = fitted positions of the tick "
            "values (registration check). Each overlay was saved through datawiz `dw.kaydet` (audit report "
            "next to the PNG).", "", "| figure | overlay | datawiz audit |", "|:---|:---|:---|", *audits, "")
    return written


def _tick_values(a: cv.AxisFit) -> list[float]:
    return list(a.tick_values)


def _audit_summary(res: dict[str, object], stem: Path) -> str:
    txt = Path(str(stem) + ".denetim.txt")
    if txt.is_file():
        t = txt.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"(\d+)\s*HATA", t)
        u = re.search(r"(\d+)\s*UYARI", t)
        return f"{m.group(1) if m else '?'} HATA, {u.group(1) if u else '?'} UYARI"
    return str({k: res[k] for k in list(res)[:3]})


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--report", type=Path, default=ROOT / "references" / "materials" / "curve_verification_report.md")
    ap.add_argument("--overlays", type=Path, default=ROOT / "references" / "materials" / "curve_overlays")
    ap.add_argument("--no-overlays", action="store_true")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = fitz.open(args.pdf)
    rep = Report()
    figs = [cv.load_curve(f) for f in cv.list_figures()]
    n_dig = sum(f.status == "digitized" for f in figs)
    n_c = sum(len(f.curves) for f in figs)
    n_p = sum(len(c.x) for f in figs for c in f.curves)
    n_unl = sum(c.label.startswith("unlabeled") for f in figs for c in f.curves)
    rep.add("# Verification of the digitized MIL-HDBK-5J curves", "",
            "Generated by `scripts/materials/verify_curves.py`; do not edit. Thresholds were fixed before the "
            "results were looked at: " + ", ".join(f"{k} = {v}" for k, v in THRESHOLDS.items()) + ". Changed after "
            "the first run (no threshold changed): curves whose digitized range does not contain 70-75 F (or "
            "that are not single-valued in temperature) are reported as 'RT check N/A' instead of FAIL; label "
            "matching for (c) was widened to entries covering several directions ('L & LT') and to a lone "
            "'Tension'/'Compression' label.", "",
            f"Figures: {len(figs)} in `figures/index.md`, {n_dig} digitized, {len(figs) - n_dig} skipped. "
            f"Curves: {n_c} ({n_unl} without a label). Points: {n_p}.", "")
    check_captions(doc, rep)
    check_axes(rep)
    check_ro(rep)
    check_temperature(rep)
    if not args.no_overlays:
        overlays(args.overlays, rep)
    rep.add("## Skipped figures", "")
    for f in figs:
        if f.status != "digitized":
            rep.add(f"- {f.figure} (PDF p. {f.pdf_page}): {'; '.join(f.skipped)}")
    rep.add("", "## Failed checks", "")
    rep.add(*[f"- {m}" for m in rep.failures] or ["- none"])
    rep.add("")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(rep.lines), encoding="utf-8")
    print(f"report: {args.report}  failures: {len(rep.failures)}")
    for m in rep.failures:
        print("  FAIL", m)
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main())
