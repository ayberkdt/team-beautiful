"""Ashby-style property charts (E vs rho, strength vs rho) with performance-index guide lines.

    python scripts/ashby_chart.py      # pool if present, else the study files -> reports/figures_en/G4_*

Data: `research_notes/Malzeme havuzu/materials_pool.json` (properties rho [kg/m3], E [GPa], Fty [MPa], each with a
source and tag) when it exists; otherwise the materials of the trade-off studies (E, Fty, rho with their
`properties_source`). Guide lines pass through the reference material so that a point above the line beats it on
that index: E/rho (tie), E^(1/2)/rho (beam), E^(1/3)/rho (panel); Fty/rho, Fty^(2/3)/rho, Fty^(1/2)/rho.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402

POOL = ROOT / "research_notes" / "Malzeme havuzu" / "materials_pool.json"
STUDIES = ["bracket_hot_strength", "panel_cabin_stiffness"]
REF = "Al 2024-T3 sheet" if POOL.exists() else "2024-T3"     # the index lines pass through it
LABEL = {"CFRP QI IM7/8552", "Ti-6Al-4V L-PBF", "Inconel 718 L-PBF", "Mg WE43B / Elektron 43", "ULTEM 9085 (FDM)",
         "PA12 SLS (EOS PA 2200)", "Al 7075-T6 sheet", "Ti-6Al-4V", "Inconel 718"}
ORDER = ["Aluminium", "Titanium", "Steel / nickel", "Magnesium", "Composite", "Polymer", "Core"]
FAMILY_OF = {"aluminium": "Aluminium", "titanium": "Titanium", "steel": "Steel / nickel", "nickel": "Steel / nickel",
             "magnesium": "Magnesium", "composite": "Composite", "polymer": "Polymer", "core": "Core"}


def _family(name: str) -> str:
    n = name.lower()
    for key, fam in (("ti-", "titanium"), ("inconel", "nickel"), ("steel", "steel"), ("ph", "steel"),
                     ("300m", "steel"), ("az31", "magnesium"), ("we43", "magnesium"), ("elektron", "magnesium"),
                     ("cfrp", "composite"), ("gfrp", "composite"), ("glass", "composite"), ("flax", "composite"),
                     ("cf/", "composite"), ("peek", "polymer"), ("ultem", "polymer"), ("pa12", "polymer"),
                     ("nomex", "core")):
        if key in n:
            return fam
    return "aluminium"


def load() -> tuple[list[dict], str]:
    if POOL.exists():
        pool = json.loads(POOL.read_text(encoding="utf-8"))["materials"]
        rows = []
        for name, rec in pool.items():
            p = rec.get("properties", {})
            if "rho" in p and "E" in p:
                rows.append({"name": name, "family": rec.get("family", _family(name)), "rho": p["rho"]["value"],
                             "E": p["E"]["value"], "Fty": p.get("Fty", {}).get("value")})
        return rows, "material pool (research_notes/Malzeme havuzu)"
    rows, seen = [], set()
    for st in STUDIES:
        d = json.loads((ROOT / "studies" / "tradeoff" / f"{st}.json").read_text(encoding="utf-8"))
        for name, m in d["materials"].items():
            if name in seen or "E" not in m:
                continue
            seen.add(name)
            rows.append({"name": name, "family": _family(name), "rho": m["rho"], "E": m["E"] / 1e9,
                         "Fty": m.get("Fty", 0) / 1e6 or None})
    return rows, "trade-off study files"


def chart(rows: list[dict], prop: str, unit: str, exps: tuple[tuple[str, float], ...], ref: str, stem: str,
          source: str) -> None:
    pts = [r for r in rows if r.get(prop)]
    present = {FAMILY_OF.get(r["family"], r["family"]) for r in pts}
    fams = [f for f in ORDER if f in present]           # fixed order: a family keeps its colour in every chart
    cols = [c if dw.renk.contrast_ratio(c, "#ffffff") >= 3.0 else dw.renk.koyu_ton(c) for c in dw.paletler.kategorik()]
    marks = "osD^vPX*"
    fig, ax = dw.figur("makale", hedef="genel-cift", oran=0.62)
    for f in fams:
        i = ORDER.index(f)
        mine = [r for r in pts if FAMILY_OF.get(r["family"], r["family"]) == f]
        ax.scatter([r["rho"] for r in mine], [r[prop] for r in mine], s=28, color=cols[i % len(cols)],
                   marker=marks[i % len(marks)], label=f, zorder=3, edgecolor="white", linewidth=0.5)
    r0 = next((r for r in pts if r["name"] == ref), pts[0])
    rho = np.geomspace(min(r["rho"] for r in pts) * 0.7, max(r["rho"] for r in pts) * 1.4, 50)
    vals = [r[prop] for r in pts]
    top = max(vals) * 3
    for label, n in exps:                       # index P^n / rho constant -> P = (rho * k)^(1/n)
        k = r0[prop] ** n / r0["rho"]
        ax.plot(rho, (rho * k) ** (1 / n), color="#8c8c8c", lw=0.8, ls="--", zorder=1)
        x_end = min(rho[-1], top ** n / k)      # where the line leaves the plot
        ax.annotate(label, (x_end, (x_end * k) ** (1 / n)), fontsize=8, color="#4d4d4d", ha="right",
                    va="top" if x_end < rho[-1] else "bottom")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(min(vals) / 2, top)          # guide lines must not stretch the axis beyond the data
    ax.set_xlabel("Density (kg/m³)")
    ax.set_ylabel(f"{'Young’s modulus' if prop == 'E' else 'Yield strength'} ({unit})")
    for r in pts:                                # name only the points that stand apart from their family cluster
        if r["name"] in LABEL:
            ax.annotate(r["name"].split(" (")[0], (r["rho"], r[prop]), xytext=(4, -3), textcoords="offset points",
                        fontsize=8,
                        color="#4d4d4d")
    dw.lejant.yerlestir(ax)
    dw.kaydet(fig, str(ROOT / "reports" / "figures_en" / stem), hedef="genel-cift", cvd=True)


def main() -> int:
    rows, source = load()
    chart(rows, "E", "GPa", (("E/ρ", 1.0), ("E^(1/2)/ρ", 0.5), ("E^(1/3)/ρ", 1 / 3)), REF, "G4_ashby_E_rho", source)
    chart(rows, "Fty", "MPa", (("σ/ρ", 1.0), ("σ^(2/3)/ρ", 2 / 3), ("σ^(1/2)/ρ", 0.5)), REF, "G4_ashby_strength_rho",
          source)
    print(len(rows), "materials from", source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
