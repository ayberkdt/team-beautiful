"""Independent re-check of every number in the trade-off figures and in TRADEOFF_SECTION.md.

It does NOT import the eco model used by tradeoff.py: life-cycle CO₂ is re-derived here from the card formulas and
the raw Granta ranges, the organisers' eco-audit phases are read from their PDF, and every figure label and every
number quoted in the section text is compared with the re-derived value.

python -I 01_Ansys/submission/trade_off/check_values.py   → check_values.txt, exit 1 on any mismatch
"""
import json
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
OFF = HERE.parents[1] / "official_2026-11-05"
lines, bad = [], 0


def ok(cond, msg):
    global bad
    lines.append(("ok  " if cond else "FAIL") + "  " + msg)
    bad += 0 if cond else 1


def close(a, b, rel=1e-9):
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-12)


# ---- raw organiser ranges (Granta selection report; machine-checked vs the PDF by verify_organiser_values.py)
R = json.loads((OFF / "analysis" / "organiser_materials.json").read_text(encoding="utf-8"))["materials"]
gm = lambda r: math.sqrt(r[0] * r[1])
KM = 4000 * 180 * 1                                   # card: 1 year x 180 days x 4000 km
USE = KM * 0.000468                                   # card: kg CO2 per kg of part
TRANS = 500 * 0.241 / 1000                            # card formula per tonne (report: 18.5 kg for 152 kg)
DISP = 7.45 / 152                                     # eco report p.2: 7.45 kg for 152 kg
life = {k: gm(R[k]["co2_virgin"]) + gm(R[k]["co2_powder"]) + TRANS + USE + DISP for k in R}
rho = {k: gm(R[k]["rho"]) for k in R}
price = {k: gm(R[k]["price"]) for k in R}

# ---- organisers' eco audit, page 2, read from the PDF now
import fitz  # noqa: E402
txt = fitz.open(OFF / "files" / "Eco assessment initial design report Ideathon challenge.pdf")[1].get_text()
tok = [t.strip() for t in txt.splitlines() if t.strip()]
def after(prefix, n):                                  # n-th number after the first row label starting with prefix
    i = next(j for j, t in enumerate(tok) if t == prefix or (prefix.endswith("(") and t.startswith(prefix)))
    nums = [t for t in tok[i + 1:] if re.fullmatch(r"-?[\d.]+(e[+-]\d+)?", t)]
    return float(nums[n])
# columns per row: Energy (MJ), Energy (%), CO2 (kg), CO2 (%) → index 2 = CO2 kg
org = {"material": after("Material", 2), "manufacture": after("Manufacture", 2), "transport": after("Transport", 2),
       "use": after("Use", 2), "disposal": after("Disposal", 2), "total": after("Total (", 2)}
lines.append(f"organisers' eco audit p.2 (152 kg S275N): {org}")
m152 = 152.0
mine = {"material": m152 * gm(R["S275N"]["co2_virgin"]), "manufacture": m152 * gm(R["S275N"]["co2_powder"]),
        "transport": m152 * TRANS, "use": m152 * USE, "disposal": m152 * DISP}
mine["total"] = sum(mine.values())
for k in org:
    d = 100 * (mine[k] - org[k]) / org[k]
    ok(abs(d) <= 1.5, f"eco phase {k:12s} ours {mine[k]:10.1f}  organisers {org[k]:10.1f}  ({d:+.2f} %)")

# ---- tradeoff_numbers.json against the independent derivation
N = json.loads((HERE / "tradeoff_numbers.json").read_text(encoding="utf-8"))
T, S = "Ti811SA", "S275N"
for k in R:
    ok(close(N["materials"][k]["co2_life_per_kg"], life[k]), f"life CO2/kg {k}: {life[k]:.3f}")
    ok(close(N["materials"][k]["rho"], rho[k]), f"density {k}: {rho[k]:.1f}")
