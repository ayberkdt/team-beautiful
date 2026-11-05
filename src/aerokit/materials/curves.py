"""Reader for MIL-HDBK-5J figure curves digitized to Markdown.

The files in ``aerokit/materials/data/curves`` are produced by
``scripts/materials/digitize_figures.py`` from the *vector paths* of the
MIL-HDBK-5J figure pages listed in ``data/figures/index.md`` (no manual
digitizing): effect-of-temperature curves (percent of room-temperature
strength or modulus), typical stress-strain and compressive tangent-modulus
curves and physical properties versus temperature. Each file records the
pixel-to-data axis fits (with residuals), every element the digitizer skipped
and why, and one table per curve in the units printed on the figure.

These are *typical* curves read from a figure, not design allowables. Values
are interpolated linearly between the digitized points; nothing is
extrapolated.

Examples
--------
>>> from aerokit.materials import curves
>>> curves.temperature_factor("al-2024-t3", "Ftu", 75.0, exposure="1/2 hr")  # doctest: +SKIP
99.9
"""

from __future__ import annotations

import functools
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, NamedTuple, overload

import numpy as np
import numpy.typing as npt

from aerokit.references import cite

__all__ = [
    "CURVES_DIR",
    "AxisFit",
    "Curve",
    "FigureCurves",
    "CurveInfo",
    "CurveFormatError",
    "OutOfRangeError",
    "parse_curve_markdown",
    "figure_file",
    "list_figures",
    "load_curve",
    "list_curves",
    "curve_value",
    "temperature_factor",
    "parse_exposure_hours",
]

CURVES_DIR: Final[Path] = Path(__file__).resolve().parent / "data" / "curves"

FloatArray = npt.NDArray[np.float64]
TemperatureUnit = Literal["F", "C", "K"]

_FIGURE_ID_RE: Final = re.compile(r"^(\d+(?:\.\d+)+)(?:\(([a-z0-9]+)\))?$")
_NUM_RE: Final = re.compile(r"^-?(?:\d+(?:\.\d+)?|\.\d+)$")
_AXES_HEADER: Final = ("| axis | side | title | unit | scale | ticks | snapped | a | b | rms residual (% span) "
                       "| max residual (% span) | tick values |")
_AXES_SEP: Final = "|:---|:---|:---|:---|:---|---:|---:|---:|---:|---:|---:|:---|"
_FIGURE_KEYS: Final = ("figure", "caption", "pdf_page", "printed_page", "materials", "page_png", "kind",
                       "status", "method", "annotations")
_CURVE_KEYS: Final = ("label_source", "kind", "x_axis", "y_axis", "x_title", "y_title", "function_of_x",
                      "function_of_y", "source_vertices", "points", "resampling_max_error_pt", "notes")
_KINDS: Final = frozenset({"effect-of-temperature", "stress-strain", "tangent-modulus", "physical-properties",
                           "other"})
_CURVE_KINDS: Final = frozenset({"curve", "stress-strain", "tangent-modulus"})


class CurveFormatError(ValueError):
    """A curve Markdown file does not follow the strict layout written by the digitizer."""


class OutOfRangeError(ValueError):
    """The requested abscissa lies outside the digitized range of the curve (no extrapolation)."""


# --------------------------------------------------------------------------- data classes


@dataclass(frozen=True)
class AxisFit:
    """Least-squares pixel-to-data map of one axis: ``v = a * p + b`` (``log10 v`` for log axes)."""

    name: str
    side: str
    title: str
    unit: str
    scale: str
    ticks: int
    snapped: int
    a: float
    b: float
    rms_residual_pct: float
    max_residual_pct: float
    tick_values: tuple[float, ...]


