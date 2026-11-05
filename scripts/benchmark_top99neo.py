"""Validate aerokit's 2-D SIMP against the published top99neo benchmark (Ferrari and Sigmund 2020, Table 2, T1).

    python -u scripts/benchmark_top99neo.py            # ~20-40 min; writes studies/scenarios/benchmark_top99neo.json

Set-up as published (research_notes/Görev senaryoları/R3 §7 [D]): half-MBB beam 300 x 100 elements, volume fraction
0.5, filter radius 8.75, density filter, p = 3, |q| = 1 at the first node, 2500 iterations: c = 252.7. aerokit's
filter normalises the cone weights near the edge (top88 style); top99neo filters with a mirrored (Neumann) boundary,
so a small difference is expected and is reported, not hidden.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.optimization import topology as tp  # noqa: E402

PUBLISHED = 252.7


def main() -> int:
    pr = tp.mbb_half(300, 100)
    t = time.time()
    r = tp.topopt(pr, 0.5, 8.75, ft=2, optimizer="OC", tol=1e-6, max_iter=2500)
    c = float(r["compliance_final"])
    out = {"published_c": PUBLISHED, "aerokit_c": c, "relative_difference": c / PUBLISHED - 1,
           "iterations": int(r["iteration"]), "grey_percent": float(r["gray"]), "seconds": round(time.time() - t),
           "setup": "mbb_half(300, 100), V 0.5, rmin 8.75, ft 2, OC move 0.2, p 3, max 2500 iterations",
           "source": "Ferrari and Sigmund 2020, SMO, arXiv 2005.05436, Table 2, T1 (via research_notes R3 §7)"}
    path = ROOT / "studies" / "scenarios" / "benchmark_top99neo.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
