"""Write ``studies/final_2026/venus/design.json`` — the hand-off file for the 3-D visual session.

    python scripts/venus_design.py            # writes design.json (+ a dated copy in studies/final_2026/venus/versions/)

Schema ``venus_rotorcraft_design/1`` as requested by the visual session (``presets/venus_rotorcraft/REQUESTS.md``):
SI units, metres, kg, K, Pa, kg/m³, m/s, rpm. Extra keys (positions, sizes, materials, tags) are ignored by the page
but carry the engineering detail. Frame: origin at the body centre, x forward, y left, z up; the vehicle is shown in
hover with arms deployed.

The vehicle numbers come from :mod:`aerokit.venus.design` (the sized baseline) when it is importable; every value has
a ``tag``: ``D`` read from a primary source, ``D-ag`` read by a research agent, ``K`` computed here, ``Y`` our
judgement / assumption.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "studies" / "final_2026" / "venus" / "design.json"
VERSIONS = OUT.parent / "versions"


def build(b=None) -> dict:
    from aerokit.venus import design as D

    return D.design_document(b) if b is not None else D.design_document()


def main(argv: list[str], b=None, out: Path | None = None) -> int:
    """Write design.json (``b``: a :class:`aerokit.venus.design.Baseline`; ``out``: another path for variants)."""
    global OUT
    if out is not None:
        OUT = out
    doc = build(b)
    doc["generated_by"] = "python scripts/venus_design.py"
    doc["generated_at"] = _dt.datetime.now().astimezone().isoformat(timespec="minutes")
    text = json.dumps(doc, indent=1, ensure_ascii=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    VERSIONS.mkdir(exist_ok=True)
    if OUT.exists():                       # anchor the old version before overwriting (user rule)
        old = OUT.read_text(encoding="utf-8")
        tag = json.loads(old).get("version", "unknown")
        shutil.copy2(OUT, VERSIONS / f"design_v{tag}_{hashlib.sha256(old.encode()).hexdigest()[:8]}.json")
    OUT.write_text(text, encoding="utf-8")
    print(f"design.json v{doc['version']} ({doc['status']}) -> {OUT}  sha256 {hashlib.sha256(text.encode()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
