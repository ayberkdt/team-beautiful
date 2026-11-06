"""Final check of the chosen design: Ti-8Al-1Mo-1V on the 25 % topology layout, using the CONFORMING T10 result of
that layout (runs/topo_fixed_bores/result.json details.tet.chosen; solved at E = 96.8 GPa, the pipeline's Ti-6Al-4V
value at 300 °C). Stress is E-independent; displacement scales with 1/E. [K]
python -I analysis/final_choice.py -> analysis/final_choice.json"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from organiser_materials import M, eco, gm   # noqa: E402

r = json.loads((HERE.parent / "runs/topo_fixed_bores/result.json").read_text(encoding="utf-8"))["details"]
t10 = r["tet"]["chosen"]
assert r["choice"]["design"] == "topo 25 %"
E_SOLVE = 96.8e9
u_unitE = max(c["max_disp_m"] for c in t10["cases"]) * E_SOLVE
sig = max(c["vm_outside_Pa"] for c in t10["cases"]) / 1e6
worst = max(t10["cases"], key=lambda c: c["vm_outside_Pa"])
ti = M["Ti811SA"]
E23 = gm(ti["E"]) * 1e9
cases = {"23 C": (E23, ti["Fy"][0]), "300 C": (E23 * 0.869, ti["Fy"][0] * 0.683)}   # catalogue knock-downs [Y]
V = t10["volume_m3"]                                    # smoothed STL of the layout (+1.9 % vs voxels): conservative
mass = V * gm(ti["rho"])
base_mass = 152.0                                       # organisers' eco report
e_new, e_base = eco(mass, "Ti811SA"), eco(base_mass, "S275N")
cost_new, cost_base = mass * gm(ti["price"]), 0.019397542 * gm(M["S275N"]["rho"]) * gm(M["S275N"]["price"])
out = {"layout": "topo 25 %", "T10_elements": t10["elements"], "volume_m3": V, "mass_kg": mass,
       "sigma_T10_MPa": sig, "sigma_at_mm": [round(x * 1e3) for x in worst["vm_outside_at_m"]], "worst_case": worst["name"],
       "limit_disp_mm": 661.01 / 400}
for k, (E, Fy) in cases.items():
    out[f"disp_mm_{k}"] = u_unitE / E * 1e3
    out[f"util_{k}"] = 1.5 * sig / Fy
out.update(life_co2_new_t=e_new["total_first_life"] / 1e3, life_co2_base_t=e_base["total_first_life"] / 1e3,
           co2_saving_pct=100 * (1 - e_new["total_first_life"] / e_base["total_first_life"]),
           mass_saving_pct=100 * (1 - mass / 152.27), cost_new_USD=cost_new, cost_base_USD=cost_base,
           USD_per_t_CO2_saved=(cost_new - cost_base) / ((e_base["total_first_life"] - e_new["total_first_life"]) / 1e3),
           eco_phases_new=e_new, eco_phases_base=e_base)
(HERE / "final_choice.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out.items():
    if not isinstance(v, dict):
        print(f"{k:24s} {v:.4g}" if isinstance(v, float) else f"{k:24s} {v}")
