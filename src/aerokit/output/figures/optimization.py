"""Optimisation figures: SIMP density map."""
from __future__ import annotations

import numpy as np
import numpy.typing as npt

from aerokit.output.figures._common import DEFAULT_TARGET, Figure, datawiz, save

__all__ = ["topology_map"]


def topology_map(x: npt.ArrayLike, path: str, target: str = DEFAULT_TARGET, title: str | None = None,
                 note: str | None = None) -> Figure:
    """SIMP density field (``nely × nelx`` array, row 0 on top). White = void, black = solid."""
    dw = datawiz()
    rho = np.asarray(x, dtype=float)
    if rho.ndim != 2:
        raise ValueError("x must be a 2-D (nely, nelx) array")
    ny, nx = rho.shape
    fig, ax = dw.figur("makale", hedef=target, oran=float(np.clip(0.9 * ny / nx + 0.12, 0.42, 1.0)))
    im = ax.imshow(rho, cmap="Greys", vmin=0.0, vmax=1.0, origin="upper", interpolation="nearest",
                   extent=(0, nx, ny, 0))
    cb = fig.colorbar(im, ax=ax, fraction=0.046 * ny / nx, pad=0.03)     # colour bar as tall as the map
    cb.set_label("Density")
    ax.set_aspect("equal")
    ax.set_xlabel("x (elements)")
    ax.set_ylabel("y (elements)")
    if title:
        ax.set_title(title, loc="left", pad=26 if note else 6)
    if note:                                                           # under the title, above the axes
        ax.text(0.0, 1.03, note, transform=ax.transAxes, color="0.35", va="bottom")
    return save(fig, path, target)
