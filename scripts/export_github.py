"""Copy the team's OWN work into a separate folder that is pushed to the public repo ayberkdt/team-beautiful.

The project folder itself is not a git repository (several sessions write into it); this script makes a filtered
copy so nothing confidential or third-party is ever published by accident. Decision (user, 5 Nov 2026): the repo
stays public and gets only our work — no organiser files, no organiser part geometry, nothing derived from the
"Proprietary. Do Not Share." Synopsys introduction.

    python -I scripts/export_github.py D:/tmp_ideathon/repo/team-beautiful   # then git add/commit/push there

Prints every excluded file over the size limit and writes EXPORT_MANIFEST.txt (included files + SHA-256 prefix).
"""
from __future__ import annotations

import fnmatch
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 20 * 1024 * 1024

INCLUDE_DIRS = ["src", "tests", "scripts", "docs", "reports", "research_notes", "studies", "design_report", "outputs"]
INCLUDE_FILES = ["README.md", "pyproject.toml", ".gitignore"]

# Never published (glob on the path relative to the project root, forward slashes)
EXCLUDE = [
    # organiser files and anything rebuilt from their CAD
    "studies/final_2026/ansys/official_2026-11-05/files/*", "studies/final_2026/ansys/official_2026-11-05/unpacked/*",
    "studies/final_2026/ansys/official_2026-11-05/Files.zip*",
    "studies/final_2026/ansys/official_2026-11-05/visuals/turntable/*",
    "*/cad/*", "*.stl", "*.step", "*.stp", "*.igs", "*.iges", "*.dsco", "*.x_b",
    # Synopsys "Do Not Share" introduction and documents derived from it (doc 10-14 and their reports)
    "*Synopsys Introduction*", "docs/10_*", "docs/11_*", "docs/12_*", "docs/13_*", "docs/14_*",
    "reports/beetiful_three_variants.*", "reports/beetiful_task_scenarios.*", "reports/beetiful_task_space.*",
    "reports/beetiful_course_playbook.*", "research_notes/Görev senaryoları/*", "research_notes/Üç sapma alanı/*",
    "studies/tradeoff/decision_rules.json",  # quotes the Do-Not-Share deck
    "tests/data/*.xml",  # third-party Ansys Workbench Engineering Data export
    # third-party documents (handbooks, regulations, papers): cite, do not redistribute
    "*.pdf.part", "research_notes/*.pdf", "research_notes/*/*.pdf", "references/*",
    # bulky / machine-local
    "*.pkl", "*.zip", "*.pptx", "*.mp4", "*.mov", "*/__pycache__/*", "*.pyc", "*/.pytest_cache/*", "*/mpl/*",
]


def excluded(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDE)


def main(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    kept, big, skipped = [], [], 0
    paths = [ROOT / f for f in INCLUDE_FILES if (ROOT / f).exists()]
    for d in INCLUDE_DIRS:
        paths += [p for p in (ROOT / d).rglob("*") if p.is_file()]
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        if excluded(rel):
            skipped += 1
            continue
        if p.stat().st_size > MAX_BYTES:
            big.append((p.stat().st_size, rel))
            continue
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, out)
        kept.append((rel, hashlib.sha256(p.read_bytes()).hexdigest()[:12], p.stat().st_size))
    readme = ROOT / "scripts" / "github_readme.md"           # the repo's front page; project README -> docs/
    if readme.exists():
        shutil.copy2(dest / "README.md", dest / "docs" / "PROJECT_README.md") if (dest / "README.md").exists() else None
        shutil.copy2(readme, dest / "README.md")
    (dest / "EXPORT_MANIFEST.txt").write_text(
        "".join(f"{h}  {s:>10d}  {r}\n" for r, h, s in sorted(kept)), encoding="utf-8")
    total = sum(s for _, _, s in kept)
    print(f"copied {len(kept)} files, {total / 1e6:.1f} MB; excluded by rule {skipped}; over {MAX_BYTES >> 20} MB {len(big)}")
    for s, r in sorted(big, reverse=True):
        print(f"  too big, not copied: {s / 1e6:7.1f} MB  {r}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(Path(sys.argv[1]))
