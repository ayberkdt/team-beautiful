"""Automatic mesh-convergence study: systematic refinement, observed order, Richardson extrapolation, GCI.

Method: Celik et al. (2008), ASME J. Fluids Eng. 130:078001 — the same formulas as
:func:`aerokit.aero.flow.gci`. Usage::

    result = study(lambda n: <build a mesh with n and return the quantity>, levels=(4, 8, 16))

At every level the representative element size is taken as ``h ∝ 1/n`` (for a structured mesh ``n``
is the number of elements per edge).
"""
from __future__ import annotations

import math
import time
from collections.abc import Callable, Sequence
from typing import Any

from aerokit.aero.flow import gci
from aerokit.references import cite

__all__ = ["study"]


@cite("celik_2008", "roache_1998", note="three-grid GCI with apparent order and Richardson extrapolation")
def study(solver: Callable[[int], float], levels: Sequence[int] = (4, 8, 16), label: str = "quantity",
          Fs: float = 1.25) -> dict[str, Any]:
    """Run ``solver(n)`` on successively refined meshes and estimate the discretisation error.

    Parameters
    ----------
    solver : callable
        ``solver(n) → float``: builds the mesh with refinement parameter ``n`` and returns the scalar
        quantity of interest.
    levels : sequence of int
        At least three strictly increasing refinement levels (coarse → fine); the three finest are
        used for the GCI.
    label : str
        Name of the quantity (stored in the result).
    Fs : float
        Safety factor of the GCI (1.25 for three-grid studies).

    Returns
    -------
    dict
        ``values``, ``n``, ``duration`` [s per level], ``r21``, ``r32``, ``label``, ``interpretation``
        and the keys of :func:`aerokit.aero.flow.gci`: ``p`` (apparent order), ``f_ext`` (Richardson
        value), ``e_a``, ``e_ext``, ``gci_fine``, ``oscillatory``.

    Raises
    ------
    ValueError
        Fewer than three levels or non-increasing levels.

    Notes
    -----
    With refinement ratios ``r21 = n₁/n₂`` and ``r32 = n₂/n₃`` (1 = finest) the apparent order ``p``
    solves ``p = |ln|ε32/ε21| + q(p)| / ln r21`` and ``GCI_fine = Fs |(f₁ − f₂)/f₁| / (r21ᵖ − 1)``.
    """
    if len(levels) < 3:
        raise ValueError("at least three mesh levels are needed")
    if any(b <= a for a, b in zip(levels, levels[1:], strict=False)):
        raise ValueError("levels must increase strictly (coarse to fine)")
    values, durations = [], []
    for n in levels:
        t0 = time.perf_counter()
        values.append(float(solver(n)))
        durations.append(time.perf_counter() - t0)
    f3, f2, f1 = values[-3:]                      # coarse, medium, fine
    n3, n2, n1 = levels[-3:]
    r21, r32 = n1 / n2, n2 / n3
    if f1 == f2 == f3:
        g: dict[str, Any] = {"p": float("nan"), "f_ext": f1, "e_a": 0.0, "e_ext": 0.0, "gci_fine": 0.0,
                             "oscillatory": False}
    else:
        g = gci(f1, f2, f3, r21, r32, Fs=Fs)
    if g["oscillatory"]:
        interpretation = "oscillatory convergence: the GCI is not reliable, add a finer level"
    elif not math.isfinite(g["p"]) or g["p"] < 0.5:
        interpretation = "observed order too low: not in the asymptotic range, or a singularity is present"
    elif g["gci_fine"] < 0.01:
        interpretation = f"mesh independent (GCI {g['gci_fine'] * 100:.2f}% < 1%)"
    else:
        interpretation = (f"mesh still matters (GCI {g['gci_fine'] * 100:.2f}%); refine further or use the "
                          "Richardson value")
    return {"values": values, "n": list(levels), "duration": durations, "r21": r21, "r32": r32,
            "label": label, "interpretation": interpretation, **g}
