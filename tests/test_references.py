"""Bibliography integrity: valid keys, no duplicates, generated page up to date, citation coverage."""
from __future__ import annotations

import importlib
import inspect
import pathlib
import pkgutil
import subprocess
import sys

import pytest

import aerokit
from aerokit.references import REFERENCES, Reference, _merge, cite, references_of

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Modules implementing physics/numerics must cite at least one source.
PHYSICS_PACKAGES = ("aerokit.aero.", "aerokit.structures.", "aerokit.composites.", "aerokit.optimization.",
                    "aerokit.fem.elements.", "aerokit.materials.handbook")


def test_registry_entries_are_complete():
    assert len(REFERENCES) >= 40
    for key, ref in REFERENCES.items():
        assert ref.key == key
        assert ref.authors.strip() and ref.title.strip(), key
        assert 1600 <= ref.year <= 2026, (key, ref.year)
        assert ref.format().endswith("."), key


def test_duplicate_and_malformed_keys_rejected():
    r = Reference("a_2000", "A", 2000, "T")
    with pytest.raises(ValueError):
        _merge([[r], [r]])
    with pytest.raises(ValueError):
        _merge([[Reference("Bad Key", "A", 2000, "T")]])


def test_cite_validates_and_documents():
    with pytest.raises(KeyError):
        cite("no_such_reference_1900")
    with pytest.raises(ValueError):
        cite()

    @cite("cook_2002", note="Eq. 3.1-1")
    def f(x: float) -> float:
        """Demo."""
        return x
    assert f.__references__ == ("cook_2002",)
    assert "References\n----------" in f.__doc__ and "Eq. 3.1-1" in f.__doc__
    assert references_of(f)[0].key == "cook_2002"


def _modules():
    for info in pkgutil.walk_packages(aerokit.__path__, "aerokit."):
        yield info.name


@pytest.mark.parametrize("modname", [m for m in _modules() if m.startswith(PHYSICS_PACKAGES)
                                     and not m.rsplit(".", 1)[-1].startswith("_")])
def test_physics_modules_cite_sources(modname):
    mod = importlib.import_module(modname)
    cited = []
    for _, obj in vars(mod).items():
        if getattr(obj, "__module__", None) != modname:
            continue
        objs = [obj] + ([v for v in vars(obj).values() if inspect.isfunction(v)] if inspect.isclass(obj) else [])
        cited += [o for o in objs if getattr(o, "__references__", ())]
    if not any(inspect.isfunction(o) or inspect.isclass(o) for o in vars(mod).values()
               if getattr(o, "__module__", None) == modname):
        pytest.skip("no public functions")
    assert cited, f"{modname} implements methods but cites no source (@cite)"


def test_generated_reference_page_up_to_date():
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_references.py"), "--check"],
                          capture_output=True, text=True, timeout=300, check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
