"""Build sim_points.json from the read-only simulator runs (refitted wake model) and copy the raw logs next to it."""
import json
import math
import shutil
from pathlib import Path

HERE = Path(r"D:\tmp_ideathon\venus\budget")
OUT = Path(r"D:\Masaustu\Ideathon 2026\04_Venus\outputs\variants\budget_update\sim_runs")
SIM = Path(r"D:\Custom Yetenekler\sunumatik\.claude\worktrees\venus-rotorcraft-visual-44d0d1"
           r"\presets\venus_rotorcraft\sim")
OUT.mkdir(parents=True, exist_ok=True)
pts = json.loads((HERE / "sim_pts2.json").read_text(encoding="utf-8"))["pts"]
curves = json.loads((SIM / "guc_egrisi.json").read_text(encoding="utf-8"))
CASES = ("off", "low", "nominal", "high")
W, ETA = 380.28, 0.80256          # baseline weight at 55 km [N], drive efficiency


def get(tag, **kw):
    return next(p for p in pts if p["tag"] == tag and all(p.get(k) == v for k, v in kw.items()))


credit, climb = {}, {}
for c in CASES:
    cr = [(get("level35", km=km, e=c)["el"] - get("descent", km=km, e=c)["el"]) / (W * 1.5 / ETA) for km in (55, 53)]
    ck = [(get("climb", km=km, e=c)["el"] - get("level8", km=km, e=c)["el"]) / (W * 3.0 / ETA) for km in (55, 53)]
    credit[c], climb[c] = sum(cr) / 2, sum(ck) / 2

Vs = [0, 5, 7, 8, 9, 10, 12]
off = {r["V"]: r["shaft_W"] for r in curves["egri"]["55_km"]["off"]}
spacing = {"V": Vs, "isolated_shaft_W": [off[v] for v in Vs], "nominal_shaft_W": {}}
for c in (0.10, 0.26, 0.52, 0.78):
    spacing["nominal_shaft_W"][f"{c:.2f}"] = [get("spacing", c=c, V=v)["sh"] for v in Vs]

RUNS = [("as simulated 5 Nov: afternoon, cos z 0.70", "dive", "dalis_on2", "nominal", "seed 1", 45.57, 1.0, 4400),
        ("same, interaction off", "dive", "dalis_off2", "off", "seed 1", 45.57, 1.0, 4400),
        ("same, calm air", "dive", "dalis_h70_calm", "nominal", "calm", 45.57, 1.0, 4400),
        ("dive at cos z 0.80 (morning)", "dive", "dalis_m80", "nominal", "seed 1", -36.87, 1.0, 4400),
        ("dive at cos z 0.87, calm", "dive", "dalis_m29_calm", "nominal", "calm", -29.0, 1.0, 4400),
        ("dive at cos z 0.87, seed 2", "dive", "dalis_m29_s2", "nominal", "seed 2", -29.0, 1.0, 4400),
        ("dive at cos z 0.87, seed 3", "dive", "dalis_m29_s3", "nominal", "seed 3", -29.0, 1.0, 4400),
        ("dive near noon", "dive", "dalis_noon", "nominal", "seed 1", -4.0, 1.0, 4400),
        ("sunset as simulated: forced SoC 35 %, cos z 0.12", "sunset", "sunset_asis2", "nominal", "seed 1", 83.1, 0.35, 1800),
        ("sunset at mission state, at 60 C", "sunset", "sunset_real", "nominal", "seed 1", 52.7, 0.50, 5000)]
checks = []
for name, kind, f, case, air, H0, soc0, t_end in RUNS:
    log = json.loads((HERE / f"{f}.json").read_text(encoding="utf-8"))
    shutil.copy2(HERE / f"{f}.json", OUT / f"{f}.json")
    if f == "sunset_real":          # the simulator does not stop at the 60 C discharge limit: compare there
        log = log[:next(i for i, r in enumerate(log) if r["Tin"] >= 60.0) + 1]
    checks.append({"name": name, "kind": kind, "log": f, "interaction": case, "air": air, "H0_deg": H0, "soc0": soc0,
                   "t_end_s": t_end, "mu0_start": math.cos(math.radians(H0)), "sim_end_soc": log[-1]["soc"],
                   "sim_end_km": log[-1]["h"] / 1e3, "sim_T_peak_C": max(r["Tin"] for r in log),
                   "sim_min_soc": min(r["soc"] for r in log)})
rel = json.loads((HERE / "release_nom.json").read_text(encoding="utf-8"))
shutil.copy2(HERE / "release_nom.json", OUT / "release_nom.json")
def tilt(f):
    return json.loads((HERE / f"{f}.log").read_text(encoding="utf-8").split(" ", 1)[1])


dive_52 = [{"seed": s_, **tilt(f)} for s_, f in (("seed 1", "t52"), ("seed 2", "t52s2"), ("seed 3", "t52s3"))]
dive_51 = [{"seed": s_, **tilt(f)} for s_, f in (("seed 1", "t51"), ("seed 2", "t51s2"), ("seed 3", "t51s3"))]
doc = {"note": "Read-only runs of the sunumatik simulator after the 6 Nov 11:07 wake refit (kw 0.3/0.5/0.7). Electric power "
               "incl. 55 W. credit = share of W V_d / eta returned at 1.5 m/s down, 3.5 m/s forward; climb_k = climb power "
               "over W V_c / eta at 3 m/s, 8 m/s forward (deck drag in the simulator); means of 55 and 53 km.",
       "descent_credit": credit, "climb_k": climb, "spacing": spacing, "dive_checks": checks,
       "release": {"min_soc": min(r["soc"] for r in rel if "soc" in r), "H0_deg": -43.0,
                   "descent_end_soc": rel[-1]["soc"]},
       "dive_52km": dive_52, "dive_51km": dive_51,
       "release_current": [json.loads(x) for x in (HERE / "sim_peak.log").read_text(encoding="utf-8").splitlines() if x],
       "descent_W_55km": {c: get("descent", km=55, e=c)["el"] for c in CASES},
       "climb_W_55km": {c: get("climb", km=55, e=c)["el"] for c in CASES}, "raw_points": pts}
(OUT / "sim_points.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
for f in ("common.mjs", "sim_hist.mjs", "sim_pts2.mjs", "sim_release.mjs", "sim_head.mjs", "sim_tilt.mjs",
          "sim_peak.mjs", "sim_peak.log", "t51.log", "t51s2.log", "t51s3.log", "t52.log", "t52s2.log", "t52s3.log",
          "collect.py"):
    shutil.copy2(HERE / f, OUT / f)
if (HERE / "sim_head.json").is_file():
    shutil.copy2(HERE / "sim_head.json", OUT / "sim_head.json")
print({k: round(v, 3) for k, v in credit.items()}, {k: round(v, 3) for k, v in climb.items()})
for c in checks:
    print(c["name"], round(c["sim_end_soc"], 3), round(c["sim_min_soc"], 3), round(c["sim_T_peak_C"], 1), round(c["sim_end_km"], 2))
