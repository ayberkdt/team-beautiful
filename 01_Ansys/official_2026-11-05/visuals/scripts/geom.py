"""Exact geometry of the official EUROAVIA Ideathon 2026 Ansys bracket (initial S275N design).

Every number here is read from ../../derived/features.json (measured from the organisers' Discovery
tessellation) and ../../setup/setup_official_fixed_bores.json; see build_exact.py for the volume check.
Units: mm, CAD frame of the Discovery file (z up).
"""
from __future__ import annotations

import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIS = HERE.parent                       # .../official_2026-11-05/visuals
ROOT = VIS.parent                       # .../official_2026-11-05
FEATURES = ROOT / "derived" / "features.json"
FACET_STL = ROOT / "derived" / "initial_from_facets.stl"
SETUP = ROOT / "setup" / "setup_official_fixed_bores.json"

# plate (features: faces 53, 98, 95, 101, 107, 104; corner cylinders 83/86/89/92 R100)
X0, X1 = 170.0, 831.01
Y0, Y1 = 30.0, 371.12
Z0, Z1 = 30.0, 100.0
R_CORNER = 100.0
# bolt bores (faces 110/113/116/119, fit Ø59.96 = tessellation chord of Ø60)
BOLTS = [(245.0, 95.0), (245.0, 305.0), (755.0, 95.0), (755.0, 305.0)]
R_BORE = 30.0
# lugs (faces 80/68 inner planes, 107/104 outer planes)
LUGS = [(30.0, 100.0), (300.0, 371.12)]
# lug profile in x-z (faces 71/44 top arc, 59/50 and 62/38 root fillets, 65/74/41/47 flanks)
ARC_C = (500.0, 241.37)
R_ARC = 80.0
FIL_L = (326.95, 180.0)
FIL_R = (673.0, 180.0)
R_FIL = 80.0
PIN = (500.0, 260.0)                    # pin bore axis (x, z), axis along y (faces 56/77)
Z_TOP = ARC_C[1] + R_ARC                # 321.37

VOLUME_REF_M3 = 0.019400                # derived/initial_from_facets.stl (boundary_conditions.md §1)
RHO = 7850.0


def flank(fil: tuple[float, float], side: int) -> dict:
    """Internal common tangent of the top arc (material inside) and a root fillet (material outside).

    Both radii are 80 mm, so the tangent passes through the midpoint of the two centres.
    side = +1 right flank, -1 left flank. Returns the unit outward normal n, offset c (n.p = c),
    tangent point on the arc and on the fillet, and the flank angle from horizontal (deg).
    """
    ax, az = ARC_C
    fx, fz = fil
    dx, dz = fx - ax, fz - az
    d = math.hypot(dx, dz)
    # n such that n.(fil - arc) = 2R (arc centre at -R, fillet centre at +R from the line)
    phi = math.atan2(dz, dx)
    beta = math.acos(2 * R_ARC / d)
    cands = [(math.cos(phi + s * beta), math.sin(phi + s * beta)) for s in (+1, -1)]
    # outward normal of a flank points sideways and slightly up (z component > 0)
    n = max(cands, key=lambda v: v[1])
    c = n[0] * ax + n[1] * az + R_ARC
    t_arc = (ax + R_ARC * n[0], az + R_ARC * n[1])
    t_fil = (fx - R_FIL * n[0], fz - R_FIL * n[1])
    ang = math.degrees(math.atan2(abs(n[0]), abs(n[1])))  # line angle from horizontal = angle of n from vertical
    return {"n": n, "c": c, "t_arc": t_arc, "t_fil": t_fil, "angle_deg": ang, "side": side}


FLANK_R = flank(FIL_R, +1)
FLANK_L = flank(FIL_L, -1)
