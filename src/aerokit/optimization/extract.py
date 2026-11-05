"""From a density field to CAD: smooth 2-D contours (DXF) and a closed 3-D surface (STL).

Ansys Student cannot export geometry, but Discovery and SpaceClaim import DXF sketches and STL bodies. This module
turns an aerokit topology result into either, so a preview can be rebuilt in Discovery (extrude the DXF profile,
or validate the STL as a faceted body) instead of being redrawn by hand.

* :func:`contours` — marching squares on the element-centred density at ``level`` (0.5 by default), with linear
  interpolation along cell edges; the field is padded with void so every ring closes; ambiguous saddle cells are
  resolved with the cell-centre average (Lorensen-style asymptotic choice). Rings come out as closed ``(n, 2)``
  arrays in physical units (element size ``h``, row 0 of a 2-D aerokit array is the top).
* :func:`taubin` — λ|μ smoothing of a closed ring (Taubin 1995): removes the staircase without shrinking the shape
  the way plain Laplacian smoothing does.
* :func:`to_dxf` — contours → outer rings and holes (:func:`aerokit.cad.surface.classify_rings`) → DXF polylines in mm.
* :func:`surface_nets` — naive surface nets on a 3-D field: one vertex per sign-changing cell at the mean of its edge
  crossings, one quad per sign-changing grid edge, split into triangles; watertight by construction for a padded
  field. :func:`write_stl` writes binary STL.
"""
from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

from aerokit.cad.dxf import write_dxf
from aerokit.cad.surface import classify_rings, signed_area
from aerokit.references import cite

__all__ = ["contours", "taubin", "to_dxf", "surface_nets", "laplacian_smooth", "write_stl", "mesh_volume",
           "ring_area"]


