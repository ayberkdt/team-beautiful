"""Static security scan of the package source (AST based, no third-party scanner needed).

The toolkit reads untrusted engineering files (STL, OBJ, DXF, JSON models) and writes reports,
so a small set of constructs is banned outright in ``src/aerokit``:

* code execution from data: ``eval``, ``exec``, ``compile``, ``__import__`` with a non-literal;
* unsafe deserialisation: ``pickle``/``marshal``/``shelve`` loads, ``yaml.load`` without SafeLoader,
  ``numpy.load(..., allow_pickle=True)``;
* shell injection: ``os.system``, ``os.popen``, ``subprocess`` with ``shell=True``;
* insecure temporary files: ``tempfile.mktemp``;
* network access (the toolkit is offline by design): ``socket``, ``urllib.request``, ``requests``, ``http.client``;
* validation by ``assert`` (stripped by ``python -O``);
* silently swallowed errors: bare ``except:`` and ``except Exception: pass``.

Each finding names file and line, so a regression is fixed where it is introduced.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "aerokit"
FILES = sorted(p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts)

BANNED_CALLS = {"eval", "exec", "compile"}
BANNED_ATTR_CALLS = {("os", "system"), ("os", "popen"), ("tempfile", "mktemp"), ("pickle", "load"),
                     ("pickle", "loads"), ("marshal", "load"), ("marshal", "loads"), ("shelve", "open")}
BANNED_IMPORTS = {"socket", "urllib.request", "requests", "http.client", "ftplib", "telnetlib", "pickle", "marshal",
                  "shelve"}


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_name(node.value)}.{node.attr}"
    return ""


def _scan(path: pathlib.Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rel = path.relative_to(SRC.parent)
    out: list[str] = []

    def hit(node: ast.AST, what: str) -> None:
        out.append(f"{rel}:{getattr(node, 'lineno', '?')}: {what}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = _name(node.func)
            if fn in BANNED_CALLS:
                hit(node, f"call to {fn}()")
            if fn == "__import__" and not (node.args and isinstance(node.args[0], ast.Constant)):
                hit(node, "dynamic __import__")
            parts = tuple(fn.rsplit(".", 1)) if "." in fn else ()
            if parts in BANNED_ATTR_CALLS:
                hit(node, f"call to {fn}()")
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            if fn.startswith("subprocess.") and isinstance(kw.get("shell"), ast.Constant) and kw["shell"].value:
                hit(node, "subprocess with shell=True")
            if fn.endswith("yaml.load") and "Loader" not in kw:
                hit(node, "yaml.load without an explicit safe Loader")
            if fn in ("np.load", "numpy.load") and isinstance(kw.get("allow_pickle"), ast.Constant) \
                    and kw["allow_pickle"].value:
                hit(node, "numpy.load(allow_pickle=True)")
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name in BANNED_IMPORTS:
                    hit(node, f"import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in BANNED_IMPORTS or any(f"{mod}.{a.name}" in BANNED_IMPORTS for a in node.names):
                hit(node, f"from {mod} import ...")
        elif isinstance(node, ast.Assert):
            hit(node, "assert used in library code (removed by python -O); raise an exception instead")
        elif isinstance(node, ast.ExceptHandler):
            if node.type is None:
                hit(node, "bare except:")
            elif _name(node.type) in ("Exception", "BaseException") and \
                    all(isinstance(s, ast.Pass) for s in node.body):
                hit(node, f"except {_name(node.type)}: pass swallows every error")
    return out


def test_source_files_found():
    assert len(FILES) > 40, f"only {len(FILES)} source files found under {SRC}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(SRC)))
def test_no_banned_constructs(path):
    findings = _scan(path)
    assert not findings, "security scan findings:\n" + "\n".join(findings)


def test_scanner_detects_banned_constructs(tmp_path):
    """The scanner itself must catch each banned construct (guards against a silently broken test)."""
    bad = tmp_path / "bad.py"
    bad.write_text(
        "import os, subprocess, pickle\n"
        "eval('1')\n"
        "os.system('ls')\n"
        "subprocess.run('ls', shell=True)\n"
        "pickle.loads(b'')\n"
        "assert 1 == 1\n"
        "try:\n    pass\nexcept:\n    pass\n"
        "try:\n    pass\nexcept Exception:\n    pass\n",
        encoding="utf-8")
    global SRC
    old = SRC
    try:
        SRC = tmp_path
        found = _scan(bad)
    finally:
        SRC = old
    kinds = " ".join(found)
    for needle in ("eval()", "os.system()", "shell=True", "pickle.loads()", "assert used", "bare except",
                   "except Exception: pass", "import pickle"):
        assert needle in kinds, f"scanner missed {needle!r}: {found}"
