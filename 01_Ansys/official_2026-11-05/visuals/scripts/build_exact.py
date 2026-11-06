"""Rebuild the official initial bracket as an exact OCC solid (gmsh) and check its volume.

Writes visuals/initial_exact.step, visuals/initial_exact.stl (fine display mesh, mm) and
visuals/scripts/out/volume_check.json. Reference volume: derived/initial_from_facets.stl.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import geom as G  # noqa: E402


def stl_volume(path) -> tuple[float, int, list]:
    """Signed-tetra volume [mm^3] of an STL (ascii or binary) via pyvista/VTK reader."""
    import pyvista as pv
    m = pv.read(str(path)).triangulate()
    f = m.faces.reshape(-1, 4)[:, 1:]
    p = m.points
    v = np.einsum("ij,ij->i", p[f[:, 0]], np.cross(p[f[:, 1]], p[f[:, 2]])).sum() / 6.0
    return float(abs(v)), int(m.n_cells), [list(map(float, m.bounds[0::2])), list(map(float, m.bounds[1::2]))]


def lug_surface(occ, y0: float) -> int:
    """Plane surface of the lug profile in the x-z plane at y = y0 (base pushed 40 mm into the plate)."""
    zb = G.Z1 - 40.0
    R, L = G.FLANK_R, G.FLANK_L
    P = lambda x, z: occ.addPoint(x, y0, z)  # noqa: E731
    p_r0 = P(G.FIL_R[0], G.Z1)               # fillet/plate tangent (right)
    c_fr = P(*G.FIL_R)
    t_fr = P(*R["t_fil"])
    t_ar = P(*R["t_arc"])
    c_a = P(*G.ARC_C)
    t_al = P(*L["t_arc"])
    t_fl = P(*L["t_fil"])
    c_fl = P(*G.FIL_L)
    p_l0 = P(G.FIL_L[0], G.Z1)
    p_lb = P(G.FIL_L[0], zb)
    p_rb = P(G.FIL_R[0], zb)
    cur = [
        occ.addCircleArc(p_r0, c_fr, t_fr),
        occ.addLine(t_fr, t_ar),
        occ.addCircleArc(t_ar, c_a, t_al),
        occ.addLine(t_al, t_fl),
        occ.addCircleArc(t_fl, c_fl, p_l0),
        occ.addLine(p_l0, p_lb),
        occ.addLine(p_lb, p_rb),
        occ.addLine(p_rb, p_r0),
    ]
    return occ.addPlaneSurface([occ.addCurveLoop(cur)])


def _xz(p, y0):
    return (p[0], y0, p[1])


def main() -> dict:
    import gmsh
    out_dir = G.HERE / "out"
    out_dir.mkdir(exist_ok=True)
    step, stl = G.VIS / "initial_exact.step", G.VIS / "initial_exact.stl"
    gmsh.initialize()
    try:
        gmsh.option.restoreDefaults()
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.option.setNumber("General.NumThreads", 1)
        gmsh.model.add("initial_exact")
        occ = gmsh.model.occ
        plate_s = occ.addRectangle(G.X0, G.Y0, G.Z0, G.X1 - G.X0, G.Y1 - G.Y0, roundedRadius=G.R_CORNER)
        plate = [t for d, t in occ.extrude([(2, plate_s)], 0, 0, G.Z1 - G.Z0) if d == 3][0]
        body = [(3, plate)]
        for ya, yb in G.LUGS:
            s = lug_surface(occ, ya)
            lug = [t for d, t in occ.extrude([(2, s)], 0, yb - ya, 0) if d == 3][0]
            body, _ = occ.fuse(body, [(3, lug)])
        tools = [(3, occ.addCylinder(G.PIN[0], G.Y0 - 50, G.PIN[1], 0, (G.Y1 - G.Y0) + 100, 0, G.R_BORE))]
        for x, y in G.BOLTS:
            tools.append((3, occ.addCylinder(x, y, G.Z0 - 50, 0, 0, (G.Z1 - G.Z0) + 100, G.R_BORE)))
        body, _ = occ.cut(body, tools)
        occ.removeAllDuplicates()
        occ.synchronize()
        vols = gmsh.model.getEntities(3)
        vol = sum(occ.getMass(3, t) for _, t in vols)
        bb = gmsh.model.getBoundingBox(-1, -1)
        n_faces = len(gmsh.model.getEntities(2))
        gmsh.write(os.fspath(step))
        gmsh.option.setNumber("Mesh.MeshSizeMax", 6.0)
        gmsh.option.setNumber("Mesh.MeshSizeMin", 0.5)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 90)   # elements per 2*pi
        gmsh.option.setNumber("Mesh.Algorithm", 6)
        gmsh.option.setNumber("Mesh.Binary", 1)                  # binary STL (6 MB instead of 32 MB)
        gmsh.model.mesh.generate(2)
        gmsh.write(os.fspath(stl))
        # B-rep edge curves as line segments (for crisp edge lines in the renders)
        segs = []
        for _, ctag in gmsh.model.getEntities(1):
            up, _ = gmsh.model.getAdjacencies(1, ctag)
            if len(set(up)) < 2:                                   # periodic seam of a cylinder: not a real edge
                continue
            _, etags, enodes = gmsh.model.mesh.getElements(1, ctag)
            if not len(etags):
                continue
            nodes = np.asarray(enodes[0], dtype=np.int64).reshape(-1, 2)
            for a, b in nodes:
                pa = gmsh.model.mesh.getNode(int(a))[0]
                pb = gmsh.model.mesh.getNode(int(b))[0]
                segs.append((pa, pb, ctag))
        np.savez(out_dir / "brep_edges.npz",
                 a=np.array([s[0] for s in segs]), b=np.array([s[1] for s in segs]),
                 curve=np.array([s[2] for s in segs]))
    finally:
        gmsh.finalize()

    v_ref_facets, ntri_ref, bb_ref = stl_volume(G.FACET_STL)
    v_stl, ntri, bb_stl = stl_volume(stl)
    ref = G.VOLUME_REF_M3 * 1e9
    res = {
        "exact_brep_volume_mm3": vol,
        "exact_brep_volume_m3": vol * 1e-9,
        "exact_mass_kg_at_7850": vol * 1e-9 * G.RHO,
        "reference_m3_boundary_conditions_md": G.VOLUME_REF_M3,
        "facet_stl_volume_mm3_recomputed": v_ref_facets,
        "facet_stl_triangles": ntri_ref,
        "diff_vs_0.019400_pct": 100 * (vol - ref) / ref,
        "diff_vs_facet_stl_recomputed_pct": 100 * (vol - v_ref_facets) / v_ref_facets,
        "display_stl_volume_mm3": v_stl,
        "display_stl_triangles": ntri,
        "display_stl_vs_brep_pct": 100 * (v_stl - vol) / vol,
        "bbox_brep_mm": [bb[:3], bb[3:]],
        "bbox_facet_stl_mm": bb_ref,
        "n_brep_faces": n_faces,
        "flank_angle_deg_right": G.FLANK_R["angle_deg"],
        "flank_angle_deg_left": G.FLANK_L["angle_deg"],
        "flank_normal_right": G.FLANK_R["n"],
        "flank_offset_right_mm": G.FLANK_R["c"],
        "flank_normal_left": G.FLANK_L["n"],
        "flank_offset_left_mm": G.FLANK_L["c"],
        "accept_le_0.5pct": abs(100 * (vol - ref) / ref) <= 0.5,
        "step": str(step), "stl": str(stl),
    }
    (out_dir / "volume_check.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        print(f"{k}: {v}")
    if not res["accept_le_0.5pct"]:
        raise SystemExit("volume check FAILED (> 0.5 %)")
    return res


if __name__ == "__main__":
    main()
