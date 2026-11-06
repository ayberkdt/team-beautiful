"""Competition-day scripts for the 2026 challenges run end to end on their rehearsal cards (figures skipped)."""
import importlib.util
import json
import sys
from pathlib import Path

from aerokit.verification import check, check_true

ROOT = Path(__file__).resolve().parents[1]
CARDS = {"approach": ROOT / "prev_guess" / "03_Advionics" / "cards",
         "easa": ROOT / "prev_guess" / "02_EASA" / "cards",
         "venus": ROOT / "prev_guess" / "04_Venus" / "cards"}
SCRIPT_DIRS = [ROOT / "scripts", *(ROOT / d for d in ("01_Ansys/scripts", "02_EASA/scripts", "prev_guess/03_Advionics/comms_kit_2026-11-05/scripts",
                                                       "04_Venus/scripts", "prev_guess/00_general/scripts",
                                                       "prev_guess/01_Ansys/scripts", "prev_guess/02_EASA/scripts",
                                                       "prev_guess/03_Advionics/scripts"))]


def script_path(name: str) -> Path:
    return next(d / f"{name}.py" for d in SCRIPT_DIRS if (d / f"{name}.py").is_file())


def _load(name: str):
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(name, script_path(name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_approach_day_runs_and_detects_the_spoof():
    m = _load("approach_day")
    card = json.loads((CARDS["approach"] / "approach_rehearsal.json").read_text(encoding="utf-8"))
    card["runs"] = 5
    card["autoland"]["runs"] = 2
    out, _ = m.run(card)
    rows = {r["scenario"]: r for r in out["autoland"]}
    sep = rows["GNSS spoof, solution-separation FDE"]
    check_true("autoland: separation FDE excludes the GNSS and lands in the box",
               sep["excluded_gnss_share"] == 1.0 and sep["in_box_share"] == 1.0)
    check("autoland: fault-free lands in the box", rows["Fault-free, all sensors"]["in_box_share"], 1.0)
    check("five sources in the table", len(out["sources"]), 5)
    check("K at 1e-7 = 5.33", out["k_factor"], 5.33, rtol=2e-3)
    check_true("the monitor alarms after the ramp starts", out["spoof"]["alarm_t_s"] > card["spoof"]["ramp_start_s"])
    check_true("undetected error stays under the computed fault bound",
               out["spoof"]["undetected_error_m"] < out["spoof"]["vertical_fault_bound_m"])
    check_true("markdown renders", "Spoofing ramp" in m.markdown(out))


def test_investigation_day_on_the_fictional_pack():
    m = _load("investigation_day")
    pack = json.loads((CARDS["easa"] / "easa_rehearsal.json").read_text(encoding="utf-8"))
    out, _ = m.analyse(pack, CARDS["easa"])
    ms = out["milestones"]
    check_true("pack is marked fictional", out["fictional"] is True)
    check_true("unstable at 1000 ft: > 150 ft above the path", ms["gate_1000"]["path_excess_ft"] > 150)
    check_true("touchdown far past the threshold (> 900 m)", -ms["touchdown"]["x_m"] > 900)
    check_true("runway excursion detected", out["overrun_m"] > 0 and "runway_end" in ms)
    check_true("ERCS S1 RED from the pack's barriers", out["ercs"]["code"] == "S1" and out["ercs"]["colour"] == "RED")
    times = [e["t"] for e in out["timeline"]]
    check_true("timeline sorted", times == sorted(times))
    check_true("FDM sink-rate event found", any("sink rate" in e["text"] for e in out["timeline"]))


def test_venus_day_ranks_concepts():
    m = _load("venus_day")
    card = json.loads((CARDS["venus"] / "venus_rehearsal.json").read_text(encoding="utf-8"))
    out = m.run(card)
    p = {r["concept"]: r["power_W"] for r in out["concepts"]}
    check_true("helium assistance cuts hover power by > 5x", p["Battery quadrotor"] > 5 * p["Helium-assisted quad"])
    check_true("station keeping costs > 1000x staying aloft", out["station_keeping_W"] > 1000 * min(p.values()))
    check("simulator block per concept", len(out["simulator"]), len(card["concepts"]))
    summary, flight = m.mission(card)
    check("five mission events", len(summary["events"]), len(card["mission"]["steps"]))
    check_true("the 48 km dwell overheats the electronics", summary["time_over_temp_min"] > 0)
    check_true("battery never empty", not summary["brownout"] and summary["battery_min_Wh"] > 0)