V0, M0 = 0.019400, 152.27
base_co2, base_cost = M0 * life[S], M0 * price[S]
ok(close(N["initial_steel"]["co2_life_kg"], base_co2), f"initial steel life CO2 {base_co2 / 1e3:.2f} t")
ti_same = rho[T] * V0
ok(close(N["ti_same_shape"]["mass_kg"], ti_same), f"Ti same shape {ti_same:.1f} kg")
ratio = rho[T] * life[T] / (rho[S] * life[S])
ok(close(N["steel_volume_to_tie_ti_ratio"], ratio), f"V_steel/V_Ti at equal CO2 {ratio:.4f}")
tie = base_co2 / life[T] / rho[T] / V0 * 100
ok(close(N["ti_tie_with_initial_steel"]["volume_pct"], tie), f"Ti ties initial steel at {tie:.1f} % volume")
# 300 C properties: Fty factors EN 1993-1-2 Annex E Table E.1 (k_p0.2,300 = 0.78) and MIL-HDBK-5J Fig. 5.3.2.1.1
# (68.3 %); E factors EN 1993-1-2 Table 3.1 (k_E,300 = 0.800) and MIL-HDBK-5J Fig. 5.3.2.1.4 (86.9 %)
allow = {S: R[S]["Fy"][0] * 0.78 / 1.5, T: R[T]["Fy"][0] * 0.683 / 1.5}
E300 = {S: gm(R[S]["E"]) * 0.800, T: gm(R[T]["E"]) * 0.869}
for k in (S, T):
    ok(close(N["materials"][k]["allow_300C_MPa"], allow[k]), f"allowable 300 C {k}: {allow[k]:.1f} MPa")
    ok(close(N["materials"][k]["E_300C_GPa"], E300[k]), f"E 300 C {k}: {E300[k]:.1f} GPa")
idx = {}
for d in N["indices"]:
    P = allow if d["property"] == "allow_300C_MPa" else E300
    r = (rho[T] / P[T] ** d["exponent"]) / (rho[S] / P[S] ** d["exponent"]) * life[T] / life[S]
    idx[d["mode"]] = r
    ok(close(d["co2_ratio_ti_over_steel"], r), f"index {d['mode']}: CO2 ratio {r:.4f}")
ex = N["example"]
f = ex["ti_volume_pct"] / 100
mt, ct = rho[T] * V0 * f, rho[T] * V0 * f * life[T]
cost_t = mt * price[T]
ok(close(ex["ti_mass_kg"], mt) and close(ex["ti_co2_life_kg"], ct), f"example Ti {ex['ti_volume_pct']:.0f} %: {mt:.2f} kg, {ct / 1e3:.2f} t")
ok(close(ex["steel_volume_pct_same_co2"], ex["ti_volume_pct"] * ratio), f"example steel tie {ex['ti_volume_pct'] * ratio:.2f} %")
per_t = (cost_t - base_cost) / ((base_co2 - ct) / 1e3)
ok(close(ex["usd_per_t_co2_avoided"], per_t), f"example USD per t avoided {per_t:.2f}")

# ---- every number printed in the figures
F = json.loads((HERE / "fig_texts.json").read_text(encoding="utf-8"))
allt = {k: " ¦ ".join(v) for k, v in F.items()}
expect = {
    "fig_tradeoff_breakeven": [f"{base_co2 / 1e3:.1f} t", f"{ct / 1e3:.1f} t", f"Ti {ex['ti_volume_pct']:.0f} %",
                               f"steel {ex['ti_volume_pct'] * ratio:.0f} %",
                               f"{ti_same / M0:.2f}×", f"{mt / M0:.2f}×", f"{ti_same * life[T] / base_co2:.2f}×",
                               f"{ct / base_co2:.2f}×", f"{ti_same * price[T] / base_cost:.1f}×",
                               f"{cost_t / base_cost:.1f}×"],
    "fig_tradeoff_indices": [f"{100 * v:.0f} %" for v in idx.values()]
                            + [f"{100 * (v - 1):+.0f} %".replace("-", "−") for v in idx.values()],
    "fig_tradeoff_table": [f"{allow[S]:.0f}", f"{allow[T]:.0f}"] + [f"{life[k]:.0f}" for k in R]
                          + [f"{gm(R[k]['co2_virgin']) + gm(R[k]['co2_powder']):.0f}" for k in R]
                          + ["471–501", "250–300", "407–455", "26–38", "31–34", "65–75", "1.0–1.6", "3.1–3.5", "23–26",
                             "7800–7900", "2720–2780", "4350–4400", "200–221", "72–76", "121–127"],
}
for fig, exps in expect.items():
    for e in exps:
        ok(e in allt[fig], f"{fig}: label contains '{e}'")

