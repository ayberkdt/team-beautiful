"""CAD output: exact B-rep of a parametric drawing (STEP + STL through gmsh/OpenCASCADE) and smooth STL of a
density field (surface nets + Taubin smoothing from :mod:`aerokit.optimization.extract`).

gmsh is an optional dependency (installed for this project in ``D:\\tmp_ideathon\\pylib``, see docs/22); without it
:func:`drawing_to_cad` raises and the pipeline falls back to the voxel surface.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np

from aerokit.bracket.geometry import Drawing, VoxelModel, _AX, _PLANE
from aerokit.optimization import extract

__all__ = ["gmsh_available", "drawing_to_cad", "density_to_stl", "read_any"]


def gmsh_available() -> bool:
    try:
        import gmsh  # noqa: F401
    except Exception:
        return False
    return True


def _solid(occ: Any, s: dict[str, Any], k: float) -> int:
    t = s["type"]
    if t == "box":
        lo, hi = np.asarray(s["min"]) * k, np.asarray(s["max"]) * k
        return occ.addBox(*lo, *(hi - lo))
    if t == "cylinder":
        p0, p1 = np.asarray(s["p0"]) * k, np.asarray(s["p1"]) * k
        return occ.addCylinder(*p0, *(p1 - p0), s["radius"] * k)
    if t == "sphere":
        return occ.addSphere(*(np.asarray(s["center"]) * k), s["radius"] * k)
    if t == "prism":
        ax = _AX[s["axis"]]
        i, j = _PLANE[ax]
        lo, hi = s["range"][0] * k, s["range"][1] * k
        poly = np.asarray(s["polygon"], float) * k
        if np.allclose(poly[0], poly[-1]):
            poly = poly[:-1]
        # drop consecutive duplicates
        keep = [0] + [n for n in range(1, len(poly)) if np.linalg.norm(poly[n] - poly[n - 1]) > 1e-9]
        poly = poly[keep]
        pts = []
        for a, b in poly:
            p = np.zeros(3)
            p[i], p[j], p[ax] = a, b, lo
            pts.append(occ.addPoint(*p))
        lines = [occ.addLine(pts[n], pts[(n + 1) % len(pts)]) for n in range(len(pts))]
        loop = occ.addCurveLoop(lines)
        surf = occ.addPlaneSurface([loop])
        d = np.zeros(3)
        d[ax] = hi - lo
        out = occ.extrude([(2, surf)], *d)
        return next(tag for dim, tag in out if dim == 3)
    raise ValueError(f"unknown solid type {t!r}")


def drawing_to_cad(d: Drawing, step_path: str | Path, stl_path: str | Path | None = None,
                   mesh_size_mm: float | None = None) -> dict[str, Any]:
    """Build the drawing in OpenCASCADE (lengths written in mm), write STEP and optionally a surface STL.

    Returns ``{"volume_mm3", "step", "stl", "bbox_mm"}``; the volume is the exact B-rep volume.
    """
    import gmsh
    k = 1e3                                         # drawing is in metres → CAD in mm
    gmsh.initialize()
    try:
        gmsh.option.restoreDefaults()                           # options survive finalize(): start clean
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)          # no OpenMP: avoids runtime clashes (MKL, numba)
        gmsh.model.add("bracket")
        occ = gmsh.model.occ
        body: list[tuple[int, int]] = []
        for s in d.solids:
            tag = _solid(occ, s, k)
            if s.get("op", "add") == "add":
                if body:
                    body, _ = occ.fuse(body, [(3, tag)])
                else:
                    body = [(3, tag)]
            else:
                body, _ = occ.cut(body, [(3, tag)])
        occ.synchronize()
        vol = sum(occ.getMass(3, t) for _, t in body)
        bb = gmsh.model.getBoundingBox(-1, -1)
        gmsh.write(os.fspath(step_path))
        out: dict[str, Any] = {"volume_mm3": vol, "step": str(step_path), "bbox_mm": [bb[:3], bb[3:]]}
        if stl_path:
            size = mesh_size_mm or max(bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]) / 60
            gmsh.option.setNumber("Mesh.MeshSizeMax", size)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 24)
            gmsh.model.mesh.generate(2)
            gmsh.write(os.fspath(stl_path))
            out["stl"] = str(stl_path)
        return out
    finally:
        gmsh.finalize()


def cad_volume(path: str | Path) -> float:
    """Volume [mm³] of the solids in a STEP/IGES file (gmsh OCC import in mm)."""
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.restoreDefaults()                           # options survive finalize(): start clean
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)          # no OpenMP: avoids runtime clashes (MKL, numba)
        gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
        ents = gmsh.model.occ.importShapes(os.fspath(path))
        gmsh.model.occ.synchronize()
        return float(sum(gmsh.model.occ.getMass(d, t) for d, t in ents if d == 3))
    finally:
        gmsh.finalize()


def density_to_stl(vm_origin: np.ndarray, h: float, field: np.ndarray, path: str | Path, level: float = 0.5,
                   smooth: int = 8, target_volume_mm3: float | None = None) -> dict[str, Any]:
    """Smooth closed STL (mm) of ``field`` (nx, ny, nz) of element values on the voxel grid.

    With pyvista/VTK: element values → point values (average of the cells around a node), flying-edges contour,
    Taubin smoothing (pass band 0.1), binary STL. A fixed level 0.5 on the point-averaged field thins or cuts
    members one or two voxels thick (seen 4 Nov: a 25 % layout kept 62 % of its volume in 3 bodies), so when
    ``target_volume_mm3`` is given the level is found by bisection to match it (±1 %). Without VTK: surface nets.
    """
    try:
        import pyvista as pv
        g = np.pad(np.asarray(field, float), 1)
        o = np.asarray(vm_origin) * 1e3 - h * 1e3
        im = pv.ImageData(dimensions=np.array(g.shape) + 1, spacing=(h * 1e3,) * 3, origin=tuple(o))
        im.cell_data["rho"] = g.ravel(order="F")
        pts = im.cell_data_to_point_data()

        def surface(lv: float) -> Any:
            srf = pts.contour([lv], scalars="rho").triangulate().clean()
            if smooth and srf.n_points:
                srf = srf.smooth_taubin(n_iter=4 * smooth, pass_band=0.1)
            return srf

        def vol(srf: Any) -> float:
            Fs = srf.faces.reshape(-1, 4)[:, 1:]
            return abs(extract.mesh_volume(np.asarray(srf.points), Fs)) if len(Fs) else 0.0

        surf = surface(level)
        used = level
        if target_volume_mm3:
            lo, hi = 0.02, 0.6
            for _ in range(14):
                v = vol(surf)
                if abs(v / target_volume_mm3 - 1) < 0.01:
                    break
                if v < target_volume_mm3:
                    hi = used
                else:
                    lo = used
                used = 0.5 * (lo + hi)
                surf = surface(used)
        if surf.n_points:                                  # drop fragments < 2 % of the volume (smoothing artefacts)
            parts = surf.split_bodies()
            vols = [vol(b.extract_surface().triangulate()) for b in parts]
            keep = [b.extract_surface().triangulate() for b, v in zip(parts, vols, strict=True) if v >= 0.02 * sum(vols)]
            if keep and len(keep) < len(parts):
                surf = keep[0].merge(keep[1:]) if len(keep) > 1 else keep[0]
                surf = surf.extract_surface().triangulate().clean()
        surf.save(str(path), binary=True)
        F = surf.faces.reshape(-1, 4)[:, 1:]
        n_bodies = int(surf.connectivity().point_data["RegionId"].max() + 1) if surf.n_points else 0
        return {"stl": str(path), "triangles": int(surf.n_cells), "volume_mm3": vol(surf), "level": used,
                "target_volume_mm3": target_volume_mm3, "bodies": n_bodies,
                "watertight": bool(extract.watertight(F)), "method": "vtk flying edges + Taubin"}
    except ImportError:
        pass
    f = np.pad(np.asarray(field, float), 1)
    V, F = extract.surface_nets(f, level=level, h=h * 1e3)
    if smooth:
        V = extract.laplacian_smooth(V, F, iterations=smooth)
    V = V + (np.asarray(vm_origin) * 1e3 - h * 1e3)          # undo the padding, metres → mm
    extract.write_stl(path, V, F, name="aerokit bracket")
    return {"stl": str(path), "triangles": int(len(F)), "volume_mm3": float(extract.mesh_volume(V, F)),
            "watertight": bool(extract.watertight(F))}


def read_step_surface(path: str | Path, size_mm: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Closed triangle surface (vertices [m], faces) of a STEP/IGES file: gmsh/OCC import in **mm**, 2-D mesh.

    Used instead of :func:`aerokit.cad.readers.read` for CAD files: that reader switches OpenCASCADE to metres,
    and on 2026-11-04 a later gmsh 3-D mesh in the same process then hung (reproduced: STEP read → T10 mesh).
    """
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.restoreDefaults()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)
        gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
        gmsh.model.occ.importShapes(os.fspath(path))
        gmsh.model.occ.synchronize()
        bb = gmsh.model.getBoundingBox(-1, -1)
        gmsh.option.setNumber("Mesh.MeshSizeMax", size_mm or max(bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]) / 60)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 24)
        gmsh.model.mesh.generate(2)
        tags, coord, _ = gmsh.model.mesh.getNodes()
        V = np.asarray(coord, float).reshape(-1, 3) * 1e-3
        lut = np.zeros(int(tags.max()) + 1, dtype=np.int64)
        lut[tags.astype(np.int64)] = np.arange(len(tags))
        ty, _, en = gmsh.model.mesh.getElements(2)
        F = lut[np.asarray(en[list(ty).index(2)], np.int64)].reshape(-1, 3)
    finally:
        gmsh.finalize()
    from aerokit.cad.surface import Surface
    surf = Surface(V, F)
    surf, _ = surf.clean()
    surf, _ = surf.fix_orientation()
    return np.asarray(surf.V, float), np.asarray(surf.F, int)


