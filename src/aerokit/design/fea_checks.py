"""Checks a careful team shows next to every FE result ("Numerically Accurate Results", docs/14).

* :func:`mesh_verdict` — three meshes of one quantity: converging (Richardson extrapolation and fine-grid GCI via
  :func:`aerokit.aero.flow.gci`), diverging (differences grow with refinement: a stress singularity at a sharp
  corner, point load or fixed edge — the value has no limit and must not be reported), or oscillating;
* :func:`reaction_balance` — support reactions against the applied load, per component;
* :func:`averaging_gap` — averaged against unaveraged peak stress; a large gap means the mesh is too coarse where the
  peak sits (the Ansys course compares the two and a nodal-difference plot).

Thresholds that are judgements are module constants, named so that a slide can quote them.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from aerokit.aero.flow import gci

__all__ = ["GCI_OK", "AVERAGING_OK", "mesh_verdict", "reaction_balance", "averaging_gap"]

GCI_OK = 0.05
"""Fine-grid GCI below which a quantity is called converged (the course demonstrates a 5 % allowable change)."""
AVERAGING_OK = 0.10
"""Averaged vs unaveraged peak gap below which the local mesh is accepted [judgement]."""


def mesh_verdict(sizes: Sequence[float], values: Sequence[float]) -> dict:
    """Verdict on one quantity from three meshes, sizes in any consistent unit (coarse to fine in any order)."""
    if len(sizes) != 3 or len(values) != 3:
        raise ValueError("three meshes are needed")
    order = np.argsort(sizes)                       # fine first
    h = np.asarray(sizes, float)[order]
    f = np.asarray(values, float)[order]
    e21, e32 = f[1] - f[0], f[2] - f[1]             # medium - fine, coarse - medium
    if e21 == 0:
        return {"verdict": "converged", "value": float(f[0]), "gci_fine": 0.0}
    if e21 * e32 < 0:
        return {"verdict": "oscillating", "value": float(f[0]),
                "advice": "refine further or report the band between the last two meshes"}
    if abs(e21) >= abs(e32):
        return {"verdict": "diverging", "value": float(f[0]), "growth": float(e21 / e32) if e32 else float("inf"),
                "advice": "singularity: read the stress away from the corner/support/load point, add the real "
                          "fillet, or report a converging measure (99th percentile, linearised stress)"}
    g = gci(float(f[0]), float(f[1]), float(f[2]), float(h[1] / h[0]), float(h[2] / h[1]))
    return {"verdict": "converged" if g["gci_fine"] <= GCI_OK else "converging", "value": float(f[0]),
            "extrapolated": float(g["f_ext"]), "order": float(g["p"]), "gci_fine": float(g["gci_fine"])}


def reaction_balance(applied: Sequence[float], reactions: Sequence[Sequence[float]]) -> dict:
    """Sum of reaction vectors + applied load (should be ~0); relative residual against the load magnitude."""
    F = np.asarray(applied, float)
    R = np.asarray(reactions, float).sum(axis=0)
    res = F + R
    scale = max(float(np.linalg.norm(F)), 1e-300)
    return {"residual": res.tolist(), "relative": float(np.linalg.norm(res)) / scale}


def averaging_gap(averaged: float, unaveraged: float) -> dict:
    """Relative gap between unaveraged and averaged peak stress, and whether the local mesh is acceptable."""
    gap = abs(unaveraged - averaged) / max(abs(unaveraged), 1e-300)
    return {"gap": gap, "ok": gap <= AVERAGING_OK}
