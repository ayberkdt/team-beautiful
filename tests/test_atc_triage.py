"""Reveal-day triage: invented task texts rank the intended case first; dry run moves nothing; apply + undo round
trip on a throw-away tree; shared and kept items never move."""
import importlib.util
import json
from pathlib import Path

import pytest

ADV = Path(__file__).resolve().parents[1] / "prev_guess" / "03_Advionics" / "comms_kit_2026-11-05"
spec = importlib.util.spec_from_file_location("triage_mod", ADV / "scripts" / "triage.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
KW = json.loads((ADV / "cases" / "triage_keywords.json").read_text(encoding="utf-8-sig"))
EX = ADV / "cases" / "triage_examples"

EXPECTED = {"task_A_voice.txt": "case_1_voice_to_display", "task_B_lost_comms.txt": "case_2_lost_comms",
            "task_C_radar.txt": "case_3_radar_signal_to_display", "task_D_par.txt": "case_4_par_talkdown",
            "task_E_inspection.txt": "case_6_flight_inspection_ils_drone",
            "task_F_spoofing.txt": "case_8_surveillance_integrity"}


@pytest.mark.parametrize("name,case", sorted(EXPECTED.items()))
def test_examples_rank_intended_case_first(name, case):
    ranked = T.score(T.read_task(str(EX / name)), KW)
    assert ranked[0]["case"] == case and ranked[0]["score"] > 2 * ranked[1]["score"]


def test_par_task_also_keeps_lost_comms():
    ranked = T.score(T.read_task(str(EX / "task_D_par.txt")), KW)
    assert {"case_4_par_talkdown", "case_2_lost_comms"} <= T.decide(ranked, KW)


def test_organiser_note_keeps_voice_lostcomm_radar():
    kept = T.decide(T.score(T.read_task(str(EX / "task_G_organiser_note.txt")), KW), KW)
    assert {"case_1_voice_to_display", "case_2_lost_comms", "case_3_radar_signal_to_display"} <= kept


def test_turkish_and_accents_fold():
    assert T.normalise("İletişim KESİLİRSE") == "iletisim kesilirse"
    r = {x["case"]: x for x in T.score("Kule ile iletişim kesilirse", KW)}
    assert r["case_2_lost_comms"]["matches"].get("kesil*") == 1


def test_no_match_keeps_everything():
    ranked = T.score("lorem ipsum dolor", KW)
    assert T.decide(ranked, KW) == set(KW["cases"])


def test_keep_and_drop_overrides():
    ranked = T.score(T.read_task(str(EX / "task_A_voice.txt")), KW)
    kept = T.decide(ranked, KW, keep=["case_7_readback_correlation"], drop=["case_1_voice_to_display"])
    assert "case_7_readback_correlation" in kept and "case_1_voice_to_display" not in kept


def _fake_tree(root: Path) -> None:
    for case in KW["cases"]:
        (root / "cases" / case).mkdir(parents=True)
        (root / "cases" / case / "run.py").write_text("# stub\n", encoding="utf-8")
    (root / "cases" / "_common.py").write_text("# shared\n", encoding="utf-8")
    (root / "outputs").mkdir()
    for f in ("F1_wrong_values_vs_snr.png", "F3_psr_pd_vs_range.png", "scope_demo.html", "report.md",
              "F7_guidance_needle.png"):
        (root / "outputs" / f).write_text("x", encoding="utf-8")
    for d in ("docs", "research", "scripts", "templates", "submission"):
        (root / d).mkdir()
        (root / d / "keep.txt").write_text("x", encoding="utf-8")


def test_plan_apply_undo_round_trip(tmp_path):
    root = tmp_path / "03_Advionics"
    _fake_tree(root)
    kept = {"case_3_radar_signal_to_display"}
    pl = T.plan(root, KW, kept)
    moving = {m["path"] for m in pl["move"]}
    assert "cases/case_1_voice_to_display" in moving and "outputs/F1_wrong_values_vs_snr.png" in moving
    assert "cases/case_3_radar_signal_to_display" not in moving
    assert "outputs/scope_demo.html" not in moving                 # claimed by kept case 3 (and case 8)
    assert "outputs/F3_psr_pd_vs_range.png" not in moving
    assert not any(p.startswith(("docs", "research", "scripts", "templates", "submission", "cases/_common"))
                   or p == "outputs/report.md" for p in moving)
    dest = tmp_path / "prev_guess" / "03_Advionics" / "2026-11-06_unused"
    man = T.apply(root, pl, dest, "task")
    assert not (root / "cases" / "case_1_voice_to_display").exists()
    assert (dest / "cases" / "case_1_voice_to_display" / "run.py").exists()
    assert (root / "outputs" / "report.md").exists() and (root / "docs" / "keep.txt").exists()
    doc = json.loads(man.read_text(encoding="utf-8"))
    assert len(doc["moves"]) == len(moving)
    with pytest.raises(SystemExit):
        T.apply(root, pl, dest, "again")                            # destination exists -> refuse
    assert T.undo(man) == len(moving)
    assert (root / "cases" / "case_1_voice_to_display" / "run.py").exists()
    assert (root / "outputs" / "F1_wrong_values_vs_snr.png").exists()


def test_cli_dry_run_moves_nothing(tmp_path, capsys):
    root = tmp_path / "03_Advionics"
    _fake_tree(root)
    before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
    rc = T.main([str(EX / "task_C_radar.txt"), "--root", str(root), "--dest", str(tmp_path / "dest")])
    assert rc == 0
    after = sorted(str(p.relative_to(root)) for p in root.rglob("*") if not p.name.startswith("triage_plan"))
    assert before == after and not (tmp_path / "dest").exists()
    plan = json.loads((root / "triage_plan.json").read_text(encoding="utf-8"))
    assert plan["ranking"][0]["case"] == "case_3_radar_signal_to_display"
    out = capsys.readouterr().out
    assert "dry run" in out.splitlines()[-1] and "--apply" in out.splitlines()[-1]


def test_default_dest_never_reuses_a_folder(tmp_path):
    a = T.default_dest(tmp_path, "2026-11-06")
    a.mkdir(parents=True)
    b = T.default_dest(tmp_path, "2026-11-06")
    assert a != b and b.name == "2026-11-06_unused_2"
