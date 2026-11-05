"""Bracket geometry: parametric drawing (constructive solid geometry in JSON) and voxelisation.

Drawing format (``units`` "mm" by default; every length in the file is in that unit)::

    {"name": "...", "units": "mm",
     "solids": [
        {"op": "add", "type": "box", "min": [x, y, z], "max": [x, y, z]},
        {"op": "add", "type": "cylinder", "p0": [x, y, z], "p1": [x, y, z], "radius": r},
        {"op": "add", "type": "prism", "axis": "z", "polygon": [[a, b], ...], "range": [lo, hi]},
        {"op": "cut", "type": "cylinder", ...}            # a hole
     ]}

Operations are applied in order (later ``cut`` removes from everything added before it). A prism is a polygon
extruded along ``axis``; its polygon coordinates are (x, y) for axis z, (x, z) for axis y and (y, z) for axis x.
:func:`arc` makes polygon points of circular arcs (rounded corners, curved arms).

Voxelisation:

* :func:`voxelize_drawing` — 2×2×2 sub-samples per voxel, solid when ≥ 4 of 8 lie inside;
* :func:`voxelize_surface` — closed triangle surface (STL/STEP mesh): ray parity along x, y and z through the voxel
  centres, majority vote of the three (robust to a few open edges).
"""
from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from matplotlib.path import Path as MplPath

__all__ = ["VoxelModel", "Drawing", "arc", "load_drawing", "voxelize_drawing", "voxelize_surface",
           "drawing_to_surface", "member_thickness", "UNIT_TO_M"]

UNIT_TO_M = {"m": 1.0, "mm": 1e-3, "cm": 1e-2, "in": 0.0254}
_AX = {"x": 0, "y": 1, "z": 2}
_PLANE = {2: (0, 1), 1: (0, 2), 0: (1, 2)}


@dataclass
class VoxelModel:
    """Boolean voxel field; ``origin`` is the corner of voxel (0, 0, 0) [m], ``h`` the edge [m]."""

    solid: np.ndarray
    h: float
    origin: np.ndarray
    name: str = ""
    source: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
    frac: np.ndarray | None = None        # solid volume fraction of every voxel (same shape), None = 0/1

    def frac_of_solid(self) -> np.ndarray:
        """(n_solid,) volume fraction of the solid voxels in ``np.argwhere(solid)`` order (1 without ``frac``)."""
        if self.frac is None:
            return np.ones(int(self.solid.sum()))
        return np.clip(self.frac[self.solid], 0.0, 1.0)

    @property
    def volume_frac(self) -> float:
        """Volume [m³] from the solid fraction of ALL voxels (partial-volume estimate of the part volume)."""
        if self.frac is None:
            return self.volume
        return float(np.clip(self.frac, 0.0, 1.0).sum()) * self.h ** 3

    @property
    def shape(self) -> tuple[int, int, int]:
        nx, ny, nz = self.solid.shape
        return int(nx), int(ny), int(nz)

    @property
    def volume(self) -> float:
        """Solid volume [m³]."""
        return float(self.solid.sum()) * self.h ** 3

    def centers(self, idx: np.ndarray | None = None) -> np.ndarray:
        """Centres [m] of the voxels ``idx`` (k, 3) (default: all solid voxels)."""
        ijk = np.argwhere(self.solid) if idx is None else np.asarray(idx)
        return self.origin + self.h * (ijk + 0.5)

    def bbox(self) -> tuple[np.ndarray, np.ndarray]:
        """(min, max) corner of the solid voxels [m]."""
        ijk = np.argwhere(self.solid)
        return self.origin + self.h * ijk.min(0), self.origin + self.h * (ijk.max(0) + 1)


def arc(center: Sequence[float], radius: float, a0_deg: float, a1_deg: float, n: int = 16) -> list[list[float]]:
    """Points of a circular arc from angle a0 to a1 (degrees, counter-clockwise if a1 > a0)."""
    a = np.radians(np.linspace(a0_deg, a1_deg, n))
    return [[center[0] + radius * math.cos(t), center[1] + radius * math.sin(t)] for t in a]