@dataclass(frozen=True)
class Curve:
    """One digitized curve; ``x`` and ``y`` are in the units printed on the figure."""

    label: str
    label_source: str
    kind: str
    x_axis: str
    y_axis: str
    x_title: str
    y_title: str
    x_unit: str
    y_unit: str
    function_of_x: bool
    function_of_y: bool
    source_vertices: int
    resampling_max_error_pt: float
    notes: str
    x: tuple[float, ...]
    y: tuple[float, ...]

    @property
    def x_array(self) -> FloatArray:
        """Abscissae as a new NumPy array."""
        return np.array(self.x, dtype=np.float64)

    @property
    def y_array(self) -> FloatArray:
        """Ordinates as a new NumPy array."""
        return np.array(self.y, dtype=np.float64)

    @property
    def x_range(self) -> tuple[float, float]:
        """(min, max) of the digitized abscissae."""
        return (min(self.x), max(self.x))

    @property
    def y_range(self) -> tuple[float, float]:
        """(min, max) of the digitized ordinates."""
        return (min(self.y), max(self.y))


@dataclass(frozen=True)
class FigureCurves:
    """Everything one curve file holds about a figure."""

    figure: str
    caption: str
    pdf_page: int
    printed_page: str
    materials: tuple[str, ...]
    page_png: str
    kind: str
    status: str
    method: str
    frame_pt: tuple[float, float, float, float] | None
    annotations: tuple[str, ...]
    axes: tuple[AxisFit, ...]
    skipped: tuple[str, ...]
    curves: tuple[Curve, ...]

    @property
    def labels(self) -> tuple[str, ...]:
        """Curve labels in file order."""
        return tuple(c.label for c in self.curves)

    def curve(self, label: str) -> Curve:
        """The curve called ``label`` (exact match, then case/space-insensitive).

        Raises
        ------
        KeyError
            No such curve; the message lists the labels of the figure.
        """
        for c in self.curves:
            if c.label == label:
                return c
        key = _norm_label(label)
        hits = [c for c in self.curves if _norm_label(c.label) == key]
        if len(hits) == 1:
            return hits[0]
        raise KeyError(f"figure {self.figure} has no curve {label!r}; curves: "
                       + (", ".join(repr(c.label) for c in self.curves) or "none (" + self.status + ")"))


class CurveInfo(NamedTuple):
    """One row of :func:`list_curves`."""

    figure: str
    label: str
    kind: str
    x_title: str
    y_title: str
    materials: tuple[str, ...]


def _norm_label(s: str) -> str:
    return re.sub(r"[\s_]+", "", s).lower().replace("½", "1/2")


# --------------------------------------------------------------------------- parser


def _err(lineno: int, msg: str) -> CurveFormatError:
    return CurveFormatError(f"line {lineno}: {msg}")


def _row(line: str, lineno: int) -> list[str]:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        raise _err(lineno, f"table row must start and end with '|': {line!r}")
    return [c.strip() for c in s[1:-1].split("|")]


def _float(text: str, lineno: int, what: str) -> float:
    try:
        v = float(text)
    except ValueError:
        raise _err(lineno, f"{what} is not a number: {text!r}") from None
    if not math.isfinite(v):
        raise _err(lineno, f"{what} is not finite: {text!r}")
    return v


def _int(text: str, lineno: int, what: str) -> int:
    if not re.fullmatch(r"\d+", text):
        raise _err(lineno, f"{what} is not a non-negative integer: {text!r}")
    return int(text)


def _yes_no(text: str, lineno: int, what: str) -> bool:
    if text not in ("yes", "no"):
        raise _err(lineno, f"{what} must be 'yes' or 'no', got {text!r}")
    return text == "yes"


def _bullets(body: list[tuple[int, str]], keys: Sequence[str], where: str) -> dict[str, tuple[int, str]]:
    out: dict[str, tuple[int, str]] = {}
    for lineno, line in body:
        m = re.match(r"^- ([a-z_]+): (.*)$", line)
        if not m:
            continue
        if m.group(1) in out:
            raise _err(lineno, f"duplicate key {m.group(1)!r} in {where}")
        out[m.group(1)] = (lineno, m.group(2).strip())
    missing = [k for k in keys if k not in out]
    if missing:
        first = body[0][0] if body else 0
        raise _err(first, f"{where} lacks {', '.join(missing)}")
    return out