def _grid_2d(field: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    f = np.pad(np.asarray(field, float), 1, constant_values=0.0)
    ny, nx = f.shape
    # sample (i, j) of the padded field = element centre; row 0 at the top of the original array
    xs = (np.arange(nx) - 0.5) * h
    ys = (ny - 1 - np.arange(ny) - 0.5) * h
    return f, xs, ys


def contours(field: np.ndarray, level: float = 0.5, h: float = 1.0) -> list[np.ndarray]:
    """Closed iso-lines of a 2-D element field ``(nely, nelx)`` at ``level``, in units of ``h``."""
    f, xs, ys = _grid_2d(field, h)
    ny, nx = f.shape
    inside = f > level

    def cross(p: tuple[int, int], q: tuple[int, int]) -> tuple[float, float]:
        (i1, j1), (i2, j2) = p, q
        a, b = f[i1, j1], f[i2, j2]
        t = 0.5 if a == b else (level - a) / (b - a)
        return (xs[j1] + t * (xs[j2] - xs[j1]), ys[i1] + t * (ys[i2] - ys[i1]))

    # edges of a cell (top-left corner i, j): 0 top, 1 right, 2 bottom, 3 left, as pairs of sample indices
    def edge_key(i: int, j: int, e: int) -> tuple[int, int, int]:
        return {0: (i, j, 0), 1: (i, j + 1, 1), 2: (i + 1, j, 0), 3: (i, j, 1)}[e]   # (row, col, horiz=0/vert=1)

    def edge_pt(i: int, j: int, e: int) -> tuple[float, float]:
        if e == 0:
            return cross((i, j), (i, j + 1))
        if e == 1:
            return cross((i, j + 1), (i + 1, j + 1))
        if e == 2:
            return cross((i + 1, j), (i + 1, j + 1))
        return cross((i, j), (i + 1, j))

    # case index: bit 0 tl, 1 tr, 2 br, 3 bl; segments as edge pairs
    table: dict[int, list[tuple[int, int]]] = {
        1: [(3, 0)], 2: [(0, 1)], 3: [(3, 1)], 4: [(1, 2)], 6: [(0, 2)], 7: [(3, 2)], 8: [(2, 3)], 9: [(2, 0)],
        11: [(2, 1)], 12: [(1, 3)], 13: [(1, 0)], 14: [(0, 3)]}
    nxt: dict[tuple, tuple] = {}
    pts: dict[tuple, tuple[float, float]] = {}
    for i in range(ny - 1):
        for j in range(nx - 1):
            c = (int(inside[i, j]) | int(inside[i, j + 1]) << 1 | int(inside[i + 1, j + 1]) << 2
                 | int(inside[i + 1, j]) << 3)
            if c in (0, 15):
                continue
            if c in (5, 10):                         # saddle: decide by the centre value
                centre = 0.25 * (f[i, j] + f[i, j + 1] + f[i + 1, j] + f[i + 1, j + 1]) > level
                if c == 5:
                    segs = [(3, 2), (1, 0)] if centre else [(3, 0), (1, 2)]
                else:
                    segs = [(0, 1), (2, 3)] if not centre else [(0, 3), (2, 1)]
            else:
                segs = table[c]
            for a, b in segs:                        # oriented so that inside is on the left
                ka, kb = edge_key(i, j, a), edge_key(i, j, b)
                pts.setdefault(ka, edge_pt(i, j, a))
                pts.setdefault(kb, edge_pt(i, j, b))
                nxt[ka] = kb
    rings: list[np.ndarray] = []
    seen: set[tuple] = set()
    for start in list(nxt):
        if start in seen:
            continue
        ring, k = [], start
        while k not in seen and k in nxt:
            seen.add(k)
            ring.append(pts[k])
            k = nxt[k]
        if len(ring) >= 3:
            rings.append(np.array(ring))
    return rings


def ring_area(ring: np.ndarray) -> float:
    """Unsigned area of a closed ring."""
    return abs(float(signed_area(np.asarray(ring, float))))


@cite("taubin_1995", note="lambda|mu smoothing of a closed polyline")
def taubin(ring: np.ndarray, iterations: int = 10, lam: float = 0.5, mu: float = -0.53) -> np.ndarray:
    """λ|μ smoothing of a closed polyline (Taubin 1995); keeps the size, removes the voxel staircase."""
    r = np.asarray(ring, float).copy()
    for _ in range(iterations):
        for w in (lam, mu):
            nb = 0.5 * (np.roll(r, 1, axis=0) + np.roll(r, -1, axis=0))
            r = r + w * (nb - r)
    return r


def to_dxf(path: str | Path, field: np.ndarray, h_mm: float, level: float = 0.5, smooth: int = 10) -> dict:
    """Write the iso-contours of a 2-D density as closed DXF polylines (mm); returns areas and ring counts."""
    rings = [taubin(r, smooth) if smooth else r for r in contours(field, level, h_mm)]
    regions = classify_rings(rings)
    polys = [reg["outer"] for reg in regions] + [hole for reg in regions for hole in reg["holes"]]
    write_dxf(path, polygons=polys, unit="mm")
    area = sum(ring_area(reg["outer"]) - sum(ring_area(hh) for hh in reg["holes"]) for reg in regions)
    return {"path": str(path), "regions": len(regions), "holes": sum(len(reg["holes"]) for reg in regions),
            "area_mm2": area}


def surface_nets(field: np.ndarray, level: float = 0.5, h: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Closed triangle surface ``(vertices (n, 3), faces (m, 3))`` of a 3-D field ``(nx, ny, nz)`` at ``level``."""
    f = np.pad(np.asarray(field, float), 1, constant_values=0.0)
    s = f > level
    nx, ny, nz = f.shape
    corners = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)])
    cube_edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if np.abs(corners[i] - corners[j]).sum() == 1]
    vid = -np.ones((nx - 1, ny - 1, nz - 1), int)
    verts: list[np.ndarray] = []
    for x in range(nx - 1):
        for y in range(ny - 1):
            for z in range(nz - 1):
                vals = np.array([f[x + a, y + b, z + c] for a, b, c in corners])
                ins = vals > level
                if ins.all() or not ins.any():
                    continue
                acc, n = np.zeros(3), 0
                for i, j in cube_edges:
                    if ins[i] != ins[j]:
                        t = (level - vals[i]) / (vals[j] - vals[i])
                        acc += corners[i] + t * (corners[j] - corners[i])
                        n += 1
                vid[x, y, z] = len(verts)
                verts.append(np.array([x, y, z]) + acc / n)
    faces = []
    for axis in range(3):
        u, v = [a for a in range(3) if a != axis]
        # along the edge axis start at the padding layer (index 0), across it the four cells need index >= 1
        rng = [range(n - 1) if a == axis else range(1, n - 1) for a, n in enumerate((nx, ny, nz))]
        for x in rng[0]:
            for y in rng[1]:
                for z in rng[2]:
                    p = [x, y, z]
                    q = list(p)
                    q[axis] += 1
                    if q[axis] >= (nx, ny, nz)[axis] or s[tuple(p)] == s[tuple(q)]:
                        continue
                    # the four cells around the edge p->q
                    cells = []
                    for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1)):
                        c = list(p)
                        c[u] -= du
                        c[v] -= dv
                        cells.append(vid[tuple(c)])
                    if min(cells) < 0:
                        continue
                    a, b, c_, d = cells
                    if s[tuple(p)]:                  # inside -> outside along +axis: keep the normal along +axis
                        quad = (a, b, c_, d) if axis != 1 else (a, d, c_, b)
                    else:
                        quad = (a, d, c_, b) if axis != 1 else (a, b, c_, d)
                    faces += [(quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])]
    V = (np.array(verts) - 1.0 + 0.5) * h          # back to the unpadded frame, element centres at (i + 0.5) h
    return V, np.array(faces, int)


@cite("taubin_1995", note="lambda|mu smoothing of a triangle mesh")
def laplacian_smooth(V: np.ndarray, F: np.ndarray, iterations: int = 5, lam: float = 0.5, mu: float = -0.53
                     ) -> np.ndarray:
    """Taubin λ|μ smoothing of a triangle mesh (vertex positions only)."""
    n = len(V)
    nbrs: list[set[int]] = [set() for _ in range(n)]
    for a, b, c in F:
        nbrs[a] |= {b, c}
        nbrs[b] |= {a, c}
        nbrs[c] |= {a, b}
    idx = [np.fromiter(s, int) for s in nbrs]
    P = np.asarray(V, float).copy()
    for _ in range(iterations):
        for w in (lam, mu):
            mean = np.array([P[i].mean(axis=0) if len(i) else P[k] for k, i in enumerate(idx)])
            P = P + w * (mean - P)
    return P


def mesh_volume(V: np.ndarray, F: np.ndarray) -> float:
    """Signed enclosed volume (divergence theorem); positive for outward-facing triangles."""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)


def write_stl(path: str | Path, V: np.ndarray, F: np.ndarray, name: str = "aerokit topology") -> str:
    """Binary STL; units are those of ``V`` (pass mm for Discovery)."""
    tri = V[F]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-300)
    with open(path, "wb") as fh:
        fh.write(name.encode("ascii", "replace")[:80].ljust(80, b" "))
        fh.write(struct.pack("<I", len(F)))
        for k in range(len(F)):
            fh.write(struct.pack("<12fH", *nrm[k], *tri[k, 0], *tri[k, 1], *tri[k, 2], 0))
    return str(path)


def _edges_shared_twice(F: np.ndarray) -> bool:
    e = np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    return bool((counts == 2).all())


def watertight(F: np.ndarray) -> bool:
    """Every edge belongs to exactly two triangles (closed and manifold)."""
    return _edges_shared_twice(np.asarray(F, int))


def edge_report(F: np.ndarray) -> dict[str, int]:
    """Counts of open edges (one triangle) and non-manifold edges (more than two); a closed surface has no open edge.

    Surface nets gives non-manifold edges where two solid voxels touch only along an edge; the surface is still
    closed. Discovery reads such STL as a faceted body; thicken the member or raise the minimum thickness if a
    tool refuses it.
    """
    e = np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1)
    _, counts = np.unique(e, axis=0, return_counts=True)
    return {"open": int((counts == 1).sum()), "non_manifold": int((counts > 2).sum()), "edges": int(len(counts))}


__all__ += ["watertight", "edge_report"]



def mass_preserving_level(field: np.ndarray, target_volume: float, h: float = 1.0, lo: float = 0.05,
                          hi: float = 0.95, tol: float = 1e-3) -> float:
    """Iso-level whose surface-nets volume equals ``target_volume`` (same units as ``h``³), by bisection.

    Thin members (one or two voxels) lose volume at the 0.5 iso-level; lowering the level restores the mass of the
    thresholded design so that the exported geometry is checked at the right mass.
    """
    def vol(level: float) -> float:
        V, F = surface_nets(field, level, h)
        return mesh_volume(V, F) if len(F) else 0.0

    a, b = lo, hi                                  # volume falls as the level rises
    if not vol(b) <= target_volume <= vol(a):
        raise ValueError("target volume outside the range of iso-levels")
    while b - a > tol:
        m = 0.5 * (a + b)
        if vol(m) > target_volume:
            a = m
        else:
            b = m
    return 0.5 * (a + b)


__all__ += ["mass_preserving_level"]
