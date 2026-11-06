"""hero_iso.png (light) and hero_iso_dark.png: studio render of the initial S275N bracket.

3600 x 2400 px output, rendered at 2x and Lanczos-downsampled (supersampling AA).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import geom as G  # noqa: E402
import render3d as R  # noqa: E402

OUT = (3600, 2400)
SS = 2
CAM = {"azim_deg": -128.0, "elev_deg": 27.0, "dist": 1650.0, "view_angle": 24.0}


def render(theme: str, path) -> None:
    part, src = R.load_part()
    edges = R.load_edges()
    p = R.new_plotter(theme, (OUT[0] * SS, OUT[1] * SS))
    R.add_studio_lights(p, theme)
    R.add_ground(p, theme)
    R.add_part(p, part, theme)
    R.set_camera(p, focal=R.CENTER + [0, 0, -25], **CAM)
    R.add_edges(p, edges, theme, lw=2.2 * SS)
    R.enable_ao(p)
    R.snap(p, path, OUT)
    p.close()
    print(f"wrote {path} ({src})")


def main() -> None:
    render("light", G.VIS / "hero_iso.png")
    render("dark", G.VIS / "hero_iso_dark.png")


if __name__ == "__main__":
    main()
