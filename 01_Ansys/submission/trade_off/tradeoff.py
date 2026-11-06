"""Trade-off numbers and figures for the Ansys bracket report (S275N vs Al 2618-T6 vs Ti-8Al-1Mo-1V).

Data: the organisers' Granta EduPack selection report, as transcribed in
official_2026-11-05/analysis/organiser_materials.py (machine-checked against the PDF by verify_organiser_values.py:
0 mismatches, re-run 5 Nov 2026) and its eco model (reproduces the organisers' initial-design eco audit).
300 °C knock-down factors: official_2026-11-05/analysis/material_swap.py (Fty: EN 1993-1-2 steel 0.78, MIL-HDBK-5J
Ti-8-1-1 0.683), evaluate_layouts.py (Ti E 0.869), material_decision.md (steel E 0.80) — sources as cited there,
not re-read here.

Figures (springer-cift, 174 mm, datawiz set tradeoff.seti.json):
  fig_tradeoff_table      card requirements and objectives, three candidates
  fig_tradeoff_indices    Ashby performance indices at 300 °C → Ti life CO₂ relative to S275N, four loading modes
  fig_tradeoff_breakeven  (a) life CO₂ vs part volume with the equal-CO₂ read-out; (b) Ti design points vs the
                          initial steel part (mass, life CO₂, material cost)

Run (from the project root):
  python -I 01_Ansys/submission/trade_off/tradeoff.py [--ti-volume-pct 45]
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parents[1] / "official_2026-11-05" / "analysis"
sys.path.insert(0, str(ANALYSIS))
from organiser_materials import M, eco, gm  # noqa: E402  (single source of the organisers' data)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
from matplotlib.patches import FancyBboxPatch  # noqa: E402
import matplotlib.text  # noqa: E402
import matplotlib.ticker  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
import numpy as np  # noqa: E402
import datawiz as dw  # noqa: E402

KEYS = ["S275N", "Al2618T6", "Ti811SA"]
SHORT = {"S275N": "S275N", "Al2618T6": "Al 2618-T6", "Ti811SA": "Ti-8Al-1Mo-1V"}
V0 = 0.019400            # m³, initial design volume (setup/boundary_conditions.md §1: 152.29 kg at 7850 kg/m³)
M0_STEEL = 152.27        # kg, organisers' mass monitor for the S275N initial design
FOS = 1.5
K300 = {"S275N": (0.78, 0.80), "Al2618T6": (None, None), "Ti811SA": (0.683, 0.869)}   # (Fty, E) factors at 300 °C
# colours: datawiz theme "derin" (dw.paletler.tema("derin")): navy #25458f, amber #bb7b21, petrol #077b7c, crimson #aa2d37
INK, GREY, RULE, GRID = "#222222", "#5a5a5a", "#c8c8c8", "#e4e4e4"
TI, AL, STEEL, STEEL_DARK = "#25458f", "#bb7b21", "#8c8c8c", "#5f5f5f"
TI_FILL = "#d3dbee"                       # light tone of the Ti navy for wide fills
PASS_C, FAIL_C, AL_TEXT = "#077b7c", "#aa2d37", "#8a5a14"   # AL_TEXT: amber darkened to >= 4.5:1 for text


def numbers(ti_vol_pct: float) -> dict:
    out = {"V0_m3": V0, "fos": FOS, "materials": {}}
    for k in KEYS:
        m = M[k]
        e1 = eco(1.0, k)                                  # per kg of part, organisers' formulas
        kF, kE = K300[k]
        out["materials"][k] = {
            "rho": gm(m["rho"]), "price_usd_per_kg": gm(m["price"]), "price_range": m["price"],
            "co2_life_per_kg": e1["total_first_life"], "co2_production_per_kg": e1["material"] + e1["manufacture"],
            "co2_use_per_kg": e1["use"], "mass_at_V0_kg": gm(m["rho"]) * V0,
            "allow_300C_MPa": (m["Fy"][0] * kF / FOS) if kF else None,
            "E_300C_GPa": (gm(m["E"]) * kE) if kE else None,
        }
    S, T = out["materials"]["S275N"], out["materials"]["Ti811SA"]
    co2_base = eco(M0_STEEL, "S275N")["total_first_life"]
    cost_base = M0_STEEL * S["price_usd_per_kg"]
    out["initial_steel"] = {"mass_kg": M0_STEEL, "co2_life_kg": co2_base, "cost_usd": cost_base}
    out["ti_same_shape"] = {"volume_pct": 100.0, "mass_kg": T["mass_at_V0_kg"],
                            "co2_life_kg": T["mass_at_V0_kg"] * T["co2_life_per_kg"],
                            "cost_usd": T["mass_at_V0_kg"] * T["price_usd_per_kg"]}
    m_tie = co2_base / T["co2_life_per_kg"]
    out["ti_tie_with_initial_steel"] = {"mass_kg": m_tie, "volume_pct": 100 * m_tie / T["rho"] / V0}
    out["steel_volume_to_tie_ti_ratio"] = (T["rho"] * T["co2_life_per_kg"]) / (S["rho"] * S["co2_life_per_kg"])
    out["life_co2_per_kg_ratio_ti_over_steel"] = T["co2_life_per_kg"] / S["co2_life_per_kg"]
    out["use_share_steel"] = S["co2_use_per_kg"] / S["co2_life_per_kg"]
    out["use_share_ti"] = T["co2_use_per_kg"] / T["co2_life_per_kg"]
    # Ashby indices (Ashby, Materials Selection in Mechanical Design): mass ∝ ρ / P^n for a member of fixed length
    # and load; life CO₂ ∝ c_life · mass. P = allowable stress or E at 300 °C.
    modes = [("Tie (axial), strength-limited", "allow_300C_MPa", 1.0),
             ("Tie (axial), stiffness-limited", "E_300C_GPa", 1.0),
             ("Beam (bending), strength-limited", "allow_300C_MPa", 2 / 3),
             ("Beam (bending), stiffness-limited", "E_300C_GPa", 1 / 2)]
    out["indices"] = []
    for name, prop, ex in modes:
        mass_ratio = (T["rho"] / T[prop] ** ex) / (S["rho"] / S[prop] ** ex)
        out["indices"].append({"mode": name, "property": prop, "exponent": ex, "mass_ratio_ti_over_steel": mass_ratio,
                               "co2_ratio_ti_over_steel": mass_ratio * out["life_co2_per_kg_ratio_ti_over_steel"],
                               "cost_ratio_ti_over_steel": mass_ratio * T["price_usd_per_kg"] / S["price_usd_per_kg"]})
    f = ti_vol_pct / 100
    mt = T["rho"] * V0 * f
    co2_t, cost_t = mt * T["co2_life_per_kg"], mt * T["price_usd_per_kg"]
    out["example"] = {"ti_volume_pct": ti_vol_pct, "ti_mass_kg": mt, "ti_co2_life_kg": co2_t, "ti_cost_usd": cost_t,
                      "steel_volume_pct_same_co2": ti_vol_pct * out["steel_volume_to_tie_ti_ratio"],
                      "steel_mass_same_co2_kg": co2_t / S["co2_life_per_kg"],
                      "co2_saving_vs_initial_kg": co2_base - co2_t,
                      "co2_saving_vs_initial_pct": 100 * (1 - co2_t / co2_base),
                      "extra_cost_vs_initial_usd": cost_t - cost_base,
                      "usd_per_t_co2_avoided": (cost_t - cost_base) / ((co2_base - co2_t) / 1000)}
    return out


# ---------------------------------------------------------------------------------------------------- table
def fig_table(S, n):
    m = n["materials"]
    PASS, FAIL, INFO = "pass", "fail", None
    rows = [  # (criterion, unit · source, cells per material in KEYS order); None row = group rule
        ("Max. service temperature > 300 °C", "°C · p.9", [("471–501", PASS), ("250–300", FAIL), ("407–455", PASS)]),
        ("Castable or 3-D printable", "stage 2 · p.5", [("yes", PASS), ("yes", PASS), ("yes", PASS)]),
        ("Fracture toughness ≥ 10", "MPa·m½ · p.9", [("26–38", PASS), ("31–34", PASS), ("65–75", PASS)]),
        None,
        ("Allowable stress at 300 °C", "MPa · σy/1.5",
         [(f"{m['S275N']['allow_300C_MPa']:.0f}", INFO), ("no data", FAIL), (f"{m['Ti811SA']['allow_300C_MPa']:.0f}", INFO)]),
        ("Young's modulus at 23 °C", "GPa · p.8", [("200–221", INFO), ("72–76", INFO), ("121–127", INFO)]),
        ("Density", "kg/m³ · p.8", [("7800–7900", INFO), ("2720–2780", INFO), ("4350–4400", INFO)]),
        None,
        ("Price", "USD/kg · p.8", [("1.0–1.6", INFO), ("3.1–3.5", INFO), ("23–26", INFO)]),
        ("Production CO₂ (virgin + powder)", "kg/kg · p.11–12",
         [(f"{m[k]['co2_production_per_kg']:.0f}", INFO) for k in KEYS]),
        ("Life-cycle CO₂ per kg of part", "kg/kg · card",
         [(f"{m[k]['co2_life_per_kg']:.0f}", INFO) for k in KEYS]),
        None,
        ("Oxidation at 500 °C", "p.11", [("acceptable", INFO), ("unacceptable", FAIL), ("acceptable", INFO)]),
        ("Stress-corrosion cracking", "p.11", [("slight", INFO), ("high", FAIL), ("slight", INFO)]),
        ("Sourcing risk", "p.10", [("low", INFO), ("very high", FAIL), ("medium", INFO)]),
    ]
    n_lines = sum(1 for r in rows if r) + 2                       # + header + verdict
    row_h = 5.6                                                   # mm per row (≈ 1.75 × 9 pt line)
    fig, ax = S.figur(genislik="cift", yukseklik_mm=row_h * n_lines + 4)
    ax.set_axis_off()
    ax.set_position([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 1)
    ax.set_ylim(n_lines + 0.15, -0.75)
    x_crit, x_unit = 0.0, 0.33
    x_cols, w_col = [0.595, 0.75, 0.905], 0.15
    hdr_color = {"S275N": INK, "Al2618T6": AL_TEXT, "Ti811SA": TI}
    ax.text(x_crit, 0, "Criterion", ha="left", va="center", fontweight="bold", color=INK)
    ax.text(x_unit, 0, "Unit · source", ha="left", va="center", fontweight="bold", color=INK)
    for xc, k in zip(x_cols, KEYS):
        ax.text(xc, 0, SHORT[k], ha="center", va="center", fontweight="bold", color=hdr_color[k])
    ax.plot([0, 1], [0.55, 0.55], color=INK, lw=0.9, solid_capstyle="butt")
    y = 1
    for r in rows:
        if r is None:
            ax.plot([0, 1], [y - 0.5, y - 0.5], color=RULE, lw=0.5)
            continue
        crit, unit, cells = r
        ax.text(x_crit, y, crit, ha="left", va="center", color=INK)
        ax.text(x_unit, y, unit, ha="left", va="center", color=GREY)
        for xc, (txt, st) in zip(x_cols, cells):
            # status: shape + colour (double coded); pass = green dot, fail = vermillion cross + vermillion text.
            # The marker sits just left of the MEASURED text edge, so it stays attached to its value.
            t = ax.text(xc, y, txt, ha="center", va="center",
                        color=FAIL_C if st == FAIL else INK, fontweight="bold" if st == FAIL else "normal")
            if st:
                bb = t.get_window_extent(fig.canvas.get_renderer()).transformed(ax.transData.inverted())
                ax.plot([bb.x0 - 0.014], [y], marker="o" if st == PASS else "X", ms=4.0 if st == PASS else 4.6,
                        mfc=PASS_C if st == PASS else FAIL_C, mec="none", zorder=2)
        y += 1
    ax.plot([0, 1], [y - 0.5, y - 0.5], color=INK, lw=0.9)
    ax.text(x_crit, y, "Verdict", ha="left", va="center", fontweight="bold", color=INK)
    for xc, k, v in zip(x_cols, KEYS, ["Reference", "Eliminated", "Selected"]):
        ax.text(xc, y, v, ha="center", va="center", fontweight="bold", color=hdr_color[k])
    ax.plot([0, 1], [y + 0.55, y + 0.55], color=INK, lw=0.9)
    return fig


# ---------------------------------------------------------------------------------------------------- indices
def _grid(ax, axis):
    """Light, sparse major grid perpendicular to the read-off direction (datawiz E11; HeerBostock2010)."""
    ax.grid(False)
    ax.grid(True, axis=axis, which="major", color=GRID, lw=0.6, zorder=0)
    ax.grid(False, which="minor")
    ax.set_axisbelow(True)


def fig_indices(S, n):
    idx = n["indices"]
    fig, ax = S.figur(genislik="cift", yukseklik_mm=56)
    ys = np.arange(len(idx))[::-1]
    vals = [100 * d["co2_ratio_ti_over_steel"] for d in idx]
    ax.barh(ys, vals, height=0.58, color=TI_FILL, edgecolor=TI, linewidth=0.9, zorder=2)
    for yy, v in zip(ys, vals):
        ax.text(max(v, 100) + 2.5, yy, f"{v:.0f} %  ({v - 100:+.0f} %)".replace("-", "−"), va="center", ha="left",
                color=INK)
    ax.set_yticks(ys)
    ax.set_yticklabels([d["mode"] for d in idx])
    S.eksen(ax, x="rel_co2")
    ax.set_xticks(np.arange(0, 121, 20))
    ax.set_xlim(0, 135)
    ax.set_ylim(-0.6, len(idx) - 0.4)
    ax.axvline(100, color=STEEL_DARK, lw=1.0, ls=(0, (4, 2)), zorder=3)
    ax.text(100, len(idx) - 0.35, "S275N = 100 %", ha="center", va="bottom", color=STEEL_DARK, clip_on=False)
    ax.set_ylabel("Governing loading mode")
    _grid(ax, "x")
    return fig


# ---------------------------------------------------------------------------------------------------- break-even
def fig_breakeven(S, n):
    mats = n["materials"]
    vol = np.linspace(0, 120, 241)
    fig, (a, b) = S.figur(genislik="cift", oran=0.46, ncols=2)
    for k in KEYS:
        mass = mats[k]["rho"] * V0 * vol / 100
        a.plot(vol, mass * mats[k]["co2_life_per_kg"] / 1000, **S.stil(SHORT[k]))
    S.eksen(a, x="vol", y="co2")
    a.set_xticks(np.arange(0, 121, 20))
    a.set_yticks(np.arange(0, 71, 10))
    _grid(a, "both")
    base, ex = n["initial_steel"], n["example"]
    yb = base["co2_life_kg"] / 1000
    a.axhline(yb, color=STEEL_DARK, lw=0.9, ls=(0, (4, 2)), zorder=2)
    a.text(3, yb + 1.2, f"Initial S275N part: {yb:.1f} t", ha="left", va="bottom", color=STEEL_DARK)
    yt, xs, xt = ex["ti_co2_life_kg"] / 1000, ex["steel_volume_pct_same_co2"], ex["ti_volume_pct"]
    a.plot([xs, xt], [yt, yt], color=STEEL_DARK, lw=0.8, ls=":", zorder=3)
    a.plot([xs, xs], [0, yt], color=STEEL_DARK, lw=0.8, ls=":", zorder=3)
    a.plot([xt, xt], [0, yt], color=STEEL_DARK, lw=0.8, ls=":", zorder=3)
    a.plot([xt], [yt], marker="o", color=TI, ms=4.8, zorder=5)
    a.plot([xs], [yt], marker="o", mfc="white", mec=STEEL_DARK, mew=1.1, ms=4.8, zorder=5)
    dw.notlar.ok(a, (xs, yt), f"Equal CO₂ ({yt:.1f} t):\nTi {xt:.0f} % ≡ steel {xs:.0f} %", nokta=False,
                 adaylar=[(0, 56), (0, 60), (0, 52), (4, 56)])
    dw.etiket.cizgi_sonu(a)

    # (b) Ti design points as a ratio to the initial steel part, log axis (½ and 2 are equally far from 1)
    same, rows = n["ti_same_shape"], ["Mass", "Life-cycle CO₂", "Material cost"]
    pts = {
        "same": [same["mass_kg"] / base["mass_kg"], same["co2_life_kg"] / base["co2_life_kg"],
                 same["cost_usd"] / base["cost_usd"]],
        "opt": [ex["ti_mass_kg"] / base["mass_kg"], ex["ti_co2_life_kg"] / base["co2_life_kg"],
                ex["ti_cost_usd"] / base["cost_usd"]],
    }
    styles = {"same": dict(marker="o", mfc="white", mec=TI, mew=1.3, ms=6.2, ls="none"),
              "opt": dict(marker="o", color=TI, ms=6.2, ls="none")}
    ys = np.arange(len(rows))[::-1].astype(float)
    b.axvline(1.0, color=STEEL_DARK, lw=1.0, ls=(0, (4, 2)), zorder=1)
    b.text(1.07, len(rows) - 0.42, "Initial S275N = 1×", ha="left", va="bottom", color=STEEL_DARK)
    for key, off in (("same", 0.14), ("opt", -0.14)):
        for yy, r in zip(ys, pts[key]):
            b.plot([1.0, r], [yy + off, yy + off], color=TI_FILL, lw=2.4, zorder=2, solid_capstyle="round")
            b.plot([r], [yy + off], zorder=4, **styles[key])
            lab = f"{r:.2f}×" if r < 1 else f"{r:.1f}×"
            b.text(r * (1.16 if r > 1 else 1 / 1.16), yy + off, lab, ha="left" if r > 1 else "right", va="center",
                   color=INK)
    b.set_xscale("log")
    S.eksen(b, x="rel")                                   # first: the set applies its own locator/formatter
    b.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.25, 0.5, 1, 2, 5, 10]))
    b.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}×"))
    b.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    b.set_xlim(0.08, 16)
    b.set_yticks(ys)
    b.set_yticklabels(rows)
    b.set_ylim(-0.6, len(rows) - 0.1)
    b.spines["left"].set_visible(False)            # categorical rows: the 0.1× gridline bounds the panel
    b.tick_params(axis="y", length=0)
    _grid(b, "x")
    # marker key in the empty region right of 1× on the Mass row (both mass values are < 1)
    for yk, key, lab in ((ys[0] + 0.14, "same", "same shape"), (ys[0] - 0.14, "opt", f"optimised, {xt:.0f} % vol.")):
        b.plot([1.6], [yk], zorder=4, **styles[key])
        b.text(1.6 * 1.16, yk, lab, va="center", ha="left", color=INK)
    S.panel_harfleri([a, b])
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ti-volume-pct", type=float, default=45.0,
                    help="worked example: Ti part volume as %% of the initial design (45 = v2 candidate, provisional)")
    args = ap.parse_args()
    n = numbers(args.ti_volume_pct)
    (HERE / "tradeoff_numbers.json").write_text(json.dumps(n, indent=1, ensure_ascii=False), encoding="utf-8")
    seti = HERE / "tradeoff.seti.json"
    if seti.exists():                     # palette changed (okabe-ito → derin): rebuild the set from scratch
        seti.unlink()
    S = dw.Seti(str(seti), hedef="springer-cift", palet="derin")
    S.varlik("S275N", renk=STEEL, cizgi="-", baglam=True)
    S.varlik("Al 2618-T6", renk=AL, cizgi="--")
    S.varlik("Ti-8Al-1Mo-1V", renk=TI, cizgi="-")
    S.nicelik("vol", "Part volume", "% of initial design", eksen="x", sinir=(0, 120))
    S.nicelik("co2", "Life-cycle CO₂-eq", "t", eksen="y", sinir=(0, 70))
    S.nicelik("rel_co2", "Ti life-cycle CO₂", "% of S275N", eksen="x")
    S.nicelik("rel", "Ratio to the initial S275N part", "×, log scale", eksen="x")
    res, texts = {}, {}
    for name, fn in (("fig_tradeoff_table", fig_table), ("fig_tradeoff_indices", fig_indices),
                     ("fig_tradeoff_breakeven", fig_breakeven)):
        fig = fn(S, n)
        res[name] = S.kaydet(fig, str(HERE / name), bicimler=("pdf", "png", "svg"), cvd=True)["rapor"]
        texts[name] = [t.get_text() for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip()]
    (HERE / "fig_texts.json").write_text(json.dumps(texts, indent=1, ensure_ascii=False), encoding="utf-8")
    for k, v in res.items():
        print(k, "→", v)
    m = n["materials"]
    print("life CO2 per kg: " + ", ".join(f"{SHORT[k]} {m[k]['co2_life_per_kg']:.1f}" for k in KEYS))
    print(f"Ti same shape: {n['ti_same_shape']['mass_kg']:.1f} kg; Ti ties initial steel at "
          f"{n['ti_tie_with_initial_steel']['volume_pct']:.0f} % volume; V_steel/V_Ti {n['steel_volume_to_tie_ti_ratio']:.3f}")


if __name__ == "__main__":
    main()
