"""Four views (iso, underside iso, side x-z, top) of an STL with pyvista, off-screen, for a visual check of the
layout (base skin, lug eyes, bosses). python -I analysis/render_views.py <stl> <out.png>"""
import sys
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "D:/tmp_ideathon/pylib")
import pyvista as pv   # noqa: E402

stl, out = Path(sys.argv[1]), Path(sys.argv[2])
mesh = pv.read(str(stl))
c = np.array(mesh.center)
L = max(mesh.bounds[1] - mesh.bounds[0], mesh.bounds[3] - mesh.bounds[2], mesh.bounds[5] - mesh.bounds[4])
views = [("iso", (1.2, -1.6, 1.1), (0, 0, 1)), ("underside", (1.2, -1.6, -1.1), (0, 0, 1)),
         ("side (x-z)", (0, -1, 0), (0, 0, 1)), ("end (y-z)", (1, 0, 0), (0, 0, 1))]
p = pv.Plotter(off_screen=True, shape=(2, 2), window_size=(1600, 1200), border=False)
for i, (name, d, up) in enumerate(views):
    p.subplot(i // 2, i % 2)
    p.set_background("white")
    p.add_mesh(mesh, color="#9aa3ad", smooth_shading=True, specular=0.2)
    d = np.array(d, float) / np.linalg.norm(d)
    p.camera_position = [tuple(c + 2.6 * L * d), tuple(c), up]
    if name.startswith(("side", "end")):
        p.enable_parallel_projection()
    p.add_text(name, font_size=12, color="#222222")
p.screenshot(str(out))
print("wrote", out)
