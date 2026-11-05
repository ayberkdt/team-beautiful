"""Competition-day command: task card JSON → first-half results and English slide figures.

    python scripts/card_day.py studies/cards/<card>.json            # topology runs included (~1-3 min)

Writes ``studies/cards/out/<card>/result.json`` and ``result.md`` and slide figures (datawiz, sunum-tam, English)
``S1_mass_deflection`` (``S1_mass_utilisation`` when the card adds a frequency, thermal or fatigue check),
``S2_life_co2``, ``S3_designs`` into the same folder. Card schema: aerokit.design.card.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.design import card as C  # noqa: E402
from aerokit.optimization import topology as tp  # noqa: E402

ROUTE_EN = {"machined": "machined", "machined_TO": "TO + machined", "am_TO": "TO + AM"}


def label(material: str, route: str) -> str:
    return f"{material} {ROUTE_EN.get(route, route)}"


def markdown(out: dict) -> str:
    lines = [f"# {out['card']}", "", f"Ultimate load {out['ultimate_N']:.0f} N (limit {out['limit_N']:.0f} N); "
             f"element {1000 * out['element_size_m']:.1f} mm; deflection mesh factor "
             f"{out['deflection_mesh_factor']:.3f}; stress check {out['tension_check']:.4f}.", "",
             "| Option | Retained volume | Mass (g) | Utilisation per check | Deflection (mm) | f1 (Hz) | Governs "
             "| Life CO₂ (kg) |",
             "|---|---:|---:|---|---:|---:|---|---:|"]
    for r in out["ranking"]:
        util = " · ".join(f"{k} {v:.2f}" for k, v in r.get("utilisation", {"strength": r["sigma_over_Fty"]}).items())
        f1 = f"{r['f1_Hz']:.0f}" if "f1_Hz" in r else "–"
        lines.append(f"| {label(r['material'], r['route'])} | {100 * r['volume']:.0f} % | {1000 * r['mass_kg']:.0f} | "
                     f"{util} | {1000 * r['deflection_m']:.3f} | {f1} | {r['governs']} | {r['co2_total_kg']:.0f} |")
    if not out["ranking"]:
        lines.append("| no option passes every check | | | | | | | |")
    gaps = sorted({f"{r['material']}: {', '.join(r['missing'])}" for r in out["rows"] if r.get("missing")})
    if gaps:
        lines += ["", "Not checked, data missing (add to the card's material_data): " + "; ".join(gaps)]
    if out["excluded"]:
        lines += ["", "Excluded: " + "; ".join(f"{e['material']} ({e['reason']})" for e in out["excluded"])]
    lines += ["", out["note"], ""]
    return "\n".join(lines)


def figures(out: dict, designs: list[dict], folder: Path, deflection_limit_m: float | None) -> None:
    import datawiz as dw
    S = dw.Seti(str(folder / "card.seti.json"), hedef="sunum-tam")
    S.nicelik("defl", "Tip deflection at limit load", "mm", eksen="x")
    S.nicelik("util", "Utilisation of the governing check", "–", eksen="x")
    S.nicelik("mass", "Part mass", "g", eksen="y")
    S.nicelik("co2", "Life-cycle CO₂", "t", eksen="x")
    names = [label(r["material"], r["route"]) for r in sorted(out["ranking"], key=lambda r: r["co2_total_kg"])]
    for r in out["rows"]:
        n = label(r["material"], r["route"])
        if n not in names:
            names.append(n)
    for n in names:
        S.varlik(n)
    for _ in range(2):      # second pass with a common plot-area margin measured from the first
        _slides(S, out, designs, folder, deflection_limit_m, names)
        if S.d.get("kenar_mm"):
            break
        S.kenar(*S.kenar_oner())


def _slides(S, out: dict, designs: list[dict], folder: Path, deflection_limit_m: float | None,
            names: list[str]) -> None:
    import datawiz as dw
    fig, ax = S.figur(oran=0.55)
    extra = any(set(r.get("utilisation", {})) - {"strength", "deflection"} for r in out["rows"])
    for n in names:
        mine = [r for r in out["rows"] if label(r["material"], r["route"]) == n and not r.get("missing")]
        pts = sorted(((max(r["utilisation"].values()) if extra else 1000 * r["deflection_m"]), 1000 * r["mass_kg"])
                     for r in mine)
        pts.sort(key=lambda p: p[1])        # join the designs in mass order (utilisation need not be monotonic)
        if pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], **S.stil(n, tur="cizgi", isaretli=True))
    if extra:
        dw.notlar.referans(ax, x=1.0, metin="limit")
    elif deflection_limit_m:
        dw.notlar.referans(ax, x=1000 * deflection_limit_m, metin="deflection limit")
    S.eksen(ax, x="util" if extra else "defl", y="mass")
    if len(names) >= 4:         # four or more options: the row above the axes wraps and runs off the edge
        dw.lejant.yerlestir(ax, yer="sag")
    else:
        dw.lejant.yerlestir(ax)
    S.kaydet(fig, str(folder / ("S1_mass_utilisation" if extra else "S1_mass_deflection")))
    if out["ranking"]:
        rk = sorted(out["ranking"], key=lambda r: r["co2_total_kg"])
        fig, ax = S.figur(oran=0.55)
        dw.ciz.yigin_cubuk(ax, [label(r["material"], r["route"]) for r in rk],
                           {"Production": [r["co2_production_kg"] / 1000 for r in rk],
                            "Use (fuel)": [r["co2_use_kg"] / 1000 for r in rk]}, yatay=True, deger_yaz=False)
        S.eksen(ax, x="co2")
        ax.set_xlim(0, max(r["co2_total_kg"] for r in rk) / 1000 * 1.25)
        for i, r in enumerate(rk):
            ax.annotate(f"{1000 * r['mass_kg']:.0f} g", (r["co2_total_kg"] / 1000, i), xytext=(6, 0),
                        textcoords="offset points", va="center")
        S.kaydet(fig, str(folder / "S2_life_co2"))
    fig, axs = S.figur(oran=0.26, ncols=len(designs))
    for a, d in zip(np.atleast_1d(axs), designs, strict=True):
        a.imshow(tp.binarize(d["density"], 0.5)["structure"], cmap="Greys", interpolation="nearest",
                      vmin=0, vmax=1)
        a.set_title(f"{100 * d['volume']:.0f} %", loc="left")
        a.set_xticks([])
        a.set_yticks([])
        a.set_anchor("N")
        for sp in a.spines.values():
            sp.set_visible(False)
    # black-and-white designs need no colour bar: one line says what black and the percentages mean
    np.atleast_1d(axs)[0].annotate("black = material · % = share of the design space kept", (0, 0),
                                   xycoords="axes fraction", xytext=(0, -8), textcoords="offset points",
                                   ha="left", va="top", annotation_clip=False)
    S.kaydet(fig, str(folder / "S3_designs"))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    # Windows consoles (cp1254/cp857) cannot print the audit's arrows: replace, do not crash mid-run
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    if not argv:
        print(__doc__)
        return 2
    card_path = Path(argv[0])
    card = C.load_card(card_path, root=ROOT)
    designs = C._designs(card)
    out = C.run(card, designs)
    folder = card_path.parent / "out" / card_path.stem
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float),
                                        encoding="utf-8")
    (folder / "result.md").write_text(markdown(out), encoding="utf-8")
    figures(out, designs, folder, card.deflection_limit_m)
    print(markdown(out))
    print(f"files: {folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