def _unit_of(header_cell: str, lineno: int, axis: str) -> str:
    m = re.fullmatch(rf"{axis} \((.*)\)", header_cell)
    if not m:
        raise _err(lineno, f"curve table header cell must be '{axis} (<unit>)', got {header_cell!r}")
    return "" if m.group(1) == "-" else m.group(1)


def _parse_curve(label: str, body: list[tuple[int, str]], axes: dict[str, AxisFit]) -> Curve:
    meta = _bullets(body, _CURVE_KEYS, f"curve {label!r}")
    kind = meta["kind"][1]
    if kind not in _CURVE_KINDS:
        raise _err(meta["kind"][0], f"unknown curve kind {kind!r}")
    for k in ("x_axis", "y_axis"):
        if meta[k][1] not in axes:
            raise _err(meta[k][0], f"{k} {meta[k][1]!r} is not an axis of this figure")
    fx = _yes_no(meta["function_of_x"][1], meta["function_of_x"][0], "function_of_x")
    fy = _yes_no(meta["function_of_y"][1], meta["function_of_y"][0], "function_of_y")
    npts = _int(meta["points"][1], meta["points"][0], "points")
    table = [(n, ln) for n, ln in body if ln.startswith("|")]
    if len(table) < 2:
        raise _err(body[-1][0] if body else 0, f"curve {label!r} has no table")
    (h_no, header), (s_no, sep) = table[0], table[1]
    cells = _row(header, h_no)
    if len(cells) != 2:
        raise _err(h_no, "curve table must have exactly two columns (x, y)")
    xu, yu = _unit_of(cells[0], h_no, "x"), _unit_of(cells[1], h_no, "y")
    if _row(sep, s_no) != ["---:", "---:"]:
        raise _err(s_no, f"bad separator row {sep!r}")
    xs: list[float] = []
    ys: list[float] = []
    for n, ln in table[2:]:
        c = _row(ln, n)
        if len(c) != 2 or not all(_NUM_RE.match(v) for v in c):
            raise _err(n, f"curve row must hold two numbers: {ln!r}")
        xs.append(_float(c[0], n, "x"))
        ys.append(_float(c[1], n, "y"))
    if len(xs) != npts:
        raise _err(meta["points"][0], f"points says {npts} but the table has {len(xs)} rows")
    if len(xs) < 2:
        raise _err(meta["points"][0], "a curve needs at least two points")
    if fx and not all(b > a for a, b in zip(xs, xs[1:], strict=False)):
        raise _err(meta["function_of_x"][0], f"curve {label!r} is marked function_of_x but x is not strictly "
                   "increasing")
    if fy and not (all(b > a for a, b in zip(ys, ys[1:], strict=False))
                   or all(b < a for a, b in zip(ys, ys[1:], strict=False))):
        raise _err(meta["function_of_y"][0], f"curve {label!r} is marked function_of_y but y is not strictly "
                   "monotone")
    return Curve(
        label=label, label_source=meta["label_source"][1], kind=kind, x_axis=meta["x_axis"][1],
        y_axis=meta["y_axis"][1], x_title=meta["x_title"][1], y_title=meta["y_title"][1], x_unit=xu, y_unit=yu,
        function_of_x=fx, function_of_y=fy,
        source_vertices=_int(meta["source_vertices"][1], meta["source_vertices"][0], "source_vertices"),
        resampling_max_error_pt=_float(meta["resampling_max_error_pt"][1], meta["resampling_max_error_pt"][0],
                                       "resampling_max_error_pt"),
        notes=meta["notes"][1], x=tuple(xs), y=tuple(ys))


