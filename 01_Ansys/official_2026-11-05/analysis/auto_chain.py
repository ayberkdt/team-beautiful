"""Automatic chain after a topology run: verify → choose → finalize → re-verify → fall back → figure. No manual step.

  CASE=<run folder in runs/> python -I analysis/auto_chain.py

1. `verify_v2.py`: every layout of the run, with
   * topology gates: one body, both lugs in it, symmetry measured;
   * T10 of the TO shape: 4 card cases + 6 combined, organisers' Ti-8Al-1Mo-1V low-end values at 300 °C,
     FoS 1.5 on yield (mentor), u < L/400.
2. Candidates = layouts that pass, lightest first.
3. For each candidate: `finalize_v2.py <tag>`, i.e. the manufacturing-ready shape plus the SAME T10 check and the
   manufacturing gate (one body, watertight, wall p1 ≥ 1.2 mm). The first finalized shape that passes is the result.
   If it fails, the next heavier layout is finalized.
4. `three_models_figure.py <tag>`: initial / TO / finalized, with the datawiz audit.
5. Summary -> analysis/auto_chain_<CASE>.json and .md
"""
import json, os, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
CASE = os.environ["CASE"]
env = dict(os.environ, CASE=CASE, PYTHONIOENCODING="utf-8")


def run(*args):
    r = subprocess.run([sys.executable, "-I", *map(str, args)], cwd=HERE.parent, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    lines = [ln for ln in (r.stdout + r.stderr).splitlines() if "Warning" not in ln and ln.strip()]
    print("\n".join(lines[-6:]), flush=True)
    if r.returncode:
        raise RuntimeError(f"{args[0]} failed (exit {r.returncode})")


run(HERE / "verify_v2.py")
ver = json.loads((HERE / f"verify_{CASE}.json").read_text(encoding="utf-8"))
cands = sorted([x for x in ver["layouts"] if x["passes_300C"]], key=lambda x: x["mass_Ti811_kg"])
log = {"case": CASE, "layouts": [{k: x[k] for k in ("layout", "mass_Ti811_kg", "sigma_max_MPa", "disp_mm_300C",
                                                     "util_300C", "bodies_kept", "lugs_in_one_body",
                                                     "x_mirror_symmetry", "y_mirror_symmetry", "passes_300C")}
                                  for x in ver["layouts"]], "tried": [], "result": None}
for x in cands:
    tag = round(100 * x["volfrac"])
    run(HERE / "finalize_v2.py", tag)
    f = json.loads((HERE / f"finalize_{CASE}_{tag}.json").read_text(encoding="utf-8"))
    row = {"tag": tag, "mass_kg": f["t10"]["mass_Ti811_kg"], "sigma_MPa": f["t10"]["sigma_max_MPa"],
           "disp_mm_300C": f["t10"]["disp_mm_300C"], "util_300C": f["t10"]["util_300C"],
           "manufacturing_ok": f["manufacturing_checks_pass"], "passes_all": f["passes_all"]}
    log["tried"].append(row)
    if f["passes_all"]:
        log["result"] = row
        break
(HERE / f"auto_chain_{CASE}.json").write_text(json.dumps(log, indent=1, default=float), encoding="utf-8")
md = [f"# Automatic chain — {CASE}", "", "| Layout | Mass Ti-8-1-1 (kg) | σ (MPa) | u 300 °C (mm) | U 300 °C | bodies | "
      "lugs in one body | sym x / y | passes |", "|---|---|---|---|---|---|---|---|---|"]
for x in log["layouts"]:
    md.append(f"| {x['layout']} | {x['mass_Ti811_kg']:.2f} | {x['sigma_max_MPa']:.0f} | {x['disp_mm_300C']:.3f} | "
              f"{x['util_300C']:.3f} | {x['bodies_kept']} | {x['lugs_in_one_body']} | {x['x_mirror_symmetry']:.3f} / "
              f"{x['y_mirror_symmetry']:.3f} | {'PASS' if x['passes_300C'] else 'FAIL'} |")
md += ["", "Finalized attempts (lightest passing layout first):", ""]
md += [f"- {r['tag']} %: {r['mass_kg']:.2f} kg, σ {r['sigma_MPa']:.0f} MPa, u {r['disp_mm_300C']:.3f} mm, "
       f"U {r['util_300C']:.3f}, manufacturing {'OK' if r['manufacturing_ok'] else 'FAIL'} -> "
       f"{'PASS' if r['passes_all'] else 'FAIL'}" for r in log["tried"]]
md += ["", f"**Result:** {log['result']}" if log["result"] else "**Result:** no finalized layout passes"]
(HERE / f"auto_chain_{CASE}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
if log["result"]:                       # figure last: a failed figure audit must not lose the engineering summary
    run(HERE / "three_models_figure.py", log["result"]["tag"])
