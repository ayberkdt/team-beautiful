"""turntable/frame_000.png ... frame_071.png: 360 deg camera orbit about the vertical axis, 1920 x 1080.

The camera orbits (5 deg per frame) and the studio light rig turns with it, so on screen the part appears to
rotate under fixed studio lights; the soft ground shadow is attached to the part. Writes turntable/README.md.
Usage: python turntable.py [--theme light|dark] [--frames 72]
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import geom as G  # noqa: E402
import render3d as R  # noqa: E402

OUT = (1920, 1080)
SS = 2
AZ0, ELEV, DIST, VIEW_ANGLE, DZ = -128.0, 27.0, 1600.0, 24.0, -25.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="light", choices=list(R.THEMES))
    ap.add_argument("--frames", type=int, default=72)
    a = ap.parse_args()
    out = G.VIS / "turntable"
    out.mkdir(exist_ok=True)
    part, src = R.load_part()
    segs = R.load_edges()
    p = R.new_plotter(a.theme, (OUT[0] * SS, OUT[1] * SS))
    R.add_ground(p, a.theme)
    R.add_part(p, part, a.theme)
    R.enable_ao(p)
    focal = R.CENTER + np.array([0, 0, DZ])
    step = 360.0 / a.frames
    edge_actor = None
    for k in range(a.frames):
        az = AZ0 + k * step
        R.add_studio_lights(p, a.theme, rot_deg=k * step)
        R.set_camera(p, az, ELEV, DIST, view_angle=VIEW_ANGLE, focal=focal)
        if edge_actor is not None:
            p.remove_actor(edge_actor)
        edge_actor = R.add_edges(p, segs, a.theme, lw=1.6 * SS)
        R.snap(p, out / f"frame_{k:03d}.png", OUT)
        if k % 12 == 0:
            print(f"frame {k:03d} azimuth {az:.1f} deg")
    p.close()
    readme = f"""# Turntable frames — official initial S275N bracket

{a.frames} PNG frames, `frame_000.png` … `frame_{a.frames - 1:03d}.png`, {OUT[0]} × {OUT[1]} px, 8-bit RGB, no alpha.
Made by `python visuals/scripts/turntable.py --theme {a.theme} --frames {a.frames}` (pyvista {R.pv.__version__} /
VTK {R.vtk.vtkVersion.GetVTKVersion()}, off-screen OpenGL, rendered at {SS}× and Lanczos-downsampled). Geometry:
`visuals/initial_exact.stl` ({src} rebuild, see `visuals/README.md`). No video was encoded (no ffmpeg on this
machine).

## Camera (CAD frame, mm, z up)

| Parameter | Value |
|---|---|
| Projection | perspective, vertical view angle {VIEW_ANGLE:.0f}° |
| Focal point | ({focal[0]:.2f}, {focal[1]:.2f}, {focal[2]:.2f}) — bounding-box centre, {abs(DZ):.0f} mm lowered |
| Distance to focal point | {DIST:.0f} |
| Elevation | {ELEV:.0f}° above the x–y plane |
| Azimuth of frame k | {AZ0:.0f}° + k × {step:.0f}° (measured from +x towards +y; frame 0 = hero azimuth and elevation; hero.py uses distance 1650 at 3:2) |
| Direction of travel | counter-clockwise seen from above (+z) → the part appears to turn clockwise |
| Up vector | (0, 0, 1) |
| Lights | key/fill/kicker/rim/top rig turned with the camera (constant look on screen) + 0.12 headlight |
| Ground | soft overhead contact shadow, attached to the part (rotates with it) |

## Assemble (for the film session)

At 24 fps the 72 frames last 3.0 s per revolution; loop it, or use 12 fps for 6 s. Example (if ffmpeg is
available elsewhere):

```
ffmpeg -framerate 24 -i frame_%03d.png -c:v libx264 -pix_fmt yuv420p -crf 16 turntable.mp4
```
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
