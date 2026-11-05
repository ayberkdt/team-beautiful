"""Output-path validation, atomic writes and bundled-data path containment."""
from __future__ import annotations

import contextlib
import os

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from aerokit.data import EXAMPLES_DIR, example_path
from aerokit.output.writers import UnsafePathError, safe_output_path, write_text_atomic


@pytest.mark.parametrize("bad", ["", "   ", "a\x00b.md", "line\nbreak.md", "tab\there.md"])
def test_rejects_empty_and_control_characters(bad):
    with pytest.raises(UnsafePathError):
        safe_output_path(bad)


@pytest.mark.parametrize("name", ["CON", "nul.md", "com1.json", "LPT9.txt", "aux"])
def test_rejects_windows_device_names(tmp_path, name):
    with pytest.raises(UnsafePathError):
        safe_output_path(tmp_path / name)


def test_suffix_whitelist(tmp_path):
    assert safe_output_path(tmp_path / "r.MD", suffixes={".md"}).name == "r.MD"
    with pytest.raises(UnsafePathError):
        safe_output_path(tmp_path / "r.exe", suffixes={".md", ".json"})


def test_directory_is_not_a_file(tmp_path):
    with pytest.raises(UnsafePathError):
        safe_output_path(tmp_path)


@pytest.mark.parametrize("rel", ["../escape.md", "sub/../../escape.md", "../../etc/passwd.md"])
def test_traversal_outside_base_dir_rejected(tmp_path, rel):
    base = tmp_path / "out"
    base.mkdir()
    with pytest.raises(UnsafePathError):
        safe_output_path(base / rel, base_dir=base)
    assert safe_output_path(base / "ok" / "r.md", base_dir=base).parent == (base / "ok").resolve()


def test_symlink_escape_rejected(tmp_path):
    base, outside = tmp_path / "base", tmp_path / "outside"
    base.mkdir()
    outside.mkdir()
    link = base / "link"
    try:
        os.symlink(outside, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not permitted on this system")
    with pytest.raises(UnsafePathError):
        safe_output_path(link / "r.md", base_dir=base)


def test_atomic_write_creates_parents_and_leaves_no_temp(tmp_path):
    target = tmp_path / "a" / "b" / "report.md"
    p = write_text_atomic(target, "hello\n")
    assert p.read_text(encoding="utf-8") == "hello\n"
    assert [f.name for f in p.parent.iterdir()] == ["report.md"]


def test_atomic_write_failure_keeps_old_content(tmp_path, monkeypatch):
    target = tmp_path / "r.md"
    target.write_text("old", encoding="utf-8")

    def boom(*_a, **_k):
        raise OSError("disk full")
    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        write_text_atomic(target, "new")
    assert target.read_text(encoding="utf-8") == "old"
    assert sorted(f.name for f in tmp_path.iterdir()) == ["r.md"], "temporary file left behind"


@settings(max_examples=200, deadline=None)
@given(st.text(max_size=60))
def test_safe_output_path_never_crashes(name):
    """Arbitrary text either validates or raises UnsafePathError/OSError — never anything else."""
    with contextlib.suppress(UnsafePathError, OSError):
        safe_output_path(name, suffixes={".md"})


def test_example_path_is_contained():
    assert example_path("plate_q8.json").parent == EXAMPLES_DIR.resolve()
    for bad in [("..", "data", "__init__.py"), ("..", "..", "references", "__init__.py"), ("cad", "..", "..", "x")]:
        with pytest.raises(ValueError):
            example_path(*bad)
    with pytest.raises(FileNotFoundError):
        example_path("does_not_exist.json")
