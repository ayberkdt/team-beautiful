"""CLI: every command runs, exits 0 and ends with one 'Result:' line and one 'Next step:' line
(ux-yasalari peak-end); --format/--out produce the same report in other formats.

argparse errors raise SystemExit; they are caught here so that one bad command cannot stop the run.
"""
import contextlib
import io
import json
import pathlib
import tempfile

import pytest

from aerokit.data import DATA_DIR, EXAMPLES_DIR
from aerokit.verification import check, check_true


def _run(argv):
    from aerokit.cli.main import main as cli
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            cli(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            if isinstance(e.code, str):          # the interpreter prints this only at top level
                err.write(e.code + "\n")
    return code, out.getvalue().strip().splitlines(), err.getvalue()


def _commands(d):
    cad = DATA_DIR / "examples" / "cad"
    return [
        ["aero", "isa"],
        ["aero", "flow", "--U", "20", "--L", "0.25"],
        ["aero", "flow", "--U", "20", "--L", "0.25", "--surface", "200000"],
        ["geometry", "airfoil", "--naca", "0012"],
        ["geometry", "planform", "--S", "27.5", "--AR", "9"],
        ["geometry", "cad", str(cad / "box.stl"), "--material", "6061-T6"],
        ["mechanics", "tensor", "--s", "100", "0", "0", "20", "--material", "7075-t6"],
        ["mechanics", "wing", "--mass", "1000", "--b", "10", "--c-root", "1.2", "--c-tip", "0.8", "--box-b", "0.5",
         "--box-h", "0.15", "--t-skin", "0.002", "--t-spar", "0.003", "--material", "6061-T6"],
        ["mechanics", "section", "--shape", "I", "--dimension", "0.1", "0.01", "0.2", "0.006"],
        ["mechanics", "section", "--shape", "dxf", "--dxf", str(cad / "profile_L.dxf")],
        ["mechanics", "buckling", "--kind", "column", "--material", "7075-T6", "--I", "2e-8", "--A", "2e-4",
         "--L", "0.8"],
        ["mechanics", "buckling", "--kind", "plate", "--material", "2024-T351", "--a-b", "3", "--t", "0.002",
         "--b", "0.15"],
        ["mechanics", "buckling", "--kind", "cylinder", "--material", "7075-T6", "--r", "0.5", "--t", "0.002"],
        ["mechanics", "vessel", "--kind", "cylinder", "--material", "7075-T6", "--ri", "0.05", "--ro", "0.08",
         "--p", "60"],
        ["mechanics", "vessel", "--kind", "disk", "--material", "Ti-6Al-4V", "--rpm", "20000", "--b", "0.2",
         "--a", "0.03"],
        ["mechanics", "life", "--kind", "fatigue", "--sa", "100", "--sm", "50", "--Se", "200", "--Sut", "500"],
        ["mechanics", "life", "--kind", "crack", "--Kc", "30", "--sigma", "150", "--W", "0.2", "--C", "1e-11",
         "--dsigma", "100"],
        ["mechanics", "joint", "--P", "3000", "--d", "0.005", "--t", "0.002", "--w", "0.02", "--e", "0.01",
         "--Fbru", "800", "--Fsu", "330", "--material", "2024-T351"],
        ["composite", "lamina", "--sequence", "0,90,s", "--N", "1e5", "0", "0", "--material", "as4 8552"],
        ["composite", "failure", "--sequence", "0,45,-45,90,s", "--material", "IM7-8552"],
        ["composite", "layup", "--material", "IM7-8552", "--n-stack", "4", "--load", "1", "0.5"],
        ["fem", "example"],
        ["fem", "example", "cantilever_frame"],
        ["fem", "solve", str(EXAMPLES_DIR / "plate_q8.json"), "--plot", str(pathlib.Path(d) / "plate")],
        ["fem", "convergence", str(EXAMPLES_DIR / "plate_q8.json")],
        ["fem", "topology", "--nelx", "30", "--nely", "10", "--rmin", "1.5", "--plot", str(pathlib.Path(d) / "topo")],
        ["fem", "optimum", str(EXAMPLES_DIR / "truss_bridge.json"), "--tension", "150", "--disp-node", "2",
         "--disp-limit", "0.01", "--plot", str(pathlib.Path(d) / "truss_opt")],
        ["sizing", "raymer"],
        ["sizing", "point"],
        ["sizing", "box", "--mass", "5974", "--n", "3.14", "--b", "15.73", "--c-root", "2.33", "--c-tip", "1.17",
         "--regions", "3"],
        ["sizing", "vn", "--mass", "5974", "--S", "27.5", "--c", "1.81", "--CLmax", "2.0", "--CLa", "5.2",
         "--plot", str(pathlib.Path(d) / "vn")],
        ["sizing", "design", str(EXAMPLES_DIR / "design" / "ansys_2023_requirements.json"), "--no-figures",
         "--out-dir", str(pathlib.Path(d) / "design")],
        ["sizing", "validate"],
        ["sizing", "mission", str(EXAMPLES_DIR / "design" / "ansys_2023_mission.json"), "--requirements",
         str(EXAMPLES_DIR / "design" / "ansys_2023_requirements.json"), "--out-dir", str(pathlib.Path(d) / "mission"),
         "--no-figures"],
        ["sizing", "mission", str(EXAMPLES_DIR / "design" / "ansys_2023_mission_polygon_wind.json"), "--requirements",
         str(EXAMPLES_DIR / "design" / "ansys_2023_requirements.json"), "--optimize", "--no-figures"],
        ["materials", "list"],
        ["materials", "list", "--handbook"],
        ["materials", "allowable", "7075-T6", "--thickness", "2"],
        ["materials", "allowable", "al-7050-t7451", "--basis", "b", "--direction", "lt", "--thickness", "50"],
        ["materials", "curve", "7075-T6", "--thickness", "2"],
    ]


def test_commands_run_and_end_with_next_step():
    d = tempfile.mkdtemp(prefix="aerokit_cli_")
    for k in _commands(d):
        code, rows, err = _run(k)
        name = " ".join(x for x in k[:3] if not x.startswith(("-", "/", "\\")) and ":" not in x)
        check_true(f"CLI '{name}': exit code 0", code == 0, f"code {code}: {err.strip()[-300:]}")
        check_true(f"CLI '{name}': last line is 'Next step'", bool(rows) and rows[-1].startswith("Next step:"),
                   rows[-1] if rows else "no output")
        check_true(f"CLI '{name}': exactly one 'Result:' line", sum(r.startswith("Result:") for r in rows) == 1,
                   str(sum(r.startswith("Result:") for r in rows)))


def test_figures_are_listed_and_audited():
    d = tempfile.mkdtemp(prefix="aerokit_cli_fig_")
    code, rows, _ = _run(["sizing", "vn", "--mass", "5974", "--S", "27.5", "--c", "1.81", "--plot",
                          str(pathlib.Path(d) / "vn")])
    check_true("CLI figure: file line printed", any(r.startswith("File:") and r.endswith("vn.png") for r in rows))
    check_true("CLI figure: audit line says 0 errors", any("datawiz audit: 0 error(s)" in r for r in rows))
    check_true("CLI figure: PNG exists", (pathlib.Path(d) / "vn.png").exists())


def test_output_formats():
    code, rows, _ = _run(["aero", "isa", "--h", "0", "1000", "--format", "json"])
    data = json.loads("\n".join(rows))
    check("CLI json: exit code", code, 0)
    check("CLI json: two table rows", len(data["tables"][0]["rows"]), 2)
    check_true("CLI json: result present", data["result"].startswith("At 1000 m"))
    code, rows, _ = _run(["aero", "isa", "--format", "md"])
    check_true("CLI md: Markdown table with right-aligned numbers", any(r.startswith("|:---|---:") for r in rows))
    code, rows, _ = _run(["aero", "isa", "--format", "csv"])
    check_true("CLI csv: header row", rows[0].startswith("h (m),T (K)"), rows[0])
    d = pathlib.Path(tempfile.mkdtemp(prefix="aerokit_cli_out_"))
    for ext, probe in ((".md", "**Result:**"), (".json", '"next_step"'), (".txt", "Next step:")):
        code, rows, _ = _run(["aero", "isa", "--out", str(d / f"report{ext}")])
        text = (d / f"report{ext}").read_text(encoding="utf-8")
        check_true(f"CLI --out {ext}: file written in the format of its extension", probe in text)
        check_true(f"CLI --out {ext}: confirmation line", rows and rows[-1].startswith("Report written:"))


def test_hick_budget():
    """Hick budget: ≤ 7 top-level groups, ≤ 7 commands per group."""
    from aerokit.cli.main import build_parser
    p = build_parser()
    top = next(a for a in p._actions if a.__class__.__name__ == "_SubParsersAction")
    check_true("CLI top-level groups ≤ 7", len(top.choices) <= 7, str(list(top.choices)))
    check("CLI top-level groups", len(top.choices), 7, source="ux-yasalari Hick")
    for name, sub in top.choices.items():
        acts = [a for a in sub._actions if a.__class__.__name__ == "_SubParsersAction"]
        n = len(acts[0].choices) if acts else 0
        check_true(f"CLI '{name}' commands ≤ 7", n <= 7, f"{n}: {list(acts[0].choices) if acts else []}")


@pytest.mark.parametrize("argv", [
    ["mechanics", "buckling", "--kind", "column"],                 # missing flags
    ["geometry", "cad", "does_not_exist.step"],                    # STEP / missing file
    ["materials", "allowable", "7075-T6", "--thickness", "999"],   # outside the tabulated range
    ["materials", "allowable", "unobtainium"],
    ["composite", "lamina", "--sequence", "0,abc", "--material", "IM7-8552"],
    ["aero", "isa", "--out", "report.exe"],                        # unsafe output suffix
    ["fem", "example", "../../secrets"],                           # path traversal through example names
])
def test_bad_input_gives_clean_one_line_error(argv):
    code, _, err = _run(argv)
    assert code != 0
    assert "Traceback" not in err
    lines = [line for line in err.strip().splitlines() if line]
    assert lines and (lines[-1].startswith("Error (") or "error:" in lines[-1]), err
