"""Organiser material data (Granta EduPack 2026 R1 selection report, read page by page 5 Nov 2026) and an eco-audit
model that reproduces the organisers' initial-design Eco Audit report. All inputs are [D-org]
(files/Material selection report Ideathon challenge.pdf p.7-13, files/Eco assessment initial design report ... p.2-8).
Run: python -I analysis/organiser_materials.py   (from official_2026-11-05/)  -> analysis/organiser_materials.json"""
import json, math, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = "Material selection report Ideathon challenge.pdf"
# (low, high) ranges exactly as printed; all at 23 degC (report p.14 'Functional parameters: Temperature 23')
M = {
 "S275N": dict(name="Structural steel, S275N, normalized", page_props="p.8-13",
     rho=(7800, 7900), E=(200, 221), Fy=(205, 275), Fu=(350, 510), elong=(23, 24), fatigue_1e7=(194, 233),
     K1c=(26.4, 38.1), Tmax=(471, 501), price=(1.02, 1.56), cte=(11, 13), k=(48, 53),
     co2_virgin=(2.89, 3.18), co2_typical=(2.03, 2.23), ee_virgin=(27.4, 30.2), co2_powder=(5.28, 6.79),
     ee_powder=(64.7, 83.2), co2_cast=None, co2_recycle=(0.78, 0.859), recycle_fraction=41,
     casting="Unsuitable", oxidation_500C="Acceptable", scc="Slightly susceptible", weldability="Good",
     mass_per_stiffness=(528, 556), cost_per_stiffness=(552, 846)),
 "Al2618T6": dict(name="Aluminum, 2618, T6", page_props="p.8-13",
     rho=(2720, 2780), E=(72, 76), Fy=(320, 380), Fu=(400, 440), elong=(8, 9), fatigue_1e7=(118, 130),
     K1c=(31, 34), Tmax=(250, 300), price=(3.12, 3.48), cte=(21.5, 22.6), k=(148, 154),
     co2_virgin=(12, 13.2), co2_typical=(8.77, 9.64), ee_virgin=(167, 184), co2_powder=(3.89, 5.17),
     ee_powder=(47.9, 63.6), co2_cast=None, co2_recycle=(2.76, 3.04), recycle_fraction=35,
     casting="Unsuitable", oxidation_500C="Unacceptable", scc="Highly susceptible", weldability="Poor",
     mass_per_stiffness=(314, 325), cost_per_stiffness=(995, 1120)),
 "Ti811SA": dict(name="Titanium, near-alpha alloy, Ti-8Al-1Mo-1V, single annealed", page_props="p.8-13",
     rho=(4350, 4400), E=(121, 127), Fy=(758, 931), Fu=(827, 1000), elong=(6, 10), fatigue_1e7=(529, 579),
     K1c=(65, 75), Tmax=(407, 455), price=(23, 26.3), cte=(8.73, 9.18), k=(6.1, 6.61),
     co2_virgin=(33.6, 37.1), co2_typical=(21.7, 23.9), ee_virgin=(553, 609), co2_powder=(6.24, 7.26),
     ee_powder=(76.4, 88.9), co2_cast=(3.79, 4.28), co2_recycle=(9.74, 10.8), recycle_fraction=50,
     casting="Limited use", oxidation_500C="Acceptable", scc="Slightly susceptible", weldability="Good",
     mass_per_stiffness=(388, 398), cost_per_stiffness=(9020, 10300)),
}
gm = lambda r: math.sqrt(r[0] * r[1])          # Granta uses the geometric mean of a range (checked below)
# eco settings [D-org card + .prd]: 500 km truck, 4000 km/day x 180 days x 1 year long-haul kerosene, recycle at EoL
USE_KM = 4000 * 180 * 1
def eco(mass_kg, key, manuf="co2_powder"):
    m = M[key]
    mat = mass_kg * gm(m["co2_virgin"])
    man = mass_kg * gm(m[manuf])
    tr = mass_kg / 1000 * 500 * 0.241           # card formula, per tonne (the report gives 18.5 kg for 152 kg)
    use = mass_kg * USE_KM * 0.000468
    disp = mass_kg * 7.45 / 152                 # report p.8: 7.45 kg for 152 kg (0.049 kg/kg) [D-org, scaled]
    eol = -mass_kg * (gm(m["co2_virgin"]) - gm(m["co2_recycle"]))
    tot = mat + man + tr + use + disp
    return dict(material=mat, manufacture=man, transport=tr, use=use, disposal=disp, total_first_life=tot,
                eol_potential=eol, total_with_eol=tot + eol)
if __name__ == "__main__":
    ref = {"material": 461, "manufacture": 910, "transport": 18.5, "use": 5.12e4, "disposal": 7.45,
           "total_first_life": 5.26e4, "eol_potential": -336}
    e = eco(152.0, "S275N")
    print("Reproduce organisers' initial-design report (152 kg S275N):")
    for k, v in ref.items():
        print(f"  {k:17s} ours {e[k]:10.1f}  report {v:10.1f}  diff {100 * (e[k] - v) / v:+.1f} %")
    json.dump({"materials": M, "source": SRC, "eco_check_152kg": e, "eco_report": ref}, open("analysis/organiser_materials.json", "w"), indent=1)
