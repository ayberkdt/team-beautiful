"""Finalize a density-based topology result into a manufacturing-ready solid (signed-distance-field pipeline).

Stages (each a standard operation; sources in 01_Ansys/official_2026-11-05/setup/literature_finalize.md):

1. **Fine grid**: the original part (design envelope) is voxelised at ``h`` (default 2 mm) with partial volumes.
2. **Density → shape**: the element densities of the optimiser are interpolated trilinearly onto the fine grid,
   smoothed with a Gaussian (σ ≈ half the optimiser's filter radius) and thresholded at the level that reproduces
   the optimised volume (volume-preserving threshold, bisection).
3. **Signed distance field** (φ < 0 inside) from exact Euclidean distance transforms of both phases.
4. **Morphological opening** by r_open (erode then dilate the SDF): rounds convex edges to ≥ r_open and deletes
   flaps and spikes thinner than 2 r_open (Rossignac & Requicha 1986 offset rounding).
5. **Functional geometry re-inserted exactly** (CSG union, φ = min): bolt bosses, lug eyes and base flange from the
   set-up's non-design definition, intersected with the original envelope.
6. **Morphological closing** by r_close (dilate then erode): fillets every concave corner, the TO-member-to-flange
   and member-to-lug junctions included, with radius ≥ r_close (stress-concentration relief).
7. **Envelope and bores**: intersection with the original part (planar mating face, lug side faces, outline kept)
   and exact cylindrical bores subtracted (functional holes at their nominal size and position).
8. **Clean-up**: islands removed (largest body kept), enclosed voids filled (trapped powder cannot be removed).
9. **Surface**: flying-edges iso-surface of φ = 0, Taubin λ|μ smoothing (non-shrinking), decimation for FEA.
10. **Checks**: bodies, enclosed voids, watertight/manifold, minimum wall (2 × the medial-axis distance), overhang
    area beyond 45° for the build direction, volume change, bore radius after smoothing.

The result MUST be re-analysed (smoothing and filleting change stiffness and stress): see
``analysis/finalize_v2.py`` which runs the T10 check on the finalized STL.
"""
from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

__all__ = ["FinalizeParams", "finalize"]


@dataclass
class FinalizeParams:
    h_mm: float = 2.0               # fine grid
    sigma_mm: float = 4.0           # Gaussian smoothing of the interpolated density
    r_open_mm: float = 6.0          # START value of the convex rounding radius (lit.: 6-8 mm); reduced until the
    max_open_loss: float = 0.02     # opening removes at most this fraction of the thresholded volume
    r_close_mm: float = 10.0        # concave fillet radius (lit.: >= 8 mm; Kt gain small beyond r/d 0.3)
    stock_mm: float = 1.5           # machining allowance of the PRINT geometry on bores + mounting face (0 = none)
    taubin_iter: int = 40
    taubin_pass_band: float = 0.05
    decimate_to_faces: int = 120_000
    build_axis: int = 2             # +z build, base on the plate
    overhang_deg: float = 45.0
    pad_mm: float = 16.0
    sdf_blur_vox: float = 1.0       # Gaussian σ (fine voxels) on the final SDF before re-imposing the interfaces
    snap_mm: float = 3.0            # body surfaces within this depth under an envelope face are snapped onto it


def _sdf(mask: np.ndarray, h: float) -> np.ndarray:
    """Signed distance [mm] at voxel centres, boundary half-way between centres (φ < 0 inside)."""
    if not mask.any():
        return np.full(mask.shape, 1e9, np.float32)
    d_out = ndimage.distance_transform_edt(~mask, sampling=h)
    d_in = ndimage.distance_transform_edt(mask, sampling=h)
    return np.where(mask, -(d_in - 0.5 * h), d_out - 0.5 * h).astype(np.float32)


def _dilate(phi: np.ndarray, r: float, h: float) -> np.ndarray:
    return _sdf(phi - r < 0, h)


def _erode(phi: np.ndarray, r: float, h: float) -> np.ndarray:
    return _sdf(phi + r < 0, h)


def opening(phi: np.ndarray, r: float, h: float) -> np.ndarray:
    return _dilate(_erode(phi, r, h), r, h)


