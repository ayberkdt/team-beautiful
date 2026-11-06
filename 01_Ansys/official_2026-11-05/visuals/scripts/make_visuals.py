"""One command for all deliverables (run from the project root with the environment of visuals/README.md):

    python studies/final_2026/ansys/official_2026-11-05/visuals/scripts/make_visuals.py [--skip-turntable]

Order: exact solid + volume check -> hero renders -> BC diagram -> dimensioned views -> turntable frames.
Each step is also runnable on its own (build_exact.py, hero.py, bc_loads.py, views.py, turntable.py).
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["build_exact.py", "hero.py", "bc_loads.py", "views.py", "turntable.py"]


def main() -> None:
    skip_tt = "--skip-turntable" in sys.argv
    for s in STEPS:
        if skip_tt and s == "turntable.py":
            continue
        print(f"=== {s}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, s)])
        if r.returncode:
            raise SystemExit(f"{s} failed with exit code {r.returncode}")
    # audit gate: every datawiz report must say 0 HATA
    vis = os.path.dirname(HERE)
    for name in ("bc_loads", "views_dimensioned"):
        first = open(os.path.join(vis, f"{name}.denetim.txt"), encoding="utf-8").readline().strip()
        print(f"{name}: {first}")
        if " 0 HATA" not in first:
            raise SystemExit(f"{name}: datawiz audit has HATA")


if __name__ == "__main__":
    main()
