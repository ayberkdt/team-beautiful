"""Reveal-day triage: score the real task text against the cases, plan which 03_Advionics items stay and which move.

    python 03_Advionics/scripts/triage.py "<task text>"              # or a path to a .txt/.md file with the task
    python 03_Advionics/scripts/triage.py task.txt --keep case_7_readback_correlation
    python 03_Advionics/scripts/triage.py task.txt --apply           # performs the move, writes a manifest
    python 03_Advionics/scripts/triage.py --undo prev_guess/03_Advionics/2026-11-06_unused/manifest.json

Scoring is a transparent keyword count (weights in ``03_Advionics/cases/triage_keywords.json``; no ML): text and
phrases are lower-cased and accent-folded; ``word*`` matches word endings; score = Σ weight × min(count, cap).
A case is kept when its score ≥ max(min_score, keep_ratio × top score); the top case is always kept when it scored.

Dry run is the default: it writes ``03_Advionics/triage_plan.json`` and ``triage_plan.md`` and moves nothing.
``--apply`` moves the planned items to ``prev_guess/03_Advionics/<date>_unused/`` (same relative paths) and writes
``manifest.json`` there; ``--undo <manifest>`` moves them back. Never moved: ``always_keep`` entries (docs, research,
scripts, templates, submission/, the shared case files) and any file a kept case claims.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ADV = Path(__file__).resolve().parents[1]           # 03_Advionics
REPO = ADV.parent
KEYWORDS = ADV / "cases" / "triage_keywords.json"
_TR = str.maketrans({"ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g", "ç": "c", "Ç": "c", "ö": "o",
                     "Ö": "o", "ü": "u", "Ü": "u"})


def normalise(text: str) -> str:
    t = text.translate(_TR).lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", t)


def _pattern(phrase: str) -> re.Pattern:
    p = normalise(phrase).strip()
    star = p.endswith("*")
    body = re.escape(p.rstrip("*")).replace(r"\ ", r"\s+")
    return re.compile(r"(?<![a-z0-9])" + body + (r"[a-z0-9\-]*" if star else "") + r"(?![a-z0-9])")


def score(text: str, kw: dict) -> list[dict]:
    """Ranked list of {case, score, matches: {phrase: count}}."""
    t = normalise(text)
    cap = kw.get("cap_per_phrase", 3)
    out = []
    for case, phrases in kw["cases"].items():
        s, m = 0.0, {}
        for ph, w in phrases.items():
            n = len(_pattern(ph).findall(t))
            if n:
                m[ph] = n
                s += float(w) * min(n, cap)
        out.append({"case": case, "score": round(s, 2), "matches": m})
    return sorted(out, key=lambda r: (-r["score"], r["case"]))


def decide(ranked: list[dict], kw: dict, keep: list[str] = (), drop: list[str] = ()) -> set[str]:
    top = ranked[0]["score"] if ranked else 0.0
    if top <= 0:
        return {r["case"] for r in ranked}                       # nothing matched: keep everything
    thr = max(kw.get("min_score", 4.0), kw.get("keep_ratio", 0.35) * top)
    kept = {r["case"] for r in ranked if r["score"] >= thr} | {ranked[0]["case"]}
    return (kept | set(keep)) - set(drop)


def _expand(root: Path, pattern: str) -> list[str]:
    if any(c in pattern for c in "*?["):
        parent = (root / pattern).parent
        if not parent.is_dir():
            return []
        return sorted(str(p.relative_to(root)).replace("\\", "/") for p in parent.iterdir()
                      if fnmatch.fnmatch(p.name, Path(pattern).name))
    return [pattern] if (root / pattern).exists() else []


def plan(root: Path, kw: dict, kept: set[str]) -> dict:
    """Which items stay / move. Items are case folders and the outputs each case claims."""
    always = set(kw.get("always_keep", []))
    claims: dict[str, set[str]] = {}
    for case in kw["cases"]:
        if (root / "cases" / case).is_dir():
            claims.setdefault(f"cases/{case}", set()).add(case)
        for pat in kw.get("case_assets", {}).get(case, []):
            for rel in _expand(root, pat):
                claims.setdefault(rel, set()).add(case)
    move, stay = [], []
    for rel, owners in sorted(claims.items()):
        if rel in always or any(rel == a or rel.startswith(a + "/") for a in always):
            stay.append({"path": rel, "why": "always kept"})
        elif owners & kept:
            stay.append({"path": rel, "why": "used by " + ", ".join(sorted(owners & kept))})
        else:
            move.append({"path": rel, "why": "only used by " + ", ".join(sorted(owners))})
    shared = sorted(p.name for p in root.iterdir() if p.name not in {"cases", "outputs"} and not p.name.startswith("."))
    for name in shared:
        stay.append({"path": name, "why": "shared (not case-specific)"})
    return {"move": move, "stay": stay}


def write_plan(out_dir: Path, task: str, ranked: list[dict], kept: set[str], pl: dict, dest: Path) -> tuple[Path, Path]:
    doc = {"created": _dt.datetime.now().isoformat(timespec="seconds"),
           "task_sha1": hashlib.sha1(task.encode("utf-8")).hexdigest(), "task": task, "ranking": ranked,
           "kept_cases": sorted(kept), "destination": str(dest), **pl}
    j = out_dir / "triage_plan.json"
    j.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    md = ["# Triage plan (dry run)", "", f"Created {doc['created']}; destination for moved items: `{dest}`.", "",
          "## Ranking", "", "| # | Case | Score | Kept | Matched (count) |", "|---|---|---|---|---|"]
    for i, r in enumerate(ranked, 1):
        mt = ", ".join(f"{k} ({v})" for k, v in sorted(r["matches"].items(), key=lambda kv: -kv[1])) or "-"
        md.append(f"| {i} | {r['case']} | {r['score']:g} | {'yes' if r['case'] in kept else 'no'} | {mt} |")
    md += ["", f"## Would move ({len(pl['move'])})", ""] + [f"- `{m['path']}` — {m['why']}" for m in pl["move"]]
    md += ["", f"## Stays ({len(pl['stay'])})", ""] + [f"- `{s['path']}` — {s['why']}" for s in pl["stay"]]
    md += ["", "Task text:", "", "> " + task.replace("\n", "\n> ")]
    m = out_dir / "triage_plan.md"
    m.write_text("\n".join(md) + "\n", encoding="utf-8")
    return j, m


def default_dest(repo: Path, date: str | None = None) -> Path:
    d = date or _dt.date.today().isoformat()
    base = repo / "prev_guess" / "03_Advionics" / f"{d}_unused"
    k, cand = 2, base
    while cand.exists():
        cand = base.with_name(f"{base.name}_{k}")
        k += 1
    return cand


def apply(root: Path, pl: dict, dest: Path, task: str = "") -> Path:
    """Move every planned item; refuse if a destination exists. Returns the manifest path."""
    for m in pl["move"]:
        if (dest / m["path"]).exists():
            raise SystemExit(f"refusing: {dest / m['path']} already exists")
    dest.mkdir(parents=True, exist_ok=False)
    moves = []
    for m in pl["move"]:
        src, dst = root / m["path"], dest / m["path"]
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moves.append({"src": str(src), "dst": str(dst)})
        print(f"  moved {m['path']}")
    man = dest / "manifest.json"
    man.write_text(json.dumps({"created": _dt.datetime.now().isoformat(timespec="seconds"), "root": str(root),
                               "task": task, "moves": moves}, indent=1, ensure_ascii=False), encoding="utf-8")
    return man


def undo(manifest: Path) -> int:
    doc = json.loads(manifest.read_text(encoding="utf-8-sig"))
    n = 0
    for mv in reversed(doc["moves"]):
        src, dst = Path(mv["src"]), Path(mv["dst"])
        if src.exists():
            print(f"  skip (already present): {src}")
            continue
        if not dst.exists():
            print(f"  missing in archive: {dst}")
            continue
        src.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dst), str(src))
        n += 1
        print(f"  restored {src}")
    return n


def read_task(arg: str) -> str:
    p = Path(arg)
    if len(arg) < 260 and p.suffix.lower() in (".txt", ".md") and p.is_file():
        return p.read_text(encoding="utf-8-sig")
    return arg


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score the real task against the cases; plan (or apply) the move.")
    ap.add_argument("task", nargs="?", help="task text, or a path to a .txt/.md file")
    ap.add_argument("--apply", action="store_true", help="perform the planned move (default: dry run)")
    ap.add_argument("--undo", metavar="MANIFEST", help="move the items of a manifest back")
    ap.add_argument("--keep", action="append", default=[], metavar="CASE", help="force-keep a case (repeatable)")
    ap.add_argument("--drop", action="append", default=[], metavar="CASE", help="force-drop a case (repeatable)")
    ap.add_argument("--root", default=str(ADV), help=argparse.SUPPRESS)
    ap.add_argument("--dest", help=argparse.SUPPRESS)
    ap.add_argument("--date", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.undo:
        n = undo(Path(a.undo))
        print(f"restored {n} item(s) from {a.undo}")
        return 0
    if not a.task:
        ap.error("give the task text (or a file path), or --undo MANIFEST")
    root = Path(a.root)
    if not root.is_dir():
        ap.error(f"root folder not found: {root}")
    kw = json.loads(KEYWORDS.read_text(encoding="utf-8-sig"))
    unknown = [c for c in a.keep + a.drop if c not in kw["cases"]]
    if unknown:
        ap.error(f"unknown case(s) {unknown}; valid: {', '.join(kw['cases'])}")
    task = read_task(a.task)
    ranked = score(task, kw)
    kept = decide(ranked, kw, a.keep, a.drop)
    pl = plan(root, kw, kept)
    dest = Path(a.dest) if a.dest else default_dest(root.parent, a.date)
    j, m = write_plan(root, task, ranked, kept, pl, dest)
    print(f"{'#':>2}  {'case':<36} {'score':>6}  keep  matched")
    for i, r in enumerate(ranked, 1):
        mt = ", ".join(k for k, _ in sorted(r["matches"].items(), key=lambda kv: -kv[1])[:5]) or "-"
        print(f"{i:>2}  {r['case']:<36} {r['score']:>6g}  {'yes ' if r['case'] in kept else 'no  '}  {mt[:60]}")
    if a.apply:
        man = apply(root, pl, dest, task)
        print(f"moved {len(pl['move'])} item(s) to {dest}; undo: python 03_Advionics/scripts/triage.py --undo \"{man}\"")
    else:
        print(f"dry run: {len(pl['move'])} item(s) would move, {len(pl['stay'])} stay -> {m.name}; "
              f"next: same command + --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
