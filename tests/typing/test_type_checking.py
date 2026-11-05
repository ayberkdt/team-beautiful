"""Static and runtime type checks of the public API.

* ``mypy`` over the whole package with the configuration in ``pyproject.toml``
  (``check_untyped_defs``, ``no_implicit_optional``, ...) must report zero errors;
* the strictly typed core modules must also pass ``mypy --strict``;
* every public function or method of the library has annotated parameters and return type;
* a ``py.typed`` marker ships with the package (PEP 561).
"""
from __future__ import annotations

import importlib
import inspect
import pathlib
import pkgutil

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

STRICT_MODULES = [
    "src/aerokit/verification.py",
    "src/aerokit/references/__init__.py",
    "src/aerokit/fem/results.py",
    "src/aerokit/fem/solvers.py",
    "src/aerokit/output/tables.py",
    "src/aerokit/output/report.py",
    "src/aerokit/output/writers.py",
    "src/aerokit/output/console.py",
    "src/aerokit/materials/handbook.py",
    "src/aerokit/materials/curves.py",
    "src/aerokit/units.py",
    "src/aerokit/data/__init__.py",
    # copied from Sidera; the files that already pass --strict (rf, antennas, dsn, itu_earth have no-any-return)
    "src/aerokit/comms/budget.py",
    "src/aerokit/comms/channel.py",
    "src/aerokit/comms/geometry.py",
    "src/aerokit/comms/terminals.py",
    "src/aerokit/comms/state.py",
    "src/aerokit/comms/digital.py",
    "src/aerokit/comms/modcod.py",
    "src/aerokit/comms/data_volume.py",
    "src/aerokit/comms/chain.py",
    "src/aerokit/orbits/constellations.py",
    "src/aerokit/orbits/visibility.py",
    "src/aerokit/orbits/gmst.py",
    "src/aerokit/orbits/kepler_j2.py",
    "src/aerokit/design/electric.py",
    "src/aerokit/reliability.py",
    "src/aerokit/operations.py",
]


def _mypy(args: list[str]) -> tuple[str, int]:
    api = pytest.importorskip("mypy.api")
    stdout, stderr, status = api.run(args)
    return stdout + stderr, status


@pytest.mark.slow
def test_mypy_whole_package_clean():
    out, status = _mypy(["--config-file", str(ROOT / "pyproject.toml"), str(SRC / "aerokit")])
    assert status == 0, f"mypy reported errors:\n{out}"


@pytest.mark.slow
def test_mypy_strict_core_modules():
    out, status = _mypy(["--strict", "--follow-imports=silent", "--ignore-missing-imports",
                         *[str(ROOT / m) for m in STRICT_MODULES]])
    assert status == 0, f"mypy --strict reported errors:\n{out}"


def test_py_typed_marker():
    assert (SRC / "aerokit" / "py.typed").is_file()


def _public_modules():
    import aerokit
    for info in pkgutil.walk_packages(aerokit.__path__, "aerokit."):
        name = info.name
        if any(part.startswith("_") for part in name.split(".")) or ".cli." in name or name.endswith(".cli"):
            continue
        yield name


def _public_callables(mod):
    for name, obj in vars(mod).items():
        if name.startswith("_") or getattr(obj, "__module__", None) != mod.__name__:
            continue
        if inspect.isfunction(obj):
            yield name, obj
        elif inspect.isclass(obj):
            for mname, meth in vars(obj).items():
                if (mname.startswith("_") and mname != "__init__") or not inspect.isfunction(meth):
                    continue
                if getattr(meth, "__module__", None) != mod.__name__:
                    continue        # e.g. the __init__ that typing.Protocol injects into a protocol class
                yield f"{name}.{mname}", meth


def _missing_annotations(fn) -> list[str]:
    sig = inspect.signature(fn)
    miss = [p.name for p in sig.parameters.values()
            if p.name not in ("self", "cls") and p.annotation is inspect.Parameter.empty]
    if sig.return_annotation is inspect.Signature.empty and fn.__name__ != "__init__":
        miss.append("return")
    return miss


@pytest.mark.parametrize("modname", sorted(_public_modules()))
def test_public_signatures_are_annotated(modname):
    mod = importlib.import_module(modname)
    gaps = {q: m for q, fn in _public_callables(mod) if (m := _missing_annotations(fn))}
    assert not gaps, f"{modname}: unannotated public API: " + "; ".join(f"{k} ({', '.join(v)})"
                                                                     for k, v in sorted(gaps.items()))
