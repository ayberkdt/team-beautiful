"""Retrofit a cached study (out/<case>/study.pkl) made before density snapshots / roles_source existed.

    python scripts/bracket_snapshots.py studies/final_2026/ansys/out/sketch --roles-source auto [--replay]

``--replay`` re-runs the warm-started topology chain with snapshots every 5 iterations
(:func:`aerokit.bracket.pipeline.replay_topology`) and prints the largest difference to the cached final density
of every run (0 = the replay is the same computation). ``--roles-source`` sets ``setup.roles_source`` when the cache
has none (take it from the run log: "set-up PROPOSED" → auto, "set-up read from …" → edited). The cache is copied
to D:/tmp_ideathon/ansys/anchor/ before it is rewritten. Then run ``bracket_day.py … --report-only [--handoff]``.
"""
from __future__ import annotations

import argparse
import pickle
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aerokit.bracket import pipeline  # noqa: E402

ANCHOR = Path("D:/tmp_ideathon/ansys/anchor")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--roles-source", choices=("auto", "edited"))
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--tolerance", type=float, default=1e-3, help="largest accepted |Δx| replay vs cache")
    a = ap.parse_args(argv)
    pk = Path(a.folder) / "study.pkl"
    with pk.open("rb") as f:
        st, opt = pickle.load(f)  # noqa: S301 - our own cache file
    ANCHOR.mkdir(parents=True, exist_ok=True)
    dst = ANCHOR / f"study_{Path(a.folder).name}_{time.strftime('%H%M')}.pkl"
    shutil.copyfile(pk, dst)
    print(f"cache anchored: {dst}")
    ok = True
    if a.replay:
        diff = pipeline.replay_topology(st, opt)
        for tag, d in diff.items():
            print(f"replay topo {tag} %: max |Δx| vs cache {d:.2e}")
        ok = all(d <= a.tolerance for d in diff.values())
        if not ok:
            print(f"RESULT: replay differs from the cache by more than {a.tolerance:g}: cache NOT rewritten")
            return 1
    if a.roles_source and "roles_source" not in st.setup:
        st.setup["roles_source"] = a.roles_source
    with pk.open("wb") as f:
        pickle.dump((st, opt), f)
    print(f"RESULT: cache rewritten ({'snapshots ' if a.replay else ''}roles_source "
          f"{st.setup.get('roles_source', '-')}). NEXT: bracket_day.py … --report-only --case {Path(a.folder).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
