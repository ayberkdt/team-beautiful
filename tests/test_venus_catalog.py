"""04_Venus/catalog: the catalogues match the files on disk, and every path in the reorganisation manifest exists."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "04_Venus" / "catalog"
SCRIPT = ROOT / "04_Venus" / "code" / "catalog" / "build_catalog.py"
MANIFEST = json.loads((CATALOG / "reorg_manifest.json").read_text(encoding="utf-8"))


def _builder():
    spec = importlib.util.spec_from_file_location("build_catalog", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_catalog_is_current():
    for name, text in _builder().build().items():
        assert (CATALOG / name).read_bytes() == text.encode("utf-8"), f"{name}: run python 04_Venus/code/catalog/build_catalog.py"


def test_build_is_deterministic():
    mod = _builder()
    assert mod.build() == mod.build()


def test_every_script_and_output_is_described():
    assert "yazılmadı" not in (CATALOG / "scripts.md").read_text(encoding="utf-8")
    assert "doc 25'te altyazı yok" not in (CATALOG / "figures.md").read_text(encoding="utf-8")
    assert "üreticisi bilinmeyen 0" in (CATALOG / "data_files.md").read_text(encoding="utf-8").splitlines()[0]


def test_manifest_new_paths_exist_and_old_paths_are_gone():
    assert len(MANIFEST["moves"]) == 120
    for row in MANIFEST["moves"]:
        assert (ROOT / row["new"]).is_file(), row["new"]
        assert not (ROOT / row["old"]).exists(), row["old"]


def test_file_names_did_not_change_in_the_move():
    assert all(Path(row["old"]).name == Path(row["new"]).name for row in MANIFEST["moves"])


def test_old_anchor_copy_is_kept():
    copy = CATALOG / "baseline_hashes_before_2026-11-06.json"
    live = ROOT / "04_Venus" / "outputs" / "variants" / "v0_7_44p6kg" / "baseline_hashes_before.json"
    assert hashlib.sha256(copy.read_bytes()).hexdigest() == hashlib.sha256(live.read_bytes()).hexdigest()
