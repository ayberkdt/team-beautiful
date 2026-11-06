"""Material selection report for the 300 °C bracket (geometry independent): comparison table, Ashby indices at
20 °C and at the working temperature, 300 °C screen, CO₂, AM route, cards, one figure.

    python 01_Ansys/scripts/bracket_material_report.py [--temperature 300]

Writes 01_Ansys/outputs/material_selection/: material_selection.md, comparison.csv,
materials_engineering_data.xml, card_<key>.md, fig_relative_mass.(png|pdf) with its datawiz audit.

Indices (aerokit.materials.selection, Ashby method; source cited there): light strong beam M = Fty^(2/3)/ρ (the
bending-dominated bracket arms), light stiff beam M = E^(1/2)/ρ, light strong tie M = Fty/ρ (lugs in tension);
the same divided by kg CO₂/kg gives the least-CO₂ ranking. A material must first pass the screen
Tmax ≥ working temperature.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.bracket import cards, matdata  # noqa: E402
from aerokit.materials.selection import rank  # noqa: E402

OUT = ROOT / "01_Ansys" / "outputs" / "material_selection"
CASES = (("beam_strong", "light strong beam Fty^2/3/ρ"), ("beam_stiff", "light stiff beam E^1/2/ρ"),
         ("tie_strong", "light strong tie Fty/ρ"))


def records(T: float) -> dict[str, dict[str, float]]:
    return {m.key: {"E": m.E_at(T), "Fty": m.Fty_at(T), "rho": m.rho.value} for m in matdata.CANDIDATES.values()}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--temperature", type=float, default=300.0)
    a = ap.parse_args(argv)
    T = a.temperature
    OUT.mkdir(parents=True, exist_ok=True)
    mats = list(matdata.CANDIDATES.values())
    ok = {m.key: m.Tmax.value >= T for m in mats}
    co2 = {m.key: m.co2.value for m in mats}
    rel: dict[tuple[str, str, float], float] = {}
    for case, _ in CASES:
        for temp in (20.0, T):
            for r in rank(case, records(temp)):
                rel[(case, r.name, temp)] = r.relative_mass
    rel_co2 = {r.name: r.relative_mass for r in rank("beam_strong", records(T), co2_per_kg=co2)}
    # ---------------- CSV
    cols = ["key", "material", "route", "AM", "rho_kg_m3", "E20_GPa", f"E{T:g}_GPa", "Fty20_MPa", f"Fty{T:g}_MPa",
            "Tmax_C", f"passes_{T:g}C_screen", "rel_mass_beam_strong_20C", f"rel_mass_beam_strong_{T:g}C",
            f"rel_mass_beam_stiff_{T:g}C", f"rel_mass_tie_strong_{T:g}C", "co2_kg_per_kg", "price_EUR_per_kg",
            f"rel_co2_beam_strong_{T:g}C", "factor_source", "factor_tag"]
    with (OUT / "comparison.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for m in mats:
            w.writerow([m.key, m.name, m.route, m.am, m.rho.value, m.E.value / 1e9, round(m.E_at(T) / 1e9, 2),
                        m.Fty.value / 1e6, round(m.Fty_at(T) / 1e6, 1), m.Tmax.value, ok[m.key],
                        round(rel[("beam_strong", m.key, 20.0)], 3), round(rel[("beam_strong", m.key, T)], 3),
                        round(rel[("beam_stiff", m.key, T)], 3), round(rel[("tie_strong", m.key, T)], 3),
                        m.co2.value, m.price.value if m.price else "NOT FOUND", round(rel_co2[m.key], 3),
                        m.k_source, m.k_tag])
    # ---------------- cards
    cards.write_matml(OUT / "materials_engineering_data.xml", mats, T)
    for m in mats:
        (OUT / f"card_{m.key}.md").write_text(cards.markdown_card(m, T), encoding="utf-8")
    # ---------------- figure (datawiz)
    fig_note = figure(mats, rel, ok, T)
    # ---------------- markdown
    order = sorted(mats, key=lambda m: (not ok[m.key], rel[("beam_strong", m.key, T)]))
    s = f"# Material selection — aircraft bracket at {T:g} °C\n\n"
    s += ("`python 01_Ansys/scripts/bracket_material_report.py` [K]. Candidates and every value with its source and tag: "
          "`aerokit.bracket.matdata` and the cards in this folder. Relative mass = mass of the part in that material / "
          "mass in the best material for the same load and stiffness or strength target (Ashby index; "
          "`aerokit.materials.selection`). The geometry-specific answer (real layouts, real stresses) is in each "
          "`outputs/cases/<case>/report.md`; this table is the screening step before it.\n\n")
    s += f"## Screen: maximum service temperature ≥ {T:g} °C\n\n"
    s += "".join(f"- {m.name}: Tmax {m.Tmax.value:g} °C [{m.Tmax.tag}] → **{'passes' if ok[m.key] else 'fails'}**\n"
                 for m in mats)
    s += (f"\n## Comparison at {T:g} °C (relative mass, 1 = lightest)\n\n| Material | ρ (kg/m³) | E (GPa) | "
          f"Fty (MPa) | Strong beam | Stiff beam | CO₂ (kg/kg) |\n|---|---|---|---|---|---|---|\n")
    for m in order:
        s += (f"| {m.name}{'' if ok[m.key] else ' (fails screen)'} | {m.rho.value:g} | {m.E_at(T) / 1e9:.1f} | "
              f"{m.Fty_at(T) / 1e6:.0f} | {rel[('beam_strong', m.key, T)]:.2f} | {rel[('beam_stiff', m.key, T)]:.2f} | "
              f"{m.co2.value:g} |\n")
    s += "\n## Effect of temperature on the strength-limited ranking\n\n| Material | Rel. mass 20 °C | Rel. mass " \
         f"{T:g} °C | Fty factor | Factor source |\n|---|---|---|---|---|\n"
    for m in order:
        s += (f"| {m.name} | {rel[('beam_strong', m.key, 20.0)]:.2f} | {rel[('beam_strong', m.key, T)]:.2f} | "
              f"{m.Fty_at(T) / m.Fty.value:.3f} | {m.k_source} [{m.k_tag}] |\n")
    best = next(m for m in order if ok[m.key] and m.am)
    s += (f"\n## Recommendation (screening level)\n\n**{best.name}** gives the lightest strength-limited bracket among "
          f"the 3-D printable candidates that pass the {T:g} °C screen (relative mass "
          f"{rel[('beam_strong', best.key, T)]:.2f}). Three materials for the comparison table: the baseline "
          "Structural Steel, the lightest printable (above) and the next printable alternative — "
          + ", ".join(m.name for m in order if ok[m.key] and m.am and m.key != best.key) +
          ". Least embodied CO₂ per strength (beam, cradle to gate): "
          + min(mats, key=lambda m: rel_co2[m.key] if ok[m.key] else 1e9).name +
          " — the use phase (fuel) still dominates the life total, see the eco audits.\n")
    s += ("\nPrice (stock or powder, EUR/kg): " + "; ".join(
        f"{m.name.split(' (')[0]} {m.price.value:g} [{m.price.tag}]" if m.price else f"{m.name.split(' (')[0]} NOT FOUND"
        for m in mats) + ". Sources in the cards; AM machine time and post-processing are not included.\n")
    s += f"\nFigure: `fig_relative_mass.png` — {fig_note}\n"
    s += ("\nFiles: `comparison.csv` (all columns), `materials_engineering_data.xml` (Ansys Engineering Data import), "
          "`card_*.md` (one card per material).\n")
    (OUT / "material_selection.md").write_text(s, encoding="utf-8")
    sys.stdout.buffer.write(s.encode("utf-8"))
    return 0


def figure(mats: list, rel: dict, ok: dict, T: float) -> str:
    """FİGÜR BRİFİ: "At 300 °C the strength-limited ranking changes; Ti-6Al-4V stays lightest" — Cleveland dot plot,
    relative mass (x, positions so no zero baseline needed), one row per material, grey = 20 °C, accent = T,
    hedef genel-tek, tema akademik."""
    import matplotlib
    matplotlib.use("Agg")
    import datawiz as dw
    import numpy as np
    S = dw.Seti(str(OUT / "material.seti.json"), hedef="genel-tek")
    S.nicelik("relm", f"Mass relative to the best at {T:g} °C", None, eksen="x")
    S.varlik("20 °C", baglam=True)
    S.varlik(f"{T:g} °C")
    from aerokit.materials.selection import performance_index
    idx = {(m.key, t): performance_index({"Fty": m.Fty_at(t), "rho": m.rho.value}, "beam_strong")
           for m in mats for t in (20.0, T)}
    ref = max(idx[(m.key, T)] for m in mats if ok[m.key])          # best material that passes, at T
    order = sorted(mats, key=lambda m: ref / idx[(m.key, T)], reverse=True)
    y = np.arange(len(order))
    fig, ax = S.figur(genislik="tek", oran=0.6)
    a20 = [ref / idx[(m.key, 20.0)] for m in order]
    aT = [ref / idx[(m.key, T)] for m in order]
    ax.scatter(a20, y + 0.12, **S.stil("20 °C", tur="sacilim"))
    ax.scatter(aT, y - 0.12, **S.stil(f"{T:g} °C", tur="sacilim"))
    ax.set_xlim(0.9 * min(a20 + aT), 1.05 * max(a20 + aT))
    ax.set_yticks(y, [m.name.split(" (")[0] + ("" if ok[m.key] else " (fails)") for m in order])
    S.eksen(ax, x="relm")
    ax.set_ylabel("Material")
    dw.lejant.yerlestir(ax)
    r = S.kaydet(fig, str(OUT / "fig_relative_mass"), cvd=True, kati=True, sessiz=True)
    return (f"mass of a strength-limited bracket arm (index Fty^2/3/ρ) relative to the best passing material at "
            f"{T:g} °C, at 20 °C and at {T:g} °C; '(fails)' = fails the "
            f"{T:g} °C screen; audit {r.get('hata', 0)} HATA")


if __name__ == "__main__":
    raise SystemExit(main())
