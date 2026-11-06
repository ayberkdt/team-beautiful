"""Figures of the Beetiful light-weighting report (datawiz set, A4 two-column width).

    python prev_guess/01_Ansys/scripts/report_figures.py            # reads prev_guess/01_Ansys/tradeoff/out/*.results.json, writes prev_guess/01_Ansys/reports/figures/
    python prev_guess/01_Ansys/scripts/report_figures.py --lang en  # English labels, writes prev_guess/01_Ansys/reports/figures_en/

F1 life-cycle CO2 by phase · F2 mass vs life-cycle CO2 (strength | stiffness) · F3 tornado · F4 buy-to-fly break-even.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

import datawiz as dw  # noqa: E402

from aerokit.design import tradeoff as T  # noqa: E402

LANG = "en" if "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en" else "tr"
OUT = ROOT / "prev_guess" / "01_Ansys" / "reports" / ("figures_en" if LANG == "en" else "figures")
STUDIES = ROOT / "prev_guess" / "01_Ansys" / "tradeoff"
OPTIONS = [("7075-T6", "machined"), ("7075-T6", "machined_TO"), ("2024-T351", "machined_TO"),
           ("Ti-6Al-4V", "machined_TO"), ("Ti-6Al-4V", "am_TO"), ("AlSi10Mg", "am_TO"), ("Scalmalloy", "am_TO")]
ROUTE_TR = {"machined": "talaşlı", "machined_TO": "TO + talaşlı", "am_TO": "TO + Eİ"}
FACTOR_TR = {
    "reference_mass": "Referans parça kütlesi",
    "lifecycle.fuel_per_kg_per_flight": "Uçuş başına marjinal yakıt",
    "lifecycle.flights": "Ömür boyu uçuş sayısı",
    "lifecycle.grid_co2_per_MJ": "Şebeke CO₂ yoğunluğu",
    "routes.am_TO.mass_factor": "Eİ kütle katsayısı",
    "routes.machined_TO.mass_factor": "TO + talaşlı kütle katsayısı",
    "routes.machined.buy_to_fly": "Talaşlı buy-to-fly",
    "routes.machined_TO.buy_to_fly": "TO + talaşlı buy-to-fly",
    "routes.am_TO.buy_to_fly": "Eİ buy-to-fly",
    "routes.machined.process_MJ_per_kg": "Talaşlı süreç enerjisi",
    "routes.machined_TO.process_MJ_per_kg": "TO + talaşlı süreç enerjisi",
    "routes.am_TO.process_MJ_per_kg": "Eİ süreç enerjisi",
}
FACTOR_EN = {
    "reference_mass": "Reference part mass",
    "lifecycle.fuel_per_kg_per_flight": "Marginal fuel per flight",
    "lifecycle.flights": "Lifetime flights",
    "lifecycle.grid_co2_per_MJ": "Grid CO₂ intensity",
    "routes.am_TO.mass_factor": "AM mass factor",
    "routes.machined_TO.mass_factor": "TO + machined mass factor",
    "routes.machined.buy_to_fly": "Machined buy-to-fly",
    "routes.machined_TO.buy_to_fly": "TO + machined buy-to-fly",
    "routes.am_TO.buy_to_fly": "AM buy-to-fly",
    "routes.machined.process_MJ_per_kg": "Machining process energy",
    "routes.machined_TO.process_MJ_per_kg": "TO + machined process energy",
    "routes.am_TO.process_MJ_per_kg": "AM process energy",
}
ROUTE_EN = {"machined": "machined", "machined_TO": "TO + machined", "am_TO": "TO + AM"}
TXT = {
    "tr": {"co2": "Ömür boyu CO₂", "kutle": "Parça kütlesi", "fark": "Kazanan ile ikinci arasındaki CO₂ farkı",
           "btf": "Buy-to-fly oranı", "uretim": "Üretim CO₂ / bitmiş parça kütlesi", "prod": "Üretim",
           "use": "Kullanım (yakıt)", "share": "{t} t · üretim %{p}", "strength": "Dayanım sınırlı",
           "stiffness": "Rijitlik sınırlı", "pbest": "P(en iyi) = ", "flip": "seçim tersine döner",
           "low": "girdi alt ucunda", "high": "üst ucunda", "ti_am": "Ti-6Al-4V TO + Eİ: {v} kg CO₂/kg",
           "cross": "kırılma ≈ {v}", "embodied": "{m} gömülü CO₂", "dec": ","},
    "en": {"co2": "Life-cycle CO₂", "kutle": "Part mass", "fark": "CO₂ gap between winner and runner-up",
           "btf": "Buy-to-fly ratio", "uretim": "Production CO₂ / finished part mass", "prod": "Production",
           "use": "Use (fuel)", "share": "{t} t · production {p} %", "strength": "Strength-limited",
           "stiffness": "Stiffness-limited", "pbest": "P(best) = ", "flip": "choice reverses",
           "low": "input at low end", "high": "at high end", "ti_am": "Ti-6Al-4V TO + AM: {v} kg CO₂/kg",
           "cross": "break-even ≈ {v}", "embodied": "{m} embodied CO₂", "dec": "."},
}[LANG]
PT = 8  # smallest text in the figures [pt]


def tr(x: float, nd: int = 1) -> str:
    """Number with the report language's decimal mark."""
    return f"{x:.{nd}f}".replace(".", TXT["dec"])