def closing(phi: np.ndarray, r: float, h: float) -> np.ndarray:
    return _erode(_dilate(phi, r, h), r, h)


def _cyl(P: tuple[np.ndarray, ...], c: np.ndarray, axis: int, R: float, seg: tuple[float, float]) -> np.ndarray:
    """SDF-like field of a finite cylinder (exact inside the radial/axial slab, a bound outside)."""
    rad = np.sqrt(sum((P[k] - c[k]) ** 2 for k in range(3) if k != axis))
    a, b = seg
    return np.maximum(rad - R, np.maximum(a - P[axis], P[axis] - b)).astype(np.float32)


def finalize(st: Any, geom: Any, tag: int, out_stl: str | Path, prm: FinalizeParams | None = None,
             log: Any = print) -> dict[str, Any]:
    """Finalize layout ``optimised_<tag>`` of the study ``st`` (aerokit.bracket.pipeline.Study) on the original
    geometry ``geom`` (pipeline.Geometry). Writes ``out_stl`` (mm) and returns the checks."""
    import pyvista as pv
    from aerokit.bracket import features
    prm = prm or FinalizeParams()
    t0 = time.perf_counter()
    h = prm.h_mm
    vm = geom.voxelize(h * 1e-3)
    pad = int(math.ceil(prm.pad_mm / h))
    frac = vm.frac if vm.frac is not None else vm.solid.astype(float)
    dom = np.pad(frac >= 0.5, pad)
    o = vm.origin * 1e3 - pad * h                                   # corner of fine voxel (0,0,0) [mm]
    n = dom.shape
    ax = [o[k] + (np.arange(n[k]) + 0.5) * h for k in range(3)]
    P = np.meshgrid(*ax, indexing="ij", sparse=True)
    log(f"finalize: fine grid {n} at {h} mm ({dom.size / 1e6:.1f} M cells), envelope {dom.sum() * h ** 3 / 1e3:.0f} cm3")
    phi_D = _sdf(dom, h)
    # sub-voxel envelope: within one voxel of the surface use the partial-volume estimate (0.5 - frac)·h, so planar
    # faces, the R80 lug arcs and the 80° flanks are not staircased by the binary distance transform
    fr = np.pad(frac, pad).astype(np.float32)
    phi_D = np.where(np.abs(phi_D) < h, (0.5 - fr) * h, phi_D).astype(np.float32)
    # ---- exact functional geometry from the set-up
    setup = st.setup
    holes = features._holes(setup)
    role = {d["id"]: d.get("role", "free") for d in setup["holes"]}
    nd = setup.get("non_design", {})
    k_role = nd.get("ring_factor_by_role", {})
    phi_K = np.full(n, 1e9, np.float32)
    bores = np.full(n, 1e9, np.float32)
    for hid, hl in holes.items():
        if role.get(hid) not in ("support", "load"):
            continue
        c = hl.center * 1e3
        R = hl.radius * 1e3
        kf = k_role.get(role[hid], nd.get("ring_factor", 0.75))
        t = max(kf * R, nd.get("ring_min_voxels", 2) * st.mesh.h * 1e3)
        for a, b in hl.segments:
            phi_K = np.minimum(phi_K, _cyl(P, c, hl.axis, R + t, (a * 1e3, b * 1e3)))
            bores = np.minimum(bores, _cyl(P, c, hl.axis, R, (a * 1e3 - 2 * h, b * 1e3 + 2 * h)))
    for bx in nd.get("boxes_mm", []) + features.load_ties(setup, st.mesh.h):
        lo, hi = np.asarray(bx["min"], float), np.asarray(bx["max"], float)
        dk = [np.maximum(lo[k] - P[k], P[k] - hi[k]) for k in range(3)]
        dbox = np.maximum(np.maximum(dk[0], dk[1]), dk[2])
        phi_K = np.minimum(phi_K, dbox.astype(np.float32))
    for sg in features.support_ties(setup, st.mesh.h):            # automatic X bracing of the bolt pattern
        a_, b_ = np.asarray(sg["a"], float), np.asarray(sg["b"], float)
        ab = b_ - a_
        tt_ = sum((P[k] - a_[k]) * ab[k] for k in range(3)) / float(ab @ ab)
        tt_ = np.clip(tt_, 0.0, 1.0)
        dseg = np.sqrt(sum((P[k] - (a_[k] + tt_ * ab[k])) ** 2 for k in range(3))) - sg["r"]
        phi_K = np.minimum(phi_K, dseg.astype(np.float32))
        del tt_, dseg
    phi_K = np.maximum(phi_K, phi_D)                                # inside the original envelope only
    # ---- density → fine grid → volume-matched threshold
    H = st.mesh.h * 1e3
    rho = st.fields[f"xphys_{tag}"] * st.fields[f"solid_{tag}"]
    oc = st.mesh.origin * 1e3
    idx = [((ax[k] - oc[k]) / H - 0.5) for k in range(3)]
    I = np.meshgrid(*idx, indexing="ij")
    rf = ndimage.map_coordinates(rho.astype(np.float32), I, order=1, mode="nearest")
    del I
    # normalised convolution inside the envelope: blur(ρ·dom)/blur(dom). 5 Nov: a plain Gaussian over the zero
    # exterior pulled the density down at the envelope surface, so the face skins of the lugs (the members that
    # carry the out-of-plane Fy bending) fell below the threshold and the finalized lug became an open arch
    dm = dom.astype(np.float32)
    rf = ndimage.gaussian_filter(rf * dm, prm.sigma_mm / h) / np.maximum(ndimage.gaussian_filter(dm, prm.sigma_mm / h), 1e-6)
    rf *= dm
    d = next(x for x in st.designs if x["label"] != "initial" and round(100 * x["volfrac"]) == tag)
    target = d["volume_m3"] / st.vol_corr * 1e9                     # optimised (voxel) volume [mm3]
    keep_in = phi_K < 0
    lo_t, hi_t = 0.05, 0.95
    for _ in range(30):
        tt = 0.5 * (lo_t + hi_t)
        v = float(((rf > tt) & dom | keep_in).sum()) * h ** 3
        if v > target:
            lo_t = tt
        else:
            hi_t = tt
    A = (rf > tt) & dom
    log(f"finalize: threshold {tt:.3f} gives {v / 1e3:.0f} cm3 (target {target / 1e3:.0f} cm3)")
    stages = {"thresholded_cm3": v / 1e3}
    phi0 = _sdf(A, h)
    # opening rounds convex edges but DELETES every member thinner than 2 r. 5 Nov: a fixed r = 6 mm removed 34 %
    # of the 45 % layout (load-carrying members) and the stress rose to 542 MPa. The radius is now reduced until the
    # opening removes at most max_open_loss of the thresholded volume (edge rounding only, no member deleted).
    vA = float(A.sum())
    r_open = prm.r_open_mm
    while True:
        phi = opening(phi0, r_open, h) if r_open >= 0.5 * h else phi0
        loss = 1.0 - float((phi < 0).sum()) / vA
        if loss <= prm.max_open_loss or r_open < 0.5 * h:
            break
        r_open -= 1.0
    log(f"finalize: opening radius {r_open:.1f} mm removes {100 * loss:.2f} % of the thresholded volume")
    stages["opened_cm3"] = float((phi < 0).sum()) * h ** 3 / 1e3
    stages["r_open_used_mm"] = r_open
    stages["opening_loss_pct"] = 100 * loss
    phi = np.minimum(phi, phi_K)
    stages["with_interfaces_cm3"] = float((phi < 0).sum()) * h ** 3 / 1e3
    phi = closing(phi, prm.r_close_mm, h)
    stages["closed_cm3"] = float((phi < 0).sum()) * h ** 3 / 1e3
    # the binary re-distancing leaves h-sized steps on sloped faces: a one-voxel Gaussian of the SDF removes them
    # (moves a plane by < 0.1 h, rounds edges by ~h); the exact interfaces are then re-imposed on top
    phi = ndimage.gaussian_filter(phi, prm.sdf_blur_vox)
    # envelope snapping: a body surface that runs within snap_mm under an envelope face (lug side faces, mounting
    # face) would be cut into a rippled strip by the intersection; dilating the body smoothly by up to snap_mm next to
    # the envelope (weight 1 on the envelope surface -> 0 at depth snap_mm) makes those faces the flat original faces
    if prm.snap_mm > 0:
        w = np.clip(1.0 + phi_D / prm.snap_mm, 0.0, 1.0)
        phi = (phi - prm.snap_mm * w).astype(np.float32)
        del w
    phi = np.minimum(phi, phi_K)
    phi = np.maximum(phi, phi_D)
    phi = np.maximum(phi, -bores)
    stock_rings = np.full(n, 1e9, np.float32)
    if prm.stock_mm > 0:
        for hid, hl in holes.items():
            if role.get(hid) not in ("support", "load"):
                continue
            c, R = hl.center * 1e3, hl.radius * 1e3
            rad = np.sqrt(sum((P[k] - c[k]) ** 2 for k in range(3) if k != hl.axis))
            for a, b in hl.segments:
                ring = np.maximum(np.maximum(rad - R - 0.5, (R - prm.stock_mm) - rad),
                                  np.maximum(a * 1e3 - P[hl.axis], P[hl.axis] - b * 1e3))
                stock_rings = np.minimum(stock_rings, ring.astype(np.float32))
    solid = phi < 0
    lab, nb = ndimage.label(solid)
    if nb > 1:
        sizes = np.bincount(lab.ravel())[1:]
        solid = lab == (1 + int(np.argmax(sizes)))
    outside, no = ndimage.label(~solid)
    border = np.unique(np.concatenate([outside[0].ravel(), outside[-1].ravel(), outside[:, 0].ravel(),
                                       outside[:, -1].ravel(), outside[:, :, 0].ravel(), outside[:, :, -1].ravel()]))
    voids = ~solid & ~np.isin(outside, border)
    n_voids = int(len(set(np.unique(outside[voids])) - {0}))
    solid |= voids
    phi = np.where(solid, np.minimum(phi, -1e-3), np.maximum(phi, 1e-3)).astype(np.float32)
    stages["final_grid_cm3"] = float(solid.sum()) * h ** 3 / 1e3
    phi_print = None
    if prm.stock_mm > 0:
        # print geometry = nominal + stock: bores printed at R - stock, mounting face extended down by stock
        kb = int(np.argmax(dom.any(axis=(0, 1))))                    # first envelope layer (z = 30 mm)
        z0 = o[2] + kb * h
        foot = np.repeat(phi[:, :, kb + 1:kb + 2], n[2], axis=2)     # in-plane footprint of the final part
        slab = np.maximum(foot, np.maximum((z0 - prm.stock_mm) - P[2], P[2] - (z0 + h)))
        phi_print = np.minimum(np.minimum(phi, slab.astype(np.float32)), stock_rings)
    # ---- minimum wall: 2 × the inside distance on the medial ridge (local maxima of the inside EDT)
    din = ndimage.distance_transform_edt(solid, sampling=h)
    ridge = solid & (din >= ndimage.maximum_filter(din, size=3)) & (din > 0)
    wall = 2 * (din[ridge] - 0.5 * h)          # din is centre-to-centre: the face lies h/2 before the outside centre
    wall_min = float(wall.min()) if wall.size else float("nan")
    wall_p1 = float(np.percentile(wall, 1)) if wall.size else float("nan")
    wall_p5 = float(np.percentile(wall, 5)) if wall.size else float("nan")
    # ---- surface
    im = pv.ImageData(dimensions=n, spacing=(h, h, h), origin=tuple(o + 0.5 * h))
    im.point_data["phi"] = phi.ravel(order="F")
    srf = im.contour([0.0], scalars="phi").triangulate().clean()
    srf = srf.smooth_taubin(n_iter=prm.taubin_iter, pass_band=prm.taubin_pass_band)
    n_full = srf.n_cells
    if srf.n_cells > prm.decimate_to_faces:
        srf = srf.decimate_pro(1 - prm.decimate_to_faces / srf.n_cells, preserve_topology=True)
    srf = srf.clean().triangulate().compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True)
    out_stl = Path(out_stl)
    out_stl.parent.mkdir(parents=True, exist_ok=True)
    srf.save(str(out_stl), binary=True)
    print_info = None
    if phi_print is not None:
        im2 = pv.ImageData(dimensions=n, spacing=(h, h, h), origin=tuple(o + 0.5 * h))
        im2.point_data["phi"] = phi_print.ravel(order="F")
        sp = im2.contour([0.0], scalars="phi").triangulate().clean()
        sp = sp.smooth_taubin(n_iter=prm.taubin_iter, pass_band=prm.taubin_pass_band)
        if sp.n_cells > prm.decimate_to_faces:
            sp = sp.decimate_pro(1 - prm.decimate_to_faces / sp.n_cells, preserve_topology=True)
        p_print = out_stl.with_name(out_stl.stem + "_print_stock.stl")
        sp.clean().save(str(p_print), binary=True)
        sp = sp.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True)
        zf = sp.cell_centers().points[:, 2]
        dn = (sp.cell_data["Normals"][:, 2] < -0.95) & (zf < z0 + 1.0)
        print_info = {"stl": str(p_print), "volume_cm3": float(abs(sp.volume)) / 1e3, "stock_mm": prm.stock_mm,
                      "z_mounting_face_nominal_mm": float(z0),
                      "z_mounting_face_print_mm": float(np.median(zf[dn])) if dn.any() else float("nan")}
    nrm = srf.cell_data["Normals"]
    area = srf.compute_cell_sizes(length=False, volume=False).cell_data["Area"]
    cz = srf.cell_centers().points[:, prm.build_axis]
    down = nrm[:, prm.build_axis] < -math.cos(math.radians(prm.overhang_deg))
    on_plate = cz < o[prm.build_axis] + pad * h + 1.5 * h        # faces on the build plate (z = 30 mm)
    ov = down & ~on_plate
    edges = srf.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False,
                                      manifold_edges=False)
    bodies = srf.connectivity().point_data["RegionId"].max() + 1 if srf.n_points else 0
    # bore radius after smoothing: mean radial distance of surface points within 1.5 mm of each nominal bore
    bore_r = {}
    pts = srf.points
    for hid, hl in holes.items():
        if role.get(hid) not in ("support", "load"):
            continue
        c = hl.center * 1e3
        rad = np.sqrt(sum((pts[:, k] - c[k]) ** 2 for k in range(3) if k != hl.axis))
        m = np.zeros(len(pts), bool)
        for a, b in hl.segments:
            m |= (pts[:, hl.axis] > a * 1e3 + 3) & (pts[:, hl.axis] < b * 1e3 - 3)
        m &= np.abs(rad - hl.radius * 1e3) < 6.0
        bore_r[hid] = {"mean": float(rad[m].mean()), "min": float(rad[m].min()), "max": float(rad[m].max()),
                       "nominal": hl.radius * 1e3} if m.any() else None
    res = {"stl": str(out_stl), "params": asdict(prm), "grid": list(n), "threshold": tt,
           "target_volume_cm3": target / 1e3, "stages_cm3": stages, "surface_volume_cm3": float(abs(srf.volume)) / 1e3,
           "faces": int(srf.n_cells), "faces_before_decimation": int(n_full), "bodies": int(bodies),
           "islands_removed": int(max(nb - 1, 0)), "enclosed_voids_filled": n_voids,
           "open_or_nonmanifold_edges": int(edges.n_cells), "min_wall_mm": wall_min, "wall_p1_mm": wall_p1, "wall_p5_mm": wall_p5,
           "overhang_area_cm2": float(area[ov].sum()) / 100, "overhang_fraction": float(area[ov].sum() / area.sum()),
           "overhang_area_cm2_50deg": float(area[(nrm[:, prm.build_axis] < -math.cos(math.radians(50.0))) & ~on_plate].sum()) / 100,
           "surface_area_cm2": float(area.sum()) / 100, "bore_radius_mm": bore_r, "print_geometry": print_info, "seconds": time.perf_counter() - t0}
    log(f"finalize: {res['surface_volume_cm3']:.0f} cm3, {res['faces']} faces, bodies {bodies}, voids filled {n_voids}, "
        f"open edges {res['open_or_nonmanifold_edges']}, min wall {wall_min:.1f} mm, overhang {res['overhang_fraction']:.3f}")
    return res
