"""LuGus final (4–5 Nov 2026): VESPER rotorcraft — numbers, audited figures and the design hand-off in one run.

    python 04_Venus/code/pipeline/venus_day.py --final          (or: python 04_Venus/code/pipeline/venus_final.py)
    python 04_Venus/code/pipeline/venus_day.py --final --payload-kg 5 --cruise-km 56     # mentor numbers -> outputs/variants/out_variant_*/

Writes to ``04_Venus/outputs/``: ``result.json``, ``result.md``, figures F1–F9 (PDF + PNG + datawiz
audit ``*.denetim.txt``, set ``vesper.seti.json`` + ``vesper.tutarlilik.txt``) and regenerates
``04_Venus/outputs/design.json``. Reads ``trade_sizing.json`` / ``sensitivity.json`` when present (produced
by ``04_Venus/code/analysis/venus_trade.py`` and ``04_Venus/code/analysis/venus_sensitivity.py``, several minutes each).

Thin entry: numbers in ``final_compute.py``, figures in ``final_figures.py``, simulator file in ``final_sim.py``,
``result.md`` in ``final_report.py``. ``OUT`` and ``BASE`` live here and are passed down, so a patched
``venus_final.OUT`` (``venus_variant_v07.py``) still reaches every writer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import final_compute  # noqa: E402
import final_figures  # noqa: E402
import final_sim  # noqa: E402
from day_common import audit_summary, console_text, progress, protect_streams  # noqa: E402
from final_report import markdown  # noqa: E402

from aerokit.venus import design as DES  # noqa: E402

OUT = ROOT / "04_Venus" / "outputs"
BASE = DES.BASELINE                     # replaced by main() when the mentor gives other numbers


def compute() -> dict:
    return final_compute.compute(BASE, OUT)


def figures(c: dict) -> None:
    final_figures.figures(c, OUT)


def simulator_parameters(c: dict) -> dict:
    return final_sim.simulator_parameters(c, BASE)


def _parse(argv: list[str]) -> tuple[dict, bool]:
    """``--payload-kg X``, ``--cruise-km X``, ``--rotor-d X`` (also ``--name=X``); ``--reuse``."""
    keys = {"payload-kg": "payload_kg", "cruise-km": "cruise_km", "rotor-d": "D"}
    over: dict = {}
    reuse = False
    i = 0
    while i < len(argv):
        a = argv[i].lower()
        if a in ("--reuse", "reuse"):
            reuse = True
        else:
            name, _, val = a.lstrip("-").partition("=")
            name = name.replace("_", "-")
            if name not in keys:
                raise SystemExit(f"unknown option {argv[i]!r}; use --payload-kg, --cruise-km, --rotor-d, --reuse")
            if not val:
                i += 1
                val = argv[i] if i < len(argv) else ""
            over[keys[name]] = float(val.replace(",", "."))
        i += 1
    return over, reuse


def main(argv: list[str] | None = None) -> int:
    global OUT, BASE
    protect_streams()
    over, reuse = _parse(list(argv or []))
    variant = bool(over)
    if variant:                           # mentor numbers: separate folder, never overwrite the hand-off files
        from dataclasses import replace as _rep

        BASE = _rep(DES.BASELINE, **over)
        tag = "_".join(f"{k}{v:g}" for k, v in sorted(over.items()))
        OUT = OUT / "variants" / f"out_variant_{tag}"   # keeps what-if runs inside 04_Venus/outputs/
    OUT.mkdir(parents=True, exist_ok=True)
    import pickle

    cache = Path("D:/tmp_ideathon/venus/final_cache.pkl")
    if reuse and not variant and cache.exists():                # figure iteration only (not for delivery runs)
        c = pickle.loads(cache.read_bytes())
    else:
        c = compute()
        try:
            cache.write_bytes(pickle.dumps(c))
        except Exception:                                       # the cache is a convenience
            pass
    for k in ("trade", "sens"):                                 # always the latest sweep outputs (baseline folder)
        f = ROOT / "04_Venus" / "outputs" / ("trade_sizing.json" if k == "trade" else "sensitivity.json")
        c[k] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    (OUT / "result.json").write_text(json.dumps(c["out"], indent=1, default=float, ensure_ascii=False), encoding="utf-8")
    (OUT / "result.md").write_text(markdown(c["out"]), encoding="utf-8")
    progress("drawing and auditing figures F1-F15")
    figures(c)
    progress("simulator parameters (vesper_for_simulator.json)")
    (OUT / "vesper_for_simulator.json").write_text(json.dumps(simulator_parameters(c), indent=1), encoding="utf-8")
    progress("regenerating design.json")
    import venus_design

    if variant:
        venus_design.main([], BASE, OUT.parent / f"design_variant_{OUT.name.removeprefix('out_variant_')}.json")
    else:
        venus_design.main([])
    n_err, line = audit_summary(OUT)
    print(console_text(markdown(c["out"])))
    print(console_text(line))
    v, m = c["out"]["vehicle"], c["out"]["mission"]
    verdict = "figures NOT deliverable (audit errors)" if n_err else "figures audited, deliverable"
    where = f"variant results in {OUT}" if variant else "design hand-off: 04_Venus/outputs/design.json"
    print(console_text(f"VESPER {v['gross_kg']:.1f} kg, {m['flight_h']:.0f} h flight; {verdict}. "
                       f"Next: read 04_Venus/docs/25_lugus_venus_rotorcraft.md ({where})."))
    return 1 if n_err else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
