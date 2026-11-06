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
    k_role = nd.get("ring_factor_by_role", {})      # e.g. {"load": 1.047} = lug eye kept to the original edge
    nmin = nd.get("ring_min_voxels", 2)
    keep = np.zeros(mesh.ne, bool)
    C = mesh.centers
    role_of = {d["id"]: d.get("role", "free") for d in setup["holes"]}
    for hid, hl in _holes(setup).items():
        if role_of.get(hid) not in roles:
            continue
        t = max(k_role.get(role_of.get(hid), k) * hl.radius, nmin * mesh.h)
        d = C - hl.center
        rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
        za = C[:, hl.axis]
        inseg = np.zeros(mesh.ne, bool)
        for a, b in hl.segments:
            inseg |= (za >= a) & (za <= b)
        keep |= inseg & (rad <= hl.radius + t)
    if roles == ("support", "load"):
        for b in nd.get("boxes_mm", []) + load_ties(setup, mesh.h):
            lo, hi = np.asarray(b["min"]) * 1e-3, np.asarray(b["max"]) * 1e-3
            keep |= np.all((lo <= C) & (hi >= C), axis=1)
        for sg in support_ties(setup, mesh.h):
            keep |= _seg_dist(C * 1e3, np.asarray(sg["a"]), np.asarray(sg["b"])) <= sg["r"]
    return keep


