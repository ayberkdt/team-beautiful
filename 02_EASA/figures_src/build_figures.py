"""Build the EASA report figures in the sunumatik visual language and export them as print PNGs.

    python 02_EASA/figures_src/build_figures.py

1. Copies the few sunumatik files the page needs into ``figures_src/vendor/`` (palette tokens, chart theme, arrow
   core, utility icon sprite). Source: $SUNUMATIK or C:/Users/ayber/Desktop/Custom Yetenekler/sunumatik.
2. Writes ``figures_src/data.json`` from the occurrence catalogue (R2 + R5 CSVs via ``canopy_day.load_occurrences``),
   ``outputs/tradeoffs/tradeoffs.json`` and the step/label lists below. No number is typed in the page.
3. Serves the folder on localhost, renders each figure in headless Chrome at 3× device scale, and reads the page's
   own text audit (text-text overlaps, text outside its card) with ``--dump-dom``.
Writes ``02_EASA/outputs/figures/F*.png``, ``audit.json`` and ``print_sizes.json`` (the width in mm each report
figure was drawn for; the docx should place it at exactly that width). Exit code 1 if a report figure (PRINT_MM) has an
overlap, an overflow, a fallback font or text below 7.6 pt on the page; the other figures are reported only.
"""
from __future__ import annotations

import html
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
EASA = ROOT / "02_EASA"
SRC = EASA / "figures_src"
OUT = EASA / "outputs" / "figures"
SUN = Path(os.environ.get("SUNUMATIK", r"C:/Users/ayber/Desktop/Custom Yetenekler/sunumatik"))
CHROME = os.environ.get("CHROME", r"C:/Program Files/Google/Chrome/Application/chrome.exe")
VENDOR = ["presets/color_themes/palette-library.css", "presets/charts_icons/chart-theme.css",
          "presets/core/isaretci.mjs", "presets/charts_icons/icon-library/sprite.svg"]
# Report figures are drawn at their print size (width, height in mm; widths from easa_report_docx.py FIGURES, agreed
# with the report session on 5 Nov). K px per mm keeps one px font size = one pt size on the page (figures.mjs).
K_PX_PER_MM = 960 / 115
PRINT_MM = {"F1a": (72, 59.7), "F1b": (72, 59.7), "F8": (160, 52.2), "F7": (80, 49.7), "F10": (176, 40)}   # report session, 5 Nov 20:00
REPORT = tuple(PRINT_MM)
SIZES = {"F2": (960, 560), "F3": (960, 560), "F4": (960, 600), "F5": (960, 600), "F6": (960, 520), "F9": (960, 560)}
SIZES |= {k: (round(w * K_PX_PER_MM), round(h * K_PX_PER_MM)) for k, (w, h) in PRINT_MM.items()}
ELEC = {"inputs": [["i-scan-search", "4 sensors", "monitored loops", True], ["i-check", "Lever switch", "primary arming", True],
                   ["i-gauge", "MAP, rpm", "engine power", False], ["i-earth", "IAS, GPS speed", "air / ground", False],
                   ["i-zap", "Main bus", "own 5 A breaker", False]],
        "unit": ["Alert unit", "line monitor", "phase logic", "hardware AND", "self-test, log"],
        "outputs": [["i-lightbulb", "Lamps rear + front", "3-colour", False],
                    ["i-audio-waveform", "Audio panel", "alert + fail-safe", False],
                    ["i-waves", "Throttle shaker", "below 30 kt", False],
                    ["i-lock", "Take-off gate", "unpowered = free", False],
                    ["i-cpu", "EFIS discrete", "optional", True]]}
LUGS = [["front", 110], ["centre", 280], ["rear", 520]]
# (label, rejected, recommended). User, 5 Nov: no throttle restriction and no knob shaker → O4 is the design; the
# shaker and gate sets are drawn dashed as rejected options so the reader sees what was given up.
CHOSEN = "O5"   # user, 5 Nov: vibration moved from the throttle knob to a lap-belt tactor (O5)
SWEEP_LABELS = {"O3": ("lamp only", False, CHOSEN == "O3"), "O4": ("lamp + voice", False, CHOSEN == "O4"),
                "O5": ("+ belt pad", CHOSEN == "O4", CHOSEN == "O5"), "O6": ("+ gate", True, False)}   # gate: rejected, kept for the trade-off
ROLLS = [("Brisk roll", 5.0), ("Slow roll", 2.8)]   # m/s², constant; the R8-timing bracket
# (112 m and 200 m to 65 kt), kept so that 30/40 kt times match cues.json; no Extra NG take-off roll published [Y]
V_LOF_KT = 80.0      # Extra NG "airborne at 80 KIAS", tail up at 40 KIAS (AOPA 2020 flight test, R9-extra S14) [D-ag]

