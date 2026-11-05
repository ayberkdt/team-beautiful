"""Shared 3-D rendering helpers (pyvista/VTK, off-screen): studio lights, soft contact shadow, B-rep edges.

The part is the exact rebuild visuals/initial_exact.stl (build_exact.py); if that file is missing the
organisers' facet STL is used with smooth shading and a warning is printed.
"""
from __future__ import annotations

import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import geom as G  # noqa: E402

import pyvista as pv  # noqa: E402
import vtk  # noqa: E402

pv.OFF_SCREEN = True
vtk.vtkMapper.SetResolveCoincidentTopologyToPolygonOffset()
vtk.vtkMapper.SetResolveCoincidentTopologyLineOffsetParameters(-1, -2)

THEMES = {
    "light": {"bg": (0.953, 0.957, 0.965), "steel": (0.640, 0.663, 0.690), "edge": (0.22, 0.24, 0.27),
              "edge_op": 0.55, "shadow": 0.55, "rim": 0.35, "gain": 1.0, "glow": 0.0},
    "dark": {"bg": (0.090, 0.102, 0.118), "steel": (0.600, 0.624, 0.655), "edge": (0.10, 0.11, 0.13),
             "edge_op": 0.70, "shadow": 0.90, "rim": 0.60, "gain": 0.78, "glow": 0.075},
}
CENTER = np.array([(G.X0 + G.X1) / 2, (G.Y0 + G.Y1) / 2, (G.Z0 + G.Z_TOP) / 2])


def load_part() -> tuple[pv.PolyData, str]:
    stl = G.VIS / "initial_exact.stl"
    src = "exact"
    if not stl.exists():
        warnings.warn("initial_exact.stl missing: rendering the facet STL (coarse, smooth-shaded)")
        stl, src = G.FACET_STL, "facets"
    m = pv.read(str(stl)).clean(tolerance=1e-6, absolute=False).triangulate()
    m = m.compute_normals(split_vertices=True, feature_angle=35, auto_orient_normals=True,
                          consistent_normals=True)
    return m, src


def load_edges(step: float = 1.5) -> np.ndarray | None:
    """B-rep edge segments (N, 2, 3) from build_exact.py, subdivided to pieces <= step mm."""
    f = G.HERE / "out" / "brep_edges.npz"
    if not f.exists():
        return None
    d = np.load(f)
    out, cid = [], []
    for a, b, c in zip(d["a"], d["b"], d["curve"]):
        k = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        t = np.linspace(0, 1, k + 1)[:, None]
        q = a + t * (b - a)
        out.append(np.stack([q[:-1], q[1:]], axis=1))
        cid.append(np.full(k, c))
    segs = np.concatenate(out)
    global _CURVE
    _CURVE = np.concatenate(cid)
    return segs


_CURVE: np.ndarray | None = None


