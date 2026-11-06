"""Decision indices for the organisers' three materials, from their Granta report only [D-org], all [K].
python -I analysis/decision_indices.py  -> analysis/decision_indices.json (+ printed table)

Which index matters for THIS part: the baseline FEA shows strength is far from critical (vM 57.9 MPa vs Fy >= 205)
while a topology-optimised bracket ends up as compact tension/compression members, for which the mass at a given
stiffness scales with rho/E (Ashby, tie in tension) — the organisers' beam index rho/E^0.5 assumes bending of a
fixed-length beam with free section area, which a topology result is not. Both are reported.
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from organiser_materials import M, gm, USE_KM   # noqa: E402

out = {}
for k, m in M.items():
    rho, E, Fy, price = gm(m["rho"]), gm(m["E"]), m["Fy"][0], gm(m["price"])
    co2_kg = gm(m["co2_virgin"]) + gm(m["co2_powder"]) + 500 * 0.241 / 1000 + USE_KM * 0.000468 + 7.45 / 152
    out[k] = {
        "name": m["name"], "rho": rho, "E_GPa": E, "Fy_min_MPa": Fy,
        "rho_over_E": rho / E,                       # tie stiffness (kg/m3/GPa) — topology members
        "rho_over_sqrtE": rho / E ** 0.5,            # beam stiffness — organisers' chart index
        "rho_over_Fy": rho / Fy,                     # strength-limited tie
        "rho_over_fatigue": rho / m["fatigue_1e7"][0],
        "price_USD_per_kg": price,
        "life_CO2_per_kg_part": co2_kg,              # 1-year life, card settings
        "production_CO2_per_kg": gm(m["co2_virgin"]) + gm(m["co2_powder"]),
        "use_share_pct": 100 * USE_KM * 0.000468 / co2_kg,
        "eol_credit_per_kg": gm(m["co2_virgin"]) - gm(m["co2_recycle"]),
        "Tmax": m["Tmax"], "K1c": m["K1c"], "casting": m["casting"], "oxidation_500C": m["oxidation_500C"],
        "scc": m["scc"], "weldability": m["weldability"],
    }
ref = out["S275N"]
for k, v in out.items():
    v["rel_mass_tie_stiffness"] = v["rho_over_E"] / ref["rho_over_E"]
    v["rel_mass_beam_stiffness"] = v["rho_over_sqrtE"] / ref["rho_over_sqrtE"]
    v["rel_mass_strength"] = v["rho_over_Fy"] / ref["rho_over_Fy"]
(HERE / "decision_indices.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{'':10s} {'rho/E':>7s} {'rel':>5s} {'rho/vE':>7s} {'rel':>5s} {'rho/Fy':>7s} {'rel':>5s} {'USD/kg':>7s} {'CO2/kg life':>11s} {'prod':>6s} {'use%':>5s}")
for k, v in out.items():
    print(f"{k:10s} {v['rho_over_E']:7.1f} {v['rel_mass_tie_stiffness']:5.2f} {v['rho_over_sqrtE']:7.0f} {v['rel_mass_beam_stiffness']:5.2f} "
          f"{v['rho_over_Fy']:7.1f} {v['rel_mass_strength']:5.2f} {v['price_USD_per_kg']:7.2f} {v['life_CO2_per_kg_part']:11.1f} "
          f"{v['production_CO2_per_kg']:6.1f} {v['use_share_pct']:5.1f}")
