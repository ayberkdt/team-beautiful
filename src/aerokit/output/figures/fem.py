"""FEM result figures: 2-D stress contour, frame/truss deformed shape, optimised truss areas.

Colour rules: unsigned magnitude (von Mises) → sequential ``viridis``; signed stress → diverging
``RdBu_r`` centred on zero; undeformed geometry → grey context; one annotation for the peak.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from aerokit.output.figures._common import (DEFAULT_TARGET, Figure, aspect_ratio, auto_scale, boundary_edges,
                                            datawiz, save, triangles)

__all__ = ["fem2d_contour", "frame_shape", "truss_areas"]

_LABELS = {"sx": "σx", "sy": "σy", "txy": "τxy", "sr": "σr", "sz": "σz", "st": "σθ", "trz": "τrz"}


def fem2d_contour(model: Any, u: npt.NDArray[np.float64], path: str, field: str = "von_mises",
                  scale: float | None = None, target: str = DEFAULT_TARGET, title: str | None = None,
                  unit: float = 1e6, unit_name: str = "MPa") -> Figure:
    """Nodal stress contour on the deformed 2-D mesh.

    Parameters
    ----------
    model : aerokit.fem.Model
        Model with plane (T3/Q4/QM6/Q8) elements.
    u : ndarray
        Displacement vector.
    path : str
        Output path without extension.
    field : str
        ``"von_mises"``, ``"sx"``, ``"sy"``, ``"txy"`` (axisymmetric: ``"sr"``, ``"sz"``, ``"st"``, ``"trz"``).
    scale : float, optional
        Displacement magnification (default: largest displacement = 8 % of the model size).
    target : str
        datawiz size profile.
    title : str, optional
    unit, unit_name : float, str
        Stress divisor and its label (default MPa).

    Returns
    -------
    Figure
        ``report`` plus ``peak_value``, ``peak_position``, ``scale``.
    """
    from matplotlib.colors import TwoSlopeNorm
    from matplotlib.tri import Triangulation

    from aerokit.fem.elements.plane import _von_mises

    dw = datawiz()
    S = model.node_stresses(u)
    formulation = model.elements[0].format
    nu = getattr(model.elements[0], "nu", 0.0)
    names = ["sr", "sz", "st", "trz"] if formulation in ("axial", "axisymmetric") else ["sx", "sy", "txy"]
    if field == "von_mises":
        value = np.array([_von_mises(s, formulation, nu) if np.all(np.isfinite(s)) else np.nan for s in S])
        label = "von Mises stress"
    elif field in names:
        value = S[:, names.index(field)]
        label = _LABELS[field]
    else:
        raise ValueError(f"field must be von_mises or one of {', '.join(names)}")
    value = value / unit
    U = u.reshape(-1, model.ndof)[:, :2]
    k = auto_scale(model.X[:, :2], U) if scale is None else scale
    Xd = model.X[:, :2] + k * U
    tri_idx = triangles(model)
    tri = Triangulation(Xd[:, 0], Xd[:, 1], tri_idx)
    fig, ax = dw.figur("makale", hedef=target, oran=aspect_ratio(model.X[:, :2]))
    for a, b in boundary_edges(tri_idx):                               # undeformed boundary (grey context)
        ax.plot(model.X[[a, b], 0], model.X[[a, b], 1], color="0.70", lw=0.8, zorder=1)
    if field == "von_mises":
        cm = ax.tripcolor(tri, value, shading="gouraud", cmap="viridis", zorder=2)
    else:
        lim = np.nanmax(np.abs(value)) or 1.0
        cm = ax.tripcolor(tri, value, shading="gouraud", cmap="RdBu_r", norm=TwoSlopeNorm(0.0, -lim, lim), zorder=2)
    cb = fig.colorbar(cm, ax=ax, shrink=0.85)
    cb.set_label(f"{label} ({unit_name})")
    i = int(np.nanargmax(np.abs(value)))
    dw.notlar.ok(ax, (Xd[i, 0], Xd[i, 1]), f"peak {value[i]:.1f} {unit_name}")
    ax.set_aspect("equal", adjustable="box")
    pts = np.vstack([model.X[:, :2], Xd])
    pad = 0.03 * np.ptp(pts, axis=0).max()
    ax.set_xlim(pts[:, 0].min() - pad, pts[:, 0].max() + pad)
    ax.set_ylim(pts[:, 1].min() - pad, pts[:, 1].max() + pad)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    if title:
        ax.set_title(title, loc="left", pad=22)
    # note above the axes: below them it collides with the x tick labels on slender geometries
    ax.text(0.0, 1.02, f"Deformed shape ×{k:.3g}; grey line: undeformed boundary", transform=ax.transAxes,
            color="0.35", va="bottom")
    return save(fig, path, target, peak_value=float(value[i]), peak_position=model.X[i, :2].tolist(), scale=k)


def frame_shape(model: Any, u: npt.NDArray[np.float64], path: str, scale: float | None = None,
                target: str = DEFAULT_TARGET, title: str | None = None, label: str | None = None) -> Figure:
    """Frame/truss: grey undeformed and coloured deformed shape (straight lines between nodes).

    Returns ``report`` and ``scale``.
    """
    dw = datawiz()
    dim = min(model.X.shape[1], 2)
    U = u.reshape(-1, model.ndof)[:, :dim]
    k = auto_scale(model.X[:, :dim], U) if scale is None else scale
    Xd = model.X[:, :dim] + k * U
    fig, ax = dw.figur("makale", hedef=target, oran=0.55)
    color = dw.paletler.kategorik()[0]
    for e in model.elements:
        i, j = e.nodes[:2]
        ax.plot(model.X[[i, j], 0], model.X[[i, j], 1], color="0.75", lw=1.0, zorder=1)
        ax.plot(Xd[[i, j], 0], Xd[[i, j], 1], color=color, lw=1.8, zorder=2)
    n = int(np.argmax(np.linalg.norm(U, axis=1)))
    dw.notlar.ok(ax, (Xd[n, 0], Xd[n, 1]), label or f"max displacement {np.linalg.norm(U[n]) * 1e3:.2f} mm")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    if title:
        ax.set_title(title, loc="left", pad=22)
    ax.text(0.0, 1.02, f"Deformed shape ×{k:.3g}; grey: undeformed", transform=ax.transAxes, color="0.35",
            va="bottom")
    return save(fig, path, target, scale=k)


def truss_areas(model: Any, areas: npt.ArrayLike, path: str, A_min: float | None = None,
                target: str = DEFAULT_TARGET, title: str | None = None, unit: str = "m",
                area_unit: tuple[str, float] = ("cm²", 1e4)) -> Figure:
    """Optimised truss: line width proportional to area; members at the lower bound (≤ 1.01 A_min) thin grey."""
    dw = datawiz()
    A = np.asarray(areas, dtype=float)
    if A.size != len(model.elements):
        raise ValueError("number of areas must equal the number of elements")
    color = dw.paletler.kategorik()[0]
    fig, ax = dw.figur("makale", hedef=target, oran=0.55)
    amax = A.max()
    for e, a_ in zip(model.elements, A, strict=True):
        i, j = e.nodes[:2]
        at_min = A_min is not None and a_ <= 1.01 * A_min
        ax.plot(model.X[[i, j], 0], model.X[[i, j], 1], color="0.70" if at_min else color,
                lw=0.8 if at_min else 0.8 + 5.2 * a_ / amax, solid_capstyle="round", zorder=1 if at_min else 2)
    k = int(np.argmax(A))
    mid = model.X[model.elements[k].nodes[:2], :2].mean(axis=0)
    lo, hi = model.X[:, 1].min(), model.X[:, 1].max()
    span = max(hi - lo, 1e-9)
    ax.set_ylim(lo - 0.2 * span, hi + 0.6 * span)                      # free band above for the note
    ax.set_aspect("equal", adjustable="box")
    xlo, xhi = model.X[:, 0].min(), model.X[:, 0].max()
    ax.set_xlim(xlo - 0.03 * (xhi - xlo), xhi + 0.03 * (xhi - xlo))
    align = "right" if mid[0] > 0.7 * xhi + 0.3 * xlo else ("left" if mid[0] < 0.3 * xhi + 0.7 * xlo else "center")
    ax.annotate(f"largest area {A[k] * area_unit[1]:.2f} {area_unit[0]}", xy=tuple(mid),
                xytext=(mid[0], hi + 0.38 * span), ha=align, va="bottom", color="0.15",
                arrowprops={"arrowstyle": "-", "color": "0.35", "lw": 0.8})
    ax.set_xlabel(f"x ({unit})")
    ax.set_ylabel(f"y ({unit})")
    if title:
        ax.set_title(title, loc="left", pad=26)
    ax.text(0.0, 1.03, "Line width proportional to cross-section area; grey: at lower bound", transform=ax.transAxes,
            color="0.35", va="bottom")
    return save(fig, path, target)
