"""Smoke test of the competition-day command 02_EASA/scripts/canopy_day.py (small sample, no figures)."""
import importlib.util
import json
import pathlib

from aerokit.verification import check, check_true

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("canopy_day", ROOT / "02_EASA" / "scripts" / "canopy_day.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_canopy_day_runs_and_reports(tmp_path):
    cfg = json.loads((ROOT / "02_EASA" / "inputs" / "inputs.json").read_text(encoding="utf-8"))
    cfg["n_samples"] = 4000
    inp = tmp_path / "inputs.json"
    inp.write_text(json.dumps(cfg), encoding="utf-8")
    code = _load().main([str(inp), "--no-figures"])
    out = tmp_path / "outputs" / "day"
    rep = (out / "analysis.md").read_text(encoding="utf-8")
    res = json.loads((out / "result.json").read_text(encoding="utf-8"))
    check("exit code without figures", code, 0)
    check_true("all five architectures reported", set(res["architectures"]) == {"A0", "A1", "A2", "A3", "A4"})
    check("seated-only switch misses every partial lock", res["architectures"]["A1"]["miss"]["partial"], 1.0,
          atol=5e-3)
    check_true("A3 better than A2 on a one-bolt hazard",
               res["architectures"]["A3"]["miss"]["one_bolt"] < res["architectures"]["A2"]["miss"]["one_bolt"])
    check_true("ERCS improves with the warning barrier",
               res["ercs"]["takeoff_partial_lock"]["with"]["value"] < res["ercs"]["takeoff_partial_lock"]["without"]["value"])
    check_true("report has every section", all(s in rep for s in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.")))
    check_true("inputs with tags are listed", "| Input | Value | Source | Tag |" in rep)


def test_merge_keeps_distinct_events_with_unpublished_registration(tmp_path, monkeypatch):
    mod = _load()
    hdr = "id,date,registration,aircraft_type,category,country,phase,event,cause_class,warning_fitted,outcome," \
          "aircraft_damage,investigator,report_id,url,page_or_section,tag,notes\n"
    a = tmp_path / "R2_occurrences.csv"
    a.write_text(hdr + "X-1,1999-05-24,unknown,Grob G103,glider,DE,cruise,canopy_opened,unknown,unknown,no_injury,"
                       "minor,BFU,3X076-99,http://a,p1,D-ag,n\n"
                       "X-2,2001-01-01,N1,Grob G103,glider,US,cruise,canopy_opened,unknown,unknown,no_injury,"
                       "minor,NTSB,N1,http://b,p1,D-ag,n\n", encoding="utf-8")
    (tmp_path / "R5_occurrences_add.csv").write_text(
        hdr + "Y-1,1999-05-24,unknown (not published),Grob G103,glider,DE,initial_climb,canopy_opened,unknown,unknown,"
              "no_injury,minor,BFU,3X081-99,http://c,p1,D-ag,n\n"
              "Y-2,2001-01-01,n1,Grob G103,glider,US,cruise,canopy_opened,unknown,unknown,no_injury,minor,NTSB,N1,"
              "http://b,p1,D-ag,duplicate of X-2\n", encoding="utf-8")
    monkeypatch.setattr(mod, "OCC_CSV", a)
    rows = mod.load_occurrences()
    check("two BFU events with unpublished registration kept, one true duplicate dropped", len(rows), 3)
    check_true("families normalised", all(r["family"] == "Grob" for r in rows))
