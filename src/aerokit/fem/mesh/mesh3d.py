"""3-D mesh generation and surface loads.

:func:`box`
    Structured H8 mesh of a rectangular prism, or T4/T10 meshes that split every brick into six
    tetrahedra.
:func:`t4_to_t10`
    Adds mid-edge nodes to a straight-edged T4 mesh.
:func:`tet_mesh_from_surface`
    Tetrahedral mesh from a closed triangulated surface (STL): surface nodes + interior grid points →
    Delaunay → keep the tetrahedra whose centroid lies inside the body (generalised winding number).
    This is a preliminary-design mesh: it is not guaranteed to conform to the boundary surface; the
    volume ratio is reported.
:func:`boundary_faces`
    Faces that belong to a single tetrahedron (outer boundary).
:func:`surface_load`
    Pressure / traction on triangular (3/6-node) or quadrilateral (4-node) faces.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike
from scipy.spatial import Delaunay

from aerokit.references import cite

__all__ = ["T10_EDGE", "tet_volume", "box", "t4_to_t10", "boundary_faces", "winding_number",
           "tet_mesh_from_surface", "surface_load", "find3"]

#: T10 edge order (same as :func:`aerokit.fem.elements.solid.shape_t10`).
T10_EDGE = [(0, 1), (1, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
# Split of a brick into six tetrahedra around the 0-6 diagonal (conforming with neighbouring bricks)
_HEX_TET = [(0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6)]


def tet_volume(X: np.ndarray, t: Sequence[int]) -> float:
    """Signed volume ``((b − a) × (c − a))·(d − a)/6`` of tetrahedron ``t`` [m³]."""
    a, b, c, d = X[t[0]], X[t[1]], X[t[2]], X[t[3]]
    return float(np.dot(np.cross(b - a, c - a), d - a) / 6.0)


def _orient_positive(X: np.ndarray, tets: Iterable[Sequence[int]]) -> list[list[int]]:
    """Swap nodes 1 and 2 of negatively oriented tetrahedra."""
    out = []
    for t in tets:
        t = list(t)
        if tet_volume(X, t) < 0:
            t[1], t[2] = t[2], t[1]
        out.append(t)
    return out


def box(Lx: float, Ly: float, Lz: float, nx: int, ny: int, nz: int, kind: str = "H8",
        x0: Sequence[float] = (0.0, 0.0, 0.0)) -> tuple[np.ndarray, list[list[int]]]:
    """Mesh of the prism ``[x0, x0 + L]`` [m].

    Parameters
    ----------
    Lx, Ly, Lz : float
        Edge lengths [m].
    nx, ny, nz : int
        Bricks per direction.
    kind : {"H8", "T4", "T10"}
        Element type (T4/T10: six tetrahedra per brick).
    x0 : sequence of float
        Origin [m].

    Returns
    -------
    X : ndarray, shape (n_node, 3)
    elements : list of list of int

    Raises
    ------
    ValueError
        Unknown ``kind``.
    """
    if kind not in ("H8", "T4", "T10"):
        raise ValueError("kind must be H8 | T4 | T10")
    xs, ys, zs = (np.linspace(0, L, n + 1) + o for L, n, o in zip((Lx, Ly, Lz), (nx, ny, nz), x0, strict=True))
    idx = np.arange((nx + 1) * (ny + 1) * (nz + 1)).reshape(nx + 1, ny + 1, nz + 1)
    X = np.array([[x, y, z] for x in xs for y in ys for z in zs])
    el: list[list[int]] = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                h = [int(v) for v in (idx[i, j, k], idx[i + 1, j, k], idx[i + 1, j + 1, k], idx[i, j + 1, k],
                                      idx[i, j, k + 1], idx[i + 1, j, k + 1], idx[i + 1, j + 1, k + 1],
                                      idx[i, j + 1, k + 1])]
                if kind == "H8":
                    el.append(h)
                else:
                    el += [[h[a] for a in t] for t in _HEX_TET]
    if kind == "H8":
        return X, el
    el = _orient_positive(X, el)
    return t4_to_t10(X, el) if kind == "T10" else (X, el)


def t4_to_t10(X: ArrayLike, tets: Iterable[Sequence[int]]) -> tuple[np.ndarray, list[list[int]]]:
    """Add straight mid-edge nodes to a T4 mesh (shared edges get one node).

    Parameters
    ----------
    X : array_like, shape (n_node, 3)
    tets : iterable of 4-node lists

    Returns
    -------
    X10 : ndarray
        Coordinates with the new mid-edge nodes appended.
    tets10 : list of 10-node lists
        Node order of :class:`aerokit.fem.elements.solid.T10`.
    """
    pts = [np.asarray(x, float) for x in np.asarray(X, float)]
    middle: dict[tuple[int, int], int] = {}
    out = []
    for t in tets:
        e = [int(v) for v in t]
        for a, b in T10_EDGE:
            k = (min(t[a], t[b]), max(t[a], t[b]))
            if k not in middle:
                middle[k] = len(pts)
                pts.append(0.5 * (pts[t[a]] + pts[t[b]]))
            e.append(middle[k])
        out.append(e)
    return np.array(pts), out


def boundary_faces(tets: Iterable[Sequence[int]]) -> list[tuple[int, int, int]]:
    """Triangular faces that belong to exactly one tetrahedron, ordered with outward normals.

    Parameters
    ----------
    tets : iterable of node lists
        Positively oriented tetrahedra (only the first four nodes are used).

    Returns
    -------
    list of (a, b, c)
    """
    faces: dict[tuple[int, ...], list[tuple[int, int, int]]] = {}
    for t in tets:
        a, b, c, d = (int(v) for v in t[:4])
        for f in ((a, c, b), (a, b, d), (a, d, c), (b, c, d)):   # outward normals of a positive tetrahedron
            k = tuple(sorted(f))
            faces.setdefault(k, []).append(f)
    return [v[0] for v in faces.values() if len(v) == 1]


@cite("jacobson_kavan_2013", "vanoosterom_strackee_1983",
      note="generalised winding number; solid angle of a triangle")
def winding_number(V: np.ndarray, F: np.ndarray, P: ArrayLike) -> np.ndarray:
    """Generalised winding number of points with respect to a closed triangle surface.

    Parameters
    ----------
    V : ndarray, shape (n_vertex, 3)
        Surface vertices [m].
    F : ndarray of int, shape (n_face, 3)
        Triangles, outward oriented.
    P : array_like, shape (k, 3)
        Query points [m].

    Returns
    -------
    ndarray, shape (k,)
        ≈ 1 inside the surface, ≈ 0 outside.

    Notes
    -----
    ``w(p) = Σ Ω_f(p) / 4π`` with the triangle solid angle of Van Oosterom & Strackee (1983),
    ``tan(Ω/2) = a·(b × c) / (|a||b||c| + (a·b)|c| + (b·c)|a| + (c·a)|b|)``.
    """
    P = np.atleast_2d(np.asarray(P, dtype=float))
    w = np.zeros(P.shape[0])
    A, B, C = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    for i0 in range(0, P.shape[0], 2000):
        p = P[i0:i0 + 2000, None, :]
        a, b, c = A[None] - p, B[None] - p, C[None] - p
        la, lb, lc = (np.linalg.norm(v, axis=2) for v in (a, b, c))
        det = np.einsum("ijk,ijk->ij", a, np.cross(b, c))
        denom = la * lb * lc + np.einsum("ijk,ijk->ij", a, b) * lc + np.einsum("ijk,ijk->ij", b, c) * la \
            + np.einsum("ijk,ijk->ij", c, a) * lb
        w[i0:i0 + 2000] = (2 * np.arctan2(det, denom)).sum(axis=1) / (4 * np.pi)
    return w


def tet_mesh_from_surface(V: ArrayLike, F: ArrayLike, h: float, kind: str = "T4", boundary_margin: float = 0.3,
                          quality_threshold: float = 0.005) -> tuple[np.ndarray, list[list[int]], dict[str, Any]]:
    """Tetrahedral mesh of the volume enclosed by a closed triangle surface.

    Parameters
    ----------
    V : array_like, shape (n_vertex, 3)
        Surface vertices [m].
    F : array_like of int, shape (n_face, 3)
        Triangles (orientation is fixed automatically).
    h : float
        Target spacing of the interior grid points [m].
    kind : {"T4", "T10"}
        Element type.
    boundary_margin : float
        Interior grid points closer than ``boundary_margin · h`` to a surface vertex are dropped
        (avoids badly shaped elements).
    quality_threshold : float
        Tetrahedra with quality ``q = 6√2 V / l_rms³`` (1 for a regular tetrahedron) at or below this
        value are removed (Delaunay slivers).

    Returns
    -------
    X : ndarray
        Nodal coordinates [m].
    elements : list of list of int
        Positively oriented tetrahedra.
    info : dict
        ``volume_mesh``, ``volume_surface``, ``ratio``, ``n_element``, ``n_node``, ``n_sliver_removed``.
    """
    V = np.asarray(V, float)
    F = np.asarray(F, int)
    volume_surface = float(np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])).sum() / 6.0)
    if volume_surface < 0:
        F = F[:, [0, 2, 1]]
        volume_surface = -volume_surface
    lo, hi = V.min(axis=0), V.max(axis=0)
    axes = [np.arange(lo[i] + h / 2, hi[i], h) for i in range(3)]
    G: np.ndarray = np.array(np.meshgrid(*axes, indexing="ij")).reshape(3, -1).T
    if G.size:
        G = G[winding_number(V, F, G) > 0.5]
        # drop interior points that are too close to the surface
        if G.size and V.shape[0] * G.shape[0] < 4e7:
            d = np.min(np.linalg.norm(G[:, None, :] - V[None, :, :], axis=2), axis=1)
            G = G[d > boundary_margin * h]
    P = np.vstack([V, G]) if G.size else V.copy()
    tri = Delaunay(P)
    tet = tri.simplices
    center = P[tet].mean(axis=1)
    inside = winding_number(V, F, center) > 0.5
    tet = tet[inside]
    vol = np.array([tet_volume(P, t) for t in tet])
    # Quality q = 6√2·V / l_rms³ (1 for a regular tetrahedron): Delaunay slivers are removed; their
    # volume is negligible but they make the stiffness matrix ill-conditioned.
    edge = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    l2 = np.mean([np.sum((P[tet[:, i]] - P[tet[:, j]]) ** 2, axis=1) for i, j in edge], axis=0)
    q = 6 * np.sqrt(2) * np.abs(vol) / l2 ** 1.5
    keep = q > quality_threshold
    n_removed = int((~keep).sum())
    kept = [list(t) if v > 0 else [t[0], t[2], t[1], t[3]] for t, v, k in zip(tet, vol, keep, strict=True) if k]
    used_ids = np.unique(np.array(kept).ravel())
    new = -np.ones(P.shape[0], int)
    new[used_ids] = np.arange(used_ids.size)
    P = P[used_ids]
    tets = [[int(new[i]) for i in t] for t in kept]
    volume_mesh = sum(tet_volume(P, t) for t in tets)
    if kind == "T10":
        P, tets = t4_to_t10(P, tets)
    return P, tets, {"volume_mesh": volume_mesh, "volume_surface": volume_surface,
                     "ratio": volume_mesh / volume_surface, "n_element": len(tets), "n_node": P.shape[0],
                     "n_sliver_removed": n_removed}


@cite("dunavant_1985", note="degree-4, 6-point triangle rule for quadratic faces")
def surface_load(X: np.ndarray, faces: Iterable[Sequence[int]], pressure: float | None = None,
                 traction: Callable[[float, float, float], Sequence[float]] | None = None,
                 ndof: int = 3) -> np.ndarray:
    """Consistent nodal loads of a pressure or traction on element faces.

    Parameters
    ----------
    X : ndarray, shape (n_node, 3)
        Nodal coordinates [m].
    faces : iterable of node tuples
        Linear triangles ``(a, b, c)``, quadratic triangles ``(a, b, c, ab, bc, ca)`` or
        quadrilaterals ``(a, b, c, d)``, counter-clockwise seen from outside.
    pressure : float, optional
        Pressure [Pa]; positive pushes on the surface (``t = −p n``).
    traction : callable, optional
        ``traction(x, y, z) → (tx, ty, tz)`` [Pa].
    ndof : int
        DOFs per node of the model.

    Returns
    -------
    ndarray, shape (n_node · ndof,)
        ``F = ∫ Nᵀ t dA`` [N].

    Raises
    ------
    ValueError
        Faces with other than 3, 4 or 6 nodes, or no load given.
    """
    if traction is None and pressure is None:
        raise ValueError("give a pressure or a traction function")
    F = np.zeros(X.shape[0] * ndof)
    for f in faces:
        f = list(f)
        xe = X[f]
        if len(f) in (3, 6):
            rule = [((1 / 6, 1 / 6), 1 / 6), ((2 / 3, 1 / 6), 1 / 6), ((1 / 6, 2 / 3), 1 / 6)]
            if len(f) == 6:
                # Dunavant (1985) degree 4, 6 points; weights multiplied by the reference area 1/2
                a, b = 0.445948490915965, 0.091576213509771
                wa, wb = 0.223381589678011 / 2, 0.109951743655322 / 2
                rule = [((a, a), wa), ((1 - 2 * a, a), wa), ((a, 1 - 2 * a), wa),
                        ((b, b), wb), ((1 - 2 * b, b), wb), ((b, 1 - 2 * b), wb)]
        elif len(f) == 4:
            g = 1 / np.sqrt(3)
            rule = [((s, t), 1.0) for s in (-g, g) for t in (-g, g)]
        else:
            raise ValueError("faces must have 3, 4 or 6 nodes")
        for (s, t), w in rule:
            if len(f) == 3:
                N = np.array([1 - s - t, s, t])
                dNs = np.array([-1, 1, 0.0])
                dNt = np.array([-1, 0, 1.0])
            elif len(f) == 6:
                L = np.array([1 - s - t, s, t])
                N = np.array([L[0] * (2 * L[0] - 1), L[1] * (2 * L[1] - 1), L[2] * (2 * L[2] - 1),
                              4 * L[0] * L[1], 4 * L[1] * L[2], 4 * L[2] * L[0]])
                dNs = np.array([-(4 * L[0] - 1), 4 * L[1] - 1, 0, 4 * (L[0] - L[1]), 4 * L[2], -4 * L[2]])
                dNt = np.array([-(4 * L[0] - 1), 0, 4 * L[2] - 1, -4 * L[1], 4 * L[1], 4 * (L[0] - L[2])])
            else:
                sg = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float)
                N = 0.25 * (1 + sg[:, 0] * s) * (1 + sg[:, 1] * t)
                dNs = 0.25 * sg[:, 0] * (1 + sg[:, 1] * t)
                dNt = 0.25 * sg[:, 1] * (1 + sg[:, 0] * s)
            x = N @ xe
            n = np.cross(dNs @ xe, dNt @ xe)                 # |n| = dA/(ds dt), outward direction
            if pressure is not None:
                tr = -pressure * n
            elif traction is not None:
                tr = np.asarray(traction(*x), float) * np.linalg.norm(n)
            else:                                   # unreachable: checked on entry
                raise ValueError("give a pressure or a traction function")
            for k, d in enumerate(f):
                F[d * ndof:d * ndof + 3] += N[k] * tr * w
    return F


def find3(X: np.ndarray, condition: Callable[[float, float, float], bool]) -> list[int]:
    """Indices of the nodes for which ``condition(x, y, z)`` is true."""
    return [i for i, p in enumerate(X) if condition(*p)]