@dataclass
class Drawing:
    """A parametric bracket drawing (lengths in metres after loading)."""

    name: str
    solids: list[dict[str, Any]]
    raw: dict[str, Any] = field(default_factory=dict)

    def inside(self, P: np.ndarray) -> np.ndarray:
        """Membership of points ``P`` (n, 3) [m]."""
        P = np.asarray(P, float)
        inside = np.zeros(len(P), bool)
        for s in self.solids:
            m = _member(s, P)
            inside = inside | m if s.get("op", "add") == "add" else inside & ~m
        return inside

    def bbox(self) -> tuple[np.ndarray, np.ndarray]:
        lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
        for s in self.solids:
            if s.get("op", "add") != "add":
                continue
            a, b = _bbox(s)
            lo, hi = np.minimum(lo, a), np.maximum(hi, b)
        return lo, hi


def _member(s: dict[str, Any], P: np.ndarray) -> np.ndarray:
    t = s["type"]
    if t == "box":
        lo, hi = np.asarray(s["min"]), np.asarray(s["max"])
        return np.all((lo <= P) & (hi >= P), axis=1)
    if t == "cylinder":
        p0, p1 = np.asarray(s["p0"], float), np.asarray(s["p1"], float)
        d = p1 - p0
        L = np.linalg.norm(d)
        u = d / L
        q = P - p0
        t_ = q @ u
        r2 = np.einsum("ij,ij->i", q, q) - t_ ** 2
        return (t_ >= 0) & (t_ <= L) & (r2 <= s["radius"] ** 2)
    if t == "prism":
        ax = _AX[s["axis"]]
        i, j = _PLANE[ax]
        lo, hi = s["range"]
        path = MplPath(np.asarray(s["polygon"], float))
        m = (P[:, ax] >= lo) & (P[:, ax] <= hi)
        out = np.zeros(len(P), bool)
        if m.any():
            out[m] = path.contains_points(P[m][:, [i, j]])
        return out
    if t == "sphere":
        c = np.asarray(s["center"], float)
        return np.sum((P - c) ** 2, axis=1) <= s["radius"] ** 2
    raise ValueError(f"unknown solid type {t!r} (box, cylinder, prism, sphere)")