def _seg_dist(P: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Distance [mm] of points P (n, 3) [mm] from the segment a-b."""
    ab = b - a
    t = np.clip(((P - a) @ ab) / float(ab @ ab), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def support_ties(setup: dict[str, Any], h: float) -> list[dict[str, Any]]:
    """Automatic support-pattern bracing (``non_design.connect_supports: "x"``): every support bore is joined to the
    support bore farthest from it (the diagonal of the bolt pattern) by a frozen round bar of radius
    ``tie_radius_mm`` (default one voxel) at the mid-height of the support bores. For a 2 × 2 bolt pattern this is
    an X: it keeps the bolt pattern and its distances rigid (card: locations and distances of the supports stay
    the same) and makes every lug that reaches a boss part of ONE body. The optimiser may thicken it."""
    nd = setup.get("non_design", {})
    if nd.get("connect_supports") != "x":
        return []
    hs = _holes(setup)
    role = {d["id"]: d.get("role") for d in setup["holes"]}
    sups = [(i, hs[i]) for i in sorted(hs) if role.get(i) == "support"]
    if len(sups) < 2:
        return []
    up = sups[0][1].axis
    r = float(nd.get("tie_radius_mm", h * 1e3))
    pairs = set()
    for i, hi in sups:
        j = max((j for j, _ in sups if j != i), key=lambda j: np.linalg.norm(hs[j].center - hi.center))
        pairs.add(tuple(sorted((i, j))))
    out = []
    for i, j in sorted(pairs):
        a, b = hs[i].center * 1e3, hs[j].center * 1e3
        mid = 0.5 * (min(x for seg in hs[i].segments for x in seg) + max(x for seg in hs[i].segments for x in seg)) * 1e3
        a = a.copy(); b = b.copy(); a[up] = b[up] = mid
        out.append({"name": f"X tie {i}-{j} (auto)", "a": a.tolist(), "b": b.tolist(), "r": r})
    return out


def load_ties(setup: dict[str, Any], h: float) -> list[dict[str, Any]]:
    """Automatic lug-to-lug connection rule (``non_design.connect_loads: true``), boxes in mm.

    Every pair of load holes is joined by a frozen minimum-section tie (``tie_section_mm``, default 2 voxels, the
    filter length scale) that runs along the line between their centres, extended over both bore segments. It lies
    at the top of the support region (the highest support-bore end along the support axis), so it ties the two load
    interfaces through the mounting level and never crosses the gap between them where the mating part sits.
    Axis-aligned layouts only (the load centres differ along one axis): anything else raises.
    """
    nd = setup.get("non_design", {})
    if not nd.get("connect_loads"):
        return []
    hs = _holes(setup)
    role = {d["id"]: d.get("role") for d in setup["holes"]}
    loads = [hs[i] for i in sorted(hs) if role.get(i) == "load"]
    sups = [hs[i] for i in sorted(hs) if role.get(i) == "support"]
    if len(loads) < 2 or not sups:
        return []
    up = sups[0].axis
    if any(s_.axis != up for s_ in sups):
        raise ValueError("connect_loads: support bores must share one axis")
    top = max(b for s_ in sups for _, b in s_.segments) * 1e3
    t = float(nd.get("tie_section_mm", 2 * h * 1e3))
    out = []
    for a_, b_ in zip(loads, loads[1:]):
        ca, cb = a_.center * 1e3, b_.center * 1e3
        d = np.abs(cb - ca)
        d[up] = 0.0
        run = int(np.argmax(d))
        if np.count_nonzero(d > 1e-6) != 1:
            raise ValueError("connect_loads: load centres must differ along one axis")
        lo, hi = np.minimum(ca, cb), np.maximum(ca, cb)
        segs = [x * 1e3 for hl in (a_, b_) for seg in hl.segments for x in seg] if a_.axis == run else []
        lo[run], hi[run] = (min(segs), max(segs)) if segs else (lo[run], hi[run])
        other = 3 - up - run
        lo[other], hi[other] = ca[other] - t / 2 - 0.5 * h * 1e3, ca[other] + t / 2
        lo[up], hi[up] = top - t, top
        out.append({"name": f"tie {a_.id if hasattr(a_, 'id') else ''}-{b_.id if hasattr(b_, 'id') else ''} (auto)",
                    "min": lo.tolist(), "max": hi.tolist()})
    return out


def scaled_setup(setup: dict[str, Any], factor: float) -> dict[str, Any]:
    """Copy of the set-up with every force and moment multiplied by ``factor`` (e.g. ultimate = 1.5 × limit)."""
    s = copy.deepcopy(setup)
    for c in s["load_cases"]:
        for ld in c["loads"]:
            for key in ("force_N", "moment_Nm"):
                if key in ld:
                    ld[key] = [factor * v for v in ld[key]]
    return s


def detect_symmetry(setup: dict[str, Any], tol_mm: float = 2.0) -> dict[str, float]:
    """Mirror planes (axis -> coordinate, mm) under which the set-up maps onto itself: every hole onto a hole of the
    same role, diameter and axis, every support onto a support, and the SET of load cases onto itself (a mirrored
    case must equal some case of the set; forces flip the normal component, moments — axial vectors — flip the two
    in-plane components). The plane is the mean hole coordinate along that axis. A plane is returned only if every
    check holds within ``tol_mm`` (positions) and 1 % (loads), so a non-symmetric problem gets no symmetry."""
    hs = setup["holes"]
    role = {d["id"]: d.get("role", "free") for d in hs}
    out: dict[str, float] = {}
    for k, ax in enumerate("xyz"):
        c = float(np.mean([d["center_mm"][k] for d in hs]))
        img: dict[str, str] = {}
        for d in hs:
            m = list(d["center_mm"]); m[k] = 2 * c - m[k]
            hit = [e for e in hs if e.get("axis") == d.get("axis") and role[e["id"]] == role[d["id"]]
                   and abs(e["diameter_mm"] - d["diameter_mm"]) < tol_mm
                   and np.linalg.norm(np.subtract(e["center_mm"], m)) < tol_mm]
            if not hit:
                break
            img[d["id"]] = hit[0]["id"]
        else:
            def key(case: dict[str, Any], mirror: bool) -> list[tuple[Any, ...]]:
                rows = []
                for ld in case["loads"]:
                    h_ = img[ld["hole"]] if mirror else ld["hole"]
                    if "force_N" in ld:
                        v = np.array(ld["force_N"], float)
                        if mirror:
                            v[k] = -v[k]
                        rows.append((h_, "F", ld.get("type", "bearing"), v))
                    else:
                        v = np.array(ld["moment_Nm"], float)
                        if mirror:
                            v = -v; v[k] = -v[k]
                        rows.append((h_, "M", ld.get("type", "moment"), v))
                return sorted(rows, key=lambda r: (r[0], r[1]))

            def same(a: list[tuple[Any, ...]], b: list[tuple[Any, ...]]) -> bool:
                return len(a) == len(b) and all(x[:3] == y[:3] and np.allclose(x[3], y[3], rtol=0.01,
                                                atol=1e-6 + 0.01 * np.abs(x[3]).max()) for x, y in zip(a, b))
            cases = setup["load_cases"]
            sup_ok = sorted(img[s_["hole"]] for s_ in setup["supports"]) == sorted(s_["hole"] for s_ in setup["supports"])
            # a moment whose sign the card does not give: a case and its mirror are both admissible -> accept
            # cases that are mirror-images of themselves up to the sign of a pure-moment case
            def in_set(case: dict[str, Any]) -> bool:
                mk = key(case, True)
                if any(same(mk, key(o, False)) for o in cases):
                    return True
                pure_m = all("moment_Nm" in ld for ld in case["loads"]) or bool(case.get("sign_free"))
                if pure_m:
                    neg = [(r[0], r[1], r[2], -r[3]) for r in mk]
                    return any(same(neg, key(o, False)) for o in cases)
                return False
            if sup_ok and all(in_set(cs) for cs in cases):
                out[ax] = round(c, 3)
    return out

