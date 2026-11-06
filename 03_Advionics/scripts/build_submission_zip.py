"""Build the Advionics submission zip: mock-up stills, stand-alone code, results. The report is sent separately.

Run again after any change to the cue code:

    python 03_Advionics/scripts/build_submission_zip.py

The zip code is a copy of ``src/aerokit/atc``. Only imports and comments change. The script checks this by comparing the
syntax trees, so the zip cannot drift from the tested code. Nothing from the organisers or third parties goes in.
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADV = ROOT / "03_Advionics"
CASE = ADV / "cases" / "case_10_par_hybrid_cue"
OUT = ADV / "submission" / "Team_Beetiful_Advionics.zip"
STAGE = ADV / "submission" / "_zip_stage"
TOP = "Team_Beetiful_Advionics"

STILLS = {
    "par-takip": "01_Start_off_path",
    "par-pilot": "02_Deviation_shown_voice_quiet",
    "par-tunel": "03_On_path_quiet",
    "par-bgecik": "04_Data_delayed",
    "par-ses": "05_Bad_data_rejected",
    "par-clost": "06_Radar_contact_lost",
    "par-esik": "07_Below_DH_advisory_only",
}
MODULES = ("parradar", "parflight", "parcue", "cue_intensity", "voice_arbiter")

RUNWAY = '''"""Landing runway and nominal glidepath. The only parts of the team toolkit that the cue needs."""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True)
class Runway:
    """Landing runway: threshold position, true course, length, glidepath angle and threshold crossing height."""

    lat: float
    lon: float
    elevation: float
    course_deg: float
    length: float = 2500.0
    glide_path_deg: float = 3.0
    tch: float = 15.24                # 50 ft

    @property
    def gpip(self) -> float:
        """Along-track coordinate of the glidepath intercept point [m] (negative: beyond the threshold)."""
        return -self.tch / math.tan(math.radians(self.glide_path_deg))


def glide_path_height(rwy: Runway, x: ArrayLike) -> np.ndarray:
    """Height of the nominal path above the threshold plane at along-track ``x`` [m]."""
    return rwy.tch + np.asarray(x, float) * math.tan(math.radians(rwy.glide_path_deg))
'''

RUN_CHECK = '''"""Repeat the main simulation result of the report: 100 runs for the heading target, the ring and no cue.

Needs Python 3.10 or later and NumPy. Takes less than one minute. Run: python run_check.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from par_cue.parcue import PilotModel, ReplayConfig, dh_frame, fly_replay  # noqa: E402
from par_cue.ring import fly_ring  # noqa: E402
from par_cue.runway import Runway  # noqa: E402

RUNS = 100
runway = Runway(51.0, 4.0, 10.0, 250.0)       # synthetic runway
start = ReplayConfig(start_range_nm=5.0, start_offset_m=150.0, start_above_m=30.0, crosswind_ms=3.0)



def report(name, frames):
    reached = [f for f in frames if f is not None]
    print(f"{name}: {len(reached)} of {RUNS} runs reach decision height, 95 % error "
          f"{np.percentile([abs(f['y_m']) for f in reached], 95):.0f} m lateral, "
          f"{np.percentile([abs(f['z_dev_m']) for f in reached], 95):.0f} m vertical")