PHASES = [("initial_climb", "Initial climb"), ("cruise", "Cruise"), ("takeoff_roll", "Take-off roll"),
          ("approach", "Approach")]
SHORT = {"O1": "Bolt marks only", "O2": "Organisers' switch", "O3": "LOCK-SENSE + lamp", "O4": "+ voice",
         "O5": "+ throttle shaker", "O6": "+ ground gate", "O7": "+ ground shut-down", "O8": "+ in-flight shut-down",
         "O9": "+ mechanical pawl", "O10": "+ starter guard"}
ARCH = {"canopy": ["steel target", "bolt 1 tip", "bolt 2 tip", "bolt 3 tip"],
        "sensors": ["S0 seated", "S1 lug 1", "S2 lug 2", "S3 lug 3"],
        "cues": [["i-lightbulb", "3-colour lamp"], ["i-audio-waveform", "Voice “CANOPY”"],
                 ["i-waves", "Throttle shaker"], ["i-lock", "Take-off gate"], ["i-database", "Lock-state log"]]}
PROCESS = [  # the twelve steps of kit 03 §4 / docs 27 (K3), with the test that closes each block
    {"name": "Define", "icon": "i-search", "steps": [["1", "Pick aircraft"], ["2", "Survey"], ["3", "Hazards + HF"]],
     "gate": ["Every hazard has", "a requirement"]},
    {"name": "Design", "icon": "i-pen-tool", "steps": [["4", "Requirements"], ["5", "Sensors + cues"], ["6", "Logic"]],
     "gate": ["Logic passes the", "fault demo"]},
    {"name": "Build & test", "icon": "i-wrench",
     "steps": [["7", "Mount + rig"], ["8", "Wire + EFIS"], ["9", "Bench test"], ["10", "Ground test"]],
     "gate": ["Every single", "fault caught"]},
    {"name": "Operate", "icon": "i-list-checks", "steps": [["11", "Flight check"], ["12", "Train + gauge"]],
     "gate": ["Log + nuisance", "review"]},
]


