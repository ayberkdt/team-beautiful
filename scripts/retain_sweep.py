"""Volume-retain sweep on the L-bracket benchmark: the template of the jury's "mass vs stiffness" curve.

    python scripts/retain_sweep.py            # writes studies/retain_sweep/retain_sweep.json and reports/figures/F5_*
    python scripts/retain_sweep.py --figure-only   # redraw F5 from the saved JSON
    python scripts/retain_sweep.py --figure-only --lang en   # English F5 in reports/figures_en/

Runs aerokit's SIMP (top88) on the L-bracket for several retained-volume fractions and records compliance,
iterations and the grey measure. On competition day the same table is filled from Discovery / Mechanical runs.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402

from aerokit.optimization import topology as tp  # noqa: E402

VOLUMES = (0.5, 0.35, 0.25, 0.15)
N, RMIN, FT = 60, 2.4, 2
OUT_JSON = ROOT / "studies" / "retain_sweep" / "retain_sweep.json"
EN = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en"
FIG = ROOT / "reports" / ("figures_en" if EN else "figures")


def run() -> list[dict]:
    rows = []
    for v in VOLUMES:
        t0 = time.perf_counter()
        r = tp.topopt(tp.l_bracket(N), v, RMIN, ft=FT, optimizer="OC", max_iter=400)
        rows.append({"volume": v, "compliance": float(r["compliance"][-1]), "iterations": int(r["iteration"]),
                     "converged": bool(r["converged"]), "grey_percent": float(r["gray"]),
                     "seconds": round(time.perf_counter() - t0, 1), "density": np.asarray(r["xfiz"]).tolist()})
    ref = next(x["compliance"] for x in rows if x["volume"] == 0.5)
    for x in rows:
        x["compliance_rel"] = x["compliance"] / ref
    return rows


def figure(rows: list[dict]) -> None:
    S = dw.Seti(str(FIG / "rapor.seti.json"))
    S.nicelik("hacim", "Retained volume fraction" if EN else "Korunan hacim oranı", "%", eksen="x")
    S.nicelik("uyum", "Compliance (relative to 50 % design)" if EN else "Uyum (%50 tasarıma göre)", "–", eksen="y")
    S.nicelik("yogunluk", "Material density" if EN else "Malzeme yoğunluğu", "–", eksen="serbest")
    dec = "." if EN else ","
    fig, axd = S.figur(oran=0.5, mozaik=[["egri", "egri", "d50", "d35"], ["egri", "egri", "d25", "d15"]])
    ax = axd["egri"]
    x = [100 * r["volume"] for r in rows]
    y = [r["compliance_rel"] for r in rows]
    ax.plot(x, y, marker="o", ms=8, color="#4d4d4d", lw=1.2)
    for xi, yi in zip(x, y, strict=True):
        ax.annotate(f"{yi:.2f}".replace(".", dec), (xi, yi), xytext=(6, 6), textcoords="offset points", fontsize=8)
    S.eksen(ax, x="hacim", y="uyum")
    ax.set_xlim(10, 60)
    ax.set_ylim(0, None)
    im = None
    for r, key in zip(rows, ("d50", "d35", "d25", "d15"), strict=True):
        a = axd[key]
        im = a.imshow(np.asarray(r["density"]), cmap="Greys", vmin=0, vmax=1, interpolation="nearest")
        pct = int(round(100 * r["volume"]))
        a.set_title(f"{pct} %" if EN else f"%{pct}", loc="left")
        a.set_xticks([])
        a.set_yticks([])
        a.tick_params(direction="out")
        a.set_anchor("N")
        for s in a.spines.values():
            s.set_visible(False)
    cb = S.renk_cubugu(fig, im, "yogunluk", ax=[axd["d35"], axd["d15"]], shrink=0.45, ticks=[0, 0.5, 1])
    cb.ax.set_yticklabels(["0", f"0{dec}5", "1"])
    cb.ax.yaxis.labelpad = 6
    S.kaydet(fig, str(FIG / "F5_hacim_taramasi"), cvd=False)


def main() -> int:
    if "--figure-only" in sys.argv and OUT_JSON.exists():
        figure(json.loads(OUT_JSON.read_text(encoding="utf-8"))["runs"])
        return 0
    rows = run()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    meta = {"problem": f"l_bracket({N})", "rmin": RMIN, "ft": FT, "optimizer": "OC",
            "note": "compliance_rel = compliance / compliance at 50 % retained volume; unit load, unit modulus"}
    OUT_JSON.write_text(json.dumps({"meta": meta, "runs": rows}, indent=1), encoding="utf-8")
    for r in rows:
        print(f"V={r['volume']:.2f}  c={r['compliance']:.3f}  rel={r['compliance_rel']:.2f}  it={r['iterations']}"
              f"  conv={r['converged']}  grey={r['grey_percent']:.1f}%  {r['seconds']} s")
    figure(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