report("Heading target", [dh_frame(fly_replay(runway, rc=start, seed=s)) for s in range(RUNS)])
report("Marker into ring", [dh_frame(fly_ring(runway, start, s)) for s in range(RUNS)])
report("No cue", [dh_frame(fly_replay(runway, rc=start, pilot=PilotModel(follows_cue=False), seed=s)) for s in range(RUNS)])
'''

README = """TEAM BEETIFUL - ADVIONICS CHALLENGE
Automated Precision Approach Guidance (HYBRID direction)

This is an educational concept on simulated and recorded data.
It is not approved or ready for operational flight use.


WHAT THE SYSTEM DOES

Radar data goes in. A cue for the pilot comes out.
The display is always on. The voice speaks only for important changes.
The pilot decides. The cue gives no turn or descend command.


WHAT IS IN THIS FOLDER

1_Report    The final report. Start here.
2_Mock_Up   Link to the 3D mock-up, and seven frames from it in the order of an approach.
3_Code      The cue logic, and run_check.py to repeat the main result.
4_Results   The result tables behind the report.


HOW TO RUN THE CODE

Python 3.10 or later and NumPy are necessary.

    cd 3_Code
    python run_check.py

The result must be:

    Heading target     99 of 100 runs reach decision height, 37 m lateral, 11 m vertical
    Marker into ring   99 of 100 runs reach decision height, 11 m lateral, 9 m vertical
    No cue             1 of 100 runs reach decision height

File guide for 3_Code/par_cue:

    parradar.py        radar model: plots with the errors that ICAO Annex 10 allows
    parflight.py       aircraft, wind, turbulence and pilot models
    parcue.py          filter, validity gate, heading target, fault states, replay
    ring.py            the ring, and the pilot who flies the marker into it
    cue_intensity.py   alert levels: quiet, advise, caution, warning
    voice_arbiter.py   voice priority below aircraft alerts
    runway.py          runway and nominal glidepath

In the code comments, [Y] marks a design value of the team. No pilot has tested these values.


WHAT IS NOT IN THIS FOLDER

The recorded Zurich tracks are a public data set. The report gives the source.
The 3D mock-up files are on Google Drive. 2_Mock_Up/README_Mock_Up.txt gives the link.
"""


MOCK_UP = """TEAM BEETIFUL - ADVIONICS CHALLENGE
3D mock-up of the approach

Link: https://drive.google.com/drive/folders/1vXZVjsg9lOGdv8gbPPw4od2-peA1_nTQ

The Stills folder has seven frames from the mock-up, in the order of an approach.
This is an educational concept on simulated data. It is not approved or ready for operational flight use.
"""


def clean(name: str, text: str) -> str:
    """Point the imports at the stand-alone package and remove references to files that are not in the zip."""
    text = text.replace("go_around", "missed_approach")
    text = re.sub(r"from aerokit\.approach import", "from par_cue.runway import", text)
    text = re.sub(r"from aerokit\.atc\.(\w+) import", r"from par_cue.\1 import", text)
    fixed = [
        (r"Evidence: ``03_Advionics/research/[^\n]*\n\(models\)\.\n", ""),
        (r" \(read in ``03_Advionics/research/[^`]*``\)", ""),
        (r"Sources are read in ``[^`]*`` and ``[^`]*``:", "Sources:"),
        (r" \(evidence in ``[^`]*``\)", ""),
        (r"The formula with height weight, trend term and sound ladder is in ``03_Advionics/complex/``\. ", ""),
        (r" Same-meaning\nfiltering and hold timers are in ``03_Advionics/complex/``\.", ""),
        (r"\[Y\] R5 B4: ", "[Y] "),
        (r"\[Y\] R2 1\.4 used ", "[Y] "),
        (r", R5 assumes ", ", assumed "),
        (r", R2 1\.4\b", ""),
        (r", R[2-6] [A-Z0-9.]+\)", ")"),
        (r",? ?\((?:R[2-6][^()\n]*)\)", ""),
        (r' \(not "or", an error in our earlier note\)', ""),
        (r" Three designs that used it failed in\n  closed loop on 6 Nov, including a drift estimate from a 10 s track \(2-3 deg of noise at 5 NM\)\.", ""),
        (r"300 real approaches", "300 recorded tracks"),
        (r"needle: 2 dots", "diamond: 2 dots"),
        (r"remove the needle", "remove the diamond"),
        (r"needles only", "diamonds only"),
        (r"Needles stay true", "Diamonds stay true"),
        (r"PAR needle noise", "PAR plot noise"),
    ]
    for pattern, new in fixed:
        text = re.sub(pattern, new, text)
    left = re.findall(r".*(?:\bR[2-6]\b|03_Advionics|earlier note|failed in|real approaches|go_around).*", text)
    if left:
        raise SystemExit(f"{name}: references left:\n" + "\n".join(left))
    return text


def same_code(a: str, b: str) -> bool:
    """True if two sources differ only in docstrings, comments and import paths."""
    def tree(src: str) -> str:
        t = ast.parse(src)
        for node in ast.walk(t):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(("aerokit", "par_cue")):
                node.module = "x"
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and ast.get_docstring(node) is not None:
                node.body = node.body[1:] or [ast.Pass()]
        return ast.dump(t)
    return tree(a.replace("go_around", "missed_approach")) == tree(b)


def section(text: str, title: str) -> str:
    return re.search(rf"^## {re.escape(title)}.*?(?=^## |\Z)", text, re.M | re.S).group(0).strip()


def results() -> str:
    src = (CASE / "outputs" / "result.md").read_text(encoding="utf-8")
    val = json.loads((CASE / "outputs" / "validation.json").read_text(encoding="utf-8"))
    hold = json.loads((CASE / "outputs" / "validation_holdout.json").read_text(encoding="utf-8"))
    ring = json.loads((ADV / "submission" / "report_build" / "report_numbers.json").read_text(encoding="utf-8"))["ring"]["baseline"]
    runs = section(src, "Monte Carlo").replace("minimums", "reached_DH").replace("Baseline pilot", "Heading target").replace("## Monte Carlo (seeds 0 to n-1, same start and wind)",
                                                                                  "## Simulation: 100 runs for each case, same start and wind")
    faults = section(src, "Fault reaction").replace("## Fault reaction (scenario B and C faults, all seeds)", "## Fault reaction: 100 runs")
    jumps = section(src, "Smallest radar jump caught")
    z = val["zurich_replay_detection_95"]
    peak = z["peak_level"] if isinstance(z, dict) and "peak_level" in z else None
    first = "| First 1000 | " + " | ".join(str(peak.get(k, 0)) for k in ("L0", "L2", "L3", "L4")) + " |" if peak else ""
    hp = hold["peak_level"]
    second = "| Further 2000, not used for tuning | " + " | ".join(str(hp.get(k, 0)) for k in ("L0", "L2", "L3", "L4")) + " |"
    return f"""# Results

Simulated and recorded data only. Not approved or ready for operational flight use.
The columns `limits` and `lost` count runs that ended outside limits or with radar contact lost.
`lat95_m` and `vert95_m` are 95 % errors at decision height. `changes` and `voice` are medians for one approach.

{runs}

Marker into ring, same start and wind: {ring["minimums"]} of {ring["of"]} runs reach decision height, 95 % error {ring["lat95_m"]:.0f} m lateral and
{ring["vert95_m"]:.0f} m vertical. This pilot model reads drift with no error, so 11 m is a best case.

{faults}

{jumps}

## Replay of recorded Zurich tracks

The aircraft did not react to the cue. No pilot saw it. The table gives the highest alert level of each track.

| Tracks | Quiet | Advise | Caution | Warning |
|---|---|---|---|---|
{first}
{second}
"""


def main() -> None:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    top = STAGE / TOP
    for d in ("1_Report", "2_Mock_Up/Stills", "3_Code/par_cue", "4_Results"):
        (top / d).mkdir(parents=True)

    (top / "README.txt").write_text(README, encoding="utf-8", newline="\r\n")
    shutil.copy2(ADV / "submission" / "versions" / "Team Beetiful Final Report.pdf", top / "1_Report" / "Team_Beetiful_Final_Report.pdf")
    (top / "2_Mock_Up" / "README_Mock_Up.txt").write_text(MOCK_UP, encoding="utf-8")
    for old, new in STILLS.items():
        shutil.copy2(ADV / "outputs" / "par_visual" / f"{old}.png", top / "2_Mock_Up" / "Stills" / f"{new}.png")

    pkg = top / "3_Code" / "par_cue"
    (pkg / "__init__.py").write_text('"""PAR cue: radar plots to pilot cue. Educational concept, not for flight use."""\n', encoding="utf-8")
    (pkg / "runway.py").write_text(RUNWAY, encoding="utf-8")
    shutil.copy2(ADV / "scripts" / "submission_ring.py", pkg / "ring.py")
    for name in MODULES:
        src = (ROOT / "src" / "aerokit" / "atc" / f"{name}.py").read_text(encoding="utf-8")
        new = clean(name, src)
        if not same_code(src, new):
            raise SystemExit(f"{name}: the zip copy differs from the tested code")
        (pkg / f"{name}.py").write_text(new, encoding="utf-8")
    (top / "3_Code" / "run_check.py").write_text(RUN_CHECK, encoding="utf-8")
    (top / "3_Code" / "requirements.txt").write_text("numpy\n", encoding="utf-8")
    (top / "4_Results" / "Results.md").write_text(results(), encoding="utf-8")

    OUT.unlink(missing_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(top.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                z.write(f, f.relative_to(STAGE).as_posix())
    shutil.rmtree(STAGE)
    with zipfile.ZipFile(OUT) as z:
        print(f"{OUT.name}: {len(z.namelist())} files, {OUT.stat().st_size / 1e6:.1f} MB")
        for n in z.namelist():
            print(" ", n)


if __name__ == "__main__":
    main()