def _bbox(s: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    t = s["type"]
    if t == "box":
        return np.asarray(s["min"], float), np.asarray(s["max"], float)
    if t == "cylinder":
        p = np.array([s["p0"], s["p1"]], float)
        u = (p[1] - p[0]) / np.linalg.norm(p[1] - p[0])
        ext = s["radius"] * np.sqrt(np.clip(1 - u * u, 0.0, 1.0))      # exact extent of the end discs
        return p.min(0) - ext, p.max(0) + ext
    if t == "prism":
        ax = _AX[s["axis"]]
        i, j = _PLANE[ax]
        poly = np.asarray(s["polygon"], float)
        lo, hi = np.zeros(3), np.zeros(3)
        lo[[i, j]], hi[[i, j]] = poly.min(0), poly.max(0)
        lo[ax], hi[ax] = s["range"]
        return lo, hi
    if t == "sphere":
        c = np.asarray(s["center"], float)
        return c - s["radius"], c + s["radius"]
    raise ValueError(f"unknown solid type {t!r}")


def _scale_solid(s: dict[str, Any], k: float) -> dict[str, Any]:
    out = dict(s)
    for key in ("min", "max", "p0", "p1", "center", "range"):
        if key in s:
            out[key] = [float(v) * k for v in s[key]]
    if "radius" in s:
        out["radius"] = float(s["radius"]) * k
    if "polygon" in s:
        out["polygon"] = [[float(a) * k, float(b) * k] for a, b in s["polygon"]]
    return out


def load_drawing(src: str | Path | dict[str, Any]) -> Drawing:
    """Read a drawing JSON (path or dict) and convert its lengths to metres."""
    raw = src if isinstance(src, dict) else json.loads(Path(src).read_text(encoding="utf-8"))
    k = UNIT_TO_M[raw.get("units", "mm")]
    solids = [_scale_solid(s, k) for s in raw["solids"]]
    if not any(s.get("op", "add") == "add" for s in solids):
        raise ValueError("drawing has no 'add' solid")
    return Drawing(raw.get("name", "bracket"), solids, raw)


def voxelize_drawing(d: Drawing, h: float, pad: int = 0, sub: int = 3) -> VoxelModel:
    """Voxels of edge ``h`` [m] covering the drawing; ``sub``³ samples per voxel give the solid fraction ``frac``;
    a voxel is solid when more than half of its samples are inside."""
    lo, hi = d.bbox()
    n = np.maximum(np.ceil((hi - lo) / h - 1e-9).astype(int), 1) + 2 * pad
    origin = lo - pad * h
    off = (np.arange(sub) + 0.5) / sub
    ii, jj, kk = np.meshgrid(np.arange(n[0]), np.arange(n[1]), np.arange(n[2]), indexing="ij")
    base = np.column_stack([ii.ravel(), jj.ravel(), kk.ravel()]).astype(float)
    count = np.zeros(len(base))
    for a in off:
        for b in off:
            for c in off:
                count += d.inside(origin + h * (base + [a, b, c]))
    frac = (count / sub ** 3).reshape(n)
    solid = frac > 0.5
    return VoxelModel(solid, h, origin, d.name, "drawing", {"sub": sub}, frac)


# --------------------------------------------------------------------------------------- surfaces
def _parity_axis(V: np.ndarray, F: np.ndarray, origin: np.ndarray, h: float, n: np.ndarray, ax: int) -> np.ndarray:
    """Inside test by ray parity along axis ``ax`` through voxel centres."""
    i, j = _PLANE[ax]
    T = V[F]                                                      # (m, 3, 3)
    # tiny irrational shift of the ray positions keeps rays off edges and vertices
    shift = np.array([0.371390676, 0.618033989]) * 1e-6 * h
    a0, b0 = origin[i] + 0.5 * h + shift[0], origin[j] + 0.5 * h + shift[1]
    ta, tb, tc = T[:, :, i], T[:, :, j], T[:, :, ax]
    ia0 = np.clip(np.ceil((ta.min(1) - a0) / h).astype(int), 0, n[i] - 1)
    ia1 = np.clip(np.floor((ta.max(1) - a0) / h).astype(int), -1, n[i] - 1)
    ib0 = np.clip(np.ceil((tb.min(1) - b0) / h).astype(int), 0, n[j] - 1)
    ib1 = np.clip(np.floor((tb.max(1) - b0) / h).astype(int), -1, n[j] - 1)
    cols: list[np.ndarray] = []
    zs: list[np.ndarray] = []
    for t in np.flatnonzero((ia1 >= ia0) & (ib1 >= ib0)):
        A, B = np.meshgrid(np.arange(ia0[t], ia1[t] + 1), np.arange(ib0[t], ib1[t] + 1), indexing="ij")
        A, B = A.ravel(), B.ravel()
        pa, pb = a0 + A * h, b0 + B * h
        (x1, x2, x3), (y1, y2, y3) = ta[t], tb[t]
        det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(det) < 1e-30:
            continue
        l1 = ((y2 - y3) * (pa - x3) + (x3 - x2) * (pb - y3)) / det
        l2 = ((y3 - y1) * (pa - x3) + (x1 - x3) * (pb - y3)) / det
        l3 = 1 - l1 - l2
        ok = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        if not ok.any():
            continue
        z = l1[ok] * tc[t, 0] + l2[ok] * tc[t, 1] + l3[ok] * tc[t, 2]
        cols.append(A[ok] * n[j] + B[ok])
        zs.append(z)
    inside = np.zeros((n[i], n[j], n[ax]), bool)
    if not cols:
        return np.moveaxis(inside, [0, 1, 2], [i, j, ax])
    col = np.concatenate(cols)
    z = np.concatenate(zs)
    order = np.lexsort((z, col))
    col, z = col[order], z[order]
    starts = np.flatnonzero(np.r_[True, col[1:] != col[:-1]])
    ends = np.r_[starts[1:], len(col)]
    cz = origin[ax] + (np.arange(n[ax]) + 0.5) * h
    for s, e in zip(starts, ends, strict=True):
        c = col[s]
        zz = z[s:e]
        if len(zz) % 2:                       # a ray through a shared edge/vertex is counted twice: merge duplicates
            keep = np.r_[True, np.diff(zz) > 1e-7 * h]
            zz = zz[keep]
            if len(zz) % 2:
                continue                                           # open surface along this ray: skip it
        k = np.searchsorted(zz, cz)                                # number of crossings below the centre
        inside[c // n[j], c % n[j], :] = (k % 2) == 1
    return np.moveaxis(inside, [0, 1, 2], [i, j, ax])


def voxelize_surface(V: np.ndarray, F: np.ndarray, h: float, pad: int = 0, name: str = "", sub: int = 3) -> VoxelModel:
    """Voxelise a closed triangle surface (vertices [m]); majority vote of ray parity along x, y and z on a grid
    ``sub`` times finer, averaged to the solid fraction ``frac`` of each voxel."""
    V = np.asarray(V, float)
    F = np.asarray(F, int)
    lo, hi = V.min(0), V.max(0)
    n = np.maximum(np.ceil((hi - lo) / h - 1e-9).astype(int), 1) + 2 * pad
    origin = lo - pad * h
    votes = sum(_parity_axis(V, F, origin, h / sub, sub * n, ax).astype(int) for ax in range(3))
    fine = np.asarray(votes >= 2, dtype=float)                                     # sub × sub × sub cells per voxel
    frac = fine.reshape(n[0], sub, n[1], sub, n[2], sub).mean(axis=(1, 3, 5))
    return VoxelModel(frac > 0.5, h, origin, name, "surface", {"triangles": int(len(F)), "sub": sub}, frac)


def drawing_to_surface(vm: VoxelModel) -> tuple[np.ndarray, np.ndarray]:
    """Closed triangle surface (vertices [m], faces) of a voxel model: the exposed voxel faces (blocky)."""
    s = np.pad(vm.solid, 1)
    quads: list[np.ndarray] = []
    corners = {  # outward normal direction → the 4 corners (offsets) of the face, counter-clockwise from outside
        (0, -1): [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
        (0, 1): [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],
        (1, -1): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
        (1, 1): [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],
        (2, -1): [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
        (2, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
    }
    for (ax, sgn), cs in corners.items():
        nb = np.roll(s, -sgn, axis=ax)
        idx = np.argwhere(s & ~nb) - 1
        if len(idx):
            quads.append(idx[:, None, :] + np.array(cs)[None, :, :])
    Q = np.concatenate(quads)                                     # (nq, 4, 3) integer corners
    P, inv = np.unique(Q.reshape(-1, 3), axis=0, return_inverse=True)
    q = inv.reshape(-1, 4)
    Fc = np.vstack([q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
    return vm.origin + vm.h * P.astype(float), Fc


def member_thickness(solid: np.ndarray, h: float) -> dict[str, float]:
    """Local member thickness of a voxel body from the ridge of its Euclidean distance transform.

    Ridge voxels (local maxima of the distance to the nearest empty voxel, centre to centre) carry the half-thickness
    of the member they sit in; thickness ≈ 2 d − ½ voxel (exact to ±½ voxel: a 5- or 6-voxel plate gives 5.5). Returns the minimum and the 10th percentile of the ridge thickness in metres and
    in voxels (a member below ~5 voxels is under-resolved for bending stiffness, see docs/22 §4).
    """
    from scipy import ndimage
    d = ndimage.distance_transform_edt(np.pad(solid, 1))[1:-1, 1:-1, 1:-1]
    ridge = solid & (d >= ndimage.maximum_filter(d, size=3)) & (d > 0)
    t = 2.0 * d[ridge] - 0.5
    if t.size == 0:
        return {"min_m": float("nan"), "p10_m": float("nan"), "min_vox": float("nan"), "p10_vox": float("nan")}
    return {"min_m": float(t.min() * h), "p10_m": float(np.percentile(t, 10) * h), "min_vox": float(t.min()),
            "p10_vox": float(np.percentile(t, 10))}
