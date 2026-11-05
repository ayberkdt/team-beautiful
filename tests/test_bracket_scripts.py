"""Smoke tests of the bracket command-line scripts (outputs redirected to temporary folders)."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_material_report(tmp_path, monkeypatch):
    pytest.importorskip("datawiz")
    mod = load("bracket_material_report")
    monkeypatch.setattr(mod, "OUT", tmp_path)
    assert mod.main([]) == 0
    md = (tmp_path / "material_selection.md").read_text(encoding="utf-8")
    assert "Ti-6Al-4V" in md and "fails" in md
    rows = list(csv.DictReader((tmp_path / "comparison.csv").open(encoding="utf-8")))
    best = min((r for r in rows if r["passes_300C_screen"] == "True"), key=lambda r: float(r["rel_mass_beam_strong_300C"]))
    assert best["key"] == "ti64_lpbf"
    assert (tmp_path / "fig_relative_mass.png").exists()
    assert "0 HATA" in (tmp_path / "fig_relative_mass.denetim.txt").read_text(encoding="utf-8")


def test_crosscheck_script(tmp_path):
    mod = load("bracket_crosscheck")
    setup = {"temperature_C": 300.0, "voxel_mm": 2.0, "holes": [
        {"id": "H1", "axis": "z", "center_mm": [0, 0, 0], "diameter_mm": 8, "segments_mm": [[0, 5]], "role": "support"}]}
    (tmp_path / "setup.json").write_text(json.dumps(setup), encoding="utf-8")
    with (tmp_path / "crosscheck_template.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "unit", "ours", "ansys", "description"])
        w.writerow(["mass_kg", "kg", "1.0", "1.0", ""])
        w.writerow(["max_deformation_mm", "mm", "0.5", "0.4565", ""])
    exp = tmp_path / "export.txt"
    exp.write_text("Node Number\tX Location (mm)\tY Location (mm)\tZ Location (mm)\t"
                   "Equivalent (von-Mises) Stress (MPa)\n1\t2\t0\t1\t900\n2\t30\t0\t1\t120\n", encoding="utf-8")
    assert mod.main([str(tmp_path), "--export", str(exp)]) == 0
    md = (tmp_path / "crosscheck_crosscheck_template.md").read_text(encoding="utf-8")
    assert "temperature" in md and "| von_mises_outside_MPa | — | 120 |" in md


def test_day_report_only_writes_to_out_not_to_the_cached_folder(tmp_path):
    """A copied study.pkl must be re-reported where --out/--case say (it used to overwrite the original folder)."""
    import shutil
    mod = load("bracket_day")
    src = tmp_path / "tiny.json"
    src.write_text(json.dumps({"name": "tiny", "units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [60, 24, 6]},
        {"op": "add", "type": "box", "min": [24, 6, 6], "max": [36, 18, 30]},
        {"op": "cut", "type": "cylinder", "p0": [8, 12, -1], "p1": [8, 12, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [52, 12, -1], "p1": [52, 12, 7], "radius": 4},
        {"op": "cut", "type": "cylinder", "p0": [23, 12, 22], "p1": [37, 12, 22], "radius": 4}]}), encoding="utf-8")
    common = ["--voxel", "2", "--volfracs", "0.5", "--iters", "8", "--no-convergence", "--no-tet", "--no-figures",
              "--magnitude", "500", "--case", "a"]
    assert mod.main([str(src), *common, "--out", str(tmp_path / "A")]) == 0
    first = (tmp_path / "A" / "a" / "report.md").read_text(encoding="utf-8")
    assert "### Bolt loads: FEA vs classical bolt group" in first
    (tmp_path / "B" / "a").mkdir(parents=True)
    shutil.copyfile(tmp_path / "A" / "a" / "study.pkl", tmp_path / "B" / "a" / "study.pkl")
    (tmp_path / "A" / "a" / "report.md").write_text("marker", encoding="utf-8")
    assert mod.main([str(src), *common, "--out", str(tmp_path / "B"), "--report-only"]) == 0
    assert (tmp_path / "A" / "a" / "report.md").read_text(encoding="utf-8") == "marker"
    assert (tmp_path / "B" / "a" / "report.md").read_text(encoding="utf-8") == first.replace(
        str(tmp_path / "A"), str(tmp_path / "B"))


def test_day_stops_on_unknown_material(tmp_path, capsys):
    mod = load("bracket_day")
    src = tmp_path / "plate.json"
    src.write_text(json.dumps({"name": "plate", "units": "mm", "solids": [
        {"op": "add", "type": "box", "min": [0, 0, 0], "max": [40, 20, 6]}]}), encoding="utf-8")
    (tmp_path / "m.csv").write_text("material\nTi-6Al-4V\nAlSi10Mg\n", encoding="utf-8")
    rc = mod.main([str(src), "--materials", str(tmp_path / "m.csv"), "--case", "c", "--out", str(tmp_path / "o")])
    assert rc == 2
    assert "STOPPED" in capsys.readouterr().out
    md = (tmp_path / "o" / "c" / "materials_match.md").read_text(encoding="utf-8")
    assert "| AlSi10Mg | unknown |" in md and "| Ti-6Al-4V | alias |" in md
    assert not (tmp_path / "o" / "c" / "study.pkl").exists()                 # nothing was run on a guess


def test_ansys_rehearsal_catches_every_planted_error(tmp_path):
    from aerokit.bracket import crosscheck
    ours = {"mass_kg": 0.85, "volume_mm3": 108000.0, "max_deformation_mm": 0.134, "load_point_deformation_mm": 0.09,
            "strain_energy_J": 0.114, "compliance_J": 0.229, "max_von_mises_MPa": 167.0,
            "von_mises_outside_MPa": 167.0, "min_safety_factor": 0.98, "retained_volume_fraction": 1.0,
            "reaction_force_N": 2544.0}
    crosscheck.write_template(tmp_path / "crosscheck_template.csv", ours, "synthetic")
    (tmp_path / "setup.json").write_text(json.dumps({"temperature_C": 300.0, "voxel_mm": 2.0, "holes": []}),
                                         encoding="utf-8")
    mod = load("bracket_ansys_rehearsal")
    assert mod.main([str(tmp_path), "--out-root", str(tmp_path / "reh")]) == 0
    md = (tmp_path / "reh" / tmp_path.name / "REHEARSAL_summary.md").read_text(encoding="utf-8")
    assert md.count("| yes |") == 4 and "| NO |" not in md and "FAKE ANSYS DATA" in md
    sc = tmp_path / "reh" / tmp_path.name / "units_m"
    assert json.loads((sc / "REHEARSAL.json").read_text(encoding="utf-8"))["fake_ansys_data"] is True
    assert not (sc / "crosscheck_template.csv").exists()                  # never under the real file name
    assert "FAKE ANSYS DATA" in (sc / "REHEARSAL_fake_ansys_crosscheck_template.csv").read_text(encoding="utf-8")
