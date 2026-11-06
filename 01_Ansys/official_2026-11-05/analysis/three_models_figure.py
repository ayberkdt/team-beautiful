"""Figure: the three models side by side (initial, topology-optimised, finalized), iso + end view.

FİGÜR BRİFİ — three_models
  Mesaj   : the finalized part keeps the original base, lug eyes and bolt bosses, is one body, and weighs a quarter
            of the initial steel part
  Okur    : karma (team + jury) · Ortam: sunum-tam · Tema: akademik (datawiz set default)
  Veri    : 3 STL renders (nominal geometry) + mass / σ / u from analysis/finalize_v2_<tag>.json and verify json
  Karşılaştırma: initial → TO → finalized (one row per view, same camera per row)
  Biçim   : small multiples of renders (no axes), panel letters, numbers in the column titles

python -I analysis/three_models_figure.py <tag> -> analysis/figures/three_models.png/.pdf (+ datawiz audit)
"""
import json, os, sys
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path[:0] = ["D:/tmp_ideathon/pylib"]
import matplotlib   # noqa: E402
matplotlib.use("Agg")
import pyvista as pv   # noqa: E402
import datawiz as dw   # noqa: E402

tag = int(sys.argv[1])
CASE = os.environ.get("CASE", "topo_v3_skeleton")
RUN = HERE.parent / "runs" / CASE
fin = json.loads((HERE / f"finalize_{CASE}_{tag}.json").read_text(encoding="utf-8"))
ver = json.loads((HERE / ("verify_v2.json" if CASE == "topo_v2_base_kept" else f"verify_{CASE}.json")).read_text(encoding="utf-8"))
lay = next(x for x in ver["layouts"] if round(100 * x["volfrac"]) == tag)
models = [("Initial, S275N", HERE.parent / "visuals" / "initial_exact.stl", "152.3 kg\n "),
          (f"Topology ({tag} %)", RUN / "cad" / f"optimised_{tag}.stl",
           f"{lay['mass_Ti811_kg']:.1f} kg Ti\nσ {lay['sigma_max_MPa']:.0f} MPa · {lay['disp_mm_300C']:.2f} mm"),
          ("Finalized", Path(fin["finalize"]["stl"]),
           f"{fin['t10']['mass_Ti811_kg']:.1f} kg Ti\nσ {fin['t10']['sigma_max_MPa']:.0f} MPa · {fin['t10']['disp_mm_300C']:.2f} mm")]
VIEWS = [((1.2, -1.6, 1.0), False), ((1.0, 0.0, 0.0), True)]


def render(stl, d, parallel, size=(1100, 800)):
    m = pv.read(str(stl))
    p = pv.Plotter(off_screen=True, window_size=list(size))
    p.set_background("white")
    p.add_mesh(m, color="#b9c4cf", smooth_shading=True, specular=0.3)
    c = np.array(m.center)
    d = np.array(d, float) / np.linalg.norm(d)
    p.camera_position = [tuple(c + 1800 * d), tuple(c), (0, 0, 1)]
    if parallel:
        p.enable_parallel_projection()
    p.reset_camera()
    img = np.asarray(p.screenshot(return_img=True))
    p.close()
    return img


ims = [[render(stl, d, par) for (_, stl, _) in models] for d, par in VIEWS]
(HERE / "figures").mkdir(exist_ok=True)
S = dw.Seti(str(HERE / "figures" / "three_models.seti.json"), hedef="sunum-tam")
fig, axs = S.figur(oran=0.62, nrows=2, ncols=3, layout="compressed")
for r in range(2):
    for k in range(3):
        ax = axs[r][k]
        ax.imshow(ims[r][k])
        ax.set_axis_off()
        if r == 0:
            ax.set_title(f"{models[k][0]}\n{models[k][2]}", fontsize=18)
dw.etiket.panel_harfleri([a for row in axs for a in row])
res = S.kaydet(fig, str(HERE / "figures" / "three_models"), cvd=False, kati=True, sessiz=True)
print("audit:", {k: v for k, v in res.items() if k in ("hata", "uyari")})
