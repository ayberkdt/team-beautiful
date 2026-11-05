"""Aircraft-load figures: V-n diagram and half-span shear/bending distribution."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import numpy.typing as npt

from aerokit.output.figures._common import DEFAULT_TARGET, Figure, datawiz, save

__all__ = ["vn_diagram", "span_distribution"]


def vn_diagram(vn: Mapping[str, Any], path: str, target: str = DEFAULT_TARGET, title: str | None = None) -> Figure:
    """V-n diagram from :func:`aerokit.aero.loads.vn_diagram`.

    The flight envelope is a light grey fill; maneuver lines are solid, gust lines dashed (colour is
    never the only cue); the governing point is the single annotation.
    """
    dw = datawiz()
    V = np.asarray(vn["V"])
    color = dw.paletler.kategorik()
    fig, ax = dw.figur("makale", hedef=target, oran=0.62)
    ax.fill_between(V, vn["n_envelope_lower"], vn["n_envelope_upper"], color="0.93", lw=0, zorder=1)
    ax.plot(V, vn["n_maneuver_upper"], color=color[0], lw=1.8, zorder=3)
    ax.plot(V, vn["n_maneuver_lower"], color=color[0], lw=1.8, zorder=3)
    ax.plot(V, vn["n_wind_upper"], color=color[1], lw=1.5, ls="--", zorder=2)
    ax.plot(V, vn["n_wind_lower"], color=color[1], lw=1.5, ls="--", zorder=2)
    ax.axhline(0, color="0.6", lw=0.8, zorder=0)
    speeds = vn["speeds"]
    top = vn["n_max"] + 0.8
    for name in ("VA", "VC", "VD"):
        # the reference line stops above its label so the line never runs through the text
        ax.vlines(speeds[name], vn["n_min"] - 0.25, top, color="0.75", lw=0.8, zorder=0)
        ax.text(speeds[name], vn["n_min"] - 0.35, name, ha="center", va="top", color="0.35")
    ax.text(V[-1], vn["n_maneuver_upper"][-1] + 0.08, "maneuver", ha="right", va="bottom", color=color[0])
    ax.text(V[-1], vn["n_wind_upper"][-1] - 0.08, "gust", ha="right", va="top", color=color[1])
    dw.notlar.ok(ax, (vn["V_n_max"], vn["n_max"]), f"n_max {vn['n_max']:.2f} ({vn['critical']})")
    ax.set_ylim(vn["n_min"] - 0.9, top)
    ax.set_xlim(0, V.max() * 1.03)
    ax.set_xlabel("Equivalent airspeed (m/s)")
    ax.set_ylabel("Load factor n")
    if title:
        ax.set_title(title, loc="left")
    return save(fig, path, target)


def span_distribution(y: npt.ArrayLike, V: npt.ArrayLike, M: npt.ArrayLike, path: str,
                      target: str = DEFAULT_TARGET, title: str | None = None) -> Figure:
    """Half-wing shear (kN) and bending moment (kN·m) along the span; two panels sharing x."""
    dw = datawiz()
    y_, V_, M_ = (np.asarray(v, dtype=float) for v in (y, V, M))
    fig, axs = dw.figur("makale", hedef=target, oran=0.75, nrows=2, sharex=True)
    color = dw.paletler.kategorik()[0]
    axs[0].plot(y_, V_ / 1e3, color=color, lw=1.8)
    axs[1].plot(y_, M_ / 1e3, color=color, lw=1.8)
    axs[0].set_ylabel("Shear (kN)")
    axs[1].set_ylabel("Moment (kN·m)")
    axs[1].set_xlabel("Span position y (m)")
    for ax in axs:
        ax.set_ylim(bottom=0)
    dw.notlar.ok(axs[1], (y_[0], M_[0] / 1e3), f"root {M_[0] / 1e3:.0f} kN·m")
    if title:
        axs[0].set_title(title, loc="left")
    return save(fig, path, target)