def label(material: str, route: str) -> str:
    short = {"7075-T6": "7075", "2024-T351": "2024"}.get(material, material)
    return f"{short} {(ROUTE_EN if LANG == 'en' else ROUTE_TR).get(route, route)}"


def factor_tr(path: str) -> str:
    names = FACTOR_EN if LANG == "en" else FACTOR_TR
    if path in names:
        return names[path]
    if path.startswith("materials.") and path.endswith(".co2_per_kg"):
        return TXT["embodied"].format(m=path.split(".")[1])
    return path


def load(stem: str) -> dict:
    return json.loads((STUDIES / "out" / f"{stem}.results.json").read_text(encoding="utf-8"))


def setup() -> dw.Seti:
    S = dw.Seti(str(OUT / "rapor.seti.json"), hedef="genel-cift", palet="okabe-ito", ondalik_ayirici=TXT["dec"])
    S.nicelik("co2", TXT["co2"], "t", eksen="x")
    S.nicelik("kutle", TXT["kutle"], "kg", eksen="y")
    S.nicelik("fark", TXT["fark"], "t", eksen="x")
    S.nicelik("btf", TXT["btf"], "–", eksen="x")
    S.nicelik("uretim", TXT["uretim"], "kg/kg", eksen="y")
    for m, r in OPTIONS:
        S.varlik(label(m, r))
    return S


def fig1_phases(S: dw.Seti, res: dict) -> None:
    rows = sorted(res["nominal"], key=lambda r: r["co2_total_kg"])
    cats = [label(r["material"], r["route"]) for r in rows]
    series = {TXT["prod"]: [r["co2_production_kg"] / 1000 for r in rows],
              TXT["use"]: [r["co2_use_kg"] / 1000 for r in rows]}
    fig, ax = S.figur(oran=0.42)
    dw.ciz.yigin_cubuk(ax, cats, series, tur="nitel", yatay=True, deger_yaz=False)
    S.eksen(ax, x="co2")
    for i, r in enumerate(rows):
        share = 100 * r["co2_production_kg"] / r["co2_total_kg"]
        ax.annotate(TXT["share"].format(t=tr(r["co2_total_kg"] / 1000), p=tr(share)), (r["co2_total_kg"] / 1000, i),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=PT, color="#4d4d4d")
    ax.set_xlim(0, max(r["co2_total_kg"] for r in rows) / 1000 * 1.5)
    S.kaydet(fig, str(OUT / "F1_evre_paylari"), cvd=True)


def fig2_plane(S: dw.Seti, strength: dict, stiffness: dict) -> None:
    fig, axs = S.figur(oran=0.5, ncols=2, sharey=True, sharex=True)
    for ax, res, title in ((axs[0], strength, TXT["strength"]), (axs[1], stiffness, TXT["stiffness"])):
        q, pb = res["monte_carlo"]["quantiles"], res["monte_carlo"]["p_best"]
        notes: dict[tuple, list] = {}
        for r in res["nominal"]:
            key = f"{r['material']} / {r['route']}"
            name = label(r["material"], r["route"])
            st = S.stil(name, tur="hata")
            m, c = q[key]["mass_kg"], q[key]["co2_total_kg"]
            ax.errorbar(c["p50"] / 1000, m["p50"],
                        xerr=[[(c["p50"] - c["p05"]) / 1000], [(c["p95"] - c["p50"]) / 1000]],
                        yerr=[[m["p50"] - m["p05"]], [m["p95"] - m["p50"]]],
                        fmt=st["marker"], color=st["color"], ms=5, lw=1, capsize=0, label=name)
            if pb[key] >= 0.05:
                x, y = c["p50"] / 1000, m["p50"]
                near = next((k for k in notes if abs(k[0] - x) < 0.6 and abs(k[1] - y) < 0.03), (x, y))
                notes.setdefault(near, []).append((name.split(" ")[0], pb[key]))
        for (x, y), items in notes.items():
            text = TXT["pbest"] + " · ".join(f"{n} {tr(p, 2)}" for n, p in items)
            dw.notlar.ok(ax, (x, y), text, nokta=False)
        ax.set_title(title, loc="left")
        S.eksen(ax, x="co2", y="kutle")
    axs[0].set_ylim(0.45, 1.4)  # room above the data for the legend in panel (b); y axis is shared
    handles, names = axs[0].get_legend_handles_labels()
    dw.lejant.yerlestir(axs[1], handles, names, yer="ic", ncols=2)
    S.panel_harfleri(axs)
    S.kaydet(fig, str(OUT / "F2_kutle_co2"), cvd=True)