def _parse_axes(body: list[tuple[int, str]]) -> dict[str, AxisFit]:
    table = [(n, ln) for n, ln in body if ln.startswith("|")]
    if not table or table[0][1].strip() != _AXES_HEADER:
        raise _err(table[0][0] if table else (body[0][0] if body else 0), "bad or missing axes table header")
    if len(table) < 2 or table[1][1].strip() != _AXES_SEP:
        raise _err(table[1][0] if len(table) > 1 else table[0][0], "bad axes table separator row")
    out: dict[str, AxisFit] = {}
    for n, ln in table[2:]:
        c = _row(ln, n)
        if len(c) != 12:
            raise _err(n, f"axes row needs 12 cells, got {len(c)}")
        if not re.fullmatch(r"[xy]\d+", c[0]):
            raise _err(n, f"bad axis name {c[0]!r}")
        if c[4] not in ("linear", "log"):
            raise _err(n, f"axis scale must be 'linear' or 'log', got {c[4]!r}")
        if c[0] in out:
            raise _err(n, f"duplicate axis {c[0]!r}")
        out[c[0]] = AxisFit(c[0], c[1], "" if c[2] == "—" else c[2], "" if c[3] == "—" else c[3], c[4],
                            _int(c[5], n, "ticks"), _int(c[6], n, "snapped"), _float(c[7], n, "a"),
                            _float(c[8], n, "b"), _float(c[9], n, "rms residual"), _float(c[10], n, "max residual"),
                            tuple(_float(v.strip(), n, "tick value") for v in c[11].split(";")))
        if len(out[c[0]].tick_values) != out[c[0]].ticks:
            raise _err(n, f"axis {c[0]}: {out[c[0]].ticks} ticks but {len(out[c[0]].tick_values)} tick values")
    return out


@cite("mil_hdbk_5j_2003", note="figure pages listed in data/figures/index.md")
def parse_curve_markdown(text: str) -> FigureCurves:
    """Parse one digitized-curve Markdown file (strict).

    Parameters
    ----------
    text:
        File content as written by ``scripts/materials/digitize_figures.py``.

    Returns
    -------
    FigureCurves

    Raises
    ------
    CurveFormatError
        Any deviation from the layout: missing sections or keys, malformed
        table rows, non-numeric or non-finite values, point counts that do
        not match, x not strictly increasing on a curve marked
        ``function_of_x``, unknown axes, duplicate curve labels.
    """
    lines = text.splitlines()
    if not lines or not re.fullmatch(r"# Digitized curves: Figure \S+", lines[0]):
        raise _err(1, "first line must be '# Digitized curves: Figure <id>'")
    sections: list[tuple[int, str, list[tuple[int, str]]]] = []
    for i, ln in enumerate(lines[1:], start=2):
        if ln.startswith("## "):
            sections.append((i, ln[3:].strip(), []))
        elif sections and ln.strip():
            sections[-1][2].append((i, ln))
    names = [s[1] for s in sections]
    for need in ("Figure", "Axes", "Skipped elements"):
        if need not in names:
            raise _err(len(lines), f"missing section '## {need}'")
    if names[:3] != ["Figure", "Axes", "Skipped elements"]:
        raise _err(sections[0][0] if sections else 1, "sections must start with Figure, Axes, Skipped elements")
    fig_body = sections[0][2]
    meta = _bullets(fig_body, _FIGURE_KEYS, "section Figure")
    figure = meta["figure"][1]
    if not _FIGURE_ID_RE.match(figure) or lines[0] != f"# Digitized curves: Figure {figure}":
        raise _err(meta["figure"][0], f"figure id {figure!r} is malformed or does not match the title")
    kind = meta["kind"][1]
    if kind not in _KINDS:
        raise _err(meta["kind"][0], f"unknown figure kind {kind!r}")
    status = meta["status"][1]
    if status not in ("digitized", "skipped"):
        raise _err(meta["status"][0], f"status must be 'digitized' or 'skipped', got {status!r}")
    frame: tuple[float, float, float, float] | None = None
    fr = [(n, ln) for n, ln in fig_body if ln.startswith("- frame_pt: ")]
    if fr:
        parts = [p.strip() for p in fr[0][1].split(":", 1)[1].split(",")]
        if len(parts) != 4:
            raise _err(fr[0][0], "frame_pt needs four numbers")
        f4 = [_float(p, fr[0][0], "frame_pt") for p in parts]
        frame = (f4[0], f4[1], f4[2], f4[3])
    ann = meta["annotations"][1]
    axes = _parse_axes(sections[1][2])
    skipped = tuple(ln[2:].strip() for _, ln in sections[2][2] if ln.startswith("- "))
    curves: list[Curve] = []
    for _, title, body in sections[3:]:
        if not title.startswith("Curve: ") or not title[7:].strip():
            raise _err(body[0][0] if body else len(lines), f"unexpected section {title!r}")
        label = title[7:].strip()
        if any(c.label == label for c in curves):
            raise _err(body[0][0] if body else len(lines), f"duplicate curve label {label!r}")
        curves.append(_parse_curve(label, body, axes))
    if status == "digitized" and not curves:
        raise _err(meta["status"][0], "status is 'digitized' but the file has no curve")
    if status == "skipped" and curves:
        raise _err(meta["status"][0], "status is 'skipped' but the file has curves")
    return FigureCurves(
        figure=figure, caption=meta["caption"][1], pdf_page=_int(meta["pdf_page"][1], meta["pdf_page"][0], "pdf_page"),
        printed_page=meta["printed_page"][1],
        materials=tuple(m.strip() for m in meta["materials"][1].split(",") if m.strip()),
        page_png=meta["page_png"][1], kind=kind, status=status, method=meta["method"][1], frame_pt=frame,
        annotations=() if ann == "none" else tuple(a.strip() for a in ann.split(" | ")),
        axes=tuple(axes.values()), skipped=skipped, curves=tuple(curves))