def _gmsh_start() -> Any:
    import gmsh
    gmsh.initialize()
    gmsh.option.restoreDefaults()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setNumber("General.NumThreads", 1)
    gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
    return gmsh


def step_bodies(path: str | Path) -> list[dict[str, Any]]:
    """Solids in a STEP/IGES file: index (1-based, file order), volume [mm³], bounding box [mm]."""
    gmsh = _gmsh_start()
    try:
        ents = gmsh.model.occ.importShapes(os.fspath(path))
        gmsh.model.occ.synchronize()
        out = []
        for i, (_, t) in enumerate([e for e in ents if e[0] == 3], 1):
            bb = gmsh.model.occ.getBoundingBox(3, t)
            out.append({"index": i, "volume_mm3": float(gmsh.model.occ.getMass(3, t)),
                        "bbox_mm": [list(bb[:3]), list(bb[3:])]})
        return out
    finally:
        gmsh.finalize()


def normalise_step(path: str | Path, dst: str | Path, bodies: str | list[int] = "all") -> dict[str, Any]:
    """One-solid STEP (mm) from a multi-body file or assembly: select ``bodies`` ("all", "largest" or 1-based
    indices from :func:`step_bodies`), fuse them (boolean union: overlaps such as inserted bolts are counted
    once) and write ``dst``. Returns the body table, the selection, the fused volume and the overlap removed."""
    table = step_bodies(path)
    if not table:
        raise ValueError(f"{path}: no solids found (surface-only STEP?)")
    if bodies == "all":
        sel = [b["index"] for b in table]
    elif bodies == "largest":
        sel = [max(table, key=lambda b: b["volume_mm3"])["index"]]
    else:
        sel = sorted({int(i) for i in bodies})
        bad = [i for i in sel if not 1 <= i <= len(table)]
        if bad:
            raise ValueError(f"bodies {bad} not in the file (it has {len(table)} solids: 1 … {len(table)})")
    gmsh = _gmsh_start()
    try:
        ents = gmsh.model.occ.importShapes(os.fspath(path))
        vols = [e for e in ents if e[0] == 3]
        keep = [vols[i - 1] for i in sel]
        drop = [v for v in vols if v not in keep]
        if drop:
            gmsh.model.occ.remove(drop, recursive=True)
        if len(keep) > 1:
            keep, _ = gmsh.model.occ.fuse(keep[:1], keep[1:])
        gmsh.model.occ.synchronize()
        fused = float(sum(gmsh.model.occ.getMass(d, t) for d, t in gmsh.model.getEntities(3)))
        n_after = len(gmsh.model.getEntities(3))
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        gmsh.write(os.fspath(dst))
    finally:
        gmsh.finalize()
    total = sum(table[i - 1]["volume_mm3"] for i in sel)
    return {"bodies": table, "selected": sel, "fused_volume_mm3": fused, "overlap_mm3": total - fused,
            "solids_after_fuse": n_after, "file": str(dst)}


def read_any(path: str | Path, unit: str = "mm") -> tuple[np.ndarray, np.ndarray]:
    """Triangle surface (vertices [m], faces) of STL/OBJ/PLY (via :func:`aerokit.cad.read`) or STEP/IGES
    (via :func:`read_step_surface`)."""
    if Path(path).suffix.lower() in (".step", ".stp", ".iges", ".igs"):
        return read_step_surface(path)
    from aerokit.cad import read
    s = read(path, unit=unit)
    return np.asarray(s.V, float), np.asarray(s.F, int)


def voxel_surface_stl(vm: VoxelModel, path: str | Path) -> dict[str, Any]:
    """Smoothed surface of a voxel model (when no exact CAD is available)."""
    return density_to_stl(vm.origin, vm.h, vm.solid.astype(float), path)
