"""Conforming quadratic-tetrahedron check (the analogue of Ansys Mechanical's default SOLID187 mesh).

gmsh (OpenCASCADE) meshes the exact B-rep of the initial design — or a closed STL — with 10-node tetrahedra;
this module assembles the linear-elastic stiffness (4-point Gauss rule, exact for Bᵀ D B of the quadratic tet),
applies the same set-up JSON as the voxel model (fixed bores; bearing / force / moment on bores) with
consistent nodal loads, solves with PARDISO (or SuperLU) and reports deformation, compliance and von Mises
(nodal average of element values evaluated at the nodes).

gmsh node order of the 10-node tetrahedron, checked on 2026-11-04 by comparing midside coordinates with the edge
midpoints: vertices 0-3, then edges (0,1) (1,2) (2,0) (3,0) (3,2) (3,1).

Why it matters: the voxel model's staircase boundary under-predicts stress concentrations at holes and fillets
(plate-with-hole Kt −4 … −33 % in ``scripts/bracket_validate.py``); this model resolves curved boundaries the way
Ansys does, so its numbers are the ones to compare with an Ansys run, and the voxel-vs-T10 difference is a
quantified discrepancy cause.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from aerokit.bracket import voxfem
from aerokit.bracket.features import Hole
from aerokit.references import cite

__all__ = ["TetMesh", "mesh_cad", "mesh_drawing", "static_t10", "evaluate_setup"]

_EDGES = [(0, 1), (1, 2), (2, 0), (3, 0), (3, 2), (3, 1)]
_a, _b = 0.5854101966249685, 0.1381966011250105
_GP = np.array([[_b, _b, _b], [_a, _b, _b], [_b, _a, _b], [_b, _b, _a]])
_GW = np.full(4, 1.0 / 24.0)


def _dN(p: np.ndarray) -> np.ndarray:
    """Derivatives (10, 3) of the T10 shape functions at natural point p = (ξ, η, ζ)."""
    xi, et, ze = p
    L = np.array([1 - xi - et - ze, xi, et, ze])
    dL = np.array([[-1, -1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    d = np.zeros((10, 3))
    for i in range(4):
        d[i] = (4 * L[i] - 1) * dL[i]
    for k, (i, j) in enumerate(_EDGES):
        d[4 + k] = 4 * (L[i] * dL[j] + L[j] * dL[i])
    return d


_NODES_NAT = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0.5, 0, 0], [0.5, 0.5, 0], [0, 0.5, 0],
                       [0, 0, 0.5], [0, 0.5, 0.5], [0.5, 0, 0.5]], float)
_DN_GP = np.array([_dN(p) for p in _GP])            # (4, 10, 3)
_DN_NODES = np.array([_dN(p) for p in _NODES_NAT])  # (10, 10, 3)


@dataclass
class TetMesh:
    X: np.ndarray            # (nn, 3) [m]
    T: np.ndarray            # (ne, 10)
    faces: np.ndarray        # (nf, 6) boundary 6-node triangles
    info: dict[str, Any]

    @property
    def ndof(self) -> int:
        return 3 * len(self.X)

    @property
    def volume(self) -> float:
        J = np.einsum("gnk,enl->egkl", _DN_GP, self.X[self.T])
        return float(np.einsum("eg,g->", np.linalg.det(J), _GW))


def _from_gmsh(gmsh: Any) -> TetMesh:
    tags, coord, _ = gmsh.model.mesh.getNodes()
    X: np.ndarray = np.asarray(coord, float).reshape(-1, 3) * 1e-3     # model in mm → m
    lut = np.zeros(int(tags.max()) + 1, dtype=np.int64)
    lut[tags.astype(np.int64)] = np.arange(len(tags))
    ty, _, en = gmsh.model.mesh.getElements(3)
    T: np.ndarray = lut[np.asarray(en[list(ty).index(11)], np.int64)].reshape(-1, 10)
    ty2, _, en2 = gmsh.model.mesh.getElements(2)
    F: np.ndarray = lut[np.asarray(en2[list(ty2).index(9)], np.int64)].reshape(-1, 6)
    used = np.unique(T)
    if len(used) != len(X):                                            # drop orphan nodes (curves, points)
        new = -np.ones(len(X), np.int64)
        new[used] = np.arange(len(used))
        X, T, F = X[used], new[T], new[F]
    return TetMesh(X, T, F, {})


def mesh_cad(path: str | Path, size_mm: float, curvature: int = 12) -> TetMesh:
    """10-node tet mesh of a STEP/IGES file (gmsh OCC import, lengths in mm in the model)."""
    import gmsh
    t0 = time.perf_counter()
    gmsh.initialize()
    try:
        gmsh.option.restoreDefaults()                           # options survive finalize(): start clean
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)          # no OpenMP: avoids runtime clashes (MKL, numba)
        gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
        gmsh.model.occ.importShapes(os.fspath(path))
        gmsh.model.occ.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMax", size_mm)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", curvature)
        gmsh.option.setNumber("Mesh.ElementOrder", 2)
        gmsh.option.setNumber("Mesh.SecondOrderLinear", 0)
        gmsh.model.mesh.generate(3)
        m = _from_gmsh(gmsh)
    finally:
        gmsh.finalize()
    m.info = {"size_mm": size_mm, "elements": len(m.T), "nodes": len(m.X), "mesh_s": time.perf_counter() - t0}
    return m


def mesh_stl(path: str | Path, size_mm: float, angle_deg: float = 40.0) -> TetMesh:
    """10-node tet mesh of the volume inside a closed STL in mm (gmsh classifySurfaces -> createGeometry ->
    volume); used for the smoothed optimised layouts."""
    import math

    import gmsh
    t0 = time.perf_counter()
    last: Exception | None = None
    for mode in ("reparametrize", "discrete"):
        gmsh.initialize()
        try:
            gmsh.option.restoreDefaults()                           # options survive finalize(): start clean
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.option.setNumber("General.NumThreads", 1)          # no OpenMP: avoids runtime clashes (MKL, numba)
            gmsh.merge(os.fspath(path))
            if mode == "reparametrize":        # remesh the surface at size_mm (smoother, may fail on thin members)
                gmsh.model.mesh.classifySurfaces(angle_deg * math.pi / 180, True, True, math.pi)
                gmsh.model.mesh.createGeometry()
            surf = gmsh.model.getEntities(2)
            loop = gmsh.model.geo.addSurfaceLoop([e[1] for e in surf])
            gmsh.model.geo.addVolume([loop])
            gmsh.model.geo.synchronize()
            gmsh.option.setNumber("Mesh.MeshSizeMax", size_mm)
            if mode == "discrete":             # keep the STL triangles as the boundary, tets inside
                gmsh.model.mesh.generate(3)
                gmsh.model.mesh.setOrder(2)
            else:
                gmsh.option.setNumber("Mesh.ElementOrder", 2)
                gmsh.model.mesh.generate(3)
            m = _from_gmsh(gmsh)
            m.info = {"size_mm": size_mm, "elements": len(m.T), "nodes": len(m.X),
                      "mesh_s": time.perf_counter() - t0, "source": f"stl ({mode})"}
            return m
        except Exception as exc:               # noqa: BLE001 - try the next mode
            last = exc
        finally:
            gmsh.finalize()
    raise RuntimeError(f"gmsh could not mesh {path}: {last}")


def mesh_drawing(drawing: Any, size_mm: float, workdir: str | Path, curvature: int = 12) -> TetMesh:
    """Mesh a parametric drawing through its exact STEP (written by :func:`cadout.drawing_to_cad`)."""
    from aerokit.bracket.cadout import drawing_to_cad
    step = Path(workdir) / "_tetcheck.step"
    drawing_to_cad(drawing, step)
    return mesh_cad(step, size_mm, curvature)


@cite("zienkiewicz_taylor_2013", "cook_2002", note="10-node tetrahedron, 4-point rule")
def _stiffness(m: TetMesh, E: float, nu: float) -> tuple[sp.csr_matrix, np.ndarray]:
    D = E * voxfem.D_iso(nu)
    ne = len(m.T)
    edof = (3 * m.T[:, :, None] + np.arange(3)).reshape(ne, 30)
    rows, cols, vals = [], [], []
    for s in range(0, ne, 20000):
        Xe = m.X[m.T[s:s + 20000]]                                     # (n, 10, 3)
        Ke = np.zeros((len(Xe), 30, 30))
        for g in range(4):
            J = np.einsum("nk,enl->ekl", _DN_GP[g], Xe)               # (n, 3, 3) dX/dξ (rows ξ)
            Ji = np.linalg.inv(J)
            dNx = np.einsum("ekl,nl->enk", Ji, _DN_GP[g])              # (n, 10, 3)
            B = np.zeros((len(Xe), 6, 30))
            B[:, 0, 0::3] = dNx[:, :, 0]
            B[:, 1, 1::3] = dNx[:, :, 1]
            B[:, 2, 2::3] = dNx[:, :, 2]
            B[:, 3, 1::3] = dNx[:, :, 2]
            B[:, 3, 2::3] = dNx[:, :, 1]
            B[:, 4, 0::3] = dNx[:, :, 2]
            B[:, 4, 2::3] = dNx[:, :, 0]
            B[:, 5, 0::3] = dNx[:, :, 1]
            B[:, 5, 1::3] = dNx[:, :, 0]
            w = _GW[g] * np.linalg.det(J)
            Ke += np.einsum("e,eia,ij,ejb->eab", w, B, D, B)
        ed = edof[s:s + 20000]
        rows.append(np.repeat(ed, 30, axis=1).ravel())
        cols.append(np.tile(ed, (1, 30)).ravel())
        vals.append(Ke.ravel())
    K = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(m.ndof, m.ndof))
    return K, edof


def _face_weights(m: TetMesh) -> np.ndarray:
    """Consistent nodal areas of the boundary (uniform traction on 6-node triangles: corners 0, midsides A/3)."""
    P = m.X[m.faces]
    A = 0.5 * np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1)
    a = np.zeros(len(m.X))
    np.add.at(a, m.faces[:, 3:].ravel(), np.repeat(A / 3.0, 3))
    return a


def _bore(m: TetMesh, hl: Hole, tol: float) -> np.ndarray:
    surf = np.unique(m.faces)
    d = m.X[surf] - hl.center
    rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
    za = m.X[surf, hl.axis]
    ins = np.zeros(len(surf), bool)
    for a, b in hl.segments:
        ins |= (za >= a - tol) & (za <= b + tol)
    return surf[ins & (np.abs(rad - hl.radius) <= tol + 1e-3 * hl.radius)]


def static_t10(m: TetMesh, setup: dict[str, Any], E: float, nu: float = 0.3,
               margin_m: float | None = None, bore_tol_m: float | None = None) -> dict[str, Any]:
    """All load cases of ``setup`` on the T10 mesh; returns per-case results like the voxel ``evaluate``.

    ``bore_tol_m``: radial tolerance for bore nodes (default 2 % of the smallest radius - exact CAD); for a
    smoothed voxel STL pass about 0.6 voxel."""
    t0 = time.perf_counter()
    holes = {d["id"]: Hole.from_json(d) for d in setup["holes"]}
    roles = {d["id"]: d.get("role", "free") for d in setup["holes"]}
    tol = bore_tol_m if bore_tol_m is not None else 0.02 * min(h.radius for h in holes.values())
    a = _face_weights(m)
    fixed = []
    for s in setup["supports"]:
        if s.get("type", "fixed_bore") != "fixed_bore":
            raise ValueError("T10 check supports fixed_bore only")
        nn = _bore(m, holes[s["hole"]], tol)
        if not len(nn):
            raise ValueError(f"no T10 nodes on bore {s['hole']}")
        fixed.append((3 * nn[:, None] + np.arange(3)).ravel())
    fixed_d = np.unique(np.concatenate(fixed))
    cases = setup["load_cases"]
    F = np.zeros((m.ndof, len(cases)))
    for c, case in enumerate(cases):
        for ld in case["loads"]:
            hl = holes[ld["hole"]]
            nn = _bore(m, hl, tol)
            w = a[nn]
            ax = np.eye(3)[hl.axis]
            d = m.X[nn] - hl.center
            d -= np.outer(d @ ax, ax)
            if "force_N" in ld:
                f = np.asarray(ld["force_N"], float)
                fa = (f @ ax) * ax
                fr = f - fa
                if ld.get("type", "bearing") == "bearing" and np.linalg.norm(fr) > 0:
                    nrm = np.linalg.norm(d, axis=1)
                    wb = w * np.maximum(0.0, (d / nrm[:, None]) @ (fr / np.linalg.norm(fr)))
                    contrib = np.outer(wb / wb.sum(), fr) + np.outer(w / w.sum(), fa)
                else:
                    contrib = np.outer(w / w.sum(), f)
            else:
                M = np.asarray(ld["moment_Nm"], float)
                mh = M / np.linalg.norm(M)
                r = m.X[nn] - (w[:, None] * m.X[nn]).sum(0) / w.sum()   # weighted centroid: zero net force
                rp = r - np.outer(r @ mh, mh)
                contrib = w[:, None] * np.cross(M, rp) / np.sum(w * np.sum(rp * rp, axis=1))
            for k in range(3):
                np.add.at(F[:, c], 3 * nn + k, contrib[:, k])
    F[fixed_d] = 0.0
    K, edof = _stiffness(m, E, nu)
    t1 = time.perf_counter()
    U, info = voxfem.solve(K, F, fixed_d, m.X, method="auto", direct_limit=10**7)
    # nodal stress: element stress evaluated at its 10 nodes, averaged
    D = E * voxfem.D_iso(nu)
    sn = np.zeros((len(cases), len(m.X), 6))
    cnt = np.bincount(m.T.ravel(), minlength=len(m.X)).astype(float)
    for s in range(0, len(m.T), 20000):
        T = m.T[s:s + 20000]
        Xe = m.X[T]
        for k in range(10):
            J = np.einsum("nk,enl->ekl", _DN_NODES[k], Xe)
            dNx = np.einsum("ekl,nl->enk", np.linalg.inv(J), _DN_NODES[k])
            for c in range(len(cases)):
                ue = U[:, c][edof[s:s + 20000]].reshape(-1, 10, 3)
                grad = np.einsum("eni,enj->eij", ue, dNx)                 # du_i/dx_j
                eps = np.stack([grad[:, 0, 0], grad[:, 1, 1], grad[:, 2, 2], grad[:, 1, 2] + grad[:, 2, 1],
                                grad[:, 0, 2] + grad[:, 2, 0], grad[:, 0, 1] + grad[:, 1, 0]], axis=1)
                np.add.at(sn[c], T[:, k], eps @ D.T)
    sn /= cnt[None, :, None]
    zone = np.zeros(len(m.X), bool)
    margin = margin_m if margin_m is not None else setup.get("exclusion_mm", 0.0) * 1e-3
    for hid, hl in holes.items():
        if roles.get(hid) not in ("support", "load"):
            continue
        d = m.X - hl.center
        rad = np.linalg.norm(np.delete(d, hl.axis, axis=1), axis=1)
        za = m.X[:, hl.axis]
        ins = np.zeros(len(m.X), bool)
        for lo, hi in hl.segments:
            ins |= (za >= lo - margin) & (za <= hi + margin)
        zone |= ins & (rad <= hl.radius + margin)
    out = []
    for c, case in enumerate(cases):
        vm = voxfem.von_mises(sn[c])
        u = U[:, c].reshape(-1, 3)
        disp = np.linalg.norm(u, axis=1)
        vo = np.where(zone, 0.0, vm)
        j = int(np.argmax(vo))
        ln = np.unique(np.concatenate([_bore(m, holes[ld["hole"]], tol) for ld in case["loads"]]))
        wl = a[ln] if a[ln].sum() > 0 else np.ones(len(ln))
        load_disp = float(np.linalg.norm((u[ln] * wl[:, None]).sum(0) / wl.sum())) if len(ln) else float("nan")
        out.append({"name": case["name"], "compliance_J": float(F[:, c] @ U[:, c]), "max_disp_m": float(disp.max()),
                    "load_disp_m": load_disp,
                    "vm_outside_Pa": float(vo[j]), "vm_outside_at_m": m.X[j].tolist(), "vm_max_Pa": float(vm.max()),
                    "vm_max_at_m": m.X[int(np.argmax(vm))].tolist()})
    surf = np.unique(m.faces)
    vm_all = np.max([voxfem.von_mises(sn[c]) for c in range(len(cases))], axis=0)
    return {"_surface": (m.X[surf], vm_all[surf]),
            "cases": out, "elements": len(m.T), "nodes": len(m.X), "dofs": m.ndof, "volume_m3": m.volume,
            "solver": info.method, "solve_s": info.seconds, "assemble_s": t1 - t0,
            "total_s": time.perf_counter() - t0, "mesh": m.info}


def evaluate_setup(drawing_or_step: Any, setup: dict[str, Any], E: float, sizes_mm: tuple[float, ...],
                   workdir: str | Path, nu: float = 0.3) -> list[dict[str, Any]]:
    """T10 results at several mesh sizes (convergence of the conforming model)."""
    rows = []
    for s in sizes_mm:
        m = mesh_cad(drawing_or_step, s) if isinstance(drawing_or_step, (str, Path)) else \
            mesh_drawing(drawing_or_step, s, workdir)
        r = static_t10(m, setup, E, nu)
        r["size_mm"] = s
        rows.append(r)
    return rows


def worst(r: dict[str, Any]) -> dict[str, float]:
    c = r["cases"]
    return {"max_disp_m": max(x["max_disp_m"] for x in c), "compliance_J": max(x["compliance_J"] for x in c),
            "load_disp_m": max(x.get("load_disp_m", float("nan")) for x in c),
            "vm_outside_Pa": max(x["vm_outside_Pa"] for x in c), "vm_max_Pa": max(x["vm_max_Pa"] for x in c)}