def vendor() -> None:
    for rel in VENDOR:
        src = SUN / rel
        dst = SRC / "vendor" / rel.removeprefix("presets/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def data() -> dict:
    spec = importlib.util.spec_from_file_location("canopy_day", EASA / "scripts" / "canopy_day.py")
    cd = importlib.util.module_from_spec(spec)
    sys.modules["canopy_day"] = cd
    spec.loader.exec_module(cd)
    rows = cd.load_occurrences()
    lock = [r for r in rows if r["cause_class"] in ("not_locked", "partially_latched")]
    n, f = Counter(r["phase"] for r in lock), Counter(r["phase"] for r in lock if r["outcome"] == "fatal")
    phases = [{"label": lab, "n": n[k], "fatal": f[k]} for k, lab in PHASES]
    rest = [k for k in n if k not in dict(PHASES)]
    phases.append({"label": "Other", "n": sum(n[k] for k in rest), "fatal": sum(f[k] for k in rest)})
    fam_n, fam_f = defaultdict(int), defaultdict(int)
    for r in lock:
        fam_n[r["family"]] += 1
        fam_f[r["family"]] += r["outcome"] == "fatal"
    named = sorted((k for k in fam_n if not k.startswith("Other")), key=lambda k: (-fam_n[k], k))[:10]
    families = [{"label": k.replace("Vans", "Van's"), "n": fam_n[k], "fatal": fam_f[k], "bold": k == "Extra"}
                for k in named]
    families.append({"label": "All other types", "n": sum(v for k, v in fam_n.items() if k not in named),
                     "fatal": sum(v for k, v in fam_f.items() if k not in named)})
    assert sum(p["n"] for p in phases) == len(lock) == sum(x["n"] for x in families)
    t = json.loads((EASA / "outputs" / "tradeoffs" / "tradeoffs.json").read_text(encoding="utf-8"))
    opts = []
    for k, lab in SHORT.items():
        m, u = t["main"][k], t["uncertainty"][k]
        opts.append({"key": k, "label": lab, "acts": m["rf_full_ind"], "match": m["rf_matching_ind"],
                     "lo": u["rf_matching"][0], "hi": u["rf_matching"][2], "recommended": k == CHOSEN})
    xmax = 10 ** (len(str(int(max(o["acts"] for o in opts)))))           # next decade above the largest RF
    SHORT_S = {"S1": "Inductive × 3 (LOCK-SENSE)", "S2": "Bolt contact + resistors", "S3": "Bolt contact, plain",
               "S4": "Snap switch × 3", "S5": "Hall + magnet × 3", "S6": "LVDT on linkage tube", "S7": "Handle switch only"}
    sensing = []
    for r in t["sensing_options"]:
        sees = "/".join("N" if h in r["blind"] else "Y" for h in ("partial", "one_bolt", "unseated"))
        sensing.append({"key": r["key"], "label": SHORT_S[r["key"]], "c": r["O6_match_c"], "u": r["O6_match_u"],
                        "sees": sees, "recommended": r["key"] == "S1"})
    sw = t["compliance_sweep"]
    series = [{"key": k, "label": lab, "barrier": bar, "recommended": rec, "vals": sw[k]}
              for k, (lab, bar, rec) in SWEEP_LABELS.items()]
    ymax = 1.3 * max(max(x["vals"]) for x in series)
    cj = json.loads((EASA / "inputs" / "cues.json").read_text(encoding="utf-8"))["timing"]
    KT = 0.514444
    rolls = []
    for lab, a in ROLLS:                                  # constant acceleration a: t(v) = v / a, roll = v² / 2a
        rolls.append({"label": lab, "a": a, "m": round((V_LOF_KT * KT) ** 2 / (2 * a)), "tlof": round(V_LOF_KT * KT / a, 2),
                      "t30": round(30 * KT / a, 2), "t40": round(40 * KT / a, 2)})
    on = cj["onset_s"]
    med, p95 = cj["rt_median_s"]["value"][1], cj["rt_p95_s"]["value"][1]
    sr = rolls[0]
    kt = lambda t: int(sr["a"] * t / KT + 0.5)              # constant acceleration, brisk case; half-up rounding
    lanes = [{"label": lab, "onset": on[k], "med_t": on[k] + med, "p95_t": on[k] + p95, "med_kt": kt(on[k] + med),
              "p95_kt": kt(on[k] + p95), "ours": k == "lever"} for k, lab in (("lever", "lever trigger"), ("rpm", "rpm trigger"))]
    timeline = {"rolls": rolls, "tmax": 2 * int(-(-(max(r["tlof"] for r in rolls) + 1) // 2)),
                "onsets": [[f"alert onset, lever switch ({on['lever']} s)", on["lever"]],
                           [f"alert onset, rpm + persistence ({on['rpm']} s)", on["rpm"]]],
                "rt_med": med, "rt_p95": p95, "lanes": lanes}
    return {"phases": phases, "families": families, "options": opts, "xmax": xmax, "arch": ARCH,
            "process": PROCESS, "n_lock": len(lock), "n_all": len(rows), "elec": ELEC, "lugs": LUGS,
            "sweep": {"c": sw["c"], "series": series, "ymax": ymax}, "timeline": timeline,
            "sensing": sensing, "sensing_xmax": 10 ** len(str(int(max(r["c"] for r in sensing)))),
            "print": {k: {"mm": PRINT_MM[k], "px": SIZES[k]} for k in REPORT}}


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def chrome(args: list[str], url: str, timeout: int = 60) -> str:
    base = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", "--virtual-time-budget=6000", "--run-all-compositor-stages-before-draw"]
    r = subprocess.run(base + args + [url], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout)
    return r.stdout


def main() -> int:
    vendor()
    (SRC / "data.json").write_text(json.dumps(data(), indent=1, ensure_ascii=False), encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=SRC,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report, bad = {}, 0
    try:
        time.sleep(1.0)
        for fig, (w, h) in SIZES.items():
            url = f"http://127.0.0.1:{port}/figures.html?fig={fig}"
            png = OUT / f"{fig}.png"
            chrome([f"--window-size={w},{h}", "--force-device-scale-factor=3", f"--screenshot={png}"], url)
            dom = chrome([f"--window-size={w},{h}", "--dump-dom"], url)
            m = re.search(r'<pre id="audit">(.*?)</pre>', dom, re.S)
            a = json.loads(html.unescape(m.group(1))) if m and m.group(1).strip() else {"error": "no audit"}
            report[fig] = a
            ok = a.get("texts", 0) > 0 and not a.get("overlaps") and not a.get("outside") and not a.get("clipped")
            if fig in REPORT:   # report figures must also render in Montserrat and stay at or above 7.6 pt on the page
                ok = ok and a.get("font_loaded") is True and a.get("min_pt", 0) >= 7.6
            bad += not ok and fig in REPORT
            print(f"{fig}: {w}×{h} px ×3 → {png.relative_to(ROOT).as_posix()}  texts {a.get('texts')}  "
                  f"overlaps {len(a.get('overlaps', []))}  outside card {len(a.get('outside', []))}  clipped {len(a.get('clipped', []))}"
                  + ("" if ok else f"  FAIL {a}"))
    finally:
        srv.terminate()
    (OUT / "audit.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    sizes = {k: {"png": f"{k}.png", "width_mm": w, "height_mm": h, "min_text_pt": report.get(k, {}).get("min_pt"),
                 "font": "Montserrat" if report.get(k, {}).get("font_loaded") else "fallback"}
             for k, (w, h) in PRINT_MM.items()}
    (OUT / "print_sizes.json").write_text(json.dumps(sizes, indent=1), encoding="utf-8")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