# --------------------------------------------------------------------------- files


def figure_file(figure_id: str) -> Path:
    """Path of the curve file for ``figure_id`` (e.g. ``"3.7.6.1.6(a)"`` -> ``fig-3-7-6-1-6a.md``).

    Raises
    ------
    ValueError
        ``figure_id`` is not of the form ``d.d...d`` with an optional ``(x)`` suffix.
    """
    m = _FIGURE_ID_RE.match(figure_id.strip())
    if not m:
        raise ValueError(f"figure id must look like '3.7.6.1.6(a)', got {figure_id!r}")
    return CURVES_DIR / ("fig-" + m.group(1).replace(".", "-") + (m.group(2) or "") + ".md")


def list_figures() -> tuple[str, ...]:
    """Figure ids that have a curve file, in the order of ``curves/index.md``."""
    out: list[str] = []
    index = CURVES_DIR / "index.md"
    for line in index.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and not line.startswith("| figure"):
            fid = line.split("|")[1].strip()
            if _FIGURE_ID_RE.match(fid):
                out.append(fid)
    return tuple(out)


@functools.lru_cache(maxsize=128)
@cite("mil_hdbk_5j_2003", note="digitized from the vector paths of the figure page")
def load_curve(figure_id: str) -> FigureCurves:
    """Load and parse the digitized curves of one figure (cached).

    Parameters
    ----------
    figure_id:
        Figure number as printed, e.g. ``"3.2.3.1.1(a)"``.

    Returns
    -------
    FigureCurves
        All curves of the figure plus the axis fits and the skipped elements.

    Raises
    ------
    KeyError
        No curve file for this figure; the message lists the available ids.
    CurveFormatError
        The file is malformed.
    """
    path = figure_file(figure_id)
    if not path.is_file():
        raise KeyError(f"no digitized curves for figure {figure_id!r}; available: {', '.join(list_figures())}")
    return parse_curve_markdown(path.read_text(encoding="utf-8"))


