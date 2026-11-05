"""Conceptual-design figures: constraint diagram, sensitivity tornado, payload-range diagram."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import numpy.typing as npt

from aerokit.output.figures._common import DEFAULT_TARGET, Figure, datawiz, save

__all__ = ["constraint_diagram", "tornado", "payload_range"]


def constraint_diagram(WS: npt.ArrayLike, curves: Mapping[str, npt.ArrayLike], ws_limit: float,
                       design: tuple[float, float], path: str, governing: str = "",
                       target: str = DEFAULT_TARGET, title: str | None = None,
                       limit_label: str = "stall limit") -> Figure:
    """P/W–W/S constraint diagram with the feasible region and the design point.

    Parameters
    ----------
    WS : array
        Wing-loading grid [N/m²].
    curves : mapping
        Constraint name → P/W [W/N] on the grid (required power per weight; feasible above).
    ws_limit : float
        Maximum wing loading of the low-speed requirements [N/m²] (feasible to the left).
    design : (float, float)
        Design point (W/S, P/W).
    limit_label : str
        Name of the requirement that sets ``ws_limit`` (e.g. "stall limit", "landing limit").
    """
    dw = datawiz()
    x = np.asarray(WS, dtype=float)
    # Okabe-Ito without its yellow, which is too light on white for thin lines
    color = [c for i, c in enumerate(dw.paletler.kategorik()) if i != 3]
    fig, ax = dw.figur("makale", hedef=target, oran=0.62)
    ys = {k: np.asarray(v, float) for k, v in curves.items()}
    envelope = np.max(np.vstack(list(ys.values())), axis=0)
    top = max(float(np.nanmax(envelope)) * 1.25, design[1] * 1.4)
    # feasible region: above every constraint and left of the stall limit (limit point inserted exactly)
    xf = np.r_[x[x < ws_limit], ws_limit]
    ef = np.interp(xf, x, envelope)
    ax.fill_between(xf, ef, top, color="0.93", lw=0, zorder=0)
    lines = []
    for i, (name, y) in enumerate(ys.items()):
        (ln,) = ax.plot(x, y, color=color[i % len(color)], lw=1.8, ls="-" if i % 2 == 0 else "--", zorder=2)
        lines.append((ln, name))
    ax.axvline(ws_limit, color="0.35", lw=1.2, zorder=1)
    ax.text(ws_limit, top * 0.98, f" {limit_label}", ha="left", va="top", color="0.35")
    ax.text(xf[0] + 0.02 * (x.max() - x.min()), top * 0.97, "feasible region", ha="left", va="top", color="0.35")
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(0, top)
    dw.etiket.cizgi_sonu(ax, [ln for ln, _ in lines], [n for _, n in lines])
    lines_txt = ["design point", f"W/S {design[0]:.0f} N/m², P/W {design[1]:.2f} W/N"]
    if governing:
        lines_txt.append(f"{governing} governs")
    text = "\n".join(lines_txt)
    # note inside the feasible region (upper left), away from the direct labels at the right edge
    ax.plot(*design, "o", color="0.1", ms=5, zorder=4)
    ax.annotate(text, xy=design, xytext=(x.min() + 0.22 * (design[0] - x.min()), 0.70 * top),
                ha="left", va="bottom", color="0.1", arrowprops={"arrowstyle": "-", "color": "0.35", "lw": 0.8})
    ax.set_xlabel("Wing loading W/S (N/m²)")
    ax.set_ylabel("Power loading P/W (W/N)")
    if title:
        ax.set_title(title, loc="left")
    return save(fig, path, target)


def tornado(names: Sequence[str], low: Sequence[float], high: Sequence[float], base: float, path: str,
            quantity: str = "Installed power", unit: str = "kW", scale: float = 1e-3,
            low_labels: Sequence[str] | None = None, high_labels: Sequence[str] | None = None,
            target: str = DEFAULT_TARGET, title: str | None = None) -> Figure:
    """Horizontal tornado chart of Δ``quantity`` at the low and high end of each assumption.

    Rows are drawn in the given order from the top (pass them sorted by swing).
    """
    dw = datawiz()
    n = len(names)
    if not (len(low) == len(high) == n) or n == 0:
        raise ValueError("names, low and high must be non-empty and of equal length")
    dlo = (np.asarray(low, float) - base) * scale
    dhi = (np.asarray(high, float) - base) * scale
    edge = [dw.paletler.kategorik()[1], dw.paletler.kategorik()[0]]          # sky blue = low, orange = high
    fill = [dw.renk.alan_tonu(c) for c in edge]                              # light tone of the same hue
    fig, ax = dw.figur("makale", hedef=target, oran=float(np.clip(0.12 + 0.075 * n, 0.4, 1.1)))
    y = np.arange(n)[::-1]
    for yi, a, b in zip(y, dlo, dhi, strict=True):
        # larger bar first so that a smaller bar of the same sign stays visible on top
        for v, k in sorted(((a, 0), (b, 1)), key=lambda t: -abs(t[0]) if np.isfinite(t[0]) else 0.0):
            if np.isfinite(v):
                ax.barh(yi, v, height=0.62, color=fill[k], edgecolor=edge[k], lw=1.0, zorder=2)
    ax.axvline(0, color="0.35", lw=1.0, zorder=3)
    span = float(np.nanmax(np.abs(np.r_[dlo, dhi]))) or 1.0
    same_side = False
    for yi, a, b, i in zip(y, dlo, dhi, range(n), strict=True):
        ends = [(v, lab) for v, lab in ((a, low_labels[i] if low_labels else ""),
                                        (b, high_labels[i] if high_labels else ""))
                if np.isfinite(v) and abs(v) > 1e-9 * span]
        if len(ends) == 2 and np.sign(ends[0][0]) == np.sign(ends[1][0]):
            # both ends on one side: the inner label would sit inside the longer bar, so one label
            # "low / high" goes at the outer end
            same_side = True
            outer = max(ends[0][0], ends[1][0], key=abs)
            text = " / ".join(f"{v:+.0f}" + (f" ({lab})" if lab else "") for v, lab in ends)
            ends = [(outer, "")]
        else:
            text = ""
        for v, lab in ends:
            ax.text(v + np.sign(v) * 0.02 * span, yi, text or f"{v:+.0f}" + (f" ({lab})" if lab else ""),
                    ha="left" if v > 0 else "right", va="center", color="0.25")
    ax.set_yticks(y, list(names))
    ax.set_xlim(-1.45 * span, 1.45 * span)
    ax.set_xlabel(f"Change of {quantity.lower()} ({unit}); base {base * scale:.0f} {unit}")
    ax.text(0.0, 1.02, "blue: low value · orange: high value · pairs: low / high" if same_side
            else "blue: assumption at its low value · orange: at its high value", transform=ax.transAxes,
            color="0.35", va="bottom")
    if title:
        ax.set_title(title, loc="left", pad=22)
    return save(fig, path, target)


def payload_range(range_km: npt.ArrayLike, payload_kg: npt.ArrayLike, path: str,
                  requirement: tuple[float, float] | None = None, corners: Sequence[str] = (),
                  target: str = DEFAULT_TARGET, title: str | None = None, **_: Any) -> Figure:
    """Payload-range diagram; optional requirement point (range km, payload kg) as the single annotation."""
    dw = datawiz()
    r, p = np.asarray(range_km, float), np.asarray(payload_kg, float)
    if r.shape != p.shape or r.size < 2:
        raise ValueError("range and payload must be equal-length arrays with ≥ 2 points")
    color = dw.paletler.kategorik()[0]
    fig, ax = dw.figur("makale", hedef=target, oran=0.55)
    ax.fill_between(r, 0, p, color="0.93", lw=0, zorder=0)
    ax.plot(r, p, color=color, lw=1.8, marker="o", ms=4, zorder=2)
    for xi, yi, name in zip(r, p, corners, strict=False):
        if name:
            ax.text(xi, yi, f" {name}", ha="left", va="bottom", color="0.35")
    if requirement:
        dw.notlar.ok(ax, requirement, f"requirement {requirement[0]:.0f} km, {requirement[1]:.0f} kg")
    ax.set_xlim(0, r.max() * 1.08)
    ax.set_ylim(0, p.max() * 1.3)
    ax.set_xlabel("Range (km)")
    ax.set_ylabel("Payload (kg)")
    if title:
        ax.set_title(title, loc="left")
    return save(fig, path, target)
