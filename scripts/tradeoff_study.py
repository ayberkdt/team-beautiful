"""Run a material × route trade-off study and write machine-readable results.

    python scripts/tradeoff_study.py studies/tradeoff/bracket_a320_strength.json --out-dir studies/tradeoff/out

Writes ``<name>.results.json`` (everything: nominal, Pareto, Monte Carlo, tornado, weak inputs) and
``<name>.results.md`` (the same as tables) next to each other, and prints a short summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aerokit.design import tradeoff as T  # noqa: E402
from aerokit.output.console import file, result, table  # noqa: E402
from aerokit.output.writers import write_text_atomic  # noqa: E402


def _markdown(out: dict) -> str:
    lines = [f"# {out['study']}", "", f"Index case `{out['case']}` · score: {out['score']}", "",
             "| Rank | Material | Route | Mass (kg) | CO₂ production (kg) | CO₂ use (kg) | CO₂ total (kg) | P(best) |",
             "|---:|---|---|---:|---:|---:|---:|---:|"]
    pb = out["monte_carlo"]["p_best"]
    for r in out["nominal"]:
        lab = f"{r['material']} / {r['route']}"
        lines.append(f"| {r['rank']} | {r['material']} | {r['route']} | {r['mass_kg']:.3f} | "
                     f"{r['co2_production_kg']:.0f} | {r['co2_use_kg']:.0f} | {r['co2_total_kg']:.0f} | "
                     f"{pb[lab]:.2f} |")
    lines += ["", f"Pareto set ({', '.join(out['objectives'])}): " + "; ".join(out["pareto"]), "",
              "| Factor | Range | Tag | Margin at low (kg) | Margin at high (kg) | Reverses choice |",
              "|---|---|---|---:|---:|---|"]
    for t in out["tornado"]:
        lines.append(f"| {t['factor']} | {t['low']:g}–{t['high']:g} {t['unit']} | {t['tag']} | "
                     f"{t['margin_low']:.0f} | {t['margin_high']:.0f} | {'yes' if t['reverses'] else 'no'} |")
    lines += ["", "Inputs tagged S or Y (replace first): " + (", ".join(out["weak_inputs"]) or "none"), ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("study", help="study JSON (schema: studies/tradeoff/README.md)")
    p.add_argument("--out-dir", default=None, help="output folder (default: <study folder>/out)")
    p.add_argument("--samples", type=int, default=3000, help="Monte Carlo samples (3000)")
    p.add_argument("--seed", type=int, default=1, help="random seed (1)")
    a = p.parse_args(argv)
    study_path = Path(a.study)
    out_dir = Path(a.out_dir) if a.out_dir else study_path.parent / "out"
    out = T.run(T.load_study(study_path), samples=a.samples, seed=a.seed)
    stem = study_path.stem
    jpath, mpath = out_dir / f"{stem}.results.json", out_dir / f"{stem}.results.md"
    write_text_atomic(jpath, json.dumps(out, indent=2, ensure_ascii=False))
    write_text_atomic(mpath, _markdown(out))
    pb = out["monte_carlo"]["p_best"]
    table(["Rank", "Option", "Mass (kg)", "CO₂ total (kg)", "P(best)"],
          [[r["rank"], f"{r['material']} / {r['route']}", f"{r['mass_kg']:.3f}", f"{r['co2_total_kg']:.0f}",
            f"{pb[r['material'] + ' / ' + r['route']]:.2f}"] for r in out["nominal"]])
    file(str(jpath))
    file(str(mpath))
    best, top = out["nominal"][0], out["tornado"][0]
    result(f"Best: {best['material']} / {best['route']} (P = {pb[best['material'] + ' / ' + best['route']]:.2f} "
           f"over {a.samples} samples); largest swing: {top['factor']}.",
           "Replace the inputs listed under 'weak_inputs' with EduPack or datasheet values and rerun.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