@cite("mil_hdbk_5j_2003")
def list_curves(material: str | None = None) -> tuple[CurveInfo, ...]:
    """All digitized curves, optionally only those of figures that list ``material``.

    Parameters
    ----------
    material:
        Material identifier as in :func:`aerokit.materials.handbook.list_materials`
        (case-insensitive), or ``None`` for every figure.

    Returns
    -------
    tuple of CurveInfo
        ``(figure, label, kind, x_title, y_title, materials)`` per curve.

    Raises
    ------
    KeyError
        ``material`` is not a known material identifier.
    """
    from aerokit.materials.handbook import list_materials

    slug = None if material is None else material.strip().lower()
    if slug is not None and slug not in list_materials():
        raise KeyError(f"unknown material {material!r}; available: {', '.join(list_materials())}")
    out: list[CurveInfo] = []
    for fid in list_figures():
        fc = load_curve(fid)
        if slug is not None and slug not in fc.materials:
            continue
        out.extend(CurveInfo(fc.figure, c.label, c.kind, c.x_title, c.y_title, fc.materials) for c in fc.curves)
    return tuple(out)


# --------------------------------------------------------------------------- interpolation


def _interp(xs: FloatArray, ys: FloatArray, q: FloatArray, what: str) -> FloatArray:
    lo, hi = float(xs[0]), float(xs[-1])
    eps = 1e-9 * max(abs(hi - lo), 1.0)
    bad = ~np.isfinite(q) | (q < lo - eps) | (q > hi + eps)
    if np.any(bad):
        first = float(q[np.flatnonzero(bad)[0]])
        raise OutOfRangeError(f"{what} = {first!r} is outside the digitized range [{lo:g}, {hi:g}] "
                              "(values are not extrapolated)")
    return np.interp(np.clip(q, lo, hi), xs, ys).astype(np.float64)


@overload
def curve_value(figure_id: str, curve_label: str, x: float, *, along: Literal["x", "y"] = "x") -> float: ...
@overload
def curve_value(figure_id: str, curve_label: str, x: FloatArray, *,
                along: Literal["x", "y"] = "x") -> FloatArray: ...
@cite("mil_hdbk_5j_2003", note="typical curve, linear interpolation between digitized points")
def curve_value(figure_id: str, curve_label: str, x: float | FloatArray, *,
                along: Literal["x", "y"] = "x") -> float | FloatArray:
    """Linearly interpolated value of a digitized curve.

    Parameters
    ----------
    figure_id:
        Figure number, e.g. ``"3.7.6.1.6(a)"``.
    curve_label:
        Curve label as listed by :func:`list_curves` (case and blanks ignored
        if unambiguous).
    x:
        Abscissa in the figure's printed unit (``along="x"``), or ordinate
        (``along="y"``) to read the abscissa at a given ordinate, e.g. the
        tangent modulus at a given stress. Scalar or array.
    along:
        ``"x"`` (default): return y at x; requires a curve that is a function
        of x. ``"y"``: return x at y; requires a curve monotone in y.

    Returns
    -------
    float or numpy.ndarray

    Raises
    ------
    KeyError
        Unknown figure or curve.
    OutOfRangeError
        A query lies outside the digitized range (no extrapolation).
    ValueError
        The curve is not single-valued in the requested direction, or
        ``along`` is invalid.
    """
    c = load_curve(figure_id).curve(curve_label)
    q = np.atleast_1d(np.asarray(x, dtype=np.float64))
    if along == "x":
        if not c.function_of_x:
            raise ValueError(f"curve {c.label!r} of figure {figure_id} is not single-valued in x "
                             "(e.g. a vertical part); use along='y' if it is monotone in y")
        out = _interp(c.x_array, c.y_array, q, f"x ({c.x_unit or 'unitless'})")
    elif along == "y":
        if not c.function_of_y:
            raise ValueError(f"curve {c.label!r} of figure {figure_id} is not monotone in y")
        ys, xs = c.y_array, c.x_array
        if ys[0] > ys[-1]:
            ys, xs = ys[::-1], xs[::-1]
        out = _interp(ys, xs, q, f"y ({c.y_unit or 'unitless'})")
    else:
        raise ValueError(f"along must be 'x' or 'y', got {along!r}")
    if isinstance(x, np.ndarray):
        return out.reshape(np.shape(x))
    return float(out[0])


