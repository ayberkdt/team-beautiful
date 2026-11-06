"""Every case runner runs (quick, no figure) into a temporary folder, writes result.md + params_used.json, and keeps
its safety invariants; parameter overrides work and unknown names are refused."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIRS = [ROOT / "03_Advionics" / "cases", ROOT / "prev_guess" / "03_Advionics" / "comms_kit_2026-11-05" / "cases"]
CASES = {p.name: p for d in DIRS for p in d.iterdir() if p.is_dir() and (p / "run.py").exists()}
NAMES = sorted(CASES)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"caserun_{name}", CASES[name] / "run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ten_cases_present_with_case_md_and_params():
    assert len(NAMES) == 10
    for n in NAMES:
        assert (CASES[n] / "CASE.md").exists(), n
        spec = json.loads((CASES[n] / "params.json").read_text(encoding="utf-8-sig"))
        for k, v in spec["params"].items():
            assert {"value", "unit", "source"} <= set(v), (n, k)
            assert v["source"], (n, k)


@pytest.mark.parametrize("name", NAMES)
def test_case_runs_quick(name, tmp_path):
    res = _load(name).main(["--quick", "--no-fig", "--out", str(tmp_path)])
    md = (tmp_path / "result.md").read_text(encoding="utf-8")
    assert "## Key numbers" in md and "## Parameters used" in md
    used = json.loads((tmp_path / "params_used.json").read_text(encoding="utf-8"))
    assert used["params"]
    assert len(res["key"]) == 3


def test_case1_invariant_conservative_not_worse(tmp_path):
    r = _load("case_1_voice_to_display").main(["--quick", "--no-fig", "--out", str(tmp_path)])
    assert sum(x["c_wrong"] for x in r["rows"]) <= sum(x["n_wrong"] for x in r["rows"])


def test_case2_nothing_unreceived_is_shown(tmp_path):
    r = _load("case_2_lost_comms").main(["--no-fig", "--out", str(tmp_path)])
    assert r["violations"] == 0 and r["not_stale"] == 0
    assert {"RX_LOST", "ALTERNATE_AVAILABLE", "ALL_COMMS_LOST", "TX_LOST", "DEGRADED"} <= set(r["first"])


def test_case2_rule_set_override(tmp_path):
    _load("case_2_lost_comms").main(["--no-fig", "--out", str(tmp_path), "--set", "rule_set=US_14CFR_91_185"])
    md = (tmp_path / "result.md").read_text(encoding="utf-8")
    assert "no fixed hold" in md and "rule_set = \"US_14CFR_91_185\"" in md


def test_case3_no_wrong_message(tmp_path):
    r = _load("case_3_radar_signal_to_display").main(["--quick", "--no-fig", "--out", str(tmp_path)])
    assert sum(x["counts"]["wrong"] for x in r["ber"]["rows"]) == 0


def test_case4_never_extrapolates(tmp_path):
    r = _load("case_4_par_talkdown").main(["--no-fig", "--out", str(tmp_path)])
    assert r["t_lost"] is not None and r["extrapolated"] == 0


def test_case6_faults_flagged_never_centred(tmp_path):
    r = _load("case_6_flight_inspection_ils_drone").main(["--quick", "--no-fig", "--out", str(tmp_path)])
    assert r["flagged_fault"] == r["n_fault"] > 0 and r["centred"] == 0 and r["false_flag"] == 0
    bad = _load("case_6_flight_inspection_ils_drone").main(["--quick", "--no-fig", "--out", str(tmp_path),
                                                             "--set", "aid_bias_ddm=0.02"])
    assert bad["verdict"] == "FAIL"


def test_case8_spoofed_crc_valid_and_large_offset_flagged(tmp_path):
    r = _load("case_8_surveillance_integrity").main(["--quick", "--no-fig", "--out", str(tmp_path)])
    assert r["spoof_crc_valid"] is True
    assert r["rows"][-1]["flag_pct"] > 95 and r["false_alarm_pct"] < 5


def test_case9_crc_and_panel(tmp_path):
    r = _load("case_9_guidance_uplink").main(["--quick", "--no-fig", "--out", str(tmp_path)])
    assert r["undetected"] == 0 and r["corrupted"] > 0
    assert r["lost_frames"] > 0 and r["removed"] >= r["lost_frames"]


def test_unknown_parameter_refused(tmp_path):
    with pytest.raises(SystemExit):
        _load("case_1_voice_to_display").main(["--no-fig", "--out", str(tmp_path), "--set", "nonsense=1"])


def test_params_file_override(tmp_path):
    f = tmp_path / "mentor.json"
    f.write_text(json.dumps({"snr_db": [25], "n_per_snr": 20}), encoding="utf-8")
    r = _load("case_1_voice_to_display").main(["--no-fig", "--out", str(tmp_path), "--params", str(f)])
    assert [x["snr"] for x in r["rows"]] == [25]


def test_case2_never_ok_without_carrier(tmp_path):
    r = _load("case_2_lost_comms").main(["--no-fig", "--out", str(tmp_path)])
    assert r["ok_without_carrier"] == 0 and "NO_SIGNAL" in r["first"]
    assert r["nosig_t"] < r["loss_t"]
    old = _load("case_2_lost_comms").main(["--no-fig", "--out", str(tmp_path), "--set", "no_signal_after_s=null"])
    assert old["ok_without_carrier"] > 0                                     # the gap the new state closes
