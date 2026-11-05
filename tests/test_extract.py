"""Density field -> contours (DXF) and surface (STL): areas, volumes, topology and a DXF round trip."""
import numpy as np

from aerokit.cad.dxf import read_dxf
from aerokit.optimization import extract as ex
from aerokit.verification import check, check_true


def _disc(n=80, r=25.0, hole=0.0):
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2)
    return ((d <= r) & (d >= hole)).astype(float)


def test_contour_area_and_holes():
    rings = ex.contours(_disc(), 0.5, 1.0)
    check("one closed ring for a disc", float(len(rings)), 1.0, atol=0.0)
    check("disc area within 1 % of pi r^2", ex.ring_area(rings[0]), np.pi * 25.0 ** 2, rtol=0.01)
    check("smoothing keeps the area", ex.ring_area(ex.taubin(rings[0], 20)), np.pi * 25.0 ** 2, rtol=0.01)
    ann = ex.contours(_disc(hole=12.0), 0.5, 1.0)
    check("annulus gives two rings", float(len(ann)), 2.0, atol=0.0)


def test_dxf_round_trip(tmp_path):
    p = tmp_path / "annulus.dxf"
    info = ex.to_dxf(p, _disc(hole=12.0), h_mm=2.0)
    check_true("one region with one hole", info["regions"] == 1 and info["holes"] == 1)
    regions, _ = read_dxf(p)
    a_out = ex.ring_area(regions[0]["outer"] * 1000) - sum(ex.ring_area(hh * 1000) for hh in regions[0]["holes"])
    check("DXF read back: same net area (mm2)", a_out, np.pi * (50.0 ** 2 - 24.0 ** 2), rtol=0.02)


def test_surface_nets_sphere(tmp_path):
    n, r = 30, 10.0
    z, y, x = np.mgrid[0:n, 0:n, 0:n] + 0.5
    f = (np.sqrt((x - n / 2) ** 2 + (y - n / 2) ** 2 + (z - n / 2) ** 2) <= r).astype(float)
    V, F = ex.surface_nets(f, 0.5, 1.0)
    check_true("watertight: every edge in two triangles", ex.watertight(F))
    vol = ex.mesh_volume(V, F)
    check_true("outward orientation (positive volume)", vol > 0)
    check("sphere volume within 4 % of 4/3 pi r^3", vol, 4 / 3 * np.pi * r ** 3, rtol=0.04)
    Vs = ex.laplacian_smooth(V, F, 5)
    check("smoothing keeps the volume within 4 %", ex.mesh_volume(Vs, F), 4 / 3 * np.pi * r ** 3, rtol=0.04)
    p = ex.write_stl(tmp_path / "s.stl", Vs, F)
    check("binary STL size = 84 + 50 bytes per triangle", float((tmp_path / "s.stl").stat().st_size),
          84.0 + 50.0 * len(F), atol=0.0)
    check_true("path returned", p.endswith("s.stl"))


def test_solid_touching_the_boundary_stays_closed():
    b = np.zeros((10, 10, 10))
    b[0:6, 2:8, 2:8] = 1.0                         # touches the x = 0 face of the design space
    V, F = ex.surface_nets(b, 0.5, 1.0)
    check("no open edge", float(ex.edge_report(F)["open"]), 0.0, atol=0.0)
    check_true("closed and manifold", ex.watertight(F))


def test_mass_preserving_level():
    t = np.zeros((12, 12, 12))
    t[2:10, 2:10, 5] = 1.0
    t = 0.25 * (np.roll(t, 1, 2) + np.roll(t, -1, 2)) + 0.5 * t     # a blurred one-voxel plate
    lvl = ex.mass_preserving_level(t, 64.0, 1.0)
    V, F = ex.surface_nets(t, lvl, 1.0)
    check("iso-level chosen to enclose the target volume", ex.mesh_volume(V, F), 64.0, rtol=0.02)
