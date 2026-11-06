"""Adds the ring pilot to the like-for-like comparison with Zurich (start on the path, no steady wind, A320 speed).

    python -I 03_Advionics/submission/report_build/report_numbers_ring.py

Run after report_numbers.py. Adds key sim.on_path_ring to report_numbers.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import report_numbers as rn  # noqa: E402


def main() -> None:
    exp = rn.load("par_visual_export", rn.ROOT / "03_Advionics" / "scripts" / "par_visual_export.py")
    rc = rn.ReplayConfig(aircraft=rn.AIRCRAFT["A320"], start_range_nm=5.0, start_offset_m=0.0, start_above_m=0.0)
    logic = rn.parcue.CueLogic
    rn.parcue.CueLogic = exp._Recording
    runs = []
    for s in range(rn.N):
        exp._Recording.log, exp._Recording.state_log, exp._Recording.drift_deg = [], {}, None
        exp._Recording.pilot = exp.RingPilot()
        runs.append(rn.fly_replay(rn.RWY, rn.CueConfig(), rc, pilot=exp._Recording.pilot, seed=s))
    base = []
    for s in range(rn.N):
        exp._Recording.log, exp._Recording.state_log, exp._Recording.drift_deg = [], {}, None
        exp._Recording.pilot = exp.RingPilot()
        base.append(rn.fly_replay(rn.RWY, rn.CueConfig(), rn.BASE, pilot=exp._Recording.pilot, seed=s))
    rn.parcue.CueLogic = logic
    p = HERE / "report_numbers.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["sim"]["on_path_ring"] = rn.sim_stats(runs)
    d["figure"]["ring_y"], d["figure"]["ring_z"] = rn.bands(base, "y_m"), rn.bands(base, "z_dev_m")
    p.write_text(json.dumps(d, indent=1), encoding="utf-8")
    print(json.dumps(d["sim"]["on_path_ring"]))


if __name__ == "__main__":
    main()