def fig3_tornado(S: dw.Seti, res: dict, top: int = 8) -> None:
    rows = res["tornado"][:top][::-1]
    nominal = [r["score"] for r in res["nominal"]]
    base = (nominal[1] - nominal[0]) / 1000
    fig, ax = S.figur(oran=0.45)
    y = np.arange(len(rows))
    c_lo, c_hi = dw.paletler.kategorik()[:2]
    for key, col in (("margin_low", c_lo), ("margin_high", c_hi)):
        v = np.array([r[key] / 1000 for r in rows])
        ax.barh(y, v - base, left=base, color=dw.renk.alan_tonu(col), edgecolor=col, height=0.6)
    ax.axvline(base, color="#4d4d4d", lw=0.8)
    dw.notlar.referans(ax, x=0, metin=TXT["flip"])
    ax.set_yticks(y, [f"{factor_tr(r['factor'])} [{r['tag']}]" for r in rows])
    S.eksen(ax, x="fark")
    top_row = rows[-1]
    dw.notlar.ok(ax, (top_row["margin_low"] / 1000, len(rows) - 1), TXT["low"])
    dw.notlar.ok(ax, (top_row["margin_high"] / 1000, len(rows) - 1), TXT["high"])
    S.kaydet(fig, str(OUT / "F3_tornado"), cvd=True)


def fig4_btf(S: dw.Seti, study: T.Study) -> None:
    g = study.lifecycle["grid_co2_per_MJ"].value
    mach = study.routes["machined"]["process_MJ_per_kg"].value
    am = study.routes["am_TO"]
    btf = np.linspace(1, 26, 200)
    al = study.materials["7075-T6"]["co2_per_kg"].value
    ti = study.materials["Ti-6Al-4V"]["co2_per_kg"].value
    fig, ax = S.figur(oran=0.42)
    dw.ciz.cizgiler(ax, btf, {label("7075-T6", "machined"): btf * (al + mach * g),
                              label("Ti-6Al-4V", "machined_TO"): btf * (ti + mach * g)},
                    renkler=[S.renk(label("7075-T6", "machined")), S.renk(label("Ti-6Al-4V", "machined_TO"))])
    ti_am = am["buy_to_fly"].value * (ti + am["process_MJ_per_kg"].value * g)
    ax.plot([am["buy_to_fly"].value], [ti_am], marker="D", ms=6, color=S.renk(label("Ti-6Al-4V", "am_TO")), lw=0)
    cross = ti_am / (al + mach * g)
    dw.notlar.referans(ax, y=ti_am, metin=TXT["ti_am"].format(v=f"{ti_am:.0f}"))
    dw.notlar.ok(ax, (cross, ti_am), TXT["cross"].format(v=tr(cross)))
    S.eksen(ax, x="btf", y="uretim")
    ax.set_xlim(0, 26)
    ax.set_ylim(0, None)
    S.kaydet(fig, str(OUT / "F4_btf_kirilma"), cvd=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    S = setup()
    strength, stiffness = load("bracket_a320_strength"), load("bracket_a320_stiffness")
    for _ in range(2):  # second pass with a common plot-area margin measured from the first
        fig1_phases(S, strength)
        fig2_plane(S, strength, stiffness)
        fig3_tornado(S, strength)
        fig4_btf(S, T.load_study(STUDIES / "bracket_a320_strength.json"))
        if S.d.get("kenar_mm"):
            break
        S.kenar(*S.kenar_oner())
    S.denetle()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
