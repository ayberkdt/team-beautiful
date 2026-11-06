"""Rehearsal of "the Ansys result arrives": fake Ansys numbers with one deliberate error each, run through the real
cross-check, and check that its verdict line names the planted error.

    python 01_Ansys/scripts/bracket_ansys_rehearsal.py 01_Ansys/outputs/cases/sketch

Writes 01_Ansys/outputs/rehearsal_crosscheck/<case>/<scenario>/ — deliberately NOT in outputs/cases/ or handoff/ and
never under the real file names (the film treats a filled crosscheck_template*.csv or crosscheck.json in a hand-off
as a real Ansys result): REHEARSAL_fake_ansys_crosscheck_template.csv (every description starts "FAKE ANSYS DATA"),
REHEARSAL.json ({"fake_ansys_data": true, ...}), copies of setup.json/result.json and the cross-check report; summary
rehearsal_crosscheck/<case>/REHEARSAL_summary.md. Scenarios (factors applied to OUR numbers of the initial design,
so the fake is plausible):

* ``correct``        — mesh-level differences only (T10 vs SOLID187: deformation +2 %, stress +6 %): must AGREE;
* ``units_m``        — deformations typed in metres into the mm column (× 1/1000): must name "units";
* ``wrong_support``  — one bolt support left out (softer: deformation and energy × 2.3, stress × 1.7): must name
                       "boundary conditions";
* ``room_temperature`` — Mechanical left at 22 °C (deformation and energy × E(T)/E(22 °C)): must name "temperature".
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import shutil
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())  # repo root
sys.path.insert(0, str(ROOT / "src"))

from aerokit.bracket import crosscheck, matdata  # noqa: E402

CSV = "REHEARSAL_fake_ansys_crosscheck_template.csv"
DEF = ("max_deformation_mm", "load_point_deformation_mm", "strain_energy_J", "compliance_J")
STRESS = ("max_von_mises_MPa", "von_mises_outside_MPa")


def scenarios(T: float) -> dict[str, tuple[dict[str, float], str]]:
    base = matdata.get("structural_steel")
    kE = base.E_at(T) / base.E.value
    mesh = {**{k: 1.02 for k in DEF}, **{k: 1.06 for k in STRESS}, "min_safety_factor": 1 / 1.06}
    return {
        "correct": (mesh, "AGREES"),
        "units_m": ({**mesh, "max_deformation_mm": 1.02e-3, "load_point_deformation_mm": 1.02e-3}, "units"),
        "wrong_support": ({**{k: 2.3 for k in DEF}, **{k: 1.7 for k in STRESS}, "min_safety_factor": 1 / 1.7},
                          "boundary conditions"),
        "room_temperature": ({**mesh, **{k: kE for k in DEF}}, "temperature"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="a bracket_day output folder (setup.json, result.json, crosscheck_template.csv)")
    ap.add_argument("--out-root", default=str(ROOT / "01_Ansys" / "outputs" / "rehearsal_crosscheck"))
    a = ap.parse_args(argv)
    folder = Path(a.folder)
    ours, _ = crosscheck.read_template(folder / "crosscheck_template.csv")
    import json
    T = json.loads((folder / "setup.json").read_text(encoding="utf-8")).get("temperature_C", 300.0)
    spec = importlib.util.spec_from_file_location("bracket_crosscheck", ROOT / "01_Ansys" / "scripts" / "bracket_crosscheck.py")
    cc = importlib.util.module_from_spec(spec)            # type: ignore[arg-type]
    spec.loader.exec_module(cc)                            # type: ignore[union-attr]
    lines = ["# REHEARSAL — FAKE ANSYS DATA: one planted error per scenario\n",
             f"Folder `{folder}`; fake Ansys numbers = ours × the factors below; verdict from "
             "`01_Ansys/scripts/bracket_crosscheck.py`.\n", "| Scenario | Planted | Expected in verdict | Verdict | Caught |",
             "|---|---|---|---|---|"]
    ok_all = True
    for name, (fac, expect) in scenarios(T).items():
        d = Path(a.out_root) / folder.name / name
        d.mkdir(parents=True, exist_ok=True)
        for f in ("setup.json", "result.json"):
            if (folder / f).exists():
                shutil.copyfile(folder / f, d / f)
        rows = list(csv.reader((folder / "crosscheck_template.csv").read_text(encoding="utf-8").splitlines()))
        for r in rows[1:]:
            o = ours.get(r[0])
            if o is not None:
                r[3] = f"{o * fac.get(r[0], 1.0):.6g}"
            r[4] = f"FAKE ANSYS DATA (rehearsal '{name}'): {r[4]}"
        with (d / CSV).open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows(rows)
        (d / "REHEARSAL.json").write_text(json.dumps({"fake_ansys_data": True, "scenario": name,
                                                      "planted_factors": fac, "source_folder": str(folder)},
                                                     indent=1), encoding="utf-8")
        buf = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")      # the script writes UTF-8 to stdout.buffer
        with redirect_stdout(buf):
            cc.main([str(d), "--csv", CSV])
        buf.flush()
        text = buf.buffer.getvalue().decode("utf-8")                # type: ignore[attr-defined]
        v = next((ln[8:] for ln in text.splitlines() if ln.startswith("RESULT: ")), "no RESULT line")
        caught = (v.startswith("AGREES:") if expect == "AGREES" else
                  (v.startswith("DISCREPANCY") or "BUT" in v) and expect in v)
        ok_all &= caught
        planted = ", ".join(f"{k} × {fac[k]:.3g}" for k in sorted(fac) if abs(fac[k] - 1) > 1e-9 and
                            not (name != "correct" and fac[k] in (1.02, 1.06, 1 / 1.06))) or "mesh differences only"
        lines.append(f"| {name} | {planted} | {expect} | {v} | {'yes' if caught else 'NO'} |")
        print(f"{name:17} {'caught' if caught else 'MISSED'}: {v}")
    summ = Path(a.out_root) / folder.name / "REHEARSAL_summary.md"
    summ.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"RESULT: {'all planted errors caught' if ok_all else 'a planted error was MISSED'} -> {summ}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