# --------------------------------------------------------------------------- temperature factor


_PROPERTY_ALIASES: Final[dict[str, str]] = {
    "ftu": "Ftu", "fty": "Fty", "e": "E", "ec": "Ec", "modulus": "E",
}


def parse_exposure_hours(text: str) -> float | None:
    """Exposure time in hours from a label such as ``"1/2 hr"``, ``"½ hr"`` or ``"10,000 hr"``.

    Returns ``None`` if the text is not an exposure-time label.
    """
    t = text.strip().replace("½", "1/2").replace(",", "")
    m = re.fullmatch(r"(?:up to\s+)?(\d+(?:\.\d+)?|\d+/\d+|\.\d+)\s*-?\s*(?:hr|hrs|hours?)\.?", t, re.I)
    if not m:
        return None
    v = m.group(1)
    if "/" in v:
        a, b = v.split("/")
        return float(a) / float(b)
    return float(v)


def _figure_properties(caption: str) -> frozenset[str]:
    c = caption.replace(" ", "")
    props = set()
    if "(Ftu)" in c or "(F_tu)" in c:
        props.add("Ftu")
    if "(Fty)" in c or "(F_ty)" in c:
        props.add("Fty")
    if re.search(r"\(EandEc\)|moduli|modulus\(E", c):
        props.update({"E", "Ec"})
    elif "modulus(E)" in c or "tensilemodulus(E)" in c:
        props.add("E")
    return frozenset(props)


def _label_property(label: str) -> frozenset[str] | None:
    k = re.sub(r"[\s_]+", "", label).replace("&", "and").lower()
    if k in ("ftu",):
        return frozenset({"Ftu"})
    if k in ("fty",):
        return frozenset({"Fty"})
    if k in ("eandec",):
        return frozenset({"E", "Ec"})
    if k == "e":
        return frozenset({"E"})
    return None


def _to_fahrenheit(t: float, units: TemperatureUnit) -> float:
    if units == "F":
        return t
    if units == "C":
        return t * 9.0 / 5.0 + 32.0
    if units == "K":
        return (t - 273.15) * 9.0 / 5.0 + 32.0
    raise ValueError(f"temperature_units must be 'F', 'C' or 'K', got {units!r}")


