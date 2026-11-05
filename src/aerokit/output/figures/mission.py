"""Mission figure: base → search area route and the search pattern in a local east/north frame."""
from __future__ import annotations

import numpy as np
import numpy.typing as npt

from aerokit.output.figures._common import DEFAULT_TARGET, Figure, datawiz, save

__all__ = ["mission_map"]


def mission_map(base_en: tuple[float, float], pattern_en: npt.ArrayLike, searched_en: npt.ArrayLike,
                area_en: npt.ArrayLike, path: str, coverage: float, time_on_station_h: float,
                target: str = DEFAULT_TARGET, title: str | None = None) -> Figure:
    """Plan view [km] centred on the search area.

    Parameters
    ----------
    base_en : (east, north) of the base [m] in the area-centred frame.
    pattern_en, searched_en : (n, 2) full pattern and the part the fuel allows [m].
    area_en : (m, 2) search-area polygon [m].
    coverage : covered fraction of the area; time_on_station_h : hours on station.
    """
    dw = datawiz()
    P = np.asarray(pattern_en, float) / 1e3
    Q = np.asarray(searched_en, float) / 1e3
    A = np.asarray(area_en, float) / 1e3
    b = np.asarray(base_en, float) / 1e3
    color = dw.paletler.kategorik()
    pts = np.vstack([P, A, b[None, :]])
    span = np.ptp(pts, axis=0)
    pad = 0.06 * span.max()
    oran = float(np.clip((span[1] + 2 * pad) / (span[0] + 2 * pad) + 0.18, 0.32, 1.0))
    fig, ax = dw.figur("makale", hedef=target, oran=oran)
    Ac = np.vstack([A, A[:1]])
    ax.fill(Ac[:, 0], Ac[:, 1], color="0.93", lw=0, zorder=0)
    ax.plot(Ac[:, 0], Ac[:, 1], color="0.55", lw=0.8, zorder=1)
    ax.plot(P[:, 0], P[:, 1], color="0.70", lw=0.8, ls="--", zorder=1)                 # not reached
    ax.plot(Q[:, 0], Q[:, 1], color=color[2], lw=1.2, zorder=2)                        # searched
    ax.plot([b[0], Q[0, 0]], [b[1], Q[0, 1]], color=color[1], lw=1.6, zorder=2)        # transit out
    ax.plot([Q[-1, 0], b[0]], [Q[-1, 1], b[1]], color=color[1], lw=1.6, ls="--", zorder=2)   # transit back
    ax.plot(*b, marker="^", color="0.1", ms=7, zorder=3)
    # label on the side away from both transit legs, so neither leg runs through it
    away = -((Q[0] - b) / max(np.hypot(*(Q[0] - b)), 1e-9) + (Q[-1] - b) / max(np.hypot(*(Q[-1] - b)), 1e-9))
    away = away / max(np.hypot(*away), 1e-9)
    ax.annotate("base", xy=(b[0], b[1]), xytext=(10 * away[0], 10 * away[1]), textcoords="offset points",
                ha="left" if away[0] > 0.3 else ("right" if away[0] < -0.3 else "center"),
                va="bottom" if away[1] > 0.3 else ("top" if away[1] < -0.3 else "center"), color="0.1")
    # corner label outside the pattern too (the lanes may run slightly past the area outline)
    corner = np.vstack([A, P]).max(axis=0)
    ax.text(corner[0], corner[1], " search area", ha="left", va="bottom", color="0.35")
    mid = 0.5 * (b + Q[0])
    # label below the outbound leg (the return leg runs above it)
    ax.annotate(f"transit {np.hypot(*(Q[0] - b)):.0f} km", xy=(mid[0], mid[1]), xytext=(0, -14),
                textcoords="offset points", ha="center", va="top", color=color[1])
    dw.notlar.ok(ax, (float(Q[-1, 0]), float(Q[-1, 1])),
                 f"{time_on_station_h:.1f} h on station, {coverage * 100:.0f} % covered")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlim(pts[:, 0].min() - pad, pts[:, 0].max() + 2.5 * pad)
    ax.set_ylim(pts[:, 1].min() - pad, pts[:, 1].max() + pad)
    ax.set_xlabel("East (km)")
    ax.set_ylabel("North (km)")
    ax.text(0.0, 1.02, "green: searched within the fuel · grey dashed: not reached", transform=ax.transAxes,
            color="0.35", va="bottom")
    if title:
        ax.set_title(title, loc="left", pad=22)
    return save(fig, path, target)
