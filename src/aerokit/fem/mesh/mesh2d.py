"""Structured 2-D mesh generators and consistent edge loads.

Every mesh is the image of the unit square ``(ξ, η) ∈ [0, 1]²`` under a user mapping; element nodes
are counter-clockwise. Edge lists run counter-clockwise around the domain:

``"lower"``  η = 0 (ξ increasing)    ``"right"``  ξ = 1 (η increasing)
``"upper"``  η = 1 (ξ decreasing)    ``"left"``   ξ = 0 (η decreasing)

so that along an edge the outward normal is ``(dy, −dx)/|ds|``. Edge tuples hold the end nodes
(linear elements) or ``(start, mid, end)`` (quadratic elements).
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike

from aerokit.fem.quadrature import gauss1d
from aerokit.references import cite

__all__ = ["mapped_mesh", "geometric_distribution", "rectangle", "cook", "quarter_plate_with_hole",
           "edge_load", "edge_nodes", "find"]

Mapping2D = Callable[[float, float], Sequence[float]]
Mesh2D = tuple[np.ndarray, list[list[int]], dict[str, list[tuple[int, ...]]]]


def mapped_mesh(mapping: Mapping2D, nx: int, ny: int, kind: str = "Q4",
                xi_distribution: ArrayLike | None = None, eta_distribution: ArrayLike | None = None) -> Mesh2D:
    """Structured mesh of the image of the unit square under ``mapping(ξ, η) → (x, y)``.

    Parameters
    ----------
    mapping : callable
        ``mapping(ξ, η)`` returns the physical point ``(x, y)`` [m] for ``ξ, η ∈ [0, 1]``.
    nx, ny : int
        Elements along ξ and η (``≥ 1``).
    kind : {"T3", "Q4", "QM6", "Q8"}
        Element topology (QM6 uses the Q4 topology; T3 splits each quad along its 0-2 diagonal).
    xi_distribution, eta_distribution : array_like, optional
        Strictly increasing element boundaries from 0 to 1 (``nx + 1`` / ``ny + 1`` values), e.g.
        :func:`geometric_distribution`. Default: uniform.

    Returns
    -------
    X : ndarray, shape (n_node, 2)
        Nodal coordinates [m].
    connectivity : list of list of int
        Element node lists.
    edges : dict
        ``{"lower", "right", "upper", "left"}`` → list of edge node tuples (counter-clockwise).

    Raises
    ------
    ValueError
        Unknown ``kind``, non-positive ``nx``/``ny`` or invalid distribution.
    """
    if kind == "QM6":
        kind = "Q4"                            # same topology
    if kind not in ("T3", "Q4", "Q8"):
        raise ValueError("kind must be T3 | Q4 | QM6 | Q8")
    if nx < 1 or ny < 1:
        raise ValueError("nx and ny must be ≥ 1")
    q = 2 if kind == "Q8" else 1
    xs = (np.linspace(0, 1, q * nx + 1) if xi_distribution is None
          else _with_midside(np.asarray(xi_distribution, float), q))
    es = (np.linspace(0, 1, q * ny + 1) if eta_distribution is None
          else _with_midside(np.asarray(eta_distribution, float), q))
    index = -np.ones((xs.size, es.size), dtype=int)
    points: list[Sequence[float]] = []
    for i in range(xs.size):
        for j in range(es.size):
            if q == 2 and i % 2 == 1 and j % 2 == 1:
                continue                      # serendipity: no element-centre node
            index[i, j] = len(points)
            points.append(mapping(float(xs[i]), float(es[j])))
    X = np.array(points, dtype=float)
    conn: list[list[int]] = []
    for a in range(nx):
        for b in range(ny):
            i, j = q * a, q * b
            if kind == "Q8":
                conn.append([int(v) for v in (index[i, j], index[i + 2, j], index[i + 2, j + 2], index[i, j + 2],
                                              index[i + 1, j], index[i + 2, j + 1], index[i + 1, j + 2],
                                              index[i, j + 1])])
            else:
                n0, n1, n2, n3 = (int(v) for v in (index[i, j], index[i + 1, j], index[i + 1, j + 1],
                                                   index[i, j + 1]))
                if kind == "Q4":
                    conn.append([n0, n1, n2, n3])
                else:
                    conn += [[n0, n1, n2], [n0, n2, n3]]
    edges: dict[str, list[tuple[int, ...]]] = {"lower": [], "right": [], "upper": [], "left": []}
    I, Jn = xs.size - 1, es.size - 1
    for a in range(0, I, q):
        edges["lower"].append(_edge(index, [(a + k, 0) for k in range(q + 1)]))
        edges["upper"].append(_edge(index, [(I - a - k, Jn) for k in range(q + 1)]))
    for b in range(0, Jn, q):
        edges["right"].append(_edge(index, [(I, b + k) for k in range(q + 1)]))
        edges["left"].append(_edge(index, [(0, Jn - b - k) for k in range(q + 1)]))
    return X, conn, edges


def _with_midside(d: np.ndarray, q: int) -> np.ndarray:
    """Element boundary distribution → the same with mid-side points inserted (``q = 2``)."""
    if d[0] != 0 or d[-1] != 1 or np.any(np.diff(d) <= 0):
        raise ValueError("distribution must increase strictly from 0 to 1")
    if q == 1:
        return d
    out = np.empty(2 * d.size - 1)
    out[0::2] = d
    out[1::2] = 0.5 * (d[:-1] + d[1:])
    return out


def _edge(index: np.ndarray, ij: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(int(index[i, j]) for i, j in ij)


def geometric_distribution(n: int, ratio: float) -> np.ndarray:
    """Geometric grading of ``[0, 1]`` into ``n`` intervals.

    Parameters
    ----------
    n : int
        Number of intervals.
    ratio : float
        Last interval / first interval (``> 1``: refined towards 0).

    Returns
    -------
    ndarray, shape (n + 1,)
        Boundaries from 0 to 1.
    """
    if n == 1:
        return np.array([0.0, 1.0])
    g = ratio ** (1 / (n - 1))
    h = np.cumsum(np.concatenate([[0], g ** np.arange(n)]))
    return h / h[-1]


def rectangle(Lx: float, Ly: float, nx: int, ny: int, kind: str = "Q4", x0: float = 0.0, y0: float = 0.0) -> Mesh2D:
    """Uniform mesh of the rectangle ``[x0, x0 + Lx] × [y0, y0 + Ly]`` [m] (see :func:`mapped_mesh`)."""
    return mapped_mesh(lambda s, t: (x0 + Lx * s, y0 + Ly * t), nx, ny, kind)


@cite("bergan_felippa_1985", "cook_2002", note="Cook's membrane geometry")
def cook(nx: int, ny: int, kind: str = "Q4") -> Mesh2D:
    """Cook's skew membrane: corners (0, 0), (48, 44), (48, 60), (0, 44).

    Parameters
    ----------
    nx, ny : int
        Elements along the length and the depth.
    kind : str
        Element topology (see :func:`mapped_mesh`).

    Returns
    -------
    X, connectivity, edges
        As :func:`mapped_mesh`; clamp ``"left"`` and load ``"right"`` with a total shear of 1.
    """
    A, B, C, D = map(np.array, ([0, 0], [48, 44], [48, 60], [0, 44]))

    def e(s: float, t: float) -> tuple[float, ...]:
        return tuple((1 - s) * (1 - t) * A + s * (1 - t) * B + s * t * C + (1 - s) * t * D)
    return mapped_mesh(e, nx, ny, kind)


@cite("timoshenko_goodier_1970", note="Kirsch plate geometry (quarter model)")
def quarter_plate_with_hole(a: float, L: float, nr: int, nt: int, kind: str = "Q8", ratio: float = 4.0) -> Mesh2D:
    """Quarter (``x ≥ 0, y ≥ 0``) of a ``2L × 2L`` plate with a central hole of radius ``a``.

    Parameters
    ----------
    a : float
        Hole radius [m], ``0 < a < L``.
    L : float
        Half-width of the plate [m].
    nr : int
        Elements in the radial direction ξ (hole → outer square).
    nt : int
        Elements in the angular direction η (even, so that the 45° corner is a node).
    kind : str
        Element topology.
    ratio : float
        Radial element size ratio (outer / inner), refining the mesh at the hole.

    Returns
    -------
    X, connectivity, edges
        As :func:`mapped_mesh`: ``"left"`` = hole, ``"right"`` = outer boundary,
        ``"lower"`` = symmetry line y = 0 (angle 0), ``"upper"`` = symmetry line x = 0 (angle 90°).

    Raises
    ------
    ValueError
        ``a`` outside ``(0, L)`` or odd ``nt``.
    """
    if not 0 < a < L:
        raise ValueError("hole radius must satisfy 0 < a < L")
    if nt % 2:
        raise ValueError("nt must be even (so that the 45° corner falls on a node)")

    def e(s: float, t: float) -> tuple[float, ...]:
        th = t * math.pi / 2
        inner = np.array([a * math.cos(th), a * math.sin(th)])
        outer = np.array([L, L * math.tan(th)]) if th <= math.pi / 4 else np.array([L / math.tan(th), L])
        return tuple((1 - s) * inner + s * outer)
    return mapped_mesh(e, nr, nt, kind, xi_distribution=geometric_distribution(nr, ratio))


@cite("cook_2002", note="consistent nodal loads of edge tractions")
def edge_load(X: np.ndarray, edges: Iterable[Sequence[int]],
              traction: Callable[[float, float], Sequence[float]] | None = None,
              pressure: float | None = None, format: str = "stress", t: float = 1.0, ndof: int = 2) -> np.ndarray:
    """Consistent nodal loads of a traction or pressure along mesh edges.

    Parameters
    ----------
    X : ndarray, shape (n_node, 2)
        Nodal coordinates [m].
    edges : iterable of tuple
        Edge node tuples (2 nodes: linear, 3 nodes: quadratic ``(start, mid, end)``), oriented
        counter-clockwise around the body.
    traction : callable, optional
        ``traction(x, y) → (tx, ty)`` [Pa].
    pressure : float, optional
        Normal pressure ``p`` [Pa]; positive pushes on the surface (``t = −p n_out``).
    format : {"stress", "strain", "axisymmetric"}
        Thickness factor: ``t`` (plane stress), 1 (plane strain) or ``2π r`` (axisymmetric; legacy
        alias ``"axial"``).
    t : float
        Thickness [m] for plane stress.
    ndof : int
        DOFs per node of the model (the load goes to local DOFs 0 and 1).

    Returns
    -------
    ndarray, shape (n_node · ndof,)
        ``F = ∫ Nᵀ t̄ c ds`` [N], 4-point Gauss rule per edge.

    Raises
    ------
    ValueError
        Edges with other than 2 or 3 nodes, or neither ``traction`` nor ``pressure`` given.
    """
    if traction is None and pressure is None:
        raise ValueError("give a traction function or a pressure")
    axisym = format in ("axial", "axisymmetric")
    F = np.zeros(X.shape[0] * ndof)
    s_g, w_g = gauss1d(4)
    for edge in edges:
        xe = X[list(edge), :2]
        for s, w in zip(s_g, w_g, strict=True):
            if len(edge) == 2:
                N = np.array([(1 - s) / 2, (1 + s) / 2])
                dN = np.array([-0.5, 0.5])
            elif len(edge) == 3:
                N = np.array([s * (s - 1) / 2, 1 - s * s, s * (s + 1) / 2])
                dN = np.array([s - 0.5, -2 * s, s + 0.5])
            else:
                raise ValueError("edges must have 2 or 3 nodes")
            x = N @ xe
            dx = dN @ xe
            ds = math.hypot(*dx)
            n_out = np.array([dx[1], -dx[0]]) / ds
            if pressure is not None:
                tr = -pressure * n_out
            elif traction is not None:
                tr = np.asarray(traction(*x), dtype=float)
            else:                                   # unreachable: checked on entry
                raise ValueError("give a traction function or a pressure")
            c = 2 * math.pi * x[0] if axisym else (t if format == "stress" else 1.0)
            for k, n in enumerate(edge):
                F[n * ndof] += N[k] * tr[0] * ds * w * c
                F[n * ndof + 1] += N[k] * tr[1] * ds * w * c
    return F


def edge_nodes(edges: Iterable[Sequence[int]]) -> list[int]:
    """Sorted unique node indices of an edge list."""
    return sorted({int(n) for k in edges for n in k})


def find(X: np.ndarray, condition: Callable[[float, float], bool], tol: float = 1e-9) -> list[int]:
    """Indices of the nodes for which ``condition(x, y)`` is true.

    ``tol`` is not used internally; it is kept so that callers can pass the comparison tolerance
    they used inside ``condition``.
    """
    return [i for i, (x, y) in enumerate(X[:, :2]) if condition(float(x), float(y))]