@cite("mil_hdbk_5j_2003", note="effect-of-temperature figures (percent of room-temperature value)")
def temperature_factor(material: str, property: str, temperature: float, exposure: float | str | None = None,
                       *, temperature_units: TemperatureUnit = "F") -> float:
    """Percent of the room-temperature value of ``property`` at ``temperature``.

    Reads the MIL-HDBK-5J "Effect of temperature on ..." figure listed for the
    material (``Ftu``, ``Fty``: strength at temperature; ``E``/``Ec``: modulus
    at temperature) and interpolates the digitized curve linearly.

    Parameters
    ----------
    material:
        Material identifier, e.g. ``"al-2024-t3"``.
    property:
        ``"Ftu"``, ``"Fty"``, ``"E"`` or ``"Ec"`` (case-insensitive).
    temperature:
        Test temperature (degrees Fahrenheit unless ``temperature_units`` says otherwise).
    exposure:
        Exposure time at temperature in hours (``0.5``) or as printed
        (``"1/2 hr"``). Required when the figure has one curve per exposure
        time; checked against "Exposure up to ..." when the figure is valid up
        to a single exposure time.
    temperature_units:
        ``"F"`` (default), ``"C"`` or ``"K"``.

    Returns
    -------
    float
        Percent of the room-temperature value (about 100 at 70-75 °F).

    Raises
    ------
    KeyError
        No effect-of-temperature figure covers this material and property.
    ValueError
        The figure could not be digitized (e.g. a raster image), the needed
        curve has no label, the exposure is missing or not on the figure, or
        the curve is not single-valued in temperature.
    OutOfRangeError
        ``temperature`` lies outside the digitized curve.
    """
    from aerokit.materials.handbook import list_materials

    slug = material.strip().lower()
    if slug not in list_materials():
        raise KeyError(f"unknown material {material!r}")
    prop = _PROPERTY_ALIASES.get(property.strip().lower())
    if prop is None:
        raise ValueError(f"property must be one of Ftu, Fty, E, Ec; got {property!r}")
    t_f = _to_fahrenheit(float(temperature), temperature_units)
    want_h = parse_exposure_hours(exposure) if isinstance(exposure, str) else (
        None if exposure is None else float(exposure))
    if isinstance(exposure, str) and want_h is None:
        raise ValueError(f"cannot read exposure {exposure!r}; use hours (0.5) or a label like '1/2 hr'")
    figs = []
    for fid in list_figures():
        fc = load_curve(fid)
        if slug in fc.materials and fc.kind == "effect-of-temperature" and prop in _figure_properties(fc.caption):
            figs.append(fc)
    if not figs:
        raise KeyError(f"no effect-of-temperature figure for {prop} of {slug}")
    if len(figs) > 1:
        raise ValueError(f"several figures give {prop} of {slug}: {', '.join(f.figure for f in figs)}")
    fc = figs[0]
    if fc.status != "digitized":
        raise ValueError(f"figure {fc.figure} could not be digitized: {'; '.join(fc.skipped)}")
    single_prop = len(_figure_properties(fc.caption) - {"Ec"}) == 1 or _figure_properties(fc.caption) == {"E", "Ec"}
    cands: list[tuple[Curve, float | None]] = []
    for c in fc.curves:
        lp = _label_property(c.label)
        if lp is not None:
            if prop in lp:
                cands.append((c, None))
        elif single_prop:
            h = parse_exposure_hours(c.label)
            if h is not None:
                cands.append((c, h))
    if not cands:
        raise ValueError(f"figure {fc.figure}: no labeled {prop} curve (curves: {', '.join(fc.labels)}; skipped: "
                         + "; ".join(s for s in fc.skipped if "label" in s) + ")")
    by_exposure = [(c, h) for c, h in cands if h is not None]
    if by_exposure:
        if want_h is None:
            raise ValueError(f"figure {fc.figure} has one curve per exposure time; pass exposure= one of "
                             + ", ".join(repr(c.label) for c, _ in by_exposure))
        hit = [c for c, h in by_exposure if h is not None and math.isclose(h, want_h, rel_tol=1e-9)]
        if not hit:
            raise ValueError(f"figure {fc.figure} has no curve for exposure {want_h:g} hr; available: "
                             + ", ".join(repr(c.label) for c, _ in by_exposure))
        curve = hit[0]
    else:
        if len(cands) > 1:
            raise ValueError(f"figure {fc.figure}: several {prop} curves {[c.label for c, _ in cands]}")
        curve = cands[0][0]
        limit = next((parse_exposure_hours(a.split("Exposure up to", 1)[1]) for a in fc.annotations
                      if "Exposure up to" in a), None)
        if want_h is not None and limit is not None and want_h > limit * (1 + 1e-9):
            raise ValueError(f"figure {fc.figure} is valid for exposures up to {limit:g} hr; got {want_h:g} hr")
    return curve_value(fc.figure, curve.label, t_f)
