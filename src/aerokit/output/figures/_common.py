"""Shared figure infrastructure: datawiz-audited saving, typed reports and geometry helpers.

Every figure is built at its target size with ``datawiz`` (the user's figure-rule library) and
saved through :func:`save`, which writes PNG + PDF + a colour-vision-deficiency preview and the
audit report ``<path>.denetim.txt``. The Turkish keys of the datawiz report are normalised into the
English :class:`FigureReport`, so callers never depend on the external library's vocabulary.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import numpy.typing as npt

__all__ = ["FigureReport", "Figure", "save", "datawiz", "triangles", "boundary_edges", "aspect_ratio",
           "auto_scale", "DEFAULT_TARGET"]

DEFAULT_TARGET = "web-640"          # datawiz profile: report/screen width; "sunum-tam" for slides


def datawiz() -> Any:
    """Import the datawiz library (optional dependency) with Matplotlib's non-interactive backend."""
    import matplotlib
    matplotlib.use("Agg")
    try:
        import datawiz as dw
    except ImportError as exc:                                   # pragma: no cover - environment
        raise ImportError("figures need the 'datawiz' library on sys.path (user skill 'datawiz')") from exc
    return dw


@dataclass(frozen=True)
class FigureReport:
    """Normalised datawiz audit report."""

    errors: int
    summary: str
    files: tuple[str, ...]
    audit_file: str = ""
    cvd_preview: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False)
    warnings: int = 0

    @property
    def ok(self) -> bool:
        """True when the audit found no error (warnings are allowed)."""
        return self.errors == 0

    @classmethod
    def from_datawiz(cls, rep: Mapping[str, Any], path: str) -> FigureReport:
        """Build from the dictionary returned by ``datawiz.kaydet``."""
        text = str(rep.get("rapor", ""))
        first_line = text.splitlines()[0] if text else ""
        counts = {k: int(v) for v, k in re.findall(r"(\d+)\s+(HATA|UYARI|BİLGİ)", first_line)}
        errors = int(rep.get("hata", counts.get("HATA", 0)))
        warnings, info = counts.get("UYARI", 0), counts.get("BİLGİ", 0)
        summary = (f"datawiz audit: {errors} error(s) · {warnings} warning(s) · {info} note(s) · "
                   f"{'ready to deliver' if errors == 0 else 'NOT deliverable'}")
        return cls(errors=errors, summary=summary, files=tuple(str(f) for f in rep.get("dosyalar", ())),
                   audit_file=f"{path}.denetim.txt", cvd_preview=str(rep.get("cvd", "")), raw=dict(rep),
                   warnings=warnings)


@dataclass(frozen=True)
class Figure(Mapping[str, Any]):
    """A saved figure: its audit report plus figure-specific values (``data``).

    Mapping access returns ``report`` or a ``data`` entry, e.g. ``fig["peak_value"]``.
    """

    report: FigureReport
    data: Mapping[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        if key == "report":
            return self.report
        return self.data[key]

    def __iter__(self) -> Iterator[str]:
        yield "report"
        yield from self.data

    def __len__(self) -> int:
        return 1 + len(self.data)


def save(fig: Any, path: str, target: str = DEFAULT_TARGET, **data: Any) -> Figure:
    """Audit and save ``fig`` (PNG, PDF, CVD preview, audit text) and close it."""
    import matplotlib.pyplot as plt
    try:
        rep = datawiz().kaydet(fig, path, hedef=target, cvd=True, sessiz=True)
    finally:
        plt.close(fig)
    return Figure(FigureReport.from_datawiz(rep, path), dict(data))


# ------------------------------------------------------------------ geometry helpers
def triangles(model: Any) -> npt.NDArray[np.int64]:
    """Triangulate 2-D continuum elements from their corner nodes (Q4/Q8 → 2 triangles, T3 → 1)."""
    tri: list[list[int]] = []
    for e in model.elements:
        d = list(e.nodes)
        if len(d) == 3:
            tri.append(d[:3])
        elif len(d) in (4, 8):
            tri += [[d[0], d[1], d[2]], [d[0], d[2], d[3]]]
    if not tri:
        raise ValueError("model has no 2-D continuum elements")
    return np.array(tri, dtype=np.int64)


def boundary_edges(tri: Iterable[Iterable[int]]) -> list[tuple[int, int]]:
    """Edges that belong to exactly one triangle (outer boundary and hole boundaries)."""
    count: dict[tuple[int, int], int] = {}
    for t in tri:
        a0, a1, a2 = (int(v) for v in t)
        for a, b in ((a0, a1), (a1, a2), (a2, a0)):
            k = (min(a, b), max(a, b))
            count[k] = count.get(k, 0) + 1
    return [k for k, v in count.items() if v == 1]


def aspect_ratio(X: npt.ArrayLike) -> float:
    """Figure height/width ratio following the geometry (with room for a colour bar)."""
    P = np.asarray(X, dtype=float)
    dx, dy = np.ptp(P[:, 0]), np.ptp(P[:, 1])
    return float(np.clip(0.85 * dy / max(dx, 1e-30), 0.35, 1.1))


def auto_scale(X: npt.ArrayLike, U: npt.ArrayLike, ratio: float = 0.08) -> float:
    """Displacement magnification that makes the largest displacement ``ratio`` × model size."""
    umax = float(np.abs(np.asarray(U, dtype=float)).max())
    size = float(np.ptp(np.asarray(X, dtype=float), axis=0).max())
    return 0.0 if umax == 0 else ratio * size / umax
