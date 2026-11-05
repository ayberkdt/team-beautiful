"""Hole detection, bolt/lug classification and the editable load + boundary set-up of a voxel bracket.

Holes are found slice by slice: for each axis and each voxel slice normal to it, void regions enclosed by material
in that slice are candidate hole sections; sections that overlap in consecutive slices are chained into a tube;
tubes that are round (fill ratio of the equivalent circle and radial spread) are holes. Tubes on one axis line with
gaps between them (a clevis: two arms, one pin) are merged into one hole with several segments.

Classification (a proposal, written to JSON for a human to override) [Y]:

* holes on several axes → the axis with the most holes carries the bolt holes (supports), the others the lugs (loads);
* holes on one axis → the largest group of equal diameters (±12 %) are bolts, the rest lugs; if every hole has
  the same diameter, the hole farthest from the centroid of the others is the lug.

The set-up JSON (lengths in mm, forces in N, moments in N m) is the single place where supports, load cases and
non-design regions are defined; :func:`apply_setup` turns it into nodal forces and fixed DOFs on a
:class:`~aerokit.bracket.voxfem.VoxelMesh`.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

from aerokit.bracket.geometry import VoxelModel
from aerokit.bracket.voxfem import H8_CORNER, VoxelMesh

__all__ = ["Hole", "detect_holes", "classify", "propose_setup", "apply_setup", "non_design_mask", "save_setup",
           "load_setup", "Applied"]

_AXV = np.eye(3)


@dataclass
class Hole:
    """A through or blind hole: axis index (0 x, 1 y, 2 z), centre on the axis line [m], radius [m], segments
    [(lo, hi)] along the axis [m] where material surrounds it."""

    id: str
    axis: int
    center: np.ndarray
    radius: float
    segments: list[tuple[float, float]]
    roundness: float = 0.0

    @property
    def length(self) -> float:
        return sum(b - a for a, b in self.segments)

    def to_json(self) -> dict[str, Any]:
        return {"id": self.id, "axis": "xyz"[self.axis], "center_mm": [round(1e3 * c, 3) for c in self.center],
                "diameter_mm": round(2e3 * self.radius, 3),
                "segments_mm": [[round(1e3 * a, 3), round(1e3 * b, 3)] for a, b in self.segments],
                "roundness": round(self.roundness, 3)}

    @staticmethod
    def from_json(d: dict[str, Any]) -> Hole:
        return Hole(d["id"], "xyz".index(d["axis"]), np.asarray(d["center_mm"], float) * 1e-3,
                    d["diameter_mm"] * 0.5e-3, [(a * 1e-3, b * 1e-3) for a, b in d["segments_mm"]],
                    d.get("roundness", 0.0))


def _sections(sl: np.ndarray, min_area: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """Enclosed void regions of a 2-D slice: list of (mask, pixel coords)."""
    lab, n = ndimage.label(~sl)
    if n == 0:
        return []
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]).tolist())
    out = []
    for k in range(1, n + 1):
        if k in border:
            continue
        pix = np.argwhere(lab == k)
        if len(pix) >= min_area:
            out.append((lab == k, pix))
    return out


def detect_holes(vm: VoxelModel, min_diameter_vox: float = 3.0, max_roundness: float = 0.35,
                 min_fill: float = 0.6, min_length_vox: int = 2) -> list[Hole]:
    """Round holes of the voxel model (see module notes)."""
    s = vm.solid
    h = vm.h
    tubes: list[dict[str, Any]] = []
    min_area = int(np.floor(np.pi * (min_diameter_vox / 2) ** 2))
    for ax in range(3):
        sm = np.moveaxis(s, ax, 0)
        prev: list[dict[str, Any]] = []
        for k in range(sm.shape[0]):
            cur = []
            for mask, pix in _sections(sm[k], min_area):
                hit = None
                for t in prev:
                    if (t["mask"] & mask).sum() > 0.5 * min(mask.sum(), t["mask"].sum()):
                        hit = t
                        break
                if hit is None:
                    hit = {"ax": ax, "k0": k, "k1": k, "areas": [], "cent": [], "spread": []}
                    tubes.append(hit)
                c = pix.mean(0)
                r = np.sqrt(len(pix) / np.pi)
                # roundness: spread of the boundary radius of the section
                er = mask & ~ndimage.binary_erosion(mask)
                bp = np.argwhere(er)
                rad = np.linalg.norm(bp + 0.0 - c, axis=1) + 0.5
                spread = float(np.std(rad) / max(np.mean(rad), 1e-9)) if len(bp) > 3 else 1.0
                bb = pix.max(0) - pix.min(0) + 1
                fill = len(pix) / (np.pi / 4 * bb[0] * bb[1])
                hit.update(k1=k, mask=mask)
                hit["areas"].append(len(pix))
                hit["cent"].append(c)
                hit["spread"].append(spread if fill >= min_fill else 1.0)
                cur.append(hit)
            prev = cur
    holes: list[Hole] = []
    for t in tubes:
        if len(t["areas"]) < min_length_vox:          # a pocket one voxel deep is not a bore
            continue
        spread = float(np.median(t["spread"]))
        if spread > max_roundness:
            continue
        ax = t["ax"]
        i, j = [a for a in range(3) if a != ax]
        c2 = np.mean(t["cent"], axis=0)
        r = np.sqrt(np.median(t["areas"]) / np.pi) * h
        center = np.zeros(3)
        center[i] = vm.origin[i] + (c2[0] + 0.5) * h
        center[j] = vm.origin[j] + (c2[1] + 0.5) * h
        lo, hi = vm.origin[ax] + t["k0"] * h, vm.origin[ax] + (t["k1"] + 1) * h
        center[ax] = 0.5 * (lo + hi)
        holes.append(Hole("", ax, center, r, [(lo, hi)], spread))
    # merge collinear tubes (clevis arms) on the same axis line
    merged: list[Hole] = []
    for hl in sorted(holes, key=lambda q: (q.axis, q.segments[0][0])):
        for m in merged:
            if m.axis != hl.axis:
                continue
            off = np.delete(m.center - hl.center, m.axis)
            if np.linalg.norm(off) < 0.5 * max(m.radius, hl.radius) and abs(m.radius - hl.radius) < 0.25 * m.radius:
                m.segments.append(hl.segments[0])
                lo = min(a for a, _ in m.segments)
                hi = max(b for _, b in m.segments)
                m.center[m.axis] = 0.5 * (lo + hi)
                break
        else:
            merged.append(hl)
    merged.sort(key=lambda q: (q.axis, round(q.center[0], 6), round(q.center[1], 6), round(q.center[2], 6)))
    for n, hl in enumerate(merged, 1):
        hl.id = f"H{n}"
    return merged


def classify(holes: list[Hole]) -> dict[str, str]:
    """Proposed role of each hole: "support" (bolt) or "load" (lug) — see module notes."""
    if not holes:
        return {}
    if len(holes) == 1:
        return {holes[0].id: "load"}
    axes = [hl.axis for hl in holes]
    counts = {a: axes.count(a) for a in set(axes)}
    if len(counts) > 1:
        bolt_axis = max(counts, key=lambda a: (counts[a], -a))
        r_bolt = float(np.median([hl.radius for hl in holes if hl.axis == bolt_axis]))
        out: dict[str, str] = {}
        for hl in holes:
            if hl.axis == bolt_axis:
                out[hl.id] = "support"
            else:                                       # a small off-axis void is a pocket, not a lug bore [Y]
                out[hl.id] = "load" if hl.radius >= 0.6 * r_bolt else "free"
        if "load" not in out.values():
            largest = max((hl for hl in holes if hl.axis != bolt_axis), key=lambda q: q.radius)
            out[largest.id] = "load"
        return out
    d = np.array([hl.radius for hl in holes])
    groups: list[list[int]] = []
    for k in np.argsort(d):
        for g in groups:
            if abs(d[k] - d[g[0]]) <= 0.12 * d[g[0]]:
                g.append(int(k))
                break
        else:
            groups.append([int(k)])
    if len(groups) > 1:
        big = max(groups, key=lambda g: (len(g), -d[g[0]]))
        return {hl.id: ("support" if k in big else "load") for k, hl in enumerate(holes)}
    C = np.array([hl.center for hl in holes])
    far = int(np.argmax([np.linalg.norm(C[k] - np.delete(C, k, 0).mean(0)) for k in range(len(holes))]))
    return {hl.id: ("load" if k == far else "support") for k, hl in enumerate(holes)}


def propose_setup(vm: VoxelModel, holes: list[Hole], magnitude_N: float = 10_000.0,
                  temperature_C: float = 300.0, ring_factor: float = 0.75,
                  roles: dict[str, str] | None = None) -> dict[str, Any]:
    """Editable set-up JSON: holes with roles, fixed bolt bores, three load cases (±x, ±y, ±z unit directions
    of ``magnitude_N`` at every lug, bearing type) and non-design rings of ``ring_factor`` × radius."""
    roles = roles or classify(holes)
    lugs = [hl for hl in holes if roles.get(hl.id) == "load"]
    cases = []
    for name, d in (("LC1 +x", [1, 0, 0]), ("LC2 +y", [0, 1, 0]), ("LC3 +z", [0, 0, 1])):
        loads = [{"hole": hl.id, "type": "bearing", "force_N": [magnitude_N * c / max(len(lugs), 1) for c in d]}
                 for hl in lugs]
        if loads:
            cases.append({"name": name, "loads": loads})
    lo, hi = vm.bbox()
    return {
        "_about": ("Editable bracket set-up (lengths mm, forces N, moments N m). Roles and loads are a PROPOSAL "
                   "from aerokit.bracket.features [Y]: check every hole role, load direction and magnitude "
                   "against the organisers' drawing before trusting any result."),
        "name": vm.name, "units": {"length": "mm", "force": "N", "moment": "N m"},
        "voxel_mm": round(vm.h * 1e3, 6), "origin_mm": [round(1e3 * v, 6) for v in vm.origin],
        "bbox_mm": [[round(1e3 * v, 3) for v in lo], [round(1e3 * v, 3) for v in hi]],
        "temperature_C": temperature_C,
        "holes": [dict(hl.to_json(), role=roles.get(hl.id, "free")) for hl in holes],
        "supports": [{"hole": hl.id, "type": "fixed_bore"} for hl in holes if roles.get(hl.id) == "support"],
        "load_cases": cases,
        "non_design": {"ring_factor": ring_factor, "ring_min_voxels": 2, "boxes_mm": []},
        "build_direction": "+z",
        "load_case_weights": None,
    }


def save_setup(setup: dict[str, Any], path: str | Path) -> Path:
    p = Path(path)
    p.write_text(json.dumps(setup, indent=1, ensure_ascii=False), encoding="utf-8")
    return p


def load_setup(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _holes(setup: dict[str, Any]) -> dict[str, Hole]:
    return {d["id"]: Hole.from_json(d) for d in setup["holes"]}


def _bore_nodes(mesh: VoxelMesh, hl: Hole, surface: np.ndarray, tol_vox: float = 0.9) -> np.ndarray:
    """Nodes on the bore wall of ``hl``: mesh nodes that are corners of an EMPTY voxel whose centre lies inside the
    hole cylinder (within a segment). Only the staircase wall facing the hole is taken — not the annulus on the end
    faces (an earlier radius rule r + 0.9 h clamped that annulus too and made bolted supports ~17 % too stiff
    against a conforming T10 model). Falls back to the radius rule when the hole is narrower than one voxel."""
    nx, ny, nz = mesh.solid.shape
    ijk = np.argwhere(~mesh.solid)
    if len(ijk):
        c = mesh.origin + mesh.h * (ijk + 0.5)
        d = c - hl.center
        rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
        za = c[:, hl.axis]
        ins = np.zeros(len(c), bool)
        for a, b in hl.segments:
            ins |= (za >= a) & (za <= b)
        hv = ijk[ins & (rad < hl.radius)]
        if len(hv):
            corner = ((H8_CORNER + 1) / 2).astype(int)
            g = np.unique(np.concatenate([((hv[:, 0] + k[0]) * (ny + 1) + hv[:, 1] + k[1]) * (nz + 1) + hv[:, 2] + k[2]
                                          for k in corner]))
            pos = np.searchsorted(mesh.grid_node, g)
            pos = np.clip(pos, 0, len(mesh.grid_node) - 1)
            hit = mesh.grid_node[pos] == g
            nodes = pos[hit]
            if len(nodes):
                return np.unique(nodes)
    X = mesh.X[surface]
    d = X - hl.center
    rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
    za = X[:, hl.axis]
    inseg = np.zeros(len(X), bool)
    for a, b in hl.segments:
        inseg |= (za >= a - 1e-9) & (za <= b + 1e-9)
    return surface[inseg & (rad <= hl.radius + tol_vox * mesh.h)]


@dataclass
class Applied:
    """Loads and supports on a mesh: F (ndof, n_cases) [N], fixed DOFs, case names, per-hole node sets."""

    F: np.ndarray
    fixed: np.ndarray
    names: list[str]
    nodes: dict[str, np.ndarray]
    load_points: dict[str, np.ndarray]


def apply_setup(mesh: VoxelMesh, setup: dict[str, Any]) -> Applied:
    """Nodal forces and fixed DOFs of the set-up (see module notes for the load distributions).

    * ``fixed_bore``: all three DOFs of the bore nodes (Ansys "Fixed Support" on the hole face);
    * ``bolt_seat``: all DOFs of the face nodes in the annulus r … ``seat_factor`` r on the segment end
      ``face`` ("lo" or "hi") (bolted joint seat);
    * load ``force``: equal share per bore node (uniform traction on the face, as an Ansys "Force" on a face);
    * load ``bearing``: the radial part with weight max(0, n·d) on the loaded half (projected-area cosine
      distribution, as an Ansys "Bearing Load"); an axial part, if any, uniform;
    * load ``moment``: F_i = M × r_i / Σ|r_i⊥|² (rigid distribution about the hole centre; zero net force).
    """
    holes = _holes(setup)
    surface = mesh.surface_nodes()
    nodes = {hid: _bore_nodes(mesh, hl, surface) for hid, hl in holes.items()}
    fixed: list[np.ndarray] = []
    for s in setup.get("supports", []):
        hl = holes[s["hole"]]
        typ = s.get("type", "fixed_bore")
        if typ == "fixed_bore":
            nn = nodes[s["hole"]]
        elif typ == "bolt_seat":
            k = s.get("seat_factor", 1.8)
            face = s.get("face", "lo")
            za = mesh.X[surface, hl.axis]
            edge = min(a for a, _ in hl.segments) if face == "lo" else max(b for _, b in hl.segments)
            d = mesh.X[surface] - hl.center
            rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
            nn = surface[(np.abs(za - edge) < 0.25 * mesh.h) & (rad <= k * hl.radius + 0.5 * mesh.h)]
        else:
            raise ValueError(f"unknown support type {typ!r} (fixed_bore, bolt_seat)")
        if len(nn) == 0:
            raise ValueError(f"support on {s['hole']}: no mesh nodes found (voxel too coarse?)")
        dofs = s.get("dofs", [0, 1, 2])
        fixed.append((3 * nn[:, None] + np.asarray(dofs)[None, :]).ravel())
    if not fixed:
        raise ValueError("set-up has no supports")
    cases = setup.get("load_cases", [])
    if not cases:
        raise ValueError("set-up has no load cases")
    F = np.zeros((mesh.ndof, len(cases)))
    points: dict[str, np.ndarray] = {}
    for c, case in enumerate(cases):
        for ld in case["loads"]:
            hl = holes[ld["hole"]]
            nn = nodes[ld["hole"]]
            if len(nn) == 0:
                raise ValueError(f"load on {ld['hole']}: no mesh nodes on the bore")
            points[ld["hole"]] = hl.center
            typ = ld.get("type", "bearing")
            if typ in ("force", "bearing"):
                f = np.asarray(ld["force_N"], float)
                a = _AXV[hl.axis]
                fa = (f @ a) * a
                fr = f - fa
                w_ax = np.full(len(nn), 1.0 / len(nn))
                if typ == "force":
                    w = w_ax
                    contrib = np.outer(w, f)
                else:
                    d = mesh.X[nn] - hl.center
                    d -= np.outer(d @ a, a)
                    nrm = np.linalg.norm(d, axis=1)
                    nrm[nrm == 0] = 1.0
                    if np.linalg.norm(fr) > 0:
                        w = np.maximum(0.0, (d / nrm[:, None]) @ (fr / np.linalg.norm(fr)))
                        if w.sum() == 0:
                            w = w_ax.copy()
                        w /= w.sum()
                    else:
                        w = w_ax
                    contrib = np.outer(w, fr) + np.outer(w_ax, fa)
                for k in range(3):
                    np.add.at(F[:, c], 3 * nn + k, contrib[:, k])
            elif typ == "moment":
                M = np.asarray(ld["moment_Nm"], float)
                r = mesh.X[nn] - mesh.X[nn].mean(axis=0)          # about the node centroid: zero net force
                mhat = M / np.linalg.norm(M)
                rp = r - np.outer(r @ mhat, mhat)
                f = np.cross(M, rp) / np.sum(rp * rp)
                for k in range(3):
                    np.add.at(F[:, c], 3 * nn + k, f[:, k])
            else:
                raise ValueError(f"unknown load type {typ!r} (force, bearing, moment)")
    fixed_all = np.unique(np.concatenate(fixed))
    F[fixed_all] = 0.0
    return Applied(F, fixed_all, [c["name"] for c in cases], nodes, points)


def non_design_mask(mesh: VoxelMesh, setup: dict[str, Any],
                    roles: tuple[str, ...] = ("support", "load")) -> np.ndarray:
    """(ne,) True for elements kept solid: a ring around every support/load hole (``ring_factor`` × r, at least
    ``ring_min_voxels`` voxels) over its segments, plus ``boxes_mm``."""
    nd = setup.get("non_design", {})
    k = nd.get("ring_factor", 0.75)
    nmin = nd.get("ring_min_voxels", 2)
    keep = np.zeros(mesh.ne, bool)
    C = mesh.centers
    role_of = {d["id"]: d.get("role", "free") for d in setup["holes"]}
    for hid, hl in _holes(setup).items():
        if role_of.get(hid) not in roles:
            continue
        t = max(k * hl.radius, nmin * mesh.h)
        d = C - hl.center
        rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
        za = C[:, hl.axis]
        inseg = np.zeros(mesh.ne, bool)
        for a, b in hl.segments:
            inseg |= (za >= a) & (za <= b)
        keep |= inseg & (rad <= hl.radius + t)
    if roles == ("support", "load"):
        for b in nd.get("boxes_mm", []):
            lo, hi = np.asarray(b["min"]) * 1e-3, np.asarray(b["max"]) * 1e-3
            keep |= np.all((lo <= C) & (hi >= C), axis=1)
    return keep


def scaled_setup(setup: dict[str, Any], factor: float) -> dict[str, Any]:
    """Copy of the set-up with every force and moment multiplied by ``factor`` (e.g. ultimate = 1.5 × limit)."""
    s = copy.deepcopy(setup)
    for c in s["load_cases"]:
        for ld in c["loads"]:
            for key in ("force_N", "moment_Nm"):
                if key in ld:
                    ld[key] = [factor * v for v in ld[key]]
    return s