def _drop_short_runs(keep: np.ndarray, curve: np.ndarray, min_run: int = 4) -> np.ndarray:
    """Remove visible runs shorter than min_run pieces (specks where a hidden edge grazes a silhouette)."""
    out = keep.copy()
    i, n = 0, len(keep)
    while i < n:
        if not keep[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and keep[j + 1] and curve[j + 1] == curve[i]:
            j += 1
        if j - i + 1 < min_run:
            out[i:j + 1] = False
        i = j + 1
    return out


def visible_edges(p: pv.Plotter, segs: np.ndarray, tol: float = 1.2) -> pv.PolyData:
    """Keep the edge pieces whose midpoint is not hidden by the part (depth-buffer test).

    Polygon offset alone lets hidden edges poke through near silhouettes; this removes them. The scene must
    already hold the part (and nothing in front of it)."""
    if not getattr(p, "_rendered", False):
        p.show(auto_close=False, interactive=False)
    p.render()
    depth = -np.asarray(p.get_image_depth(fill_value=np.nan, reset_camera_clipping_range=False))      # camera distance along view axis, (H, W)
    H, W = depth.shape
    mid = segs.mean(axis=1)
    cam = np.array(p.camera.position)
    fwd = np.array(p.camera.focal_point) - cam
    fwd /= np.linalg.norm(fwd)
    dist = (mid - cam) @ fwd
    px = world_to_px(p, mid)
    ix = np.clip(np.round(px[:, 0]).astype(int), 0, W - 1)
    iy = np.clip(np.round(px[:, 1]).astype(int), 0, H - 1)
    zb = depth[iy, ix]
    keep = np.isnan(zb) | (dist <= zb + tol)
    if _CURVE is not None and len(_CURVE) == len(keep):
        keep = _drop_short_runs(keep, _CURVE)
    a, b = segs[keep, 0], segs[keep, 1]
    n = len(a)
    lines = np.column_stack([np.full(n, 2), np.arange(n), np.arange(n) + n]).ravel()
    return pv.PolyData(np.vstack([a, b]), lines=lines)


def footprint_shadow(theme: str, res: float = 2.0, margin: float = 420.0) -> tuple[pv.PolyData, pv.Texture]:
    """Textured ground plane under the part: blurred overhead footprint (plate outline minus the 4 through
    bores), two blur widths (contact + ambient). Plane lies 0.3 mm below the underside, in the part frame."""
    from scipy.ndimage import gaussian_filter
    T = THEMES[theme]
    x0, x1 = G.X0 - margin, G.X1 + margin
    y0, y1 = G.Y0 - margin, G.Y1 + margin
    nx, ny = int((x1 - x0) / res), int((y1 - y0) / res)
    X, Y = np.meshgrid(x0 + (np.arange(nx) + 0.5) * res, y0 + (np.arange(ny) + 0.5) * res)
    # rounded rectangle
    cx = np.clip(X, G.X0 + G.R_CORNER, G.X1 - G.R_CORNER)
    cy = np.clip(Y, G.Y0 + G.R_CORNER, G.Y1 - G.R_CORNER)
    inside = ((X - cx) ** 2 + (Y - cy) ** 2 <= G.R_CORNER ** 2) & (X >= G.X0) & (X <= G.X1) & (Y >= G.Y0) & (Y <= G.Y1)
    for bx, by in G.BOLTS:
        inside &= (X - bx) ** 2 + (Y - by) ** 2 > G.R_BORE ** 2
    m = inside.astype(float)
    a = 0.95 * gaussian_filter(m, 5.0 / res) + 0.55 * gaussian_filter(m, 45.0 / res) \
        + 0.25 * gaussian_filter(m, 140.0 / res)
    a = np.clip(a / 1.2, 0, 1) * T["shadow"]
    bg = np.array(T["bg"])
    # dark theme: faint elliptical floor glow under the part (reaches 0 inside the plane, so no visible edge)
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    r = np.sqrt(((X - (x0 + x1) / 2) / rx) ** 2 + ((Y - (y0 + y1) / 2) / ry) ** 2)
    floor = bg[None, None, :] + T["glow"] * np.clip(1 - r, 0, 1)[..., None] ** 1.5
    rgb = floor * (1.0 - a[..., None])
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    plane = pv.Plane(center=((x0 + x1) / 2, (y0 + y1) / 2, G.Z0 - 0.3), direction=(0, 0, 1),
                     i_size=x1 - x0, j_size=y1 - y0, i_resolution=1, j_resolution=1)
    plane.texture_map_to_plane(inplace=True)
    tex = pv.Texture(img)                  # numpy row 0 = texture v = 0 (y0 side)
    tex.interpolate = True
    return plane, tex


def add_studio_lights(p: pv.Plotter, theme: str, rot_deg: float = 0.0) -> None:
    """Key/fill/kicker/rim/top lights; rot_deg turns the whole rig about z (turntable: rig follows camera)."""
    T = THEMES[theme]
    p.remove_all_lights()
    c = CENTER
    cr, sr = np.cos(np.radians(rot_deg)), np.sin(np.radians(rot_deg))
    for d, inten in [((-0.35, -1.0, 0.85), 0.95),   # key: front, camera-left, medium height
                     ((-1.0, -0.15, 0.35), 0.42),   # fill: left end faces
                     ((1.2, -0.4, 0.5), 0.20),      # kicker: right
                     ((0.4, 1.6, 0.9), T["rim"]),   # rim: behind
                     ((0.0, 0.0, 1.0), 0.22)]:      # top
        d = np.asarray(d, float) / np.linalg.norm(d)
        d = np.array([cr * d[0] - sr * d[1], sr * d[0] + cr * d[1], d[2]])
        p.add_light(pv.Light(position=tuple(c + 2000 * d), focal_point=tuple(c), intensity=inten * T["gain"],
                             light_type="scene light"))
    p.add_light(pv.Light(light_type="headlight", intensity=0.12))


def new_plotter(theme: str, size: tuple[int, int]) -> pv.Plotter:
    p = pv.Plotter(off_screen=True, window_size=list(size), lighting="none")
    p.set_background(THEMES[theme]["bg"])
    return p


def add_part(p: pv.Plotter, part: pv.PolyData, theme: str, color=None, **kw):
    T = THEMES[theme]
    return p.add_mesh(part, color=color or T["steel"], smooth_shading=True, specular=0.55, specular_power=28,
                      diffuse=0.80, ambient=0.16, **kw)


def add_edges(p: pv.Plotter, segs: np.ndarray | None, theme: str, lw: float):
    """Call after the camera is set and the part is in the scene (visibility is camera dependent)."""
    if segs is None:
        return None
    T = THEMES[theme]
    return p.add_mesh(visible_edges(p, segs), color=T["edge"], line_width=lw, opacity=T["edge_op"],
                      lighting=False)


def add_ground(p: pv.Plotter, theme: str) -> None:
    plane, tex = footprint_shadow(theme)
    p.add_mesh(plane, texture=tex, lighting=False, show_scalar_bar=False)


def set_camera(p: pv.Plotter, azim_deg: float, elev_deg: float, dist: float, view_angle: float = 22.0,
               focal=None, parallel: bool = False, parallel_scale: float | None = None) -> None:
    f = CENTER if focal is None else np.asarray(focal)
    az, el = np.radians(azim_deg), np.radians(elev_deg)
    d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    p.camera.position = tuple(f + dist * d)
    p.camera.focal_point = tuple(f)
    p.camera.up = (0, 0, 1)
    p.camera.view_angle = view_angle
    if parallel:
        p.camera.enable_parallel_projection()
        if parallel_scale:
            p.camera.parallel_scale = parallel_scale
    p.camera.clipping_range = (10, dist * 4)


def enable_ao(p: pv.Plotter) -> None:
    try:
        p.enable_ssao(radius=35.0, bias=3.0, kernel_size=256, blur=True)   # bias < ~2 bands on the R80 fillets
    except Exception as e:  # pragma: no cover
        warnings.warn(f"SSAO not available: {e}")


def snap(p: pv.Plotter, path, out_size: tuple[int, int]) -> np.ndarray:
    """Render, downsample the supersampled frame to out_size (Lanczos) and save PNG."""
    from PIL import Image
    img = p.screenshot(return_img=True)
    im = Image.fromarray(img)
    if im.size != tuple(out_size):
        im = im.resize(out_size, Image.LANCZOS)
    if path:
        im.save(path, optimize=True)
    return np.asarray(im)


def world_to_px(p: pv.Plotter, pts: np.ndarray, ss: float = 1.0) -> np.ndarray:
    """World points -> output-image pixel coordinates (x right, y down), after supersample factor ss."""
    ren = p.renderer
    W, H = p.window_size
    out = []
    c = vtk.vtkCoordinate()
    c.SetCoordinateSystemToWorld()
    for q in np.atleast_2d(pts):
        c.SetValue(*map(float, q))
        dx, dy = c.GetComputedDoubleDisplayValue(ren)
        out.append((dx / ss, (H - dy) / ss))
    return np.array(out)