# ---- numbers quoted in the section text
md = (HERE / "TRADEOFF_SECTION.md").read_text(encoding="utf-8")
quotes = [f"{life[S]:.0f} kg CO₂/kg", f"{life[T]:.0f}", f"{USE:.0f} kg CO₂-eq per kilogram", f"{ti_same:.1f} kg",
          f"{ti_same * life[T] / 1e3:.1f} t", f"{100 * (1 - ti_same * life[T] / base_co2):.0f} %",
          f"{tie:.0f} %", f"{base_co2 / life[T]:.0f} kg", f"{ratio:.2f} ×", f"{ct / 1e3:.1f} t",
          f"{ex['ti_volume_pct'] * ratio:.0f} %", f"{ct / life[S]:.0f} kg", f"{allow[S]:.0f} MPa", f"{allow[T]:.0f} MPa",
          f"{E300[S]:.0f} GPa", f"{E300[T]:.0f} GPa", f"{allow[T] / allow[S]:.1f}×",
          f"{ti_same * price[T]:,.0f}".replace(",", " "), f"{base_cost:.0f} USD", f"{cost_t:.0f} USD",
          f"+{cost_t - base_cost:.0f}", f"{(base_co2 - ct) / 1e3:.0f} t", f"about {per_t:.0f} USD",
          f"{100 * USE / life[S]:.0f} %", f"{100 * USE / life[T]:.0f} %"]
for v in idx.values():
    quotes.append(f"{v:.2f} ({100 * (v - 1):+.0f} %)".replace("-", "−"))
for q in quotes:
    ok(q in md, f"section text quotes '{q}'")

# ---- analytic relations (section 3.5): coefficients re-derived here, printed strings must match
rec = {k: gm(R[k]["co2_recycle"]) for k in R}
eol152 = -m152 * (gm(R[S]["co2_virgin"]) - rec[S])
org_eol = after("End of life potential", 1)               # columns: energy (MJ), CO2 (kg)
ok(abs(eol152 - org_eol) / abs(org_eol) <= 0.015, f"EoL credit 152 kg S275N ours {eol152:.1f} organisers {org_eol:.1f}")
cS_eol = life[S] - (gm(R[S]["co2_virgin"]) - rec[S])
cT_eol = life[T] - (gm(R[T]["co2_virgin"]) - rec[T])
eq_strings = [
    f"C_S = {life[S] / 1000:.4f} · m_S", f"C_Ti = {life[T] / 1000:.4f} · m_Ti", f"C_Al = {life['Al2618T6'] / 1000:.4f} · m_Al",
    f"m_S = {life[T] / life[S]:.3f} · m_Ti", f"m_Ti = {life[S] / life[T]:.3f} · m_S",
    f"C_S = {rho[S] * V0 * life[S] / 1e5:.4f} · f_S", f"C_Ti = {rho[T] * V0 * life[T] / 1e5:.4f} · f_Ti",
    f"f_S = {ratio:.3f} · f_Ti", f"f_Ti = {1 / ratio:.3f} · f_S", f"m_Ti = {rho[T] / rho[S]:.4f} · m_S",
    f"ΔC = {base_co2 / 1e3:.2f} − {life[T] / 1000:.4f} · m_Ti", f"1 − m_Ti / {base_co2 / life[T]:.1f}",
    f"ΔK = {price[T]:.2f} · m_Ti − {base_cost:.1f}", f"m_Ti = {base_cost / price[T]:.1f} kg",
    f"**{life[S]:.1f}**", f"**{life[T]:.1f}**", f"{cS_eol:.1f} (S275N)", f"{cT_eol:.1f}",
    f"m_S = {cT_eol / cS_eol:.3f} · m_Ti",
]
for q in eq_strings:
    ok(q in md, f"section 3.5 states '{q}'")
# the linear relations reproduce the figure numbers (no hidden intercept)
ok(close((base_co2 / 1e3 - life[T] / 1000 * mt) * 1e3, base_co2 - ct), "eq.(5) at the example mass = figure saving")
ok(close(life[T] / life[S] * mt, ct / life[S]), "eq.(2) at the example mass = steel mass with the same CO2")

lines.append(f"\n{len([l for l in lines if l.startswith(('ok', 'FAIL'))])} checks, {bad} FAIL")
(HERE / "check_values.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(l for l in lines if not l.startswith("ok")))
sys.exit(1 if bad else 0)
