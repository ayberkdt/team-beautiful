"""Shared helpers for the case runners (``cases/<case>/run.py``): parameters, output folder, figures.

Parameters live in ``<case>/params.json``::

    {"case": "...", "params": {"snr_db": {"value": [...], "unit": "dB", "source": "[Y] ..."}, ...},
     "quick": {"n_per_snr": 60}}

Override order (last wins): params.json → ``quick`` block (with ``--quick``) → ``--params mentor.json`` (flat
``{"name": value}`` or the same structure) → ``--set name=value`` (repeatable; the value is read as JSON when it
parses, e.g. ``--set snr_db=[30,20,10]``, else as text). Unknown names are rejected with the list of valid ones.
Everything used is written to ``outputs/params_used.json`` with the override trail.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
CASES = Path(__file__).resolve().parent


def _coerce(raw: str, default):
    try:
        v = json.loads(raw)
    except json.JSONDecodeError:
        v = raw
    if isinstance(default, bool) and isinstance(v, str):
        return v.lower() in ("1", "true", "yes", "on")
    if isinstance(default, float) and isinstance(v, int) and not isinstance(v, bool):
        return float(v)
    return v


class Case:
    """Parsed parameters + output folder of one case run."""

    def __init__(self, run_file: str, argv: list[str] | None = None, description: str = ""):
        self.dir = Path(run_file).resolve().parent
        self.name = self.dir.name
        ap = argparse.ArgumentParser(prog=f"{self.name}/run.py", description=description)
        ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                        help="override one parameter (repeatable); JSON values accepted")
        ap.add_argument("--params", help="JSON file with overrides (e.g. the mentor's numbers)")
        ap.add_argument("--out", help="output folder (default: <case>/outputs)")
        ap.add_argument("--quick", action="store_true", help="smaller Monte Carlo (smoke test)")
        ap.add_argument("--no-fig", action="store_true", help="skip the figure (no datawiz needed)")
        self.args = ap.parse_args(argv)
        spec = json.loads((self.dir / "params.json").read_text(encoding="utf-8-sig"))
        self.meta = spec["params"]
        self.p = {k: v["value"] for k, v in self.meta.items()}
        self.trail: list[str] = []
        if self.args.quick:
            for k, v in spec.get("quick", {}).items():
                self._put(k, v, "quick")
        if self.args.params:
            extra = json.loads(Path(self.args.params).read_text(encoding="utf-8-sig"))
            extra = extra.get("params", extra)
            for k, v in extra.items():
                self._put(k, v["value"] if isinstance(v, dict) and "value" in v else v, self.args.params)
        for item in self.args.set:
            if "=" not in item:
                ap.error(f"--set needs NAME=VALUE, got {item!r}")
            k, raw = item.split("=", 1)
            k = k.strip()
            if k not in self.p:
                ap.error(f"unknown parameter {k!r}; valid: {', '.join(sorted(self.p))}")
            self._put(k, _coerce(raw.strip(), self.p[k]), "--set")
        self.out = Path(self.args.out) if self.args.out else self.dir / "outputs"
        self.out.mkdir(parents=True, exist_ok=True)
        self.t0 = time.time()
        print(f"running {self.name} ({'quick' if self.args.quick else 'full'}) ...", flush=True)

    def _put(self, k: str, v, why: str) -> None:
        if k not in self.p:
            raise SystemExit(f"{self.name}: unknown parameter {k!r} (from {why}); valid: {', '.join(sorted(self.p))}")
        self.trail.append(f"{k} = {json.dumps(v)}  ({why})")
        self.p[k] = v

    def unit(self, k: str) -> str:
        return self.meta[k].get("unit", "")

    def params_table(self) -> str:
        rows = ["| Parameter | Value | Unit | Source |", "|---|---|---|---|"]
        for k, v in self.p.items():
            m = self.meta[k]
            val = json.dumps(v) if not isinstance(v, str) else v
            if len(val) > 70:
                val = val[:67] + "..."
            rows.append(f"| `{k}` | {val} | {m.get('unit', '')} | {m.get('source', '')} |")
        return "\n".join(rows)

    def finish(self, title: str, key_numbers: list[tuple[str, str]], body: str, figures: list[str]) -> Path:
        """Write ``result.md`` + ``params_used.json``; print ≤ 8 console lines (UX budget in cases/UX_AUDIT.md)."""
        (self.out / "params_used.json").write_text(json.dumps({"params": self.p, "overrides": self.trail},
                                                              indent=1, default=str), encoding="utf-8")
        cmd = "python " + " ".join([f"03_Advionics/cases/{self.name}/run.py"] + (sys.argv[1:] if sys.argv else []))
        md = [f"# {title}", "", f"Generated by `{cmd}` on {time.strftime('%Y-%m-%d %H:%M')} "
              f"({time.time() - self.t0:.1f} s). Tags: [K] computed here, [Y] assumption, [D-ag] research note.", "",
              "## Key numbers [K]", ""]
        md += [f"- **{k}:** {v}" for k, v in key_numbers]
        md += ["", body, "", "## Figures", ""]
        md += [f"- `{f}.png` (+ `.pdf`, datawiz audit `{f}.denetim.txt`)" for f in figures] or ["- none (--no-fig)"]
        md += ["", "## Parameters used", "", self.params_table()]
        if self.trail:
            md += ["", "Overrides: " + "; ".join(self.trail)]
        path = self.out / "result.md"
        path.write_text("\n".join(md) + "\n", encoding="utf-8")
        for k, v in key_numbers[:3]:          # console ≤ 120 columns; the full text is in result.md
            print(f"  {k[:40]:<40} {v if len(v) <= 77 else v[:74] + '...'}")
        if figures:
            print(f"  {'figure':<40} {', '.join(figures)}")
        print(f"done in {time.time() - self.t0:.1f} s -> open {path}")
        return path


def figure_set(case: "Case"):
    """The datawiz set of one case (``<case>/figures.seti.json``, target sunum-tam). One set per case: the cases are
    independent slides, and one shared 8-colour palette cannot hold every entity of nine cases."""
    import datawiz as dw
    return dw, dw.Seti(str(case.dir / "figures.seti.json"), hedef="sunum-tam")


def save_figure(S, fig, out: Path, name: str) -> str:
    """Save through datawiz (cila + audit) and fail loudly if the audit has a HATA."""
    S.kaydet(fig, str(out / name), sessiz=True)
    import matplotlib.pyplot as plt
    plt.close(fig)
    first = (out / f"{name}.denetim.txt").read_text(encoding="utf-8").splitlines()[0]
    if " 0 HATA" not in first:
        raise SystemExit(f"datawiz audit failed for {name}: {first}")
    return name


def md_table(rows: list[dict], cols: list[str], fmt: dict[str, str] | None = None) -> str:
    fmt = fmt or {}
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(format(r[c], fmt.get(c, "")) if c in fmt else str(r[c]) for c in cols) + " |")
    return "\n".join(out)
