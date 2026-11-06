"""Material-only swap on the UNCHANGED organiser geometry (volume 0.019400 m^3), organiser data at 23 degC [D-org]
and a 300 degC sensitivity with our catalogue knock-downs [Y]. Stress field is material-independent (linear,
isotropic, prescribed loads); displacement scales with 1/E. Baseline FEA: runs/baseline_fixed_bores/report.md
(voxel H8IM 6.2 mm: vM outside hole zones 57.9 MPa, max |u| 0.2047 mm at E = 182.7 GPa).
Run: python -I analysis/material_swap.py"""
import json, sys, math
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "analysis")
from organiser_materials import M, eco, gm
V = 0.019400                     # m^3, exact CAD (derived/features.json, visuals/initial_exact.step)
SIG = 57.9                       # MPa, smooth peak outside hole zones (voxel); T10 sharp-edge peak is singular
U0, E0 = 0.2047, 182.7           # mm at GPa
LIM_U = 661.01 / 400
FOS = 1.5
K300 = {"S275N": 0.78, "Al2618T6": None, "Ti811SA": 0.683}   # Fty(300)/Fty(RT): EN 1993-1-2 k_p0.2; MIL 2618 none >204 C; MIL Ti-8-1-1 68.3 %
KE300 = {"S275N": 0.80, "Al2618T6": None, "Ti811SA": 0.869}
rows = []
for key, m in M.items():
    rho, E, Fy = gm(m["rho"]), gm(m["E"]), m["Fy"][0]
    mass = V * rho
    u23 = U0 * E0 / E
    e = eco(mass, key)
    r = dict(material=m["name"], mass_kg=mass, disp_mm_23C=u23, disp_ok=u23 < LIM_U,
             util_23C=SIG * FOS / Fy, Fy_min_MPa=Fy,
             util_300C=(SIG * FOS / (Fy * K300[key])) if K300[key] else None,
             disp_mm_300C=(U0 * E0 / (E * KE300[key])) if KE300[key] else None,
             Tmax_C=m["Tmax"], K1c=m["K1c"], cost_USD=mass * gm(m["price"]),
             co2_total_first_life=e["total_first_life"], co2_material=e["material"], co2_manufacture=e["manufacture"],
             co2_use=e["use"], co2_with_eol=e["total_with_eol"])
    rows.append(r)
base = rows[0]
print(f"{'material':58s} {'kg':>7s} {'u23 mm':>7s} {'U23':>5s} {'U300':>5s} {'USD':>7s} {'CO2 t':>7s} {'dCO2 %':>7s}")
for r in rows:
    u3 = f"{r['util_300C']:.2f}" if r['util_300C'] else "n/a"
    print(f"{r['material']:58s} {r['mass_kg']:7.1f} {r['disp_mm_23C']:7.3f} {r['util_23C']:5.2f} {u3:>5s} {r['cost_USD']:7.0f} "
          f"{r['co2_total_first_life']/1e3:7.2f} {100*(r['co2_total_first_life']/base['co2_total_first_life']-1):+7.1f}")
json.dump(rows, open("analysis/material_swap.json", "w"), indent=1)
