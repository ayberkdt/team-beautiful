"""How many normal Zurich approaches raise a closure caution without the noise margin (the "43 %" of TECHNICAL.md)?

    python -I 03_Advionics/submission/report_build/false_caution_check.py

Current cue code. Compares the shipped setting with the margin removed. Adds key false_caution to report_numbers.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import report_numbers as rn  # noqa: E402


def main() -> None:
    val = rn.load("validate_real", rn.CASE / "validate_real.py")
    rwy = val._runway_14()
    df = val._load(Path("D:/tmp_ideathon/advionics_data"))
    tr = val._tracks(df, rwy, 1000)
    val._centre(tr, rwy)
    res = {}
    for name, cfg in (("shipped", rn.CueConfig()), ("no_margin", rn.CueConfig(fast_margin=0.0)),
                      ("no_margin_one_frame", rn.CueConfig(fast_margin=0.0, fast_frames=1))):
        fast = caution = 0
        for k, a in enumerate(tr):
            fr = rn.parcue.replay_track(rwy, a["t"], a["x"], a["y"], a["z"], cfg=cfg, seed=k, stop_at_end_state=True)
            fast += any(f["closing_fast"] for f in fr)
            caution += any(f["level"] >= 3 for f in fr)
        res[name] = {"approaches": len(tr), "closing_fast": fast, "caution_or_more": caution}
        print(name, res[name], flush=True)
    p = HERE / "report_numbers.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["false_caution"] = res
    p.write_text(json.dumps(d, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
