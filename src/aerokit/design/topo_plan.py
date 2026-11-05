"""Small conversions and choices that come up in every topology run on the day.

* :func:`fraction_for_mass` — target mass → retained volume fraction of the design space;
* :func:`discovery_target` / :func:`mechanical_target` — the same number as Discovery's "volume reduction" and
  Mechanical's "percent to retain" (both read in the Ansys help, docs/14 §3 and §7);
* :func:`knee` — the retained volume where removing more material starts to cost stiffness fast: the point of the
  compliance–volume curve farthest from the chord between its ends, both axes scaled to [0, 1] (this repository's
  geometric rule, stated so a slide can quote it);
* :func:`trio` — mass, maximum deformation and maximum stress change against the original, the reporting format of
  the Ansys topology courses (bell crank −78 % / +11 % stress; FSAE upright −29 % / +14 % / +4 %).
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

__all__ = ["fraction_for_mass", "discovery_target", "mechanical_target", "knee", "trio"]


def fraction_for_mass(target_mass_kg: float, rho: float, design_volume_m3: float, kept_volume_m3: float = 0.0
                      ) -> float:
    """Volume fraction of the design space that gives ``target_mass_kg``; ``kept_volume_m3`` is protected solid
    (bosses, lugs) that is part of the mass but not of the optimised region."""
    if rho <= 0 or design_volume_m3 <= 0:
        raise ValueError("rho and design volume must be positive")
    f = (target_mass_kg / rho) / design_volume_m3
    if not 0 < f <= 1:
        raise ValueError(f"target mass needs {f:.3f} of the design space")
    if kept_volume_m3 >= design_volume_m3:
        raise ValueError("protected volume fills the design space")
    return f


def discovery_target(fraction: float) -> float:
    """Discovery "volume reduction" [%] for a retained fraction."""
    return 100.0 * (1.0 - fraction)


def mechanical_target(fraction: float) -> float:
    """Mechanical "percent to retain" [%] for a retained fraction."""
    return 100.0 * fraction


def knee(volumes: Sequence[float], compliances: Sequence[float]) -> dict[str, float]:
    """Knee of the compliance–volume curve (farthest point from the end-to-end chord in scaled axes)."""
    v = np.asarray(volumes, float)
    c = np.asarray(compliances, float)
    if len(v) < 3:
        raise ValueError("need at least three volumes")
    o = np.argsort(v)
    v, c = v[o], c[o]
    vs = (v - v[0]) / (v[-1] - v[0])
    cs = (c - c.min()) / (c.max() - c.min())
    a, b = np.array([vs[0], cs[0]]), np.array([vs[-1], cs[-1]])
    ab = b - a
    d = np.abs(ab[0] * (cs - a[1]) - ab[1] * (vs - a[0])) / np.linalg.norm(ab)     # distance to the chord
    i = int(np.argmax(d))
    return {"volume": float(v[i]), "compliance": float(c[i]), "distance": float(d[i])}


def trio(base: dict[str, float], new: dict[str, float]) -> dict[str, float]:
    """Percent change of mass, maximum deformation and maximum stress (keys ``mass``, ``deformation``, ``stress``)."""
    return {k: 100.0 * (new[k] / base[k] - 1.0) for k in ("mass", "deformation", "stress") if k in base and k in new}
