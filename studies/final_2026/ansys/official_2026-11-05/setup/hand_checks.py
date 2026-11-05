"""Order-of-magnitude hand checks for the official bracket (geometry from derived/features.json).
Run: python -I setup/hand_checks.py  (from the official_2026-11-05 folder). All results are [K]."""
import json, math, sys
sys.stdout.reconfigure(encoding="utf-8")
Fz, Fy, My = 97e3, 24e3, 2000.0           # per pin hole [N], torsion total [N m] (challenge card)
d, t_lug = 60.0, 70.0                     # pin bore Ø and lug thickness [mm] (features.json)
z_plate, z_pin, z_top, r_arc, z_arc = 100.0, 260.0, 321.37, 80.0, 241.37
x_bolt, y_bolt = (245.0, 755.0), (95.0, 305.0)
out = {}
out["bearing_MPa"] = Fz / (d * t_lug)
half_w = math.sqrt(r_arc**2 - (z_pin - z_arc) ** 2)          # lug half-width at pin height
out["lug_halfwidth_at_pin_mm"] = half_w
out["net_section_tension_MPa"] = Fz / (2 * (half_w - d / 2) * t_lug)
out["ligament_above_pin_mm"] = z_top - (z_pin + d / 2)
b_root = 188.0                                              # lug width at top of the root fillets (flank planes) [mm]
h_arm = z_pin - z_plate
out["lug_root_out_of_plane_bending_MPa"] = Fy * h_arm / (b_root * t_lug**2 / 6)
out["lug_root_axial_MPa"] = Fz / (b_root * t_lug)
span, B, T = x_bolt[1] - x_bolt[0], 341.12, 70.0
P = 2 * Fz
Z = B * T**2 / 6
out["plate_bending_fixed_fixed_MPa"] = P * span / 8 / Z
out["plate_bending_pinned_MPa"] = P * span / 4 / Z
out["bolt_tension_LC1_kN"] = P / 4 / 1e3
out["bolt_shear_LC1_kN"] = 2 * Fy / 4 / 1e3
arm = (x_bolt[1] - x_bolt[0]) / 2 / 1e3
out["bolt_axial_LC2_kN"] = My / (4 * arm) / 1e3                # 2 bolts each side, lever ±255 mm
out["largest_dimension_mm"] = 661.01
out["displacement_limit_mm"] = 661.01 / 400
for k, v in out.items():
    print(f"{k:38s} {v:10.3f}")
json.dump(out, open("setup/hand_checks.json", "w"), indent=1)
