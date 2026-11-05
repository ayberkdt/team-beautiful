"""Topology optimisation with Discovery-style geometric constraints: symmetry, extrusion (pull direction), and
the lightest design that meets a check (Discovery's "Minimize Volume" with a limit).

Symmetry and extrusion are *linear design-variable maps* ``x = P z``: every element of a group (mirror pair,
extrusion column) shares one variable. The density filter is not translation-invariant at the boundary, so the
filtered field is averaged over each group again, ``x̄ = A H x / Hs`` with ``A = P diag(1/n) Pᵀ``; the physical
density then obeys the constraint exactly. The driver is the top88 density-filter loop (``ft = 2``) with the
optimality-criteria update on ``z`` and the exact chain rule ``∂c/∂z = Pᵀ Hᵀ (A ∂c/∂x̄) / Hs``. With the
identity map it reproduces :func:`aerokit.optimization.topology.topopt` with ``ft = 2`` (tested).

:func:`min_volume` brackets the smallest retained volume whose thresholded design passes a user check (peak
stress against an allowable, a deflection or a frequency limit) by bisection on full topology runs; it is the
offline analogue of Discovery's Minimize Volume goal.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
import scipy.sparse as sp

from aerokit.optimization import topology as tp
from aerokit.optimization.am_filter import AMFilter2D
from aerokit.references import cite

__all__ = ["group_map", "topopt_mapped", "min_volume", "symmetry_error", "extrusion_error"]


def _union(n: int, pairs: Sequence[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    parent = np.arange(n)

    def find(i: int) -> int:
        root = i
        while parent[root] != root:
            root = parent[root]
        while parent[i] != root:
            parent[i], i = root, parent[i]
        return root

    for a, b in pairs:
        for i, j in zip(a.ravel(), b.ravel(), strict=True):
            ri, rj = find(int(i)), find(int(j))
            if ri != rj:
                parent[max(ri, rj)] = min(ri, rj)
    return np.array([find(i) for i in range(n)])


def group_map(grid: tp._Grid, mirror: Sequence[int] = (), extrude: Sequence[int] = ()) -> sp.csr_matrix:
    """``P`` (nel × n_groups) tying elements across mirror planes and along extrusion axes.

    Axes refer to the density array of :meth:`aerokit.optimization.topology._Grid.to_array`: 2-D ``(nely, nelx)``
    with row 0 at the top (axis 0 = y, axis 1 = x); 3-D ``(nelx, nely, nelz)``. ``mirror=[1]`` on a 2-D grid
    makes the design symmetric about the vertical mid-line; ``extrude=[2]`` on a 3-D grid makes every column along z
    one variable (constant cross-section, i.e. a machinable profile or a casting pull direction).
    """
    idx = grid.to_array(np.arange(grid.nel))
    pairs = [(idx, np.flip(idx, axis=a)) for a in mirror]
    for a in extrude:
        first = np.take(idx, [0], axis=a)
        pairs.append((np.broadcast_to(first, idx.shape), idx))
    root = _union(grid.nel, pairs)
    _, col = np.unique(root, return_inverse=True)
    return sp.csr_matrix((np.ones(grid.nel), (np.arange(grid.nel), col)), shape=(grid.nel, int(col.max()) + 1))


def symmetry_error(grid: tp._Grid, x: np.ndarray, axis: int) -> float:
    """max |x − mirror(x)| of an element vector."""
    a = grid.to_array(np.asarray(x, float))
    return float(np.abs(a - np.flip(a, axis=axis)).max())


def extrusion_error(grid: tp._Grid, x: np.ndarray, axis: int) -> float:
    """max over the grid of the spread of x along ``axis``."""
    a = grid.to_array(np.asarray(x, float))
    return float((a.max(axis=axis) - a.min(axis=axis)).max())


@cite("andreassen_2011", "bourdin_2001", note="top88 density-filter loop and OC update, applied to reduced variables")
def topopt_mapped(problem: tp.Problem, volume: float, rmin: float, P: sp.spmatrix | None = None,
                  move: float = 0.2, tol: float = 0.01, max_iter: int = 400,
                  am: str | AMFilter2D | None = None) -> dict[str, Any]:
    """Compliance minimisation (sum over load cases) with ``x = P z`` and a density filter.

    ``am`` ('S', 'N', 'E', 'W'; 2-D grids only) adds the overhang filter of :mod:`aerokit.optimization.am_filter`
    after the density filter, with the base plate on that side; use a smaller ``move`` (0.05–0.1) with it.

    Returns the same keys as :func:`topology.topopt` that the rest of aerokit reads: ``x``, ``xfiz`` (arrays),
    ``compliance`` (history), ``compliance_final``, ``iteration``, ``converged``, ``gray``, ``U``, plus ``z``.
    """
    grid = problem.grid
    nel = grid.nel
    P = sp.identity(nel, format="csr") if P is None else sp.csr_matrix(P)
    if P.shape[0] != nel:
        raise ValueError("P must have one row per element")
    dens = tp.Density(grid, rmin, 2, problem.passive)
    counts = np.asarray(P.sum(axis=0)).ravel()
    A = (P @ sp.diags(1.0 / counts) @ P.T).tocsr()
    passive = problem.passive

    amf = (am if isinstance(am, AMFilter2D) else AMFilter2D(am)) if am else None
    if amf is not None and not isinstance(grid, tp.Grid2D):
        raise ValueError("the AM filter is implemented for 2-D grids")

    def physical(xv: np.ndarray) -> np.ndarray:
        xt = A @ dens.intermediate(xv)
        if amf is not None:
            xt = grid.vector(amf.forward(grid.to_array(xt)))
        return dens._apply_passive(xt)

    def chain(d: np.ndarray, xv: np.ndarray) -> np.ndarray:
        d = np.array(d, float)
        d[passive > 0] = 0.0
        if amf is not None:
            xt = A @ dens.intermediate(xv)
            d = grid.vector(amf.backward(grid.to_array(xt), grid.to_array(d)))
        return dens.Ht @ ((A @ d) / dens.Hs)

    z = np.full(P.shape[1], float(volume))
    x = P @ z
    xphys = physical(x)
    hist: list[float] = []
    loop, change = 0, 1.0
    while change > tol and loop < max_iter:
        loop += 1
        c, dcf, _ = problem.analysis(xphys)
        hist.append(c)
        dz = P.T @ chain(dcf, x)
        dvz = P.T @ chain(np.ones(nel), x)
        dvz = np.where(dvz > 0, dvz, counts * 1e-9 + 1e-12)
        l1, l2 = 0.0, 1e9
        while (l2 - l1) > 1e-3 * (l1 + l2):
            lmid = 0.5 * (l1 + l2)
            Be = np.sqrt(np.maximum(-dz / dvz / lmid, 0.0))
            znew = np.maximum(0.0, np.maximum(z - move, np.minimum(1.0, np.minimum(z + move, z * Be))))
            xphys = physical(P @ znew)
            if xphys.sum() > volume * nel:
                l1 = lmid
            else:
                l2 = lmid
        change = float(np.max(np.abs(znew - z)))
        z = znew
        x = P @ z
    c_final, _, U = problem.analysis(xphys)
    return {"x": grid.to_array(x), "xfiz": grid.to_array(xphys), "z": z, "compliance": np.array(hist),
            "compliance_final": c_final, "iteration": loop, "converged": change <= tol,
            "gray": tp.gray_measure(xphys), "U": U}


def min_volume(run: Callable[[float], Any], passes: Callable[[Any], bool], lo: float = 0.1, hi: float = 0.6,
               tol: float = 0.02) -> dict[str, Any]:
    """Smallest volume fraction in ``[lo, hi]`` whose design passes, by bisection (needs ``passes(run(hi))``).

    ``run(v)`` returns a design (e.g. a ``topopt`` result); ``passes(design)`` applies the check. Each step is a
    full topology run, so keep ``tol`` coarse (0.02 = two percent of the design space).
    """
    top = run(hi)
    if not passes(top):
        return {"feasible": False, "volume": hi, "design": top, "runs": 1}
    best_v, best, runs = hi, top, 1
    a, b = lo, hi
    while b - a > tol:
        m = 0.5 * (a + b)
        d = run(m)
        runs += 1
        if passes(d):
            b, best_v, best = m, m, d
        else:
            a = m
    return {"feasible": True, "volume": best_v, "design": best, "runs": runs}
